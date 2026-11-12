"""Ported from api/Services/Localization/AzureTranslatorProviderService.cs."""

from __future__ import annotations

import logging
from urllib.parse import quote

import httpx

from ...settings import AzureTranslatorSettings, get_environment, get_settings

logger = logging.getLogger(__name__)


class AzureTranslatorProviderService:
    def __init__(
        self,
        options: AzureTranslatorSettings | None = None,
        is_production: bool | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._options = options or get_settings().azure_translator
        if is_production is None:
            is_production = get_environment().lower() == "production"
        self._is_production = is_production
        self._http_client = http_client

    async def translate_async(
        self, source_text: str, source_locale: str, target_locale: str
    ) -> str:
        # C# reads _options.ApiKey here, but AzureTranslatorOptions declares
        # Key (the C# does not compile as written); the port reads key (env
        # AzureTranslator__Key) per the options class and CONTRACT.
        mock = f"[MOCK-{target_locale.upper()}] {source_text}"
        if not self._options.key or not self._options.key.strip():
            if self._is_production:
                raise RuntimeError(
                    "Azure Translator API key is not configured in production environment."
                )
            logger.warning(
                "Azure Translator API key not set. Using mock translation in non-production."
            )
            return mock

        try:
            endpoint = self._options.endpoint.rstrip("/")
            url = (
                f"{endpoint}/translate?api-version=3.0"
                f"&from={quote(source_locale, safe='')}"
                f"&to={quote(target_locale, safe='')}"
            )
            headers = {"Ocp-Apim-Subscription-Key": self._options.key}
            if self._options.region and self._options.region.strip():
                headers["Ocp-Apim-Subscription-Region"] = self._options.region
            body = [{"Text": source_text}]
            client = self._http_client
            owns_client = client is None
            if client is None:
                client = httpx.AsyncClient(follow_redirects=True)
            try:
                response = await client.post(url, json=body, headers=headers)
                response.raise_for_status()
                root = response.json()
            finally:
                if owns_client and client is not None:
                    await client.aclose()
            # Mirrors json?[0]?["translations"]?[0]?["text"]: a missing node
            # falls back to the mock, a wrong-shaped node raises into the
            # handler below (mock in non-prod, rethrow in prod).
            if not isinstance(root, list):
                raise ValueError("unexpected translate payload")
            first = root[0]
            if not isinstance(first, dict):
                raise ValueError("unexpected translate payload")
            translations = first.get("translations")
            if translations is None:
                return mock
            if not isinstance(translations, list):
                raise ValueError("unexpected translate payload")
            first_translation = translations[0]
            if not isinstance(first_translation, dict):
                raise ValueError("unexpected translate payload")
            translated_text = first_translation.get("text")
            if translated_text is None:
                return mock
            if not isinstance(translated_text, str):
                raise ValueError("unexpected translate payload")
            return translated_text
        except Exception as exc:
            logger.error(
                "Azure Translator API call failed for target locale %s: %s",
                target_locale,
                exc,
            )
            if not self._is_production:
                return mock
            raise
