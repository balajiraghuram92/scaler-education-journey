# Prompt for Local LLM — FDE Phase 15: Application Engineering, Security & Reliability (Module 7), Lessons 1-6 of 12

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-15-application-security-reliability-content.md` in full, and report
back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not
paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies and
MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match what
this prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **73 existing cases** before `_ => null`. This phase is applied third in a
three-phase batch: Phase 12 (6 cases) is applied first, then Phase 13 (6 cases), then this Phase
15. 73 = 61 cases from Phases 1-11 + 6 from Phase 12 + 6 from Phase 13.

**If the case count is anything other than 73, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains.

One thing this check deliberately does NOT require: Module 6's remaining lessons 7-11 do not need
to exist yet. Phase 14 (which would add those) is intentionally skipped for now — Module 6 will
show only 6 of 11 lessons with authored content when this phase lands, and that is expected and
has no bearing on this phase. This phase's only real dependency is the **case count being exactly
73** — Module 7 (this phase) has no content dependency on Module 6 at all, since they are
independent modules. Do not block on Module 6's completeness; block only on the count.

Also confirm `app/src/data/lessonInteractions.js` has **95 existing keys** before proceeding: 22
`java-spring-lld/...` + 73 `fde-curriculum/...` (61 from Phases 1-11 + 6 from Phase 12 + 6 from
Phase 13). If this count doesn't match, STOP and report the exact count you find.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-15-application-security-reliability-content.md`

This file contains 6 lessons, the **first half** of a **new module**, Module 7 ("7. Application
Engineering, Security & Reliability"), lessons 1-6 of 12. A later phase covers lessons 7-12
(Enterprise Security for FDE Systems: PII, SOC2, GDPR; Secrets, Encryption & Deployment
Topologies; Load Testing, Capacity Planning & Performance with k6; Incident Response &
Customer-Facing RCA; Enterprise Readiness Checklist & Go-Live; and an Assessment) and completes
the module — do not add placeholder content for those 6 lessons in this phase.

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 1 | Product Thinking & Architecture for FDE Apps | `01-product-thinking-and-architecture-for-fde-apps` | 8 |
| 2 | Frontend Essentials for FDEs: React + TypeScript | `02-frontend-essentials-for-fdes-react-plus-typescript` | 8 |
| 3 | Multi-Tenant Design & Background Workflows (Postgres RLS, Celery) | `03-multi-tenant-design-and-background-workflows-postgres-rls-celery` | 9 |
| 4 | Document Processing & AI Extraction Workflows | `04-document-processing-and-ai-extraction-workflows` | 9 |
| 5 | Build: Enterprise Document Review App | `05-build-enterprise-document-review-app` | 9 |
| 6 | Developer Experience & API Documentation | `06-developer-experience-and-api-documentation` | 8 |

Total MCQs across all 6 lessons: **51**.

Module slug for all 6: `application-security-reliability` (this is a brand-new module — this is
its first phase; a later phase adds lessons 7-12 to the same module, completing it at 12 total).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 73 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 73 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 73 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/application-security-reliability/{lesson-slug}'
```

e.g. `'fde-curriculum/application-security-reliability/01-product-thinking-and-architecture-for-fde-apps'`

Do NOT touch any existing key — 22 `java-spring-lld/...` + 73 `fde-curriculum/...` (11
`agentic-ai-core` + 12 `fde-foundations` + 15 `backend-observability-data` + 5
`full-stack-ai-frontends` + 12 `cloud-devops-infrastructure` + 6 `enterprise-consulting-llm`
Phase 11 + 6 Phase 12 + 6 Phase 13) = **95 total existing keys** already present. After this
phase, the file should have **101 total keys** (95 + 6 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-application-security-reliability-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 01-06 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons.

Lesson 5 ("Build: Enterprise Document Review App") is the one genuine candidate — its Concepts
Covered describes a request/job/poll flow spanning three separate processes (the upload API
handler, the Celery extraction worker, and the review-queue's polling API call), each of which
must independently apply the RLS session-context pattern, and this multi-process, multi-actor
relationship is not fully obvious from the prose alone. If you include an `architecture` object
for lesson 5, model the three process boundaries as nodes with the RLS enforcement point
highlighted (`highlighted: true`) at each of the three, per §8a's node shape — do not model it as
a simple linear upload→extract→review→export flow, since that repeats what the Practical Backend
Scenario prose already states; the diagram only earns its place if it makes the "three separate
enforcement points" relationship visually clearer than the prose does.

For lessons 1, 2, 3, 4, and 6: these are architecture-discussion, frontend-pattern, RLS-mechanism,
extraction-pipeline, and API-documentation lessons respectively, and none describe a multi-actor
async flow, decorator chain, or runtime-branching pattern beyond what a single before/after code
block or the scenario prose already covers — omit `architecture` for all five. If in doubt on
lesson 5, omit it as well; a diagram is not required for this phase to be complete.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-application-security-reliability-{lesson-number:00}-mcq-{01, 02, ...}`. None of this
phase's questions need a `codeBlock` field — omit it, even for Q1 of lesson 2, which discusses a
TypeScript code concept in prose (the actual multi-line code sample lives in the chapter body, not
in an MCQ).

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 73 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (95 total from Phases 1-13)
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
Full method body — all 79 cases now present (73 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 95 existing entries unchanged, plus the 6 new entries for this phase
(101 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 1, 2, 3, 4, and 6 omitted (no qualifying multi-actor or
runtime-branching flow); lesson 5 is a judgment call — either omitted (default, if the three-node
RLS-boundary diagram doesn't clearly clear the inclusion bar) or included with the three-process
RLS-boundary framing described in §3b above, not a linear upload→extract→review→export restatement
of the scenario prose.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons likely already exist in the database with thin, machine-templated `ContentBody`.
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-product-thinking-and-architecture-for-fde-apps',
  '02-frontend-essentials-for-fdes-react-plus-typescript',
  '03-multi-tenant-design-and-background-workflows-postgres-rls-celery',
  '04-document-processing-and-ai-extraction-workflows',
  '05-build-enterprise-document-review-app',
  '06-developer-experience-and-api-documentation'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the first half of Module 7 ("7. Application Engineering, Security & Reliability")
— lessons 1-6 of 12 should now have authored content. Lessons 7-12 remain for a future phase, and
Module 6's lessons 7-11 also remain outstanding from the deliberately-skipped Phase 14 — neither
of those is in scope for this phase.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 73 existing cases, before
      `_ => null` (79 total)
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/application-security-reliability/...`
      keys; all 95 pre-existing keys unchanged (101 total)
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 1-6 of "7. Application Engineering,
      Security & Reliability" render real authored content, and lessons 7-12 still show
      placeholder/draft content pending a future phase
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this, but verify none were dropped or duplicated
      during transcription
