"""Ported from api/Program.cs inline routes for /api/chapters (lines 1326-1631)
plus the BuildChapterDetailResponse helper (lines 1650-1883) and CountWords.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..models.concept_next_lesson import ConceptNextLesson
from ..models.concept_prerequisite import ConceptPrerequisite
from ..models.course import Course
from ..models.course_module import CourseModule
from ..models.domain_concept_connection import DomainConceptConnection
from ..models.knowledge_concept import KnowledgeConcept
from ..models.lesson import Lesson
from ..models.lesson_note import LessonNote
from ..models.study_vertical import StudyVertical
from ..schemas.dtos import (
    ChapterConceptConnectionsDto,
    ChapterCourseInfoDto,
    ChapterDetailDto,
    ChapterDiagramDto,
    ChapterHierarchyDto,
    ChapterModuleInfoDto,
    ChapterNavDto,
    ChapterNoteDto,
    ChapterSummaryDto,
    CodeComparisonDto,
    ConceptPrerequisiteItemDto,
    ConnectedConceptDto,
    CourseWithChaptersDto,
    CreateChapterNoteRequest,
    LessonResourceDto,
    MapChapterRequest,
    ModuleWithChaptersDto,
    ProblemSummaryDto,
)
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
)
from ..services.learner_progress_service import LearnerProgressService

router = APIRouter(tags=["chapters"])


def count_words(text: str | None) -> int:
    """Ported from the CountWords helper in Program.cs (line 1886)."""
    if not text or not text.strip():
        return 0
    return len([w for w in re.split(r"[ \r\n\t]+", text) if w])


@router.get("/api/chapters")  # Program.cs line 1326
async def get_chapters_list(
    vertical: str | None = None,
    course: str | None = None,
    module: str | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    progress = LearnerProgressService(session)
    completed_ids = await progress.get_completed_lesson_ids(current.user_id)
    stmt = (
        select(Course)
        .options(
            selectinload(Course.vertical),
            selectinload(Course.modules)
            .selectinload(CourseModule.lessons)
            .selectinload(Lesson.problems),
            selectinload(Course.modules)
            .selectinload(CourseModule.lessons)
            .selectinload(Lesson.resources),
            selectinload(Course.modules)
            .selectinload(CourseModule.lessons)
            .selectinload(Lesson.code_comparisons),
            selectinload(Course.modules)
            .selectinload(CourseModule.lessons)
            .selectinload(Lesson.diagrams),
            selectinload(Course.modules)
            .selectinload(CourseModule.lessons)
            .selectinload(Lesson.notes),
        )
        .order_by(Course.order_index)
    )
    if course and course.strip():
        stmt = stmt.where(Course.slug == course)
    if vertical and vertical.strip():
        stmt = (
            stmt.join(StudyVertical, Course.vertical_id == StudyVertical.id)
            .where(func.lower(StudyVertical.name).contains(vertical.lower()))
        )
    course_entities = (await session.execute(stmt)).scalars().all()

    all_lessons = [
        lesson for c in course_entities for m in c.modules for lesson in m.lessons
    ]
    total_chapters = len(all_lessons)
    completed_chapters = sum(1 for lesson in all_lessons if lesson.id in completed_ids)
    total_reading_time = sum(
        lesson.estimated_minutes if lesson.estimated_minutes > 0 else 15
        for lesson in all_lessons
    )
    total_words = sum(count_words(lesson.content_body) for lesson in all_lessons)

    course_dtos = []
    for c in course_entities:
        modules = sorted(c.modules, key=lambda m: m.order_index)
        if module and module.strip():
            modules = [m for m in modules if m.slug == module]
        module_dtos = []
        for m in modules:
            lessons = sorted(m.lessons, key=lambda l: l.order_index)
            m_chapters = [
                ChapterSummaryDto(
                    id=lesson.id,
                    slug=lesson.slug,
                    full_slug=f"{c.slug}/{m.slug}/{lesson.slug}",
                    title=lesson.title,
                    description=lesson.description,
                    lecture_number=lesson.lecture_number,
                    reading_time_minutes=lesson.estimated_minutes,
                    word_count=count_words(lesson.content_body),
                    difficulty=lesson.difficulty
                    if lesson.difficulty is not None
                    else "Intermediate",
                    is_completed=lesson.id in completed_ids,
                    order_index=lesson.order_index,
                    course_slug=c.slug,
                    course_title=c.title,
                    vertical_slug=c.vertical.name if c.vertical is not None else None,
                    module_slug=m.slug,
                    module_title=m.title,
                    module_badge=m.badge,
                    problem_count=len(lesson.problems),
                    resource_count=len(lesson.resources),
                    has_code_comparisons=len(lesson.code_comparisons) > 0,
                    has_diagrams=len(lesson.diagrams) > 0,
                    notes_count=len(lesson.notes),
                )
                for lesson in lessons
            ]
            module_dtos.append(
                ModuleWithChaptersDto(
                    id=m.id,
                    slug=m.slug,
                    title=m.title,
                    description=m.description,
                    badge=m.badge,
                    order_index=m.order_index,
                    total_chapters=len(m_chapters),
                    completed_chapters=sum(1 for x in m_chapters if x.is_completed),
                    total_reading_time_minutes=sum(
                        x.reading_time_minutes for x in m_chapters
                    ),
                    chapters=m_chapters,
                )
            )
        course_dtos.append(
            CourseWithChaptersDto(
                id=c.id,
                slug=c.slug,
                title=c.title,
                description=c.description,
                vertical_id=c.vertical_id,
                vertical_name=c.vertical.name if c.vertical is not None else None,
                total_chapters=sum(m.total_chapters for m in module_dtos),
                completed_chapters=sum(m.completed_chapters for m in module_dtos),
                total_reading_time_minutes=sum(
                    m.total_reading_time_minutes for m in module_dtos
                ),
                modules=module_dtos,
            )
        )
    return ChapterHierarchyDto(
        total_chapters=total_chapters,
        completed_chapters=completed_chapters,
        total_reading_time_minutes=total_reading_time,
        total_words=total_words,
        courses=course_dtos,
    )


@router.get("/api/chapters/{slug}")  # Program.cs line 1459
async def get_chapter_by_slug(
    slug: str,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    return await _build_chapter_detail_response(slug, None, None, session, current.user_id)


@router.get("/api/chapters/{vertical_or_course_slug}/{module_slug}/{lesson_slug}")  # Program.cs line 1466
async def get_chapter_by_path(
    vertical_or_course_slug: str,
    module_slug: str,
    lesson_slug: str,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    return await _build_chapter_detail_response(
        lesson_slug, module_slug, vertical_or_course_slug, session, current.user_id
    )


@router.post("/api/chapters/{lesson_id}/notes")  # Program.cs line 1479
async def create_chapter_note(
    lesson_id: int,
    body: CreateChapterNoteRequest,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    # Personal notes belong to the signed-in learner; editorial note types remain admin content.
    is_personal = (
        not body.note_type
        or not body.note_type.strip()
        or body.note_type.strip().lower() == "personalnote"
    )
    if current.user_id is None:
        return Response(status_code=401)
    lesson = await session.get(Lesson, lesson_id)
    if lesson is None:
        return JSONResponse(
            status_code=404, content={"message": "Chapter/Lesson not found."}
        )
    if not body.title or not body.title.strip() or not body.content_body or not body.content_body.strip():
        return JSONResponse(
            status_code=400, content={"message": "Title and ContentBody are required."}
        )
    max_order = (
        await session.execute(
            select(func.max(LessonNote.order_index)).where(
                LessonNote.lesson_id == lesson_id
            )
        )
    ).scalar_one()
    now = datetime.now(timezone.utc)
    note_type = (
        "PersonalNote"
        if is_personal
        else (body.note_type.strip() if body.note_type else "PersonalNote")
    )
    note = LessonNote(
        lesson_id=lesson_id,
        user_id=current.user_id if is_personal else None,
        note_type=note_type,
        anchor_section=body.anchor_section.strip() if body.anchor_section else None,
        title=body.title.strip(),
        content_body=body.content_body.strip(),
        order_index=body.order_index
        if body.order_index is not None
        else (max_order or 0) + 1,
        created_at=now,
        updated_at=now,
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return JSONResponse(
        status_code=201,
        headers={"Location": f"/api/chapters/{lesson_id}/notes/{note.id}"},
        content=ChapterNoteDto(
            id=note.id,
            note_type=note.note_type,
            anchor_section=note.anchor_section,
            title=note.title,
            content_body=note.content_body,
            order_index=note.order_index,
            updated_at=note.updated_at,
        ).model_dump(by_alias=True, mode="json"),
    )


@router.post("/api/chapters/map")  # Program.cs line 1530
async def map_curriculum_chapter(
    body: MapChapterRequest, session: AsyncSession = Depends(get_session)
):
    if not body.title or not body.title.strip() or not body.markdown_content or not body.markdown_content.strip():
        return JSONResponse(
            status_code=400, content={"message": "Title and MarkdownContent are required."}
        )
    domain_name = body.domain.strip() if body.domain and body.domain.strip() else "Backend"
    module_title = (
        body.module_name.strip()
        if body.module_name and body.module_name.strip()
        else "Backend Architecture"
    )
    lesson_title = body.title.strip()
    slug = (
        re.sub(r"[^a-z0-9]+", "-", lesson_title.lower()).strip("-")
        if not body.slug or not body.slug.strip()
        else body.slug.strip().lower()
    )

    # 1. Find or create Course / Domain Vertical
    courses = (
        await session.execute(
            select(Course).options(selectinload(Course.modules))
        )
    ).scalars().all()
    course = next(
        (
            c
            for c in courses
            if domain_name.lower() in c.title.lower() or c.slug == domain_name.lower()
        ),
        None,
    )
    if course is None:
        course = next((c for c in courses if c.slug == "java-spring-lld"), None) or next(
            iter(courses), None
        )
    if course is None:
        course = Course(
            slug="backend-systems",
            title=domain_name,
            description=f"{domain_name} curriculum and architectural patterns.",
            order_index=1,
            path_type="Course",
            is_published=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(course)
        await session.commit()
        await session.refresh(course)

    # 2. Find or create CourseModule
    module_slug = re.sub(r"[^a-z0-9]+", "-", module_title.lower()).strip("-")
    course_module = (
        await session.execute(
            select(CourseModule)
            .options(selectinload(CourseModule.lessons))
            .where(CourseModule.course_id == course.id)
        )
    ).scalars().all()
    module_row = next(
        (
            m
            for m in course_module
            if m.title.lower() == module_title.lower() or m.slug == module_slug
        ),
        None,
    )
    if module_row is None:
        max_module_order = (
            await session.execute(
                select(func.max(CourseModule.order_index)).where(
                    CourseModule.course_id == course.id
                )
            )
        ).scalar_one() or 0
        module_row = CourseModule(
            course_id=course.id,
            slug=module_slug,
            title=module_title,
            description=f"Module for {module_title}",
            badge="Module",
            order_index=max_module_order + 1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(module_row)
        await session.commit()
        await session.refresh(module_row)

    # 3. Find or create Lesson
    existing_lessons = (
        await session.execute(
            select(Lesson)
            .options(
                selectinload(Lesson.code_comparisons), selectinload(Lesson.resources)
            )
            .where(Lesson.module_id == module_row.id)
        )
    ).scalars().all()
    existing = next(
        (
            lesson
            for lesson in existing_lessons
            if lesson.slug == slug or lesson.title.lower() == lesson_title.lower()
        ),
        None,
    )
    if existing is not None:
        existing.title = lesson_title
        existing.description = body.description if body.description is not None else existing.description
        existing.content_body = body.markdown_content
        existing.difficulty = body.difficulty if body.difficulty is not None else "Intermediate"
        existing.estimated_minutes = (
            body.estimated_minutes if body.estimated_minutes is not None else 45
        )
        existing.updated_at = datetime.now(timezone.utc)
    else:
        max_lesson_order = (
            await session.execute(
                select(func.max(Lesson.order_index)).where(
                    Lesson.module_id == module_row.id
                )
            )
        ).scalar_one() or 0
        now = datetime.now(timezone.utc)
        existing = Lesson(
            module_id=module_row.id,
            slug=slug,
            title=lesson_title,
            description=body.description if body.description is not None else "",
            lecture_number=max_lesson_order + 1,
            class_date=now.strftime("%Y-%m-%d"),
            content_body=body.markdown_content,
            difficulty=body.difficulty if body.difficulty is not None else "Intermediate",
            estimated_minutes=body.estimated_minutes if body.estimated_minutes is not None else 45,
            order_index=max_lesson_order + 1,
            is_completed=False,
            created_at=now,
            updated_at=now,
        )
        session.add(existing)
    await session.commit()
    await session.refresh(existing)
    return JSONResponse(
        status_code=201,
        headers={"Location": f"/api/chapters/{slug}"},
        content={
            "id": existing.id,
            "slug": existing.slug,
            "title": existing.title,
            "domain": domain_name,
            "module": module_title,
            "message": "Chapter mapped and stored successfully.",
        },
    )


async def _build_chapter_detail_response(
    lesson_slug: str,
    module_slug: str | None,
    course_or_vertical_slug: str | None,
    session: AsyncSession,
    user_id: int | None,
):
    progress = LearnerProgressService(session)
    completed_ids = await progress.get_completed_lesson_ids(user_id)
    solved_ids = await progress.get_solved_problem_ids(user_id)

    def _options() -> list:
        return [
            selectinload(Lesson.module)
            .selectinload(CourseModule.course)
            .selectinload(Course.vertical),
            selectinload(Lesson.problems),
            selectinload(Lesson.resources),
            selectinload(Lesson.code_comparisons),
            selectinload(Lesson.diagrams),
            selectinload(Lesson.notes),
        ]

    stmt = select(Lesson).options(*_options())
    if module_slug and module_slug.strip() and course_or_vertical_slug and course_or_vertical_slug.strip():
        stmt = (
            stmt.join(CourseModule, Lesson.module_id == CourseModule.id)
            .join(Course, CourseModule.course_id == Course.id)
            .outerjoin(StudyVertical, Course.vertical_id == StudyVertical.id)
            .where(
                Lesson.slug == lesson_slug,
                CourseModule.slug == module_slug,
                (Course.slug == course_or_vertical_slug)
                | (
                    func.lower(StudyVertical.name) == course_or_vertical_slug.lower()
                ),
            )
        )
    else:
        stmt = stmt.where(Lesson.slug == lesson_slug)
    lesson = (await session.execute(stmt)).scalar_one_or_none()

    if lesson is None:
        # Try fallback search if user provided compound full slug like "oop-foundations/03-oop-2-access-modifiers-encapsulation"
        if "/" in lesson_slug:
            actual_slug = lesson_slug.split("/")[-1]
            lesson = (
                await session.execute(
                    select(Lesson)
                    .options(*_options())
                    .where(Lesson.slug == actual_slug)
                )
            ).scalar_one_or_none()
        if lesson is None:
            return JSONResponse(
                status_code=404, content={"message": f"Chapter '{lesson_slug}' not found."}
            )

    module = lesson.module
    course = module.course if module is not None else None
    course_slug = course.slug if course is not None else "curriculum"
    current_module_slug = module.slug if module is not None else "general"
    full_slug = f"{course_slug}/{current_module_slug}/{lesson.slug}"

    # Fetch sibling chapters in the same module
    sibling_rows = (
        await session.execute(
            select(
                Lesson.id,
                Lesson.slug,
                Lesson.title,
                Lesson.estimated_minutes,
                Lesson.order_index,
            )
            .where(Lesson.module_id == lesson.module_id)
            .order_by(Lesson.order_index)
        )
    ).all()
    sibling_dtos = [
        ChapterNavDto(
            id=row[0],
            slug=row[1],
            full_slug=f"{course_slug}/{current_module_slug}/{row[1]}",
            title=row[2],
            module_title=module.title if module is not None else "",
            reading_time_minutes=row[3],
            is_completed=row[0] in completed_ids,
        )
        for row in sibling_rows
    ]
    current_index = next(
        (i for i, row in enumerate(sibling_rows) if row[0] == lesson.id), -1
    )
    prev_chapter = sibling_dtos[current_index - 1] if current_index > 0 else None
    next_chapter = (
        sibling_dtos[current_index + 1]
        if 0 <= current_index < len(sibling_dtos) - 1
        else None
    )

    # Fetch Linked Knowledge Concepts (Synaptic mesh)
    linked_concept_ids = (
        await session.execute(
            select(ConceptNextLesson.concept_id).where(
                (ConceptNextLesson.lesson_id == lesson.id)
                | (ConceptNextLesson.lesson_slug == lesson.slug)
            )
        )
    ).scalars().all()
    linked_concepts = (
        await session.execute(
            select(KnowledgeConcept)
            .options(
                selectinload(KnowledgeConcept.domain_connections).selectinload(
                    DomainConceptConnection.domain
                ),
                selectinload(KnowledgeConcept.prerequisites).selectinload(
                    ConceptPrerequisite.prerequisite_concept
                ),
            )
        )
    ).scalars().all()
    linked_concepts = [
        c
        for c in linked_concepts
        if c.id in set(linked_concept_ids)
        or c.slug.lower() == lesson.slug.lower()
        or c.title.lower() in lesson.title.lower()
    ]
    direct_concept_dtos = [
        ConnectedConceptDto(
            id=c.id,
            slug=c.slug,
            title=c.title,
            summary=c.summary,
            difficulty=c.difficulty,
            icon=c.icon,
            connected_domains=[
                dc.domain.name
                for dc in c.domain_connections
                if dc.domain is not None and dc.domain.name
            ],
        )
        for c in linked_concepts
    ]
    seen_prereq: set[str] = set()
    prerequisites: list[ConceptPrerequisiteItemDto] = []
    for c in linked_concepts:
        for p in c.prerequisites:
            name = p.prerequisite_concept.title if p.prerequisite_concept is not None else "Prerequisite Topic"
            if name not in seen_prereq:
                seen_prereq.add(name)
                prerequisites.append(
                    ConceptPrerequisiteItemDto(name=name, status=p.status)
                )
    next_topics = [
        row[0]
        for row in (
            await session.execute(
                select(ConceptNextLesson.lesson_title)
                .where(
                    ConceptNextLesson.concept_id.in_(list(linked_concept_ids)),
                    ConceptNextLesson.lesson_slug != lesson.slug,
                )
                .distinct()
            )
        ).all()
    ]
    interchange_domains = list(
        dict.fromkeys(
            dc.domain.name
            for c in linked_concepts
            for dc in c.domain_connections
            if dc.domain is not None and dc.domain.name
        )
    )
    concept_connections = ChapterConceptConnectionsDto(
        direct_concepts=direct_concept_dtos,
        prerequisites=prerequisites,
        next_recommended_topics=next_topics,
        interchange_domains=interchange_domains,
    )

    notes = [
        ChapterNoteDto(
            id=n.id,
            note_type=n.note_type,
            anchor_section=n.anchor_section,
            title=n.title,
            content_body=n.content_body,
            order_index=n.order_index,
            updated_at=n.updated_at,
        )
        for n in sorted(lesson.notes, key=lambda x: x.order_index)
        if (n.user_id is not None and n.user_id == user_id)
        or (n.user_id is None and n.note_type != "PersonalNote")
    ]
    if lesson.horstmann_ref and lesson.horstmann_ref.strip() and not any(
        n.note_type == "HorstmannRef" for n in notes
    ):
        notes.append(
            ChapterNoteDto(
                id=0,
                note_type="HorstmannRef",
                anchor_section="Core Reading",
                title="Horstmann Core Java Reference",
                content_body=lesson.horstmann_ref,
                order_index=0,
                updated_at=lesson.updated_at,
            )
        )
    )
    return ChapterDetailDto(
        id=lesson.id,
        slug=lesson.slug,
        full_slug=full_slug,
        title=lesson.title,
        description=lesson.description,
        lecture_number=lesson.lecture_number,
        class_date=lesson.class_date,
        reading_time_minutes=lesson.estimated_minutes if lesson.estimated_minutes > 0 else 45,
        word_count=count_words(lesson.content_body),
        difficulty=lesson.difficulty if lesson.difficulty is not None else "Intermediate",
        is_completed=lesson.id in completed_ids,
        order_index=lesson.order_index,
        content_body=lesson.content_body,
        horstmann_ref=lesson.horstmann_ref,
        course=ChapterCourseInfoDto(
            id=course.id if course is not None else 0,
            slug=course_slug,
            title=course.title if course is not None else "Course",
            vertical_id=course.vertical_id if course is not None else None,
            vertical_name=course.vertical.name
            if course is not None and course.vertical is not None
            else None,
        ),
        module=ChapterModuleInfoDto(
            id=module.id if module is not None else 0,
            slug=current_module_slug,
            title=module.title if module is not None else "Module",
            description=module.description if module is not None else "",
            badge=module.badge if module is not None else "Module",
            order_index=module.order_index if module is not None else 0,
        ),
        code_comparisons=[
            CodeComparisonDto(
                id=c.id,
                title=c.title,
                description=c.description,
                before_label=c.before_label,
                before_language=c.before_language,
                before_code=c.before_code,
                after_label=c.after_label,
                after_language=c.after_language,
                after_code=c.after_code,
                explanation=c.explanation,
                order_index=c.order_index,
            )
            for c in sorted(lesson.code_comparisons, key=lambda x: x.order_index)
        ],
        diagrams=[
            ChapterDiagramDto(
                id=d.id,
                title=d.title,
                caption=d.caption,
                diagram_type=d.diagram_type,
                svg_content=d.svg_content,
                diagram_spec_json=d.diagram_spec_json,
                order_index=d.order_index,
            )
            for d in sorted(lesson.diagrams, key=lambda x: x.order_index)
        ],
        notes=notes,
        concept_connections=concept_connections,
        problems=[
            ProblemSummaryDto(
                id=p.id,
                lesson_id=p.lesson_id,
                slug=p.slug,
                title=p.title,
                difficulty=p.difficulty,
                package_name=p.package_name,
                test_class_name=p.test_class_name,
                problem_statement=p.problem_statement,
                requirements_body=p.requirements_body,
                worked_example=p.worked_example,
                hints=p.hints,
                is_completed=p.id in solved_ids,
                order_index=p.order_index,
            )
            for p in sorted(lesson.problems, key=lambda x: x.order_index)
        ],
        resources=[
            LessonResourceDto(
                id=r.id,
                lesson_id=r.lesson_id,
                resource_type=r.resource_type,
                title=r.title,
                content_body=r.content_body,
                order_index=r.order_index,
            )
            for r in sorted(lesson.resources, key=lambda x: x.order_index)
        ],
        previous_chapter=prev_chapter,
        next_chapter=next_chapter,
        sibling_chapters=sibling_dtos,
    )
