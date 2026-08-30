# STRICT PROMPT — Migrate all flat-text MCQs into the interactive Practice Questions UI

Read this entire document before touching any file. Follow every rule exactly. Where a
rule gives a choice, make the choice explicitly stated — do not improvise a different one.
This is a mechanical transformation task, not a rewriting task: **you must not paraphrase,
reword, shorten, or "improve" any question, option, or explanation text.** Copy it verbatim
from the source, changing only what these rules explicitly require you to change (quote
escaping, whitespace normalization for JS string literals, and the two content changes
named in Rule 6).

## Why this migration is happening

This codebase has two independent MCQ-rendering mechanisms:

1. **`app/src/data/lessonInteractions.js`** — a hand-authored JS object keyed by
   `"{courseSlug}/{moduleSlug}/{lessonSlug}"`. Each entry can have a `conceptChecks` array
   and/or a `practiceQuestions` array. This renders as the polished interactive widget:
   radio-button options, a "PRACTICE — N QUESTIONS" header, and reveal-on-select feedback.
   Consumed by `app/src/components/learning/PracticeQuestions.jsx` and
   `app/src/components/learning/ConceptCheck.jsx`.
2. **Flat `## Self-Check (From Class Material)` markdown blocks** inside each lesson's
   `ContentBody` string, defined in `api/Data/JavaVerticalSeedData.cs`'s
   `GetAuthoredLessonContent` method. This renders as static, non-interactive text.

Only lessons 1–4 currently use mechanism #1. Thirteen lessons (listed in Rule 2) have real,
correctly-sourced MCQs trapped in mechanism #2. The task: port every one of those 95
questions into mechanism #1, matching the existing shape and conventions exactly, then
remove the now-redundant flat text from `ContentBody` so each MCQ appears exactly once, in
the interactive widget, consistently across every lesson.

## Files you will modify

1. `app/src/data/lessonInteractions.js` — add a `practiceQuestions` array to 13 existing
   entries (12 of which do not exist yet in the object and must be added; lesson 4 already
   exists with a `conceptChecks` array only — add `practiceQuestions` alongside it, do not
   touch its existing `conceptChecks` or `architecture` blocks).
