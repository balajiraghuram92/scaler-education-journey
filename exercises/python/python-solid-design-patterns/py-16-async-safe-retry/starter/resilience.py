from __future__ import annotations

import asyncio
import functools
import inspect
import time
from collections.abc import Callable
from typing import Any


def retry(
    attempts: int = 3,
    on: tuple[type[BaseException], ...] = (ConnectionError, TimeoutError),
    backoff_s: float = 0.0,
    sleep: Callable[[float], Any] = time.sleep,
    asleep: Callable[[float], Any] = asyncio.sleep,
):
    """Return a decorator that retries a sync or async callable.

    - attempts < 1 raises ValueError immediately (when retry(...) is called)
    - a coroutine function gets an ``async def`` wrapper that awaits the call inside the
      try block; inspect.iscoroutinefunction(decorated) stays True. Anything else gets a
      plain wrapper
    - only exceptions in ``on`` are retried; others propagate at once, with no extra attempt
    - between attempts (never after the last) wait backoff_s * 2 ** (attempt - 1) using the
      injected ``sleep`` (sync) or ``asleep`` (async, awaited)
    - after the last failed attempt re-raise the last exception unchanged
    - use functools.wraps so __name__ and __doc__ survive
    """
    raise NotImplementedError("Implement retry")
