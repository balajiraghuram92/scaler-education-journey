"""Ported from api/Models/LessonCodeComparison.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson


class LessonCodeComparison(Base):
    __tablename__ = "lesson_code_comparisons"
    __table_args__ = (Index("IX_lesson_code_comparisons_LessonId", "lesson_id"),)

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    before_label: Mapped[str] = mapped_column(String(100))
    before_language: Mapped[str] = mapped_column(String(50))
    before_code: Mapped[str] = mapped_column(Text)
    after_label: Mapped[str] = mapped_column(String(100))
    after_language: Mapped[str] = mapped_column(String(50))
    after_code: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="code_comparisons", lazy="raise"
    )
