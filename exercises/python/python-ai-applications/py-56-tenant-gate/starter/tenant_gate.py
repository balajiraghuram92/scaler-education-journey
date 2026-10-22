from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import FastAPI

PROMPT_VERSION = "v1"
MODEL = "small-model"


@dataclass(frozen=True, slots=True)
class Generation:
    text: str
    cost_usd: float


Generate = Callable[[str], Awaitable[Generation]]


# Suggested building blocks (free design, tests only use create_app and Generation):
#   - a per-tenant token-bucket limiter  (take(tenant) -> 0.0 or seconds to wait)
#   - a per-tenant, per-UTC-day spend guard (day = int(clock() // 86400))
#   - a TTL cache keyed by sha256(canonical JSON of tenant, PROMPT_VERSION, MODEL, prompt, temperature)
#   - a request model: prompt (min length 1), temperature float 0..2 (default 0.0)
#   - a MODULE-LEVEL tenant-header dependency (with postponed annotations FastAPI resolves
#     annotations through module globals, so a dependency defined inside create_app becomes a query parameter)


def create_app(*, clock: Callable[[], float], generate: Generate, rate: float = 1.0, burst: float = 2,
               daily_budget_usd: float = 0.01, estimate_usd: float = 0.004,
               cache_ttl_s: float = 60.0) -> FastAPI:
    """Build the app with ``POST /chat`` (body ``{"prompt", "temperature"}``, header ``X-Tenant-Id``).

    Order of checks:
    1. rate limit  -> 429 ``{"error": "rate_limited"}`` + ``Retry-After`` (ceil of the wait, whole seconds)
    2. cache (only when temperature == 0.0) -> ``{"answer", "cached": true, "cost_usd": 0.0}``
    3. budget (spent + ``estimate_usd`` <= ``daily_budget_usd`` per tenant per day) -> 429
       ``{"error": "budget_exhausted"}`` with NO ``Retry-After`` and no provider call
    4. provider ``await generate(prompt)``; record ``cost_usd``; cache when temperature == 0.0;
       return ``{"answer", "cached": false, "cost_usd"}``. A provider exception -> 502
       ``{"error": "upstream_failed"}``, no spend recorded, nothing cached.

    A missing tenant header or an invalid body gives 422. All state is per tenant; time comes
    only from ``clock``.
    """
    raise NotImplementedError("Implement create_app")
