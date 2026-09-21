Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/B1XltyQuGx

Pre-Reads-Backend-LLD-9

PRE-READ	Applied Design & Machine Coding	Machine Coding - 9: Code BookMyShow 1

Context
Last session finished designing BookMyShow: the class diagram, the Seat/ShowSeat status correction, the ShowSeatType pricing correction, and a primer on Spring Boot and JPA, with schema deliberately deferred to today.
This session stops designing and starts building, following the same development order used for Parking Lot: models first, then real ORM wiring, then one full requirement built end to end.
A few names change between the Design lecture and the actual codebase (City becomes Region, Ticket becomes Booking), and this is called out openly rather than silently adopted, the same way a real engineer reconciles naming when joining an existing project.
The instructor notes for today's class also contain a few genuine gaps and bugs (a stray field, a missing class body, missing links), which get caught and fixed live as "review someone else's code" moments rather than glossed over.
Only one AI Corner appears today instead of the usual two, since this is a code-heavy session: AI generates a real, mechanical piece of the codebase, and the checking process focuses on whether it fits this system's specific requirement.

Overview
Segment | What is covered | Concepts in play
Recall and project setup | Quick recall of why Spring Boot and JPA were chosen, then generating the real BookMyShow project via Spring Initializr with its actual group, artifact, and package names | Tooling continuity from the previous session
Building the models (Pass 1) | Writing every model class as a plain Java class with Lombok's getter/setter annotations only, with no database annotations yet, plus reconciling naming differences from the Design lecture | Separation of boilerplate generation from persistence concerns
Connecting to a real database | Configuring application.properties to point at MySQL, and understanding what ddl-auto=update actually does to a schema over time | Practical Spring Boot configuration, schema lifecycle
Deciding the mappings (Pass 2) | Adding @Entity to every model, and working out the correct @ManyToOne/@OneToMany pairing for every relationship, including the trickier Booking-to-ShowSeat case | Cardinality reasoning, avoiding accidental duplicate tables
Handling enums | Applying @Enumerated(EnumType.STRING) to single-enum fields and @ElementCollection to list-of-enum fields, and understanding why STRING is safer than ORDINAL | Enum persistence strategy
Deciding the ID strategy | Choosing GenerationType.IDENTITY so the database itself assigns primary keys on every insert | Primary key generation
Repositories and AI Corner | Using Spring Data JPA's JpaRepository interface to get standard storage operations for free, then adding one custom query method by hand, checked against AI-generated output | Spring Data derived queries, verifying AI output against a real requirement
Coding one requirement end to end | Building R9 (listing movies playing in a region, grouped and counted) as a real Service method, driven by command-line input instead of a Controller | Requirement-to-code translation, deliberate scope-narrowing for an MVP

Why This Session Matters
Getting the @ManyToOne/@OneToMany pairing wrong is a real, common production mistake: forgetting mappedBy silently creates an extra join table instead of one clean relationship, a bug that is easy to miss until someone inspects the actual schema.
Choosing EnumType.ORDINAL over EnumType.STRING is exactly the kind of decision that looks harmless on day one and causes silent, unflagged data corruption months later, the moment someone reorders or inserts a new enum constant. This is precisely the class of bug that senior engineers screen for in code review.
Distinguishing what a schema structurally allows (a ShowSeat linked to many Booking rows over time) from what a business rule currently permits (only one active booking at a time) is a recurring interview and design-review theme: cardinality is not the same thing as validation logic.
Reviewing a partially broken codebase and fixing a missing class body, a stray field, or a missing foreign key link is realistic engineering work. Most real onboarding involves reading and correcting someone else's code, not writing everything from a blank file.
Checking AI-generated repository code against a system's own specific query need, rather than trusting it purely because it compiles and looks conventional, is the same AI-verification discipline built earlier in this module, now applied to a new kind of output (generated boilerplate rather than a design correction).

Real-World Use Cases
JPA and Hibernate in production Java backends: Most real Java services use JPA-backed entities for standard CRUD operations rather than hand-written SQL, reserving raw queries only for complex reporting or performance-sensitive paths, exactly the tradeoff being set up in this session.
mappedBy avoiding duplicate join tables: Any production schema with parent-child relationships (an e-commerce order and its line items, a course and its enrolled students) depends on correctly linking both sides of a relationship, or risks silently doubling its table count as a system grows.
Many-to-many-over-time modeling: Hotel and flight booking systems track a room or seat's full booking history rather than overwriting it, since a cancelled and later rebooked unit needs both records preserved for audits, refunds, and dispute resolution, the same reasoning behind the Booking-ShowSeat relationship here.
EnumType.STRING in production status columns: Payment processors and order-management systems almost universally store status values as readable strings rather than numeric codes, specifically to stay safe when a new status is added or an existing one is reordered in code.
Derived query methods in Spring Data: Internal admin tools and reporting dashboards commonly rely on Spring Data method-name-derived queries (walking a chain like show-to-screen-to-theatre-to-region) instead of hand-written joins, trading a small naming discipline for a large reduction in boilerplate SQL.
Command-line runners for early-stage verification: Engineering teams commonly use a lightweight command-line entry point to sanity-check a new service or query against a real database, before any REST endpoint or UI exists, exactly the role CommandLineRunner plays in this session.

