"""LlamaApiClient tests with a fake HTTP transport (no real network calls)."""

from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal

import httpx
import pytest

from app.services.llama_api_client import ChatPromptMessage, LlamaApiClient
from app.settings import LlamaApiSettings


def _options(**overrides: object) -> LlamaApiSettings:
    values: dict = {"LlamaApi__ApiKey": "test-key"}
    values.update(overrides)
    return LlamaApiSettings(**values)


def _client(
    handler: Callable[[httpx.Request], httpx.Response], **option_overrides: object
) -> LlamaApiClient:
    options = _options(**option_overrides)
    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport, base_url="https://api.llama.com/v1/")
    return LlamaApiClient(options=options, is_production=False, http_client=http_client)


@pytest.mark.asyncio
async def test_success_parses_reply_usage_and_cost() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "Hi there"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            },
        )

    client = _client(
        handler,
        LlamaApi__PricePerMillionInputTokensUsd=Decimal("1.0"),
        LlamaApi__PricePerMillionOutputTokensUsd=Decimal("2.0"),
    )
    result = await client.generate_completion(
        [ChatPromptMessage(role="system", content="sys"), ChatPromptMessage(role="user", content="hi")]
    )

    assert seen["method"] == "POST"
    assert seen["path"] == "/v1/chat/completions"
    assert seen["auth"] == "Bearer test-key"
    assert seen["body"]["model"] == "Llama-4-Maverick-17B-128E-Instruct-FP8"
    assert seen["body"]["temperature"] == 0.7
    assert seen["body"]["messages"] == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "hi"},
    ]
    assert result.reply_content == "Hi there"
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5
    assert result.usage_estimated is False
    assert result.estimated_cost_usd == Decimal("0.000020")
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_missing_usage_falls_back_to_character_estimation() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    result = await _client(handler).generate_completion(
        [ChatPromptMessage(role="user", content="123456789")]
    )

    # prompt "123456789\n" (10 chars) -> 3 tokens; "ok" -> 1 token.
    assert result.usage_estimated is True
    assert result.prompt_tokens == 3
    assert result.completion_tokens == 1


@pytest.mark.asyncio
async def test_error_status_raises_with_status_and_reason() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="slow down")

    with pytest.raises(RuntimeError, match="Llama API error: 429"):
        await _client(handler).generate_completion([ChatPromptMessage(role="user", content="hi")])


@pytest.mark.asyncio
async def test_missing_key_returns_mock_in_development() -> None:
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("no HTTP call expected")

    client = _client(handler, LlamaApi__ApiKey="")
    result = await client.generate_completion([ChatPromptMessage(role="user", content="hi")])

    assert "not configured" in result.reply_content
    assert result.usage_estimated is True
    assert result.prompt_tokens >= 1
    assert result.completion_tokens >= 1


@pytest.mark.asyncio
async def test_missing_key_raises_in_production() -> None:
    options = _options(LlamaApi__ApiKey="")
    client = LlamaApiClient(options=options, is_production=True)

    with pytest.raises(RuntimeError, match="not configured"):
        await client.generate_completion([ChatPromptMessage(role="user", content="hi")])
