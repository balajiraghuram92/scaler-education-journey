"""Ported from api/Models/StudyTaskContentLink.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    text,
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
            "mapping_type::text = ANY (ARRAY['Exact'::character varying, 'TitleAndModule'::character varying, 'Manual'::character varying, 'DuplicateAlias'::character varying]::text[])",
            name="ck_task_content_mapping_type",
        ),
        CheckConstraint(
            "mapping_status::text = ANY (ARRAY['Proposed'::character varying, 'Verified'::character varying, 'Rejected'::character varying]::text[])",
            name="ck_task_content_mapping_status",
        ),
        CheckConstraint(
            "confidence >= 0::numeric AND confidence <= 1::numeric",
            name="ck_task_content_confidence",
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
    mapping_type: Mapped[str] = mapped_column(
        String(32), server_default=text("'TitleAndModule'"), default="TitleAndModule"
    )
    mapping_status: Mapped[str] = mapped_column(
        String(32), server_default=text("'Proposed'"), default="Proposed"
    )
    confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), server_default=text("1.0000"), default=Decimal("1.0000")
    )
    source_checksum: Mapped[str] = mapped_column(String(64), default="")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )

    task: Mapped[StudyTask | None] = relationship(
        "StudyTask", back_populates="content_link", lazy="raise"
    )
    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="legacy_task_links", lazy="raise"
    )
    problem: Mapped[Problem | None] = relationship(
        "Problem", back_populates="legacy_task_links", lazy="raise"
    )
