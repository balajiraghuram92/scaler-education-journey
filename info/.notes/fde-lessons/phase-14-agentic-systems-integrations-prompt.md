# Prompt for Local LLM — FDE Phase 14: Agentic Systems & Enterprise Integrations (Module 6), Lessons 7-11 of 11 (Module Complete)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-14-agentic-systems-integrations-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

This phase is applied **after** Phase 12, Phase 13, and Phase 15 have all already been applied
(uncommitted, but applied) to `api/Data/FdeCurriculumSeedData.cs` and
`app/src/data/lessonInteractions.js`. Phase 12 completed `enterprise-consulting-llm` (Module 5,
12/12). Phase 13 authored the first six lessons of `agentic-systems-integrations` (Module 6,
lessons 1-6 of 11). Phase 15 authored all six lessons of `application-security-reliability`
(Module 7, 6/6, module complete).

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **exactly 79 existing cases** before `_ => null`: 61 from Phases 1-11
(`agentic-ai-core` (11) + `fde-foundations` (12) + `backend-observability-data` (15) +
`full-stack-ai-frontends` (5) + `cloud-devops-infrastructure` (12) + the first half of
`enterprise-consulting-llm` (6, Phase 11) = 61), **plus 6 from Phase 12** completing
`enterprise-consulting-llm` to 12 total = 67, **plus 6 from Phase 13** (the first half of
`agentic-systems-integrations`, lessons 1-6 of 11) = 73, **plus 6 from Phase 15**
(`application-security-reliability`, module complete) = **79 total**.

**If the count is short of 79 — in particular, if `agentic-systems-integrations` does not yet have
at least 6 cases (lessons 1-6), or if `application-security-reliability` does not yet have 6 cases
— STOP.** Phases 12, 13, and 15 must all be applied first; do not proceed with this phase until
they are. Do not attempt to "fill in" any of those phases' cases yourself or guess their content —
report the exact case count you found and wait for the missing phase(s) to be applied.

Also confirm `app/src/data/lessonInteractions.js` has **exactly 101 existing keys** (22
`java-spring-lld/...` + 79 `fde-curriculum/...`, the same 79-lesson set as above) before
proceeding. If short, STOP for the same reason.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-14-agentic-systems-integrations-content.md`

This file contains 5 lessons, lessons 7-11 of 11, completing Module 6 ("6. Agentic Systems &
Enterprise Integrations"). Phase 13 already authored lessons 1-6 of the same module — do not
re-add or modify those; this phase only adds lessons 7-11.

Each of the 5 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 5 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 7 | API Integration Patterns & Connector Design | `07-api-integration-patterns-and-connector-design` | 9 |
| 8 | Integration Failure Modes & Debugging | `08-integration-failure-modes-and-debugging` | 9 |
| 9 | Messy Customer Data & Entity Resolution | `09-messy-customer-data-and-entity-resolution` | 8 |
| 10 | Build: CRM-to-AI Support Copilot | `10-build-crm-to-ai-support-copilot` | 9 |
| 11 | Assessments: Agentic System Build & Red-Team, Integration War Room | `11-assessments-agentic-system-build-and-red-team-integration-war-room` | 8 |

Module slug for all 5: `agentic-systems-integrations` (existing module — this is its **second and
final** phase; lessons 1-6 were added by Phase 13, and this phase's 5 lessons complete it at
11/11).

Total MCQs across the 5 lessons: 43 (9+9+8+9+8).

**Slug derivation note (for your own verification, do not recompute — use the table above
verbatim):** slugs are produced by the file's own `Slugify` method: lowercase, `&` → ` and `, `+` →
` plus `, every other run of non-alphanumeric characters (including `:`, `,`, and `-`) collapsed to
a single `-`, then trimmed of leading/trailing `-`. Lesson 10's title starts with "Build:" and
lesson 11's title contains a colon, a comma, and an internal hyphen ("Red-Team") — all of these
collapse into single hyphens per that rule, which is how the table above's slugs were derived.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the (exactly) 79 existing
cases followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above,
**immediately before** `_ => null` (after all existing cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the existing cases
already in place (including the 6 Phase 13 cases for lessons 1-6 of this same module — they stay
exactly as they are).

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/agentic-systems-integrations/{lesson-slug}'
```

