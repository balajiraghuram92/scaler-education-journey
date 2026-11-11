"""Ported from api/Services/LearningPathQueryService.cs."""

from __future__ import annotations

from pydantic import computed_field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.course import Course
from ..models.course_domain_link import CourseDomainLink
from ..models.course_module import CourseModule
from ..models.lesson import Lesson
from ..models.lesson_concept_link import LessonConceptLink
from ..schemas.base import CamelModel
from .learner_progress_service import LearnerProgressService


class LearningPathLessonSummaryDto(CamelModel):
    id: int
    slug: str
    title: str
    difficulty: str = "Intermediate"
    content_status: str = "Published"
    estimated_minutes: int = 0
    is_completed: bool = False
    order_index: int = 0
    problem_count: int = 0
    concept_slugs: list[str] = []


class ModuleDto(CamelModel):
    id: int
    slug: str
    title: str
    description: str = ""
    badge: str = ""
    order_index: int = 0
    lessons: list[LearningPathLessonSummaryDto] = []


class LearningPathDto(CamelModel):
    id: int
    slug: str
    title: str
    description: str = ""
    path_type: str = "Course"
    is_published: bool = True
    order_index: int = 0
    total_lessons: int = 0
    completed_lessons: int = 0
    domains: list[str] = []
    modules: list[ModuleDto] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def progress_percentage(self) -> int:
        if self.total_lessons == 0:
            return 0
        return int(round(self.completed_lessons / self.total_lessons * 100))


class LearningPathQueryService:
    def __init__(self, session: AsyncSession, progress: LearnerProgressService) -> None:
        self._session = session
        self._progress = progress

    async def get_all_learning_paths(self, user_id: int | None = None) -> list[LearningPathDto]:
        courses = (
            await self._session.execute(
                select(Course)
                .options(
                    selectinload(Course.domain_links).selectinload(
                        CourseDomainLink.domain
                    ),
                    selectinload(Course.modules)
                    .selectinload(CourseModule.lessons)
                    .selectinload(Lesson.problems),
                )
                .order_by(Course.order_index)
            )
        ).scalars().all()
        completed = await self._progress.get_completed_lesson_ids(user_id)
        # The C# GetAll query does not Include ConceptLinks, so conceptSlugs is
        # always empty here (unlike BySlug below). Ports the quirk as-is.
        return [
            _map_to_path_dto(course, completed, include_concepts=False) for course in courses
        ]

    async def get_learning_path_by_slug(
        self, slug: str, user_id: int | None = None
    ) -> LearningPathDto | None:
        course = (
            await self._session.execute(
                select(Course)
                .options(
                    selectinload(Course.domain_links).selectinload(
                        CourseDomainLink.domain
                    ),
                    selectinload(Course.modules)
                    .selectinload(CourseModule.lessons)
                    .selectinload(Lesson.problems),
                    selectinload(Course.modules)
                    .selectinload(CourseModule.lessons)
                    .selectinload(Lesson.concept_links)
                    .selectinload(LessonConceptLink.concept),
                )
                .where(Course.slug == slug)
            )
        ).scalar_one_or_none()
        if course is None:
            return None
        completed = await self._progress.get_completed_lesson_ids(user_id)
        return _map_to_path_dto(course, completed, include_concepts=True)


def _map_to_path_dto(
    course: Course, completed_lesson_ids: set[int], include_concepts: bool
) -> LearningPathDto:
    all_lessons = [lesson for module in course.modules for lesson in module.lessons]
    return LearningPathDto(
        id=course.id,
        slug=course.slug,
        title=course.title,
        description=course.description,
        path_type=course.path_type,
        is_published=course.is_published,
        order_index=course.order_index,
        total_lessons=len(all_lessons),
        completed_lessons=sum(1 for lesson in all_lessons if lesson.id in completed_lesson_ids),
        domains=[
            link.domain.name
            for link in course.domain_links
            if link.domain is not None and link.domain.name
        ],
        modules=[
            ModuleDto(
                id=module.id,
                slug=module.slug,
                title=module.title,
                description=module.description,
                badge=module.badge,
                order_index=module.order_index,
                lessons=[
                    LearningPathLessonSummaryDto(
                        id=lesson.id,
                        slug=lesson.slug,
                        title=lesson.title,
                        difficulty=lesson.difficulty,
                        content_status=lesson.content_status,
                        estimated_minutes=lesson.estimated_minutes,
                        is_completed=lesson.id in completed_lesson_ids,
                        order_index=lesson.order_index,
                        problem_count=len(lesson.problems),
                        concept_slugs=(
                            [
                                link.concept.slug
                                for link in lesson.concept_links
                                if link.concept is not None and link.concept.slug
                            ]
                            if include_concepts
                            else []
                        ),
                    )
                    for lesson in sorted(module.lessons, key=lambda row: row.order_index)
                ],
            )
            for module in sorted(course.modules, key=lambda m: m.order_index)
        ],
    )
