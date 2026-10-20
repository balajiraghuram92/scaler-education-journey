# pytest Fundamentals and Fixtures

A test suite is a production system with one customer: the engineer who has to trust a green build at 6 p.m. on a Friday. Slow, order-dependent or over-mocked suites get ignored, and then they stop catching regressions. In interviews, "how do you structure tests for this service?" is a cheap way to see whether you have maintained code for years or only written it.

## Concepts Covered

### Discovery and assertion rewriting

By default pytest collects files named `test_*.py` or `*_test.py`, then functions named `test_*` and methods of classes named `Test*` (the class must not define `__init__`). Set `testpaths`, `python_files` and friends in `pyproject.toml` so a bare `pytest` run does not wander into `node_modules` or a vendored directory. Prefer `--import-mode=importlib` for new projects: the default `prepend` mode mutates `sys.path` and forces unique test-module basenames unless you add `__init__.py` files.

The reason plain `assert` works is **assertion rewriting**. When pytest imports a test module (and `conftest.py` files and registered plugins) it rewrites the AST of every `assert` so that, on failure, it can show the intermediate values: both sides of `==`, the diff between two lists, the sub-expression that was `False`. Two consequences matter. First, helper modules that your tests import are not rewritten, so asserts inside a shared `assertions.py` give bare `AssertionError`s unless you call `pytest.register_assert_rewrite("assertions")` before importing it. Second, `python -O` strips asserts entirely, which is also why production code must never use `assert` for validation.

Use the right comparison tools instead of hand-rolled ones: `pytest.approx` for floats (relative tolerance 1e-6 by default), and `pytest.raises(..., match=...)`, where `match` is applied with `re.search` against `str(exception)`.

```python
import pytest
from gateway.budget import BudgetExceeded, BudgetService


def test_cost_is_float_safe():
    assert 0.1 + 0.2 == pytest.approx(0.3)


def test_rejects_non_positive_tokens(service: BudgetService):
    with pytest.raises(ValueError, match="positive"):
        service.charge("acme", 0)


def test_budget_exceeded_carries_context(service: BudgetService):
    service.charge("acme", 900)
    with pytest.raises(BudgetExceeded) as excinfo:
        service.charge("acme", 200)
    assert "acme" in str(excinfo.value)
```

### Fixtures, scopes and `yield` teardown

A fixture is a function registered with `@pytest.fixture`. A test (or another fixture) asks for it by naming a parameter; pytest builds a dependency graph, resolves it, and caches the value for the fixture's **scope**: `function` (default), `class`, `module`, `package` or `session`. Wider scope means fewer expensive setups but more shared state. A fixture may only depend on fixtures of the same or wider scope; a `session` fixture that requests a function-scoped one fails with `ScopeMismatch`.

Use `yield` to split setup from teardown. Everything after the `yield` runs when the scope ends, in reverse order of setup, even if the test failed. If the setup code before the `yield` raises, the code after it does **not** run, so acquire the resource first and put the cleanup right after the `yield`. For several independent resources, make several small fixtures rather than one large one, so a failure in the third setup still cleans up the first two.

```python
import sqlite3
from collections.abc import Iterator

import pytest
from gateway.budget import BudgetService
from gateway.repos import SqlUsageRepo


@pytest.fixture(scope="session")
def engine() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE usage(tenant TEXT PRIMARY KEY, tokens INTEGER NOT NULL)"
    )
    yield conn
    conn.close()


@pytest.fixture
def db(engine: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    yield engine
    engine.rollback()  # every test starts from an empty table


@pytest.fixture
def service(db: sqlite3.Connection) -> BudgetService:
    return BudgetService(SqlUsageRepo(db), limit=1_000)
```

The expensive object (the connection or schema) lives at `session` scope, and a cheap function-scoped fixture undoes each test's writes. I checked this rollback pattern against the standard-library `sqlite3` module: after two charges and a `rollback()`, a read returns 0.

Other fixture features worth knowing: `autouse=True` applies a fixture to every test in its scope (use it for things like freezing a random seed, never for hidden business setup), `request.addfinalizer` registers teardown callbacks, and a fixture can return a **factory** function when a test needs to create several objects with different parameters.

