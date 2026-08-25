using System.Text.Json.Serialization;

namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseManifest
{
    public string Id { get; set; } = string.Empty;

    public string LessonSlug { get; set; } = string.Empty;

    public string Title { get; set; } = string.Empty;

    public string Language { get; set; } = string.Empty;

    public string Difficulty { get; set; } = string.Empty;

    public int EstimatedMinutes { get; set; }

    public string? Instructions { get; set; }

    public ExerciseRuntimeManifest Runtime { get; set; } = new();

    public List<ExerciseFileManifest> Files { get; set; } = new();

    public ExerciseTestSuiteManifest TestSuite { get; set; } = new();

    public List<ExerciseEvidenceManifest> Evidence { get; set; } = new();
}

public sealed class ExerciseRuntimeManifest
{
    public string Profile { get; set; } = string.Empty;

    public int JavaVersion { get; set; }

    public int TimeoutSeconds { get; set; }
}

public sealed class ExerciseFileManifest
{
    public string Id { get; set; } = string.Empty;

    public string Path { get; set; } = string.Empty;

    public string DisplayName { get; set; } = string.Empty;

    public bool Editable { get; set; }
}

public sealed class ExerciseTestSuiteManifest
{
    public bool Visible { get; set; }

    public string Path { get; set; } = string.Empty;

    public string ClassName { get; set; } = string.Empty;
}

public sealed class ExerciseEvidenceManifest
{
    public string Id { get; set; } = string.Empty;

    public string Label { get; set; } = string.Empty;

    public string TestMethod { get; set; } = string.Empty;
}

public sealed class ExerciseDefinition
{
    public required ExerciseManifest Manifest { get; init; }

    public required string ManifestPath { get; init; }

    public required string ExerciseRoot { get; init; }

    public IReadOnlyDictionary<string, ExerciseFileManifest> EditableFiles { get; init; } =
        new Dictionary<string, ExerciseFileManifest>(StringComparer.Ordinal);

    public IReadOnlyDictionary<string, ExerciseEvidenceManifest> EvidenceByTestMethod { get; init; } =
        new Dictionary<string, ExerciseEvidenceManifest>(StringComparer.Ordinal);
}

internal static class ExercisePathRules
{
    public static bool IsSafeRelativePath(string? path)
    {
        if (string.IsNullOrWhiteSpace(path) || path.Contains('\\') || path.Contains(':'))
        {
            return false;
        }

        if (Path.IsPathRooted(path))
        {
            return false;
        }

        var segments = path.Split('/', StringSplitOptions.None);
        return segments.All(segment => segment.Length > 0 && segment != "." && segment != "..");
    }

    public static string ResolveInside(string root, string relativePath)
    {
        if (!IsSafeRelativePath(relativePath))
        {
            throw new InvalidOperationException($"Unsafe trusted exercise path '{relativePath}'.");
        }

        var fullRoot = Path.GetFullPath(root);
        var fullPath = Path.GetFullPath(Path.Combine(fullRoot, relativePath.Replace('/', Path.DirectorySeparatorChar)));
        var comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        var rootWithSeparator = fullRoot.EndsWith(Path.DirectorySeparatorChar)
            ? fullRoot
            : fullRoot + Path.DirectorySeparatorChar;

        if (!fullPath.StartsWith(rootWithSeparator, comparison))
        {
            throw new InvalidOperationException($"Trusted exercise path '{relativePath}' escapes the exercise root.");
        }

        return fullPath;
    }
}
