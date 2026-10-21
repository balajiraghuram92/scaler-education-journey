# Code Parking Lot 1: Layers, Models and Ticket Issuance

Once the diagram for the parking lot is agreed, the machine-coding round becomes an exercise in structure: where does each line of code live, and can it be tested and changed without touching the rest? Interviewers read the layout before they read the logic. A clean controller, service and repository stack with DTOs, a generic repository, and a strategy for slot allocation tells them in thirty seconds that you can build systems that grow. This lesson codes the first feature, **issuing a ticket**, in exactly that shape.

## Concepts Covered

### One job per layer

Every layer has a single reason to change, and the rules about who may touch what are strict enough to be checked in a code review.

| Layer | Job | May touch | Must not |
|---|---|---|---|
| Models | Data and identity | nothing | contain I/O or orchestration |
| Repository | Save and find | models | decide anything, assign spots, validate gates |
| Service | Business rules | models, repositories, strategies | import or return DTOs |
| Controller | Unwrap request DTO, call service, wrap response DTO | service, DTOs | contain business logic or touch repositories |
| DTOs | The shape of the outside conversation | primitives | leak domain objects outward |

A reception desk is a fair picture of the controller: it takes the request, hands it to the people who do the work, and returns the answer, without cooking or cleaning itself. The rule most often broken in interviews is the second one on the service row: a service method that takes `IssueTicketRequestDTO` ties business rules to one transport format, so a CLI, a test or a batch job cannot call it without building a DTO. Services take plain values: `issue_ticket(gate_id, vehicle_number, vehicle_type, owner_name)`.

### Models with identity and audit fields

Every persisted entity needs an id and timestamps, so they live in a `BaseModel`. Two details matter. `@dataclass(kw_only=True)` on the base makes its defaulted fields keyword-only (Python 3.10+), so subclasses can declare required fields without the "non-default argument follows default argument" error. And the models use `eq=False`: entities are compared by identity or by id, never by field values, because two different spots with the same number and status would otherwise be `==`, which is a trap when you search lists. A spot supports a **set** of vehicle types because one large spot can host a bike, a car or a truck, and that is also what makes concurrency interesting later.

```python
from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(kw_only=True, eq=False)
class BaseModel:
    """Identity and audit fields shared by every persisted entity."""

    id: int | None = None
    created_at: datetime | None = None
    last_modified_at: datetime | None = None


@dataclass(eq=False)
class Gate(BaseModel):
    name: str
    gate_type: GateType


@dataclass(eq=False)
class ParkingSpot(BaseModel):
    number: int
    supported_vehicle_types: frozenset[VehicleType]     # one big spot can take a bike, a car or a truck
    status: SpotStatus = SpotStatus.AVAILABLE


@dataclass(eq=False)
class Vehicle(BaseModel):
    number: str
    vehicle_type: VehicleType
    owner_name: str


@dataclass(eq=False)
class Ticket(BaseModel):
    ticket_number: str
    entry_time: datetime
    vehicle: Vehicle
    spot: ParkingSpot
    gate: Gate


class ParkingLotError(Exception):
    """Base class for every domain failure the controller translates."""


class InvalidGateError(ParkingLotError):
    pass


class ParkingFullError(ParkingLotError):
    pass
```

A single base class `ParkingLotError` lets the controller catch every expected failure in one clause without swallowing programming errors such as `TypeError`.

### A generic repository, written once

Saving and finding do the same thing for every model, so one `InMemoryRepository[T]` serves all of them, and concrete repositories inherit from it and add only their special queries. Three points deserve a sentence each. `TypeVar("T", bound=BaseModel)` documents that the element needs an `id`, but the bound is checked by mypy or pyright, **not** by the interpreter: a repository of a plain class compiles and fails at runtime with `AttributeError` on the first `item.id`. Storing items in a dictionary keyed by id means saving the same object twice updates it; a version that appends to a list adds a duplicate on every update. And injecting the clock keeps timestamps deterministic in tests. On Python 3.12 and later the generic can be declared as `class InMemoryRepository[T: BaseModel]`, without `Generic` or `TypeVar`.

