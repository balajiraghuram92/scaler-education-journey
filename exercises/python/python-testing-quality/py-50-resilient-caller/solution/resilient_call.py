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
        if self.state is State.OPEN:
            if self.clock() - self._opened_at < self.reset_timeout:
                raise CircuitOpen("circuit open: failing fast")
            self.state = State.HALF_OPEN

    def record_success(self) -> None:
        self._failures = 0
        self.state = State.CLOSED

    def record_failure(self) -> None:
        self._failures += 1
        if self.state is State.HALF_OPEN or self._failures >= self.failure_threshold:
            self.state = State.OPEN
            self._opened_at = self.clock()


def full_jitter(attempt: int, base: float, cap: float, rng: random.Random) -> float:
    return rng.uniform(0.0, min(cap, base * 2**attempt))


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
        self._clock, self._sleep, self._rng, self._breaker = clock, sleep, rng, breaker
        self._max_attempts, self._base, self._cap = max_attempts, base, cap
        self._deadline, self._key_factory = deadline, key_factory

    def call[R](self, fn: Callable[[str], R]) -> R:
        """Call fn(idempotency_key); the SAME key is reused on every attempt."""
        key = self._key_factory()
        started = self._clock()
        for attempt in range(self._max_attempts):
            self._breaker.before_call()  # CircuitOpen propagates: never retried
            try:
                result = fn(key)
            except GatewayError as exc:
                if not exc.retryable:
                    raise
                self._breaker.record_failure()
                if attempt == self._max_attempts - 1:
                    raise
                delay = full_jitter(attempt, self._base, self._cap, self._rng)
                if isinstance(exc, RateLimited) and exc.retry_after is not None:
                    delay = max(delay, exc.retry_after)
                remaining = self._deadline - (self._clock() - started)
                if delay >= remaining:
                    raise DeadlineExceeded(
                        f"{delay:.2f}s backoff exceeds {remaining:.2f}s left"
                    ) from exc
                log.warning("retrying after %s", type(exc).__name__,
                            extra={"attempt": attempt + 1, "delay": round(delay, 3)})
                self._sleep(delay)
            else:
                self._breaker.record_success()
                return result
        raise AssertionError("unreachable")
