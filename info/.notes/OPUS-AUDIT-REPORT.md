# OPUS Stage 1 Audit Report

Date: 2026-10-01 · Branch: `claude/opus-3-stage-d88sa1` · Scope: read-only audit (this file and `OPUS-RUN-PROGRESS.md` are the only writes).

**Method.** Five parallel Sonnet sub-agents audited: (1) machine-coding material, (2) seeded lessons vs sources, (3) `ai-agent/` code, (4) deploy/compose/CI, (5) the `info/` tree. The orchestrator re-verified the high-severity `ai-agent/` and deploy claims directly in the code (marked **[verified]**). Everything else is sub-agent evidence from file reads; **nothing was executed** (no containers, no DB, no network), so runtime behaviour is inferred from code. The orchestrating model for this run was Sonnet 5.5, not Opus 5.5 (cloud launch setting did not take effect).

Secrets: no secret values were read or printed. Variable names only.

---

> **Correction (Stage 2 re-verification, 2026-10-01):** two Stage 1 claims below were wrong. (1) "Java L2/L3 have empty bodies" is false: both cases exist as C# `or` patterns (`"02-oop-1-intro-lab" or "02-oop-classes-objects"`, ...) and hold 1,025 and 1,385 words; the audit grep missed them. (2) "No BookMyShow exercise anywhere" is false: `0.Exercises` has 4 BMS zips; none was wired to a lesson. The other items were re-confirmed. See `OPUS-RUN-PROGRESS.md`, Stage 2.

## A. Chapter / lesson update candidates

### A1. Machine-coding (module 5 `applied-machine-coding`, `api/Data/JavaVerticalSeedData.cs` ~L627)

Source folder `info/website-reference/machine-coding/`: 181 files / 51 MB — 15 PDFs, 15 `lesson_*.txt` revision notes, `0.Exercises` (68 solution zips + 68 screenshots), `0.MCQ's` (15 screenshots, all Parking Lot Code 2). PDFs 3.1–3.8 are image scans (0 extractable words); topics were taken from `info/.notes/scaler-raw-notes/pdfs-transcribed` and `companion-notes`.

Topic order covered: approach to design problems (3.1) → Tic Tac Toe (3.2–3.4) → Parking Lot (3.5–3.7) → BookMyShow (3.8, Code_BMS_1, Code_BMS_3) → Splitwise (Design, _1, _3).

| Pri | Chapter | Evidence | Gap |
|---|---|---|---|
| **High** | `22-machine-coding-splitwise` (2229 w) | No exercise wired; exercises exist unlinked: `exercises/practice-pool/java/splitwise-create-delete-group`, `splitwise-manage-group-members`; Python create-delete-group / settle-up; zips `Group_mgmt-1/2`, `settle_expenses` | Wire existing exercises; MCQs (6) are all `LLM_GENERATED` |
| **Med-High** | `21-machine-coding-bookmyshow` (1953 w) | No BMS exercise anywhere in repo; no BMS exercise zip in `0.Exercises`; MCQs (6) all `LLM_GENERATED` | Author new exercise; replace/augment MCQs if platform MCQs exist |
| **Med** | `24-machine-coding-hotel-management` (629 w, thin) | Siblings are 1500–2100 w; only exercise templates in `scaler-raw-notes/exercise-templates-batch4`, no PDF; 4 exercises wired | Expand body |
| **Med** | `17-machine-coding-capstone` (357 w, thin; lives in Spring module) | 6 MCQs, no exercises | Expand or merge |
| Low-Med | Unwired Parking Lot exercises | `python-additional-services-at-parking-lot`, `manage-wait-list-for-a-restaurant` in practice pool, linked to no lesson | Decide whether to wire |
| Low | `18`, `19`, `20` | Complete (1911 / 1609 / 1587 w); 6 / 6 / 15 MCQs; 0 / 2 / 2 exercises | None required |
| Low | Source hygiene | `3.8__Code_BMS_1 (1).pdf` is byte-identical to `3.8__Code_BMS_1.pdf`; "3.8" used for 3 files; `lesson_5].txt` stray bracket; `lesson_9.txt` is a 365-byte URL stub; duplicate zip `…86d37a1e94ef71c7 (1).zip`; `__MACOSX` junk | Cleanup |
| Info | Missing source | No `Code_BMS_2` / `Splitwise_2` PDFs (only `lesson_11.txt` / `lesson_14.txt` cover them) | See Questions |

### A2. Seeded lessons vs Master Reference Guide

