"""Ported from api/Services/Exercises/ExerciseProgressService.cs.

Persists a signed-in learner's live-exercise work: the latest draft (restored
in the editor), every run's result, and auto-marks the matching coding
assignment solved on an all-green run.
"""

from __future__ import annotations

import logging

from ...stjson import dumps as _json_dumps
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.problem import Problem
from ...models.user_exercise_state import UserExerciseAttempt, UserExerciseDraft
from ...schemas.base import CamelModel, DotNetDateTime
from ...schemas.exercise_dtos import ExerciseExecutionResponse, ExerciseSubmissionRequest
from ..learner_progress_service import LearnerProgressService, ProblemStatusRequest

logger = logging.getLogger(__name__)

MAX_ATTEMPTS_KEPT = 50


class ExerciseDraftFileDto(CamelModel):
    path: str | None = None
    content: str | None = None


class ExerciseDraftRequest(CamelModel):
    files: list[ExerciseDraftFileDto] | None = None


class ExerciseAttemptSummaryDto(CamelModel):
    id: int
    status: str
    tests_total: int
    tests_passed: int
    duration_milliseconds: int
    submitted_at: DotNetDateTime


class ExerciseWorkspaceStateDto(CamelModel):
    exercise_id: str
    draft_files: list[ExerciseDraftFileDto]
    draft_updated_at: DotNetDateTime | None
    last_attempt: ExerciseAttemptSummaryDto | None
    best_attempt: ExerciseAttemptSummaryDto | None
    attempt_count: int
    solved: bool


class ExerciseProgressService:
    def __init__(
        self, session: AsyncSession, progress: LearnerProgressService | None = None
    ) -> None:
        self._session = session
        self._progress = progress or LearnerProgressService(session)

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    async def save_draft(
        self, user_id: int, exercise_id: str, files: list[ExerciseDraftFileDto]
    ) -> None:
        draft = (
            await self._session.execute(
                select(UserExerciseDraft).where(
                    UserExerciseDraft.user_id == user_id,
                    UserExerciseDraft.exercise_id == exercise_id,
                )
            )
        ).scalar_one_or_none()
        if draft is None:
            draft = UserExerciseDraft(user_id=user_id, exercise_id=exercise_id)
            self._session.add(draft)
        draft.files_json = _json_dumps(
            [
                {"path": f.path, "content": f.content if f.content is not None else ""}
                for f in files
            ]
        )
        draft.updated_at = self._utcnow()
        await self._save_ignoring_race()

    async def record_run(
        self,
        user_id: int,
        exercise_id: str,
        request: ExerciseSubmissionRequest,
        result: ExerciseExecutionResponse,
    ) -> None:
        files = [
            ExerciseDraftFileDto(path=f.path, content=f.content)
            for f in (request.files or [])
        ]
        await self.save_draft(user_id, exercise_id, files)

        failing = [
            e.label for e in result.evidence if e.status != "passed"
        ][:10]
        now = self._utcnow()
        self._session.add(
            UserExerciseAttempt(
                user_id=user_id,
                exercise_id=exercise_id,
                status=result.status,
                tests_total=result.summary.total,
                tests_passed=result.summary.passed,
                duration_milliseconds=result.duration_milliseconds,
                files_json=_json_dumps(
                    [
                        {"path": f.path, "content": f.content}
                        for f in files
                    ]
                ),
                summary_json=_json_dumps(
                    {
                        "failing": failing,
                        "failed": result.summary.failed,
                        "errors": result.summary.errors,
                    }
                ),
                submitted_at=now,
            )
        )

        problem = (
            await self._session.execute(
                select(Problem).where(Problem.slug == exercise_id)
            )
        ).scalar_one_or_none()
        self._progress.add_activity(
            user_id,
            "ExerciseRun",
            lesson_id=problem.lesson_id if problem is not None else None,
            problem_id=problem.id if problem is not None else None,
            metadata={
                "exerciseId": exercise_id,
                "Status": result.status,
                "Total": result.summary.total,
                "Passed": result.summary.passed,
            },
        )
        await self._session.flush()

        if problem is not None:
            solved = await self._progress.get_solved_problem_ids(user_id)
            if result.passed:
                await self._progress.set_problem_status(
                    user_id,
                    problem.id,
                    ProblemStatusRequest(status="Solved", solution_revealed=None),
                )
            elif problem.id not in solved:
                await self._progress.set_problem_status(
                    user_id,
                    problem.id,
                    ProblemStatusRequest(status="Attempted", solution_revealed=None),
                )
        await self._trim_history(user_id, exercise_id)

    async def get_state(self, user_id: int, exercise_id: str) -> ExerciseWorkspaceStateDto:
        draft = (
            await self._session.execute(
                select(UserExerciseDraft).where(
                    UserExerciseDraft.user_id == user_id,
                    UserExerciseDraft.exercise_id == exercise_id,
                )
            )
        ).scalar_one_or_none()
        attempts = (
            await self._session.execute(
                select(UserExerciseAttempt)
                .where(
                    UserExerciseAttempt.user_id == user_id,
                    UserExerciseAttempt.exercise_id == exercise_id,
                )
                .order_by(desc(UserExerciseAttempt.submitted_at))
            )
        ).scalars().all()
        summaries = [
            ExerciseAttemptSummaryDto(
                id=a.id,
                status=a.status,
                tests_total=a.tests_total,
                tests_passed=a.tests_passed,
                duration_milliseconds=a.duration_milliseconds,
                submitted_at=a.submitted_at,
            )
            for a in attempts
        ]
        best = None
        if summaries:
            best = sorted(
                summaries,
                key=lambda a: (
                    0 if a.status == "success" else 1,
                    -(a.tests_passed / a.tests_total) if a.tests_total else 0,
                    a.submitted_at,
                ),
            )[0]
        draft_files: list[ExerciseDraftFileDto] = []
        if draft is not None:
            try:
                raw = json.loads(draft.files_json)
            except (json.JSONDecodeError, ValueError, TypeError):
                raw = []
            if isinstance(raw, list):
                for entry in raw:
                    if isinstance(entry, dict):
                        lowered = {str(k).lower(): v for k, v in entry.items()}
                        draft_files.append(
                            ExerciseDraftFileDto(
                                path=lowered.get("path"),
                                content=lowered.get("content"),
                            )
                        )
        return ExerciseWorkspaceStateDto(
            exercise_id=exercise_id,
            draft_files=draft_files,
            draft_updated_at=draft.updated_at if draft is not None else None,
            last_attempt=summaries[0] if summaries else None,
            best_attempt=best,
            attempt_count=len(summaries),
            solved=any(a.status == "success" for a in summaries),
        )

    async def _trim_history(self, user_id: int, exercise_id: str) -> None:
        stale = (
            await self._session.execute(
                select(UserExerciseAttempt)
                .where(
                    UserExerciseAttempt.user_id == user_id,
                    UserExerciseAttempt.exercise_id == exercise_id,
                )
                .order_by(desc(UserExerciseAttempt.submitted_at))
                .offset(MAX_ATTEMPTS_KEPT)
            )
        ).scalars().all()
        if not stale:
            return
        for row in stale:
            await self._session.delete(row)
        await self._session.flush()

    async def _save_ignoring_race(self) -> None:
        try:
            await self._session.flush()
        except IntegrityError as exc:
            # Two tabs created the same (user, exercise) draft at once; the other write won.
            logger.info("Concurrent exercise draft insert; keeping the existing row: %s", exc)
            await self._session.rollback()
