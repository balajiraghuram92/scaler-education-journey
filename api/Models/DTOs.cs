using System;
using System.Collections.Generic;

namespace StudyTracker.Api.Models;

public record CourseSummaryDto(
    int Id,
    string Slug,
    string Title,
    string Description,
    int OrderIndex,
    int? VerticalId,
    int TotalLessons,
    int CompletedLessons,
    int TotalProblems,
    int CompletedProblems,
    int ProgressPercent,
    List<ModuleSummaryDto> Modules
);

public record ModuleSummaryDto(
    int Id,
    int CourseId,
    string Slug,
    string Title,
    string Description,
    string Badge,
    int OrderIndex,
    int TotalLessons,
    int CompletedLessons,
    int ProgressPercent,
    List<LessonSummaryDto> Lessons
);

public record LessonSummaryDto(
    int Id,
    int ModuleId,
    string Slug,
    string Title,
    string Description,
    int LectureNumber,
    string ClassDate,
    string HorstmannRef,
    int EstimatedMinutes,
    bool IsCompleted,
    int OrderIndex,
    int ProblemCount
);

public record LessonDetailDto(
    int Id,
    int ModuleId,
    string ModuleTitle,
    int CourseId,
    string CourseTitle,
    string Slug,
    string Title,
    string Description,
    int LectureNumber,
    string ClassDate,
    string ContentBody,
    string HorstmannRef,
    int EstimatedMinutes,
    bool IsCompleted,
    int OrderIndex,
    List<ProblemSummaryDto> Problems,
    List<LessonResourceDto> Resources
);

public record ProblemSummaryDto(
    int Id,
    int LessonId,
    string Slug,
    string Title,
    string Difficulty,
    string PackageName,
    string TestClassName,
    string ProblemStatement,
    string RequirementsBody,
    string WorkedExample,
    string Hints,
    bool IsCompleted,
    int OrderIndex
);

public record LessonResourceDto(
    int Id,
    int LessonId,
    string ResourceType,
    string Title,
    string ContentBody,
    int OrderIndex
);

public record CreateLessonRequest(
    int ModuleId,
    string Slug,
    string Title,
    string Description,
    int LectureNumber,
    string? ClassDate,
    string? ContentBody,
    string? HorstmannRef,
    int? EstimatedMinutes,
    int? OrderIndex
);

public record UpdateLessonRequest(
    string? Title,
    string? Description,
    string? ContentBody,
    string? HorstmannRef,
    int? EstimatedMinutes,
    bool? IsCompleted
);

public record CreateProblemRequest(
    int LessonId,
    string Slug,
    string Title,
    string Difficulty,
    string PackageName,
    string TestClassName,
    string ProblemStatement,
    string RequirementsBody,
    string? WorkedExample,
    string? Hints,
    int? OrderIndex
);

public record UpdateProblemProgressRequest(
    bool IsCompleted
);

public record ToggleProgressResponse(
    int Id,
    bool IsCompleted,
    string Message
);

// ==========================================
// KNOWLEDGE ATLAS DTOS
// ==========================================

public record KnowledgeAtlasDto(
    List<DomainSummaryDto> Domains,
    List<ConceptSummaryDto> Concepts,
    List<KnowledgeConnectionDto> Connections
);

public record DomainSummaryDto(
    int Id,
    string Slug,
    string Name,
    string Code,
    string Description,
    string Icon,
    string ColorHex,
    int OrderIndex
);

public record ConceptSummaryDto(
    int Id,
    string Slug,
    string Title,
    string SubLabel,
    string Summary,
    string Description,
    string Difficulty,
    string Icon,
    int EstimatedHours,
    int OrderIndex,
    List<string> ConnectedDomains,
    List<ConceptPrerequisiteItemDto> Prerequisites,
    List<string> RelatedLessons,
    List<string> NextLessons
);

public record ConceptPrerequisiteItemDto(
    string Name,
    string Status
);

public record KnowledgeConnectionDto(
    string From,
    string To,
    int RelevanceWeight,
    bool IsPrimary
);

// ==========================================
// READING MAP DTOS (Panel B: Progress / Reading Map)
// ==========================================

public record ReadingMapDto(
    List<ReadingMapItemDto> ReadThisWeek,
    List<ReadingMapItemDto> Revisited,
    List<ReadingMapItemDto> Deferred,
    List<ReadingMapItemDto> Lists,
    List<ReadingMapItemDto> Prerequisites,
    List<DailyActivityDto> ActivityTimeline,
    List<KnowledgeThreadDto> KnowledgeThreads
);

