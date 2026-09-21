Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/H1MF9crufg

Pre-Reads-Backend-LLD-10 — Machine Coding - 10: Code BookMyShow 2

Context
Last session built every model, wired up JPA mappings, connected to real MySQL, and got one requirement (R9) working end to end through the command line.
This session shifts to the actual booking use case: a real Controller, real DTOs, and finally solving R10 and R11, the seat-locking race condition named twice before and deliberately left unsolved until now.
A couple of real bugs surface again this session, this time reserved SQL keywords colliding with entity names, continuing the module's running discipline of catching and fixing gaps live rather than pretending the cue card arrived perfect.
The session is built as one continuous story rather than a list of separate topics: the booking flow itself reveals where the race condition lives, which leads directly into why the obvious fix fails, which leads into the real fix, which is then proven with a real multithreaded test.
The AI Corner this session introduces something new: genuine non-determinism. Two runs of the identical prompt produce meaningfully different code, which shifts the lesson from "spot this one mistake" to "know how to catch mistakes in general."

Overview
Segment | What is covered | Concepts in play
Reserved keyword bug fixing | Why User and Show need explicit table names on MySQL, and why Seat.rowVal/colVal accidentally avoided this earlier | Database reserved words, @Entity(name = ...)
Booking Controller and DTOs | Why @Controller is wrong for a JSON API and @RestController is needed, and designing request/response DTOs that pass IDs instead of full objects | REST conventions, DTO discipline at controller boundaries
The booking flow and the race condition | Walking selection, confirmation, and payment as one flow, then tracing exactly where a naive check-then-set implementation breaks under two concurrent users | Check-then-act race conditions
Why the easy fix fails, and soft locking | Why holding one long database transaction across an entire payment flow is correct but unusable at scale, and what a soft lock (a status field standing in for a lock) actually is | Transaction scope, soft locking
Isolation levels: READ_COMMITTED vs SERIALIZABLE | Tracing why the default isolation level still allows two threads through, and how SERIALIZABLE catches the conflict by reasoning about valid one-at-a-time orderings | Database isolation levels
Why synchronized is the wrong fix | Why an in-process Java lock does nothing across multiple servers, and why it is wasteful even on a single server compared to row-level database protection | Distributed systems, lock granularity
Proving the fix with a real concurrency test | Writing a test with two genuine threads targeting the same seats, and checking for the right invariant across repeated runs | Test fidelity to a named problem
Building BookingService | Turning the full booking plan into real code: fetching entities, enforcing the R10 seat cap, applying the soft lock, calculating price, and creating a PENDING booking | Service layer construction
Autowiring and repository recall | Why @Autowired becomes required once a class has multiple constructors, and confirming which repositories already exist from the previous session | Dependency injection
AI Corner: PriceCalculator | Handing a tedious, well-specified task to AI, discovering genuinely different outputs across runs, and applying a four-question checklist to find the same underlying gap regardless of which output appeared | Verifying non-deterministic AI output against a system's real design

Why This Session Matters
Reserved-keyword collisions between an entity name and a database's own vocabulary are a real, easy-to-miss source of production startup failures, especially when a team changes databases later and inherits a table name that used to be safe.
Check-then-act race conditions are one of the most common concurrency bugs raised in system design interviews, precisely because the buggy code looks completely correct when read top to bottom and only fails under genuine concurrent load.
Understanding why "just hold one big transaction" and "just use synchronized" both fail, for different concrete reasons (connection exhaustion at scale, and no protection across multiple servers) is what separates a candidate who can name a race condition from one who can actually reason about a correct, deployable fix.
Knowing the practical difference between READ_COMMITTED and SERIALIZABLE is a genuine interview differentiator. Most candidates can say "add a lock" but very few can explain why a specific isolation level does or does not prevent a specific interleaving.
This session's AI Corner demonstrates something practically important: AI output is not deterministic, so relying on having memorized "the" mistake in one sample response is fragile. The checklist that checks contract, conventions, edge cases, and fit to the system's actual design catches the underlying gap regardless of which specific version of the code appears, which is the transferable skill.

