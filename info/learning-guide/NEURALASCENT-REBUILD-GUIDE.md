# Neuralascent: the hands-on rebuild guide

A study guide for rebuilding every part of Neuralascent by hand, one step at a time, with a smaller AI model (Microsoft Copilot, Gemini Flash or similar) as your tutor.

Written 12 November 2026, from the state of branch `muse/tracks-la-p-g` (commit `9e10e41`).

---

## Part 0 — How to use this guide

### 0.1 For you (the learner)

1. Start a fresh chat with the tutor model.
2. Paste **section 0.2 (the tutor brief)** first, exactly as written.
3. Then paste **Part 1** (the big picture) so the tutor knows the whole system.
4. Then paste one step at a time from Parts 2 to 6, for example "Track P, step P2". Do not paste the whole guide at once: smaller models lose track of long inputs.
5. When the tutor asks for a file from the repository, paste that file (or the part it names). The tutor cannot see your disk.
6. Mark a step done only when its **Done when** checks pass on your machine.

What stays true the whole time:

- **The .NET API is live and is the source of truth.** You do not change it while learning. It is the answer to "what should this do?".
- **The existing Python code is your answer key.** `api-python/`, `localization-ai/` and `issue-intel/` are already built and verified. You write your own version, and compare with these only when you are stuck or finished.
- **You write all the Python yourself.** The tutor explains, hints and reviews. It never writes Python for you.
- **You decide when to move to Python.** Part 7 is the checklist for that day.

Suggested folder for your own work: a new folder next to the reference, for example `my-api-python/`, `my-localization-ai/`, `my-issue-intel/`. Keep the reference folders untouched so you can always compare.

### 0.2 The tutor brief (paste this first, every new chat)

```
You are my coding tutor. I am an experienced backend developer (7+ years, Java/Spring and
C#/.NET) rebuilding a working system by hand to learn it. I will paste one step at a time.

The system already exists and works. Its .NET code is the source of truth for behaviour.
A finished Python version exists as an answer key; I will paste parts of it when needed.

Rules you must follow:

1. Never write Python code for me. Not a full file, not a function, not a "small example",
   not pseudocode that is really Python. For Python you may only: explain concepts, name the
   library feature to use, describe the steps in plain English, and review code I paste.
   When reviewing, point at the line and say what is wrong and why; let me fix it.
2. For C#, SQL, React/JavaScript, YAML and shell commands you may show code, but only after
   I ask for it ("show me").
3. Hints come in levels. Start at level 1 and go up only when I ask for "next hint":
   - Level 1: what the piece is for and which concept it uses.
   - Level 2: which file in the reference to read, and what to look for in it.
   - Level 3: the exact steps in plain English, in order, with the names of the library
     features involved.
   - Level 4 (only for non-Python, only when I say "show me"): the code.
4. One step at a time. At the start of a step, restate its goal in two sentences, list what
   I should read first, and ask me to try. Do not move on until I say the "Done when" checks
   pass.
5. Never invent facts about this system. If you need a file, a route, a column name or a
   number, ask me to paste it. If the guide and a pasted file disagree, the file wins.
6. When I paste an error, ask for the full error and the code around it before guessing.
   Give the most likely cause first, then how to confirm it, then the fix in words.
7. Keep answers short: at most about 15 lines unless I ask for more. Use plain English.
8. Every few steps, ask me one question that checks I understood the "why" of a decision
   (the guide lists the decisions). Do not grade harshly; explain the answer if I miss it.
9. If I ask you to "just do it", remind me of rule 1 for Python; for other languages, follow
   rule 2.
```

### 0.3 Commands you will use often

These are not Python; the tutor may show variations.

```bash
# Local stack of the live site (from the repo root)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# .NET build and tests
dotnet build api
dotnet test tests/StudyTracker.Api.Tests

# React tests and build
cd app && npm ci && npx vitest run && npm run build

# Python checks (run inside a Python project folder)
ruff check . ; ruff format --check . ; mypy app ; pytest
```

Local database: container `studytracker-postgres`, user `studyuser`, database `studytracker`. Run SQL through `psql` (for example `docker exec -i studytracker-postgres psql -U studyuser -d studytracker`), never typed loose into the shell.

---

## Part 1 — The big picture

### 1.1 What Neuralascent is

A personal learning platform for experienced developers (Java/Spring backend and applied AI). It has courses, lessons, MCQs, live code exercises that run in containers, a knowledge atlas, a reading map, a learning chatbot, and lab projects. One lab project is the **Localization Lab**, a working model of a translation service with clients, vendor teams and an operations side.

### 1.2 The systems

| System | Folder | Language | Role | Status |
|---|---|---|---|---|
| Web app | `app/` | React 19, Vite, React Router 7 | Everything the user sees | Live |
| API | `api/` | C#, ASP.NET Core 8 minimal API, EF Core 8 | All business logic and data | **Live, source of truth** |
| Database | Docker `pgvector/pgvector:pg16` | PostgreSQL 16 + pgvector | All data; schema owned by EF Core migrations | Live |
| Exercise runners | `runner/` | Docker images (Java, Java-Spring, Python) | Run learners' code in throwaway containers | Live |
| AI agent | `ai-agent/` | Python, FastAPI | Separate agent service on the site | Live (not covered here) |
| API port | `api-python/` | Python, FastAPI, async SQLAlchemy | Full copy of the API, for learning; same database, same JSON | Reference, verified |
| Localization AI | `localization-ai/` | Python, FastAPI | MT Optimize, quality scoring, Auto-Route, eval harness; called by the .NET API | Reference, verified on fake models |
| Issue intelligence | `issue-intel/` | Python, FastAPI, Alembic, MCP | Agentic bug-fix system on invented data ("Tessera Engines") | Reference, verified on fake models |

