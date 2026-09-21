Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/rJGtpPtDzl

Post Read - Machine Coding - 6: Code Parking Lot 1
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Aug 24, 2026
POST-READ	Applied Design & Machine Coding	Machine Coding - 6: Code Parking Lot 1
Introduction

Post-Read 5 designed the whole Parking Lot system on paper: requirements, class diagram, and a first pass at the schema. This document does three things. First, it learns two schema ideas skipped previously, how to handle inheritance in a schema, and the right way to store enums. Second, it finishes the schema completely. Third, it starts writing real Java model classes and controller methods.

Running example: the same multi-level Parking Lot system carried from Post-Read 5, now moving from paper design into a real schema and real code.
Along the way, this document works through a genuine design question about parking spots and vehicle sizes, one not fully thought through in the previous design session, resolved live the same way a real team would catch it while building, not while just planning on paper.
Today's focus is a clean, correct foundation: models → controllers → a proper way to talk to the outside world using DTOs.
This session contains six embedded animations, each narrated in full below at the point where the lecture places it.
Section 1: Quick Recap
What It Means
The nine classes found in Post-Read 5's user journey: ParkingLot, ParkingFloor, Gate, ParkingSpot, Vehicle, Operator, Ticket, Bill, Payment.
Already built last class:
- parking_lot, gates, parking_floor, parking_spot
- operators, tickets, bills, payments (partial)
- Some enum tables as lookup tables (lot_status, gate_type, etc.)

Still missing:
- A clean way to handle classes that will have SUBTYPES
  (like Payment → CashPayment / OnlinePayment, from homework)
- A proper, consistent way to store EVERY enum-like value
- The rest of the primitive columns for every table

Hidden Pitfalls
Treating last session's schema as final rather than a first pass: Post-Read 5 explicitly left the Payment inheritance question and full column detail as homework; carrying that work forward as unfinished, not forgotten, matters for correctly picking up where the design left off.
Section 2: Inheritance in a Schema
What It Means

The homework from Post-Read 5 asked for Payment to be sketched as an abstract class with CashPayment and OnlinePayment subtypes. Before returning to that, the idea is worked out with something simpler: pens.

        Pen
      (generic)
     /         \
 BallPen      GelPen

Pen has common attributes, like id and name. BallPen and GelPen each also have their own extra attributes. A naive way to store this: one table for pens, one for ball_pens, one for gel_pens, copying the common attributes into all three.
With that naive setup, how would a query be written to get the names of every pen, ball pens and gel pens together? All three tables would need to be queried separately and combined.
select name from pens
union
select name from ball_pens
union
select name from gel_pens

That's just for names. What happens the moment someone asks something simple, like "what's the minimum price across all pens"? The same messy union query has to repeat, every single time, for every simple question, and it gets worse as more pen types are added.
Problem: common data is copied into every child table.
Even a simple question needs a long UNION query across every
single subtype table.

Given that problem, what if the common attributes lived in exactly ONE place, and only the special attributes lived in the child tables? A pens table holds id, name, and anything shared. ball_pens and gel_pens only hold their own unique columns, plus a foreign key back to pens.
How to represent inheritance in a schema:
1. Create ONE table for the parent class.
2. Put every COMMON attribute in that parent table.
3. Create a table per child class, holding ONLY that child's
   own special attributes, plus a foreign key back to the parent.

❌ NAIVE APPROACH — data duplicated across every table

  pens                ball_pens              gel_pens
 ┌──────────┐        ┌──────────┐           ┌──────────┐
 │ id       │        │ id       │           │ id       │
 │ name     │        │ name     │  ← copied │ name     │  ← copied
 │ price    │        │ price    │  ← copied │ price    │  ← copied
 └──────────┘        │ ball_grip│           │ ink_type │
                     └──────────┘           └──────────┘

  Getting all pen names = UNION across all 3 tables, every time.

✅ BETTER APPROACH — parent holds common data, ONCE

              pens  (PARENT — common attributes)
             ┌──────────────┐
             │ id           │
             │ name         │
             │ price        │
             └──────────────┘
                 ▲        ▲
                 │        │            (FK: pen_id → pens.id)
         ┌────────┴───┐ ┌──┴───────────┐
        │ ball_pens   │ │ gel_pens     │
        ├─────────────┤ ├──────────────┤
        │ pen_id (FK) │ │ pen_id (FK)  │
        │ ball_grip   │ │ ink_type     │
        └─────────────┘ └──────────────┘

  Getting all pen names = SELECT name FROM pens. Done. No unions.

The arrows point upward from each child table to the parent, the real foreign key relationship: ball_pens.pen_id points to pens.id, and gel_pens.pen_id points to pens.id. Common data lives in exactly one row, in exactly one table. That is the whole trick.
Now the same question is trivial:
select name from pens

One table, no unions. The same idea works for minimum price, maximum price, counting all pens, everything gets simple, because the shared data lives in exactly one place.

What the Animation Shows: Parent-Child Table Inheritance Pattern

Clicking a child row, say a row from gel_pens where pen_id = 2, starts the animation tracing what happens next.

It follows the foreign key pen_id = 2 across to pens.id = 2, visibly landing on the matching parent row: pens(2, "Pro", $5.49).

The shared fields (id, name, price) get pulled from that parent row, then the specialized fields unique to gel_pens get added on top.

A single, complete, reassembled object appears once both pieces are combined, showing exactly what a SELECT * ... JOIN would return.

Clicking different child rows (from ball_pens or gel_pens) repeats the exact same trace-and-assemble process, with different parent rows and different specialized fields.

This makes the abstract "child table holds only its own columns, plus a foreign key back to the parent" rule into something watchable, row by row, instead of just a diagram. It reinforces that reconstructing a full object is just a JOIN following the foreign key, the same mental model needed later for querying inherited entities like CashPayment/OnlinePayment.

Answering the paired instructor question ("If gel_pens needed a SELECT that also showed ink_type alongside the name and price, what would that query actually need to do?"): the query would need to join gel_pens to pens on the foreign key (gel_pens.pen_id = pens.id), selecting pens.name, pens.price from the parent table and gel_pens.ink_type from the child table in the same statement, exactly the trace-and-assemble process the animation shows happening for a single row.

Bringing this back to already-known classes: where has a class that's really a parent, with subtypes underneath it, already been seen, either in TicTacToe or in the Parking Lot homework? Player (abstract) with HumanPlayer/BotPlayer in TicTacToe (Post-Read 3, Post-Read 4). And Payment with CashPayment/OnlinePayment from Post-Read 5's homework. The same rule applies to both: a payments table holds the shared fields (amount, time, status). A cash_payments table and an online_payments table each hold only what's unique to them, plus a payment_id foreign key back to payments.

Quiz Recap

You're modeling Vehicle as a parent, with BikeVehicle and TruckVehicle as subtypes, following the pattern we just built. Using this schema, which query correctly returns the total count of every vehicle currently parked, regardless of type?

