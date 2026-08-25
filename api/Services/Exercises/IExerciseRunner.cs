namespace StudyTracker.Api.Services.Exercises;

public interface IExerciseRunner
{
    Task<RunnerExecutionResult> RunAsync(
        PreparedExerciseWorkspace workspace,
        CancellationToken cancellationToken);
}
