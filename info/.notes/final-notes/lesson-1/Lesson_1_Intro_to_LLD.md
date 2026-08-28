---
# YAML METADATA FOR LOCAL LLM
lesson_id: java-spring-lld-01-intro-lld
lesson_title: "Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems"
pathway: java-spring-lld
module: oop-foundations
difficulty: Intermediate
estimated_minutes: 45
content_status: Published
learning_outcomes:
  - Distinguish HLD (infrastructure) from LLD (code design)
  - Understand why procedural code fails to scale in large teams
  - Recognize OOP as a team and maintainability paradigm
  - Identify entities as the foundational unit of LLD design
  - Apply entity-first thinking to a concrete backend system
created_date: 2026-08-28
last_updated: 2026-08-28
has_mcq_section: true
has_coding_exercises: true
mcq_count: 10
exercise_count: 2
---

# Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems

## Concepts Covered

**System design operates at two altitudes: infrastructure and code.** High-Level Design (HLD) answers *what components exist and how they connect* — load balancers, application servers, databases, caches, message queues. It is a bird's-eye view. **Low-Level Design (LLD) answers how each component is actually written in code.** The critical realization is that infrastructure layers are themselves just software. A load balancer running on a machine is code that reads requests, routes them using an algorithm, and forwards them. A database is code handling queries, storage engines, and transactions. Once HLD has decided *what* to build, **LLD is about how we write that code well**: maintainably (someone can understand and modify it without breaking things), extensibly (new features don't require rewriting everything), and reusably (logic is not duplicated across the codebase). The difference between "code that works once" and "code that scales" is exactly what LLD teaches.

**Procedural programming and Object-Oriented programming represent two fundamentally different ways of structuring code, with profound consequences for team scalability.** In Procedural style — think of it as puppeteer and puppets — functions are the active concept, and data structs are passive. Any function anywhere in the codebase can reach into a struct's fields and modify them. A `Trip` struct with fields `driverId`, `passengerId`, and `status` can be mutated by `updateTripStatus(trip, "CANCELLED")`, by direct field assignment `trip.status = "COMPLETED"`, or by any other function that touches it. As the codebase grows to tens of thousands of lines across hundreds of files, tracing which function changed which field becomes impossible. Debugging a wrong status value means searching every file for every place that touches Trip. **In Object-Oriented style, entities are the core active concept; they own their data and their behavior.** A `Trip` object protects its own state. You don't arbitrarily set `trip.status`; you call `trip.cancelTrip()`, which enforces business rules: "Cannot cancel a completed trip." The entity encapsulates and controls what happens to its data. In a team of 100 engineers, this means the business logic for state transitions lives in exactly one place—the Trip class—not scattered across 20 functions. When a bug appears in trip cancellation, engineers know exactly where to look. This is why OOP exists: it structures code the way humans already make sense of the world (agents doing things to themselves) and scales to large teams by keeping related data and behavior together.

## Practical Backend Scenario

You are designing the core of a ride-sharing application: the `Trip` entity. A trip represents a ride from a passenger to a destination, assigned to a driver. The trip moves through states: `REQUESTED`, `ACCEPTED_BY_DRIVER`, `DRIVER_ARRIVED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`. At any point, the system must enforce business rules: a passenger can cancel only if the trip is not yet completed; a driver can only mark arrival once they have accepted the trip; once completed, nothing can change. The application runs across 15 backend servers, all stateless—they do not store trip data in memory. Every server can receive a request to update any trip, so the Trip entity must be a single source of truth that all servers can query and update. This scenario drives every design decision in this lesson: which data belongs to the entity, which methods it exposes, how it protects its invariants, and why that structure enables the system to scale horizontally without chaos.

## Practice Loop

1. **Identify the trip's state and behavior by reading the business rules.** Write down what data a Trip holds (passenger ID, driver ID, source, destination, current status, fare, etc.) and what actions it must support (accept, cancel, markArrived, complete). Do this without writing code yet.

2. **Sketch a Procedural version:** Write a `Trip` struct with public fields for all state, and a set of standalone functions (`acceptTrip()`, `cancelTrip()`, `markArrived()`) that take a Trip and modify its fields directly. Note where business rule checks would live (inside the function, not inside the Trip).

3. **Identify the scaling problem:** For your Procedural version, list all the places across the codebase where someone might call these functions or directly modify trip.status. Ask: "If trip.status is wrong, how many files do I need to check?" Recognize why this is untenable at scale.