A) SELECT COUNT(*) FROM bike_vehicles UNION SELECT COUNT(*) FROM truck_vehicles
B) SELECT COUNT(*) FROM vehicles (correct)
C) SELECT COUNT(*) FROM vehicles JOIN bike_vehicles ON vehicles.id = bike_vehicles.vehicle_id UNION SELECT COUNT(*) FROM vehicles JOIN truck_vehicles ON vehicles.id = truck_vehicles.vehicle_id
D) You need a separate vehicle_count column on parking_lot that gets updated manually every time a vehicle enters
Correct answer: B. id is a shared attribute, so it lives on the parent vehicles table only. Every vehicle, no matter its subtype, has exactly one row there. That is the entire point of putting common attributes on the parent, no joins or unions needed for anything that's common to all subtypes.
Why A is wrong: this is exactly the naive, pre-optimization approach the pen example was built to move away from; it works, but only because it repeats the exact mistake the parent table was designed to eliminate.
Why C is wrong: joining each child table to the parent and unioning the results is unnecessary work for a question that only needs data from the parent table; the join adds complexity without adding any information the parent table doesn't already have on its own.
Why D is wrong: manually maintaining a separate count column introduces a synchronization risk (the count could drift out of sync with reality) for a value that a simple COUNT(*) query already computes correctly and automatically.
Hidden Pitfalls
Duplicating common attributes across every child table: this is precisely the naive approach shown to break down, forcing a union query for even the simplest questions and multiplying the maintenance burden every time a new subtype is added.
Forgetting the foreign key direction runs from child to parent: each child table (ball_pens, gel_pens, or cash_payments, online_payments) holds the foreign key pointing up to the parent; the parent table itself holds no reference down to its children.
Assuming every hierarchy needs this treatment even when there's no real behavioral difference: this pattern earns its keep specifically when subtypes have genuinely different attributes or behavior (like CashPayment needing no reference number versus OnlinePayment needing one); applying it to a distinction that's purely cosmetic would add unnecessary schema complexity.
Section 3: The Right Way to Store Enums
What It Means
Post-Read 5 briefly noted an enum can become its own small lookup table instead of a plain column. This section works out why that matters, and when to just use a real Java enum instead.
Suppose a Human table exists, and a person can be a HUMAN or a BOT. The simplest way to store that is a type column, holding the text "HUMAN" or "BOT" directly. What problems come from storing it this way? It uses more storage, the same text repeats in every row. Comparing and searching by text is slower than comparing a small number. A typo can slip in, nothing stops bad data from getting stored.
Naive way — storing type as raw text:
1. Extra storage — repeating the same string many times
2. Slower comparisons — matching text vs matching a small number
3. No safety — a typo like "HUMN" is technically valid data

Given those problems, what if every possible value existed only ONCE, somewhere else, and just a small reference to it was stored? A separate small table, one row per possible value, and the main table just stores that row's ID.
Better way — enum as a lookup table:
1. Create a separate table for the enum. Two columns: id, value.
2. Insert one row per possible enum value.
3. In the main table, store just the ID — a foreign key.

What the Animation Shows: Raw String vs Lookup Table Enum Storage

Two empty table schemas appear side by side, a raw messages_raw table with a VARCHAR sender column, and a normalized setup with a sender_types lookup table plus a messages_norm table.

The lookup table gets seeded once, HUMAN(id=1) and BOT(id=2), a one-time 8-byte cost.

Row by row, both tables get the same data inserted: the raw table stores the full word "HUMAN" (5 bytes) or "BOT" (3 bytes) every single time, while the normalized table just stores a 1-byte sender_id pointing back to the lookup table.

A running byte-total ticks up under each table as more rows are added, the raw table's total climbs faster and faster (5B, 8B, 13B, 16B, 21B…), while the normalized table's total barely grows (9B, 10B, 11B, 12B, 13B…).

By row 17, the raw table has used 73 bytes while the normalized table has used only 25, and the gap keeps widening with every additional row.

This turns "extra storage, repeating the same string many times" from an abstract claim into an actual running number that visibly grows apart, row after row. It makes clear that the storage savings from a lookup table aren't a one-time trick, they compound with every single row added afterward.

Answering the paired instructor question ("If this table eventually holds a million rows, roughly how much bigger will the raw-string version be compared to the normalized one?"): scaling the per-row pattern shown in the animation (roughly 4 bytes saved per row on average, comparing a ~4-byte average string cost against a 1-byte foreign key), a million rows would produce a gap on the order of several megabytes, purely from this one column, with the gap growing linearly as more rows are added, exactly the widening pattern the animation shows at row 17.

Given this rule, should every single enum-like thing in the Parking Lot system get this same treatment? GateType, VehicleType, PaymentMode, SpotAssignmentStrategyType, all of them, the same way? The actual test to use: how likely is this set of values to change, without needing a code deploy?

GateType will only ever be ENTRY or EXIT. That's never changing.
SpotAssignmentStrategyType might grow, a new client might want a brand-new assignment method added later, without touching old code.

Given that test, which fits a plain, compile-time Java enum better, and which fits a full lookup-table-backed class better? GateType, fixed, tiny, never changes, fits a plain Java enum. SpotAssignmentStrategyType, genuinely might grow, especially since it was made configurable in R8 (Post-Read 5), deserves the full lookup-table-backed class, so new values can be added without a redeploy. This connects straight back to R5 and R8 from Post-Read 5: fee calculation and spot assignment both need to be swappable at runtime. That configurability is exactly the signal indicating a value earns the lookup-table treatment, not a plain enum.

Quiz Recap

In our model code, PaymentMode (CASH / ONLINE) is written as a real Java enum, while SpotAssignmentStrategyType is written as a class extending BaseModel, with an id and a value. Using the test we just built, why does this split make sense?

A) SpotAssignmentStrategyType is used more often at runtime, so it needs to be a class
B) PaymentMode has a small, fixed set of values unlikely to ever change without a code deploy, while assignment strategies are expected to grow as new clients configure new ones (correct)
C) Both should always be full lookup-table classes, enums should never be used for domain concepts
D) Both should always be plain Java enums, since enums are always faster
Correct answer: B. The deciding question is always "how likely is this set of values to change without a redeploy." A fixed pair like CASH/ONLINE is safe as a real enum. Something already promised to be configurable, like assignment strategies, needs the flexibility of a lookup table.
Why A is wrong: frequency of runtime use has nothing to do with this decision; the deciding factor is stability of the value set over time, not how often the field is read or written.
Why C is wrong: this overcorrects into treating every domain concept identically, ignoring that a genuinely fixed, small value set (like GateType or PaymentMode) gains nothing from the extra complexity of a lookup table and loses compile-time type safety in the process.
Why D is wrong: this ignores the entire reason SpotAssignmentStrategyType needs to support new values without a redeploy; a plain enum would require a code change and recompilation every time a new assignment strategy is added, directly contradicting R8's configurability requirement.
Hidden Pitfalls
Applying the lookup-table treatment to every enum-like field uniformly: not every value set benefits equally; a genuinely fixed pair like GateType gains nothing from the extra join and loses the compile-time safety a real Java enum provides.
Using a plain Java enum for a value set already promised to be configurable: this directly contradicts requirements like R5 and R8, which specifically called for fee calculation and spot assignment to be swappable without a redeploy.
Forgetting that the deciding test is stability, not size or usage frequency: a small value set isn't automatically a safe enum candidate if it's expected to grow; the test is specifically about whether new values might need to be added without a code change.
Section 4: Finishing the Schema
What It Means

Both new ideas, proper enum tables and inheritance where needed, are now applied to finish every table.

Practical Mechanics: Parking Lot
parking_lot's primitive columns: id, status_id, allotment_strategy_id, fees_calculator_strategy_id.
parking_lot
| id | status_id | allotment_strategy_id | fees_calculator_strategy_id |

Which vehicle types a lot allows, is that a simple column, or does it need something else? A mapping table. One lot allows many vehicle types, and one vehicle type is allowed across many lots. That's M:M.
allowed_vehicle
| parking_lot_id | vehicle_type_id |

vehicle_type
| id | value |

parking_lot_status
| id | value |

allotment_strategies
| id | value |

fees_calculator_strategies
| id | value |

Practical Mechanics: Parking Floor and Gates
parking_floor: id, floor_name, parking_lot_id (foreign key, since Parking Lot : Floor is 1:M).
parking_floor
| id | floor_name | parking_lot_id |

gates: id, number, parking_lot_id, gate_type_id, operator_id, gate_status_id.
gates
| id | number | parking_lot_id | gate_type_id | operator_id | gate_status_id |

gate_type
| id | value |

gate_status
| id | value |

