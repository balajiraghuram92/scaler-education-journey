using Microsoft.Extensions.Options;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class ExerciseMetadataServiceTests
{
    [Fact]
    public void ReturnsLearnerSafeMetadataAndTrustedStarterContent()
    {
        var root = ExerciseTestFactory.CreateExerciseRoot();
        try
        {
            Directory.CreateDirectory(Path.Combine(root, "starter", "src", "main", "java"));
            File.WriteAllText(Path.Combine(root, "starter", "src", "main", "java", "One.java"), "class One { }");
            File.WriteAllText(Path.Combine(root, "starter", "src", "main", "java", "Two.java"), "class Two { }");

            var definition = ExerciseTestFactory.CreateDefinition(root);
            definition.Manifest.Instructions = "Implement the protected coordinates.";
            var repository = new StubRepository(definition);
            var service = new ExerciseMetadataService(
                repository,
                Options.Create(ExerciseTestFactory.Options()));

            var metadata = service.GetById("test-exercise");

            Assert.Equal("test-exercise", metadata.Id);
            Assert.Equal(2, metadata.Files.Count);
            Assert.Equal("class One { }", metadata.Files.Single(file => file.Id == "one").StarterContent);
            Assert.Equal("One works", metadata.Evidence.Single(evidence => evidence.Id == "one-evidence").Label);
            Assert.DoesNotContain(metadata.Files, file => file.Path.Contains("TrustedTest", StringComparison.Ordinal));
            Assert.Equal("Implement the protected coordinates.", metadata.Instructions);
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
        }
    }

    [Fact]
    public void MissingExerciseThrowsNotFoundException()
    {
        var root = ExerciseTestFactory.CreateExerciseRoot();
        try
        {
            var definition = ExerciseTestFactory.CreateDefinition(root);
            var service = new ExerciseMetadataService(
                new StubRepository(definition),
                Options.Create(ExerciseTestFactory.Options()));

            Assert.Throws<ExerciseNotFoundException>(() => service.GetById("missing"));
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
        }
    }

    private sealed class StubRepository : IExerciseRepository
    {
        private readonly ExerciseDefinition _definition;

        public StubRepository(ExerciseDefinition definition)
        {
            _definition = definition;
        }

        public ExerciseDefinition? GetById(string exerciseId) =>
            exerciseId == _definition.Manifest.Id ? _definition : null;
    }
}
