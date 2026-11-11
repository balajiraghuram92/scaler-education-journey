"""Ported from api/Models/Problem.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Identity, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson
    from .study_task_content_link import StudyTaskContentLink


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (
        Index("IX_problems_lesson_id_slug", "lesson_id", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(100), default="")
    title: Mapped[str] = mapped_column(String(200), default="")
    difficulty: Mapped[str] = mapped_column(String(50), default="Warm-up")
    package_name: Mapped[str] = mapped_column(String(100), default="")
    test_class_name: Mapped[str] = mapped_column(String(100), default="")
    problem_statement: Mapped[str] = mapped_column(Text, default="")
    requirements_body: Mapped[str] = mapped_column(Text, default="")
    worked_example: Mapped[str] = mapped_column(Text, default="")
    hints: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(20), server_default=text("'java'"), default="java")
    run_command: Mapped[str] = mapped_column(String(200), server_default=text("''"), default="")
    reference_solution: Mapped[str] = mapped_column(Text, server_default=text("''"), default="")
    source_type: Mapped[str] = mapped_column(
        String(30), server_default=text("'FROM_MATERIAL'"), default="FROM_MATERIAL"
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="problems", lazy="raise"
    )
    legacy_task_links: Mapped[list[StudyTaskContentLink]] = relationship(
        "StudyTaskContentLink", back_populates="problem", lazy="raise"
    )
