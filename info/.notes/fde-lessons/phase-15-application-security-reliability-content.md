# FDE Phase 15 — Module 7: Application Engineering, Security & Reliability (Lessons 1-6 of 12)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-15-application-security-reliability-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `application-security-reliability` ("7. Application Engineering,
Security & Reliability")

This is a **new module** and this file covers its **first half only** — lessons 1-6 of 12. A later
phase covers lessons 7-12 (Enterprise Security for FDE Systems: PII, SOC2, GDPR; Secrets, Encryption
& Deployment Topologies; Load Testing, Capacity Planning & Performance with k6; Incident Response &
Customer-Facing RCA; Enterprise Readiness Checklist & Go-Live; and an Assessment) and completes the
module — do not add placeholder content for those 6 lessons here.

Lesson 2 ("Frontend Essentials for FDEs: React + TypeScript") deliberately builds on Module 3
("Full-Stack FDE: TypeScript, React & AI-First Frontends") rather than re-teaching `useState`,
`useEffect`, or TypeScript basics — Module 3 already covers those. Lesson 3's Postgres RLS and Celery
coverage deliberately builds on Module 2's existing Celery/idempotent-webhook lesson ("Building
Payments & Notifications (Stripe, Celery)") rather than re-explaining what Celery is — it goes one
level up into multi-tenant-specific RLS and background-job design.

All six lessons follow one continuous scenario: an FDE engagement for **Meridian Legal Ops**,
building **ClauseReview**, a multi-tenant SaaS contract-review tool. Meridian sells ClauseReview to
corporate legal departments — the pilot customer is **Acme Corp**, with a second tenant, **Globex**,
onboarding partway through the lessons, which is what makes the multi-tenant design lesson concrete
rather than abstract.

---

# LESSON 1

```yaml
lesson_id: fde-application-security-reliability-01-product-thinking-and-architecture-for-fde-apps
lesson_title: "Product Thinking & Architecture for FDE Apps"
lesson_order: 1

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: application-security-reliability
module_name: "7. Application Engineering, Security & Reliability"
module_order: 7

difficulty: Intermediate
estimated_minutes: 55
content_status: Draft

learning_outcomes:
  - "Build a vertical slice — one full path through every layer for the narrowest real use case — before broadening any single layer of an FDE app."
  - "Distinguish a cheap architectural seam worth leaving on day one from speculative generality worth deferring, using a concrete migration-cost argument rather than intuition."
  - "Default an FDE app's architecture to a single store, single API, single worker process, reserving async boundaries for steps with evidenced latency, not assumed scale."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Product Thinking & Architecture for FDE Apps

## Concepts Covered

Product thinking for an FDE is not full product-management practice — it is compressing the distance between a confirmed PRD-lite and the smallest working system that proves the core value, because an FDE engagement runs in weeks, not quarters. The biggest architectural risk in that window is not picking the wrong scaling pattern; it is building generality nobody asked for yet, at the direct expense of shipping the one vertical slice that actually earns the next stakeholder demo. A vertical slice is a full path through every layer — request, business logic, storage, UI — for the single narrowest real use case, built ugly and working end to end, before any one layer gets broadened or polished further. This is the opposite of layer-first building, where an FDE builds a generic ingestion pipeline, then a generic processing layer, then a generic UI, with no working system to react to until all three are "done" — a structure that reliably misjudges what actually matters, because judgment about what matters comes from watching a real user hit a real gap in a working system, not from anticipating gaps in the abstract.

The architecture "spine" for a new FDE app should default to boring: one relational store, one API process, one background worker, synchronous request handling except where a specific, evidenced step — not an assumed future one — genuinely requires moving off the request path. This is not "build nothing extra" as a blanket rule; it is a judgment call about which seams are cheap to leave now and expensive to retrofit later, versus which generality is genuinely speculative. A tenant-scoping column on every table costs one column and one migration today; adding it after a pilot customer's data already exists means retrofitting every existing query and risking a missed one leaking data across tenants — that is a seam worth leaving from day one. A plugin architecture supporting five interchangeable LLM providers, when only one has ever been requested, is speculative generality — it adds real complexity today against a requirement that may never materialize, and building it can always happen later, cheaply, once a second provider is an actual, not hypothetical, requirement. This is the discovery-and-scoping module's non-goals discipline, applied to code structure instead of a written document.

## Practical Backend Scenario

Scoping ClauseReview's MVP for Meridian's pilot customer, Acme Corp, the FDE makes three architecture decisions in the same sitting. First: every table carries an `org_id` column and every query is written scoped by it from the very first migration, even though only Acme's data will ever exist in the database for the next several weeks — a one-column, day-one decision. Second: Meridian's product lead asks, in the same meeting, whether the extraction pipeline should support swapping between multiple LLM providers, since "we might want that eventually" — the FDE declines to build it now, since no second provider has ever been named as an actual requirement, and notes it as a clean extension point to revisit if one is. Third: the FDE measures that document extraction genuinely takes 30-90 seconds per contract — long enough that a synchronous HTTP request would time out or feel broken — and moves only that specific step off the request path into a background worker, while the upload endpoint itself, the review-queue listing, and the export endpoint all stay synchronous, because none of them have shown any latency problem that would justify the added complexity of an async boundary.

## Practice Loop

1. Write a one-page architecture spine for the ClauseReview MVP naming the single API, single store, and single worker, and state which specific step (contract extraction) evidences the one async boundary and why the other endpoints stay synchronous.
2. List every piece of "generality" a stakeholder has asked for (multi-LLM-provider support, per-customer configurable extraction rules) and mark each build-now or defer, with one sentence of justification per item.
3. Count how many tables and queries would need a migration if `org_id` were added after Acme's pilot data already existed, versus added on day one — this diagnostic quantifies the seam-versus-generality distinction rather than asserting it.
4. Draw the vertical slice — upload, extract, review, export — and confirm every layer has at least a working, unpolished implementation before any single layer is refined further.
5. Rewrite the architecture one-pager to explicitly state what this MVP's architecture will not support yet (multi-provider extraction, per-tenant custom extraction rules), so a stakeholder has something concrete to check a later request against.

## Evidence of Understanding

You can build a vertical slice through every layer of a new FDE app for its narrowest real use case, rather than building any single layer out generically first. You can distinguish a cheap architectural seam worth leaving on day one from speculative generality worth deferring, using a concrete migration-cost argument rather than gut feel. You can default a new app's architecture to a single store, API, and worker, and justify an async boundary with a measured latency figure rather than an assumed one.

## Suggested Extension

Add a second pilot customer, Globex, to the scenario once the MVP has shipped, and name exactly which day-one decision (the `org_id` column) pays off immediately versus which correctly-deferred decision (the multi-provider plugin) should still stay deferred, since Globex still uses the same single LLM provider Acme does.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What a vertical slice actually is
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson mean by building a "vertical slice" for an FDE app's MVP?

**OPTIONS:**
- [x] A: A full, working path through every layer — request, logic, storage, UI — for the single narrowest real use case, built end to end before any one layer is broadened or polished
- [ ] B: Building the database schema completely before writing any API or UI code
- [ ] C: A UI mockup that demonstrates the intended user flow without any working backend
- [ ] D: A generic ingestion pipeline built to handle every future use case before the first real one is implemented

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson explicitly defines a vertical slice as cutting through every layer for the narrowest real case, in direct contrast to layer-first building, which builds one layer generically before any other layer exists.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [vertical-slice, layer-first-risk]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why layer-first building misjudges what matters
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that layer-first building (a generic ingestion pipeline, then a generic processing layer, then a generic UI) tends to misjudge what actually matters?

**OPTIONS:**
- [ ] A: Layer-first building always takes longer in absolute engineering hours than a vertical slice
- [x] B: There is no working system to react to until all layers are "done," so judgment about what actually matters — which only comes from watching a real user hit a real gap — has nothing to inform it until far too late
- [ ] C: Generic layers are inherently more bug-prone than layers built for one specific use case
- [ ] D: Customers refuse to review any architecture that isn't built as a vertical slice

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific claim is about the source of judgment, not raw speed or bug rates — a working system generates real feedback a purely anticipated one cannot.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [layer-first-risk, feedback-timing]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Distinguishing a cheap seam from speculative generality
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's framework, why does an `org_id` column on every table belong in the MVP from day one, while a multi-provider LLM plugin architecture does not?

**OPTIONS:**
- [ ] A: Columns are always cheaper to add than any other kind of code, regardless of timing
- [x] B: The column costs one migration today but retrofitting it after real tenant data exists risks a missed query leaking data across tenants, while the plugin architecture adds real complexity now against a requirement (a second LLM provider) that has never actually been requested
- [ ] C: Plugin architectures are never appropriate for any FDE engagement under any circumstances
- [ ] D: Meridian's product lead explicitly forbade building the plugin architecture in the discovery call

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's central distinction stated as a concrete cost comparison: retrofit cost and leak risk justify the seam now, while the plugin adds complexity against a hypothetical, not an evidenced, need.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [seam-vs-generality, org-id-decision]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the "boring" architecture spine is the default
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson recommend as the default architecture spine for a new FDE app, before any evidence suggests otherwise?

**OPTIONS:**
- [x] A: One relational store, one API process, one background worker, with synchronous request handling by default
- [ ] B: A microservices architecture with one service per business capability from the first commit
- [ ] C: An event bus connecting every component, so future consumers can be added without code changes
- [ ] D: A NoSQL document store chosen for its flexibility with an unknown future schema

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's stated default is deliberately unremarkable — one store, one API, one worker, synchronous unless a specific evidenced step requires otherwise.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [architecture-spine, boring-by-default]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What evidences the one async boundary in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE move contract extraction, specifically, off the synchronous request path, while leaving the upload, review-queue listing, and export endpoints synchronous?

**OPTIONS:**
- [ ] A: Extraction is inherently more important than the other endpoints, so it deserves special infrastructure regardless of latency
- [x] B: Extraction was measured to take 30-90 seconds, long enough to time out or feel broken over a synchronous HTTP request, while none of the other endpoints showed any latency problem that would justify the added complexity of an async boundary
- [ ] C: Background workers are always the correct default for every endpoint in a production system
- [ ] D: The upload, listing, and export endpoints do not touch the database, unlike extraction

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The async boundary is justified by a measured figure (30-90 seconds), not a blanket rule — the other endpoints stay synchronous precisely because no evidence justifies the added complexity for them.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [async-boundary, evidenced-latency]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Connecting architecture non-goals to the scoping module
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson connects deferring the multi-provider plugin architecture to which earlier discipline from the discovery-and-scoping module?

**OPTIONS:**
- [ ] A: The four-pass discovery call structure (current-state walkthrough, pain quantification, stakeholder mapping, constraints)
- [x] B: The PRD-lite's non-goals section — stating explicitly what will not be built yet, so a later request can be checked against it, now applied to code structure instead of a written document
- [ ] C: The risk register's requirement that every risk have a named owner
- [ ] D: The certainty-language discipline from status update writing

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson explicitly draws this parallel: architecture generality deferred today is the non-goals discipline applied to code rather than a scoping document.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [non-goals-parallel, architecture-discipline]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Diagnostic step in the practice loop
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does Practice Loop step 3 (counting migrations needed if `org_id` were added after Acme's data already existed, versus added on day one) actually demonstrate?

**OPTIONS:**
- [ ] A: That databases should never be migrated once real customer data exists, under any circumstances
- [x] B: A concrete, countable quantification of the seam-versus-generality distinction, rather than asserting the retrofit cost is high without evidence
- [ ] C: That Acme's data model was designed incorrectly from the start
- [ ] D: How many rows exist in the contracts table at the time of the pilot

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The step exists specifically to make the abstract cost argument concrete and countable, matching the lesson's broader insistence on diagnostic, measurable steps over conceptual reflection.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [migration-cost-diagnostic, seam-quantification]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Extending the scenario to a second tenant
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
When Globex onboards as ClauseReview's second tenant, why does the multi-provider LLM plugin architecture correctly remain deferred, per the Suggested Extension?

**OPTIONS:**
- [ ] A: Because Globex is a smaller company than Acme and has fewer requirements overall
- [x] B: Because Globex still uses the same single LLM provider Acme does — a second tenant existing is not the same evidence as a second LLM provider being an actual requirement
- [ ] C: Because plugin architectures are technically impossible to add once a second tenant exists
- [ ] D: Because Meridian's product lead has permanently withdrawn the original request

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is precise about what counts as evidence: a second tenant is not the same trigger as a second LLM provider requirement — the `org_id` seam pays off with Globex, but the plugin architecture still has no real justification.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [deferred-generality, tenant-vs-provider-requirement]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

Reference: own knowledge (product engineering practice, YAGNI-informed architecture)

---

# LESSON 2

```yaml
lesson_id: fde-application-security-reliability-02-frontend-essentials-for-fdes-react-plus-typescript
lesson_title: "Frontend Essentials for FDEs: React + TypeScript"
lesson_order: 2

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: application-security-reliability
module_name: "7. Application Engineering, Security & Reliability"
module_order: 7

