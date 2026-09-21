Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/BJNyvjMOGl

Post Read : Machine Coding - 8: Design BookMyShow
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Aug 31, 2026
POST-READ	Applied Design & Machine Coding	Machine Coding - 8: Design BookMyShow
Introduction

Post-Read 7 closed out the Parking Lot system as a working MVP: a real Service layer, every controller finished, and the "two gates, one spot" race condition proven fixed with two real Gate objects and a synchronized block. This document starts a brand-new system: BookMyShow, India's movie-ticketing platform, and it is a genuine milestone, not just another system to design the same way. It is the first system in this course built with a real database in mind from the start (MySQL, not an in-memory List), and it closes with a first look at the actual tooling (JPA, Spring Boot) that next session's code will depend on.

Running examples carried through this entire document: the physical hierarchy City → Theatre → Screen → Seat, the content-versus-instance pair Movie and Show, and the two purpose-built mapping classes ShowSeat (booking status) and ShowSeatType (pricing).
Today only covers three of the six framework steps: Overview, Requirements Gathering, and Class Diagram. Schema Diagram moves to the start of the next document (Code BookMyShow 1), exactly the same restructuring already done once before, when Schema moved to the start of Code Parking Lot 1.
This session's script contains no 🎬 Animation blocks. Every visual referenced in the live class was a static board diagram or screenshot, not an embedded animation, so no "What the Animation Shows" subsections appear anywhere in this document. Where the script pointed at a diagram, that diagram is reconstructed here as a plain-text class-box board note instead.
Section 5 is a real part of this session, not an added extra: a primer on JPA and Spring Boot, taught specifically so that next session's code doesn't have to pause and explain brand-new tooling in the middle of building BookMyShow.
Today's unsolved problem, named but deliberately not fixed yet, is "two users, one seat", the harder sibling of Parking Lot's "two gates, one spot," because it also has a time-based hold sitting on top of it. It gets solved with real threads once the Code lectures begin.
Section 1: Overview
What It Means
The same opening move as every design session in this course: align with an interviewer on what the system even means, before designing anything.
BookMyShow, in real life, sells tickets for movies, plays, concerts, and sports, all from one platform.
This session locks scope down hard: movies only. Plays, concerts, and sports are explicitly out of bounds for this MVP, the same kind of scope-lock discipline used for every prior system in this course.
A second, quieter scope decision sits right next to it: this system assumes a real MySQL database, not an in-memory list. That is a genuine change from every earlier system built so far.

[ASK LEARNERS] in the original script raised a sharp question worth restating here directly: does needing a real database change anything about how the class diagram gets built today?

The honest answer is: not really, not for the class diagram itself. A class is a class whether it eventually gets persisted to a List or to a MySQL table.
It matters far more once the Schema step is reached. Real persistence means real tables get built next class, not just designed on paper the way schema was handled for TicTacToe and Parking Lot.
This is exactly why Schema was deliberately moved to the start of the next session instead of being squeezed into today's already-packed 120 minutes: it deserves its own proper block of time, not a rushed final ten minutes.
Hidden Pitfalls
Assuming "we'll use a real database this time" changes today's class diagram: it does not. Persistence choice affects how classes eventually get stored, not what fields and relationships those classes need in the first place. Conflating the two leads to premature schema thinking creeping into a step that should stay focused purely on object modeling.
Treating scope lock as optional formality: without explicitly ruling out plays, concerts, and sports up front, it becomes very easy to accidentally design fields or relationships (like a generic "Event" abstraction) that serve a system twice the size of the one actually being asked for.
Section 2: Requirements Gathering
What It Means

Eighteen requirements are covered today, more than double Parking Lot's eight, walked through strictly in the order R1 to R18, exactly as numbered, so nothing looks quietly skipped. Most are quick facts. A handful demand real thinking, and those are where this document slows down.

R1 and R2: The Basic Shape
R1: Users book movie tickets.
R2: Users select their own seats while booking.

Nothing to debate here. This is the foundational shape of the entire system: users book tickets, and they pick their own seats rather than being auto-assigned one.
R3 to R6: The Physical Hierarchy
R3: BMS supports multiple cities, and each city can have
    multiple theatres.
R4: BMS only supports movie bookings.
R5: Each theatre has multiple screens; each screen has many seats.
R6: One screen runs only ONE movie at a time.

R4 simply reconfirms the scope lock already made in the Overview. Nothing new to reason about there.
R3, R5, and R6 together build out the full physical chain: City → Theatre → Screen → Seat.
This shape has already been seen once before in this course: it is the exact same tree as ParkingLot → ParkingFloor → ParkingSpot, one-to-many, all the way down.
It is also composition all the way down, for the same reason as Parking Lot: a Screen without a Theatre means nothing on its own, and neither does a Seat without a Screen. Composition is the right relationship whenever the child object has no independent meaning outside its parent.
R7 to R9: Movie vs. Show, and the Query That Isn't a Field
R7: Users book seats for a particular SHOW.
R8: A show = one movie + a start time + an end time + one screen.
R9: BMS lists down all the movies running in a city, and for
    each movie there can be multiple shows running.

The single most important distinction introduced in these three requirements: a Show is not the same thing as a Movie.
The movie is the content, for example, "Pathaan."
A show is one specific screening of that content: 6 PM today, Screen 3, PVR Forum Mall.
The same movie can have dozens of shows, across dozens of theatres and screens, all on the same day.
Almost every genuinely tricky decision in today's class diagram comes back to one repeated question: is this a property of the MOVIE, or of the SHOW?
R9 needs unpacking, because it is really describing two separate operations happening underneath one simple sentence:
Discovery: when a user picks a city, the system finds every Show, across every Screen, in every Theatre, that belongs to that one City.
Grouping: those shows then get grouped by Movie, so the user sees a clean list of movies rather than a messy list of individual screening times.
A genuinely useful question follows from this: which class does the actual work of answering "what movies are running in Bengaluru today"? Is it a field on some class, or something else entirely?
It is not a field anywhere. No class needs a new attribute to answer this question.
It is a query that joins across the hierarchy already built (City, Theatre, Screen, Show).
This becomes a Service method once coding starts, not a change to today's class diagram.
This is the first time in this course a requirement has taken this particular shape clearly: not every requirement adds a new field to a class. Some requirements describe how existing classes get queried together later, and belong entirely to the Service layer, not the model layer.
R10 and R11: The First Genuinely New Idea
R10: In one booking, users can select a MAXIMUM of 10 seats.
     Selected seats are held during the payment step, so a
     frustrated user can't just select seats and vanish.
