"""Ported from api/Models/KnowledgeConcept.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .concept_next_lesson import ConceptNextLesson
    from .concept_prerequisite import ConceptPrerequisite
    from .concept_relation import ConceptRelation
    from .domain_concept_connection import DomainConceptConnection
    from .knowledge_thread_step import KnowledgeThreadStep
    from .lesson_concept_link import LessonConceptLink


class KnowledgeConcept(Base):
    __tablename__ = "knowledge_concepts"
    __table_args__ = (Index("IX_knowledge_concepts_Slug", "slug", unique=True),)

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200))
    sub_label: Mapped[str] = mapped_column("sub_label", Text)
    summary: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(50))
    icon: Mapped[str] = mapped_column(String(100))
    estimated_hours: Mapped[int] = mapped_column(Integer)
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    domain_connections: Mapped[list[DomainConceptConnection]] = relationship(
        "DomainConceptConnection", back_populates="concept", lazy="raise"
    )
    prerequisites: Mapped[list[ConceptPrerequisite]] = relationship(
        "ConceptPrerequisite",
        back_populates="concept",
        foreign_keys="ConceptPrerequisite.concept_id",
        lazy="raise",
    )
    prerequisite_for: Mapped[list[ConceptPrerequisite]] = relationship(
        "ConceptPrerequisite",
        back_populates="prerequisite_concept",
        foreign_keys="ConceptPrerequisite.prerequisite_concept_id",
        lazy="raise",
    )
    outgoing_relations: Mapped[list[ConceptRelation]] = relationship(
        "ConceptRelation",
        back_populates="source_concept",
        foreign_keys="ConceptRelation.source_concept_id",
        lazy="raise",
    )
    incoming_relations: Mapped[list[ConceptRelation]] = relationship(
        "ConceptRelation",
        back_populates="target_concept",
        foreign_keys="ConceptRelation.target_concept_id",
        lazy="raise",
    )
    next_lessons: Mapped[list[ConceptNextLesson]] = relationship(
        "ConceptNextLesson", back_populates="concept", lazy="raise"
    )
    lesson_links: Mapped[list[LessonConceptLink]] = relationship(
        "LessonConceptLink", back_populates="concept", lazy="raise"
    )
    thread_steps: Mapped[list[KnowledgeThreadStep]] = relationship(
        "KnowledgeThreadStep", back_populates="concept", lazy="raise"
    )
