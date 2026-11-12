"""Ported from api/Models/Localization/TranslationJob.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject
    from .vendor import Vendor


# The table keeps its original name (localization_marketplace_jobs) and column
# names to avoid a table rename with its constraint renames.
class TranslationJob(Base):
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
    status: Mapped[str] = mapped_column(String(20), default="Assigned")
    string_count: Mapped[int] = mapped_column(Integer)
    word_count: Mapped[int] = mapped_column(Integer)
    vendor_id: Mapped[int | None] = mapped_column(
        "awarded_vendor_id", ForeignKey("localization_vendors.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime | None] = mapped_column("posted_at", DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="translation_jobs", lazy="raise"
    )
    vendor: Mapped[Vendor | None] = relationship(
        "Vendor", back_populates="jobs", lazy="raise"
    )
