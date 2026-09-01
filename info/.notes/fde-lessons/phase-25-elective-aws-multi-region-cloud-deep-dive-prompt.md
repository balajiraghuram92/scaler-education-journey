# Prompt for Local LLM — FDE Phase 25: Elective "AWS Multi-Region Cloud Deep Dive", Lessons 13-17 of 17 (COMPLETES THE MODULE)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-25-elective-aws-multi-region-cloud-deep-dive-content.md` in full,
and report back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do
not paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies
and MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match
what this prompt describes, STOP and report the discrepancy instead of substituting your own
content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **133 existing cases** before `_ => null`. This phase is applied after the
`elective-containerization-orchestration` module is fully authored and applied (Phases 20, 21, 22
— 17 cases) AND after this module's own first two sub-phases, Phase 23 (lessons 1-6) and Phase 24
(lessons 7-12), are applied (6 + 6 = 12 more cases). The arithmetic: 104 core + 17
Containerization/K8s + 6 (Phase 23) + 6 (Phase 24) = **133**.

**If the case count is anything other than 133, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains. In particular:
- If the count is 104, the entire electives batch is missing — stop.
- If the count is 121, Phases 20-22 are applied but Phase 23 and Phase 24 are not — stop.
- If the count is 127, Phase 23 is applied but Phase 24 is not — stop and say so explicitly; do
  NOT apply this phase's lessons 13-17 out of order ahead of lessons 7-12.
- Only proceed if the count is exactly 133.

Also confirm `app/src/data/lessonInteractions.js` has **151 existing keys** before proceeding: 18
`java-spring-lld/...` + 133 `fde-curriculum/...` (104 core + 17 Containerization/K8s + 6 from
Phase 23 + 6 from Phase 24). If this count doesn't match, STOP and report the exact count you
find.

This phase has no content dependency on the third elective (`elective-storage-networking-
reliability`), which remains entirely out of scope here, and no dependency on the Containerization/
K8s elective's own subject matter, only on its case/key counts being fully landed.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-25-elective-aws-multi-region-cloud-deep-dive-content.md`

This file contains 5 lessons — **lessons 13-17 of 17**, the final lessons in the "AWS
Multi-Region Cloud Deep Dive" elective module (`elective-aws-multi-region-cloud-deep-dive`).
**Applying this phase completes the module at 17/17 lessons** — the second of the three elective
modules to reach 100%, after Containerization/K8s. Only the third elective, "Storage, Networking &
Reliability for FDEs" (Phases 26-27, 14 lessons), will remain unauthored/unapplied after this.

Each of the 5 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s. Several MCQ blocks carry a `**CODE_BLOCK:**` field between
`QUESTION_TEXT` and `OPTIONS` (a fenced AWS CLI / IAM policy JSON / GuardDuty finding JSON snippet
the question refers to) — see §3c.

The 5 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 13 | Microservices on AWS Project | `13-microservices-on-aws-project` | 8 |
| 14 | Microservices Project: Phase 2 | `14-microservices-project-phase-2` | 8 |
| 15 | AWS Security: Identity and Network | `15-aws-security-identity-and-network` | 9 |
| 16 | AWS Security: Data and Detection | `16-aws-security-data-and-detection` | 9 |
| 17 | AWS Security Hands-on | `17-aws-security-hands-on` | 8 |

Total MCQs across all 5 lessons: **42**.

Module slug for all 5: `elective-aws-multi-region-cloud-deep-dive` (this is the SAME
`SupplementalModuleDefinition` that Phases 23 and 24 already added lessons 1-12 to — this phase
adds the final 5 lessons, completing it at 17 total).

Double-check each slug against `Slugify(lessonDefinition.Title)` yourself before using it:
lowercase, `&`→` and `, `+`→` plus `, everything else non-alphanumeric (including colons) collapsed
to `-`, trimmed. Note lesson 14's title contains a colon ("Microservices Project: Phase 2") — the
colon collapses to a hyphen, and adjacent hyphens/spaces collapse together, giving
`14-microservices-project-phase-2` (not a double hyphen) — verify this yourself against the actual
`Slugify` implementation rather than trusting this description alone.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 133 existing cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 133 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's `<!-- CHAPTER_BODY_START -->` / `<!-- CHAPTER_BODY_END -->`
  markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

