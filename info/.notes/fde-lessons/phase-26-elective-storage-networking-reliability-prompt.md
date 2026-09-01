# Prompt for Local LLM — FDE Phase 26: Elective "Storage, Networking & Reliability for FDEs", Lessons 1-7 of 14

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-26-elective-storage-networking-reliability-content.md` in full,
and report back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do
not paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies
and MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match
what this prompt describes, STOP and report the discrepancy instead of substituting your own
content.

---

## 0. Prerequisite check

This is the **first phase of the THIRD and FINAL elective module**. It is applied only after BOTH
the `elective-containerization-orchestration` module (17 lessons, Phases 20-22) AND the
`elective-aws-multi-region-cloud-deep-dive` module (17 lessons, Phases 23-25) are fully authored
and applied.

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **138 existing cases** before `_ => null`. That figure is 104 core cases + 17
Containerization/K8s elective cases + 17 AWS Multi-Region elective cases = 138.

**If the case count is anything other than 138, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains. In particular:
- If the count is 104, no electives have been applied yet.
- If the count is 110, 116, or 121, the Containerization/K8s elective is only partially applied.
- If the count is 127 or 133, the AWS Multi-Region elective is only partially applied.
- Any of these means a prior phase has not been applied yet — stop and say so rather than
  proceeding out of order.

Also confirm `app/src/data/lessonInteractions.js` has **156 existing keys** before proceeding: 18
`java-spring-lld/...` + 138 `fde-curriculum/...` (104 core + 17 Containerization/K8s + 17 AWS
Multi-Region). If this count doesn't match, STOP and report the exact count you find.

This phase has no content dependency on either completed elective's actual subject matter, only
on their case/key counts being fully landed. It also has no dependency on lessons 8-14 of this
same module (`elective-storage-networking-reliability`), which are entirely out of scope here and
covered by a later Phase 27.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-26-elective-storage-networking-reliability-content.md`

This file contains 7 lessons — **lessons 1-7 of 14** in a brand-new elective module, "Storage,
Networking & Reliability for FDEs" (`elective-storage-networking-reliability`). This is the
**third and final of three elective modules** now in scope. A later phase (27, covering lessons
8-14) completes this module at 14 total — do not add placeholder content for those 7 lessons in
this phase. Once Phase 27 lands, the entire ~152-lesson FDE curriculum (104 core + 17 + 17 + 14
elective lessons) is complete.

Each of the 7 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s. Several MCQ blocks carry a `**CODE_BLOCK:**` field between
`QUESTION_TEXT` and `OPTIONS` (a fenced Terraform / AWS CLI / JSON snippet the question refers
to) — see §3c.

The 7 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 1 | Architect the Storage for an Application | `01-architect-the-storage-for-an-application` | 8 |
| 2 | Data Lifecycle Management and Storage Optimization | `02-data-lifecycle-management-and-storage-optimization` | 8 |
| 3 | Backup and Disaster Recovery Strategies | `03-backup-and-disaster-recovery-strategies` | 9 |
| 4 | Designing the Networking of an Application | `04-designing-the-networking-of-an-application` | 8 |
| 5 | Load Balancing and Auto Scaling Groups | `05-load-balancing-and-auto-scaling-groups` | 8 |
| 6 | Designing for Scalability of Application and Data | `06-designing-for-scalability-of-application-and-data` | 8 |
| 7 | Database Sharding Strategies and Hot-Spot Mitigation | `07-database-sharding-strategies-and-hot-spot-mitigation` | 9 |

Total MCQs across all 7 lessons: **58**.

Module slug for all 7: `elective-storage-networking-reliability` (this is a brand-new
`SupplementalModuleDefinition` — this is its first phase; a later phase adds lessons 8-14 to the
same module, completing it at 14 total).

Double-check each slug against `Slugify(lessonDefinition.Title)` yourself before using it:
lowercase, `&`→` and `, `+`→` plus `, everything else non-alphanumeric collapsed to `-`, trimmed.
None of these 7 titles contain `&` or `+`, so each slug is a straightforward lowercase-and-hyphenate
of the title.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 138 existing cases
followed by `_ => null`. Add 7 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 138 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's `<!-- CHAPTER_BODY_START -->` / `<!-- CHAPTER_BODY_END -->`
  markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

**These 7 lessons' chapter bodies contain fenced code blocks (Terraform/HCL, AWS CLI commands and
output, JSON lifecycle policies and target-group/scaling configuration, and plain-text subnet
layouts and shard-distribution worked examples).** Copy them exactly as written, including all
indentation inside the code fences — do not reformat, re-indent, or "clean up" any code sample.
Any double quote inside a code sample (the JSON blocks especially) still needs to be doubled per
the rule above — be especially careful here since JSON is quote-heavy.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 138 existing
cases already in place. Do NOT modify `SupplementalModules`, `EnsureSupplementalModules`,
`Slugify`, `BuildSupplementalLessonContent`, or any other method.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 7 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/elective-storage-networking-reliability/{lesson-slug}'
```

e.g. `'fde-curriculum/elective-storage-networking-reliability/01-architect-the-storage-for-an-application'`

This is the same key pattern as every core and elective module — `EnsureSupplementalModules`
builds the lesson slug the same way core modules do (`{lessonIndex+1:00}-{Slugify(Title)}`).

Do NOT touch any existing key — 18 `java-spring-lld/...` + 138 `fde-curriculum/...` (104 core +
17 Containerization/K8s + 17 AWS Multi-Region) = **156 total existing keys** already present.
After this phase, the file should have **163 total keys** (156 + 7 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Pick the two most non-trivial, misconception-prone points from each lesson. `id` pattern:
`lesson-fde-elective-storage-networking-reliability-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 01-07 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 7 lessons: (1)
the flow must be genuinely non-obvious from prose alone, (2) it must show something the Practical
Backend Scenario prose does not already cover, (3) it must give a 7-8 year developer a faster
mental model than another paragraph would.

