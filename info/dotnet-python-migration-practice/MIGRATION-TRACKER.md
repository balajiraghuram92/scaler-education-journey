# .NET → Python API Migration Practice Tracker

**Purpose:** Manually re-create the Python API implementation while using the existing migration as a read-only reference. For each slice, first understand the corresponding .NET behavior and how the Python version replaces it, then type the Python implementation by hand, ask questions, and continue.

**Working target:** Wednesday, 2026-11-25, based on the discussed 15-hour days. This is a target, not a guarantee; reserve time for failures found by the reused tests and parity checks.

## Scope

### Included

- Port the backend under `api/` to the Python API under `api-python/`.
- Preserve API contracts and relevant .NET behavior, including auth, persistence, seed/reconciliation behavior, and the Localization Lab API integration.
- Manually type the Python implementation from the reference branch after discussing each related .NET slice.
- Reuse the Python branch's tests rather than manually authoring a duplicate test suite. Run those tests against the practice implementation.

### Excluded from this tracker

- Merging `origin/muse/tracks-la-p-g` or replacing manual work with its implementation.
- The standalone `localization-ai/` and `issue-intel/` services.
- The AWS Agentic AI Bootcamp content and the separate Agentic AI implementation project.
- Frontend redesign or production deployment.

The reference branch contains work from multiple tracks. Only its `api-python/` implementation, migration map, progress notes, and matching tests are in scope here.

## Reference material

- .NET source: `api/` (especially `api/Program.cs`, `api/Endpoints/`, `api/Services/`, `api/Models/`, `api/Data/`, and `api/Options/`).
- Python implementation and reusable tests: `origin/muse/tracks-la-p-g:api-python/`.
- File/route mapping: `api-python/PORT-MAP.md` on the reference branch.
- Implementation history and recorded verification gaps: `api-python/PROGRESS.md` on the reference branch.
- Python setup and commands: `api-python/README.md` on the reference branch.

**Important:** The reference branch's map marks many files as ported but unverified. Its progress notes say the final full route-parity sweep was not run. Reference code being present does not mean the hand-typed practice version is complete or verified.

## How we will work each slice

1. Pick a small, coherent part of the .NET API and identify its callers, data, and contract.
2. Explain what the .NET code does and which framework behavior it relies on.
3. Walk through the matching Python file or files and explain the replacement choices.
4. You type the Python code by hand into the practice target; do not merge the reference branch.
5. Answer questions and compare the result with the reference implementation.
6. Bring over/run the relevant existing test from the reference branch and record the result.
7. Mark the slice done only after its code is present and its relevant check passes (or record a clear exception).

At the start, choose a practice branch or isolated target so the reference stays unchanged and the existing `api-python/` baseline is not accidentally overwritten. Record that target below before the first code change.

**Practice target:** _To be selected before implementation._

## Status key

- ⬜ Not started
- 🟨 In progress
- ✅ Complete and checked
- ⚠️ Blocked or has a recorded exception

Update this tracker after each work session. For each completed phase, record the commit or files changed, the checks run, their result, and any migration insight worth keeping.

## Phase tracker

### Phase 0 — Baseline and safe practice setup

**Status: ⬜ Not started**

- [ ] Confirm the practice branch/target and record its starting commit.
- [ ] Keep `origin/muse/tracks-la-p-g` as the read-only Python reference; do not merge it.
- [ ] Read the Python README, PORT-MAP, and PROGRESS notes for setup, ordering, and known findings.
- [ ] Confirm local database/test setup uses a scratch database; the Python CLI's `--migrate` is a schema check, not a schema migration.
- [ ] Capture baseline status and identify any files already present in the practice target.

**Exit check:** A clean, separate practice target is ready; source and reference paths are recorded.

### Phase 1 — Application shell and shared infrastructure

**Status: ⬜ Not started**

Main mapping: `api/Program.cs` and `api/Options/*.cs` → `api-python/app/main.py`, `settings.py`, `db.py`, `errors.py`, `rate_limit.py`, and health/root routers.

