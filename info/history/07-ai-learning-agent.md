# 07 — AI Learning Agent ("AI Tutor", Python vertical) — PRIMARY PROJECT

> **Read this first for anything under `ai-agent/`, `tutor.neuralascent.top`, RAG, Langfuse, pgvector or the
> Python side of the platform.** Consolidated 2026-09-30 from 12 source docs (see `00-INDEX.md`).
> Status below was checked against the actual `ai-agent/` source at repo HEAD `9e6d03f` (2026-09-22),
> not just against the old trackers.

**Project name variants that all mean this project:** "AI Learning Agent", "AI Tutor", "AI Tutor Python vertical",
"AI Copilot" (early planning name), "the learning support agent", "`ai-agent/`".
It is **AI integration (site infrastructure)**, *not* AI-vertical curriculum content (see `01-…` §Scope rules).

---

## 0. Status snapshot (as of 2026-09-30; code last touched 2026-09-21)

| Area | State |
|---|---|
| Phase 0 — infra & routing scaffold | ✅ Done and verified in prod (JWT trust bridge live, 2026-09-12/13) |
| Phase 1.1 — project scaffold | ✅ Done, verified locally (Compose) **and** on EC2 (2026-09-20) |
| Phase 1.2 Phase A — DB pool, `content_chunks` schema, idempotent migrations | ✅ Done, verified against local dev DB (2026-09-21). **Not run in production** (see §5.3) |
| Phase 1.2 Phases B–E — extractors, chunking, embedding, `ingest.py` | ❌ Not started — **no code exists** |
| Phase 1.3 retrieval, 1.4 tutor agent, 1.5 eval harness, 1.6 TS frontend | ❌ Not started |
| Phase 2 / 3 / 4 | ❌ Not started |
| Work since 2026-09-21 | None on `ai-agent/`. The 2026-09-22 handoff prioritised exercise-grading fixes (WSL2 → EC2), and only *then* a return to the AI Tutor (see `04-…`) |
| Target dates | Phase 1 mid-Oct 2026 · Phase 2 late Nov · Phase 3 late Dec · interviews Jan 2027 (Phase 1 date is at risk — Phases B–E + 1.3–1.6 remain) |

Doc staleness warning: three source docs still said "design phase, implementation not started" (handoff §header,
ARCHITECTURE §header, `neuralascent-work-status.md`, all dated 2026-09-08). That was true then and is **wrong now**.

---

## 1. Working rules for any assistant (LOCKED — read before touching anything)

1. **`ai-agent/` Python is hand-written by the user.** This started as "Python AI logic only" (2026-09-07), was widened on
   2026-09-15 to *all AI-Tutor-supporting work* (incl. the `docker-compose.yml` pgvector swap and `scripts/deploy-single-ec2.sh`),
   and re-confirmed on 2026-09-21 when the user chose "keep the rule, walk me through it" over speed. Reason: AI-assisted coding has
   eroded raw coding fluency that interviews test.
2. **Claude = architect / reviewer / concept teacher only.** Explain the concept, point at file + line + shape of the fix, review
   afterwards. **Do not** write scaffolds, copy-paste implementation docs, diffs or Local-LLM/Gemini prompts for this code — not
   even framed as "just a doc". Accepted workaround for "show me code": a toy example with deliberately different names, shown in chat,
   never written to disk. Live incident help (diagnostic `psql`/`docker`/`pg_dump` commands) is fine.
