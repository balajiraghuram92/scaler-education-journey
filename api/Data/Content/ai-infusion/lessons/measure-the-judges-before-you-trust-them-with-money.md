# Measure the judges before you trust them with money

## Measure the judges before you trust them with money

A unit test asks “is the answer exactly X?”. That can't work for a component that answers differently each time. An **eval** asks “across a set of cases where we know the right answer, how often is it right, and how bad are the mistakes?”

Three ideas make an eval:

1. **A golden set.** Inputs paired with the answer a careful human would give, on *this* evidence. Start with 8 cases, aim for 200, and add every production mistake you find.
2. **Metrics chosen by the cost of each error.** Plain accuracy treats every mistake as equal, and here they aren't. Wrongly *refusing* a valid claim loses a customer, so that metric gets a hard limit.
3. **A gate.** The eval exits non-zero when the limit is breached, so a prompt change that makes the judges harsher fails CI before it reaches customers.

#### Which metric guards which risk

| Metric | Catches | Gate |
| --- | --- | --- |
| **False rejects** | Honest claim refused: the expensive error | **must be 0** |
| **False approvals** | Paid a claim the evidence doesn't support | watch and trend |
| **Bench vs single-judge accuracy** | Whether K=3 is earning its 3× bill | bench should be ≥ single |
| **Unanimity rate** | How often cases are clear; falling means drift | watch and trend |
| **Calls used** | Cost per eval run, which is also cost per dispute | matches 1 + N×K + 1 |

#### Eval 1: does extraction split complaints correctly?

```pseudo title="eval_extract.py"
SET EVIDENCE = a frozen snapshot of order ORD-1840
SET CASES = three pairs of a complaint and its expected categories:
    // the four-grievance case study
    // "Worst app ever. Never ordering again. Refund me." expects no categories
    // a cold Paneer Tikka and a double charge expects QUALITY and BILLING
SET passed = 0

FOR EACH complaint and expected in CASES:
    SET got = the sorted categories that extract_grievances finds
    SET ok = got is the same as the sorted expected list
    ADD 1 to passed when ok
    PRINT PASS or FAIL, with the expected and the actual categories
PRINT how many complaints split correctly
```

> **Imported:**
> - `SAMPLE_COMPLAINT` from `evidence`, the local file evidence.py: the four-grievance complaint from the case study.
> - `snapshot` from `evidence`, the local file evidence.py: freezes the sample order to test against.
> - `extract_grievances` from `stages`, the local file stages.py: the extraction stage under test.

```python reveal title="eval_extract.py · step 6 · python eval_extract.py"
from evidence import SAMPLE_COMPLAINT, snapshot
from stages import extract_grievances

EVIDENCE = snapshot("ORD-1840")

# complaint -> the categories a careful human would extract (order doesn't matter)
CASES = [
    (SAMPLE_COMPLAINT, ["LATE_DELIVERY", "MISSING_ITEM", "PACKAGING", "PARTNER_CONDUCT"]),
    ("Worst app ever. Never ordering again. Refund me.", []),          # feelings + demand only
    ("The Paneer Tikka was stone cold and I was charged twice.", ["QUALITY", "BILLING"]),
]

passed = 0
for complaint, expected in CASES:
    got = sorted(g["category"] for g in extract_grievances(complaint, EVIDENCE))
    ok = got == sorted(expected)
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'}  expected {sorted(expected)}\n      got      {got}")
print(f"\nextraction: {passed}/{len(CASES)} complaints split correctly")
```

Each case pins a different rule from the extraction prompt: the four-grievance case study, a complaint that is *only* feelings and demands (so the right answer is zero grievances), and a two-claim complaint where one claim is billing and must later go to a human.

#### Eval 2: does the bench rule correctly, and is K=3 worth it?