difficulty: Intermediate
estimated_minutes: 65
content_status: Draft

learning_outcomes:
  - "Replace hand-rolled useEffect data fetching with a server-state library (TanStack Query) for an FDE app with tables, filters, and optimistic edits, and explain what class of bug this collapses."
  - "Model a multi-state API result as a TypeScript discriminated union with an exhaustive switch, and explain why this catches a missing UI state at compile time instead of a customer-facing blank screen."
  - "Share a single Zod schema between a form's runtime validation and its TypeScript type, and explain what drift it prevents compared to a hand-maintained interface and a separate validation function."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Frontend Essentials for FDEs: React + TypeScript

## Concepts Covered

The `useEffect`-based data fetching Module 3 taught works fine for a single demo call, but an FDE building a real reviewer-facing app — a table with filters, pagination, and inline edits a reviewer expects to see reflected immediately — will end up hand-rolling loading, error, staleness, request-cancellation, and optimistic-update logic separately in every component that needs server data, if left at that layer. A server-state library such as TanStack Query replaces this with cache-key-based fetching (`useQuery(['contracts', orgId], fetchContracts)`) that deduplicates identical in-flight requests, refetches stale data automatically, and pairs with a `useMutation` hook that handles an optimistic UI update and its rollback on failure as one declarative unit. This is not simply less code for its own sake — it is fewer places where the exact stale-closure class of bug Module 3's `OrderStatus` example demonstrated can be silently reintroduced by the next component that needs server data, which matters more for a single FDE building fast under a demo deadline than it would in a larger codebase with more review bandwidth to catch the same mistake.

TypeScript's real payoff at this layer is not annotation for its own sake — it is using a discriminated union to make every possible state of an API result exhaustively checkable by the compiler, instead of guessed at with a runtime `if (data)`. A clause extraction result is not simply present or absent; it can be `pending`, `succeeded` with typed extracted fields, or `failed` with a typed reason, and modeling this as `type ExtractionResult = { status: 'pending' } | { status: 'succeeded'; clauses: Clause[] } | { status: 'failed'; reason: string }` means a `switch` on `.status` that omits one case is a compile error the FDE catches while building, not a blank screen a reviewer hits during a customer demo. The second FDE-specific payoff is sharing one schema between the form that submits data and the type describing what the API expects: a library like Zod defines a runtime-validated schema once (`z.object({ clauseType: z.enum([...]), liabilityCapUsd: z.number().positive() })`), and both the form's validation and the TypeScript type (`z.infer<typeof schema>`) derive from that single source, so the two never silently drift the way a hand-maintained interface and a separately written validation function eventually do once either one is edited without the other.

```tsx
type ExtractionResult =
  | { status: 'pending' }
  | { status: 'succeeded'; clauses: Clause[] }
  | { status: 'failed'; reason: string };

function ClauseCell({ result }: { result: ExtractionResult }) {
  switch (result.status) {
    case 'pending':
      return <Spinner />;
    case 'succeeded':
      return <ClauseList clauses={result.clauses} />;
    case 'failed':
      return <ErrorBadge reason={result.reason} />;
    // omitting a case here is a compile error, not a silent blank render
  }
}
```

The component-architecture question specific to an FDE, as opposed to a product team building the same table over months, is how much custom UI to build under a deadline measured in days. Reaching for a pre-built component library for the table, form inputs, and modal primitives (rather than hand-rolling a data grid or a date picker from scratch) is almost always the right call for a first pilot, because the reviewer's actual requirement is a correct, usable queue, not a bespoke visual identity — the custom design work belongs later, only once the underlying interaction (filter, sort, inline-edit, approve) has already been validated against a real reviewer's workflow. This is the same seam-versus-generality judgment the architecture lesson applied to the backend, now applied to frontend build time: a component library is a cheap, reversible choice that unblocks the vertical slice immediately, while a custom design system is exactly the kind of generality that pays off only once a second, third, and fourth screen genuinely need to share a consistent, hand-built visual language — a requirement a one-screen pilot review queue does not yet have.

## Practical Backend Scenario

The FDE is building ClauseReview's reviewer queue: a table of contracts and their extracted clauses, where each cell must render exactly one of three extraction states, and where a reviewer editing a clause's `liabilityCapUsd` value inline expects the row to update immediately, not after a page refresh. The queue is built with `useQuery(['clauses', orgId, contractId], fetchClauses)` so switching between contracts reuses cached data instead of re-fetching, and the inline edit uses `useMutation` with an optimistic update — the row shows the new value the instant the reviewer submits it, and rolls back to the previous value automatically if the PATCH request fails. `ExtractionResult` is modeled as the three-state discriminated union above; when a teammate later adds a fourth state, `needs_review` (for extractions that failed a grounding check), the `switch` in `ClauseCell` fails to compile until that case is handled, catching the gap before it ever reaches a reviewer as a blank cell. The edit form and the API's expected shape both derive from one shared Zod schema, so a reviewer typing a negative liability cap is rejected by the same validation logic the backend would also apply, not two independently maintained copies of "what a valid clause looks like" that could quietly disagree.

## Practice Loop

1. Build the review queue with `useQuery`, fetching contracts and clauses scoped by `orgId`, and confirm switching between two contracts reuses cached data instead of issuing a duplicate request for one already fetched.
2. Model `ExtractionResult` as the three-state discriminated union and write an exhaustive `switch` in `ClauseCell`, deliberately omitting the `failed` case first.
3. Attempt to compile with the `failed` case omitted and count exactly how many places the TypeScript compiler flags the missing case — this diagnostic makes the "compile error instead of blank screen" claim concrete rather than asserted.
4. Add the `failed` case back, then wire the inline liability-cap edit with `useMutation`, implementing the optimistic update and confirming it correctly rolls back when you simulate a failed PATCH.
5. Extract a single Zod schema shared by the edit form's validation and the TypeScript type via `z.infer`, and verify a negative liability-cap value is rejected identically whether entered through the form or sent directly to the mutation.

## Evidence of Understanding

You can replace hand-rolled `useEffect` data fetching with a server-state library for a component that needs caching, deduplication, and optimistic updates, and explain what class of race-condition bug this collapses compared to Module 3's approach. You can model a multi-state API result as an exhaustive discriminated union and demonstrate that omitting a case is a compile-time error, not a runtime blank render. You can share one Zod schema between a form's validation and its TypeScript type and explain what drift this prevents compared to maintaining an interface and a validation function separately.

## Suggested Extension

Add pagination or list virtualization to the review queue for a contract with several thousand extracted clauses, and note which of `useQuery`'s built-in caching behavior you get to reuse unchanged versus what genuinely needs new code for the virtualized case.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What a server-state library collapses compared to hand-rolled useEffect fetching
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that a server-state library like TanStack Query is more than just "less code" compared to hand-rolled `useEffect` fetching for an FDE app with many data-driven components?

