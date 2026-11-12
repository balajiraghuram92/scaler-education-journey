"""Ported from api/Services/Localization/QpsScoringService.cs.

Thin client over the localization-ai /qps-score endpoint.
Contains no scoring rubric; that stays in the Python service.
Raises LocalizationAiException when the judge falls back without a score.
"""

from __future__ import annotations

from .i_quality_scorer import QualityScoreResult
from .localization_ai_client import (
    NOT_CONFIGURED_MESSAGE,
    LocalizationAiClient,
    LocalizationAiException,
)


class QpsScoringService:
    def __init__(self, client: LocalizationAiClient | None = None) -> None:
        self._client = client

    @property
    def is_configured(self) -> bool:
        return self._client is not None and self._client.is_configured

    async def score_async(
        self, source_text: str, target_text: str, target_locale: str
    ) -> QualityScoreResult:
        if self._client is None:
            raise NotImplementedError(NOT_CONFIGURED_MESSAGE)
        response = await self._client.score_qps_async(
            source_text, target_text, target_locale
        )
        if response.score is None:
            exc = LocalizationAiException(
                "The QPS judge fell back without producing a score."
            )
            exc.input_tokens = response.input_tokens
            exc.output_tokens = response.output_tokens
            raise exc
        return QualityScoreResult(
            response.score,
            response.flagged_issues,
            response.input_tokens,
            response.output_tokens,
        )