Practical Mechanics: Parking Spot, a Real Design Question Worth Stopping For
Recall R2 from Post-Read 5: "a vehicle can only be given a spot of its exact type, no squeezing." Simple rule on paper. But now, actually building this spot by spot, what physically decides whether a vehicle fits into a spot? The size of the spot, compared to the size of the vehicle.
Rough size order, small to large:
BIKE  <  CAR  <  TRUCK

If a spot is physically built big enough to fit a truck, could that same physical spot also fit a car? Could it fit a bike? Or two bikes, side by side? Yes, a truck-sized spot is big enough to easily fit a car, or a bike, or even more than one bike at once, since it has plenty of extra space.
Flipping it around: could a bike-sized spot ever fit a car? No, a bike spot is too small. A car simply won't physically fit there.
So the real rule isn't "one spot, one exact type." It's:
A spot built for a bigger vehicle can ALSO hold smaller vehicles.
A spot built for a smaller vehicle can NEVER hold bigger vehicles.

BIKE spot   → fits BIKE only
CAR spot    → fits CAR, and BIKE
TRUCK spot  → fits TRUCK, CAR, and BIKE

Why this actually matters for the business, not just for correctness: if every truck spot could only ever hold a truck, and 80% of truck spots sit empty most of the day, what's being wasted? A lot of usable parking space. Those large spots could easily serve bikes or cars whenever no truck needs them, instead of sitting empty. This is a real optimization, not just a technical detail. Letting bigger spots serve smaller vehicles means the parking lot uses its space far more efficiently.
Given all this, should ParkingSpot store just ONE vehicleType, or something else? A list of vehicle types it can support, based on its size. A truck spot's list includes TRUCK, CAR, and BIKE. A bike spot's list includes only BIKE. This is a genuine refinement on R2, not a contradiction of it. Exact type matching is still being done; it's just that "exact type" needs to be checked against a list a spot supports, not a single fixed label.
parking_spot
| id | number | parking_floor_id | parking_spot_status_id |

supportedVehicleTypes : List<VehicleType>   ← based on spot SIZE

In terms of cardinality: a ParkingSpot can support several VehicleTypes. And a single VehicleType, like BIKE, is supported by many different spots across the lot (bike spots, car spots, and truck spots all support BIKE). What's the cardinality between ParkingSpot and VehicleType? Many-to-many, both sides can have many of the other. That needs a mapping table, not a foreign key on either side.
parking_spot
| id | number | parking_floor_id | parking_spot_status_id |

parking_spot_status
| id | value |

supported_vehicle_types
| parking_spot_id | vehicle_type_id |

What the Animation Shows: Many-to-Many, FK vs Mapping Table

Two table designs sit side by side for comparison, a naive single-column attempt and a proper mapping table.
Spot A needs to allow both Bicycle and Scooter, the naive side crams both into one comma-separated cell (flagged as a violation), while the clean side simply adds two separate rows, one per type.
Spot B needs three types (Sedan, SUV, Compact), the naive cell gets even more crowded and is flagged again, while the clean side just adds three more individual rows.
Spot C needs four types (Pickup, Semi, Van, Box Truck), the naive cell is now flagged a third time, with a note that a reliable search for just "Van" isn't possible without fragile string parsing, while the clean side adds four more rows, reaching 9 total.
A closing summary contrasts "0 violations, easy queries, proper indexing" on the mapping-table side against the repeated 1NF violations on the naive side.
This makes concrete exactly why cramming multiple vehicle types into a single column breaks down, watching the naive cell get more crowded and less reliable with every added type. It directly confirms why supported_vehicle_types needs to be its own table with one row per spot-type pair, rather than a single column trying to hold a list.
Answering the paired instructor question ("Using the naive comma-separated version, how would you even write a query to find every spot that supports 'Van'?"): with a comma-separated text column, finding every spot supporting "Van" would require a fragile pattern-matching query (something like WHERE types LIKE '%Van%'), which is slow (it can't use a proper index efficiently), error-prone (it could accidentally match a substring inside a longer unrelated value), and impossible to reliably combine with other structured filters. The mapping table avoids all of this entirely, since finding matching spots is a simple, indexed WHERE vehicle_type_id = 'Van' join.
Quiz Recap

In our current design: one ParkingSpot can support multiple VehicleTypes (based on size), and one VehicleType (like BIKE) is supported by many different spots across the lot (bike spots, car spots, and truck spots all support BIKE). Given this, why does supported_vehicle_types need to be a separate mapping table, instead of just a foreign key on one side?

A) Because ParkingSpot has many VehicleTypes, a foreign key on parking_spot pointing to one vehicle_type_id isn't enough to store more than one value
B) Because VehicleType also has many ParkingSpots, a foreign key on vehicle_type pointing to one parking_spot_id isn't enough either
C) Both A and B, since BOTH sides can have many of the other, neither side can hold a single foreign key; only a separate mapping table can represent this correctly (correct)
D) Because ParkingSpot and VehicleType are unrelated entities, so no direct relationship should exist between them at all
Correct answer: C. A mapping table is only needed when the relationship is genuinely many-to-many, meaning both sides fail the "single foreign key" test. Here, a spot supports many types (rules out a foreign key on parking_spot), and a type is supported by many spots (rules out a foreign key on vehicle_type). Since neither table can hold just one foreign key value, supported_vehicle_types is the only correct way to represent it.
Why A is wrong on its own: it correctly identifies half of the problem (a spot having many types) but stops short of recognizing that the reverse direction also fails, which is what actually forces the need for a mapping table rather than a differently-placed single foreign key.
Why B is wrong on its own: symmetrically, it identifies only the other half of the problem; either A or B alone would suggest that simply moving the foreign key to the other table might solve things, when in fact neither placement works.
Why D is wrong: a real, meaningful relationship clearly exists between ParkingSpot and VehicleType (which types a spot can accommodate); the correct response to a many-to-many relationship is a mapping table, not the false conclusion that no relationship should be modeled at all.
Practical Mechanics: Operators, Tickets, Bills, Payments
operators: id, employee_id, name, and email, added after noticing a mismatch between the class diagram and an earlier note in Post-Read 5.
operators
| id | employee_id | name | email |

tickets: id, number, entry_time, plus foreign keys, vehicle_id, parking_spot_id, gate_id, operator_id.
tickets
| id | number | entry_time | vehicle_id | parking_spot_id | gate_id | operator_id |

bills: id, exit_time, amount, plus ticket_id, gate_id, operator_id, bill_status_id.
bills
| id | exit_time | amount | ticket_id | gate_id | operator_id | bill_status_id |

bill_status
| id | value |

payments: id, time, amount, reference_number, payment_mode, payment_status_id, bill_id.
payments
| id | time | amount | reference_number | payment_mode | payment_status_id | bill_id |

payment_status
| id | value |

Detail work still remains: finishing every column precisely, matching the class diagram exactly, and a second schema for a separate assignment problem. Both are left as homework.
Hidden Pitfalls
Treating R2's "exact type match" as literally one label per spot, without questioning what physically determines fit: the entire size-based rethink in this section only surfaces because the physical reality (spot size versus vehicle size) was examined directly, rather than trusting the original wording of the requirement at face value.
Missing that a size-based hierarchy (bike < car < truck) implies asymmetric compatibility: assuming compatibility is symmetric (if a truck spot fits a car, a car spot must fit a truck) would be a serious modeling error; the direction of the "bigger can hold smaller" rule only goes one way.
Storing supported vehicle types as a comma-separated string column: as the animation demonstrates, this breaks normalization, makes querying for a specific type unreliable and slow, and gets progressively worse as more types are added to any single spot.
Applying the M:M mapping-table pattern without checking that both sides genuinely have "many": not every relationship discovered while building a schema is many-to-many; each one still needs the explicit both-sides check demonstrated in this quiz.
Section 5: Coding the Models
What It Means

