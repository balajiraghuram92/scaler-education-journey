# ADR-001 — Orchestration framework: LangGraph vs LangChain vs CrewAI

**Status:** Accepted
**Date:** 2026-09-18
**Applies to:** AI Learning Agent (tutor) and Localization Lab

> **Honesty caveat — read this first.** This reasoning was newly constructed on
> 2026-09-18. It is **not** a retroactive record of a decision the project made
> earlier. What the repo actually contained before this file was:
> `ai-learning-agent-ARCHITECTURE.md` §2.2 asserting LangGraph in a one-line
> stack-table rationale, with no written comparison against alternatives — and
> `SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md` §4 explicitly
> flagging that *"CrewAI is not mentioned anywhere in this repo's actual
> architecture docs"* and that the earlier LangGraph-vs-CrewAI argument was
> *"Claude's own constructed argument… not a decision this project's notes ever
> actually recorded being made."* This file closes that gap. It is reasoning to
> be checked against your own judgement, not history to be recited.

---

## 1. Context

Two systems in this repo need LLM orchestration, and they have genuinely
different shapes. Treating them as one decision is what made the earlier
discussion circular.

| | AI Learning Agent (tutor) | Localization Lab |
|---|---|---|
| Status | Phase 1.1 in progress, critical path | .NET/React side built and verified; AI layer unbuilt; **on hold** (`ai-learning-agent-ARCHITECTURE.md` §14) |
| Control flow | Conditional fan-out, retry loops, human-in-the-loop pause | Straight pipeline with two conditionals |
| Persisted state | Yes — learner model, hint-disclosure position | No — per-string, stateless |
| Current blocker | Scaffolding | Three .NET stubs throwing `NotImplementedException` → HTTP 501 |

---

## 2. Decision

1. **Tutor → LangGraph.** Unchanged. This is correct and load-bearing.
2. **Localization Lab → LangChain**, when it comes off hold. This is the
   framework's genuine best fit in this repo, not a keyword exercise.
3. **CrewAI → neither product.** Timeboxed standalone sandbox only, for
   interview trade-off reasoning. Explicitly not wired into anything.

---

## 3. Reasoning

### 3.1 Why LangGraph owns the tutor

The tutor has four committed features that are LangGraph's actual
differentiators — not things a linear chain expresses cleanly:

- **Conditional fan-out** — the Router classifies intent and dispatches to one
  of Tutor / Support / Admin (`ai-learning-agent-ARCHITECTURE.md` §3.3).
- **Cycles** — the retrieval-sufficiency retry loop and the validation/repair
  loop (`RETRIEVE → GRADE_EVIDENCE → GENERATE → VALIDATE → REPAIR`, carried over
  from the chatbot HLD §16.4). A chain runs forward once; this has to go
  backward on a failed grade.
- **Persisted, resumable state** — the progressive hint-disclosure state machine
  has to remember which hint tier a learner has already been given, across
  requests.
- **Human-in-the-loop interrupt** — the Admin Agent pauses for approval on
  anything outside pre-approved action types (§3.2, Admin Agent). This is
  LangGraph's `interrupt` primitive; simulating it in a chain means inventing a
  state store and a resume path by hand.

Any one of these is arguable. All four together is the case.

### 3.2 Why LangChain fits the Localization Lab, and why that is not a contrivance

The pending pipeline (`localization-lab-ARCHITECTURE-AND-WORKFLOW.md` Part E.5)
is:

```
Legacy MT (Google, stays in .NET)
  → semantic cache check (pgvector)   [conditional: hit / miss]
  → MT Optimize (glossary-grounded LLM call)
  → QPS score (LLM-as-judge) + COMET-Kiwi (local model)
  → auto-route                        [conditional: >= threshold / below]
```

Linear, forward-only, two conditionals, no persisted state, no resumption, no
human pause inside the pipeline (human review happens *after*, via the existing
Marketplace flow). **Reaching for LangGraph here would be ceremony.** That is
the point — it makes the tool choice honest in both directions.

LangChain earns its place on specifics, not vibes:

- **Provider abstraction** over vLLM's OpenAI-compatible endpoint (Part F.5) —
  the design already calls for swapping providers by config, not rewrite.
- **Structured output parsing** for the QPS score + flagged-issues payload
  (Part F.2, `POST /qps-score`).
- **Vector store + embeddings interface** for the pgvector semantic cache
  (Part E.2) — `PGVector` is a first-class LangChain integration against the
  Postgres 16 instance that already exists.

And it comes attached to the thing that defeats the interview anti-patterns:
Part E.4 already specifies a golden eval set, COMET-Kiwi, glossary-adherence and
placeholder-preservation checks, and `EvalRun` rows. The LangChain usage ships
with measurement, not as a bare dependency.

