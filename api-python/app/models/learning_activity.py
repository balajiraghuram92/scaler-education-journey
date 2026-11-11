"""Ported from api/Models/LearningActivity.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .types import JsonbText

if TYPE_CHECKING:
    from .app_user import AppUser
    from .lesson import Lesson
    from .problem import Problem
    from .reading_map_item import ReadingMapItem
    from .study_task import StudyTask


class LearningActivity(Base):
    __tablename__ = "learning_activity"
    __table_args__ = (
        Index("ix_learning_activity_occurred_at", "occurred_at"),
        Index("IX_learning_activity_ProblemId", "problem_id"),
        Index("IX_learning_activity_ReadingMapItemId", "reading_map_item_id"),
        Index("IX_learning_activity_TaskId", "task_id"),
        Index(
            "ux_learning_activity_correlation_event",
            "correlation_id",
            "event_type",
            unique=True,
        ),
        Index("ix_learning_activity_lesson", "lesson_id"),
        Index("ix_learning_activity_user", "user_id", "occurred_at"),
        CheckConstraint(
            "event_type::text = ANY (ARRAY['LessonCompleted'::character varying,"
            " 'LessonReopened'::character varying, 'ProblemCompleted'::character varying,"
            " 'ProblemReopened'::character varying, 'TaskCompleted'::character varying,"
            " 'TaskReopened'::character varying, 'ReadingScheduled'::character varying,"
            " 'ReadingDeferred'::character varying, 'ReadingRevisited'::character varying,"
            " 'NoteCreated'::character varying, 'ChapterImported'::character varying,"
            " 'LessonOpened'::character varying, 'McqAnswered'::character varying,"
            " 'ProblemAttempted'::character varying, 'SolutionRevealed'::character varying,"
            " 'ExerciseRun'::character varying]::text[])",
            name="ck_learning_activity_event_type",
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, Identity(), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(40), default="")
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("app_users.id", ondelete="CASCADE")
    )
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problems.id", ondelete="SET NULL")
    )
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("Tasks.Id", ondelete="SET NULL")
    )
    reading_map_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("reading_map_items.Id", ondelete="SET NULL")
    )
    correlation_id: Mapped[UUID] = mapped_column(Uuid, default=uuid4)
    metadata_json: Mapped[str] = mapped_column(
        "metadata", JsonbText, server_default=text("'{}'::jsonb"), default="{}"
    )

    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")
    lesson: Mapped[Lesson | None] = relationship("Lesson", lazy="raise")
    problem: Mapped[Problem | None] = relationship("Problem", lazy="raise")
    task: Mapped[StudyTask | None] = relationship("StudyTask", lazy="raise")
    reading_map_item: Mapped[ReadingMapItem | None] = relationship(
        "ReadingMapItem", lazy="raise"
    )
