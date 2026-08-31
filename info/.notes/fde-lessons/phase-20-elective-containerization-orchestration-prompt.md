# Prompt for Local LLM — FDE Phase 20: Elective — Containerization and Orchestration (Lessons 1-6 of 17)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-20-elective-containerization-orchestration-content.md` in full, and
report back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not
paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies and
MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match what
this prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

This is the **first phase of a new elective batch**. The entire ~104-lesson core FDE curriculum
(Prerequisite + Modules 1-8) is already complete and applied. This phase does not touch any of it —
it adds the first 6 lessons of the first of three brand-new elective modules on top.

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **exactly 104 existing cases** before `_ => null`.

**If the case count is anything other than 104, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains. A short count
most likely means an earlier authored-but-unapplied phase (16-19) has not actually been applied
yet — do not paper over that; report it.

Also confirm `app/src/data/lessonInteractions.js` has **exactly 122 existing keys** before
proceeding: 18 `java-spring-lld/...` + 104 `fde-curriculum/...`. If this count doesn't match, STOP
and report the exact count you find.

Also confirm `api/Data/FdeCurriculumSeedData.cs` contains a `SupplementalModuleDefinition` for
`elective-containerization-orchestration` inside a `SupplementalModules` collection, and an
`EnsureSupplementalModules` method that calls `GetAuthoredFdeLessonContent(lessonSlug) ??
BuildSupplementalLessonContent(...)` for each of its lessons — this is the same override
mechanism the 104 core cases already use, applied to a `SupplementalModuleDefinition` instead of a
numbered core module. If this module definition or mechanism is not present, STOP and report what
you find instead of inventing a different wiring approach.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-20-elective-containerization-orchestration-content.md`

This file contains 6 lessons — **lessons 1-6 of 17** in a brand-new elective module,
"Containerization and Orchestration" (`elective-containerization-orchestration`). This is the
**first of three elective modules** now in scope (Containerization/K8s, 17 lessons; AWS
Multi-Region Cloud Deep Dive, 17 lessons; Storage, Networking & Reliability for FDEs, 14 lessons).
A later phase (21) covers this module's lessons 7-12, and Phase 22 covers lessons 13-17, completing
it — do not add placeholder content for those 11 lessons in this phase.

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s. Several MCQ blocks in this phase also carry an extra
**`CODE_BLOCK:`** field between `QUESTION_TEXT` and `OPTIONS` — a fenced code/CLI-output snippet
the question refers to. This maps to the `codeBlock` field on the corresponding
`practiceQuestions` entry in `lessonInteractions.js` (see §3c below).

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 1 | Docker Introduction | `01-docker-introduction` | 8 |
| 2 | Docker Images and Containers | `02-docker-images-and-containers` | 8 |
| 3 | Building Your Own Docker Image | `03-building-your-own-docker-image` | 9 |
| 4 | Images and Containers Deep Dive | `04-images-and-containers-deep-dive` | 9 |
| 5 | Docker Volumes | `05-docker-volumes` | 8 |
| 6 | Docker Networking Deep Dive | `06-docker-networking-deep-dive` | 9 |

Total MCQs across all 6 lessons: **51**.

Module slug for all 6: `elective-containerization-orchestration` (this is a brand-new
`SupplementalModuleDefinition` — this is its first phase; later phases add lessons 7-17 to the
same module, completing it at 17 total).

Double-check each slug against `Slugify(lessonDefinition.Title)` yourself before using it: lowercase,
`&`→` and `, `+`→` plus `, everything else non-alphanumeric collapsed to `-`, trimmed. All 6 titles
in this phase slugify exactly as shown in the table above with no `&`/`+` characters involved.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 104 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 104 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's `<!-- CHAPTER_BODY_START -->` / `<!-- CHAPTER_BODY_END -->`
  markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 104 existing
cases already in place. Do NOT modify `SupplementalModules`, `EnsureSupplementalModules`,
`Slugify`, `BuildSupplementalLessonContent`, or any other method — this phase only adds switch
cases to `GetAuthoredFdeLessonContent`.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/elective-containerization-orchestration/{lesson-slug}'
```

e.g. `'fde-curriculum/elective-containerization-orchestration/01-docker-introduction'`

This is the same key pattern as every core module (`fde-curriculum/{module-slug}/{lesson-slug}`) —
`elective-containerization-orchestration` is just another module slug under the same
`fde-curriculum` course; there is no separate "electives" namespace in this file.

