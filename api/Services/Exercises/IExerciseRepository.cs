namespace StudyTracker.Api.Services.Exercises;

public interface IExerciseRepository
{
    ExerciseDefinition? GetById(string exerciseId);
}
