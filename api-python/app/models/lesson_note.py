"""Ported from api/Models/LessonNote.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .app_user import AppUser
    from .lesson import Lesson


class LessonNote(Base):
    __tablename__ = "lesson_notes"
    __table_args__ = (
        Index("ix_lesson_notes_lesson_id_note_type", "lesson_id", "note_type"),
        Index("ix_lesson_notes_user_lesson", "user_id", "lesson_id"),
    )

    id: Mapped[int] = mapped_column(
        "id", Integer, server_default=text("nextval('lesson_notes_id_seq'::regclass)"), primary_key=True
    )
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("app_users.id", ondelete="CASCADE")
    )
    note_type: Mapped[str] = mapped_column(
        String(50), server_default=text("'FieldNote'"), default="FieldNote"
    )
    anchor_section: Mapped[str | None] = mapped_column(String(150))
    title: Mapped[str] = mapped_column(String(250), default="")
    content_body: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer, server_default=text("0"), default=0)
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

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="notes", lazy="raise"
    )
    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")
