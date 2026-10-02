# Paste-ready prompt for a Claude cloud session (Opus 5.5)

Paste everything below the line into a new chat. It runs in **3 stages, one at a time**, and keeps a progress file in the repo so any later session (cloud or local) can resume.

---

You are working in the repo `scaler-education-journey` (Neuralascent: React `app/`, ASP.NET Core `api/`, Python FastAPI `ai-agent/`, Postgres 16 + pgvector, Docker, EC2 deploy via GitHub Actions + SSM). The repo owner is Raghuram Balaji.

## Authorization for this task (overrides repo CLAUDE.md and prior working-style notes, for this task only)
The repo's `CLAUDE.md` normally forbids Claude from editing files outside `info/.notes/`, `exercises/` and memory, and `info/history/07-ai-learning-agent.md` records that `ai-agent/` is normally hand-written by the owner. **For this task the owner explicitly authorizes you to edit files**, limited to:
- Stage 1: only create/update `info/.notes/OPUS-RUN-PROGRESS.md` and `info/.notes/OPUS-AUDIT-REPORT.md`. No other edits.
- Stage 2: lesson/chapter content and its source files, only for chapters the Stage 1 report marks as needing updates and the owner approved.
- Stage 3: files under `ai-agent/`, plus the minimum compose/env-example/deploy-script lines needed to wire it.
Do all work on a new git branch (e.g. `claude/opus-3-stage`). **Never push to `main`, never run or trigger a deploy (no `[deploy]` in commit messages), never touch EC2/AWS/SSM, never read or print secrets or `.env` values** (variable *names* only). Local WSL/Docker is the only runtime environment.

## How to work: 3 stages, ONE stage per turn
1. Do **only** the stage I name (start with Stage 1). When it is finished, **stop**, summarize in under 25 lines, and wait for me to say "go Stage N".
2. Before stopping, update `info/.notes/OPUS-RUN-PROGRESS.md` with: stage status, files changed, decisions made, what remains, and the exact next action. A fresh session must be able to continue from that file alone. Commit after each stage with a clear message.
3. If you are running low on budget mid-stage, stop at a clean checkpoint, write the progress file, and commit. Do not leave half-edited files uncommitted.
4. Verify, don't trust: when you claim something works, show the command and its output. Report failures plainly.
5. Do not invent facts. If something is ambiguous or undocumented, list it under "Questions for owner" instead of guessing.

