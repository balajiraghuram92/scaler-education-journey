namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseSubmissionValidationException : Exception
{
    public ExerciseSubmissionValidationException(IReadOnlyList<string> errors)
        : base("The exercise submission is invalid.")
    {
        Errors = errors;
    }

    public IReadOnlyList<string> Errors { get; }
}

public sealed class ExerciseInfrastructureException : Exception
{
    public ExerciseInfrastructureException(string message, Exception? innerException = null)
        : base(message, innerException)
    {
    }
}

public sealed class ExerciseRunnerUnavailableException : Exception
{
    public ExerciseRunnerUnavailableException(string message, Exception? innerException = null)
        : base(message, innerException)
    {
    }
}

public sealed class ExerciseNotFoundException : Exception
{
    public ExerciseNotFoundException(string exerciseId)
        : base($"Exercise '{exerciseId}' was not found.")
    {
        ExerciseId = exerciseId;
    }

    public string ExerciseId { get; }
}

public sealed class ExerciseConcurrencyLimitException : Exception
{
    public ExerciseConcurrencyLimitException()
        : base("The exercise execution concurrency limit has been reached.")
    {
    }
}