```pseudo title="eval_judge.py"
SET K = 3 judges for each grievance
SET EVIDENCE = a frozen snapshot of order ORD-1840
SET GOLDEN = eight grievances, each with the ruling a careful human gives on this evidence
SET single_ok, bench_ok, false_rejects, false_approvals, unanimous = 0

FOR EACH text and gold in GOLDEN:
    SET rulings = judge_grievance, run once for each judge index from 0 to K-1
    SET verdict = tally(rulings)
    SET single = the first judge's ruling, and bench = the verdict's ruling
    ADD 1 to single_ok when single is gold
    ADD 1 to bench_ok when bench is gold
    ADD 1 to false_rejects when bench is REJECTED but gold is not   // the expensive mistake
    ADD 1 to false_approvals when bench is UPHELD but gold is not   // money we did not owe
    ADD 1 to unanimous when all K judges agree
    PRINT gold, single, bench, the votes and the text

PRINT single-judge accuracy and bench accuracy
PRINT false rejects, false approvals, the unanimous count and the total LLM calls
IF false_rejects is more than 0 THEN STOP with "EVAL GATE FAILED"
```

> **Imported:**
> - `tally` from `bench`, the local file bench.py: counts the three rulings into a verdict.
> - `snapshot` from `evidence`, the local file evidence.py: freezes the sample order.
> - `judge_grievance` from `stages`, the local file stages.py: one judge call, the thing being measured.

```python reveal title="eval_judge.py · step 6 · python eval_judge.py"
from bench import tally
from evidence import snapshot
from stages import judge_grievance

K = 3
EVIDENCE = snapshot("ORD-1840")

# The golden set: grievance -> the ruling a careful human gives on THIS evidence.
GOLDEN = [
    ("Order was delivered 85 minutes after it was placed.", "UPHELD"),
    ("2 of the 4 Hyderabadi Biryani units ordered were not delivered.", "UPHELD"),
    ("The bag weighed about half of what the order should weigh.", "UPHELD"),
    ("The order was delivered more than two hours late.", "REJECTED"),
    ("The customer was charged a delivery fee of Rs 99.", "REJECTED"),
    ("The delivery partner behaved rudely when asked about the missing items.", "REJECTED"),
    ("The raita container leaked inside the delivery bag.", "ESCALATE"),
    ("The Paneer Tikka was cold on arrival.", "ESCALATE"),
]

single_ok = bench_ok = false_rejects = false_approvals = unanimous = 0
print(f"{'gold':9} {'1 judge':9} {'bench':9} votes  grievance")
for text, gold in GOLDEN:
    rulings = [judge_grievance({"text": text}, EVIDENCE, k) for k in range(K)]
    verdict = tally(rulings)
    single, bench = rulings[0]["ruling"], verdict["ruling"]
    single_ok += single == gold
    bench_ok += bench == gold
    false_rejects += bench == "REJECTED" and gold != "REJECTED"   # the expensive mistake
    false_approvals += bench == "UPHELD" and gold != "UPHELD"     # the cheaper one: money we didn't owe
    unanimous += verdict["split"] == f"{K}-0"
    print(f"{gold:9} {single:9} {bench:9} {verdict['votes']:6} {text[:52]}")

n = len(GOLDEN)
print(f"\nsingle-judge accuracy {single_ok}/{n}   bench accuracy {bench_ok}/{n}")
print(f"false rejects {false_rejects}   false approvals {false_approvals}   "
      f"unanimous {unanimous}/{n}   LLM calls {n * K}")
if false_rejects:
    raise SystemExit("EVAL GATE FAILED: the bench refused a claim the evidence supports")
```

1 **The golden set covers all three rulings** Three upheld, three rejected (two of them contradicted by the evidence: “two hours late” vs 85 minutes, “₹99 fee” vs ₹49), and two that the evidence can't speak to, so they should escalate.

2 **Single judge vs bench, same run** `rulings[0]` is what you'd get with K=1. Comparing it with the tally on the same calls shows what the extra two calls bought.

