"""Ported from api/Models/LessonRelation.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .lesson import Lesson


class LessonRelation(Base):
    __tablename__ = "lesson_relations"
    __table_args__ = (
        Index("ix_lesson_relations_target_lesson", "target_lesson_id"),
        Index(
            "ux_lesson_relations_identity",
            "source_lesson_id",
            "relationship_type",
            "target_title",
            unique=True,
        ),
        CheckConstraint(
            "relationship_type::text = ANY (ARRAY['Prerequisite'::character varying, 'Related'::character varying, 'Next'::character varying]::text[])",
            name="ck_lesson_relation_type",
        ),
        CheckConstraint(
            "resolution_status::text = ANY (ARRAY['Unresolved'::character varying, 'Resolved'::character varying, 'External'::character varying]::text[])",
            name="ck_lesson_relation_resolution",
        ),
        CheckConstraint(
            "target_lesson_id IS NOT NULL OR length(TRIM(BOTH FROM target_title)) > 0",
            name="ck_lesson_relation_target",
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, Identity(), primary_key=True)
    source_lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE")
    )
    target_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    target_title: Mapped[str] = mapped_column(String(300), default="")
    target_slug: Mapped[str | None] = mapped_column(String(150))
    relationship_type: Mapped[str] = mapped_column(String(32), default="Related")
    resolution_status: Mapped[str] = mapped_column(
        String(32), server_default=text("'Unresolved'"), default="Unresolved"
    )
    order_index: Mapped[int] = mapped_column(Integer, server_default=text("0"), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )

    source_lesson: Mapped[Lesson | None] = relationship(
        "Lesson",
        back_populates="outgoing_relations",
        foreign_keys=[source_lesson_id],
        lazy="raise",
    )
    target_lesson: Mapped[Lesson | None] = relationship(
        "Lesson",
        back_populates="incoming_relations",
        foreign_keys=[target_lesson_id],
        lazy="raise",
    )