**OPTIONS:**
- [x] A: It collapses loading, error, staleness, cancellation, and optimistic-update logic into one declarative call, reducing the number of places the same stale-closure class of bug can be reintroduced by each new component
- [ ] B: It removes the need for TypeScript entirely in any component that fetches data
- [ ] C: It eliminates all network requests by caching data permanently regardless of changes on the server
- [ ] D: It is required by React itself for any component that fetches data from an API

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's specific claim is about bug surface area, not raw code volume — fewer hand-written fetch effects means fewer places to reintroduce the exact stale-closure bug Module 3 demonstrated.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [server-state-library, bug-surface-reduction]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What a discriminated union catches at compile time
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does modeling `ExtractionResult` as a discriminated union with an exhaustive `switch` catch that a runtime `if (data)` guess would not?

**OPTIONS:**
- [ ] A: Network timeouts during the actual fetch request
- [x] B: A missing UI case (like forgetting to handle the `failed` state) becomes a compile error the developer catches while building, instead of a blank cell a reviewer discovers live
- [ ] C: Incorrect values returned by the backend API
- [ ] D: Slow database queries on the server extracting the clause data

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's exhaustiveness claim is specifically about UI-state coverage — a missing branch fails to compile rather than silently rendering nothing at runtime.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [discriminated-union, exhaustiveness-check]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why a shared Zod schema prevents drift
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does deriving both the form's validation and the TypeScript type from one Zod schema (via `z.infer`) prevent a problem that a hand-maintained interface plus a separate validation function does not?

**OPTIONS:**
- [ ] A: Zod schemas run faster at runtime than hand-written validation functions
- [x] B: A single source of truth means the form's validation and the type can never silently disagree, unlike two independently maintained artifacts that can drift apart when one is edited without the other
- [ ] C: TypeScript cannot infer types from any source other than a Zod schema
- [ ] D: Zod schemas are required by the backend framework to accept any request

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The drift the lesson describes happens specifically when two hand-maintained artifacts are edited independently — deriving both from one schema removes that possibility structurally.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [shared-schema, drift-prevention]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** How the optimistic update behaves on failure
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, what happens when a reviewer edits a clause's `liabilityCapUsd` value and the resulting PATCH request fails?

**OPTIONS:**
- [ ] A: The row silently keeps displaying the new value even though the change was never saved
- [x] B: The optimistic update, which showed the new value immediately, rolls back automatically to the previous value once the mutation reports failure
- [ ] C: The entire review queue becomes unresponsive until the page is manually refreshed
- [ ] D: The extraction status for the clause is permanently set to `failed`

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the specific behavior the `useMutation` optimistic-update pattern provides: an immediate UI update paired with an automatic rollback if the underlying request does not succeed.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [optimistic-update, rollback-on-failure]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What happens when a fourth extraction state is added
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, a teammate later adds a fourth state, `needs_review`, to `ExtractionResult`. What is the concrete effect on `ClauseCell`'s existing `switch` statement?

**OPTIONS:**
- [ ] A: The switch continues to compile and silently renders nothing for the new state until someone notices in production
- [x] B: The switch fails to compile until the new `needs_review` case is explicitly handled, catching the gap before it reaches a reviewer
- [ ] C: React automatically generates a default UI for any unhandled discriminated union case
- [ ] D: The application crashes at runtime the first time a `needs_review` result is fetched, with no compile-time warning
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the exhaustiveness guarantee made concrete: adding a new union member surfaces every switch that needs updating as a compile error, not a silent runtime gap.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [exhaustiveness-guarantee, added-union-member]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What useQuery's cache key achieves when switching contracts
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does `useQuery(['clauses', orgId, contractId], fetchClauses)` avoid re-fetching when a reviewer switches back to a contract they viewed a moment ago?

**OPTIONS:**
- [ ] A: TanStack Query permanently disables re-fetching after the very first request for any query key
- [x] B: The cache key (`orgId`, `contractId`) lets already-fetched data for that exact key be reused directly from cache instead of triggering a duplicate request
- [ ] C: The browser's own HTTP cache is solely responsible for this behavior, unrelated to the query key
- [ ] D: Switching contracts never actually changes which data needs to be displayed
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The cache key is what makes deduplication and reuse possible — identical keys reuse cached data, distinct keys trigger a fresh fetch.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [cache-key, request-deduplication]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the shared schema also protects the mutation path, not just the form
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why does a reviewer entering a negative liability cap get rejected the same way whether they use the edit form or a request is sent directly to the mutation?

**OPTIONS:**
- [ ] A: React automatically blocks all negative numeric inputs across every form by default
- [x] B: Both the form's validation and the mutation's expected type derive from the same Zod schema, so the same validation rule applies regardless of entry point instead of living in two independently maintained places
- [ ] C: Negative numbers are rejected by the browser before any JavaScript runs
- [ ] D: The backend API silently converts negative values to zero rather than rejecting them
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the practical payoff of a single shared schema — one rule enforced consistently, rather than two separately maintained checks that could disagree.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [shared-schema-consistency, validation-entry-points]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What genuinely needs new code when adding virtualization
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, when adding pagination or list virtualization for a contract with thousands of extracted clauses, what does the lesson imply is reused unchanged versus what needs genuinely new code?

**OPTIONS:**
- [x] A: `useQuery`'s caching, deduplication, and staleness behavior is reused as-is; the genuinely new work is rendering only the visible subset of rows and requesting data in pages rather than all at once
- [ ] B: Every part of the existing data-fetching layer must be rewritten from scratch for virtualization to work at all
- [ ] C: TypeScript's discriminated union types stop functioning correctly once virtualization is introduced
- [ ] D: Virtualization eliminates the need for a cache key entirely, since only visible rows are ever fetched
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The question tests whether the learner understands the actual scope of the change — the caching layer's behavior does not need to change, only how much and which data is requested and rendered at once.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [virtualization-scope, reuse-vs-new-work]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

Reference: own knowledge (TanStack Query and Zod documentation patterns, TypeScript discriminated unions)

---

# LESSON 3

