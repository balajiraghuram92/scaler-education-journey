<!--
================================================================================
LESSON 1 - INTRO TO LLD FOR SCALABLE & AI-READY SYSTEMS
Neuralascent Editorial Platform - Java/Spring Low-Level Design Module
================================================================================

LOCAL_LLM_PARSING_GUIDE:
This file contains FOUR distinct sections:

1. METADATA_BLOCK (YAML)
   Location: Lines 1-22 (after this comment)
   Purpose: Database fields (pathway, module, difficulty, content_status, etc.)
   Destination: Lesson metadata table
   Action: Parse YAML, populate lesson attributes

2. CHAPTER_BODY (Core Teaching Content)
   Location: Lines 24-230 (after metadata, between markers)
   Markers: <!-- CHAPTER_BODY_START --> to <!-- CHAPTER_BODY_END -->
   Purpose: The actual lesson students read
   Destination: Lesson.ContentBody (database)
   Structure: # Title, ## Concepts Covered, ## Practical Backend Scenario,
              ## Practice Loop, ## Evidence of Understanding, ## Suggested Extension
   Action: Extract everything between markers AS-IS, insert into ContentBody

3. SUPPLEMENTARY_CONTENT (MCQs, Exercises, Resources)
   Location: Lines 232+ (after CHAPTER_BODY)
   Markers: Each section (MCQ, EXERCISE, RESOURCE) has explicit markers
   Purpose: Extended learning and assessment
   Destination: Separate database tables (questions, exercises, resources)
   Action: Parse by section type, extract structured data

4. MANIFEST (Inventory of all supplementary content)
   Location: This comment section
   Current inventory:
   - MCQ_COUNT: 13 (Q1-Q6 assignment main questions, Q7-Q10 additional provided MCQs, Q11-Q12 assignment additional problems, Q13 LLM-generated)
   - EXERCISE_COUNT: 3 (EX1 procedural-to-oop, EX2 payment-abstraction, EX3 anemic-model-refactor)
   - EXTERNAL_ZIP_COUNT: 3 (referenced, not embedded)
   - RESOURCE_COUNT: 3 (further reading, reference materials)

SOURCE_TYPE LEGEND (applies to all MCQ and EXERCISE blocks):
   FROM_MATERIAL  — derived directly from provided source files (lectures, notes, assignment files)
   LLM_GENERATED  — added by the LLM based on lesson topics; not from a specific source provided

EXTRACTION WORKFLOW FOR LOCAL_LLM:
1. Parse YAML metadata → Store lesson attributes
2. Extract CHAPTER_BODY (between markers) → Validate 6-section structure → Insert to ContentBody
3. Extract MCQs (between MCQ markers) → Create Question records with QUESTION_ID (Q1-Q13)
4. Extract Exercises (between EXERCISE markers) → Create Exercise records with EXERCISE_ID (EX1-EX3)
5. Validate external references (zips) exist before linking
6. Update Lesson.ContentStatus = "Published"

CRITICAL: Chapter body must be extracted cleanly without metadata or supplementary sections.
================================================================================
-->

---
# METADATA BLOCK (DATABASE FIELDS)

lesson_id: java-spring-lld-01-intro-lld
lesson_title: "Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems"
lesson_order: 1

pathway_id: java-spring-lld
pathway_name: "Java Low-Level Design & Spring Architecture"

module_id: oop-foundations
module_name: "OOP Foundations & Entities"
module_order: 1

difficulty: Intermediate
estimated_minutes: 45
content_status: Published

learning_outcomes:
  - "Distinguish HLD (infrastructure) from LLD (code design)"
  - "Understand why procedural code fails to scale in large teams"
  - "Recognise OOP as a team and maintainability paradigm, not just a syntax choice"
  - "Identify the Anemic Domain Model as the most common OOP anti-pattern in Spring codebases"
  - "Identify entities as the foundational unit of LLD design"
  - "Apply entity-first thinking to a concrete backend system"

created_date: "2026-08-28"
last_updated: "2026-08-28"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 13
  has_coding_exercises: true
  exercise_count: 3
  has_further_reading: true
  resource_count: 3

---

<!-- CHAPTER_BODY_START: This is the core lesson content. Extract everything between START and END markers (inclusive of headers) for Lesson.ContentBody database field. -->

# Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems

## Concepts Covered

System design operates at two altitudes: infrastructure and code. High-Level Design (HLD) answers *what components exist and how they connect* — load balancers, application servers, databases, caches, message queues. It is a bird's-eye view of the system, deliberately silent on internals. **Low-Level Design (LLD) answers how each component is actually written in code.** The critical realization is that every infrastructure layer is itself just software. A load balancer is code that reads requests, applies a routing algorithm (round-robin, least-connections, ip-hash), and forwards them. A database (PostgreSQL, MySQL, MongoDB) is code that handles query parsing, storage engines, indexing, and transaction management. Once HLD has decided *what* to build, **LLD governs how we write that code: maintainably** (a teammate can read, modify, and extend it without breaking adjacent behaviour), **extensibly** (new requirements don't trigger rewrites of existing logic), and **reusably** (a payment abstraction written once plugs into checkout, refunds, and subscriptions without duplication). The gap between "adding a new payment provider takes a day" and "it takes three weeks and introduces two regressions" is entirely an LLD question, not an infrastructure one.

In Procedural style, functions are the active concept and data structs are passive — the puppeteer and the puppets. A `Trip` struct with fields `driverId`, `passengerId`, and `status` can be mutated by `updateTripStatus(trip, "CANCELLED")`, by direct assignment `trip.status = "COMPLETED"`, or by any function across the entire codebase that holds a reference to it. As the system grows across hundreds of files and dozens of engineers, tracing which function corrupted a status field becomes an investigation, not a lookup. OOP resolves this by making entities the primary cognitive unit — a `Trip` object owns its state and exposes controlled methods that enforce business rules at the point where the data lives:

