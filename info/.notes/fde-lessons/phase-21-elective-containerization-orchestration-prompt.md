# Prompt for Local LLM — FDE Phase 21: Elective "Containerization and Orchestration", Lessons 7-12 of 17

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-21-elective-containerization-orchestration-content.md` in full, and
report back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not
paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies and
MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match what
this prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **110 existing cases** before `_ => null`. This phase is applied second in a
batch of electives: Phase 20 (elective "Containerization and Orchestration", lessons 1-6 of 17)
is applied first, adding 6 cases on top of the 104-case core curriculum baseline (104 + 6 = 110),
then this Phase 21 adds 6 more (110 + 6 = 116).

**If the case count is anything other than 110, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains. In particular,
if the count is 104, Phase 20 has not been applied yet — stop and say so rather than proceeding
out of order.

Also confirm `app/src/data/lessonInteractions.js` has **128 existing keys** before proceeding: 18
`java-spring-lld/...` + 110 `fde-curriculum/...` (104 core + 6 from Phase 20). If this count
doesn't match, STOP and report the exact count you find.

One thing this check deliberately does NOT require: this phase has no content dependency on any
other elective module (AWS Multi-Region, Storage/Networking/Reliability) — those are out of scope
entirely and irrelevant to this phase's prerequisite check. Block only on the two counts above
(110 cases, 128 keys), nothing else.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-21-elective-containerization-orchestration-content.md`

This file contains 6 lessons — the **middle section** of a **17-lesson elective module**,
`elective-containerization-orchestration` ("Containerization and Orchestration"), lessons 7-12 of
17. A sibling phase (Phase 20, applied before this one) covers lessons 1-6 (Docker Introduction
through Docker Networking Deep Dive). A later phase (Phase 22) covers lessons 13-17 (Kubernetes
Networking, Kubernetes Scaling: HPA/Cluster Autoscaler/VPA/Karpenter, Kubernetes Scaling and
Network Policies, Kubernetes Security: RBAC and DevSecOps, Kubernetes Volumes) and completes the
module — do not add placeholder content for either range in this phase.

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 7 | Hardening the Docker Environment (DevSecOps) | `07-hardening-the-docker-environment-devsecops` | 9 |
| 8 | Industry-Standard Container Hardening Demo | `08-industry-standard-container-hardening-demo` | 9 |
| 9 | Introduction to Orchestration | `09-introduction-to-orchestration` | 8 |
| 10 | Kubernetes Architecture | `10-kubernetes-architecture` | 9 |
| 11 | Kubernetes Pod Deep Dive | `11-kubernetes-pod-deep-dive` | 9 |
| 12 | ReplicaSets, Deployments, and Sidecars | `12-replicasets-deployments-and-sidecars` | 9 |

Total MCQs across all 6 lessons: **53**.

Module slug for all 6: `elective-containerization-orchestration` (this is a
`SupplementalModuleDefinition`, not one of the 8 numbered core modules — it is still part of the
same `fde-curriculum` course; this phase is its second content phase, following Phase 20 and
preceding Phase 22, which completes it at 17 total).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 110 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 110 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

