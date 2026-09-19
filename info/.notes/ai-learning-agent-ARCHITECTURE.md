# AI Learning Agent — Architecture & Design Specification

> **Living document.** Update this file as decisions are made and phases ship.
> This is the single source of truth for the AI Learning Agent project on
> Neuralascent — read it before touching any agent code.

**Last updated:** 2026-09-08
**Status:** Design phase — no implementation started

---

## 0. Purpose & positioning

### What this is
A personalized, AI-first learning platform built on top of Neuralascent's
existing Java LLD and FDE curriculum content. The AI tutor agent IS the
primary learning interface — not a sidebar chatbot bolted onto a traditional
LMS. **Revised 2026-09-08:** the learner-facing frontend is a fresh
TypeScript build (no reuse of the existing `app/` React/JSX), talking to a
**separate Python FastAPI microservice**. The .NET API is not kept on
indefinitely as "legacy" — it is cut over in stages (see §2.4 Routing &
cutover plan) and either retired or reduced to whatever isn't yet ported.

### Why this exists
This is the user's **primary portfolio project for AI-role job applications**
targeting ₹40–60+ LPA Applied/GenAI Engineering positions at Indian services
firms and mid-size product companies (Jan 2027 job search). It replaces the
previously-planned Projects A (RAG tutor), B (content quality audit), and C
(code execution grounding) as a single unified system that covers every
interview-relevant cluster:

| Interview cluster | How this project demonstrates it |
|---|---|
| RAG depth | Hierarchical + AST-aware chunking over real curriculum content, hybrid search, reranking |
| Agentic workflows | Multi-agent architecture with explicit agent roles, stateful orchestration |
| Evaluation | Golden eval set, RAGAS metrics, MCQ quality calibration, tutoring effectiveness |
| Cost governance | Model cascade, per-student/per-agent cost attribution, budget caps |
| Tool use | Sandboxed Java code execution, MCQ generation, git analysis |
| MCP | Tools exposed via MCP protocol |
| Multi-agent | 5-6 specialized agents with justifiable separation of concerns |
| Observability | OpenTelemetry + Langfuse tracing, cost dashboard |
| Production hardening | Auth (already built), rate limiting, guardrails, prompt injection defense |
| LLM-as-judge | MCQ quality scoring, tutoring answer evaluation |

### What this is NOT
- Not a SaaS product — it's a portfolio piece with real depth
- Not a replacement for the .NET API — that stays for legacy content serving
- Not the AI-vertical curriculum content (that's hand-authored per CLAUDE.md
  §0) — this is AI integration (site infrastructure)

---

## 1. Core concept

### The learner experience (UX vision)
The interface is a **conversational workspace** — similar to Claude's chat
interface but purpose-built for learning:

- **Chat mode (default):** AI tutor converses with the learner, delivers
  curriculum content via RAG, explains concepts, answers questions. The tutor
  follows the existing Java LLD / FDE curriculum structure but adapts pacing
  and depth to the learner's measured mastery.
- **MCQ mode:** When the tutor decides to assess (or the learner requests it),
  the chat minimizes to the side and an interactive MCQ panel takes focus.
  The agent watches the learner's answer selection in real-time and provides
  contextual hints via a non-intrusive UI element. After submission, results
  flow back into the conversation with explanation.
- **Exercise mode:** For Java exercises, the workspace shifts to a code
  editor + output panel. The agent monitors the code, can provide hints, and
  scores the solution via sandboxed execution. Results and feedback integrate
  back into the conversation.
- **Support mode:** The same interface, but the agent persona switches from
  tutor to support bot. Different RAG data (help docs, FAQs, known issues
  instead of curriculum content). Accessible via a "Need help?" trigger.
- **Admin view:** Dashboard showing per-student progress, per-agent cost
  attribution, AI-suggested resolutions for support tickets, automated
  action log (e.g. Stripe test-mode refunds).

The key UX principle: **one interface, multiple modes** — the agent drives
the mode transitions based on context, not manual page navigation.

Frontend implementation will be built using AI assistance (Gemini/etc.) — the
user's hand-written work is the **Python AI layer**, which is the
interview-defensible core.

### The AI's behavior model
The agent is NOT a passive Q&A bot. It is:

1. **Curriculum-aware** — follows the existing Java LLD / FDE topic ordering,
   respects concept prerequisites
2. **Personalized** — adapts to the learner's measured skill level, pace,
   and knowledge gaps
3. **Proactive** — nudges the learner to engage, suggests next topics,
   increases/decreases assessment frequency based on pass rate
4. **Grounded** — all tutoring answers are RAG-grounded in the existing
   curriculum content, with citations
5. **Measurably effective** — every interaction contributes to a learner
   model that tracks mastery per concept

---

## 2. Architecture

### 2.1 System topology

