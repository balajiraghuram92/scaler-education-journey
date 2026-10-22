from __future__ import annotations

import asyncio
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
    """Return a decorator that retries a synchronous callable.

    - exceptions matching ``on`` are retried; the last one is re-raised when
      ``attempts`` is exhausted; other exceptions propagate immediately
    - delay before the next attempt is ``base_delay * 2 ** (attempt - 1)``;
      never sleep after the final attempt
    - ``attempts < 1`` raises ``ValueError("attempts must be >= 1")`` when the factory is called
    - use ``functools.wraps`` and type the wrapper ``(*args: P.args, **kwargs: P.kwargs) -> R``
      so the decorated function keeps its exact signature and metadata

    Type-checking (mypy --strict / pyright) is a self-check; the hidden tests only
    exercise runtime behaviour.
    """
    raise NotImplementedError("Implement retry")


def aretry[**P, R](
    *,
    attempts: int,
    on: type[Exception] | tuple[type[Exception], ...] = ConnectionError,
    base_delay: float = 0.5,
    sleep: ASleep = asyncio.sleep,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Async twin of ``retry``: wraps a coroutine function, awaits it and awaits ``sleep``."""
    raise NotImplementedError("Implement aretry")
