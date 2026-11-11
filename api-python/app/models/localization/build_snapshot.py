"""Ported from api/Models/Localization/BuildSnapshot.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .build_snapshot_locale_count import BuildSnapshotLocaleCount
    from .localization_project import LocalizationProject


class BuildSnapshot(Base):
    __tablename__ = "localization_build_snapshots"
    __table_args__ = (
        Index("ix_localization_build_snapshots_project_id", "project_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    snapshot_identifier: Mapped[str] = mapped_column(String(50), default="")
    source_revision: Mapped[str] = mapped_column(String(50), default="")
    localization_revision: Mapped[str] = mapped_column(String(50), default="")
    config: Mapped[str] = mapped_column(String(100), default="Production-Default")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="build_snapshots", lazy="raise"
    )
    locale_counts: Mapped[list[BuildSnapshotLocaleCount]] = relationship(
        "BuildSnapshotLocaleCount", back_populates="build_snapshot", lazy="raise"
    )
