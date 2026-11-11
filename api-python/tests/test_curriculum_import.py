"""Translated from CurriculumImportTests.cs, plus service coverage on the scratch DB."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.course_module import CourseModule
from app.services.curriculum_import_service import (
    CurriculumImportRequest,
    CurriculumImportService,
)


def test_curriculum_import_request_validation() -> None:
    req = CurriculumImportRequest(
        course_slug="java-spring-lld",
        module_slug="concurrency",
        title="Virtual Threads & Structured Concurrency",
        estimated_minutes=60,
        content_status="Published",
    )

    assert req.course_slug == "java-spring-lld"
    assert req.module_slug == "concurrency"
    assert req.title == "Virtual Threads & Structured Concurrency"
    assert req.content_status == "Published"


async def _seed_course(db: AsyncSession) -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    course = Course(
        slug="java-spring-lld",
        title="Java",
        description="d",
        order_index=0,
        path_type="Course",
        is_published=True,
        created_at=now,
        updated_at=now,
    )
    db.add(course)
    await db.flush()
    module = CourseModule(
        course_id=course.id,
        slug="concurrency",
        title="Concurrency",
        description="d",
        badge="M",
        order_index=0,
        created_at=now,
        updated_at=now,
    )
    db.add(module)
    await db.flush()
    return course.id, module.id


@pytest.mark.asyncio
async def test_import_chapter_creates_lesson_and_canonical_url(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    await _seed_course(db)
    service = CurriculumImportService(db)

    result = await service.import_chapter(
        CurriculumImportRequest(
            course_slug="java-spring-lld",
            module_slug="concurrency",
            lesson_slug="virtual-threads",
            title="Virtual Threads",
            description="d",
            content_body="body",
        )
    )

    assert result.success is True
    assert result.lesson_id is not None
    assert (
        result.canonical_url
        == "/learning-paths/java-spring-lld/concurrency/virtual-threads"
    )
    assert result.unresolved_relations == []


@pytest.mark.asyncio
async def test_import_chapter_rejects_unknown_course_and_bad_title(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    await _seed_course(db)
    service = CurriculumImportService(db)

    missing = await service.import_chapter(
        CurriculumImportRequest(course_slug="nope", module_slug="concurrency", title="T")
    )
    assert missing.success is False
    assert missing.error is not None and "nope" in missing.error

    blank = await service.import_chapter(
        CurriculumImportRequest(course_slug="java-spring-lld", module_slug="concurrency")
    )
    assert blank.success is False
    assert blank.error is not None and "Title" in blank.error


@pytest.mark.asyncio
async def test_import_chapter_is_idempotent_on_correlation_id(
    scratch_session: AsyncSession,
) -> None:
    from sqlalchemy import func, select

    from app.models.learning_activity import LearningActivity
    from app.models.lesson import Lesson

    db = scratch_session
    await _seed_course(db)
    service = CurriculumImportService(db)
    correlation_id = uuid4()

    def _request() -> CurriculumImportRequest:
        return CurriculumImportRequest(
            course_slug="java-spring-lld",
            module_slug="concurrency",
            lesson_slug="idem-lesson",
            title="Idempotent",
            correlation_id=correlation_id,
        )

    first = await service.import_chapter(_request())
    second = await service.import_chapter(_request())

    assert first.success is True
    assert second.success is True
    assert first.lesson_id == second.lesson_id
    lesson_count = (
        await db.execute(
            select(func.count(Lesson.id)).where(Lesson.slug == "idem-lesson")
        )
    ).scalar_one()
    assert lesson_count == 1
    activity_count = (
        await db.execute(
            select(func.count(LearningActivity.id)).where(
                LearningActivity.correlation_id == correlation_id,
                LearningActivity.event_type == "ChapterImported",
            )
        )
    ).scalar_one()
    assert activity_count == 1