Before writing a single class, the code organization is set up first.

com.example.parkinglot
 ├── models
 └── controllers

Every model class needs an ID. Most real systems also want to know when a record was created, and when it was last changed. Instead of repeating those three fields in every class, what should be done? Put them in one shared base class, and have every model extend it.
public class BaseModel {
    private Long id;
    private Date createdAt;
    private Date lastModifiedAt;

    // getters and setters
}

Should any of these fields be public? No, everything stays private, with getters and setters, the same rule since Module 1.
Practical Mechanics: ParkingLot
Based on the class diagram, what does ParkingLot hold? Its floors, its gates, which vehicle types it allows, its status, and both strategies.
public class ParkingLot extends BaseModel {
    private List<ParkingFloor> parkingFloors;
    private List<Gate> gates;
    private List<VehicleType> vehicleTypes;
    private ParkingLotStatus parkingLotStatus;
    private SpotAssignmentStrategyType spotAssignmentStrategyType;
    private FeesCalculatorStrategyType feesCalculatorStrategyType;

    // getters and setters
}

parkingLotStatus, spotAssignmentStrategyType, and feesCalculatorStrategyType are all written as single fields, not lists. Why should these be single values, not lists? A parking lot only has ONE current status at a time, it can't be both OPEN and CLOSED at once. Same logic for the current strategy in use, one active strategy at a time. This is the same reflex used all module: before accepting a field's type, ask whether the thing actually needs to hold many values, or just one. A list here would be a real mistake, even if it looks harmless at first glance.
Practical Mechanics: Gate
What does Gate hold? Its type, its number, the operator currently there, and its status.
public class Gate extends BaseModel {
    private GateType gateType;
    private int gateNumber;
    private Operator currentOperator;
    private GateStatus gateStatus;

    // getters and setters
}

Should GateType be a real Java enum, or a BaseModel-extending lookup class? A real Java enum, already decided in Section 3, since ENTRY/EXIT will never realistically change.
Practical Mechanics: ParkingSpot
What does ParkingSpot hold, based on the size discussion just worked through? A list of supported vehicle types, its own status, its spot number, and which floor it's on.
public class ParkingSpot extends BaseModel {
    private List<VehicleType> supportedVehicleTypes;
    private ParkingSpotStatus parkingSpotStatus;
    private int spotNumber;
    private ParkingFloor parkingFloor;

    // getters and setters
}

This field really is a list, supportedVehicleTypes, because of the size reasoning just worked through. This differs from parkingLotStatus above, which had to be a single value. The same lesson each time: check what the situation actually requires, don't just copy the shape of the last field written.
Practical Mechanics: Vehicle, Operator
public class Vehicle extends BaseModel {
    private String number;
    private VehicleType vehicleType;
    private String ownerName;

    // getters and setters
}

public class Operator extends BaseModel {
    private int empId;
    private String name;

    // getters and setters
}

Practical Mechanics: Ticket
What does Ticket need, based on the schema? A ticket number, entry time, the vehicle, the assigned spot, which gate it was made at, and which operator made it.
public class Ticket extends BaseModel {
    private String number;
    private Date entryTime;
    private Vehicle vehicle;
    private ParkingSpot assignedSpot;
    private Gate generatedAt;
    private Operator generatedBy;

    // getters and setters
}

Practical Mechanics: Bill
public class Bill extends BaseModel {
    private Date exitTime;
    private int amount;
    private Ticket ticket;
    private Gate gate;
    private Operator generatedBy;
    private BillStatus billStatus;
    private List<Payment> payments;

    // getters and setters
}

Should Bill also remember which fee-calculation strategy actually produced this exact amount, in case pricing rules change later and someone needs to check an old bill? That's reasonable to want, but if added, it should be a single reference, not a list, since a bill is calculated by exactly one strategy at the time it's made. This is the same idea as Ticket.operator from Post-Read 5: Gate tells you who's currently stationed there, Ticket.operator remembers who was there at that specific moment. If added to Bill, this field would be a snapshot of which rule made this exact amount, not a changing, current value.
Practical Mechanics: Payment
What does Payment need? Its mode, amount, time, status, and a reference number for online payments.
public class Payment extends BaseModel {
    private PaymentMode paymentMode;
    private int amount;
    private Date time;
    private PaymentStatus paymentStatus;
    private String referenceNumber;

    // getters and setters
}

PaymentMode should be a real Java enum, same reasoning as GateType. But PaymentStatus, plain enum, or lookup-table-backed? PaymentStatus probably deserves the full lookup-table-backed class. Statuses like PENDING, SUCCESS, FAILED, REFUNDED are more likely to expand as new payment flows get added, compared to a fixed pair like CASH/ONLINE. The same test is applied every time, rather than guessing.

Every remaining class follows the exact same shape: VehicleType, ParkingLotStatus, GateStatus, ParkingSpotStatus, BillStatus, SpotAssignmentStrategyType, FeesCalculatorStrategyType.

public class VehicleType extends BaseModel {
    private String value;
    // getters and setters
}
// Same shape for: ParkingLotStatus, GateStatus, ParkingSpotStatus,
// BillStatus, SpotAssignmentStrategyType, FeesCalculatorStrategyType

Hidden Pitfalls
Making a status or strategy field a list out of copy-paste habit: ParkingLot's parkingLotStatus, spotAssignmentStrategyType, and feesCalculatorStrategyType must each be single values, since a lot has exactly one active status and one active strategy at any given time; treating them as lists misrepresents the domain.
Making supportedVehicleTypes a single value instead of a list: this would directly undo the size-based rethink from Section 4, reintroducing the exact "one exact type only" limitation that was just identified as incomplete.
Skipping the enum-versus-lookup-table test for a new field just because a similar field nearby already made that decision: each field's stability needs to be assessed on its own; PaymentMode and PaymentStatus sit right next to each other on the same class but land on opposite sides of the test.
Section 6: Coding the Controllers, and DTOs
What It Means

With the models complete, the next question is how someone actually uses this system, issuing a ticket, generating a bill, and so on.

Issuing a ticket is a create operation. What other three operations, together with create, make up the classic set always checked for on any model? CRUD, Create, Read, Update, Delete.
Step 1: Find which model needs CRUD-style operations.
        Example: Ticket needs "issue a ticket" → a create.

Step 2: Create a controller for that model.
Step 3: Add a method for that specific use case.

public class TicketController {
    public Ticket issueTicket(Vehicle vehicle, Gate gate, Operator operator) {
        // logic to assign a spot, build a Ticket, return it
    }
}

Running Example 1: What Actually Breaks When the Model Changes

Say two different parts of the system both call issueTicket() today:

// Caller A — the mobile app's entry-gate screen
Ticket ticket = ticketController.issueTicket(vehicle, gate, operator);
displayTicketNumber(ticket.getNumber());
displayEntryTime(ticket.getEntryTime());

// Caller B — a nightly report generator
Ticket ticket = ticketController.issueTicket(vehicle, gate, operator);
totalTicketsToday.add(ticket);

Both callers are happy. Neither cares about anything except getNumber() and getEntryTime(). Now, three months later, product asks for a new feature: every Ticket must also store a securityClearanceLevel, marked required in the constructor.
public class Ticket extends BaseModel {
    private String number;
    private Date entryTime;
    private Vehicle vehicle;
    private ParkingSpot assignedSpot;
    private Gate generatedAt;
    private Operator generatedBy;
    private SecurityClearanceLevel securityClearanceLevel;  // NEW, required

    public Ticket(String number, Date entryTime, Vehicle vehicle,
                   ParkingSpot assignedSpot, Gate generatedAt,
                   Operator generatedBy, SecurityClearanceLevel level) {
        // constructor signature changed
    }
}

