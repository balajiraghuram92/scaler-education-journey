import re
import sqlite3

import pytest

from uow import NoActiveTransaction, TransactionAlreadyBegun, UnitOfWork, import_messages

INSERT = "INSERT INTO messages(conversation_id, external_id, body) VALUES (1, '{}', 'x')"
SCHEMA = (
    "CREATE TABLE messages (id INTEGER PRIMARY KEY, conversation_id INT, external_id TEXT, body TEXT, "
    "UNIQUE(conversation_id, external_id))"
)


def make_uow() -> UnitOfWork:
    conn = sqlite3.connect(":memory:", isolation_level=None)
    conn.execute(SCHEMA)
    return UnitOfWork(conn)


def ids(uow):
    return sorted(r[0] for r in uow.conn.execute("SELECT external_id FROM messages"))


def test_import_skips_duplicates_only():
    uow = make_uow()
    items = [("a", "x"), ("b", "x"), ("a", "dup"), ("c", "x"), ("b", "dup")]
    assert import_messages(uow, 1, items) == (3, 2), "3 rows saved, 2 duplicates skipped"
    assert ids(uow) == ["a", "b", "c"] and not uow.in_transaction
    assert import_messages(uow, 2, [("a", "other conversation")]) == (1, 0), "uniqueness is per conversation"


def test_import_is_one_transaction():
    uow = make_uow()
    with pytest.raises(ValueError):
        import_messages(uow, 1, [("a", "x"), ("b", "x"), ("broken",)])  # unpacking the last item fails
    assert ids(uow) == [], "an unexpected error must roll back the whole import"
    assert not uow.in_transaction and uow.depth == 0


def test_outer_failure_rolls_back_released_savepoints():
    uow = make_uow()
    with pytest.raises(ValueError):
        with uow.begin() as conn:
            with uow.begin_nested():
                conn.execute(INSERT.format("a"))
            raise ValueError("late failure")
    assert ids(uow) == [], "a released savepoint is still undone by the outer rollback"
    assert not uow.in_transaction and uow.depth == 0


def test_begin_twice_raises_and_outer_still_commits():
    uow = make_uow()
    with uow.begin() as conn:
        conn.execute(INSERT.format("a"))
        with pytest.raises(TransactionAlreadyBegun):
            with uow.begin():
                pass
        assert uow.in_transaction, "the failed second begin() must not disturb the active transaction"
    assert ids(uow) == ["a"]


def test_begin_nested_requires_transaction():
    uow = make_uow()
    with pytest.raises(NoActiveTransaction):
        with uow.begin_nested():
            pass
    assert issubclass(NoActiveTransaction, RuntimeError) and issubclass(TransactionAlreadyBegun, RuntimeError)


def test_two_level_nesting_inner_failure_keeps_outer_work():
    uow = make_uow()
    with uow.begin() as conn:
        with uow.begin_nested():
            conn.execute(INSERT.format("outer"))
            try:
                with uow.begin_nested():
                    assert uow.depth == 2
                    conn.execute(INSERT.format("inner"))
                    raise RuntimeError("inner fails")
            except RuntimeError:
                pass
            assert uow.depth == 1
    assert ids(uow) == ["outer"]


def test_requires_autocommit_connection():
    with pytest.raises(ValueError):
        UnitOfWork(sqlite3.connect(":memory:"))


def test_base_exceptions_roll_back_and_state_is_reusable():
    uow = make_uow()
    with pytest.raises(KeyboardInterrupt):
        with uow.begin() as conn:
            conn.execute(INSERT.format("a"))
            with uow.begin_nested():
                conn.execute(INSERT.format("b"))
                raise KeyboardInterrupt
    assert ids(uow) == []
    assert not uow.in_transaction and uow.depth == 0, "state must be reset even after a BaseException"
    with uow.begin() as conn:
        conn.execute(INSERT.format("c"))
    assert ids(uow) == ["c"], "a new transaction can begin afterwards"


def test_statements_issued_use_unique_savepoint_names():
    uow = make_uow()
    log: list[str] = []
    uow.conn.set_trace_callback(log.append)
    with uow.begin():
        with uow.begin_nested():
            pass
        with pytest.raises(RuntimeError):
            with uow.begin_nested():
                raise RuntimeError("x")
    uow.conn.set_trace_callback(None)
    sql = [s.strip().upper() for s in log]
    assert sql[0] == "BEGIN" and sql[-1] == "COMMIT", f"expected BEGIN ... COMMIT, got {sql}"
    names = [m.group(1) for s in sql if (m := re.match(r"SAVEPOINT (\S+)", s))]
    assert len(names) == 2 and len(set(names)) == 2, "each begin_nested() needs its own savepoint name"
    assert any(s.startswith("ROLLBACK TO") for s in sql), "a failing savepoint must ROLLBACK TO"
    assert sum(s.startswith("RELEASE") for s in sql) == 2, "both savepoints are released"


def test_commit_makes_changes_visible_to_other_connections(tmp_path):
    path = str(tmp_path / "uow.db")
    conn = sqlite3.connect(path, isolation_level=None)
    conn.execute(SCHEMA)
    uow = UnitOfWork(conn)
    other = sqlite3.connect(path)
    with uow.begin() as c:
        c.execute(INSERT.format("a"))
        assert other.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 0, "uncommitted rows are invisible"
    assert other.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 1, "COMMIT publishes the rows"
    other.close()
    conn.close()
