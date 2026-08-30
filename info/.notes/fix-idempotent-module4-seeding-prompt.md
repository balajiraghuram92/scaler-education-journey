# Prompt for Local LLM — Fix idempotent Module 4 seeding + remove two more redundant modules

## Context

`api/Data/JavaVerticalSeedData.cs`'s `Seed(...)` method has an idempotent reconciliation
block for existing databases (databases where the `java-spring-lld` course already exists,
so the initial course-creation branch does not run). That block currently reads:

```csharp
// Ensure Module 4 (design-principles-patterns) exists
var designModule = db.Modules.FirstOrDefault(m => m.CourseId == existingCourse.Id && m.Slug == "design-principles-patterns");
if (designModule == null)
{
    designModule = new CourseModule
    {
        CourseId = existingCourse.Id,
        Slug = "design-principles-patterns",
        Title = "Design Principles & Patterns for Extensible Systems",
        Description = "SOLID principles, creational, structural, and behavioural design patterns, and UML class diagrams.",
        Badge = "Module 4",
        OrderIndex = 4
    };
    db.Modules.Add(designModule);
    db.SaveChanges();
    SeedModule4Lessons(db, designModule.Id);
}

// Ensure Module 5 (applied-machine-coding) exists
var machineModule = db.Modules.FirstOrDefault(m => m.CourseId == existingCourse.Id && m.Slug == "applied-machine-coding");
if (machineModule == null)
{
    machineModule = new CourseModule
    {
        CourseId = existingCourse.Id,
        Slug = "applied-machine-coding",
        Title = "Applied Design & Machine Coding",
        Description = "End-to-end object-oriented design and implementation of real-world systems: TicTacToe, Parking Lot, BookMyShow, and Splitwise.",
        Badge = "Module 5",
        OrderIndex = 5
    };
    db.Modules.Add(machineModule);
    db.SaveChanges();
    SeedModule5Lessons(db, machineModule.Id);
}
```

**The bug**: on a production database, a module with slug `design-principles-patterns`
already exists — but it was created long ago by the (now largely removed) `GetExpandedModules()`
path with `Badge = "Module 10"` and none of the real Lesson 14–17 content. Because the guard
is `if (designModule == null)`, and the module is *not* null, `SeedModule4Lessons` never
runs, the badge is never corrected, and the real lessons are never inserted. Confirmed by
direct query against a long-lived database: the module existed with `Badge = "Module 10"`
and 0 lessons.

A fresh/newly created database does not hit this bug, because the initial course-creation
branch calls `SeedModule4Lessons`/`SeedModule5Lessons` unconditionally. Only existing
databases (including production) are affected.

## Task 1 — Make the Module 4 and Module 5 idempotent checks self-healing

In `Seed(...)`, replace the two blocks above so that, regardless of whether the module
already existed under a different badge/without the real lessons, the code:

1. Creates the module if it is missing (unchanged behavior).
2. Corrects `Badge`, `Title`, `Description`, and `OrderIndex` on the module if they don't
   already match the canonical values (do this whether the module was just created or
   already existed).
3. Calls `SeedModule4Lessons(db, designModule.Id)` / `SeedModule5Lessons(db, machineModule.Id)`
   whenever the module does not yet contain its first canonical lesson — check with
   something like `!db.Lessons.Any(l => l.ModuleId == designModule.Id && l.Slug == "14-solid-principles")`
   for Module 4, and the equivalent first-lesson slug check for Module 5 (use whatever the
   first lesson slug actually is inside `SeedModule5Lessons` — read that method to confirm
   it, do not guess). This must run even when the module already existed, not only on first
   creation, so it does not matter that `SeedModule4Lessons`/`SeedModule5Lessons` add lessons
   with `db.Lessons.Add(...)` unconditionally — guard the *call site*, not those methods,
   against re-adding lessons that already exist. (Check whether those two methods already
   guard against duplicate lesson slugs internally by reading them first; if they do, the
   call-site existence check can be simplified accordingly — but do not remove the site-level
   check for the *module's* Badge/Title/Description correction, since that part is unrelated
   to lesson duplication.)

Keep the existing Spring-module reconciliation block (`springModule.OrderIndex != 6`) as-is;
it is correct and unaffected by this bug — do not modify it.

## Task 2 — Remove two more redundant `GetExpandedModules()` entries

In the same file's `GetExpandedModules()` method, remove these two additional entries
(same category as the three already removed in a prior change — auto-templated filler that
duplicates or is no longer wanted alongside the curated Modules 1–6):

1. `"ai-first-backend-capstone-advanced"` (Badge `"Module 13"`, title
   `"AI-First Backend Capstone Project - Advance"`) — duplicates Module 6's Spring/REST/JPA
   coverage with generic filler (RestTemplate/resilience, UUIDs, mocking, JWT, OAuth2, etc.)
2. `"production-ai-enabled-system"` (Badge `"Elective"`, title
   `"Build a Production-Ready AI-Enabled System"`) — confirmed unused, no frontend reference,
   safe to remove.

Remove each entire `new(...) { ... }),` entry the same way the prior three were removed:
matched by first constructor argument (the slug), removing everything from the `new(` line
through its closing `}),`, preserving surrounding style and comma placement.

## Constraints

- Do not touch `StandaloneExpandedCourseOrders`, `SeedModule1Lessons` through
  `SeedModule6Lessons`, `GetAuthoredLessonContent`, `BackfillLessonContent`,
  `EnsureExpandedModules`, `EnsureStandaloneExpandedCourse(s)`, or the `Chapter(...)` helper.
- Do not touch the remaining `"databases-sql"` entry in `GetExpandedModules()`.
- Do not change the Spring-module `OrderIndex != 6` reconciliation block.
- Do not add, rename, or renumber anything beyond what is specified above.
- Preserve exact existing indentation, brace style, and comma conventions.
- The file must remain balanced (braces/parens) and compile after the change.
- Do not change any other file.

## Output expectations

Return the full updated `api/Data/JavaVerticalSeedData.cs` file (or a unified diff against
the current file) reflecting both tasks.
