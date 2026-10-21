# Code BookMyShow 2: Booking, Transactions and Race Conditions

Two users click the same seat at the same moment, and both get a confirmation email. That single failure is the most common follow-up in a machine-coding round and the classic bug in real ticketing, flash-sale and GPU-slot reservation systems. The interesting part is not knowing that "locking" exists, but knowing which lock lives where, what each isolation level actually promises, and why the obvious Python fix does not work.

## Concepts Covered

### The check-then-act race

A booking method has two steps: **check** that every seat is available, then **act** by marking them blocked. Between those steps another request can run its own check. Both see `AVAILABLE`, both write `BLOCKED`, and the last writer wins while both callers believe they succeeded.

The GIL does not help. It makes single bytecode operations safe, not a multi-step sequence, and the thread switch can happen anywhere between the two steps. The demo below uses a `Barrier` to force the unlucky interleaving deterministically.

```python
import threading


class Inventory:
    def __init__(self) -> None:
        self.status = {"C4": "AVAILABLE"}
        self.owner: dict[str, str] = {}

    def book(self, seat: str, user: str, barrier: threading.Barrier) -> bool:
        if self.status[seat] != "AVAILABLE":   # CHECK
            return False
        barrier.wait()                         # both threads have now checked
        self.status[seat] = "BLOCKED"          # ACT
        self.owner[seat] = user
        return True


inv = Inventory()
barrier = threading.Barrier(2)
results: dict[str, bool] = {}


def worker(user: str) -> None:
    results[user] = inv.book("C4", user, barrier)


threads = [threading.Thread(target=worker, args=(u,)) for u in ("alice", "bob")]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(sorted(results.items()))
print("double booked:", all(results.values()))
```

```text
[('alice', True), ('bob', True)]
double booked: True
```

Wrapping check and act in one `threading.Lock` fixes this inside one process: the second thread waits, then sees `BLOCKED` and returns `False`. That is the trap.

### Why `threading.Lock` does not protect a database

A `threading.Lock` is an object in one process's memory. A production API runs several Uvicorn or Gunicorn workers, several containers, several pods. Each process has its own lock object, so worker A holding its lock says nothing to worker B. Even `multiprocessing.Lock` only spans processes forked from one parent on one host. The shared resource is the database row, so the coordination primitive must live where the data lives: row locks, constraints, version columns, or isolation levels. (A distributed lock in Redis or a PostgreSQL advisory lock can also serialise a critical section, but it adds failure modes: expiry, clock drift and fencing tokens.)

> **Interview tip:** If you are asked "just add a lock?", answer with the scope: "a thread lock protects one process; the invariant lives in the database, so the database must enforce it."

### What the isolation levels actually guarantee

| Level | What it stops | Does it stop two check-then-act bookings? |
|---|---|---|
| Read Committed (PostgreSQL default) | Dirty reads | No. Each statement sees the latest committed data. |
| Repeatable Read (MySQL InnoDB default) | Non-repeatable reads: your reads come from one snapshot | No. Both transactions read `AVAILABLE` from their snapshots. |
| Serializable | Any outcome that no one-at-a-time ordering could produce | Yes, by aborting one transaction. |

On MySQL, T-A and T-B both read `AVAILABLE`, T-A updates and commits, and T-B's later `UPDATE` waits for the row lock and then succeeds, overwriting T-A: the snapshot guarantee protects reads, not your business rule. PostgreSQL's Repeatable Read is stricter (it aborts T-B with a serialization error on a concurrent update), so know which database you are quoting.

`SERIALIZABLE` means the concurrent result must equal **some** serial order. It does not mean one transaction at a time database-wide. Transactions touching unrelated rows commit independently; only conflicting ones are aborted, and the application must **retry** the loser. In PostgreSQL the failure is SQLSTATE `40001`; InnoDB's serializable mode turns plain reads into locking reads, so you more often see lock waits and deadlocks (`40001`/`1213`) instead.

### Fix 1: pessimistic row locks with `SELECT ... FOR UPDATE`

Lock exactly the rows you intend to change, in a deterministic order (otherwise two bookings that take overlapping seats in different orders can deadlock), then check and act inside the same transaction.

