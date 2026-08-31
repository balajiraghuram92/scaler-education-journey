# Prompt for Local LLM — FDE Phase 2: Agentic AI Core, Lessons 7-11 of 11 (module complete)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files following the
exact mechanism Phase 0 put in place and Phase 1 already used successfully. If any step below
doesn't match what you find in the actual files, STOP and report the discrepancy instead of
guessing.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 6 existing cases (`01-genai-world-and-llm-landscape` through
`06-n8n-automation-workflow`, from Phase 1) before `_ => null`. If those aren't there, STOP —
Phase 1 must be applied first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-2-agentic-ai-core-content.md`

This file contains 5 lessons (7-11), completing the `agentic-ai-core` module, each with a YAML
metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!-- CHAPTER_BODY_END -->` block, and a
`<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block with 8-9 structured
`QUESTION_BLOCK`s per lesson.

The 5 lessons, in order, with their exact database slugs (already computed via this project's
`Slugify()` — use these exact strings, do not recompute):

| # | Lesson title | Lesson slug (use exactly) |
|---|---|---|
| 7 | What Is an AI Agent? | `07-what-is-an-ai-agent` |
| 8 | Building Agents with n8n | `08-building-agents-with-n8n` |
| 9 | OpenClaw: Personal 24/7 AI Agent | `09-openclaw-personal-24-7-ai-agent` |
| 10 | Multi-Agent Systems | `10-multi-agent-systems` |
| 11 | Debugging AI | `11-debugging-ai` |

Module slug for all 5: `agentic-ai-core` (same module Phase 1 used — this completes it, 11 of
11 lessons total).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 6 Phase-1 cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 6 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as Phase 1:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Result shape (only the new part shown; the 6 existing Phase-1 cases stay exactly as they are,
directly above this):
```csharp
        "06-n8n-automation-workflow" => @"...", // existing, from Phase 1 — do not touch
        "07-what-is-an-ai-agent" => @"# What Is an AI Agent?

[... full chapter body for lesson 7 ...]
",
        "08-building-agents-with-n8n" => @"...",
        "09-openclaw-personal-24-7-ai-agent" => @"...",
        "10-multi-agent-systems" => @"...",
        "11-debugging-ai" => @"...",
        _ => null
    };
```

Do NOT change any other part of the file, and do NOT modify or re-order any of the 6 Phase-1
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/agentic-ai-core/{lesson-slug}'
```

e.g. `'fde-curriculum/agentic-ai-core/07-what-is-an-ai-agent'`

Do NOT touch any existing key — this includes both the 22 `java-spring-lld/...` keys and the 6
`fde-curriculum/agentic-ai-core/...` keys Phase 1 already added.

Follow the exact same conventions Phase 1 used:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before (application/misconception over recall; plausible distractors;
central concept; would stump a skimmer). `id` pattern:
`lesson-fde-agentic-ai-core-{lesson-number:00}-concept-check-{01|02}` (lesson-number is 07-11 for
this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase `correctOptionId`. Never add
`initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from Phase 1's prompt hold (non-obvious flow, shows something
the prose doesn't, faster mental model than re-reading). Lesson 10 (Multi-Agent Systems, the
mesh-to-orchestrator-worker redesign) is the most likely candidate in this batch — a before/after
contrast (mesh's many-to-many negotiation vs. orchestrator-worker's single accountability point)
would be genuinely illustrative if you choose to add it. Otherwise omit the `architecture` key
per lesson.

### 3c. practiceQuestions (all remaining MCQs)
Same format as Phase 1, `id` pattern `lesson-fde-agentic-ai-core-{lesson-number:00}-mcq-{01, 02,
...}`. None of this phase's questions need a `codeBlock` field — omit it.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS
data field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise. Do not add any entry for this phase.

---

## 5. Constraints

Do NOT touch:
- Any of the 6 existing cases in `GetAuthoredFdeLessonContent` from Phase 1
- `BuildLessonContent`, `BuildSupplementalLessonContent`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 `java-spring-lld/...` + 6
  `fde-curriculum/agentic-ai-core/...` from Phase 1)
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
Full method body — all 11 cases now present (6 from Phase 1 unchanged, 5 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 28 existing entries unchanged, plus the 5 new entries for this phase
(33 total).

### OUTPUT C: Architecture diagram decisions
For each of the 5 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 5 lessons already exist in the database with non-empty, generic `ContentBody`. After
applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '07-what-is-an-ai-agent',
  '08-building-agents-with-n8n',
  '09-openclaw-personal-24-7-ai-agent',
  '10-multi-agent-systems',
  '11-debugging-ai'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the `agentic-ai-core` module — all 11 lessons should now have authored content.

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 6 Phase-1 cases, before
      `_ => null`
- [ ] `lessonInteractions.js` has 5 new `fde-curriculum/agentic-ai-core/...` keys; all 28
      pre-existing keys unchanged
- [ ] Ran the SQL reset for all 5 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 11 lessons in the "Prerequisite:
      Agentic AI Core" module render real authored content
- [ ] Spot-checked at least 2 of the 5 new lessons: concept checks not pre-answered on load,
      practice questions render at the bottom
