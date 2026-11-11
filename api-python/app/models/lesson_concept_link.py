"""Ported from api/Models/LessonConceptLink.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .knowledge_concept import KnowledgeConcept
    from .lesson import Lesson


class LessonConceptLink(Base):
    __tablename__ = "lesson_concept_links"
    __table_args__ = (
        Index(
            "ix_lesson_concept_links_concept",
            "concept_id",
            "relationship_type",
            "order_index",
        ),
        CheckConstraint(
            "relationship_type IN ('Primary', 'Related', 'PrerequisiteContext')",
            name="ck_lesson_concept_relationship",
        ),
    )

    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True
    )
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="CASCADE"), primary_key=True
    )
    relationship_type: Mapped[str] = mapped_column(String(32), primary_key=True)
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    lesson: Mapped[Lesson | None] = relationship(
        "Lesson", back_populates="concept_links", lazy="raise"
    )
    concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept", back_populates="lesson_links", lazy="raise"
    )
