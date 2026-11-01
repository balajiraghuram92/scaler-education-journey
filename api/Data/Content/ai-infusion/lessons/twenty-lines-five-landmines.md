# Twenty lines, five landmines

## Twenty lines, five landmines

The pseudocode is the happy path. The annotations are where the money lives.

```text
1dispute_id = hash(complaint_text + order_id)

1if ledger.get(dispute_id).status == SETTLED:
     return ledger.get(dispute_id).settlement  # never pay twice

2evidence = evidence_service.snapshot(order_id)
 ledger.save(dispute_id, evidence, status=INTAKE)

3grievances = grievance_extractor.run(complaint_text, evidence.line_items)
 ledger.save(dispute_id, grievances, status=JUDGING)

4judging_tasks = []
 for g in grievances:
     for judge_index in range(K):
         judging_tasks.append((g, evidence, judge_index))

 rulings = parallel_execute(judge_grievance, judging_tasks,
                           batch_size=BATCH_SIZE)

5verdicts = bench.tally(rulings)
5amount   = pricing.compute(verdicts, evidence)   # code, not LLM
5if amount > AUTO_APPROVE_CAP:  return escalate(dispute_id)
 ledger.save(dispute_id, verdicts, amount, status=TALLIED)

 message = settlement_writer.run(complaint_text, verdicts, amount)
 payments.refund(dispute_id, amount)   # idempotency key = dispute_id
 ledger.save(dispute_id, message, status=SETTLED)
```

1 **Idempotency is not an optimisation here — it is the product** The complaint's own text is its key. In the fact-checker, a duplicate run wasted API credits. Here it *wires money out of the company twice*. The same key is also passed to the payments API, so even a double call at that layer settles once.

2 **Evidence is frozen once, before any judging** All K judges on all N grievances see the identical snapshot. Re-fetch per call and a retry can legitimately produce a different verdict on the same dispute — which is indefensible when someone asks why.

3 **Grievances are persisted before judging begins** For resumption and for the customer-facing “here's what we checked.” A crashed worker must not re-extract.

4 **The K judges share nothing** No conversation history between them. If judge 2 could see judge 1's ruling it would anchor on it — and you would be counting one opinion three times instead of three opinions once.

5 **The bench counts, the pricing table calculates, the cap decides** Three things the model never touches. It rules on facts; it does not do arithmetic and it does not sign cheques.

#### Being pessimistic on purpose

| Failure | Response |
| --- | --- |
| **Worker dies mid-dispute** | State checkpoints per stage and judging is idempotent per grievance, so the job resumes where it stopped instead of re-judging from scratch. |
| **Provider returns 429** | Exponential backoff with jitter. At 2,800 calls a minute this is a daily event, not an incident. |
| **Some grievances never resolve** | Default to escalate — never to rejected. If ≥ 60% resolved and the settled amount is under the cap, pay that part now and send the remainder to an agent. A partial refund plus an honest note beats an error screen. |
| **The total exceeds ₹2,000** | Stop. A human approves. No confidence score, no unanimous bench, no amount of model certainty overrides this — it is a hard ceiling in code, checked before the payments call. |

Ask the room

“The bench is unanimous, confidence 0.99, and the refund comes to ₹4,500. Ship it?”

No. And the reason is not that the model might be wrong — it is that **an unbounded automated payout is an unbounded loss when something eventually goes wrong**: a prompt injection in the complaint text, a pricing bug, a bad deploy. The cap does not express distrust of the model. It caps your blast radius. Every agent that can spend money needs one.

The prompts

## Three prompts, and the one line in each that does the work

##### 1 · Extraction — the hardest one to get right

