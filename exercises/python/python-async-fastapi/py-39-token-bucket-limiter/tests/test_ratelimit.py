import asyncio

import pytest

from ratelimit import TokenBucket


class FakeTime:
    def __init__(self) -> None:
        self.now = 100.0
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.now

    async def sleep(self, delay: float) -> None:
        self.sleeps.append(delay)
        self.now += delay
        await asyncio.sleep(0)  # still yield to the loop


def make(rate: float, burst: int) -> tuple[TokenBucket, FakeTime]:
    ft = FakeTime()
    return TokenBucket(rate, burst, clock=ft.clock, sleep=ft.sleep), ft


@pytest.mark.asyncio
async def test_burst_is_free_then_throttled():
    bucket, ft = make(rate=10, burst=2)
    for _ in range(2):
        await bucket.acquire()
    assert ft.sleeps == [], "the first `burst` acquisitions must not wait"
    await bucket.acquire()
    assert len(ft.sleeps) == 1, "the third acquisition must wait once"
    assert abs(ft.sleeps[0] - 0.1) < 1e-9, "wait should be (cost - tokens) / rate = 0.1 s"


@pytest.mark.asyncio
async def test_partial_refill_shortens_the_wait():
    bucket, ft = make(rate=10, burst=1)
    await bucket.acquire()
    ft.now += 0.04  # 0.4 tokens refilled
    await bucket.acquire()
    assert len(ft.sleeps) == 1
    assert abs(ft.sleeps[0] - 0.06) < 1e-9, "only the missing 0.6 tokens (0.06 s) should be waited for"


@pytest.mark.asyncio
async def test_refill_is_capped_at_burst():
    bucket, ft = make(rate=10, burst=2)
    ft.now += 1000  # a long idle period must not bank 10,000 tokens
    for _ in range(2):
        await bucket.acquire()
    assert ft.sleeps == [], "the capped burst is still free"
    await bucket.acquire()
    assert len(ft.sleeps) == 1, "the third call must wait because tokens were capped at burst"


@pytest.mark.asyncio
async def test_waiters_are_served_in_arrival_order():
    bucket, _ = make(rate=10, burst=1)
    await bucket.acquire()  # drain the bucket
    order: list[int] = []

    async def caller(i: int) -> None:
        await bucket.acquire()
        order.append(i)

    async with asyncio.TaskGroup() as tg:
        for i in range(5):
            tg.create_task(caller(i))
    assert order == [0, 1, 2, 3, 4], "waiters must be served first come, first served"


@pytest.mark.asyncio
async def test_large_request_is_not_overtaken_by_small_ones():
    bucket, _ = make(rate=10, burst=3)
    await bucket.acquire(3)  # drain
    order: list[str] = []

    async def caller(name: str, cost: float) -> None:
        await bucket.acquire(cost)
        order.append(name)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(caller("big", 3))
        tg.create_task(caller("small1", 1))
        tg.create_task(caller("small2", 1))
    assert order == ["big", "small1", "small2"], "a large request must not be starved by later small ones"


@pytest.mark.asyncio
async def test_total_time_matches_rate():
    bucket, ft = make(rate=4, burst=1)
    start = ft.now
    for _ in range(9):
        await bucket.acquire()
    assert abs((ft.now - start) - 2.0) < 1e-6, "8 throttled calls at 4/s take 8 * 0.25 = 2.0 virtual seconds"


@pytest.mark.asyncio
async def test_fractional_costs_are_deducted():
    bucket, ft = make(rate=10, burst=2)
    await bucket.acquire(0.5)
    await bucket.acquire(1.5)
    assert ft.sleeps == [], "0.5 + 1.5 fits in a burst of 2"
    await bucket.acquire(0.5)
    assert len(ft.sleeps) == 1 and abs(ft.sleeps[0] - 0.05) < 1e-9


def test_invalid_constructor_arguments():
    for rate, burst in [(0, 1), (-1, 1), (1, 0)]:
        with pytest.raises(ValueError):
            TokenBucket(rate, burst)


@pytest.mark.asyncio
async def test_invalid_cost_is_rejected():
    bucket, _ = make(rate=1, burst=2)
    for cost in (0, -1, 3):
        with pytest.raises(ValueError):
            await bucket.acquire(cost)


@pytest.mark.asyncio
async def test_works_with_the_real_clock_and_sleep():
    bucket = TokenBucket(rate=1000, burst=2)
    async with asyncio.timeout(2):
        for _ in range(4):
            await bucket.acquire()