```python
from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T", bound=BaseModel)      # on 3.12+ you can write: class InMemoryRepository[T: BaseModel]


class InMemoryRepository(Generic[T]):
    """Written once: save and find do the same thing for every model type."""

    def __init__(self, clock: Callable[[], datetime] = datetime.now) -> None:
        self._items: dict[int, T] = {}
        self._next_id = 1
        self._clock = clock

    def save(self, item: T) -> T:
        now = self._clock()
        if item.id is None:
            item.id = self._next_id
            self._next_id += 1
            item.created_at = now
        item.last_modified_at = now
        self._items[item.id] = item            # keyed by id: saving twice updates, never duplicates
        return item

    def find_by_id(self, item_id: int) -> T | None:
        return self._items.get(item_id)

    def find_all(self) -> list[T]:
        return list(self._items.values())


class GateRepository(InMemoryRepository[Gate]):
    pass


class ParkingSpotRepository(InMemoryRepository[ParkingSpot]):
    pass


class TicketRepository(InMemoryRepository[Ticket]):
    pass


class VehicleRepository(InMemoryRepository[Vehicle]):
    def find_by_number(self, number: str) -> Vehicle | None:
        return next((v for v in self._items.values() if v.number == number), None)
```

### Strategy for slot allocation, and the service

The slot-allocation policy is a Strategy from the start: given the spots and the vehicle type, return a spot or `None`. `FirstAvailableSpotStrategy` is enough for the first feature; a nearest-to-exit or least-full-floor policy is a new class later. Returning `None` instead of raising keeps the strategy free of policy.

The service then does the work in a deliberate order: validate the gate; ask the strategy for a spot; only if one exists, find or create the vehicle; mark the spot occupied; save the ticket. Validation first, mutation last means a failure (a full lot, an exit gate) leaves no partial state, which a test asserts. The ticket number and the clock are injected so tests are deterministic. The service is allowed to raise domain errors but never touches a DTO.

```python
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence


class SpotAllotmentStrategy(ABC):
    @abstractmethod
    def find_spot(self, spots: Sequence[ParkingSpot], vehicle_type: VehicleType) -> ParkingSpot | None: ...


class FirstAvailableSpotStrategy(SpotAllotmentStrategy):
    def find_spot(self, spots: Sequence[ParkingSpot], vehicle_type: VehicleType) -> ParkingSpot | None:
        return next((s for s in spots
                     if s.status is SpotStatus.AVAILABLE and vehicle_type in s.supported_vehicle_types), None)


class TicketService:
    """Business rules only. Plain values in, a model out: it never sees a DTO."""

    def __init__(self, gates: GateRepository, spots: ParkingSpotRepository, vehicles: VehicleRepository,
                 tickets: TicketRepository, strategy: SpotAllotmentStrategy,
                 clock: Callable[[], datetime] = datetime.now,
                 new_number: Callable[[], str] = lambda: str(uuid.uuid4())) -> None:
        self._gates, self._spots, self._vehicles = gates, spots, vehicles
        self._tickets, self._strategy = tickets, strategy
        self._clock, self._new_number = clock, new_number

    def issue_ticket(self, gate_id: int, vehicle_number: str, vehicle_type: VehicleType,
                     owner_name: str) -> Ticket:
        gate = self._gates.find_by_id(gate_id)
        if gate is None or gate.gate_type is not GateType.ENTRY:
            raise InvalidGateError(f"gate {gate_id} cannot issue tickets")
        spot = self._strategy.find_spot(self._spots.find_all(), vehicle_type)
        if spot is None:
            raise ParkingFullError(f"no spot for a {vehicle_type.value}")
        vehicle = self._vehicles.find_by_number(vehicle_number) or self._vehicles.save(
            Vehicle(number=vehicle_number, vehicle_type=vehicle_type, owner_name=owner_name))
        spot.status = SpotStatus.OCCUPIED
        self._spots.save(spot)
        return self._tickets.save(Ticket(ticket_number=self._new_number(), entry_time=self._clock(),
                                         vehicle=vehicle, spot=spot, gate=gate))
```

### Controller and DTOs

The controller converts the outside world to values the service understands (the text `"car"` becomes `VehicleType.CAR`), calls the service, and wraps the outcome. It catches `KeyError` for an unknown type and `ParkingLotError` for domain failures, and nothing else, so a real bug still surfaces. DTOs are frozen dataclasses with plain fields; the response carries the ticket number and spot number, not the ticket object.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class IssueTicketRequestDTO:
    gate_id: int
    vehicle_number: str
    vehicle_type: str          # arrives as text from the outside world
    owner_name: str


