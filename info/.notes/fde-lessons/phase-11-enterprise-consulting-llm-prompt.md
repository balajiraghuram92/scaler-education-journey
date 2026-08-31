# Prompt for Local LLM — FDE Phase 11: Enterprise Communication, Consulting & LLM Engineering (Module 5), Lessons 1-6 of 12

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-11-enterprise-consulting-llm-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **55 existing cases** (11 `agentic-ai-core` + 12 `fde-foundations` + 15
`backend-observability-data` + 5 `full-stack-ai-frontends` + 12 `cloud-devops-infrastructure`,
covering Phases 1-10) before `_ => null`. If those 55 cases aren't there — in particular, if
`cloud-devops-infrastructure` does not yet have 12 cases — STOP. Phase 10 must be applied first;
do not proceed with this phase until it has been.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-11-enterprise-consulting-llm-content.md`

This file contains 6 lessons, the first half of Module 5 ("5. Enterprise Communication,
Consulting & LLM Engineering"), lessons 1-6 of 12. A later phase covers lessons 7-12 (RAG
Architecture, RAG over Customer Documents, RAG Evaluation/RAGAS, LLM Safety/Guardrails,
Cost/Latency/Model Routing, and an Assessment) and completes the module — do not add placeholder
content for those 6 lessons in this phase.

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 1 | Customer Discovery & Requirements Gathering | `01-customer-discovery-and-requirements-gathering` | 8 |
| 2 | Technical Scoping & Solution Documentation (PRD-lite, options matrix, risk register) | `02-technical-scoping-and-solution-documentation-prd-lite-options-matrix-risk-register` | 8 |
| 3 | Stakeholder Communication & Written Artifacts | `03-stakeholder-communication-and-written-artifacts` | 8 |
| 4 | Demo Storytelling & Handling Pushback | `04-demo-storytelling-and-handling-pushback` | 8 |
| 5 | LLM Fundamentals for Production | `05-llm-fundamentals-for-production` | 9 |
| 6 | Prompt Engineering for Production Systems | `06-prompt-engineering-for-production-systems` | 9 |

Module slug for all 6: `enterprise-consulting-llm` (new module — this is its first phase; a later
phase adds lessons 7-12 to the same module).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 55 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 55 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 55 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/enterprise-consulting-llm/{lesson-slug}'
```

e.g. `'fde-curriculum/enterprise-consulting-llm/01-customer-discovery-and-requirements-gathering'`

Do NOT touch any existing key — 22 `java-spring-lld/...` + 11 `fde-curriculum/agentic-ai-core/...`
+ 12 `fde-curriculum/fde-foundations/...` + 15 `fde-curriculum/backend-observability-data/...` + 5
`fde-curriculum/full-stack-ai-frontends/...` + 12 `fde-curriculum/cloud-devops-infrastructure/...`
= **77 total existing keys** (from Phases 1-10) already present. After this phase, the file should
have 83 total keys (77 + 6 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-enterprise-consulting-llm-{lesson-number:00}-concept-check-{01|02}` (lesson-number is
01-06 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase `correctOptionId`.
Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons.
Lessons 1-4 are process/communication lessons (a discovery call, a written scoping document, a
status email, a demo) with no multi-actor async flow, decorator chain, or runtime-branching
pattern to diagram — omit `architecture` for all four. Lesson 6's prompt-versioning/eval-gate
sequence (prompt edit → golden test set run → pass/fail → merge or block) was considered for
lesson 5 or 6, but it is a linear request → check → outcome flow that the Practical Backend
Scenario prose already fully covers, which fails the inclusion test's second condition (the
diagram must show something the prose doesn't). Default to omitting the `architecture` key for
all 6 lessons in this phase unless you find a genuinely non-obvious multi-actor flow this
description missed — if in doubt, omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-enterprise-consulting-llm-{lesson-number:00}-mcq-{01, 02, ...}`. None of this phase's
questions need a `codeBlock` field — omit it.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 55 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (77 total from Phases 1-10)
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
Full method body — all 61 cases now present (55 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 77 existing entries unchanged, plus the 6 new entries for this phase
(83 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: all 6 omitted (lessons 1-4 have no qualifying flow; lessons 5-6's
candidate flows are linear and already covered by their scenario prose).

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons likely already exist in the database with thin, machine-templated `ContentBody`.
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-customer-discovery-and-requirements-gathering',
  '02-technical-scoping-and-solution-documentation-prd-lite-options-matrix-risk-register',
  '03-stakeholder-communication-and-written-artifacts',
  '04-demo-storytelling-and-handling-pushback',
  '05-llm-fundamentals-for-production',
  '06-prompt-engineering-for-production-systems'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the first half of Module 5 ("5. Enterprise Communication, Consulting & LLM
Engineering") — lessons 1-6 of 12 should now have authored content. Lessons 7-12 remain for a
future Phase 12.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 55 existing cases, before
      `_ => null` (61 total)
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/enterprise-consulting-llm/...` keys; all 77
      pre-existing keys unchanged (83 total)
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 1-6 of "5. Enterprise
      Communication, Consulting & LLM Engineering" render real authored content, and lessons 7-12
      still show placeholder/draft content pending a future phase
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
