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
  }
};

export function getLessonInteractions(courseSlug, moduleSlug, lessonSlug) {
  return lessonInteractions[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonInteractions;
