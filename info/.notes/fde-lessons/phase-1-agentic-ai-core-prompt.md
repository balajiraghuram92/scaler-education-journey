# Prompt for Local LLM — FDE Phase 1: Agentic AI Core, Lessons 1-6 of 11

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files following the
exact mechanism Phase 0 already put in place. If any step below doesn't match what you find in
the actual files, STOP and report the discrepancy instead of guessing.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method (added in a prior "Phase 0" prompt) containing `_ => null` as its only case so far.
If it does not exist, STOP — Phase 0 must be applied first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-1-agentic-ai-core-content.md`

This file contains 6 lessons, each with a YAML metadata block, a `<!-- CHAPTER_BODY_START -->`
… `<!-- CHAPTER_BODY_END -->` block (the exact markdown to use as `ContentBody`), and a
`<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block with 8-9 structured
`QUESTION_BLOCK`s per lesson.

The 6 lessons, in order, with their exact database slugs (already computed via this project's
`Slugify()` — use these exact strings, do not recompute):

| # | Lesson title | Lesson slug (use exactly) |
|---|---|---|
| 1 | GenAI World & LLM Landscape | `01-genai-world-and-llm-landscape` |
| 2 | Prompt Engineering Basics | `02-prompt-engineering-basics` |
| 3 | Advanced Prompting & AI Safety Basics | `03-advanced-prompting-and-ai-safety-basics` |
| 4 | LLM Built-in Power Tools | `04-llm-built-in-power-tools` |
| 5 | RAG (Retrieval-Augmented Generation) | `05-rag-retrieval-augmented-generation` |
| 6 | n8n Automation Workflow | `06-n8n-automation-workflow` |

Module slug for all 6: `agentic-ai-core`

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently contains:

```csharp
    private static string? GetAuthoredFdeLessonContent(string slug) => slug switch
    {
        _ => null
    };
```

Add 6 new cases, one per lesson slug in the table above, **immediately before** `_ => null`.
Each case's value is the lesson's full chapter body — everything between that lesson's
`<!-- CHAPTER_BODY_START -->` and `<!-- CHAPTER_BODY_END -->` markers in the source file,
copied verbatim (including the leading `# Lesson Title` line and all `##` section headers).

**CHAPTER_BODY rules (same convention already used in `JavaVerticalSeedData.cs`):**
- Copy the text between the markers verbatim. Do not include the marker comments themselves.
- This project uses C# verbatim strings (`@"..."`) for lesson content — escape every literal
  double-quote in the copied text by doubling it: `"` → `""`.
- Backticks need no escaping in a C# verbatim string.
- The string must end with a newline before the closing `"`.

Result shape:
```csharp
    private static string? GetAuthoredFdeLessonContent(string slug) => slug switch
    {
        "01-genai-world-and-llm-landscape" => @"# GenAI World & LLM Landscape

[... full chapter body for lesson 1 ...]
",
        "02-prompt-engineering-basics" => @"# Prompt Engineering Basics

[... full chapter body for lesson 2 ...]
",
        "03-advanced-prompting-and-ai-safety-basics" => @"...",
        "04-llm-built-in-power-tools" => @"...",
        "05-rag-retrieval-augmented-generation" => @"...",
        "06-n8n-automation-workflow" => @"...",
        _ => null
    };
```

Do NOT change any other part of the file. Do not touch `BuildLessonContent`,
`BuildSupplementalLessonContent`, `ModuleGuides`, or anything outside this one method.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson. The key format is:

```
'fde-curriculum/agentic-ai-core/{lesson-slug}'
```

e.g. `'fde-curriculum/agentic-ai-core/01-genai-world-and-llm-landscape'`

Do NOT touch any existing key (all current keys are `java-spring-lld/...` — leave every one of
them exactly as-is).

For each lesson, build the entry from that lesson's MCQ_SECTION in the source file:

### 3a. conceptChecks (exactly 2 per lesson)

Select the 2 questions from that lesson's MCQ block that work best as gated mid-page interaction
points, using this priority order:
1. Tests application or misconception recognition, not verbatim recall
2. Has plausible wrong options reflecting real mistakes, not silly distractors
3. Covers the lesson's central concept
4. Would genuinely stump someone who skimmed rather than read

Use this format (note: source questions are numbered Q1-Q8/Q9 with a `CORRECT_ANSWER_KEY` of
A/B/C/D — map that to the lowercase `correctOptionId` used here):

```js
conceptChecks: [
  {
    id: 'lesson-fde-agentic-ai-core-01-concept-check-01',
    eyebrow: 'CONCEPT CHECK 01 — TOPIC NAME IN CAPS',
    question: '...',
    options: [
      { id: 'a', label: 'A', text: '...' },
      { id: 'b', label: 'B', text: '...' },
      { id: 'c', label: 'C', text: '...' },
      { id: 'd', label: 'D', text: '...' }
    ],
    correctOptionId: 'b',
    explanation: '...',
    incorrectExplanation: '...',
    hint: '...'
  }
]
```

