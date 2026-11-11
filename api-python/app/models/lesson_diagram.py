"""Ported from api/Models/LessonDiagram.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson


class LessonDiagram(Base):
    __tablename__ = "lesson_diagrams"
    __table_args__ = (Index("IX_lesson_diagrams_LessonId", "lesson_id"),)

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    caption: Mapped[str] = mapped_column(String(300))
    diagram_type: Mapped[str] = mapped_column(String(50))
    svg_content: Mapped[str] = mapped_column(Text)
    diagram_spec_json: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="diagrams", lazy="raise"
    )
