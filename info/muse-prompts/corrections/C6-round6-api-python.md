# C6 — Round 6: `api-python/`, the last failing test and one reverted instruction

Round 5 worked. Reviewer's run after it:

- No database: ruff clean, mypy clean (173 files), 112 passed, 1 failed, 64 skipped.
- Real PostgreSQL, schema from the .NET `--migrate`: **175 passed, 1 failed, 1 skipped**. Schema parity, the AES test and both reconciliation tests now pass.

Logs in `info/muse-prompts/corrections/round6/` (`api-python.log`, `api-python-db.log`).

Two tasks. Task 2 undoes an instruction the reviewer got wrong in round 5.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `api-python/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `api-python/PROGRESS.md` under "Round 6 corrections" before starting the next.

## Task 1 — the endpoint-mapping test still cannot see included routers

File: `tests/exercises/test_exercise_endpoint_mapping.py`, the `_flatten_routes` helper added in round 5.

Still failing: `('/api/exercises/{exercise_id}', 'get_metadata')` is not in the set. The helper descends into entries that have a `routes` attribute. In `fastapi==0.141.1` the entries that `include_router` adds to `app.routes` have **no** `routes` attribute. The reviewer printed one in a container:

```
type:  _IncludedRouter
attrs: original_router   -> the fastapi.routing.APIRouter that was included (it has .routes)
       include_context   -> _RouterIncludeContext(prefix='', tags=[], ...)
```

So the child routes are at `entry.original_router.routes`, and the prefix given to `include_router(...)` is `entry.include_context.prefix`. The `APIRouter`'s own prefix is already part of each child route's `path`.

Replace the body of `_flatten_routes` with this logic (the reviewer ran exactly this against `create_app()` in a container; it yields 106 routes, including the six exercise routes with the names and methods the test asserts):

```
for each route in routes:
    orig = getattr(route, "original_router", None)
    if orig is not None:
        descend into orig.routes with prefix + route.include_context.prefix
    elif getattr(route, "routes", None):
        descend into route.routes with prefix + getattr(route, "path", "")
    else:
        yield (prefix + getattr(route, "path", ""), route)
```

Update the helper's docstring to describe the `_IncludedRouter` shape instead of "mount-like entries". Do not change any assertion in the test. Do not change `app/main.py` or any router.

## Task 2 — revert the case-insensitive reviewed-title lookup (reviewer's error in round 5)

Round 5 Task 4 told you to make the Java reconciler's reviewed-title lookup case-insensitive. That instruction was wrong, and your note in `PROGRESS.md` was right: the C# dictionaries are built with `StringComparer.Ordinal` (`api/Services/Reconciliation/JavaReconciler.cs:21` and `:42`) and looked up with `TryGetValue(task.Title, ...)` (`:138`, `:165`). The C# test `JavaReconciler_ReviewedLegacyTitle_MapsToCanonicalLessonSlug` (`tests/StudyTracker.Api.Tests/BackfillReconciliationTests.cs:389`) uses an exact-case title. This port is a reading reference for the C#, so it must behave the same. The Python test was the wrong side.

1. `app/services/reconciliation/java_reconciler.py`: remove `_LEGACY_LESSON_SLUG_MAP_LOWER`, `_LEGACY_PROBLEM_SLUG_MAP_LOWER`, their comment, and `title_key`. Restore the exact-case lookups as they were before round 5:
   - `if task.title in LEGACY_PROBLEM_SLUG_MAP:` … `p.slug == LEGACY_PROBLEM_SLUG_MAP[task.title]`
   - `if task.title in LEGACY_LESSON_SLUG_MAP:` … `les.slug == LEGACY_LESSON_SLUG_MAP[task.title]`
   Nothing else in the file changes.

2. `tests/test_java_reconciliation.py`, the test `test_java_reconciler_reviewed_legacy_title_matches_case_insensitively` (starts near line 48):
   - Rename it to `test_java_reconciler_reviewed_legacy_title_maps_to_canonical_lesson_slug`.
   - Change the task title, in both places it appears (the `StudyTask(...)` near line 54 and the `legacy_title` assertion near line 71), to the exact map key: `"Spring Boot 3 Core: Inversion of Control & Dependency Injection"`.
   - Add one assertion after the existing ones, matching the C# test's second assert: the single mapping's target lesson id equals the id of the lesson the test created. Keep a reference to that `Lesson` object when adding it so its `id` can be read after the flush. Use the field name the Python mapping model actually has for C# `TargetLessonId`; read it from the model, do not guess.
   - Change nothing else in the file.

3. In `PROGRESS.md`, under round 6, state that the round 5 Task 4 divergence is withdrawn and the lookup is ordinal again, as in C#.

## Finish

End with a short report: each task done or not done, files changed, and anything that could not be done as written. Never say a test or check passes; you have not run it.
