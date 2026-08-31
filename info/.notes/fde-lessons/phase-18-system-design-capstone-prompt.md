# Prompt for Local LLM — FDE Phase 18: System Design, Capstone & Hiring Readiness (Module 8), Lessons 6-10 of 14

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-18-system-design-capstone-content.md` in full, and report
back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not
paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies and
MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match what
this prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **95 existing cases** before `_ => null`. This phase is applied third in a
four-phase batch touching Module 7 and Module 8: Phase 16 (Module 7, lessons 7-12, 6 cases) is
applied first, then Phase 17 (Module 8, lessons 1-5, 5 cases), then this Phase 18. 95 = 84 cases
already on disk prior to this batch + 6 from Phase 16 + 5 from Phase 17.

**If the case count is anything other than 95, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains.

Also confirm `app/src/data/lessonInteractions.js` has **113 existing keys** before proceeding: 18
`java-spring-lld/...` + 95 `fde-curriculum/...` keys (84 already on disk prior to this batch + 6
from Phase 16 + 5 from Phase 17). If this count doesn't match, STOP and report the exact count you
find.

One thing this check deliberately does NOT require: Module 8's lessons 11-14 (Capstone Demo Day,
Interview Readiness & Career Launch, FDE Mock Engagement, Graduation Review) do not need to exist
yet. A sibling Phase 19 covers those and may land before or after this phase — Module 8 will show
only 10 of 14 lessons with authored content when this phase lands (5 from Phase 17 + 5 from this
phase), and that is expected and has no bearing on this phase. This phase's only real dependency
is the **case count being exactly 95** before you begin.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-18-system-design-capstone-content.md`

This file contains 5 lessons, the **middle third** of Module 8 ("8. System Design, Capstone &
Hiring Readiness"), lessons 6-10 of 14. A sibling Phase 17 (authored separately, may already be
applied) covers lessons 1-5 (Distributed Systems Fundamentals + four System Design scenario
lessons). A sibling Phase 19 (authored separately) covers lessons 11-14 (Capstone Demo Day,
Interview Readiness & Career Launch, FDE Mock Engagement, Graduation Review) and completes the
module — do not add placeholder content for those 4 lessons in this phase.

The four Capstone Sprint lessons in this phase (7-10) form one continuous fictional engagement —
Meridian Risk Partners, an insurance MGA, and the SubmissionIQ platform an FDE builds for them
across all four sprints. This is intentional narrative continuity; do not treat each sprint lesson
as an independent, unrelated case study.

Each of the 5 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block with
structured `QUESTION_BLOCK`s, and a single `Reference:` line after the MCQ section.

The 5 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 6 | System Design Interview Framework & Practice | `06-system-design-interview-framework-and-practice` | 8 |
| 7 | Capstone Sprint 1: Discovery & Solution Design | `07-capstone-sprint-1-discovery-and-solution-design` | 8 |
| 8 | Capstone Sprint 2: Core Build & Integration Layer | `08-capstone-sprint-2-core-build-and-integration-layer` | 9 |
| 9 | Capstone Sprint 3: Harden, Secure & Observe | `09-capstone-sprint-3-harden-secure-and-observe` | 9 |
| 10 | Capstone Sprint 4: Red-Team, Eval & Fix | `10-capstone-sprint-4-red-team-eval-and-fix` | 8 |

Total MCQs across all 5 lessons: **42**.

