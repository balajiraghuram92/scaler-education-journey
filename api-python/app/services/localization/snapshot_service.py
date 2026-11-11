"""Ported from api/Services/Localization/SnapshotService.cs."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.localization.build_snapshot import BuildSnapshot
from ...models.localization.build_snapshot_locale_count import (
    BuildSnapshotLocaleCount,
)
from ...models.localization.localization_project import LocalizationProject
from ...models.localization.localization_string import LocalizationString
from ...schemas.localization_dtos import BuildSnapshotDto, BuildSnapshotLocaleCountDto
from .localization_exceptions import LocalizationProjectNotFoundException


class SnapshotService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_snapshots_async(
        self, project_slug: str
    ) -> list[BuildSnapshotDto]:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        snapshots = (
            await self._session.execute(
                select(BuildSnapshot)
                .options(selectinload(BuildSnapshot.locale_counts))
                .where(BuildSnapshot.project_id == project.id)
                .order_by(BuildSnapshot.created_at.desc())
            )
        ).scalars().all()
        return [
            BuildSnapshotDto(
                id=snapshot.id,
                snapshot_identifier=snapshot.snapshot_identifier,
                source_revision=snapshot.source_revision,
                localization_revision=snapshot.localization_revision,
                config=snapshot.config,
                created_at=snapshot.created_at,
                locale_counts=[
                    BuildSnapshotLocaleCountDto(
                        locale_code=count.locale_code,
                        approved_count=count.approved_count,
                    )
                    for count in sorted(
                        snapshot.locale_counts, key=lambda item: item.locale_code
                    )
                ],
            )
            for snapshot in snapshots
        ]

    async def cut_snapshot_async(self, project_slug: str) -> BuildSnapshotDto:
        project = (
            await self._session.execute(
                select(LocalizationProject)
                .options(
                    selectinload(LocalizationProject.locales),
                    selectinload(LocalizationProject.strings).selectinload(
                        LocalizationString.translations
                    ),
                )
                .where(LocalizationProject.slug == project_slug)
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        now = datetime.now(UTC)
        date_prefix = f"snap-{now.strftime('%Y-%m-%d')}-"
        todays_snapshots = (
            await self._session.execute(
                select(BuildSnapshot)
                .where(
                    BuildSnapshot.project_id == project.id,
                    BuildSnapshot.snapshot_identifier.startswith(date_prefix),
                )
                .order_by(BuildSnapshot.snapshot_identifier)
            )
        ).scalars().all()
        next_suffix = chr(ord("a") + len(todays_snapshots))
        snapshot_id = f"{date_prefix}{next_suffix}"
        total_snapshots_count = (
            await self._session.execute(
                select(func.count(BuildSnapshot.id)).where(
                    BuildSnapshot.project_id == project.id
                )
            )
        ).scalar_one()
        source_revision = f"r{18235 + total_snapshots_count}"
        # C# $"l{09982 + count:D5}": the literal 09982 is decimal 9982 (C# has
        # no octal literals); the sum is zero-padded to 5 digits.
        localization_revision = f"l{(9982 + total_snapshots_count):05d}"
        snapshot = BuildSnapshot(
            project_id=project.id,
            snapshot_identifier=snapshot_id,
            source_revision=source_revision,
            localization_revision=localization_revision,
            config="Production-Default",
            created_at=now,
        )
        locale_counts: list[BuildSnapshotLocaleCount] = []
        for locale in project.locales:
            approved_count = sum(
                1
                for item in project.strings
                if any(
                    trans.locale_code == locale.locale_code
                    and trans.stage == "Approved"
                    for trans in item.translations
                )
            )
            locale_counts.append(
                BuildSnapshotLocaleCount(
                    build_snapshot=snapshot,
                    locale_code=locale.locale_code,
                    approved_count=approved_count,
                )
            )
        snapshot.locale_counts = locale_counts
        self._session.add(snapshot)
        await self._session.flush()
        return BuildSnapshotDto(
            id=snapshot.id,
            snapshot_identifier=snapshot.snapshot_identifier,
            source_revision=snapshot.source_revision,
            localization_revision=snapshot.localization_revision,
            config=snapshot.config,
            created_at=snapshot.created_at,
            locale_counts=[
                BuildSnapshotLocaleCountDto(
                    locale_code=count.locale_code,
                    approved_count=count.approved_count,
                )
                for count in locale_counts
            ],
        )
