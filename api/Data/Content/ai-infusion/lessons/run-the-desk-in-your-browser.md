# Run the desk in your browser

## Run the desk in your browser

The calculators, thresholds, triage log and daily summary are a line-for-line port of the Python. The two LLM calls are replaced by **clearly fake stand-ins**: a keyword classifier and a fill-in-the-blanks message. You can also override the category to play “what if the model said…”. The money never changes with the wording of the message.

**EXCEPTION DESK** · rules real, LLM simulated 0 processed today

Samples

Exception report

Shipment value ($)

800

Customer tier

(standard / premium)

Category

(auto (stand-in classifier) / force: delayed / force: damaged / force: lost / force: unknown)

> **Note:**
> Things to try: send the routine delay as *premium* and nothing changes, because $40 is under $100. Make it a $1,500 urgent delay and the doubled rate pushes it past $100. Force *unknown* on anything and it always escalates at $0.

**Sample · Urgent premium:** URGENT: medical kit arrived three days late, the patient had to wait.

**Sample · Scratch:** Small scratch on the lid of the speaker, works fine otherwise.

Ask 1 · chains.py

## Three chains, one model, three jobs

All three chains use the same LLM object. What makes them behave differently is the system prompt. Each chain is LangChain's expression language, `prompt | llm | parser`: fill the template, call the model, and turn the reply into a plain string.

```pseudo title="llm.py"
RUN load_dotenv()          // reads GROQ_API_KEY from .env into the environment
CREATE llm = a ChatGroq model "openai/gpt-oss-20b", temperature 0   // as repeatable as the model allows
```

> **Imported:**
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file and copies each line into the environment.
> - `ChatGroq` from `langchain_groq`, package langchain-groq: the chat model class that sends requests to models hosted by Groq.

```python reveal title="llm.py · the one model object"
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()   # reads GROQ_API_KEY from .env

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
```

```pseudo title="chains.py"
USE the one shared llm object from llm.py          // the same model for all three chains

SET classify_chain = fill the prompt, CALL the model, keep the reply as plain text
    system: reply with exactly ONE word: delayed, damaged, lost or unknown
    human:  the report text

SET escalate_chain = fill the prompt, CALL the model, keep the reply as plain text
    system: write 2-3 sentences for a manager, end with a request for approval, do not change the amount
    human:  report, category, proposed compensation, reasoning

SET draft_email_chain = fill the prompt, CALL the model, keep the reply as plain text
    system: write a short, polite customer email of 3-4 sentences, never state a different amount
    human:  report, category, compensation, reasoning
```

> **Imported:**
> - `StrOutputParser` from `langchain_core.output_parsers`, package langchain-core: turns the model's reply into a plain string.
> - `ChatPromptTemplate` from `langchain_core.prompts`, package langchain-core: builds the system and human messages, with `{placeholders}` to fill.
> - `llm` from `llm`: the one shared model object from `llm.py`.

```python reveal title="chains.py · ask 1 · the three LLM jobs"
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from llm import llm

# 1. Classify: the only decision the model makes in this whole system.
classify_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You triage shipment exception reports for a logistics company. "
     "Read the report and classify it with exactly ONE word: "
     "delayed, damaged, lost, or unknown. Use unknown if it does not clearly fit "
     "one of the other three. Reply with that single word only - nothing else."),
    ("human", "{report_text}"),
])
classify_chain = classify_prompt | llm | StrOutputParser()

# 2. Escalate: an internal note a manager reads before approving money.
escalate_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Write a short internal note for a shipment-exceptions manager who must approve "
     "compensation. Summarise the report, the category and the reasoning in 2-3 "
     "sentences, then end with a clear request for approval. Do not change the amount."),
    ("human", "Report: {report_text}\nCategory: {category}\n"
              "Proposed compensation: ${amount}\nReasoning: {reasoning}"),
])
escalate_chain = escalate_prompt | llm | StrOutputParser()

# 3. Draft email: what the customer reads when the case auto-resolves.
email_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Write a short, polite customer-facing email for a logistics company resolving a "
     "shipment exception. Acknowledge the issue, state the compensation being issued, "
     "keep it to 3-4 sentences. Never state an amount other than the one given."),
    ("human", "Report: {report_text}\nCategory: {category}\n"
              "Compensation: ${amount}\nReasoning: {reasoning}"),
])
draft_email_chain = email_prompt | llm | StrOutputParser()
```

