import logging
import random

import pytest

from errors import BadRequest, GatewayError, RateLimited, UpstreamTimeout
from resilient_call import (
    CircuitBreaker, CircuitOpen, DeadlineExceeded, ResilientCaller, State, full_jitter,
)


class FakeTime:
    """One object plays clock and sleeper, so sleeping advances time."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class Flaky:
    """Callable that raises scripted errors, then succeeds; records keys it received."""

    def __init__(self, *errors: Exception) -> None:
        self.errors = list(errors)
        self.keys: list[str] = []

    def __call__(self, key: str) -> str:
        self.keys.append(key)
        if self.errors:
            raise self.errors.pop(0)
        return "ok"


def make_caller(t: FakeTime, **overrides):
    breaker = CircuitBreaker(clock=t.clock, failure_threshold=3, reset_timeout=10.0)
    params = dict(clock=t.clock, sleep=t.sleep, rng=random.Random(1), breaker=breaker, key_factory=lambda: "key-1")
    params.update(overrides)
    return ResilientCaller(**params)


def test_full_jitter_stays_within_bounds():
    rng = random.Random(0)
    early = [full_jitter(1, 0.5, 20.0, rng) for _ in range(200)]
    assert all(0.0 <= v <= 1.0 for v in early), "attempt 1 with base 0.5 allows at most 1.0"
    late = [full_jitter(6, 0.5, 20.0, rng) for _ in range(500)]
    assert all(0.0 <= v <= 20.0 for v in late), "never above the cap"
    assert max(late) > 15.0, "values should spread over the whole window"


def test_retries_transient_errors_and_reuses_idempotency_key():
    t = FakeTime()
    fn = Flaky(UpstreamTimeout("t"), UpstreamTimeout("t"))
    assert make_caller(t).call(fn) == "ok"
    assert fn.keys == ["key-1", "key-1", "key-1"], "the same key must be sent on every attempt"
    assert len(t.sleeps) == 2


def test_non_retryable_error_is_raised_immediately():
    t = FakeTime()
    fn = Flaky(BadRequest("bad", status=400))
    with pytest.raises(BadRequest):
        make_caller(t).call(fn)
    assert len(fn.keys) == 1
    assert t.sleeps == []


def test_retry_after_is_a_floor_for_the_delay():
    t = FakeTime()
    fn = Flaky(RateLimited("slow down", retry_after=5.0))
    make_caller(t).call(fn)
    assert t.sleeps[0] >= 5.0, "must wait at least Retry-After"


def test_gives_up_after_max_attempts_and_reraises_last_error():
    t = FakeTime()
    fn = Flaky(*[UpstreamTimeout("t")] * 4)
    caller = make_caller(t, max_attempts=4, breaker=CircuitBreaker(clock=t.clock, failure_threshold=99))
    with pytest.raises(UpstreamTimeout):
        caller.call(fn)
    assert len(fn.keys) == 4
    assert len(t.sleeps) == 3, "no sleep after the final attempt"


def test_deadline_stops_retrying_without_sleeping():
    t = FakeTime()
    fn = Flaky(RateLimited("slow", retry_after=60.0))
    with pytest.raises(DeadlineExceeded) as excinfo:
        make_caller(t, deadline=30.0).call(fn)
    assert isinstance(excinfo.value.__cause__, RateLimited), "DeadlineExceeded must chain the last error"
    assert t.sleeps == [], "never sleep past the budget"
    assert len(fn.keys) == 1


def test_breaker_opens_then_fails_fast_then_recovers():
    t = FakeTime()
    breaker = CircuitBreaker(clock=t.clock, failure_threshold=2, reset_timeout=10.0)
    caller = make_caller(t, breaker=breaker, max_attempts=2)
    with pytest.raises(UpstreamTimeout):
        caller.call(Flaky(UpstreamTimeout("t"), UpstreamTimeout("t")))
    assert breaker.state is State.OPEN

    probe = Flaky()
    with pytest.raises(CircuitOpen):
        caller.call(probe)
    assert probe.keys == [], "the dependency must not be touched while open"
    assert isinstance(CircuitOpen("x"), GatewayError)

    t.now += 11.0
    assert caller.call(probe) == "ok"
    assert breaker.state is State.CLOSED


def test_breaker_half_open_failure_reopens_and_success_resets_count():
    t = FakeTime()
    breaker = CircuitBreaker(clock=t.clock, failure_threshold=2, reset_timeout=10.0)
    breaker.record_failure()
    breaker.record_success()
    breaker.record_failure()
    assert breaker.state is State.CLOSED, "a success must reset the failure count"
    breaker.record_failure()
    assert breaker.state is State.OPEN
    with pytest.raises(CircuitOpen):
        breaker.before_call()
    t.now += 10.0
    breaker.before_call()
    assert breaker.state is State.HALF_OPEN, "after the cool-down one probe is allowed"
    breaker.record_failure()
    assert breaker.state is State.OPEN, "a failed probe re-opens immediately"
    with pytest.raises(CircuitOpen):
        breaker.before_call()


def test_each_retry_is_logged_at_warning_with_attempt_and_delay(caplog):
    t = FakeTime()
    fn = Flaky(UpstreamTimeout("t"), UpstreamTimeout("t"))
    with caplog.at_level(logging.WARNING, logger="gateway.resilience"):
        make_caller(t).call(fn)
    records = [r for r in caplog.records if r.name == "gateway.resilience"]
    assert [r.levelno for r in records] == [logging.WARNING, logging.WARNING]
    assert [r.attempt for r in records] == [1, 2]
    assert all(isinstance(r.delay, float) and r.delay >= 0 for r in records)


def test_default_key_factory_is_unique_per_call_but_stable_within_one():
    t = FakeTime()
    caller = ResilientCaller(clock=t.clock, sleep=t.sleep, rng=random.Random(2), breaker=CircuitBreaker(clock=t.clock))
    first = Flaky(UpstreamTimeout("t"))
    second = Flaky()
    caller.call(first)
    caller.call(second)
    assert len(set(first.keys)) == 1 and len(first.keys) == 2
    assert first.keys[0] != second.keys[0], "a new idempotency key per logical call"