- [ ] Application construction and router registration order
- [ ] Settings/environment-variable aliases
- [ ] Database engine, session lifecycle, and dependency wiring
- [ ] Middleware order, request IDs, API-key checks, and error/problem response shape
- [ ] Health and root routes
- [ ] Reuse and run the matching startup/health checks

**Exit check:** Python app starts locally, health endpoints respond, and shared error/config behavior is understood.

### Phase 2 — Data models, database mapping, and shared schemas

**Status: ⬜ Not started**

Main mapping: `api/Data/StudyTrackerContext.cs`, `api/Models/`, and shared DTO definitions → `api-python/app/models/` and `api-python/app/schemas/`.

- [ ] Base model, naming/types, timestamps, JSONB behavior, indexes, constraints, and relationships
- [ ] Core user, session, course, lesson, exercise, progress, and knowledge models
- [ ] Localization models used by the .NET API
- [ ] Shared DTO/Pydantic base behavior and .NET-compatible JSON formatting
- [ ] Reuse and run the schema/model parity checks against the scratch database
- [ ] Review documented model-versus-migration differences; record rather than silently changing behavior

**Exit check:** Models import cleanly and schema checks pass, with known database exceptions documented.

### Phase 3 — Authentication, sessions, email, and user administration

**Status: ⬜ Not started**

Main mapping: `api/Endpoints/AuthEndpoints.cs`, `MeEndpoints.cs`, `AdminEndpoints.cs`, `api/Services/Auth/`, and `api/Services/Email/` → Python auth/email services, routers, and schemas.

- [ ] Password hashing and .NET-compatible credential behavior
- [ ] JWT claims, cookies, refresh, current-user lookup, and authorization policies
- [ ] TOTP enrollment/verification and secret protection
- [ ] Session creation, listing, revocation, expiry, and logout flows
- [ ] Email notifications and background-task behavior
- [ ] Admin approval/rejection and user-management routes
- [ ] Reuse and run auth, TOTP, session, email, and user tests

**Exit check:** Auth flows and role checks match the intended API behavior; tests pass or exceptions are recorded.

### Phase 4 — Core learning API and learner state

**Status: ⬜ Not started**

Main mapping: inline routes in `api/Program.cs`, `api/Endpoints/V2Endpoints.cs`, `api/Services/ProgressService.cs`, `LearnerProgressService.cs`, `LearningPathQueryService.cs`, `AtlasQueryService.cs`, `ReadingMapService.cs`, and `McqService.cs` → Python routers/services/schemas.

- [ ] Verticals, courses, modules, lessons, chapters, and curriculum queries
- [ ] Learner summaries, resume state, lesson/problem progress, and activity
- [ ] Reading map and knowledge atlas queries/updates
- [ ] V2 learning paths, chapters, and progress routes
- [ ] MCQ presentation, attempts, retry, and performance
- [ ] Preserve route methods, auth requirements, status codes, response fields, and ordering
- [ ] Reuse and run matching route/service tests

**Exit check:** Core read/write flows and authenticated progress behavior pass their automated checks.

### Phase 5 — Exercise execution and submissions

**Status: ⬜ Not started**

Main mapping: `api/Endpoints/ExerciseEndpoints.cs` and `api/Services/Exercises/` → Python exercise routers/services.

- [ ] Exercise repository and manifest parsing
- [ ] Metadata, starter/solution access, and workspace construction
- [ ] Submission validation, runner interface, Docker runner, and result parsing
- [ ] Execution classification, timeouts, concurrency limits, and saved progress
- [ ] Reuse and run non-Docker tests; run Docker-specific checks if the local runner is available

**Exit check:** Exercise endpoints and execution paths behave as expected; any environment-only Docker gap is recorded.

### Phase 6 — Chat, LLM client, budgets, and curriculum import

**Status: ⬜ Not started**

