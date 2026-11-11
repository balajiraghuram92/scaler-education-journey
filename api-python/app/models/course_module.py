"""Ported from api/Models/CourseModule.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .course import Course
    from .lesson import Lesson


class CourseModule(Base):
    __tablename__ = "course_modules"
    __table_args__ = (
        Index("IX_course_modules_course_id_slug", "course_id", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(100), default="")
    title: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    badge: Mapped[str] = mapped_column(String(50), default="")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    course: Mapped[Course | None] = relationship(
        "Course", back_populates="modules", lazy="raise"
    )
    lessons: Mapped[list[Lesson]] = relationship(
        "Lesson", back_populates="module", lazy="raise"
    )
