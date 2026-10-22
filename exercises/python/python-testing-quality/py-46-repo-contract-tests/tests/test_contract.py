import json
import sqlite3
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from budget import BudgetExceeded, BudgetService, InMemoryUsageRepo, UsageRepo
from repos import FileUsageRepo, SqlUsageRepo

RepoFactory = Callable[[], UsageRepo]


@pytest.fixture(params=["memory", "sql", "file"])
def repo_factory(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[RepoFactory]:
    opened: list[SqlUsageRepo] = []
    if request.param == "memory":
        shared = InMemoryUsageRepo()

        def factory() -> UsageRepo:
            return shared
    elif request.param == "sql":

        def factory() -> UsageRepo:
            r = SqlUsageRepo(tmp_path / "usage.db")
            opened.append(r)
            return r
    else:

        def factory() -> UsageRepo:
            return FileUsageRepo(tmp_path / "usage.json")

    yield factory
    for r in opened:
        r.close()


def test_unknown_tenant_is_zero(repo_factory):
    assert repo_factory().get("nobody") == 0, "unknown tenants must have usage 0"


def test_add_returns_running_total(repo_factory):
    repo = repo_factory()
    assert repo.add("acme", 10) == 10
    assert repo.add("acme", 5) == 15
    assert repo.get("acme") == 15


def test_tenants_are_isolated(repo_factory):
    repo = repo_factory()
    repo.add("acme", 10)
    assert repo.get("globex") == 0


def test_writes_visible_through_a_second_instance(repo_factory):
    repo_factory().add("acme", 7)
    assert repo_factory().get("acme") == 7, "a write must be visible to another instance (commit / flush it)"


def test_service_enforces_limit_on_every_backend(repo_factory):
    service = BudgetService(repo_factory(), limit=100)
    service.charge("acme", 60)
    with pytest.raises(BudgetExceeded):
        service.charge("acme", 41)
    assert service.remaining("acme") == 40


def test_sql_repo_persists_after_close_and_reopen(tmp_path):
    path = tmp_path / "u.db"
    first = SqlUsageRepo(path)
    first.add("acme", 10)
    first.add("acme", 5)
    first.close()
    second = SqlUsageRepo(path)
    try:
        assert second.get("acme") == 15
    finally:
        second.close()
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
    finally:
        conn.close()
    assert rows >= 1, "the table must be created in the database file"


def test_file_repo_missing_file_means_no_usage(tmp_path):
    path = tmp_path / "usage.json"
    repo = FileUsageRepo(path)
    assert repo.get("acme") == 0
    assert not path.exists(), "reading must not create the file"


def test_file_repo_writes_atomically_without_leftovers(tmp_path):
    path = tmp_path / "usage.json"
    repo = FileUsageRepo(path)
    repo.add("acme", 3)
    repo.add("acme", 4)
    assert json.loads(path.read_text(encoding="utf-8")) == {"acme": 7}
    assert [p.name for p in tmp_path.iterdir()] == ["usage.json"], "temporary files must be replaced, not left behind"


def test_file_repo_replaces_via_os_replace(tmp_path, monkeypatch):
    import os

    calls: list[tuple[str, str]] = []
    real = os.replace

    def spy(src, dst):
        calls.append((str(src), str(dst)))
        return real(src, dst)

    monkeypatch.setattr(os, "replace", spy)
    FileUsageRepo(tmp_path / "usage.json").add("acme", 1)
    assert len(calls) == 1, "add must write a temp file and publish it with os.replace"
    assert calls[0][0] != calls[0][1]