```text
You are a precise dispute-intake assistant.

Given a customer complaint and the order's line items,
extract every atomic, checkable grievance.

Rules:
- A grievance is a statement about something that happened
  to THIS order, which evidence could confirm or contradict
- Exclude feelings, opinions, demands, and rhetorical questions
- Do NOT judge whether the grievance is true — only extract it
- Each grievance must be self-contained: resolve pronouns and
  vague references against the order's line items
- Assign one category from the enum below
- Return ONLY a JSON array, no preamble, no markdown fences

Categories: LATE_DELIVERY | MISSING_ITEM | WRONG_ITEM |
            QUALITY | PACKAGING | PARTNER_CONDUCT | BILLING

Schema:
[{ "grievance_id": "<uuid>",
   "text": "<the grievance as a standalone sentence>",
   "category": "<one of the above>",
   "span_start": <char offset>, "span_end": <char offset> }]

Complaint:  {{complaint_text}}
Order:      {{line_items_json}}
```

**“Do NOT judge — only extract.”** Without it the model helpfully pre-filters: it silently drops “the delivery guy was rude” because it senses there is no evidence for it, and the grievance never reaches the bench that would have *rejected* it on the 5★ rating. Extraction and judgement are separate stages, and the prompt has to say so. **The spans** are what let the reply underline the exact sentence that was rejected.

##### 2 · Judging — run K times per grievance

```text
You are an impartial claims adjudicator.
Rule on the following grievance using ONLY the evidence given.

Grievance: {{grievance_text}}
Evidence:  {{evidence_snapshot_json}}

Rulings:
- UPHELD:   the evidence supports the grievance
- REJECTED: the evidence contradicts the grievance
- ESCALATE: the evidence is silent or ambiguous on this point

Rules:
- Do not hedge — pick the single best ruling
- Rule ONLY on the evidence provided. Do not reason about what
  is typical, likely, or fair
- If the evidence does not speak to this grievance, the ruling
  is ESCALATE — never REJECTED
- Return ONLY valid JSON, no preamble, no markdown fences

Schema:
{ "ruling": "UPHELD" | "REJECTED" | "ESCALATE",
  "confidence": <float 0.0 to 1.0>,
  "evidence_cited": "<which field(s) decided it>",
  "reasoning": "<one to three sentences>" }
```

**“Silent evidence means ESCALATE, never REJECTED.”** This single line is the asymmetry from earlier, written into the prompt. Absence of proof is not proof of absence — and the cheaper mistake is sending a case to a human, not refusing an honest customer. **`evidence_cited`** earns its place too: it forces the model to name the field it used, which makes a bad ruling debuggable instead of mysterious.

##### 3 · Settlement — once, at low temperature

```text
You are a customer-support writer for a food delivery app.

Below is a customer's complaint, the final ruling on each
grievance, and the refund amount already calculated.

Write a 3-4 sentence reply that:
- States the refund amount and when it will arrive
- Names what was resolved and what a colleague will look into
- Acknowledges the experience without grovelling

Rules:
- Do NOT re-adjudicate any ruling — treat all rulings as final
- Do NOT state, recalculate, or negotiate any amount other
  than the one given
- Never blame the restaurant or the delivery partner
- Plain language. No apology more than once.

Complaint: {{complaint_text}}
Rulings:   {{verdicts_json}}
Amount:    {{refund_amount}}
```

**“Treat all rulings as final”** is the most valuable sentence across all three prompts. Without it the model re-litigates the bench while writing — a sympathetic complaint quietly turns a 1–2 escalate into an upheld in the prose, and now your message promises a refund your ledger says you are not paying. **“Do not state any amount other than the one given”** is the same defence pointed at the number.

#### What the customer actually receives

**OUTBOUND** d7a41…c39 **SETTLED** 21:52:07 IST

We've refunded ₹689 to your original payment method — ₹640 for the two biryanis that weren't delivered and ₹49 for the delivery fee, since the order arrived well past its estimated time. It should reflect within 3 working days. On the spilled raita, we don't have enough from the order record to settle it automatically, so a colleague will review it and write to you within 24 hours.

