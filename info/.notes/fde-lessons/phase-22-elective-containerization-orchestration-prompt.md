# Prompt for Local LLM — FDE Phase 22: Elective "Containerization and Orchestration", Lessons 13-17 of 17 (COMPLETES the module)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-22-elective-containerization-orchestration-content.md` in full, and
report back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not
paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies and
MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match what
this prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **116 existing cases** before `_ => null`. This phase is the third and final
phase for this elective module: Phase 20 (lessons 1-6, 6 cases) and Phase 21 (lessons 7-12, 6
cases) are applied first, adding 12 cases on top of the 104-case core curriculum baseline
(104 + 6 + 6 = 116).

**If the case count is anything other than 116, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains. In particular,
if the count is 104 or 110, Phase 20 and/or Phase 21 have not been applied yet — stop and say so
rather than proceeding out of order.

Also confirm `app/src/data/lessonInteractions.js` has **134 existing keys** before proceeding: 18
`java-spring-lld/...` + 116 `fde-curriculum/...` (104 core + 6 from Phase 20 + 6 from Phase 21).
If this count doesn't match, STOP and report the exact count you find.

This phase has no content dependency on either other elective module (AWS Multi-Region,
Storage/Networking/Reliability) — those are out of scope entirely and irrelevant to this phase's
prerequisite check. Block only on the two counts above (116 cases, 134 keys), nothing else.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-22-elective-containerization-orchestration-content.md`

This file contains 5 lessons — the **final section** of a **17-lesson elective module**,
`elective-containerization-orchestration` ("Containerization and Orchestration"), lessons 13-17 of
17. Sibling phases 20 (lessons 1-6) and 21 (lessons 7-12), applied before this one, cover the rest
of the module. **Applying this phase completes the module at 17/17 lessons.**

Each of the 5 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s. Several MCQ blocks carry a `**CODE_BLOCK:**` field between
`QUESTION_TEXT` and `OPTIONS` (a fenced YAML/kubectl snippet the question refers to) — see §3c.

The 5 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 13 | Kubernetes Networking | `13-kubernetes-networking` | 9 |
| 14 | Kubernetes Scaling: HPA, Cluster Autoscaler, VPA, and Karpenter | `14-kubernetes-scaling-hpa-cluster-autoscaler-vpa-and-karpenter` | 9 |
| 15 | Kubernetes Scaling and Network Policies | `15-kubernetes-scaling-and-network-policies` | 8 |
| 16 | Kubernetes Security: RBAC and DevSecOps | `16-kubernetes-security-rbac-and-devsecops` | 9 |
| 17 | Kubernetes Volumes | `17-kubernetes-volumes` | 8 |

Total MCQs across all 5 lessons: **43**.

Module slug for all 5: `elective-containerization-orchestration` (this is a
`SupplementalModuleDefinition`, not one of the 8 numbered core modules — it is still part of the
same `fde-curriculum` course; this is its third and final content phase, completing it at 17
total).

Double-check each slug against `Slugify(lessonDefinition.Title)` yourself before using it:
lowercase, `&`→` and `, `+`→` plus `, everything else non-alphanumeric — including colons and
commas — collapsed to `-`, trimmed.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 116 existing cases
followed by `_ => null`. Add 5 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 116 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's `<!-- CHAPTER_BODY_START -->` / `<!-- CHAPTER_BODY_END -->`
  markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

**These 5 lessons' chapter bodies contain fenced code blocks (YAML manifests — Service,
NetworkPolicy, HPA, Role/RoleBinding, PersistentVolumeClaim — plus `kubectl` commands and
output).** Copy them exactly as written, including all indentation inside the code fences — do
not reformat, re-indent, or "clean up" any code sample. Any double quote inside a code sample
(e.g. inside a YAML string value) still needs to be doubled per the rule above.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 116 existing
cases already in place. Do NOT modify `SupplementalModules`, `EnsureSupplementalModules`,
`Slugify`, `BuildSupplementalLessonContent`, or any other method.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 5 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/elective-containerization-orchestration/{lesson-slug}'
```

e.g. `'fde-curriculum/elective-containerization-orchestration/13-kubernetes-networking'`

This is the same key pattern as the core curriculum and Phases 20-21 of this same elective module.

