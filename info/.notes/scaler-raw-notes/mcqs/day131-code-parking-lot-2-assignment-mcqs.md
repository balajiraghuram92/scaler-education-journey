Source: Scaler platform, live "Assignment" tab — Day 131, Backend LLD: Machine Coding - 7: Code
Parking Lot 2 (class date Wed, 2 Sep 2026). Transcribed directly from screenshots provided by the
user (`Downloads/machine-coding/0.MCQ's/`). Scenario/code-based reasoning questions on layered
architecture, generic repositories, and concurrency correctness — none were marked as answered on
the platform; all correct answers below were determined by Claude from the question logic. Q1 was
not captured in the screenshot batch (screenshots start at Q2).

## Q2. Repository Layer Responsibility

**Question:** In a layered backend design (Controller → Service → Repository), what is the
Repository layer's job?

**Options:**
- A. Saving and fetching data — nothing about business rules
- B. Converting request DTOs into model objects
- C. Deciding which resource (e.g. a parking spot) to assign to a request
- D. Validating business rules, like rejecting an invalid input type

**Answer: A** — A Repository's sole job is persistence (save/find/list). Resource-assignment logic
(C) belongs in a Service using a Strategy, DTO conversion (B) belongs at the Controller boundary,
and business-rule validation (D) belongs in the Service layer. Mixing any of these into the
Repository breaks the separation the layered architecture exists to provide.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q2)*

## Q3. Generic Bound Compilation Requirement

**Question:**
```java
public class InMemoryRepository<T extends BaseModel> {
    private final List<T> items = new ArrayList<>();

    public T save(T item) {
        if (item.getId() == null) {
            item.setId(1L);
        }
        items.add(item);
        return item;
    }
}
```
Why is the bound `T extends BaseModel` necessary here, instead of just `T`?

**Options:**
- A. It lets the repository store multiple unrelated types at once
- B. Without it, `item.getId()` wouldn't compile, since plain `Object` has no `getId()` method
- C. It is required syntax for all Java generic classes
- D. It makes the compiled code run faster at execution time

**Answer: B** — Without a bound, `T` is erased to `Object`, and `Object` has no `getId()`/`setId()`
methods, so the method body wouldn't compile. The bound is what gives the generic class compile-time
access to `BaseModel`'s methods on every `T`. Option A is backwards (a bound narrows what `T` can be,
it doesn't widen storage); C is false (unbounded generics are valid Java); D confuses compile-time
type-checking with runtime performance.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q3)*

## Q4. Auto-Increment ID Assignment Trace

**Question:**
```java
public class InMemoryRepository<T extends BaseModel> {
    private final List<T> items = new ArrayList<>();
    private long nextId = 1;

    public T save(T item) {
        if (item.getId() == null) {
            item.setId(nextId++);
        }
        items.add(item);
        return item;
    }
}
```
```java
InMemoryRepository<Gate> repo = new InMemoryRepository<>();
Gate g1 = new Gate();
Gate g2 = new Gate();
repo.save(g1);
repo.save(g2);
System.out.println(g1.getId() + ", " + g2.getId());
```
What gets printed?

**Options:**
- A. 0, 1
- B. 1, 1
- C. 1, 2
- D. 2, 3

**Answer: C** — `nextId` starts at 1. `save(g1)` reads `nextId` (1), assigns it to `g1`, then
post-increments `nextId` to 2. `save(g2)` reads `nextId` (2), assigns it to `g2`, then increments to
3. So `g1.getId()==1` and `g2.getId()==2`, printing `1, 2`.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q4)*

## Q5. Business Logic Misplaced In Controller

