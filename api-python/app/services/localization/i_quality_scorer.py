"""Ported from api/Services/Localization/IQualityScorer.cs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class QualityScoreResult:
    score: int
    flagged_issues: list[str]
    input_tokens: int = 0
    output_tokens: int = 0


class IQualityScorer(Protocol):
    @property
    def is_configured(self) -> bool: ...

    async def score_async(
        self, source_text: str, target_text: str, target_locale: str
    ) -> QualityScoreResult: ...