```yaml
lesson_id: fde-application-security-reliability-03-multi-tenant-design-and-background-workflows-postgres-rls-celery
lesson_title: "Multi-Tenant Design & Background Workflows (Postgres RLS, Celery)"
lesson_order: 3

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: application-security-reliability
module_name: "7. Application Engineering, Security & Reliability"
module_order: 7

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Enforce tenant isolation at the database layer with Postgres row-level security policies and per-transaction SET LOCAL session context, and explain why this closes a class of leak that WHERE-clause filtering alone does not."
  - "Design a background worker pool that explicitly re-establishes tenant context per job and routes work so one tenant's stuck retries cannot starve another tenant's queue."
  - "Scope an idempotency key by tenant, not just by event ID, and explain the specific collision risk that leaves open."

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
# Multi-Tenant Design & Background Workflows (Postgres RLS, Celery)

## Concepts Covered

Postgres row-level security (RLS) enforces tenant isolation at the database layer instead of relying on every query to remember a `WHERE org_id = ...` clause. Enabling RLS on a table (`ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;`) and attaching a policy (`CREATE POLICY tenant_isolation ON contracts USING (org_id = current_setting('app.current_org_id')::uuid);`) means the database itself refuses to return rows outside the session's current tenant, regardless of what a given query looks like — a raw debugging query run directly against production, a background job, or a future engineer's new endpoint all inherit the same enforcement without having to remember it. The application sets that session variable per transaction with `SET LOCAL app.current_org_id = '...'`, not the connection-wide `SET`, because `SET LOCAL` scopes the value to the current transaction and automatically clears it when the transaction ends — critical on a pooled connection, where the same physical connection is reused across requests for different tenants, and a connection-wide `SET` would leave the previous tenant's context leaking into the next request that happens to reuse that connection. A separate, narrowly-scoped role with the `BYPASSRLS` attribute is reserved for genuine cross-tenant operations like migrations or admin tooling — the application's own runtime role should never carry it, or the entire point of database-layer enforcement is undone by a single misconfigured connection.

The genuinely new territory beyond what a single-tenant Celery setup already covers is what changes when many tenants share the same background worker pool. First, a worker that pulls a batch of pending jobs across tenants must explicitly re-set the session's tenant context at the start of each individual job, not once at worker startup — a defect class specific to connection pooling is a worker that processes job N for tenant A, then job N+1 for tenant B on a reused connection, without re-issuing `SET LOCAL` for the new job's tenant, silently running tenant B's queries under tenant A's now-stale session context. Second, a single shared FIFO queue creates a noisy-neighbor risk: one tenant's malformed input triggering repeated retries can occupy worker capacity and queue position that starves every other tenant's legitimate, quick-to-process jobs behind it, which is why per-tenant queue routing or fair-share worker allocation — not a single global queue — is the correct default once more than one tenant shares infrastructure. Third, an idempotency key built only from an event ID (as the single-tenant webhook-handling pattern used) is insufficient once multiple tenants' independent systems can plausibly generate the same raw identifier — an idempotency key must be scoped as `(org_id, event_id)`, or one tenant's job can silently collide with, and be dropped or overwritten by, another's.

Two verification habits catch the gaps the design itself doesn't automatically prevent. Postgres exempts a table's owner from its own RLS policies by default — a connection running as the table owner (often the same role migrations run as) sees every tenant's rows regardless of any policy, unless the table is explicitly altered with `FORCE ROW LEVEL SECURITY`, so an FDE who tests isolation only as a non-owner application role can ship a policy that looks correct in every test and still leaks the moment the application accidentally connects as the owning role. The second habit is testing RLS the same way a security boundary, not a convenience feature, is tested: connect explicitly as tenant A's context and assert tenant B's rows are genuinely absent from the result set, not merely unindexed or slow to reach — an integration test that only checks "tenant A's own data is present and correct" can pass while a leak of tenant B's data alongside it goes completely unnoticed, because nobody asserted the negative case at all.

## Practical Backend Scenario

Once Globex onboards as ClauseReview's second tenant, a stress test surfaces a real defect: Globex uploads a malformed PDF that puts its extraction worker into a retry loop, and because all tenants' extraction jobs share a single Celery queue, Acme Corp's uploads — simple, well-formed, one-page contracts that should extract in seconds — end up queued behind Globex's stuck retries for over 40 minutes. Separately, a code review catches a second defect before it reaches production: the worker that pulls a batch of pending extraction jobs sets `app.current_org_id` once when the worker process starts, not per job, meaning a worker that happens to process a Globex job immediately after an Acme job would silently query Acme's contracts table under Globex's tenant context if the connection were reused without re-issuing `SET LOCAL`. The fix addresses both: each job explicitly re-sets its own tenant context via `SET LOCAL` inside its own transaction before touching any RLS-protected table, and Celery task routing sends each tenant's jobs to a tenant-specific queue (`extraction.acme`, `extraction.globex`) so one tenant's stuck retries can no longer occupy capacity that would otherwise serve another tenant's quick jobs.

## Practice Loop

1. Write the RLS policy and the `SET LOCAL app.current_org_id` pattern for the `contracts` table, and explain in one sentence why `SET LOCAL` inside a transaction is required instead of a connection-wide `SET` on a pooled connection.
2. Write a Celery task that pulls a batch of pending extraction jobs spanning multiple tenants, and explicitly re-issue `SET LOCAL` for each job's own `org_id` before that job's queries run, rather than setting it once when the worker starts.
3. Reproduce the noisy-neighbor scenario with a single shared queue: force one tenant's job into repeated retries and measure how long a second tenant's simple, well-formed job waits behind it — this diagnostic quantifies the starvation risk rather than asserting it.
4. Add per-tenant Celery queue routing and re-run the same measurement, confirming the second tenant's job no longer waits behind the first tenant's stuck retries.
5. Design the `(org_id, event_id)` idempotency key and write a test proving that two different tenants independently submitting the same raw `upload_id` do not collide or overwrite each other's job record.

## Evidence of Understanding

You can write a Postgres RLS policy and the `SET LOCAL` session-context pattern that enforces tenant isolation at the database layer, and explain why this closes a class of leak that relying on every query's `WHERE` clause does not. You can identify and fix the pooled-connection defect where a background worker fails to re-establish tenant context per job, and you can design per-tenant queue routing that prevents one tenant's stuck retries from starving another tenant's jobs. You can scope an idempotency key by tenant and explain the specific cross-tenant collision it prevents that an event-ID-only key leaves open.

## Suggested Extension

Add a third tenant with unusually high upload volume, and design a fairness policy — a maximum number of concurrently running jobs per tenant, even within that tenant's own dedicated queue — that goes beyond simple per-tenant queue routing to prevent one large tenant from monopolizing overall worker capacity.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why RLS closes a class of leak that WHERE-clause filtering doesn't
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that Postgres RLS enforcement closes a class of data leak that application-level `WHERE org_id = ...` filtering does not?

**OPTIONS:**
- [x] A: RLS makes the database itself refuse to return out-of-tenant rows regardless of what a given query looks like, so a missed WHERE clause in a new endpoint, a raw debugging query, or a background job all inherit the same enforcement automatically
- [ ] B: WHERE-clause filtering is slower to execute than RLS policies at query time
- [ ] C: RLS eliminates the need for a tenant identifier column on any table entirely
- [ ] D: WHERE-clause filtering only works for SELECT statements, never for INSERT or UPDATE

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's core claim is about enforcement location — a WHERE clause is remembered per call site, while an RLS policy is enforced once, at the database, regardless of the calling code.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [rls-enforcement, where-clause-risk]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why SET LOCAL, not SET, on a pooled connection
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why must the tenant context be set with `SET LOCAL app.current_org_id = ...` inside a transaction, rather than a connection-wide `SET`, on a pooled database connection?

**OPTIONS:**
- [ ] A: `SET LOCAL` executes faster than `SET` regardless of connection pooling
- [x] B: `SET LOCAL` scopes the value to the current transaction and clears automatically when it ends, while a connection-wide `SET` would leave a previous tenant's context leaking into the next request that reuses the same pooled connection
- [ ] C: `SET` is not valid syntax for session variables in Postgres under any circumstances
- [ ] D: `SET LOCAL` is required by Celery specifically, but not by any other background job framework

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The specific risk is connection reuse across tenants — `SET LOCAL`'s transaction scoping is exactly what prevents one tenant's session context from bleeding into the next request on the same physical connection.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [set-local, pooled-connection-leak]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why BYPASSRLS belongs on a separate, narrow role
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist the `BYPASSRLS` attribute be reserved for a separate, narrowly-scoped role, never the application's own runtime role?

**OPTIONS:**
- [ ] A: `BYPASSRLS` is a deprecated Postgres feature no longer supported in current versions
- [x] B: Granting `BYPASSRLS` to the application's runtime role undoes the entire point of database-layer enforcement — any connection using that role could return cross-tenant data regardless of the policy
- [ ] C: `BYPASSRLS` only affects INSERT statements, so it is irrelevant to read-path tenant isolation
- [ ] D: Postgres requires every migration tool to use a role with `BYPASSRLS`, making it unavoidable in practice

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson frames this as a single point of failure — one misconfigured connection carrying `BYPASSRLS` defeats database-layer enforcement entirely, which is why it must stay isolated to genuine admin/migration use.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [bypassrls, role-scoping]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** The per-job session-context defect
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific defect does the lesson describe when a worker sets `app.current_org_id` once at worker startup rather than per job?

**OPTIONS:**
- [ ] A: The worker crashes immediately on startup and cannot process any jobs
- [x] B: If the connection is reused across jobs for different tenants without re-issuing `SET LOCAL`, a job for one tenant can silently run its queries under a previous job's stale tenant context
- [ ] C: Extraction jobs run correctly, but noticeably slower than if the context were set per job
- [ ] D: RLS policies stop being enforced entirely once a worker process has been running for more than one job

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the exact pooled-connection defect class the lesson names — stale session context from a previous job silently applies to the next job's queries if not explicitly re-set.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [stale-session-context, per-job-reset]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why a single shared FIFO queue creates noisy-neighbor risk
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend per-tenant queue routing over a single shared FIFO queue for a multi-tenant background worker pool?

**OPTIONS:**
- [ ] A: A single shared queue is technically incapable of processing more than one job at a time
- [x] B: One tenant's malformed input triggering repeated retries can occupy worker capacity and queue position, starving every other tenant's quick, legitimate jobs behind it
- [ ] C: Celery does not support a single shared queue under any configuration
- [ ] D: Per-tenant queues eliminate the need for idempotency keys entirely
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The noisy-neighbor risk is specifically about shared capacity and ordering — a stuck tenant's retries occupy the queue position and worker time that unrelated tenants' quick jobs would otherwise use.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [noisy-neighbor, shared-queue-risk]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the idempotency key must include org_id
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why is an idempotency key built only from an event ID insufficient in a multi-tenant background job system?

**OPTIONS:**
- [ ] A: Event IDs are always too short to be useful as a database key
- [x] B: Two different tenants' independent systems can plausibly generate the same raw identifier, so an event-ID-only key risks one tenant's job silently colliding with, and being dropped or overwritten by, another tenant's job
- [ ] C: Idempotency keys are unnecessary once RLS is correctly enforced
- [ ] D: Event IDs change every time a job is retried, making them unusable for idempotency in any system
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The specific risk is a cross-tenant identifier collision, which is exactly why the key must be scoped `(org_id, event_id)` rather than the event ID alone.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [idempotency-key-scoping, cross-tenant-collision]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why Acme's uploads queued behind Globex's stuck retries
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why did Acme's simple, well-formed uploads end up waiting 40 minutes behind Globex's malformed PDF?

**OPTIONS:**
- [ ] A: Acme's own contracts were themselves malformed in a similar way
- [x] B: Both tenants' extraction jobs shared a single Celery queue, so Globex's job retrying repeatedly occupied queue position and worker capacity that Acme's quick jobs needed, with no per-tenant isolation to prevent it
- [ ] C: RLS policies blocked Acme's jobs from running until Globex's issue was resolved
- [ ] D: Acme's worker process had crashed independently of Globex's issue
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the noisy-neighbor mechanism made concrete — shared queue capacity, not any per-tenant technical block, is what caused Acme's unrelated jobs to wait.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scenario-noisy-neighbor, shared-queue-starvation]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What the code review caught before production
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific defect did the code review catch in the scenario, separate from the noisy-neighbor issue?

**OPTIONS:**
- [ ] A: The worker was missing an RLS policy on the `contracts` table entirely
- [x] B: The worker set `app.current_org_id` once at process startup instead of per job, meaning a Globex job processed right after an Acme job on a reused connection could silently query Acme's data under Globex's tenant context if `SET LOCAL` weren't re-issued
- [ ] C: The Celery queue name was misspelled in the routing configuration
- [ ] D: The idempotency key was missing the event ID component entirely
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the per-job session-context defect from Concepts Covered, made concrete in the scenario as a real code-review catch rather than a hypothetical.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scenario-session-context-fix, code-review-catch]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Fairness beyond simple per-tenant queues
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, why might per-tenant queue routing alone still be insufficient once a third, unusually high-volume tenant joins?

**OPTIONS:**
- [ ] A: Per-tenant queues stop working correctly once more than two tenants exist
- [x] B: A single large tenant's own dedicated queue could still monopolize overall worker capacity across the pool, so a per-tenant concurrency limit is needed on top of queue routing to keep that tenant's volume from crowding out others
- [ ] C: Per-tenant queues are only compatible with exactly two tenants by design
- [ ] D: Idempotency keys need to be redesigned for a third tenant to function
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Per-tenant queues solve isolation of ordering, but not overall capacity fairness — a large tenant's own queue can still consume a disproportionate share of shared worker capacity without an added concurrency limit.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [worker-fairness, concurrency-limit]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: PostgreSQL documentation — Row Security Policies (CREATE POLICY, current_setting, SET LOCAL)

---

# LESSON 4

```yaml
lesson_id: fde-application-security-reliability-04-document-processing-and-ai-extraction-workflows
lesson_title: "Document Processing & AI Extraction Workflows"
lesson_order: 4

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: application-security-reliability
module_name: "7. Application Engineering, Security & Reliability"
module_order: 7

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Design an AI extraction pipeline's output as a fixed, structured schema with a required evidence citation per field, rather than freeform generation."
  - "Implement a grounding check that verifies an extracted field's evidence quote is a literal match in the source document text, and route non-matches to mandatory human review instead of auto-approving them."
  - "Distinguish OCR error, LLM hallucination, and schema drift as distinct failure modes in a document-extraction pipeline, each requiring a different mitigation."

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
# Document Processing & AI Extraction Workflows

