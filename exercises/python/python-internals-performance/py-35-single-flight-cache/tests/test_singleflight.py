import threading
import time

from singleflight import SingleFlightCache


def run_threads(n: int, target) -> None:
    threads = [threading.Thread(target=target) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert not any(t.is_alive() for t in threads)


def test_same_key_computed_once_under_contention() -> None:
    calls: list[str] = []

    def compute(key: str) -> int:
        calls.append(key)
        time.sleep(0.05)  # widen the race window
        return len(key)

    cache = SingleFlightCache(compute)
    barrier = threading.Barrier(8)
    results: list[int] = []

    def worker() -> None:
        barrier.wait()
        results.append(cache.get("abc"))

    run_threads(8, worker)
    assert results == [3] * 8
    assert calls == ["abc"]
    assert cache.get("abc") == 3 and calls == ["abc"]


def test_different_keys_compute_concurrently() -> None:
    both_inside = threading.Barrier(2, timeout=5)

    def compute(key: str) -> str:
        both_inside.wait()  # only passes if both computations overlap
        return key.upper()

    cache = SingleFlightCache(compute)
    out: dict[str, str] = {}

    def make(k: str):
        return lambda: out.__setitem__(k, cache.get(k))

    threads = [threading.Thread(target=make(k)) for k in ("a", "b")]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert out == {"a": "A", "b": "B"}


def test_exception_reaches_all_waiters_and_is_not_cached() -> None:
    attempts = 0
    gate = threading.Event()

    def compute(key: str) -> int:
        nonlocal attempts
        attempts += 1
        gate.wait(timeout=5)
        if attempts == 1:
            raise RuntimeError("upstream down")
        return 7

    cache = SingleFlightCache(compute)
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            cache.get("k")
        except RuntimeError as exc:
            errors.append(exc)

    start = threading.Barrier(5)

    def synced_worker() -> None:
        start.wait(timeout=5)
        worker()

    threads = [threading.Thread(target=synced_worker) for _ in range(4)]
    for t in threads:
        t.start()
    start.wait(timeout=5)
    time.sleep(0.1)  # let all four callers reach get() while the leader is blocked
    gate.set()
    for t in threads:
        t.join(timeout=10)
    assert len(errors) == 4 and attempts == 1
    assert cache.get("k") == 7  # a later call retries
    assert attempts == 2


def test_invalidate_forces_recompute() -> None:
    n = 0

    def compute(key: int) -> int:
        nonlocal n
        n += 1
        return key * 2

    cache = SingleFlightCache(compute)
    assert cache.get(2) == 4 and cache.get(2) == 4 and n == 1
    cache.invalidate(2)
    assert cache.get(2) == 4 and n == 2
    assert len(cache) == 1


def test_failure_is_not_cached_and_retry_succeeds_sequentially() -> None:
    attempts = 0

    def compute(key: str) -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ValueError("boom")
        return key * 2

    cache = SingleFlightCache(compute)
    try:
        cache.get("ab")
    except ValueError:
        pass
    else:
        raise AssertionError("the first call should have raised ValueError")
    assert len(cache) == 0, "a failed computation must not be cached"
    assert cache.get("ab") == "abab"
    assert attempts == 2


def test_len_counts_cached_keys_and_invalidate_of_unknown_key_is_harmless() -> None:
    cache = SingleFlightCache(lambda key: key + 1)
    cache.invalidate(99)  # must not raise
    assert len(cache) == 0
    assert (cache.get(1), cache.get(2)) == (2, 3)
    assert len(cache) == 2
    cache.invalidate(1)
    assert len(cache) == 1
