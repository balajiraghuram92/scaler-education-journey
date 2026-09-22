# STRICT PROMPT — Wire 2 real Parking Lot exercises into the live grading system

Read this entire document before touching any file. This adds new exercise directories under
`exercises/java/java-lld/applied-machine-coding/` only. Do not touch any other file, and do not
touch anything under `exercises/practice-pool/` except to read from it (it is the source
material, read-only for this task).

## Why

`20-machine-coding-parking-lot` currently has zero wired exercises, despite two real, complete,
already-tested Scaler exercises sitting unwired at:
- `exercises/practice-pool/java/generate-ticket-for-parking-lot-system/`
- `exercises/practice-pool/java/display-parking-lot-capacity/`

Both were verified (by Claude, this session) to be genuinely framework-free plain Java —
no Spring, no JPA, no Lombok anywhere in their source — so they already match this repo's
existing lean exercise contract almost exactly. This is different from the Splitwise exercises
also sitting in the practice pool (`splitwise-manage-group-members`,
`splitwise-create-delete-group`), which genuinely DO use Spring (`@Controller`, `@Autowired`) and
JPA/Lombok (`@MappedSuperclass`, `@Id`, `@Data`) in their real source — **do not touch those, they
are explicitly out of scope for this prompt** and need a separate decision (adapt vs. extend the
sandbox) before anyone converts them.

## Required reading before writing anything

Read the full existing reference contract, end to end, so the new exercises match it exactly, not
approximately:
- `exercises/java/java-lld/applied-machine-coding/hotel-add-rooms/exercise.json`
- `exercises/java/java-lld/applied-machine-coding/hotel-add-rooms/pom.xml`
- Every file under `hotel-add-rooms/starter/` and the same paths under `hotel-add-rooms/solution/`
  — diff them mentally (or literally, with `diff`) to see exactly how an "editable" file's real
  implementation gets replaced with a `// TODO: ...` comment plus a minimal compiling stub
  (e.g. `return null;`) in the starter, while non-editable files (DTOs, models, exceptions,
  interfaces) are byte-identical between starter and solution.
- `hotel-add-rooms/tests/src/test/java/.../RoomControllerTests.java` — the test file convention.
- `api/Services/Exercises/ExerciseRepository.cs` and `ExerciseWorkspaceBuilder.cs` (if present) —
  confirm exactly how `files[]`, `testSuite`, and `evidence[]` are consumed at runtime, so the two
  new `exercise.json` files are contractually correct, not just visually similar.

## Task — Exercise 1: Generate Ticket for Parking Lot System

Source: `exercises/practice-pool/java/generate-ticket-for-parking-lot-system/` (real Scaler
solution + real test file `src/test/java/com/scaler/parking_lot/controllers/TestTicketController.java`,
7 real `@Test` methods, already verified passing-shape by Claude).

1. Create `exercises/java/java-lld/applied-machine-coding/generate-parking-ticket/`.
2. Copy the real `pom.xml` shape from `hotel-add-rooms/pom.xml` (JUnit Jupiter 5.7.0 + `org.reflections`
   0.10.2, `maven.compiler.source/target=11`, surefire plugin) — do NOT reuse the practice-pool
   copy's Spring Boot `pom.xml`, it is unused scaffolding the real code never references.
3. Copy every file under `src/main/java/com/scaler/parking_lot/` from the practice-pool source
   into both `solution/src/main/java/com/scaler/parking_lot/...` (verbatim, unchanged) and
   `starter/src/main/java/com/scaler/parking_lot/...` (same tree, but see step 4).
4. In the **starter** copy only, strip the real implementation out of exactly these files (the
   "editable" set — everything else stays byte-identical to the solution):
   - `services/TicketServiceImpl.java` — replace the body of `generateTicket(...)` with a
     `// TODO: ...` comment describing the real steps (look up the gate, reject exit gates,
     find-or-create the vehicle, resolve the parking lot from the gate, assign a spot via the
     strategy, build and save the Ticket) and a minimal compiling stub (`return null;` or
     equivalent matching the declared return type/throws clause).
   - `respositories/InMemoryGateRepositoryImpl.java`, `InMemoryParkingLotRepositoryImpl.java`,
     `InMemoryTicketRepositoryImpl.java`, `InMemoryVehicleRepositoryImpl.java` — strip each
     method body to a TODO + minimal stub the same way, following the exact pattern
     `hotel-add-rooms`'s starter repositories use (check those files for the precedent before
     guessing the shape).
   - `strategies/assignment/AssignNearestAvailableSpotStrategy.java` and
     `EqualDistributionAssignmentStrategy.java` — same TODO+stub treatment.
   Leave every model, DTO, exception, and interface file identical between starter and solution
   (these are the "non-editable" contract files, same as `hotel-add-rooms`).
5. Copy the real test file verbatim into
   `tests/src/test/java/com/scaler/parking_lot/controllers/TestTicketController.java`.
