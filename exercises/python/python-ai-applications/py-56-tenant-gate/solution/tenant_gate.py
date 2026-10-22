from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

PROMPT_VERSION = "v1"
MODEL = "small-model"


@dataclass(frozen=True, slots=True)
class Generation:
    text: str
    cost_usd: float


Generate = Callable[[str], Awaitable[Generation]]


class TenantLimiter:
    """Token bucket per tenant. take() returns 0.0 if allowed, else seconds to wait."""

    def __init__(self, rate: float, burst: float, clock: Callable[[], float]) -> None:
        self.rate, self.burst, self._clock = rate, burst, clock
        self._state: dict[str, tuple[float, float]] = {}

    def take(self, tenant: str, cost: float = 1.0) -> float:
        now = self._clock()
        tokens, last = self._state.get(tenant, (self.burst, now))
        tokens = min(self.burst, tokens + (now - last) * self.rate)
        if tokens >= cost:
            self._state[tenant] = (tokens - cost, now)
            return 0.0
        self._state[tenant] = (tokens, now)
        return (cost - tokens) / self.rate


class SpendGuard:
    """Daily budget per tenant; the day boundary comes from the injected clock."""

    def __init__(self, daily_budget_usd: float, clock: Callable[[], float]) -> None:
        self.budget, self._clock = daily_budget_usd, clock
        self._spent: dict[tuple[str, int], float] = {}

    def _key(self, tenant: str) -> tuple[str, int]:
        return tenant, int(self._clock() // 86400)

    def allows(self, tenant: str, estimate_usd: float) -> bool:
        return self._spent.get(self._key(tenant), 0.0) + estimate_usd <= self.budget

    def record(self, tenant: str, actual_usd: float) -> None:
        key = self._key(tenant)
        self._spent[key] = self._spent.get(key, 0.0) + actual_usd

    def spent(self, tenant: str) -> float:
        return self._spent.get(self._key(tenant), 0.0)


class TTLCache:
    def __init__(self, ttl_s: float, clock: Callable[[], float]) -> None:
        self._ttl, self._clock = ttl_s, clock
        self._data: dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> str | None:
        item = self._data.get(key)
        if item is None or item[0] <= self._clock():
            self._data.pop(key, None)
            return None
        return item[1]

    def put(self, key: str, value: str) -> None:
        self._data[key] = (self._clock() + self._ttl, value)


def cache_key(tenant: str, prompt: str, temperature: float) -> str:
    blob = json.dumps({"t": tenant, "pv": PROMPT_VERSION, "m": MODEL, "p": prompt, "temp": temperature},
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


class ChatIn(BaseModel):
    prompt: str = Field(min_length=1)
    temperature: float = Field(0.0, ge=0.0, le=2.0)


def tenant_id(x_tenant_id: Annotated[str, Header()]) -> str:
    return x_tenant_id      # module level: with postponed annotations FastAPI resolves names via module globals


def create_app(*, clock: Callable[[], float], generate: Generate, rate: float = 1.0, burst: float = 2,
               daily_budget_usd: float = 0.01, estimate_usd: float = 0.004,
               cache_ttl_s: float = 60.0) -> FastAPI:
    limiter = TenantLimiter(rate, burst, clock)
    spend = SpendGuard(daily_budget_usd, clock)
    cache = TTLCache(cache_ttl_s, clock)
    app = FastAPI()

    @app.post("/chat")
    async def chat(body: ChatIn, tenant: Annotated[str, Depends(tenant_id)]) -> JSONResponse:
        wait = limiter.take(tenant)
        if wait > 0:
            return JSONResponse({"error": "rate_limited"}, status_code=429,
                                headers={"Retry-After": str(math.ceil(wait))})
        key = cache_key(tenant, body.prompt, body.temperature)
        if body.temperature == 0.0 and (hit := cache.get(key)) is not None:
            return JSONResponse({"answer": hit, "cached": True, "cost_usd": 0.0})
        if not spend.allows(tenant, estimate_usd):
            return JSONResponse({"error": "budget_exhausted"}, status_code=429)
        try:
            gen = await generate(body.prompt)
        except Exception:
            return JSONResponse({"error": "upstream_failed"}, status_code=502)
        spend.record(tenant, gen.cost_usd)
        if body.temperature == 0.0:
            cache.put(key, gen.text)
        return JSONResponse({"answer": gen.text, "cached": False, "cost_usd": gen.cost_usd})

    return app