Caller A and Caller B never asked for securityClearanceLevel. They never even knew it existed. What happens to them right now? If the constructor signature changed, anything that builds a Ticket directly won't even compile anymore. And even if issueTicket() itself still compiles, both callers are now silently depending on a Ticket shape that's grown; one unrelated feature request just forced changes to ripple into code that had nothing to do with security clearance. Neither caller cares about security clearance, neither should even need to know it exists. But because they're holding the entire real model, any change to that model is a change to their world too, whether they asked for it or not.

What the Animation Shows: Raw Model vs DTO Controller Boundary

A Ticket model with [id, title, status] appears, and the controller is shown returning this raw object directly, no abstraction in between.
Mobile App and Report Generator both connect straight to the raw model, reading ticket.id, ticket.title, ticket.status directly, visibly tightly coupled to the exact shape of Ticket.
A new internal field, securityClearanceLevel, gets added, flagged as sensitive, and the animation shows it leaking straight down into both Mobile App and Report Generator, since nothing is stopping it.
Then a TicketDTO gets introduced, exposing only [id, title, status], and the controller is shown mapping Ticket → TicketDTO before anything reaches a caller.
securityClearanceLevel is shown rippling down again, but this time it visibly stops right at the DTO boundary, never reaching Mobile App or Report Generator, who still only ever receive the same three original fields.
This is a literal, watchable version of Caller A and Caller B from the lecture, same two callers, same new field, same before-and-after contrast. It makes the DTO's role unmistakable: it's not just a smaller model, it's a wall that stops anything not explicitly listed on it from ever reaching a caller.
Answering the paired instructor question ("At this exact frame, which line of code is actually responsible for this leak happening at all?"): the leak happens specifically at the line where the controller method returns the raw Ticket object directly to the caller (return ticket; in the pre-DTO version), rather than mapping it to a filtered, explicitly-defined response object first. Any caller holding that raw object automatically has access to every field it contains, including ones added long after that caller's code was written.
Running Example 2: What Actually Gets Exposed, and to Whom
Say the Parking Lot company partners with a third-party billing service, an outside company that just needs to confirm "a ticket was issued, at this time, for this spot," so they can log it for invoicing.
If issueTicket() returns the raw Ticket model directly to that billing partner, what does the billing partner now have access to, that they almost certainly shouldn't? Everything on Ticket, including things like generatedBy (the actual Operator object, with their empId and internal name), assignedSpot (full internal spot object), and now even securityClearanceLevel, none of which a billing partner has any real business seeing.
Raw Ticket, handed to an outside billing partner, exposes:
- generatedBy → full Operator object (empId, name — internal HR data)
- assignedSpot → full ParkingSpot object (internal spot IDs, status)
- securityClearanceLevel → internal security data, none of their business
- vehicle → full Vehicle object, more than just "was a ticket issued"

The billing partner only actually needed:
- ticketNumber
- entryTime
- (maybe) spot number, for their own invoicing reference

What the Animation Shows: DTO Data Exposure Filtering

All 8 fields on the Ticket entity appear first, nothing has passed through to the DTO yet.

One by one, the fields the billing partner actually needs get checked and pass through the filter: number, entryTime, customerName, totalAmount, each one shown flowing through into the outgoing DTO.

Then, one by one, the sensitive fields get explicitly BLOCKED: securityClearanceLevel, internalAuditId, adminNotes, systemHashKey, each one flagged with a reason for why it must never leave the system boundary.

Toggling the checkboxes on the DTO filter allows control over which fields pass through, watching fields move from "blocked" to "included" and back.

The end state clearly separates two groups side by side: what the billing partner receives versus what stayed behind, sealed off inside the system.

This makes the abstract "billing partner shouldn't see Operator or security data" concern into a literal checklist enforced field by field. It reinforces that a DTO isn't just "fewer fields," it's a deliberate, field-by-field decision about what's safe to expose, with a real reason attached to every block.

Answering the paired instructor question ("What's the realistic worst-case outcome if this specific field had leaked to an outside billing partner?"): a field like systemHashKey leaking to an external party could expose internal implementation details (such as an internal identifier scheme or a security-relevant hash) that could be used to infer system internals, forge or guess related identifiers, or otherwise be exploited in ways the internal system was never designed to defend against from an external actor; at minimum it represents an unnecessary and avoidable exposure of internal system details to a party with no legitimate need for them.

Who exactly is at risk here, is this just a "nice to have" cleanliness issue, or a real problem? It's real. Internal employee data (Operator), and internal security data, are now sitting inside an object handed to an outside company, data they were never supposed to receive, just because they asked for confirmation of a ticket. This is precisely the second problem named earlier: raw models expose everything, whether the caller needs it or not, and whether it's safe to expose or not. It doesn't matter that the billing partner wouldn't misuse empId, it matters that the system handed it to them at all.

Practical Mechanics: The DTO Fix
Problem with passing/returning raw models directly:
1. If the model changes shape later, every caller can break —
   even ones that never cared about the new field.
   (Just saw this: Caller A and B, broken by an unrelated
   security-clearance feature.)
2. Raw models expose everything, including internal fields
   that outsiders have no business seeing.
   (Just saw this: the billing partner receiving Operator and
   security data they never asked for.)
3. Handling missing/null values gets messy without a clear
   contract for what's actually required.

The fix: a dedicated object just for this conversation, carrying exactly what's needed, in exactly one direction.

DTO = Data Transfer Object

- Used to communicate with anything OUTSIDE our system.
- Looks similar to a model, but rarely identical.
- Hides internal details — only shares what's actually needed.
- Every controller method gets its own Request DTO and its own
  Response DTO — so changing one use case never breaks another.

public class IssueTicketRequestDTO {
    private String vehicleNumber;
    private VehicleType vehicleType;
    private String ownerName;
    private Long gateId;
    private Long operatorId;

    // getters and setters
}

public class IssueTicketResponseDTO {
    private String ticketNumber;
    private Date entryTime;
    private int assignedSpotNumber;
    private int assignedFloorNumber;

    // getters and setters
}

public class TicketController {
    public IssueTicketResponseDTO issueTicket(IssueTicketRequestDTO request) {
        // build the real Ticket internally, using request's data
        // return only what the caller actually needs to know
    }
}

Re-running both examples with this new version. First, Ticket gains that securityClearanceLevel field tomorrow. Does IssueTicketResponseDTO need to change at all? Do Caller A or Caller B need to change anything? No, the DTO only has the four fields explicitly chosen to expose. Ticket can grow internally however it needs to, and both callers keep working exactly as before, completely unaffected.
Second, the billing partner now calls issueTicket() and gets back an IssueTicketResponseDTO. Do they see Operator, securityClearanceLevel, or anything about internal spot objects? No, they only ever see ticketNumber, entryTime, assignedSpotNumber, assignedFloorNumber. Nothing internal is even reachable from the DTO, because it was never put there in the first place. That's the whole point of a DTO. It's not just "a smaller model," it's a deliberate, one-way boundary. Whatever isn't explicitly placed on the DTO simply cannot leak out, no matter how much the internal model grows later.

What the Animation Shows: Internal Model Change Breaking Callers, Ripple Effect

Ticket starts as {id, title, assignee}, with all callers shown depending directly on this exact shape.
A new requirement forces securityClearanceLevel onto Ticket, the model changes, and without a DTO layer, this new field ripples straight down: Caller A breaks, then Caller B also breaks, both turning red.
The animation then rewinds and replays the same scenario, but this time with a DTO layer sitting between Ticket and the callers, the DTO maps only {id, title, assignee} through, absorbing the change.
This time, Caller A and Caller B both stay green and unaffected, even though the exact same field was added to Ticket underneath.
A closing summary states the contrast directly: "Without DTO: 1 change → 2 broken callers. With DTO: 1 change → 0 broken callers."
This directly confirms the answer to "does Caller A or Caller B need to change anything" by showing the same change played out twice, once breaking everything, once breaking nothing. The closing "1 change → 2 broken vs 0 broken" summary gives a crisp, memorable number to attach to the whole idea of a DTO boundary.
Answering the paired instructor question ("If we'd added a second new field on top of securityClearanceLevel next month, would that '0 broken callers' number change at all, with the DTO in place?"): no, the count would stay at 0 broken callers, since any additional internal field added to Ticket would similarly stop at the DTO boundary unless it was deliberately added to the DTO itself. The DTO's protection isn't a one-time effect tied to this specific field; it holds for every future internal change, which is exactly why it's described as a durable, deliberate boundary rather than a one-off fix.
Quiz Recap