## Concepts Covered

A document-processing pipeline turns an uploaded file into structured, verifiable data through a fixed sequence: text and layout extraction (distinguishing a text-native PDF, where character data is embedded directly, from a scanned or faxed image PDF, which requires OCR to produce any text at all), chunking that preserves each piece of text's page and, ideally, bounding-box provenance, an LLM extraction step producing structured output against a fixed schema, and a validation and confidence step before any extracted value reaches a human reviewer or a downstream system. The critical difference from a freeform chat interaction is that extraction output is not judged on being generally helpful — it is judged on precision and recall against a known, fixed set of fields (clause type, obligation text, liability cap, renewal date, governing law), and every value the LLM returns needs a traceable citation back to the specific page and passage it came from, because a reviewer's job is to verify a claim against the source, not to trust a claim on its own authority.

Three failure modes are specific to this kind of pipeline and each needs a distinct mitigation, not one generic "add more prompt instructions" response. Silent hallucination — the model returning a plausible-looking value that is not actually present in the source document — is mitigated by requiring a structured `evidence_quote` field alongside every extracted value, and by a grounding check that rejects any extraction whose quote does not appear as a literal (or near-literal, fuzzy-matched) substring of the OCR'd source page text; a value with no matching quote in the source is treated as unverified, not as a slightly-wrong-but-usable answer. OCR error — a scanned or faxed page producing garbled or misread characters — is mitigated by routing pages below a confidence threshold to a mandatory human-first review lane rather than letting a low-confidence extraction quietly enter the same pipeline as a high-confidence one; degrading silently is worse than being visibly slower for that page. Schema drift — the extraction prompt returning a shape the downstream review UI or export doesn't expect — is mitigated by validating the LLM's structured output against the same shared schema the frontend and API already use, so a malformed extraction fails loudly on the server the moment it's produced, instead of reaching the frontend as an unexpected shape that crashes a component built for a rigid contract.

```json
{
  "field": "liabilityCapUsd",
  "value": 50000,
  "evidence_quote": "the Vendor's aggregate liability shall not exceed fifty thousand dollars ($50,000)",
  "source_page": 23,
  "confidence": 0.94
}
```

Chunking strategy deserves its own care beyond "split the text into pieces," because a contract's structure carries meaning a naive fixed-size character split destroys. Splitting strictly by page preserves the citation granularity the grounding check depends on, but a clause that legitimately spans a page break gets cut in half, with the extraction seeing only whichever half falls in its chunk; splitting by detected section or clause boundary (using the document's own headings and numbering, when present) usually preserves a full clause intact, but requires a reliable layout-detection step upstream that a purely OCR-based pipeline may not have. Contracts also frequently carry tabular data — a payment schedule, a table of covered products — that a plain-text chunking strategy flattens into a single run-on line, destroying the row/column relationships an extraction prompt needs to read a table correctly; a pipeline that ignores this and chunks tables the same way it chunks prose paragraphs will reliably misread which value belongs to which row once a table has more than two or three columns. The practical answer is not to solve every layout edge case up front, but to know exactly which layout situations the current chunking strategy handles correctly and which it doesn't, and to route the ones it doesn't handle to the same human-first review lane OCR failures already use, rather than letting a known blind spot silently produce a confidently wrong extraction.

## Practical Backend Scenario

Extracting a liability-cap clause from one of Acme's 40-page vendor contracts — a scanned, fax-era document — the OCR output for page 23, where the clause lives, is noisy: a digit is misread, turning "$50,000" into text the OCR engine renders ambiguously. The LLM extraction step, working from that noisy OCR text, confidently returns a `liabilityCapUsd` value of `500000` with an `evidence_quote` claiming the source says "$500,000." The grounding check runs the literal-match comparison against page 23's actual OCR'd text and finds no substring matching "$500,000" anywhere on that page — only the ambiguous, digit-garbled original — so the extraction is flagged as ungrounded rather than auto-approved. Instead of silently entering Acme's review queue as a high-confidence value a reviewer might rubber-stamp, the flagged extraction routes to a mandatory human review lane with the low-confidence OCR page and the original scanned image attached side by side, so the reviewer can resolve the ambiguity by looking directly at the scan rather than trusting either the OCR text or the LLM's confident-but-wrong reading of it.

## Practice Loop

1. Write the extraction prompt with a structured JSON schema output, requiring an `evidence_quote`, `source_page`, and `confidence` field alongside every extracted value.
2. Implement the grounding check: verify that each `evidence_quote` appears as a literal substring of the corresponding OCR'd page text, flagging any extraction where it does not.
3. Run the extraction pipeline against ten scanned pages with varying OCR quality and count how many extractions fail the grounding check versus pass automatically — this diagnostic reveals the actual OCR error rate this pipeline must be designed around, rather than assuming a rate.
4. Route every grounding-check failure to a mandatory human review lane distinct from passing extractions, which can auto-populate the review queue without requiring a human look first.
5. Review a sample of the grounding-check failures from step 3 and confirm each one traces back to a real OCR or hallucination issue rather than an overly strict literal-match check producing a false positive, adjusting the match tolerance (for example, allowing minor whitespace or punctuation differences) if it is rejecting genuinely correct extractions.

## Evidence of Understanding

You can design an extraction pipeline's output as a fixed, structured schema requiring an evidence citation per field, rather than freeform generation a reviewer has no way to verify. You can implement a grounding check that rejects an extraction whose evidence quote doesn't literally match the source page, and explain why an ungrounded extraction should route to mandatory human review rather than being auto-approved at a lower confidence tier. You can distinguish OCR error, LLM hallucination, and schema drift as separate failure modes, each with its own specific mitigation, rather than treating pipeline failures as one undifferentiated category.

## Suggested Extension

Add a second failure mode to the scenario — a liability clause that spans pages 23 and 24 rather than sitting entirely on one page — and describe how the `evidence_quote`/`source_page` citation design needs to extend to reference a page range instead of a single page number for the grounding check to still work correctly.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why extraction pipelines are judged differently from freeform chat
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson say a document-extraction pipeline's output should be judged, in contrast to a freeform chat response?

**OPTIONS:**
- [x] A: On precision and recall against a known, fixed set of fields, with every value carrying a traceable citation back to the source, rather than on being generally helpful
- [ ] B: On response speed alone, since accuracy is assumed to be equivalent across both use cases
- [ ] C: On the total length of the generated response, since longer answers are considered more thorough
- [ ] D: Extraction pipelines and freeform chat should be judged by identical standards with no meaningful difference

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's central distinction is that extraction targets a fixed, known field set that can be precisely checked, unlike open-ended chat, and every value must be independently verifiable via citation.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [extraction-vs-chat, precision-recall]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What the grounding check actually verifies
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the grounding check specifically verify about an extracted field's `evidence_quote`?

**OPTIONS:**
- [ ] A: That the quote is grammatically correct English
- [x] B: That the quote appears as a literal (or near-literal) substring of the actual OCR'd source page text, not merely that the extracted value seems plausible
- [ ] C: That the quote is shorter than a fixed maximum character length
- [ ] D: That the quote matches a pre-written list of expected clause phrases

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The grounding check's entire purpose is checking the claimed evidence against the actual source text, which is what catches a hallucinated value that has no real basis in the document.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [grounding-check, literal-match]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Distinguishing OCR error from hallucination as failure modes
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist OCR error and LLM hallucination need distinct mitigations rather than one generic response?

**OPTIONS:**
- [ ] A: OCR error and hallucination are actually the same underlying problem described with two different names
- [x] B: OCR error is mitigated by routing low-confidence pages to human-first review before extraction even runs, while hallucination is mitigated by a grounding check on the extraction's own output — treating them as one problem would leave one of the two failure modes unaddressed
- [ ] C: OCR error only affects scanned documents, so it can be ignored entirely for any text-native PDF pipeline
- [ ] D: Hallucination cannot occur in an extraction pipeline that uses structured JSON output

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Each failure mode has a distinct point of intervention — OCR confidence gating happens before extraction, while grounding checks happen after — so conflating them into one fix leaves a gap.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [ocr-vs-hallucination, distinct-mitigations]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why schema drift is mitigated server-side
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson validate the LLM's extraction output against the shared schema on the server, rather than letting a malformed extraction reach the review-queue frontend?

**OPTIONS:**
- [ ] A: Server-side validation is always faster to execute than client-side validation
- [x] B: A malformed extraction should fail loudly at the point it's produced instead of reaching the frontend as an unexpected shape that crashes a component built for a rigid, fixed contract
- [ ] C: The frontend has no ability to display any error state under any circumstances
- [ ] D: Schema validation is only possible on a server, never in a browser

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's point is about where a failure surfaces, not raw execution speed — catching a shape mismatch server-side prevents it from becoming a frontend crash discovered live.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [schema-drift, server-side-validation]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the scenario's extraction was flagged, not auto-approved
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why was the `$500,000` liability-cap extraction flagged as ungrounded instead of entering Acme's review queue as a high-confidence value?