Connection to the Upcoming Class
Next session brings back the Controller and DTO layer properly, since today deliberately skips it in favor of talking directly to the Service from the command line.
Next session builds booking and payment end to end, giving Booking, Payment, and the mapping classes built today their first real business logic.
Next session finally solves R10 and R11, the "two users, one seat" race condition with a live payment-window hold, using real threads, the harder sibling of the "two gates, one spot" problem already solved for Parking Lot.
The entities, relationships, and repositories finished today are the direct foundation the next session's Service and Controller layers are built on top of; nothing from today gets rebuilt, only extended.

Prerequisites from the Previous Class
The eighteen requirements, especially R9 through R12
R9 (listing movies running in a city, grouped by movie) is not a new field on any class, it is a query across the physical hierarchy, and this session finally implements exactly that query.
R10 and R11 (seat holding during payment, and no double-booking the same seat for the same show) are named but deliberately left unsolved again this session, carried forward as the concurrency problem to be solved next.
R12 (price as a function of show and seat type, not of an individual seat) is the reasoning behind why ShowSeatType exists as its own class rather than storing price directly on a seat mapping.
The Seat/ShowSeat status correction: Booking status cannot live on Seat itself, since the same physical seat is free for one show and booked for another; it belongs on the mapping between a show and a seat.
SeatType as configurable data, not an enum: Different theatre chains can define their own seat-tier names, so SeatType was built as a real class rather than a shared Java enum, a decision this session gives a concrete database table.
The capability-vs-snapshot features pattern: Screen.features describes what a screen can physically support; Show.features describes what is actually switched on for one specific screening. Both were introduced in the Design lecture and both get real persistence treatment today.
The Spring Boot, JPA, and Hibernate primer: JPA is the specification, Hibernate is the implementation that actually generates SQL, and Spring Boot is what wires the two together with minimal manual setup.
Spring Initializr, Maven, and the five dependencies (Spring Boot DevTools, Lombok, Spring Configuration Processor, Spring Data JPA, MySQL Driver) were all introduced last session and are assumed working today.

Key Concept Preview
Writing "many" on one class and "one" on another does not automatically tell Hibernate these two lines describe the same relationship. Without mappedBy pointing at the exact field name on the other side, Hibernate quietly creates an extra join table nobody asked for.
A schema's cardinality describes what can be linked structurally over time, not what is allowed to be true right now. A ShowSeat linked to two different Booking rows across time (one cancelled, one active) is a completely different question from whether two bookings can be active on the same seat at once, which is a business rule, not a schema constraint.
Storing an enum as ORDINAL saves a few bytes but silently breaks the moment someone reorders or inserts a new value into that enum later, with no error thrown anywhere. Storing it as STRING costs a little more space and is immune to that failure mode entirely.
A list of enum values needs @ElementCollection, not @ManyToMany. @ManyToMany is for relating two real entities with their own tables; an enum has no table of its own to relate to.
A Spring Data method name like one that walks show to screen to theatre to region is only as reliable as the real field names it references. If a field gets renamed later, the method name has to be updated to match exactly, or it fails at startup rather than at query time.

Environment Setup
This session assumes the Spring Initializr project generated as homework from the previous session is now replaced with BookMyShow's real project details rather than a throwaway test.
Generate a project at start.spring.io using group com.scaler, an artifact name of your choice (the lecture uses a name like bookmyshowmay23), and a matching package name built from those two. Keeping the package name consistent with the artifact name from the start avoids import-resolution confusion later.
Select the same five dependencies from last session: Spring Boot DevTools, Lombok, Spring Configuration Processor, Spring Data JPA, and MySQL Driver.
Have a local MySQL instance available and reachable, since this session connects the project to a real database rather than working purely in memory. Know your MySQL username and password ahead of time so class time isn't spent on connection troubleshooting.

What You Will Walk Away With
Explain why Lombok's boilerplate-generation annotations and JPA's persistence annotations solve two unrelated problems, and why every model needs its own getter/setter regardless of what its parent class provides
Distinguish ddl-auto=update, create, and validate, and justify why update is the practical default for active development
Correctly pair @ManyToOne and @OneToMany(mappedBy = ...) for a given relationship, and identify when a missing mappedBy would create an unwanted extra table
Reason through a genuinely ambiguous cardinality question (Booking to ShowSeat) by separating structural possibility from business-rule enforcement
Apply @Enumerated(EnumType.STRING) to single enum fields and @ElementCollection plus @Enumerated to list-of-enum fields, and justify choosing STRING over ORDINAL
Identify a missing class body, a stray field, or a missing back-reference in an existing codebase and correct it with reasoning, not guesswork
Write a Spring Data derived query method by chaining real field names across related entities
Evaluate AI-generated repository code against a system's own specific requirement, not just against general correctness
Translate a previously-named requirement (R9) into a working Service method and a command-line entry point, end to end against a real database
