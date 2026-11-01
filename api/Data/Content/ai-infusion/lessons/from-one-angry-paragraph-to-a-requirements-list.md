# From one angry paragraph to a requirements list

## From one angry paragraph to a requirements list

Before writing code, turn the problem statement into a list you can tick off. In an interview, this is the first five minutes and the part most people skip.

Read the brief four times, each time looking for one thing:

1. **Inputs and outputs.** In: complaint text plus an order id. Out: a refund amount, a customer message, and a record of every decision.
2. **What it must do** (functional requirements).
3. **How well it must do it** (non-functional: speed, safety, cost).
4. **What we are *not* building today** (out of scope), so the build stays finishable.

#### Functional requirements

| # | The system must… | Lives in | Proved by |
| --- | --- | --- | --- |
| F1 | Freeze the order evidence once per dispute | `evidence.py`, `ledger.py` | resume test (step 9) |
| F2 | Split a complaint into atomic, checkable grievances and drop feelings and demands | `stages.extract_grievances` | `eval_extract.py` |
| F3 | Judge each grievance K=3 times, independently | `stages.judge_grievance` | `eval_judge.py` |
| F4 | Decide by majority in code; no majority means escalate | `bench.tally` | `check_rules.py` |
| F5 | Price upheld grievances from the order, never from the model | `pricing.price` | `check_rules.py` |
| F6 | Send anything above ₹2,000 to a human | `pipeline.py` | the simulator below |
| F7 | Pay the resolved part when ≥ 60% resolved; hold the rest | `pipeline.py` | outage test (step 9) |
| F8 | Write a customer message that states only the computed amount | `stages.write_settlement` | read it in the app |
| F9 | Never pay the same dispute twice | `pipeline.py`, `payments.py` | replay test (step 9) |

#### Non-functional requirements

Latency

< 15 sp50, so parallel judging

Budget

14LLM calls for 4 grievances

Safety

₹2,000hard auto-approval cap

Audit

everyraw ruling kept

#### Out of scope for this build (and what stands in)

- **Kafka/SQS and worker fleets.** One process calls `resolve_dispute()` directly. The ledger still checkpoints every stage, so moving to a queue later changes the caller, not the pipeline.
- **Real order services and payments.** `evidence.py` and `payments.py` are small stand-ins with the same shape, including an idempotency key.
- **Several model providers.** One Groq model. Seating judges from different providers is an extension (see the end).

Ask the room

“Part 1 said the refund amount is “a price lookup against the order”. Look at the extraction schema from Part 1. Can you actually do that lookup?”

No. The schema had `text`, `category` and spans, but no *item* and no *quantity*. “2 of the 4 biryanis” is in the sentence, but code can't price a sentence. Writing requirements is how you find this **before** building: F5 needs two extra fields. So the extraction prompt in step 4 asks for `item` and `quantity`. The model still never computes money. It only says *which* item and *how many*, and code looks up the price.

Step 0 · setup

## The project folder

refund-bench/ ├── .env *# GROQ_API_KEY=… (never commit this)* ├── requirements.txt ├── evidence.py *# step 1 · the order + frozen snapshot* ├── pricing.py *# step 2 · rupees, in code* ├── bench.py *# step 2 · counting votes, in code* ├── check_rules.py *# step 2 · proof, no API key* ├── llm.py *# step 3 · one door to the model* ├── prompts.py *# step 4 · the three prompts* ├── stages.py *# step 5 · extract · judge · settle* ├── eval_extract.py *# step 6 · evals* ├── eval_judge.py *# step 6 · evals* ├── ledger.py *# step 7 · SQLite, four tables* ├── payments.py *# step 7 · idempotent payout stand-in* ├── pipeline.py *# step 8 · resolve_dispute()* ├── bench_check.py *# step 9 · end-to-end proof* └── app.py *# step 10 · Gradio*

```pseudo title="requirements.txt"
RUN pip install groq             // the Groq SDK, which talks to the model
RUN pip install gradio           // the web UI that app.py starts
RUN pip install python-dotenv    // reads the .env file for llm.py
```

```python reveal title="requirements.txt · three packages"
groq
gradio
python-dotenv
```