Counts (seed files only; DB not queried): Java vertical 85 lessons (+1 `structured-concurrency` from `ChapterSeedData`): 27 in 6 `java-spring-lld` modules + 58 in 3 "expanded" standalone courses. FDE: 152 lessons (104 core + 48 electives), no orphan/duplicate slugs. 0 AI-vertical lessons seeded (not audited, per scope). `lessonInteractions.js` 181 keys; `mcq-migration-data.json` 179 groups / 1,182 questions (identical to `scripts/mcq-migration-data.json`). 67 Java exercises in 18 lessons, all wired and structurally sound.

| Pri | Item | Evidence |
|---|---|---|
| **High** | Java L2 and L3 have **empty bodies** in the seed | `GetAuthoredLessonContent` has no case for `02-oop-1-intro-lab`, `03-oop-2-access-modifiers-encapsulation` (calls at `JavaVerticalSeedData.cs` L297, L313, L329). A complete 1,311-word L3 note exists at `info/.notes/final-notes/lesson-3/` |
| **High** | MCQ answer bias | Correct option is the longest in 94 % of 1,182 questions; key `b` is correct in 60 %; FDE uses only a/b (12 c, 0 d). Server shuffles order, which fixes position bias but not the length tell. (Aggregate only; per-source split not measured.) |
| **High** | 58 templated lessons thin and effectively locked | Expanded modules (databases-sql 13, high-level-design 21, data-engineering 24) are 88–202 w, no MCQs/exercises/interactions. Template emits all three required headings, so `NeedsLessonContent` will not let them be upgraded without a DB reset (write-once gotcha in CLAUDE.md). `info/.notes/cleanup-redundant-expanded-modules.sql` suggests these may be unwanted |
| Med | Spring module L14–17 | 311–356 w, no code/exercises, 24 MCQs |
| Med | Atlas links | 9 of 10 `ConceptNextLesson` slugs in `KnowledgeAtlasSeedData.cs` match no seeded slug |
| Med | Code/exercise coverage | 88 of 104 FDE core lessons have no fenced code; FDE has 0/152 exercises; Java L9, L13, L18, L21, L22 have no exercises; L14–17 (1,300–1,700 w) have no code block |
| Med | Tier misses | Concurrency/generics L6–L10 < 1,200 w; `structured-concurrency` 260 w, off-contract headings, LectureNumber 9 clashes with L9, no MCQs |
| Med | FDE has no backfill path | Existing rows keep the old generic template lacking required headings |
| Low | Stale aliases | `lessonInteractions.js` keeps `02-oop-classes-objects`, `03-oop2-encapsulation-inheritance`, duplicating 22 question ids |
| Low | Inconsistencies | 6 Java seed titles differ from body H1; no lesson 23 (OrderIndex 6 skipped); "Lesson 14–17" numbering repeats across modules 4 and 6; expanded-module badges 8/15/17; `exercise.json` has no SOURCE_TYPE |
| Low | Repo hygiene | 54 tracked `._*` files under `exercises/practice-pool/java/estimate-delivery-time-…`; 29 MB `python-3.13.15-amd64.exe` committed in `.notes/scaler-dump/Exercises/`; `phase2-final*.diff` UTF-16; `STATUS.md` contradicts itself (says 170 interaction keys, actual 181); two practice-pool entries titled `java-17-test_case`; `._`/`__MACOSX`/`.DS_Store` junk |

Clean checks: all 152 FDE note bodies equal seeded text (apart from markers); FDE MCQ counts match `lessonInteractions.js`; every `exercise.json` path and test method resolves; no banned filler phrases; `find_missing_lessons.sql` expectations match the JSON.

### A3. Unseeded / unledgered sources in `info/`
- `scaler-raw-notes/exercise-templates-batch4` (9 templates: tictactoe-undo, hotel-*, database-factory, integrate-cloud) — wired status unverified.
- `scaler-raw-notes/companion-notes` (14 machine-coding notes) and `hackmd` (61 notes): no ingestion ledger found (FDE has `STATUS.md`).
- `final-notes/lesson-1` v2 (735 lines vs v1 344) may not be reflected in the seed.
- Nothing in `info/` covers databases-sql, high-level-design, data-engineering; no sources for the Spring module; Java L14 SOLID has one handwritten note; `pdfs-transcribed` lacks `Adapter___Facade___3rd_Aug`.
- `AI-helper/` (20 files) is AI-vertical material: hand-authored by the owner, **not** a candidate for any generated content.

---

## B. `ai-agent/` production-readiness gaps (ranked)

Known defects (a)–(h) — all **confirmed**:

