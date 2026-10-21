# Code Parking Lot 2: Payments, Fees and Concurrency

The first half of the parking-lot feature is easy to demo: a car arrives, a ticket is issued. The second half is where the interviewer's follow-ups go: how are fees calculated and how do you add a new tariff, what happens when a customer pays part in cash and the rest by UPI, and what happens when two gates hand out the same spot. Each follow-up tests one idea you must be able to code under time pressure: Strategy for fees, a payment model that survives failure, and a lock that actually protects the right thing.

## Concepts Covered

### The layers, one more time

The service layer keeps the rule from the previous lesson: it takes plain values and returns models, and never touches a DTO. The controller unwraps the request DTO, calls the service, and wraps the response DTO. The repository only saves and finds. Because `BillService` and `PaymentService` follow the same rule as `TicketService`, their controllers are pure wiring, the same unwrap, call, wrap shape you already wrote, which is why interviewers accept them as quick additions or as homework. The generic repository is declared once as `InMemoryRepository(Generic[T])` with `T = TypeVar("T", bound=BaseModel)`, because `save` and `find_by_id` are identical for every model. Remember that the bound is advisory: for a class with no `id`, `repo.save(Foo())` fails at runtime with `AttributeError` on the first `item.id`, since only a type checker enforces the bound.

### Fee strategies

Fees are the part of a parking lot most likely to change, so they sit behind a `FeeStrategy` interface. Two tariffs appear in the exercises. **Weekday**: a flat rate per started hour for every vehicle type. **Weekend**: slab pricing per vehicle type, where each hour is charged at the rate of the slab it falls into, like a marginal tax bracket. For a car with slabs 0-2 at 20, 2-4 at 30, 4-6 at 40 and 6 onwards at 50, three hours cost 2 x 20 + 1 x 30 = 70, and seven hours cost 40 + 60 + 80 + 50 = 230. A slab with end hour `-1` has no upper limit. A small factory chooses the tariff from the exit date; `weekday()` returns 5 and 6 for Saturday and Sunday.

Two details are worth saying aloud. Hours are **rounded up** (61 minutes is two hours), and a stay shorter than a minute still costs a minimum of one hour; define that rule once in `started_hours`. And the slab loop stops at the first slab whose start is not below the total, which is the line people get wrong.

```python
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


def started_hours(entry: datetime, exit_: datetime) -> int:
    """Every started hour counts: 61 minutes is 2 hours. The minimum bill is one hour."""
    return max(1, math.ceil((exit_ - entry).total_seconds() / 3600))


class FeeStrategy(ABC):
    @abstractmethod
    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float: ...


class WeekdayFee(FeeStrategy):
    """A flat rate of 10 per started hour for every vehicle type."""

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        return 10.0 * started_hours(entry, exit_)


@dataclass(frozen=True)
class Slab:
    start_hour: int
    end_hour: int          # -1 means "no upper limit"
    price: float           # per hour inside this slab


class WeekendSlabFee(FeeStrategy):
    """Each hour is charged at the rate of the slab it falls in (a marginal, tax-bracket style tariff)."""

    def __init__(self, slabs: Mapping[VehicleType, Sequence[Slab]]) -> None:
        self._slabs = {t: sorted(s, key=lambda slab: slab.start_hour) for t, s in slabs.items()}

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        hours, total = started_hours(entry, exit_), 0.0
        for slab in self._slabs[vehicle_type]:
            if hours <= slab.start_hour:
                break
            upper = hours if slab.end_hour == -1 else min(hours, slab.end_hour)
            total += (upper - slab.start_hour) * slab.price
        return total


class FeeStrategyFactory:
    """The single place that knows weekends differ: Saturday and Sunday have weekday() 5 and 6."""

    def __init__(self, weekday: FeeStrategy, weekend: FeeStrategy) -> None:
        self._weekday, self._weekend = weekday, weekend

    def for_exit_time(self, exit_: datetime) -> FeeStrategy:
        return self._weekend if exit_.weekday() in (5, 6) else self._weekday
```