```pseudo title="setup.sh"
RUN python -m venv .venv                 // create the .venv folder with its own Python
RUN source .venv/bin/activate            // use it in this terminal (Windows: .venv\Scripts\activate)
RUN pip install -r requirements.txt      // install the packages listed in that file
SAVE "GROQ_API_KEY=your_key_here" as the .env file   // this replaces any old .env; put your real key here
RUN a one-line check: ask llm.call to say hi in three words, at temperature 0   // milestone 0
```

```python reveal title="setup.sh · terminal · run from the project folder"
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
python -c "from llm import call; print(call('Say hi in three words', 0))"
```

The last line is your milestone-0 proof: if the model answers, the key, the network and the package are all fine. It needs `llm.py` from step 3, so come back and run it then if you're building strictly in order.

Step 1 · no LLM

## The evidence, and why we freeze it

In production the evidence comes from several services and keeps changing: ratings move, bills are edited, reconciliation runs overnight. Here it's one dictionary with exactly the fields from Part 1's case. Pay attention to what *isn't* in it.

```pseudo title="evidence.py"
SET ORDERS = one order, ORD-1840, with its line items, fees, times, weight and partner rating   // no field records packaging condition
SET SAMPLE_COMPLAINT = the customer's paragraph, joined from its parts

DEFINE snapshot(order_id):
    // freeze the evidence once: every judge on every grievance sees this copy
    SET frozen = a deep copy of ORDERS[order_id]
    SET frozen["snapshot_taken_at"] = the current time, to the second
    RETURN frozen
```

> **Imported:**
> - `copy` Python standard library: makes the deep copy that freezes the order.
> - `datetime` from `datetime`, Python standard library: gives the time the snapshot was taken.

```python reveal title="evidence.py · step 1"
import copy
from datetime import datetime

# Stand-in for the order service. In production this is several services
# (orders, logistics, ratings) and every field can change after the fact.
ORDERS = {
    "ORD-1840": {
        "order_id": "ORD-1840",
        "line_items": [
            {"name": "Hyderabadi Biryani", "quantity": 4, "unit_price": 320},
            {"name": "Paneer Tikka", "quantity": 1, "unit_price": 360},
            {"name": "Raita", "quantity": 1, "unit_price": 60},
            {"name": "Gulab Jamun", "quantity": 1, "unit_price": 91},
        ],
        "delivery_fee": 49,                       # order total = 1,840
        "placed_at": "20:15",
        "delivered_at": "21:40",
        "sla_minutes": 45,
        "pickup_weight_kg": 1.2,
        "expected_weight_kg": 2.4,
        "partner_rating": {"stars": 5, "rated_at": "21:41"},
        # note what is NOT here: nothing records packaging condition
    }
}

SAMPLE_COMPLAINT = (
    "Ordered at 8:15pm and the food showed up at 9:40pm. We had guests over, it was "
    "embarrassing. Two of the four were missing completely. The raita had leaked all over "
    "the inside of the bag. And the delivery guy was rude when I asked him about it. "
    "Honestly the worst experience I've had on this app - refund everything.")

def snapshot(order_id: str) -> dict:
    """Freeze the evidence once. Every judge on every grievance sees this copy."""
    frozen = copy.deepcopy(ORDERS[order_id])
    frozen["snapshot_taken_at"] = datetime.now().isoformat(timespec="seconds")
    return frozen
```

1 **Prices add up to the case study** 4 × ₹320 + ₹360 + ₹60 + ₹91 + ₹49 delivery = ₹1,840. When the arithmetic is internally consistent, you can check every later result by hand.

2 **The missing field is deliberate** Nothing records packaging condition. That's why the raita grievance *should* escalate, and the eval in step 6 checks that it does.

3 **`deepcopy` plus a timestamp** The snapshot is a copy, not a reference. If someone edits `ORDERS` later, the dispute is still judged against what was true at intake, and you can say when that was.

*prove it* $ python -c "from evidence import snapshot; print(snapshot('ORD-1840')['delivered_at'])" **21:40**

Step 2 · no LLM

## Write the money rules before the model

Everything here decides money, and none of it needs an API key. That's exactly why it comes first.

#### Pricing: rupees come from the order

