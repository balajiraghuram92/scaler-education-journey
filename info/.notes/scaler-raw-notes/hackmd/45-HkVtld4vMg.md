Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/HkVtld4vMg

# Machine Coding - 5: Design Parking Lot

## Overview

This document applies a six-step design framework to a multi-level parking lot system for a third-party company managing facilities like airports and malls.

**Key clarifications:**
- "End-to-end WORKING SYSTEM" (not just entities)
- In-memory storage only (no database)
- Command-line interface

The system must handle "entry, exit, payment, assigning spots" as real behaviors, making it a full system problem rather than a simple data model.

## Requirements (Eight Total)

**R1:** Multiple floors per lot

**R2:** Vehicle-type-specific spots with exact matching only (trucks cannot use car spots)

**R3:** Token creation and spot assignment happen simultaneously at entry gates

**R4:** Payment and spot-freeing occur at exit gates before vehicle departure

**R5:** "Fee calculation must be DYNAMIC — the system should support many, swappable fee-calculating algorithms"

**R6:** Payment via cash or third-party online gateway

**R7:** Multiple entry and exit gates (physically different)

**R8:** Spot assignment is configurable (auto-pick nearest or user selection)

Requirements 5 and 8 signal the **Strategy pattern** will be needed—two separate interfaces for fees and spot assignment.

## User Journey & Class List

Walking through driver experience yields nine classes:

- `ParkingLot`
- `ParkingFloor`
- `Gate`
- `ParkingSpot`
- `Vehicle`
- `Operator`
- `Ticket`
- `Bill`
- `Payment`

## Class Diagram Design

**ParkingLot** (built via `ParkingLotBuilder`)
- Holds floors, gates, status, both strategies, allowed vehicle types
- Builder pattern justified: multiple interdependent pieces must be correct before the lot is usable

**Gate** (single class with `GateType` enum)
- Not separate `EntryGate`/`ExitGate` classes—they're nearly identical except for type
- Includes: id, name, operator, status

**ParkingSpot**
- Fields: id, number, vehicleType, status (enum, not boolean)
- Tradeoff decision: storing `floorId` directly makes frequent lookups instant, justified by high usage (printing tickets)

**Ticket** (created at entry)
- Captures: id, number, entryTime, vehicle, parkingSpot, parkingFloor, gate, operator
- `Ticket.operator` is a snapshot, distinct from `Gate.operator` (which changes with shifts)

**Bill** (created at exit)
- Fields: id, ticketNumber, exitTime, amount, ticket, gate, operator, status
- Holds `List<Payment>` (not single Payment) to support partial payments: part cash, part online

**Payment**
- Fields: id, mode (enum), status (enum), referenceNumber, time, amount
- Multiple payments per bill enable independent refunds and shift audits

**Two Strategy Interfaces:**
- `FeeCalculationStrategy`: swappable pricing algorithms
- `AllotmentStrategy`: auto-pick nearest spot vs. user selection

## Schema Design

**Core Rules** (from Post-Read 2):
- Every class becomes a table
- Simple fields become columns
- Foreign keys placed on the "many" side of 1:M relationships

**Key Decisions:**

1. `ParkingLot` → `ParkingFloor` is 1:M, so `parking_lot_id` goes on `parking_floor`, not the reverse
2. `Gate` → `Operator` is 1:1 at any moment; stores current operator
3. `Bill` → `Payment` is 1:M (one bill, many payments), so direct `bill_id` FK on payments
4. Enums can become lookup tables (id + name) for easier future changes, though plain columns work too

**Why not place foreign keys on "one" side:**
A single `floor_id` column on `parking_lot` can only reference one floor, but a lot has many—the relationship wouldn't be representable.

## AI Corner Findings

**Gap identified:** Nothing prevents two entry gates from assigning the same empty spot to different vehicles simultaneously. `AllotmentStrategy.assignSpot()` decides which spot, but no lock prevents a second gate from seeing it as free at nearly the same moment.

**Deliberately left unresolved:** This is a genuine concurrency problem, not a design flaw. It requires actual multi-threaded code to address properly—it emerges only when real gates run concurrently.

## Common Pitfalls

- Jumping to "grid of spots" without confirming scope
- Treating in-memory as less rigorous (only database layer changes)
- Missing Strategy signals in requirements before diagramming
- Creating separate `EntryGate` and `ExitGate` classes (unnecessary duplication)
- Conflating `Ticket.operator` with `Gate.operator` (snapshots vs. live references)
- Giving `Bill` a single `Payment` instead of a list
- Applying data-duplication decisions uniformly without re-checking frequency
- Placing foreign keys on the "one" side of 1:M relationships
- Ignoring small mismatches in design notes

## Key Interview Questions Addressed

1. Why one `Gate` with `GateType` enum beats two separate classes
2. Why `Ticket` stores its own `operator` snapshot
3. Why `Bill` holds `List<Payment>`
4. Tradeoff reasoning for storing vs. deriving `floorId`
5. One-to-many foreign key placement
6. Enum-as-lookup-table vs. plain column choice
7. Why `Bill`:Payment is 1:M, not M:M
8. Contrast with Gate-Operator shift history (genuinely M:M, requiring mapping table)

---

**Complete design produced:** class diagram with composition/aggregation, nine classes, four+ enums, two Strategy sets, one Builder, and corresponding schema with all foreign key placements explained and justified.