from __future__ import annotations

import asyncio
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import aclosing
from dataclasses import dataclass

from llm_retry import RetryPolicy, is_retryable


class StreamInterrupted(Exception):
    """The stream failed after tokens were already delivered; a retry would corrupt the output.

    Expose the text delivered so far as ``.partial``. Raise it ``from`` the original error.
    """

    def __init__(self, partial: str) -> None:
        raise NotImplementedError("Implement StreamInterrupted.__init__")


class BudgetExceeded(Exception):
    pass


@dataclass(slots=True)
class TokenBudget:
    limit: int
    used: int = 0
    reserved: int = 0

    def reserve(self, tokens: int) -> None:
        """Reserve worst-case tokens; raise ``BudgetExceeded`` if ``used + reserved + tokens > limit``.

        Must be a plain (non-async) method with no ``await`` so check-and-reserve is atomic.
        """
        raise NotImplementedError("Implement TokenBudget.reserve")

    def settle(self, reserved: int, actual: int) -> None:
        """Release the reservation and record the actual usage."""
        raise NotImplementedError("Implement TokenBudget.settle")


async def stream_with_retry(
    open_stream: Callable[[], AsyncIterator[str]],
    *,
    policy: RetryPolicy,
    rng: random.Random,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> AsyncIterator[str]:
    """Yield chunks from ``open_stream()``, retrying only while NO chunk has been delivered.

    - retry only when nothing was emitted, the error is retryable (``is_retryable``),
      attempts remain, and the ``retry_after`` hint is within ``policy.max_retry_after``
    - once a chunk was yielded, a failure raises ``StreamInterrupted(partial_text)`` from the error
    - non-retryable errors propagate unchanged
    - close the upstream async generator deterministically with ``contextlib.aclosing``
    """
    raise NotImplementedError("Implement stream_with_retry")
    yield ""  # pragma: no cover


async def metered_stream(
    budget: TokenBudget, reserve_tokens: int, chunks: AsyncIterator[str]
) -> AsyncIterator[str]:
    """Reserve ``reserve_tokens``, forward the chunks, and ALWAYS settle actual usage.

    - ``BudgetExceeded`` is raised on first iteration, before the upstream is touched
    - one chunk counts as one token; settle ``(reserve_tokens, produced)`` in a ``finally``
      so early ``break``, errors and cancellation all release the reservation
    - close the upstream with ``contextlib.aclosing``
    """
    raise NotImplementedError("Implement metered_stream")
    yield ""  # pragma: no cover
