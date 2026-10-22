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
    """Retry a sync or async callable. `sleep`/`asleep` are injectable so tests never wait."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def decorate(fn):
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def awrapper(*args, **kwargs):
                for attempt in range(1, attempts + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except on:
                        if attempt == attempts:
                            raise
                        await asleep(backoff_s * 2 ** (attempt - 1))
            return awrapper

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except on:
                    if attempt == attempts:
                        raise
                    sleep(backoff_s * 2 ** (attempt - 1))
        return wrapper

    return decorate
