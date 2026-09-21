# STRICT PROMPT — Replace lesson 20's MCQs with real Scaler assignment questions

Read this entire document before touching any file. This is a targeted MCQ replacement on ONE
file: `app/src/data/lessonInteractions.js`. Do not touch any other file.

## Why

`java-spring-lld/applied-machine-coding/20-machine-coding-parking-lot` currently has 6
`LLM_GENERATED` practice questions. A real 16-question Scaler assignment on this exact topic
(Day 131, Code Parking Lot 2 — layered architecture, generic repositories, and concurrency
correctness) has since been transcribed in full, with verified answers and explanations, at
`info/.notes/scaler-raw-notes/mcqs/day131-code-parking-lot-2-assignment-mcqs.md` (Q2 through Q16
— Q1 was not captured in the source screenshots). This real material is more scenario-anchored
and code-grounded than the existing generated questions, and covers concepts (generic repository
bounds, layered validation reuse, lock granularity, faithful concurrency test design) the current
6 questions don't touch at all.

## Task

1. Read `info/.notes/scaler-raw-notes/mcqs/day131-code-parking-lot-2-assignment-mcqs.md` in full.
2. Read the current `20-machine-coding-parking-lot` entry in `app/src/data/lessonInteractions.js`
   (its `practiceQuestions` array) to see the exact schema/style to match.
3. **Delete** the existing 6 `LLM_GENERATED` questions under
   `java-spring-lld/applied-machine-coding/20-machine-coding-parking-lot`.
4. **Replace** them with all 15 questions (Q2–Q16) from the transcribed file, converted into this
   project's exact `practiceQuestions` schema:
   - `id`: `lesson-20-parking-mcq-01` through `lesson-20-parking-mcq-15`, in the same order as the
     source file (Q2→01, Q3→02, ... Q16→15).
   - `question`: the question text. Where the source includes a code block, embed it inside the
     question string using the same multi-line-string-with-`\n` style already used elsewhere in
     this file for code-bearing questions (see any existing question with an embedded code
     snippet for the exact formatting convention).
   - `options`: exactly 4 options, `id`/`label` `a`/`A` through `d`/`D`, `text` taken verbatim
     from the source's lettered options.
   - `correctOptionId`: matching the source's stated correct answer.
   - `explanation`: the source's explanation paragraph, verbatim or lightly tightened to match
     this file's existing explanation tone (state why the correct answer is right AND why the
     most tempting wrong answer is wrong — the source explanations already do this).
   - Add a leading `// SOURCE_TYPE: FROM_MATERIAL` comment above every one of these 15 questions
     (not `LLM_GENERATED` — this is real, transcribed Scaler assignment content).

## Constraints

- Only edit the `20-machine-coding-parking-lot` entry. Do not touch any other lesson's
  `practiceQuestions`, and do not touch `conceptChecks` if present elsewhere in the file.
- Preserve exact code style: single-quoted strings, existing indentation, existing key order
  (`id`, `question`, `options`, `correctOptionId`, `explanation`).
- Do not invent, omit, or reorder any of the 15 questions — this is a direct, faithful conversion
  of already-finalized content into the file's schema, not a rewrite.
- Net effect: lesson 20 goes from 6 questions to 15 questions, all `SOURCE_TYPE: FROM_MATERIAL`.

## Verification checklist

1. `grep -c "lesson-20-parking-mcq-"` returns 15, with ids `01` through `15`, each appearing
   exactly once.
2. `grep -c "SOURCE_TYPE: FROM_MATERIAL"` increased by 15; the 6 old
   `SOURCE_TYPE: LLM_GENERATED` lesson-20 questions are gone.
3. Every question has exactly 4 options (`a`–`d`) and a `correctOptionId` matching one of them.
4. No other lesson's questions changed — diff should show changes scoped entirely to the
   `20-machine-coding-parking-lot` block.
5. File still ends with the unchanged `getLessonInteractions` function and default export.
