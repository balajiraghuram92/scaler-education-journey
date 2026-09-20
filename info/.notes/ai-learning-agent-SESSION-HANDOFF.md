# AI Learning Agent — Session Handoff & Context Document

> **Read this first in any new chat session.** This is the single entry point
> for the AI Learning Agent project on Neuralascent. It tells you who the user
> is, what they're building, every decision that's been locked, and where to
> find detailed specs. Do not re-derive or re-debate anything marked "LOCKED."

**Last updated:** 2026-09-08
**Status:** Design complete, implementation not started
**Architecture spec:** [ai-learning-agent-ARCHITECTURE.md](ai-learning-agent-ARCHITECTURE.md)
**Build tracker:** [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)

---

## 1. Who is the user

- **Name:** Raghuram Balaji
- **Current role:** Working at Coforge (India), ~30 LPA
- **Experience:** ~2 years AI experience, 5 years Java experience, 4.5 years
  technical artist experience
- **Target:** ₹40–60+ LPA Applied AI / GenAI Engineering roles at Indian
  services firms (Accenture, TCS, Infosys AI units) and mid-size product
  companies
- **Job search timeline:** January 2027
- **Build timeline:** September–December 2026

---

## 2. What this project is

An **AI-first personalized learning platform** built on Neuralascent
(`neuralascent.top`). The AI tutor agent IS the primary learning interface —
not a sidebar chatbot. It uses the existing Java LLD and FDE curriculum
content as RAG data to deliver personalized, adaptive tutoring.

### Why one project instead of three

The user originally planned three separate projects from a market research doc:
- **Project A:** RAG-based curriculum tutor
- **Project B:** Content quality audit pipeline
- **Project C:** Code execution grounding engine

They decided (2026-09-07) that a single deep, unified project covering all
interview clusters is stronger than three separate tutorial-grade projects.
This AI Learning Agent subsumes all three.

### The interview story (the whole point)

This project exists to demonstrate, in interviews, mastery of:

| Interview cluster | How this project demonstrates it |
|---|---|
| RAG depth | Hierarchical + AST-aware chunking, hybrid search, reranking |
| Agentic workflows | 6 agents with explicit roles, stateful LangGraph orchestration |
| Evaluation | Golden eval set, RAGAS metrics, MCQ calibration, tutoring effectiveness |
| Cost governance | Model cascade, per-student/per-agent cost attribution, budget caps |
| Tool use | Sandboxed Java code execution, MCQ generation, git analysis |
| MCP | Tools exposed via Model Context Protocol (asked at Accenture Dec 2025) |
| Multi-agent | 5-6 specialized agents with justifiable separation of concerns |
| Observability | OpenTelemetry + Langfuse tracing, cost dashboard |
| Production hardening | Auth (already built), rate limiting, guardrails, prompt injection defense |
| LLM-as-judge | MCQ quality scoring, tutoring answer evaluation |
| Stripe integration | AI-assisted admin operations demo (test-mode refunds) |

---

## 3. Architecture summary

### System topology

```
React Frontend (existing site + new chat/MCQ/code-editor components)
    │ HTTP/WebSocket
    ▼
Python FastAPI Service (NEW — separate microservice)
    ├── LangGraph Orchestrator
    │   ├── Profiler Agent    — skill assessment, onboarding
    │   ├── Tutor Agent       — RAG-grounded teaching (primary)
    │   ├── Assessment Agent  — MCQ gen, Java exercises, difficulty calibration
    │   ├── Nudge Agent       — spaced repetition, proactive engagement
    │   ├── Support Agent     — help/FAQ, different RAG corpus
    │   └── Admin Agent       — dashboard, Stripe refunds, anomaly alerts
    ├── RAG Engine (pgvector dense + tsvector sparse, cross-encoder rerank)
    ├── Eval Engine (DeepEval + RAGAS metrics)
    ├── Tool Registry (MCP protocol)
    ├── Learner Memory Store (3-layer: traces → mastery → profile)
    ├── Langfuse Tracing
    └── Cost Governor
    │
    ├── PostgreSQL (pgvector — already in the stack)
    ├── LLM Providers (Meta Muse + AWS Bedrock Nova + Gemini)
    └── Docker Sandbox (Java code execution)
```

