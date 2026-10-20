# Module 3 — MCQs by Lesson

Multiple-choice questions transcribed from the screenshots in `info/Python-vertical/Lessons/Module-3/Mcqs/`, grouped by the lesson named in each screenshot's page header. Lessons are in class-date order. Within a lesson, questions are split into the page's two sections (**Assignment** and **Additional Problems**), each numbered as on the page (Qn). Options are lettered a, b, c, … in on-screen order. The screenshots show no answers, so none are given.

**56 questions** from 56 screenshots, across 5 lessons.

## Contents

- [MCQs for lesson: Backend LLD: Machine Coding - 7: Code Parking Lot 2 .](#mcqs-for-lesson-backend-lld-machine-coding---7-code-parking-lot-2-) — 10 questions
- [MCQs for lesson: Backend LLD: Machine Coding - 9: Code BookMyShow 1](#mcqs-for-lesson-backend-lld-machine-coding---9-code-bookmyshow-1) — 10 questions
- [MCQs for lesson: Backend LLD: Machine Coding - 10: Code BookMyShow 2](#mcqs-for-lesson-backend-lld-machine-coding---10-code-bookmyshow-2) — 10 questions
- [MCQs for lesson: Backend LLD: Machine Coding - 11: Code BookMyShow 3](#mcqs-for-lesson-backend-lld-machine-coding---11-code-bookmyshow-3) — 10 questions
- [MCQs for lesson: Backend LLD: Machine Coding - 13: Code Splitwise 1](#mcqs-for-lesson-backend-lld-machine-coding---13-code-splitwise-1) — 16 questions

---

## MCQs for lesson: Backend LLD: Machine Coding - 7: Code Parking Lot 2 .

_Class date: Fri, 11 Sep 2026_

### Assignment

#### Q3. Question 01: Layering responsibility

In the Controller → Service → Repository pattern used in this lecture, which statement correctly describes where responsibilities live?

- **a)** The Service contains business logic and never touches a DTO; the Controller only unwraps/wraps DTOs; the Repository only saves and finds data
- **b)** The Controller contains business logic, the Service validates DTOs, and the Repository decides which spot to assign
- **c)** The Repository contains business logic since it’s closest to the data; the Service only stores objects in memory
- **d)** The Controller, Service, and Repository are interchangeable — any of them can hold validation logic

<sub>Screenshot: `msedge_UHorMg0lfv.png`</sub>

#### Q4. Ques 02: Generic Repository

Look at this code from the lecture:

```python
T = TypeVar("T", bound=BaseModel)

class InMemoryRepository(Generic[T]):
    def __init__(self):
        self.items: List[T] = []
        self.next_id = 1

    def save(self, item: T) -> T:
        if item.id is None:
            item.id = self.next_id
            self.next_id += 1
            item.created_at = datetime.now()
        item.last_modified_at = datetime.now()
        self.items.append(item)
        return item
```
Why does the class use Generic[T] instead of writing separate GateRepository, TicketRepository, etc. classes from scratch, each with their own save()?

- **a)** Because Generic[T] automatically creates a real database connection under the hood
- **b)** Because save() and findbyid() do the exact same thing regardless of model type, so writing one generic class avoids repeating identical logic across many near-identical classes
- **c)** Because Python requires all repositories to inherit from Generic[T] in order to work with TypeVar
- **d)** Because without Generic[T], Python would not allow more than one repository class in the same file

<sub>Screenshot: `msedge_1muAoLhWMe.png`</sub>

#### Q5. Tracing - give the output

Foo below is a plain class that does not inherit from BaseModel, so it has no id, createdat, or lastmodified_at attributes.

```python
class Foo:
    pass

class FooRepository(InMemoryRepository[Foo]):
    pass

repo = FooRepository()
repo.save(Foo())
```
What actually happens when repo.save(Foo()) runs?

- **a)** Python silently converts Foo into a BaseModel automatically
- **b)** This code cannot even be written — Generic[T] classes reject non-conforming types at import time
- **c)** The code raises an AttributeError at runtime, the moment it tries to read or set item.id, since TypeVar bounds are advisory and not enforced by the interpreter
- **d)** Python raises a TypeError immediately, before save() even runs, because Foo doesn’t satisfy the bound=BaseModel constraint

<sub>Screenshot: `msedge_n3dAZG2f5a.png`</sub>

#### Q6. Question 04: Why the DTO rule matters

BillController and PaymentController were left as homework, not built live. According to the lecture, why is this considered “low-risk” homework rather than a real gap in understanding?

- **a)** Because Controllers are optional in Python and the system works fine without them
- **b)** Because DTOs aren’t needed at all in a working system
- **c)** Because BillService and PaymentService are simpler than TicketService, so their Controllers don’t really matter
- **d)** Because BillService and PaymentService already take plain values in and return models out, following the exact same rule as TicketService — so their Controllers are just wiring: unwrap Request DTO, call Service, wrap Response DTO, the exact pattern already shown in full for TicketController

<sub>Screenshot: `msedge_SHpyD4H18L.png`</sub>

#### Q7. Debug: Find the layering violation

A teammate writes this TicketService method:

```python
class TicketService:
    def issue_ticket(self, request: IssueTicketRequestDTO) -> Ticket:
        gate = self.gate_repository.find_by_id(request.gate_id)
        if gate.gate_type != GateType.ENTRY:
            raise InvalidGateException("Cannot issue a ticket at an exit gate")
        vehicle = Vehicle(request.vehicle_number, request.vehicle_type, request.owner_name)
```
According to the rules taught in this lecture, what is wrong with this code?

- **a)** issue_ticket() takes request: IssueTicketRequestDTO directly, which violates the rule that the Service layer must never touch a DTO — it should take plain values (gate_id, vehicle_number, vehicle_type, owner_name) instead
- **b)** Nothing is wrong — this is exactly how TicketService.issue_ticket() should be written
- **c)** The gate-type check should not be inside the Service at all — it belongs in the Controller
- **d)** Vehicle objects cannot be constructed inside a Service method

