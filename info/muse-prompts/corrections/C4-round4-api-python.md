# C4 — Round 4: `api-python/` against a real database

Round 3 worked. For the first time the reviewer ran the port against a real PostgreSQL whose schema was created by the .NET API's own `--migrate` (including the new LA1 migration, which the reviewer generated).

Logs in `info/muse-prompts/corrections/round4/`:

- `api-python.log` — no database: ruff (7 left), mypy (6 left), pytest
- `api-python-db.log` — with the database: **145 passed, 30 failed, 1 skipped**
- `ruff-diff.log` — the diff you asked for

Also done by the reviewer: the seed converter runs (`check OK`) and its two JSON files are now in `app/seed/data/`.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `api-python/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `api-python/PROGRESS.md` under "Round 4 corrections" before starting the next.

Main log: `info/muse-prompts/corrections/round4/api-python-db.log`. Each failure has a short traceback there; read the traceback for a test before touching anything for it.

## Task 1 — C# property defaults were not ported to the models (16 failures)

Two examples from the log:

- `null value in column "password_iterations" of relation "app_users" violates not-null constraint` (10 tests). C#: `public int PasswordIterations { get; set; } = 210_000;` (`api/Models/AppUser.cs:29`). Python: `mapped_column(Integer)` with no default (`app/models/app_user.py:39`).
- `null value in column "horstmann_ref" of relation "lessons" violates not-null constraint` (6 tests). C#: `public string HorstmannRef { get; set; } = string.Empty;` (`api/Models/Lesson.cs:47`). Python: `mapped_column(Text)` (`app/models/lesson.py:54`).

In C#, a new entity gets these values in memory, so EF inserts them. The Python models give `None`. This is one rule broken across the whole `app/models/` folder, not two columns.

Change: go through **every** file in `api/Models/` (including `api/Models/Localization/`). For every property with an initializer (`= string.Empty`, `= 0`, `= 210_000`, `= false`, `= DateTime.UtcNow`, `= new List<...>()`, an enum member, and so on), the matching `mapped_column(...)` in the Python model gets a Python-side `default=` with the same value (a callable for times and collections). Use `default=`, not `server_default=`: the schema is owned by EF and must not change. Do not touch columns whose C# property has no initializer.

In `PROGRESS.md`, list each model and the number of defaults added.

## Task 2 — schema parity (1 failure)

`tests/test_schema_parity.py::test_schema_parity` reports one difference:
`table Tasks column Id: server-default presence differs (metadata=None database=Identity(start=1, increment=1, ...))`.

Every other identity primary key passes, so compare how `Id` is declared in `app/models/study_task.py` with a model that passes (for example `app/models/study_vertical.py`) and with how `app/seed/schema_check.py` treats identity columns. Fix whichever side is inconsistent. Say which.

## Task 3 — localization service behaviour (7 failures)

- 4 tests in `tests/test_marketplace_service.py` and `tests/test_vendor_portal_service.py` fail with `InvalidJobStateException: All strings must have non-empty translations before submitting the job for review.` raised during test set-up. The same tests pass in .NET (`tests/StudyTracker.Api.Tests/Localization/`). Compare the Python fixture `tests/localization_fixture.py` with `LocalizationTestFixture.cs` first (does it create the same translations?), then `submit_job_for_review` in `app/services/localization/vendor_portal_service.py` with `VendorPortalService.cs` (which strings does the C# count: all strings, or only those in the job's locale?). Fix the side that differs from the C#.
- `tests/test_localization_workflow_service.py::test_run_step_phase3_actions_still_surface_not_implemented` fails. The .NET side changed in round 2: `WorkflowService.RunStepAsync` now calls a shared `ThrowIfAiNotConfigured` check at the start of each of the three AI branches, before any loop (`api/Services/Localization/WorkflowService.cs`, the method near line 614 and its three call sites). Port that change to `app/services/localization/workflow_service.py`, and port the new .NET test `Phase3Actions_EmptyBaseUrl_ThrowNotImplementedAndWriteNoLedger` to `tests/test_localization_ai_workflow.py`.
- 2 tests fail with `assert False is True`; find them in the log and compare the asserted field against the C# service.

## Task 4 — seeding and reconciliation counts (2 failures, plus the 5 in the same file)

`tests/test_backfill_reconciliation.py`: `assert 22 == 28` and `assert 17 == 27`, and three more failures in the same file. These ran for the first time now that `app/seed/data/*.json` exists. The converter printed: `java: 22 tasks, 27 module lessons, 15 study-guide topics, 3 expanded modules (58 lessons), 29 authored bodies`.

For each failing assertion, find the number the C# test expects (`tests/StudyTracker.Api.Tests/`, the test of the same name) and how `JavaVerticalSeedData.cs` reaches it. Then decide which is wrong: the converter (it extracts 22 tasks where the C# builds 28, for example because some tasks are added outside the `new List<StudyTask> { ... }` block), the Python seeder, or the Python test. Fix that one and say which. If the converter changes, say so clearly: the reviewer must re-run it.

Also fix the converter's output path: `tools/extract_seed_data.py` `main()` writes to `tools/../seed/data`, which is `api-python/seed/data`. The seeders read `app/seed/data`. Make the converter write to `app/seed/data`.

## Task 5 — four tests that fail without a database

1. `tests/test_interchange.py::test_aesgcm_primitive_matches_nist_vector`. The first 16 bytes of ciphertext match and the 16-byte tag does not, so the code is very likely right and the expected constant in the test is wrong. Hex constants written from memory cannot be trusted. Replace the hard-coded expected tag: keep the assertion on the ciphertext bytes, and assert that decrypting the output with the same key, nonce and associated data returns the plaintext and that a flipped tag bit is rejected. Rename the test so it no longer claims to be a NIST vector.
2. `tests/test_llama_api_client.py::test_success_parses_reply_usage_and_cost`: `assert None == 'Bearer test-key'`. The request the client sent has no `Authorization` header, or the test reads it from the wrong place. Compare with `api/Services/LlamaApiClient.cs`.
3. `tests/exercises/test_exercise_endpoint_mapping.py::test_endpoint_mapping_registers_run_and_check_routes`: `('/api/exercises/{exercise_id}', 'get_metadata')` is not among the registered routes. Check whether the exercises router is included in `app/main.py`, and whether the path parameter name and endpoint function name match what the test expects. The routes in `api/Endpoints/` are the authority.
4. `tests/exercises/test_python_exercises.py::test_python_compiler_output_keeps_learner_error_lines_and_drops_framework_frames`: expects `File "config/countFreq.py", line 1` in the cleaned output and gets the raw pytest `ERRORS` banner. Compare the output-cleaning function with its C# original.

## Task 6 — the remaining failures

After tasks 1 to 5, go through the `FAILED` list at the end of the log. For every test not covered above (`test_budget_guard.py`, `test_curriculum_import.py`, `test_bridge_schema_constraints.py`, `test_session_*`, `test_java_reconciliation.py`, `test_python_exercises.py::test_progress_service_...`), read its traceback. Most are the Task 1 not-null errors and need nothing more; write one line per test saying which task covers it, or fix it if it has its own cause.

## Task 7 — mypy (6) and ruff (7)

mypy, from `api-python.log`:

- `app/seed/mcq_migration_seed_data.py:116` and `app/services/localization/workflow_service.py:312`: `Name ... already defined`. The round 3 fix re-annotated an existing variable. Use a new variable name instead.
- `app/services/llama_api_client.py:166`: `int(None)` possible; default to 0 before converting.
- `app/seed/schema_check.py:164, 165, 167`: the names can be a `_NoneName` sentinel as well as `None`; keep only `str` values (`isinstance(name, str)`) before sorting.

ruff, 7 `I001`:

- `app/errors.py` and `app/main.py`: `ruff-diff.log` shows the fix is to delete one of the two blank lines after the import block (the project's ruff settings allow one).
- `app/services/curriculum_import_service.py`, `app/services/exercises/exercise_progress_service.py`, `app/services/learner_progress_service.py`, `app/services/mcq_service.py`, `app/services/progress_service.py`: the import block at the top is unsorted. Standard library first, then third party, then local relative imports, each group alphabetical, one blank line between groups, and one blank line after the block.

## Finish

End with a short report: for each task, done or not done, the files changed, and for tasks 2, 3 and 4 which side you judged wrong. Never say a test or check passes; you have not run it.
