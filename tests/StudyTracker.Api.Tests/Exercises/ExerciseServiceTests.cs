using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class ExerciseServiceTests
{
    [Fact]
    public async Task Service_ReturnsNormalizedSuccessAndCleansWorkspace()
    {
        var exerciseRoot = ExerciseTestFactory.CreateExerciseRoot();
        var workspaceRoot = Path.Combine(Path.GetTempPath(), "studytracker-service-tests", Guid.NewGuid().ToString("N"));
        try
        {
            var definition = ExerciseTestFactory.CreateDefinition(exerciseRoot);
            var repository = new StubRepository(definition);
            var options = Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options(workspaceRoot));
            var validator = new ExerciseSubmissionValidator(options);
            var builder = new ExerciseWorkspaceBuilder(options);
            var runner = new StubRunner
            {
                Result = new RunnerExecutionResult
                {
                    RunId = Guid.Empty,
                    ExitCode = 0,
                    SurefireXml = "<testsuite><testcase name=\"testOne\" /><testcase name=\"testTwo\" /></testsuite>",
                    Duration = TimeSpan.FromMilliseconds(25)
                }
            };
            var service = new ExerciseService(
                repository,
                validator,
                builder,
                runner,
                new ExerciseExecutionClassifier(new SurefireResultParser()),
                new SemaphoreSlim(1, 1),
                ExerciseTestFactory.Logger<ExerciseService>());

            var response = await service.ExecuteAsync("test-exercise", ExerciseTestFactory.ValidSubmission(), CancellationToken.None);

            Assert.Equal("success", response.Status);
            Assert.True(response.Passed);
            Assert.Equal(2, response.Summary.Passed);
            Assert.NotEqual(string.Empty, response.RunId);
            Assert.Empty(Directory.Exists(workspaceRoot) ? Directory.GetDirectories(workspaceRoot) : Array.Empty<string>());
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(exerciseRoot);
            ExerciseTestFactory.DeleteRoot(workspaceRoot);
        }
    }

    private sealed class StubRepository : IExerciseRepository
    {
        private readonly ExerciseDefinition _definition;

        public StubRepository(ExerciseDefinition definition)
        {
            _definition = definition;
        }

        public ExerciseDefinition? GetById(string exerciseId) => exerciseId == _definition.Manifest.Id ? _definition : null;
    }

    private sealed class StubRunner : IExerciseRunner
    {
        public required RunnerExecutionResult Result { get; init; }

        public Task<RunnerExecutionResult> RunAsync(PreparedExerciseWorkspace workspace, CancellationToken cancellationToken)
        {
            return Task.FromResult(new RunnerExecutionResult
            {
                RunId = workspace.RunId,
                ExitCode = Result.ExitCode,
                TimedOut = Result.TimedOut,
                StandardOutput = Result.StandardOutput,
                StandardError = Result.StandardError,
                SurefireXml = Result.SurefireXml,
                Duration = Result.Duration
            });
        }
    }
}
