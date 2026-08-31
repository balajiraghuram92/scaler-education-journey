# Prompt for Local LLM — FDE Phase 8: Full-Stack FDE (Module 3), Lessons 1-5 of 5 (module complete)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-8-full-stack-ai-frontends-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 38 existing cases (11 `agentic-ai-core` + 12 `fde-foundations` + 15
`backend-observability-data`, covering Phases 1-7) before `_ => null`. If those aren't there,
STOP — Phase 7 must be applied first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-8-full-stack-ai-frontends-content.md`

This file contains 5 lessons, completing Module 3 ("3. Full-Stack FDE: TypeScript, React &
AI-First Frontends"), lessons 1-5 of 5 (this module has exactly 5 lessons total, so this single
phase covers the whole module). Each has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` …
`<!-- CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->`
block with 8-9 structured `QUESTION_BLOCK`s per lesson.

The 5 lessons, in order, with their exact database slugs:

| # | Lesson title | Lesson slug (use exactly) |
|---|---|---|
| 1 | TypeScript Fundamentals for Python Engineers | `01-typescript-fundamentals-for-python-engineers` |
| 2 | React Essentials for AI Apps | `02-react-essentials-for-ai-apps` |
| 3 | Next.js for Full-Stack AI Apps | `03-next-js-for-full-stack-ai-apps` |
| 4 | Vercel AI SDK & Streaming UIs | `04-vercel-ai-sdk-and-streaming-uis` |
| 5 | AI Product UX & Customer-Facing Polish | `05-ai-product-ux-and-customer-facing-polish` |

Module slug for all 5: `full-stack-ai-frontends` (a new module — this is its first and only
phase, 5 of 5 lessons total).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 38 existing cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 38 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Note: several lessons in this phase include fenced TypeScript/TSX code blocks inside `##
Concepts Covered` (and one inside `## Practical Backend Scenario` for Lesson 5). Copy these
exactly as written, including the triple-backtick fences and language tags — they are real code,
not pseudocode, and must not be reformatted or re-indented.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 38 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/full-stack-ai-frontends/{lesson-slug}'
```

e.g. `'fde-curriculum/full-stack-ai-frontends/01-typescript-fundamentals-for-python-engineers'`

Do NOT touch any existing key — 22 `java-spring-lld/...`, 11 `fde-curriculum/agentic-ai-core/...`,
12 `fde-curriculum/fde-foundations/...`, and 15 `fde-curriculum/backend-observability-data/...`
(60 total, from Phases 1-7) already present.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two points in each lesson most likely to be
misunderstood or conflated with something from an earlier module, not the most trivially
recalled fact. `id` pattern:
`lesson-fde-full-stack-ai-frontends-{lesson-number:00}-concept-check-{01|02}` (lesson-number is
01-05 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase `correctOptionId`.
Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from prior phases hold (non-obvious flow, shows something the
prose doesn't, faster mental model than another paragraph). Lesson 4 (Vercel AI SDK & Streaming
UIs) is the most plausible candidate this phase — a diagram contrasting the request/response
shape of a normal `fetch`-and-JSON round trip against the `streamText` → route handler →
`useChat` token-by-token push could show the streaming boundary more clearly than prose alone.
Lesson 3 (Next.js server/client component boundary) is a second plausible candidate — a diagram
showing which parts of the component tree run server-side (with access to the internal API
token) versus client-side (shipped as JavaScript) could also pass the test. Evaluate both
against the inclusion criteria before including either; if neither clearly earns its place
independently, default to omitting `architecture` for both, matching the established convention
in every prior phase of including at most one diagram only when it's genuinely earned. Do not
add a diagram to any of Lessons 1, 2, or 5 — none of them involve a non-obvious flow.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-full-stack-ai-frontends-{lesson-number:00}-mcq-{01, 02, ...}`. None of this phase's
questions need a `codeBlock` field — omit it; the MCQ text refers to code shown in the chapter
body prose rather than asking the learner to read a fresh snippet inline in the question itself.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS
data field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 38 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 + 11 + 12 + 15 = 60 total)
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
Full method body — all 43 cases now present (38 existing unchanged, 5 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 60 existing entries unchanged, plus the 5 new entries for this phase
(65 total).

### OUTPUT C: Architecture diagram decisions
For each of the 5 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. For Lessons 3 and 4 in particular, state explicitly which of the two
candidate diagrams (if either) was included, since only one lesson in this phase should end up
with an `architecture` key per the established one-diagram-per-phase convention, and only if it
genuinely earns it.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 5 lessons may already exist in the database with placeholder/generic `ContentBody` from the
module's initial machine-templated seeding. After applying the code changes and restarting the
API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-typescript-fundamentals-for-python-engineers',
  '02-react-essentials-for-ai-apps',
  '03-next-js-for-full-stack-ai-apps',
  '04-vercel-ai-sdk-and-streaming-uis',
  '05-ai-product-ux-and-customer-facing-polish'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes Module 3 ("3. Full-Stack FDE: TypeScript, React & AI-First Frontends") — all 5
lessons should now have authored content.

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 38 existing cases,
      before `_ => null`
- [ ] `lessonInteractions.js` has 5 new `fde-curriculum/full-stack-ai-frontends/...` keys; all
      60 pre-existing keys unchanged
- [ ] Ran the SQL reset for all 5 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 5 lessons in "3. Full-Stack FDE:
      TypeScript, React & AI-First Frontends" render real authored content
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim
      (including fenced code blocks rendering correctly), concept checks not pre-answered on
      load, practice questions render at the bottom
- [ ] Confirmed at most one lesson in this phase ended up with an `architecture` key, and only
      if it genuinely passed the inclusion test
