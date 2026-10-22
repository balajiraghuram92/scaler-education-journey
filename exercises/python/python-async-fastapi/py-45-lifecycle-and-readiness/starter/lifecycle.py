from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass


class ShuttingDown(Exception):
    """Raised when new work is started after draining began."""


class Lifecycle:
    """Tracks in-flight work and drains it on shutdown."""

    def __init__(self) -> None:
        """Use an ``asyncio.Event`` that is set whenever the in-flight count is zero."""
        raise NotImplementedError("Implement __init__")

    @property
    def draining(self) -> bool:
        raise NotImplementedError("Implement draining")

    @property
    def inflight(self) -> int:
        raise NotImplementedError("Implement inflight")

    @asynccontextmanager
    async def track(self) -> AsyncIterator[None]:
        """Raise ``ShuttingDown`` if draining has begun; otherwise count the work as in flight
        while the body runs, and always decrement on exit (also when the body raises)."""
        raise NotImplementedError("Implement track")
        yield  # pragma: no cover  (makes this an async generator for @asynccontextmanager)

    async def shutdown(self, timeout: float) -> bool:
        """Start draining, wait up to ``timeout`` seconds for the in-flight count to reach zero and
        return ``True`` if drained, ``False`` on timeout. Do not cancel the in-flight work."""
        raise NotImplementedError("Implement shutdown")


@dataclass(frozen=True)
class Readiness:
    ready: bool
    checks: dict[str, str]


async def run_checks(
    lifecycle: Lifecycle,
    checks: dict[str, Callable[[], Awaitable[None]]],
    *,
    timeout: float = 1.0,
    hard: set[str] | None = None,
) -> Readiness:
    """Power for ``/readyz``.

    - if ``lifecycle.draining``: return ``Readiness(False, {"lifecycle": "draining"})`` without
      calling any check
    - otherwise run all checks concurrently with ``asyncio.gather``, each under
      ``asyncio.timeout(timeout)``
    - each result is ``"ok"``, ``"timeout"`` or ``"error: <ExceptionClassName>"``; a failing check
      must never raise out of ``run_checks``
    - ``ready`` is true when every check named in ``hard`` is ``"ok"``; if ``hard`` is None, all
      checks are hard
    """
    raise NotImplementedError("Implement run_checks")