3 **The gate is asymmetric on purpose** Only false rejects fail the run. False approvals are printed and trended, because the cap and human review already bound that risk.

*example run against a stand-in model; your numbers will differ by model and by day* gold 1 judge bench votes grievance UPHELD UPHELD UPHELD U,U,U Order was delivered 85 minutes after it was placed. … ESCALATE **UPHELD** ESCALATE U,E,E The raita container leaked inside the delivery bag. ESCALATE UPHELD **UPHELD** U,U,E The Paneer Tikka was cold on arrival. single-judge accuracy 6/8 bench accuracy **7/8** false rejects **0** false approvals 1 unanimous 6/8 LLM calls 24

Read your own run the way you'd read it at work. In the example above, the single judge would have **paid for the raita** on a claim nothing can prove, and the bench caught it. That's Part 1's argument for K=3, and it's the pattern to look for in your numbers. But the bench still upheld the cold Paneer Tikka 2–1. That's one false approval, and the next thing to work on: a sharper judging rule, or a different model as the third judge.

Production reality

**Offline evals before release, online evals after.** This is the offline half: a fixed set, run on every prompt or model change. In production you also sample real disputes and compare the bench with what human agents decided on the escalated and appealed cases. Every disagreement you find becomes a new golden case. The golden set is never finished. It grows from your mistakes.

Ask the room

“Why not use another LLM to grade the judges instead of writing a golden set by hand?”

LLM-as-judge is useful for open-ended text, such as “is this settlement message polite?”. Rulings here are a three-way label with a correct answer on known evidence, so a hand-labelled set is cheaper, exact, and doesn't share the judge's blind spots. Use an LLM grader where there's no single right answer. Use labels where there is one.

Step 7 · memory that survives a crash

## The ledger: Part 1's four tables, in SQLite

The capacity section of Part 1 counted rows in four tables. Here they are as real tables. SQLite is a file, so there's no server to install.

```pseudo title="ledger.py"
SET DB = open the SQLite file ledger.db, with rows readable by column name
RUN the SQL that creates the four tables if they do not exist yet
    // disputes, evidence_snapshots, grievances, judge_rulings

DEFINE _now(): RETURN the current time, to the second
DEFINE get_dispute(dispute_id): RETURN that row as a dictionary, or None
DEFINE create_dispute(dispute_id, order_id, complaint):
    SAVE a row with status RECEIVED, ignored if the id already exists
DEFINE set_status(dispute_id, status, extra fields):
    UPDATE the status and the time, plus any extra fields, for this dispute
DEFINE save_evidence(dispute_id, snapshot):
    SAVE the snapshot as JSON, ignored if one already exists   // frozen once
    RETURN get_evidence(dispute_id)
DEFINE get_evidence(dispute_id): RETURN the saved snapshot, or None
DEFINE save_grievances(dispute_id, grievances):
    SAVE each grievance as JSON, replacing any with the same id   // one transaction
DEFINE get_grievances(dispute_id): RETURN the saved grievances, sorted by id
DEFINE save_ruling(dispute_id, grievance_id, judge_index, ruling):
    SAVE one judge's ruling as JSON, replacing any with the same key   // one transaction per save
DEFINE get_rulings(dispute_id): RETURN every saved ruling, keyed by grievance and judge
```

> **Imported:**
> - `json` Python standard library: stores snapshots, grievances and rulings as JSON text.
> - `sqlite3` Python standard library: the built-in database that keeps the ledger in one file.
> - `datetime` from `datetime`, Python standard library: gives the time of each status change.