**OPTIONS:**
- [ ] A: The LLM itself reported low confidence in the value, which triggered the flag automatically
- [x] B: The grounding check found no literal match for "$500,000" anywhere on page 23's actual OCR'd text, since the real source text was digit-garbled and did not contain that exact figure
- [ ] C: Acme's contract review policy requires every liability-cap value to be manually flagged regardless of extraction quality
- [ ] D: The extraction pipeline does not support dollar-figure fields at all

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scenario is a direct illustration of the grounding check working as designed — the claimed value had no literal basis in the actual source text, so it was rejected rather than trusted.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scenario-grounding-failure, ocr-digit-error]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What the reviewer sees for a flagged extraction
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the scenario's flagged extraction actually route to, and what does the reviewer receive to resolve it?

**OPTIONS:**
- [ ] A: The extraction is silently discarded with no notification to any reviewer
- [x] B: It routes to a mandatory human review lane, with the low-confidence OCR page and the original scanned image attached, so the reviewer can resolve the ambiguity by looking directly at the scan
- [ ] C: The system automatically substitutes a default liability-cap value of zero
- [ ] D: The extraction is re-run automatically with a different LLM model until it passes the grounding check

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The design specifically gives the reviewer the source material (OCR text and the actual scan) rather than asking them to trust the pipeline's own uncertain output.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [human-review-routing, scenario-resolution]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Purpose of the diagnostic step counting grounding-check pass/fail
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does Practice Loop step 3 — counting how many of ten scanned pages fail versus pass the grounding check — actually establish?

**OPTIONS:**
- [ ] A: Whether the extraction prompt is syntactically valid JSON
- [x] B: The pipeline's actual OCR error rate against real scanned pages, which the pipeline's design needs to be built around, rather than an assumed or guessed rate
- [ ] C: Whether the ten pages belong to the same tenant or different tenants
- [ ] D: The total dollar value of all liability caps extracted across the ten pages
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is a diagnostic step in the lesson's established pattern: it converts an assumed error rate into a measured one, which is what actually informs whether the human-review lane's capacity is sized correctly.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [ocr-error-rate-diagnostic, measured-vs-assumed]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why step 5 checks for false positives in the grounding check
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does Practice Loop step 5 ask the learner to confirm grounding-check failures are real issues, not false positives from an overly strict literal-match check?

**OPTIONS:**
- [x] A: A grounding check that is too strict (rejecting minor whitespace or punctuation differences as non-matches) would route genuinely correct extractions into human review unnecessarily, undermining the pipeline's usefulness even though it is technically safe
- [ ] B: False positives are impossible once a grounding check has been implemented correctly
- [ ] C: This step exists only to satisfy a compliance requirement unrelated to the pipeline's actual accuracy
- [ ] D: The grounding check cannot produce false positives, only false negatives
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
An overly strict match tolerance trades one failure mode (missed hallucinations) for another (unnecessary human review load on correct extractions) — step 5 exists to catch that trade-off going too far in the strict direction.

**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [false-positive-check, match-tolerance-tuning]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Extending citation design to a multi-page clause
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, what needs to change about the `evidence_quote`/`source_page` design for a liability clause that spans pages 23 and 24?

**OPTIONS:**
- [ ] A: Nothing — the existing single-page citation design already handles multi-page clauses correctly
- [x] B: The citation needs to reference a page range rather than a single page number, since the grounding check's literal-match comparison must now search across both pages' OCR'd text instead of just one
- [ ] C: Multi-page clauses should be excluded from extraction entirely, since they cannot be verified
- [ ] D: The evidence_quote field should be removed entirely for any clause spanning more than one page
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The single-page assumption baked into the original design breaks for a clause split across pages — the citation and the grounding check both need to extend to a page range for the same verification logic to still hold.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [multi-page-citation, grounding-check-extension]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: own knowledge (retrieval-augmented extraction and document-grounding patterns for structured LLM output)

---

# LESSON 5

