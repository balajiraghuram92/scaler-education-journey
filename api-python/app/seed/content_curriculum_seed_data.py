"""Ported from api/Data/ContentCurriculumSeedData.cs.

Seeds a file-driven course from a folder under api/Data/Content/{folder}:
  course.json              — vertical, course, modules and lesson metadata (source of truth for structure)
  lessons/{slug}.md        — lesson body (markdown)
  assignments/{slug}.json  — coding assignments, stored as Problems
  diagrams/{slug}.json     — inline SVG diagrams, referenced from the body as {{diagram:N}} (N = order index)
  mcqs/{slug}.json         — multiple-choice questions, keyed by a globally unique legacyKey

The files are canonical: when a lesson file changes, the stored body is replaced and the lesson
returns to Draft for review. Diagrams and MCQs are updated in place from their files. Learner
progress, notes and MCQ history are keyed by lesson id, question id and option key, so they
survive content updates.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.course import Course
from ..models.course_module import CourseModule
from ..models.lesson import Lesson
from ..models.lesson_diagram import LessonDiagram
from ..models.mcq_option import McqOption
from ..models.mcq_question import McqQuestion
from ..models.problem import Problem
from ..models.study_vertical import StudyVertical


def resolve_content_root(folder: str) -> str | None:
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    candidates = [
        os.path.join(repo_root, "api", "Data", "Content", folder),
        os.path.join(os.getcwd(), "Data", "Content", folder),
        os.path.join(os.getcwd(), "api", "Data", "Content", folder),
    ]
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, "course.json")):
            return candidate
    return None


def _get(obj: dict, name: str, default=None):  # type: ignore[no-untyped-def]
    for key, value in obj.items():
        if str(key).lower() == name.lower():
            return value
    return default


def _norm(text: str | None) -> str:
    # C#: (text ?? "").Replace("\r\n", "\n").TrimEnd() + "\n"  (TrimEnd trims whitespace)
    return (text or "").replace("\r\n", "\n").rstrip() + "\n"


def _truncate(value: str | None, max_length: int) -> str:
    text = value or ""
    return text if len(text) <= max_length else text[:max_length]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def seed_folder(session: AsyncSession, folder: str) -> None:
    root = resolve_content_root(folder)
    if root is None:
        print(f"[WARN] Curriculum content folder (Data/Content/{folder}) was not found. Skipping.")
        return
    await seed(session, root)


async def seed(session: AsyncSession, root: str) -> None:
    with open(os.path.join(root, "course.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    if manifest is None:
        raise ValueError(f"{os.path.join(root, 'course.json')} could not be parsed.")

    vertical_name = _get(manifest, "verticalName", "") or ""
    vertical = (
        await session.execute(
            select(StudyVertical).where(StudyVertical.name == vertical_name)
        )
    ).scalar_one_or_none()
    if vertical is None:
        vertical = StudyVertical(
            name=vertical_name,
            description=_get(manifest, "verticalDescription", "") or "",
            updated_at=_utcnow(),
        )
        session.add(vertical)
        await session.flush()

    course_slug = _get(manifest, "slug", "") or ""
    course = (
        await session.execute(select(Course).where(Course.slug == course_slug))
    ).scalar_one_or_none()
    if course is None:
        course = Course(slug=course_slug)
        session.add(course)

    course.title = _get(manifest, "title", "") or ""
    course.description = _get(manifest, "description", "") or ""
    course.order_index = _get(manifest, "orderIndex", 2) or 0
    course.path_type = "Course"
    course.is_published = True
    course.vertical_id = vertical.id
    if course.created_at is None:
        course.created_at = _utcnow()
    course.updated_at = _utcnow()
    await session.flush()

    lecture_number = 0
    lessons_changed = 0
    modules = _get(manifest, "modules", []) or []
    for module_index, module_def in enumerate(modules):
        module_slug = _get(module_def, "slug", "") or ""
        module = (
            await session.execute(
                select(CourseModule).where(
                    CourseModule.course_id == course.id, CourseModule.slug == module_slug
                )
            )
        ).scalar_one_or_none()
        if module is None:
            module = CourseModule(course_id=course.id, slug=module_slug)
            session.add(module)
        module.title = _get(module_def, "title", "") or ""
        module.description = _get(module_def, "description", "") or ""
        module.badge = _get(module_def, "badge", "") or ""
        module.order_index = module_index + 1
        if module.created_at is None:
            module.created_at = _utcnow()
        module.updated_at = _utcnow()
        await session.flush()

        lessons = _get(module_def, "lessons", []) or []
        for lesson_index, lesson_def in enumerate(lessons):
            lesson_slug = _get(lesson_def, "slug", "") or ""
            lecture_number += 1
            body_path = os.path.join(root, "lessons", f"{lesson_slug}.md")
            if os.path.isfile(body_path):
                with open(body_path, encoding="utf-8") as fh:
                    body = _norm(fh.read())
                body_exists = True
            else:
                title = _get(lesson_def, "title", "") or ""
                description = _get(lesson_def, "description", "") or ""
                body = f"# {title}\n\n{description}\n\nThis chapter is being written."
                body_exists = False

            lesson = (
                await session.execute(
                    select(Lesson).where(
                        Lesson.module_id == module.id, Lesson.slug == lesson_slug
                    )
                )
            ).scalar_one_or_none()
            if lesson is None:
                lesson = Lesson(
                    module_id=module.id,
                    slug=lesson_slug,
                    class_date="",
                    content_status="Draft" if body_exists else "Outline",
                    content_body=body,
                    is_completed=False,
                    created_at=_utcnow(),
                )
                session.add(lesson)
                lessons_changed += 1
            elif _norm(lesson.content_body) != body:
                lesson.content_body = body
                lesson.content_status = "Draft" if body_exists else "Outline"
                lesson.updated_at = _utcnow()
                lessons_changed += 1

            lesson.title = _get(lesson_def, "title", "") or ""
            lesson.description = _get(lesson_def, "description", "") or ""
            lesson.lecture_number = lecture_number
            lesson.order_index = lesson_index + 1
            minutes = _get(lesson_def, "minutes", 0) or 0
            lesson.estimated_minutes = minutes if minutes > 0 else 60
            difficulty = _get(lesson_def, "difficulty")
            lesson.difficulty = difficulty if difficulty and str(difficulty).strip() else "Intermediate"
            lesson.horstmann_ref = _get(lesson_def, "reference") or ""
            if lesson.created_at is None:
                lesson.created_at = _utcnow()
            lesson.updated_at = _utcnow()
            await session.flush()

            await _seed_assignments(session, root, lesson)
            await _seed_diagrams(session, root, lesson)
            await _seed_mcqs(session, root, lesson)

    print(
        f"[INFO] {course.title} seeded: {len(modules)} modules, {lecture_number} lessons ({lessons_changed} new or updated)."
    )


async def _seed_assignments(session: AsyncSession, root: str, lesson: Lesson) -> None:
    path = os.path.join(root, "assignments", f"{lesson.slug}.json")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        file = json.load(fh)
    assignments = _get(file, "assignments") if isinstance(file, dict) else None
    if assignments is None:
        return
    for i, definition in enumerate(assignments):
        slug = _get(definition, "slug", "") or ""
        if not slug.strip():
            continue
        problem = (
            await session.execute(
                select(Problem).where(
                    Problem.lesson_id == lesson.id, Problem.slug == slug
                )
            )
        ).scalar_one_or_none()
        if problem is None:
            problem = Problem(
                lesson_id=lesson.id, slug=slug, is_completed=False, created_at=_utcnow()
            )
            session.add(problem)
        problem.title = _truncate(_get(definition, "title", "") or "", 200)
        difficulty = _get(definition, "difficulty")
        problem.difficulty = _truncate(
            difficulty if difficulty and str(difficulty).strip() else "Core", 50
        )
        problem.package_name = ""
        problem.test_class_name = ""
        problem.problem_statement = _get(definition, "problemStatement") or ""
        problem.requirements_body = _get(definition, "requirements") or ""
        problem.worked_example = _get(definition, "workedExample") or ""
        problem.hints = _get(definition, "hints") or ""
        problem.reference_solution = _get(definition, "referenceSolution") or ""
        run_command = _get(definition, "runCommand")
        problem.run_command = _truncate(
            run_command if run_command and str(run_command).strip() else "pytest -q", 200
        )
        problem.language = "python"
        source = _get(definition, "source")
        problem.source_type = _truncate(
            source if source and str(source).strip() else "LLM_GENERATED", 30
        )
        problem.order_index = i + 1
        problem.updated_at = _utcnow()
    await session.flush()


async def _seed_diagrams(session: AsyncSession, root: str, lesson: Lesson) -> None:
    path = os.path.join(root, "diagrams", f"{lesson.slug}.json")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        file = json.load(fh)
    diagrams = _get(file, "diagrams") if isinstance(file, dict) else None
    if diagrams is None:
        return

    # Diagrams are matched by position: the body references them as {{diagram:N}}.
    existing = (
        await session.execute(
            select(LessonDiagram).where(LessonDiagram.lesson_id == lesson.id)
        )
    ).scalars().all()
    for i, definition in enumerate(diagrams):
        order_index = i + 1
        diagram = next((d for d in existing if d.order_index == order_index), None)
        if diagram is None:
            diagram = LessonDiagram(
                lesson_id=lesson.id, order_index=order_index, created_at=_utcnow()
            )
            session.add(diagram)
        title = _get(definition, "title")
        diagram.title = _truncate(
            title if title and str(title).strip() else f"Diagram {order_index}", 200
        )
        diagram.caption = _truncate(_get(definition, "caption"), 300)
        diagram.diagram_type = "svg-inline"
        diagram.svg_content = _get(definition, "svg") or ""
    for stale in [d for d in existing if d.order_index > len(diagrams)]:
        await session.delete(stale)
    await session.flush()


async def _seed_mcqs(session: AsyncSession, root: str, lesson: Lesson) -> None:
    path = os.path.join(root, "mcqs", f"{lesson.slug}.json")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        file = json.load(fh)
    questions = _get(file, "questions") if isinstance(file, dict) else None
    if questions is None:
        return

    keys = [
        _get(q, "legacyKey", "") or ""
        for q in questions
        if (_get(q, "legacyKey", "") or "").strip()
    ]
    existing = (
        await session.execute(
            select(McqQuestion)
            .options(selectinload(McqQuestion.options))
            .where(
                (McqQuestion.lesson_id == lesson.id)
                | (
                    McqQuestion.legacy_key.is_not(None)
                    & McqQuestion.legacy_key.in_(keys)
                )
            )
        )
    ).scalars().all()
    existing = list(existing)

    for definition in questions:
        legacy_key = _get(definition, "legacyKey", "") or ""
        if not legacy_key.strip():
            continue
        question = next((q for q in existing if q.legacy_key == legacy_key), None)
        if question is None:
            question = McqQuestion(legacy_key=legacy_key, created_at=_utcnow())
            session.add(question)
            existing.append(question)
        question.lesson_id = lesson.id
        question.question_text = _get(definition, "questionText", "") or ""
        question.explanation = _get(definition, "explanation") or ""
        source_type = _get(definition, "sourceType")
        question.source_type = _truncate(
            source_type if source_type and str(source_type).strip() else "FROM_MATERIAL", 50
        )
        category = _get(definition, "category")
        question.category = _truncate(
            category if category and str(category).strip() else "Checkpoint", 30
        )
        question.is_active = True
        question.updated_at = _utcnow()

        # Attempts store the option key, so options are updated in place by key.
        for option_def in _get(definition, "options", []) or []:
            option_key = _get(option_def, "optionKey", "") or ""
            option = next(
                (o for o in question.options if o.option_key == option_key), None
            )
            if option is None:
                option = McqOption(option_key=option_key)
                question.options.append(option)
            option.option_text = _get(option_def, "optionText", "") or ""
            option.is_correct = bool(_get(option_def, "isCorrect", False))

        option_keys = {_get(o, "optionKey", "") or "" for o in _get(definition, "options", []) or []}
        for stale in [o for o in list(question.options) if o.option_key not in option_keys]:
            question.options.remove(stale)
            await session.delete(stale)

    # Questions removed from the file stop being served but keep their attempt history.
    for removed in [
        q for q in existing if q.lesson_id == lesson.id and (q.legacy_key or "") not in keys
    ]:
        removed.is_active = False

    await session.flush()
