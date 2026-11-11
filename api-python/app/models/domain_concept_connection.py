"""Ported from api/Models/DomainConceptConnection.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .knowledge_concept import KnowledgeConcept
    from .knowledge_domain import KnowledgeDomain


class DomainConceptConnection(Base):
    __tablename__ = "domain_concept_connections"
    __table_args__ = (
        Index("IX_domain_concept_connections_ConceptId", "concept_id"),
        Index(
            "IX_domain_concept_connections_DomainId_ConceptId",
            "domain_id",
            "concept_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    domain_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_domains.id", ondelete="CASCADE")
    )
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_concepts.id", ondelete="CASCADE")
    )
    is_primary: Mapped[bool] = mapped_column(Boolean)
    relevance_weight: Mapped[int] = mapped_column(Integer)
    role_description: Mapped[str] = mapped_column(String(250))
    order_index: Mapped[int] = mapped_column(Integer)

    domain: Mapped[KnowledgeDomain | None] = relationship(
        "KnowledgeDomain", back_populates="concept_connections", lazy="raise"
    )
    concept: Mapped[KnowledgeConcept | None] = relationship(
        "KnowledgeConcept", back_populates="domain_connections", lazy="raise"
    )
