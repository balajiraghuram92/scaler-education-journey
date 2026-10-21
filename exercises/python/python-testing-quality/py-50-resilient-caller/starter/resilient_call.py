from __future__ import annotations

import logging
import random
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from errors import GatewayError, RateLimited

log = logging.getLogger("gateway.resilience")


class CircuitOpen(GatewayError):
    """Raised without calling the dependency while the breaker is open."""


class DeadlineExceeded(GatewayError):
    """The overall time budget ran out before an attempt could succeed."""


class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    clock: Callable[[], float]
    failure_threshold: int = 3
    reset_timeout: float = 30.0
    state: State = State.CLOSED
    _failures: int = field(default=0, init=False, repr=False)
    _opened_at: float = field(default=0.0, init=False, repr=False)

    def before_call(self) -> None:
        """Raise ``CircuitOpen`` while OPEN and inside the cool-down; otherwise move OPEN to HALF_OPEN."""
        raise NotImplementedError("Implement CircuitBreaker.before_call")

    def record_success(self) -> None:
        """Close the circuit and reset the failure count."""
        raise NotImplementedError("Implement CircuitBreaker.record_success")

    def record_failure(self) -> None:
        """Open the circuit at ``failure_threshold`` failures, or immediately when HALF_OPEN."""
        raise NotImplementedError("Implement CircuitBreaker.record_failure")


def full_jitter(attempt: int, base: float, cap: float, rng: random.Random) -> float:
    """Uniform value in ``[0, min(cap, base * 2**attempt)]``."""
    raise NotImplementedError("Implement full_jitter")


class ResilientCaller:
    """Retries retryable GatewayErrors with jitter, within a deadline and a breaker."""

    def __init__(
        self,
        *,
        clock: Callable[[], float],
        sleep: Callable[[float], None],
        rng: random.Random,
        breaker: CircuitBreaker,
        max_attempts: int = 4,
        base: float = 0.5,
        cap: float = 20.0,
        deadline: float = 30.0,
        key_factory: Callable[[], str] = lambda: uuid.uuid4().hex,
    ) -> None:
        raise NotImplementedError("Implement ResilientCaller.__init__")

    def call[R](self, fn: Callable[[str], R]) -> R:
        """Call ``fn(idempotency_key)``; the SAME key (from ``key_factory()``) is used on every attempt.

        - non-retryable ``GatewayError`` and ``CircuitOpen`` propagate immediately
        - retryable failures call ``breaker.record_failure()``; success calls ``record_success()``
        - after the last attempt the last error is re-raised
        - delay is ``full_jitter(attempt, ...)`` (attempt starts at 0), at least ``retry_after`` for RateLimited
        - if the delay does not fit in the time left before ``deadline``, raise
          ``DeadlineExceeded`` ``from`` the last error WITHOUT sleeping
        - log each retry at WARNING with ``attempt`` (1-based) and ``delay`` in ``extra``
        """
        raise NotImplementedError("Implement ResilientCaller.call")
