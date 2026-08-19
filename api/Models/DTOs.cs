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

