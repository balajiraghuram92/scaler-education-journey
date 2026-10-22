from __future__ import annotations

import asyncio
import math
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import TypeVar

T = TypeVar("T")

RETRYABLE_STATUS = frozenset({500, 502, 503, 504})
NON_RETRYABLE_429_CODES = frozenset({"insufficient_quota", "billing_hard_limit_reached"})


class TransportError(Exception):
    """Connection reset, connect failure or read timeout (not a deadline you set)."""


class ProviderError(Exception):
    def __init__(self, status: int, code: str | None = None,
                 retry_after: float | None = None) -> None:
        super().__init__(f"HTTP {status} {code or ''}".strip())
        self.status = status
        self.code = code
        self.retry_after = retry_after


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    if value is None:
        return None
    try:
        seconds = float(value)
        return max(0.0, seconds) if math.isfinite(seconds) else None
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - (now or datetime.now(timezone.utc))).total_seconds())


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 4
    base_delay: float = 0.5
    max_delay: float = 20.0
    max_retry_after: float = 30.0

    def delay(self, attempt: int, retry_after: float | None, rng: random.Random) -> float:
        window = min(self.max_delay, self.base_delay * 2**attempt)
        jittered = rng.uniform(0.0, window)
        return jittered if retry_after is None else max(jittered, retry_after)


def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, TransportError):
        return True
    if isinstance(exc, ProviderError):
        if exc.status == 429:
            return exc.code not in NON_RETRYABLE_429_CODES
        return exc.status in RETRYABLE_STATUS
    return False


async def retry_async(
    op: Callable[[], Awaitable[T]],
    *,
    policy: RetryPolicy,
    rng: random.Random,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    for attempt in range(policy.max_attempts):
        try:
            return await op()
        except Exception as exc:                   # CancelledError is BaseException: not caught
            if not is_retryable(exc) or attempt + 1 >= policy.max_attempts:
                raise
            hint = getattr(exc, "retry_after", None)
            if hint is not None and hint > policy.max_retry_after:
                raise
            await sleep(policy.delay(attempt, hint, rng))
    raise AssertionError("unreachable")