R11: No two users should be able to book the same seat for the
     same show.

R10 raises a question worth answering directly: why would a platform bother temporarily holding selected seats during payment? What happens if it didn't?
Someone could select 10 seats "just to look," never actually pay, and simply walk away.
Without a temporary hold, those seats would stay blocked for every other user, indefinitely.
Holding them only for the duration of the payment step prevents that from happening.
R11 is a shape of problem already seen once in this course, just wearing different clothes: two gates racing for the same parking spot, from Parking Lot's Design session. Here, it is two users racing for the same seat instead.
This version is genuinely harder than Parking Lot's, because there is a time-based hold layered on top of the plain "don't double-assign" problem. A seat isn't just claimed or unclaimed, it can also be temporarily held during someone else's payment window.
As with Parking Lot, this problem is only named today, not solved. It gets solved for real, with actual threads, once the Code lectures for BookMyShow begin.
R12: Price as a Function of Show and SeatType
R12: Price will be a function of SHOW + SEATTYPE.
     (e.g. seat-type could be Gold, Silver, or Platinum)

Hold onto the exact phrase "function of show AND seatType." It is not "function of seat." This distinction gets tested hard once the class diagram reaches pricing.
R13 and R14: Payment, Already Solved Once
R13: Only ONLINE payment is supported, via a 3rd-party
     payment gateway.
R14: Partial payments are also supported.

This exact pair of requirements has already been built once before, in Parking Lot: a PaymentGateway interface backed by a fake implementation, plus Bill.payments modeled as a list specifically to support partial payment.
The same reasoning applies here almost unchanged, and does not need to be re-derived from scratch. Ticket.payments in BookMyShow plays the exact same role Bill.payments played in Parking Lot.
A real payment gateway, end to end, typically works as: redirect the user to the gateway, the third party processes the card, and a webhook or callback confirms success back to the platform. This detail is worth knowing conceptually even though the MVP implementation stays a simulated, fake gateway.
R15 and R16: Data That Belongs to the Movie
R15: For every movie, we also store its cast, genre, and
     languages.
R16: Each movie supports multiple FEATURES — 2D / 3D / IMAX,
     Dolby Atmos (sound quality), and a trailer description.

Both of these describe data that belongs to the movie itself, not to any one screening of it. They get a real home once the Movie class is built in Section 3.
R17: Seat Types
R17: Seats can be of different types (e.g. GOLD, SILVER,
     PLATINUM).

Exactly how to model this, a plain enum, or something more flexible, gets decided in Section 3, once one key question is asked: is this set of values the same for every theatre, or does it vary?
R18: A Deliberate Simplification, Named Out Loud
R18 states plainly that the real seat, show, and pricing data is actually owned by the theatre, not by BookMyShow. BMS just calls the theatre's APIs, and the theatre is the true source of truth, normally responsible for handling its own concurrency.
A fair question follows directly from that: if the theatre owns the data and its own concurrency, why does this course still spend class time solving "two users, one seat" itself?
The honest answer: for this course, BookMyShow is treated as if it owns the data directly. That is what makes it possible to actually practice solving the concurrency problem hands-on, even though that is not exactly how the real company is architected.
This is the same honesty applied to every MVP scoping decision throughout this module: reality gets simplified on purpose, and that simplification is said out loud rather than hidden.
Quiz Recap

Same physical seat, A1, on Screen 3. It's booked for the 6 PM show today. A different user tries to book seat A1 for the 9 PM show, same screen, same day. Based on R11 alone, should this be allowed?

A) No, seat A1 is already booked, so it can never be booked again by anyone
B) Yes, R11 only blocks the SAME seat for the SAME show; a different show is a completely different booking target
C) It depends on whether the 6 PM show has ended by 9 PM
D) No, one seat can only ever belong to one show for its entire lifetime
Correct answer: B. R11 is scoped precisely to "same seat, same show," not "same seat, forever." The 6 PM show and the 9 PM show are two entirely separate Show instances that happen to run on the same physical screen, so seat A1 is legitimately re-bookable for the later show.
Why A is wrong: it ignores that "booked" only has meaning relative to a specific show, not as a permanent, lifetime label on the physical seat.
Why C is wrong: whether the 6 PM show has technically ended by 9 PM is irrelevant to R11's scope; the uniqueness rule is defined per show, not per overlapping time window.
Why D is wrong: this treats the seat as if it were permanently consumed by a single booking, which contradicts the entire premise that one screen runs many different shows over a day.
This quiz sets up the exact modeling decision made later in Section 3: this uniqueness rule does not attach to Seat itself. It attaches to the mapping between a seat and a specific show.
Hidden Pitfalls
Confusing Movie with Show: almost every mistake possible in today's class diagram traces back to attaching a piece of data (features, price, status) to the wrong one of these two concepts; always ask which of the two a given fact actually describes.
Treating R9 as if it needs a new field somewhere: R9 describes a cross-hierarchy query, not new class data; adding a field to satisfy it would be solving a Service-layer problem inside the model layer.
Assuming R18's "theatre owns the data" detail means the concurrency problem can be skipped entirely: the course deliberately pretends BookMyShow owns the data so the concurrency problem can actually be practiced; skipping it because "the real theatre would handle this" misses the entire point of the exercise.
Re-deriving R13/R14 from scratch instead of reusing the Parking Lot reasoning: PaymentGateway and a payments list already exist as proven patterns from Post-Read 5; treating this as a brand-new problem wastes time re-solving something already settled.
Section 3: Class Diagram
What It Means