```java
// Procedural — any caller anywhere mutates state directly
tripStruct.status = "CANCELLED";   // no validation, no rule enforcement

// OOP — the entity owns and enforces its own state transitions
public void cancelTrip() throws TripException {
    if ("IN_PROGRESS".equals(status) || "COMPLETED".equals(status)) {
        throw new TripException("Cannot cancel trip in state: " + status);
    }
    this.status = "CANCELLED";
}
```

The business logic for every state transition lives in exactly one place — the `Trip` class — which is exactly where you look when a status bug lands in production. One pattern to watch for: the **Anemic Domain Model** — classes that contain only getters and setters with all business logic pushed into a `TripService` or `TripManager`. This is procedural code wearing Java syntax. The service becomes the puppeteer; the entity becomes the puppet. `TripService.markCancelled(Trip t, String reason)` is functionally identical to `updateTripStatus(trip, "CANCELLED")` with a longer name. Real OOP keeps behaviour close to the data it governs: state transitions belong in the entity, not in a service class that reaches into it. Service classes coordinate across entities; entities govern their own state.

## Practical Backend Scenario

A passenger requests a ride and a driver accepts. While the driver is en route, the passenger attempts to cancel. In the procedural codebase, three different service functions — `CancellationService`, `NotificationService`, and `FareService` — each reach directly into the `Trip` struct to read and compare `status`. When a race condition under concurrent load corrupts the field, the bug trace spans three files and pulls in four engineers to determine which write landed last. In the OOP design, `Trip.cancelTrip()` is the single method that reads, validates, and writes `status`. All three service functions call it. A `TripException` is thrown if the cancel violates a business rule (trip is already `IN_PROGRESS`); the caller handles that exception at its own boundary. When the same concurrency bug surfaces, the trace ends in one method in one class. This single design decision — state transitions belong to the entity — shapes every choice that follows: which fields stay `private`, what the method signatures expose to callers, and how callers handle invalid transitions. The application runs stateless across 15 backend servers; any server can receive the cancel request. The `Trip` entity persisted in the shared database is the single source of truth, and its method contracts are what prevent concurrent writes from producing incoherent state.

## Practice Loop

1. **Identify state and behaviour from the business rules.** Write down what data a `Trip` holds (passenger ID, driver ID, source, destination, current status, fare) and what actions it must support (`acceptTrip`, `cancelTrip`, `markArrived`, `complete`). Do this without code — you are naming the entity's responsibility boundary before a single line is written.

2. **Sketch a procedural version.** Write a `Trip` struct with public fields for all state and a set of standalone functions (`acceptTrip(Trip t, String driverId)`, `cancelTrip(Trip t)`, `markArrived(Trip t)`) that take a `Trip` and modify its fields directly. Put business rule checks inside the functions, not inside the struct.

3. **Count your blast radius.** For the procedural version, count every line across the codebase — service functions, HTTP handlers, notification callbacks, utility helpers — that reads or writes `trip.status` directly. Write down the total. That number is how many files you must inspect when a status bug appears in production at 3am. If it exceeds single digits, OOP's encapsulation has already paid for itself before you write a single class.

4. **Refactor into OOP.** Move state and behaviour into a `Trip` class. Write methods like `public void cancelTrip() throws TripException` that enforce rules internally. Make state `private`. Ensure business invariants — "cannot cancel a completed trip", "cannot mark arrived unless accepted" — are enforced by the class, not by callers.

5. **Verify encapsulation.** Write down which methods are safe to expose as `public` and which state must remain `private`. Ask: "Can I change the internal representation of `Trip` — switching from a `String` status to an enum — without changing any caller?" If yes, encapsulation is correct. That substitution question is the hallmark of good LLD design.

## Evidence of Understanding

You can explain why scaling a team on procedural code becomes exponentially harder as the codebase grows — any function can modify any entity's state, so there is no single authoritative location for business rules — and you can design a `Trip` entity that consolidates state ownership and enforces invariants through method contracts. You can demonstrate the difference by refactoring the same scenario from procedural to OOP, showing that the OOP version requires checking exactly one class for trip-state bugs. You can identify an Anemic Domain Model in a Spring codebase — a class with only getters/setters and a `Service` class holding all logic — and articulate why it recreates the procedural problem in Java syntax. You can articulate why this matters at scale: a 100-engineer team shipping features to millions of users depends on code that is easy to change and hard to break, and entities with encapsulated behaviour are the unit of that trust.

## Suggested Extension

Add a `Discount` entity and a method `applyDiscount(Discount d)` to `Trip` that applies a discount code only if the trip is still in `REQUESTED` state and the discount has not already been applied. Build this such that discount validation logic stays in `Discount`, fare recalculation stays in `Trip`, and neither class knows about the other's internal representation — only the method contract crosses the boundary.

---

Reference: Lecture material — "Intro to LLD for Scalable & AI-Ready Systems" (Scaler, August 2026)

<!-- CHAPTER_BODY_END: End of core lesson content for Lesson.ContentBody field. -->

---

<!-- MCQ_SECTION_START: Multiple-Choice Questions (Assessment). Extract each QUESTION_BLOCK separately. -->

## Multiple-Choice Questions

**SUPPLEMENTARY_CONTENT_TYPE: MCQ**
**SECTION_PURPOSE: Assessment and concept verification**
**DESTINATION: questions table (one record per MCQ)**

---

### QUESTION_BLOCK_START: Q1

**QUESTION_ID:** Q1
**QUESTION_TITLE:** LLD Fundamentals
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
What does LLD stand for, and what is its primary focus?

**OPTIONS:**
- [ ] A: Large Level Design — designing the overall system architecture
- [x] B: Low Level Design — designing how the actual code is written well
- [ ] C: Low Level Design — designing the network infrastructure
- [ ] D: Logical Level Design — designing database schemas

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
LLD (Low Level Design) focuses on *how code is written* within each infrastructure component — maintainability, extensibility, encapsulation. It is not about network infrastructure (that is HLD) nor about database schema design in isolation.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1

**KEYWORDS:** HLD, LLD, code design, infrastructure

### QUESTION_BLOCK_END: Q1

---

