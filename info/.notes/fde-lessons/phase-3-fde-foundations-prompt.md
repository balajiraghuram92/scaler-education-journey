# Prompt for Local LLM — FDE Phase 3: FDE Foundations (Module 1), Lessons 1-6 of 12

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files following the
exact mechanism used successfully in Phases 0-2. If any step below doesn't match what you find
in the actual files, STOP and report the discrepancy instead of guessing.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 11 existing cases (`01-genai-world-and-llm-landscape` through
`11-debugging-ai`, all inside the `agentic-ai-core` module, from Phases 1-2) before `_ => null`.
If those aren't there, STOP — Phases 1-2 must be applied first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-3-fde-foundations-content.md`

This file contains 6 lessons, the first half of Module 1 ("FDE Foundations: Python, Workflow &
Delivery"), each with a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->`
block with 8-9 structured `QUESTION_BLOCK`s per lesson.

**Important — this is a different module from Phases 1-2.** These 6 lessons belong to module
slug `fde-foundations`, NOT `agentic-ai-core`. Use the correct module slug in every
`lessonInteractions.js` key below.

The 6 lessons, in order, with their exact database slugs (already computed via this project's
`Slugify()` — use these exact strings, do not recompute):

| # | Lesson title | Lesson slug (use exactly) |
|---|---|---|
| 1 | The FDE Role: Customer-Embedded Engineering | `01-the-fde-role-customer-embedded-engineering` |
| 2 | Problem Discovery & Solution Thinking for FDEs | `02-problem-discovery-and-solution-thinking-for-fdes` |
| 3 | Python Toolchain & Environment Setup (pyenv, uv, ruff, mypy) | `03-python-toolchain-and-environment-setup-pyenv-uv-ruff-mypy` |
| 4 | Iterators, Generators & Comprehensions | `04-iterators-generators-and-comprehensions` |
| 5 | Closures, Decorators & Context Managers | `05-closures-decorators-and-context-managers` |
| 6 | OOP, Concurrency & Async Python | `06-oop-concurrency-and-async-python` |

Module slug for all 6: `fde-foundations`

**Note on slug collision:** these lesson slugs (`01-...` through `06-...`) are numerically the
same prefixes as the Phase 1 lessons, but they live in a DIFFERENT module (`fde-foundations` vs
`agentic-ai-core`), so the full lesson slugs are different strings (e.g.
`01-the-fde-role-customer-embedded-engineering` vs `01-genai-world-and-llm-landscape`) and the
`GetAuthoredFdeLessonContent` switch is keyed on lesson slug alone — confirm none of these 6 new
case strings collide with any of the 11 existing ones before adding them (they don't, but verify
by reading the existing cases first).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 11 existing cases
(Phases 1-2) followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above,
**immediately before** `_ => null` (after the existing 11 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 11 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/fde-foundations/{lesson-slug}'
```

e.g. `'fde-curriculum/fde-foundations/01-the-fde-role-customer-embedded-engineering'`

Note the module segment is `fde-foundations`, not `agentic-ai-core` — this is a new module.

Do NOT touch any existing key — this includes the 22 `java-spring-lld/...` keys and all 11
`fde-curriculum/agentic-ai-core/...` keys from Phases 1-2.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before (application/misconception over recall; plausible distractors;
central concept; would stump a skimmer). `id` pattern:
`lesson-fde-fde-foundations-{lesson-number:00}-concept-check-{01|02}` (lesson-number is 01-06 for
this phase, within the `fde-foundations` module). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to
lowercase `correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from prior phases hold (non-obvious flow, shows something the
prose doesn't, faster mental model than re-reading). None of these 6 lessons obviously need one
— they're conceptual/process (lessons 1-2) or Python-mechanism lessons (3-6) better served by
code than a system diagram. Default to omitting the `architecture` key for this phase unless you
find a specific case where the test genuinely passes.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern `lesson-fde-fde-foundations-{lesson-number:00}-mcq-{01,
02, ...}`. Some of this phase's questions include a multi-line code snippet in the
`QUESTION_TEXT` (lessons 4, 5, 6 — iterators/generators, closures, and concurrency questions
reference short code blocks like the `groupby` example, the closure loop-lambda example, and the
`time.sleep` vs `asyncio.sleep` comparison). For any question where the source's `QUESTION_TEXT`
contains an embedded multi-line code snippet, extract that snippet into the `codeBlock` field and
leave `question` as pure prose introducing it (e.g. "What does the following code print?"),
per the standard convention. Questions with only a short inline identifier or single-line
reference stay as prose with backtick-formatted inline code — do not add `codeBlock` for those.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS
data field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry for this phase.

---

## 5. Constraints

Do NOT touch:
- Any of the 11 existing cases in `GetAuthoredFdeLessonContent` from Phases 1-2
- `BuildLessonContent`, `BuildSupplementalLessonContent`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 `java-spring-lld/...` + 11
  `fde-curriculum/agentic-ai-core/...`)
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
Full method body — all 17 cases now present (11 from Phases 1-2 unchanged, 6 new from this
phase), before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 33 existing entries unchanged, plus the 6 new entries for this phase
(39 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason.

### OUTPUT D: codeBlock usage
List which specific questions (by lesson and question number) received a `codeBlock` field and
which snippet each one contains, so this can be spot-checked against the source file.

### OUTPUT E: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons already exist in the database with non-empty, generic `ContentBody`. After
applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-the-fde-role-customer-embedded-engineering',
  '02-problem-discovery-and-solution-thinking-for-fdes',
  '03-python-toolchain-and-environment-setup-pyenv-uv-ruff-mypy',
  '04-iterators-generators-and-comprehensions',
  '05-closures-decorators-and-context-managers',
  '06-oop-concurrency-and-async-python'
);
```

**Note:** this `WHERE slug IN (...)` clause matches by slug alone, and these slugs happen to
share the `01-` through `06-` numeric prefix pattern with Phase 1's `agentic-ai-core` lessons —
but the actual slug strings are entirely different (e.g.
`01-the-fde-role-customer-embedded-engineering` vs `01-genai-world-and-llm-landscape`), so this
reset will only affect the 6 `fde-foundations` module lessons targeted here. If you want to be
extra certain, you can instead join through the module to scope the reset explicitly:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE module_id = (
  SELECT id FROM course_modules WHERE slug = 'fde-foundations'
)
AND slug IN (
  '01-the-fde-role-customer-embedded-engineering',
  '02-problem-discovery-and-solution-thinking-for-fdes',
  '03-python-toolchain-and-environment-setup-pyenv-uv-ruff-mypy',
  '04-iterators-generators-and-comprehensions',
  '05-closures-decorators-and-context-managers',
  '06-oop-concurrency-and-async-python'
);
```
(Adjust the table/column names above if `course_modules`/`module_id` differ from this project's
actual schema — check `api/Models/` if unsure before running either version.)

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 11 existing cases, before
      `_ => null`
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/fde-foundations/...` keys; all 33
      pre-existing keys unchanged
- [ ] Ran the SQL reset scoped correctly to the `fde-foundations` module's first 6 lessons, then
      restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed the first 6 lessons in "1. FDE
      Foundations: Python, Workflow & Delivery" render real authored content
- [ ] Confirmed the remaining 6 lessons in that module (7-12) still show the old generic content
      (expected — they're Phase 4's job, not this phase's)
- [ ] Spot-checked at least 2 of the 6 new lessons: concept checks not pre-answered on load,
      practice questions render at the bottom, and any code-block questions render the snippet
      correctly
