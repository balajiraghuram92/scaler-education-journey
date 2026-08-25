using System.Text;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Exercises;

public sealed class ExerciseSubmissionValidator
{
    private readonly ExerciseExecutionOptions _options;

    public ExerciseSubmissionValidator(IOptions<ExerciseExecutionOptions> options)
    {
        _options = options.Value;
    }

    public IReadOnlyDictionary<string, ExerciseFileSubmission> Validate(
        ExerciseDefinition definition,
        ExerciseSubmissionRequest? request)
    {
        var errors = new List<string>();
        var submitted = new Dictionary<string, ExerciseFileSubmission>(StringComparer.Ordinal);

        if (request?.Files is null || request.Files.Count == 0)
        {
            errors.Add("At least one editable file must be submitted.");
            throw new ExerciseSubmissionValidationException(errors);
        }

        long totalBytes = 0;
        foreach (var file in request.Files)
        {
            if (file is null || string.IsNullOrWhiteSpace(file.Path))
            {
                errors.Add("Every submitted file must have a path.");
                continue;
            }

            if (!ExercisePathRules.IsSafeRelativePath(file.Path))
            {
                errors.Add($"Submitted path '{file.Path}' is not a safe relative path.");
                continue;
            }

            if (!definition.EditableFiles.ContainsKey(file.Path))
            {
                errors.Add($"Submitted path '{file.Path}' is not declared editable by the exercise manifest.");
                continue;
            }

            if (file.Content is null)
            {
                errors.Add($"Submitted file '{file.Path}' must contain text content.");
                continue;
            }

            if (!submitted.TryAdd(file.Path, file))
            {
                errors.Add($"Submitted path '{file.Path}' was provided more than once.");
                continue;
            }

            var fileBytes = Encoding.UTF8.GetByteCount(file.Content);
            if (fileBytes > _options.MaxFileBytes)
            {
                errors.Add($"Submitted file '{file.Path}' exceeds the per-file size limit.");
            }

            totalBytes += fileBytes;
        }

        foreach (var editablePath in definition.EditableFiles.Keys)
        {
            if (!submitted.ContainsKey(editablePath))
            {
                errors.Add($"Editable file '{editablePath}' is missing from the submission.");
            }
        }

        if (totalBytes > _options.MaxSubmissionBytes)
        {
            errors.Add("The submission exceeds the total size limit.");
        }

        if (errors.Count > 0)
        {
            throw new ExerciseSubmissionValidationException(errors);
        }

        return submitted;
    }
}
