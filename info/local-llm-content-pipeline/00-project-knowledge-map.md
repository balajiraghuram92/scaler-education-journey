# Neuralascent — Project Knowledge Map (for a fresh LLM session)

**Purpose of this file:** let a new local LLM (or a new Claude/Codex session) understand
this workspace in one read, without re-deriving it from scratch. This is a map, not a
replacement for the detailed source-of-truth documents it points to.

**Owner / learner:** Raghuram Balaji (`balajiraghuram92@gmail.com`). Neuralascent is his
personal study site — Java/Spring backend + AI-vertical upskilling, built to also double
as a portfolio/interview artifact (Coforge AI Architect track, Azure certs, FDE self-study).

---

## 1. What Neuralascent is

Neuralascent (`https://neuralascent.top`) is a personal editorial learning platform, not a
generic course clone. Visual identity: warm/parchment editorial reading experience (serif
headings, restrained sage/teal accent, hairline rules) — deliberately **not** a SaaS
dashboard (no gauges, radar charts, progress donuts). Reference docs for the visual
language: [`../images-newdesign/v2-references/neuralascent-redesign-prompts.md`](../images-newdesign/v2-references/neuralascent-redesign-prompts.md)
and its `-v2` sibling.

Structure: `Pathway → Course → Module → Lesson ("Chapter")`. A lesson reads like a short
textbook chapter: Concepts Covered → Practical Backend Scenario → Practice Loop → Evidence
of Understanding → Suggested Extension, optionally followed by an embedded concept-check
question and/or a runnable Java coding exercise.

Two active pathways today:
- **Java Low-Level Design & Spring Architecture** (`java-spring-lld`) — OOP, concurrency,
  JVM/collections/streams, Spring Boot, SOLID/patterns, machine coding, an AI-first backend
  capstone (two parts), HLD, data engineering. ~9+ modules, 150+ lessons.
- **Forward Deployed Engineer (FDE)** — customer delivery, applied AI/LLM engineering,
  agentic systems, cloud, enterprise integration. Legacy task-tracker data plus an
  additive canonical course/module/lesson layer.

Several more pathways exist as `ComingSoon` catalog cards only (DSA, SQL, HLD/Distributed
Systems, React frontend, Data Engineering, ML/DL, AWS, DevOps) — see
[`../curriculum-modernization-tracker.md`](../curriculum-modernization-tracker.md).

## 2. Tech stack

```
React 19 + Vite  →  Nginx  →  ASP.NET Core 8 (.NET) API  →  PostgreSQL 16
Docker / Docker Compose · GitHub Actions · GHCR · AWS EC2 (ARM64)
```

A Java/Spring Boot backend migration is a **deliberate long-term learning goal**, not yet
started — see §7. Do not start it unprompted.

## 3. The content model (this is the part that matters for content work)

Backed by `api/Models/Lesson.cs` and friends. Key fields on a `Lesson` row:

| Field | Meaning |
|---|---|
| `ContentBody` | The chapter itself: one Markdown string with a fixed header contract (see §4). This is what you are improving. |
| `ContentStatus` | `Outline \| Draft \| Published \| Archived`. `Draft` = thin/template content awaiting an editorial pass. `Published` = the hand-authored, higher-quality tier. |
| `HorstmannRef` | A single citation string ("Further reading" / primary reference shown on the page). |
| `Difficulty`, `EstimatedMinutes` | Shown as chapter metadata badges. |

Side tables that a lesson can also carry (all currently **empty** for essentially every
lesson except the one POC exercise — this is under-used surface area, not dead schema):

- `LessonResource` (`api/Models/LessonResource.cs`) — further-reading items:
  `ResourceType` ∈ `StudyGuideTopic | HackMdPre | HackMdPost | PdfNotes | HorstmannRef`, `Title`, `ContentBody`.
- `LessonCodeComparison` — a labeled Before/After code pair with an explanation
  (e.g. "Before: raw thread per request" / "After: bounded executor"). Renders as the
  two-tab code comparison seen in the redesign mockups.
- `LessonDiagram` — inline SVG or a `diagram_spec_json`, with a title/caption.
- `Problem` — a lighter-weight **static problem card** (title, difficulty, problem
  statement, requirements, worked example, hints) — distinct from the heavier, Docker-executed
  coding exercise below. This is the "static Java problem cards" some lessons already show.

None of this is invented — it's real, migrated schema. A high-quality content pass should
use `ContentBody` **and** populate `LessonResource`/`LessonCodeComparison`/`LessonDiagram`
where a lesson genuinely benefits, not just fatten one markdown blob.

## 4. The `ContentBody` header contract (must match exactly)

Every lesson body is Markdown with this exact section order (see real examples in
`api/Data/JavaVerticalSeedData.cs`):

