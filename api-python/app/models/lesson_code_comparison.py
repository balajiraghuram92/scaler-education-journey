"""Ported from api/Models/LessonCodeComparison.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson


class LessonCodeComparison(Base):
    __tablename__ = "lesson_code_comparisons"
    __table_args__ = (Index("ix_lesson_code_comparisons_lesson_id", "lesson_id"),)

    id: Mapped[int] = mapped_column(
        "id", Integer, server_default=text("nextval('lesson_code_comparisons_id_seq'::regclass)"), primary_key=True
    )
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    before_label: Mapped[str] = mapped_column(String(100), default="Unstructured Concurrency")
    before_language: Mapped[str] = mapped_column(String(50), default="java")
    before_code: Mapped[str] = mapped_column(Text, default="")
    after_label: Mapped[str] = mapped_column(String(100), default="Structured Concurrency")
    after_language: Mapped[str] = mapped_column(String(50), default="java")
    after_code: Mapped[str] = mapped_column(Text, default="")
    explanation: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer, server_default=text("0"), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="code_comparisons", lazy="raise"
    )