```yaml
lesson_id: fde-application-security-reliability-05-build-enterprise-document-review-app
lesson_title: "Build: Enterprise Document Review App"
lesson_order: 5

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: application-security-reliability
module_name: "7. Application Engineering, Security & Reliability"
module_order: 7

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Wire an upload API, a tenant-routed background extraction worker, and a polling React review queue into one coherent, end-to-end multi-tenant document review app."
  - "Apply the RLS session-context pattern consistently across every process boundary a single request's lifecycle crosses — the API handler, the background worker, and the export endpoint — and explain why a gap at just one of the three is a real leak."
  - "Sequence a build using a throwaway extraction stub to unblock frontend work in parallel, while keeping the tenant-isolation seam from lesson 1's architecture decision in place from the very first migration."

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
# Build: Enterprise Document Review App

## Concepts Covered

Wiring ClauseReview's four pieces together — upload, extraction, review, export — surfaces an integration decision none of the individual pieces reveal on their own. The upload API creates a `contracts` row scoped by `org_id` and hands the file to storage; a Celery worker, routed to that tenant's own queue, picks up the extraction job, runs OCR and grounded LLM extraction, and writes clause rows tagged `pending`, `succeeded`, or `failed-grounding`; the React review queue fetches and displays those rows with `useQuery`, refetching on a fixed interval rather than over a live socket connection, since polling every five seconds is boring, correct, and entirely sufficient at pilot scale — a direct continuation of the architecture-spine lesson's "default to boring" argument, now applied to a real choice instead of an abstract one; and an approved clause exports to Acme's legal-ops system through a documented endpoint. The concrete wrinkle only visible once these pieces are wired together is that a single contract's lifecycle spans three separate processes — the API request that creates it, the background worker that extracts from it, and the API request that later exports it — and the RLS session-context pattern from the multi-tenant lesson has to be applied consistently at all three entry points, not just the one that happens to get built or tested first. A defect where two of the three correctly set `app.current_org_id` and the third silently doesn't is exactly the kind of gap that produces no visible symptom until a second tenant's data exists for it to leak into.

Sequencing the build itself is where the architecture lesson's seam-versus-generality distinction gets used for real, not just argued abstractly. The correct build order is: first, the upload endpoint and its RLS-scoped `contracts` row, since the tenant-isolation seam is cheap now and expensive to retrofit, exactly as lesson 1 argued; second, a hardcoded extraction stub that returns a fixed set of canned clauses instead of running any real OCR or LLM call, specifically to unblock the review-queue frontend from being built and tested against realistic-shaped data without waiting on the real extraction pipeline to exist yet; third, the real grounded extraction pipeline from the document-processing lesson, swapped in once the review queue already renders real data correctly and can absorb the swap without also being built from scratch at the same time; and only after that, once Globex actually onboards as a second tenant, per-tenant queue routing — not before, because building queue routing against a single tenant has nothing real to validate it against. The stub is deliberately throwaway and cheap to discard; the `org_id` column and RLS policy are kept from the very first migration, because retrofitting either after real tenant data exists is the expensive mistake this sequencing is specifically designed to avoid.

The failure case worth designing for explicitly, not discovering by accident, is a contract that gets uploaded successfully but whose extraction job never completes — a worker crash mid-task, a queue message lost during a deploy, or a job that silently exceeds its timeout. Without an explicit answer, a `contracts` row sits forever in `pending` with no signal to anyone that anything is wrong, and a reviewer eventually notices only because a contract they expected to review never showed up, at which point diagnosing whether the job failed, is still running, or was never picked up at all requires manually inspecting three different systems. The concrete fix costs little relative to the failure it prevents: a job-level timeout that flips a stuck `pending` row to a distinct `stalled` status after a fixed window, visible in the same review queue as its own state rather than an invisible non-event, and a periodic reconciliation check comparing `contracts` rows against completed Celery task records to catch the rarer case of a job that was queued but never dequeued at all.

## Practical Backend Scenario

Building ClauseReview for Acme's pilot, the FDE ships the upload endpoint and RLS-scoped `contracts` table first, with a hardcoded extraction stub returning three canned clauses regardless of what was actually uploaded — enough for the review queue's table, inline-edit form, and status rendering to be built and demoed against realistic data while the real extraction pipeline is still in progress. Once the review queue correctly displays and edits the stubbed clauses, the real OCR-and-grounded-extraction pipeline replaces the stub, and the review queue needs no changes, because both produced data in the same shape. A pre-launch review of all three RLS entry points catches a real gap: the upload handler and the export endpoint both correctly issue `SET LOCAL app.current_org_id` per request, but the Celery extraction task — copied from an earlier single-tenant prototype — never had the line added at all, silently relying on RLS being permissive by default rather than explicitly enforced for that one code path. The gap produces no visible symptom with only Acme's data in the system, and is only caught because the review deliberately checks all three entry points against the multi-tenant lesson's checklist rather than assuming the pattern that worked in one place was copied everywhere.

## Practice Loop

1. Build the upload endpoint and RLS-scoped `contracts` table first, along with a hardcoded extraction stub that returns a fixed set of canned clauses regardless of the actual uploaded file.
2. Build the React review queue (table, extraction-status rendering, inline edit) entirely against the stub's canned data, and confirm it renders and edits correctly before any real extraction code exists.
3. Audit all three process boundaries a contract's lifecycle crosses — the upload API handler, the extraction worker, and the export endpoint — and count how many of the three correctly issue `SET LOCAL app.current_org_id`; this diagnostic is what actually catches a gap, not an assumption that a pattern used once was applied everywhere.
4. Swap the real grounded-extraction pipeline in for the stub, and confirm the review queue needs zero changes because the stub and the real pipeline both produce clause data in the identical shape.
5. Measure the true end-to-end latency from a real contract upload to its clauses appearing, reviewable, in the queue, and compare it against the review queue's five-second polling interval to confirm polling is still an acceptable user experience at this stage rather than an assumed one.

## Evidence of Understanding

You can wire an upload API, a background extraction worker, and a polling React review queue into one coherent multi-tenant app, and explain why polling, not a live socket, is the correct default at pilot scale. You can audit a contract's full lifecycle across all three process boundaries it crosses and identify a gap where tenant context is not consistently enforced, even when it produces no visible symptom with only one tenant's data present. You can sequence a build using a deliberately throwaway extraction stub to unblock frontend work in parallel, while correctly keeping the tenant-isolation seam in place from the very first migration rather than deferring it alongside the stub.

## Suggested Extension

Replace the five-second polling interval with a WebSocket push notification that fires the moment extraction completes, and state the specific load or customer-feedback threshold (for example: multiple concurrent reviewers actively waiting on the same in-flight extraction) that would justify that added complexity, rather than building it preemptively at pilot scale.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why polling, not a live socket, at pilot scale
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the review queue use a fixed polling interval with `useQuery` instead of a live WebSocket connection for extraction status updates?

**OPTIONS:**
- [x] A: Polling every few seconds is boring, correct, and entirely sufficient at pilot scale, matching the earlier architecture lesson's default-to-boring principle applied to a real implementation choice
- [ ] B: WebSocket connections are technically incompatible with React applications
- [ ] C: Polling is always faster than a WebSocket connection under any load
- [ ] D: RLS policies cannot be enforced over a WebSocket connection

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a direct callback to lesson 1's architecture-spine argument, now used as a real implementation decision rather than an abstract principle — the simpler mechanism is chosen because nothing yet justifies the added complexity.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [polling-vs-websocket, boring-default-applied]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why three process boundaries all need the RLS pattern
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist the RLS session-context pattern be applied consistently at all three of the upload handler, the extraction worker, and the export endpoint, rather than just the one built or tested first?

**OPTIONS:**
- [ ] A: Postgres requires the pattern to be repeated exactly three times in any application, regardless of the actual number of entry points
- [x] B: A single contract's lifecycle spans all three as genuinely separate processes, and a gap at just one of them — even if the other two are correct — is a real cross-tenant leak that produces no visible symptom until a second tenant's data exists
- [ ] C: The pattern only actually needs to exist at one entry point; the other two are redundant safety measures
- [ ] D: Export endpoints are exempt from RLS enforcement by design, since they only read already-approved data
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific claim is that correctness at two of three entry points provides no protection at the third — each process boundary is an independent place the pattern can be forgotten.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [three-entry-points, consistent-enforcement]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why the extraction stub is built before the real pipeline
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson's recommended build order put a hardcoded extraction stub before the real OCR-and-grounded-extraction pipeline?

**OPTIONS:**
- [ ] A: The real extraction pipeline is technically impossible to build without a stub existing first
- [x] B: The stub unblocks the review-queue frontend from being built and tested against realistic-shaped data without waiting on the real extraction pipeline, which takes longer to build correctly
- [ ] C: Stubs are required by the discovery module's non-goals discipline for every FDE engagement
- [ ] D: The real extraction pipeline cannot produce data in the same shape the stub does
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The stub's purpose is unblocking parallel frontend work against realistic data, which is why it is deliberately throwaway rather than kept — unlike the RLS seam, which is kept from day one.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [extraction-stub, build-sequencing]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the stub is throwaway but the org_id column is not
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What distinguishes the extraction stub (deliberately throwaway) from the `org_id` column and RLS policy (kept from the first migration), per the lesson's use of the earlier architecture lesson's framework?

**OPTIONS:**
- [ ] A: There is no meaningful distinction; both should ideally be discarded once the real pipeline exists
- [x] B: The stub exists only to unblock parallel work and is cheap to discard once its purpose is served, while the `org_id` column is the cheap-now, expensive-to-retrofit-later seam that must be kept from day one to avoid a costly migration and leak risk
- [ ] C: The `org_id` column should also be discarded once a second tenant onboards, since it was only needed for the pilot
- [ ] D: The stub and the `org_id` column serve identical purposes and are interchangeable in the build sequence
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This connects lesson 1's seam-versus-generality distinction directly to this build's real sequencing choices — one decision is cheap to discard, the other is expensive to add later, and the build order treats them accordingly.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [stub-vs-seam, architecture-lesson-callback]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why per-tenant queue routing waits for Globex
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the build order defer per-tenant Celery queue routing until Globex actually onboards, rather than building it alongside the first version of the extraction worker?

**OPTIONS:**
- [ ] A: Per-tenant queue routing is technically impossible to implement before a second tenant's data exists in the database
- [x] B: Building queue routing against a single tenant has nothing real to validate it against — the noisy-neighbor problem it solves only becomes real, and testable, once a second tenant's jobs actually share worker capacity
- [ ] C: Celery does not support queue routing under any circumstances
- [ ] D: Acme explicitly requested that queue routing be delayed as part of the pilot contract
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This mirrors the lesson's build-order logic — deferring a feature until there is a real, evidenced need to validate it against, not because it's technically infeasible earlier.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [deferred-queue-routing, evidenced-need]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What the pre-launch RLS audit found
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific gap did the pre-launch review of all three RLS entry points catch in the scenario?

**OPTIONS:**
- [ ] A: The upload handler was missing the `org_id` column on the `contracts` table entirely
- [x] B: The Celery extraction task, copied from an earlier single-tenant prototype, never had the `SET LOCAL app.current_org_id` line added, unlike the upload handler and export endpoint, which both correctly set it
- [ ] C: The React review queue was displaying clauses from the wrong tenant on every page load
- [ ] D: The export endpoint was exporting clauses before they had been approved by a reviewer
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the exact gap the "three entry points" claim in Concepts Covered predicts — two boundaries correct, one silently missed, inherited from code that predates the multi-tenant requirement.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scenario-rls-gap, prototype-inherited-defect]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the gap produced no visible symptom
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the missing `SET LOCAL` line in the Celery extraction task produce no visible symptom before the pre-launch review caught it?

**OPTIONS:**
- [x] B: With only Acme's data in the system, there was no second tenant's data for a missing tenant-context enforcement to leak into or from, so the gap was invisible until a real cross-tenant scenario existed to expose it
- [ ] A: The gap was cosmetic and never actually affected query results, regardless of how many tenants existed
- [ ] C: Postgres automatically prevents any query from running without a session variable set, masking the bug
- [ ] D: The review queue's polling interval was too slow to display the resulting incorrect data
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is exactly why the audit had to be deliberate rather than incidental — a single-tenant system cannot organically surface a cross-tenant enforcement gap through normal use.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [invisible-defect, single-tenant-masking]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What the latency measurement in step 5 actually validates
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does Practice Loop step 5 (measuring true end-to-end latency and comparing it to the polling interval) actually establish?

**OPTIONS:**
- [ ] A: The exact dollar cost of running the extraction pipeline per contract
- [x] B: Whether the five-second polling interval is still an acceptable user experience given the real, measured latency of the full pipeline, rather than an assumption that polling is fine without ever checking against real numbers
- [ ] C: Whether the RLS policy on the `contracts` table is correctly configured
- [ ] D: How many concurrent reviewers the system can support at once
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This step converts the "polling is fine at pilot scale" claim from an assumption into something checked against a real measured number, consistent with the lesson's broader insistence on diagnostic steps over assertions.

**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [latency-diagnostic, polling-validation]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What would justify the WebSocket upgrade
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, what kind of evidence would justify replacing polling with a WebSocket push notification, rather than building it preemptively?

**OPTIONS:**
- [ ] A: A stakeholder's general preference for more modern-sounding technology
- [x] B: A concrete load or customer-feedback threshold, such as multiple concurrent reviewers actively waiting on the same in-flight extraction, where polling's latency becomes a genuinely felt problem
- [ ] C: WebSockets should always replace polling as soon as the codebase is stable enough to support the change
- [ ] D: The five-second polling interval being technically possible to reduce further
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the same evidenced-need discipline the lesson applies throughout — the upgrade is justified by a real, demonstrated pain point, not by the technology sounding more sophisticated.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [evidenced-upgrade, websocket-justification]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: own knowledge (FDE application-integration practice, synthesizing lessons 1-4 of this module)

---

# LESSON 6

```yaml
lesson_id: fde-application-security-reliability-06-developer-experience-and-api-documentation
lesson_title: "Developer Experience & API Documentation"
lesson_order: 6

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: application-security-reliability
module_name: "7. Application Engineering, Security & Reliability"
module_order: 7

difficulty: Intermediate
estimated_minutes: 55
content_status: Draft

learning_outcomes:
  - "Publish an OpenAPI spec as the single source of truth for an external-facing API, so documentation and a typed client can be generated from it rather than hand-maintained separately."
  - "Design a structured, machine-parseable error response shape that lets an external integrator's code distinguish retryable from non-retryable failures without a support conversation."
  - "Version an external API with an explicit prefix and deprecation window, so an external integrator is never broken by a change they had no way to anticipate."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Developer Experience & API Documentation

## Concepts Covered

The export API that lets Acme's own integration engineer pull approved clauses out of ClauseReview is a different product surface from the reviewer-facing UI, aimed at a different persona who will likely never talk to the FDE directly — an external engineer integrating against documentation alone, on their own schedule, with no shared context about how the system was built. An OpenAPI spec written as the single source of truth for that endpoint, rather than a hand-written markdown page describing it after the fact, is the same discipline the frontend lesson applied to a Zod schema shared between a form and its type, now applied to an external contract instead of an internal one — the spec can generate both human-readable docs and, ideally, a typed client, so the documentation and the actual behavior of the endpoint cannot silently drift apart the way a hand-maintained description of an endpoint eventually does once the endpoint changes and nobody remembers to update the prose describing it. Versioning the endpoint under an explicit `/v1/` prefix, with a stated deprecation window before anything under it changes incompatibly, matters specifically because an external integrator cannot redeploy their own code on the FDE's schedule — a breaking change with no warning is a production incident on someone else's system that the FDE doesn't control and often doesn't even find out about until a support ticket arrives.

