using Microsoft.Extensions.Options;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class ExerciseSolutionServiceTests
{
    [Fact]
    public void ReturnsAllManifestEditableSolutionFilesInDisplayOrder()
    {
        var root = ExerciseTestFactory.CreateExerciseRoot();
        try
        {
            Directory.CreateDirectory(Path.Combine(root, "solution", "src", "main", "java"));
            File.WriteAllText(Path.Combine(root, "solution", "src", "main", "java", "One.java"), "class One { int value = 1; }");
            File.WriteAllText(Path.Combine(root, "solution", "src", "main", "java", "Two.java"), "class Two { int value = 2; }");

            var definition = ExerciseTestFactory.CreateDefinition(root);
            definition.Manifest.Language = "java";
            var service = new ExerciseSolutionService(
                new StubRepository(definition),
                Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options()));

            var solution = service.GetById("test-exercise");

            Assert.Equal("test-exercise", solution.ExerciseId);
            Assert.Equal(2, solution.Files.Count);
            Assert.Equal(new[] { "one", "two" }, solution.Files.Select(file => file.Id));
            Assert.Equal("class One { int value = 1; }", solution.Files[0].Content);
            Assert.All(solution.Files, file => Assert.Equal("java", file.Language));
            Assert.Equal(0, solution.Files[0].DisplayOrder);
            Assert.Equal(1, solution.Files[1].DisplayOrder);
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
        }
    }

    [Fact]
    public void MissingReferenceSolutionIsReportedWithoutBreakingMetadataLookup()
    {
        var root = ExerciseTestFactory.CreateExerciseRoot();
        try
        {
            var definition = ExerciseTestFactory.CreateDefinition(root);
            var service = new ExerciseSolutionService(
                new StubRepository(definition),
                Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options()));

            Assert.Throws<ExerciseSolutionNotFoundException>(() => service.GetById("test-exercise"));
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
        }
    }

    [Fact]
    public void UnknownExerciseIdDoesNotResolveAFilePath()
    {
        var root = ExerciseTestFactory.CreateExerciseRoot();
        try
        {
            var definition = ExerciseTestFactory.CreateDefinition(root);
            var service = new ExerciseSolutionService(
                new StubRepository(definition),
                Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options()));

            Assert.Throws<ExerciseNotFoundException>(() => service.GetById("unknown"));
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
        }
    }

    [Fact]
    public void UnsafeManifestSolutionPathIsRejectedBeforeFilesystemAccess()
    {
        var root = ExerciseTestFactory.CreateExerciseRoot();
        try
        {
            var definition = ExerciseTestFactory.CreateDefinition(root);
            definition.Manifest.Files[0].Path = "../outside.java";
            var service = new ExerciseSolutionService(
                new StubRepository(definition),
                Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options()));

            Assert.Throws<ExerciseInfrastructureException>(() => service.GetById("test-exercise"));
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
