# Design BookMyShow

A movie-ticket booking system looks like the parking lot with prettier posters: a tree of physical things (city, theatre, screen, seat) and a flow of transactions on top (show, booking, payment). The twist that makes it a favourite interview problem is that the interesting data does not live on the physical objects. The price and the availability of a seat belong to a **show**, and two users must never hold the same seat of the same show. This lesson designs the system, and the next three build it with SQLAlchemy.

## Concepts Covered

### Align, then gather requirements

Alignment for this problem: an online movie-ticket booking system, persisted (a real database, since bookings must survive restarts), driven from the command line for the MVP. Gather requirements outside to inside, structure first and user journey second, and generic before specific.

| # | Requirement | Scope |
|---|---|---|
| 1 | A user can book movie tickets | MVP |
| 2 | Multiple regions (cities); a region has many theatres | MVP |
| 3 | A theatre has many screens; a screen has many seats | MVP |
| 4 | Screens have types (2D, 3D, IMAX) | MVP |
| 5 | A theatre plays different movies | MVP |
| 6 | A user books seats in a **show** (movie, theatre, screen, date and time) | MVP |
| 7 | Seats have types (silver, gold, platinum) and the user picks the type | MVP |
| 8 | No two people can book the same seat of the same show | MVP, the hard part |
| 9 | Price depends on the show and the seat type | MVP |
| 10 | Online payment only | MVP |
| 11 | A user can see their bookings | MVP |
| 12 | Cancel a booking, search, filter, discounts, reviews, upcoming movies, gift cards, food orders | Version 2 |

Name the version-2 list out loud; it shows scope control and lets you point at seams. Non-movie events are ignored for simplicity.

### Entities by noun spotting

The structural nouns form a tree, exactly like `ParkingLot`, `ParkingFloor`, `ParkingSpot`: `Region` has `Theatre`s, a theatre has `Screen`s, a screen has `Seat`s. `Movie` carries name, genre, language and cast. A `Show` ties a movie to a screen at a time. The transactional nouns are `User`, `Booking` and `Payment`. Enums cover seat type, screen type, show-seat status, booking status and payment status.

```text
Region 1 <>--- * Theatre 1 <>--- * Screen (ScreenType) 1 <>--- * Seat (row, col, SeatType)
Movie (name, genre, language)
Show (movie, screen, start_time) 1 ---- * ShowSeatType (show, seat_type, price)
                                 1 ---- * ShowSeat     (show, seat, status)
User 1 ---- * Booking (user, show, show_seats, status, amount) 1 ---- * Payment (amount, mode, status, ref)
```

### The key insight: where do price and availability live?

The obvious design puts `price` on `SeatType` and a `status` on `Seat`. Both are wrong, and spotting why is the heart of this question. A seat type does not have one price: gold costs 250 at 10 am and 400 at 8 pm, so price is a function of **(show, seat type)**. A seat is not "booked" in general: the same physical seat is free for the 10 am show and sold for the 8 pm one, so status is a function of **(show, seat)**. Each function becomes its own entity: `ShowSeatType` and `ShowSeat`.

The cost is more rows, and it is worth sizing aloud. With three seat types and a 500-seat screen, one show needs 3 `ShowSeatType` rows for prices but 500 `ShowSeat` rows for availability. Putting the price on every `ShowSeat` would repeat it 500 times and make a price change a 500-row update; keeping `ShowSeatType` separate stores each price once.

### Pseudo-code for the user journey

A user picks a region, then a theatre or a movie, then a show, selects seats, and a booking and payment follow. In terms of states the booking is `PENDING` while the seats are held for payment, becomes `CONFIRMED` when the payment succeeds, `EXPIRED` if the hold times out, and `CANCELLED` if the user cancels a confirmed booking. Only those transitions are legal, and encoding them in one place prevents an expired booking from being confirmed later.

### Skeleton: models

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SeatType(Enum):
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class ScreenType(Enum):
    TWO_D = "2d"
    THREE_D = "3d"
    IMAX = "imax"


class ShowSeatStatus(Enum):
    AVAILABLE = "available"
    LOCKED = "locked"          # held while the user pays, released on expiry
    BOOKED = "booked"


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass(eq=False)
class Seat:
    """A physical seat. It knows where it is and what kind it is, nothing about any show."""

    row: str
    column: int
    seat_type: SeatType


@dataclass(eq=False)
class Screen:
    name: str
    screen_type: ScreenType
    seats: list[Seat] = field(default_factory=list)


@dataclass(eq=False)
class Theatre:
    name: str
    address: str
    screens: list[Screen] = field(default_factory=list)


@dataclass(eq=False)
class Region:
    name: str
    theatres: list[Theatre] = field(default_factory=list)


