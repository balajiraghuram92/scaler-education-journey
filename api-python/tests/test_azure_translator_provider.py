"""AzureTranslatorProviderService tests with a fake HTTP transport.

No C# equivalent; pins the request shape, the [MOCK-XX] fallback rules and
the production failure behavior from AzureTranslatorProviderService.cs.
"""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from app.services.localization.azure_translator_provider_service import (
    AzureTranslatorProviderService,
)
from app.settings import AzureTranslatorSettings


def _options(**overrides: object) -> AzureTranslatorSettings:
    values: dict = {"AzureTranslator__Key": "test-key"}
    values.update(overrides)
    return AzureTranslatorSettings(**values)


def _provider(
    handler: Callable[[httpx.Request], httpx.Response],
    is_production: bool = False,
    **option_overrides: object,
) -> AzureTranslatorProviderService:
    options = _options(**option_overrides)
    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    return AzureTranslatorProviderService(
        options=options, is_production=is_production, http_client=http_client
    )


@pytest.mark.asyncio
async def test_success_posts_expected_payload_and_returns_translation() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        seen["key"] = request.headers.get("ocp-apim-subscription-key")
        seen["region"] = request.headers.get("ocp-apim-subscription-region")
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json=[{"translations": [{"text": "Hallo Welt", "to": "de-DE"}]}],
        )

    result = await _provider(handler).translate_async(
        "Hello world", "en-US", "de-DE"
    )

    assert seen["method"] == "POST"
    assert seen["url"].startswith(
        "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
    )
    assert "from=en-US" in seen["url"]
    assert "to=de-DE" in seen["url"]
    assert "test-key" not in seen["url"]
    assert seen["key"] == "test-key"
    assert seen["region"] is None
    assert seen["body"] == [{"Text": "Hello world"}]
    assert result == "Hallo Welt"


@pytest.mark.asyncio
async def test_region_header_sent_when_configured() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["region"] = request.headers.get("ocp-apim-subscription-region")
        return httpx.Response(
            200, json=[{"translations": [{"text": "Bonjour", "to": "fr-FR"}]}]
        )

    result = await _provider(
        handler, AzureTranslator__Region="westeurope"
    ).translate_async("Hello", "en-US", "fr-FR")

    assert seen["region"] == "westeurope"
    assert result == "Bonjour"


@pytest.mark.asyncio
async def test_missing_key_returns_mock_in_development() -> None:
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("no HTTP call expected")

    result = await _provider(handler, AzureTranslator__Key="").translate_async(
        "Hello world", "en-US", "de-DE"
    )
    assert result == "[MOCK-DE-DE] Hello world"


@pytest.mark.asyncio
async def test_missing_key_raises_in_production() -> None:
    options = _options(AzureTranslator__Key="")
    provider = AzureTranslatorProviderService(
        options=options, is_production=True
    )
    with pytest.raises(RuntimeError, match="not configured in production"):
        await provider.translate_async("Hello world", "en-US", "de-DE")


@pytest.mark.asyncio
async def test_error_status_returns_mock_in_development() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="bad key")

    result = await _provider(handler).translate_async(
        "Hello world", "en-US", "fr-FR"
    )
    assert result == "[MOCK-FR-FR] Hello world"


@pytest.mark.asyncio
async def test_error_status_raises_in_production() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="bad key")

    with pytest.raises(httpx.HTTPStatusError):
        await _provider(handler, is_production=True).translate_async(
            "Hello world", "en-US", "fr-FR"
        )


@pytest.mark.asyncio
async def test_missing_translated_text_returns_mock() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"translations": [{}]}])

    result = await _provider(handler, is_production=True).translate_async(
        "Hello world", "en-US", "de-DE"
    )
    # A missing node falls back to the mock even in production, as in C#.
    assert result == "[MOCK-DE-DE] Hello world"