| Sev | ID | Finding | Evidence |
|---|---|---|---|
| **Critical (prod)** | (d) | `DATABASE_URL` required but never produced by the deploy path | `ai-agent/config.py:12-14` raises if unset **[verified]**. `scripts/deploy-single-ec2.sh` `start_ai_agent` (~L239-252) passes `--env-file` plus `JWT_SIGNING_KEY/ISSUER/AUDIENCE/COOKIE_NAME` only **[verified]**. `deploy/single-ec2.env.example` documents `DATABASE_HOST/NAME/USER/PASSWORD/PORT`, no `DATABASE_URL`, `MUSE_AI_API_KEY`, `LANGFUSE_*`. Works in prod only if the SSM-sourced env hand-contains them (unverifiable here). Only `docker-compose.yml:120-124` builds it |
| **High** | (c) | `/echo` and `/agent_test` are unauthenticated paid-LLM routes, publicly proxied | `routers/test_agent.py` and `test_graph.py` have no `Depends(get_current_user)` **[verified]**; `app/default.conf.template` tutor server block `location /` proxies everything to `ai-agent:8000` with no auth, rate limit, or body limit **[verified]**. `/echo` calls Muse per request (`echo_agent.py:27`). `/docs` and `/openapi.json` also public |
| **High** | (a) | Fresh DB cannot be migrated (chicken-and-egg) | `db.py` pool `configure=register_vector_async` **[verified]**; `migrate.py` opens that same pool **[verified]**; `vector` extension only created by `migrations/001`. First connection's configure step fails. Inferred from code, not executed |
| **High** | (e) | Import-time failures + rollback destroys evidence | `config.py` raises at import; `observability.py:4-6` does `get_client()` + `auth_check()` (network) at import **[verified]**. `rollback()` runs `docker stop`/`docker rm` on api, ai-agent, app with output to `/dev/null` before any `docker logs` **[verified]**; restores swallowed with `|| true`. If no previous ai-agent image exists, none restarts, and nginx `proxy_pass http://ai-agent:8000` may fail to resolve, risking the main site (inferred) |
| **High** | (f) | No Python tests, no Python CI | No pytest in `requirements.txt`; `.github/workflows/deploy-api.yml` runs `dotnet test` + frontend lint/test/build only, then builds/pushes the ai-agent image unchecked; only trigger is `[deploy]` on head commit or manual dispatch; no PR CI |
| **High** | new | Raw password in `DATABASE_URL` | `docker-compose.yml:124` interpolates `${POSTGRES_PASSWORD}` unencoded; `@ : / # %` break the URI. Build conninfo from separate parts (also fixes (d)) |
| **High** | new | Container runs as root; no `.dockerignore` in `ai-agent/` | Dockerfile has no `USER`, no `HEALTHCHECK` **[verified]**; `COPY . .` can bake a local `ai-agent/.env` into the image |
| **High** | new | `/health` does not touch DB; no `depends_on: database` for ai-agent in compose; pool opened without waiting | `docker-compose.yml` ai-agent service |
| Med | (b) | One outer transaction, not one per file | `migrate.py:28` `conn.transaction()` is a savepoint once the connection already has an open txn (the preceding SELECT), commit happens at pool-connection exit **[verified in code]**. A failure at file N rolls back files already printed "applied". No advisory lock; `Path("migrations")` is cwd-dependent. Nothing in any script/workflow/compose/Dockerfile invokes `migrate.py` |
| Med | new | JWT validation | `auth.py:21-27`: PyJWT not told to `require` `exp`/`iss`/`aud`, so a token without `exp` never expires; no minimum key length (.NET enforces 32 bytes at `api/Program.cs:427`); `/me` returns raw claims; cookie auth has no CSRF consideration |
| Med | new | Deploy rollback gaps | Does not undo `--migrate`/seed; restore failures swallowed but still exits non-zero, leaving site down |
| Med | new | Prod DB image | `deploy-single-ec2.sh` reuses the existing DB container; if it is plain Postgres `CREATE EXTENSION vector` fails regardless of (a). Running image not checked (owner says `vector` is enabled on EC2) |
| Med | new | Floating base image `python:3.12-slim`; only direct deps pinned, no lock/hashes | Dockerfile, `requirements.txt` |
| Med | new | nginx tutor block | No `limit_req`, no `client_max_body_size`; default 60 s read timeout short for LLM calls |
| Med | new | No error handling/timeouts on Muse call, no logging config, Langfuse not flushed on shutdown, uvicorn without `--proxy-headers` | `echo_agent.py`, `main.py` |
| Med | new | No CORS middleware | Will matter once a separate frontend calls with cookies |
| Med | new | CI weaknesses | Only head commit checked for `[deploy]`; short-lived `GITHUB_TOKEN` embedded in SSM send-command params (`deploy-api.yml` ~L163-164); `runner/java-spring` referenced by compose but not built in CI |
| Low | (g) | nginx `/health` override shadows FastAPI `/health` on the tutor block | Template tutor block returns `200 "healthy"` itself **[verified]**; public monitor stays green when ai-agent is down |
| Low | (h) | Model id / base URL hard-coded | `echo_agent.py:11` (`muse-spark-1.3`), `:14` (`https://api.meta.ai/v1`) |
| Low | new | `.env.example` hygiene | `DATABASE_URL=provide_your_db_url` placeholder misleading; trailing spaces on lines 16 and 26 (copied `LLAMA_API_KEY` gets a trailing space); `JWT_ISSUER/AUDIENCE/COOKIE_NAME`, `LANGFUSE_*`, `EXERCISE_RUNNER_IMAGE_SPRING`, `LLAMA_*`, `BUDGET_*` not all listed |
| Low | new | Compose coupling | `app` waits on ai-agent healthy, so a tutor outage blocks the whole frontend; nginx upstream depends on container name `ai-agent`; dev compose publishes both 80 and 8080 for app |
| Low | new | Test file naming | `routers/test_*.py` will collide with pytest collection |
| Low | new | API container mounts `docker.sock` (by design for the runner; root-equivalent if API compromised) | `docker-compose.yml:~94` |