<sub>Screenshot: `msedge_bLEKlySs3h.png`</sub>

#### Q8. Scenario-based: Partial payments

A customer pays ₹200 in cash and then ₹300 online for the same bill, recorded as two separate Payment objects. Given this line from

```python
PaymentService.make_payment():

total_paid = sum( p.amount for p in bill.payments if p.payment_status == PaymentStatus.SUCCESS)
```
If the online ₹300 payment FAILS (status = FAILED) but the ₹200 cash payment succeeded, and the bill amount is ₹500, what happens?

- **a)** total_paid becomes ₹500 because both payments are counted regardless of status, so the bill is marked PAID and the spot is freed
- **b)** total_paid becomes ₹200 (only the successful cash payment counts), which is less than ₹500, so the bill stays UNPAID and the spot stays OCCUPIED
- **c)** The code crashes with an exception because a FAILED payment is not allowed to exist in bill.payments
- **d)** total_paid becomes ₹300 because only the most recent payment is considered

<sub>Screenshot: `msedge_EyKYkhRDjO.png`</sub>

#### Q9. Question 7: Why the GIL doesn't prevent the race condition

Python’s GIL (Global Interpreter Lock) ensures only one thread executes Python bytecode at any given instant. Given this, why can two gate threads still race on the same ParkingSpot?

- **a)** The GIL only applies to single-core machines, and most servers use multiple cores
- **b)** The GIL is disabled automatically whenever threading.Thread is used
- **c)** The GIL guarantees atomicity for a single bytecode instruction, but “read spot status” and “later write spot status” are separate steps — the GIL can switch which thread runs in the gap between those steps, so the overall read-then-write sequence is not atomic
- **d)** The GIL only protects integer variables, not object attributes like parkingspotstatus

<sub>Screenshot: `msedge_nWEvOFvjx4.png`</sub>

#### Q10. Coding: Where should the lock be created?

```python
class TicketService:
    def __init__(self, gate_repository,
                 parking_spot_repository,
                 ticket_repository, allotment_strategy):
        self.gate_repository = gate_repository
        self.parking_spot_repository = parking_spot_repository
        self.ticket_repository = ticket_repository
        self.allotment_strategy = allotment_strategy
        self._spot_lock = threading.Lock()

    def issue_ticket(self, gate_id, vehicle_number,
                     vehicle_type, owner_name):
        with self._spot_lock:
            pass
```
The lock, self._spot_lock, is created once in init and reused on every call to issue_ticket(), instead of writing lock = threading.Lock() as the first line inside issue_ticket() itself. Why does this placement matter for correctly fixing the two-gate race condition?

- **a)** It doesn’t matter — both placements behave identically, since every threading.Lock() call refers to the same global lock object in Python
- **b)** A lock only blocks other threads that are trying to acquire that exact same lock object. If the lock were created fresh inside issue_ticket(), Gate A’s thread and Gate B’s thread would each get their own private lock and would never actually wait on each other, so the race condition would still happen
- **c)** Creating the lock inside init makes TicketService immutable, which is what actually prevents the race condition
- **d)** It only matters for performance, not correctness — either placement would prevent the race condition equally well

<sub>Screenshot: `msedge_02Nhfk9o5t.png`</sub>

#### Q11. Predicting the concurrency test result

In concurrencytest.py, exactly ONE ParkingSpot exists, and two separate Gate objects (Gate A and Gate B) both call issueticket() on the SAME TicketService instance from two threads, with the correct shared-lock fix in place. What is the guaranteed outcome, no matter how many times the test is run?

- **a)** Exactly one thread will print “got spot” and the other will print “found lot full” (raising ParkingFullException) — never both succeeding
- **b)** Both threads will always succeed and print “got spot,” since Python threads run independently
- **c)** The outcome is random — sometimes both succeed, sometimes both fail, since there is no way to control thread scheduling
- **d)** The program will deadlock and never finish, since both threads are waiting on the same lock forever

<sub>Screenshot: `msedge_C55JKBUiOw.png`</sub>

#### Q12. Debug: The AI Corner locking bug

The AI-suggested fix uses one lock per VehicleType:

```python
self._locks_by_vehicle_type = defaultdict(threading.Lock)

def issue_ticket(self, gate_id, vehicle_number,
vehicle_type, owner_name):
    with self._locks_by_vehicle_type[vehicle_type]:
        assigned_spot = self.allotment_strategy.find_spot(
            self.parking_spot_repository.find_all(),
            vehicle_type)
```
Gate A is issuing a ticket for a CAR, and at the exact same moment, Gate B is issuing a ticket for a TRUCK. There is only one available spot, and it supports [TRUCK, CAR, BIKE] (per the spot-size design from the earlier lecture). What is the actual risk with this fix?

- **a)** There is no risk — different vehicle types always mean different spots, so this fix is completely safe
- **b)** Gate A and Gate B acquire two DIFFERENT lock objects (one for CAR, one for TRUCK), so neither blocks the other. Since the one available spot supports both CAR and TRUCK, both threads can read it as EMPTY at the same time and both assign it — reintroducing the original race condition
- **c)** The code will raise a KeyError because defaultdict cannot be used with threading.Lock
- **d)** This fix is strictly worse than no lock at all, because defaultdict is slower than a regular dictionary

<sub>Screenshot: `msedge_RVSEAqF44y.png`</sub>

## MCQs for lesson: Backend LLD: Machine Coding - 9: Code BookMyShow 1

_Class date: Mon, 21 Sep 2026_

### Assignment

#### Q2. Abstract Base Class Purpose

In SQLAlchemy, what does setting __abstract__ = True on a base class actually do?**

