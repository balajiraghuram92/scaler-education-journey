using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Services;
using StudyTracker.Api.Services.Auth;

namespace StudyTracker.Api.Endpoints;

/// <summary>
/// The signed-in learner's own state: progress, resume point, assignment status, MCQ
/// performance and activity history. Every route requires authentication and is scoped
/// to the caller — there is no way to read another learner's state here.
/// </summary>
public static class MeEndpoints
{
    public static void MapMeEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/me").RequireAuthorization();

        group.MapGet("/summary", async (ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
            Results.Ok(await progress.GetSummaryAsync(user.UserId!.Value, ct)))
            .WithName("MeSummary");

        group.MapGet("/resume", async (ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
            Results.Ok(await progress.GetResumeAsync(user.UserId!.Value, ct)))
            .WithName("MeResume");

        group.MapGet("/lessons/progress", async (ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
            Results.Ok((await progress.GetLessonProgressMapAsync(user.UserId!.Value, null, ct)).Values))
            .WithName("MeLessonProgressList");

        group.MapPost("/lessons/{lessonId:int}/visit", async (int lessonId, ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
        {
            var result = await progress.RecordVisitAsync(user.UserId!.Value, lessonId, ct);
            return result == null ? LessonNotFound(lessonId) : Results.Ok(result);
        }).WithName("MeRecordLessonVisit");

        group.MapPut("/lessons/{lessonId:int}/position", async (int lessonId, LessonPositionRequest request, ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
        {
            var result = await progress.UpdatePositionAsync(user.UserId!.Value, lessonId, request, ct);
            return result == null ? LessonNotFound(lessonId) : Results.Ok(result);
        }).WithName("MeUpdateLessonPosition");

        group.MapPut("/lessons/{lessonId:int}/completion", async (int lessonId, LessonCompletionRequest request, ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
        {
            var result = await progress.SetLessonCompletionAsync(user.UserId!.Value, lessonId, request.IsCompleted, ct);
            return result == null ? LessonNotFound(lessonId) : Results.Ok(result);
        }).WithName("MeSetLessonCompletion");

        group.MapPut("/problems/{problemId:int}/status", async (int problemId, ProblemStatusRequest request, ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
        {
            try
            {
                var result = await progress.SetProblemStatusAsync(user.UserId!.Value, problemId, request, ct);
                return result == null
                    ? Results.NotFound(new { error = $"Problem {problemId} not found." })
                    : Results.Ok(result);
            }
            catch (ArgumentException ex)
            {
                return Results.BadRequest(new { error = ex.Message });
            }
        }).WithName("MeSetProblemStatus");

        group.MapGet("/mcq-performance", async (string? course, ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
            Results.Ok(await progress.GetMcqPerformanceAsync(user.UserId!.Value, course, ct)))
            .WithName("MeMcqPerformance");

        group.MapGet("/activity", async (int? limit, DateTime? before, ICurrentUser user, LearnerProgressService progress, CancellationToken ct) =>
            Results.Ok(await progress.GetActivityAsync(user.UserId!.Value, limit ?? 50, before, ct)))
            .WithName("MeActivity");
    }

    private static IResult LessonNotFound(int lessonId) =>
        Results.NotFound(new { error = $"Lesson {lessonId} not found." });
}
