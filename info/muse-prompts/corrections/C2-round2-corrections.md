# C2 — Round 2 corrections for the LA, P and G tracks

The reviewer re-ran every check after round 1. Raw output is in `info/muse-prompts/corrections/round2/`:

- `dotnet.log` — `dotnet build api` (clean) and `dotnet test` (1 failed, 179 passed)
- `localization-ai.log` — ruff clean, mypy clean, 58 passed, 30 skipped (need a database or a real model)
- `api-python.log` — ruff, mypy, then pytest (74 failed, 99 passed, 3 skipped), then `pip freeze`
- `issue-intel.log` — ruff, mypy, pytest (3 failed, 53 passed, 6 skipped), then `pip freeze`
- `seed-extract.log` — the seed converter's first real run: it crashes

Each Python log comes from a clean `python:3.12-slim` container with no database and no Docker inside it. The `pip freeze` sections list the versions that actually installed and worked.

Paste everything below this line into Muse Code at the repository root.

---

Use a workflow to fan out three parallel agents, one per folder. Work on the current branch; do not create or switch branches; do not commit. Do not run commands; a reviewer runs the checks after you finish.

Round 1 worked: all three projects now install and load their tests. This round fixes what the tests then showed. Read your log in full first. Fix causes, not symptoms. Do not add features and do not refactor.

## Agent 1 — the .NET side of LA4 (`api/Services/Localization/`, `tests/StudyTracker.Api.Tests/Localization/`)

`localization-ai/` itself is clean in this round; do not touch it.

1. **One failing test:** `WorkflowServiceTests.RunStep_Phase3Actions_StillSurfaceNotImplemented` ("No exception was thrown"). The test builds `MtOptimizeService`, `QpsScoringService` and `AutoRoutingService` with no AI client and expects `NotImplementedException` from `RunStepAsync` for "Run MT Optimize", "Score QPS" and "Auto-Route". The services do throw when they have no client, but `WorkflowService.RunStepAsync` only calls them inside the per-translation loop, and the test project has no translation that qualifies, so the loop body never runs and the step "succeeds" having done nothing.
   The test is right and the code is wrong: an unconfigured AI service must give 501 regardless of the data (LA4 item 5, "the not-configured 501 path"). Make each of the three action branches fail up front, before any loop and before any database write, when the AI service is not configured. Use one small shared check rather than three copies. Do not weaken or delete the test.
2. In `LocalizationAiWorkflowTests.cs`, add one test for the same thing through the configured-client path: a client whose options have an empty base URL, a project with no eligible translations, each of the three actions, expecting `NotImplementedException` and no ledger entry written.

## Agent 2 — `api-python/`

Log: `info/muse-prompts/corrections/round2/api-python.log` and `seed-extract.log`.

1. **`requirements.txt` cannot run the app.** `sqlalchemy.ext.asyncio` needs `greenlet`, which is not installed by plain `sqlalchemy`. Use `sqlalchemy[asyncio]`. (The reviewer added `greenlet` by hand to get the pytest section of the log.)
2. **Pin every unpinned package** in `requirements.txt` and `requirements-dev.txt` to the exact version in the log's `pip freeze` section. Remove the "reviewer will pin" comments.
3. **Most of the 74 failures have one cause.** SQLAlchemy cannot configure the mappers:
   `Could not determine join condition between parent/child tables on relationship StudyVertical.canonical_vertical - there are no foreign keys linking these tables.`
   In `app/models/study_vertical.py`, `canonical_vertical_id` is a plain `Integer` column with no `ForeignKey`. Check it against the C# model and `StudyTrackerContext.cs`: the column, its constraint name and its delete behaviour must match what EF created.
   Then do not stop at this one. One broken mapper hides every other broken mapper, and the reviewer will only see the next one on the next run. Go through **every** model in `app/models/` and, for every `relationship(...)`, confirm that: a `ForeignKey` exists on the right column; `back_populates` names an attribute that exists on the other class and points back; self-referencing relationships have `remote_side`; where two relationships link the same pair of tables, each has `foreign_keys`. List the models you corrected in `PROGRESS.md`.
