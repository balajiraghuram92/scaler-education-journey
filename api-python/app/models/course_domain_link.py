"""Ported from api/Models/CourseDomainLink.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .course import Course
    from .knowledge_domain import KnowledgeDomain


class CourseDomainLink(Base):
    __tablename__ = "course_domain_links"
    __table_args__ = (
        Index("ix_course_domain_links_domain_id", "domain_id", "order_index"),
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )
    domain_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_domains.id", ondelete="CASCADE"), primary_key=True
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), default=False
    )
    order_index: Mapped[int] = mapped_column(Integer, server_default=text("0"), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )

    course: Mapped[Course | None] = relationship(
        "Course", back_populates="domain_links", lazy="raise"
    )
    domain: Mapped[KnowledgeDomain | None] = relationship(
        "KnowledgeDomain", back_populates="course_links", lazy="raise"
    )