```
┌──────────────────────────────────────────────────────────┐
│                    React Frontend                         │
│  (Chat UI + MCQ panel + Code editor + Admin dashboard)   │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼─────────────────────────────────────┐
│              Python FastAPI Service                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           LangGraph Orchestrator                     │ │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐           │ │
│  │  │ Profiler  │ │  Tutor   │ │Assessment │           │ │
│  │  │  Agent    │ │  Agent   │ │  Agent    │           │ │
│  │  └──────────┘ └──────────┘ └───────────┘           │ │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐           │ │
│  │  │  Nudge   │ │ Support  │ │  Admin    │           │ │
│  │  │  Agent   │ │  Agent   │ │  Agent    │           │ │
│  │  └──────────┘ └──────────┘ └───────────┘           │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌──────────────┐ ┌────────────┐ ┌──────────────────┐   │
│  │  RAG Engine  │ │ Eval Engine│ │ Tool Registry    │   │
│  │  (pgvector + │ │ (DeepEval +│ │ (MCP protocol)   │   │
│  │   BM25)      │ │  RAGAS)    │ │                  │   │
│  └──────────────┘ └────────────┘ └──────────────────┘   │
│  ┌──────────────┐ ┌────────────┐ ┌──────────────────┐   │
│  │ Learner      │ │ Langfuse   │ │ Cost Governor    │   │
│  │ Memory Store │ │ Tracing    │ │                  │   │
│  └──────────────┘ └────────────┘ └──────────────────┘   │
└────────────────────┬─────────────────────────────────────┘
                     │
    ┌────────────────┼────────────────────────┐
    │                │                        │
┌───▼────┐    ┌──────▼──────┐    ┌────────────▼───────────┐
│Postgres│    │ LLM Provider│    │ Sandboxed Java         │
│(pgvec- │    │ (API or     │    │ Executor (Docker)      │
│ tor)   │    │  self-hosted│    │                        │
│        │    │  via vLLM)  │    │                        │
└────────┘    └─────────────┘    └────────────────────────┘
```

### 2.2 Technology stack

| Layer | Technology | Rationale |
|---|---|---|
| **Agent logic** | Pydantic AI (v1.0) | Type-safe, FastAPI-style ergonomics, 44% faster P95 than LangGraph alone, automatic output validation via Pydantic v2 |
| **Orchestration** | LangGraph | Stateful graph for multi-agent coordination, branching, human-in-the-loop. Pydantic AI agents drop into LangGraph nodes. In production at Uber, JPMorgan, Replit |
| **API serving** | FastAPI | Standard for Python AI services, async, OpenAPI docs |
| **Vector store** | pgvector (on existing Postgres 16) | No new infra, already in the stack |
| **Sparse search** | PostgreSQL tsvector / pg_trgm | BM25-equivalent for exact term matching, hybrid with dense |
| **Embeddings** | OpenAI text-embedding-3-large (or BGE) | Proven quality; BGE as self-hostable alternative |
| **Reranking** | bge-reranker-v2-m3, **local-first via Mac Studio** (revised 2026-09-08) | Cross-encoder reranking is a strong-hire interview signal; API cost was pricing out too high, moved local with API fallback — see §2.4 |
| **Eval framework** | DeepEval | pytest-style, CI-gatable, RAGAS-compatible metrics |
| **Observability** | Langfuse (open-source) | LLM tracing, cost tracking, eval integration, self-hostable |
| **Structured output** | Pydantic v2 | Schema enforcement for all LLM outputs |
| **Memory** | Custom PostgreSQL tables + Mem0 (evaluate) | Learner state, conversation history, concept mastery |
| **Tool protocol** | MCP (Model Context Protocol) | Standardized tool access; hot interview topic |
| **Code execution** | Docker sandbox (JDK, no network, resource caps) | Safe Java code compilation and execution |
| **LLM providers** | Multi-provider cascade — see §2.3 | Meta Muse (primary), Amazon Nova Micro/Bedrock (routing), Gemini free tier (eval) |
| **Embeddings** | One model, **local-first via Mac Studio**, cloud API fallback on the same weights (revised 2026-09-08) | Never swap embedding models after the corpus is indexed — vectors from different models aren't comparable, a swap forces a full re-embed |
| **Local inference host** | Mac Studio M1 Max, 32GB, SSH tunnel from AWS, UPS-backed always-on | Runs embedding + reranking; cuts API spend, doubles as a model-economics data point |
| **Frontend** | **Fresh TypeScript build** (revised 2026-09-08 — supersedes "React existing + new components") | Built with AI assistance, not hand-written |

### 2.3 LLM provider cascade (locked 2026-09-07)

Three-provider cascade: Meta (primary), AWS Bedrock (routing/bulk/batch),
Google (eval judging). Chosen for cost, interview signal, and to avoid
eval self-preference bias.

| Tier | Model | $/MTok (in/out) | RPM | Use case |
|---|---|---|---|---|
| **Primary (quality)** | Meta Muse Spark 1.3 Contributor | $0.10 / $0.20 | 60 | Tutor Agent, Assessment Agent, complex reasoning, exercise generation |
| **Routing + Bulk** | Amazon Nova Micro (Bedrock) | $0.035 / $0.14 | high | Intent router, complexity classifier, nudge messages, admin summaries |
| **Batch eval runs** | Amazon Nova Micro Batch (Bedrock) | $0.0175 / $0.07 | async | Golden set evaluation (50% off, async — eval doesn't need real-time) |
| **Eval judging** | Google Gemini free tier (Flash models) | $0 | 10-15 | RAG eval judge, MCQ quality validation (different provider = no bias) |

**Why Muse Contributor:** Cheapest output tokens ($0.20/MTok vs $0.40
everywhere else) while being the highest-quality model in the set. The
contributor tier trains on prompts/completions — acceptable for a portfolio
project using public curriculum content, not proprietary data. The 60 RPM
cap is fine for development/demo; for production, position as "I'd move to
standard tier or self-hosted." **Access confirmed from India** (UPI-based
registration on Meta developer console, tested via Muse Code, 2026-09-07).

