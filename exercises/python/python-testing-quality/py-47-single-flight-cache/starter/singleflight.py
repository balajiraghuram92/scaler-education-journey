from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta

Loader = Callable[[str], Awaitable[str]]
Clock = Callable[[], datetime]


class SingleFlightCache:
    """Async TTL cache where concurrent misses for one key share a single load."""

    def __init__(self, loader: Loader, clock: Clock, ttl: timedelta) -> None:
        raise NotImplementedError("Implement SingleFlightCache.__init__")

    async def get(self, key: str) -> str:
        """Return the cached value if ``clock() - stored_at < ttl``.

        Otherwise start ONE load for the key (an ``asyncio.Task``) and make every
        concurrent caller await that same task.

        - a successful load is cached with the clock time at completion
        - a failed load is NOT cached; all waiters receive the exception and the
          next ``get`` retries the loader
        - cancelling one waiter must not cancel the shared load (``asyncio.shield``)
        - the in-flight entry is always removed when the load ends
        """
        raise NotImplementedError("Implement SingleFlightCache.get")