```python
CAR_SLABS = [Slab(0, 2, 20), Slab(2, 4, 30), Slab(4, 6, 40), Slab(6, -1, 50)]
weekend = WeekendSlabFee({VehicleType.CAR: CAR_SLABS})
factory = FeeStrategyFactory(WeekdayFee(), weekend)

saturday = datetime(2026, 1, 3, 9, 0)          # a Saturday
print([weekend.calculate(saturday, saturday.replace(hour=9 + h), VehicleType.CAR) for h in (1, 3, 5, 7)])

monday = datetime(2026, 1, 5, 10, 0)
print(factory.for_exit_time(datetime(2026, 1, 5, 11, 30)).calculate(monday, datetime(2026, 1, 5, 11, 30), VehicleType.CAR))
print(type(factory.for_exit_time(datetime(2026, 1, 3, 12, 0))).__name__)
```

```text
[20.0, 70.0, 140.0, 230.0]
20.0
WeekendSlabFee
```

### Bills and partial payments

A customer may pay 200 in cash and 300 by UPI for a bill of 500, recorded as two `Payment` objects with an amount, mode and status. The bill is settled only when the sum of **successful** payments reaches the bill amount. A failed attempt is kept for the audit trail but adds nothing. If the 300 UPI payment fails, the total is 200, the bill stays unpaid, and the spot stays occupied; a successful retry settles the bill and frees the spot. Free the spot only when the bill is settled, and reject an amount larger than the outstanding balance before calling the gateway, so a bad request never charges a card.

```python
from collections.abc import Callable


class PaymentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"


class SpotStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"


@dataclass(eq=False)
class Spot:
    number: int
    status: SpotStatus = SpotStatus.OCCUPIED


@dataclass(frozen=True)
class Payment:
    amount: float
    mode: str
    status: PaymentStatus


@dataclass(eq=False)
class Bill:
    amount: float
    spot: Spot
    payments: list[Payment]

    @property
    def total_paid(self) -> float:
        """Only successful payments count: a failed attempt is kept for the audit trail but adds nothing."""
        return sum(p.amount for p in self.payments if p.status is PaymentStatus.SUCCESS)

    @property
    def is_paid(self) -> bool:
        return self.total_paid >= self.amount


class OverpaymentError(Exception):
    pass


class PaymentService:
    """Plain values in, a model out. The gateway is injected: it returns True when the charge went through."""

    def __init__(self, gateway: Callable[[float, str], bool]) -> None:
        self._gateway = gateway

    def make_payment(self, bill: Bill, amount: float, mode: str) -> Payment:
        if amount > bill.amount - bill.total_paid:
            raise OverpaymentError(f"only {bill.amount - bill.total_paid} is outstanding")
        ok = self._gateway(amount, mode)
        payment = Payment(amount, mode, PaymentStatus.SUCCESS if ok else PaymentStatus.FAILED)
        bill.payments.append(payment)
        if bill.is_paid:
            bill.spot.status = SpotStatus.AVAILABLE      # free the spot only when the bill is settled
        return payment
```

```python
outcomes = iter([True, False, True])            # cash ok, UPI fails, UPI retry ok
service = PaymentService(lambda amount, mode: next(outcomes))
bill = Bill(500, Spot(7), [])

service.make_payment(bill, 200, "cash")
service.make_payment(bill, 300, "upi")
print(bill.total_paid, bill.is_paid, bill.spot.status.name)
service.make_payment(bill, 300, "upi")
print(bill.total_paid, bill.is_paid, bill.spot.status.name, len(bill.payments))
```

```text
200 False OCCUPIED
500 True AVAILABLE 3
```

### The race, and why the GIL does not save you