TicketController.issueTicket() currently takes raw Vehicle and Gate model objects as parameters, and returns a raw Ticket model. What's the strongest reason to replace these with dedicated DTOs?

A) DTOs make the method run measurably faster
B) If Vehicle or Ticket's internal fields ever change, every single caller of issueTicket() could break, even ones that never needed the new field (correct)
C) Java doesn't technically allow model classes as method parameters
D) DTOs remove the need to write getters and setters
Correct answer: B. This is the exact coupling problem walked through with Caller A and Caller B. A DTO creates a stable, deliberate contract between issueTicket() and whoever calls it, so changes to the internal model don't ripple out and break unrelated code.
Why A is wrong: DTOs are not primarily a performance optimization; their value is architectural (decoupling and controlled exposure), not measured in execution speed.
Why C is wrong: this is factually false; Java has no restriction preventing model classes from being used as method parameters or return types. The reason to avoid it is a design choice, not a language limitation.
Why D is wrong: DTOs are themselves classes that still need getters and setters (as shown in IssueTicketRequestDTO and IssueTicketResponseDTO above); they don't eliminate this requirement, they simply apply it to a different, smaller, purpose-built class.
Hidden Pitfalls
Returning or accepting raw model objects directly at a controller boundary: this is the root cause of both problems demonstrated in this section, unrelated model changes rippling out to unaffected callers, and internal fields being exposed to parties who have no legitimate need for them.
Reusing the same DTO across multiple unrelated controller methods: each method should get its own dedicated Request and Response DTO pair; sharing one DTO across use cases reintroduces the same coupling problem DTOs exist to prevent, since a change needed for one use case can now unexpectedly affect another.
Assuming a DTO is "just a smaller model" rather than a deliberate boundary: this framing misses the point that what's excluded from a DTO matters as much as what's included; the value comes from the fields that are deliberately never placed there, not merely from having fewer fields overall.
Section 7: AI Corner, Spot the Mistakes, Don't Generate
What It Means

This mirrors the same closing AI Corner structure used in Post-Reads 3 through 5: a deliberately flawed class is written in advance, AI is asked only to diagnose, not fix, each issue is matched back to something already known, and the fix is applied using the design already built by hand. This time, the flawed code exercises today's two new ideas (DTOs, proper enum handling) plus one older idea (exception-over-null).

Practical Mechanics: The Flawed Controller
public class TicketController {

    public Ticket issueTicket(Vehicle vehicle, Gate gate, Operator operator) {
        Ticket ticket = new Ticket();
        ticket.setVehicle(vehicle);
        ticket.setGeneratedAt(gate);
        ticket.setGeneratedBy(operator);
        ticket.setEntryTime(new Date());

        if (gate.getGateType().toString().equals("EXIT")) {
            System.out.println("Cannot issue ticket at an exit gate");
            return null;
        }

        return ticket;
    }
}

Reading this, several things already feel off, worth sitting with before the AI diagnosis below.

AI's Diagnosis

Prompt used:

"Here's a TicketController from a Parking Lot machine coding
problem. We just learned two things in this lecture: controller
methods should use dedicated Request/Response DTOs instead of
raw models, and GateType is a proper Java enum, not a raw string.
Can you review this method and tell me what's wrong with it, and
why? Don't rewrite it yet — just point out the problems."

[paste the TicketController above]

AI's response, diagnosing the problems:

A few real issues here:

1. This method takes raw Vehicle, Gate, and Operator models
   directly as parameters, and returns a raw Ticket model
   directly. This tightly couples every caller to the exact
   shape of these models — a change to Ticket later could break
   every caller, even unrelated ones.

2. `gate.getGateType().toString().equals("EXIT")` converts an
   enum into a string just to compare it. Since GateType is
   already a proper Java enum, this should just be a direct
   enum comparison. Converting to a string throws away all the
   type-safety an enum gives you in the first place.

3. When the gate is an exit gate, this method just returns
   `null` and prints a message. A caller that isn't expecting
   `null` could crash the moment this happens. There's no clear
   contract telling the caller this can even happen.

Matching each of AI's three points to something already known:
Point 1: the DTO problem just built in Section 6, raw models crossing the controller boundary.
Point 2: GateType is a real enum; comparing it as a string throws away the whole point of using an enum instead of raw text.
Point 3: returning null silently is a known trap, the same category of issue as EasyBotPlayingStrategy returning null on a full board, from Post-Read 4.
Every single issue traces back to something already given a name for. That is the whole reason these ideas are learned properly first, spotting them afterward becomes almost automatic.
The Corrected Version
public class TicketController {

    public IssueTicketResponseDTO issueTicket(IssueTicketRequestDTO request) {
        Gate gate = fetchGate(request.getGateId());

        if (gate.getGateType() == GateType.EXIT) {
            throw new InvalidGateException("Cannot issue a ticket at an exit gate");
        }

        // build the real Ticket internally using request data
        Ticket ticket = buildTicket(request, gate);

        return toResponseDTO(ticket);
    }
}

The silent null return was replaced with throwing an exception instead. Why is that a better contract for a caller? A caller is forced to either catch the exception or let it propagate; it can't accidentally ignore the failure the way it could silently ignore a null return. This is the same discipline as InvalidMoveException in Post-Read 4.
What AI Actually Contributed
Same rule, every AI Corner this course: generate fast, but the
judgement calls are yours to make and yours to check.

What did AI do here, and what did it not do? It correctly named three real problems, using ideas already known. It did not design the fix; the DTO pattern and the exception-over-null habit both came from work already done independently.
Hidden Pitfalls
Using .toString().equals(...) to compare an enum value: this silently discards compile-time type safety, since a typo in the string literal (like "EXITT") would compile fine but never match, producing a bug that's invisible until runtime.
Returning null to signal a failure condition instead of throwing a named exception: this creates a silent contract violation, since nothing forces a caller to check for null, unlike an exception, which forces explicit handling or propagation.
Accepting raw models as controller method parameters, even after learning about DTOs: recognizing the DTO problem in theory and still writing code that skips it in practice suggests the lesson hasn't yet become an automatic habit; the whole value of this AI Corner exercise is training that automaticity.
Wrap-Up: Tying It Together
Built today:
- Inheritance in schema: one parent table for common attributes,
  child tables only for special attributes — no more UNION queries
- Enum representation: naive string storage vs. lookup-table
  classes — and a real test for when a plain Java enum is fine
  (GateType, PaymentMode) vs when you need the full lookup table
  (SpotAssignmentStrategyType, PaymentStatus)
- Completed schema: every table, every FK
- A real design catch: ParkingSpot needed a size-based rethink —
  bigger spots (TRUCK) can support smaller vehicle types (CAR,
  BIKE), but not the reverse. This turned "one exact type" into
  "a list of supported types," and created a genuine M:M
  relationship (ParkingSpot ↔ VehicleType, via
  supported_vehicle_types)
- All model classes written, extending BaseModel
- Caught real mistakes ourselves while building models: status
  and strategy fields on ParkingLot should be single values,
  not lists
- Controllers: how to find CRUD use cases, and why raw models
  should never cross the controller boundary
- DTOs: Request/Response objects that protect callers from
  internal model changes

