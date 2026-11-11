"""Ported from api/Models/McqQuestion.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Identity, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson
    from .mcq_option import McqOption
    from .mcq_presentation import McqPresentation


class McqQuestion(Base):
    __tablename__ = "mcq_questions"
    __table_args__ = (
        Index("ux_mcq_questions_legacy_key", "legacy_key", unique=True),
        Index("ix_mcq_questions_lesson_id", "lesson_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    legacy_key: Mapped[str | None] = mapped_column(String(120))
    question_text: Mapped[str] = mapped_column(Text, default="")
    source_type: Mapped[str] = mapped_column(String(50), default="")
    explanation: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(30), server_default=text("'Assignment'"), default="Assignment")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    lesson: Mapped[Lesson | None] = relationship("Lesson", lazy="raise")
    options: Mapped[list[McqOption]] = relationship(
        "McqOption", back_populates="question", lazy="raise"
    )
    presentations: Mapped[list[McqPresentation]] = relationship(
        "McqPresentation", back_populates="question", lazy="raise"
    )
