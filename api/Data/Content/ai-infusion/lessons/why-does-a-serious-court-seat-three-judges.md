# Why does a serious court seat three judges?

> **Lesson resources · Lesson 9 · this page also holds Lesson 10:**
> - [Watch the Class 9 recording](https://www.scaler.com/meetings/i/ai-infused-learning-9/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

AI Infusion · Classes 9 & 10 · Design → evals → hands-on build

#### The *Refund* Bench

A customer types one angry paragraph. Inside it are four separate accusations, some true, some false, one unknowable. An agent must find them, judge each one against evidence, and decide how much money to give back — in under fifteen seconds, without ever paying twice.

**Scale** 200 disputes/min at dinner peak **Budget** 14 LLM calls per dispute **Hard limit** ₹2,000 auto-approval cap

The hook

## Why does a serious court seat three judges?

Not because three people are smarter than one. Because one judge can have a bad day, misread a document, or carry a blind spot — and there is no way to tell from the outside which day it was. So you seat three, let them rule independently, and count.

A **2–1 split is information**. It tells you the case was genuinely hard, in a way that a single confident ruling never could. A **3–0 ruling is information too** — it tells you this one was clear.

An LLM is a judge who has a different day every time you ask. Same question, same evidence, slightly different answer — because the model samples from a distribution rather than looking anything up. So do what the courts did: **ask three times, independently, and count.**

This is **self-consistency** (Wang et al., 2022). When the model genuinely knows, the reasoning paths converge. When it is guessing, they scatter. The verdict you keep is the majority; the spread becomes your confidence. The cost is exact and brutal: K samples, K times the bill.

Ask the room

“If the bench splits 2–1 on whether to refund ₹640, and you only get to keep one number — the verdict, or the fact that it was split — which do you keep?”

The split. A 2–1 upheld and a 3–0 upheld are the same verdict and completely different risks. The whole system exists to keep that difference.

{{diagram:1}}

*Three independent rulings, temperature 0.5–0.8, no shared history between them. On the right, one judge would happily have approved a refund on a claim nothing can prove. The two dissenters are what send it to a human instead of to the payments API.*

Production reality

Temperature is set per stage, not once. Verification samples need **T > 0**, roughly 0.5–0.8 — at T = 0 all three judges return byte-identical answers and the bench is theatre. Push past 0.8 and rulings go incoherent. Synthesis runs at **low temperature**: that stage writes the customer-facing message and must not invent anything.

The case

## One angry paragraph, four separate accusations

Everything below follows this single dispute. Real ones carry 1–8 grievances; this one has four.

**DISPUTE** d7a41…c39 **ORDER** ₹1,840 **FILED** 21:52 IST

Ordered at 8:15pm and the food showed up at 9:40pm.g1 We had guests over, it was embarrassing.✕ Two of the four were missing completely.g2 The raita had leaked all over the inside of the bag.g3 And the delivery guy was rude when I asked him about it.g4 Honestly the worst experience I've had on this app — refund everything.✕

upheld  rejected  escalate  not a grievance

#### Two sentences were thrown away, and that is the hardest part

“We had guests over, it was embarrassing” is context and feeling — there is nothing to check it against. “The worst experience I've had” is an opinion, and “refund everything” is a demand, not a claim. None of them can be true or false, so none of them enter the pipeline.

Which forces the question the entire system rests on, and it has to be answered before a line of code is written: **what counts as a grievance?**

Ask the room

“Is “the delivery guy was rude” a grievance?”

Yes — and this is where half the room gets it wrong. It is a *claim about an event*, so it belongs in the pipeline. It is not an opinion like “the food was mediocre.” The fact that you may have no evidence for it does not disqualify it at extraction — that gets decided at **judgement**, not at **extraction**. Confusing those two stages is the most common design error in this system.

So the working definition, and it goes verbatim into the prompt: **a grievance is a statement about something that happened to this order, which evidence could in principle confirm or contradict.** “Arrived at 9:40pm” qualifies. “It was embarrassing” does not.

#### One sentence needed repair before it could be judged

“Two of *the four* were missing” cannot be judged on its own — four of what? The extraction prompt demands every grievance be **self-contained**, with references resolved against the order:

| As the customer wrote it | As extracted |
| --- | --- |
| “Two of the four were missing completely.” | “2 of the 4 Hyderabadi Biryani units ordered were not delivered.” |
| “The delivery guy was rude when I asked *him* about *it*.” | “The delivery partner behaved rudely when asked about the missing items.” |

Production reality

A rule that says “do not use pronouns” tells the model what *not* to do without telling it what to do instead. Name the operation — this is **co-reference resolution**, a task the model already knows by name — and give it the order's line items to resolve against. A prohibition produces refusals; a procedure produces work.

The bench rules

## Four grievances, twelve rulings, one cheque

Each grievance goes to the bench **three times, independently** — no shared history, no chaining. Each judge sees the grievance *and the evidence snapshot*. Twelve calls.

g1Order was delivered 85 minutes after it was placed. evidence · placed 20:15 · delivered 21:40 · SLA 45 min

upheld 0.98₹49

g22 of the 4 Hyderabadi Biryani units ordered were not delivered. evidence · billed 4 · pickup weight 1.2 kg vs expected 2.4 kg

upheld 0.91₹640

g3The raita container leaked inside the delivery bag. evidence · none — no field records packaging condition

escalate 0.35₹60 ?

g4The delivery partner behaved rudely when asked about the missing items. evidence · customer rated this partner 5★ at handover, 21:41

rejected 0.88₹0

| Outcome | Grievances | Amount |
| --- | --- | --- |
| upheld | g1 late delivery, g2 missing items | ₹689 |
| escalate | g3 leaked raita | ₹60 held |
| rejected | g4 rude partner | ₹0 |
| Auto-approved now | under the ₹2,000 cap, so no human needed | ₹689 |

**g4 is the one that earns the system its keep.** A plausible, sympathetic, entirely human-sounding accusation — and the evidence flatly contradicts it: the same customer gave this partner five stars at the door, one minute after handover. A tired support agent at 10pm approves that. The bench does not.

**g3 is the one that shows why you sample three times.** One judge was willing to approve ₹60 on a claim nothing can prove. Two admitted there was nothing to go on. Majority rules, confidence drops to 0.35, and it goes to a human. With a single call you would have had a coin-flip chance of paying out on an unprovable claim — *every time*, at 200 disputes a minute.

Ask the room

“Which mistake costs more — refunding ₹640 that you did not owe, or refusing ₹640 that you did?”

The refusal, by a long way. A wrong refund costs you ₹640, once. A wrong refusal costs you a customer — and in food delivery that is thousands of rupees of lifetime value, plus a one-star review. **The errors are asymmetric, so the system should be too.** Which is why the three verdicts are not symmetric either: when unsure, the design never rejects, it escalates.

Production reality

**Do not trust the confidence score.** It is a number the model generated, not a calibrated probability. Show it to your ops team, log it, chart it — but never branch a payout on it. Branch on the *vote split*, which you computed yourself and can defend.

**The synthesis prompt must say “treat all verdicts as final.”** Without that line, the model re-litigates the bench's ruling while writing the summary — quietly turning a 1–2 escalate into an upheld because the complaint *reads* sympathetic. One sentence in the prompt is what makes the majority actually be the majority.

Architecture

## Four stages, one of which explodes

The pipeline has exactly four logical components. Three of them are a single LLM call each, no matter what you feed them. The fourth is *N × K* of them.

{{diagram:2}}

*Stage 2 must finish before stage 3 can start — you cannot fan out until you know how many grievances there are. That single sequential call is why wall-clock time is set by the fan-out that follows it, not by the number of stages.*

#### Walk it stage by stage

Same dispute, one stage at a time. Watch the **cost** on the right — that is the whole story.

1

#### Intake & evidence snapshot

0 LLM calls · ~200 ms

In

The complaint text and the order id.

Does

Hashes the complaint, then **freezes a copy of the evidence** — order lines, delivery timestamps, GPS trail, pickup weight, partner rating. No model touched.

Out

dispute_id: d7a41…c39 status: RECEIVED evidence: snapshot @ 21:52

> **Note:**
> **Why freeze the evidence?** Because the order record keeps changing — the partner's rating moves, the restaurant edits its bill, a reconciliation job runs overnight. If you re-read evidence during a retry you can get a *different verdict on the same dispute*. Money decisions must be reproducible, so you judge against a frozen copy and keep it.

2

#### Extract grievances

1 LLM call · ~1.5 s

In

The complaint text plus the order's line items, in one prompt.

Does

Keeps checkable accusations, drops feelings and demands, resolves references against the order, records where each sat in the text.

Out

[ {"grievance_id":"g2", "text":"2 of the 4 Hyderabadi Biryani units ordered were not delivered.", "category":"MISSING_ITEM", "span_start":112, "span_end":152}, … g1, g3, g4 ]

> **Note:**
> **This is the barrier.** Until this returns you do not know whether the dispute has one grievance or eight — so you cannot start the parallel work, and you cannot even size it. One call, and everything waits on it.

3

#### Judge by voting

12 calls · ~4.5 s

In

4 grievances + the frozen evidence.

Does

Sends every grievance to **K = 3 judges**, each its own request, none aware of the others. Then counts — in plain code, not another LLM call.

Out

g1 → U,U,U → UPHELD ₹49 g2 → U,U,U → UPHELD ₹640 g3 → U,E,E → ESCALATE ₹60? g4 → R,R,R → REJECTED ₹0

> **Note:**
> **This is the stage that explodes.** 4 grievances × 3 judges = 12 calls. A long complaint with 8 grievances = 24. Every extra grievance, and every extra judge, lands here and nowhere else.

4

#### Settle

1 LLM call · ~1 s

In

The complaint plus the four final rulings and amounts.

Does

One call at low temperature, writing the message the customer reads. Forbidden from changing any ruling. The *amount* is computed in code, never by the model.

Out

status: SETTLED refund: ₹689 held: ₹60 → agent queue message: "We've refunded…"

> **Note:**
> **The model writes the words; the code writes the cheque.** Never let an LLM produce the number that goes to your payments API — let it produce prose about a number your code already computed and can prove.

#### The same thing, against a clock

{{diagram:3}}

*The white hairlines inside stage 3 are the waves: 12 calls going out four at a time is 3 rounds, not one burst. Raise the parallelism and that band shortens; add grievances or raise K and it lengthens. The three blue bars never move.*

#### What “explodes” actually means

Change the input and only one segment responds. Each bar is the same four stages, drawn to the same scale.

{{diagram:4}}

*The blue slivers at both ends are identical in all three bars. Adding grievances or raising K stretches only the middle. That asymmetry is why every operational lever — batch size, worker cap, retry policy, the partial-settlement rule — is aimed at stage 3 and ignores the rest.*

Number crunching
