# You have two hours. Solve it in front of us.”

> **Lesson resources · Lesson 8 · The shipment exception desk:**
> - [Watch the Class 8 recording](https://www.scaler.com/meetings/i/ai-infused-learning-8/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

AI Infusion · Class 8 · Live project session

#### The model reads the ticket. *Code* signs the refund.

A customer reports a late, broken or missing parcel. One LLM call works out what kind of problem it is. Python computes the compensation and decides whether a manager has to approve it. A second LLM call writes the customer email or the internal escalation note. Built live with LangChain and Gradio.

**Stack** Python · LangChain · Groq · Gradio **LLM calls** 2 per exception **Decisions the model makes** 1 **Scope** 9 milestones

Before the build

## “You have two hours. Solve it in front of us.”

Shivank opened with a concern rather than a topic: many learners had treated the previous project session as optional. It isn't, and the reason is how hiring has changed.

Interviews for AI roles increasingly look like this: *here's the data, here's the problem statement, you have two hours, think out loud.* You can't answer “I only do take-home assignments.” The same is true of the job. He pointed at the **Forward Deployed Engineer** (FDE) role that's appearing across the market, where you sit with a client, sometimes with their CXOs, and write code in front of them while they ask you questions.

Building live is uncomfortable for everyone, instructors included. That's the point of practising it in class first.

Asked in class

“Claude and Cursor can write code in any language. Why do AI companies now insist on Python?”

Because the AI ecosystem lives in Python, and because generated code still has to be **read**. Shivank estimated that about **40% of his own working time** goes into reviewing AI-written code, line by line. The model writes syntactically correct code that's often logically wrong, or works but isn't fit for production. You can't review a language you can't read. More and more AI-focused job descriptions now say “Python” where they used to say “Java, Python or Scala.”

For anyone joining at this class

A learner from a Java background asked why they were in an AI session. The answer from the room: AI now touches every layer of a product, from the user-facing edge to internal tooling. Even when you aren't building models, you need enough hands-on context to follow what stakeholders are deciding and to connect it to your own system. The only prerequisite for this track is one programming language.

Preview · not final

## What the weekend intensives will build

To speed up placement-readiness, Shivank is planning **hands-on weekend intensives** of roughly 16 hours, possibly over two or three weekends. They'll be online, with an optional in-person room in Bangalore and at least 10 days' notice. He flagged it as *still in planning*, and asked people not to raise support tickets about it yet. He showed the first of two projects so you can see the scale.

{{diagram:1}}

*“Write a blog post” sounds trivial until you draw it. Run the research agent 40 times and you get 40 different source sets, yet the article has to come out factually right every time. Long drafts are full of mistakes, so the writer has to find them, fix them, and decide when to stop.*

| Hard part | Why it's hard |
| --- | --- |
| **Reliable research** | A ReAct loop has no fixed order: act, observe, decide it isn't good enough, go again. Non-determinism is the default. The design has to make the *result* reliable even when the path isn't. |
| **Choosing what to keep** | Finding 47 relevant sources is easy. Writing from all 47 is expensive and worse. The agent has to decide what to drop. |
| **Long-form writing** | Large outputs carry many mistakes. The writer needs checkpoints, a review step with explicit guidelines, and a stopping condition. That's why it uses LangGraph rather than a single prompt. |
| **Cost control** | Beyond model choice, **reasoning effort** is a dial on every call, set per step. High everywhere is how a demo turns into a bill. |

The second planned project is a **deep RAG system** with no agents: a chatbot that answers from an entire body of teaching content. It's the kind of system a learner's company was struggling with, including when fine-tuning becomes necessary. His advice on both projects: **don't all put the identical project on your résumé.** Use them to learn the pattern, then rebuild it around your own idea, or on AWS once that track is done.

The brief

## A support desk for parcels that went wrong

Think of the support chats you've had with Amazon, Swiggy, Zepto or Instamart. Agents handle most of those tickets behind the scenes, and a few still need a human. This project builds that shape for a logistics company:

1. **Classify** a customer's exception report as delayed damaged lost or unknown.
2. **Calculate compensation** using the company's business rules for that category.
3. **Decide** whether it is safe to auto-resolve, or must be escalated to a manager.
4. **Draft** the right message: a customer-facing email, or an internal note asking for approval.
5. **Keep a log** of every decision, and summarise the day on demand.

#### The demo case

**VALUE** $800.00 **TIER** standard **OUTCOME** auto-resolved

“Package arrived 2 days later than the estimated delivery date and the customer just flagged the delay for the record.”

Category

delayedLLM · classify_chain

Compensation

$405% of $800 · code

Threshold

$200standard tier · code

Message

emailLLM · draft_email_chain

$40 is under the standard customer's $200 threshold and the category is known, so no human is needed. The customer gets an email and the triage log gets a line. Every number on that card came from code. The model chose one word and wrote one paragraph.

The hook

## Four decisions, two owners

Every exception involves four decisions. Before writing any code, decide which of them you would trust a language model with.

| Decision | Owner | Why |
| --- | --- | --- |
| What kind of problem is this? | LLM | Customers describe the same problem a hundred ways (“never showed up”, “tracking froze”, “not here yet”). Reading messy language is what models are for. |
| How much do we pay? | code | Money must be deterministic, auditable and identical for identical cases. Compensation rules are company policy, and they belong in reviewed code. |
| Does a manager sign off? | code | A threshold is a business rule with real cost. You don't want it to vary with a model's mood. |
| What do we say? | LLM | Tone, acknowledgement and clarity are language work. The model gets the amount as an input and is told not to change it. |

Asked in class

“Could the model also detect urgency, or judge how severe the damage sounds?”

It could, but that puts a model's judgement straight into the money path, where it can hallucinate. The solution keeps urgency and severity as keyword rules in `tools.py`: crude, but deterministic and reviewable. In situations where money moves, you want determinism and hard rules, and you keep the model out of the decision. Last class's rule was “tools measure, the model explains.” This class it becomes **the model reads, code pays.**

The asks

## Three asks, no starter code

The problem was small enough that no starter code was provided. You got the brief, a README and `requirements.txt`, and wrote every file yourself.

| # | Ask | What “done” means |
| --- | --- | --- |
| 1 | **Exception-processing pipeline** | `chains.py` holds three LangChain chains: classify, escalate, draft email. `tools.py` holds three compensation calculators that each return a *structured dict, not a formatted string*. `pipeline.py`'s `process_exception()` classifies, routes to the right calculator, applies a tier threshold, sends unknown straight to a manager, and calls the right drafting chain. |
| 2 | **Real daily aggregation** | `session.py` records every processed exception and computes total compensation paid, escalation rate, and the costliest category by total compensation. `triage_check.py` runs four reports with stated expected outcomes against your pipeline. |
| 3 | **Working Gradio interface** | `app.py`: a form with report text, shipment value and customer tier, an outcome panel, the running triage log and a daily-summary button. Any UI framework you're comfortable with is acceptable. |

Much of it was intentionally open-ended: the compensation formulas, the escalation rule, what goes in the summary, even extra form fields. Business rules differ from company to company, so the brief asked you to **design them** rather than copy them. The rules below are one defensible set, not the answer key.

Architecture

## Two LLM calls with code in between

{{diagram:2}}

*The model sits at the two ends, reading language in and writing language out. Everything in the middle, where money and approval are decided, is plain Python with constants a reviewer can read.*

shipment-exception-desk/ ├── .env *# GROQ_API_KEY=…* ├── requirements.txt *# langchain-core, langchain-groq, gradio, python-dotenv* ├── llm.py *# the one model object every chain shares* ├── chains.py *# classify · escalate · draft email* ├── tools.py *# delay · damage · lost calculators* ├── pipeline.py *# process_exception(): the wiring* ├── session.py *# daily_log, record(), generate_daily_summary()* ├── main.py *# terminal test of the pipeline* ├── triage_check.py *# four scenarios with expected outcomes* └── app.py *# Gradio UI — built last*

#### Milestones, in the order to build them

| M | Build | Prove it |
| --- | --- | --- |
| M1 | venv, `pip install -r requirements.txt`, `.env` with the API key | imports work inside the venv |
| M2 | `delay_compensation` | `python tools.py`: each calculator alone, with known inputs and expected amounts. No LLM. |
| M3 | `damage_compensation` |  |
| M4 | `lost_compensation` |  |
| M5 | `pipeline.py`: classify + compensate, *single path* (always draft the email) | `python main.py` |
| M6 | Add the escalation branch: threshold or unknown → manager note | `python main.py` |
| M7 | `session.py`: `generate_daily_summary()` with real aggregation | summary after a few runs |
| M8 | `triage_check.py`: delayed · damaged · lost · unknown | `python triage_check.py` |
| M9 | `app.py`: the full flow in a browser | `python app.py` |

Same rule as last class

Get the three calculators working and tested **on their own** before any chain touches them. If you wire everything together and the refund is wrong, you won't know whether the classifier, the calculator or the threshold is to blame, and every guess costs API tokens. The UI is the last layer. You can start from the UI if you prefer, but then you're debugging back-end wiring through a browser.

Milestones 2–4 · tools.py

## Company policy, written as constants

Each calculator takes the shipment value and the report text and returns `{"amount", "reasoning"}`. The amount drives the escalation decision. The reasoning travels into both the email and the manager's note, so the humans downstream can see *why*.

```pseudo title="tools.py"
SET DELAY_BASE_RATE = 5% of the shipment value, URGENT_MULTIPLIER = 2
SET URGENT_SIGNALS, SEVERE_DAMAGE_KEYWORDS and MINOR_DAMAGE_KEYWORDS = lists of words

DEFINE delay_compensation(shipment_value, report_text):
    SET text = report_text in lower case
    SET urgent = TRUE IF any urgent signal appears in text
    SET rate = DELAY_BASE_RATE, doubled when urgent
    SET amount = shipment_value × rate, rounded to 2 decimals
    RETURN a dict with amount and reasoning

DEFINE damage_compensation(shipment_value, report_text):
    SET text = report_text in lower case
    IF any severe keyword appears in text THEN
        SET rate = 100%
    ELSE IF any minor keyword appears in text THEN
        SET rate = 25%
    ELSE
        SET rate = 50%          // unclear severity: a deliberate policy choice
    SET amount = shipment_value × rate, rounded to 2 decimals
    RETURN a dict with amount and reasoning

DEFINE lost_compensation(shipment_value, report_text):
    SET amount = shipment_value, rounded to 2 decimals
    RETURN a dict with amount and reasoning

IF this file is run directly THEN
    PRINT each calculator on known inputs     // prove each one alone, no LLM
```

```python reveal title="tools.py · milestones 2–4 · python tools.py"
# Company policy, written as code. The LLM never computes money.
DELAY_BASE_RATE = 0.05                 # 5% of shipment value
URGENT_MULTIPLIER = 2
URGENT_SIGNALS = ["urgent", "critical", "time-sensitive", "time sensitive", "asap", "medical"]

SEVERE_DAMAGE_KEYWORDS = ["destroyed", "shattered", "crushed", "unusable"]
MINOR_DAMAGE_KEYWORDS = ["scratch", "dent", "scuff", "torn packaging"]

def delay_compensation(shipment_value: float, report_text: str) -> dict:
    text = report_text.lower()
    urgent = any(signal in text for signal in URGENT_SIGNALS)
    rate = DELAY_BASE_RATE * (URGENT_MULTIPLIER if urgent else 1)
    amount = round(shipment_value * rate, 2)
    reasoning = (f"Delay compensation at {rate:.0%} of the ${shipment_value:,.2f} shipment value"
                 f"{' (urgent signal detected, rate doubled)' if urgent else ''}.")
    return {"amount": amount, "reasoning": reasoning}

def damage_compensation(shipment_value: float, report_text: str) -> dict:
    text = report_text.lower()
    if any(k in text for k in SEVERE_DAMAGE_KEYWORDS):
        rate, tier = 1.0, "severe"
    elif any(k in text for k in MINOR_DAMAGE_KEYWORDS):
        rate, tier = 0.25, "minor"
    else:
        rate, tier = 0.5, "unclear severity"
    amount = round(shipment_value * rate, 2)
    reasoning = f"Damage compensation ({tier}) at {rate:.0%} of the ${shipment_value:,.2f} shipment value."
    return {"amount": amount, "reasoning": reasoning}

def lost_compensation(shipment_value: float, report_text: str) -> dict:
    amount = round(float(shipment_value), 2)
    return {"amount": amount, "reasoning": f"Lost shipment: full value of ${amount:,.2f} refunded."}

if __name__ == "__main__":
    # Milestones 2-4: prove each calculator before any chain touches it.
    print(delay_compensation(800, "Package arrived 2 days late."))          # 40.0
    print(delay_compensation(800, "URGENT medical supplies arrived late"))  # 80.0
    print(damage_compensation(400, "The vase was shattered"))               # 400.0
    print(damage_compensation(400, "small scratch on the lid"))             # 100.0
    print(lost_compensation(1250, "never arrived"))                         # 1250.0
```

1 **Every rate is a named constant at the top** When finance changes the delay rate from 5% to 7%, it's a one-line diff in a reviewed pull request, not a prompt edit that silently changes every future payout.

2 **Severity from wording: crude on purpose** “Shattered” → 100%, “scratch” → 25%, anything else → 50%. Keyword rules will misjudge some reports. But they misjudge *consistently* and visibly, and the 50% default for unclear severity is an explicit policy choice, not an accident.

3 **Check severe before minor** “Crushed box, a few scratches on the casing” contains both. The first matching branch wins, so the order of the `if` s is itself a rule: the worse reading takes priority.

4 **A dict, not an f-string** The pipeline needs `amount` as a number to compare with a threshold, and the summary needs it to add up totals. A sentence like “Refund $40 because…” would have to be parsed back. That's why the brief insisted on structured returns.

Try it
