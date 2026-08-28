# Neuralascent — Local LLM Lesson Ingestion Prompt Template

**Purpose:** Paste this prompt into your Local LLM session after a new lesson `.md` file has been reviewed and approved. The LLM will wire the lesson content into the two app files that need updating.

**When to use:** After Step 1 (Claude generates lesson `.md`) and your self-review (§6 checklist passes).

**Last updated:** 2026-08-28

---

## HOW TO USE THIS TEMPLATE

1. Fill in every `[PLACEHOLDER]` in the **USER FILLS IN** section below.
2. Copy the entire block from `═══ START OF PROMPT ═══` to `═══ END OF PROMPT ═══`.
3. Paste into your Local LLM session.
4. Review the output, then copy-paste the generated file content into the actual files.
5. Run: `docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api`
6. Verify the lesson page renders correctly in the local build.

---

## USER FILLS IN (before copying the prompt)

```
LESSON_SLUG:        [e.g. 02-oop-access-modifiers]
LESSON_FILE_PATH:   [e.g. C:\Users\balaj\Downloads\Lesson_2_OOP_Access_Modifiers_v1.md]
LESSON_NUMBER:      [e.g. 2]
MCQ_COUNT:          [total MCQ count from the lesson file, e.g. 11]
```

---

═══════════════════════════════════════════════
START OF PROMPT — COPY EVERYTHING BELOW THIS LINE
═══════════════════════════════════════════════

## TASK: Wire lesson [LESSON_NUMBER] into the Neuralascent React app

You are wiring a reviewed, approved lesson file into two app files.
Read all source files carefully before writing any output.

---

## STEP 1 — READ THESE FILES IN FULL

1. **The lesson file:** `[LESSON_FILE_PATH]`
   This is your primary source. Extract everything from it.

2. **`api/Data/JavaVerticalSeedData.cs`**
   Find the method `GetAuthoredLessonContent(string slug)` — it is a switch statement.
   You will add one new `case` to it.

3. **`app/src/data/lessonInteractions.js`**
   Find the `const lessonInteractions = { ... }` object.
   You will add one new key to it. Do NOT touch any existing keys.

4. **`app/src/data/lessonExerciseAssociations.js`**
   Find the `const lessonExerciseAssociations = { ... }` object.
   If this lesson has a coding exercise (EXERCISE_BLOCK present in the lesson file), you will add one new entry. If there is no exercise, do not touch this file.

---

## STEP 2 — UPDATE `api/Data/JavaVerticalSeedData.cs`

Find `GetAuthoredLessonContent(string slug)`. It contains a switch with cases like:

```csharp
"01-intro-to-lld" => @"# Lesson 1 — ...",
"02-oop-1-intro-lab" => @"# Lesson 2 — ...",
_ => null
```

Add a new case for `"[LESSON_SLUG]"` immediately before the `_ => null` line:

```csharp
"[LESSON_SLUG]" => @"[FULL CHAPTER BODY HERE]",
_ => null
```

**CHAPTER BODY rules:**
- Copy the text between `<!-- CHAPTER_BODY_START -->` and `<!-- CHAPTER_BODY_END -->` markers in the lesson file verbatim.
- In C# verbatim strings (`@"..."`), escape every double-quote by doubling it: `"` → `""`
- Escape backticks: none needed — backticks are fine in C# verbatim strings.
- Do NOT include the HTML marker comments themselves (`<!-- CHAPTER_BODY_START -->` etc.) in the string.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the seed file.

---

## STEP 3 — UPDATE `app/src/data/lessonInteractions.js`

Add a new key to the `lessonInteractions` object for this lesson.
The key format is: `'java-spring-lld/{module-slug}/{lesson-slug}'`

Determine `{module-slug}` from the lesson file's YAML metadata (`module_id` field).
The lesson slug is `[LESSON_SLUG]`.

The entry must contain:

### 3a. conceptChecks (exactly 2)

