"""Ported from api/Models/ConceptNextLesson.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .knowledge_concept import KnowledgeConcept
    from .lesson import Lesson


class ConceptNextLesson(Base):
    __tablename__ = "concept_next_lessons"
    __table_args__ = (
        Index("IX_concept_next_lessons_ConceptId", "concept_id"),
        Index("IX_concept_next_lessons_LessonId", "lesson_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="CASCADE")
    )
    lesson_title: Mapped[str] = mapped_column(String(300))
    module_name: Mapped[str] = mapped_column(String(200))
    lesson_slug: Mapped[str] = mapped_column(String(150))
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    order_index: Mapped[int] = mapped_column(Integer)

    concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept", back_populates="next_lessons", lazy="raise"
    )
    lesson: Mapped[Lesson | None] = relationship("Lesson", lazy="raise")
