"""Ported from api/Services/Localization/ITranslationProvider.cs."""

from __future__ import annotations

from typing import Protocol


class ITranslationProvider(Protocol):
    async def translate_async(
        self, source_text: str, source_locale: str, target_locale: str
    ) -> str: ...