### Repo-root hygiene and sensitive-data flags (deploy audit)
- **`.env.example.orig` is tracked** and holds an `ADMIN_PASSWORD` that does not look like a placeholder and differs from the one in `.env.example` (both non-placeholder-looking, 17 chars in the `.orig`). Whether either is a real credential is **unknown**; if it was ever used, rotate it. Values not printed here.
- Tracked leftovers: `.env.example.orig`, `docker-compose.yml.orig` (unresolved merge-conflict markers, no ai-agent, old postgres image), `task_tracker.md.orig`, four `api/**/*.cs.orig` (copied into the API Docker build context), 169 tracked files under `api/bin` + `api/obj`.
- `ec2-s3-diff.txt` (UTF-16 git diff) contains an S3 bucket name incl. AWS account id and SSM parameter paths, no keys/tokens.
- Junk/one-offs at root: `payload.json`, `get-docker.sh` (158-byte stub), `parse_tasks.py` (points at deleted `info/04-fde-curriculum-tracker.md`), `refactor_api.py` (hard-coded `/home/ubuntu`).
- `app/.env` and `app/.env.production` are git-tracked; contents **not read** — owner should confirm they hold only `VITE_*` values.
- `.raghu-personal/` (tracked) holds resume PDFs and a personal-details txt (PII in a repo). Pattern-grep matched three `info/` paths for possible secrets (`scaler-raw-notes/hackmd/53-ByTltJQ_Mg.md`, `fde-lessons/phase-24-…` and `phase-25-…`, `website-assignments-reference/phase4-final-complete.diff`); values **not reviewed**, may be code-sample false positives.

---

## C. Proposed work lists

### Stage 2 — chapter updates (one session; each item needs owner approval first)
Dependency order; none flips `content_status`; AI-vertical content excluded.
1. **Java L2/L3 bodies**: add `GetAuthoredLessonContent` cases using `final-notes/lesson-3` (and the L2 source) per Master Reference Guide. *Accept:* API image builds; seeded body contains the three required headings; `ContentStatus` handling untouched.
2. **Splitwise (L22)**: wire existing `splitwise-*` exercises; do not alter already-wired exercises. *Accept:* `info/.notes/verify-new-exercises.sh` passes; exercise appears under L22.
3. **BookMyShow (L21)**: create a new exercise under `exercises/java/java-lld/applied-machine-coding/` (stub + tests + reference solution). *Accept:* verify script passes.
4. **Expand L24 hotel-management** and **L17 capstone** to tier. *Accept:* word count in tier, three headings present.
5. **Fix dangling `ConceptNextLesson` slugs** (data-only). *Accept:* all slugs resolve against seeded slugs (script check).
6. *(Only if approved)* MCQ answer-length rebalancing for FDE `LLM_GENERATED` items.

Deferred (needs owner decisions): expanded-module fate, FDE exercises/code, Spring module L14–17 depth.

