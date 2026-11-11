"""Ported from api/Program.cs inline routes for /api/lessons (lines 962-1083)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..models.course_module import CourseModule
from ..models.lesson import Lesson
from ..schemas.base import format_dotnet_datetime
from ..schemas.dtos import (
    CreateLessonRequest,
    LessonDetailDto,
    LessonResourceDto,
    ProblemSummaryDto,
    ToggleProgressResponse,
    UpdateLessonRequest,
)
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
    require_user,
)
from ..services.learner_progress_service import LearnerProgressService

router = APIRouter(tags=["lessons"])


def lesson_to_dict(lesson: Lesson) -> dict:
    """System.Text.Json shape of a Lesson entity (navs are [JsonIgnore])."""
    return {
        "id": lesson.id,
        "moduleId": lesson.module_id,
        "slug": lesson.slug,
        "title": lesson.title,
        "description": lesson.description,
        "lectureNumber": lesson.lecture_number,
        "classDate": lesson.class_date,
        "contentBody": lesson.content_body,
        "horstmannRef": lesson.horstmann_ref,
        "estimatedMinutes": lesson.estimated_minutes,
        "isCompleted": lesson.is_completed,
        "orderIndex": lesson.order_index,
        "createdAt": format_dotnet_datetime(lesson.created_at),
        "updatedAt": format_dotnet_datetime(lesson.updated_at),
        "difficulty": lesson.difficulty,
        "contentStatus": lesson.content_status,
        "problems": [],
        "resources": [],
        "codeComparisons": [],
        "diagrams": [],
        "notes": [],
        "conceptLinks": [],
        "outgoingRelations": [],
        "incomingRelations": [],
        "legacyTaskLinks": [],
        "readingMapItems": [],
    }


@router.get("/api/lessons/{lesson_id}")  # Program.cs line 962
async def get_lesson_by_id(
    lesson_id: int,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    lesson = (
        await session.execute(
            select(Lesson)
            .options(
                selectinload(Lesson.module).selectinload(CourseModule.course),
                selectinload(Lesson.problems),
                selectinload(Lesson.resources),
            )
            .where(Lesson.id == lesson_id)
        )
    ).scalar_one_or_none()
    if lesson is None:
        return JSONResponse(status_code=404, content={"message": "Lesson not found."})
    progress = LearnerProgressService(session)
    completed_ids = await progress.get_completed_lesson_ids(current.user_id)
    solved_ids = await progress.get_solved_problem_ids(current.user_id)
    module = lesson.module
    course = module.course if module is not None else None
    return LessonDetailDto(
        id=lesson.id,
        module_id=lesson.module_id,
        module_title=module.title if module is not None else "",
        course_id=module.course_id if module is not None else 0,
        course_title=course.title if course is not None else "",
        slug=lesson.slug,
        title=lesson.title,
        description=lesson.description,
        lecture_number=lesson.lecture_number,
        class_date=lesson.class_date,
        content_body=lesson.content_body,
        horstmann_ref=lesson.horstmann_ref,
        estimated_minutes=lesson.estimated_minutes,
        is_completed=lesson.id in completed_ids,
        order_index=lesson.order_index,
        problems=[
            ProblemSummaryDto(
                id=p.id,
                lesson_id=p.lesson_id,
                slug=p.slug,
                title=p.title,
                difficulty=p.difficulty,
                package_name=p.package_name,
                test_class_name=p.test_class_name,
                problem_statement=p.problem_statement,
                requirements_body=p.requirements_body,
                worked_example=p.worked_example,
                hints=p.hints,
                is_completed=p.id in solved_ids,
                order_index=p.order_index,
            )
            for p in sorted(lesson.problems, key=lambda x: x.order_index)
        ],
        resources=[
            LessonResourceDto(
                id=r.id,
                lesson_id=r.lesson_id,
                resource_type=r.resource_type,
                title=r.title,
                content_body=r.content_body,
                order_index=r.order_index,
            )
            for r in sorted(lesson.resources, key=lambda x: x.order_index)
        ],
    )


@router.post("/api/lessons")  # Program.cs line 1021
async def create_lesson(
    body: CreateLessonRequest, session: AsyncSession = Depends(get_session)
):
    if not body.title or not body.title.strip() or not body.slug or not body.slug.strip():
        return JSONResponse(
            status_code=400, content={"message": "Title and Slug are required."}
        )
    module_exists = (
        await session.execute(
            select(CourseModule.id).where(CourseModule.id == body.module_id)
        )
    ).first()
    if module_exists is None:
        return JSONResponse(status_code=400, content={"message": "Invalid ModuleId."})
    now = datetime.now(timezone.utc)
    lesson = Lesson(
        module_id=body.module_id,
        slug=body.slug.strip().lower(),
        title=body.title.strip(),
        description=body.description if body.description is not None else "",
        lecture_number=body.lecture_number,
        class_date=body.class_date
        if body.class_date is not None
        else now.strftime("%Y-%m-%d"),
        content_body=body.content_body if body.content_body is not None else "",
        horstmann_ref=body.horstmann_ref if body.horstmann_ref is not None else "",
        estimated_minutes=body.estimated_minutes if body.estimated_minutes is not None else 45,
        order_index=body.order_index if body.order_index is not None else 0,
        is_completed=False,
        difficulty="Intermediate",
        created_at=now,
        updated_at=now,
    )
    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)
    return JSONResponse(
        status_code=201,
        headers={"Location": f"/api/lessons/{lesson.id}"},
        content=lesson_to_dict(lesson),
    )


@router.put("/api/lessons/{lesson_id}")  # Program.cs line 1055
async def update_lesson(
    lesson_id: int,
    body: UpdateLessonRequest,
    session: AsyncSession = Depends(get_session),
):
    lesson = await session.get(Lesson, lesson_id)
    if lesson is None:
        return Response(status_code=404)
    if body.title and body.title.strip():
        lesson.title = body.title
    if body.description is not None:
        lesson.description = body.description
    if body.content_body is not None:
        lesson.content_body = body.content_body
    if body.horstmann_ref is not None:
        lesson.horstmann_ref = body.horstmann_ref
    if body.estimated_minutes is not None:
        lesson.estimated_minutes = body.estimated_minutes
    if body.is_completed is not None:
        lesson.is_completed = body.is_completed
    lesson.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(lesson)
    return lesson_to_dict(lesson)


@router.patch(
    "/api/lessons/{lesson_id}/progress", dependencies=[Depends(require_user)]
)  # Program.cs line 1073
async def toggle_lesson_progress(
    lesson_id: int,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    progress = LearnerProgressService(session)
    completed = await progress.get_completed_lesson_ids(current.user_id)
    result = await progress.set_lesson_completion(
        current.user_id, lesson_id, lesson_id not in completed
    )
    await session.commit()
    if result is None:
        return Response(status_code=404)
    return ToggleProgressResponse(
        id=lesson_id,
        is_completed=result.is_completed,
        message=f"Lesson status toggled to {'Completed' if result.is_completed else 'Pending'}",
    )