Two gates call `issue_ticket` at the same moment, and both can receive the same spot. The GIL ensures that only one thread executes Python bytecode at a time, which tempts people to say "so it is safe". It is not. The GIL makes individual bytecode operations safe, but "read the spot status" and "later write the spot status" are separate steps, and the interpreter can switch threads in the gap between them. The read-then-write sequence as a whole is not atomic. The gap in real code is a database call, a log line or a network request; the demo below makes it explicit with a short sleep and releases both threads at the same instant with a `threading.Barrier`, so the outcome is reliable instead of rare.

The fix is a lock that both gates share, around the **whole** check-and-update. The lock must be created **once**, in `__init__`, and reused on every call. A lock only blocks threads that try to acquire that exact lock object; if each call does `lock = threading.Lock()` locally, every gate gets a private lock, nobody waits on anybody, and the race is back.

A subtler trap is lock granularity. An AI assistant may suggest one lock per `VehicleType`. But if a single spot supports several types (a large spot for a truck, a car or a bike), a car gate and a truck gate acquire two different locks, both read the same spot as available, and both assign it. The lock must cover the **resource** being contended, here the set of spots, not a property of the request. The demo reproduces all four variants.

```python
import threading
import time
from collections import defaultdict


class ParkingFullError(Exception):
    pass


@dataclass(eq=False)
class SharedSpot:
    number: int
    types: frozenset[VehicleType]
    status: SpotStatus = SpotStatus.AVAILABLE


class NaiveAllocator:
    """Read, then write, with a gap between them. The gap stands for logging, a DB call, anything."""

    def __init__(self, spots: list[SharedSpot]) -> None:
        self._spots = spots

    def allocate(self, vehicle_type: VehicleType) -> SharedSpot:
        spot = next((s for s in self._spots
                     if s.status is SpotStatus.AVAILABLE and vehicle_type in s.types), None)
        if spot is None:
            raise ParkingFullError
        time.sleep(0.02)                                   # another thread can run right here
        spot.status = SpotStatus.OCCUPIED
        return spot


class LockedAllocator(NaiveAllocator):
    def __init__(self, spots: list[SharedSpot]) -> None:
        super().__init__(spots)
        self._lock = threading.Lock()                      # created once, shared by every call

    def allocate(self, vehicle_type: VehicleType) -> SharedSpot:
        with self._lock:                                   # check and update become one step
            return super().allocate(vehicle_type)


class FreshLockAllocator(NaiveAllocator):
    def allocate(self, vehicle_type: VehicleType) -> SharedSpot:
        lock = threading.Lock()                            # BUG: every call gets its own private lock
        with lock:
            return super().allocate(vehicle_type)


class PerTypeLockAllocator(NaiveAllocator):
    def __init__(self, spots: list[SharedSpot]) -> None:
        super().__init__(spots)
        self._locks: dict[VehicleType, threading.Lock] = defaultdict(threading.Lock)

    def allocate(self, vehicle_type: VehicleType) -> SharedSpot:
        with self._locks[vehicle_type]:                    # BUG: a CAR and a TRUCK use different locks
            return super().allocate(vehicle_type)


def race(allocator: NaiveAllocator, vehicle_types: list[VehicleType]) -> list[str]:
    barrier, outcomes, guard = threading.Barrier(len(vehicle_types)), [], threading.Lock()

    def gate(vehicle_type: VehicleType) -> None:
        barrier.wait()                                     # release every gate at the same instant
        try:
            outcome = f"got spot {allocator.allocate(vehicle_type).number}"
        except ParkingFullError:
            outcome = "lot full"
        with guard:
            outcomes.append(outcome)

    threads = [threading.Thread(target=gate, args=(t,)) for t in vehicle_types]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return sorted(outcomes)
```