```python reveal title="ledger.py · step 7"
import json
import sqlite3
from datetime import datetime

DB = sqlite3.connect("ledger.db", check_same_thread=False)
DB.row_factory = sqlite3.Row
DB.executescript("""
CREATE TABLE IF NOT EXISTS disputes (
  dispute_id TEXT PRIMARY KEY, order_id TEXT, complaint TEXT, status TEXT,
  refund_amount INTEGER DEFAULT 0, held_amount INTEGER DEFAULT 0,
  message TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS evidence_snapshots (
  dispute_id TEXT PRIMARY KEY, snapshot_json TEXT);
CREATE TABLE IF NOT EXISTS grievances (
  dispute_id TEXT, grievance_id TEXT, data_json TEXT,
  PRIMARY KEY (dispute_id, grievance_id));
CREATE TABLE IF NOT EXISTS judge_rulings (
  dispute_id TEXT, grievance_id TEXT, judge_index INTEGER, ruling_json TEXT,
  PRIMARY KEY (dispute_id, grievance_id, judge_index));
""")

def _now():
    return datetime.now().isoformat(timespec="seconds")

def get_dispute(dispute_id):
    row = DB.execute("SELECT * FROM disputes WHERE dispute_id = ?", (dispute_id,)).fetchone()
    return dict(row) if row else None

def create_dispute(dispute_id, order_id, complaint):
    with DB:
        DB.execute("INSERT OR IGNORE INTO disputes (dispute_id, order_id, complaint, status, updated_at)"
                   " VALUES (?, ?, ?, 'RECEIVED', ?)", (dispute_id, order_id, complaint, _now()))

def set_status(dispute_id, status, **fields):
    cols = ", ".join(f"{k} = ?" for k in fields)
    with DB:
        DB.execute(f"UPDATE disputes SET status = ?, updated_at = ?{', ' + cols if cols else ''}"
                   " WHERE dispute_id = ?", (status, _now(), *fields.values(), dispute_id))

def save_evidence(dispute_id, snapshot):
    with DB:
        DB.execute("INSERT OR IGNORE INTO evidence_snapshots VALUES (?, ?)",
                   (dispute_id, json.dumps(snapshot)))
    return get_evidence(dispute_id)

def get_evidence(dispute_id):
    row = DB.execute("SELECT snapshot_json FROM evidence_snapshots WHERE dispute_id = ?",
                     (dispute_id,)).fetchone()
    return json.loads(row[0]) if row else None

def save_grievances(dispute_id, grievances):
    with DB:
        DB.executemany("INSERT OR REPLACE INTO grievances VALUES (?, ?, ?)",
                       [(dispute_id, g["grievance_id"], json.dumps(g)) for g in grievances])

def get_grievances(dispute_id):
    rows = DB.execute("SELECT data_json FROM grievances WHERE dispute_id = ? ORDER BY grievance_id",
                      (dispute_id,)).fetchall()
    return [json.loads(r[0]) for r in rows]

def save_ruling(dispute_id, grievance_id, judge_index, ruling):
    with DB:
        DB.execute("INSERT OR REPLACE INTO judge_rulings VALUES (?, ?, ?, ?)",
                   (dispute_id, grievance_id, judge_index, json.dumps(ruling)))

def get_rulings(dispute_id):
    rows = DB.execute("SELECT grievance_id, judge_index, ruling_json FROM judge_rulings"
                      " WHERE dispute_id = ?", (dispute_id,)).fetchall()
    return {(r[0], r[1]): json.loads(r[2]) for r in rows}
```

```pseudo title="payments.py"
SET _executed = an empty record of idempotency key to amount   // a stand-in for the provider's memory

DEFINE refund(idempotency_key, amount):
    // the provider refuses to execute the same key twice
    IF idempotency_key is already in _executed THEN
        RETURN status duplicate_ignored, with the amount recorded the first time
    store amount in _executed under idempotency_key
    RETURN status paid, with amount

DEFINE payouts(): RETURN a copy of _executed
```