### QUESTION_BLOCK_START: Q2

**QUESTION_ID:** Q2
**QUESTION_TITLE:** HLD Overview
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
Which of the following best describes High Level Design (HLD)?

**OPTIONS:**
- [ ] A: Writing clean, maintainable code inside individual components
- [x] B: Defining what components exist in a system and how they connect
- [ ] C: Designing the internal logic of a single class
- [ ] D: Writing unit tests for backend services

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
HLD is a bird's-eye view: load balancers, app servers, databases, queues, how they interact. LLD (code structure inside components) is separate.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1

**KEYWORDS:** HLD, components, system architecture

### QUESTION_BLOCK_END: Q2

---

### QUESTION_BLOCK_START: Q3

**QUESTION_ID:** Q3
**QUESTION_TITLE:** Load Balancing Role
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
In a horizontally scaled system, what is the primary role of a Load Balancer?

**OPTIONS:**
- [ ] A: To store user session data across multiple servers
- [ ] B: To upgrade the existing server to a more powerful machine
- [x] C: To decide which server handles each incoming request
- [ ] D: To encrypt all incoming user requests before processing

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The load balancer sits between users and application servers, routing each request to an available server using algorithms like round-robin or least-connections. It is not responsible for session storage (that is the database layer) or encryption (a separate concern) or vertical scaling.

**LESSON_CONNECTION:** Practical Backend Scenario context

**KEYWORDS:** load balancer, horizontal scaling, routing

### QUESTION_BLOCK_END: Q3

---

### QUESTION_BLOCK_START: Q4

**QUESTION_ID:** Q4
**QUESTION_TITLE:** Procedural Limitations
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
Which of the following is the core problem with Procedural Programming as the codebase scales?

**OPTIONS:**
- [ ] A: Procedures cannot call other procedures
- [x] B: Entities are passive — any procedure can read or modify any entity's data freely
- [ ] C: Procedural code does not support functions
- [ ] D: Procedural code cannot work with databases

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
In Procedural style, data is passive and behaviour is active. This creates a debugging nightmare at scale: if a field is wrong, you must search every function everywhere that touches it. OOP solves this by centralising behaviour (methods) with data (state) inside the entity.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (puppeteer and puppets)

**KEYWORDS:** procedural, scalability, debugging, state management

### QUESTION_BLOCK_END: Q4

---

### QUESTION_BLOCK_START: Q5

**QUESTION_ID:** Q5
**QUESTION_TITLE:** OOP Entities
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
In Object-Oriented Programming, what does an Entity own?

**OPTIONS:**
- [ ] A: Only its attributes (data)
- [ ] B: Only the functions that act on it
- [x] C: Both its data (what it IS) and its behaviour (what it DOES)
- [ ] D: References to all other entities in the system

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
OOP bundles data and behaviour together. An entity owns both; it is the unit of cohesion and control. This ownership is what enables invariant enforcement at the point where the data lives.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2

**KEYWORDS:** OOP, entity, encapsulation, data, behavior

### QUESTION_BLOCK_END: Q5

---

### QUESTION_BLOCK_START: Q6

**QUESTION_ID:** Q6
**QUESTION_TITLE:** OOP Thinking
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
Which of the following code snippets represents the OOP style of thinking?

**OPTIONS:**
- [ ] A: `printStudent(student)`
- [ ] B: `processPayment(trip, driver, rider)`
- [x] C: `driver.acceptRide(trip)`
- [ ] D: `calculateFare(source, destination, vehicle)`

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
`driver.acceptRide(trip)` makes the subject (driver) the active agent performing the action. This is entity-first thinking. The alternatives are procedural — the action comes from outside the entity, not from the entity itself.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (entity as active agent)

**KEYWORDS:** OOP thinking, entity, method call, active agent

### QUESTION_BLOCK_END: Q6

---

### QUESTION_BLOCK_START: Q7

**QUESTION_ID:** Q7
**QUESTION_TITLE:** Java Access Modifiers and Encapsulation
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
In a Java `Trip` class representing a ride-sharing trip, which approach best ensures encapsulation and guards against accidental state corruption?

```java
// Option A
public class Trip {
    public String status;  // accessible from anywhere
    public void updateStatus(String newStatus) {
        this.status = newStatus;  // no validation
    }
}

// Option B
public class Trip {
    private String status;  // only Trip can access
    public void updateStatus(String newStatus) throws InvalidStatusException {
        if (isValidTransition(this.status, newStatus)) {
            this.status = newStatus;
        } else {
            throw new InvalidStatusException(...);
        }
    }
}
```

**OPTIONS:**
- [ ] A: Option A is better because it allows flexibility and direct access
- [x] B: Option B is better because it centralises validation and enforces invariants at the single source of truth
- [ ] C: Both are equivalent for a small team
- [ ] D: Option A is better for performance; Option B is better for safety only

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Option A (public state) is the Procedural trap in Java syntax: anyone anywhere in the codebase can corrupt `Trip.status`. Option B enforces that *all* state transitions go through the class's logic, protecting invariants. This is especially critical in a distributed system (like the Practical Backend Scenario) where multiple servers might try to update the same trip — the `Trip` object must be the single arbiter of valid transitions.

**LESSON_CONNECTION:** Practice Loop, Step 4 (Refactor into OOP); Evidence of Understanding

**KEYWORDS:** Java, access modifiers, private, encapsulation, invariants

### QUESTION_BLOCK_END: Q7

---

### QUESTION_BLOCK_START: Q8

**QUESTION_ID:** Q8
**QUESTION_TITLE:** Inheritance vs. Composition for OOP Design
**DIFFICULTY:** Medium-Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
You need to extend the `Trip` entity to handle two trip types: `LocalTrip` (within a city) and `OutstationTrip` (across cities). Both share common state (passenger, driver, status, fare) but differ in pricing logic and cancellation policies. Which approach better reflects LLD principles?

