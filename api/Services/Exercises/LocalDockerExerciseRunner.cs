using System.Formats.Tar;
using System.Net;
using System.Text;
using System.Diagnostics;
using Docker.DotNet;
using Docker.DotNet.Models;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Exercises;

public sealed class LocalDockerExerciseRunner : IExerciseRunner
{
    private readonly DockerClient _dockerClient;
    private readonly ExerciseExecutionOptions _options;
    private readonly ILogger<LocalDockerExerciseRunner> _logger;

    public LocalDockerExerciseRunner(
        DockerClient dockerClient,
        IOptions<ExerciseExecutionOptions> options,
        ILogger<LocalDockerExerciseRunner> logger)
    {
        _dockerClient = dockerClient;
        _options = options.Value;
        _logger = logger;
    }

    public async Task<RunnerExecutionResult> RunAsync(
        PreparedExerciseWorkspace workspace,
        CancellationToken cancellationToken)
    {
        var startedAt = Stopwatch.GetTimestamp();
        var containerName = $"studytracker-exercise-{workspace.RunId:N}";
        string? containerId = null;
        var timedOut = false;
        var runnerImage = ResolveRunnerImage(workspace.Definition);

        try
        {
            await EnsureRunnerImageAsync(runnerImage, cancellationToken);

            var createResponse = await _dockerClient.Containers.CreateContainerAsync(
                new CreateContainerParameters
                {
                    Image = runnerImage,
                    Name = containerName,
                    WorkingDir = "/workspace",
                    Labels = new Dictionary<string, string>
                    {
                        ["com.studytracker.exercise-runner"] = "true",
                        ["com.studytracker.run-id"] = workspace.RunId.ToString("N")
                    },
                    HostConfig = new HostConfig
                    {
                        Init = true,
                        AutoRemove = false,
                        NetworkMode = "bridge",
                        Memory = _options.MemoryLimitBytes,
                        NanoCPUs = _options.NanoCpus,
                        PidsLimit = _options.PidsLimit,
                        Mounts = new List<Mount>
                        {
                            new()
                            {
                                Type = "volume",
                                Source = _options.MavenCacheVolume,
                                Target = "/root/.m2"
                            }
                        }
                    }
                },
                cancellationToken);

            containerId = createResponse.ID;

            await CopyWorkspaceIntoContainerAsync(containerId, workspace.Path, cancellationToken);
            await _dockerClient.Containers.StartContainerAsync(
                containerId,
                new ContainerStartParameters(),
                cancellationToken);

            var waitTask = _dockerClient.Containers.WaitContainerAsync(containerId, cancellationToken);
            var timeoutTask = Task.Delay(GetExecutionTimeout(workspace.Definition), CancellationToken.None);
            var completedTask = await Task.WhenAny(waitTask, timeoutTask);

            ContainerWaitResponse waitResponse;
            if (completedTask == timeoutTask)
            {
                timedOut = true;
                await KillContainerAsync(containerId, cancellationToken);
                waitResponse = await waitTask;
            }
            else
            {
                waitResponse = await waitTask;
            }

            var logs = await ReadContainerLogsAsync(containerId, cancellationToken);
            var surefireXml = await ReadSurefireXmlAsync(containerId, cancellationToken);

            return new RunnerExecutionResult
            {
                RunId = workspace.RunId,
                ExitCode = Convert.ToInt32(waitResponse.StatusCode),
                TimedOut = timedOut,
                StandardOutput = logs.StandardOutput,
                StandardError = logs.StandardError,
                SurefireXml = surefireXml,
                Duration = Stopwatch.GetElapsedTime(startedAt)
            };
        }
        catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
        {
            throw;
        }
        catch (DockerImageNotFoundException ex)
        {
            throw new ExerciseRunnerUnavailableException("The configured exercise runner image is unavailable.", ex);
        }
        catch (DockerApiException ex) when (ex.StatusCode is HttpStatusCode.BadRequest or HttpStatusCode.NotFound)
        {
            throw new ExerciseRunnerUnavailableException("The configured exercise runner is unavailable.", ex);
        }
        catch (TaskCanceledException ex) when (!cancellationToken.IsCancellationRequested)
        {
            throw new ExerciseRunnerUnavailableException("The Docker daemon did not respond in time.", ex);
        }
        catch (DockerApiException ex)
        {
            throw new ExerciseInfrastructureException("The Docker runner failed to execute the exercise.", ex);
        }
        catch (HttpRequestException ex)
        {
            throw new ExerciseRunnerUnavailableException("The Docker daemon is unavailable.", ex);
        }
        finally
        {
            if (!string.IsNullOrWhiteSpace(containerId))
            {
                await RemoveContainerQuietlyAsync(containerId);
            }
        }
    }

    private string ResolveRunnerImage(ExerciseDefinition definition)
    {
        var profile = definition.Manifest.Runtime.Profile;
        if (!string.IsNullOrWhiteSpace(profile))
        {
            if (_options.RunnerImagesByProfile.TryGetValue(profile, out var image) &&
                !string.IsNullOrWhiteSpace(image))
            {
                return image;
            }

            var normalizedProfile = profile.Replace('-', '_');
            if (_options.RunnerImagesByProfile.TryGetValue(normalizedProfile, out var normalizedImage) &&
                !string.IsNullOrWhiteSpace(normalizedImage))
            {
                return normalizedImage;
            }
        }

        return _options.RunnerImage;
    }

