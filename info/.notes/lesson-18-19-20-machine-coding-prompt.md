# Prompt for Local LLM — Author real content for Lessons 18, 19, 20

## Context

`api/Data/JavaVerticalSeedData.cs`'s `GetAuthoredLessonContent` method has no case for
`"18-how-to-approach-design"`, `"19-machine-coding-tictactoe"`, or
`"20-machine-coding-parking-lot"`. Those three lessons currently render only the bare
placeholder `ContentBody` set in `SeedModule5Lessons` (a few "Key Topics" bullets, no real
content). The content below is grounded in real Scaler class material (handwritten notes
and post-read summaries) and is ready to use verbatim.

**Note on scope**: Lessons 21 (`21-machine-coding-bookmyshow`), 22
(`22-machine-coding-splitwise`), and 23 (`23-machine-coding-contest`) are intentionally
**not** included here — no source material exists for them yet. Do not touch those three
cases; leave them exactly as they are.

**Note on MCQs**: none of these three lessons get a `## Self-Check` section. No verbatim MCQ
question material exists in the source for these topics (only conceptual summaries) — do
not invent any. This matches the precedent already set for `15-creational-patterns`, which
also has real content with no self-check section.

## Task

Add three new cases to the `GetAuthoredLessonContent` switch expression in
`api/Data/JavaVerticalSeedData.cs`, alongside the existing cases (e.g. right after
`"17-behavioural-patterns-uml"` or wherever fits the existing ordering convention). Use the
exact same C# pattern as every other case: `"<slug>" => @"<content>",` with a verbatim
string, doubling any literal `"` inside the content (`""`) per the file's established
convention.

