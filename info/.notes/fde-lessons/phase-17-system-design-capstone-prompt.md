# Prompt for Local LLM — FDE Phase 17: System Design, Capstone & Hiring Readiness (Module 8), Lessons 1-5 of 14

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-17-system-design-capstone-content.md` in full, and report back what
lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from that
file verbatim. If you cannot read the file, or if what you find doesn't match what this prompt
describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **90 existing cases** before `_ => null`. This phase is applied second in a
four-phase batch: Phase 16 (Module 7, completing it — 6 cases) is applied first, then this Phase
17, then Phase 18, then Phase 19 (Phases 18/19 cover the rest of Module 8, being authored in
parallel — do not worry about their exact content, and do not treat their absence as a problem).
90 = 84 cases already on disk before this batch (Phases 1-15) + 6 from Phase 16.

**If the case count is anything other than 90, STOP and report the exact count you find instead of
proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains.

Also confirm `app/src/data/lessonInteractions.js` has **108 existing keys** before proceeding: 18
`java-spring-lld/...` + 90 `fde-curriculum/...` (84 from Phases 1-15 + 6 from Phase 16). If this
count doesn't match, STOP and report the exact count you find.

One thing this check deliberately does NOT require: Module 8's lessons 6-14 do not need to exist
yet. Phases 18 and 19 (which will add those) may land before or after this phase depending on
execution order — Module 8 will show only 5 of 14 lessons with authored content when this phase
lands on its own, and that is expected and has no bearing on this phase. This phase's only real
dependency is the **case count being exactly 90** before this phase's 5 cases are added.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-17-system-design-capstone-content.md`

This file contains 5 lessons, the **first third** of a **brand-new module** — the final module of
the entire FDE core curriculum — Module 8 ("8. System Design, Capstone & Hiring Readiness"),
lessons 1-5 of 14. Two more phases (18 and 19), already in progress in parallel, cover lessons 6-14
(Interview Framework, four Capstone Sprints, Demo Day, Interview Readiness, Mock Engagement, and a
Graduation Review) and complete the module — do not add placeholder content for those 9 lessons in
this phase.

Each of the 5 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 5 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 1 | Distributed Systems Fundamentals (CAP, PACELC, Raft, Saga) | `01-distributed-systems-fundamentals-cap-pacelc-raft-saga` | 9 |
| 2 | System Design: RAG System at Scale | `02-system-design-rag-system-at-scale` | 9 |
| 3 | System Design: Agentic Platform at Scale | `03-system-design-agentic-platform-at-scale` | 9 |
| 4 | System Design: Multi-Tenant SaaS Platform | `04-system-design-multi-tenant-saas-platform` | 9 |
| 5 | System Design: Enterprise Integration Hub | `05-system-design-enterprise-integration-hub` | 9 |

Total MCQs across all 5 lessons: **45**.

Module slug for all 5: `system-design-capstone` (this is a brand-new module — this is its first
phase; two later phases add lessons 6-14 to the same module, completing it at 14 total).

These slugs were derived by hand-applying the repo's own `Slugify` function (lowercase; `&` → `
and `; `+` → ` plus `; every other run of non-alphanumeric characters, including parentheses and
commas, collapsed to a single `-`; trimmed) to each exact title in `api/Data/FdeSeedData.cs` — do
not re-derive them; use the table above exactly as written.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 90 existing cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 90 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 90 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/system-design-capstone/{lesson-slug}'
```

e.g. `'fde-curriculum/system-design-capstone/01-distributed-systems-fundamentals-cap-pacelc-raft-saga'`