> **Pitfall:** A module- or session-scoped fixture that returns a mutable object (a list, a dict, a fake repository) leaks state between tests. The suite passes in file order and fails under `pytest-randomly` or `pytest-xdist`. Keep shared fixtures immutable, or reset them in a function-scoped wrapper.

### `conftest.py` layering

Fixtures defined in a `conftest.py` are visible to every test in that directory and below, with no import. Layer them by blast radius: repo-wide fixtures (clock, settings) in `tests/conftest.py`, domain-specific ones in `tests/billing/conftest.py`. Resolution is nearest-first, so a test module or a deeper `conftest.py` can **override** a fixture of the same name, and the override can itself request the parent fixture by that name to wrap it. Never import from `conftest.py`; if two places need the same helper, put it in a normal module. Declare `pytest_plugins` only in the top-level `conftest.py`.

### Parametrization and markers

`@pytest.mark.parametrize` generates one test per case, so one failing input does not hide the rest. Give cases readable ids, either with `ids=[...]` or with `pytest.param(..., id="...")`, which also lets you attach marks to a single case. Stacking two `parametrize` decorators produces the cartesian product.

```python
import pytest
from gateway.budget import BudgetExceeded, BudgetService


@pytest.mark.parametrize(
    ("used", "ask", "ok"),
    [
        pytest.param(0, 1_000, True, id="exactly-at-limit"),
        pytest.param(999, 1, True, id="last-token"),
        pytest.param(1_000, 1, False, id="one-over"),
        pytest.param(0, 1_001, False, id="single-request-over"),
        pytest.param(
            500, 500, True, id="known-bug-123",
            marks=pytest.mark.xfail(reason="rounding bug #123", strict=True),
        ),
    ],
)
def test_limit_boundary(service: BudgetService, used: int, ask: int, ok: bool):
    if used:
        service.repo.add("acme", used)
    if ok:
        service.charge("acme", ask)
    else:
        with pytest.raises(BudgetExceeded):
            service.charge("acme", ask)
```

Markers classify tests: `skip`, `skipif`, `xfail`, and custom ones such as `@pytest.mark.integration`. Register custom markers under `[tool.pytest.ini_options] markers = [...]` and run with `--strict-markers`, otherwise a typo like `@pytest.mark.integraton` silently selects nothing. With `xfail(strict=True)`, an unexpected pass fails the build, which forces you to delete the marker once the bug is fixed.

### Built-in fixtures: `tmp_path`, `monkeypatch`, `capsys`

- `tmp_path` is a unique `pathlib.Path` directory per test; use `tmp_path_factory` when a wider-scoped fixture needs one.
- `monkeypatch` sets attributes, environment variables, dict items, working directory and `sys.path`, and undoes every change at test teardown.
- `capsys` and `capfd` capture what the code wrote to stdout and stderr; `caplog` captures log records.

```python
import json
from pathlib import Path

import pytest
from gateway.settings import load_settings


def test_settings_from_env_and_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg = tmp_path / "gateway.json"
    cfg.write_text(json.dumps({"limit": 500}))
    monkeypatch.setenv("GATEWAY_CONFIG", str(cfg))
    monkeypatch.delenv("GATEWAY_LIMIT", raising=False)
    assert load_settings().limit == 500


def test_cli_prints_summary(capsys: pytest.CaptureFixture[str]):
    from gateway.cli import main
    main(["usage", "acme"])
    out = capsys.readouterr().out
    assert "acme" in out
```

### Designing tests for a service layer

Test through the public methods of the service, with a fast **fake** of its edge (an in-memory repository) in most tests, and a small number of tests that run the real adapter against a real database. Name tests after behaviour (`test_rejects_charge_beyond_limit`), structure them as arrange, act, assert, and keep one reason to fail per test. Put the object under test behind one `service` fixture so a constructor change touches one place. Resist fixtures that do too much: a fixture named `everything_set_up` hides the arrange step and makes failures unreadable.

## Practical Backend Scenario

You run an LLM gateway that enforces per-tenant token budgets. A customer reports being charged twice for one request after a retry, and the fix touches `BudgetService.charge`. A good suite lets you write the failing test first against an in-memory repository (milliseconds), pin the boundary cases with a parametrized test, and run the same contract tests against the SQL adapter on CI. A bad suite mocks `repo.add` with `MagicMock`, asserts it was called once, and stays green while the real SQL upsert double-counts.