**These 5 lessons' chapter bodies contain fenced code blocks (AWS CLI commands and output, ECS
`create-service`/Service Connect JSON, Java HTTP-client snippets, SQL transactional-outbox
statements, IAM policy JSON — including overly-broad "before" policies next to scoped "after"
policies — S3 bucket policy JSON, and GuardDuty finding JSON).** Copy them exactly as written,
including all indentation inside the code fences — do not reformat, re-indent, or "clean up" any
code sample. Any double quote inside a code sample (very likely inside JSON IAM policies, S3
bucket policies, and GuardDuty findings — several blocks are quote-dense) still needs to be doubled
per the rule above — be especially careful here, there are more JSON code blocks in this phase than
in any prior AWS-elective phase.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 133 existing
cases already in place. Do NOT modify `SupplementalModules`, `EnsureSupplementalModules`,
`Slugify`, `BuildSupplementalLessonContent`, or any other method.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/elective-aws-multi-region-cloud-deep-dive/{lesson-slug}'
```

e.g. `'fde-curriculum/elective-aws-multi-region-cloud-deep-dive/13-microservices-on-aws-project'`

This is the same key pattern as every core and elective module — `EnsureSupplementalModules`
builds the lesson slug the same way core modules do (`{lessonIndex+1:00}-{Slugify(Title)}`).

Do NOT touch any existing key — 18 `java-spring-lld/...` + 133 `fde-curriculum/...` (104 core + 17
Containerization/K8s + 6 Phase 23 + 6 Phase 24) = **151 total existing keys** already present.
After this phase, the file should have **156 total keys** (151 + 5 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Pick the two most non-trivial, misconception-prone points from each lesson. `id` pattern:
`lesson-fde-elective-aws-multi-region-cloud-deep-dive-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 13-17 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

Strong candidates per lesson (your own read of the final lesson text governs — these are
suggestions, not a mandate):
- Lesson 13: sync-vs-async boundary choice (Q1); why the timeout-and-fallback code degrades
  gracefully rather than failing (Q2 or Q8).
- Lesson 14: the dual-write problem and what the transactional outbox actually guarantees (Q1/Q2);
  why SQS delivery is at-least-once, not exactly-once (Q4).
- Lesson 15: the four IAM policy dimensions and why checking only `Action` misses risk (Q1); trust
  policy vs. permission policy as two independent controls (Q4).
- Lesson 16: why bucket-policy-level enforcement beats relying on application code (Q1);
  reconnaissance vs. exfiltration GuardDuty finding types (Q4).
- Lesson 17: implemented vs. tested vs. residual risk (Q1); why containment must be re-verified,
  not just applied (Q4).

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 5 lessons: (1)
the flow must be genuinely non-obvious from prose alone, (2) it must show something the Practical
Backend Scenario prose does not already cover, (3) it must give a 7-8 year developer a faster
mental model than another paragraph would.

