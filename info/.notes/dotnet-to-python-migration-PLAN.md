# .NET → Python Migration Plan (Neuralascent API)

Decided 2026-10-02 (supersedes the Java version of this plan dated 2026-10-01). Goal: (1) learn how to migrate a codebase between stacks, (2) get **hands-on Python backend skill for Python roles** — the owner's current Python skill is the weak spot, so the migration is mostly a Python practice track.

This matches `info/history/00-INDEX.md` and `08-python-migration-and-study-plans.md`, which already present the backend migration as a Python migration, and the stack of the AI tutor (`ai-agent/`).

**What did not change:** the Java LLD / Spring *curriculum* and the Java exercise runners stay Java. Only the language of the platform backend changes from "Java (planned)" to "Python".

## 1. Working rules
- **All Python is written by the owner.** Claude explains concepts, gives hints, answers "why", and reviews pasted code. Claude does not write the migration code (`api-py/` is read-only for Claude under `CLAUDE.md`).
- Strangler pattern: the Python service runs beside .NET; the proxy (`app/nginx.conf`) routes by path group, one slice at a time; rollback = revert the proxy rule.
- .NET `api/` is **frozen**: hotfixes only, no new features, no new EF migrations.
- Shared Postgres database; no second copy of the schema.

## 2. Stack — proposed defaults (owner to confirm or change at slice 0)
| Area | Default | Why |
|---|---|---|
| Python | 3.12 | Same as `ai-agent/`; current and widely used |
| Web | FastAPI + uvicorn | Same as `ai-agent/`; the dominant modern Python API stack in job posts |
| Validation / DTOs | Pydantic v2 (`BaseModel`, `pydantic-settings`) | Typed request/response models; learn once, reuse in the tutor |
| DB access | SQLAlchemy 2.0 (typed ORM) over `psycopg` 3 | The ORM question every Python backend interview asks; psycopg is already used in `ai-agent/` |
| Schema changes | Alembic, **baselined on the existing schema** (`alembic stamp`, no `create_all`) | Schema is owned by EF Core today; Alembic takes over only after the .NET API is retired for a table |
| Tests | pytest (fixtures, parametrize), `httpx` TestClient, Testcontainers-Python Postgres | Fast unit tests plus real-DB integration tests |
| Lint / format / types | ruff, mypy (strict-ish) | Habits employers look for |
| Packaging | `venv` + `requirements.txt` first; move to `uv` or `pyproject` later if wanted | Don't add tooling before you need it |
| Module folder | `api-py/` (separate from `ai-agent/`) | Keeps the core API and the tutor decoupled; folder name still open (`08` leaves it undecided) |

Not decided yet (decide when the slice needs it): sync vs async SQLAlchemy sessions (start sync, learn async at slice 2), background jobs approach, whether `api-py/` and `ai-agent/` ever merge.

## 3. Slice order
| # | Slice | .NET source | Python concepts to practise |
|---|-------|-------------|-----------------------------|
| 0 | Health + config | `/health*`, `appsettings*` | Project layout, venv, `pydantic-settings`, FastAPI app factory and lifespan, logging, Dockerfile (non-root), pytest basics, ruff |
| 1 | Read-only: reading-map | `/api/reading-map` | SQLAlchemy models mapped to an existing schema (never `create_all`), sessions and dependency injection, Pydantic response models, type hints, repository vs service split |
| 2 | Read-only: courses / lessons / atlas | `/api/courses`, `/api/lessons/{id}`, `/api/knowledge-atlas` | Relationships, N+1 and `selectinload`, pagination, query building, async vs sync, caching with `functools.lru_cache` |
| 3 | Writes | task toggle, lessons/problems POST/PUT/PATCH, ingest | Transactions and rollback, request validation, mapping errors to the *same* status codes as .NET, idempotency, context managers |
| 4 | Auth + MFA | `AuthEndpoints`, `Services/Auth`, `Services/Email` | JWT with the shared HS256 key, cookies, password-hash compatibility (below), TOTP (`pyotp`), email (`smtplib` / `aiosmtplib`), dependency-based auth, secrets handling |
| 5 | Exercise runner | `ExerciseEndpoints`, `Services/Exercises` | `docker` SDK or `subprocess`, process isolation, timeouts, `asyncio`, generators for streaming output |
| 6 | Localization + reconciliation (+ chat/import/admin as needed) | `Services/Localization`, `Services/Reconciliation`, `ChatEndpoints` | Service design, outbound HTTP with `httpx`, scheduling and background tasks, testing strategy, retries |

Localization Lab is ON HOLD as a product; slice 6 is last and may stay in .NET longer.

**Concrete compatibility example for slice 4.** The .NET `Pbkdf2PasswordHasher` stores PBKDF2-HMAC-SHA256, 210,000 iterations, a 16-byte random salt (base64) and a 32-byte hash (base64), with the iteration count in its own column. Python's `hashlib.pbkdf2_hmac` can verify exactly those hashes, so users keep their passwords and nobody is forced to reset. Compare in constant time (`hmac.compare_digest`). Read `api/Services/Auth/Pbkdf2PasswordHasher.cs`, `JwtTokenService.cs` and `TotpSecretProtector.cs` before writing anything, and write the behaviour down first.

## 4. Per-slice checklist
1. Read the .NET endpoint/service and write down its behaviour (inputs, outputs, status codes, edge cases). Don't port line by line.
2. Design the Python shape yourself (layers, models, errors).
3. Implement (you type it).
4. **Contract-compare:** send the same request to .NET and Python, diff the JSON. Differences are bugs or documented decisions.
5. Tests: unit plus integration against a throwaway Postgres.
6. Route the path to Python in the proxy; watch; rollback = revert the proxy rule.
7. Log it below and mark the .NET endpoint as migrated.

## 5. Skills ladder (what this should leave you able to talk about in interviews)
Typing and Pydantic models · dependency injection in FastAPI · SQLAlchemy mapping and the N+1 problem · transactions · async/await and when not to use it · pytest fixtures, parametrization and mocking · JWT and password hashing · Docker for a Python service · structured logging and error handling · a real contract-compare migration story.

## 6. Open items
- Confirm or change the stack table above, and the folder name, when slice 0 starts.
- Slice-0 detail (Dockerfile, compose service, proxy rule): decide when we start.
- Seed data (`api/Data/*SeedData.cs`) stays with .NET until a later slice, since the schema is shared.
- Stale Java-migration references the owner may want to update (outside `info/`, so not editable by Claude): `task_tracker.md` (~line 47, "Phase 8 Java 21 + Spring Boot 3 in `api-java`") and `.agents/memory/migration-plan.md` (active sub-task 8.1). `docker-compose` and the runners are unaffected.

## 7. Status log
- 2026-10-01: Java version of this plan written (stack, schema strategy, slice order). Nothing built.
- 2026-10-02: Switched to Python at the owner's request, to get hands-on Python practice for Python roles. File renamed from `dotnet-to-java-migration-PLAN.md`. Nothing built yet.
