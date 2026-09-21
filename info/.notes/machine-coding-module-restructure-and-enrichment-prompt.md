# STRICT PROMPT — Restructure and enrich the Applied Machine Coding module with real Scaler course material

Read this entire document before touching any file. This is a large content-authoring task
across TWO files:

1. `api/Data/JavaVerticalSeedData.cs` — the lesson content switch (`GetAuthoredLessonContent`)
   and the module-5 lesson list (`SeedModule5Lessons`).
2. `app/src/data/lessonInteractions.js` — the MCQ data file.

Do not touch any other file. Do not touch any lesson outside the six named below
(`18-how-to-approach-design`, `19-machine-coding-tictactoe`, `20-machine-coding-parking-lot`,
`21-machine-coding-bookmyshow`, `22-machine-coding-splitwise`, `23-machine-coding-contest`).
`24-machine-coding-hotel-management` is explicitly OUT OF SCOPE — leave it completely untouched.

## Why this is happening

Five of this module's six machine-coding lessons (`18`, `19`, `20`, `21`, `22`) currently hold
generic, LLM-invented prose about real system-design topics (TicTacToe, Parking Lot, BookMyShow,
Splitwise) that a real Scaler LLD course actually taught, in detail, across many real class
sessions. That real material has now been gathered and transcribed into this repo, and it is
dramatically richer than what is currently seeded: real requirements numbered R1-R18, real
worked algorithms with complexity analysis, real Java/Spring/JPA code (concurrency fixes, entity
mappings, an settle-up algorithm), and real "AI Corner" verification exercises. The task is to
rewrite these five lessons' `## Concepts Covered` sections using this real material as the
authoritative source, replacing invented content with it wherever they overlap, and to fold a
sixth, redundant lesson (`23-machine-coding-contest`, which duplicates `18`'s "how to approach a
machine coding round" territory almost exactly, with no real source material behind it) into
`18` and then delete it.

## Required reading before writing anything

Read ALL of the following files in full before writing a single word of new lesson content.
They are this task's `SOURCE_TYPE: FROM_MATERIAL` — real, transcribed Scaler class material, not
invented:

**HackMD Pre-Read/Post-Read class notes** (`info/.notes/scaler-raw-notes/hackmd/`):
- `36-BksHm_3Ufx.md` through `45-HkVtld4vMg.md` — earlier sessions already indexed (orientation,
  design patterns, TicTacToe design, Parking Lot design) — skim for continuity, not required in
  full detail.
- `46-rJmbguKDGe.md`, `47-rJGtpPtDzl.md` — Code Parking Lot 1 (Pre-Read + Post-Read): schema
  inheritance, enum-vs-lookup-table test, the parking-spot sizing correction, models, DTOs.
- `48-SJx-mTKwGl.md`, `49-SyG-QptPfx.md` — Code Parking Lot 2 (Pre-Read + Post-Read): generic
  repository, Service layer extraction, the concurrency race condition and its `synchronized` fix,
  a genuinely unsafe AI-suggested optimization.
- `50-H1QaIsMOGg.md`, `51-BJNyvjMOGl.md` — Design BookMyShow (Pre-Read + Post-Read): requirements
  R1-R18, City→Theatre→Screen→Seat, the Seat/ShowSeat status correction, SeatType as configurable
  data, ShowSeatType pricing correction, Spring Boot/JPA primer.
- `52-B1XltyQuGx.md`, `53-ByTltJQ_Mg.md` — Code BookMyShow 1 (Pre-Read + Post-Read): real entity
  code, `@ManyToOne`/`@OneToMany(mappedBy=...)`, `EnumType.STRING` vs `ORDINAL`, `@ElementCollection`,
  `GenerationType.IDENTITY`, Spring Data derived queries.
- `54-H1MF9crufg.md`, `55-SkLF59Hdfg.md` — Code BookMyShow 2 (Pre-Read + Post-Read): the
  check-then-act race condition, why a long transaction and `synchronized` both fail, soft
  locking, `READ_COMMITTED` vs `SERIALIZABLE`, the real concurrency test, `BookingService`.
- `56-rkOoS4TdMe.md`, `57-BymsSNT_Gg.md` — Code BookMyShow 3 (Post-Read + Pre-Read): the lazy
  expiry fix for an abandoned hold, signup/login, BCrypt salted hashing, JPA auditing.
- `58-Hy2Tk1yKMx.md`, `59-SyZCJ1kYfl.md` — Design Splitwise (Pre-Read + Post-Read): requirements
  R1-R12, the paid-vs-owed invariant, the `extra_amount` formula, the sorted-chain and greedy
  get/give settlement algorithms, the NP-hard framing.
- `60-ryhAL8btfx.md`, `61-HJ1iuIbYMg.md` — Code Splitwise 1 (Pre-Read + Post-Read): noun-spotting
  class-diagram method, the dummy-expense trick, `ExpenseUser` as a mapping class, schema, the
  Command pattern for CLI input.

**Companion class-revision notes** (`info/.notes/scaler-raw-notes/companion-notes/`):
- `01-lld-orientation-vehicle-design.md` — the three interview types, the Scaler 6-step
  framework, the Vehicle design worked example.
- `02` through `04` — TicTacToe design, the win-check algorithm's optimization path, bot
  strategies (Easy, Minimax, depth limits).
- `05` through `07` — Parking Lot design, schema/DTOs, the real concurrency fix code
  (`InMemoryRepository<T>`, the `synchronized (spotLock)` block).
- `08` through `11` — BookMyShow design, JPA model code, the booking/race-condition code
  (`BookingService.bookMovie()` with `@Transactional(isolation = Isolation.SERIALIZABLE)`),
  signup/login/auditing code.
- `12` through `14` — Splitwise design, schema/Command pattern, the full settle-up code
  (`SettleUpStrategy`, `NaiveSettleUpStrategy`, `SettleUpService`, `SettleUpController`).

**Existing lesson content, read-only reference for structure and voice**: the current cases for
all six lessons in `api/Data/JavaVerticalSeedData.cs`'s `GetAuthoredLessonContent` switch, and
the existing `## Practical Backend Scenario` / `## Practice Loop` / `## Evidence of
Understanding` / `## Suggested Extension` sections for each — these four H2 sections stay
**completely untouched** for all five lessons; only `## Concepts Covered` gets rewritten.

## Part 1 — Remove `23-machine-coding-contest`

`23-machine-coding-contest`'s three subheadings ("What a Timed Machine Coding Round Actually
Evaluates," "A Repeatable Approach Under Time Pressure," "Common Failure Modes and How to
Self-Review") cover the same ground as `18-how-to-approach-design` — how to approach a machine
coding interview — with no real Scaler session behind it (it was LLM-invented earlier this
project). Before deleting it, read its current full content once, and carry forward into `18`
(Part 2 below) any genuinely distinct, useful point it makes that `18` does not already cover —
do not just discard it silently.

1. In `api/Data/JavaVerticalSeedData.cs`:
   - Remove the `Lessons.Add(new Lesson { ... Slug = "23-machine-coding-contest" ... })` block
     from `SeedModule5Lessons` (or wherever it is registered — search for the slug string).
   - Remove the entire `"23-machine-coding-contest" => @"..."` case from
     `GetAuthoredLessonContent`.
2. In `app/src/data/lessonInteractions.js`:
   - Remove the entire `'java-spring-lld/applied-machine-coding/23-machine-coding-contest': { ... }`
     object (its 6 `practiceQuestions`), including its trailing comma, so the file remains valid.
3. Do not renumber `24-machine-coding-hotel-management` or change its slug. A gap in the numeric
   prefix (`...22, 24...`, no `23`) is expected and fine.

## Part 2 — Rewrite `18-how-to-approach-design`

Keep the existing three subheadings' topics but rewrite them using the real material below, and
fold in `23`'s genuinely distinct point(s) per Part 1. Target 4 `###` subheadings under
`## Concepts Covered`.

Must include, accurately:
- **The three real interview types**: Theoretical (quickfire concept recall, common at older
  companies), Design (~45 minutes, class diagrams + schema design, e.g. "design Tinder"),
  Machine Coding (full working code under time pressure, common at startups and some product
  companies). Ground this in a concrete framing, not just a bullet list.
- **The real Scaler 6-step framework**, in order: Overview (align with the interviewer's actual
  intent) → Gather Requirements (5-8 core features) → Clarify Requirements (edge cases and
  scope) → Class Diagram (built outside-in) → Schema Diagram (only once a real persistent system
  is in scope) → Working Code (built stepwise, under a time box). Note explicitly that a seventh
  step, Follow-up, appears in later Splitwise material as a closing step, so include it too.
- **The "resist the first reaction" discipline** (Step 0): the instinct to instantly start
  listing attributes or jumping to a solution is exactly what a strong candidate suppresses in
  favor of alignment first.
- **The recurring three clarifying questions**, observed across every real design session
  gathered (Parking Lot, BookMyShow, Splitwise): scope (what's actually in/out), persistence
  (does data need to survive between runs, or is in-memory/H2 fine), and interaction mode (CLI
  vs a real API). Naming this as a transferable, repeatable checklist — not something to
  reinvent per problem — is a genuinely new, useful point worth adding here.
- **The worked Vehicle example**: an abstract `Vehicle` class with `VehicleType`/
  `TransmissionType`/`VehicleState` enums; the Aggregation-vs-Composition distinction (Vehicle
  *has* a Driver — aggregation; `FuelTank` is integral to `Engine` — composition); and
  `Refuelable`/`Chargeable` as separate interfaces specifically to avoid forcing an electric
  vehicle to implement a `refuel()` method it has no business having (interface segregation in
  practice, not just in name).
- **Whatever distinct, useful material `23-machine-coding-contest`'s current content contributes**
  beyond what's already listed above (read it first, per Part 1's instruction, before deciding
  what if anything to carry forward).

## Part 3 — Rewrite `19-machine-coding-tictactoe`

Keep the existing four subheadings' general topics, but replace the algorithm and bot-strategy
subsections with the real, specific material below. Target 4 `###` subheadings.

Must include, accurately:
- The real requirement generalization: an **N×N board**, not fixed 3×3, and **N-1 players**
  specifically to keep the game meaningfully contested as N grows (not an arbitrary choice —
  explain why N players on an N×N board would trivially degenerate).
- The real **undo feature trade-off analysis**: three approaches compared — Direct Reversal
  (fine for simple games, breaks for games with side effects like Chess), Replay from Scratch
  (correct for complex rules, wasteful), Snapshot Saving (the actual chosen approach for
  TicTacToe — save board state after every move).
- The real **win-check optimization path**, as an explicit progression, not just the end state:
  naive brute-force checking every possible win condition (O(N³)) → check only the row/column/
  diagonal touched by the *current move*, not the whole board → final solution: maintain running
  hashmap counts of symbols per row, per column, and per diagonal, updated incrementally on each
  move, giving **O(1) win-check per move**. Show this as a real before/after code-shape
  contrast, not just a complexity-number claim.
- **Bot difficulty as the Strategy pattern**: Easy bot (first available empty cell), Minimax
  (theoretically optimal but exponential in board size), and the practical fix actually used —
  a depth limit on larger boards, explicitly framed as a deliberate, honest simplification
  rather than a hidden shortcut.
- **Enums over booleans for cell state**: `CellState` as `EMPTY`/`FILLED`/`BLOCKED` rather than a
  boolean, specifically because it is extensible to states a boolean cannot represent.

## Part 4 — Rewrite `20-machine-coding-parking-lot`

Keep the existing four subheadings' general topics, but deepen each with the specific real
material below, and add real code where noted. Target 4-5 `###` subheadings.

Must include, accurately:
- The real **nine-class design** (`ParkingLot`, `ParkingFloor`, `Gate`, `ParkingSpot`, `Vehicle`,
  `Operator`, `Ticket`, `Bill`, `Payment`), derived from a real user-journey walkthrough (vehicle
  arrives → entry gate → ticket issued → spot assigned → exit gate → payment).
- **Representing inheritance in a schema** — use the Pen/BallPen/GelPen teaching example
  verbatim as the illustrative analogy (it is a genuinely good, concrete way to teach this): the
  naive approach duplicates common columns across every child table and forces UNION queries for
  even simple aggregate questions; the correct approach puts every common attribute on ONE parent
  table, with child tables holding only their own specialized columns plus a foreign key back to
  the parent. Apply this directly to `Payment` → `CashPayment`/`OnlinePayment`.
- **The enum-vs-lookup-table test**: the deciding question is not how the value is used, it's
  "how likely is this set of values to change without a code redeploy." `GateType` (ENTRY/EXIT)
  stays a plain Java enum; `SpotAssignmentStrategyType`/`FeesCalculatorStrategyType` become
  lookup-table-backed classes because they were explicitly required to be swappable at runtime.
- **The parking-spot sizing correction** — a genuine mid-build design gap, not a planned
  refinement: the original "exact type match" rule (a vehicle can only use a spot of its exact
  type) turns out to be wrong once physical size is considered — a spot built for a bigger
  vehicle (BIKE < CAR < TRUCK) can also hold smaller ones. This turns `ParkingSpot`'s vehicle
  type from a single field into a many-to-many `supportedVehicleTypes` list, requiring a real
  mapping table (not a comma-separated column — explain concretely why that breaks: it violates
  1NF and makes a query like "find every spot supporting Van" unreliable and unindexable).
- **The case for DTOs at the controller boundary**, via its two real concrete failure scenarios:
  (1) Caller A and Caller B, two unrelated callers of `issueTicket()`, both silently forced to
  change (or break, if the constructor signature changes) when an unrelated new field
  (`securityClearanceLevel`) is added to `Ticket` — with no DTO, one change breaks N callers;
  with a DTO, it breaks zero. (2) A third-party billing partner calling `issueTicket()` and
  receiving the raw `Ticket` model would see `Operator` (internal HR-adjacent data),
  `assignedSpot`, and any future internal field, none of which they have any legitimate need to
  see — a DTO is a deliberate one-way boundary, not just "a smaller model."
- **The real concurrency fix**, as an actual code block:
  ```java
  public class TicketService {
      private final Object spotLock = new Object();

      public Ticket issueTicket(IssueTicketRequestDTO request) {
          // validate gate, create vehicle...
          ParkingSpot assignedSpot;
          synchronized (spotLock) {
              assignedSpot = allotmentStrategy.findSpot(
                  parkingSpotRepository.findAll(), request.getVehicleType());
              if (assignedSpot == null) {
                  throw new ParkingFullException("No available spot for this vehicle type");
              }
              assignedSpot.setParkingSpotStatus(ParkingSpotStatus.OCCUPIED);
              parkingSpotRepository.save(assignedSpot);
          }
          // create and save ticket...
      }
  }
  ```
  Explain why the lock scope is narrow (just the read-then-write critical section, not the whole
  method), and that the fix was proven with two genuinely distinct `Gate` objects in a real
  concurrency test, not a simulated abstraction of "two requests."

## Part 5 — Rewrite `21-machine-coding-bookmyshow` (largest expansion)

This lesson has the richest real source material of the six (a full Design session plus three
Code sessions). Keep roughly the existing three-subheading shape but expand it to 6 `###`
subheadings covering design, JPA modeling, the concurrency fix, and auth. This lesson may run
longer than the site's normal "advanced mechanism" 1200-1500 word tier — that's expected and
fine given the source depth; do not compress real material just to hit a shorter target.

Must include, accurately:
- **The physical hierarchy and the two real design corrections**: `City`(later renamed `Region`
  in code) → `Theatre` → `Screen` → `Seat`, directly mirroring Parking Lot's composition
  pattern. First correction: booking status cannot live on `Seat` itself, since the same
  physical seat is free for one show and booked for another — it belongs on `ShowSeat`, a
  mapping class keyed by (show, seat). Second correction: price cannot live on `Seat` or
  `ShowSeat` either, since price varies by seat *tier* per show, not per physical seat — it
  belongs on `ShowSeatType`, keyed by (show, seatType).
- **`SeatType` as configurable data, not a shared enum** — the "same set for every owner" test:
  a shared enum only works if every owner in the system agrees on the same values; the moment
  different theatre chains define their own tier names (Gold, Recliner, Executive), it is no
  longer enum material.
- **The capability-vs-snapshot features pattern**, shown twice: `Screen.features` (what a screen
  can physically support, e.g. Dolby Atmos, 3D) versus `Show.features` (what is actually
  switched on for one specific screening) — a screen capable of 3D can still run a specific show
  in plain 2D.
- **Real JPA/entity code and its gotchas**:
  - Reserved-keyword collisions: `User` and `Show` collide with SQL reserved words, fixed with
    `@Entity(name = "users")` / `@Entity(name = "shows")`.
  - Correct `@ManyToOne`/`@OneToMany(mappedBy = "...")` pairing, and the real bug it prevents:
    forgetting `mappedBy` silently creates an unwanted extra join table instead of one clean
    relationship.
  - `@Enumerated(EnumType.STRING)` versus `EnumType.ORDINAL` — STRING is immune to silent data
    corruption if an enum is later reordered or a new constant inserted; ORDINAL is not.
  - `@ElementCollection` for a list of enum values (not `@ManyToMany`, which is for relating two
    real entities with their own tables).
  - `GenerationType.IDENTITY` for primary keys.
- **The seat-booking race condition — the harder sibling of Parking Lot's "two gates, one
  spot"**: "two users, one seat." Walk through why the obvious fixes both fail for concrete,
  different reasons: holding one long transaction across the entire payment flow is correct but
  exhausts database connections at real scale; `synchronized` provides zero protection the
  moment the system runs on more than one server, since each server has its own JVM memory and
  its own separate lock. The real fix: a **soft lock** (an existing `ShowSeatStatus.BLOCKED`
  status field standing in for a lock, so the actual database transaction is milliseconds long)
  combined with `@Transactional(isolation = Isolation.SERIALIZABLE)` around only the short
  check-and-block critical section. Explain concretely why `READ_COMMITTED` (the default) still
  lets two threads through — it only guarantees you never read uncommitted data, it does not
  check whether someone else changed the row between your read and your write — while
  `SERIALIZABLE` catches the conflict by reasoning about valid one-at-a-time orderings, without
  serializing unrelated rows. Include the real method shape as a code block:
  ```java
  @Transactional(isolation = Isolation.SERIALIZABLE)
  public Booking bookMovie(Long userId, List<Long> seatIds, Long showId) {
      User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("User not found"));
      Show show = showRepository.findById(showId).orElseThrow(() -> new RuntimeException("Show not found"));

      List<ShowSeat> showSeats = showSeatRepository.findAllById(seatIds);
      for (ShowSeat showSeat : showSeats) {
          boolean isAvailable = showSeat.getShowSeatStatus() == ShowSeatStatus.AVAILABLE;
          boolean isExpiredBlock = showSeat.getShowSeatStatus() == ShowSeatStatus.BLOCKED
                  && Duration.between(showSeat.getBlockedAt().toInstant(), new Date().toInstant()).toMinutes() > 15;
          if (!(isAvailable || isExpiredBlock)) {
              throw new RuntimeException("Seat " + showSeat.getId() + " is not available");
          }
      }
      for (ShowSeat showSeat : showSeats) {
          showSeat.setShowSeatStatus(ShowSeatStatus.BLOCKED);
          showSeat.setBlockedAt(new Date());
          showSeatRepository.save(showSeat);
      }
      Booking booking = new Booking();
      // assign remaining fields, save, return
      return bookingRepository.save(booking);
  }
  ```
  Note the `isExpiredBlock` check is the **lazy expiry** fix: a seat abandoned mid-payment is not
  proactively swept by a background job, it is simply re-evaluated the moment someone else's
  request reads it — explain why this is a complement to, not a replacement for, occasional
  proactive sweeping.
  Explicitly state the fix was proven with a real concurrency test using genuinely separate
  threads targeting the same seats, checking the correct invariant across repeated runs (never
  zero bookings succeed, never two threads both succeed for the same seat).
- **Authentication and auditing**: why plaintext and naive fixed-hash password storage both fail;
  BCrypt embeds a fresh salt directly inside the stored hash string itself, so verification
  (`matches()`, never `equals()`) re-derives and compares without ever decrypting anything.
  `@CreatedDate`/`@LastModifiedDate` are inert on their own — they require both
  `@EntityListeners(AuditingEntityListener.class)` on the base entity and `@EnableJpaAuditing` on
  the application's entry point before they do anything at all.

## Part 6 — Rewrite `22-machine-coding-splitwise` (major expansion)

Splitwise's real material is algorithm-heavy rather than structure-heavy — the class diagram
was deliberately not built live in the real course until the second session, because the hard
problem here is algorithmic. Expand to 5-6 `###` subheadings, giving the settlement algorithm
real, worked weight rather than a passing mention.

Must include, accurately:
- **The real requirements shape (R1-R12)**: user/group management, the paid-vs-owed invariant
  for every expense (`sum(paid) == sum(owed)` — if this doesn't hold, money has silently
  vanished or appeared from nowhere), individual settle-up (R10: one person across every expense
  they're part of anywhere) versus group settle-up (R11: one group's own expenses only, leaving
  unrelated balances untouched) as genuinely different scopes, and transaction-minimization as
  an explicit "good to have," not a hard requirement.
- **The `extra_amount` balance formula**, spelled out concretely: for each person, across every
  expense, `extra_amount += whoPaid[person] - whoHadToPay[person]`; a positive total means they
  are owed money, negative means they owe money; the sum across everyone in a group must always
  be zero. Walk a small worked example (3-4 people, 2-3 expenses) rather than stating the formula
  abstractly.
- **Two competing settlement algorithms, explicitly contrasted, not just the final one presented
  as if it were obvious**:
  1. **Sorted-chain (brute-force)**: mathematically correct, uses at most n-1 transactions, but
     produces socially awkward pairings (e.g. someone who barely owes anything ends up owing the
     single biggest creditor directly).
  2. **Greedy get/give (the practical fix)**: split people into a "GET" group (creditors) and a
     "GIVE" group (debtors), each a max-heap by amount; repeatedly match the biggest creditor
     with the biggest debtor, settling at least one side fully each round; same n-1 upper bound,
     but far more sensible pairings in practice, at O(n log n).
  3. **Explicitly name that minimizing to the true mathematical minimum is NP-hard** — the
     greedy approach is a deliberate, honest approximation with a known bound, not a disguised
     exact solution, and that distinction (provably hard vs. "I didn't think about it") is itself
     the point worth teaching.
- **The noun-spotting class-diagram method** — a genuinely different technique from the
  physical-hierarchy visualization used for Parking Lot and BookMyShow, applied by reading
  requirements text directly and asking, for each noun, whether it deserves its own class, is
  really just an attribute, or describes behavior that becomes a Service method instead.
- **The dummy-expense trick**: rather than inventing a separate `Transaction` class for
  settlements (which would create two sources of truth for "money moving between people"), a
  settlement is modeled as a specially flagged `Expense` (`ExpenseType.PAYMENT` vs
  `ExpenseType.NORMAL`) — reusing the existing ledger rather than duplicating it.
- **`ExpenseUser` as the relationship-shaped mapping class**: "how much did this person pay for
  this expense" depends on both `User` and `Expense` together, so it cannot cleanly live as an
  attribute of either alone — the same reasoning already used for BookMyShow's `ShowSeatType`.
- **The five-table schema**: `users`, `groups`, `group_members` (many-to-many), `expenses`,
  `expense_users`.
- **The Command pattern for CLI input**, as a real refactor, not just a definition: a naive
  `main()` full of if-else branches per command violates SRP and gets worse with every new
  command; the fix is a `Command` interface (`matches(input)` / `execute(input)`) plus a
  `CommandExecutor` that Spring's dependency injection automatically collects every `Command`
  bean into, dispatching to whichever one matches.
- **Real settle-up code**, as an actual block:
  ```java
  public interface SettleUpStrategy {
      List<Expense> settleUp(List<Expense> expensesToSettleUp);
  }

  @Service
  public class NaiveSettleUpStrategy implements SettleUpStrategy {
      @Override
      public List<Expense> settleUp(List<Expense> expensesToSettleUp) {
          // compute extra_amount per user, split into GET/GIVE heaps,
          // greedily match biggest creditor with biggest debtor
      }
  }
  ```
  and mention `ExpenseRepository.findAllByGroup` / `ExpenseUserRepository.findAllByUser` as the
  real Spring Data query methods the settle-up service is built on.
- **The H2-vs-MySQL tooling choice**, contrasted directly with BookMyShow: Splitwise's own
  requirements confirm no data needs to survive between runs, so an in-memory H2 database (and
  no web starter, since input is CLI-driven) is the correct, deliberate choice — not a
  simplification to apologize for.

## Constraints — read before writing

- Only edit `api/Data/JavaVerticalSeedData.cs` (Part 1 removal + Parts 2-6 rewrites) and
  `app/src/data/lessonInteractions.js` (Part 1 removal only — do not touch the existing MCQ
  entries for `18`, `19`, `20`, `21`, or `22`; the new prose does not invalidate those questions).
- Tag all new/rewritten prose content implicitly as `SOURCE_TYPE: FROM_MATERIAL` in spirit (it is
  now sourced from real transcribed class material) — no literal tag needed in lesson prose
  (that convention is for MCQs/exercises per `CLAUDE.md`), but do not blend in invented facts not
  supported by the source files.
- Every rewritten lesson must still open its `## Concepts Covered` section the same way and end
  it before `## Practical Backend Scenario`, which — along with `## Practice Loop`, `##
  Evidence of Understanding`, and `## Suggested Extension` — stays **completely unchanged** for
  all five lessons.
- Keep the existing code style: fenced ` ```java ` blocks, real class/method bodies (not
  pseudocode), matching indentation and quote style already present in the file's other embedded
  code blocks.
- Do not shorten `21` or `22` to fit the standard word-count tier — their real source material is
  substantial (4 and 4 real class sessions respectively); comprehensiveness matters more than
  hitting a target length here.
- Do not touch `24-machine-coding-hotel-management` or any lesson outside this module.

## Output expectations

Produce the complete, modified `api/Data/JavaVerticalSeedData.cs` and
`app/src/data/lessonInteractions.js` (or unified diffs — state which). Report, per lesson,
roughly how many words/characters the rewritten `## Concepts Covered` section grew by, and
confirm the `23-machine-coding-contest` removal is clean in both files.

## Verification checklist (self-check before returning the result)

1. `grep -c '_ => null'` in `GetAuthoredLessonContent` is unchanged (removing a case does not
   change this count; only content between existing cases changed).
2. `grep -c "23-machine-coding-contest"` across the whole repo returns 0 (fully removed from both
   files, including the `SeedModule5Lessons` registration).
3. Lessons `18`, `19`, `20`, `21`, `22` each still open `## Concepts Covered` right after the
   lesson's leading `# Lesson N — ...` line (or wherever the existing file places it) and still
   flow into an unchanged `## Practical Backend Scenario` afterward.
4. Every new ` ```java ` fence has a matching closing fence (`grep -c '```'` is even).
5. `lessonInteractions.js` still has exactly 11 `practiceQuestions:` object removed as one
   (the count of top-level lesson keys under `applied-machine-coding` drops by exactly 1 — from
   `23-machine-coding-contest`'s removal — and no other key changed).
6. No lesson content for `24-machine-coding-hotel-management` or any lesson outside this module
   changed at all — diff should show zero touches there.

## After this lands — manual DB cleanup (tell the user, do not attempt yourself)

Deleting the seed-code case does not delete the already-seeded DB row for
`23-machine-coding-contest`. After this change is applied and reseeded, the user will need to
run (against both WSL and EC2, same pattern as prior reseed steps this project has used):

```sql
DELETE FROM lessons WHERE slug = '23-machine-coding-contest';
```

Only after first confirming no other table has a foreign key row pointing at that lesson's `id`
(check `lesson_resources`, `lesson_notes`, `lesson_concept_links`, `lesson_diagrams`,
`lesson_code_comparisons`, `lesson_relations`, `reading_map_items` for any row referencing it —
this repo's own earlier investigation this session found none, but re-verify against the live
DB before deleting, since state may have changed).
