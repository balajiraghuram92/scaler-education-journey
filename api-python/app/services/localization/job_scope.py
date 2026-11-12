"""Ported from api/Services/Localization/JobScope.cs."""

from __future__ import annotations

from collections.abc import Sequence

from ...models.localization.localization_string import LocalizationString
from ...models.localization.localization_translation import LocalizationTranslation


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


class JobScope:
    """One definition of "open" and "vendor-reviewed" (CONTRACT 2.5)."""

    VENDOR_SOURCE = "Marketplace"
    MACHINE_SOURCE = "AI"

    @staticmethod
    def is_open(item: LocalizationString, locale_code: str) -> bool:
        translation = next(
            (t for t in item.translations if t.locale_code == locale_code),
            None,
        )
        return (
            translation is None
            or _is_blank(translation.target_text)
            or translation.stage != "Approved"
        )

    @staticmethod
    def is_vendor_reviewed(
        translation: LocalizationTranslation | None,
    ) -> bool:
        return (
            translation is not None
            and translation.translation_source == JobScope.VENDOR_SOURCE
            and not _is_blank(translation.target_text)
        )

    @staticmethod
    def completed_percent(
        strings: Sequence[LocalizationString],
        locale_code: str,
        string_count: int,
        job_status: str,
    ) -> int:
        if job_status == "Approved":
            return 100
        if string_count == 0:
            return 0
        done = 0
        for item in strings:
            translation = next(
                (t for t in item.translations if t.locale_code == locale_code),
                None,
            )
            if (
                translation is not None
                and translation.stage != "Approved"
                and JobScope.is_vendor_reviewed(translation)
            ):
                done += 1
        # C# truncating int division on non-negative values is round-down.
        return min((done * 100) // string_count, 100)
