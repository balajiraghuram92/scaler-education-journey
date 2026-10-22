from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta

Loader = Callable[[str], Awaitable[str]]
Clock = Callable[[], datetime]


class SingleFlightCache:
    """TTL cache where concurrent misses for one key share a single load."""

    def __init__(self, loader: Loader, clock: Clock, ttl: timedelta) -> None:
        self._loader = loader
        self._clock = clock
        self._ttl = ttl
        self._values: dict[str, tuple[datetime, str]] = {}
        self._inflight: dict[str, asyncio.Task[str]] = {}

    async def get(self, key: str) -> str:
        hit = self._values.get(key)
        if hit is not None and self._clock() - hit[0] < self._ttl:
            return hit[1]
        task = self._inflight.get(key)
        if task is None:
            task = asyncio.create_task(self._load(key))
            self._inflight[key] = task
        # shield: one cancelled waiter must not cancel the shared load
        return await asyncio.shield(task)

    async def _load(self, key: str) -> str:
        try:
            value = await self._loader(key)
            self._values[key] = (self._clock(), value)
            return value
        finally:
            self._inflight.pop(key, None)
