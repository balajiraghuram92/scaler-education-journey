namespace StudyTracker.Api.Models;

public sealed record ExerciseSubmissionRequest(
    List<ExerciseFileSubmission> Files,
    string? ClientRequestId = null);

public sealed record ExerciseFileSubmission(
    string Path,
    string Content);

public sealed record ExerciseExecutionResponse(
    string RunId,
    string ExerciseId,
    string Status,
    bool Passed,
    long DurationMilliseconds,
    ExerciseTestSummaryDto Summary,
    IReadOnlyList<ExerciseEvidenceResultDto> Evidence,
    ExerciseDiagnosticsDto Diagnostics);

public sealed record ExerciseTestSummaryDto(
    int Total,
    int Passed,
    int Failed,
    int Errors,
    int Skipped);

public sealed record ExerciseEvidenceResultDto(
    string Id,
    string Label,
    string Status,
    long DurationMilliseconds,
    string? Message);

public sealed record ExerciseDiagnosticsDto(
    string? CompilerOutput,
    string? RuntimeOutput);