2. `api/Data/JavaVerticalSeedData.cs` — remove the `## Self-Check (From Class Material)`
   section (and everything after it, through the end of that lesson's content string) from
   the 13 affected `GetAuthoredLessonContent` cases, once its content has been faithfully
   ported. Change nothing else in this file.

## Rule 1 — Exact source format you are parsing

Inside each affected `GetAuthoredLessonContent` case, the block looks like this (verbatim
example, from the `"09-concurrency-4-semaphores"` case):

```
## Self-Check (From Class Material)

**Q1.** Which of the following statements is true regarding mutex locks and semaphores?
- A. Mutex Locks are used for synchronization while Semaphores is a syntax for creating threads
- B. Mutex Locks allow only 1 thread in critical section while Semaphores can allow multiple threads in the critical section at same time
- C. Lock and unlock are methods of semaphores
- D. Acquire and release are methods of mutex locks

**Answer: B** — A mutex restricts critical section access to at most one thread, whereas a counting semaphore maintains a permit count allowing multiple threads to enter simultaneously up to its capacity limit.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 4; answer determined from source material, not marked in original)*

**Q2.** ...
```

Structure per question, in order:
- A line starting `**Q<n>.**` followed by the question text. The question text may span
  multiple lines and may itself contain a short numbered sub-list (e.g. "Consider the
  following two statements: 1. ... 2. ...") — that sub-list is part of the question text,
  not separate options; keep it inside the `question` field with its numbering intact.
- A blank line, then exactly 4 lines starting `- A.`, `- B.`, `- C.`, `- D.`.
- A blank line, then a line starting `**Answer: <LETTER>**` followed by an em-dash (`—`)
  and the explanation text. The explanation may wrap to a second physical line before the
  paragraph ends — treat it as one continuous string with the line break collapsed to a
  single space.
- Optionally, a line starting `*(SOURCE_TYPE: ...)*` — this is the citation. Do not discard
  it; see Rule 4 for where it goes.
- A blank line separates each question from the next.

Some questions embed a multi-line fenced code block (triple backticks, e.g. ` ```java `)
inside the question text — for example lesson 16's decorator-chain question. See Rule 3 for
how to handle those.

## Rule 2 — Exact scope: 13 lessons, 95 questions total

Migrate exactly these `GetAuthoredLessonContent` cases, and no others. The question count
is given so you can self-check after parsing each one — if your count differs, stop and
recheck your parsing before writing anything.

| Lesson slug | Lesson number (for ids) | Question count |
|---|---|---|
| `04-oop-3-polymorphism-interfaces` | 4 | 4 |
| `05-oop-4-lms-lab` | 5 | 3 |
| `06-concurrency-1-threads` | 6 | 3 |
| `07-concurrency-2-executors` | 7 | 5 |
| `08-concurrency-3-synchronization` | 8 | 5 |
| `09-concurrency-4-semaphores` | 9 | 5 |
| `10-java-adv-1-generics` | 10 | 5 |
| `11-java-adv-2-collections-lab` | 11 | 5 |
| `12-java-adv-3-lambdas-streams` | 12 | 5 |
| `13-java-adv-4-streams-exceptions` | 13 | 4 |
| `14-solid-principles` | 14 | 11 |
| `16-structural-patterns` | 16 | 12 |
| `17-behavioural-patterns-uml` | 17 | 28 |

All 13 of these lessons belong to module slug matching what is already established for
that lesson (lessons 4–13 are under `oop-foundations`, `concurrency-multithreading`, or
`advanced-java-collections` respectively — read each lesson's actual `ModuleId` wiring in
`SeedModule1Lessons`/`SeedModule2Lessons`/`SeedModule3Lessons` to get the exact module slug
right per lesson, do not guess; lessons 14/16/17 are under `design-principles-patterns`).
The full key format is `java-spring-lld/{moduleSlug}/{lessonSlug}`.

Do NOT touch lesson `15-creational-patterns` (it has zero Self-Check questions by design —
no real MCQ material exists for it, confirmed separately; do not invent any) or any lesson
outside this table.

## Rule 3 — Target JSON shape (exact fields, nothing more, nothing less)

Each migrated question becomes one object in that lesson's `practiceQuestions` array:

```js
// SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 4
{
  id: 'lesson-9-mcq-01',
  question: 'Which of the following statements is true regarding mutex locks and semaphores?',
  options: [
    { id: 'a', label: 'A', text: 'Mutex Locks are used for synchronization while Semaphores is a syntax for creating threads' },
    { id: 'b', label: 'B', text: 'Mutex Locks allow only 1 thread in critical section while Semaphores can allow multiple threads in the critical section at same time' },
    { id: 'c', label: 'C', text: 'Lock and unlock are methods of semaphores' },
    { id: 'd', label: 'D', text: 'Acquire and release are methods of mutex locks' }
  ],
  correctOptionId: 'b',
  explanation: 'A mutex restricts critical section access to at most one thread, whereas a counting semaphore maintains a permit count allowing multiple threads to enter simultaneously up to its capacity limit.'
}
```

Field rules:
- `id`: see Rule 5 for the exact naming scheme (it is NOT always `lesson-{n}-mcq-{nn}`).
- `question`: the verbatim question text (collapse internal line breaks to single spaces;
  preserve inline code spans like `` `acquire()` `` as-is — the renderer already handles
  backtick inline code via `formatInline`).
- `options`: always exactly 4 entries, `id` lowercase `a`/`b`/`c`/`d`, `label` uppercase
  `A`/`B`/`C`/`D`, `text` verbatim from the source line (drop the leading `A. ` marker).
- `correctOptionId`: lowercase letter matching the `**Answer: X**` line.
- `explanation`: verbatim text after the em-dash, with the trailing
  `*(SOURCE_TYPE: ...)*` citation **removed from this field** — it goes above the object as
  a `//` comment instead (see Rule 4). Do not lose the citation; just relocate it.
- Do **not** add `incorrectExplanation` or `hint` fields — those belong to `conceptChecks`
  objects only (see the existing `conceptChecks` entries in the file for reference); the
  `PracticeQuestions` component (`app/src/components/learning/PracticeQuestions.jsx`) does
  not read those fields at all, so adding them would be dead data.
- `codeBlock` (optional field, only when the source question contains a fenced code block):
  set it to the exact code content (no triple backticks, no language tag) as a template
  literal or a string with embedded `\n` — match how existing `codeBlock` fields in the
  file are written (see `lesson-3-mcq-09` and `lesson-3-mcq-10` for the exact pattern:
  ```js
  codeBlock: 'public class Car extends Vehicle {\n    private static final double PER_KM_RATE = 15.0;\n...}',
  ```
  placed as a property directly after `question`). When present, strip the fenced code
  block out of the `question` text itself so it is not duplicated in both places.

## Rule 4 — Source-type comment convention

Immediately above each question object in the array, add a one-line comment in this exact
form, matching the existing convention already used elsewhere in this same file for lessons
1–3 (see `// Q1 — FROM_MATERIAL`, `// Q6 — LLM_GENERATED` near line 445 and 519):

```js
// SOURCE_TYPE: FROM_MATERIAL — <citation text from the original *(SOURCE_TYPE: ...)* line, minus the "FROM_MATERIAL — " prefix if it is already implied, keep it exactly as it reads>
```

If a question in the source has no `*(SOURCE_TYPE: ...)*` line at all, write
`// SOURCE_TYPE: FROM_MATERIAL — Scaler class material (citation not recorded)` instead of
inventing a fabricated citation — do not guess a source.

## Rule 5 — Exact `id` naming scheme (avoids future collisions)

Module 6 (`spring-enterprise-architecture`) reuses lesson **numbers** 14, 15, 16, 17 for a
completely different set of lessons (Spring Boot Core, Spring Data JPA, REST APIs, Capstone)
that do not currently have any MCQs but might in the future. To avoid an id collision if
that ever happens, use this scheme:

- Lessons 4–13 (numbers do not repeat anywhere else in the course): `lesson-{n}-mcq-{nn}`,
  e.g. `lesson-9-mcq-01`, `lesson-9-mcq-02`, ... — exactly matching the existing pattern
  used for lessons 1–3 in this same file.
- Lesson 14 (`14-solid-principles`): `lesson-14-solid-mcq-{nn}`
- Lesson 16 (`16-structural-patterns`): `lesson-16-structural-mcq-{nn}`
- Lesson 17 (`17-behavioural-patterns-uml`): `lesson-17-behavioural-mcq-{nn}`

`{nn}` is a two-digit, zero-padded sequence number starting at `01`, in the same order the
questions appear in the source (`Q1` → `01`, `Q2` → `02`, etc. — do not renumber or reorder).

## Rule 6 — The only two content changes you are allowed to make

1. Relocate the `*(SOURCE_TYPE: ...)*` citation from inline explanation text to a `//`
   comment above the object (Rule 4) — this is a relocation, not a content change to the
   substance of the explanation.
2. Strip a fenced fenced code block out of `question` text into a separate `codeBlock`
   field when present (Rule 3).

Everything else — every word of every question, option, and explanation — must match the
source exactly. Do not fix typos you notice in the source, do not rephrase awkward
sentences, do not shorten anything. If you believe something in the source is wrong, leave
it as-is and do not silently correct it.

## Rule 7 — JS string literal quoting

Match the file's existing convention: prefer single-quoted strings (`'...'`); when the text
itself contains an apostrophe (e.g. "Car's constructor"), either escape it (`\'`) or switch
that one string to double quotes — look at how nearby existing entries in the same file
handle this (both styles appear; pick whichever the immediately surrounding code already
uses, for consistency within the file, not a global rule). Never leave an unescaped
apostrophe that would break the string literal.

## Rule 8 — Where to insert new entries in `lessonInteractions.js`

Add each new lesson's object as a new top-level key in the `lessonInteractions` object,
following the exact same structural pattern as the existing entries (see lines 2–650 of the
current file for the pattern). For lesson 4, which already exists, add the
`practiceQuestions` key as a sibling of the existing `conceptChecks` and `architecture` keys
inside that same object — do not create a duplicate top-level key for lesson 4.

Insertion order within the object does not need to match lesson number, but keep each
lesson's entry contiguous and do not scatter one lesson's data across multiple locations in
the file.

## Rule 9 — Removing the flat Self-Check block from `JavaVerticalSeedData.cs`

For each of the 13 lessons in Rule 2's table, after (and only after) you have verified the
question count and content match what you migrated into `lessonInteractions.js`, remove
from that lesson's `ContentBody` string:

- The `## Self-Check (From Class Material)` heading line, and
- everything after it through the end of that lesson's content (the closing `"` of the
  verbatim string for that `GetAuthoredLessonContent` case).

Verify before deleting that nothing else follows the Self-Check section in that lesson's
content (in every lesson checked so far, Self-Check is the final section, after
`## Suggested Extension` — but confirm this per lesson rather than assuming; if you find an
exception, stop and describe what you found instead of guessing what to do with it).

Do not touch `## Concepts Covered`, `## Practical Backend Scenario`, `## Practice Loop`,
`## Evidence of Understanding`, or `## Suggested Extension` in any lesson — only the
Self-Check section and what follows it is removed.

## Constraints

- Do not modify any lesson's `ContentBody` other than removing the Self-Check section as
  specified.
- Do not modify `lesson-1`, `lesson-2`, or `lesson-3` entries in `lessonInteractions.js` —
  they are already correct and out of scope.
- Do not modify `PracticeQuestions.jsx`, `ConceptCheck.jsx`, or any other component file.
- Do not add `conceptChecks` entries for any of the 13 lessons — only `practiceQuestions`
  are in scope for this migration. No new conceptChecks content should be invented.
- Do not touch `15-creational-patterns` or any lesson outside the Rule 2 table.
- Preserve exact existing indentation, quote style variance, and brace conventions already
  present in both files.
- Both files must remain syntactically valid (JS object literal syntax; C# verbatim string
  with correctly doubled internal quotes) after the change.

## Output expectations

Return the full updated `app/src/data/lessonInteractions.js` and the full updated
`api/Data/JavaVerticalSeedData.cs` (or unified diffs against each), reflecting all 13
migrations.

## Self-verification checklist — run this before finishing, and report the results

1. Count the total number of new question objects added across all `practiceQuestions`
   arrays. It must be exactly 95. If not, find the discrepancy before finishing.
2. For every new question object, confirm `options` has exactly 4 entries with ids
   `a`,`b`,`c`,`d` and labels `A`,`B`,`C`,`D`.
3. Confirm every `correctOptionId` is one of `a`,`b`,`c`,`d` and matches what the source's
   `**Answer: X**` line said — re-check this against the source table in Rule 2, letter by
   letter, for at least the lessons with the highest question counts (14, 16, 17).
4. Confirm no two `id` values collide anywhere in the entire `lessonInteractions.js` file
   (including the pre-existing lessons 1–3 ids).
5. Confirm `api/Data/JavaVerticalSeedData.cs` still has balanced `{`/`}` and balanced
   `(`/`)` counts, and that every doubled-quote (`""`) pair used for literal quotes inside
   verbatim strings is still balanced (no stray unescaped `"`).
6. Confirm none of the 13 lessons' `ContentBody` still contains the string
   `"Self-Check (From Class Material)"` after your edit.
7. Confirm `15-creational-patterns` and lessons 1–3's `lessonInteractions.js` entries are
   byte-for-byte unchanged.

Report the outcome of all 7 checks explicitly in your response, including the actual counts
found, not just "looks good."
