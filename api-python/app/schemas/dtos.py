"""Ported from api/Models/DTOs.cs.

Classes are ordered so forward references resolve (Pydantic builds schemas
at class-definition time); the C# file lists them in a different order.

Request models mirror C# binding semantics: ASP.NET does not validate
[Required] on minimal-API bodies, so a missing reference-type property binds
as null and the handler decides. Hence request fields default to None (value
types to their C# defaults) and handlers keep the C# outcome.
"""

from __future__ import annotations

from pydantic import Field

from .base import CamelModel, DotNetDateTime


class LessonSummaryDto(CamelModel):
    id: int
    module_id: int
    slug: str
    title: str
    description: str
    lecture_number: int
    class_date: str
    horstmann_ref: str
    estimated_minutes: int
    is_completed: bool
    order_index: int
    problem_count: int


class ModuleSummaryDto(CamelModel):
    id: int
    course_id: int
    slug: str
    title: str
    description: str
    badge: str
    order_index: int
    total_lessons: int
    completed_lessons: int
    progress_percent: int
    lessons: list[LessonSummaryDto]


class CourseSummaryDto(CamelModel):
    id: int
    slug: str
    title: str
    description: str
    order_index: int
    vertical_id: int | None
    total_lessons: int
    completed_lessons: int
    total_problems: int
    completed_problems: int
    progress_percent: int
    modules: list[ModuleSummaryDto]


class ProblemSummaryDto(CamelModel):
    id: int
    lesson_id: int
    slug: str
    title: str
    difficulty: str
    package_name: str
    test_class_name: str
    problem_statement: str
    requirements_body: str
    worked_example: str
    hints: str
    is_completed: bool
    order_index: int


class LessonResourceDto(CamelModel):
    id: int
    lesson_id: int
    resource_type: str
    title: str
    content_body: str
    order_index: int


class LessonDetailDto(CamelModel):
    id: int
    module_id: int
    module_title: str
    course_id: int
    course_title: str
    slug: str
    title: str
    description: str
    lecture_number: int
    class_date: str
    content_body: str
    horstmann_ref: str
    estimated_minutes: int
    is_completed: bool
    order_index: int
    problems: list[ProblemSummaryDto]
    resources: list[LessonResourceDto]


class CreateLessonRequest(CamelModel):
    module_id: int = 0
    slug: str | None = None
    title: str | None = None
    description: str | None = None
    lecture_number: int = 0
    class_date: str | None = None
    content_body: str | None = None
    horstmann_ref: str | None = None
    estimated_minutes: int | None = None
    order_index: int | None = None


class UpdateLessonRequest(CamelModel):
    title: str | None = None
    description: str | None = None
    content_body: str | None = None
    horstmann_ref: str | None = None
    estimated_minutes: int | None = None
    is_completed: bool | None = None


class CreateProblemRequest(CamelModel):
    lesson_id: int = 0
    slug: str | None = None
    title: str | None = None
    difficulty: str | None = None
    package_name: str | None = None
    test_class_name: str | None = None
    problem_statement: str | None = None
    requirements_body: str | None = None
    worked_example: str | None = None
    hints: str | None = None
    order_index: int | None = None


class UpdateProblemProgressRequest(CamelModel):
    is_completed: bool = False


class ToggleProgressResponse(CamelModel):
    id: int
    is_completed: bool
    message: str


class DomainSummaryDto(CamelModel):
    id: int
    slug: str
    name: str
    code: str
    description: str
    icon: str
    color_hex: str
    order_index: int


class ConceptPrerequisiteItemDto(CamelModel):
    name: str
    status: str


class KnowledgeConnectionDto(CamelModel):
    from_: str = Field(alias="from")
    to: str
    relevance_weight: int
    is_primary: bool


class ConceptSummaryDto(CamelModel):
    id: int
    slug: str
    title: str
    sub_label: str
    summary: str
    description: str
    difficulty: str
    icon: str
    estimated_hours: int
    order_index: int
    connected_domains: list[str]
    prerequisites: list[ConceptPrerequisiteItemDto]
    related_lessons: list[str]
    next_lessons: list[str]


class KnowledgeAtlasDto(CamelModel):
    domains: list[DomainSummaryDto]
    concepts: list[ConceptSummaryDto]
    connections: list[KnowledgeConnectionDto]


class ReadingMapItemDto(CamelModel):
    id: int
    category: str
    title: str
    sub_text: str | None
    is_completed: bool
    order_index: int


class DailyActivityDto(CamelModel):
    id: int
    day_label: str
    activity_count: int
    order_index: int


class KnowledgeThreadDto(CamelModel):
    id: int
    domain: str
    raw_path: str
    nodes: list[str]
    order_index: int


