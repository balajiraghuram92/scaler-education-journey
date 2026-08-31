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
  },
  'fde-curriculum/fde-foundations/01-the-fde-role-customer-embedded-engineering': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-01-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — FDE ACCOUNTABILITY & SCOPE',
        question:
          'What is the key practical difference between an FDE\'s accountability and a typical product engineer\'s?',
        options: [
          { id: 'a', label: 'A', text: 'FDEs never write production code, only prototypes' },
          { id: 'b', label: 'B', text: 'Judgment calls a product engineer would escalate to a PM or tech lead — scope, first slice, demo-readiness — are the FDE\'s own to make in real time, often with few or no other engineers on-site' },
          { id: 'c', label: 'C', text: 'FDEs work exclusively on internal company tools, never customer-facing systems' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference in accountability between the two roles' }
        ],
        correctOptionId: 'b',
        explanation:
          'The embedded, often-solo nature of FDE engagements means scope and judgment decisions that would normally go through a PM or tech lead review become the FDE\'s direct responsibility, made under real customer-facing time pressure.',
        incorrectExplanation:
          'Consider where decisions about scope, first slice, and demo-readiness are made and who is present when they are made.',
        hint: 'Product engineers escalate scope and readiness decisions to PMs; embedded FDEs make these judgment calls in real time.'
      },
      {
        id: 'lesson-fde-fde-foundations-01-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — THE DISCIPLINE OF NARROW SLICES',
        question:
          'What is the lesson\'s specific cost argument for validating a narrow slice before building comprehensively?',
        options: [
          { id: 'a', label: 'A', text: 'Narrow slices always take less total engineering time than comprehensive builds, regardless of correctness' },
          { id: 'b', label: 'B', text: 'It\'s far cheaper to be wrong about a narrow, validated slice than to be comprehensively wrong across a whole platform\'s worth of unvalidated assumptions' },
          { id: 'c', label: 'C', text: 'Comprehensive builds are technically infeasible for any FDE engagement' },
          { id: 'd', label: 'D', text: 'There is no cost difference; the choice is purely about developer preference' }
        ],
        correctOptionId: 'b',
        explanation:
          'The argument isn\'t that narrow is always faster in raw hours — it\'s that the blast radius of being wrong is much smaller when the wrong guess is scoped to one validated slice rather than baked into an entire platform\'s assumptions.',
        incorrectExplanation:
          'Think about what happens when a full platform is built on an unverified guess versus validating assumptions on a small slice first.',
        hint: 'Validating a narrow slice limits the cost of being wrong about unvalidated assumptions.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-01-mcq-01',
        question:
          'How does the lesson define FDE success, in contrast to typical product-engineering success?',
        options: [
          { id: 'a', label: 'A', text: 'Number of features shipped against a quarterly roadmap' },
          { id: 'b', label: 'B', text: 'A specific, real customer outcome actually achieved — not roadmap completeness or code correctness alone' },
          { id: 'c', label: 'C', text: 'Lines of code delivered per engagement' },
          { id: 'd', label: 'D', text: 'Number of customer meetings attended' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson is explicit that FDE success is judged by a concrete outcome the customer experiences (a process now takes minutes instead of hours), not by shipped-feature count or code that merely runs without error.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-01-mcq-02',
        question:
          'What is the correct order of the FDE loop described in the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Prototype, discover, validate, instrument, enable' },
          { id: 'b', label: 'B', text: 'Discover, prototype, instrument, validate, enable' },
          { id: 'c', label: 'C', text: 'Enable, discover, prototype, validate, instrument' },
          { id: 'd', label: 'D', text: 'Instrument, validate, discover, prototype, enable' }
        ],
        correctOptionId: 'b',
        explanation:
          'The loop starts with understanding the real need (discover), builds the smallest provable slice (prototype), makes its behavior visible (instrument), confirms the actual outcome (validate), and transfers capability to the customer\'s own team (enable).'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-01-mcq-03',
        question:
          'Why did the FDE in the scenario spend day one shadowing a dispatcher instead of starting to build against "add AI to our dispatch process" directly?',
        options: [
          { id: 'a', label: 'A', text: 'Shadowing is a mandatory company policy unrelated to problem discovery' },
          { id: 'b', label: 'B', text: 'The literal request was too vague to build against without guessing; shadowing the real workflow was necessary to discover the actual, narrow pain point (the 20-minute cross-reference step) before committing to a build' },
          { id: 'c', label: 'C', text: 'The FDE didn\'t have the technical skill to start building yet' },
          { id: 'd', label: 'D', text: 'The operations lead explicitly forbade any code from being written on day one' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the discover step in action — building against the literal vague request risks comprehensively solving the wrong problem, whereas direct observation surfaced the actual, specific, narrow pain point worth targeting first.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-01-mcq-04',
        question:
          'Why did the FDE log the script\'s recommendation against what the dispatcher actually chose, run on real data in front of the dispatcher, rather than presenting the work in a slide deck?',
        options: [
          { id: 'a', label: 'A', text: 'Slide decks are technically impossible to produce for a dispatch system' },
          { id: 'b', label: 'B', text: 'A customer trusts evidence of real behavior on real data far more than a verbal promise or a slide describing intended behavior' },
          { id: 'c', label: 'C', text: 'Logging output has no bearing on customer trust, it\'s purely for the FDE\'s own debugging' },
          { id: 'd', label: 'D', text: 'This step was unnecessary and added no value beyond the working script itself' }
        ],
        correctOptionId: 'b',
        explanation:
          'Instrumentation makes the slice\'s actual behavior visible and provable, which is precisely why it earns more trust than a description or promise of what the system will eventually do.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-01-mcq-05',
        question:
          'Why does the lesson treat "enable" (transferring capability to the customer\'s own team) as a distinct, necessary step rather than an optional nice-to-have?',
        options: [
          { id: 'a', label: 'A', text: 'Enable is only relevant for engagements longer than six months' },
          { id: 'b', label: 'B', text: 'An engagement that ends with only the FDE understanding the system hasn\'t actually transferred capability, which undermines the point of embedding with the customer in the first place' },
          { id: 'c', label: 'C', text: 'Customers never want to operate systems themselves, they always prefer full outsourcing' },
          { id: 'd', label: 'D', text: 'Enable is a formality with no real impact on engagement success' }
        ],
        correctOptionId: 'b',
        explanation:
          'The value of an FDE engagement isn\'t just the artifact built, but the customer\'s own team\'s ability to operate and extend it — skipping enablement leaves that value locked inside the FDE\'s own head.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-01-mcq-06',
        question:
          'The operations lead asks the FDE to extend the dispatch solution to an unrelated warehouse process. What is the correct next step, according to the lesson\'s framework?',
        options: [
          { id: 'a', label: 'A', text: 'Assume the first week\'s solution architecture generalizes and extend it directly without further discovery' },
          { id: 'b', label: 'B', text: 'Apply the discover step again for the new process — the first slice\'s success doesn\'t imply the new request\'s actual need is already understood' },
          { id: 'c', label: 'C', text: 'Decline the request since FDEs should only work on one process per engagement' },
          { id: 'd', label: 'D', text: 'Skip straight to instrumenting a solution, since validation already happened once this engagement' }
        ],
        correctOptionId: 'b',
        explanation:
          'Each new request carries its own risk of being a vague ask masking a different real need — the loop restarts at discover for the new process rather than assuming the prior slice\'s approach transfers automatically.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/02-problem-discovery-and-solution-thinking-for-fdes': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-02-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — STATED REQUEST VS ROOT CAUSE',
        question:
          'Why is "add AI to our dispatch process" described as a solution-shaped request rather than a problem statement?',
        options: [
          { id: 'a', label: 'A', text: 'It is too short to be a valid request' },
          { id: 'b', label: 'B', text: 'It names a solution category (AI) rather than describing the actual current-state pain, its impact, or its cause — there\'s no way to check whether a given build actually addresses it' },
          { id: 'c', label: 'C', text: 'It explicitly mentions a specific technology, which automatically disqualifies it as a problem statement' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference between this request and a problem statement' }
        ],
        correctOptionId: 'b',
        explanation:
          'A request framed around a solution shape (AI, automation, a dashboard) doesn\'t commit to what specifically should improve, which is exactly why it can\'t be used to check whether a proposed build actually addresses the real need.',
        incorrectExplanation:
          'Distinguish between a customer prescribing an imagined solution versus describing the underlying friction.',
        hint: 'Customers often state an imagined solution rather than the underlying operational friction.'
      },
      {
        id: 'lesson-fde-fde-foundations-02-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — FALSIFIABLE SUCCESS SIGNALS',
        question:
          'What specific risk does defining a measurable success signal before building protect against, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The risk of writing too much code before starting' },
          { id: 'b', label: 'B', text: 'Unconsciously redefining success after the fact to match whatever the prototype happened to do well, producing a demo that looks convincing but was never tested against the real bar' },
          { id: 'c', label: 'C', text: 'The risk of the customer changing their mind about wanting the feature at all' },
          { id: 'd', label: 'D', text: 'There is no real risk; this step is purely a formality' }
        ],
        correctOptionId: 'b',
        explanation:
          'Without a signal fixed in advance, it\'s easy to retroactively frame whatever the prototype does as "success" — defining it first is what keeps validation honest rather than self-serving.',
        incorrectExplanation:
          'Consider what happens at demo time if there is no objective, measurable definition of success.',
        hint: 'Without an agreed falsifiable metric, neither side can objectively prove whether the prototype solved the problem.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-02-mcq-01',
        question:
          'How does the lesson say you know you\'ve reached the actual underlying need during root-cause questioning?',
        options: [
          { id: 'a', label: 'A', text: 'After exactly three rounds of "why," regardless of the answers' },
          { id: 'b', label: 'B', text: 'When the next "why" just restates the same answer differently instead of moving from a symptom toward a new cause' },
          { id: 'c', label: 'C', text: 'As soon as the customer stops answering questions' },
          { id: 'd', label: 'D', text: 'When the answer includes a specific dollar figure' }
        ],
        correctOptionId: 'b',
        explanation:
          'The technique isn\'t a fixed number of iterations — it\'s iterating until further questioning stops surfacing new causal information, which signals you\'ve reached something close to the actual root need.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-02-mcq-02',
        question:
          'What three components make up the problem-statement format the lesson recommends?',
        options: [
          { id: 'a', label: 'A', text: 'Solution, timeline, and budget' },
          { id: 'b', label: 'B', text: 'Current state, impact, and cause' },
          { id: 'c', label: 'C', text: 'Stakeholder, priority, and deadline' },
          { id: 'd', label: 'D', text: 'Feature list, acceptance criteria, and owner' }
        ],
        correctOptionId: 'b',
        explanation:
          'A problem statement describes what happens today concretely (current state), what it costs (impact), and why it happens (cause) — all without naming a solution, which is what makes it checkable against any proposed fix.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-02-mcq-03',
        question:
          'In the scenario, the success signal "misassigned deliveries drop to 0-1/week" was derived directly from which part of the problem statement?',
        options: [
          { id: 'a', label: 'A', text: 'The cause line (no shared availability view)' },
          { id: 'b', label: 'B', text: 'The impact line (an average of 2 misassigned deliveries per week)' },
          { id: 'c', label: 'C', text: 'The current-state line describing the 20-minute manual step' },
          { id: 'd', label: 'D', text: 'It was invented independently of the problem statement' }
        ],
        correctOptionId: 'b',
        explanation:
          'The measurable success signal is a direct, checkable transformation of the impact line\'s number — this is exactly why writing a specific, numeric impact matters, not just a qualitative description of harm.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-02-mcq-04',
        question:
          'Why can\'t "reduce dispatch errors" function as a validation signal the way "misassigned deliveries drop from 2/week to 0-1/week, measured over two weeks" can?',
        options: [
          { id: 'a', label: 'A', text: '"Reduce dispatch errors" is grammatically incorrect as a goal statement' },
          { id: 'b', label: 'B', text: '"Reduce dispatch errors" has no specific baseline, target, or measurement window, so there\'s no way to check directly against real data whether it was actually achieved' },
          { id: 'c', label: 'C', text: 'Vague goals are always false, while specific goals are always true' },
          { id: 'd', label: 'D', text: 'There is no practical difference between the two phrasings' }
        ],
        correctOptionId: 'b',
        explanation:
          'A falsifiable signal names a baseline, a target, and how/when it\'s measured — "reduce" alone could be satisfied by an improvement of any size at any time, which makes it impossible to fail and therefore useless as a real check.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-02-mcq-05',
        question:
          'What is the main risk of building directly against "add AI to our dispatch process" instead of the derived problem statement?',
        options: [
          { id: 'a', label: 'A', text: 'The build would be technically impossible to implement' },
          { id: 'b', label: 'B', text: 'The build could comprehensively address the wrong 80% of "dispatch" while missing the specific 20-minute cross-reference step that was actually causing the measurable harm' },
          { id: 'c', label: 'C', text: 'The customer would immediately reject any AI-labeled solution' },
          { id: 'd', label: 'D', text: 'There is no meaningful risk difference between the two starting points' }
        ],
        correctOptionId: 'b',
        explanation:
          'Without the discovery work, "dispatch" is broad enough that a technically impressive build could easily target a part of the process that isn\'t actually where the real, measurable pain lives.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-02-mcq-06',
        question:
          'What does it demonstrate if two genuinely different solution approaches can both satisfy the same success signal derived from a problem statement?',
        options: [
          { id: 'a', label: 'A', text: 'The problem statement was written incorrectly if more than one solution satisfies it' },
          { id: 'b', label: 'B', text: 'A well-written problem statement and success signal constrain what "success" means without prematurely constraining how to achieve it, leaving room for genuine solution-design judgment' },
          { id: 'c', label: 'C', text: 'Success signals are meaningless if multiple solutions can satisfy them' },
          { id: 'd', label: 'D', text: 'This situation should never occur in well-scoped FDE work' }
        ],
        correctOptionId: 'b',
        explanation:
          'A good problem statement fixes the outcome bar, not the implementation — leaving multiple valid solution shapes open is a feature of this discipline, not a flaw, since it preserves engineering judgment about how to get there.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/03-python-toolchain-and-environment-setup-pyenv-uv-ruff-mypy': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-03-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — MODERN PYTHON TOOLCHAIN CONSOLIDATION',
        question:
          'Which set of tools\' roles does uv consolidate into a single Rust binary?',
        options: [
          { id: 'a', label: 'A', text: 'flake8, black, and isort' },
          { id: 'b', label: 'B', text: 'pip, virtualenv, poetry, and pyenv' },
          { id: 'c', label: 'C', text: 'pytest, coverage, and tox' },
          { id: 'd', label: 'D', text: 'mypy and pyright' }
        ],
        correctOptionId: 'b',
        explanation:
          'uv handles Python version management (pyenv\'s former role), virtual environment creation (virtualenv), and dependency resolution/installation (pip and poetry) all in one fast native tool — the first group listed (flake8/black/isort) is ruff\'s consolidation, not uv\'s.',
        incorrectExplanation:
          'Look at the full stack of separate legacy tools (pip, virtualenv, pip-tools, poetry) that uv replaces.',
        hint: 'uv unifies Python version management, virtualenv creation, package resolution, and locking in a single fast tool.'
      },
      {
        id: 'lesson-fde-fde-foundations-03-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — LINTING VS STATIC TYPE CHECKING',
        question:
          'What category of bug does mypy catch that ruff\'s linting does not?',
        options: [
          { id: 'a', label: 'A', text: 'Missing semicolons at the end of statements' },
          { id: 'b', label: 'B', text: 'Type mismatches that are syntactically valid Python but semantically wrong, like passing a `str` where a function signature declares `int`' },
          { id: 'c', label: 'C', text: 'Unused imports' },
          { id: 'd', label: 'D', text: 'Inconsistent indentation' }
        ],
        correctOptionId: 'b',
        explanation:
          'ruff\'s linting and formatting operate on syntax and style; mypy performs static type analysis, catching a distinct category of bug — type mismatches — that\'s syntactically valid but semantically incorrect, which is exactly why both tools are used together, not as substitutes for each other.',
        incorrectExplanation:
          'Distinguish between fast AST linting and deep static type-checker cross-module analysis.',
        hint: 'ruff checks formatting and AST lint rules; mypy verifies type compatibility across module boundaries.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-03-mcq-01',
        question:
          'What problem did pyenv originally solve?',
        options: [
          { id: 'a', label: 'A', text: 'Linting and formatting Python code' },
          { id: 'b', label: 'B', text: 'Managing multiple installed Python versions on one machine and letting a project pin which version it needs, so different projects on the same laptop don\'t conflict' },
          { id: 'c', label: 'C', text: 'Resolving and locking third-party package dependency versions' },
          { id: 'd', label: 'D', text: 'Running Python tests' }
        ],
        correctOptionId: 'b',
        explanation:
          'pyenv\'s job was specifically Python-version management via shims and a project-level `.python-version` file — a distinct concern from dependency resolution (pip/poetry) or code quality (flake8/black), which uv and ruff respectively absorbed.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-03-mcq-02',
        question:
          'In the modern toolchain the lesson describes, where does uv, ruff, mypy, and pytest configuration typically live?',
        options: [
          { id: 'a', label: 'A', text: 'Each tool requires its own separate config file, with no consolidation possible' },
          { id: 'b', label: 'B', text: 'A single `pyproject.toml` file, replacing the older sprawl of `setup.py`, `setup.cfg`, `.flake8`, and `mypy.ini`' },
          { id: 'c', label: 'C', text: 'Environment variables set in the shell profile' },
          { id: 'd', label: 'D', text: 'A `Dockerfile` is required to configure any of these tools' }
        ],
        correctOptionId: 'b',
        explanation:
          '`pyproject.toml` has become the single configuration surface for the whole modern Python toolchain, eliminating the need to hunt across several separate config files scattered through the project.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-03-mcq-03',
        question:
          'Why did the inherited script "work fine" on the customer\'s laptop but fail on the FDE\'s machine?',
        options: [
          { id: 'a', label: 'A', text: 'The FDE\'s machine had a corrupted Python installation' },
          { id: 'b', label: 'B', text: 'The project had no lockfile and no pinned versions, so each machine\'s `pip install` independently resolved to whatever compatible versions happened to be latest at install time, and those had drifted between machines over time' },
          { id: 'c', label: 'C', text: 'The script used a Python syntax feature that doesn\'t exist on any machine but the customer\'s' },
          { id: 'd', label: 'D', text: 'The customer\'s laptop had a newer Python version than the FDE\'s machine, which is always the cause of import errors' }
        ],
        correctOptionId: 'b',
        explanation:
          'Unpinned dependencies mean "works on my machine" is really "happens to resolve favorably on my machine at this point in time" — exactly the fragility a lockfile is designed to eliminate.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-03-mcq-04',
        question:
          'Why does the lesson say deleting and recreating the environment from the lockfile is the real test of reproducibility, rather than just confirming the project currently runs?',
        options: [
          { id: 'a', label: 'A', text: 'Deleting the environment is required by uv\'s license terms' },
          { id: 'b', label: 'B', text: 'A project that currently runs might still be relying on stale, already-installed packages that wouldn\'t actually be reproduced from a clean install — deleting and rebuilding from the lockfile is what actually proves the pinned versions are sufficient' },
          { id: 'c', label: 'C', text: 'This step has no diagnostic value beyond what simply running the project already shows' },
          { id: 'd', label: 'D', text: 'Lockfiles cannot be trusted under any circumstances without manual verification of every line' }
        ],
        correctOptionId: 'b',
        explanation:
          'A currently-working environment could be masking a gap in the lockfile if it still contains leftover packages from before the lockfile existed — only a clean rebuild proves the lockfile alone is sufficient to reproduce a working environment.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-03-mcq-05',
        question:
          'Why does the lesson argue toolchain consolidation (uv, ruff) matters more for FDEs specifically than for engineers working on one long-lived internal codebase?',
        options: [
          { id: 'a', label: 'A', text: 'Consolidated tools are only available to FDE-specific accounts' },
          { id: 'b', label: 'B', text: 'FDEs repeatedly stand up clean environments on unfamiliar customer infrastructure they didn\'t originally build, so fewer tools and a single lockfile reduce the number of ways that unfamiliar environment can silently diverge from what worked elsewhere' },
          { id: 'c', label: 'C', text: 'Internal-codebase engineers never need reproducible environments' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference in how this benefit applies across roles' }
        ],
        correctOptionId: 'b',
        explanation:
          'The recurring pattern of standing up environments on unfamiliar customer infrastructure is exactly where fewer moving parts and a single source of pinned truth (the lockfile) pays off most directly.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-03-mcq-06',
        question:
          'Why would an FDE want ruff, mypy, and pytest in a separate dependency group from the project\'s runtime dependencies, when deploying code into a customer\'s production environment?',
        options: [
          { id: 'a', label: 'A', text: 'Development tools are technically incompatible with production Python versions' },
          { id: 'b', label: 'B', text: 'The customer\'s production environment should only need what the running system actually requires — installing development-only tooling into it adds unnecessary attack surface and bloat with no runtime benefit' },
          { id: 'c', label: 'C', text: 'Separating dependency groups is required by uv and cannot be configured otherwise' },
          { id: 'd', label: 'D', text: 'There is no meaningful reason to separate them; it\'s purely a style preference' }
        ],
        correctOptionId: 'b',
        explanation:
          'Development tooling has no role in what the deployed system actually needs to run — keeping it in a separate dependency group means the production install stays minimal, which matters for both attack surface and deployment size in a customer\'s environment.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/04-iterators-generators-and-comprehensions': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-04-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — ITERTOOLS.GROUPBY CONSECUTIVE KEY CONTRACT',
        question:
          '`itertools.groupby` is used on a list of records that is NOT sorted by the grouping key. What happens?',
        options: [
          { id: 'a', label: 'A', text: 'It raises a `ValueError` requiring the input to be sorted first' },
          { id: 'b', label: 'B', text: 'It silently produces multiple separate groups for the same key wherever that key happens to reappear in the unsorted input order, with no error raised — it groups only consecutive equal keys, and does not sort first' },
          { id: 'c', label: 'C', text: 'It automatically sorts the input before grouping, so the result is always correct regardless of input order' },
          { id: 'd', label: 'D', text: 'It returns an empty result if the input isn\'t sorted' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the specific trap the lesson calls out: `groupby` only groups consecutive matches and never sorts, so unsorted input produces a plausible-looking but wrong result with no error — the fix is always sorting by the same key first.',
        incorrectExplanation:
          'Remember that groupby does not build a hash table; it breaks groups whenever the key changes in stream order.',
        hint: 'itertools.groupby only groups consecutive identical keys; unsorted input produces multiple fragmented groups for the same key.'
      },
      {
        id: 'lesson-fde-fde-foundations-04-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — STREAMING MEMORY EFFICIENCY',
        question:
          'Why did fixing the CSV pipeline\'s memory problem require only changing list comprehensions to generator expressions, with no change to the CSV library or the write step?',
        options: [
          { id: 'a', label: 'A', text: 'The CSV library needed to be replaced with a streaming-specific alternative' },
          { id: 'b', label: 'B', text: 'The CSV reader already yields rows one at a time as an iterator, and the write step already consumes its input one item at a time — the only place eager materialization was introduced was the intermediate list comprehensions, so removing just those restores the pipeline\'s lazy, constant-memory property end to end' },
          { id: 'c', label: 'C', text: 'The write step needed to be rewritten to accept a list instead of an iterator' },
          { id: 'd', label: 'D', text: 'This fix is incomplete and additional library changes were actually required' }
        ],
        correctOptionId: 'b',
        explanation:
          'Since both endpoints of the pipeline (the reader and the writer) were already iterator-based, the bug was isolated entirely to the eager list comprehensions in the middle — replacing just those with generator expressions was sufficient to make the whole chain lazy again.',
        incorrectExplanation:
          'Consider how generator expressions change evaluation from eager in-memory materialization to lazy row-by-row streaming.',
        hint: 'Generators yield records one at a time, keeping memory constant O(1) regardless of file size.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-04-mcq-01',
        question:
          'What makes a Python function a generator function?',
        options: [
          { id: 'a', label: 'A', text: 'It must be decorated with `@generator`' },
          { id: 'b', label: 'B', text: 'It returns a list explicitly' },
          { id: 'c', label: 'C', text: '' },
          { id: 'd', label: 'D', text: 'It must not take any arguments' }
        ],
        correctOptionId: 'a',
        explanation:
          'Containing `yield` is what transforms a function\'s calling convention — instead of running to completion and returning once, calling it produces a generator object whose execution suspends and resumes across `__next__` calls.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-04-mcq-02',
        question:
          'What happens to a generator\'s local variables and loop position between successive calls to `__next__`?',
        options: [
          { id: 'a', label: 'A', text: 'They are reset to their initial values on every call' },
          { id: 'b', label: 'B', text: 'They are suspended and preserved exactly as they were, resuming from that point on the next call, rather than being recomputed from scratch' },
          { id: 'c', label: 'C', text: 'They are discarded, and the generator has no memory of prior calls at all' },
          { id: 'd', label: 'D', text: 'They are stored in a global variable accessible outside the generator' }
        ],
        correctOptionId: 'b',
        explanation:
          'This suspend-and-resume behavior is exactly what makes laziness possible — the generator picks up exactly where it left off rather than restarting, which is why it can produce values one at a time without recomputing prior state.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-04-mcq-03',
        question:
          'You need to sort a moderately-sized collection of transformed values and then index into it repeatedly afterward. Which is the more appropriate choice, and why?',
        options: [
          { id: 'a', label: 'A', text: 'A generator expression, since it\'s always more memory-efficient regardless of use case' },
          { id: 'b', label: 'B', text: 'A list comprehension, since you genuinely need the full materialized list to sort and repeatedly index into it — a generator would be consumed after one pass and couldn\'t support repeated indexing' },
          { id: 'c', label: 'C', text: 'Neither is appropriate; only a dict comprehension supports repeated indexing' },
          { id: 'd', label: 'D', text: 'It doesn\'t matter, the two are functionally interchangeable in every case' }
        ],
        correctOptionId: 'b',
        explanation:
          'A generator is single-pass and doesn\'t support indexing or being iterated more than once — when the full collection is genuinely needed for repeated access, a list comprehension is the correct choice despite using more memory upfront.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-04-mcq-04',
        question:
          'Why did the first CSV-processing attempt work on a small sample file but run out of memory on the customer\'s actual multi-gigabyte export?',
        options: [
          { id: 'a', label: 'A', text: 'The CSV library used is fundamentally incompatible with large files' },
          { id: 'b', label: 'B', text: 'Building a full list of every parsed row with a list comprehension before filtering means the entire dataset must exist in memory at once, which only becomes a problem once the dataset is large enough to exceed available memory' },
          { id: 'c', label: 'C', text: 'Python cannot process files larger than a few megabytes under any circumstances' },
          { id: 'd', label: 'D', text: 'The customer\'s export file was corrupted' }
        ],
        correctOptionId: 'b',
        explanation:
          'The list comprehension\'s eager materialization was invisible at small scale (a small list fits in memory trivially) and only became a real failure once the input size grew large enough to matter — exactly the kind of bug that passes local testing and fails in production.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-04-mcq-05',
        question:
          '`itertools.islice(generator, 5)` is used to get the first 5 values from a generator that could in principle produce millions of values. What happens to the values beyond the first 5?',
        options: [
          { id: 'a', label: 'A', text: 'All millions of values are computed first, and only the first 5 are returned' },
          { id: 'b', label: 'B', text: 'They are never computed at all — `islice` stops pulling from the underlying generator once it has produced the requested 5 values, preserving laziness' },
          { id: 'c', label: 'C', text: '`islice` raises an error if the generator could produce more than the requested count' },
          { id: 'd', label: 'D', text: 'The generator is converted to a list internally before slicing' }
        ],
        correctOptionId: 'b',
        explanation:
          '`islice` is itself lazy — it only pulls as many values from the underlying iterator as actually requested, which is exactly why it\'s useful for "give me the first N" without forcing the full (potentially huge or infinite) sequence to be computed.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-04-mcq-06',
        question:
          'Adding a running count of filtered-out rows to the lazy CSV pipeline, without breaking its constant-memory property, requires which approach?',
        options: [
          { id: 'a', label: 'A', text: 'Converting the entire pipeline back into list comprehensions so the filtered rows can be counted with `len()`' },
          { id: 'b', label: 'B', text: 'Accumulating a simple counter variable that\'s incremented as each row is evaluated within the existing generator chain, rather than collecting filtered rows into a list to count them afterward' },
          { id: 'c', label: 'C', text: 'This cannot be done without breaking the pipeline\'s lazy property' },
          { id: 'd', label: 'D', text: 'Running the pipeline twice, once for the data and once for the count' }
        ],
        correctOptionId: 'b',
        explanation:
          'A scalar counter incremented inline as the pipeline processes each item adds negligible, constant memory — the key insight is that accumulating a small piece of state alongside a generator chain doesn\'t require materializing the underlying data, only collecting individual items into a list would.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/05-closures-decorators-and-context-managers': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-05-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — CLOSURE LATE-BINDING PITFALL',
        question:
          'What is the standard fix for the late-binding closure gotcha in `[lambda: i for i in range(3)]`?',
        options: [
          { id: 'a', label: 'A', text: 'Use a `for` loop instead of a list comprehension, which fixes the issue automatically' },
          { id: 'b', label: 'B', text: 'Pass the loop variable as a default argument, `lambda i=i: i`, which captures the current value at each iteration instead of a shared reference to the loop variable' },
          { id: 'c', label: 'C', text: 'This behavior cannot be fixed and must be avoided by never using closures in loops' },
          { id: 'd', label: 'D', text: 'Rename the loop variable to something other than `i`' }
        ],
        correctOptionId: 'b',
        explanation:
          'Default argument values are evaluated once, at function-definition time, which forces early binding — capturing the current value of `i` at each iteration rather than a shared reference to the loop variable itself.',
        incorrectExplanation:
          'Remember that Python closures look up variables in the enclosing scope when called, not when defined, unless bound via default args.',
        hint: 'Use default argument assignment (lambda i=i: i) to capture the value of the loop variable at definition time.'
      },
      {
        id: 'lesson-fde-fde-foundations-05-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — CONTEXT MANAGER YIELD BOUNDARY',
        question:
          'In a generator function decorated with `@contextlib.contextmanager`, what do the code before `yield` and the code after `yield` correspond to?',
        options: [
          { id: 'a', label: 'A', text: 'Both sections run as `__enter__`; there is no equivalent of `__exit__` in this pattern' },
          { id: 'b', label: 'B', text: 'Code before `yield` runs as `__enter__` (with the yielded value bound by `as`); code after `yield` runs as `__exit__`, guaranteed to execute even if the `with` block\'s body raised' },
          { id: 'c', label: 'C', text: 'Code before `yield` is optional and has no special meaning' },
          { id: 'd', label: 'D', text: 'The code after `yield` only runs if no exception occurred in the `with` block' }
        ],
        correctOptionId: 'b',
        explanation:
          'This maps the generator\'s structure directly onto the context manager protocol — critically, the code after `yield` runs regardless of whether the `with` block succeeded or raised, which is what provides the cleanup guarantee.',
        incorrectExplanation:
          'Think about how the with statement enters and exits the block around the single yielded value.',
        hint: 'Code before yield executes during __enter__; code after yield in a finally block executes during __exit__.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-05-mcq-01',
        question:
          'Does a closure capture the value of an enclosing-scope variable at the moment the closure is created, or a reference to the variable itself?',
        options: [
          { id: 'a', label: 'A', text: 'A copy of the value at the moment the closure is created, permanently fixed' },
          { id: 'b', label: 'B', text: 'A reference to the variable itself — if the variable\'s value changes after the closure is created but before it\'s called, the closure sees the updated value, not a snapshot from creation time' },
          { id: 'c', label: 'C', text: 'Closures cannot access enclosing-scope variables at all' },
          { id: 'd', label: 'D', text: 'It depends on whether the variable is a string or a number' }
        ],
        correctOptionId: 'b',
        explanation:
          'This "by reference, not value-at-definition-time" behavior is exactly what causes the late-binding loop-variable gotcha — every closure created in the loop shares the same underlying variable, not an independent snapshot.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-05-mcq-02',
        question:
          'What problem does `functools.wraps` solve when writing a decorator?',
        options: [
          { id: 'a', label: 'A', text: 'Without it, the decorator fails to execute at all' },
          { id: 'b', label: 'B', text: 'Without it, the wrapper function silently replaces the original function\'s `__name__`, docstring, and other metadata, which breaks introspection, debugging tools, and anything relying on the function\'s identity' },
          { id: 'c', label: 'C', text: 'It is required for a decorator to accept arguments' },
          { id: 'd', label: 'D', text: 'It improves the runtime performance of the wrapped function' }
        ],
        correctOptionId: 'b',
        explanation:
          'A decorator without `functools.wraps` still works functionally, but the wrapped function reports the wrapper\'s own name and docstring instead of the original\'s, which silently breaks introspection and debugging.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-05-mcq-03',
        question:
          'Why does a decorator that itself takes arguments, like `@retry(times=3)`, need an extra level of function nesting compared to a plain `@decorator`?',
        options: [
          { id: 'a', label: 'A', text: 'Parameterized decorators do not actually require any extra nesting' },
          { id: 'b', label: 'B', text: 'The outermost function has to accept the decorator\'s own arguments (`times=3`) and return the actual decorator function, which then accepts and wraps the target function — three levels deep total' },
          { id: 'c', label: 'C', text: 'Python requires exactly three levels of nesting for every decorator, parameterized or not' },
          { id: 'd', label: 'D', text: 'The extra nesting is only needed if `functools.wraps` is also used' }
        ],
        correctOptionId: 'b',
        explanation:
          '`@retry(times=3)` first calls `retry(times=3)`, which must return the actual decorator (a function expecting the target function), which itself returns the wrapper — three nested layers, one more than a plain decorator that skips the arguments layer.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-05-mcq-04',
        question:
          'What guarantee does a `with` block using a properly implemented context manager provide that a manual `try`/`finally` written at each call site does not reliably provide?',
        options: [
          { id: 'a', label: 'A', text: '`with` blocks execute faster than `try`/`finally` blocks' },
          { id: 'b', label: 'B', text: 'The cleanup logic is defined once, correctly, in the context manager itself, so every call site automatically gets correct cleanup-on-exception behavior without someone having to remember to write a correct `try`/`finally` every single time' },
          { id: 'c', label: 'C', text: '`try`/`finally` cannot handle exceptions at all' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference; the two approaches are identical in every way' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both mechanisms can achieve guaranteed cleanup, but a context manager centralizes that correctness once instead of relying on every call site remembering to write it correctly — a real and common source of bugs at scale.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-05-mcq-05',
        question:
          'In the scenario, why was `timed_operation` built as a context manager rather than as another decorator like `@retry`?',
        options: [
          { id: 'a', label: 'A', text: 'Decorators cannot measure elapsed time under any circumstances' },
          { id: 'b', label: 'B', text: 'The lesson doesn\'t state this must be a context manager rather than a decorator, but the scenario needs it to wrap a block of code (a `with` statement\'s body) directly at the call site, which is exactly what a context manager is designed for, distinct from wrapping an entire function definition the way a decorator does' },
          { id: 'c', label: 'C', text: 'Context managers execute faster than decorators for timing purposes' },
          { id: 'd', label: 'D', text: '`functools.wraps` is incompatible with timing logic' }
        ],
        correctOptionId: 'b',
        explanation:
          'A decorator wraps a whole function definition; a context manager wraps an arbitrary block of code at the call site via `with`. Timing "this specific operation right here" fits the context-manager shape more naturally than requiring the operation to be its own separately-defined function just to decorate it.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-05-mcq-06',
        question:
          'When combining `@retry` and `timed_operation` on the same flaky API call, what design question does the lesson say you need to explicitly decide?',
        options: [
          { id: 'a', label: 'A', text: 'Whether `functools.wraps` should be applied to the context manager as well as the decorator' },
          { id: 'b', label: 'B', text: 'Whether the timer should measure the total elapsed time across all retry attempts, or only the duration of the final successful attempt — these answer different diagnostic questions and the combination doesn\'t pick one for you automatically' },
          { id: 'c', label: 'C', text: 'This combination is technically impossible and one of the two must be dropped' },
          { id: 'd', label: 'D', text: 'Whether the retry decorator should be converted into a context manager to match the timer\'s style' }
        ],
        correctOptionId: 'b',
        explanation:
          '"How long did this operation take" is ambiguous once retries are involved — total wall-clock time including failed attempts tells you something different from just the successful attempt\'s duration, and the implementation has to deliberately choose which question it\'s answering, not default to one silently.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/06-oop-concurrency-and-async-python': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-06-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — EVENT LOOP BLOCKING HAZARD',
        question:
          'Why does a single blocking (non-`await`-ing) call inside an `async def` function stall every other task the event loop is managing, not just the task that made the call?',
        options: [
          { id: 'a', label: 'A', text: 'Blocking calls raise an exception that propagates to every other task' },
          { id: 'b', label: 'B', text: 'A blocking call never yields control back to the event loop, and since only one thread is running all the tasks cooperatively, nothing else can run until that blocking call finally returns' },
          { id: 'c', label: 'C', text: 'This only affects tasks created after the blocking call, not ones already running' },
          { id: 'd', label: 'D', text: 'This description is incorrect; a blocking call only affects the task that made it' }
        ],
        correctOptionId: 'b',
        explanation:
          'Because asyncio\'s concurrency depends entirely on tasks voluntarily yielding at `await` points, a call that never yields (a blocking call) monopolizes the single thread for its whole duration, silently stalling every other task with no error to indicate why.',
        incorrectExplanation:
          'Remember that asyncio uses cooperative multitasking on a single OS thread; blocking that thread blocks all tasks.',
        hint: 'Asyncio runs on a single thread; any synchronous blocking call freezes the entire event loop from running other coroutines.'
      },
      {
        id: 'lesson-fde-fde-foundations-06-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — GIL & CONCURRENCY PARADIGMS',
        question:
          'Why does threading provide a real speed benefit for I/O-bound work but not for CPU-bound work?',
        options: [
          { id: 'a', label: 'A', text: 'I/O operations are always faster than CPU operations regardless of threading' },
          { id: 'b', label: 'B', text: 'The GIL is released while a thread is blocked waiting on I/O, letting another thread run during that wait; for CPU-bound work there\'s no wait to release the GIL during, so threads simply take turns with no parallel gain' },
          { id: 'c', label: 'C', text: 'Threading provides no benefit for either type of workload' },
          { id: 'd', label: 'D', text: 'CPU-bound work cannot be run in a thread at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'The GIL\'s release during I/O waits is the specific mechanism that makes threading useful for I/O-bound work — CPU-bound work never triggers that release, so threads just take turns executing on the single GIL-holding slot with no real parallelism.',
        incorrectExplanation:
          'Consider when CPython releases the GIL during network/disk wait versus continuous bytecode computation.',
        hint: 'The GIL is released while waiting on I/O operations, but CPU-bound tasks compete for execution time on a single core.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-06-mcq-01',
        question:
          'What does CPython\'s Global Interpreter Lock (GIL) actually restrict?',
        options: [
          { id: 'a', label: 'A', text: 'A Python program can only ever run a single thread total, with no ability to create more' },
          { id: 'b', label: 'B', text: 'Only one thread can execute Python bytecode at a time, regardless of how many CPU cores are available' },
          { id: 'c', label: 'C', text: 'Python programs cannot perform any I/O operations' },
          { id: 'd', label: 'D', text: 'The GIL only affects programs running on a single-core machine' }
        ],
        correctOptionId: 'b',
        explanation:
          'Multiple threads can exist, but only one executes Python bytecode at any given instant due to the GIL — this single fact is what determines whether threading actually parallelizes a given workload or not.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-06-mcq-02',
        question:
          'Why does multiprocessing achieve real parallelism for CPU-bound work where threading does not?',
        options: [
          { id: 'a', label: 'A', text: 'Processes run faster than threads for any workload, unrelated to the GIL' },
          { id: 'b', label: 'B', text: 'Each process has its own separate Python interpreter and its own GIL, so multiple processes can genuinely execute Python bytecode simultaneously on multiple cores, unlike threads which share one interpreter and one GIL' },
          { id: 'c', label: 'C', text: 'Multiprocessing eliminates the need for a GIL entirely, even within a single process' },
          { id: 'd', label: 'D', text: 'There is no real difference between multiprocessing and threading for CPU-bound work' }
        ],
        correctOptionId: 'b',
        explanation:
          'Sidestepping the shared GIL by using entirely separate interpreter processes is exactly what makes multiprocessing capable of true parallel execution on multiple cores, at the cost of higher memory overhead and explicit data serialization between processes.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-06-mcq-03',
        question:
          'How does asyncio achieve concurrency using only a single thread?',
        options: [
          { id: 'a', label: 'A', text: 'asyncio secretly spawns operating system threads behind the scenes for every `await`' },
          { id: 'b', label: 'B', text: 'A task voluntarily yields control at each `await` point, letting the single-threaded event loop run other tasks during that wait, and resumes once its own wait is satisfied — cooperative, not preemptive, switching' },
          { id: 'c', label: 'C', text: 'asyncio bypasses the GIL entirely, similar to multiprocessing' },
          { id: 'd', label: 'D', text: 'asyncio achieves concurrency by running tasks in a random, non-deterministic order with no coordination' }
        ],
        correctOptionId: 'b',
        explanation:
          'asyncio\'s model is cooperative multitasking on one thread — tasks explicitly hand control back to the event loop at `await` points, which is what lets many I/O waits overlap without the overhead of real OS threads or processes.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-06-mcq-04',
        question:
          'Why is asyncio the right model for the five-sequential-API-calls scenario, rather than multiprocessing?',
        options: [
          { id: 'a', label: 'A', text: 'Multiprocessing cannot make HTTP requests under any circumstances' },
          { id: 'b', label: 'B', text: 'The bottleneck is I/O wait (network round-trips), not CPU computation, and asyncio\'s cooperative model overlaps I/O waits efficiently without the memory and process-management overhead multiprocessing would add for no corresponding benefit' },
          { id: 'c', label: 'C', text: 'asyncio is always the correct choice for every workload, regardless of shape' },
          { id: 'd', label: 'D', text: 'Multiprocessing and asyncio produce identical results for I/O-bound work, so the choice doesn\'t matter' }
        ],
        correctOptionId: 'b',
        explanation:
          'Multiprocessing solves a CPU-parallelism problem, which this scenario doesn\'t have — it would add process overhead without addressing the actual bottleneck (waiting on network responses), which asyncio\'s cooperative concurrency handles directly and cheaply.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-06-mcq-05',
        question:
          'Why would converting the scenario\'s CPU-bound record-transformation step to `async`/`await` provide no real benefit, even though the rest of the integration benefits from asyncio?',
        options: [
          { id: 'a', label: 'A', text: '`async`/`await` syntax is technically incompatible with data transformation code' },
          { id: 'b', label: 'B', text: 'The step doesn\'t wait on anything — it\'s pure computation — so there\'s no I/O wait for asyncio\'s cooperative yielding to exploit; if it becomes a bottleneck, multiprocessing (real parallelism across cores) would help, not `async`/`await`' },
          { id: 'c', label: 'C', text: 'Every step in a program must use the same concurrency model, so it should stay synchronous to match unrelated parts of the codebase' },
          { id: 'd', label: 'D', text: 'asyncio always speeds up any code it\'s applied to, so this reasoning is incorrect' }
        ],
        correctOptionId: 'b',
        explanation:
          'asyncio\'s entire benefit comes from overlapping waits during `await` points — a step with no waits to overlap gains nothing from being rewritten as async, which is exactly why matching the concurrency model to the actual bottleneck (I/O vs. CPU) matters more than defaulting to one model everywhere.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-06-mcq-06',
        question:
          'In the practice loop, replacing `asyncio.sleep(0.2)` with a real blocking `time.sleep(0.2)` inside one async function causes the whole batch to become slow again. Why?',
        options: [
          { id: 'a', label: 'A', text: '`time.sleep` and `asyncio.sleep` behave identically; the slowdown must be caused by something else' },
          { id: 'b', label: 'B', text: '`time.sleep` blocks the single thread entirely without yielding to the event loop, so no other coroutine can run during that 0.2 seconds, unlike `asyncio.sleep` which yields control back and lets other tasks proceed concurrently' },
          { id: 'c', label: 'C', text: '`time.sleep` raises an error that asyncio silently retries, adding delay' },
          { id: 'd', label: 'D', text: 'This only happens if `time.sleep` is called more than once in the same program' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a direct, hands-on demonstration of the blocking-call failure mode — `time.sleep` never yields to the event loop the way `asyncio.sleep` does, so it stalls every concurrent task for its full duration.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-06-mcq-07',
        question:
          'Why does the suggested extension explicitly call out that concurrent error handling in asyncio needs to be considered deliberately, rather than assumed to work like a single sequential try/except?',
        options: [
          { id: 'a', label: 'A', text: 'asyncio does not support exceptions at all, so error handling is irrelevant' },
          { id: 'b', label: 'B', text: 'With several coroutines running concurrently via something like `asyncio.gather`, one call\'s failure can, if not handled deliberately, cancel or otherwise affect the others — a naive single try/except wrapping the whole batch doesn\'t give the same per-call isolation a sequential loop\'s individual try/except blocks would' },
          { id: 'c', label: 'C', text: 'Concurrent and sequential error handling are always identical in behavior' },
          { id: 'd', label: 'D', text: 'Only the first coroutine\'s errors are ever caught in a concurrent batch' }
        ],
        correctOptionId: 'b',
        explanation:
          'Running calls concurrently changes the failure semantics compared to a sequential loop with per-iteration try/except — deliberately deciding how one call\'s failure should (or shouldn\'t) affect the others is a design decision the concurrency introduces, not something that carries over automatically from sequential code.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/07-pydantic-v2-structured-logging-and-profiling': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-07-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — PARSE, DON\'T VALIDATE',
        question:
          'Once a Pydantic model has successfully validated a piece of external data into an object, why can downstream code trust its shape without re-checking?',
        options: [
          { id: 'a', label: 'A', text: 'Pydantic models cannot be constructed with invalid data under any circumstances, even before validation runs' },
          { id: 'b', label: 'B', text: 'Construction itself was the check — if the object exists, it already satisfied the model\'s type and constraint rules, so re-validating downstream would be redundant' },
          { id: 'c', label: 'C', text: 'Downstream code should always re-validate regardless, Pydantic provides no real guarantee' },
          { id: 'd', label: 'D', text: 'This is only true for models with no optional fields' }
        ],
        correctOptionId: 'b',
        explanation:
          'The entire value of the "parse, don\'t validate" pattern is that a successfully constructed model instance is proof the data already passed validation — checking again downstream would just repeat work the constructor already did.',
        incorrectExplanation:
          'Consider the design principle of establishing a single validation boundary versus scattering type checks throughout the codebase.',
        hint: 'Validation at the boundary guarantees that internal code can assume strongly-typed, guaranteed-valid domain objects without defensive checks.'
      },
      {
        id: 'lesson-fde-fde-foundations-07-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — PROFILING METRICS: CUMULATIVE VS TOTAL TIME',
        question:
          'A profiler reports function `process_batch` with high cumulative time but low total/own time. What does this indicate?',
        options: [
          { id: 'a', label: 'A', text: '`process_batch` is definitely the function that needs to be optimized' },
          { id: 'b', label: 'B', text: '`process_batch` itself isn\'t the bottleneck — most of its cumulative time comes from functions it calls, so the actual slow code lives in one of those called functions, not in `process_batch`\'s own logic' },
          { id: 'c', label: 'C', text: 'High cumulative time with low own time is a measurement error and should be ignored' },
          { id: 'd', label: 'D', text: '`process_batch` is called far more often than any other function in the program' }
        ],
        correctOptionId: 'b',
        explanation:
          'Cumulative time includes everything a function calls; own/total time is just its own execution. A high cumulative but low own time means the real cost is downstream in a called function, not in this function\'s own code.',
        incorrectExplanation:
          'Distinguish between the time spent inside a function\'s own bytecode versus time spent inside child functions it calls.',
        hint: '`cumtime` includes time spent in subfunctions, while `tottime` measures only the function\'s own body execution.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-07-mcq-01',
        question:
          'Why is a typed settings object that fails loudly at startup on a missing environment variable specifically valuable for an FDE, compared to code that reads `os.environ.get()` with silent defaults?',
        options: [
          { id: 'a', label: 'A', text: '`pydantic-settings` is required by law for handling environment variables' },
          { id: 'b', label: 'B', text: 'An FDE\'s code runs against different, unfamiliar configuration on every customer\'s infrastructure, so a loud startup failure surfaces a misconfiguration immediately rather than as a mysterious runtime error hours into a demo' },
          { id: 'c', label: 'C', text: 'Silent defaults are always safer than loud failures in any context' },
          { id: 'd', label: 'D', text: 'This has no particular relevance to FDE work specifically' }
        ],
        correctOptionId: 'b',
        explanation:
          'The recurring FDE context — new, unfamiliar customer infrastructure every engagement — is exactly where a loud, immediate startup failure on bad configuration is more valuable than in a stable, long-lived internal environment where configuration rarely changes.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-07-mcq-02',
        question:
          'What can a structured log statement support that a free-text log line cannot, without a fragile regex against message wording?',
        options: [
          { id: 'a', label: 'A', text: 'Structured logs execute faster than free-text logs at runtime' },
          { id: 'b', label: 'B', text: 'Filtering, aggregating, and querying by specific field values (e.g. "show every record where duration_ms > 1000")' },
          { id: 'c', label: 'C', text: 'Free-text logs cannot be written to a file, only structured logs can' },
          { id: 'd', label: 'D', text: 'There is no practical difference between the two formats' }
        ],
        correctOptionId: 'b',
        explanation:
          'Structured logs carry queryable fields directly, so filtering by a specific value is a direct query rather than requiring a regex against a message string whose wording might change and silently break the query.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-07-mcq-03',
        question:
          'Why does the lesson argue structured logging matters more for an FDE than for an engineer on a long-lived internal team?',
        options: [
          { id: 'a', label: 'A', text: 'Internal teams never read logs at all' },
          { id: 'b', label: 'B', text: 'An FDE\'s logs are frequently read by someone else entirely — a customer\'s on-call engineer, an observability tool with no context on the FDE\'s personal habits — so a log only useful to the person who wrote it defeats the point' },
          { id: 'c', label: 'C', text: 'FDE code produces more log volume than internal team code by default' },
          { id: 'd', label: 'D', text: 'This distinction doesn\'t actually matter; the lesson treats the two cases identically' }
        ],
        correctOptionId: 'b',
        explanation:
          'The recurring theme of an FDE handing off work to people who didn\'t write it (echoing the "enable" step from the FDE-role lesson) applies directly to logs — they need to be legible to someone without the FDE\'s personal context.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-07-mcq-04',
        question:
          'Why does the lesson insist on profiling under realistic data volume rather than a small hand-picked test input?',
        options: [
          { id: 'a', label: 'A', text: 'Profilers technically cannot run against small inputs' },
          { id: 'b', label: 'B', text: 'A function\'s relative cost can invert entirely between small and large input sizes, so a profile against toy data can point optimization effort at exactly the wrong function' },
          { id: 'c', label: 'C', text: 'Small test inputs always produce identical relative costs to large inputs, so this is only a minor concern' },
          { id: 'd', label: 'D', text: 'Realistic-scale profiling is only needed for functions that use loops' }
        ],
        correctOptionId: 'b',
        explanation:
          'Algorithmic behavior that\'s invisible at small scale (like quadratic growth) can dominate at real scale, so a profile at the wrong scale risks misidentifying the actual bottleneck.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-07-mcq-05',
        question:
          'Why was the FDE able to identify the actual slow stage of the sync job from shared logs alone, without a second round of production access?',
        options: [
          { id: 'a', label: 'A', text: 'Because the customer happened to already know which stage was slow' },
          { id: 'b', label: 'B', text: 'Because every stage\'s Pydantic-validated events were logged with structured, queryable fields including per-stage duration, filtering the shared logs for duration outliers directly revealed which stage was slow, without needing live debugging access' },
          { id: 'c', label: 'C', text: 'Because Pydantic models automatically profile themselves' },
          { id: 'd', label: 'D', text: 'This was luck and would not generally be possible from logs alone' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct payoff of the earlier structured-logging investment — a diagnostic question answerable purely by filtering existing structured log data, without needing new production access at all.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-07-mcq-06',
        question:
          'Why did the FDE only request a scoped profiling run after narrowing the problem to the fetch stage via logs, rather than requesting a full profiling run of the entire job upfront?',
        options: [
          { id: 'a', label: 'A', text: 'Profiling an entire job is technically impossible' },
          { id: 'b', label: 'B', text: 'A scoped, targeted profiling request (specifically the fetch stage) is more likely to be granted quickly by the customer and produces a more directly useful result than an unscoped, broad request made before the actual bottleneck was known' },
          { id: 'c', label: 'C', text: 'Logs and profiling data are mutually exclusive and cannot be used together' },
          { id: 'd', label: 'D', text: 'There was no particular reason; either order would have worked identically' }
        ],
        correctOptionId: 'b',
        explanation:
          'Narrowing scope first via cheap, already-available log data before requesting a more invasive or costly diagnostic (production profiling access) is a practical sequencing decision that respects both the customer\'s constraints and gets to the answer faster.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/08-git-internals-github-workflows-and-ai-dev-tools-cursor-claude-code-mcp': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-08-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — GIT COMMIT REWRITE HAZARD',
        question:
          'Why is rebasing dangerous specifically on a branch other people have already pulled, but safe on a branch only you\'re working on?',
        options: [
          { id: 'a', label: 'A', text: 'Rebasing is always unsafe regardless of who else has pulled the branch' },
          { id: 'b', label: 'B', text: 'Rebasing creates new commit objects with different hashes; anyone who already pulled the old commits now has local history that diverges from the rewritten remote history, causing painful conflicts on their next pull' },
          { id: 'c', label: 'C', text: 'Rebasing only affects the remote repository, never local copies' },
          { id: 'd', label: 'D', text: 'This risk only applies to branches with more than 10 commits' }
        ],
        correctOptionId: 'b',
        explanation:
          'Since rebase produces new commit objects, anyone else\'s already-pulled copies of the old commits become orphaned relative to the rewritten history, creating a divergence that has to be manually reconciled — this is exactly what didn\'t happen with the FDE\'s declined rebase suggestion in the scenario.',
        incorrectExplanation:
          'Consider what happens to commit SHAs when replaying commits and how that impacts team members who branched from the original commits.',
        hint: 'Rebasing creates new commit hashes for existing changes, desynchronizing the histories of everyone sharing the branch.'
      },
      {
        id: 'lesson-fde-fde-foundations-08-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — AI DIFFS AS PROPOSALS',
        question:
          'How does the lesson connect an AI coding assistant proposing a diff to the function-calling pattern from the Agentic AI Core module?',
        options: [
          { id: 'a', label: 'A', text: 'The two concepts are unrelated; the comparison is purely coincidental phrasing' },
          { id: 'b', label: 'B', text: 'Both follow the same "model proposes, you/your code decides" seam — the assistant proposes a diff, but the FDE (not the tool) decides whether and how to actually apply it, just as a function call is proposed but not automatically executed' },
          { id: 'c', label: 'C', text: 'AI coding assistants execute diffs automatically with no review step, unlike function calling' },
          { id: 'd', label: 'D', text: 'Function calling and diff proposals both bypass any human decision point' }
        ],
        correctOptionId: 'b',
        explanation:
          'This mirrors the "model proposes a call, your code decides whether to execute" distinction from the built-in-tools lesson — here applied to code changes, with the human FDE as the decision point instead of application logic.',
        incorrectExplanation:
          'Think about the seam between proposal and execution: the model generates a candidate action, but the engineer and CI retain execution authority.',
        hint: 'The AI assistant only produces a proposed change; deterministic tests and human judgment gate whether that change is executed or merged.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-08-mcq-01',
        question:
          'What is a Git branch, at the object-model level?',
        options: [
          { id: 'a', label: 'A', text: 'A container that physically holds a copy of every commit made on it' },
          { id: 'b', label: 'B', text: 'A movable pointer to a single commit, updated to point at a new commit each time you commit while that branch is checked out' },
          { id: 'c', label: 'C', text: 'A separate, isolated copy of the entire repository\'s file contents' },
          { id: 'd', label: 'D', text: 'A tag that permanently marks one specific commit and never moves' }
        ],
        correctOptionId: 'b',
        explanation:
          'Understanding a branch as a movable pointer, not a container, is what makes operations like rebase (which moves where commits sit relative to other branches) reasoned rather than memorized.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-08-mcq-02',
        question:
          'What is the key structural difference between `merge` and `rebase`?',
        options: [
          { id: 'a', label: 'A', text: 'Merge and rebase produce identical resulting commit history in every case' },
          { id: 'b', label: 'B', text: 'Merge creates a new commit with two parents, preserving both branches\' history as it happened; rebase re-plays commits onto a new base, creating entirely new commit objects with new hashes, rewriting history' },
          { id: 'c', label: 'C', text: 'Rebase deletes commits permanently with no way to recover them' },
          { id: 'd', label: 'D', text: 'Merge only works on branches with a single commit' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the core distinction: merge preserves actual history via a two-parent commit; rebase creates new commit objects (even if the content looks the same) by replaying changes onto a different base, which is what makes it history-rewriting.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-08-mcq-03',
        question:
          'Why does the lesson argue a PR-plus-CI workflow substitutes for something an FDE often lacks, more than it does for an engineer on a large internal team?',
        options: [
          { id: 'a', label: 'A', text: 'CI checks run faster on FDE projects than on internal team projects' },
          { id: 'b', label: 'B', text: 'FDE work is often solo or in a very small on-site group, so an automated, required check provides a structural safety net that doesn\'t depend on a peer reviewer happening to be available, unlike routine code review on a larger team' },
          { id: 'c', label: 'C', text: 'Large internal teams never use PR-based workflows' },
          { id: 'd', label: 'D', text: 'This distinction is not actually meaningful; the lesson treats both cases identically' }
        ],
        correctOptionId: 'b',
        explanation:
          'The structural safety net argument is specific to the reduced peer-oversight reality of embedded, often-solo FDE work — CI as a required, always-available check substitutes for the review capacity a larger team would otherwise provide.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-08-mcq-04',
        question:
          'What does connecting an AI coding assistant like Claude Code to a customer\'s ticket tracker via MCP actually enable, in the scenario?',
        options: [
          { id: 'a', label: 'A', text: 'MCP allows the assistant to merge pull requests without any human review' },
          { id: 'b', label: 'B', text: 'The assistant can read the actual ticket description directly as additional context while drafting a change, rather than requiring the FDE to manually paste it in' },
          { id: 'c', label: 'C', text: 'MCP is unrelated to AI coding assistants and only applies to n8n workflows' },
          { id: 'd', label: 'D', text: 'MCP automatically rewrites Git history to match ticket descriptions' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is MCP\'s role as a context-connection mechanism, consistent with its use elsewhere in the course — it extends what external context a tool can pull in, here letting the coding assistant reach the ticket tracker directly instead of requiring manual copy-paste.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-08-mcq-05',
        question:
          'Why did the FDE accept the AI assistant\'s bug-fix diff but decline its rebase suggestion in the scenario?',
        options: [
          { id: 'a', label: 'A', text: 'The bug fix itself was actually incorrect and needed to be rejected' },
          { id: 'b', label: 'B', text: 'The bug fix was correctly scoped and safe to apply, but the rebase suggestion targeted a branch two other contractors had already pulled, which would have rewritten history they were actively working from — exactly the dangerous case identified earlier in the lesson' },
          { id: 'c', label: 'C', text: 'AI-proposed diffs should always be rejected in customer repositories as a blanket policy' },
          { id: 'd', label: 'D', text: 'The rebase suggestion was rejected purely because AI tools cannot perform Git operations' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a direct application of the shared-branch rebase danger from earlier in the lesson — the fix itself was fine, but the specific rebase suggestion targeted a branch with real, current dependents, making it the higher-risk part of the proposal to reject.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-08-mcq-06',
        question:
          'According to the lesson, what category of AI-assistant-proposed change deserves the most careful review before acceptance in an unfamiliar customer repository?',
        options: [
          { id: 'a', label: 'A', text: 'Any change under 5 lines long, regardless of what it does' },
          { id: 'b', label: 'B', text: 'History-rewriting operations (like a rebase on a shared branch) or changes that extend outside the stated scope of the actual task, since these carry consequences well beyond the immediate diff being reviewed' },
          { id: 'c', label: 'C', text: 'Changes to files with long names, since they\'re statistically more likely to be important' },
          { id: 'd', label: 'D', text: 'All AI-proposed changes carry identical risk and require identical scrutiny' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson specifically calls out history-rewriting git operations and scope-creeping changes as the higher-risk category — not line count or file naming, which don\'t correlate with actual consequence.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/09-testing-pytest-property-based-testing-and-ci': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-09-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — PROPERTY-BASED VS EXAMPLE-BASED TESTING',
        question:
          'What is the fundamental difference between property-based testing and example-based testing?',
        options: [
          { id: 'a', label: 'A', text: 'Property-based tests run faster than example-based tests in every case' },
          { id: 'b', label: 'B', text: 'Property-based testing specifies a property that should hold for all valid inputs and lets the framework generate a wide range of inputs to search for violations, rather than checking only specific, hand-picked example inputs' },
          { id: 'c', label: 'C', text: 'Property-based testing replaces the need to write any test assertions' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference; the two terms describe the same technique' }
        ],
        correctOptionId: 'b',
        explanation:
          'The core inversion is specifying a property instead of examples — the framework then generates inputs (including ones a human wouldn\'t think to write) to search for a case that breaks the stated property.',
        incorrectExplanation:
          'Distinguish between testing pre-defined static examples versus testing invariant properties over a generative input domain.',
        hint: 'Example tests verify specific inputs chosen by developer imagination; property tests verify universal invariants across hundreds of generated inputs.'
      },
      {
        id: 'lesson-fde-fde-foundations-09-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — HYPOTHESIS TEST SHRINKING',
        question:
          'Why is Hypothesis\'s automatic shrinking of a failing input to its minimal reproducing case valuable?',
        options: [
          { id: 'a', label: 'A', text: 'Shrinking makes the test suite run faster overall' },
          { id: 'b', label: 'B', text: 'A large, complex randomly-generated failing input is harder to debug than the smallest input that still triggers the same failure — shrinking makes the actual root cause easier to see' },
          { id: 'c', label: 'C', text: 'Shrinking is required for Hypothesis to detect a failure at all' },
          { id: 'd', label: 'D', text: 'Shrinking converts a property-based test back into an example-based test' }
        ],
        correctOptionId: 'b',
        explanation:
          'The debugging value comes specifically from reducing a large, possibly confusing generated input down to the minimal case that still fails — which is far easier to reason about than the original.',
        incorrectExplanation:
          'Consider the difficulty of debugging a failure when given a 10,000-line random string versus a 1-character minimal reproducer.',
        hint: 'Shrinking reduces a massive 500-character failing string down to the single minimal character (like a null byte) that actually triggers the bug.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-09-mcq-01',
        question:
          'What problem does `@pytest.mark.parametrize` solve compared to writing several near-duplicate test functions?',
        options: [
          { id: 'a', label: 'A', text: 'It makes tests run in parallel automatically' },
          { id: 'b', label: 'B', text: 'It collapses near-duplicate test logic into one function and a data table of input/expected-output pairs, so adding a new case is adding one row instead of a whole new function' },
          { id: 'c', label: 'C', text: 'It removes the need for assertions in test functions' },
          { id: 'd', label: 'D', text: 'It is required for pytest to discover any test at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'Parametrize\'s value is reducing duplication — the test logic is written once, and new cases are added as data, keeping the suite maintainable as it grows.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-09-mcq-02',
        question:
          'Why did the CSV pipeline\'s solid example-based test suite fail to catch the null-byte crash before it hit production?',
        options: [
          { id: 'a', label: 'A', text: 'The example-based tests were poorly written and contained bugs of their own' },
          { id: 'b', label: 'B', text: 'Example-based tests only check inputs a human specifically thought to write down, and no one writing the hand-picked examples anticipated an embedded null byte, so the suite never exercised that case' },
          { id: 'c', label: 'C', text: 'pytest cannot detect crashes under any circumstances' },
          { id: 'd', label: 'D', text: 'The null byte issue was unrelated to testing and was actually a deployment configuration problem' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is exactly the coverage gap property-based testing is designed to close — example-based tests are bounded by human imagination about what inputs to write, and real-world data routinely exceeds that imagination.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-09-mcq-03',
        question:
          'Why would a Hypothesis property test ("parsing any string should never raise an unhandled exception, only return a record or a clear validation error") have caught the null-byte bug during development?',
        options: [
          { id: 'a', label: 'A', text: 'This property test would not have caught the bug; only manual testing against the real customer file could have' },
          { id: 'b', label: 'B', text: 'Hypothesis\'s text-generation strategies deliberately include edge cases like null bytes and control characters, so the property test would generate exactly this kind of input while searching for a violation, catching it in CI before it reached production' },
          { id: 'c', label: 'C', text: 'Hypothesis only tests numeric inputs, not string inputs' },
          { id: 'd', label: 'D', text: 'Property-based tests cannot detect unhandled exceptions' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct payoff of property-based testing over example-based testing — Hypothesis\'s generation strategies are specifically built to explore edge cases like this without a human having to anticipate them individually.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-09-mcq-04',
        question:
          'How does this lesson\'s framing of CI connect to the reduced-peer-oversight argument from the Git/GitHub lesson?',
        options: [
          { id: 'a', label: 'A', text: 'CI and code review serve completely unrelated purposes with no meaningful connection' },
          { id: 'b', label: 'B', text: 'CI is the automated component of the same review substitute — it doesn\'t depend on a human reviewer\'s availability, catching regressions the moment they\'re introduced, which specifically benefits FDE work that often has less routine peer review than a larger team' },
          { id: 'c', label: 'C', text: 'CI replaces the need for any human review of any kind, ever' },
          { id: 'd', label: 'D', text: 'This connection only applies to teams larger than 10 engineers' }
        ],
        correctOptionId: 'b',
        explanation:
          'CI gating merge is the automated half of the same structural-safety-net argument made about PR review in the previous lesson — together they substitute for the peer-oversight capacity a small or solo FDE engagement may lack.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-09-mcq-05',
        question:
          'Based on the lesson\'s framing, for which kind of FDE code is property-based testing most worth its extra setup effort compared to example-based tests alone?',
        options: [
          { id: 'a', label: 'A', text: 'A fixed configuration constant that never changes' },
          { id: 'b', label: 'B', text: 'Code parsing real, messy customer data, where the actual range of production inputs is exactly the kind of thing a human wouldn\'t fully anticipate by hand-writing examples' },
          { id: 'c', label: 'C', text: 'Code with no external inputs of any kind' },
          { id: 'd', label: 'D', text: 'Property-based testing provides equal value for every kind of code, with no meaningful difference in worthwhileness' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson\'s central justification for property-based testing\'s extra effort is specifically about input-parsing code exposed to unpredictable real-world data — exactly the CSV-parsing scenario used to illustrate it.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-09-mcq-06',
        question:
          'What class of bug does a round-trip property test (parse, serialize, re-parse, compare) catch that a simple "doesn\'t crash" property does not?',
        options: [
          { id: 'a', label: 'A', text: 'Round-trip properties and "doesn\'t crash" properties catch exactly the same bugs' },
          { id: 'b', label: 'B', text: 'Silent data corruption or information loss during parsing/serialization — cases where the code runs without error but produces a subtly different result than the original, which a "doesn\'t crash" check would never flag since no exception occurs' },
          { id: 'c', label: 'C', text: 'Round-trip properties can only be used with numeric data types' },
          { id: 'd', label: 'D', text: 'Round-trip properties are strictly a performance optimization, not a correctness check' }
        ],
        correctOptionId: 'b',
        explanation:
          'A "doesn\'t crash" property only guards against exceptions; a round-trip equality check specifically guards against silent correctness bugs where parsing succeeds but subtly loses or alters information — a materially different and often more insidious failure mode.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/10-software-engineering-best-practices-solid-hexagonal-architecture': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-10-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — PORTS AND ADAPTERS IN HEXAGONAL ARCHITECTURE',
        question:
          'In hexagonal architecture, what is the difference between a "port" and an "adapter"?',
        options: [
          { id: 'a', label: 'A', text: 'A port and an adapter are two names for the exact same thing' },
          { id: 'b', label: 'B', text: 'A port is the interface business logic defines for what it needs, with no reference to any specific technology; an adapter is a concrete implementation of that interface against an actual external system' },
          { id: 'c', label: 'C', text: 'A port is always a database, and an adapter is always an API' },
          { id: 'd', label: 'D', text: 'An adapter defines what the logic needs, and a port implements it against a real system' }
        ],
        correctOptionId: 'b',
        explanation:
          'The port is the abstract contract (what operations are needed); the adapter is the concrete implementation of that contract against a specific real system — getting this direction right is what makes the pattern\'s naming meaningful, not arbitrary.',
        incorrectExplanation:
          'Consider where the interface contract is defined versus where the technology-specific implementation lives.',
        hint: 'A port is an abstract protocol defined inside the domain core; an adapter is a concrete implementation that connects external infrastructure to that port.'
      },
      {
        id: 'lesson-fde-fde-foundations-10-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — DEPENDENCY INVERSION UNDER CUSTOMER CONSTRAINTS',
        question:
          'Why does the lesson single out Dependency Inversion as carrying the most practical weight specifically for FDE work?',
        options: [
          { id: 'a', label: 'A', text: 'The other four SOLID principles are irrelevant to any software engineering context' },
          { id: 'b', label: 'B', text: 'FDE scope changes rapidly and unpredictably mid-engagement, and if business logic depends directly on a concrete implementation rather than an abstraction, a change in what\'s available (like real customer system access arriving later) forces a rewrite instead of a swap' },
          { id: 'c', label: 'C', text: 'Dependency Inversion is the only SOLID principle that applies to Python specifically' },
          { id: 'd', label: 'D', text: 'This distinction is arbitrary and has no real justification' }
        ],
        correctOptionId: 'b',
        explanation:
          'The practical argument is specific to FDE\'s rapid-scope-change reality — depending on abstractions is what keeps a later change in the concrete implementation from forcing a rewrite of the logic that depends on it.',
        incorrectExplanation:
          'Think about how delayed customer access and evolving database credentials impact early development velocity without interface boundaries.',
        hint: 'Decoupling business logic from external APIs lets you build, validate, and test against local mocks in week one before customer credentials arrive.'
      }
    ],
    architecture: {
      id: 'lesson-fde-fde-foundations-10-hexagonal-ports-adapters',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — HEXAGONAL ARCHITECTURE (PORTS & ADAPTERS)',
      boundaryLabel: 'CORE DOMAIN & PORT BOUNDARY',
      boundaryText:
        'The ProvisioningService depends solely on the abstract DeviceRepository port. Concrete adapters (SQLite for local dev, Postgres for prod, or Cache decorators) plug in without modifying business logic.',
      nodes: [
        { id: 'driver', label: 'CLI / Webhook Trigger', kind: 'input' },
        { id: 'domain', label: 'ProvisioningService (Core Logic)', kind: 'service' },
        { id: 'boundary', label: 'DeviceRepository Port (Protocol)', kind: 'boundary', highlighted: true },
        { id: 'adapter-sqlite', label: 'SqliteDeviceRepository (Week 1 Dev)', kind: 'adapter' },
        { id: 'adapter-postgres', label: 'PostgresDeviceRepository (Prod)', kind: 'adapter' },
        { id: 'adapter-cache', label: 'CachedDeviceRepository (Decorator)', kind: 'adapter' }
      ]
    },
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-10-mcq-01',
        question:
          'What specifically makes it possible to swap `SqliteDeviceRepository` for `CustomerApiDeviceRepository` without changing the provisioning logic?',
        options: [
          { id: 'a', label: 'A', text: 'SQLite and the customer\'s API happen to have identical underlying data formats' },
          { id: 'b', label: 'B', text: 'The provisioning logic only ever calls methods on the `DeviceRepository` port\'s interface, never referencing SQLite or any storage detail directly, so any adapter satisfying that same interface is interchangeable' },
          { id: 'c', label: 'C', text: 'The provisioning logic contains conditional checks for which storage backend is active' },
          { id: 'd', label: 'D', text: 'Swapping adapters always requires rewriting the business logic; this scenario is unusual' }
        ],
        correctOptionId: 'b',
        explanation:
          'The swap works because the logic was never coupled to any adapter\'s implementation details — it only depends on the port\'s interface, which both adapters satisfy identically from the logic\'s point of view.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-10-mcq-02',
        question:
          'What would have gone wrong in week three if the provisioning logic had called SQLite directly instead of going through a `DeviceRepository` port?',
        options: [
          { id: 'a', label: 'A', text: 'Nothing different would happen; the outcome would be identical either way' },
          { id: 'b', label: 'B', text: 'Every place SQLite calls were sprinkled through the business logic would need to be found and rewritten to call the real customer API instead, turning a one-adapter swap into a risky, scattered rewrite of the logic itself' },
          { id: 'c', label: 'C', text: 'The customer\'s real API would automatically become compatible with the SQLite calls' },
          { id: 'd', label: 'D', text: 'The provisioning tool would stop working entirely with no possible fix' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct cost of skipping the port/adapter boundary — coupling business logic to a concrete implementation means a later swap requires finding and changing every coupled call site instead of writing one new adapter.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-10-mcq-03',
        question:
          'Why was building against a local SQLite mock in week one, before the customer\'s real device database was accessible, a sound decision rather than a risky shortcut?',
        options: [
          { id: 'a', label: 'A', text: 'Because the customer\'s real database was never actually going to be needed' },
          { id: 'b', label: 'B', text: 'Because the hexagonal structure made that decision cheap to reverse later — the mock adapter could be swapped for a real one without touching the already-validated business logic, so building against the mock didn\'t lock in any real risk' },
          { id: 'c', label: 'C', text: 'Because SQLite is technically identical to any production database system' },
          { id: 'd', label: 'D', text: 'Because mocks are always safe regardless of how the code is structured' }
        ],
        correctOptionId: 'b',
        explanation:
          'The soundness of the decision depends entirely on the structure being in place — the same decision without the port/adapter boundary would have been a real risk, since it would have locked business logic to the mock\'s specifics.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-10-mcq-04',
        question:
          'What shared practical outcome do Single Responsibility and Open/Closed both reinforce, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'They guarantee code runs faster at scale' },
          { id: 'b', label: 'B', text: 'Code structured around these principles tolerates rapid, discovery-driven scope change without requiring an increasingly risky rewrite each time the picture changes' },
          { id: 'c', label: 'C', text: 'They eliminate the need for any testing' },
          { id: 'd', label: 'D', text: 'They are only relevant to object-oriented languages, not Python specifically' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson frames all three principles it discusses (SRP, Open/Closed, Dependency Inversion) as reinforcing the same practical outcome — tolerance for the kind of scope change that\'s normal in FDE engagements, not an abstract design purity goal.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-10-mcq-05',
        question:
          'Why does the practice loop specify passing the concrete adapter in via constructor injection, rather than having the provisioning logic import and instantiate `SqliteDeviceRepository` internally?',
        options: [
          { id: 'a', label: 'A', text: 'Constructor injection is required by Python syntax for any class to function' },
          { id: 'b', label: 'B', text: 'Instantiating a concrete adapter internally would re-couple the logic to that specific implementation, defeating the purpose of depending only on the port\'s interface — injection keeps the logic agnostic to which adapter is actually supplied' },
          { id: 'c', label: 'C', text: 'There is no practical difference between the two approaches' },
          { id: 'd', label: 'D', text: 'Internal instantiation is always faster at runtime than injection' }
        ],
        correctOptionId: 'b',
        explanation:
          'If the logic imports and constructs the concrete adapter itself, it\'s coupled to that specific class regardless of the interface existing — injection is what actually keeps the swap possible, echoing the same dependency-injection principle from the Facade pattern discussion in other parts of this platform.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-10-mcq-06',
        question:
          'Why can a `CachedDeviceRepository` wrap another `DeviceRepository` adapter and add caching, without the business logic ever needing to know a cache was introduced?',
        options: [
          { id: 'a', label: 'A', text: 'Caching requires modifying the business logic directly to check a cache before calling the repository' },
          { id: 'b', label: 'B', text: '`CachedDeviceRepository` itself satisfies the same `DeviceRepository` port as any other adapter, so from the logic\'s perspective it\'s just another interchangeable implementation — the fact that it happens to wrap and delegate to a different adapter internally is invisible to the logic' },
          { id: 'c', label: 'C', text: 'This kind of composition is not actually possible in a hexagonal architecture' },
          { id: 'd', label: 'D', text: '`CachedDeviceRepository` must be a subclass of the business logic itself to function' }
        ],
        correctOptionId: 'b',
        explanation:
          'Because the port defines the contract and any adapter satisfying it is interchangeable to the logic, an adapter is free to be implemented however it likes internally — including wrapping and delegating to another adapter — without that internal detail ever surfacing to the business logic depending on the port.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/11-linux-shell-and-scripting-for-fdes': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-11-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — DEFENSIVE BASH SCRIPTING',
        question:
          'What does `set -euo pipefail` do at the top of a bash script?',
        options: [
          { id: 'a', label: 'A', text: 'Makes the script run faster by skipping error checks' },
          { id: 'b', label: 'B', text: 'Exits immediately on any command failure, on any reference to an unset variable, and on a failure anywhere in a pipeline (not just the last command) — preventing the script from silently continuing past a failed step' },
          { id: 'c', label: 'C', text: 'Automatically fixes any errors the script encounters' },
          { id: 'd', label: 'D', text: 'Suppresses all output from the script for cleaner logs' }
        ],
        correctOptionId: 'b',
        explanation:
          'Each flag closes a specific silent-failure gap: `-e` for command failures, `-u` for unset variables, `pipefail` for failures buried in the middle of a pipeline that would otherwise be masked by the last command\'s exit status.',
        incorrectExplanation:
          'Consider what happens in standard bash when an intermediate pipe command fails or when an unset variable evaluates to an empty string.',
        hint: 'It enforces strict error handling: exiting on command failure (`-e`), failing on undefined variables (`-u`), and propagating pipeline errors (`-o pipefail`).'
      },
      {
        id: 'lesson-fde-fde-foundations-11-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — SCRIPTING LANGUAGE SELECTION BOUNDARY',
        question:
          'According to the lesson, which task is a better fit for a quick shell command than for a Python script?',
        options: [
          { id: 'a', label: 'A', text: 'A task involving complex branching logic and structured error handling that will run repeatedly in production' },
          { id: 'b', label: 'B', text: 'A one-off question like "how many lines in this log file contain a specific error code," asked once and not expected to be repeated or maintained' },
          { id: 'c', label: 'C', text: 'Anything that needs unit tests' },
          { id: 'd', label: 'D', text: 'Any task that processes more than 100 lines of input' }
        ],
        correctOptionId: 'b',
        explanation:
          'The judgment line is about repetition, complexity, and cost of a mistake — a genuinely one-off, simple diagnostic question is shell\'s natural territory, while anything with real logic or lasting maintenance need belongs in Python where testing and typing tooling actually applies.',
        incorrectExplanation:
          'Look at where the complexity lies: OS process orchestration vs. structured data parsing and multi-step business logic.',
        hint: 'Shell excels at piping native OS commands and process control; Python is required once complex data structures, JSON parsing, or API calls are involved.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-11-mcq-01',
        question:
          'Why does the lesson describe shell fluency as a baseline requirement rather than a nice-to-have for FDE work?',
        options: [
          { id: 'a', label: 'A', text: 'Shell scripts always run faster than equivalent Python programs' },
          { id: 'b', label: 'B', text: 'An FDE frequently operates on infrastructure they didn\'t set up, often without a full IDE and sometimes without the ability to install new tools, making shell the tool that\'s reliably already available' },
          { id: 'c', label: 'C', text: 'Customers require every FDE to use shell exclusively by contractual policy' },
          { id: 'd', label: 'D', text: 'IDEs are technically incompatible with Linux servers' }
        ],
        correctOptionId: 'b',
        explanation:
          'The justification is about availability and constraint, not raw performance — shell is what\'s reliably present on unfamiliar infrastructure the FDE didn\'t set up and may not be able to modify.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-11-mcq-02',
        question:
          'You need to see the last hour of a specific systemd-managed service\'s log history to look for errors. Which command is the right tool?',
        options: [
          { id: 'a', label: 'A', text: '`ps aux`, since it shows all currently running processes' },
          { id: 'b', label: 'B', text: '`journalctl -u <service> --since "1 hour ago"`, since `journalctl` pulls a service\'s full structured log history filterable by time range' },
          { id: 'c', label: 'C', text: '`systemctl status <service>` alone, since it shows the complete log history with no time limit' },
          { id: 'd', label: 'D', text: '`chmod 777` on the service\'s log directory' }
        ],
        correctOptionId: 'b',
        explanation:
          '`ps` shows current process state, not log history; `systemctl status` shows only a brief recent excerpt, not a full time-ranged query. `journalctl -u` with `--since` is specifically built for pulling filtered log history.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-11-mcq-03',
        question:
          'Why does the lesson single out `chmod 777` as a red flag on a customer\'s production server rather than an acceptable quick fix for a permission error?',
        options: [
          { id: 'a', label: 'A', text: '`chmod 777` is technically invalid syntax on most Linux systems' },
          { id: 'b', label: 'B', text: 'It grants far more access than the actual problem requires, leaving a lasting security gap — the same least-privilege reasoning that applies to agent tool permissions applies to filesystem permissions' },
          { id: 'c', label: 'C', text: 'Permission errors can never actually be fixed with `chmod`' },
          { id: 'd', label: 'D', text: '`chmod 777` only affects files, never directories, making it ineffective for most fixes' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a direct application of least-privilege thinking from earlier security-focused lessons, just applied to filesystem permissions instead of agent tool access — granting maximal access to fix a narrow problem is the anti-pattern being flagged.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-11-mcq-04',
        question:
          'Why did the FDE in the 2am scenario write a defensive multi-step script instead of a single chained `systemctl restart` one-liner?',
        options: [
          { id: 'a', label: 'A', text: '`systemctl restart` is technically incapable of restarting any service' },
          { id: 'b', label: 'B', text: 'One-liners are always slower to execute than multi-step scripts' },
          { id: 'c', label: 'C', text: '' },
          { id: 'd', label: 'D', text: 'The customer\'s server did not support shell scripts of any kind' }
        ],
        correctOptionId: 'a',
        explanation:
          'The risk being managed is a silent partial failure under time pressure — a defensive, explicitly-checked script surfaces a failure at the exact step it occurs rather than masking it inside a chained command.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-11-mcq-05',
        question:
          'Why does the lesson recommend quoting shell variables (`"$variable"`) rather than leaving them bare (`$variable`)?',
        options: [
          { id: 'a', label: 'A', text: 'Quoting is purely a stylistic convention with no functional effect' },
          { id: 'b', label: 'B', text: 'Bare variables are subject to word-splitting and glob-expansion, which can cause surprising bugs when the variable\'s actual value contains spaces or special characters' },
          { id: 'c', label: 'C', text: 'Bare variables are faster to type but always crash the script' },
          { id: 'd', label: 'D', text: 'Quoting is only required for variables holding numeric values' }
        ],
        correctOptionId: 'b',
        explanation:
          'Unquoted variables undergo word-splitting and glob expansion by the shell, which is a real, common source of subtle bugs when a value contains spaces or shell-special characters — quoting prevents this.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-11-mcq-06',
        question:
          'Why does the suggested extension connect adding logging to the restart script back to the "enable" step from the FDE-role lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Logging has no relationship to enablement; the connection is incorrect' },
          { id: 'b', label: 'B', text: 'A script that logs its own actions leaves a clear record for someone else — like the customer\'s own on-call engineer — who runs it later without the FDE present, which is exactly the capability-transfer goal "enable" describes' },
          { id: 'c', label: 'C', text: 'Scripts without logging cannot technically be executed by anyone other than their original author' },
          { id: 'd', label: 'D', text: 'This connection only applies if the script fails' }
        ],
        correctOptionId: 'b',
        explanation:
          'This ties the module\'s very first lesson (enable — transferring capability to the customer\'s own team) to a concrete practice here: a script that logs what it did is legible and safely re-runnable by someone who wasn\'t there when it was written, exactly the enablement goal.'
      }
    ]
  },
  'fde-curriculum/fde-foundations/12-assessment-python-engineering-challenge': {
    conceptChecks: [
      {
        id: 'lesson-fde-fde-foundations-12-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — ARCHITECTURAL EVALUATION CRITERIA',
        question:
          'How does the rubric\'s "structural soundness" category propose checking whether the `LogSource` port is genuinely respected, rather than just nominally present?',
        options: [
          { id: 'a', label: 'A', text: 'Counting the number of lines of code in the `LogSource` interface definition' },
          { id: 'b', label: 'B', text: 'Swapping the in-memory adapter for the file adapter should require zero changes to the summarization logic — if it doesn\'t, implementation details leaked through the supposed abstraction' },
          { id: 'c', label: 'C', text: 'Checking whether the interface is named with the word "Port" in it' },
          { id: 'd', label: 'D', text: 'Structural soundness cannot actually be verified and is a purely subjective judgment' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a concrete, checkable test rather than a subjective judgment — it directly verifies the hexagonal-architecture claim from the earlier lesson: if swapping adapters requires touching the logic, the port wasn\'t actually respected regardless of what the code looks like on the surface.',
        incorrectExplanation:
          'Consider how the rubric checks for clean separation of concerns and interface boundaries rather than just evaluating raw script length.',
        hint: 'By checking that core aggregation and domain models depend only on abstract ports, allowing log sources and sinks to be swapped without modifying business logic.'
      },
      {
        id: 'lesson-fde-fde-foundations-12-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — ROBUST STREAMING ERROR BOUNDARIES',
        question:
          'Per the challenge brief, what should happen when the tool encounters a malformed log line?',
        options: [
          { id: 'a', label: 'A', text: 'The entire tool should stop and exit immediately on the first malformed line' },
          { id: 'b', label: 'B', text: 'The malformed line should be routed to a separate error count, not crash the entire run' },
          { id: 'c', label: 'C', text: 'Malformed lines should be silently discarded with no record of how many were skipped' },
          { id: 'd', label: 'D', text: 'Malformed lines should be automatically corrected and processed as if valid' }
        ],
        correctOptionId: 'b',
        explanation:
          'The brief is explicit: malformed input increments an error count rather than crashing the run or being silently dropped — a design decision that mirrors the earlier lesson\'s Hypothesis property about never raising unhandled exceptions on arbitrary input.',
        incorrectExplanation:
          'Think about how production streaming pipelines maintain resilience when processing noisy, multi-gigabyte customer log exports.',
        hint: 'The analyzer must log a structured warning, record error telemetry, and continue streaming remaining records without aborting the batch.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-12-mcq-01',
        question:
          'What is the actual purpose of this assessment, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Teaching an entirely new Python library not covered elsewhere in the module' },
          { id: 'b', label: 'B', text: 'Confirming that the module\'s individual tools (lazy iteration, validation, logging, hexagonal structure, testing) compose correctly into one coherent deliverable, the way they\'d need to on a real engagement — not testing any single new mechanism' },
          { id: 'c', label: 'C', text: 'Testing typing speed under a strict time limit' },
          { id: 'd', label: 'D', text: 'Determining whether the learner should use Python or a different language going forward' }
        ],
        correctOptionId: 'b',
        explanation:
          'This lesson is explicitly a composition check, not new content — its value is in proving the module\'s separate lessons actually integrate, which is a distinct skill from executing each one in isolation.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-12-mcq-02',
        question:
          'According to the rubric\'s "test quality" criterion, what distinguishes a good property-based test from a weak one that technically satisfies the requirement?',
        options: [
          { id: 'a', label: 'A', text: 'A good property-based test must contain at least 100 lines of code' },
          { id: 'b', label: 'B', text: 'A good property test exercises a meaningful property that would actually catch a real regression if one were introduced, not a trivial always-true assertion that technically runs Hypothesis but proves nothing' },
          { id: 'c', label: 'C', text: 'Any test using the Hypothesis library automatically counts as high quality regardless of what it checks' },
          { id: 'd', label: 'D', text: 'Test quality is measured purely by how long the test suite takes to run' }
        ],
        correctOptionId: 'b',
        explanation:
          'The rubric explicitly guards against gaming the checklist — merely having a Hypothesis test present isn\'t the bar; the test has to actually check something meaningful enough to catch a real regression.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-12-mcq-03',
        question:
          'Why does the practice loop suggest building the `InMemoryLogSource` adapter before the `FileLogSource` adapter?',
        options: [
          { id: 'a', label: 'A', text: 'In-memory adapters are always required to be built before file adapters by Python convention' },
          { id: 'b', label: 'B', text: 'It lets the summarization logic be developed and tested immediately, without any real file-reading code needing to exist yet — the same "build against a lightweight local adapter first" pattern from the hexagonal-architecture lesson' },
          { id: 'c', label: 'C', text: 'File-reading code is technically impossible to write in Python' },
          { id: 'd', label: 'D', text: 'This ordering has no particular rationale; either order works identically' }
        ],
        correctOptionId: 'b',
        explanation:
          'This directly reuses the earlier lesson\'s pattern — building against a fast, simple local adapter first lets the core logic get built and validated before the (often slower or less available) real adapter is ready.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-12-mcq-04',
        question:
          'What does the rubric\'s "operational hygiene" category evaluate?',
        options: [
          { id: 'a', label: 'A', text: 'How many total commits the project has' },
          { id: 'b', label: 'B', text: 'Whether the environment is genuinely reproducible from a clean clone plus the lockfile, whether logs are structured and actually useful to someone else, and whether CI genuinely gates the PR rather than being decorative' },
          { id: 'c', label: 'C', text: 'Whether the code uses tabs or spaces for indentation' },
          { id: 'd', label: 'D', text: 'The total file count in the project directory' }
        ],
        correctOptionId: 'b',
        explanation:
          'Operational hygiene pulls together the toolchain, logging, and CI lessons from earlier in the module into one checkable category — genuinely reproducible, genuinely useful logs, and a CI check that actually blocks a broken PR rather than existing only nominally.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-12-mcq-05',
        question:
          'Why does the lesson argue that skipping a rubric item (e.g. coding directly against file I/O instead of through the `LogSource` port) produces a "noticeably worse, less defensible" result rather than merely a less polished one?',
        options: [
          { id: 'a', label: 'A', text: 'The rubric items are arbitrary stylistic preferences with no functional consequence' },
          { id: 'b', label: 'B', text: 'Each rubric item corresponds to a real capability the deliverable loses without it (e.g. skipping the port means losing the ability to swap adapters or test in isolation) — the gap is functional, not cosmetic' },
          { id: 'c', label: 'C', text: '"Less polished" and "less defensible" mean exactly the same thing in this context' },
          { id: 'd', label: 'D', text: 'Skipping any rubric item makes the code fail to run entirely' }
        ],
        correctOptionId: 'b',
        explanation:
          'The rubric items were chosen because each maps to a real, demonstrated capability from earlier lessons (adapter swapping, catching regressions, reproducibility) — skipping one is a functional loss of that capability, not just a stylistic shortfall.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-fde-foundations-12-mcq-06',
        question:
          'Why does the suggested extension recommend having a peer, or yourself after a day\'s gap, re-score the solution independently against the same rubric?',
        options: [
          { id: 'a', label: 'A', text: 'Independent re-scoring is purely a formality with no diagnostic value' },
          { id: 'b', label: 'B', text: 'A significant disagreement between the original and independent score on any category usually means that rubric criterion was more ambiguous in practice than it seemed while writing the code, which is worth investigating directly' },
          { id: 'c', label: 'C', text: 'A second scoring pass is only useful to catch typos in the code' },
          { id: 'd', label: 'D', text: 'Rubric criteria are never ambiguous, so disagreement always indicates a scoring mistake, never an ambiguous criterion' }
        ],
        correctOptionId: 'b',
        explanation:
          'This echoes the "define success before building" discipline from the problem-discovery lesson — a rubric that produces consistent scores across independent evaluators is doing its job; disagreement is diagnostic of where the rubric (or the solution) was more ambiguous than assumed.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/01-introduction-to-backend-engineering-http-rest-and-api-design': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-01-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — HTTP METHOD SEMANTICS & RETRY SAFETY',
        question:
          'Why is blindly retrying a timed-out POST request more dangerous than retrying a timed-out PUT request?',
        options: [
          { id: 'a', label: 'A', text: 'POST requests are always slower than PUT requests, unrelated to idempotency' },
          { id: 'b', label: 'B', text: 'POST is not idempotent by default, so retrying it can create a duplicate resource; PUT is idempotent, so repeating it produces the same end state without duplication' },
          { id: 'c', label: 'C', text: 'PUT requests cannot be retried under any circumstances' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference between retrying the two' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is exactly the semantic distinction the lesson establishes — idempotency determines whether "just retry" is safe advice, and POST\'s lack of idempotency is why naive retries risk duplicate resource creation.',
        incorrectExplanation:
          'Consider the definition of idempotency and the real-world side effects of executing non-idempotent operations multiple times.',
        hint: 'POST is non-idempotent by default, risking duplicate resource creation, whereas PUT guarantees that repeating the request results in the exact same state.'
      },
      {
        id: 'lesson-fde-backend-observability-data-01-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — HTTP STATUS CODE CONTRACTS',
        question:
          'A client receives a 400 status code from an API. What should a well-behaved client do?',
        options: [
          { id: 'a', label: 'A', text: 'Retry the identical request immediately, since 4xx errors are usually transient' },
          { id: 'b', label: 'B', text: 'Not retry the identical request — a 4xx means the client\'s request itself was wrong, and retrying the same request will fail the same way' },
          { id: 'c', label: 'C', text: 'Retry with exponential backoff, treating it the same as a 5xx error' },
          { id: 'd', label: 'D', text: 'Status codes carry no implication for retry behavior; the client should decide arbitrarily' }
        ],
        correctOptionId: 'b',
        explanation:
          '4xx errors indicate a problem with the request itself, which won\'t be fixed by simply resending the same request — this is the core reason the 4xx/5xx distinction matters for client behavior, not just human debugging.',
        incorrectExplanation:
          'Distinguish between client-side errors (4xx) and transient server-side failures (5xx) when formulating retry policies.',
        hint: '4xx indicates client error (invalid payload or syntax); repeating the same request will deterministically fail without payload correction.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-01-mcq-01',
        question:
          'What is the key difference between a REST-style endpoint (`POST /orders`) and an RPC-style endpoint (`POST /createOrder`) for the same operation?',
        options: [
          { id: 'a', label: 'A', text: 'RPC-style endpoints cannot use the POST method' },
          { id: 'b', label: 'B', text: 'REST organizes the API around resources (nouns) manipulated via standard HTTP methods; RPC-style organizes it around actions (verbs) embedded directly in the URL' },
          { id: 'c', label: 'C', text: 'REST-style endpoints are always faster to execute than RPC-style ones' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference; the two terms describe identical designs' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the defining stylistic distinction — REST\'s resource-and-method structure versus RPC\'s action-in-the-URL structure — independent of performance, which the lesson doesn\'t claim differs between the two.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-01-mcq-02',
        question:
          'What does the lesson say about most production APIs described as "REST" not being fully HATEOAS-compliant?',
        options: [
          { id: 'a', label: 'A', text: 'Any API that isn\'t fully HATEOAS-compliant is not actually usable in production' },
          { id: 'b', label: 'B', text: 'That\'s a reasonable trade-off, since the actual goal — a predictable, consistent contract — is achievable with a pragmatic subset of REST conventions, not strict spec purity' },
          { id: 'c', label: 'C', text: 'HATEOAS compliance is required by the HTTP specification for any resource-oriented API' },
          { id: 'd', label: 'D', text: 'This is always a critical design flaw that must be fixed immediately' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson explicitly frames pragmatic, non-purist REST as fine — what matters is the practical outcome (a predictable, consistent contract), not adherence to the full REST specification.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-01-mcq-03',
        question:
          'Why did fixing the three inconsistent error shapes in the scenario become a breaking change instead of a simple correction?',
        options: [
          { id: 'a', label: 'A', text: 'Error response shapes cannot technically be changed once an API is deployed' },
          { id: 'b', label: 'B', text: 'By the time the inconsistency was noticed, two customer-side integrations were already built against the existing inconsistent shapes, so changing them without warning would break those integrations' },
          { id: 'c', label: 'C', text: 'The customer explicitly requested that the error shapes remain inconsistent' },
          { id: 'd', label: 'D', text: 'JSON responses cannot be restructured after initial deployment for technical reasons' }
        ],
        correctOptionId: 'b',
        explanation:
          'The cost comes from real clients already depending on the existing (inconsistent) shape — this is exactly why the lesson argues these decisions are expensive to retrofit, not because of any technical limitation on changing JSON structure itself.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-01-mcq-04',
        question:
          'What does defining one consistent error-response shape across every endpoint let an API consumer do?',
        options: [
          { id: 'a', label: 'A', text: 'Skip handling errors entirely, since a consistent shape guarantees no errors will occur' },
          { id: 'b', label: 'B', text: 'Write one generic error-handling code path instead of special-casing each endpoint\'s different error format' },
          { id: 'c', label: 'C', text: 'Avoid needing to check HTTP status codes at all' },
          { id: 'd', label: 'D', text: 'Automatically retry every failed request regardless of error type' }
        ],
        correctOptionId: 'b',
        explanation:
          'The whole point of a consistent error envelope is enabling one reusable error-handling path on the consumer side, rather than needing a special case for every endpoint\'s unique response shape.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-01-mcq-05',
        question:
          'DELETE is described as idempotent even though calling it a second time on an already-deleted resource might return a 404 instead of the original 200. Why is this still considered idempotent?',
        options: [
          { id: 'a', label: 'A', text: 'DELETE is not actually idempotent, and this is a misconception the lesson corrects' },
          { id: 'b', label: 'B', text: 'Idempotency is about the resulting state, not the exact response returned — the resource ends up deleted either way, regardless of whether the specific status code differs between the first and second call' },
          { id: 'c', label: 'C', text: 'A 404 response always indicates the operation was not idempotent' },
          { id: 'd', label: 'D', text: 'Idempotency only applies to GET and PUT, never to DELETE' }
        ],
        correctOptionId: 'b',
        explanation:
          'Idempotency is defined by the end state being the same across repeated calls, not by every response being byte-identical — this is a subtlety worth understanding precisely rather than by rote memorization of "DELETE is idempotent."'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-01-mcq-06',
        question:
          'What is the purpose of deciding an API versioning strategy upfront, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Versioning strategies are purely cosmetic and have no functional impact on API consumers' },
          { id: 'b', label: 'B', text: 'So a breaking change to the contract doesn\'t silently break every existing consumer — existing clients can keep using the old version while new clients adopt the updated one' },
          { id: 'c', label: 'C', text: 'Versioning is only relevant for APIs with more than 100 endpoints' },
          { id: 'd', label: 'D', text: 'A versioning strategy prevents any future changes to the API from ever being necessary' }
        ],
        correctOptionId: 'b',
        explanation:
          'Versioning exists specifically to let a breaking change coexist with the old contract for existing consumers, rather than forcing every consumer to update simultaneously or break silently.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/02-fastapi-intro-to-deep-dive': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-02-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — FASTAPI ASYNC DEF VS DEF EXECUTION MODEL',
        question:
          'What is the key operational difference between how FastAPI runs an `async def` handler versus a plain `def` handler?',
        options: [
          { id: 'a', label: 'A', text: '`async def` and `def` handlers are executed identically by FastAPI, with no operational difference' },
          { id: 'b', label: 'B', text: '`def` handlers cannot access request data, only `async def` handlers can' },
          { id: 'c', label: 'C', text: '' },
          { id: 'd', label: 'D', text: '`async def` handlers always run faster regardless of what they contain' }
        ],
        correctOptionId: 'a',
        explanation:
          'This is the direct connection to the earlier concurrency lesson\'s blocking-call danger — FastAPI\'s automatic thread-pool offloading for plain `def` handlers is specifically what protects the event loop from a blocking call that an `async def` handler would expose it to.',
        incorrectExplanation:
          'Consider where FastAPI executes synchronous versus asynchronous handlers to avoid blocking the main event loop.',
        hint: 'FastAPI runs `async def` handlers directly on the event loop thread, while plain `def` handlers are automatically dispatched to an external threadpool.'
      },
      {
        id: 'lesson-fde-backend-observability-data-02-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — DEPENDENCY INJECTION BOUNDARIES',
        question:
          'Why is centralizing an authentication check in one `Depends`-based dependency function better than repeating the same check inline at the top of every route handler?',
        options: [
          { id: 'a', label: 'A', text: 'Dependency functions execute faster than inline code, purely as a performance matter' },
          { id: 'b', label: 'B', text: 'Fixing a bug in the centralized dependency function fixes every route using it at once, instead of requiring the fix to be correctly copy-pasted into every handler that repeated the logic inline' },
          { id: 'c', label: 'C', text: 'FastAPI technically does not allow authentication logic to be written inline in a handler' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference between the two approaches' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a maintainability argument, not a performance one — a single source of truth for shared logic means a fix propagates automatically to every consumer, unlike duplicated inline logic which risks an inconsistent, partial fix.',
        incorrectExplanation:
          'Think about code duplication, testability, and whether security rules should gate execution before or inside business logic.',
        hint: '`Depends` executes before the handler runs, guarantees uniform enforcement, generates accurate OpenAPI security schemes, and simplifies unit testing.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-02-mcq-01',
        question:
          'What two things does a FastAPI route handler\'s type hints simultaneously drive?',
        options: [
          { id: 'a', label: 'A', text: 'Only request validation; OpenAPI docs must be maintained separately by hand' },
          { id: 'b', label: 'B', text: 'Request/response validation at runtime and automatic, always-current OpenAPI schema/docs generation, both derived from the same declaration' },
          { id: 'c', label: 'C', text: 'Only OpenAPI docs generation; request validation must be written manually in each handler' },
          { id: 'd', label: 'D', text: 'Database schema migrations and authentication logic' }
        ],
        correctOptionId: 'b',
        explanation:
          'The core value proposition is that both validation and documentation come from one source of truth (the type hints), which is exactly what prevents the docs from silently drifting out of sync with the actual code.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-02-mcq-02',
        question:
          'According to the lesson, when should a route handler be declared `async def`?',
        options: [
          { id: 'a', label: 'A', text: 'Always, regardless of what I/O the handler performs, since `async def` is universally the more modern choice' },
          { id: 'b', label: 'B', text: 'Only when the handler\'s actual I/O is genuinely async-compatible end to end; if any part makes a blocking, synchronous call with no async alternative, a plain `def` handler is the safer choice' },
          { id: 'c', label: 'C', text: 'Never, since `def` handlers are always preferable in FastAPI' },
          { id: 'd', label: 'D', text: 'Only for handlers that don\'t call any external service at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson explicitly rejects a blanket rule in either direction — the decision depends on whether the handler\'s actual I/O is genuinely async-compatible, not on `async def` being inherently more "correct" or modern.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-02-mcq-03',
        question:
          'Why did the inherited service\'s latency spikes affect completely unrelated endpoints, not just the one making the slow blocking database call?',
        options: [
          { id: 'a', label: 'A', text: 'The database itself was down, affecting all endpoints equally' },
          { id: 'b', label: 'B', text: 'Because the blocking call was inside an `async def` handler, it stalled the entire event loop for the whole worker process, delaying every other concurrent request being handled by that same process regardless of which endpoint they belonged to' },
          { id: 'c', label: 'C', text: 'FastAPI has a global rate limit that throttles all endpoints uniformly' },
          { id: 'd', label: 'D', text: 'This behavior would occur regardless of whether the handler was `async def` or `def`' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the specific, damaging consequence of a blocking call inside `async def` — the stall isn\'t confined to the offending request, it blocks the entire event loop and therefore every concurrent request sharing it.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-02-mcq-04',
        question:
          'Why did the FDE convert only the handlers with blocking calls to `def`, rather than converting every handler in the service to `def` for safety?',
        options: [
          { id: 'a', label: 'A', text: 'FastAPI technically requires at least one handler in a service to be `async def`' },
          { id: 'b', label: 'B', text: 'Handlers whose I/O is genuinely async-compatible get real concurrency benefit from staying `async def`; converting them to `def` unnecessarily would trade away that benefit for no safety gain, since they had no blocking-call problem to begin with' },
          { id: 'c', label: 'C', text: 'Converting all handlers to `def` would have been faster to implement, which was the only consideration' },
          { id: 'd', label: 'D', text: 'There is no real trade-off; converting everything to `def` would have been strictly better' }
        ],
        correctOptionId: 'b',
        explanation:
          'The fix matches each handler\'s declaration to its actual I/O characteristics — blanket-converting everything to `def` would needlessly sacrifice real async concurrency benefits on the handlers that never had a blocking-call problem.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-02-mcq-05',
        question:
          'When a request doesn\'t match a route\'s declared Pydantic request-body shape, at what point does the automatic 422 rejection happen?',
        options: [
          { id: 'a', label: 'A', text: 'After the handler\'s code has already fully executed' },
          { id: 'b', label: 'B', text: 'Before the handler\'s own code ever runs — validation happens at the boundary based on the type hints, and only a request matching the declared shape reaches the handler body' },
          { id: 'c', label: 'C', text: 'Only if the handler explicitly calls a validation function itself' },
          { id: 'd', label: 'D', text: 'FastAPI does not automatically validate request bodies; this must be implemented manually' }
        ],
        correctOptionId: 'b',
        explanation:
          'This mirrors the "parse, don\'t validate" boundary from the Pydantic lesson — the validation boundary sits before the handler\'s own logic, so the handler can trust the shape of whatever it receives.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-02-mcq-06',
        question:
          'A new `require_role("admin")` dependency depends on the existing `get_current_user` dependency. What does this composition achieve?',
        options: [
          { id: 'a', label: 'A', text: '`require_role` replaces the need for `get_current_user` entirely, making the original dependency obsolete' },
          { id: 'b', label: 'B', text: 'A more specific, reusable authorization check (role verification) is built on top of the existing identity-lookup logic without duplicating that logic — both dependencies stay independently correct and composable' },
          { id: 'c', label: 'C', text: 'Dependencies in FastAPI cannot depend on other dependencies; this composition is not actually possible' },
          { id: 'd', label: 'D', text: 'This composition requires rewriting `get_current_user` to be role-aware internally' }
        ],
        correctOptionId: 'b',
        explanation:
          'Dependency chains letting a more specific check build on a more general one without duplicating logic is exactly the compositional benefit `Depends` provides — each piece of logic stays in one place and gets reused rather than re-implemented.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/03-auth-oauth2-jwt-oidc-and-rbac': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-03-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — JWT INTEGRITY VS CONFIDENTIALITY',
        question:
          'Is a JWT\'s payload readable by anyone who has the token, or is it encrypted and hidden by default?',
        options: [
          { id: 'a', label: 'A', text: 'Fully encrypted and unreadable without the correct private key' },
          { id: 'b', label: 'B', text: 'Readable by anyone holding the token — a JWT is signed, not encrypted by default, so its payload is just base64url-encoded plain text' },
          { id: 'c', label: 'C', text: 'Readable only by the server that issued it, never by the client holding it' },
          { id: 'd', label: 'D', text: 'JWTs do not have a payload at all, only a signature' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the single most commonly misunderstood JWT detail the lesson calls out directly — the signature proves integrity, not confidentiality, so nothing in the payload should be treated as hidden.',
        incorrectExplanation:
          'Distinguish between cryptographic signing (tamper-detection) and encryption (confidentiality).',
        hint: 'Standard JWTs are Base64URL-encoded and cryptographically signed for integrity, but their payload claims are visible in plaintext to anyone holding the token.'
      },
      {
        id: 'lesson-fde-backend-observability-data-03-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — STATELESS TOKEN REVOCATION TRADE-OFFS',
        question:
          'Why are JWTs inherently hard to revoke before their stated expiry?',
        options: [
          { id: 'a', label: 'A', text: 'JWTs cannot technically have an expiry field at all' },
          { id: 'b', label: 'B', text: 'JWTs are typically stateless and self-contained — a server verifying a JWT\'s signature doesn\'t need to check a central store, so there\'s no built-in mechanism to mark one invalid before its expiry without adding that lookup back in' },
          { id: 'c', label: 'C', text: 'JWTs are always valid forever regardless of any expiry claim' },
          { id: 'd', label: 'D', text: 'Revocation is trivial and requires no special handling for JWTs' }
        ],
        correctOptionId: 'b',
        explanation:
          'Statelessness is precisely what makes JWTs efficient (no database lookup needed to verify) and what makes revocation hard (there\'s no central state to update to invalidate one early) — a genuine trade-off, not an oversight.',
        incorrectExplanation:
          'Consider the architectural trade-off of stateless token verification: zero database lookups per request means no central revocation check.',
        hint: 'Resource servers validate JWT signatures locally using public keys without querying a centralized database, so they cannot know if a token was revoked early.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-03-mcq-01',
        question:
          'What is the difference between authentication and authorization?',
        options: [
          { id: 'a', label: 'A', text: 'They are two names for the exact same concept' },
          { id: 'b', label: 'B', text: 'Authentication answers "who is this"; authorization answers "what is this identity allowed to do"' },
          { id: 'c', label: 'C', text: 'Authentication concerns permissions; authorization concerns identity verification' },
          { id: 'd', label: 'D', text: 'Authorization always happens before authentication in any system' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the foundational distinction the lesson establishes before layering OAuth2, OIDC, JWT, and RBAC on top of it — each of those mechanisms addresses one or the other, not both interchangeably.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-03-mcq-02',
        question:
          'What does a bare OAuth2 access token NOT reliably tell you, which is why OIDC exists?',
        options: [
          { id: 'a', label: 'A', text: 'Whether the client has any access at all' },
          { id: 'b', label: 'B', text: 'A verified identity claim about who the user actually is — OAuth2 proves a scoped grant exists, not a standardized answer to "who"' },
          { id: 'c', label: 'C', text: 'What scope of access was granted' },
          { id: 'd', label: 'D', text: 'OAuth2 access tokens provide identical information to OIDC ID tokens, making OIDC redundant' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the exact gap OIDC\'s ID token closes — OAuth2 is a delegation/authorization framework, and identity was never its core job, which is why conflating an access token with proof of identity is a real, consequential mistake.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-03-mcq-03',
        question:
          'What was the actual vulnerability in the scenario\'s early authorization middleware?',
        options: [
          { id: 'a', label: 'A', text: 'The middleware used OIDC instead of plain OAuth2, which was itself the vulnerability' },
          { id: 'b', label: 'B', text: 'It decoded and trusted the JWT\'s `role` claim without first verifying the token\'s cryptographic signature against the identity provider\'s public key, so any editable JSON blob shaped like a JWT could claim `role: admin`' },
          { id: 'c', label: 'C', text: 'The JWT\'s payload was encrypted, preventing the middleware from reading the role claim at all' },
          { id: 'd', label: 'D', text: 'The vulnerability had nothing to do with signature verification and was purely a network configuration issue' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct, concrete consequence of the "signed, not encrypted" property combined with skipped verification — the fix is mandatory signature verification before any claim is trusted, which the scenario\'s remediation implements.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-03-mcq-04',
        question:
          'Why does the lesson recommend re-verifying a user\'s role against a source of truth for high-stakes actions, rather than trusting the role claim embedded in an already-signature-verified token?',
        options: [
          { id: 'a', label: 'A', text: 'Signature-verified tokens can never be trusted for any purpose whatsoever' },
          { id: 'b', label: 'B', text: 'A user\'s role could change (e.g. be demoted from admin) after a token was issued but before it expires; trusting the token\'s claim alone means that change wouldn\'t take effect until the token naturally expires, which is an acceptable risk for low-stakes actions but not high-stakes ones' },
          { id: 'c', label: 'C', text: 'Re-verifying against a source of truth is required for every single request regardless of stakes, with no exceptions' },
          { id: 'd', label: 'D', text: 'This recommendation applies only to OAuth2 access tokens, never to OIDC ID tokens' }
        ],
        correctOptionId: 'b',
        explanation:
          'Even a properly signature-verified token can carry a claim that\'s gone stale since issuance — the lesson\'s judgment call is to bound that risk window for high-stakes actions specifically, not to distrust signature verification itself.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-03-mcq-05',
        question:
          'A backend service needs to authenticate directly to another backend service with no user involved at all. Which OAuth2 grant type fits this case?',
        options: [
          { id: 'a', label: 'A', text: 'Authorization code flow, since it\'s the correct grant type for every scenario' },
          { id: 'b', label: 'B', text: 'Client credentials flow, since it\'s designed for service-to-service authentication with no user in the loop' },
          { id: 'c', label: 'C', text: 'Neither flow supports service-to-service communication' },
          { id: 'd', label: 'D', text: 'OIDC ID tokens are required for any service-to-service authentication' }
        ],
        correctOptionId: 'b',
        explanation:
          'Authorization code flow is specifically for user-facing applications where a real user approves access; client credentials flow is the fit when no user is involved, exactly this service-to-service case.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-03-mcq-06',
        question:
          'Why does the lesson describe short-lived access tokens paired with refresh tokens as a "practical mitigation" for the revocation problem rather than a full solution?',
        options: [
          { id: 'a', label: 'A', text: 'Short-lived tokens completely eliminate any risk of token compromise' },
          { id: 'b', label: 'B', text: 'A compromised access token is still valid and usable for the remainder of its (short) lifetime — the mitigation bounds the exposure window rather than eliminating it, since there\'s still no real-time way to invalidate an already-issued access token early' },
          { id: 'c', label: 'C', text: 'Refresh tokens are themselves encrypted, which solves the revocation problem entirely' },
          { id: 'd', label: 'D', text: 'This is not actually a mitigation; short-lived tokens have no bearing on revocation risk' }
        ],
        correctOptionId: 'b',
        explanation:
          'The word "mitigation" is precise here — bounding the exposure window reduces the practical risk without providing a true real-time revocation mechanism for an already-issued token, which is the honest limitation the lesson wants understood, not glossed over.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-03-mcq-07',
        question:
          'What does refresh-token rotation (issuing a new refresh token and invalidating the old one on every use) specifically defend against that a long-lived, non-rotating refresh token would not?',
        options: [
          { id: 'a', label: 'A', text: 'Rotation prevents access tokens from ever expiring' },
          { id: 'b', label: 'B', text: 'If a refresh token is stolen and used by an attacker, rotation means the legitimate holder\'s next use of what they believe is still their valid refresh token will fail (since it was already rotated/invalidated), surfacing the compromise, rather than both the attacker and the legitimate user silently sharing the same long-lived token indefinitely' },
          { id: 'c', label: 'C', text: 'Rotation eliminates the need for signature verification on access tokens' },
          { id: 'd', label: 'D', text: 'Rotation has no defensive purpose and is purely a performance optimization' }
        ],
        correctOptionId: 'b',
        explanation:
          'Rotation creates a detectable signal on theft — reuse of an already-rotated (invalidated) refresh token is a clear compromise indicator, something a static, non-rotating refresh token provides no way to detect.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/04-building-an-order-management-module-and-its-api': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-04-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — FINITE STATE MACHINE INTEGRITY',
        question:
          'Why is a free-text or loosely-typed `status` field, relying on "the UI just doesn\'t offer that button," an insufficient guarantee against invalid state transitions?',
        options: [
          { id: 'a', label: 'A', text: 'Free-text fields are technically impossible to store in a database' },
          { id: 'b', label: 'B', text: 'Any other client able to call the API directly — an admin tool, a script, a bug — bypasses whatever the UI happens to offer, so the guarantee has to be enforced in the API/logic itself, not merely in what buttons a UI presents' },
          { id: 'c', label: 'C', text: 'UI-level restrictions are always sufficient and this concern doesn\'t apply in practice' },
          { id: 'd', label: 'D', text: 'This concern only applies to publicly accessible APIs, never to internal tools' }
        ],
        correctOptionId: 'b',
        explanation:
          'Any real guarantee has to be enforced server-side, since a UI restriction is trivially bypassed by anything else that can call the same API — internal tools and bugs included.',
        incorrectExplanation:
          'Consider what happens when API requests bypass frontend forms and write arbitrary strings directly into database records.',
        hint: 'Direct API callers or concurrent requests can bypass the UI, writing invalid state jumps (e.g. `cancelled` to `shipped`) and corrupting downstream workflows.'
      },
      {
        id: 'lesson-fde-backend-observability-data-04-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — EXPLICIT STATE TRANSITION ENDPOINTS',
        question:
          'Why does the fixed design use `PATCH /orders/{id}/status` with a `target_status` field, instead of a generic `PATCH /orders/{id}` that happens to accept a status field among others?',
        options: [
          { id: 'a', label: 'A', text: 'FastAPI technically does not support PATCH requests on a resource\'s root path' },
          { id: 'b', label: 'B', text: 'The dedicated endpoint signals in the API surface itself that status changes are a distinct, specially-validated operation, rather than an arbitrary field update that might not receive the same transition validation as other fields' },
          { id: 'c', label: 'C', text: 'There is no meaningful design difference between the two approaches' },
          { id: 'd', label: 'D', text: 'The dedicated endpoint is required because HTTP forbids nested resource paths' }
        ],
        correctOptionId: 'b',
        explanation:
          'A dedicated endpoint for a specially-validated operation makes the contract self-documenting about which fields get transition-validation treatment, rather than burying that distinction inside a generic update handler.',
        incorrectExplanation:
          'Think about how finite state transitions require distinct authorization, validation, and side effects compared to updating a shipping address.',
        hint: 'Dedicated transition endpoints enforce state machine business rules, audit log creation, and role-based transition permissions at the backend boundary.'
      }
    ],
    architecture: {
      id: 'lesson-fde-backend-observability-data-04-order-state-machine',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — ORDER MANAGEMENT STATE MACHINE',
      boundaryLabel: 'ORDER FINITE STATE MACHINE BOUNDARY',
      boundaryText:
        'Orders transition through strict, validated state boundaries. Invalid jumps (e.g. CANCELLED -> SHIPPED) are rejected by the domain state validator.',
      nodes: [
        { id: 'created', label: 'Order Created', kind: 'input' },
        { id: 'pending', label: 'PENDING', kind: 'service' },
        { id: 'boundary', label: 'State Transition Validator', kind: 'boundary', highlighted: true },
        { id: 'paid', label: 'PAID', kind: 'service' },
        { id: 'shipped', label: 'SHIPPED', kind: 'service' },
        { id: 'delivered', label: 'DELIVERED (Terminal)', kind: 'output' },
        { id: 'cancelled', label: 'CANCELLED (Terminal)', kind: 'output' },
        { id: 'refunded', label: 'REFUNDED (Terminal)', kind: 'output' }
      ]
    },
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-04-mcq-01',
        question:
          'Why does the order module define an `OrderRepository` port rather than having the business logic call the database directly?',
        options: [
          { id: 'a', label: 'A', text: 'Ports are a FastAPI-specific requirement with no relation to earlier lessons in this course' },
          { id: 'b', label: 'B', text: 'It reuses the hexagonal architecture pattern from the earlier SOLID lesson — business logic depends on the port\'s interface, letting the concrete storage adapter (Postgres, an in-memory store during development) be swapped without touching the logic' },
          { id: 'c', label: 'C', text: 'Calling the database directly is technically impossible in Python' },
          { id: 'd', label: 'D', text: 'The `OrderRepository` port exists purely to satisfy a naming convention with no functional purpose' }
        ],
        correctOptionId: 'b',
        explanation:
          'This module is explicitly framed as composing earlier lessons — the port/adapter structure is the same pattern from the hexagonal-architecture lesson, applied here to a real customer-facing module instead of the earlier illustrative example.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-04-mcq-02',
        question:
          'An order in the `completed` state receives a request to transition to `created`. According to the fixed design, what should happen?',
        options: [
          { id: 'a', label: 'A', text: 'The transition is silently applied since the API accepts any valid enum value for status' },
          { id: 'b', label: 'B', text: 'The request is rejected with a specific, clear error explaining the invalid transition, following the same consistent error-envelope shape from the REST lesson — not silently accepted and not a generic, unhelpful error' },
          { id: 'c', label: 'C', text: 'The server crashes with an unhandled exception' },
          { id: 'd', label: 'D', text: 'The request succeeds but does nothing, with no indication to the caller that anything went wrong' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct fix described in the scenario — an explicit, specific rejection using the established error-envelope pattern, not a silent no-op, a crash, or a generic unhelpful message.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-04-mcq-03',
        question:
          'Why might a customer-facing user be allowed to cancel their own pending order, but only an internal role be allowed to mark an order as fulfilled?',
        options: [
          { id: 'a', label: 'A', text: 'FastAPI technically requires every endpoint to have identical role requirements' },
          { id: 'b', label: 'B', text: 'Different transitions carry different stakes and different appropriate actors — cancelling your own order is a low-stakes, self-directed action, while marking fulfillment is an operational action that should reflect actual warehouse/shipping state, not a customer\'s self-report' },
          { id: 'c', label: 'C', text: 'RBAC only applies to read operations, never to state-changing operations like transitions' },
          { id: 'd', label: 'D', text: 'There is no legitimate reason to differentiate; every transition should be equally accessible to all authenticated users' }
        ],
        correctOptionId: 'b',
        explanation:
          'This connects directly to the RBAC lesson\'s judgment about matching authorization strictness to the stakes and appropriate actor for a given action, applied concretely to order-state transitions.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-04-mcq-04',
        question:
          'Why did the original unvalidated `PATCH /orders/{id}` endpoint corrupt downstream reporting specifically, beyond just being a data-integrity concern in the abstract?',
        options: [
          { id: 'a', label: 'A', text: 'The reporting system was entirely unrelated to the order module and this was a coincidence' },
          { id: 'b', label: 'B', text: 'The downstream reporting logic assumed `completed` orders were immutable/terminal, and the unvalidated endpoint let a `completed` order be silently reverted to `created`, violating that assumption in a way the reporting code had no way to detect or guard against' },
          { id: 'c', label: 'C', text: 'Reporting bugs are always caused by database performance issues, not data-integrity violations' },
          { id: 'd', label: 'D', text: 'This consequence would have occurred regardless of whether transition validation existed' }
        ],
        correctOptionId: 'b',
        explanation:
          'This shows the real cost of a missing invariant — other parts of the system built on the (previously reasonable) assumption that `completed` is terminal, and violating that assumption silently, without any enforced guarantee, is what caused the downstream corruption.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-04-mcq-05',
        question:
          'Why does the practice loop specify testing at least one valid AND one invalid transition for every state, rather than just testing that a few example transitions work correctly?',
        options: [
          { id: 'a', label: 'A', text: 'Testing invalid transitions is unnecessary; only valid-path tests provide any real value' },
          { id: 'b', label: 'B', text: 'Testing only valid transitions would never actually verify that the rejection logic works at all — the invalid-transition tests are what confirm the allowed-transitions map genuinely blocks disallowed changes, not just that some transitions happen to succeed' },
          { id: 'c', label: 'C', text: 'This requirement exists purely to increase the total test count for its own sake' },
          { id: 'd', label: 'D', text: 'Invalid-transition tests are only useful for the `completed` state specifically, not other states' }
        ],
        correctOptionId: 'b',
        explanation:
          'Testing rejection behavior is what actually validates the guard exists and works — a test suite covering only the happy path would pass even if the rejection logic were completely missing.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-04-mcq-06',
        question:
          'The suggested extension asks whether order-transition history should be a structured log event, a database table, or both. What consideration from the lesson should drive that choice?',
        options: [
          { id: 'a', label: 'A', text: 'Structured logs and database tables are functionally identical, so the choice doesn\'t matter' },
          { id: 'b', label: 'B', text: 'Whether the history needs to be queried later as part of normal application functionality (favoring a database table, queryable by the app) versus being purely for audit/debugging purposes (favoring structured logs, per the earlier logging lesson) — the two aren\'t mutually exclusive if both needs exist' },
          { id: 'c', label: 'C', text: 'Order history must always be stored exclusively as structured logs, never in a database table' },
          { id: 'd', label: 'D', text: 'The choice should be based solely on which option requires writing less code' }
        ],
        correctOptionId: 'b',
        explanation:
          'This connects back to the structured-logging lesson\'s framing — logs and queryable application data serve different purposes, and the right choice (possibly both) depends on how the history will actually be used, not a default preference for one over the other.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/05-building-payments-and-notifications-stripe-celery': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-05-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — PAYMENT STATE ASYMMETRY',
        question:
          'Why is a frontend\'s claim that "payment succeeded" never treated as the source of truth for whether a payment actually happened?',
        options: [
          { id: 'a', label: 'A', text: 'Frontends are technically incapable of making HTTP requests to a backend' },
          { id: 'b', label: 'B', text: 'A client can be wrong, manipulated, or simply lose connection right after a real charge succeeds — only Stripe\'s own signed webhook event reliably reflects the actual payment status' },
          { id: 'c', label: 'C', text: 'Client claims are always intentionally malicious' },
          { id: 'd', label: 'D', text: 'This is a stylistic preference with no real security or correctness implication' }
        ],
        correctOptionId: 'b',
        explanation:
          'The concern isn\'t necessarily malice — a client can simply be wrong or lose connectivity at the wrong moment — which is exactly why the authoritative source has to be the payment processor\'s own verified event, not anything the client reports.',
        incorrectExplanation:
          'Consider the security perimeter: client browsers are untrusted; only cryptographically signed provider webhooks confirm real funds capture.',
        hint: 'Frontend code runs in an untrusted client environment where network calls can be intercepted, spoofed, or replayed; only server-side signed webhooks prove payment settlement.'
      },
      {
        id: 'lesson-fde-backend-observability-data-05-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — WEBHOOK AT-LEAST-ONCE DELIVERY',
        question:
          'Why must a webhook handler be idempotent, given that Stripe doesn\'t guarantee exactly-once delivery?',
        options: [
          { id: 'a', label: 'A', text: 'Idempotency has nothing to do with delivery guarantees; it\'s purely a performance concern' },
          { id: 'b', label: 'B', text: 'The same event can be delivered more than once (due to network retries or a slow acknowledgment), so a non-idempotent handler risks double-executing side effects like fulfilling an order or sending a notification twice' },
          { id: 'c', label: 'C', text: 'Stripe technically only ever sends each event exactly once, making this concern purely theoretical' },
          { id: 'd', label: 'D', text: 'Idempotent handlers run faster than non-idempotent ones, which is the primary reason for the requirement' }
        ],
        correctOptionId: 'b',
        explanation:
          'The at-least-once delivery guarantee (not exactly-once) is exactly what makes idempotency a correctness requirement, not an optimization — without it, a legitimate retry looks identical to a duplicate processing risk.',
        incorrectExplanation:
          'Think about what happens when network timeouts cause Stripe to retry a payment_intent.succeeded event.',
        hint: 'Payment providers like Stripe guarantee at-least-once delivery, frequently re-sending identical event payloads if network latency delays response acknowledgments.'
      }
    ],
    architecture: {
      id: 'lesson-fde-backend-observability-data-05-payments-celery-pipeline',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — ASYNC WEBHOOK & CELERY NOTIFICATION PIPELINE',
      boundaryLabel: 'FAST WEBHOOK ACKNOWLEDGMENT BOUNDARY',
      boundaryText:
        'The webhook handler validates Stripe signatures and records idempotency state in < 10ms, enqueuing notification jobs to Celery workers to prevent Stripe retry storms.',
      nodes: [
        { id: 'stripe', label: 'Stripe Webhook Event', kind: 'input' },
        { id: 'handler', label: 'FastAPI Webhook Handler', kind: 'service' },
        { id: 'boundary', label: 'Signature & Idempotency Gate', kind: 'boundary', highlighted: true },
        { id: 'db', label: 'Order DB (State: PAID)', kind: 'service' },
        { id: 'redis', label: 'Redis / Celery Message Broker', kind: 'adapter' },
        { id: 'worker', label: 'Celery Notification Worker', kind: 'adapter' },
        { id: 'email', label: 'Customer Confirmation Email', kind: 'output' }
      ]
    },
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-05-mcq-01',
        question:
          'The lesson connects webhook signature verification to two earlier examples in the course. What is the shared underlying principle across all three?',
        options: [
          { id: 'a', label: 'A', text: 'All three examples are about database performance optimization' },
          { id: 'b', label: 'B', text: 'Something claims to be authoritative (a prompt\'s embedded instructions, a JWT\'s claims, a webhook\'s payload), and only a verifiable signature or deterministic check — not the mere presence of the claim — actually proves it\'s legitimate' },
          { id: 'c', label: 'C', text: 'The three examples are unrelated and the connection is coincidental' },
          { id: 'd', label: 'D', text: 'The shared principle is that all external data should be encrypted, not verified' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the explicit cross-lesson thread the course draws — prompt injection defenses, JWT signature verification, and webhook verification are all instances of the same "verify before trusting a claim" discipline in different technical contexts.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-05-mcq-02',
        question:
          'What was the actual chain of events that caused the confirmation email to be sent twice in the scenario?',
        options: [
          { id: 'a', label: 'A', text: 'The email provider itself sent duplicate emails due to an internal bug, unrelated to the webhook handler\'s design' },
          { id: 'b', label: 'B', text: 'A slow email send inside the webhook handler caused a timeout, Stripe retried the webhook delivery believing it hadn\'t been acknowledged, and because the handler wasn\'t idempotent, it reprocessed the already-successful payment and sent a second email' },
          { id: 'c', label: 'C', text: 'The customer accidentally submitted the payment form twice' },
          { id: 'd', label: 'D', text: 'Stripe\'s webhook system has a known bug that always delivers every event exactly twice' }
        ],
        correctOptionId: 'b',
        explanation:
          'This traces the full causal chain — the slow synchronous email send was the trigger for the timeout, and the missing idempotency check was what let the resulting retry cause a real duplicate side effect.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-05-mcq-03',
        question:
          'What does moving notification-sending into a Celery task decouple from the payment-confirmation webhook handler\'s response time?',
        options: [
          { id: 'a', label: 'A', text: 'The Celery task decouples the webhook handler from Stripe\'s signature verification requirement' },
          { id: 'b', label: 'B', text: 'The reliability and speed of a slow, external, occasionally-failing third-party service (the email provider) — the webhook handler no longer has to wait on it to return a response' },
          { id: 'c', label: 'C', text: 'Celery removes the need for idempotent webhook handling entirely' },
          { id: 'd', label: 'D', text: 'There is no meaningful decoupling; Celery only changes which process executes the code' }
        ],
        correctOptionId: 'b',
        explanation:
          'The core benefit is separating the payment-confirmation critical path (which should be fast and reliable) from an unrelated, slower, less reliable side effect — not eliminating any other concern like signature verification or idempotency, which remain necessary regardless.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-05-mcq-04',
        question:
          'Why did moving notification-sending into a Celery task also indirectly fix the webhook-handler timeout problem, not just the double-send problem?',
        options: [
          { id: 'a', label: 'A', text: 'Celery tasks are technically incapable of failing, unlike inline code' },
          { id: 'b', label: 'B', text: 'With the slow email send removed from the webhook handler\'s critical path, the handler itself returns quickly regardless of the email provider\'s speed that day, which means it stops timing out and Stripe stops retrying it in the first place — removing the retry trigger removes the opportunity for a duplicate to occur at all' },
          { id: 'c', label: 'C', text: 'The two problems were entirely unrelated, and fixing one had no effect on the other' },
          { id: 'd', label: 'D', text: 'Idempotency alone would have been sufficient without also queuing the notification' }
        ],
        correctOptionId: 'b',
        explanation:
          'The two problems were causally linked — the slow inline email send was the root trigger for the timeout-and-retry cycle, so removing it from the critical path addresses the trigger itself, on top of idempotency handling any retries that do still occur for other reasons.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-05-mcq-05',
        question:
          'How does the lesson connect a Celery task\'s retry-with-backoff behavior to the earlier closures/decorators lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Celery tasks and Python decorators are unrelated technologies with no conceptual overlap' },
          { id: 'b', label: 'B', text: 'It\'s conceptually the same idea as the `@retry` decorator from that lesson — automatically retrying a transient failure — just operating at the infrastructure level across process/worker boundaries instead of within a single in-process function call' },
          { id: 'c', label: 'C', text: 'Celery tasks technically use the exact same `@retry` decorator code from the earlier lesson with no modification' },
          { id: 'd', label: 'D', text: 'This connection only applies if the Celery task itself is decorated with `@retry` explicitly, which is required syntax' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson draws a conceptual parallel, not a literal code reuse — the same "automatically retry a transient failure" idea shows up at two different levels of the system, in-process versus across a distributed task queue.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-05-mcq-06',
        question:
          'The suggested extension asks what should happen if a `payment_succeeded` event arrives after a `payment_failed` event for the same order was already processed. Given the order-management lesson\'s state machine, what determines the correct behavior?',
        options: [
          { id: 'a', label: 'A', text: 'This situation is impossible and requires no handling of any kind' },
          { id: 'b', label: 'B', text: 'Whether the allowed-transitions map permits a transition from `payment_failed` to `payment_succeeded`/`paid` — if it doesn\'t, the later event should be rejected by the same transition-validation logic already in place, exactly as any other invalid transition would be, rather than requiring new special-case code' },
          { id: 'c', label: 'C', text: 'The most recently received event should always simply overwrite the current state with no validation' },
          { id: 'd', label: 'D', text: 'This scenario has no connection to the order-management lesson\'s state machine' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the payoff of the earlier investment in explicit transition validation — an out-of-order or conflicting webhook event is just another attempted transition, and the existing allowed-transitions map already provides the mechanism to accept or reject it correctly without new bespoke logic.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/06-building-the-demo-frontend': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-06-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — REAL BACKEND WIRED PROTOTYPING',
        question:
          'Why does the lesson insist the demo frontend call the real API rather than a mocked or hand-simulated version of it?',
        options: [
          { id: 'a', label: 'A', text: 'Mocked APIs are technically incompatible with `fetch` calls' },
          { id: 'b', label: 'B', text: 'A demo that fakes its responses to always show success isn\'t actually proving the backend does what it claims — it\'s the same "verify, don\'t trust presented data" discipline applied to the demo\'s own integrity' },
          { id: 'c', label: 'C', text: 'Real APIs are always faster to call than mocked ones, which is the only consideration' },
          { id: 'd', label: 'D', text: 'This distinction doesn\'t actually matter for a demo\'s effectiveness' }
        ],
        correctOptionId: 'b',
        explanation:
          'This connects the "verify, don\'t trust" theme from earlier lessons to the demo\'s own credibility — a mocked demo proves nothing about whether the real system actually works.',
        incorrectExplanation:
          'Consider the difference between demoing a UI skin versus validating end-to-end system integration.',
        hint: 'Mocks disguise real API latency, authentication gaps, and payload shape mismatches; calling the live backend provides authentic validation.'
      },
      {
        id: 'lesson-fde-backend-observability-data-06-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — DEMONSTRATING ERROR BOUNDARIES',
        question:
          'Why did the FDE in the scenario deliberately trigger an invalid order transition during the live demo, instead of only showing a smooth, sequential happy path?',
        options: [
          { id: 'a', label: 'A', text: 'Invalid transitions are technically required to occur during every demo by convention' },
          { id: 'b', label: 'B', text: 'Showing a real failure handled gracefully is more persuasive evidence of production-readiness than a flawless run, because it demonstrates the system was built to handle the cases that matter, not just one rehearsed path' },
          { id: 'c', label: 'C', text: 'This was a mistake that happened to work out, not a deliberate choice' },
          { id: 'd', label: 'D', text: 'Showing error states has no effect on customer trust either way' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a deliberate credibility choice — proving the system handles failure correctly builds more trust than a curated success-only demo, which risks looking staged.',
        incorrectExplanation:
          'Think about how customer trust is built by demonstrating resilience and clear error handling rather than only showing happy paths.',
        hint: 'Demonstrating graceful rejection of illegal actions proves that backend state machine guards and validation boundaries are functioning reliably.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-06-mcq-01',
        question:
          'What is the demo frontend\'s primary job, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Being visually indistinguishable from a finished production application' },
          { id: 'b', label: 'B', text: 'Proving the real backend contract works end to end, in front of a customer, with real requests and responses — not being a polished, complete product UI' },
          { id: 'c', label: 'C', text: 'Replacing the need for the actual backend API entirely' },
          { id: 'd', label: 'D', text: 'Demonstrating the FDE\'s frontend framework expertise' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson is explicit that polish is not the goal here — proving real backend behavior is, which is why a minimal HTML-plus-fetch client is a legitimate, deliberate choice rather than a shortcut.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-06-mcq-02',
        question:
          'Why does the lesson argue against building a polished, production-grade frontend before the backend contract has been validated with the customer?',
        options: [
          { id: 'a', label: 'A', text: 'Production-grade frontends are technically impossible to build before a backend exists' },
          { id: 'b', label: 'B', text: 'The contract might still change based on what the customer actually needs, discovered only once they see it working — investing significant UI-polish time before that validation risks wasted effort if the contract shifts' },
          { id: 'c', label: 'C', text: 'Customers never want to see a polished frontend under any circumstances' },
          { id: 'd', label: 'D', text: 'This has no relationship to the discover-before-build principle from earlier lessons' }
        ],
        correctOptionId: 'b',
        explanation:
          'This connects directly to the discover-prototype-validate discipline from the FDE-role lesson — validating the contract cheaply before investing in polish avoids wasted work on a contract that might still need to change.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-06-mcq-03',
        question:
          'What is the specific risk of hardcoding a "success" response in the frontend to make a demo look smoother under time pressure?',
        options: [
          { id: 'a', label: 'A', text: 'Hardcoded responses are technically slower to render than real API responses' },
          { id: 'b', label: 'B', text: 'A system that only ever shows success in its own demo erodes trust the moment reality diverges from the demo, which it eventually will — and it means the demo never actually proved the backend does what it claims' },
          { id: 'c', label: 'C', text: 'There is no real risk; hardcoding a success response is an acceptable practice for any demo' },
          { id: 'd', label: 'D', text: 'This risk only applies to payment-related demos, not other kinds of demos' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct consequence of skipping the "call the real API" principle — the demo becomes disconnected from reality, and that gap surfaces eventually, at a worse moment than during a controlled demo.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-06-mcq-04',
        question:
          'Where does this lesson say its scope ends, relative to the later Full-Stack FDE module?',
        options: [
          { id: 'a', label: 'A', text: 'This lesson fully covers everything the Full-Stack FDE module will teach, making that module redundant' },
          { id: 'b', label: 'B', text: 'This lesson\'s scope stops at "prove the contract works" with a minimal client; the later module covers building an actual production-grade frontend (React, TypeScript, real UX), a materially larger undertaking' },
          { id: 'c', label: 'C', text: 'There is no scope distinction between the two; they cover identical material' },
          { id: 'd', label: 'D', text: 'This lesson\'s frontend work should be discarded entirely once the Full-Stack FDE module begins' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson explicitly draws this boundary — minimal contract-proving here, full production frontend work later — rather than conflating the two very different-scoped tasks.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-06-mcq-05',
        question:
          'Why should the transition buttons shown in the demo UI reflect the order\'s actual current state (from the real API response) rather than a fixed, always-identical set of buttons?',
        options: [
          { id: 'a', label: 'A', text: 'Fixed buttons are technically impossible to implement in plain HTML' },
          { id: 'b', label: 'B', text: 'A fixed set of buttons regardless of state would misrepresent what the backend actually allows, undermining the demo\'s purpose of proving real contract behavior rather than a UI\'s own assumptions' },
          { id: 'c', label: 'C', text: 'This has no bearing on demo credibility either way' },
          { id: 'd', label: 'D', text: 'Buttons should always be hidden entirely to avoid any risk of an invalid click' }
        ],
        correctOptionId: 'b',
        explanation:
          'Consistent with the lesson\'s "prove real behavior, don\'t fake it" theme — the UI reflecting real state, not assumptions baked into the frontend, keeps the demo honest about what the backend actually enforces.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-06-mcq-06',
        question:
          'Before adding a live order-status display to the demo frontend, what question does the suggested extension say should be asked first?',
        options: [
          { id: 'a', label: 'A', text: 'Whether the feature can be implemented within one hour, with no other consideration' },
          { id: 'b', label: 'B', text: 'Whether this addition is proving something about the backend contract that matters to the customer, or whether it\'s polish that actually belongs in the later production-frontend module' },
          { id: 'c', label: 'C', text: 'Whether the customer has explicitly requested real-time updates in writing' },
          { id: 'd', label: 'D', text: 'No such question is necessary; any technically feasible addition should be built immediately' }
        ],
        correctOptionId: 'b',
        explanation:
          'This reinforces the lesson\'s core scope discipline — even a technically interesting addition should be checked against whether it\'s proving the contract or just adding polish outside this lesson\'s actual purpose.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/07-real-time-queues-and-caching-websockets-sse-redis': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-07-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — REAL-TIME PROTOCOL SELECTION',
        question:
          'What is the deciding question the lesson uses to choose between WebSockets and SSE?',
        options: [
          { id: 'a', label: 'A', text: 'Which technology has better browser support, considered in isolation from the actual use case' },
          { id: 'b', label: 'B', text: 'Does the client need to send messages back over the same real-time channel, or does it only need to receive them?' },
          { id: 'c', label: 'C', text: 'Which technology is newer' },
          { id: 'd', label: 'D', text: 'Whether the feature involves any form of real-time behavior at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson frames this as the single deciding factor — bidirectional need favors WebSockets, one-directional push favors SSE\'s simplicity.',
        incorrectExplanation:
          'Distinguish between unidirectional server push vs bidirectional full-duplex communication requirements.',
        hint: 'SSE is ideal for unidirectional server-to-client streaming over HTTP; WebSockets is required only when true bidirectional low-latency duplex messaging is necessary.'
      },
      {
        id: 'lesson-fde-backend-observability-data-07-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — DISTRIBUTED PUB/SUB BROKERING',
        question:
          'Why does a single server process\'s in-memory event handling fail to deliver a real-time update to a client connected to a different server instance?',
        options: [
          { id: 'a', label: 'A', text: 'In-memory event handling is technically incapable of functioning under any circumstances' },
          { id: 'b', label: 'B', text: 'Separate server processes don\'t share memory, so an in-memory event in one process has no mechanism to reach connections held open by a different process — Redis pub/sub bridges that gap by broadcasting across processes' },
          { id: 'c', label: 'C', text: 'This problem only occurs with WebSockets, never with SSE' },
          { id: 'd', label: 'D', text: 'A single server instance is always sufficient for any real-time system, making this scenario unrealistic' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the exact multi-instance reality behind a load balancer — the memory-isolation between processes is precisely the gap Redis pub/sub is designed to bridge for real-time delivery.',
        incorrectExplanation:
          'Consider what happens when client WebSockets/SSE connections are distributed across multiple independent server processes.',
        hint: 'When clients are connected across multiple load-balanced server nodes, an event processed on Node A cannot reach clients on Node B without a shared message broker like Redis.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-07-mcq-01',
        question:
          'Why does the lesson describe SSE as simpler to operate than WebSockets?',
        options: [
          { id: 'a', label: 'A', text: 'SSE connections use less bandwidth than WebSocket connections in every case' },
          { id: 'b', label: 'B', text: 'SSE works through standard HTTP infrastructure (load balancers, proxies) without special handling, unlike WebSockets which often require specific proxy/load-balancer configuration' },
          { id: 'c', label: 'C', text: 'SSE is a newer protocol than WebSockets and therefore inherently simpler' },
          { id: 'd', label: 'D', text: 'There is no operational difference between the two; the lesson\'s claim is incorrect' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is exactly why the scenario\'s FDE chose SSE — it avoided needing to request special WebSocket-proxying configuration from the customer\'s infrastructure team.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-07-mcq-02',
        question:
          'Why does the lesson describe cache invalidation as famously hard specifically, rather than just "somewhat tricky"?',
        options: [
          { id: 'a', label: 'A', text: 'Redis technically cannot support any form of cache invalidation' },
          { id: 'b', label: 'B', text: 'It\'s easy to forget one of the write paths that should invalidate a given cache entry, leaving a stale value silently served until its TTL happens to expire on its own, with no error to signal the mistake' },
          { id: 'c', label: 'C', text: 'Cache invalidation requires rewriting the entire application from scratch' },
          { id: 'd', label: 'D', text: 'This difficulty only applies to caches with a TTL longer than 24 hours' }
        ],
        correctOptionId: 'b',
        explanation:
          'The silent nature of the failure (no error, just stale data served until TTL expiry) is exactly what makes this class of bug hard to catch — it requires deliberate discipline at every write path, not a one-time setup.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-07-mcq-03',
        question:
          'Why did the FDE choose SSE over WebSockets for the demo frontend\'s live order-status updates?',
        options: [
          { id: 'a', label: 'A', text: 'WebSockets are technically incapable of transmitting order-status data' },
          { id: 'b', label: 'B', text: 'The client only needs to receive status changes, never send anything back over that channel — exactly the one-directional case the lesson identifies as SSE\'s fit' },
          { id: 'c', label: 'C', text: 'SSE is required by Stripe\'s API for any payment-related feature' },
          { id: 'd', label: 'D', text: 'The choice was arbitrary and either technology would have been equally justified' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a direct application of the lesson\'s deciding question — the requirement was purely one-directional, matching SSE\'s fit exactly as described.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-07-mcq-04',
        question:
          'Why did an order status change processed by one server instance need to be published to Redis rather than delivered directly to the connected client?',
        options: [
          { id: 'a', label: 'A', text: 'Redis is technically required for any SSE connection to function at all, even with a single server instance' },
          { id: 'b', label: 'B', text: 'The client\'s SSE connection might be held open by a different server instance than the one that processed the status change (a Stripe webhook could land on any instance behind the load balancer), and only Redis pub/sub, subscribed to by every instance, can bridge that gap' },
          { id: 'c', label: 'C', text: 'Direct delivery would have been faster and equally correct; Redis was an unnecessary addition' },
          { id: 'd', label: 'D', text: 'This routing decision was unrelated to the number of server instances involved' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the multi-instance reality driving the design — the webhook handler and the SSE connection for the same order can land on different instances, and pub/sub is what makes that not matter.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-07-mcq-05',
        question:
          'How does the lesson connect defaulting to WebSockets when SSE would suffice to a pattern from an earlier lesson?',
        options: [
          { id: 'a', label: 'A', text: 'There is no meaningful connection; the comparison is purely coincidental' },
          { id: 'b', label: 'B', text: 'It\'s the same over-engineering pattern as reaching for an agent loop when a fixed workflow would suffice — choosing the more complex, more flexible tool for no corresponding benefit when the simpler one already covers the actual requirement' },
          { id: 'c', label: 'C', text: 'WebSockets and agent loops are technically the same underlying mechanism' },
          { id: 'd', label: 'D', text: 'This connection only applies to systems that also use AI agents' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is an explicit cross-lesson pattern the course draws — matching tool complexity to actual requirement complexity, whether the domain is agent architecture or real-time transport choice.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-07-mcq-06',
        question:
          'Adding a short TTL alongside explicit cache invalidation is suggested as a safety net. What does this TTL protect against, and what does it NOT protect against?',
        options: [
          { id: 'a', label: 'A', text: 'A TTL provides complete protection against every possible cache-invalidation bug, with no remaining gap' },
          { id: 'b', label: 'B', text: 'It bounds the damage of a forgotten invalidation path (the stale value expires eventually, on its own), but it does not help if a client needs correctness within a shorter window than the TTL itself allows' },
          { id: 'c', label: 'C', text: 'A TTL has no protective value whatsoever and is purely a performance optimization' },
          { id: 'd', label: 'D', text: 'A TTL only matters for caches that never receive any writes' }
        ],
        correctOptionId: 'b',
        explanation:
          'A TTL is a bounded-damage safety net, not a substitute for correct invalidation logic — it limits how long a forgotten invalidation stays wrong, but a use case requiring tighter correctness than the TTL window still needs explicit invalidation to actually work.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/08-observability-and-distributed-tracing-opentelemetry-grafana': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-08-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — DISTRIBUTED TRACING VS ISOLATED LOGS',
        question:
          'Why can\'t a single service\'s logs alone reveal that its slowness was actually caused by a call to a different downstream service?',
        options: [
          { id: 'a', label: 'A', text: 'Logs are technically incapable of recording timestamps' },
          { id: 'b', label: 'B', text: 'The downstream service\'s own internal behavior isn\'t captured in the calling service\'s logs at all — only a trace that follows the request across both services can show the causal relationship' },
          { id: 'c', label: 'C', text: 'This is not actually true; a single service\'s logs are always sufficient regardless of how many services a request touches' },
          { id: 'd', label: 'D', text: 'Structured logging (from the earlier lesson) makes this limitation irrelevant' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is precisely the gap traces are designed to close — a service\'s own logs are scoped to what happened inside it, not to what happened in whatever else it called.',
        incorrectExplanation:
          'Consider how disconnected log files fail to show causality and timing breakdowns across network and process boundaries.',
        hint: 'Tracing correlates end-to-end request latency across multiple microservices and background queues, showing exact span breakdowns in a unified waterfall.'
      },
      {
        id: 'lesson-fde-backend-observability-data-08-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — TRACE CONTEXT PROPAGATION',
        question:
          'How does a trace ID generated at the start of a request end up associated with spans reported by a Celery task queued partway through that request\'s handling?',
        options: [
          { id: 'a', label: 'A', text: 'Celery automatically detects and reuses trace IDs with no explicit propagation needed' },
          { id: 'b', label: 'B', text: 'The trace ID is embedded in the queued task\'s payload when it\'s queued, so the Celery worker processing that task can report its own spans under the same trace ID, even though it runs in a completely separate process' },
          { id: 'c', label: 'C', text: 'Trace IDs cannot cross process boundaries under any circumstances, so this scenario is not actually possible' },
          { id: 'd', label: 'D', text: 'The trace ID is regenerated fresh for every new process, intentionally disconnecting the task\'s spans from the original request' }
        ],
        correctOptionId: 'b',
        explanation:
          'Explicit propagation — carrying the trace ID forward into whatever crosses a process or service boundary, whether an HTTP header or a queued task\'s payload — is the actual mechanism; it doesn\'t happen automatically without this deliberate step.',
        incorrectExplanation:
          'Think about how downstream services receive the parent trace ID across network and queue hops without shared process memory.',
        hint: 'By injecting standardized metadata headers (such as the W3C `traceparent` header containing trace ID and parent span ID) into outgoing HTTP requests and message payloads.'
      }
    ],
    architecture: {
      id: 'lesson-fde-backend-observability-data-08-distributed-trace-waterfall',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — OPENTELEMETRY DISTRIBUTED TRACE WATERFALL',
      boundaryLabel: 'DISTRIBUTED CONTEXT PROPAGATION BOUNDARY',
      boundaryText:
        'Trace context (trace_id, span_id) flows across HTTP and message queue boundaries via W3C traceparent headers, pinpointing external API latency.',
      nodes: [
        { id: 'client', label: 'HTTP POST /checkout', kind: 'input' },
        { id: 'api-span', label: 'FastAPI Span (Total: 1250ms)', kind: 'service' },
        { id: 'boundary', label: 'W3C Context Propagation', kind: 'boundary', highlighted: true },
        { id: 'db-span', label: 'Postgres Span (15ms)', kind: 'adapter' },
        { id: 'stripe-span', label: 'Stripe API Span (1180ms - Bottleneck)', kind: 'adapter' },
        { id: 'celery-span', label: 'Celery Enqueue Span (5ms)', kind: 'adapter' },
        { id: 'collector', label: 'OpenTelemetry Collector / Jaeger', kind: 'output' }
      ]
    },
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-08-mcq-01',
        question:
          'What do metrics provide that makes them useful even though they can\'t pinpoint which specific request or downstream call caused a problem?',
        options: [
          { id: 'a', label: 'A', text: 'Metrics are functionally identical to traces and provide the same information' },
          { id: 'b', label: 'B', text: 'Aggregated numeric signals over time (request rate, p99 latency, error rate) — good for spotting that something is wrong and roughly how bad, at a scale that inspecting individual traces one at a time wouldn\'t be efficient for' },
          { id: 'c', label: 'C', text: 'Metrics can identify the exact root cause of any specific slow request' },
          { id: 'd', label: 'D', text: 'Metrics are only useful for billing purposes, not diagnostics' }
        ],
        correctOptionId: 'b',
        explanation:
          'Metrics\' aggregated nature is their strength for spotting a trend or an anomaly at scale — the trade-off is they can\'t tell you which specific instance or downstream call to blame, which is where traces take over.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-08-mcq-02',
        question:
          'Why does the lesson emphasize instrumenting a system with tracing before an incident happens, rather than reactively adding it after a customer complaint?',
        options: [
          { id: 'a', label: 'A', text: 'Adding tracing after an incident is technically impossible for unrelated reasons' },
          { id: 'b', label: 'B', text: 'By the time an incident is reported, the specific slow request that would have shown the actual cause has already happened and passed — tracing added afterward can\'t retroactively see into that already-completed request' },
          { id: 'c', label: 'C', text: 'There is no real difference in value between instrumenting before versus after an incident' },
          { id: 'd', label: 'D', text: 'Grafana specifically requires instrumentation to be added before any system is deployed' }
        ],
        correctOptionId: 'b',
        explanation:
          'Tracing only captures what happens after it\'s instrumented — the specific request that caused the reported problem is already gone by the time reactive instrumentation would be added, which is exactly why proactive instrumentation is the actual discipline being taught.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-08-mcq-03',
        question:
          'Why was the FDE able to immediately identify the Stripe API call as the slow span, rather than the order-service logic or the Celery task\'s own processing?',
        options: [
          { id: 'a', label: 'A', text: 'The FDE had to guess based on general knowledge that Stripe calls are usually slow' },
          { id: 'b', label: 'B', text: 'With trace context propagated across all three systems, the trace waterfall laid out every span by duration and nesting, making the disproportionately long Stripe-call span visually obvious compared to the other spans, without needing to manually correlate separate log sources' },
          { id: 'c', label: 'C', text: 'Metrics alone, without any tracing, were sufficient to identify the specific slow span' },
          { id: 'd', label: 'D', text: 'The order service\'s logs alone contained enough detail to pinpoint the Stripe call as the bottleneck' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct payoff of the earlier tracing instrumentation — a visual waterfall making the disproportionate span obvious is precisely the diagnostic power distributed tracing adds over log correlation alone.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-08-mcq-04',
        question:
          'How does this lesson\'s trace-waterfall diagnostic technique relate to the "walk the trace backward" principle from the agent-debugging lesson earlier in the course?',
        options: [
          { id: 'a', label: 'A', text: 'The two techniques are entirely unrelated and the comparison is coincidental' },
          { id: 'b', label: 'B', text: 'Both apply the same underlying discipline — isolate which specific stage/step introduced a problem instead of judging the whole system by its final, aggregate outcome — generalized here from an AI agent\'s internal Thought/Action/Observation loop to a traditional multi-service backend request' },
          { id: 'c', label: 'C', text: 'The agent-debugging lesson\'s technique only applies to AI systems and has no analog in traditional backend systems' },
          { id: 'd', label: 'D', text: 'Distributed tracing replaces the need for the agent-debugging lesson\'s technique entirely' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is an explicit cross-module connection the course draws — the same "isolate the failing stage, don\'t guess from the aggregate symptom" discipline shows up in both AI-agent debugging and traditional distributed-systems tracing.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-08-mcq-05',
        question:
          'What does a single span in a trace represent?',
        options: [
          { id: 'a', label: 'A', text: 'An entire trace covering every service a request touches' },
          { id: 'b', label: 'B', text: 'One unit of work (an HTTP handler, a database call, an external API call), nested to show its causal relationship to the rest of the request' },
          { id: 'c', label: 'C', text: 'A single log line with no relationship to timing or causality' },
          { id: 'd', label: 'D', text: 'A metric aggregated over a fixed time window' }
        ],
        correctOptionId: 'b',
        explanation:
          'A trace is composed of many spans, each representing one unit of work, nested (parent/child) to reflect what called what — this is the structural building block that makes a trace waterfall\'s visualization possible.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-08-mcq-06',
        question:
          'In the suggested extension, how would a checkout-duration metric and a specific slow trace work together to diagnose a latency regression?',
        options: [
          { id: 'a', label: 'A', text: 'Metrics and traces provide identical information and using both is redundant' },
          { id: 'b', label: 'B', text: 'The metric, aggregated over time, would first reveal that checkout latency has degraded overall — then a specific slow trace, pulled for an individual instance of that degradation, would reveal exactly which span within that request is responsible' },
          { id: 'c', label: 'C', text: 'A metric alone, without any trace, is always sufficient to identify the exact cause of a regression' },
          { id: 'd', label: 'D', text: 'Traces should always be checked before metrics, in every diagnostic scenario, with no exceptions' }
        ],
        correctOptionId: 'b',
        explanation:
          'This models the complementary roles established earlier in the lesson — metrics for noticing an aggregate trend, traces for finding the specific cause within an individual instance of that trend.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/09-postgres-advanced-jsonb-full-text-search-and-pgvector': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-09-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — POSTGRES JSONB USE CASES',
        question:
          'For which situation is JSONB genuinely the right modeling choice, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Well-structured data with a fixed, known set of fields, used purely to avoid writing a migration' },
          { id: 'b', label: 'B', text: 'Any data at all, since JSONB is always the superior modeling choice regardless of structure' },
          { id: 'c', label: 'C', text: '' },
          { id: 'd', label: 'D', text: 'Only for data that will never be queried after being stored' }
        ],
        correctOptionId: 'a',
        explanation:
          'The lesson draws a specific line — genuine variability justifies JSONB; well-structured data dumped into JSONB purely to skip a migration is the smell to avoid.',
        incorrectExplanation:
          'Consider the trade-off between strict relational columns (with constraints and types) versus semi-structured polymorphic attributes.',
        hint: 'JSONB is ideal for semi-structured, polymorphic attributes (like custom tenant metadata or raw third-party webhook payloads) where schema shapes vary widely.'
      },
      {
        id: 'lesson-fde-backend-observability-data-09-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — PGVECTOR VS DEDICATED VECTOR STORES',
        question:
          'What does the pgvector-versus-dedicated-vector-database trade-off actually weigh against each other?',
        options: [
          { id: 'a', label: 'A', text: 'pgvector and dedicated vector databases are functionally identical, making this a non-decision' },
          { id: 'b', label: 'B', text: 'Operational simplicity (keeping embeddings in the same database as everything else, avoiding a new system to operate) versus specialized indexing and query performance that pulls further ahead as data volume and query load grow' },
          { id: 'c', label: 'C', text: 'Cost is the only relevant factor in this decision, with performance being irrelevant' },
          { id: 'd', label: 'D', text: 'pgvector is always the objectively superior choice regardless of scale' }
        ],
        correctOptionId: 'b',
        explanation:
          'This mirrors the built-in-versus-custom-tool trade-off theme from earlier in the course — the decision genuinely depends on scale and operational appetite, not a universal winner.',
        incorrectExplanation:
          'Think about infrastructure overhead, dual-write synchronization hazards, and relational join capabilities.',
        hint: '`pgvector` enables transactional consistency and relational joins alongside domain data with zero extra infrastructure; dedicated vector DBs are optimized for billion-scale vector indexing at the cost of dual-write operational complexity.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-09-mcq-01',
        question:
          'What does using JSONB for well-structured data, purely to avoid writing a migration, trade away?',
        options: [
          { id: 'a', label: 'A', text: 'Nothing; JSONB provides identical guarantees to real columns in every respect' },
          { id: 'b', label: 'B', text: 'Proper types, foreign key constraints, targeted indexes, and the query planner\'s ability to reason about the data — guarantees a real relational column provides that JSONB doesn\'t' },
          { id: 'c', label: 'C', text: 'Only query speed, with no other meaningful trade-off' },
          { id: 'd', label: 'D', text: 'The ability to store the data at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson is specific about what\'s lost — type safety, constraints, targeted indexing, and planner reasoning — which is exactly why this trade should be made deliberately, not defaulted into.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-09-mcq-02',
        question:
          'According to the lesson, when does standing up a dedicated search engine (instead of Postgres\'s built-in full-text search) become the justified choice?',
        options: [
          { id: 'a', label: 'A', text: 'Immediately, for any project involving text search, regardless of actual requirements' },
          { id: 'b', label: 'B', text: 'Once requirements grow past sophisticated relevance tuning, faceted search across many dimensions, or search volume/latency needs a dedicated engine\'s specialized indexing is built for — not as a default made because Postgres search "feels basic"' },
          { id: 'c', label: 'C', text: 'Postgres\'s built-in full-text search is never sufficient for any real use case' },
          { id: 'd', label: 'D', text: 'Only when the dataset contains fewer than 100 documents' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson explicitly frames Postgres\'s built-in search as genuinely sufficient for many needs, with a specific, requirement-driven threshold for when a dedicated engine becomes justified, not a reflexive default.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-09-mcq-03',
        question:
          'Why did the FDE choose pgvector over a dedicated vector database for the customer\'s RAG system in the scenario?',
        options: [
          { id: 'a', label: 'A', text: 'Dedicated vector databases are technically incompatible with RAG systems in general' },
          { id: 'b', label: 'B', text: 'The customer\'s existing infrastructure was entirely Postgres, their document volume was a few thousand (not millions), and they had a strong preference against adding new infrastructure — pgvector fit all three factors specifically for this customer' },
          { id: 'c', label: 'C', text: 'pgvector is always the objectively correct choice for every RAG system regardless of customer context' },
          { id: 'd', label: 'D', text: 'The customer explicitly forbade the FDE from ever reconsidering this decision in the future' }
        ],
        correctOptionId: 'b',
        explanation:
          'The decision was context-specific — matched to this customer\'s actual scale and infrastructure preference, not a universal rule, and the FDE was explicit that it could be revisited if the customer\'s scale changed significantly.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-09-mcq-04',
        question:
          'Why did the FDE explicitly tell the customer that pgvector was the right call "at their current volume" rather than presenting it as an unconditionally correct decision?',
        options: [
          { id: 'a', label: 'A', text: 'This transparency was unnecessary and added no value to the customer relationship' },
          { id: 'b', label: 'B', text: 'Being explicit about the trade-off sets accurate expectations that the decision may need revisiting if the customer\'s scale changes significantly, rather than implying the choice is permanently settled regardless of future growth' },
          { id: 'c', label: 'C', text: 'pgvector is only a temporary technology that will stop being supported soon' },
          { id: 'd', label: 'D', text: 'The FDE was required by contract to disclose every technical decision in this level of detail' }
        ],
        correctOptionId: 'b',
        explanation:
          'This reflects a broader honesty-about-trade-offs discipline consistent with the FDE-role lesson\'s emphasis on evidence and clear communication, rather than presenting a scale-dependent choice as a permanent, unconditional answer.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-09-mcq-05',
        question:
          'What does a GIN index on a JSONB column enable?',
        options: [
          { id: 'a', label: 'A', text: 'Automatic conversion of JSONB data into separate relational columns' },
          { id: 'b', label: 'B', text: 'Efficient containment queries (e.g. `WHERE metadata @> \'{"color": "red"}\'`) without requiring a full table scan' },
          { id: 'c', label: 'C', text: 'JSONB columns cannot be indexed under any circumstances' },
          { id: 'd', label: 'D', text: 'Full-text search capability, unrelated to JSONB containment queries' }
        ],
        correctOptionId: 'b',
        explanation:
          'GIN indexes are specifically what makes JSONB containment queries efficient — without one, the same query would require scanning every row.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-09-mcq-06',
        question:
          'Combining Postgres full-text search and pgvector similarity search in one hybrid query mirrors which earlier concept from the RAG lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The lost-in-the-middle generation failure mode' },
          { id: 'b', label: 'B', text: 'Hybrid search combining dense vector similarity with sparse keyword/BM25 matching — the same principle, here implemented entirely inside Postgres using its full-text search as the sparse/keyword side and pgvector as the dense side' },
          { id: 'c', label: 'C', text: 'RAGAS\'s four core evaluation metrics' },
          { id: 'd', label: 'D', text: 'There is no meaningful connection between this and any concept from the RAG lesson' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a direct cross-lesson application — the RAG lesson\'s hybrid-search concept (dense plus sparse) implemented concretely using Postgres\'s two search capabilities together.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/10-postgres-internals-explain-analyze-indexing-and-mvcc': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-10-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — POSTGRES QUERY PLAN DIAGNOSTICS',
        question:
          'What is the key difference between `EXPLAIN` and `EXPLAIN ANALYZE`?',
        options: [
          { id: 'a', label: 'A', text: 'They are functionally identical, differing only in output formatting' },
          { id: 'b', label: 'B', text: '`EXPLAIN` shows the planner\'s estimated cost and chosen plan without running the query; `EXPLAIN ANALYZE` actually executes the query and reports real timing and row counts alongside the plan' },
          { id: 'c', label: 'C', text: '`EXPLAIN ANALYZE` never actually runs the query, while `EXPLAIN` does' },
          { id: 'd', label: 'D', text: '`EXPLAIN` is only available in newer Postgres versions, while `EXPLAIN ANALYZE` is deprecated' }
        ],
        correctOptionId: 'b',
        explanation:
          'This distinction is the lesson\'s central point — only `EXPLAIN ANALYZE` reveals real execution behavior, which is why a plan that looks fine under plain `EXPLAIN` can still turn out to be slow in reality.',
        incorrectExplanation:
          'Distinguish between static cost estimation versus live execution profiling.',
        hint: '`EXPLAIN` outputs the planner\'s estimated cost without running the query; `EXPLAIN ANALYZE` actually executes the statement and captures real execution timings and row counts.'
      },
      {
        id: 'lesson-fde-backend-observability-data-10-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — MULTI-VERSION CONCURRENCY CONTROL (MVCC)',
        question:
          'What does MVCC (multi-version concurrency control) enable in Postgres?',
        options: [
          { id: 'a', label: 'A', text: 'MVCC prevents any two transactions from ever running concurrently' },
          { id: 'b', label: 'B', text: 'Readers never block writers and writers never block readers, because multiple versions of a row can exist simultaneously instead of requiring readers to wait for a writer\'s lock to release' },
          { id: 'c', label: 'C', text: 'MVCC eliminates the need for any locking whatsoever, including within a single transaction' },
          { id: 'd', label: 'D', text: 'MVCC only applies to `SELECT` statements, never to writes' }
        ],
        correctOptionId: 'b',
        explanation:
          'Keeping multiple row versions is exactly what avoids the reader-blocks-writer / writer-blocks-reader problem — the direct benefit of MVCC, alongside its dead-tuple cost covered next.',
        incorrectExplanation:
          'Consider how PostgreSQL handles concurrent read and write operations without requiring table-level read locks.',
        hint: 'By creating new row versions on mutation rather than in-place overwrites, readers never block writers and writers never block readers.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-10-mcq-01',
        question:
          'Why might a sequential scan actually be the correct, fastest choice for a query against a very small table, even with a relevant index available?',
        options: [
          { id: 'a', label: 'A', text: 'Postgres always malfunctions when an index exists on a small table' },
          { id: 'b', label: 'B', text: 'On a small enough table, scanning every row directly can be faster than the overhead of using an index to look up a small number of rows — "index scan is always better" is not actually true, and the planner\'s choice reflects real cost trade-offs, not a mistake' },
          { id: 'c', label: 'C', text: 'Indexes are technically unusable on tables below a fixed row-count threshold' },
          { id: 'd', label: 'D', text: 'This situation never actually occurs in practice; sequential scans are always worse' }
        ],
        correctOptionId: 'b',
        explanation:
          'This directly counters the common misconception that index scans are unconditionally superior — at small table sizes, the overhead of index traversal can genuinely exceed the cost of just reading every row.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-10-mcq-02',
        question:
          'Why does adding an index to a table impose a real cost on writes, not just provide a free read-performance benefit?',
        options: [
          { id: 'a', label: 'A', text: 'Indexes have no effect whatsoever on write performance in Postgres' },
          { id: 'b', label: 'B', text: 'Every insert, update, or delete has to maintain every index on the table alongside the actual row data, so a table with many indexes accepts writes more slowly' },
          { id: 'c', label: 'C', text: 'This cost only applies to indexes on primary key columns, not other indexes' },
          { id: 'd', label: 'D', text: 'Indexes only affect read performance, and any perceived write-cost effect is a myth' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the genuine trade-off the lesson emphasizes — indexes aren\'t a free performance upgrade, and their write-side cost has to be weighed against their read-side benefit for a given table\'s actual workload.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-10-mcq-03',
        question:
          'What happens to an old row version immediately after an `UPDATE` or `DELETE` in Postgres, under MVCC?',
        options: [
          { id: 'a', label: 'A', text: 'It is immediately and permanently deleted from disk with no further processing needed' },
          { id: 'b', label: 'B', text: 'It isn\'t immediately removed — it\'s marked as a dead tuple, and accumulates until Postgres\'s autovacuum process reclaims that space' },
          { id: 'c', label: 'C', text: 'It is automatically converted into a new index entry' },
          { id: 'd', label: 'D', text: 'MVCC has no concept of old row versions after an update or delete' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct operational consequence of MVCC\'s row-versioning approach — old versions linger as dead tuples until vacuumed, which is exactly why vacuuming matters for sustained performance.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-10-mcq-04',
        question:
          'What specifically did `EXPLAIN ANALYZE` reveal about the first slow order-history query in the scenario?',
        options: [
          { id: 'a', label: 'A', text: 'The Stripe API call was the actual bottleneck for this specific query, unrelated to indexing' },
          { id: 'b', label: 'B', text: 'A sequential scan across the entire orders table despite the FDE\'s assumption that an index on `customer_id` already existed — there wasn\'t one' },
          { id: 'c', label: 'C', text: 'The table had too many indexes, degrading write performance' },
          { id: 'd', label: 'D', text: 'The query itself contained a syntax error preventing execution' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct diagnostic finding that led to the straightforward fix — adding the missing index — verified afterward by re-running `EXPLAIN ANALYZE` and confirming the plan changed.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-10-mcq-05',
        question:
          'The second slow query in the scenario already had a correct index in place, yet was still slow. What did `EXPLAIN ANALYZE` reveal as the actual cause?',
        options: [
          { id: 'a', label: 'A', text: 'The index itself was corrupted and needed to be rebuilt from scratch' },
          { id: 'b', label: 'B', text: 'A large gap between the planner\'s estimated row count and the actual row count returned — a specific signal of stale table statistics, traced back to a misconfigured autovacuum threshold that had left the table un-vacuumed and un-analyzed for months' },
          { id: 'c', label: 'C', text: 'The query needed a second, additional index on the same column to resolve the slowness' },
          { id: 'd', label: 'D', text: 'The table had too few rows for any query against it to perform well' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is exactly the case the lesson uses to show that "add more indexes" isn\'t a universal fix — here, stale statistics from a vacuuming problem, not a missing index, was the actual root cause.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-10-mcq-06',
        question:
          'Why would simply adding more indexes have failed to fix the second slow query\'s actual problem?',
        options: [
          { id: 'a', label: 'A', text: 'Postgres technically has a hard limit on the number of indexes per table that had already been reached' },
          { id: 'b', label: 'B', text: 'The problem was stale planner statistics causing a bad plan choice, not a missing index — an existing, correct index was already in place, so adding more indexes wouldn\'t address the root cause and would only add unnecessary write overhead' },
          { id: 'c', label: 'C', text: 'Adding more indexes would have fixed this problem just as effectively as correcting the vacuum configuration' },
          { id: 'd', label: 'D', text: 'This query had no relationship to indexing at all, making the question irrelevant' }
        ],
        correctOptionId: 'b',
        explanation:
          'This reinforces the lesson\'s "measure, don\'t guess" discipline — misdiagnosing a statistics/vacuum problem as an indexing problem would add cost (more write overhead) without addressing the actual cause.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-10-mcq-07',
        question:
          'What single detail in `EXPLAIN ANALYZE`\'s output is the specific signal that distinguishes "this query needs an index" from "this query needs a vacuum/analyze"?',
        options: [
          { id: 'a', label: 'A', text: 'The total number of columns in the table, unrelated to either query plan or row-count estimates' },
          { id: 'b', label: 'B', text: 'The alphabetical order of column names in the SELECT clause' },
          { id: 'c', label: 'C', text: '' },
          { id: 'd', label: 'D', text: 'There is no way to distinguish the two causes from `EXPLAIN ANALYZE` output alone; only guessing can determine the cause' }
        ],
        correctOptionId: 'a',
        explanation:
          'The estimated-vs-actual row count gap is the specific diagnostic signal the scenario uses to point toward stale statistics rather than a missing index — a genuinely missing index instead shows up as a sequential scan with no relevant index available at all.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/11-nosql-document-dbs-and-vector-databases': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-11-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — NOSQL TAXONOMY & PARADIGMS',
        question:
          'Why does the lesson argue against treating "NoSQL" as one undifferentiated category with one set of trade-offs?',
        options: [
          { id: 'a', label: 'A', text: 'NoSQL databases are all functionally identical, making the distinction purely academic' },
          { id: 'b', label: 'B', text: 'Document, key-value, and wide-column stores have genuinely different access-pattern fits and trade-offs, and conflating them skips the actual engineering question of which access pattern the data has and which trade-offs are acceptable to sacrifice' },
          { id: 'c', label: 'C', text: 'Only document databases actually qualify as "real" NoSQL systems' },
          { id: 'd', label: 'D', text: 'This distinction only matters for systems processing more than a million records' }
        ],
        correctOptionId: 'b',
        explanation:
          'Each NoSQL category is a genuinely different design point suited to a different access pattern — key-value for simple get/set, document for flexible nested entities, wide-column for high-throughput time-series-like data — and lumping them together obscures the actual decision that matters.',
        incorrectExplanation:
          'Distinguish between the specific storage paradigms under the NoSQL umbrella (key-value, document, graph, vector) rather than treating them as interchangeable.',
        hint: 'NoSQL comprises fundamentally distinct data models—key-value, document, column-family, graph, and vector—each optimized for completely different access patterns.'
      },
      {
        id: 'lesson-fde-backend-observability-data-11-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — DOCUMENT STORE TRADE-OFFS',
        question:
          'What does a document database typically sacrifice, relative to a relational database, in exchange for schema flexibility and easier horizontal write scaling?',
        options: [
          { id: 'a', label: 'A', text: 'The ability to store any data at all beyond simple key-value pairs' },
          { id: 'b', label: 'B', text: 'Efficient cross-entity joins and strong relational consistency guarantees' },
          { id: 'c', label: 'C', text: 'Compatibility with any programming language' },
          { id: 'd', label: 'D', text: 'Document databases sacrifice nothing; the trade-off described in the lesson does not actually exist' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the specific, named trade-off the lesson establishes — not a vague "it\'s different," but a concrete loss of efficient joins and strong consistency in exchange for flexibility and scaling ease.',
        incorrectExplanation:
          'Consider what guarantees (relational integrity, declarative joins, schema enforcement) are given up when moving from relational tables to nested documents.',
        hint: 'Document databases trade strict relational integrity, cross-table constraints, and declarative joins for flexible nested document schemas and horizontal scaling.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-11-mcq-01',
        question:
          'How does this lesson\'s reasoning about a genuinely relational system moved into a document store connect to the earlier JSONB lesson\'s "smell" concept?',
        options: [
          { id: 'a', label: 'A', text: 'The two lessons describe entirely unrelated concepts with no meaningful connection' },
          { id: 'b', label: 'B', text: 'Both describe the same underlying mistake — forcing genuinely relational, well-structured, frequently-joined data into a schema-flexible format (JSONB or a document store) doesn\'t change its actual relational nature, it just trades away the guarantees and efficient joins that format was suited for' },
          { id: 'c', label: 'C', text: 'JSONB and document databases are functionally identical technologies' },
          { id: 'd', label: 'D', text: 'This connection only applies if the system in question uses Postgres specifically' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both lessons make the same point at different scales — schema-flexible storage doesn\'t change what the data actually is, and forcing genuinely structured, relational data into a flexible format sacrifices real guarantees for no corresponding benefit.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-11-mcq-02',
        question:
          'What did investigating the customer\'s "move to MongoDB for scale" request actually reveal as the root cause of their performance complaint?',
        options: [
          { id: 'a', label: 'A', text: 'Postgres genuinely could not handle the customer\'s actual write volume' },
          { id: 'b', label: 'B', text: 'A single unindexed query on a specific report, not a genuine write-throughput ceiling the relational database couldn\'t handle — a cheap, targeted fix, not a database migration' },
          { id: 'c', label: 'C', text: 'The order-management system had no performance problem at all, and the customer\'s complaint was baseless' },
          { id: 'd', label: 'D', text: 'MongoDB was confirmed to be strictly faster for every query type in this system' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the payoff of applying the earlier `EXPLAIN ANALYZE` diagnostic discipline before accepting a costly architectural change at face value — the actual problem was narrow and cheap to fix, not evidence of a fundamental database-choice mismatch.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-11-mcq-03',
        question:
          'Why did the FDE investigate before agreeing to migrate the order-management system to MongoDB, rather than deferring to the customer\'s stated preference?',
        options: [
          { id: 'a', label: 'A', text: 'FDEs are contractually forbidden from ever agreeing to database migrations' },
          { id: 'b', label: 'B', text: 'A migration to a database poorly suited to the system\'s actual, deeply relational access pattern (constant joins across orders, customers, products) would be costly and risky, and the customer\'s stated justification ("more scalable") hadn\'t been verified against the actual cause of the complaint' },
          { id: 'c', label: 'C', text: 'MongoDB is technically incapable of storing order data' },
          { id: 'd', label: 'D', text: 'The customer\'s request was not taken seriously for unrelated reasons' }
        ],
        correctOptionId: 'b',
        explanation:
          'This reflects the broader discipline from the problem-discovery lesson — investigating the actual underlying cause before committing to an expensive, potentially unnecessary solution the customer\'s stated request happened to suggest.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-11-mcq-04',
        question:
          'What does it mean, concretely, for a system to briefly serve inconsistent data across replicas after a write?',
        options: [
          { id: 'a', label: 'A', text: 'The write itself fails and no data is stored anywhere' },
          { id: 'b', label: 'B', text: 'A write succeeds on one replica, but a read shortly after, served from a different replica that hasn\'t yet received that write, could return the old (stale) value instead of the newly written one' },
          { id: 'c', label: 'C', text: 'All replicas are always perfectly synchronized at every instant, making this scenario impossible' },
          { id: 'd', label: 'D', text: 'This only affects reads that happen more than 24 hours after the original write' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the concrete behavior behind the abstract term "eventual consistency" — a real, observable staleness window between a write completing on one replica and that write propagating to others.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-11-mcq-05',
        question:
          'For which scenario does the lesson consider a document database a reasonable fit?',
        options: [
          { id: 'a', label: 'A', text: 'An orders system joined constantly across customers, products, and line items for everyday business logic' },
          { id: 'b', label: 'B', text: 'A product catalog entry with deeply nested, category-specific attributes that varies genuinely by category and is usually read and written as one coherent whole' },
          { id: 'c', label: 'C', text: 'Simple session data accessed only by a single key with no need for nested structure' },
          { id: 'd', label: 'D', text: 'A document database is never actually the right fit for any real-world scenario' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the lesson\'s own example of a genuine fit — variable, deeply nested, whole-document access is exactly the pattern document databases suit well, in contrast to the deeply relational orders scenario.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-11-mcq-06',
        question:
          'What principle should guide which pieces of an e-commerce system\'s data go into a relational store versus a document store or JSONB, per the suggested extension?',
        options: [
          { id: 'a', label: 'A', text: 'All data should always use exactly one storage technology for the sake of consistency, regardless of access pattern' },
          { id: 'b', label: 'B', text: 'Each piece of data\'s actual access pattern — transactional, frequently-joined data stays relational; genuinely variable, whole-document-accessed data fits a document store or JSONB — rather than forcing the entire system into one uniform storage choice' },
          { id: 'c', label: 'C', text: 'The choice should be based solely on which technology is newest' },
          { id: 'd', label: 'D', text: 'Storage technology choice has no meaningful connection to a piece of data\'s access pattern' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the lesson\'s central takeaway applied practically — a hybrid approach matching each piece of data to its actual access pattern, rather than a single one-size-fits-all storage decision for an entire system.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/12-dimensional-modeling-dbt-and-modern-data-stack': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-12-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — DIMENSIONAL MODELING FUNDAMENTALS',
        question:
          'What is the difference between a fact table and a dimension table in a star schema?',
        options: [
          { id: 'a', label: 'A', text: 'They are two names for the exact same kind of table' },
          { id: 'b', label: 'B', text: 'A fact table holds one row per business event with numeric measures (e.g. quantity, amount); a dimension table holds descriptive context around those facts (e.g. customer, product, date)' },
          { id: 'c', label: 'C', text: 'A dimension table holds numeric measures; a fact table holds descriptive context' },
          { id: 'd', label: 'D', text: 'Fact tables are always smaller than dimension tables' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the core structural distinction of dimensional modeling — facts are the measured events, dimensions are the descriptive context surrounding them, and getting this direction right is what makes a star schema\'s shape meaningful.',
        incorrectExplanation:
          'Distinguish between quantitative event measurements (facts) and contextual descriptive attributes (dimensions).',
        hint: 'Fact tables record quantitative event metrics (e.g. order amount, units sold); dimension tables hold descriptive context (e.g. customer info, product details, timestamps).'
      },
      {
        id: 'lesson-fde-backend-observability-data-12-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — MODERN DATA STACK (ELT VS ETL)',
        question:
          'What is the key difference between the ELT pattern and the older ETL pattern?',
        options: [
          { id: 'a', label: 'A', text: 'ELT and ETL describe the exact same process with different names' },
          { id: 'b', label: 'B', text: 'ELT loads raw data into the warehouse largely as-is and transforms it afterward, inside the warehouse; ETL transforms data before loading it, discarding the untransformed version' },
          { id: 'c', label: 'C', text: 'ETL loads raw data first and transforms it afterward; ELT transforms before loading' },
          { id: 'd', label: 'D', text: 'ELT is only usable for data smaller than 1 gigabyte' }
        ],
        correctOptionId: 'b',
        explanation:
          'The order of operations is the defining difference, and it\'s not arbitrary — ELT\'s "load raw first" order is what enables the retroactive-reprocessing benefit the lesson highlights.',
        incorrectExplanation:
          'Think about where and when data transformations occur relative to loading raw data into the analytical warehouse.',
        hint: 'ELT loads raw data directly into the warehouse and executes transformations using warehouse SQL (e.g. via dbt), preserving raw history and leveraging warehouse compute.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-12-mcq-01',
        question:
          'Why does the normalized OLTP schema from the order-management lesson perform poorly for an analytical query like "total revenue by product category last quarter"?',
        options: [
          { id: 'a', label: 'A', text: 'OLTP schemas are technically incapable of storing revenue figures' },
          { id: 'b', label: 'B', text: 'The normalized shape, optimized for fast individual reads/writes of one order at a time, requires many joins across many tables to answer an aggregation query that conceptually should be simple' },
          { id: 'c', label: 'C', text: 'This performance difference is a myth; OLTP and analytical schemas perform identically for any query type' },
          { id: 'd', label: 'D', text: 'Aggregation queries are impossible to write in SQL against a normalized schema' }
        ],
        correctOptionId: 'b',
        explanation:
          'The mismatch between the OLTP schema\'s design goal (fast individual transactional operations) and the analytical query\'s actual need (aggregating across many rows) is exactly why dimensional modeling exists as a separate discipline.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-12-mcq-02',
        question:
          'How does the lesson connect dbt\'s testing capability to the earlier testing/CI lesson from the FDE Foundations module?',
        options: [
          { id: 'a', label: 'A', text: 'dbt tests and application code tests are technically unrelated concepts that happen to share a name' },
          { id: 'b', label: 'B', text: 'It\'s the same discipline — a failing test catching a problem before it reaches downstream consumers — applied here to data models instead of application code, earning the same "CI as automated reviewer" benefit' },
          { id: 'c', label: 'C', text: 'dbt replaces the need for any application-code testing entirely' },
          { id: 'd', label: 'D', text: 'This connection only applies to tests checking numeric data types' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is an explicit cross-module reuse of the same principle — automated tests as a safety net that doesn\'t depend on a human noticing a problem, applied to data transformations rather than application logic.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-12-mcq-03',
        question:
          'Why does keeping raw, untransformed data available specifically help when a bug is found in a transformation model months later?',
        options: [
          { id: 'a', label: 'A', text: 'Raw data is technically immune to ever containing bugs, unlike transformed data' },
          { id: 'b', label: 'B', text: 'The fix can be re-run against the still-available raw data to correct the historical record; if the raw data had already been discarded during an upfront ETL transform, the same fix might be impossible without re-extracting from a source that may no longer be available in the same form' },
          { id: 'c', label: 'C', text: 'This benefit only applies if the bug is found within 24 hours of the original transformation' },
          { id: 'd', label: 'D', text: 'Keeping raw data has no bearing on the ability to fix a transformation bug retroactively' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the concrete operational payoff of ELT\'s raw-data-retention approach — a fixable historical record versus a potentially unrecoverable one, depending on whether the raw source is still available.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-12-mcq-04',
        question:
          'What did the referential-integrity dbt test catch in the scenario, and why did that matter?',
        options: [
          { id: 'a', label: 'A', text: 'A syntax error in the dbt model\'s SQL that would have prevented it from running at all' },
          { id: 'b', label: 'B', text: 'A small number of fact rows referencing a customer ID that no longer existed in `dim_customer`, caught in CI before the broken model reached the reporting dashboard — preventing a silently undercounted revenue figure from reaching a customer stakeholder' },
          { id: 'c', label: 'C', text: 'A performance regression in query execution time, unrelated to data correctness' },
          { id: 'd', label: 'D', text: 'The test found nothing wrong, and the scenario describes a successful, uneventful run' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the concrete stakes of the test — without it, the broken model\'s output would have silently reached a dashboard a real stakeholder trusts, exactly the failure mode automated data-quality tests exist to prevent.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-12-mcq-05',
        question:
          'What made the shift from ETL toward ELT practical, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'ETL was fundamentally impossible to implement correctly, forcing a switch to ELT' },
          { id: 'b', label: 'B', text: 'Warehouse compute becoming cheap enough that transforming data repeatedly inside the warehouse is no longer the bottleneck the older ETL pattern was designed to avoid' },
          { id: 'c', label: 'C', text: 'Raw data storage became more expensive, making ELT the only economically viable option' },
          { id: 'd', label: 'D', text: 'This shift has no relationship to compute or storage cost considerations' }
        ],
        correctOptionId: 'b',
        explanation:
          'The economic shift (cheap warehouse compute) is the specific enabling factor the lesson names — ETL\'s upfront-transform design existed to avoid a compute cost that\'s no longer the binding constraint it used to be.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-12-mcq-06',
        question:
          'Why does typical analytical reporting usually favor preserving a customer\'s historical region at the time of each order, rather than always showing their current region?',
        options: [
          { id: 'a', label: 'A', text: 'Customers never change region, making this consideration purely theoretical' },
          { id: 'b', label: 'B', text: 'A report on "revenue by region last year" should reflect where the customer actually was when each order happened, not retroactively reassign old orders to wherever the customer has since moved — preserving historical accuracy is usually the point of analytical reporting' },
          { id: 'c', label: 'C', text: 'Showing current region is always the objectively correct choice for every reporting need' },
          { id: 'd', label: 'D', text: 'This decision has no impact on the accuracy of historical reports' }
        ],
        correctOptionId: 'b',
        explanation:
          'Analytical reporting typically needs to answer "what was true at the time," which is exactly what a slowly-changing-dimension design that preserves historical values is built to support — the simpler "always current" design silently rewrites history.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/13-workflow-orchestration-with-airflow-and-data-quality': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-13-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — WORKFLOW ORCHESTRATION WITH DAGS',
        question:
          'What does Airflow\'s DAG model of explicit task dependencies provide that a monolithic cron-scheduled script does not?',
        options: [
          { id: 'a', label: 'A', text: 'DAGs eliminate the need for any scheduling at all' },
          { id: 'b', label: 'B', text: 'Task B is explicitly declared to run only after task A actually succeeds, rather than the pipeline relying on timing happening to work out or on independently-scheduled scripts staying correctly offset from each other' },
          { id: 'c', label: 'C', text: 'A monolithic cron script provides identical dependency guarantees to a DAG, making the distinction meaningless' },
          { id: 'd', label: 'D', text: 'DAGs are only useful for pipelines with fewer than three total tasks' }
        ],
        correctOptionId: 'b',
        explanation:
          'Explicit, success-gated dependency declaration is the core structural advantage over timing-based coordination, which is fragile and doesn\'t actually guarantee anything about whether an upstream step truly succeeded.',
        incorrectExplanation:
          'Consider what happens when interdependent cron scripts fail partway through or require scheduled backfills.',
        hint: 'Airflow DAGs explicitly manage inter-task dependencies, execution ordering, upstream failure cascading, retries, and programmatic backfilling.'
      },
      {
        id: 'lesson-fde-backend-observability-data-13-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — DATA QUALITY GATES IN PIPELINES',
        question:
          'Why does the lesson insist data-quality checks be explicit, first-class DAG tasks rather than an assumption that upstream data is fine?',
        options: [
          { id: 'a', label: 'A', text: 'Data-quality checks are required by Airflow\'s own internal architecture to function at all' },
          { id: 'b', label: 'B', text: 'Without explicit checks, bad data can silently flow downstream into whatever consumes it, with no one noticing until the bad output itself is eventually noticed, possibly much later and disconnected from its actual root cause' },
          { id: 'c', label: 'C', text: 'Assuming upstream data is fine is always a safe assumption in a well-built pipeline' },
          { id: 'd', label: 'D', text: 'This concern only applies to pipelines processing financial data specifically' }
        ],
        correctOptionId: 'b',
        explanation:
          'The core risk being defended against is silent propagation of bad data — explicit checks are what surface the problem at its actual source instead of letting it drift downstream undetected.',
        incorrectExplanation:
          'Think about the consequences of allowing downstream reporting models to execute when an upstream extraction produces corrupt or zero-row data.',
        hint: 'Gating checks halt DAG execution on validation anomalies, preventing bad, empty, or corrupted data from contaminating downstream marts and reports.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-13-mcq-01',
        question:
          'How does Airflow\'s DAG concept relate to the earlier n8n workflow lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Airflow and n8n are functionally identical tools with no meaningful difference' },
          { id: 'b', label: 'B', text: 'It\'s the same underlying idea — a graph of dependent steps — reappearing in a new domain, with Airflow specialized specifically for data-pipeline orchestration (backfills, per-task retries, SLA monitoring) rather than n8n\'s broader general-purpose automation focus' },
          { id: 'c', label: 'C', text: 'n8n and Airflow solve entirely unrelated problems with no conceptual overlap' },
          { id: 'd', label: 'D', text: 'Airflow replaces the need for n8n in every context' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is an explicit cross-module connection — the same graph-of-dependent-steps concept, specialized differently for different domains (data pipelines versus general automation).'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-13-mcq-02',
        question:
          'Why does the lesson argue a pipeline stage that "succeeds" while producing wrong data is more dangerous than one that fails loudly?',
        options: [
          { id: 'a', label: 'A', text: 'Loud failures are always more expensive to fix than silent ones' },
          { id: 'b', label: 'B', text: 'Everything downstream treats the wrong output as valid, and the eventual symptom surfaces disconnected from its actual root cause, often much later than when the original problem occurred — whereas a loud failure is immediately actionable by someone who knows exactly what broke' },
          { id: 'c', label: 'C', text: 'There is no real difference in danger between the two failure modes' },
          { id: 'd', label: 'D', text: 'Silent failures are actually easier to diagnose because they produce no error noise' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the lesson\'s central risk argument — a silent failure\'s damage compounds by propagating downstream and surfacing later, disconnected from its cause, unlike a loud failure that\'s immediately traceable.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-13-mcq-03',
        question:
          'Why was a dashboard showing "zero orders today," caused by a silent source-system outage, particularly dangerous in the scenario?',
        options: [
          { id: 'a', label: 'A', text: 'Zero-row extracts always cause the entire warehouse to become permanently corrupted' },
          { id: 'b', label: 'B', text: 'It looks like "no orders were placed" rather than "the pipeline failed to extract anything" — a materially different and far more alarming situation the customer would have no way to distinguish from the dashboard alone' },
          { id: 'c', label: 'C', text: 'The dashboard would have displayed an explicit error message, making the problem obvious' },
          { id: 'd', label: 'D', text: 'This scenario has no realistic risk since source-system outages never actually occur' }
        ],
        correctOptionId: 'b',
        explanation:
          'The danger is specifically the ambiguity — a plausible-looking but wrong result (zero orders) is indistinguishable from a genuinely quiet business day without an explicit check surfacing the real cause.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-13-mcq-04',
        question:
          'How did the row-count sanity check task change the outcome of the scenario\'s source-system outage?',
        options: [
          { id: 'a', label: 'A', text: 'It automatically fixed the source-system outage without any human involvement' },
          { id: 'b', label: 'B', text: 'It compared today\'s extracted row count against a reasonable historical range, caught the anomalous zero-row extract, failed the DAG loudly, and alerted the FDE before the empty data ever reached the dashboard' },
          { id: 'c', label: 'C', text: 'It silently corrected the zero-row extract by estimating what the data should have looked like' },
          { id: 'd', label: 'D', text: 'It had no actual effect on the outcome described in the scenario' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the direct mechanism of the fix — turning a silent, misleading failure into a loud, immediately actionable one, exactly the transformation the lesson\'s concepts describe.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-13-mcq-05',
        question:
          'How does this lesson connect a symptom-appearing-downstream-of-its-cause problem to the earlier debugging-AI lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The two lessons describe entirely unrelated failure modes with no shared principle' },
          { id: 'b', label: 'B', text: 'Both describe the same structural risk — a symptom observed at the end of a chain (a wrong dashboard, a wrong final agent output) doesn\'t by itself reveal where the actual fault originated, which is why isolating the specific failing stage matters in both domains' },
          { id: 'c', label: 'C', text: 'This connection only applies to pipelines that use AI agents internally' },
          { id: 'd', label: 'D', text: 'The debugging-AI lesson\'s principle only applies to non-deterministic systems, never to data pipelines' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a deliberate cross-module echo — the same "isolate the actual failing stage instead of trusting the final symptom" discipline reappears here in a data-pipeline context, mirroring the agent-debugging lesson\'s trace-backward technique.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-13-mcq-06',
        question:
          'Why does the suggested extension\'s backfill scenario depend on the raw data for the affected dates still being available?',
        options: [
          { id: 'a', label: 'A', text: 'Backfills do not actually require any raw data at all; they regenerate historical records from nothing' },
          { id: 'b', label: 'B', text: 'A backfill re-runs the DAG\'s transformation logic for historical dates, which requires the original raw data for those dates to still exist to transform correctly — exactly the ELT raw-data-retention benefit from the previous lesson' },
          { id: 'c', label: 'C', text: 'Raw data retention has no relationship to Airflow\'s backfill capability' },
          { id: 'd', label: 'D', text: 'Backfills only work if the raw data is less than one week old' }
        ],
        correctOptionId: 'b',
        explanation:
          'This directly reuses the previous lesson\'s ELT/raw-data-retention argument — backfilling to correct historical data is only possible because the raw source for those dates was deliberately kept around, not discarded after an upfront transform.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/14-event-driven-architecture-and-kafka-fundamentals': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-14-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — EVENT-DRIVEN PRODUCER-CONSUMER DECOUPLING',
        question:
          'What is the core decoupling event-driven architecture provides that a direct synchronous call does not?',
        options: [
          { id: 'a', label: 'A', text: 'Event-driven architecture eliminates the need for any consumer to exist at all' },
          { id: 'b', label: 'B', text: 'A producer publishes an event without knowing or caring who, if anyone, is listening — consumers subscribe independently and can be added later with zero changes to the producer' },
          { id: 'c', label: 'C', text: 'A direct synchronous call and an event-driven publish provide identical decoupling' },
          { id: 'd', label: 'D', text: 'Event-driven architecture requires the producer to know every consumer\'s identity in advance' }
        ],
        correctOptionId: 'b',
        explanation:
          'The defining property is that the producer has no knowledge of or dependency on its consumers — this is what allows new consumers to be added later without touching the producer\'s code at all.',
        incorrectExplanation:
          'Distinguish between point-to-point command invocations and decoupled broadcast event publishing.',
        hint: 'Producers publish facts ("OrderCreated") to a topic without coupling to downstream consumers, allowing new consumers to subscribe with zero producer changes.'
      },
      {
        id: 'lesson-fde-backend-observability-data-14-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — KAFKA PARTITION ORDERING GUARANTEES',
        question:
          'Two events for different order IDs are published close together. Does Kafka guarantee their processing order relative to each other?',
        options: [
          { id: 'a', label: 'A', text: 'Yes, Kafka guarantees global ordering across an entire topic regardless of key' },
          { id: 'b', label: 'B', text: 'No — ordering is only guaranteed within a partition, for events sharing the same key; events with different keys landing on different partitions carry no ordering guarantee relative to one another' },
          { id: 'c', label: 'C', text: 'Kafka provides no ordering guarantees whatsoever, even within a single partition' },
          { id: 'd', label: 'D', text: 'Ordering guarantees only apply if the events are published by the same producer instance' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the specific, concrete detail the lesson flags as a common source of real bugs — assuming topic-wide ordering when Kafka only actually guarantees it within a partition, for matching keys.',
        incorrectExplanation:
          'Consider how Kafka distributes messages across topic partitions and what that means for ordering across different partition keys.',
        hint: 'Kafka guarantees strict FIFO ordering within an individual partition, but does NOT guarantee global ordering across multiple partitions in a topic.'
      }
    ],
    architecture: {
      id: 'lesson-fde-backend-observability-data-14-event-driven-kafka-pipeline',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — EVENT-DRIVEN DECOUPLING VIA KAFKA',
      boundaryLabel: 'EVENT STREAMING LOG BOUNDARY',
      boundaryText:
        'FastAPI producer publishes OrderEvents keyed by order_id to a partitioned Kafka topic; independent consumer groups process asynchronously.',
      nodes: [
        { id: 'api-producer', label: 'FastAPI Order Service (Producer)', kind: 'service' },
        { id: 'kafka-topic', label: 'Kafka Topic: order-events (Partitioned by order_id)', kind: 'boundary', highlighted: true },
        { id: 'consumer-payments', label: 'Payments Worker (Consumer Group A)', kind: 'adapter' },
        { id: 'consumer-notifications', label: 'Notifications Worker (Consumer Group B)', kind: 'adapter' },
        { id: 'consumer-analytics', label: 'Analytics / Data Lake Ingestion (Consumer Group C)', kind: 'adapter' },
        { id: 'dlq', label: 'Dead-Letter Queue (DLQ)', kind: 'output' }
      ]
    },
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-14-mcq-01',
        question:
          'How does an event-driven publish differ from a Celery task queued earlier in this module, in terms of decoupling?',
        options: [
          { id: 'a', label: 'A', text: 'Celery tasks and event-driven publishing provide identical decoupling with no meaningful difference' },
          { id: 'b', label: 'B', text: 'A queued Celery task still names its specific downstream work at the point it\'s queued; a published event doesn\'t know or need to know what, if anything, will consume it — a materially looser coupling' },
          { id: 'c', label: 'C', text: 'Celery tasks are inherently incapable of being processed asynchronously, unlike events' },
          { id: 'd', label: 'D', text: 'Event-driven publishing always requires fewer lines of code than a Celery task' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a precise distinction the lesson draws — Celery decouples timing (the work happens later, off the critical path) but still names its specific consumer; events decouple identity of consumer entirely.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-14-mcq-02',
        question:
          'What does Kafka\'s "durable log" framing enable that a simpler message queue typically does not?',
        options: [
          { id: 'a', label: 'A', text: 'Durable logs prevent any event from ever being consumed more than once, under any circumstances' },
          { id: 'b', label: 'B', text: 'A consumer can replay from any earlier offset in the log, useful for reprocessing after fixing a downstream bug or for a new consumer catching up on historical events, not just future ones' },
          { id: 'c', label: 'C', text: 'Durable logs are only relevant for events smaller than 1 kilobyte' },
          { id: 'd', label: 'D', text: 'This framing has no practical difference from a simple queue' }
        ],
        correctOptionId: 'b',
        explanation:
          'Replayability is the specific capability the durable-log model adds — a consumer isn\'t limited to only future events, which matters directly for reprocessing and onboarding new consumers.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-14-mcq-03',
        question:
          'Why should events for the order-management system be keyed by order ID rather than a random ID?',
        options: [
          { id: 'a', label: 'A', text: 'Random keys are technically forbidden by Kafka\'s protocol' },
          { id: 'b', label: 'B', text: 'Keying by order ID guarantees all events for the same order land on the same partition and are processed in order relative to each other — a random key would break this per-order ordering guarantee' },
          { id: 'c', label: 'C', text: 'The choice of key has no bearing on ordering or partition assignment' },
          { id: 'd', label: 'D', text: 'Order ID must be used as the key specifically because it improves consumer throughput, unrelated to ordering' }
        ],
        correctOptionId: 'b',
        explanation:
          'The key directly determines partition assignment and therefore ordering scope — choosing order ID as the key is what makes per-order event ordering an actual guarantee rather than incidental.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-14-mcq-04',
        question:
          'Why did the FDE consider the event-driven redesign justified for this specific system, rather than over-engineering?',
        options: [
          { id: 'a', label: 'A', text: 'Event-driven architecture should always be adopted regardless of demonstrated need, since it\'s inherently more scalable' },
          { id: 'b', label: 'B', text: '"New independent consumers appearing over time" was a demonstrated, recurring pattern for this system (a second consumer request in as many months, with a third already anticipated), not a hypothetical flexibility being bought defensively against a need that might never materialize' },
          { id: 'c', label: 'C', text: 'The redesign was justified purely because Kafka is a more modern technology than direct calls or Celery' },
          { id: 'd', label: 'D', text: 'There was no real justification; this was an example of unjustified over-engineering the lesson criticizes' }
        ],
        correctOptionId: 'b',
        explanation:
          'The justification is explicitly evidence-based — a real, recurring pattern of new consumers, not an abstract appeal to scalability or modernity, which is exactly the distinction the lesson draws between justified and unjustified architectural complexity.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-14-mcq-05',
        question:
          'How does this lesson\'s judgment about event-driven architecture connect to the agent-versus-workflow and WebSockets-versus-SSE decisions from earlier lessons?',
        options: [
          { id: 'a', label: 'A', text: 'These three decisions are technically unrelated and any perceived similarity is coincidental' },
          { id: 'b', label: 'B', text: 'All three are instances of the same discipline — match the architecture\'s complexity to a genuine, demonstrated need for that complexity\'s specific benefit, rather than reaching for the more flexible or more sophisticated-sounding option by default' },
          { id: 'c', label: 'C', text: 'This connection only applies to systems that use both AI agents and Kafka simultaneously' },
          { id: 'd', label: 'D', text: 'Event-driven architecture should always be preferred in the same way an agent should always be preferred over a fixed workflow' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is an explicit recurring pattern across the course — matching tool/architecture complexity to genuine need, not defaulting to the more sophisticated option, shown here for the third time in a different technical domain.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-14-mcq-06',
        question:
          'What do Kafka consumer groups enable?',
        options: [
          { id: 'a', label: 'A', text: 'Consumer groups let every consumer in the group process every event, duplicating all work across all members' },
          { id: 'b', label: 'B', text: 'Multiple consumer instances splitting a topic\'s partitions among themselves for horizontal processing scale, with each partition consumed by exactly one group member at a time' },
          { id: 'c', label: 'C', text: 'Consumer groups are only relevant for producers, not consumers' },
          { id: 'd', label: 'D', text: 'Consumer groups eliminate the need for partitions entirely' }
        ],
        correctOptionId: 'b',
        explanation:
          'Consumer groups are the horizontal-scaling mechanism for consumption — splitting partitions among group members so processing throughput scales with the number of consumer instances, without duplicating work.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-14-mcq-07',
        question:
          'Why does the suggested extension warn against letting a repeatedly-failing event block its partition indefinitely?',
        options: [
          { id: 'a', label: 'A', text: 'Indefinite blocking is technically impossible in Kafka regardless of consumer behavior' },
          { id: 'b', label: 'B', text: 'Because a partition is consumed in order, a stuck event blocking indefinitely would also block every other, unrelated event queued behind it on the same partition — a dead-letter-queue pattern (moving the failing event aside after bounded retries) lets those other events continue being processed' },
          { id: 'c', label: 'C', text: 'This concern only applies to producers, not consumers' },
          { id: 'd', label: 'D', text: 'Blocking indefinitely has no effect on any other event, since each event is processed in total isolation' }
        ],
        correctOptionId: 'b',
        explanation:
          'This connects directly to the partition-ordering concept from earlier in the lesson — because a partition processes events in order, a stuck event has a real blast radius on everything queued behind it, which is exactly why a dead-letter pattern matters.'
      }
    ]
  },
  'fde-curriculum/backend-observability-data/15-assessment-data-pipeline-build-and-debug': {
    conceptChecks: [
      {
        id: 'lesson-fde-backend-observability-data-15-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — BLIND DIAGNOSTIC EVALUATION',
        question:
          'Why must the person diagnosing the injected failure not be told what was injected beforehand?',
        options: [
          { id: 'a', label: 'A', text: 'Undisclosed injection is a formality with no bearing on what the exercise actually tests' },
          { id: 'b', label: 'B', text: 'Diagnosing with foreknowledge of the actual injected failure would just confirm they can recognize a known answer, not that the pipeline\'s instrumentation genuinely surfaces enough evidence to find an unknown root cause from scratch — the real-world diagnostic skill being tested' },
          { id: 'c', label: 'C', text: 'This requirement exists purely to make the exercise take longer' },
          { id: 'd', label: 'D', text: 'Disclosing the failure in advance would make the pipeline itself technically fail to run' }
        ],
        correctOptionId: 'b',
        explanation:
          'Undisclosed injection is what makes this a genuine test of the pipeline\'s diagnosability rather than the diagnoser\'s memory — mirroring the realistic situation of a genuinely unknown production failure.',
        incorrectExplanation:
          'Think about why diagnosing an unknown defect tests true observability and root-cause analysis skills.',
        hint: 'A blind failure forces the engineer to rely on structured telemetry, backward tracing, and DAG logs rather than pre-rehearsed fixes.'
      },
      {
        id: 'lesson-fde-backend-observability-data-15-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — RESILIENT PIPELINE FAILURE HANDLING',
        question:
          'What does the rubric\'s "failure handling" category specifically check?',
        options: [
          { id: 'a', label: 'A', text: 'How many total lines of code the pipeline contains' },
          { id: 'b', label: 'B', text: 'Whether the injected failure actually gets caught by a data-quality check or dbt-style test, failing the pipeline loudly rather than silently propagating bad data through to the final output' },
          { id: 'c', label: 'C', text: 'Whether the pipeline runs faster than a fixed time threshold' },
          { id: 'd', label: 'D', text: 'Whether the pipeline uses a specific named orchestration tool rather than any equivalent' }
        ],
        correctOptionId: 'b',
        explanation:
          'This directly checks whether the earlier lesson\'s "silent failure is worse than loud failure" principle was actually implemented, not just discussed — a real, checkable behavior under the injected failure.',
        incorrectExplanation:
          'Consider what constitutes resilient data pipeline engineering when upstream sources deliver bad or empty data.',
        hint: 'It evaluates whether pipeline quality gates catch invalid or missing records and fail loudly before bad data pollutes analytical models.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-15-mcq-01',
        question:
          'What is the distinguishing feature of this assessment compared to the earlier Python Engineering Challenge assessment?',
        options: [
          { id: 'a', label: 'A', text: 'This assessment does not require any code to be written at all, unlike the earlier one' },
          { id: 'b', label: 'B', text: 'It includes a deliberately injected, undisclosed failure that must be diagnosed using only the pipeline\'s own instrumentation, directly testing diagnosability rather than only whether the system works under normal conditions' },
          { id: 'c', label: 'C', text: 'This assessment has no rubric, unlike the earlier one' },
          { id: 'd', label: 'D', text: 'There is no meaningful difference between the two assessments' }
        ],
        correctOptionId: 'b',
        explanation:
          'The undisclosed-failure diagnosis requirement is the specific new element here, testing the observability and diagnosability discipline this module built toward, beyond what the earlier assessment covered.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-15-mcq-02',
        question:
          'Why does the lesson describe "diagnosability" as the rubric category most lessons in this module were explicitly building toward?',
        options: [
          { id: 'a', label: 'A', text: 'Diagnosability is unrelated to any specific earlier lesson and was introduced for the first time in this assessment' },
          { id: 'b', label: 'B', text: 'The observability lesson (traces/logs), the Postgres-internals lesson (EXPLAIN ANALYZE diagnosis), and the data-quality/Airflow lesson (catching problems loudly) all specifically taught diagnostic technique, and this category is where that accumulated skill actually gets tested against a real, unknown failure' },
          { id: 'c', label: 'C', text: 'Diagnosability only reflects how fast the pipeline executes, unrelated to earlier lessons\' content' },
          { id: 'd', label: 'D', text: 'This category was included arbitrarily with no connection to the module\'s actual content' }
        ],
        correctOptionId: 'b',
        explanation:
          'Multiple lessons across this module (tracing, EXPLAIN ANALYZE, data-quality checks) each taught a piece of diagnostic discipline — this assessment\'s diagnosability category is where all of that accumulated skill is actually exercised together against an unknown problem.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-15-mcq-03',
        question:
          'Why does the "modeling soundness" rubric category require the referential-integrity or null-check test to "genuinely catch a broken case," not merely exist?',
        options: [
          { id: 'a', label: 'A', text: 'The mere presence of any test file automatically satisfies this rubric category regardless of what it checks' },
          { id: 'b', label: 'B', text: 'A test that\'s present but never actually fails on bad data (a decorative test that always passes) provides no real safety net — the rubric requires demonstrating the test would actually catch a genuine violation, not just that a test file exists' },
          { id: 'c', label: 'C', text: 'This requirement only applies to referential-integrity tests, never to null checks' },
          { id: 'd', label: 'D', text: 'Modeling soundness has no relationship to whether tests actually catch real problems' }
        ],
        correctOptionId: 'b',
        explanation:
          'This echoes the "test quality" rubric principle from the earlier Python assessment — a test that never actually fails on bad input isn\'t meaningfully testing anything, regardless of its mere presence in the codebase.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-15-mcq-04',
        question:
          'Why does the lesson say this assessment doesn\'t need a separate practical scenario, unlike most other lessons in this course?',
        options: [
          { id: 'a', label: 'A', text: 'Assessments are exempt from needing to demonstrate any real-world relevance' },
          { id: 'b', label: 'B', text: 'The assessment itself, deliberately built so skipping any rubric item produces a materially worse (not just cosmetically worse) result, already demonstrates the module\'s real stakes directly, functioning as its own scenario' },
          { id: 'c', label: 'C', text: 'This lesson genuinely has no connection to any real-world situation' },
          { id: 'd', label: 'D', text: 'A separate scenario was omitted purely to save space, with no substantive justification' }
        ],
        correctOptionId: 'b',
        explanation:
          'This mirrors the same reasoning from the earlier Python assessment lesson — the assessment\'s own structure (rubric items mapping to real capabilities) makes it self-demonstrating rather than needing an additional illustrative example.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-15-mcq-05',
        question:
          'Why does the practice loop suggest building the star schema and ELT ingestion before adding orchestration or quality checks?',
        options: [
          { id: 'a', label: 'A', text: 'Airflow technically cannot be installed until a star schema already exists' },
          { id: 'b', label: 'B', text: 'Validating the core data-modeling logic first, before layering orchestration and quality checks on top, mirrors the earlier "build against a simple foundation first" pattern from the hexagonal-architecture and agent lessons — getting the fundamentals right before adding operational complexity' },
          { id: 'c', label: 'C', text: 'This ordering has no particular rationale and any order would work identically' },
          { id: 'd', label: 'D', text: 'Quality checks are only possible to write after the pipeline has already failed once in production' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a reasonable build-order heuristic consistent with earlier lessons\' "validate the core first, then add operational layers" pattern, even though the rubric doesn\'t strictly require this specific build order.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-backend-observability-data-15-mcq-06',
        question:
          'Why does the suggested extension say it\'s worth investigating if diagnosing a second, different injected failure isn\'t meaningfully faster than the first?',
        options: [
          { id: 'a', label: 'A', text: 'The second diagnosis should always take exactly the same amount of time as the first, regardless of instrumentation quality' },
          { id: 'b', label: 'B', text: 'Familiarity with the pipeline\'s instrumentation from the first diagnosis should genuinely speed up the second one if the instrumentation is doing its job well — a lack of improvement is a signal the instrumentation itself may not be as diagnosable as the first success suggested, not just bad luck on the second failure' },
          { id: 'c', label: 'C', text: 'This comparison has no diagnostic value about the pipeline\'s own instrumentation quality' },
          { id: 'd', label: 'D', text: 'A slower second diagnosis always indicates the second injected failure was objectively harder, with no other possible explanation' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a self-diagnostic check on the instrumentation itself — genuinely good observability should compound in usefulness with familiarity, and a lack of improvement is worth investigating as a signal about the instrumentation\'s real quality.'
      }
    ]
  },
  'fde-curriculum/full-stack-ai-frontends/01-typescript-fundamentals-for-python-engineers': {
    conceptChecks: [
      {
        id: 'lesson-fde-full-stack-ai-frontends-01-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — STRUCTURAL VS. NOMINAL TYPING',
        question:
          'How does TypeScript\'s structural typing differ from the nominal, class-based checking `mypy` performs on Python type hints?',
        options: [
          { id: 'a', label: 'A', text: 'TypeScript and mypy use identical typing models with no meaningful difference' },
          { id: 'b', label: 'B', text: 'A value satisfies a TypeScript interface if it has the right shape, regardless of whether it was ever declared to implement it, whereas `mypy` generally wants a value that actually is the declared class or a subclass' },
          { id: 'c', label: 'C', text: 'TypeScript requires every object to explicitly declare which interfaces it implements, like a Python class declaring inheritance' },
          { id: 'd', label: 'D', text: 'Structural typing means TypeScript never checks types at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'Structural typing checks shape, not declared identity — an object literal can satisfy an interface with zero explicit relationship to it, which is closer to Python\'s runtime duck-typing instinct than to mypy\'s nominal class checking.',
        incorrectExplanation:
          'Recall the distinction between nominal typing (matching declared class hierarchy) and structural typing (matching field shapes).',
        hint: 'TypeScript checks whether the shape matches, regardless of explicit inheritance or class declarations.'
      },
      {
        id: 'lesson-fde-full-stack-ai-frontends-01-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — UNKNOWN VS. ANY & TYPE NARROWING',
        question:
          'Why does the lesson recommend `unknown` over `any` for a value whose shape genuinely isn\'t known yet, like a raw API response body?',
        options: [
          { id: 'a', label: 'A', text: '`unknown` and `any` behave identically at compile time but `unknown` runs faster' },
          { id: 'b', label: 'B', text: '`unknown` forces a narrowing check (a type guard or validation) before the value can be used for anything, whereas `any` lets code compile and run against the value with no verification at all' },
          { id: 'c', label: 'C', text: '`unknown` is only usable for numeric values, never for objects' },
          { id: 'd', label: 'D', text: '`any` requires more lines of code to use correctly than `unknown` does' }
        ],
        correctOptionId: 'b',
        explanation:
          '`unknown`\'s defining property is that you cannot use it without first narrowing it, which matches "verify before trusting this data" — exactly the discipline the parseOrder example demonstrates.',
        incorrectExplanation:
          'Consider what the compiler forces you to do before accessing properties on an unknown value versus an any value.',
        hint: '`unknown` requires explicit narrowing or runtime type guards before properties can be accessed, whereas `any` completely disables type checking.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-01-mcq-01',
        question:
          'Per the lesson\'s practical default, when should you reach for `type` rather than `interface`?',
        options: [
          { id: 'a', label: 'A', text: 'Always — `interface` is deprecated and should never be used' },
          { id: 'b', label: 'B', text: 'For unions, intersections, and anything that isn\'t a plain object shape, since `type` is strictly more general than `interface`' },
          { id: 'c', label: 'C', text: 'Only when describing the shape of a class you plan to extend later' },
          { id: 'd', label: 'D', text: '`type` and `interface` are functionally identical in every case, so the choice never matters' }
        ],
        correctOptionId: 'b',
        explanation:
          '`type` can alias unions and other non-object type expressions that `interface` cannot express, while `interface` reads more naturally for object shapes and supports declaration merging.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-01-mcq-02',
        question:
          'What does typing a value `any` specifically disable, according to the lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Nothing — `any` is purely cosmetic and has no effect on compile-time checking' },
          { id: 'b', label: 'B', text: 'All compile-time checking on that value — it can be assigned, called, or have any property accessed with zero verification, deferring the error TypeScript would have caught to runtime instead' },
          { id: 'c', label: 'C', text: 'Only the ability to call methods on the value, while property access remains checked' },
          { id: 'd', label: 'D', text: '`any` only affects values returned from third-party libraries, never your own code' }
        ],
        correctOptionId: 'b',
        explanation:
          '`any` is a total escape hatch from the type system for that value, not a partial one — every operation on it compiles regardless of correctness, which is exactly why it\'s compared to a blanket `# type: ignore`.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-01-mcq-03',
        question:
          'Why does the scenario\'s `parseOrder` function perform explicit runtime checks instead of casting the raw response directly to `Order` with `as Order`?',
        options: [
          { id: 'a', label: 'A', text: '`as Order` is a syntax error in TypeScript and would never compile' },
          { id: 'b', label: 'B', text: 'A cast with `as` compiles cleanly and silently trusts the shape is correct — a malformed response would flow into the UI as if valid, deferring the real failure to some unrelated line deep in a component instead of catching it at the parse boundary' },
          { id: 'c', label: 'C', text: 'Runtime checks are required by the TypeScript compiler for every cast, with no way to opt out' },
          { id: 'd', label: 'D', text: 'Casting with `as` is functionally identical to a runtime check, so the choice makes no practical difference' }
        ],
        correctOptionId: 'b',
        explanation:
          '`as` is a compile-time-only assertion with no runtime effect — it silences the type checker without verifying anything, which is exactly the risk `parseOrder`\'s explicit checks are designed to catch at the boundary instead.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-01-mcq-04',
        question:
          'Why does the `Order` interface type `status` as `"created" | "paid" | "shipped" | "cancelled"` rather than a plain `string`?',
        options: [
          { id: 'a', label: 'A', text: 'TypeScript does not allow plain `string` as a field type under any circumstances' },
          { id: 'b', label: 'B', text: 'A plain `string` would let any arbitrary text compile as a valid status, while the literal union lets the compiler catch a typo or an invalid status value at compile time' },
          { id: 'c', label: 'C', text: 'A literal union is only a documentation comment with no actual compile-time effect' },
          { id: 'd', label: 'D', text: 'This choice has no bearing on what values the compiler will accept' }
        ],
        correctOptionId: 'b',
        explanation:
          'A string-literal union narrows the accepted values to exactly the known set, catching an invalid or misspelled status at compile time instead of allowing any string through unchecked.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-01-mcq-05',
        question:
          'How does the lesson connect treating `any` usage as "a deliberate, justified exception, not a default" to a habit from the Python toolchain lessons?',
        options: [
          { id: 'a', label: 'A', text: 'The two concepts are unrelated; the comparison is purely coincidental phrasing' },
          { id: 'b', label: 'B', text: 'It\'s the same discipline as reviewing an unreviewed `# noqa` lint suppression — both silence a safety tool, and both should require an explicit, reviewed justification rather than being reached for by default under pressure' },
          { id: 'c', label: 'C', text: '`# noqa` and `any` are the exact same language feature shared between Python and TypeScript' },
          { id: 'd', label: 'D', text: 'This comparison implies TypeScript should never be used unless mypy is also present in the same project' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both `any` and an unreviewed lint suppression silence a safety mechanism the tooling exists to enforce, and both should be treated as an explicit, justified exception rather than a convenient default.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-01-mcq-06',
        question:
          'Why is a discriminated union (`{ status: "success"; transactionId }` vs. `{ status: "failed"; reason }`) safer than one `PaymentResult` interface with both fields marked optional?',
        options: [
          { id: 'a', label: 'A', text: 'Discriminated unions are purely a stylistic choice with no effect on what the compiler can verify' },
          { id: 'b', label: 'B', text: 'With a discriminated union, switching on `status` lets TypeScript narrow the type automatically inside each branch, guaranteeing `transactionId` exists only in the success branch — an all-optional interface would compile even if both or neither field were present, with no such guarantee' },
          { id: 'c', label: 'C', text: 'An all-optional interface is strictly safer because it allows more possible shapes' },
          { id: 'd', label: 'D', text: 'TypeScript cannot narrow types inside a switch statement under any circumstances' }
        ],
        correctOptionId: 'b',
        explanation:
          'The discriminant field lets the compiler prove which fields are guaranteed present in each branch, closing off the invalid states (both fields present, or neither) that an all-optional interface would silently allow.'
      }
    ]
  },
  'fde-curriculum/full-stack-ai-frontends/02-react-essentials-for-ai-apps': {
    conceptChecks: [
      {
        id: 'lesson-fde-full-stack-ai-frontends-02-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — USESTATE MECHANICS & RE-RENDER SCHEDULING',
        question:
          'What actually happens when you call a `useState` setter function?',
        options: [
          { id: 'a', label: 'A', text: 'The state variable is mutated directly in memory, and the DOM updates automatically as a side effect of that mutation' },
          { id: 'b', label: 'B', text: 'React schedules the component function to re-run with the new value, producing a new UI tree that React diffs against the previous one and updates in the browser — it does not mutate anything in place' },
          { id: 'c', label: 'C', text: 'Nothing happens until the component\'s next scheduled render occurs on a fixed timer' },
          { id: 'd', label: 'D', text: 'The setter immediately re-renders every component in the application, not just the one that called it' }
        ],
        correctOptionId: 'b',
        explanation:
          'The setter\'s job is to schedule a re-render, not to mutate — the component function re-runs, produces new UI, and React reconciles that against what\'s currently on screen.',
        incorrectExplanation:
          'React uses a declarative state model rather than direct in-memory mutation or polling timers.',
        hint: 'Calling the setter schedules React to re-run the component function with updated state and diff the resulting UI tree.'
      },
      {
        id: 'lesson-fde-full-stack-ai-frontends-02-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — USEEFFECT DEPENDENCY ARRAY CONTRACT',
        question:
          'What does the lesson say the `useEffect` dependency array actually represents?',
        options: [
          { id: 'a', label: 'A', text: 'An optional performance hint that has no bearing on program correctness' },
          { id: 'b', label: 'B', text: 'A correctness contract stating exactly which values from the surrounding scope the effect depends on — getting it wrong produces real bugs, not just wasted re-renders' },
          { id: 'c', label: 'C', text: 'A list of every state variable in the entire component, regardless of whether the effect uses them' },
          { id: 'd', label: 'D', text: 'A required field that must always be an empty array for the effect to run at all' }
        ],
        correctOptionId: 'b',
        explanation:
          'The dependency array tells React exactly when the effect needs to re-run relative to changing values — an incorrect array (like an empty one on an effect that reads a changing prop) produces stale-data bugs, not merely a performance difference.',
        incorrectExplanation:
          'An empty or missing dependency array when referencing external props or state causes stale closure bugs.',
        hint: 'The dependency array is a correctness contract specifying all captured reactive values the effect synchronizes with.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-02-mcq-01',
        question:
          'Why did `OrderStatus`\'s displayed status stay frozen on the first order even after a different row was selected, in the scenario\'s initial buggy version?',
        options: [
          { id: 'a', label: 'A', text: 'The order-management API itself was broken and always returned the same order regardless of the ID requested' },
          { id: 'b', label: 'B', text: 'The effect had an empty `[]` dependency array, so it only ran once on initial mount and never re-ran to fetch data for the new `orderId`, even though the prop itself had changed' },
          { id: 'c', label: 'C', text: 'React does not support re-rendering a component when its props change' },
          { id: 'd', label: 'D', text: 'The component was never actually re-rendered at all after the initial mount, for any reason' }
        ],
        correctOptionId: 'b',
        explanation:
          'An empty dependency array means "run once, on mount" regardless of later prop changes — the effect simply never re-runs to notice the new `orderId`, which is the exact mechanism behind the frozen display.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-02-mcq-02',
        question:
          'What specific problem does the `AbortController` cleanup function in `useEffect` solve in the `OrderStatus` example?',
        options: [
          { id: 'a', label: 'A', text: 'It permanently disables the fetch effect from ever running again for the rest of the component\'s lifetime' },
          { id: 'b', label: 'B', text: 'It cancels an in-flight fetch when `orderId` changes or the component unmounts, preventing a slow response for a previously selected (now abandoned) order from overwriting the state of whatever is currently selected' },
          { id: 'c', label: 'C', text: 'It makes the fetch request complete faster by reducing network latency' },
          { id: 'd', label: 'D', text: 'Cleanup functions in useEffect have no functional purpose and exist only for code readability' }
        ],
        correctOptionId: 'b',
        explanation:
          'Without cancellation, a slow response tied to a stale `orderId` can resolve after the user has already moved on, silently overwriting the currently displayed order with outdated data — the cleanup function prevents exactly that race condition.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-02-mcq-03',
        question:
          'How does the lesson connect `useEffect`\'s cleanup function to a principle from the earlier async Python lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The two concepts share no meaningful relationship beyond both involving asynchronous code' },
          { id: 'b', label: 'B', text: 'Both describe the same discipline — not leaving dangling work you can\'t cancel — applied to cancelling an in-flight fetch in React versus cancelling a stalled coroutine in Python' },
          { id: 'c', label: 'C', text: 'React\'s cleanup function and Python\'s `asyncio` cancellation are literally the same API shared across languages' },
          { id: 'd', label: 'D', text: 'This connection only applies when the fetch request specifically targets a Python backend' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both mechanisms exist to prevent stale, uncancellable work from corrupting state after it\'s no longer relevant — the specific APIs differ, but the underlying discipline is identical.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-02-mcq-04',
        question:
          'Per the lesson, when should a value NOT be stored with `useState`?',
        options: [
          { id: 'a', label: 'A', text: 'Never — every value used anywhere in a component must always be stored in useState' },
          { id: 'b', label: 'B', text: 'When it never needs to trigger a re-render — for example, a value only read inside an event handler — putting it in `useState` just adds unnecessary re-renders with no benefit' },
          { id: 'c', label: 'C', text: 'Only when the value is a string, since useState is reserved for numeric and boolean values' },
          { id: 'd', label: 'D', text: '`useState` should be avoided entirely in favor of plain variables in all cases' }
        ],
        correctOptionId: 'b',
        explanation:
          '`useState` exists specifically to trigger re-renders when a value changes — a value that never needs to be reflected in the rendered UI doesn\'t benefit from that mechanism and shouldn\'t pay its cost.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-02-mcq-05',
        question:
          'What motivates extracting fetch-and-parse logic into a custom hook like `useOrder`, per the lesson\'s comparison to the Python decorators lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Custom hooks are a purely cosmetic renaming convention with no functional benefit over copy-pasting the same code' },
          { id: 'b', label: 'B', text: 'The same motivation as factoring shared logic into a decorator in Python — avoiding duplicating the same stateful logic across multiple call sites, even though the underlying mechanism (a hook versus a decorator) is different' },
          { id: 'c', label: 'C', text: 'React requires all `useEffect` calls to be wrapped in a custom hook before the application will compile' },
          { id: 'd', label: 'D', text: 'Extracting a custom hook changes the underlying re-render behavior of the components that use it' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both custom hooks and decorators solve the same underlying problem — stopping duplicated logic from being copy-pasted across call sites — just through mechanisms specific to their respective languages.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-02-mcq-06',
        question:
          'Why does the suggested extension add explicit loading and error states to `useOrder`, rather than only returning the fetched `order` value?',
        options: [
          { id: 'a', label: 'A', text: 'Loading and error states are required by TypeScript\'s type checker for any function using useState' },
          { id: 'b', label: 'B', text: 'Without them, consuming components have no way to distinguish "still fetching," "fetch failed," and "no order exists" from each other, and can only render a blank screen instead of a spinner or a meaningful error message' },
          { id: 'c', label: 'C', text: 'This addition has no effect on what a consuming component is able to render' },
          { id: 'd', label: 'D', text: 'A hook returning only the happy-path value is strictly better because it\'s simpler for every possible consumer' }
        ],
        correctOptionId: 'b',
        explanation:
          'A hook that only exposes the successful result gives consuming components no signal to distinguish "in progress," "failed," and "genuinely empty," collapsing all three into the same blank rendering.'
      }
    ]
  },
  'fde-curriculum/full-stack-ai-frontends/03-next-js-for-full-stack-ai-apps': {
    conceptChecks: [
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — SERVER COMPONENTS BY DEFAULT',
        question:
          'What is the default component model in the Next.js App Router, before any `"use client"` directive is added?',
        options: [
          { id: 'a', label: 'A', text: 'Every component runs in the browser by default, identical to plain React, unless marked otherwise' },
          { id: 'b', label: 'B', text: 'Every component is a Server Component by default — it runs only on the server, renders to HTML there, and ships zero of its own JavaScript to the browser' },
          { id: 'c', label: 'C', text: 'Components alternate between server and client rendering automatically based on their file size' },
          { id: 'd', label: 'D', text: 'The App Router has no meaningful distinction between server and client execution' }
        ],
        correctOptionId: 'b',
        explanation:
          'Server Components are the App Router\'s default — this is the core shift from plain React, where a component marked `"use client"` opts back into the browser-executed model from the previous lesson.',
        incorrectExplanation:
          'In the Next.js App Router, components default to server execution unless explicitly opted into client rendering.',
        hint: 'Server Components run exclusively on the server and ship zero client-side JavaScript by default.'
      },
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — ROUTE HANDLER AS A BFF TRUST BOUNDARY',
        question:
          'Why does the FDE build a Next.js route handler in front of the FastAPI order-management API rather than having the browser call FastAPI directly?',
        options: [
          { id: 'a', label: 'A', text: 'Browsers are technically incapable of making HTTP requests to any API other than the one that served the page' },
          { id: 'b', label: 'B', text: 'The route handler runs server-side and can hold the FastAPI service\'s internal URL and credentials without exposing them to the browser, and can shape or aggregate the response into exactly what the client needs rather than forwarding it verbatim' },
          { id: 'c', label: 'C', text: 'A route handler is required by Next.js and cannot be omitted under any architecture' },
          { id: 'd', label: 'D', text: 'This choice has no effect on what credentials or data are exposed to the browser' }
        ],
        correctOptionId: 'b',
        explanation:
          'The BFF pattern\'s value is specifically holding a trust boundary — internal credentials and endpoints stay server-side, and the response can be reshaped to expose only what the client is authorized to see.',
        incorrectExplanation:
          'Consider the security implications of exposing backend service URLs, bearer tokens, and raw unshaped database payloads to the client browser.',
        hint: 'A backend-for-frontend (BFF) keeps service secrets server-side and reshapes responses to avoid leaking internal fields.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-mcq-01',
        question:
          'Per the lesson\'s discipline, when should a component be marked `"use client"`?',
        options: [
          { id: 'a', label: 'A', text: 'Every component should be marked "use client" as a safe default to avoid server-rendering bugs' },
          { id: 'b', label: 'B', text: 'Only when it genuinely needs interactivity, browser APIs, or React state — not by habit, and not applied to a whole page just because one button inside it needs a click handler' },
          { id: 'c', label: 'C', text: 'Only components that fetch data should ever be marked "use client"' },
          { id: 'd', label: 'D', text: '"use client" should be applied at the top-level layout file and never on individual leaf components' }
        ],
        correctOptionId: 'b',
        explanation:
          'Pushing the boundary down to the smallest leaf component that genuinely needs it keeps the rest of the tree as zero-JavaScript Server Components — a real reduction in what ships to the browser, not a style preference.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-mcq-02',
        question:
          'How does the lesson connect the Server/Client Component split to a principle from the earlier auth lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The two concepts describe entirely unrelated engineering decisions with no shared principle' },
          { id: 'b', label: 'B', text: 'Both are about deciding what should genuinely run or be exposed to a client the FDE doesn\'t fully trust — keeping secrets and trusted computation server-side is the frontend equivalent of never trusting client-submitted data at face value' },
          { id: 'c', label: 'C', text: 'This connection only applies when the client-submitted data happens to be a JWT specifically' },
          { id: 'd', label: 'D', text: 'Server Components and the auth lesson\'s verification principle are literally the same code, reused verbatim' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both principles are about where trust boundaries should sit — the auth lesson\'s "verify server-side, don\'t trust the client" instinct reappears here as "run and hold secrets server-side, don\'t expose them to a client that could inspect or tamper with them."'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-mcq-03',
        question:
          'In the scenario, why does the checkout route handler\'s response to the browser differ from the FastAPI payments endpoint\'s raw response?',
        options: [
          { id: 'a', label: 'A', text: 'The route handler adds entirely fabricated data to the response that the FastAPI backend never provided' },
          { id: 'b', label: 'B', text: 'The FastAPI response includes an internal-only field (a customer risk score) that has no business reaching the browser, and the route handler strips it before forwarding the rest to the client' },
          { id: 'c', label: 'C', text: 'The route handler and the FastAPI response are always byte-for-byte identical by design, with no reshaping' },
          { id: 'd', label: 'D', text: 'The difference exists only because of a bug, not a deliberate design choice' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the concrete payoff of the BFF pattern — the route handler deliberately reshapes the backend\'s response to expose only what the client needs, keeping an internal field out of the browser entirely.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-mcq-04',
        question:
          'What does the practice loop\'s step 5 (marking the entire order-detail page `"use client"` and comparing bundle sizes) demonstrate?',
        options: [
          { id: 'a', label: 'A', text: 'That "use client" placement has no measurable effect on anything observable in the browser' },
          { id: 'b', label: 'B', text: 'A concrete, measurable increase in client-side JavaScript bundle size when the "use client" boundary is applied too broadly, versus scoping it only to the component that genuinely needs it' },
          { id: 'c', label: 'C', text: 'That marking a whole page "use client" always makes the page render faster' },
          { id: 'd', label: 'D', text: 'That bundle size is unrelated to how many components are marked "use client"' }
        ],
        correctOptionId: 'b',
        explanation:
          'This step exists to make the abstract "push the boundary down" guidance concrete and measurable — an unnecessarily broad client boundary has a real, quantifiable JavaScript cost.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-mcq-05',
        question:
          'In the order-detail page example, why does the Server Component fetch directly using an internal service URL and bearer token, rather than the pattern from the previous lesson\'s `useEffect`-based fetch?',
        options: [
          { id: 'a', label: 'A', text: 'Server Components are technically incapable of ever fetching data, so this distinction does not actually apply' },
          { id: 'b', label: 'B', text: 'Because the fetch happens entirely server-side during rendering, the internal URL and token are never sent to or visible from the browser — a `useEffect` fetch, by contrast, would run in the browser and expose whatever URL and credentials it used' },
          { id: 'c', label: 'C', text: 'There is no meaningful difference in what\'s exposed to the browser between the two approaches' },
          { id: 'd', label: 'D', text: '`useEffect`-based fetching is strictly forbidden anywhere in a Next.js application' }
        ],
        correctOptionId: 'b',
        explanation:
          'The defining advantage of a Server Component fetch here is exactly what stays hidden from the browser — credentials and internal URLs used during server-side rendering never appear in client-visible network traffic, unlike a client-side `useEffect` fetch.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-mcq-06',
        question:
          'Per the suggested extension, what is the trade-off between a Server Action tied to one form and a route handler used for checkout?',
        options: [
          { id: 'a', label: 'A', text: 'Server Actions and route handlers are functionally identical with no trade-off between them' },
          { id: 'b', label: 'B', text: 'A Server Action is more tightly coupled to the one form calling it, which is acceptable for a simple, single-purpose action; a route handler requires more explicit wiring but is reusable across multiple callers, which matters for something like checkout that may need to be called from more than one place' },
          { id: 'c', label: 'C', text: 'Route handlers can only be called from Server Components, while Server Actions can only be called from Client Components' },
          { id: 'd', label: 'D', text: 'A Server Action always requires more code than an equivalent route handler' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a genuine reusability-versus-simplicity trade-off — a Server Action\'s tight coupling to a single form is fine for a narrow case, while a route handler\'s more explicit interface pays off when multiple callers need the same endpoint.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-03-mcq-07',
        question:
          'Why is it insufficient to assume a component is a Server Component just because it lives under the `app/` directory with no other information?',
        options: [
          { id: 'a', label: 'A', text: 'Files under `app/` are always Client Components regardless of any directive present' },
          { id: 'b', label: 'B', text: 'Any file under `app/` can still opt into being a Client Component with an explicit `"use client"` directive at the top — the directory alone doesn\'t determine which model a given file uses' },
          { id: 'c', label: 'C', text: 'The `app/` directory has no relationship to the Server/Client Component distinction at all' },
          { id: 'd', label: 'D', text: 'Only files named `page.tsx` can ever be Server Components; all others default to client' }
        ],
        correctOptionId: 'b',
        explanation:
          'The Server Component default applies per-file, and any specific file can override it with `"use client"` — the directory location alone is not sufficient information to know which model a given component actually uses.'
      }
    ]
  },
  'fde-curriculum/full-stack-ai-frontends/04-vercel-ai-sdk-and-streaming-uis': {
    conceptChecks: [
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — LLM STREAMING AS ONE-DIRECTIONAL PUSH',
        question:
          'Why does the lesson describe streaming an LLM response as "conceptually the exact same pattern" as the SSE mechanism from the earlier real-time lesson?',
        options: [
          { id: 'a', label: 'A', text: 'Streaming and SSE are literally the same network protocol with no conceptual distinction being made' },
          { id: 'b', label: 'B', text: 'Both are a one-directional, server-to-client push where the client only receives updates and never needs to send anything back over the same channel mid-stream — the payload differs (tokens vs. an order-status change), but the shape of the problem is identical' },
          { id: 'c', label: 'C', text: 'This comparison is inaccurate; LLM streaming actually requires bidirectional communication like WebSockets' },
          { id: 'd', label: 'D', text: 'The comparison only holds if the LLM provider happens to be the same company that built SSE' }
        ],
        correctOptionId: 'b',
        explanation:
          'The pattern match is specifically about directionality and need — both are cases where the client is purely a receiver of incremental updates, which is exactly the condition the earlier lesson identified as SSE\'s genuine fit.',
        incorrectExplanation:
          'Compare the communication flow requirements: does the client need to send data back upstream during generation, or only receive incoming chunks?',
        hint: 'Both LLM token streaming and SSE represent unidirectional server-to-client data delivery.'
      },
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — API KEY ISOLATION & BOUNDARY DISCIPLINE',
        question:
          'Why must the model provider\'s API key live in the `streamText` route handler rather than in the `useChat` client component?',
        options: [
          { id: 'a', label: 'A', text: '`useChat` technically cannot make any network requests at all, regardless of where the key lives' },
          { id: 'b', label: 'B', text: '`streamText` is exclusively a server-side concept, and the route handler is the only place the key stays hidden from the browser — putting it in the client component would expose it to anyone inspecting the browser\'s network requests or bundled code' },
          { id: 'c', label: 'C', text: 'There is no actual difference in exposure risk between the two locations' },
          { id: 'd', label: 'D', text: 'API keys are only sensitive when used with GPT-4-class models, not smaller ones' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is the same BFF discipline from the Next.js lesson applied to a provider API key — anything the browser can inspect is exposed, so the key must stay entirely within server-side code the browser never receives.',
        incorrectExplanation:
          'Any secret included in client-side code or browser requests is fully inspectable by the user.',
        hint: 'Client bundles and browser network traffic are publicly visible; provider secrets must remain strictly server-side.'
      }
    ],
    architecture: {
      id: 'lesson-fde-full-stack-ai-frontends-04-streaming-ui-lifecycle',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — VERCEL AI SDK STREAMING ARCHITECTURE',
      boundaryLabel: 'SERVER-SIDE SECRETS & STREAMING BOUNDARY',
      boundaryText:
        'The route handler isolates the LLM provider API key and injects grounded order data server-side, pushing token chunks over an SSE stream to useChat for incremental UI rendering.',
      nodes: [
        { id: 'client-input', label: 'User Message (useChat UI)', kind: 'input' },
        { id: 'route-handler', label: 'Next.js BFF Route Handler (/api/support-chat)', kind: 'service' },
        { id: 'order-api', label: 'FastAPI Backend (Order Data Grounding)', kind: 'adapter' },
        { id: 'llm-provider', label: 'streamText & OpenAI/Anthropic API Key', kind: 'adapter' },
        { id: 'stream-pipe', label: 'toUIMessageStreamResponse (SSE Stream)', kind: 'boundary', highlighted: true },
        { id: 'client-render', label: 'Incremental Token Render & Interruption Recovery', kind: 'output' }
      ]
    },
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-mcq-01',
        question:
          'Why does streaming a response with `streamText` improve perceived latency, even though the total time to the last token is roughly the same as waiting for the full response?',
        options: [
          { id: 'a', label: 'A', text: 'Streaming makes the model itself generate tokens measurably faster than it would for a non-streamed request' },
          { id: 'b', label: 'B', text: 'The user sees the first words of the response within a second or two instead of staring at a blank UI for the full generation time, even though the actual total generation duration is unchanged' },
          { id: 'c', label: 'C', text: 'Streaming has no effect on what the user perceives; the lesson\'s claim is inaccurate' },
          { id: 'd', label: 'D', text: 'Streaming only improves latency for responses shorter than a single sentence' }
        ],
        correctOptionId: 'b',
        explanation:
          'The benefit is specifically about perceived latency, not actual total generation time — visible progress starting immediately changes the user\'s experience of waiting, even when the underlying total duration is unchanged.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-mcq-02',
        question:
          'Why does the lesson argue a chat UI needs to distinguish a failure before any tokens arrive from a failure partway through a streamed response?',
        options: [
          { id: 'a', label: 'A', text: 'There is no meaningful difference between the two failure types, and both should be handled identically' },
          { id: 'b', label: 'B', text: 'A mid-stream failure has already produced real, partial content the user can see value in, and the UI should preserve and mark it as interrupted with a retry option — silently discarding it or hanging indefinitely are both worse outcomes than a clean pre-stream failure with no content to lose' },
          { id: 'c', label: 'C', text: 'A mid-stream failure is always the user\'s fault, unlike a pre-stream failure' },
          { id: 'd', label: 'D', text: 'Mid-stream failures are impossible to detect programmatically, so no distinct handling can be built' }
        ],
        correctOptionId: 'b',
        explanation:
          'The key distinction is that a mid-stream failure has already produced something worth preserving — treating it the same as a clean failure with nothing generated yet either wastes that partial content or leaves the UI in a confusing, unresolved state.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-mcq-03',
        question:
          'Why does the scenario\'s route handler inject the customer\'s actual order status into the system prompt before calling `streamText`?',
        options: [
          { id: 'a', label: 'A', text: 'Injecting order data into the prompt is required by the Vercel AI SDK\'s API and has no bearing on answer quality' },
          { id: 'b', label: 'B', text: 'Grounding the assistant\'s answers in real order data, rather than letting the model guess or hallucinate, is the entire point of embedding it in this specific product rather than pointing the customer at a generic chatbot' },
          { id: 'c', label: 'C', text: 'This step is optional polish with no meaningful effect on whether the assistant\'s answers are accurate' },
          { id: 'd', label: 'D', text: 'The model would refuse to respond at all without order data present in the prompt' }
        ],
        correctOptionId: 'b',
        explanation:
          'The scenario is explicit that grounding in real, injected order data (rather than a generic response) is what makes this assistant valuable specifically because it\'s embedded in the product with access to real account data.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-mcq-04',
        question:
          'What does the `useChat` hook manage on the client side?',
        options: [
          { id: 'a', label: 'A', text: 'The model provider\'s API key and the actual LLM inference itself' },
          { id: 'b', label: 'B', text: 'The chat\'s message history in state, sending new messages to the configured route handler, and incrementally updating the UI as tokens of the streamed response arrive' },
          { id: 'c', label: 'C', text: 'Database queries against the order-management backend, bypassing the route handler entirely' },
          { id: 'd', label: 'D', text: 'Nothing related to state — it is a purely presentational, stateless function' }
        ],
        correctOptionId: 'b',
        explanation:
          '`useChat` is exclusively a client-side state and lifecycle manager — message history, sending, and incremental rendering — while inference and provider credentials stay entirely server-side.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-mcq-05',
        question:
          'How does the lesson connect handling a mid-stream failure gracefully to a principle from the earlier Building the Demo Frontend lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The two lessons describe entirely unrelated concerns with no shared principle' },
          { id: 'b', label: 'B', text: 'Both describe the same trust-building principle — showing a real, handled failure state is more credible than either always showing a flawless happy path or failing in a way that looks like the whole application broke' },
          { id: 'c', label: 'C', text: 'This connection only applies if the demo frontend and the chat assistant use the exact same underlying API' },
          { id: 'd', label: 'D', text: 'The demo frontend lesson explicitly forbids ever showing an error state in a production application' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both lessons make the same point at different layers — a system that only ever shows success (or that fails in a confusing way) is less credible than one that demonstrably handles a real failure gracefully and visibly.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-mcq-06',
        question:
          'What is the role of a method like `toUIMessageStreamResponse()` on the `streamText` result, called inside the route handler?',
        options: [
          { id: 'a', label: 'A', text: 'It stores the entire conversation permanently in a database on every call' },
          { id: 'b', label: 'B', text: 'It converts the SDK\'s internal stream representation into an HTTP response using a protocol the client-side `useChat` hook understands, shaping what the client actually receives' },
          { id: 'c', label: 'C', text: 'It synchronously blocks the route handler until the full response has finished generating' },
          { id: 'd', label: 'D', text: 'It has no functional purpose and exists purely for TypeScript type inference' }
        ],
        correctOptionId: 'b',
        explanation:
          'This method is the boundary-shaping step — converting the server-side stream into the exact wire format the client hook expects, mirroring the previous lesson\'s route-handler-as-boundary pattern.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-04-mcq-07',
        question:
          'Why does the suggested extension propose visually distinguishing a message grounded in injected order data from one the model answered without needing any?',
        options: [
          { id: 'a', label: 'A', text: 'This distinction is purely a visual preference with no bearing on how much a customer should trust a given answer' },
          { id: 'b', label: 'B', text: 'So the customer can see when the assistant\'s answer is backed by their actual account data versus general knowledge, which is a transparency signal about how much to trust that specific answer' },
          { id: 'c', label: 'C', text: 'The Vercel AI SDK requires this visual distinction as part of its API contract' },
          { id: 'd', label: 'D', text: 'Answers without injected order data are always factually wrong and should be hidden from the user' }
        ],
        correctOptionId: 'b',
        explanation:
          'This is a transparency signal, not a stylistic flourish — it lets the customer calibrate trust in a specific answer based on whether it\'s grounded in their real data or general model knowledge, previewing the next lesson\'s deeper coverage of this concern.'
      }
    ]
  },
  'fde-curriculum/full-stack-ai-frontends/05-ai-product-ux-and-customer-facing-polish': {
    conceptChecks: [
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-concept-check-01',
        eyebrow: 'CONCEPT CHECK 01 — AI OUTPUT UNCERTAINTY & TRUST POSTURE',
        question:
          'Why does the lesson argue "the response loaded successfully" and "the response is trustworthy" are two different things a production AI feature needs to communicate separately?',
        options: [
          { id: 'a', label: 'A', text: 'These two properties are always identical for any API response, AI-generated or not, making the distinction meaningless' },
          { id: 'b', label: 'B', text: 'An LLM response can be confidently wrong while looking exactly as polished as a correct one, unlike a typical CRUD response that\'s either correct or visibly errored — so a UI that only signals "it loaded" gives the user no way to gauge whether to trust the content itself' },
          { id: 'c', label: 'C', text: 'LLM responses are never wrong once they have successfully streamed to completion' },
          { id: 'd', label: 'D', text: 'This distinction only matters for responses longer than a few sentences' }
        ],
        correctOptionId: 'b',
        explanation:
          'The specific risk named is a confidently wrong but fluent-looking answer — since it\'s indistinguishable in polish from a correct one, "it rendered" carries no information about whether it should be trusted.',
        incorrectExplanation:
          'Unlike deterministic database errors that fail with status codes, LLM hallucinations appear syntactically and visually identical to correct responses.',
        hint: 'LLMs can generate fluent, grammatical, yet factually incorrect output with high confidence.'
      },
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-concept-check-02',
        eyebrow: 'CONCEPT CHECK 02 — REVERSIBILITY & HUMAN-IN-THE-LOOP CONTROL',
        question:
          'Why does the fixed `DraftReply` design require an explicit agent click to send, rather than sending the model\'s draft automatically once streaming completes?',
        options: [
          { id: 'a', label: 'A', text: 'Auto-sending is technically impossible to implement with the Vercel AI SDK' },
          { id: 'b', label: 'B', text: 'An AI-suggested action is competing with the ground truth the user actually has, not an authoritative instruction — collapsing "the model suggested this" and "this is now sent" removes the human review step that caught the scenario\'s stale-order-reference error before it reached a customer' },
          { id: 'c', label: 'C', text: 'Requiring a manual click has no relationship to catching errors in the assistant\'s output' },
          { id: 'd', label: 'D', text: 'The compose box exists purely as a stylistic choice with no bearing on the incident described in the scenario' }
        ],
        correctOptionId: 'b',
        explanation:
          'The scenario\'s incident happened specifically because auto-send removed the review step — the fix restores a deliberate human confirmation boundary between the model\'s suggestion and the action actually taken.',
        incorrectExplanation:
          'Review the scenario where an assistant referenced a stale order number and why an automated send caused a customer incident.',
        hint: 'AI suggestions are drafts that require human review and confirmation before initiating irreversible real-world actions.'
      }
    ],
    practiceQuestions: [
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-mcq-01',
        question:
          'How does this lesson connect to the scope boundary explicitly drawn in the earlier Building the Demo Frontend lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The demo frontend lesson and this lesson describe entirely unrelated, non-overlapping concerns' },
          { id: 'b', label: 'B', text: 'That lesson deliberately deferred "an actual production-grade frontend (React, TypeScript, real UX)" to this later module, and this lesson is specifically where that deferred production-UX work happens, applied to AI-assisted features' },
          { id: 'c', label: 'C', text: 'The demo frontend lesson said a production frontend would never be necessary for this course' },
          { id: 'd', label: 'D', text: 'This lesson replaces the demo frontend with an identical plain-HTML client, just restyled' }
        ],
        correctOptionId: 'b',
        explanation:
          'This lesson explicitly picks up the deferred scope the demo-frontend lesson named — a real production frontend with genuine UX — and applies it specifically to the module\'s AI-assisted features.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-mcq-02',
        question:
          'How does the lesson connect the "system suggested" versus "system did" UI boundary to the earlier rate-limiting lesson?',
        options: [
          { id: 'a', label: 'A', text: 'The two lessons describe identical technical mechanisms with no conceptual distinction' },
          { id: 'b', label: 'B', text: 'Both are about maintaining explicit, visible boundaries around automated behavior — rate limiting bounds request volume explicitly rather than letting it run unchecked, and this lesson bounds an AI action\'s actual effect (sending, applying) behind an explicit confirmation rather than letting generation alone trigger it' },
          { id: 'c', label: 'C', text: 'Rate limiting and AI action review solve the exact same problem using the same code' },
          { id: 'd', label: 'D', text: 'This connection only applies to systems that use both an AI assistant and a rate limiter simultaneously' }
        ],
        correctOptionId: 'b',
        explanation:
          'Both principles are about explicit, visible boundaries on automated behavior\'s blast radius — applied to request volume in one case and to an AI suggestion\'s real-world effect in the other.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-mcq-03',
        question:
          'Why does the lesson say the previous lesson\'s token-by-token streaming display is itself part of the AI UX solution, not just a technical implementation detail?',
        options: [
          { id: 'a', label: 'A', text: 'Streaming display has no relationship to user experience; it exists purely for backend performance reasons' },
          { id: 'b', label: 'B', text: 'Showing partial, growing text as it arrives is both an accurate representation of what\'s actually happening and a materially better experience than a blank screen followed by a sudden wall of text — a generic spinner undersells what\'s really occurring during generation' },
          { id: 'c', label: 'C', text: 'A blank loading spinner is always a strictly better experience than showing partial content' },
          { id: 'd', label: 'D', text: 'Streaming display is only relevant for responses under one sentence in length' }
        ],
        correctOptionId: 'b',
        explanation:
          'The lesson frames the streaming display as doing real UX work — accurately representing in-progress generation — rather than treating it as an incidental side effect of the streaming architecture from the previous lesson.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-mcq-04',
        question:
          'Why does the lesson recommend a "polite" ARIA live region setting for streaming text, rather than a setting that interrupts on every token?',
        options: [
          { id: 'a', label: 'A', text: 'ARIA live regions have no effect on how screen readers announce dynamically updating content' },
          { id: 'b', label: 'B', text: 'Announcing every individual token as it streams in would make the experience unusable rather than merely unpolished for a screen-reader user, so a "polite" setting queues updates sensibly instead of interrupting continuously' },
          { id: 'c', label: 'C', text: 'The "polite" setting is required by the Vercel AI SDK\'s API and cannot be configured differently' },
          { id: 'd', label: 'D', text: 'Accessibility settings for streamed text are a cosmetic nicety with no functional consequence for real users' }
        ],
        correctOptionId: 'b',
        explanation:
          'The concrete, checkable requirement here is choosing an announcement mode that doesn\'t overwhelm a screen-reader user with rapid, per-token interruptions — "polite" is the setting that avoids that specific failure mode.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-mcq-05',
        question:
          'Why is showing "based on your order #4821, placed March 3rd" alongside an assistant\'s answer described as a better trust posture than showing the answer alone?',
        options: [
          { id: 'a', label: 'A', text: 'This detail has no effect on how much a user trusts the answer; it is purely decorative' },
          { id: 'b', label: 'B', text: 'It lets the user cross-check the claim against something concrete, rather than asking them to take the assistant\'s word for it with no way to verify the answer against the underlying data' },
          { id: 'c', label: 'C', text: 'Source attribution is only meaningful when the underlying order data is itself incorrect' },
          { id: 'd', label: 'D', text: 'Adding this detail makes the assistant\'s answer generate measurably faster' }
        ],
        correctOptionId: 'b',
        explanation:
          'Attribution gives the user a concrete, checkable anchor for the claim, converting "trust the assistant" into "verify against something specific" — a materially stronger trust posture.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-mcq-06',
        question:
          'Per the practice loop\'s final review step, what distinguishes genuine production-readiness work in the finished console from mere polish?',
        options: [
          { id: 'a', label: 'A', text: 'Any visual change to the UI counts equally as production-readiness work, regardless of what problem it solves' },
          { id: 'b', label: 'B', text: 'Additions like typed data, componentized UI, streaming AI assistance, and explicit review boundaries around AI actions are each specifically tied to correctness, trust, or safety concerns the demo frontend never needed to address — not cosmetic changes that could have waited' },
          { id: 'c', label: 'C', text: 'Production-readiness is determined solely by how much code a given change adds to the project' },
          { id: 'd', label: 'D', text: 'There is no meaningful distinction between polish and production-readiness work; the terms are interchangeable' }
        ],
        correctOptionId: 'b',
        explanation:
          'The review step asks specifically whether each addition addresses a real correctness, trust, or safety gap the demo frontend didn\'t need to solve — that\'s the test for genuine production-readiness versus cosmetic polish.'
      },
      // LLM_GENERATED
      {
        id: 'lesson-fde-full-stack-ai-frontends-05-mcq-07',
        question:
          'What is the purpose of the suggested extension\'s thumbs up/down feedback control on each AI-drafted reply?',
        options: [
          { id: 'a', label: 'A', text: 'To automatically retrain the underlying model in real time based on each individual click' },
          { id: 'b', label: 'B', text: 'To log enough context (order reference, draft text, any agent edit) to later audit which kinds of drafts the assistant tends to get wrong, informing future improvements to the grounding logic from the previous lesson' },
          { id: 'c', label: 'C', text: 'The feedback control has no downstream use; it exists only to make agents feel heard' },
          { id: 'd', label: 'D', text: 'To immediately block the assistant from generating any further drafts after a single negative rating' }
        ],
        correctOptionId: 'b',
        explanation:
          'The extension frames the feedback as an auditable data source for future improvement, not an immediate automated action — it\'s meant to surface patterns in what the assistant tends to get wrong.'
      }
    ]
  }
};

export function getLessonInteractions(courseSlug, moduleSlug, lessonSlug) {
  return lessonInteractions[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonInteractions;
