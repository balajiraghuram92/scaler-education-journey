"""Ported from api/Program.cs inline routes for /api/courses (lines 797-956)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..models.course import Course
from ..models.course_module import CourseModule
from ..models.lesson import Lesson
from ..schemas.dtos import CourseSummaryDto, LessonSummaryDto, ModuleSummaryDto
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
)
from ..services.learner_progress_service import LearnerProgressService

router = APIRouter(tags=["courses"])


def _course_to_dto(
    course: Course, completed_ids: set[int], solved_ids: set[int]
) -> CourseSummaryDto:
    all_lessons = [lesson for module in course.modules for lesson in module.lessons]
    all_problems = [p for lesson in all_lessons for p in lesson.problems]
    total_lessons = len(all_lessons)
    completed_lessons = sum(1 for lesson in all_lessons if lesson.id in completed_ids)
    total_problems = len(all_problems)
    completed_problems = sum(1 for p in all_problems if p.id in solved_ids)
    progress_percent = (
        int(round(completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
    )
    module_dtos = []
    for module in sorted(course.modules, key=lambda m: m.order_index):
        m_lessons = sorted(module.lessons, key=lambda lesson: lesson.order_index)
        m_total = len(m_lessons)
        m_completed = sum(1 for lesson in m_lessons if lesson.id in completed_ids)
        module_dtos.append(
            ModuleSummaryDto(
                id=module.id,
                course_id=module.course_id,
                slug=module.slug,
                title=module.title,
                description=module.description,
                badge=module.badge,
                order_index=module.order_index,
                total_lessons=m_total,
                completed_lessons=m_completed,
                progress_percent=int(round(m_completed / m_total * 100)) if m_total > 0 else 0,
                lessons=[
                    LessonSummaryDto(
                        id=lesson.id,
                        module_id=lesson.module_id,
                        slug=lesson.slug,
                        title=lesson.title,
                        description=lesson.description,
                        lecture_number=lesson.lecture_number,
                        class_date=lesson.class_date,
                        horstmann_ref=lesson.horstmann_ref,
                        estimated_minutes=lesson.estimated_minutes,
                        is_completed=lesson.id in completed_ids,
                        order_index=lesson.order_index,
                        problem_count=len(lesson.problems),
                    )
                    for lesson in m_lessons
                ],
            )
        )
    return CourseSummaryDto(
        id=course.id,
        slug=course.slug,
        title=course.title,
        description=course.description,
        order_index=course.order_index,
        vertical_id=course.vertical_id,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        total_problems=total_problems,
        completed_problems=completed_problems,
        progress_percent=progress_percent,
        modules=module_dtos,
    )


@router.get("/api/courses")  # Program.cs line 797
async def get_courses(
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    courses = (
        await session.execute(
            select(Course)
            .options(
                selectinload(Course.modules)
                .selectinload(CourseModule.lessons)
                .selectinload(Lesson.problems)
            )
            .order_by(Course.order_index)
        )
    ).scalars().all()
    progress = LearnerProgressService(session)
    completed_ids = await progress.get_completed_lesson_ids(current.user_id)
    solved_ids = await progress.get_solved_problem_ids(current.user_id)
    return [_course_to_dto(c, completed_ids, solved_ids) for c in courses]


@router.get("/api/courses/{slug_or_id}")  # Program.cs line 874
async def get_course_by_slug_or_id(
    slug_or_id: str,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    progress = LearnerProgressService(session)
    completed_ids = await progress.get_completed_lesson_ids(current.user_id)
    solved_ids = await progress.get_solved_problem_ids(current.user_id)
    stmt = (
        select(Course)
        .options(
            selectinload(Course.modules)
            .selectinload(CourseModule.lessons)
            .selectinload(Lesson.problems)
        )
    )
    try:
        course_id = int(slug_or_id)
    except ValueError:
        course_id = None
    if course_id is not None:
        stmt = stmt.where(Course.id == course_id)
    else:
        stmt = stmt.where(Course.slug == slug_or_id)
    course = (await session.execute(stmt)).scalar_one_or_none()
    if course is None:
        return JSONResponse(status_code=404, content={"message": "Course not found."})
    return _course_to_dto(course, completed_ids, solved_ids)
