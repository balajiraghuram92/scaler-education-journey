"""Ported from api/Services/Localization/GoogleTranslateProviderService.cs."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import httpx

from ...settings import GoogleTranslateSettings, get_environment, get_settings

logger = logging.getLogger(__name__)


class GoogleTranslateProviderService:
    def __init__(
        self,
        options: GoogleTranslateSettings | None = None,
        is_production: bool | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._options = options or get_settings().google_translate
        if is_production is None:
            is_production = get_environment().lower() == "production"
        self._is_production = is_production
        self._http_client = http_client

    async def translate_async(
        self, source_text: str, source_locale: str, target_locale: str
    ) -> str:
        mock = f"[MOCK-{target_locale.upper()}] {source_text}"
        if not self._options.api_key or not self._options.api_key.strip():
            if self._is_production:
                raise RuntimeError(
                    "Google Translate API key is not configured in production environment."
                )
            logger.warning(
                "Google Translate API key not set. Using mock translation in non-production."
            )
            return mock

        try:
            target_lang = target_locale.split("-")[0]
            source_lang = source_locale.split("-")[0]
            url = (
                "https://translation.googleapis.com/language/translate/v2"
                f"?key={quote(self._options.api_key, safe='')}"
            )
            payload = {
                "q": [source_text],
                "target": target_lang,
                "source": source_lang,
                "format": "text",
            }
            client = self._http_client
            owns_client = client is None
            if client is None:
                client = httpx.AsyncClient(follow_redirects=True)
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                root: Any = response.json()
            finally:
                if owns_client and client is not None:
                    await client.aclose()
            # Mirrors json?["data"]?["translations"]?[0]?["translatedText"]:
            # a missing node falls back to the mock, a wrong-shaped node raises
            # into the handler below (mock in non-prod, rethrow in prod).
            if not isinstance(root, dict):
                raise ValueError("unexpected translate payload")
            data = root.get("data")
            if data is None:
                return mock
            if not isinstance(data, dict):
                raise ValueError("unexpected translate payload")
            translations = data.get("translations")
            if translations is None:
                return mock
            if not isinstance(translations, list):
                raise ValueError("unexpected translate payload")
            first = translations[0]
            if not isinstance(first, dict):
                raise ValueError("unexpected translate payload")
            translated_text = first.get("translatedText")
            if translated_text is None:
                return mock
            if not isinstance(translated_text, str):
                raise ValueError("unexpected translate payload")
            return translated_text
        except Exception as exc:
            logger.error(
                "Google Translate API call failed for target locale %s: %s",
                target_locale,
                exc,
            )
            if not self._is_production:
                return mock
            raise