```python
from sqlalchemy import select
from sqlalchemy.orm import Session


class SeatUnavailableError(RuntimeError):
    pass


def hold_seats(session: Session, req: "BookSeatsRequest") -> "Booking":
    stmt = (
        select(ShowSeat)
        .where(ShowSeat.show_id == req.show_id, ShowSeat.seat_id.in_(req.seat_ids))
        .order_by(ShowSeat.id)                         # stable lock order
        .with_for_update()                             # SELECT ... FOR UPDATE
        .execution_options(populate_existing=True)     # refresh stale identity-map copies
    )
    rows = session.scalars(stmt).all()
    if len(rows) != len(set(req.seat_ids)):
        raise SeatUnavailableError("unknown seat for this show")
    if any(r.status is not ShowSeatStatus.AVAILABLE for r in rows):
        raise SeatUnavailableError("a seat is no longer available")

    now = utc_now()
    for row in rows:
        row.status = ShowSeatStatus.BLOCKED
        row.blocked_at = now
    booking = Booking(user_id=req.user_id, status=BookingStatus.PENDING, show_seats=rows)
    session.add(booking)
    session.commit()                                   # locks are released here
    return booking
```

A second transaction reaching the same rows blocks at `FOR UPDATE` until the first commits, then re-reads `BLOCKED` and fails the check. `with_for_update(nowait=True)` fails immediately and `skip_locked=True` skips locked rows (useful for work queues, not for specific seats). Note that you never call `session.add(row)` for the rows: SQLAlchemy's unit of work tracks attribute changes on loaded objects and flushes them on `commit()`.

The request is a **DTO**, a frozen dataclass that states exactly what the use case needs, so changes to model shape do not ripple to callers:

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BookSeatsRequest:
    user_id: int
    show_id: int
    seat_ids: tuple[int, ...]
```

### Fix 2: compare-and-set in one statement

Move the check into the `UPDATE`'s `WHERE`. The database applies it atomically per row, so no explicit lock or read is needed, and the transaction is tiny. Success is measured by `rowcount`.

```python
from sqlalchemy import update


def hold_seats_cas(session: Session, req: BookSeatsRequest) -> None:
    stmt = (
        update(ShowSeat)
        .where(
            ShowSeat.show_id == req.show_id,
            ShowSeat.seat_id.in_(req.seat_ids),
            ShowSeat.status == ShowSeatStatus.AVAILABLE,
        )
        .values(status=ShowSeatStatus.BLOCKED, blocked_at=utc_now())
    )
    result = session.execute(stmt)
    if result.rowcount != len(req.seat_ids):
        session.rollback()                    # undo the seats we did win
        raise SeatUnavailableError("a seat is no longer available")
    session.commit()
```

The same idea, run against real concurrent connections with the standard library, shows the effect (20 threads, one seat):

```python
import os
import sqlite3
import tempfile
import threading

path = os.path.join(tempfile.mkdtemp(), "cinema.db")
setup = sqlite3.connect(path)
setup.executescript(
    "CREATE TABLE show_seats (id INTEGER PRIMARY KEY, status TEXT NOT NULL DEFAULT 'AVAILABLE', holder TEXT);"
    "INSERT INTO show_seats (id) VALUES (1);"
)
setup.commit()
setup.close()

winners: list[str] = []
guard = threading.Lock()  # protects only this local list


def try_hold(user: str) -> None:
    conn = sqlite3.connect(path, timeout=10, isolation_level=None)
    cur = conn.execute(
        "UPDATE show_seats SET status = 'BLOCKED', holder = ? WHERE id = 1 AND status = 'AVAILABLE'",
        (user,),
    )
    if cur.rowcount == 1:
        with guard:
            winners.append(user)
    conn.close()


