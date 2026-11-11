"""Ported from api/Services/Localization/LocalizationStringService.cs."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.localization.localization_project import LocalizationProject
from ...models.localization.localization_string import LocalizationString
from ...models.localization.localization_translation import LocalizationTranslation
from ...schemas.localization_dtos import (
    LocalizationStringRowDto,
    UpdateTranslationRequest,
)
from .localization_exceptions import (
    LocalizationProjectNotFoundException,
    LocalizationStringNotFoundException,
)


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


class LocalizationStringService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_strings_async(
        self, project_slug: str, locale_code: str
    ) -> list[LocalizationStringRowDto]:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        # Filtered eager load mirrors Include(s => s.Translations.Where(...)).
        strings = (
            await self._session.execute(
                select(LocalizationString)
                .options(
                    selectinload(LocalizationString.translations.and_(
                        LocalizationTranslation.locale_code == locale_code
                    ))
                )
                .where(LocalizationString.project_id == project.id)
                .order_by(LocalizationString.id)
            )
        ).scalars().all()
        result: list[LocalizationStringRowDto] = []
        for item in strings:
            translation = item.translations[0] if item.translations else None
            result.append(
                LocalizationStringRowDto(
                    string_id=item.id,
                    key=item.key,
                    source_text=item.source_text,
                    locale_code=locale_code,
                    target_text=translation.target_text if translation else None,
                    stage=translation.stage if translation else "New",
                    translation_source=translation.translation_source
                    if translation
                    else "Manual",
                    qps_score=translation.qps_score if translation else None,
                    needs_review=translation.needs_review if translation else False,
                    updated_at=translation.updated_at if translation else None,
                    raw_mt_text=translation.raw_mt_text if translation else None,
                    raw_mt_qps_score=translation.raw_mt_qps_score
                    if translation
                    else None,
                )
            )
        return result

    async def update_translation_async(
        self,
        project_slug: str,
        string_id: int,
        locale_code: str,
        request: UpdateTranslationRequest,
    ) -> LocalizationStringRowDto:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        item = (
            await self._session.execute(
                select(LocalizationString).where(
                    LocalizationString.id == string_id,
                    LocalizationString.project_id == project.id,
                )
            )
        ).scalar_one_or_none()
        if item is None:
            raise LocalizationStringNotFoundException(string_id)
        translation = (
            await self._session.execute(
                select(LocalizationTranslation).where(
                    LocalizationTranslation.string_id == string_id,
                    LocalizationTranslation.locale_code == locale_code,
                )
            )
        ).scalar_one_or_none()
        has_target = not _is_blank(request.target_text)
        if translation is None:
            translation = LocalizationTranslation(
                string_id=string_id,
                locale_code=locale_code,
                target_text=request.target_text,
                stage="Translated" if has_target else "New",
                translation_source="Manual",
                needs_review=False,
                updated_at=datetime.now(UTC),
            )
            self._session.add(translation)
        else:
            translation.target_text = request.target_text
            translation.translation_source = "Manual"
            translation.stage = "Translated" if has_target else "New"
            translation.updated_at = datetime.now(UTC)
        await self._session.flush()
        return LocalizationStringRowDto(
            string_id=item.id,
            key=item.key,
            source_text=item.source_text,
            locale_code=locale_code,
            target_text=translation.target_text,
            stage=translation.stage,
            translation_source=translation.translation_source,
            qps_score=translation.qps_score,
            needs_review=translation.needs_review,
            updated_at=translation.updated_at,
            raw_mt_text=translation.raw_mt_text,
            raw_mt_qps_score=translation.raw_mt_qps_score,
        )
