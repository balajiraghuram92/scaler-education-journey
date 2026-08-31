# Prompt for Local LLM — FDE Phase 19: System Design, Capstone & Hiring Readiness (Module 8), Lessons 11-14 of 14 — FINAL PHASE OF THE ENTIRE FDE CURRICULUM

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**This is the final content phase of the entire Neuralascent FDE project.** After this phase is
applied, all 8 numbered modules plus the Prerequisite module — the full ~104-lesson FDE core
curriculum — will have authored content. Treat the completeness of this phase's application with
extra care: this is not one of an ongoing series with more phases to follow.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-19-system-design-capstone-content.md` in full, and report back what
lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from that
file verbatim. If you cannot read the file, or if what you find doesn't match what this prompt
describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **100 existing cases** before `_ => null`. This phase is applied fourth and
last in a four-phase batch: Phase 16 (Module 7 lessons 7-12, 6 cases) is applied first, then Phase
17 (Module 8 lessons 1-5, 5 cases), then Phase 18 (Module 8 lessons 6-10, 5 cases), then this
Phase 19. 100 = 84 cases already on disk (Phases 1-15) + 6 from Phase 16 + 5 from Phase 17 + 5
from Phase 18.

**If the case count is anything other than exactly 100, STOP and report the exact count you find
instead of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and
do not substitute a different set of existing cases than what the file actually contains. A count
short of 100 means one of Phase 16, 17, or 18 has not landed yet — do not attempt to backfill their
content yourself; report the gap and wait.

Also confirm `app/src/data/lessonInteractions.js` has **118 existing keys** before proceeding: 18
`java-spring-lld/...` + 100 `fde-curriculum/...` (84 from Phases 1-15 + 6 from Phase 16 + 5 from
Phase 17 + 5 from Phase 18). If this count doesn't match, STOP and report the exact count you find.

**After this phase lands successfully, `GetAuthoredFdeLessonContent` will have 104 cases and
`lessonInteractions.js` will have 122 total keys — this completes the entire ~104-lesson FDE core
curriculum (all 8 numbered modules plus the Prerequisite module). There is no Phase 20.**

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-19-system-design-capstone-content.md`

