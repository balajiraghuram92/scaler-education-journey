"""Ported from api/Services/Localization/LocalizationProjectService.cs."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.localization.localization_project import LocalizationProject
from ...schemas.localization_dtos import LocalizationLocaleDto, LocalizationProjectDto
from .localization_exceptions import LocalizationProjectNotFoundException


class LocalizationProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_project_async(self, slug: str) -> LocalizationProjectDto:
        project = (
            await self._session.execute(
                select(LocalizationProject)
                .options(selectinload(LocalizationProject.locales))
                .where(LocalizationProject.slug == slug)
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(slug)
        locales = [
            LocalizationLocaleDto(
                id=locale.id,
                locale_code=locale.locale_code,
                display_name=locale.display_name,
            )
            for locale in sorted(project.locales, key=lambda item: item.id)
        ]
        return LocalizationProjectDto(
            id=project.id,
            slug=project.slug,
            name=project.name,
            source_locale=project.source_locale,
            created_at=project.created_at,
            locales=locales,
        )

    async def get_projects_async(self) -> list[LocalizationProjectDto]:
        projects = (
            await self._session.execute(
                select(LocalizationProject)
                .options(selectinload(LocalizationProject.locales))
                .order_by(LocalizationProject.id)
            )
        ).scalars().all()
        result: list[LocalizationProjectDto] = []
        for project in projects:
            locales = [
                LocalizationLocaleDto(
                    id=locale.id,
                    locale_code=locale.locale_code,
                    display_name=locale.display_name,
                )
                for locale in sorted(project.locales, key=lambda item: item.id)
            ]
            result.append(
                LocalizationProjectDto(
                    id=project.id,
                    slug=project.slug,
                    name=project.name,
                    source_locale=project.source_locale,
                    created_at=project.created_at,
                    locales=locales,
                )
            )
        return result
