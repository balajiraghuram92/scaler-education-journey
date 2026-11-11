"""Ported from api/Endpoints/ExerciseEndpoints.cs."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..errors import endpoint_problem
from ..schemas.exercise_dtos import ExerciseSubmissionRequest
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
    require_user,
)
from ..services.exercises.exercise_execution_exceptions import (
    ExerciseConcurrencyLimitException,
    ExerciseInfrastructureException,
    ExerciseNotFoundException,
    ExerciseRunnerUnavailableException,
    ExerciseSolutionNotFoundException,
    ExerciseSubmissionValidationException,
)
from ..services.exercises.exercise_metadata_service import ExerciseMetadataService
from ..services.exercises.exercise_progress_service import (
    ExerciseDraftRequest,
    ExerciseProgressService,
)
from ..services.exercises.exercise_repository import get_exercise_repository
from ..services.exercises.exercise_service import ExerciseService
from ..services.exercises.exercise_solution_service import ExerciseSolutionService
from ..settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.get("/{exercise_id}")
def get_metadata(exercise_id: str, request: Request):
    try:
        service = ExerciseMetadataService(get_exercise_repository())
        return service.get_by_id(exercise_id)
    except ExerciseNotFoundException:
        return endpoint_problem(
            request, 404, "Exercise not found.", "The requested exercise does not exist."
        )
    except ExerciseInfrastructureException:
        return endpoint_problem(
            request,
            503,
            "Exercise metadata unavailable.",
            "The exercise metadata is temporarily unavailable.",
        )


@router.get("/{exercise_id}/solution")
def get_solution(exercise_id: str, request: Request):
    try:
        service = ExerciseSolutionService(get_exercise_repository())
        return service.get_by_id(exercise_id)
    except ExerciseNotFoundException:
        return endpoint_problem(
            request, 404, "Exercise not found.", "The requested exercise does not exist."
        )
    except ExerciseSolutionNotFoundException:
        return endpoint_problem(
            request,
            404,
            "Reference solution unavailable.",
            "This exercise does not include a reference solution.",
        )
    except ExerciseInfrastructureException:
        return endpoint_problem(
            request,
            503,
            "Reference solution unavailable.",
            "The reference solution is temporarily unavailable.",
        )


@router.post("/{exercise_id}/run")
async def execute_run(
    exercise_id: str,
    request: Request,
    body: ExerciseSubmissionRequest | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    return await _execute(exercise_id, body, request, current, session)


@router.post("/{exercise_id}/check")
async def execute_check(
    exercise_id: str,
    request: Request,
    body: ExerciseSubmissionRequest | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    return await _execute(exercise_id, body, request, current, session)


async def _execute(
    exercise_id: str,
    body: ExerciseSubmissionRequest | None,
    request: Request,
    current: CurrentUser,
    session: AsyncSession,
):
    try:
        result = await ExerciseService(get_exercise_repository()).execute_async(
            exercise_id, body
        )
        if current.user_id is not None:
            try:
                await ExerciseProgressService(session).record_run(
                    current.user_id, exercise_id, body or ExerciseSubmissionRequest(), result
                )
                await session.commit()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                # Recording history must never hide the learner's test result.
                logger.warning(
                    "Failed to record exercise run for %s: %s", exercise_id, exc
                )
                await session.rollback()
        return result
    except ExerciseNotFoundException:
        return endpoint_problem(
            request, 404, "Exercise not found.", "The requested exercise does not exist."
        )
    except ExerciseSubmissionValidationException as exc:
        return JSONResponse(
            status_code=400,
            media_type="application/problem+json",
            content={
                "type": "https://tools.ietf.org/html/rfc9110#section-15.5.1",
                "title": "One or more validation errors occurred.",
                "status": 400,
                "errors": {
                    f"files[{index}]": [error]
                    for index, error in enumerate(exc.errors)
                },
                "traceId": getattr(getattr(request, "state", None), "correlation_id", ""),
            },
        )
    except ExerciseConcurrencyLimitException:
        return endpoint_problem(
            request,
            429,
            "Execution limit reached.",
            "Try the exercise again shortly.",
        )
    except ExerciseRunnerUnavailableException:
        return endpoint_problem(
            request,
            503,
            "Exercise runner unavailable.",
            "The exercise execution service is temporarily unavailable.",
        )
    except ExerciseInfrastructureException:
        return endpoint_problem(
            request,
            503,
            "Exercise execution unavailable.",
            "The exercise could not be executed by the platform.",
        )


@router.get("/{exercise_id}/workspace", dependencies=[Depends(require_user)])
async def get_workspace_state(
    exercise_id: str,
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    if get_exercise_repository().get_by_id(exercise_id) is None:
        return endpoint_problem(
            request, 404, "Exercise not found.", "The requested exercise does not exist."
        )
    assert current.user_id is not None
    return await ExerciseProgressService(session).get_state(current.user_id, exercise_id)


@router.put("/{exercise_id}/draft", dependencies=[Depends(require_user)])
async def save_draft(
    exercise_id: str,
    request: Request,
    body: ExerciseDraftRequest | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    definition = get_exercise_repository().get_by_id(exercise_id)
    if definition is None:
        return endpoint_problem(
            request, 404, "Exercise not found.", "The requested exercise does not exist."
        )
    assert current.user_id is not None
    files = body.files if body is not None and body.files is not None else []
    total_bytes = sum(len((f.content or "").encode("utf-8")) for f in files)
    if (
        len(files) == 0
        or any(f.path is None or f.path not in definition.editable_files for f in files)
        or total_bytes > get_settings().exercise_execution.max_submission_bytes
    ):
        return endpoint_problem(
            request,
            400,
            "Invalid draft.",
            "Drafts may only contain the exercise's editable files within the size limit.",
        )
    await ExerciseProgressService(session).save_draft(current.user_id, exercise_id, files)
    await session.commit()
    return Response(status_code=204)