**Question:**
```java
public class TicketController {
    public IssueTicketResponseDTO issueTicket(IssueTicketRequestDTO request) {
        Gate gate = fetchGate(request.getGateId());
        if (gate.getGateType() == GateType.EXIT) {
            throw new InvalidGateException("Cannot issue a ticket at an exit gate");
        }
        Ticket ticket = buildTicket(request, gate);
        return toResponseDTO(ticket);
    }
    private Gate fetchGate(Long gateId) { /* looks gate up from storage */ }
    private Ticket buildTicket(IssueTicketRequestDTO request, Gate gate) { /* builds a Vehicle, finds a spot, creates the Ticket */ }
}
```
Assuming this code compiles and runs correctly, what is the actual design problem with it?

**Options:**
- A. The gate-type check compares against `GateType.EXIT` instead of `GateType.ENTRY`, which is a logic bug
- B. `IssueTicketResponseDTO` is never returned, so this code doesn't compile
- C. `InvalidGateException` needs to be declared in a `throws` clause for this to compile
- D. `fetchGate()` is a storage lookup and `buildTicket()` contains real business logic (spot assignment, ticket creation), but both are implemented directly inside the Controller instead of a Repository/Service

**Answer: D** — The code is logically and syntactically fine (A, B, C are all false claims about
this specific snippet); the real problem is architectural: storage lookup and business logic sit
directly in the Controller, which should be a thin layer delegating to a Service and Repository.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q5)*

## Q6. Service Layer Validation Reuse

**Question:**
```java
public class TicketService {
    public Ticket issueTicket(IssueTicketRequestDTO request) {
        Gate gate = gateRepository.findById(request.getGateId())
                .orElseThrow(() -> new IllegalArgumentException("Gate not found"));
        if (gate.getGateType() != GateType.ENTRY) {
            throw new InvalidGateException("Cannot issue a ticket at an exit gate");
        }
        // ... builds and saves the ticket ...
    }
}
```
A second, completely separate `AdminController` is added later, and it calls
`ticketService.issueTicket(...)` directly (it does not go through the original `TicketController`).
Will the "gate must be ENTRY" rule still be enforced for requests coming from `AdminController`?

**Options:**
- A. Yes — because the check lives inside `TicketService`, any caller of the Service automatically gets the same validation, regardless of which Controller invoked it
- B. No — the check lives in the Controller layer, so `AdminController` would need to reimplement it
- C. No — validation only runs when a DTO object is passed in, and `AdminController` might use different DTOs
- D. Yes, but only if `AdminController` also extends `TicketController`

**Answer: A** — The validation lives in the Service, not the Controller, so every caller of
`TicketService.issueTicket()` gets it for free. This is precisely why business logic belongs in the
Service layer: it becomes a single enforced rule regardless of how many Controllers call into it.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q6)*

## Q7. Filtered Payment Sum And Status

**Question:**
```java
int totalPaid = bill.getPayments().stream()
        .filter(p -> p.getPaymentStatus() == PaymentStatus.SUCCESS)
        .mapToInt(Payment::getAmount)
        .sum();
if (totalPaid >= bill.getAmount()) {
    bill.setBillStatus(BillStatus.PAID);
}
```
A `Bill` has `amount = 500`. Two `Payment` records exist on it: Payment1 (amount=200,
status=SUCCESS) and Payment2 (amount=300, status=FAILED). What is `totalPaid`, and what happens to
the bill's status?

**Options:**
- A. totalPaid = 500; bill is marked PAID
- B. totalPaid = 200; bill stays whatever it was before (not PAID)
- C. totalPaid = 300; bill is marked PAID
- D. totalPaid = 500; bill stays unpaid because one payment failed

**Answer: B** — The filter keeps only `SUCCESS` payments, so only Payment1's 200 counts.
`200 >= 500` is false, so the bill's status is untouched (the `if` block never runs) — it stays
whatever it already was, not explicitly set to "unpaid."
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q7)*

## Q8. Unfiltered Payment Status Bug

**Question:** A developer simplifies the paid-amount check by removing the status filter:
```java
int totalPaid = bill.getPayments().stream()
        .mapToInt(Payment::getAmount)
        .sum();
if (totalPaid >= bill.getAmount()) {
    bill.setBillStatus(BillStatus.PAID);
    freeParkingSpot(bill);
}
```
What real problem does removing the filter introduce?

