import asyncio
import time
from collections.abc import Awaitable, Callable


class TokenBucket:
    """Allows ``rate`` operations per second on average, with bursts of up to ``burst``."""

    def __init__(
        self,
        rate: float,
        burst: int,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        """``rate`` tokens are added per second, up to ``burst``; the bucket starts full.

        ``rate <= 0`` or ``burst < 1`` raises ``ValueError``.
        """
        raise NotImplementedError("Implement __init__")

    async def acquire(self, cost: float = 1.0) -> None:
        """Wait until ``cost`` tokens are available, then deduct them.

        - ``cost <= 0`` or ``cost > burst`` raises ``ValueError`` (it could never be satisfied)
        - waiters are served in arrival order (FIFO)
        - the wait is computed, not polled: sleep ``(cost - tokens) / rate`` seconds, then re-check
        - refill lazily from the clock, never above ``burst``
        - allow a tiny epsilon (about 1e-9) when comparing tokens to cost so floating-point
          error cannot make the loop spin forever with zero-length sleeps
        """
        raise NotImplementedError("Implement acquire")
