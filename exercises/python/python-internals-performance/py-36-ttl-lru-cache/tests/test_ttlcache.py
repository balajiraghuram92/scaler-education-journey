import pytest

from ttlcache import CacheInfo, ttl_cache


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_hits_and_misses_are_counted() -> None:
    clock = FakeClock()
    calls: list[int] = []

    @ttl_cache(maxsize=4, ttl=10, clock=clock)
    def square(x: int) -> int:
        calls.append(x)
        return x * x

    assert [square(2), square(2), square(3)] == [4, 4, 9]
    assert calls == [2, 3]
    assert square.cache_info() == CacheInfo(hits=1, misses=2, maxsize=4, currsize=2)


def test_entries_expire_after_ttl() -> None:
    clock = FakeClock()
    calls = 0

    @ttl_cache(maxsize=4, ttl=10, clock=clock)
    def fetch(key: str) -> str:
        nonlocal calls
        calls += 1
        return key.upper()

    fetch("a")
    clock.now = 9.9
    fetch("a")
    assert calls == 1
    clock.now = 10.0
    fetch("a")
    assert calls == 2


def test_lru_eviction_keeps_recently_used() -> None:
    clock = FakeClock()
    calls: list[int] = []

    @ttl_cache(maxsize=2, ttl=100, clock=clock)
    def f(x: int) -> int:
        calls.append(x)
        return x

    f(1)
    f(2)
    f(1)  # 2 is now the least recently used
    f(3)                  # evicts 2
    f(1)                  # still cached
    f(2)                  # recomputed
    assert calls == [1, 2, 3, 2]
    assert f.cache_info().currsize == 2


def test_kwargs_form_part_of_the_key_and_unhashable_args_raise() -> None:
    clock = FakeClock()
    calls = 0

    @ttl_cache(clock=clock)
    def g(a: int, b: int = 0) -> int:
        nonlocal calls
        calls += 1
        return a + b

    g(1, b=2)
    g(1, b=2)
    g(1, b=3)
    assert calls == 2
    with pytest.raises(TypeError):
        g([1])  # type: ignore[arg-type]


def test_cache_clear_and_metadata_and_exceptions_not_cached() -> None:
    clock = FakeClock()
    attempts = 0

    @ttl_cache(clock=clock)
    def flaky(x: int) -> int:
        """doc"""
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("boom")
        return x

    assert flaky.__name__ == "flaky" and flaky.__doc__ == "doc"
    with pytest.raises(RuntimeError):
        flaky(1)
    assert flaky(1) == 1 and attempts == 2
    flaky.cache_clear()
    assert flaky.cache_info() == CacheInfo(0, 0, 128, 0)


def test_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        ttl_cache(maxsize=0)
    with pytest.raises(ValueError):
        ttl_cache(ttl=0)


def test_a_hit_does_not_extend_the_ttl_and_expired_entries_leave_currsize() -> None:
    clock = FakeClock()

    @ttl_cache(maxsize=4, ttl=10, clock=clock)
    def f(x: int) -> int:
        return x

    f(1)
    clock.now = 6.0
    f(1)  # hit, but stored_at stays 0
    clock.now = 10.0
    assert f.cache_info().currsize == 1
    f(1)  # expired at exactly ttl seconds after it was stored
    info = f.cache_info()
    assert (info.hits, info.misses) == (1, 2), "the third call must be a miss, the hit must not refresh the entry"
    assert info.currsize == 1, "the stale entry is replaced, not counted twice"


def test_a_slow_call_for_one_key_does_not_block_another_key() -> None:
    import threading

    both_inside = threading.Barrier(2, timeout=5)

    @ttl_cache(maxsize=4, ttl=100)
    def slow(x: int) -> int:
        both_inside.wait()  # only passes if both calls are inside the function at once
        return x

    results: dict[int, int] = {}
    errors: list[BaseException] = []

    def run(x: int) -> None:
        try:
            results[x] = slow(x)
        except BaseException as exc:  # BrokenBarrierError means the function ran under the lock
            errors.append(exc)

    threads = [threading.Thread(target=run, args=(x,)) for x in (1, 2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert not errors, f"the wrapped function must run outside the lock: {errors!r}"
    assert results == {1: 1, 2: 2}


def test_positional_and_keyword_calls_are_distinct_keys_and_clear_resets_counters() -> None:
    clock = FakeClock()
    calls = 0

    @ttl_cache(maxsize=4, ttl=100, clock=clock)
    def h(a: int, b: int = 0) -> int:
        nonlocal calls
        calls += 1
        return a + b

    h(1, 2)
    h(1, b=2)
    h(1, 2)
    assert calls == 2, "h(1, 2) and h(1, b=2) are different keys, as with functools.lru_cache"
    h.cache_clear()
    assert h.cache_info() == CacheInfo(0, 0, 4, 0)
    h(1, 2)
    assert calls == 3
