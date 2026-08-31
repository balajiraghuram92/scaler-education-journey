# Prompt for Local LLM — FDE Phase 7: Backend Engineering (Module 2), Lessons 11-15 of 15 (module complete)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-7-backend-observability-data-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 33 existing cases (11 `agentic-ai-core` + 12 `fde-foundations` + 10
`backend-observability-data` lessons 1-10 from Phases 5-6) before `_ => null`. If those aren't
there, STOP — Phase 6 must be applied first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-7-backend-observability-data-content.md`

This file contains 5 lessons, completing Module 2 ("2. Backend Engineering, Observability &
Advanced Data Systems"), lessons 11-15 of 15. Each has a YAML metadata block, a `<!--
CHAPTER_BODY_START -->` … `<!-- CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->`
… `<!-- MCQ_SECTION_END -->` block with 8-9 structured `QUESTION_BLOCK`s per lesson.

The 5 lessons, in order, with their exact database slugs:

| # | Lesson title | Lesson slug (use exactly) |
|---|---|---|
| 11 | NoSQL, Document DBs & Vector Databases | `11-nosql-document-dbs-and-vector-databases` |
| 12 | Dimensional Modeling, dbt & Modern Data Stack | `12-dimensional-modeling-dbt-and-modern-data-stack` |
| 13 | Workflow Orchestration with Airflow & Data Quality | `13-workflow-orchestration-with-airflow-and-data-quality` |
| 14 | Event-Driven Architecture & Kafka Fundamentals | `14-event-driven-architecture-and-kafka-fundamentals` |
| 15 | Assessment: Data Pipeline Build & Debug | `15-assessment-data-pipeline-build-and-debug` |

Module slug for all 5: `backend-observability-data` (same module Phases 5-6 used — this
completes it, 15 of 15 lessons total).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 33 existing cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 33 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Note: Lesson 15 ("Assessment: Data Pipeline Build & Debug") has the same assessment-style
structure as the earlier "Assessment: Python Engineering Challenge" lesson — a short `##
Practical Backend Scenario` (the assessment IS the scenario) and a rubric embedded in `##
Concepts Covered`. Copy it exactly as it appears between the markers, same as any other lesson.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 33 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/backend-observability-data/{lesson-slug}'
```

e.g. `'fde-curriculum/backend-observability-data/11-nosql-document-dbs-and-vector-databases'`

Do NOT touch any existing key — 22 `java-spring-lld/...`, 11 `fde-curriculum/agentic-ai-core/...`,
12 `fde-curriculum/fde-foundations/...`, and 10 `fde-curriculum/backend-observability-data/...`
(from Phases 5-6) already present.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before. `id` pattern:
`lesson-fde-backend-observability-data-{lesson-number:00}-concept-check-{01|02}` (lesson-number
is 11-15 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from prior phases hold. Lesson 14 (Event-Driven
Architecture/Kafka) is the most likely candidate — a before/after contrast diagram (tightly
coupled synchronous/Celery calls vs. decoupled producer publishing to independent consumers)
could genuinely show something the prose doesn't. Otherwise default to omitting the
`architecture` key.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-backend-observability-data-{lesson-number:00}-mcq-{01, 02, ...}`. None of this
phase's questions need a `codeBlock` field — omit it.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS
data field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise, including lesson 15 (the assessment is
self-contained content with a rubric, not a submitted coding exercise — same convention as the
earlier Python Engineering Challenge assessment). Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 33 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 + 11 + 12 + 10 = 55 total)
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
Full method body — all 38 cases now present (33 existing unchanged, 5 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 55 existing entries unchanged, plus the 5 new entries for this phase
(60 total).

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
  '11-nosql-document-dbs-and-vector-databases',
  '12-dimensional-modeling-dbt-and-modern-data-stack',
  '13-workflow-orchestration-with-airflow-and-data-quality',
  '14-event-driven-architecture-and-kafka-fundamentals',
  '15-assessment-data-pipeline-build-and-debug'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes Module 2 ("2. Backend Engineering, Observability & Advanced Data Systems") —
all 15 lessons should now have authored content.

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 33 existing cases,
      before `_ => null`
- [ ] `lessonInteractions.js` has 5 new `fde-curriculum/backend-observability-data/...` keys; all
      55 pre-existing keys unchanged
- [ ] Ran the SQL reset for all 5 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 15 lessons in "2. Backend
      Engineering, Observability & Advanced Data Systems" render real authored content
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
