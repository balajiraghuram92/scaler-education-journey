# Neuralascent — Work Status & Resume Point

> **Current as of 2026-09-07.**

**Last updated:** 2026-09-07

---

## Active tracks

### 1. AI Learning Agent (PRIMARY — all portfolio energy goes here)

**Status:** Design phase — architecture spec written, no implementation started.
**Spec:** [ai-learning-agent-ARCHITECTURE.md](ai-learning-agent-ARCHITECTURE.md)
**Handoff:** [ai-learning-agent-SESSION-HANDOFF.md](ai-learning-agent-SESSION-HANDOFF.md) — read this first in any new session
**Tracker:** [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)
**Timeline:** Build through Dec 2026, interview-ready Jan 2027.

This is the user's **primary portfolio project** for AI-role job applications.
It replaces the previously-planned Projects A (RAG tutor), B (content quality
audit), and C (code execution grounding) as a single unified system.

**What it is:** An AI-first personalized learning tutor for Neuralascent — the
agent IS the primary interface, not a sidebar chatbot. Multi-agent system
(Profiler, Tutor, Assessment, Nudge, Support, Admin) built in Python
(Pydantic AI + LangGraph + FastAPI) as a separate microservice, using existing
Java LLD/FDE content as RAG data.

**Stack:** Python, FastAPI, Pydantic AI, LangGraph, pgvector, DeepEval,
Langfuse, MCP. Existing React/.NET stays as legacy.

**Build phases:**
- Phase 1 (weeks 1-5, target mid-Oct): RAG + eval harness + single tutor agent
- Phase 2 (weeks 6-10, target late Nov): Multi-agent + personalization
- Phase 3 (weeks 11-14, target late Dec): Support bot + admin + Stripe demo
- Phase 4 (stretch): Self-hosted model comparison, advanced UX

**LLM providers (LOCKED):** Meta Muse Spark 1.3 Contributor (primary) +
Amazon Nova Micro on Bedrock (routing/batch) + Gemini free tier (eval judge).
**Open decisions:** Mem0 vs custom PostgreSQL for learner memory, embeddings
provider (OpenAI vs BGE).

### 2. Localization Lab — ON HOLD

**Status:** Disabled from the running site (prompt produced 2026-09-07, not
yet executed by user). Will resume after the AI Learning Agent ships.

All code stays on disk — routes, imports, DI registrations, endpoint mappings,
and seed data are commented out, not deleted.

**Full status:** [localization-lab-STATUS-TRACKER.md](localization-lab-STATUS-TRACKER.md)

---

## Completed (committed to `main`)

### Auth / TOTP / AI Chat system
Self-serve signup → admin approval → mandatory TOTP MFA → AI chat with $2/day
budget cap. Committed across multiple commits ending at `a660f95`. Backend was
never compiler-verified in Claude's environment — user has since committed
"fixed compiler issues" commits, but exact fixes were not reviewed by Claude.

**Full record:** [SESSION-2026-09-AI-chatbot-planning-and-auth-build.md](SESSION-2026-09-AI-chatbot-planning-and-auth-build.md)

---

## Parked indefinitely

### AI vertical curriculum content (Model Economics Matrix etc.)
Hand-authored only per CLAUDE.md §0. No longer a priority track — the AI
Learning Agent project subsumes the interview-portfolio motivation. May
revisit as stretch content later.

---

## Order of work
AI Learning Agent (all phases) → Localization Lab (resume) → everything else.