@dataclass(frozen=True)
class IssueTicketResponseDTO:
    success: bool
    ticket_number: str | None = None
    spot_number: int | None = None
    message: str = ""


class TicketController:
    """Unwrap the request DTO, call the service, wrap the response DTO. No rules here."""

    def __init__(self, service: TicketService) -> None:
        self._service = service

    def issue_ticket(self, request: IssueTicketRequestDTO) -> IssueTicketResponseDTO:
        try:
            vehicle_type = VehicleType[request.vehicle_type.upper()]
            ticket = self._service.issue_ticket(
                request.gate_id, request.vehicle_number, vehicle_type, request.owner_name)
        except KeyError:
            return IssueTicketResponseDTO(False, message=f"unknown vehicle type: {request.vehicle_type}")
        except ParkingLotError as exc:
            return IssueTicketResponseDTO(False, message=str(exc))
        return IssueTicketResponseDTO(True, ticket.ticket_number, ticket.spot.number)
```

### Wiring it together

The only place that knows which concrete classes are used is the composition root, here the top of a script. Replace `GateRepository` with a database-backed one and nothing above it changes.

```python
# composition root: the only place that knows which concrete classes are used
gates, spots, vehicles, tickets = GateRepository(), ParkingSpotRepository(), VehicleRepository(), TicketRepository()
entry = gates.save(Gate(name="North", gate_type=GateType.ENTRY))
exit_gate = gates.save(Gate(name="South", gate_type=GateType.EXIT))
spots.save(ParkingSpot(number=1, supported_vehicle_types=frozenset({VehicleType.BIKE})))
spots.save(ParkingSpot(number=2, supported_vehicle_types=frozenset({VehicleType.CAR, VehicleType.BIKE})))

controller = TicketController(TicketService(gates, spots, vehicles, tickets, FirstAvailableSpotStrategy(),
                                            new_number=iter(["T-1", "T-2", "T-3"]).__next__))

print(controller.issue_ticket(IssueTicketRequestDTO(entry.id, "KA01", "car", "Asha")))
print(controller.issue_ticket(IssueTicketRequestDTO(entry.id, "KA02", "car", "Ravi")))
print(controller.issue_ticket(IssueTicketRequestDTO(exit_gate.id, "KA03", "bike", "Meera")))
print(controller.issue_ticket(IssueTicketRequestDTO(entry.id, "KA04", "plane", "Zed")))
```

```text
IssueTicketResponseDTO(success=True, ticket_number='T-1', spot_number=2, message='')
IssueTicketResponseDTO(success=False, ticket_number=None, spot_number=None, message='no spot for a car')
IssueTicketResponseDTO(success=False, ticket_number=None, spot_number=None, message='gate 2 cannot issue tickets')
IssueTicketResponseDTO(success=False, ticket_number=None, spot_number=None, message='unknown vehicle type: plane')
```

The first car skips the bike-only spot 1 and takes spot 2; the second finds nothing; the exit gate and the unknown type are rejected at different layers.

### Tests

All five pass against the code above and need no database and no mocks.

```python
import pytest


def build(spot_types, new_numbers=("T-1", "T-2", "T-3")):
    gates, spots, vehicles, tickets = GateRepository(), ParkingSpotRepository(), VehicleRepository(), TicketRepository()
    entry = gates.save(Gate(name="N", gate_type=GateType.ENTRY))
    exit_gate = gates.save(Gate(name="S", gate_type=GateType.EXIT))
    for number, kinds in enumerate(spot_types, start=1):
        spots.save(ParkingSpot(number=number, supported_vehicle_types=frozenset(kinds)))
    service = TicketService(gates, spots, vehicles, tickets, FirstAvailableSpotStrategy(),
                            new_number=iter(new_numbers).__next__)
    return service, entry, exit_gate, spots, vehicles


def test_issue_marks_the_spot_occupied_and_reuses_a_known_vehicle() -> None:
    service, entry, _, spots, vehicles = build([{VehicleType.CAR}, {VehicleType.CAR}])
    first = service.issue_ticket(entry.id, "KA01", VehicleType.CAR, "Asha")
    assert first.spot.status is SpotStatus.OCCUPIED and first.spot.number == 1
    service.issue_ticket(entry.id, "KA01", VehicleType.CAR, "Asha")
    assert len(vehicles.find_all()) == 1