**Why Nova Micro on Bedrock:** Cheapest model on Bedrock ($0.035/$0.14),
Bedrock-native = IAM auth (no separate API key), existing EC2 infra,
batch inference at 50% off for async eval workloads. Text-only, 128K
context — sufficient for routing/classification tasks.

**Why Gemini free tier for eval:** Using a different provider for eval
judging than for generation avoids self-preference bias — a documented
LLM-as-judge pitfall and a strong interview answer. The free tier (10-15
RPM, Flash models, no card required) is sufficient for eval runs that
happen a few times per week, not per session.

**Estimated costs:**
- Per session (one learner, ~30 min): ~$0.014
- Per eval run (100 Q/A, batch): ~$0.007
- Monthly (30 sessions/day): ~$13-15
- 4-month build phase total: ~$50-60

The existing $2/day budget cap is more than sufficient. No credits needed.

**Note (revised 2026-09-08):** the Mac Studio is not used for the LLM
routing tier — Nova Micro still owns that. It's used for embedding +
reranking instead; see §2.4.

**Interview narrative:** "Provider-agnostic cascade across three providers —
Meta Muse for quality-sensitive tutoring at $0.20/MTok output, Amazon Nova
Micro on Bedrock for routing at $0.035/MTok with batch inference at 50% off
for eval runs, and Gemini free tier as the eval judge to avoid self-preference
bias. Per-session cost is $0.014; I can attribute cost per-agent and per-
student from Langfuse traces."

---

### 2.4 Local inference host & routing/cutover plan (added 2026-09-08)

**Embedding + reranking — local-first, API fallback:**
Cross-encoder reranking via API was pricing out too high for this project's
usage pattern. Both embedding and reranking now run **locally on a Mac
Studio M1 Max (32GB)**, reached from the AWS host over an SSH tunnel, kept
always-on and UPS-backed. Cloud API keys for the *same model weights* are
provisioned as automatic fallback if the Mac or tunnel goes down. This is
deliberate: it cuts recurring API spend, and the local-vs-API split (cost,
latency, uptime) becomes its own model-economics data point for the
interview story.

**Hard rule:** the embedding model, once the corpus is indexed, is never
swapped. A different model's vectors are not comparable to the existing
index — switching would require re-embedding the entire corpus, not just
new content. The local and fallback paths must therefore serve the *same*
model weights, not merely "an equivalent" model.

**Model choice (locked 2026-09-08):** **BAAI/bge-m3** for embedding,
**bge-reranker-v2-m3** for reranking. Both run locally on the M1 Max 32GB
via `FlagEmbedding`/`sentence-transformers` on the MPS (Metal) backend, and
both are hosted as-is (same weights) on **Deepinfra** as the API-parity
fallback — satisfies the "same weights on both sides" rule exactly.
`bge-m3` natively outputs dense + sparse (lexical) + multi-vector
representations from one model, which can serve the hybrid dense/sparse
retrieval directly (tsvector remains a simpler fallback for the sparse leg
if preferred).

**Toggle model — manual, no auto-fallback (locked 2026-09-08):** unlike a
typical HA design, this project deliberately does **not** auto-fail over
from local to API. Instead:
- An **admin-panel global toggle** (`embedding_backend`, `reranker_backend`
  ∈ {local, api}) read per-request — flip it live, no redeploy. This is the
  default dev/testing mode, used to collect real local-vs-API cost/latency
  data (the model-economics interview story).
- A **per-account override** (e.g. a `force_api_backend` flag on a specific
  login) that always forces the API path regardless of the global toggle —
  used for interview demos so the demo never depends on the home Mac/WiFi
  being reachable.
- Both paths implement the same `EmbeddingProvider`/`RerankerProvider`
  interface; only the factory branches on (account override) → (admin
  toggle). Agent/RAG code never branches on this itself.
- An admin-panel health indicator ("Mac: reachable/unreachable") is shown
  next to the toggle so a bad flip is visible before it causes failed
  requests — acceptable to fail loudly here, this is a personal project,
  not something needing silent resilience.
- Every call is still Langfuse-tagged by which backend actually served it,
  regardless of toggle position.

**SSH tunnel setup (Mac Studio, home WiFi → AWS, locked 2026-09-08):** the
Mac has no public IP, so it initiates a **reverse SSH tunnel** to AWS:
```
autossh -M 0 -N \
  -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" \
  -o "ExitOnForwardFailure yes" \
  -R 127.0.0.1:9000:127.0.0.1:8001 \
  ai-tunnel@<aws-host>
```
- Binds port 9000 on AWS's **loopback only** (not `0.0.0.0`) to the Mac's
  local embedding/rerank service on 8001 — FastAPI (same AWS host) calls
  `http://127.0.0.1:9000`. No `GatewayPorts` needed since only same-host
  FastAPI needs to reach it.
