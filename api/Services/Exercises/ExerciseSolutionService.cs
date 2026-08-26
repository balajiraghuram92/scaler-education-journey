using System.Text;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseSolutionService
{
    private readonly IExerciseRepository _repository;
    private readonly ExerciseExecutionOptions _options;

    public ExerciseSolutionService(
        IExerciseRepository repository,
        IOptions<ExerciseExecutionOptions> options)
    {
        _repository = repository;
        _options = options.Value;
    }

    public ExerciseSolutionResponse GetById(string exerciseId)
    {
        var definition = _repository.GetById(exerciseId)
            ?? throw new ExerciseNotFoundException(exerciseId);

        var files = definition.Manifest.Files
            .Where(file => file.Editable)
            .Select((file, index) => new ExerciseSolutionFileDto(
                file.Id,
                file.Path,
                file.DisplayName,
                definition.Manifest.Language,
                ReadSolutionContent(definition, file),
                index))
            .ToList();

        if (files.Count == 0)
        {
            throw new ExerciseSolutionNotFoundException(exerciseId);
        }

        return new ExerciseSolutionResponse(definition.Manifest.Id, files);
    }

    private string ReadSolutionContent(ExerciseDefinition definition, ExerciseFileManifest file)
    {
        try
        {
            var solutionRoot = ExercisePathRules.ResolveInside(definition.ExerciseRoot, "solution");
            var solutionPath = ExercisePathRules.ResolveInside(solutionRoot, file.Path);

            if (!Directory.Exists(solutionRoot) || !File.Exists(solutionPath) || ContainsLink(solutionRoot, file.Path))
            {
                throw new ExerciseSolutionNotFoundException(definition.Manifest.Id);
            }

            var content = File.ReadAllText(solutionPath);
            if (Encoding.UTF8.GetByteCount(content) > _options.MaxFileBytes)
            {
                throw new ExerciseInfrastructureException("Trusted reference solution exceeds the configured file limit.");
            }

            return content;
        }
        catch (ExerciseSolutionNotFoundException)
        {
            throw;
        }
        catch (ExerciseInfrastructureException)
        {
            throw;
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
            throw new ExerciseInfrastructureException("Trusted reference solution is unavailable.", ex);
        }
    }

    private static bool IsLink(string path)
    {
        var info = new FileInfo(path);
        return info.LinkTarget is not null || info.Attributes.HasFlag(FileAttributes.ReparsePoint);
    }

    private static bool ContainsLink(string root, string relativePath)
    {
        if (IsLink(root)) return true;

        var currentPath = root;
        foreach (var segment in relativePath.Split('/', StringSplitOptions.None))
        {
            currentPath = Path.Combine(currentPath, segment);
            if (IsLink(currentPath)) return true;
        }

        return false;
    }
}