```python reveal title="payments.py · step 7 · F9"
# Stand-in for the payment provider. Real ones (Razorpay, Stripe) accept an
# idempotency key and refuse to execute the same key twice - so does this.
_executed = {}

def refund(idempotency_key: str, amount: int) -> dict:
    if idempotency_key in _executed:
        return {"status": "duplicate_ignored", "amount": _executed[idempotency_key]}
    _executed[idempotency_key] = amount
    return {"status": "paid", "amount": amount}

def payouts() -> dict:
    return dict(_executed)
```

1 **One row per judge call in `judge_rulings`** The primary key is (dispute, grievance, judge). That key is what lets a crashed run resume: anything already in the table is never asked again.

2 **`INSERT OR IGNORE` on evidence** A retry can't overwrite the snapshot with a fresher one, so the evidence is frozen at the database level too.

3 **`with DB:` is a transaction** Each save either fully happens or doesn't happen. A crash halfway through a write leaves no half-row.

4 **Two layers of “never pay twice”** The ledger refuses to re-run a settled dispute, and the payment provider refuses to execute the same idempotency key twice. If either layer has a bug, the other still holds. That's why Part 1 passed the key to the payments API as well.

Step 8 · wire it

## resolve_dispute(): the twenty lines, for real

Put this next to Part 1's pseudocode with five landmines. The numbered comments follow the same stages, and every landmine has a line that defuses it.

```pseudo title="pipeline.py"
SET K = 3 judges per grievance, PARALLELISM = 4 calls at a time, AUTO_APPROVE_CAP = 2000 rupees, PARTIAL_SETTLE_MIN = 0.6

DEFINE dispute_key(complaint, order_id):
    RETURN the first 16 characters of the SHA-256 hash of order_id and the trimmed complaint

DEFINE resolve_dispute(complaint, order_id):
    SET dispute_id = dispute_key(complaint, order_id)
    // 1. never pay twice: a SETTLED or ESCALATED dispute is returned as it was
    IF the ledger already has this dispute as SETTLED or ESCALATED THEN RETURN it, marked replayed
    CREATE the dispute in the ledger with status RECEIVED
    // 2. freeze the evidence once; a resumed run reuses the same copy
    SET evidence = the saved snapshot, or a new snapshot saved now
    SET status = INTAKE
    // 3. extraction is the barrier; it is saved so a crash never extracts again
    SET grievances = the saved grievances, or extract_grievances and save them
    IF there are none THEN ESCALATE with "Nothing checkable found"
    SET status = JUDGING
    // 4. judge: N × K calls, PARALLELISM at a time, skipping slots already ruled
    RUN judge_grievance for each missing grievance and judge index, PARALLELISM at a time
    SAVE each ruling as soon as it arrives; a failed call stays unresolved
    // 5. tally and price: plain code, no model
    FOR EACH grievance:
        SET v = tally of its K rulings
        SET amount = price(grievance, evidence)
        IF it is UPHELD but amount is None THEN SET ruling = ESCALATE
    SAVE the grievances with their verdicts and amounts to the ledger
    SET refund = total of the UPHELD amounts, and held = total of the ESCALATE and unresolved amounts
    SET status = TALLIED
    // 6. hard rules decide whether money moves automatically
    IF refund is over AUTO_APPROVE_CAP THEN ESCALATE and RETURN
    IF resolved grievances are under 60% of all THEN ESCALATE and RETURN
    // 7. settle: the model writes the words, code writes the cheque
    SET message = write_settlement(complaint, resolved, refund)
    IF refund is more than 0 THEN CALL payments.refund with dispute_id as the idempotency key
    SET status = SETTLED, with the message
    RETURN the dispute
```

