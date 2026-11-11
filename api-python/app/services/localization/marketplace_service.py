"""Ported from api/Services/Localization/MarketplaceService.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.localization.ledger_entry import LedgerEntry
from ...models.localization.localization_project import LocalizationProject
from ...models.localization.localization_string import LocalizationString
from ...models.localization.localization_translation import LocalizationTranslation
from ...models.localization.marketplace_bid import MarketplaceBid
from ...models.localization.marketplace_job import MarketplaceJob
from ...schemas.localization_dtos import (
    MarketplaceBidDto,
    MarketplaceJobDto,
    MarketplaceJobSummaryDto,
)
from .credit_ledger_service import CreditLedgerService
from .localization_exceptions import (
    InvalidJobStateException,
    LocalizationLocaleNotFoundException,
    LocalizationProjectNotFoundException,
    MarketplaceBidNotFoundException,
    MarketplaceJobNotFoundException,
)


def _word_count(source_text: str) -> int:
    # C# splits on the space character only and drops empty entries.
    return len([word for word in source_text.split(" ") if word != ""])


def _bid_dto(bid: MarketplaceBid) -> MarketplaceBidDto:
    return MarketplaceBidDto(
        id=bid.id,
        marketplace_job_id=bid.marketplace_job_id,
        vendor_id=bid.vendor_id,
        vendor_name=bid.vendor.name if bid.vendor else "Unknown Vendor",
        vendor_languages=bid.vendor.languages if bid.vendor else "",
        vendor_rating=bid.vendor.rating if bid.vendor else Decimal("5.0"),
        proposed_price=bid.proposed_price,
        note=bid.note,
        status=bid.status,
        submitted_at=bid.submitted_at,
    )


class MarketplaceService:
    def __init__(
        self, session: AsyncSession, credit_ledger_service: CreditLedgerService
    ) -> None:
        self._session = session
        self._credit_ledger_service = credit_ledger_service

    async def get_locale_overview_async(
        self, project_slug: str
    ) -> list[MarketplaceJobSummaryDto]:
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
        jobs = (
            await self._session.execute(
                select(MarketplaceJob)
                .options(
                    selectinload(MarketplaceJob.awarded_vendor),
                    selectinload(MarketplaceJob.bids),
                )
                .where(MarketplaceJob.project_id == project.id)
            )
        ).scalars().all()
        overview: list[MarketplaceJobSummaryDto] = []
        for locale in sorted(project.locales, key=lambda item: item.id):
            matching = [job for job in jobs if job.locale_code == locale.locale_code]
            job = max(matching, key=lambda item: item.id) if matching else None
            untranslated = [
                item
                for item in project.strings
                if not any(
                    trans.locale_code == locale.locale_code
                    and trans.target_text is not None
                    and trans.target_text.strip()
                    for trans in item.translations
                )
            ]
            untranslated_count = len(untranslated)
            word_count = sum(_word_count(item.source_text) for item in untranslated)
            if job is None:
                est_low, est_high = (
                    await self._credit_ledger_service.estimate_price_band_async(
                        word_count
                    )
                )
                overview.append(
                    MarketplaceJobSummaryDto(
                        id=None,
                        project_id=project.id,
                        locale_code=locale.locale_code,
                        status="Not Posted",
                        string_count=untranslated_count,
                        word_count=word_count,
                        suggested_price_low=est_low,
                        suggested_price_high=est_high,
                        awarded_vendor_id=None,
                        awarded_vendor_name=None,
                        posted_at=None,
                        awarded_at=None,
                        submitted_at=None,
                        approved_at=None,
                        bid_count=0,
                    )
                )
            else:
                overview.append(
                    MarketplaceJobSummaryDto(
                        id=job.id,
                        project_id=project.id,
                        locale_code=job.locale_code,
                        status=job.status,
                        string_count=job.string_count,
                        word_count=job.word_count,
                        suggested_price_low=job.suggested_price_low,
                        suggested_price_high=job.suggested_price_high,
                        awarded_vendor_id=job.awarded_vendor_id,
                        awarded_vendor_name=job.awarded_vendor.name
                        if job.awarded_vendor
                        else None,
                        posted_at=job.posted_at,
                        awarded_at=job.awarded_at,
                        submitted_at=job.submitted_at,
                        approved_at=job.approved_at,
                        bid_count=len(job.bids),
                    )
                )
        return overview

    async def post_to_marketplace_async(
        self, project_slug: str, locale_code: str
    ) -> MarketplaceJobDto:
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
        if not any(
            locale.locale_code == locale_code for locale in project.locales
        ):
            raise LocalizationLocaleNotFoundException(locale_code)
        most_recent_job = (
            await self._session.execute(
                select(MarketplaceJob)
                .where(
                    MarketplaceJob.project_id == project.id,
                    MarketplaceJob.locale_code == locale_code,
                )
                .order_by(MarketplaceJob.id.desc())
            )
        ).scalars().first()
        if (
            most_recent_job is not None
            and most_recent_job.status != "Approved"
            and most_recent_job.status != "Closed"
        ):
            raise InvalidJobStateException(
                f"Cannot post a new job for locale '{locale_code}' while job "
                f"{most_recent_job.id} is in status '{most_recent_job.status}'."
            )
        # Unlike EF change tracking, SQLAlchemy does not backfill
        # already-loaded collections when rows are added later in the
        # session, so refresh before counting.
        await self._session.refresh(project, ["strings"])
        for item in project.strings:
            await self._session.refresh(item, ["translations"])
        untranslated_strings = [
            item
            for item in project.strings
            if not any(
                trans.locale_code == locale_code
                and trans.target_text is not None
                and trans.target_text.strip()
                for trans in item.translations
            )
        ]
        if len(untranslated_strings) == 0:
            raise InvalidJobStateException(
                f"There is nothing left to translate for locale '{locale_code}'."
            )
        string_count = len(untranslated_strings)
        word_count = sum(
            _word_count(item.source_text) for item in untranslated_strings
        )
        low, high = await self._credit_ledger_service.estimate_price_band_async(
            word_count
        )
        now = datetime.now(UTC)
        job = MarketplaceJob(
            project_id=project.id,
            locale_code=locale_code,
            status="Open",
            string_count=string_count,
            word_count=word_count,
            suggested_price_low=low,
            suggested_price_high=high,
            posted_at=now,
        )
        self._session.add(job)
        await self._session.flush()
        return await self.get_job_dto_async(job.id)

    async def get_bids_async(
        self, marketplace_job_id: int
    ) -> list[MarketplaceBidDto]:
        job = (
            await self._session.execute(
                select(MarketplaceJob).where(
                    MarketplaceJob.id == marketplace_job_id
                )
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(marketplace_job_id)
        bids = (
            await self._session.execute(
                select(MarketplaceBid)
                .options(selectinload(MarketplaceBid.vendor))
                .where(MarketplaceBid.marketplace_job_id == marketplace_job_id)
                .order_by(MarketplaceBid.submitted_at.desc())
            )
        ).scalars().all()
        return [_bid_dto(bid) for bid in bids]

    async def award_bid_async(
        self, marketplace_job_id: int, bid_id: int
    ) -> MarketplaceJobDto:
        job = (
            await self._session.execute(
                select(MarketplaceJob)
                .options(selectinload(MarketplaceJob.bids))
                .where(MarketplaceJob.id == marketplace_job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(marketplace_job_id)
        selected_bid = next(
            (bid for bid in job.bids if bid.id == bid_id), None
        )
        if selected_bid is None:
            raise MarketplaceBidNotFoundException(bid_id)
        if job.status != "Open":
            raise InvalidJobStateException(
                f"Cannot award bid {bid_id} because job {marketplace_job_id} is in "
                f"status '{job.status}'. Expected 'Open'."
            )
        if selected_bid.status != "Pending":
            raise InvalidJobStateException(
                f"Cannot award bid {bid_id} because it is in status "
                f"'{selected_bid.status}'. Expected 'Pending'."
            )
        now = datetime.now(UTC)
        selected_bid.status = "Awarded"
        for sibling in job.bids:
            if sibling.id != bid_id:
                sibling.status = "Declined"
        job.status = "Awarded"
        job.awarded_vendor_id = selected_bid.vendor_id
        job.awarded_at = now
        await self._session.flush()
        return await self.get_job_dto_async(job.id)

    async def approve_submission_async(
        self, marketplace_job_id: int
    ) -> MarketplaceJobDto:
        job = (
            await self._session.execute(
                select(MarketplaceJob)
                .options(
                    selectinload(MarketplaceJob.project),
                    selectinload(MarketplaceJob.bids),
                )
                .where(MarketplaceJob.id == marketplace_job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(marketplace_job_id)
        if job.status != "SubmittedForReview":
            raise InvalidJobStateException(
                f"Cannot approve job {marketplace_job_id} because it is in status "
                f"'{job.status}'. Expected 'SubmittedForReview'."
            )
        awarded_bid = next(
            (bid for bid in job.bids if bid.status == "Awarded"), None
        )
        if awarded_bid is None:
            raise InvalidJobStateException(
                f"Cannot approve job {marketplace_job_id} because it has no awarded bid."
            )
        now = datetime.now(UTC)
        job.status = "Approved"
        job.approved_at = now
        # Record credit ledger spend
        price = awarded_bid.proposed_price
        ledger_entry = LedgerEntry(
            project_id=job.project_id,
            source="Marketplace",
            amount=price,
            related_marketplace_job_id=job.id,
            created_at=now,
        )
        self._session.add(ledger_entry)
        # Advance translations in project + locale that have target text to "Approved"
        translations = (
            await self._session.execute(
                select(LocalizationTranslation)
                .options(selectinload(LocalizationTranslation.string))
                .join(
                    LocalizationString,
                    LocalizationTranslation.string_id == LocalizationString.id,
                )
                .where(
                    LocalizationString.project_id == job.project_id,
                    LocalizationTranslation.locale_code == job.locale_code,
                )
            )
        ).scalars().all()
        for trans in translations:
            if trans.target_text is not None and trans.target_text.strip():
                trans.stage = "Approved"
                trans.updated_at = now
        await self._session.flush()
        return await self.get_job_dto_async(job.id)

    async def send_back_for_revision_async(
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
        if job.status != "SubmittedForReview":
            raise InvalidJobStateException(
                f"Cannot send back job {marketplace_job_id} because it is in status "
                f"'{job.status}'. Expected 'SubmittedForReview'."
            )
        job.status = "NeedsRevision"
        await self._session.flush()
        return await self.get_job_dto_async(job.id)

    async def get_job_dto_async(self, job_id: int) -> MarketplaceJobDto:
        job = (
            await self._session.execute(
                select(MarketplaceJob)
                .options(
                    selectinload(MarketplaceJob.awarded_vendor),
                    selectinload(MarketplaceJob.bids).selectinload(
                        MarketplaceBid.vendor
                    ),
                )
                .where(MarketplaceJob.id == job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(job_id)
        bids = [_bid_dto(bid) for bid in job.bids]
        return MarketplaceJobDto(
            id=job.id,
            project_id=job.project_id,
            locale_code=job.locale_code,
            status=job.status,
            string_count=job.string_count,
            word_count=job.word_count,
            suggested_price_low=job.suggested_price_low,
            suggested_price_high=job.suggested_price_high,
            awarded_vendor_id=job.awarded_vendor_id,
            awarded_vendor_name=job.awarded_vendor.name
            if job.awarded_vendor
            else None,
            posted_at=job.posted_at,
            awarded_at=job.awarded_at,
            submitted_at=job.submitted_at,
            approved_at=job.approved_at,
            bids=bids,
        )