## Practice Loop

1. Create `gateway/budget.py` with `BudgetService`, `BudgetExceeded` and a `UsageRepo` protocol, and an in-memory `FakeUsageRepo`.
2. Write the `service` fixture in `tests/conftest.py` using the fake, then write five behaviour tests, including the boundary table above with `pytest.param(..., id=...)`.
3. Add a `SqlUsageRepo` over `sqlite3` with a `session`-scoped connection and a function-scoped rollback fixture. Run the same contract tests against both repositories by parametrizing the fixture with `params=["fake", "sql"]`.
4. Register an `integration` marker, enable `--strict-markers`, and run `pytest -m "not integration"`.
5. Deliberately make a session fixture depend on `tmp_path` and read the `ScopeMismatch` error. Fix it with `tmp_path_factory`.
6. Run with `-p no:randomly` and then with `pytest-randomly` or `-n auto` installed. Find any test that depends on order.

## Evidence of Understanding

- I can explain how assertion rewriting works and name one case where it does not apply.
- I can predict the setup and teardown order of three fixtures with different scopes and autouse flags.
- I can explain why teardown after `yield` is skipped if setup raised, and how to structure fixtures so it does not leak resources.
- I can override a fixture in a nested `conftest.py` and wrap the parent version.
- I can justify a fake over a mock for a repository, and name the tests that still need the real adapter.

## Interview Questions to Rehearse

### Q: How does a bare `assert` produce such detailed failure messages?

pytest installs an import hook that rewrites the AST of test modules, `conftest.py` files and registered plugins. Each `assert` is compiled into code that keeps intermediate values and builds an explanation on failure. Helper modules are not rewritten unless registered with `pytest.register_assert_rewrite` before import, and the whole mechanism disappears under `python -O`.

### Q: What decides fixture scope, and what goes wrong with wide scopes?

Scope is about setup cost versus isolation. Put expensive, read-only resources (engine, schema, container) at `session` or `module` scope and cheap mutable state at `function` scope. A wide-scope fixture returning mutable state creates order-dependent tests that fail only under random ordering or xdist. A wide fixture also cannot request a narrower one: that raises `ScopeMismatch`.

### Q: Walk me through teardown semantics of a `yield` fixture.

Code before the `yield` is setup; code after is teardown, run when the scope ends in reverse order of setup, even when the test failed. If setup raises, the post-`yield` code never runs, so split multiple resources into separate fixtures so each one's cleanup is registered as soon as it is acquired.

### Q: How do you organise `conftest.py` files in a large repo?

By blast radius. Shared plumbing at the top, domain fixtures in the subpackage that uses them. Nearest definition wins, so a subdirectory can override a fixture and wrap the parent one by requesting it by name. I never import from `conftest.py` and I keep `pytest_plugins` at the root.

### Q: When do you use `parametrize` versus separate tests?

When the behaviour is the same and only data differs. I give each case an `id` so a failure names the scenario, use `pytest.param` for per-case marks, and avoid giant tables that mix unrelated behaviour. Different behaviour gets its own test with its own name.

### Q: A test passes alone and fails in the full run. How do you debug?

Suspect shared state: a wide-scope mutable fixture, module-level globals, environment variables set without `monkeypatch`, or files written outside `tmp_path`. Run with random ordering and `-x`, bisect with `--lf` and `-k`, and print fixture setup with `--setup-show`.

## Common Pitfalls

- Using `assert` in application code for validation; it vanishes under `-O`.
- Session-scoped fixtures that return mutable objects, causing order-dependent failures.
- Asserting on mock calls instead of observable outcomes, so refactors break tests that never caught bugs.
- Forgetting `--strict-markers`, so misspelled markers silently select nothing.
- Importing helpers from `conftest.py`, which breaks under different import modes.
- Setting `os.environ` directly in a test instead of `monkeypatch`, leaking into later tests.
- Writing test data into the repo instead of `tmp_path`.
- Giant "set everything up" fixtures that hide the arrange step.

## Suggested Extension

Write a reusable **contract test** class for `UsageRepo` (as a plain module of tests parametrized over repository factories) and run it against the fake, the SQLite adapter, and a Postgres adapter started with a container fixture. Mark the Postgres leg `integration` and make CI run it nightly.