> **Imported:**
> - `hashlib` Python standard library: builds the SHA-256 hash that becomes the dispute id.
> - `ThreadPoolExecutor` from `concurrent.futures`, Python standard library: runs the judge calls in parallel.
> - `as_completed` from `concurrent.futures`, Python standard library: hands back each judge call as soon as it finishes.
> - `ledger` the local file ledger.py: the saved state of each dispute.
> - `payments` the local file payments.py: the payout stand-in that refuses a repeated key.
> - `tally` from `bench`, the local file bench.py: counts the rulings into a verdict.
> - `snapshot` from `evidence`, the local file evidence.py: freezes the order when the dispute first arrives.
> - `price` from `pricing`, the local file pricing.py: looks up the rupees for each grievance.
> - `extract_grievances` from `stages`, the local file stages.py: stage 2, the extraction call.
> - `judge_grievance` from `stages`, the local file stages.py: stage 3, one judge call.
> - `write_settlement` from `stages`, the local file stages.py: stage 4, the customer message.

```python reveal title="pipeline.py · step 8 · the whole system"
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import ledger
import payments
from bench import tally
from evidence import snapshot
from pricing import price
from stages import extract_grievances, judge_grievance, write_settlement

K = 3                       # judges per grievance
PARALLELISM = 4             # "4 lines" - calls in flight per dispute
AUTO_APPROVE_CAP = 2000     # rupees; above this a human approves, always
PARTIAL_SETTLE_MIN = 0.6    # pay now if >= 60% of grievances resolved

def dispute_key(complaint: str, order_id: str) -> str:
    return hashlib.sha256(f"{order_id}|{complaint.strip()}".encode()).hexdigest()[:16]

def resolve_dispute(complaint: str, order_id: str) -> dict:
    dispute_id = dispute_key(complaint, order_id)

    # 1. Idempotency: a finished dispute is returned, never re-run, never re-paid.
    existing = ledger.get_dispute(dispute_id)
    if existing and existing["status"] in ("SETTLED", "ESCALATED"):
        return {**existing, "replayed": True}
    ledger.create_dispute(dispute_id, order_id, complaint)

    # 2. Freeze the evidence once. A resumed run reuses the same snapshot.
    evidence = ledger.get_evidence(dispute_id) or ledger.save_evidence(dispute_id, snapshot(order_id))
    ledger.set_status(dispute_id, "INTAKE")

    # 3. Extract - the barrier. Persisted, so a crashed worker never re-extracts.
    grievances = ledger.get_grievances(dispute_id)
    if not grievances:
        grievances = extract_grievances(complaint, evidence)
        ledger.save_grievances(dispute_id, grievances)
    if not grievances:
        ledger.set_status(dispute_id, "ESCALATED", message="Nothing checkable found - needs a human.")
        return ledger.get_dispute(dispute_id)
    ledger.set_status(dispute_id, "JUDGING")

    # 4. Judge: N x K independent calls, PARALLELISM at a time. Skip slots already ruled.
    done = ledger.get_rulings(dispute_id)
    todo = [(g, k) for g in grievances for k in range(K) if (g["grievance_id"], k) not in done]
    with ThreadPoolExecutor(max_workers=PARALLELISM) as pool:
        futures = {pool.submit(judge_grievance, g, evidence, k): (g["grievance_id"], k) for g, k in todo}
        for future in as_completed(futures):
            gid, k = futures[future]
            try:
                ruling = future.result()
            except Exception:
                continue                               # stays unresolved; a retry resumes here
            ledger.save_ruling(dispute_id, gid, k, ruling)
            done[(gid, k)] = ruling

    # 5. Tally and price - plain code, no model.
    verdicts = []
    for g in grievances:
        v = tally([done.get((g["grievance_id"], k)) for k in range(K)])
        amount = price(g, evidence)
        if v and v["ruling"] == "UPHELD" and amount is None:
            v["ruling"] = "ESCALATE"                   # upheld but unpriceable -> human
        verdicts.append({**g, **(v or {"ruling": None}), "amount": amount})
    ledger.save_grievances(dispute_id, verdicts)

    resolved = [v for v in verdicts if v["ruling"] is not None]
    refund = sum(v["amount"] for v in verdicts if v["ruling"] == "UPHELD")
    held = sum(v["amount"] or 0 for v in verdicts if v["ruling"] in ("ESCALATE", None))
    ledger.set_status(dispute_id, "TALLIED", refund_amount=refund, held_amount=held)

    # 6. Hard rules decide whether money moves automatically.
    if refund > AUTO_APPROVE_CAP:
        ledger.set_status(dispute_id, "ESCALATED",
                          message=f"Refund of Rs {refund} exceeds the Rs {AUTO_APPROVE_CAP} cap - awaiting approval.")
        return ledger.get_dispute(dispute_id)
    if len(resolved) / len(verdicts) < PARTIAL_SETTLE_MIN:
        ledger.set_status(dispute_id, "ESCALATED", message="Too few grievances resolved - sent to an agent.")
        return ledger.get_dispute(dispute_id)

    # 7. Settle: the model writes the words, the code writes the cheque.
    message = write_settlement(complaint, resolved, refund)
    if refund > 0:
        payments.refund(idempotency_key=dispute_id, amount=refund)
    ledger.set_status(dispute_id, "SETTLED", message=message)
    return ledger.get_dispute(dispute_id)
```

