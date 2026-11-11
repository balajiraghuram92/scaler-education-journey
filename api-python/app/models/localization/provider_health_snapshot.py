"""Ported from api/Models/Localization/ProviderHealthSnapshot.cs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class ProviderHealthSnapshot(Base):
    __tablename__ = "localization_provider_health"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(30))
    p50_latency_ms: Mapped[int] = mapped_column(Integer)
    p99_latency_ms: Mapped[int] = mapped_column(Integer)
    error_rate_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    circuit_state: Mapped[str] = mapped_column(String(20))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
