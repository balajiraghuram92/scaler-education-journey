import threading

import pytest

from optimistic import ConflictError, VersionedStore, retry


class Boom(Exception):
    pass


def test_retry_delays_use_capped_exponential_full_jitter():
    delays: list[float] = []
    calls: list[int] = []

    def flaky() -> str:
        calls.append(1)
        if len(calls) < 4:
            raise Boom
        return "ok"

    result = retry(
        flaky,
        is_retryable=lambda e: isinstance(e, Boom),
        attempts=5,
        base_delay=0.05,
        max_delay=0.12,
        sleep=delays.append,
        rng=lambda: 1.0,
    )
    assert result == "ok"
    assert delays == [0.05, 0.1, 0.12]  # third delay is capped


def test_retry_does_not_retry_other_errors_or_last_attempt():
    calls: list[int] = []

    def bad() -> None:
        calls.append(1)
        raise ValueError("no")

    with pytest.raises(ValueError):
        retry(bad, is_retryable=lambda e: isinstance(e, Boom), sleep=lambda s: None)
    assert len(calls) == 1

    calls.clear()

    def always_boom() -> None:
        calls.append(1)
        raise Boom

    with pytest.raises(Boom):
        retry(always_boom, is_retryable=lambda e: True, attempts=3, sleep=lambda s: None)
    assert len(calls) == 3


def test_retry_rejects_zero_attempts():
    with pytest.raises(ValueError):
        retry(lambda: 1, is_retryable=lambda e: True, attempts=0)


def test_update_bumps_value_and_version():
    store = VersionedStore({"seats_left": 100})
    assert store.update("seats_left", lambda n: n - 1) == 99
    assert store.read("seats_left") == (99, 2)
    with pytest.raises(KeyError):
        store.read("missing")


def test_compare_and_set_rejects_stale_version():
    store = VersionedStore({"x": 1})
    assert store.compare_and_set("x", 1, 10) is True
    assert store.compare_and_set("x", 1, 20) is False
    assert store.read("x") == (10, 2)


def test_concurrent_increments_lose_no_updates():
    store = VersionedStore({"counter": 0})

    def worker() -> None:
        for _ in range(50):
            store.update("counter", lambda n: n + 1, attempts=10_000, base_delay=0.0001, max_delay=0.001)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert store.read("counter") == (400, 401)


def test_conflict_error_after_attempts_exhausted():
    class AlwaysStale(VersionedStore):
        def compare_and_set(self, key, expected_version, new_value):
            return False

    store = AlwaysStale({"x": 1})
    sleeps: list[float] = []
    with pytest.raises(ConflictError):
        store.update("x", lambda n: n + 1, attempts=3, sleep=sleeps.append, rng=lambda: 1.0)
    assert len(sleeps) == 2


def test_errors_from_fn_are_not_retried():
    store = VersionedStore({"x": 1})
    calls: list[int] = []

    def fn(n: int) -> int:
        calls.append(1)
        raise ValueError("bad input")

    with pytest.raises(ValueError):
        store.update("x", fn, sleep=lambda s: None)
    assert len(calls) == 1
    assert store.read("x") == (1, 1)


def test_retry_returns_immediately_without_sleeping_on_success():
    slept: list[float] = []
    assert retry(lambda: 42, is_retryable=lambda e: True, sleep=slept.append) == 42
    assert slept == [], "no sleep when the first attempt succeeds"


def test_retry_jitter_scales_the_delay_by_rng():
    delays: list[float] = []
    calls: list[int] = []

    def flaky() -> str:
        calls.append(1)
        if len(calls) < 3:
            raise Boom
        return "ok"

    retry(
        flaky,
        is_retryable=lambda e: True,
        base_delay=0.1,
        max_delay=10,
        sleep=delays.append,
        rng=lambda: 0.5,
    )
    assert delays == pytest.approx([0.05, 0.1]), "delay = rng() * min(max_delay, base * 2**(attempt-1))"
