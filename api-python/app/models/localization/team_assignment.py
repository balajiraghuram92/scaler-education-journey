"""Ported from api/Models/Localization/TeamAssignment.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .service_agreement import ServiceAgreement
    from .vendor import Vendor


class TeamAssignment(Base):
    __tablename__ = "localization_team_assignments"
    __table_args__ = (
        Index(
            "ux_localization_team_assignments_agreement_locale",
            "agreement_id",
            "locale_code",
            unique=True,
        ),
        Index("ix_localization_team_assignments_vendor_id", "vendor_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    agreement_id: Mapped[int] = mapped_column(
        ForeignKey("localization_service_agreements.id", ondelete="CASCADE")
    )
    vendor_id: Mapped[int] = mapped_column(
        ForeignKey("localization_vendors.id", ondelete="RESTRICT")
    )
    locale_code: Mapped[str] = mapped_column(String(20), default="")
    member_count: Mapped[int] = mapped_column(Integer)

    # One-sided like the C# WithMany(): no collections on agreement or vendor.
    agreement: Mapped[ServiceAgreement | None] = relationship(
        "ServiceAgreement", lazy="raise"
    )
    vendor: Mapped[Vendor | None] = relationship("Vendor", lazy="raise")
