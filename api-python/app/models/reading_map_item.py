"""Ported from api/Models/ReadingMapItem.cs."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson
    from .study_task import StudyTask


class ReadingMapItem(Base):
    __tablename__ = "reading_map_items"
    __table_args__ = (
        Index("IX_reading_map_items_Category", "Category"),
        Index("IX_reading_map_items_LessonId", "lesson_id"),
        Index("IX_reading_map_items_TaskId", "task_id"),
        Index(
            "ix_reading_map_status_schedule", "status", "scheduled_for", "priority"
        ),
        CheckConstraint(
            "status IN ('Planned', 'Reading', 'Completed', 'Revisited', 'Deferred', 'Archived')",
            name="ck_reading_map_status",
        ),
        CheckConstraint("priority BETWEEN 0 AND 100", name="ck_reading_map_priority"),
    )

    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True)
    category: Mapped[str] = mapped_column("Category", Text)
    title: Mapped[str] = mapped_column("Title", Text)
    sub_text: Mapped[str | None] = mapped_column("SubText", Text)
    order_index: Mapped[int] = mapped_column("OrderIndex", Integer)
    is_completed: Mapped[bool] = mapped_column("IsCompleted", Boolean)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime(timezone=True))
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("Tasks.Id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(String(32))
    scheduled_for: Mapped[date | None] = mapped_column(Date)
    priority: Mapped[int] = mapped_column(Integer)
    is_seeded: Mapped[bool] = mapped_column(Boolean)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="reading_map_items", lazy="raise"
    )
    task: Mapped[StudyTask | None] = relationship("StudyTask", lazy="raise")
