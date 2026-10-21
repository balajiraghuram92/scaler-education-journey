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

        if (ExerciseRuntimeProfiles.IsPython(definition.Manifest))
        {
            return ClassifyPython(definition, runnerResult);
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

    // Python has no compile step: the equivalent is pytest failing to import the learner's
    // modules while collecting tests (SyntaxError, IndentationError, ImportError, NameError at import).
    private static readonly string[] PythonCollectionMarkers =
    {
        "ERROR collecting",
        "SyntaxError",
        "IndentationError",
        "TabError",
        "ImportError",
        "ModuleNotFoundError"
    };

    private ClassifiedExerciseExecution ClassifyPython(ExerciseDefinition definition, RunnerExecutionResult runnerResult)
    {
        ParsedSurefireResult? parsed = null;
        if (!string.IsNullOrWhiteSpace(runnerResult.SurefireXml))
        {
            try
            {
                parsed = _surefireResultParser.Parse(runnerResult.SurefireXml, definition);
            }
            catch (ExerciseInfrastructureException)
            {
                parsed = null; // an empty report (nothing collected) is handled below
            }
        }

        var output = $"{runnerResult.StandardOutput}\n{runnerResult.StandardError}";
        var collectionFailed = parsed?.Tests.Any(test =>
                                   test.Status == "error" &&
                                   (!test.TestMethod.StartsWith("test", StringComparison.Ordinal) ||
                                    (test.Message ?? string.Empty).Contains("collection failure", StringComparison.OrdinalIgnoreCase))) == true
                               || output.Contains("ERROR collecting", StringComparison.Ordinal)
                               || output.Contains("Interrupted: ", StringComparison.Ordinal);

        if (collectionFailed || (parsed is null && PythonCollectionMarkers.Any(marker => output.Contains(marker, StringComparison.Ordinal))))
        {
            return new ClassifiedExerciseExecution
            {
                Status = ExerciseExecutionStatus.CompilationFailure,
                RunnerResult = runnerResult
            };
        }

        if (parsed is null)
        {
            throw new ExerciseInfrastructureException("The Python runner exited without producing a pytest report.");
        }

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

        throw new ExerciseInfrastructureException("pytest exited unsuccessfully despite a non-failing report.");
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
