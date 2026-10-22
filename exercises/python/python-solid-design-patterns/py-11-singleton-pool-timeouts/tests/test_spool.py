import threading

import pytest

from spool import Connection, ConnectionPool, PoolTimeout, get_pool, reset_pool


@pytest.fixture(autouse=True)
def clean():
    try:
        reset_pool()
    except NotImplementedError:
        pass
    yield
    try:
        reset_pool()
    except NotImplementedError:
        pass


def setup_pool(size: int = 3):
    reset_pool()
    return get_pool(size)


def test_get_pool_is_a_singleton_across_threads():
    reset_pool()
    barrier = threading.Barrier(10)
    seen = []

    def worker():
        barrier.wait(timeout=5)
        seen.append(get_pool(3))

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert len(seen) == 10
    assert len({id(p) for p in seen}) == 1, "ten simultaneous first calls must create one pool"


def test_default_size_and_reset():
    first = get_pool()
    assert first.size == 10, "default size is 10"
    assert get_pool() is first
    reset_pool()
    assert get_pool(2) is not first


def test_conflicting_size_is_rejected_not_ignored():
    setup_pool(3)
    with pytest.raises(ValueError):
        get_pool(5)
    assert get_pool().size == 3
    assert get_pool(3).size == 3, "asking for the same size is fine"


def test_invalid_size_and_connection_identity():
    with pytest.raises(ValueError):
        ConnectionPool(0)
    pool = ConnectionPool(2)
    a, b = pool.acquire(), pool.acquire()
    assert isinstance(a, Connection) and a is not b and a != b, "connections compare by identity"
    assert a.id != b.id


def test_acquire_and_release_update_available():
    pool = setup_pool(3)
    conn = pool.acquire()
    assert pool.available == 2
    pool.release(conn)
    assert pool.available == 3


def test_exhausted_pool_times_out():
    pool = setup_pool(1)
    pool.acquire()
    with pytest.raises(PoolTimeout):
        pool.acquire(timeout=0.05)


def test_context_manager_releases_even_on_error():
    pool = setup_pool(2)
    with pytest.raises(RuntimeError):
        with pool.connection() as conn:
            assert isinstance(conn, Connection)
            assert pool.available == 1
            raise RuntimeError("query failed")
    assert pool.available == 2, "the connection must be returned when the body raises"


def test_double_release_is_rejected():
    pool = setup_pool(2)
    conn = pool.acquire()
    pool.release(conn)
    with pytest.raises(ValueError):
        pool.release(conn)
    assert pool.available == 2, "a rejected release must not grow the pool"


def test_blocked_acquire_wakes_up_after_release():
    pool = setup_pool(1)
    held = pool.acquire()
    got = []
    ready = threading.Event()

    def waiter():
        ready.set()
        got.append(pool.acquire(timeout=5))

    t = threading.Thread(target=waiter, daemon=True)
    t.start()
    assert ready.wait(timeout=2)
    t.join(timeout=0.1)
    assert got == [], "the waiter must stay blocked while the pool is empty"
    pool.release(held)
    t.join(timeout=3)
    assert len(got) == 1 and got[0] is held, "the waiter should receive the released connection"
