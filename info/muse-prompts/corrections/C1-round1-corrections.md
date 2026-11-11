# C1 — Round 1 corrections for the LA, P and G tracks

The reviewer ran every check that the first run could not. The raw output is in `info/muse-prompts/corrections/round1/`:

- `dotnet.log` — `dotnet build api` and `dotnet test`
- `localization-ai.log`, `api-python.log`, `issue-intel.log` — for each project: `pip install`, `ruff check`, `ruff format --check`, `mypy app`, `pytest`

Each Python log was produced in a clean `python:3.12-slim` container, from a copy of the project folder, with no database and no Docker available inside it.

Paste everything below this line into Muse Code at the repository root.

---

Use a workflow to fan out three parallel agents, one per folder. Work on the current branch; do not create or switch branches; do not commit.

You cannot run commands in this environment, so do not try. A reviewer runs the checks after you finish and sends back the next log. Your job in this round is narrow: **make each project install, import and collect its tests**, and fix the specific failures listed. Do not add features, do not refactor, do not start any phase that is not finished.

Read the log for your project in full before changing anything. Fix causes, not symptoms: where one mistake produces many errors, find the one mistake.

## Agent 1 — `localization-ai/` and the .NET test file

Log: `info/muse-prompts/corrections/round1/localization-ai.log` and `dotnet.log`.

1. **Six test errors, one cause.** `tests/test_api.py` and `tests/test_api_pipeline.py` fail in setup with `AttributeError: 'FixtureFunctionDefinition' object has no attribute 'main'`. A fixture is named the same as something it then tries to use as a module (a fixture called `app` shadowing the `app` package, or similar). Rename the fixture and fix every use.
2. **One real failure:** `tests/test_mt_optimize.py::test_optimize_checks_catch_bad_output`. Read the assertion in the log, then read `app/pipeline/mt_optimize.py`. Decide which is wrong, the check or the test, from the LA3 specification (placeholders preserved, glossary terms present, output not empty, output not identical to the source), and fix that one. Say which you changed and why.
3. **mypy: 36 errors in 4 files.** The first group is in `app/routers/eval.py`: the response model is built with snake_case keyword arguments (`tokens_used`, `fallback_count`, `prompt_version`) but the model's fields are camelCase. Make the models accept their Python field names (populate-by-name) or construct them correctly, consistently across all routers. Then clear the rest of the list in the log.
4. **ruff: 5 errors**, listed in the log. Fix them by hand.
5. **30 tests are skipped** because they need a database. Leave the skip logic alone, but check each skipped test file for the same fixture-naming mistake as item 1.
6. **`tests/StudyTracker.Api.Tests/Localization/LocalizationAiWorkflowTests.cs` does not compile.** Three errors, in `dotnet.log`:
   - lines 93 and 108: `StudyTracker.Api.Options.Create` does not exist. `Options.Create(...)` is being resolved against the project's own `StudyTracker.Api.Options` namespace. Use `Microsoft.Extensions.Options.Options.Create(...)` fully qualified.
   - line 327: an `Assert.Equal` call is being given a collection and a sequence of `int?` where the overload chosen expects `DateTime`. Rewrite that assertion so both arguments have the same element type.
7. Do **not** write the EF migration; the reviewer generates it.

## Agent 2 — `api-python/`

Log: `info/muse-prompts/corrections/round1/api-python.log`.

Nothing in this project has been exercised yet: no test file loads. Fix these in order.

1. **Syntax error:** `app/routers/chapters.py` line 654, "Expected a statement" (an unbalanced bracket a few lines above it). ruff reports 131 `invalid-syntax` items; check whether they all come from this one place, and if any other file has its own syntax error, fix that too. After this, re-read every router file top to bottom for bracket balance; this is exactly the kind of error that cannot be caught without running the code.
2. **Every test file fails at import** with `KeyError: 'first_column_name'`, raised from the naming convention in `app/models/base.py` line 16. `first_column_name` is not a token SQLAlchemy provides. The foreign-key names must match what EF Core generated in the real database (`FK_<table>_<principal table>_<column>`), so use SQLAlchemy's real token for the constrained column (`column_0_name`), and check the other entries in the same convention dictionary for invented tokens. Where the EF name cannot be produced by a convention, name the constraint explicitly on the model.
3. **`requirements-dev.txt` pins a version that does not exist:** `types-cryptography==44.0.0.20251029`. That stub package stopped at 3.3.x because `cryptography` now ships its own types. Remove the line. Then check every other pin in `requirements.txt` and `requirements-dev.txt` against what you can verify; do not invent version numbers. Where you are not certain a version exists, copy the pin from `ai-agent/requirements.txt` if the package is there, and otherwise leave the package unpinned with a comment saying the reviewer will pin it.
4. **4 undefined names** (ruff `F821`). These are real bugs. Find each in the log and fix it.
5. **Blocking file access inside async functions** (ruff `ASYNC230`, `ASYNC240`, 27 places). Decide once how the port handles file reads in async code and apply it consistently; a short comment at the first use explaining the choice is enough.
6. Leave the 328 line-length findings and the 135 `B008` findings (FastAPI `Depends(...)` defaults) alone in this round. Instead, configure ruff in `pyproject.toml` to ignore `B008`, and set the line length to match what the code was written to. Do not reformat files.
7. **The seed data was never extracted.** `app/seed/` has the seeder modules but there is no `app/seed/data/`. Do not hand-write the data. Make sure `tools/extract_seed_data.py` is complete, and state the exact command the reviewer should run to produce the JSON files.
8. Update `PORT-MAP.md`: every row you cannot honestly call verified is `done (unverified)`, not `done`.

## Agent 3 — `issue-intel/`

Log: `info/muse-prompts/corrections/round1/issue-intel.log`.

1. **The project does not install.** `pip install -e .` fails with "Multiple top-level packages discovered in a flat-layout: ['app', 'web', 'evals', 'alembic', 'synthetic', 'sample_repo']". Declare the packages explicitly in `pyproject.toml` (`app`, `evals`, `synthetic` and their sub-packages; not `web`, `sample_repo` or `alembic`). Also add a `requirements.txt` and `requirements-dev.txt` with the same dependencies, pinned only to versions you can verify, so the reviewer can install without building the package.
2. Because of item 1, no test could import its dependencies, so nothing is known about the tests. Read each of the nine test files against the code it tests and fix anything that plainly cannot work (wrong import path, wrong function name, wrong signature).
3. **mypy: 56 errors in 17 files**, and **ruff: 24 errors**, in the log. Fix them.
4. **G4 has no entry in `PROGRESS.md`.** Compare what exists on disk against the ten numbered items of the G4 prompt in `info/muse-prompts/issue-intel/G0-to-G4-prompts.md`. Finish only what is missing or half-written, then write the G4 entry listing, item by item, done or not done.
5. `sample_repo/` must be its own git repository with a `main` branch and two release branches, and it is not (there is a `setup-history.py` instead). Confirm that script, when run, creates the repository, the commits that introduce the 12 planted bugs, and the two release branches. State the exact command for the reviewer.
6. State the exact commands that generate the synthetic corpus and the ground truth.

## Rules for all three agents

- No agent edits a file outside its own folder (Agent 1 also has the one .NET test file named above).
- Never describe a test, lint run or eval as passing. You have not run it.
- Append a section "Round 1 corrections" to the `PROGRESS.md` in your folder: each numbered item above, what you changed (file and line), and anything you could not resolve.
- If an item turns out to be wrong as described, do not guess around it. Say what you found instead.
- Finish with one report, a section per agent.
