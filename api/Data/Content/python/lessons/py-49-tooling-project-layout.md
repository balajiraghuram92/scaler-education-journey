# Tooling, Packaging and Project Layout

Teams rarely lose weeks to a clever algorithm; they lose them to "works on my machine": a dependency that resolved differently in CI, tests that pass only because the repo root is on `sys.path`, a formatter war in every pull request. A senior engineer sets up a project so that a new hire runs one command and gets the same environment as production, and so that CI rejects drift automatically. In interviews, this shows up as "how would you structure and ship this service?"

## Concepts Covered

### `pyproject.toml` as the single source of truth

PEP 518 and PEP 621 moved build configuration and project metadata into `pyproject.toml`, replacing `setup.py`, `setup.cfg`, `requirements*.txt` and a pile of tool-specific files. The file has three kinds of tables: `[build-system]` (which backend builds the wheel), `[project]` (name, version, `requires-python`, runtime `dependencies`, `optional-dependencies` for extras, `scripts` for console entry points), and `[tool.*]` (configuration for ruff, mypy, pytest and others). Development-only dependencies belong in a PEP 735 `[dependency-groups]` table, which, unlike extras, is never published with the package. I parsed the file below with the standard-library `tomllib` to confirm it is valid TOML.

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "gateway"
version = "0.4.0"
description = "LLM gateway with budgets and retries"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115,<1",
    "httpx>=0.27,<1",
    "pydantic>=2.8,<3",
]

[project.optional-dependencies]
otel = ["opentelemetry-sdk>=1.27"]

[project.scripts]
gateway = "gateway.cli:main"

[dependency-groups]
dev = ["pytest>=8", "pytest-asyncio", "mypy", "ruff"]

[tool.hatch.build.targets.wheel]
packages = ["src/gateway"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "ASYNC", "PT", "RUF"]

[tool.mypy]
strict = true
python_version = "3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config"
asyncio_mode = "auto"
markers = ["integration: needs real services"]
```

Distinguish **abstract** requirements from **concrete** ones. `pyproject.toml` says what the code needs (`httpx>=0.27,<1`); a lock file says exactly what was tested (`httpx==0.28.1` plus hashes). Libraries publish ranges; applications and services also commit a lock file. Common build backends are `hatchling`, `setuptools`, `flit-core` and (newer) `uv_build`; they are interchangeable behind the PEP 517 interface.

### uv: environments, lock files and Python versions

`uv` is a fast, Rust-based tool that replaces `pip`, `venv`, `pip-tools` and much of `pyenv`. The commands you should know:

```bash
uv init --package gateway        # src layout + pyproject.toml
uv python install 3.13           # download and manage interpreters
uv python pin 3.13               # write .python-version for the project
uv add httpx "pydantic>=2.8"     # edit pyproject.toml and update uv.lock
uv add --dev pytest ruff mypy    # dev dependency group
uv sync --locked                 # create .venv from uv.lock, fail if the lock is stale
uv run pytest -q                 # run inside the project environment
uv lock --check                  # CI: is uv.lock up to date with pyproject.toml?
uv build                         # sdist + wheel into dist/
```

`uv.lock` is a cross-platform lock file that you **commit**. `uv sync --locked` fails when `pyproject.toml` and the lock disagree, which is what you want in CI; `--frozen` uses the lock without checking it, which is faster but hides drift. The project is installed in editable mode by default, so your source edits take effect immediately. The older alternative is `pip-tools` (`pip-compile` produces a pinned `requirements.txt` with hashes); the principle is the same.

### ruff: lint and format in one tool

`ruff` replaces flake8 and its plugins, isort, pyupgrade and black with one fast binary. `ruff check` lints (add `--fix` for safe autofixes), `ruff format` formats. Choose rule families deliberately: `E`/`F` (pycodestyle errors, pyflakes), `I` (import sorting), `UP` (pyupgrade, modern syntax), `B` (bugbear: mutable default arguments, `raise ... from`), `SIM` (simplifications), `ASYNC` (blocking calls in async code), `PT` (pytest style), `S` (security checks from bandit) and `RUF`. Start with a small set, fix the findings once, then ratchet. Per-file ignores (`[tool.ruff.lint.per-file-ignores]`) let tests skip rules like `S101` (use of `assert`) without weakening the production code.

> **Pitfall:** Running the formatter as part of lint fixes in CI. Put `ruff format --check` in CI (it fails, never rewrites), and let developers and pre-commit do the rewriting.

### pre-commit: fail fast on the laptop

`pre-commit` runs hooks on staged files before each commit, so style issues never reach review. Keep hooks quick (ruff, whitespace, secrets scan) and leave slow work (the full test suite) to CI. Always pin hook revisions, and run `pre-commit autoupdate` on a schedule. Type checking is usually a `repo: local` hook using `uv run mypy` with `pass_filenames: false`, because checkers need the whole project to resolve imports.

```text
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.0          # pin a release, bump with `pre-commit autoupdate`
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy
        language: system
        types: [python]
        pass_filenames: false