1 **System vs human messages** The system message says how to behave (“reply with that single word only”). The human message is the data (`{report_text}`). Keeping the data out of the instructions makes the prompt reusable and keeps the instructions harder to override with a cleverly worded report.

2 **“Exactly one word… nothing else”** The classification prompt is the most important prompt in the system. A one-word answer is easy to check in code. A sentence like “This appears to be a delay issue” is not.

3 **The amount is an input to the writers** Both writing prompts receive `{amount}` and are told not to change it. The model narrates a number it was given; it never produces one.

4 **`temperature=0`** Classification should be as repeatable as a model allows. The more detailed the system prompt, the better the output, and the tighter the instructions, the less there is to vary.

Ask 1 · pipeline.py

## Where every piece meets

`process_exception()` is the only function that knows about all the others. It takes exactly the three things the form collects and returns one flat dict with everything the UI, the log and the summary need.

```pseudo title="pipeline.py"
SET PREMIUM_ESCALATION_THRESHOLD = $100, STANDARD_ESCALATION_THRESHOLD = $200
SET CALCULATORS = "delayed" to delay_compensation, "damaged" to damage_compensation, "lost" to lost_compensation

DEFINE process_exception(report_text, shipment_value, customer_tier):
    SET log = empty list
    // 1. The LLM classifies, and that is ALL it decides
    SET raw = the classifier's reply, with spaces and the final full stop removed, in lower case
    SET category = raw IF raw is a key in CALCULATORS, ELSE "unknown"
    ADD "classified as ..." to log
    // 2. Code computes the money
    IF category is "unknown" THEN
        SET comp = amount 0, with a reason saying it could not be classified
    ELSE
        SET comp = CALCULATORS[category](shipment_value, report_text)
    ADD the amount and reasoning to log
    // 3. Code decides who signs off
    SET threshold = $100 IF tier is premium, ELSE $200
    SET needs_approval = TRUE IF category is "unknown" OR amount is more than threshold
    ADD the tier, the threshold and ESCALATE or auto-resolve to log
    // 4. The LLM writes the words for the chosen path
    IF needs_approval THEN
        SET message = escalate_chain(report, category, amount, reasoning)
        ADD "drafted internal escalation note" to log
    ELSE
        SET message = draft_email_chain(report, category, amount, reasoning)
        ADD "drafted customer email" to log
    RETURN one flat dict: the inputs, category, amount, reasoning, needs_approval, drafted message and log
```

> **Imported:**
> - `classify_chain` from `chains`: the classifier chain, which returns one category word.
> - `escalate_chain` from `chains`: writes the manager note for cases that need approval.
> - `draft_email_chain` from `chains`: writes the customer email for cases that auto-resolve.
> - `delay_compensation` from `tools`: the calculator for delayed shipments.
> - `damage_compensation` from `tools`: the calculator for damaged shipments.
> - `lost_compensation` from `tools`: the calculator for lost shipments.

```python reveal title="pipeline.py · milestones 5–6 · the wiring"
from chains import classify_chain, escalate_chain, draft_email_chain
from tools import delay_compensation, damage_compensation, lost_compensation

# Escalation thresholds by customer tier. Premium gets a human sooner.
PREMIUM_ESCALATION_THRESHOLD = 100
STANDARD_ESCALATION_THRESHOLD = 200

CALCULATORS = {
    "delayed": delay_compensation,
    "damaged": damage_compensation,
    "lost": lost_compensation,
}

def process_exception(report_text: str, shipment_value: float, customer_tier: str) -> dict:
    log = []

    # 1. The LLM classifies - and that is ALL it decides.
    raw = classify_chain.invoke({"report_text": report_text}).strip().lower().strip(".")
    category = raw if raw in CALCULATORS else "unknown"
    log.append(f"classified as '{category}' (model said '{raw}')")

    # 2. Code computes the money.
    if category == "unknown":
        comp = {"amount": 0.0, "reasoning": "Could not confidently classify this report."}
    else:
        comp = CALCULATORS[category](shipment_value, report_text)
    log.append(f"compensation ${comp['amount']:,.2f}: {comp['reasoning']}")

    # 3. Code decides who signs off.
    threshold = (PREMIUM_ESCALATION_THRESHOLD if customer_tier == "premium"
                 else STANDARD_ESCALATION_THRESHOLD)
    needs_approval = category == "unknown" or comp["amount"] > threshold
    log.append(f"{customer_tier} threshold ${threshold}: "
               f"{'ESCALATE' if needs_approval else 'auto-resolve'}")

    # 4. The LLM writes the words for whichever path was chosen.
    chain_input = {"report_text": report_text, "category": category,
                   "amount": comp["amount"], "reasoning": comp["reasoning"]}
    if needs_approval:
        message = escalate_chain.invoke(chain_input)
        log.append("drafted internal escalation note")
    else:
        message = draft_email_chain.invoke(chain_input)
        log.append("drafted customer email")

    return {
        "report_text": report_text, "shipment_value": shipment_value,
        "customer_tier": customer_tier, "category": category,
        "compensation_amount": comp["amount"], "compensation_reasoning": comp["reasoning"],
        "needs_approval": needs_approval, "drafted_message": message, "log": log,
    }
```