- **a)** It tells SQLAlchemy that this class's columns should be inherited by subclasses, but the class itself does not get its own table
- **b)** It prevents the class from ever being instantiated in Python
- **c)** It marks the class as read-only in the database
- **d)** It automatically creates a table with no rows allowed

<sub>Screenshot: `msedge_5anJJFvH4V.png`</sub>

#### Q3. Relationship Sync Without Back_Populates

Two model classes, Screen and Seat, each declare a relationship() describing the connection between them, but neither uses back_populates. What is the direct consequence of this?**

- **a)** The database foreign key column will not be created
- **b)** The two in-memory Python attributes (e.g. screen.seats and seat.screen) may not automatically stay in sync with each other, even though the underlying foreign key is set correctly
- **c)** SQLAlchemy will throw an error when the program starts
- **d)** The relationship becomes many-to-many automatically

<sub>Screenshot: `msedge_s2PK6JGul9.png`</sub>

#### Q4. Foreign Key Avoids Data Duplication

A SeatType table stores rows like "GOLD" and "SILVER". Both Seat and ShowSeatType reference SeatType using a foreign key rather than storing a copy of the name. What is the main benefit of this design?**

- **a)** It makes queries run without needing joins
- **b)** It allows a Seat to have multiple seat types at once
- **c)** Renaming a SeatType (e.g. "GOLD" to "Premium Gold") only requires updating one row, and it reflects everywhere that type is referenced
- **d)** It removes the need for a primary key on SeatType

<sub>Screenshot: `msedge_iURiZypRPd.png`</sub>

#### Q5. Auto-Incrementing Primary Key Values

Consider this code, where BaseModel gives every class an auto-incrementing integer id, and a table is created fresh (it didn't exist before):**

```python
class Movie(BaseModel):
    __tablename__ = "movies"
    name = Column(String)

movie1 = Movie(name="Inception")
movie2 = Movie(name="Interstellar")
session.add(movie1)
session.add(movie2)
session.commit()

print(movie1.id, movie2.id)
```
What gets printed?

- **a)** None None
- **b)** 0 1
- **c)** It throws an error because id was never set manually
- **d)** 1 2

<sub>Screenshot: `msedge_VxOFXTMxrG.png`</sub>

#### Q6. Enum Storage As Text Name

Given this enum and column definition:**

```python
class BookingStatus(Enum):
    CONFIRMED = auto()
    CANCELLED = auto()
    PENDING = auto()

booking_status = Column(Enum(BookingStatus))
```
If a Booking row is saved with booking_status = BookingStatus.CONFIRMED, what value is actually stored as text in the database column by default?

- **a)** "CONFIRMED" (the member's name)
- **b)** 1 (the position of CONFIRMED in the enum)
- **c)** "BookingStatus.CONFIRMED" (the full qualified name)
- **d)** True

<sub>Screenshot: `msedge_hj4WayKhVD.png`</sub>

#### Q7. Unimported Models Skip Table Creation

A team defines all their 12 model classes across multiple files, correctly using `Base` and `__tablename__`, but only imports 10 of them into `main.py` before calling this:**

```python
Base.metadata.create_all(engine)
```
What happens to the 2 model classes that were never imported?

- **a)** SQLAlchemy scans the whole project automatically and creates their tables anyway
- **b)** Their tables are silently not created, because SQLAlchemy only registers a class once Python has actually run that class's definition
- **c)** The program throws an error immediately, refusing to start
- **d)** Their tables are created but left empty

<sub>Screenshot: `msedge_32oD8iGOnM.png`</sub>

#### Q8. Copy-Paste Field Mistake

Here is a class meant to represent a Region that has many Theatres:**

```python
class Region(BaseModel):
    def __init__(self, name, region):
        super().__init__()
        self.name = name
        self.region = region
```
What is wrong with this code, and what's the correct fix?

- **a)** It's missing a theatres list, which must always be added immediately
- **b)** super().__init__() should not be called in a subclass
- **c)** The region parameter/field doesn't make sense on a Region class — it looks like a copy-paste leftover from Theatre, which is the class that should hold a reference to its parent Region
- **d)** name should be renamed to region_name

<sub>Screenshot: `msedge_QMk7d3iKwo.png`</sub>

#### Q9. Seat-Booking Link Over Time

A junior developer writes the ShowSeat model like this, believing a simple foreign key back to Booking is enough to track which booking a seat belongs to:

```python
class ShowSeat(BaseModel):
    __tablename__ = "show_seats"

    show_id = Column(Integer, ForeignKey("shows.id"))
    seat_id = Column(Integer, ForeignKey("seats.id"))
    show_seat_status = Column(Enum(ShowSeatStatus))
    booking_id = Column(Integer,
ForeignKey("bookings.id")) # <-- added by the junior dev

    show = relationship("Show")
    seat = relationship("Seat")
    booking = relationship("Booking")
```
Why is adding booking_id directly on ShowSeat an incorrect way to link Booking and ShowSeat over time?

- **a)** It's fine — one seat can only ever belong to one booking for all time, so a direct foreign key is correct
- **b)** relationship("Booking") is invalid syntax and will not run
- **c)** ForeignKey("bookings.id") should instead point to "users.id"
- **d)** A single foreign key on ShowSeat can only point to one Booking at a time, but the same ShowSeat can legitimately be linked to more than one Booking over time (e.g., after a cancellation and a later rebooking) — this needs a proper many-to-many association table instead

<sub>Screenshot: `msedge_ZajH4JTdSt.png`</sub>

#### Q10. Screen Capability Vs Show Configuration

A Screen can physically support both 3D and Dolby Audio (this is stored as Screen.features). However, a specific 6 PM showing of a movie on that screen is only actually running in 2D that day. Why does the system also need a separate Show.features list, instead of just relying on Screen.features?

