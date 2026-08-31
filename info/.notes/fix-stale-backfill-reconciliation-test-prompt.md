# Prompt: Fix stale module-slug assertions in BackfillReconciliationTests

Paste everything below into the Local LLM verbatim.

---

## Context

Commit `1542598` ("Self-heal Module 4/5 idempotent seeding; remove redundant
capstone-advanced and elective module") removed two modules —
`"ai-first-backend-capstone-advanced"` and `"production-ai-enabled-system"` — from
`GetExpandedModules()` in `api/Data/JavaVerticalSeedData.cs`, but the test file below
was never updated to match. It has been failing in CI on every run since that commit.

The test `JavaVerticalSeedData_AddsExpandedModulesAndIsIdempotent` in
`tests/StudyTracker.Api.Tests/BackfillReconciliationTests.cs` currently fails with:

```
Assert.True() Failure
Expected: True
Actual:   False
   at ...BackfillReconciliationTests.cs:line 159
```

Confirmed current reality (do not re-derive this, it's already verified): the
`java-spring-lld` course now only has these module slugs seeded directly (not via
`GetExpandedModules()`): `oop-foundations`, `concurrency-multithreading`,
`advanced-java-collections`, `design-principles-patterns`, `applied-machine-coding`,
`spring-enterprise-architecture`. `GetExpandedModules()` itself now only returns
`databases-sql`, `high-level-design`, `data-engineering` — all three of which are
filtered into the *standalone*-course path (`StandaloneExpandedCourseOrders`), so
**none** of them get attached to the `java-spring-lld` course anymore. The slugs
`"applied-design-machine-coding"`, `"ai-first-backend-capstone-primer"`,
`"ai-first-backend-capstone-advanced"`, and `"production-ai-enabled-system"` do not
exist anywhere in the current codebase.

## The fix

File: `tests/StudyTracker.Api.Tests/BackfillReconciliationTests.cs`

Find this block (around line 129, inside
`JavaVerticalSeedData_AddsExpandedModulesAndIsIdempotent`):

```csharp
        var expectedJavaModuleSlugs = new HashSet<string>(StringComparer.Ordinal)
        {
            "design-principles-patterns",
            "applied-design-machine-coding",
            "ai-first-backend-capstone-primer",
            "ai-first-backend-capstone-advanced",
            "production-ai-enabled-system"
        };
```

Replace it with (the two module slugs that are actually seeded onto the
`java-spring-lld` course today; do not add back any of the four removed/renamed
slugs):

```csharp
        var expectedJavaModuleSlugs = new HashSet<string>(StringComparer.Ordinal)
        {
            "design-principles-patterns",
            "applied-machine-coding"
        };
```

Do not change anything else in this file — the `expectedStandaloneModuleSlugs` set
(`databases-sql`, `high-level-design`, `data-engineering`), the rest of this test
method's assertions, and every other test in the file are all still correct and must
stay exactly as they are.

## Verification

After the edit, run:

```
dotnet test tests/StudyTracker.Api.Tests/StudyTracker.Api.Tests.csproj --configuration Release
```

Expect `JavaVerticalSeedData_AddsExpandedModulesAndIsIdempotent` to pass, and the full
suite to report `Failed: 0` (previously: `Failed: 1, Passed: 94, Skipped: 1, Total: 96`).
