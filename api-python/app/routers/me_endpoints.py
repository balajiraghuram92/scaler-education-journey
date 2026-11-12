"""Ported from api/Endpoints/MeEndpoints.cs.

The signed-in learner's own state: progress, resume point, assignment status,
MCQ performance and activity history. Every route requires authentication and
is scoped to the caller — there is no way to read another learner's state here.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
    require_user,
)
from ..services.learner_progress_service import (
    LearnerProgressService,
    LessonCompletionRequest,
    LessonPositionRequest,
    ProblemStatusRequest,
)

router = APIRouter(prefix="/api/me", tags=["me"])


def _service(session: AsyncSession) -> LearnerProgressService:
    return LearnerProgressService(session)


@router.get("/summary", dependencies=[Depends(require_user)])
async def summary(
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    return await _service(session).get_summary(current.user_id)


@router.get("/resume", dependencies=[Depends(require_user)])
async def resume(
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    return await _service(session).get_resume(current.user_id)


@router.get("/lessons/progress", dependencies=[Depends(require_user)])
async def lesson_progress_list(
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    progress_map = await _service(session).get_lesson_progress_map(current.user_id, None)
    return list(progress_map.values())


@router.post("/lessons/{lesson_id:int}/visit", dependencies=[Depends(require_user)])
async def record_lesson_visit(
    lesson_id: int,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    result = await _service(session).record_visit(current.user_id, lesson_id)
    await session.commit()
    if result is None:
        return _lesson_not_found(lesson_id)
    return result


@router.put("/lessons/{lesson_id:int}/position", dependencies=[Depends(require_user)])
async def update_lesson_position(
    lesson_id: int,
    body: LessonPositionRequest,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    result = await _service(session).update_position(current.user_id, lesson_id, body)
    await session.commit()
    if result is None:
        return _lesson_not_found(lesson_id)
    return result


@router.put("/lessons/{lesson_id:int}/completion", dependencies=[Depends(require_user)])
async def set_lesson_completion(
    lesson_id: int,
    body: LessonCompletionRequest,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    result = await _service(session).set_lesson_completion(
        current.user_id, lesson_id, body.is_completed
    )
    await session.commit()
    if result is None:
        return _lesson_not_found(lesson_id)
    return result


@router.put("/problems/{problem_id:int}/status", dependencies=[Depends(require_user)])
async def set_problem_status(
    problem_id: int,
    body: ProblemStatusRequest,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    try:
        result = await _service(session).set_problem_status(
            current.user_id, problem_id, body
        )
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    await session.commit()
    if result is None:
        return JSONResponse(
            status_code=404, content={"error": f"Problem {problem_id} not found."}
        )
    return result


@router.get("/mcq-performance", dependencies=[Depends(require_user)])
async def mcq_performance(
    course: str | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    return await _service(session).get_mcq_performance(current.user_id, course)


@router.get("/activity", dependencies=[Depends(require_user)])
async def activity(
    limit: int | None = None,
    before: datetime | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    return await _service(session).get_activity(
        current.user_id, limit if limit is not None else 50, before
    )


def _lesson_not_found(lesson_id: int) -> JSONResponse:
    return JSONResponse(
        status_code=404, content={"error": f"Lesson {lesson_id} not found."}
    )
