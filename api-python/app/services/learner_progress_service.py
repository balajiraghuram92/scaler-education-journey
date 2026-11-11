"""Ported from api/Services/LearnerProgressService.cs.

Per-learner learning state: lesson reading/completion, assignment status, the
activity log, resume pointers and MCQ performance. All reads are keyed by user
id, so anonymous readers simply see no progress.
"""

from __future__ import annotations

import logging

from ..stjson import dumps as _json_dumps
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.course import Course
from ..models.course_module import CourseModule
from ..models.learning_activity import LearningActivity
from ..models.lesson import Lesson
from ..models.mcq_attempt import McqAttempt
from ..models.mcq_presentation import McqPresentation
from ..models.mcq_question import McqQuestion
from ..models.problem import Problem
from ..models.user_lesson_progress import UserLessonProgress
from ..models.user_problem_progress import UserProblemProgress
from ..schemas.base import CamelModel, DotNetDateTime

logger = logging.getLogger(__name__)

# Re-opening a lesson within this window continues the same visit.
VISIT_WINDOW = timedelta(minutes=30)
MAX_SECONDS_PER_HEARTBEAT = 300


class LessonPositionRequest(CamelModel):
    section_id: str | None = None
    scroll_percent: int | None = None
    seconds_delta: int | None = None


class LessonCompletionRequest(CamelModel):
    is_completed: bool = False


class ProblemStatusRequest(CamelModel):
    status: str | None = None
    solution_revealed: bool | None = None


class LessonProgressDto(CamelModel):
    lesson_id: int
    status: str
    is_completed: bool
    first_opened_at: DotNetDateTime
    last_opened_at: DotNetDateTime
    completed_at: DotNetDateTime | None
    last_section_id: str | None
    scroll_percent: int
    visit_count: int
    time_spent_seconds: int


class ProblemProgressDto(CamelModel):
    problem_id: int
    status: str
    solution_revealed_at: DotNetDateTime | None
    solved_at: DotNetDateTime | None
    updated_at: DotNetDateTime


class ResumeLessonDto(CamelModel):
    lesson_id: int
    title: str
    full_slug: str
    course_slug: str
    course_title: str
    module_slug: str
    module_title: str
    status: str
    last_section_id: str | None
    scroll_percent: int
    last_opened_at: DotNetDateTime


class ResumeDto(CamelModel):
    last_lesson: ResumeLessonDto | None
    next_lesson: ResumeLessonDto | None


class CourseProgressSummaryDto(CamelModel):
    course_id: int
    course_slug: str
    course_title: str
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    progress_percentage: int
    mcq_answered: int
    mcq_correct: int
    assignments_solved: int
    last_activity_at: DotNetDateTime | None


class LearnerSummaryDto(CamelModel):
    total_lessons_completed: int
    total_lessons_in_progress: int
    total_mcq_answered: int
    total_mcq_correct: int
    total_time_spent_seconds: int
    assignments_solved: int
    courses: list[CourseProgressSummaryDto]


class LessonMcqPerformanceDto(CamelModel):
    lesson_id: int
    lesson_title: str
    full_slug: str
    question_count: int
    answered_count: int
    correct_count: int
    accuracy_percentage: int
    last_answered_at: DotNetDateTime | None


class ActivityEventDto(CamelModel):
    id: int
    event_type: str
    occurred_at: DotNetDateTime
    lesson_id: int | None
    lesson_title: str | None
    problem_id: int | None
    metadata_json: str


@dataclass
class LatestAttemptRow:
    question_id: int
    lesson_id: int
    is_correct: bool
    answered_at: datetime


