"""Translated from BridgeSchemaConstraintTests.cs.

Unlike the C# version (EF InMemory, no enforcement), these tests run against the
scratch Postgres database, so the check constraints are enforced for real.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.learning_activity import LearningActivity
from app.models.lesson import Lesson
from app.models.lesson_relation import LessonRelation
from app.models.problem import Problem
from app.models.study_task import StudyTask
from app.models.study_task_content_link import StudyTaskContentLink
from app.models.study_vertical import StudyVertical


def _now() -> datetime:
    return datetime.now(UTC)


@pytest.mark.asyncio
async def test_study_task_content_link_enforces_exactly_one_target(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    now = _now()
    vertical = StudyVertical(name="V", description="d", updated_at=now)
    db.add(vertical)
    await db.flush()
    task = StudyTask(vertical_id=vertical.id, title="T", is_completed=False, module="M", updated_at=now)
    db.add(task)
    await db.flush()

    # Both null violates the exactly-one-target check.
    db.add(
        StudyTaskContentLink(
            task_id=task.id, mapping_type="Manual", mapping_status="Proposed",
            confidence=Decimal("1.0"), source_checksum="x",
            created_at=now, updated_at=now,
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    # Both set violates it too.
    course = Course(slug="c", title="t", description="d", order_index=1, path_type="Course", is_published=True, created_at=now, updated_at=now)
    db.add(course)
    await db.flush()
    module = CourseModule(course_id=course.id, slug="m", title="M", description="d", badge="M", order_index=1, created_at=now, updated_at=now)
    db.add(module)
    await db.flush()
    lesson = Lesson(module_id=module.id, slug="l", title="L", description="", lecture_number=1, class_date="", content_body="", estimated_minutes=10, is_completed=False, difficulty="Intermediate", created_at=now, updated_at=now)
    db.add(lesson)
    await db.flush()
    problem = Problem(
        lesson_id=lesson.id, slug="p", title="P", difficulty="Warm-up",
        package_name="", test_class_name="", problem_statement="",
        requirements_body="", worked_example="", hints="", language="python",
        run_command="", reference_solution="", source_type="FROM_MATERIAL",
        is_completed=False, order_index=0, created_at=now, updated_at=now,
    )
    db.add(problem)
    await db.flush()
    db.add(
        StudyTaskContentLink(
            task_id=task.id, lesson_id=lesson.id, problem_id=problem.id,
            mapping_type="Manual", mapping_status="Proposed",
            confidence=Decimal("1.0"), source_checksum="x",
            created_at=now, updated_at=now,
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()


@pytest.mark.asyncio
async def test_lesson_relation_enforces_target_rule(scratch_session: AsyncSession) -> None:
    db = scratch_session
    now = _now()
    course = Course(slug="c", title="t", description="d", order_index=1, path_type="Course", is_published=True, created_at=now, updated_at=now)
    db.add(course)
    await db.flush()
    module = CourseModule(course_id=course.id, slug="m", title="M", description="d", badge="M", order_index=1, created_at=now, updated_at=now)
    db.add(module)
    await db.flush()
    lesson = Lesson(module_id=module.id, slug="l", title="L", description="", lecture_number=1, class_date="", content_body="", estimated_minutes=10, is_completed=False, difficulty="Intermediate", created_at=now, updated_at=now)
    db.add(lesson)
    await db.flush()

    db.add(
        LessonRelation(
            source_lesson_id=lesson.id, target_lesson_id=None, target_title="   ",
            relationship_type="Related", resolution_status="Unresolved",
            order_index=0, created_at=now, updated_at=now,
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()


@pytest.mark.asyncio
async def test_learning_activity_accepts_known_event_types(scratch_session: AsyncSession) -> None:
    db = scratch_session
    known_events = [
        "LessonCompleted", "LessonReopened", "ProblemCompleted", "ProblemReopened",
        "TaskCompleted", "TaskReopened", "ReadingScheduled", "ReadingDeferred",
        "ReadingRevisited", "NoteCreated", "ChapterImported",
    ]
    for event_type in known_events:
        db.add(
            LearningActivity(
                event_type=event_type, occurred_at=_now(), metadata_json="{}",
            )
        )
    await db.flush()

    db.add(
        LearningActivity(event_type="BogusEvent", occurred_at=_now(), metadata_json="{}")
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()