Do NOT touch any existing key — 18 `java-spring-lld/...` + 116 `fde-curriculum/...` (104 core + 6
from Phase 20 + 6 from Phase 21) = **134 total existing keys** already present. After this phase,
the file should have **139 total keys** (134 + 5 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Pick the two most non-trivial, misconception-prone points from each lesson — favor a point with a
genuine, plausible wrong answer over a fact the learner just read verbatim. `id` pattern:
`lesson-fde-elective-containerization-orchestration-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 13-17 for this phase, matching the lesson's position in the 17-lesson module —
do not renumber to 01-05). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 5 lessons: (1)
the flow must be genuinely non-obvious from prose alone, (2) it must show something the Practical
Backend Scenario prose does not already cover, (3) it must give a 7-8 year developer a faster
mental model than another paragraph would.

Lesson 13 (Kubernetes Networking) is the strongest candidate — it involves a Service, an
Endpoints/EndpointSlice object, and a NetworkPolicy boundary as distinct actors, which is a
genuine multi-object relationship. Apply the test yourself against the actual final lesson text —
if it clearly passes, include an `architecture` object modeling the Service → Endpoints →
selected-Pods relationship with the NetworkPolicy boundary highlighted (`highlighted: true`); if
it doesn't clearly earn its place beyond the existing YAML/kubectl examples, omit it. For lessons
14, 15, 16, and 17: these are a scaling-mechanism lesson, a scaling+policy lesson, an RBAC lesson,
and a volumes lesson respectively, each anchored by a YAML manifest example that already shows the
concrete mechanism as clearly as a diagram would — omit `architecture` for all four unless your
own read finds a genuine exception. If in doubt on any lesson, omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-elective-containerization-orchestration-{lesson-number:00}-mcq-{01, 02, ...}`
(lesson-number 13-17, matching the source file's lesson numbering — do not renumber to 01-05).

**`codeBlock` field:** Several MCQs in this phase's source file carry a `**CODE_BLOCK:**` field
inside the `QUESTION_TEXT` section — YAML or kubectl-output snippets the learner must read to
answer (5 such questions total across the 5 lessons — locate them by searching the source file
for `CODE_BLOCK:`). For each of these, set the practiceQuestions entry's `codeBlock` field to that
exact code sample (verbatim, preserving indentation) and keep `question` as pure prose per §8a's
rule. All other MCQs in this phase have no `CODE_BLOCK` field in the source — omit `codeBlock` for
those.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 5 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 116 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, `EnsureSupplementalModules`,
  `SupplementalModules`, or any other method/definition in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (134 total from prior phases)
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
Full method body — all 121 cases now present (116 existing unchanged, 5 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 134 existing entries unchanged, plus the 5 new entries for this phase
(139 total).

### OUTPUT C: Architecture diagram decisions
For each of the 5 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 14, 15, 16, and 17 omitted; lesson 13 is a judgment call —
either omitted (default) or included with the Service/Endpoints/NetworkPolicy framing described
in §3b above.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

### OUTPUT E: Module completion confirmation
State: "The `elective-containerization-orchestration` module is now complete at 17/17 lessons
(lessons 1-6 from Phase 20, 7-12 from Phase 21, 13-17 from this phase)."

---

## 7. Operational note — database reset required

These 5 lessons likely already exist in the database with thin, machine-templated `ContentBody`
(from `BuildSupplementalLessonContent`'s skeleton-expansion, not this phase's authored content).
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '13-kubernetes-networking',
  '14-kubernetes-scaling-hpa-cluster-autoscaler-vpa-and-karpenter',
  '15-kubernetes-scaling-and-network-policies',
  '16-kubernetes-security-rbac-and-devsecops',
  '17-kubernetes-volumes'
);
```

**Note:** scope this `UPDATE` to only these 5 slugs — do not include lessons 1-12 of this same
module (Phases 20-21), which are out of scope for this phase's reset.

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the "Containerization and Orchestration" elective module at 17/17 lessons — the
FIRST of three elective modules now fully authored and applied. Two elective modules remain (AWS
Multi-Region Cloud Deep Dive — Phases 23-25; Storage, Networking & Reliability for FDEs — Phases
26-27).

---

## 8. Post-ingestion checklist

- [ ] All 5 new cases added to `GetAuthoredFdeLessonContent`, after the 116 existing cases, before
      `_ => null` (121 total)
- [ ] `lessonInteractions.js` has 5 new
      `fde-curriculum/elective-containerization-orchestration/...` keys (numbered 13-17, not
      renumbered); all 134 pre-existing keys unchanged (139 total)
- [ ] Ran the SQL reset for exactly the 5 slugs listed in Section 7, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 13-17 of "Containerization and
      Orchestration" render real authored content — including visible, correctly-formatted YAML
      and kubectl code blocks — and the module now shows 17/17 lessons with authored content
- [ ] Spot-checked at least 2 of the 5 new lessons: content matches the source file verbatim
      (including code samples), concept checks not pre-answered on load, practice questions render
      at the bottom, and any `codeBlock`-bearing MCQ renders its code sample as a distinct
      monospace block
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this (43/43 blocks verified: exactly 4 options in
      A-D order, `correctOptionId` matching the marked option), but verify none were dropped or
      duplicated during transcription
