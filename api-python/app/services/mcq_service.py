"""Ported from api/Services/McqService.cs."""

from __future__ import annotations

import json
import logging
import random
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.course_module import CourseModule
from ..models.learning_activity import LearningActivity
from ..models.lesson import Lesson
from ..models.mcq_attempt import McqAttempt
from ..models.mcq_option import McqOption
from ..models.mcq_presentation import McqPresentation
from ..models.mcq_question import McqQuestion
from ..schemas.base import CamelModel, DotNetDateTime
from ..stjson import dumps as _json_dumps

logger = logging.getLogger(__name__)


class McqOptionPresentationDto(CamelModel):
    option_key: str = ""
    option_text: str = ""


class McqPreviousAttemptDto(CamelModel):
    selected_option_key: str = ""
    is_correct: bool = False
    correct_option_key: str = ""
    explanation: str = ""
    answered_at: DotNetDateTime


class McqPresentationDto(CamelModel):
    presentation_id: UUID
    question_id: int
    category: str = "Assignment"
    source_type: str = "FROM_MATERIAL"
    question_text: str = ""
    options: list[McqOptionPresentationDto] = []

    # Populated for a signed-in learner who already answered this question.
    previous_attempt: McqPreviousAttemptDto | None = None
    attempt_count: int = 0


class McqAttemptResultDto(CamelModel):
    is_correct: bool = False
    correct_option_key: str = ""
    explanation: str = ""
    selected_option_key: str = ""
    answered_at: DotNetDateTime


class McqAttemptRequest(CamelModel):
    selected_option_key: str | None = None


class McqAccessDeniedException(Exception):
    pass


_LESSON_SLUG_ALIASES = {
    "02-oop-classes-objects": "02-oop-1-intro-lab",
    "03-oop2-encapsulation-inheritance": "03-oop-2-access-modifiers-encapsulation",
}

_CATEGORY_ORDER = {"checkpoint": 0, "assignment": 1, "additional": 2}


