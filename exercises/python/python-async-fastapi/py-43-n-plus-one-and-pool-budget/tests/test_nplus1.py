import sqlite3

import pytest

from nplus1 import Budget, QueryCounter, connection_budget, largest_pool_size, load_batched, load_naive


def make_db(parents: int, per_parent: int = 2) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE conversations (id INTEGER PRIMARY KEY, user_id TEXT);
        CREATE TABLE messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, body TEXT);
        """
    )
    conn.executemany("INSERT INTO conversations(id, user_id) VALUES (?, 'u1')", [(i,) for i in range(1, parents + 1)])
    conn.executemany(
        "INSERT INTO messages(conversation_id, body) VALUES (?, ?)",
        [(c, f"{c}-{k}") for c in range(1, parents + 1) for k in range(per_parent)],
    )
    conn.execute("INSERT INTO conversations(id, user_id) VALUES (?, 'u2')", (parents + 1,))
    conn.commit()
    return conn


def test_naive_is_n_plus_one():
    conn = make_db(50)
    with QueryCounter(conn) as qc:
        data = load_naive(conn, "u1")
    assert qc.count == 51, f"expected 1 + 50 SELECTs, counted {qc.count}"
    assert len(data) == 50 and data[1] == ["1-0", "1-1"]


def test_batched_matches_naive_with_two_queries():
    conn = make_db(50)
    with QueryCounter(conn) as qc:
        batched = load_batched(conn, "u1")
    assert qc.count == 2, f"expected 1 + 1 SELECTs, counted {qc.count}"
    assert batched == load_naive(conn, "u1")
    assert all(s.lstrip().upper().startswith("SELECT") for s in qc.statements)
    assert " IN " in qc.statements[1].upper(), "the second query must use IN (...)"


def test_chunking_is_ceil_division():
    conn = make_db(1200, per_parent=1)
    with QueryCounter(conn) as qc:
        load_batched(conn, "u1", chunk_size=500)
    assert qc.count == 1 + 3, "1200 ids in chunks of 500 need 3 IN queries"
    with QueryCounter(conn) as qc:
        load_batched(conn, "u1", chunk_size=1200)
    assert qc.count == 2
    with QueryCounter(conn) as qc:
        load_batched(conn, "u1", chunk_size=1)
    assert qc.count == 1 + 1200


def test_parents_without_children_and_no_parents():
    conn = make_db(3)
    conn.execute("DELETE FROM messages WHERE conversation_id = 2")
    assert load_batched(conn, "u1")[2] == [], "a conversation without messages maps to []"
    assert load_naive(conn, "u1")[2] == []
    with QueryCounter(conn) as qc:
        assert load_batched(conn, "nobody") == {}
    assert qc.count == 1, "with no conversations only the parent query runs"


def test_results_are_ordered_by_id_and_scoped_to_user():
    conn = make_db(2, per_parent=0)
    conn.executemany(
        "INSERT INTO messages(id, conversation_id, body) VALUES (?, ?, ?)",
        [(30, 1, "third"), (10, 1, "first"), (20, 1, "second"), (5, 2, "other")],
    )
    conn.execute("INSERT INTO conversations(id, user_id) VALUES (99, 'u2')")
    conn.execute("INSERT INTO messages(id, conversation_id, body) VALUES (1, 99, 'not-mine')")
    for loader in (load_naive, load_batched):
        data = loader(conn, "u1")
        assert data == {1: ["first", "second", "third"], 2: ["other"]}, f"{loader.__name__}: ordered by id, only u1's rows"
    assert list(load_batched(conn, "u1")) == [1, 2], "conversations are ordered by id"


def test_chunk_size_must_be_positive():
    conn = make_db(2)
    for bad in (0, -1):
        with pytest.raises(ValueError):
            load_batched(conn, "u1", chunk_size=bad)


def test_counter_only_counts_selects_and_detaches():
    conn = make_db(2)
    with QueryCounter(conn) as qc:
        conn.execute("SELECT 1")
        conn.execute("select 2")
        conn.execute("INSERT INTO conversations(id, user_id) VALUES (500, 'x')")
        conn.execute("UPDATE conversations SET user_id = 'y' WHERE id = 500")
    conn.execute("SELECT 3")
    assert qc.count == 2, "only SELECT statements (any case) are counted, and only inside the block"
    assert len(qc.statements) == 2


def test_counter_detaches_even_when_the_block_raises():
    conn = make_db(1)
    qc = QueryCounter(conn)
    with pytest.raises(RuntimeError):
        with qc:
            conn.execute("SELECT 1")
            raise RuntimeError("boom")
    conn.execute("SELECT 2")
    assert qc.count == 1, "the trace callback must be removed on exit even after an exception"


def test_connection_budget():
    b = connection_budget(2, 3, 10, 5, 100, 20)
    assert isinstance(b, Budget)
    assert (b.worst_case, b.available, b.fits) == (90, 80, False)
    assert connection_budget(2, 3, 9, 4, 100, 20).fits, "78 <= 80 fits"
    assert connection_budget(1, 1, 10, 10, 20, 0).fits, "exactly equal fits"
    with pytest.raises(Exception):
        connection_budget(1, 1, 1, 1, 10, 0).worst_case = 1  # frozen dataclass


def test_largest_pool_size():
    assert largest_pool_size(2, 3, 100, 20) == 9, "9 + int(9 * 0.5) = 13 per worker; 6 workers = 78 <= 80"
    assert largest_pool_size(100, 100, 100, 20) == 0, "even a pool of one does not fit"
    assert largest_pool_size(1, 1, 10, 0, overflow_ratio=0) == 10
    assert largest_pool_size(1, 1, 10, 0, overflow_ratio=1.0) == 5
    best = largest_pool_size(3, 4, 200, 20)
    assert connection_budget(3, 4, best, int(best * 0.5), 200, 20).fits
    assert not connection_budget(3, 4, best + 1, int((best + 1) * 0.5), 200, 20).fits, "it must be the largest"
