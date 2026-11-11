"""Ported from api/Models/ConceptRelation.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .knowledge_concept import KnowledgeConcept


class ConceptRelation(Base):
    __tablename__ = "concept_relations"
    __table_args__ = (
        Index("IX_concept_relations_target_concept_id", "target_concept_id"),
        Index(
            "IX_concept_relations_source_concept_id_target_concept_id",
            "source_concept_id",
            "target_concept_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    source_concept_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="CASCADE")
    )
    target_concept_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="RESTRICT")
    )
    relationship_type: Mapped[str] = mapped_column(String(50), default="Related")

    source_concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept",
        back_populates="outgoing_relations",
        foreign_keys=[source_concept_id],
        lazy="raise",
    )
    target_concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept",
        back_populates="incoming_relations",
        foreign_keys=[target_concept_id],
        lazy="raise",
    )
