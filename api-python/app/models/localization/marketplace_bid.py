"""Ported from api/Models/Localization/MarketplaceBid.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .marketplace_job import MarketplaceJob
    from .vendor import Vendor


class MarketplaceBid(Base):
    __tablename__ = "localization_marketplace_bids"
    __table_args__ = (
        Index("ix_localization_marketplace_bids_job_id", "marketplace_job_id"),
        Index("ix_localization_marketplace_bids_vendor_id", "vendor_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    marketplace_job_id: Mapped[int] = mapped_column(
        ForeignKey("localization_marketplace_jobs.id", ondelete="CASCADE")
    )
    vendor_id: Mapped[int] = mapped_column(
        ForeignKey("localization_vendors.id", ondelete="CASCADE")
    )
    proposed_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    note: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(20), default="Pending")
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    marketplace_job: Mapped[MarketplaceJob | None] = relationship(
        "MarketplaceJob", back_populates="bids", lazy="raise"
    )
    vendor: Mapped[Vendor | None] = relationship(
        "Vendor", back_populates="bids", lazy="raise"
    )
