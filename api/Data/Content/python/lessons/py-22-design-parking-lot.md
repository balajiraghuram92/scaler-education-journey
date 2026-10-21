# Design Parking Lot

"Design a parking lot" is the design question that gets asked most often, because it is small enough to finish and rich enough to show judgement: multiple floors, several vehicle types, tickets and bills, and two behaviours that obviously vary (where to park, how much to charge). This lesson is the design half: requirements, user journey, entities, class diagram, patterns and schema, with a skeleton in Python that proves the diagram is coherent. The next two lessons turn it into layered, running code.

## Concepts Covered

### Step 0 and 1: align, then gather requirements

Align first. For this problem the agreed answers are: an interactive system, a command line and not a GUI, and in-memory state for now. Then gather requirements from outside to inside, structure first and then the user journey, and split them into a minimum viable product and version 2. Propose, do not ask.

| # | Requirement | Scope |
|---|---|---|
| 1 | Entry and exit gates, one of each or more | MVP |
| 2 | Many parking spots, supporting different vehicle types | MVP |
| 3 | Multiple floors | MVP |
| 4 | Lift-based parking | Version 2 |
| 5 | Lifts and stairs to move between floors | MVP (as a note, no model) |
| 6 | Emergency exit path | Version 2 |
| 7 | A ticket is generated at the entry gate | MVP |
| 8 | An operator staffs each gate | MVP |
| 9 | A spot is assigned; handle "no spot available" | MVP |
| 10 | Pluggable parking strategies | Version 2 for new variants, but design the seam now |
| 11 | A bill is generated at the exit gate, with fee calculation | MVP |
| 12 | Payment at exit, in several modes (cash, card, UPI, FASTag) | MVP |
| 13 | Value-added services such as cleaning | Version 2 |
| 14 | Online booking | Version 2 |

Fee calculation is where requirements explode: vehicle type, duration, time of day, day of the week, holiday surcharge, overnight parking, lost ticket, monthly pass. You do not implement them all. You note them and make the fee a replaceable piece.

The user journey ties the list together: a vehicle arrives at an entry gate, a ticket is issued and a spot assigned, the entry is stored, and on exit the fee is calculated, payment is taken, and the spot becomes available again immediately.

### Entities by noun spotting

Underline the nouns: lot, gate (entry or exit), floor, spot, vehicle, ticket, bill, payment, operator. Attributes that are fixed sets become enums: vehicle type, gate type, spot status, floor status, payment mode and status. Verbs become behaviour on the owner of the data, or become strategies when they vary: "assign a spot" and "calculate a fee".

```text
 ParkingLot 1 <>---- * ParkingFloor 1 <>---- * ParkingSpot (supported VehicleType, SpotStatus)
     |  1 <>---- * Gate (GateType) o---- 0..1 Operator
 Vehicle (VehicleType)
 Ticket  -> Vehicle, ParkingSpot, Gate (entry), entry_time
 Bill    -> Ticket, Gate (exit), exit_time, amount
 Payment -> Bill, amount, PaymentMode, PaymentStatus, reference
 <<interface>> SpotAssignmentStrategy   assign(lot, vehicle_type) -> spot | none
 <<interface>> FeeStrategy              calculate(entry, exit, vehicle_type) -> amount
 ParkingLotBuilder                      validates floors, gates, spot numbers, then builds the lot
```

Relationships carry meaning. A lot **composes** its floors and a floor composes its spots: they have no life outside the lot. A ticket merely **references** a vehicle, a spot and a gate. One bill belongs to one ticket, and a bill may have several payments, which is what makes a partial or retried payment possible.

### Choosing patterns on purpose

- **Strategy for spot assignment.** "Fill the nearest spot" and "fill the fullest floor first" are two real policies, and the interviewer will ask for a third.
- **Strategy for fee calculation.** Weekday flat hourly, weekend slabs, monthly pass: each is one class behind one interface. A small **Factory** can choose the strategy from the exit time.
- **Builder for the lot.** A lot has cross-cutting validity rules (at least one floor, one entry and one exit gate, unique floor and spot numbers). Validate them together before the object exists.
- **Not** a Singleton for the lot, even though there is one lot in the demo. A real deployment has several, and a global makes tests order-dependent.

### Skeleton: models

The models are plain dataclasses and enums. Nothing here has behaviour yet; that is deliberate, because behaviour lives in strategies and services.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