**OPTIONS:**
- [ ] A: Create a single `Trip` class and add conditional logic: `if (tripType == "outstation") { pricing logic A } else { pricing logic B }`
- [x] B: Create `LocalTrip` and `OutstationTrip` as separate classes inheriting from a `Trip` base class, each overriding pricing and cancellation rules
- [ ] C: Option B (inheritance) is better because it separates concerns and allows each trip type to encapsulate its own rules; Option A (conditional) couples different types and makes the class fragile to new trip types
- [ ] D: Both are equivalent; pick based on team preference

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Option B avoids the "Anemic Domain Model" trap (procedural code in OOP syntax). Each entity owns its behaviour. As you add `PetDeliveryTrip`, `MedicineTrip`, etc., you extend the hierarchy instead of adding more conditionals to a monolithic class. This is extensibility — a core LLD goal — in practice.

**LESSON_CONNECTION:** Suggested Extension context; foreshadows Module 2 (SOLID principles, Liskov Substitution)

**KEYWORDS:** Java, inheritance, composition, domain model, extensibility

### QUESTION_BLOCK_END: Q8

---

### QUESTION_BLOCK_START: Q9

**QUESTION_ID:** Q9
**QUESTION_TITLE:** Stateless vs. Stateful Design in Scalable Systems
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
A ride-sharing application runs across 15 backend servers, all behind a load balancer. If an individual server tries to store user session state (e.g., "Driver 123 is currently logged in") in that server's memory:

**OPTIONS:**
- [ ] A: It is efficient and reduces database load, so it is fine
- [ ] B: It works as long as all requests from the same driver are routed to the same server (session affinity)
- [x] C: It will fail when a second request from the driver lands on a different server, because that server has no knowledge of the session; the only robust solution is to externalise session state to a shared database or cache layer
- [ ] D: It is a problem only if the number of servers exceeds 10

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
Horizontal scaling requires **stateless servers** — each server must be interchangeable. Any server must handle any request for any user. This constraint directly impacts LLD: you cannot have objects hoarding per-user data across request boundaries; that data must live in the `Trip` entity, `User` entity, etc., persisted in the database, not on the server.

**LESSON_CONNECTION:** Practical Backend Scenario (15 servers, stateless design); HLD→LLD bridge

**KEYWORDS:** stateless, scalability, horizontal scaling, session state, distributed systems

### QUESTION_BLOCK_END: Q9

---

### QUESTION_BLOCK_START: Q10

**QUESTION_ID:** Q10
**QUESTION_TITLE:** Java Final Keyword and Immutability in LLD
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
You have designed a `Trip` entity and want to prevent subclasses from breaking its invariant-protection contract. Which statement is most accurate about using the `final` keyword?

```java
public final class Trip {  // final class
    private final String tripId;  // final field
    private String status;  // mutable field

    public Trip(String tripId) {
        this.tripId = tripId;
    }
}
```

**OPTIONS:**
- [ ] A: Using `final` everywhere is always good practice; it guarantees the class is immutable
- [ ] B: Using `final` on the class prevents extension, which restricts flexibility
- [x] C: Using `final` on the class prevents careless subclassing that might violate Trip's business rules (like invalid status transitions); using `final` on certain fields (like tripId) prevents accidental reassignment; this is a deliberate LLD design decision
- [ ] D: `final` is a performance optimisation with no semantic value for design

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
LLD is about intentionality. Marking `Trip` as `final` says "this entity's contract is non-negotiable; subclassing is not the extension path." Marking `tripId` as `final` says "identity does not change." This protects invariants. It is not paranoia; it is documenting design intent to the next engineer who reads the code.

**LESSON_CONNECTION:** Evidence of Understanding (encapsulation and invariant preservation); Suggested Extension

**KEYWORDS:** Java, final keyword, immutability, invariants, design intent

### QUESTION_BLOCK_END: Q10

---

### QUESTION_BLOCK_START: Q11

**QUESTION_ID:** Q11
**QUESTION_TITLE:** Paradigm Choice as a Constraint-Driven Decision
**DIFFICULTY:** Medium-Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
Consider the following two systems:

* **System A:** A real-time trading engine processing millions of transactions per second, written in C, where every microsecond of latency matters and a team of 5 engineers maintains it full-time.
* **System B:** An e-commerce platform with 200+ engineers, frequent feature additions, complex business logic, and new payment/shipping integrations every quarter.

Which paradigm is most appropriate for each, and why?

**OPTIONS:**
- [ ] A: System A → OOP, because it has a small team; System B → Procedural, because it has more engineers
- [x] B: System A → Procedural, because performance is the critical constraint and the team is small enough to manage it; System B → OOP, because maintainability, extensibility, and team collaboration are the critical constraints
- [ ] C: Both systems should use OOP because OOP is always better than procedural
- [ ] D: Both systems should use procedural because it performs better in all cases

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Paradigm choice is a constraint-driven engineering decision, not a philosophical preference. C's performance characteristics — no GC pauses, predictable memory layout, zero-cost abstractions, direct hardware access — matter when microseconds are the competitive unit. For a 5-engineer team on stable, latency-critical code, OOP's team-scalability benefits (encapsulation, extensibility, polymorphism) carry overhead — both runtime and cognitive — that the problem cannot tolerate. For System B, the engineering constraint is 200 engineers shipping concurrent features without stepping on each other's code; OOP's boundaries and method contracts provide exactly that structure. Choosing OOP for System A would introduce dispatch overhead and abstraction layers into code where every clock cycle counts; choosing Procedural for System B would scatter business logic across hundreds of functions with no ownership, making the codebase increasingly unmaintainable as the team and feature set grow.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (trade-offs of paradigm choice); Practical Backend Scenario

**KEYWORDS:** paradigm choice, performance, maintainability, trade-offs, team scalability, C, Java

### QUESTION_BLOCK_END: Q11

---

### QUESTION_BLOCK_START: Q12

**QUESTION_ID:** Q12
**QUESTION_TITLE:** OOP vs Procedural — The Philosophical Shift
**DIFFICULTY:** Medium-Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
A junior engineer argues: *"OOP and Procedural are basically the same thing — in both, you have data and functions. OOP just puts them together in a class. It is just a syntactic difference."* Which response most accurately addresses this argument?