This file contains 4 lessons — the **final 4 lessons** of Module 8 ("8. System Design, Capstone &
Hiring Readiness"), lessons 11-14 of 14, which completes both the module and the entire FDE
curriculum. Each lesson has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 4 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 11 | Capstone Demo Day: Client Panel Presentation | `11-capstone-demo-day-client-panel-presentation` | 9 |
| 12 | Interview Readiness & Career Launch | `12-interview-readiness-and-career-launch` | 8 |
| 13 | FDE Mock Engagement: Full Simulation | `13-fde-mock-engagement-full-simulation` | 9 |
| 14 | Graduation Review: Portfolio Defense & Next Steps | `14-graduation-review-portfolio-defense-and-next-steps` | 6 |

Total MCQs across all 4 lessons: **32**.

Module slug for all 4: `system-design-capstone`. This module (module 8) is now complete at 14/14
lessons: lessons 1-5 from Phase 17, lessons 6-10 from Phase 18, lessons 11-14 from this phase.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 100 existing cases
followed by `_ => null`. Add 4 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 100 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 100 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 4 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/system-design-capstone/{lesson-slug}'
```

e.g. `'fde-curriculum/system-design-capstone/11-capstone-demo-day-client-panel-presentation'`

Do NOT touch any existing key — 18 `java-spring-lld/...` + 100 `fde-curriculum/...` = **118 total
existing keys** already present. After this phase, the file should have **122 total keys** (118 +
4 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-system-design-capstone-{lesson-number:00}-concept-check-{01|02}` (lesson-number is
11-14 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase `correctOptionId`.
Never add `initialSelectedOption` or `initialSubmitted`.

Suggested picks (use judgment, these are strong candidates — not a requirement to match exactly):
- Lesson 11: the panel-triage concept (Q1 or Q2) and the spine-consistency concept (Q3 or Q8).
- Lesson 12: the behavioral-question-reasoning concept (Q1 or Q2) and the T-shape/defensible-depth
  concept (Q3 or Q4).
- Lesson 13: the compressed-discovery-triage concept (Q2) and the honest-evidence-gap pushback
  concept (Q5).
- Lesson 14: the depth-over-breadth portfolio concept (Q1) and the specificity-diagnostic concept
  (Q6).

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 4 lessons.

None of these 4 lessons qualify. Lesson 11 (panel demo) and lesson 13 (mock engagement) are
communication/judgment scenarios best conveyed in prose, not a system flow — there is no
multi-actor async flow, decorator chain, or runtime-branching pattern to diagram; the "flow" is a
live conversation, not a request/response architecture. Lesson 12 (interview prep) and lesson 14
(portfolio review) have no system architecture content at all. **Omit `architecture` for all 4
lessons.** If in doubt, omit — a diagram is not required for this phase to be complete, and none of
these lessons pass the inclusion test.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-system-design-capstone-{lesson-number:00}-mcq-{01, 02, ...}`. None of this phase's
questions need a `codeBlock` field — omit it; none of the 32 questions reference multi-line code or
a "what does this print" style prompt.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 4 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 100 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (118 total from Phases 1-18)
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
Full method body — all 104 cases now present (100 existing unchanged, 4 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 118 existing entries unchanged, plus the 4 new entries for this phase
(122 total).

### OUTPUT C: Architecture diagram decisions
For each of the 4 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: all 4 omitted — none contain a multi-actor async flow, decorator
chain, or runtime-branching pattern; each is a communication, interview-prep, or reflective
scenario better conveyed in prose.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

### OUTPUT E: Final curriculum-completion confirmation
State the final totals explicitly: "`GetAuthoredFdeLessonContent` now has 104 cases.
`lessonInteractions.js` now has 122 total keys (18 java-spring-lld + 104 fde-curriculum). Module 8
('8. System Design, Capstone & Hiring Readiness') is now complete at 14/14 lessons. This completes
the entire FDE core curriculum — all 8 numbered modules plus the Prerequisite module."

---

## 7. Operational note — database reset required (final reset of the project)

These 4 lessons likely already exist in the database with thin, machine-templated `ContentBody`.
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '11-capstone-demo-day-client-panel-presentation',
  '12-interview-readiness-and-career-launch',
  '13-fde-mock-engagement-full-simulation',
  '14-graduation-review-portfolio-defense-and-next-steps'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

**This completes Module 8 ("8. System Design, Capstone & Hiring Readiness") at 14/14 lessons, and
with it, the entire FDE core curriculum — all 8 numbered modules plus the Prerequisite module,
roughly 104 lessons in total. This is the final SQL reset and the final API restart of the whole
FDE content-authoring project.** There are no further phases planned after this one.

---

## 8. Post-ingestion checklist

- [ ] All 4 new cases added to `GetAuthoredFdeLessonContent`, after the 100 existing cases, before
      `_ => null` (104 total)
- [ ] `lessonInteractions.js` has 4 new `fde-curriculum/system-design-capstone/...` keys; all 118
      pre-existing keys unchanged (122 total)
- [ ] Ran the SQL reset for all 4 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 11-14 of "8. System Design,
      Capstone & Hiring Readiness" render real authored content, and that the module now shows
      14/14 lessons with authored content, not placeholder/draft
- [ ] Spot-checked at least 2 of the 4 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this, but verify none were dropped or duplicated
      during transcription
- [ ] Confirmed the entire `fde-curriculum` pathway now shows all 8 numbered modules plus the
      Prerequisite module with authored (non-placeholder) content across all lessons — this is the
      final verification that the whole ~104-lesson FDE curriculum is complete
