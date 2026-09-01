# Prompt for Local LLM — FDE Phase 23: Elective "AWS Multi-Region Cloud Deep Dive", Lessons 1-6 of 17

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-23-elective-aws-multi-region-cloud-deep-dive-content.md` in full,
and report back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do
not paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies
and MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match
what this prompt describes, STOP and report the discrepancy instead of substituting your own
content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **121 existing cases** before `_ => null`. This phase is applied after the
`elective-containerization-orchestration` module is fully authored and applied (Phases 20, 21, 22
— 6 + 6 + 5 = 17 cases on top of the 104-case core curriculum baseline: 104 + 17 = 121).

**If the case count is anything other than 121, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains. In particular,
if the count is 104, 110, or 116, one of Phases 20/21/22 has not been applied yet — stop and say
so rather than proceeding out of order.

Also confirm `app/src/data/lessonInteractions.js` has **139 existing keys** before proceeding: 18
`java-spring-lld/...` + 121 `fde-curriculum/...` (104 core + 17 from the completed
Containerization/K8s elective). If this count doesn't match, STOP and report the exact count you
find.

This phase has no content dependency on the `elective-containerization-orchestration` module's
actual subject matter, only on its case/key counts being fully landed. It also has no dependency
on the third elective (Storage/Networking/Reliability), which is entirely out of scope here.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-23-elective-aws-multi-region-cloud-deep-dive-content.md`

This file contains 6 lessons — **lessons 1-6 of 17** in a brand-new elective module, "AWS
Multi-Region Cloud Deep Dive" (`elective-aws-multi-region-cloud-deep-dive`). This is the
**second of three elective modules** now in scope. Later phases (24 covering lessons 7-12, 25
covering 13-17) complete this module at 17 total — do not add placeholder content for those 11
lessons in this phase.

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s. Several MCQ blocks carry a `**CODE_BLOCK:**` field between
`QUESTION_TEXT` and `OPTIONS` (a fenced AWS CLI / Terraform / JSON policy snippet the question
refers to) — see §3c.

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 1 | AWS VPC and Networking Basics | `01-aws-vpc-and-networking-basics` | 9 |
| 2 | Advanced AWS Networking | `02-advanced-aws-networking` | 8 |
| 3 | AWS Observability with CloudWatch | `03-aws-observability-with-cloudwatch` | 10 |
| 4 | CloudWatch and CloudTrail Advanced | `04-cloudwatch-and-cloudtrail-advanced` | 10 |
| 5 | Docker App on EC2 Project | `05-docker-app-on-ec2-project` | 9 |
| 6 | AWS Lambda and API Gateway | `06-aws-lambda-and-api-gateway` | 9 |

Total MCQs across all 6 lessons: **55**.

Module slug for all 6: `elective-aws-multi-region-cloud-deep-dive` (this is a brand-new
`SupplementalModuleDefinition` — this is its first phase; later phases add lessons 7-17 to the
same module, completing it at 17 total).

Double-check each slug against `Slugify(lessonDefinition.Title)` yourself before using it:
lowercase, `&`→` and `, `+`→` plus `, everything else non-alphanumeric collapsed to `-`, trimmed.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 121 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 121 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's `<!-- CHAPTER_BODY_START -->` / `<!-- CHAPTER_BODY_END -->`
  markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

**These 6 lessons' chapter bodies contain fenced code blocks (AWS CLI commands and output,
Terraform/CloudFormation snippets, IAM policy JSON, CloudWatch Logs Insights queries, Lambda
function code).** Copy them exactly as written, including all indentation inside the code
fences — do not reformat, re-indent, or "clean up" any code sample. Any double quote inside a
code sample (very likely inside JSON IAM policies) still needs to be doubled per the rule above —
be especially careful here since JSON is quote-heavy.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 121 existing
cases already in place. Do NOT modify `SupplementalModules`, `EnsureSupplementalModules`,
`Slugify`, `BuildSupplementalLessonContent`, or any other method.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/elective-aws-multi-region-cloud-deep-dive/{lesson-slug}'
```

e.g. `'fde-curriculum/elective-aws-multi-region-cloud-deep-dive/01-aws-vpc-and-networking-basics'`

This is the same key pattern as every core and elective module — `EnsureSupplementalModules`
builds the lesson slug the same way core modules do (`{lessonIndex+1:00}-{Slugify(Title)}`).

Do NOT touch any existing key — 18 `java-spring-lld/...` + 121 `fde-curriculum/...` (104 core +
17 from the completed Containerization/K8s elective) = **139 total existing keys** already
present. After this phase, the file should have **145 total keys** (139 + 6 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Pick the two most non-trivial, misconception-prone points from each lesson. `id` pattern:
`lesson-fde-elective-aws-multi-region-cloud-deep-dive-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 01-06 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons: (1)
the flow must be genuinely non-obvious from prose alone, (2) it must show something the Practical
Backend Scenario prose does not already cover, (3) it must give a 7-8 year developer a faster
mental model than another paragraph would.