**OPTIONS:**
- [ ] A: The junior engineer is correct — OOP and Procedural are functionally identical, just with different syntax
- [ ] B: The junior engineer is wrong — OOP does not use functions at all, whereas Procedural does
- [x] C: The junior engineer is partially right about grouping, but misses the fundamental shift: in Procedural, procedures are the core active concept and entities are passive data; in OOP, entities become the core active concept, owning both their data and their behaviour, and controlling what can be done to them — this is a philosophical shift in how you structure and reason about an entire system
- [ ] D: The junior engineer is wrong — OOP is only about inheritance and polymorphism, not about grouping data and functions

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The junior engineer has identified a syntactic similarity but missed the semantic shift. In Procedural, the procedure is the primary cognitive unit — you think "what do I do to this data?" In OOP, the entity is the primary cognitive unit — you think "what is this entity responsible for?" In Procedural, `cancelTrip(trip)` is a free-floating concern that any module can invoke or duplicate. In OOP, `trip.cancelTrip()` is the Trip entity's declared responsibility — one canonical location, one authority over that state transition. As team size scales, the procedural model produces a codebase where the same business rule exists in multiple places with slight variations; the OOP model produces a codebase where each business rule has a known owner. The junior engineer will feel this distinction concretely by year 3 on a large product team.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (philosophical shift, not syntactic); Evidence of Understanding

**KEYWORDS:** OOP vs Procedural, philosophical shift, entity ownership, team scalability, cognitive model

### QUESTION_BLOCK_END: Q12

---

### QUESTION_BLOCK_START: Q13

**QUESTION_ID:** Q13
**QUESTION_TITLE:** Recognising the Anemic Domain Model in a Spring Codebase
**DIFFICULTY:** Medium-Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A Spring backend for a payment platform has a `Payment` class with `private` fields and only public getters and setters, and a `PaymentService` class containing `validatePayment(Payment p)`, `applyDiscount(Payment p, Discount d)`, and `markComplete(Payment p, String newStatus)`. A senior engineer in code review comments: *"This is procedural code dressed in Java syntax."* Which analysis is most accurate?

**OPTIONS:**
- [ ] A: The engineer is wrong — using classes with `private` fields and a separate service class qualifies as OOP by definition
- [x] B: The engineer is correct — `Payment` has no behaviour; all business logic lives in `PaymentService`, making `Payment` an anemic data container that external functions operate on, recreating the exact Procedural problem OOP was designed to solve
- [ ] C: The engineer is partially right — the fix is to merge `PaymentService` into `Payment` as static methods
- [ ] D: The engineer is wrong — Spring service classes are a standard architectural pattern and are not procedural by nature

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the Anemic Domain Model anti-pattern. A class with only getters/setters and no behaviour is functionally identical to a C struct — it is passive data that external procedures manipulate. `PaymentService.markComplete(Payment p, String newStatus)` is `updatePaymentStatus(payment, "COMPLETE")` with a different name. Moving all logic into a service class means any code with a reference to `PaymentService` can perform any operation on any `Payment` — no different from a procedure reaching into a struct. The fix: move state-transition methods into `Payment` itself — `payment.markComplete()`, `payment.applyDiscount(Discount d)`, `payment.refund()` — where they enforce business invariants ("cannot mark complete twice", "cannot apply discount to a cancelled payment"). `PaymentService` still exists but coordinates workflows across entities; it delegates state transitions to the entity rather than performing them directly. Service classes coordinate; entities govern.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (Anemic Domain Model callout); Evidence of Understanding

**KEYWORDS:** anemic domain model, Spring, service layer, OOP anti-pattern, encapsulation, Martin Fowler

### QUESTION_BLOCK_END: Q13

---

<!-- MCQ_SECTION_END -->

---

<!-- EXERCISES_SECTION_START: Coding Exercises (Practical Application). Extract each EXERCISE_BLOCK separately. -->

## Coding Exercises

**SUPPLEMENTARY_CONTENT_TYPE: CODING_EXERCISE**
**SECTION_PURPOSE: Hands-on practice with encapsulation and extensibility**
**DESTINATION: exercises table (one record per exercise)**
**NOTE:** Exercises are provided as separate Maven project zips (see EXTERNAL_REFERENCES below)

---

### EXERCISE_BLOCK_START: EX1

**EXERCISE_ID:** EX1
**EXERCISE_TITLE:** Refactor Procedural to OOP — Trip State Management
**DIFFICULTY:** Intermediate
**BLOOM_LEVEL:** Application
**ESTIMATED_TIME_MINUTES:** 30
**SOURCE_TYPE:** LLM_GENERATED

**SKILLS_TESTED:**
- Encapsulation
- Access modifiers (private, public)
- Method-based state transitions
- Invariant enforcement
- Exception handling

**SCENARIO:**
A ride-sharing app manages trips. Currently, `Trip` has public fields (status, passengerId, driverId) and standalone functions handle state transitions.

**STARTER_CODE_STRUCTURE:**
```
exercises/exercise-01-procedural-to-oop/
├── pom.xml                          (Maven config, Java 11+, JUnit 5)
├── README.md                        (problem statement)
├── src/main/java/
│   ├── Trip.java                   (STARTER: Procedural struct-like class; YOU refactor)
│   └── TripOperations.java         (STARTER: Standalone functions; YOU move logic to Trip)
└── src/test/java/
    └── TripRefactoringTest.java    (HIDDEN: Tests Trip's invariants)
```

**REFACTORING_REQUIREMENTS:**
1. Move `acceptTrip()` logic into `Trip.acceptTrip(String driverId)` method
2. Move `cancelTrip()` logic into `Trip.cancelTrip()` method
3. Make state `private`; expose it only through `public String getStatus()` getter
4. Enforce these invariants inside the methods:
   - Cannot accept a trip that is not in `REQUESTED` state
   - Cannot cancel a trip if it is `COMPLETED` or `IN_PROGRESS`
   - Can only mark arrived if status is `ACCEPTED_BY_DRIVER`
   - Can only complete if status is `IN_PROGRESS`
