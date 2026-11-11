"""Ported from api/Services/Localization/CreditLedgerService.cs."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.localization.ledger_entry import LedgerEntry
from ...models.localization.localization_project import LocalizationProject
from .localization_exceptions import LocalizationProjectNotFoundException


class CreditLedgerService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_project_balance_async(self, project_slug: str) -> Decimal:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        total = (
            await self._session.execute(
                select(func.coalesce(func.sum(LedgerEntry.amount), 0)).where(
                    LedgerEntry.project_id == project.id
                )
            )
        ).scalar_one()
        return Decimal(total)

    async def record_entry_async(
        self,
        project_slug: str,
        source: str,
        amount: Decimal,
        related_marketplace_job_id: int | None,
    ) -> LedgerEntry:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        entry = LedgerEntry(
            project_id=project.id,
            source=source,
            amount=amount,
            related_marketplace_job_id=related_marketplace_job_id,
            created_at=datetime.now(timezone.utc),
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def estimate_price_band_async(
        self, word_count: int
    ) -> tuple[Decimal, Decimal]:
        # Formula: Low = wordCount * 0.145m rounded to nearest 5, High = wordCount * 0.19m rounded to nearest 5.
        # Math.Round(x, AwayFromZero) rounds half away from zero: ROUND_HALF_UP
        # matches it for the non-negative values word counts produce.
        raw_low = Decimal(word_count) * Decimal("0.145")
        raw_high = Decimal(word_count) * Decimal("0.19")
        low = (raw_low / Decimal(5)).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * Decimal(5)
        high = (raw_high / Decimal(5)).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * Decimal(5)
        if low < Decimal(5):
            low = Decimal(5)
        if high < low + Decimal(15):
            high = low + Decimal(15)
        return (low, high)
