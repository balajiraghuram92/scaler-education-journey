"""Gateway provider tests: OpenAI header modes, Anthropic adapter, routing.

All HTTP goes through httpx.MockTransport; no test makes a network call.
"""
from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from app.gateway.adapters import (
    AdapterResult,
    AnthropicMessagesAdapter,
    FakeAdapter,
    ModelAdapter,
    OpenAICompatAdapter,
    RoutedAdapter,
    price_of,
)
from app.gateway.gateway import ModelGateway
from app.gateway.routing import Route
from app.gateway.tasks import TaskType
from app.settings import Settings


def _canned_openai_reply() -> dict:
    return {
        "choices": [{"message": {"content": "hello there"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 7},
    }


def _canned_anthropic_reply() -> dict:
    return {
        "content": [
            {"type": "text", "text": "part one. "},
            {"type": "tool_use", "id": "t1", "name": "x", "input": {}},
            {"type": "text", "text": "part two."},
        ],
        "usage": {"input_tokens": 3, "output_tokens": 9},
    }


def _recording_transport(
    seen: list[httpx.Request], payload: dict
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


def test_openai_adapter_default_bearer_header() -> None:
    seen: list[httpx.Request] = []
    adapter = OpenAICompatAdapter(
        base_url="https://example.test/openai/v1",
        api_key="k",
        transport=_recording_transport(seen, _canned_openai_reply()),
    )
    result = asyncio.run(adapter.complete("gpt-x", "sys", "hi"))
    assert len(seen) == 1
    assert seen[0].headers["Authorization"] == "Bearer k"
    assert "api-key" not in seen[0].headers
    assert str(seen[0].url).endswith("/chat/completions")
    assert result.text == "hello there"
    assert (result.tokens_in, result.tokens_out) == (5, 7)


def test_openai_adapter_api_key_header_mode() -> None:
    seen: list[httpx.Request] = []
    adapter = OpenAICompatAdapter(
        base_url="https://example.test/openai/v1",
        api_key="k",
        key_header="api-key",
        transport=_recording_transport(seen, _canned_openai_reply()),
    )
    asyncio.run(adapter.complete("gpt-x", "sys", "hi"))
    assert seen[0].headers["api-key"] == "k"
    assert "authorization" not in seen[0].headers


def test_anthropic_adapter_request_and_reply_shape() -> None:
    seen: list[httpx.Request] = []
    adapter = AnthropicMessagesAdapter(
        base_url="https://example.test/anthropic",
        api_key="k",
        version="2023-06-01",
        max_tokens=4096,
        transport=_recording_transport(seen, _canned_anthropic_reply()),
    )
    result = asyncio.run(adapter.complete("claude-x", "be brief", "summarise"))
    assert str(seen[0].url) == "https://example.test/anthropic/v1/messages"
    assert seen[0].headers["x-api-key"] == "k"
    assert seen[0].headers["anthropic-version"] == "2023-06-01"
    body = json.loads(seen[0].content.decode())
    assert body["system"] == "be brief"
    assert body["max_tokens"] == 4096
    assert body["messages"] == [{"role": "user", "content": "summarise"}]
    assert result.text == "part one. part two."
    assert (result.tokens_in, result.tokens_out) == (3, 9)


def test_anthropic_adapter_embed_raises() -> None:
    adapter = AnthropicMessagesAdapter(
        base_url="https://example.test/anthropic",
        api_key="k",
        version="2023-06-01",
        max_tokens=4096,
    )
    with pytest.raises(NotImplementedError):
        asyncio.run(adapter.embed("claude-x", ["hi"], 64))


def test_routed_adapter_selects_by_prefix() -> None:
    default = FakeAdapter(default="from-default")
    claude = FakeAdapter(default="from-Muse")
    routed = RoutedAdapter(default=default, by_prefix=[("claude-", claude)])

    async def run() -> tuple[str, str]:
        first = await routed.complete("claude-x", "", "hi")
        second = await routed.complete("gpt-x", "", "hi")
        return first.text, second.text

    assert asyncio.run(run()) == ("from-Muse", "from-default")
    assert [model for model, _ in claude.calls] == ["claude-x"]
    assert [model for model, _ in default.calls] == ["gpt-x"]


class _FailingAdapter:
    """Adapter whose chat path always fails, for the fallback test."""

    async def complete(self, model: str, system: str, user: str) -> AdapterResult:
        raise RuntimeError("primary provider is down")

    async def embed(self, model: str, texts: list[str], dim: int) -> list[list[float]]:
        raise RuntimeError("primary provider is down")


class _StaticRouteGateway(ModelGateway):
    """Gateway with a fixed cross-provider route (no database needed)."""

    def __init__(self, settings: Settings, adapter: ModelAdapter, route: Route) -> None:
        super().__init__(settings=settings, adapter=adapter)
        self._test_route = route

    async def route_for(
        self, task: TaskType, module: str | None = None
    ) -> tuple[Route, int | None]:
        del task, module
        return self._test_route, None


def test_gateway_fallback_crosses_providers() -> None:
    claude = FakeAdapter(default="claude-text")
    routed: ModelAdapter = RoutedAdapter(
        default=_FailingAdapter(),
        by_prefix=[("claude-", claude)],
    )
    gateway = _StaticRouteGateway(
        settings=Settings(),
        adapter=routed,
        route=Route(primary="gpt-x", fallback="claude-x", token_limit=8000, mode="SYNC"),
    )
    result = asyncio.run(gateway.complete(TaskType.SYNTHESIS, system="s", user="u"))
    assert result.text == "claude-text"
    assert result.model == "claude-x"
    assert gateway.logged_calls[0].fallback_used is True


def test_price_of_prefers_overrides_then_table() -> None:
    override = price_of("tessera-small", 1000, 1000, {"tessera-small": (1.0, 2.0)})
    assert override == (1000 * 1.0 + 1000 * 2.0) / 1000.0
    assert price_of("tessera-small", 1000, 1000) != override
    assert price_of("tessera-small", 1000, 1000) == (1000 * 0.0005 + 1000 * 0.0015) / 1000.0


def test_default_settings_stay_offline() -> None:
    settings = Settings()
    assert settings.model_adapter == "fake"
    assert settings.openai_api_key_header == "bearer"
    assert settings.anthropic_base_url == ""
