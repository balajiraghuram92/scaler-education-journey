using System.Text;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseMetadataService
{
    private readonly IExerciseRepository _repository;
    private readonly ExerciseExecutionOptions _options;

    public ExerciseMetadataService(
        IExerciseRepository repository,
        IOptions<ExerciseExecutionOptions> options)
    {
        _repository = repository;
        _options = options.Value;
    }

    public ExerciseMetadataResponse GetById(string exerciseId)
    {
        var definition = _repository.GetById(exerciseId)
            ?? throw new ExerciseNotFoundException(exerciseId);

        // Python exercises also show provided (read-only) modules the learner builds on.
        var includeProvided = ExerciseRuntimeProfiles.IsPython(definition.Manifest);
        var files = definition.Manifest.Files
            .Where(file => file.Editable || includeProvided)
            .OrderBy(file => file.Editable ? 0 : 1)
            .Select(file => new ExerciseFileMetadataDto(
                file.Id,
                file.Path,
                file.DisplayName,
                file.Editable,
                ReadStarterContent(definition, file)))
            .ToList();

        return new ExerciseMetadataResponse(
            definition.Manifest.Id,
            definition.Manifest.LessonSlug,
            definition.Manifest.Title,
            definition.Manifest.Language,
            definition.Manifest.Difficulty,
            definition.Manifest.EstimatedMinutes,
            definition.Manifest.Instructions,
            files,
            definition.Manifest.Evidence
                .Select(evidence => new ExerciseEvidenceMetadataDto(evidence.Id, evidence.Label))
                .ToList());
    }

    private string ReadStarterContent(ExerciseDefinition definition, ExerciseFileManifest file)
    {
        try
        {
            var starterRoot = ExercisePathRules.ResolveInside(definition.ExerciseRoot, "starter");
            var starterPath = ExercisePathRules.ResolveInside(starterRoot, file.Path);

            if (!File.Exists(starterPath) || IsLink(starterPath))
            {
                throw new ExerciseInfrastructureException("Trusted starter source is unavailable.");
            }

            var content = File.ReadAllText(starterPath);
            if (Encoding.UTF8.GetByteCount(content) > _options.MaxFileBytes)
            {
                throw new ExerciseInfrastructureException("Trusted starter source exceeds the configured file limit.");
            }

            return content;
        }
        catch (ExerciseInfrastructureException)
        {
            throw;
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
            throw new ExerciseInfrastructureException("Trusted starter source is unavailable.", ex);
        }
    }

    private static bool IsLink(string path)
    {
        var info = new FileInfo(path);
        return info.LinkTarget is not null || info.Attributes.HasFlag(FileAttributes.ReparsePoint);
    }
}
