# Prompt for Local LLM — FDE Phase 10: Cloud, DevOps, Kubernetes & Infrastructure (Module 4), Lessons 7-12 of 12 (COMPLETES MODULE 4)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-10-cloud-devops-infrastructure-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 49 existing cases (11 `agentic-ai-core` + 12 `fde-foundations` + 15
`backend-observability-data` + 5 `full-stack-ai-frontends` + 6 `cloud-devops-infrastructure`
lessons 1-6, covering Phases 1-9) before `_ => null`. If those aren't there, STOP — Phase 9 must
be applied first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-10-cloud-devops-infrastructure-content.md`

This file contains 6 lessons — lessons 7-12 of 12 in Module 4 ("4. Cloud, DevOps, Kubernetes &
Infrastructure"). **This phase completes Module 4** (12 of 12 lessons) — Phase 9 already applied
lessons 1-6 (AWS Core, Compute/Storage, AWS Security, Docker, Kubernetes Architecture, EKS/Helm).

Each lesson has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!-- CHAPTER_BODY_END
-->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block with 8-9
structured `QUESTION_BLOCK`s.

The 6 lessons, in order, with their exact database slugs:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 7 | Kubernetes Networking, Security & GPU Workloads | `07-kubernetes-networking-security-and-gpu-workloads` | 9 |
| 8 | CI/CD Pipelines & GitOps (GitHub Actions, ArgoCD) | `08-ci-cd-pipelines-and-gitops-github-actions-argocd` | 8 |
| 9 | Terraform & Infrastructure as Code | `09-terraform-and-infrastructure-as-code` | 8 |
| 10 | Serverless & Event-Driven Cloud (Lambda, API Gateway, Step Functions) | `10-serverless-and-event-driven-cloud-lambda-api-gateway-step-functions` | 9 |
| 11 | SRE & Reliability Engineering for FDEs | `11-sre-and-reliability-engineering-for-fdes` | 9 |
| 12 | Assessment: Deploy, Break, Fix on Cloud | `12-assessment-deploy-break-fix-on-cloud` | 8 |

Module slug for all 6: `cloud-devops-infrastructure` (same module as Phase 9 — this phase adds its
remaining 6 of 12 lessons and completes it).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 49 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 49 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 49 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/cloud-devops-infrastructure/{lesson-slug}'
```

e.g. `'fde-curriculum/cloud-devops-infrastructure/07-kubernetes-networking-security-and-gpu-workloads'`

Do NOT touch any existing key — 22 `java-spring-lld/...`, 11 `fde-curriculum/agentic-ai-core/...`,
12 `fde-curriculum/fde-foundations/...`, 15 `fde-curriculum/backend-observability-data/...`, 5
`fde-curriculum/full-stack-ai-frontends/...`, and 6 `fde-curriculum/cloud-devops-infrastructure/...`
(lessons 1-6, from Phase 9) — 71 total from Phases 1-9 — already present. After this phase, the
`cloud-devops-infrastructure` module will have 12 keys total (6 from Phase 9 + 6 new here), and
`lessonInteractions.js` will have 77 keys total.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two points in each lesson most likely to be
misapplied or conflated (e.g. Lesson 7's NetworkPolicy-enforcement-depends-on-CNI point, Lesson
9's dual state-locking-and-drift distinction). `id` pattern:
`lesson-fde-cloud-devops-infrastructure-{lesson-number:00}-concept-check-{01|02}` (lesson-number
is 07-12 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from the Master Reference Guide (§8a) hold: the flow is
genuinely non-obvious from prose alone, it shows something the Practical Backend Scenario prose
does not already cover, and it would give a 7-8 year developer a faster mental model than another
paragraph.

**Lesson 8 (CI/CD Pipelines & GitOps) was considered** for a diagram showing the CI pipeline
(GitHub Actions: test → build → push → commit to manifests repo) on one side and ArgoCD's
pull-based reconciliation loop (watch manifests repo → diff against live cluster → apply → self-heal)
on the other, making the "CI never touches the cluster; ArgoCD is the only writer" claim visible at
a glance instead of read as prose. This is a genuine candidate because it's a multi-actor,
two-loop flow (a push-based CI loop feeding a pull-based CD loop) that prose has to describe
sequentially even though the two loops actually run independently and asynchronously. **Default
to including it** if you build it: use `kind: input/service/boundary/adapter/output` with the
manifests repo Git commit as the single `boundary`-highlighted node (the one thing both loops
actually share), and do NOT draw a single linear pipeline — draw the two loops meeting at that one
shared boundary node.

**Lesson 11 (SRE & Reliability Engineering) was considered** for an SLO/error-budget burn-down
diagram but default to **omitting** it — the burn-rate formula and the concrete numeric example
already in the chapter body communicate the same relationship, and a diagram here would mostly
restate arithmetic already shown in prose, which fails the inclusion test.

For all other lessons (7, 9, 10, 12), omit the `architecture` key — none of them present a
non-linear, multi-actor flow that isn't already covered by their scenario prose.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-cloud-devops-infrastructure-{lesson-number:00}-mcq-{01, 02, ...}`. None of this
phase's questions need a `codeBlock` field — omit it.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS
data field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise, including Lesson 12 (the assessment) — same
convention as the two earlier assessment lessons in this course ("Assessment: Python Engineering
Challenge" and "Assessment: Data Pipeline Build & Debug"), which also carry no separate coding
exercise entry. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 49 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `ResolveModuleGuide`, `Slugify`, or any
  other method in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 + 11 + 12 + 15 + 5 + 6 = 71 total)
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
Full method body — all 55 cases now present (49 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 71 existing entries unchanged, plus the 6 new entries for this phase
(77 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed. Lesson 12 is the
assessment and, matching the two earlier assessment lessons in this course, carries no separate
coding exercise."

---

## 7. Operational note — database reset required

These 6 lessons may already exist in the database with generic, machine-templated `ContentBody`
(Tier 2). After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '07-kubernetes-networking-security-and-gpu-workloads',
  '08-ci-cd-pipelines-and-gitops-github-actions-argocd',
  '09-terraform-and-infrastructure-as-code',
  '10-serverless-and-event-driven-cloud-lambda-api-gateway-step-functions',
  '11-sre-and-reliability-engineering-for-fdes',
  '12-assessment-deploy-break-fix-on-cloud'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This lands lessons 7-12 of 12 in Module 4 ("4. Cloud, DevOps, Kubernetes & Infrastructure") —
**Module 4 is now complete (12 of 12 lessons)** across Phase 9 and this phase together.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 49 existing cases, before
      `_ => null` (55 total)
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/cloud-devops-infrastructure/...` keys; all
      71 pre-existing keys unchanged (77 total)
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 12 lessons of "4. Cloud, DevOps,
      Kubernetes & Infrastructure" now render real authored content (Module 4 is complete)
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
- [ ] Confirmed Lesson 12 (the assessment) renders with no coding exercise widget, matching the
      two earlier assessment lessons in this course
- [ ] If Lesson 8's architecture diagram was included, confirmed it renders and shows the two
      independent loops (CI push, ArgoCD pull) meeting at the manifests-repo commit, not a single
      linear pipeline