### Relationship to existing site — REVISED 2026-09-08

**Supersedes the "existing React/.NET stays as legacy" language above.**
Decided in a session on another machine (2026-09-07/08):

- The new learner-facing frontend is a **fresh TypeScript build** — NOT a
  reuse of the existing `app/` React/JSX codebase. New project, new repo
  path.
- The new backend is **Python + FastAPI** — a separate microservice from the
  .NET API, not a plugin into it.
- **Auth is not rebuilt** — the existing TOTP-gated JWT auth (already built
  in `api/`) keeps issuing tokens. The FastAPI service only **validates**
  those JWTs (shared secret/keys) — no parallel auth system.
- **Routing/cutover plan (infra, same AWS public IP, same EC2 host):**
  1. Today: `neuralascent.top` → .NET API/site, unchanged, for current users.
  2. Phase 0: add a new subdomain or path (e.g. `tutor.neuralascent.top` or
     `/agent/*`) via Nginx pointing at the new FastAPI service, dev-only.
  3. Phase 1–2: new TS frontend + FastAPI built out behind that
     subdomain/path, authenticating against the shared JWT.
  4. Phase 3: once the new stack has full feature + auth parity, flip Nginx
     so `neuralascent.top` itself routes to the new stack. .NET API is kept
     alive only for whatever isn't yet ported, or retired at that point.
- The existing Llama API chat (`ChatEndpoints.cs`) is the precursor this
  agent replaces, but the .NET site itself is not assumed to live on
  indefinitely as "legacy" — full cutover is the target, not permanent
  coexistence.

---

## 4. Technology stack (LOCKED)

| Layer | Technology | Why |
|---|---|---|
| Agent logic | **Pydantic AI v1.0** | Type-safe, FastAPI-style, 44% faster P95 than LangGraph alone |
| Orchestration | **LangGraph** | Stateful graph, branching, human-in-the-loop. Production at Uber, JPMorgan, Replit |
| API | **FastAPI** | Standard for Python AI services |
| Vector store | **pgvector** on existing Postgres 16 | No new infra |
| Sparse search | PostgreSQL **tsvector / pg_trgm** | BM25-equivalent hybrid with dense |
| Embeddings | **OpenAI text-embedding-3-large** | Locked 2026-09-07. Zero infra, negligible cost at this corpus size, ships faster. BGE self-hosted comparison pushed to Phase 4 stretch. |
| Learner memory | **Hybrid: PostgreSQL + Mem0** | Locked 2026-09-07. See §6 Learner memory. |
| Reranking | **bge-reranker-v2-m3** | Cross-encoder reranking = strong interview signal |
| Eval | **DeepEval** | pytest-style, CI-gatable, RAGAS-compatible |
| Observability | **Langfuse** (open-source) | LLM tracing, cost tracking |
| Structured output | **Pydantic v2** | Schema enforcement on all LLM outputs |
| Tool protocol | **MCP** (Model Context Protocol) | Hot interview topic |
| Code execution | **Docker sandbox** (JDK, no network, resource caps) | Safe Java compilation |
| Frontend | **TypeScript, fresh build** (revised 2026-09-08 — no reuse of existing `app/` React/JSX) | Built with AI assistance (Gemini) |
| Local inference host | **Mac Studio M1 Max, 32GB**, via SSH tunnel from AWS, always-on/UPS-backed | Runs embedding + reranking locally to cut API cost |
| Embedding/rerank fallback | Cloud API keys for the *same* model weights as the local models | Failover if Mac/tunnel is down — avoids re-embedding drift from mixed models |

---

## 5. LLM provider cascade (LOCKED 2026-09-07)

Three-provider cascade. Do NOT add more providers or change models without
the user's explicit approval.

| Tier | Model | $/MTok (in/out) | Use case |
|---|---|---|---|
| **Primary** | Meta Muse Spark 1.3 Contributor | $0.10 / $0.20 | Tutor Agent, Assessment Agent, complex reasoning |
| **Routing + Bulk** | Amazon Nova Micro (Bedrock) | $0.035 / $0.14 | Intent router, nudge, admin summaries |
| **Batch eval** | Amazon Nova Micro Batch (Bedrock) | $0.0175 / $0.07 | Golden set eval (50% off, async) |
| **Eval judging** | Google Gemini free tier | $0 | RAG eval judge, MCQ quality (different provider = no bias) |

