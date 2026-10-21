using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseService
{
    private readonly IExerciseRepository _repository;
    private readonly ExerciseSubmissionValidator _submissionValidator;
    private readonly ExerciseWorkspaceBuilder _workspaceBuilder;
    private readonly IExerciseRunner _runner;
    private readonly ExerciseExecutionClassifier _classifier;
    private readonly SemaphoreSlim _concurrencyLimiter;
    private readonly ILogger<ExerciseService> _logger;

    public ExerciseService(
        IExerciseRepository repository,
        ExerciseSubmissionValidator submissionValidator,
        ExerciseWorkspaceBuilder workspaceBuilder,
        IExerciseRunner runner,
        ExerciseExecutionClassifier classifier,
        SemaphoreSlim concurrencyLimiter,
        ILogger<ExerciseService> logger)
    {
        _repository = repository;
        _submissionValidator = submissionValidator;
        _workspaceBuilder = workspaceBuilder;
        _runner = runner;
        _classifier = classifier;
        _concurrencyLimiter = concurrencyLimiter;
        _logger = logger;
    }

    public async Task<ExerciseExecutionResponse> ExecuteAsync(
        string exerciseId,
        ExerciseSubmissionRequest request,
        CancellationToken cancellationToken)
    {
        var definition = _repository.GetById(exerciseId)
            ?? throw new ExerciseNotFoundException(exerciseId);

        if (!await _concurrencyLimiter.WaitAsync(0, cancellationToken))
        {
            throw new ExerciseConcurrencyLimitException();
        }

        var runId = Guid.NewGuid();
        PreparedExerciseWorkspace? workspace = null;
        try
        {
            _logger.LogInformation(
                "Starting exercise execution {RunId} for {ExerciseId}.",
                runId,
                exerciseId);

            var submission = _submissionValidator.Validate(definition, request);
            workspace = await _workspaceBuilder.BuildAsync(runId, definition, submission, cancellationToken);
            var runnerResult = await _runner.RunAsync(workspace, cancellationToken);
            var classified = _classifier.Classify(definition, runnerResult);
            var response = ToResponse(exerciseId, classified, ExerciseRuntimeProfiles.IsPython(definition.Manifest));

            _logger.LogInformation(
                "Completed exercise execution {RunId} for {ExerciseId} with status {Status} in {DurationMilliseconds} ms.",
                runId,
                exerciseId,
                response.Status,
                response.DurationMilliseconds);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(
                ex,
                "Exercise execution {RunId} for {ExerciseId} failed.",
                runId,
                exerciseId);
            throw;
        }
        finally
        {
            if (workspace is not null)
            {
                try
                {
                    ExerciseWorkspaceBuilder.DeleteWorkspace(workspace.Path);
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Failed to remove exercise workspace for run {RunId}.", runId);
                }
            }

            _concurrencyLimiter.Release();
        }
    }

    private static ExerciseExecutionResponse ToResponse(
        string exerciseId,
        ClassifiedExerciseExecution classified,
        bool isPython = false)
    {
        var parsed = classified.SurefireResult;
        var evidence = parsed?.Tests
            .Where(test => !string.IsNullOrWhiteSpace(test.EvidenceId))
            .Select(test => new ExerciseEvidenceResultDto(
                test.EvidenceId!,
                test.Label ?? test.EvidenceId!,
                test.Status,
                (long)test.Duration.TotalMilliseconds,
                test.Message))
            .ToList() ?? new List<ExerciseEvidenceResultDto>();

        var compilerOutput = classified.Status == ExerciseExecutionStatus.CompilationFailure
            ? (isPython ? PythonCompilerOutput(CombineOutput(classified.RunnerResult)) : CombineOutput(classified.RunnerResult))
            : null;
        var runtimeOutput = classified.Status == ExerciseExecutionStatus.TestFailure
            ? CombineOutput(classified.RunnerResult)
            : null;

        return new ExerciseExecutionResponse(
            classified.RunnerResult.RunId.ToString("N"),
            exerciseId,
            ToPublicStatus(classified.Status),
            classified.Status == ExerciseExecutionStatus.Success,
            (long)classified.RunnerResult.Duration.TotalMilliseconds,
            new ExerciseTestSummaryDto(
                parsed?.Total ?? 0,
                parsed?.Passed ?? 0,
                parsed?.Failed ?? 0,
                parsed?.Errors ?? 0,
                parsed?.Skipped ?? 0),
            evidence,
            new ExerciseDiagnosticsDto(compilerOutput, runtimeOutput));
    }

    private static readonly System.Text.RegularExpressions.Regex LearnerFrame =
        new(@"^(?!tests/|/usr/|<frozen)[\w./-]+\.py:\d+: in ", System.Text.RegularExpressions.RegexOptions.Compiled);

    /// <summary>
    /// pytest reports a learner's syntax/import error as a collection error buried in framework frames.
    /// Keep what the learner can act on: the error lines ("E ...") and frames inside their own files.
    /// </summary>
    public static string? PythonCompilerOutput(string? combined)
    {
        if (string.IsNullOrWhiteSpace(combined))
        {
            return combined;
        }

        var lines = combined.Replace("\r", string.Empty).Split('\n');
        var kept = new List<string>();
        for (var i = 0; i < lines.Length; i++)
        {
            var line = lines[i];
            if (line.StartsWith("E ", StringComparison.Ordinal))
            {
                kept.Add(line.Length > 4 ? line[4..] : string.Empty);
            }
            else if (LearnerFrame.IsMatch(line))
            {
                kept.Add(line);
                if (i + 1 < lines.Length && lines[i + 1].StartsWith("    ", StringComparison.Ordinal))
                {
                    kept.Add(lines[++i]);
                }
            }
        }

        return kept.Count == 0
            ? combined
            : string.Join('\n', kept).Replace("/workspace/", string.Empty);
    }

    private static string? CombineOutput(RunnerExecutionResult result)
    {
        var combined = string.Join(
            Environment.NewLine,
            new[] { result.StandardOutput, result.StandardError }.Where(value => !string.IsNullOrWhiteSpace(value)));

        return string.IsNullOrWhiteSpace(combined) ? null : combined;
    }

    private static string ToPublicStatus(ExerciseExecutionStatus status)
    {
        return status switch
        {
            ExerciseExecutionStatus.Success => "success",
            ExerciseExecutionStatus.TestFailure => "testFailure",
            ExerciseExecutionStatus.CompilationFailure => "compilationFailure",
            ExerciseExecutionStatus.Timeout => "timeout",
            _ => throw new ArgumentOutOfRangeException(nameof(status), status, null)
        };
    }
}