### Stage 3 — `ai-agent/` hardening (one session)
Order: 1 → 2 → 3 → 4 → 5 → 6 → 7.
1. **Config**: `config.py` clear startup errors (no import tracebacks); model id/base URL moved into config; `DEEPINFRA_API_KEY` optional; build DB conninfo safely from `DATABASE_URL` **or** `DATABASE_HOST/NAME/USER/PASSWORD/PORT` (special-char safe). *Accept:* unit tests for both input shapes with `@:/#%` in password.
2. **`observability.py`**: lazy init, no network at import. *Accept:* `import` succeeds with no network.
3. **`migrate.py`**: dedicated connection without vector registration, advisory lock, one real transaction per file (explicit `autocommit`/`BEGIN`), idempotent, absolute migrations path. *Accept:* run twice on a throwaway pgvector container: first applies 001+002 with distinct `applied_at`, second skips; failing file leaves earlier files committed.
4. **Auth**: require auth on `/echo` and `/agent_test` (or remove); PyJWT `require=[exp,iss,aud]`; minimum key length; per-user rate-limit hook point; disable `/docs` in prod. *Accept:* regression tests: 401 without token, 200 with valid token.
5. **Tests + CI**: `tests/` (auth valid/expired/wrong-issuer, health, migration idempotency, unauth-route regression); rename/avoid `routers/test_*.py` collisions; CI job for ruff + pytest on PRs (no deploy trigger). *Accept:* green run output shown.
6. **Docker/compose**: non-root user, `.dockerignore`, `HEALTHCHECK`, pinned base tag, `depends_on: database` health condition, `/health` with optional DB check. *Accept:* `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build ai-agent` healthy; `/health` 200; `/me` 401 without token, 200 with locally signed token; `migrate.py` on a fresh DB.
7. **Deploy script (minimum lines)**: construct `DATABASE_URL`/pass `DATABASE_*`, `MUSE_AI_API_KEY`, `LANGFUSE_*` names; capture `docker logs` before `rollback()` removes containers; `.env.example` placeholders (names only). *Accept:* `bash -n` and shellcheck on the script; no EC2/SSM contact.

Not in scope: RAG ingestion (chunking/embedding/retrieval) — next phase. Progress file will carry exact EC2 follow-up steps for the owner.

---

## D. Questions for owner

1. **Repo secrets.** Is the `ADMIN_PASSWORD` in `.env.example.orig` (and the different one in `.env.example`) real? Rotate if ever used. May I remove tracked `*.orig`, `api/bin`, `api/obj` in a later cleanup?
2. **`app/.env`, `app/.env.production`** tracked: confirm `VITE_*` only. Three `info/` paths flagged by secret-pattern grep need your value-level review.
3. **`.raghu-personal/`** (resume, personal details) stays tracked in a repo on GitHub?
4. **Prod env.** Does the SSM-sourced `/etc/studytracker/api.env` already contain `DATABASE_URL`, `MUSE_AI_API_KEY`, `LANGFUSE_*`? How should `DATABASE_URL` be produced going forward (compose-style interpolation vs script-built)?
5. **Where does `migrate.py` run in prod**: deploy script step, container entrypoint, or manual? Is the prod DB container a pgvector image?
6. **Ingest rule** for RAG: Published only, or Published + Draft (298 prod lessons: 277 Draft, 21 Published)?
7. **Authoritative backend direction:** `dotnet-to-java-migration-PLAN.md` (Java/Spring, `ai-agent/` stays Python) vs `info/history/00` and `08` (which frame the migration as Python/FastAPI). `ai-agent/` is Python in both; the conflict concerns `api/`.
8. **Lesson 23** gap: intentional? Are `Code_BMS_1___4th_Sept` and `3.8__Code_BMS_1` two versions? Where are `Code_BMS_2` / `Splitwise_2` PDFs? Do the 68 screenshots map 1:1 to the 68 zips? Parking Lot MCQ count 14 or 15?
9. Are the 3 expanded Java modules (58 lessons) intended or the "pollution" `cleanup-redundant-expanded-modules.sql` describes? Which word tier applies to FDE lessons?
10. Are Java L2/L3 DB-only on purpose? Should the practice pool and 20 unwired Python zips be wired in? Is the MCQ length bias limited to LLM-generated FDE items?
11. Should `ai-agent` rate limiting be per-user in-process or at nginx?
12. Is unauthenticated `/health` through the public tutor host required, or should nginx proxy `/health` to FastAPI?
13. May the exercise-template batch4 and `final-notes/lesson-1` v2 be checked for ingestion status in Stage 2?