5. Throw checked exceptions (`TripException`) for invalid transitions with descriptive messages

**IMPLEMENTATION_CHECKLIST:**
- [ ] Define a `TripException` custom exception (extend `Exception`)
- [ ] Define `Trip` with private state and public methods for valid transitions
- [ ] No public setters for `status`; state changes only through methods
- [ ] Include a method `public void display()` that prints trip state

**TEST_EXPECTATIONS:**
- ✓ `acceptTrip()` changes status to `ACCEPTED_BY_DRIVER` only if current status is `REQUESTED`
- ✓ `acceptTrip()` throws `TripException` if trip is already accepted or completed
- ✓ `cancelTrip()` changes status to `CANCELLED` only if trip is not completed
- ✓ `cancelTrip()` throws `TripException` if trip is `IN_PROGRESS` or `COMPLETED`
- ✓ Reflection test: `status` field is private (not public)
- ✓ Reflection test: no public setter for `status`

**DELIVERABLES:**
- Refactored `Trip.java` class with proper encapsulation
- `TripException.java` class for domain-specific errors
- All tests passing without modification

**LEARNING_CONNECTION:** Concepts Covered (Paragraph 2), Practice Loop (Steps 2-5), Evidence of Understanding

**EXTERNAL_RESOURCE:** exercises-lesson-01-ex01-procedural-to-oop.zip

### EXERCISE_BLOCK_END: EX1

---

### EXERCISE_BLOCK_START: EX2

**EXERCISE_ID:** EX2
**EXERCISE_TITLE:** Build an Entity with Business Logic — Payment Abstraction
**DIFFICULTY:** Intermediate-Advanced
**BLOOM_LEVEL:** Application + Synthesis
**ESTIMATED_TIME_MINUTES:** 45
**SOURCE_TYPE:** LLM_GENERATED

**SKILLS_TESTED:**
- Encapsulation
- Abstraction through interfaces
- Extension without modification (Open/Closed Principle foreshadowing)
- Factory pattern
- OOP design for scalability

**SCENARIO:**
A ride-sharing app processes payments. Initially, only PhonePe is supported. The business now wants to add Razorpay and Paytm without modifying existing payment code.

**STARTER_CODE_STRUCTURE:**
```
exercises/exercise-02-payment-abstraction/
├── pom.xml
├── README.md
├── src/main/java/
│   ├── PaymentProcessor.java           (STARTER: Interface contract; you define methods)
│   ├── PhonePeProcessor.java           (STARTER: One implementation)
│   ├── Payment.java                    (STARTER: Entity: amount, status, paymentId)
│   ├── PaymentGatewayException.java    (STARTER: Custom exception)
│   └── PaymentRegistry.java            (STARTER: Factory; you complete it)
└── src/test/java/
    ├── PaymentProcessorTest.java       (HIDDEN: Tests interface contract)
    └── PaymentRegistryTest.java        (HIDDEN: Tests extensibility)
```

**INTERFACE_DEFINITION:**
```java
public interface PaymentProcessor {
    public Payment processPayment(String userId, long amountInPaisa, String description)
        throws PaymentGatewayException;
    public PaymentStatus getPaymentStatus(String paymentId) throws PaymentGatewayException;
    public void refund(String paymentId, long amountInPaisa) throws PaymentGatewayException;
}
```

**IMPLEMENTATION_REQUIREMENTS:**

1. **`Payment` entity** (not a struct — a proper entity) with:
   - Private fields: `paymentId` (UUID), `userId`, `amountInPaisa`, `status` (PENDING, COMPLETED, FAILED, REFUNDED)
   - Method: `public void markComplete()` (only if status is PENDING)
   - Method: `public void markFailed(String reason)` (only if status is PENDING)
   - Method: `public void refund()` (only if status is COMPLETED)
   - Method: `public PaymentStatus getStatus()`
   - Business invariant: once a payment transitions to terminal state (COMPLETED or FAILED), it cannot change

2. **`PhonePeProcessor`** implements `PaymentProcessor`:
   - Simulate PhonePe gateway call: if amount > 0, mark COMPLETED; otherwise fail
   - Implement all interface methods

3. **`PaymentRegistry`** (factory pattern):
   - Store implementations in a static Map
   - `public static PaymentProcessor getProcessor(String providerName)` throws exception for unknown provider
   - Initially register PhonePe

4. **`RazorpayProcessor`** (you create):
   - Mirrors PhonePe logic (same simulation for now)
   - Register in PaymentRegistry

**IMPLEMENTATION_CHECKLIST:**
- [ ] Complete `Payment` entity with encapsulation and invariant checks
- [ ] Implement `PhonePeProcessor` (if amount > 0, succeed; else fail)
- [ ] Complete `PaymentRegistry` to return correct processor
- [ ] Write new `RazorpayProcessor` class
- [ ] Register Razorpay in PaymentRegistry (1 line only)
- [ ] Verify: Adding Razorpay required only one new class + one registration line

**TEST_EXPECTATIONS:**
- ✓ Payment state transitions are guarded: cannot mark complete twice, cannot refund a failed payment
- ✓ PaymentRegistry.getProcessor("phonepe") returns PhonePeProcessor
- ✓ PaymentRegistry.getProcessor("razorpay") returns RazorpayProcessor (after you add it)
- ✓ PaymentRegistry.getProcessor("unknown") throws PaymentGatewayException
- ✓ Reflection test: `Payment.status` is private
- ✓ Reflection test: `Payment` has no public setter for status

**DELIVERABLES:**
- Completed `Payment.java` with proper encapsulation and business rules
- Completed `PhonePeProcessor.java` implementation
- New `RazorpayProcessor.java` implementation
- Updated `PaymentRegistry.java` with Razorpay registered
- All tests passing without modification

**WHY_THIS_MATTERS:**
This exercise embodies the lesson's core principle: **good encapsulation + abstraction = extensibility without modification**. Adding a new provider required exactly one new class and one registration line — that is the hallmark of Tier-1 LLD design and the reason teams can scale.