class GateType(Enum):
    ENTRY = "entry"
    EXIT = "exit"


class SpotStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    OUT_OF_SERVICE = "out_of_service"


class FloorStatus(Enum):
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"


class PaymentMode(Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"


class PaymentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class ParkingSpot:
    number: int
    supported_vehicle_type: VehicleType
    status: SpotStatus = SpotStatus.AVAILABLE


@dataclass
class ParkingFloor:
    floor_number: int
    spots: list[ParkingSpot] = field(default_factory=list)
    status: FloorStatus = FloorStatus.OPERATIONAL


@dataclass
class Operator:
    name: str


@dataclass
class Gate:
    gate_id: int
    gate_type: GateType
    operator: Operator | None = None


@dataclass
class ParkingLot:
    name: str
    floors: list[ParkingFloor]
    gates: list[Gate]


@dataclass
class Vehicle:
    registration_number: str
    vehicle_type: VehicleType


@dataclass
class Ticket:
    ticket_id: int
    vehicle: Vehicle
    spot: ParkingSpot
    gate: Gate
    entry_time: datetime


@dataclass
class Bill:
    ticket: Ticket
    gate: Gate
    exit_time: datetime
    amount: float


@dataclass
class Payment:
    bill: Bill
    amount: float
    mode: PaymentMode
    status: PaymentStatus
    reference: str
```

### Skeleton: strategies and the Builder

Two assignment strategies follow, to prove the seam. `NearestSpotStrategy` takes the first free spot on the lowest operational floor. `LeastAvailableFloorStrategy` picks the operational floor with the fewest free spots of that type (greater than zero), breaking ties by the lowest floor number, and then the nearest spot; it keeps the lot compact so whole floors can be shut. Both return `None` when nothing is free, and the caller decides what "no spot available" means. The fee strategy rounds started hours up, with a one-hour minimum. The Builder collects every problem.

```python
import math
from abc import ABC, abstractmethod


class InvalidParkingLotConfigError(Exception):
    """The Builder refused to create a lot; the message lists every problem."""


class SpotAssignmentStrategy(ABC):
    @abstractmethod
    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None: ...


def _available(floor: ParkingFloor, vehicle_type: VehicleType) -> list[ParkingSpot]:
    return [s for s in floor.spots
            if s.status is SpotStatus.AVAILABLE and s.supported_vehicle_type is vehicle_type]


class NearestSpotStrategy(SpotAssignmentStrategy):
    """First available matching spot on the lowest operational floor."""

    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None:
        for floor in sorted(lot.floors, key=lambda f: f.floor_number):
            if floor.status is FloorStatus.OPERATIONAL:
                free = _available(floor, vehicle_type)
                if free:
                    return min(free, key=lambda s: s.number)
        return None


class LeastAvailableFloorStrategy(SpotAssignmentStrategy):
    """Fill the fullest floor first: fewest free spots for this type, ties to the lowest floor."""

    def assign(self, lot: ParkingLot, vehicle_type: VehicleType) -> ParkingSpot | None:
        candidates = [(len(free), f.floor_number, free) for f in lot.floors
                      if f.status is FloorStatus.OPERATIONAL and (free := _available(f, vehicle_type))]
        if not candidates:
            return None
        _, _, free = min(candidates, key=lambda c: (c[0], c[1]))
        return min(free, key=lambda s: s.number)


class FeeStrategy(ABC):
    @abstractmethod
    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float: ...


class HourlyFeeStrategy(FeeStrategy):
    """Rate per started hour, by vehicle type."""

    RATES = {VehicleType.BIKE: 10.0, VehicleType.CAR: 20.0, VehicleType.TRUCK: 50.0}

    def calculate(self, entry: datetime, exit_: datetime, vehicle_type: VehicleType) -> float:
        hours = max(1, math.ceil((exit_ - entry).total_seconds() / 3600))
        return hours * self.RATES[vehicle_type]


class ParkingLotBuilder:
    def __init__(self, name: str) -> None:
        self._name = name
        self._floors: list[ParkingFloor] = []
        self._gates: list[Gate] = []

    def add_floor(self, floor: ParkingFloor) -> ParkingLotBuilder:
        self._floors.append(floor)
        return self

    def add_gate(self, gate: Gate) -> ParkingLotBuilder:
        self._gates.append(gate)
        return self

    def build(self) -> ParkingLot:
        problems = []
        if not self._floors:
            problems.append("at least one floor is required")
        if len({f.floor_number for f in self._floors}) != len(self._floors):
            problems.append("floor numbers must be unique")
        for f in self._floors:
            if len({s.number for s in f.spots}) != len(f.spots):
                problems.append(f"floor {f.floor_number} has duplicate spot numbers")
        kinds = {g.gate_type for g in self._gates}
        if GateType.ENTRY not in kinds or GateType.EXIT not in kinds:
            problems.append("need at least one entry gate and one exit gate")
        if problems:
            raise InvalidParkingLotConfigError("; ".join(problems))
        return ParkingLot(self._name, self._floors, self._gates)
```

Run them on a small lot. The demo prints the floor by identity, not by `in`: dataclasses compare field by field, so two different spots with the same number, type and status are `==`, and `spot in floor.spots` can match the wrong floor.

```python
def spots(floor_number: int, bikes: int, cars: int, first: int = 1) -> ParkingFloor:
    nums = iter(range(first, first + bikes + cars))
    return ParkingFloor(floor_number,
                        [ParkingSpot(next(nums), VehicleType.BIKE) for _ in range(bikes)]
                        + [ParkingSpot(next(nums), VehicleType.CAR) for _ in range(cars)])


floor0, floor1 = spots(0, bikes=1, cars=3), spots(1, bikes=1, cars=1)
lot = (ParkingLotBuilder("Central")
       .add_floor(floor0).add_floor(floor1)
       .add_gate(Gate(1, GateType.ENTRY, Operator("Asha")))
       .add_gate(Gate(2, GateType.EXIT, Operator("Ravi")))
       .build())

for strategy in (NearestSpotStrategy(), LeastAvailableFloorStrategy()):
    spot = strategy.assign(lot, VehicleType.CAR)
    floor_no = next(f.floor_number for f in lot.floors if any(s is spot for s in f.spots))   # identity, not ==
    print(f"{type(strategy).__name__}: floor {floor_no}, spot {spot.number}")

entry = datetime(2026, 1, 5, 10, 0)
print(HourlyFeeStrategy().calculate(entry, datetime(2026, 1, 5, 11, 30), VehicleType.CAR))   # 90 minutes = 2 started hours
print(HourlyFeeStrategy().calculate(entry, datetime(2026, 1, 5, 11, 0), VehicleType.CAR))    # exactly 1 hour

try:
    ParkingLotBuilder("Broken").add_floor(ParkingFloor(0)).add_gate(Gate(1, GateType.ENTRY)).build()
except InvalidParkingLotConfigError as exc:
    print("config error:", exc)
```

```text
NearestSpotStrategy: floor 0, spot 2
LeastAvailableFloorStrategy: floor 1, spot 2
40.0
20.0
config error: need at least one entry gate and one exit gate
```

The two strategies disagree, which is the point: switching policy is a constructor argument, and the 90-minute fee rounds up to two started hours.

```python
import pytest


def make_lot() -> ParkingLot:
    return (ParkingLotBuilder("T").add_floor(spots(0, 1, 3)).add_floor(spots(1, 1, 1))
            .add_gate(Gate(1, GateType.ENTRY)).add_gate(Gate(2, GateType.EXIT)).build())


def test_least_available_floor_picks_the_fuller_floor_and_nearest_spot() -> None:
    lot = make_lot()                                      # floor 0 has 3 free cars, floor 1 has 1
    spot = LeastAvailableFloorStrategy().assign(lot, VehicleType.CAR)
    assert spot is lot.floors[1].spots[1]


def test_nearest_strategy_skips_floors_under_maintenance() -> None:
    lot = make_lot()
    lot.floors[0].status = FloorStatus.UNDER_MAINTENANCE
    assert NearestSpotStrategy().assign(lot, VehicleType.CAR) is lot.floors[1].spots[1]


def test_no_spot_returns_none_instead_of_raising() -> None:
    lot = make_lot()
    for floor in lot.floors:
        for s in floor.spots:
            s.status = SpotStatus.OCCUPIED
    assert NearestSpotStrategy().assign(lot, VehicleType.CAR) is None


def test_fee_rounds_started_hours_up_and_has_a_one_hour_minimum() -> None:
    fee = HourlyFeeStrategy()
    start = datetime(2026, 1, 5, 10, 0)
    assert fee.calculate(start, datetime(2026, 1, 5, 10, 1), VehicleType.CAR) == 20.0
    assert fee.calculate(start, datetime(2026, 1, 5, 12, 1), VehicleType.TRUCK) == 150.0


def test_builder_lists_all_problems() -> None:
    with pytest.raises(InvalidParkingLotConfigError) as info:
        ParkingLotBuilder("X").build()
    assert "floor" in str(info.value) and "gate" in str(info.value)
```

All five tests pass against the code above, and none needed a database.

### Schema design

Convert the diagram mechanically. Every class becomes a table. Primitive attributes become columns. Non-primitive attributes become relationships, so decide cardinality and put the foreign key on the "many" side: `parking_floors.parking_lot_id`, `parking_spots.parking_floor_id`, `tickets.parking_spot_id`. Enums become constrained columns or lookup tables; lookup tables make adding a vehicle type a data change instead of a migration. Add uniqueness where the domain demands it: a spot number is unique within a floor, a bill belongs to exactly one ticket.

```sql
CREATE TABLE parking_lots (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE parking_floors (
    id             INTEGER PRIMARY KEY,
    parking_lot_id INTEGER NOT NULL REFERENCES parking_lots(id),
    floor_number   INTEGER NOT NULL,
    status         TEXT NOT NULL CHECK (status IN ('OPERATIONAL', 'UNDER_MAINTENANCE')),
    UNIQUE (parking_lot_id, floor_number)
);
CREATE TABLE parking_spots (
    id                      INTEGER PRIMARY KEY,
    parking_floor_id        INTEGER NOT NULL REFERENCES parking_floors(id),
    spot_number             INTEGER NOT NULL,
    supported_vehicle_type  TEXT NOT NULL CHECK (supported_vehicle_type IN ('BIKE', 'CAR', 'TRUCK')),
    status                  TEXT NOT NULL CHECK (status IN ('AVAILABLE', 'OCCUPIED', 'OUT_OF_SERVICE')),
    UNIQUE (parking_floor_id, spot_number)
);
CREATE TABLE operators (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE gates (
    id             INTEGER PRIMARY KEY,
    parking_lot_id INTEGER NOT NULL REFERENCES parking_lots(id),
    gate_type      TEXT NOT NULL CHECK (gate_type IN ('ENTRY', 'EXIT')),
    operator_id    INTEGER REFERENCES operators(id)
);
CREATE TABLE vehicles (
    id                  INTEGER PRIMARY KEY,
    registration_number TEXT NOT NULL UNIQUE,
    vehicle_type        TEXT NOT NULL
);
CREATE TABLE tickets (
    id              INTEGER PRIMARY KEY,
    vehicle_id      INTEGER NOT NULL REFERENCES vehicles(id),
    parking_spot_id INTEGER NOT NULL REFERENCES parking_spots(id),
    gate_id         INTEGER NOT NULL REFERENCES gates(id),
    entry_time      TEXT NOT NULL
);
CREATE TABLE bills (
    id         INTEGER PRIMARY KEY,
    ticket_id  INTEGER NOT NULL UNIQUE REFERENCES tickets(id),
    gate_id    INTEGER NOT NULL REFERENCES gates(id),
    exit_time  TEXT NOT NULL,
    amount     REAL NOT NULL
);
CREATE TABLE payments (
    id        INTEGER PRIMARY KEY,
    bill_id   INTEGER NOT NULL REFERENCES bills(id),
    amount    REAL NOT NULL,
    mode      TEXT NOT NULL CHECK (mode IN ('CASH', 'CARD', 'UPI')),
    status    TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED')),
    reference TEXT
);
```

I ran this DDL in SQLite with `PRAGMA foreign_keys = ON`: inserting a second spot with number 1 on floor 1 was rejected with `UNIQUE constraint failed: parking_spots.parking_floor_id, parking_spots.spot_number`, and a capacity query grouped free car spots per floor, which is exactly the question the "least available floor" strategy asks the database.

### Two things to say out loud

Concurrency: two entry gates can both read the same spot as free and both assign it. The design leaves room for a lock or a database constraint; the machine-coding lessons implement it. Scale: one lot is in memory; many lots mean spots live in a database and the assignment query must be atomic.

## Practical Backend Scenario

A GPU cluster scheduler for a forward-deployed customer assigns fine-tuning jobs to nodes, and the requirements read like a parking lot: nodes with floors (racks), slots that only fit certain job types (GPU class), a ticket when a job is admitted, a bill when it finishes with a cost that depends on duration and priority, and "no capacity" as a first-class outcome. The same two strategies, "pack the fullest rack" for compaction and "nearest free slot" for latency, plug into one interface. The design you draw for a parking lot is the design you present for that scheduler.

## Practice Loop

1. Write the alignment answers and fourteen requirements for a parking lot without looking, mark the MVP, and compare with the table above.
2. Underline the nouns in your list and sort them into classes, enums and attributes. Draw the diagram in a `text` fence, marking composition and reference.
3. Add a third spot strategy, "prefer the floor closest to the exit gate", as a new class without editing the others.
4. Add a weekend `FeeStrategy` with two hourly slabs, and a small factory that picks weekday or weekend by exit time.
5. Run the DDL against SQLite, add sample rows, and write the query that finds the best floor for a car under `LeastAvailableFloorStrategy`.
6. Say aloud, in two minutes, how the design behaves when two gates race for the last spot.

## Evidence of Understanding

- I can separate MVP from version 2 and justify each item I deferred.
- I can derive the entities, enums and relationships from the requirements by noun and verb spotting.
- I can explain composition versus reference in this diagram.
- I can name the two strategies and the Builder, and say which requirement drove each, and why there is no Singleton.
- I can convert the diagram to tables with foreign keys on the "many" side and constrained enums.
- I can explain why dataclass `==` can mislead when comparing spots.
- I can describe the concurrency risk with two gates before it is coded.

## Interview Questions to Rehearse

### Q: How do you start a parking lot design?

I align on scope (interactive command line, in-memory, no GUI), then propose requirements outside to inside: gates, floors, spots by vehicle type, ticket at entry, bill and payment at exit. I mark lift-based parking, emergency routes, bookings and value-added services as version 2 and list the fee inputs that will vary. Then I draw the diagram and name the patterns.

### Q: Where would you use patterns, and where not?

Strategy for spot assignment and for fee calculation, because both policies will change. A Builder for the lot, to validate floors, gates and spot numbers together. A small Factory to choose a fee strategy from the exit time. I would not use a Singleton for the lot: it hides a dependency and breaks tests, and a deployment can have several lots.

### Q: How do you model the bill and payments?

A bill belongs to one ticket and records the exit gate, exit time and amount. A payment belongs to a bill and has an amount, mode, status and reference. Because a bill can have several payments, the service sums successful payments and compares with the bill amount, which supports split payments and retries after a failure.

### Q: Why composition for floors and spots but references for tickets?

Floors and spots do not exist without the lot, so the lot owns their lifecycle. A ticket points at a vehicle, a spot and a gate that exist independently and outlive the ticket. Choosing the relationship decides who is responsible for creating and deleting, and where the foreign key goes in the schema.

### Q: What goes wrong when two vehicles arrive at the same time?

Both can read the same spot as available before either marks it occupied, so two tickets reference one spot. A lock around the read-and-assign step fixes it inside one process; across processes the database must enforce it, with a constraint or a row lock. A thread lock does not protect a database shared by several workers.

## Common Pitfalls

- Starting with classes before agreeing scope, then modelling lifts and emergency exits nobody asked for.
- A `Vehicle` subclass per vehicle type, when type is just a value that selects a spot and a fee.
- Putting the fee rules inside `Ticket` or `ParkingLot`, so every new pricing rule edits an old class.
- Comparing dataclass entities with `in` or `==` and matching the wrong object; use identity or ids.
- A Singleton lot, which makes tests share state.
- Foreign keys on the "one" side, or no uniqueness on (floor, spot number).
- Raising an exception for "no spot available" inside the strategy, so callers cannot choose their own policy.
- Truncating hours instead of rounding started hours up, so a five-minute stay costs nothing.

## Suggested Extension

Add reserved spots for an EV charging service: a new spot attribute, a new vehicle type, and a strategy that only considers spots with a charger. Decide whether this is a new `SpotAssignmentStrategy`, a filter inside an existing one, or a change to the data model, and write down one sentence on the trade-off for each option.