```markdown
# {Lesson Title}

## Concepts Covered
{1–2 dense paragraphs of real explanation, not bullet outlines}

## Practical Backend Scenario
{1 paragraph: a concrete, named backend/AI scenario that uses the concept}

## Practice Loop
1. {imperative step}
2. {imperative step}
3. {imperative step}
4. {imperative step}
5. {imperative step}

## Evidence of Understanding
{1 paragraph: what the learner should be able to explain/demonstrate/prove with tests}

## Suggested Extension
{1–2 sentences: a stretch task}
```

Inline code identifiers use backticks (`` `PaymentAuthorizer` ``); fenced code blocks
(```` ```java ````) are allowed and encouraged where a real snippet clarifies the point —
the current Draft-tier content under-uses this. Do not invent new top-level `##` sections;
the frontend renders these five as fixed panels (`ChapterReader`/lesson page).

## 5. Two honest quality tiers today — this is the actual gap

Verified live on 2026-08-28 (`https://neuralascent.top/chapters/java-spring-lld`):

- **Tier 1 — hand-authored, `Published`.** Modules 1–4 of the Java pathway (17 lessons):
  two dense paragraphs of Concepts Covered, a concrete named scenario, a 5-step Practice
  Loop, a real Evidence paragraph. This is the quality bar. Lesson 4
  (`oop-foundations/04-oop-3-polymorphism-interfaces`) is the flagship — it also carries a
  concept-check MCQ and the one real coding exercise.
- **Tier 2 — machine-templated, `Draft`.** Modules 5 onward (~165 additive lessons across
  Java + FDE, per the modernization tracker): one short paragraph per section, no code
  blocks, no diagrams, no resources, no exercises, no MCQs. Example verified live —
  `design-principles-patterns/patterns-01-solid` — genuinely coherent English, just thin
  and generic. **This Tier-2 population is what the user means by "mock" and wants a local
  LLM to turn into real teaching material.**

This is the concrete target: bring every Tier-2 lesson up to (or past) Tier-1 depth, using
real source material (textbooks, the Scaler curriculum PDFs/MDs the user provides,
authoritative docs) rather than free-floating generic prose.

## 6. The interactive-exercise engine — already built, barely populated

This is a separate, already-completed subsystem — **do not redesign or rebuild it**. Full
history: [`../website-assignments-reference/2.neuralascent_java_exercises_architecture_handoff.md`](../website-assignments-reference/2.neuralascent_java_exercises_architecture_handoff.md)
and the retrospective [`../website-assignments-reference/neuralascent-interactive-java-exercise-architecture-and-java-reimplementation-blueprint.md`](../website-assignments-reference/neuralascent-interactive-java-exercise-architecture-and-java-reimplementation-blueprint.md).

- Exercises live as Git-versioned packages under `exercises/java/<pathway>/<topic>/<slug>/`:
  `exercise.json` manifest + trusted `pom.xml` + `starter/` (learner-editable) +
  `tests/` (trusted, never sent to browser) + `solution/` (golden reference, lazy-loaded
  behind "View solution").
- A generic, exercise-agnostic Maven/JDK Docker runner lives in `runner/java/`. One fresh
  disposable container per Run; the image is cached, not rebuilt per submission.
- **Exactly one exercise exists today**: `exercises/java/java-lld/oop-3/point-threedpoint/`
  (the `Point`/`ThreedPoint` polymorphism exercise wired into Lesson 4). Every other lesson
  has zero coding exercises.
- The **concept-check MCQ** seen on Lesson 4 (payment-authorizer question) is real UI but,
  per [`../website-assignments-reference/1.neuralascent-java-lld-interactive-learning-blueprint.md`](../website-assignments-reference/1.neuralascent-java-lld-interactive-learning-blueprint.md),
  the generic `LearningInteraction`/`ConceptQuestion` DB-backed model described there was a
  *proposal*; verify at implementation time whether it's now generic or still a Lesson-4-only
  fixture before assuming every lesson can get one for free.

Adding an MCQ or a coding exercise to a Tier-2 lesson is valuable and in scope for the
content push, but treat it as "author one more exercise package using the existing engine,"
not "extend the platform."

## 7. Explicitly out of scope right now

- Rebuilding the backend in Java/Spring Boot. This is a real, deliberate future learning
  goal (see [`../website-assignments-reference/neuralascent-interactive-java-exercise-architecture-and-java-reimplementation-blueprint.md`](../website-assignments-reference/neuralascent-interactive-java-exercise-architecture-and-java-reimplementation-blueprint.md) §30) but happens
  **after** using the site to actually learn the material — don't let a content-authoring
  session drift into "let's migrate the API."
- Kubernetes, queues, microservices, a second EC2, S3-backed exercise storage — all
  explicitly deferred in the architecture docs. The whole system runs on one small EC2.
- The Azure certification plan, the FDE self-study calendar, and the two portfolio "rebuild
  labs" (WebRTC support platform, localization platform) in
  [`../01-project-labs-rebuild-guide.md`](../01-project-labs-rebuild-guide.md),
  [`../02-azure-certification-plan-2026.md`](../02-azure-certification-plan-2026.md),
  [`../03-fde-ai-self-study-plan.md`](../03-fde-ai-self-study-plan.md) are a **parallel,
  separate track** (interview prep for a specific role). They explain *why* certain topics
  matter to the user but are not part of the Neuralascent content pipeline.

## 8. Where things live in the repo (content work)

```
api/Data/JavaVerticalSeedData.cs     # Java pathway: course/module/lesson seed + content
api/Data/FdeCurriculumSeedData.cs    # FDE canonical course/module/lesson seed + content
api/Data/FdeSeedData.cs              # FDE legacy task tracker (completion history; do not delete)
api/Data/ChapterSeedData.cs          # shared chapter seeding helpers
api/Models/Lesson.cs                 # ContentBody / ContentStatus / Difficulty / EstimatedMinutes
api/Models/LessonResource.cs         # further-reading rows
api/Models/LessonCodeComparison.cs   # before/after code panels
api/Models/LessonDiagram.cs          # inline SVG / diagram spec
api/Models/Problem.cs                # static problem cards
exercises/java/...                   # Git-versioned coding-exercise packages
runner/java/                         # generic Maven/JDK Docker runner (Dockerfile, run.sh)
app/src/pages/ChapterReader.jsx      # (or equivalent) lesson-reading page component
```

**Critical gotcha — read before editing a seed file.** The Java seed file has two
different code paths, and they behave very differently for an *already-seeded* database
(i.e. production, which already has all these rows):

1. `GetAuthoredLessonContent(slug)` + `BackfillLessonContent()` — runs on **every** app
   startup and *can* overwrite an existing lesson's `ContentBody`, but only if
   `NeedsLessonContent()` says the current body is still a bare/short outline (no
   `## Practical Backend Scenario` + `## Practice Loop` + `## Evidence of Understanding`
   headers, or under ~900 characters). This is how Lessons 1–17 got their Tier-1 content.
2. `GetExpandedModules()` + `EnsureExpandedModules()` — this is how Modules 5+ (`Chapter(...)`
   helper calls) were added. **It only writes a lesson's `ContentBody` when the row doesn't
   exist yet, or when its body is empty / its status is still `Outline`.** Once a lesson has
   been created with Draft-tier content (which all of them now have), **editing the
   `Chapter(...)` string in source and redeploying does nothing** — the guard at
   `lesson.ContentBody` non-empty + `ContentStatus == "Draft"` (not `"Outline"`) skips the
   update silently.

So: **do not expect "edit the seed file, redeploy" to upgrade an already-Draft lesson.**
The content-population workflow (next doc) accounts for this and proposes the fix.

## 9. Full source-of-truth index

Read in this order for a deep dive; this map deliberately does not repeat their detail:

| Doc | Covers |
|---|---|
| [`../curriculum-modernization-tracker.md`](../curriculum-modernization-tracker.md) | Pathway catalog, shared-content rules, phase status, what's been added and why |
| [`../website-reference/chat-handoff-2026-08-23.md`](../website-reference/chat-handoff-2026-08-23.md) | Most recent redesign/migration runtime handoff, VM/Docker specifics, known gaps |
| [`../website-assignments-reference/1.neuralascent-java-lld-interactive-learning-blueprint.md`](../website-assignments-reference/1.neuralascent-java-lld-interactive-learning-blueprint.md) | Original interaction-model proposal (ConceptQuestion / CodingExercise / evidence) |
| [`../website-assignments-reference/2.neuralascent_java_exercises_architecture_handoff.md`](../website-assignments-reference/2.neuralascent_java_exercises_architecture_handoff.md) | Phase-1 exercise-engine build plan (Point/ThreedPoint POC), Docker runner design |
| [`../website-assignments-reference/neuralascent-interactive-java-exercise-architecture-and-java-reimplementation-blueprint.md`](../website-assignments-reference/neuralascent-interactive-java-exercise-architecture-and-java-reimplementation-blueprint.md) | Retrospective on the now-completed exercise engine; Java/Spring reimplementation blueprint |
| [`../study-tracker-webpage-redesign.md`](../study-tracker-webpage-redesign.md) | Reading Map / knowledge-atlas feature spec |
| [`../04-fde-curriculum-tracker.md`](../04-fde-curriculum-tracker.md) | Full FDE syllabus checklist (source curriculum for FDE content) |
| [`../java_aws_migration_tracker.md`](../java_aws_migration_tracker.md) | Future Spring Boot + AWS migration plan (not started) |
| This pipeline folder (`01-...`, `02-...`) | How to actually turn source material into published chapters using a local LLM |
