const lessonInteractions = {
  'java-spring-lld/oop-foundations/01-intro-to-lld': {
    conceptChecks: [
      {
        id: 'lesson-1-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — PROCEDURAL VS OOP',
        question:
          'Which of the following is the core problem with Procedural Programming as the codebase scales across a large engineering team?',
        options: [
          { id: 'a', label: 'A', text: 'Procedures cannot call other procedures or external libraries.' },
          { id: 'b', label: 'B', text: 'Entities are passive data structs — any procedure across the codebase can read or modify state freely without centralized invariant enforcement.' },
          { id: 'c', label: 'C', text: 'Procedural code does not support functions or memory allocation.' },
          { id: 'd', label: 'D', text: 'Procedural code cannot interact with relational databases.' }
        ],
        correctOptionId: 'b',
        explanation:
          'In Procedural style, data structs are passive puppets and external functions are active puppeteers. When an entity status is corrupted, finding the offending write requires auditing every function that touches it. Real OOP resolves this by making entities own their state and enforce their own business invariants.',
        incorrectExplanation:
          'Focus on how state is manipulated in procedural vs. object-oriented design and what happens when dozens of engineers touch the same shared struct across multiple services.',
        hint: 'Passive structs + unbounded external mutation = impossible bug tracing at scale.'
      },
      {
        id: 'lesson-1-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — THE ANEMIC DOMAIN MODEL',
        question:
          'A Spring backend has a Payment class with private fields and only getters/setters, and a PaymentService containing validatePayment(), applyDiscount(), and markComplete(). Why does this represent the Anemic Domain Model anti-pattern?',
        options: [
          { id: 'a', label: 'A', text: 'Using private fields and a separate service class violates Spring Boot conventions.' },
          { id: 'b', label: 'B', text: 'Payment has no behaviour; all business logic lives in PaymentService, reducing the entity to an anemic data struct and recreating procedural programming in Java syntax.' },
          { id: 'c', label: 'C', text: 'The fix is to merge PaymentService into Payment as static helper methods.' },
          { id: 'd', label: 'D', text: 'Service classes should always hold all state mutation rules to keep entities purely passive.' }
        ],
        correctOptionId: 'b',
        explanation:
          'An Anemic Domain Model creates classes that are merely data holders with getters and setters, while services act as external procedures manipulating them. Real OOP dictates that entities govern their own state transitions (e.g. payment.markComplete()), while service classes focus on coordinating workflows across entities.',
        incorrectExplanation:
          'Think about who owns state transitions: an entity governing its own invariants, or a service class reaching into passive getters and setters.',
        hint: 'Service classes coordinate workflows; entities govern their own internal state transitions.'
      }
    ],
    practiceQuestions: [
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-01',
        question: 'What does LLD stand for, and what is its primary focus?',
        options: [
          { id: 'a', label: 'A', text: 'Large Level Design — designing the overall system architecture' },
          { id: 'b', label: 'B', text: 'Low Level Design — designing how the actual code is written well' },
          { id: 'c', label: 'C', text: 'Low Level Design — designing the network infrastructure' },
          { id: 'd', label: 'D', text: 'Logical Level Design — designing database schemas' }
        ],
        correctOptionId: 'b',
        explanation: 'LLD (Low Level Design) focuses on how code is written within each infrastructure component — maintainability, extensibility, encapsulation. It is not about network infrastructure (that is HLD) nor about database schema design in isolation.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-02',
        question: 'Which of the following best describes High Level Design (HLD)?',
        options: [
          { id: 'a', label: 'A', text: 'Writing clean, maintainable code inside individual components' },
          { id: 'b', label: 'B', text: 'Defining what components exist in a system and how they connect' },
          { id: 'c', label: 'C', text: 'Designing the internal logic of a single class' },
          { id: 'd', label: 'D', text: 'Writing unit tests for backend services' }
        ],
        correctOptionId: 'b',
        explanation: "HLD is a bird's-eye view: load balancers, app servers, databases, queues, how they interact. LLD (code structure inside components) is separate."
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-03',
        question: 'In a horizontally scaled system, what is the primary role of a Load Balancer?',
        options: [
          { id: 'a', label: 'A', text: 'To store user session data across multiple servers' },
          { id: 'b', label: 'B', text: 'To upgrade the existing server to a more powerful machine' },
          { id: 'c', label: 'C', text: 'To decide which server handles each incoming request' },
          { id: 'd', label: 'D', text: 'To encrypt all incoming user requests before processing' }
        ],
        correctOptionId: 'c',
        explanation: 'The load balancer sits between users and application servers, routing each request to an available server using algorithms like round-robin or least-connections. It is not responsible for session storage (that is the database layer) or encryption (a separate concern) or vertical scaling.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-04',
        question: 'Which of the following is the core problem with Procedural Programming as the codebase scales?',
        options: [
          { id: 'a', label: 'A', text: 'Procedures cannot call other procedures' },
          { id: 'b', label: 'B', text: "Entities are passive — any procedure can read or modify any entity's data freely" },
          { id: 'c', label: 'C', text: 'Procedural code does not support functions' },
          { id: 'd', label: 'D', text: 'Procedural code cannot work with databases' }
        ],
        correctOptionId: 'b',
        explanation: 'In Procedural style, data is passive and behaviour is active. This creates a debugging nightmare at scale: if a field is wrong, you must search every function everywhere that touches it. OOP solves this by centralising behaviour (methods) with data (state) inside the entity.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-05',
        question: 'In Object-Oriented Programming, what does an Entity own?',
        options: [
          { id: 'a', label: 'A', text: 'Only its attributes (data)' },
          { id: 'b', label: 'B', text: 'Only the functions that act on it' },
          { id: 'c', label: 'C', text: 'Both its data (what it IS) and its behaviour (what it DOES)' },
          { id: 'd', label: 'D', text: 'References to all other entities in the system' }
        ],
        correctOptionId: 'c',
        explanation: 'OOP bundles data and behaviour together. An entity owns both; it is the unit of cohesion and control. This ownership is what enables invariant enforcement at the point where the data lives.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-06',
        question: 'Which of the following code snippets represents the OOP style of thinking?',
        options: [
          { id: 'a', label: 'A', text: 'printStudent(student)' },
          { id: 'b', label: 'B', text: 'processPayment(trip, driver, rider)' },
          { id: 'c', label: 'C', text: 'driver.acceptRide(trip)' },
          { id: 'd', label: 'D', text: 'calculateFare(source, destination, vehicle)' }
        ],
        correctOptionId: 'c',
        explanation: 'driver.acceptRide(trip) makes the subject (driver) the active agent performing the action. This is entity-first thinking. The alternatives are procedural — the action comes from outside the entity, not from the entity itself.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-07',
        question: 'In a Java Trip class representing a ride-sharing trip, which approach best ensures encapsulation and guards against accidental state corruption?',
        options: [
          { id: 'a', label: 'A', text: 'Option A is better because it allows flexibility and direct access' },
          { id: 'b', label: 'B', text: 'Option B is better because it centralises validation and enforces invariants at the single source of truth' },
          { id: 'c', label: 'C', text: 'Both are equivalent for a small team' },
          { id: 'd', label: 'D', text: 'Option A is better for performance; Option B is better for safety only' }
        ],
        correctOptionId: 'b',
        explanation: "Option A (public state) is the Procedural trap in Java syntax: anyone anywhere in the codebase can corrupt Trip.status. Option B enforces that all state transitions go through the class's logic, protecting invariants. This is especially critical in a distributed system where multiple servers might try to update the same trip — the Trip object must be the single arbiter of valid transitions."
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-08',
        question: 'You need to extend the Trip entity to handle two trip types: LocalTrip (within a city) and OutstationTrip (across cities). Both share common state (passenger, driver, status, fare) but differ in pricing logic and cancellation policies. Which approach better reflects LLD principles?',
        options: [
          { id: 'a', label: 'A', text: 'Create a single Trip class and add conditional logic: if (tripType == "outstation") { pricing logic A } else { pricing logic B }' },
          { id: 'b', label: 'B', text: 'Create LocalTrip and OutstationTrip as separate classes inheriting from a Trip base class, each overriding pricing and cancellation rules' },
          { id: 'c', label: 'C', text: 'Option B (inheritance) is better because it separates concerns and allows each trip type to encapsulate its own rules; Option A (conditional) couples different types and makes the class fragile to new trip types' },
          { id: 'd', label: 'D', text: 'Both are equivalent; pick based on team preference' }
        ],
        correctOptionId: 'b',
        explanation: 'Option B avoids the "Anemic Domain Model" trap (procedural code in OOP syntax). Each entity owns its behaviour. As you add PetDeliveryTrip, MedicineTrip, etc., you extend the hierarchy instead of adding more conditionals to a monolithic class. This is extensibility — a core LLD goal — in practice.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-09',
        question: "A ride-sharing application runs across 15 backend servers, all behind a load balancer. If an individual server tries to store user session state (e.g., \"Driver 123 is currently logged in\") in that server's memory:",
        options: [
          { id: 'a', label: 'A', text: 'It is efficient and reduces database load, so it is fine' },
          { id: 'b', label: 'B', text: 'It works as long as all requests from the same driver are routed to the same server (session affinity)' },
          { id: 'c', label: 'C', text: 'It will fail when a second request from the driver lands on a different server, because that server has no knowledge of the session; the only robust solution is to externalise session state to a shared database or cache layer' },
          { id: 'd', label: 'D', text: 'It is a problem only if the number of servers exceeds 10' }
        ],
        correctOptionId: 'c',
        explanation: 'Horizontal scaling requires stateless servers — each server must be interchangeable. Any server must handle any request for any user. This constraint directly impacts LLD: you cannot have objects hoarding per-user data across request boundaries; that data must live in the Trip entity, User entity, etc., persisted in the database, not on the server.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-10',
        question: 'You have designed a Trip entity and want to prevent subclasses from breaking its invariant-protection contract. Which statement is most accurate about using the final keyword?',
        options: [
          { id: 'a', label: 'A', text: 'Using final everywhere is always good practice; it guarantees the class is immutable' },
          { id: 'b', label: 'B', text: 'Using final on the class prevents extension, which restricts flexibility' },
          { id: 'c', label: 'C', text: "Using final on the class prevents careless subclassing that might violate Trip's business rules (like invalid status transitions); using final on certain fields (like tripId) prevents accidental reassignment; this is a deliberate LLD design decision" },
          { id: 'd', label: 'D', text: 'final is a performance optimisation with no semantic value for design' }
        ],
        correctOptionId: 'c',
        explanation: 'LLD is about intentionality. Marking Trip as final says "this entity\'s contract is non-negotiable; subclassing is not the extension path." Marking tripId as final says "identity does not change." This protects invariants. It is not paranoia; it is documenting design intent to the next engineer who reads the code.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-11',
        question: 'Consider the following two systems:\nSystem A: A real-time trading engine processing millions of transactions per second, written in C, where every microsecond of latency matters and a team of 5 engineers maintains it full-time.\nSystem B: An e-commerce platform with 200+ engineers, frequent feature additions, complex business logic, and new payment/shipping integrations every quarter.\nWhich paradigm is most appropriate for each, and why?',
        options: [
          { id: 'a', label: 'A', text: 'System A → OOP, because it has a small team; System B → Procedural, because it has more engineers' },
          { id: 'b', label: 'B', text: 'System A → Procedural, because performance is the critical constraint and the team is small enough to manage it; System B → OOP, because maintainability, extensibility, and team collaboration are the critical constraints' },
          { id: 'c', label: 'C', text: 'Both systems should use OOP because OOP is always better than procedural' },
          { id: 'd', label: 'D', text: 'Both systems should use procedural because it performs better in all cases' }
        ],
        correctOptionId: 'b',
        explanation: "Paradigm choice is a constraint-driven engineering decision, not a philosophical preference. C's performance characteristics — no GC pauses, predictable memory layout, zero-cost abstractions, direct hardware access — matter when microseconds are the competitive unit. For System B, the engineering constraint is 200 engineers shipping concurrent features without stepping on each other's code; OOP's boundaries and method contracts provide exactly that structure."
      },
      // FROM_MATERIAL
      {
        id: 'lesson-1-mcq-12',
        question: 'A junior engineer argues: "OOP and Procedural are basically the same thing — in both, you have data and functions. OOP just puts them together in a class. It is just a syntactic difference." Which response most accurately addresses this argument?',
        options: [
          { id: 'a', label: 'A', text: 'The junior engineer is correct — OOP and Procedural are functionally identical, just with different syntax' },
          { id: 'b', label: 'B', text: 'The junior engineer is wrong — OOP does not use functions at all, whereas Procedural does' },
          { id: 'c', label: 'C', text: 'The junior engineer is partially right about grouping, but misses the fundamental shift: in Procedural, procedures are the core active concept and entities are passive data; in OOP, entities become the core active concept, owning both their data and their behaviour, and controlling what can be done to them — this is a philosophical shift in how you structure and reason about an entire system' },
          { id: 'd', label: 'D', text: 'The junior engineer is wrong — OOP is only about inheritance and polymorphism, not about grouping data and functions' }
        ],
        correctOptionId: 'c',
        explanation: 'In Procedural, the procedure is the primary cognitive unit — you think "what do I do to this data?" In OOP, the entity is the primary cognitive unit — you think "what is this entity responsible for?" In Procedural, cancelTrip(trip) is a free-floating concern that any module can invoke or duplicate. In OOP, trip.cancelTrip() is the Trip entity\'s declared responsibility — one canonical location, one authority over that state transition.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-1-mcq-13',
        question: 'A Spring backend for a payment platform has a Payment class with private fields and only public getters and setters, and a PaymentService class containing validatePayment(Payment p), applyDiscount(Payment p, Discount d), and markComplete(Payment p, String newStatus). A senior engineer in code review comments: "This is procedural code dressed in Java syntax." Which analysis is most accurate?',
        options: [
          { id: 'a', label: 'A', text: 'The engineer is wrong — using classes with private fields and a separate service class qualifies as OOP by definition' },
          { id: 'b', label: 'B', text: 'The engineer is correct — Payment has no behaviour; all business logic lives in PaymentService, making Payment an anemic data container that external functions operate on, recreating the exact Procedural problem OOP was designed to solve' },
          { id: 'c', label: 'C', text: 'The engineer is partially right — the fix is to merge PaymentService into Payment as static methods' },
          { id: 'd', label: 'D', text: 'The engineer is wrong — Spring service classes are a standard architectural pattern and are not procedural by nature' }
        ],
        correctOptionId: 'b',
        explanation: 'This is the Anemic Domain Model anti-pattern. A class with only getters/setters and no behaviour is functionally identical to a C struct — it is passive data that external procedures manipulate. Real OOP dictates that entities govern their own state transitions (e.g. payment.markComplete()), while service classes coordinate workflows across entities.'
      }
    ]
  },

  'java-spring-lld/oop-foundations/02-oop-1-intro-lab': {
    conceptChecks: [
      {
        id: 'lesson-2-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — REFERENCE MODEL',
        question:
          'After `Driver d2 = d1;` followed by `d2.name = "Suresh";`, what does `System.out.println(d1.name)` print?',
        options: [
          { id: 'a', label: 'A', text: 'Rahul — d1 was assigned first and is unchanged' },
          { id: 'b', label: 'B', text: 'Suresh — both variables point to the same heap object' },
          { id: 'c', label: 'C', text: 'null — d2 points to a new empty object' },
          { id: 'd', label: 'D', text: 'A NullPointerException is thrown' }
        ],
        correctOptionId: 'b',
        explanation:
          'Assigning d2 = d1 copies the reference (the heap address), not the object. Both variables point at the same Driver on the heap, so writing to d2 is writing to d1.',
        incorrectExplanation:
          'Java reference variables hold addresses, not objects. d2 = d1 means both point to the same heap allocation — there is still only one Driver in memory.',
        hint: 'Ask yourself: after d2 = d1, how many Driver objects exist on the heap?'
      },
      {
        id: 'lesson-2-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — STATIC KEYWORD',
        question:
          'A `Driver` class has `int totalDrivers = 0;` (no `static`) and the constructor does `totalDrivers++`. After creating three Driver objects, what does `d1.totalDrivers` equal?',
        options: [
          { id: 'a', label: 'A', text: '3 — it tracks the total across all instances' },
          { id: 'b', label: 'B', text: '1 — each object has its own copy, incremented once at construction' },
          { id: 'c', label: 'C', text: '0 — instance fields are not modified by constructors' },
          { id: 'd', label: 'D', text: 'A compile error — non-static fields cannot be incremented in constructors' }
        ],
        correctOptionId: 'b',
        explanation:
          'Without `static`, every Driver object gets its own copy of `totalDrivers`. Each copy is incremented once by that object\'s constructor, ending at 1. Only `static int totalDrivers` is shared across all instances and would reach 3.',
        incorrectExplanation:
          'Instance fields belong to each object independently. `d1.totalDrivers`, `d2.totalDrivers`, and `d3.totalDrivers` are three separate integers, each holding 1. To get a shared counter, the field must be `static`.',
        hint: 'How many copies of a non-static field exist when you create three objects?'
      }
    ],
    practiceQuestions: [
      // FROM_MATERIAL
      {
        id: 'lesson-2-mcq-01',
        question: 'What does the following code print?',
        codeBlock: 'Driver d1 = new Driver();\nd1.name = "Rahul";\nDriver d2 = d1;\nd2.name = "Suresh";\nSystem.out.println(d1.name);',
        options: [
          { id: 'a', label: 'A', text: 'Rahul' },
          { id: 'b', label: 'B', text: 'Suresh' },
          { id: 'c', label: 'C', text: 'null' },
          { id: 'd', label: 'D', text: 'A NullPointerException is thrown' }
        ],
        correctOptionId: 'b',
        explanation:
          'd2 = d1 copies the reference (heap address), not the object. Both variables point at the same Driver. Writing d2.name modifies that shared object, so d1.name returns "Suresh".'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-2-mcq-02',
        question:
          'After calling `new Driver("Rahul", 4.8)` with the constructor below, what is the value of the driver\'s `name` field?',
        codeBlock: 'public Driver(String name, double rating) {\n    name = name;\n    rating = rating;\n}',
        options: [
          { id: 'a', label: 'A', text: '"Rahul" — assigned correctly' },
          { id: 'b', label: 'B', text: 'A compile error — name appears twice' },
          { id: 'c', label: 'C', text: 'null — the parameter assigned to itself, field untouched' },
          { id: 'd', label: 'D', text: '"Rahul" — Java auto-infers this.name when names match' }
        ],
        correctOptionId: 'c',
        explanation:
          'name = name reassigns the local parameter to itself — a legal no-op. The instance field this.name is never touched and stays null. The fix is this.name = name.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-2-mcq-03',
        question:
          'A `Driver` class needs a counter that tracks how many `Driver` objects have ever been created across the entire application. A developer writes this code. What is wrong with this design?',
        codeBlock: 'public class Driver {\n    int totalDrivers = 0;  // incremented in constructor\n    // ...\n}',
        options: [
          {
            id: 'a',
            label: 'A',
            text: 'Nothing — `totalDrivers` will correctly track the total across all Driver objects'
          },
          {
            id: 'b',
            label: 'B',
            text: 'Every Driver object gets its own copy of `totalDrivers`, each starting at 0; the field tracks nothing meaningful at the application level'
          },
          {
            id: 'c',
            label: 'C',
            text: 'The field will cause a compile error because counters must be declared `final`'
          },
          {
            id: 'd',
            label: 'D',
            text: 'The field is private and cannot be incremented from the constructor'
          }
        ],
        correctOptionId: 'b',
        explanation:
          'An instance field belongs to each individual object. If five Driver objects are created, there are five separate `totalDrivers` fields, each holding the value 1 (or whatever the constructor set). No single number reflects the total. The fix is `static int totalDrivers = 0` — a static field belongs to the class itself and is shared by every instance, so incrementing it in any constructor accumulates the true total.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-2-mcq-04',
        question: 'Which statement correctly describes the relationship between a class and an object in Java?',
        options: [
          { id: 'a', label: 'A', text: 'A class holds all its objects — deleting the class deletes the objects' },
          { id: 'b', label: 'B', text: 'A class is a blueprint with minimal memory; each object is a separate heap allocation created by new' },
          { id: 'c', label: 'C', text: 'A class and an object are the same thing; "object" is just informal for a class at runtime' },
          { id: 'd', label: 'D', text: 'An object is stored on the stack and the class is stored on the heap' }
        ],
        correctOptionId: 'b',
        explanation:
          'The class definition (bytecode) is the template. Each new call allocates a separate heap block for one object with its own copy of every instance field. Class and objects are independent.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-2-mcq-05',
        question: 'A Driver class has `public double rating`. Which statement is most accurate?',
        options: [
          { id: 'a', label: 'A', text: 'Acceptable — developers will know not to set invalid values' },
          { id: 'b', label: 'B', text: 'Should be protected to prevent subclass corruption' },
          { id: 'c', label: 'C', text: 'Any code anywhere can write driver.rating = 10.0; making it private with a validated setRating() is the only design that enforces the rule' },
          { id: 'd', label: 'D', text: 'Fine to keep public; a validateRating() method called by callers is sufficient' }
        ],
        correctOptionId: 'c',
        explanation:
          'Convention-based protection fails at scale. Any code with a Driver reference can write any value to a public field. Private + setRating() means the compiler rejects direct writes and the method is the single enforcement point.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-2-mcq-06',
        question: 'Which access modifier restricts a field so that only the class that declares it can read or write it?',
        options: [
          { id: 'a', label: 'A', text: 'private' },
          { id: 'b', label: 'B', text: 'protected' },
          { id: 'c', label: 'C', text: 'public' },
          { id: 'd', label: 'D', text: 'package-private (no modifier)' }
        ],
        correctOptionId: 'a',
        explanation:
          'private limits access to the declaring class only. protected allows same-package + subclasses. Package-private allows the same package. public allows everywhere.'
      },
      // FROM_MATERIAL
      {
        id: 'lesson-2-mcq-07',
        question:
          'A developer lists "four pillars of OOP: Abstraction, Encapsulation, Inheritance, Polymorphism." A senior engineer says the framing is imprecise. Which response is most accurate?',
        options: [
          { id: 'a', label: 'A', text: 'The developer is correct — all four are independent equal pillars' },
          { id: 'b', label: 'B', text: 'Abstraction is not part of OOP; it belongs to functional programming' },
          { id: 'c', label: 'C', text: 'Abstraction is the overarching principle OOP exists to implement; Encapsulation, Inheritance, and Polymorphism are the three mechanisms that achieve it' },
          { id: 'd', label: 'D', text: 'Abstraction and Encapsulation are synonyms; the real pillars are only Inheritance and Polymorphism' }
        ],
        correctOptionId: 'c',
        explanation:
          'Abstraction is the destination (represent a system as bounded ideas). The three pillars are mechanisms to get there. Treating all four as equal obscures the hierarchy.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-2-mcq-08',
        question:
          'A `Driver` object is created with `Driver d = new Driver()` using only the no-argument constructor (which has an empty body). The code then calls `System.out.println(d.name.length())`. What happens, and why?',
        options: [
          { id: 'a', label: 'A', text: 'It prints 0 — Java initializes String fields to an empty string `""`' },
          { id: 'b', label: 'B', text: 'It prints the length of the class name "Driver"' },
          {
            id: 'c',
            label: 'C',
            text: 'A NullPointerException is thrown — reference-type fields default to null, and calling `.length()` on null dereferences a null reference'
          },
          { id: 'd', label: 'D', text: 'It prints -1 — Java uses -1 to indicate an uninitialized String' }
        ],
        correctOptionId: 'c',
        explanation:
          'Java initializes unassigned instance fields to type-specific zero-equivalents: reference types (including `String`) default to `null`, not to `""`. Calling any method on a null reference throws `NullPointerException` at runtime. This is why constructors exist: to replace null defaults with real values before the object is used. The fix is either a constructor that sets `this.name` explicitly, or a null guard before the call. NullPointerException is the most common Java runtime error and almost always traces back to a field or return value that was assumed to be non-null but was not initialized.'
      }
    ]
  },

  'java-spring-lld/oop-foundations/02-oop-classes-objects': {
    get conceptChecks() {
      return lessonInteractions['java-spring-lld/oop-foundations/02-oop-1-intro-lab'].conceptChecks;
    },
    get practiceQuestions() {
      return lessonInteractions['java-spring-lld/oop-foundations/02-oop-1-intro-lab'].practiceQuestions;
    }
  },

  'java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation': {
    conceptChecks: [
      {
        id: 'lesson-3-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — COPY SEMANTICS',
        question:
          'A Trip copy constructor assigns this.route = other.route. After creating tripCopy from originalTrip, the caller invokes tripCopy.getRoute().setSource("Whitefield"). What does originalTrip.getRoute().getSource() return?',
        options: [
          { id: 'a', label: 'A', text: 'The original source — the copy owns an independent Route object' },
          { id: 'b', label: 'B', text: 'null — the Route field was cleared during copy construction' },
          { id: 'c', label: 'C', text: '"Whitefield" — both Trip objects alias the same Route heap object' },
          { id: 'd', label: 'D', text: 'A NullPointerException is thrown at the setSource call' }
        ],
        correctOptionId: 'c',
        explanation:
          'this.route = other.route copies the 64-bit reference, not the object. Both Trip variables point to the same Route in heap memory. Calling setSource() through the copy mutates that single shared object, so reading getSource() through either Trip returns "Whitefield". This is aliasing — one Route, two names.',
        incorrectExplanation:
          'There is only one Route object in heap memory after this constructor runs. Because the copy constructor used reference assignment rather than new Route(other.route), both Trip instances reach the same heap address. Any mutation through either reference affects the same object.',
        hint: 'How many Route objects exist in heap memory after the copy constructor completes?'
      },
      {
        id: 'lesson-3-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — EQUALS AND HASHCODE CONTRACT',
        question:
          'A Trip class overrides equals() to return true when two trips share the same tripId, but does NOT override hashCode(). Two distinct Trip objects, both with tripId "T-101", are added to a HashSet<Trip>. How many entries does the set contain?',
        options: [
          { id: 'a', label: 'A', text: '1 — HashSet calls equals() to detect duplicates before consulting hashCode()' },
          { id: 'b', label: 'B', text: '2 — the default hashCode uses memory identity, producing different bucket assignments; equals() is never reached' },
          { id: 'c', label: 'C', text: '0 — the broken contract throws an exception during insertion' },
          { id: 'd', label: 'D', text: 'It depends on JVM garbage-collection timing' }
        ],
        correctOptionId: 'b',
        explanation:
          'HashSet first calls hashCode() to find the bucket, then scans that bucket with equals(). The default hashCode() (from Object) is derived from memory identity — two distinct Trip objects almost always land in separate buckets. equals() is never called between them, and both trips are stored. The set size is 2, not 1.',
        incorrectExplanation:
          'HashSet does not start with equals() — it starts with hashCode(). Because hashCode() is not overridden, the two Trip objects produce different hashes and land in different buckets. equals() is only called within the same bucket, so it never compares these two trips. Both are stored.',
        hint: 'Which method does HashSet call first when deciding where to store an object?'
      }
    ],
    practiceQuestions: [
      // Q1 — FROM_MATERIAL
      {
        id: 'lesson-3-mcq-01',
        question:
          'Which access modifier makes a member accessible to subclasses in a different package, but NOT to unrelated classes in that same different package?',
        options: [
          { id: 'a', label: 'A', text: '`private`' },
          { id: 'b', label: 'B', text: 'default (no modifier)' },
          { id: 'c', label: 'C', text: '`protected`' },
          { id: 'd', label: 'D', text: '`public`' }
        ],
        correctOptionId: 'c',
        explanation:
          '`protected` grants access within the declaring package AND to subclasses in any package. An unrelated class in a different package has no access. `public` removes all restrictions and is therefore too permissive. `private` and default are both too restrictive.'
      },
      // Q2 — FROM_MATERIAL
      {
        id: 'lesson-3-mcq-02',
        question: 'In Java, where must a `this(...)` constructor call be placed within a constructor body?',
        options: [
          { id: 'a', label: 'A', text: 'Anywhere before the first field assignment' },
          { id: 'b', label: 'B', text: 'After all field assignments are complete' },
          { id: 'c', label: 'C', text: 'As the very first statement in the constructor body' },
          { id: 'd', label: 'D', text: 'Only in a constructor that takes no arguments' }
        ],
        correctOptionId: 'c',
        explanation:
          'The Java Language Specification (JLS §8.8.7) requires that both this(...) and super(...) appear as the first statement of a constructor body. The compiler enforces this at compile time — any code before this(...) is a compile error.'
      },
      // Q3 — FROM_MATERIAL
      {
        id: 'lesson-3-mcq-03',
        question:
          'What keyword designates a member as class-level in Java — shared across all instances rather than belonging to any individual object?',
        options: [
          { id: 'a', label: 'A', text: '`const`' },
          { id: 'b', label: 'B', text: '`final`' },
          { id: 'c', label: 'C', text: '`auto`' },
          { id: 'd', label: 'D', text: '`static`' }
        ],
        correctOptionId: 'd',
        explanation:
          '`static` designates a member as class-level: one copy lives in the method area regardless of how many instances exist. `const` is reserved but unused in Java. `final` makes a variable unresettable but does not make it class-level. `auto` does not exist in Java.'
      },
      // Q4 — FROM_MATERIAL
      {
        id: 'lesson-3-mcq-04',
        question:
          'A Fare class must be fully immutable — no subclass should be able to add a setter that breaks the guarantee. Which combination is required?',
        options: [
          { id: 'a', label: 'A', text: 'All fields `private` and all methods declared `final`' },
          { id: 'b', label: 'B', text: 'The class declared `final` and all fields declared `private final`' },
          { id: 'c', label: 'C', text: 'All fields `private final` and a private constructor' },
          { id: 'd', label: 'D', text: 'All fields declared `static final`' }
        ],
        correctOptionId: 'b',
        explanation:
          'Declaring the class `final` prevents subclassing — no subclass can add setters. Declaring each field `private final` prevents reassignment after construction and blocks external access. Together they form the complete immutability guarantee. `final` methods (option A) still allow a subclass to introduce entirely new setter methods. A private constructor (option C) prevents subclassing but also blocks normal external instantiation.'
      },
      // Q5 — FROM_MATERIAL
      {
        id: 'lesson-3-mcq-05',
        question:
          'A Trip copy constructor contains `this.route = other.route`. After creating tripCopy from originalTrip, the caller calls `tripCopy.getRoute().setSource("Delhi")`. What is `originalTrip.getRoute().getSource()`?',
        options: [
          { id: 'a', label: 'A', text: 'The original source — the copy owns an independent Route' },
          { id: 'b', label: 'B', text: '"Delhi" — both Trip objects reference the same Route heap object' },
          { id: 'c', label: 'C', text: 'null — the Route field was cleared during copy' },
          { id: 'd', label: 'D', text: 'A NullPointerException is thrown' }
        ],
        correctOptionId: 'b',
        explanation:
          'this.route = other.route copies the reference pointer, not the object. Both Trip variables point to the same Route in heap memory. Calling setSource("Delhi") through either reference mutates the single shared object, so reading getSource() through originalTrip also returns "Delhi".'
      },
      // Q6 — LLM_GENERATED
      {
        id: 'lesson-3-mcq-06',
        question:
          'A Trip class overrides equals() to compare by tripId but does NOT override hashCode(). Two Trip objects with tripId "T-101" are added to a HashSet<Trip>. How many entries does the set contain?',
        options: [
          { id: 'a', label: 'A', text: '0 — the broken contract causes an exception during insertion' },
          { id: 'b', label: 'B', text: '2 — the unoverridden hashCode produces different bucket assignments and equals() is never called' },
          { id: 'c', label: 'C', text: '1 — HashSet calls equals() first to detect duplicates before consulting hashCode()' },
          { id: 'd', label: 'D', text: 'It depends on JVM garbage-collection timing' }
        ],
        correctOptionId: 'b',
        explanation:
          'HashSet uses hashCode() to find the bucket before it calls equals(). The default hashCode() derives from memory identity — two distinct objects produce different hashes and land in separate buckets; equals() is never compared between them. Both trips are stored, giving a set size of 2.'
      },
      // Q7 — LLM_GENERATED
      {
        id: 'lesson-3-mcq-07',
        question: 'A Driver class declares `private final long driverId`. Which statement correctly describes how this field may be assigned?',
        options: [
          { id: 'a', label: 'A', text: 'It must be assigned in the field declaration itself; constructor assignment is not allowed' },
          { id: 'b', label: 'B', text: 'It can be assigned repeatedly from within any instance method' },
          { id: 'c', label: 'C', text: 'It can be assigned exactly once, either in a field initializer or in any constructor of the class' },
          { id: 'd', label: 'D', text: 'It is automatically assigned the default value 0L and cannot be explicitly set' }
        ],
        correctOptionId: 'c',
        explanation:
          'A final instance field must be definitely assigned before the constructor exits (JLS §8.3.1.2). Assignment can happen at the declaration site or inside any constructor body — but exactly once across the path that executes. The compiler performs definite-assignment analysis. Instance methods cannot assign a final field after construction.'
      },
      // Q8 — LLM_GENERATED
      {
        id: 'lesson-3-mcq-08',
        question: 'Why is it impossible for `this(...)` and `super(...)` to both appear explicitly in the same constructor?',
        options: [
          { id: 'a', label: 'A', text: 'The JVM only permits one parent-class initializer call per class hierarchy' },
          { id: 'b', label: 'B', text: 'Both must occupy the first statement of the constructor body — a structural impossibility in a single constructor' },
          { id: 'c', label: 'C', text: '`super(...)` is implicitly invoked after `this(...)` completes, making an explicit call redundant' },
          { id: 'd', label: 'D', text: '`this(...)` internally delegates to `super(...)`, so an explicit super call would execute it twice' }
        ],
        correctOptionId: 'b',
        explanation:
          'The JLS mandates that both this(...) and super(...) appear as the first statement of a constructor body. A constructor body has exactly one first statement, so only one can hold that slot. When this(...) is used, the delegated master constructor handles the super() call.'
      },
      // Q9 — LLM_GENERATED
      {
        id: 'lesson-3-mcq-09',
        question: 'In the code below, what does `super(vehicleId, licensePlate, 4)` accomplish?',
        codeBlock: 'public class Car extends Vehicle {\n    private static final double PER_KM_RATE = 15.0;\n\n    public Car(String vehicleId, String licensePlate) {\n        super(vehicleId, licensePlate, 4);\n    }\n\n    @Override\n    public double calculateFare(double distanceKm) {\n        return distanceKm * PER_KM_RATE;\n    }\n}',
        options: [
          { id: 'a', label: 'A', text: 'It creates a new Vehicle instance and stores it as a hidden parent field inside Car' },
          { id: 'b', label: 'B', text: "It invokes Vehicle's constructor to initialize the shared fields vehicleId, licensePlate, and capacity on the current Car object" },
          { id: 'c', label: 'C', text: 'It calls a static factory method on Vehicle that pre-configures four-seat defaults' },
          { id: 'd', label: 'D', text: "It overrides Vehicle's constructor with Car-specific behaviour" }
        ],
        correctOptionId: 'b',
        explanation:
          "There is only one object being constructed — the Car instance. super(vehicleId, licensePlate, 4) delegates initialization of inherited fields to Vehicle's constructor on that same object. No second Vehicle instance is created. This is standard inheritance delegation: shared fields live in the parent constructor, subclass-specific state and overrides live in the child."
      },
      // Q10 — LLM_GENERATED
      {
        id: 'lesson-3-mcq-10',
        question: 'After executing the three statements below in order, what is Driver.totalCount?',
        codeBlock: 'public class Driver {\n    static int totalCount = 0;\n    long id; String name; double rating; boolean isOnline;\n\n    public Driver(long id, String name, double rating, boolean isOnline) {\n        this.id = id; this.name = name;\n        this.rating = rating; this.isOnline = isOnline;\n        Driver.totalCount++;\n    }\n    public Driver(long id, String name) { this(id, name, 0.0, false); }\n    public Driver() { this(0L, "Anonymous", 0.0, false); }\n}\n\nnew Driver();\nnew Driver(1L, "Alice");\nnew Driver(2L, "Bob", 4.8, true);',
        options: [
          { id: 'a', label: 'A', text: '1 — only the master constructor is counted' },
          { id: 'b', label: 'B', text: '2 — the no-arg and partial constructors are excluded' },
          { id: 'c', label: 'C', text: '3 — every construction routes through the master constructor, incrementing the counter once per object' },
          { id: 'd', label: 'D', text: '0 — totalCount++ inside a chained constructor is not executed' }
        ],
        correctOptionId: 'c',
        explanation:
          'new Driver() chains to this(0L, "Anonymous", 0.0, false), which calls the four-argument master → totalCount becomes 1. new Driver(1L, "Alice") chains to the master → totalCount = 2. new Driver(2L, "Bob", 4.8, true) calls the master directly → totalCount = 3. Constructor chaining ensures the counter lives in one place and runs once per object regardless of which overload is used.'
      }
    ]
  },

  'java-spring-lld/oop-foundations/03-oop2-encapsulation-inheritance': {
    get conceptChecks() {
      return lessonInteractions['java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation'].conceptChecks;
    },
    get practiceQuestions() {
      return lessonInteractions['java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation'].practiceQuestions;
    }
  },

  'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces': {
    conceptChecks: [
      {
        id: 'lesson-4-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01',
        question:
          'An order service must support card, wallet, and bank-transfer payments without changing its orchestration code when a new payment method is added. Which design best preserves the contract?',
        options: [
          { id: 'a', label: 'A', text: 'Make PaymentService branch on each provider with instanceof checks.' },
          { id: 'b', label: 'B', text: 'Depend on a small PaymentAuthorizer interface and register adapters that implement it.' },
          { id: 'c', label: 'C', text: 'Expose every gateway SDK method on one large interface so all callers share one type.' },
          { id: 'd', label: 'D', text: 'Put provider-specific response translation in the controller before calling the service.' }
        ],
        correctOptionId: 'b',
        explanation:
          'A consumer-shaped PaymentAuthorizer keeps PaymentService focused on the use case. Each adapter translates its provider at the boundary, while dynamic dispatch lets the service work through the same contract when another implementation is registered.',
        incorrectExplanation:
          'Look for the boundary that owns provider-specific behavior. The application service should depend on a capability, not on concrete SDK types or a growing chain of type checks.',
        hint: 'PaymentService → capability contract → provider adapters',
        initialSelectedOption: 'b',
        initialSubmitted: true
      }
    ],
    architecture: {
      id: 'lesson-4-payment-authorization-flow',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — PAYMENT AUTHORIZATION',
      boundaryLabel: 'BOUNDARY ACCEPTED',
      boundaryText:
        'PaymentService depends on authorization capability, not on the infrastructure that provides it.',
      nodes: [
        { id: 'request', label: 'Request', kind: 'input' },
        { id: 'service', label: 'PaymentService', kind: 'service' },
        { id: 'contract', label: 'PaymentAuthorizer', kind: 'boundary', highlighted: true },
        { id: 'card', label: 'CardAuthorizer', kind: 'adapter' },
        { id: 'wallet', label: 'WalletAuthorizer', kind: 'adapter' },
        { id: 'bank', label: 'BankTransferAuthorizer', kind: 'adapter' },
        { id: 'result', label: 'AuthorizationResult', kind: 'output' }
      ]
    },
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 5; answer determined from source material, not marked in original
      {
        id: 'lesson-4-mcq-01',
        question: 'Consider the following statements: i. Calling of overloaded methods is decided at compile time ii. Calling of overridden methods is decided at runtime. Which of the following is correct?',
        options: [
          { id: 'a', label: 'A', text: 'Both are correct' },
          { id: 'b', label: 'B', text: 'Both are incorrect' },
          { id: 'c', label: 'C', text: 'i is correct, ii is incorrect' },
          { id: 'd', label: 'D', text: 'i is incorrect, ii is correct' }
        ],
        correctOptionId: 'a',
        explanation: 'Overloaded method resolution is performed statically by the compiler based on parameter signatures, while overridden method invocation is dispatched dynamically by the JVM at runtime based on the actual object instance.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 7; answer determined from source material, not marked in original
      {
        id: 'lesson-4-mcq-02',
        question: 'Which of the following does Java not support?',
        options: [
          { id: 'a', label: 'A', text: 'Method overriding' },
          { id: 'b', label: 'B', text: 'Method overloading' },
          { id: 'c', label: 'C', text: 'Operator overloading' },
          { id: 'd', label: 'D', text: 'Method hiding' }
        ],
        correctOptionId: 'c',
        explanation: 'Java natively supports method overriding, method overloading, and static method hiding, but intentionally does not support programmer-defined operator overloading.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 7; answer determined from source material, not marked in original
      {
        id: 'lesson-4-mcq-03',
        question: 'What is true about static methods? i. They can be overloaded ii. They can be overridden Which of the following is correct?',
        options: [
          { id: 'a', label: 'A', text: 'Both are correct' },
          { id: 'b', label: 'B', text: 'Both are incorrect' },
          { id: 'c', label: 'C', text: 'i is correct, ii is incorrect' },
          { id: 'd', label: 'D', text: 'i is incorrect, ii is correct' }
        ],
        correctOptionId: 'c',
        explanation: 'Static methods belong to the class rather than an instance; they can be overloaded with different parameter signatures, but cannot be polymorphically overridden (redefining them in a subclass results in method hiding).'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 60; answer determined from source material, not marked in original
      {
        id: 'lesson-4-mcq-04',
        question: "Consider the following classes: If client code does `P obj = new C(); obj.display();` where `display()` prints `d1`, `d`, then calls `fun1()`, `fun()`, `sfun()` — what is the output?",
        codeBlock: 'public class P {\n  protected int d1 = 10;\n  protected int d = 100;\n\n  protected void fun1(){\n    System.out.println("P\'s fun1");\n  }\n  protected void fun(){\n    System.out.println("P\'s fun");\n  }\n  static protected void sfun(){\n    System.out.println("P\'s sfun");\n  }\n}\n\npublic class C extends P {\n  protected int d2 = 20;\n  protected int d = 200;\n\n  protected void fun2(){\n    System.out.println("C\'s fun2");\n  }\n  protected void fun(){\n    System.out.println("C\'s fun");\n  }\n  static protected void sfun(){\n    System.out.println("C\'s sfun");\n  }\n}',
        options: [
          { id: 'a', label: 'A', text: 'Compile Time Error' },
          { id: 'b', label: 'B', text: "10 100 P's fun1 C's fun P's sfun" },
          { id: 'c', label: 'C', text: "100 100 P's fun1 C's fun P's sfun" },
          { id: 'd', label: 'D', text: "10 10 P's fun1 C's fun P's sfun" }
        ],
        correctOptionId: 'b',
        explanation: "Fields are never polymorphic in Java; `obj.d1` and `obj.d` resolve by the *reference type* (`P`), so both read `P`'s fields (10, 100) regardless of the actual object being a `C`. `fun1()` is not overridden in `C`, so it prints `P's fun1`. `fun()` **is** overridden, and instance methods dispatch dynamically on the *actual object type* (`C`), so it prints `C's fun`. `sfun()` is `static`, so it is hidden, not overridden — static calls resolve at compile time by reference type (`P`), printing `P's sfun`."
      }
    ]
  },

  'java-spring-lld/oop-foundations/05-oop-4-lms-lab': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 1; answer determined from source material, not marked in original
      {
        id: 'lesson-5-mcq-01',
        question: 'Consider the following about interface data-members: 1. They are final 2. They are static Which of the following is true?',
        options: [
          { id: 'a', label: 'A', text: 'Both are correct' },
          { id: 'b', label: 'B', text: 'Both are incorrect' },
          { id: 'c', label: 'C', text: 'i is correct, ii is incorrect' },
          { id: 'd', label: 'D', text: 'i is incorrect, ii is correct' }
        ],
        correctOptionId: 'a',
        explanation: 'All fields declared in a Java interface are implicitly `public static final` constants.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 9; answer determined from source material, not marked in original
      {
        id: 'lesson-5-mcq-02',
        question: 'Consider the following two statements: 1. Abstract classes should necessarily have abstract methods 2. Classes having abstract methods should be abstract Which of the following is true?',
        options: [
          { id: 'a', label: 'A', text: 'Both are correct' },
          { id: 'b', label: 'B', text: 'Both are incorrect' },
          { id: 'c', label: 'C', text: 'i is correct, ii is incorrect' },
          { id: 'd', label: 'D', text: 'i is incorrect, ii is correct' }
        ],
        correctOptionId: 'd',
        explanation: 'An abstract class is not required to declare any abstract methods (it may contain only concrete methods to prevent instantiation), but any class that contains at least one abstract method must be declared abstract.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 9; answer determined from source material, not marked in original
      {
        id: 'lesson-5-mcq-03',
        question: 'Which keyword is used to make a non-inheritable class in Java?',
        options: [
          { id: 'a', label: 'A', text: 'static' },
          { id: 'b', label: 'B', text: 'abstract' },
          { id: 'c', label: 'C', text: 'final' },
          { id: 'd', label: 'D', text: 'finally' }
        ],
        correctOptionId: 'c',
        explanation: 'Applying the `final` keyword to a class declaration prevents any other class from extending it.'
      }
    ]
  },

  'java-spring-lld/concurrency-multithreading/06-concurrency-1-threads': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 11; answer determined from source material, not marked in original
      {
        id: 'lesson-6-mcq-01',
        question: 'Consider the following two statements: i. Runnable interface is implemented by class which will be invoked via a separate Thread ii. The name of the function to start a new Thread is run Which of the following is correct?',
        options: [
          { id: 'a', label: 'A', text: 'Both a and b are true' },
          { id: 'b', label: 'B', text: 'Only a is true' },
          { id: 'c', label: 'C', text: 'Only b is true' },
          { id: 'd', label: 'D', text: 'Both a and b are false' }
        ],
        correctOptionId: 'b',
        explanation: 'Statement i is true; statement ii is false because the method to start a new concurrent thread is `start()`. Calling `run()` directly merely executes the method synchronously on the calling thread.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 7; answer determined from source material, not marked in original
      {
        id: 'lesson-6-mcq-02',
        question: "Consider the following two statements: 1. Threads of same process can access each other's stack data 2. Threads of same process can access each other's global data Which of the following is correct?",
        options: [
          { id: 'a', label: 'A', text: 'Both a and b are true' },
          { id: 'b', label: 'B', text: 'Only a is true' },
          { id: 'c', label: 'C', text: 'Only b is true' },
          { id: 'd', label: 'D', text: 'Both a and b are false' }
        ],
        correctOptionId: 'c',
        explanation: "Each thread has its own private call stack and local variable storage, while global, static, and heap data is shared across all threads within the same process."
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 1; answer determined from source material, not marked in original
      {
        id: 'lesson-6-mcq-03',
        question: 'Consider the following two statements: 1. Parallel programming requires multiple program counters 2. Concurrent programming requires time-bound CPU scheduling Which of the following is correct?',
        options: [
          { id: 'a', label: 'A', text: 'Both a and b are true' },
          { id: 'b', label: 'B', text: 'Only a is true' },
          { id: 'c', label: 'C', text: 'Only b is true' },
          { id: 'd', label: 'D', text: 'Both a and b are false' }
        ],
        correctOptionId: 'a',
        explanation: 'Parallel execution requires multiple physical CPU cores executing instructions simultaneously (each with its own hardware Program Counter), whereas concurrency on a single core relies on time-sliced CPU scheduling and context switching.'
      }
    ]
  },

  'java-spring-lld/concurrency-multithreading/07-concurrency-2-executors': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 9; answer determined from source material, not marked in original
      {
        id: 'lesson-7-mcq-01',
        question: 'Consider the following two statements: i. ExecutorService.submit returns a Future object ii. The method name to receive a value from Future object is get. Which of the following is correct?',
        options: [
          { id: 'a', label: 'A', text: 'Both a and b are true' },
          { id: 'b', label: 'B', text: 'Only a is true' },
          { id: 'c', label: 'C', text: 'Only b is true' },
          { id: 'd', label: 'D', text: 'Both a and b are false' }
        ],
        correctOptionId: 'a',
        explanation: '`ExecutorService.submit()` returns a `Future` instance representing the pending asynchronous computation, and `.get()` blocks the calling thread until the computed value is available.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 1; answer determined from source material, not marked in original
      {
        id: 'lesson-7-mcq-02',
        question: 'Consider the following two statements: 1. The responsibility of the Executor is to decide how to run different tasks on different threads 2. The responsibility of class implementing Callable is to define a task to be done on a separate thread Which of the following is correct?',
        options: [
          { id: 'a', label: 'A', text: 'Both a and b are true' },
          { id: 'b', label: 'B', text: 'Only a is true' },
          { id: 'c', label: 'C', text: 'Only b is true' },
          { id: 'd', label: 'D', text: 'Both a and b are false' }
        ],
        correctOptionId: 'a',
        explanation: '`Executor` manages thread lifecycle, pooling, and task scheduling, while a `Callable` implementation encapsulates the specific computation and return value of the task itself.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 2; answer determined from source material, not marked in original
      {
        id: 'lesson-7-mcq-03',
        question: "Consider the following two statements: 1. Executor manages the assignment of tasks to threads within the thread pool. 2. Waiting Queue holds the tasks that couldn't be assigned to threads in the thread pool. Which of the following is correct?",
        options: [
          { id: 'a', label: 'A', text: 'Both a and b are true' },
          { id: 'b', label: 'B', text: 'Only a is true' },
          { id: 'c', label: 'C', text: 'Only b is true' },
          { id: 'd', label: 'D', text: 'Both a and b are false' }
        ],
        correctOptionId: 'a',
        explanation: 'An Executor assigns queued tasks to available worker threads in the pool, while the internal waiting queue holds tasks when all pool threads are currently busy.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 8; answer determined from source material, not marked in original
      {
        id: 'lesson-7-mcq-04',
        question: "Consider the following two statements: 1. Runnable interface is used to create classes that run on a separate thread and return values to the main thread. 2. Callable interface is used to create classes that run on a separate thread and don't need to return values to the main thread. Which of the following is correct?",
        options: [
          { id: 'a', label: 'A', text: 'Both a and b are true' },
          { id: 'b', label: 'B', text: 'Only a is true' },
          { id: 'c', label: 'C', text: 'Only b is true' },
          { id: 'd', label: 'D', text: 'Both a and b are false' }
        ],
        correctOptionId: 'd',
        explanation: 'Both statements have it backwards: `Runnable.run()` returns `void` and cannot return a value to the caller, while `Callable<V>.call()` is specifically designed to return a typed value `V`. Neither statement correctly describes its interface.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 10; answer determined from source material, not marked in original
      {
        id: 'lesson-7-mcq-05',
        question: 'Consider the following two statements: 1. A class implementing Callable<Integer> will have a call function that returns integer 2. To get a value from a class implementing Callable<Integer>, we can use Future<Integer> Which of the following is correct?',
        options: [
          { id: 'a', label: 'A', text: 'Both a and b are true' },
          { id: 'b', label: 'B', text: 'Only a is true' },
          { id: 'c', label: 'C', text: 'Only b is true' },
          { id: 'd', label: 'D', text: 'Both are false' }
        ],
        correctOptionId: 'a',
        explanation: '`Callable<Integer>.call()` is declared to return `Integer`, and submitting that `Callable` to an `ExecutorService` returns a `Future<Integer>` whose `.get()` retrieves the computed value once ready.'
      }
    ]
  },

  'java-spring-lld/concurrency-multithreading/08-concurrency-3-synchronization': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 1; answer determined from source material, not marked in original
      {
        id: 'lesson-8-mcq-01',
        question: 'What is the name of the algorithm used by Atomic Data types for thread-safety?',
        options: [
          { id: 'a', label: 'A', text: 'Mark and Sweep' },
          { id: 'b', label: 'B', text: 'Binary Search' },
          { id: 'c', label: 'C', text: 'Compare and Swap' },
          { id: 'd', label: 'D', text: 'None of the above' }
        ],
        correctOptionId: 'c',
        explanation: 'Atomic classes (such as `AtomicInteger`) achieve lock-free thread safety using the hardware-level Compare-And-Swap (CAS) instruction.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 3; answer determined from source material, not marked in original
      {
        id: 'lesson-8-mcq-02',
        question: 'Which of the following statements about mutex locks in Java is true?',
        options: [
          { id: 'a', label: 'A', text: 'Mutex locks are used to achieve parallel execution of threads.' },
          { id: 'b', label: 'B', text: 'Mutex locks are synonymous with atomic data types in Java.' },
          { id: 'c', label: 'C', text: 'Mutex locks are used to protect critical sections of code from concurrent access.' },
          { id: 'd', label: 'D', text: 'Mutex locks are only applicable to single-threaded programs' }
        ],
        correctOptionId: 'c',
        explanation: 'A mutex lock enforces mutual exclusion, ensuring that only one thread can execute within a protected critical section at any given time.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 6; answer determined from source material, not marked in original
      {
        id: 'lesson-8-mcq-03',
        question: 'Which of the following statements is true about the synchronized keyword?',
        options: [
          { id: 'a', label: 'A', text: 'It can only be applied to instance methods' },
          { id: 'b', label: 'B', text: 'It can be applied to both instance methods and static methods' },
          { id: 'c', label: 'C', text: 'It can only be applied to static methods' },
          { id: 'd', label: 'D', text: 'It cannot be used in a multithreaded application' }
        ],
        correctOptionId: 'b',
        explanation: 'The `synchronized` keyword can be applied to instance methods (locking the instance `this`), static methods (locking the `Class` object), and standalone synchronized blocks.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 5; answer determined from source material, not marked in original
      {
        id: 'lesson-8-mcq-04',
        question: 'Which of the following is true regarding the differences between Hashtable and ConcurrentHashMap in Java?',
        options: [
          { id: 'a', label: 'A', text: 'Hashtable allows multiple threads to access different parts of the map at the same time, while ConcurrentHashMap does not.' },
          { id: 'b', label: 'B', text: 'ConcurrentHashMap is synchronized, while Hashtable is not.' },
          { id: 'c', label: 'C', text: 'Hashtable is synchronized, ConcurrentHashMap is not.' },
          { id: 'd', label: 'D', text: 'ConcurrentHashMap allows multiple threads to access different parts of the map at the same time, while Hashtable does not.' }
        ],
        correctOptionId: 'd',
        explanation: '`Hashtable` synchronizes on the entire map for every operation, allowing only one thread in at a time. `ConcurrentHashMap` uses finer-grained internal locking (segment/bucket-level), letting multiple threads operate on different parts of the map concurrently.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 2; answer determined from source material, not marked in original
      {
        id: 'lesson-8-mcq-05',
        question: 'Consider the following class: And client code creating `A obj1 = new A();` and `A obj2 = new A();`. Which pair of calls CANNOT execute concurrently?',
        codeBlock: 'public class A {\n  synchronized static void fun1(){}\n  synchronized void fun2(){}\n  void fun3(){}\n}',
        options: [
          { id: 'a', label: 'A', text: 'obj1.fun1() and obj1.fun2()' },
          { id: 'b', label: 'B', text: 'obj1.fun1() and obj2.fun1()' },
          { id: 'c', label: 'C', text: 'obj2.fun2() and obj2.fun3()' },
          { id: 'd', label: 'D', text: 'obj1.fun2() and obj2.fun2()' }
        ],
        correctOptionId: 'b',
        explanation: '`fun1()` is `static synchronized`, so it locks the shared `Class` object (`A.class`), not any particular instance. Both `obj1.fun1()` and `obj2.fun1()` compete for that one class-level lock regardless of which instance calls it, so they cannot run concurrently. `fun2()` is an instance-level lock, so different instances (`obj1`/`obj2`) calling it are unaffected by each other.'
      }
    ]
  },

  'java-spring-lld/concurrency-multithreading/09-concurrency-4-semaphores': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 4; answer determined from source material, not marked in original
      {
        id: 'lesson-9-mcq-01',
        question: 'Which of the following statements is true regarding mutex locks and semaphores?',
        options: [
          { id: 'a', label: 'A', text: 'Mutex Locks are used for synchronization while Semaphores is a syntax for creating threads' },
          { id: 'b', label: 'B', text: 'Mutex Locks allow only 1 thread in critical section while Semaphores can allow multiple threads in the critical section at same time' },
          { id: 'c', label: 'C', text: 'Lock and unlock are methods of semaphores' },
          { id: 'd', label: 'D', text: 'Acquire and release are methods of mutex locks' }
        ],
        correctOptionId: 'b',
        explanation: 'A mutex restricts critical section access to at most one thread, whereas a counting semaphore maintains a permit count allowing multiple threads to enter simultaneously up to its capacity limit.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 3; answer determined from source material, not marked in original
      {
        id: 'lesson-9-mcq-02',
        question: 'Which of the following methods in a Semaphore is a blocking method?',
        options: [
          { id: 'a', label: 'A', text: 'acquire' },
          { id: 'b', label: 'B', text: 'release' },
          { id: 'c', label: 'C', text: 'Both acquire and release' },
          { id: 'd', label: 'D', text: 'Neither acquire nor release' }
        ],
        correctOptionId: 'a',
        explanation: '`acquire()` blocks the calling thread if no permits are available (permit count is 0), whereas `release()` increments the permit count and never blocks.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 8; answer determined from source material, not marked in original
      {
        id: 'lesson-9-mcq-03',
        question: 'Consider the following two statements: 1. Release method of Semaphores increases the number of threads allowed in the critical section by 1. 2. If the value of Semaphore is 0, Release method of Semaphores blocks the thread Which of the following is true?',
        options: [
          { id: 'a', label: 'A', text: 'Only 1 is true' },
          { id: 'b', label: 'B', text: 'Only 2 is true' },
          { id: 'c', label: 'C', text: 'Both 1 and 2 are true' },
          { id: 'd', label: 'D', text: 'Both 1 and 2 are false' }
        ],
        correctOptionId: 'a',
        explanation: 'Statement 1 is true because `release()` increments the permit count; statement 2 is false because `release()` is a non-blocking operation that unblocks waiting threads rather than blocking itself.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 1; answer determined from source material, not marked in original
      {
        id: 'lesson-9-mcq-04',
        question: 'Consider the following two statements: a. If the value of a Semaphore is greater than 0, `acquire()` reduces the permit count by 1 but allows the thread to enter the critical section. b. If the value of a Semaphore is 0, `acquire()` blocks the thread. Which of the following is true?',
        options: [
          { id: 'a', label: 'A', text: 'Only a is true' },
          { id: 'b', label: 'B', text: 'Only b is true' },
          { id: 'c', label: 'C', text: 'Both a and b are true' },
          { id: 'd', label: 'D', text: 'Both a and b are false' }
        ],
        correctOptionId: 'c',
        explanation: "Both statements correctly describe `acquire()`'s behavior: when permits remain, it decrements the count and lets the thread proceed immediately; when the permit count has reached zero, it blocks the calling thread until another thread calls `release()`."
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 7; answer determined from source material, not marked in original
      {
        id: 'lesson-9-mcq-05',
        question: 'Which of the following is true about the critical section of a correctly working producer-consumer problem using two semaphores (a producer semaphore tracking empty slots, a consumer semaphore tracking filled slots)?',
        options: [
          { id: 'a', label: 'A', text: 'Critical section of producer should begin with acquire on producer semaphore and end with release on consumer semaphore' },
          { id: 'b', label: 'B', text: 'Critical section of producer should begin with acquire on producer semaphore and end with release on producer semaphore' },
          { id: 'c', label: 'C', text: 'Critical section of consumer should begin with acquire on producer semaphore and end with release on consumer semaphore' },
          { id: 'd', label: 'D', text: 'Critical section of consumer should begin with acquire on consumer semaphore and end with release on consumer semaphore' }
        ],
        correctOptionId: 'a',
        explanation: 'A producer must first `acquire()` an empty slot (the producer semaphore), then after producing, `release()` the consumer semaphore to signal that a new item is available. Signaling the *other* semaphore, not your own, is what lets the two sides coordinate.'
      }
    ]
  },

  'java-spring-lld/advanced-java-collections/10-java-adv-1-generics': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 64; answer determined from source material, not marked in original
      {
        id: 'lesson-10-mcq-01',
        question: 'What does T denote in the following code:',
        codeBlock: 'public class Box<T> {\n  // class implementation\n}',
        options: [
          { id: 'a', label: 'A', text: 'Type parameter' },
          { id: 'b', label: 'B', text: 'Generic instance' },
          { id: 'c', label: 'C', text: 'Class name' },
          { id: 'd', label: 'D', text: 'Class type' }
        ],
        correctOptionId: 'a',
        explanation: '`T` is a formal type parameter that serves as a placeholder for the concrete type specified when the `Box` class is instantiated.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 62; answer determined from source material, not marked in original
      {
        id: 'lesson-10-mcq-02',
        question: 'What is the purpose of using bounded wildcards in Java generics?',
        options: [
          { id: 'a', label: 'A', text: 'To allow any type to be passed as an argument' },
          { id: 'b', label: 'B', text: 'To restrict the type of objects that can be used' },
          { id: 'c', label: 'C', text: 'To enforce type safety in generic classes' },
          { id: 'd', label: 'D', text: 'To simplify the syntax of generic declarations' }
        ],
        correctOptionId: 'b',
        explanation: 'Bounded wildcards (like `? extends Number` or `? super Integer`) restrict the acceptable type arguments to a specific inheritance hierarchy for controlled reading or writing.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 10; answer determined from source material, not marked in original
      {
        id: 'lesson-10-mcq-03',
        question: 'When is it appropriate to use wildcards with an upper bound in Java generics?',
        options: [
          { id: 'a', label: 'A', text: 'To allow any type as a method parameter' },
          { id: 'b', label: 'B', text: 'When the method should work with specific subclasses' },
          { id: 'c', label: 'C', text: 'When the method should work with any object type' },
          { id: 'd', label: 'D', text: 'To specify a lower limit on the allowed types' }
        ],
        correctOptionId: 'b',
        explanation: 'Upper-bounded wildcards (`? extends SuperType`) are used when a method needs to operate on a collection of elements belonging to any subclass of a given supertype (read-only producer operations).'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 49; answer determined from source material, not marked in original
      {
        id: 'lesson-10-mcq-04',
        question: 'Suppose you are writing a generic method to return the first element of a list. What is the correct method declaration?',
        options: [
          { id: 'a', label: 'A', text: '`public static <T> T getFirstElement(List<T> list)`' },
          { id: 'b', label: 'B', text: '`public static T getFirstElement(List<T> list)`' },
          { id: 'c', label: 'C', text: '`public static void getFirstElement(List<T> list)`' },
          { id: 'd', label: 'D', text: '`public static <T> void getFirstElement(List<T> list)`' }
        ],
        correctOptionId: 'a',
        explanation: 'A generic static method must declare its own type parameter `<T>` immediately before the return type, since static members have no access to a class-level type parameter. The return type must also be `T`, not `void`, since the method returns the first element.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 59; answer determined from source material, not marked in original
      {
        id: 'lesson-10-mcq-05',
        question: 'What does the `extends` keyword signify in the context of Java generics (e.g. `<T extends Number>`)?',
        options: [
          { id: 'a', label: 'A', text: 'It specifies a lower bound for a type parameter.' },
          { id: 'b', label: 'B', text: 'It restricts the use of wildcard types.' },
          { id: 'c', label: 'C', text: 'It indicates inheritance for a generic class.' },
          { id: 'd', label: 'D', text: 'It denotes an upper bound for a type parameter.' }
        ],
        correctOptionId: 'd',
        explanation: 'In a generic type-parameter declaration, `extends` denotes an upper bound: `T` must be that type or a subtype of it. This is distinct from wildcard usage but relies on the same "extends = upper bound" idea.'
      }
    ]
  },

  'java-spring-lld/advanced-java-collections/11-java-adv-2-collections-lab': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 4; answer determined from source material, not marked in original
      {
        id: 'lesson-11-mcq-01',
        question: 'Consider the following two statements about Vector, ArrayList and LinkedList: 1. Both vector and arraylist are dynamic arrays but the vector is thread-safe while arraylist is not 2. Both arraylist and linkedlist can grow dynamically but memory in an arraylist is contiguous while not so in linkedlist Which of the following is correct?',
        options: [
          { id: 'a', label: 'A', text: 'Both 1 and 2 are true' },
          { id: 'b', label: 'B', text: 'Only 1 is true' },
          { id: 'c', label: 'C', text: 'Only 2 is true' },
          { id: 'd', label: 'D', text: 'Both 1 and 2 are false' }
        ],
        correctOptionId: 'a',
        explanation: 'Statement 1 is true because `Vector` synchronizes its methods for thread safety while `ArrayList` is unsynchronized; statement 2 is true because `ArrayList` uses contiguous array memory while `LinkedList` allocates disconnected heap nodes linked by pointers.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 4; answer determined from source material, not marked in original
      {
        id: 'lesson-11-mcq-02',
        question: 'Which of the following require the elements passed to implement Comparable interface?',
        options: [
          { id: 'a', label: 'A', text: 'HashSet' },
          { id: 'b', label: 'B', text: 'ArrayDeque' },
          { id: 'c', label: 'C', text: 'TreeSet' },
          { id: 'd', label: 'D', text: 'Stack' }
        ],
        correctOptionId: 'c',
        explanation: '`TreeSet` requires elements to implement `Comparable` (or have an explicit `Comparator` provided) to maintain its internal Red-Black tree sorted order.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 3; answer determined from source material, not marked in original
      {
        id: 'lesson-11-mcq-03',
        question: 'What should go inside <> if you want to write a generic compare method?',
        codeBlock: 'public static <____> int compareTo(T a, T b) {\n    return a.compareTo(b);\n}',
        options: [
          { id: 'a', label: 'A', text: 'T' },
          { id: 'b', label: 'B', text: '?' },
          { id: 'c', label: 'C', text: 'T extends Comparable' },
          { id: 'd', label: 'D', text: 'T extends Comparator' }
        ],
        correctOptionId: 'c',
        explanation: 'Declaring `<T extends Comparable<T>>` bounds the type parameter `T` to types that implement `Comparable`, enabling the method body to invoke `.compareTo()`.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 46; answer determined from source material, not marked in original
      {
        id: 'lesson-11-mcq-04',
        question: 'Which of the following is thread-safe?',
        options: [
          { id: 'a', label: 'A', text: 'ArrayList' },
          { id: 'b', label: 'B', text: 'HashMap' },
          { id: 'c', label: 'C', text: 'Hashtable' },
          { id: 'd', label: 'D', text: 'LinkedList' }
        ],
        correctOptionId: 'c',
        explanation: '`Hashtable` synchronizes every method internally, making it thread-safe (though coarse-grained and slower under contention). `ArrayList`, `HashMap`, and `LinkedList` are all unsynchronized by default.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 5; answer determined from source material, not marked in original
      {
        id: 'lesson-11-mcq-05',
        question: "Which of the following classes doesn't implement the `List` interface (directly or indirectly)?",
        options: [
          { id: 'a', label: 'A', text: 'Vector' },
          { id: 'b', label: 'B', text: 'Stack' },
          { id: 'c', label: 'C', text: 'ArrayList' },
          { id: 'd', label: 'D', text: 'PriorityQueue' }
        ],
        correctOptionId: 'd',
        explanation: '`Vector`, `Stack` (which extends `Vector`), and `ArrayList` all implement `List`. `PriorityQueue` implements the `Queue` interface instead — it is backed by a binary heap and does not offer indexed `List` access.'
      }
    ]
  },

  'java-spring-lld/advanced-java-collections/12-java-adv-3-lambdas-streams': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 10; answer determined from source material, not marked in original
      {
        id: 'lesson-12-mcq-01',
        question: 'Output of above code:',
        codeBlock: 'public class LambdaExample {\n  public static void main(String[] args) {\n    IntFunction<Integer> square = x -> x * x;\n    System.out.println(square.apply(5));\n    \n    BinaryOperator<Integer> addition = (x, y) -> x + y;\n    System.out.println(addition.apply(10, 20));\n    \n    Function<Integer, Integer> increment = x -> x + 1;\n    System.out.println(increment.apply(7));\n  }\n}',
        options: [
          { id: 'a', label: 'A', text: '25 30 8' },
          { id: 'b', label: 'B', text: '25 30 7' },
          { id: 'c', label: 'C', text: '5 30 7' },
          { id: 'd', label: 'D', text: 'Compile Error' }
        ],
        correctOptionId: 'a',
        explanation: '`square.apply(5)` computes $5 \\times 5 = 25$, `addition.apply(10, 20)` computes $10 + 20 = 30$, and `increment.apply(7)` computes $7 + 1 = 8$.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 6; answer determined from source material, not marked in original
      {
        id: 'lesson-12-mcq-02',
        question: 'Which of the following is a terminal function in streams api?',
        options: [
          { id: 'a', label: 'A', text: 'map' },
          { id: 'b', label: 'B', text: 'filter' },
          { id: 'c', label: 'C', text: 'foreach' },
          { id: 'd', label: 'D', text: 'none of the above' }
        ],
        correctOptionId: 'c',
        explanation: '`forEach` is a terminal operation that triggers pipeline execution; `map` and `filter` are lazy intermediate operations.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 52; answer determined from source material, not marked in original
      {
        id: 'lesson-12-mcq-03',
        question: 'In the above code, Function, BinaryOperator, IntFunction are types of:',
        codeBlock: 'IntFunction<Integer> square = x -> x * x;\nBinaryOperator<Integer> addition = (x, y) -> x + y;\nFunction<Integer, Integer> increment = x -> x + 1;',
        options: [
          { id: 'a', label: 'A', text: 'Lambda Expressions' },
          { id: 'b', label: 'B', text: 'Functional Interfaces' },
          { id: 'c', label: 'C', text: 'Functions' },
          { id: 'd', label: 'D', text: 'Classes' }
        ],
        correctOptionId: 'b',
        explanation: '`IntFunction`, `BinaryOperator`, and `Function` are standard functional interfaces provided in the `java.util.function` package.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 8; answer determined from source material, not marked in original
      {
        id: 'lesson-12-mcq-04',
        question: 'What does the following code snippet do?',
        codeBlock: 'Set<String> uniqueFruits = fruits.stream()\n  .collect(Collectors.toSet());\nSystem.out.println("Result: " + uniqueFruits);',
        options: [
          { id: 'a', label: 'A', text: 'Removes duplicate fruits from the list.' },
          { id: 'b', label: 'B', text: 'Creates a set of all fruit names.' },
          { id: 'c', label: 'C', text: 'Concatenates all fruits into a single string.' },
          { id: 'd', label: 'D', text: 'Compile Error.' }
        ],
        correctOptionId: 'b',
        explanation: '`Collectors.toSet()` collects the stream elements into a `Set<String>`. Deduplication is a natural consequence of the `Set` contract, but the collector\'s direct action is building that set, not "removing duplicates" as a separate step.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 8; answer determined from source material, not marked in original
      {
        id: 'lesson-12-mcq-05',
        question: 'Which of the following comparators will sort a list of strings in descending order according to length?',
        options: [
          { id: 'a', label: 'A', text: '`Comparator<String> c = (s1, s2) -> Integer.compare(s2.length(), s1.length());`' },
          { id: 'b', label: 'B', text: '`Comparator<String> c = (s1, s2) -> s2.length() - s1.length();`' },
          { id: 'c', label: 'C', text: '`Comparator<String> c = Comparator.comparingInt(String::length).reversed();`' },
          { id: 'd', label: 'D', text: 'All of the above' }
        ],
        correctOptionId: 'd',
        explanation: 'All three are valid, equivalent ways of expressing a descending-by-length comparator: two hand-written lambda forms (integer subtraction and `Integer.compare` for overflow safety) and one built from the fluent `Comparator.comparingInt(...).reversed()` API.'
      }
    ]
  },

  'java-spring-lld/advanced-java-collections/13-java-adv-4-streams-exceptions': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 8; answer determined from source material, not marked in original
      {
        id: 'lesson-13-mcq-01',
        question: 'What does the following code snippet do?',
        codeBlock: 'Map<Integer, List<String>> groupedByLength = fruits.stream()\n    .collect(Collectors.groupingBy(String::length));',
        options: [
          { id: 'a', label: 'A', text: 'Creates a map where keys are fruit lengths and values are fruit names.' },
          { id: 'b', label: 'B', text: 'Creates a map where keys are fruit names and values are fruit length.' },
          { id: 'c', label: 'C', text: 'Counts the total number of fruits.' },
          { id: 'd', label: 'D', text: 'Compile Error.' }
        ],
        correctOptionId: 'a',
        explanation: '`Collectors.groupingBy(String::length)` classifies elements by their string length, returning a `Map<Integer, List<String>>` where each key is a word length and the value is the list of matching fruits.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 10; answer determined from source material, not marked in original
      {
        id: 'lesson-13-mcq-02',
        question: 'Which of the following stream methods return a boolean?',
        options: [
          { id: 'a', label: 'A', text: 'findFirst' },
          { id: 'b', label: 'B', text: 'filter' },
          { id: 'c', label: 'C', text: 'allMatch' },
          { id: 'd', label: 'D', text: 'collect' }
        ],
        correctOptionId: 'c',
        explanation: '`allMatch` is a short-circuiting terminal operation that returns a `boolean` indicating whether all elements match the given predicate.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 55; answer determined from source material, not marked in original
      {
        id: 'lesson-13-mcq-03',
        question: 'What does the following code snippet do?',
        codeBlock: 'String result = fruits.stream()\n  .collect(Collectors.joining(", "));',
        options: [
          { id: 'a', label: 'A', text: 'Concatenates all fruits into a single string.' },
          { id: 'b', label: 'B', text: 'Creates a list of fruits.' },
          { id: 'c', label: 'C', text: 'Calculates the total length of all fruits.' },
          { id: 'd', label: 'D', text: 'Compilation Error.' }
        ],
        correctOptionId: 'a',
        explanation: '`Collectors.joining(", ")` is a terminal collector that concatenates the stream of fruit strings into a single delimited `String`.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 6; answer determined from source material, not marked in original
      {
        id: 'lesson-13-mcq-04',
        question: 'Which of the following is NOT a way of creating a stream?',
        options: [
          { id: 'a', label: 'A', text: '`Stream.of()`' },
          { id: 'b', label: 'B', text: '`list.stream()`' },
          { id: 'c', label: 'C', text: '`Stream.iterate()`' },
          { id: 'd', label: 'D', text: '`stream.collect()`' }
        ],
        correctOptionId: 'd',
        explanation: '`Stream.of()`, `list.stream()`, and `Stream.iterate()` all *create* a stream. `collect()` is a terminal operation that *consumes* an existing stream and produces a result — it does not create a new stream.'
      }
    ]
  },

  'java-spring-lld/design-principles-patterns/14-solid-principles': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 6
      {
        id: 'lesson-14-solid-mcq-01',
        question: 'A class is responsible for generating reports in different formats such as PDF, HTML, and CSV using a switch case with one branch per format. Adding TXT support requires modifying the class. Which SOLID principle is violated?',
        options: [
          { id: 'a', label: 'A', text: 'Open/closed' },
          { id: 'b', label: 'B', text: 'Liskov substitution' },
          { id: 'c', label: 'C', text: 'Interface segregation' },
          { id: 'd', label: 'D', text: 'Dependency inversion' }
        ],
        correctOptionId: 'a',
        explanation: 'Every new format requires editing the existing, already-tested switch statement instead of adding new code, the defining shape of an Open/Closed violation.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 9
      {
        id: 'lesson-14-solid-mcq-02',
        question: 'In a video game, a class handles different enemy types and their behaviors. As new enemies are introduced, the developer adds a new if-else block to the same class each time. Which SOLID principle is violated?',
        options: [
          { id: 'a', label: 'A', text: 'Open/closed' },
          { id: 'b', label: 'B', text: 'Liskov substitution' },
          { id: 'c', label: 'C', text: 'Interface segregation' },
          { id: 'd', label: 'D', text: 'Dependency inversion' }
        ],
        correctOptionId: 'a',
        explanation: 'Same shape as the report-generator case: a new enemy type should be new code (a new class), not a new branch inside an existing method.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 7
      {
        id: 'lesson-14-solid-mcq-03',
        question: 'In an inventory management system, one class handles inventory operations, generates sales reports, AND sends notifications to suppliers. Which SOLID principle is violated?',
        options: [
          { id: 'a', label: 'A', text: 'Single responsibility' },
          { id: 'b', label: 'B', text: 'Open/closed' },
          { id: 'c', label: 'C', text: 'Liskov substitution' },
          { id: 'd', label: 'D', text: 'Interface segregation' }
        ],
        correctOptionId: 'a',
        explanation: 'Three unrelated reasons to change (inventory logic, reporting, notifications) are bundled into one class.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 3
      {
        id: 'lesson-14-solid-mcq-04',
        question: 'A class handles both user authentication (verifying credentials) and database interactions (querying, updating user records). Which SOLID principle is violated?',
        options: [
          { id: 'a', label: 'A', text: 'Single responsibility' },
          { id: 'b', label: 'B', text: 'Open/closed' },
          { id: 'c', label: 'C', text: 'Liskov substitution' },
          { id: 'd', label: 'D', text: 'Interface segregation' }
        ],
        correctOptionId: 'a',
        explanation: 'Authentication logic and persistence logic are two unrelated reasons to change, bundled into one class.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 4
      {
        id: 'lesson-14-solid-mcq-05',
        question: "According to the Liskov Substitution Principle, if class B is a subclass of class A, what must be true when replacing an instance of A with an instance of B?",
        options: [
          { id: 'a', label: 'A', text: "The program's execution speed must remain identical or increase" },
          { id: 'b', label: 'B', text: 'The program must continue to function correctly without violating the behavioral expectations established by class A' },
          { id: 'c', label: 'C', text: 'Class B must override every single public and private method defined in class A' },
          { id: 'd', label: 'D', text: 'The client code must explicitly cast class B back to class A before calling any inherited methods' }
        ],
        correctOptionId: 'b',
        explanation: 'LSP is about behavioral substitutability: the caller must not need any special handling to safely use B wherever A was expected.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 45
      {
        id: 'lesson-14-solid-mcq-06',
        question: "Under LSP, how must a subclass handle the preconditions and postconditions established by its parent class?",
        options: [
          { id: 'a', label: 'A', text: 'It must make preconditions stricter and postconditions weaker' },
          { id: 'b', label: 'B', text: 'It cannot change preconditions, but it can safely remove all postconditions' },
          { id: 'c', label: 'C', text: 'It can make preconditions less strict (require less) and postconditions more strict (guarantee more)' },
          { id: 'd', label: 'D', text: "It must ignore the parent class's conditions and define completely independent validation rules" }
        ],
        correctOptionId: 'c',
        explanation: 'A subtype may only ask for less and promise at least as much as its parent — this is the precise technical definition behind "a promise being kept."'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 54
      {
        id: 'lesson-14-solid-mcq-07',
        question: 'Why is the Interface Segregation Principle highly relevant when designing object-oriented applications?',
        options: [
          { id: 'a', label: 'A', text: 'It requires all classes to implement a single, massive interface to guarantee consistency across the application' },
          { id: 'b', label: 'B', text: 'It prevents bloated interfaces from forcing subclasses to implement "dummy" or empty methods, which pollutes the API and misleads developers' },
          { id: 'c', label: 'C', text: 'It guarantees that an application will consume less memory at runtime' },
          { id: 'd', label: 'D', text: 'It dictates that interfaces should only contain private methods to secure implementation details' }
        ],
        correctOptionId: 'b',
        explanation: 'This is exactly the "Penguin problem" transplanted to interfaces: a fat interface forces implementers into dummy or exception-throwing methods they cannot honestly support.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 5
      {
        id: 'lesson-14-solid-mcq-08',
        question: 'How do ISP and DIP conceptually work together in a well-architected system?',
        options: [
          { id: 'a', label: 'A', text: 'DIP forces the creation of abstractions, and ISP ensures those abstractions are granular, focused, and client-specific' },
          { id: 'b', label: 'B', text: 'ISP restricts the total number of interfaces allowed, while DIP forces all classes to eventually merge into a single abstract base class' },
          { id: 'c', label: 'C', text: 'They inherently contradict each other; applying DIP requires violating ISP' },
          { id: 'd', label: 'D', text: 'ISP solely dictates the UI layer, while DIP solely manages the database layer' }
        ],
        correctOptionId: 'a',
        explanation: 'DIP says depend on abstractions; ISP says make sure those abstractions are small and focused rather than fat — the two principles work at different levels of the same design decision.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 2
      {
        id: 'lesson-14-solid-mcq-09',
        question: 'The Dependency Inversion Principle consists of two core parts regarding high-level and low-level modules. Which statement perfectly captures the essence of DIP?',
        options: [
          { id: 'a', label: 'A', text: 'High-level modules should depend on low-level modules; both should depend on concrete details' },
          { id: 'b', label: 'B', text: 'Low-level modules should inherit directly from high-level modules to invert the control flow' },
          { id: 'c', label: 'C', text: 'High-level modules should not depend on low-level modules; both must depend on abstractions (like interfaces or abstract classes)' },
          { id: 'd', label: 'D', text: 'Dependencies should always be instantiated globally at the very top of a source file' }
        ],
        correctOptionId: 'c',
        explanation: "Both sides depend on a shared abstraction rather than one depending directly on the other's concrete implementation."
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 11
      {
        id: 'lesson-14-solid-mcq-10',
        question: 'Why does DIP explicitly advocate for depending on abstractions rather than concretions?',
        options: [
          { id: 'a', label: 'A', text: 'Because abstract classes compile faster than concrete classes in modern languages' },
          { id: 'b', label: 'B', text: 'Because it eliminates the need for unit testing, as abstractions are inherently bug-free' },
          { id: 'c', label: 'C', text: 'Because concretions are volatile and change frequently, whereas abstractions represent stable business concepts' },
          { id: 'd', label: 'D', text: 'Because object-oriented languages physically do not allow high-level modules to directly instantiate concrete classes' }
        ],
        correctOptionId: 'c',
        explanation: 'Concrete implementations (a specific database driver, a specific payment SDK) change far more often than the stable business-level contract they fulfill; depending on the stable abstraction insulates high-level code from that churn.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 3
      {
        id: 'lesson-14-solid-mcq-11',
        question: 'When a system consistently violates LSP, ISP, and DIP simultaneously across a major codebase, what is the most likely structural consequence during a system redesign?',
        options: [
          { id: 'a', label: 'A', text: 'High Rigidity and Fragility: changing a low-level detail forces massive cascading rewrites across high-level business logic, and code reuse becomes nearly impossible' },
          { id: 'b', label: 'B', text: 'Memory Leaks: the garbage collector will consistently fail to clean up instances of classes that use inheritance' },
          { id: 'c', label: 'C', text: 'Syntax Errors: the compiler will refuse to process files containing deep inheritance hierarchies' },
          { id: 'd', label: 'D', text: 'Loss of Thread Safety: the application will automatically lose its ability to handle concurrent tasks' }
        ],
        correctOptionId: 'a',
        explanation: 'These three principles all exist to keep high-level and low-level code loosely coupled; violating all three together produces exactly the rigid, fragile, hard-to-reuse codebase SOLID as a whole is meant to prevent.'
      }
    ]
  },

  'java-spring-lld/design-principles-patterns/16-structural-patterns': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q3
      {
        id: 'lesson-16-structural-mcq-01',
        question: 'What is the main idea behind the Decorator pattern?',
        options: [
          { id: 'a', label: 'A', text: 'Copying an existing object to create a new one' },
          { id: 'b', label: 'B', text: 'Adding new behavior to an object by wrapping it, without changing its original class' },
          { id: 'c', label: 'C', text: 'Storing shared data in one place and reusing it across many objects' },
          { id: 'd', label: 'D', text: 'Notifying multiple objects whenever one object changes' }
        ],
        correctOptionId: 'b',
        explanation: 'Decorator attaches new responsibilities to an object dynamically by wrapping it in another object implementing the same interface, leaving the original class untouched. (A describes Prototype, C describes Flyweight, D describes Observer.)'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q4
      {
        id: 'lesson-16-structural-mcq-02',
        question: 'Consider this code: What gets printed?',
        codeBlock: 'Beverage order = new Espresso();        // cost = 80.0\norder = new Mocha(order);               // adds 20.0\norder = new Whip(order);                // adds 15.0\nSystem.out.println(order.cost());',
        options: [
          { id: 'a', label: 'A', text: '80.0' },
          { id: 'b', label: 'B', text: '100.0' },
          { id: 'c', label: 'C', text: '115.0' },
          { id: 'd', label: 'D', text: 'Compile error' }
        ],
        correctOptionId: 'c',
        explanation: "Each decorator's `cost()` calls the wrapped object's `cost()` and adds its own charge: 80.0 + 20.0 + 15.0 = 115.0."
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q5
      {
        id: 'lesson-16-structural-mcq-03',
        question: "A student writes this Decorator code but it doesn't compile: No constructor was written for `Mocha`. What's the most likely problem?",
        codeBlock: 'class Mocha extends CondimentDecorator {\n    public double cost() {\n        return wrappedBeverage.cost() + 20.0;\n    }\n}',
        options: [
          { id: 'a', label: 'A', text: '`CondimentDecorator` requires a constructor that passes the wrapped `Beverage`, and `Mocha` never provides one' },
          { id: 'b', label: 'B', text: '`cost()` should not call `wrappedBeverage.cost()`' },
          { id: 'c', label: 'C', text: '`Mocha` should implement `Beverage` directly, not extend `CondimentDecorator`' },
          { id: 'd', label: 'D', text: 'There is no problem, this code is correct' }
        ],
        correctOptionId: 'a',
        explanation: '`CondimentDecorator` needs to receive the wrapped `Beverage` instance via a constructor. Without `Mocha` writing one (typically calling `super(beverage)`), `wrappedBeverage` is never properly initialized.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q6
      {
        id: 'lesson-16-structural-mcq-04',
        question: 'You\'re building a coffee shop app. The business now wants a "double mocha" option — mocha added twice for extra flavor and cost. Which design lets you support this most naturally?',
        options: [
          { id: 'a', label: 'A', text: 'Add a `mochaCount` field to `Espresso`' },
          { id: 'b', label: 'B', text: 'Add an `if (isDouble)` check inside `Mocha.cost()`' },
          { id: 'c', label: 'C', text: "Create a new class called `DoubleMocha` that copies all of `Espresso`'s fields" },
          { id: 'd', label: 'D', text: 'Wrap the order in `Mocha` twice: `new Mocha(new Mocha(order))`' }
        ],
        correctOptionId: 'd',
        explanation: 'Decorators can be stacked arbitrarily. Wrapping a beverage in `Mocha` twice naturally doubles the mocha charge and behavior with zero new code.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q7
      {
        id: 'lesson-16-structural-mcq-05',
        question: 'In the Flyweight pattern, what does "intrinsic state" mean?',
        options: [
          { id: 'a', label: 'A', text: 'Data that changes every time, unique to one specific object' },
          { id: 'b', label: 'B', text: 'Data used only for logging and debugging' },
          { id: 'c', label: 'C', text: 'Data that is shared and identical across many objects' },
          { id: 'd', label: 'D', text: 'Data that is never stored in memory' }
        ],
        correctOptionId: 'c',
        explanation: 'Intrinsic state is identical across many instances and can be shared from a single cached flyweight object, which is what makes the memory savings possible.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q8
      {
        id: 'lesson-16-structural-mcq-06',
        question: 'Assuming `BulletTypeFactory` caches `BulletType` objects in a `HashMap`, what does this print?',
        codeBlock: 'BulletType t1 = BulletTypeFactory.getBulletType("AKM");\nBulletType t2 = BulletTypeFactory.getBulletType("AKM");\nSystem.out.println(t1 == t2);',
        options: [
          { id: 'a', label: 'A', text: 'true' },
          { id: 'b', label: 'B', text: 'false' },
          { id: 'c', label: 'C', text: 'Compile error' },
          { id: 'd', label: 'D', text: "It depends on the bullet's position" }
        ],
        correctOptionId: 'a',
        explanation: 'The factory returns the same cached instance both times for the same key, so `t1` and `t2` reference the identical object and `==` is `true`. Position is extrinsic and irrelevant here.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q9
      {
        id: 'lesson-16-structural-mcq-07',
        question: 'A student splits a `Character` class (used to render millions of characters in a text editor) like this: What did they get backwards?',
        codeBlock: 'class CharacterIntrinsic {\n    int row;\n    int column;\n}\nclass CharacterExtrinsic {\n    String font;\n    int size;\n    String color;\n}',
        options: [
          { id: 'a', label: 'A', text: 'Nothing — this split is correct' },
          { id: 'b', label: 'B', text: '`row` and `column` should be intrinsic; `font`, `size`, `color` should be extrinsic' },
          { id: 'c', label: 'C', text: '`row` and `column` should be extrinsic; `font`, `size`, `color` should be intrinsic' },
          { id: 'd', label: 'D', text: 'All fields should be in the same class' }
        ],
        correctOptionId: 'c',
        explanation: "Font/size/color are typically shared across large runs of text (intrinsic, cacheable); each character's position is unique per occurrence (extrinsic, passed in at render time). The student inverted the split."
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q10
      {
        id: 'lesson-16-structural-mcq-08',
        question: 'A team is building a food delivery app. Every order line item needs a `Category` (like "Beverages" or "Desserts") with a name, icon, and tax rate. There are only 30 categories, but millions of order line items per day. What\'s the best approach?',
        options: [
          { id: 'a', label: 'A', text: 'Create a new `Category` object for every line item, since each order is different' },
          { id: 'b', label: 'B', text: 'Store one shared `Category` object per category name in a factory/cache, and have every line item just reference it' },
          { id: 'c', label: 'C', text: 'Store all category data directly inside the `OrderLineItem` class as separate fields' },
          { id: 'd', label: 'D', text: 'Avoid using categories altogether to save memory' }
        ],
        correctOptionId: 'b',
        explanation: 'Classic Flyweight factory: cache one `Category` object per name and have every line item hold a reference to the shared instance.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q11
      {
        id: 'lesson-16-structural-mcq-09',
        question: 'What is the key difference between Decorator and Flyweight?',
        options: [
          { id: 'a', label: 'A', text: 'Flyweight adds new behavior; Decorator saves memory' },
          { id: 'b', label: 'B', text: 'They are the same pattern with different names' },
          { id: 'c', label: 'C', text: 'Decorator is only used in games; Flyweight is only used in coffee shop examples' },
          { id: 'd', label: 'D', text: 'Decorator adds new behavior by wrapping objects; Flyweight saves memory by sharing common data across many objects' }
        ],
        correctOptionId: 'd',
        explanation: "Decorator's purpose is behavioral extension via wrapping; Flyweight's purpose is memory optimization via sharing intrinsic state."
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q12
      {
        id: 'lesson-16-structural-mcq-10',
        question: 'An AI assistant was asked to add a "combo discount" to the coffee shop example. It gave back this code: What\'s wrong with this from a Decorator design point of view?',
        codeBlock: 'class Espresso implements Beverage {\n    boolean hasMocha = false;\n    boolean hasWhip = false;\n    public double cost() {\n        double cost = 80.0;\n        if (hasMocha) cost += 20.0;\n        if (hasWhip) cost += 15.0;\n        if (hasMocha && hasWhip) cost *= 0.9;\n        return cost;\n    }\n}',
        options: [
          { id: 'a', label: 'A', text: 'The discount math is calculated incorrectly' },
          { id: 'b', label: 'B', text: 'It puts add-on flags and combo logic back inside the base class, which is exactly the design the pattern was meant to avoid' },
          { id: 'c', label: 'C', text: 'Nothing is wrong, this is a valid Decorator' },
          { id: 'd', label: 'D', text: '`Espresso` should not implement `Beverage`' }
        ],
        correctOptionId: 'b',
        explanation: 'This reintroduces the exact tight coupling Decorator solves: every new add-on now requires editing `Espresso` itself.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — hackmd/29-rytL_zqBMe.md, "Distinguishing Adapter from Facade"
      {
        id: 'lesson-16-structural-mcq-11',
        question: 'What is the key differentiator between Adapter and Facade?',
        options: [
          { id: 'a', label: 'A', text: 'Adapter always uses more memory than Facade' },
          { id: 'b', label: 'B', text: 'Adapter solves incompatible interfaces (typically one adaptee); Facade solves complex, hard-to-use systems (typically multiple subsystems)' },
          { id: 'c', label: 'C', text: 'Facade is only for legacy code; Adapter is only for new code' },
          { id: 'd', label: 'D', text: 'They are interchangeable and the choice is purely stylistic' }
        ],
        correctOptionId: 'b',
        explanation: "The test is *why* the wrapper exists: translating between two shapes that don't fit (Adapter) versus hiding coordination across several complex subsystems behind one simple entry point (Facade)."
      },
      // SOURCE_TYPE: FROM_MATERIAL — hackmd/29-rytL_zqBMe.md, "Dependency Injection"
      {
        id: 'lesson-16-structural-mcq-12',
        question: 'Why should a Facade receive its subsystem dependencies through its constructor instead of creating them internally with `new`?',
        options: [
          { id: 'a', label: 'A', text: "It has no real benefit, it's just a style preference" },
          { id: 'b', label: 'B', text: 'It locks the facade to one concrete implementation, which is the goal' },
          { id: 'c', label: 'C', text: 'It keeps the facade testable with mocks and swappable to different implementations without modifying the facade itself' },
          { id: 'd', label: 'D', text: 'Constructors in Java cannot call `new` at all' }
        ],
        correctOptionId: 'c',
        explanation: 'Constructing dependencies internally hardcodes the facade to specific implementations, making it untestable without real subsystems and unable to swap implementations later. Injecting them keeps the facade decoupled.'
      }
    ]
  },

  'java-spring-lld/design-principles-patterns/17-behavioural-patterns-uml': {
    practiceQuestions: [
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q4
      {
        id: 'lesson-17-behavioural-mcq-01',
        question: 'Assuming `register` adds to an `ArrayList` and `orderPlaced` loops through and calls each observer, what gets printed?',
        codeBlock: 'Amazon amazon = new Amazon();\namazon.register(o -> System.out.println("Invoice generated for " + o));\namazon.register(o -> System.out.println("Inventory updated for " + o));\namazon.orderPlaced("ORD123");',
        options: [
          { id: 'a', label: 'A', text: 'Only "Invoice generated for ORD123"' },
          { id: 'b', label: 'B', text: 'Only "Inventory updated for ORD123"' },
          { id: 'c', label: 'C', text: 'Both lines print, in the order they were registered' },
          { id: 'd', label: 'D', text: 'Nothing prints, this code has a compile error' }
        ],
        correctOptionId: 'c',
        explanation: '`orderPlaced` iterates subscribers in insertion order and invokes each, so both lambdas fire in registration order.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q5
      {
        id: 'lesson-17-behavioural-mcq-02',
        question: 'A `RouterFactory` is built like this: When called with `QueryComplexity.COMPLEX`, what happens?',
        codeBlock: 'private static final Map<QueryComplexity, RoutingStrategy> STRATEGIES = Map.of(\n    QueryComplexity.SIMPLE, new SimpleQueryStrategy()\n);\nstatic RoutingStrategy getStrategy(QueryComplexity c) {\n    return STRATEGIES.get(c);\n}',
        options: [
          { id: 'a', label: 'A', text: 'It automatically falls back to `SimpleQueryStrategy`' },
          { id: 'b', label: 'B', text: 'It throws a `ClassNotFoundException` immediately' },
          { id: 'c', label: 'C', text: 'It compiles but silently does nothing' },
          { id: 'd', label: 'D', text: 'It returns `null`, which will likely cause a `NullPointerException` later when a method is called on it' }
        ],
        correctOptionId: 'd',
        explanation: '`Map.get()` returns `null` for a missing key; there is no fallback, so the caller crashes with an NPE the moment it calls a method on the result.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q6
      {
        id: 'lesson-17-behavioural-mcq-03',
        question: 'A payment system tries Razorpay first, then Stripe, then PayPal, only moving to the next provider if the previous one fails. Which pattern best fits this situation?',
        options: [
          { id: 'a', label: 'A', text: 'Neither Strategy nor Observer — this is closer to Chain of Responsibility' },
          { id: 'b', label: 'B', text: 'Strategy, since each payment provider is a different way of paying' },
          { id: 'c', label: 'C', text: 'Observer, since all providers get notified together' },
          { id: 'd', label: 'D', text: 'Factory, since it creates payment objects' }
        ],
        correctOptionId: 'a',
        explanation: 'Strategy picks one implementation up front; Observer notifies all subscribers at once. Sequential try-until-success is Chain of Responsibility.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q7
      {
        id: 'lesson-17-behavioural-mcq-04',
        question: 'Why does a concrete strategy class like `CarPathCalculator` NOT take a `mode` parameter in its methods?',
        options: [
          { id: 'a', label: 'A', text: "Because Java doesn't allow extra parameters in overridden methods" },
          { id: 'b', label: 'B', text: 'Because the class itself already represents one specific way of doing the task, so it doesn\'t need to be told what "mode" it is' },
          { id: 'c', label: 'C', text: 'Because mode is only needed inside the Factory class' },
          { id: 'd', label: 'D', text: "Because strategies are stateless and can't accept any parameters at all" }
        ],
        correctOptionId: 'b',
        explanation: 'The class instance itself already IS the "car mode" implementation; passing a mode flag in would reintroduce the branching Strategy exists to remove.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q8
      {
        id: 'lesson-17-behavioural-mcq-05',
        question: '`VolatilityStrategy.calculate` returns `Math.abs(current - previous)`. What is printed?',
        codeBlock: 'List<TradingIndicatorStrategy> strategies = List.of(new MomentumStrategy(), new VolatilityStrategy());\nfor (TradingIndicatorStrategy s : strategies) {\n    if (s.supportsType("VOLATILITY")) {\n        System.out.println(s.calculate(50, 70));\n    }\n}',
        options: [
          { id: 'a', label: 'A', text: '-20.0' },
          { id: 'b', label: 'B', text: '0.0' },
          { id: 'c', label: 'C', text: '20.0' },
          { id: 'd', label: 'D', text: 'Nothing is printed' }
        ],
        correctOptionId: 'c',
        explanation: 'Only `VolatilityStrategy` matches; `Math.abs(50 - 70) = 20.0`.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q9
      {
        id: 'lesson-17-behavioural-mcq-06',
        question: "A `WeatherMonitoringApplication`'s `setTemperature(double temp)` updates its field but never notifies its registered observers. `TemperatureService` is registered correctly but never receives updates. What is missing?",
        options: [
          { id: 'a', label: 'A', text: 'The `Observer` interface needs a `getTemperature` method' },
          { id: 'b', label: 'B', text: '`observers` should be a `Map` instead of a `List`' },
          { id: 'c', label: 'C', text: '`setTemperature` needs to be declared `static`' },
          { id: 'd', label: 'D', text: 'A call to notify all observers (e.g., looping through observers and calling their update method) inside `setTemperature`' }
        ],
        correctOptionId: 'd',
        explanation: 'Registration only adds to the list; the publisher must explicitly loop and invoke observers whenever state changes. Missing that loop is the most common Observer bug.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q10
      {
        id: 'lesson-17-behavioural-mcq-07',
        question: "Your team's third-party analytics library only understands `trackEvent(XML data)`, but your codebase only works with `log(JSON data)`. Which pattern bridges them without changing either side?",
        options: [
          { id: 'a', label: 'A', text: 'Adapter' },
          { id: 'b', label: 'B', text: 'Strategy' },
          { id: 'c', label: 'C', text: 'Observer' },
          { id: 'd', label: 'D', text: 'Factory' }
        ],
        correctOptionId: 'a',
        explanation: 'Two incompatible interface shapes needing translation without modifying either side is the textbook Adapter scenario.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q11
      {
        id: 'lesson-17-behavioural-mcq-08',
        question: 'Why is it usually fine for a Strategy Factory to reuse the same strategy object every time instead of creating a new one on each call?',
        options: [
          { id: 'a', label: 'A', text: 'Because Java does not allow creating multiple objects of the same class' },
          { id: 'b', label: 'B', text: 'Because most strategy classes have no changing internal state, so sharing one instance (like a Singleton) is safe and avoids unnecessary object creation' },
          { id: 'c', label: 'C', text: 'Because reusing objects makes the code violate Open-Closed Principle' },
          { id: 'd', label: 'D', text: 'Because Factory pattern requires objects to be reused' }
        ],
        correctOptionId: 'b',
        explanation: 'Concrete strategies are typically stateless, so one shared instance behaves identically for every caller.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q12
      {
        id: 'lesson-17-behavioural-mcq-09',
        question: 'What is printed (assuming `Logger.update` prints "LOG: " + event)?',
        codeBlock: 'Publisher publisher = new Publisher();\nLogger logger = new Logger();\npublisher.subscribe(logger);\npublisher.publish("Order Placed");\npublisher.unsubscribe(logger);\npublisher.publish("Order Shipped");',
        options: [
          { id: 'a', label: 'A', text: 'Both "LOG: Order Placed" and "LOG: Order Shipped" print' },
          { id: 'b', label: 'B', text: 'Only "LOG: Order Shipped" prints' },
          { id: 'c', label: 'C', text: 'Only "LOG: Order Placed" prints' },
          { id: 'd', label: 'D', text: 'Nothing is printed' }
        ],
        correctOptionId: 'c',
        explanation: '`logger` is subscribed for the first publish, then unsubscribed before the second — so only the first event reaches it.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q3
      {
        id: 'lesson-17-behavioural-mcq-10',
        question: 'What is the key difference in intent between Strategy and Observer, even though both rely on one interface with multiple implementing classes?',
        options: [
          { id: 'a', label: 'A', text: 'Strategy is only for payments; Observer is only for notifications' },
          { id: 'b', label: 'B', text: 'Strategy picks exactly one implementation to use; Observer notifies many implementations at once' },
          { id: 'c', label: 'C', text: 'Strategy requires a Factory; Observer never uses a Factory' },
          { id: 'd', label: 'D', text: 'There is no real difference between them' }
        ],
        correctOptionId: 'b',
        explanation: 'Strategy delegates to a single chosen algorithm; Observer broadcasts to every registered listener simultaneously.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q5
      {
        id: 'lesson-17-behavioural-mcq-11',
        question: 'What is the main problem with writing one method that uses if-else blocks to handle different "modes" (like car, bike, walk) inside the same class?',
        options: [
          { id: 'a', label: 'A', text: 'It violates Open-Closed and Single Responsibility Principles, since adding a new mode means editing existing working code' },
          { id: 'b', label: 'B', text: 'The code runs slower than using classes' },
          { id: 'c', label: 'C', text: 'Java does not allow more than 3 if-else conditions' },
          { id: 'd', label: 'D', text: 'It cannot be tested using JUnit' }
        ],
        correctOptionId: 'a',
        explanation: 'Every new mode requires reopening and modifying the same method, and one class now owns logic for every mode.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q9
      {
        id: 'lesson-17-behavioural-mcq-12',
        question: 'In the Strategy pattern, what is the actual job of the Factory class (e.g., `PathCalculatorFactory`)?',
        options: [
          { id: 'a', label: 'A', text: 'To decide and return the correct strategy object based on some input' },
          { id: 'b', label: 'B', text: 'To execute the algorithm itself' },
          { id: 'c', label: 'C', text: 'To notify all subscribers when an event occurs' },
          { id: 'd', label: 'D', text: 'To translate one interface into another' }
        ],
        correctOptionId: 'a',
        explanation: "The Factory's only job is selection and construction; the chosen strategy itself executes the algorithm."
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-13',
        question: 'What is the primary purpose of a PRIMARY KEY in a database table?',
        options: [
          { id: 'a', label: 'A', text: 'To uniquely identify each row in the table' },
          { id: 'b', label: 'B', text: 'To link one table to another' },
          { id: 'c', label: 'C', text: 'To make queries run faster automatically' },
          { id: 'd', label: 'D', text: 'To enforce a fixed number of columns' }
        ],
        correctOptionId: 'a',
        explanation: "A primary key's core job is guaranteeing every row is uniquely identifiable; foreign keys (not primary keys) are what link tables together."
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-14',
        question: 'In a Class Diagram, what does a dashed line with a hollow triangle arrowhead represent?',
        options: [
          { id: 'a', label: 'A', text: 'A class implementing an interface' },
          { id: 'b', label: 'B', text: 'A class extending another class' },
          { id: 'c', label: 'C', text: 'Aggregation between two classes' },
          { id: 'd', label: 'D', text: 'Composition between two classes' }
        ],
        correctOptionId: 'a',
        explanation: 'A dashed line with a hollow triangle is realization (implements an interface). A solid line with a hollow triangle is generalization (extends a class).'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-15',
        question: 'One instructor teaches many courses, but each course has only one instructor. Where should the foreign key go?',
        options: [
          { id: 'a', label: 'A', text: 'In the instructors table' },
          { id: 'b', label: 'B', text: 'In the courses table' },
          { id: 'c', label: 'C', text: 'In both tables at once' },
          { id: 'd', label: 'D', text: 'In a separate junction table' }
        ],
        correctOptionId: 'b',
        explanation: 'The foreign key always lives on the "many" side of a one-to-many relationship, so `instructor_id` belongs in the `courses` table.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-16',
        question: 'In a Use Case Diagram, "Enroll in Course" always triggers "Make Payment" — there\'s no scenario where enrollment happens without it. What relationship connects these two use cases?',
        options: [
          { id: 'a', label: 'A', text: 'Extends' },
          { id: 'b', label: 'B', text: 'Actor' },
          { id: 'c', label: 'C', text: 'System Boundary' },
          { id: 'd', label: 'D', text: 'Includes' }
        ],
        correctOptionId: 'd',
        explanation: 'A solid **includes** arrow means the parent use case always triggers the child. **Extends** (dashed) would be for an optional variant, like "Pay by UPI" extending "Make Payment".'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-17',
        question: 'Current rows (id, student_id, course_id): (1, 1, 1), (2, 1, 2), (3, 2, 1). How many courses is the student with id = 1 enrolled in?',
        codeBlock: 'CREATE TABLE enrollments (\n  id INT PRIMARY KEY, student_id INT, course_id INT,\n  FOREIGN KEY (student_id) REFERENCES students(id),\n  FOREIGN KEY (course_id) REFERENCES courses(id)\n);',
        options: [
          { id: 'a', label: 'A', text: '3' },
          { id: 'b', label: 'B', text: '0' },
          { id: 'c', label: 'C', text: '2' },
          { id: 'd', label: 'D', text: '1' }
        ],
        correctOptionId: 'c',
        explanation: 'Rows with `student_id = 1` are (1,1,1) and (2,1,2), referencing `course_id` 1 and 2 — two distinct courses.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-18',
        question: 'What is the main purpose of normalization in database schema design?',
        options: [
          { id: 'a', label: 'A', text: 'To duplicate frequently-used data across tables for faster reads' },
          { id: 'b', label: 'B', text: 'To store each fact only once and reference it elsewhere with a foreign key, avoiding out-of-sync copies' },
          { id: 'c', label: 'C', text: 'To ensure every table has exactly the same number of columns' },
          { id: 'd', label: 'D', text: 'To turn every relationship into a many-to-many relationship' }
        ],
        correctOptionId: 'b',
        explanation: "Normalization's goal is eliminating duplicate, potentially-inconsistent copies of the same fact by storing it once and referencing it via foreign key."
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-19',
        question: 'A library system has `Book` and `Author`. One book can have multiple authors, one author can write multiple books, and the relationship needs no extra data (no dates, no royalty percentage). Which Hibernate approach fits best?',
        options: [
          { id: 'a', label: 'A', text: 'Manually create a `BookAuthor` entity class, similar to how `Enrollment` was modeled' },
          { id: 'b', label: 'B', text: 'Use a plain `@ManyToMany` annotation directly between `Book` and `Author`, since no extra data needs to be stored' },
          { id: 'c', label: 'C', text: 'Use `@OneToMany` on both sides' },
          { id: 'd', label: 'D', text: 'Store author names as a comma-separated column inside books' }
        ],
        correctOptionId: 'b',
        explanation: 'A plain `@ManyToMany` is exactly right when the relationship itself carries no additional data — a full entity is only needed once the relationship needs its own fields.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-20',
        question: 'Given a Hibernate `Enrollment` entity with `@ManyToOne` to both `Student` and `Course`, plus its own `enrolledAt` field, why was `Enrollment` modeled as its own full entity instead of a plain `@ManyToMany` between `Student` and `Course`?',
        options: [
          { id: 'a', label: 'A', text: "@ManyToMany doesn't exist in Hibernate" },
          { id: 'b', label: 'B', text: '`@ManyToOne` runs faster than `@ManyToMany` in every case' },
          { id: 'c', label: 'C', text: "The relationship itself carries extra data (`enrolledAt`), which a plain `@ManyToMany` junction table can't hold — so it needs to be a real entity" },
          { id: 'd', label: 'D', text: 'Student and Course cannot have a many-to-many relationship' }
        ],
        correctOptionId: 'c',
        explanation: "The moment a many-to-many relationship needs to carry its own data, a plain `@ManyToMany` junction table (which only holds the two foreign keys) is insufficient — the relationship must be promoted to its own entity."
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-21',
        question: 'A junior developer wanted to model aggregation between `Car` and `Driver` (a driver should exist independently of any car): What\'s wrong, and what\'s the fix?',
        codeBlock: 'public class Car {\n  private final Driver driver;\n  public Car() {\n    this.driver = new Driver(); // Car creates its own Driver internally\n  }\n}',
        options: [
          { id: 'a', label: 'A', text: 'Nothing is wrong — this already models aggregation correctly' },
          { id: 'b', label: 'B', text: '`Driver` should be marked `static`' },
          { id: 'c', label: 'C', text: '`final` should be removed from the field' },
          { id: 'd', label: 'D', text: "The `Car` constructor creates and owns the `Driver` internally, which is composition-like behavior — fix it by passing an existing `Driver` object into the constructor instead" }
        ],
        correctOptionId: 'd',
        explanation: "Constructing the dependency internally makes the `Car` own the `Driver`'s lifecycle (composition-like), which contradicts the stated goal of aggregation. Passing an already-existing `Driver` in via the constructor (dependency injection) is what actually models independent lifecycles."
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-22',
        question: 'A hospital has a `Department` class and a `Doctor` class. A doctor belongs to one department at a time, but if a department is dissolved, doctors continue to exist and can be reassigned elsewhere. Which pair correctly identifies the relationship type AND the foreign key placement?',
        options: [
          { id: 'a', label: 'A', text: 'Aggregation, with `department_id` placed inside the `doctors` table' },
          { id: 'b', label: 'B', text: 'Composition, with `department_id` placed inside the `doctors` table' },
          { id: 'c', label: 'C', text: 'Aggregation, with `doctor_id` placed inside the `departments` table' },
          { id: 'd', label: 'D', text: 'Composition, with `doctor_id` placed inside the `departments` table' }
        ],
        correctOptionId: 'a',
        explanation: 'Doctors outliving their department\'s dissolution is the definition of aggregation (independent lifecycles). The foreign key still follows the standard one-to-many rule: it lives on the "many" side (`doctors`), pointing back to the one `department`.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-23',
        question: 'A teammate wrote this schema for a blog, where one post can have many comments: What is the main problem, and what\'s the correct fix?',
        codeBlock: 'CREATE TABLE posts (\n  id INT PRIMARY KEY, title VARCHAR(255),\n  comment_1 VARCHAR(500), comment_2 VARCHAR(500), comment_3 VARCHAR(500)\n);',
        options: [
          { id: 'a', label: 'A', text: 'A fixed number of comment columns caps the relationship — create a separate `comments` table with a `post_id` foreign key instead' },
          { id: 'b', label: 'B', text: '`id` should not be declared as a primary key' },
          { id: 'c', label: 'C', text: '`title` should be split into two columns' },
          { id: 'd', label: 'D', text: 'The comments should be merged into one column separated by commas' }
        ],
        correctOptionId: 'a',
        explanation: 'Hardcoding a fixed number of columns for what is really a one-to-many relationship caps it artificially (a 4th comment has nowhere to go) and wastes space for posts with fewer comments. The fix is a proper `comments` table with a foreign key back to `posts`.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-24',
        question: 'A teammate wrote this schema for an orders system, where a separate `customers` table already stores customer details: What\'s wrong with this design, and what\'s the fix?',
        codeBlock: 'CREATE TABLE orders (\n  id INT PRIMARY KEY, customer_name VARCHAR(255),\n  customer_email VARCHAR(255), product VARCHAR(255)\n);',
        options: [
          { id: 'a', label: 'A', text: 'Nothing is wrong — storing the name and email directly avoids extra joins' },
          { id: 'b', label: 'B', text: '`product` should be split into `product_name` and `product_price`' },
          { id: 'c', label: 'C', text: '`id` should not be declared as a primary key since orders can repeat' },
          { id: 'd', label: 'D', text: '`customer_name` and `customer_email` duplicate data that already lives in `customers` — replace both with a single `customer_id` foreign key instead' }
        ],
        correctOptionId: 'd',
        explanation: 'This is a direct normalization violation: customer data is duplicated into every order row instead of referenced once via foreign key, risking the two copies going out of sync if a customer updates their email.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-25',
        question: 'A ride-sharing app\'s `Trip` class has a `List<RouteCoordinate>` — the GPS points making up that specific trip\'s path. If the trip record is deleted, those exact coordinates have no meaning anywhere else in the system. Which combination correctly describes the relationship and its notation?',
        options: [
          { id: 'a', label: 'A', text: 'Association without ownership — plain line, no diamond' },
          { id: 'b', label: 'B', text: 'Inheritance — hollow triangle' },
          { id: 'c', label: 'C', text: 'Aggregation — hollow diamond' },
          { id: 'd', label: 'D', text: 'Composition — filled diamond' }
        ],
        correctOptionId: 'd',
        explanation: 'The route coordinates cannot outlive the trip they belong to (they have no independent meaning), which is composition, notated with a filled diamond on the `Trip` end.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-26',
        question: 'In a many-to-many junction table like `enrollments`, some teams skip a separate surrogate `id` column entirely and instead make the combination of both foreign keys (`student_id` + `course_id` together) the primary key. What is this called?',
        options: [
          { id: 'a', label: 'A', text: 'A composite primary key' },
          { id: 'b', label: 'B', text: 'A duplicate key' },
          { id: 'c', label: 'C', text: 'A foreign primary key' },
          { id: 'd', label: 'D', text: 'A static key' }
        ],
        correctOptionId: 'a',
        explanation: 'A primary key made of more than one column is a composite primary key; it works here because the pairing of the two foreign keys is already guaranteed unique.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-27',
        question: 'When Hibernate generates the table for this class, what column represents the relationship with `Instructor`?',
        codeBlock: '@Entity\npublic class Course {\n  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)\n  private Long id;\n  private String title;\n  @ManyToOne\n  @JoinColumn(name = "instructor_id")\n  private Instructor instructor;\n}',
        options: [
          { id: 'a', label: 'A', text: '`instructor` (storing the full object)' },
          { id: 'b', label: 'B', text: '`instructor_name`' },
          { id: 'c', label: 'C', text: '`instructor_id`' },
          { id: 'd', label: 'D', text: 'No column — a junction table is created instead' }
        ],
        correctOptionId: 'c',
        explanation: '`@JoinColumn(name = "instructor_id")` tells Hibernate to store the relationship as a plain foreign-key column named `instructor_id` on the `Course` table, matching the standard one-to-many FK placement rule.'
      },
      // SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams
      {
        id: 'lesson-17-behavioural-mcq-28',
        question: 'A banking app allows joint accounts — one account can have multiple owners, and one person can be an owner on multiple accounts. How should this be modeled in the schema?',
        options: [
          { id: 'a', label: 'A', text: 'Add an `owner_id` column directly inside `accounts`' },
          { id: 'b', label: 'B', text: 'Create a separate junction table (e.g. `account_owners`) holding `account_id` and `owner_id`' },
          { id: 'c', label: 'C', text: 'Add an `account_id` column directly inside `owners`' },
          { id: 'd', label: 'D', text: 'Store all owner names as a comma-separated list inside `accounts`' }
        ],
        correctOptionId: 'b',
        explanation: 'A many-to-many relationship (many accounts to many owners) requires a junction table holding both foreign keys; a single column on either side cannot represent a many-to-many link.'
      }
    ]
  }
};

export function getLessonInteractions(courseSlug, moduleSlug, lessonSlug) {
  return lessonInteractions[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonInteractions;
