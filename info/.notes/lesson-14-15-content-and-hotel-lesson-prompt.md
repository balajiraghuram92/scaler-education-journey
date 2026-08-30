# Prompt for Local LLM — Add Lesson 14 (SOLID), Lesson 15 (Creational Patterns), and a New Hotel Management Machine-Coding Lesson

Paste everything below this line into the local LLM as-is. All lesson content and MCQs
below were already authored by hand from the real Scaler source material — you are NOT
being asked to write new prose or invent examples. Copy everything verbatim into the
correct place in the C# code. If any step below doesn't match what you find in the actual
file, STOP and report the discrepancy instead of guessing.

---

## 0. Prerequisite check

Confirm `api/Data/JavaVerticalSeedData.cs` already has 6 modules, and that
`GetAuthoredLessonContent` already has real (non-placeholder) cases for
`"16-structural-patterns"` and `"17-behavioural-patterns-uml"`. If either is missing, first
apply, in order: `info/.notes/module-restructure-prompt.md`,
`info/.notes/lesson-16-structural-patterns-prompt.md`,
`info/.notes/lesson-17-behavioural-patterns-uml-prompt.md`,
`info/.notes/lesson-17-uml-enrichment-prompt.md`. Only then continue here.

---

## 1. Add Lesson 14 content (`"14-solid-principles"`)

Find the `"14-solid-principles"` case in `GetAuthoredLessonContent` (currently a thin
`## Key Topics` placeholder). Replace its entire returned string with:

