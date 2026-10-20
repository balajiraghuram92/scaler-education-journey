# Code BookMyShow 1: SQLAlchemy Models and Relationships

A ticketing system is mostly a schema: if the tables cannot express "this seat is sold for this show at this price", no amount of clever service code will save you later. This lesson turns the BookMyShow class diagram into SQLAlchemy 2.0 models, and every decision here (where status lives, what is an enum, what is a lookup table) comes back as a bug or a rewrite in the next two lessons. In an interview, the schema you draw in the first ten minutes is what the interviewer attacks for the remaining thirty.

## Concepts Covered

### A typed declarative base and an abstract BaseModel

SQLAlchemy 2.0 replaces `declarative_base()` and `Column(...)` with a `DeclarativeBase` subclass and annotated attributes. `Mapped[T]` carries the Python type and nullability (`Mapped[str | None]` is nullable), while `mapped_column()` carries the database details. Every table in this project shares an `id` and two audit timestamps, so they live on an abstract base.

`__abstract__ = True` tells the mapper "this class contributes columns to its subclasses but gets no table of its own". Without it SQLAlchemy complains that the class has no `__tablename__` or `__table__`. A plain mixin class (no `Base` ancestor) also works, but note one trap: a mixin or abstract base that declares a **foreign key** or **relationship** must wrap it in `declared_attr`, because each subclass needs its own copy of that object.

```python
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
```

Pass the **function** `utc_now`, never `utc_now()`. The next lesson shows why. An integer primary key on a fresh table is auto-incrementing, so two objects added in one session and committed get ids `1` and `2` (on a brand-new table, in insertion order).

### Foreign keys, relationships and back_populates

A `ForeignKey` is a database fact: the `theatres.region_id` column must hold an existing `regions.id`. A `relationship()` is an ORM convenience: it lets you write `theatre.region` and `region.theatres` instead of joining by hand. The two are separate, and you need both.

`back_populates` links the two halves of one relationship so they stay in sync **in memory**. Without it, `theatre.region = bangalore` sets the foreign key correctly on flush, but `bangalore.theatres` will not show the new theatre until it is expired and reloaded. Each side names the other's attribute.

```python
from sqlalchemy import ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Region(BaseModel):
    __tablename__ = "regions"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    theatres: Mapped[list["Theatre"]] = relationship(back_populates="region")


class Theatre(BaseModel):
    __tablename__ = "theatres"

    name: Mapped[str] = mapped_column(String(120))
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"))
    region: Mapped["Region"] = relationship(back_populates="theatres")
    screens: Mapped[list["Screen"]] = relationship(back_populates="theatre")


class Screen(BaseModel):
    __tablename__ = "screens"

    name: Mapped[str] = mapped_column(String(60))
    theatre_id: Mapped[int] = mapped_column(ForeignKey("theatres.id"))
    # What the hardware can do: {"3D", "DOLBY_AUDIO"}. Not what is playing today.
    features: Mapped[list[str]] = mapped_column(JSON, default=list)
    theatre: Mapped["Theatre"] = relationship(back_populates="screens")
    seats: Mapped[list["Seat"]] = relationship(back_populates="screen")
```

The foreign key lives on the **many** side (`Theatre.region_id`), and the `Mapped[list[...]]` annotation marks the collection side. Watch for copy-paste damage: `Region` must not have a `region` field. The parent never points up.

> **Pitfall:** `JSON` columns are not mutation-tracked. `screen.features.append("3D")` changes nothing the ORM can see. Reassign a new list, or wrap the column in `MutableList.as_mutable(JSON)`.

### Lookup table or enum?

Ask one question: can this set of values change without a code release, or differ per owner? `BookingStatus` (`PENDING`, `CONFIRMED`, `CANCELLED`, `EXPIRED`) drives branching code, so it is an enum. `SeatType` (`SILVER`, `GOLD`, `PLATINUM`) is configurable per theatre chain and carries a price, so it is a table that other tables reference by foreign key. Renaming "GOLD" to "Premium Gold" then touches one row instead of every seat.

By default SQLAlchemy stores an enum by its **member name** (`"CONFIRMED"`), not the value and not `"BookingStatus.CONFIRMED"`. That makes a rename a data migration: an old row holding `PAYMENT` fails to load after the member becomes `SETTLEMENT`.

```python
import enum

from sqlalchemy import Enum as SAEnum


class BookingStatus(enum.Enum):
    PENDING = enum.auto()
    CONFIRMED = enum.auto()
    CANCELLED = enum.auto()
    EXPIRED = enum.auto()


class Booking(BaseModel):
    __tablename__ = "bookings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, native_enum=False, length=16),
        default=BookingStatus.PENDING,
    )
```

Import SQLAlchemy's `Enum` under an alias. `from enum import Enum` followed by `from sqlalchemy import Enum` silently rebinds the name, and your "Python enum" suddenly is not one. `native_enum=False` stores a `VARCHAR` instead of a PostgreSQL `ENUM` type, which avoids `ALTER TYPE` ceremony when members are added.