**These 6 lessons' chapter bodies contain fenced code blocks (Dockerfile, YAML, bash, kubectl
output).** Copy them exactly as written, including all indentation inside the code fences — do
not reformat, re-indent, or "clean up" any code sample. A code fence uses triple backticks
(` ``` `), which need no escaping in a C# verbatim string, but any double quote that appears
inside a code sample (for example, inside a YAML string value) still needs to be doubled per the
rule above.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 110 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/elective-containerization-orchestration/{lesson-slug}'
```

e.g. `'fde-curriculum/elective-containerization-orchestration/07-hardening-the-docker-environment-devsecops'`

This is the same key pattern as the core curriculum (`fde-curriculum/{module-slug}/{lesson-slug}`)
— `EnsureSupplementalModules` builds the lesson slug the same way core modules do
(`{lessonIndex+1:00}-{Slugify(Title)}`), and the elective module is still part of the
`fde-curriculum` course, so no different key format is needed.

Do NOT touch any existing key — 18 `java-spring-lld/...` + 110 `fde-curriculum/...` (104 core +
6 from Phase 20) = **128 total existing keys** already present. After this phase, the file should
have **134 total keys** (128 + 6 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-elective-containerization-orchestration-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 07-12 for this phase, matching the lesson's position in the 17-lesson module —
do not renumber to 01-06). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

Suggested picks (source content already supports these; use judgment if a different pair reads
better once you've read the full lesson):
- Lesson 7: the SBOM-vs-scanner distinction (Q4/Q8), and the reachability-based accepted-risk
  argument (Q5) — both are genuine, easy-to-flatten misconceptions.
- Lesson 8: false-positive vs. accepted-risk (Q2), and what makes a gate auditable (Q1).
- Lesson 9: imperative vs. declarative desired state (Q1), and when orchestration is premature
  (Q3).
- Lesson 10: API-server acceptance vs. scheduling vs. readiness as three separate checkpoints
  (Q5), and Pending vs. Running-but-not-Ready as two different failure domains (Q6).
- Lesson 11: liveness vs. readiness probe failure behavior (Q2), and why Pod state does not
  survive replacement (Q4).
- Lesson 12: what a rolling update concretely is (Q2), and why old Pods kept serving traffic
  during the stalled rollout (Q4).

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons.

Lesson 10 ("Kubernetes Architecture") is the one genuine candidate — its Concepts Covered traces a
multi-actor request path (API server → etcd write → Deployment controller → ReplicaSet controller
→ scheduler → kubelet → container runtime) that is genuinely non-obvious from prose alone and is
not fully captured by the kubectl example in the chapter body (which shows a `Pending` failure,
not the full successful path). If you include an `architecture` object for lesson 10, model it as
the linear-but-multi-actor request path with the API server's `etcd` write highlighted as the one
`highlighted: true` node (per §8a's node shape: `input` for `kubectl apply`, `service` nodes for
the Deployment/ReplicaSet controllers and the scheduler, `boundary` for the API server/etcd write,
`adapter` for the kubelet/container runtime, `output` for the running container) — this is an
exception to the "no linear flow" guidance in §8a, because the point being made here is precisely
which distinct component owns which step in a chain, not a decorator/strategy/async pattern; a
diagram earns its place if it makes the six-actor handoff clearer than another paragraph would.

For lessons 7, 8, 9, 11, and 12: these are a hardening-checklist lesson, a CI-gate demo lesson, a
conceptual bridge lesson, a Pod-internals lesson, and a ReplicaSet/Deployment-mechanism lesson
respectively. None of the last two describe a flow better shown as a diagram than as the
before/after `kubectl` transcripts already in their chapter bodies — omit `architecture` for all
five. If in doubt on lesson 10, omit it as well; a diagram is not required for this phase to be
complete.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-elective-containerization-orchestration-{lesson-number:00}-mcq-{01, 02, ...}`
(lesson-number 07-12, matching the source file's lesson numbering — do not renumber to 01-06).

**`codeBlock` field:** Several MCQs in this phase's source file carry a `**CODE_BLOCK:**` field
inside the `QUESTION_TEXT` section (Lesson 7 Q3, Lesson 8 Q3, Lesson 10 Q4, Lesson 11 Q3, Lesson
12 Q3 and Q8) — these are Dockerfile, YAML, or kubectl-output snippets the learner must read to
answer. For each of these, set the practiceQuestions entry's `codeBlock` field to that exact code
sample (verbatim, preserving indentation) and keep `question` as pure prose per §8a's rule. All
other MCQs in this phase have no `CODE_BLOCK` field in the source — omit `codeBlock` for those.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 110 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, `EnsureSupplementalModules`,
  `SupplementalModules`, or any other method/definition in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (128 total from prior phases)
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
Full method body — all 116 cases now present (110 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 128 existing entries unchanged, plus the 6 new entries for this phase
(134 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 7, 8, 9, 11, and 12 omitted (no qualifying multi-actor
diagram opportunity beyond what the chapter body's code examples already show); lesson 10 is a
judgment call — either omitted (default, if the six-actor request-path diagram doesn't clearly
clear the inclusion bar) or included with the linear multi-actor framing described in §3b above.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons likely already exist in the database with thin, machine-templated `ContentBody`
(from `BuildSupplementalLessonContent`, populated from the inline skeleton in
`SupplementalModuleDefinition`). After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '07-hardening-the-docker-environment-devsecops',
  '08-industry-standard-container-hardening-demo',
  '09-introduction-to-orchestration',
  '10-kubernetes-architecture',
  '11-kubernetes-pod-deep-dive',
  '12-replicasets-deployments-and-sidecars'
);
```

**Note:** if lessons 1-6 of this same module (from Phase 20) share any of these slugs by
coincidence, do NOT include them in this `WHERE` list — this phase's SQL targets only the 6 slugs
above (lessons 7-12). Double-check the slug list against the table in Section 1 before running.

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes the middle section of the "Containerization and Orchestration" elective module —
lessons 7-12 of 17 should now have authored content. Lessons 1-6 (Phase 20) should already be
authored if applied first; lessons 13-17 remain for Phase 22, which completes the module. Neither
of those is in scope for this phase.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 110 existing cases, before
      `_ => null` (116 total)
- [ ] `lessonInteractions.js` has 6 new
      `fde-curriculum/elective-containerization-orchestration/...` keys (numbered 07-12, not
      renumbered to 01-06); all 128 pre-existing keys unchanged (134 total)
- [ ] Ran the SQL reset for exactly the 6 slugs listed in Section 7, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 7-12 of "Containerization and
      Orchestration" render real authored content — including visible, correctly-formatted code
      blocks (Dockerfile, YAML, bash/kubectl) inside the chapter body — and lessons 13-17 still
      show placeholder/draft content pending Phase 22
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim
      (including code samples), concept checks not pre-answered on load, practice questions render
      at the bottom, and any `codeBlock`-bearing MCQ renders its code sample as a distinct
      monospace block
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this (53/53 blocks verified: exactly 4 options in
      A-D order, `correctOptionId` matching the marked option), but verify none were dropped or
      duplicated during transcription
