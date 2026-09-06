# AI Learning Agent — Build Tracker

> Single source of truth for build progress. Update checkboxes as tasks ship.
> Architecture details live in
> [ai-learning-agent-ARCHITECTURE.md](ai-learning-agent-ARCHITECTURE.md);
> full context lives in
> [ai-learning-agent-SESSION-HANDOFF.md](ai-learning-agent-SESSION-HANDOFF.md).

**Last updated:** 2026-09-07
**Overall status:** Design complete — build not started

---

## Pre-build (before Phase 1)

- [x] Architecture & design specification written
- [x] LLM provider cascade locked (Muse + Nova Micro + Gemini free)
- [x] Build phases & timeline defined
- [x] Session handoff document created
- [x] This build tracker created
- [ ] Localization Lab disabled from running site (Gemini prompt produced,
      not yet executed by user)
- [ ] Python project directory created (e.g. `ai-agent/` at repo root)
- [ ] Python virtual environment + dependency management (pyproject.toml or
      requirements.txt)

---

## Phase 1 — The Substrate (weeks 1–5, target: mid-October 2026)

**Goal:** Working RAG tutor + eval harness. Interview-ready after this phase.

**Interview sentence:** "Naive RAG scored 0.62 context precision and 0.71
faithfulness on my 100-question golden set; AST-aware chunking + bge
cross-encoder reranker moved context precision to 0.84 and faithfulness
to 0.88."

### 1.1 Project scaffold
- [ ] FastAPI app scaffold (main.py, routers, config)
- [ ] Pydantic AI integration + Pydantic v2 schema setup
- [ ] LangGraph basic graph scaffold (single-node to start)
- [ ] Docker Compose integration with existing Postgres + React + .NET stack
- [ ] Environment config (.env, settings) for LLM provider keys
- [ ] Langfuse tracing integration (basic — trace every LLM call)
- [ ] Health check endpoint

### 1.2 Content ingestion pipeline
- [ ] Lesson content parser (read existing curriculum .md / seed data)
- [ ] Hierarchical chunking (H2 → H3 → H4 section boundaries)
- [ ] AST-aware chunking via tree-sitter (Java code blocks stay intact)
- [ ] Atomic MCQ chunking (one MCQ = one chunk)
- [ ] Metadata extraction per chunk (lesson_id, module_id, section_path,
      chunk_type, concept_tags, content_quality_tier)
- [ ] Embedding generation via OpenAI text-embedding-3-large (locked 2026-09-07)
- [ ] pgvector table creation + index
- [ ] tsvector column + GIN index for sparse search
- [ ] Ingestion script (run once, idempotent re-run)

### 1.3 RAG retrieval pipeline
- [ ] Dense retrieval (pgvector cosine similarity)
- [ ] Sparse retrieval (tsvector BM25-equivalent)
- [ ] Reciprocal Rank Fusion (merge dense + sparse results)
- [ ] Cross-encoder reranking (bge-reranker-v2-m3)
- [ ] Parent-document expansion (retrieve child, return parent section)
- [ ] Query rewriting for multi-hop questions
- [ ] Content-quality weighting in context assembly

### 1.4 Tutor Agent (single agent, Phase 1 version)
- [ ] Pydantic AI agent definition (system prompt, tools, output schema)
- [ ] RAG retriever as agent tool
- [ ] Citation enforcement (must cite source lesson/section)
- [ ] Content-boundary guardrail (refuse out-of-scope questions)
- [ ] Basic prompt injection detection
- [ ] Conversation history management
- [ ] WebSocket or SSE streaming for chat responses

### 1.5 Evaluation harness
- [ ] Golden eval set: write ~80–100 hand-written Q/A pairs
  - [ ] Single-lesson questions (~30)
  - [ ] Cross-lesson questions (~20)
  - [ ] Code-specific questions (~20)
  - [ ] Conceptual questions (~20)
- [ ] DeepEval integration (pytest runner)
- [ ] RAGAS metrics: context precision, context recall, faithfulness,
      answer relevancy
- [ ] Baseline measurement: naive 512-token chunking, single dense, top-k=5,
      no reranking
- [ ] Intervention measurements (one at a time):
  - [ ] AST + hierarchy chunking vs baseline
  - [ ] Hybrid search (dense + sparse) vs baseline
  - [ ] Cross-encoder reranking vs baseline
  - [ ] Parent-document expansion vs baseline
  - [ ] Query rewriting for multi-hop vs baseline
- [ ] Results documented with numbers (these become interview talking points)

