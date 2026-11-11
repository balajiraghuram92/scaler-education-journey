# C5 — Round 5: the last five `api-python/` failures

Round 4 worked. Against a real database built by the .NET migrations: **171 passed, 5 failed, 1 skipped** (was 145 / 30). `ruff check` is clean and `mypy app` reports no issues in 173 files. The reviewer re-ran the seed converter; it now writes to `app/seed/data/`.

Logs: `info/muse-prompts/corrections/round5/api-python-db.log` (with database) and `api-python.log` (without).

Paste everything below this line into Muse Code at the repository root.

---

Work only in `api-python/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Five tasks, one per failing test. After each, append what you did to `api-python/PROGRESS.md` under "Round 5 corrections". Each task below states what the reviewer observed by running code; where it contradicts a round 4 conclusion, the observation stands.

## Task 1 — `tests/test_schema_parity.py::test_schema_parity` (7 differences left, down from about 150)

**a. Three stale exceptions.** The log says `column comet_kiwi_score / raw_mt_qps_score / raw_mt_text in database but missing from metadata` for `localization_translations`. The model has all three columns (`app/models/localization/localization_translation.py` lines 55-57). They are reported because `app/seed/schema_check.py` lines 32-34 list them as known exceptions, written when no migration created them. The reviewer has since added the migration `api/Migrations/20261111140209_AddLocalizationAiLayer.cs`, and the database now has them.
Change: remove those three entries from the exception list in `schema_check.py`. Remove the paragraph in the docstring of `localization_translation.py` (lines 3-6) that says the migration does not create them, and the matching finding in `PORT-MAP.md`. Read the new migration and check that every table and column it creates (five new tables, seven new columns) is in the models with the same names, types, nullability and defaults; it was generated after the models were written.

**b. Four indexes that do not exist.** The models declare these, and the database does not have them:

- `knowledge_thread_steps`: `IX_knowledge_thread_steps_lesson_id`
- `learning_activity`: `IX_learning_activity_ProblemId`, `IX_learning_activity_ReadingMapItemId`, `IX_learning_activity_TaskId`

The real indexes, read from the migrated database with `pg_indexes`:

| Table | Indexes that exist |
|---|---|
| `knowledge_thread_steps` | `PK_knowledge_thread_steps`, `ix_knowledge_thread_steps_concept` |
| `learning_activity` | `PK_learning_activity`, `ix_learning_activity_lesson`, `ix_learning_activity_occurred_at`, `ix_learning_activity_user`, `ux_learning_activity_correlation_event` |

Change: delete the four index declarations from the two models. Do not add anything in their place unless the table above lists an index the model lacks.

## Task 2 — `tests/test_interchange.py::test_aesgcm_primitive_matches_nist_vector`

The code is right and the constant in the test is wrong. For AES-128-GCM with an all-zero key, nonce and 16-byte plaintext, the library returns

`0388dace60b6a392f328c2b971b2fe78` + `ab6e47d42cec13bdf53a67b21257bddf`

and that tag is the published value for NIST test case 2. The test's tag, `ab6e47c2b514f2c2458c5f558a5a9551`, is not. This is not a fault in the container's library.
Change: replace the second string in the assertion with `ab6e47d42cec13bdf53a67b21257bddf`. Nothing else.

## Task 3 — `tests/exercises/test_exercise_endpoint_mapping.py`

The router is included (`app/main.py` line 205) and the six handlers exist with the expected names (`app/routers/exercise_endpoints.py`). The test fails because, with the installed `fastapi==0.141.1`, iterating `app.routes` yields only the top-level entries (`/`, `/docs`, `/health`, ...); routes added through `include_router` are not in that flat list.
Change, in the test only: collect routes with a small recursive helper that walks `app.routes` and, for any entry that itself has a `routes` attribute, descends into it, joining the parent's prefix (`path` or `prefix`) with the child's `path`. Build the `routes` set and the `methods` dictionary from that flattened list. Keep every assertion as it is.
Then search `app/` and `tools/` for any other code that iterates `app.routes` or `router.routes` (for example `tools/parity.py`, or anything that lists the 102 routes) and make it use the same helper, moved to one shared place. List each place you changed.

## Task 4 — `tests/test_java_reconciliation.py::test_java_reconciler_reviewed_legacy_title_matches_case_insensitively`

`assert report.verified_count == 1` gets 0. The audit log shows the vertical was found with 1 legacy task, so discovery works and the title match fails. The task title is `spring Boot 3 Core: inversion of control & dependency injection` (lower-case first letter) and the lesson slug is `14-spring-boot-core`.
Read `JavaReconciler` in `api/Services/Reconciliation/` and its C# test `JavaReconciler_ReviewedLegacyTitle_MapsToCanonicalLessonSlug` in `tests/StudyTracker.Api.Tests/BackfillReconciliationTests.cs`. Find how the C# looks up the reviewed-title table (which `StringComparer` the dictionary uses, any trimming or normalising of the title) and make `app/services/reconciliation/java_reconciler.py` do the same. A plain `dict` lookup in Python is case-sensitive; that is the likely difference. Fix the service, not the test.

## Task 5 — `tests/test_backfill_reconciliation.py::test_phase3a_repeat_apply_repairs_missing_links`

`assert first.verified_count == 22` gets 17. Round 4 called this expectation unachievable. Before changing the test, settle it from the C#: find the C# test for the same scenario in `BackfillReconciliationTests.cs` and read the number it asserts. That test passes in .NET.

- If the C# asserts 22 (or `tasks.Count`), the Python reconciler verifies five tasks fewer than the C# does with the same seed. Task 4's fix may account for some or all of them (titles that differ only in case). Fix the service.
- If the C# asserts 17, or asserts something that is not a fixed count, correct the Python test to assert the same thing the C# does.

Say which case it was and quote the C# assertion in `PROGRESS.md`.

## Finish

End with a short report: each task done or not done, files changed, and for tasks 4 and 5 which side was wrong. Never say a test or check passes; you have not run it.
