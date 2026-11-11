"""GoogleTranslateProviderService tests with a fake HTTP transport.

No C# equivalent; pins the request shape, the [MOCK-XX] fallback rules and
the production failure behavior from GoogleTranslateProviderService.cs.
"""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from app.services.localization.google_translate_provider_service import (
    GoogleTranslateProviderService,
)
from app.settings import GoogleTranslateSettings


def _options(**overrides: object) -> GoogleTranslateSettings:
    values: dict = {"GoogleTranslate__ApiKey": "test-key"}
    values.update(overrides)
    return GoogleTranslateSettings(**values)


def _provider(
    handler: Callable[[httpx.Request], httpx.Response],
    is_production: bool = False,
    **option_overrides: object,
) -> GoogleTranslateProviderService:
    options = _options(**option_overrides)
    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    return GoogleTranslateProviderService(
        options=options, is_production=is_production, http_client=http_client
    )


@pytest.mark.asyncio
async def test_success_posts_expected_payload_and_returns_translation() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={"data": {"translations": [{"translatedText": "Hallo Welt"}]}},
        )

    result = await _provider(handler).translate_async(
        "Hello world", "en-US", "de-DE"
    )

    assert seen["method"] == "POST"
    assert seen["url"].startswith(
        "https://translation.googleapis.com/language/translate/v2?key="
    )
    assert "key=test-key" in seen["url"]
    assert seen["body"] == {
        "q": ["Hello world"],
        "target": "de",
        "source": "en",
        "format": "text",
    }
    assert result == "Hallo Welt"


@pytest.mark.asyncio
async def test_missing_key_returns_mock_in_development() -> None:
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("no HTTP call expected")

    result = await _provider(handler, GoogleTranslate__ApiKey="").translate_async(
        "Hello world", "en-US", "de-DE"
    )
    assert result == "[MOCK-DE-DE] Hello world"


@pytest.mark.asyncio
async def test_missing_key_raises_in_production() -> None:
    options = _options(GoogleTranslate__ApiKey="")
    provider = GoogleTranslateProviderService(
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
        return httpx.Response(200, json={"data": {"translations": [{}]}})

    result = await _provider(handler, is_production=True).translate_async(
        "Hello world", "en-US", "de-DE"
    )
    # A missing node falls back to the mock even in production, as in C#.
    assert result == "[MOCK-DE-DE] Hello world"
