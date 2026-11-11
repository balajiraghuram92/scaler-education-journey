"""Ported from api/Models/LessonResource.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson


class LessonResource(Base):
    __tablename__ = "lesson_resources"
    __table_args__ = (Index("IX_lesson_resources_lesson_id", "lesson_id"),)

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    resource_type: Mapped[str] = mapped_column(String(50), default="StudyGuideTopic")
    title: Mapped[str] = mapped_column(String(250), default="")
    content_body: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="resources", lazy="raise"
    )
