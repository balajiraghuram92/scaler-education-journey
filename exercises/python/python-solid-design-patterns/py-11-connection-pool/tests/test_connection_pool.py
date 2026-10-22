import threading

import pytest

from pool.connection_pool_impl import ConnectionPoolImpl
from pool.database_connection import DatabaseConnection


@pytest.fixture(autouse=True)
def fresh_singleton():
    try:
        ConnectionPoolImpl.reset_instance()
    except NotImplementedError:
        pass
    yield
    try:
        ConnectionPoolImpl.reset_instance()
    except NotImplementedError:
        pass


def test_get_instance_returns_the_same_pool():
    pool = ConnectionPoolImpl.get_instance(3)
    assert ConnectionPoolImpl.get_instance(3) is pool, "get_instance must return the shared pool"
    assert isinstance(pool, ConnectionPoolImpl)


def test_same_instance_across_threads():
    n = 8
    barrier = threading.Barrier(n)
    seen = []

    def worker():
        barrier.wait(timeout=5)
        seen.append(ConnectionPoolImpl.get_instance(4))

    threads = [threading.Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert len(seen) == n
    assert len({id(p) for p in seen}) == 1, "concurrent first calls must still create exactly one pool"


def test_reset_instance_allows_a_new_pool():
    first = ConnectionPoolImpl.get_instance(2)
    ConnectionPoolImpl.reset_instance()
    second = ConnectionPoolImpl.get_instance(5)
    assert second is not first
    assert second.get_total_connections_count() == 5, "the new pool uses the new size"


def test_pool_starts_full_with_distinct_connections():
    pool = ConnectionPoolImpl.get_instance(4)
    assert pool.get_total_connections_count() == 4
    assert pool.get_available_connections_count() == 4
    conns = [pool.get_connection() for _ in range(4)]
    assert all(isinstance(c, DatabaseConnection) for c in conns)
    assert len({id(c) for c in conns}) == 4, "each borrowed connection must be a distinct object"


def test_borrow_and_release_update_available_count():
    pool = ConnectionPoolImpl.get_instance(3)
    conn = pool.get_connection()
    assert pool.get_available_connections_count() == 2, "borrowing marks a connection unavailable"
    assert pool.get_total_connections_count() == 3, "total size never changes"
    pool.release_connection(conn)
    assert pool.get_available_connections_count() == 3


def test_release_none_is_ignored():
    pool = ConnectionPoolImpl.get_instance(2)
    pool.release_connection(None)
    assert pool.get_available_connections_count() == 2, "releasing None must not add a connection"


def test_get_connection_blocks_until_one_is_released():
    pool = ConnectionPoolImpl.get_instance(1)
    held = pool.get_connection()
    got = []
    started = threading.Event()

    def borrower():
        started.set()
        got.append(pool.get_connection())

    t = threading.Thread(target=borrower, daemon=True)
    t.start()
    assert started.wait(timeout=2)
    t.join(timeout=0.15)
    assert t.is_alive() and got == [], "an exhausted pool must block the caller"
    pool.release_connection(held)
    t.join(timeout=3)
    assert not t.is_alive(), "the blocked caller must wake up when a connection is released"
    assert len(got) == 1 and got[0] is held, "the waiting caller should receive the released connection"


def test_many_threads_never_exceed_pool_size():
    pool = ConnectionPoolImpl.get_instance(3)
    lock = threading.Lock()
    in_use = 0
    peak = 0

    def worker():
        nonlocal in_use, peak
        conn = pool.get_connection()
        with lock:
            in_use += 1
            peak = max(peak, in_use)
        threading.Event().wait(0.01)
        with lock:
            in_use -= 1
        pool.release_connection(conn)

    threads = [threading.Thread(target=worker) for _ in range(12)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert not any(t.is_alive() for t in threads), "all workers should complete"
    assert peak <= 3, f"never more than 3 connections may be lent out at once, saw {peak}"
    assert pool.get_available_connections_count() == 3
