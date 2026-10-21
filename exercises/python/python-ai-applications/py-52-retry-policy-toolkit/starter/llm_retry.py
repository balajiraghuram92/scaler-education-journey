from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar

T = TypeVar("T")


class TransportError(Exception):
    """Connection reset, connect failure or read timeout (not a deadline you set)."""


class ProviderError(Exception):
    """An HTTP error from the provider.

    Store ``status``, ``code`` and ``retry_after`` as attributes. The message should be
    ``"HTTP <status> <code>"`` (without a trailing space when there is no code).
    """

    def __init__(self, status: int, code: str | None = None,
                 retry_after: float | None = None) -> None:
        raise NotImplementedError("Implement ProviderError.__init__")


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    """Parse a ``Retry-After`` header: delta-seconds or an HTTP-date.

    Negative values and past dates clamp to ``0.0``; ``None``, ``"nan"``, ``"inf"`` and
    unparseable text return ``None``. ``now`` (default: current UTC time) makes dates testable.
    """
    raise NotImplementedError("Implement parse_retry_after")


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 4
    base_delay: float = 0.5
    max_delay: float = 20.0
    max_retry_after: float = 30.0

    def delay(self, attempt: int, retry_after: float | None, rng: random.Random) -> float:
        """Full jitter: ``rng.uniform(0, min(max_delay, base_delay * 2**attempt))``;
        when ``retry_after`` is given return ``max(jitter, retry_after)``."""
        raise NotImplementedError("Implement RetryPolicy.delay")


def is_retryable(exc: BaseException) -> bool:
    """True for TransportError, HTTP 500/502/503/504 and 429, except a 429 whose ``code`` is
    ``insufficient_quota`` or ``billing_hard_limit_reached``. Everything else is False."""
    raise NotImplementedError("Implement is_retryable")


async def retry_async(
    op: Callable[[], Awaitable[T]],
    *,
    policy: RetryPolicy,
    rng: random.Random,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Await ``op()``; on a retryable failure sleep ``policy.delay(...)`` and try again.

    - at most ``policy.max_attempts`` attempts; re-raise the last error when exhausted
    - re-raise immediately when the error's ``retry_after`` exceeds ``policy.max_retry_after``
    - never swallow ``asyncio.CancelledError`` (catch ``Exception`` only)
    """
    raise NotImplementedError("Implement retry_async")