4. **Refactor into OOP:** Move state and behavior into a `Trip` class. Write methods like `public boolean acceptTrip(String driverId) throws TripException` that enforce rules internally. Make state `private`. Ensure that business invariants (e.g., "can only accept if status is REQUESTED") are enforced by the class, not by callers.

5. **Verify encapsulation:** Write down which methods are safe to expose and which state must remain private. Ask: "Can I change the internal representation of Trip later without breaking the interface?" If yes, your encapsulation is correct. This is the hallmark of good LLD design.

## Evidence of Understanding

You can explain why scaling a team on Procedural code becomes exponentially harder as the codebase grows (everyone can modify everything, no central authority for business rules), and you can design a `Trip` entity that consolidates state ownership and enforces invariants through method contracts. You can demonstrate the difference by refactoring the same scenario from procedural to OOP and showing that the OOP version requires checking only one class for trip-state bugs. You can articulate why this matters for production systems: a 100-engineer team shipping features to millions of users depends on code that is easy to change and hard to break. Entities are that unit of trust.

## Suggested Extension

Add a `Discount` entity and a method `applyDiscount(Discount d)` to `Trip` that applies a discount code only if the trip is still in `REQUESTED` state. Extend the encapsulation to handle cascading business rules: the discount affects the fare, which must be recalculated, and the total must never go negative. Build this such that the discount logic remains isolated in the Discount class, not leaked into Trip.

---

## Reference

**Primary Sources:**
- Lecture material: "Intro to LLD for Scalable & AI-Ready Systems" (Scaler, August 2026)
- Foundational principle: Bertrand Meyer, *Object-Oriented Software Construction*, on the concept of invariant preservation
- Java implementation patterns: Joshua Bloch, *Effective Java*, Item 52 ("Refer to objects by their interfaces") and Item 17 ("Design and document for inheritance, or prohibit it")

---

<!-- MCQ_SECTION_START -->

## Multiple-Choice Questions

### Original Questions (from Assignment)

#### Q1. LLD Fundamentals

**Question:** What does LLD stand for, and what is its primary focus?

- [ ] Large Level Design — designing the overall system architecture
- [x] Low Level Design — designing how the actual code is written well
- [ ] Low Level Design — designing the network infrastructure
- [ ] Logical Level Design — designing database schemas

**Explanation:** LLD (Low Level Design) focuses on *how code is written* within each infrastructure component—maintainability, extensibility, encapsulation. It is not about network infrastructure (that is HLD) nor about database schema design in isolation.

**Lesson Connection:** Concepts Covered, Paragraph 1.

---

#### Q2. HLD Overview

**Question:** Which of the following best describes High Level Design (HLD)?

- [ ] Writing clean, maintainable code inside individual components
- [x] Defining what components exist in a system and how they connect
- [ ] Designing the internal logic of a single class
- [ ] Writing unit tests for backend services

**Explanation:** HLD is a bird's-eye view: load balancers, app servers, databases, queues, how they interact. LLD (code structure inside components) is separate.

**Lesson Connection:** Concepts Covered, Paragraph 1.

---

#### Q3. Load Balancing Role

**Question:** In a horizontally scaled system, what is the primary role of a Load Balancer?

- [ ] To store user session data across multiple servers
- [ ] To upgrade the existing server to a more powerful machine
- [x] To decide which server handles each incoming request
- [ ] To encrypt all incoming user requests before processing

**Explanation:** The load balancer sits between users and application servers, routing each request to an available server using algorithms like round-robin or least-connections. It is not responsible for session storage (that is the database layer) or encryption (separate concern) or vertical scaling.

**Lesson Connection:** Practical Backend Scenario context.

---

#### Q4. Procedural Limitations

**Question:** Which of the following is the core problem with Procedural Programming as the codebase scales?

- [ ] Procedures cannot call other procedures
- [x] Entities are passive — any procedure can read or modify any entity's data freely
- [ ] Procedural code does not support functions
- [ ] Procedural code cannot work with databases

**Explanation:** In Procedural style, data is passive and behavior is active. This creates a debugging nightmare at scale: if a field is wrong, you must search all functions everywhere that touch it. OOP solves this by centralizing behavior (methods) with data (state).

**Lesson Connection:** Concepts Covered, Paragraph 2 ("puppeteer and puppets").

---

#### Q5. OOP Entities

**Question:** In Object-Oriented Programming, what does an Entity own?

- [ ] Only its attributes (data)
- [ ] Only the functions that act on it
- [x] Both its data (what it IS) and its behaviour (what it DOES)
- [ ] References to all other entities in the system

**Explanation:** OOP bundles data and behavior together. An entity owns both; it is the unit of cohesion and control.