4. **Three failures with other causes**; find each in the log:
   - `tests/test_budget_guard.py::test_empty_day_is_within_budget` and `tests/test_schema_parity.py::test_schema_parity` fail with `OSError: Multiple ex...` (a connection attempt). Any test that needs a real PostgreSQL must skip with a clear reason when none is reachable, the way the Docker-backed exercise test already does; a unit test that does not need PostgreSQL must not try to connect to one.
   - `tests/test_db_connstr.py::test_sql_server_aliases` fails on an assertion. Read the test, then the connection-string parser against the C# it ports, and fix whichever is wrong. Say which.
5. **The seed converter crashes on its first run.** `seed-extract.log`: `AssertionError: expected string at 11146`, from `decode_at` via `_decode_string_in_span` via `parse_value` via `parse_initializer`. Offset 11146 of `api/Data/JavaVerticalSeedData.cs` (line 251) is inside
   `new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "...", IsCompleted = true },`
   The cause is an offset mix-up: `parse_initializer` passes `part_offset`, the position of the whole `Name = value` part, but `_decode_string_in_span` then searches for the opening quote inside the stripped *value* and adds that index to `part_offset`, so it lands on the wrong character. Make the span start and the text searched refer to the same position. Then trace, by reading, one initializer of each shape the two C# files contain (regular string, verbatim `@"..."` string, interpolated or concatenated string if any, int, bool, enum, `null`, nested `new`, a bare identifier such as `verticalId`) through the parser and fix anything else that cannot work.
6. **mypy: 20 errors in 12 files.** Fix them at the cause. Several are real bugs, not typing noise: `workflow_service.py:474/479` assigns a QPS result to a variable typed as an optimize result; `fde_curriculum_seed_data.py:244-245` adds to a value that can be `None`; `session_service.py:156/202` and `learner_progress_service.py:358/365` use a possibly-missing row without checking. For each of those, compare against the C# and port its behaviour, including what it does when the row is missing.
7. **ruff: 142 findings**, all listed. Fix by hand, without reformatting whole files: `UP017` (99), `I001` (13), `F401` (10), `E741` (14, rename `l`), `UP042` (3), `UP035`, `F841`, and the one remaining `ASYNC240` at `exercise_workspace_builder.py:107`.
8. Leave `ruff format` alone.

## Agent 3 — `issue-intel/`

Log: `info/muse-prompts/corrections/round2/issue-intel.log`.

1. **Pin every unpinned package** in `requirements.txt` and `requirements-dev.txt` to the exact version in the log's `pip freeze` section, and make `pyproject.toml` agree.
2. **`tests/test_gate_parse.py`, 2 failures.** The parser returns `passed=0` for the line
   `Passed!  - Failed:     0, Passed:    12, Skipped:     0, Total:    12`
   and for the red case reports `failed=1` but `passed=0` (expected 11). The summary-line pattern does not match the real `dotnet test` output, which pads the numbers with several spaces. Fix the parser, not the tests. A real example of this output is in `info/muse-prompts/corrections/round2/dotnet.log`.
3. **`tests/test_no_merge.py::test_tools_are_exactly_the_seven`.** The agent exposes two tools the test does not allow: `evidence_pack` and `patch_files`. Check the tool list in `info/muse-prompts/issue-intel/BUILD-SPEC.md`. If the spec lists seven tools, remove or fold in the two extras; do not widen the test to fit the code. Say what you did with each.
4. **mypy: 11 errors, 10 of them in `app/mcp_server/server.py`.** The installed SDK is `mcp==2.3.0`. Against it: `Server` has no `list_tools` or `call_tool` decorator attributes, and `Tool(...)` takes `input_schema`, not `inputSchema`. The file was written for an older SDK interface. If you know the 2.x server interface for certain, port the file to it. If you do not, say so plainly, constrain the dependency to `mcp<2` in all three dependency files with a comment, and leave the code as it is. Do not guess at an interface.
   The eleventh: `app/pipeline/manager.py:94`, "Cannot infer type of lambda".
5. **ruff: 6 `I001`** in `alembic/env.py` and the five files under `alembic/versions/`. Fix the import order by hand.
6. Leave `ruff format` alone.

## Rules for all three agents

- No agent edits a file outside the folders named for it.
- Never describe a test, lint run or eval as passing. You have not run it.
- Append a section "Round 2 corrections" to the `PROGRESS.md` in your folder (Agent 1: `localization-ai/PROGRESS.md`): each numbered item, what you changed (file and line), and anything you could not resolve.
- If an item turns out to be wrong as described, do not guess around it. Say what you found instead.
- Finish with one report, a section per agent.