```pseudo title="pricing.py"
SET ITEM_CATEGORIES = MISSING_ITEM, WRONG_ITEM, QUALITY, PACKAGING

DEFINE find_item(name, evidence):
    IF name is empty THEN RETURN None
    SET name = name in lowercase
    FOR EACH item in the order's line items:
        IF one name contains the other THEN RETURN item
    RETURN None

DEFINE price(grievance, evidence):
    // rupees owed if upheld; None means code cannot price it, so a human does
    IF category is LATE_DELIVERY THEN RETURN the order's delivery fee
    IF category is PARTNER_CONDUCT THEN RETURN 0   // an ops matter, not a refund
    IF category is one of ITEM_CATEGORIES THEN
        SET item = find_item(the named item, evidence)
        IF item is None THEN RETURN None
        SET qty = the quantity given (1 if none), kept between 1 and the quantity ordered
        RETURN qty times the item's unit price
    RETURN None   // BILLING and unknown categories: always a human
```

```python reveal title="pricing.py · step 2 · F5"
ITEM_CATEGORIES = {"MISSING_ITEM", "WRONG_ITEM", "QUALITY", "PACKAGING"}

def find_item(name: str | None, evidence: dict) -> dict | None:
    if not name:
        return None
    name = name.lower()
    for item in evidence["line_items"]:
        if name in item["name"].lower() or item["name"].lower() in name:
            return item
    return None

def price(grievance: dict, evidence: dict) -> int | None:
    """Rupees owed if this grievance is upheld. None = code cannot price it -> human."""
    category = grievance["category"]
    if category == "LATE_DELIVERY":
        return evidence["delivery_fee"]
    if category == "PARTNER_CONDUCT":
        return 0                                      # an ops matter, not a refund
    if category in ITEM_CATEGORIES:
        item = find_item(grievance.get("item"), evidence)
        if item is None:
            return None
        qty = grievance.get("quantity") or 1
        qty = max(1, min(int(qty), item["quantity"]))   # never refund more than was ordered
        return qty * item["unit_price"]
    return None                                       # BILLING, UNKNOWN: always a human
```

1 **`None` means “a human prices this”** Billing disputes, unknown categories and items that aren't on the order all return `None`. The pipeline turns an upheld-but-unpriceable grievance into an escalation. Code never guesses a number.

2 **Quantity is clamped** If the model extracts “9 biryanis missing” from an order of 4, `min(qty, ordered)` caps it. A mis-extraction or a lying customer can't push the refund past what was bought.

3 **Partner conduct prices at ₹0** Even if upheld, rudeness isn't a refund line. It's an operations matter. Writing that down as a rule is a product decision you can now see and change.

#### The bench: a vote is a `Counter`

```pseudo title="bench.py"
DEFINE tally(rulings):
    // a failed judge call is not a vote, so the grievance stays unresolved
    IF rulings is empty or any judge call failed THEN RETURN None
    SET votes = the ruling of each judge, as letters like U,E,E
    SET winner, count = the most common ruling and how many judges gave it
    IF count is not more than half of the votes THEN SET winner = ESCALATE   // no majority
    SET confidence = average confidence of the judges who agreed with winner   // logged only, never branched on
    RETURN winner, the votes, the split like 2-1, and the confidence
```

> **Imported:**
> - `Counter` from `collections`, Python standard library: counts how many judges gave each ruling.

```python reveal title="bench.py · step 2 · F4"
from collections import Counter

def tally(rulings: list) -> dict | None:
    """Count K rulings in plain code. None in the list = a judge call that failed."""
    if not rulings or any(r is None for r in rulings):
        return None                                   # unresolved, not rejected
    votes = [r["ruling"] for r in rulings]
    winner, count = Counter(votes).most_common(1)[0]
    if count * 2 <= len(votes):                       # no strict majority (e.g. U, R, E)
        winner = "ESCALATE"
    agreeing = [r.get("confidence", 0) for r in rulings if r["ruling"] == winner]
    return {
        "ruling": winner,
        "votes": ",".join(v[0] for v in votes),       # "U,E,E" - keep the split, not just the winner
        "split": f"{count}-{len(votes) - count}",
        # logged and charted, never branched on: it is a number the model made up
        "confidence": round(sum(agreeing) / len(agreeing), 2) if agreeing else 0.0,
    }
```

