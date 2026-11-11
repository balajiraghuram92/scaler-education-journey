"""Ported from api/Models/Localization/BuildSnapshotLocaleCount.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .build_snapshot import BuildSnapshot


class BuildSnapshotLocaleCount(Base):
    __tablename__ = "localization_build_snapshot_locale_counts"
    __table_args__ = (
        Index(
            "ix_localization_build_snapshot_locale_counts_snapshot_id",
            "build_snapshot_id",
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    build_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("localization_build_snapshots.id", ondelete="CASCADE")
    )
    locale_code: Mapped[str] = mapped_column(String(20))
    approved_count: Mapped[int] = mapped_column(Integer)

    build_snapshot: Mapped[BuildSnapshot | None] = relationship(
        "BuildSnapshot", back_populates="locale_counts", lazy="raise"
    )
