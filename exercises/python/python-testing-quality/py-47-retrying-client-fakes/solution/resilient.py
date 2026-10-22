from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Response:
    status: int
    body: str = ""
    retry_after: float | None = None


class UpstreamError(Exception):
    def __init__(self, attempts: int, last_status: int) -> None:
        super().__init__(f"gave up after {attempts} attempts (last status {last_status})")
        self.attempts = attempts
        self.last_status = last_status


Transport = Callable[[str], Awaitable[Response]]
Sleep = Callable[[float], Awaitable[None]]

RETRYABLE = frozenset({429, 500, 502, 503, 504})


class RetryingClient:
    def __init__(
        self,
        transport: Transport,
        sleep: Sleep,
        *,
        max_attempts: int = 4,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self._transport = transport
        self._sleep = sleep
        self._max_attempts = max_attempts
        self._base = base_delay
        self._max_delay = max_delay

    def _delay(self, attempt: int, resp: Response) -> float:
        backoff = min(self._base * 2 ** (attempt - 1), self._max_delay)
        if resp.retry_after is not None:
            return min(max(backoff, resp.retry_after), self._max_delay)
        return backoff

    async def call(self, prompt: str) -> str:
        resp = Response(0)
        for attempt in range(1, self._max_attempts + 1):
            resp = await self._transport(prompt)
            if resp.status < 400:
                return resp.body
            if resp.status not in RETRYABLE:
                raise UpstreamError(attempt, resp.status)
            if attempt < self._max_attempts:
                await self._sleep(self._delay(attempt, resp))
        raise UpstreamError(self._max_attempts, resp.status)
