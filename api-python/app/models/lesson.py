"""Ported from api/Models/Lesson.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .course_module import CourseModule
    from .lesson_code_comparison import LessonCodeComparison
    from .lesson_concept_link import LessonConceptLink
    from .lesson_diagram import LessonDiagram
    from .lesson_note import LessonNote
    from .lesson_relation import LessonRelation
    from .lesson_resource import LessonResource
    from .problem import Problem
    from .reading_map_item import ReadingMapItem
    from .study_task_content_link import StudyTaskContentLink


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        Index("IX_lessons_ModuleId_Slug", "module_id", "slug", unique=True),
        CheckConstraint(
            "content_status IN ('Outline', 'Draft', 'Published', 'Archived')",
            name="ck_lessons_content_status",
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("course_modules.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(150))
    title: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text)
    lecture_number: Mapped[int] = mapped_column(Integer)
    class_date: Mapped[str] = mapped_column(String(50))
    content_body: Mapped[str] = mapped_column(Text)
    horstmann_ref: Mapped[str] = mapped_column(Text)
    estimated_minutes: Mapped[int] = mapped_column(Integer)
    is_completed: Mapped[bool] = mapped_column(Boolean)
    order_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    difficulty: Mapped[str] = mapped_column(String(50))
    content_status: Mapped[str] = mapped_column(String(32), server_default=text("'Published'"))

    module: Mapped[CourseModule | None] = relationship(
        "CourseModule", back_populates="lessons", lazy="raise"
    )
    problems: Mapped[list[Problem]] = relationship(
        "Problem", back_populates="lesson", lazy="raise"
    )
    resources: Mapped[list[LessonResource]] = relationship(
        "LessonResource", back_populates="lesson", lazy="raise"
    )
    code_comparisons: Mapped[list[LessonCodeComparison]] = relationship(
        "LessonCodeComparison", back_populates="lesson", lazy="raise"
    )
    diagrams: Mapped[list[LessonDiagram]] = relationship(
        "LessonDiagram", back_populates="lesson", lazy="raise"
    )
    notes: Mapped[list[LessonNote]] = relationship(
        "LessonNote", back_populates="lesson", lazy="raise"
    )
    concept_links: Mapped[list[LessonConceptLink]] = relationship(
        "LessonConceptLink", back_populates="lesson", lazy="raise"
    )
    outgoing_relations: Mapped[list[LessonRelation]] = relationship(
        "LessonRelation",
        back_populates="source_lesson",
        foreign_keys="LessonRelation.source_lesson_id",
        lazy="raise",
    )
    incoming_relations: Mapped[list[LessonRelation]] = relationship(
        "LessonRelation",
        back_populates="target_lesson",
        foreign_keys="LessonRelation.target_lesson_id",
        lazy="raise",
    )
    legacy_task_links: Mapped[list[StudyTaskContentLink]] = relationship(
        "StudyTaskContentLink", back_populates="lesson", lazy="raise"
    )
    reading_map_items: Mapped[list[ReadingMapItem]] = relationship(
        "ReadingMapItem", back_populates="lesson", lazy="raise"
    )
