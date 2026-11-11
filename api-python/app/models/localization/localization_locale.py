"""Ported from api/Models/Localization/LocalizationLocale.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject


class LocalizationLocale(Base):
    __tablename__ = "localization_locales"
    __table_args__ = (
        Index("ix_localization_locales_project_id", "project_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    locale_code: Mapped[str] = mapped_column(String(20))
    display_name: Mapped[str] = mapped_column(String(100))

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="locales", lazy="raise"
    )
