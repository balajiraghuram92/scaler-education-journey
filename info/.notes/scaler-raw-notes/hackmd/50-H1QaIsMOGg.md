Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/H1QaIsMOGg

# Pre-Reads-Backend-LLD-8 — Machine Coding - 8: Design BookMyShow

## Context

Last session closed out Parking Lot as a working MVP: a generic repository layer, a real Service layer, corrected controllers, and a resolved version of the "two gates, one spot" race condition.

This session moves to a brand-new system, BookMyShow, but deliberately reuses the same teaching rhythm: overview, then requirements gathered in strict numbered order, then a class diagram built by correcting first-attempt designs in real time.

Today only covers three of the usual six framework steps: Overview, Requirements, and Class Diagram. Schema is explicitly deferred to the start of next class, the same slot where the Parking Lot schema was built, and this deferral is called out openly rather than treated as a silent cut.

Much of the physical structure (City, Theatre, Screen, Seat) is a direct copy of Parking Lot's hierarchy shape, so the session moves quickly through anything repeated and slows down only on what is genuinely new: why a seat cannot hold its own booking status, and why price lives on its own mapping class rather than directly on a seat-show pairing.

A new closing block is added this session that has no precedent in Parking Lot: a short orientation to Spring Boot and JPA, since next class jumps straight into writing real framework code for the first time in this module.

## Overview

| Segment | What is covered | Concepts in play |
|---|---|---|
| Overview and scope lock | Aligning on what BookMyShow is, and locking scope to movie ticket booking only (no plays, concerts, or sports), plus the shift from in-memory storage to a real database | Scope definition, MVP boundary-setting |
| Requirements gathering (R1-R18) | Eighteen requirements covering the physical hierarchy, the movie/show distinction, seat selection limits, seat-locking during payment, pricing rules, payment support, and movie metadata, walked through in strict numbered order | Requirement decomposition, distinguishing data properties from query behavior |
| The physical hierarchy | City, Theatre, Screen, and Seat modeled as a composition chain, directly mirroring Parking Lot's structure | Composition, one-to-many hierarchies |
| Seat and the status correction | Why a seat cannot store its own booking status, and the introduction of a mapping class to hold status per (show, seat) pair instead | Normalization, mapping/join classes |
| SeatType as configurable data | Testing whether a small fixed set of values (Gold, Silver, Platinum) should be a shared enum, and discovering it should not be once different theatres define their own tier names | Enum vs. configurable data, the "same set for every owner" test |
| Movie class | Giving cast, genre, languages, and supported features a proper home on the Movie class itself, separate from any one screening | Content vs. instance separation |
| Show class and the features pattern | Why Show needs its own features list even though Screen already has one, distinguishing physical capability from what is actually switched on for one screening | Capability-vs-snapshot pattern |
| ShowSeatType and the pricing correction | Why price cannot live directly on the seat-show mapping, and why it instead belongs on a class keyed by (show, seatType) | Normalization, avoiding duplicated data across rows |
| User, Ticket, and Payment | Why a Ticket stores a list of seat-show mappings rather than plain seats, and why payments are stored as a list to support partial payment | Aggregation, list-based partial state |
| AI Corner: refine and diagnose | Using AI once to sanity-check the completed design for a genuine gap, and once to diagnose a deliberately flawed class before fixing it by hand | Verifying AI output against a system's own real constraints |
| Spring Boot and JPA primer | Orientation to Maven, Spring vs. Spring Boot, JPA vs. Hibernate, Spring Initializr, dependencies, and a first hint of annotations, ahead of writing real framework code next class | Tooling literacy, ORM concepts |

## Why This Session Matters

Almost every genuine correction in this session traces back to one question: is this a property of the seat, or of the show? Interviewers routinely probe exactly this kind of reasoning, because getting it wrong produces subtle bugs that only surface once a system has real concurrent usage, not during a quick demo.

The seat-status and pricing corrections are both instances of the same real-world bug class: storing a value on the wrong entity, so it either cannot represent all valid states or has to be duplicated across many rows and kept in sync by hand. This is one of the most common sources of data-integrity bugs in production systems.

