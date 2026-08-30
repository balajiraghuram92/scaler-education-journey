# Prompt for Local LLM — Reground Lessons 4–13 Content in Real Scaler Source Material

Paste everything below this line into the local LLM as-is. Do not summarize, skip steps, or
add content that isn't explicitly instructed here. If a referenced file is missing or a
step cannot be completed exactly as specified, STOP and report the discrepancy instead of
guessing or substituting your own content.

---

## 0. Context — read this first

Repo root: `C:\Users\balaj\Documents\GitHub\Raghuram-git\scaler-education-journey`

The file `api/Data/JavaVerticalSeedData.cs` contains a private static method
`GetAuthoredLessonContent(string slug)` — a big `switch` expression, one case per lesson
slug, each returning a C# verbatim string (`@"..."`) that is the lesson's markdown content
(`ContentBody`).

Ten cases in that switch — slugs `"04-oop-3-polymorphism-interfaces"` through
`"13-java-adv-4-streams-exceptions"` — currently contain **generic, plausible-sounding
Java content that was NOT written from the actual Scaler class material**. It uses generic
scenarios (ride-hailing app, payment gateway, dispatch service) instead of the specific
examples, analogies, and vocabulary the instructor actually used in class. Your job is to
**replace those 10 cases** with new content grounded in the real source material listed
below for each lesson, while preserving the exact same five-section markdown structure
already used (do not invent a different structure).

### Why the structure must stay exactly the same

A separate method, `NeedsLessonContent`, only allows a lesson to be overwritten by this
switch if its live `ContentBody` does NOT already contain all three of these exact
substrings: `## Practical Backend Scenario`, `## Practice Loop`, `## Evidence of
Understanding`. If you rename, merge, or drop any of these three headings, future
re-seeding logic will misbehave. Keep all five headings below, in this order, for every
lesson you rewrite:

```
# Lesson <N> — <Title>

## Concepts Covered
## Practical Backend Scenario
## Practice Loop
## Evidence of Understanding
## Suggested Extension
```

You will ADD one new sixth section after `Suggested Extension`:

```
## Self-Check (From Class Material)
```

This section must contain 2–3 real MCQs pulled from the source material described in
step 2 below — not invented — each tagged with its provenance.

---

## 1. Source material locations (already extracted, read-only)

All paths below are relative to the repo root.

- **HackMD pre/post-lecture notes:** `info/.notes/scaler-raw-notes/hackmd/01-*.md` through
  `18-*.md` (files `19` onward belong to later lessons not in scope here — do not use them).
- **Handwritten class notes (already OCR-transcribed):**
  `info/.notes/scaler-raw-notes/pdfs-transcribed/*.md`
- **MCQ bank (88 questions across 8 files):** `info/.notes/scaler-raw-notes/mcqs/01-11.md`,
  `12-22.md`, `23-33.md`, `34-44.md`, `45-55.md`, `56-66.md`, `67-77.md`, `78-88.md`. Each
  MCQ entry has a `**Topic:**` line — search across ALL 8 files for the topic keyword given
  per lesson below; do not assume which file a topic lives in.
- **Reference lesson style (for tone/format only, do not copy its content):**
  `api/Data/JavaVerticalSeedData.cs`, the existing `"01-intro-to-lld"`,
  `"02-oop-1-intro-lab"`, and `"03-oop-2-access-modifiers-encapsulation"` cases in the same
  switch — these three are already hand-authored to the correct quality bar and were NOT
  flagged as generic. Match their sentence-level register (technical, direct, no filler),
  not their specific scenario content.

---

## 2. Per-lesson source map, MCQ topic filter, and word-count tier

For each lesson: read every file listed, extract the actual terminology/analogies/examples
the instructor used, and write the new content using them. Do not substitute a generic
example when the source material already has a specific one (e.g. if the source uses an
"office" metaphor for a concept, use that metaphor, not a different one you invent).

### Lesson 4 — `04-oop-3-polymorphism-interfaces` (Tier: Foundational, 500–800 words)
- HackMD: `hackmd/01-BkT7Xqqzfe.md` (pre-read), `hackmd/02-Bk0Qmcqzfl.md` (post-read)
- PDF notes: `pdfs-transcribed/Note_Jun_26__2026_8_42_57_PM.md` (covers Polymorphism,
  Overloading vs Overriding, Abstraction, Interfaces, the Diamond Problem)
