namespace StudyTracker.Api.Services.Exercises;

public enum ExerciseExecutionStatus
{
    Success,
    TestFailure,
    CompilationFailure,
    Timeout
}

public sealed class PreparedExerciseWorkspace
{
    public required Guid RunId { get; init; }

    public required string Path { get; init; }

    public required ExerciseDefinition Definition { get; init; }
}

public sealed class RunnerExecutionResult
{
    public required Guid RunId { get; init; }

    public int ExitCode { get; init; }

    public bool TimedOut { get; init; }

    public string StandardOutput { get; init; } = string.Empty;

    public string StandardError { get; init; } = string.Empty;

    public string? SurefireXml { get; init; }

    public TimeSpan Duration { get; init; }
}

public sealed class ParsedSurefireResult
{
    public int Total { get; init; }

    public int Passed { get; init; }

    public int Failed { get; init; }

    public int Errors { get; init; }

    public int Skipped { get; init; }

    public IReadOnlyList<ParsedSurefireTest> Tests { get; init; } = Array.Empty<ParsedSurefireTest>();
}

public sealed class ParsedSurefireTest
{
    public required string TestMethod { get; init; }

    public string? EvidenceId { get; init; }

    public string? Label { get; init; }

    public required string Status { get; init; }

    public TimeSpan Duration { get; init; }

    public string? Message { get; init; }
}