@dataclass(eq=False)
class Movie:
    name: str
    genre: str
    language: str


@dataclass(eq=False)
class Show:
    movie: Movie
    screen: Screen
    start_time: datetime


@dataclass(eq=False)
class ShowSeatType:
    """Price is a function of (show, seat type): the same seat type costs more at 8 pm than at 10 am."""

    show: Show
    seat_type: SeatType
    price: int


@dataclass(eq=False)
class ShowSeat:
    """Availability is a function of (show, seat): the same seat is free for one show and sold for the next."""

    show: Show
    seat: Seat
    status: ShowSeatStatus = ShowSeatStatus.AVAILABLE


@dataclass(eq=False)
class User:
    name: str
    email: str


class InvalidTransitionError(Exception):
    pass


class MissingPriceError(Exception):
    pass
```

### Pricing and the booking state machine

The price of a booking is the sum, over the chosen seats, of the price of that seat's type **for that show**; a missing price is a named error, not a silent zero. The booking owns its transition table.

```python
_ALLOWED = {
    BookingStatus.PENDING: {BookingStatus.CONFIRMED, BookingStatus.CANCELLED, BookingStatus.EXPIRED},
    BookingStatus.CONFIRMED: {BookingStatus.CANCELLED},
    BookingStatus.CANCELLED: set(),
    BookingStatus.EXPIRED: set(),
}


@dataclass(eq=False)
class Booking:
    user: User
    show: Show
    show_seats: list[ShowSeat]
    status: BookingStatus = BookingStatus.PENDING

    def transition(self, new_status: BookingStatus) -> None:
        if new_status not in _ALLOWED[self.status]:
            raise InvalidTransitionError(f"{self.status.name} -> {new_status.name}")
        self.status = new_status


def total_amount(show: Show, show_seats: list[ShowSeat], prices: list[ShowSeatType]) -> int:
    """Sum the price of each chosen seat's type for THIS show."""
    by_type = {p.seat_type: p.price for p in prices if p.show is show}
    try:
        return sum(by_type[ss.seat.seat_type] for ss in show_seats)
    except KeyError as exc:
        raise MissingPriceError(f"no price for {exc.args[0].name} at this show") from None
```

```python
screen = Screen("Audi 1", ScreenType.IMAX, [Seat("A", 1, SeatType.GOLD), Seat("A", 2, SeatType.GOLD),
                                           Seat("B", 1, SeatType.SILVER)])
movie = Movie("Dune", "sci-fi", "en")
morning = Show(movie, screen, datetime(2026, 3, 1, 10, 0))
evening = Show(movie, screen, datetime(2026, 3, 1, 20, 0))
prices = [ShowSeatType(morning, SeatType.GOLD, 250), ShowSeatType(morning, SeatType.SILVER, 150),
          ShowSeatType(evening, SeatType.GOLD, 400), ShowSeatType(evening, SeatType.SILVER, 250)]

# one ShowSeat per (show, seat): independent availability for the same physical seat
morning_seats = [ShowSeat(morning, s) for s in screen.seats]
evening_seats = [ShowSeat(evening, s) for s in screen.seats]
morning_seats[0].status = ShowSeatStatus.BOOKED

print(total_amount(morning, morning_seats[:2], prices), total_amount(evening, evening_seats[:2], prices))
print(morning_seats[0].status.name, evening_seats[0].status.name, morning_seats[0].seat is evening_seats[0].seat)

booking = Booking(User("Asha", "asha@example.com"), evening, evening_seats[:2])
booking.transition(BookingStatus.CONFIRMED)
try:
    booking.transition(BookingStatus.EXPIRED)
except InvalidTransitionError as exc:
    print("rejected:", exc)
```

```text
500 800
BOOKED AVAILABLE True
rejected: CONFIRMED -> EXPIRED
```

The same two gold seats cost 500 in the morning and 800 in the evening; booking the first morning seat leaves the same physical seat available for the evening show, and an illegal state change is rejected.

```python
import pytest


def test_same_seat_type_has_a_different_price_per_show() -> None:
    assert total_amount(morning, morning_seats[:2], prices) == 500
    assert total_amount(evening, evening_seats[:2], prices) == 800


def test_availability_is_per_show_not_per_seat() -> None:
    assert morning_seats[0].status is ShowSeatStatus.BOOKED
    assert evening_seats[0].status is ShowSeatStatus.AVAILABLE
    assert morning_seats[0].seat is evening_seats[0].seat


def test_missing_price_is_a_named_error() -> None:
    with pytest.raises(MissingPriceError):
        total_amount(morning, [ShowSeat(morning, Seat("Z", 1, SeatType.PLATINUM))], prices)


