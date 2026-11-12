"""Ported from api/Models/Localization/LocalizationProviderRate.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Identity, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class LocalizationProviderRate(Base):
    __tablename__ = "localization_provider_rates"
    __table_args__ = (
        Index(
            "ux_localization_provider_rates_meter_kind_from",
            "meter",
            "unit_kind",
            "valid_from",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    meter: Mapped[str] = mapped_column(String(30), default="")
    unit_kind: Mapped[str] = mapped_column(String(20), default="")
    usd_per_million: Mapped[Decimal] = mapped_column(Numeric(12, 6))
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
