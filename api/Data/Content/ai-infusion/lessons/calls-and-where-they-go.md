# calls, and where they go

## 14 calls, and where they go

The formula fits in your head, which is the point of writing it down:

calls = **1** *(extract)* + **N × K** *(judge)* + **1** *(settle)* = 1 + (4 × 3) + 1 = **14 calls per dispute**

Notice what is *not* in the formula: the vote. Counting three rulings is a `Counter()`, not a model call. Neither is the refund amount — that is a price lookup against the order.

Average load

20/mindisputes across the day

Dinner peak

200/min8–10 pm, ten times average

Peak call rate

2,800LLM calls per minute

That last number is the one your provider cares about: 200 × 14 = 2,800 calls a minute, sustained for two hours every single evening. Size on the average and you will discover your rate limit during Friday dinner, which is the worst possible time to discover it.

#### Where “4.5 seconds” comes from

You have 12 calls to make. Each takes about 1–2 seconds. How long until you are done?

**One at a time:**

12 calls × 1.5 sec = **18 seconds**

Far too slow — there is an angry customer watching a spinner. So you run several at once. **“4-way parallelism” means 4 at a time** — four phone lines, each handling one call, all working simultaneously:

Line A: call 1 call 5 call 9 **3 calls** Line B: call 2 call 6 call 10 **3 calls** Line C: call 3 call 7 call 11 **3 calls** Line D: call 4 call 8 call 12 **3 calls** *────────* *12 calls ✓*

{{diagram:1}}

*Each block is one LLM call, and both rows use the same clock. The four-line version isn't doing less work — it finishes a quarter of the way along because the same 12 blocks are stacked four deep instead of laid end to end.*

12 calls ÷ 4 lines = **3 calls per line** 3 × 1 sec = **3 seconds** *← if calls run fast* 3 × 2 sec = **6 seconds** *← if calls run slow* *→ call it 4.5 seconds typical*

> **Note:**
> The **3** here is **3 calls per line** — not 3 seconds. Seconds only appear once you multiply by how long a single call takes. Skipping that multiplication is why this line looks like it came from nowhere.

#### Why not more lines?

| Lines | Calls per line | Time | Verdict |
| --- | --- | --- | --- |
| 1 | 12 | 12–24 s | customer already gone |
| **4** | **3** | **3–6 s** | the design's choice |
| 12 | 1 | 1–2 s | lovely — for one dispute |

Twelve lines per dispute looks free until you multiply by concurrency. At peak there are roughly **25 disputes in flight at once**. Four lines each is 100 simultaneous requests; twelve lines each is 300. **The parallelism you can afford per dispute is set by your total rate limit divided by your concurrency** — never by what one dispute would like.

#### 7 seconds of work, 15 seconds of promise

intake *0.2 sec* extraction *1.5 sec* judging *4.5 sec* **← the part above** settlement *1.0 sec* *────────* **~7.2 sec**

So why does the requirement say **p50 < 15 seconds**? Because 7 seconds is an **estimate of the work** and 15 is a **promise to the customer**. The gap absorbs queue wait, 429 retries, the next complaint having 8 grievances instead of 4, and your provider having a slow evening. Set the SLA equal to the estimate and you miss it half the time by definition.

Work, typical

~7 swhat the pipeline costs

p50 promise

< 15 shalf of disputes

p90 promise

< 30 snine in ten

Ask the room

“The fact-checking system we designed last week allowed 90 seconds. This one allows 15. Same architecture — what changed?”

The person on the other end. A journalist submitting an article will accept “come back in two minutes.” A customer who just got the wrong dinner will not — every extra second on that spinner is a support ticket you are about to receive anyway. **The architecture is identical; the latency budget is a product decision, not an engineering one.**

Capacity estimation

## 35 KB a dispute, 380 GB a year

The question is narrower than it looks. Not “how big is our data” — but: *when one dispute settles, which rows did we just write?*

Four tables. Count the rows in each.

#### Table 1 — `disputes`, one row

Id, complaint hash, order id, customer id, status, final amount, timestamps.

1 row × 1 KB = **1 KB**

#### Table 2 — `grievances`, four rows

One per grievance. Text, category, character span, final ruling, vote split, confidence, amount, reasoning.

4 rows × 1.5 KB = **6 KB**

#### Table 3 — `evidence_snapshots`, one row

The frozen copy — order lines, timestamps, GPS trail, weights, ratings, as they stood at 21:52.

1 row × 3 KB = **3 KB**

#### Table 4 — `judge_rulings`, twelve rows

This is the one people forget. You made 12 judging calls and you keep **every single ruling**, not just the winners — the raw JSON each judge returned, around 2 KB:

{"ruling":"ESCALATE","confidence":0.31, "reasoning":"No field in the evidence records packaging condition on arrival…"}

12 rows × 2 KB = **24 KB**

*Why keep all 12?* Because when a customer escalates, or a regulator asks, or your own ops lead asks why ₹640 left the company — “the bench ruled 3–0” is only credible if you can produce the three rulings. Throw them away and you can never explain a payout again.

#### Add it up

1 KB *disputes* + 6 KB *grievances* + 3 KB *evidence_snapshots* + 24 KB *judge_rulings* *───────* 34 KB ≈ **35 KB per dispute**