**Options:**
- A. It won't compile, since `mapToInt` requires an `IntStream` as its argument
- B. It silently doubles the amount charged to the customer
- C. A bill could be marked PAID (and its spot freed) even though an online payment attempt actually FAILED, since failed payments now count toward the total
- D. Cash payments would stop being counted entirely

**Answer: C** — Without the `SUCCESS` filter, a `FAILED` payment's amount still gets summed, so a
bill can cross the paid threshold and get marked `PAID` (freeing the spot) purely from failed
payment attempts — a real correctness and revenue bug, not a compile error (A is false) or a
doubling/undercounting bug (B, D are false).
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q8)*

## Q9. Definition Of Critical Section

**Question:** In multithreaded code, what is a "critical section"?

**Options:**
- A. Any method that is allowed to throw a checked exception
- B. The part of a method that only constructs new objects (no shared state)
- C. The part of a Controller responsible for converting a model into a response DTO
- D. A piece of code, operating on shared data, that must never be executing simultaneously in more than one thread at a time

**Answer: D** — This is the standard definition: a critical section is the specific region of code
touching shared mutable state that requires mutual exclusion. A, B, and C describe unrelated
concepts (exception declarations, object construction, DTO mapping) with no inherent connection to
concurrency.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q9)*

## Q10. Race Condition Double Claim

**Question:**
```java
public boolean tryClaim(ParkingSpot spot) {
    if (spot.getStatus() == SpotStatus.EMPTY) {   // read
        spot.setStatus(SpotStatus.OCCUPIED);      // write
        return true;
    }
    return false;
}
```
Two threads run this method concurrently on the same `spot` object, which starts with
`status = EMPTY`, with no synchronization at all. Both threads happen to reach the `if` check
before either thread reaches the `setStatus` line. What is the realistic outcome?

**Options:**
- A. Both threads see EMPTY at their read, and both proceed to set the status and return `true` — the spot gets "claimed" twice
- B. Only one thread's `if` check passes; the JVM automatically blocks the second thread's read until the first thread finishes
- C. The final status ends up back at EMPTY, since the two writes cancel out
- D. A `ConcurrentModificationException` is thrown, and neither thread returns `true`

**Answer: A** — This is the canonical check-then-act race condition: with no synchronization, both
threads can read `EMPTY` before either writes `OCCUPIED`, so both pass the check and both return
`true` — a double claim on one physical spot. The JVM provides no automatic blocking (B is false),
writes don't "cancel out" (C is false), and no exception is thrown by this code (D is false).
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q10)*

## Q11. Ineffective Per-Call Lock Object

**Question:** A developer attempts to fix a race condition like this:
```java
public boolean tryClaim(ParkingSpot spot) {
    Object lock = new Object();   // created fresh, every single call
    synchronized (lock) {
        if (spot.getStatus() == SpotStatus.EMPTY) {
            spot.setStatus(SpotStatus.OCCUPIED);
            return true;
        }
        return false;
    }
}
```
If two threads call `tryClaim(spot)` on the same `spot` object at nearly the same time, does this
actually prevent both from succeeding?

**Options:**
- A. Yes — any `synchronized` block prevents concurrent access, regardless of which object is used as the lock
- B. No — `lock` is a brand-new object on every call, so each thread synchronizes on a DIFFERENT object and never actually blocks the other
- C. Yes, but only the first two times the method is called
- D. No — this code fails to compile, since `synchronized` requires a `static final` lock object

**Answer: B** — A `synchronized` block only excludes threads that lock on the *same* object
instance. Since `lock` is instantiated fresh inside the method on every call, two concurrent
invocations each get their own private lock object and never actually contend — the synchronization
is a no-op in practice. A is false (the lock object identity is exactly what matters); C is
nonsensical; D is false (`synchronized` works with any object reference, no such requirement exists).
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q11)*

## Q12. Instance-Level Lock Not Shared

