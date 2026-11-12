"""Ported from api/Services/Localization/VendorPortalService.cs."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.localization.localization_project import LocalizationProject
from ...models.localization.localization_string import LocalizationString
from ...models.localization.localization_translation import LocalizationTranslation
from ...models.localization.translation_job import TranslationJob
from ...models.localization.vendor import Vendor
from ...schemas.localization_dtos import (
    VendorJobRowDto,
    VendorStringRowDto,
    VendorTeamDto,
)
from .job_scope import JobScope
from .localization_exceptions import (
    InvalidJobStateException,
    LocalizationProjectNotFoundException,
    LocalizationStringNotFoundException,
    MarketplaceJobNotFoundException,
    VendorNotFoundException,
)


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


class VendorPortalService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_vendor_roster_async(self) -> list[VendorTeamDto]:
        vendors = (
            await self._session.execute(
                select(Vendor).order_by(Vendor.id)
            )
        ).scalars().all()
        return [
            VendorTeamDto(id=v.id, alias=v.alias, languages=v.languages)
            for v in vendors
        ]

    async def get_jobs_for_vendor_async(self, vendor_id: int) -> list[VendorJobRowDto]:
        vendor = (
            await self._session.execute(
                select(Vendor).where(Vendor.id == vendor_id)
            )
        ).scalar_one_or_none()
        if vendor is None:
            raise VendorNotFoundException(vendor_id)

        jobs = (
            await self._session.execute(
                select(TranslationJob)
                .where(TranslationJob.vendor_id == vendor_id)
                .order_by(
                    TranslationJob.created_at.desc(), TranslationJob.id.desc()
                )
            )
        ).scalars().all()

        rows: list[VendorJobRowDto] = []
        for job in jobs:
            # C# passes the tracked job entity here, but the only overload
            # takes the job id (the C# does not compile as written); the
            # port passes the id.
            rows.append(await self._vendor_job_row_async(job.id))
        return rows

    async def get_job_strings_async(self, job_id: int) -> list[VendorStringRowDto]:
        job = (
            await self._session.execute(
                select(TranslationJob).where(TranslationJob.id == job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(job_id)

        strings = (
            await self._session.execute(
                select(LocalizationString)
                .options(
                    selectinload(LocalizationString.translations.and_(
                        LocalizationTranslation.locale_code == job.locale_code
                    ))
                )
                .where(LocalizationString.project_id == job.project_id)
                .order_by(LocalizationString.id)
            )
        ).scalars().all()

        return [
            _vendor_string_row(
                item, job.locale_code, item.translations[0] if item.translations else None
            )
            for item in strings
        ]

    async def update_job_string_async(
        self, job_id: int, string_id: int, target_text: str | None
    ) -> VendorStringRowDto:
        job = (
            await self._session.execute(
                select(TranslationJob).where(TranslationJob.id == job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(job_id)
        if job.status not in ("Assigned", "InProgress", "NeedsRevision"):
            raise InvalidJobStateException(
                f"Cannot edit strings on job {job_id} because it is in status "
                f"'{job.status}'."
            )

        item = (
            await self._session.execute(
                select(LocalizationString)
                .options(selectinload(LocalizationString.translations))
                .where(
                    LocalizationString.id == string_id,
                    LocalizationString.project_id == job.project_id,
                )
            )
        ).scalar_one_or_none()
        if item is None:
            raise LocalizationStringNotFoundException(string_id)

        translation = (
            await self._session.execute(
                select(LocalizationTranslation).where(
                    LocalizationTranslation.string_id == string_id,
                    LocalizationTranslation.locale_code == job.locale_code,
                )
            )
        ).scalar_one_or_none()

        if translation is not None and translation.stage == "Approved":
            raise InvalidJobStateException(
                f"String {string_id} is already approved for {job.locale_code}."
            )

        has_target = not _is_blank(target_text)
        if translation is None:
            translation = LocalizationTranslation(
                string_id=string_id,
                locale_code=job.locale_code,
                target_text=target_text,
                stage="Translated" if has_target else "New",
                translation_source=JobScope.VENDOR_SOURCE,
                needs_review=False,
                updated_at=datetime.now(UTC),
            )
            self._session.add(translation)
            # Same EF-fixup parity as the workflow MT branch.
            item.translations.append(translation)
        else:
            translation.target_text = target_text
            translation.translation_source = JobScope.VENDOR_SOURCE
            translation.stage = "Translated" if has_target else "New"
            translation.updated_at = datetime.now(UTC)

        if job.status in ("Assigned", "NeedsRevision"):
            job.status = "InProgress"

        await self._session.flush()
        return _vendor_string_row(item, job.locale_code, translation)

    async def submit_job_for_review_async(self, job_id: int) -> VendorJobRowDto:
        job = (
            await self._session.execute(
                select(TranslationJob).where(TranslationJob.id == job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(job_id)
        if job.status not in ("Assigned", "InProgress", "NeedsRevision"):
            raise InvalidJobStateException(
                f"Cannot submit job {job_id} for review because it is in status "
                f"'{job.status}'."
            )

        # Refresh each string's translations first: SQLAlchemy leaves
        # already-loaded collections stale where EF relationship fixup
        # backfills them, so the check must read fresh rows (Round 4).
        strings = (
            await self._session.execute(
                select(LocalizationString).where(
                    LocalizationString.project_id == job.project_id
                )
            )
        ).scalars().all()
        for item in strings:
            await self._session.refresh(item, ["translations"])

        untranslated_exists = any(
            not any(
                t.locale_code == job.locale_code and not _is_blank(t.target_text)
                for t in item.translations
            )
            for item in strings
        )
        if untranslated_exists:
            raise InvalidJobStateException(
                "All strings must have non-empty translations before submitting "
                "the job for review."
            )

        unreviewed_machine_count = 0
        for item in strings:
            translation = next(
                (
                    t
                    for t in item.translations
                    if t.locale_code == job.locale_code
                ),
                None,
            )
            if (
                translation is not None
                and translation.translation_source == JobScope.MACHINE_SOURCE
                and JobScope.is_open(item, job.locale_code)
            ):
                unreviewed_machine_count += 1

        if unreviewed_machine_count > 0:
            raise InvalidJobStateException(
                f"{unreviewed_machine_count} machine-translated strings still "
                "need review before the job can be submitted."
            )

        job.status = "SubmittedForReview"
        job.submitted_at = datetime.now(UTC)

        await self._session.flush()
        return await self._vendor_job_row_async(job.id)

    async def _vendor_job_row_async(self, job_id: int) -> VendorJobRowDto:
        job = (
            await self._session.execute(
                select(TranslationJob).where(TranslationJob.id == job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(job_id)

        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.id == job.project_id
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(str(job.project_id))

        strings = (
            await self._session.execute(
                select(LocalizationString)
                .options(
                    selectinload(LocalizationString.translations.and_(
                        LocalizationTranslation.locale_code == job.locale_code
                    ))
                )
                .where(LocalizationString.project_id == job.project_id)
            )
        ).scalars().all()

        return VendorJobRowDto(
            id=job.id,
            client_alias=project.client_alias,
            locale_code=job.locale_code,
            status=job.status,
            string_count=job.string_count,
            word_count=job.word_count,
            completed_percent=JobScope.completed_percent(
                strings, job.locale_code, job.string_count, job.status
            ),
            created_at=job.created_at,
            submitted_at=job.submitted_at,
            approved_at=job.approved_at,
        )


def _vendor_string_row(
    item: LocalizationString,
    locale_code: str,
    translation: LocalizationTranslation | None,
) -> VendorStringRowDto:
    return VendorStringRowDto(
        string_id=item.id,
        key=item.key,
        source_text=item.source_text,
        locale_code=locale_code,
        target_text=translation.target_text if translation else None,
        stage=translation.stage if translation else "New",
        translation_source=translation.translation_source if translation else "Manual",
        updated_at=translation.updated_at if translation else None,
        score=translation.qps_score if translation else None,
        needs_review=translation.needs_review if translation else False,
        raw_mt_text=translation.raw_mt_text if translation else None,
        raw_mt_score=translation.raw_mt_qps_score if translation else None,
        in_job=JobScope.is_open(item, locale_code),
        vendor_reviewed=JobScope.is_vendor_reviewed(translation),
    )
