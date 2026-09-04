# Java/Spring Course Reference Map

**Reference course:** [Java Low-Level Design & Spring Architecture](https://neuralascent.top/chapters/java-spring-lld)

**Observed on:** 2026-09-01

The course currently presents 10 modules and 88 lessons. We will use it as a just-in-time reference for the rebuild. A roadmap phase does not require completing an entire module first; we will touch the smallest relevant concept, implement it, test it, and then return for deeper lessons when the project creates a real need.

## Course modules at a glance

| Module | Main concept area |
|---|---|
| 1. OOP Foundations & Design Principles | Classes, encapsulation, inheritance, polymorphism, interfaces |
| 2. Concurrency & Multithreading | Threads, executors, futures, synchronization, locks, semaphores, structured concurrency |
| 3. Advanced Java, Collections & Streams | Generics, type erasure, collections, sorting, lambdas, streams, exceptions |
| 4. Design Principles & Patterns | SOLID, creational/structural/behavioral patterns, UML, extensibility |
| 5. Applied Design & Machine Coding | Design and implement complete systems such as TicTacToe, Parking Lot, BookMyShow, Splitwise, and Hotel Management |
| 6. Spring Boot & Enterprise Architecture | IoC/DI, Spring Data JPA, PostgreSQL, REST, validation, security, distributed systems |
| 7. Applied Design & Machine Coding | Design-first and code-first machine-coding practice across multiple systems |
| 8. AI-First Backend Capstone — Primer | Backend development with AI assistance, Git, Spring APIs/MVC, third-party AI APIs, JPA, testing, authentication, AWS |
| 9. AI-First Backend Capstone — Advance | Resilience, UUIDs/inheritance, mocking/testing, JWT/OAuth2, AWS networking, search, payments, Redis/Kafka, Spring Cloud, Docker |
| 10. Production-Ready AI-Enabled System | Prompt engineering, chat agents, receipt/AI processing, and an AI backend capstone |

## Roadmap phase alignment

| Roadmap phase | What we build | Course concepts we will reference |
|---|---|---|
| 0. Understand the existing application | Trace browser → API → database behavior | Module 8: backend systems, Git, AI-assisted development; Module 6: REST/API vocabulary |
| 1. Smallest possible website | React calls a Spring Boot `/api/hello` endpoint | Module 8: Spring Framework and APIs, MVC and requests; Module 6: IoC and dependency injection |
| 2. First database connection | Add a small `lesson` table and read endpoints | Module 6: Spring Data JPA and PostgreSQL; Module 8: JPA, repositories, and queries |
| 3. Basic login | Register, login, logout, current user, server session | Module 6: REST validation/security; Module 8: authentication vs authorization and `UserAuthService`; Module 9: JWT/OAuth2 as later alternatives |
| 4. Java LLD chapters | Build the first real curriculum hierarchy | Module 1: OOP foundations; Module 3: collections/streams; Module 4: SOLID and patterns |
| 5. Expand curriculum hierarchy | Add verticals, courses, modules, lessons, problems, resources | Module 1: relationships and object modeling; Module 3: generics/collections; Module 6: JPA relationships and REST DTOs |
| 6. User progress | Add user-scoped completion and reopen behavior | Module 6: persistence, validation, security, and transactions; Module 3: enums, collections, streams; Module 9: concurrency and resilience concepts where needed |
| 7. Exercises and code state | Store exercise files, learner code, results, and attempts | Module 5 or 7: machine-coding workflow; Module 6: API design; Module 8/9: testing and mocking |
| 8. Docker Java execution | Build workspace, run tests, capture and normalize results | Module 9: Docker for backend services; Module 2: executors, bounds, synchronization; Module 8/9: testing and failure handling |
| 9. Knowledge Atlas and learning graph | Model concepts, prerequisites, relations, and next lessons | Module 1: interfaces and object modeling; Module 3: generics and stream transformations; Module 4: UML and extensible design; Module 9: search and semantic-search introduction |
| 10. .NET behavioral parity | Compare Java and .NET behavior through contracts and tests | Module 8: Git and disciplined AI-assisted development; Module 8/9: unit testing, mocking, and advanced testing strategies; Module 6: REST contracts |
| 11. Target Java architecture | Refactor into business-capability packages | Module 4: SOLID, Factory, Adapter, Facade, Decorator, and behavioral patterns; Module 6: enterprise architecture; Module 9: Spring Cloud concepts when justified |
| 12. AI gateway | Add provider abstraction, quotas, usage, cost, and idempotency | Module 1/4: interfaces, Adapter, Factory, Strategy, Decorator; Module 8: third-party APIs and LLM services; Module 9: resilience, Redis/Kafka, and distributed service concepts |
| 13. Current-context tutor | Resolve lesson/exercise context and provide progressive hints | Module 6: REST validation/security; Module 8: third-party AI services; Module 10: prompt engineering and chat-agent foundations; Module 3: streams for context transformation |
| 14. Conversation memory | Persist bounded conversation state and ownership | Module 2: concurrency and thread safety; Module 3: collections; Module 9: Redis/caching and distributed behavior; Module 10: chat-agent workflows |
| 15. Admin operations | Usage, cost, health, invocation, quotas, and audit views | Module 6: REST and security; Module 9: logging/monitoring through API Gateway and Spring Cloud; Module 8/9: testing and operational failure handling |
| 16. Support assistant | Separate support conversations, tickets, and handoff | Module 4: State/Strategy-style workflow modeling; Module 6: REST/security; Module 10: AI-assisted backend workflows |
| 17. pgvector and RAG | Ingest, chunk, embed, filter, retrieve, and evaluate | Module 9: search and semantic search; Module 10: prompts and AI agents; Module 3: collections/streams; Module 4: Adapter/Strategy boundaries |
| 18. Routing and cross-vertical retrieval | Choose current context, same-vertical, cross-vertical, or clarification paths | Module 4: Strategy, Factory, Adapter, and behavioral patterns; Module 3: predicates and streams; Module 9: Spring Cloud routing concepts |
| 19. Seeders and reconcilers | Synchronize source content and database state idempotently | Module 3: collections and transformations; Module 6: persistence; Module 9: payments/reconciliation as a reference for state reconciliation and failure handling |
| 20. Production engineering and security | Add observability, limits, retries, circuit breakers, and threat tests | Module 2: concurrency; Module 8/9: testing; Module 9: resilience, AWS, Redis/Kafka, Spring Cloud, Docker; Module 10: production AI systems |
| 21. Strangler migration and .NET retirement | Route capabilities incrementally and verify parity | Module 6: enterprise architecture; Module 8: Git/version control; Module 9: gateway, load balancing, monitoring, Docker, and distributed systems |
| 22. Unity Localization capstone | Build translation jobs, providers, cost, review, approval, and export | Module 4/5/7: domain modeling and machine coding; Module 8: third-party APIs and AI; Module 9: payments/reconciliation, async/distributed systems; Module 10: production AI workflows |

## How we will use the course during implementation

For each phase, I will provide:

1. The project problem we are solving.
2. The small set of course concepts relevant to that problem.
3. The specific module/lesson area to review.
4. A small implementation task.
5. A test or failure case.
6. A short checkpoint to confirm understanding before increasing complexity.

We will not introduce a concept merely because the course contains it. The project must create the reason for learning it.

