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
    architecture: {
      id: 'lesson-1-trip-state-flow',
      eyebrow: 'PRACTICAL BACKEND SCENARIO — RIDE-SHARING TRIP STATE MANAGEMENT',
      boundaryLabel: 'ENCAPSULATED STATE BOUNDARY',
      boundaryText:
        'The Trip entity validates and mutates status internally; services coordinate workflows without directly mutating fields.',
      nodes: [
        { id: 'request', label: 'Passenger Cancel Request', kind: 'input' },
        { id: 'controller', label: 'TripController', kind: 'service' },
        { id: 'service', label: 'CancellationService', kind: 'service' },
        { id: 'boundary', label: 'Trip.cancelTrip() (Entity Invariant)', kind: 'boundary', highlighted: true },
        { id: 'notification', label: 'NotificationService', kind: 'adapter' },
        { id: 'fare', label: 'FareService', kind: 'adapter' },
        { id: 'output', label: 'Guarded Trip State (Cancelled)', kind: 'output' }
      ]
    },
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
