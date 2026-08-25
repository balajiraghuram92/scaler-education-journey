using Microsoft.Extensions.Options;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class ExerciseWorkspaceBuilderTests
{
    [Fact]
    public async Task Builder_CopiesTrustedPomAndTests_AndOnlySubmittedSource()
    {
        var exerciseRoot = ExerciseTestFactory.CreateExerciseRoot();
        var workspaceRoot = Path.Combine(Path.GetTempPath(), "studytracker-workspace-tests", Guid.NewGuid().ToString("N"));
        try
        {
            var definition = ExerciseTestFactory.CreateDefinition(exerciseRoot);
            var validator = new ExerciseSubmissionValidator(Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options(workspaceRoot)));
            var builder = new ExerciseWorkspaceBuilder(Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options(workspaceRoot)));
            var submission = validator.Validate(definition, ExerciseTestFactory.ValidSubmission());

            var workspace = await builder.BuildAsync(Guid.NewGuid(), definition, submission, CancellationToken.None);

            Assert.True(File.Exists(Path.Combine(workspace.Path, "pom.xml")));
            Assert.True(File.Exists(Path.Combine(workspace.Path, "src", "test", "java", "TrustedTest.java")));
            Assert.Equal("class One {}", await File.ReadAllTextAsync(Path.Combine(workspace.Path, "src", "main", "java", "One.java")));
            Assert.False(File.Exists(Path.Combine(workspace.Path, "exercise.json")));
            Assert.False(File.Exists(Path.Combine(workspace.Path, "solution", "src", "main", "java", "One.java")));

            ExerciseWorkspaceBuilder.DeleteWorkspace(workspace.Path);
            Assert.False(Directory.Exists(workspace.Path));
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(exerciseRoot);
            ExerciseTestFactory.DeleteRoot(workspaceRoot);
        }
    }
}