def test_booking_state_machine_allows_only_legal_moves() -> None:
    booking = Booking(User("A", "a@x"), morning, morning_seats[1:2])
    booking.transition(BookingStatus.CONFIRMED)
    booking.transition(BookingStatus.CANCELLED)
    with pytest.raises(InvalidTransitionError):
        booking.transition(BookingStatus.CONFIRMED)
    pending = Booking(User("B", "b@x"), morning, [])
    pending.transition(BookingStatus.EXPIRED)
    assert pending.status is BookingStatus.EXPIRED
```

All four tests pass against the code above.

### The concurrency requirement is a design requirement

"No two people can book the same seat of a show" must be designed now, not patched later. Two users who select the same seat at the same time will both read it as available. The design has three parts. First, **seat status is per show**, so contention is limited to one (show, seat) pair, not the whole theatre. Second, selecting seats **locks** them with an expiry, because payment takes time: the status moves from `AVAILABLE` to `LOCKED` for, say, ten minutes, and to `BOOKED` on payment, with an expiry job returning abandoned locks to `AVAILABLE`. Third, the guarantee comes from the **database**, not from a Python lock, because the API will run on several processes; the later lessons implement transactions, isolation levels and `SELECT ... FOR UPDATE`.

### Schema design

Convert mechanically: each class becomes a table, primitives become columns, and relationships become foreign keys on the "many" side. The constraints carry the rules. `UNIQUE (show_id, seat_id)` guarantees one availability row per show and seat; `UNIQUE (show_id, seat_type)` one price per show and seat type; `CHECK` constraints keep the enums valid.

```sql
CREATE TABLE shows (id INTEGER PRIMARY KEY, movie TEXT NOT NULL, start_time TEXT NOT NULL);
CREATE TABLE seats (
    id        INTEGER PRIMARY KEY,
    row_label TEXT NOT NULL,
    col       INTEGER NOT NULL,
    seat_type TEXT NOT NULL CHECK (seat_type IN ('SILVER', 'GOLD', 'PLATINUM'))
);
CREATE TABLE show_seat_types (
    id        INTEGER PRIMARY KEY,
    show_id   INTEGER NOT NULL REFERENCES shows(id),
    seat_type TEXT NOT NULL,
    price     INTEGER NOT NULL CHECK (price > 0),
    UNIQUE (show_id, seat_type)
);
CREATE TABLE show_seats (
    id       INTEGER PRIMARY KEY,
    show_id  INTEGER NOT NULL REFERENCES shows(id),
    seat_id  INTEGER NOT NULL REFERENCES seats(id),
    status   TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'LOCKED', 'BOOKED')),
    held_by  INTEGER,
    UNIQUE (show_id, seat_id)
);
```

An all-or-nothing claim is one conditional `UPDATE`: lock every requested seat that is still available, then compare the number of rows changed with the number requested. If any seat was already taken the counts differ and the whole attempt is rolled back.

```python
import sqlite3
from pathlib import Path


def claim(con: sqlite3.Connection, show_id: int, seat_ids: list[int], user_id: int) -> bool:
    """All-or-nothing: lock every seat in one statement, or none of them."""
    marks = ",".join("?" * len(seat_ids))
    cur = con.execute(
        f"UPDATE show_seats SET status = 'LOCKED', held_by = ? "
        f"WHERE show_id = ? AND seat_id IN ({marks}) AND status = 'AVAILABLE'",
        (user_id, show_id, *seat_ids),
    )
    if cur.rowcount != len(seat_ids):          # someone else already holds at least one seat
        con.rollback()
        return False
    con.commit()
    return True
```

```python
con = sqlite3.connect(":memory:")
con.execute("PRAGMA foreign_keys = ON")
SCHEMA = Path("schema.sql").read_text()          # the DDL above, saved to a file
con.executescript(SCHEMA)
con.execute("INSERT INTO shows VALUES (1, 'Dune', '2026-03-01 20:00')")
con.executemany("INSERT INTO seats VALUES (?, ?, ?, ?)", [(1, "A", 1, "GOLD"), (2, "A", 2, "GOLD"), (3, "A", 3, "GOLD")])
con.executemany("INSERT INTO show_seats (show_id, seat_id) VALUES (1, ?)", [(1,), (2,), (3,)])
con.commit()

print(claim(con, 1, [1, 2], user_id=101))      # first user gets seats 1 and 2
print(claim(con, 1, [2, 3], user_id=202))      # overlaps on seat 2: all or nothing
print(con.execute("SELECT seat_id, status, held_by FROM show_seats ORDER BY seat_id").fetchall())
try:
    con.execute("INSERT INTO show_seats (show_id, seat_id) VALUES (1, 1)")
except sqlite3.IntegrityError as exc:
    print("rejected:", exc)
