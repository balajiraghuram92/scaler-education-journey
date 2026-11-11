"""Learner-progress/MCQ tests from tests/StudyTracker.Api.Tests/SessionAndLearnerStateTests.cs.

Translated in P3 (this file) rather than P2 because they exercise
LearnerProgressService and McqService. Uses the scratch database; the fixture
rolls back after every test.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.mcq_option import McqOption
from app.models.mcq_question import McqQuestion
from app.models.problem import Problem
from app.services.learner_progress_service import (
    LearnerProgressService,
    LessonPositionRequest,
    ProblemStatusRequest,
)
from app.services.mcq_service import McqAccessDeniedException, McqService


async def _add_user(db: AsyncSession) -> AppUser:
    user = AppUser(
        email=f"{uuid4().hex}@example.com",
        password_hash="h",
        password_salt="s",
        role="User",
        status="Approved",
        created_at=datetime.now(timezone.utc),
        totp_enabled=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def _add_course(db: AsyncSession) -> tuple[Course, Lesson, Lesson, Problem]:
    now = datetime.now(timezone.utc)
    course = Course(
        slug="python-engineering",
        title="Python",
        description="d",
        order_index=2,
        path_type="Course",
        is_published=True,
        created_at=now,
        updated_at=now,
    )
    db.add(course)
    await db.flush()
    module = CourseModule(
        course_id=course.id,
        slug="m1",
        title="Module 1",
        description="d",
        badge="Module 1",
        order_index=1,
        created_at=now,
        updated_at=now,
    )
    db.add(module)
    await db.flush()
    first = Lesson(
        module_id=module.id,
        slug="py-01",
        title="One",
        description="",
        lecture_number=1,
        class_date="2026-01-01",
        content_body="",
        horstmann_ref="",
        estimated_minutes=45,
        is_completed=False,
        order_index=1,
        created_at=now,
        updated_at=now,
        difficulty="Intermediate",
        content_status="Published",
    )
    second = Lesson(
        module_id=module.id,
        slug="py-02",
        title="Two",
        description="",
        lecture_number=2,
        class_date="2026-01-02",
        content_body="",
        horstmann_ref="",
        estimated_minutes=45,
        is_completed=False,
        order_index=2,
        created_at=now,
        updated_at=now,
        difficulty="Intermediate",
        content_status="Published",
    )
    db.add_all([first, second])
    await db.flush()
    problem = Problem(
        lesson_id=first.id,
        slug="p1",
        title="Problem",
        difficulty="Warm-up",
        package_name="",
        test_class_name="",
        problem_statement="",
        requirements_body="",
        worked_example="",
        hints="",
        language="python",
        run_command="",
        reference_solution="",
        source_type="FROM_MATERIAL",
        is_completed=False,
        order_index=0,
        created_at=now,
        updated_at=now,
    )
    db.add(problem)
    await db.flush()
    for row in (course, first, second, problem):
        await db.refresh(row)
    return course, first, second, problem


@pytest.mark.asyncio
async def test_lesson_progress_is_per_user_and_resume_points_to_last_and_next(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    _, first, second, _ = await _add_course(db)
    alice = await _add_user(db)
    bob = await _add_user(db)
    progress = LearnerProgressService(db)

    await progress.record_visit(alice.id, first.id)
    await progress.update_position(
        alice.id, first.id, LessonPositionRequest(section_id="concepts-covered", scroll_percent=140, seconds_delta=9999)
    )
    completed = await progress.set_lesson_completion(alice.id, first.id, True)

    assert completed is not None
    assert completed.is_completed is True
    assert completed.last_section_id == "concepts-covered"
    assert completed.scroll_percent == 100  # clamped
    assert completed.time_spent_seconds == 300  # heartbeat capped

    assert first.id in await progress.get_completed_lesson_ids(alice.id)
    assert await progress.get_completed_lesson_ids(bob.id) == set()
    assert await progress.get_completed_lesson_ids(None) == set()

    resume = await progress.get_resume(alice.id)
    assert resume.last_lesson is not None
    assert resume.last_lesson.lesson_id == first.id
    assert resume.last_lesson.full_slug == "python-engineering/m1/py-01"
    assert resume.next_lesson is not None
    assert resume.next_lesson.lesson_id == second.id

    events = await progress.get_activity(alice.id, 10, None)
    assert any(e.event_type == "LessonOpened" for e in events)
    assert any(e.event_type == "LessonCompleted" for e in events)
    assert await progress.get_activity(bob.id, 10, None) == []


@pytest.mark.asyncio
async def test_problem_status_tracks_solved_and_revealed_solution(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    _, _, _, problem = await _add_course(db)
    user = await _add_user(db)
    progress = LearnerProgressService(db)

    revealed = await progress.set_problem_status(
        user.id, problem.id, ProblemStatusRequest(status="Attempted", solution_revealed=True)
    )
    assert revealed is not None
    assert revealed.solution_revealed_at is not None
    solved = await progress.set_problem_status(
        user.id, problem.id, ProblemStatusRequest(status="Solved", solution_revealed=None)
    )
    assert solved is not None
    assert solved.solved_at is not None
    assert problem.id in await progress.get_solved_problem_ids(user.id)

    with pytest.raises(ValueError):
        await progress.set_problem_status(
            user.id, problem.id, ProblemStatusRequest(status="Bogus", solution_revealed=None)
        )
    assert (
        await progress.set_problem_status(
            user.id, 99999, ProblemStatusRequest(status="Solved", solution_revealed=None)
        )
        is None
    )


@pytest.mark.asyncio
async def test_mcq_restores_previous_attempt_enforces_ownership_and_supports_retry(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    _, first, _, _ = await _add_course(db)
    alice = await _add_user(db)
    bob = await _add_user(db)

    now = datetime.now(timezone.utc)
    question = McqQuestion(
        lesson_id=first.id,
        legacy_key="python-engineering/py-01/checkpoint/g01",
        question_text="Q?",
        source_type="FROM_MATERIAL",
        explanation="**Answer: (b)**",
        category="Checkpoint",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(question)
    await db.flush()
    db.add_all(
        [
            McqOption(question_id=question.id, option_key="a", option_text="A", is_correct=False),
            McqOption(question_id=question.id, option_key="b", option_text="B", is_correct=True),
        ]
    )
    await db.flush()

    mcq = McqService(db)
    presented = (await mcq.get_practice_questions("python-engineering", "m1", "py-01", alice.id))[0]
    assert presented.category == "Checkpoint"
    assert presented.previous_attempt is None

    # Reloading before answering reuses the same presentation (no row explosion).
    reloaded = (await mcq.get_practice_questions("python-engineering", "m1", "py-01", alice.id))[0]
    assert presented.presentation_id == reloaded.presentation_id

    with pytest.raises(McqAccessDeniedException):
        await mcq.record_attempt(presented.presentation_id, "b", bob.id)
    with pytest.raises(ValueError):
        await mcq.record_attempt(presented.presentation_id, "z", alice.id)

    result = await mcq.record_attempt(presented.presentation_id, "a", alice.id)
    assert result.is_correct is False
    assert result.correct_option_key == "b"

    restored = (await mcq.get_practice_questions("python-engineering", "m1", "py-01", alice.id))[0]
    assert restored.previous_attempt is not None
    assert restored.previous_attempt.selected_option_key == "a"
    assert restored.previous_attempt.correct_option_key == "b"
    assert restored.attempt_count == 1

    retry = await mcq.retry(restored.presentation_id, alice.id)
    assert retry.presentation_id != restored.presentation_id
    assert retry.previous_attempt is None
    await mcq.record_attempt(retry.presentation_id, "b", alice.id)

    progress = LearnerProgressService(db)
    latest = await progress.get_latest_attempts(alice.id)
    assert len(latest) == 1
    assert latest[0].is_correct is True  # latest attempt wins

    summary = await progress.get_summary(alice.id)
    assert summary.total_mcq_answered == 1
    assert summary.total_mcq_correct == 1
    assert any(
        e.event_type == "McqAnswered"
        for e in await progress.get_activity(alice.id, 10, None)
    )