- `autossh`, not plain `ssh`, so home-WiFi drops auto-reconnect.
- Runs as a `launchd` agent on the Mac (starts on boot, restarted on death)
  — Mac Studio is always-on so this is simple.
- Dedicated, restricted SSH key on the AWS side's `authorized_keys`:
  `command="/bin/false",no-pty,no-X11-forwarding,no-agent-forwarding,permitopen="127.0.0.1:8001" ssh-ed25519 AAAA... mac-studio-tunnel`
  — this key can only open that one forwarded port even if it leaked.
- No further hardening (static home IP, VPN, security-group source-IP
  lock) — explicitly accepted as unnecessary for a personal project with a
  restricted key already in place.

**Routing & cutover (same AWS public IP/host as today):**

1. **Today:** `neuralascent.top` → .NET API/site (Nginx), unchanged.
2. **Phase 0:** stand up the new FastAPI service on the same host; Nginx
   adds a dev-only subdomain or path (e.g. `tutor.neuralascent.top` or
   `/agent/*`) pointing at it. `neuralascent.top` itself is untouched.
   **This is DNS + Nginx only, not a .NET change:**
   - Add a DNS A record for `tutor` → the same AWS public IP (or a
     `*.neuralascent.top` wildcard record if more subdomains are likely
     later), wherever the domain's DNS is managed.
   - Add a new Nginx `server_name tutor.neuralascent.top` block that
     proxies to the FastAPI process's local port; the existing `.NET`
     server block for the bare domain is untouched.
   - Extend the TLS cert with a SAN for the new subdomain (or rely on an
     existing wildcard cert if one is already in place).
3. **Phases 1–2:** the new TypeScript frontend + FastAPI backend are built
   out behind that subdomain/path. Auth is **not** duplicated — FastAPI
   validates the JWTs the existing .NET auth system already issues (shared
   secret/keys), so there's no second login system to build or maintain.
4. **Phase 3:** once the new stack has full feature + auth parity, Nginx is
   flipped so `neuralascent.top` routes directly to the new stack. The .NET
   API is then kept only for anything not yet ported, or retired.

---

## 3. Agent architecture (multi-agent detail)

### 3.1 Why multi-agent (the interview answer)

"Single-agent becomes untenable when the system needs to maintain distinct
state machines — a learner's knowledge model, an assessment difficulty
calibrator, and a proactive engagement scheduler all have different update
frequencies, failure modes, and evaluation criteria. Separating them lets me
test, trace, and cost-attribute each independently."

### 3.2 Agent roster

#### Profiler Agent
- **Trigger:** First login, explicit profile update, or periodic re-assessment
- **Input:** User-provided experience, resume, git project links, self-rated
  skills, past MCQ/exercise performance
- **Output:** Skill vector (per-concept mastery estimate), recommended
  starting point in curriculum, difficulty tier
- **State:** `learner_profiles` table
- **Tools:** Git repo analyzer (read-only clone + static analysis), resume
  parser
- **Interview signal:** Personalization via structured user modeling, not
  just chat history

#### Tutor Agent (primary)
- **Trigger:** Every learner message in chat mode
- **Input:** Learner query + conversation history + current concept context +
  learner profile + RAG-retrieved content
- **Output:** Grounded, cited response following scaffolded tutoring stages:
  1. **Investigate** — probe what the learner already knows
  2. **Guide** — incremental hints, not full answers
  3. **Explain** — deliver the concept with curriculum-grounded content
  (Inspired by DeepTutor's three-stage scaffolding model)
- **RAG:** Hybrid retrieval (pgvector dense + tsvector sparse) → cross-encoder
  rerank → parent-document expansion
- **State:** Conversation history, current topic/concept
- **Tools:** RAG retriever, concept graph navigator
- **Guardrails:** Must cite source lesson/section; must refuse to answer
  outside curriculum scope; prompt injection detection

#### Assessment Agent
- **Trigger:** Tutor agent decides it's time to assess (based on concept
  coverage), or learner requests practice
- **Input:** Current concept, learner mastery state, difficulty tier
- **Output:**
  - MCQs: 4-option, calibrated difficulty, with explanation for each option
  - Java exercises: problem statement + starter code + test cases