- **a)** Because Screen.features describes what the screen is physically capable of, while Show.features describes what is actually active for that one specific showing — these are two different questions and can have different answers
- **b)** Because Screen.features and Show.features must always contain identical values
- **c)** Because SQLAlchemy requires every enum to be duplicated across two tables
- **d)** Because Show cannot have any relationship to Screen

<sub>Screenshot: `msedge_YZZ5odX9Fu.png`</sub>

#### Q11. Multi-Level Join Query Design

A repository layer needs a method to list every Show playing in a given region. The relationships are: Show belongs to a Screen, Screen belongs to a Theatre, and Theatre belongs to a Region. Which approach correctly fetches all shows for a region named "Bangalore"?

- **a)** Query Show directly by a region_name column, since every Show should store its region name directly for fast lookups
- **b)** Query Show, then join through Screen, then through Theatre, then through Region, filtering where the Region's name equals "Bangalore"
- **c)** Query Region only, since regions automatically know all shows happening inside them without any joins
- **d)** Fetch all Show rows, then manually loop through every one checking screen and theatre in application code, since joins across four tables are not supported by an ORM

<sub>Screenshot: `msedge_gWCktvsIsi.png`</sub>

## MCQs for lesson: Backend LLD: Machine Coding - 10: Code BookMyShow 2

_Class date: Wed, 23 Sep 2026_

### Assignment

#### Q2. Avoiding Reserved SQL Table Names

A team is building a backend using SQLAlchemy. They create a model called Order. In many SQL databases, ORDER is a reserved keyword (used in ORDER BY). What is the correct and safe way to handle this?

- **a)** Leave __tablename__ unset — SQLAlchemy will detect the conflict and automatically choose a safe name
- **b)** Explicitly set __tablename__ = "orders" — a name that avoids the reserved word
- **c)** Rename the Python class from Order to OrderModel — this alone fixes the table name conflict
- **d)** Set __tablename__ = "Order" exactly as the class name — SQLAlchemy automatically escapes reserved words in generated SQL

<sub>Screenshot: `msedge_IiELyuhE31.png`</sub>

#### Q3. Double-Booking Race Condition

Two application threads run the following method at nearly the same time, targeting the exact same list of seats. No database-level locking or special isolation is used:

```python
def book_seats(seats):
    for seat in seats:
        if seat.status != Status.AVAILABLE:
            raise RuntimeError("Seat unavailable")
    for seat in seats:
        seat.status = Status.BLOCKED
    repository.save_all(seats)
```
What is the most likely outcome if both threads run this at nearly the same time on the same seats?

- **a)** The second thread will always raise RuntimeError, since a seat can't be checked twice
- **b)** save_all() automatically detects the conflict and rejects the second thread
- **c)** Both threads can pass the availability check before either one performs the write, so both may end up marking the same seat as BLOCKED — effectively double-booking
- **d)** This code is thread-safe, because Python's GIL ensures only one thread runs at a time, so the two threads can never interleave their steps

<sub>Screenshot: `msedge_2m7cPfMYh6.png`</sub>

#### Q4. Isolation Level Doesn't Prevent Race

Under an isolation level called REPEATABLE READ (a common default in some relational databases), a transaction is guaranteed not to see changes made by other transactions to rows it has already read, until it re-reads or commits. Consider this timeline between two transactions, T-A and T-B, both updating the same row X:

```
Time 0ms: T-A starts, reads row X: value = AVAILABLE
Time 2ms: T-B starts, reads row X: value = AVAILABLE
Time 4ms: T-A updates row X to BLOCKED, commits successfully
Time 5ms: T-B updates row X to BLOCKED (based on its own earlier read), commits
```
What actually happens at Time 5ms?

- **a)** T-B's commit also succeeds, because REPEATABLE READ does not stop two separate transactions from each reading the same "before" value and both acting on it
- **b)** T-B's commit fails automatically, since T-A already changed the row
- **c)** T-A's commit is retroactively rolled back once T-B commits
- **d)** Both transactions are blocked from committing until a human manually resolves the conflict

<sub>Screenshot: `msedge_UQGmDHNTE9.png`</sub>

#### Q5. Serializable Isolation Definition

Which of the following best defines what SERIALIZABLE isolation guarantees in a relational database?

- **a)** Only one transaction is allowed to be active anywhere in the database at any moment
- **b)** Transactions are guaranteed to always commit in the exact order they were started
- **c)** No transaction can ever fail, roll back, or need a retry
- **d)** The outcome of running transactions concurrently must be equivalent to some valid outcome of running those same transactions one after another, in some order

<sub>Screenshot: `msedge_WDFjDtM5N0.png`</sub>

#### Q6. Serializable Allows Unrelated Concurrency

Two transactions run under SERIALIZABLE isolation. Transaction 1 updates Row X. Transaction 2, running at the same time, updates a completely different Row Y in the same table — the two rows share no data or relationship. What is the most likely outcome?

- **a)** Both transactions fail, because SERIALIZABLE permits only one active transaction across the whole database
- **b)** Both transactions commit successfully and independently, since SERIALIZABLE only prevents conflicts on rows that are actually accessed by both transactions
- **c)** Only the transaction that started first is allowed to commit
- **d)** Both commit, but the transaction that commits second silently overwrites data from the first

<sub>Screenshot: `msedge_xcv8aUeWfm.png`</sub>

#### Q7. Threading Lock Across Processes

A backend application runs as multiple separate server processes (for example, behind a load balancer), all connecting to the same shared database. A developer adds a threading.Lock() inside a booking method, reasoning: "only one thread can hold the lock at a time, so this prevents double-booking." Why does this NOT actually prevent two different server processes from double-booking the same database row?

- **a)** A threading.Lock() object only coordinates threads within a single process's memory — a lock created in one server process has no effect on threads running in a separate server process
- **b)** threading.Lock() objects expire automatically after a few milliseconds, so they don't stay held long enough to help
- **c)** threading.Lock() can only be used with synchronous code, and database calls are always asynchronous
- **d)** threading.Lock() requires a special database driver to function correctly

