# Prompt for Local LLM — FDE Phase 5: Backend Engineering (Module 2), Lessons 1-5 of 15

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-5-backend-observability-data-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 23 existing cases (11 from `agentic-ai-core`, 12 from `fde-foundations`,
covering Phases 1-4) before `_ => null`. If those aren't there, STOP — Phase 4 must be applied
first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-5-backend-observability-data-content.md`

This file contains 5 lessons, the first third of Module 2 ("2. Backend Engineering,
Observability & Advanced Data Systems"). Each has a YAML metadata block, a `<!--
CHAPTER_BODY_START -->` … `<!-- CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->`
… `<!-- MCQ_SECTION_END -->` block with 8-9 structured `QUESTION_BLOCK`s per lesson.

**Important — this is a new, different module.** These 5 lessons belong to module slug
`backend-observability-data`, NOT `agentic-ai-core` or `fde-foundations`. Use the correct module
slug in every `lessonInteractions.js` key below.

The 5 lessons, in order, with their exact database slugs:

| # | Lesson title | Lesson slug (use exactly) |
|---|---|---|
| 1 | Introduction to Backend Engineering — HTTP, REST & API Design | `01-introduction-to-backend-engineering-http-rest-and-api-design` |
| 2 | FastAPI: Intro to Deep Dive | `02-fastapi-intro-to-deep-dive` |
| 3 | Auth: OAuth2, JWT, OIDC & RBAC | `03-auth-oauth2-jwt-oidc-and-rbac` |
| 4 | Building an Order Management Module & its API | `04-building-an-order-management-module-and-its-api` |
| 5 | Building Payments & Notifications (Stripe, Celery) | `05-building-payments-and-notifications-stripe-celery` |

Module slug for all 5: `backend-observability-data`

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 23 existing cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 23 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 23 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/backend-observability-data/{lesson-slug}'
```

e.g. `'fde-curriculum/backend-observability-data/01-introduction-to-backend-engineering-http-rest-and-api-design'`

Do NOT touch any existing key — 22 `java-spring-lld/...`, 11 `fde-curriculum/agentic-ai-core/...`,
and 12 `fde-curriculum/fde-foundations/...`.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before. `id` pattern:
`lesson-fde-backend-observability-data-{lesson-number:00}-concept-check-{01|02}` (lesson-number
is 01-05 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from prior phases hold. Lesson 4 (Order Management) is the most
likely candidate — an order state-machine diagram (states as nodes, valid transitions as edges)
could genuinely show something the prose doesn't as clearly. Lesson 5 (Payments/Celery) is a
second candidate — a webhook-to-queue flow (Stripe → webhook handler → order state update +
queued Celery task → async worker) could also pass the test. Otherwise default to omitting the
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
- Any of the 23 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 + 11 + 12 = 45 total)
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
Full method body — all 28 cases now present (23 existing unchanged, 5 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 45 existing entries unchanged, plus the 5 new entries for this phase
(50 total).

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
  '01-introduction-to-backend-engineering-http-rest-and-api-design',
  '02-fastapi-intro-to-deep-dive',
  '03-auth-oauth2-jwt-oidc-and-rbac',
  '04-building-an-order-management-module-and-its-api',
  '05-building-payments-and-notifications-stripe-celery'
);
```

**Note:** these slugs share the `01-` through `05-` numeric prefix pattern with earlier modules'
lessons, but the full slug strings are entirely different — this reset will only affect the 5
`backend-observability-data` module lessons targeted here. If you want to be extra certain, scope
the reset by module explicitly (adjust table/column names to this project's actual schema — check
`api/Models/` if unsure):

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE module_id = (
  SELECT id FROM course_modules WHERE slug = 'backend-observability-data'
)
AND slug IN (
  '01-introduction-to-backend-engineering-http-rest-and-api-design',
  '02-fastapi-intro-to-deep-dive',
  '03-auth-oauth2-jwt-oidc-and-rbac',
  '04-building-an-order-management-module-and-its-api',
  '05-building-payments-and-notifications-stripe-celery'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 23 existing cases,
      before `_ => null`
- [ ] `lessonInteractions.js` has 5 new `fde-curriculum/backend-observability-data/...` keys; all
      45 pre-existing keys unchanged
- [ ] Ran the SQL reset scoped correctly to this module's first 5 lessons, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed the first 5 lessons in "2. Backend
      Engineering, Observability & Advanced Data Systems" render real authored content
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim
      (not rewritten/paraphrased), concept checks not pre-answered on load, practice questions
      render at the bottom