    private async Task EnsureRunnerImageAsync(string runnerImage, CancellationToken cancellationToken)
    {
        try
        {
            await _dockerClient.Images.InspectImageAsync(runnerImage, cancellationToken);
        }
        catch (DockerImageNotFoundException ex)
        {
            throw new ExerciseRunnerUnavailableException($"The configured exercise runner image '{runnerImage}' is unavailable.", ex);
        }
        catch (DockerApiException ex)
        {
            throw new ExerciseRunnerUnavailableException($"The Docker daemon could not inspect the exercise runner image '{runnerImage}'.", ex);
        }
        catch (TaskCanceledException ex) when (!cancellationToken.IsCancellationRequested)
        {
            throw new ExerciseRunnerUnavailableException("The Docker daemon did not respond in time.", ex);
        }
        catch (HttpRequestException ex)
        {
            throw new ExerciseRunnerUnavailableException("The Docker daemon is unavailable.", ex);
        }
    }

    private async Task CopyWorkspaceIntoContainerAsync(
        string containerId,
        string workspacePath,
        CancellationToken cancellationToken)
    {
        await using var archive = new MemoryStream();
        TarFile.CreateFromDirectory(workspacePath, archive, includeBaseDirectory: false);
        archive.Position = 0;

        await _dockerClient.Containers.ExtractArchiveToContainerAsync(
            containerId,
            new ContainerPathStatParameters
            {
                Path = "/workspace"
            },
            archive,
            cancellationToken);
    }

    private async Task KillContainerAsync(string containerId, CancellationToken cancellationToken)
    {
        try
        {
            await _dockerClient.Containers.KillContainerAsync(
                containerId,
                new ContainerKillParameters { Signal = "SIGKILL" },
                cancellationToken);
        }
        catch (DockerContainerNotFoundException)
        {
            // The container already exited while the timeout path was being handled.
        }
    }

    private async Task<(string StandardOutput, string StandardError)> ReadContainerLogsAsync(
        string containerId,
        CancellationToken cancellationToken)
    {
        using var logs = await _dockerClient.Containers.GetContainerLogsAsync(
            containerId,
            false,
            new ContainerLogsParameters
            {
                ShowStdout = true,
                ShowStderr = true,
                Follow = false,
                Timestamps = false
            },
            cancellationToken);

        await using var standardOutput = new MemoryStream();
        await using var standardError = new MemoryStream();
        await logs.CopyOutputToAsync(Stream.Null, standardOutput, standardError, cancellationToken);

        return (
            Truncate(Encoding.UTF8.GetString(standardOutput.ToArray())),
            Truncate(Encoding.UTF8.GetString(standardError.ToArray())));
    }

    private async Task<string?> ReadSurefireXmlAsync(string containerId, CancellationToken cancellationToken)
    {
        try
        {
            var archive = await _dockerClient.Containers.GetArchiveFromContainerAsync(
                containerId,
                new GetArchiveFromContainerParameters
                {
                    Path = "/workspace/target/surefire-reports"
                },
                statOnly: false,
                cancellationToken: cancellationToken);

            await using var archiveStream = archive.Stream;
            using var archiveBuffer = new MemoryStream();
            await archiveStream.CopyToAsync(archiveBuffer, cancellationToken);
            archiveBuffer.Position = 0;
            using var reader = new TarReader(archiveBuffer);
            TarEntry? entry;
            while ((entry = reader.GetNextEntry()) is not null)
            {
                if (entry.EntryType is not TarEntryType.RegularFile ||
                    !entry.Name.EndsWith(".xml", StringComparison.OrdinalIgnoreCase) ||
                    !Path.GetFileName(entry.Name).StartsWith("TEST-", StringComparison.OrdinalIgnoreCase) ||
                    entry.DataStream is null)
                {
                    continue;
                }

                using var report = new MemoryStream();
                await entry.DataStream.CopyToAsync(report, cancellationToken);
                return Truncate(Encoding.UTF8.GetString(report.ToArray()));
            }

            return null;
        }
        catch (DockerApiException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
        {
            return null;
        }
    }

    private TimeSpan GetExecutionTimeout(ExerciseDefinition definition)
    {
        var manifestSeconds = definition.Manifest.Runtime.TimeoutSeconds;
        var seconds = manifestSeconds > 0
            ? Math.Min((long)manifestSeconds + _options.ExecutionStartupGraceSeconds, _options.MaxExecutionSeconds)
            : _options.MaxExecutionSeconds;

        return TimeSpan.FromSeconds(Math.Max(1, seconds));
    }

    private string Truncate(string value)
    {
        if (value.Length <= _options.MaxOutputBytes)
        {
            return value;
        }

        return value[.._options.MaxOutputBytes] + "\n[output truncated]";
    }

    private async Task RemoveContainerQuietlyAsync(string containerId)
    {
        try
        {
            await _dockerClient.Containers.RemoveContainerAsync(
                containerId,
                new ContainerRemoveParameters { Force = true, RemoveVolumes = false });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to remove exercise runner container {ContainerId}.", containerId);
        }
    }
}
