"""Ported from api/Models/Localization/MarketplaceJob.cs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject
    from .marketplace_bid import MarketplaceBid
    from .vendor import Vendor


class MarketplaceJob(Base):
    __tablename__ = "localization_marketplace_jobs"
    __table_args__ = (
        Index("ix_localization_marketplace_jobs_project_id", "project_id"),
        Index("ix_localization_marketplace_jobs_vendor_id", "awarded_vendor_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    locale_code: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(20), default="Draft")
    string_count: Mapped[int] = mapped_column(Integer)
    word_count: Mapped[int] = mapped_column(Integer)
    suggested_price_low: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    suggested_price_high: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    awarded_vendor_id: Mapped[int | None] = mapped_column(
        ForeignKey("localization_vendors.id", ondelete="SET NULL")
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    awarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="marketplace_jobs", lazy="raise"
    )
    awarded_vendor: Mapped[Vendor | None] = relationship(
        "Vendor", back_populates="awarded_jobs", lazy="raise"
    )
    bids: Mapped[list[MarketplaceBid]] = relationship(
        "MarketplaceBid", back_populates="marketplace_job", lazy="raise"
    )
