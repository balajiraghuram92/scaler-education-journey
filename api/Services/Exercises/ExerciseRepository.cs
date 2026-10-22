using System.Text.Json;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseRepository : IExerciseRepository
{
    private readonly IReadOnlyDictionary<string, ExerciseDefinition> _definitions;

    public ExerciseRepository(IOptions<ExerciseExecutionOptions> options, ILogger<ExerciseRepository> logger)
    {
        var root = ResolveExerciseRoot(options.Value.ExercisesRoot);
        _definitions = LoadDefinitions(root, logger);

        if (_definitions.Count == 0)
        {
            throw new InvalidOperationException($"No exercise manifests were found under '{root}'.");
        }
    }

    public ExerciseDefinition? GetById(string exerciseId)
    {
        return _definitions.TryGetValue(exerciseId, out var definition) ? definition : null;
    }

    private static string ResolveExerciseRoot(string configuredRoot)
    {
        var root = string.IsNullOrWhiteSpace(configuredRoot)
            ? Path.Combine(Directory.GetCurrentDirectory(), "exercises")
            : configuredRoot;

        var fullRoot = Path.GetFullPath(root);
        if (!Directory.Exists(fullRoot))
        {
            throw new InvalidOperationException($"Configured exercise root does not exist: '{fullRoot}'.");
        }

        return fullRoot;
    }

    private static IReadOnlyDictionary<string, ExerciseDefinition> LoadDefinitions(string root, ILogger logger)
    {
        var definitions = new Dictionary<string, ExerciseDefinition>(StringComparer.Ordinal);
        var jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        foreach (var manifestPath in Directory.EnumerateFiles(root, "exercise.json", SearchOption.AllDirectories))
        {
            if (IsLink(manifestPath))
            {
                throw new InvalidOperationException($"Exercise manifest links are not allowed: '{manifestPath}'.");
            }

            var json = File.ReadAllText(manifestPath);
            var manifest = JsonSerializer.Deserialize<ExerciseManifest>(json, jsonOptions)
                ?? throw new InvalidOperationException($"Exercise manifest is empty: '{manifestPath}'.");

            ValidateManifest(manifest, manifestPath);

            if (!definitions.TryAdd(manifest.Id, new ExerciseDefinition
            {
                Manifest = manifest,
                ManifestPath = manifestPath,
                ExerciseRoot = Path.GetDirectoryName(manifestPath)!,
                EditableFiles = manifest.Files
                    .Where(file => file.Editable)
                    .ToDictionary(file => file.Path, StringComparer.Ordinal),
                EvidenceByTestMethod = manifest.Evidence
                    .ToDictionary(evidence => evidence.TestMethod, StringComparer.Ordinal)
            }))
            {
                throw new InvalidOperationException($"Duplicate exercise ID '{manifest.Id}'.");
            }

            logger.LogInformation("Loaded exercise manifest {ExerciseId} from {ManifestPath}.", manifest.Id, manifestPath);
        }

        return definitions;
    }

    private static void ValidateManifest(ExerciseManifest manifest, string manifestPath)
    {
        if (string.IsNullOrWhiteSpace(manifest.Id) || string.IsNullOrWhiteSpace(manifest.Runtime.Profile))
        {
            throw new InvalidOperationException($"Exercise manifest '{manifestPath}' must define an ID and runtime profile.");
        }

        var exerciseRoot = Path.GetDirectoryName(manifestPath)!;
        var editableIds = new HashSet<string>(StringComparer.Ordinal);
        var filePaths = new HashSet<string>(StringComparer.Ordinal);

        foreach (var file in manifest.Files)
        {
            if (string.IsNullOrWhiteSpace(file.Id) || !editableIds.Add(file.Id) || !filePaths.Add(file.Path) ||
                !ExercisePathRules.IsSafeRelativePath(file.Path))
            {
                throw new InvalidOperationException($"Exercise manifest '{manifestPath}' contains invalid or duplicate file metadata.");
            }
        }

        if (manifest.Files.Count(file => file.Editable) == 0)
        {
            throw new InvalidOperationException($"Exercise manifest '{manifestPath}' declares no editable files.");
        }

        if (!ExercisePathRules.IsSafeRelativePath(manifest.TestSuite.Path))
        {
            throw new InvalidOperationException($"Exercise manifest '{manifestPath}' contains an unsafe test path.");
        }

        var testPath = ExercisePathRules.ResolveInside(exerciseRoot, manifest.TestSuite.Path);
        if (ExerciseRuntimeProfiles.IsPython(manifest))
        {
            // Python suites are a directory of trusted pytest files (test_*.py, conftest.py, helpers).
            if (!Directory.Exists(testPath) || IsLink(testPath) ||
                !Directory.EnumerateFiles(testPath, "test_*.py", SearchOption.AllDirectories).Any())
            {
                throw new InvalidOperationException($"Trusted pytest directory is missing, linked or empty: '{testPath}'.");
            }

            foreach (var file in manifest.Files)
            {
                var starterPath = ExercisePathRules.ResolveInside(Path.Combine(exerciseRoot, "starter"), file.Path);
                if (!File.Exists(starterPath) || IsLink(starterPath))
                {
                    throw new InvalidOperationException($"Python exercise '{manifest.Id}' is missing starter file '{file.Path}'.");
                }
            }
        }
        else if (!File.Exists(testPath) || IsLink(testPath))
        {
            throw new InvalidOperationException($"Trusted test file is missing or linked: '{testPath}'.");
        }

        if (manifest.Runtime.Profile.Equals("java-maven", StringComparison.OrdinalIgnoreCase))
        {
            var pomPath = Path.Combine(exerciseRoot, "pom.xml");
            if (!File.Exists(pomPath) || IsLink(pomPath))
            {
                throw new InvalidOperationException($"Java Maven exercise is missing a trusted pom.xml: '{pomPath}'.");
            }
        }

        var evidenceIds = new HashSet<string>(StringComparer.Ordinal);
        var testMethods = new HashSet<string>(StringComparer.Ordinal);
        foreach (var evidence in manifest.Evidence)
        {
            if (string.IsNullOrWhiteSpace(evidence.Id) || string.IsNullOrWhiteSpace(evidence.TestMethod) ||
                !evidenceIds.Add(evidence.Id) || !testMethods.Add(evidence.TestMethod))
            {
                throw new InvalidOperationException($"Exercise manifest '{manifestPath}' contains invalid evidence mappings.");
            }
        }
    }

    private static bool IsLink(string path)
    {
        var info = new FileInfo(path);
        return info.LinkTarget is not null || info.Attributes.HasFlag(FileAttributes.ReparsePoint);
    }
}