Boxes stay light on detail today, the same rule followed for every prior class diagram in this course: getters are not written out live, only the fields and relationships that actually matter to the design decisions being made.

The Physical Hierarchy: City, Theatre, Screen, Feature
These four classes are mostly direct copies of the Parking Lot shape, so this part moves fast.
City                     Theatre                  Screen
 - id                     - id                     - id
 - name                   - name                   - name
                          - address                - screenNumber
                          - city: City             - theatre: Theatre
                                                    - features: List<Feature>

Feature (enum)
 - TWO_D
 - THREE_D
 - IMAX
 - DOLBY_ATMOS

City-Theatre-Screen-Seat is composition all the way down, using the exact same test applied to ParkingFloor inside ParkingLot: a Screen without a Theatre doesn't mean anything on its own, so the relationship is composition, not aggregation.
Seat: The First Real Design Decision

The obvious first attempt at Seat looks like this:

Seat  (first attempt — has a problem)
 - id
 - screen: Screen
 - seatNumber: String
 - seatType: SeatType
 - status: SeatStatus       <-- the problem

status here would mean something like BOOKED or EMPTY. But a seat gets booked for a show, and the same physical seat serves many different shows over the course of a single day.
Walking through what breaks the moment a second show starts: seat A1's status gets set to BOOKED for the 6 PM show. At 9 PM, that same single field still says BOOKED, even though nobody has booked it for the 9 PM show yet. One status field simply cannot say "booked for show X, but free for show Y" at the same time.
This is a genuine correction, found by actually reasoning through the consequences, in the same spirit as Parking Lot's ParkingSpot.vehicleType becoming supportedVehicleTypes.
status does not belong to Seat at all. It belongs to the pairing of a specific seat with a specific show:
Seat  (corrected)
 - id
 - screen: Screen
 - seatNumber: String
 - seatType: SeatType

ShowSeat
 - id
 - show: Show
 - seat: Seat
 - status: SeatStatus     (EMPTY / HELD / BOOKED)

Quiz Recap

Same seat A1, Screen 3. It's booked for the 6 PM show today. A different user tries to book seat A1 for the 9 PM show, same day. Given status now lives on ShowSeat, not Seat, how many ShowSeat rows exist for seat A1 by the end of the day, and what do their statuses look like?

A) One ShowSeat row, shared between both shows, with status = BOOKED
B) Two separate ShowSeat rows, one for (6 PM show, A1) marked BOOKED, one for (9 PM show, A1), independently bookable
C) Zero ShowSeat rows, Seat.seatType already tells us the price, so no mapping is needed
D) One ShowSeat row per seatType, not per seat
Correct answer: B. This is exactly why status was moved off Seat in the first place. Every (show, seat) combination gets its own independent ShowSeat row, so the same physical seat can be BOOKED for one show and EMPTY for another, at the exact same time, with zero conflict between them.
Why A is wrong: sharing one row between both shows recreates the original bug, a single status field cannot represent two different, simultaneous states.
Why C is wrong: it confuses SeatType (which affects pricing) with ShowSeat (which tracks booking status); the two solve completely different problems.
Why D is wrong: ShowSeat is keyed on the pairing of a specific show and a specific physical seat, not on seat type; grouping by type instead of by individual seat would make it impossible to track which exact seat is taken.
SeatType: Enum, or Something More Flexible?
R17 gave GOLD, SILVER, and PLATINUM as examples. The usual reflex for a small, fixed set of values is a plain Java enum.
That reflex needs pushing on here, for a reason specific to this system: BookMyShow is not one theatre. It works with every theatre chain across the whole country, and some chains might call their tiers "Recliner" or "Executive" instead of Gold, Silver, or Platinum.
If different theatres can each define their own seat-type names, a single shared Java enum cannot work. An enum has one fixed set of values for the entire system; if Theatre A wants "Recliner" and Theatre B wants "Gold," one shared enum cannot hold both at once.
This is a step beyond the usual "will this list grow" test already used for enum-versus-lookup-table decisions. The real question here is a new one: is this set even the same for every owner, or does each owner define its own? Once the answer is "each owner defines its own," the set is no longer a platform-wide enum; it becomes plain, configurable data, with each theatre supplying its own list of type names as regular strings.
SeatType
 - id
 - name: String        (e.g. "GOLD", "RECLINER", "EXECUTIVE")
 - theatre: Theatre     (each theatre owns its own set)

Movie: A Home for R15 and R16
R15 and R16 both described data belonging to the movie itself, not to any one screening of it. That data finally gets a real home:
Movie
 - id
 - title: String
 - cast: List<String>
 - genre: String
 - languages: List<String>
 - features: List<Feature>
 - trailerDescription: String

Movie has its own features list, and Show is about to get one too. It is worth asking directly: is this the same mistake that was just corrected between Seat and ShowSeat?
It is not the same mistake, and it is legitimate for both to exist:
Movie.features describes what the movie was actually shot in or supports, for example, "shot in 3D."
Show.features describes what is actually switched on for one specific screening. A screen without 3D hardware would still show that same movie, just in plain 2D.
These two can genuinely disagree with each other, which is exactly why they need to be two separate fields rather than one shared one.
This is the first appearance of a pattern that repeats once more, immediately below, with Screen.features versus Show.features: a capability (what something can generally do) versus a snapshot (what is actually true for one specific instance).
Show: The Capability-vs-Snapshot Pattern, Repeating
Show
 - id
 - movie: Movie
 - screen: Screen
 - startTime: DateTime
 - endTime: DateTime
 - features: List<Feature>