Select the 2 MCQs from the lesson file that best work as **gated interaction points** mid-page.
Selection criteria (in priority order):
1. Tests application or misconception recognition — not verbatim recall of a definition
2. Has 3–4 plausible wrong answers that reflect real mistakes (not obviously silly distractors)
3. Covers the lesson's central concept (the mechanism the whole lesson is about)
4. Would genuinely stump someone who skimmed rather than read

Use the format:
```js
conceptChecks: [
  {
    id: 'lesson-[LESSON_NUMBER]-concept-check-01',
    eyebrow: 'CONCEPT CHECK 01 — TOPIC NAME IN CAPS',
    question: '...',
    options: [
      { id: 'a', label: 'A', text: '...' },
      { id: 'b', label: 'B', text: '...' },
      { id: 'c', label: 'C', text: '...' },
      { id: 'd', label: 'd', text: '...' }
    ],
    correctOptionId: 'b',
    explanation: '...',
    incorrectExplanation: '...',
    hint: '...'
  }
]
```

**HARD RULES:**
- Exactly 2 concept checks — never more, never fewer.
- NEVER add `initialSelectedOption` or `initialSubmitted` to any concept check object. These cause the question to appear pre-answered on load. They are banned.
- `incorrectExplanation` should be diagnostic — guide the learner toward the right reasoning, not just say "wrong".
- `hint` is one sentence shown on demand after a wrong answer.

### 3b. architecture (optional — apply inclusion test before adding)

Before adding an architecture diagram, apply this test. The diagram earns its place ONLY if ALL of these are true:
- [ ] The flow is genuinely non-obvious from the Practical Backend Scenario prose alone
- [ ] The diagram shows something the prose does NOT already cover
- [ ] A 7–8 year developer gains a faster mental model from the diagram than from re-reading the paragraph

If the test fails (a linear request→entity→output flow that repeats the prose): **omit the `architecture` key entirely.**

If the test passes, use:
```js
architecture: {
  id: 'lesson-[LESSON_NUMBER]-{concept-slug}',
  eyebrow: 'PRACTICAL BACKEND SCENARIO — {SCENARIO NAME IN CAPS}',
  boundaryLabel: 'BOUNDARY LABEL',
  boundaryText: 'One sentence explaining what the boundary enforces.',
  nodes: [
    { id: 'input',    label: 'Entry Point',       kind: 'input'    },
    { id: 'service',  label: 'ServiceName',        kind: 'service'  },
    { id: 'boundary', label: 'Entity.method()',    kind: 'boundary', highlighted: true },
    { id: 'adapter',  label: 'DownstreamService',  kind: 'adapter'  },
    { id: 'output',   label: 'Result State',       kind: 'output'   }
  ]
}
```

Best pattern for OOP lessons: **before/after contrast** (left: procedural data mutation; right: OOP encapsulated flow) — NOT a linear flow. If you cannot make a genuine contrast, omit the diagram.

### 3c. practiceQuestions (all remaining MCQs)

All MCQs that are NOT used as concept checks go here.
Total MCQ count in this lesson: [MCQ_COUNT]
Concept checks use 2 → practiceQuestions gets [MCQ_COUNT - 2] questions.

Use the format:
```js
practiceQuestions: [
  {
    id: 'lesson-[LESSON_NUMBER]-mcq-01',
    question: '...',
    // codeBlock: '...',   ← OPTIONAL — see rules below
    options: [
      { id: 'a', label: 'A', text: '...' },
      { id: 'b', label: 'B', text: '...' },
      { id: 'c', label: 'C', text: '...' },
      { id: 'd', label: 'D', text: '...' }
    ],
    correctOptionId: 'b',
    explanation: '...'
  },
  // ... one object per remaining MCQ
]
```

**`codeBlock` field rules (optional field):**
Add `codeBlock` when the question requires the learner to read code carefully to answer — multi-line snippets, constructor bodies, assignment chains, or "what does this print?" style questions. When `codeBlock` is present, keep `question` as pure prose (e.g. "What does the following code print?") with NO embedded code in the question string. The component renders `codeBlock` as a dark monospace block between the question text and the options.

Do NOT add `codeBlock` for questions that reference a short identifier or keyword inline (e.g. "A class has `public double rating`. Which is most accurate?") — those stay as prose with backtick-formatted inline code in the `question` string. Single-expression references embedded in a sentence do not need a separate block.

