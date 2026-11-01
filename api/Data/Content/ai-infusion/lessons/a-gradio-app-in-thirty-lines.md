# A Gradio app in thirty lines

## A Gradio app in thirty lines

```pseudo title="app.py"
DEFINE on_submit(complaint, order_id):
    SET result = resolve_dispute(complaint, order_id)
    SET rows = one row per grievance saved in the ledger: id, text, category, votes, ruling or UNRESOLVED, amount
    SET header = the status, the refund, the amount held and the dispute id
    IF the result was replayed THEN add "replayed - no new payment" to the header
    RETURN header, rows and the customer message

CREATE the Gradio page titled "The Refund Bench":
    ADD a text box for the complaint, filled with SAMPLE_COMPLAINT
    ADD a dropdown of the orders, set to ORD-1840
    ADD a "Resolve dispute" button, a status line, a read-only table and a message box
    WHEN the button is clicked, CALL on_submit and show its three results

IF this file is run directly THEN START the page
```

> **Imported:**
> - `gradio` third-party package (as `gr`): builds the web page from Python objects.
> - `ledger` the local file ledger.py: reads the grievance rows for the table.
> - `ORDERS` from `evidence`, the local file evidence.py: the order list for the dropdown.
> - `SAMPLE_COMPLAINT` from `evidence`, the local file evidence.py: pre-fills the complaint box.
> - `resolve_dispute` from `pipeline`, the local file pipeline.py: the whole flow behind the button.

```python reveal title="app.py · step 10 · python app.py"
import gradio as gr

import ledger
from evidence import ORDERS, SAMPLE_COMPLAINT
from pipeline import resolve_dispute

def on_submit(complaint, order_id):
    result = resolve_dispute(complaint, order_id)
    rows = [[g["grievance_id"], g["text"], g["category"], g.get("votes", "-"),
             g.get("ruling") or "UNRESOLVED", g.get("amount")]
            for g in ledger.get_grievances(result["dispute_id"])]
    header = (f"### {result['status']}{'  (replayed - no new payment)' if result.get('replayed') else ''}\n"
              f"**Refund:** Rs {result['refund_amount']}  ·  **Held for an agent:** Rs {result['held_amount']}  ·  "
              f"`{result['dispute_id']}`")
    return header, rows, result.get("message") or ""

with gr.Blocks(title="The Refund Bench") as demo:
    gr.Markdown("# The Refund Bench")
    complaint = gr.Textbox(label="Customer complaint", value=SAMPLE_COMPLAINT, lines=5)
    order = gr.Dropdown(list(ORDERS), value="ORD-1840", label="Order")
    go = gr.Button("Resolve dispute", variant="primary")
    status = gr.Markdown()
    table = gr.Dataframe(headers=["id", "grievance", "category", "votes", "ruling", "Rs"],
                         interactive=False, wrap=True)
    message = gr.Textbox(label="Message to the customer", lines=4)
    go.click(on_submit, inputs=[complaint, order], outputs=[status, table, message])

if __name__ == "__main__":
    demo.launch()
```