### 1.3 How a request flows (live site)

```
Browser (React)
  │  HTTPS, cookie "na_auth" (JWT); nginx (app/nginx.conf) proxies /api to the API
  ▼
ASP.NET Core API (api/Program.cs)
  middleware: correlation id + problem details → CORS → rate limiter → authentication
              → authorization → API-key check   (api/Program.cs, from about line 476)
  ▼
Endpoint (Program.cs inline routes or api/Endpoints/*.cs)
  ▼
Service (api/Services/**)  ──►  other services: exercise runner (Docker), Llama chat API,
  ▼                              localization-ai (HTTP, shared secret), Azure Translator
EF Core DbContext (api/Data/StudyTrackerContext.cs)
  ▼
PostgreSQL
```

### 1.4 Tech-stack decisions and why

| Decision | Why |
|---|---|
| ASP.NET Core **minimal API**, not MVC controllers | Less ceremony; route groups per area (`MapGroup`), handlers are plain methods. |
| **EF Core owns the schema** (migrations in `api/Migrations/`) | One owner for the schema. The Python services map the same tables and never create or alter them (issue-intel is the exception: it has its own database and uses Alembic). |
| snake_case table and column names | PostgreSQL convention; C# properties stay PascalCase and are mapped with `[Column]` attributes or Fluent config. |
| **PostgreSQL + pgvector** | One database for relational data and embeddings (semantic cache, search). No separate vector store. |
| JWT in an **HTTP-only cookie**, plus an **`x-api-key` middleware** | The cookie carries the user session. The API-key check applies to every route except `/health` and `/swagger`; when no key is configured it lets requests through outside production and refuses them in production. Scripts and the parity tool send the header. How browser traffic satisfies it on your host is an exercise in C2. |
| **TOTP second factor** and admin approval of new users | Personal site with paid model calls behind it: only approved people get in. |
| PBKDF2-SHA256 with 210,000 iterations | Standard, built into .NET, no extra package; the Python port reproduces it byte for byte. |
| Content as JSON files + seed classes, **write-once seeding** | Content lives in Git; the seeder never overwrites a finished lesson by accident. |
| Exercises run in **Docker containers** started by the API | Untrusted learner code never runs inside the API process. |
| Python AI services are **separate HTTP services** | AI code moves fast and has its own dependencies; the .NET API calls them with a shared secret and keeps the business rules. |
| **No agent frameworks** (no LangChain) in the Python AI services | Every step is a plain function you can read, test and trace. |
| **Fake model providers** in every test | Tests are free, fast and deterministic. Fake results prove the wiring, not the quality. |
| Images on **GHCR**, deployed to **one EC2 host** with Docker Compose | Simple and cheap for a personal site. |

### 1.5 Repository map (the parts you will touch)

```
api/Program.cs                     startup, middleware, CLI modes, many inline routes
api/Endpoints/                     route groups: Auth, Me, Admin, Chat, Exercise, Import, V2, Localization/*
api/Services/                      business logic (Auth/, Exercises/, Localization/, Email/, ...)
api/Models/                        EF entities and DTO records
api/Data/StudyTrackerContext.cs    DbContext, Fluent mapping, indexes
api/Data/*SeedData.cs, Content/    seed data and content JSON
api/Migrations/                    EF migrations + model snapshot
tests/StudyTracker.Api.Tests/      xUnit tests
app/src/                           React: pages/, components/, api/client.js, App.jsx
api-python/                        Python port (reference)
localization-ai/                   Localization AI service (reference)
issue-intel/                       Issue intelligence system (reference)
info/muse-prompts/                 the build specs each Python project was built from
.github/workflows/deploy-api.yml   build and deploy
deploy/single-ec2-automation.md    how the EC2 host is set up
```

The build specs in `info/muse-prompts/` are the most useful reading after this guide:
`python-port/PORT-RULES.md` and `P0-to-P8-prompts.md`, `localization-ai/LA1-to-LA4-prompts.md`, `localization-rebuild/CONTRACT.md` and `R1`–`R8`, `issue-intel/BUILD-SPEC.md` and `G0-to-G4-prompts.md`.

---

## Part 2 — Track C: understand the live site (.NET + React)

You do not rebuild the live site. You learn it well enough to explain every piece, because every Python step later copies it. Each step: read, answer the questions, run the check.

### C1 — Run it locally

- **Goal:** the full stack runs on your machine and you can log in.
- **Read:** `docker-compose.yml`, `docker-compose.dev.yml`, `docker instructions.md`.
- **Do:** start the stack (section 0.3). Run the migrations and the seed: `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --seed-reference-data`. Create an admin with the `--seed-admin` mode (see `api/Program.cs`, search for `--seed-admin`).
- **Done when:** `GET http://localhost:5000/health/live` returns 200, and the React app shows the course list.
- **Questions:** Why does restarting the API not seed? (Answer: seeding is a separate CLI mode, not part of startup.)

### C2 — The startup pipeline

