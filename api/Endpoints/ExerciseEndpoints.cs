using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Auth;
using StudyTracker.Api.Services.Exercises;

namespace StudyTracker.Api.Endpoints;

public static class ExerciseEndpoints
{
    public static void MapExerciseEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/exercises");

        group.MapGet("/{exerciseId}", GetMetadata)
            .WithName("GetExerciseMetadata");

        group.MapGet("/{exerciseId}/solution", GetSolution)
            .WithName("GetExerciseSolution");

        group.MapPost("/{exerciseId}/run", ExecuteAsync)
            .WithName("RunExercise");

        group.MapPost("/{exerciseId}/check", ExecuteAsync)
            .WithName("CheckExercise");

        // The signed-in learner's saved code and run history for one exercise.
        group.MapGet("/{exerciseId}/workspace", GetWorkspaceStateAsync)
            .WithName("GetExerciseWorkspaceState")
            .RequireAuthorization();

        group.MapPut("/{exerciseId}/draft", SaveDraftAsync)
            .WithName("SaveExerciseDraft")
            .RequireAuthorization();
    }

    private static async Task<IResult> GetWorkspaceStateAsync(
        string exerciseId,
        IExerciseRepository repository,
        ExerciseProgressService progress,
        ICurrentUser currentUser,
        HttpContext httpContext,
        CancellationToken cancellationToken)
    {
        if (repository.GetById(exerciseId) is null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Exercise not found.", "The requested exercise does not exist.");
        }

        return Results.Ok(await progress.GetStateAsync(currentUser.UserId!.Value, exerciseId, cancellationToken));
    }

    private static async Task<IResult> SaveDraftAsync(
        string exerciseId,
        ExerciseDraftRequest request,
        IExerciseRepository repository,
        ExerciseProgressService progress,
        ICurrentUser currentUser,
        IOptions<ExerciseExecutionOptions> options,
        HttpContext httpContext,
        CancellationToken cancellationToken)
    {
        var definition = repository.GetById(exerciseId);
        if (definition is null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Exercise not found.", "The requested exercise does not exist.");
        }

        var files = request?.Files ?? new List<ExerciseDraftFileDto>();
        var totalBytes = files.Sum(f => System.Text.Encoding.UTF8.GetByteCount(f.Content ?? string.Empty));
        if (files.Count == 0 ||
            files.Any(f => f.Path is null || !definition.EditableFiles.ContainsKey(f.Path)) ||
            totalBytes > options.Value.MaxSubmissionBytes)
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid draft.", "Drafts may only contain the exercise's editable files within the size limit.");
        }

        await progress.SaveDraftAsync(currentUser.UserId!.Value, exerciseId, files, cancellationToken);
        return Results.NoContent();
    }

    private static IResult GetMetadata(
        string exerciseId,
        ExerciseMetadataService metadataService,
        HttpContext httpContext)
    {
        try
        {
            return Results.Ok(metadataService.GetById(exerciseId));
        }
        catch (ExerciseNotFoundException)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Exercise not found.", "The requested exercise does not exist.");
        }
        catch (ExerciseInfrastructureException)
        {
            return Problem(httpContext, StatusCodes.Status503ServiceUnavailable, "Exercise metadata unavailable.", "The exercise metadata is temporarily unavailable.");
        }
    }

    private static IResult GetSolution(
        string exerciseId,
        ExerciseSolutionService solutionService,
        HttpContext httpContext)
    {
        try
        {
            return Results.Ok(solutionService.GetById(exerciseId));
        }
        catch (ExerciseNotFoundException)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Exercise not found.", "The requested exercise does not exist.");
        }
        catch (ExerciseSolutionNotFoundException)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Reference solution unavailable.", "This exercise does not include a reference solution.");
        }
        catch (ExerciseInfrastructureException)
        {
            return Problem(httpContext, StatusCodes.Status503ServiceUnavailable, "Reference solution unavailable.", "The reference solution is temporarily unavailable.");
        }
    }

    private static async Task<IResult> ExecuteAsync(
        string exerciseId,
        ExerciseSubmissionRequest request,
        ExerciseService exerciseService,
        ExerciseProgressService progress,
        ICurrentUser currentUser,
        ILoggerFactory loggerFactory,
        HttpContext httpContext,
        CancellationToken cancellationToken)
    {
        try
        {
            var result = await exerciseService.ExecuteAsync(exerciseId, request, cancellationToken);

            if (currentUser.UserId is int userId)
            {
                try
                {
                    await progress.RecordRunAsync(userId, exerciseId, request, result, cancellationToken);
                }
                catch (Exception ex) when (ex is not OperationCanceledException)
                {
                    // Recording history must never hide the learner's test result.
                    loggerFactory.CreateLogger("ExerciseEndpoints").LogWarning(ex, "Failed to record exercise run for {ExerciseId}.", exerciseId);
                }
            }

            return Results.Ok(result);
        }
        catch (ExerciseNotFoundException)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Exercise not found.", "The requested exercise does not exist.");
        }
        catch (ExerciseSubmissionValidationException ex)
        {
            return Results.ValidationProblem(
                ex.Errors
                    .Select((error, index) => new { Key = $"files[{index}]", Error = error })
                    .GroupBy(item => item.Key, StringComparer.Ordinal)
                    .ToDictionary(group => group.Key, group => group.Select(item => item.Error).ToArray(), StringComparer.Ordinal));
        }
        catch (ExerciseConcurrencyLimitException)
        {
            return Problem(httpContext, StatusCodes.Status429TooManyRequests, "Execution limit reached.", "Try the exercise again shortly.");
        }
        catch (ExerciseRunnerUnavailableException)
        {
            return Problem(httpContext, StatusCodes.Status503ServiceUnavailable, "Exercise runner unavailable.", "The exercise execution service is temporarily unavailable.");
        }
        catch (ExerciseInfrastructureException)
        {
            return Problem(httpContext, StatusCodes.Status503ServiceUnavailable, "Exercise execution unavailable.", "The exercise could not be executed by the platform.");
        }
    }

    private static IResult Problem(HttpContext context, int statusCode, string title, string detail)
    {
        return Results.Json(
            new
            {
                type = "https://tools.ietf.org/html/rfc7231",
                title,
                status = statusCode,
                detail,
                instance = context.Request.Path.Value,
                traceId = context.TraceIdentifier
            },
            contentType: "application/problem+json",
            statusCode: statusCode);
    }
}