The app only formats what the pipeline returns. Press the button twice and the header says *replayed - no new payment*, which is F9 visible in the UI. All the business logic stays in `pipeline.py`, so replacing Gradio with a REST endpoint (Part 1's “thin API”) touches only this file.

Try it

## Rule on the case yourself

Set each judge's vote, mark a call as failed, change the cap or the number of missing biryanis. The tally, pricing, cap and 60% rule below are a line-for-line port of `bench.py`, `pricing.py` and step 6 of `pipeline.py`. The defaults are the case study.

**THE BENCH** · code half only K = 3

Biryanis missing (g2)

(1 / 2 / 3 / 4)

Auto-approve cap (₹)

2000

> **Note:**
> Try “Split every bench”: U, R, E on every grievance means no majority anywhere, so nothing is paid and everything is held. Then fail two of g2's judges as well as g3's: only 2 of 4 grievances resolve, which is below 60%, so the whole dispute goes to an agent.

**Escalated, refund over the cap:** Refund ₹… exceeds the ₹… cap: a human approves, whatever the bench said.

**Escalated, too few grievances resolved:** Only … of … grievances resolved (…% < 60%): the whole dispute goes to an agent.

**Settled:** … of … resolved (…% ≥ 60%), under the cap: pay ₹… now, or nothing was upheld, so nothing is paid; hold ₹… for an agent when anything is held.

Milestones & shipping

## Ten milestones, then post it

| M | Milestone | Done when |
| --- | --- | --- |
| M1 | Environment and first call | the model says hi |
| M2 | Evidence snapshot | `21:40` prints |
| M3 | Money rules | `check_rules.py`: 12/12 |
| M4 | LLM wrapper and prompts | JSON parses, even with fences |
| M5 | Three stages | 4 grievances from the sample |
| M6 | Evals | 0 false rejects; you can explain every miss |
| M7 | Ledger and payments | `ledger.db` has four tables |
| M8 | Pipeline | ₹689 paid, ₹60 held |
| M9 | Replay, outage and crash proofs | `bench_check.py` green; resume works |
| M10 | Gradio app | submit twice → “replayed” |

#### Ship it to LinkedIn (same 3 steps as Classes 1–3)

1. Push the repo with a README containing the architecture diagram and your eval table.
2. Record 30 seconds: submit the complaint, show the grievance table, submit again to show “replayed”.
3. Post it. A caption to adapt:

I built an AI refund adjudicator that can't pay twice. One complaint → atomic grievances → 3 independent LLM judges each → majority vote in code. The model never touches the money: pricing, a ₹2,000 cap and idempotency keys are plain Python. My eval: bench accuracy [x/8] vs single judge [y/8], with **0 honest claims refused**. Built in #AIInfusion · repo in comments

Extensions · your homework

## Four upgrades, each one file

| Upgrade | Touches | Hint |
| --- | --- | --- |
| **Judges from different providers** | `llm.py`, `stages.py` | Pass a model name per `judge_index`. Re-run `eval_judge.py`: do false approvals drop when blind spots stop correlating? |
| **Judges with tools** | `stages.py` | Class 7's tool-calling loop inside `judge_grievance`, with `get_delivery_timeline()` and friends. Log every tool result into the snapshot to keep it reproducible. |
| **A real queue** | new `worker.py` | The API writes the dispute and enqueues the id; a worker loop calls `resolve_dispute`. The pipeline doesn't change, because it already resumes from the ledger. |
| **An eval gate in CI** | `.github/workflows` | Run `eval_judge.py` on every pull request that touches `prompts.py`. The non-zero exit fails the build. |

Self-check

## Eight questions on the build

#### Why are `pricing.py` and `bench.py` built and tested before any LLM code?

They decide money and need no API key. Proving them first means any later wrong refund must come from extraction or judging: fewer suspects, and no tokens spent finding them.

#### Which requirement forced the extraction schema to change, and how?

F5: price from the order, in code. Code can't price a sentence, so extraction now returns `item` and `quantity`. The model names what is affected, and code looks up what it costs.

#### Two judges return results and one call times out. What does `tally` return, and what happens next?

`None`, so the grievance is unresolved, not rejected. If at least 60% of the dispute's grievances are resolved and the refund is under the cap, the rest is paid and this one's amount is held for an agent.

#### Why do the judges run at temperature 0.7 but extraction at 0?

At T=0 the three judges would give identical answers and the vote would carry no information. Extraction should return the same grievances every time, so it runs at 0.

#### What is the eval gate, and why does it fail only on false rejects?

`eval_judge.py` exits non-zero if the bench refused any claim the golden set says is valid. That's the costly error. False approvals are bounded by the cap and human review, so they're tracked rather than gated.

#### The customer double-clicks “submit”. Name both things that stop a second payment.

The ledger returns the settled dispute without re-running it, and the payment provider ignores a repeated idempotency key (the `dispute_id`).

#### The worker dies after 5 of 12 judge calls. How many calls does the retry make, and why?

Seven. Each ruling is saved the moment it completes, and the retry skips every (grievance, judge) slot already in `judge_rulings`.

#### `bench_check.py` shows ₹749 instead of ₹689. Is the code broken?

Probably not. The bench upheld the raita 2–1 on that run. Check the votes in the ledger. If the ruling was wrong for that evidence, add the case to the golden set and improve the judging prompt or the model, not the arithmetic.

Teaching case study. Part 1 is built on the agentic system-design pattern from Arpit Bhayani's Applied AI Masterclass, session 1. Self-consistency: Wang et al., 2022. The dispute, the order and all figures are invented for teaching; the ₹ amounts are internally consistent so the arithmetic can be checked live. Part 2's code is a runnable reconstruction of Part 1's design, checked end-to-end against a stubbed model (replay, outage and crash-resume included). Run the evals with your own key before trusting any numbers.

> **Lesson resources · Lesson 10 · Build & evaluate the bench:**
> - [Watch the Class 10 · part 1 recording](https://www.scaler.com/meetings/i/ai-infused-learning-10/archive)
> - [Watch the Class 10 · part 2 recording](https://www.scaler.com/meetings/i/ai-infused-learning-10-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

Class 10 continues Class 9, so both live on one page, as Classes 3 and 4 do.

[Go to Class 10 · Build the Refund Bench, step by step →](/chapter/ai-infusion/lessons-09-10-refund-bench/why-does-a-serious-court-seat-three-judges)