**HARD RULES (same as the Java vertical convention):**
- Exactly 2 concept checks per lesson — never more, never fewer.
- NEVER add `initialSelectedOption` or `initialSubmitted` — these make a question appear
  pre-answered on load and are banned.
- `explanation` can reuse the source question's `EXPLANATION` field near-verbatim.
- `incorrectExplanation` should be diagnostic, guiding toward the right reasoning, not just
  "wrong" — write one if the source doesn't give a ready-made version, using the source
  `EXPLANATION` as your basis.
- `hint` is one sentence, shown on demand after a wrong answer — write one derived from the
  source question's `LESSON_CONNECTION` and `EXPLANATION` fields.
- The `id` pattern is `lesson-fde-{module-slug}-{lesson-number:00}-concept-check-{01|02}` — use
  the lesson's position within this course (1 through 6 for this phase), not its position within
  a Java-vertical-style global numbering.

### 3b. architecture (optional — apply the inclusion test)

Add an `architecture` key ONLY if all of these are true:
- The flow is genuinely non-obvious from the Practical Backend Scenario prose alone
- The diagram shows something the prose does not already cover
- A 7-8 year developer gains a faster mental model from the diagram than from re-reading the
  paragraph

For this batch of 6 lessons, the RAG lesson (05) and the n8n lesson (06) are the most likely
candidates (RAG's ingestion → retrieval → generation pipeline; n8n's trigger → node → branch
graph) — but only add the diagram if it passes the test above; otherwise omit the `architecture`
key entirely for that lesson. If you add one, use:

```js
architecture: {
  id: 'lesson-fde-agentic-ai-core-{lesson-number:00}-{concept-slug}',
  eyebrow: 'PRACTICAL BACKEND SCENARIO — {SCENARIO NAME IN CAPS}',
  boundaryLabel: 'BOUNDARY LABEL',
  boundaryText: 'One sentence explaining what the boundary enforces.',
  nodes: [
    { id: 'input',    label: 'Entry Point',      kind: 'input'    },
    { id: 'service',  label: 'ServiceName',       kind: 'service'  },
    { id: 'boundary',  label: 'Key step',         kind: 'boundary', highlighted: true },
    { id: 'adapter',  label: 'DownstreamService', kind: 'adapter'  },
    { id: 'output',   label: 'Result State',      kind: 'output'   }
  ]
}
```

### 3c. practiceQuestions (all remaining MCQs)

Every question NOT used as a concept check goes here, in its original order, mapped from the
source's structured QUESTION_BLOCK format:

```js
practiceQuestions: [
  {
    id: 'lesson-fde-agentic-ai-core-01-mcq-01',
    question: '...',
    // codeBlock: '...',   ← only if the question needs a code/config snippet read carefully
    options: [
      { id: 'a', label: 'A', text: '...' },
      { id: 'b', label: 'B', text: '...' },
      { id: 'c', label: 'C', text: '...' },
      { id: 'd', label: 'D', text: '...' }
    ],
    correctOptionId: 'b',
    explanation: '...'
  },
  // one object per remaining question in this lesson, renumbered mcq-01, mcq-02, ...
]
```

None of this phase's MCQs require a `codeBlock` field (no lesson in this batch has a
code-reading question) — omit that field entirely rather than adding an empty one.

SOURCE_TYPE from the source file (`LLM_GENERATED` for every question in this phase) is a review
marker only — do not add it as a JS data field. A `// LLM_GENERATED` comment above each question
object is fine if you want to preserve the marker for the reviewer.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry to this file for this phase.

---

## 5. Constraints

Do NOT touch:
- Any other case in `GetAuthoredFdeLessonContent` (there should be none yet besides `_ => null`)
- `BuildLessonContent`, `BuildSupplementalLessonContent`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (all current `java-spring-lld/...` entries)
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
Full method body with all 6 new cases added before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all existing entries unchanged, plus the 6 new entries for this phase.

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons already exist in the database with non-empty, generic `ContentBody` from the
earlier seeder run — the "populate only empty scaffold fields" rule means your new authored
content will NOT appear until those rows are cleared first. After applying the code changes
above and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-genai-world-and-llm-landscape',
  '02-prompt-engineering-basics',
  '03-advanced-prompting-and-ai-safety-basics',
  '04-llm-built-in-power-tools',
  '05-rag-retrieval-augmented-generation',
  '06-n8n-automation-workflow'
);
```

Then restart the API again so the seeder repopulates those 6 rows from the new authored switch:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

---

## 8. Post-ingestion checklist (run this after applying)

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, before `_ => null`
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/agentic-ai-core/...` keys, no existing
      keys removed or changed
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 6 lessons render real content, not
      the old generic "Treat this chapter as a working draft" filler
- [ ] Confirmed concept check 01 and 02 are NOT pre-answered on load, for at least 2 of the 6
      lessons spot-checked
- [ ] Confirmed practice questions render at the bottom of each lesson page