3. **Teaching split:** do *not* teach Python syntax/idioms (user has C++/C#/Java). *Do* teach backend + AI-engineering concepts from
   scratch, in real depth, when a concept is about to matter (JWT, DI, vector DB, RAG stages, LangGraph state model, Docker image-vs-volume…).
   Reason: Jan-2027 interview prep. If something is ambiguous or undocumented, **ask, don't fabricate**.
4. **Frontend/UX is AI-assisted** (Gemini prompts) and is a *fresh TypeScript build*, not the existing `app/` JSX.
5. **AI-vertical curriculum content** (lessons about AI topics, e.g. Model Economics Matrix) is hand-authored only — no prompts, ever.
6. **Verify, never trust a self-reported "done"** (lesson from the 2026-09-22 exercise-grading work; see `04-…`).
7. Doc-check habit that paid off: verify library APIs against live docs (caught pydantic-ai 2.x removing `instrument=True`, and the
   hard `langchain` import inside `langfuse.langchain`). Training-data knowledge of 2026 library versions is unreliable.

---

## 2. Who / why / interview story

- **Owner:** Raghuram Balaji — Coforge (India), ~30 LPA; ~2 yrs AI, 5 yrs Java, 4.5 yrs technical-artist experience.
- **Goal:** ₹40–60+ LPA Applied/GenAI Engineering roles (Accenture/TCS/Infosys AI units, mid-size product cos.), job search **Jan 2027**;
  build window Sep–Dec 2026.
- **Why one project:** originally three (A: RAG tutor, B: content-quality audit, C: code-execution grounding — from the market playbook,
  see `05-…`). Decided **2026-09-07** that one deep unified system beats three tutorial-grade ones.
- **Interview clusters covered:** RAG depth, agentic workflows, evaluation, cost governance, tool use, **MCP** (asked at Accenture Dec 2025),
  multi-agent with justified separation, observability (OTel + Langfuse), production hardening, LLM-as-judge, Stripe (test-mode) ops demo.
- **Rehearsal sentences:**
  - P1: "Naive RAG scored 0.62 context precision / 0.71 faithfulness on my 100-question golden set; AST-aware chunking + bge cross-encoder
    reranker moved them to 0.84 / 0.88." *(numbers are targets/illustrations until measured)*
  - P2: "Five agents orchestrated via LangGraph; the assessment agent calibrates MCQ difficulty to mastery; the model cascade cuts per-session cost 60%."
  - P3: "Support agent shares RAG infra, swaps corpus+persona; red-teamed with 30 adversarial cases — 93% containment, zero injection successes; admin agent automates policy-compliant Stripe refunds."
  - Cascade: "Three providers — Muse for tutoring at $0.20/MTok out, Nova Micro on Bedrock for routing at $0.035/MTok (batch 50% off for evals), Gemini free tier as eval judge to avoid self-preference bias; ~$0.014/session."

---

## 3. LOCKED decisions (with dates and supersessions — do not re-litigate)

| # | Decision | Date | Notes |
|---|---|---|---|
| 1 | One unified AI Learning Agent replaces Projects A/B/C | 2026-09-07 | |
| 2 | LLM cascade: **Meta Muse Spark 1.3 Contributor** (primary, $0.10/$0.20 per MTok) · **Amazon Nova Micro** on Bedrock (routing/bulk, $0.035/$0.14; batch $0.0175/$0.07) · **Gemini free tier** (eval judge). Do not add providers/models without user approval | 2026-09-07 | Muse Contributor tier trains on prompts — accepted for public curriculum content. Muse reachable from India via UPI signup. Gemini 2.5 Flash-Lite shuts down 2026-10-16 → use current free Flash-Lite |
| 3 | Learner memory = **hybrid**: Postgres for L1 raw traces + L2 concept mastery (FSRS `next_review_at`); **Mem0** (self-hosted on Postgres/pgvector) for L3 free-text profile/misconceptions; LangGraph `PostgresSaver` for in-thread state | 2026-09-07 | LangMem rejected (59.8 s p95 retrieval in a third-party benchmark) |
| 4 | FDE exercise grading = LLM-as-judge with rubric (Phase 3; no auto-grading in v1) | 2026-09-07 | |
| 5 | **Embeddings: originally OpenAI text-embedding-3-large (09-07) → superseded 09-08 → BAAI/bge-m3** (dense 1024-d; also dense+sparse+multi-vector capable) + **bge-reranker-v2-m3**. Never swap the embedding model once the corpus is indexed (full re-embed) | 2026-09-08 | Local (Mac Studio) and API fallback must be the *same weights* |
| 6 | Local inference host: Mac Studio M1 Max 32 GB, reverse `autossh` tunnel to AWS (loopback-only port 9000→8001), `launchd` agent, restricted SSH key; used for **embedding+reranking only** (not the LLM tier). **Manual toggle, no auto-failover**: admin-panel `embedding_backend`/`reranker_backend` ∈ {local, api} + per-account `force_api_backend` for demos + Mac/tunnel health indicator; same `EmbeddingProvider`/`RerankerProvider` interface | 2026-09-08 | **Deferred (2026-09-13):** build/prove the full pipeline on the cloud API first; Mac/tunnel work only after cloud-only version is proven end-to-end |
| 7 | **Embedding/rerank provider now: DeepInfra** (`bge-m3` $0.01/M tok; `bge-reranker-v2-m3`) | 2026-09-13 confirmed 09-21 | Rejected: Bedrock Titan V2 (2× price), Cohere/Nova (10–13.5×), Amazon Rerank 1.0 (~10–125× dearer). Sarvam AI & Krutrim have no embedding models. AICredits.in = UPI proxy at ~10% markup if payment friction. User accepts prepaid-wallet non-refundable risk (~$5 loaded). **Do not re-raise.** Muse stays for higher-intelligence agent work regardless of "enterprise" concerns |
| 8 | Frontend = **fresh TypeScript build** (not `app/`); backend = **FastAPI** microservice | 2026-09-08 | |
| 9 | Staged cutover: `.NET` keeps `neuralascent.top` through Phases 0–2; new stack on `tutor.neuralascent.top`; Nginx flips domain in Phase 3 at feature+auth parity; .NET retired or narrowed. **This is the "Python migration"** — see `08-…` | 2026-09-08 | Auth not duplicated: FastAPI only *validates* .NET-issued JWTs |
| 10 | Orchestration: **LangGraph for the tutor**, LangChain for the (on-hold) Localization Lab pipeline, **CrewAI in neither** (optional 1-day disconnected sandbox for interview reasoning). See ADR summary §3.1 | 2026-09-18 | ADR-001 is *newly-constructed reasoning*, not retroactive history — its own honesty caveat |
| 11 | Observability: **Langfuse Cloud** (Hobby, 50K units/mo, host `https://us.cloud.langfuse.com`), not self-hosted, not LangSmith | 2026-09-19/20 | Re-verified with live 2026 data (2,300+ cos, 63 Fortune 500, acquired by ClickHouse Jan 2026) |
| 12 | Sequencing: Langfuse before Docker Compose integration (isolate variables) | 2026-09-19 | done |
| 13 | Compose files are **dev-only**; prod = GitHub Actions → GHCR → SSM → plain `docker run` (`scripts/deploy-single-ec2.sh`). `ai-agent` dev block has **no live-reload** (matches `api`/`app`) | 2026-09-20 | |
| 14 | `ai-agent/` config = plain `os.environ.get` in `config.py`; `pydantic-settings` upgrade optional/deferred | 2026-09-20 | |
| 15 | `echo_graph.py` / `echo_agent.py` are scaffold names; the real six-agent orchestrator must get a distinct name (`tutor_graph.py`/`orchestrator.py`) | 2026-09-19 | |
| 16 | Vector index: **HNSW** over IVFFlat; `search_vector` is a `GENERATED … STORED` tsvector (cannot drift); `module_id`/`concept_tags` denormalised onto chunks; `VECTOR(1024)` **not yet verified against a real DeepInfra response** | 2026-09-21 | confirm on first real embed call |
| 17 | Exercise ingestion source = `exercises/**/exercise.json` (+`solution/**/*.java`), **not** the `problems` table (5 rows, admin-entered). 65 exercises / 9 topics / 17 lessons at the time (`lessonSlug` → `lessons.slug`, string match not FK) | 2026-09-21 | Later sessions added more exercises; recount before relying on 65 |
| 18 | Lesson ingestion source = `lessons.content_body` where `content_status='Published'` (no lesson `.md` files exist on disk any more); MCQs live *inside* `content_body` (until the dynamic-MCQ DB schema — see below) | 2026-09-21 | |
| 19 | The "two planning tracks" (this architecture vs the "AI Copilot"/26-week/HLD-python-LangChain track) — in practice the ARCHITECTURE track won: all real work since 09-15 follows it. User never explicitly ruled; treat the copilot docs as superseded background | 2026-09-08→09-21 | §6 |

**Post-2026-09-21 platform change that affects ingestion (from the 2026-09-22 handoff):** MCQs moved from the static
`app/src/data/lessonInteractions.js` to DB tables `mcq_questions`, `mcq_options`, `mcq_presentations`, `mcq_attempts`
(1182 unique questions, 179 lesson groups). Decision #18's "MCQs embedded in `content_body`" and the tracker's "atomic MCQ chunking
from `content_body`" line therefore need revisiting: MCQ chunks should now come from those tables. Also lesson bodies were given `###`
(H3) hierarchy specifically so a RAG chunker can split on H2→H3→H4 (see `02-…`, content-hierarchy prompt).

### 3.1 ADR-001 summary (orchestration framework)
- **Tutor → LangGraph** because it has four real graph needs: conditional fan-out (router → Tutor/Support/Admin), cycles
  (`RETRIEVE → GRADE_EVIDENCE → GENERATE → VALIDATE → REPAIR`), persisted resumable state (progressive hint-disclosure tier per learner),
  human-in-the-loop interrupt (Admin Agent approval).
- **Localization Lab → LangChain** when off hold: pipeline is linear with two conditionals and no persisted state (Legacy MT → semantic cache →
  MT Optimize → QPS + COMET-Kiwi → auto-route). Fit: provider abstraction over vLLM's OpenAI endpoint, structured output for QPS, `PGVector` cache.
- **CrewAI → neither**: no honest home (Lab "roles" are human vendors); "multi-agent theater" is a named interview red flag.
  Interview answer = able to say why not, with hands-on grounding (optional ~1-day sandbox).
- **LangChain inside the tutor:** minimal and late — text-splitter/loader spot in ingestion only.
- **Reversal triggers:** tutor collapses to one agent with no loops → LangChain; Lab pipeline gains an in-pipeline human pause/repair loop → LangGraph.
- The `-python-LangChain` / `-JAVA-LANGCHAIN` / `-dotnet-Semantic-Kernal` chatbot HLDs are stack-variant drafts, **not** independent evidence for LangChain.

---

## 4. Target architecture (from ARCHITECTURE.md, condensed; design is largely unimplemented)

**Topology:** React/TS frontend → FastAPI service → LangGraph orchestrator (Profiler, Tutor, Assessment, Nudge, Support, Admin agents) ·
RAG engine (pgvector dense + tsvector sparse, cross-encoder rerank) · eval engine (DeepEval + RAGAS) · MCP tool registry · learner memory ·
Langfuse tracing · cost governor → Postgres 16 (pgvector) · LLM providers · Docker sandbox (JDK, no network, caps) for Java exercises.

**UX vision:** one conversational workspace, agent-driven mode transitions: Chat (default) → MCQ panel (chat minimises, hints in a non-intrusive
element) → Exercise mode (code editor + output, sandboxed run) → Support mode ("Need help?", different corpus/persona) → Admin view
(per-student progress, per-agent cost, AI resolution suggestions, automated-action log). Behaviour model: curriculum-aware, personalised,
proactive, grounded (citations), measurably effective.

**Agents:**
- *Profiler* — first login/periodic; skill vector, starting point, optional read-only git-repo analyzer; table `learner_profiles`.
- *Tutor (primary)* — every chat message; three-stage scaffold Investigate → Guide → Explain (DeepTutor-inspired); must cite lesson/section, refuse out-of-scope, detect prompt injection.
- *Assessment* — 4-option calibrated MCQs (LLM-judge validation: distractor plausibility, single correct answer, difficulty), persist good ones to `generated_mcqs`; Java exercises (problem+starter+tests); sandbox scoring.
- *Nudge* — scheduled (not per-message); FSRS/SM-2 review scheduling; inactivity / declining pass-rate / progress-summary messages.
- *Support* — different corpus (help docs/FAQ/known issues), account lookup, Stripe test-mode refund automation; red-team eval.
- *Admin* — resolution suggestions, pre-approved auto-actions only (e.g. refunds under threshold), anomaly alerts, human-in-the-loop for the rest.
- *Router* (LangGraph) — intent classification (Nova Micro): tutor | support | admin; complexity classifier simple→Nova Micro / complex→Muse.

**RAG pipeline:** query → (rewrite for multi-hop) → dense + sparse → Reciprocal Rank Fusion → bge cross-encoder rerank → parent-document expansion →
concept-prerequisite filter → context assembly with content-quality weighting.
Chunking: prose by heading hierarchy (H2→H3→H4); Java code AST-aware via tree-sitter ("cAST"); MCQs atomic; exercises = manifest (atomic) + evidence entries (atomic) + solution code (AST).
Per-chunk metadata: `lesson_id, module_id, section_path, chunk_type (prose|code|mcq|exercise*), concept_tags, content_quality_tier, embedding, tsvector`.
Corpus reality (2026-08/09): ~17 hand-authored Tier-1 lessons + ~165 thin drafts — quality-tier weighting needed to stop retrieval favouring the 17.
By 2026-09-01 the FDE vertical alone has 152 authored lessons (see `02-…`), so the Tier-1/Tier-2 gap is smaller than these notes assume; recheck `content_status` counts.

**Concept prerequisite DAG:** extracted from Java LLD curriculum, table `(concept_id, prerequisite_concept_id)` (a `concept_prerequisites` table already exists in prod, seen in the 2026-09-13 backup TOC).

**Learner memory tables (planned):** `learner_profiles`, `concept_mastery` (score, attempts, pass_rate, last_assessed_at, next_review_at, misconception_notes[]),
`interaction_traces` (agent, type, summaries, tokens, cost, latency), `generated_mcqs`.

**Evaluation (5 categories):** RAG golden set (~80–120 hand-written Q/A; single-lesson ~30 / cross-lesson ~20 / code ~20 / conceptual ~20; RAGAS context precision/recall,
faithfulness, answer relevancy; thresholds faithfulness ≥0.75, relevancy ≥0.80, precision ≥0.70, recall ≥0.80; baseline = naive 512-token chunks, dense, top-5, no rerank; five
interventions measured one at a time: AST+hierarchy chunking, hybrid, rerank, parent-doc, query rewriting) · MCQ quality · tutoring effectiveness (learning gain, time-to-mastery, retention) ·
support red-team (~30 cases: 10 injection, 5 off-topic, 5 hallucination, 5 emotional, 5 edge) · agent-level metrics (latency, cost, error rate, router accuracy).

**Cost governance:** cascade table (routing/simple→Nova Micro; standard tutoring→Muse; complex→Muse; eval judge→Gemini free; batch eval→Nova batch); every LLM call tagged `user_id, agent_name, query_type, model_tier`;
caps: per-student daily (inherits existing **$2/day** design), aggregate daily, per-agent hourly. Estimates: ~$0.014/session, ~$0.007/eval run, ~$13–15/month at 30 sessions/day, ~$50–60 for the 4-month build.

**Security/guardrails:** existing TOTP-gated JWT (validated, not re-issued); input validation/injection detection before any LLM call; Pydantic schema on all LLM output;
sandbox with no network; content boundary refusal; FastAPI-layer rate limiting (the .NET limiter doesn't cover it).

**FDE vertical approach:** Java LLD first (Phases 1–2); FDE in Phase 3 via same RAG pipeline on a different corpus partition + LLM-judged design questions; no FDE auto-grading in v1.
**Stripe:** test-mode only, $0 refund demos; support agent classifies → checks policy → auto-refund under threshold or suggest to admin; audit trail on dashboard.

**Companion HLD ideas worth keeping (from the chatbot HLD drafts, `06-…`):** exact-context-first (load current lesson/exercise by ID — RAG only for discovery), metadata-before-similarity,
model-is-not-an-authorization-engine, 5-level progressive hints (conceptual nudge → structural hint → pseudocode → partial code → full solution only if policy allows), retrieved text = untrusted data,
route set `CURRENT_CONTEXT | CURRENT_VERTICAL_RAG | CROSS_VERTICAL_RAG | GENERAL_KNOWLEDGE | CLARIFICATION_REQUIRED` with rules-first routing and a later micro-LLM router only after collecting labelled data.

---

## 5. Real implementation status vs BUILD-TRACKER (verified against source, 2026-09-30)

### 5.1 What is actually in `ai-agent/` (252 lines total)

| File | What it really does | Tracker item it backs |
|---|---|---|
| `Dockerfile` | `python:3.12-slim`, installs `curl` (needed by compose healthcheck), `pip install -r requirements.txt`, `uvicorn main:app` on 8000 | 1.1 scaffold |
| `requirements.txt` | fastapi 0.141.1, uvicorn 0.53.0, pyjwt 2.14.0, pydantic 2.13.5, pydantic-ai 2.44.0, langgraph 1.2.11, langfuse 4.15.2, langchain 1.4.2 (only because `langfuse.langchain` hard-requires it), psycopg[binary] 3.3.6, psycopg_pool 3.3.2, pgvector 0.5.0. **No** tiktoken, tree-sitter, httpx pin, deepeval/ragas, pytest | 1.1 |
| `main.py` | `import observability` first; FastAPI with `lifespan` that `await pool.open()` / `pool.close()`; includes 4 routers | 1.1, 1.2-A1 |
| `config.py` | Fail-fast env reads at import: `JWT_SIGNING_KEY`, `MUSE_AI_API_KEY`, `DATABASE_URL` (RuntimeError if unset); defaults: `JWT_ISSUER=neuralascent`, `JWT_AUDIENCE=neuralascent-app`, `JWT_COOKIE_NAME=na_auth`. **No DeepInfra key, no Langfuse vars** (Langfuse reads its own env) | 1.1 env config |
| `auth.py` | `get_current_user`: Bearer header else `na_auth` cookie; `jwt.decode` HS256 with issuer+audience; 401 on any failure; returns raw claims. **No DB re-check of user status/role** | Phase 0 JWT bridge |
| `observability.py` | `get_client()` + `auth_check()` **at import time** (network call at import) | 1.1 Langfuse |
| `echo_agent.py` | Pydantic AI `Agent` on `OpenAIChatModel("muse-spark-1.3", OpenAIProvider(base_url="https://api.meta.ai/v1"))`, `output_type=PromptedOutput(EchoResult)` (Muse only supports `tool_choice="auto"`), `Agent.instrument_all()` | 1.1 Pydantic AI |
| `echo_graph.py` | LangGraph `StateGraph` START→`root_step`→END, compiled with Langfuse `CallbackHandler` bound via `.with_config()` | 1.1 LangGraph |
| `db.py` | `AsyncConnectionPool(min 1, max 5, open=False, configure=register_vector_async)` | 1.2-A1 |
| `migrate.py` | Creates `schema_migrations`, applies `migrations/*.sql` in filename order, each in a transaction with its bookkeeping row, skips applied | 1.2-A4 |
| `migrations/001_enable_pgvector_extension.sql` | `CREATE EXTENSION IF NOT EXISTS vector;` | 1.2 |
| `migrations/002_create_content_chunks.sql` | `content_chunks` table (see decision #16), HNSW cosine index, GIN on `search_vector`; **FK `lesson_id → lessons(id)`** | 1.2-A2/A3 |
| `routers/health.py` | `GET /health` → `{"status":"ok"}` (unauthenticated) | 1.1 |
| `routers/identity.py` | `GET /me` (JWT required) → claims | Phase 0 |
| `routers/test_agent.py` | `GET /echo` → live Muse call "say hi" (**no auth**) | 1.1 |
| `routers/test_graph.py` | `GET /agent_test` → graph invoke (**no auth**) | 1.1 |

No tests, no `ingest.py`, no chunker/extractor/embedding-client modules, no retrieval, no agents beyond the echo scaffold.

### 5.2 Tracker reconciliation
Every ✅ in the tracker for Phase 0, 1.1 and 1.2-A is **confirmed by the code**. Every ❌/unchecked item beyond that is confirmed **absent**. No item is marked done that isn't.
Known tracker drift (not code drift): (a) `Localization Lab disabled from running site` is still unchecked — and it really is *not* disabled: `app/src/App.jsx` still imports and routes all Localization pages (§ Localization file, `05-…`); (b) tracker "Overall status" text lags the 2026-09-22 platform changes (dynamic MCQ tables); (c) the build-tracker milestone "Phase 1 start 2026-09-13 🚧" is still the last Phase-1 row.

### 5.3 Reviewer observations (architect/reviewer role — findings, not fixes)
1. **`migrate.py` is not wired into any automated path.** Compose has no migrate step; `scripts/deploy-single-ec2.sh` only runs `api … --migrate` (EF Core). So `content_chunks`/`schema_migrations` exist only where someone ran `docker compose … exec ai-agent python migrate.py` (verified locally 2026-09-21). Production has `vector` enabled manually (2026-09-13) but **no evidence `002` was ever applied there**. Decide where migrate runs (deploy step vs container start) — a user decision.
2. **Migration ordering dependency:** `002` references `lessons(id)`, so EF Core migrations must have run first; a fresh DB with `ai-agent` migrating before `api --migrate` would fail.
3. **Unauthenticated LLM-calling route in production:** `/echo` (and `/agent_test`) have no `Depends(get_current_user)`, and the repo's nginx template proxies all of `tutor.${DOMAIN_NAME}` to `ai-agent:8000` (only `/health` is answered by nginx). A public GET can therefore trigger a paid Muse call, contradicting the project's own "no model call without the shared admission gateway" principle (tracker/TODO P3). No rate limiting exists in `ai-agent` at all.
4. **`/health` on the tutor subdomain is answered by nginx, not FastAPI.** The template's `location /health { return 200 "healthy\n"; }` inside the `tutor` HTTPS server shadows the proxy, so `https://tutor…/health` returns plain text and does not prove FastAPI is up (the 2026-09-10 notes treated plain-text `/health` as the *old* config symptom; the repo template still contains this block). Deployed nginx config was not inspected — verify with `/me`/`/echo` instead, or remove the override.
5. **Import-time side effects:** `observability.py` does a network `auth_check()` and `config.py` raises at import — a bad env value (like the quoted `LANGFUSE_BASE_URL` incident) crashes the container at boot before `/health` can answer; `rollback()` in the deploy script then deletes the crashed container before logs can be read (why the incident took a foreground `docker run` to diagnose).
6. **Claims-only auth:** a suspended/deleted .NET user with an unexpired JWT (12 h) still passes `get_current_user`; fine for scaffold, not for Phase 2+ (the TODO tracker requires status re-checks and ownership checks before any content load).
7. **Model id / base URL are hard-coded in `echo_agent.py`** (`muse-spark-1.3`, `https://api.meta.ai/v1`), not in `config.py`; the provider-neutral adapter the TODO tracker demands isn't there yet (expected at this stage).
8. **No CI for `ai-agent`:** `deploy-api.yml` builds/pushes the image but runs no lint/test step for Python; no `tests/` for it.
9. **Compose:** `ai-agent` has no `depends_on: database` (pool opens lazily so it boots, but early requests can fail); `app` depends on `ai-agent` health.
10. **Prod secrets:** SSM `/neuralascent/prod/api-env` was updated 2026-09-20 with `MUSE_AI_API_KEY`, `LANGFUSE_*`; a `DEEPINFRA_API_KEY` (or chosen name) has **not** been provisioned in config/compose/`.env.example`/SSM.
11. `VECTOR(1024)` and the DeepInfra request/response shape remain unverified until the first real embed call.

### 5.4 What is verified live in production
`tutor.neuralascent.top` → nginx (TLS SAN added via manual `certbot --expand`, expires 2026-12-07) → `ai-agent` container; `/me` with a real `na_auth` cookie returns decoded claims (JWT bridge proven 2026-09-12/13);
first real EC2 deploy of `ai-agent` with Langfuse/Muse env went green on 2026-09-20 after fixing `--env-file` omission and a quoted SSM value. pgvector image swap in prod 2026-09-13.

---

## 6. Two planning tracks (reconciliation record)
- **Track A (authoritative, built):** ARCHITECTURE.md — Pydantic AI + LangGraph + FastAPI, six agents, Muse/Nova/Gemini cascade, fresh TS frontend, staged cutover.
- **Track B (superseded background):** `ai-copilot-session-summary-for-opus5` + `copilot-week1-2-*` — 26-week AI-transition plan (target offers by Feb 2027; 12–15 h/wk now, 20–30 h/wk on bench after Dec 2026), HLD = Python/FastAPI/LangChain (LangGraph later)/SQLAlchemy+Alembic/pgvector, `copilot/` dir, Phase 0–4 (discovery → current-context tutor with no RAG → filtered RAG → routing/cross-vertical → evidence-driven). Week 1–2 note scoped to a naive-RAG baseline: 5 classes (`LessonChunker`, `EmbeddingClient`, `ChunkRepository`, `ContentIngestionRunner`, `RetrievalService`) writing `lesson_chunks`; `POST /query` returning raw ranked chunks; Langfuse span. Its Local-LLM prompt (`copilot-week1-2-fastapi-foundation-prompt.md`) was flagged **superseded/do-not-use** (violated the hand-written rule). It also said "explicitly decided against migrating the .NET backend to Python for practice" — later overtaken by decision #9 (staged cutover).
- Open tensions from Track B that Track A resolved in practice: LangChain vs raw SDK (→ LangGraph + minimal LangChain, ADR-001); HLD Phase 1 "no RAG" vs plan "naive RAG baseline first" (→ the tracker builds RAG first with a baseline-then-interventions eval); "Tier-1" has no schema field (→ `content_status='Published'` proxy + `content_quality_tier` column); chatbot paywall/usage gating (→ existing $2/day design, per-student caps in Phase 2.9).
- Naming differences to remember: Track B `lesson_chunks` vs real `content_chunks`; Track B `copilot/` vs real `ai-agent/`.

---

## 7. BUILD-TRACKER (condensed, preserved) — checkbox state as of 2026-09-21, verified 2026-09-30

**Pre-build:** [x] architecture spec · [x] provider cascade locked · [x] phases/timeline · [x] handoff doc · [x] tracker · [ ] Localization Lab disabled from running site (Gemini prompt produced 2026-09-07, never executed; see `05-…`) · [x] `ai-agent/` dir · [x] dependency management (`requirements.txt`).

**Phase 0 (infra scaffold, 2026-09-08→13):** [x] FastAPI skeleton + CI/deploy wiring (commits `c3742f6`, `f2db042`) · [x] DNS `tutor` A record (GoDaddy) · [x] Nginx `tutor.` server blocks · [x] TLS SAN (**future new subdomains need the same manual `certbot --expand`** — deploy script only runs `certonly` for a first-ever cert) · [x] JWT middleware · [x] actual EC2 deploy confirmed 2026-09-12/13 (needed identical `JWT_SIGNING_KEY` in SSM for both `Auth__JwtSigningKey` (.NET) and `JWT_SIGNING_KEY` (ai-agent)).
Deferred until Phase 1 pipeline works (decision 2026-09-13): [ ] DeepInfra keys provisioned (**do next, part of 1.2**) · [ ] restricted SSH key for tunnel · [ ] `autossh` reverse tunnel · [ ] launchd wrapper · [ ] local bge-m3 + reranker on Mac (MPS) · [ ] admin toggle `embedding_backend`/`reranker_backend` + `force_api_backend` · [ ] Mac/tunnel health indicator · [ ] fresh TS frontend scaffold.

**Phase 1 (target mid-Oct 2026; "interview-ready after this"):**
- 1.1 [x] all six items (scaffold, Pydantic AI, LangGraph, Compose, env config, Langfuse both hook points, `/health`).
- 1.2 Done: [x] DB pool [x] `content_chunks` schema [x] HNSW [x] tsvector+GIN [x] idempotent migrations. **Remaining (Phases B–E):** [ ] lesson parser (DB read, Published only, join `course_modules` + `lesson_concept_links→knowledge_concepts`) [ ] hierarchical H2→H3→H4 chunking [ ] atomic MCQ chunking (**now from `mcq_*` tables**, see §3) [ ] AST chunking via tree-sitter (Java `solution/**/*.java`) [ ] exercise ingestion (manifest / `evidence[]` / solution code, via `lessonSlug`) [ ] metadata extraction [ ] embeddings via DeepInfra `bge-m3` (**wire last** so chunking bugs and API bugs aren't debugged together) [ ] `ingest.py` idempotent via per-chunk `content_hash` (`ON CONFLICT … DO UPDATE`, same pattern as the migration runner). Build order: **A** foundation ✅ → **B** lessons prose → **C** MCQs → **D** exercises (tree-sitter risk isolated here) → **E** embed + orchestrate. Phase B goal: prove read→chunk→store→idempotent-rerun on the simplest content type, embeddings null.
- 1.3 [ ] dense (cosine) [ ] sparse (tsvector) [ ] RRF [ ] bge cross-encoder rerank [ ] parent-document expansion [ ] query rewriting [ ] content-quality weighting.
- 1.4 [ ] Pydantic AI tutor agent [ ] retriever as tool [ ] citation enforcement [ ] content-boundary guardrail [ ] basic injection detection [ ] conversation history [ ] SSE/WebSocket streaming.
- 1.5 [ ] golden set (~80–100 hand-written) [ ] DeepEval pytest runner [ ] RAGAS metrics [ ] baseline [ ] five interventions [ ] documented numbers.
- 1.6 [ ] chat component [ ] markdown rendering [ ] citation links [ ] streaming state [ ] JWT auth integration (no new login) [ ] API client.
- Definition of done: chat with RAG-grounded, cited answers; eval harness produces RAGAS metrics; ≥3 interventions beat baseline; Langfuse trace per interaction; within **$2/day**.

**Phase 2 (weeks 6–10, late Nov):** 2.1 intent router + cascade (Nova Micro classifiers; LangGraph branching) · 2.2 Profiler (+`learner_profiles`, optional git analyzer) · 2.3 Assessment (MCQ gen + LLM-judge validation + `generated_mcqs`; Java exercise generation; calibration; pass-rate tracking) · 2.4 concept prerequisite DAG · 2.5 3-layer memory (`interaction_traces`, `concept_mastery`, Mem0, `PostgresSaver`) · 2.6 Nudge (FSRS/SM-2, scheduled) · 2.7 Java sandbox (Docker, no network, caps, MCP tool) · 2.8 MCP exposure (RAG retriever, Java executor, MCQ generator, concept navigator) · 2.9 cost attribution (tags, per-agent/student aggregation, budget caps). DoD: all 5 non-admin agents, MCQs persisted, exercises run in sandbox, concept graph drives selection, sensible nudges, per-agent/student cost visible, cascade demonstrably cheaper.

**Phase 3 (weeks 11–14, late Dec):** 3.1 Support agent (own corpus/persona/account lookup/Stripe test refunds/escalation) · 3.2 red-team eval (30 cases) · 3.3 Admin agent · 3.4 admin dashboard · 3.5 Stripe test-mode ($0 refund demo, policy rules, audit) · 3.6 FDE integration (RAG only, LLM-judged design questions) · 3.7 UX polish (mode transitions, MCQ panel w/ hints, code editor, support trigger, responsive) · 3.8 demo narrative · **3.9 routing cutover (added 2026-09-08)**: parity verified → Nginx flip `neuralascent.top` → new stack → .NET retired/narrowed.

**Phase 4 (Jan 2027, only if time):** local-vs-API model-economics write-up (Mac Studio vs cloud) · Model Economics Matrix measurements · FSRS vs SM-2 A/B · animations.

**Milestones:** architecture locked 2026-09-07 ✅ · infra revision 2026-09-08 ✅ · Phase 0 core goal 2026-09-12/13 ✅ · Phase 1 start 2026-09-13 🚧 · Phase 1 done mid-Oct ⏳ · Phase 2 late Nov ⏳ · Phase 3 late Dec ⏳ · interview-ready Jan 2027 ⏳.

---

## 8. Session timeline (what happened, in order)

| Date | Session | Key outcomes / gotchas |
|---|---|---|
| 09-04→06 | AI chatbot planning + auth build (`06-…`) | Course review of Scaler "AI Infusion"; new "learning support agent" idea; language question left open |
| 09-07/08 | Architecture written (other machine) → Phase 0 infra | Six-agent design, cascade, memory decision, staged cutover; skeleton + Nginx + CI + deploy script + DNS + TLS. Corrections: prod never uses `docker-compose.yml`; `python:3.12-slim` is Debian (apt is right); healthcheck needs `curl`; TLS is `certonly --standalone` so a SAN needs a manual `--expand` |
| 09-09/10 | Phase 0 deploy debugging | Fixed .NET test-compile errors (`Options` namespace collision; `TotpSecretProtector(IHostEnvironment)`; `ThrowsAny<CryptographicException>` for macOS), a real React rules-of-hooks crash (`BidSubmissionModal.jsx`), private-repo curl 404 (added `GITHUB_TOKEN` auth header to the SSM `curl`s). Blocker: stale `/etc/studytracker/api.env` missing `Auth__JwtSigningKey` (bootstrap only fetches SSM if the file is absent — consider always-refresh) |
| 09-12/13 | Phase 0 close-out; **pgvector prod migration** | Prod DB image → `pgvector/pgvector:pg16` (arm64 verified). See mistakes list §9 |
| 09-15 | Teaching style + Phase 1 kickoff | Working-style rules (§1); CrewAI question flagged |
| 09-19 | LangGraph scaffold + ADR-001 | 3 rounds of typo bugs (`typing_extentions`, `Ouput_txt` vs `output_txt`, backwards `add_edge(END,…)`); `PromptedOutput` fix for Muse; Langfuse vs LangSmith check |
| 09-20 | Langfuse both hooks; Compose dev integration; first real EC2 deploy | Podman/rootless debugging arc; SSM output truncation → S3 log capture + IAM `deploy-logs/*`; **`--env-file` omission** and **quoted SSM value** bugs (commits `b37b78a`, `a3d6c14`) |
| 09-21 | Ingestion Phase A + provider decisions | DeepInfra decision; exercises-vs-`problems` correction; DB pool; `content_chunks`; `migrate.py` proven idempotent; typo fix `efb31f1` |
| 09-22 | Exercise-grading handoff (`04-…`) | Priority order: finish exercise grading (WSL2→EC2) **then** return to `ai-agent/` |

---

## 9. Gotchas & hard-won facts (keep)

- **Prod DB name is `StudyTrackerDB` (mixed case, quoted)**, not the compose fallback `studytracker`. Wrong name → looks like data loss but isn't.
- **`docker exec -t` corrupts binary stdout** (broke two "backups"); never use `-t`/`-it` when redirecting `pg_dump -F c`. **Verify every backup immediately** (`pg_restore --list`, run in a disposable container with a `-v` mount — `docker exec` can't see host files). Valid backup at the time: `StudyTrackerDB_backup_20260913_131226.dump` (324 TOC entries) — get it off the host; delete the three corrupt ones.
- `deploy-single-ec2.sh` never recreates an existing DB container; changing the image needs manual `docker stop/rm`, then one deploy with `ALLOW_CREATE_DATABASE=true` (flip back to `false` immediately — it's a safety guard) with `RESTORE_LATEST_BACKUP` restoring from S3. Run `bash -n scripts/deploy-single-ec2.sh` before pushing edits (a mangled `${POSTGRES_IMAGE:-…}` once killed the script under `set -u`). `pgvector/pgvector:pg16` arm64 manifest verified; the script does not verify `POSTGRES_IMAGE`'s platform.
- `docker-compose.yml` **and** `deploy-single-ec2.sh` each have their own `POSTGRES_IMAGE`; a compose change never affects prod. Local compose once had typo `pgvector/pgvector:pg1` (fixed to `pg16`).
- **Docker `--env-file` does not strip quotes** — never quote values in SSM/`.env` (`LANGFUSE_BASE_URL="https://…"` broke `auth_check`).
- **Prod secrets ≠ local `.env`:** prod env comes from SSM `/neuralascent/prod/api-env` (SecureString) pulled once by `bootstrap-single-ec2.sh` into `/etc/studytracker/api.env`; editing compose/`.env.example` does nothing for prod. Compose var precedence: shell env > `.env` > default (a stale exported `JWT_SIGNING_KEY` once shadowed `.env`).
- `restart: unless-stopped` reuses a container's baked-in env — pick up compose changes with `docker rm -f` + `up -d --build`.
- Local `.env` placeholders (`your_jwt_signing_key_…`, `your_secure_password_here`) were left in by mistake more than once; Postgres only applies `POSTGRES_PASSWORD` on first volume init.
- GitHub Actions/SSM output truncates at a few KB (EF Core logs every query during `--seed-reference-data`) → deploy now writes SSM output to S3 (`deploy-logs/${GITHUB_SHA}`).
- Deploy workflow runs only on `[deploy]` in the commit message or manual dispatch; a plain push ships nothing.
- `api/obj/*` build artifacts are tracked despite `.gitignore` (recommended `git rm -r --cached api/obj api/bin`, not done).
- SSH `Connection timed out` after the pgvector session was never confirmed fixed — suspect Security Group source IP vs `curl https://checkip.amazonaws.com`, or a changed EC2 public IP.
- Muse rejects forced `tool_choice`; Pydantic AI 2.x has no `instrument=True` kwarg; Langfuse `CallbackHandler` needs `langchain` installed.
- Langfuse shows $0.00 cost for Muse — pricing simply isn't registered; not a bug.
- Env var names: `.NET` `Auth__JwtSigningKey` ↔ ai-agent `JWT_SIGNING_KEY` **must be identical strings**.
- Muse Spark 1.2 model notes (from the TODO tracker Appendix A, `06-…`): preview API, OpenAI-compatible; Standard tier for learner/curriculum traffic; `reasoning_effort` bills as output tokens — use the routing table (`CURRENT_CONTEXT` low, RAG routes medium, clarification minimal, general low). The agent is on **1.3 Contributor**; re-verify pricing/limits at `developer.meta.com/ai`.

---

## 10. Open items / decisions waiting on the user
1. Where does `ai-agent/migrate.py` run (deploy step vs container start), and apply `002` to prod? (§5.3-1)
2. Authenticate or remove `/echo` & `/agent_test`; add FastAPI-layer rate limiting/admission gate (§5.3-3).
3. `/health` nginx override on the tutor block (§5.3-4).
4. DeepInfra key name/plumbing (config, compose, `.env.example`, SSM).
5. MCQ chunk source now that MCQs are in `mcq_*` tables.
6. Recount the exercise corpus (65 was the 2026-09-21 number).
7. Optional: `pydantic-settings`; ~1-day CrewAI sandbox; LangChain text-splitter spot in ingestion (keep tiny).
8. Localization disable prompt (§ `05-…`) — produced, never executed; Localization is still live in `app/`.
9. Provision remaining credentials before their phases: Bedrock IAM (Nova Micro), Google AI Studio key (Gemini judge).
10. Off-critical-path: rotate the local dev Postgres password; add `IMAGE_AI_AGENT` doc parity already present in `.env.example`.
