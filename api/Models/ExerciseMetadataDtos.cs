namespace StudyTracker.Api.Models;

public sealed record ExerciseMetadataResponse(
    string Id,
    string LessonSlug,
    string Title,
    string Language,
    string Difficulty,
    int EstimatedMinutes,
    string? Instructions,
    IReadOnlyList<ExerciseFileMetadataDto> Files,
    IReadOnlyList<ExerciseEvidenceMetadataDto> Evidence);

public sealed record ExerciseFileMetadataDto(
    string Id,
    string Path,
    string DisplayName,
    bool Editable,
    string StarterContent);

public sealed record ExerciseEvidenceMetadataDto(
    string Id,
    string Label);

public sealed record ExerciseSolutionResponse(
    string ExerciseId,
    IReadOnlyList<ExerciseSolutionFileDto> Files);

public sealed record ExerciseSolutionFileDto(
    string Id,
    string Path,
    string DisplayName,
    string Language,
    string Content,
    int DisplayOrder);