```
"14-solid-principles" => @"# Lesson 14 — SOLID Principles for Extensible Systems

## Concepts Covered

SOLID names five instincts about code quality precisely enough to diagnose and discuss a design problem in specific terms, rather than a vague sense that ""this code is messy."" Each principle in this lesson is anchored to the same running example: a naive `Bird` class holding every bird's data and a branching `fly()` method, corrected one principle at a time.

**Single Responsibility Principle (SRP):** a code unit should have exactly one reason to change. The violation is not about length — a long method built from steps of one coherent algorithm can still respect SRP — it is specifically when the reasons a method might change are unrelated to each other. A `Bird.fly()` method with an `if/else` chain per bird type is really doing two jobs: representing a bird, and knowing how every kind of bird flies. Real-world anchor: an employee expected to simultaneously be the accountant, the IT support, and the receptionist will drop something the moment two of those unrelated responsibilities compete for attention at once.

**Open/Closed Principle (OCP):** a system should be open for extension but closed for modification — a new requirement should be met with new code, not edits to code that already worked and already has passing tests. Refactoring `Bird` into an `abstract class Bird` with an abstract `fly()` method, overridden by `Pigeon`, `Sparrow`, and `Peacock`, means adding a new bird type is a new subclass, not a new `else if` branch in a shared method. Real-world anchor: a well-designed house allows a new room to be added without demolishing the kitchen to do it.

**The Penguin Problem — the bridge from OCP to LSP:** the abstract-`fly()` refactor immediately hits a wall: a `Penguin` cannot honestly fly. Giving it an empty `fly()` body or having it `throw new UnsupportedOperationException()` both compile fine, but both are lies about the contract every other `Bird` subtype honors — client code that does `for (Bird b : birds) b.fly();` now either does nothing for a penguin (silently wrong) or crashes (a runtime surprise nothing in the type system warned about).

**Liskov Substitution Principle (LSP):** a subtype must be usable anywhere its parent type is expected, without the caller needing special-case handling, and this is about a promise being kept, not about inheritance syntax being valid — code that compiles cleanly can still violate LSP. A subclass may only make preconditions less strict (require less than the parent demanded) and postconditions more strict (guarantee at least as much as the parent promised); weakening a guarantee or demanding more up front breaks substitutability even if every method technically overrides correctly. The `Penguin.fly()` problem is exactly an LSP violation dressed up as an OCP fix: client code that loops over `List<Bird>` and calls `.fly()` on each one now needs a `Penguin`-specific `if (b.type == ""Penguin"") continue;` check to avoid a crash — the moment a caller needs a type check or a `try/catch` to safely use a subtype where its parent type was expected, LSP is broken. Real-world anchor: a ""Backend Developer"" job description promises the ability to write REST APIs — anyone hired into that role is expected to deliver on it without the team handling them differently.

**Interface Segregation Principle (ISP):** no client should be forced to depend on methods it does not use. An interface that bundles several unrelated capabilities into one contract forces every implementer to take on obligations it may not actually have — exactly the same shape of problem the Penguin hit, but at the interface level instead of the inheritance level. Real-world anchor: a fixed thali forces every customer to take the full combination of courses, whether they want all of it or not; an à la carte menu lets a customer order exactly what they need.

**Dependency Inversion Principle (DIP):** high-level modules should not depend on low-level modules — both should depend on abstractions. A class that depends directly on another concrete class is wired in a way that makes both classes harder to change independently and harder to test in isolation. Real-world anchor: a phone charger does not wire itself directly into the power plant; it plugs into a wall socket, a standard interface both sides agree to.

**Dependency Injection (not itself a SOLID letter):** a natural consequence of DIP, not a sixth principle — supplying a class's dependencies from outside rather than having the class construct them itself. Real-world anchor: a new employee joining a company is not expected to bring their own laptop and desk; the company supplies it, and the employee simply plugs in and starts working.

**Where this leads next:** by the end of the `Bird` refactor, flying has been extracted into its own `FlyingBehaviour` interface, supplied to a bird rather than hard-coded inside it — this is already a named, well-established design pattern (Strategy), the subject of the very next class, and easier to follow because this lesson builds the underlying reasoning by hand first, before the pattern is named.

## Practical Backend Scenario

A notification system started with a single class containing `if/else` branches for email, SMS, and push notifications — every new channel required editing that same tested method (an OCP violation identical in shape to the `Bird.fly()` branching problem). A separate `UserService` class was found to be simultaneously validating credentials, querying the database directly, and formatting API responses — three unrelated reasons to change bundled into one class (an SRP violation). A `PaymentProcessor` interface required every implementer to expose `refund()`, `chargeSubscription()`, and `generateInvoice()`, even though a one-time-payment provider had no concept of a subscription — forcing that implementer to throw `UnsupportedOperationException` from methods it could never honestly support (an ISP violation with the exact same ""Penguin smell"" as the `Bird` example). Fixing all three: the notification class became a `NotificationChannel` interface with one implementation per channel (OCP), `UserService` was split so authentication, persistence, and formatting each live in their own focused class (SRP), and the fat `PaymentProcessor` interface was split into `Refundable`, `SubscriptionCapable`, and `InvoiceGenerating`, each implemented only by the providers that can genuinely support it (ISP).

## Practice Loop

1. Take the `Bird` class with a branching `fly()` method; refactor it into an abstract class with one subclass per bird type, and identify the exact `Penguin`-shaped case where a subtype cannot honestly implement the forced method.
2. Rewrite the caller loop over `List<Bird>` so that it needs zero special-case type checks for any subtype — if it still needs one, the LSP violation has not actually been fixed yet.
3. Find a fat interface in any codebase (or write one deliberately) where at least one implementer throws `UnsupportedOperationException` from a required method; split it into smaller, capability-specific interfaces.
4. Take two concrete classes wired directly to each other (`new ConcreteLogger()` called directly inside a service); introduce a shared interface and inject the dependency through the constructor instead.
5. Write down, for a class you already have, exactly one sentence naming its single reason to change; if you cannot do it in one sentence, it likely violates SRP.

## Evidence of Understanding

You can recognize an SRP violation as unrelated reasons to change, not merely length. You can distinguish extending a system from modifying its existing, working code, and explain the regression risk of the latter. You can identify the ""Penguin problem"" pattern — a forced method a subtype cannot honestly implement — as the shared root of an OCP-refactor gone wrong and an LSP violation. You can restate LSP as a promise being kept (in terms of precondition/postcondition strictness) rather than a compiler-checked guarantee. You can split a fat interface using ISP and rewrite a direct concrete-to-concrete dependency using DIP, and explain why Dependency Injection is a consequence of DIP rather than a sixth principle.

## Suggested Extension

Take the `FlyingBehaviour` interface this lesson arrives at (flying extracted out of `Bird` and supplied from outside) and predict, before the next lesson, what pattern this already is and why supplying it through a constructor rather than hard-coding it inside `Bird` is itself an application of DIP.

## Self-Check (From Class Material)

**Q1.** A class is responsible for generating reports in different formats such as PDF, HTML, and CSV using a switch case with one branch per format. Adding TXT support requires modifying the class. Which SOLID principle is violated?
- A. Open/closed
- B. Liskov substitution
- C. Interface segregation
- D. Dependency inversion

**Answer: A** — Every new format requires editing the existing, already-tested switch statement instead of adding new code, the defining shape of an Open/Closed violation.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 6)*

**Q2.** In a video game, a class handles different enemy types and their behaviors. As new enemies are introduced, the developer adds a new if-else block to the same class each time. Which SOLID principle is violated?
- A. Open/closed
- B. Liskov substitution
- C. Interface segregation
- D. Dependency inversion

**Answer: A** — Same shape as the report-generator case: a new enemy type should be new code (a new class), not a new branch inside an existing method.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 9)*

**Q3.** In an inventory management system, one class handles inventory operations, generates sales reports, AND sends notifications to suppliers. Which SOLID principle is violated?
- A. Single responsibility
- B. Open/closed
- C. Liskov substitution
- D. Interface segregation

**Answer: A** — Three unrelated reasons to change (inventory logic, reporting, notifications) are bundled into one class.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 7)*

**Q4.** A class handles both user authentication (verifying credentials) and database interactions (querying, updating user records). Which SOLID principle is violated?
- A. Single responsibility
- B. Open/closed
- C. Liskov substitution
- D. Interface segregation

**Answer: A** — Authentication logic and persistence logic are two unrelated reasons to change, bundled into one class.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 3)*

**Q5.** According to the Liskov Substitution Principle, if class B is a subclass of class A, what must be true when replacing an instance of A with an instance of B?
- A. The program's execution speed must remain identical or increase
- B. The program must continue to function correctly without violating the behavioral expectations established by class A
- C. Class B must override every single public and private method defined in class A
- D. The client code must explicitly cast class B back to class A before calling any inherited methods

**Answer: B** — LSP is about behavioral substitutability: the caller must not need any special handling to safely use B wherever A was expected.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 4)*

**Q6.** Under LSP, how must a subclass handle the preconditions and postconditions established by its parent class?
- A. It must make preconditions stricter and postconditions weaker
- B. It cannot change preconditions, but it can safely remove all postconditions
- C. It can make preconditions less strict (require less) and postconditions more strict (guarantee more)
- D. It must ignore the parent class's conditions and define completely independent validation rules

**Answer: C** — A subtype may only ask for less and promise at least as much as its parent — this is the precise technical definition behind ""a promise being kept.""
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 45)*

**Q7.** Why is the Interface Segregation Principle highly relevant when designing object-oriented applications?
- A. It requires all classes to implement a single, massive interface to guarantee consistency across the application
- B. It prevents bloated interfaces from forcing subclasses to implement ""dummy"" or empty methods, which pollutes the API and misleads developers
- C. It guarantees that an application will consume less memory at runtime
- D. It dictates that interfaces should only contain private methods to secure implementation details

**Answer: B** — This is exactly the ""Penguin problem"" transplanted to interfaces: a fat interface forces implementers into dummy or exception-throwing methods they cannot honestly support.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 54)*

**Q8.** How do ISP and DIP conceptually work together in a well-architected system?
- A. DIP forces the creation of abstractions, and ISP ensures those abstractions are granular, focused, and client-specific
- B. ISP restricts the total number of interfaces allowed, while DIP forces all classes to eventually merge into a single abstract base class
- C. They inherently contradict each other; applying DIP requires violating ISP
- D. ISP solely dictates the UI layer, while DIP solely manages the database layer

**Answer: A** — DIP says depend on abstractions; ISP says make sure those abstractions are small and focused rather than fat — the two principles work at different levels of the same design decision.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 5)*

**Q9.** The Dependency Inversion Principle consists of two core parts regarding high-level and low-level modules. Which statement perfectly captures the essence of DIP?
- A. High-level modules should depend on low-level modules; both should depend on concrete details
- B. Low-level modules should inherit directly from high-level modules to invert the control flow
- C. High-level modules should not depend on low-level modules; both must depend on abstractions (like interfaces or abstract classes)
- D. Dependencies should always be instantiated globally at the very top of a source file

**Answer: C** — Both sides depend on a shared abstraction rather than one depending directly on the other's concrete implementation.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 2)*

**Q10.** Why does DIP explicitly advocate for depending on abstractions rather than concretions?
- A. Because abstract classes compile faster than concrete classes in modern languages
- B. Because it eliminates the need for unit testing, as abstractions are inherently bug-free
- C. Because concretions are volatile and change frequently, whereas abstractions represent stable business concepts
- D. Because object-oriented languages physically do not allow high-level modules to directly instantiate concrete classes

**Answer: C** — Concrete implementations (a specific database driver, a specific payment SDK) change far more often than the stable business-level contract they fulfill; depending on the stable abstraction insulates high-level code from that churn.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 11)*

**Q11.** When a system consistently violates LSP, ISP, and DIP simultaneously across a major codebase, what is the most likely structural consequence during a system redesign?
- A. High Rigidity and Fragility: changing a low-level detail forces massive cascading rewrites across high-level business logic, and code reuse becomes nearly impossible
- B. Memory Leaks: the garbage collector will consistently fail to clean up instances of classes that use inheritance
- C. Syntax Errors: the compiler will refuse to process files containing deep inheritance hierarchies
- D. Loss of Thread Safety: the application will automatically lose its ability to handle concurrent tasks

**Answer: A** — These three principles all exist to keep high-level and low-level code loosely coupled; violating all three together produces exactly the rigid, fragile, hard-to-reuse codebase SOLID as a whole is meant to prevent.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 3)*
",
```