### 3.3 Why CrewAI gets no seat

- It has **no honest home**. The tutor's six agents are already coordinated by
  LangGraph with explicit state. The Localization Lab's roles (vendors bidding
  on jobs) are **human** vendors in a marketplace, not agents — modelling them
  as a crew would be fiction.
- The user's own market research names *"Multi-agent theater — many agents, no
  eval, no reason"* as a red flag interviewers report
  (`info/localization-design/compass_artifact_wf-*.md` §1.7). Bolting CrewAI on
  would walk directly into it.
- What that same research says is actually tested is **trade-off reasoning**:
  interviewers ask *"LangChain or CrewAI, and why?"* and want reasoning, not
  brand loyalty (line 42). You satisfy that by being able to say why you did
  *not* pick it, with hands-on grounding. That costs about a day in a throwaway
  sandbox — not an architectural commitment.

---

## 4. On LangChain in the tutor specifically

Keep it minimal and keep it late. The market doc's actual prescription is
*"Raw provider SDK first (hand-written loop), then LangChain/LangGraph wrapper
for the ATS keyword and stateful multi-turn"* (line 153) — wrapper **after**
mechanism, explicitly for resume keyword coverage. It does not argue for
LangChain being architecturally load-bearing in the tutor.

Concretely: the text-splitter / document-loader spot in Phase 1.2 ingestion is a
real, small, honest fit (and `neuralascent-chatbot-hld-python-LangChain.md` §9.1
gives compatible semantic-chunking guidance). Do that. Do not expand it.

**Note on the four HLD drafts.** `architecture-notes/` holds
`-python-LangChain.md`, `-JAVA-LANGCHAIN.md`, and `-dotnet-Semantic-Kernal.md`,
plus earlier copies under `references/`. These are stack-*variant* drafts of the
same chatbot from when the stack was undecided — LangChain appears in the Python
one and Semantic Kernel in the .NET one because those are each ecosystem's
default name. They are **not** independent evidence that LangChain is right, and
all are superseded by `ai-learning-agent-ARCHITECTURE.md`.

---

## 5. The interview answer this buys

> "Two systems, two different tools, for reasons I hit in practice. The tutor
> runs on LangGraph because the hint-disclosure state machine has to persist
> where a learner is across requests, the retrieval grader loops backward on
> insufficient evidence, and the admin agent has to pause for human approval —
> those are graph primitives, and I'd have been hand-rolling a state store to
> fake them in a chain. The localization pipeline is LangChain, because it's
> genuinely linear: MT, cache check, glossary-grounded refinement, judge, route.
> I used LangChain's PGVector retriever and structured output there and skipped
> the graph machinery entirely, because there was nothing to persist. I looked
> at CrewAI for the localization marketplace and didn't use it — the roles there
> are human vendors, not agents, and a role-play abstraction over a
> deterministic pipeline would have cost me the ability to measure each stage."

Every claim in that paragraph is checkable against code that exists.

---

## 6. What would reverse this

- **Tutor → LangChain** if the agent roster collapses to one agent with no retry
  loop and no admin approval. (Would contradict §3.2 and Phase 2.)
- **Localization → LangGraph** if the pipeline gains a resumable human-approval
  pause *inside* it, or a repair cycle back into MT Optimize on a failed QPS
  score. Part E.5 currently routes to human review *after* the pipeline, which
  is why it stays a chain.
- **CrewAI → real seat** if a genuinely agent-to-agent negotiation task appears
  (agents bidding against agents, not vendors bidding on jobs).

---

## 7. Sources in this repo

| Claim | Source |
|---|---|
| Six-agent roster, router fan-out, Admin human-in-the-loop | `ai-learning-agent-ARCHITECTURE.md` §3.2–3.3 |
| LangGraph asserted with one-line rationale, no comparison | `ai-learning-agent-ARCHITECTURE.md` §2.2 |
| Localization Lab on hold | `ai-learning-agent-ARCHITECTURE.md` §14 |
| Pipeline shape, FastAPI contracts, pgvector cache, eval harness | `localization-lab-ARCHITECTURE-AND-WORKFLOW.md` Parts E–F |
| .NET stubs throwing 501, verified live end-to-end | `localization-lab-STATUS-TRACKER.md` §1, §3.1 |
| CrewAI absent from architecture; prior argument flagged as constructed | `SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md` §4 |
| ATS keyword; "LangChain or CrewAI, and why"; multi-agent theater; SDK-first-then-wrap | `info/localization-design/compass_artifact_wf-*.md` lines 5, 42, 57, 118, 153 |
| Retrieve→grade→generate→validate→repair chain | `architecture-notes/neuralascent-chatbot-hld-python-LangChain.md` §16.4 |
