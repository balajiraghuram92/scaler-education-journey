import asyncio

import pytest

from fanout import fan_out


async def job(value: int, delay: float = 0.0) -> int:
    await asyncio.sleep(delay)
    return value


@pytest.mark.asyncio
async def test_results_keep_input_order():
    results = await fan_out(
        [lambda: job(1, 0.03), lambda: job(2, 0.0), lambda: job(3, 0.01)],
        timeout=1,
    )
    assert results == [1, 2, 3], "results must follow input order, not completion order"


@pytest.mark.asyncio
async def test_empty_input():
    assert await fan_out([], timeout=1) == [], "an empty sequence must return []"


@pytest.mark.asyncio
async def test_calls_run_concurrently():
    first_started, second_started = asyncio.Event(), asyncio.Event()

    async def first() -> str:
        first_started.set()
        await second_started.wait()  # only finishes if the sibling is running at the same time
        return "first"

    async def second() -> str:
        second_started.set()
        await first_started.wait()
        return "second"

    results = await fan_out([first, second], timeout=1)
    assert results == ["first", "second"], "calls must run concurrently, not one after another"


@pytest.mark.asyncio
async def test_each_factory_is_called_exactly_once():
    calls: list[int] = []

    def make(n: int):
        def factory():
            calls.append(n)
            return job(n)

        return factory

    results = await fan_out([make(1), make(2), make(3)], timeout=1)
    assert results == [1, 2, 3]
    assert sorted(calls) == [1, 2, 3], "each factory must be called exactly once"


@pytest.mark.asyncio
async def test_failure_cancels_siblings_and_raises_group():
    cleaned: list[str] = []

    async def slow() -> str:
        try:
            await asyncio.sleep(5)
            return "never"
        finally:
            cleaned.append("slow")

    async def boom() -> str:
        await asyncio.sleep(0.01)
        raise ValueError("bad")

    with pytest.raises(ExceptionGroup) as info:
        await fan_out([slow, boom], timeout=1)

    assert cleaned == ["slow"], "the sibling's finally block must have run before fan_out returned"
    assert [type(e) for e in info.value.exceptions] == [ValueError], "do not unwrap the ExceptionGroup"


@pytest.mark.asyncio
async def test_multiple_failures_are_all_reported():
    async def boom(msg: str) -> None:
        await asyncio.sleep(0)
        raise ValueError(msg)

    with pytest.raises(ExceptionGroup) as info:
        await fan_out([lambda: boom("a"), lambda: boom("b")], timeout=1)

    assert sorted(str(e) for e in info.value.exceptions) == ["a", "b"], "both failures must be in the group"


@pytest.mark.asyncio
async def test_timeout_cancels_everything():
    cleaned: list[int] = []

    async def hang(n: int) -> int:
        try:
            await asyncio.sleep(5)
            return n
        finally:
            cleaned.append(n)

    with pytest.raises(TimeoutError):
        await fan_out([lambda: hang(1), lambda: hang(2)], timeout=0.05)

    assert sorted(cleaned) == [1, 2], "every call must be cancelled and cleaned up when the deadline passes"


@pytest.mark.asyncio
async def test_does_not_use_gather(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("asyncio.gather must not be used; use asyncio.TaskGroup")

    monkeypatch.setattr(asyncio, "gather", forbidden)
    assert await fan_out([lambda: job(1), lambda: job(2)], timeout=1) == [1, 2]