Main mapping: `api/Endpoints/ChatEndpoints.cs`, `ImportEndpoints.cs`, `api/Services/LlamaApiClient.cs`, `BudgetGuardService.cs`, and `CurriculumImportService.cs` → Python routers/services.

- [ ] Chat request/response handling, auth, and usage accounting
- [ ] LLM HTTP client, errors, timeout behavior, and mockable transport
- [ ] Budget/usage guard and admin usage routes
- [ ] Curriculum import validation and slug/normalization behavior
- [ ] Reuse and run LLM, budget, import, and endpoint tests

**Exit check:** Mock-backed chat and import flows pass; external credentials are not required for basic checks.

### Phase 7 — Seeders, CLI, and reconciliation

**Status: ⬜ Not started**

Main mapping: `api/Services/Reconciliation/`, seed code under `api/Data/`, and API hosted CLI modes → `api-python/app/seed/`, `app/services/reconciliation/`, `app/cli.py`, and extraction tools.

- [ ] Schema check and reference-data seeders
- [ ] Curriculum, localization, MCQ, and vertical seed data
- [ ] Content reconciliation models, normalizers, and per-curriculum reconcilers
- [ ] CLI flags, exit codes, dry-run/apply/verify behavior
- [ ] Seed-data extraction/check tool
- [ ] Reuse and run seeder/reconciliation tests against scratch data only
- [ ] Review known constraint/table mismatches from the reference notes

**Exit check:** CLI help/schema checks work; seed/reconcile checks are repeatable and do not touch production data.

### Phase 8 — Localization Lab API integration

**Status: ⬜ Not started**

Main mapping: `api/Endpoints/Localization/`, `api/Services/Localization/`, localization models, and options → Python localization routers/services. The standalone `localization-ai/` service itself is out of scope.

- [ ] Project/string/translation operations and workflow steps
- [ ] Marketplace jobs, bids, vendor portal, and owner routes
- [ ] Snapshot and provider-health routes
- [ ] Translation provider/client HTTP boundaries and failure mapping
- [ ] Usage ledger, caps, and transaction/commit behavior
- [ ] Reuse and run localization API tests

**Exit check:** Localization API endpoints and integrations pass local tests; standalone AI-service behavior remains behind its existing HTTP contract.

### Phase 9 — Reused tests, route parity, and final review

**Status: ⬜ Not started**

- [ ] Reuse relevant test modules from `origin/muse/tracks-la-p-g:api-python/tests/`; do not hand-author a duplicate suite
- [ ] Run focused tests after each phase, then the full non-Docker test suite
- [ ] Run Ruff checks/format and mypy if available in the chosen environment
- [ ] Start .NET and Python APIs against identically seeded local data and run the parity route list
- [ ] Cover anonymous/API-key and signed-in flows, including auth/session state changes
- [ ] Resolve or document parity differences; review all reference PORT-MAP findings
- [ ] Confirm health, error responses, response JSON/date/decimal formatting, and route auth
- [ ] Record final commands, results, remaining gaps, and a short learning summary

**Exit check:** Reused tests pass; route parity has a recorded result; all exceptions have an owner/reason. Do not mark complete just because the reference branch contains the code.

## Session log

| Date | Phase/slice | .NET files discussed | Python files hand-typed | Checks run/result | Questions or migration notes |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Known reference limitations to revisit

- The reference `PROGRESS.md` records the final full 102-route parity sweep as **not run**.
- Earlier parity notes record remaining mismatches in signed-in steps; rerun after the hand-typed implementation is assembled.
- The reference notes identify database models/seeders that are ahead of the committed .NET migrations or constrained by existing database checks. Treat these as explicit findings to investigate, not as permission to change schema or production data during this practice.
- The Python API's migration command checks schema; EF migrations remain the schema owner.

## Completion definition

The migration practice is complete when the in-scope Python API has been hand-typed into the chosen practice target, the branch-provided tests have been reused and run, the full parity result is recorded, and every remaining difference is documented. Production deployment and the standalone Agentic AI projects are not completion criteria for this tracker.
