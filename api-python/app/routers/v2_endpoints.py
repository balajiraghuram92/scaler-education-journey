"""Ported from api/Endpoints/V2Endpoints.cs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..models.course_module import CourseModule
from ..models.lesson import Lesson
from ..models.lesson_code_comparison import LessonCodeComparison
from ..models.lesson_concept_link import LessonConceptLink
from ..models.lesson_diagram import LessonDiagram
from ..models.lesson_note import LessonNote
from ..models.lesson_resource import LessonResource
from ..schemas.base import CamelModel, format_dotnet_datetime
from ..services.atlas_query_service import AtlasQueryService
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
    require_user,
)
from ..services.learner_progress_service import (
    LearnerProgressService,
    ProblemStatusRequest,
)
from ..services.learning_path_query_service import LearningPathQueryService
from ..services.mcq_service import McqAccessDeniedException, McqAttemptRequest, McqService
from ..services.progress_service import ProgressService
from ..services.reading_map_service import ReadingMapService

router = APIRouter(prefix="/api/v2", tags=["v2"])


class LessonProgressRequest(CamelModel):
    lesson_id: int = 0
    is_completed: bool = False
    correlation_id: UUID | None = None


class ProblemProgressRequest(CamelModel):
    problem_id: int = 0
    is_completed: bool = False
    correlation_id: UUID | None = None


class TaskProgressRequest(CamelModel):
    task_id: int = 0
    is_completed: bool = False
    correlation_id: UUID | None = None


def _resource_to_dict(resource: LessonResource) -> dict:
    return {
        "id": resource.id,
        "lessonId": resource.lesson_id,
        "resourceType": resource.resource_type,
        "title": resource.title,
        "contentBody": resource.content_body,
        "orderIndex": resource.order_index,
        "createdAt": format_dotnet_datetime(resource.created_at),
    }


def _code_comparison_to_dict(comparison: LessonCodeComparison) -> dict:
    return {
        "id": comparison.id,
        "lessonId": comparison.lesson_id,
        "title": comparison.title,
        "description": comparison.description,
        "beforeLabel": comparison.before_label,
        "beforeLanguage": comparison.before_language,
        "beforeCode": comparison.before_code,
        "afterLabel": comparison.after_label,
        "afterLanguage": comparison.after_language,
        "afterCode": comparison.after_code,
        "explanation": comparison.explanation,
        "orderIndex": comparison.order_index,
        "createdAt": format_dotnet_datetime(comparison.created_at),
    }


def _diagram_to_dict(diagram: LessonDiagram) -> dict:
    return {
        "id": diagram.id,
        "lessonId": diagram.lesson_id,
        "title": diagram.title,
        "caption": diagram.caption,
        "diagramType": diagram.diagram_type,
        "svgContent": diagram.svg_content,
        "diagramSpecJson": diagram.diagram_spec_json,
        "orderIndex": diagram.order_index,
        "createdAt": format_dotnet_datetime(diagram.created_at),
    }


def _note_to_dict(note: LessonNote) -> dict:
    return {
        "id": note.id,
        "lessonId": note.lesson_id,
        "userId": note.user_id,
        "noteType": note.note_type,
        "anchorSection": note.anchor_section,
        "title": note.title,
        "contentBody": note.content_body,
        "orderIndex": note.order_index,
        "createdAt": format_dotnet_datetime(note.created_at),
        "updatedAt": format_dotnet_datetime(note.updated_at),
    }


@router.get("/learning-paths")
async def get_learning_paths(
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    service = LearningPathQueryService(session, LearnerProgressService(session))
    return await service.get_all_learning_paths(current.user_id)


@router.get("/learning-paths/{slug}")
async def get_learning_path_by_slug(
    slug: str,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    service = LearningPathQueryService(session, LearnerProgressService(session))
    path = await service.get_learning_path_by_slug(slug, current.user_id)
    if path is None:
        return JSONResponse(
            status_code=404, content={"error": f"Learning path '{slug}' not found."}
        )
    return path


@router.get("/knowledge-atlas")
async def get_knowledge_atlas(session: AsyncSession = Depends(get_session)):
    return await AtlasQueryService(session).get_knowledge_atlas()


@router.get("/reading-map")
async def get_reading_map(session: AsyncSession = Depends(get_session)):
    return await ReadingMapService(session).get_reading_map()


@router.get("/chapters/{course_slug}/{module_slug}/{lesson_slug}")
async def get_chapter_detail(
    course_slug: str,
    module_slug: str,
    lesson_slug: str,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    from ..services.exercises.exercise_repository import get_exercise_repository

    user_id = current.user_id
    lessons = (
        await session.execute(
            select(Lesson)
            .options(
                selectinload(Lesson.module).selectinload(CourseModule.course),
                selectinload(Lesson.problems),
                selectinload(Lesson.resources),
                selectinload(Lesson.code_comparisons),
                selectinload(Lesson.diagrams),
                selectinload(Lesson.notes),
                selectinload(Lesson.concept_links).selectinload(
                    LessonConceptLink.concept
                ),
                selectinload(Lesson.outgoing_relations),
            )
            .where(Lesson.slug == lesson_slug)
        )
    ).scalars().all()
    lesson = next(
        (
            candidate
            for candidate in lessons
            if candidate.module is not None
            and candidate.module.slug == module_slug
            and candidate.module.course is not None
            and candidate.module.course.slug == course_slug
        ),
        None,
    )
    if lesson is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Chapter '{course_slug}/{module_slug}/{lesson_slug}' not found."},
        )
    assert lesson.module is not None and lesson.module.course is not None

    # Filtered include: ownerless notes plus the caller's own (anonymous callers
    # see ownerless notes only, since `userId == null` never matches in SQL).
    included_notes = [
        n
        for n in lesson.notes
        if n.user_id is None or (user_id is not None and n.user_id == user_id)
    ]
    # Personal notes written before notes became per-user have no owner; only
    # editorial note types are shared, so hide ownerless personal ones.
    notes = sorted(
        (
            n
            for n in included_notes
            if n.user_id is not None or n.note_type != "PersonalNote"
        ),
        key=lambda n: n.order_index,
    )

    # Course-wide reading order for previous/next and the in-module sibling list.
    course_lessons = (
        await session.execute(
            select(
                Lesson.id,
                Lesson.slug,
                Lesson.title,
                Lesson.estimated_minutes,
                Lesson.module_id,
                CourseModule.slug,
                CourseModule.title,
            )
            .join(CourseModule, Lesson.module_id == CourseModule.id)
            .where(CourseModule.course_id == lesson.module.course.id)
            .order_by(CourseModule.order_index, Lesson.order_index)
        )
    ).all()

    progress = LearnerProgressService(session)
    progress_map = await progress.get_lesson_progress_map(
        user_id, [row[0] for row in course_lessons]
    )
    problem_progress = await progress.get_problem_progress_map(
        user_id, [p.id for p in lesson.problems]
    )

    def to_nav(row) -> dict:  # type: ignore[no-untyped-def]
        entry = progress_map.get(row[0])
        return {
            "id": row[0],
            "slug": row[1],
            "fullSlug": f"{course_slug}/{row[5]}/{row[1]}",
            "title": row[2],
            "moduleTitle": row[6],
            "readingTimeMinutes": row[3],
            "isCompleted": entry is not None and entry.is_completed,
        }

    index = next((i for i, row in enumerate(course_lessons) if row[0] == lesson.id), -1)
    previous = to_nav(course_lessons[index - 1]) if index > 0 else None
    next_lesson = (
        to_nav(course_lessons[index + 1])
        if 0 <= index < len(course_lessons) - 1
        else None
    )
    siblings = [to_nav(row) for row in course_lessons if row[4] == lesson.module_id]
    my_progress = progress_map.get(lesson.id)

    repository = get_exercise_repository()
    problems = sorted(lesson.problems, key=lambda p: p.order_index)
    return {
        "id": lesson.id,
        "slug": lesson.slug,
        "fullSlug": f"{course_slug}/{module_slug}/{lesson.slug}",
        "title": lesson.title,
        "description": lesson.description,
        "lectureNumber": lesson.lecture_number,
        "classDate": lesson.class_date,
        "contentBody": lesson.content_body,
        "horstmannRef": lesson.horstmann_ref,
        "estimatedMinutes": lesson.estimated_minutes,
        "isCompleted": my_progress.is_completed if my_progress is not None else False,
        "difficulty": lesson.difficulty,
        "contentStatus": lesson.content_status,
        "userProgress": my_progress.model_dump(by_alias=True, mode="json")
        if my_progress is not None
        else None,
        "course": {
            "id": lesson.module.course.id,
            "slug": lesson.module.course.slug,
            "title": lesson.module.course.title,
        },
        "module": {
            "id": lesson.module.id,
            "slug": lesson.module.slug,
            "title": lesson.module.title,
            "badge": lesson.module.badge,
        },
        "problems": [
            {
                "id": p.id,
                "lessonId": p.lesson_id,
                "slug": p.slug,
                "title": p.title,
                "difficulty": p.difficulty,
                "packageName": p.package_name,
                "testClassName": p.test_class_name,
                "problemStatement": p.problem_statement,
                "requirementsBody": p.requirements_body,
                "workedExample": p.worked_example,
                "hints": p.hints,
                "language": p.language,
                "runCommand": p.run_command,
                "referenceSolution": p.reference_solution,
                "sourceType": p.source_type,
                "orderIndex": p.order_index,
                # Live in-browser exercise (hidden tests) when one exists for this assignment.
                "exerciseId": None if repository.get_by_id(p.slug) is None else p.slug,
                "isCompleted": problem_progress.get(p.id) is not None
                and problem_progress[p.id].status == "Solved",
                "userStatus": problem_progress[p.id].model_dump(by_alias=True, mode="json")
                if p.id in problem_progress
                else None,
            }
            for p in problems
        ],
        "resources": [_resource_to_dict(r) for r in lesson.resources],
        "codeComparisons": [_code_comparison_to_dict(c) for c in lesson.code_comparisons],
        "diagrams": [_diagram_to_dict(d) for d in lesson.diagrams],
        "notes": [_note_to_dict(n) for n in notes],
        "concepts": [
            {
                "id": cl.concept.id if cl.concept is not None else None,
                "slug": cl.concept.slug if cl.concept is not None else None,
                "title": cl.concept.title if cl.concept is not None else None,
            }
            for cl in lesson.concept_links
        ],
        "relatedLessons": [
            {
                "targetTitle": r.target_title,
                "targetSlug": r.target_slug,
                "relationshipType": r.relationship_type,
                "resolutionStatus": r.resolution_status,
            }
            for r in lesson.outgoing_relations
        ],
        "previousChapter": previous,
        "nextChapter": next_lesson,
        "siblingChapters": siblings,
    }


@router.post("/progress/lesson", dependencies=[Depends(require_user)])
async def set_lesson_progress(
    body: LessonProgressRequest,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    result = await LearnerProgressService(session).set_lesson_completion(
        current.user_id, body.lesson_id, body.is_completed
    )
    await session.commit()
    if result is None:
        return JSONResponse(
            status_code=404, content={"error": f"Lesson {body.lesson_id} not found."}
        )
    return result


@router.post("/progress/problem", dependencies=[Depends(require_user)])
async def set_problem_progress(
    body: ProblemProgressRequest,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    assert current.user_id is not None
    result = await LearnerProgressService(session).set_problem_status(
        current.user_id,
        body.problem_id,
        ProblemStatusRequest(
            status="Solved" if body.is_completed else "Attempted",
            solution_revealed=None,
        ),
    )
    await session.commit()
    if result is None:
        return JSONResponse(
            status_code=404, content={"error": f"Problem {body.problem_id} not found."}
        )
    return result


@router.post("/progress/task", dependencies=[Depends(require_user)])
async def set_task_progress(
    body: TaskProgressRequest, session: AsyncSession = Depends(get_session)
):
    result = await ProgressService(session).set_task_completion(
        body.task_id, body.is_completed, body.correlation_id
    )
    await session.commit()
    if result.success:
        return result
    return JSONResponse(status_code=400, content=result.model_dump(by_alias=True, mode="json"))


@router.get("/practice-questions/{course_slug}/{module_slug}/{lesson_slug}")
async def get_practice_questions(
    course_slug: str,
    module_slug: str,
    lesson_slug: str,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    questions = await McqService(session).get_practice_questions(
        course_slug, module_slug, lesson_slug, current.user_id
    )
    await session.commit()
    return questions


@router.post("/practice-questions/{presentation_id}/attempts")
async def record_practice_attempt(
    presentation_id: UUID,
    body: McqAttemptRequest | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    if body is None or not body.selected_option_key or not body.selected_option_key.strip():
        return JSONResponse(
            status_code=400, content={"error": "selectedOptionKey is required."}
        )
    try:
        result = await McqService(session).record_attempt(
            presentation_id, body.selected_option_key, current.user_id
        )
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except McqAccessDeniedException as exc:
        return JSONResponse(status_code=403, content={"error": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    await session.commit()
    return result


@router.post("/practice-questions/{presentation_id}/retry")
async def retry_practice_question(
    presentation_id: UUID,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await McqService(session).retry(presentation_id, current.user_id)
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except McqAccessDeniedException as exc:
        return JSONResponse(status_code=403, content={"error": str(exc)})
    await session.commit()
    return result