Lesson 4 (Designing the Networking of an Application) is the strongest candidate in this phase —
the three-tier subnet/trust-boundary layout (public ALB subnet, private app subnet, private data
subnet, with the specific ingress-only relationships between them) is a genuinely spatial,
multi-component relationship a diagram can clarify faster than prose. Apply the test yourself
against the actual final lesson text — if it clearly passes, include an `architecture` object
modeling the three-tier subnet/trust-boundary relationship with the data-tier boundary highlighted
(`highlighted: true`); if the existing plain-text subnet layout block already makes the topology as
clear as a diagram would, omit it. For lessons 1, 2, 3, 5, 6, and 7: these are a storage-decision
lesson, a lifecycle-policy lesson, a backup/restore-runbook lesson, a load-balancer/scaling-config
lesson, a bottleneck-capacity-modeling lesson, and a shard-key-comparison lesson respectively, each
anchored by a code/config example or worked numeric comparison that already shows the concrete
mechanism — omit `architecture` for all six unless your own read finds a genuine exception. If in
doubt on any lesson, omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-elective-storage-networking-reliability-{lesson-number:00}-mcq-{01, 02, ...}`.

**`codeBlock` field:** Several MCQs in this phase's source file carry a `**CODE_BLOCK:**` field
inside the `QUESTION_TEXT` section — Terraform, JSON (lifecycle policy, target-group config,
scaling policy), or plain-text subnet/shard-distribution snippets the learner must read to
answer (8 such questions total across the 7 lessons — one per lesson except lesson 5, which has
two; locate them by searching the source file for `CODE_BLOCK:`). For each of these, set the
practiceQuestions entry's `codeBlock` field to that exact code sample (verbatim, preserving
indentation) and keep `question` as pure prose per §8a's rule. All other MCQs in this phase have
no `CODE_BLOCK` field in the source — omit `codeBlock` for those.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 7 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 138 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, `EnsureSupplementalModules`,
  `SupplementalModules`, or any other method/definition in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (156 total from prior phases)
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
Full method body — all 145 cases now present (138 existing unchanged, 7 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 156 existing entries unchanged, plus the 7 new entries for this phase
(163 total).

### OUTPUT C: Architecture diagram decisions
For each of the 7 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 1, 2, 3, 5, 6, and 7 omitted; lesson 4 is a judgment call —
either omitted (default) or included with the three-tier subnet/trust-boundary framing described
in §3b above.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 7 lessons likely already exist in the database with thin, machine-templated `ContentBody`
(from `BuildSupplementalLessonContent`'s skeleton-expansion, not this phase's authored content).
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-architect-the-storage-for-an-application',
  '02-data-lifecycle-management-and-storage-optimization',
  '03-backup-and-disaster-recovery-strategies',
  '04-designing-the-networking-of-an-application',
  '05-load-balancing-and-auto-scaling-groups',
  '06-designing-for-scalability-of-application-and-data',
  '07-database-sharding-strategies-and-hot-spot-mitigation'
);
```

**Note:** these slugs (`01-...` through `07-...`) are reused across multiple modules by design
(numbering restarts per module). If your `lessons` table has a composite or module-scoped
uniqueness constraint, scope this `UPDATE` by joining to the module
(`elective-storage-networking-reliability`) explicitly instead of relying on `slug` alone —
check the schema before running this if you have any doubt, so you don't accidentally reset
lessons in a different module that happen to share the same slug.

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the first 7 of 14 lessons in the "Storage, Networking & Reliability for FDEs"
elective module. Lessons 8-14 remain for Phase 27 — not in scope for this phase. Once Phase 27
lands, this is the final phase of the entire ~152-lesson FDE curriculum (core + all three
electives).

---

## 8. Post-ingestion checklist

- [ ] All 7 new cases added to `GetAuthoredFdeLessonContent`, after the 138 existing cases, before
      `_ => null` (145 total)
- [ ] `lessonInteractions.js` has 7 new
      `fde-curriculum/elective-storage-networking-reliability/...` keys; all 156 pre-existing
      keys unchanged (163 total)
- [ ] Ran the SQL reset for the 7 slugs, scoped to the correct module if the schema requires it,
      then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed the "Storage, Networking & Reliability for
      FDEs" elective module appears with lessons 1-7 rendering real authored content — including
      visible, correctly-formatted Terraform / AWS CLI / JSON code blocks — and lessons 8-14
      still show placeholder/skeleton-expanded content pending Phase 27
- [ ] Spot-checked at least 2 of the 7 new lessons: content matches the source file verbatim
      (including fenced code blocks), concept checks not pre-answered on load, practice questions
      render at the bottom, and any question with a `codeBlock` renders it as a distinct
      monospace block
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this (58/58 blocks verified: exactly 4 options in
      A-D order, `correctOptionId` matching the marked option), but verify none were dropped or
      duplicated during transcription