**LEARNING_CONNECTION:** Practical Backend Scenario (stateless servers, single source of truth), Suggested Extension (isolate discount logic), foreshadows Module 2 (SOLID principles, Open/Closed Principle)

**EXTERNAL_RESOURCE:** exercises-lesson-01-ex02-payment-abstraction.zip

### EXERCISE_BLOCK_END: EX2

---

### EXERCISE_BLOCK_START: EX3

**EXERCISE_ID:** EX3
**EXERCISE_TITLE:** Identify and Refactor an Anemic Domain Model — Order Processing
**DIFFICULTY:** Intermediate-Advanced
**BLOOM_LEVEL:** Analysis + Application
**ESTIMATED_TIME_MINUTES:** 40
**SOURCE_TYPE:** LLM_GENERATED

**SKILLS_TESTED:**
- Identifying the Anemic Domain Model anti-pattern
- Distinguishing entity governance from service coordination
- Moving business logic from Service to Entity
- Encapsulation with private state
- Invariant enforcement through method contracts

**SCENARIO:**
A Spring e-commerce backend has an `Order` class with public getters and setters (no behaviour) and an `OrderService` class containing `validateOrder(Order o)`, `applyPromoCode(Order o, String code)`, `cancelOrder(Order o, String reason)`, and `markShipped(Order o, String trackingId)`. The codebase has identified this as an Anemic Domain Model, and you are tasked with the refactor.

**STARTER_CODE_STRUCTURE:**
```
exercises/exercise-03-anemic-model-refactor/
├── pom.xml                           (Maven config, Java 11+, JUnit 5)
├── README.md                         (problem statement)
├── src/main/java/
│   ├── Order.java                   (STARTER: Anemic class — only getters/setters; YOU refactor)
│   ├── OrderService.java            (STARTER: Overloaded service; YOU redistribute logic)
│   ├── PromoCode.java               (PROVIDED: Represents a discount code with validity rules)
│   └── OrderException.java         (PROVIDED: Domain exception)
└── src/test/java/
    └── OrderRefactoringTest.java    (HIDDEN: Tests entity behaviour and invariants)
```

**REFACTORING_REQUIREMENTS:**
1. Move `cancelOrder()` logic into `Order.cancel(String reason)` — enforces "cannot cancel an order that is already SHIPPED or CANCELLED"
2. Move `applyPromoCode()` logic into `Order.applyPromoCode(PromoCode code)` — enforces "cannot apply to a CANCELLED order", "cannot apply the same code twice", updates total fare accordingly
3. Move `markShipped()` logic into `Order.markShipped(String trackingId)` — enforces "cannot ship an order that has not been paid"
4. Leave `validateOrder()` in `OrderService` — it orchestrates across entities (inventory check, fraud check) and belongs at the coordination layer, not in the entity
5. Make all state fields `private`; expose only through getters and the business methods above
6. Throw `OrderException` with descriptive messages for all invalid transitions

**IMPLEMENTATION_CHECKLIST:**
- [ ] `Order.cancel(String reason)` enforces correct pre-conditions
- [ ] `Order.applyPromoCode(PromoCode code)` validates applicability and updates total
- [ ] `Order.markShipped(String trackingId)` validates payment status before shipping
- [ ] `OrderService.validateOrder()` still exists and coordinates across entities but does not mutate `Order` state directly
- [ ] No public setter for `status` on `Order`
- [ ] All business rule checks live inside `Order`, not in callers

**TEST_EXPECTATIONS:**
- ✓ `Order.cancel()` changes status to CANCELLED only if order is not already SHIPPED or CANCELLED
- ✓ `Order.cancel()` throws `OrderException` if called on a SHIPPED order
- ✓ `Order.applyPromoCode()` throws `OrderException` if the same code is applied twice
- ✓ `Order.applyPromoCode()` throws `OrderException` if the order is CANCELLED
- ✓ `Order.markShipped()` throws `OrderException` if order has not been paid
- ✓ Reflection test: `Order.status` is private
- ✓ Reflection test: no public `setStatus()` method on `Order`
- ✓ `OrderService.validateOrder()` still exists but does not directly write to `Order` fields

**DELIVERABLES:**
- Refactored `Order.java` with business methods and private state
- Updated `OrderService.java` that delegates state transitions to `Order` and retains only coordination logic
- All tests passing without modification

**WHY_THIS_MATTERS:**
This exercise targets the most prevalent OOP anti-pattern in production Spring codebases. The Anemic Domain Model is not obvious from code structure alone — it *looks* like OOP because it uses classes and `private` fields. Getting comfortable distinguishing "what the entity governs" from "what the service coordinates" is the design intuition that shows up in architecture discussions and code reviews at senior and staff level.

**LEARNING_CONNECTION:** Concepts Covered, Paragraph 2 (Anemic Domain Model callout); Q13; Evidence of Understanding; foreshadows Module 2 (Single Responsibility Principle)

**EXTERNAL_RESOURCE:** exercises-lesson-01-ex03-anemic-model-refactor.zip

### EXERCISE_BLOCK_END: EX3

---

<!-- EXERCISES_SECTION_END -->

---

<!-- FURTHER_READING_SECTION_START: Optional supplementary resources for deeper learning. -->

## Further Reading & Resources

**SUPPLEMENTARY_CONTENT_TYPE: LEARNING_RESOURCE**
**SECTION_PURPOSE: Extend understanding beyond core lesson**
**DESTINATION: resources table (optional, not required)**

---

### RESOURCE_BLOCK_START: RESOURCE_1

**RESOURCE_ID:** RESOURCE_1
**RESOURCE_TYPE:** BookChapter
**RESOURCE_TITLE:** Object-Oriented Software Construction — Invariant Preservation
**AUTHOR:** Bertrand Meyer
**SOURCE:** *Object-Oriented Software Construction*, 2nd Edition, Chapter 11

**READING_LEVEL:** Advanced
**TIME_ESTIMATE_MINUTES:** 45