| Comment | Part 1 idea | The line that does it |
| --- | --- | --- |
| # 1 | Idempotency is the product | `if existing and existing["status"] in ("SETTLED", "ESCALATED"): return` |
| # 2 | Freeze evidence once | `ledger.get_evidence(...) or ledger.save_evidence(...)` |
| # 3 | The barrier; persist before judging | `if not grievances: extract → save` |
| # 4 | N × K independent calls, 4 lines | `ThreadPoolExecutor(max_workers=PARALLELISM)`, skipping slots already in the ledger |
| # 5 | The bench counts, the price list prices | `tally(...)`, `price(...)`; no model involved |
| # 6 | Cap and the 60% rule | `refund > AUTO_APPROVE_CAP`, `len(resolved) / len(verdicts) < PARTIAL_SETTLE_MIN` |
| # 7 | The model writes the words, code writes the cheque | `write_settlement(...)` then `payments.refund(idempotency_key=dispute_id, …)` |

1 **The key ignores trailing whitespace** `complaint.strip()` means a double-submitted form with an extra newline is still the same dispute. Normalise before you hash.

2 **`as_completed` saves each ruling the moment it lands** Not after all twelve. If the worker dies after five rulings, those five are in the ledger and the retry makes only the other seven calls.

3 **A failed future is skipped, not fatal** One provider timeout leaves one slot empty, so that grievance is unresolved. The 60% rule then decides whether the rest can still be paid now.

4 **Status is written after every stage** `RECEIVED → INTAKE → JUDGING → TALLIED → SETTLED / ESCALATED`. That's what a “GET status” endpoint would read, and how you'd find disputes stuck in one stage.

Step 9 · prove the whole thing

## Replay it, break it, check the money

`bench_check.py` runs the case study end to end, then attacks the two guarantees that matter most: *never pay twice* and *an outage doesn't mean a rejection*.

```pseudo title="bench_check.py"
IF ledger.db exists THEN DELETE it   // start from an empty ledger, before ledger is imported
SET checks = an empty record of named results

// 1. the happy path from the case study
SET r = resolve_dispute(SAMPLE_COMPLAINT, "ORD-1840")
Record each check: status is SETTLED, refund is 689, held is 60, and the PARTNER_CONDUCT grievance is REJECTED

// 2. idempotency: the customer hits submit again
SET again = resolve_dispute(SAMPLE_COMPLAINT, "ORD-1840")
Record each check: the second result is replayed, and payouts holds exactly one payment of 689

// 3. chaos: the provider fails every judge call on one grievance
REPLACE pipeline.judge_grievance with flaky_judge, which raises a timeout for PACKAGING grievances and otherwise calls the real judge
SET r2 = resolve_dispute(SAMPLE_COMPLAINT plus " Please sort it out.", "ORD-1840")
Record each check: status is SETTLED, and the held amount is 60, not rejected

FOR EACH name and ok in checks:
    PRINT PASS or FAIL, then the name
PRINT how many checks passed
```