Module slug for all 5: `system-design-capstone` (this module already exists from Phase 17's
lessons 1-5 — do not create a new module, only add lessons to the existing one).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 95 existing cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 95 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 95 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/system-design-capstone/{lesson-slug}'
```

e.g. `'fde-curriculum/system-design-capstone/06-system-design-interview-framework-and-practice'`

Do NOT touch any existing key — 18 `java-spring-lld/...` + 95 `fde-curriculum/...` = **113 total
existing keys** already present. After this phase, the file should have **118 total keys** (113 +
5 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-system-design-capstone-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 06-10 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

For the four Capstone Sprint lessons (7-10), prefer picking concept-check points that test the
*reasoning* behind a design decision in the Meridian/SubmissionIQ narrative (why the hybrid
architecture, why the seam-before-stub build order, why a business-rule check rather than a schema
check) over points that only test recall of a named fact from the scenario.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 5 lessons.

Lesson 8 ("Capstone Sprint 2: Core Build & Integration Layer") is the one genuine candidate — its
Concepts Covered describes an orchestrator-worker recommendation flow (an unblocked
`intake-summary-worker` alongside a gated `recommend-worker` that calls `appetite_check` and
`atlas_lookup` before its proposal reaches a human-approval gate) combined with an MCP-server-and-
connector layer underneath it, a multi-actor composition that is not fully obvious from the prose
alone. If you include an `architecture` object for lesson 8, model the orchestrator, the two
workers, the human-approval gate, and the `atlas-mcp-server`/`AtlasConnector` boundary as distinct
nodes with the human-approval gate highlighted (`highlighted: true`) as the enforcement point, per
§8a's node shape — do not model it as a simple linear intake→extract→recommend→export flow, since
that repeats what the Practical Backend Scenario prose already states; the diagram only earns its
place if it makes the "proposal versus gated execution" relationship visually clearer than the
prose does.

For lessons 6, 7, 9, and 10: these are an interview-framework lesson, a discovery/scoping lesson, a
hardening/observability lesson, and a red-team/eval lesson respectively, and none describe a
multi-actor async flow, decorator chain, or runtime-branching pattern beyond what the scenario
prose or a single before/after contrast already covers — omit `architecture` for all four. If in
doubt on lesson 8, omit it as well; a diagram is not required for this phase to be complete.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-system-design-capstone-{lesson-number:00}-mcq-{01, 02, ...}`. None of this phase's
questions need a `codeBlock` field — omit it for all 42 questions; none of them require reading a
multi-line code sample to answer.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 95 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (113 total from before this phase)
- `lessonExerciseAssociations.js`
- Any CSS file, any other `.cs` file, any other `.js` file
- The `getLessonInteractions` export at the bottom of `lessonInteractions.js`
- Any lesson belonging to Module 8 lessons 1-5 or 11-14 (owned by sibling Phases 17 and 19) — this
  phase only adds lessons 6-10

Match code style exactly:
- `FdeCurriculumSeedData.cs`: C# verbatim strings, double-quote escaping, 4-space indent
- `lessonInteractions.js`: single quotes, 2-space indent, trailing comma on last property

---

## 6. Output format

Produce, clearly labeled:

### OUTPUT A: The updated `GetAuthoredFdeLessonContent` method
Full method body — all 100 cases now present (95 existing unchanged, 5 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 113 existing entries unchanged, plus the 5 new entries for this phase
(118 total).

### OUTPUT C: Architecture diagram decisions
For each of the 5 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 6, 7, 9, and 10 omitted (no qualifying multi-actor or
runtime-branching flow); lesson 8 is a judgment call — either omitted (default, if the
orchestrator/worker/gate/connector diagram doesn't clearly clear the inclusion bar) or included
with the orchestrator-worker-plus-human-gate framing described in §3b above, not a linear
intake→extract→recommend→export restatement of the scenario prose.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 5 lessons likely already exist in the database with thin, machine-templated `ContentBody`.
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '06-system-design-interview-framework-and-practice',
  '07-capstone-sprint-1-discovery-and-solution-design',
  '08-capstone-sprint-2-core-build-and-integration-layer',
  '09-capstone-sprint-3-harden-secure-and-observe',
  '10-capstone-sprint-4-red-team-eval-and-fix'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the middle third of Module 8 ("8. System Design, Capstone & Hiring Readiness") —
lessons 6-10 of 14 should now have authored content. Lessons 1-5 (from sibling Phase 17) and
lessons 11-14 (from sibling Phase 19) are owned by those other phases and are not in scope here.

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 95 existing cases, before
      `_ => null` (100 total)
- [ ] `lessonInteractions.js` has 5 new `fde-curriculum/system-design-capstone/...` keys; all 113
      pre-existing keys unchanged (118 total)
- [ ] Ran the SQL reset for all 5 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 6-10 of "8. System Design, Capstone
      & Hiring Readiness" render real authored content, and lessons 11-14 still show
      placeholder/draft content pending sibling Phase 19 (lessons 1-5 should already be real if
      sibling Phase 17 has landed)
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this, but verify none were dropped or duplicated
      during transcription
- [ ] Confirmed the four Capstone Sprint lessons (7-10) read as one continuous engagement narrative
      (Meridian Risk Partners / SubmissionIQ / Coastal Underwriters) when viewed in sequence on the
      site, not as four disconnected case studies
