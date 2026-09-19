# Session 2026-09-19 — LangGraph scaffold, orchestration ADR, Langfuse-next decision

**Purpose of this file**: if you're picking this up in a brand-new chat, read
this before doing anything else. It covers everything since
[SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md](SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md)
(read that one too — it has the working-style rules this session followed).

---

## 0. Orientation — read these two things first

1. **`CLAUDE.md`** (repo root) — the hard write-permission rule. Claude may
   only write: `CLAUDE.md` itself, the memory directory, `info/.notes/`, and
   `exercises/` (new ones only).
2. **The broadened "hand-written by user" rule**, from
   `SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md` §1.1: for the AI
   Learning Agent and its supporting infra (`ai-agent/` Python code,
   `docker-compose.yml`, deploy scripts), Claude does **not** draft
   copy-paste-ready code, diffs, or scaffolds — not even framed as "just a
   toy example, you still write the real one." Claude explains the concept,
   points at exactly what needs to change (file, line, shape of the fix), and
   the user writes it. Illustrative toy examples with deliberately different
   names (e.g. `toy_graph.py` instead of the user's real file) are the one
   accepted workaround for "show me code" requests — they're shown in chat,
   never written to disk in the repo.

---

## 1. What got done this session

### 1.1 Pydantic AI integration — confirmed complete
`/echo` returns a real Meta Muse Spark 1.3 call, 200 OK,
`{"message": "say hi"}`. The fix that made it work:
`Agent(output_type=PromptedOutput(EchoResult))` in
[ai-agent/echo_agent.py](../../ai-agent/echo_agent.py) — Muse rejects forced
tool-calling (`tool_choice` other than `"auto"`), which is Pydantic AI's
default output strategy, so `PromptedOutput` avoids that path entirely.

### 1.2 LangGraph one-node scaffold — built, debugged, verified working
This was the main work this session. Three rounds of bugs, all diagnosed by
Claude and fixed by the user (per the hand-written rule above):

**Round 1** (first draft, files named `agent_test.py` at repo root +
`routers/test_agentGraph.py` — collided in name with the existing
`routers/agent_test.py` echo router):
- `typing_extentions` / `TypeDict` typos (should be `typing_extensions` /
  `TypedDict`)
- Node returned `{"Ouput_txt": ...}` — didn't match the schema's declared
  `output_txt` field (typo + case mismatch)
- `builder.add_edge(END, "root_step")` — backwards; should be
  `add_edge("root_step", END)` (nothing may flow *out* of `END`)
- Router did `from agent_test import agent_test` but the module only
  exported `agent_graph` — `ImportError`

**Round 2** (renamed cleanly: `echo_agent.py` alone at root, old
`routers/agent_test.py` deleted, new `ai-agent/echo_graph.py` +
`routers/test_agent.py` (echo) + `routers/test_graph.py` (LangGraph)):
- Naming collision resolved — good clean split, no more ambiguity
- Edge direction fixed correctly
- Import name fixed correctly
- One bug remained: node returned `{"Output_txt": ...}` (capital O) vs.
  schema's `output_txt` (lowercase o) — still a case mismatch

**Round 3** — fixed. Verified live:
```
GET /agent_test → 200
{"input_txt": "Hello", "output_txt": "graph says: Hello"}
```
This confirms `START → root_step → END` compiles and runs correctly, and the
node's partial-dict return merges into state as expected.

**Current final file state** (for a fresh session to orient against):
- [ai-agent/echo_graph.py](../../ai-agent/echo_graph.py) — the `StateGraph`
  module (`AgentGraph` TypedDict, `node()`, `builder`, `agent_graph = builder.compile()`)
- [ai-agent/routers/test_graph.py](../../ai-agent/routers/test_graph.py) —
  `GET /agent_test`, calls `agent_graph.invoke(...)`
- [ai-agent/routers/test_agent.py](../../ai-agent/routers/test_agent.py) —
  the renamed echo router (was `routers/agent_test.py`), `GET /echo`
- [ai-agent/main.py](../../ai-agent/main.py) — imports
  `health, identity, test_agent, test_graph`, all four `include_router`'d
- [ai-agent/requirements.txt](../../ai-agent/requirements.txt) —
  `langgraph==1.2.11` added, resolved cleanly with no new conflicts (its
  `langchain-core<2,>=1.4.7` / `pydantic>=2.7.4` deps were already satisfied)

**Note on naming, if a new session touches this again:** `echo_graph.py` is a
placeholder/toy name for the *scaffold*, not what Phase 2's real orchestrator
graph should be called. When the six-agent router graph from
`ai-learning-agent-ARCHITECTURE.md` §3.3 gets built, it should get its own
clearly-different name (e.g. `tutor_graph.py` or `orchestrator.py`) — don't
let the real thing quietly inherit the scaffold's name.

### 1.3 Real-use-case research: does LangChain/CrewAI have a genuine home here?
Prompted by the user's push-back that "theory will always be hypothetical,
only practical will provide accurate understanding." Full research trail and
conclusions are written up as
**[ADR-001-orchestration-framework-choice.md](ADR-001-orchestration-framework-choice.md)**
— read that file in full before re-litigating this question. Short version:

- **Tutor → LangGraph**, unchanged. Four concrete features justify it: router
  fan-out, the retrieval-sufficiency retry/repair cycle, persisted
  hint-disclosure state, and the Admin Agent's human-in-the-loop pause.
- **Localization Lab → LangChain**, when that project comes off hold. Its
  designed-but-unbuilt AI pipeline (Legacy MT → semantic cache → MT Optimize →
  QPS score → auto-route,
  [localization-lab-ARCHITECTURE-AND-WORKFLOW.md](localization-lab-ARCHITECTURE-AND-WORKFLOW.md)
  Part E.5) is a genuinely linear pipeline — reaching for LangGraph there
  would be ceremony. LangChain's real fit: provider abstraction over vLLM,
  structured-output parsing for QPS scores, and a `PGVector` retriever for
  the semantic cache.
- **CrewAI → neither product.** No honest home in either system (tutor
  already has 6 LangGraph-coordinated agents; the Lab's "roles" are human
  vendors, not agents). Recommendation: a timeboxed (~1 day) disconnected
  sandbox script, purely so "LangChain or CrewAI, and why?" — a real
  interview question per the user's own market-research doc,
  `info/localization-design/compass_artifact_wf-*.md` line 42 — has a
  hands-on answer behind it.
- **Correction of an earlier overstatement**: a prior response in this
  conversation (before this session) claimed the Python-LangChain HLD in
  `architecture-notes/` was "a real, reasoned design" that should shift
  LangChain's role in the tutor upward. That's overstated — it's one of
  three parallel stack-variant drafts (`-python-LangChain.md`,
  `-JAVA-LANGCHAIN.md`, `-dotnet-Semantic-Kernal.md`) from when the stack was
  undecided; LangChain/Semantic Kernel appear in each because that's each
  ecosystem's default name, not independent evidence. All three are
  superseded by `ai-learning-agent-ARCHITECTURE.md`. ADR-001 §4 has the
  correction in writing.
- Also fixed: the earlier "no labprojects directory exists" finding (from
  before this session) was wrong — the **Localization Lab** *is* that
  project (`LabProjects.jsx` entry point, `.NET`/React side built and
  verified per
  [localization-lab-STATUS-TRACKER.md](localization-lab-STATUS-TRACKER.md)),
  just not named literally "labprojects" on disk.

**Files touched for this:**
- New: [ADR-001-orchestration-framework-choice.md](ADR-001-orchestration-framework-choice.md)
- Edited: `ai-learning-agent-ARCHITECTURE.md` (§13 decision 9, §15 file index)
- Edited: `SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md` (§4 now
  has a "RESOLVED 2026-09-18" banner pointing at the ADR — the open question
  there does **not** need to be re-asked)

### 1.4 Langfuse vs LangSmith — verified via live web search (2026-09-19)
User asked which one enterprises actually use. Checked rather than answered
from memory (Claude's training cutoff predates 2026 market data). Findings:
- Langfuse: 2,300+ companies, 63 Fortune 500 companies, 12M+ monthly SDK
  downloads for the OSS platform. Acquired by ClickHouse, Jan 2026.
- LangSmith wins when a team is already deep in the LangChain/LangGraph
  ecosystem (native integration). Langfuse wins for OSS-first, self-hosted,
  regulated/EU-resident teams (trace data — which can hold full
  prompts/completions — never leaves your infra).
- **For this project specifically**: Langfuse remains the right call. It's
  self-hostable (matches the "no new infra cost" pattern already followed for
  Postgres/pgvector), and since the tutor stack is Pydantic AI + LangGraph
  rather than LangChain-heavy, LangSmith's main advantage doesn't apply here
  anyway. This is a legitimate, specific interview answer, not "I used the
  free one."

### 1.5 Sequencing decision: Langfuse before Docker Compose
User asked directly for a recommendation on the two remaining Phase 1.1
items. Decision: **Langfuse tracing next, Docker Compose dev-integration
last.** Reasoning (full version in the conversation, condensed here):
1. Isolates variables — verify tracing against a known-working local
   (non-containerized) run first, so a failure can't be ambiguously blamed on
   Docker networking/env-passthrough.
2. Langfuse has its own open provisioning decision (self-hosted vs. Cloud,
   key pair) flagged back in the Sep-15 session and still unresolved — worth
   settling on its own, not bundled with a container change.
3. Docker Compose integration is comparatively mechanical: the `ai-agent`
   service already exists in `docker-compose.yml` from Phase 0; what's
   missing is just the `docker-compose.dev.yml` override (host port +
   live-reload mount), matching the shape the `api`/`app` services already
   use there. No new concept to learn, so no benefit to front-loading it.
4. Makes Docker Compose a natural capstone: "prove FastAPI + Pydantic AI +
   LangGraph + Langfuse all come up together in the real Compose stack" as
   one final integration pass.

**This was not yet started.** Next session should open with: explain what
Langfuse actually captures (traces/spans/generations) and the two hook
points in this codebase (Pydantic AI's `Agent`, the LangGraph node in
`echo_graph.py`), then let the user decide self-hosted vs. Cloud before any
code gets touched.

---

## 2. Current git state

Uncommitted at end of session (per `git status --short`):
```
 M ai-agent/main.py
 M ai-agent/requirements.txt
 D ai-agent/routers/agent_test.py
 M info/.notes/SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md
 M info/.notes/ai-learning-agent-ARCHITECTURE.md
 M info/.notes/ai-learning-agent-BUILD-TRACKER.md
?? ai-agent/echo_graph.py
?? ai-agent/routers/test_agent.py
?? ai-agent/routers/test_graph.py
?? info/.notes/ADR-001-orchestration-framework-choice.md
?? info/.notes/SESSION-2026-09-19-langgraph-scaffold-and-adr.md
```
None of this has been committed or pushed. Run `git status --short` first to
confirm this hasn't drifted before trusting it.

---

## 3. Pending — the actual remaining work

### 3.1 Phase 1.1 (2 items left, see build tracker for full detail)
- [ ] **Langfuse tracing** — next up. Needs: self-hosted vs. Cloud decision +
      key pair, then instrument `echo_agent.py`'s `Agent` and
      `echo_graph.py`'s node.
- [ ] **Docker Compose dev-integration** — after Langfuse. Add an `ai-agent`
      entry to `docker-compose.dev.yml` (host port publish + live-reload
      mount), matching the existing `api`/`app` service shape there.

### 3.2 Longer-horizon, not urgent
- Deepinfra account + API key, needed before Phase 1.2's real embedding work
- The CrewAI sandbox exercise from ADR-001 §3.3 (timeboxed, disconnected,
  purely for interview trade-off reasoning — not on the critical path)
- LangChain text-splitter spot in Phase 1.2 ingestion (small, deliberate,
  per ADR-001 §4 — keep it minimal, don't let it grow)
- Optional/deferred: `config.py` → `pydantic-settings` upgrade (not blocking)

---

## 4. Key decisions made this session (don't re-litigate)

- LangGraph for the tutor, LangChain for the (on-hold) Localization Lab,
  CrewAI in neither product — see ADR-001, now recorded as decision 9 in
  `ai-learning-agent-ARCHITECTURE.md` §13.
- Langfuse (not LangSmith) for tracing — already the architecture doc's
  choice; re-confirmed this session with live 2026 market data, not just
  restated from memory.
- Langfuse tracing gets built before the Docker Compose dev-integration,
  not after — see §1.5 above for the four reasons.
- The `echo_graph.py` scaffold's name is a placeholder for the *scaffold
  step only* — Phase 2's real orchestrator graph must get its own distinct
  name, per the naming-collision lesson learned this session.

---

## 5. If you're a fresh LLM session reading this cold

1. `git status --short` — confirm section 2's snapshot still holds.
2. Read `CLAUDE.md` and this file's §0 — confirm the write-permission and
   hand-written-code rules haven't changed.
3. Read `ADR-001-orchestration-framework-choice.md` in full if the
   LangChain/LangGraph/CrewAI question comes up again — it's resolved, don't
   re-derive it from scratch.
4. Ask the user whether to start Langfuse tracing (the agreed next step) or
   something else has taken priority since this was written.