**Key decisions and rationale:**
- **Muse Contributor tier** trains on prompts/completions — acceptable for a
  portfolio project with public curriculum content, not proprietary data
- **Muse access from India confirmed** — UPI-based registration on Meta
  developer console, tested via Muse Code (2026-09-07)
- **Nova Micro on Bedrock** — cheapest Bedrock model, IAM auth, batch at 50% off
- **Gemini free tier for eval** — different provider for eval judging avoids
  self-preference bias (a documented LLM-as-judge pitfall)
- **Gemini 2.5 Flash-Lite is shutting down Oct 16, 2026** — target Gemini 3.1
  Flash-Lite or whatever free tier is current

**Estimated costs:**
- Per session (~30 min): ~$0.014
- Per eval run (100 Q/A, batch): ~$0.007
- Monthly (30 sessions/day): ~$13–15
- 4-month total: ~$50–60
- No credits needed. Existing $2/day budget cap is sufficient.

---

## 6. Key design decisions (all LOCKED unless noted)

### RAG pipeline
- **Chunking:** Hierarchical by heading (H2→H3→H4) for prose, AST-aware via
  tree-sitter for Java code, atomic for MCQs
- **Retrieval:** Dense (pgvector) + sparse (tsvector) → Reciprocal Rank Fusion
  → bge cross-encoder rerank → parent-document expansion → concept-prerequisite
  filter
- **Query rewriting** for multi-hop questions
- **Content quality weighting** — Tier-1 deep lessons weighted higher than
  thin machine-templated drafts

### Learner memory (3-layer model, inspired by DeepTutor) — LOCKED 2026-09-07
Hybrid storage, chosen deliberately rather than picking one tool for everything:
- **L1 Raw traces (Postgres):** Every interaction logged — `interaction_traces` table
- **L2 Concept mastery (Postgres):** Per-concept score (0.0–1.0), pass rate, FSRS
  `next_review_at` scheduling — inherently relational/numeric, no memory library
  (including Mem0) models scored spaced-repetition scheduling well
- **L3 Learner profile (Mem0):** Free-text synthesized facts — misconceptions
  ("kept confusing composition with inheritance"), pace/style preferences
  ("prefers code examples over prose") — this is the fuzzy semantic-fact
  extraction Mem0 is actually built for
- **In-thread conversation state:** LangGraph checkpointer + `PostgresSaver` —
  separate concern from long-term memory above, needed regardless

