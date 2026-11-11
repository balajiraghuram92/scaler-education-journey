"""Ported from api/Models/KnowledgeDomain.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .course_domain_link import CourseDomainLink
    from .domain_concept_connection import DomainConceptConnection


class KnowledgeDomain(Base):
    __tablename__ = "knowledge_domains"
    __table_args__ = (
        Index("IX_knowledge_domains_Slug", "slug", unique=True),
        Index("IX_knowledge_domains_Code", "code", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(String(100))
    color_hex: Mapped[str] = mapped_column(String(50))
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    concept_connections: Mapped[list[DomainConceptConnection]] = relationship(
        "DomainConceptConnection", back_populates="domain", lazy="raise"
    )
    course_links: Mapped[list[CourseDomainLink]] = relationship(
        "CourseDomainLink", back_populates="domain", lazy="raise"
    )
