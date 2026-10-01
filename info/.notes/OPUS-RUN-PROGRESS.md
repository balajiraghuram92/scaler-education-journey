# OPUS Run Progress

Branch: `claude/opus-3-stage-d88sa1` (never push `main`; no deploys; no EC2/AWS/SSM; no secrets; never change `content_status`; no DB writes).
Prompt: `info/.notes/opus-cloud-prompt-3-stage-audit-and-ai-agent-hardening.md`

## Status
| Stage | Status |
|---|---|
| 1 Audit | **Complete** (2026-10-01) |
| 2 Chapter updates | **Complete** (2026-10-01), local commit on this branch, not pushed; see Stage 2 below |
| 3 `ai-agent/` hardening | **Complete** (2026-10-01), local commit on this branch, not pushed, not deployed; see Stage 3 below |

## Stage 1
- Files changed: `info/.notes/OPUS-AUDIT-REPORT.md` (new), `info/.notes/OPUS-RUN-PROGRESS.md` (new). Nothing else.
- Method: 5 parallel Sonnet 5.5 sub-agents (machine-coding inventory, seeded lessons, ai-agent code, deploy/CI, info/ tree); orchestrator re-verified high-severity ai-agent and deploy claims in the code. **Nothing was executed**; runtime behaviour is inferred from code. The orchestrator was Sonnet 5.5, not Opus 5.5.
- Headline findings: (d) `DATABASE_URL` never produced by the deploy path (Critical for prod); unauthenticated `/echo` and `/agent_test` publicly proxied; fresh-DB migration deadlock; rollback deletes crash logs; no Python tests/CI. All defects (a)–(h) confirmed.
- Content headline: Java L2/L3 seed bodies are empty; Splitwise exercises exist but are unwired; BookMyShow has no exercise; MCQ correct answer is the longest option in 94 % of questions; 58 templated lessons thin and effectively locked.
- Decisions made: none beyond audit scope. Locked decisions (bge-m3, LangGraph, Pydantic AI, Langfuse, Muse/Nova/Gemini, HNSW, hybrid retrieval) respected and not re-opened.

## What remains
- Owner answers to report §D (esp. 1, 4, 5, 6).
- Stage 2 and Stage 3 work lists are in report §C.

## Exact next action
Owner reviews and merges the Stage 1 PR, answers §D, then says "go Stage 2" or "go Stage 3" (naming the §A/§B items approved). A fresh session starts from this file, reads the report, and begins with §C item 1 of the named stage.

## EC2 follow-up steps (written in Stage 3; owner runs later)
Nothing below has been run. Commands print variable **names** only; never paste values into notes or chat.

