Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/rJmbguKDGe

# Pre-Reads-AppliedDesignMachineCoding-06 — Machine Coding - 6: Code Parking Lot 1

## Context

Last session produced a full class diagram and a first pass at the schema for the Parking Lot system, but deliberately left two schema techniques unaddressed: how to represent inheritance in a database, and the right way to store enum-like values.

This session adds both techniques, finishes the schema completely, and then moves into writing real Java model and controller code.

A genuine design gap surfaces mid-session, not by plan: parking spot sizing turns out to be more nuanced than the original "exact type match" rule from last session, and gets reworked live, the same way a real team discovers gaps while building rather than only while planning.

The session closes with the case for Data Transfer Objects (DTOs) at the controller boundary, worked out through two concrete failure scenarios rather than asserted as a rule, followed by the module's now-familiar AI Corner diagnosing a deliberately flawed controller.

## Overview

| Segment | What is covered | Concepts in play |
|---|---|---|
| Recap of remaining schema work | What was already built last session versus what still needs inheritance handling and consistent enum representation | Continuity, checkpoint discipline |
| Representing inheritance in a schema | Moving from a naive duplicated-column approach across subtype tables to a single parent table holding shared attributes, with child tables holding only their own specialization | Schema normalization, avoiding UNION-based queries |
| Choosing enum representation | Comparing raw text storage against a dedicated lookup table, and a concrete test for when a plain Java enum is sufficient versus when a lookup-table-backed class is needed | Storage cost, query safety, configurability |
| Finishing the schema | Applying both new techniques across every remaining table, including a live rethink of how ParkingSpot relates to vehicle types | Cardinality rules, many-to-many discovery |
| The parking spot sizing rethink | Realizing a spot built for a larger vehicle can also hold smaller vehicles, turning a single vehicle type field into a list, and creating a genuine many-to-many relationship | Real-world constraint modeling, mapping tables |
| Coding the models | A shared BaseModel for common fields, and careful field-by-field judgment about lists versus single values | Encapsulation, inheritance in code, precise data modeling |
| Coding controllers and identifying CRUD use cases | A repeatable process for finding which model needs which controller method | CRUD, controller design |
| The case for DTOs | Two concrete scenarios showing what breaks when raw models cross a controller boundary, motivating dedicated Request and Response objects | Coupling, encapsulation, API boundary design |
| AI Corner: diagnosing a flawed controller | Reviewing a controller that skips DTOs, misuses an enum, and returns null silently, then fixing it using ideas from the same session | Enum type safety, exception-over-null discipline |

## Why This Session Matters

Representing inheritance correctly in a schema is a common real interview and real production decision, not a niche technique. Getting it wrong means every simple aggregate query turns into a chain of unions that only gets worse as the system grows.

Deciding between a plain enum and a lookup table is a genuine architectural choice with a real cost (an extra join) and a real benefit (adding values without a redeploy). Being able to articulate the deciding test, rather than guessing case by case, is exactly the kind of reasoning a reviewer or interviewer probes for.

The parking spot sizing gap illustrates something important about real engineering: even a carefully designed system from the previous session can reveal a missed constraint the moment it gets modeled concretely in code. Catching this gracefully, mid-build, is a more realistic and more valuable skill than pretending a paper design is always complete.

Passing raw models across a controller boundary is a common, costly mistake. It silently couples unrelated callers to internal changes and can expose internal data to parties who have no business seeing it, both of which are exactly the kind of issue that surfaces in real production incidents, not just style guides.

## Real-World Use Cases