e.g. `'fde-curriculum/agentic-systems-integrations/07-api-integration-patterns-and-connector-design'`

Do NOT touch any existing key — exactly 101 total existing keys (22 `java-spring-lld/...` + 79
`fde-curriculum/...` from Phases 1-13 and 15, including the 6 Phase 13 keys for lessons 1-6 of this
same module) already present. After this phase, the file should have 101 + 5 = **106 total keys**.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-agentic-systems-integrations-{lesson-number:00}-concept-check-{01|02}` (lesson-number
is 07-11 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 5 lessons.
Lessons 7, 8, and 9 are each anchored by a concrete mechanism (a connector's auth/pagination/
rate-limit handling, a multi-system failure-and-trace-propagation path, a fuzzy-matching-plus-
golden-record pipeline) that could plausibly be diagrammed, but in every one of these 3 cases the
Practical Backend Scenario prose already walks through that exact same mechanism step by step —
the diagram would restate, not add. Lesson 10 ("Build: CRM-to-AI Support Copilot") is the one
genuine candidate: it is a multi-actor, multi-boundary assembled system (webhook → orchestrator →
crosswalk resolution → worker dispatch → MCP servers → connectors → human-approval gate → source
systems) whose full shape a reader would otherwise have to construct mentally from prose alone,
which is the kind of non-obvious, multi-actor flow §8a's inclusion test is written for. Lesson 11
is an assessment lesson and should not carry an architecture diagram (assessment lessons in this
curriculum do not use this pattern). **Default to omitting `architecture` for lessons 7, 8, 9, and
11. For lesson 10, apply the inclusion test yourself against the actual final scenario text you
read in the source file — if you judge the assembled end-to-end flow passes all three criteria,
include it as an annotated flow diagram (webhook entry point through to the source-system writes,
with the crosswalk-resolution and human-approval-gate nodes highlighted as the two decision
points); if you judge it does not clearly pass, omit it and say so in Output C.** If in doubt on
any lesson, omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-agentic-systems-integrations-{lesson-number:00}-mcq-{01, 02, ...}`. None of this
phase's questions need a `codeBlock` field — omit it for all of them.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the existing cases in `GetAuthoredFdeLessonContent` (exactly 79, from Phases 1-13 and 15
  — including the 6 Phase 13 cases for lessons 1-6 of this same module)
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (exactly 101 total, from Phases 1-13 and 15)
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
Full method body — all cases now present (all 79 pre-existing ones unchanged, 5 new from this
phase — 84 total), before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 101 pre-existing entries unchanged, plus the 5 new entries for this
phase (106 total).

### OUTPUT C: Architecture diagram decisions
For each of the 5 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 7, 8, 9, and 11 omitted (their candidate mechanisms are
already fully covered by their own scenario prose, or — for lesson 11 — the lesson is an
assessment); lesson 10 either included (if its assembled end-to-end flow passes your own
application of the inclusion test) or omitted with your specific reason if it does not.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 5 lessons likely already exist in the database with thin, machine-templated `ContentBody`.
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '07-api-integration-patterns-and-connector-design',
  '08-integration-failure-modes-and-debugging',
  '09-messy-customer-data-and-entity-resolution',
  '10-build-crm-to-ai-support-copilot',
  '11-assessments-agentic-system-build-and-red-team-integration-war-room'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes Module 6 ("6. Agentic Systems & Enterprise Integrations") — all 11 lessons (1-6
from Phase 13, 7-11 from this phase) should now have authored content. **Module 6 is now fully
complete (11/11).**

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after all 79 pre-existing cases,
      before `_ => null` (84 total)
- [ ] `lessonInteractions.js` has 5 new `fde-curriculum/agentic-systems-integrations/...` keys; all
      101 pre-existing keys unchanged (106 total)
- [ ] Ran the SQL reset for all 5 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 11 lessons of "6. Agentic Systems &
      Enterprise Integrations" (1-6 from Phase 13, 7-11 from this phase) render real authored
      content, and the module shows as fully complete
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