**Why not Mem0 for everything or Postgres for everything:** Mem0 has no
concept of a numeric mastery score with FSRS-scheduled reviews — forcing that
in fights the tool. Skipping Mem0 entirely would mean no hands-on experience
with the industry-standard memory layer (50k+ devs, deepest LangGraph/CrewAI
ecosystem integration) where it actually fits. LangMem (LangGraph's own store)
was considered and rejected — a third-party benchmark reported 59.82s p95
retrieval latency, disqualifying for an interactive tutor, vs. Mem0's ~0.2s.

### Evaluation harness (5 categories)
1. RAG golden set (~80–120 hand-written Q/A, RAGAS metrics)
2. MCQ quality (difficulty calibration, distractor quality)
3. Tutoring effectiveness (learning gain, time-to-mastery, retention)
4. Support bot red-team suite (~30 adversarial cases)
5. Agent-level metrics (latency, cost, error rate, router accuracy)

### Spaced repetition
- FSRS or SM-2 variant for the Nudge Agent's review scheduling

### Concept prerequisite graph
- DAG extracted from Java LLD curriculum
- Stored as `(concept_id, prerequisite_concept_id)` edges in PostgreSQL
- Used by Tutor (never teach before prereqs), Assessment (frontier questions),
  Nudge (gap identification)

### Stripe integration
- Test mode only, $0 refund demonstrations
- Support Agent auto-refunds under threshold; Admin Agent surfaces suggestions
  for edge cases

### Decisions — resolved 2026-09-07

| # | Decision | Resolution |
|---|---|---|
| 1 | Mem0 vs custom PostgreSQL for learner memory | **LOCKED: Hybrid** — Postgres for L1/L2 (scores, FSRS scheduling), Mem0 for L3 (free-text profile/misconceptions). See §6 Learner memory. |
| 2 | FDE exercise grading: LLM-as-judge vs human review only | **LOCKED: LLM-as-judge** — Phase 3 concern, no action needed yet. |

### Decisions — resolved 2026-09-08 (revises #2 embeddings and #4 Mac Studio above)

| # | Decision | Resolution |
|---|---|---|
| 3 | Embeddings provider | **REVISED, supersedes the 2026-09-07 "OpenAI text-embedding-3-large" lock.** Reranking via API was pricing out too high, so embedding + reranking move to **local-first via the Mac Studio M1 Max (32GB)**, reached over an SSH tunnel from the AWS host, kept always-on on a UPS. Cloud API keys for the *same model weights* are provisioned as automatic fallback if the Mac/tunnel is unreachable. **Rule: pick one embedding model and never swap it once the corpus is indexed** — a different model's vectors aren't comparable, so a swap means a full re-embed of the whole corpus, not just new content. The local/fallback pair must be the *same* weights for this reason. |
| 4 | Mac Studio M1 Max local model for routing tier | **Narrowed and locked** — not used for the LLM routing tier (Nova Micro still handles that). Used specifically as the **embedding + reranking host**, for cost savings and as a deliberate model-economics/local-vs-API comparison data point for the interview story. |
| 5 | Frontend/backend for the new learner-facing stack | **LOCKED: fresh TypeScript frontend + Python FastAPI backend**, no reuse of the existing `app/` React/JSX or the .NET API for the new tutor UI. See §3 "Relationship to existing site — REVISED 2026-09-08". |
| 6 | Cutover routing from `neuralascent.top` | **LOCKED: staged.** .NET keeps serving the domain through Phase 0–2 (new stack lives on a subdomain/path). Nginx flips the domain to the new stack in Phase 3 once feature + auth parity is reached. Auth itself is not duplicated — FastAPI validates the existing .NET-issued JWTs. |

---

## 7. Build phases & timeline

| Phase | Target | Goal |
|---|---|---|
| **Phase 0** — Infra & routing scaffold (added 2026-09-08) | Before Phase 1, ~3–5 days | FastAPI skeleton live on the same EC2 host/public IP under a dev subdomain/path; Nginx still sends `neuralascent.top` → .NET unchanged; JWT validation against existing tokens; SSH tunnel from Mac Studio wired up with API fallback for embedding/rerank. |
| **Phase 1** — The substrate | Weeks 1–5, mid-October 2026 | Working RAG tutor + eval harness, new TS frontend on the dev subdomain. Interview-ready after this. |
| **Phase 2** — Multi-agent + personalization | Weeks 6–10, late November 2026 | Full agent roster + adaptive learning. Much stronger interview story. |
| **Phase 3** — Support + Admin + Polish + cutover | Weeks 11–14, late December 2026 | Complete system, full portfolio piece, **and** the Nginx routing flip so `neuralascent.top` serves the new stack directly. |
| **Phase 4** — Stretch | January 2027 (only if time) | Local-vs-API model economics writeup, further self-hosted experiments, advanced UX. |

See **[ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)**
for the detailed task-level tracker with checkboxes.

---

## 8. Critical rules for any assistant working on this

### Code editing rules (from CLAUDE.md)
- **Claude does NOT have permission to edit, create, or delete source code
  files** in this repo (`.cs`, `.jsx`, `.js`, `.tsx`, `.css`, `.html`, configs)
- Claude's only lever on those files is producing a **fully self-contained,
  copy-paste-ready prompt** that the user pastes into a different LLM (Gemini)
- **Exceptions:** `CLAUDE.md`, memory directory, `info/.notes/*`, `exercises/*`

### Hand-written vs AI-assisted
- **All Python AI logic** (agents, RAG pipeline, eval harness, orchestration)
  is **hand-written by the user** for interview defensibility
- **Frontend/UX** is built with AI assistance (Gemini prompts)
- **AI-vertical curriculum content** (the actual lesson text) is hand-authored
  only — never generate content-generation prompts for it (CLAUDE.md §AI-VERTICAL)

### What "AI integration" means here
The AI Learning Agent is **AI integration** (site infrastructure), NOT
AI-vertical content. The prompt workflow (read files → produce copy-paste-ready
Gemini prompt) applies to frontend and infrastructure changes. The Python AI
layer is hand-written by the user, but Claude can help with architecture,
design, debugging advice, and documentation.

---

## 9. Other Neuralascent projects — status

### Localization Lab — ON HOLD
- All code stays on disk. Routes, imports, DI registrations, endpoint mappings,
  and seed data are to be **commented out** (not deleted) from the running site.
- A Gemini prompt for disabling it was produced (2026-09-07) targeting:
  `App.jsx`, `LabProjects.jsx`, `Program.cs`, `DbSeeder.cs`
- **Status of that prompt:** Produced but NOT executed by the user yet
- Will resume after the AI Learning Agent ships
- Full status: [localization-lab-STATUS-TRACKER.md](localization-lab-STATUS-TRACKER.md)

### Auth / TOTP / AI Chat — COMPLETED
- Self-serve signup → admin approval → mandatory TOTP MFA → AI chat with
  $2/day budget cap
- Committed to `main` (ending at `a660f95`)
- Backend was never compiler-verified in Claude's environment — user has since
  committed "fixed compiler issues" commits
- Full record: [SESSION-2026-09-AI-chatbot-planning-and-auth-build.md](SESSION-2026-09-AI-chatbot-planning-and-auth-build.md)

### AI vertical curriculum content — PARKED
- Hand-authored only. No longer a priority track. The AI Learning Agent
  subsumes the interview-portfolio motivation.

---

## 10. Interview preparation context

The user's market research identified these key expectations for ₹40–60+ LPA
AI roles in India (Jan 2027):

**Must-have skills:**
- RAG pipelines (advanced: hybrid search, reranking, evaluation)
- Agent frameworks (LangGraph, CrewAI, or equivalent)
- Prompt engineering & evaluation (RAGAS, DeepEval)
- Python + FastAPI
- Vector databases
- LLM observability & cost management

**Strong differentiators:**
- MCP (Model Context Protocol) — actively asked about in interviews
- Multi-agent orchestration with justifiable agent separation
- LLM-as-judge with bias-aware evaluation design
- Production hardening (guardrails, prompt injection defense)
- Cost governance with per-agent attribution

**Interview rehearsal sentences** (one per phase — practice these):

Phase 1: "Naive RAG scored 0.62 context precision and 0.71 faithfulness on
my 100-question golden set; AST-aware chunking + bge cross-encoder reranker
moved context precision to 0.84 and faithfulness to 0.88."

Phase 2: "Five agents orchestrated via LangGraph; the assessment agent
calibrates MCQ difficulty against the learner's mastery state, and the model
cascade cuts per-session cost 60% by routing simple queries to an 8B model."

Phase 3: "The support agent shares RAG infrastructure but swaps corpus and
persona; I red-teamed it with 30 adversarial cases — containment rate 93%,
zero prompt injection successes. The admin agent automates policy-compliant
refunds via Stripe and surfaces resolution suggestions for edge cases."

Provider cascade: "Provider-agnostic cascade across three providers — Meta
Muse for quality-sensitive tutoring at $0.20/MTok output, Amazon Nova Micro
on Bedrock for routing at $0.035/MTok with batch inference at 50% off for
eval runs, and Gemini free tier as the eval judge to avoid self-preference
bias. Per-session cost is $0.014."

---

## 11. File index

| File | Purpose |
|---|---|
| `info/.notes/ai-learning-agent-SESSION-HANDOFF.md` | **This file** — read first in any new session |
| [SESSION-2026-09-20-langfuse-integration-and-docker-compose.md](SESSION-2026-09-20-langfuse-integration-and-docker-compose.md) | **Most recent AI Learning Agent session — read this first.** Langfuse tracing wired for both Pydantic AI (OTel-backed `get_client()`/`instrument_all()`) and LangGraph (`CallbackHandler` via `.with_config()`), Docker Compose dev-integration done and verified live end-to-end, several pre-existing Compose/Podman bugs fixed along the way. **Phase 1.1 is now fully complete** — Phase 1.2 (content ingestion) is next |
| [SESSION-2026-09-19-langgraph-scaffold-and-adr.md](SESSION-2026-09-19-langgraph-scaffold-and-adr.md) | LangGraph scaffold built/debugged/verified working, ADR-001 written (resolves the CrewAI-vs-LangGraph question below), Langfuse-vs-LangSmith checked against live 2026 data |
| [SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md](SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md) | How the user wants an assistant to operate (teaching style, hand-written-code scope). Its CrewAI-vs-LangGraph open question is now resolved — see the session file above and `ADR-001-orchestration-framework-choice.md` |
| [ADR-001-orchestration-framework-choice.md](ADR-001-orchestration-framework-choice.md) | Decision record: LangGraph for the tutor, LangChain for the (on-hold) Localization Lab, CrewAI in neither |
| `info/.notes/ai-learning-agent-ARCHITECTURE.md` | Full architecture & design specification (technical detail) |
| `info/.notes/ai-learning-agent-BUILD-TRACKER.md` | Phase-by-phase build tracker with checkboxes |
| [SESSION-2026-09-13-pgvector-migration.md](SESSION-2026-09-13-pgvector-migration.md) | **Most recent infra session** — production Postgres → pgvector migration; several concrete mistakes documented (wrong assumed DB name, `docker exec -t` corrupting binary backups, an unverified "backup" that was actually corrupt) worth reading before touching this database again; also flags one still-open item (the `vector` extension was enabled manually, not via migration) |
| `info/.notes/neuralascent-work-status.md` | Overall project status across all Neuralascent tracks |
| `info/.notes/SESSION-2026-09-10-phase0-deploy-debugging.md` | **Most recent session** — debugging the first real deploy runs; has a confirmed, unfixed blocker (stale env file / missing `Auth__JwtSigningKey` on EC2) — read this first before touching the deploy again |
| `info/.notes/SESSION-2026-09-08-phase0-infra-and-deploy.md` | Earlier session — Phase 0 infra build (ai-agent skeleton, CI/deploy wiring, DNS/TLS), and a flagged conflict with a second unreconciled planning track (still unresolved) |
| `info/.notes/SESSION-2026-09-AI-chatbot-planning-and-auth-build.md` | Earlier session handoff (auth build + AI-helper review) |
| `info/.notes/localization-lab-STATUS-TRACKER.md` | Localization project status (on hold) |
| `CLAUDE.md` | Repo-wide rules (no direct code edits, prompt workflow, scope boundaries) |

---

## 12. Localization disable prompt (produced 2026-09-07, not yet executed)

The user needs to paste this into Gemini to comment out all Localization
references from the running site. All Localization code stays on disk — only
routes, imports, DI registrations, endpoints, and seed data are commented out.

**Target files and changes:**

### `app/src/App.jsx`
- **Lines 17–24:** Comment out all 7 Localization imports
  (`LocalizationShell`, `StringsTab`, `WorkflowTab`, `SnapshotsTab`,
  `MarketplaceTab`, `VendorOpenJobs`, `VendorMyJob`)
- **Lines 138–188:** Comment out all 9 Localization route definitions
  (both Owner routes and Vendor Portal routes)

### `app/src/pages/LabProjects.jsx`
- **Lines 24–31:** Remove Lab B fixture data entirely ("Unity Localization &
  Asset Delivery Platform") — delete the object from the `modules` array so
  only Lab A remains
- **Line 179:** Simplify the destination routing logic — remove the
  `mod.title?.includes('Lab B') || mod.id === 2` branch since Lab B no longer
  exists in fixtures

### `api/Program.cs`
- **Lines 7, 9, 15:** Comment out 3 Localization using statements
- **Lines 128–142:** Comment out 10 Localization DI registrations
  (`GoogleTranslateOptions`, all services)
- **Lines 1577–1580:** Comment out 4 endpoint mapping calls
  (`MapLocalizationEndpoints`, `MapMarketplaceEndpoints`,
  `MapVendorPortalEndpoints`, `MapProviderHealthEndpoints`)

### `api/Data/DbSeeder.cs`
- **Line 15:** Comment out Lab B task seed
- **Lines 61–62:** Comment out `LocalizationSeedData.Seed(db)` call

**Do NOT delete any files** under `app/src/pages/Localization/` or
`api/Endpoints/Localization/` — they stay on disk for future re-enablement.