Screen already carries its own features list. It is worth asking directly whether Show needs a separate one too, or whether that would just be the same information repeated.
It is not repeated:
Screen.features is what the screen is physically capable of, it HAS Dolby hardware, it CAN project 3D.
Show.features is what is actually turned on for this one specific screening.
The same physical screen might run one show in plain 2D and another in 3D, even though the hardware supports both at once.
This is the exact same shape as Gate.operator (who is currently assigned) versus Ticket.operator (who was actually there at that specific moment), from Parking Lot. One field is the current, general capability of a resource; the other is a frozen snapshot for one specific instance. This pattern, capability versus snapshot, shows up twice in today's design: once between Movie and Show, and once between Screen and Show.
ShowSeatType: The Price Question
Recall R12: price is a function of show AND seatType, not of one individual seat. Writing the mapping the obvious way first, by adding a price field directly onto ShowSeat:
ShowSeat  (if price were added directly — don't do this)
 - id
 - show: Show
 - seat: Seat
 - status: SeatStatus
 - price: int        <-- the problem

Working through the consequence directly: a screen has, say, 100 GOLD seats. If price lives directly on each ShowSeat row, how many rows need updating the day the theatre raises the GOLD price for one show?
All 100 rows, one per gold seat, for that one show. The same value gets repeated 100 times, and all 100 have to change together, every single time the price changes.
That is wasted storage, and a real bug risk. If even one of those 100 rows fails to get updated, the same show now has GOLD seats sitting at two different prices, for no legitimate reason at all.
Price is not really a property of one seat, it is a property of "this seatType, for this show." That deserves its own dedicated row:
ShowSeat  (corrected — no price here)
 - id
 - show: Show
 - seat: Seat
 - status: SeatStatus

ShowSeatType
 - id
 - show: Show
 - seatType: SeatType
 - price: int

Quiz Recap

Screen 3 runs two shows today: a 12 PM matinee and a 9 PM night show. The theatre wants matinee GOLD seats priced at ₹200, and night GOLD seats priced at ₹350, same screen, same seat type, different price. Given ShowSeatType is keyed on (show, seatType), does our current design already support this, with no changes needed?

A) No, since both shows run on the same Screen, and the screen is where seat types physically exist, GOLD has to be one shared price across every show on that screen
B) Yes, ShowSeatType is scoped to (show, seatType), not (screen, seatType), so the matinee Show and the night Show each get their own independent ShowSeatType row for GOLD
C) No, we'd need to add a SeatType value for each time slot, like GOLD_MATINEE and GOLD_NIGHT
D) Only if Seat stores the price directly, since the seat itself doesn't change between shows
Correct answer: B. This is exactly why ShowSeatType was tied to Show, not to Screen, in the first place. Two different Show instances on the same physical screen are still two entirely separate rows in ShowSeatType, so they can carry two completely different GOLD prices with zero additional modeling required.
Why A is wrong: it assumes price lives at the screen level, when it actually lives at the (show, seatType) level; screens do not own pricing at all in this design.
Why C is wrong: this repeats the same style of mistake already corrected once earlier with Seat.status, multiplying enum-like values instead of trusting the mapping class already built to solve exactly this problem.
Why D is wrong: it confuses Seat, the physical chair, with ShowSeatType, the class where price actually belongs; the seat itself never stores a price at all.
User, Ticket, and Payment
User
 - id
 - name
 - email
 - phoneNumber

Ticket
 - id
 - user: User
 - show: Show
 - showSeats: List<ShowSeat>
 - payments: List<Payment>
 - bookingTime: DateTime

Payment
 - id
 - amount: int
 - mode: PaymentMode
 - status: PaymentStatus
 - referenceNumber: String
 - time: DateTime

Ticket stores List<ShowSeat>, not List<Seat>. The reasoning follows directly from everything just built: a "seat" is never booked in isolation, it is always booked for a specific show, and ShowSeat already carries both pieces of information together. Storing ShowSeat directly on the ticket is simply the natural fit.
Ticket.payments is a list, for exactly the same reason Bill.payments was a list in Parking Lot: R14, partial payments.
Complete Class Diagram Summary

Thirteen classes make up today's full design: City, Theatre, Screen, Feature (enum), Movie, Seat, SeatType, Show, ShowSeat, ShowSeatType, User, Ticket, and Payment. Reading the whole diagram in one pass:

Physical spine:
  City -> Theatre -> Screen -> Seat        (pure composition)

Content vs. instance:
  Movie is the content
  Show is one screening of it, tied to exactly one Screen

The two corrected mappings (the heart of today):
  ShowSeat      : Show x Seat     -> status
  ShowSeatType  : Show x SeatType -> price
  (neither Seat nor ShowSeat carries booking status or price
   directly; both live on purpose-built mapping classes)

Booking flow:
  User -> Ticket -> (Show + a list of ShowSeats)
                  -> paid off by one or more Payments

Hidden Pitfalls
Storing status directly on Seat: this collapses every show that seat will ever serve into a single field, making it impossible to represent "booked for one show, free for another" at the same moment.
Assuming a small fixed-value set is automatically an enum: SeatType shows this reflex breaking down the moment a system spans multiple independent owners (theatres) who each define their own values.
Duplicating price across every ShowSeat row of the same type: this wastes storage and creates a real bug risk, since a single missed update leaves seats of the same type at inconsistent prices for the same show.
Confusing Movie.features, Screen.features, and Show.features as redundant: each answers a genuinely different question (what the content supports, what the hardware supports, what is actually switched on right now), and collapsing them loses real information the system needs.
Section 4: AI Corner
Touchpoint 1: Refine and Visualize

The design was fully built by hand before this touchpoint, and gets checked against AI once, the same way Parking Lot's design was checked.

Prompt used:

"Here is a class design I built by hand for a movie ticketing
system: [City, Theatre, Screen, Feature enum, Movie, Seat,
SeatType, Show, ShowSeat, ShowSeatType, User, Ticket, Payment —
with the key decisions: status lives on ShowSeat not Seat, price
lives on ShowSeatType not ShowSeat, seatType may be per-theatre
rather than a single global enum]. Only point out something
genuinely missing — don't restructure what's already there."

A plausible AI response:

This design correctly separates show-specific state from the
seat and movie itself — good instinct on ShowSeat and
ShowSeatType. One gap: nothing here stops two users from both
selecting the SAME empty ShowSeat at nearly the same moment,
before either one finishes paying. Your model tracks status, but
nothing described actually locks a seat the instant it's picked.