**RELEVANCE:**
Provides deep theoretical foundation for why encapsulation and invariant preservation matter in OOP design. Explains the Contract model (preconditions, postconditions, invariants) that underlies all the Trip entity design in this lesson.

**KEY_CONCEPTS:**
- Design by Contract
- Class invariants and their preservation
- Method preconditions and postconditions
- Why contracts enable team scalability

**RELATIONSHIP_TO_LESSON:**
Directly supports "Evidence of Understanding" section (invariant preservation as the hallmark of good LLD).

### RESOURCE_BLOCK_END: RESOURCE_1

---

### RESOURCE_BLOCK_START: RESOURCE_2

**RESOURCE_ID:** RESOURCE_2
**RESOURCE_TYPE:** BookChapter
**RESOURCE_TITLE:** Effective Java — Refer to Objects by Their Interfaces
**AUTHOR:** Joshua Bloch
**SOURCE:** *Effective Java*, 3rd Edition, Item 52

**READING_LEVEL:** Intermediate
**TIME_ESTIMATE_MINUTES:** 30

**RELEVANCE:**
Explains why abstracting behind interfaces (like `PaymentProcessor`) is foundational to good Java design. Connects to Exercise 2 and foreshadows Module 2 (SOLID principles).

**KEY_CONCEPTS:**
- Interface-based design in Java
- Type contracts and substitutability
- Why implementation details should be hidden
- Benefits for testing and extensibility

**RELATIONSHIP_TO_LESSON:**
Supports Practice Loop (Step 5: "Can I change the internal representation later?") and Exercise 2 (PaymentProcessor abstraction).

### RESOURCE_BLOCK_END: RESOURCE_2

---

### RESOURCE_BLOCK_START: RESOURCE_3

**RESOURCE_ID:** RESOURCE_3
**RESOURCE_TYPE:** DocumentationReference
**RESOURCE_TITLE:** Java Language Specification — Access Modifiers
**AUTHOR:** Oracle
**SOURCE:** https://docs.oracle.com/javase/specs/jls/se17/html/jls-6.html#jls-6.6

**READING_LEVEL:** Reference
**TIME_ESTIMATE_MINUTES:** 20

**RELEVANCE:**
Official reference for Java's `private`, `protected`, `public`, and package-private modifiers. Essential for understanding Q7 (Access Modifiers and Encapsulation) and Exercise 1 (making state private).

**KEY_CONCEPTS:**
- Visibility rules for each modifier
- Package-private (default) access
- Protected access in inheritance hierarchies
- Why choosing the right modifier matters for encapsulation

**RELATIONSHIP_TO_LESSON:**
Supports Practice Loop (Step 4: "Which state must remain private?") and Q7.

### RESOURCE_BLOCK_END: RESOURCE_3

---

<!-- FURTHER_READING_SECTION_END -->

---

<!-- EXTERNAL_REFERENCES_START: Zips and files referenced in this lesson. -->

## External References & Downloadable Resources

**MANIFEST OF EXTERNAL FILES:**

| Reference ID | Type | Filename | Purpose | Size_Est | Status |
|---|---|---|---|---|---|
| ZIP_EX1 | Exercise Starter | exercises-lesson-01-ex01-procedural-to-oop.zip | Maven project: Refactor procedural to OOP | ~2 MB | Required |
| ZIP_EX2 | Exercise Starter | exercises-lesson-01-ex02-payment-abstraction.zip | Maven project: Payment abstraction with extensibility | ~2 MB | Required |
| ZIP_EX3 | Exercise Starter | exercises-lesson-01-ex03-anemic-model-refactor.zip | Maven project: Identify and refactor Anemic Domain Model | ~2 MB | Required |

**DOWNLOAD_INSTRUCTIONS:**
All exercise zips should be provided separately to the Local LLM (not embedded in this file due to size). They are referenced by filename throughout this lesson (in Exercise Blocks EX1, EX2, and EX3).

**VALIDATION:**
Before seeding this lesson into production, verify:
- [ ] `exercises-lesson-01-ex01-procedural-to-oop.zip` exists and contains starter code
- [ ] `exercises-lesson-01-ex02-payment-abstraction.zip` exists and contains starter code
- [ ] `exercises-lesson-01-ex03-anemic-model-refactor.zip` exists and contains starter code
- [ ] All pom.xml files reference Java 11+ and JUnit 5
- [ ] All include README.md with clear problem statements
- [ ] All include test suites in src/test/java/ (hidden from learners during exercise)

<!-- EXTERNAL_REFERENCES_END -->

---

## How to Use This Lesson

**For Learners:**
1. Read **Concepts Covered** to understand the shift from Procedural to OOP thinking and to recognise the Anemic Domain Model anti-pattern.
2. Review **Practical Backend Scenario** to ground the abstractions in a concrete production moment (passenger cancel during active trip).
3. Work through **Practice Loop** with pen and paper, then with code.
4. Complete the **Coding Exercises** (EX1, EX2, EX3) to reinforce encapsulation, extensibility, and the service-vs-entity boundary.
5. Answer **Multiple-Choice Questions** (Q1–Q13) to verify understanding gaps.
6. Explore **Further Reading** for deeper theoretical foundation.

**For Local LLM (Insertion Workflow):**
1. Extract YAML metadata → Populate lesson attributes (pathway, module, difficulty, etc.)
2. Extract CHAPTER_BODY (between markers) → Validate 6-section structure → Insert to `Lesson.ContentBody`
3. Extract MCQs (Q1–Q13) → Create Question records; use QUESTION_ID as primary key; note SOURCE_TYPE for review
4. Extract Exercises (EX1–EX3) → Create Exercise records; validate external zips exist; note SOURCE_TYPE for review
5. Extract Resources (RESOURCE_1–3) → Create LessonResource records (optional; omit if not needed)
6. Validate all external references (zips, URLs) are accessible
7. Update `Lesson.ContentStatus` = "Published"

---

**Next Lesson:** Lesson 2 — Classes and Objects (Creating and Using Java Entities)
