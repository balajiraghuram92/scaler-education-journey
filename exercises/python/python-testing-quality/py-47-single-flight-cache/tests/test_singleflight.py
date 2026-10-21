import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from singleflight import SingleFlightCache


class FakeClock:
    def __init__(self) -> None:
        self.now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs: float) -> None:
        self.now += timedelta(**kwargs)


class GatedLoader:
    """Loader that blocks on an event so tests control exactly when it finishes."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.gate = asyncio.Event()
        self.fail_next = False

    async def __call__(self, key: str) -> str:
        self.calls.append(key)
        await self.gate.wait()
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("upstream down")
        return f"value-{len(self.calls)}"


async def settle() -> None:
    for _ in range(5):
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_concurrent_misses_share_one_load():
    loader = GatedLoader()
    cache = SingleFlightCache(loader, FakeClock(), timedelta(minutes=5))
    waiters = [asyncio.create_task(cache.get("doc")) for _ in range(5)]
    await settle()
    loader.gate.set()
    results = await asyncio.gather(*waiters)
    assert results == ["value-1"] * 5, "all five callers share the same result"
    assert loader.calls == ["doc"], "the loader must be called exactly once"


@pytest.mark.asyncio
async def test_ttl_expiry_triggers_reload():
    clock = FakeClock()
    loader = GatedLoader()
    loader.gate.set()
    cache = SingleFlightCache(loader, clock, timedelta(minutes=5))
    assert await cache.get("doc") == "value-1"
    clock.advance(minutes=4)
    assert await cache.get("doc") == "value-1", "still fresh after 4 minutes"
    assert loader.calls == ["doc"]
    clock.advance(minutes=2)
    assert await cache.get("doc") == "value-2", "expired after 6 minutes"


@pytest.mark.asyncio
async def test_value_is_stale_exactly_at_ttl():
    clock = FakeClock()
    loader = GatedLoader()
    loader.gate.set()
    cache = SingleFlightCache(loader, clock, timedelta(minutes=5))
    await cache.get("doc")
    clock.advance(minutes=5)
    assert await cache.get("doc") == "value-2", "fresh means strictly less than the ttl"


@pytest.mark.asyncio
async def test_failure_is_shared_but_not_cached():
    loader = GatedLoader()
    loader.fail_next = True
    cache = SingleFlightCache(loader, FakeClock(), timedelta(minutes=5))
    waiters = [asyncio.create_task(cache.get("doc")) for _ in range(3)]
    await settle()
    loader.gate.set()
    outcomes = await asyncio.gather(*waiters, return_exceptions=True)
    assert all(isinstance(o, RuntimeError) for o in outcomes), "every waiter receives the exception"
    assert loader.calls == ["doc"]
    assert await cache.get("doc") == "value-2", "the next call must retry the loader"


@pytest.mark.asyncio
async def test_cancelled_waiter_does_not_cancel_the_shared_load():
    loader = GatedLoader()
    cache = SingleFlightCache(loader, FakeClock(), timedelta(minutes=5))
    first = asyncio.create_task(cache.get("doc"))
    second = asyncio.create_task(cache.get("doc"))
    await settle()
    first.cancel()
    loader.gate.set()
    assert await second == "value-1"
    with pytest.raises(asyncio.CancelledError):
        await first
    assert loader.calls == ["doc"]


@pytest.mark.asyncio
async def test_cancelled_only_waiter_still_populates_cache():
    clock = FakeClock()
    loader = GatedLoader()
    cache = SingleFlightCache(loader, clock, timedelta(minutes=5))
    waiter = asyncio.create_task(cache.get("doc"))
    await settle()
    waiter.cancel()
    loader.gate.set()
    await settle()
    assert await cache.get("doc") == "value-1", "the load keeps running and its result is cached"
    assert loader.calls == ["doc"]


@pytest.mark.asyncio
async def test_different_keys_load_independently():
    loader = GatedLoader()
    loader.gate.set()
    cache = SingleFlightCache(loader, FakeClock(), timedelta(minutes=5))
    a, b = await asyncio.gather(cache.get("a"), cache.get("b"))
    assert sorted(loader.calls) == ["a", "b"]
    assert a != b
    assert await cache.get("a") == a, "second read of a key is a cache hit"
    assert len(loader.calls) == 2
