# STRICT PROMPT — Move MCQs from a static frontend file to a real, session-tracked DB schema

Read this entire document before touching any file. This is a real architecture migration
touching FIVE areas. Read all listed files fully before writing anything.

## Why this is happening

Today, every practice question on this site lives in `app/src/data/lessonInteractions.js` as a
plain JS object, consumed via `getLessonInteractions(courseSlug, moduleSlug, lessonSlug)` —a
synchronous, build-time lookup with zero server round-trip. This means:
- Every user sees byte-identical questions in byte-identical option order.
- There is no way to shuffle options per learner.
- There is no way to serve an AI-reworded variant of a question.
- There is no record anywhere of what was shown to a learner or what they answered.

There is currently **no MCQ table in Postgres at all** — confirmed by reading `api/Models/`;
the only adjacent table, `problems`, is an unrelated, near-empty admin table with no
options/correctness columns.

By contrast, lesson prose (`lessons.content_body`) is already correctly DB-backed and dynamic —
this migration brings MCQs up to the same standard, and lays the exact schema the future AI
Tutor (`ai-agent/`, hand-written separately, not part of this prompt) needs to write
AI-reworded question variants and read learner attempt history, since `ai-agent` already shares
this same Postgres database via its own connection pool.

This prompt does **not** touch exercises (`exercises/**`) or `conceptChecks` (the separate,
smaller array used only for lessons 1-4) — both are explicitly out of scope, left for later,
separately-scoped work.

## Required reading before writing anything

- `app/src/data/lessonInteractions.js` — the full current data shape (`practiceQuestions` arrays
  only; ignore `conceptChecks`), and the `getLessonInteractions` / default export at the bottom.
- `app/src/components/learning/PracticeQuestions.jsx` — how the frontend currently renders a
  question, checks the answer, and shows the explanation. This is the component that needs to
  switch from a static import to API calls.