Checking this gap against everything discussed earlier in the session: is it real?
Yes, it is real, but it is not new information. It is exactly R10 and R11, the seat-locking problem already named and deliberately left open earlier in this same document.
Nothing new surfaces here, only confirmation. The same discipline applies as with Parking Lot: timing problems are not fixed on paper. That work belongs to the Code lectures, with real threads.
Touchpoint 2: Diagnose, Don't Generate

This time, the direction reverses. A flawed class is shown, AI diagnoses only, and the fix happens by hand, using ideas already established earlier in this document.

ShowSeat  (flawed — price and isGoldSeat sitting on the wrong class again)
 - id
 - show: Show
 - seat: Seat
 - status: SeatStatus
 - price: int
 - isGoldSeat: boolean

Prompt used: "Diagnose only, don't rewrite yet. What's wrong with this class?"

A plausible AI response:

Two issues:
1. `price` is stored per (show, seat) — this duplicates the same
   value across every seat of the same type for a given show, and
   makes bulk price changes error-prone.
2. `isGoldSeat` is a boolean flag standing in for what should be
   a proper SeatType — it can't represent SILVER or PLATINUM at
   all, and breaks the moment a new tier is added.

Matching each issue back to a concept already named earlier in this document:
Issue 1 is exactly the ShowSeatType normalization problem already solved in Section 3.
Issue 2 is the familiar "a boolean isn't extensible, use an enum or a type" reflex, a boolean can only ever mean two things, and seat tiers are clearly not limited to two things.
Fixing this by hand, using what was already built:
ShowSeat  (fixed)
 - id
 - show: Show
 - seat: Seat
 - status: SeatStatus

ShowSeatType
 - id
 - show: Show
 - seatType: SeatType
 - price: int

The same rule applies at every AI Corner in this course: generate fast, but the judgement calls stay human, especially when checking against the real constraints of the actual system being built, not a generic version of the same problem.
Hidden Pitfalls
Treating an AI-confirmed gap as new information: Touchpoint 1's confirmation of the seat-locking gap is not a new discovery, it is validation of a problem already named in Section 2; mistaking confirmation for discovery risks re-deriving work already done.
Accepting a diagnosis without tracing it back to an existing pattern: both issues AI found in Touchpoint 2 map directly onto corrections already made earlier in the class diagram; skipping that trace-back step means the fix risks reinventing a slightly different, possibly inconsistent solution.
Section 5: A Primer for JPA and Spring Boot

This is a genuine part of today's live session, taught specifically because next session jumps straight into writing real Spring Boot code with no time set aside to explain the tooling itself. By the end of this section, "Spring Boot" and "JPA" should feel like known tools rather than mysteries.

5.1 What Actually Changes, Compared to Parking Lot
In Parking Lot, data lived nowhere permanent. It sat in a plain Java List, inside the hand-built InMemoryRepository<T> class. The moment the program stopped running, everything was gone.
Today's Overview locked in something genuinely different for BookMyShow: real MySQL, real persistence.
Working through what saving a Show object into a real MySQL table by hand would actually require: writing the literal SQL (INSERT INTO shows (...) VALUES (...)), manually converting every Java field into a column value, and doing the reverse conversion when reading it back.
That is tedious and repetitive for every single class designed today. This exact gap is what JPA exists to close.
Parking Lot:  Java object  →  our own List (in memory)
BookMyShow:   Java object  →  ??? (we need something that writes
                                    the SQL Queries for us, and keeps our
                                    objects and real tables in sync)

5.2 What Is JPA
The problem just identified is not new: keeping normal Java objects (a Show, a Seat) while having something else translate them into real database rows, without hand-writing SQL, already has a name in this course.
That name is ORM, Object-Relational Mapping: the general idea of mapping Java objects to database tables automatically.
ORM       → the general IDEA: map Java objects to DB rows,
            automatically, without hand-written SQL.

JPA       → Java Persistence API — the official Java
            SPECIFICATION for how ORM should work in Java.
            It defines the annotations (@Entity, @Id, @ManyToOne)
            and the rules, but it's just a specification —
            it doesn't do the actual work by itself.

Hibernate → the most popular real IMPLEMENTATION of JPA.
            This is the actual code that reads your @Entity
            classes and generates the real SQL behind the scenes.

Thinking of this as an interface and a class: if JPA is like an interface, a contract saying "any ORM tool must support these annotations and behaviors," then Hibernate is the concrete class that actually implements that contract, one real, working implementation of it. Other implementations could exist too.
This is the same shape as every interface/implementation pair already used throughout this course. When a Spring Boot project says "Spring Data JPA," it means: the JPA specification, backed by Hibernate as the actual engine underneath.
The concrete payoff: next session, every class designed today, Show, Seat, Ticket, gets one annotation, @Entity, and JPA, via Hibernate, creates the actual MySQL table for it. No SQL gets written by hand at all.
5.3 Why Spring Boot, Specifically, to Use JPA
JPA itself is a plain Java specification, not something tied to Spring at all. It is worth asking directly why Spring Boot enters the picture instead of just using JPA in plain Java, the same way everything was written for Parking Lot.
Using JPA on its own still needs a fair amount of manual setup: configuring the database connection, wiring Hibernate up correctly by hand. Spring Boot automates that setup, the same way it automates everything else it touches.
Spring       → the original, powerful Java framework. Can do
               almost anything, but needs a lot of manual
               configuration to get started.
Spring Boot  → built on top of Spring, specifically to remove
               that manual setup — sensible defaults, starter
               dependencies, and (for us) a ready-made "Spring
               Data JPA" starter that wires up JPA + Hibernate
               with almost no configuration.

To be precise about today's real shift: the point is not "switching to Spring Boot" for its own sake. It is switching to it because it is the easiest way to get JPA working with almost no setup, and JPA is what actually solves the persistence problem.
5.4 Maven: How the Project Gets JPA and Hibernate At All
JPA and Hibernate are libraries, code someone else wrote. Something has to actually download them into the project.
Maven  → a build tool. Reads a file called pom.xml, downloads
         every library our project needs (including JPA/
         Hibernate/MySQL support), and compiles our project.

