Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/SJx-mTKwGl

# Pre-Reads-AppliedDesignMachineCoding-6.2 — Machine Coding - 6.2: Code Parking Lot 2

## Context

Last session finished the schema and every model class for the Parking Lot system, but left the Repository layer unbuilt, the Service layer only ever named, and TicketController holding real business logic directly inside it rather than delegating properly.

This session closes the system into a working MVP: a generic in-memory storage layer, a real Service layer that finally exposes why that layer exists, corrected controllers, and a resolved version of the concurrency problem named all the way back in the design session.

Every deliberate simplification made to keep this an MVP (plain enums instead of lookup tables, one strategy implementation instead of a swappable pair, a simulated payment gateway) is named explicitly rather than silently skipped, continuing the module's running discipline of honest, checkable gaps over quiet shortcuts.

The session closes with an AI Corner built around a genuinely unfinished optimization in the team's own working code, not a planted mistake, mirroring the discipline first introduced with TicTacToe's Hard bot.

## Overview

| Segment | What is covered | Concepts in play |
|---|---|---|
| Recap and named MVP simplifications | What was finished last session, what remains open, and four explicit simplifications made today to keep the system an MVP | Checkpoint discipline, honest scoping |
| The generic Repository layer | A single generic in-memory storage class shared across every model type, bounded to guarantee common fields exist | Generics, type bounds, storage-only responsibility |
| Building the Service layer for real | Moving business logic out of TicketController and into a proper TicketService, exposing what a Controller, Service, and Repository should each actually be responsible for | Layered architecture, constructor injection |
| BillService and PaymentService | Fee calculation via a swappable strategy, partial payment tracking, and a properly abstracted (if simulated) third-party payment gateway | Strategy pattern in practice, interface-based abstraction |
| Finishing the remaining controllers | BillController, PaymentController, and a new read-only ParkingLotController use case for spot availability | CRUD identification, DTO discipline reapplied |
| Identifying the critical section | Pinpointing the exact read-then-write gap in spot assignment where two threads can interfere | Race conditions, critical sections |
| The synchronized fix | Choosing a narrow, targeted lock over a whole-method lock, and understanding what a shared lock object actually protects | Thread synchronization, lock granularity |
| Proving the fix with a genuine two-gate test | Writing a concurrency test using two real, distinct Gate objects rather than an abstract "two requests" scenario | Test fidelity to a named problem |
| Wiring a full end-to-end demo | Assembling repositories, services, and controllers into a single running flow: entry, billing, payment, and spot release | System integration, closing the loop on a requirement |
| AI Corner: an unsafe optimization | Reviewing an AI-suggested per-vehicle-type locking scheme that looks reasonable but reintroduces the original race condition because of the spot-sizing design from a previous session | Verifying AI output against a system's own real constraints |

## Why This Session Matters

A controller silently holding business logic for an entire session, without anyone flagging it, is a realistic illustration of how architectural drift happens gradually in real codebases. Catching and correcting it here reinforces that "it compiles and works" is not the same as "it is in the right layer."

Race conditions are, by nature, invisible under normal testing. They only surface under genuine concurrent load, which is exactly why this session insists on testing with two real, distinct entities (two actual Gate objects) rather than a loosely similar simulation. This distinction — testing the exact scenario that was named rather than something adjacent to it — is a transferable engineering discipline well beyond this one problem.

The AI Corner in this session demonstrates a genuinely dangerous pattern: an AI-generated fix that is well-structured, matches the existing interface, and still silently reintroduces a serious concurrency bug because it does not account for the system's own prior design decision (that one physical spot can support multiple vehicle types). This is precisely the kind of verification failure that causes real production incidents when AI-suggested code is trusted without checking it against a system's actual data model.

Naming every MVP simplification explicitly, rather than letting them pass unnoticed, is treated as being just as much a skill as writing the working code itself, a discipline that maps directly onto how real engineering teams communicate scope and technical debt.

## Real-World Use Cases