---

## 2. Add Lesson 15 content (`"15-creational-patterns"`)

Find the `"15-creational-patterns"` case and replace its entire returned string with:

```
"15-creational-patterns" => @"# Lesson 15 — Creational Design Patterns

## Concepts Covered

A design pattern is a well-known, reusable solution to a problem that keeps showing up across different, unrelated software systems — not one person's clever idea, but a shape many engineers independently arrive at. In 1994, four authors (Gamma, Helm, Johnson, Vlissides — the ""Gang of Four"" or GoF) catalogued 23 of these. Design patterns are not separate from SOLID; they are named, reusable shapes for applying principles like SOLID to a recurring problem. This module covers the **creational** family — patterns about how and when objects get created.

**Singleton — Exactly One Shared Object:** use Singleton when a shared resource sits behind the class (a DB connection, a logger, a cache — one shared office printer beats five competing ones), or when creating the object is genuinely expensive (a DB connection setup involves real network round-trips before the first query even runs). Building one correctly, step by step: (1) make the constructor `private` so outside code cannot call `new` directly; (2) keep one `private static` field holding the single instance; (3) expose a `public static getInstance()` that creates the instance only if it doesn't exist yet, then returns it — never make the instance field itself `public`, since that removes all protection over the ""only one"" rule. **Eager loading** (`private static Instance = new Instance();`, built at class-load time) needs no locking but slows startup and locks in configuration too early; **lazy loading** (built on first `getInstance()` call) avoids that cost but introduces a real concurrency danger: two threads can both see `instance == null` at nearly the same moment and both create their own object, a race condition. The fix, **double-checked locking**, checks for null once without a lock (fast, used almost every call), and only takes the lock — then checks null *again* inside it — during the one risky moment; the inner check exists because a second thread could have been waiting for the lock while the first thread finished creating the instance, and skipping it lets two objects slip through anyway. Even correct double-checked locking has one more gap that AI-generated code frequently misses: the `instance` field must be declared `private static volatile`, because `instance = new DBConnection()` is really three steps (allocate memory, run the constructor, assign the reference) that the compiler and CPU are otherwise free to reorder — without `volatile`, a second thread could see a non-null reference pointing to a half-constructed object. Serialization is a separate hole double-checked locking does not close at all: Java deserialization rebuilds an object directly from saved bytes, skipping the private constructor and `getInstance()` entirely, which is why many engineers reach for an **enum Singleton** instead — the JVM guarantees exactly one instance, thread-safety, and serialization-safety for free. Since a Singleton always hands back the same object, tests can silently leak state between each other; a `resetInstance()` helper (not part of the original GoF pattern, added purely for testing) clears the stored instance so each test starts fresh — but must never be called from production code, since resetting a live instance while other parts of the app still hold the old one creates two competing ""shared"" objects, exactly what Singleton exists to prevent.

**Builder — Safely Constructing Objects with Many Optional Fields:** a large constructor with many same-typed parameters is easy to call with arguments silently swapped (the compiler cannot catch it), and a `Map<String, Object>` of settings makes a wrong key ""silently do nothing"" with type errors only surfacing at runtime. Builder fixes this with a nested helper class that collects values with compiler-checked chainable setters (each setter returns `this`), then performs validation and constructs the real object through a single `build()` method. Four things make a production-quality Builder: a static `getBuilder()` on the main class showing how to begin; `build()` performing real validation before constructing; every setter returning the Builder itself for fluent chaining (`.setAge(21).setName(""Naman"").build()`); and a `private` constructor on the main class so nothing can bypass the Builder's validation. Mutable fields like `List`s must be defensively copied inside `build()`, not just referenced, or the caller can mutate the ""finished"" object from outside after construction completes.

**Prototype and Registry — Copying Instead of Constructing:** manually copying an object's fields from outside the class couples the caller to every internal field name, cannot reach private fields with no setters, and forces a growing `instanceof` chain to handle subclasses (an OCP violation). Prototype fixes this with a `Prototype<T>` interface requiring `T clone()`; every subclass must override `clone()` itself and call `super(instance)`, because a child that forgets to override `clone()` silently runs its parent's clone logic and drops any fields the child added. A **Registry** is a separate `Map`-based store (`ConcurrentHashMap` for thread safety) for retrieving named prototype templates — `registry.get(""ubuntu-base"")` — where a missing key returns `null` silently, which then causes a `NullPointerException` later, on a completely different line, the moment `.clone()` runs on that `null`. The most common implementation bug is a **shallow copy trap**: copying a mutable field like a `List` by reference (`this.list = instance.list;`) leaves the original and the copy sharing the exact same underlying list, so mutating one mutates both; the fix constructs a genuinely new container from the source's contents (`new ArrayList<>(instance.list)`).

**Factory — Deciding Which Class to Instantiate:** the problem Factory solves is a decision (""which class to build"") becoming known only at runtime, from configuration or user choice. A naive `if/else` chain hardcoded inside a client (`if (provider.equals(""openai""))...`) is an OCP violation — a new provider means editing tested code — and duplicates the same decision logic anywhere else it's needed. A **Simple/Static Factory** centralizes that decision into one method (`AIServiceClientProvider.getClient(provider)`), so the client depends only on an interface. This is deliberately not the strict GoF Factory Method (which uses an abstract method overridden by subclasses, with polymorphism doing the dispatch) — the practical static-factory shape is far more common in real codebases. An **Abstract Factory** goes one level up: when a single provider must supply a *family* of related objects that must stay compatible with each other (a chat client, an embeddings client, and a moderation client that must all come from the same vendor), an `AIProviderFactory` interface groups the related creation methods together so a caller can never accidentally mix an OpenAI chat client with a Gemini moderation client. Even a well-intentioned static factory can still secretly violate OCP: if adding a new provider still means reopening `getClient()`'s `if/else` chain, it has only centralized the branching, not eliminated the extensibility problem — a **registry-backed factory** (`Map<String, Supplier<T>>`, populated via a `register(name, Constructor::new)` call from each provider's own bootstrap code) genuinely lets a different team add a new provider without ever touching the factory class itself. Java's built-in `ServiceLoader` takes this even further, discovering implementations automatically from `META-INF/services` metadata files with no shared registration code at all — this is exactly how JDBC drivers and SLF4J logging backends register themselves.

## Practical Backend Scenario

A payments platform needs exactly one shared `ConnectionPoolManager` coordinating all database connections (Singleton, built with double-checked locking and `volatile`, with a `resetInstance()` used only in its test suite). Creating a `PaymentRequest` object safely, with required fields (amount, currency) and several optional ones (idempotency key, metadata, retry policy), uses a `Builder` with a private constructor so no `PaymentRequest` can exist without passing through validation. When a new merchant account is provisioned, its default settings are cloned from a `MerchantConfigTemplate` `Prototype`, looked up by tier name (""gold"", ""silver"") from a `ConfigRegistry`, with every clone defensively copying its mutable `allowedCurrencies` list rather than sharing a reference. Finally, routing a chat completion request to OpenAI, Anthropic, or Gemini goes through a registry-backed `AIServiceClientFactory`, so integrating a fourth provider next quarter is a one-line `register()` call from that provider's own module, not an edit to the factory class.

## Practice Loop

1. Build a `DBConnection` Singleton from scratch, in order: private constructor, static field, `getInstance()`; deliberately remove `volatile` first and explain in one sentence why the code still compiles but is unsafe, then add it back.
2. Add a `resetInstance()` to your Singleton and use it in a `@BeforeEach` to prove two sequential tests don't leak state between each other.
3. Build a `Builder` for a class with at least 5 fields (2 required, 3 optional, one of them a `List`); verify the `List` is defensively copied by mutating the caller's original list after `build()` and confirming the built object is unaffected.
4. Implement `Prototype<T>` on a two-level class hierarchy (a subclass adding its own field); deliberately forget to override `clone()` on the subclass first, observe the dropped field, then fix it with `super(instance)`.
5. Refactor an `if/else` factory into a registry-backed one (`Map<String, Supplier<T>>`), and prove a new type can be registered from a separate class without touching the factory itself.

## Evidence of Understanding

You can name the two legitimate reasons to reach for Singleton and explain why double-checked locking needs two null checks and a `volatile` field. You can build a Builder with proper validation, chaining, and defensive copying, and explain why a public constructor defeats the pattern's entire purpose. You can implement Prototype correctly across a subclass hierarchy and identify the shallow-copy trap on sight. You can distinguish a Simple Factory from an Abstract Factory by whether a single object or a compatible family of objects is being created, and explain why a registry-backed factory is more genuinely extensible than a static if/else factory.

## Suggested Extension

Build a small plugin-style system where a `Registry` of `Prototype` templates is populated at startup via a registry-backed `Factory`, so that adding a new template type requires registering it from that type's own module — combining all four patterns from this lesson into one cohesive design.
",
```

