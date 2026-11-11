"""Ported from api/Models/Problem.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson
    from .study_task_content_link import StudyTaskContentLink


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (
        Index("IX_problems_LessonId_Slug", "lesson_id", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200))
    difficulty: Mapped[str] = mapped_column(String(50))
    package_name: Mapped[str] = mapped_column(String(100))
    test_class_name: Mapped[str] = mapped_column(String(100))
    problem_statement: Mapped[str] = mapped_column(Text)
    requirements_body: Mapped[str] = mapped_column(Text)
    worked_example: Mapped[str] = mapped_column(Text)
    hints: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20))
    run_command: Mapped[str] = mapped_column(String(200))
    reference_solution: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(30))
    is_completed: Mapped[bool] = mapped_column(Boolean)
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="problems", lazy="raise"
    )
    legacy_task_links: Mapped[list[StudyTaskContentLink]] = relationship(
        "StudyTaskContentLink", back_populates="problem", lazy="raise"
    )
