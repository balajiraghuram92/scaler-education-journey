using System.Text.Json;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class ExerciseManifestRepositoryTests
{
    [Fact]
    public void Repository_LoadsManifestById_WithoutExerciseSpecificKnowledge()
    {
        var root = ExerciseTestFactory.CreateExerciseRoot();
        try
        {
            var manifest = ExerciseTestFactory.CreateDefinition(root).Manifest;
            File.WriteAllText(Path.Combine(root, "exercise.json"), JsonSerializer.Serialize(manifest));

            var options = Microsoft.Extensions.Options.Options.Create(new ExerciseExecutionOptions { ExercisesRoot = root });
            var repository = new ExerciseRepository(options, ExerciseTestFactory.Logger<ExerciseRepository>());

            var definition = repository.GetById("test-exercise");

            Assert.NotNull(definition);
            Assert.Equal("java-maven", definition.Manifest.Runtime.Profile);
            Assert.Equal(2, definition.EditableFiles.Count);
            Assert.Null(repository.GetById("unknown"));
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
        }
    }
}
