"""Ported from api/Services/Localization/MtOptimizeService.cs.

Thin client over the localization-ai /translate-and-optimize endpoint.
Contains no prompt, scoring or threshold logic; that stays in the Python service.
"""

from __future__ import annotations

from .localization_ai_client import (
    NOT_CONFIGURED_MESSAGE,
    AiGlossaryTermDto,
    LocalizationAiClient,
    OptimizeTranslationResult,
)


class MtOptimizeService:
    def __init__(self, client: LocalizationAiClient | None = None) -> None:
        self._client = client

    async def optimize_async(
        self, raw_translation: str, project_slug: str, target_locale: str
    ) -> str:
        result = await self.optimize_detailed_async(
            raw_translation, raw_translation, project_slug, target_locale, []
        )
        return result.optimized_translation

    async def optimize_detailed_async(
        self,
        source_text: str,
        raw_translation: str,
        project_slug: str,
        target_locale: str,
        glossary_terms: list[AiGlossaryTermDto],
    ) -> OptimizeTranslationResult:
        if self._client is None:
            raise NotImplementedError(NOT_CONFIGURED_MESSAGE)
        return await self._client.translate_and_optimize_async(
            source_text,
            raw_translation,
            target_locale,
            project_slug,
            glossary_terms,
        )