Do NOT touch any existing key — 18 `java-spring-lld/...` + 90 `fde-curriculum/...` = **108 total
existing keys** already present. After this phase, the file should have **113 total keys** (108 +
5 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-system-design-capstone-{lesson-number:00}-concept-check-{01|02}` (lesson-number is
01-05 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase `correctOptionId`.
Never add `initialSelectedOption` or `initialSubmitted`.

Good candidates, one suggestion per lesson (use your own judgment on the second):
- Lesson 1: the CAP-is-per-data-path correction (Q1), or the Raft odd-cluster-sizing argument (Q4)
- Lesson 2: the tiered vector-index topology justification (Q4), or the PACELC application to
  index vs. routing-table consistency (Q6)
- Lesson 3: the I/O-bound worker-pool sizing correction (Q1), or the structural (not
  policy-based) per-tenant MCP scoping argument (Q3)
- Lesson 4: the three-tier isolation justification (Q1), or the RLS owner-bypass danger (Q6)
- Lesson 5: the point-to-point-vs-hub connection-count math (Q1), or the hub's central tension
  (Q2)

### 3b. architecture (optional — apply the inclusion test seriously)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 5 lessons. **This
phase is different from prior phases: these lessons are explicitly about system topology, so
apply the test with real scrutiny per lesson rather than defaulting to omit.** A system-design
lesson whose "Practical Backend Scenario" section names concrete named components (a routing
layer, a shard topology, a hub, a saga orchestrator) with real relationships between them is a
strong candidate — evaluate each one on its own merits rather than assuming the OOP-lesson default
("most lessons should not include one") transfers unchanged to this module.

Suggested (not mandatory) starting judgment per lesson — verify against the actual inclusion test
yourself before deciding:
- **Lesson 1**: borderline. The CAP/PACELC/Raft/Saga content is conceptual rather than one system
  topology; if you include a diagram, it should show the two distinct scenarios (multi-region
  write-path CP/AP choice; the 3-node Raft coordination cluster; the 3-step saga with
  compensations) as three small distinct groups, not a single linear flow. Omitting is a reasonable
  default here since the three sub-topics don't share one topology worth drawing as one diagram.
- **Lesson 2**: a strong candidate. The tiered vector-index topology (query router → dedicated
  shards for large tenants + partitioned shared index for the long tail) is a genuine multi-path
  routing structure not fully obvious from prose alone. If included, model the router as the
  `highlighted: true` node and show both the dedicated-shard path and the shared-index path as
  distinct branches — not a single linear query→answer flow.
- **Lesson 3**: a strong candidate. The per-tenant MCP server isolation (each tenant's workflow
  reaching only its own MCP server instance, never another tenant's) is exactly the kind of
  structural-boundary relationship the inclusion test rewards, and is not obvious from prose alone
  in a way a single diagram could clarify quickly. If included, highlight the per-tenant boundary
  nodes.
- **Lesson 4**: a strong candidate. The three-tier isolation architecture (RLS shared / schema-per-
  tenant / database-per-tenant, with a connection-pooling proxy in front of the dedicated tier) is
  a genuine multi-path structure with three distinct enforcement boundaries. If included, highlight
  the pooling-proxy node and the RLS-boundary node as the two enforcement points worth calling out.
- **Lesson 5**: a strong candidate. The hub-based topology itself (event bus at the center, 20+
  connectors, entity-resolution service, saga orchestrator, audit log) is precisely the
  "multi-actor async flow" the inclusion test is looking for, and the whole point of a hub topology
  is that it's easier to see in a diagram than to read as prose. If included, highlight the event
  bus node as the central boundary/enforcement point.

For whichever lessons you decide, after applying the test yourself, do NOT qualify: omit the
`architecture` key entirely rather than including a weak or purely decorative diagram. Do not
model any included diagram as a simple linear request→output flow — that fails the test regardless
of the lesson.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-system-design-capstone-{lesson-number:00}-mcq-{01, 02, ...}`. None of this phase's
questions need a `codeBlock` field — omit it; every question in this phase is prose-only
(capacity-estimation reasoning, trade-off analysis, failure-mode design), with no multi-line code
snippet to render.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 90 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (108 total from Phases 1-16)
- `lessonExerciseAssociations.js`
- Any CSS file, any other `.cs` file, any other `.js` file
- The `getLessonInteractions` export at the bottom of `lessonInteractions.js`

Match code style exactly:
- `FdeCurriculumSeedData.cs`: C# verbatim strings, double-quote escaping, 4-space indent
- `lessonInteractions.js`: single quotes, 2-space indent, trailing comma on last property

---

## 6. Output format

Produce, clearly labeled:

### OUTPUT A: The updated `GetAuthoredFdeLessonContent` method
Full method body — all 95 cases now present (90 existing unchanged, 5 new from this phase), before
`_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 108 existing entries unchanged, plus the 5 new entries for this phase
(113 total).

### OUTPUT C: Architecture diagram decisions
For each of the 5 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason, referencing the specific inclusion-test criterion that decided it. Unlike
prior phases, do not default to omitting all five — this module's lessons are strong candidates by
design; justify each decision on its own merits.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 5 lessons likely already exist in the database with thin, machine-templated `ContentBody`
(or may not exist yet, if this is the first time Module 8 has been seeded at all — either case is
fine). After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-distributed-systems-fundamentals-cap-pacelc-raft-saga',
  '02-system-design-rag-system-at-scale',
  '03-system-design-agentic-platform-at-scale',
  '04-system-design-multi-tenant-saas-platform',
  '05-system-design-enterprise-integration-hub'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the first third of Module 8 ("8. System Design, Capstone & Hiring Readiness") —
lessons 1-5 of 14 should now have authored content. Lessons 6-14 remain for Phases 18 and 19,
already in progress in parallel — neither is in scope for this phase.

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 90 existing cases, before
      `_ => null` (95 total)
- [ ] `lessonInteractions.js` has 5 new `fde-curriculum/system-design-capstone/...` keys; all 108
      pre-existing keys unchanged (113 total)
- [ ] Ran the SQL reset for all 5 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 1-5 of "8. System Design, Capstone &
      Hiring Readiness" render real authored content, and lessons 6-14 still show
      placeholder/draft content pending Phases 18 and 19
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
- [ ] For each lesson where an `architecture` object was included, confirmed it renders after the
      Practical Backend Scenario section and reflects the genuine multi-path/multi-boundary
      structure described in §3b, not a simple linear flow
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this programmatically, but verify none were dropped
      or duplicated during transcription