**Question:**
```java
public class SpotAllotter {
    private final Object lock = new Object();

    public boolean tryClaim(ParkingSpot spot) {
        synchronized (lock) {
            if (spot.getStatus() == SpotStatus.EMPTY) {
                spot.setStatus(SpotStatus.OCCUPIED);
                return true;
            }
            return false;
        }
    }
}
```
Two different threads call `tryClaim()`, but each thread is working with its own,
separately-constructed `SpotAllotter` instance (`new SpotAllotter()` was called twice, instead of
both threads sharing one instance). Does `lock` still protect against both threads claiming the
same spot?

**Options:**
- A. Yes — `lock` is declared `final`, so it's automatically shared across all instances
- B. Yes — Java merges fields with the same name across different instances of a class
- C. No — each `SpotAllotter` instance has its own separate `lock` object, so two different instances mean two different locks that never block each other
- D. No — `synchronized` blocks stop working once more than one thread is involved, regardless of instances

**Answer: C** — `final` only means the field reference can't be reassigned after construction; it
says nothing about sharing across instances. Each `new SpotAllotter()` gets its own `lock` object, so
two separate instances mean two separate locks — no mutual exclusion between them. A and B
misunderstand what `final` and instance fields actually do; D is simply false (synchronized blocks
work correctly with multiple threads when the lock object is genuinely shared).
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q12)*

## Q13. Faithful Concurrency Test Design

**Question:** A test is written to prove that two concurrent requests for the same single resource
can't both succeed. Version 1 spins up two threads that both call a method on the exact same
request object, just with two different thread names. Version 2 spins up two threads that call the
method using two separate, independently-constructed request objects (e.g., two different `Gate`
instances) representing two different real-world entry points, competing for the same one resource.
Which version more faithfully proves that a real-world "two independent callers, one shared
resource" bug is actually fixed?

**Options:**
- A. Version 1 — using the same object for both threads is closer to how concurrent requests actually arrive
- B. Neither — thread names and object identity have no effect on whether a race condition is proven
- C. Version 1 — it uses fewer objects, so it's a simpler and therefore stronger test
- D. Version 2 — it recreates the real scenario of two distinct, independent callers competing for one resource, rather than one object being accessed by two threads in the abstract

**Answer: D** — Real concurrent requests come from independent callers (different gates, different
users) each with their own request object, not from one shared object accessed by two threads with
different names. Version 2's use of two genuinely distinct `Gate` instances is what makes the test
faithful to the actual production scenario; Version 1 tests something related but not identical.
A and C invert this reasoning; B is false since object identity is exactly the variable that
determines test fidelity here.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q13)*

## Q14. Wrong Lock Granularity Bug

**Question:** To reduce lock contention, a developer proposes locking per resource *category*
instead of one global lock:
```java
private final ConcurrentHashMap<VehicleType, Object> locksByVehicleType = new ConcurrentHashMap<>();

private Object getLockFor(VehicleType type) {
    return locksByVehicleType.computeIfAbsent(type, t -> new Object());
}

public boolean tryClaim(ParkingSpot spot, VehicleType requestedType) {
    synchronized (getLockFor(requestedType)) {
        if (spot.getStatus() == SpotStatus.EMPTY) {
            spot.setStatus(SpotStatus.OCCUPIED);
            return true;
        }
        return false;
    }
}
```
Suppose a single physical spot supports multiple vehicle types — for example, one large spot
supports both TRUCK and CAR. Thread 1 calls `tryClaim(thatSpot, VehicleType.CAR)` and Thread 2
calls `tryClaim(thatSpot, VehicleType.TRUCK)` on that exact same spot object, at nearly the same
time. What bug does this locking strategy introduce?

**Options:**
- A. The two threads lock on different `VehicleType` keys (CAR vs TRUCK), so they never block each other — both can read and claim the SAME physical spot object, causing a double assignment
- B. `ConcurrentHashMap.computeIfAbsent` throws an exception when called concurrently from two threads
- C. `getLockFor()` returns `null` the first time a new `VehicleType` is seen
- D. The code fails to compile, since `Object` cannot be used as a `ConcurrentHashMap` value type