Known gap, left as homework:
- Full schema detail work, and a second schema for the
  assignment problem
- Controllers still needed for ParkingLot, Bill, and Payment
- The two-gates-one-spot problem is STILL not solved — that's
  coming once we're further into the actual code

Everything new in this document, inheritance, enum tables, DTOs, and the spot-size rethink, solved a real problem that could actually be felt, not something memorized as an abstract rule. The ParkingSpot size question came up naturally, while actually building the model, not because a place to fix something was being sought. That is how real design gaps usually get found: while building, not just while planning. Writing model code out loud, together, is exactly how mistakes like a list where a single value belongs get caught, the same habit that works in a real interview, and on a real team.

The next document in this series finishes the remaining controllers, and finally deals with the problem flagged in Post-Read 5, two gates trying to grab the same parking spot at the same time. That is where real concurrency enters this module.

Common Pitfalls Summary
1. Duplicating common attributes across every child table in an
   inheritance hierarchy.
   -> Forces a union query for even the simplest question, and
      the problem multiplies with every new subtype added.

2. Forgetting the foreign key direction runs from child to parent
   in an inheritance schema.
   -> Each child table holds the FK pointing up; the parent
      table holds no reference down to its children.

3. Applying the lookup-table treatment to every enum-like field
   uniformly, regardless of stability.
   -> A genuinely fixed pair like GateType gains nothing from
      the extra join and loses compile-time enum safety.

4. Using a plain Java enum for a value set already promised to be
   configurable (like SpotAssignmentStrategyType).
   -> Directly contradicts requirements calling for that value
      set to grow without a code redeploy.

5. Assuming compatibility between spot size and vehicle type is
   symmetric.
   -> A truck spot fitting a car does NOT mean a car spot fits
      a truck; the "bigger holds smaller" rule only runs one way.

6. Storing supported vehicle types as a comma-separated string
   column instead of a mapping table.
   -> Breaks normalization, makes searching for a specific type
      unreliable, and gets worse as more types are added per spot.

7. Making a status or strategy field a List when the domain only
   ever has one active value at a time.
   -> ParkingLot's status and strategy fields must be single
      values; a list here misrepresents the domain.

8. Skipping the enum-vs-lookup-table test for a new field just
   because a nearby field already made that decision.
   -> PaymentMode and PaymentStatus sit on the same class but
      land on opposite sides of the test; each field needs its
      own check.

9. Returning or accepting raw model objects directly at a
   controller boundary.
   -> Causes unrelated model changes to ripple out and break
      callers who never needed the new field, and exposes
      internal data to parties with no legitimate need for it.

10. Reusing one DTO across multiple unrelated controller methods.
    -> Reintroduces the same coupling problem DTOs exist to
       prevent, since a change for one use case can affect another.

11. Using .toString().equals(...) to compare an enum value.
    -> Silently discards compile-time type safety; a typo in the
       string literal compiles fine but never correctly matches.

12. Returning null to signal a failure instead of throwing a
    named exception.
    -> Creates a silent contract violation; nothing forces a
       caller to check for null the way an exception forces
       explicit handling.

Higher-Level Hidden Pitfalls (cross-cutting, not listed above):

Treating design gaps discovered during coding as failures of the earlier design session: the ParkingSpot size rethink is presented explicitly as a normal, expected part of the process, catching a refinement while building is a sign of a healthy workflow, not evidence that the original design session in Post-Read 5 was done poorly.
Applying every schema and modeling rule mechanically instead of re-deriving the reasoning each time: whether it's inheritance-as-tables, enum-as-lookup-table, or DTO boundaries, each rule in this document came from working through a concrete problem first; applying any of them as a checklist without re-confirming the underlying reasoning fits the current situation risks misapplying a rule where it doesn't actually belong.
Key Terminology
Term	Meaning in Simple Words
Table Inheritance (Class-Table Inheritance)	A schema pattern where a parent table holds attributes common to all subtypes, and each child table holds only its own special attributes plus a foreign key back to the parent.
Lookup Table (Enum Table)	A small dedicated table (an id and a value) used to represent a set of allowed values, letting new values be added by inserting a row instead of changing a table's structure or redeploying code.
DTO (Data Transfer Object)	A dedicated object used to communicate across a system boundary, exposing only the specific fields a particular caller needs, deliberately hiding everything else about the internal model.
Request DTO / Response DTO	A pair of DTOs, one carrying data into a controller method, one carrying data back out, each scoped specifically to that one method's use case.
BaseModel	A shared parent class holding fields common to every model in a system (such as id, createdAt, lastModifiedAt), so they don't need to be repeated in every individual model class.

Enums, the Strategy pattern, the Builder pattern, composition versus aggregation, and the class-to-table schema algorithm were already defined in Post-Read 1 through Post-Read 5 and are not redefined here.

Frequently Asked Interview Questions

1. Explain the class-table inheritance pattern, and why it's preferred over duplicating common attributes across every subtype table.
The pattern creates one table for the parent class holding every attribute common across all subtypes, and one table per child class holding only that child's unique attributes plus a foreign key back to the parent. This is preferred over duplication because duplicating common attributes (like name and price in the pen example) forces even simple queries, like getting every pen's name, to use a UNION across every subtype table. With the parent-holds-common-data pattern, that same query becomes a single, simple SELECT against the parent table, with no unions required, and this simplicity holds for any future question about shared attributes, not just the one demonstrated.

