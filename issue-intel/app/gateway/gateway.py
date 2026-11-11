"""ModelGateway: the only code allowed to call a model."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.gateway.adapters import (
    AnthropicMessagesAdapter,
    FakeAdapter,
    ModelAdapter,
    OpenAICompatAdapter,
    RoutedAdapter,
    price_of,
)
from app.gateway.budgets import check_budget, record_spend
from app.gateway.cache import ResultCache, cache_key
from app.gateway.routing import Route, get_active, route_from_dict
from app.gateway.tasks import TaskType
from app.settings import Settings, get_settings

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GatewayResult:
    text: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int


@dataclass
class LoggedCall:
    task_type: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    run_id: str | None = None
    fallback_used: bool = False
    routing_version: int | None = None
    cached: bool = False
    is_shadow: bool = False


class ModelGateway:
    def __init__(
        self,
        settings: Settings | None = None,
        adapter: ModelAdapter | None = None,
        session_factory: Callable[[], AsyncSession] | None = None,
        model_override: str | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._adapter = adapter or self._build_adapter()
        self._session_factory = session_factory
        self._model_override = model_override
        self._cache = ResultCache()
        self._embed_vectors: dict[str, list[list[float]]] = {}
        self.logged_calls: list[LoggedCall] = []

    def _build_adapter(self) -> ModelAdapter:
        if self._settings.model_adapter == "openai":
            openai = OpenAICompatAdapter(
                base_url=self._settings.openai_base_url,
                api_key=self._settings.openai_api_key,
                key_header=self._settings.openai_api_key_header,
            )
            if not self._settings.anthropic_base_url:
                return openai
            anthropic = AnthropicMessagesAdapter(
                base_url=self._settings.anthropic_base_url,
                api_key=self._settings.anthropic_api_key,
                version=self._settings.anthropic_version,
                max_tokens=self._settings.anthropic_max_tokens,
            )
            return RoutedAdapter(
                default=openai,
                by_prefix=[
                    (prefix, anthropic)
                    for prefix in self._settings.anthropic_model_prefixes
                ],
            )
        return FakeAdapter(dim=self._settings.embedding_dim)

    def model_for(self, task: TaskType) -> str:
        """Static table (G0-G3 compat). Prefer route_for (versioned routing)."""
        return self._settings.task_models[task.value]

    async def route_for(
        self, task: TaskType, module: str | None = None
    ) -> tuple[Route, int | None]:
        if self._session_factory is not None:
            async with self._session_factory() as session:
                active = await get_active(session)
                if active is not None:
                    route = route_from_dict(task.value, active.routes)
                    if (
                        route.canary_module
                        and route.canary_model
                        and module == route.canary_module
                        and random.random() < route.canary_share
                    ):
                        route = Route(
                            primary=route.canary_model, fallback=route.fallback,
                            token_limit=route.token_limit, mode=route.mode,
                        )
                    return route, active.version
        static = self._settings.task_models[task.value]
        return Route(primary=static, fallback="", token_limit=8000, mode="SYNC"), None

    async def complete(
        self,
        task: TaskType,
        *,
        system: str,
        user: str,
        data: dict[str, str] | None = None,
        run_id: str | None = None,
        module: str | None = None,
    ) -> GatewayResult:
        """Run one chat call. Untrusted `data` is wrapped in delimited blocks."""
        route, routing_version = await self.route_for(task, module)
        model = self._model_override or route.primary
        if data:
            blocks = "\n".join(f"<data name={k}>\n{v}\n</data>" for k, v in data.items())
            user = f"{user}\n{blocks}"
        hit = self._cache.get(cache_key(task.value, model, system, user))
        if hit is not None:
            text, tin, tout = hit
            await self._log(
                LoggedCall(
                    task_type=task.value, model=model, tokens_in=tin,
                    tokens_out=tout, cost_usd=0.0, latency_ms=0, run_id=run_id,
                    routing_version=routing_version, cached=True,
                )
            )
            return GatewayResult(text=text, model=model, tokens_in=tin,
                                 tokens_out=tout, cost_usd=0.0, latency_ms=0)
        estimate = price_of(
            model, max(1, len(user.split())), route.token_limit,
            self._settings.model_prices,
        )
        await self._check_budget(run_id, estimate)
        try:
            raw = await self._adapter.complete(model, system, user)
            fallback_used = False
        except Exception:
            if not route.fallback or route.fallback == model:
                raise
            raw = await self._adapter.complete(route.fallback, system, user)
            model = route.fallback
            fallback_used = True
        cost = price_of(
            model, raw.tokens_in, raw.tokens_out, self._settings.model_prices
        )
        await self._record_spend(run_id, cost)
        await self._log(
            LoggedCall(
                task_type=task.value,
                model=model,
                tokens_in=raw.tokens_in,
                tokens_out=raw.tokens_out,
                cost_usd=cost,
                latency_ms=raw.latency_ms,
                run_id=run_id,
                fallback_used=fallback_used,
                routing_version=routing_version,
            )
        )
        await self._maybe_shadow(task, system, user, run_id, routing_version)
        self._cache.set(
            cache_key(task.value, model, system, user),
            (raw.text, raw.tokens_in, raw.tokens_out),
        )
        return GatewayResult(
            text=raw.text,
            model=model,
            tokens_in=raw.tokens_in,
            tokens_out=raw.tokens_out,
            cost_usd=cost,
            latency_ms=raw.latency_ms,
        )

    async def embed(self, texts: list[str], run_id: str | None = None) -> list[list[float]]:
        route, routing_version = await self.route_for(TaskType.EMBED)
        model = self._model_override or route.primary
        key = cache_key(TaskType.EMBED.value, model, "", "\n".join(texts))
        if key in self._embed_vectors:
            vectors = self._embed_vectors[key]
            tokens = sum(max(1, len(t.split())) for t in texts)
            await self._log(
                LoggedCall(
                    task_type=TaskType.EMBED.value, model=model, tokens_in=tokens,
                    tokens_out=0, cost_usd=0.0, latency_ms=0, run_id=run_id,
                    routing_version=routing_version, cached=True,
                )
            )
            return vectors
        tokens = sum(max(1, len(t.split())) for t in texts)
        await self._check_budget(
            run_id, price_of(model, tokens, 0, self._settings.model_prices)
        )
        vectors = await self._adapter.embed(model, texts, self._settings.embedding_dim)
        cost = price_of(model, tokens, 0, self._settings.model_prices)
        await self._record_spend(run_id, cost)
        await self._log(
            LoggedCall(
                task_type=TaskType.EMBED.value,
                model=model,
                tokens_in=tokens,
                tokens_out=0,
                cost_usd=cost,
                latency_ms=0,
                run_id=run_id,
                routing_version=routing_version,
            )
        )
        self._embed_vectors[key] = vectors
        return vectors

    async def complete_batch(self, calls: list[dict[str, Any]]) -> list[GatewayResult]:
        return [
            await self.complete(
                TaskType(call["task"]), system=call["system"], user=call["user"],
                data=call.get("data"), run_id=call.get("run_id"),
                module=call.get("module"),
            )
            for call in calls
        ]

    async def _check_budget(self, run_id: str | None, estimate: float) -> None:
        if self._session_factory is None:
            return
        async with self._session_factory() as session:
            await check_budget(session, run_id, estimate)

    async def _record_spend(self, run_id: str | None, cost: float) -> None:
        if self._session_factory is None:
            return
        async with self._session_factory() as session:
            await record_spend(session, run_id, cost)

    async def _maybe_shadow(
        self, task: TaskType, system: str, user: str,
        run_id: str | None, routing_version: int | None,
    ) -> None:
        """Shadow: a share of calls is also sent to a candidate model.

        The candidate output is stored for comparison and never returned.
        """
        candidate = self._settings.shadow_model
        if not candidate or random.random() >= self._settings.shadow_share:
            return
        try:
            raw = await self._adapter.complete(candidate, system, user)
        except Exception:
            return
        cost = price_of(
            candidate, raw.tokens_in, raw.tokens_out, self._settings.model_prices
        )
        await self._record_spend(run_id, cost)
        await self._log(
            LoggedCall(
                task_type=task.value, model=candidate, tokens_in=raw.tokens_in,
                tokens_out=raw.tokens_out, cost_usd=cost,
                latency_ms=raw.latency_ms, run_id=run_id,
                routing_version=routing_version, is_shadow=True,
            )
        )

    async def _log(self, call: LoggedCall) -> None:
        self.logged_calls.append(call)
        if self._session_factory is None:
            return
        from app.models.gateway import ModelCall

        async with self._session_factory() as session:
            session.add(
                ModelCall(
                    run_id=call.run_id,
                    task_type=call.task_type,
                    model=call.model,
                    tokens_in=call.tokens_in,
                    tokens_out=call.tokens_out,
                    cost_usd=call.cost_usd,
                    latency_ms=call.latency_ms,
                    fallback_used=call.fallback_used,
                    routing_version=call.routing_version,
                    cached=call.cached,
                    is_shadow=call.is_shadow,
                )
            )
            await session.commit()