Do NOT touch any existing key — 18 `java-spring-lld/...` + 104 `fde-curriculum/...` = **122 total
existing keys** already present. After this phase, the file should have **128 total keys** (122 +
6 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Pick the two most non-trivial, misconception-prone points from each lesson — favor a point with a
genuine, plausible wrong answer over a fact the learner just read verbatim. Good candidates already
in the source content: Lesson 1 — the PID-namespace diagnostic (`docker run --rm alpine sh -c
'echo $$; cat /proc/1/comm'` reporting PID 1) or the `--pid=host` trade-off; Lesson 3 — exec form
vs shell form for `CMD`/`ENTRYPOINT`; Lesson 4 — the PID 1 problem (no automatic init behavior) or
distinguishing exit code 137 from 143; Lesson 6 — `EXPOSE` vs an actual published port. Use your
own judgment for lessons 2 and 5 following the same "genuine misconception, not verbatim recall"
bar. `id` pattern:
`lesson-fde-elective-containerization-orchestration-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 01-06 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons: (1) the
flow must be genuinely non-obvious from prose alone, (2) it must show something the Practical
Backend Scenario prose does not already cover, (3) it must give a 7-8 year developer a faster
mental model than another paragraph would.

None of this phase's 6 lessons meet this bar. Lessons 1, 2, 3, and 5 are single-actor,
single-container mechanism lessons (isolation mechanics, image/container relationship, Dockerfile
authoring, volume mounting) with no multi-actor or async flow to diagram. Lesson 4's PID 1/signal
material is a single-process mechanism, not a multi-actor flow. Lesson 6 is the closest candidate —
it does involve multiple containers (`ticket-api`, `ticket-db`) and a network boundary — but its
Concepts Covered and code block already lay out the exact topology (two containers, one shared
network, one published port) as clearly as a diagram would, so it does not clear bar (2). **Omit
`architecture` for all 6 lessons in this phase.** If you judge one differently, state your
reasoning in Output C below rather than silently including it.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-elective-containerization-orchestration-{lesson-number:00}-mcq-{01, 02, ...}`.

Several questions in the source file carry a `**CODE_BLOCK:**` field (a fenced snippet) between
`QUESTION_TEXT` and `OPTIONS` — for those questions only, add a `codeBlock` field to the
`practiceQuestions` entry containing that exact snippet (preserve its formatting, including
newlines), and keep `question` as pure prose per §8a's rule. Questions with no `CODE_BLOCK` field
in the source get no `codeBlock` field in the JS object — do not invent one.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 104 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, `SupplementalModules`,
  `EnsureSupplementalModules`, or any other method in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (122 total, pre-existing)
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
Full method body — all 110 cases now present (104 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 122 existing entries unchanged, plus the 6 new entries for this phase
(128 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: all 6 omitted (single-actor mechanism lessons, or — for Lesson 6 —
a topology already fully covered by the prose and code block).

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons likely already exist in the database with thin, machine-templated `ContentBody`
(from `BuildSupplementalLessonContent`'s skeleton-expansion, not this phase's authored content).
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-docker-introduction',
  '02-docker-images-and-containers',
  '03-building-your-own-docker-image',
  '04-images-and-containers-deep-dive',
  '05-docker-volumes',
  '06-docker-networking-deep-dive'
);
```

**Note:** these slugs are not globally unique across modules in this schema if any other module
happens to reuse the same numbering and title-derived slug — if your `lessons` table has a
composite or module-scoped uniqueness constraint, scope this `UPDATE` by joining to the module
(`elective-containerization-orchestration`) explicitly instead of relying on `slug` alone; check
the schema before running this if you have any doubt.

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the first 6 of 17 lessons in the "Containerization and Orchestration" elective
module. Lessons 7-17 remain for Phases 21 and 22 — neither is in scope for this phase.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 104 existing cases, before
      `_ => null` (110 total)
- [ ] `lessonInteractions.js` has 6 new
      `fde-curriculum/elective-containerization-orchestration/...` keys; all 122 pre-existing keys
      unchanged (128 total)
- [ ] Ran the SQL reset for all 6 slugs (scoped to the elective module if the schema requires it),
      then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed the "Containerization and Orchestration"
      elective module appears with lessons 1-6 rendering real authored content (Dockerfile/CLI
      code blocks visible in the chapter body), and lessons 7-17 still show
      placeholder/skeleton-expanded content pending future phases
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim
      (including fenced code blocks), concept checks not pre-answered on load, practice questions
      render at the bottom, and any question with a `codeBlock` renders it as a dark monospace
      block between the question text and the options
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this (all 51 MCQs verified programmatically:
      exactly 4 options each, correct-answer key/index/marked-option all consistent), but verify
      none were dropped or duplicated during transcription