1 **Normalise, then check against an allowed set** `.strip().lower().strip(".")` turns “Delayed.” into `delayed`. Anything still not a known category becomes `unknown`. The model's reply is *untrusted input*, and this line is the guard.

2 **A dispatch dict instead of if/elif** `CALCULATORS[category]` picks the function. Adding a new category, say “wrong item”, means one calculator and one dict entry.

3 **Unknown never auto-resolves** `needs_approval = category == "unknown" or amount > threshold`. If the system can't say what happened, a person decides. That's the cheap mistake to make.

4 **The log is built as you go** Every step appends a human-readable line. When a manager asks why a case escalated, the answer is already written down in the order it happened.

#### The demo case, step by step

1

#### Classify

LLM call 1

In

“Package arrived 2 days later than the estimated delivery date…”

Model says

`Delayed.`

Code keeps

category = "delayed"

2

#### Compensate

0 LLM calls

Calls

`delay_compensation(800, report)`

Rule

5%; no urgent signal, so no doubling

Out

{"amount": 40.0, "reasoning": "Delay compensation at 5%…"}

3

#### Decide

0 LLM calls

Tier

standard → threshold $200

Test

unknown? no · 40 > 200? no

Out

needs_approval = False

4

#### Draft

LLM call 2

Chain

`draft_email_chain`

Given

report, category, amount, reasoning

Out

A 3–4 sentence customer email stating the $40.

> **Note:**
> If step 3 had said `True`, the same four inputs would go to `escalate_chain` instead, and the output would be a note asking a manager to approve, not an email.

Ask the room

“Premium customers escalate above $100, standard above $200. Isn't that backwards? Shouldn't premium customers get paid faster?”

Both readings came up during the session, and both are defensible. A **lower** premium threshold puts a human on high-value relationships sooner. A **higher** one auto-pays them more generously. One alternative even escalated every premium case regardless of amount, because “I don't want to lose that customer.” Which is right is a business decision, not an engineering one. That's exactly why it lives in two named constants a product owner can read and change, rather than in a prompt.

Ask 2 · session.py

## A daily log that can actually be summed

Same idea as the interview coach's memory. A plain Python list stands in for a database, and each entry is the full structured result of `process_exception()`, never a concatenated string. Because the entries have keys, the summary is a few lines of arithmetic.

```pseudo title="session.py"
SET daily_log = empty list          // one dict per processed exception, a DB table in real life

DEFINE record(final_state):
    ADD final_state to daily_log

DEFINE generate_daily_summary():
    IF daily_log is empty THEN
        RETURN "No exceptions processed yet today."
    SET total = sum of compensation_amount over all entries
    SET escalation_rate = entries that needed approval ÷ all entries × 100
    SET by_category = total compensation for each category
    SET costliest = the category with the largest total in by_category
    SET lines = a heading with the number of exceptions
    FOR EACH entry in daily_log:
        ADD one line: category, amount, ESCALATED or auto-resolved
    ADD total compensation, escalation rate and costliest category
    RETURN the lines, joined with new lines
```

```python reveal title="session.py · ask 2 · real aggregation"
daily_log = []   # one structured dict per processed exception (a DB table in real life)

def record(final_state: dict) -> None:
    daily_log.append(final_state)

def generate_daily_summary() -> str:
    if not daily_log:
        return "No exceptions processed yet today."

    total = sum(s["compensation_amount"] for s in daily_log)
    escalated = [s for s in daily_log if s["needs_approval"]]
    escalation_rate = len(escalated) / len(daily_log) * 100

    by_category = {}
    for s in daily_log:
        by_category[s["category"]] = by_category.get(s["category"], 0) + s["compensation_amount"]
    costliest = max(by_category, key=by_category.get)

    lines = [f"**Daily triage summary** - {len(daily_log)} exceptions processed", ""]
    for s in daily_log:
        status = "ESCALATED" if s["needs_approval"] else "auto-resolved"
        lines.append(f"- {s['category']} - ${s['compensation_amount']:,.2f} - {status}")
    lines += ["",
              f"Total compensation: ${total:,.2f}",
              f"Escalation rate: {escalation_rate:.0f}%",
              f"Costliest category: {costliest} (${by_category[costliest]:,.2f})"]
    return "\n".join(lines)
```

