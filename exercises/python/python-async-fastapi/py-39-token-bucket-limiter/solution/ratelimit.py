import asyncio
import time
from collections.abc import Awaitable, Callable

_EPS = 1e-9  # float slack: after sleeping exactly long enough, the refill can fall a hair short


class TokenBucket:
    """Allows `rate` operations per second on average, with bursts of up to `burst`."""

    def __init__(
        self,
        rate: float,
        burst: int,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if rate <= 0 or burst < 1:
            raise ValueError("rate must be > 0 and burst >= 1")
        self._rate = rate
        self._burst = burst
        self._clock = clock
        self._sleep = sleep
        self._tokens = float(burst)
        self._updated = clock()
        self._lock = asyncio.Lock()  # asyncio.Lock wakes waiters in FIFO order

    def _refill(self) -> None:
        now = self._clock()
        elapsed = now - self._updated
        self._updated = now
        self._tokens = min(float(self._burst), self._tokens + elapsed * self._rate)

    async def acquire(self, cost: float = 1.0) -> None:
        if cost <= 0 or cost > self._burst:
            raise ValueError("cost must be in (0, burst]")
        async with self._lock:
            while True:
                self._refill()
                if self._tokens >= cost - _EPS:
                    self._tokens = max(0.0, self._tokens - cost)
                    return
                await self._sleep((cost - self._tokens) / self._rate)
