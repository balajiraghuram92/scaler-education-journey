"""Ported from api/Models/ConceptNextLesson.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .knowledge_concept import KnowledgeConcept
    from .lesson import Lesson


class ConceptNextLesson(Base):
    __tablename__ = "concept_next_lessons"
    __table_args__ = (
        Index("IX_concept_next_lessons_concept_id", "concept_id"),
        Index("IX_concept_next_lessons_lesson_id", "lesson_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="CASCADE")
    )
    lesson_title: Mapped[str] = mapped_column(String(300), default="")
    module_name: Mapped[str] = mapped_column(String(200), default="")
    lesson_slug: Mapped[str] = mapped_column(String(150), default="")
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept", back_populates="next_lessons", lazy="raise"
    )
    lesson: Mapped[Lesson | None] = relationship("Lesson", lazy="raise")
