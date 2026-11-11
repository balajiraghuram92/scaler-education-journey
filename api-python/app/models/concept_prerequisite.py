"""Ported from api/Models/ConceptPrerequisite.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .knowledge_concept import KnowledgeConcept


class ConceptPrerequisite(Base):
    __tablename__ = "concept_prerequisites"
    __table_args__ = (
        Index("IX_concept_prerequisites_PrerequisiteConceptId", "prerequisite_concept_id"),
        Index(
            "IX_concept_prerequisites_ConceptId_PrerequisiteConceptId",
            "concept_id",
            "prerequisite_concept_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="CASCADE")
    )
    prerequisite_concept_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(50))

    concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept",
        back_populates="prerequisites",
        foreign_keys=[concept_id],
        lazy="raise",
    )
    prerequisite_concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept",
        back_populates="prerequisite_for",
        foreign_keys=[prerequisite_concept_id],
        lazy="raise",
    )