```python
def one_spot(*types: VehicleType) -> list[SharedSpot]:
    return [SharedSpot(1, frozenset(types))]


two_cars = [VehicleType.CAR, VehicleType.CAR]
print("no lock        :", race(NaiveAllocator(one_spot(VehicleType.CAR)), two_cars))
print("shared lock    :", race(LockedAllocator(one_spot(VehicleType.CAR)), two_cars))
print("fresh lock     :", race(FreshLockAllocator(one_spot(VehicleType.CAR)), two_cars))
print("lock per type  :", race(PerTypeLockAllocator(one_spot(VehicleType.CAR, VehicleType.TRUCK)),
                               [VehicleType.CAR, VehicleType.TRUCK]))
```

```text
no lock        : ['got spot 1', 'got spot 1']
shared lock    : ['got spot 1', 'lot full']
fresh lock     : ['got spot 1', 'got spot 1']
lock per type  : ['got spot 1', 'got spot 1']
```

With the correct shared lock the outcome is guaranteed however many times it is run: exactly one gate gets the spot and the other sees a full lot, never both and never a deadlock, because each thread acquires and releases one lock and holds nothing else.

> **Production note:** A `threading.Lock` protects threads inside one process. If the API runs several worker processes (as `uvicorn --workers` or gunicorn do), each has its own lock and its own memory, so the race returns. The guarantee must move to the shared resource: an atomic `UPDATE ... WHERE status = 'AVAILABLE'` whose affected-row count you check, a row lock with `SELECT ... FOR UPDATE`, or a unique constraint. The BookMyShow lessons do exactly that.

### Testing the lot deterministically

Concurrency tests that pass "usually" are worse than none. Use a `Barrier` to force the interleaving, repeat the scenario, and assert the invariant (one winner) rather than a timing. Alongside, plain unit tests pin the fee examples and the partial-payment rules.

```python
import pytest


def test_slab_fees_match_the_published_examples() -> None:
    start = datetime(2026, 1, 3, 9, 0)
    fees = [weekend.calculate(start, start.replace(hour=9 + h), VehicleType.CAR) for h in (1, 3, 5, 7)]
    assert fees == [20.0, 70.0, 140.0, 230.0]


def test_weekday_rounds_started_hours_up() -> None:
    start = datetime(2026, 1, 5, 10, 0)
    assert WeekdayFee().calculate(start, datetime(2026, 1, 5, 11, 30), VehicleType.BIKE) == 20.0
    assert WeekdayFee().calculate(start, datetime(2026, 1, 5, 11, 0), VehicleType.BIKE) == 10.0


def test_a_failed_payment_does_not_count_and_a_retry_settles_the_bill() -> None:
    results = iter([True, False, True])
    service, bill = PaymentService(lambda a, m: next(results)), Bill(500, Spot(1), [])
    service.make_payment(bill, 200, "cash")
    service.make_payment(bill, 300, "upi")
    assert bill.total_paid == 200 and not bill.is_paid and bill.spot.status is SpotStatus.OCCUPIED
    service.make_payment(bill, 300, "upi")
    assert bill.is_paid and bill.spot.status is SpotStatus.AVAILABLE


def test_overpayment_is_rejected_before_the_gateway_is_called() -> None:
    calls = []
    service = PaymentService(lambda a, m: calls.append(a) or True)
    with pytest.raises(OverpaymentError):
        service.make_payment(Bill(100, Spot(1), []), 150, "cash")
    assert calls == []


def test_shared_lock_gives_the_single_spot_to_exactly_one_gate_every_time() -> None:
    for _ in range(10):
        results = race(LockedAllocator(one_spot(VehicleType.CAR)), two_cars)
        assert results == ["got spot 1", "lot full"]
```

All five tests pass, including ten repetitions of the locked race.

## Practical Backend Scenario

An LLM gateway has a pool of GPU slots and several request workers in one process. A request checks for a free slot of a suitable class and then marks it busy. It fails in exactly the parking-lot way: two requests read the same free slot and both launch on it. The cure is the same: one shared lock around check-and-mark, created at construction, covering the pool and not a property of the request. When the gateway scales out to several processes, the lock moves into Redis or the database, and billing follows the same payment logic: usage charged in several attempts, only successful charges counted, the slot released when the bill is settled.