SOURCE_TYPE from the lesson file is a review marker — do NOT add it as a data field in the JS objects. JS comment only if you want to note it, e.g. `// FROM_MATERIAL`.

---

## STEP 4 — UPDATE `app/src/data/lessonExerciseAssociations.js` (only if lesson has an exercise)

If the lesson file contains an `EXERCISE_BLOCK` in the `EXERCISES_SECTION`, add one entry to `lessonExerciseAssociations.js`:

```js
'java-spring-lld/{module-slug}/[LESSON_SLUG]': {
  exerciseId: 'java-lld-{exercise-id}'
},
```

The `{exercise-id}` comes from the `EXERCISE_ID` field in the EXERCISE_BLOCK (lowercased, hyphenated). The `exerciseId` value must match the `Id` (or slug) of the Exercise record in the database — the component uses this to fetch exercise data from the API.

**CRITICAL:** If no entry exists in `lessonExerciseAssociations.js` for this lesson slug, the `ImplementationExercise` component will never render — even if the exercise is correctly seeded in the database and correctly described in the lesson file. Both the database record AND the association file entry are required for the exercise to appear.

If the lesson has NO coding exercise, skip this step entirely. Do not add a placeholder entry.

Do NOT touch any existing entries in `lessonExerciseAssociations.js`.

---

## STEP 5 — CONSTRAINTS

Do NOT touch:
- Any other case in `GetAuthoredLessonContent` switch
- Any existing key in `lessonInteractions`
- Any existing entry in `lessonExerciseAssociations.js`
- Any CSS file
- Any other `.cs` file
- `BackfillLessonContent` or `NeedsLessonContent` methods
- The `getLessonInteractions` export at the bottom of `lessonInteractions.js`
- The `getLessonExerciseAssociation` export at the bottom of `lessonExerciseAssociations.js`

Match code style exactly:
- `JavaVerticalSeedData.cs`: C# verbatim strings, double-quote escaping, 4-space indent
- `lessonInteractions.js`: single quotes, 2-space indent, trailing comma on last property

---

## STEP 6 — OUTPUT

Produce the following, clearly labeled:

### OUTPUT A: Addition to `api/Data/JavaVerticalSeedData.cs`
Show only the new `case` block to add to the switch. Mark exactly where it goes
(before `_ => null`). Do NOT print the entire seed file.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file. It must contain all existing entries unchanged, plus the new entry.

### OUTPUT C: Architecture diagram decision
State whether you included or omitted the `architecture` key, and the one-sentence reason.

### OUTPUT D: Addition to `app/src/data/lessonExerciseAssociations.js` (only if exercise exists)
Show only the new entry to add. If the lesson has no exercise, state "No exercise — lessonExerciseAssociations.js not changed."

═══════════════════════════════════════════════
END OF PROMPT
═══════════════════════════════════════════════

---

## POST-INGESTION CHECKLIST (you run this after applying the output)

- [ ] Pasted the new `case` block into `JavaVerticalSeedData.cs` before `_ => null`
- [ ] Replaced `lessonInteractions.js` with the LLM's output B
- [ ] Verified no existing lesson entries are missing or changed in `lessonInteractions.js`
- [ ] Ran: `docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api`
- [ ] Verified lesson page renders (not "being prepared" placeholder)
- [ ] Verified concept check 01 is NOT pre-answered on load
- [ ] Verified concept check 02 is NOT pre-answered on load
- [ ] Verified practice questions appear at bottom of page
- [ ] If lesson has an exercise: exercise component appears after the Practice Loop section
- [ ] If lesson has an exercise: confirm the `exerciseId` in `lessonExerciseAssociations.js` matches an Exercise record in the database
- [ ] If content shows old content: run the force-reset command and restart:
  ```
  docker exec -it studytracker-db psql -U studyuser -d studytracker \
    -c "UPDATE lessons SET content_body = '', content_status = 'Outline' WHERE slug = '[LESSON_SLUG]';"
  docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
  ```
