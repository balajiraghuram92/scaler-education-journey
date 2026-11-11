"""Ported from api/Models/Localization/LocalizationString.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject
    from .localization_translation import LocalizationTranslation


class LocalizationString(Base):
    __tablename__ = "localization_strings"
    __table_args__ = (
        Index("ix_localization_strings_project_id", "project_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    key: Mapped[str] = mapped_column(String(200), default="")
    source_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="strings", lazy="raise"
    )
    translations: Mapped[list[LocalizationTranslation]] = relationship(
        "LocalizationTranslation", back_populates="string", lazy="raise"
    )