1 **A failed call is not a vote** If any judge call failed, the grievance is *unresolved*, never rejected. That's the asymmetry from Part 1 in one `return None`.

2 **“Strict majority” in one line** `count * 2 <= len(votes)` catches U, R, E: three different rulings, so no majority, so escalate.

3 **Keep the split** `"U,E,E"` and `"2-1"` are stored next to the winner. A 3–0 and a 2–1 upheld are the same verdict with very different risk.

4 **Confidence is logged, never branched on** It's an average of numbers the model generated. Chart it, but no `if` anywhere in the project reads it.

#### Prove it, still with no API key

```pseudo title="check_rules.py"
SET ev = a frozen snapshot of order ORD-1840
DEFINE r(ruling, confidence): RETURN a judge result with that ruling and confidence
SET U, R, E = UPHELD, REJECTED, ESCALATE

// the bench: counting, no model
Check: three UPHELD votes give UPHELD
Check: U, E, E gives ESCALATE                  // one UPHELD against two ESCALATE
Check: U, U, R gives a split of 2-1            // the split is kept
Check: U, R, E gives ESCALATE                  // no majority at all
Check: a failed call makes the result None     // a failed call is not a vote

// the price list: code, no model
Check: a late delivery is worth 49
Check: 2 biryanis are worth 640
Check: 9 biryanis are capped at the 4 ordered, so 1280
Check: raita packaging is worth 60
Check: partner conduct is worth 0
Check: a Pizza that is not on the order gives None
Check: billing gives None

PRINT "all 12 rule checks passed - no API key needed"
```

> **Imported:**
> - `tally` from `bench`, the local file bench.py: counts the rulings into a verdict.
> - `snapshot` from `evidence`, the local file evidence.py: freezes the sample order, so the checks use fixed data.
> - `price` from `pricing`, the local file pricing.py: the price list being checked.

```python reveal title="check_rules.py · step 2 · python check_rules.py"
from bench import tally
from evidence import snapshot
from pricing import price

ev = snapshot("ORD-1840")

def r(ruling, confidence=0.9):
    return {"ruling": ruling, "confidence": confidence}

U, R, E = "UPHELD", "REJECTED", "ESCALATE"

# the bench - counting, no model
assert tally([r(U), r(U), r(U)])["ruling"] == U
assert tally([r(U), r(E), r(E)])["ruling"] == E           # 1-2 -> majority escalates
assert tally([r(U), r(U), r(R)])["split"] == "2-1"        # the split is kept, not thrown away
assert tally([r(U), r(R), r(E)])["ruling"] == E           # no majority at all -> human
assert tally([r(U), None, r(U)]) is None                  # a failed call is not a vote

# the price list - code, no model
assert price({"category": "LATE_DELIVERY"}, ev) == 49
assert price({"category": "MISSING_ITEM", "item": "Hyderabadi Biryani", "quantity": 2}, ev) == 640
assert price({"category": "MISSING_ITEM", "item": "biryani", "quantity": 9}, ev) == 1280  # capped
assert price({"category": "PACKAGING", "item": "Raita", "quantity": None}, ev) == 60
assert price({"category": "PARTNER_CONDUCT"}, ev) == 0
assert price({"category": "QUALITY", "item": "Pizza", "quantity": 1}, ev) is None   # not on the order
assert price({"category": "BILLING"}, ev) is None

print("all 12 rule checks passed - no API key needed")
```

*$ python check_rules.py* **all 12 rule checks passed - no API key needed**

Why this order matters

If step 8 later refunds the wrong amount, you already *know* pricing and tallying are correct. So the bug is in extraction (wrong item or quantity) or judging (wrong ruling). Two suspects instead of five, and no tokens spent finding out.

Step 3 · the model's only door

## One wrapper for every LLM call

Every call in the project goes through these three functions, so retry, backoff, jitter and JSON parsing are written once.