2. What is the deciding test for whether an enum-like value should be a plain Java enum or a lookup-table-backed class?
The deciding question is how likely the set of values is to change without needing a code deploy. A value set that is small and functionally permanent, like GateType (ENTRY/EXIT), fits a plain Java enum, since compile-time type safety is valuable and the set genuinely will not grow. A value set that is expected to grow, especially one a requirement has already promised to be configurable (like SpotAssignmentStrategyType, tied to R8's configurability requirement), needs the full lookup-table-backed class, so new values can be added as data rather than as a code change.

3. Walk through the reasoning that led to ParkingSpot storing a list of supported vehicle types instead of a single vehicle type field.
The original requirement (R2) stated a vehicle can only be given a spot of its exact type, which suggested one label per spot. But examining what physically determines fit revealed that spot size, not an arbitrary label, is what actually matters: a spot built for a truck is physically large enough to also fit a car or a bike, while a spot built for a bike cannot fit a car. This means a bigger spot can support multiple smaller vehicle types, which requires ParkingSpot to hold a list of supported types ([TRUCK, CAR, BIKE] for a truck spot) rather than a single fixed type. This also creates a genuine many-to-many relationship between ParkingSpot and VehicleType, requiring a supported_vehicle_types mapping table in the schema.

4. Why does the size-based rethink on ParkingSpot create a many-to-many relationship, and what would go wrong with a single foreign key on either side?
A single ParkingSpot can support several VehicleTypes (based on its size), and a single VehicleType, like BIKE, is supported by many different spots across the lot (bike spots, car spots, and truck spots all support BIKE). A foreign key on parking_spot pointing to one vehicle_type_id could only capture one supported type per spot, which contradicts a truck spot supporting three types. Symmetrically, a foreign key on vehicle_type pointing to one parking_spot_id could only capture one spot per type, which contradicts many spots supporting BIKE. Since neither side can be represented with a single foreign key, a separate mapping table is the only correct representation.

5. Explain, using the Caller A and Caller B example, why raw models should not cross a controller's boundary.
Caller A (a mobile app screen) and Caller B (a nightly report generator) both call issueTicket() and only use getNumber() and getEntryTime() from the returned Ticket. When an unrelated feature request adds a new required field (securityClearanceLevel) to Ticket, both callers are affected even though neither of them cares about that field, potentially failing to compile if the constructor changed, or silently depending on a Ticket shape that has grown without their knowledge. Because both callers hold the entire real model rather than a filtered subset, any change to that model becomes a change to their world too, regardless of whether they asked for it.

6. What specific risk does returning a raw model to an external party (like a third-party billing partner) introduce, beyond the coupling problem?
Returning a raw model exposes every field on it, regardless of whether the recipient has any legitimate need to see it. In the billing partner example, this would expose the full Operator object (internal HR-adjacent data like empId), the full ParkingSpot object (internal spot IDs and status), and even securityClearanceLevel, none of which the billing partner needs to simply confirm that a ticket was issued. This is a data exposure risk distinct from the coupling risk: even if the model never changes again, the raw model already contains more information than should ever leave the system boundary to an outside party.

7. What is a DTO, and how does it solve both the coupling problem and the data exposure problem simultaneously?
A DTO (Data Transfer Object) is a dedicated object used specifically for communication across a system boundary, deliberately including only the fields relevant to that particular use case. It solves the coupling problem because the DTO's shape is chosen once and stays stable regardless of how the internal model changes; a new internal field on Ticket never appears on IssueTicketResponseDTO unless explicitly added there. It solves the exposure problem for the same reason: since only explicitly chosen fields exist on the DTO, sensitive internal data like Operator details or securityClearanceLevel simply has no path to reach an external caller, because it was never placed on the DTO in the first place.

8. Why should every controller method get its own dedicated Request DTO and Response DTO, rather than sharing DTOs across methods?
Sharing a DTO across multiple use cases reintroduces the exact coupling problem DTOs are meant to prevent: a change needed to support one use case (adding a field to a shared Response DTO for one method) can now unexpectedly affect a completely different method that happens to reuse the same DTO. Giving each method its own dedicated DTO pair keeps each use case's contract independent, so a change driven by one feature's needs cannot silently ripple into an unrelated feature.

9. In the flawed TicketController example, why is comparing gate.getGateType().toString().equals("EXIT") considered worse than comparing the enum value directly?
GateType is already a proper Java enum, which gives compile-time type safety, the compiler can catch a typo in an enum reference immediately. Converting the enum to a string and comparing text throws that safety away: a typo like "EXITT" would compile without error and simply fail to match at runtime, producing a bug that's invisible until the specific code path executes. Comparing the enum value directly (gate.getGateType() == GateType.EXIT) preserves the type safety the enum was chosen for in the first place.

10. Why is throwing a named exception preferred over silently returning null when issueTicket() is called on an exit gate?
Returning null creates a silent failure path: nothing forces a caller to check for null before using the result, so a caller unaware of this possibility could crash later with a NullPointerException far from the actual point of failure, or worse, silently proceed with invalid state. Throwing a named exception (like InvalidGateException) forces the caller to either explicitly handle the failure or let it propagate visibly, making the failure condition part of the method's contract rather than a silent, easy-to-miss edge case. This mirrors the same discipline already established with InvalidMoveException in the TicTacToe lectures.

11. Why does ParkingLot.parkingLotStatus need to be a single field rather than a List<ParkingLotStatus>, even though other fields on the same class, like vehicleTypes, are correctly lists?
The deciding factor is whether the real-world thing being modeled can genuinely hold more than one value at once. A parking lot has exactly one current operational status at any given moment, it cannot simultaneously be both OPEN and CLOSED, so a single field correctly represents this. By contrast, a parking lot genuinely does allow multiple vehicle types simultaneously, so a list is correct there. The lesson is to check what the specific field represents in reality, rather than assuming every field on a class should follow the same shape as its neighbors.

12. Summarize the specific problem-solving pattern demonstrated by the ParkingSpot size rethink, and explain why it's presented as a normal, expected part of building software.
The pattern is: while implementing a previously agreed-upon requirement (R2's exact type matching) at a level of detail not previously considered (what physically determines whether a vehicle fits a spot), a gap or refinement in the original design becomes visible, and the design is updated on the spot rather than treated as a mistake to avoid. This is presented as normal and expected because building software inherently surfaces details that pure paper design cannot fully anticipate; catching and resolving such gaps during implementation, the same way a real engineering team would, is treated as a sign of a healthy process, not a failure of the earlier design session.

Self-Check Questions
In your own words, explain why a query to find the minimum price across all pens becomes trivial once inheritance is modeled with a parent table holding common attributes.
Trace through: using the class-table inheritance pattern, sketch the payments, cash_payments, and online_payments tables, including which columns live where and which table holds the foreign key.
Write a snippet: using the enum-vs-lookup-table test from Section 3, decide whether a hypothetical VehicleColor field (used only for record-keeping, never for business logic) should be a plain Java enum or a lookup-table-backed class, and justify your answer.
Compare the reasoning behind ParkingSpot.supportedVehicleTypes being a list to the reasoning behind ParkingLot.parkingLotStatus being a single value. What question determines which shape is correct in each case?
Explain, in your own words, why the relationship between ParkingSpot and VehicleType is many-to-many, and describe what would go wrong if a single foreign key were placed on parking_spot instead of using a mapping table.
Trace through: if Bill were given a feesCalculatorStrategyType field to record which strategy calculated its amount, explain why this should be a single reference and not a list, using the same reasoning applied to Ticket.operator.
Write a snippet: sketch a BillController with an issueBill method, using a dedicated IssueBillRequestDTO and IssueBillResponseDTO, following the pattern established for TicketController.
Compare what happens to Caller A and Caller B in the "without DTO" scenario versus the "with DTO" scenario, when a new required field is added to Ticket. Be specific about what breaks and what doesn't in each case.
Explain why gate.getGateType().toString().equals("EXIT") is a real problem even though it likely produces the correct result most of the time.
Trace through: rewrite the flawed TicketController.issueTicket() method's exit-gate check to throw an exception instead of returning null, and explain what a calling method would now need to do differently to handle this case correctly.
In your own words, explain why the ParkingSpot size rethink is described in this document as a "genuine design catch" rather than a mistake in the original design session.
Write a short paragraph describing how you would explain, to a teammate, the difference between a model class and a DTO, using the billing partner scenario as your example.
Further Reading
Post-Read 5, Machine Coding 5: Design Parking Lot - this document builds directly on the class diagram, the nine identified classes, and the original (incomplete) schema pass from that session; revisit it for the full requirements-gathering reasoning behind every class referenced here.
Post-Read 4, Machine Coding 4: Code TicTacToe 2 - the original source of the exception-over-null discipline (InvalidMoveException, the EasyBotPlayingStrategy null-return gap) directly reused in this document's AI Corner.
Post-Read 2, Machine Coding 2: Design TicTacToe - the original source of the class-to-table schema algorithm (foreign keys for 1:1/1:M, mapping tables for M:M), extended in this document with the two new ideas (inheritance-as-tables, enum-as-lookup-table).
Martin Fowler, Patterns of Enterprise Application Architecture - relevant background on both class-table inheritance mapping and the Data Transfer Object pattern, both introduced formally in this document.
Effective Java, Joshua Bloch (items on minimizing mutability and designing method signatures) - directly relevant to why DTOs are scoped narrowly per use case rather than reused broadly across a codebase.
Oracle Java Documentation on Enum Types - relevant reference for how Java enums provide compile-time type safety, directly connected to why .toString().equals(...) comparisons are discouraged in this document's AI Corner.
Homework
1. Complete the full schema design for Parking Lot — every
   column, matching your own class diagram exactly.

2. Complete the schema design for this week's separate
   assignment question. [INSTRUCTOR: reference the specific
   assignment problem shared with learners this week.]

3. Write controllers for ParkingLot, Bill, and Payment, using
   the same method: find the CRUD use case, name the controller,
   write the method, and use a Request/Response DTO pair for
   every method — no raw models crossing the controller boundary.

4. Push everything to GitHub — branch name: parkinglot-code-part1-complete

Last changed by 
 
Tushar Harsan·Follow
0
50
Add a comment
Published on  HackMD
