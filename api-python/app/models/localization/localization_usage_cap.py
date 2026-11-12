"""Ported from api/Models/Localization/LocalizationUsageCap.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject


class LocalizationUsageCap(Base):
    __tablename__ = "localization_usage_caps"
    __table_args__ = (
        Index("ux_localization_usage_caps_project_kind", "project_id", "kind", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    kind: Mapped[str] = mapped_column(String(30), default="")
    monthly_limit: Mapped[int] = mapped_column(BigInteger)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # One-sided like the C# WithMany(): no collection on the project.
    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", lazy="raise"
    )