- **Generic repository patterns**: Most production ORMs and data-access frameworks provide a generic base repository class bounded by a common entity interface, exactly mirroring InMemoryRepository<T extends BaseModel>, so that create, find, and list logic is written once rather than duplicated per entity.
- **Service layer enforcing rules independent of caller**: A banking system's transfer validation logic lives in a service class rather than in each API endpoint, so a mobile app, an admin tool, and a batch job all get the exact same enforced rules automatically, the same reasoning behind moving the gate-type check out of TicketController.
- **Swappable gateway interfaces for testing**: Payment processing systems commonly define a gateway interface with a real implementation for production and a fake or sandboxed implementation for testing and demos, exactly matching the PaymentGateway/FakePaymentGateway split built here.
- **Partial payment reconciliation**: Subscription and invoicing platforms that allow a single invoice to be settled across multiple payment attempts rely on summing only successful transactions toward the total owed, the same logic applied in PaymentService when checking whether a bill is fully paid.
- **Fine-grained locking in inventory systems**: Ticketing and inventory-reservation systems that lock on the specific unit of inventory being contested (a particular seat or SKU), rather than a broader category, mirror the corrected per-spot locking strategy built in this session's AI Corner resolution.
- **Verifying AI-suggested concurrency fixes**: An engineer reviewing an AI-generated caching or locking optimization checks it specifically against known overlapping cases in the system's own data model, the exact discipline applied here when checking the AI's vehicle-type-based lock against overlapping spot support.

## Connection to the Upcoming Class

The next session moves to a new problem entirely, designing BookMyShow, confirmed directly by this lecture's own closing line.

That session is explicitly framed as encountering a harder version of the exact concurrency problem just solved here: seat locking during a live booking, where multiple users can attempt to reserve the same seat at nearly the same moment, the same shape of problem as two gates racing for one parking spot.

The layered discipline built across the Parking Lot sessions (thin controllers, real logic in services, storage isolated in repositories) carries forward unchanged as the default architecture for BookMyShow.

The habit of testing a named concurrency scenario with the exact real entities it describes, rather than a loosely similar substitute, becomes directly relevant again once seat locking needs to be proven correct.

## Prerequisites from the Previous Class

- **The completed schema and model classes**: Every model (ParkingLot, Gate, ParkingSpot, Vehicle, Ticket, Bill, Payment, and supporting enums) extends BaseModel, holding shared id, created-at, and last-modified-at fields.
- **The AllotmentStrategy and FeeCalculationStrategy interfaces**: Both were introduced because their underlying requirements were phrased as needing runtime-swappable behavior; this session builds one concrete implementation of each to prove the shape works.
- **DTO discipline at controller boundaries**: Request and Response DTOs were established as the only things that should cross a controller boundary, a pattern extended to every controller finished in this session.
- **The originally-named race condition**: The design session's AI Corner first surfaced that nothing prevented two gates from assigning the same spot to two vehicles at nearly the same moment; this session finally resolves that named, previously unsolved gap.
- **The spot-sizing decision from the schema session**: A spot's supportedVehicleTypes is a list, meaning a truck-sized spot also supports car and bike vehicles; this earlier decision is precisely what makes the AI Corner's per-vehicle-type locking suggestion unsafe in this session.

## Key Concept Preview

A critical section is not "the whole method that touches shared data," it is the specific gap between reading a piece of shared state and writing back a decision based on that read. Locking more than this gap wastes time; locking less than it reintroduces the bug.

A synchronized block only protects against other threads trying to acquire the exact same lock object. A lock object created fresh inside the method being called (`new Object()` on every invocation) provides no protection at all, since every thread ends up locking on its own separate object.

A test written to prove a specific named concurrency problem should recreate that problem using the same real entities it describes. A test using two threads racing on one shared Gate object does not prove the same thing as a test using two genuinely distinct Gate objects, even though both involve concurrency.

Locking by a proxy for the shared resource (vehicle type) rather than the resource itself (the specific spot) is unsafe the moment two different proxy values can legitimately point at the same underlying resource, exactly the case here since one truck-sized spot supports multiple vehicle types.

## What You Will Walk Away With

- Build a generic, type-bounded repository class that stores any model extending a shared base class
- Explain why business logic sitting inside a Controller is a layering violation, and correctly relocate it to a Service
- Implement a Service class that coordinates repositories and a Strategy interface to fulfill a use case
- Design a gateway interface with a simulated implementation to represent a third-party integration boundary safely in an MVP
- Correctly total only successful partial payments when determining whether an obligation has been fully settled
- Identify the exact critical section in a piece of shared-state-modifying code
- Justify choosing a narrow synchronized block over a whole-method lock, and identify what object must be shared for a lock to provide real protection
- Write a concurrency test that faithfully recreates a named race condition using the same real entities the problem describes
- Diagnose why a plausible, interface-matching AI-suggested locking strategy can still be unsafe against a system's own prior design decisions
- Name and communicate every deliberate scope simplification in an MVP explicitly, rather than allowing them to pass unnoticed