## Context to read first (all stages)
- `info/history/00-INDEX.md`, then `01-…` and `07-ai-learning-agent.md` (full AI Tutor status, locked decisions, reviewer findings, gotchas), `04-deployment-infra-and-ops.md` before touching deploy/DB. These were consolidated 2026-09-30; originals are recoverable via `git show 9e6d03f:<path>`.
- `info/.notes/dotnet-to-python-migration-PLAN.md` (a separate track: .NET→Python migration, renamed from the earlier Java version on 2026-10-02; `ai-agent/` stays Python; do not touch `api/` beyond what's strictly required).
- `info/.notes/Neuralascent_Master_Reference_Guide_Updated.md` (lesson authoring contract) and `info/.notes/Neuralascent_Local_LLM_Ingestion_Prompt.md`.
- All of `ai-agent/`, `docker-compose.yml`, `docker-compose.dev.yml`, `.env.example`, `scripts/deploy-single-ec2.sh`, `.github/workflows/deploy-api.yml`, `app/default.conf.template`.
- `info/website-reference/machine-coding/` (PDF lecture material plus `0.Exercises` and `0.MCQ's`) and the rest of `info/` (skim the tree first; do not bulk-read multi-MB files or zips).

## Known facts (verified 2026-10-01; re-verify against the code, they drift)
- `ai-agent/` has: `main.py` (lifespan opens/closes an `AsyncConnectionPool`), `config.py` (fail-fast env reads), `auth.py` (HS256 JWT, issuer+audience, Bearer or `na_auth` cookie), `db.py` (pool with `register_vector_async`), `migrate.py` + `migrations/001,002`, `observability.py` (Langfuse, network call at import), echo agent (Pydantic AI → Muse) and echo graph (LangGraph), routers `health`, `identity` (`/me`, authed), `test_agent` (`/echo`, **no auth**), `test_graph` (`/agent_test`, **no auth**).
- Local WSL stack is healthy; `content_chunks` + `schema_migrations` exist locally; EC2 has the `vector` extension enabled but no `content_chunks`/`schema_migrations`, and its SSM env has `DATABASE_HOST/NAME/USER/PASSWORD/PORT` but **no `DATABASE_URL`**.
- Known defects to confirm and fix in Stage 3: (a) `migrate.py` opens the pool whose `configure=register_vector_async` fails when the `vector` extension doesn't exist yet, so a fresh DB cannot be migrated (chicken-and-egg); (b) `migrate.py` runs all files inside one outer transaction in practice (identical `applied_at`), contradicting its intent of one transaction per file; (c) `/echo` and `/agent_test` are unauthenticated paid-LLM routes proxied publicly by nginx; (d) `DATABASE_URL` is required by `config.py` but not produced by the deploy script; (e) `observability.py` and `config.py` fail at import, and the deploy `rollback()` deletes the crashed container before logs can be read; (f) no tests, no CI for Python; (g) the tracker's `/health` nginx override on the tutor server block shadows FastAPI's `/health`; (h) Muse model id/base URL hard-coded in `echo_agent.py`.
- Content data: prod has 298 lessons (277 `Draft`, 21 `Published`); local has 239 (231 Draft, 8 Published). `Draft` rows have real bodies (hundreds >3000 chars with the full finished-lesson marker). "Published" is a manual human-review gate, so **never change `content_status`** and never write to any database. MCQs now live in tables `mcq_questions`, `mcq_options`, `mcq_presentations`, `mcq_attempts`.
- Locked decisions you must respect: embeddings BAAI/bge-m3 (1024-d) + bge-reranker-v2-m3 via DeepInfra (no model swaps); orchestration = LangGraph for the tutor; Pydantic AI for agents; Langfuse Cloud; Muse primary / Nova Micro routing / Gemini judge; HNSW index; hybrid dense+tsvector retrieval. Do not re-open these.
- Credentials: Muse, Langfuse, and (later) DeepInfra keys are env-only. Never hard-code or echo them. Add new vars as unquoted names in `.env.example` with placeholders.

## STAGE 1 — Audit (read-only; writes only the two `info/.notes/OPUS-*` files)
1. Scan the whole workspace and `info/`, including `info/website-reference/machine-coding/` (list what's there: lectures, `0.Exercises`, `0.MCQ's`; extract the topics each PDF covers without reproducing copyrighted text).
2. Produce `info/.notes/OPUS-AUDIT-REPORT.md` with:
   - **A. Chapter/lesson update candidates:** compare the machine-coding material and `info/` sources against the lessons/exercises/MCQs already seeded in `api/Data/*SeedData.cs`, `exercises/`, `api/Data/mcq-migration-data.json`. List each chapter that is missing, thin, stale, inconsistent with the Master Reference Guide, or lacks exercises/MCQs, with evidence (file + what's missing) and a priority. Do not edit anything yet.
   - **B. `ai-agent/` production-readiness gap list:** every defect above (confirm or refute each with evidence) plus anything new you find (security, config, errors, migrations, tests, CI, observability, Dockerfile, healthchecks, dependency pins). Rank by severity.
   - **C. Proposed Stage 2 and Stage 3 work lists**, small enough to complete in one session each, in dependency order, with the acceptance check for each item.
   - **D. Questions for owner** (decisions only the owner can make, e.g. ingest rule Published-vs-Draft, where `migrate.py` runs in prod, how `DATABASE_URL` is produced).
3. Update `OPUS-RUN-PROGRESS.md`, commit, stop.

## STAGE 2 — Chapter updates (only after I say "go Stage 2")
Implement only the approved Stage 1 section-A items, following the Master Reference Guide and the existing seed-data/exercise conventions. For `exercises/`, never modify an exercise that is already wired and working; only add new ones or fix ones I flag. Hand-authored AI-vertical curriculum content (lessons about AI topics) is out of scope: do not write it. Never flip `content_status`. Validate what you can locally (build the API image / run the relevant tests / `verify-new-exercises.sh`) and show the output. Update the progress file, commit, stop.

## STAGE 3 — `ai-agent/` production hardening (only after I say "go Stage 3")
Implement the approved Stage 1 section-B items on the WSL/Docker path first. Required outcomes unless I told you otherwise:
- `migrate.py` works on a brand-new empty database and is truly one-transaction-per-file and idempotent; the app pool and the migration runner no longer deadlock on the missing `vector` type.
- No unauthenticated route can call a paid model; scaffold routes either require `get_current_user` or are removed; add a simple per-user rate limit hook point.
- `DATABASE_URL` is handled safely (special characters in the password must not break it) and works for both compose and the deploy script's `DATABASE_*` variables, **without** touching EC2.
- Config: provider model id/base URL moved to `config.py`; add `DEEPINFRA_API_KEY` as an optional var (not required until used); clear startup errors instead of tracebacks at import.
- A `tests/` directory with pytest covering auth (valid/expired/wrong-issuer token), health, migrations idempotency (against a throwaway pgvector container), and the unauthenticated-route regression; a minimal CI job for Python lint + tests (do not trigger a deploy).
- Dockerfile/compose hygiene: non-root user, pinned deps, `depends_on: database` health condition for `ai-agent`.
- Prove it: rebuild with `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build ai-agent`, show `/health`, `/me` (401 without token, 200 with a locally signed test token), test run output, and `migrate.py` on a fresh DB.
Do **not** start RAG ingestion (chunking/embedding/retrieval) in this task. List it as the next phase. Update the progress file with exact EC2 follow-up steps (for the owner to run later), commit, stop.