class McqService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_practice_questions(
        self, course_slug: str, module_slug: str, lesson_slug: str, user_id: int | None
    ) -> list[McqPresentationDto]:
        resolved_lesson_slug = _LESSON_SLUG_ALIASES.get(lesson_slug.lower(), lesson_slug)
        lesson = (
            await self._session.execute(
                select(Lesson)
                .options(
                    selectinload(Lesson.module).selectinload(CourseModule.course)
                )
                .where(Lesson.slug == resolved_lesson_slug)
            )
        ).scalar_one_or_none()
        if (
            lesson is None
            or lesson.module is None
            or lesson.module.slug != module_slug
            or lesson.module.course is None
            or lesson.module.course.slug != course_slug
        ):
            logger.warning(
                "Lesson not found for path %s/%s/%s", course_slug, module_slug, lesson_slug
            )
            return []

        questions = (
            await self._session.execute(
                select(McqQuestion)
                .options(selectinload(McqQuestion.options))
                .where(McqQuestion.lesson_id == lesson.id, McqQuestion.is_active.is_(True))
                .order_by(McqQuestion.id)
            )
        ).scalars().all()
        questions = sorted(
            questions,
            key=lambda q: (_CATEGORY_ORDER.get((q.category or "").lower(), 9), q.id),
        )
        if not questions:
            return []

        # A signed-in learner resumes their own presentations: answered ones come back
        # with the recorded result, unanswered ones keep their option order.
        latest_by_question: dict[int, McqPresentation] = {}
        attempt_counts: dict[int, int] = {}
        if user_id is not None:
            question_ids = [q.id for q in questions]
            presentations = (
                await self._session.execute(
                    select(McqPresentation)
                    .options(selectinload(McqPresentation.attempt))
                    .where(
                        McqPresentation.user_id == user_id,
                        McqPresentation.question_id.in_(question_ids),
                    )
                )
            ).scalars().all()
            by_question: dict[int, list[McqPresentation]] = {}
            for presentation in presentations:
                by_question.setdefault(presentation.question_id, []).append(presentation)
            for question_id, group in by_question.items():
                latest_by_question[question_id] = max(group, key=lambda p: p.presented_at)
                attempt_counts[question_id] = sum(1 for p in group if p.attempt is not None)

        result: list[McqPresentationDto] = []
        created = False
        for question in questions:
            existing = latest_by_question.get(question.id)
            if existing is not None:
                presentation = existing
                ordered_options = _order_options(question.options, existing.displayed_option_order)
            else:
                ordered_options = sorted(question.options, key=lambda _: random.random())
                presentation = _new_presentation(question.id, user_id, ordered_options)
                self._session.add(presentation)
                created = True
            dto = _to_presentation_dto(question, presentation, ordered_options)
            dto.attempt_count = attempt_counts.get(question.id, 0)
            if presentation.attempt is not None:
                correct_key = next(
                    (o.option_key for o in question.options if o.is_correct), ""
                )
                dto.previous_attempt = McqPreviousAttemptDto(
                    selected_option_key=presentation.attempt.selected_option_key,
                    is_correct=presentation.attempt.is_correct,
                    correct_option_key=correct_key,
                    explanation=question.explanation,
                    answered_at=presentation.attempt.answered_at,
                )
            result.append(dto)
        if created:
            await self._session.flush()
        return result

    async def retry(self, presentation_id: UUID, user_id: int | None) -> McqPresentationDto:
        """Start a fresh, unanswered presentation of the same question ("try again")."""
        previous = (
            await self._session.execute(
                select(McqPresentation)
                .options(
                    selectinload(McqPresentation.question).selectinload(
                        McqQuestion.options
                    )
                )
                .where(McqPresentation.id == presentation_id)
            )
        ).scalar_one_or_none()
        if previous is None:
            raise KeyError(f"Presentation '{presentation_id}' not found.")
        _ensure_ownership(previous, user_id)
        question = previous.question
        if question is None:
            raise RuntimeError(
                f"Question for presentation '{presentation_id}' was not found."
            )
        ordered_options = sorted(question.options, key=lambda _: random.random())
        presentation = _new_presentation(
            question.id, user_id if user_id is not None else previous.user_id, ordered_options
        )
        self._session.add(presentation)
        await self._session.flush()

        attempt_count = 0
        if user_id is not None:
            attempt_count = (
                await self._session.execute(
                    select(func.count(McqAttempt.id))
                    .select_from(McqAttempt)
                    .join(McqPresentation, McqAttempt.presentation_id == McqPresentation.id)
                    .where(
                        McqPresentation.question_id == question.id,
                        McqPresentation.user_id == user_id,
                    )
                )
            ).scalar_one()
        dto = _to_presentation_dto(question, presentation, ordered_options)
        dto.attempt_count = attempt_count
        return dto

    async def record_attempt(
        self, presentation_id: UUID, selected_option_key: str, user_id: int | None = None
    ) -> McqAttemptResultDto:
        presentation = (
            await self._session.execute(
                select(McqPresentation)
                .options(
                    selectinload(McqPresentation.question).selectinload(
                        McqQuestion.options
                    ),
                    selectinload(McqPresentation.attempt),
                )
                .where(McqPresentation.id == presentation_id)
            )
        ).scalar_one_or_none()
        if presentation is None:
            raise KeyError(f"Presentation '{presentation_id}' not found.")
        _ensure_ownership(presentation, user_id)
        question = presentation.question
        if question is None:
            raise RuntimeError(
                f"Question for presentation '{presentation_id}' was not found."
            )
        correct_option = next((o for o in question.options if o.is_correct), None)
        correct_option_key = correct_option.option_key if correct_option else ""

        # Idempotency: if attempt already exists, return existing result
        if presentation.attempt is not None:
            return McqAttemptResultDto(
                is_correct=presentation.attempt.is_correct,
                correct_option_key=correct_option_key,
                explanation=question.explanation,
                selected_option_key=presentation.attempt.selected_option_key,
                answered_at=presentation.attempt.answered_at,
            )

        trimmed_key = (selected_option_key or "").strip()
        if not any(o.option_key.lower() == trimmed_key.lower() for o in question.options):
            raise ValueError(f"'{trimmed_key}' is not an option of this question.")
        is_correct = bool(correct_option_key) and correct_option_key.lower() == trimmed_key.lower()

        attempt = McqAttempt(
            id=uuid4(),
            presentation_id=presentation.id,
            selected_option_key=trimmed_key,
            is_correct=is_correct,
            answered_at=self._utcnow(),
        )
        self._session.add(attempt)
        if presentation.user_id is not None:
            self._session.add(
                LearningActivity(
                    user_id=presentation.user_id,
                    event_type="McqAnswered",
                    lesson_id=question.lesson_id,
                    correlation_id=attempt.id,
                    occurred_at=attempt.answered_at,
                    metadata_json=_json_dumps(
                        {
                            "questionId": question.id,
                            "LegacyKey": question.legacy_key,
                            "Category": question.category,
                            "selectedOptionKey": trimmed_key,
                            "isCorrect": is_correct,
                        }
                    ),
                )
            )
        try:
            await self._session.flush()
        except IntegrityError as exc:
            logger.warning(
                "Conflict saving attempt for presentation %s. Checking for existing attempt: %s",
                presentation_id,
                exc,
            )
            await self._session.rollback()
            existing_attempt = (
                await self._session.execute(
                    select(McqAttempt).where(McqAttempt.presentation_id == presentation_id)
                )
            ).scalar_one_or_none()
            if existing_attempt is not None:
                return McqAttemptResultDto(
                    is_correct=existing_attempt.is_correct,
                    correct_option_key=correct_option_key,
                    explanation=question.explanation,
                    selected_option_key=existing_attempt.selected_option_key,
                    answered_at=existing_attempt.answered_at,
                )
            raise
        return McqAttemptResultDto(
            is_correct=is_correct,
            correct_option_key=correct_option_key,
            explanation=question.explanation,
            selected_option_key=trimmed_key,
            answered_at=attempt.answered_at,
        )