```pseudo title="llm.py"
LOAD every KEY=value line from .env into the environment
SET client = a Groq client, using the GROQ_API_KEY environment variable
SET MODEL = "openai/gpt-oss-20b"
SET MAX_RETRIES = 4

DEFINE call(prompt, temperature):
    FOR EACH attempt from 0 to MAX_RETRIES:
        TRY
            SEND prompt to MODEL at this temperature
            RETURN the reply text
        ON ERROR a rate limit (429) or a network blip:
            IF this was the last attempt THEN raise the error
            WAIT 2 to the power of attempt, plus a random 0 to 1 second   // backoff + jitter

DEFINE call_json(prompt, temperature):
    SET text = call(prompt, temperature), trimmed
    Remove a leading or trailing markdown fence   // models add them anyway
    RETURN the text parsed as JSON

DEFINE render(template, values):
    // {{name}} slots, so the JSON braces inside prompts stay untouched
    FOR EACH name and value in values:
        Replace "{{name}}" in the template with the value
    RETURN the template
```

> **Imported:**
> - `json` Python standard library: turns the model's reply text into Python data.
> - `os` Python standard library: reads the GROQ_API_KEY from the environment.
> - `random` Python standard library: adds the jitter to each retry wait.
> - `re` Python standard library: strips markdown fences from replies.
> - `time` Python standard library: pauses between retries.
> - `load_dotenv` from `dotenv`, package python-dotenv: copies the .env file into the environment.
> - `Groq` from `groq`: the client that sends the requests.
> - `RateLimitError` from `groq`: the 429 error that triggers a retry.
> - `APIConnectionError` from `groq`: the network error that triggers a retry.

````python reveal title="llm.py · step 3"
import json
import os
import random
import re
import time

from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIConnectionError

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"
MAX_RETRIES = 4

def call(prompt: str, temperature: float) -> str:
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL, temperature=temperature,
                messages=[{"role": "user", "content": prompt}])
            return resp.choices[0].message.content
        except (RateLimitError, APIConnectionError):          # 429 or network blip
            if attempt == MAX_RETRIES:
                raise
            time.sleep(2 ** attempt + random.uniform(0, 1))   # backoff + jitter

def call_json(prompt: str, temperature: float):
    text = call(prompt, temperature).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)      # models love fences
    return json.loads(text)

def render(template: str, **values) -> str:
    # {{name}} placeholders, so the JSON braces inside prompts stay untouched
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template
````

1 **Backoff plus jitter, exactly as in Part 1** `2 ** attempt` waits 1, 2, 4, 8 seconds. `random.uniform(0, 1)` is the jitter that stops forty workers retrying in lockstep. Only rate limits and network errors are retried. A bad request fails immediately, because retrying it would just fail again more slowly.

2 **Models wrap JSON in fences anyway** The prompt says “no markdown fences”, and sometimes the model adds them. The regex strips them before `json.loads`. Defend in code; don't just ask nicely in the prompt.

3 **`{{name}}` placeholders** The prompts contain literal JSON braces, which would break Python's `.format()`. A tiny `replace`-based `render` leaves them alone. LangChain's templates (Class 8) solve the same problem by escaping braces as `{{ }}`.

Step 4 · prompts

## The three prompts, with two edits

These are Part 1's prompts almost word for word. Re-read “the one line in each that does the work” first. Two edits came out of the requirements:

- **Extraction** now asks for `item` and `quantity` (from F5). The model still doesn't judge or price anything.
- **Settlement** now says “do not mention grievances that were REJECTED”. Part 1 called silently dropping g4 a product choice, and a choice only holds if it's written into the prompt.

```pseudo title="prompts.py"
SET CATEGORIES = the seven categories, from LATE_DELIVERY to BILLING

SET EXTRACT = the extraction prompt, with slots for the complaint and the line items
    // rules: one checkable grievance each, judge nothing, resolve references, JSON only
SET JUDGE = the judging prompt, with slots for one grievance and the evidence
    // rules: UPHELD, REJECTED or ESCALATE; silent evidence means ESCALATE, never REJECTED
SET SETTLE = the settlement prompt, with slots for the complaint, the rulings and the amount
    // rules: treat all rulings as final; mention no REJECTED grievance; state only the given amount
```