### Per-show state: ShowSeat and show-level pricing

The most important modelling move in this lesson: **a seat has no status. A seat in a show has a status.** The physical `Seat` row is reused by every show on that screen, so "is C4 available?" is only meaningful as "is C4 available for the 6 PM show?". That join row is `ShowSeat`.

The same reasoning gives pricing. Price depends on the pair (show, seat type), so it lives in its own table keyed on that pair. A weekday matinee and a weekend night are different `Show` rows, so they get different prices with no code change.

The supporting entities are small. `Seat` belongs to a screen and references a seat type; `Show` ties a movie, a screen and a start time together.

```python
class SeatType(BaseModel):
    __tablename__ = "seat_types"

    name: Mapped[str] = mapped_column(String(40), unique=True)  # SILVER, GOLD...


class Seat(BaseModel):
    __tablename__ = "seats"
    __table_args__ = (UniqueConstraint("screen_id", "label", name="uq_screen_label"),)

    label: Mapped[str] = mapped_column(String(8))  # "C4"
    screen_id: Mapped[int] = mapped_column(ForeignKey("screens.id"))
    seat_type_id: Mapped[int] = mapped_column(ForeignKey("seat_types.id"))
    screen: Mapped["Screen"] = relationship(back_populates="seats")
    seat_type: Mapped["SeatType"] = relationship()


class Show(BaseModel):
    __tablename__ = "shows"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    screen_id: Mapped[int] = mapped_column(ForeignKey("screens.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    features: Mapped[list[str]] = mapped_column(JSON, default=list)  # what is running
    screen: Mapped["Screen"] = relationship()
    show_seats: Mapped[list["ShowSeat"]] = relationship(back_populates="show")
    prices: Mapped[list["ShowSeatType"]] = relationship(back_populates="show")
```

Now the per-show tables.

```python
class ShowSeatStatus(enum.Enum):
    AVAILABLE = enum.auto()
    BLOCKED = enum.auto()
    BOOKED = enum.auto()


class ShowSeat(BaseModel):
    __tablename__ = "show_seats"
    __table_args__ = (UniqueConstraint("show_id", "seat_id", name="uq_show_seat"),)

    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id"))
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"))
    status: Mapped[ShowSeatStatus] = mapped_column(
        SAEnum(ShowSeatStatus, native_enum=False, length=16),
        default=ShowSeatStatus.AVAILABLE,
    )
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    show: Mapped["Show"] = relationship(back_populates="show_seats")
    seat: Mapped["Seat"] = relationship()


class ShowSeatType(BaseModel):
    """Price of one seat type for one show."""

    __tablename__ = "show_seat_types"
    __table_args__ = (UniqueConstraint("show_id", "seat_type_id", name="uq_show_type"),)

    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id"))
    seat_type_id: Mapped[int] = mapped_column(ForeignKey("seat_types.id"))
    price: Mapped[int] = mapped_column()  # minor units (paise); never float
    show: Mapped["Show"] = relationship(back_populates="prices")
    seat_type: Mapped["SeatType"] = relationship()
```

`Show.features` (what is actually running: `["2D"]`) is a different fact from `Screen.features` (what the room supports), so both exist. The unique constraint on `(show_id, seat_id)` is the first line of defence against generating the same inventory twice, and in the next lesson it becomes a weapon against double booking.

### Booking links seats many-to-many over time

A booking covers several `ShowSeat` rows, and one `ShowSeat` can belong to different bookings over its life: booked, cancelled, then booked again by someone else. A `booking_id` column on `ShowSeat` can only hold the **current** answer and destroys history. A plain association table holds every link.

```python
from sqlalchemy import Column, Table

booking_show_seats = Table(
    "booking_show_seats",
    Base.metadata,
    Column("booking_id", ForeignKey("bookings.id"), primary_key=True),
    Column("show_seat_id", ForeignKey("show_seats.id"), primary_key=True),
)

# inside Booking:
#   show_seats: Mapped[list["ShowSeat"]] = relationship(secondary=booking_show_seats)
```

If the link needs its own attributes (price paid per seat, refund state), promote the table to a mapped class, the same move that turns Splitwise's paid/owed rows into `ExpenseUser` later.

### Registering models and querying across levels

`Base.metadata.create_all(engine)` only creates tables for classes whose module has been **imported**, because a model registers itself on `Base.metadata` when its class body runs. Import every model module in `models/__init__.py` before creating tables. In production use Alembic migrations, since `create_all` never alters an existing table.

Name tables in the plural (`users`, `shows`, `bookings`). `user` is reserved in PostgreSQL, so it fails or needs quoting there while working in MySQL.

To fetch "all shows in Bangalore", walk the chain with joins, not application loops:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload


