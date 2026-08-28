# Content Population Workflow — Source Material → Local LLM → Published Chapter

Read [`00-project-knowledge-map.md`](00-project-knowledge-map.md) first. This document is
the repeatable per-chapter (or per-module) pipeline for turning a PDF/Markdown source into
a high-quality, live Neuralascent chapter using a local LLM.

## 0. Principles

1. **The local LLM authors; you (or a review pass) approve.** Never flip `ContentStatus`
   to `Published` without a human read-through. This mirrors the existing project rule
   ("the LLM is an authoring assistant, not automatically the source of truth for
   correctness" — see blueprint doc 1 §2.3).
2. **One chapter at a time, verified end-to-end, before batching.** Prove the loop on one
   Tier-2 lesson (recommend `patterns-01-solid` — already inspected, small, self-contained)
   before running it across dozens of lessons.
3. **Match the Tier-1 bar, not the Tier-2 template.** The target is Lesson 4's depth
   (`oop-foundations/04-oop-3-polymorphism-interfaces`), not merely "longer than before."
4. **Ground claims in real source material.** Feed the local LLM the actual PDF/MD you
   have (Scaler curriculum export, a textbook chapter, official docs) plus its own
   knowledge — don't let it free-associate a whole chapter from the title alone when a
   source document exists.
5. **Don't touch the exercise engine's trust boundaries.** New coding exercises are new
   Git-versioned packages under `exercises/java/...` with a `tests/` directory a learner
   never sees — never invert that.

## 1. Pipeline overview

```
 (A) Gather source material for one chapter
        │  PDF / .md / textbook excerpt / official docs, one per topic
        ▼
 (B) Run the Master Content Prompt (02-local-llm-prompts.md §1) against the local LLM,
     with the Per-Chapter Fill-in Template (02 §2) for this specific lesson
        │  → Markdown matching the exact ContentBody header contract
        │  → optional: LessonResource / LessonCodeComparison / LessonDiagram JSON
        │  → optional: one MCQ concept-check + (rarely) one coding-exercise package
        ▼
 (C) Human review pass (10–15 min): technical accuracy, no invented API/library facts,
     matches Tier-1 depth, code compiles/reads correctly, no leftover placeholder text
        ▼
 (D) Insert into the repo
        │  - ContentBody → the matching Chapter(...)/lesson entry in
        │    api/Data/JavaVerticalSeedData.cs (or FdeCurriculumSeedData.cs for FDE)
        │  - LessonResource / LessonCodeComparison / LessonDiagram → matching seed calls,
        │    or a small new seed method if none exists yet for that table
        ▼
 (E) Make the update actually reach the database (see §3 — the write-once gotcha)
        ▼
 (F) Rebuild + reseed locally, verify the rendered chapter in the browser
        ▼
 (G) Commit, deploy, verify on neuralascent.top, flip ContentStatus → "Published"
     only after a second read-through on the live page
```

## 2. Step (A) — gather source material

For each lesson, collect whatever real material exists:
- The user's Scaler curriculum PDFs/MD exports for that exact module/lesson title.
- A relevant textbook section (e.g. *Effective Java*, *Core Java*, official Spring docs,
  the JLS) — cite it in the `HorstmannRef`/reference field, the same way Tier-1 lessons do
  (`"Core Java Vol I Ch. 6 §6.1"`, `"Spring Framework Documentation: Dependency Injection"`).
- If genuinely no source exists for a topic, say so explicitly to the local LLM and let it
  rely on its own trained knowledge — but flag that lesson for extra scrutiny in review.

Keep a simple manifest as you go (a plain checklist file is enough) so a multi-session
effort doesn't lose track of which lessons have been upgraded:

```
[ ] patterns-01-solid          — source: scaler-lld-module5.pdf pp.12-18 — status: drafted
[ ] patterns-02-singleton      — source: scaler-lld-module5.pdf pp.19-24 — status: reviewed
[ ] patterns-03-builder        — source: none found, LLM knowledge only — status: needs extra review
```

## 3. Step (E) — the write-once seeding gotcha, and how to actually push an update

As documented in the knowledge map §8: for any lesson that already exists in the database
with non-empty `Draft` content (i.e. every Tier-2 lesson today), editing the `Chapter(...)`
call in `GetExpandedModules()` and redeploying **will not update the live row** — the
`EnsureExpandedModules()` guard only writes when the row is missing or still `Outline`.

Pick one of these, in order of preference:

**Option 1 (recommended) — add a proper enrichment backfill, mirroring the existing
`BackfillLessonContent`/`GetAuthoredLessonContent` pattern that already works for Modules
1–4.** Add a new method, e.g. `BackfillExpandedLessonContent(db, courseId)`, called
alongside `BackfillLessonContent(db, course.Id)` in `Seed()`, with its own
`GetEnrichedExpandedLessonContent(slug)` switch and a gate such as:

```csharp
private static bool NeedsExpandedEnrichment(Lesson lesson)
{
    // Draft content from the Chapter() helper is short and template-shaped.
    // Only overwrite if it still looks like the thin template, and never touch
    // content a human has since edited by hand or already marked Published.
    return lesson.ContentStatus == "Draft"
        && lesson.ContentBody.Length < 1200; // Tier-1 bodies run well past this
}
```

This is idempotent, safe to run every startup, never touches `Published` lessons or
lessons a human has since hand-edited past the length threshold, and reuses a pattern
that's already proven in this codebase. This is the one real code change this workflow
asks for — everything else is content authoring.

**Option 2 (fast, one-off, for a single lesson you're validating the loop with)** — update
the row directly with a migration or a one-time SQL statement against the local/dev
Postgres, then keep the seed source in sync for future fresh databases:

```sql
UPDATE lessons
SET content_body = '<new markdown>', updated_at = now()
WHERE slug = 'patterns-01-solid';
```

Still update `Chapter(...)` in source afterwards so a brand-new database seeds correctly
too — SQL-only changes rot the moment someone runs a fresh `docker compose down -v`.

**Option 3 (do not use)** — do **not** work around this by deleting and re-inserting the
lesson row. That silently discards `IsCompleted`, `OrderIndex`, and any linked
`Problem`/`Note`/progress rows tied to the lesson's `Id` via foreign keys.

## 4. Step (F) — local verification loop

```bash
# rebuild the API image so the updated seed source is compiled in
dotnet build api/StudyTracker.Api.csproj
dotnet test tests/StudyTracker.Api.Tests/StudyTracker.Api.Tests.csproj

# bring up (or restart) the local stack so Seed() runs again on startup
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml \
  up -d --build --force-recreate api

# confirm the row actually changed
docker compose exec db psql -U <user> -d <db> -c \
  "select slug, content_status, length(content_body) from lessons where slug = 'patterns-01-solid';"
```

Then open the chapter in a browser and read it as a learner would — this is the same
check the architecture docs insist on for the exercise engine ("implemented in source is
not the same as verified"; see `curriculum-modernization-tracker.md` §Phase 5).

## 5. Step (G) — publish

- Flip `ContentStatus` to `"Published"` only for the specific lesson(s) reviewed, not as a
  blanket operation across a whole module.
- Commit with a message naming the lessons touched (e.g. `content: author patterns-01..03
  (SOLID, Singleton, Builder) to Tier-1 depth`).
- Deploy through the existing pipeline (GitHub Actions → GHCR → EC2) — no changes needed to
  that pipeline for a content-only change.
- After deploy, re-read the live page once. The chat-handoff doc notes a real prior
  incident where a stale cached frontend bundle looked unchanged after deploy — a hard
  refresh resolved it; don't mistake that for the content failing to update.

## 6. Batching once the loop is proven

Once one lesson has gone all the way through (A)→(G) successfully:
- Batch by **module**, not by whole pathway — a module is a coherent unit of ~5–15 lessons
  sharing a topic, source material, and reviewer attention span.
- Use the batch prompt in `02-local-llm-prompts.md` §4 to generate several lessons' bodies
  in one local-LLM session while still reviewing each individually before insertion.
- Re-run the manifest checklist from §2 after each module to track real progress instead
  of trusting `git diff` size as a proxy for "done."

## 7. When a coding exercise or MCQ is actually warranted

Not every lesson needs one — the original blueprint is explicit that "curriculum drives
interaction," not a feature checklist (blueprint doc 1 §33). Add one only when:
- **MCQ**: the concept has a genuine common misconception or a design decision with 3–4
  plausible-looking wrong answers (like the Lesson 4 payment-authorizer question). Skip it
  for purely descriptive lessons (e.g. "EBS and RDS" overview content).
- **Coding exercise**: the lesson teaches a mechanic small enough to verify with a handful
  of JUnit tests in a few files (OOP mechanics, a small pattern, a collections/streams
  exercise). Skip it for lessons about infrastructure, architecture discussion, or
  capstone-scale builds that don't fit the single-Run/single-container execution model.

Use `02-local-llm-prompts.md` §3 for MCQ authoring and §5 for exercise-package authoring;
follow the exact trust-boundary structure in
[`../website-assignments-reference/2.neuralascent_java_exercises_architecture_handoff.md`](../website-assignments-reference/2.neuralascent_java_exercises_architecture_handoff.md) §12–13
when creating a new exercise package.
