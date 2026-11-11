"""Ported from api/Services/CurriculumImportService.cs."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.course import Course
from ..models.knowledge_concept import KnowledgeConcept
from ..models.learning_activity import LearningActivity
from ..models.lesson import Lesson
from ..models.lesson_concept_link import LessonConceptLink
from ..models.lesson_relation import LessonRelation
from ..schemas.base import CamelModel
from ..stjson import dumps as _json_dumps
from .reconciliation.normalization_helper import generate_slug

logger = logging.getLogger(__name__)


class LessonRelationImportDto(CamelModel):
    target_title: str | None = ""
    target_slug: str | None = None
    relationship_type: str | None = "Related"  # Prerequisite, Related, Next


class CurriculumImportRequest(CamelModel):
    course_slug: str | None = ""
    module_slug: str | None = ""
    lesson_slug: str | None = ""
    title: str | None = ""
    description: str | None = ""
    content_body: str | None = ""
    difficulty: str | None = "Intermediate"
    content_status: str | None = "Published"  # Outline, Draft, Published, Archived
    estimated_minutes: int = 45
    concept_slugs: list[str] = Field(default_factory=list)
    relations: list[LessonRelationImportDto] = Field(default_factory=list)
    correlation_id: UUID = Field(default_factory=uuid4)


class CurriculumImportResult(CamelModel):
    success: bool = False
    lesson_id: int | None = None
    canonical_url: str | None = None
    unresolved_relations: list[str] = Field(default_factory=list)
    error: str | None = None


class CurriculumImportService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def import_chapter(
        self, request: CurriculumImportRequest
    ) -> CurriculumImportResult:
        # 1. Validate Input Limits
        if not request.course_slug or not request.course_slug.strip() or not request.module_slug or not request.module_slug.strip():
            return CurriculumImportResult(
                success=False,
                error="Explicit CourseSlug and ModuleSlug are required. Silent fallbacks are prohibited.",
            )
        if not request.title or not request.title.strip() or len(request.title) > 250:
            return CurriculumImportResult(
                success=False,
                error="Lesson Title is required and must not exceed 250 characters.",
            )
        if request.content_body is not None and len(request.content_body) > 500_000:
            return CurriculumImportResult(
                success=False,
                error="ContentBody exceeds maximum size limit (500 KB).",
            )

        # 2. Validate Explicit Destination Existence
        course = (
            await self._session.execute(
                select(Course)
                .options(selectinload(Course.modules))
                .where(Course.slug == request.course_slug)
            )
        ).scalar_one_or_none()
        if course is None:
            return CurriculumImportResult(
                success=False,
                error=f"Target course '{request.course_slug}' does not exist. Create the course first.",
            )
        module = next(
            (m for m in course.modules if m.slug == request.module_slug), None
        )
        if module is None:
            return CurriculumImportResult(
                success=False,
                error=f"Target module '{request.module_slug}' does not exist in course '{request.course_slug}'.",
            )

        lesson_slug = (
            generate_slug(request.title)
            if not request.lesson_slug or not request.lesson_slug.strip()
            else request.lesson_slug
        )

        try:
            lesson = (
                await self._session.execute(
                    select(Lesson)
                    .options(
                        selectinload(Lesson.concept_links),
                        selectinload(Lesson.outgoing_relations),
                    )
                    .where(Lesson.module_id == module.id, Lesson.slug == lesson_slug)
                )
            ).scalar_one_or_none()
            now = self._utcnow()
            if lesson is None:
                lesson = Lesson(
                    module_id=module.id,
                    slug=lesson_slug,
                    title=request.title,
                    # C# leaves LectureNumber unset (implicit CLR default 0);
                    # SQLAlchemy has no implicit default, so pass it explicitly.
                    lecture_number=0,
                    description=request.description
                    if request.description is not None
                    else "",
                    content_body=request.content_body
                    if request.content_body is not None
                    else "",
                    difficulty=request.difficulty
                    if request.difficulty is not None
                    else "Intermediate",
                    content_status=request.content_status
                    if request.content_status is not None
                    else "Published",
                    estimated_minutes=request.estimated_minutes
                    if request.estimated_minutes > 0
                    else 45,
                    is_completed=False,
                    created_at=now,
                    updated_at=now,
                )
                self._session.add(lesson)
                await self._session.flush()
            else:
                lesson.title = request.title
                lesson.description = (
                    request.description
                    if request.description is not None
                    else lesson.description
                )
                lesson.content_body = (
                    request.content_body
                    if request.content_body is not None
                    else lesson.content_body
                )
                lesson.difficulty = (
                    request.difficulty
                    if request.difficulty is not None
                    else lesson.difficulty
                )
                lesson.content_status = (
                    request.content_status
                    if request.content_status is not None
                    else lesson.content_status
                )
                lesson.estimated_minutes = (
                    request.estimated_minutes
                    if request.estimated_minutes > 0
                    else lesson.estimated_minutes
                )
                lesson.updated_at = now

            # Link Concepts
            for concept_slug in request.concept_slugs:
                concept = (
                    await self._session.execute(
                        select(KnowledgeConcept).where(
                            KnowledgeConcept.slug == concept_slug
                        )
                    )
                ).scalar_one_or_none()
                if concept is not None:
                    existing_link = await self._session.get(
                        LessonConceptLink, (lesson.id, concept.id, "Related")
                    )
                    if existing_link is None:
                        self._session.add(
                            LessonConceptLink(
                                lesson_id=lesson.id,
                                concept_id=concept.id,
                                relationship_type="Related",
                                order_index=0,
                                created_at=self._utcnow(),
                            )
                        )

            # Persist Lesson Relations
            unresolved: list[str] = []
            for rel in request.relations:
                target_lesson = None
                if rel.target_slug and rel.target_slug.strip():
                    target_lesson = (
                        await self._session.execute(
                            select(Lesson).where(Lesson.slug == rel.target_slug)
                        )
                    ).scalar_one_or_none()
                resolution_status = "Resolved" if target_lesson is not None else "Unresolved"
                if target_lesson is None:
                    unresolved.append(rel.target_title or "")
                now = self._utcnow()
                self._session.add(
                    LessonRelation(
                        source_lesson_id=lesson.id,
                        target_lesson_id=target_lesson.id if target_lesson is not None else None,
                        # Explicit nulls flow to the database and fail there, as in C#.
                        target_title=rel.target_title,  # type: ignore[arg-type]
                        target_slug=rel.target_slug,
                        relationship_type=rel.relationship_type,  # type: ignore[arg-type]
                        resolution_status=resolution_status,
                        order_index=0,
                        created_at=now,
                        updated_at=now,
                    )
                )

            # Record ChapterImported LearningActivity with correlation idempotency
            existing_activity = (
                await self._session.execute(
                    select(LearningActivity).where(
                        LearningActivity.correlation_id == request.correlation_id,
                        LearningActivity.event_type == "ChapterImported",
                    )
                )
            ).scalar_one_or_none()
            if existing_activity is None:
                self._session.add(
                    LearningActivity(
                        event_type="ChapterImported",
                        lesson_id=lesson.id,
                        correlation_id=request.correlation_id,
                        occurred_at=self._utcnow(),
                        metadata_json=_json_dumps(
                        {
                            "Course": request.course_slug,
                            "Module": request.module_slug,
                            "Lesson": lesson_slug,
                        }
                    ),
                    )
                )

            await self._session.flush()
            return CurriculumImportResult(
                success=True,
                lesson_id=lesson.id,
                canonical_url=f"/learning-paths/{request.course_slug}/{request.module_slug}/{lesson_slug}",
                unresolved_relations=unresolved,
            )
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                "Failed to import chapter into %s/%s (CorrelationId: %s): %s",
                request.course_slug,
                request.module_slug,
                request.correlation_id,
                exc,
            )
            return CurriculumImportResult(
                success=False,
                error="An internal error occurred while saving the chapter. Please reference the correlation ID for support.",
            )