- **Inheritance in a schema**: An e-commerce catalog storing a shared products table for common fields like name and price, with separate electronics and apparel tables holding only their own specialized columns, mirrors the parent-table-for-common, child-table-for-special pattern built here for payment types.
- **Lookup tables for evolving values**: A customer support platform storing ticket priority levels in a dedicated table rather than a fixed database enum, so a new priority level can be added without a schema migration, mirrors the reasoning behind making SpotAssignmentStrategyType a lookup-table-backed class.
- **Capacity-based resource substitution**: A cloud compute platform allowing a larger instance type to satisfy a request for a smaller one when the smaller type is unavailable, mirrors a truck-sized spot being able to hold a car or a bike.
- **Shared base fields across models**: Nearly every production ORM framework provides a base entity class with id, created-at, and updated-at fields that every model extends, exactly matching this session's BaseModel.
- **CRUD-oriented controller design**: A user management service organizing its API around create, read, update, and delete operations per resource is the same systematic process used here to decide what TicketController needs.
- **DTOs shielding external partners**: A payments company exposing a minimal transaction confirmation object to a partner integration, rather than its full internal transaction record, mirrors the billing-partner scenario used to motivate DTOs in this session.

## Connection to the Upcoming Class

The next session, Code Parking Lot 2, finishes the remaining controllers (ParkingLot, Bill, Payment), applying the same CRUD-identification process and DTO discipline established today.

The concurrency problem named back in the design session — two entry gates potentially assigning the same spot to two different vehicles at nearly the same moment — is explicitly deferred to that session, introducing multi-threading concepts to this module for the first time.

The completed schema and model classes from this session become the concrete foundation the next session builds controller logic on top of, with no re-derivation needed.

## Prerequisites from the Previous Class

- **The nine-class design**: ParkingLot, ParkingFloor, Gate, ParkingSpot, Vehicle, Operator, Ticket, Bill, and Payment, derived from a user-journey walkthrough.
- **The two Strategy interfaces**: FeeCalculationStrategy and AllotmentStrategy, both introduced because their underlying requirements were phrased as needing runtime-swappable behavior.
- **Builder-validated construction**: ParkingLot requiring its floors, gates, and strategies to be correctly assembled before use, the same reasoning applied earlier to Game.
- **The class-to-table schema algorithm**: Simple attributes become columns directly; class-typed attributes require a cardinality check, with foreign keys on the "many" side for one-to-many relationships and a mapping table only for genuine many-to-many relationships.
- **The previously flagged concurrency gap**: AI's review in the design session surfaced that nothing yet prevents two gates from assigning the same spot at nearly the same time, a gap named but explicitly not solved, and carried forward as unfinished business into this session and the next.

## Key Concept Preview

Storing shared attributes once, in a single parent table, turns any simple aggregate question ("how many pens total," "what is the minimum price") into a single-table query. Duplicating shared columns across every subtype table turns the same simple question into a growing chain of unions.

The deciding question for choosing between a plain enum and a lookup-table-backed class is not how the value is used, but how likely its set of possible values is to change without a code redeploy. A fixed pair like entry versus exit almost never changes; a configurable strategy type, by definition, is expected to grow.

A constraint that looks like "exact type match" on paper can turn out to be "a larger option can substitute for a smaller one" once it is modeled against physical reality. This kind of refinement is not a contradiction of the original requirement, it is a more accurate version of it.

A DTO is not simply a smaller version of a model. It is a deliberate one-way boundary: whatever field is not explicitly placed on a DTO can never reach a caller, no matter how the internal model grows or changes afterward.

## What You Will Walk Away With

- Represent an inheritance relationship in a schema using a shared parent table and specialized child tables, avoiding duplicated columns and union-based queries
- Apply a concrete test (likelihood of change without a redeploy) to decide between a plain enum and a lookup-table-backed value
- Identify a many-to-many relationship that was not obvious from an initial requirement, and justify a mapping table rather than a single foreign key
- Explain why a resource sized for a larger requirement can often satisfy a smaller one, and model that substitution correctly
- Write model classes that extend a shared base class, making a deliberate list-versus-single-value decision for every field rather than copying a previous field's shape
- Identify CRUD use cases for a given model and structure controller methods around them
- Explain, using concrete failure scenarios, why raw models should not cross a controller boundary
- Design Request and Response DTOs that expose only what a specific caller needs, independent of internal model changes
- Diagnose enum misuse, missing DTO boundaries, and silent null returns in a flawed controller, connecting each diagnosis to a previously learned concept
