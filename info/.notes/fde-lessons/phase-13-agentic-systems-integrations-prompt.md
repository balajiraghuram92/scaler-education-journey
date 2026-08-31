# Prompt for Local LLM — FDE Phase 13: Agentic Systems & Enterprise Integrations (Module 6), Lessons 1-6 of 11

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-13-agentic-systems-integrations-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

This phase is applied **second** in a three-phase batch: Phase 12 (the second half of Module 5,
"Enterprise Communication, Consulting & LLM Engineering," lessons 7-12) is applied first, then this
Phase 13, then Phase 15 (Phase 14 is deliberately skipped/not yet authored — do not treat a missing
Phase 14 file as an error).

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **at least 67 existing cases** (61 from Phases 1-11, covering
`agentic-ai-core` (11) + `fde-foundations` (12) + `backend-observability-data` (15) +
`full-stack-ai-frontends` (5) + `cloud-devops-infrastructure` (12) + the first half of
`enterprise-consulting-llm` (6, Phase 11) = 61, **plus 6 more from Phase 12** completing
`enterprise-consulting-llm` to 12 total lessons = 67) before `_ => null`.

**If the count is short of 67 — in particular, if `enterprise-consulting-llm` does not yet have 12
cases — STOP.** Phase 12 must be applied first; do not proceed with this phase until it has been.
Do not attempt to "fill in" Phase 12's cases yourself or guess their content — report the exact
case count you found and wait for Phase 12 to be applied.

Also confirm `app/src/data/lessonInteractions.js` has **at least 89 existing keys** (22
`java-spring-lld/...` + 67 `fde-curriculum/...`, the same 67-lesson set as above) before proceeding.
If short, STOP for the same reason.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-13-agentic-systems-integrations-content.md`

This file contains 6 lessons, the first half of a **new** Module 6 ("6. Agentic Systems &
Enterprise Integrations"), lessons 1-6 of 11. A later phase covers lessons 7-11 (Enterprise Systems
Landscape continuation into API Integration Patterns & Connector Design, Integration Failure Modes
& Debugging, Messy Customer Data & Entity Resolution, Build: CRM-to-AI Support Copilot, and
Assessments) and completes the module — do not add placeholder content for those 5 lessons in this
phase.

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 1 | Tool Calling, Function Calling & Structured Output | `01-tool-calling-function-calling-and-structured-output` | 8 |
| 2 | Agentic Patterns & Production Concerns | `02-agentic-patterns-and-production-concerns` | 8 |
| 3 | Agent Debugging, Failure Analysis & Evaluation | `03-agent-debugging-failure-analysis-and-evaluation` | 8 |
| 4 | MCP (Model Context Protocol) & Enterprise Tooling | `04-mcp-model-context-protocol-and-enterprise-tooling` | 8 |
| 5 | Multi-Agent Patterns & Human-in-the-Loop | `05-multi-agent-patterns-and-human-in-the-loop` | 9 |
| 6 | Enterprise Systems Landscape & Integration Topology | `06-enterprise-systems-landscape-and-integration-topology` | 9 |

Module slug for all 6: `agentic-systems-integrations` (new module — this is its first phase; a
later phase adds lessons 7-11 to the same module).

Total MCQs across the 6 lessons: 50 (8+8+8+8+9+9).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the (at least) 67 existing
cases followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after all existing cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the existing cases
already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/agentic-systems-integrations/{lesson-slug}'
```

e.g. `'fde-curriculum/agentic-systems-integrations/01-tool-calling-function-calling-and-structured-output'`

Do NOT touch any existing key — at least 89 total existing keys (22 `java-spring-lld/...` + 67
`fde-curriculum/...` from Phases 1-11, plus 6 more from Phase 12 completing
`enterprise-consulting-llm` = 95 total if Phase 12 has been applied) already present. After this
phase, the file should have 95 + 6 = **101 total keys**.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-agentic-systems-integrations-{lesson-number:00}-concept-check-{01|02}` (lesson-number is
01-06 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase `correctOptionId`.
Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons.
Lessons 1-4 and lesson 5 are each anchored by one concrete mechanism (a tool-call retry loop, a
timeout/retry/circuit-breaker sequence, a backward-trace-walk, an MCP client/server call path, a
gated worker/approval flow) that could plausibly be diagrammed, but in every one of these 5 cases
the Practical Backend Scenario prose already walks through that exact same mechanism step by step —
the diagram would restate, not add. Lesson 6's point-to-point-vs-hub topology comparison is the one
genuine candidate: it is a structural, multi-node contrast (three or more systems connected
pairwise vs. through one hub) rather than a linear request→response flow, and the Practical Backend
Scenario prose describes the count and the decision but does not visually show the node-and-edge
shape a reader would otherwise have to construct mentally. **Default to omitting `architecture` for
lessons 1-5. For lesson 6, apply the inclusion test yourself against the actual final scenario text
you read in the source file — if you judge the point-to-point-vs-hub contrast passes all three
criteria, include it as a before/after node-group diagram (point-to-point nodes fully
interconnected on one side, the same systems connected only to a central hub node on the other);
if you judge it does not clearly pass, omit it and say so in Output C.** If in doubt on any lesson,
omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-agentic-systems-integrations-{lesson-number:00}-mcq-{01, 02, ...}`. None of this
phase's questions need a `codeBlock` field — omit it, **except** lesson 1's Q2 (about
`additionalProperties: false`), which may optionally render the JSON schema snippet from the
lesson's Concepts Covered section as a `codeBlock` if you judge it clarifies the question; this is
optional, not required — omit it if unsure.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the existing cases in `GetAuthoredFdeLessonContent` (at least 67, all from Phases 1-12)
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (at least 95 total, from Phases 1-12)
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
Full method body — all cases now present (all pre-existing ones unchanged, 6 new from this
phase — 73 total if Phase 12's 67 were already in place), before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all pre-existing entries unchanged, plus the 6 new entries for this phase
(101 total if Phase 12's 95 were already in place).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 1-5 omitted (their candidate mechanisms are already fully
covered by their own scenario prose); lesson 6 either included (if its point-to-point-vs-hub
contrast passes your own application of the inclusion test) or omitted with your specific reason
if it does not.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons likely already exist in the database with thin, machine-templated `ContentBody`.
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-tool-calling-function-calling-and-structured-output',
  '02-agentic-patterns-and-production-concerns',
  '03-agent-debugging-failure-analysis-and-evaluation',
  '04-mcp-model-context-protocol-and-enterprise-tooling',
  '05-multi-agent-patterns-and-human-in-the-loop',
  '06-enterprise-systems-landscape-and-integration-topology'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the first half of Module 6 ("6. Agentic Systems & Enterprise Integrations") —
lessons 1-6 of 11 should now have authored content. Lessons 7-11 remain for a future phase.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after all pre-existing cases, before
      `_ => null` (73 total if Phase 12 was already applied)
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/agentic-systems-integrations/...` keys; all
      pre-existing keys unchanged (101 total if Phase 12 was already applied)
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 1-6 of "6. Agentic Systems &
      Enterprise Integrations" render real authored content, and lessons 7-11 still show
      placeholder/draft content pending a future phase
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