- **Goal:** explain `api/Program.cs` from top to bottom.
- **Read:** `api/Program.cs`. Find: options binding, DbContext registration, authentication (search `AddJwtBearer`), CORS, rate limiter (`AddRateLimiter`), the CLI modes (`--migrate`, `--seed-reference-data`, `--seed-admin`, `--reconcile-content`), the API-key middleware (search `x-api-key`), health checks, and the `Map...Endpoints()` calls at the end.
- **Done when:** you can draw the middleware order from memory and say what each one rejects.
- **Decision to explain:** the JWT is read from a cookie when there is no `Authorization` header (search `cookieName`). Why a cookie for a browser app?
- **Find out:** the React client (`app/src/api/client.js`) does not add an `x-api-key` header, and `app/nginx.conf` only passes through whatever header the caller sent. So how does browser traffic pass the API-key middleware in your deployment? Check the API's `API_KEY` setting on your host and the middleware's rules. Write the answer down; it matters on switch-over day.

### C3 — Data and migrations

- **Goal:** know how entities, mapping and migrations fit together.
- **Read:** one entity (`api/Models/Lesson.cs`), its mapping in `StudyTrackerContext.cs`, one migration in `api/Migrations/` and `StudyTrackerContextModelSnapshot.cs`.
- **Do:** run `dotnet ef migrations add Probe` in a throwaway copy and confirm the generated migration is empty, then delete it. An empty migration proves the model and the snapshot agree.
- **Done when:** you can say what the snapshot is for and why a hand-written migration also needs its `.Designer.cs` (it carries the `[Migration]` attribute EF uses to find it).
- **Trap (happened in this project):** every foreign key needs an index whose first column is that key. EF adds one automatically unless one exists; if you write the migration by hand and forget it, the model check fails.

### C4 — Authentication and users

- **Goal:** trace sign-up to a signed-in request.
- **Read:** `api/Endpoints/AuthEndpoints.cs`, `api/Services/Auth/*` (`Pbkdf2PasswordHasher`, `JwtTokenService`, `TotpService`, `TotpSecretProtector`, `SessionService`), `api/Models/AppUser.cs`, `api/Endpoints/AdminEndpoints.cs`, `AdminAuthorization.cs`.
- **The flow:** sign up → user `Status = "PendingApproval"` → an admin approves → log in with password → server returns an MFA challenge → first time: enrol TOTP (secret shown as `manualEntryCode`), confirm with a 6-digit code → the server sets the `na_auth` cookie (JWT, default 720 minutes) → later requests carry the cookie.
- **Done when:** you can sign up, approve yourself with SQL, enrol an authenticator app and call `GET /api/me/summary`.
- **Decisions to explain:** why the TOTP secret is stored encrypted (`TotpSecretProtector`); why `LastAcceptedTotpCounter` exists (it stops reuse of the same code).

### C5 — Content and seeding

- **Goal:** know where lessons come from.
- **Read:** `api/Data/DbSeeder.cs`, `api/Data/Content/` (one `course.json`), one `*SeedData.cs`, the "Write-once seeding gotcha" in `CLAUDE.md`.
- **Done when:** you can explain why a lesson whose body has the three marker headings is never overwritten, and list the steps to force a reseed.

### C6 — Live code exercises

- **Goal:** follow a "Run" click to a test result.
- **Read:** `api/Endpoints/ExerciseEndpoints.cs`, `api/Services/Exercises/` (`ExerciseService`, `ExerciseWorkspaceBuilder`, `LocalDockerExerciseRunner`, `SurefireResultParser`, `ExerciseExecutionClassifier`), `runner/`, one exercise under `exercises/`.
- **Done when:** you can say how the API starts a container (Docker socket mounted into the API container), how it limits time and resources, and how test output becomes a pass/fail result.

### C7 — Chat and the budget guard

- **Read:** `api/Endpoints/ChatEndpoints.cs`, `api/Services/LlamaApiClient.cs`, `api/Services/BudgetGuardService.cs`.
- **Done when:** you can explain the daily cap (default USD 2.00 and 500 requests) and what happens with no API key outside production (a mock reply).

### C8 — The React app

- **Read:** `app/src/App.jsx` (routes, `ProtectedRoute`), `app/src/api/client.js` (one place that sends cookies with `credentials: 'include'` and turns error bodies into `ApiError` with `problemDetails`), one page such as `app/src/pages/Localization/LocalizationJobs.jsx`, one test in `app/src/__tests__/`.
- **Done when:** you can add a route to a new empty page and write one Vitest test for it.

### C9 — Build and deploy

- **Read:** `.github/workflows/deploy-api.yml`, `deploy/single-ec2-automation.md`.
- **The flow:** push to `main` → the workflow "Build and Deploy to AWS" builds and tests the API and the app → builds images (API, app, Java runner, Python runner, AI agent) → pushes them to GHCR → the EC2 host pulls them and restarts Compose.
- **Done when:** you can explain where secrets live (not in the repo) and how the host gets the GHCR read token.

---

## Part 3 — Track P: the Python port of the API

This is the main rebuild. You write your own `my-api-python/`. The finished reference is `api-python/`. The rules it was built under are in `info/muse-prompts/python-port/PORT-RULES.md`; read that file before P0. The phase list matches `P0-to-P8-prompts.md`.

### 3.1 The rules of the port (and why)