Note what the message does *not* do: it doesn't mention g4 at all. Silently dropping a rejected grievance is a deliberate product choice — telling a customer “we checked and you're wrong about the delivery partner” wins you nothing. **The bench's ruling is for your ledger; the customer gets the outcome.**

Judgement calls

## Four decisions people get wrong

| Decision | Tempting answer | What it should be |
| --- | --- | --- |
| **How to batch** | Put all 4 grievances in one prompt, ask for 4 rulings. | No. Lost-in-the-middle is real, and a dropped grievance is a refund you silently didn't pay. Use the provider's *batch API* — separate prompts in one request, one output each. Nothing gets skipped. |
| **Batch API vs threads** | Batch endpoints are cheaper, so use them. | Check the SLA first. OpenAI and Azure batch endpoints carry a **24-hour completion window**. For a customer watching a spinner that is unusable — use parallel calls across threads and pay list price. Batch APIs belong to your overnight re-scoring jobs. |
| **Caching rulings** | “Order was late” appears in thousands of disputes — cache the ruling. | **Never.** And this is the sharpest lesson in the system. Caching needs two properties: a homogeneous corpus *and* context-free claims. “ISRO is in Bengaluru” is context-free — true regardless of the article. “Order was late” is *not* — it is true for this order and false for the next one. Homogeneity alone is a trap. |
| **Reasoning models** | Money is involved, so use the thinking model. | Overkill. The grievances are *atomic* by construction and the evidence is handed over pre-fetched — “was 21:40 more than 45 minutes after 20:15” has no reasoning chain to walk. Atomicity plus evidence does the work reasoning would have done, at a fraction of the cost and latency you cannot spare. |

Ask the room

“Last week we said caching depends on whether the corpus is homogeneous. This week the corpus *is* homogeneous and the answer is still no. Did we get it wrong last week?”

No — the test was incomplete, and this system is what exposes it. Caching needs homogeneity **and** context-independence. Fact-checking claims are context-free but the corpus is long-tailed. Refund grievances repeat constantly but each one is bound to its own order. Neither caches — for opposite reasons. *That* is the lesson worth carrying out of both case studies.

Where it goes next

## Two extensions worth the money

#### Seat judges from different courts

Three samples from one model share that model's blind spots. If a model systematically reads pickup-weight evidence badly, asking it three times gives you three confident wrong rulings, and the vote launders them into consensus. Seat one GPT judge, one Claude judge, one Kimi judge and the failures stop correlating — the same idea as a random forest, transferred intact.

Then weight them. If one model is measurably better on timestamp arithmetic and another on free-text quality complaints, weight their votes by *category*. The weights come from your own evals and stay somewhat subjective — but a weighted bench across different models is a strictly better estimator than an unweighted bench of one model three times.

#### Give the judges a tool, not a snapshot

Today all evidence is fetched up front in stage 1 — which means you fetch everything that *might* be relevant for every dispute, and a grievance about packaging still carries the full GPS trail in its prompt. Give the judge a tool call instead and it fetches only what that grievance needs: `get_delivery_timeline()` for g1, `get_pickup_weight()` for g2.

The architecture does not move. The fan-out, the bench, the checkpointing, the cap, the 60% rule — all of it still holds. Only the inside of `judge_grievance` changes. That is the sign the decomposition was right.

Production reality

The moment judges fetch their own evidence you have **lost reproducibility** — two runs can see different data. So a tool-using version must log every tool call and its response into the snapshot as it goes. You are not removing the frozen evidence; you are building it lazily.

Where else this shape fits

## Six places to seat a bench

Dispute resolution is one instance of a general pattern: *when the cost of being wrong exceeds the cost of asking again, ask again and count.*