- MCQ topic filter: search for `OOP-3` across all 8 mcq files
- Key material to use: the "Three-Question Design Test" table (IS A TYPE OF / CAN DO /
  HAS A) from `hackmd/01-BkT7Xqqzfe.md` — use this exact framework, do not paraphrase it
  into something else

### Lesson 5 — `05-oop-4-lms-lab` (Tier: Advanced mechanism, 1200–1500 words)
- HackMD: `hackmd/03-rJSH0zTGfe.md` (LMS lab overview), `hackmd/04-rJgHH0GpMze.md`
  (post-read)
- PDF notes: `pdfs-transcribed/Note_Jun_29__2026_8_04_06_PM.md` (Library Management System
  milestones: user hierarchy, lending functionality, full LMS with DSA considerations)
- MCQ topic filter: search for `OOP-4` across all 8 mcq files
- Key material to use: the three-milestone structure from the PDF notes (representing user
  hierarchy → lending books → full system with design patterns) as the lab's actual
  progression, not an invented progression

### Lesson 6 — `06-concurrency-1-threads` (Tier: Advanced mechanism, 1200–1500 words)
- HackMD: `hackmd/05-rJeBxlS-7zl.md` and `hackmd/08-r1WMg1SXGe.md` (both Concurrency-1
  pre-reads; read both, reconcile any overlap)
- PDF notes: `pdfs-transcribed/Note_Jul_1__2026_8_46_36_PM.md` (Process vs Thread, Process
  Control Block, single/multi-core, concurrency vs parallelism, context switching, SOP for
  implementing multithreading)