<sub>Screenshot: `msedge_cN22B5qts2.png`</sub>

#### Q8. DTO Boundary Decoupling Benefit

A Controller class in a layered backend application accepts a dedicated request object (a DTO — Data Transfer Object) as its parameter, instead of accepting raw domain/model objects directly or a long list of loose primitive parameters. What is the main benefit of this design choice?

- **a)** DTOs are mandatory for any class that uses an ORM like SQLAlchemy
- **b)** DTOs make the application run measurably faster, since fewer objects are created in memory
- **c)** A DTO defines a stable, deliberate contract for exactly what a use case needs — so if the underlying domain models change shape later, callers of the use case aren't automatically broken
- **d)** DTOs are only useful for return values, not for input parameters

<sub>Screenshot: `msedge_nSdHr5VgRU.png`</sub>

#### Q9. SQLAlchemy Automatic Change Tracking

In an application using SQLAlchemy, an object seat was fetched earlier in a session (e.g., session.query(Seat).get(seat_id)). Later in the same function, this code runs:

```python
seat.status = "BLOCKED"
seat.blocked_at = datetime.now()
# ... some other unrelated database operations using the same session ...
session.commit()
```
Notice there is no explicit session.add(seat) or repository.save(seat) call after changing seat.status. What happens when session.commit() runs?

- **a)** The changes to seat.status and seat.blocked_at are silently lost, since nothing was explicitly re-saved
- **b)** The commit throws a runtime error, because SQLAlchemy requires every changed object to be explicitly re-added to the session
- **c)** Only seat.status is saved; seat.blocked_at is ignored because it was set after the first attribute
- **d)** Both changes are saved automatically — SQLAlchemy tracks changes to objects that were already loaded through the session, and commit() flushes all pending changes together

<sub>Screenshot: `msedge_KBhFq4eBCX.png`</sub>

#### Q10. AI-Generated Code Missing Business Rule

A movie-ticket booking system has a business rule: the price of a seat depends on both which specific show it belongs to and its seat type — the same seat type (say, "GOLD") can be priced differently for a matinee show versus a night show, or between two different theatres. To support this, prices are stored in a table keyed on the pair (show, seat_type), not as a flat price on the seat type alone.
An AI assistant was asked to write a pricing function and returned this:

```python
class PriceCalculator:
    def calculate_price(self, show_seats):
        total = 0
        for show_seat in show_seats:
            seat_type_name = show_seat.seat.seat_type.name
            if seat_type_name == "GOLD":
                total += 300
            elif seat_type_name == "SILVER":
                total += 200
            else:
                total += 150
        return total
```
What is the most fundamental problem with this code, given the business rule above?

- **a)** It uses an if/elif chain instead of a dictionary lookup, which is considered bad Python style
- **b)** It hardcodes a single flat price per seat-type name and never considers which specific show the seat belongs to, so it cannot support the (show, seat_type) pricing rule at all
- **c)** It returns an integer instead of a float, which will always cause a runtime crash in Python
- **d)** It doesn't use a try/except block, so it will always crash if show_seats is an empty list

<sub>Screenshot: `msedge_no8hhTniKD.png`</sub>

#### Q11. Show-Level Pricing

In a booking system, ticket prices are stored in a table keyed on the specific (show, seat_type) pair — meaning every individual show has its own price row per seat type, rather than seat types having one single global price. A theatre now wants weekday GOLD seats priced at ₹250 and weekend GOLD seats priced at ₹400, on the exact same screen. Does this pricing design already support that, with zero code or schema changes?

- **a)** No — a day_of_week field would need to be added to the seat-type table first
- **b)** No — the price table is keyed by screen, not by individual show, so all shows on one screen must share the same price
- **c)** Yes — a weekday show and a weekend show are two different show records, so each one already gets its own (show, seat_type) price row
- **d)** Only if the pricing function is modified to manually check the day of the week from the show's start time

<sub>Screenshot: `msedge_LLtjSpL6za.png`</sub>

## MCQs for lesson: Backend LLD: Machine Coding - 11: Code BookMyShow 3

_Class date: Fri, 25 Sep 2026_

### Assignment

#### Q3. Check-On-Demand Expiry Tradeoff

A booking system needs to release a seat that a user reserved but never paid for, after a fixed hold time. One design checks and resets expired holds only at the moment a different user tries to book that same seat, instead of running a background job that scans and clears every expired hold on a fixed schedule. What is the main trade-off of this "check-on-demand" approach compared to a scheduled background sweep?

- **a)** It keeps stale reservations invisible to nobody in particular — a seat that nobody attempts to rebook can stay stuck in its expired state indefinitely, since there is no other trigger to re-evaluate it.
- **b)** It is always faster, because it avoids writing to the database entirely, even on a successful booking.
- **c)** It never needs a background job at all, because the database engine automatically expires rows on its own.
- **d)** It requires an extra column on every table in the database to track expiry, which a scheduled job does not need.

<sub>Screenshot: `msedge_kxjtxEYfYA.png`</sub>

#### Q4. Unexecuted Query Always Truthy

A developer writes the following method to look up a user by email so that a signup flow can check whether an account already exists:

```python
def find_by_email(self, email):
    return self.session.query(User).filter(User.email == email)
```
In the service layer, this result is used as: if existing_user: raise RuntimeError("already exists"). What will actually happen when a brand-new user, whose email has never been used before, tries to sign up?

- **a)** The signup will succeed normally, because the filter only matches rows where the email is equal.
- **b)** The signup will always be rejected as "already exists", because the method returns a Query object (which is always truthy) instead of an actual User or None.
- **c)** The application will raise a database connection error, because .filter() cannot be used without .first() or .all().
- **d)** The signup will succeed, but the new user's row will be saved twice into the database.

