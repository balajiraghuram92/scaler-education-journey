# Prompt for Local LLM — FDE Phase 24: Elective "AWS Multi-Region Cloud Deep Dive", Lessons 7-12 of 17

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-24-elective-aws-multi-region-cloud-deep-dive-content.md` in full,
and report back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do
not paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies
and MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match
what this prompt describes, STOP and report the discrepancy instead of substituting your own
content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **127 existing cases** before `_ => null`. This phase is applied after the
`elective-containerization-orchestration` module is fully authored and applied (Phases 20, 21, 22
— 17 cases) AND after Phase 23 (lessons 1-6 of this same `elective-aws-multi-region-cloud-deep-dive`
module — 6 more cases): 104 core + 17 containerization elective + 6 (Phase 23) = 127.

**If the case count is anything other than 127, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains. In particular:
- If the count is 104, 110, 116, or 121, one or more of Phases 20/21/22 (the Containerization/K8s
  elective) has not been fully applied yet — stop and say so.
- If the count is exactly 121, Phases 20-22 are done but Phase 23 (lessons 1-6 of THIS module,
  `elective-aws-multi-region-cloud-deep-dive`) has not been applied yet — stop and say so; this
  phase cannot be applied before Phase 23 since they add lessons to the same module and lesson
  ordering must stay sequential.

Also confirm `app/src/data/lessonInteractions.js` has **145 existing keys** before proceeding: 18
`java-spring-lld/...` + 127 `fde-curriculum/...` (104 core + 17 Containerization/K8s elective + 6
from Phase 23). If this count doesn't match, STOP and report the exact count you find.

This phase has no content dependency on the third elective (Storage/Networking/Reliability),
which is entirely out of scope here.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-24-elective-aws-multi-region-cloud-deep-dive-content.md`

This file contains 6 lessons — **lessons 7-12 of 17** in the "AWS Multi-Region Cloud Deep Dive"
elective module (`elective-aws-multi-region-cloud-deep-dive`), continuing directly after Phase 23's
lessons 1-6. A later phase (Phase 25) covers lessons 13-17 and completes this module at 17 total —
do not add placeholder content for those 5 lessons in this phase.

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s. Several MCQ blocks carry a `**CODE_BLOCK:**` field between
`QUESTION_TEXT` and `OPTIONS` (a fenced AWS CLI / JSON / YAML snippet the question refers to) —
see §3c.

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 7 | End-to-End Cloud Project Day | `07-end-to-end-cloud-project-day` | 8 |
| 8 | AWS ECS and ECR Introduction | `08-aws-ecs-and-ecr-introduction` | 9 |
| 9 | ECS Fundamentals | `09-ecs-fundamentals` | 9 |
| 10 | EKS Basics | `10-eks-basics` | 8 |
| 11 | EKS Advanced | `11-eks-advanced` | 9 |
| 12 | EKS Security and Operations | `12-eks-security-and-operations` | 9 |

Total MCQs across all 6 lessons: **52**.

Module slug for all 6: `elective-aws-multi-region-cloud-deep-dive` (same module as Phase 23 — this
phase adds lessons 7-12 to it, continuing the numbering; later phases add lessons 13-17,
completing it at 17 total).

Double-check each slug against `Slugify(lessonDefinition.Title)` yourself before using it:
lowercase, `&`→` and `, `+`→` plus `, everything else non-alphanumeric collapsed to `-`, trimmed.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 127 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 127 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's `<!-- CHAPTER_BODY_START -->` / `<!-- CHAPTER_BODY_END -->`
  markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

**These 6 lessons' chapter bodies contain fenced code blocks (AWS CLI commands and output, ECS
task-definition JSON, IAM trust-policy JSON, `eksctl`/Kubernetes YAML manifests, CloudWatch Logs
Insights queries).** Copy them exactly as written, including all indentation inside the code
fences — do not reformat, re-indent, or "clean up" any code sample. Any double quote inside a code
sample (very likely inside JSON — IAM policies, ECS task definitions) still needs to be doubled per
the rule above — be especially careful here since JSON is quote-heavy, and several lessons have
multiple separate fenced code blocks per chapter body (e.g. Lesson 11 has four, Lesson 12 has
four) — copy every one of them, not just the first.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 127 existing
cases already in place. Do NOT modify `SupplementalModules`, `EnsureSupplementalModules`,
`Slugify`, `BuildSupplementalLessonContent`, or any other method.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/elective-aws-multi-region-cloud-deep-dive/{lesson-slug}'
```

e.g. `'fde-curriculum/elective-aws-multi-region-cloud-deep-dive/07-end-to-end-cloud-project-day'`

This is the same key pattern as every core and elective module — `EnsureSupplementalModules`
builds the lesson slug the same way core modules do (`{lessonIndex+1:00}-{Slugify(Title)}`).

Do NOT touch any existing key — 18 `java-spring-lld/...` + 127 `fde-curriculum/...` (104 core + 17
Containerization/K8s elective + 6 from Phase 23) = **145 total existing keys** already present.
After this phase, the file should have **151 total keys** (145 + 6 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Pick the two most non-trivial, misconception-prone points from each lesson. `id` pattern:
`lesson-fde-elective-aws-multi-region-cloud-deep-dive-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 07-12 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons: (1)
the flow must be genuinely non-obvious from prose alone, (2) it must show something the Practical
Backend Scenario prose does not already cover, (3) it must give a 7-8 year developer a faster
mental model than another paragraph would.