6. Write `exercise.json`:
   - `id`: `"java-lld-generate-parking-ticket"`
   - `lessonSlug`: `"20-machine-coding-parking-lot"`
   - `title`: `"Parking Lot — Generate Entry Ticket"`
   - `language`: `"java"`, `difficulty`: `"intermediate"`, `estimatedMinutes`: 45
   - `runtime`: `{ "profile": "java-maven", "javaVersion": 11, "timeoutSeconds": 10 }`
   - `files[]`: every file under `src/main/java/...`, `editable: true` only for the 6 files
     listed in step 4, `editable: false` for everything else (models, DTOs, exceptions,
     interfaces `TicketService`, `GateRepository`, `ParkingLotRepository`, `TicketRepository`,
     `VehicleRepository`, `SpotAssignmentStrategy`).
   - `testSuite`: `{ "visible": false, "path": "tests/src/test/java/com/scaler/parking_lot/controllers/TestTicketController.java", "className": "TestTicketController" }`
   - `evidence[]`: one entry per real `@Test` method, using the method's own real assertion intent
     as the label (do not invent claims — read each test method's assertions and describe what it
     actually proves):
     - `testIssueTicketWith1AvailableParkingSpot`
     - `testIssueTicketWith2AvailableParkingSpots`
     - `testIssueTicketWithNoAvailableSpots`
     - `testIssueTicketWithFromExitGate`
     - `testIssueTicketFromNonExistingGate`
     - `testIssueTicketWith3Floors2CarsOn1stAnd2ndFloorAnd1On3rdFloor`
     - `testIssueWithWith1FloorUnderMaintenance`

## Task — Exercise 2: Display Parking Lot Capacity

Source: `exercises/practice-pool/java/display-parking-lot-capacity/` (real Scaler solution + real
test file `src/test/java/com/scaler/parking_lot/controllers/ParkingLotControllerTest.java`, 7 real
`@Test` methods).

Follow the exact same process as Exercise 1:
1. Create `exercises/java/java-lld/applied-machine-coding/display-parking-lot-capacity/`.
2. Same lean `pom.xml` shape (reuse from `hotel-add-rooms`).
3. Copy `src/main/java/com/scaler/parking_lot/` into both `solution/` and `starter/`.
4. In `starter/` only, strip `services/ParkingLotServiceImpl.java`'s
   `getParkingLotCapacity(...)` body to a TODO + stub (the real logic: look up the parking lot,
   throw `InvalidParkingLotException` if missing, filter to the requested floor ids (or all floors
   if none given), filter to the requested vehicle types (or all types if none given), and for
   each floor compute available-spot counts per vehicle type via `ParkingFloorUtils`), and strip
   `respositories/InMemoryParkingLotRepositoryImpl.java` the same way. Also check
   `utils/ParkingFloorUtils.java` — if it contains the actual counting logic being tested, strip
   it too and add it to `files[]` as editable; if it's a trivial helper with nothing to implement,
   leave it non-editable. Everything else stays identical between starter and solution.
5. Copy the real test file verbatim into
   `tests/src/test/java/com/scaler/parking_lot/controllers/ParkingLotControllerTest.java`.
6. Write `exercise.json` with `id: "java-lld-display-parking-lot-capacity"`,
   `lessonSlug: "20-machine-coding-parking-lot"`, and `evidence[]` mapped to all 7 real test
   methods (`testGetParkingLotCapacityWithNegativeParkingLotId`,
   `testGetParkingLotCapacityWithInvalidParkingLotId`,
   `testGetParkingLotCapacityWithNoVehiclesParked`,
   `testGetParkingLotCapacityWithFewSpotsOccupied`,
   `testGetParkingLotCapacityWithFewSpotsOccupiedAndJust2ndFloor`,
   `testGetParkingLotCapacityWithFewSpotsOccupiedAndVehicleTypeCar`,
   `testGetParkingLotCapacityWithFewSpotsOccupiedAndVehicleTypeCarAnd2ndFloor`), same
   label-from-real-assertion-intent rule as Exercise 1.

## Critical constraint — actually verify this compiles, do not just assert it does

This project's earlier attempt at self-reported verification (a different task, same repo)
included a fabricated number that didn't match reality when independently checked. Do not repeat
that failure mode here. For **both** exercises, before reporting completion:

1. Actually run `mvn test` (or the equivalent for this environment) against the **solution**
   variant and confirm all 7 tests genuinely pass — paste the real command output, not a summary
   claim.
2. Actually run `mvn test` against the **starter** variant and confirm it compiles (proving the
   stubs are syntactically valid) but fails the tests (proving the TODOs aren't accidentally
   already-working implementations) — paste the real output.
3. If you cannot actually execute Maven in your environment, say so explicitly and clearly in
   your response instead of asserting success. An honest "I could not verify this compiles" is
   far more useful than a confident claim that turns out to be wrong.

## Constraints

- Do not touch `exercises/practice-pool/` (read-only source for this task).
- Do not touch the Splitwise exercises in the practice pool at all.
- Do not touch any existing wired exercise (`hotel-*`, `tictactoe-*`).
- Match `hotel-add-rooms`'s exact file/JSON conventions — do not invent a different shape.

## Output expectations

Report, per exercise: the real `mvn test` output for both starter and solution (or an explicit
statement that you could not run Maven), the final file tree, and the `exercise.json` content.