Recognizing when a requirement describes a query rather than a new field (as with R9, listing movies running in a city) is a skill that prevents over-engineering a class diagram with attributes that should really be computed on demand by a service.

Naming a hard concurrency problem clearly, without solving it prematurely on paper, is treated as real engineering progress in its own right. Interviewers and senior reviewers consistently value a candidate who can say "this is a race condition, here is exactly where it would occur" over one who either ignores it or hand-waves a fix that has not been thought through.

The Spring Boot and JPA orientation exists so that tooling unfamiliarity does not compete with system-design learning next class. This mirrors a very real onboarding problem at most engineering jobs: new tools are usually learned in parallel with a real project, and being able to separate "I don't understand this business logic" from "I don't understand this tool" is a practical skill in itself.

## Real-World Use Cases

- **Movie/show separation**: Streaming and ticketing platforms consistently separate a piece of content (a movie) from a scheduled instance of it (a screening or broadcast slot), which is exactly why a single film can appear in dozens of independent showtimes across a city.
- **Seat-status mapping tables**: Airline and train booking systems never store seat-occupied status on the physical seat itself; they store it against a (flight or trip instance, seat) pairing, since the same physical seat is free on one journey and occupied on another.
- **Configurable seat-tier data**: Multiplex chains like PVR and INOX each define their own seating category names (Recliner, Executive, Gold Class) rather than sharing one fixed industry-wide list, which is why a platform aggregating multiple chains cannot hardcode tiers as a single enum.
- **Capability-vs-snapshot features**: A cinema screen physically wired for Dolby Atmos and 3D projection can still run an individual show in plain 2D if the content or scheduling calls for it, the same way a hotel room capable of extra bedding is not always booked with it.
- **Price normalization via mapping class**: Airlines and event-ticketing platforms price a fare class per specific flight or event instance, not per physical seat, so a price change for one departure never needs to touch thousands of individually stored seat records.
- **Seat holds during checkout**: E-commerce and ticketing checkouts commonly place a short-lived hold on selected inventory the moment it enters a cart or payment flow, releasing it automatically if payment is not completed, to stop inventory from being silently locked by abandoned sessions.
- **Partial payments**: Invoicing and subscription billing systems that allow an amount to be settled across multiple transactions track each successful payment separately and sum only the successful ones toward the total owed.
- **ORM and JPA in production systems**: Most production Java backends use JPA (commonly via Hibernate) instead of hand-written SQL for standard CRUD operations, reserving raw queries for genuinely complex reporting or performance-critical paths.

## Connection to the Upcoming Class

The next session opens with the schema for everything designed today, the same sequencing used for Parking Lot, with particular attention on how ShowSeat and ShowSeatType translate into real tables.

Immediately after schema, the next session moves straight into writing real Spring Boot model classes annotated with `@Entity` and `@Id`. Today's tooling primer exists specifically so that transition feels like syntax rather than a fresh mystery.

The seat-locking race condition named today ("two users, one seat," with a time-based hold layered on top) is explicitly flagged as harder than Parking Lot's "two gates, one spot," and is scheduled to be solved with real threads and real code soon after schema and models are in place.

The layered discipline built across the Parking Lot sessions (thin controllers, real logic in services, storage isolated behind a repository) carries forward unchanged as the default architecture for BookMyShow once coding begins.

## Prerequisites from the Previous Class