```python reveal title="prompts.py · step 4"
CATEGORIES = ["LATE_DELIVERY", "MISSING_ITEM", "WRONG_ITEM", "QUALITY",
              "PACKAGING", "PARTNER_CONDUCT", "BILLING"]

EXTRACT = """You are a precise dispute-intake assistant.

Given a customer complaint and the order's line items,
extract every atomic, checkable grievance.

Rules:
- A grievance is a statement about something that happened
  to THIS order, which evidence could confirm or contradict
- Exclude feelings, opinions, demands, and rhetorical questions
- Do NOT judge whether the grievance is true - only extract it
- Each grievance must be self-contained: resolve pronouns and
  vague references against the order's line items
- Assign one category from the list below
- If it concerns a line item, copy the item name exactly and the
  quantity affected; otherwise use null
- Return ONLY a JSON array, no preamble, no markdown fences

Categories: LATE_DELIVERY | MISSING_ITEM | WRONG_ITEM |
            QUALITY | PACKAGING | PARTNER_CONDUCT | BILLING

Schema:
[{ "text": "<the grievance as a standalone sentence>",
   "category": "<one of the above>",
   "item": "<line item name or null>", "quantity": <int or null>,
   "span_start": <char offset>, "span_end": <char offset> }]

Complaint:  {{complaint_text}}
Order:      {{line_items_json}}"""

JUDGE = """You are an impartial claims adjudicator.
Rule on the following grievance using ONLY the evidence given.

Grievance: {{grievance_text}}
Evidence:  {{evidence_snapshot_json}}

Rulings:
- UPHELD:   the evidence supports the grievance
- REJECTED: the evidence contradicts the grievance
- ESCALATE: the evidence is silent or ambiguous on this point

Rules:
- Do not hedge - pick the single best ruling
- Rule ONLY on the evidence provided. Do not reason about what
  is typical, likely, or fair
- If the evidence does not speak to this grievance, the ruling
  is ESCALATE - never REJECTED
- Return ONLY valid JSON, no preamble, no markdown fences

Schema:
{ "ruling": "UPHELD" | "REJECTED" | "ESCALATE",
  "confidence": <float 0.0 to 1.0>,
  "evidence_cited": "<which field(s) decided it>",
  "reasoning": "<one to three sentences>" }"""

SETTLE = """You are a customer-support writer for a food delivery app.

Below is a customer's complaint, the final ruling on each
grievance, and the refund amount already calculated.

Write a 3-4 sentence reply that:
- States the refund amount and when it will arrive
- Names what was resolved and what a colleague will look into
- Acknowledges the experience without grovelling

Rules:
- Do NOT re-adjudicate any ruling - treat all rulings as final
- Do NOT state, recalculate, or negotiate any amount other
  than the one given
- Never blame the restaurant or the delivery partner
- Do not mention grievances that were REJECTED
- Plain language. No apology more than once.

Complaint: {{complaint_text}}
Rulings:   {{verdicts_json}}
Amount:    {{refund_amount}}"""
```

Step 5 · the three stages

## Extract, judge, settle: three functions

```pseudo title="stages.py"
SET RULINGS = UPHELD, REJECTED, ESCALATE

DEFINE extract_grievances(complaint, evidence):
    // stage 2: one call at temperature 0, the barrier everything waits on
    SET raw = call_json of EXTRACT, filled with the complaint and the line items, at temperature 0
    FOR EACH item g in raw, numbered from 1:
        ADD a grievance with id g1, g2 and so on, its text, category, item, quantity and span
        // a category that is not in CATEGORIES becomes UNKNOWN
    RETURN the grievances

DEFINE judge_grievance(grievance, evidence, judge_index):
    // stage 3: one of K independent judges, at temperature 0.7
    SET prompt = JUDGE, filled with the grievance text and the evidence
    TRY
        SET ruling = call_json(prompt, 0.7)
    ON ERROR the reply is not usable JSON THEN
        SET ruling = an empty result
    IF the ruling is not one of RULINGS THEN
        SET ruling = ESCALATE, with confidence 0.0 and "judge output could not be parsed"
    ADD judge_index to the ruling
    RETURN the ruling

DEFINE write_settlement(complaint, verdicts, amount):
    // stage 4: one call at temperature 0.2, writes words about a number it is given
    SET summary = each grievance text with its ruling
    RETURN the reply from SETTLE, filled with the complaint, the summary and "Rs" plus the amount, at temperature 0.2
```