public record ReadingMapItemDto(
    int Id,
    string Category,
    string Title,
    string? SubText,
    bool IsCompleted,
    int OrderIndex
);

public record DailyActivityDto(
    int Id,
    string DayLabel,
    int ActivityCount,
    int OrderIndex
);

public record KnowledgeThreadDto(
    int Id,
    string Domain,
    string RawPath,
    List<string> Nodes,
    int OrderIndex
);

public record CreateReadingItemRequest(
    string Category,
    string Title,
    string? SubText,
    int? OrderIndex
);

// ==========================================
// CHAPTER & EDITORIAL READING DTOS (Panel D)
// ==========================================

public record ChapterDetailDto(
    int Id,
    string Slug,
    string FullSlug,
    string Title,
    string Description,
    int LectureNumber,
    string ClassDate,
    int ReadingTimeMinutes,
    int WordCount,
    string Difficulty,
    bool IsCompleted,
    int OrderIndex,
    string ContentBody,
    string HorstmannRef,
    ChapterCourseInfoDto Course,
    ChapterModuleInfoDto Module,
    List<CodeComparisonDto> CodeComparisons,
    List<ChapterDiagramDto> Diagrams,
    List<ChapterNoteDto> Notes,
    ChapterConceptConnectionsDto ConceptConnections,
    List<ProblemSummaryDto> Problems,
    List<LessonResourceDto> Resources,
    ChapterNavDto? PreviousChapter,
    ChapterNavDto? NextChapter,
    List<ChapterNavDto> SiblingChapters
);

public record ChapterSummaryDto(
    int Id,
    string Slug,
    string FullSlug,
    string Title,
    string Description,
    int LectureNumber,
    int ReadingTimeMinutes,
    int WordCount,
    string Difficulty,
    bool IsCompleted,
    int OrderIndex,
    string CourseSlug,
    string CourseTitle,
    string? VerticalSlug,
    string ModuleSlug,
    string ModuleTitle,
    string ModuleBadge,
    int ProblemCount,
    int ResourceCount,
    bool HasCodeComparisons,
    bool HasDiagrams,
    int NotesCount
);

public record ChapterHierarchyDto(
    int TotalChapters,
    int CompletedChapters,
    int TotalReadingTimeMinutes,
    int TotalWords,
    List<CourseWithChaptersDto> Courses
);

public record CourseWithChaptersDto(
    int Id,
    string Slug,
    string Title,
    string Description,
    int? VerticalId,
    string? VerticalName,
    int TotalChapters,
    int CompletedChapters,
    int TotalReadingTimeMinutes,
    List<ModuleWithChaptersDto> Modules
);

public record ModuleWithChaptersDto(
    int Id,
    string Slug,
    string Title,
    string Description,
    string Badge,
    int OrderIndex,
    int TotalChapters,
    int CompletedChapters,
    int TotalReadingTimeMinutes,
    List<ChapterSummaryDto> Chapters
);

public record ChapterCourseInfoDto(
    int Id,
    string Slug,
    string Title,
    int? VerticalId,
    string? VerticalName
);

public record ChapterModuleInfoDto(
    int Id,
    string Slug,
    string Title,
    string Description,
    string Badge,
    int OrderIndex
);

public record CodeComparisonDto(
    int Id,
    string Title,
    string Description,
    string BeforeLabel,
    string BeforeLanguage,
    string BeforeCode,
    string AfterLabel,
    string AfterLanguage,
    string AfterCode,
    string Explanation,
    int OrderIndex
);

public record ChapterDiagramDto(
    int Id,
    string Title,
    string Caption,
    string DiagramType,
    string SvgContent,
    string? DiagramSpecJson,
    int OrderIndex
);

public record ChapterNoteDto(
    int Id,
    string NoteType,
    string? AnchorSection,
    string Title,
    string ContentBody,
    int OrderIndex,
    DateTime UpdatedAt
);

public record ChapterConceptConnectionsDto(
    List<ConnectedConceptDto> DirectConcepts,
    List<ConceptPrerequisiteItemDto> Prerequisites,
    List<string> NextRecommendedTopics,
    List<string> InterchangeDomains
);

public record ConnectedConceptDto(
    int Id,
    string Slug,
    string Title,
    string Summary,
    string Difficulty,
    string Icon,
    List<string> ConnectedDomains
);

public record ChapterNavDto(
    int Id,
    string Slug,
    string FullSlug,
    string Title,
    string ModuleTitle,
    int ReadingTimeMinutes,
    bool IsCompleted
);

public record CreateChapterNoteRequest(
    string NoteType,
    string? AnchorSection,
    string Title,
    string ContentBody,
    int? OrderIndex
);