Insert the following three content blocks verbatim (only fix internal quote-doubling for
C# verbatim-string syntax — do not reword, shorten, or rephrase anything below):

---

### `18-how-to-approach-design`

```
# Lesson 18 — How to Approach Design Problems

A repeatable framework for machine coding interviews and real-world system design: requirements gathering, entity identification, relationship mapping, and iterative refinement.

## Concepts Covered

Machine coding interviews fail most often not from lack of Java knowledge but from lack of sequencing discipline — jumping straight into classes before the requirements are pinned down. Scaler's 6-step framework exists to prevent that: Step 0 is alignment with the interviewer (or with yourself, in a solo problem) — confirm what you already know and explicitly name what you don't, rather than assuming. Two questions settle the shape of the whole exercise before any design starts: does this system need to persist data, or is an in-memory, single-run structure acceptable; and how will a user actually interact with it — a REST API, a CLI, or a hardcoded `main()` method exercising the classes directly. Getting these two answers wrong early costs far more time than getting them right.

Step 1 is requirement gathering, typically producing 5–10 explicit, numbered requirements (R1, R2, R3...) rather than a vague paragraph. Step 2 clarifies and resolves tradeoffs within those requirements — this is where multiple candidate approaches to a tricky requirement (like an undo feature, or a pluggable pricing strategy) get compared on time and space complexity before committing to one. Step 3 turns the clarified requirements into a class diagram: nouns from the requirements become candidate classes, verbs become candidate methods, and the diagram should be walkable as a user journey — a reader should be able to trace what happens, in order, class by class, when a user performs the core action.

A phrase like "this behavior needs to be swappable without rewriting the system" is a Strategy pattern appearing in plain English — trained eyes catch it during requirement clarification, before any diagramming starts, rather than noticing only once the code has already ossified around a single hardcoded approach. Requirements that describe multiple interchangeable algorithms (fee calculation, spot assignment, bot difficulty, winning-condition checks) are the strongest signal.

## Practical Backend Scenario

A team is asked to design a vehicle management system: a `Vehicle` class family covering fuel, electric, and hybrid types, each supporting `refuel()`, `recharge()`, and `start()`/`stop()` operations where applicable. Before any class is written, Step 0 settles that this is an in-memory entity system exercised via a hardcoded `main()` — no database, no REST layer. Step 1 produces requirements: vehicles have name, brand, cost, and type; hybrid vehicles must support both refueling and recharging; transmission type (automatic or manual) needs a shared base representation. Step 2 clarifies the inheritance shape — an `IVehicle` interface at the top, with `IFuelable` and `IRechargeable` capability interfaces mixed in per vehicle type, so a `HybridVehicle` can implement both without a fragile single-inheritance chain forcing awkward compromises.

## Practice Loop

Apply the 6-step framework to a single new problem end to end: state Step 0's two answers explicitly (persistence? interaction mode?) before writing a single requirement. Write 6–8 numbered requirements for a vehicle rental system. Identify which requirement phrases signal a Strategy pattern before drawing anything. Produce a class diagram from those requirements, and verify it by walking through one full user journey (a user rents a vehicle, drives it, returns it) using only the diagram — if a step in the journey can't be traced to a class and method, the diagram is incomplete.

## Evidence of Understanding

You can name Step 0's two settling questions from memory and explain why answering them first changes everything downstream. You can read a requirement and identify, before diagramming, whether it signals a Strategy pattern. You can produce a class diagram directly from a numbered requirements list and defend each class's existence by pointing to the requirement that justified it.

## Suggested Extension

Take a requirements list you've already turned into a class diagram for a past problem and audit it: for every class, can you name the exact requirement number that justified its existence? Any class that can't be justified this way is a sign the framework was skipped, not followed.
```

---

### `19-machine-coding-tictactoe`

```
# Lesson 19 — Machine Coding: TicTacToe

Design and implement a clean, extensible TicTacToe engine: board abstraction, player management, win-condition strategy, and handling NxN generalization.

## Concepts Covered

TicTacToe is Scaler's first full application of the 6-step framework to a complete, working system, and its value is in the seven requirements it generates: an N×N board (not fixed at 3×3), up to N−1 players, unique symbols chosen per player, support for bot players, bots with a difficulty curve (easy, medium, hard), configurable win-condition rules chosen before the game starts, and an undo feature. Each of these pushes the design toward extensibility rather than a special-cased 3×3, two-player script.

The undo feature is the requirement most worth slowing down on, because three genuinely different implementations exist with different tradeoffs. The first stores a stack of past moves and works for TicTacToe specifically, but breaks down for games with more complex state mutation per move (chess captures, for example) because undoing a move isn't always the exact inverse of applying it. The second replays all N−1 prior moves onto a freshly empty board — correct for any game, but O(N²) time and O(N·N·m) space for m stored move-lists, since every undo re-simulates from scratch. The third stores a full board snapshot after every move, making undo an O(N) lookup — trading memory for speed, which is the right trade for a bounded board size where snapshots stay small.

Win-condition checking has its own optimization arc, moving through four solutions. The naive approach checks every player against the entire board (every row, column, and diagonal) after every move: O(N³). Since only the player who just moved could possibly have created a new winning line, checking only the current player already drops this to O(N²). Since a move at position (i, j) can only ever affect row i, column j, and — only when i == j or i + j == N−1 — one or both diagonals, checking only the touched lines drops this further to O(N). The final optimization replaces re-scanning entirely with running counters: a map per row, per column, and two fixed maps for the diagonals, incremented on every placed symbol and compared against N. This reaches O(1) time per move at the cost of O(N) additional space — for a bounded board size, accepting that space cost for constant-time checking is the correct trade, and it only works if the counters live as persistent fields on the class, not as local variables recreated on every call.

Three design patterns organize the resulting system. `Game` is constructed exclusively through a `GameBuilder`, whose validation (bot count capped at one per game, player count matching board dimension minus one, symbol uniqueness across all players) runs before any `Game` instance can exist — a private constructor makes bypassing this impossible. Player creation goes through a `PlayerFactory` returning the correct concrete type. Both winning-condition checks and bot move-selection are Strategy implementations: a `WinningStrategy` interface lets a new rule be added as one new class without touching `Game`'s core logic, and `BotPlayingStrategy` implementations (an easy strategy picking the first empty cell, a hard strategy using minimax with alpha-beta pruning) let a `Bot` delegate its move-selection entirely, keeping `Bot` itself thin.

## Practical Backend Scenario

A generalized N×N TicTacToe engine needs to support a variable board size chosen at game start, an arbitrary number of human and bot players up to N−1, and a pluggable win-condition so a "diagonal-only" or "four-corners" variant can be added later without modifying `Game`. The engine also needs O(1) win detection per move so that even a large board doesn't degrade turn latency, and an undo feature cheap enough to support repeatedly without rebuilding board state from scratch.

## Practice Loop

Implement the core model — `Board`, `Cell`, `Symbol`, `Move`, an abstract `Player` — with `Game` buildable only through `GameBuilder`, enforcing the three validations (bot cap, player count, symbol uniqueness). Implement `RowWinningStrategy`, `ColWinningStrategy`, and `DiagonalWinningStrategy` using persistent running-count maps rather than rescans, and verify each fires in O(1) per move. Implement `EasyBotPlayingStrategy` (first empty cell) and, as a stretch, a `HardBotPlayingStrategy` using minimax. Implement one undo approach and justify, in a comment, why you chose it over the other two given this specific bounded board size.

## Evidence of Understanding

You can explain all four stages of the win-checking optimization and why each one is strictly better than the last for this problem's bounds. You can compare the three undo approaches by time and space complexity and justify your choice for a bounded N. You can point to the exact three validations `GameBuilder` must enforce and explain why a private `Game` constructor is what makes them unbypassable. You can explain why `WinningStrategy` is a list rather than a single implementation.

## Suggested Extension

Add a new winning condition (for example, four-in-a-row on any N×N board, not just the standard N-in-a-row) as a single new `WinningStrategy` implementation, and confirm `Game`'s core logic required zero changes to support it.
```

---

### `20-machine-coding-parking-lot`

```
# Lesson 20 — Machine Coding: Parking Lot

Design and implement a multi-floor parking lot system: spot types, vehicle hierarchy, entry/exit ticketing, fee calculation strategy, and concurrent slot management.

## Concepts Covered

Parking Lot moves the 6-step framework from a pure game (TicTacToe) to a system involving physical resources and financial transactions, and the eight requirements it generates read differently as a result: multiple floors per lot, vehicle-type-specific spots with exact-match allocation only (a truck can never occupy a car spot), a token created and a spot assigned simultaneously at entry, payment and spot-release happening together at exit, dynamically swappable fee-calculation algorithms, support for both cash and third-party online payment, multiple physically distinct entry and exit gates, and configurable spot assignment (auto-nearest-pick or user selection). Requirements 5 and 8 are the same Strategy-pattern signal from Lesson 18 appearing twice in one problem — two separate interfaces are needed, one for fee calculation and one for spot allotment.

Walking through a driver's actual journey — arrive, receive a ticket, park, later present the ticket, pay, leave — yields nine classes: `ParkingLot`, `ParkingFloor`, `Gate`, `ParkingSpot`, `Vehicle`, `Operator`, `Ticket`, `Bill`, and `Payment`. Several of the modeling decisions here generalize well beyond parking lots. `Gate` is one class with a `GateType` enum (ENTRY or EXIT) rather than two separate `EntryGate`/`ExitGate` classes, because the two are identical except for that one field — creating a subclass distinction for a single enum value is needless duplication. `Ticket` captures its own `operator` field as a snapshot at the moment of issue, distinct from `Gate.operator`, which reflects whoever is *currently* staffing that gate — conflating the two would mean a ticket's audit trail silently changes when a shift changes, which is wrong: a ticket must record who was actually on duty when it was issued. `Bill` holds a `List<Payment>` rather than a single `Payment`, because real payment splitting (part cash, part card) needs to be representable, and each payment in the list can be independently refunded or audited. `ParkingSpot` stores its `floorId` directly rather than deriving it by walking up through the floor object on every lookup — a deliberate duplication justified by how frequently that lookup happens (printing every ticket), not applied blindly everywhere.

Schema design here follows the same class-to-table algorithm from earlier lessons — every class becomes a table, every simple attribute becomes a column, and every attribute that is itself another class needs its cardinality checked before deciding where the foreign key goes. `ParkingLot`-to-`ParkingFloor` is one-to-many, so `parking_lot_id` lives on the `parking_floor` table, not the reverse — a single `floor_id` column on `parking_lot` could only ever reference one floor, which can't represent a lot having many floors. `Bill`-to-`Payment` is similarly one-to-many, so `bill_id` sits on the `payment` table. `Gate`-to-`Operator`, by contrast, is genuinely many-to-many across the shift history (many operators work many gates over time), which would need its own mapping table if that full history matters — a plain foreign key column would only capture the *current* operator, matching what `Gate.operator` is meant to store, but not the shift history.

The design deliberately leaves one real gap unresolved after the class diagram is complete: nothing in the paper design prevents two entry gates from assigning the same empty spot to two different vehicles arriving at nearly the same moment. `AllotmentStrategy.assignSpot()` decides which spot to hand out, but no lock exists between the moment it reads "this spot is free" and the moment it commits that assignment — a genuine concurrency problem that only manifests when gates run concurrently, and one that a single-threaded paper design cannot surface or fix by itself.

## Practical Backend Scenario

A third-party facility-management company needs an in-memory, command-line parking system for airports and malls: multiple floors, vehicle-type-exact spot matching, tickets issued at entry with an assigned spot, bills generated at exit supporting split cash/card payment, and a fee-calculation algorithm that must be swappable per client contract without a code change to the core system.

## Practice Loop

Design the nine core classes and both Strategy interfaces (`FeeCalculationStrategy`, `AllotmentStrategy`), building `ParkingLot` through a `ParkingLotBuilder` that validates floors, gates, and both strategies are set before the lot becomes usable. Implement entry (token creation plus spot assignment as one atomic step from the caller's perspective) and exit (bill generation, payment collection, spot release) as end-to-end flows through in-memory collections. Derive the schema from your class diagram using the class-to-table algorithm, and justify every foreign key placement by naming the cardinality that dictated it. Finally, without writing concurrent code, write down in one paragraph exactly where the two-entry-gates race condition would occur in your specific implementation.

## Evidence of Understanding

You can justify why `Gate` is one class with an enum rather than two subclasses, and why `Ticket` needs its own `operator` snapshot separate from `Gate.operator`. You can explain why `Bill` holds a list of payments rather than one. You can derive correct foreign key placement for a one-to-many relationship from the cardinality alone, and explain why placing the key on the "one" side is representationally impossible. You can identify, without writing any threading code, exactly where a concurrent access race would occur in a spot-allotment flow.

## Suggested Extension

Add a `ReservationStrategy` allowing spots to be pre-booked ahead of physical arrival, and work through how it interacts with `AllotmentStrategy` — does a reservation reduce the pool `AllotmentStrategy` chooses from, or bypass it entirely for that vehicle?
```

---

## Constraints

- Do not touch `21-machine-coding-bookmyshow`, `22-machine-coding-splitwise`, or
  `23-machine-coding-contest` — leave those cases exactly as they currently are (still
  falling through to the placeholder `ContentBody`).
- Do not add a `## Self-Check` section to any of these three — none is included above, and
  none should be added.
- Do not modify `SeedModule5Lessons`, `BackfillLessonContent`, `NeedsLessonContent`, or any
  other method — only add the three new switch cases to `GetAuthoredLessonContent`.
- Do not touch `lessonInteractions.js` for this task — it is unrelated to this change.
- Preserve exact existing indentation, `=>` formatting, and quote-doubling convention used
  by every other case in the switch expression.
- The file must remain balanced (braces/parens, doubled-quote pairs) and compile after the
  change.

## Output expectations

Return the full updated `api/Data/JavaVerticalSeedData.cs` (or a unified diff against the
current file) with the three new cases added and nothing else changed.