- **MCQ generation:** LLM-generated with quality validation (distractor
  plausibility, single correct answer verification, difficulty calibration
  against learner's measured level)
- **MCQ persistence:** When a generated MCQ passes quality checks, persist
  it to the backend DB for reuse (reduces future generation cost)
- **Exercise scoring:** Compile + run learner's Java code in sandbox, compare
  against test cases, provide feedback
- **State:** Per-concept pass rates, difficulty history, generated MCQ bank
- **Tools:** Java code executor (MCP tool), MCQ quality validator
- **Interview signal:** Adaptive difficulty calibration, LLM-as-judge for
  MCQ quality, tool use for code execution

#### Nudge Agent (proactive)
- **Trigger:** Scheduled check (not every message — periodic, e.g. daily)
- **Input:** Learner's last activity timestamp, mastery state, pass rate
  trends, incomplete topics
- **Output:** Proactive message suggesting next action:
  - "You haven't practiced Strategy Pattern in 3 days — want a quick MCQ?"
  - "Your pass rate on SOLID dropped last week — let's review DIP"
  - "You've mastered 8/12 Java LLD topics — here's what's left"
- **Algorithm:** Evidence-based spaced repetition (FSRS or SM-2 variant) for
  concept review scheduling, NOT random pings
- **State:** Engagement history, spaced repetition schedule
- **Interview signal:** Proactive agent behavior (not just reactive),
  evidence-based algorithms, scheduled agent execution

#### Support Agent
- **Trigger:** User clicks "Need help?" or types a support-related query
- **Input:** User's issue description + account state
- **Output:** Diagnosis, resolution suggestion, or escalation
- **RAG data:** Different corpus — help docs, FAQs, known issues, account
  state (NOT curriculum content)
- **Tools:** Account lookup, Stripe API (test mode) for refund automation
- **Eval:** Red-team test suite (prompt injection, off-topic, hallucination
  probes, adversarial edge cases)
- **Interview signal:** Same RAG infrastructure, different corpus + persona =
  demonstrates versatility; red-team eval = security awareness

#### Admin Agent
- **Trigger:** Admin accesses dashboard, or automated escalation from
  Support Agent
- **Input:** Support tickets, usage analytics, cost data
- **Output:** Resolution suggestions, automated actions (e.g. Stripe
  test-mode refund), anomaly alerts
- **Tools:** Stripe API (test mode), usage analytics queries, cost
  attribution reports
- **Automation scope:** Only pre-approved action types (refunds under
  threshold, standard resolutions); anything else is a suggestion, not an
  auto-action
- **Interview signal:** AI-assisted operations, human-in-the-loop for
  high-stakes decisions, Stripe integration

### 3.3 Agent orchestration (LangGraph)

```
                    ┌─────────────┐
                    │   Router    │
                    │  (classify  │
                    │   intent)   │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
     │   Tutor     │ │ Support  │ │   Admin     │
     │   Agent     │ │  Agent   │ │   Agent     │
     └──────┬──────┘ └──────────┘ └─────────────┘
            │
     ┌──────▼──────┐
     │ Assessment  │ (Tutor decides when to assess)
     │   Agent     │
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │   Nudge     │ (Scheduled, reads learner state)
     │   Agent     │
     └─────────────┘

     Profiler Agent runs on first login and periodic re-assessment,
     outside the main conversation loop.
```

---

## 4. RAG pipeline detail

### 4.1 Content ingestion

**Source data:** Existing Neuralascent curriculum — ~17 deep "Tier-1" lessons
(Modules 1-4) on Java LLD + FDE, plus ~165 thin machine-templated drafts in
later modules. Content includes prose, code samples, MCQs, and exercises.

**Chunking strategy (the interview-critical piece):**

| Content type | Strategy | Rationale |
|---|---|---|
| **Prose** | Recursive splitting by heading hierarchy (H2 → H3 → H4), respecting section boundaries | Preserves pedagogical structure; a chunk is always a complete concept explanation |
| **Code blocks** | AST-aware splitting via tree-sitter (Java parser) — functions/classes stay intact | Prevents shredding code across chunk boundaries; interview talking point ("cAST chunking") |
| **MCQs** | Atomic — one MCQ = one chunk, with metadata (topic, difficulty, source) | MCQs are self-contained units |

**Metadata stored per chunk:**
- `lesson_id`, `module_id`, `section_path` (e.g. "Module 3 > SOLID > DIP")
- `chunk_type` (prose | code | mcq | exercise)
- `concept_tags` (extracted concepts, normalized)
- `content_quality_tier` (Tier-1 deep vs thin draft — affects retrieval
  weighting to avoid over-favoring the 17 dense lessons)
- `embedding_vector` (pgvector)
- `tsvector` (for BM25-equivalent sparse search)

### 4.2 Retrieval pipeline

```
Query → Query Rewriting (for multi-hop) →
  ├── Dense search (pgvector cosine similarity)
  └── Sparse search (tsvector BM25-equivalent)
→ Reciprocal Rank Fusion (merge dense + sparse) →
→ Cross-encoder reranker (bge-reranker-v2-m3) →
→ Parent-document expansion (retrieve child, return parent section) →
→ Concept-prerequisite filter (don't retrieve concepts the learner
   hasn't reached yet, unless explicitly asked) →
→ Context assembly (with content-quality weighting)
```

### 4.3 Concept prerequisite knowledge graph

Extract a concept dependency DAG from the existing Java LLD curriculum:

```
OOP Basics → Encapsulation → Abstraction → Interfaces
                                              ↓
           SOLID Principles → SRP → OCP → LSP → ISP → DIP
                                                        ↓
           Design Patterns → Strategy → Factory → Observer → ...
```

Stored in PostgreSQL as `(concept_id, prerequisite_concept_id)` edges.

**Used by:**
- Tutor Agent: never teaches a concept before prerequisites are mastered
- Assessment Agent: generates questions at the learner's frontier, not
  randomly
- Nudge Agent: identifies knowledge gaps ("you scored well on Strategy but
  weak on DIP")

---

## 5. Learner memory model

### 5.1 Three-layer memory (inspired by DeepTutor's trace forest)

| Layer | What it stores | Update frequency | Used by |
|---|---|---|---|
| **L1 — Raw traces** | Every interaction logged (messages, MCQ attempts, exercise submissions, time-on-task) | Every interaction | Eval engine, admin analytics |
| **L2 — Concept mastery** | Per-concept mastery score (0.0–1.0), last-assessed timestamp, pass rate, misconception patterns | After each assessment | Tutor, Assessment, Nudge agents |
| **L3 — Learner profile** | Synthesized profile: skill tier, learning pace, preferred explanation style, knowledge frontier | Periodic (daily or on significant state change) | All agents, personalization |

### 5.2 Data model (PostgreSQL)

```
learner_profiles:
  user_id (FK to app_users), skill_vector (jsonb),
  current_frontier_concept_id, learning_pace_category,
  total_concepts_mastered, last_profile_refresh_at

concept_mastery:
  user_id, concept_id, mastery_score (decimal),
  attempts_count, pass_rate (decimal),
  last_assessed_at, next_review_at (FSRS-computed),
  misconception_notes (text[])

interaction_traces:
  id, user_id, agent_name, interaction_type (chat|mcq|exercise|nudge),
  input_summary, output_summary, tokens_used, cost_usd,
  latency_ms, created_at

generated_mcqs:
  id, concept_id, question_text, options (jsonb),
  correct_option_index, explanation, difficulty_tier,
  quality_score (decimal), times_served, pass_rate,
  source_type ('LLM_GENERATED'), created_at
```

---

## 6. Evaluation harness

### 6.1 RAG evaluation (golden set)

- **Size:** ~80–120 hand-written Q/A pairs
- **Structure per item:** question, gold answer, gold source lesson/section,
  query type tag (single-lesson | cross-lesson | code-specific | conceptual)
- **Metrics:** context precision, context recall, faithfulness, answer
  relevancy (via RAGAS/DeepEval)
- **Reference thresholds:** faithfulness ≥0.75, answer relevancy ≥0.80,
  context precision ≥0.70, context recall ≥0.80
- **Baseline:** naive fixed-size (512-token) chunking, single dense retrieval,
  top-k=5, no reranking
- **Measured interventions (one at a time):**
  1. AST + hierarchy chunking
  2. Hybrid search (dense + sparse)
  3. Cross-encoder reranking
  4. Parent-document expansion
  5. Query rewriting for multi-hop
- **Cost per eval run:** ~$0.001–0.003 per test case with LLM-judged eval

### 6.2 MCQ quality evaluation

- Difficulty calibration accuracy (does the MCQ's rated difficulty match
  actual pass rate across learners?)
- Distractor quality (are wrong answers plausible but clearly wrong?)
- Single correct answer verification (LLM cross-check)
- Quality score threshold for persistence to backend

### 6.3 Tutoring effectiveness

- Learning gain: pre-test vs post-test delta per concept
- Time-to-mastery per concept
- Retention: performance on spaced-repetition reviews
- Engagement: session length, return rate, nudge response rate

### 6.4 Support bot evaluation (red-team suite)

- ~30 adversarial test cases:
  - Prompt injection attempts
  - Off-topic requests (try to use support bot as general AI)
  - Hallucination probes (ask about non-existent features)
  - Emotional/frustrated user scenarios
- Metrics: containment rate, correct-resolution rate, escalation
  appropriateness

### 6.5 Agent-level evaluation

- Per-agent: latency, token consumption, cost, error rate
- Router accuracy: does intent classification route to the correct agent?
- Multi-agent coordination: do agent handoffs maintain conversation context?

---

## 7. Cost governance

### 7.1 Model cascade (locked 2026-09-07)

| Query complexity | Model | Estimated cost/query |
|---|---|---|
| Routing / classification | Nova Micro — Bedrock ($0.035/$0.14 MTok) | ~$0.00005 |
| Simple (MCQ delivery, nudge messages) | Nova Micro — Bedrock | ~$0.0002 |
| Standard tutoring (RAG-grounded) | Muse Spark 1.3 Contributor ($0.10/$0.20 MTok) | ~$0.001 |
| Complex (exercise gen, multi-hop) | Muse Spark 1.3 Contributor | ~$0.003 |
| Eval judging (RAGAS, MCQ quality) | Gemini free tier ($0) | ~$0 |
| Batch eval runs (golden set) | Nova Micro Batch — Bedrock ($0.0175/$0.07 MTok) | ~$0.00007/question |

### 7.2 Cost attribution

Every LLM call tagged with:
- `user_id` — per-student cost tracking
- `agent_name` — per-agent cost attribution
- `query_type` — what kind of work this was
- `model_tier` — which model handled it

Admin dashboard shows: daily/weekly spend by agent, by student, by query
type. Alerts on anomalous spend patterns.

### 7.3 Budget caps

- Per-student daily cap (inherited from existing $2/day design, adjustable)
- Aggregate daily cap across all students
- Per-agent hourly cap (prevents a runaway agent loop)

---

## 8. Observability

- **Langfuse integration:** every agent call gets a trace with spans for
  retrieval, LLM call, tool execution, response assembly
- **OpenTelemetry:** standard traces/metrics/logs for the FastAPI service
- **Cost dashboard:** real-time spend tracking, per-agent attribution
- **Eval dashboard:** RAG metric trends over time, MCQ quality distribution

---

## 9. Security & guardrails

- **Auth:** existing TOTP-gated JWT auth (already built, §1 of session
  handoff)
- **Prompt injection defense:** input validation layer before any LLM call;
  detect and reject injection attempts
- **Output validation:** Pydantic schema enforcement on all LLM outputs;
  reject malformed responses
- **Code execution sandbox:** Docker container with no network, CPU/memory
  caps, execution timeout
- **Content boundary:** Tutor agent must only answer from curriculum content;
  out-of-scope questions get a clear refusal, not a hallucinated answer
- **Rate limiting:** per-user, per-endpoint (existing ASP.NET rate limiting
  covers the .NET layer; FastAPI layer needs its own)

---

## 10. FDE vertical — approach

FDE (Forward Deployed Engineering) content is more tricky than Java LLD
because:
- Less structured — system design topics don't have clean "right answer"
  MCQs
- Exercises are design exercises, not code exercises — harder to auto-grade
- Content may reference external systems, architectures, case studies

**Initial approach (Java LLD first, FDE second):**
- Phase 1-2: Java LLD only (MCQs + Java exercises + code execution)
- Phase 3+: FDE integration via:
  - RAG over FDE content (same pipeline, different corpus partition)
  - Design-question assessments (open-ended, LLM-judged)
  - User provides git links, logs, architecture docs → agent analyzes and
    provides feedback
  - No auto-grading of FDE exercises in v1 — LLM-as-judge with structured
    rubric instead

---

## 11. Stripe integration (demo / support bot showcase)

- **Purpose:** Demonstrate AI-assisted admin operations, not a real payment
  system
- **Scope:** Stripe test mode only, $0 refund demonstrations
- **Flow:**
  1. Support agent receives a refund-related query
  2. Agent classifies the issue, checks policy rules
  3. If auto-refund eligible (under threshold, valid reason): executes
     Stripe test-mode refund via API
  4. If not eligible: suggests resolution to admin, logs for human review
  5. Admin dashboard shows: automated actions taken, resolution suggestions,
     audit trail
- **Interview signal:** AI agent with real tool integration, human-in-the-
  loop for high-stakes decisions, policy-based automation

---

## 12. Build phases

### Phase 0 — Infra & routing scaffold (added 2026-09-08, before Phase 1, ~3-5 days)
**Goal:** New stack reachable and provable-working end-to-end before any
tutor logic exists, with zero disruption to the live .NET site.

- [ ] FastAPI skeleton deployed on the same AWS host/public IP
- [ ] Nginx: add dev-only subdomain or path (e.g. `tutor.neuralascent.top`
      or `/agent/*`) → FastAPI; `neuralascent.top` still → .NET, unchanged
- [ ] FastAPI JWT-validation middleware against existing .NET-issued tokens
- [ ] SSH tunnel from Mac Studio M1 Max into the AWS host, verified stable
- [ ] Local embedding + reranking service running on the Mac Studio
- [ ] Cloud API fallback (same model weights) wired in and tested by
      killing the tunnel and confirming failover
- [ ] Fresh TypeScript frontend project scaffolded (not the existing `app/`)

### Phase 1 — The substrate (weeks 1-5, target: mid-October 2026)
**Goal:** Working RAG tutor + eval harness. Interview-ready after this phase.

- [ ] Python project scaffold (FastAPI + Pydantic AI + LangGraph)
- [ ] Content ingestion pipeline (parse existing lessons, chunk, embed via
      the locked local-first embedding model)
- [ ] pgvector setup on existing Postgres
- [ ] Single Tutor Agent with RAG retrieval
- [ ] Golden eval set (~80-100 Q/A pairs)
- [ ] Baseline measurements (naive chunking)
- [ ] Intervention measurements (hybrid search, reranking, AST chunking)
- [ ] Chat UI in the new TypeScript frontend (functional, not fancy)
- [ ] Langfuse tracing integration, tagged by local-vs-API-fallback path
- [ ] Docker Compose integration with existing stack

**Interview sentence after Phase 1:**
"Naive RAG scored 0.62 context precision and 0.71 faithfulness on my
100-question golden set; AST-aware chunking + bge cross-encoder reranker
moved context precision to 0.84 and faithfulness to 0.88."

### Phase 2 — Multi-agent + personalization (weeks 6-10, target: late Nov)
**Goal:** Full agent roster + adaptive learning. Significantly stronger
interview story.

- [ ] Profiler Agent (skill vector from user input)
- [ ] Assessment Agent (MCQ generation + difficulty calibration)
- [ ] Concept prerequisite knowledge graph
- [ ] Learner memory model (3-layer: traces → mastery → profile)
- [ ] Model cascade (cheap → mid → expensive routing)
- [ ] Nudge Agent (spaced repetition scheduling)
- [ ] Java code execution sandbox (Docker)
- [ ] MCP tool exposure
- [ ] Per-agent cost attribution
- [ ] MCQ persistence to backend

**Interview sentence after Phase 2:**
"Five agents orchestrated via LangGraph; the assessment agent calibrates MCQ
difficulty against the learner's mastery state, and the model cascade cuts
per-session cost 60% by routing simple queries to an 8B model."

### Phase 3 — Support + Admin + Polish + cutover (weeks 11-14, target: late Dec)
**Goal:** Complete system with support bot + admin automation, and the
routing cutover to the new stack. Full portfolio piece.

- [ ] Support Agent (different RAG corpus + persona)
- [ ] Support bot red-team eval suite (30 adversarial cases)
- [ ] Admin Agent (resolution suggestions, automated actions)
- [ ] Stripe test-mode integration
- [ ] Admin dashboard (cost attribution, action audit trail)
- [ ] FDE vertical initial integration (RAG only, no auto-grading)
- [ ] Interactive UX improvements (mode transitions, hints)
- [ ] Routing cutover: flip Nginx so `neuralascent.top` routes to the new
      TypeScript/FastAPI stack (see §2.4); retire or narrow the .NET API
- [ ] End-to-end demo narrative rehearsed

**Interview sentence after Phase 3:**
"The support agent shares RAG infrastructure but swaps corpus and persona;
I red-teamed it with 30 adversarial cases — containment rate 93%, zero
prompt injection successes. The admin agent automates policy-compliant
refunds via Stripe and surfaces resolution suggestions for edge cases."

### Phase 4 — Stretch (only if time allows, Jan 2027)
- [ ] Self-hosted model comparison (Ryzen AI Max+ / vLLM)
- [ ] Model Economics Matrix measurements
- [ ] Spaced repetition algorithm tuning
- [ ] Advanced UX polish

---

## 13. Open decisions

| # | Decision | Options | Status |
|---|---|---|---|
| 1 | LLM provider cascade | Multi-provider: Muse + Nova Micro + Gemini | **Decided 2026-09-07** |
| 2 | Cost budget for demo usage | $2/day cap sufficient at ~$0.015/session | **Decided 2026-09-07** |
| 3 | Mac Studio M1 Max local model | Embedding + reranking host (not LLM routing tier) | **Decided 2026-09-08** — see §2.4 |
| 4 | FDE exercise grading approach | LLM-as-judge vs human review only | Recommended: LLM-as-judge with rubric |
| 5 | Mem0 vs custom PostgreSQL for learner memory | Mem0 (faster to build) vs custom (more control) | Evaluate in Phase 1 |
| 6 | Embeddings provider | Local-first on Mac Studio, API fallback on same weights | **Decided 2026-09-08** — supersedes prior OpenAI/BGE framing, see §2.4 |
| 7 | Frontend/backend stack for new tutor UI | Fresh TypeScript + FastAPI vs reuse existing React/.NET | **Decided 2026-09-08** — fresh build, no reuse |
| 8 | Routing cutover from `neuralascent.top` | Staged: dev subdomain first, full flip in Phase 3 | **Decided 2026-09-08** — see §2.4 |
| 9 | Orchestration framework: LangGraph vs LangChain vs CrewAI | LangGraph for the tutor; LangChain for the Localization Lab pipeline; CrewAI in neither product | **Decided 2026-09-18** — full reasoning in [ADR-001-orchestration-framework-choice.md](ADR-001-orchestration-framework-choice.md) |

---

## 14. Relationship to other Neuralascent work

- **Existing auth/TOTP/chat system (§1 of session handoff):** The JWT auth
  and rate limiting stay. The existing Llama API chat (`ChatEndpoints.cs`) is
  the precursor — this agent replaces it with something far more capable.
  The auth layer is reused as-is.
- **Localization Lab:** On hold (disabled from site, will resume after this
  project ships). Separate portfolio piece for interviews if time allows.
- **AI-vertical curriculum content:** Hand-authored only, per CLAUDE.md §0.
  This agent USES that content as RAG data but does not GENERATE curriculum
  content.
- **AI Infusion course (Scaler):** The course teaches concepts (RAG,
  agents, Docker, LangChain) that this project puts into practice. As more
  classes arrive (10-20 remaining), new concepts can inform architecture
  decisions — but the project's architecture should not wait for the course
  to finish.

---

## 15. File index

| File | Purpose |
|---|---|
| `info/.notes/ai-learning-agent-ARCHITECTURE.md` | This file — architecture & design spec |
| `info/.notes/ADR-001-orchestration-framework-choice.md` | Why LangGraph for the tutor, LangChain for the Localization Lab, CrewAI for neither (§13 decision 9) |
| `info/.notes/SESSION-2026-09-19-langgraph-scaffold-and-adr.md` | Most recent session — LangGraph scaffold built/debugged/verified, ADR-001 written, Langfuse-next sequencing decision |
| `info/.notes/SESSION-2026-09-AI-chatbot-planning-and-auth-build.md` | Previous session handoff (auth build + AI-helper review) |
| `info/.notes/localization-lab-STATUS-TRACKER.md` | Localization project status (on hold) |
| `CLAUDE.md` | Repo-wide rules (no direct code edits, prompt workflow, scope boundaries) |
