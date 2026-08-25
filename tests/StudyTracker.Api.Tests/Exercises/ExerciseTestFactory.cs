using Microsoft.Extensions.Logging.Abstractions;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Exercises;

namespace StudyTracker.Api.Tests.Exercises;

internal static class ExerciseTestFactory
{
    public static ExerciseDefinition CreateDefinition(string root)
    {
        var manifest = new ExerciseManifest
        {
            Id = "test-exercise",
            Runtime = new ExerciseRuntimeManifest
            {
                Profile = "java-maven",
                TimeoutSeconds = 10
            },
            Files = new List<ExerciseFileManifest>
            {
                new() { Id = "one", Path = "src/main/java/One.java", DisplayName = "One.java", Editable = true },
                new() { Id = "two", Path = "src/main/java/Two.java", DisplayName = "Two.java", Editable = true },
                new() { Id = "read-only", Path = "src/main/java/ReadOnly.java", DisplayName = "ReadOnly.java", Editable = false }
            },
            TestSuite = new ExerciseTestSuiteManifest
            {
                Path = "tests/src/test/java/TrustedTest.java",
                ClassName = "TrustedTest"
            },
            Evidence = new List<ExerciseEvidenceManifest>
            {
                new() { Id = "one-evidence", Label = "One works", TestMethod = "testOne" },
                new() { Id = "two-evidence", Label = "Two works", TestMethod = "testTwo" }
            }
        };

        return new ExerciseDefinition
        {
            Manifest = manifest,
            ManifestPath = Path.Combine(root, "exercise.json"),
            ExerciseRoot = root,
            EditableFiles = manifest.Files.Where(file => file.Editable).ToDictionary(file => file.Path, StringComparer.Ordinal),
            EvidenceByTestMethod = manifest.Evidence.ToDictionary(evidence => evidence.TestMethod, StringComparer.Ordinal)
        };
    }

    public static string CreateExerciseRoot()
    {
        var root = Path.Combine(Path.GetTempPath(), "studytracker-exercise-tests", Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path.Combine(root, "tests", "src", "test", "java"));
        File.WriteAllText(Path.Combine(root, "pom.xml"), "<project />");
        File.WriteAllText(Path.Combine(root, "tests", "src", "test", "java", "TrustedTest.java"), "class TrustedTest {}");
        return root;
    }

    public static void DeleteRoot(string? root)
    {
        if (!string.IsNullOrWhiteSpace(root) && Directory.Exists(root))
        {
            Directory.Delete(root, recursive: true);
        }
    }

    public static ExerciseExecutionOptions Options(string? workspaceRoot = null)
    {
        return new ExerciseExecutionOptions
        {
            WorkspaceRoot = workspaceRoot ?? Path.Combine(Path.GetTempPath(), "studytracker-exercise-workspaces", Guid.NewGuid().ToString("N")),
            MaxFileBytes = 1024,
            MaxSubmissionBytes = 2048,
            MaxOutputBytes = 4096,
            MaxExecutionSeconds = 10
        };
    }

    public static ExerciseSubmissionRequest ValidSubmission()
    {
        return new ExerciseSubmissionRequest(new List<ExerciseFileSubmission>
        {
            new("src/main/java/One.java", "class One {}"),
            new("src/main/java/Two.java", "class Two {}")
        });
    }

    public static NullLogger<T> Logger<T>() => NullLogger<T>.Instance;
}
