# Prompt for Local LLM — FDE Phase 6: Backend Engineering (Module 2), Lessons 6-10 of 15

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-6-backend-observability-data-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 28 existing cases (11 `agentic-ai-core` + 12 `fde-foundations` + 5
`backend-observability-data` lessons 1-5 from Phase 5) before `_ => null`. If those aren't there,
STOP — Phase 5 must be applied first.

**Note on a numbering correction:** Phase 5 covered curriculum lessons 1-5 of the
`backend-observability-data` module (Intro to Backend Engineering, FastAPI, Auth, Order
Management, Payments). Lesson 6 of that module ("Building the Demo Frontend") was inadvertently
not included in any earlier phase — this phase (Phase 6) correctly starts at lesson 6 and covers
6-10. No lesson is duplicated or skipped across Phases 5+6 combined; verify this by confirming
none of the 5 slugs in the table below already exist among the 28 current cases.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-6-backend-observability-data-content.md`

This file contains 5 lessons, each with a YAML metadata block, a `<!-- CHAPTER_BODY_START -->`
… `<!-- CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!--
MCQ_SECTION_END -->` block with 8-9 structured `QUESTION_BLOCK`s per lesson.

The 5 lessons, in order, with their exact database slugs:

| # | Lesson title | Lesson slug (use exactly) |
|---|---|---|
| 6 | Building the Demo Frontend | `06-building-the-demo-frontend` |
| 7 | Real-Time, Queues & Caching (WebSockets, SSE, Redis) | `07-real-time-queues-and-caching-websockets-sse-redis` |
| 8 | Observability & Distributed Tracing (OpenTelemetry, Grafana) | `08-observability-and-distributed-tracing-opentelemetry-grafana` |
| 9 | Postgres Advanced: JSONB, Full-Text Search & pgvector | `09-postgres-advanced-jsonb-full-text-search-and-pgvector` |
| 10 | Postgres Internals: EXPLAIN ANALYZE, Indexing & MVCC | `10-postgres-internals-explain-analyze-indexing-and-mvcc` |

Module slug for all 5: `backend-observability-data` (same module Phase 5 used).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 28 existing cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 28 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 28 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/backend-observability-data/{lesson-slug}'
```

e.g. `'fde-curriculum/backend-observability-data/06-building-the-demo-frontend'`

Do NOT touch any existing key — 22 `java-spring-lld/...`, 11 `fde-curriculum/agentic-ai-core/...`,
12 `fde-curriculum/fde-foundations/...`, and 5 `fde-curriculum/backend-observability-data/...`
(from Phase 5) already present.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before. `id` pattern:
`lesson-fde-backend-observability-data-{lesson-number:00}-concept-check-{01|02}` (lesson-number
is 06-10 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from prior phases hold. Lesson 8 (Observability/Distributed
Tracing) is the most likely candidate — a trace-waterfall-style diagram (spans across the
FastAPI service, Celery worker, and Stripe call, showing which one dominates duration) could
genuinely show something the prose doesn't as clearly. Otherwise default to omitting the
`architecture` key.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-backend-observability-data-{lesson-number:00}-mcq-{01, 02, ...}`. None of this
phase's questions need a `codeBlock` field — omit it.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS
data field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 28 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 + 11 + 12 + 5 = 50 total)
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
Full method body — all 33 cases now present (28 existing unchanged, 5 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 50 existing entries unchanged, plus the 5 new entries for this phase
(55 total).

### OUTPUT C: Architecture diagram decisions
For each of the 5 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 5 lessons already exist in the database with non-empty, generic `ContentBody`. After
applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '06-building-the-demo-frontend',
  '07-real-time-queues-and-caching-websockets-sse-redis',
  '08-observability-and-distributed-tracing-opentelemetry-grafana',
  '09-postgres-advanced-jsonb-full-text-search-and-pgvector',
  '10-postgres-internals-explain-analyze-indexing-and-mvcc'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 28 existing cases,
      before `_ => null`
- [ ] `lessonInteractions.js` has 5 new `fde-curriculum/backend-observability-data/...` keys; all
      50 pre-existing keys unchanged
- [ ] Ran the SQL reset for all 5 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 6-10 in "2. Backend Engineering,
      Observability & Advanced Data Systems" render real authored content, and that lesson 6
      ("Building the Demo Frontend") — which was skipped in Phase 5 — is no longer showing
      generic draft content
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