class LearnerProgressService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    async def get_completed_lesson_ids(self, user_id: int | None) -> set[int]:
        if user_id is None:
            return set()
        rows = (
            await self._session.execute(
                select(UserLessonProgress.lesson_id).where(
                    UserLessonProgress.user_id == user_id,
                    UserLessonProgress.status == "Completed",
                )
            )
        ).all()
        return {row[0] for row in rows}

    async def get_lesson_progress_map(
        self, user_id: int | None, lesson_ids: list[int] | set[int] | None = None
    ) -> dict[int, LessonProgressDto]:
        if user_id is None:
            return {}
        stmt = select(UserLessonProgress).where(UserLessonProgress.user_id == user_id)
        if lesson_ids is not None:
            id_list = list(lesson_ids)
            stmt = stmt.where(UserLessonProgress.lesson_id.in_(id_list))
        rows = (await self._session.execute(stmt)).scalars().all()
        return {row.lesson_id: _lesson_to_dto(row) for row in rows}

    async def get_solved_problem_ids(self, user_id: int | None) -> set[int]:
        if user_id is None:
            return set()
        rows = (
            await self._session.execute(
                select(UserProblemProgress.problem_id).where(
                    UserProblemProgress.user_id == user_id,
                    UserProblemProgress.status == "Solved",
                )
            )
        ).all()
        return {row[0] for row in rows}

    async def get_problem_progress_map(
        self, user_id: int | None, problem_ids: list[int] | set[int]
    ) -> dict[int, ProblemProgressDto]:
        if user_id is None:
            return {}
        id_list = list(problem_ids)
        rows = (
            await self._session.execute(
                select(UserProblemProgress).where(
                    UserProblemProgress.user_id == user_id,
                    UserProblemProgress.problem_id.in_(id_list),
                )
            )
        ).scalars().all()
        return {row.problem_id: _problem_to_dto(row) for row in rows}

    async def record_visit(self, user_id: int, lesson_id: int) -> LessonProgressDto | None:
        """Record that the learner opened a lesson (starts or continues a visit)."""
        exists = (
            await self._session.execute(select(Lesson.id).where(Lesson.id == lesson_id))
        ).first()
        if exists is None:
            return None
        now = self._utcnow()
        row, created = await self._upsert_lesson_row(user_id, lesson_id)
        is_new_visit = created or (now - row.last_opened_at) > VISIT_WINDOW
        if not created and is_new_visit:
            row.visit_count += 1
        row.last_opened_at = now
        row.updated_at = now
        if is_new_visit:
            self.add_activity(
                user_id, "LessonOpened", lesson_id=lesson_id, metadata={"VisitCount": row.visit_count}
            )
        dto = _lesson_to_dto(row)
        await self._save_with_unique_retry()
        return dto

    async def update_position(
        self, user_id: int, lesson_id: int, request: LessonPositionRequest
    ) -> LessonProgressDto | None:
        """Heartbeat from the reader: where the learner is and how long they stayed."""
        exists = (
            await self._session.execute(select(Lesson.id).where(Lesson.id == lesson_id))
        ).first()
        if exists is None:
            return None
        now = self._utcnow()
        row, _ = await self._upsert_lesson_row(user_id, lesson_id)
        if request.section_id and request.section_id.strip():
            section = request.section_id.strip()
            row.last_section_id = section[:160] if len(section) > 160 else section
        if request.scroll_percent is not None:
            row.scroll_percent = max(0, min(100, request.scroll_percent))
        if request.seconds_delta is not None and request.seconds_delta > 0:
            row.time_spent_seconds += min(request.seconds_delta, MAX_SECONDS_PER_HEARTBEAT)
        row.last_opened_at = now
        row.updated_at = now
        dto = _lesson_to_dto(row)
        await self._save_with_unique_retry()
        return dto

    async def set_lesson_completion(
        self, user_id: int, lesson_id: int, is_completed: bool
    ) -> LessonProgressDto | None:
        exists = (
            await self._session.execute(select(Lesson.id).where(Lesson.id == lesson_id))
        ).first()
        if exists is None:
            return None
        now = self._utcnow()
        row, _ = await self._upsert_lesson_row(user_id, lesson_id)
        was_completed = row.status == "Completed"
        row.status = "Completed" if is_completed else "InProgress"
        row.completed_at = (row.completed_at or now) if is_completed else None
        row.updated_at = now
        if was_completed != is_completed:
            self.add_activity(
                user_id,
                "LessonCompleted" if is_completed else "LessonReopened",
                lesson_id=lesson_id,
            )
        dto = _lesson_to_dto(row)
        await self._save_with_unique_retry()
        return dto

    async def set_problem_status(
        self, user_id: int, problem_id: int, request: ProblemStatusRequest
    ) -> ProblemProgressDto | None:
        status = (request.status or "").strip()
        if status not in ("NotStarted", "Attempted", "Solved"):
            raise ValueError("Status must be NotStarted, Attempted or Solved.")
        problem = (
            await self._session.execute(select(Problem).where(Problem.id == problem_id))
        ).scalar_one_or_none()
        if problem is None:
            return None
        now = self._utcnow()
        row = (
            await self._session.execute(
                select(UserProblemProgress).where(
                    UserProblemProgress.user_id == user_id,
                    UserProblemProgress.problem_id == problem_id,
                )
            )
        ).scalar_one_or_none()
        created = row is None
        if row is None:
            row = UserProblemProgress(
                user_id=user_id, problem_id=problem_id, created_at=now
            )
            self._session.add(row)
        previous = row.status
        row.status = status
        row.solved_at = (row.solved_at or now) if status == "Solved" else None
        row.updated_at = now
        if request.solution_revealed is True and row.solution_revealed_at is None:
            row.solution_revealed_at = now
            self.add_activity(
                user_id, "SolutionRevealed", lesson_id=problem.lesson_id, problem_id=problem_id
            )
        if previous != status or created:
            event_type = {"Solved": "ProblemCompleted", "Attempted": "ProblemAttempted"}.get(
                status, "ProblemReopened"
            )
            self.add_activity(
                user_id, event_type, lesson_id=problem.lesson_id, problem_id=problem_id
            )
        dto = _problem_to_dto(row)
        await self._save_with_unique_retry()
        return dto

    async def get_resume(self, user_id: int) -> ResumeDto:
        last = (
            await self._session.execute(
                select(UserLessonProgress)
                .options(
                    selectinload(UserLessonProgress.lesson)
                    .selectinload(Lesson.module)
                    .selectinload(CourseModule.course)
                )
                .where(UserLessonProgress.user_id == user_id)
                .order_by(desc(UserLessonProgress.last_opened_at))
            )
        ).scalars().first()
        lesson = last.lesson if last is not None else None
        module = lesson.module if lesson is not None else None
        course = module.course if module is not None else None
        if lesson is None or module is None or course is None:
            return ResumeDto(last_lesson=None, next_lesson=None)
        last_dto = _to_resume_dto(lesson, module, course, last)

        # Next = first lesson after the last-opened one (in course order) that isn't completed.
        ordered_lessons = (
            await self._session.execute(
                select(Lesson)
                .options(selectinload(Lesson.module))
                .join(CourseModule, Lesson.module_id == CourseModule.id)
                .where(CourseModule.course_id == course.id)
                .order_by(CourseModule.order_index, Lesson.order_index)
            )
        ).scalars().all()
        completed = await self.get_completed_lesson_ids(user_id)
        start_index = next(
            (i for i, lesson_row in enumerate(ordered_lessons) if lesson_row.id == last.lesson_id),
            -1,
        )
        candidates = list(ordered_lessons[start_index + 1 :]) + list(
            ordered_lessons[: max(start_index, 0)]
        )
        next_lesson = None
        if last.status == "Completed":
            next_lesson = next(
                (lesson_row for lesson_row in candidates if lesson_row.id not in completed),
                None,
            )
        next_dto = None
        if next_lesson is not None:
            next_dto = _to_resume_dto(next_lesson, next_lesson.module, course, None)
        return ResumeDto(last_lesson=last_dto, next_lesson=next_dto)

    async def get_summary(self, user_id: int) -> LearnerSummaryDto:
        courses = (
            await self._session.execute(
                select(Course)
                .options(
                    selectinload(Course.modules)
                    .selectinload(CourseModule.lessons)
                    .selectinload(Lesson.problems)
                )
                .order_by(Course.order_index)
            )
        ).scalars().all()
        lesson_rows = (
            await self._session.execute(
                select(UserLessonProgress).where(UserLessonProgress.user_id == user_id)
            )
        ).scalars().all()
        solved_problems = await self.get_solved_problem_ids(user_id)

        # Latest attempt per question for this user; a question counts once.
        latest_attempts = await self.get_latest_attempts(user_id)

        course_dtos: list[CourseProgressSummaryDto] = []
        for course in courses:
            lessons = [lesson for module in course.modules for lesson in module.lessons]
            if not lessons:
                continue
            lesson_ids = {lesson.id for lesson in lessons}
            rows = [row for row in lesson_rows if row.lesson_id in lesson_ids]
            attempts = [a for a in latest_attempts if a.lesson_id in lesson_ids]
            completed = sum(1 for row in rows if row.status == "Completed")
            last_activity = None
            candidates = [row.last_opened_at for row in rows] + [
                a.answered_at for a in attempts
            ]
            if candidates:
                last_activity = max(candidates)
            course_dtos.append(
                CourseProgressSummaryDto(
                    course_id=course.id,
                    course_slug=course.slug,
                    course_title=course.title,
                    total_lessons=len(lessons),
                    completed_lessons=completed,
                    in_progress_lessons=sum(1 for row in rows if row.status == "InProgress"),
                    progress_percentage=int(round(completed / len(lessons) * 100)),
                    mcq_answered=len(attempts),
                    mcq_correct=sum(1 for a in attempts if a.is_correct),
                    assignments_solved=sum(
                        1
                        for lesson in lessons
                        for problem in lesson.problems
                        if problem.id in solved_problems
                    ),
                    last_activity_at=last_activity,
                )
            )
        return LearnerSummaryDto(
            total_lessons_completed=sum(1 for row in lesson_rows if row.status == "Completed"),
            total_lessons_in_progress=sum(1 for row in lesson_rows if row.status == "InProgress"),
            total_mcq_answered=len(latest_attempts),
            total_mcq_correct=sum(1 for a in latest_attempts if a.is_correct),
            total_time_spent_seconds=sum(row.time_spent_seconds for row in lesson_rows),
            assignments_solved=len(solved_problems),
            courses=course_dtos,
        )

    async def get_mcq_performance(
        self, user_id: int, course_slug: str | None
    ) -> list[LessonMcqPerformanceDto]:
        latest = await self.get_latest_attempts(user_id)
        if not latest:
            return []
        lesson_ids = list({a.lesson_id for a in latest})
        lessons = (
            await self._session.execute(
                select(Lesson)
                .options(
                    selectinload(Lesson.module).selectinload(CourseModule.course)
                )
                .where(Lesson.id.in_(lesson_ids))
            )
        ).scalars().all()
        counts = (
            await self._session.execute(
                select(McqQuestion.lesson_id, func.count(McqQuestion.id))
                .where(
                    McqQuestion.lesson_id.in_(lesson_ids),
                    McqQuestion.is_active.is_(True),
                )
                .group_by(McqQuestion.lesson_id)
            )
        ).all()
        question_counts = {row[0]: row[1] for row in counts}
        result = []
        for lesson in lessons:
            module = lesson.module
            course = module.course if module is not None else None
            if course_slug and course_slug.strip() and (course is None or course.slug != course_slug):
                continue
            attempts = [a for a in latest if a.lesson_id == lesson.id]
            correct = sum(1 for a in attempts if a.is_correct)
            result.append(
                LessonMcqPerformanceDto(
                    lesson_id=lesson.id,
                    lesson_title=lesson.title,
                    full_slug=f"{course.slug if course else ''}/{module.slug if module else ''}/{lesson.slug}",
                    question_count=question_counts.get(lesson.id, len(attempts)),
                    answered_count=len(attempts),
                    correct_count=correct,
                    accuracy_percentage=(
                        0 if not attempts else int(round(correct / len(attempts) * 100))
                    ),
                    last_answered_at=max((a.answered_at for a in attempts), default=None),
                )
            )
        result.sort(
            key=lambda x: (
                x.accuracy_percentage,
                -(x.last_answered_at.timestamp() if x.last_answered_at else float("-inf")),
            )
        )
        return result

    async def get_activity(
        self, user_id: int, limit: int, before: datetime | None
    ) -> list[ActivityEventDto]:
        take = max(1, min(200, limit))
        stmt = (
            select(LearningActivity, Lesson.title)
            .outerjoin(Lesson, LearningActivity.lesson_id == Lesson.id)
            .where(LearningActivity.user_id == user_id)
        )
        if before is not None:
            stmt = stmt.where(LearningActivity.occurred_at < before)
        stmt = stmt.order_by(desc(LearningActivity.occurred_at)).limit(take)
        rows = (await self._session.execute(stmt)).all()
        return [
            ActivityEventDto(
                id=activity.id,
                event_type=activity.event_type,
                occurred_at=activity.occurred_at,
                lesson_id=activity.lesson_id,
                lesson_title=title,
                problem_id=activity.problem_id,
                metadata_json=activity.metadata_json,
            )
            for activity, title in rows
        ]

    def add_activity(
        self,
        user_id: int,
        event_type: str,
        lesson_id: int | None = None,
        problem_id: int | None = None,
        metadata: dict | None = None,
    ) -> None:
        self._session.add(
            LearningActivity(
                user_id=user_id,
                event_type=event_type,
                lesson_id=lesson_id,
                problem_id=problem_id,
                correlation_id=uuid4(),
                occurred_at=self._utcnow(),
                metadata_json="{}" if metadata is None else _json_dumps(metadata),
            )
        )

    async def get_latest_attempts(self, user_id: int) -> list[LatestAttemptRow]:
        """For each question the user answered, only their most recent attempt."""
        rows = (
            await self._session.execute(
                select(
                    McqQuestion.id,
                    McqQuestion.lesson_id,
                    McqAttempt.is_correct,
                    McqAttempt.answered_at,
                )
                .select_from(McqAttempt)
                .join(McqPresentation, McqAttempt.presentation_id == McqPresentation.id)
                .join(McqQuestion, McqPresentation.question_id == McqQuestion.id)
                .where(McqPresentation.user_id == user_id)
            )
        ).all()
        attempts = [
            LatestAttemptRow(
                question_id=row[0], lesson_id=row[1], is_correct=row[2], answered_at=row[3]
            )
            for row in rows
        ]
        # A single learner's attempt history is small; grouping in memory keeps the SQL simple.
        by_question: dict[int, list[LatestAttemptRow]] = {}
        for attempt in attempts:
            by_question.setdefault(attempt.question_id, []).append(attempt)
        return [
            max(group, key=lambda a: a.answered_at) for group in by_question.values()
        ]

    async def _upsert_lesson_row(
        self, user_id: int, lesson_id: int
    ) -> tuple[UserLessonProgress, bool]:
        row = (
            await self._session.execute(
                select(UserLessonProgress).where(
                    UserLessonProgress.user_id == user_id,
                    UserLessonProgress.lesson_id == lesson_id,
                )
            )
        ).scalar_one_or_none()
        if row is not None:
            return row, False
        now = self._utcnow()
        row = UserLessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status="InProgress",
            first_opened_at=now,
            last_opened_at=now,
            updated_at=now,
            visit_count=1,
            scroll_percent=0,
            time_spent_seconds=0,
        )
        self._session.add(row)
        return row, True

    async def _save_with_unique_retry(self) -> None:
        try:
            await self._session.flush()
        except IntegrityError as exc:
            # Two tabs inserted the same (user, lesson) row at once. The other insert won;
            # drop ours and let the caller's next heartbeat update the existing row.
            logger.info("Concurrent progress insert detected; discarding duplicate row: %s", exc)
            await self._session.rollback()