(Gradle is the other common option — same job, different config
 style. We're using Maven today, since it's the Spring
 Initializr default.)

5.5 Creating the Project with Spring Initializr
Spring Initializr is a website that generates a ready-to-run Spring Boot project, based on choices made on a form.
Step 1 — Project basics:
  Project:      Maven
  Language:     Java
  Spring Boot version: latest stable (non-SNAPSHOT)

Step 2 — Project metadata:
  Group:        com.scaler
  Artifact:     bookmyshow
  Package name: com.scaler.bookmyshow
  Packaging:    Jar
  Java version: 17 (or your class standard)

The dependencies panel is where today's JPA discussion becomes a real, concrete choice:
Spring Boot DevTools           → auto-restarts the app on save;
                                  not included in the final build
Lombok                         → auto-generates getters/setters
Spring Configuration Processor → helps avoid hardcoded values
Spring Data JPA                → THE ONE FROM TODAY — brings in
                                  JPA + Hibernate, pre-wired by
                                  Spring Boot
MySQL Driver                   → the specific code that lets
                                  Hibernate talk to MySQL
                                  (JPA is database-agnostic;
                                  this driver is what makes it
                                  MySQL specifically)

Given everything covered so far, one clear question can be answered directly: of these five dependencies, which one is actually doing the "map Java objects to database tables" work discussed above?
Spring Data JPA is the one bringing in JPA and Hibernate. MySQL Driver is only what lets it connect specifically to MySQL, rather than some other database.
Clicking Generate, unzipping, and opening it in an IDE produces a fully working, empty Spring Boot project, already wired for JPA, ready to run.
5.6 Dependencies and a First Hint of Annotations
Adding the Spring Data JPA dependency, in plain terms, means telling Maven "go download this library, because our project needs it," the same idea as importing a class, just scaled up to an entire external library.
Next session, this dependency shows up as @-prefixed labels sitting on model classes: @Entity, @Id, @ManyToOne.
Since an annotation is just a label sitting on a class, not code that runs by itself, it is worth asking what actually reads that label and does something with it.
Hibernate scans for these labels and reacts to them. The annotation itself is only a marker; Hibernate is what turns it into real behavior.
@Entity   on a class   → Hibernate (via JPA) treats this class
                          as a real database table
@Id       on a field    → Hibernate treats this field as that
                          table's primary key