## 3. Add a new Lesson: Machine Coding — Hotel Management System

Add a new lesson to `SeedModule5Lessons` (the Applied Machine Coding module), after the
existing `""23-machine-coding-contest""` entry, as a new `OrderIndex = 7` lesson:

```csharp
db.Lessons.Add(new Lesson
{
    ModuleId = moduleId,
    Slug = "24-machine-coding-hotel-management",
    Title = "Lesson 24 — Machine Coding: Hotel Management System",
    Description = "Design and implement a layered hotel booking system across four incremental stages: adding rooms, browsing availability, booking rooms, and generating invoices — Controller/DTO/Repository/Service architecture.",
    LectureNumber = 24,
    ClassDate = "TBD",
    HorstmannRef = "TBD",
    EstimatedMinutes = 180,
    IsCompleted = false,
    OrderIndex = 7,
    ContentBody = GetAuthoredLessonContent("24-machine-coding-hotel-management") ?? string.Empty
});
```

Then add this case to `GetAuthoredLessonContent`:

```
"24-machine-coding-hotel-management" => @"# Lesson 24 — Machine Coding: Hotel Management System

## Concepts Covered

This machine-coding exercise builds a Hotel Management System incrementally, across four stages, each adding one capability on top of a shared layered architecture: a **Controller** layer (accepting request DTOs and returning response DTOs), a **Service** layer (interface + implementation holding business logic), a **Repository** layer (interface + an in-memory implementation, so the domain logic stays independent of any real database), and plain **domain models** (`Room`, `User`, `Booking`, `Invoice`, `CustomerSession`) with their own enums (`RoomType`, `UserType`, `CustomerSessionStatus`) and typed exceptions (`UserNotFoundException`, `UnAuthorizedAccess`, `InvalidRoomException`). The four stages build on each other: **Add Rooms** (ADMIN-only capability to register new rooms into the system), **Get Rooms** (customers browse available rooms), **Book Rooms** (customers reserve a room, tracked through a `CustomerSession`), and **Generate Invoice** (producing a bill for a completed booking). Each stage's Controller and Service only add the one new capability the stage is named for, while reusing the Repository and domain models already established by earlier stages — this is the same incremental-milestone structure used in the OOP-4 Library Management System lab, but applied to a full request/response layered architecture instead of a single class hierarchy.

## Practical Backend Scenario

A hotel chain's booking backend separates ADMIN operations (adding rooms with a type and nightly rate) from CUSTOMER operations (browsing available rooms, filtering by type, and booking one for a date range). Every request enters through a Controller that translates an HTTP-shaped request DTO into a call on the Service layer; the Service layer enforces business rules (a `UserType` check before allowing a room to be added, a room-availability check before allowing a booking) and delegates persistence to a Repository interface, currently backed by an in-memory implementation so the whole system can be built and tested before a real database is wired in. A completed booking transitions a `CustomerSession` through its status lifecycle and becomes eligible for `Invoice` generation, which reads the booking's room rate and duration to compute the final bill.

## Practice Loop

1. Implement the **Add Rooms** stage: `RoomController`, `AddRoomRequestDto`/`AddRoomResponseDto`, `RoomService`/`RoomServiceImpl`, `RoomRepository`/`InMemoryRoomRepository`, enforcing that only an ADMIN `UserType` may add a room (throwing `UnAuthorizedAccess` otherwise).
2. Implement the **Get Rooms** stage on top of the same `Room`/`RoomRepository`: a `GetRoomsRequestDto`/`GetRoomsResponseDto` pair letting a customer browse available rooms.
3. Implement the **Book Rooms** stage: introduce `Booking`, `CustomerSession`, and `CustomerSessionStatus`; a `BookingController` accepting a `MakeBookingRequestDto` that validates the room exists (`InvalidRoomException` otherwise) and the user exists (`UserNotFoundException` otherwise) before creating a `Booking`.
4. Implement the **Generate Invoice** stage: an `Invoice` domain object and a `GenerateInvoiceRequestDto`/`GenerateInvoiceResponseDto` pair that looks up a completed `CustomerSession` (throwing `CustomerSessionNotFoundException` if it can't be found) and computes a bill from its associated `Booking` and `Room` rate.
5. Once all four stages are implemented against the same in-memory repositories, write one end-to-end test that adds a room as an ADMIN, browses it as a customer, books it, and generates its invoice — proving all four stages compose correctly through the shared Repository and domain layer.

## Evidence of Understanding

You can explain why splitting a machine-coding problem into Controller/DTO/Service/Repository layers, even for an in-memory-only implementation, keeps business logic independent of any specific persistence technology. You can justify why role-based checks (ADMIN vs. CUSTOMER) belong in the Service layer rather than the Controller. You can trace a booking's full lifecycle from `Room` creation through `CustomerSession` to `Invoice` generation, and name which typed exception fires for which specific failure case (missing room, missing user, missing session).

## Suggested Extension

Add a `CancelBooking` capability that transitions a `CustomerSession` back to an available state and updates `RoomRepository` accordingly, then extend `Invoice` generation to apply a cancellation-fee rule based on how close to the booking date the cancellation occurred.
",
```

