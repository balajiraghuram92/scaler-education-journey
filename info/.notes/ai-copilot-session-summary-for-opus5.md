# Session Summary — Neuralascent AI Copilot: Context for Implementation Planning

**Purpose of this file:** condensed record of a planning conversation, handed to Opus 5 to produce a concrete implementation plan for the Neuralascent AI Copilot. Written to stand alone — no other conversation context assumed.

---

## 1. Why this project exists

The user is executing a **26-week plan** to transition from a Java/backend (Unity, 7–8 years experience) background into an **AI Engineering role**, targeting offers by **February 2027**. Employed through December 2026, then likely on a bench with more available hours. Budget: 12–15 hrs/week now, 20–30 hrs/week once on bench.

The **Neuralascent AI Copilot** — an AI tutor/chatbot layered onto an existing personal learning platform (Java/Spring + AI curriculum content) — is the vehicle for this transition. The website itself (`scaler-education-journey` repo: React frontend in `app/`, C# ASP.NET Core API in `api/`, Postgres) was already built by the user using AI (Claude Sonnet 5), with deliberately high-quality curriculum content, specifically to serve as **test infrastructure for building a real AI/LLM chatbot on top of it**. The website is not the deliverable; the chatbot-building process is.

Full 26-week plan detail: application tiering strategy, tool picks (pgvector, LangGraph, hosted embeddings, Langfuse, RAGAS, etc.), week-by-week build sequence (retrieval+eval Weeks 3–8, agent+guardrails Weeks 9–13, MCP+cost governance Weeks 14–17, multimodal/localization Weeks 18–21, packaging Weeks 22–26) — this document doesn't restate all of it; ask the user for the full plan text if needed, or see prior session context.

## 2. The design to build from — do not deviate

**Explicit instruction from the user: follow the existing HLD faithfully, even if it takes longer than the 26-week plan's original pacing implies.**

The authoritative design document is:
[`info/.notes/Chatbot-implementation/architecture-notes/neuralascent-chatbot-hld-python-LangChain.md`](Chatbot-implementation/architecture-notes/neuralascent-chatbot-hld-python-LangChain.md)

This HLD (dated 2026-08-31, already written before this session) specifies:
- **Stack**: Python, FastAPI, LangChain (LangGraph optional/later), PostgreSQL + pgvector, SQLAlchemy + Alembic
- **Use case**: context-aware learner assistance for Java LLD exercises — exact DB lookup for the current lesson/exercise first, RAG only for knowledge outside that exact context (prerequisites, cross-vertical questions, "was this taught earlier")
- **Core design principles**: exact context first, retrieval only when useful, metadata-before-similarity filtering, model-is-not-an-authorization-engine, progressive hint disclosure (5 levels: conceptual nudge → structural hint → pseudocode → partial code → full solution), retrieved text treated as untrusted data, structured LLM I/O contracts, graceful fallback
- **Full architecture**: component diagram, sequence diagrams, domain class diagram (`ChatController` → `ChatOrchestrator` → `ContextResolver`/`RoutePolicyEngine`/`RetrievalService`/`PromptAssembler`/`TutorModelClient`/`ResponseGuardrail`/`ConversationService`), relational ER diagram, full Postgres schema (§12), API design (start conversation, streaming SSE message endpoint, feedback endpoint), security/privacy controls (prompt injection defense, server-side authorization, content-leakage prevention), reliability/fallback flowchart, observability spec, evaluation strategy (router dataset, retrieval dataset, tutor dataset, product metrics), and its own **4-phase implementation plan** (§22): Phase 0 discovery/policy → Phase 1 current-context tutor (no RAG) → Phase 2 content indexing + filtered RAG → Phase 3 routing + cross-vertical retrieval → Phase 4 improve only from measured evidence.

**A previously-drafted narrower "Week 1–2" design note** ([`copilot-week1-2-design-overview.md`](copilot-week1-2-design-overview.md)) scoped the build down to just ingestion + naive retrieval (5 classes, skipping auth/routing/guardrails for later). That was written before the "don't deviate from the HLD" instruction — **Opus 5 should treat the HLD's own Phase 0–4 sequencing as authoritative** and reconcile/replace that narrower note rather than assume it still stands. Whether Phase 1's "no RAG yet" ordering or the 26-week plan's "naive RAG as Week 1–2 eval control group" ordering wins is an open call — see §5.

## 3. Repo structure (existing, factual — read before planning)

```
scaler-education-journey/          (repo root, will likely be renamed/split per Week 0 of the 26-week plan — not yet done)
├── api/                            C# ASP.NET Core — existing platform, DO NOT rewrite
│   ├── Endpoints/                  Minimal API style (ExerciseEndpoints.cs, ImportEndpoints.cs, V2Endpoints.cs)
│   ├── Models/                     Lesson.cs, CourseModule.cs, Problem.cs, Course.cs, etc.
│   ├── Data/                       Seed data, schema.sql, DbSeeder.cs
│   └── ...
├── app/                            React frontend — existing platform, DO NOT rewrite
├── copilot/                        DOES NOT EXIST YET — this is what's being built (Python/FastAPI, per the HLD)
├── docker-compose.yml              prod compose — database (currently postgres:16-alpine, NEEDS to become
│                                    pgvector/pgvector:pg16), api, app services
├── docker-compose.dev.yml          dev overlay
├── info/.notes/                    reference docs + Local-LLM prompt files (Claude may read/write here)
│   └── Chatbot-implementation/architecture-notes/   the three chatbot HLD variants (Python/LangChain,
│       .NET/Semantic Kernel, Java/LangChain4j) — Python/LangChain one is the chosen path
└── CLAUDE.md                       repo rules (see §4)
```

Key existing schema facts (from `api/Models/*.cs`): `lessons` table has `content_body` (markdown), `content_status` ('Outline'/'Draft'/'Published'/'Archived'), `slug`, `title`; joins to `course_modules` via `module_id`. No explicit "Tier-1" flag exists anywhere — if the plan's "ingest Tier-1 lessons" language matters, that needs a definition (currently assumed as `content_status = 'Published'`, unconfirmed).

## 4. Repo constraints (binding, from `CLAUDE.md`)

Claude does not have permission to edit/create/delete files in this repo directly, **except**: `CLAUDE.md` itself, the Claude memory directory, `info/.notes/`, and `exercises/`. For all other file changes, Claude's role is to produce fully-specified, copy-paste-ready prompts for a **Local LLM** that the user runs themselves to make the actual edits.

## 5. Working-mode split — established this session, binding going forward

This is the most important operational constraint for whatever plan Opus 5 produces:

- **`copilot/` (the Python/AI side — chunking, embeddings, retrieval, LangChain/LangGraph orchestration, eval harness, guardrails, agent control flow)** → **the user writes all of this by hand.** No code generation, no Local LLM prompts, for this side. AI's role here is limited to design (diagrams, explanations, trade-offs) and post-hoc code review. Rationale: this is the actual interview-relevant skill-building; the whole point of the project is the user personally being able to defend these design choices under follow-up questioning, not having a working demo fast.
- **`api/` and `app/` (the existing .NET/React platform — anything needed to support the chatbot: auth gating, a paywall/usage-limit so the chatbot isn't abused, new endpoints the copilot needs, DB schema additions)** → business as usual for this repo: Claude drafts a Local LLM prompt, the user runs it through their Local LLM.

**Implication for Opus 5's plan**: any plan should clearly tag each deliverable/task as "Python/copilot — user hand-codes, get design support only" vs ".NET/React — Local LLM prompt workflow," so the boundary doesn't get blurred during execution.

## 6. Language/stack clarifications settled this session (for context, not decisions needed)

- Python is required for AI Engineer roles; Java stays relevant mainly for the adjacent "backend/platform engineer on an AI product team" path the 26-week plan also targets.
- FastAPI is Python-only, not language-agnostic; it's conceptually parallel to ASP.NET Core Minimal APIs (which the existing `api/Endpoints/` already uses) — same lightweight philosophy, different ecosystem, not interchangeable.
- Explicitly decided **against** migrating/rewriting the existing .NET backend to Python "for the practice" — rejected as low interview value, high risk to a working system, and directly contradicted by the HLD's own recommendation to keep this a modular monolith addition rather than a rewrite.

## 7. Open tensions Opus 5 should resolve or flag back to the user

1. **LangChain vs. raw provider SDKs.** The HLD (§16) recommends LangChain as the primary AI composition library, LangGraph optional/later. The user's broader 26-week plan's tool-pick table says the opposite — "Provider SDKs directly... LangChain's chain and retriever abstractions hide the exact layer you're interviewed on" and "LangGraph, nothing above it." The user just said "don't deviate from the HLD, even if it takes time" — this may mean they've decided to follow the HLD's LangChain-first approach over the 26-week plan's raw-SDK stance, or it may mean they only meant "don't deviate from the HLD's architecture/phases" without having weighed this specific tool conflict. **Worth confirming explicitly before committing a plan to one or the other**, since it affects nearly every file in `copilot/`.
2. **Phase sequencing**: HLD's own Phase 1 ships a working tutor with *no* RAG at all (exact-context lookup only) before Phase 2 adds indexing/retrieval. The 26-week plan's Week 1–2 wants a naive RAG pipeline immediately as an eval control group, with the eval harness (golden set, hit@5/MRR) starting Week 3. These aren't strictly incompatible (Phase 1 could be built without needing an eval harness at all, since it doesn't retrieve), but the ordering of "build RAG" vs. "build the exact-context tutor" needs to be picked.
3. **"Tier-1 lessons"** is 26-week-plan language with no corresponding field in the actual schema — needs a concrete definition before ingestion scope is unambiguous.
4. **Chatbot access gating / paywall** (mentioned by the user as needed on the `.NET` side to prevent misuse) has no design yet in the HLD beyond generic "authenticate every chat request" (§18.1) — needs its own small spec before a Local LLM prompt can be drafted for it.

## 8. Current status

Nothing under `copilot/` has been created. No docker-compose changes have been made. No Local LLM prompts have been executed. This session produced only reference/planning documents under `info/.notes/`:
- This file
- [`copilot-week1-2-design-overview.md`](copilot-week1-2-design-overview.md) — narrower scoping note, likely superseded per §2/§7.2 above
- [`copilot-week1-2-fastapi-foundation-prompt.md`](copilot-week1-2-fastapi-foundation-prompt.md) — an earlier Local-LLM-prompt draft that incorrectly had the Local LLM write Python retrieval-pipeline logic; **superseded and should not be used** (violates §5's working-mode split).

## 9. What's being asked of Opus 5

Produce a concrete implementation plan for the Neuralascent AI Copilot that:
- Follows the HLD at §2 as the architectural source of truth
- Resolves or explicitly surfaces the open tensions in §7 (especially the LangChain question — recommend confirming with the user first)
- Respects the hand-coding/Local-LLM-prompt boundary in §5
- Produces a sequence of concrete, buildable milestones the user can execute personally on the `copilot/` side, sized to their available hours (12–15 hrs/week through December 2026)
