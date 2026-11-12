# C17 — api-python: fixes after the track R review

The reviewer ran R6's code against a real PostgreSQL database migrated by the .NET API (R1-R3 migrations applied): **7 tests failed, 209 passed, 1 skipped**. `ruff check` found 2 errors and `mypy app` found 3. The .NET side is green (202 passed, 1 skipped), so the C# behaviour below is the reference.

The reviewer already deleted the 8 emptied Python files and fixed the C# compile breaks and stale C# tests R6 listed (`_options.Key`, `VendorJobRowAsync(job.Id, ct)`, fixture `Alias = "Test Team"`, `RawMtQpsScore = 2`, the HighCap test now asserts no ledger rows).

Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository. Edit files under `api-python/` only. Do not touch `api/`, `app/`, `localization-ai/`, `tests/StudyTracker.Api.Tests/`, compose files, `.env*`, deploy scripts or workflows. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `api-python/PROGRESS.md` under a new heading "C17 — track R review fixes".

Read first: `info/muse-prompts/localization-rebuild/CONTRACT.md`, `api/Data/LocalizationSeedData.cs`, and the files named in each task.

## Task 1 — lint (ruff I001)

`tests/test_usage_controls.py` line 3 and `tests/test_usage_metering.py` line 6: the import blocks are not sorted. Sort them the way the other test modules do (standard library, third party, then `app.` imports, each group alphabetical, one blank line between groups).

## Task 2 — mypy (3 errors)

1. `app/services/localization/usage_metering_service.py` around line 185: `UsageMissingRateDto(row.meter, kind)` passes positional arguments to a pydantic model. Use `UsageMissingRateDto(meter=row.meter, unit_kind=kind)`. Search the rest of `app/` for any other DTO built with positional arguments and fix those too. This is also the cause of two failing tests: `test_usage_cost_without_rate_is_zero_and_listed_missing` and `test_usage_summary_totals_for_one_month_and_project_are_exact` (`TypeError: BaseModel.__init__() takes 1 positional argument but 3 were given`).
2. `_completed_percent` in `app/services/localization/translation_job_service.py` (around line 537) and in `app/services/localization/vendor_portal_service.py` (around line 279): change the first parameter's type from `list[LocalizationString]` to `Sequence[LocalizationString]` (import `Sequence` from `collections.abc`). The callers pass `project.strings`, which mypy sees as a `Sequence`.

## Task 3 — new translations must join their string's collection

Failing test: `tests/test_usage_metering.py::test_workflow_without_metering_runs_every_action`, `assert '0 strings affected' == '4 strings affected'` on "Send to Review".

Cause: in `app/services/localization/workflow_service.py`, the machine-translation branch (around line 375) creates `new_trans = LocalizationTranslation(string_id=item.id, ...)` and calls `self._session.add(new_trans)`, but does not add it to `item.translations`. The next step in the same session loads the project with `selectinload(...)`; SQLAlchemy keeps the collection already in the identity map, so "Send to Review" never sees the new rows. EF Core fixes up the navigation by itself, which is why the C# test passes.

Fix: wherever the workflow (or any other service in `app/services/localization/`) creates a `LocalizationTranslation` for a string object it already holds, append it to that string's collection (`item.translations.append(new_trans)`) instead of, or as well as, `session.add`. Search every `LocalizationTranslation(` construction in `app/services/localization/` and apply the same rule. Do not add `populate_existing` to the loads.

## Task 4 — replacing an agreement's teams

Failing test: `tests/test_translation_job_service.py::test_save_agreement_tier_update_changes_member_counts`, `UniqueViolationError ... ux_localization_team_assignments_agreement_locale`.

Cause: in `save_agreement_async` (`app/services/localization/translation_job_service.py`, around line 420), the old `TeamAssignment` rows are deleted with `session.delete` and the new rows are added in the same flush. SQLAlchemy's unit of work emits the INSERTs before the DELETEs, so the new `(agreement_id, locale_code)` collides with the old one.

Fix: after the loop that deletes the stale rows, `await self._session.flush()` before adding the new assignments.

## Task 5 — stale test expectations

1. `tests/exercises/test_exercise_endpoint_mapping.py::test_endpoint_mapping_localization_rebuild_routes`: the routers declare `/api/localization/jobs/{job_id:int}/approve` and `/api/localization/jobs/{job_id:int}/send-back` (the `:int` convention used across this port, e.g. the admin routes). Change the test's expected paths to include `:int` for every route that declares it. Check each asserted path against the decorator in the router file; change the test, not the routers.
2. `tests/test_localization_ai_workflow.py::test_score_qps_does_not_rescore_raw_when_already_set`: the fixture inserts `raw_mt_qps_score=55`, which PostgreSQL now rejects (`ck_localization_translations_raw_mt_qps_score_range`, 1 to 5). Use `2`, and assert `2` at the end. The C# test made the same change.
3. `tests/test_usage_controls.py::test_high_cap_run_matches_uncapped_behaviour`: R3 removed the ledger writes. Replace the ledger assertions with an assertion that the ledger table has no rows, as the C# test now does.

## Task 6 — the localization seeder

`app/seed/localization_seed_data.py` still imports `marketplace_bid` and `marketplace_job`, which no longer exist, so the seed command fails on import. Port the current `api/Data/LocalizationSeedData.cs` in full:

- the project's `client_alias` ("Client Team Kestrel") and the vendors' `alias` values;
- the Gold service agreement and its five team assignments (member count from `ServiceTiers.members_for`);
- the de-DE, fr-FR and es-ES translation jobs on the `TranslationJob` model, with the statuses and timestamps the C# seed uses;
- the two usage-cap rows for the demo project (2,000,000 machine-translation characters, 5,000,000 llm tokens);
- the provider-health row named `"AzureTranslator"`;
- scores: the C# seed sets no `qps_score` or `raw_mt_qps_score` at all, so leave them unset;
- no bids; the single ledger row for the approved es-ES job stays (`Source = "Marketplace"`, `Amount = 195`, linked to that job), as in C#.

Port the two C# "ensure" steps as well, wired the way C# wires them: `EnsureUsageCaps` (public, called from `DbSeeder` right after `Seed`; find the Python seeder's equivalent call site) and `EnsureServiceAgreement` (private, called from inside the seed method; read the C# to see exactly where). An already-seeded database must end in the same state as in C#. Match the C# order of inserts and every literal value; the parity run compares JSON from both APIs.

## Finish

End with a short report: each task done or not done, every file changed, and anything that could not be done as written. Never say a test or lint passes; you have not run them.
