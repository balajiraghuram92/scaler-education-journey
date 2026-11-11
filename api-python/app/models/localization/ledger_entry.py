"""Ported from api/Models/Localization/LedgerEntry.cs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject
    from .marketplace_job import MarketplaceJob


class LedgerEntry(Base):
    __tablename__ = "localization_ledger_entries"
    __table_args__ = (
        Index("ix_localization_ledger_entries_project_id", "project_id"),
        Index("ix_localization_ledger_entries_job_id", "related_marketplace_job_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    source: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    units_consumed: Mapped[int | None] = mapped_column(Integer)
    unit_type: Mapped[str | None] = mapped_column(String(20))
    real_cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    related_marketplace_job_id: Mapped[int | None] = mapped_column(
        ForeignKey("localization_marketplace_jobs.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="ledger_entries", lazy="raise"
    )
    related_marketplace_job: Mapped[MarketplaceJob | None] = relationship(
        "MarketplaceJob", lazy="raise"
    )
