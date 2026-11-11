"""Ported from api/Models/KnowledgeDomain.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Identity, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .course_domain_link import CourseDomainLink
    from .domain_concept_connection import DomainConceptConnection


class KnowledgeDomain(Base):
    __tablename__ = "knowledge_domains"
    __table_args__ = (
        Index("IX_knowledge_domains_slug", "slug", unique=True),
        Index("IX_knowledge_domains_code", "code", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), default="")
    name: Mapped[str] = mapped_column(String(200), default="")
    code: Mapped[str] = mapped_column(String(50), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(100), default="layers")
    color_hex: Mapped[str] = mapped_column(String(50), default="#3B82F6")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    concept_connections: Mapped[list[DomainConceptConnection]] = relationship(
        "DomainConceptConnection", back_populates="domain", lazy="raise"
    )
    course_links: Mapped[list[CourseDomainLink]] = relationship(
        "CourseDomainLink", back_populates="domain", lazy="raise"
    )