```

```text
True
False
[(1, 'LOCKED', 101), (2, 'LOCKED', 101), (3, 'AVAILABLE', None)]
rejected: UNIQUE constraint failed: show_seats.show_id, show_seats.seat_id
```

I ran this against SQLite: the first user locks seats 1 and 2; the second asks for 2 and 3, fails because seat 2 is held, and seat 3 correctly stays available (all or nothing); and a duplicate show-seat row is rejected by the unique constraint. The key point is that the decision is made by the database inside a single statement, with no read-then-write gap.

## Practical Backend Scenario

A GPU-hours marketplace sells time slots on shared clusters. A slot on a given date has a price that varies by instance class, and a customer may hold a set of slots for ten minutes while their card is charged. The structure is BookMyShow in disguise: `Cluster`, `Node` and `Slot` are the physical tree, a `Reservation` window is the show, price is a function of (window, instance class), and availability is a function of (window, slot). The same design mistake appears there too: if you store "is_free" on the physical slot, two overlapping reservation windows corrupt each other.

## Practice Loop

1. Write the requirements table from memory, mark the MVP, and list five version-2 features without looking.
2. Draw the class diagram in a `text` fence, then underline the two relationships that carry price and availability, and write one sentence on why each is not an attribute of `Seat`.
3. Extend the Python skeleton with a `Payment` model and a `ConfirmBooking` helper that moves a booking to `CONFIRMED` and every seat to `BOOKED`; test the illegal transitions.
4. Create the SQLite schema, load two shows for the same screen, and show that booking a seat in one show leaves it available in the other.
5. Run `claim` from two Python threads on separate connections and observe that exactly one claim of an overlapping seat wins.
6. Write a two-minute spoken answer: "How do you stop two users booking the same seat?", covering lock with expiry, per-show status and the database guarantee.

## Evidence of Understanding

- I can separate the MVP from version 2 and justify the cut.
- I can explain why price depends on (show, seat type) and availability on (show, seat), and name the two entities that result.
- I can estimate the row counts for a 500-seat show and justify keeping `ShowSeatType` separate.
- I can list the booking states and the legal transitions.
- I can describe the lock-with-expiry flow and say why the guarantee belongs in the database.
- I can explain the all-or-nothing `UPDATE` with a row-count check.
- I can name the unique constraints that encode the business rules.

## Interview Questions to Rehearse

### Q: Why not store the price on the seat type?

Because a seat type does not have one price. The same gold seat costs more for an evening show than a morning one, and for a premiere. Price is a function of the show and the seat type, so it gets its own entity, `ShowSeatType`, with one row per show and seat type. That also means a price change is a single row, not 500.

### Q: Why is seat availability not a field on `Seat`?

A `Seat` is a physical object that exists for every show on that screen. Whether it is free depends on the show: free for 10 am, sold for 8 pm. Availability is a function of (show, seat), so it lives in `ShowSeat`. A field on `Seat` would make a booking for one show block every other show.

### Q: How do you prevent double booking?

I make seat state per show and lock the chosen seats before payment, with an expiry so abandoned selections release themselves. The lock must be acquired atomically in the database, for example a conditional update that changes only `AVAILABLE` seats and a check that all requested seats changed, plus a unique constraint as the last line of defence. A Python lock is not enough, because several processes serve requests.

### Q: What happens if payment takes longer than the hold?

The booking has moved to `EXPIRED` and the seats are available again. When the late payment arrives it must not confirm the booking; the state machine rejects `EXPIRED` to `CONFIRMED`, and the system refunds or offers to rebook. This is why the transition table lives in one place.

### Q: How would you search by city and language?

Join region to theatres to screens to shows to movies, filter on region and movie language, and index the foreign keys and the show start time. I would also denormalise nothing at first; the search is a version-two feature, and the schema above supports it with indexed foreign keys.

## Common Pitfalls

- Putting `price` on `SeatType` or `status` on `Seat`, which makes one show affect another.
- Forgetting the lock expiry, so abandoned selections block seats forever.
- Relying on a Python `threading.Lock` for double-booking in a multi-process deployment.
- Checking availability in one query and updating in another, with no atomic step in between.
- No `UNIQUE (show_id, seat_id)`, so a bug creates two availability rows for one seat.
- Letting booking status be set to any value instead of a transition table.
- Modelling the movie as part of the show, so a movie's name and language are copied into every show.
- Forgetting to ask whether non-movie events and cancellations are in scope.

## Suggested Extension

Add cancellation as version 2: a confirmed booking can be cancelled up to two hours before the show, its seats return to `AVAILABLE`, and the payment is refunded. Decide where the two-hour rule lives, write the new transition and the schema change (a `cancelled_at` column and a refund row), and describe what must be atomic.