- `api/Models/Lesson.cs`, `api/Models/AppUser.cs` — the exact FK shapes and column-naming
  convention (`snake_case` DB columns via `[Column("...")]`, matching C# `PascalCase` properties).
- `api/Endpoints/V2Endpoints.cs` — the existing `MapGroup("/api/v2")` pattern, and specifically
  how `/progress/lesson` etc. are wired to a service class. New endpoints must follow this exact
  shape (`group.MapGet(...)`/`group.MapPost(...)`, `.WithName(...)`, a request record type where
  needed).
- `api/Endpoints/ChatEndpoints.cs` (around the `ClaimTypes.NameIdentifier` usage) — the exact
  pattern this codebase uses to extract the current authenticated user's id from
  `HttpContext.User`. Use this identical pattern; do not invent a different auth mechanism.
- `api/Services/ProgressService.cs` — the existing service-class shape and transaction pattern
  (`_db.Database.BeginTransactionAsync()`) to mirror for the new service.
- `api/Migrations/` — open the most recent migration file to confirm the exact EF Core migration
  file-naming and structure convention already used in this project.

## Part 1 — Schema (new EF Core models + migration)

Add four new models under `api/Models/`, following this project's exact existing column/FK
conventions (see `Lesson.cs`/`AppUser.cs` for the pattern):

**`McqQuestion`** (table `mcq_questions`)
- `Id` (PK)
- `LessonId` (FK → `lessons.id`, required)
- `LegacyKey` (string, e.g. `'lesson-20-parking-mcq-01'` — traceability back to the static file
  being migrated away from; unique)
- `QuestionText` (text)
- `SourceType` (string, `'FROM_MATERIAL'` or `'LLM_GENERATED'` — copy the value already encoded
  as a `// SOURCE_TYPE: ...` comment above each question in the source file)
- `Explanation` (text)
- `IsActive` (bool, default true)
- `CreatedAt`, `UpdatedAt`

**`McqOption`** (table `mcq_options`)
- `Id` (PK)
- `QuestionId` (FK → `mcq_questions.id`, required)
- `OptionKey` (single char, `'a'`/`'b'`/`'c'`/`'d'` — this is the STABLE canonical identity of an
  option, independent of what order it's ever displayed in)
- `OptionText` (text)
- `IsCorrect` (bool)

**`McqPresentation`** (table `mcq_presentations`) — one row every time a question is actually
served to someone
- `Id` (PK)
- `QuestionId` (FK → `mcq_questions.id`, required)
- `UserId` (int, nullable FK → `app_users.id` — null for an unauthenticated/anonymous viewer, if
  this site allows viewing lessons without login; check `Lesson`/existing endpoints for whether
  anonymous access is possible and follow that precedent)
- `DisplayedOptionOrder` (jsonb array of option_key strings, e.g. `["c","a","d","b"]` — the exact
  shuffled order actually shown for this presentation)
- `QuestionTextShown` (text, nullable — null means the canonical `QuestionText` was shown
  verbatim; populated later by `ai-agent` when it serves an AI-reworded variant instead — this
  prompt only needs to add the column, not populate it)
- `PresentedAt` (timestamptz, default now)

**`McqAttempt`** (table `mcq_attempts`)
- `Id` (PK)
- `PresentationId` (FK → `mcq_presentations.id`, required, unique — one attempt per presentation)
- `SelectedOptionKey` (single char)
- `IsCorrect` (bool)
- `AnsweredAt` (timestamptz, default now)

Add a new EF Core migration for these four tables plus their indexes (at minimum: index
`mcq_questions.lesson_id`, index `mcq_presentations.user_id`, unique index
`mcq_questions.legacy_key`), following the exact naming/structure convention of the most recent
existing migration file you read above.

## Part 2 — One-time data migration script (Node.js, run once, not part of the app)

`lessonInteractions.js` is a plain JS module — the most reliable way to migrate its data without
hand-transcription errors is to actually `require()`/import it and walk the real object, not to
manually re-type ~24,000 lines.

Write a standalone script, `scripts/migrate-mcqs-to-db.mjs` (or `.js` — match this repo's module
convention), that:
1. Imports the default export from `app/src/data/lessonInteractions.js`.
2. Walks every top-level key (`"{courseSlug}/{moduleSlug}/{lessonSlug}"`), and for each entry's
   `practiceQuestions` array (skip `conceptChecks` entirely — out of scope per above), extracts:
   the lesson identification (needed to resolve `lesson_id` via a DB lookup at insert time), and
   for each question: its `id` (→ `legacy_key`), `question` (→ `question_text`), the
   `// SOURCE_TYPE: ...` comment immediately preceding it in the source (→ `source_type` — you'll
   need to re-read the raw file text alongside the parsed object to recover this comment, since
   comments aren't part of the JS object at runtime), `options` (→ 4 `mcq_options` rows),
   `correctOptionId` (→ which option's `is_correct = true`), and `explanation`.
3. Emits a single JSON file, `scripts/mcq-migration-data.json`, shaped as an array of
   `{ courseSlug, moduleSlug, lessonSlug, questions: [...] }` objects — this is the intermediate,
   inspectable artifact a human can sanity-check before it's loaded into Postgres.
4. Do **not** have this script talk to the database directly — keep it a pure, side-effect-free
   extraction step.

Then add a C# seeding method (in a new file `api/Data/McqMigrationSeedData.cs`, following the
exact style of `JavaVerticalSeedData.cs`'s `Seed(db)` method signature and idempotency pattern —
skip a question if a row with its `legacy_key` already exists) that reads
`scripts/mcq-migration-data.json` at seed time, resolves each `(courseSlug, moduleSlug,
lessonSlug)` to a real `lesson_id` via the existing `Lessons`/`CourseModules`/`Courses` tables,
and inserts the `McqQuestion`/`McqOption` rows. Wire this new seeder into `DbSeeder.Initialize`
alongside the existing seed calls (add it as a new numbered step, same pattern as the existing
`JavaVerticalSeedData.Seed(db)` call).

## Part 3 — API endpoints

Add a new endpoint group (either inside `V2Endpoints.cs` or a new `McqEndpoints.cs` following the
exact same `MapGroup`/service-injection pattern):

- **`GET /api/v2/practice-questions/{courseSlug}/{moduleSlug}/{lessonSlug}`** — looks up all
  `IsActive` `McqQuestion` rows for that lesson. For each one: shuffle its 4 options into a random
  display order server-side, insert a new `McqPresentation` row recording that exact order (and
  the current user id, via the same `ClaimTypes.NameIdentifier` pattern you read in
  `ChatEndpoints.cs` — null if unauthenticated), and return `{ presentationId, questionText,
  options: [{ optionKey, optionText }] }` in the shuffled order — **do not include
  `isCorrect` or `explanation` in this response**, only after an attempt is recorded.
- **`POST /api/v2/practice-questions/{presentationId}/attempts`** — body
  `{ selectedOptionKey }`. Looks up the `McqPresentation`, confirms it doesn't already have an
  attempt (idempotency — return the existing result if called twice), records a new
  `McqAttempt`, and returns `{ isCorrect, correctOptionKey, explanation }` by joining back to the
  question's real options/explanation.

Put the actual logic in a new `McqService` class under `api/Services/`, mirroring
`ProgressService`'s constructor-injection and transaction style — endpoints should stay thin,
same as every other endpoint in `V2Endpoints.cs`.

## Part 4 — Frontend

Update `app/src/components/learning/PracticeQuestions.jsx`:
- Replace the static `getLessonInteractions(...)` import/call with a `fetch` (or this project's
  existing API client helper, if one exists — check `app/src/` for an existing pattern like an
  `apiClient.js`/`useApi` hook before inventing a new fetch call style) to
  `GET /api/v2/practice-questions/{courseSlug}/{moduleSlug}/{lessonSlug}` on mount.
- Render options in the exact order the API returned them (do not re-sort or re-shuffle
  client-side).
- On answer selection, `POST` to `/api/v2/practice-questions/{presentationId}/attempts` with the
  selected `optionKey`, and use the response's `isCorrect`/`correctOptionKey`/`explanation` to
  render the existing correct/incorrect UI state — do not compute correctness client-side anymore.
- Keep the component's existing visual design/CSS entirely as-is; this is a data-source change,
  not a redesign.

## Constraints

- Do **not** delete `app/src/data/lessonInteractions.js` or remove its `practiceQuestions` data
  in this pass. Leave it in place, unused by the new component, until the migration is verified
  live against a real reseed. Removing the static file is an explicit, separate follow-up step
  once confirmed working.
- Do **not** touch `conceptChecks` anywhere, and do not touch anything under `exercises/`.
- Match this codebase's existing conventions exactly (column naming, endpoint shape, service
  style, migration file structure) — do not invent a different pattern than what's already
  established.
- The Node extraction script (Part 2) must be side-effect-free and produce an inspectable JSON
  artifact — do not have it write to the database directly.

## Output expectations

Produce: the 4 new EF Core model files, the new migration file, the Node extraction script, the
generated `mcq-migration-data.json` (or a representative sample plus a note on its full size), the
new `McqMigrationSeedData.cs`, the `DbSeeder.cs` wiring change, the new `McqService.cs`, the new
endpoint(s), and the updated `PracticeQuestions.jsx`. State clearly which files were created vs.
modified.

## Verification checklist (self-check before returning the result)

1. The migration applies cleanly (`dotnet ef database update` succeeds, or equivalent for this
   project's actual migration-run mechanism).
2. After seeding, `SELECT count(*) FROM mcq_questions` matches the total question count currently
   in `lessonInteractions.js`'s `practiceQuestions` arrays (report both numbers).
3. Every `mcq_questions.legacy_key` is unique and every one resolves to a real `lesson_id` — no
   orphaned rows from an unmatched `courseSlug/moduleSlug/lessonSlug`.
4. Calling the GET endpoint twice for the same lesson produces two different
   `DisplayedOptionOrder` values across enough calls to demonstrate real shuffling (not always the
   same order).
5. Calling the POST endpoint twice for the same `presentationId` does not create two `McqAttempt`
   rows.
6. `PracticeQuestions.jsx` no longer imports from `app/src/data/lessonInteractions.js`.
7. `app/src/data/lessonInteractions.js` itself is untouched (still present, still has all its
   original content) — this pass is additive, not destructive.
