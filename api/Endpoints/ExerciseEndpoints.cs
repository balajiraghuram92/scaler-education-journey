using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services.Exercises;

namespace StudyTracker.Api.Endpoints;

public static class ExerciseEndpoints
{
    public static void MapExerciseEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/exercises");

        group.MapPost("/{exerciseId}/run", ExecuteAsync)
            .WithName("RunExercise");

        group.MapPost("/{exerciseId}/check", ExecuteAsync)
            .WithName("CheckExercise");
    }

    private static async Task<IResult> ExecuteAsync(
        string exerciseId,
        ExerciseSubmissionRequest request,
        ExerciseService exerciseService,
        HttpContext httpContext,
        CancellationToken cancellationToken)
    {
        try
        {
            var result = await exerciseService.ExecuteAsync(exerciseId, request, cancellationToken);
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