Total compensation

sum of `compensation_amount`

Escalation rate

escalated ÷ processed × 100

Costliest category

argmax of per-category totals

What goes in the summary was left open, because the readers are the company's own staff, not customers. Add whatever an operations lead would want: average payout per tier, the single largest claim, how many unknowns came in. You can format it with plain Python, render a chart, or hand the structured log to an LLM to narrate. The structure is what makes all three possible.

Production reality

In production, `daily_log` is a table and `record()` is an insert. Two things change when you make that move. Records need a **timestamp**, because “daily” has to mean a date and not “since the server restarted”. And they need an **id**, so that processing the same report twice is detectable. Paying twice is the failure Class 9 is built around.

Ask 3 · the interface

## A form, an outcome, a log

```pseudo title="app.py"
DEFINE on_submit(report_text, shipment_value, customer_tier):
    IF report_text is blank THEN
        RETURN "Please paste an exception report first", the current log, and the report text unchanged
    SET result = process_exception(report_text, shipment_value, customer_tier)
    CALL record(result)
    SET status = "Escalated to manager" IF needs_approval, ELSE "Auto-resolved"
    SET outcome = status, category, amount with reasoning, drafted message and steps
    RETURN outcome, the triage log, and an empty report box

DEFINE format_triage_log():
    FOR EACH entry in daily_log, numbered from 1:
        ADD one line: status, category, amount and tier
    RETURN the lines, or "Nothing processed yet." when the log is empty

CREATE demo = a Gradio page titled "Shipment Exception Desk"
    ADD the report box, next to a column with the value box and the tier choice
    ADD the "Process exception" button, SEND the three inputs to on_submit
    ADD the outcome panel, the triage log and the "Generate daily summary" button
    SEND the summary button to generate_daily_summary, shown in the summary box
IF this file is run directly THEN
    RUN demo.launch()
```

> **Imported:**
> - `gradio` (as `gr`) package gradio: builds the web page from text boxes, buttons and Markdown panels.
> - `process_exception` from `pipeline`: runs the whole exception flow for one report.
> - `daily_log` from `session`: the list of processed exceptions that the triage log is printed from.
> - `record` from `session`: adds one result to `daily_log`.
> - `generate_daily_summary` from `session`: builds the daily summary text.

```python reveal title="app.py · ask 3 · python app.py"
import gradio as gr

from pipeline import process_exception
from session import daily_log, record, generate_daily_summary

def format_triage_log() -> str:
    lines = []
    for i, s in enumerate(daily_log, 1):
        status = "ESCALATED" if s["needs_approval"] else "auto-resolved"
        lines.append(f"{i}. **{status}** - {s['category']} - "
                     f"${s['compensation_amount']:,.2f} ({s['customer_tier']})")
    return "\n".join(lines) or "_Nothing processed yet._"

def on_submit(report_text, shipment_value, customer_tier):
    if not report_text.strip():
        return "Please paste an exception report first.", format_triage_log(), report_text
    result = process_exception(report_text, float(shipment_value), customer_tier)
    record(result)
    status = "Escalated to manager" if result["needs_approval"] else "Auto-resolved"
    outcome = (f"### {status}\n"
               f"**Category:** {result['category']}  \n"
               f"**Compensation:** ${result['compensation_amount']:,.2f} - "
               f"{result['compensation_reasoning']}\n\n"
               f"**Drafted message**\n\n{result['drafted_message']}\n\n"
               f"**Steps:** " + " -> ".join(result["log"]))
    return outcome, format_triage_log(), ""

with gr.Blocks(title="Shipment Exception Desk") as demo:
    gr.Markdown("# Shipment Exception Desk")
    with gr.Row():
        report_box = gr.Textbox(label="Exception report", lines=5, scale=3)
        with gr.Column(scale=1):
            value_box = gr.Number(label="Shipment value ($)", value=800)
            tier_box = gr.Radio(["standard", "premium"], value="standard", label="Customer tier")
    submit_btn = gr.Button("Process exception", variant="primary")
    outcome_box = gr.Markdown()
    gr.Markdown("### Triage log")
    log_box = gr.Markdown(format_triage_log())
    summary_btn = gr.Button("Generate daily summary")
    summary_box = gr.Markdown()

    submit_btn.click(on_submit, inputs=[report_box, value_box, tier_box],
                     outputs=[outcome_box, log_box, report_box])
    summary_btn.click(generate_daily_summary, outputs=summary_box)

if __name__ == "__main__":
    demo.launch()
```