> **Imported:**
> - `json` Python standard library: turns the evidence and rulings into JSON text for the prompts.
> - `call` from `llm`, the local file llm.py: sends one prompt and returns the reply text.
> - `call_json` from `llm`, the local file llm.py: sends a prompt and parses the reply as JSON.
> - `render` from `llm`, the local file llm.py: fills the {{slots}} in a prompt.
> - `CATEGORIES` from `prompts`, the local file prompts.py: the allowed category names.
> - `EXTRACT` from `prompts`, the local file prompts.py: the extraction prompt.
> - `JUDGE` from `prompts`, the local file prompts.py: the judging prompt.
> - `SETTLE` from `prompts`, the local file prompts.py: the settlement prompt.

```python reveal title="stages.py · step 5 · F2, F3, F8"
import json

from llm import call, call_json, render
from prompts import CATEGORIES, EXTRACT, JUDGE, SETTLE

RULINGS = {"UPHELD", "REJECTED", "ESCALATE"}

def extract_grievances(complaint: str, evidence: dict) -> list:
    """Stage 2 - one call, temperature 0. The barrier everything waits on."""
    raw = call_json(render(EXTRACT, complaint_text=complaint,
                           line_items_json=json.dumps(evidence["line_items"])), temperature=0)
    grievances = []
    for i, g in enumerate(raw, 1):
        grievances.append({
            "grievance_id": f"g{i}",              # ids come from code, not the model
            "text": g["text"],
            "category": g.get("category") if g.get("category") in CATEGORIES else "UNKNOWN",
            "item": g.get("item"),
            "quantity": g.get("quantity"),
            "span_start": g.get("span_start"),
            "span_end": g.get("span_end"),
        })
    return grievances

def judge_grievance(grievance: dict, evidence: dict, judge_index: int) -> dict:
    """Stage 3 - one of K independent judges. No shared history, T > 0."""
    prompt = render(JUDGE, grievance_text=grievance["text"],
                    evidence_snapshot_json=json.dumps(evidence))
    try:
        ruling = call_json(prompt, temperature=0.7)
    except (json.JSONDecodeError, TypeError):
        ruling = {}
    if ruling.get("ruling") not in RULINGS:            # unparseable -> the safe verdict
        ruling = {"ruling": "ESCALATE", "confidence": 0.0,
                  "evidence_cited": "", "reasoning": "judge output could not be parsed"}
    ruling["judge_index"] = judge_index
    return ruling

def write_settlement(complaint: str, verdicts: list, amount: int) -> str:
    """Stage 4 - one call, low temperature. Writes words about a number it was given."""
    summary = [{"grievance": v["text"], "ruling": v["ruling"]} for v in verdicts]
    return call(render(SETTLE, complaint_text=complaint,
                       verdicts_json=json.dumps(summary), refund_amount=f"Rs {amount}"),
                temperature=0.2)
```

1 **Ids come from code: `g1`, `g2`…** Part 1's schema had the model invent a uuid. Here code numbers the grievances. Ids then stay stable across a resumed run, and the ledger can say “judge 2 on g3 already ruled”.

2 **Validate the enum** A category outside the list becomes `UNKNOWN`, which pricing refuses to price. A ruling outside UPHELD, REJECTED and ESCALATE becomes ESCALATE. Every model output passes through an allow-list before code acts on it.

3 **Temperature per stage** Extraction runs at 0, because you want the same grievances every time. Judges run at 0.7, because at 0 all three judges would answer identically and the bench would be *theatre*. Settlement runs at 0.2, because the customer reads it and it must not invent anything.

4 **The settlement call gets rulings, not reasoning** The writer sees each grievance and its final ruling, plus the amount as a string. It can't re-argue a case it never saw argued.

*prove it: one extraction on the sample complaint (expected output; the wording of the text varies)* $ python -c "from stages import *; from evidence import *; \ [print(g['grievance_id'], g['category'], g['item'], g['quantity']) \ for g in extract_grievances(SAMPLE_COMPLAINT, snapshot('ORD-1840'))]" g1 **LATE_DELIVERY** None None g2 **MISSING_ITEM** Hyderabadi Biryani 2 g3 **PACKAGING** Raita 1 g4 **PARTNER_CONDUCT** None None *← "embarrassing" and "refund everything" are gone*

Step 6 · evals