**Raw rulings are 69% of it.** Same shape as the call budget, same reason: K-sampling dominates both.

#### Scale it to a day, then a year

35 KB × 30,000 disputes/day = 1,050,000 KB 1,050,000 KB ÷ 1,000 = 1,050 MB 1,050 MB ÷ 1,000 = **~1 GB per day** 1 GB × 365 days ≈ **380 GB per year**

> **Note:**
> And here the answer is *different* from the fact-checking system, which landed at 51 GB a year and could piggyback on any existing cluster. **380 GB a year is big enough that you must now make a decision** rather than shrug.

That decision is a **retention policy**, and the four tables want different ones:

| Table | Share | Keep it how long, and why |
| --- | --- | --- |
| `judge_rulings` | 69% | **90 days hot, then cold storage.** You need it while the dispute can still be escalated. After that it is audit material, not working data. |
| `grievances` | 17% | **7 years.** This is the financial record of why money moved. Statutory. |
| `evidence_snapshots` | 9% | **7 years.** Useless without it — the ruling means nothing if you cannot show what it was ruled against. |
| `disputes` | 3% | **7 years.** Tiny, and it is the index into everything else. |

Move the 69% to cold storage after 90 days and your hot footprint drops from 380 GB to about 150 GB a year — which *can* sit on a cluster you already run.

Ask the room

“We just decided storage is cheap and then spent a whole slide on retention. Why?”

Because storage is cheap and *queries* are not. 380 GB of raw JSON in your hot path slows every dashboard and every scan that touches the table. Retention is rarely about the disk bill — it is about keeping the working set small enough to stay fast.

Production shape

## Submission is synchronous. The work is not.

Think of a dry cleaner. You hand over a shirt, they write ticket #47, you leave — thirty seconds. The cleaning takes two days. You come back with the ticket and ask if it is ready.

Nobody would accept the alternative: *standing at the counter for two days* because the only way to get your shirt back is to still be there when it is done. That is what a synchronous design is, and at 200 disputes a minute it fails four different ways at once — held-open connections timing out, needing every server and every LLM credit simultaneously, losing all work on a crash, and having nowhere to put a burst.

{{diagram:2}}

*The counter clerk (REST API) takes the complaint, writes it down, drops the ticket on the pile, and hands you a receipt in 50 ms. Workers pull from the pile when they have capacity. The ledger is how the app answers “is it ready yet?” — and how a crashed worker finds its place again.*

| In the diagram | In the dry cleaner |
| --- | --- |
| **APP** | You, standing at the counter |
| **REST API** | The clerk. Writes the ticket, never cleans anything |
| `dispute_id` | Ticket #47 |
| **KAFKA / SQS** | The pile of bags waiting to be worked |
| **WORKER NODE** | The back-office person handling one ticket |
| **LLM PROVIDERS** | The specialist shops they send each item out to — 14 errands per ticket |
| **LEDGER** | The book recording which ticket is at what stage |
| **GET status** (dashed) | You phoning to ask “is #47 ready?” |

**The pile is the part people skip, and it is doing real work.** Two hundred disputes land in a minute and you can process forty at a time. Without a pile you would have to reject a hundred and sixty of them. With a pile, everyone gets a ticket, nothing is dropped, and the last person simply waits longer.

#### The 429, and why jitter matters

`429` is the HTTP status for **“Too Many Requests.”** At 2,800 calls a minute you will meet it every evening. Three separate ideas in the response:

- **Retry** — don't give up, send it again shortly.
- **Exponential backoff** — wait longer each time: 1 s, then 2, then 4, then 8. Retrying instantly just adds to the flood that refused you.
- **Jitter** — add a random offset to every wait. Without it, forty workers refused at the same instant all wait exactly 2 s, all return at the same instant, and all get refused again — locked in step forever. Backoff lowers the pressure; jitter spreads it out. You need both.

#### Visibility timeout — the trap that pays twice

When a worker takes a message off SQS, the message is *not* deleted. It is hidden for N seconds. Finish and acknowledge within N and it is removed; let N pass in silence and SQS assumes you died and **puts it back on the pile for someone else.**

Now set N to 10 seconds on a job that takes 30:

*t=0s* Worker A takes dispute d7a41…c39 *t=10s* A is at grievance 2 of 4 — but N expired SQS assumes A died, requeues the dispute *t=11s* Worker B picks up the SAME dispute, starts over *t=20s* SQS does it again → Worker C starts it too *t=30s* Three workers settled the same dispute **The customer was refunded ₹689 three times.**

Nobody crashed. The work was fine. **The deadline was just shorter than the job.** In a fact-checking system that bug costs you API credits; here it wires real money out of the company, three times, silently.

Three fixes: set the timeout above your p99; heartbeat with `ChangeMessageVisibility` while you work; or use Kafka, which has no such timeout and lets a consumer hold its partition until it is genuinely done.

Production reality

The API does two things — write the row, then enqueue the id. If the write succeeds and the enqueue fails, you have a dispute stored that no worker will ever touch, stuck on `RECEIVED` forever while a customer refreshes. Fix it with a **transactional outbox**, or run CDC off the disputes table so the database write *is* the queue event.

The agentic loop