**Answer: A** — Locking per vehicle-type is the wrong granularity because one physical spot can be
claimed under two different type keys (a spot supporting both CAR and TRUCK can be locked via
either), so two threads requesting different types never contend for the same lock even though
they're racing for the same underlying resource — reintroducing the exact double-claim bug locking
was meant to fix. B, C, and D are all false claims about `ConcurrentHashMap`'s real, well-defined
behavior.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q14 — this is the real "AI Corner"
scenario referenced in the Code Parking Lot 2 Post-Read, HackMD file `49-SyG-QptPfx.md`)*

## Q15. Correct Spot-Level Lock Behavior

**Question:** Here is a corrected claiming method that locks on the spot itself and re-checks
status inside the lock:
```java
public boolean tryClaim(ParkingSpot spot) {
    synchronized (spot) {
        if (spot.getStatus() == SpotStatus.EMPTY) {
            spot.setStatus(SpotStatus.OCCUPIED);
            return true;
        }
        return false;
    }
}
```
`spot.status` starts as EMPTY. Two threads call `tryClaim(spot)` on this exact same `spot` object
at nearly the same moment. What is guaranteed about the result?

**Options:**
- A. Both threads return `true`, since both read EMPTY before either one writes
- B. Exactly one thread returns `true` and sets the status to OCCUPIED; the other thread enters the lock afterward, sees OCCUPIED (not its earlier assumption), and returns `false`
- C. Both threads deadlock, since they both try to `synchronize` on `spot` at the same time
- D. The result is undefined and could differ depending on the JVM version

**Answer: B** — Locking on `spot` itself means both threads contend for the same lock object; one
acquires it first, sees `EMPTY`, claims it, and releases the lock. The second thread then acquires
the lock, but by that point re-reads `status` as `OCCUPIED` (not stale), so it correctly returns
`false`. This is exactly the correct, deterministic behavior a mutual-exclusion lock should
guarantee — not a race (A), not a deadlock (`synchronized` blocks waiting threads, it doesn't
deadlock two threads over one lock — C is false), and not JVM-dependent (D is false).
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q15)*

## Q16. Fix Described Isn't Fix Applied

**Question:** A code reviewer sees this comment above a class:
```java
// NOTE: Locking is currently per-VehicleType (see getLockFor()).
// A teammate mentioned that a walkthrough elsewhere shows what a
// correct per-ParkingSpot locking fix looks like, so they believe
// no further work is needed here.
public class SpotAllotter {
    private final ConcurrentHashMap<VehicleType, Object> locksByVehicleType = new ConcurrentHashMap<>();
    // ... tryClaim() still uses getLockFor(requestedType)
}
```
Given that the actual running code in this class still uses `getLockFor(requestedType)`
(per-vehicle-type locking), is the teammate's belief — that no further work is needed — correct?

**Options:**
- A. Yes — since a correct version has been described elsewhere, the bug is effectively already fixed
- B. Yes — per-vehicle-type locking is safe as long as `ConcurrentHashMap` is used
- C. No — the class shown here still uses the flawed per-vehicle-type locking strategy in its actual code; describing a correct fix elsewhere doesn't change what this class does at runtime, so the fix still needs to be implemented and verified with a real concurrency test on this class
- D. No — the real problem is that `ConcurrentHashMap` isn't thread-safe for this use case

**Answer: C** — A design discussion or walkthrough describing the correct fix has zero effect on
what compiled, running code actually does. This class's `tryClaim()` still calls
`getLockFor(requestedType)`, so it still has Q14's exact double-claim bug, regardless of what was
discussed elsewhere. A and B both wrongly treat a description as equivalent to an implementation;
D misdiagnoses the bug (`ConcurrentHashMap` itself is thread-safe — the bug is lock granularity, not
the map's thread-safety).
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Assignment, Day 131, Q16)*
