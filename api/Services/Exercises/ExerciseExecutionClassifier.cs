namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseExecutionClassifier
{
    private static readonly string[] CompilationMarkers =
    {
        "COMPILATION ERROR",
        "Compilation failure",
        "maven-compiler-plugin",
        "cannot find symbol",
        "';' expected",
        "illegal start of"
    };

    private readonly SurefireResultParser _surefireResultParser;

    public ExerciseExecutionClassifier(SurefireResultParser surefireResultParser)
    {
        _surefireResultParser = surefireResultParser;
    }

    public ClassifiedExerciseExecution Classify(
        ExerciseDefinition definition,
        RunnerExecutionResult runnerResult)
    {
        if (runnerResult.TimedOut)
        {
            return new ClassifiedExerciseExecution
            {
                Status = ExerciseExecutionStatus.Timeout,
                RunnerResult = runnerResult
            };
        }

        if (!string.IsNullOrWhiteSpace(runnerResult.SurefireXml))
        {
            var parsed = _surefireResultParser.Parse(runnerResult.SurefireXml, definition);
            if (parsed.Failed > 0 || parsed.Errors > 0)
            {
                return new ClassifiedExerciseExecution
                {
                    Status = ExerciseExecutionStatus.TestFailure,
                    RunnerResult = runnerResult,
                    SurefireResult = parsed
                };
            }

            if (runnerResult.ExitCode == 0 && parsed.Total > 0)
            {
                return new ClassifiedExerciseExecution
                {
                    Status = ExerciseExecutionStatus.Success,
                    RunnerResult = runnerResult,
                    SurefireResult = parsed
                };
            }

            throw new ExerciseInfrastructureException("Maven exited unsuccessfully despite a non-failing Surefire report.");
        }

        if (LooksLikeCompilationFailure(runnerResult.StandardOutput, runnerResult.StandardError))
        {
            return new ClassifiedExerciseExecution
            {
                Status = ExerciseExecutionStatus.CompilationFailure,
                RunnerResult = runnerResult
            };
        }

        throw new ExerciseInfrastructureException("The exercise runner exited without producing authoritative Surefire results.");
    }

    private static bool LooksLikeCompilationFailure(string standardOutput, string standardError)
    {
        var output = $"{standardOutput}\n{standardError}";
        return CompilationMarkers.Any(marker => output.Contains(marker, StringComparison.OrdinalIgnoreCase));
    }
}

public sealed class ClassifiedExerciseExecution
{
    public required ExerciseExecutionStatus Status { get; init; }

    public required RunnerExecutionResult RunnerResult { get; init; }

    public ParsedSurefireResult? SurefireResult { get; init; }
}
