# Prompt for Local LLM — Remove redundant "Expanded Modules" definitions

## Context

`api/Data/JavaVerticalSeedData.cs` seeds the Java LLD course. Its `GetExpandedModules()`
method defines a second, older, auto-templated set of modules that runs on every seed via
`EnsureExpandedModules(db, course.Id)` (called at the end of `Seed(...)`). Three of its
module definitions are now fully redundant with the curated Modules 4–6 authored later in
this same file, and one of them actively pollutes Module 4 because it shares the exact same
slug.

The redundant definitions to remove, all inside the `List<ExpandedModuleSeed>` returned by
`GetExpandedModules()`:

1. `"design-principles-patterns"` (Badge `"Module 10"`) — its slug is identical to the real
   Module 4 (`design-principles-patterns`, Badge `"Module 4"`, created in `Seed(...)` and
   populated by `SeedModule4Lessons`). Because `EnsureExpandedModules` looks up modules by
   slug before creating one, this definition's 10 lessons (`patterns-01-solid` through
   `patterns-10-contest`) get merged directly into the real Module 4 instead of creating a
   separate module.
2. `"applied-design-machine-coding"` (Badge `"Module 11"`) — duplicates Module 5
   (`applied-machine-coding`, TicTacToe/Parking Lot/BookMyShow/Splitwise/Hotel Management)
   with generic filler content instead of the authored machine-coding lessons.
3. `"ai-first-backend-capstone-primer"` (Badge `"Module 12"`) — duplicates Module 6
   (`spring-enterprise-architecture`) coverage of Spring Boot, Spring Data JPA, and REST API
   design with generic filler content instead of the authored lessons.

## Task

Open `api/Data/JavaVerticalSeedData.cs` and locate the `GetExpandedModules()` method (it
returns `new List<ExpandedModuleSeed> { ... }` containing `new(...)` entries, each starting
with a slug string literal as the first constructor argument).

Remove exactly these three `new(...)` entries from that list, matched by their first
argument (the slug):

- `new("design-principles-patterns", "Design Principles & Patterns for Extensible Systems", ..., "Module 10", 5, new[] { Chapter("patterns-01-solid", ...), ... Chapter("patterns-10-contest", ...) })`
- `new("applied-design-machine-coding", "Applied Design & Machine Coding", ..., "Module 11", 6, new[] { Chapter("machine-01-approach", ...), ... Chapter("machine-14-final", ...) })`
- `new("ai-first-backend-capstone-primer", "AI-First Backend Capstone Project - Primer", ..., "Module 12", 7, new[] { Chapter("primer-01-backend-ai-development", ...), ... })`

Each entry runs from its `new(` line down through its closing `}),` — remove the entire
entry including every `Chapter(...)` call inside it. Do not touch any other entry in the
list (e.g. `"databases-sql"` at the top, and any entries that come after the three removed
ones, such as further primer/capstone modules if present — confirm by reading the full list
before editing).

## Constraints

- **Do not** touch `StandaloneExpandedCourseOrders`, `SeedModule1Lessons` through
  `SeedModule6Lessons`, `GetAuthoredLessonContent`, `BackfillLessonContent`,
  `EnsureExpandedModules`, `EnsureStandaloneExpandedCourse(s)`, or the `Chapter(...)` helper
  method itself.
- **Do not** touch the remaining `"databases-sql"` entry (and any other entries not listed
  above) in `GetExpandedModules()` — it is re-homed to its own standalone course via
  `StandaloneExpandedCourseOrders` and is intentionally kept.
- **Do not** add, rename, or renumber anything — this is a pure removal.
- Preserve exact existing indentation, brace style, and trailing-comma conventions used
  elsewhere in the same list (match the surrounding `new(...)` entries' style exactly).
- After removal, the file must still compile: verify brace and parenthesis balance stays
  correct (removing a `new(...) { ... }),` block means removing one matching open/close
  pair plus its trailing comma — do not leave a dangling comma before the next entry or a
  missing comma before the removed entry's former position if it was not last in the list).
- Do not change any other file.

## Output expectations

Return the full updated `api/Data/JavaVerticalSeedData.cs` file (or a unified diff against
the current file, whichever your tooling produces) with only the three entries removed.