---

## 4. What must NOT change

- Do not touch any lesson other than `14-solid-principles`, `15-creational-patterns`, and the
  new `24-machine-coding-hotel-management` addition.
- Do not modify `NeedsLessonContent`, `BackfillLessonContent`, or any other method.
- Every `"` inside all the content above is already correctly doubled (`""`) for C# verbatim
  strings — copy it exactly.
- Lesson 15 intentionally has NO Self-Check section — there is no real assessed MCQ material
  yet for Singleton/Builder/Prototype/Factory, and none should be invented. Do not add one.
- The new Hotel Management lesson also intentionally has no Self-Check section, for the same
  reason.

## 5. Exercises to attach (informational — handled separately, not part of this prompt)

9 new Java exercises have been analyzed and written to
`info/.notes/scaler-raw-notes/exercise-templates-batch4/`:
- `01-tictactoe-undo.md`, `02-tictactoe-winner-check.md` → attach under lesson `19-machine-coding-tictactoe`
- `03-boardgame-factory.md`, `04-database-factory.md` → attach under lesson `15-creational-patterns`
- `05-integrate-cloud-solid.md` → attach under lesson `14-solid-principles`
- `06-hotel-generate-invoice.md`, `07-hotel-add-rooms.md`, `08-hotel-get-rooms.md`, `09-hotel-book-rooms.md` → attach under the new lesson `24-machine-coding-hotel-management`

