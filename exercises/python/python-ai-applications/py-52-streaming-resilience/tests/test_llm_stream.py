import asyncio
import inspect
import random
from contextlib import aclosing

import pytest

from llm_retry import ProviderError, RetryPolicy, TransportError
from llm_stream import (
    BudgetExceeded,
    StreamInterrupted,
    TokenBudget,
    metered_stream,
    stream_with_retry,
)


async def nosleep(_s):
    pass


async def collect(agen):
    return [x async for x in agen]


def retrying(open_stream, **kw):
    return stream_with_retry(open_stream, policy=RetryPolicy(**kw), rng=random.Random(0), sleep=nosleep)


def test_retries_when_failure_happens_before_first_token():
    opens = 0

    async def open_stream():
        nonlocal opens
        opens += 1
        if opens == 1:
            raise ProviderError(503)
        yield "a"
        yield "b"

    out = asyncio.run(collect(retrying(open_stream)))
    assert out == ["a", "b"] and opens == 2, "a failure before any token must be retried"


def test_failure_after_first_token_is_not_retried():
    opens = 0

    async def open_stream():
        nonlocal opens
        opens += 1
        yield "Hel"
        yield "lo"
        raise TransportError("reset")

    async def run():
        got = []
        with pytest.raises(StreamInterrupted) as info:
            async for chunk in retrying(open_stream):
                got.append(chunk)
        return got, info.value

    got, exc = asyncio.run(run())
    assert got == ["Hel", "lo"]
    assert exc.partial == "Hello"
    assert isinstance(exc.__cause__, TransportError), "raise StreamInterrupted from the original error"
    assert opens == 1, "no retry once the consumer has seen tokens"


def test_non_retryable_error_is_raised_immediately():
    opens = 0

    async def open_stream():
        nonlocal opens
        opens += 1
        raise ProviderError(400, "context_length_exceeded")
        yield ""  # pragma: no cover

    with pytest.raises(ProviderError) as info:
        asyncio.run(collect(retrying(open_stream)))
    assert info.value.status == 400 and opens == 1


def test_attempt_limit_and_large_retry_after_propagate_the_original_error():
    opens = 0

    async def always_503():
        nonlocal opens
        opens += 1
        raise ProviderError(503)
        yield ""  # pragma: no cover

    with pytest.raises(ProviderError):
        asyncio.run(collect(retrying(always_503, max_attempts=3)))
    assert opens == 3, "stop after max_attempts"

    opens = 0

    async def huge_hint():
        nonlocal opens
        opens += 1
        raise ProviderError(429, retry_after=300.0)
        yield ""  # pragma: no cover

    with pytest.raises(ProviderError):
        asyncio.run(collect(retrying(huge_hint)))
    assert opens == 1, "a Retry-After beyond max_retry_after must not be retried"


def test_consumer_break_closes_the_upstream_stream_immediately():
    closed = False

    async def open_stream():
        nonlocal closed
        try:
            yield "a"
            yield "b"
        finally:
            closed = True

    async def run():
        async with aclosing(retrying(open_stream)) as s:
            async for _chunk in s:
                break
        return closed

    assert asyncio.run(run()) is True, "the upstream finally block must have run"


def test_token_budget_reserve_and_settle():
    budget = TokenBudget(limit=100)
    assert not inspect.iscoroutinefunction(TokenBudget.reserve), "reserve must contain no await"
    budget.reserve(60)
    assert budget.reserved == 60
    with pytest.raises(BudgetExceeded):
        budget.reserve(41)
    assert budget.reserved == 60, "a rejected reservation changes nothing"
    budget.reserve(40)
    budget.settle(60, 25)
    assert (budget.used, budget.reserved) == (25, 40)
    budget.settle(40, 0)
    assert (budget.used, budget.reserved) == (25, 0)


def test_metered_stream_settles_actual_usage_on_early_exit():
    budget = TokenBudget(limit=100)
    closed = False

    async def chunks():
        nonlocal closed
        try:
            for ch in "abcdef":
                yield ch
        finally:
            closed = True

    async def run():
        async with aclosing(metered_stream(budget, 40, chunks())) as s:
            async for chunk in s:
                if chunk == "c":
                    break

    asyncio.run(run())
    assert budget.used == 3 and budget.reserved == 0, "settle the 3 chunks actually produced"
    assert closed, "the upstream must be closed on early exit"


def test_over_budget_stream_is_rejected_before_touching_upstream():
    budget = TokenBudget(limit=10, used=8)
    touched = False

    async def chunks():
        nonlocal touched
        touched = True
        yield "x"

    with pytest.raises(BudgetExceeded):
        asyncio.run(collect(metered_stream(budget, 5, chunks())))
    assert touched is False
    assert (budget.used, budget.reserved) == (8, 0)


def test_metered_stream_settles_when_the_task_is_cancelled():
    budget = TokenBudget(limit=100)

    async def slow_chunks():
        yield "a"
        await asyncio.sleep(10)
        yield "b"

    async def run():
        async def consume():
            async for _ in metered_stream(budget, 30, slow_chunks()):
                pass

        task = asyncio.create_task(consume())
        for _ in range(5):
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert budget.reserved == 0, "a cancelled consumer must still release its reservation"
    assert budget.used == 1


def test_concurrent_consumers_exactly_budget_many_succeed():
    budget = TokenBudget(limit=100)

    async def chunks():
        for _ in range(5):
            await asyncio.sleep(0)
            yield "x"

    async def one():
        try:
            return len(await collect(metered_stream(budget, 10, chunks())))
        except BudgetExceeded:
            return -1

    async def run():
        return await asyncio.gather(*(one() for _ in range(20)))

    results = asyncio.run(run())
    assert results.count(5) == 10 and results.count(-1) == 10, "exactly 10 reservations fit"
    assert budget.used == 50 and budget.reserved == 0
