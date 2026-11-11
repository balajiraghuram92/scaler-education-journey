# Python port — phase prompts

Run the phases in order, one Muse session per phase. After each phase, stop and have the result reviewed before starting the next. Start each session by pasting **one** block below (everything between two `=====` lines) into Muse Code at the repository root.

Run P6 only after the localization fixes (L1–L3) are merged, so the port copies the corrected code.

=====

## P0 — Scaffold, configuration, parity tooling

Read `info/muse-prompts/python-port/PORT-RULES.md` in full and follow it. Then read `api/Program.cs` (all of it), `api/appsettings.json`, `api/appsettings.Development.json`, every file in `api/Options/`, `api/Dockerfile`, `docker-compose.yml` and `docker-compose.dev.yml`.

Build the skeleton only; port no business logic yet.

1. Create the `api-python/` layout from PORT-RULES.
2. `app/settings.py`: one settings class per file in `api/Options/`, plus the connection string and every other configuration key `Program.cs` reads. Same environment variable names as .NET.
3. `app/db.py`: async engine and a per-request session dependency. Convert the .NET-style connection string (`Host=…;Database=…;Username=…;Password=…`) to an asyncpg URL in one small, tested function.
4. `app/errors.py`: a problem-details helper producing exactly the body the C# `Problem(...)` helpers produce.
5. `app/main.py`: port the middleware pipeline of `Program.cs` in the same order — CORS policy, the `x-api-key` check (same exempt paths), rate limiting (same limits and partitions), authentication wiring as a placeholder that P2 fills in — and the health endpoints. Then create one empty router module for every endpoint file under `api/Endpoints/**` and for each URL-prefix group of inline routes in `Program.cs`, each exporting an `APIRouter` with no routes, and register all of them in `main.py` now, in the order `Program.cs` maps them. Later phases run in parallel on separate branches and only fill in these modules; they must never need to edit `main.py`. For the same reason, create `PORT-MAP.md` with one section per phase, so parallel phases edit different sections.
6. `Dockerfile` for the Python API, and a new file `docker-compose.python.yml` at the repo root: an override that adds a service `api-python` on host port 8081, on the same network and database as the existing `api` service. Do not edit the existing compose files.
7. A scratch database for write tests: document in `api-python/README.md` the exact commands that create a database `studytracker_py` in the local Postgres container and apply the EF migrations to it by running the existing .NET image with `--migrate` and an overridden connection string. Add a pytest fixture that connects to it and rolls back after every test.
8. `tools/parity.py`: given a list of `METHOD path [json body]` lines, call the .NET API and the Python API with the same headers, and print a unified diff of status code and normalised JSON for each. Options to ignore named volatile fields (timestamps, trace ids).
9. `PORT-MAP.md`: list **every** `.cs` file under `api/` except `bin/`, `obj/` and `Migrations/`, with the phase it belongs to (use the phase list in this file) and status `todo`. Add a second table listing every route in the .NET API (method, path, C# handler, auth requirement), taken from `Program.cs` and `api/Endpoints/**`.
10. `README.md`: how to run locally, how to run tests, how to run a parity check.

Done when the health endpoints pass a parity check and PORT-RULES' definition of done is met.

=====

## P1 — Entities

Read `info/muse-prompts/python-port/PORT-RULES.md` and `api-python/PORT-MAP.md`. Then read `api/Data/StudyTrackerContext.cs` in full and every file in `api/Models/` and `api/Models/Localization/` that defines an entity.

Port every entity to `api-python/app/models/`, one module per C# file.

- Table names, column names, types, lengths, nullability, defaults, primary keys, foreign keys, unique constraints and indexes must match the database. Where an attribute on the class and the Fluent configuration in `StudyTrackerContext.cs` disagree, Fluent wins, as it does in EF.
- Port navigation properties as `relationship(...)` with the same names in snake_case. Use `lazy="raise"` so that every query has to state what it loads, mirroring explicit `Include` calls.
- Do not port DTO classes in this phase.

Test: write `tests/test_schema_parity.py`, which reflects the scratch database and fails on any table, column, type, nullability, key or index that differs from the SQLAlchemy metadata, in either direction. This test is the proof for this phase; it must pass with zero differences and zero ignored tables (other than `__EFMigrationsHistory`).

=====

## P2 — Authentication, sessions, users

Read `info/muse-prompts/python-port/PORT-RULES.md` and `api-python/PORT-MAP.md`. Then read every file in `api/Services/Auth/` and `api/Services/Email/`, `api/Endpoints/AuthEndpoints.cs`, `api/Endpoints/MeEndpoints.cs`, `api/Endpoints/AdminEndpoints.cs`, `api/Models/AuthDtos.cs`, the authentication and authorisation sections of `api/Program.cs`, and `tests/StudyTracker.Api.Tests/AuthAndUserManagementTests.cs`, `SessionAndLearnerStateTests.cs`, `TotpServiceTests.cs`, `TotpSecretProtectorTests.cs`. Ignore `*.orig` files.

Port those services and the three endpoint files, and replace the P0 authentication placeholder with the real thing.

Interchangeability is the point of this phase. Prove each of these with a test that uses a value produced by the .NET code (take fixed vectors from the C# tests, or generate them once with the running .NET API and store them as test fixtures):

- a PBKDF2 password hash written by .NET verifies in Python, and one written by Python has the identical format and parameters
- a JWT issued by .NET is accepted by Python and the reverse (same algorithm, issuer, audience, claims, lifetime)
- a TOTP secret encrypted by `TotpSecretProtector` decrypts in Python and the reverse; a TOTP code computed by Python matches .NET for the same secret and time
- a session row created by .NET is honoured by Python (same token hashing, expiry and revocation rules)

Port the cookie names, cookie flags, lockout and rate-limit behaviour, and every status code exactly. Email sending is ported but must be covered only by tests that use a fake SMTP transport.

Also translate the C# test cases in the four test files above into pytest, keeping the same test names in snake_case.

=====

## P3 — Curriculum, progress, atlas, MCQs

Read `info/muse-prompts/python-port/PORT-RULES.md` and `api-python/PORT-MAP.md`. Then read `api/Program.cs` (every inline route not yet ported), `api/Endpoints/V2Endpoints.cs`, `api/Models/DTOs.cs`, and these services: `ProgressService`, `LearnerProgressService`, `LearningPathQueryService`, `AtlasQueryService`, `ReadingMapService`, `McqService`. Read `tests/StudyTracker.Api.Tests/ProgressSynchronizationTests.cs` and `LifecycleAndProblemDetailsTests.cs`.

Port those services, the DTOs they use, the inline routes from `Program.cs` (into routers grouped by URL prefix, each handler carrying a comment with its line number in `Program.cs`) and `V2Endpoints.cs`.

Pay attention to query shape: where the C# uses `Include`/`ThenInclude`, `AsNoTracking`, projection, ordering or grouping, write the equivalent explicit SQLAlchemy query and keep the same ordering, because ordering differences will show up as parity failures. Do not port by loading everything and filtering in Python unless the C# does that.

Translate the two C# test files into pytest. Run a parity check on every GET route in this phase against the seeded local database, and on write routes against the scratch database.

=====

## P4 — Exercise runner

Read `info/muse-prompts/python-port/PORT-RULES.md` and `api-python/PORT-MAP.md`. Then read every file in `api/Services/Exercises/`, `api/Endpoints/ExerciseEndpoints.cs`, `api/Models/ExerciseDtos.cs`, `ExerciseMetadataDtos.cs`, `UserExerciseState.cs`, `api/Options/ExerciseExecutionOptions.cs`, the folder `tests/StudyTracker.Api.Tests/Exercises/`, and two exercise folders under `exercises/` (one Java, one Python) to see the manifest format. Read `runner/` to see the runner images.

Port the whole exercise subsystem: manifest loading and validation, metadata, submission validation, workspace building, the Docker runner (same image names, same resource limits, same timeouts, same network and filesystem restrictions, same command line), Surefire and pytest result parsing, classification of outcomes, drafts, attempts and progress.

The runner executes untrusted learner code. Port every isolation flag exactly as the C# passes it; do not relax or "simplify" any of them, and list each flag in a comment block at the top of the runner module with the C# line it came from.

Translate the C# exercise tests into pytest. Tests that need Docker are marked so they can be skipped where Docker is unavailable; the parsers and validators must be fully tested without Docker.

=====

## P5 — Chat, LLM client, budget guard, import

Read `info/muse-prompts/python-port/PORT-RULES.md` and `api-python/PORT-MAP.md`. Then read `api/Endpoints/ChatEndpoints.cs`, `api/Endpoints/ImportEndpoints.cs`, `api/Services/LlamaApiClient.cs`, `BudgetGuardService.cs`, `CurriculumImportService.cs`, `api/Models/ChatConversation.cs`, `ChatMessage.cs`, `ChatDtos.cs`, `api/Options/LlamaApiOptions.cs`, `BudgetOptions.cs`, and `tests/StudyTracker.Api.Tests/CurriculumImportTests.cs`. Ignore `*.orig` files.

Port them. For the LLM client: same request payload, same headers, same timeout and retry behaviour, same non-production mock behaviour when no key is configured, and the same streaming behaviour if the C# streams. Copy prompt strings verbatim; do not rewrite or improve them. Tests must use a fake HTTP transport and make no real network call.

Translate the import tests into pytest.

=====

## P6 — Localization Lab

Run only after the localization fixes L1–L3 are merged.

Read `info/muse-prompts/python-port/PORT-RULES.md` and `api-python/PORT-MAP.md`. Then read every file in `api/Services/Localization/`, `api/Endpoints/Localization/`, `api/Options/GoogleTranslateOptions.cs`, and `tests/StudyTracker.Api.Tests/Localization/`.

Also read the original design documents in `info/localization-design/specs/`: `localization-lab-BUILD-PROMPT.md`, `localization-lab-marketplace-flow.md`, `localization-lab-workflow-snapshots-flow.md`, `localization-lab-ai-vertical-flow.md` and `localization-lab-ARCHITECTURE-AND-WORKFLOW.md`.

Port all of it, including the job-lifecycle guards and the exception-to-status-code mapping. The C# is what you translate; the documents are what you check it against. Where the C# and the documents disagree, port the C# behaviour and add a row to "Findings" in `PORT-MAP.md` quoting the document section. Do not "fix" the Python to match the documents.

`MtOptimizeService`, `QpsScoringService` and `AutoRoutingService`: port exactly what the C# does at the time you run this phase. If they still throw `NotImplementedException`, port them as stubs that raise `NotImplementedError` with the same messages, mapped to HTTP 501, and implement nothing. If they have been replaced by an HTTP client that calls the `localization-ai` service (step LA4), port that client. In neither case write prompt text, scoring or routing logic in `api-python/`; that logic lives only in `localization-ai/`.

`GoogleTranslateProviderService`: same request, same non-production `[MOCK-XX]` behaviour, same production failure behaviour. Tests use a fake HTTP transport.

Translate the C# localization tests into pytest and run a parity check on all four endpoint groups.

=====

## P7 — Seeders, CLI modes, reconciliation

Read `info/muse-prompts/python-port/PORT-RULES.md` and `api-python/PORT-MAP.md`. Then read `api/Data/DbSeeder.cs`, every `api/Data/*SeedData.cs`, every file in `api/Services/Reconciliation/`, the CLI section of `api/Program.cs` (`--migrate`, `--seed-reference-data`, `--seed-admin`, `--reconcile-content`), `scripts/reconcile-content.sh`, and `tests/StudyTracker.Api.Tests/BackfillReconciliationTests.cs`, `JavaReconciliationTests.cs`, `BridgeSchemaConstraintTests.cs`.

1. **Seeder logic** (ordering, idempotency guards, the write-once rule for lesson content, backfill, status changes): port by hand into `app/seed/`, one module per C# file.
2. **Seed content** — the large literal data inside `FdeCurriculumSeedData.cs` (about 9,500 lines), `JavaVerticalSeedData.cs` (about 3,300 lines) and the other seed files: do **not** retype it. Write a one-off converter, `api-python/tools/extract_seed_data.py`, that parses the C# initialisers and writes the data to JSON files under `app/seed/data/`. The Python seeders load those JSON files. Keep the converter in the repo so the extraction can be repeated. Markdown and JSON content under `api/Data/Content/` and `api/Data/mcq-migration-data.json` are read from their existing locations, not copied.
3. **CLI** in `app/cli.py`: `--seed-reference-data`, `--seed-admin`, `--reconcile-content` with the same flags and exit codes. `--migrate` does not migrate; it checks that the database schema matches the models (reuse the P1 parity check) and exits non-zero if it does not.
4. **Reconciliation engine and reconcilers**: port, and translate the three C# test files into pytest.

Proof for this phase, on two empty scratch databases with the EF migrations applied: seed one with the .NET seeder and the other with the Python seeder, dump both with the same deterministic ordering, and diff. The only allowed differences are generated timestamps; list them. Then run each seeder a second time on its own database and show that nothing changes.

=====

## P8 — Full parity sweep and reading guide

Read `info/muse-prompts/python-port/PORT-RULES.md` and `api-python/PORT-MAP.md`.

1. Every row in both tables of `PORT-MAP.md` must be `done` or carry a written reason. Port anything still `todo`.
2. Write `api-python/tools/parity_routes.txt` covering every route in the route table, and run the full parity check. Fix every difference that is a port error; list every difference that is a genuine Finding.
3. Point the React app at the Python API locally (document the one environment variable or proxy setting that does it; do not commit a change to `app/`) and click through: sign in, open a lesson, answer an MCQ, run one Java and one Python exercise, open the Localization Lab. Report what worked and what did not.
4. Write `api-python/README.md` as a reading guide for a C# developer learning Python: a suggested reading order through the code base (start to finish for one request: router → service → model → schema), and a table of "C# construct → what the port uses instead" with one real file-and-line example from this port for each (dependency injection, `IOptions`, async/await, LINQ queries, `Include`, records and DTOs, exceptions to problem-details, middleware, hosted CLI modes).
5. Final report: totals from `PORT-MAP.md`, the parity result, and the complete Findings list.
