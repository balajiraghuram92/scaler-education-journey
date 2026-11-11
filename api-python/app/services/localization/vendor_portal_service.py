"""Ported from api/Services/Localization/VendorPortalService.cs."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.localization.localization_string import LocalizationString
from ...models.localization.localization_translation import LocalizationTranslation
from ...models.localization.marketplace_bid import MarketplaceBid
from ...models.localization.marketplace_job import MarketplaceJob
from ...models.localization.vendor import Vendor
from ...schemas.localization_dtos import (
    LocalizationStringRowDto,
    MarketplaceBidDto,
    MarketplaceJobDto,
    MarketplaceJobSummaryDto,
    VendorDto,
)
from .localization_exceptions import (
    InvalidJobStateException,
    LocalizationStringNotFoundException,
    MarketplaceJobNotFoundException,
    VendorLanguageMismatchException,
    VendorNotFoundException,
)
from .marketplace_service import MarketplaceService


def _parse_languages(languages: str) -> set[str]:
    # C# splits on ',' with RemoveEmptyEntries + TrimEntries, compared
    # OrdinalIgnoreCase; locale codes are ASCII so lower() matches.
    return {
        part.strip().lower() for part in languages.split(",") if part.strip()
    }


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


def _summary_dto(job: MarketplaceJob) -> MarketplaceJobSummaryDto:
    return MarketplaceJobSummaryDto(
        id=job.id,
        project_id=job.project_id,
        locale_code=job.locale_code,
        status=job.status,
        string_count=job.string_count,
        word_count=job.word_count,
        suggested_price_low=job.suggested_price_low,
        suggested_price_high=job.suggested_price_high,
        awarded_vendor_id=job.awarded_vendor_id,
        awarded_vendor_name=job.awarded_vendor.name if job.awarded_vendor else None,
        posted_at=job.posted_at,
        awarded_at=job.awarded_at,
        submitted_at=job.submitted_at,
        approved_at=job.approved_at,
        bid_count=len(job.bids),
    )


class VendorPortalService:
    def __init__(
        self, session: AsyncSession, marketplace_service: MarketplaceService
    ) -> None:
        self._session = session
        self._marketplace_service = marketplace_service

    async def get_vendor_roster_async(self) -> list[VendorDto]:
        vendors = (
            await self._session.execute(
                select(Vendor).order_by(Vendor.id)
            )
        ).scalars().all()
        return [
            VendorDto(
                id=vendor.id,
                name=vendor.name,
                languages=vendor.languages,
                rating=vendor.rating,
            )
            for vendor in vendors
        ]

    async def get_open_jobs_for_vendor_async(
        self, vendor_id: int
    ) -> list[MarketplaceJobSummaryDto]:
        vendor = (
            await self._session.execute(
                select(Vendor).where(Vendor.id == vendor_id)
            )
        ).scalar_one_or_none()
        if vendor is None:
            raise VendorNotFoundException(vendor_id)
        vendor_languages = _parse_languages(vendor.languages)
        open_jobs = (
            await self._session.execute(
                select(MarketplaceJob)
                .options(
                    selectinload(MarketplaceJob.awarded_vendor),
                    selectinload(MarketplaceJob.bids),
                )
                .where(MarketplaceJob.status == "Open")
                .order_by(MarketplaceJob.posted_at.desc())
            )
        ).scalars().all()
        return [
            _summary_dto(job)
            for job in open_jobs
            if job.locale_code.lower() in vendor_languages
        ]

    async def submit_bid_async(
        self,
        marketplace_job_id: int,
        vendor_id: int,
        proposed_price: Decimal,
        note: str | None,
    ) -> MarketplaceBidDto:
        job = (
            await self._session.execute(
                select(MarketplaceJob).where(
                    MarketplaceJob.id == marketplace_job_id
                )
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(marketplace_job_id)
        vendor = (
            await self._session.execute(
                select(Vendor).where(Vendor.id == vendor_id)
            )
        ).scalar_one_or_none()
        if vendor is None:
            raise VendorNotFoundException(vendor_id)
        if job.status != "Open":
            raise InvalidJobStateException(
                f"Cannot bid on job {marketplace_job_id} because it is in status "
                f"'{job.status}'. Expected 'Open'."
            )
        vendor_languages = _parse_languages(vendor.languages)
        if job.locale_code.lower() not in vendor_languages:
            raise VendorLanguageMismatchException(vendor_id, job.locale_code)
        pending_count = (
            await self._session.execute(
                select(func.count(MarketplaceBid.id)).where(
                    MarketplaceBid.marketplace_job_id == marketplace_job_id,
                    MarketplaceBid.vendor_id == vendor_id,
                    MarketplaceBid.status == "Pending",
                )
            )
        ).scalar_one()
        if pending_count > 0:
            raise InvalidJobStateException(
                f"Vendor {vendor_id} already has a pending bid on job "
                f"{marketplace_job_id}."
            )
        if proposed_price <= 0:
            # The detail embeds .NET's ArgumentException Message suffix verbatim
            # (" (Parameter 'proposedPrice')") so error bodies match.
            raise ValueError(
                "Proposed price must be greater than zero. (Parameter 'proposedPrice')"
            )
        bid = MarketplaceBid(
            marketplace_job_id=marketplace_job_id,
            vendor_id=vendor_id,
            proposed_price=proposed_price,
            note=note or "",
            status="Pending",
            submitted_at=datetime.now(timezone.utc),
        )
        self._session.add(bid)
        await self._session.flush()
        return MarketplaceBidDto(
            id=bid.id,
            marketplace_job_id=bid.marketplace_job_id,
            vendor_id=bid.vendor_id,
            vendor_name=vendor.name,
            vendor_languages=vendor.languages,
            vendor_rating=vendor.rating,
            proposed_price=bid.proposed_price,
            note=bid.note,
            status=bid.status,
            submitted_at=bid.submitted_at,
        )

    async def get_awarded_jobs_for_vendor_async(
        self, vendor_id: int
    ) -> list[MarketplaceJobSummaryDto]:
        vendor = (
            await self._session.execute(
                select(Vendor).where(Vendor.id == vendor_id)
            )
        ).scalar_one_or_none()
        if vendor is None:
            raise VendorNotFoundException(vendor_id)
        jobs = (
            await self._session.execute(
                select(MarketplaceJob)
                .options(
                    selectinload(MarketplaceJob.awarded_vendor),
                    selectinload(MarketplaceJob.bids),
                )
                .where(
                    MarketplaceJob.awarded_vendor_id == vendor_id,
                    MarketplaceJob.status.in_(
                        [
                            "Awarded",
                            "InProgress",
                            "NeedsRevision",
                            "SubmittedForReview",
                            "Approved",
                        ]
                    ),
                )
                .order_by(
                    func.coalesce(
                        MarketplaceJob.awarded_at, MarketplaceJob.posted_at
                    ).desc()
                )
            )
        ).scalars().all()
        return [_summary_dto(job) for job in jobs]

    async def get_job_strings_async(
        self, marketplace_job_id: int
    ) -> list[LocalizationStringRowDto]:
        job = (
            await self._session.execute(
                select(MarketplaceJob).where(
                    MarketplaceJob.id == marketplace_job_id
                )
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(marketplace_job_id)
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
        result: list[LocalizationStringRowDto] = []
        for item in strings:
            translation = item.translations[0] if item.translations else None
            result.append(
                LocalizationStringRowDto(
                    string_id=item.id,
                    key=item.key,
                    source_text=item.source_text,
                    locale_code=job.locale_code,
                    target_text=translation.target_text if translation else None,
                    stage=translation.stage if translation else "New",
                    translation_source=translation.translation_source
                    if translation
                    else "Marketplace",
                    qps_score=translation.qps_score if translation else None,
                    needs_review=translation.needs_review if translation else False,
                    updated_at=translation.updated_at if translation else None,
                )
            )
        return result

    async def update_job_string_async(
        self, marketplace_job_id: int, string_id: int, target_text: str | None
    ) -> LocalizationStringRowDto:
        job = (
            await self._session.execute(
                select(MarketplaceJob).where(
                    MarketplaceJob.id == marketplace_job_id
                )
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(marketplace_job_id)
        if job.status != "Awarded" and job.status != "InProgress" and job.status != "NeedsRevision":
            raise InvalidJobStateException(
                f"Cannot edit strings on job {marketplace_job_id} because it is in "
                f"status '{job.status}'."
            )
        item = (
            await self._session.execute(
                select(LocalizationString).where(
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
        has_target = not _is_blank(target_text)
        if translation is None:
            translation = LocalizationTranslation(
                string_id=string_id,
                locale_code=job.locale_code,
                target_text=target_text,
                stage="Translated" if has_target else "New",
                translation_source="Marketplace",
                needs_review=False,
                updated_at=datetime.now(timezone.utc),
            )
            self._session.add(translation)
        else:
            translation.target_text = target_text
            translation.translation_source = "Marketplace"
            translation.stage = "Translated" if has_target else "New"
            translation.updated_at = datetime.now(timezone.utc)
        if job.status == "Awarded" or job.status == "NeedsRevision":
            job.status = "InProgress"
        await self._session.flush()
        return LocalizationStringRowDto(
            string_id=item.id,
            key=item.key,
            source_text=item.source_text,
            locale_code=job.locale_code,
            target_text=translation.target_text,
            stage=translation.stage,
            translation_source=translation.translation_source,
            qps_score=translation.qps_score,
            needs_review=translation.needs_review,
            updated_at=translation.updated_at,
        )

    async def submit_job_for_review_async(
        self, marketplace_job_id: int
    ) -> MarketplaceJobDto:
        job = (
            await self._session.execute(
                select(MarketplaceJob).where(
                    MarketplaceJob.id == marketplace_job_id
                )
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(marketplace_job_id)
        if job.status != "Awarded" and job.status != "InProgress" and job.status != "NeedsRevision":
            raise InvalidJobStateException(
                f"Cannot submit job {marketplace_job_id} for review because it is in "
                f"status '{job.status}'."
            )
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
        untranslated_exists = any(
            not any(
                trans.locale_code == job.locale_code
                and trans.target_text is not None
                and trans.target_text.strip()
                for trans in item.translations
            )
            for item in strings
        )
        if untranslated_exists:
            raise InvalidJobStateException(
                "All strings must have non-empty translations before submitting "
                "the job for review."
            )
        job.status = "SubmittedForReview"
        job.submitted_at = datetime.now(timezone.utc)
        await self._session.flush()
        return await self._marketplace_service.get_job_dto_async(job.id)