Lesson 1 (AWS VPC and Networking Basics) and lesson 2 (Advanced AWS Networking) are the strongest
candidates in this phase — VPC/subnet/route-table topology and any peering/Transit Gateway content
are genuinely spatial, multi-component relationships that a diagram can clarify faster than prose.
Apply the test yourself against the actual final lesson text — if either clearly passes, include an
`architecture` object modeling the VPC/subnet/route-table/gateway relationship with the
public/private subnet boundary highlighted (`highlighted: true`); if the existing CIDR-layout code
block and CLI walkthrough already make the topology as clear as a diagram would, omit it. For
lessons 3, 4, 5, and 6: these are an observability-tooling lesson, an advanced-observability
lesson, a hands-on project lesson, and a serverless lesson respectively, each anchored by CLI/code
examples that already show the concrete mechanism — omit `architecture` for all four unless your
own read finds a genuine exception. If in doubt on any lesson, omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-elective-aws-multi-region-cloud-deep-dive-{lesson-number:00}-mcq-{01, 02, ...}`.

**`codeBlock` field:** Several MCQs in this phase's source file carry a `**CODE_BLOCK:**` field
inside the `QUESTION_TEXT` section — AWS CLI, Terraform, or JSON policy snippets the learner must
read to answer (12 such questions total across the 6 lessons — locate them by searching the
source file for `CODE_BLOCK:`). For each of these, set the practiceQuestions entry's `codeBlock`
field to that exact code sample (verbatim, preserving indentation) and keep `question` as pure
prose per §8a's rule. All other MCQs in this phase have no `CODE_BLOCK` field in the source — omit
`codeBlock` for those.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 121 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, `EnsureSupplementalModules`,
  `SupplementalModules`, or any other method/definition in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (139 total from prior phases)
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
Full method body — all 127 cases now present (121 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 139 existing entries unchanged, plus the 6 new entries for this phase
(145 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 3, 4, 5, and 6 omitted; lessons 1 and 2 are judgment
calls — either omitted (default) or included with the VPC/subnet/gateway topology framing
described in §3b above.

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
  '01-aws-vpc-and-networking-basics',
  '02-advanced-aws-networking',
  '03-aws-observability-with-cloudwatch',
  '04-cloudwatch-and-cloudtrail-advanced',
  '05-docker-app-on-ec2-project',
  '06-aws-lambda-and-api-gateway'
);
```

**Note:** these slugs (`01-...` through `06-...`) are reused across multiple modules by design
(numbering restarts per module). If your `lessons` table has a composite or module-scoped
uniqueness constraint, scope this `UPDATE` by joining to the module
(`elective-aws-multi-region-cloud-deep-dive`) explicitly instead of relying on `slug` alone —
check the schema before running this if you have any doubt, so you don't accidentally reset
lessons in a different module that happen to share the same slug.

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the first 6 of 17 lessons in the "AWS Multi-Region Cloud Deep Dive" elective
module. Lessons 7-17 remain for Phases 24 and 25 — neither is in scope for this phase.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 121 existing cases, before
      `_ => null` (127 total)
- [ ] `lessonInteractions.js` has 6 new
      `fde-curriculum/elective-aws-multi-region-cloud-deep-dive/...` keys; all 139 pre-existing
      keys unchanged (145 total)
- [ ] Ran the SQL reset for the 6 slugs, scoped to the correct module if the schema requires it,
      then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed the "AWS Multi-Region Cloud Deep Dive"
      elective module appears with lessons 1-6 rendering real authored content — including
      visible, correctly-formatted AWS CLI / Terraform / JSON code blocks — and lessons 7-17
      still show placeholder/skeleton-expanded content pending future phases
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim
      (including fenced code blocks), concept checks not pre-answered on load, practice questions
      render at the bottom, and any question with a `codeBlock` renders it as a distinct
      monospace block
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this (55/55 blocks verified: exactly 4 options in
      A-D order, `correctOptionId` matching the marked option), but verify none were dropped or
      duplicated during transcription