def test_exit_gate_and_unknown_gate_cannot_issue() -> None:
    service, entry, exit_gate, _, _ = build([{VehicleType.CAR}])
    with pytest.raises(InvalidGateError):
        service.issue_ticket(exit_gate.id, "KA01", VehicleType.CAR, "Asha")
    with pytest.raises(InvalidGateError):
        service.issue_ticket(999, "KA01", VehicleType.CAR, "Asha")


def test_full_lot_raises_and_leaves_no_trace() -> None:
    service, entry, _, spots, vehicles = build([{VehicleType.BIKE}])
    with pytest.raises(ParkingFullError):
        service.issue_ticket(entry.id, "KA01", VehicleType.CAR, "Asha")
    assert vehicles.find_all() == [] and spots.find_all()[0].status is SpotStatus.AVAILABLE


def test_saving_twice_updates_instead_of_duplicating() -> None:
    repo = GateRepository()
    gate = repo.save(Gate(name="N", gate_type=GateType.ENTRY))
    first_created = gate.created_at
    gate.name = "North"
    repo.save(gate)
    assert len(repo.find_all()) == 1 and gate.created_at == first_created


def test_controller_translates_domain_errors_into_a_response() -> None:
    service, entry, exit_gate, _, _ = build([{VehicleType.CAR}])
    controller = TicketController(service)
    ok = controller.issue_ticket(IssueTicketRequestDTO(entry.id, "KA01", "car", "Asha"))
    assert ok.success and ok.ticket_number == "T-1" and ok.spot_number == 1
    bad_gate = controller.issue_ticket(IssueTicketRequestDTO(exit_gate.id, "KA02", "car", "Ravi"))
    assert not bad_gate.success and "cannot issue" in bad_gate.message
    bad_type = controller.issue_ticket(IssueTicketRequestDTO(entry.id, "KA03", "plane", "Zed"))
    assert not bad_type.success and "unknown vehicle type" in bad_type.message
```

### Inheritance in a schema

Class hierarchies reach the database too. Take pens: a ball pen and a gel pen share a name and price but differ in grip and ink. The naive schema copies the common columns into three tables, so listing every pen means querying all three and combining the results. The better schema is **joined-table inheritance**: the parent table holds the common columns, each child table holds only its own columns plus a foreign key to the parent.

```sql
-- naive: copy the common columns into every table (listing all pens needs a UNION)
-- better: the parent holds the common columns, each child holds only its own plus a foreign key
CREATE TABLE pens (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    price REAL NOT NULL,
    kind  TEXT NOT NULL CHECK (kind IN ('BALL', 'GEL'))
);
CREATE TABLE ball_pens (
    id        INTEGER PRIMARY KEY REFERENCES pens(id),
    ball_grip TEXT NOT NULL
);
CREATE TABLE gel_pens (
    id       INTEGER PRIMARY KEY REFERENCES pens(id),
    ink_type TEXT NOT NULL
);
```

I ran this DDL in SQLite with foreign keys on: `SELECT name, price FROM pens` lists every pen from one table, the join to `ball_pens` returns `[('Reynolds', 'rubber')]`, and inserting a gel-pen row for a missing parent fails with `FOREIGN KEY constraint failed`. With SQLAlchemy 2.0 the same shape is expressed with a polymorphic mapping; this sketch is standard but was not executed here.

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Pen(Base):
    __tablename__ = "pens"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float]
    kind: Mapped[str] = mapped_column(String(10))
    __mapper_args__ = {"polymorphic_on": "kind", "polymorphic_identity": "PEN"}


class BallPen(Pen):
    __tablename__ = "ball_pens"
    id: Mapped[int] = mapped_column(ForeignKey("pens.id"), primary_key=True)
    ball_grip: Mapped[str] = mapped_column(String(50))
    __mapper_args__ = {"polymorphic_identity": "BALL"}
```

### Where it will break

`issue_ticket` reads the spots, picks one, and later writes it back as occupied. Two gates can interleave between the read and the write and issue the same spot twice. The next lesson reproduces and fixes that.

