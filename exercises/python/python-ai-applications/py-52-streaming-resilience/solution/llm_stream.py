from __future__ import annotations

import asyncio
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import aclosing
from dataclasses import dataclass

from llm_retry import RetryPolicy, is_retryable


class StreamInterrupted(Exception):
    """The stream failed after tokens were already delivered; a retry would corrupt the output."""

    def __init__(self, partial: str) -> None:
        super().__init__(f"stream interrupted after {len(partial)} characters")
        self.partial = partial


class BudgetExceeded(Exception):
    pass


@dataclass(slots=True)
class TokenBudget:
    limit: int
    used: int = 0
    reserved: int = 0

    def reserve(self, tokens: int) -> None:
        if self.used + self.reserved + tokens > self.limit:
            raise BudgetExceeded(f"need {tokens}, have {self.limit - self.used - self.reserved}")
        self.reserved += tokens

    def settle(self, reserved: int, actual: int) -> None:
        self.reserved -= reserved
        self.used += actual


async def stream_with_retry(
    open_stream: Callable[[], AsyncIterator[str]],
    *,
    policy: RetryPolicy,
    rng: random.Random,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> AsyncIterator[str]:
    for attempt in range(policy.max_attempts):
        emitted: list[str] = []
        try:
            async with aclosing(open_stream()) as chunks:
                async for chunk in chunks:
                    emitted.append(chunk)
                    yield chunk
            return
        except Exception as exc:
            if emitted:
                raise StreamInterrupted("".join(emitted)) from exc
            if not is_retryable(exc) or attempt + 1 >= policy.max_attempts:
                raise
            hint = getattr(exc, "retry_after", None)
            if hint is not None and hint > policy.max_retry_after:
                raise
            await sleep(policy.delay(attempt, hint, rng))


async def metered_stream(
    budget: TokenBudget, reserve_tokens: int, chunks: AsyncIterator[str]
) -> AsyncIterator[str]:
    budget.reserve(reserve_tokens)              # raises BudgetExceeded before any work
    produced = 0
    try:
        async with aclosing(chunks) as it:
            async for chunk in it:
                produced += 1                   # treat each chunk as one token in this exercise
                yield chunk
    finally:
        budget.settle(reserve_tokens, produced)
