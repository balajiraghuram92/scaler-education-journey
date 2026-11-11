"""Ported from api/Models/CourseModule.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .course import Course
    from .lesson import Lesson


class CourseModule(Base):
    __tablename__ = "course_modules"
    __table_args__ = (
        Index("IX_course_modules_CourseId_Slug", "course_id", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    badge: Mapped[str] = mapped_column(String(50))
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    course: Mapped[Course | None] = relationship(
        "Course", back_populates="modules", lazy="raise"
    )
    lessons: Mapped[list[Lesson]] = relationship(
        "Lesson", back_populates="module", lazy="raise"
    )
