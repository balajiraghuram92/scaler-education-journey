"""Ported from api/Models/StudyTaskContentLink.cs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson
    from .problem import Problem
    from .study_task import StudyTask


class StudyTaskContentLink(Base):
    __tablename__ = "study_task_content_links"
    __table_args__ = (
        Index("ix_task_content_links_lesson", "lesson_id"),
        Index("ix_task_content_links_problem", "problem_id"),
        CheckConstraint(
            "num_nonnulls(lesson_id, problem_id) = 1",
            name="ck_task_content_exactly_one_target",
        ),
        CheckConstraint(
            "mapping_type IN ('Exact', 'TitleAndModule', 'Manual', 'DuplicateAlias')",
            name="ck_task_content_mapping_type",
        ),
        CheckConstraint(
            "mapping_status IN ('Proposed', 'Verified', 'Rejected')",
            name="ck_task_content_mapping_status",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1", name="ck_task_content_confidence"
        ),
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey("Tasks.Id", ondelete="CASCADE"), primary_key=True
    )
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="RESTRICT")
    )
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problems.id", ondelete="RESTRICT")
    )
    mapping_type: Mapped[str] = mapped_column(String(32))
    mapping_status: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    source_checksum: Mapped[str] = mapped_column(String(64))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    task: Mapped[StudyTask | None] = relationship(
        "StudyTask", back_populates="content_link", lazy="raise"
    )
    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="legacy_task_links", lazy="raise"
    )
    problem: Mapped[Problem | None] = relationship(
        "Problem", back_populates="legacy_task_links", lazy="raise"
    )
