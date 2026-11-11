"""Ported from api/Models/ReadingMapItem.cs."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    text,
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
        Index(
            "ix_reading_map_status_schedule", "status", "scheduled_for", "priority"
        ),
        CheckConstraint(
            "status::text = ANY (ARRAY['Planned'::character varying, 'Reading'::character varying, 'Completed'::character varying, 'Revisited'::character varying, 'Deferred'::character varying, 'Archived'::character varying]::text[])",
            name="ck_reading_map_status",
        ),
        CheckConstraint(
            "priority >= 0 AND priority <= 100", name="ck_reading_map_priority"
        ),
    )

    id: Mapped[int] = mapped_column("Id", Integer, Identity(), primary_key=True)
    category: Mapped[str] = mapped_column("Category", Text, default="")
    title: Mapped[str] = mapped_column("Title", Text, default="")
    sub_text: Mapped[str | None] = mapped_column("SubText", Text)
    order_index: Mapped[int] = mapped_column("OrderIndex", Integer)
    is_completed: Mapped[bool] = mapped_column("IsCompleted", Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        "CreatedAt", DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        "UpdatedAt", DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("Tasks.Id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(
        String(32), server_default=text("'Planned'"), default="Planned"
    )
    scheduled_for: Mapped[date | None] = mapped_column(Date)
    priority: Mapped[int] = mapped_column(Integer, server_default=text("0"), default=0)
    is_seeded: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), default=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="reading_map_items", lazy="raise"
    )
    task: Mapped[StudyTask | None] = relationship("StudyTask", lazy="raise")