**Lesson Connection:** Concepts Covered, Paragraph 2.

---

#### Q6. OOP Thinking

**Question:** Which of the following code snippets represents the OOP style of thinking?

- [ ] `printStudent(student)`
- [ ] `processPayment(trip, driver, rider)`
- [x] `driver.acceptRide(trip)`
- [ ] `calculateFare(source, destination, vehicle)`

**Explanation:** `driver.acceptRide(trip)` makes the subject (driver) the active agent performing the action. This is entity-first thinking. The alternatives are procedural—the action comes from outside.

**Lesson Connection:** Concepts Covered, Paragraph 2 ("agent does things to itself").

---

### Additional Java-Specific Questions

#### Q7. Java Access Modifiers and Encapsulation

**Question:** In a Java `Trip` class representing a ride-sharing trip, which approach best ensures encapsulation and guards against accidental state corruption?

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

- [ ] Option A is better because it allows flexibility and direct access
- [x] Option B is better because it centralizes validation and enforces invariants at the single source of truth
- [ ] Both are equivalent for a small team
- [ ] Option A is better for performance; Option B is better for safety only

**Explanation:** Option A (public state) is the Procedural trap: anyone anywhere in the codebase can corrupt Trip.status. Option B enforces that *all* state transitions go through the class's logic, protecting invariants. This is especially critical in a distributed system (like Practical Backend Scenario) where multiple servers might try to update the same trip—the Trip object itself must be the arbiter of valid transitions.

**Lesson Connection:** Practice Loop, Step 4 (Refactor into OOP); Evidence of Understanding.

---

#### Q8. Inheritance vs. Composition for OOP Design

**Question:** You need to extend the `Trip` entity to handle two trip types: `LocalTrip` (within a city) and `OutstationTrip` (across cities). Both share common state (passenger, driver, status, fare) but differ in pricing logic and cancellation policies. Which approach better reflects LLD principles?

- [ ] Create a single `Trip` class and add conditional logic: `if (tripType == "outstation") { pricing logic A } else { pricing logic B }`
- [ ] Create `LocalTrip` and `OutstationTrip` as separate classes inheriting from a `Trip` base class, each overriding pricing and cancellation rules
- [x] Option B (inheritance) better separates concerns and allows each trip type to encapsulate its own rules; Option A (conditional) couples different types and makes the class fragile to new trip types
- [ ] Both are equivalent; pick based on team preference

**Explanation:** Option B avoids the "Anemic Domain Model" trap (procedural code in OOP syntax). Each entity owns its behavior. As you add `PetDeliveryTrip`, `MedicineTrip`, etc., you extend the hierarchy instead of adding more conditionals to a monolithic class. This is extensibility (core LLD goal).

**Lesson Connection:** Suggested Extension context; foreshadows Module 2 (SOLID principles, Liskov Substitution).

---

#### Q9. Stateless vs. Stateful Design in Scalable Systems

**Question:** A ride-sharing application runs across 15 backend servers, all behind a load balancer. If an individual server tries to store user session state (e.g., "Driver 123 is currently logged in") in that server's memory:

- [ ] It is efficient and reduces database load, so it is fine
- [ ] It works as long as all requests from the same driver are routed to the same server (session affinity)
- [x] It will fail when a second request from the driver lands on a different server, because that server has no knowledge of the session; the only robust solution is to externalize session state to a shared database or cache layer
- [ ] It is a problem only if the number of servers exceeds 10

**Explanation:** Horizontal scaling requires **stateless servers**—each server must be interchangeable. Any server must handle any request for any user. This constraint directly impacts LLD: you cannot have objects hoarding per-user data across request boundaries; that data must live in the Trip entity, User entity, etc., persisted in the database, not on the server.

**Lesson Connection:** Practical Backend Scenario (15 servers, stateless design); HLD→LLD bridge.

---

#### Q10. Java Final Keyword and Immutability in LLD

**Question:** You have designed a `Trip` entity and want to prevent subclasses from breaking its invariant-protection contract. Which statement is most accurate about using the `final` keyword?

```java
public final class Trip {  // final class
    private final String tripId;  // final field
    private String status;  // mutable field
    
    public Trip(String tripId) {
        this.tripId = tripId;
    }
}
```

- [ ] Using `final` everywhere is always good practice; it guarantees the class is immutable
- [ ] Using `final` on the class prevents extension, which restricts flexibility
- [x] Using `final` on the class prevents careless subclassing that might violate Trip's business rules (like invalid status transitions); using `final` on certain fields (like tripId) prevents accidental reassignment; this is a deliberate LLD design decision
- [ ] `final` is a performance optimization with no semantic value for design