(Filenames are approximate — the analysis agents chose the exact slugs; match by content/topic
if a name differs slightly.)

## 6. Output format

Output the complete, updated `SeedModule5Lessons` method (with the new lesson added) AND the
complete, updated `GetAuthoredLessonContent` method body, ready to paste over the existing
methods in `api/Data/JavaVerticalSeedData.cs`.

After the code block, report:
- Confirmation Lesson 14 and Lesson 15 content was replaced (not appended to the old
  placeholder).
- Confirmation the new Hotel Management lesson was added to `SeedModule5Lessons` with
  `OrderIndex = 7` and a matching `GetAuthoredLessonContent` case.
- Any discrepancy encountered.

## 7. Self-check before you output

1. Lesson 14 has exactly 11 self-check questions, Q1–Q11, no duplicates.
2. Lesson 15 and the new Hotel Management lesson each have exactly 5 sections (no
   Self-Check): Concepts Covered, Practical Backend Scenario, Practice Loop, Evidence of
   Understanding, Suggested Extension.
3. Every `"` inside all new content is doubled (`""`), not single or backslash-escaped.
4. No lesson outside 14, 15, and the new Hotel Management lesson was touched.
5. The new lesson's slug does not collide with any existing slug in the file.

## 8. Operational note

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN ('14-solid-principles', '15-creational-patterns');
```

The new Hotel Management lesson needs no reset since it's being created fresh. Then
rebuild/restart the API.