| Rule | Why |
|---|---|
| One C# file → one Python module, same name in snake_case, same sub-folder | You can open both side by side. `api-python/PORT-MAP.md` lists every pair. |
| Port behaviour, including odd behaviour; record oddities in a "Findings" list | The goal is a faithful copy you can test against the live API. Fixing things silently breaks parity. |
| The schema belongs to EF Core migrations; Python never creates or alters tables | One schema owner. Your tests run against a database migrated by the .NET API. |
| Same routes, status codes, JSON names (camelCase), null handling, date format, error body | So a script can call both APIs and compare JSON. |
| Same environment variable names (`ConnectionStrings__DefaultConnection`, `Jwt__…`, `Auth__…`, `API_KEY`) | Both containers can share one `.env`. |
| Password hashes, JWTs, sessions and TOTP secrets must be interchangeable | A user signed up on one API can log in on the other. This is what makes a real switch-over possible. |
| Money is `Decimal`, never `float` | Same as C# `decimal`. |
| No clever abstractions the C# does not have | Readability over elegance. |

Stack: Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2 (async, asyncpg), Pydantic v2, pydantic-settings, httpx, PyJWT, cryptography, pytest, pytest-asyncio, ruff, mypy.

### 3.2 C# → Python mapping (learn this table first)

| C# | Python equivalent to look up |
|---|---|
| Dependency injection, `AddScoped` | Plain constructor arguments wired per request in the router (FastAPI `Depends` for the session) |
| `IOptions<T>` with `SectionName` | One `pydantic-settings` class per options file, with the same env names as aliases |
| `async Task<T>` | `async def`, `await` |
| LINQ `Where`, `OrderBy`, `FirstOrDefaultAsync` | SQLAlchemy `select()`, `.where()`, `.order_by()`, `scalar_one_or_none()` |
| `Include` / `ThenInclude` | `selectinload` chains; models use `lazy="raise"` so every load is explicit |
| Filtered `Include(x => x.Y.Where(...))` | `selectinload(...).and_(...)` loader criteria |
| `SaveChangesAsync` | services `flush()`; routers `commit()` |
| Records / DTOs | Pydantic models on a shared base that emits camelCase |
| Interfaces | `typing.Protocol` |
| Exceptions → `Problem(...)` | Same exception names → one helper that writes the same problem JSON |
| `decimal.Round(x, 6)` (banker's rounding) | `Decimal.quantize(..., rounding=ROUND_HALF_EVEN)` |
| `DateTime.UtcNow` in JSON (`…Z`, 7 fraction digits) | A custom serializer that writes the .NET format |
| `HttpClient` | `httpx.AsyncClient` |
| CLI flags in `Program.cs` | `argparse` in a `cli` module with the same flags and exit codes |

### 3.3 The phases

Each phase: **Read** (C# first, then the reference only when stuck), **Build** (in words; you write it), **Done when**.

#### P0 — Scaffold, configuration, parity tool

- **Read:** `api/Program.cs` (configuration and middleware), `api/Options/*.cs`, `appsettings.json`.
- **Build:** project layout (`app/main.py`, `settings.py`, `db.py`, `errors.py`, `models/`, `schemas/`, `services/`, `routers/`, `seed/`, `tests/`, `tools/`); settings classes with the .NET env names; an async engine and a session dependency; the health routes; the API-key middleware in the same order as .NET; the problem-details helper; the camelCase base model and the .NET date format.
- **Parity tool:** a small script that reads a list of `METHOD path [json]` lines, calls both APIs with the same API key, normalises volatile fields (timestamps, trace ids), and diffs the JSON. Reference: `api-python/tools/parity.py` and `parity_routes.txt`.
- **Test database:** create `studytracker_py` and migrate it with the .NET image's `--migrate` mode (commands in `api-python/README.md`).
- **Done when:** `/health/live` matches .NET in the parity tool, and lint, types and tests pass.
- **Decision to explain:** why compare against the live API instead of writing expected JSON by hand?

#### P1 — Entities

- **Read:** `api/Models/*.cs`, `api/Data/StudyTrackerContext.cs`.
- **Build:** one SQLAlchemy model per entity, table and column names taken from `[Table]`, `[Column]` and the Fluent config, never guessed. A schema check that compares your models with the real database (reference: `api-python/app/seed/schema_check.py`).
- **Done when:** the schema check reports no differences against a database migrated by .NET.
- **Trap:** Fluent defaults (for example a `HasDefaultValue`) live in `StudyTrackerContext.cs`, not on the entity.

#### P2 — Authentication, sessions, users

- **Read:** Track C4 files.
- **Build:** the PBKDF2 hasher (same format, salt length, iterations), JWT issue and validate (same claims, same signing key setting), the cookie, the MFA challenge and TOTP (same secret protection, same counter rule), sessions, `/api/me`, the admin routes.
- **Done when:** a user created on .NET logs in on Python and the reverse, including TOTP; the signed-in parity steps match.
- **Decision to explain:** why must these be byte-compatible, and what breaks on switch-over day if they are not?

#### P3 — Curriculum, progress, atlas, MCQs

- **Read:** the inline routes in `Program.cs` (verticals, courses, lessons, chapters, problems, knowledge atlas, reading map, tasks), `V2Endpoints.cs`, `ProgressService`, `LearnerProgressService`, `AtlasQueryService`, `LearningPathQueryService`, `ReadingMapService`, `McqService`.
- **Done when:** every read route in this area matches in the parity tool.
- **Trap:** list order. If two rows share a sort value, the order is not defined and the two APIs may differ. The fix in this project was to give three courses distinct `orderIndex` values, not to change the query.

#### P4 — Exercise runner

- **Read:** Track C6 files.
- **Build:** the same workspace builder, the Docker-based runner, the result parsers and the classifier.
- **Done when:** running the same exercise on both APIs gives the same result JSON.

#### P5 — Chat, model client, budget guard, import

- **Read:** Track C7 files, `CurriculumImportService`, `ImportEndpoints.cs`.
- **Done when:** with no model key, both return the same mock reply; the budget guard refuses at the same limits.

#### P6 — Localization Lab

Do Track L (Part 4) first. P6 is the port of what you learn there.

#### P7 — Seeders, CLI modes, reconciliation

- **Read:** `api/Data/DbSeeder.cs`, every `*SeedData.cs`, the `--reconcile-content` mode.
- **Build:** the seeders, reading the same JSON content; the CLI with the same flags and exit codes.
- **Done when:** an empty database seeded by your Python seeder and one seeded by .NET give the same rows (compare with SQL counts and key columns per table; in this project the localization tables matched on 14 of 14 checks).

#### P8 — Full parity sweep

- **Done when:** every route in `parity_routes.txt` matches (the reference reached 108 of 108 with the API key, and 124 of 128 signed-in steps, the 4 differences being random by design: shuffled MCQ options and new ids), and you have a short reading guide in your README.

---

## Part 4 — Track L: the Localization Lab

### 4.1 The business model (owner decisions, 12 Nov 2026)

The first version was a marketplace where vendors bid on jobs and spent credits. It was replaced, because that is not how the real service works. The model now:

| Topic | Rule |
|---|---|
| Vendors | Vendor teams are contracted through a **service agreement** per project. No bidding, no credits. |
| Tiers | Tier = **team capacity**, not quality: Silver 3 linguists, Gold 6, Platinum 10 (placeholder sizes). |
| Privacy | **Aliases both ways.** A client never sees a vendor's real name; a vendor never sees the project's real name or slug. Only operations sees both. |
| Machine help | Azure Translator drafts (Google Translate removed). A model optimizes the draft and scores it 1 to 5. **Scores are for vendors only.** |
| Usage | Every paid provider call is recorded. Each project has a **hard monthly cap** on machine-translation characters and on model tokens. At the cap no new call starts; a call in flight finishes. |
| Kill switch | Operations can switch AI off for a project. |
| Jobs | One job per language goes to the team named in the agreement. A job covers **every string not yet approved, including machine drafts**, which the vendor must edit or accept before submitting. |
| Operations | The existing admin role. |

The full contract (every route, JSON shape and fixed string): `info/muse-prompts/localization-rebuild/CONTRACT.md`. It is the most important file in this track. Read it before L1.

### 4.2 The audiences and their routes

| Audience | Path prefix | Access |
|---|---|---|
| Client | `/api/localization/projects…`, `/jobs…`, `/provider-health…` | API key |
| Vendor team | `/api/localization/vendor…` | API key |
| Operations | `/api/localization/ops…` | signed-in admin (role `Admin`, status `Approved`), else 403 |

### 4.3 Steps (learn the .NET version, then port it in P6)

#### L1 — Projects, strings, workflow (the base)

- **Read:** `api/Models/Localization/*`, `LocalizationProjectService`, `LocalizationStringService`, `WorkflowService` (the stage actions "Mark Translated", "Send to Review", "Approve"), `api/Endpoints/Localization/LocalizationEndpoints.cs`.
- **Understand:** a translation row per string and locale, with `stage`, `translationSource` (`AI`, `Marketplace` = vendor team, `Manual`), `rawMtText`, `qpsScore`, `rawMtQpsScore`, `needsReview`. A workflow is an ordered list of steps; running a step returns an outcome text such as "12 strings affected".

#### L2 — Usage metering (track step R1)

- **Read:** `LocalizationUsageEvent.cs`, `LocalizationProviderRate.cs`, `UsageConstants.cs`, `UsageMeteringService.cs`, `UsageEndpoints.cs`, CONTRACT section 4.1–4.2.
- **Understand:** one usage event per provider call (meter `machine-translation`, `llm-optimize` or `llm-score`; units in and out; cache hit; success). Cost = units × the rate in force at the event time ÷ 1,000,000, rounded once to 6 decimals. A missing rate costs 0 and is listed in `ratesMissing`.
- **Trap (happened):** SQL `SUM` over an all-null column returns 0 through EF (it adds `COALESCE`), but the contract says the character meter has no output units, so the service maps it to null explicitly.

#### L3 — Caps, kill switch, Azure Translator (R2)

- **Read:** `LocalizationUsageCap.cs`, `UsageBudget` in `UsageMeteringService.cs`, the provider branches in `WorkflowService.RunStepAsync`, `AzureTranslatorProviderService.cs`, CONTRACT sections 2.3, 4.3 and 5.
- **The cap rules:** "used" is the sum for the current UTC month. Machine translation knows its size before the call, so a call is skipped if `used + size > limit`. A model call does not know its size, so it is skipped once `used >= limit`; the call that crosses the limit finishes and is recorded. A skipped string is left as it is; the outcome ends with `, {n} skipped: monthly {kind} cap reached ({used} of {limit})`. A cap already reached before the first call gives 409.
- **Azure call:** `POST {endpoint}/translate?api-version=3.0&from=..&to=..`, key in the header `Ocp-Apim-Subscription-Key` (never in the URL or a log), region header when set, body `[{"Text": "..."}]`. With no key outside production it returns `[MOCK-{LOCALE}] text`.
- **Decision to explain:** why is the controls `PUT` body read as raw JSON? (To tell "field absent: leave as is" from "field present and null: remove the cap".)

#### L4 — Agreements, jobs, scores (R3 and R7)

- **Read:** `ServiceAgreement.cs`, `TeamAssignment.cs`, `ServiceTiers.cs`, `TranslationJob.cs`, `TranslationJobService.cs`, `JobScope.cs`, `VendorPortalService.cs`, `JobEndpoints.cs`, `VendorPortalEndpoints.cs`, CONTRACT sections 2.4, 2.5, 3, 4.4, 6.
- **Job lifecycle:** NotCreated → Assigned → (first vendor edit) InProgress → (vendor submit) SubmittedForReview → (client approve) Approved, or (client send back) NeedsRevision → (vendor edit) InProgress.
- **Job scope:** a string is *open* when its translation is missing, blank, or not `Approved`. A job covers the open strings. A vendor accepts a machine draft by saving the same text, which marks it vendor-reviewed. Submit is refused while any open string is still machine output. Progress = vendor-reviewed open strings ÷ job size (100 when approved).
- **Machine steps never overwrite vendor work:** MT Optimize, Score Quality and Auto-Route touch only `AI` rows that are not `Approved`.
- **Privacy check you should write:** fetch every client and vendor response and search the JSON (not the screen) for vendor real names, project name, slug and score fields.
- **Trap (happened):** in the first version, MT Optimize rewrote any row with a raw draft, which would have overwritten vendor edits. Always ask "who else writes this column?".

#### L5 — The React side (R4, R7)

- **Read:** `app/src/pages/Localization/LocalizationJobs.jsx`, `LocalizationOps.jsx`, `LocalizationWorkflow.jsx`, `Vendor/VendorJobs.jsx`, `Vendor/VendorMyJob.jsx`, and their tests.
- **Done when:** you can explain how the workflow page turns an outcome text into success, partial (amber) or failed (red), and how the vendor page groups strings by score.

#### L6 — The Localization AI service (`localization-ai/`, Python, you rebuild it)

Built from `info/muse-prompts/localization-ai/LA1-to-LA4-prompts.md` and updated by R5. The .NET API calls it over HTTP with the `x-api-key` shared secret.

| Step | What you build (in words) | Done when |
|---|---|---|
| LA1 | Nothing in Python: read the .NET migration that added the AI tables (translation cache with a `vector(384)` embedding and HNSW index, golden cases, eval runs, raw draft and score columns). | You can list the tables and who writes each. |
| LA2 | Service scaffold, settings, the shared-secret check, provider protocols (chat and embeddings) with an OpenAI-compatible HTTP version and **deterministic fakes**, then the **eval harness first**: a golden set loader, pure metric functions, a runner. | The harness runs end to end on fakes before any translation logic exists. |
| LA3 | The pipeline, one module per stage: semantic cache (embed the source, nearest neighbour above a cosine threshold, 0.95 by default), MT Optimize (prompt with glossary terms and checks), the quality judge, Auto-Route (pure function of score and threshold). | Unit tests on fakes pass; a second identical run is served from the cache (the reference served 136 of 136 from cache with 0 tokens). |
| LA4 | Nothing in Python: read how .NET calls the service (`LocalizationAiClient.cs`, `MtOptimizeService`, `QpsScoringService`, `AutoRoutingService`). | You can trace one "Run MT Optimize" click to a cache row. |
| R5 | The judge scores 1 to 5 with prompt version `qps_judge_v2`; a translation whose placeholders do not match the source can never score above 2 (the veto); responses add `operation`, `model`, `promptVersion`, `vetoed`. | Tests for the veto and the new fields pass. |

- **Decisions to explain:** why eval-first (you cannot tell if a prompt change helped without a baseline); why plain functions instead of a framework; why the golden set is marked `verified: false` until a human checks every gold translation.
- **Trap (happened):** the cache insert worked in tests and failed on the real database, because the test table had column defaults the real table did not. Always run against a database built by the real migrations.
- **Limit to remember:** on fake models the judge returns no score, so scoring and Auto-Route can only be proved with a real model.

#### L7 — Port the Localization Lab to Python (P6)

- **Read:** everything in L1–L4, then the CONTRACT once more.
- **Done when:** your service tests pass against a migrated database, every localization route matches in the parity tool, and your seeder gives the same localization rows as the .NET seeder.
- **Traps (all happened in this project's port):** see Part 6, items 1 to 5.

---

## Part 5 — Track G: the agentic bug-fix system (`issue-intel/`)

A self-contained system on invented data: the company **Tessera Engines**, its product **Tessera Editor**, a support group **Sustained Engineering**. It recovers knowledge lost in a tool migration, investigates new tickets with citations and permission checks, drafts fixes and backports for an allow-listed part of a C# codebase with tests and a human as the gate, and routes model calls by cost and quality.

Read `info/muse-prompts/issue-intel/BUILD-SPEC.md` before G0. Its hard rules are the design:

- Synthetic data only. No real companies, people or ids.
- A human approves every write. The agent cannot merge.
- **Leakage must be zero**, and it is tested, not assumed.
- One `ModelGateway` is the only code allowed to call a model; callers ask for a **task type**, never a model name.
- No agent framework; the pipeline is fixed plain functions and the fix agent is a bounded loop written by hand.
- Background work uses a database job table and a worker; no Celery, Redis or broker.

Stack: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 async, **Alembic** (this project owns its database `issueintel`), pgvector + PostgreSQL full-text search, httpx, the official Python MCP SDK, pytest, ruff, mypy. The sample codebase is a small C# solution with xUnit tests.

### G0 — Scaffold, synthetic world, sample repository

- **Build:** settings (`ISSUEINTEL_` prefix), async session, Alembic, Compose (api, worker, pgvector), health route; the `ModelGateway` with an OpenAI-compatible adapter and a scriptable fake, a static task-type → model table, and a log row per call. The sample C# repo with 12 planted bugs, each with a hidden xUnit test and a reference patch, and a script that builds the git history (one commit per planted bug, two release branches). A seeded generator for the corpus (legacy cases, tracker and support tickets, chat threads, people, a third of whom have left, ACLs, prompt-injection samples) that also writes the **ground truth**.
- **Done when:** the sample repo's own tests pass, the hidden tests fail on `main` as expected (bugs planted), and the generator is deterministic for a given seed.
- **Rule to enforce with a test:** the app never imports or reads the ground-truth folders; only the generator and the eval runners do.

### G1 — Knowledge foundation

- **Build:** tables with a 64-dimension vector column (HNSW index) and a `tsvector` column (GIN index); **row-level security** (`ENABLE` + `FORCE`) with policies on every table that carries an `acl_id`, reading the user's entitlements from `SET LOCAL` settings and failing closed when they are unset. Ingest: extract (CSV, JSON, XML) → normalise (idempotent natural keys) → tag ACLs → crosswalk old and new ids (explicit link 1.0, mentioned in text 0.9, title similarity ≥ 0.75 at 0.8) → classify legacy outcomes → chunk (500 words, 50 overlap) and embed → ownership map with a redirect for people who left. Hybrid search: full text + vector, merged with reciprocal-rank fusion, reranked over the top 30, then lineage expansion. A "similar cases" route whose synthesis cites an evidence id for every claim.
- **Done when:** the RLS test proves zero rows for an unentitled user on both ORM and raw SQL; the G1 eval writes recall@5/@10, MRR, outcome accuracy and a leakage rate of 0.
- **Decision to explain:** why RLS first and redaction second? (Retrieval cannot return what the database will not give; redaction is only a backstop.)
- **Lesson (happened):** full-text recall was 0.003 until the query used any-word matching instead of all-words; it is still low (about 0.115) on this corpus, and the causes are written up in `issue-intel/PROGRESS.md`.

### G2 — Investigation pipeline, review, MCP, dashboard

- **Build:** runs and stages tables, a run manager (dedupe, triggers NEW/UPDATE/RERUN, cache on ticket + content hash + pipeline version), a worker that runs stages S1–S8 (parse, module check, ticket retrieval, chat retrieval, code lineage, docs, synthesis, checks) with one row per stage. Failure policy: transient errors retry twice; anything else stops at `FAILED_AWAITING_HUMAN`; no stage is skipped silently. Per-viewer rendering: evidence filtered by entitlement, claims citing removed evidence withheld. A review API, fake tracker/chat/docs adapters, an MCP server with read-only tools, and a small React dashboard.
- **Done when:** the G2 eval reports wrong-module F1, change-attribution precision, citation correctness, zero leakage per viewer, and the 15 injection samples have no effect (nothing posted, no payload echoed).
- **Rule to explain:** text from tickets, chat and code is untrusted. It goes to models inside delimited data blocks and can never choose a tool, a filter or an ACL.

### G3 — Fix agent, backport agent, approvals

- **Build:** a sandbox (a fresh git worktree per attempt) and seven tools: list, read, search, apply patch, build, test, read evidence. Path validation: no absolute paths, no `..`, no symlink escape, writes only into allow-listed modules. **No shell, network or integration tool**, proved by a test. The loop in one readable file: baseline → plan → patch → build → test → revise, bounded by 3 cycles and a token budget; a stopped attempt keeps its trace. A fix is offered only when the ship tests are green and a previously failing test now passes. PR records in a fake code host; the human approves and merges. A backport agent cherry-picks to release branches and resolves only textual conflicts. A final check (`OK`, `NEED_MORE_INFO`, `BLOCK`). Approval tokens: short-lived, single-use, bound to run, ticket and payload hash.
- **Done when:** the G3 benchmark on fakes offers 10 of 10 fixes, each flips its hidden test, and the backports open with the hidden test passing on the release branch (the reference reached exactly this).
- **Lesson (happened):** a rollback added to a session helper expired loaded objects and broke code that read them afterwards. Unit tests did not show it; only the end-to-end run did.

### G4 — Model gateway

- **Build:** versioned routing (per task type: primary model, fallback, token limit, sync or batch, optional canary; exactly one active version; switch and rollback are single audited operations), budgets per run, day and product, a result cache, batch mode through the job table, fallback on provider error, **shadow mode** (a share of calls also go to a candidate model, logged, never returned), a cheap `quality_verify` screen before the expensive final check, scorecards and a metrics route.
- **Done when:** the shadow test proves shadow output is never returned, and you can walk the upgrade runbook in `issue-intel/README.md` (offline eval → shadow → canary → switch → rollback).
- **Decision to explain:** why callers ask for a task type, not a model name. (So models can change by data and evidence, not by code edits.)

---

## Part 6 — Traps and lessons from this project

Each of these really happened during the build. Ask the tutor to quiz you on them.

1. **Lazy loading is off on purpose.** The Python models use `lazy="raise"`. Touching a relationship that was not loaded raises an error. Load what you use (`selectinload`) in the same query.
2. **The identity map keeps old collections.** If you add a new child row to the session but not to its parent's collection, a later query in the same session still shows the old, shorter collection. EF Core fixes this up for you; SQLAlchemy does not. Append to the collection.
3. **Delete-then-insert on a unique key fails in one flush.** SQLAlchemy writes inserts before deletes. Flush after the deletes.
4. **Pydantic models take keyword arguments only.** Positional arguments raise at runtime, and mypy catches it if you run it.
5. **Test schemas can lie.** A table built by tests had column defaults that the real migrated table did not; the insert passed in tests and failed in reality. Test against a database built by the real migrations.
6. **Check constraints catch stale tests.** When scores moved to 1–5, a test inserting 55 failed only on PostgreSQL, not on the in-memory provider.
7. **Hand-written EF migrations need every foreign-key index**, and the model snapshot must match; generate a throwaway migration to prove it is empty.
8. **A default in two places drifts.** The score threshold default was 4 in the migration and snapshot but still 70 in the Fluent mapping.
9. **EF cannot translate an ORDER BY on a record built through its constructor.** Project to an anonymous type, sort, then map.
10. **Undefined sort order shows up as parity noise.** Make sort keys unique.
11. **Read the authority before changing a port.** A correction once made a lookup case-insensitive when the C# compares exactly (ordinal). The C# was right.
12. **Run end to end, not only unit tests.** Several bugs (the rollback, the cache insert, the job scope) appeared only on the real stack.
13. **Fake models prove wiring, not quality.** Never quote a quality number from a fake run.
14. **Who else writes this column?** MT Optimize would have overwritten vendor edits until it was limited to machine rows.
15. **Environment matters in tests.** A .NET test failed only because the test run inherited `ASPNETCORE_ENVIRONMENT=Development`, which turns on service validation at startup.
16. **Banker's rounding.** C# `decimal.Round` rounds halves to even; reproduce that, or costs differ in the sixth decimal.

---

## Part 7 — Switching the live site to Python (when you are ready)

Do not start this until every item below is true for **your** Python API.

### 7.1 Readiness checklist

- [ ] Every route in `parity_routes.txt` matches the live .NET API (API-key and signed-in runs).
- [ ] A user created on .NET logs in on Python with password and TOTP, and the reverse.
- [ ] Your seeders produce the same rows as the .NET seeders on an empty database.
- [ ] Exercise runs give the same results on both.
- [ ] Lint, types and tests pass in CI, not only on your laptop.
- [ ] The Python image builds in the deploy workflow and runs on the EC2 host beside the .NET API.
- [ ] You know which EF migration is the latest, and you have a plan for future schema changes (keep EF as the owner until you choose Alembic, then hand over in one deliberate step).

### 7.2 A safe cut-over plan

1. **Run both** on the host: .NET as today, Python on another port, same database.
2. **Shadow reads:** send a copy of read-only traffic to Python and log differences (the parity tool is a manual version of this).
3. **Move one route group at a time** behind the reverse proxy (for example the read-only curriculum routes first), watching errors and latency.
4. **Writes last**, starting with low-risk ones.
5. **Keep rollback one config change away:** the proxy points back at .NET.
6. Only when every group runs on Python for a while with no differences, retire the .NET container. Keep its image tag.

### 7.3 The other two services

`localization-ai/` and `issue-intel/` are already Python. For them, "switching" means moving from fake to real providers:

- localization-ai: set the `LOCALIZATION_AI_CHAT_*` and `LOCALIZATION_AI_EMBEDDING_*` variables, verify the golden set by hand, then run the eval configs and compare against the baseline.
- issue-intel: set `ISSUEINTEL_MODEL_ADAPTER` and the endpoint variables, run the G1–G4 evals with real models, and label every number with the model names used.
- The .NET API needs `AzureTranslator__Key` and `AzureTranslator__Region` for real machine translation, and rates entered through `POST /api/localization/ops/rates` for real costs.

Real model calls cost money. Start small.

---

## Appendix A — Glossary

| Term | Meaning |
|---|---|
| Parity | Calling the same route on two APIs with the same data and comparing the JSON. |
| Problem details | The standard error body: `type`, `title`, `status`, `detail`, `instance`, `traceId`. |
| Model snapshot | EF Core's record of the current model, used to compute the next migration. |
| RLS | Row-level security: PostgreSQL policies that filter rows per database session. |
| `SET LOCAL` | Sets a setting for the current transaction only; used to pass the user's entitlements to RLS. |
| HNSW | A fast approximate nearest-neighbour index for vectors (pgvector). |
| RRF | Reciprocal-rank fusion: merging two ranked lists by summing 1/(k + rank). |
| Golden set | Hand-checked input/expected-output pairs used to score a pipeline. |
| Fake provider | A deterministic stand-in for a model, used in tests. |
| Shadow mode | Sending a copy of live calls to a candidate model and logging, never returning, its output. |
| Canary | Sending a small share of real traffic to a new version. |
| TOTP | Time-based one-time password (authenticator app codes). |
| MT | Machine translation. |
| QPS score | The quality score the judge gives a translation (now 1 to 5). |

## Appendix B — Prompts to start each step with the tutor

Copy, fill in the step, paste.

```
We are on Track P, step P2 (authentication). Here is the step from the guide:
<paste the P2 section>
Here are the C# files it names:
<paste AuthEndpoints.cs and Pbkdf2PasswordHasher.cs>
Start at hint level 1. I will write the Python.
```

```
I finished step L3 and the checks pass. Quiz me with three questions on the decisions in
this step, one at a time.
```

```
Review this Python I wrote for step G3 (the sandbox path check). Do not rewrite it. Point
at the lines that are wrong and say why.
<paste your code>
```

```
I am stuck on P7 (seeders). Give me hint level 2: which reference file to read and what
to look for in it.
```