None of this phase's 6 lessons are primarily spatial/topological the way Phase 23's VPC lesson
was — they are sequencing (Lesson 7), registry/task-definition (Lesson 8), service/target-group
(Lesson 9), and cluster-mechanics (Lessons 10-12) lessons, each already anchored by a concrete CLI
transcript or manifest that shows the actual mechanism directly. Apply the test yourself against
the final lesson text regardless — if you find a genuine exception (for instance, Lesson 11's
control-plane → add-on → node-group upgrade *sequence*, or Lesson 12's IRSA OIDC-trust-policy
chain, could arguably benefit from a diagram if the final prose reads as non-obvious to you), you
may include `architecture` for that one lesson with a one-sentence justification in Output C. If
in doubt, omit — the module's existing pattern (Phase 23 omitted 4 of 6) is to include only when
clearly justified.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-elective-aws-multi-region-cloud-deep-dive-{lesson-number:00}-mcq-{01, 02, ...}`.

**`codeBlock` field:** Several MCQs in this phase's source file carry a `**CODE_BLOCK:**` field
inside the `QUESTION_TEXT` section — AWS CLI, ECS task-definition JSON, IAM trust-policy JSON, or
Kubernetes/`eksctl` YAML snippets the learner must read to answer (locate them by searching the
source file for `CODE_BLOCK:` — there are multiple per lesson in several of the 6). For each of
these, set the practiceQuestions entry's `codeBlock` field to that exact code sample (verbatim,
preserving indentation) and keep `question` as pure prose per §8a's rule. All other MCQs in this
phase have no `CODE_BLOCK` field in the source — omit `codeBlock` for those.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 127 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, `EnsureSupplementalModules`,
  `SupplementalModules`, or any other method/definition in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (145 total from prior phases)
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
Full method body — all 133 cases now present (127 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 145 existing entries unchanged, plus the 6 new entries for this phase
(151 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected default: all 6 omitted, unless your own read of the final text finds
a genuine exception per §3b — if you include one, name which lesson and why.

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
  '07-end-to-end-cloud-project-day',
  '08-aws-ecs-and-ecr-introduction',
  '09-ecs-fundamentals',
  '10-eks-basics',
  '11-eks-advanced',
  '12-eks-security-and-operations'
);
```

**Note:** these slugs (`07-...` through `12-...`) are reused across multiple modules by design
(numbering restarts per module). If your `lessons` table has a composite or module-scoped
uniqueness constraint, scope this `UPDATE` by joining to the module
(`elective-aws-multi-region-cloud-deep-dive`) explicitly instead of relying on `slug` alone —
check the schema before running this if you have any doubt, so you don't accidentally reset
lessons in a different module that happen to share the same slug (this module's own Lessons 7-12
in the C# skeleton have distinct titles from lessons 7-12 of the Containerization/K8s elective, so
a plain slug match should be safe, but verify against your actual schema regardless).

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes lessons 7-12 of 17 in the "AWS Multi-Region Cloud Deep Dive" elective module,
bringing it to 12/17. Lessons 13-17 remain for Phase 25, which completes the module — not in scope
for this phase.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 127 existing cases, before
      `_ => null` (133 total)
- [ ] `lessonInteractions.js` has 6 new
      `fde-curriculum/elective-aws-multi-region-cloud-deep-dive/...` keys; all 145 pre-existing
      keys unchanged (151 total)
- [ ] Ran the SQL reset for the 6 slugs, scoped to the correct module if the schema requires it,
      then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed the "AWS Multi-Region Cloud Deep Dive"
      elective module now shows lessons 1-12 rendering real authored content (1-6 from Phase 23,
      7-12 from this phase) — including visible, correctly-formatted AWS CLI / JSON / YAML code
      blocks — and lessons 13-17 still show placeholder/skeleton-expanded content pending Phase 25
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim
      (including every fenced code block — several lessons have more than one), concept checks
      not pre-answered on load, practice questions render at the bottom, and any question with a
      `codeBlock` renders it as a distinct monospace block
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this (52/52 blocks verified programmatically:
      exactly 4 options in A-D order, `correctOptionId` matching the marked option), but verify
      none were dropped or duplicated during transcription
