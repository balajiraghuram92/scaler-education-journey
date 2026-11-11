"""Fixed-window rate limiter (ported from the AddRateLimiter block in api/Program.cs).

AuthPolicy: 10 requests / 15 minutes. RefreshPolicy: 30 requests / 5 minutes,
partitioned by client IP. Rejection is a 429 problem-details response.
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request

from .errors import ApiProblem

_rate_buckets: dict[str, list[float]] = defaultdict(list)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_fixed_window(key: str, permit_limit: int, window_seconds: float) -> bool:
    now = time.monotonic()
    cutoff = now - window_seconds
    bucket = [t for t in _rate_buckets[key] if t > cutoff]
    _rate_buckets[key] = bucket
    if len(bucket) >= permit_limit:
        return False
    bucket.append(now)
    return True


async def require_auth_policy(request: Request) -> None:
    if not _check_fixed_window(f"auth:{_client_ip(request)}", 10, 15 * 60):
        raise ApiProblem(429, "Too Many Requests", "Rate limit exceeded.", request.url.path)


async def require_refresh_policy(request: Request) -> None:
    if not _check_fixed_window(f"refresh:{_client_ip(request)}", 30, 5 * 60):
        raise ApiProblem(429, "Too Many Requests", "Rate limit exceeded.", request.url.path)