### 1.6 Frontend (basic chat UI)
- [ ] Chat component (functional, not fancy — Gemini builds this)
- [ ] Message display with markdown rendering
- [ ] Citation display (link back to source lesson)
- [ ] Loading/streaming state
- [ ] Auth integration (reuse existing JWT)
- [ ] API client for the Python FastAPI service

### Phase 1 — Definition of Done
- [ ] User can chat with the tutor and get RAG-grounded answers
- [ ] Answers cite source lessons
- [ ] Eval harness runs and produces RAGAS metrics
- [ ] At least 3 intervention measurements show improvement over baseline
- [ ] Langfuse traces visible for every interaction
- [ ] All runs within $2/day budget cap

---

## Phase 2 — Multi-Agent + Personalization (weeks 6–10, target: late Nov 2026)

**Goal:** Full agent roster + adaptive learning. Significantly stronger
interview story.

**Interview sentence:** "Five agents orchestrated via LangGraph; the
assessment agent calibrates MCQ difficulty against the learner's mastery
state, and the model cascade cuts per-session cost 60% by routing simple
queries to an 8B model."

### 2.1 Intent router + model cascade
- [ ] Intent classification (Nova Micro): tutor | support | admin
- [ ] Complexity classifier (Nova Micro): simple → Nova Micro, complex → Muse
- [ ] LangGraph router node with branching
- [ ] Per-query model selection based on classification

### 2.2 Profiler Agent
- [ ] Pydantic AI agent definition
- [ ] User input collection (experience, skills, self-rating)
- [ ] Skill vector generation (per-concept mastery estimate)
- [ ] Recommended curriculum starting point
- [ ] `learner_profiles` table
- [ ] Optional: Git repo analyzer tool (read-only clone + static analysis)

### 2.3 Assessment Agent
- [ ] MCQ generation (4-option, calibrated difficulty, explanations)
- [ ] MCQ quality validation (LLM-as-judge: distractor plausibility,
      single correct answer, difficulty calibration)
- [ ] Quality score threshold for MCQ persistence
- [ ] MCQ persistence to `generated_mcqs` table for reuse
- [ ] Java exercise generation (problem + starter code + test cases)
- [ ] Difficulty calibration against learner's measured mastery level
- [ ] Per-concept pass rate tracking

### 2.4 Concept prerequisite knowledge graph
- [ ] Extract concept dependency DAG from Java LLD curriculum
- [ ] Store as `(concept_id, prerequisite_concept_id)` edges in PostgreSQL
- [ ] Tutor Agent: never teach before prerequisites are mastered
- [ ] Assessment Agent: generate questions at learner's frontier
- [ ] Nudge Agent: identify knowledge gaps

### 2.5 Learner memory model (3-layer, hybrid — locked 2026-09-07)
- [ ] L1 Raw traces (Postgres): `interaction_traces` table (every interaction logged)
- [ ] L2 Concept mastery (Postgres): `concept_mastery` table (per-concept score,
      pass rate, FSRS-computed next_review_at)
- [ ] L3 Learner profile (Mem0): free-text misconceptions, pace/style
      preferences — self-hosted Mem0 pointed at existing Postgres/pgvector
- [ ] LangGraph checkpointer + `PostgresSaver` for in-thread conversation state
      (separate from long-term memory above)

### 2.6 Nudge Agent
- [ ] Spaced repetition scheduling (FSRS or SM-2 variant)
- [ ] Proactive message generation based on:
  - [ ] Inactivity (days since last practice on a concept)
  - [ ] Declining pass rate
  - [ ] Progress summary ("8/12 topics mastered")
- [ ] Scheduled execution (not triggered per-message — periodic)

### 2.7 Java code execution sandbox
- [ ] Docker container setup (JDK, no network, CPU/memory caps, timeout)
- [ ] MCP tool definition for code execution
- [ ] Compile + run + test case comparison
- [ ] Feedback generation from execution results

### 2.8 MCP tool exposure
- [ ] RAG retriever as MCP tool
- [ ] Java code executor as MCP tool
- [ ] MCQ generator as MCP tool
- [ ] Concept graph navigator as MCP tool

### 2.9 Cost attribution
- [ ] Every LLM call tagged: user_id, agent_name, query_type, model_tier
- [ ] Per-agent cost aggregation in Langfuse
- [ ] Per-student cost tracking
- [ ] Budget cap enforcement (per-student daily, aggregate daily,
      per-agent hourly)

### Phase 2 — Definition of Done
- [ ] All 5 non-admin agents operational (Profiler, Tutor, Assessment,
      Nudge + router)
