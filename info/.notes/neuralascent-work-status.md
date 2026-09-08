# Neuralascent — Work Status & Resume Point

> **Current as of 2026-09-08.**

**Last updated:** 2026-09-08

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

**Stack (revised 2026-09-08):** Fresh TypeScript frontend + Python FastAPI
backend — **no reuse of the existing React/.NET codebase** for the new tutor
UI (supersedes the earlier "existing site stays as legacy" framing). Pydantic
AI, LangGraph, pgvector, DeepEval, Langfuse, MCP unchanged. Embedding +
reranking run **local-first on a Mac Studio M1 Max (32GB)** over an SSH
tunnel, UPS-backed always-on, with cloud API fallback on the same model
weights if the Mac/tunnel is down.

**Routing:** `neuralascent.top` stays on .NET through Phase 0–2 (new stack
lives on a dev subdomain/path); Nginx flips the domain to the new stack in
Phase 3 once feature + auth parity is reached. Auth is shared, not
duplicated — FastAPI validates the existing .NET-issued JWTs.

**Build phases:**
- Phase 0 (added 2026-09-08, before Phase 1): infra scaffold — FastAPI on a
  dev subdomain, Mac Studio SSH tunnel + API fallback, fresh TS frontend
  scaffolded
- Phase 1 (weeks 1-5, target mid-Oct): RAG + eval harness + single tutor agent
- Phase 2 (weeks 6-10, target late Nov): Multi-agent + personalization
- Phase 3 (weeks 11-14, target late Dec): Support bot + admin + Stripe demo +
  routing cutover to the new stack
- Phase 4 (stretch): local-vs-API model economics writeup, advanced UX

**LLM providers (LOCKED):** Meta Muse Spark 1.3 Contributor (primary) +
Amazon Nova Micro on Bedrock (routing/batch) + Gemini free tier (eval judge).
**Open decisions:** Mem0 vs custom PostgreSQL for learner memory.

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