- MCQ topic filter: search for `Concurrency-1` across all 8 mcq files
- Key material to use: the **office/company metaphor** from `hackmd/05-rJeBxlS-7zl.md`
  (company = process, employees = threads, managers = CPU scheduler, desks = processing
  resources) — use this metaphor explicitly, it is the actual teaching device used in
  class. Also use the two diagnostic questions for concurrency vs. parallelism given there
  ("how many tasks are partially done simultaneously" / "how many tasks actively advance
  right now").

### Lesson 7 — `07-concurrency-2-executors` (Tier: Advanced mechanism, 1200–1500 words)
- HackMD: `hackmd/06-SySgeSZmzg.md` (Executors, Callable & Parallel Decomposition),
  `hackmd/07-ryxZzgySXzg.md` (post-read)
- PDF notes: `pdfs-transcribed/Note_Jul_3__2026_8_38_22_PM.md` (Executor Service, thread
  pools, Callable vs Runnable, Futures, TATA motor production line analogy, merge sort
  parallelization)
- MCQ topic filter: search for `Concurrency-2` across all 8 mcq files
- Key material to use: the **TATA motor production line analogy** for executor/thread-pool
  behavior, and the merge-sort parallelization example, both from the PDF notes — these are
  the actual examples used in class, do not replace them with a different analogy.

### Lesson 8 — `08-concurrency-3-synchronization` (Tier: Advanced mechanism, 1200–1500 words)
- HackMD: `hackmd/09-SklYF0bYmfg.md` (pre-read), `hackmd/10-ByFK0-FQMl.md` (post-read)
- PDF notes: `pdfs-transcribed/Note_Jul_6__2026_8_53_24_PM__1_.md` (Adder-Subtractor
  problem, Mutex, `synchronized` keyword, critical sections, intro to Producer-Consumer)
- MCQ topic filter: search for `Concurrency-3` across all 8 mcq files
- Key material to use: the **Adder-Subtractor race-condition problem** exactly as posed in
  the PDF notes as the worked example for why synchronization is needed, before
  introducing `synchronized`/locks.

### Lesson 9 — `09-concurrency-4-semaphores` (Tier: Advanced mechanism, 1200–1500 words)
- HackMD: `hackmd/11-Sygxrx9j7fx.md` (pre-read), `hackmd/12-BkeBgqj7fg.md` (post-read)
- PDF notes: `pdfs-transcribed/Note_Jul_8__2026_8_31_35_PM.md` (Semaphores, Producer-
  Consumer solution, full/partial/empty queue-state cases, homework: array sum with
  multiple threads and Futures)
- MCQ topic filter: search for `Concurrency-4` across all 8 mcq files
- Key material to use: the full/partial/empty bounded-buffer state cases from the PDF
  notes as the concrete worked example, and reference the array-sum-with-Futures homework
  as the Practice Loop's final step if it fits naturally.

### Lesson 10 — `10-java-adv-1-generics` (Tier: Advanced mechanism, 1200–1500 words)
- HackMD: `hackmd/13-Byl7MI-Amze.md` (pre-read), `hackmd/14-BJmMLbRXzl.md` (post-read)
- PDF notes: `pdfs-transcribed/Note_Jul_10__2026_8_54_07_PM.md` (Generics with coordinate
  storage example, generic `Pair` class, bounded type parameters and wildcards, Collections
  Framework hierarchy diagram)
- Also read: `pdfs-transcribed/LLD_1___Generics_and_Collections___2.md` (Comparable, natural
  ordering, lambda-based sorting, type erasure)
- MCQ topic filter: search for `Generic` (not `Generics-1` — the transcribed MCQs use
  varying labels; match anything containing "Generic")
- Key material to use: the generic `Pair` class example and the coordinate-storage example
  from `Note_Jul_10`, exactly as presented, before generalizing to wildcards/PECS.

### Lesson 11 — `11-java-adv-2-collections-lab` (Tier: Advanced mechanism, 1200–1500 words)
- HackMD: `hackmd/15-ryeZoFzz4Me.md` (pre-read, six-milestone lab), `hackmd/16-H1ZiYzG4Mg.md`
  (post-read)
- PDF notes: reuse `pdfs-transcribed/LLD_1___Generics_and_Collections___2.md` (doubly
  linked lists, HashSet implementation details) if not already fully used in Lesson 10 —
  do not duplicate the same paragraphs verbatim between the two lessons; split the material
  so each lesson covers a distinct part of it.
- MCQ topic filter: search for `Collections` across all 8 mcq files
- Key material to use: the six-milestone structure from `hackmd/15-ryeZoFzz4Me.md` as the
  lab's actual progression.

### Lesson 12 — `12-java-adv-3-lambdas-streams` (Tier: Advanced mechanism, 1200–1500 words)
- HackMD: `hackmd/17-ryxQN064Efx.md` (pre-read), `hackmd/18-SJXV0p4EGe.md` (post-read,
  functional interfaces section)
- PDF notes: `pdfs-transcribed/Note_Jul_15__2026_8_31_26_PM.md` (Functional Interfaces,
  Lambda Expressions, Streams with code examples)
- MCQ topic filter: search for `Streams` or `Lambda` across all 8 mcq files
- Key material to use: the functional-interface code examples from `Note_Jul_15` as the
  worked example for lambda syntax, before introducing the stream pipeline.

### Lesson 13 — `13-java-adv-4-streams-exceptions` (Tier: Advanced mechanism, 1200–1500 words)
- There is no dedicated "Java Advanced 4" HackMD pair in the extracted set — this lesson's
  streams-in-depth material must draw on the same `hackmd/17-ryxQN064Efx.md` /
  `hackmd/18-SJXV0p4EGe.md` / `Note_Jul_15` files as Lesson 12, but must cover the DISTINCT
  remainder: `groupingBy`/`partitioningBy`/`mapping`/`toMap` collectors and exception
  architecture. If, after reading those files, you find no exception-handling material in
  the extracted source at all, do NOT invent Scaler-specific exception content — instead
  keep the exception-architecture half of this lesson as general Java best-practice
  content (as it already mostly is), and only reground the streams/collectors half in the
  real source material. State clearly in your final report which half of this lesson was
  regrounded and which half was left as general content, so this gets flagged for a
  follow-up pass once more source notes are available.
- MCQ topic filter: search for `Streams` across all 8 mcq files (reuse different questions
  than the ones you already used in Lesson 12 — do not repeat the same MCQ in two lessons)

---

## 3. MCQ selection and citation rules

- For each lesson, pick 2–3 MCQs matching that lesson's topic filter. Prefer ones with a
  clearly marked correct answer over ones marked "no answer marked" in the transcription;
  if you must use an unmarked one, determine the correct answer yourself from the source
  material and state your reasoning is your own (not sourced) in the citation.
- Do not reuse the same MCQ (by its filename + seq number) in more than one lesson.
- Format each one in the new `## Self-Check (From Class Material)` section like this:

```
**Q1.** <question text, verbatim>
- A. <option>
- B. <option>
- C. <option>
- D. <option>

**Answer: <letter>** — <one-sentence why, referencing the concept above>
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/<filename>, MCQ <seq>)*
```

If you had to determine the answer yourself because none was marked, use
`*(SOURCE_TYPE: FROM_MATERIAL — mcqs/<filename>, MCQ <seq>; answer determined from source
material, not marked in original)*` instead.

---

## 4. What must NOT change

- Do not touch any switch case outside the 10 listed (`04-...` through `13-...`). Lessons
  `01`–`03` and `14`+ must be byte-identical to their current state.
- Do not change the method signature, the surrounding `switch`/`return` syntax, or any
  other method in the file.
- Do not change `NeedsLessonContent`, `BackfillLessonContent`, or any other method.
- Keep C# verbatim-string escaping consistent with the existing code: a literal `"` inside
  the string is written as `""` (see the existing lessons for examples, e.g. `""CANCELLED""`
  in lesson 1's case).
- Do not add a 7th section or reorder the six sections.
- Do not invent class dates, lecture numbers, or instructor names not present in the source
  material.

## 5. Output format

Output the complete, updated `GetAuthoredLessonContent` method body — from
`private static string? GetAuthoredLessonContent(string slug)` through its closing `}` —
as one code block, ready to paste over the existing method in
`api/Data/JavaVerticalSeedData.cs` (lines 933 onward in the current file, but locate it by
the method signature, not by line number, since line numbers may have shifted).

After the code block, output a short report:
- One line per lesson: which source files you used, and word count of the new content.
- Which MCQs you used per lesson (file + seq number), confirming none were reused across
  lessons.
- Any lesson where source material was thin or ambiguous (expected for Lesson 13 — see
  §2) and what you did about it.

## 6. Self-check before you output (do all of these)

1. All 10 target slugs are present in your output, none dropped, none duplicated.
2. Each of the 10 cases has exactly these six `##` headings in order: Concepts Covered,
   Practical Backend Scenario, Practice Loop, Evidence of Understanding, Suggested
   Extension, Self-Check (From Class Material).
3. Every MCQ used is traceable to a real file + seq number you actually read — you did not
   invent a question.
4. No MCQ appears in more than one lesson's Self-Check section.
5. Word counts roughly match the tier given per lesson (Lesson 4 lighter, Lessons 5–13
   fuller).
6. No case outside the 10 listed was touched; diff mentally against the original before
   output.
7. All embedded quotes inside the C# string use `""` escaping, not `\"`.
8. Every named analogy/example instructed above (office metaphor, TATA production line,
   Adder-Subtractor, six-milestone lab, generic Pair/coordinate example) actually appears
   in your rewritten content for its lesson.

---

## 7. Operational note for the human running this (not part of the LLM's task)

After pasting the LLM's output into `api/Data/JavaVerticalSeedData.cs` and saving: the
lessons already have `ContentBody` containing the three guard headings from a previous
seed run, so the normal seeder will silently skip them on restart. Before restarting the
API, reset those 10 lessons in the database so the new content actually gets written:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '04-oop-3-polymorphism-interfaces',
  '05-oop-4-lms-lab',
  '06-concurrency-1-threads',
  '07-concurrency-2-executors',
  '08-concurrency-3-synchronization',
  '09-concurrency-4-semaphores',
  '10-java-adv-1-generics',
  '11-java-adv-2-collections-lab',
  '12-java-adv-3-lambdas-streams',
  '13-java-adv-4-streams-exceptions'
);
```

Then rebuild/restart the API (`docker compose -f docker-compose.yml -f
docker-compose.dev.yml up -d --build`) so `BackfillLessonContent` re-applies the new
`GetAuthoredLessonContent` output.