1. **SSM env names.** `aws ssm get-parameter --name /neuralascent/prod/api-env --with-decryption --query Parameter.Value --output text | cut -d= -f1 | sort` and, on the host, `sudo cut -d= -f1 /etc/studytracker/api.env | sort`. Required for ai-agent: `Auth__JwtSigningKey` (32+ bytes; .NET already enforces this in Production), `MUSE_AI_API_KEY`, and either `DATABASE_HOST`/`DATABASE_NAME`/`DATABASE_USER`/`DATABASE_PASSWORD` (+ optional `DATABASE_PORT`) **or** `DATABASE_URL` with a percent-encoded password. `DATABASE_NAME` must be `StudyTrackerDB`. Recommended: `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`/`LANGFUSE_BASE_URL` (without them tracing is off, with a warning). Optional: `DEEPINFRA_API_KEY`. No quotes around values. `bootstrap-single-ec2.sh` only fetches SSM when `/etc/studytracker/api.env` is absent, so after changing SSM, refresh the host file by hand (or move it aside so bootstrap re-creates it). The deploy script now fails **before touching any container** if the database names or `MUSE_AI_API_KEY` are missing.
2. **Prod DB image is pgvector.** `docker inspect --format '{{.Config.Image}}' studytracker-postgres` should print `pgvector/pgvector:pg16`. Then `docker exec studytracker-postgres psql -U studyuser -d StudyTrackerDB -tAc "SELECT extversion FROM pg_extension WHERE extname='vector'"` should print a version. Also check for leftovers: `... -tAc "SELECT to_regclass('schema_migrations'), to_regclass('content_chunks')"`.
3. **Backup first.** `pg_dump -F c` without `-t` (see `info/history/04` §4), then verify with `pg_restore --list`.
4. **Deploy** (owner's normal `[deploy]` commit or manual dispatch, after merging this branch). Both the ai-agent image and the app image (nginx) change. Check:
   `curl -s localhost:5001/health` → `{"status":"ok"}` · `curl -s localhost:5001/health/ready` → `database: ok` · `curl -s https://tutor.neuralascent.top/health` → JSON from FastAPI (it is no longer nginx's fixed `healthy`) · `curl -s -o /dev/null -w '%{http_code}' https://tutor.neuralascent.top/echo` → `401` · `/docs` → `404` · `/me` with a real `na_auth` cookie → `200`.
5. **Run `migrate.py` once, by hand, after a deploy** (the deploy's `api --migrate` creates `lessons`, which 002 needs): `docker exec ai-agent python migrate.py`. Expected: `001_…: applied` (a no-op `IF NOT EXISTS`, now recorded) and `002_…: applied`, then `migrate: done (2 applied)`. Run it again: both `already applied, skipping`. Check `SELECT filename, applied_at FROM schema_migrations` and `\d content_chunks`. Then `docker restart ai-agent` so pooled connections register the vector type (otherwise this happens within an hour via `max_lifetime`). Not wired into the deploy script: where it runs long-term is still your decision (report §D Q5).
6. **Rollback expectations.** `rollback()` now prints each container's state (exit code, OOM, restarts) and its last 100 log lines **before** removing it; this goes to the SSM output and the S3 `deploy-logs/<sha>/` prefix. Rollback restores the previous api/ai-agent/app images but **does not undo DB changes** (EF `--migrate`/seed, or `migrate.py`). `migrate.py` changes are additive (extension plus a new table) and old images ignore them; manual undo of 002 is `DROP TABLE content_chunks; DELETE FROM schema_migrations WHERE filename = '002_create_content_chunks.sql';` (keep the extension). Caveat: a rollback to the **previous** ai-agent image brings back the old code, which needs `DATABASE_URL`. If the env file lacks it, that container crash-loops; with the new nginx config the main site stays up and only `tutor.` returns 502. With a rolled-back **app** image, nginx again resolves `ai-agent` at startup.

## Stage 2 — Java vertical content (2026-10-01)

Authorised by the owner (relayed by the orchestrating session) to edit Java-vertical lesson/exercise content only, overriding CLAUDE.md for this task. No DB writes, no `content_status` changes, no deploys, no push.

### Stage 1 findings re-verified against the code
| Stage 1 claim | Verdict |
|---|---|
| L2/L3 empty bodies (no case in `GetAuthoredLessonContent`) | **False.** Both cases exist as C# `or` patterns (`"02-oop-1-intro-lab" or "02-oop-classes-objects"`, `"03-oop-2-access-modifiers-encapsulation" or "03-oop2-encapsulation-inheritance"`); 1,025 and 1,385 words, all headings. A plain `"slug" =>` grep misses them. No change made. |
| Splitwise exercises unwired to L22 | True. Practice-pool sources are Spring Boot 3 + JPA + Lombok (Java 17). The runner only supports `java-maven` (`ExerciseWorkspaceBuilder` throws for any other profile), so they could not be wired as-is. |
| No BookMyShow exercise anywhere | **False.** `0.Exercises` has 4 BMS zips (`1773391369_aa02…` ratings, also in practice-pool; `1789721304_196f…` create show; `1789729988_b93c…` book ticket; `1789730688_7e2a…` signup/login). None was wired. |
| L17 capstone 357 w, L24 hotel 629 w | True (356 / 628). L24 also misdescribed its own exercises (date ranges, "completed" session, rate × duration). |
| Dangling `ConceptNextLesson` slugs | True: 9 of 10. Note: `KnowledgeAtlasSeedData.Seed` returns early once domains exist, and `ConceptDetailPopover.jsx` ignores `lessonSlug` (it guesses a slug from the title), so the fix only affects fresh databases. |
| Spring L14–17 thin | True (321–363 w). |
| Extra (found this stage) | L21's Practical Backend Scenario contradicted its own Concepts (in-memory lock, `LOCKED`, 5-min TTL versus `BLOCKED`, 15 min, `SERIALIZABLE`, and "synchronized fails across pods"). L5, L21, L22 Practice Loops have 6 steps (contract says 5). L18–L20 Practice Loops do not use `1.` numbering (not checked further). |

### Files changed
- `api/Data/JavaVerticalSeedData.cs`: replaced bodies of `24-machine-coding-hotel-management` (628 → 1,216 w), `17-machine-coding-capstone` (356 → 1,338 w), `14-spring-boot-core` (321 → 1,216 w), `15-spring-data-jpa` (363 → 1,221 w), `16-spring-rest-api` (325 → 1,233 w). All have the 5 contract sections with `###` sub-headings, 5-step loops, and a one-line Reference; each case carries a `// SOURCE_TYPE:` comment (L24 FROM_MATERIAL with LLM_GENERATED scenario figures; the other four LLM_GENERATED, needing owner review). Rewrote one paragraph of the L21 scenario to match its Concepts. No metadata, `ContentStatus`, or seeding logic touched.
- `api/Data/KnowledgeAtlasSeedData.cs`: 8 `LessonSlug` values now resolve (`java-concurrency` → `06-concurrency-1-threads`; the 7 FDE targets → their real FDE slugs). `next-security` left as is (ambiguous; see Questions).
- New exercises (`java-maven`, Java 11, in-memory repositories; Lombok, JPA and Spring stripped, following the hotel-* precedent):
  - `exercises/java/java-lld/applied-machine-coding/splitwise-create-delete-group/` (`java-lld-splitwise-create-delete-group`, 6 tests). FROM_MATERIAL: Scaler zip `1773391465_1711…` / practice pool.
  - `exercises/java/java-lld/applied-machine-coding/splitwise-manage-group-members/` (`java-lld-splitwise-manage-group-members`, 14 tests). FROM_MATERIAL: Scaler zip `1773391463_7dc9…` / practice pool.
  - `exercises/java/java-lld/applied-machine-coding/bms-book-ticket/` (`java-lld-bms-book-ticket`, 8 tests). FROM_MATERIAL: Scaler zip `1789729988_b93c…` (6 tests ported); 2 tests LLM_GENERATED (unavailable-id reporting, and an 8-thread race that uses a slow-`getStatus` `ShowSeat` subclass so a lock-free solution fails deterministically). Uses typed exceptions instead of the original's bare `Exception`.
  - Ported tests keep the original scenarios and assertions, with Spring DI replaced by constructor wiring and `.toList()` replaced by `Collectors.toList()` for Java 11. A few assertions were added (creator is the admin, group survives an unauthorised delete, a member row exists before delete, seats untouched on failure).
- `app/src/data/lessonExerciseAssociations.js`: added entries for L21 (`java-lld-bms-book-ticket`) and L22 (both Splitwise ids). No existing entry changed.
- `info/.notes/verify-new-exercises.sh`: appended the 3 new exercise paths.

### Validation run
- `mvn test` (JDK 21 with `-Dmaven.compiler.release=11`, plus the repo verify script): all 3 solutions pass (6/6, 14/14, 8/8); all 3 starters compile and fail. The race test failed a lock-free variant 3/3 (8 of 8 bookings succeeded) and passed the reference 5/5.
- `dotnet build`: **not run.** No SDK in the container and `builds.dotnet.microsoft.com` is blocked by proxy policy. Substitute: a tree-sitter C# parse of both seed files reports 0 syntax errors (negative control: an injected unescaped quote produced 109 errors), and each new body round-trips byte-for-byte from the C# verbatim string to the Markdown draft. **Owner must still run `docker compose ... build api` or `dotnet build api`.**
- Association test (vitest, isolated copy): 4/4 pass. All 20 association ids resolve to an `exercise.json` with a matching `lessonSlug` (70 manifests).

### Remaining / not done
- **Write-once gotcha.** Existing DB rows for L14–17 (Spring) and L24 already contain all three headings, so `BackfillLessonContent` will **not** overwrite them; the new text reaches only fresh databases unless the owner reseeds those 5 slugs (CLAUDE.md procedure). L21's scenario fix has the same limitation. The atlas fix applies only to a fresh atlas seed.
- No new MCQs were written. MCQs for L17 and L14–16 remain LLM_GENERATED.
- BMS zips for create-show, ratings, and signup are still unwired. Unwired practice-pool items remain.
- The 6-step Practice Loops (L5, L21, L22) were not normalised.

### Questions for owner
1. Reseed the 5 rewritten slugs (and L21) locally/in prod using the CLAUDE.md procedure? That resets `content_status` to Draft for those rows.
2. `next-security` (title "Next Security", module "Application Engineering & Reliability", under the concurrency concept): which lesson should it point to, or should the row be removed?
3. OK that ported exercises changed the original contract slightly: typed BMS exceptions, extra assertions, and an LLM-added concurrency test?
4. Wire the other three BMS zips (create show, ratings, signup/login) next?
5. Normalise L5/L21/L22 Practice Loops to 5 steps, or are 6 steps acceptable for machine-coding lessons?
6. Is the advanced tier (1,200–1,500 w) right for the Spring lessons, or do you want them at the foundational 500–800?

### Exact next action
Owner runs `dotnet build api` (or the docker compose build) and the API container locally, opens L17, L21, L22, L24, and L14–16 after reseeding (Q1), runs one exercise from each new directory through the UI, answers the Questions, then says "go Stage 3".


## Stage 3 — `ai-agent/` hardening (2026-10-01)

The owner authorised edits for this task, overriding CLAUDE.md. Scope: `ai-agent/**`, plus minimal lines in `docker-compose.yml`, `docker-compose.dev.yml`, `.env.example`, `scripts/deploy-single-ec2.sh`, `deploy/single-ec2.env.example` and `app/default.conf.template`, and a new `.github/workflows/ai-agent-ci.yml`. No deploys, no push, no EC2/AWS/SSM access, no secret values read, no real DB (throwaway `pgvector/pgvector:pg16` containers only), no RAG ingestion. Locked decisions were not re-opened. Config stays plain `os.environ` (decision #14).

### Stage 1 defects re-verified before fixing
All confirmed. (a) was **reproduced**: the old `migrate.py` on a fresh pgvector DB failed with `psycopg_pool.PoolTimeout: couldn't get a connection after 30.00 sec`. (b), (c), (d), (e), (g) and (h) were confirmed in the code. One addition: libpq silently mis-parses a `DATABASE_URL` that has an unencoded `@` or `/` in the password (`u:p@ss@h` → host `ss@h`). `config.py` now rejects this.

### Files changed
- `ai-agent/config.py`: no side effects at import. `load_settings()`/`get_settings()` collect every problem into one `ConfigError` that names variables but never values. The DB conninfo comes from `DATABASE_URL` (validated), **or** `DATABASE_HOST/NAME/USER/PASSWORD/PORT` via `psycopg.conninfo.make_conninfo`. The signing key needs 32+ bytes. Muse model id and base URL moved here (`MUSE_MODEL`, `MUSE_BASE_URL`, same defaults). New: optional `DEEPINFRA_API_KEY`, plus `LLM_TIMEOUT_SECONDS`, `AI_AGENT_ENABLE_DOCS` and `AI_AGENT_RATE_LIMIT_PER_MINUTE`. `Settings` hides its secrets from `repr`.
- `ai-agent/main.py`: `create_app()` factory (`uvicorn main:create_app --factory`). A bad env prints one line, `ai-agent startup error: ...`, and exits 1 with no traceback. `/docs`, `/redoc` and `/openapi.json` are off unless `AI_AGENT_ENABLE_DOCS=true`. The lifespan opens the pool with `wait=False` and flushes Langfuse on shutdown.
- `ai-agent/observability.py`: lazy. `init_observability()` runs from the lifespan and makes no network call. The `auth_check()` network call is now the opt-in `check_auth()`. `Agent.instrument_all()` moved here. Tracing is disabled with a warning when the LANGFUSE keys are absent.
- `ai-agent/db.py`: `create_pool()`. `configure` registers pgvector only if the type exists, and leaves the connection idle. `max_lifetime=3600`.
- `ai-agent/migrate.py`: one plain sync connection in `autocommit`, without vector registration. It takes `pg_advisory_lock`, runs each file in its own real transaction together with its ledger row, and resolves the path relative to the file. `MigrationError` names the failing file. Exit codes: 0 ok, 1 migration/connection failure, 2 config.
- `ai-agent/auth.py`: `options={"require": ["exp","iss","aud"]}`, settings from `app.state`, `WWW-Authenticate: Bearer`, and a `user_id()` helper (`nameid`, the .NET `ClaimTypes.NameIdentifier`).
- `ai-agent/rate_limit.py` (new): in-process sliding-window per-user limiter. The `rate_limited_user` dependency gives 429 + `Retry-After`. The hook point and its limits are documented in the module docstring.
- `ai-agent/routers/test_agent.py` → `routers/echo.py`: `/echo` requires auth and rate limiting. The agent is built lazily from config. An upstream failure gives a 502 with no details.
- `ai-agent/routers/test_graph.py` → `routers/graph_demo.py`: `/agent_test` requires auth. Langfuse callbacks are attached per call.
- `ai-agent/routers/health.py`: `/health` is still pure liveness. New `/health/ready` checks the DB and reports `vector_extension` (503 when the DB is down).
- `ai-agent/echo_agent.py`, `echo_graph.py`: no import-time clients. `routers/identity.py`: lint only.
- `ai-agent/Dockerfile`: `python:3.12-slim-bookworm`, non-root `app` (uid 10001), code root-owned and read-only, `HEALTHCHECK`, and `--proxy-headers`. New `ai-agent/.dockerignore` excludes `.env*`, `tests/` and caches.
- New: `ai-agent/tests/` (51 tests), `requirements-dev.txt` (pytest 9.1.1, httpx 0.28.1, ruff 0.16.9), `pyproject.toml` (ruff + pytest config only), `.github/workflows/ai-agent-ci.yml` (pull_request + push on `ai-agent/**`, `contents: read`, ruff + pytest, no secrets, no image build, no deploy).
- `docker-compose.yml`: ai-agent now gets `DATABASE_HOST/PORT/NAME/USER/PASSWORD` in place of the raw-password `DATABASE_URL`, optional passthroughs for the new names, and `depends_on: database: service_healthy`. `docker-compose.dev.yml`: `AI_AGENT_ENABLE_DOCS: "true"` for dev, and a trailing space removed.
- `scripts/deploy-single-ec2.sh`: new `require_ai_agent_env` preflight (DB names or `DATABASE_URL`, plus `MUSE_AI_API_KEY`; warns if LANGFUSE is unset) and new `dump_container_logs`, called at the start of `rollback()`. `start_ai_agent` is unchanged apart from a comment, because `--env-file` already passes all names through.
- `app/default.conf.template` (tutor HTTPS block only, plus one `limit_req_zone`): `/health` now proxies to FastAPI. It adds `limit_req` (5 r/s per IP, burst 20, 429), `client_max_body_size 1m` and 120 s proxy timeouts. `ai-agent` is resolved per request (`resolver 127.0.0.11` + variable), so nginx starts even when ai-agent is absent.
- `.env.example`: removed the misleading `DATABASE_URL` line and the trailing spaces on old lines 16 and 26; added ai-agent names with placeholders/defaults. `deploy/single-ec2.env.example`: added `Auth__JwtSigningKey`, `MUSE_AI_API_KEY`, `LANGFUSE_*` and `DEEPINFRA_API_KEY` with placeholders.

### Validation (this container; a Docker daemon was started locally)
- `pytest`: **51 passed**, also from a clean venv installed from `requirements-dev.txt`. Covered: auth (valid bearer/cookie; expired, wrong issuer/audience/key, missing exp/iss/aud, alg none, tampered, garbage → 401), `/me` `/echo` `/agent_test` 401 without a token with no model call, 429 per user, docs off/on, `/health`, `/health/ready` 503, config in both shapes with `@:/#%'\` in the password, the startup subprocess (bad env → exit 1 with no traceback; importing every module with LANGFUSE set does not import `langfuse`), and migrations on pgvector (described below). With Docker unavailable, the 6 DB tests skip with `migration/DB tests need Docker: docker daemon not reachable`.
- Migrations on a throwaway container: run 1 printed `001…: applied`, `002…: applied` (applied_at `…18.813605` vs `…18.840686`); run 2 printed both `already applied, skipping`. With `003_broken.sql` (`CREATE TABLE half_done; SELECT 1/0`) and `004_after.sql`: 001/002 stayed committed, `half_done` and `after_failure` do not exist, and the ledger holds only 001 and 002. Three concurrent runners applied each file exactly once. The pool opens on a DB without `vector`, and after migration a new connection round-trips a `Vector`.
- `ruff check` and `ruff format --check`: clean. `py_compile`: OK. `actionlint`: OK. `bash -n`: OK. `shellcheck -S warning`: 1 warning, the pre-existing SC2034 (`attempt` unused), with the same count before and after. The new deploy functions were tested against throwaway env files (pass / `DATABASE_NAME is missing` / `MUSE_AI_API_KEY is missing`) and against a crashed container (`status=exited exit=3`, last log line shown).
- `docker compose ... up -d --build ai-agent`: **the repo Dockerfile could not be built here**. `apt-get` against `deb.debian.org` got 403 from this sandbox's egress policy. A scratch-only variant without the apt/curl step (Python healthcheck, proxy CA as a BuildKit secret for pip) was built and started through the real compose files. Results: `database` healthy, `neuralascent-ai-agent` healthy, uid 10001, `/app` not writable, `tests/` not in the image. `/health` 200; `/health/ready` 200 with `vector_extension: false`; `/me`, `/echo` and `/agent_test` 401 without a token; `/me` 200 and `/agent_test` 200 with a locally signed token; `/openapi.json` 200 (dev flag). The compose DB password contained `@:/#%` and worked. In-container `migrate.py` on the fresh compose DB applied 001, then failed cleanly on 002 (`relation "lessons" does not exist`, the expected EF ordering dependency); after a stub `lessons` table it applied 002, and a rerun skipped both. The stack was removed with `down -v`; the volume was a throwaway one in this sandbox.
- nginx (`nginx:alpine`, template rendered with the entrypoint's `sed`, self-signed cert): `nginx -t` OK. With **no** ai-agent container, nginx started, the main `/health` returned 200 and tutor `/health` 502. With ai-agent: tutor `/health` returned FastAPI `{"status":"ok"}`, `/me` 401, `/docs` 404, a 2 MB POST 413, and 40 parallel requests gave 20× 401 + 20× 429.

### Not verified / remaining
- The `apt-get install curl` layer of the real Dockerfile (egress policy). The image was not built for arm64 here; the deploy workflow builds arm64.
- The CI workflow has not run on GitHub (branch not pushed). `deploy-api.yml` does not gate on it (deploy workflow untouched).
- Base image is pinned by tag, not digest; there is no dependency lock or hashes. `/me` still returns raw claims. There is no user-status re-check (the JWT has a `status` claim), no CORS and no CSRF handling. The port-80 tutor `/health` is still nginx's static 200 (it only redirects). The rate limiter is in-process only.
- `migrate.py` is not wired into deploy or container start (owner decision).

### Decisions made this stage
1. App factory plus `--factory`, so importing modules is side-effect free and tests build apps from `Settings` directly.
2. LANGFUSE keys are optional at runtime (tracing off plus a warning); `MUSE_AI_API_KEY` stays required.
3. Two rate-limit layers: nginx per IP (5 r/s, burst 20) and in-app per user (30/min default). This answers report §D Q11 provisionally.
4. Tutor `/health` is proxied to FastAPI (§D Q12): public and unauthenticated, liveness only. `/health/ready` is also reachable through `tutor.`, but it reveals only ok/down and whether the extension is present.
5. The 32-byte key floor applies in every environment (the .NET API enforces it only in Production).

### Questions for owner
1. `info/history/07` §1 rule 1 says `ai-agent/` Python is hand-written by you. This stage wrote it under your explicit override. Do you want to review it line by line, or re-type it, before merging?
2. Where should `migrate.py` run long-term: a deploy step after `api --migrate`, container start, or manual?
3. Should LANGFUSE be mandatory again (fail at startup when unset)?
4. Are the limits OK: 5 r/s per IP with burst 20, 30 requests/min per user, 1 MB body, 120 s read timeout? SSE streaming (Phase 1.4) will need `proxy_buffering off` and a longer timeout.
5. Should `deploy-api.yml` also run the ai-agent pytest before building images? That file was not touched.
6. Should `/health/ready` be blocked at nginx for public traffic?

### Exact next action
Owner reviews the diff (`git show` on this branch), answers the Questions, pushes the branch or opens a PR so `ai-agent CI` runs on GitHub, then follows the "EC2 follow-up steps" above (steps 1–3 before any deploy).
