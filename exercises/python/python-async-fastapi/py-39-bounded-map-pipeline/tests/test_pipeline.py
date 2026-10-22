import asyncio

import pytest

from pipeline import bounded_map


@pytest.mark.asyncio
async def test_results_keep_input_order():
    async def double(x: int) -> int:
        await asyncio.sleep(0.01 if x % 2 else 0)  # odd items finish later
        return x * 2

    assert await bounded_map(double, range(10), workers=3) == [x * 2 for x in range(10)]


@pytest.mark.asyncio
async def test_empty_input_returns_empty_list():
    async def ident(x: int) -> int:
        return x

    assert await bounded_map(ident, [], workers=3) == []
    assert await bounded_map(ident, iter(()), workers=1, queue_size=1) == []


@pytest.mark.asyncio
async def test_concurrency_equals_workers():
    state = {"now": 0, "peak": 0}

    async def job(_: int) -> None:
        state["now"] += 1
        state["peak"] = max(state["peak"], state["now"])
        await asyncio.sleep(0.005)
        state["now"] -= 1

    await bounded_map(job, range(40), workers=4)
    assert state["peak"] == 4, "exactly `workers` calls should run at once with plenty of items"


@pytest.mark.asyncio
async def test_fewer_items_than_workers():
    async def ident(x: int) -> int:
        await asyncio.sleep(0.001)
        return x

    assert await bounded_map(ident, [7, 8], workers=10) == [7, 8]


@pytest.mark.asyncio
async def test_accepts_a_generator():
    async def ident(x: int) -> int:
        return x

    assert await bounded_map(ident, (i for i in range(25)), workers=4, queue_size=2) == list(range(25))


@pytest.mark.asyncio
async def test_items_are_pulled_lazily():
    pulled = 0

    def source():
        nonlocal pulled
        for i in range(10_000):
            pulled += 1
            yield i

    gate = asyncio.Event()

    async def blocked(_: int) -> None:
        await gate.wait()

    task = asyncio.create_task(bounded_map(blocked, source(), workers=2, queue_size=3))
    await asyncio.sleep(0.05)  # workers are stuck, so the producer must be blocked in put()
    seen = pulled
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert 2 <= seen <= 2 + 3 + 1, f"pulled {seen} items; at most workers + queue_size + 1 may be pulled ahead"


@pytest.mark.asyncio
async def test_failure_cancels_workers_and_does_not_deadlock():
    cleaned: list[int] = []

    async def job(x: int) -> int:
        try:
            if x == 0:
                await asyncio.sleep(0.02)  # let the other worker start item 1 first
                raise RuntimeError("boom")
            await asyncio.sleep(5)
            return x
        finally:
            cleaned.append(x)

    with pytest.raises(ExceptionGroup) as info:
        async with asyncio.timeout(2):  # a deadlock would surface as TimeoutError instead
            await bounded_map(job, range(100), workers=2, queue_size=1)

    assert [type(e) for e in info.value.exceptions] == [RuntimeError]
    assert 0 in cleaned
    assert 1 in cleaned, "the other worker must be cancelled and run its finally block"


@pytest.mark.asyncio
async def test_workers_must_be_positive():
    async def ident(x: int) -> int:
        return x

    for bad in (0, -1):
        with pytest.raises(ValueError):
            await bounded_map(ident, [1], workers=bad)


@pytest.mark.asyncio
async def test_queue_size_must_be_positive():
    async def ident(x: int) -> int:
        return x

    for bad in (0, -3):
        with pytest.raises(ValueError):
            await bounded_map(ident, [1], workers=1, queue_size=bad)
