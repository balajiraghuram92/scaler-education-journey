"""Ported from api/Models/Localization/Vendor.cs."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .marketplace_bid import MarketplaceBid
    from .marketplace_job import MarketplaceJob


class Vendor(Base):
    __tablename__ = "localization_vendors"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    languages: Mapped[str] = mapped_column(String(200))
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 1))

    awarded_jobs: Mapped[list[MarketplaceJob]] = relationship(
        "MarketplaceJob", back_populates="awarded_vendor", lazy="raise"
    )
    bids: Mapped[list[MarketplaceBid]] = relationship(
        "MarketplaceBid", back_populates="vendor", lazy="raise"
    )
