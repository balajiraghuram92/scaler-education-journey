# Python Live Exercises: Authoring Spec (for exercise agents)

Repo root: `C:\Users\balaj\Documents\GitHub\Raghuram-git\scaler-education-journey` (Windows, Git Bash; Docker runs inside WSL `Ubuntu-26.04`).

You are turning **coding assignments** into **live, auto-graded exercises**. In the browser, the learner opens an editor with starter code and presses Run. Hidden pytest tests then run in a sandbox, and the learner sees which checks passed, why others failed, and any syntax or import ("compile") errors. The learner is a senior engineer preparing for Python, AI Engineer and FDE interviews. Write tests that teach: precise behaviour, edge cases, and clear failure messages.

## Permission (read carefully)

You **may** create `.py` files, but **only** inside `exercises/python/<module-slug>/<exercise-id>/`, for your assigned exercises. Do not touch any other file in the repo: no edits to the assignments JSON, lessons or app code. Don't run git.

## Source of truth

- Assignments: `api/Data/Content/python/assignments/<lesson-slug>.json`. Each has `slug`, `title`, `difficulty`, `problemStatement`, `requirements`, `workedExample`, `hints`, `referenceSolution` and `runCommand`. `referenceSolution` holds files as `**`path/file.py`**` followed by a fenced code block.
- Lesson to module mapping: `api/Data/Content/python/course.json`.
- **Worked example to copy exactly:** `exercises/python/python-object-model-concurrency/py-09-frequency-count/`. Read all four parts (`exercise.json`, `starter/`, `solution/`, `tests/`) before you start.

## Layout per exercise

```text
exercises/python/<module-slug>/<exercise-id>/
  exercise.json
  starter/<every file in files[]>        # what the learner sees; editable files are stubs
  solution/<every editable file>         # reference solution (passes all tests)
  tests/test_*.py  (+ optional conftest.py, helpers)   # hidden tests, pytest style
```

### `exercise.json`

- `id`: **exactly the assignment `slug`**, which is also the folder name.
- `lessonSlug`: the assignment file's `lessonSlug`.
- `title`: the assignment title.
- `language: "python"`.
- `difficulty`: `warm-up`, `core` or `stretch`, mapped from `Warm-up`, `Core` or `Stretch`.
- `estimatedMinutes`: a realistic estimate, between 10 and 60.
- `instructions`: 2–5 sentences of plain text with inline backticks, naming the file(s) to edit and what to build. The full problem statement is shown separately on the page.
- `runtime: { "profile": "python-pytest", "timeoutSeconds": 20 }`. Use up to 40 only for concurrency or async exercises that need it.
- `files`: every file placed in the workspace other than tests:
  - `editable: true` marks files the learner implements. Use 1–3, at most 4.
  - `editable: false` marks provided helper modules the exercise builds on, such as models from an earlier step. Their full code goes in `starter/` only.
  - `displayName` is the file name.
  - Keep the assignment's package paths (for example `config/counter.py`, `parking/design.py`).
  - Only `.py` files. Nothing under `tests/`.
- `testSuite: { "visible": false, "path": "tests" }`.
- `evidence`: **one entry per test function**, as `{ id, label, testMethod }`. The `label` is the short, learner-facing statement of the behaviour, for example "Raises ValueError for a negative amount".

### `starter/`

- Expose the same public API the tests import: modules, classes, functions, method signatures with type hints, constants, Enums, exception classes, and the dataclass or field declarations the problem statement says are given.
- Replace behaviour with `raise NotImplementedError("...")`, or leave a minimal placeholder that is clearly incomplete.
- Add docstrings that state the contract, so the learner knows what to write. **Never include solution logic.**
- The starter **must import cleanly**. Tests must then be *collected* and *fail* (pytest exit 1), never error at import.
- For "extend this design" Stretch tasks, the earlier code goes in as `editable: false` files, and the learner edits only the new module.

### `solution/`

- Start from the assignment's `referenceSolution` code.
- Remove module-level demo code that runs on import (`print(...)` examples, `if __name__ == "__main__":` blocks are fine to keep).
- Fix any defect your tests expose, keeping the same API.
- It must pass every test.

### `tests/`

- Use pytest style: plain `test_*` functions, fixtures, `pytest.raises`, `parametrize` (avoid many cases per function, because each function is one evidence row). Convert `unittest.TestCase` tests to functions.
- **5–10 test functions per exercise** covering:
  - the main behaviour
  - edge cases from the requirements: empty input, invalid input and the exceptions raised, boundaries
  - design constraints where they can be checked: an abstract class can't be instantiated, a Protocol is satisfied, a singleton returns the same instance, a pattern is honoured
- Reuse the assignment's existing tests where they exist, then add what's missing. For assignments without tests, write them from the problem statement and requirements.
- Give assertions useful messages, for example `assert x == 3, "expected 3 slots after parking two cars"`. The learner sees them when a test fails.
- Tests must be deterministic and fast (well under 10 s total), with no network and no real sleeps over about 0.2 s.
  - For concurrency, use `threading.Event`/`Barrier`, join threads with a timeout, and assert on outcomes, not timing.
  - Freeze time with `freezegun` or by injecting a clock.
- Libraries available in the runner: pytest 8.4, pytest-asyncio (use `@pytest.mark.asyncio`), anyio, httpx, respx, fastapi, pydantic 2, pydantic-settings, sqlalchemy 2 and aiosqlite (use SQLite in-memory, never Postgres), numpy, tenacity and freezegun. Nothing else.
- Don't test private implementation details unless the requirement is about them.

## Skip rules

If an assignment is not code (a design write-up, a SQL-only schema, a diagram) or can't be auto-graded honestly, **don't create an exercise**. List it in your report with the reason.

## Verify (required for every exercise)

1. Static checks, from the repo root in Git Bash:
   ```bash
   node runner/python/check-manifests.js exercises/python/<module>/<id> [more dirs...]
   ```
2. Run the real sandbox: solution → all pass, starter → collected and failing.
   ```bash
   wsl.exe -d Ubuntu-26.04 -- bash -c "cd /mnt/c/Users/balaj/Documents/GitHub/Raghuram-git/scaler-education-journey && bash runner/python/verify-exercise.sh exercises/python/<module>/<id> [more dirs...]"
   ```
   The runner image `neuralascent-python-runner:dev` is already built. **Every exercise must print `PASS`.**
3. For anything involving threads, processes, async or time, run step 2 **three times** and make sure it passes every time.

## Report

When you finish, report:
- each exercise created (id, number of tests, editable and provided files)
- each skipped assignment with its reason
- any defect you fixed in a reference solution
- confirmation that `check-manifests.js` reports 0 problems and `verify-exercise.sh` passes for all of your exercises

Don't paste file contents.
