from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable

Sleep = Callable[[float], None]
ASleep = Callable[[float], Awaitable[None]]


def retry[**P, R](
    *,
    attempts: int,
    on: type[Exception] | tuple[type[Exception], ...] = ConnectionError,
    base_delay: float = 0.5,
    sleep: Sleep = lambda s: None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry a sync callable; the decorated function keeps its exact signature."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except on:
                    if attempt == attempts:
                        raise
                    sleep(base_delay * 2 ** (attempt - 1))
            raise AssertionError("unreachable")  # keeps the checker happy

        return wrapper

    return decorate


def aretry[**P, R](
    *,
    attempts: int,
    on: type[Exception] | tuple[type[Exception], ...] = ConnectionError,
    base_delay: float = 0.5,
    sleep: ASleep = asyncio.sleep,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Async twin of retry: wraps a coroutine function."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def decorate(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except on:
                    if attempt == attempts:
                        raise
                    await sleep(base_delay * 2 ** (attempt - 1))
            raise AssertionError("unreachable")

        return wrapper

    return decorate
