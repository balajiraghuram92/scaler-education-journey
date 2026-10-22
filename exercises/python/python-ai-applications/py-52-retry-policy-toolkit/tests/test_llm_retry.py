import asyncio
import dataclasses
import random
from datetime import datetime, timezone

import pytest

from llm_retry import (
    ProviderError,
    RetryPolicy,
    TransportError,
    is_retryable,
    parse_retry_after,
    retry_async,
)


def run(coro):
    return asyncio.run(coro)


def test_parse_retry_after_seconds_date_and_garbage():
    now = datetime(2026, 10, 21, 7, 28, 0, tzinfo=timezone.utc)
    assert parse_retry_after("3") == 3.0
    assert parse_retry_after("1.5") == 1.5
    assert parse_retry_after("-5") == 0.0, "negative values clamp to 0"
    assert parse_retry_after(None) is None
    for junk in ("nan", "inf", "-inf", "soon", ""):
        assert parse_retry_after(junk) is None, f"{junk!r} should be unparseable"
    assert parse_retry_after("Wed, 21 Oct 2026 07:28:10 GMT", now=now) == 10.0
    assert parse_retry_after("Wed, 21 Oct 2026 07:27:00 GMT", now=now) == 0.0, "past dates clamp to 0"


def test_provider_error_and_policy_defaults():
    err = ProviderError(429, "rate_limited", 2.5)
    assert (err.status, err.code, err.retry_after) == (429, "rate_limited", 2.5)
    plain = ProviderError(503)
    assert plain.code is None and plain.retry_after is None
    assert str(plain) == "HTTP 503"
    assert isinstance(TransportError("x"), Exception)
    policy = RetryPolicy()
    assert (policy.max_attempts, policy.base_delay, policy.max_delay, policy.max_retry_after) == (4, 0.5, 20.0, 30.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        policy.max_attempts = 9


def test_delay_stays_inside_full_jitter_window():
    policy = RetryPolicy(base_delay=0.5, max_delay=4.0)
    rng = random.Random(1)
    for attempt in range(8):
        window = min(4.0, 0.5 * 2**attempt)
        values = [policy.delay(attempt, None, rng) for _ in range(200)]
        assert all(0.0 <= v <= window for v in values), f"attempt {attempt} must stay within [0, {window}]"
    wide = [policy.delay(3, None, random.Random(i)) for i in range(200)]
    assert max(wide) > 2.0, "jitter should use the whole window, not a fixed value"


def test_retry_after_is_a_floor_not_a_replacement():
    policy = RetryPolicy(base_delay=0.5)
    rng = random.Random(1)
    assert all(policy.delay(0, 2.0, rng) == 2.0 for _ in range(50))
    big = policy.delay(10, 1.0, rng)
    assert 1.0 <= big <= 20.0


@pytest.mark.parametrize(
    "exc, expected",
    [
        pytest.param(lambda: TransportError("reset"), True, id="transport"),
        pytest.param(lambda: ProviderError(429), True, id="429"),
        pytest.param(lambda: ProviderError(429, "insufficient_quota"), False, id="429-quota"),
        pytest.param(lambda: ProviderError(429, "billing_hard_limit_reached"), False, id="429-billing"),
        pytest.param(lambda: ProviderError(500), True, id="500"),
        pytest.param(lambda: ProviderError(502), True, id="502"),
        pytest.param(lambda: ProviderError(503), True, id="503"),
        pytest.param(lambda: ProviderError(504), True, id="504"),
        pytest.param(lambda: ProviderError(501), False, id="501"),
        pytest.param(lambda: ProviderError(400, "context_length_exceeded"), False, id="400"),
        pytest.param(lambda: ProviderError(401), False, id="401"),
        pytest.param(lambda: ValueError("bug"), False, id="value-error"),
    ],
)
def test_is_retryable(exc, expected):
    assert is_retryable(exc()) is expected


def test_retries_transient_then_succeeds_and_sleeps_with_hint():
    attempts = []
    sleeps = []

    async def op():
        attempts.append(1)
        if len(attempts) == 1:
            raise ProviderError(429, retry_after=2.0)
        if len(attempts) == 2:
            raise TransportError("reset")
        return "ok"

    async def fake_sleep(s):
        sleeps.append(s)

    result = run(retry_async(op, policy=RetryPolicy(), rng=random.Random(0), sleep=fake_sleep))
    assert result == "ok"
    assert len(attempts) == 3
    assert sleeps[0] == 2.0, "the first wait honours Retry-After"
    assert 0.0 <= sleeps[1] <= 1.0, "second wait is full jitter for attempt 1 (window 1.0)"


def test_quota_error_fails_after_one_attempt():
    calls = 0

    async def op():
        nonlocal calls
        calls += 1
        raise ProviderError(429, "insufficient_quota")

    with pytest.raises(ProviderError):
        run(retry_async(op, policy=RetryPolicy(), rng=random.Random(0)))
    assert calls == 1


def test_huge_retry_after_fails_fast_without_sleeping():
    async def op():
        raise ProviderError(429, retry_after=120.0)

    async def boom(_s):
        raise AssertionError("must not sleep")

    with pytest.raises(ProviderError):
        run(retry_async(op, policy=RetryPolicy(max_retry_after=30.0), rng=random.Random(0), sleep=boom))


def test_exhausts_attempts_and_reraises_last_error():
    calls = 0
    sleeps = []

    async def op():
        nonlocal calls
        calls += 1
        raise ProviderError(503)

    async def nosleep(s):
        sleeps.append(s)

    with pytest.raises(ProviderError) as info:
        run(retry_async(op, policy=RetryPolicy(max_attempts=3), rng=random.Random(0), sleep=nosleep))
    assert info.value.status == 503 and calls == 3
    assert len(sleeps) == 2, "no sleep after the final attempt"


def test_cancellation_is_not_swallowed():
    calls = 0

    async def op():
        nonlocal calls
        calls += 1
        await asyncio.sleep(5)

    async def main():
        async with asyncio.timeout(0.05):
            await retry_async(op, policy=RetryPolicy(), rng=random.Random(0))

    with pytest.raises(TimeoutError):
        run(main())
    assert calls == 1, "an outer timeout must not trigger a retry"
