"""LocalizationAiClient contract tests with a fake HTTP transport.

No C# equivalent (the C# suite covers the client through the workflow
tests); these pin the client's own error mapping and request shape.
"""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from app.services.localization.localization_ai_client import (
    AiGlossaryTermDto,
    LocalizationAiClient,
    LocalizationAiException,
)
from app.settings import LocalizationAiSettings


def _options(**overrides: object) -> LocalizationAiSettings:
    values: dict = {
        "LocalizationAi__BaseUrl": "http://ai/",
        "LocalizationAi__SharedSecret": "test-secret",
    }
    values.update(overrides)
    return LocalizationAiSettings(**values)


def _client(
    handler: Callable[[httpx.Request], httpx.Response],
    **option_overrides: object,
) -> LocalizationAiClient:
    options = _options(**option_overrides)
    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport, base_url="http://ai/")
    return LocalizationAiClient(options=options, http_client=http_client)


@pytest.mark.asyncio
async def test_translate_and_optimize_posts_camel_case_body_and_parses_result() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["api_key"] = request.headers.get("x-api-key")
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={
                "optimizedTranslation": "Hallo Welt",
                "cacheHit": True,
                "checks": {"glossary": True},
                "inputTokens": 10,
                "outputTokens": 5,
                "tokensUsed": 15,
                "latencyMs": 3,
                "fallback": False,
            },
        )

    result = await _client(handler).translate_and_optimize_async(
        "Hello world",
        "Hallo world",
        "de-DE",
        "test-proj",
        [AiGlossaryTermDto(source="Hello", target="Hallo")],
    )

    assert seen["method"] == "POST"
    assert seen["path"] == "/translate-and-optimize"
    assert seen["api_key"] == "test-secret"
    assert seen["body"] == {
        "rawMtText": "Hallo world",
        "sourceText": "Hello world",
        "targetLocale": "de-DE",
        "projectSlug": "test-proj",
        "glossaryTerms": [{"source": "Hello", "target": "Hallo"}],
    }
    assert result.optimized_translation == "Hallo Welt"
    assert result.cache_hit is True
    assert result.checks == {"glossary": True}
    assert result.input_tokens == 10
    assert result.output_tokens == 5
    assert result.tokens_used == 15
    assert result.latency_ms == 3
    assert result.fallback is False


@pytest.mark.asyncio
async def test_score_qps_allows_null_score() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "score": None,
                "flaggedIssues": [],
                "tokensUsed": 0,
                "latencyMs": 1,
                "fallback": True,
            },
        )

    result = await _client(handler).score_qps_async("s", "t", "de-DE")
    assert result.score is None
    assert result.fallback is True


@pytest.mark.asyncio
async def test_auto_route_posts_score_threshold_and_null_checks() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"needsReview": True, "reasons": ["low"]})

    result = await _client(handler).auto_route_async(60, 70, None)
    assert seen["body"] == {
        "qpsScore": 60,
        "projectThreshold": 70,
        "checks": None,
    }
    assert result.needs_review is True
    assert result.reasons == ["low"]


@pytest.mark.asyncio
async def test_run_eval_parses_nullable_metrics() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "evalRunId": 7,
                "avgCometKiwi": 0.81,
                "avgQpsScore": None,
                "glossaryAdherenceRate": 1.0,
                "placeholderPreservationRate": None,
                "cacheHitRate": 0.25,
                "avgLatencyMs": None,
                "totalCostUsd": 0.5,
                "tokensUsed": 100,
                "fallbackCount": 2,
                "promptVersion": "mt_optimize_v1",
            },
        )

    result = await _client(handler).run_eval_async("test-proj", "legacy+optimize")
    assert result.eval_run_id == 7
    assert result.avg_comet_kiwi == 0.81
    assert result.avg_qps_score is None
    assert result.prompt_version == "mt_optimize_v1"


@pytest.mark.asyncio
async def test_not_configured_raises_not_implemented_without_http_call() -> None:
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("no HTTP call expected")

    client = _client(handler, LocalizationAi__BaseUrl="")
    assert client.is_configured is False
    with pytest.raises(NotImplementedError, match="not configured"):
        await client.score_comet_async("s", "t", "de-DE")


@pytest.mark.asyncio
async def test_error_status_raises_with_status_and_reason() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    with pytest.raises(LocalizationAiException, match=r"localization-ai error: 500"):
        await _client(handler).score_qps_async("s", "t", "de-DE")


@pytest.mark.asyncio
async def test_unreadable_payload_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json{")

    with pytest.raises(LocalizationAiException, match="unreadable payload"):
        await _client(handler).auto_route_async(60, 70, None)


@pytest.mark.asyncio
async def test_wrong_shaped_payload_raises_unreadable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"score": "eighty-five"})

    with pytest.raises(LocalizationAiException, match="unreadable payload"):
        await _client(handler).score_qps_async("s", "t", "de-DE")


@pytest.mark.asyncio
async def test_null_payload_raises_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="null")

    with pytest.raises(LocalizationAiException, match="empty payload"):
        await _client(handler).run_eval_async("test-proj", "legacy-only")


@pytest.mark.asyncio
async def test_transport_error_raises_wrapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(LocalizationAiException, match=r"qps-score failed"):
        await _client(handler).score_qps_async("s", "t", "de-DE")


@pytest.mark.asyncio
async def test_no_shared_secret_sends_no_api_key_header() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["api_key"] = request.headers.get("x-api-key")
        return httpx.Response(
            200, json={"score": 0.5, "available": True, "latencyMs": 1}
        )

    result = await _client(handler, LocalizationAi__SharedSecret="").score_comet_async(
        "s", "t", "de-DE"
    )
    assert seen["api_key"] is None
    assert result.score == 0.5
    assert result.available is True