**Explanation:** LLD is about intentionality. Marking `Trip` as `final` says "this entity's contract is non-negotiable; subclassing is not the extension path." Marking `tripId` as `final` says "identity does not change." This protects invariants. It is not paranoia; it is documenting design intent to the next engineer who reads the code.

**Lesson Connection:** Evidence of Understanding (encapsulation and invariant preservation); Suggested Extension (adding new trip types → use composition or marker interfaces, not inheritance).

---

<!-- MCQ_SECTION_END -->

---

<!-- EXERCISES_SECTION_START -->

## Coding Exercises

**Exercises for this lesson are structured as Maven projects with starter code, reference solutions, and JUnit 5 test suites. Each tests your understanding of encapsulation, state ownership, and the OOP paradigm shift.**

### Exercise 1: Refactor Procedural to OOP — Trip State Management

**Difficulty:** Intermediate  
**Estimated Time:** 30–40 minutes  
**Skills Tested:** Encapsulation, access modifiers, method-based state transitions, invariant enforcement

#### Overview
You are given a Procedural implementation of a `Trip` with public fields and standalone functions. Your task is to refactor it into a proper OOP entity that enforces business rules through methods. This mirrors the Practical Backend Scenario.

#### Starter Code Structure
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

#### Problem Statement
**Scenario:** A ride-sharing app manages trips. Currently, `Trip` has public fields (status, passengerId, driverId) and standalone functions handle state transitions:

```java
// BEFORE (Procedural)
public class Trip {
    public String tripId;
    public String passengerId;
    public String driverId;
    public String status = "REQUESTED";  // Mutable, no validation
}

public class TripOperations {
    public static void acceptTrip(Trip trip, String driverId) {
        trip.status = "ACCEPTED";  // No check for valid transition
    }
    public static void cancelTrip(Trip trip) {
        trip.status = "CANCELLED";  // Can cancel even if COMPLETED
    }
}
```

**Refactoring Requirements:**

1. Move `acceptTrip()` logic into `Trip.acceptTrip(String driverId)` method
2. Move `cancelTrip()` logic into `Trip.cancelTrip()` method
3. Make state `private`; expose it only through a `public String getStatus()` getter
4. Enforce these invariants inside the methods:
   - Cannot accept a trip that is not in `REQUESTED` state
   - Cannot cancel a trip if it is `COMPLETED` or `IN_PROGRESS`
   - Can only mark arrived if status is `ACCEPTED_BY_DRIVER`
   - Can only complete if status is `IN_PROGRESS`
5. Throw checked exceptions (`TripException`) for invalid transitions with descriptive messages

#### Your Implementation Should
- Define a `TripException` custom exception (extend `Exception`)
- Define `Trip` with private state and public methods for valid transitions
- Have no public setters for `status`; state changes only through methods
- Include a method `public void display()` that prints the trip state in the format: `"Trip[ID=..., Status=..., Passenger=..., Driver=...]"`

#### Test Expectations (from `TripRefactoringTest.java`)
- ✓ `acceptTrip()` changes status to `ACCEPTED_BY_DRIVER` only if current status is `REQUESTED`
- ✓ `acceptTrip()` throws `TripException` if trip is already accepted or completed
- ✓ `cancelTrip()` changes status to `CANCELLED` only if trip is not completed
- ✓ `cancelTrip()` throws `TripException` if trip is `IN_PROGRESS` or `COMPLETED`
- ✓ Reflection test: `status` field is private (not public)
- ✓ Reflection test: no public setter for `status`; only private field with getter

#### Deliverables
- A refactored `Trip.java` class with proper encapsulation
- A `TripException.java` class for domain-specific errors
- All tests passing without modification

---

### Exercise 2: Build an Entity with Business Logic — Payment Abstraction

**Difficulty:** Intermediate–Advanced  
**Estimated Time:** 45–60 minutes  
**Skills Tested:** Encapsulation, abstraction through interfaces, extension without modification, OOP design for scalability

#### Overview
The lesson introduces the idea that good LLD makes adding new features (like new payment providers) a small change, not a rewrite. This exercise has you build a clean `PaymentProcessor` entity (and interface) such that adding a new payment provider requires only one new class, not touching existing code.

#### Starter Code Structure
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

#### Problem Statement
**Scenario:** A ride-sharing app processes payments. Initially, only PhonePe is supported. The business now wants to add Razorpay and Paytm without modifying existing payment code.

**Define the Abstraction:**