All 5 lessons in this phase are anchored by dense, concrete code/config examples (ECS service
definitions, IAM policy JSON, SQL transactions, GuardDuty findings, CloudTrail queries) that already
make the concrete mechanism as clear as a diagram would — the default expectation is to **omit**
`architecture` for all 5. Lesson 13 (Microservices on AWS Project) is the one arguable case, since a
three-service topology with one sync and one async boundary is a genuinely spatial, multi-actor
relationship — apply the test yourself against the final lesson text; if it clearly passes, include
an `architecture` object showing `booking-service` → (sync, timeout-bounded) → `settlement-service`
→ (async, SNS/SQS) → `notification-service`, with the async boundary's decoupling point
`highlighted: true`. If in doubt on any of the 5 lessons, omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-elective-aws-multi-region-cloud-deep-dive-{lesson-number:00}-mcq-{01, 02, ...}`.

**`codeBlock` field:** Several MCQs in this phase's source file carry a `**CODE_BLOCK:**` field
inside the `QUESTION_TEXT` section — AWS CLI, ECS/SNS/SQS JSON, IAM/S3-bucket-policy JSON, SQL, Java,
or GuardDuty-finding JSON snippets the learner must read to answer (**12 such questions total**
across the 5 lessons — locate them by searching the source file for `CODE_BLOCK:`). For each of
these, set the practiceQuestions entry's `codeBlock` field to that exact code sample (verbatim,
preserving indentation) and keep `question` as pure prose per §8a's rule. All other MCQs in this
phase have no `CODE_BLOCK` field in the source — omit `codeBlock` for those.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 133 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, `EnsureSupplementalModules`,
  `SupplementalModules`, or any other method/definition in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (151 total from prior phases)
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
Full method body — all 138 cases now present (133 existing unchanged, 5 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 151 existing entries unchanged, plus the 5 new entries for this phase
(156 total).

### OUTPUT C: Architecture diagram decisions
For each of the 5 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 14, 15, 16, and 17 omitted; lesson 13 is a judgment call —
either omitted (default) or included with the sync/async service-topology framing described in
§3b above.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

### OUTPUT E: Module completion confirmation
State the total lesson count now present for `elective-aws-multi-region-cloud-deep-dive` (expect
17) and confirm this matches `SupplementalModules`' own `Lessons` list length for that module.

---

## 7. Operational note — database reset required

These 5 lessons likely already exist in the database with thin, machine-templated `ContentBody`
(from `BuildSupplementalLessonContent`'s skeleton-expansion, not this phase's authored content).
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '13-microservices-on-aws-project',
  '14-microservices-project-phase-2',
  '15-aws-security-identity-and-network',
  '16-aws-security-data-and-detection',
  '17-aws-security-hands-on'
);
```

**Note:** these slugs (`13-...` through `17-...`) may be reused across multiple modules by design
(numbering restarts per module). If your `lessons` table has a composite or module-scoped
uniqueness constraint, scope this `UPDATE` by joining to the module
(`elective-aws-multi-region-cloud-deep-dive`) explicitly instead of relying on `slug` alone —
check the schema before running this if you have any doubt, so you don't accidentally reset
lessons in a different module that happen to share the same slug.

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the "AWS Multi-Region Cloud Deep Dive" elective module at 17/17 lessons. Only the
third elective module, "Storage, Networking & Reliability for FDEs" (Phases 26-27, 14 lessons),
remains unauthored/unapplied after this phase lands.

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 133 existing cases, before
      `_ => null` (138 total)
- [ ] `lessonInteractions.js` has 5 new
      `fde-curriculum/elective-aws-multi-region-cloud-deep-dive/...` keys; all 151 pre-existing
      keys unchanged (156 total)
- [ ] Ran the SQL reset for the 5 slugs, scoped to the correct module if the schema requires it,
      then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed the "AWS Multi-Region Cloud Deep Dive"
      elective module now shows all 17/17 lessons rendering real authored content — including
      visible, correctly-formatted AWS CLI / IAM policy JSON / SQL / Java / GuardDuty-finding code
      blocks for lessons 13-17 specifically
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim
      (including fenced code blocks and their internal double quotes, especially in the IAM/S3/
      GuardDuty JSON blocks), concept checks not pre-answered on load, practice questions render
      at the bottom, and any question with a `codeBlock` renders it as a distinct monospace block
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this (42/42 blocks verified programmatically:
      exactly 4 options in A-D order, `correctOptionId`/`CORRECT_ANSWER_INDEX` matching the marked
      option, no duplicate QUESTION_IDs within any lesson), but verify none were dropped or
      duplicated during transcription
- [ ] Confirmed the "AWS Multi-Region Cloud Deep Dive" module now shows 17/17 lessons complete in
      whatever module-progress indicator the app surfaces (course listing, module header, etc.)