@Getter   on a class    → (this one's Lombok, not JPA) generates
                          every getter method for you

Next session, every time a new @Something shows up, one question resolves almost all of the new syntax: is this a JPA annotation Hibernate is reading, or a Lombok annotation generating boilerplate?
Hidden Pitfalls
Treating JPA and Hibernate as the same thing: JPA is only a specification, it defines the rules and the annotations; Hibernate is the actual implementation that does the real work. Conflating the two makes it harder to understand why other implementations of JPA could exist at all.
Assuming Spring Boot invented ORM or JPA: Spring Boot did not create either idea; it only automates the setup work needed to wire JPA (via Hibernate) into a project with minimal manual configuration.
Assuming an annotation runs code by itself: an annotation like @Entity is only a label; nothing happens until Hibernate scans for it and reacts. Believing the annotation itself performs the work leads to confusion when debugging why something isn't behaving as expected.
Not distinguishing JPA annotations from Lombok annotations: @Entity and @Id are read by Hibernate for persistence; @Getter is read by Lombok purely to generate boilerplate code. Mixing up which tool is responsible for which annotation makes debugging unnecessarily confusing next session.
Common Pitfalls Summary
1. Assuming "we'll use a real database this time" changes the
   class diagram itself.
   -> Persistence choice affects how classes are stored, not
      what fields and relationships they need; that belongs to
      the Schema step, not Class Diagram.

2. Confusing Movie with Show when placing a field.
   -> Nearly every mistake in this session's design traces back
      to attaching data to the wrong one of these two concepts.

3. Treating R9 (list movies running in a city) as needing a new
   field on some class.
   -> R9 describes a cross-hierarchy query, which becomes a
      Service method later, not a model change.

4. Storing `status` directly on `Seat` instead of on a
   show-seat mapping.
   -> Collapses every show that seat will ever serve into one
      field, making "booked for show X, free for show Y" at the
      same time impossible to represent.

5. Assuming a small, fixed-value set is automatically a shared
   enum.
   -> SeatType breaks this reflex the moment different owners
      (theatres) can each define their own distinct set of values.

6. Duplicating price across every ShowSeat row of the same
   seat type.
   -> Wastes storage and creates a real bug risk if even one row
      is missed during a bulk price update.

7. Treating Movie.features, Screen.features, and Show.features
   as redundant.
   -> Each answers a genuinely different question (content
      support, hardware capability, what's switched on right
      now); collapsing them loses real information.

8. Skipping the seat-locking problem (R10/R11) because "the real
   theatre would handle its own concurrency" (R18).
   -> The course deliberately treats BookMyShow as owning the
      data, specifically so the concurrency problem can be
      practiced hands-on; this is a scoping choice, not a reason
      to skip it.

9. Conflating JPA and Hibernate as the same thing.
   -> JPA is a specification; Hibernate is one real
      implementation of it. Confusing the two obscures why other
      implementations could exist.

10. Assuming Spring Boot itself performs the object-to-table
    mapping.
    -> Spring Boot only automates the setup; JPA (via Hibernate)
       is what actually does the mapping work.

11. Believing an annotation like @Entity executes code on its
    own.
    -> An annotation is only a label; Hibernate is what scans
       for it and turns it into real behavior.

Higher-Level Hidden Pitfalls (cross-cutting, not listed above):

Treating "we discussed a gap in the AI Corner" as new information rather than confirmation: both AI Corner touchpoints in this session confirmed problems already named earlier in the lecture (the seat-race condition, the price-and-boolean mistakes); mistaking confirmation for discovery risks re-deriving work already settled.
Assuming today's tooling primer (Section 5) is separate from the actual design work: JPA and Spring Boot were introduced specifically because next session's Show, Seat, and Ticket classes are about to become real @Entity classes; the primer and the class diagram are two halves of the same upcoming step, not unrelated topics.
Key Terminology
Term	Meaning in Simple Words
Show	One specific screening of a movie: a particular movie, on a particular screen, with a start and end time. Distinct from the movie itself, which can have many shows.
ShowSeat	A mapping class pairing one specific Show with one specific Seat, holding that pairing's own booking status (EMPTY, HELD, or BOOKED), so the same physical seat can have a different status for every different show.
ShowSeatType	A mapping class pairing one specific Show with one SeatType, holding the price for that combination, so the same seat type can be priced differently across different shows on the same screen.
Capability vs. Snapshot Pattern	A recurring modeling shape where one field represents what something can generally do (a capability, like Screen.features) and a separate field represents what is actually true for one specific instance (a snapshot, like Show.features).
ORM (Object-Relational Mapping)	The general idea of automatically mapping Java objects to database table rows, without hand-writing SQL for every save or read.
JPA (Java Persistence API)	The official Java specification defining how ORM should work: it defines annotations like @Entity and @Id and the rules around them, but does not itself perform any work.
Hibernate	The most popular real implementation of the JPA specification; the actual code that reads @Entity-annotated classes and generates the real SQL behind the scenes.
Spring	The original, powerful Java framework capable of nearly anything, but requiring substantial manual configuration to get started.
Spring Boot	A framework built on top of Spring specifically to remove manual configuration, via sensible defaults and starter dependencies, including a ready-made Spring Data JPA starter.
Maven	A build tool that reads a project's pom.xml file, downloads every library the project depends on, and compiles the project.
Spring Initializr	A website (start.spring.io) that generates a ready-to-run Spring Boot project based on selections made on a form (build tool, language, dependencies, metadata).
@Entity	A JPA annotation placed on a class, telling Hibernate to treat that class as a real database table.

Repository/Service/Controller layering, DTOs, generics, synchronized, critical sections, race conditions, and the enum-versus-lookup-table test were already defined in earlier post-reads in this series and are not redefined here.

Frequently Asked Interview Questions

1. Why can't Seat.status alone represent whether a physical seat is bookable?
A single status field on Seat would need to simultaneously represent that seat's booking state across every show it will ever be part of, but a physical seat serves many different, independent shows over the course of a day. Setting status to BOOKED for the 6 PM show would leave that same field incorrectly showing BOOKED at 9 PM, even though nobody booked it for the later show. The fix is to move status onto ShowSeat, a mapping class keyed on the specific (show, seat) pairing, so each show gets its own independent status for that seat.

2. Explain why SeatType in BookMyShow is not modeled as a plain Java enum, even though R17 gives a small, fixed-looking list (GOLD, SILVER, PLATINUM).
The usual test for choosing an enum is whether a value set is small and unlikely to change. BookMyShow adds a second dimension to that test: whether the set of values is even the same across every owner in the system. Since BookMyShow works with many different theatre chains, and each chain can define its own tier names (for example, "Recliner" or "Executive" instead of Gold/Silver/Platinum), a single shared enum cannot hold every theatre's distinct set of values at once. SeatType is instead modeled as configurable data, with each theatre supplying its own list of type names as plain strings tied to that theatre.

3. Why does price live on ShowSeatType instead of directly on ShowSeat?
Price, per R12, is a function of the show and the seat type, not of any one individual seat. Storing price directly on ShowSeat would duplicate the same price value across every seat of a given type for a given show; for a screen with 100 GOLD seats, that means 100 identical rows to update every time the GOLD price changes for that show, with real risk of some rows being missed and ending up inconsistent. Giving price its own row, keyed on (show, seatType), means a single update changes the price for every seat of that type in that show at once, with no duplication.

4. How does ShowSeatType correctly support the same seat type having two different prices on the same physical screen, for two different shows?
ShowSeatType is keyed on (show, seatType), not (screen, seatType). Since a matinee show and a night show on the same screen are two entirely separate Show instances, each gets its own independent ShowSeatType row for GOLD, one might be priced at ₹200 and the other at ₹350, with no additional modeling needed. This works precisely because the mapping is tied to the show, which already captures the specific screening, rather than to the screen, which is shared across many different shows.

5. Distinguish Movie.features, Screen.features, and Show.features. Why do all three need to exist as separate fields?
Movie.features describes what the movie itself was shot in or supports, for example, being filmed in 3D. Screen.features describes what a physical screen is capable of, for example, having Dolby Atmos hardware installed. Show.features describes what is actually switched on for one specific screening. These three can genuinely disagree: a movie shot in 3D can still be shown in plain 2D on a screen that supports 3D, if that particular show simply doesn't enable it. Collapsing any two of these into one field would lose real, independently meaningful information.

6. Why is Ticket.showSeats typed as List<ShowSeat> rather than List<Seat>?
A user never books a bare "seat" in isolation, they book that seat specifically for one show. ShowSeat already carries both pieces of information together, which show and which physical seat, in a single object. Storing List<ShowSeat> on Ticket is the natural fit, since it directly represents exactly what was booked, without needing a separate field to also track which show the seats belong to.

7. Why does R11 ("no two users should book the same seat for the same show") attach to ShowSeat rather than to Seat?
Booking uniqueness is meaningful only relative to a specific show; the same physical seat is legitimately re-bookable across different shows on the same day. Since ShowSeat is the class that represents the pairing of one specific seat with one specific show, that is exactly where a uniqueness constraint on booking needs to live, ensuring at most one active booking exists per (show, seat) combination, without incorrectly blocking that same seat from being booked again for a different show.

8. What is the practical difference between JPA and Hibernate, and why does that distinction matter?
JPA is a specification: it defines the rules and annotations (such as @Entity, @Id, @ManyToOne) that any compliant ORM tool must support, but it does not perform any actual work itself. Hibernate is the most popular concrete implementation of that specification, the real code that scans @Entity-annotated classes and generates the actual SQL behind the scenes. The distinction matters because it clarifies that other implementations of JPA could exist, and that annotations alone do nothing without an implementation like Hibernate actually reading and acting on them.

9. Why is Spring Boot used to bring in JPA, rather than using JPA directly in plain Java?
JPA itself is a plain Java specification with no dependency on Spring. However, using it directly still requires a fair amount of manual setup: configuring the database connection and wiring Hibernate correctly by hand. Spring Boot automates that setup through sensible defaults and a ready-made "Spring Data JPA" starter dependency, which wires up JPA and Hibernate together with almost no manual configuration. The choice to use Spring Boot is therefore driven by ease of getting JPA working, not by any inherent need for Spring itself.

10. In the "two users, one seat" problem, why is this considered a harder version of Parking Lot's "two gates, one spot" problem?
Both problems share the same basic shape: two concurrent actors racing to claim the same shared resource before either commits. BookMyShow's version adds an additional wrinkle, a time-based hold, where a seat gets temporarily reserved during another user's payment window (R10), rather than being either simply free or simply booked. Solving it correctly requires handling not just mutual exclusion (only one user ends up with the seat) but also a temporary, expiring lock tied to the payment process, which Parking Lot's simpler occupied/empty model did not need to handle.

11. Why does this session explicitly move the Schema step to the start of the next class instead of covering it today?
This is a genuine milestone: BookMyShow is the first system in this course designed with real MySQL persistence in mind from the start, rather than an in-memory list. Building a real schema deserves proper, unrushed time, and squeezing it into the last few minutes of an already dense 120-minute session covering 18 requirements and a full class diagram would shortchange it. Moving Schema to the start of the next session, the same restructuring already used once before with Parking Lot, ensures it gets the attention it needs.

12. What is the significance of R9 being described as "a query, not a field"?
R9 asks for a list of movies running in a given city, grouped from underlying shows. Answering it correctly requires joining across the existing hierarchy (finding every Show, across every Screen, in every Theatre, belonging to one City, then grouping those shows by Movie), rather than adding any new attribute to any existing class. This distinction matters because it clarifies that not every requirement changes the class diagram; some requirements only describe how already-existing classes will later be queried together in the Service layer.

Self-Check Questions
In your own words, explain why status cannot correctly live on Seat, and describe the exact scenario that exposes the bug if it does.
Trace through: a theatre wants to change the GOLD price for only its 9 PM show, leaving its 12 PM show's GOLD price unchanged. Walk through exactly what needs to be updated in the current design, and confirm nothing else is accidentally affected.
Write a snippet (as a class-box style description, not full Java) of a SeatType class that supports each theatre defining its own set of tier names, and explain what would break if SeatType were instead a single shared enum.
Compare Movie.features and Show.features. Describe a real scenario where the two would legitimately hold different values for the same movie.
Explain, in your own words, why R9 ("list all movies running in a city") does not require any new field on any class in today's design.
Trace through: describe, step by step, what would go wrong if ShowSeatType were keyed on (screen, seatType) instead of (show, seatType).
Compare R11 in BookMyShow ("no two users can book the same seat for the same show") to Parking Lot's "two gates, one spot" problem. Identify the one additional complication BookMyShow's version has that Parking Lot's did not.
Explain, in your own words, the difference between JPA and Hibernate, using the interface/implementation analogy from this session.
Write a short explanation, in plain English, of what actually happens, step by step, when a Show object gets saved once next session's @Entity annotation is in place, compared to how saving worked in Parking Lot's InMemoryRepository.
Trace through: if BookMyShow needed to add support for a brand-new content type, say, "Live Events," alongside movies, list every class from today's design that would need to change, and every one that would not.
Compare the two AI Corner touchpoints in this session (refine-and-visualize versus diagnose-a-broken-class). Explain why neither one produced information that was genuinely new to this lecture.
In your own words, explain why this session deliberately separates the Overview/Requirements/Class Diagram steps (done today) from the Schema step (moved to next class), rather than compressing all four into one session.
Further Reading
Post-Read 5, Machine Coding 5: Design Parking Lot - the original source of the two-gates-one-spot race condition pattern that BookMyShow's R10/R11 directly extends, and the original source of the PaymentGateway interface and partial-payment reasoning reused unchanged in R13/R14.
Post-Read 6, Machine Coding 6: Code Parking Lot 1 - the original source of the Gate.operator versus Ticket.operator capability-vs-snapshot pattern, directly echoed today by Screen.features versus Show.features and Movie.features versus Show.features.
Post-Read 7, Machine Coding 6.2: Code Parking Lot 2 - the full worked solution to "two gates, one spot," including the per-spot locking fix; revisit this once BookMyShow's Code lectures tackle "two users, one seat," since the same reasoning pattern (critical section, re-check after lock, correct lock granularity) will apply again.
Oracle/Jakarta EE Documentation on the Java Persistence API (JPA) - the official specification reference for @Entity, @Id, and related annotations introduced in Section 5.
Hibernate ORM Official Documentation - the reference for how Hibernate, the JPA implementation used in this course, actually generates SQL from annotated Java classes.
Spring Initializr (start.spring.io) - the actual tool walked through in Section 5.5; worth generating a real test project from, per this session's homework, before next class.
Homework
1. Draw the schema for today's class diagram on your own before
   next class — pay special attention to ShowSeat and
   ShowSeatType, and to whether Feature needs a mapping table.

2. Write out, in plain English, your own answer to: "why can't
   Seat.status alone represent whether a seat is bookable?" Be
   ready to defend it out loud, the same way you'd defend it to
   an interviewer.

3. Go to start.spring.io yourself, and generate one blank test
   project using the exact settings from Section 5.4 (Maven,
   Java, the 5 dependencies listed). Open it in your IDE and just
   run it — you don't need to write anything. The goal is to not
   be doing this step for the first time live in the next class.

4. Use an AI assistant as a mock interviewer. Ask it to challenge
   your BookMyShow design — e.g. "what if a show gets cancelled
   after seats are booked," or "what if a theatre wants to change
   seat layout mid-run." Practice defending your design choices.

5. Push your design notes to GitHub — branch name:
   bookmyshow-design-complete

Last changed by 
 
Tushar Harsan·Follow
0
48
Add a comment
Published on  HackMD