<sub>Screenshot: `msedge_GN7y5p0NHe.png`</sub>

#### Q5. Missing Self Attribute Assignment

A developer writes the following constructor for a service class that depends on a password-hashing helper:

```python
class UserService:
    def __init__(self, user_repository, password_hasher):
        self.user_repository = user_repository

    def sign_up(self, email, password):
        hashed = self.password_hasher.encode(password)
        ...
```
What will happen when sign_up() is called?

- **a)** It will run correctly, because Python automatically assigns every constructor parameter to an instance attribute of the same name.
- **b)** It will silently hash the password using a default algorithm instead of the one passed in.
- **c)** It will raise an AttributeError, because password_hasher was accepted as a parameter but never assigned to self.password_hasher, so that attribute does not exist on the instance.
- **d)** It will raise a TypeError at the point the class is instantiated, before sign_up() is ever called.

<sub>Screenshot: `msedge_zd5cDGYsbZ.png`</sub>

#### Q6. Salted Hash Differs Each Call

A password-hashing helper is used as follows, where encode() internally generates a fresh random salt on every call before hashing:

```python
hash1 = password_hasher.encode("hunter2")
hash2 = password_hasher.encode("hunter2")
print(hash1 == hash2)
```
What will this print?

- **a)** True, because the same input to the same function always produces the same output.
- **b)** It will raise an exception, because the same password cannot be hashed twice in the same program.
- **c)** True, but only on the first run of the program; False on every run after that.
- **d)** False, because each call generates a new random salt, so the two resulting hash strings will differ even though the underlying password is identical.

<sub>Screenshot: `msedge_Ey6bCunb30.png`</sub>

#### Q7. Timestamp Update Scoped To Row

A Booking model has automatic timestamp columns defined roughly as:

```python
created_at = Column(DateTime, default=datetime.utcnow)
last_modified_at = Column(DateTime,
default=datetime.utcnow, onupdate=datetime.utcnow)
```
A Payment row (a separate table, with a foreign key pointing back to Booking) is created and linked by running booking.payments.append(new_payment) and committing the session. No column on the bookings row itself is changed. What happens to booking.last_modified_at?

- **a)** It stays unchanged, because onupdate only fires when a column on that exact row (the bookings row) is modified, and appending a related Payment only touches the payments table's foreign key column.
- **b)** It updates to the current time, because appending to any related list counts as a change to the booking.
- **c)** It is reset to NULL, because relationship changes invalidate cached timestamp columns.
- **d)** It updates immediately, without needing a commit, because SQLAlchemy tracks relationship changes in real time.

<sub>Screenshot: `msedge_RHNTjqWZdQ.png`</sub>

#### Q8. Deterministic Hash Password Correlation

A system stores user passwords by running them through a plain, deterministic hash function (one where the same input always produces the same output, with no randomness involved) before saving them. Two different users, Alice and Bob, happen to choose the exact same password. What problem does this create, specifically because the hash function is deterministic?

- **a)** Nothing — as long as the function is one-way, it does not matter whether it is deterministic.
- **b)** Their stored hash values will be identical, so if an attacker ever figures out one of them, they immediately know that the other account has the same password too.
- **c)** The database will refuse to store two identical hash values in the same column, causing one of the signups to fail.
- **d)** Deterministic hashing makes the password recoverable in plain text directly from the hash.

<sub>Screenshot: `msedge_fZLFH8ENwF.png`</sub>

#### Q9. Correct Salted Hash Verification

A password-hashing library provides two methods: encode(raw_password), which produces a new salted hash from a plain password, and matches(raw_password, stored_hash), which checks a login attempt against a previously stored hash. Why is it incorrect to check a login by writing if password_hasher.encode(login_password) == stored_hash: instead of using matches()?

- **a)** Because encode() cannot be called more than once per program run.
- **b)** Because encode() only works on the first password a user ever sets, not on subsequent login attempts.
- **c)** Because encode() generates a brand-new random salt every time it runs, so re-encoding the login attempt produces a hash with a different salt than the one embedded in the originally stored hash — the two will almost never match, even for the correct password.
- **d)** Because == cannot be used to compare two strings in Python.

<sub>Screenshot: `msedge_hlNGlChok1.png`</sub>

#### Q10. Stale Status Until Re-Evaluated

A seat-booking system marks a seat as "held" the moment a user selects it, and treats a held seat as available again if more than 15 minutes have passed since it was held — but only re-checks this at the moment a new booking attempt reads that seat's row; nothing proactively rewrites the row when the 15 minutes pass. Seat C4 is marked "held" at 2:00 PM by a user who then abandons the booking. At 2:19 PM, before anyone else has attempted to book it, what does the seat's stored status literally say in the database at that exact moment?

- **a)** "Available", because the database automatically flips the status back after the hold period elapses.
- **b)** "Expired", a distinct status that gets set automatically once 15 minutes pass.
- **c)** The row is deleted automatically once the hold expires.
- **d)** "Held", because nothing has re-evaluated or rewritten that row since it was set — the status only changes at the moment a fresh booking attempt reads and re-evaluates it.

<sub>Screenshot: `msedge_8QH8qL89cG.png`</sub>

#### Q11. Missing Foreign Key Existence Check

A generated Service class for adding a new Theatre under a Region looks like this:

```python
class TheatreService:
    def __init__(self, theatre_repository):
        self.theatre_repository = theatre_repository

    def add_theatre(self, name, region_id):
        theatre = Theatre(name=name, region_id=region_id)
        return self.theatre_repository.save(theatre)
```
Elsewhere in the same codebase, every other place that accepts a foreign-key-style ID (such as a user ID or a show ID) looks up the referenced entity through its repository first and raises an error if it is not found, before using it. Judged against that established convention, what is the most important gap in this Service?