Real-World Use Cases
Reserved-word table naming: Real ORM-backed systems regularly hit failures when an entity name coincides with a SQL keyword across different databases, which is why production teams often adopt a naming convention (plural table names, prefixed columns) specifically to sidestep this class of bug before it happens.
REST APIs returning JSON: Any public-facing API, from a payments provider to a food delivery backend, depends on returning structured data rather than rendered HTML, exactly the distinction between @Controller and @RestController covered in this session.
Seat and inventory holds during checkout: Airline booking, e-commerce checkout, and event ticketing all place a short-lived hold on the exact item selected the moment checkout begins, releasing it automatically if payment does not complete, the same mechanism as the BLOCKED status here.
SERIALIZABLE isolation in financial and inventory systems: Banking transfer systems and inventory-reservation systems that cannot tolerate two conflicting writes both succeeding commonly use the strictest isolation level available specifically for the small, short-lived critical section where money or stock changes hands.
Why distributed systems cannot rely on in-process locks: Any horizontally scaled backend behind a load balancer, from ticketing platforms to ride-hailing dispatch systems, cannot use a language-level lock like Java's synchronized to protect shared data, because each server process has its own separate memory and its own separate lock.
Concurrency testing with real threads: Payment and inventory systems at any real company run dedicated concurrency tests with genuinely separate threads targeting the same resource before shipping a fix, rather than trusting that a single successful manual test proves correctness.
Verifying AI-generated code against system-specific design: An engineer reviewing an AI-suggested pricing or business-rule function checks it against the team's own data model (here, ShowSeatType) rather than accepting a generically reasonable-looking implementation, since a generic prompt has no way to know about decisions unique to one system.

Connection to the Upcoming Class
Next session implements real payment and moves bookings from PENDING to CONFIRMED, building directly on top of the BookingService.bookMovie() method completed in this session.
Next session builds the 15-minute expiry mechanism that automatically returns a BLOCKED seat to AVAILABLE if payment is never completed, closing the gap explicitly left open in this session's scope.
Next session continues through the remaining requirements not yet covered, using the same race-safe, soft-locked booking foundation built here rather than revisiting concurrency from scratch.
The @ControllerAdvice and custom exception homework from this session sets up cleaner error handling that next session's payment flow will also need.

Prerequisites from the Previous Class
The full entity set and its JPA mappings: All 12 entities, their @ManyToOne/@OneToMany(mappedBy = ...) pairings, and the enum handling (@Enumerated(EnumType.STRING), @ElementCollection) built last session are assumed working without re-explanation.
ShowSeatStatus and the BLOCKED state: ShowSeatStatus already includes AVAILABLE, UNAVAILABLE, BOOKED, and BLOCKED, with BLOCKED introduced last session specifically to represent R10's temporary hold during payment. This session uses that existing value directly rather than inventing a new one.
ShowSeatType and R12 pricing: Price lives on ShowSeatType, keyed by (Show, SeatType), not on Seat or ShowSeat directly. This session's PriceCalculator depends entirely on that earlier decision.
Repositories generated via AI, plus the one custom query: All 11 repositories from last session (including ShowRepository.findByScreen_Theatre_Region_Name) are reused without modification; only one new repository, ShowSeatTypeRepository, gets added this session.
The naming reconciliation discipline: City became Region and Ticket became Booking in the actual codebase, a reconciliation carried forward without re-derivation this session.
The AI-verification checklist: The same four-question checklist first applied to AI-generated repositories last session (matches the contract, follows conventions, handles edge cases, fits the real requirement) reappears this session applied to PriceCalculator.

Key Concept Preview
A check-then-act race condition is invisible by reading the code top to bottom. The check and the write both look individually correct; the bug only exists in the unprotected gap between them, and only shows up under genuine concurrent execution.
Soft locking is not a database lock at all. It means using an existing status field as the signal that something is claimed, so the actual database transaction protecting the check-and-set moment can be milliseconds long instead of minutes.
READ_COMMITTED only guarantees you never read data that hasn't been saved yet. It does not check whether someone else changed the row between your read and your write, which is exactly the gap a check-then-act race exploits.
SERIALIZABLE is not about running things one at a time globally. It only blocks conflicts on the exact rows two transactions actually share; two transactions touching unrelated rows still run fully in parallel.
Java's synchronized keyword only coordinates threads inside one JVM. The moment a system runs on more than one server, synchronized provides zero protection against a server sitting right next to it, because true protection has to live where the shared data actually lives: the database.

What You Will Walk Away With
Identify a reserved-keyword collision between an entity name and a database's own vocabulary, and fix it with @Entity(name = ...)
Distinguish @Controller from @RestController and explain why a JSON API needs the latter
Design request and response DTOs that pass identifiers rather than full domain objects across a controller boundary
Trace a check-then-act race condition to the exact two lines of code where it occurs
Explain why a long-held transaction across an entire payment flow is correct but unusable at production scale
Explain what a soft lock is, and why it makes the real transaction's critical section short
Contrast READ_COMMITTED and SERIALIZABLE using a concrete interleaved timeline, and explain what each does and does not protect against
Justify why synchronized fails across multiple servers, and why it is wasteful even on a single server compared to row-level isolation
Write a concurrency test using genuinely separate threads targeting the same resource, and identify the correct invariant to check across repeated runs
Build a Service method that enforces a business rule (R10's seat cap), applies a soft lock, and creates an entity in a pending state
Apply a four-question verification checklist to non-deterministic AI-generated code, and identify a gap that traces back to a system's own prior design decision (R12 and ShowSeatType)