- [ ] MCQs generated, quality-validated, and persisted
- [ ] Java exercises compile and run in sandbox
- [ ] Concept graph drives adaptive question selection
- [ ] Spaced repetition scheduling produces sensible nudge messages
- [ ] Cost attribution visible per-agent and per-student
- [ ] Model cascade demonstrably reduces cost vs single-model

---

## Phase 3 — Support + Admin + Polish (weeks 11–14, target: late Dec 2026)

**Goal:** Complete system with support bot + admin automation. Full portfolio
piece ready for January 2027 interviews.

**Interview sentence:** "The support agent shares RAG infrastructure but
swaps corpus and persona; I red-teamed it with 30 adversarial cases —
containment rate 93%, zero prompt injection successes. The admin agent
automates policy-compliant refunds via Stripe and surfaces resolution
suggestions for edge cases."

### 3.1 Support Agent
- [ ] Different RAG corpus (help docs, FAQs, known issues)
- [ ] Different persona (support, not tutor)
- [ ] Account lookup tool
- [ ] Stripe API integration (test mode) for refund automation
- [ ] Auto-refund for eligible cases (under threshold, valid reason)
- [ ] Escalation path for non-eligible cases

### 3.2 Support bot red-team eval
- [ ] Write ~30 adversarial test cases:
  - [ ] Prompt injection attempts (~10)
  - [ ] Off-topic requests (~5)
  - [ ] Hallucination probes (~5)
  - [ ] Emotional/frustrated user scenarios (~5)
  - [ ] Edge cases (~5)
- [ ] Metrics: containment rate, correct-resolution rate,
      escalation appropriateness
- [ ] All results documented for interview

### 3.3 Admin Agent
- [ ] Resolution suggestions for support tickets
- [ ] Automated Stripe test-mode refund execution
- [ ] Pre-approved action types only — everything else is a suggestion
- [ ] Anomaly alerts on spend patterns

### 3.4 Admin dashboard
- [ ] Per-student progress view
- [ ] Per-agent cost attribution charts
- [ ] Automated action audit trail
- [ ] AI resolution suggestion log

### 3.5 Stripe test-mode integration
- [ ] Stripe test-mode API setup
- [ ] $0 refund demonstration flow
- [ ] Policy-based automation rules
- [ ] Audit trail for all automated actions

### 3.6 FDE vertical initial integration
- [ ] RAG over FDE content (same pipeline, different corpus partition)
- [ ] Design-question assessments (open-ended, LLM-judged with rubric)
- [ ] No auto-grading of FDE exercises in v1

### 3.7 UX polish
- [ ] Mode transitions (chat → MCQ → exercise → back to chat)
- [ ] MCQ interactive panel with hint system
- [ ] Code editor + output panel for exercises
- [ ] Support mode trigger ("Need help?")
- [ ] Responsive design

### 3.8 Demo narrative
- [ ] End-to-end demo script written
- [ ] Demo rehearsed and timed
- [ ] Key metrics documented (eval numbers, cost numbers, latency numbers)

### Phase 3 — Definition of Done
- [ ] Complete 6-agent system operational
- [ ] Support bot passes red-team evaluation
- [ ] Admin dashboard shows real cost/progress data
- [ ] Stripe test-mode refund demo works end-to-end
- [ ] FDE content accessible via same RAG pipeline
- [ ] Demo narrative rehearsed, timed, and polished
- [ ] Ready for January 2027 interview season

---

## Phase 4 — Stretch (January 2027, only if time allows)

- [ ] Self-hosted model on Mac Studio M1 Max (7B–8B for routing tier)
- [ ] Model Economics Matrix measurements (latency, cost, quality per model)
- [ ] BGE self-hosted embeddings vs OpenAI text-embedding-3-large comparison
      (cost/quality/latency) — deferred from Phase 1 decision
- [ ] Spaced repetition algorithm tuning (A/B test FSRS vs SM-2)
- [ ] Advanced UX polish (animations, transitions)

---

## Milestone dates

| Milestone | Target | Actual | Status |
|---|---|---|---|
| Architecture & design locked | 2026-09-07 | 2026-09-07 | ✅ Done |
| Localization disabled from site | 2026-09-08 (est.) | — | ⏳ Pending |
| Phase 1 start | 2026-09-08 (est.) | — | ⏳ Pending |
| Phase 1 complete (RAG + eval) | mid-October 2026 | — | ⏳ Pending |
| Phase 2 complete (multi-agent) | late November 2026 | — | ⏳ Pending |
| Phase 3 complete (full system) | late December 2026 | — | ⏳ Pending |
| Interview-ready | January 2027 | — | ⏳ Pending |
