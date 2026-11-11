"""Ported from api/Models/UserLessonProgress.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .app_user import AppUser
    from .lesson import Lesson


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"
    __table_args__ = (
        Index("IX_user_lesson_progress_LessonId", "lesson_id"),
        Index("ix_user_lesson_progress_user_recent", "user_id", "last_opened_at"),
        Index(
            "ux_user_lesson_progress_user_lesson", "user_id", "lesson_id", unique=True
        ),
        CheckConstraint(
            "status IN ('InProgress', 'Completed')",
            name="ck_user_lesson_progress_status",
        ),
        CheckConstraint(
            "scroll_percent >= 0 AND scroll_percent <= 100",
            name="ck_user_lesson_progress_scroll",
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20))
    first_opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_section_id: Mapped[str | None] = mapped_column(String(160))
    scroll_percent: Mapped[int] = mapped_column(Integer)
    visit_count: Mapped[int] = mapped_column(Integer)
    time_spent_seconds: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")
    lesson: Mapped[Lesson | None] = relationship("Lesson", lazy="raise")

    @property
    def is_completed(self) -> bool:
        return self.status == "Completed"