> **Imported:**
> - `os` Python standard library: checks for and deletes the old ledger file.
> - `ledger` the local file ledger.py: reads the saved grievances during the checks.
> - `payments` the local file payments.py: reads the payouts record to count the payments.
> - `pipeline` the local file pipeline.py: its judge function is swapped out for the outage test.
> - `SAMPLE_COMPLAINT` from `evidence`, the local file evidence.py: the case-study complaint.
> - `resolve_dispute` from `pipeline`, the local file pipeline.py: runs the whole dispute.

```python reveal title="bench_check.py · step 9 · python bench_check.py"
import os

if os.path.exists("ledger.db"):          # start from an empty ledger (before ledger is imported)
    os.remove("ledger.db")

import ledger
import payments
import pipeline
from evidence import SAMPLE_COMPLAINT
from pipeline import resolve_dispute

checks = {}

# 1. the happy path from the case study
r = resolve_dispute(SAMPLE_COMPLAINT, "ORD-1840")
by_cat = {g["category"]: g for g in ledger.get_grievances(r["dispute_id"])}
checks["settled without a human"] = r["status"] == "SETTLED"
checks["refund is Rs 689 (49 + 640)"] = r["refund_amount"] == 689
checks["raita (Rs 60) held for an agent"] = r["held_amount"] == 60
checks["rude-partner claim rejected"] = by_cat.get("PARTNER_CONDUCT", {}).get("ruling") == "REJECTED"

# 2. idempotency: the customer hits submit again
again = resolve_dispute(SAMPLE_COMPLAINT, "ORD-1840")
checks["resubmission replayed, not re-run"] = again.get("replayed") is True
checks["paid exactly once"] = list(payments.payouts().values()) == [689]

# 3. chaos: the provider fails every judge call on one grievance
real_judge = pipeline.judge_grievance

def flaky_judge(grievance, evidence, judge_index):
    if grievance["category"] == "PACKAGING":
        raise TimeoutError("provider down")
    return real_judge(grievance, evidence, judge_index)

pipeline.judge_grievance = flaky_judge
r2 = resolve_dispute(SAMPLE_COMPLAINT + " Please sort it out.", "ORD-1840")
checks["outage: 3 of 4 resolved (75% >= 60%) -> partial settle"] = r2["status"] == "SETTLED"
checks["outage: unresolved raita held, not rejected"] = r2["held_amount"] == 60

for name, ok in checks.items():
    print(("PASS " if ok else "FAIL ") + name)
print(f"\n{sum(checks.values())}/{len(checks)} checks passed")
```

*$ python bench_check.py* **PASS** settled without a human **PASS** refund is Rs 689 (49 + 640) **PASS** raita (Rs 60) held for an agent **PASS** rude-partner claim rejected **PASS** resubmission replayed, not re-run **PASS** paid exactly once **PASS** outage: 3 of 4 resolved (75% >= 60%) -> partial settle **PASS** outage: unresolved raita held, not rejected 8/8 checks passed

When a check goes red

The first four checks depend on the model's rulings. While testing this page with a stand-in model that votes randomly on unprovable claims, one run upheld the raita 2–1 and refunded ₹749 instead of ₹689. The code was correct; the bench just ruled differently that time. That's not a flaky test to ignore. It's a **case for the golden set** in step 6. The replay and outage checks test your code and should never go red.

#### Try the crash yourself

Run `python app.py`, submit, and press `Ctrl+C` in the terminal while it's judging. Start it again and submit the same complaint. The dispute resumes from `JUDGING`, and only the judge calls missing from `judge_rulings` are made. When this page was tested (with a stubbed model), a crash after 5 saved rulings resumed with exactly 7 calls.

Step 10 · the face
