# FDE Phase 17 — Module 8: System Design, Capstone & Hiring Readiness (Lessons 1-5 of 14)

Five lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-17-system-design-capstone-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `system-design-capstone` ("8. System Design, Capstone & Hiring
Readiness")

This is a **brand-new module** — the final module of the entire FDE core curriculum — and this
file covers its **first third only**: lessons 1-5 of 14. Two more phases, already in progress in
parallel, cover the remaining 9 lessons (Interview Framework, four Capstone Sprints, Demo Day,
Interview Readiness, Mock Engagement, and a Graduation Review) and complete the module — do not
add placeholder content for those here.

These five lessons are explicitly **synthesis**, not new mechanism teaching (with one exception:
Lesson 1 introduces genuinely new distributed-systems-theory content — CAP, PACELC, Raft, and
Saga — that nothing earlier in the curriculum covers). Lessons 2-5 assume the reader already knows
RAG internals (Phases 1-2, 12), agentic/tool-calling/MCP/multi-agent internals (Phases 13-14),
Postgres RLS and multi-tenant mechanics (Phase 15), and enterprise integration topology/connector
design/entity resolution (Phases 13-14) — they apply all of it to a from-scratch, at-scale system
design problem, in the structure of a real system-design-interview walkthrough: requirements
clarification, capacity estimation, high-level design, a deep dive on 2-3 hard trade-offs, and
failure modes. This is why the "Practical Backend Scenario" section in these lessons runs
considerably longer and more structured than in earlier modules — it carries the actual design
walkthrough instead of a single paragraph.

---

# LESSON 1

```yaml
lesson_id: fde-system-design-capstone-01-distributed-systems-fundamentals-cap-pacelc-raft-saga
lesson_title: "Distributed Systems Fundamentals (CAP, PACELC, Raft, Saga)"
lesson_order: 1

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: system-design-capstone
module_name: "8. System Design, Capstone & Hiring Readiness"
module_order: 8

difficulty: Hard
estimated_minutes: 80
content_status: Draft

learning_outcomes:
  - "Apply CAP theorem correctly at the level of a single data path rather than an entire system, and use PACELC to reason about the latency/consistency trade-off that exists even when no partition is happening."
  - "Explain Raft's leader-election and log-replication mechanics well enough to justify a specific quorum size for a coordination service, and name the specific failure Raft's term numbers prevent."
  - "Design a saga (orchestration or choreography) for a multi-system write with a compensating action per step, and explain why idempotency keys are what make a compensation safe to replay."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Distributed Systems Fundamentals (CAP, PACELC, Raft, Saga)

## Concepts Covered

CAP theorem is routinely applied at the wrong granularity. It does not say "pick two of consistency, availability, and partition tolerance" as a one-time, whole-system choice — partition tolerance isn't optional in any system that spans more than one network-reachable node, so the actual choice CAP forces is what a node does *during* a partition: block until it can confirm it holds the latest write (choosing consistency, C) or answer with whatever it has (choosing availability, A). The granularity that matters is the data path, not the system. A single Postgres primary with synchronous replicas is CP on its write path — a write blocks until the replica quorum acknowledges, so a partitioned minority cannot accept writes that would later conflict — while reads served from an asynchronous replica on the same deployment are AP: they answer immediately with data that might be a few hundred milliseconds stale rather than blocking to confirm freshness. Calling the whole system "CP" or "AP" erases this distinction and produces wrong reasoning the first time someone asks whether a specific read is safe to trust.

PACELC is the more useful framing precisely because it makes the common case, not just the partition case, an explicit trade-off: **P**artition — **A**vailability or **C**onsistency; **E**lse — **L**atency or **C**onsistency. The "Else" branch is the one CAP is silent on and PACELC forces onto the table: even when no partition is happening, a system replicating synchronously to a remote region to guarantee strong consistency pays a real, permanent latency tax on every write, not just during an outage. Google Spanner is PC/EC — it accepts that tax everywhere, always, because its correctness guarantees depend on it. DynamoDB is PA/EL — it accepts weaker consistency everywhere in exchange for latency it can bound tightly, always. Neither choice is more correct in the abstract; the right one depends on which cost — write latency paid on every request, or the operational cost of reasoning about staleness — a specific data path can actually afford. A multi-region multi-tenant SaaS choosing between a single-writer region (CP: one authoritative write region, cross-region reads are asynchronously replicated and slightly stale, simple to reason about, but every write from a distant region pays that region's round-trip latency) and multi-writer active-active (AP: every region accepts local writes at local latency, but now needs a conflict-resolution strategy — last-writer-wins, or a CRDT — for the case where two regions write the same record concurrently) is making exactly this PACELC trade-off, not an abstract CAP one.

Raft is the consensus protocol that makes a CP data path actually implementable across multiple nodes without a single point of failure, and it underlies the coordination services (etcd, and by extension Kubernetes' own control plane, CockroachDB's range consensus) an FDE will actually configure. A Raft cluster elects one leader via randomized election timeouts — each follower waits a randomized interval before declaring a candidacy, which is what prevents two nodes from perpetually re-triggering elections in lockstep — and every write goes through that leader, which replicates it to followers and only commits once a **majority** (not all) of the cluster has acknowledged. This is why Raft clusters are sized as an odd number (3 or 5, rarely more): a 5-node cluster tolerates 2 simultaneous node failures while still holding a majority (3) among the survivors, and an even-numbered cluster (4 nodes) gets no benefit over the next odd number down — it still only tolerates 1 failure before losing majority, while paying the replication cost of a 4th node for nothing. Term numbers are Raft's specific defense against split-brain: each election increments a monotonic term, and any node encountering a message from a higher term immediately recognizes its own leader (or candidacy) as stale and steps down — this is exactly what prevents two leaders from both believing they're authoritative after a partition heals and both having accepted writes during the split, a scenario CAP's "choose C" framing gestures at abstractly but Raft's term mechanism actually solves in code.

Saga is the answer to a different problem: coordinating a write across multiple independent systems (a database and a third-party payment API; three separate SaaS systems in an integration hub) where no distributed transaction (no two-phase commit spanning heterogeneous systems) is available or desirable. A saga replaces one atomic transaction with a sequence of local transactions, each paired with a **compensating action** that semantically undoes it if a later step fails — there is no rollback in the database sense, only a forward-moving compensation. **Orchestration-based** sagas use a central coordinator that explicitly calls each step and, on failure, explicitly calls each prior step's compensation in reverse order — centralized visibility, one place to read the whole workflow, but a single component that owns real complexity. **Choreography-based** sagas have each service publish an event on completion and react to others' events with no central coordinator — no single point of workflow logic, but the failure path is now scattered across services with no one place to read "what happens when step 3 fails." Neither is universally better: a saga with 3-4 steps and few branches is often clearer as choreography; a saga with real branching logic (approve here, escalate there, retry with backoff elsewhere) usually needs the explicit state machine an orchestrator provides. In both shapes, a compensating action is only safe to run more than once — which it will be, under retry — if it is idempotent, which is exactly the idempotency-key discipline already load-bearing for tool calls and connector writes elsewhere in this curriculum, now applied to a compensation rather than a forward step.

## Practical Backend Scenario

Meridian Legal Ops is expanding ClauseReview into a second AWS region (`eu-west-1`) to satisfy a European customer's data-residency requirement, alongside the existing `us-east-1` deployment serving Acme and Globex. Two distinct distributed-systems decisions land on the same design review. First: should the Postgres primary stay single-writer in `us-east-1`, with `eu-west-1` serving read-only replica traffic and routing writes back across the Atlantic, or should Meridian stand up a second writable primary in `eu-west-1`? The team picks single-writer — CP on the write path, an explicit PACELC choice to accept `eu-west-1` writes paying transatlantic latency (a genuinely rare operation: contract *review* is read-heavy; only clause edits and status changes write) rather than take on active-active conflict resolution for a feature with no evidenced need for local write latency. Second: ClauseReview's background extraction workers use a distributed lock, backed by a 3-node etcd cluster (Raft consensus), to ensure only one worker in the fleet claims a given contract's extraction job at a time — sized at 3, not 4 or 2, because 3 is the smallest odd cluster that tolerates one node failure while keeping a majority, and a 2-node cluster couldn't tolerate any failure at all without losing the ability to elect a leader.

Separately, Meridian's enterprise-integration team is designing a saga for a new customer workflow: when a contract is approved in ClauseReview, the system must create a matching record in the customer's own CLM (contract lifecycle management) system, notify their e-signature platform, and update a billing record in Meridian's own Ledger — three independent systems, no shared transaction. The team chooses orchestration: a `ContractApprovalSaga` coordinator calls each step in sequence and, if the e-signature step fails after the CLM record was already created, explicitly calls the CLM record's compensating action (mark it `cancelled`, not delete it — deleting a record a human may have already looked at is a worse compensation than clearly labeling it void) before surfacing the failure. Every step and its compensation carry the same `(org_id, event_id)` idempotency key discipline from Phase 15's multi-tenant background-job lesson, so a saga step retried after a transient timeout — CLM record creation that actually succeeded but whose response never reached the orchestrator — does not create a second CLM record on retry.

## Practice Loop

1. For ClauseReview's `us-east-1`/`eu-west-1` expansion, write one sentence naming which data path (writes, reads) is CP and which is AP, and justify the choice using PACELC's "Else" branch — the latency cost paid on every write in the common case, not only during a partition.
2. Size the etcd coordination cluster for the extraction-job lock at 3 nodes, then recompute fault tolerance for a 2-node and a 4-node cluster — this diagnostic step should make the odd-cluster-size argument concrete rather than asserted.
3. Write the `ContractApprovalSaga`'s three steps (CLM record, e-signature notification, Ledger billing update) and a compensating action for each, then trace exactly what happens if the Ledger step fails after the first two steps already succeeded.
4. Simulate the CLM-creation-step timeout-but-actually-succeeded scenario: show what the retry does with the `(org_id, event_id)` idempotency key in place, versus what it would do without one.
5. Decide whether the `ContractApprovalSaga` should stay orchestration-based as Meridian scales to 10 downstream systems per approval, or whether a choreography-based redesign becomes justified — name the specific factor (branching complexity, need for centralized visibility) that should drive the decision.

## Evidence of Understanding

You can apply CAP theorem at the level of a specific data path rather than an entire system, and use PACELC to explain the latency/consistency trade-off a system pays in the common case, not only during a partition. You can justify a specific Raft cluster size using the majority-quorum math, and explain what problem Raft's term numbers specifically prevent. You can design a saga — orchestration or choreography — for a multi-system write with a compensating action per step, and explain why idempotency keys are what make replaying a compensation safe rather than dangerous.

## Suggested Extension

Redesign the `ContractApprovalSaga` as choreography — each system publishes an event on completion, and the next system's own listener reacts — and identify the one piece of information (a way to answer "what is the current state of approval X across all three systems, right now") that was trivial to get from the orchestrator's own state and is now genuinely harder to reconstruct without one.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** The correct granularity for applying CAP
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that labeling an entire system "CP" or "AP" is often a mistake?

**OPTIONS:**
- [ ] A: Because CAP theorem only applies to systems with exactly two nodes
- [x] B: Because the actual C-vs-A choice happens per data path — a single deployment can have a CP write path (synchronous replica quorum) and an AP read path (asynchronous replica) at the same time
- [ ] C: Because partition tolerance is optional and most systems choose not to have it
- [ ] D: Because CAP theorem was superseded by PACELC and no longer applies to any modern system
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific correction is about granularity: CAP's C-vs-A choice is made per data path (what a node does during a partition on that path), not once for an entire deployment.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [cap-theorem, data-path-granularity]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What PACELC adds that CAP does not address
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does PACELC's "Else" (E) branch force a system designer to reason about that CAP theorem alone is silent on?

**OPTIONS:**
- [ ] A: What happens when a system has zero nodes remaining after a failure
- [x] B: The latency-versus-consistency trade-off a system pays in the common case, when no partition is happening at all
- [ ] C: Whether a system should use SQL or NoSQL for its primary datastore
- [ ] D: How many replicas a system needs to survive a single disk failure
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
CAP is entirely about partition behavior; PACELC's "Else" branch is specifically the non-partition case, where a system still pays a latency-vs-consistency cost on every request.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [pacelc, else-branch, latency-tax]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Single-writer-region vs. active-active as a PACELC choice
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's multi-region SaaS framing, what is the real cost being traded off between a single-writer-region design and a multi-writer active-active design?

**OPTIONS:**
- [ ] A: Single-writer designs are always cheaper to host regardless of traffic patterns
- [x] B: Single-writer pays cross-region write latency on every distant write but stays simple to reason about; active-active gives every region local write latency but requires an explicit conflict-resolution strategy for concurrent writes to the same record
- [ ] C: Active-active designs never need a conflict-resolution strategy because Postgres handles it automatically
- [ ] D: Single-writer designs cannot serve read traffic from any region other than the primary
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's concrete PACELC application — the cost isn't abstract, it's a specific choice between paying latency on every distant write versus taking on real conflict-resolution complexity.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [multi-region-tradeoff, active-active-conflicts]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why Raft clusters are sized as odd numbers
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue a 4-node Raft cluster gets no real benefit over a 3-node cluster?

**OPTIONS:**
- [ ] A: Raft does not support clusters with an even number of nodes at all
- [x] B: A 4-node cluster still only tolerates 1 node failure before losing majority — the same fault tolerance as 3 nodes — while paying the replication cost of a 4th node for no additional benefit
- [ ] C: A 4-node cluster elects leaders twice as often as a 3-node cluster
- [ ] D: Even-numbered clusters cannot use randomized election timeouts
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Majority of 4 is 3, same as majority of 5 minus 2 failures being tolerated by 5 but not 4 — the specific comparison the lesson draws is 3 vs. 4: both tolerate exactly 1 failure, so the 4th node adds cost without adding tolerance.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [raft-quorum-sizing, odd-cluster-size]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What Raft's term numbers specifically prevent
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific failure does Raft's monotonically increasing term number prevent?

**OPTIONS:**
- [ ] A: A follower node running out of disk space during log replication
- [x] B: Split-brain — two nodes both believing they are the current leader and both accepting writes, typically after a partition heals; a node encountering a higher term steps down immediately
- [ ] C: A client sending a malformed write request to the cluster
- [ ] D: The cluster losing all its data if the network is ever partitioned
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Term numbers are Raft's concrete mechanism against split-brain: any node seeing a higher term recognizes its own leadership claim as stale and steps down, which is what CAP's abstract "choose C" framing doesn't actually implement on its own.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [raft-term-numbers, split-brain-prevention]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Orchestration vs. choreography saga trade-off
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the core trade-off between an orchestration-based saga and a choreography-based saga, per the lesson?

**OPTIONS:**
- [ ] A: Orchestration-based sagas cannot use compensating actions, only choreography-based ones can
- [x] B: Orchestration centralizes workflow logic and visibility in one coordinator at the cost of that component owning real complexity; choreography has no single point of workflow logic but scatters the failure path across services with no one place to read it
- [ ] C: Choreography-based sagas are always faster because they have no coordinator to call
- [ ] D: Orchestration-based sagas require a distributed two-phase commit across all systems involved
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's exact trade-off statement — centralized visibility and complexity versus no single point of logic but a scattered failure path.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 4
**KEYWORDS:** [saga-orchestration, saga-choreography]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why idempotency keys make a compensation safe to replay
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the `ContractApprovalSaga` scenario, why does the CLM-creation step's retry, carrying an `(org_id, event_id)` idempotency key, not create a second CLM record even though the original request actually succeeded before the orchestrator's timeout?

**OPTIONS:**
- [ ] A: CLM systems automatically reject any request made more than once, regardless of its contents
- [x] B: The idempotency key lets the retried request be recognized as a duplicate of a request that already completed, so the same effect is not applied twice
- [ ] C: The orchestrator waits indefinitely for the first request instead of ever retrying
- [ ] D: Compensating actions are only ever needed for the first step of a saga, never a retry of it
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the specific mechanism: an idempotency key lets a retried call be recognized as a duplicate of an already-applied effect, which is exactly why a compensation or a forward step is safe to replay with one.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [idempotency-key, safe-replay]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What compensating "cancel," not "delete," achieves
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the `ContractApprovalSaga`'s compensation for a failed e-signature step mark the already-created CLM record `cancelled` rather than delete it?

**OPTIONS:**
- [ ] A: Deleting records is technically impossible in most CLM systems
- [x] B: A human may have already seen the record; clearly labeling it void is a more accurate and auditable compensation than making it disappear as though it never existed
- [ ] C: Marking a record cancelled is always faster to execute than deleting it
- [ ] D: CLM systems require every record to remain in the system permanently by law
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific point is about what a compensation should semantically communicate — a visible, correctly-labeled void state, not an erasure that could confuse anyone who already saw the record.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [compensating-action-design, audit-friendly-compensation]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** When choreography becomes harder to reason about
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, what specifically becomes harder once the `ContractApprovalSaga` is redesigned as choreography instead of orchestration?

**OPTIONS:**
- [ ] A: Each individual system's own local transaction becomes impossible to complete
- [x] B: Answering "what is the current state of approval X across all three systems, right now" — trivial to read from an orchestrator's own state, and genuinely harder to reconstruct once no single component tracks the whole workflow
- [ ] C: Compensating actions can no longer be defined for any step in the workflow
- [ ] D: Idempotency keys stop working once there is no central coordinator
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's named cost of choreography: centralized state visibility, which an orchestrator gives essentially for free, has to be reconstructed some other way (e.g., a read-side projection) once no component is coordinating in one place.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [choreography-cost, centralized-visibility-loss]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: own knowledge (Raft consensus paper — Ongaro & Ousterhout; Brewer's CAP theorem; Abadi's PACELC formulation; the Saga pattern — Garcia-Molina & Salem)

---

# LESSON 2

```yaml
lesson_id: fde-system-design-capstone-02-system-design-rag-system-at-scale
lesson_title: "System Design: RAG System at Scale"
lesson_order: 2

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: system-design-capstone
module_name: "8. System Design, Capstone & Hiring Readiness"
module_order: 8

difficulty: Hard
estimated_minutes: 85
content_status: Draft

learning_outcomes:
  - "Produce a defensible capacity estimate (storage, QPS, latency budget) for a multi-tenant RAG system from stated scale requirements, not from a guessed number."
  - "Choose and justify a vector-index sharding strategy (shared multi-tenant index, per-tenant index, or a tiered hybrid) for 500 tenants against isolation, cost, and operational overhead."
  - "Apply CAP/PACELC reasoning from Lesson 1 to decide which parts of a RAG pipeline can tolerate eventual consistency and which cannot, and design the failure-mode handling for an embedding-service or reranker outage."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# System Design: RAG System at Scale

## Concepts Covered

This lesson does not re-teach what RAG is, what hybrid search combines, what RAGAS measures, or how model routing works — Phases 1, 2, and 12 already covered all of that in depth. What's genuinely new here is the discipline of a system-design interview applied to a RAG system specifically: turning a one-line prompt ("design a RAG system serving 500 enterprise tenants") into an explicit set of numbers before a single component gets drawn, because every interesting design decision in a RAG system at this scale — how the vector index is sharded, whether the reranker runs on every query or only some, how much cache hit rate is needed to hit a cost target — is a direct consequence of a capacity estimate, not a matter of taste. The estimate does not need to be precise; it needs to be defensible and load-bearing, meaning every later design decision can point back to a specific number in it and explain why that number, not a different one, drove the choice.

The second thing genuinely new at this scale is that "the vector store" stops being one design decision and becomes three coupled ones: how data is partitioned across index shards, how a query is routed to the right shard(s), and how consistency staleness after a new document is ingested is tolerated across that partitioning scheme. Phase 12's retrieval-time access-control lesson already established that a tenant's rows must be pre-filtered before ranking runs — at 500-tenant, 50-million-document scale, the question is no longer just *whether* to filter but *where in the physical index* that tenant's vectors live at all, because a single unpartitioned index across all 500 tenants means every similarity search scans (or at minimum touches the graph structure of) vectors belonging to tenants that were never going to match, and a poorly chosen partitioning scheme can turn a single large tenant's re-indexing event into a latency spike every other tenant on the same shard feels. This is the CAP/PACELC discipline from Lesson 1 landing directly on a concrete infrastructure choice: a vector index is overwhelmingly read-heavy, and staleness of a newly-ingested document by a few minutes is an acceptable AP trade — nobody is harmed by a contract clause not being searchable for 90 seconds after upload — which is a different consistency requirement than, say, a financial ledger balance, and the index architecture should be free to exploit that.

## Practical Backend Scenario

**Requirements clarification.** Functional: each of 500 enterprise tenants can search across only their own documents (hard isolation requirement — a leak here is a security incident, not a quality bug), retrieval must support hybrid search with citations back to source chunks, and responses must reflect documents ingested within the last few minutes, not hours. Non-functional: 500 tenants, 50 million documents total across all tenants (tenant sizes vary widely — a handful of large tenants may hold millions of documents, most hold a few thousand), sub-2-second p99 end-to-end latency (query in, answer streaming out), and a cost ceiling that makes per-query infrastructure spend a first-class design constraint, not an afterthought.

**Capacity estimation.** Average 100,000 documents per tenant (50M / 500). Assuming ~500-token chunks at roughly 5 chunks per document, that's 250 million chunks total. Each chunk's embedding (a common 1536-dimension model) is 1536 × 4 bytes = ~6KB; 250M chunks × 6KB ≈ 1.5TB of raw vector data, and a production ANN index (HNSW's graph overhead, typically) runs 2-3× that footprint — call it 4TB of index storage to plan for, before replication. On query volume: assume 500 tenants × ~200 daily active users × ~10 queries/user/day ≈ 1 million queries/day, which averages to roughly 12 QPS but peaks (business-hours concentration, roughly 5× average) at ~60 QPS — the number the system actually has to be provisioned against. Within the 2-second p99 budget: embedding the query (~50-100ms), hybrid retrieval against the shard(s) (~50-150ms), an optional reranking pass (~100-150ms), and generation (~500-1000ms, streamed so the *perceived* latency to first token matters more than total completion time) — leaving real headroom, which is exactly what makes a reranking pass and a semantic-cache check (Phase 12's cost/latency lesson) affordable additions rather than a threat to the SLA.

**High-level design.** An ingestion pipeline (Phase 12's chunking/tagging pattern, horizontally scaled and partitioned by tenant so one tenant's large bulk upload doesn't stall another's) writes into a **tiered vector-index topology**: the handful of tenants whose document count or query volume is disproportionately large get a dedicated index shard each; the long tail of small-to-medium tenants share a common multi-tenant index, partitioned into several shards by a hash of `org_id` and queried with the pre-filter pattern from Phase 12 Lesson 8. A query router looks up which shard(s) a tenant's traffic belongs to and fans out only there — never scanning the shared index for a tenant's query that's actually served by their own dedicated shard, and never scanning a dedicated shard for anyone else's traffic. A model-routing gateway (Phase 12's cost/latency lesson) and a semantic cache sit in front of the generation step.

**Deep dive — three hard trade-offs.** First: shared multi-tenant index versus per-tenant index versus the tiered hybrid above. A fully shared index is operationally simplest (one index to tune and rebuild) but means one tenant's re-indexing or a spike in that tenant's document churn can degrade query latency for every tenant on the same shard — a direct noisy-neighbor risk. A fully per-tenant index (500 separate indexes) gives hard isolation but is an operational burden that doesn't pay for itself for a tenant with 500 documents. The tiered design earns its complexity specifically because tenant size is heavily skewed in this scale profile — isolating only the tenants whose scale or noisy-neighbor risk actually justifies it, while keeping the long tail cheap to operate as a shared resource, mirrors the same tiering judgment Lesson 4 of this module makes for a general multi-tenant SaaS. Second: where to spend the 2-second latency budget. Running a reranker on every query is not free, and running it unconditionally for a simple factoid query that hybrid retrieval alone already answers correctly wastes 100-150ms for no accuracy gain — a complexity-based routing check (has this query type historically benefited from reranking?) decides per-query whether the reranking pass runs at all, the same routing discipline Phase 12's cost lesson applied to model tier selection, now applied to a pipeline stage instead of a model choice. Third: applying Lesson 1's PACELC framing explicitly — the vector index's replicas are AP by design (a newly-ingested document being searchable a couple of minutes late is an acceptable cost, and demanding synchronous strong consistency here would tax every write for a freshness guarantee nobody asked for), while the tenant-to-shard routing metadata itself (which tenant lives on which shard) is a small, low-write-volume table that can afford to be CP, since routing a query to the wrong shard — not staleness, but outright misrouting — is the actual failure that would matter.

**Failure modes.** An embedding-service outage should degrade the query path to keyword-only (BM25) search rather than fail the request outright — a worse answer beats no answer, and hybrid search's keyword component was designed to survive exactly this. A reranker outage should short-circuit to unreranked hybrid results rather than block the query, since reranking is a quality improvement, not a correctness requirement. A single large tenant's ingestion pipeline backing up (a bulk upload of 50,000 documents overnight) should never delay another tenant's ingestion — the per-tenant partitioning in the ingestion pipeline, plus per-tenant rate limits, is what prevents this from becoming a platform-wide incident instead of one tenant's slow morning.

## Practice Loop

1. Recompute the capacity estimate above using 1,000-token chunks instead of 500, and state which two downstream numbers (index storage footprint, chunks-per-document count) change as a direct result — this diagnostic shows exactly how sensitive the estimate is to one input assumption.
2. Draw the tiered vector-index topology (dedicated shards for large tenants, a partitioned shared index for the long tail, a query router in front) as a component diagram, and label which component enforces the tenant pre-filter from Phase 12.
3. For one of the three deep-dive trade-offs, write the one-paragraph case for the *opposite* choice (e.g., argue for a fully shared index instead of the tiered hybrid) and identify the specific scale assumption that would have to be false for that opposite choice to actually be correct.
4. Simulate the embedding-service-outage failure mode: trace exactly what a query does at each pipeline stage when the embedding call fails, and confirm the fallback reaches keyword-only search rather than an error.
5. Given the 60 QPS peak estimate, calculate how many concurrent in-flight requests the generation stage alone needs to support if average generation time is 800ms, and state whether that concurrency figure changes your view on how aggressively semantic caching needs to be tuned.

## Evidence of Understanding

You can produce a defensible capacity estimate — storage, QPS, and a latency budget breakdown — for a multi-tenant RAG system from stated scale requirements, and show your work rather than asserting a final number. You can choose and justify a vector-index sharding strategy for a tenant population with skewed scale, explaining specifically why a tiered hybrid earns its operational complexity over either fully-shared or fully-per-tenant extremes. You can apply CAP/PACELC reasoning to decide which parts of a RAG pipeline can tolerate eventual consistency (index freshness) and which cannot (shard-routing correctness), and design graceful-degradation failure handling for an embedding-service or reranker outage.

## Suggested Extension

A single enterprise tenant's usage grows from 100,000 documents to 8 million over a year, well past what the shared long-tail index was sized for. Design the migration path that moves this one tenant from the shared index to its own dedicated shard without downtime for that tenant's own queries, and name the trigger metric (document count, query volume, or measured latency impact on shard-mates) that should decide when this migration happens automatically rather than being noticed manually.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why a capacity estimate must be load-bearing
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson mean by a capacity estimate needing to be "load-bearing" rather than merely precise?

**OPTIONS:**
- [ ] A: The estimate must be calculated to the exact byte and query, with no rounding permitted
- [x] B: Every later design decision should be able to point back to a specific number in the estimate and explain why that number, not a different one, drove the choice
- [ ] C: The estimate should only ever be produced by a senior engineer, never a junior one
- [ ] D: The estimate must be verified against production traffic before any design work can begin
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific claim is about the estimate's role in justifying design choices, not about numerical precision — a rough but load-bearing number beats a precise one nobody's decision actually depends on.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [capacity-estimation, load-bearing-numbers]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What changes at 500-tenant, 50M-document scale
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what becomes a genuinely new design question at this scale that a single-tenant or small-scale RAG deployment never has to answer?

**OPTIONS:**
- [x] A: Where in the physical index a tenant's vectors actually live, and how that partitioning scheme affects noisy-neighbor risk and staleness handling
- [ ] B: Whether retrieval should be pre-filtered or post-filtered by tenant, since post-filtering is only unsafe at large scale
- [ ] C: Whether hybrid search should combine dense and sparse retrieval, since that only matters above a certain document count
- [ ] D: Whether RAGAS scoring is necessary, since evaluation is only needed once a system serves multiple tenants

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Pre-filtering (not post-filtering) is always correct regardless of scale — Phase 12 already established this. What's new at this scale is a physical partitioning decision: where a tenant's vectors actually live in the index topology.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [index-partitioning, scale-specific-decisions]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the latency budget breakdown
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's capacity estimate, why does the 2-second p99 latency budget leave enough headroom to afford both a reranking pass and a semantic-cache check?

**OPTIONS:**
- [ ] A: Reranking and caching cost no additional latency under any circumstances
- [x] B: The itemized budget (embedding ~50-100ms, retrieval ~50-150ms, reranking ~100-150ms, generation ~500-1000ms streamed) sums to well under 2 seconds, leaving real room for these additions
- [ ] C: The 2-second budget only applies to the embedding and retrieval stages, not to generation
- [ ] D: Semantic caching eliminates the need for a latency budget entirely

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's itemized stage-by-stage budget is what makes the "affordable" claim concrete rather than asserted — summing the stages shows genuine headroom under 2 seconds.

**LESSON_CONNECTION:** Practical Backend Scenario, Capacity Estimation
**KEYWORDS:** [latency-budget, headroom-calculation]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the tiered index topology earns its complexity
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson choose a tiered vector-index topology (dedicated shards for large tenants, a shared partitioned index for the long tail) over either a fully shared index or a fully per-tenant index?

**OPTIONS:**
- [ ] A: A tiered topology is always the correct default for any multi-tenant system regardless of tenant size distribution
- [x] B: Tenant size in this scenario is heavily skewed — a fully shared index risks noisy-neighbor effects from the largest tenants, while a fully per-tenant index (500 separate indexes) doesn't pay for itself for tenants with only a few thousand documents
- [ ] C: Per-tenant indexes are technically impossible to build with current vector database technology
- [ ] D: A shared index cannot support hybrid search under any configuration

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The tiering decision is justified specifically by the skewed scale profile in this scenario's requirements, not as a universal default — the lesson is explicit that this is a judgment call driven by the actual tenant-size distribution.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [tiered-index-topology, skewed-tenant-scale]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Conditional reranking as a latency-budget decision
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend routing only some queries through the reranking pass, rather than running it unconditionally on every query?

**OPTIONS:**
- [ ] A: Reranking is deprecated and should never be used in a production RAG system
- [x] B: A simple factoid query that hybrid retrieval already answers correctly gains no accuracy from reranking, so running it unconditionally wastes 100-150ms of the latency budget for no benefit on that class of query
- [ ] C: Reranking cannot run on queries shorter than a certain length
- [ ] D: Running reranking on every query would exceed the storage budget, not the latency budget

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific argument is about wasted latency on queries that don't benefit — a complexity-based routing check decides per-query whether reranking is worth its cost, mirroring the model-tier routing discipline from Phase 12.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [conditional-reranking, latency-vs-accuracy]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Applying PACELC to the vector index vs. the routing table
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson treat the vector index's replicas as AP but the tenant-to-shard routing metadata as CP, within the same system?

**OPTIONS:**
- [ ] A: Because the routing metadata is stored on a different physical machine than the vector index
- [x] B: Because a newly-ingested document being searchable a couple of minutes late is an acceptable cost (AP), while routing a query to the wrong shard entirely is a real failure the system cannot tolerate (CP) — different data paths within one system can have different consistency requirements
- [ ] C: Because CAP theorem requires every subsystem within a larger system to make the same C-vs-A choice
- [ ] D: Because routing metadata never changes after the system is first deployed

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This directly applies Lesson 1's data-path-granularity correction to a concrete system: two data paths within one RAG deployment can and should make different C-vs-A choices based on what staleness or misrouting would actually cost.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [pacelc-application, per-data-path-consistency]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Graceful degradation on embedding-service outage
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What should happen to a query's retrieval path when the embedding service is unavailable, per the lesson's failure-mode design?

**OPTIONS:**
- [ ] A: The entire request should fail immediately with an error, since retrieval cannot function without embeddings
- [x] B: The query should degrade to keyword-only (BM25) search rather than fail outright, since a worse answer beats no answer and this is exactly what hybrid search's keyword component was designed to survive
- [ ] C: The request should be silently dropped with no response returned to the caller
- [ ] D: The system should wait indefinitely for the embedding service to recover before responding

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific design is graceful degradation, not failure — hybrid search's dual (dense + sparse) design is exactly what makes a keyword-only fallback available.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [graceful-degradation, embedding-outage-fallback]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Isolating one tenant's ingestion spike
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does a single tenant's bulk upload of 50,000 documents overnight not delay another tenant's ingestion, per the lesson's design?

**OPTIONS:**
- [ ] A: Bulk uploads are processed at a lower priority than all other traffic system-wide, regardless of tenant
- [x] B: The ingestion pipeline is partitioned per tenant with per-tenant rate limits, preventing one tenant's volume from consuming capacity that another tenant's ingestion needs
- [ ] C: Only one tenant is permitted to upload documents at any given time across the entire platform
- [ ] D: Document ingestion has no capacity limits at all in this design

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Per-tenant partitioning and rate limits in the ingestion pipeline are the specific mechanism the lesson names to prevent this from becoming a platform-wide incident.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [per-tenant-partitioning, ingestion-isolation]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Choosing the migration trigger for a growing tenant
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, what kind of metric should trigger migrating a tenant from the shared long-tail index to a dedicated shard?

**OPTIONS:**
- [ ] A: The tenant's billing tier alone, regardless of any measured technical impact
- [x] B: A metric tied to actual scale or impact — document count, query volume, or measured latency impact on shard-mates — so the migration happens based on evidence rather than being noticed only after it becomes a problem
- [ ] C: A fixed calendar schedule migrating one tenant per quarter regardless of size
- [ ] D: Whichever tenant complains first, regardless of whether their usage has actually grown

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This mirrors the lesson's broader insistence on evidence-driven decisions — the migration trigger should be a measured signal, not an arbitrary schedule or a reactive response to a complaint.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [migration-trigger, evidence-based-scaling]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: own knowledge (vector database sharding patterns; production RAG system design practice)

---

# LESSON 3

```yaml
lesson_id: fde-system-design-capstone-03-system-design-agentic-platform-at-scale
lesson_title: "System Design: Agentic Platform at Scale"
lesson_order: 3

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: system-design-capstone
module_name: "8. System Design, Capstone & Hiring Readiness"
module_order: 8

difficulty: Hard
estimated_minutes: 85
content_status: Draft

learning_outcomes:
  - "Produce a concurrency and throughput estimate for a multi-tenant agentic platform from stated workflow-count and tool-call requirements, and use it to size the worker pool."
  - "Design per-tenant MCP server governance and per-tenant fair-share scheduling for a shared orchestrator serving 50 enterprise customers."
  - "Apply CAP/PACELC reasoning to choose a consistency model for workflow-state storage, and design failure handling for an LLM-provider outage and a stuck workflow."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# System Design: Agentic Platform at Scale

## Concepts Covered

This lesson assumes tool-calling contracts, MCP's client-server architecture, orchestrator-worker topology, human-in-the-loop gates, and connector-layer design are already understood from Phases 13 and 14 — nothing here re-explains what those are. What's new is the platform question: not "how does one agent call one tool safely," but "how does a shared platform serve 200 concurrent agent workflows across 50 different enterprise customers without one customer's traffic degrading another's, without tool governance leaking across tenant boundaries, and without workflow state becoming inconsistent under the platform's own coordination failures." Concurrency is the first number that needs a real estimate, and it behaves differently from a typical web-request capacity estimate because an agent workflow spends most of its wall-clock time waiting — on an LLM completion, on a downstream tool call's network round-trip — rather than consuming CPU. That distinction is what makes the difference between sizing a worker pool for 200 *threads* versus 200 *concurrent async tasks on far fewer worker processes*, and getting this wrong either wastes most of a platform's compute budget on idle wait or, worse, undersizes true concurrency and silently queues customer workflows behind each other.

The second thing genuinely new at platform scale is that MCP governance — which Phase 13's MCP lesson designed for one customer's systems — now needs a second dimension: not just which resources and tools a given *client* can see on a given MCP server, but which *tenant's* traffic is allowed to reach which tenant's own MCP server instance at all. A platform serving 50 enterprise customers, each with their own Salesforce or ticketing system, cannot run one shared MCP server per system type with a single access-control list that happens to include everyone — that reintroduces exactly the cross-tenant leak risk Phase 15's RLS lesson spent a full lesson closing at the database layer, now at the tool-integration layer instead. The correct shape is per-tenant MCP server instances (or a single multi-tenant MCP server that enforces tenant scoping as rigorously as a database enforces RLS, with the same "never trust a WHERE clause alone" skepticism), each holding only that tenant's own credentials and exposing only that tenant's own systems, so a workflow running on behalf of Tenant A structurally cannot reach Tenant B's Salesforce instance regardless of what the orchestrator's routing logic does or fails to do correctly.

## Practical Backend Scenario

**Requirements clarification.** Functional: an orchestrator-worker agent platform (Phase 13's proven topology) executing customer-defined workflows, each workflow making a sequence of LLM reasoning steps interleaved with tool calls against that customer's own enterprise systems (CRM, ticketing, ERP), with a blocking human-in-the-loop gate on any step with hard-to-reverse consequence (Phase 13's criterion). Non-functional: 200 concurrent active workflows at any given moment, spread across 50 enterprise customers (a highly uneven distribution — some customers run a handful of workflows a day, others run dozens concurrently), with per-tenant tool governance that is structurally impossible to bypass, and a workflow-state store that survives an orchestrator-process crash mid-workflow without losing track of which steps already executed.

**Capacity estimation.** Assume an average workflow makes 10 sequential tool calls, each preceded by an LLM reasoning step; average LLM completion latency (mixed model tiers, per the cost-routing lesson) is ~1.5 seconds, average tool-call round-trip is ~1 second — so a workflow's total wall-clock duration is roughly 10 × (1.5s + 1s) = 25 seconds, almost entirely spent waiting on I/O, not computing. Because each waiting step yields the CPU (an async event loop, not a blocked thread), a single worker process can hold many workflows' waiting state concurrently — the real constraint on how many workflows one process can serve is memory (each workflow's accumulated context) and the platform's own concurrency limits against upstream LLM providers' rate limits, not CPU cores. Provisioning for 200 concurrent workflows at this profile is comfortably achievable with a modest number of worker processes (say, 10-20) each running an async event loop holding roughly 10-20 workflows' pending I/O simultaneously — a very different sizing conclusion than the naive "200 concurrent workflows needs 200 worker threads" assumption, and getting this distinction right is most of what separates a right-sized platform from one that either overspends heavily on idle compute or falls over the first time traffic clusters around a handful of large customers.

**High-level design.** A stateless orchestrator service layer (any instance can pick up any workflow's next step, since state lives externally) persists workflow state — which step a workflow is on, what's been completed, what's pending human approval — in a durable store designed for exactly this kind of state-machine tracking (a Postgres table modeling workflow/step state explicitly, not an in-memory structure that dies with the process). Each of the 50 tenants has its own MCP server instance (or a rigorously tenant-scoped shared server) holding only that tenant's own system credentials. A shared worker pool executes reasoning steps and tool calls across all tenants' workflows, routed through a model-routing gateway (Phase 12) for cost-appropriate tier selection. A human-approval queue with SLA-based escalation (Phase 13 Lesson 5) sits at each blocking gate. An audit log records every tool call, every approval decision, and every workflow-state transition, tagged by tenant, for later governance review.

**Deep dive — three hard trade-offs.** First: a shared orchestrator and worker pool across all 50 tenants versus a dedicated pool per tenant. A fully shared pool is dramatically more compute-efficient — the 200-concurrent-workflow estimate above assumed exactly this sharing — but creates a real noisy-neighbor risk: one tenant's workflow stuck in a retry loop against a misbehaving downstream tool can occupy a disproportionate share of worker capacity if nothing bounds it. The correct design borrows directly from the multi-tenant background-job lesson (Phase 15): per-tenant concurrency caps and fair-share scheduling within the shared pool, so one tenant's stuck workflows can degrade only that tenant's own throughput, never another tenant's, without needing the operational overhead of 50 fully separate pools. Second: MCP governance at platform scale, argued above — per-tenant server instances (or equivalently rigorous per-tenant scoping within a shared server) are not optional hardening, they are the structural boundary that makes a cross-tenant tool-call leak impossible rather than merely unlikely, the identical argument Phase 15 made for RLS over relying on every query remembering a `WHERE org_id` clause. Third: applying Lesson 1's CAP/PACELC framing to workflow-state storage specifically — a workflow's step sequence must never fork or duplicate under a coordination failure (two orchestrator instances both believing they own the next step of the same workflow would double-execute a tool call), so this data path is deliberately CP, using the same Raft-backed coordination (a distributed lock per workflow ID, or a database-level `SELECT ... FOR UPDATE` claim) Lesson 1 justified for exactly this kind of "exactly one owner" guarantee — a different consistency requirement than the vector index's AP-leaning design in Lesson 2's RAG system, underscoring that the right consistency model is a property of the specific data path, not a platform-wide default.

**Failure modes.** An LLM-provider outage should trip the model-routing gateway's circuit breaker (Phase 12) and fail over to an alternate provider tier rather than stall every in-flight workflow waiting on that provider. A workflow stuck retrying a failing tool call should hit a bounded retry count and then route to a dead-letter state visible to a human, not retry indefinitely and consume its tenant's fair-share concurrency budget forever. A tool call that times out from the orchestrator's perspective but actually succeeded downstream must be idempotency-key-protected (Phase 13's tool-contract discipline) so a retry doesn't double-execute a side-effecting action like a refund or a deal-stage update.

## Practice Loop

1. Recompute the worker-process sizing estimate assuming average tool-call round-trip time doubles to 2 seconds, and state whether this changes the "10-20 processes" conclusion or only the number of workflows one process can hold concurrently.
2. Draw the per-tenant MCP server topology for 3 of the 50 tenants, showing explicitly why a workflow running for Tenant A has no code path that could reach Tenant B's credentials, structurally, not just by policy.
3. Simulate the noisy-neighbor scenario: one tenant's workflow enters a retry loop against a failing downstream tool, and measure (or estimate) how much shared worker-pool capacity it would consume without a per-tenant concurrency cap versus with one.
4. Design the workflow-state table's schema (workflow ID, current step, tenant ID, status) and specify exactly what lock or coordination mechanism prevents two orchestrator instances from both claiming the same workflow's next step after an instance crash mid-workflow.
5. Trace what happens to an in-flight workflow's pending tool call when the LLM-provider outage failure mode triggers, from the moment the circuit breaker trips to the moment the workflow either resumes on a fallback provider or reaches a human-visible dead-letter state.

## Evidence of Understanding

You can produce a concurrency and throughput estimate for a multi-tenant agentic platform, correctly distinguishing I/O-bound waiting concurrency from CPU-bound thread-per-workflow sizing, and use the result to size a worker pool defensibly. You can design per-tenant MCP server governance that makes a cross-tenant tool-call leak structurally impossible, and per-tenant fair-share scheduling that bounds one tenant's stuck workflow from starving another tenant's throughput. You can apply CAP/PACELC reasoning to choose a CP consistency model for workflow-state coordination specifically, and design failure handling for an LLM-provider outage, a stuck workflow, and a timed-out-but-actually-succeeded tool call.

## Suggested Extension

One of the 50 tenants signs a contract requiring their agent workflows to run on dedicated, physically isolated compute for compliance reasons, not just logical tenant scoping within the shared pool. Design how this one tenant's workflows would be routed to a dedicated worker pool while every other tenant continues sharing the common pool, and name the one piece of the platform's design (from the deep dive above) that has to change versus the pieces that stay exactly as they are.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why I/O-bound waiting changes worker-pool sizing
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that sizing a worker pool for "200 concurrent workflows needs 200 worker threads" is the wrong conclusion?

**OPTIONS:**
- [ ] A: Because 200 concurrent workflows is an unrealistic number for any production agentic platform
- [x] B: Because a workflow spends most of its wall-clock time waiting on I/O (LLM completions, tool-call round-trips), not consuming CPU, so an async event loop can hold many workflows' waiting state per worker process — the real constraint is memory and upstream rate limits, not thread count
- [ ] C: Because worker threads are always slower than async event loops regardless of workload
- [ ] D: Because LLM providers refuse to serve more than one request per worker process
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific correction is about I/O-bound versus CPU-bound concurrency — waiting time dominates a workflow's duration, which is exactly what makes async concurrency on far fewer processes the right sizing model.

**LESSON_CONNECTION:** Practical Backend Scenario, Capacity Estimation
**KEYWORDS:** [io-bound-concurrency, worker-pool-sizing]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why platform-scale MCP governance needs a second dimension
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What additional governance dimension does a 50-tenant agentic platform need beyond the per-client resource/tool scoping Phase 13's MCP lesson already designed for a single customer?

**OPTIONS:**
- [ ] A: MCP servers must be rewritten to support a completely different protocol at platform scale
- [x] B: Which tenant's traffic is allowed to reach which tenant's own MCP server instance at all — a single shared server per system type with one shared access-control list would risk exactly the cross-tenant leak Phase 15's RLS lesson closed at the database layer
- [ ] C: Whether resources, tools, and prompts should be merged into a single MCP primitive at scale
- [ ] D: Whether MCP servers need to support synchronous calls, since they only supported asynchronous ones for a single customer
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson draws a direct parallel to Phase 15's RLS argument — tenant scoping at the tool-integration layer needs the same structural rigor as tenant scoping at the database layer, not a shared ACL that happens to include everyone.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [mcp-tenant-scoping, cross-tenant-leak-risk]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why per-tenant MCP scoping must be structural, not policy-based
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist that a workflow running for Tenant A must be structurally unable to reach Tenant B's credentials, rather than merely prevented by the orchestrator's routing logic being written correctly?

**OPTIONS:**
- [ ] A: Because orchestrator routing logic is always faster when it doesn't need to check tenant identity
- [x] B: Because a structural boundary (separate credentials per tenant's MCP server instance) cannot be bypassed by a routing bug, while a policy that depends on every code path remembering to check tenant identity correctly can be — the same reasoning that made database-layer RLS preferred over WHERE-clause discipline alone
- [ ] C: Because MCP servers cannot technically support more than one tenant's credentials in the same platform
- [ ] D: Because human-in-the-loop gates are only effective when tenants are structurally isolated
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's explicit parallel to the RLS-over-WHERE-clause argument from Phase 15 — a structural boundary survives a routing bug; a policy relying on every call site remembering to check does not.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [structural-tenant-isolation, mcp-governance]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Shared pool vs. dedicated pool per tenant
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson choose a shared worker pool with per-tenant fair-share scheduling over a fully dedicated pool per tenant, for the 50-tenant platform?

**OPTIONS:**
- [ ] A: Dedicated pools are technically impossible to implement for an agentic workflow platform
- [x] B: A shared pool is dramatically more compute-efficient given the uneven, mostly-waiting workload profile, and per-tenant concurrency caps bound the noisy-neighbor risk without the operational overhead of 50 fully separate pools
- [ ] C: Fair-share scheduling eliminates the need for per-tenant MCP server scoping entirely
- [ ] D: Dedicated pools would violate the platform's human-in-the-loop requirements
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's explicit trade-off is compute efficiency (shared pool) against operational overhead (50 dedicated pools) — fair-share scheduling is what lets the platform get the efficiency without the noisy-neighbor risk.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [shared-pool-tradeoff, fair-share-scheduling]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why workflow-state storage is deliberately CP
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson design workflow-state coordination (which orchestrator instance owns a given workflow's next step) as CP rather than AP?

**OPTIONS:**
- [ ] A: CP is always the correct default for any data path in a distributed system
- [x] B: Two orchestrator instances both believing they own the same workflow's next step would double-execute a tool call — an outcome the system cannot tolerate, unlike the vector index's staleness in Lesson 2, which was an acceptable AP trade
- [ ] C: Workflow state changes so rarely that consistency has no real cost either way
- [ ] D: AP designs are incompatible with human-in-the-loop approval gates
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's explicit contrast with Lesson 2's RAG index — the correct consistency model is a property of what a specific failure would cost (double-executing a tool call here versus stale search results there), not a platform-wide default.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [workflow-state-cp, exactly-once-ownership]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Circuit breaker behavior on LLM-provider outage
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What should the model-routing gateway do when the primary LLM provider becomes unavailable, per the lesson's failure-mode design?

**OPTIONS:**
- [ ] A: Stall every in-flight workflow waiting on that provider until it recovers, with no fallback
- [x] B: Trip a circuit breaker and fail over to an alternate provider tier, rather than let every dependent workflow stall indefinitely
- [ ] C: Immediately terminate every in-flight workflow across all 50 tenants
- [ ] D: Silently drop the failing requests with no retry or fallback of any kind
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's design is a circuit breaker with failover, consistent with the model-routing gateway's reliability discipline from Phase 12, not a stall or a silent drop.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [circuit-breaker, provider-failover]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why a stuck workflow needs a bounded retry count
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does a workflow retrying a failing tool call need a bounded retry count and a dead-letter state, rather than retrying indefinitely?

**OPTIONS:**
- [ ] A: Bounded retries are required by every LLM provider's terms of service
- [x] B: An indefinitely retrying workflow consumes its tenant's fair-share concurrency budget forever, degrading that tenant's own other workflows without ever surfacing the problem to a human
- [ ] C: Tool calls can only be retried a maximum of three times by protocol design
- [ ] D: Dead-letter states are only relevant for workflows involving a human-in-the-loop gate
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson connects this directly to the fair-share scheduling design — an unbounded retry loop is exactly the noisy-neighbor failure mode the per-tenant concurrency cap is meant to prevent, and a dead-letter state is what makes the problem visible instead of silently ongoing.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [bounded-retries, dead-letter-state]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Idempotency for a timed-out-but-succeeded tool call
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why must a tool call that times out from the orchestrator's perspective but actually succeeded downstream be protected by an idempotency key?

**OPTIONS:**
- [ ] A: Idempotency keys are required by MCP's protocol specification for every call
- [x] B: Without one, a retry of the timed-out call would execute the side-effecting action (a refund, a deal-stage update) a second time, since the orchestrator has no way to know the first attempt already succeeded
- [ ] C: Idempotency keys make tool calls execute faster on retry
- [ ] D: This scenario cannot actually occur once workflow state is stored in a CP data path
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the same idempotency discipline from Phase 13's tool-contract lesson, applied here to the specific timeout-vs-actual-success ambiguity a retry has no other way to resolve safely.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [idempotent-tool-calls, timeout-ambiguity]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What changes for a compliance-driven dedicated-compute tenant
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, when one tenant requires physically isolated compute for compliance reasons, which piece of the platform's design actually has to change?

**OPTIONS:**
- [ ] A: The workflow-state consistency model must switch from CP to AP for every tenant, not just this one
- [x] B: Only the worker-pool routing for this one tenant's workflows needs to change (to a dedicated pool); the per-tenant MCP server scoping and workflow-state CP design were already tenant-isolated by construction and need no change
- [ ] C: MCP server scoping must be rebuilt from scratch, since it was never actually tenant-isolated before
- [ ] D: Every other tenant must also move to dedicated compute for the platform to remain consistent
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Because MCP scoping and workflow-state ownership were already designed per-tenant, only the physical compute-routing layer needs to change for this one tenant — the lesson's point is that good tenant-isolation design at the right layers means a compliance requirement like this is a narrow, contained change, not a platform-wide rearchitecture.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [dedicated-compute-tenant, contained-design-change]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: own knowledge (async I/O-bound concurrency patterns; MCP governance and multi-tenant agent platform design practice)

---

# LESSON 4

```yaml
lesson_id: fde-system-design-capstone-04-system-design-multi-tenant-saas-platform
lesson_title: "System Design: Multi-Tenant SaaS Platform"
lesson_order: 4

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: system-design-capstone
module_name: "8. System Design, Capstone & Hiring Readiness"
module_order: 8

difficulty: Hard
estimated_minutes: 85
content_status: Draft

learning_outcomes:
  - "Choose between RLS shared-schema, schema-per-tenant, and database-per-tenant isolation for different tenant-size tiers within one platform, using a capacity estimate to justify the tier boundaries."
  - "Design noisy-neighbor mitigation for a shared-RLS tier — connection pooling limits, statement timeouts, and query cost governance — and explain what each specifically prevents."
  - "Design a tenant's migration path from a shared isolation tier to a dedicated one, and name the trigger metric that should drive it."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# System Design: Multi-Tenant SaaS Platform

## Concepts Covered

Phase 15 already taught the mechanism — Postgres RLS, `SET LOCAL` session context, per-tenant idempotency keys — for enforcing tenant isolation within a single shared database. This lesson does not re-teach that mechanism; it asks the system-design question RLS alone doesn't answer: at what tenant-population scale, and for which tenants specifically, does shared-schema RLS stop being the right isolation strategy, and what replaces it? The honest answer is that isolation strategy is not a single platform-wide decision — a real multi-tenant SaaS platform almost always ends up running more than one isolation strategy simultaneously, tiered by tenant size and requirements, because the three common strategies trade off cost, operational overhead, and blast radius differently, and no single point on that trade-off curve is right for both a 500MB free-tier tenant and a 5TB enterprise tenant with a contractual data-residency requirement.

The three strategies differ in where the isolation boundary physically lives. RLS shared-schema, shared-database (Phase 15's mechanism) puts every tenant's rows in the same tables, with the database itself enforcing the boundary per query via policy — the cheapest strategy by a wide margin (one schema, one set of indexes, one connection pool to operate), but its blast radius is the largest: a single RLS policy bug or a `BYPASSRLS` misconfiguration can, in principle, expose every tenant sharing that schema at once. Schema-per-tenant puts each tenant's tables in their own Postgres schema within the same database cluster — a real isolation improvement (a schema-level permission error can't silently return another tenant's rows the way a missing RLS predicate can) and it makes per-tenant operations like a point-in-time restore of one specific tenant's data tractable in a way a shared-schema restore fundamentally isn't, but it multiplies the number of schemas (and, practically, migrations that must run against each one) linearly with tenant count, which becomes a real operational burden in the thousands. Database-per-tenant goes further still — each tenant gets an entirely separate database (potentially on separate compute), giving the strongest isolation and the cleanest story for a customer's own compliance or data-residency demands, at the highest cost: a naive one-connection-pool-per-database model breaks down long before a few hundred tenants, because connection pool exhaustion (each database needing its own reserved pool slots against a hard connection ceiling) becomes the actual constraint, not compute — a constraint a connection-pooling proxy that can multiplex logical tenant connections onto a shared pool (PgBouncer with dynamic per-tenant routing, or a managed equivalent) is specifically built to solve, and any DB-per-tenant design at real scale needs that proxy layer as a first-class component, not an afterthought.

## Practical Backend Scenario

**Requirements clarification.** Functional: a general multi-tenant SaaS platform (CRUD-heavy application data, per-tenant reporting, per-tenant admin operations including point-in-time restore). Non-functional: a tenant population with a heavily skewed size distribution — several thousand small, self-serve tenants; a smaller number of mid-market tenants with real support contracts; and a handful of enterprise "whale" tenants with strict per-tenant SLAs and, for some, contractual data-residency requirements. The platform must guarantee that one tenant's usage pattern (a runaway report query, a data migration import) cannot degrade another tenant's experience — the noisy-neighbor requirement that is the load-bearing constraint of this entire design.

**Capacity estimation.** Assume 5,000 total tenants: 4,900 small tenants averaging 1GB of data each (≈4.9TB aggregate), 90 mid-market tenants averaging 10GB each (≈900GB aggregate), and 10 enterprise tenants ranging from 500GB to several TB each (a genuinely different scale regime, easily exceeding the entire small-tenant tier combined for the largest single account). This distribution is the direct justification for tiering: treating the enterprise tenants the same as the long tail would force either massively over-provisioning the shared tier's infrastructure to accommodate the handful of whales, or under-serving those whales' actual SLA needs — neither of which is necessary once the tiers are separated.

**High-level design.** Three isolation tiers map directly onto the three size classes: the 4,900 small tenants share one RLS-enforced schema and database (Phase 15's mechanism, at scale it was designed for), the 90 mid-market tenants each get their own schema within a shared database cluster (schema-per-tenant, giving them per-tenant restore and a stronger isolation boundary their support contracts justify), and the 10 enterprise tenants each get a dedicated database, provisioned behind a connection-pooling proxy that multiplexes their traffic without requiring a permanently reserved connection-pool slot per tenant sitting idle most of the time. A tenant's tier is not fixed at signup — the platform tracks tier-appropriate metrics per tenant and supports migrating a tenant upward as it grows.

**Deep dive — three hard trade-offs.** First, the three-tier isolation strategy itself: the case for it over a single strategy applied uniformly is exactly the skewed distribution above — RLS shared-schema is by far the cheapest per-tenant to operate and is correct for thousands of small tenants where the operational cost of schema-per-tenant would dwarf what any of them individually pays the platform, while a whale tenant's SLA and blast-radius requirements justify the real cost of a dedicated database that would be wasteful for a 1GB tenant. Second, noisy-neighbor mitigation within the shared-RLS tier specifically, since it's the tier holding by far the most tenants on the least isolated infrastructure: a per-tenant-role `statement_timeout` (so one tenant's accidentally unindexed, full-table-scanning report query is killed rather than holding a connection and CPU indefinitely), a connection-pool cap per tenant role (so one tenant cannot exhaust the shared pool's connection slots and starve every other tenant sharing it), and, for genuinely reporting-heavy small tenants, routing their read traffic to a dedicated read replica rather than the primary that write-path tenants depend on — three independent mechanisms, each closing a different specific way one tenant's load can degrade another's, none of which is optional once real tenants share real infrastructure. Third, the tier-migration decision: a tenant should move from shared-RLS to schema-per-tenant, or from schema-per-tenant to a dedicated database, based on an evidenced trigger — data volume crossing a threshold, sustained query load that repeatedly hits the shared tier's guardrails, or a contractual requirement (data residency, a dedicated-restore SLA) — not as a one-time decision made at signup based on a sales conversation's guess about how large the tenant will eventually become.

**Failure modes.** An RLS policy misconfiguration (Phase 15's owner-bypass gotcha: a connection running as the table owner, or a table missing `FORCE ROW LEVEL SECURITY`, silently sees every tenant's rows) is the single most dangerous failure mode in the shared tier precisely because it can pass every test written from a non-owner role — it requires a standing audit habit, not a one-time check, testing explicitly that a wrong tenant's rows are absent, not merely that the right tenant's rows are present. A single whale tenant landing in the shared tier by mistake (a sales or onboarding error, not a technical one) risks a platform-wide outage the moment that tenant's usage spikes — which is why the tier-assignment decision needs an explicit, enforced threshold check at onboarding, not just at growth time.

## Practice Loop

1. For the 5,000-tenant distribution above, recompute what fraction of total platform data volume the 10 enterprise tenants represent versus the 4,900 small tenants combined, and use the result to argue in one sentence why treating all 5,000 tenants identically would be the wrong default.
2. Design the `statement_timeout`, connection-pool cap, and read-replica-routing mechanisms for the shared-RLS tier, and for each, write one sentence naming the specific noisy-neighbor scenario it prevents.
3. Diagnostic step: simulate a mid-market tenant's data volume crossing 200GB (well past the shared-RLS tier's typical small-tenant profile) and trace what evidence should trigger a review of whether that tenant needs to move to a dedicated schema, versus what evidence would suggest it's fine to leave as is.
4. Design the connection-pooling proxy layer for the 10 dedicated-database enterprise tenants, and explain specifically why a naive one-reserved-pool-per-database model breaks down well before a few hundred tenants even though only 10 tenants are in this tier today.
5. Write the RLS audit test the shared tier needs: not "tenant A's own data is present and correct" but the explicit negative assertion Phase 15 requires, and confirm it would have caught a `FORCE ROW LEVEL SECURITY` omission.

## Evidence of Understanding

You can choose between RLS shared-schema, schema-per-tenant, and database-per-tenant isolation for different tenant tiers within one platform, and justify the tier boundaries using a capacity estimate showing the actual skew in tenant size and requirements, not a uniform default. You can design three independent noisy-neighbor mitigations for a shared-RLS tier and explain what specific failure mode each one closes. You can design a tenant's migration path between isolation tiers driven by an evidenced trigger metric, and explain why the RLS owner-bypass failure mode specifically requires a standing audit habit rather than a one-time check.

## Suggested Extension

One of the 90 mid-market, schema-per-tenant customers is acquired by one of the 10 enterprise, dedicated-database customers, and the acquiring company wants their two tenants' data queryable together for a combined reporting view without merging the underlying isolation tiers. Design how the platform would support this cross-tenant read without weakening either tenant's own isolation boundary, and name the specific risk this feature reintroduces that the rest of this lesson's design was built to avoid.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why no single isolation strategy fits a real tenant population
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that a real multi-tenant SaaS platform usually needs more than one isolation strategy running simultaneously, rather than picking one for the whole platform?

**OPTIONS:**
- [ ] A: Because Postgres technically does not support running RLS and schema-per-tenant in the same database cluster
- [x] B: Because the three strategies trade off cost, operational overhead, and blast radius differently, and a real tenant population's skewed size distribution means no single point on that trade-off curve serves both a tiny free-tier tenant and a multi-terabyte enterprise tenant well
- [ ] C: Because schema-per-tenant is strictly better than RLS in every way and should always be preferred once a platform can afford it
- [ ] D: Because database-per-tenant is required by law for any platform serving more than 1,000 tenants
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's core argument is about matching the isolation strategy's trade-off profile to the actual, skewed tenant distribution, not asserting one strategy is universally superior.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [tiered-isolation-strategy, skewed-tenant-distribution]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What database-per-tenant's real constraint is at scale
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what is the actual constraint that breaks a naive database-per-tenant design well before a few hundred tenants?

**OPTIONS:**
- [ ] A: Postgres cannot technically run more than 100 separate databases on one cluster
- [x] B: Connection pool exhaustion — a one-reserved-pool-per-database model runs into a hard connection ceiling long before compute becomes the bottleneck, requiring a connection-pooling proxy that multiplexes tenant connections
- [ ] C: Query performance inherently degrades once more than 100 databases exist on a single server
- [ ] D: Database-per-tenant designs cannot support point-in-time restore at any scale
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific claim is about connection pooling, not compute or query performance — a pooling proxy that multiplexes logical tenant connections is what actually makes DB-per-tenant viable at real scale.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [connection-pool-exhaustion, pooling-proxy]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why the capacity estimate justifies the tier boundaries
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson use the 4,900/90/10 tenant-size breakdown to justify the three-tier isolation design, rather than choosing a tier count arbitrarily?

**OPTIONS:**
- [ ] A: Three tiers is simply the industry-standard number regardless of any specific platform's tenant distribution
- [x] B: The breakdown shows the actual skew — a handful of enterprise tenants hold data volume and SLA requirements dramatically different from the long tail, which is the concrete evidence that treating all tenants uniformly would either over-provision for the small tenants or under-serve the large ones
- [ ] C: The breakdown is used only to calculate the platform's total hosting bill, not to justify the isolation design
- [ ] D: Three tiers were chosen because Postgres only supports three distinct isolation mechanisms
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The capacity estimate is the load-bearing evidence for the tiering decision — the lesson explicitly ties the tier boundaries to the measured skew in tenant size, not to an arbitrary or universal tier count.

**LESSON_CONNECTION:** Practical Backend Scenario, Capacity Estimation
**KEYWORDS:** [capacity-estimate-justification, tier-boundary-evidence]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What a per-tenant statement_timeout specifically prevents
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific noisy-neighbor scenario does a per-tenant-role `statement_timeout` in the shared-RLS tier prevent?

**OPTIONS:**
- [ ] A: A tenant exceeding their contracted total storage quota
- [x] B: One tenant's accidentally unindexed, full-table-scanning query holding a connection and CPU indefinitely, degrading every other tenant sharing the same infrastructure
- [ ] C: A tenant attempting to read another tenant's rows without an RLS policy in place
- [ ] D: Two tenants signing up with the same email domain
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the specific mechanism-to-failure mapping the lesson requires — a statement timeout bounds how long one runaway query can hold shared resources, distinct from RLS (which is about row-level access, not resource consumption).

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [statement-timeout, noisy-neighbor-mitigation]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the tier-migration trigger must be evidenced
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist a tenant's move from shared-RLS to schema-per-tenant should be driven by an evidenced trigger metric, rather than decided once at signup?

**OPTIONS:**
- [ ] A: Because Postgres technically prevents migrating a tenant between isolation tiers after signup
- [x] B: Because a sales conversation's guess about eventual tenant size at signup is unreliable, while data volume, sustained load against the shared tier's guardrails, or an actual contractual requirement are measurable signals the platform can act on when they actually occur
- [ ] C: Because every tenant eventually needs to migrate to the most isolated tier regardless of actual size
- [ ] D: Because tier migration is only possible once a tenant reaches the enterprise size class
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific argument is evidence-over-guesswork — a signup-time guess is unreliable, while a measured signal (volume, load, contract) is something the platform can actually act on correctly and at the right time.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [tier-migration-trigger, evidence-based-migration]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the RLS owner-bypass failure mode is especially dangerous
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson single out the RLS owner-bypass gotcha (a table missing `FORCE ROW LEVEL SECURITY`, or a connection running as the table owner) as the single most dangerous failure mode in the shared tier?

**OPTIONS:**
- [ ] A: Because it only affects tenants in the schema-per-tenant tier, not the shared-RLS tier
- [x] B: Because it can pass every test written from a non-owner role, making it invisible until an audit specifically tests the negative case — that a wrong tenant's rows are genuinely absent, not merely that the right tenant's rows are present
- [ ] C: Because it is the only failure mode that requires a database restart to fix
- [ ] D: Because it can only occur once a tenant crosses the 1GB data-volume threshold
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the specific danger the lesson names, directly inherited from Phase 15's RLS lesson — a test suite that only checks the positive case (right tenant's data present) can pass while a leak of another tenant's data goes completely unnoticed.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [rls-owner-bypass, negative-case-testing]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why a misassigned whale tenant threatens the whole shared tier
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does a single enterprise-scale tenant landing in the shared-RLS tier by an onboarding mistake risk a platform-wide outage?

**OPTIONS:**
- [ ] A: Enterprise tenants are technically incompatible with the RLS mechanism and cause immediate query errors
- [x] B: The shared tier's guardrails (statement timeouts, connection caps, read-replica routing) are sized for the long tail's typical usage, and a whale-scale tenant's usage spike can exceed them in ways that degrade every other tenant sharing that infrastructure
- [ ] C: Whale tenants always have more support tickets than small tenants, overwhelming the support team
- [ ] D: A whale tenant in the shared tier automatically triggers a schema migration for every other tenant
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's point is capacity mismatch — the shared tier's guardrails are calibrated for the long tail, and an enterprise-scale tenant's usage can exceed what those guardrails were sized to absorb, directly threatening every tenant sharing that infrastructure.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [misassigned-tenant-risk, guardrail-capacity-mismatch]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why schema-per-tenant enables tractable per-tenant restore
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say schema-per-tenant makes a point-in-time restore of one specific tenant's data tractable in a way shared-schema RLS fundamentally doesn't?

**OPTIONS:**
- [ ] A: Schema-per-tenant databases are backed up more frequently than shared-schema databases by default
- [x] B: Each tenant's data lives in its own schema, so restoring that schema restores exactly and only that tenant's data; a shared-schema restore would restore every tenant's data at once, since they all live in the same tables
- [ ] C: RLS makes point-in-time restore technically impossible for any tenant under any circumstances
- [ ] D: Schema-per-tenant tenants are not permitted to request a restore at all
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The mechanism is structural: a schema boundary aligns exactly with a tenant boundary, so a restore operation scoped to a schema naturally scopes to one tenant — something a shared-table restore cannot do without restoring every tenant's rows in that table.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [schema-per-tenant-restore, isolation-boundary]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** The risk a cross-tenant reporting feature reintroduces
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, what specific risk does building a combined cross-tenant reporting view (for an acquiring company's two tenants) reintroduce that the rest of this lesson's design was built to avoid?

**OPTIONS:**
- [ ] A: The risk that connection pooling becomes unnecessary once cross-tenant queries are allowed
- [x] B: The exact cross-tenant data-leak risk RLS and schema isolation were built to prevent — a feature that deliberately reads across tenant boundaries needs its own carefully scoped, explicit exception rather than weakening the underlying isolation guarantee for either tenant more broadly
- [ ] C: The risk that the acquiring company's dedicated database will run out of storage
- [ ] D: The risk that schema-per-tenant migrations will fail for unrelated tenants
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the tension the extension is designed to surface — a legitimate cross-tenant feature has to be built as a narrow, explicit exception, not by loosening the isolation guarantees this entire lesson was built to establish.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [cross-tenant-feature-risk, scoped-exception-design]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: own knowledge (multi-tenant SaaS isolation strategy patterns; Postgres connection pooling and RLS operational practice)

---

# LESSON 5

```yaml
lesson_id: fde-system-design-capstone-05-system-design-enterprise-integration-hub
lesson_title: "System Design: Enterprise Integration Hub"
lesson_order: 5

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: system-design-capstone
module_name: "8. System Design, Capstone & Hiring Readiness"
module_order: 8

difficulty: Hard
estimated_minutes: 85
content_status: Draft

learning_outcomes:
  - "Design a hub-based integration topology for 20+ enterprise source systems from scratch, and quantify the connection-count savings over point-to-point using the actual system count."
  - "Choose sync-vs-async and batch-vs-event-driven delivery per connector based on each system's actual freshness requirement, and design a saga for a multi-system write with per-step compensation."
  - "Design the hub's failure isolation (per-connector circuit breaking, dead-letter queues, backpressure) so one source system's outage cannot halt the bus for every other system."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# System Design: Enterprise Integration Hub

## Concepts Covered

Phase 13's integration-topology lesson established the vocabulary — CRM, ERP, ITSM as distinct sources of record; point-to-point growing combinatorially versus a hub-based topology growing linearly — and Phase 14 built the connector-layer mechanics (OAuth refresh, cursor pagination, rate-limit backoff, idempotent writes) and entity resolution (fuzzy matching, golden records, source-of-record conflict rules) for connecting to one system at a time. This lesson is the system-design synthesis of both: actually architecting the hub itself for an enterprise with 20+ source systems, not one or two. At this system count, the combinatorial argument for hub-based topology stops being a rule of thumb and becomes an unambiguous number — the reason the design decision has already been made before the first component is drawn, and the real design work shifts entirely to how the hub itself is built: what sits at its center, how heterogeneous freshness requirements across 20+ systems are supported without forcing every connector onto the same topology, and how the hub survives one connector's failure without becoming a single point of failure for the other nineteen.

The central design tension at this scale is that a hub-based topology's biggest architectural risk is also its biggest architectural benefit: putting one shared intermediary in the middle means every system's data flows through one place, which is exactly what makes entity resolution, saga-based multi-system writes, and centralized audit logging buildable once instead of redundantly per point-to-point connection — but it also means the hub itself must never become a system-count-N single point of failure, where one misbehaving connector or one overloaded downstream consumer degrades the other nineteen systems' otherwise-healthy traffic. This is not a hypothetical tension; it's the direct consequence of centralizing 20+ systems' worth of heterogeneous traffic — vastly different volumes (a CRM firing dozens of webhook events per second versus an HR system exporting once nightly), vastly different freshness needs, and vastly different reliability profiles (some source systems are rock-solid SaaS platforms, others are internal legacy systems an FDE cannot fully trust to stay up) — onto one piece of shared infrastructure, and resolving that tension is most of what separates a hub design that scales cleanly to 20+ systems from one that becomes exactly the kind of fragile central chokepoint the hub pattern was supposed to avoid.

## Practical Backend Scenario

**Requirements clarification.** Functional: bi-directional synchronization across 20+ source systems (a CRM, an ERP, an ITSM platform, an HR system, and a long tail of internal and third-party systems), a standing entity-resolution service maintaining a golden-record crosswalk across all of them (Phase 14's mechanism, now serving every consumer rather than one), and saga-coordinated multi-system writes for workflows that must update more than one system consistently (Lesson 1's pattern, applied here). Non-functional: some flows need near-real-time freshness (a support ticket update reflected across systems within seconds), others tolerate daily batch (financial reconciliation reporting); the hub must survive any single connector's outage without disrupting any other system's traffic; every write must be auditable end to end.

**Capacity estimation.** Across 20 source systems, assume a skewed event-volume profile: 3-4 high-volume systems (CRM, ITSM) generating on the order of 20-50 webhook events per second at peak each, and the remaining systems generating a combined trickle of a few events per second plus nightly batch jobs — a reasonable peak aggregate hub throughput estimate of roughly 150-200 events/second. Point-to-point would require up to 20×19/2 = 190 pairwise connections if every system pair needed to talk directly; the hub-based topology collapses this to 20 connector integrations (one per system) plus whatever consumers subscribe to the bus — the concrete number that makes the topology decision a closed question at this system count, not a judgment call. Connector count therefore scales linearly (N) with source-system count, not combinatorially (N²), which is the entire basis for the hub's operational tractability as the 21st and 22nd systems are inevitably added later.

**High-level design.** A central event bus (a durable, partitioned log — the same shape as an event-driven data platform, distinct from a simple message queue in that consumers can replay history, which matters for a newly-added downstream consumer needing to catch up on state it missed) sits at the hub's core. Each of the 20+ source systems has its own connector, built against Phase 14's abstraction layer (`fetch_page`, `fetch_record`, `write_record`) with system-specific OAuth, pagination, and rate-limit handling isolated inside it — publishing changes onto the bus (webhook-driven for systems needing near-real-time freshness, scheduled-batch for systems that don't) and consuming write requests routed to it from the bus. A standing entity-resolution service consumes the bus's identity-relevant events, maintains the golden-record crosswalk, and publishes resolved identity mappings back onto the bus for every other consumer to use — built once, serving all 20+ systems' worth of downstream consumers, instead of being reimplemented per point-to-point pair the way Phase 14's lesson showed it would have to be without a hub. A saga orchestrator (Lesson 1's pattern) coordinates any workflow needing a consistent multi-system write, calling each system's connector in sequence with a compensating action per step. An audit log records every event and every write, keyed by the same crosswalk identity, giving one unified answer to "what happened to this real-world entity across every system it touches," a question Phase 14's lesson noted was unanswerable without a standing, hub-centralized resolution process.

**Deep dive — three hard trade-offs.** First, delivery semantics for the bus: exactly-once delivery is real infrastructure to build and operate correctly at 20+-system scale, and the pragmatic default — for the same reason Phase 14's connector-write-back lesson already established — is at-least-once delivery paired with idempotent consumers, using the same `(entity_id, event_id)`-style idempotency keys the earlier connector-design lesson required for a single system's writes, now enforced uniformly across every consumer subscribing to the bus rather than reasoned about per pair. Second, sync-versus-async and batch-versus-event-driven per connector, decided individually per system by its actual freshness requirement (Phase 13's axis) rather than forcing every one of the 20+ systems onto one uniform topology: the CRM and ITSM connectors are webhook-driven because a support conversation genuinely needs near-real-time state, while the HR and finance-reporting connectors stay on nightly batch because nothing downstream needs same-day freshness from them, and building batch-only or webhook-only support into the hub as a hard constraint would force a wrong trade-off onto whichever category of system doesn't fit it. Third, where entity resolution runs: centralizing it in the hub, as a standing service consumed by every downstream system, is what makes it buildable once instead of redundantly reimplemented at each of up to 190 point-to-point pairs — the same "build once, serve every consumer" argument the hub topology itself makes for connection count, now applied specifically to identity resolution rather than raw connectivity.

**Failure modes.** A single connector's outage (a legacy internal system going down, or a third-party API's own incident) must not halt the bus for any other system — each connector runs behind its own circuit breaker, and a connector's failed publish or consume attempts route to a dead-letter queue for that connector specifically, isolated from every other connector's own traffic. A downstream consumer falling behind (the entity-resolution service backing up under load, or a saga orchestrator processing workflows slower than events arrive) must apply backpressure — a bounded queue with consumer-lag alerting — rather than let unbounded buffering silently grow until the hub itself runs out of memory or disk. A saga step failing mid-multi-system-write (an invoice created in the ERP but a corresponding CRM deal-stage update failing) needs the exact compensating-action discipline Lesson 1 built — reversing or flagging the ERP-side effect for reconciliation, never leaving two systems' states silently disagreeing with no record of the discrepancy.

## Practice Loop

1. Compute the point-to-point connection count for 20 systems (N×(N-1)/2) versus the hub-based connector count (N), and recompute both for 25 systems to show how the gap widens as more systems are added — this diagnostic step is what makes the topology decision a closed question rather than a preference.
2. Draw the hub's component diagram (event bus, 20+ connectors, entity-resolution service, saga orchestrator, audit log) and label which components are shared, built once, versus which are per-system.
3. For three specific systems in the scenario (CRM, ITSM, HR/finance), classify each as webhook-driven or batch, and justify each choice using that specific system's actual downstream freshness requirement, not a platform-wide default.
4. Design the saga for a multi-system write (e.g., a new deal closing in the CRM triggers an ERP invoice and an ITSM onboarding ticket), including a compensating action for each step, and trace what happens when the ITSM step fails after the ERP invoice already succeeded.
5. Simulate one connector's outage (pick the HR system) and confirm, in your design, that the CRM and ITSM connectors' traffic continues flowing unaffected — this is the diagnostic proof that the failure-isolation design actually works, not just a stated intention.

## Evidence of Understanding

You can design a hub-based integration topology for 20+ source systems from scratch and quantify the connection-count savings over point-to-point using the actual system count, not an abstract argument. You can choose sync-vs-async and batch-vs-event-driven delivery per connector based on each system's actual freshness requirement, and design a saga with per-step compensation for a multi-system write that must stay consistent across the hub. You can design the hub's failure isolation — per-connector circuit breaking, dead-letter queues, backpressure — so that no single source system's outage or slowdown can halt or degrade the bus for any other system.

## Suggested Extension

A 21st system — a newly-acquired subsidiary's own CRM, running on a different platform than the parent company's — needs to join the hub, and its data must be entity-resolved against the existing crosswalk built from the original 20 systems. Design what changes for the entity-resolution service specifically (new signals to match on, since the subsidiary's records share no ID structure with the parent's systems) versus what stays exactly as it was for the bus, the connector abstraction layer, and the saga orchestrator.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why the topology decision is closed at 20+ systems
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that the point-to-point-versus-hub topology decision "stops being a rule of thumb and becomes an unambiguous number" once an enterprise has 20+ source systems?

**OPTIONS:**
- [ ] A: Because point-to-point integration becomes technically impossible to implement above 20 systems
- [x] B: Because the point-to-point connection count (up to 190 pairwise connections for 20 systems) versus the hub's linear connector count (20) makes the operational cost gap concrete and decisive, not a matter of preference
- [ ] C: Because hub-based topologies only became available as a pattern once systems reached this scale
- [ ] D: Because 20 systems is the maximum number any event bus can technically support
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific claim is about the concrete number (190 vs. 20) making the decision unambiguous, not about any technical impossibility of point-to-point at this scale.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [hub-topology-decision, connection-count-math]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** The hub's central tension
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson identify as the hub topology's central design tension at 20+-system scale?

**OPTIONS:**
- [ ] A: Hub-based topologies cannot support both synchronous and asynchronous connectors at the same time
- [x] B: Centralizing all systems' traffic through one intermediary is exactly what makes entity resolution, sagas, and audit logging buildable once — but it also means the hub itself must never become a single point of failure that one connector's misbehavior degrades for every other system
- [ ] C: Entity resolution is impossible to build correctly once more than 10 systems are involved
- [ ] D: A hub-based topology requires every source system to use the same authentication protocol
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's stated central tension — the hub's centralization is simultaneously its biggest benefit (build-once shared services) and its biggest risk (a potential single point of failure), and resolving that tension is the real design work.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [hub-central-tension, single-point-of-failure-risk]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why exactly-once delivery is not the pragmatic default
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson choose at-least-once delivery with idempotent consumers over building exactly-once delivery into the hub's event bus?

**OPTIONS:**
- [ ] A: Exactly-once delivery is theoretically impossible in any distributed messaging system
- [x] B: Exactly-once delivery is real infrastructure to build and operate correctly at 20+-system scale, while at-least-once paired with idempotency keys (already required for connector writes) achieves the same practical safety with far less operational complexity
- [ ] C: At-least-once delivery is always faster than exactly-once delivery under any load
- [ ] D: Idempotent consumers are only needed for batch connectors, not event-driven ones
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's argument is pragmatic, not theoretical impossibility — at-least-once plus idempotency achieves the needed safety without the operational cost of building genuine exactly-once semantics.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [at-least-once-delivery, idempotent-consumers]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why connectors are decided individually, not uniformly
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist each of the 20+ connectors be decided individually as webhook-driven or batch, rather than forcing all connectors onto one uniform topology?

**OPTIONS:**
- [ ] A: Because the event bus technically cannot support more than one delivery pattern at a time
- [x] B: Because each system's actual downstream freshness requirement differs — forcing a uniform topology would impose a wrong trade-off on whichever category of system doesn't fit it (e.g., forcing batch on a support system needing near-real-time state)
- [ ] C: Because webhook-driven connectors are always superior and batch should only be used when webhooks are technically unavailable
- [ ] D: Because HR and finance systems are incapable of supporting webhook delivery under any circumstances
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's point is a per-system freshness-requirement decision (Phase 13's axis), not a preference for one pattern — a uniform default would force a wrong trade-off onto systems whose actual requirement doesn't match it.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [per-connector-freshness-decision, no-uniform-default]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why centralizing entity resolution pays off at this scale
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does running entity resolution as one standing hub service, rather than per point-to-point pair, matter more at 20+ systems than it would for just two or three?

**OPTIONS:**
- [ ] A: Entity resolution is only technically possible once a hub-based topology is in place
- [x] B: A point-to-point design would require reimplementing resolution logic redundantly at up to 190 pairs; centralizing it means it is built once and correctly serves every consumer, the same "build once, serve all" argument the hub makes for connectivity itself
- [ ] C: Entity resolution becomes unnecessary once more than 10 systems share the same hub
- [ ] D: Centralized entity resolution eliminates the need for any human review of ambiguous matches
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This directly extends the hub's core "build once" argument from raw connectivity to identity resolution specifically — the payoff scales with the number of systems that would otherwise each need their own resolution logic.

**LESSON_CONNECTION:** Practical Backend Scenario, Deep Dive
**KEYWORDS:** [centralized-entity-resolution, build-once-serve-all]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Isolating one connector's outage from the rest of the bus
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specifically prevents one connector's outage from halting the bus for every other one of the 20+ systems?

**OPTIONS:**
- [ ] A: The event bus automatically restarts every connector simultaneously whenever one fails
- [x] B: Each connector runs behind its own circuit breaker with its own dead-letter queue, so a failed connector's errors are isolated to that connector rather than blocking the bus's shared infrastructure
- [ ] C: Only one connector is permitted to be active on the bus at any given time
- [ ] D: Connectors do not communicate with the bus directly, so their failures cannot affect it
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the specific failure-isolation mechanism the lesson names — per-connector circuit breaking and dead-lettering, not a shared fate across all connectors.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [per-connector-circuit-breaker, dead-letter-isolation]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why backpressure, not unbounded buffering, on a slow consumer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson design a slow downstream consumer (e.g., the entity-resolution service falling behind) to apply backpressure rather than buffer unboundedly?

**OPTIONS:**
- [ ] A: Backpressure makes the slow consumer process events faster automatically
- [x] B: Unbounded buffering would let the backlog silently grow until the hub itself runs out of memory or disk, while a bounded queue with lag alerting surfaces the problem before it becomes a hub-wide incident
- [ ] C: Backpressure is only relevant for batch connectors, never for event-driven ones
- [ ] D: Buffering is technically unsupported by any event bus implementation
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific concern is bounding the failure — an unbounded backlog is a slow-motion hub-wide incident, while bounded backpressure with alerting surfaces the problem while it's still contained.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [backpressure, unbounded-buffering-risk]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Handling a mid-saga failure in the deal-closing workflow
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practice Loop's deal-closing saga, if the ERP invoice step succeeds but the ITSM onboarding-ticket step then fails, what should the saga do?

**OPTIONS:**
- [ ] A: Leave the ERP invoice in place with no record of the ITSM failure, since the invoice itself succeeded
- [x] B: Run the ERP step's compensating action (reverse or flag the invoice for reconciliation) per the saga pattern, rather than leave the two systems' states silently disagreeing with no record of the discrepancy
- [ ] C: Immediately retry the entire saga from the beginning an unlimited number of times until it succeeds
- [ ] D: Delete the CRM deal record entirely so the workflow never appears to have started
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is Lesson 1's saga-compensation discipline applied directly — a failed later step triggers the compensating action for the already-succeeded earlier step, never a silent, unreconciled state mismatch.

**LESSON_CONNECTION:** Practical Backend Scenario, Failure Modes
**KEYWORDS:** [saga-compensation, multi-system-write-failure]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What changes when a 21st system with no shared ID structure joins
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, when a newly-acquired subsidiary's CRM joins the hub with no shared ID structure against the existing 20 systems, what specifically has to change?

**OPTIONS:**
- [ ] A: The event bus's core architecture must be rebuilt to support a 21st system, since it was hard-coded for exactly 20
- [x] B: The entity-resolution service needs new corroborating signals to match the subsidiary's records against the existing crosswalk (since exact-key matching won't work); the bus, connector abstraction layer, and saga orchestrator need no structural change to onboard the new connector
- [ ] C: Every existing connector must be rewritten to support the subsidiary's authentication protocol
- [ ] D: The saga orchestrator must switch from orchestration to choreography once a 21st system is added
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Because the hub's core components (bus, connector abstraction, saga orchestrator) are already system-agnostic by design, onboarding a new system is a contained change — the real new work is specific to entity resolution, which needs new matching signals for records with no shared ID structure.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [onboarding-new-system, contained-design-change]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: own knowledge (enterprise integration hub patterns, event-driven architecture, entity resolution and saga orchestration practice)
