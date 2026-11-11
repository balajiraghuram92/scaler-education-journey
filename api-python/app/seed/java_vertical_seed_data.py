"""Ported from api/Data/JavaVerticalSeedData.cs.

Seeder LOGIC is hand-ported here; the lesson/module/task DATA is extracted from the C#
file by tools/extract_seed_data.py into app/seed/data/java_vertical.json (see
info/muse-prompts/python-port/P0-to-P8-prompts.md P7 step 2). Run the converter first:

    python api-python/tools/extract_seed_data.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.course import Course
from ..models.course_module import CourseModule
from ..models.lesson import Lesson
from ..models.lesson_resource import LessonResource
from ..models.study_task import StudyTask
from ..models.study_vertical import StudyVertical

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "java_vertical.json")

STANDALONE_EXPANDED_COURSE_ORDERS = {
    "databases-sql": 3,
    "high-level-design": 4,
    "data-engineering": 5,
}

_MODULE_METHODS = [
    ("oop-foundations", "SeedModule1Lessons"),
    ("concurrency-multithreading", "SeedModule2Lessons"),
    ("advanced-java-collections", "SeedModule3Lessons"),
    ("design-principles-patterns", "SeedModule4Lessons"),
    ("applied-machine-coding", "SeedModule5Lessons"),
    ("spring-enterprise-architecture", "SeedModule6Lessons"),
]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _load_data() -> dict:
    if not os.path.isfile(DATA_PATH):
        raise RuntimeError(
            "java_vertical.json is missing. Run the converter first: "
            "python api-python/tools/extract_seed_data.py"
        )
    with open(DATA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _resolve_content(value: object, authored: dict[str, str]) -> str:
    if isinstance(value, dict) and "$content_ref" in value:
        return authored.get(value["$content_ref"], "")
    return value if isinstance(value, str) else ""


async def seed(session: AsyncSession) -> None:
    data = _load_data()
    authored: dict[str, str] = data["authored_content"]

    # 1. Seed or Update StudyVertical for Java & Spring Architecture
    java_vertical = (
        await session.execute(
            select(StudyVertical).where(
                StudyVertical.name == "Java & Spring Architecture"
            )
        )
    ).scalar_one_or_none()
    if java_vertical is None:
        java_vertical = StudyVertical(
            name="Java & Spring Architecture",
            description="Low-Level Design, Concurrency, Spring Boot & Distributed Enterprise Systems",
            updated_at=_utcnow(),
        )
        session.add(java_vertical)
        await session.flush()

    # Populate vertical tasks if empty
    has_tasks = (
        await session.execute(
            select(StudyTask.id).where(StudyTask.vertical_id == java_vertical.id).limit(1)
        )
    ).first()
    if has_tasks is None:
        for task in data["vertical_tasks"]:
            session.add(
                StudyTask(
                    vertical_id=java_vertical.id,
                    module=task.get("Module", "General"),
                    title=task.get("Title", ""),
                    is_completed=bool(task.get("IsCompleted", False)),
                    updated_at=_utcnow(),
                )
            )
        await session.flush()

    # 2. Seed Course Hierarchy for Java LLD & Spring Architecture
    course = (
        await session.execute(select(Course).where(Course.slug == "java-spring-lld"))
    ).scalar_one_or_none()
    if course is None:
        now = _utcnow()
        course = Course(
            slug="java-spring-lld",
            title="Java Low-Level Design & Spring Architecture",
            description="Mastering Object-Oriented Design, Concurrency, JVM Internals, and Spring Boot Enterprise Architecture.",
            order_index=1,
            vertical_id=java_vertical.id,
            path_type="Course",
            is_published=True,
            created_at=now,
            updated_at=now,
        )
        session.add(course)
        await session.flush()

        modules_by_method: dict[str, CourseModule] = {}
        for order, (slug, title, description, badge) in enumerate(
            [
                ("oop-foundations", "OOP Foundations & Design Principles", "Core encapsulation, constructor chaining, class hierarchies, polymorphism, and abstraction.", "Module 1"),
                ("concurrency-multithreading", "Concurrency & Multithreading", "Thread lifecycles, race conditions, synchronized blocks, locks, semaphores, and executors.", "Module 2"),
                ("advanced-java-collections", "Advanced Java, Collections & Streams", "Generics, type erasure, collections framework internals, lambda expressions, and functional stream pipelines.", "Module 3"),
                ("design-principles-patterns", "Design Principles & Patterns for Extensible Systems", "SOLID principles, creational, structural, and behavioural design patterns, and UML class diagrams.", "Module 4"),
                ("applied-machine-coding", "Applied Design & Machine Coding", "End-to-end object-oriented design and implementation of real-world systems: TicTacToe, Parking Lot, BookMyShow, and Splitwise.", "Module 5"),
                ("spring-enterprise-architecture", "Spring Boot & Enterprise Architecture", "Dependency injection, Spring Data JPA, RESTful API design, PostgreSQL integration, and distributed architectures.", "Module 6"),
            ],
            start=1,
        ):
            module = CourseModule(
                course_id=course.id,
                slug=slug,
                title=title,
                description=description,
                badge=badge,
                order_index=order,
                created_at=now,
                updated_at=now,
            )
            session.add(module)
            await session.flush()
            modules_by_method[slug] = module

        for slug, method in _MODULE_METHODS:
            await _seed_module_lessons(
                session, modules_by_method[slug].id, data["module_lessons"][method], authored
            )
        lesson3_id = (
            await session.execute(
                select(Lesson.id).where(
                    Lesson.slug == "03-oop-2-access-modifiers-encapsulation"
                )
            )
        ).scalar_one_or_none()
        if lesson3_id is not None:
            await _seed_lesson3_study_guide(session, data, lesson3_id)
        await session.flush()

    # Idempotent module restructure — safe to run on existing databases
    existing_course = (
        await session.execute(select(Course).where(Course.slug == "java-spring-lld"))
    ).scalar_one_or_none()
    if existing_course is not None:
        spring_module = (
            await session.execute(
                select(CourseModule).where(
                    CourseModule.course_id == existing_course.id,
                    CourseModule.slug == "spring-enterprise-architecture",
                )
            )
        ).scalar_one_or_none()
        if spring_module is not None and spring_module.order_index != 6:
            spring_module.order_index = 6
            spring_module.badge = "Module 6"
            await session.flush()

        design_module = await _ensure_canonical_module(
            session,
            existing_course.id,
            "design-principles-patterns",
            "Design Principles & Patterns for Extensible Systems",
            "SOLID principles, creational, structural, and behavioural design patterns, and UML class diagrams.",
            "Module 4",
            4,
        )
        has_14 = (
            await session.execute(
                select(Lesson.id)
                .where(
                    Lesson.module_id == design_module.id, Lesson.slug == "14-solid-principles"
                )
                .limit(1)
            )
        ).first()
        if has_14 is None:
            await _seed_module_lessons(
                session, design_module.id, data["module_lessons"]["SeedModule4Lessons"], authored
            )
            await session.flush()

        machine_module = await _ensure_canonical_module(
            session,
            existing_course.id,
            "applied-machine-coding",
            "Applied Design & Machine Coding",
            "End-to-end object-oriented design and implementation of real-world systems: TicTacToe, Parking Lot, BookMyShow, and Splitwise.",
            "Module 5",
            5,
        )
        has_18 = (
            await session.execute(
                select(Lesson.id)
                .where(
                    Lesson.module_id == machine_module.id,
                    Lesson.slug == "18-how-to-approach-design",
                )
                .limit(1)
            )
        ).first()
        if has_18 is None:
            await _seed_module_lessons(
                session, machine_module.id, data["module_lessons"]["SeedModule5Lessons"], authored
            )
            await session.flush()

    assert course is not None
    await _backfill_lesson_content(session, course.id, authored)
    await _ensure_standalone_expanded_courses(session, course, data)
    await _ensure_expanded_modules(session, course.id, data)
    await session.flush()


async def _ensure_canonical_module(
    session: AsyncSession,
    course_id: int,
    slug: str,
    title: str,
    description: str,
    badge: str,
    order_index: int,
) -> CourseModule:
    module = (
        await session.execute(
            select(CourseModule).where(
                CourseModule.course_id == course_id, CourseModule.slug == slug
            )
        )
    ).scalar_one_or_none()
    now = _utcnow()
    if module is None:
        module = CourseModule(
            course_id=course_id,
            slug=slug,
            title=title,
            description=description,
            badge=badge,
            order_index=order_index,
            created_at=now,
            updated_at=now,
        )
        session.add(module)
        await session.flush()
    elif (
        module.badge != badge
        or module.title != title
        or module.description != description
        or module.order_index != order_index
    ):
        module.badge = badge
        module.title = title
        module.description = description
        module.order_index = order_index
        await session.flush()
    return module


async def _seed_module_lessons(
    session: AsyncSession, module_id: int, lessons: list[dict], authored: dict[str, str]
) -> None:
    for record in lessons:
        now = _utcnow()
        session.add(
            Lesson(
                module_id=module_id,
                slug=record.get("Slug", ""),
                title=record.get("Title", ""),
                description=record.get("Description", ""),
                lecture_number=record.get("LectureNumber", 0),
                class_date=record.get("ClassDate", ""),
                content_body=_resolve_content(record.get("ContentBody"), authored),
                horstmann_ref=record.get("HorstmannRef", ""),
                estimated_minutes=record.get("EstimatedMinutes", 0),
                is_completed=bool(record.get("IsCompleted", False)),
                order_index=record.get("OrderIndex", 0),
                difficulty=record.get("Difficulty", "Intermediate"),
                content_status=record.get("ContentStatus", "Published"),
                created_at=now,
                updated_at=now,
            )
        )
    await session.flush()


async def _seed_lesson3_study_guide(
    session: AsyncSession, data: dict, lesson_id: int
) -> None:
    # No idempotency check in C# either; this runs once when the course is created.
    for topic in data["study_guide"]:
        session.add(
            LessonResource(
                lesson_id=lesson_id,
                resource_type="StudyGuideTopic",
                title=topic["title"],
                content_body=topic["content"],
                order_index=topic["order"],
                created_at=_utcnow(),
            )
        )
    await session.flush()


async def _backfill_lesson_content(
    session: AsyncSession, course_id: int, authored: dict[str, str]
) -> None:
    lessons = (
        await session.execute(
            select(Lesson)
            .join(CourseModule, Lesson.module_id == CourseModule.id)
            .where(CourseModule.course_id == course_id)
        )
    ).scalars().all()
    for lesson in lessons:
        authored_content = authored.get(lesson.slug)
        if authored_content is None or not _needs_lesson_content(lesson.content_body):
            continue
        lesson.content_body = authored_content
        lesson.content_status = "Draft"
        lesson.updated_at = _utcnow()
    await session.flush()


def _needs_lesson_content(content: str | None) -> bool:
    if not content or not content.strip():
        return True
    # Preserve an authored body even if it was written outside this seed file.
    if (
        "## Practical Backend Scenario" in content
        and "## Practice Loop" in content
        and "## Evidence of Understanding" in content
    ):
        return False
    return True


async def _ensure_standalone_expanded_courses(
    session: AsyncSession, java_course: Course, data: dict
) -> None:
    definitions = {
        m["slug"]: m
        for m in data["expanded_modules"]
        if m["slug"] in STANDALONE_EXPANDED_COURSE_ORDERS
    }
    for slug, order in STANDALONE_EXPANDED_COURSE_ORDERS.items():
        await _ensure_standalone_expanded_course(
            session, java_course, definitions[slug], order
        )


async def _ensure_standalone_expanded_course(
    session: AsyncSession, java_course: Course, definition: dict, order_index: int
) -> None:
    standalone_course = (
        await session.execute(select(Course).where(Course.slug == definition["slug"]))
    ).scalar_one_or_none()
    now = _utcnow()
    if standalone_course is None:
        standalone_course = Course(
            slug=definition["slug"],
            title=definition["title"],
            description=definition["description"],
            order_index=order_index,
            path_type="Course",
            is_published=True,
            vertical_id=None,
            created_at=now,
            updated_at=now,
        )
        session.add(standalone_course)
        await session.flush()
    else:
        standalone_course.title = definition["title"]
        standalone_course.description = definition["description"]
        standalone_course.path_type = "Course"
        standalone_course.is_published = True
        standalone_course.order_index = order_index

    java_module = (
        await session.execute(
            select(CourseModule).where(
                CourseModule.course_id == java_course.id,
                CourseModule.slug == definition["slug"],
            )
        )
    ).scalar_one_or_none()
    standalone_module = (
        await session.execute(
            select(CourseModule).where(
                CourseModule.course_id == standalone_course.id,
                CourseModule.slug == definition["slug"],
            )
        )
    ).scalar_one_or_none()

    if (
        java_module is not None
        and standalone_module is not None
        and java_module.id != standalone_module.id
    ):
        raise RuntimeError(
            f"Expanded curriculum '{definition['slug']}' exists under both Java LLD "
            "and its standalone course. Resolve the duplicate modules before seeding."
        )

    if standalone_module is None and java_module is not None:
        # Re-home the existing module instead of recreating it. This keeps
        # lesson ids, authored bodies, linked resources, and completion state.
        java_module.course_id = standalone_course.id
        java_module.updated_at = _utcnow()

    await session.flush()
    await _ensure_expanded_modules_for(session, standalone_course.id, [definition])


async def _ensure_expanded_modules(
    session: AsyncSession, course_id: int, data: dict
) -> None:
    java_definitions = [
        m
        for m in data["expanded_modules"]
        if m["slug"] not in STANDALONE_EXPANDED_COURSE_ORDERS
    ]
    await _ensure_expanded_modules_for(session, course_id, java_definitions)


async def _ensure_expanded_modules_for(
    session: AsyncSession, course_id: int, definitions: list[dict]
) -> None:
    max_lecture = (
        await session.execute(
            select(func.max(Lesson.lecture_number))
            .select_from(Lesson)
            .join(CourseModule, Lesson.module_id == CourseModule.id)
            .where(CourseModule.course_id == course_id)
        )
    ).scalar_one()
    next_lecture_number = max_lecture or 0

    for definition in definitions:
        module = (
            await session.execute(
                select(CourseModule).where(
                    CourseModule.course_id == course_id,
                    CourseModule.slug == definition["slug"],
                )
            )
        ).scalar_one_or_none()
        now = _utcnow()
        if module is None:
            module = CourseModule(
                course_id=course_id,
                slug=definition["slug"],
                title=definition["title"],
                description=definition["description"],
                badge=definition["badge"],
                order_index=definition["order_index"],
                created_at=now,
                updated_at=now,
            )
            session.add(module)
            await session.flush()

        for lesson_index, chapter in enumerate(definition["lessons"]):
            lesson = (
                await session.execute(
                    select(Lesson).where(
                        Lesson.module_id == module.id, Lesson.slug == chapter["slug"]
                    )
                )
            ).scalar_one_or_none()
            if lesson is None:
                next_lecture_number += 1
                session.add(
                    Lesson(
                        module_id=module.id,
                        slug=chapter["slug"],
                        title=chapter["title"],
                        description=chapter["description"],
                        lecture_number=next_lecture_number,
                        class_date="",
                        content_body=_build_expanded_content(chapter),
                        horstmann_ref=chapter["reference"],
                        estimated_minutes=chapter["estimated_minutes"],
                        is_completed=False,
                        order_index=lesson_index + 1,
                        difficulty=chapter["difficulty"],
                        content_status="Draft",
                        created_at=now,
                        updated_at=now,
                    )
                )
                continue

            # A refresh may encounter an earlier outline-only import. Complete that
            # row, but never replace a substantive body or alter progress metadata.
            if not lesson.content_body or not lesson.content_body.strip() or lesson.content_status == "Outline":
                lesson.content_body = _build_expanded_content(chapter)
                lesson.updated_at = _utcnow()
                if not lesson.content_status or not lesson.content_status.strip() or lesson.content_status == "Outline":
                    lesson.content_status = "Draft"
        await session.flush()


def _build_expanded_content(chapter: dict) -> str:
    # Chapter() builds $"# {title}\n\n## Concepts Covered\n..." — LF newlines from
    # the interpolated (non-verbatim) string.
    return (
        f"# {chapter['title']}\n\n## Concepts Covered\n{chapter['concepts']}\n\n"
        f"## Practical Backend Scenario\n{chapter['scenario']}\n\n"
        f"## Practice Loop\n{chapter['practice']}\n\n"
        f"## Evidence of Understanding\n{chapter['evidence']}\n\n"
        f"## Suggested Extension\n{chapter['extension']}"
    )
