from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass


class ShuttingDown(Exception):
    """Raised when new work is started after draining began."""


class Lifecycle:
    def __init__(self) -> None:
        self._draining = False
        self._inflight = 0
        self._idle = asyncio.Event()
        self._idle.set()

    @property
    def draining(self) -> bool:
        return self._draining

    @property
    def inflight(self) -> int:
        return self._inflight

    @asynccontextmanager
    async def track(self) -> AsyncIterator[None]:
        if self._draining:
            raise ShuttingDown("service is shutting down")
        self._inflight += 1
        self._idle.clear()
        try:
            yield
        finally:
            self._inflight -= 1
            if self._inflight == 0:
                self._idle.set()

    async def shutdown(self, timeout: float) -> bool:
        self._draining = True
        if self._inflight == 0:  # already drained: a zero timeout must not turn this into a failure
            return True
        try:
            async with asyncio.timeout(timeout):
                await self._idle.wait()
        except TimeoutError:
            return False
        return True


@dataclass(frozen=True)
class Readiness:
    ready: bool
    checks: dict[str, str]


async def _run_one(check: Callable[[], Awaitable[None]], timeout: float) -> str:
    try:
        async with asyncio.timeout(timeout):
            await check()
    except TimeoutError:
        return "timeout"
    except Exception as exc:  # a failing check must never crash the probe
        return f"error: {type(exc).__name__}"
    return "ok"


async def run_checks(
    lifecycle: Lifecycle,
    checks: dict[str, Callable[[], Awaitable[None]]],
    *,
    timeout: float = 1.0,
    hard: set[str] | None = None,
) -> Readiness:
    if lifecycle.draining:
        return Readiness(False, {"lifecycle": "draining"})
    names = list(checks)
    results = await asyncio.gather(*(_run_one(checks[n], timeout) for n in names))
    report = dict(zip(names, results))
    required = set(names) if hard is None else hard
    return Readiness(all(report[n] == "ok" for n in required if n in report), report)
