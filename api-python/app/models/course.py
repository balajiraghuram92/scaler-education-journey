"""Ported from api/Models/Course.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .course_domain_link import CourseDomainLink
    from .course_module import CourseModule
    from .study_vertical import StudyVertical


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        Index("IX_courses_slug", "slug", unique=True),
        Index("IX_courses_vertical_id", "vertical_id"),
        CheckConstraint(
            "path_type::text = ANY (ARRAY['Course'::character varying, 'Certification'::character varying, 'Project'::character varying]::text[])",
            name="ck_courses_path_type",
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), default="")
    title: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    vertical_id: Mapped[int | None] = mapped_column(ForeignKey("Verticals.Id"))
    path_type: Mapped[str] = mapped_column(
        String(32), server_default=text("'Course'"), default="Course"
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    vertical: Mapped[StudyVertical | None] = relationship("StudyVertical", lazy="raise")
    modules: Mapped[list[CourseModule]] = relationship(
        "CourseModule", back_populates="course", lazy="raise"
    )
    domain_links: Mapped[list[CourseDomainLink]] = relationship(
        "CourseDomainLink", back_populates="course", lazy="raise"
    )
