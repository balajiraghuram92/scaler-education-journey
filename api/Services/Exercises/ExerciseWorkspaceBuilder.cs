using System.Text;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseWorkspaceBuilder
{
    private readonly ExerciseExecutionOptions _options;

    public ExerciseWorkspaceBuilder(IOptions<ExerciseExecutionOptions> options)
    {
        _options = options.Value;
    }

    public async Task<PreparedExerciseWorkspace> BuildAsync(
        Guid runId,
        ExerciseDefinition definition,
        IReadOnlyDictionary<string, ExerciseFileSubmission> submission,
        CancellationToken cancellationToken)
    {
        var workspaceRoot = string.IsNullOrWhiteSpace(_options.WorkspaceRoot)
            ? Path.Combine(Path.GetTempPath(), "studytracker-exercises")
            : _options.WorkspaceRoot;

        Directory.CreateDirectory(workspaceRoot);
        var workspacePath = ExercisePathRules.ResolveInside(workspaceRoot, runId.ToString("N"));
        Directory.CreateDirectory(workspacePath);

        try
        {
            var pomSource = Path.Combine(definition.ExerciseRoot, "pom.xml");
            var pomDestination = ExercisePathRules.ResolveInside(workspacePath, "pom.xml");
            File.Copy(pomSource, pomDestination);

            var testSource = ExercisePathRules.ResolveInside(definition.ExerciseRoot, definition.Manifest.TestSuite.Path);
            var testDestinationPath = ResolveTestWorkspacePath(definition.Manifest);
            var testDestination = ExercisePathRules.ResolveInside(workspacePath, testDestinationPath);
            Directory.CreateDirectory(Path.GetDirectoryName(testDestination)!);
            File.Copy(testSource, testDestination);

            foreach (var file in submission.Values)
            {
                var destination = ExercisePathRules.ResolveInside(workspacePath, file.Path);
                Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
                await File.WriteAllTextAsync(
                    destination,
                    file.Content ?? string.Empty,
                    new UTF8Encoding(encoderShouldEmitUTF8Identifier: false),
                    cancellationToken);
            }

            return new PreparedExerciseWorkspace
            {
                RunId = runId,
                Path = workspacePath,
                Definition = definition
            };
        }
        catch
        {
            DeleteWorkspace(workspacePath);
            throw;
        }
    }

    public static void DeleteWorkspace(string? workspacePath)
    {
        if (string.IsNullOrWhiteSpace(workspacePath) || !Directory.Exists(workspacePath))
        {
            return;
        }

        Directory.Delete(workspacePath, recursive: true);
    }

    private static string ResolveTestWorkspacePath(ExerciseManifest manifest)
    {
        if (manifest.Runtime.Profile.Equals("java-maven", StringComparison.OrdinalIgnoreCase))
        {
            const string testsPrefix = "tests/";
            if (manifest.TestSuite.Path.StartsWith(testsPrefix, StringComparison.Ordinal))
            {
                return manifest.TestSuite.Path[testsPrefix.Length..];
            }

            return manifest.TestSuite.Path;
        }

        throw new ExerciseInfrastructureException($"No workspace layout is registered for runtime profile '{manifest.Runtime.Profile}'.");
    }
}