threads = [threading.Thread(target=try_hold, args=(f"user{i}",)) for i in range(20)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("winners:", len(winners))
```

```text
winners: 1
```

### Fix 3: constraints and optimistic versions

A unique constraint turns the race into an error the database raises for you. Because a show seat can have many bookings over time (cancelled ones stay as history), uniqueness must apply only to **active** links. A partial unique index does exactly that:

```sql
CREATE UNIQUE INDEX uq_active_show_seat
    ON booking_seats (show_seat_id)
    WHERE is_active = 1;
-- a second active booking for show_seat_id 10 fails:
-- UNIQUE constraint failed: booking_seats.show_seat_id
-- after the first is deactivated (cancellation), the insert succeeds
```

In SQLAlchemy declare it with `Index("uq_active_show_seat", "show_seat_id", unique=True, postgresql_where=text("is_active"))` (and `sqlite_where` for SQLite), and translate `IntegrityError` into `SeatUnavailableError`.

An **optimistic** version column avoids holding locks at all: every update says "apply this if the row is still version N".

```python
from sqlalchemy.orm.exc import StaleDataError


class ShowSeat(BaseModel):
    __tablename__ = "show_seats"

    version: Mapped[int] = mapped_column(nullable=False)
    # ... other columns as before ...
    __mapper_args__ = {"version_id_col": version}


def block_optimistically(session: Session, show_seat_id: int) -> None:
    seat = session.get(ShowSeat, show_seat_id)
    seat.status = ShowSeatStatus.BLOCKED
    try:
        session.commit()      # UPDATE ... WHERE id = ? AND version = <value we read>
    except StaleDataError:
        session.rollback()
        raise SeatUnavailableError("someone else changed this seat")
```

SQLAlchemy increments the version on every UPDATE and raises `StaleDataError` when zero rows matched. Optimistic locking shines when conflicts are rare and transactions are long; for a hot seat on opening night, pessimistic or compare-and-set is cheaper than repeated failures.

### Fix 4: serializable isolation plus retries

Serializable gives you correctness without designing locks, but you pay with aborted transactions, so you **must** wrap the unit of work in a retry loop. Retry only errors that are safe to retry, with jittered backoff.

```python
import random
import time
from collections.abc import Callable


def retry[T](
    fn: Callable[[], T],
    *,
    is_retryable: Callable[[Exception], bool],
    attempts: int = 4,
    base_delay: float = 0.05,
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
) -> T:
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:
            if attempt == attempts or not is_retryable(exc):
                raise
            sleep(rng() * base_delay * 2 ** (attempt - 1))   # full jitter
    raise AssertionError("unreachable")
```

Wiring it to SQLAlchemy (the isolation level must be set before the first statement of the transaction):

```python
from sqlalchemy.exc import OperationalError


def is_serialization_failure(exc: Exception) -> bool:
    orig = getattr(exc, "orig", None)
    code = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
    return isinstance(exc, OperationalError) and code in {"40001", "40P01"}


def book_serializable(engine, req: BookSeatsRequest) -> None:
    def attempt() -> None:
        with Session(engine) as session:
            session.connection(execution_options={"isolation_level": "SERIALIZABLE"})
            hold_seats(session, req)      # check-then-act, now safe

    retry(attempt, is_retryable=is_serialization_failure)
```

### Hard locks versus soft locks: the hybrid design

The tempting design opens a transaction at "select seats" and keeps it until payment completes. Payment takes minutes, so row locks and a pooled connection are held that long: a few abandoned carts exhaust the pool. Use a **soft lock** instead: a short transaction sets `status = BLOCKED` and `blocked_at`, then commits. Payment happens with no database transaction open. A second short transaction confirms: it re-checks that the seat is still blocked for this booking and not expired, then sets `BOOKED`. Both short transactions use one of the fixes above, so the soft lock itself cannot be double-acquired. Expiry is evaluated lazily (next lesson).

Finally, one naming trap: name the table for the `Order` model `orders`. `ORDER` is reserved SQL, and `user` is reserved in PostgreSQL, so always set `__tablename__` to a plural.

## Practical Backend Scenario

You run an inference-slot reservation API for a GPU fleet: customers reserve a 2-hour A100 slot, pay through an external gateway, and the slot must belong to exactly one customer. During a launch, a product manager asks you to "add a mutex". You explain that the API has twelve pods, so a mutex is meaningless, then ship a compare-and-set `UPDATE ... WHERE status = 'AVAILABLE'` for the hold, a partial unique index as a safety net, and a short confirm transaction after the gateway callback. Support tickets about double-sold slots drop to zero, and the pool never starves because no transaction waits on the gateway.

## Practice Loop

1. Run the `Barrier` demo three times and confirm both threads report success. Then add a `threading.Lock` around check and act and observe one failure.
2. Run the 20-thread SQLite compare-and-set demo and confirm exactly one winner. Change the `WHERE` clause to drop `AND status = 'AVAILABLE'` and observe 20 "winners".
3. Create the partial unique index in SQLite, insert two active rows for one show seat, and watch the second fail. Deactivate the first and retry.
4. Implement `retry` with an injectable `sleep` and a fake `SerializationFailure`. Assert the delays double and that a `ValueError` is not retried.
5. Sketch `hold_seats` with `with_for_update`, and write the timeline for two transactions overlapping on seats `[1, 2]` and `[2, 1]`. Show how `order_by` prevents a deadlock.
6. Write the confirm step: given a booking id, re-check `BLOCKED` and expiry and flip to `BOOKED`, or raise.

## Evidence of Understanding

- You can explain check-then-act and demonstrate it with a deterministic interleaving.
- You can say why a `threading.Lock` fails across processes and name where the coordination must live instead.
- You can state what Repeatable Read and Serializable guarantee, and that Serializable allows unrelated transactions to commit concurrently.
- You can implement and compare four fixes (row lock, compare-and-set, unique constraint, optimistic version) and choose by contention level.
- You can explain why a serializable transaction needs a retry loop, and which errors qualify.
- You can justify soft locks over holding a transaction open during payment.

## Interview Questions to Rehearse

### Q: Two users book the same seat. Walk me through why it happens and how you fix it.

Both requests read `AVAILABLE` before either writes `BLOCKED`, a check-then-act race. The fix is to make check and act atomic in the database: lock the rows with `SELECT ... FOR UPDATE`, or fold the check into the write with `UPDATE ... WHERE status = 'AVAILABLE'` and verify `rowcount`, or add a unique constraint so the second insert fails. I would add a constraint even when I use a lock, as a backstop.

### Q: Why isn't a `threading.Lock` enough?

It only coordinates threads within one process's memory. Production runs many workers and pods, each with its own lock object. The invariant is about a database row shared by all of them, so enforcement must be in the database or in a distributed primitive designed for it.

### Q: Does Repeatable Read prevent the double booking?

Not in the check-then-act form. It gives each transaction a stable snapshot for reads, so both see `AVAILABLE`. On MySQL the second `UPDATE` waits for the row lock and then overwrites; PostgreSQL's Repeatable Read would abort the second transaction instead. Only locking reads, atomic conditional writes, constraints or Serializable protect the rule.

### Q: What does Serializable cost you?

Aborted transactions. The result must equal some serial order, so the database detects conflicts and fails one with a serialization error. Unrelated transactions still run concurrently, but the application must retry with jittered backoff, and retries must be idempotent for side effects outside the database.

### Q: Pessimistic or optimistic locking for seats?

Hot inventory with high contention favours pessimistic locks or compare-and-set, because optimistic retries waste work. Low-contention, long-edit flows favour version columns because no locks are held. Whichever I pick, I keep transactions short and never hold one across a payment call.

## Common Pitfalls

- Believing the GIL makes multi-step logic safe.
- Adding a process-local lock and testing only with one process.
- Locking rows in inconsistent order, causing deadlocks.
- Treating Repeatable Read as "no concurrency bugs".
- Using Serializable with no retry loop, or retrying non-idempotent side effects.
- Checking `rowcount` after a multi-seat compare-and-set but forgetting to roll back the partial win.
- Keeping a transaction open while waiting on a payment gateway.
- Unique constraints on `show_seat_id` that forbid rebooking after a cancellation (use a partial index on active rows).

## Suggested Extension

Replace the soft-lock expiry with a PostgreSQL advisory lock around the confirm step (`pg_advisory_xact_lock(show_seat_id)`), and write a short comparison of advisory locks, row locks and a Redis lock: scope, failure behaviour on crash, and what happens when the lock holder is paused for longer than the lease.
