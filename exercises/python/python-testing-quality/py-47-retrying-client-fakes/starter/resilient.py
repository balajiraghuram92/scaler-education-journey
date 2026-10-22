from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Response:
    status: int
    body: str = ""
    retry_after: float | None = None


class UpstreamError(Exception):
    """Raised when the call fails. Carries ``attempts`` and ``last_status``.

    Message format: ``"gave up after <n> attempts (last status <status>)"``.
    """

    def __init__(self, attempts: int, last_status: int) -> None:
        raise NotImplementedError("Implement UpstreamError.__init__")


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
        """``max_attempts < 1`` raises ``ValueError``."""
        raise NotImplementedError("Implement RetryingClient.__init__")

    async def call(self, prompt: str) -> str:
        """Return the body of the first response with ``status < 400``.

        - Retry only the RETRYABLE statuses; any other status >= 400 raises
          ``UpstreamError`` immediately (one attempt, no sleep).
        - Delay after failed attempt ``n`` is ``min(base_delay * 2 ** (n - 1), max_delay)``;
          if the response has ``retry_after`` use ``max(backoff, retry_after)``, still
          capped at ``max_delay``.
        - After the last attempt fails raise ``UpstreamError(max_attempts, last_status)``
          without sleeping after it.
        """
        raise NotImplementedError("Implement RetryingClient.call")