def _lesson_to_dto(row: UserLessonProgress) -> LessonProgressDto:
    return LessonProgressDto(
        lesson_id=row.lesson_id,
        status=row.status,
        is_completed=row.status == "Completed",
        first_opened_at=row.first_opened_at,
        last_opened_at=row.last_opened_at,
        completed_at=row.completed_at,
        last_section_id=row.last_section_id,
        scroll_percent=row.scroll_percent,
        visit_count=row.visit_count,
        time_spent_seconds=row.time_spent_seconds,
    )


def _problem_to_dto(row: UserProblemProgress) -> ProblemProgressDto:
    return ProblemProgressDto(
        problem_id=row.problem_id,
        status=row.status,
        solution_revealed_at=row.solution_revealed_at,
        solved_at=row.solved_at,
        updated_at=row.updated_at,
    )


def _to_resume_dto(
    lesson: Lesson,
    module: CourseModule | None,
    course: Course,
    row: UserLessonProgress | None,
) -> ResumeLessonDto:
    module_slug = module.slug if module is not None else ""
    module_title = module.title if module is not None else ""
    return ResumeLessonDto(
        lesson_id=lesson.id,
        title=lesson.title,
        full_slug=f"{course.slug}/{module_slug}/{lesson.slug}",
        course_slug=course.slug,
        course_title=course.title,
        module_slug=module_slug,
        module_title=module_title,
        status=row.status if row is not None else "NotStarted",
        last_section_id=row.last_section_id if row is not None else None,
        scroll_percent=row.scroll_percent if row is not None else 0,
        last_opened_at=(
            row.last_opened_at if row is not None else datetime(1, 1, 1, tzinfo=timezone.utc)
        ),
    )
