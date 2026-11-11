"""Ported from api/Models/StudyTask.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .study_task_content_link import StudyTaskContentLink
    from .study_vertical import StudyVertical


class StudyTask(Base):
    __tablename__ = "Tasks"
    __table_args__ = (Index("IX_Tasks_VerticalId", "VerticalId"),)

    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True)
    vertical_id: Mapped[int] = mapped_column(
        "VerticalId", ForeignKey("Verticals.Id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column("Title", Text)
    is_completed: Mapped[bool] = mapped_column("IsCompleted", Boolean)
    module: Mapped[str] = mapped_column("Module", Text)
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=text("now()")
    )

    vertical: Mapped[StudyVertical | None] = relationship(
        "StudyVertical", back_populates="tasks", lazy="raise"
    )
    content_link: Mapped[StudyTaskContentLink | None] = relationship(
        "StudyTaskContentLink", back_populates="task", uselist=False, lazy="raise"
    )
