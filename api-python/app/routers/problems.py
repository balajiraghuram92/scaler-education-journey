"""Ported from api/Program.cs inline routes for /api/problems (lines 1089-1160)."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models.lesson import Lesson
from ..models.problem import Problem
from ..schemas.base import format_dotnet_datetime
from ..schemas.dtos import (
    CreateProblemRequest,
    ProblemSummaryDto,
    ToggleProgressResponse,
)
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
    require_user,
)
from ..services.learner_progress_service import (
    LearnerProgressService,
    ProblemStatusRequest,
)

router = APIRouter(tags=["problems"])


def problem_to_dict(problem: Problem) -> dict:
    """System.Text.Json shape of a Problem entity (navs are [JsonIgnore])."""
    return {
        "id": problem.id,
        "lessonId": problem.lesson_id,
        "slug": problem.slug,
        "title": problem.title,
        "difficulty": problem.difficulty,
        "packageName": problem.package_name,
        "testClassName": problem.test_class_name,
        "problemStatement": problem.problem_statement,
        "requirementsBody": problem.requirements_body,
        "workedExample": problem.worked_example,
        "hints": problem.hints,
        "language": problem.language,
        "runCommand": problem.run_command,
        "referenceSolution": problem.reference_solution,
        "sourceType": problem.source_type,
        "isCompleted": problem.is_completed,
        "orderIndex": problem.order_index,
        "createdAt": format_dotnet_datetime(problem.created_at),
        "updatedAt": format_dotnet_datetime(problem.updated_at),
        "legacyTaskLinks": [],
    }


@router.get("/api/problems/{problem_id:int}")  # Program.cs line 1089
async def get_problem_by_id(
    problem_id: int,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    problem = (
        await session.execute(select(Problem).where(Problem.id == problem_id))
    ).scalar_one_or_none()
    if problem is None:
        return Response(status_code=404)
    solved_ids = await LearnerProgressService(session).get_solved_problem_ids(
        current.user_id
    )
    return ProblemSummaryDto(
        id=problem.id,
        lesson_id=problem.lesson_id,
        slug=problem.slug,
        title=problem.title,
        difficulty=problem.difficulty,
        package_name=problem.package_name,
        test_class_name=problem.test_class_name,
        problem_statement=problem.problem_statement,
        requirements_body=problem.requirements_body,
        worked_example=problem.worked_example,
        hints=problem.hints,
        is_completed=problem.id in solved_ids,
        order_index=problem.order_index,
    )


@router.post("/api/problems")  # Program.cs line 1114
async def create_problem(
    body: CreateProblemRequest, session: AsyncSession = Depends(get_session)
):
    if not body.title or not body.title.strip() or not body.slug or not body.slug.strip():
        return JSONResponse(
            status_code=400, content={"message": "Title and Slug are required."}
        )
    lesson_exists = (
        await session.execute(select(Lesson.id).where(Lesson.id == body.lesson_id))
    ).first()
    if lesson_exists is None:
        return JSONResponse(status_code=400, content={"message": "Invalid LessonId."})
    now = datetime.now(UTC)
    problem = Problem(
        lesson_id=body.lesson_id,
        slug=body.slug.strip().lower(),
        title=body.title.strip(),
        difficulty=body.difficulty if body.difficulty is not None else "Warm-up",
        package_name=body.package_name if body.package_name is not None else "",
        test_class_name=body.test_class_name if body.test_class_name is not None else "",
        problem_statement=body.problem_statement if body.problem_statement is not None else "",
        requirements_body=body.requirements_body if body.requirements_body is not None else "",
        worked_example=body.worked_example if body.worked_example is not None else "",
        hints=body.hints if body.hints is not None else "",
        order_index=body.order_index if body.order_index is not None else 0,
        language="java",
        run_command="",
        reference_solution="",
        source_type="FROM_MATERIAL",
        is_completed=False,
        created_at=now,
        updated_at=now,
    )
    session.add(problem)
    await session.commit()
    await session.refresh(problem)
    return JSONResponse(
        status_code=201,
        headers={"Location": f"/api/problems/{problem.id}"},
        content=problem_to_dict(problem),
    )


@router.patch(
    "/api/problems/{problem_id:int}/progress", dependencies=[Depends(require_user)]
)  # Program.cs line 1149
async def toggle_problem_progress(
    problem_id: int,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    progress = LearnerProgressService(session)
    solved = await progress.get_solved_problem_ids(current.user_id)
    result = await progress.set_problem_status(
        current.user_id,
        problem_id,
        ProblemStatusRequest(
            status="Attempted" if problem_id in solved else "Solved",
            solution_revealed=None,
        ),
    )
    await session.commit()
    if result is None:
        return Response(status_code=404)
    is_solved = result.status == "Solved"
    return ToggleProgressResponse(
        id=problem_id,
        is_completed=is_solved,
        message=f"Problem status toggled to {'Completed' if is_solved else 'Pending'}",
    )
