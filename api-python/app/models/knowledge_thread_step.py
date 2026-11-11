"""Ported from api/Models/KnowledgeThreadStep.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .knowledge_concept import KnowledgeConcept
    from .knowledge_thread import KnowledgeThread
    from .lesson import Lesson


class KnowledgeThreadStep(Base):
    __tablename__ = "knowledge_thread_steps"
    __table_args__ = (
        Index("ix_knowledge_thread_steps_concept", "concept_id"),
        Index("IX_knowledge_thread_steps_LessonId", "lesson_id"),
        CheckConstraint("length(trim(label)) > 0", name="ck_knowledge_thread_step_label"),
    )

    thread_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_threads.Id", ondelete="CASCADE"), primary_key=True
    )
    order_index: Mapped[int] = mapped_column(primary_key=True)
    concept_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="SET NULL")
    )
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    label: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    thread: Mapped[KnowledgeThread | None] = relationship(
        "KnowledgeThread", back_populates="steps", lazy="raise"
    )
    concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept", back_populates="thread_steps", lazy="raise"
    )
    lesson: Mapped[Lesson | None] = relationship("Lesson", lazy="raise")
