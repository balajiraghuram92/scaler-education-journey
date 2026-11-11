"""Ported from api/Models/LessonDiagram.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson


class LessonDiagram(Base):
    __tablename__ = "lesson_diagrams"
    __table_args__ = (Index("ix_lesson_diagrams_lesson_id", "lesson_id"),)

    id: Mapped[int] = mapped_column(
        "id", Integer, server_default=text("nextval('lesson_diagrams_id_seq'::regclass)"), primary_key=True
    )
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), default="")
    caption: Mapped[str] = mapped_column(String(300), default="")
    diagram_type: Mapped[str] = mapped_column(
        String(50), server_default=text("'svg-inline'"), default="svg-inline"
    )
    svg_content: Mapped[str] = mapped_column(Text, default="")
    diagram_spec_json: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, server_default=text("0"), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="diagrams", lazy="raise"
    )