1 **Validate before you spend** An empty report returns immediately with a message. Otherwise you'd pay for an LLM call to classify nothing, and get unknown plus an escalation for your trouble.

2 **The UI only formats** `on_submit` calls the pipeline, records the result and renders it. No business logic lives in `app.py`, so swapping Gradio for Streamlit or a REST API touches one file.

3 **`gr.Row` / `gr.Column(scale=…)`** The report box takes three-quarters of the width, and value and tier stack in the remaining quarter. That's all the layout this app needs.

#### Terminal test

```pseudo title="main.py"
SET SAMPLES = three cases, each with a report, a shipment value and a tier

FOR EACH report, value, tier in SAMPLES:
    SET r = process_exception(report, value, tier)
    CALL record(r)
    PRINT ESCALATE or AUTO, the category and the amount
    PRINT each step in the log, one per line
    PRINT the drafted message
PRINT generate_daily_summary()          // totals for all three runs
```

> **Imported:**
> - `process_exception` from `pipeline`: runs the whole exception flow for one report.
> - `record` from `session`: adds each result to the daily log.
> - `generate_daily_summary` from `session`: builds the summary printed at the end.

```python reveal title="main.py · milestones 5–6 · python main.py"
from pipeline import process_exception
from session import record, generate_daily_summary

SAMPLES = [
    ("Package arrived 2 days later than the estimated delivery date. Customer just flagged it.", 800, "standard"),
    ("URGENT: medical kit arrived three days late, patient had to wait.", 1500, "premium"),
    ("The crate was crushed and the glass panels are unusable.", 320, "standard"),
]

for report, value, tier in SAMPLES:
    r = process_exception(report, value, tier)
    record(r)
    print(f"\n[{'ESCALATE' if r['needs_approval'] else 'AUTO'}] {r['category']} "
          f"${r['compensation_amount']:,.2f}")
    print("  " + "\n  ".join(r["log"]))
    print(r["drafted_message"])

print("\n" + generate_daily_summary())
```

#### The triage check

Four reports, one per category, each with the outcome *your* rules should produce. If you change the thresholds or rates, update the expectations. The scenarios encode your policy, not the instructor's.

```pseudo title="triage_check.py"
SET SCENARIOS = four cases, each with a report, value, tier, expected category and expected escalation
SET passed = 0

FOR EACH scenario in SCENARIOS:
    SET r = process_exception(report, value, tier)
    SET ok = TRUE IF category matches the expected category AND escalation matches the expected escalation
    ADD ok to passed          // 1 for a pass, 0 for a fail
    PRINT PASS or FAIL, the expected and got values, and the amount
PRINT passed, the total number of scenarios, and "scenarios behave as designed"
```

> **Imported:**
> - `process_exception` from `pipeline`: the flow under test, run once per scenario.

```python reveal title="triage_check.py · milestone 8 · python triage_check.py"
from pipeline import process_exception

# label, report, value, tier, expected category, expected escalation
SCENARIOS = [
    ("routine delay", "Package arrived 2 days after the estimated date. Just flagging it.",
     800, "standard", "delayed", False),
    ("severe damage", "Box was crushed and the monitor inside is shattered.",
     450, "standard", "damaged", True),
    ("lost, premium", "Tracking stopped a week ago and the parcel never arrived.",
     90, "premium", "lost", False),
    ("unclassifiable", "Your driver parked on my lawn.",
     60, "standard", "unknown", True),
]

passed = 0
for label, report, value, tier, want_cat, want_esc in SCENARIOS:
    r = process_exception(report, value, tier)
    ok = r["category"] == want_cat and r["needs_approval"] == want_esc
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'}  {label:15} expected {want_cat}/{'esc' if want_esc else 'auto'}"
          f"  got {r['category']}/{'esc' if r['needs_approval'] else 'auto'}"
          f"  ${r['compensation_amount']:,.2f}")
print(f"\n{passed}/{len(SCENARIOS)} scenarios behave as designed")
```