## Practical Backend Scenario

An LLM gateway issues an "inference ticket" to each request: it must find a free GPU slot of a suitable class, record the caller, and return a handle, and requests may arrive on several workers. The structure is the same: a controller that unwraps an HTTP DTO, a service that takes plain values and owns the rules (validate the tenant, find a slot, mark it busy, record the ticket), a generic repository behind a protocol so tests use an in-memory fake, and a slot-allocation strategy you can swap from first-fit to best-fit. The "validate first, mutate last" ordering is what keeps a failed request from leaving a half-reserved slot.

## Practice Loop

1. Type out `BaseModel`, the models and the generic repository from memory, then write the test that saving the same object twice yields one record.
2. Break the generic repository deliberately: make `save` append to a list, and watch the duplicate test fail. Restore the dictionary.
3. Instantiate `InMemoryRepository` for a plain class with no `id` and observe the runtime error; then run a type checker, if you have one, to see the same mistake caught statically.
4. Implement `LeastAvailableFirstStrategy` (prefer the spot supporting the fewest vehicle types) as a new class, and swap it in at the composition root without editing the service.
5. Add the exit side: a `Bill` and a `BillService.create_bill(ticket_number, gate_id)` that takes plain values, with its own controller and DTOs.
6. Review your own code against the layer table and fix any place a service imports a DTO.

## Evidence of Understanding

- I can state each layer's single job and what it must not do.
- I can explain why services take plain values and not DTOs.
- I can explain what `TypeVar(bound=...)` guarantees, and what it does not at runtime.
- I can say why the repository stores items by id, and why `eq=False` matters for entities.
- I can justify the order: validate, find a spot, create the vehicle, mutate, save.
- I can describe joined-table inheritance and why it beats copying columns.
- I can identify the read-then-write window in `issue_ticket`.

## Interview Questions to Rehearse

### Q: Why do the service methods take plain values instead of DTOs?

DTOs describe one transport's request shape. If the service depends on them, every caller, whether a CLI, a test or a message consumer, must build that DTO, and a change to the wire format ripples into business logic. Plain values keep rules reusable. The controller is the single adapter: it unwraps the request, calls the service, and wraps the response.

### Q: What does the generic repository buy you, and what are its limits?

It removes duplicated save and find logic across entities and gives one place for ids and audit timestamps. Concrete repositories add only special queries. The limits: the `TypeVar` bound is a static promise, so a wrong type fails at runtime unless a type checker runs; and an in-memory store is not a database, so ordering, transactions and concurrency need their own thought.

### Q: Why is `find_spot` a strategy and not a method on the service?

Allocation policy is the likeliest thing to change: first fit, nearest to exit, least-full floor. As a strategy it can be swapped at the composition root and tested alone. Returning `None` for "no spot" lets the service choose the policy, whether to raise, queue or reject.

### Q: How do you make sure a failed ticket request leaves no side effects?

By ordering: validate everything and find the spot before creating or changing anything, so every failure happens before the first mutation, and then write. A test asserts that a full-lot failure leaves no vehicle and the spot still available. For multi-step writes in a database I would also use a transaction.

### Q: What is wrong with `items.append(item)` inside `save`?

Saving an existing object appends it again, so updates create duplicates and `find_all` returns repeated entries. Keying a dictionary by id makes save an upsert. The only time append is right is when every save is a brand-new record.

## Common Pitfalls

- A service signature that takes a DTO, or a service that returns one.
- A controller that checks gate types or touches repositories, so rules leak upward.
- A generic repository that appends to a list, so each update duplicates the entity.
- Trusting `TypeVar(bound=...)` at runtime, then being surprised by an `AttributeError`.
- `@dataclass` entities with default equality, so `spot in spots` matches the wrong spot.
- Mutating the spot before checking everything else, leaving it occupied when the ticket fails.
- Catching bare `Exception` in the controller, which hides bugs as failed requests.
- Copying common columns into every subclass table instead of using a parent table.

## Suggested Extension

Add a `ParkingFloor` model and make `FirstAvailableSpotStrategy` respect floor status. Then write `SqlAlchemy`-style repositories behind the same interface without changing the service, keeping the in-memory ones for tests, and decide which tests move to the database and which stay on the fake, justifying the split in two sentences.