- **Layered architecture discipline**: Business logic belongs in a Service class, not in a Controller; a Controller that holds real logic directly is a layering violation, not a shortcut. Repositories exist purely for storage and retrieval, kept isolated from business rules.
- **The generic repository pattern**: A single generic, type-bounded storage class (`InMemoryRepository<T>`) was built to serve every model type sharing a common base, avoiding duplicated storage logic per entity. BookMyShow's move to real MySQL persistence is the reason this pattern gets replaced by JPA next class rather than repeated by hand.
- **Gateway abstraction and partial payments**: A PaymentGateway interface with a simulated implementation represented a third-party integration boundary safely inside an MVP. `Bill.payments` (a list, not a single value) tracked partial payments by summing only successful transactions, the same reasoning reused for `Ticket.payments` in BookMyShow.
- **The originally-named race condition**: Parking Lot's design session first surfaced that nothing stopped two gates from assigning the same spot to two vehicles at nearly the same moment; that problem was solved for real, with a narrow synchronized block on the correct shared lock object, in the previous session. BookMyShow's "two users, one seat" is explicitly framed as the harder sibling of this exact problem, and is deliberately left unsolved on paper today.
- **Composition-based physical hierarchy**: ParkingLot → ParkingFloor → ParkingSpot was a composition chain, tested by asking whether a child object means anything without its parent. The same test applies directly to City → Theatre → Screen → Seat.
- **The enum vs. configurable-data reflex**: Parking Lot used a "will this list grow" test to decide between an enum and a lookup table. BookMyShow's seat-type question pushes this reflex one step further.

## Key Concept Preview

Almost every correction in this session comes back to one question: is this a property of the seat, or of the show? Whenever a field's correct value could differ across two different screenings of the same physical thing, that field does not belong on the physical entity itself.

A shared Java enum only works if every "owner" in the system agrees on the exact same set of values. The moment different theatres are allowed to define their own seat-tier names, the set is no longer platform-wide, and it stops being enum material at all.

Not every requirement adds a field to a class. Some requirements describe how existing classes get queried together later; recognizing that shape early prevents cluttering a class diagram with attributes that should really be computed by a service.

The same "capability vs. this-instance-only" split shows up twice in one session: Movie.features versus Show.features, and Screen.features versus Show.features. Once you notice it the first time, expect it to repeat elsewhere in real systems too.

A JPA annotation like `@Entity` or `@Id` is only a label. It does nothing by itself; Hibernate is the piece that actually scans for these labels and turns them into real database behavior.

## Environment Setup

Homework for this session asks you to generate a real Spring Boot project before the next class, so it is worth doing this once, calmly, ahead of time rather than for the first time live in class.

1. Go to start.spring.io (Spring Initializr), a website that generates a ready-to-run Spring Boot project from a form.
2. Under project basics, select Maven as the build tool, Java as the language, and the latest stable (non-SNAPSHOT) Spring Boot version.
3. Under project metadata, use a group and artifact name of your choice (the lecture uses `com.scaler` and `bookmyshow` as an example), Jar packaging, and Java 17 or your class's standard version.
4. In the dependencies panel, add these five: Spring Boot DevTools, Lombok, Spring Configuration Processor, Spring Data JPA, and MySQL Driver. Spring Data JPA is the one that actually brings in JPA and Hibernate; MySQL Driver is what lets that setup talk to MySQL specifically, since JPA itself is database-agnostic.
5. Click Generate, unzip the project, and open it in your IDE. You do not need to write any code, just confirm it opens and runs, so the tool itself is already familiar before next class.

## What You Will Walk Away With

- Distinguish a movie (content) from a show (one specific screening of it), and identify which requirements attach to each
- Recognize when a requirement describes a query across existing classes rather than a new field on any one class
- Explain why a seat cannot store its own booking status, and correctly relocate that status to a mapping class keyed by show and seat
- Apply a "same set for every owner" test to decide whether a small fixed set of values should be a shared enum or per-owner configurable data
- Distinguish a capability field (what an entity can generally do) from a snapshot field (what is actually active for one specific instance)
- Explain why price should be keyed on (show, seatType) rather than duplicated across every individual seat-show mapping row
- Justify why a Ticket should reference a seat-show mapping rather than a plain seat
- Diagnose a flawed class design where a value sits on the wrong entity, using normalization and enum-vs-boolean reasoning already established earlier in the module
- Name a genuinely hard concurrency problem precisely (two users, one seat, with a time-based hold) without attempting to solve it prematurely on paper
- Explain what JPA is, how it relates to Hibernate, and why Spring Boot is used to adopt it with minimal manual configuration
- Generate and run a blank Spring Boot project via Spring Initializr with the correct dependencies for JPA-based persistence
