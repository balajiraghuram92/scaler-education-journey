"""Ported from api/Models/Localization/ServiceAgreement.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject


class ServiceAgreement(Base):
    __tablename__ = "localization_service_agreements"
    __table_args__ = (
        Index("ux_localization_service_agreements_project_id", "project_id", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    tier: Mapped[str] = mapped_column(String(20), default="")
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # One-sided like the C# WithMany(): no collection on the project.
    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", lazy="raise"
    )