class ReadingMapDto(CamelModel):
    read_this_week: list[ReadingMapItemDto]
    revisited: list[ReadingMapItemDto]
    deferred: list[ReadingMapItemDto]
    lists: list[ReadingMapItemDto]
    prerequisites: list[ReadingMapItemDto]
    activity_timeline: list[DailyActivityDto]
    knowledge_threads: list[KnowledgeThreadDto]


class CreateReadingItemRequest(CamelModel):
    category: str | None = None
    title: str | None = None
    sub_text: str | None = None
    order_index: int | None = None


class ChapterCourseInfoDto(CamelModel):
    id: int
    slug: str
    title: str
    vertical_id: int | None
    vertical_name: str | None


class ChapterModuleInfoDto(CamelModel):
    id: int
    slug: str
    title: str
    description: str
    badge: str
    order_index: int


class CodeComparisonDto(CamelModel):
    id: int
    title: str
    description: str
    before_label: str
    before_language: str
    before_code: str
    after_label: str
    after_language: str
    after_code: str
    explanation: str
    order_index: int


class ChapterDiagramDto(CamelModel):
    id: int
    title: str
    caption: str
    diagram_type: str
    svg_content: str
    diagram_spec_json: str | None
    order_index: int


class ChapterNoteDto(CamelModel):
    id: int
    note_type: str
    anchor_section: str | None
    title: str
    content_body: str
    order_index: int
    updated_at: DotNetDateTime


class ConnectedConceptDto(CamelModel):
    id: int
    slug: str
    title: str
    summary: str
    difficulty: str
    icon: str
    connected_domains: list[str]


class ChapterConceptConnectionsDto(CamelModel):
    direct_concepts: list[ConnectedConceptDto]
    prerequisites: list[ConceptPrerequisiteItemDto]
    next_recommended_topics: list[str]
    interchange_domains: list[str]


class ChapterNavDto(CamelModel):
    id: int
    slug: str
    full_slug: str
    title: str
    module_title: str
    reading_time_minutes: int
    is_completed: bool


class ChapterDetailDto(CamelModel):
    id: int
    slug: str
    full_slug: str
    title: str
    description: str
    lecture_number: int
    class_date: str
    reading_time_minutes: int
    word_count: int
    difficulty: str
    is_completed: bool
    order_index: int
    content_body: str
    horstmann_ref: str
    course: ChapterCourseInfoDto
    module: ChapterModuleInfoDto
    code_comparisons: list[CodeComparisonDto]
    diagrams: list[ChapterDiagramDto]
    notes: list[ChapterNoteDto]
    concept_connections: ChapterConceptConnectionsDto
    problems: list[ProblemSummaryDto]
    resources: list[LessonResourceDto]
    previous_chapter: ChapterNavDto | None
    next_chapter: ChapterNavDto | None
    sibling_chapters: list[ChapterNavDto]


class ChapterSummaryDto(CamelModel):
    id: int
    slug: str
    full_slug: str
    title: str
    description: str
    lecture_number: int
    reading_time_minutes: int
    word_count: int
    difficulty: str
    is_completed: bool
    order_index: int
    course_slug: str
    course_title: str
    vertical_slug: str | None
    module_slug: str
    module_title: str
    module_badge: str
    problem_count: int
    resource_count: int
    has_code_comparisons: bool
    has_diagrams: bool
    notes_count: int


class ModuleWithChaptersDto(CamelModel):
    id: int
    slug: str
    title: str
    description: str
    badge: str
    order_index: int
    total_chapters: int
    completed_chapters: int
    total_reading_time_minutes: int
    chapters: list[ChapterSummaryDto]


class CourseWithChaptersDto(CamelModel):
    id: int
    slug: str
    title: str
    description: str
    vertical_id: int | None
    vertical_name: str | None
    total_chapters: int
    completed_chapters: int
    total_reading_time_minutes: int
    modules: list[ModuleWithChaptersDto]


class ChapterHierarchyDto(CamelModel):
    total_chapters: int
    completed_chapters: int
    total_reading_time_minutes: int
    total_words: int
    courses: list[CourseWithChaptersDto]


class CreateChapterNoteRequest(CamelModel):
    note_type: str | None = None
    anchor_section: str | None = None
    title: str | None = None
    content_body: str | None = None
    order_index: int | None = None


class MapChapterRequest(CamelModel):
    domain: str | None = None
    module_name: str | None = None
    title: str | None = None
    slug: str | None = None
    description: str | None = None
    markdown_content: str | None = None
    prerequisites: list[str] | None = None
    related_concepts: list[str] | None = None
    next_lessons: list[str] | None = None
    difficulty: str | None = None
    estimated_minutes: int | None = None