def _ensure_ownership(presentation: McqPresentation, user_id: int | None) -> None:
    # A presentation issued to a signed-in learner can only be answered by that learner.
    if presentation.user_id is not None and presentation.user_id != user_id:
        raise McqAccessDeniedException("This question was presented to a different account.")


def _new_presentation(
    question_id: int, user_id: int | None, ordered_options: list[McqOption]
) -> McqPresentation:
    return McqPresentation(
        id=uuid4(),
        question_id=question_id,
        user_id=user_id,
        displayed_option_order=_json_dumps([o.option_key for o in ordered_options]),
        question_text_shown=None,
        presented_at=datetime.now(UTC),
    )


def _order_options(options: list[McqOption], displayed_order_json: str) -> list[McqOption]:
    items = list(options)
    try:
        order = json.loads(displayed_order_json)
        if not isinstance(order, list):
            return sorted(items, key=lambda o: o.option_key)
        rank = {str(key).lower(): index for index, key in enumerate(order)}
        return sorted(
            items, key=lambda o: (rank.get(o.option_key.lower(), 2**31 - 1), o.option_key)
        )
    except (json.JSONDecodeError, ValueError, TypeError):
        return sorted(items, key=lambda o: o.option_key)


def _to_presentation_dto(
    question: McqQuestion, presentation: McqPresentation, ordered_options: list[McqOption]
) -> McqPresentationDto:
    # Options: optionKey and optionText only - NO correctness or explanation!
    return McqPresentationDto(
        presentation_id=presentation.id,
        question_id=question.id,
        category=question.category,
        source_type=question.source_type,
        question_text=question.question_text,
        options=[
            McqOptionPresentationDto(option_key=o.option_key, option_text=o.option_text)
            for o in ordered_options
        ],
    )
