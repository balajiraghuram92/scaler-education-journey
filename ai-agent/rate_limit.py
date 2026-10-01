"""Per-user rate-limit hook point (in-process, no external dependency).

Use ``Depends(rate_limited_user)`` instead of ``Depends(get_current_user)`` on
any route that can trigger a paid model call. It authenticates first, then
allows at most ``AI_AGENT_RATE_LIMIT_PER_MINUTE`` requests per user in a
sliding 60-second window and answers 429 beyond that.

Limits: state lives in this process only, so it resets on restart and is not
shared between replicas (fine for the single EC2 container). Replace
``SlidingWindowLimiter`` with a Postgres- or Redis-backed implementation of the
same ``allow(key)`` method when the service scales out, or when the daily
$-budget gate (cost governor) lands. nginx ``limit_req`` on the tutor host is
the coarse per-IP layer in front of this.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, Request

from auth import get_current_user, user_id


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: float = 60.0, clock=time.monotonic):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = self._clock()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window_seconds:
                hits.popleft()
            if len(hits) >= self.max_requests:
                return False
            hits.append(now)
            return True


def rate_limited_user(request: Request, claims: dict = Depends(get_current_user)) -> dict:
    limiter: SlidingWindowLimiter = request.app.state.rate_limiter
    if not limiter.allow(user_id(claims)):
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": str(int(limiter.window_seconds))},
        )
    return claims