```

### The `src` layout and test layout

In a flat layout (`gateway/` at the repo root), running `python` or `pytest` from the root puts the working directory on `sys.path`, so `import gateway` finds your **source tree** even if packaging is broken: a missing `__init__.py` or data file is invisible until a user installs the wheel. The `src/` layout forces tests to import the **installed** package. I ran this experiment:

```bash
mkdir -p flat/gateway src_layout/src/gateway
echo "VERSION = 'local'" > flat/gateway/__init__.py
echo "VERSION = 'local'" > src_layout/src/gateway/__init__.py
(cd flat && python -c "import gateway; print('flat: imported', gateway.VERSION)")
(cd src_layout && python -c "import gateway")
```

```text
flat: imported local
ModuleNotFoundError: No module named 'gateway'
```

The flat layout silently succeeded; the src layout failed until the package was installed (editable installs do that for you). Keep `tests/` outside `src/`, mirror the package structure (`tests/budget/test_service.py`), and put shared fixtures in `tests/conftest.py`. Tests are not shipped in the wheel.

### Versioning and building wheels

Choose SemVer for libraries with consumers and CalVer for services if you prefer date-based releases, but pick **one source of truth**: a static `version` in `pyproject.toml`, or `dynamic = ["version"]` with a plugin that derives it from git tags. Read it at runtime with `importlib.metadata.version("gateway")` instead of duplicating it in `__version__`. `uv build` (or `python -m build`) produces an **sdist** and a **wheel** in `dist/`; a pure-Python wheel is tagged `py3-none-any`. Smoke-test the wheel in a clean environment (create a throwaway venv, `pip install dist/*.whl`, then `python -c "import gateway"`) before publishing, and in Docker use a multi-stage build that installs the wheel and the locked dependencies into the final image.

### CI quality gates

A pipeline is a list of gates, ordered cheap to expensive, that must all be green to merge. A minimal one for this project:

```bash
set -euo pipefail
uv sync --locked                      # reproducible env, fails on a stale lock
uv run ruff check .                   # lint
uv run ruff format --check .          # formatting, never rewrites in CI
uv run mypy                           # strict type check
uv run pytest -q --cov=gateway --cov-fail-under=85
uv build                              # packaging still works
```

Add a matrix over supported Python versions, a dependency audit (`pip-audit`), caching keyed on `uv.lock`, and make the checks **required** in branch protection. Gates that are optional rot within a month.

## Practical Backend Scenario

A new FastAPI service for document ingestion is about to go to production. Developers use three Python versions, the Docker image installs unpinned dependencies, and a transitive `pydantic` upgrade changes a validation message that a client parses. The fix is structural: `requires-python`, `uv.lock` committed, `uv sync --locked` in both CI and the Dockerfile, a src layout so tests exercise the installed package, and required CI gates so a dependency bump arrives as a pull request with test results.

## Practice Loop

1. Run `uv init --package gateway` and compare the generated tree with the layout above; add `httpx` and a dev group, and read the diff in `pyproject.toml` and `uv.lock`.
2. Reproduce the flat versus src experiment, then break packaging on purpose (forget a data file) and see which layout hides it.
3. Enable ruff with the rule set above, run `ruff check --fix`, and read every remaining finding before adding any ignore.
4. Add the pre-commit config, commit a badly formatted file, and watch the hook fix it.
5. Write the CI script as a single `ci.sh`, then wire it into your CI system's required checks.
6. Run `uv build`, install the wheel into a clean environment, and call the console script.

## Evidence of Understanding

- I can explain the roles of `[build-system]`, `[project]`, `[dependency-groups]` and `[tool.*]`.
- I can explain why applications commit a lock file, and the difference between `--locked` and `--frozen`.
- I can justify the src layout with a concrete failure it prevents.
- I can name which checks belong in pre-commit and which only in CI, and why formatting is checked rather than applied in CI.
- I can build a wheel and verify it in a clean environment.

## Interview Questions to Rehearse

### Q: What goes in `pyproject.toml` versus the lock file?

`pyproject.toml` declares intent: supported Python versions and dependency ranges. The lock file records the exact resolved versions and hashes, for all platforms, that CI tested. Libraries publish ranges; services additionally commit the lock and install from it.

### Q: Why use the src layout?

It stops the working directory from shadowing the installed package, so tests exercise what users will install and packaging mistakes surface early. It also keeps import paths unambiguous and separates code from repo-level files.

### Q: How do you make installs reproducible across dev, CI and Docker?

Pin the interpreter (`requires-python`, `.python-version`), commit the lock file, and use the same command everywhere (`uv sync --locked`). CI also runs `uv lock --check` so a drifted lock fails the build.

### Q: What does ruff replace, and how do you adopt it on a legacy codebase?

It replaces flake8 and plugins, isort, pyupgrade and black. On a legacy codebase enable a small rule set, run `--fix` once in a dedicated commit (added to `.git-blame-ignore-revs`), use per-file ignores for the worst offenders, and tighten gradually.

### Q: Extras versus dependency groups?

Extras (`optional-dependencies`) are published with the package so consumers can opt in (`gateway[otel]`). Dependency groups (PEP 735) are local to the project, for dev, test and docs tooling, and are not part of the wheel's metadata.

### Q: What would your minimum CI gate list be?

Locked sync, lint, format check, strict type check, tests with a coverage floor, and a build-and-import smoke test of the wheel, all required for merge, plus a scheduled dependency audit.

## Common Pitfalls

- Not committing the lock file for an application, then debugging differences between laptop and CI.
- Using `--frozen` in CI so that a stale lock goes unnoticed.
- Flat layout hiding packaging bugs until after release.
- Dev tools in `dependencies`, so they ship to production images.
- Having `ruff format` rewrite files in CI instead of failing the build.
- Unpinned pre-commit hooks that change behaviour overnight.
- Duplicating the version in `pyproject.toml` and `__version__`, which then disagree.
- Optional CI checks that nobody enforces.

## Suggested Extension

Containerise the service with a multi-stage Dockerfile: stage one runs `uv build` and exports the locked dependencies; stage two installs only the wheel and its locked runtime dependencies into a slim image running as a non-root user. Add a CI job that builds the image and runs a smoke test against `/healthz`.