1. **`PaymentProcessor` interface** with methods:
   - `public Payment processPayment(String userId, long amountInPaisa, String description) throws PaymentGatewayException`
   - `public PaymentStatus getPaymentStatus(String paymentId) throws PaymentGatewayException`
   - `public void refund(String paymentId, long amountInPaisa) throws PaymentGatewayException`

2. **`Payment` entity** (not a struct—a proper entity) with:
   - Private fields: `paymentId` (UUID), `userId`, `amountInPaisa`, `status` (PENDING, COMPLETED, FAILED, REFUNDED)
   - Method: `public void markComplete()` (only if status is PENDING)
   - Method: `public void markFailed(String reason)` (only if status is PENDING)
   - Method: `public void refund()` (only if status is COMPLETED)
   - Method: `public PaymentStatus getStatus()`
   - Business invariant: once a payment transitions to a terminal state (COMPLETED or FAILED), it cannot change

3. **`PhonePeProcessor`** implements `PaymentProcessor`:
   ```java
   public class PhonePeProcessor implements PaymentProcessor {
       @Override
       public Payment processPayment(String userId, long amountInPaisa, String description) {
           // Simulate PhonePe gateway call
           // For this exercise: if amount > 0, mark COMPLETED; otherwise fail
           Payment payment = new Payment(UUID.randomUUID().toString(), userId, amountInPaisa);
           payment.markComplete();
           return payment;
       }
       // ... other methods
   }
   ```

4. **`PaymentRegistry`** (factory pattern):
   ```java
   public class PaymentRegistry {
       private static final Map<String, PaymentProcessor> registry = new HashMap<>();
       
       static {
           registry.put("phonepe", new PhonePeProcessor());
           // registry.put("razorpay", new RazorpayProcessor());  // Add when needed
       }
       
       public static PaymentProcessor getProcessor(String providerName) throws PaymentGatewayException {
           if (!registry.containsKey(providerName)) {
               throw new PaymentGatewayException("Unknown provider: " + providerName);
           }
           return registry.get(providerName);
       }
   }
   ```

**Your Task:**

1. Complete the `Payment` entity with encapsulation and invariant checks
2. Implement `PhonePeProcessor` (logic: if amount > 0, succeed; else fail)
3. Complete `PaymentRegistry` to return the correct processor
4. Write a new `RazorpayProcessor` class (same logic as PhonePe for now) and register it
5. Verify: Adding Razorpay required only one new class and one line in PaymentRegistry—no changes to existing code (Open/Closed Principle foreshadowing)

#### Test Expectations
- ✓ Payment state transitions are guarded: cannot mark complete twice, cannot refund a failed payment
- ✓ PaymentRegistry.getProcessor("phonepe") returns a PhonePeProcessor
- ✓ PaymentRegistry.getProcessor("razorpay") returns a RazorpayProcessor (after you add it)
- ✓ PaymentRegistry.getProcessor("unknown") throws PaymentGatewayException
- ✓ Reflection test: `Payment.status` is private
- ✓ Reflection test: `Payment` has no public setter for status

#### Deliverables
- Completed `Payment.java` with proper encapsulation and business rules
- Completed `PhonePeProcessor.java` implementation
- New `RazorpayProcessor.java` implementation (mirrors PhonePe logic)
- Updated `PaymentRegistry.java` with Razorpay registered
- All tests passing without modification

#### Why This Matters
This exercise embodies the lesson's core principle: **good encapsulation + abstraction = extensibility without modification**. You have not changed existing code to add a new provider—that is the hallmark of Tier-1 LLD design and the reason teams can scale.

---

<!-- EXERCISES_SECTION_END -->

---

## How to Use This Lesson

**For Learners:**
1. Read **Concepts Covered** to understand the shift from Procedural to OOP thinking.
2. Review **Practical Backend Scenario** to ground abstractions in real systems (stateless servers, shared state).
3. Work through **Practice Loop** with pen and paper, then with code.
4. Complete the **Coding Exercises** to reinforce encapsulation and extensibility.
5. Answer **Multiple-Choice Questions** to verify your understanding gaps (especially Q7–Q10 for Java-specific nuances).

**For Instructors / Local LLM:**
- Metadata (pathway, module, difficulty, counts) supports database insertion.
- Section markers (`<!-- SECTION_START -->` / `<!-- SECTION_END -->`) enable programmatic parsing.
- MCQs have unique question IDs (`Q1` through `Q10`) for tracking.
- Exercises reference Maven project structures and test patterns consistent with your platform.
- Lesson is self-contained; no external files required for reading (exercises are separate project zips).

---

**Next Lesson:** Lesson 2 — Classes and Objects (Creating and Using Java Entities)

---

