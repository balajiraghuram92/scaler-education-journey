# C3 — Round 3: finish the `api-python/` corrections

Round 2 status after the reviewer's re-run (logs in `info/muse-prompts/corrections/round3/`):

- .NET: build clean, 181 passed, 0 failed. Done for now.
- `localization-ai/`: ruff and mypy clean, 58 passed, 30 skipped. Done for now.
- `issue-intel/`: ruff clean, 56 passed, 6 skipped, 3 mypy notes in `app/mcp_server/server.py`. Done for now.
- `api-python/`: the round 2 agent died. Only `requirements.txt` and `requirements-dev.txt` changed. Everything else in round 2 is still open: 74 failed, 99 passed, 20 mypy errors, 142 ruff findings, seed converter still crashes.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `api-python/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the six tasks below **in order**. After finishing each task, immediately append what you did to `api-python/PROGRESS.md` under a heading "Round 3 corrections" before starting the next task, so that nothing is lost if the session stops.

Logs: `info/muse-prompts/corrections/round3/api-python.log` and `seed-extract.log`.

## Task 1 — the mapper error (blocks most tests)

File: `app/models/study_vertical.py`, line 27.

Now:
```
canonical_vertical_id: Mapped[int | None] = mapped_column(Integer)
```
The column has no foreign key, so SQLAlchemy cannot configure `canonical_vertical` / `aliases` and every model fails with it. The C# is in `api/Data/StudyTrackerContext.cs` lines 104-107: `HasOne(CanonicalVertical).WithMany(Aliases).HasForeignKey(CanonicalVerticalId).OnDelete(DeleteBehavior.Restrict)`.

Change: add a `ForeignKey` to `Verticals.Id` with `ondelete="RESTRICT"` on that column. Keep the column name, the index and `remote_side` as they are.

The reviewer searched every file in `app/models/`: this is the only `*_id` column that feeds a relationship without a `ForeignKey`. Still check one thing in the 36 model files that have `relationship(...)`: every `back_populates="x"` names an attribute `x` that exists on the target class and whose own `back_populates` points back. List any pair you had to correct.

## Task 2 — tests that need PostgreSQL must skip cleanly

`tests/conftest.py` line 19 and `tests/test_schema_parity.py` line 22 connect to `localhost:5432/studytracker_py`. With no database this gives `OSError: Multiple exceptions: [Errno 111] Connect call failed` inside the test, which reads as a failure.

Change: in `tests/conftest.py`, try one connection once per session; if it fails, every test that uses the database fixture is skipped with the reason `no PostgreSQL at <url>`. `test_schema_parity.py` uses the same check. The URL comes from one environment variable (keep the existing name if there is one; otherwise `API_PYTHON_TEST_DATABASE_URL`) with the current URL as the default. Do not change any test body.

## Task 3 — `tests/test_db_connstr.py::test_sql_server_aliases`

The test expects `"Server=127.0.0.1;Database=StudyTracker;User Id=sa;Password=p@ss word"` to become `postgresql+asyncpg://sa:p%40ss%20word@127.0.0.1:5432/StudyTracker`. It fails on the assertion. Read `dotnet_connstr_to_asyncpg_url` and check, in this order: are `Server` and `User Id` accepted as aliases of `Host` and `Username` (keys compared case-insensitively, with the space in `User Id`)? Is the default port 5432 added? Are user and password percent-encoded with space as `%20`, not `+`? Fix the function; do not change the test.

## Task 4 — the seed converter

File: `tools/extract_seed_data.py`. It crashes: `AssertionError: expected string at 11146`.

Cause, lines 176-184 and 203-212: `parse_initializer` computes `part_offset`, the position in the file of the whole part `Name = value`. `parse_value` passes that same `part_offset` to `_decode_string_in_span` together with `stripped`, which is only the *value*. `_decode_string_in_span` finds the quote's index inside the value and adds it to the offset of the part, so it points into the property name.

Change: make `_decode_string_in_span` receive the whole part text (the text that actually starts at `part_offset`), and search for the opening `"` or `@"` after the first `=`. Nothing else about the function changes.

Then read `api/Data/JavaVerticalSeedData.cs` and `api/Data/FdeCurriculumSeedData.cs` and write down, in `PROGRESS.md`, each distinct shape of initializer value that appears (for example: regular string, verbatim string, string concatenation, int, bool, `null`, enum member, bare identifier such as `verticalId`, nested `new`, method call). For each shape, name the branch of `parse_value` that handles it. Add a branch for any shape with none.

## Task 5 — mypy, 20 errors

All 20 are listed under `##### mypy app` in the log. Fix each at the cause; no `# type: ignore` except the two noted.

| Location | What is wrong | What to do |
|---|---|---|
| `services/localization/workflow_service.py:474, 479` | a QPS result is assigned to a variable already typed as the optimize result | use a separate variable; compare with `api/Services/Localization/WorkflowService.cs` |
| `services/localization/workflow_service.py:312` | lookup result may be `None` | port what the C# does when the row is missing |
| `services/auth/session_service.py:156, 202` | `AppUser | None` passed where `AppUser` is required | port the C# missing-user branch |
| `services/learner_progress_service.py:358, 365` | attribute access on `UserLessonProgress | None` | port the C# null handling |
| `seed/fde_curriculum_seed_data.py:189` | `.append` on a `Sequence` | annotate as `list` |
| `seed/fde_curriculum_seed_data.py:244, 245` | `int | None` + `int` | port the C# default |
| `seed/mcq_migration_seed_data.py:116` | `Lesson | None` assigned to `Lesson` | handle the missing lesson as the C# does |
| `services/budget_guard_service.py:47`, `routers/admin_endpoints.py:237` | `Decimal(None)` possible | port the C# `?? 0` |
| `services/llama_api_client.py:165` | returns optional ints where ints are declared | default to 0 as the C# does |
| `seed/schema_check.py:164, 165, 167` | sorting names that may be `None` | filter out `None` first |
| `main.py:143` | exception handler typed for a subclass | annotate the parameter as `Exception` and narrow inside |
| `schemas/base.py:38` | `ser_json_by_alias` is not a `ConfigDict` key | remove it and use the real pydantic 2.13 setting for serialising by alias (`serialize_by_alias=True`) |
| `services/exercises/exercise_manifest_models.py:165` | `ctypes.windll` does not exist off Windows | guard with `sys.platform == "win32"`; a `# type: ignore[attr-defined]` is acceptable here |

## Task 6 — ruff, 142 findings

Every one is listed with file and line under `##### ruff check` in the log. Fix by hand; do not reformat files.

- `UP017` (99): `datetime.timezone.utc` → `datetime.UTC`, and fix the import.
- `I001` (13): import order.
- `F401` (10) and `F841` (1): remove the unused import or variable.
- `E741` (14): rename the variable `l` to a real name (`lesson`, `link`, `line`, as fits).
- `UP042` (3): `class X(str, Enum)` → `class X(StrEnum)`.
- `UP035` (1): `app/models/types.py:5`, import `Callable` from `collections.abc`.
- `ASYNC240` (1): `app/services/exercises/exercise_workspace_builder.py:107`, route through the same `asyncio.to_thread` helper the rest of the file uses.

## Finish

End with a short report: for each of the six tasks, done or not done, and files changed. Never say a test or check passes; you have not run it.
