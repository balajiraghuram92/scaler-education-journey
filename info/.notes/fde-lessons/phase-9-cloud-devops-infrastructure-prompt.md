# Prompt for Local LLM — FDE Phase 9: Cloud, DevOps, Kubernetes & Infrastructure (Module 4), Lessons 1-6 of 12

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-9-cloud-devops-infrastructure-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with 43 existing cases (11 `agentic-ai-core` + 12 `fde-foundations` + 15
`backend-observability-data` + 5 `full-stack-ai-frontends`, covering Phases 1-8) before `_ =>
null`. If those aren't there, STOP — Phase 8 must be applied first.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-9-cloud-devops-infrastructure-content.md`

This file contains 6 lessons — lessons 1-6 of 12 in Module 4 ("4. Cloud, DevOps, Kubernetes &
Infrastructure"). This is **the first half of the module only**: a future Phase 10 will cover
lessons 7-12 (CI/CD & GitOps, Terraform, Serverless, SRE, and an Assessment) and complete the
module. Do not treat this phase as finishing Module 4.

Each lesson has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!-- CHAPTER_BODY_END
-->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block with 8-9
structured `QUESTION_BLOCK`s.

The 6 lessons, in order, with their exact database slugs:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 1 | AWS Core: IAM, VPC & Networking | `01-aws-core-iam-vpc-and-networking` | 9 |
| 2 | Compute, Storage & Managed Services (EC2, S3, RDS, SQS) | `02-compute-storage-and-managed-services-ec2-s3-rds-sqs` | 8 |
| 3 | AWS Security & Secrets Management (KMS, Secrets Manager, CloudTrail) | `03-aws-security-and-secrets-management-kms-secrets-manager-cloudtrail` | 8 |
| 4 | Docker: Production Containers | `04-docker-production-containers` | 9 |
| 5 | Kubernetes Architecture & Core Concepts | `05-kubernetes-architecture-and-core-concepts` | 9 |
| 6 | EKS, Helm & Production Kubernetes | `06-eks-helm-and-production-kubernetes` | 8 |

Module slug for all 6: `cloud-devops-infrastructure` (new module — this is its first phase, 6 of
12 lessons total).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 43 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 43 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 43 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/cloud-devops-infrastructure/{lesson-slug}'
```

e.g. `'fde-curriculum/cloud-devops-infrastructure/01-aws-core-iam-vpc-and-networking'`

Do NOT touch any existing key — 22 `java-spring-lld/...`, 11 `fde-curriculum/agentic-ai-core/...`,
12 `fde-curriculum/fde-foundations/...`, 15 `fde-curriculum/backend-observability-data/...`, and 5
`fde-curriculum/full-stack-ai-frontends/...` (65 total from Phases 1-8) already present.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two points in each lesson most likely to be
misapplied or conflated (e.g. Lesson 1's trust-policy vs. permission-boundary distinction, Lesson
5's readiness vs. liveness probes). `id` pattern:
`lesson-fde-cloud-devops-infrastructure-{lesson-number:00}-concept-check-{01|02}` (lesson-number
is 01-06 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D/E) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Add only if all three conditions from the Master Reference Guide (§8a) hold: the flow is
genuinely non-obvious from prose alone, it shows something the Practical Backend Scenario prose
does not already cover, and it would give a 7-8 year developer a faster mental model than another
paragraph.

**Lesson 5 (Kubernetes Architecture & Core Concepts) is the recommended candidate**: a diagram
showing the control plane (API server as the sole component touching etcd, with the scheduler and
controllers watching/writing through it) on one side, and worker nodes (kubelet, Pods, with a
Service's stable address routing to a changing set of Pod endpoints) on the other, with the
Deployment→ReplicaSet→Pod chain shown explicitly. This is a genuine candidate because the
API-server-as-sole-etcd-writer relationship and the Service/Deployment split are structural facts
the prose explains but doesn't visually separate — a diagram could make the "who talks to what"
question answerable at a glance. If you build this diagram, use `kind: input/service/boundary/adapter/output`
sensibly (e.g. the API server as the single `boundary`-highlighted node) and do NOT draw a linear
request→response flow — draw the actual control-plane/worker-node structural split.

**Lesson 1 (AWS Core: IAM, VPC & Networking) was considered** for an IAM trust-boundary diagram
(trust policy vs. permission policy vs. permission boundary as nested/intersecting scopes) but
default to **omitting** it unless the diagram can show the intersection relationship more clearly
than the "effective permission is always the intersection, never the union" sentence already in
the chapter body — if in doubt, omit, per the established convention in every prior phase.

For all other lessons (2, 3, 4, 6), omit the `architecture` key — none of them present a
non-linear, multi-actor flow that isn't already covered by their scenario prose.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-cloud-devops-infrastructure-{lesson-number:00}-mcq-{01, 02, ...}`. None of this
phase's questions need a `codeBlock` field — omit it.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS
data field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 43 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `ResolveModuleGuide`, `Slugify`, or any
  other method in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (22 + 11 + 12 + 15 + 5 = 65 total)
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
Full method body — all 49 cases now present (43 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 65 existing entries unchanged, plus the 6 new entries for this phase
(71 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons may already exist in the database with generic, machine-templated `ContentBody`
(Tier 2). After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '01-aws-core-iam-vpc-and-networking',
  '02-compute-storage-and-managed-services-ec2-s3-rds-sqs',
  '03-aws-security-and-secrets-management-kms-secrets-manager-cloudtrail',
  '04-docker-production-containers',
  '05-kubernetes-architecture-and-core-concepts',
  '06-eks-helm-and-production-kubernetes'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This lands lessons 1-6 of 12 in Module 4 ("4. Cloud, DevOps, Kubernetes & Infrastructure") — the
module is not yet complete; lessons 7-12 await Phase 10.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 43 existing cases, before
      `_ => null`
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/cloud-devops-infrastructure/...` keys; all
      65 pre-existing keys unchanged
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed lessons 1-6 of "4. Cloud, DevOps,
      Kubernetes & Infrastructure" render real authored content (lessons 7-12 will still show
      draft/generic content until Phase 10 lands — that's expected)
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
- [ ] If Lesson 5's architecture diagram was included, confirmed it renders and shows the
      control-plane/worker-node structural split, not a linear request/response flow
