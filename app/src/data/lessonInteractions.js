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
  },
  'fde-curriculum/agentic-ai-core/01-genai-world-and-llm-landscape': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-01-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — TRAINING STAGES & BEHAVIOR',
        question:
          'Two models have near-identical pretraining corpora and knowledge cutoffs, but one follows multi-step instructions reliably and the other frequently ignores part of a compound instruction. Which stage most likely explains the difference?',
        options: [
          { id: 'a', label: 'A', text: 'Pretraining — one model must have seen more text' },
          { id: 'b', label: 'B', text: 'Supervised fine-tuning — instruction-following quality is primarily learned during SFT on instruction-response pairs' },
          { id: 'c', label: 'C', text: 'Tokenization — one model must use a larger vocabulary' },
          { id: 'd', label: 'D', text: 'Context window size' }
        ],
        correctOptionId: 'b',
        explanation:
          'Pretraining teaches broad language and world statistics; it does not teach the model to follow a chat/instruction format or track multiple sub-instructions. That behavior is trained during SFT on curated instruction-response data, which is why two models with similar pretraining can diverge sharply in instruction-following.',
        incorrectExplanation:
          'Consider which training stage is responsible for teaching a model to adopt a chat role and follow complex instructions versus just predicting text statistics.',
        hint: 'Pretraining learns general world statistics; supervised fine-tuning (SFT) on curated instruction pairs teaches instruction following.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-01-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — BENCHMARK PARITY & CALIBRATION',
        question:
          'Two models score nearly identically on a public benchmark, but in a specific customer workflow one is noticeably more prone to overconfident wrong answers than the other. What does the lesson\'s framework suggest is the most likely source of this difference?',
        options: [
          { id: 'a', label: 'A', text: 'Their tokenizers must differ' },
          { id: 'b', label: 'B', text: 'One model must have a smaller context window' },
          { id: 'c', label: 'C', text: 'The difference likely lives in preference optimization (RLHF/DPO) calibration — how strongly the model was rewarded for assertive-sounding answers versus appropriately hedged ones — not in raw pretraining knowledge' },
          { id: 'd', label: 'D', text: 'Benchmark scores always predict production calibration directly' }
        ],
        correctOptionId: 'c',
        explanation:
          'Benchmark parity mostly reflects pretraining-era capability and broad instruction-following. Calibration — how appropriately a model signals uncertainty versus sounding confident — is shaped by the preference-optimization stage, which benchmarks often under-measure. Two similarly-scoring models can diverge exactly here.',
        incorrectExplanation:
          'Look beyond raw pretraining knowledge to how model tone and confidence calibration are trained during preference optimization.',
        hint: 'Calibration and hedging behavior are shaped during preference optimization (RLHF/DPO), which standard benchmark scores often fail to capture.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-01-mcq-01',
        question:
          'A decoder-only LLM confidently states an incorrect fact in response to a question about a niche, rarely-discussed topic. What is the most accurate explanation for this behavior?',
        options: [
          { id: 'a', label: 'A', text: 'The model has a database lookup that failed silently' },
          { id: 'b', label: 'B', text: 'The model is predicting the statistically most likely next tokens given its training distribution, which didn\'t densely cover this topic — this is expected behavior, not a malfunction' },
          { id: 'c', label: 'C', text: 'The model\'s context window overflowed and corrupted the output' },
          { id: 'd', label: 'D', text: 'The model intentionally lies when it doesn\'t know an answer' }
        ],
        correctOptionId: 'b',
        explanation:
          'LLMs have no built-in fact database and no explicit "I don\'t know" state unless trained in. Confident wrong answers on sparse topics are next-token prediction behaving normally on thin training signal, which is why grounding and verification steps are architectural necessities, not optional polish.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-01-mcq-02',
        question:
          'An FDE is building a feature that classifies incoming support tickets into one of five fixed categories using a short, well-defined prompt. What is the strongest reason to prefer a small, fast model over the frontier "reasoning" tier for this task?',
        options: [
          { id: 'a', label: 'A', text: 'Small models are always more accurate than large models' },
          { id: 'b', label: 'B', text: 'Frontier models cannot be used for classification tasks' },
          { id: 'c', label: 'C', text: 'Fixed-category classification rarely benefits from deeper reasoning, so a smaller model likely clears the accuracy bar at a fraction of the latency and cost' },
          { id: 'd', label: 'D', text: 'Small models have larger context windows' }
        ],
        correctOptionId: 'c',
        explanation:
          'The right model tier is the smallest one that reliably clears the task\'s accuracy bar. Fixed-category classification is a shallow task where a small model\'s capability is usually sufficient, so paying frontier-tier latency and cost for it is waste, not safety margin.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-01-mcq-03',
        question:
          'A customer in a regulated industry wants no customer data leaving their own infrastructure, even to a vendor API. What does this constraint most directly push the FDE toward?',
        options: [
          { id: 'a', label: 'A', text: 'Using the largest frontier model available, regardless of hosting' },
          { id: 'b', label: 'B', text: 'An open-weight model self-hosted inside the customer\'s infrastructure, trading operational burden for data control' },
          { id: 'c', label: 'C', text: 'A hosted model with a longer context window' },
          { id: 'd', label: 'D', text: 'This constraint has no effect on model choice' }
        ],
        correctOptionId: 'b',
        explanation:
          'Open-weight models are the option that lets an organization keep inference entirely inside its own infrastructure. It costs more in operational effort (hosting, scaling, updating the model) but directly satisfies a hard data-residency constraint that no hosted API can.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-01-mcq-04',
        question:
          'What happens to information from earlier in a conversation once it falls outside the model\'s context window?',
        options: [
          { id: 'a', label: 'A', text: 'It is no longer visible to the model at all for that call — there is no persistent memory beyond the context window unless the application re-supplies it' },
          { id: 'b', label: 'B', text: 'The model retrieves it automatically from a hidden memory store' },
          { id: 'c', label: 'C', text: 'It is compressed and summarized automatically by the model' },
          { id: 'd', label: 'D', text: 'It is stored permanently in the model\'s weights' }
        ],
        correctOptionId: 'a',
        explanation:
          'The model has no memory beyond what\'s in its context window for that specific call. Anything the application wants remembered across turns must be re-supplied (verbatim, summarized, or retrieved) by the calling system — this is exactly the gap RAG and conversation-memory systems exist to fill.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-01-mcq-05',
        question:
          'In the support-copilot scenario, what is the most defensible first signal to use for routing a question to a cheap model versus the frontier model?',
        options: [
          { id: 'a', label: 'A', text: 'The time of day the question was asked' },
          { id: 'b', label: 'B', text: 'A cheap, fast complexity signal (e.g. question length, presence of multiple sub-questions, or a lightweight classifier) computed before the expensive model call' },
          { id: 'c', label: 'C', text: 'Always route to the frontier model first and downgrade later' },
          { id: 'd', label: 'D', text: 'The user\'s job title' }
        ],
        correctOptionId: 'b',
        explanation:
          'Routing only pays off if the classification step itself is cheap relative to the savings — a lightweight heuristic or small classifier call, evaluated before any expensive model call, is what makes the routing economically worthwhile. Routing "after" the frontier call defeats the purpose.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-01-mcq-06',
        question:
          'A three-tier routing system sends a query to the small model, which returns a low-confidence or malformed response. What is the correct next step in a well-designed routing system?',
        options: [
          { id: 'a', label: 'A', text: 'Return the weak answer to the user regardless' },
          { id: 'b', label: 'B', text: 'Silently drop the query' },
          { id: 'c', label: 'C', text: 'Escalate the same query to the next model tier up, since the small model\'s own output signaled it likely couldn\'t handle this case' },
          { id: 'd', label: 'D', text: 'Retry the identical call on the same small model' }
        ],
        correctOptionId: 'c',
        explanation:
          'A routing system is only safe to ship if it has an escalation path for cases the cheap tier can\'t handle. Detecting a low-confidence or invalid response and escalating to the next tier preserves the cost savings on the easy majority of traffic without sacrificing quality on the hard minority.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/02-prompt-engineering-basics': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-02-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — PROMPT AS SPECIFICATION',
        question:
          'A prompt asks for "a JSON object with the order details" and, across ten calls, the model sometimes returns `quantity` as a number and sometimes as a word like "two". What is the root cause?',
        options: [
          { id: 'a', label: 'A', text: 'The model is malfunctioning and needs a different provider' },
          { id: 'b', label: 'B', text: 'The prompt never specified the field\'s type, so the model resolves that ambiguity differently each call' },
          { id: 'c', label: 'C', text: 'JSON output is inherently non-deterministic and cannot be fixed' },
          { id: 'd', label: 'D', text: 'The email inputs must have been inconsistent, not the prompt' }
        ],
        correctOptionId: 'b',
        explanation:
          'Every unspecified detail in a prompt is a degree of freedom the model resolves arbitrarily. An explicit schema (`quantity: integer`) removes that ambiguity and is the direct fix, not a different model or provider.',
        incorrectExplanation:
          'Consider whether the prompt provided an unambiguous schema contract specifying types, or left degrees of freedom for the model to resolve.',
        hint: 'Every unspecified property or data type in a prompt becomes an arbitrary degree of freedom resolved inconsistently across calls.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-02-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — FEW-SHOT ANCHORING RISKS',
        question:
          'An FDE adds four few-shot examples to fix an extraction task\'s format, but the model starts defaulting to one specific example\'s quantity value even for unrelated emails. What does this indicate?',
        options: [
          { id: 'a', label: 'A', text: 'The model needs even more examples to correct this' },
          { id: 'b', label: 'B', text: 'The model is anchoring on a superficial pattern from the examples (e.g. always echoing a specific value) rather than the intended format rule, and the example set needs to be reduced or diversified' },
          { id: 'c', label: 'C', text: 'This is expected and requires no fix, since few-shot prompting always causes this' },
          { id: 'd', label: 'D', text: 'The prompt\'s system message must be too short' }
        ],
        correctOptionId: 'b',
        explanation:
          'Adding examples without checking what pattern the model is actually anchoring on can backfire — a single well-chosen example isolating the real format decision often beats several loosely related ones that introduce spurious patterns.',
        incorrectExplanation:
          'Examine whether the added examples introduced unintended superficial patterns that the model is anchoring on instead of the general format rule.',
        hint: 'Too many or poorly isolated few-shot examples can cause the model to latch onto specific values rather than the structural format.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-02-mcq-01',
        question:
          'Why is task-specific data (like a customer email to be processed) usually a poor fit for the system message, even though the system message is technically capable of holding any text?',
        options: [
          { id: 'a', label: 'A', text: 'System messages have a hard length limit smaller than user messages' },
          { id: 'b', label: 'B', text: 'The system message is meant to carry persistent, reusable behavior rules; mixing in per-request data makes the prompt harder to reuse and harder to defend against injection' },
          { id: 'c', label: 'C', text: 'Models ignore data placed in the system message' },
          { id: 'd', label: 'D', text: 'System messages are only visible to the model, never logged' }
        ],
        correctOptionId: 'b',
        explanation:
          'The system/user/assistant split exists to separate persistent behavior from per-request data. Dumping task data into the system prompt defeats that separation of concerns and, as later lessons cover, widens the injection attack surface.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-02-mcq-02',
        question:
          'A summarization task performs consistently well with a plain instruction and no examples. An unusual internal ticket-tagging format performs inconsistently the same way. What does this contrast suggest about when few-shot prompting earns its keep?',
        options: [
          { id: 'a', label: 'A', text: 'Few-shot prompting should always be used regardless of task' },
          { id: 'b', label: 'B', text: 'Few-shot examples help most when the output format is unusual or domain-specific and the model\'s training distribution doesn\'t already encode the expected shape' },
          { id: 'c', label: 'C', text: 'Summarization always requires more examples than tagging' },
          { id: 'd', label: 'D', text: 'Few-shot prompting is only useful for translation tasks' }
        ],
        correctOptionId: 'b',
        explanation:
          'Zero-shot works when the task is common enough that the model already "knows" the expected output shape. Few-shot earns its cost when the format is unusual or inconsistent under zero-shot — exactly the ticket-tagging case, not the summarization case.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-02-mcq-03',
        question:
          'An extraction prompt\'s schema doesn\'t specify what to do when `delivery_date` isn\'t mentioned in the source email. What is the most likely observable consequence?',
        options: [
          { id: 'a', label: 'A', text: 'The model will handle the missing field inconsistently across calls — sometimes omitting the key, sometimes using an empty string, sometimes guessing a date' },
          { id: 'b', label: 'B', text: 'The model will always omit the field consistently' },
          { id: 'c', label: 'C', text: 'The API call will fail with a validation error' },
          { id: 'd', label: 'D', text: 'The model will always insert today\'s date' }
        ],
        correctOptionId: 'a',
        explanation:
          'Just like field typing, missing-field handling is a specification gap the model resolves arbitrarily and inconsistently unless the prompt states the rule explicitly (e.g. "use null if not mentioned in the email").'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-02-mcq-04',
        question:
          'Why wrap the customer email being processed in a labeled fenced block like `<EMAIL>...</EMAIL>` instead of pasting it directly after the instructions?',
        options: [
          { id: 'a', label: 'A', text: 'It reduces the token count of the prompt' },
          { id: 'b', label: 'B', text: 'It clearly separates instructions from the data being processed, which improves output quality and is a first line of defense against the data itself being interpreted as instructions' },
          { id: 'c', label: 'C', text: 'It is required by every LLM API\'s syntax' },
          { id: 'd', label: 'D', text: 'It has no real effect, it\'s purely stylistic' }
        ],
        correctOptionId: 'b',
        explanation:
          'A clear delimiter helps the model distinguish "text to process" from "instructions to follow" — both a quality improvement (less confusion about what to act on) and the first defensive layer against prompt injection, covered in depth next lesson.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-02-mcq-05',
        question:
          'After rewriting the extraction prompt with an explicit schema, what is the correct way to confirm the fix actually worked before shipping it?',
        options: [
          { id: 'a', label: 'A', text: 'Read the three outputs and judge by eye whether they look reasonable' },
          { id: 'b', label: 'B', text: 'Programmatically validate each output against the schema (types, required/optional fields) across a representative test set, not just eyeball it' },
          { id: 'c', label: 'C', text: 'Assume the schema in the prompt guarantees the output matches it' },
          { id: 'd', label: 'D', text: 'Only test with the exact email used to originally write the prompt' }
        ],
        correctOptionId: 'b',
        explanation:
          'A schema in the prompt is a strong instruction, not a guarantee — the model can still drift. Programmatic validation against the schema, across a representative set of inputs (including edge cases), is what would actually catch drift before it reaches production.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-02-mcq-06',
        question:
          'Compared to a transcription field like `item_name` (copied near-verbatim from the email), why does a judgment field like `urgency: "low" | "medium" | "high"` typically need more careful few-shot examples?',
        options: [
          { id: 'a', label: 'A', text: 'Judgment fields are always shorter, so they need less context' },
          { id: 'b', label: 'B', text: 'A judgment field requires the model to infer a category from tone and content rather than copy text, so the model has more freedom to interpret the rule differently without concrete examples anchoring the boundary' },
          { id: 'c', label: 'C', text: 'Transcription fields are technically impossible without few-shot examples' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference between the two field types' }
        ],
        correctOptionId: 'b',
        explanation:
          'Transcription is close to copying, which zero-shot instructions handle well. A judgment field asks the model to apply a rule it has to infer, and examples that show where the category boundary falls (e.g. what makes an email "high" vs "medium" urgency) reduce that ambiguity far more than for a transcription field.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/03-advanced-prompting-and-ai-safety-basics': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-03-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — STRUCTURAL NATURE OF PROMPT INJECTION',
        question:
          'What makes prompt injection a structural risk of LLM architecture rather than a bug fixable purely with better prompt wording?',
        options: [
          { id: 'a', label: 'A', text: 'LLM APIs have no way to send a system message at all' },
          { id: 'b', label: 'B', text: 'The model cannot structurally distinguish developer instructions from instructions that happen to appear inside data it\'s processing — both arrive as tokens in the same context window' },
          { id: 'c', label: 'C', text: 'Injection only affects models with very small context windows' },
          { id: 'd', label: 'D', text: 'It only happens when the model is run at high temperature' }
        ],
        correctOptionId: 'b',
        explanation:
          'Because system instructions and untrusted data both become part of the same token sequence, there\'s no hard architectural boundary preventing data from being interpreted as instructions — better wording reduces the risk but cannot eliminate it, which is why layered defenses (not prompt wording alone) are required.',
        incorrectExplanation:
          'Think about how developer instructions and retrieved data are processed together as tokens in the same context window.',
        hint: 'Both developer instructions and untrusted input data enter the model as an indistinguishable sequence of tokens in the same context window.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-03-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — DETERMINISTIC OUTPUT VALIDATION',
        question:
          'Why does the lesson describe deterministic output validation (checking a tool call\'s parameters against independently-computed values before execution) as the defense layer that "actually holds," compared to instruction-hierarchy wording alone?',
        options: [
          { id: 'a', label: 'A', text: 'Instruction-hierarchy wording has no effect at all and should be skipped' },
          { id: 'b', label: 'B', text: 'Instruction-hierarchy wording reduces but cannot eliminate the risk, since the model is still just predicting tokens; a deterministic check outside the model\'s control blocks an unauthorized action regardless of what the model was manipulated into deciding' },
          { id: 'c', label: 'C', text: 'Deterministic validation replaces the need for privilege separation' },
          { id: 'd', label: 'D', text: 'Output validation is only needed for read-only tool calls' }
        ],
        correctOptionId: 'b',
        explanation:
          'Prompt-level defenses (instruction hierarchy, delimiters) reduce the probability of a successful injection but remain probabilistic, since they operate inside the same token-prediction process being attacked. A deterministic, non-model check on the actual side-effecting call is the layer that provides a hard guarantee.',
        incorrectExplanation:
          'Compare probabilistic token prediction inside the model context with deterministic code execution checks outside the model.',
        hint: 'Prompt instructions are probabilistic; deterministic code validation outside the LLM context is the only layer that enforces hard security guarantees.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-03-mcq-01',
        question:
          'For which of the following tasks is chain-of-thought prompting most likely to meaningfully improve accuracy?',
        options: [
          { id: 'a', label: 'A', text: 'Naming the capital city of a well-known country' },
          { id: 'b', label: 'B', text: 'Deciding whether a multi-line expense report complies with three separate reimbursement policy rules' },
          { id: 'c', label: 'C', text: 'Translating a single short sentence' },
          { id: 'd', label: 'D', text: 'Returning a fixed greeting message' }
        ],
        correctOptionId: 'b',
        explanation:
          'CoT helps most on genuine multi-step logic where committing to intermediate reasoning steps as tokens improves the final answer. Single-step lookups or fixed responses gain nothing from it and only add latency and cost.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-03-mcq-02',
        question:
          'Why is decomposing a large ambiguous request into an explicit sequence of smaller prompts generally more reliable than one prompt doing everything at once?',
        options: [
          { id: 'a', label: 'A', text: 'Smaller prompts always run faster regardless of task' },
          { id: 'b', label: 'B', text: 'Each intermediate output can be validated before it feeds the next step, catching errors early — the same reasoning that favors small, testable functions over one large one' },
          { id: 'c', label: 'C', text: 'Models cannot process large prompts at all' },
          { id: 'd', label: 'D', text: 'Decomposition eliminates the need for any validation' }
        ],
        correctOptionId: 'b',
        explanation:
          'The reliability gain comes from being able to check each step\'s output before it becomes input to the next, not from raw speed. This mirrors why composing small, testable functions is more reliable than one large opaque one in traditional software.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-03-mcq-03',
        question:
          'A malicious instruction hidden inside a support ticket\'s body text, intended to manipulate a downstream tool-calling agent, is an example of which kind of prompt injection?',
        options: [
          { id: 'a', label: 'A', text: 'Direct injection' },
          { id: 'b', label: 'B', text: 'Indirect injection' },
          { id: 'c', label: 'C', text: 'Neither — this is a data validation bug unrelated to injection' },
          { id: 'd', label: 'D', text: 'A model hallucination' }
        ],
        correctOptionId: 'b',
        explanation:
          'Indirect injection is instructions hidden inside data the system retrieves and feeds to the model — a ticket body, a fetched webpage, a document — as opposed to a user typing an override directly into the chat (direct injection). It\'s the more dangerous case in FDE-style integrations because the injected content arrives through a "trusted" data pipeline.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-03-mcq-04',
        question:
          'What does "privilege separation" mean in the context of a support-ticket triage agent that has an `issue_refund` tool available?',
        options: [
          { id: 'a', label: 'A', text: 'The agent should have unrestricted access to all tools to maximize flexibility' },
          { id: 'b', label: 'B', text: 'The agent\'s tool-calling permissions should be scoped to the minimum required for its task — e.g. a hard cap far below any large refund amount, with anything above requiring separate human-reviewed approval' },
          { id: 'c', label: 'C', text: 'Every tool call must be logged, regardless of what permissions it has' },
          { id: 'd', label: 'D', text: 'The agent should never be allowed to call any tool' }
        ],
        correctOptionId: 'b',
        explanation:
          'Privilege separation limits the blast radius of a successful injection: even if the model is manipulated into deciding to issue a large refund, a hard-capped tool permission prevents that decision from executing as a large unauthorized action.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-03-mcq-05',
        question:
          'What is the appropriate default for actions where a false positive is expensive (e.g. issuing a large refund), according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Fully automate the action from day one to reduce latency' },
          { id: 'b', label: 'B', text: 'Require explicit human confirmation by default, and only relax it once the system has enough measured accuracy and audit trail to justify doing so — even then, degrading to sampled review rather than removing the gate entirely' },
          { id: 'c', label: 'C', text: 'Never automate any part of the workflow' },
          { id: 'd', label: 'D', text: 'Automate the action but disable logging to reduce noise' }
        ],
        correctOptionId: 'b',
        explanation:
          'Human-in-the-loop is the safe default for high-stakes, hard-to-reverse actions. Relaxing it should be earned with measured accuracy and audit trail, and even then a degrade-to-sampling approach preserves some oversight rather than full removal.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-03-mcq-06',
        question:
          'In the scenario\'s fix, the refund amount from the model\'s tool call is checked against a value looked up independently from the customer\'s order database. Why is this specifically effective against the injection example given?',
        options: [
          { id: 'a', label: 'A', text: 'It prevents the model from ever calling the refund tool' },
          { id: 'b', label: 'B', text: 'The injected instruction ("$9,999... pre-approved") only exists inside the model\'s context; an independently computed order value from a separate system is unaffected by anything in the ticket text, so a mismatch reliably surfaces the manipulation' },
          { id: 'c', label: 'C', text: 'It removes the need for a refund cap' },
          { id: 'd', label: 'D', text: 'It only works if the ticket is in a specific language' }
        ],
        correctOptionId: 'b',
        explanation:
          'The defense works because the validation source is entirely outside the model\'s influence — no amount of injected text in the ticket can change what the order database independently reports, so a mismatch between the model\'s proposed amount and the ground-truth value is a reliable signal.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-03-mcq-07',
        question:
          'A triage agent is given a tool that can not only issue refunds but also permanently delete customer accounts, even though deletion is never part of its actual task. Which OWASP-style LLM risk does this best illustrate?',
        options: [
          { id: 'a', label: 'A', text: 'Sensitive information disclosure' },
          { id: 'b', label: 'B', text: 'Excessive agency — the agent holds more capability than its task requires, widening the blast radius of any manipulation' },
          { id: 'c', label: 'C', text: 'Training data poisoning' },
          { id: 'd', label: 'D', text: 'Model denial of service' }
        ],
        correctOptionId: 'b',
        explanation:
          'Excessive agency is granting an LLM-driven system more permissions or capability than the task genuinely needs. Here, account deletion capability has nothing to do with refund triage, so its mere presence is a risk independent of whether injection ever succeeds — directly reinforcing the privilege-separation principle from this lesson.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/04-llm-built-in-power-tools': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-04-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — FUNCTION CALLING MECHANISM',
        question:
          'When a model "calls" a described function during a chat completion, what actually happens?',
        options: [
          { id: 'a', label: 'A', text: 'The model directly executes the function on the vendor\'s servers' },
          { id: 'b', label: 'B', text: 'The model returns a structured proposal (function name and arguments) for your own code to decide whether and how to execute' },
          { id: 'c', label: 'C', text: 'The function runs automatically inside the model\'s context window' },
          { id: 'd', label: 'D', text: 'The model modifies its own weights to include the function\'s logic' }
        ],
        correctOptionId: 'b',
        explanation:
          'Function/tool calling is the model proposing a structured call; your application code decides whether to actually execute it and feeds the result back. This seam is exactly where output validation and privilege-separation defenses attach.',
        incorrectExplanation:
          'Distinguish between the model proposing structured arguments and your host application actually executing code.',
        hint: 'The LLM never directly executes tools; it generates a structured proposal for your application runtime to validate and execute.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-04-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — TOOL PROPOSAL VALIDATION SEAM',
        question:
          'Why does the fact that function calling only ever produces a proposed call (not an executed action) matter for the injection defenses covered in the previous lesson?',
        options: [
          { id: 'a', label: 'A', text: 'It means injection defenses are unnecessary since the model never executes anything' },
          { id: 'b', label: 'B', text: 'It means the deterministic output-validation and privilege-separation checks have a concrete point to attach to — your own code, not the model, makes the final decision to execute, so those defenses can actually intercept a manipulated call before it runs' },
          { id: 'c', label: 'C', text: 'It means every function call is automatically safe' },
          { id: 'd', label: 'D', text: 'It has no relationship to injection defenses' }
        ],
        correctOptionId: 'b',
        explanation:
          'The gap between "model proposes a call" and "your code executes it" is exactly the seam where validation and privilege separation are enforced. If the model executed actions directly, there would be no interception point at all.',
        incorrectExplanation:
          'Consider where deterministic security checks, parameter validation, and privilege bounds can intercept side-effecting operations.',
        hint: 'The interception point between the proposed function call and host execution is where deterministic validation and privilege caps attach.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-04-mcq-01',
        question:
          'How does schema-constrained "structured output" differ from simply asking the model in the prompt to "return JSON matching this schema"?',
        options: [
          { id: 'a', label: 'A', text: 'They are functionally identical, structured output is just a marketing term' },
          { id: 'b', label: 'B', text: 'Structured output constrains the model\'s token generation itself to match the schema, a stronger guarantee than an instruction the model could still deviate from' },
          { id: 'c', label: 'C', text: 'Structured output only works for numeric fields' },
          { id: 'd', label: 'D', text: 'Prompt-only JSON requests are always more reliable' }
        ],
        correctOptionId: 'b',
        explanation:
          'Prompt-level formatting instructions are still just instructions the model can drift from. Schema-constrained decoding restricts what tokens can even be generated at each step, providing a materially stronger structural guarantee.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-04-mcq-02',
        question:
          'For which situation is a computer-use / GUI agent tool most specifically justified over building an API integration?',
        options: [
          { id: 'a', label: 'A', text: 'The target system has a well-documented, stable REST API' },
          { id: 'b', label: 'B', text: 'The target system is a legacy internal tool or third-party vendor portal with no API to integrate against' },
          { id: 'c', label: 'C', text: 'The task only requires reading structured data from a database' },
          { id: 'd', label: 'D', text: 'The task requires the lowest possible latency' }
        ],
        correctOptionId: 'b',
        explanation:
          'Computer-use tooling is valuable precisely when there\'s no API to integrate against and building one isn\'t an option — operating existing software the way a human would. When a real API exists, a direct integration is more reliable and lower-latency.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-04-mcq-03',
        question:
          'Why did the scenario\'s FDE build a custom retrieval tool for the internal market-research documents instead of using the vendor\'s hosted equivalent?',
        options: [
          { id: 'a', label: 'A', text: 'The vendor\'s hosted tool doesn\'t technically support document retrieval' },
          { id: 'b', label: 'B', text: 'The documents are covered by NDA data-residency clauses, and a custom tool run inside the customer\'s own infrastructure keeps proprietary content from leaving their boundary, unlike a vendor-hosted tool' },
          { id: 'c', label: 'C', text: 'Custom tools are always faster than hosted equivalents' },
          { id: 'd', label: 'D', text: 'Custom tools are cheaper to build than to operate a hosted tool' }
        ],
        correctOptionId: 'b',
        explanation:
          'Data control and compliance was the deciding factor here, not speed or cost — a hosted tool sends data to the vendor\'s infrastructure, which conflicts directly with a data-residency requirement, so the custom-tool cost was justified specifically by that constraint.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-04-mcq-04',
        question:
          'Why is a code-execution sandbox tool useful for a task like "calculate the average of these 40 numbers," even though the model could attempt the arithmetic directly in text?',
        options: [
          { id: 'a', label: 'A', text: 'Code execution is always faster than text generation' },
          { id: 'b', label: 'B', text: 'Models are unreliable at multi-step arithmetic performed purely through token generation; delegating the calculation to actually-executed code produces a correct, verifiable result' },
          { id: 'c', label: 'C', text: 'Models cannot generate numeric tokens at all' },
          { id: 'd', label: 'D', text: 'This is not a valid use case for code execution tools' }
        ],
        correctOptionId: 'b',
        explanation:
          '"Reasoning" arithmetic in text is prone to error at scale, since the model is predicting plausible-looking tokens, not running deterministic computation. A code-execution tool actually runs real code, giving a verifiably correct result instead of a plausible-sounding one.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-04-mcq-05',
        question:
          'What is the specific fidelity limitation of a vendor\'s built-in web-search tool compared to a custom retrieval tool the FDE builds themselves?',
        options: [
          { id: 'a', label: 'A', text: 'Built-in web-search tools cannot return any results at all for niche queries' },
          { id: 'b', label: 'B', text: 'The FDE has no control over the vendor\'s source prioritization or citation format when using a built-in web-search tool, whereas a custom retrieval tool gives full control over what\'s indexed and how results are ranked' },
          { id: 'c', label: 'C', text: 'Built-in web-search tools are always slower than custom retrieval' },
          { id: 'd', label: 'D', text: 'There is no fidelity difference between the two' }
        ],
        correctOptionId: 'b',
        explanation:
          'Speed to ship favors the built-in tool, but you inherit whatever the vendor\'s search index and ranking decide, with no control over source prioritization — that control is exactly what a custom retrieval/RAG tool buys you, at the cost of building and maintaining it.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-04-mcq-06',
        question:
          'What does the lesson\'s framework suggest is typical of a mature FDE engagement\'s tool selection?',
        options: [
          { id: 'a', label: 'A', text: 'Always choosing built-in tools exclusively for consistency' },
          { id: 'b', label: 'B', text: 'Always building every tool from scratch to maximize control' },
          { id: 'c', label: 'C', text: 'Mixing both — built-in tools where speed and low compliance risk make sense (e.g. public web search), custom tools where proprietary data or full control is required (e.g. internal document retrieval)' },
          { id: 'd', label: 'D', text: 'Avoiding tool use entirely in favor of longer prompts' }
        ],
        correctOptionId: 'c',
        explanation:
          'None of the three factors (speed, data control, fidelity/cost) dominates categorically — the right choice is scenario-specific, and real engagements typically mix built-in and custom tools based on which factor matters most for each individual piece of the system.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/05-rag-retrieval-augmented-generation': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-05-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — DIAGNOSING RAG FAILURE MODES',
        question:
          'A RAG system gives a wrong answer. Inspection shows the correct chunk was retrieved and included in the prompt, but placed 7th out of 10 chunks with no reordering by relevance. What kind of failure is this?',
        options: [
          { id: 'a', label: 'A', text: 'A retrieval miss — the correct chunk was never found' },
          { id: 'b', label: 'B', text: 'A lost-in-the-middle generation failure — the chunk was retrieved correctly, but its position deep in a long, unordered context made the model less likely to use it' },
          { id: 'c', label: 'C', text: 'An embedding model failure requiring retraining' },
          { id: 'd', label: 'D', text: 'A chunking failure requiring smaller chunks' }
        ],
        correctOptionId: 'b',
        explanation:
          'Since the correct chunk was retrieved (context recall was fine), the fault lies in generation, not retrieval — models are measurably less likely to use information buried mid-context, which is exactly why reordering retrieved chunks by relevance before assembly matters.',
        incorrectExplanation:
          'Check if the retrieval stage succeeded in finding the chunk, and where the degradation occurred during generation.',
        hint: 'When the correct document chunk is retrieved but placed deep in a long context window, generation quality degrades due to the lost-in-the-middle effect.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-05-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — CONTEXT PRECISION VS RECALL',
        question:
          'A RAG system retrieves 10 chunks for a query; 2 of them are actually relevant, and those 2 represent all of the relevant material that existed in the index. What does this tell you about context precision and context recall?',
        options: [
          { id: 'a', label: 'A', text: 'Both context precision and context recall are high' },
          { id: 'b', label: 'B', text: 'Context recall is high (all relevant material available was found), but context precision is low (only 2 of 10 retrieved chunks were actually relevant)' },
          { id: 'c', label: 'C', text: 'Both context precision and context recall are low' },
          { id: 'd', label: 'D', text: 'Context precision is high, context recall is low' }
        ],
        correctOptionId: 'b',
        explanation:
          'Context recall asks "of the relevant material that exists, how much did we find" — here, all of it (2 of 2). Context precision asks "of what we retrieved, how much was relevant" — here, only 2 of 10, so precision is poor even though recall is perfect.',
        incorrectExplanation:
          'Recall measures the proportion of available relevant chunks retrieved; precision measures the proportion of retrieved chunks that are actually relevant.',
        hint: 'Recall is high when all available relevant chunks are found; precision is low when irrelevant chunks dilute the retrieved set.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-05-mcq-01',
        question:
          'Which three stages make up a standard RAG pipeline, in order?',
        options: [
          { id: 'a', label: 'A', text: 'Ingestion (chunk and embed source documents), retrieval (find relevant chunks for a query), generation (produce an answer grounded in retrieved context)' },
          { id: 'b', label: 'B', text: 'Training, fine-tuning, deployment' },
          { id: 'c', label: 'C', text: 'Tokenization, embedding, classification' },
          { id: 'd', label: 'D', text: 'Prompting, sampling, evaluation' }
        ],
        correctOptionId: 'a',
        explanation:
          'RAG\'s three stages are ingestion (prepare and index source content), retrieval (find the relevant pieces for a given query), and generation (produce a grounded answer using what was retrieved). A weak link in any one degrades the whole system.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-05-mcq-02',
        question:
          'Why does a chunk covering five unrelated topics tend to retrieve poorly for queries about any one of those topics?',
        options: [
          { id: 'a', label: 'A', text: 'Large chunks are always rejected by vector databases' },
          { id: 'b', label: 'B', text: 'The chunk\'s embedding becomes a blurry average across all five topics, making it a worse match for any single specific query than a focused chunk would be' },
          { id: 'c', label: 'C', text: 'Large chunks cannot be embedded at all' },
          { id: 'd', label: 'D', text: 'This only happens with keyword search, not vector search' }
        ],
        correctOptionId: 'b',
        explanation:
          'An embedding is a single vector summarizing the chunk\'s content; mixing unrelated topics dilutes that vector\'s specificity, so it matches a targeted query less precisely than a smaller, focused chunk would.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-05-mcq-03',
        question:
          'A fixed-size chunker splits documents every 500 characters regardless of sentence boundaries. What is the most likely quality problem this introduces?',
        options: [
          { id: 'a', label: 'A', text: 'Fixed-size chunking always produces faster retrieval' },
          { id: 'b', label: 'B', text: 'A chunk can be cut off mid-sentence, destroying its meaning as a coherent, independently retrievable unit' },
          { id: 'c', label: 'C', text: 'Fixed-size chunking prevents any embedding from being generated' },
          { id: 'd', label: 'D', text: 'This has no meaningful effect on retrieval quality' }
        ],
        correctOptionId: 'b',
        explanation:
          'A chunk that\'s cut mid-sentence no longer represents a complete, coherent idea, which damages both its embedding quality and its usefulness once retrieved — this is why recursive/semantic chunking that respects natural boundaries is the practical default.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-05-mcq-04',
        question:
          'A query looking for an exact product SKU or error code often retrieves poorly with dense vector search alone. Why does hybrid search address this?',
        options: [
          { id: 'a', label: 'A', text: 'Hybrid search removes the need for an embedding model entirely' },
          { id: 'b', label: 'B', text: 'It combines dense vector similarity with sparse keyword/BM25 matching, and exact-match needs like SKUs or error codes are handled well by keyword matching even when semantic similarity alone misses them' },
          { id: 'c', label: 'C', text: 'Hybrid search only works for very short documents' },
          { id: 'd', label: 'D', text: 'Dense vector search always outperforms keyword search on exact terms' }
        ],
        correctOptionId: 'b',
        explanation:
          'Dense embeddings capture semantic similarity, not exact string matching, so specific identifiers can be under-weighted. Sparse keyword search is precisely strong where dense search is weak, which is why combining both consistently outperforms either alone on real-world query mixes.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-05-mcq-05',
        question:
          'What does the RAGAS "faithfulness" metric specifically measure?',
        options: [
          { id: 'a', label: 'A', text: 'Whether the retrieved chunks are relevant to the query' },
          { id: 'b', label: 'B', text: 'Whether the generated answer\'s claims actually follow from the retrieved context, or whether the model added unsupported claims' },
          { id: 'c', label: 'C', text: 'How many chunks were retrieved in total' },
          { id: 'd', label: 'D', text: 'How fast the answer was generated' }
        ],
        correctOptionId: 'b',
        explanation:
          'Faithfulness evaluates the generation stage specifically — whether the model\'s output stays grounded in what was actually retrieved, rather than introducing claims not supported by the context. Relevancy of retrieved chunks is a separate metric (context precision).'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-05-mcq-06',
        question:
          'Why does the lesson recommend scoring RAGAS\'s four metrics separately rather than just judging whether the final answer was right or wrong?',
        options: [
          { id: 'a', label: 'A', text: 'RAGAS metrics are only meaningful in aggregate, never individually' },
          { id: 'b', label: 'B', text: 'A wrong final answer alone doesn\'t reveal whether the problem is in retrieval (precision/recall) or generation (faithfulness/relevancy), and fixing the wrong stage wastes effort — separate scoring points directly at what to fix' },
          { id: 'c', label: 'C', text: 'The final answer is never a reliable signal of anything' },
          { id: 'd', label: 'D', text: 'Separate scoring is only useful for very large document sets' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is exactly the diagnostic value demonstrated in the practical scenario: separating retrieval-stage metrics (precision, recall) from generation-stage metrics (faithfulness, relevancy) let the FDE conclude the fault was lost-in-the-middle generation, not a retrieval problem, and fix the right thing.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-05-mcq-07',
        question:
          'What does a reranking step (cross-encoder model) add to a RAG pipeline that initial embedding-similarity retrieval alone doesn\'t provide?',
        options: [
          { id: 'a', label: 'A', text: 'It replaces the need for chunking entirely' },
          { id: 'b', label: 'B', text: 'It re-scores the top candidates from initial retrieval against the actual query more expensively but more accurately than embedding similarity, typically applied once basic retrieval and hybrid search stop being the main bottleneck' },
          { id: 'c', label: 'C', text: 'It eliminates the need for an evaluation framework like RAGAS' },
          { id: 'd', label: 'D', text: 'It reduces the total number of documents that can be indexed' }
        ],
        correctOptionId: 'b',
        explanation:
          'Reranking is a more expensive, more accurate second pass over a smaller candidate set already narrowed by initial retrieval — it\'s the next lever reached for once chunking and hybrid search improvements stop moving the needle.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/06-n8n-automation-workflow': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-06-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — N8N ITEMS-ARRAY EXECUTION MODEL',
        question:
          'A node in an n8n workflow receives 5 records from a previous step. By default, how many times does the next node in the chain execute?',
        options: [
          { id: 'a', label: 'A', text: 'Exactly once, receiving all 5 records as a single combined input' },
          { id: 'b', label: 'B', text: 'Once per item — the node runs independently for each of the 5 records unless they\'re explicitly aggregated first' },
          { id: 'c', label: 'C', text: 'Zero times, since n8n requires manual iteration to be configured' },
          { id: 'd', label: 'D', text: 'A random number of times depending on server load' }
        ],
        correctOptionId: 'b',
        explanation:
          'n8n\'s item-array data model means most nodes operate on every item independently by default — this is the detail that trips up newcomers most, since it\'s easy to assume a node runs once total rather than once per item.',
        incorrectExplanation:
          'Remember that in n8n data flows as an array of items and nodes iterate over items individually unless explicit aggregation is used.',
        hint: 'n8n nodes process each incoming item in the array independently by default, executing once per item.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-06-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — HUMAN-IN-THE-LOOP BRANCH SELECTION',
        question:
          'Of the lead-triage workflow\'s three branches (sales-qualified, needs-more-info, spam), which most benefits from a human-in-the-loop approval gate before any automated reply is sent, and why?',
        options: [
          { id: 'a', label: 'A', text: 'Spam — because spam messages are the most numerous' },
          { id: 'b', label: 'B', text: 'Needs-more-info — it\'s the branch where an automated reply requires judgment about what specific follow-up question to ask, making an incorrect auto-response more likely and more costly to the lead relationship than a straightforward CRM write or a discarded spam message' },
          { id: 'c', label: 'C', text: 'Sales-qualified — because it\'s the highest-value branch' },
          { id: 'd', label: 'D', text: 'None of the branches benefit from a human-in-the-loop gate' }
        ],
        correctOptionId: 'b',
        explanation:
          'Sales-qualified just writes to CRM and notifies a human sales rep (who reviews before acting further), and spam is simply logged — neither sends an automated customer-facing reply. Needs-more-info is the branch most likely to involve an automated response requiring judgment, making it the one where a wrong auto-reply is most costly, which is exactly why it\'s the best candidate for a human gate per the human-in-the-loop principle from the safety lesson.',
        incorrectExplanation:
          'Consider which branch involves sending an outward-facing automated reply that requires contextual judgment and carries relationship risk.',
        hint: 'Human-in-the-loop gates are most vital where automated customer-facing responses require nuanced judgment and carry relationship risk.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-06-mcq-01',
        question:
          'What makes n8n more than "a rigid if-this-then-that tool," according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'It has more triggers than competing tools' },
          { id: 'b', label: 'B', text: 'It lets you write actual JavaScript or Python in a Code node when a visual node can\'t express a needed transformation, mixing no-code speed with full-code flexibility in the same workflow' },
          { id: 'c', label: 'C', text: 'It only supports webhook triggers, which simplifies its model' },
          { id: 'd', label: 'D', text: 'It requires all logic to be written in code, with no visual nodes at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'The Code node is the escape hatch that keeps n8n from being limited to whatever its built-in visual nodes can express, letting you drop into real code for a specific transformation without abandoning the rest of the visual workflow.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-06-mcq-02',
        question:
          'How does n8n\'s AI Agent node relate to the function/tool-calling pattern covered in an earlier lesson?',
        options: [
          { id: 'a', label: 'A', text: 'It is unrelated; the AI Agent node cannot call any external tools' },
          { id: 'b', label: 'B', text: 'It\'s the same pattern expressed visually — you attach other nodes as callable tools the model can invoke mid-execution, instead of describing functions in application code' },
          { id: 'c', label: 'C', text: 'It replaces the need for function calling entirely with a different mechanism' },
          { id: 'd', label: 'D', text: 'It only works with models that don\'t support function calling' }
        ],
        correctOptionId: 'b',
        explanation:
          'The AI Agent node wraps an LLM call with tool-calling support and lets you attach other nodes as tools — conceptually identical to the function-calling mechanism from lesson 4, just expressed as a visual graph instead of code.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-06-mcq-03',
        question:
          'What does n8n\'s native MCP client and server support specifically enable?',
        options: [
          { id: 'a', label: 'A', text: 'n8n workflows can only ever consume external tools, never be exposed as one' },
          { id: 'b', label: 'B', text: 'An AI Agent node can call external MCP-compliant tool servers (client mode), and any n8n workflow can itself be exposed as a callable tool for an external agent (server mode) — letting a workflow built once be reused across different agentic systems' },
          { id: 'c', label: 'C', text: 'MCP support removes the need for webhook triggers' },
          { id: 'd', label: 'D', text: 'MCP is unrelated to n8n\'s tool-calling capabilities' }
        ],
        correctOptionId: 'b',
        explanation:
          'Bidirectional MCP support means n8n workflows aren\'t locked into being either only a tool-consumer or only a tool-provider — a workflow can be reused as a tool by a separate agentic system without rebuilding the integration from scratch.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-06-mcq-04',
        question:
          'Why did the lead-triage scenario favor building the automation in n8n over a hand-written Python service, at least initially?',
        options: [
          { id: 'a', label: 'A', text: 'n8n workflows always run faster than hand-written services' },
          { id: 'b', label: 'B', text: 'It shipped faster in week one of the engagement, and a non-engineer on the customer\'s team could see and understand the workflow graph, which matters early when requirements are still shifting' },
          { id: 'c', label: 'C', text: 'Python cannot make HTTP requests to a CRM API' },
          { id: 'd', label: 'D', text: 'n8n is required by law for lead-triage automations' }
        ],
        correctOptionId: 'b',
        explanation:
          'The trade-off in the scenario was speed-to-ship and customer visibility/modifiability early in an engagement, not raw technical capability — both n8n and a hand-written service could implement the same logic, but n8n won on those specific factors for this stage of the engagement.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-06-mcq-05',
        question:
          'According to the lesson, what should trigger porting a workflow from n8n into a hand-written service?',
        options: [
          { id: 'a', label: 'A', text: 'As soon as the workflow uses an AI Agent node' },
          { id: 'b', label: 'B', text: 'Once the logic needs version-controlled testing, complex branching that\'s genuinely clearer as code, or a scale/latency profile n8n\'s execution model isn\'t built for' },
          { id: 'c', label: 'C', text: 'n8n workflows should never be ported to a hand-written service under any circumstances' },
          { id: 'd', label: 'D', text: 'As soon as more than one external API is involved' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson frames n8n as often a fast prototyping and glue-integration layer, not necessarily the final production home for every workflow — the port-out signal is specific (testing rigor, branching complexity, or scale/latency needs), not a fixed rule like "as soon as an LLM is involved."'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-06-mcq-06',
        question:
          'In the lead-triage scenario\'s node graph, what determines which of the three downstream paths (CRM write, log-only, or otherwise) a given lead follows?',
        options: [
          { id: 'a', label: 'A', text: 'The order in which leads arrive' },
          { id: 'b', label: 'B', text: 'The classification output from the AI Agent node, evaluated by a conditional (IF/Switch) node downstream of it' },
          { id: 'c', label: 'C', text: 'A fixed round-robin assignment' },
          { id: 'd', label: 'D', text: 'The Slack node decides the routing before classification happens' }
        ],
        correctOptionId: 'b',
        explanation:
          'The AI Agent node classifies the lead first; a downstream IF/Switch node then branches execution based on that classification result — sales-qualified leads go to CRM write and Slack notification, everything else is logged.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/07-what-is-an-ai-agent': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-07-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — WORKFLOW VS AGENT DECISION BOUNDARY',
        question:
          'What is the single question that best distinguishes a fixed workflow from a true agent?',
        options: [
          { id: 'a', label: 'A', text: 'Which programming language was used to build it' },
          { id: 'b', label: 'B', text: 'Who decides the next step and when — a human/builder at design time (workflow) or the model itself at runtime (agent)' },
          { id: 'c', label: 'C', text: 'Whether it uses an LLM at all' },
          { id: 'd', label: 'D', text: 'How many total steps it has' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both a fixed workflow and an agent can use LLMs and have multiple steps. The defining difference is whether the sequence and branching are fixed by the builder in advance, or decided dynamically by the model as it runs.',
        incorrectExplanation:
          'Consider who decides the sequence of actions and whether that decision happens at build time or during execution.',
        hint: 'Distinguish whether the execution path is decided by a builder at design time or by the LLM itself at runtime.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-07-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — DISCOVERY-DRIVEN EXECUTION',
        question:
          'Why does the provisioning-assistant scenario specifically favor an agent loop over a fixed workflow, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Provisioning tasks always require more tools than triage tasks' },
          { id: 'b', label: 'B', text: 'The number and order of needed steps genuinely depends on what earlier tool calls discover (e.g. whether a device record already exists), which a fixed workflow would need a combinatorially growing number of explicit branches to express' },
          { id: 'c', label: 'C', text: 'Agents are required whenever more than two tools are involved' },
          { id: 'd', label: 'D', text: 'Fixed workflows cannot call more than one tool' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the exact discovery-dependent shape that justifies an agent: what needs to happen next depends on what an earlier step revealed, which a workflow can only handle by enumerating every combination in advance — a genuinely different problem from lead triage\'s fixed shape.',
        incorrectExplanation:
          'Think about how variable prerequisite discovery and unexpected edge cases affect workflow branching.',
        hint: 'Dynamic discovery of prerequisites at runtime makes fixed branching combinatorially unmanageable.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-07-mcq-01',
        question:
          'What is the correct order of steps in one iteration of the ReAct agent loop?',
        options: [
          { id: 'a', label: 'A', text: 'Action, then Thought, then Observation' },
          { id: 'b', label: 'B', text: 'Thought, then Action, then Observation' },
          { id: 'c', label: 'C', text: 'Observation, then Thought, then Action' },
          { id: 'd', label: 'D', text: 'There is no fixed order; steps happen simultaneously' }
        ],
        correctOptionId: 'b',
        explanation:
          'ReAct produces a Thought (reasoning about what to do), then an Action (a tool call), then receives an Observation (the tool\'s result), which feeds the next Thought — this cycle repeats until the model produces a Final Answer.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-07-mcq-02',
        question:
          'Why does a five-iteration agent loop cost significantly more than a single LLM call?',
        options: [
          { id: 'a', label: 'A', text: 'Agent loops always use a larger, more expensive model than single calls' },
          { id: 'b', label: 'B', text: 'Each iteration of the loop is a full separate LLM call, so a five-iteration loop is at minimum five LLM calls, not one' },
          { id: 'c', label: 'C', text: 'Tool calls are billed at a higher rate than LLM calls' },
          { id: 'd', label: 'D', text: 'There is no meaningful cost difference' }
        ],
        correctOptionId: 'b',
        explanation:
          'Each Thought/Action/Observation iteration requires the model to be called again with the updated transcript. The cost scales directly with iteration count, which is exactly why an unnecessary agent loop is wasteful compared to a workflow that needs only one or two calls.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-07-mcq-03',
        question:
          'Why should an agent loop have a hard iteration cap in addition to relying on the model to emit an explicit "finish" action?',
        options: [
          { id: 'a', label: 'A', text: 'Iteration caps make the agent run faster' },
          { id: 'b', label: 'B', text: 'The model has no innate sense of "done" any more than it has an innate sense of "I don\'t know" — relying solely on it to self-terminate risks a runaway loop if it never emits finish' },
          { id: 'c', label: 'C', text: 'The "finish" action is deprecated and no longer supported' },
          { id: 'd', label: 'D', text: 'A hard cap is only needed for agents with more than one tool' }
        ],
        correctOptionId: 'b',
        explanation:
          'Just as a model doesn\'t reliably know when it doesn\'t know something, it doesn\'t reliably know when it\'s genuinely finished. A deterministic hard cap, independent of the model\'s own judgment, is a necessary safety net against an unbounded loop.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-07-mcq-04',
        question:
          'The previous lesson\'s lead-triage automation (classify, then branch to CRM/Slack or log) was correctly built as a fixed n8n workflow rather than an agent. Why?',
        options: [
          { id: 'a', label: 'A', text: 'n8n does not support building agents at all' },
          { id: 'b', label: 'B', text: 'The number and order of steps was fully knowable in advance — classify, then branch — with no discovery-dependent variation in how many steps were needed' },
          { id: 'c', label: 'C', text: 'Fixed workflows are always cheaper than agents regardless of task shape' },
          { id: 'd', label: 'D', text: 'Lead triage cannot use an LLM under any circumstances' }
        ],
        correctOptionId: 'b',
        explanation:
          'The deciding factor is whether step count/order is knowable ahead of time. Lead triage always follows the same shape (one classification, one branch), so a fixed workflow is more predictable and cheaper with no capability loss.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-07-mcq-05',
        question:
          'What role does the running Thought/Action/Observation transcript play in an agent loop?',
        options: [
          { id: 'a', label: 'A', text: 'It is purely a logging artifact with no effect on the model\'s next decision' },
          { id: 'b', label: 'B', text: 'It functions as the loop\'s short-term memory, letting the model see what it already tried and learned so it doesn\'t repeat itself or ignore earlier findings' },
          { id: 'c', label: 'C', text: 'It replaces the need for a system prompt' },
          { id: 'd', label: 'D', text: 'It is only used after the loop finishes, for auditing' }
        ],
        correctOptionId: 'b',
        explanation:
          'The transcript is fed back into context on each subsequent call, which is precisely what lets the model "remember" its own prior steps within the loop — without it, each iteration would have no awareness of what already happened.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-07-mcq-06',
        question:
          'What does the lesson identify as the most common over-engineering mistake when choosing between a fixed workflow and an agent?',
        options: [
          { id: 'a', label: 'A', text: 'Using a fixed workflow for a task that genuinely needs discovery-dependent steps' },
          { id: 'b', label: 'B', text: 'Reaching for an agent by default for tasks that are actually fixed-shape, adding cost, unpredictability, and testing difficulty for no corresponding benefit' },
          { id: 'c', label: 'C', text: 'Using too few tools in an agent\'s tool set' },
          { id: 'd', label: 'D', text: 'Setting an iteration cap that is too low' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson explicitly frames "agent by default" as the common mistake — not because agents are bad, but because applying the more flexible, more expensive, less predictable tool to a task that doesn\'t need that flexibility is pure waste.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/08-building-agents-with-n8n': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-08-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — LLM WORKFLOW NODE VS AI AGENT NODE',
        question:
          'The lead-triage workflow from the earlier lesson uses an LLM classification step, yet the lesson still calls it a "fixed workflow," not an agent. Why?',
        options: [
          { id: 'a', label: 'A', text: 'n8n does not allow LLM nodes inside fixed workflows' },
          { id: 'b', label: 'B', text: 'The branching after classification was decided by the builder at design time (an IF/Switch node), not discovered dynamically by the model deciding its own next step' },
          { id: 'c', label: 'C', text: 'The workflow doesn\'t use any tools at all' },
          { id: 'd', label: 'D', text: 'It processes fewer than 5 items per execution' }
        ],
        correctOptionId: 'b',
        explanation:
          'Containing an LLM call doesn\'t make something an agent — what matters is whether the *branching/next-step decision* is made by the model at runtime or fixed by the builder in advance. The lead-triage workflow\'s branching is fixed, so it remains a workflow despite using an LLM.',
        incorrectExplanation:
          'Distinguish between a single static prompt transformation and a node that can autonomously call tools in a loop.',
        hint: 'A basic chain executes a single prompt in a fixed sequence; an AI Agent node runs an autonomous tool-calling loop.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-08-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — ENCAPSULATED TOOL ABSTRACTIONS',
        question:
          'What is the main benefit of building `check_ticket_status` as its own small sub-workflow and attaching it as a tool, rather than embedding that logic directly inside the AI Agent node\'s configuration?',
        options: [
          { id: 'a', label: 'A', text: 'Sub-workflows execute faster than inline logic' },
          { id: 'b', label: 'B', text: 'The sub-workflow can be independently tested and reused as a tool by a completely different agent later, without rebuilding the lookup logic' },
          { id: 'c', label: 'C', text: 'AI Agent nodes cannot call any tools unless they are sub-workflows' },
          { id: 'd', label: 'D', text: 'This has no practical benefit over inline configuration' }
        ],
        correctOptionId: 'b',
        explanation:
          'The sub-workflow-as-tool pattern is a composability win — build a capability once, test it in isolation, and reuse it as a tool across multiple different agents, exactly as the scenario\'s lookup workflows are meant to be reused by a future "manager dashboard" agent.',
        incorrectExplanation:
          'Consider the complexity and reliability of exposing raw multi-step API mechanics directly to model prompt context.',
        hint: 'Sub-workflows encapsulate multi-step validation and error handling behind a single clean tool interface.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-08-mcq-01',
        question:
          'What does n8n\'s AI Agent node do internally that a plain LLM-call node does not?',
        options: [
          { id: 'a', label: 'A', text: 'It automatically writes the rest of the workflow\'s nodes' },
          { id: 'b', label: 'B', text: 'It runs a self-contained ReAct-style loop, deciding which of its attached tools to call and when to stop, without the builder wiring that loop by hand' },
          { id: 'c', label: 'C', text: 'It replaces the need for a system prompt entirely' },
          { id: 'd', label: 'D', text: 'It only differs in having a larger context window' }
        ],
        correctOptionId: 'b',
        explanation:
          'The AI Agent node implements the Thought/Action/Observation loop from the previous lesson as a self-contained sub-graph, deciding tool use and termination internally — a plain LLM node just produces one response with no loop.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-08-mcq-02',
        question:
          'A customer expects their helpdesk bot to remember a detail a user mentioned in a conversation yesterday. Which memory configuration does this require?',
        options: [
          { id: 'a', label: 'A', text: 'Window buffer memory, since it\'s the default option' },
          { id: 'b', label: 'B', text: 'Persistent memory backed by a database, since window buffer memory is forgotten once a single execution ends and cannot survive across separate executions' },
          { id: 'c', label: 'C', text: 'Neither — n8n cannot support any form of memory' },
          { id: 'd', label: 'D', text: 'This requires switching to a fixed workflow instead of an agent' }
        ],
        correctOptionId: 'b',
        explanation:
          'Window buffer memory only persists for the duration of one execution. Remembering something across separate conversations (yesterday vs. today) requires persistent memory that survives between executions.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-08-mcq-03',
        question:
          'What is the downside of configuring persistent memory for an agent that only ever handles one-shot, unrelated requests with no ongoing conversation?',
        options: [
          { id: 'a', label: 'A', text: 'Persistent memory makes the agent\'s tool calls fail' },
          { id: 'b', label: 'B', text: 'It adds unnecessary infrastructure and latency for a continuity guarantee the use case never actually needs' },
          { id: 'c', label: 'C', text: 'Persistent memory is strictly cheaper than window buffer memory, so there is no downside' },
          { id: 'd', label: 'D', text: 'Persistent memory prevents the agent from using tools' }
        ],
        correctOptionId: 'a',
        explanation:
          'The trade-off runs both directions — persistent memory costs infrastructure and latency, so provisioning it for a use case that\'s genuinely one-shot is waste, the mirror image of the earlier example where window buffer memory was insufficient.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-08-mcq-04',
        question:
          'What specifically distinguishes the helpdesk scenario from the lead-triage workflow in a way that justifies an AI Agent node over a fixed IF/Switch branch?',
        options: [
          { id: 'a', label: 'A', text: 'The helpdesk bot uses more Slack integrations' },
          { id: 'b', label: 'B', text: 'Some helpdesk requests require chaining an unpredictable number of tool calls together (discovering mid-conversation that a second lookup is needed), whereas lead triage only ever needed one classification call' },
          { id: 'c', label: 'C', text: 'The helpdesk bot processes a higher volume of requests' },
          { id: 'd', label: 'D', text: 'Fixed workflows cannot call more than one external system' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the same discovery-dependent-steps justification from the previous lesson, applied concretely: the helpdesk bot sometimes needs to chain tool calls based on what it learns mid-conversation, which a fixed branch can\'t express, while lead triage\'s shape never varies.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-08-mcq-05',
        question:
          'How does the sub-workflow-as-tool pattern relate to n8n\'s MCP client/server support covered in an earlier lesson?',
        options: [
          { id: 'a', label: 'A', text: 'They are mutually exclusive features; a workflow can use one or the other but never both' },
          { id: 'b', label: 'B', text: 'They can combine — a sub-workflow tool built once inside n8n can also be exposed over MCP, making it callable by agents running entirely outside n8n, not just by other n8n AI Agent nodes' },
          { id: 'c', label: 'C', text: 'MCP support replaces the need for sub-workflows entirely' },
          { id: 'd', label: 'D', text: 'Sub-workflows can only be called by MCP clients, never by n8n\'s own AI Agent node' }
        ],
        correctOptionId: 'b',
        explanation:
          'Sub-workflow-as-tool is n8n\'s internal composition mechanism; MCP server support extends that same reusable capability to external agentic systems outside n8n entirely — the two combine rather than compete.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-08-mcq-06',
        question:
          'Why does the `escalate_to_human` tool specifically warrant a human-in-the-loop confirmation step, rather than executing automatically like the lookup tools?',
        options: [
          { id: 'a', label: 'A', text: 'Lookup tools never have real-world consequences worth gating' },
          { id: 'b', label: 'B', text: 'Escalation has real consequences for response time and routing; a deliberate handoff step (e.g. Slack approval buttons) avoids the agent over- or under-escalating based on a misjudged situation, consistent with the human-in-the-loop principle for high-stakes actions' },
          { id: 'c', label: 'C', text: 'n8n technically cannot execute a tool without human approval' },
          { id: 'd', label: 'D', text: 'Escalation is the cheapest tool to call, so gating it saves the most cost' }
        ],
        correctOptionId: 'b',
        explanation:
          'Read-only lookups have low consequence if wrong; escalation changes what happens to a real support case and its response-time expectations, making it the highest-stakes action in this tool set and the one that most benefits from a deliberate human checkpoint.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/09-openclaw-personal-24-7-ai-agent': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-09-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — PROACTIVE VS REACTIVE EXECUTION',
        question:
          'What is the defining difference between a proactive agent and a reactive agent, as this lesson uses the terms?',
        options: [
          { id: 'a', label: 'A', text: 'Proactive agents use larger models than reactive agents' },
          { id: 'b', label: 'B', text: 'A proactive agent decides for itself that now is a moment to act, without a fresh external trigger initiating that specific decision; a reactive agent only acts because something triggered it' },
          { id: 'c', label: 'C', text: 'Reactive agents cannot use tools, while proactive agents can' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference; the terms are interchangeable' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the new axis this lesson introduces: every agent covered earlier (ReAct loop, n8n AI Agent node) is reactive — it runs because a webhook, message, or manual trigger started it. Proactive means the system itself judges when to act.',
        incorrectExplanation:
          'Consider how the execution is initiated: waiting passively for a user turn versus waking up autonomously on a heartbeat.',
        hint: 'Reactive agents only run when a user messages them; proactive agents wake up on heartbeats or events to inspect state and act.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-09-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — STATEFUL PROACTIVE MEMORY',
        question:
          'Why does persistent, cross-session memory matter more for a proactive agent than it does for a purely reactive, one-shot request-response agent?',
        options: [
          { id: 'a', label: 'A', text: 'Persistent memory is required by n8n for any agent to function' },
          { id: 'b', label: 'B', text: 'A proactive agent needs to remember what it already checked or acted on across separate, self-initiated wake cycles (e.g. which tickets it already drafted for) to avoid repeating or missing actions, whereas a reactive agent\'s context is often fully contained within a single triggered exchange' },
          { id: 'c', label: 'C', text: 'Reactive agents never need any form of memory' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference in memory needs between the two' }
        ],
        correctOptionId: 'b',
        explanation:
          'Because a proactive agent\'s actions happen across many separate, self-initiated wake cycles rather than one bounded exchange, it needs durable memory of what it has already done to make sound decisions on the next cycle — this is architecture\'s default, not an optional add-on, for exactly this reason.',
        incorrectExplanation:
          'Think about what happens on subsequent heartbeats if the agent has no memory of what it observed and alerted on previously.',
        hint: 'Without persistent memory of past heartbeats, the agent cannot detect state transitions or prevent spamming duplicate alerts.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-09-mcq-01',
        question:
          'What mechanism does OpenClaw use to run continuously and decide on its own when to act, rather than waiting for an incoming request?',
        options: [
          { id: 'a', label: 'A', text: 'A heartbeat daemon that wakes on a recurring cycle and evaluates whether anything warrants action' },
          { id: 'b', label: 'B', text: 'A single webhook endpoint that must be called externally for anything to happen' },
          { id: 'c', label: 'C', text: 'A fixed daily cron job with no other trigger types' },
          { id: 'd', label: 'D', text: 'It only responds when a user opens a dedicated chat window' }
        ],
        correctOptionId: 'a',
        explanation:
          'The heartbeat daemon is what makes OpenClaw\'s architecture proactive rather than reactive — it wakes on its own recurring cycle and decides whether action is warranted, rather than only running because an external event triggered it.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-09-mcq-02',
        question:
          'How does a heartbeat trigger differ from both a webhook trigger and a scheduled/cron trigger?',
        options: [
          { id: 'a', label: 'A', text: 'A heartbeat is just a webhook with a different name' },
          { id: 'b', label: 'B', text: 'A webhook fires because something external happened, and a schedule fires because a fixed time arrived; a heartbeat wakes repeatedly and itself judges whether anything warrants action, rather than a fixed condition or fixed time determining the action' },
          { id: 'c', label: 'C', text: 'A heartbeat only fires once per day, identical to a daily cron job' },
          { id: 'd', label: 'D', text: 'There is no functional difference between the three trigger types' }
        ],
        correctOptionId: 'b',
        explanation:
          'Webhook and schedule triggers both fire based on an external, predetermined condition (an event or a fixed time). A heartbeat wakes on a cycle and then itself evaluates whether action is warranted — the judgment happens inside the heartbeat, not at the trigger level.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-09-mcq-03',
        question:
          'Why can no vendor-hosted SaaS agent platform offer the same data-ownership guarantee as a self-hosted architecture like OpenClaw\'s?',
        options: [
          { id: 'a', label: 'A', text: 'Vendor-hosted platforms are always less capable technically' },
          { id: 'b', label: 'B', text: 'By definition, a hosted platform\'s infrastructure belongs to the vendor, not the customer, so any data processed there is not entirely within the customer\'s own control — a self-hosted architecture keeps infrastructure, keys, and data on the customer\'s own systems' },
          { id: 'c', label: 'C', text: 'Vendor-hosted platforms cannot support messaging integrations' },
          { id: 'd', label: 'D', text: 'This is not actually true; hosted and self-hosted platforms offer identical data guarantees' }
        ],
        correctOptionId: 'b',
        explanation:
          'Self-hosting is the direct mechanism for satisfying a hard data-ownership requirement — running on the user\'s own hardware with their own keys means nothing has to leave infrastructure they control, a guarantee a hosted vendor platform structurally cannot make.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-09-mcq-04',
        question:
          'Why does the scenario conclude the overnight ticket-monitoring requirement leans toward a proactive/ambient architecture rather than a scheduled workflow?',
        options: [
          { id: 'a', label: 'A', text: 'Because it runs overnight, and scheduled workflows cannot run outside business hours' },
          { id: 'b', label: 'B', text: 'Because the requirement implies ongoing judgment about which tickets are worth drafting for and when a draft is ready, not a single fixed-time batch action — the "deciding for itself" quality that distinguishes proactive from scheduled behavior' },
          { id: 'c', label: 'C', text: 'Because scheduled workflows cannot call an LLM' },
          { id: 'd', label: 'D', text: 'Because it involves messaging platforms, which only proactive agents can use' }
        ],
        correctOptionId: 'b',
        explanation:
          'The distinguishing test from this lesson is whether the system needs to decide, on an ongoing basis, whether now is the moment to act. "Monitor and draft responses" implies exactly that kind of continuous judgment, unlike a single fixed-time summary job.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-09-mcq-05',
        question:
          'What is the trade-off in choosing how often a heartbeat cycle should wake?',
        options: [
          { id: 'a', label: 'A', text: 'Heartbeat frequency has no effect on cost or responsiveness' },
          { id: 'b', label: 'B', text: 'Too frequent wastes cost checking for changes that haven\'t happened yet; too infrequent risks missing timely action on something that needed a faster response' },
          { id: 'c', label: 'C', text: 'A more frequent heartbeat always produces better outcomes with no downside' },
          { id: 'd', label: 'D', text: 'Heartbeat frequency can only be set to once every 24 hours' }
        ],
        correctOptionId: 'b',
        explanation:
          'Each heartbeat wake is itself a cost (checking state, potentially calling an LLM to judge whether action is warranted), so the frequency has to be tuned against how time-sensitive the underlying task actually is — the same cost-versus-responsiveness trade-off that shows up throughout this module.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-09-mcq-06',
        question:
          'Why should the overnight-monitoring agent only draft responses and never send them without human review?',
        options: [
          { id: 'a', label: 'A', text: 'Drafting is technically impossible without a review step' },
          { id: 'b', label: 'B', text: 'A proactive agent acting on its own judgment, without a fresh external trigger confirming the action is correct, is exactly the kind of high-stakes, hard-to-reverse customer-facing action that warrants a human-in-the-loop gate before it takes effect' },
          { id: 'c', label: 'C', text: 'OpenClaw-style agents cannot send messages under any circumstances' },
          { id: 'd', label: 'D', text: 'Human review is only needed for scheduled workflows, not proactive agents' }
        ],
        correctOptionId: 'b',
        explanation:
          'Because the agent decided to act entirely on its own judgment (no human explicitly triggered this specific action), the case for a human checkpoint before anything customer-facing goes out is if anything stronger than for a reactive agent responding to a direct request.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/10-multi-agent-systems': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-10-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — MULTI-AGENT TOPOLOGY PITFALLS',
        question:
          'Which multi-agent pattern category has struggled most once systems move past the demo/pilot stage into production?',
        options: [
          { id: 'a', label: 'A', text: 'Sequential pipeline' },
          { id: 'b', label: 'B', text: 'Orchestrator-worker' },
          { id: 'c', label: 'C', text: 'Free-form swarm/mesh peer negotiation with no single accountable decision-maker' },
          { id: 'd', label: 'D', text: 'Hierarchical' }
        ],
        correctOptionId: 'c',
        explanation:
          'Production systems that survived past a pilot almost always had phase gates, shared artifacts, or a final supervisor — pure free-form peer negotiation has mostly stayed confined to narrow, heavily instrumented niches rather than becoming a reliable general-purpose default.',
        incorrectExplanation:
          'Look at the pattern where agents chat freely with each other without a centralized coordinator enforcing termination and schemas.',
        hint: 'Decentralized peer-to-peer agent meshes suffer from conversational loops, unbounded token spend, and lack of accountability.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-10-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — WORKER ISOLATION & ACCOUNTABILITY',
        question:
          'Why does the practice loop ask you to write a "done" definition for each worker\'s subtask in the redesigned system?',
        options: [
          { id: 'a', label: 'A', text: 'It is only useful for documentation purposes with no bearing on debugging' },
          { id: 'b', label: 'B', text: 'A clear "done" definition per worker is what creates the accountability boundary that lets a failure be traced to exactly one worker\'s output, rather than an ambiguous multi-way negotiation' },
          { id: 'c', label: 'C', text: 'Workers cannot execute at all without an explicit "done" definition' },
          { id: 'd', label: 'D', text: 'This step is unnecessary in an orchestrator-worker design' }
        ],
        correctOptionId: 'b',
        explanation:
          'The traceability benefit of orchestrator-worker over mesh specifically depends on each worker having a clearly scoped, checkable output — without that, you\'re back to an ambiguous system where a bad final result can\'t be attributed to any one stage.',
        incorrectExplanation:
          'Consider what prevents workers from colliding, duplicating work, or returning unverifiable open-ended results.',
        hint: 'Workers must have disjoint write scopes, clear acceptance criteria, and bounded input/output contracts.'
      }
    ],
    architecture: {
      id: 'lesson-fde-agentic-ai-core-10-orchestrator-worker',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — ORCHESTRATOR-WORKER REFACTOR',
      boundaryLabel: 'CENTRAL ORCHESTRATOR BOUNDARY',
      boundaryText:
        'The orchestrator delegates isolated tasks to specialized workers with strict schemas, preventing peer-to-peer negotiation loops.',
      nodes: [
        { id: 'request', label: 'User Request', kind: 'input' },
        { id: 'orchestrator', label: 'Lead Orchestrator', kind: 'service' },
        { id: 'boundary', label: 'Contract & Schema Gate', kind: 'boundary', highlighted: true },
        { id: 'retriever', label: 'Document Retriever Worker', kind: 'adapter' },
        { id: 'analyst', label: 'Financial Analyst Worker', kind: 'adapter' },
        { id: 'writer', label: 'Report Writer Worker', kind: 'adapter' },
        { id: 'output', label: 'Synthesized Report', kind: 'output' }
      ]
    },
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-10-mcq-01',
        question:
          'What defines the orchestrator-worker multi-agent pattern?',
        options: [
          { id: 'a', label: 'A', text: 'All agents negotiate as equal peers with no single decision-maker' },
          { id: 'b', label: 'B', text: 'A single orchestrator decomposes a task into known subtasks and dispatches each to a specialized worker, with one accountability point responsible for aggregating results' },
          { id: 'c', label: 'C', text: 'Every agent has access to every other agent\'s memory at all times' },
          { id: 'd', label: 'D', text: 'There is exactly one agent total, performing all subtasks sequentially' }
        ],
        correctOptionId: 'b',
        explanation:
          'Orchestrator-worker\'s defining trait is the single accountable decomposition/aggregation point — this is what makes it the most disciplined and production-proven pattern compared to free-form peer negotiation.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-10-mcq-02',
        question:
          'What did controlled research find when comparing a single agent to a multi-agent system given identical tools and context?',
        options: [
          { id: 'a', label: 'A', text: 'Multi-agent systems always significantly outperform a single agent' },
          { id: 'b', label: 'B', text: 'The single agent matched or outperformed the multi-agent system on the large majority of benchmarked tasks, with multi-agent\'s accuracy edge, where present, coming at roughly double the cost' },
          { id: 'c', label: 'C', text: 'Single agents cannot use tools, making the comparison invalid' },
          { id: 'd', label: 'D', text: 'There was no measurable difference in cost between the two approaches' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the core finding that should temper reflexive multi-agent adoption: a single well-tooled agent is frequently as good or better, and multi-agent\'s modest accuracy gains where they exist come at a real, roughly doubled cost.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-10-mcq-03',
        question:
          'Why does multi-agent orchestration tend to consume dramatically more tokens than a single chat-style interaction?',
        options: [
          { id: 'a', label: 'A', text: 'Multi-agent systems always use larger context windows by requirement' },
          { id: 'b', label: 'B', text: 'Every hand-off between agents typically re-summarizes or re-explains context, and each orchestrator decision is its own additional LLM call layered on top of the workers\' own calls' },
          { id: 'c', label: 'C', text: 'Token cost is identical between single-agent and multi-agent systems' },
          { id: 'd', label: 'D', text: 'Workers do not consume tokens, only the orchestrator does' }
        ],
        correctOptionId: 'b',
        explanation:
          'Each hand-off and each orchestrator decision is additional LLM-call overhead stacked on top of what the workers themselves need, which is why research-style multi-agent orchestration can burn an order of magnitude more tokens than a single interaction.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-10-mcq-04',
        question:
          'Why does the lesson describe the orchestrator as "both a bottleneck and a single point of failure"?',
        options: [
          { id: 'a', label: 'A', text: 'The orchestrator is the only component that costs money to run' },
          { id: 'b', label: 'B', text: 'Every worker\'s result routes back through the orchestrator, so it becomes a throughput bottleneck, and a worker\'s bad output propagates into whatever the orchestrator does next, compounding the failure' },
          { id: 'c', label: 'C', text: 'Orchestrators are always the slowest individual agent in the system' },
          { id: 'd', label: 'D', text: 'This description only applies to swarm and mesh patterns, not orchestrator-worker' }
        ],
        correctOptionId: 'b',
        explanation:
          'The orchestrator\'s centralizing role is both its strength (clear accountability) and its risk (a single choke point whose downstream decisions inherit any upstream worker\'s mistake) — this is an inherent property of the pattern, not a flaw unique to a bad implementation.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-10-mcq-05',
        question:
          'What specifically was wrong with the original five-agent mesh design for the research-and-report system, and how did the orchestrator-worker redesign fix it?',
        options: [
          { id: 'a', label: 'A', text: 'The mesh design had too few agents; the fix was adding more agents to improve coverage' },
          { id: 'b', label: 'B', text: 'Free-form negotiation with no single accountable agent produced inconsistent output run-to-run and high token cost; collapsing to one orchestrator dispatching three well-scoped, sequential worker subtasks with a final review gate made failures traceable to a specific worker and reduced hand-offs' },
          { id: 'c', label: 'C', text: 'The mesh design was fine; the redesign only changed which LLM model was used' },
          { id: 'd', label: 'D', text: 'The fix was removing all agents and using a single fixed workflow with no LLM calls' }
        ],
        correctOptionId: 'b',
        explanation:
          'The scenario\'s core lesson is that the failure mode (inconsistency, high cost, opaque negotiation) came directly from the lack of a single accountable decision-maker — orchestrator-worker\'s defined subtasks and accountability boundary is what fixed it, not adding more agents or removing agentic structure entirely.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-10-mcq-06',
        question:
          'According to the lesson\'s framework, what is the honest question an FDE should answer before recommending a multi-agent design over a single well-tooled agent?',
        options: [
          { id: 'a', label: 'A', text: 'Whether the customer specifically asked for the word "multi-agent"' },
          { id: 'b', label: 'B', text: 'Whether the task genuinely decomposes into independent, parallelizable, or specialist-distinct subproblems — not whether multi-agent sounds more sophisticated' },
          { id: 'c', label: 'C', text: 'Whether enough budget exists to run more LLM calls, regardless of task shape' },
          { id: 'd', label: 'D', text: 'Whether the team has more than one available engineer to build it' }
        ],
        correctOptionId: 'b',
        explanation:
          'Given the accuracy and cost data, the lesson is explicit that multi-agent should be chosen because a task genuinely has that decomposable shape, not by default or because it seems like the more advanced choice.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-10-mcq-07',
        question:
          'In the redesigned orchestrator-worker research system, where does the final review/supervisor gate belong, and why?',
        options: [
          { id: 'a', label: 'A', text: 'Before the orchestrator decomposes the task, since earlier is always better' },
          { id: 'b', label: 'B', text: 'After the writer worker produces the final report but before it\'s returned to the customer, since this is the last point where an inconsistency from any earlier worker would otherwise reach the customer undetected' },
          { id: 'c', label: 'C', text: 'A review gate is unnecessary once orchestrator-worker replaces mesh' },
          { id: 'd', label: 'D', text: 'The review gate should run after each individual worker\'s every intermediate token, not just at the end' }
        ],
        correctOptionId: 'b',
        explanation:
          'The gate\'s job is to catch anything that slipped through the pipeline before it reaches the customer — placing it at the very end, after the writer\'s output but before delivery, is the last checkpoint where that\'s still possible.'
      }
    ]
  },
  'fde-curriculum/agentic-ai-core/11-debugging-ai': {
    conceptChecks: [
      {
        id: 'lesson-fde-agentic-ai-core-11-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — STOCHASTIC EVALUATION VS RE-RUNS',
        question:
          'Why is "I ran the agent again with the same input and it worked correctly" not reliable evidence that a suspected bug is fixed?',
        options: [
          { id: 'a', label: 'A', text: 'Agents never produce the same output twice under any circumstances' },
          { id: 'b', label: 'B', text: 'Because the agent\'s execution path depends on sampling at every generation step, the same input can take a different route through the loop on different runs, so a successful re-run doesn\'t rule out the original faulty path recurring' },
          { id: 'c', label: 'C', text: 'Re-running an agent is always technically impossible' },
          { id: 'd', label: 'D', text: 'This reasoning is actually valid and sufficient to confirm a fix' }
        ],
        correctOptionId: 'b',
        explanation:
          'Unlike deterministic code, an agent\'s non-deterministic sampling means the same input doesn\'t guarantee the same path, so a clean re-run doesn\'t prove the earlier failing path is gone — this is exactly why trace-level inspection of the actual failing run matters more than reproduction attempts.',
        incorrectExplanation:
          'Consider the probabilistic nature of LLM generation and how single-run confirmation leads to phantom fixes.',
        hint: 'LLMs are non-deterministic; a single successful run can simply be statistical variance unless validated across a test suite.'
      },
      {
        id: 'lesson-fde-agentic-ai-core-11-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — BACKWARD TRACE DIAGNOSTICS',
        question:
          'When walking a failing trace backward from the final wrong output, what question do you ask at each step to decide whether to keep going further back?',
        options: [
          { id: 'a', label: 'A', text: 'Was this step\'s output the same as the final output?' },
          { id: 'b', label: 'B', text: 'Was this step\'s output correct given what it actually received as input? If yes, the fault is further upstream; if no, this step is a candidate for the actual fault' },
          { id: 'c', label: 'C', text: 'How long did this step take to execute?' },
          { id: 'd', label: 'D', text: 'Did this step use the largest available model?' }
        ],
        correctOptionId: 'b',
        explanation:
          'The technique isolates correctness relative to each step\'s own input, not relative to the final outcome — a step can be "correct" (reasonable given bad input) while still being downstream of the actual fault, which is exactly the helpdesk scenario\'s escalate decision.',
        incorrectExplanation:
          'Follow the causal chain in reverse: from the final flawed action back to the specific step that introduced invalid state.',
        hint: 'Inspect the final bad output, then step backward through preceding tool calls, prompt context, and retrieval data to find the earliest corrupted step.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-11-mcq-01',
        question:
          'Why does the lesson describe "the final answer was wrong" as a symptom rather than a diagnosis?',
        options: [
          { id: 'a', label: 'A', text: 'Final answers are never actually wrong in practice' },
          { id: 'b', label: 'B', text: 'The root cause of a wrong final output frequently sits several steps upstream, so knowing only that the final answer is wrong doesn\'t tell you which of potentially many earlier steps actually introduced the error' },
          { id: 'c', label: 'C', text: 'Symptoms and diagnoses are the same thing in agent debugging' },
          { id: 'd', label: 'D', text: 'Only the first step in a trace can ever be the actual fault' }
        ],
        correctOptionId: 'b',
        explanation:
          'A wrong final output tells you something is broken, but in a multi-step trace it doesn\'t identify where — the diagnosis requires isolating the specific upstream step whose output was itself incorrect, which is the whole point of trace-level observability.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-11-mcq-02',
        question:
          'In the helpdesk scenario, why was the agent\'s final "escalate" decision not actually the bug, even though escalating the low-priority ticket was the wrong outcome?',
        options: [
          { id: 'a', label: 'A', text: 'The agent\'s decision was actually correct, and the ticket genuinely was urgent' },
          { id: 'b', label: 'B', text: 'The decision was reasonable given the (stale, incorrect) priority data the agent received from an upstream tool call — the agent reasoned correctly from bad information, so the fault was in the tool\'s caching behavior, not the agent\'s reasoning' },
          { id: 'c', label: 'C', text: 'Escalation decisions are never considered bugs in agent systems' },
          { id: 'd', label: 'D', text: 'The bug was in the system prompt\'s wording, unrelated to any tool call' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the scenario\'s central point: a step behaving correctly relative to its (bad) input is not the same as that step being the fault — the actual root cause was the stale-cache tool response two steps earlier, invisible without walking the trace back that far.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-11-mcq-03',
        question:
          'Why would rewriting the helpdesk agent\'s system prompt have failed to fix the escalation bug in the scenario?',
        options: [
          { id: 'a', label: 'A', text: 'System prompts cannot be edited once an agent is deployed' },
          { id: 'b', label: 'B', text: 'The defect was a caching bug in the tool three steps upstream, not a reasoning flaw in the agent — no amount of system prompt rewriting changes what data the tool returns, so the same stale-data failure would recur' },
          { id: 'c', label: 'C', text: 'Rewriting the system prompt would have fixed it, and the scenario is describing a successful fix' },
          { id: 'd', label: 'D', text: 'The agent doesn\'t use a system prompt at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'Misdiagnosing a tool bug as a reasoning bug leads to fixing the wrong layer entirely — this is exactly why root-causing via the backward trace, rather than guessing based on the symptom alone, matters: it points at the tool, not the prompt.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-11-mcq-04',
        question:
          'What does trace-level observability capture that plain input/output logging of an agent does not?',
        options: [
          { id: 'a', label: 'A', text: 'Only the total execution time of the run' },
          { id: 'b', label: 'B', text: 'Every LLM call, every tool call and its raw result, and every intermediate reasoning step within a single execution — not just the initial input and the final output' },
          { id: 'c', label: 'C', text: 'Only whether the run succeeded or failed, as a boolean' },
          { id: 'd', label: 'D', text: 'Trace-level observability and input/output logging capture identical information' }
        ],
        correctOptionId: 'b',
        explanation:
          'Input/output logging alone would have shown "ticket, escalated" — enough to know something happened, but nothing about the intermediate tool calls that would reveal the stale-cache root cause. Trace-level capture of every intermediate step is what makes backward root-causing possible at all.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-11-mcq-05',
        question:
          'How does the backward-trace debugging technique in this lesson generalize the diagnostic approach from the earlier RAG lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The two techniques are unrelated; RAG evaluation and agent debugging solve entirely different problems' },
          { id: 'b', label: 'B', text: 'The RAG lesson isolated whether a wrong answer was a retrieval-stage or generation-stage failure using separate metrics; this lesson applies the same "isolate which specific stage introduced the error" principle to any number of steps in any agent, not just a two-stage pipeline' },
          { id: 'c', label: 'C', text: 'RAGAS metrics are used directly to debug any agent, including non-RAG agents' },
          { id: 'd', label: 'D', text: 'The RAG lesson\'s technique only applies to retrieval, and has no broader lesson for agent debugging' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both techniques share the same core discipline: don\'t judge the whole system by its final output alone — separately check each distinguishable stage (two stages in RAG, any number of steps in a general agent trace) to find exactly where the error was introduced.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-agentic-ai-core-11-mcq-06',
        question:
          'After root-causing the helpdesk escalation bug to the stale-cache tool response, what should happen next according to the lesson\'s closing-the-loop principle?',
        options: [
          { id: 'a', label: 'A', text: 'Nothing further is needed once the immediate ticket is manually corrected' },
          { id: 'b', label: 'B', text: 'The specific failing trace should be turned into a permanent, automatically-run regression test or eval case (e.g. a mocked stale-cache tool response with an assertion that the agent no longer escalates), so the same failure mode is caught automatically in the future' },
          { id: 'c', label: 'C', text: 'The agent should be replaced entirely with a fixed workflow' },
          { id: 'd', label: 'D', text: 'The bug should be left undocumented since agent bugs cannot be reliably reproduced' }
        ],
        correctOptionId: 'b',
        explanation:
          'Closing the loop — converting a found failure into a permanent automated test — is what prevents the same failure mode from being silently rediscovered later; it\'s the same disciplined instinct as a regression test in traditional software, applied to a system that\'s otherwise harder to reproduce failures in on demand.'
      }
    ]
  }
};

export function getLessonInteractions(courseSlug, moduleSlug, lessonSlug) {
  return lessonInteractions[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonInteractions;
