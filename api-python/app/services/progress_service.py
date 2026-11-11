"""Ported from api/Services/ProgressService.cs."""

from __future__ import annotations

import logging

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.learning_activity import LearningActivity
from ..models.lesson import Lesson
from ..models.problem import Problem
from ..models.study_task import StudyTask
from ..models.study_task_content_link import StudyTaskContentLink
from ..schemas.base import CamelModel
from ..stjson import dumps as _json_dumps

logger = logging.getLogger(__name__)


class ProgressResult(CamelModel):
    success: bool = False
    entity_type: str = ""
    entity_id: int = 0
    is_completed: bool = False
    synchronized_task_ids: list[int] = []
    synchronized_lesson_id: int | None = None
    synchronized_problem_id: int | None = None
    correlation_id: UUID = UUID(int=0)
    error: str | None = None


class ProgressService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def set_lesson_completion(
        self, lesson_id: int, is_completed: bool, correlation_id: UUID | None = None
    ) -> ProgressResult:
        corr_id = correlation_id or uuid4()
        try:
            lesson = (
                await self._session.execute(
                    select(Lesson)
                    .options(selectinload(Lesson.legacy_task_links))
                    .where(Lesson.id == lesson_id)
                )
            ).scalar_one_or_none()
            if lesson is None:
                return ProgressResult(
                    success=False,
                    error=f"Lesson {lesson_id} not found.",
                    correlation_id=corr_id,
                )
            lesson.is_completed = is_completed
            lesson.updated_at = self._utcnow()

            affected_task_ids: list[int] = []
            # ONLY synchronize legacy tasks if mapping is explicitly Verified
            verified_links = [
                link
                for link in lesson.legacy_task_links
                if link.mapping_status == "Verified"
            ]
            for link in verified_links:
                task = await self._session.get(StudyTask, link.task_id)
                if task is not None:
                    task.is_completed = is_completed
                    task.updated_at = self._utcnow()
                    affected_task_ids.append(task.id)

            # Record LearningActivity with correlation idempotency
            event_type = "LessonCompleted" if is_completed else "LessonReopened"
            existing = (
                await self._session.execute(
                    select(LearningActivity).where(
                        LearningActivity.correlation_id == corr_id,
                        LearningActivity.event_type == event_type,
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                self._session.add(
                    LearningActivity(
                        event_type=event_type,
                        lesson_id=lesson.id,
                        correlation_id=corr_id,
                        occurred_at=self._utcnow(),
                        metadata_json=_json_dumps({"SynchronizedTasks": affected_task_ids}),
                    )
                )
            await self._session.flush()
            return ProgressResult(
                success=True,
                entity_type="Lesson",
                entity_id=lesson.id,
                is_completed=is_completed,
                synchronized_task_ids=affected_task_ids,
                correlation_id=corr_id,
            )
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                "Failed to set Lesson %s completion atomically (Correlation: %s): %s",
                lesson_id,
                corr_id,
                exc,
            )
            return ProgressResult(
                success=False,
                entity_type="Lesson",
                entity_id=lesson_id,
                correlation_id=corr_id,
                error="An error occurred while updating lesson progress. Please refer to traceId for support.",
            )

    async def set_problem_completion(
        self, problem_id: int, is_completed: bool, correlation_id: UUID | None = None
    ) -> ProgressResult:
        corr_id = correlation_id or uuid4()
        try:
            problem = (
                await self._session.execute(
                    select(Problem)
                    .options(selectinload(Problem.legacy_task_links))
                    .where(Problem.id == problem_id)
                )
            ).scalar_one_or_none()
            if problem is None:
                return ProgressResult(
                    success=False,
                    error=f"Problem {problem_id} not found.",
                    correlation_id=corr_id,
                )
            problem.is_completed = is_completed
            problem.updated_at = self._utcnow()

            affected_task_ids: list[int] = []
            # ONLY synchronize legacy tasks if mapping is explicitly Verified
            verified_links = [
                link
                for link in problem.legacy_task_links
                if link.mapping_status == "Verified"
            ]
            for link in verified_links:
                task = await self._session.get(StudyTask, link.task_id)
                if task is not None:
                    task.is_completed = is_completed
                    task.updated_at = self._utcnow()
                    affected_task_ids.append(task.id)

            event_type = "ProblemCompleted" if is_completed else "ProblemReopened"
            existing = (
                await self._session.execute(
                    select(LearningActivity).where(
                        LearningActivity.correlation_id == corr_id,
                        LearningActivity.event_type == event_type,
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                self._session.add(
                    LearningActivity(
                        event_type=event_type,
                        problem_id=problem.id,
                        correlation_id=corr_id,
                        occurred_at=self._utcnow(),
                        metadata_json=_json_dumps({"SynchronizedTasks": affected_task_ids}),
                    )
                )
            await self._session.flush()
            return ProgressResult(
                success=True,
                entity_type="Problem",
                entity_id=problem.id,
                is_completed=is_completed,
                synchronized_task_ids=affected_task_ids,
                correlation_id=corr_id,
            )
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                "Failed to set Problem %s completion atomically (Correlation: %s): %s",
                problem_id,
                corr_id,
                exc,
            )
            return ProgressResult(
                success=False,
                entity_type="Problem",
                entity_id=problem_id,
                correlation_id=corr_id,
                error="An error occurred while updating problem progress. Please refer to traceId for support.",
            )

    async def set_task_completion(
        self, task_id: int, is_completed: bool, correlation_id: UUID | None = None
    ) -> ProgressResult:
        corr_id = correlation_id or uuid4()
        try:
            task = (
                await self._session.execute(
                    select(StudyTask)
                    .options(selectinload(StudyTask.content_link))
                    .where(StudyTask.id == task_id)
                )
            ).scalar_one_or_none()
            if task is None:
                return ProgressResult(
                    success=False,
                    error=f"Task {task_id} not found.",
                    correlation_id=corr_id,
                )
            task.is_completed = is_completed
            task.updated_at = self._utcnow()

            mapped_lesson_id: int | None = None
            mapped_problem_id: int | None = None

            # ONLY synchronize canonical entities if mapping is explicitly Verified
            link: StudyTaskContentLink | None = task.content_link
            if link is not None and link.mapping_status == "Verified":
                if link.lesson_id is not None:
                    lesson = await self._session.get(Lesson, link.lesson_id)
                    if lesson is not None:
                        lesson.is_completed = is_completed
                        lesson.updated_at = self._utcnow()
                        mapped_lesson_id = lesson.id
                if link.problem_id is not None:
                    problem = await self._session.get(Problem, link.problem_id)
                    if problem is not None:
                        problem.is_completed = is_completed
                        problem.updated_at = self._utcnow()
                        mapped_problem_id = problem.id

            event_type = "TaskCompleted" if is_completed else "TaskReopened"
            existing = (
                await self._session.execute(
                    select(LearningActivity).where(
                        LearningActivity.correlation_id == corr_id,
                        LearningActivity.event_type == event_type,
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                self._session.add(
                    LearningActivity(
                        event_type=event_type,
                        task_id=task.id,
                        lesson_id=mapped_lesson_id,
                        problem_id=mapped_problem_id,
                        correlation_id=corr_id,
                        occurred_at=self._utcnow(),
                        metadata_json="{}",
                    )
                )
            await self._session.flush()
            return ProgressResult(
                success=True,
                entity_type="StudyTask",
                entity_id=task.id,
                is_completed=is_completed,
                synchronized_lesson_id=mapped_lesson_id,
                synchronized_problem_id=mapped_problem_id,
                correlation_id=corr_id,
            )
        except Exception as exc:
            await self._session.rollback()
            logger.error(
                "Failed to set Task %s completion atomically (Correlation: %s): %s",
                task_id,
                corr_id,
                exc,
            )
            return ProgressResult(
                success=False,
                entity_type="StudyTask",
                entity_id=task_id,
                correlation_id=corr_id,
                error="An error occurred while updating task progress. Please refer to traceId for support.",
            )