The second discipline is designing error responses as structured, machine-parseable data, not just an HTTP status code and a prose message a human is expected to read. A response shaped as `{ error: { code: 'RATE_LIMITED', message: '...', retryable: true } }` lets an integrator's calling code branch on `code` and `retryable` directly — retry a `RATE_LIMITED` response with backoff, but fail fast and alert a human on a `SCHEMA_VALIDATION_ERROR`, since retrying a permanently malformed request only repeats the same failure indefinitely. What developer experience concretely buys an FDE, beyond convenience, is fewer support escalations and a faster, more self-serve integration timeline for the customer's own engineer — and in an enterprise sales and delivery context, that engineer's actual experience integrating against the FDE's API becomes part of how the customer's organization evaluates the FDE's overall engineering maturity, not a detail confined to one technical corner of the engagement.

## Practical Backend Scenario

An earlier, ad-hoc version of ClauseReview's export endpoint returned a bare HTTP 500 with a generic message for two entirely different failure conditions: a transient database hiccup, which is safe to retry, and a permanently malformed export request, which is not. Acme's integration engineer's calling code, written to retry any 500 automatically, could not distinguish the two — and when a batch export request had a genuinely malformed field, the retry loop hammered the endpoint every few seconds for six hours before anyone at Meridian noticed the elevated error rate in their own logs. The FDE's fix ships an OpenAPI spec for `/v1/exports`, a structured error shape distinguishing `code`, `message`, and `retryable` so the integrator's existing retry logic can be updated to check `retryable` before retrying at all, and a documented deprecation policy stating that any future breaking change to `/v1/` will ship as `/v2/` with a minimum 90-day window before `/v1/` is removed — giving Acme's engineer, who the FDE may never speak with directly again after this incident, everything needed to build correct, self-correcting integration code without another six-hour incident or another support call.

## Practice Loop

1. Write an OpenAPI spec for the `/v1/exports` endpoint, covering the request shape, the success response shape, and every distinct error condition it can return.
2. Define the structured error response shape (`code`, `message`, `retryable`), and explicitly classify each error condition from step 1 as retryable or not.
3. Count how many genuinely distinct error conditions an integrator's code would need to distinguish to behave correctly (retry some, fail fast on others, alert a human on others) and confirm your structured shape actually covers all of them, not just the two from the incident.
4. Add the `/v1/` version prefix and write one sentence stating the deprecation policy an external integrator can rely on before any breaking change ships.
5. Write one changelog entry documenting a hypothetical future breaking change to `/v1/exports`, and state exactly how an external integrator would be notified of it before it takes effect.

## Evidence of Understanding

You can publish an OpenAPI spec as the single source of truth for an external-facing endpoint, and explain why generating documentation from it prevents the drift a hand-maintained description eventually accumulates. You can design a structured error response shape that lets an external integrator's code distinguish retryable from non-retryable failures programmatically, without a support conversation. You can version an external API with an explicit prefix and a stated deprecation window, and explain why an external integrator needs that guarantee in a way an internal team, which can coordinate a deploy directly, does not.

## Suggested Extension

Add a sandbox or test-mode API key that returns realistic sample export data, so Acme's integration engineer can build and test their integration against `/v1/exports` before ever being granted access to real tenant data.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why an OpenAPI spec is the single source of truth
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson prefer an OpenAPI spec that generates documentation, over a hand-written markdown page describing the endpoint after the fact?

**OPTIONS:**
- [x] A: A spec-generated doc and the endpoint's actual behavior cannot silently drift apart the way a hand-maintained prose description eventually does once the endpoint changes and nobody remembers to update the description
- [ ] B: OpenAPI specs are required by law for any externally-facing API
- [ ] C: Hand-written documentation is always less detailed than a generated one, regardless of maintenance
- [ ] D: Generated documentation loads faster in a browser than hand-written documentation

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The drift argument is the lesson's specific claim — a single source of truth cannot silently disagree with itself the way two independently maintained artifacts (the code and a separate description of it) can.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [openapi-single-source, doc-drift]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Parallel to the frontend lesson's shared Zod schema
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson connect the OpenAPI spec discipline to the earlier frontend lesson's shared Zod schema?

**OPTIONS:**
- [ ] A: OpenAPI specs and Zod schemas are literally the same technology used interchangeably
- [x] B: Both apply the same underlying discipline — a single source of truth that generates both the type/validation and the documentation/client, so the two can never silently disagree — just applied to an external API contract here instead of an internal frontend/backend one
- [ ] C: The connection is purely coincidental and carries no shared underlying principle
- [ ] D: Zod schemas are only usable for external APIs, never for internal frontend forms
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson explicitly draws this parallel: single-source-of-truth discipline against drift, applied at a different boundary (external API) than lesson 2's internal form/type boundary.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [single-source-of-truth-parallel, lesson-2-callback]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why external integrators specifically need a deprecation window
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say versioning and a deprecation window matter specifically for an external-facing API, in a way that matters less for a purely internal one?

**OPTIONS:**
- [ ] A: External APIs are technically incapable of being versioned using the same mechanisms as internal ones
- [x] B: An external integrator cannot redeploy their own code on the FDE's schedule, so a breaking change with no warning becomes a production incident on a system the FDE doesn't control and may not even find out about until a support ticket arrives
- [ ] C: Internal APIs never change once they are first deployed, unlike external ones
- [ ] D: Deprecation windows are a purely cosmetic convention with no practical effect on integrators
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific claim is about coordination — an internal team can coordinate a deploy directly, while an external integrator has no such coordination channel and needs advance warning instead.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [deprecation-window, external-coordination]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What a structured error shape lets calling code do
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does a structured error response like `{ error: { code: 'RATE_LIMITED', message: '...', retryable: true } }` let an integrator's calling code do that a bare HTTP status and prose message does not?

**OPTIONS:**
- [x] A: Branch programmatically on `code` and `retryable` — retrying a rate-limited request with backoff, but failing fast and alerting a human on a permanently malformed request, without a human reading and interpreting a prose message first
- [ ] B: Automatically fix the underlying cause of the error without any code changes required
- [ ] C: Guarantee the request will always eventually succeed if retried enough times
- [ ] D: Bypass the need for any authentication on subsequent retry attempts
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The structured shape's entire value is programmatic branching — retryable versus not — without requiring a human to read and interpret an unstructured message first.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [structured-error-shape, retryable-branching]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the original bare-500 endpoint caused the six-hour incident
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did Acme's integration engineer's retry logic hammer the export endpoint for six hours in the scenario?

**OPTIONS:**
- [ ] A: The integration engineer's code had a bug entirely unrelated to the API's error responses
- [x] B: The endpoint returned a bare HTTP 500 with a generic message for both a transient, safely-retryable database hiccup and a permanently malformed request, so the integrator's blanket retry-on-500 logic could not distinguish the two and kept retrying a request that would never succeed
- [ ] C: Meridian's servers were experiencing an unrelated outage during that six-hour window
- [ ] D: The `/v1/` version prefix had not yet been added to the endpoint at the time
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The root cause is the undifferentiated 500 response, exactly the problem structured, machine-parseable error codes are designed to fix.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scenario-retry-loop, undifferentiated-500]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What the fix specifically gave Acme's engineer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What did the FDE's fix specifically give Acme's integration engineer, whom the FDE may never speak with directly again after the incident?

**OPTIONS:**
- [ ] A: A promise that the export endpoint would never return an error response again
- [x] B: An OpenAPI spec, a structured retryable-vs-not error shape, and a documented deprecation policy — everything needed to build correct, self-correcting integration code without another support call or incident
- [ ] C: Direct, ongoing access to the FDE's personal contact information for future troubleshooting
- [ ] D: A completely different API endpoint replacing the original export functionality
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The fix is specifically about self-service — giving the integrator everything needed to build correct code independently, since ongoing direct FDE involvement doesn't scale.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [self-serve-integration, scenario-fix]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Purpose of counting distinct error conditions in the practice loop
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does Practice Loop step 3 ask the learner to count every genuinely distinct error condition the endpoint can return, rather than stopping once the two conditions from the incident are covered?

**OPTIONS:**
- [x] A: A structured error shape that only covers the specific conditions from one past incident, rather than the endpoint's full range of possible failures, would leave other real error conditions still undifferentiated and vulnerable to the same class of problem
- [ ] B: OpenAPI specifications technically require documenting an exact fixed number of error conditions
- [ ] C: This step is purely a documentation exercise with no bearing on the integrator's actual retry behavior
- [ ] D: Every API must have exactly as many error codes as it has endpoints
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The diagnostic guards against fixing only the specific incident that happened rather than the general class of problem — a narrow fix leaves other undifferentiated error conditions still capable of causing the same kind of incident.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [error-coverage-diagnostic, beyond-the-incident]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why a sandbox key matters for the suggested extension
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the Suggested Extension add a sandbox or test-mode API key with realistic sample data, rather than having Acme's engineer integrate directly against real tenant data from the start?

**OPTIONS:**
- [ ] A: Real tenant data is technically incompatible with the export API's response format
- [x] B: It lets the integrator build and test their integration independently before being granted access to real, sensitive tenant data — extending the same self-serve, don't-require-a-live-conversation principle the rest of the lesson establishes
- [ ] C: Sandbox keys are a regulatory requirement for every enterprise API regardless of data sensitivity
- [ ] D: A sandbox key removes the need for the OpenAPI spec entirely
**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The sandbox key extends the same self-serve philosophy — letting the integrator work independently and safely before real data or a live conversation with the FDE is required.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [sandbox-key, self-serve-extension]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

Reference: OpenAPI Specification documentation (openapis.org) — versioning and error-response design conventions