## Practice Loop

1. Implement `WeekdayFee` and `WeekendSlabFee` and check the four published values (20, 70, 140, 230) in a test. Add a third tariff for holidays as a new class.
2. Add `OverpaymentError` and prove with a test that the gateway is not called when the amount exceeds the balance.
3. Reproduce the double allocation with `NaiveAllocator` and a `Barrier`, then fix it with a shared lock created in `__init__`.
4. Turn the lock into a local variable inside `allocate` and watch the test fail, then explain why.
5. Implement the per-type lock, find the failing scenario with a spot that supports two types, and fix it with one lock over the spot collection.
6. Write the paragraph you would say in an interview about why a thread lock is not enough with multiple workers.

## Evidence of Understanding

- I can describe the controller, service and repository responsibilities and why a controller for bills or payments is only wiring.
- I can explain why `TypeVar(bound=...)` does not stop a bad type at runtime.
- I can compute weekday and weekend slab fees and explain the rounding rule.
- I can say why only successful payments count and when the spot is freed.
- I can explain why the GIL does not make read-then-write atomic.
- I can explain why the lock must be created once and shared, and why a lock per vehicle type fails.
- I can state the guaranteed outcome of the locked two-gate test, and why it cannot deadlock.
- I can say what changes when the service runs in several processes.

## Interview Questions to Rehearse

### Q: Python has a GIL. Why do you need a lock at all?

The GIL serialises bytecode execution, not your logic. "Check the spot is free" and "mark it occupied" are separate steps, and the interpreter may switch threads between them, so two threads can both pass the check. A lock makes the whole sequence one critical section. The GIL protects the interpreter's internals, not application invariants.

### Q: Where should the lock be created, and why?

Once, in the constructor, so every call on that service instance, from every gate, acquires the same object. A lock blocks only threads trying to acquire that exact lock. A lock created inside the method gives each thread its own, so nobody ever waits and the race remains.

### Q: Would you use one lock per vehicle type to reduce contention?

Only if spots are disjoint by type. When one spot can serve several types, different locks let a car and a truck both claim it. I would lock the resource, the collection of spots, accept the contention for a parking lot's volume, and if it became a bottleneck shard by floor or by spot. In a database I would use a row lock on the spot.

### Q: A customer pays 200 in cash and 300 by UPI, and the UPI payment fails. What state is the system in?

The bill amount is 500 and successful payments total 200, so the bill is unpaid and the spot stays occupied. The failed payment is stored for the audit trail but does not count. The customer retries 300; when successful payments reach 500 the bill is settled and the spot is freed. An amount above the outstanding balance is rejected before calling the gateway.

### Q: Why is a threading lock not a solution in production?

Because production runs several worker processes, and a lock lives in one process's memory. The guarantee has to come from the shared resource: an atomic conditional update, a row lock inside a transaction, or a uniqueness constraint. I would still keep an in-process lock for in-memory structures, and say clearly which problem each one solves.

## Common Pitfalls

- Believing the GIL makes check-then-act sequences safe.
- Creating the lock inside the method, so every call has its own.
- One lock per request attribute (vehicle type) when the contended resource is shared across types.
- Holding the lock while calling slow external services, so the whole lot serialises behind one gateway call.
- Counting failed payments, or freeing the spot after a partial payment.
- Calling the gateway before checking the outstanding balance.
- Treating the slab table as a flat per-hour rate for the whole stay, instead of marginal rates per slab.
- A concurrency test with no barrier, which passes by luck on the machine you run it on.

## Suggested Extension

Replace the single lock with one lock per floor and have the allocator try floors in order, acquiring only the lock of the floor it inspects. Prove with the barrier test that a car and a truck racing for the same single spot still yield exactly one winner, and describe the lock-ordering rule you need if an allocation ever has to take two floor locks.