*expected output with the rules on this page* **PASS** routine delay expected delayed/auto got delayed/auto $40.00 **PASS** severe damage expected damaged/esc got damaged/esc $450.00 **PASS** lost, premium expected lost/auto got lost/auto $90.00 **PASS** unclassifiable expected unknown/esc got unknown/esc $0.00 4/4 scenarios behave as designed

A failure here has two possible causes: the model classified differently, or your rules computed differently. The printed `got` category tells you which. If the category matches but the escalation doesn't, the bug is in your code.

Judgement calls

## Six decisions people get wrong

| Decision | Tempting answer | What it should be |
| --- | --- | --- |
| **Who computes the refund** | Give the model the policy and let it calculate. | Code. A model can hallucinate a number, and a payout must be identical for identical cases. |
| **One prompt or three** | One prompt: classify, price and write the email at once. | Three chains with one job each, plus code in between. Each piece can be tested, and the money step isn't in a prompt. |
| **Trusting the classifier** | `if raw == "delayed"` | Normalise, then check membership in an allowed set, falling back to `unknown`. “Delayed.” with a full stop would otherwise escalate every delay. |
| **When unsure** | Pick the closest category. | unknown → $0 → manager. Escalating is the cheap mistake. |
| **Calculator returns** | `return f"Refund ${amt}"` | `{"amount": …, "reasoning": …}`. The threshold and the summary need a number. |
| **Where to start** | The UI, because it's the demo. | The calculators, standalone. The UI is the last layer. |

#### Where it goes next

- **Structured classification.** Ask for a typed enum (for example with `llm.with_structured_output(…)`) instead of parsing one word. The guard stays anyway.
- **Mixed reports.** “Arrived a week late *and* the lid is cracked” is two exceptions. Extract each one, price each, and sum them. That's the extraction step Class 9 starts from.
- **An approval queue.** Escalations land in a manager view with approve and reject buttons, and only an approval releases the payment.
- **Idempotency and timestamps.** Key each exception by a hash of the report plus the shipment id, so a double-click never pays twice.
- **LangGraph.** The if/else branch is a two-node graph. Once there are retries, approvals and loops, a graph framework earns its place, which is exactly where the weekend projects begin.

Self-check

## Eight questions before you build it yourself

#### Which two of the four decisions does the LLM make, and why only those?

Classifying the report and writing the message, because both are language tasks. The compensation and the escalation decision are money and policy, so they're deterministic code.

#### The classifier returns “Damaged.” What does the pipeline do?

`.strip().lower().strip(".")` gives `damaged`, which is in `CALCULATORS`, so it routes to `damage_compensation`. Without the normalisation it would fall through to `unknown` and escalate.

#### A $1,500 premium delay marked “URGENT”. Amount and outcome?

5% × 2 = 10% → $150. The premium threshold is $100, so it escalates to a manager with an internal note.

#### Why must the calculators return dicts?

The pipeline compares `amount` with a threshold, the summary adds amounts up, and the chains need `reasoning` as a separate field. A formatted string would have to be parsed back into a number.

#### What is the `|` in `prompt | llm | StrOutputParser()`?

LangChain's expression language composes runnables into a chain. The output of each step is the input to the next: the template becomes messages, the model returns an AI message, and the parser turns that into a string.

#### Why does an empty report return early in `on_submit`?

To avoid paying for an LLM call on nothing, and to avoid logging a meaningless escalation.

#### A triage-check scenario fails. How do you tell whether the model or your rules caused it?

Compare the printed `got` category with the expected one. If the category is wrong, it's the classifier, so look at the prompt. If the category is right but the escalation or amount is wrong, it's your code.

#### Why did Shivank say Python knowledge still matters when AI writes the code?

Because generated code has to be reviewed. It's often syntactically fine but logically wrong or not production-ready. He spends about 40% of his time reading AI-written code, and AI-focused roles increasingly interview in Python only.

AI Infusion · Class 8 — live project session. It opened with Shivank on why project sessions matter, the FDE role, Python in AI hiring, and a preview of the planned weekend intensives. Shijan then presented the Shipment Exception Desk brief, milestones and solution walkthrough. The code on this page is a cleaned, runnable reconstruction of the walkthrough (checked against a stubbed model), not the official solution zip. The rates and thresholds are one defensible policy, and the brief asked you to design your own.
