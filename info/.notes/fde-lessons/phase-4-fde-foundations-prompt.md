# Prompt for Local LLM — FDE Phase 4: FDE Foundations (Module 1), Lessons 7-12 of 12 (module complete)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-4-fde-foundations-content.md` in full, and report back what
lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim, exactly as Phase 1-3 did successfully. If you cannot read the file, or if
what you find doesn't match what this prompt describes, STOP and report the discrepancy instead
of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 17 existing cases (11 from the `agentic-ai-core` module, Phases 1-2, plus 6
from the `fde-foundations` module, Phase 3: `01-the-fde-role-customer-embedded-engineering`
through `06-oop-concurrency-and-async-python`) before `_ => null`. If those aren't there, STOP —
Phase 3 must be applied first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-4-fde-foundations-content.md`

This file contains 6 lessons, completing Module 1 ("FDE Foundations: Python, Workflow &
Delivery"), lessons 7-12 of 12. Each has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->`
… `<!-- CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!--
MCQ_SECTION_END -->` block with 8 structured `QUESTION_BLOCK`s per lesson.

The 6 lessons, in order, with their exact database slugs:

| # | Lesson title | Lesson slug (use exactly) |
|---|---|---|
| 7 | Pydantic v2, Structured Logging & Profiling | `07-pydantic-v2-structured-logging-and-profiling` |
| 8 | Git Internals, GitHub Workflows & AI Dev Tools (Cursor, Claude Code, MCP) | `08-git-internals-github-workflows-and-ai-dev-tools-cursor-claude-code-mcp` |
| 9 | Testing: pytest, Property-Based Testing & CI | `09-testing-pytest-property-based-testing-and-ci` |
| 10 | Software Engineering Best Practices (SOLID, Hexagonal Architecture) | `10-software-engineering-best-practices-solid-hexagonal-architecture` |
| 11 | Linux, Shell & Scripting for FDEs | `11-linux-shell-and-scripting-for-fdes` |
| 12 | Assessment: Python Engineering Challenge | `12-assessment-python-engineering-challenge` |

Module slug for all 6: `fde-foundations` (same module Phase 3 used — this completes it, 12 of
12 lessons total).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 17 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 17 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Note: Lesson 12 ("Assessment: Python Engineering Challenge") has a slightly different internal
structure than a normal lesson — its `## Practical Backend Scenario` section is short (the
assessment IS the scenario) and it ends with a `## Self-Assessment Questions` sub-heading right
before the chapter-body closing marker. Copy it exactly as it appears between the markers, same
as any other lesson — do not restructure it to match the other lessons' shape.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 17 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/fde-foundations/{lesson-slug}'
```

e.g. `'fde-curriculum/fde-foundations/07-pydantic-v2-structured-logging-and-profiling'`

Do NOT touch any existing key — this includes the 22 `java-spring-lld/...` keys, the 11
`fde-curriculum/agentic-ai-core/...` keys, and the 6 `fde-curriculum/fde-foundations/...` keys
already present from Phase 3.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before. `id` pattern:
`lesson-fde-fde-foundations-{lesson-number:00}-concept-check-{01|02}` (lesson-number is 07-12 for
this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase `correctOptionId`. Never add
`initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from prior phases hold. Lesson 10 (SOLID/Hexagonal
Architecture) is the most likely candidate in this batch — a ports-and-adapters diagram (core
logic in the center, a `DeviceRepository` port, two adapters plugged into it) could genuinely
show something the prose doesn't. Otherwise default to omitting the `architecture` key.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern `lesson-fde-fde-foundations-{lesson-number:00}-mcq-{01,
02, ...}`. None of this phase's questions need a `codeBlock` field (no embedded multi-line code
in this batch's MCQs) — omit it.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS
data field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise, including lesson 12 (the assessment lesson is
self-contained content with a rubric, not a submitted coding exercise — this platform's
`exercises/` infrastructure is out of scope for FDE lessons for now). Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 17 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 `java-spring-lld/...` + 11
  `fde-curriculum/agentic-ai-core/...` + 6 `fde-curriculum/fde-foundations/...`)
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
Full method body — all 23 cases now present (17 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 39 existing entries unchanged, plus the 6 new entries for this phase
(45 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons already exist in the database with non-empty, generic `ContentBody`. After
applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '07-pydantic-v2-structured-logging-and-profiling',
  '08-git-internals-github-workflows-and-ai-dev-tools-cursor-claude-code-mcp',
  '09-testing-pytest-property-based-testing-and-ci',
  '10-software-engineering-best-practices-solid-hexagonal-architecture',
  '11-linux-shell-and-scripting-for-fdes',
  '12-assessment-python-engineering-challenge'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes Module 1 ("FDE Foundations: Python, Workflow & Delivery") — all 12 lessons
should now have authored content.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 17 existing cases,
      before `_ => null`
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/fde-foundations/...` keys; all 39
      pre-existing keys unchanged
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 12 lessons in "1. FDE Foundations:
      Python, Workflow & Delivery" render real authored content
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file (not
      rewritten/paraphrased), concept checks not pre-answered on load, practice questions render
      at the bottom