- **a)** It never checks whether region_id actually refers to an existing Region — it builds and saves a Theatre pointing at a region_id that could be completely invalid, unlike the validation convention used everywhere else for foreign IDs.
- **b)** It does not hash or encrypt the theatre's name before saving it.
- **c)** It is missing a try/except block around the database call.
- **d)** It should not accept region_id as a plain integer parameter at all.

<sub>Screenshot: `msedge_HJ3oaL13BZ.png`</sub>

#### Q12. Default Vs Onupdate Column Behavior

An ORM lets you declare a timestamp column with both a default value and an onupdate value, roughly as Column(DateTime, default=some_function, onupdate=some_function). What do these two arguments each control?

- **a)** default sets the value once when the application starts up; onupdate sets it once when the application shuts down.
- **b)** default fills the column the moment a row is first inserted; onupdate refreshes the column's value whenever that row is later updated.
- **c)** default and onupdate do the same thing — onupdate is simply required for older versions of the ORM.
- **d)** default sets a fixed, unchanging value; onupdate overrides it with a random value on every read.

<sub>Screenshot: `msedge_hbvmUP1WGW.png`</sub>

## MCQs for lesson: Backend LLD: Machine Coding - 13: Code Splitwise 1

_Class date: Wed, 30 Sep 2026_

### Assignment

#### Q2. Command Matching Loop Output

What does the following code print?

```python
class Command:
    def __init__(self, keyword):
        self.keyword = keyword

    def matches(self, text):
        return text.startswith(self.keyword)

class CommandExecutor:
    def __init__(self, commands):
        self.commands = commands

    def execute(self, text):
        for c in self.commands:
            if c.matches(text):
                print("Matched:", c.keyword)
                return
        print("Invalid command")

ex = CommandExecutor([Command("create"), Command("settle"), Command("add")])
ex.execute("settle up g1")
ex.execute("delete g1")
```

- **a)** Matched: create followed by Invalid command
- **b)** Matched: settle followed by Invalid command
- **c)** Matched: settle followed by Matched: add
- **d)** Invalid command followed by Invalid command

<sub>Screenshot: `msedge_gh55xclSkX.png`</sub>

#### Q3. Enum Name Value Comparison

What does the following code print?

```python
from enum import Enum

class ExpenseType(Enum):
    NORMAL = 1
    PAYMENT = 2

e = ExpenseType.PAYMENT
print(e.name, e.value)
print(e == ExpenseType.NORMAL)
```

- **a)** PAYMENT 2 followed by True
- **b)** ExpenseType.PAYMENT 2 followed by False
- **c)** PAYMENT 2 followed by False
- **d)** 2 PAYMENT followed by False

<sub>Screenshot: `msedge_ZejCjVtrMM.png`</sub>

#### Q4. Balance Sheet From Rows

Each row below is (user, kind, amount). A "PAID" row adds the amount to that user's balance, and a "HAD_TO_PAY" row subtracts it. What does the code print?**

```python
rows = [
    ("A", "PAID", 900),
    ("A", "HAD_TO_PAY", 300),
    ("B", "HAD_TO_PAY", 300),
    ("C", "HAD_TO_PAY", 300),
]

balance = {}
for user, kind, amt in rows:
    if kind == "PAID":
        balance[user] = balance.get(user, 0) + amt
    else:
        balance[user] = balance.get(user, 0) - amt

print(balance)
```

- **a)** {'A': 600, 'B': -300, 'C': -300}
- **b)** {'A': 900, 'B': 300, 'C': 300}
- **c)** {'A': 600, 'B': 300, 'C': 300}
- **d)** {'A': 300, 'B': -300, 'C': -300}

<sub>Screenshot: `msedge_6mbOrdH51b.png`</sub>

#### Q5. Filtered Expense Rows For User

In an expense-sharing app, each row records one person's part in one expense. What does the code print?**

```python
expense_users = [
    {"expense_id": 1, "user": "A", "type": "PAID", "amount": 600},
    {"expense_id": 1, "user": "B", "type": "HAD_TO_PAY", "amount": 300},
    {"expense_id": 1, "user": "C", "type": "HAD_TO_PAY", "amount": 300},
    {"expense_id": 2, "user": "B", "type": "PAID", "amount": 200},
    {"expense_id": 2, "user": "A", "type": "HAD_TO_PAY", "amount": 200},
]

rows_for_b = [
    r for r in expense_users
    if r["user"] == "B" and r["type"] == "HAD_TO_PAY"
]

ids = [r["expense_id"] for r in rows_for_b]
total = sum(r["amount"] for r in rows_for_b)
print(ids, total)
```

- **a)** [1, 2] 500
- **b)** [2] 200
- **c)** [1, 2] 300
- **d)** [1] 300

<sub>Screenshot: `msedge_4j9vsmcAYY.png`</sub>

#### Q6. Identifying Classes From Nouns

While reading a written requirement to find the classes of a system, you spot the nouns "user", "phone number" and "password". Which conclusion is correct?

- **a)** "User" should become a class, while "phone number" and "password" should be attributes of it
- **b)** All three nouns should become separate classes, because each one is a noun
- **c)** Only "password" should become a class, because it is sensitive information
- **d)** None of them should be a class, because they are all just pieces of data

<sub>Screenshot: `msedge_8BqDr4loPl.png`</sub>

#### Q7. Modeling Paid/Owed Relationships

An Expense must record how much each person paid and how much each person owes. Why is keeping this as a dictionary such as dict[User, int] inside Expense a poor design for a relational database?

- **a)** Python does not allow a dictionary to be stored inside a class
- **b)** Databases can never store JSON or any structured data in a column
- **c)** A dictionary always takes more memory than a table with the same data
- **d)** The amount depends on both the user and the expense, so one row per (expense, user) in its own table is much easier to query

<sub>Screenshot: `msedge_YYmr5lyh06.png`</sub>

#### Q8. Enum Versus Lookup Table

