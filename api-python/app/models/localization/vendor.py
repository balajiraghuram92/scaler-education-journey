"""Ported from api/Models/Localization/Vendor.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Identity, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .translation_job import TranslationJob


class Vendor(Base):
    __tablename__ = "localization_vendors"
    __table_args__ = (
        Index("ux_localization_vendors_alias", "alias", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), default="")
    languages: Mapped[str] = mapped_column(String(200), default="")
    alias: Mapped[str] = mapped_column(String(100), default="")

    jobs: Mapped[list[TranslationJob]] = relationship(
        "TranslationJob", back_populates="vendor", lazy="raise"
    )
