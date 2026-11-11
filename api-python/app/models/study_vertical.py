"""Ported from api/Models/StudyVertical.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .study_task import StudyTask


class StudyVertical(Base):
    __tablename__ = "Verticals"
    __table_args__ = (
        Index("IX_Verticals_Name", "Name", unique=True),
        Index("ix_verticals_canonical_vertical_id", "canonical_vertical_id"),
    )

    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("Name", Text)
    description: Mapped[str] = mapped_column("Description", Text)
    canonical_vertical_id: Mapped[int | None] = mapped_column(
        ForeignKey("Verticals.Id", ondelete="RESTRICT")
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    canonical_vertical: Mapped[StudyVertical | None] = relationship(
        "StudyVertical",
        remote_side="StudyVertical.id",
        back_populates="aliases",
        lazy="raise",
    )
    aliases: Mapped[list[StudyVertical]] = relationship(
        "StudyVertical", back_populates="canonical_vertical", lazy="raise"
    )
    tasks: Mapped[list[StudyTask]] = relationship(
        "StudyTask", back_populates="vertical", lazy="raise"
    )

    @property
    def layout_mode(self) -> str:
        tasks = self.__dict__.get("tasks") or []
        if any(t.module and t.module != "General" for t in tasks):
            return "Modular"
        return "Flat"