| Use case | What the bench protects you from |
| --- | --- |
| **Insurance claim triage** | The same shape with a bigger cap and a longer clock. Split benches route to a human assessor. |
| **Loan document verification** | One model misreading one figure on one payslip and approving credit against it. |
| **Content moderation appeals** | Inconsistency — the same post restored on Monday and removed on Tuesday. |
| **Invoice / PO matching** | A line item silently skipped in a 40-row invoice, which reconciliation finds three months later. |
| **Code review risk scoring** | A P0 change scored as cosmetic because one sample skimmed the diff. |
| **Financial data extraction** | Tokenisation on numbers. “₹20,000.00” read as “₹2,000,000” because a decimal fell on a token boundary. Three judges catch it; one does not. |

Close the session

“You now have two systems — a fact checker and a refund adjudicator. Different domains, different numbers, different latency budgets. What is actually the same?”

`1 + N×K + 1`. A sequential barrier followed by a fan-out. A vote computed in code. A third verdict that means “a human decides.” Checkpoint after every stage, key everything by a content hash, back off with jitter, and never let the model near the arithmetic. **Everything else was a parameter.**

> **Lesson resources · End of Lesson 9 · Lesson 10 starts just below:**
> - [Watch the Class 10 · part 1 recording](https://www.scaler.com/meetings/i/ai-infused-learning-10/archive)
> - [Watch the Class 10 · part 2 recording](https://www.scaler.com/meetings/i/ai-infused-learning-10-2/archive)

Part 2 · Class 10 · Hands-on

Now *build* the bench

Part 1 designed the system on a whiteboard. Part 2 builds it on your laptop, one small file at a time, with a check after every step. Then you measure it with evals before you trust it with money.

Step back first

## You already know every idea in this build

Nothing in this project is new. It combines lessons from the last three classes:

| From | The lesson | Where it shows up here |
| --- | --- | --- |
| [Class 7](/chapter/ai-infusion/lesson-07-interview-coach/why-hand-an-llm-a-ruler) | Tools measure, the model explains. Build parts standalone first. | The judges give rulings; `bench.py` counts them in plain code. Money rules are tested before any LLM is wired in. |
| [Class 8](/chapter/ai-infusion/lesson-08-shipment-exception-desk/you-have-two-hours-solve-it-in-front-of-us) | The model reads, code pays. Thresholds live in constants. Unknown means a human decides. | `pricing.py` computes every rupee. `AUTO_APPROVE_CAP` is one constant. Unpriceable becomes escalate. |
| Part 1 | Self-consistency, the extraction barrier, frozen evidence, idempotency, checkpoints, the cap, the 60% rule. | Each one becomes a few lines of `pipeline.py`, and each gets a test. |

#### Our flight plan

| Step | You build | LLM? | Proof it works |
| --- | --- | --- | --- |
| 0 | venv, packages, `.env` | 1 call | The model says hi. |
| 1 | `evidence.py`: the order and the frozen snapshot | no | Snapshot prints `21:40`. |
| 2 | `pricing.py` + `bench.py`: the money rules | no | `check_rules.py`: 12 checks pass. |
| 3 | `llm.py`: one wrapper with retry, backoff, jitter | yes | A JSON reply parses. |
| 4 | `prompts.py`: the three prompts from Part 1 | — | Read them side by side with Part 1. |
| 5 | `stages.py`: extract, judge, settle | yes | One extraction returns 4 grievances. |
| 6 | **Evals**: `eval_extract.py`, `eval_judge.py` | yes | Zero false rejects on the golden set. |
| 7 | `ledger.py` + `payments.py`: memory that survives crashes | no | Four tables appear in `ledger.db`. |
| 8 | `pipeline.py`: wire it all together | yes | ₹689 refunded, ₹60 held. |
| 9 | `bench_check.py`: replay and outage tests | yes | Paid exactly once; a judge outage still settles. |
| 10 | `app.py`: Gradio | yes | The whole flow in the browser. |

Notice the order. Steps 1 and 2 need no API key at all. Every rupee the system can pay is pinned down and tested before a model is involved. The UI comes last, as in Classes 7 and 8.

Break the problem down