When should a fixed set of values, such as NORMAL and PAYMENT, be modeled as an enum instead of a separate lookup table?

- **a)** When every value is a short piece of text, because text is simple to store
- **b)** When the set rarely changes without a code release, and every owner uses the same set
- **c)** When the set has only two values, because a table would be too small to be useful
- **d)** When the values are shown on screen, because tables are only for hidden data

<sub>Screenshot: `msedge_P29yf0SLJ1.png`</sub>

#### Q9. Reserved Word Table Names

A developer names a database table order (or group). Which statement is most accurate?

- **a)** The app will always crash at startup, because table names can never match a SQL keyword
- **b)** Only the Python class name matters to SQL, so the table name can never cause any problem
- **c)** It may still work because the ORM adds quotes, but hand-written SQL and other tools can break, so plural names like orders are a safer habit
- **d)** Reserved words are always safe as long as they are written in lowercase

<sub>Screenshot: `msedge_DMOnFtlm6v.png`</sub>

#### Q10. Enum Import Name Collision

A developer writes the code below and expects ExpenseType to be a normal Python enum, but it does not behave like one. What is the cause and the fix?

```python
from enum import Enum
from sqlalchemy import Column, Enum

class ExpenseType(Enum):
    NORMAL = 1
    PAYMENT = 2
```

- **a)** Enum classes must define an __init__ method before their members can be used
- **b)** Enum values must be strings, so 1 and 2 should be "1" and "2"
- **c)** The second import replaces the first, so Enum now means SQLAlchemy's Enum. Import it under another name, such as from sqlalchemy import Enum as SAEnum
- **d)** Python enums cannot be used in a file that also imports from sqlalchemy

<sub>Screenshot: `msedge_QJMqYEGFR4.png`</sub>

#### Q11. Abstract Base Model Fix

This shared base class is meant to provide common columns to other models, but SQLAlchemy raises an error saying the class has no __table__ or __tablename__. What is the fix?

```python
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

- **a)** Add __abstract__ = True inside BaseModel, so it gets no table of its own and only shares its columns with subclasses
- **b)** Rename Base to BaseModel
- **c)** Remove the id column
- **d)** Change the type of created_at and updated_at from DateTime to Integer

<sub>Screenshot: `msedge_j34M3r7k2L.png`</sub>

#### Q12. Missing Return After Match

A CommandExecutor should print "Invalid command" only when no command matches the input. Instead, it prints "Invalid command" after every input, even when a command ran successfully. What is the fix?

```python
class CommandExecutor:
    def __init__(self, commands):
        self.commands = commands

    def execute(self, text):
        for c in self.commands:
            if c.matches(text):
                c.execute(text)
        print("Invalid command")
```

- **a)** Call matches after execute instead of before it
- **b)** Replace the for loop with a while loop
- **c)** Move the print statement into __init__
- **d)** Add a return right after c.execute(text), so the method stops at the first match

<sub>Screenshot: `msedge_umh5HDc9TF.png`</sub>

#### Q13. Unregistered Models Skip Table Creation

A developer has model files (for example, models/user.py) that define tables. In main.py, they run the code below, but no tables are created, even though echo=True is set. What is the fix?**

```python
# main.py
from sqlalchemy import create_engine
from models.base_model import Base

engine = create_engine("sqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)
```

- **a)** Set echo=False so that the tables can be created
- **b)** Import the model files (for example, from models.user import User) before calling create_all, so that Base knows about the tables
- **c)** Replace the in-memory SQLite database with a file-based one
- **d)** Call create_all twice, so the second call creates the tables

<sub>Screenshot: `msedge_L1NroDhEzM.png`</sub>

#### Q14. Quantity Belongs To Order-Product Pair

In an online store, one order can contain several products, and for each product in an order we must record the quantity bought. Where should the quantity be stored?

- **a)** As a quantity column on the Product table
- **b)** As a quantity column on the Order table
- **c)** As a list stored inside the customer's profile
- **d)** In a separate table with one row per (order, product) that also holds the quantity

<sub>Screenshot: `msedge_1tb6ZpC11C.png`</sub>

#### Q15. Settlements Unified In One Table

A group-expense app calculates balances from a table of expense records. When two people settle a debt, that payment must count in all future balance calculations. Which design avoids having two separate sources of truth for "money moving between people"?

- **a)** Create a separate Transaction table, and make every balance calculation read both tables
- **b)** Delete the original expense once it has been settled, so it no longer affects anything
- **c)** Store the settlement as another record in the same expense table, marked with a type such as PAYMENT, so balances are computed from one table
- **d)** Keep settlements only in memory and leave them out of balance calculations

<sub>Screenshot: `msedge_ATd86OVC9e.png`</sub>

#### Q16. Adding Command Without Modifying Executor

A command-line app has a main() that passes every input line to a CommandExecutor. The executor holds a list of command objects, and each command implements matches(text) and execute(text). You now need to add a LeaveGroup command. What is the correct change?

- **a)** Add a new elif branch for it inside main()
- **b)** Write a new class that implements matches and execute, and add it to the list given to CommandExecutor
- **c)** Add a leave_group() method to the shared base command class
- **d)** Add a hardcoded check for LeaveGroup inside CommandExecutor

<sub>Screenshot: `msedge_m4bruFRS19.png`</sub>

#### Q17. In-Memory Database For Session Data

You are building a small app that tracks shared expenses while it is running. Nothing needs to be kept after the app is closed. Which database setup fits this requirement best?

- **a)** SQLite in memory, using create_engine("sqlite:///:memory:"), which is a real relational database whose data disappears when the app stops
- **b)** A MySQL server plus a driver package, because every relational database needs a separate server
- **c)** A plain text file, because SQL cannot be used unless data is saved permanently
- **d)** No database at all, because SQLAlchemy only works with data that survives a restart

<sub>Screenshot: `msedge_pIdb9ftJ0L.png`</sub>