def shows_in_region(session: Session, region_name: str) -> list["Show"]:
    stmt = (
        select(Show)
        .join(Show.screen)
        .join(Screen.theatre)
        .join(Theatre.region)
        .where(Region.name == region_name)
        .options(selectinload(Show.prices))
        .order_by(Show.starts_at)
    )
    return list(session.scalars(stmt).all())
```

`selectinload` fetches each show's prices in one extra query for the whole result, instead of one lazy-load query per show (the N+1 problem).

> **Production note:** SQLite ignores foreign keys unless you run `PRAGMA foreign_keys=ON` per connection. A test suite on in-memory SQLite can pass while PostgreSQL rejects the same insert.

## Practical Backend Scenario

You are the forward deployed engineer at a cinema chain that wants an LLM assistant answering "any 7 PM show in Bangalore with Dolby seats under 300 rupees?". The assistant calls a tool that queries your service. With status on `Seat`, the tool answers for the wrong show. With a flat price on `SeatType`, every weekend price is wrong. With region names copied onto `Show`, a renamed region breaks search. The schema from this lesson makes each question a single, indexed join, which is exactly what you want to hand a model as a tool.

## Practice Loop

1. Create `models/` with `base.py` (the `Base` and `BaseModel` above) and one module per entity. Import them all in `models/__init__.py`.
2. Point an engine at `sqlite:///:memory:` with `echo=True`, enable the foreign-key pragma on connect, and run `create_all`. Read the emitted DDL and confirm `show_seats` has the unique constraint.
3. Remove one import from `models/__init__.py` and rerun. Observe the missing table, then restore it.
4. Insert a region, a theatre, a screen and three seats. Set `seat.screen = screen` **without** `back_populates` on one side, print `screen.seats` before flushing, then add `back_populates` and compare.
5. Store `BookingStatus.CONFIRMED`, then read the raw column with `text("select status from bookings")` and confirm it holds `CONFIRMED`.
6. Write `shows_in_region`, count queries with `echo=True`, then remove `selectinload` and watch the N+1 pattern appear.

## Evidence of Understanding

- You can explain why `__abstract__ = True` is needed and what `declared_attr` solves for mixins.
- You can say what `back_populates` synchronises (in-memory attributes) and what it does not (it adds no column).
- You can justify enum versus lookup table for `BookingStatus` and `SeatType` with the "changes without a release?" test.
- You can state that enums are stored by name and describe what happens to rows after a member rename.
- You can explain why status belongs on `ShowSeat`, price on `(show, seat type)`, and booking links in an association table.
- You can predict why a model whose module was never imported has no table.

## Interview Questions to Rehearse

### Q: Why model `ShowSeat` instead of putting `status` on `Seat`?

A seat is physical and shared by every show on that screen, while availability is per show. Putting status on `Seat` makes the 6 PM sale block the 9 PM show. `ShowSeat` is the (show, seat) row that owns status, blocked time and, later, the version column used for locking. It also makes inventory creation a bulk insert per show.

### Q: What does `back_populates` do, and does it change the schema?

It pairs two `relationship()` objects so a change on one side updates the other in the session before any flush. It adds no column and no constraint, since the foreign key is what changes the schema. Without it both attributes still load correctly from the database, but a live session can show inconsistent collections.

### Q: Enum column or lookup table?

If the values are fixed by code and every tenant sees the same set, use an enum. If operators add or rename values, or the value carries data like a price, use a table and reference it with a foreign key. Note that enums are stored by name, so renaming a member needs a migration.

### Q: Your `create_all` skipped two tables. What happened?

The model classes were never imported, so their class bodies never ran and `Base.metadata` does not know them. Import all model modules before `create_all`, usually via `models/__init__.py`. In production, replace `create_all` with Alembic migrations, which also handle alterations.

### Q: How would you list shows for a region without N+1 queries?

Join `Show` to `Screen`, `Theatre` and `Region` in one `select` and filter on the region name. For related collections such as prices, add `selectinload`, which issues one additional query per relationship rather than one per row.

### Q: Why store money as an integer?

Floats cannot represent most decimal fractions exactly, and totals drift. Use integer minor units (paise) or `Numeric` with `Decimal`, and convert only at the display edge.

## Common Pitfalls

- A `region` field on the `Region` model (copy-paste from `Theatre`). The parent never references itself.
- Declaring a `ForeignKey` but no `relationship()`, then wondering why `theatre.region` does not exist.
- `from enum import Enum` followed by `from sqlalchemy import Enum`. Alias the SQLAlchemy one.
- A `booking_id` on `ShowSeat`, which erases the history of earlier bookings.
- Mutating a JSON list in place and expecting an UPDATE.
- Relying on `create_all` in production, or forgetting to import a model module.
- Using `datetime.utcnow()` (deprecated since 3.12) or a naive datetime in a timezone-aware column.

## Suggested Extension

Add a `Price` history: instead of a mutable `price` column, make `ShowSeatType` rows append-only with `valid_from`, and write the query that returns the price in force when a booking was created. Then explain which unique constraint you would drop and which you would add.
