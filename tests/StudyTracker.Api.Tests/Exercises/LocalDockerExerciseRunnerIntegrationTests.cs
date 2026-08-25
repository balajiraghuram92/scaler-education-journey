using Docker.DotNet;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class LocalDockerExerciseRunnerIntegrationTests
{
    [Fact(Skip = "Run the Docker-backed exercise integration through the end-to-end validation command.")]
    public async Task GoldenSolution_ExecutesThroughThePhase1Runner()
    {
        if (!string.Equals(Environment.GetEnvironmentVariable("RUN_DOCKER_EXERCISE_TESTS"), "1", StringComparison.Ordinal))
        {
            return;
        }

        var repositoryRoot = FindRepositoryRoot();
        var optionsValue = new ExerciseExecutionOptions
        {
            ExercisesRoot = Path.Combine(repositoryRoot, "exercises"),
            WorkspaceRoot = Path.Combine(Path.GetTempPath(), "studytracker-docker-tests", Guid.NewGuid().ToString("N")),
            RunnerImage = Environment.GetEnvironmentVariable("EXERCISE_RUNNER_IMAGE") ?? "neuralascent-java-runner:dev",
            DockerEndpoint = Environment.GetEnvironmentVariable("DOCKER_ENDPOINT") ?? "unix:///var/run/docker.sock",
            MavenCacheVolume = Environment.GetEnvironmentVariable("EXERCISE_MAVEN_CACHE_VOLUME") ?? "neuralascent-maven-cache",
            MaxOutputBytes = 65_536,
            MaxExecutionSeconds = 120
        };

        var options = Microsoft.Extensions.Options.Options.Create(optionsValue);
        var repository = new ExerciseRepository(options, ExerciseTestFactory.Logger<ExerciseRepository>());
        var definition = repository.GetById("java-lld-oop3-point-threedpoint");
        Assert.NotNull(definition);

        var request = new ExerciseSubmissionRequest(
            definition.Manifest.Files
                .Where(file => file.Editable)
                .Select(file => new ExerciseFileSubmission(
                    file.Path,
                    File.ReadAllText(Path.Combine(definition.ExerciseRoot, "solution", file.Path))))
                .ToList());
        var validator = new ExerciseSubmissionValidator(options);
        var submission = validator.Validate(definition, request);
        var builder = new ExerciseWorkspaceBuilder(options);
        var workspace = await builder.BuildAsync(Guid.NewGuid(), definition, submission, CancellationToken.None);

        using var dockerClient = new DockerClientConfiguration(new Uri(optionsValue.DockerEndpoint)).CreateClient();
        var runner = new LocalDockerExerciseRunner(dockerClient, options, ExerciseTestFactory.Logger<LocalDockerExerciseRunner>());
        try
        {
            var rawResult = await runner.RunAsync(workspace, CancellationToken.None);
            var classified = new ExerciseExecutionClassifier(new SurefireResultParser()).Classify(definition, rawResult);

            Assert.Equal(ExerciseExecutionStatus.Success, classified.Status);
            Assert.NotNull(classified.SurefireResult);
            Assert.Equal(7, classified.SurefireResult!.Total);
            Assert.Equal(7, classified.SurefireResult.Passed);
        }
        finally
        {
            ExerciseWorkspaceBuilder.DeleteWorkspace(workspace.Path);
            ExerciseTestFactory.DeleteRoot(optionsValue.WorkspaceRoot);
        }
    }

    private static string FindRepositoryRoot()
    {
        var current = new DirectoryInfo(AppContext.BaseDirectory);
        while (current is not null)
        {
            if (Directory.Exists(Path.Combine(current.FullName, "exercises")) &&
                File.Exists(Path.Combine(current.FullName, "api", "StudyTracker.Api.csproj")))
            {
                return current.FullName;
            }

            current = current.Parent;
        }

        throw new InvalidOperationException("Could not locate the repository root for Docker exercise integration testing.");
    }
}
