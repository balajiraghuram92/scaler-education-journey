using System;
using System.Text.Json;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Services;

namespace StudyTracker.Api.Endpoints;

public static class V2Endpoints
{
    public static void MapV2Endpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v2");

        // 1. Learning Paths
        group.MapGet("/learning-paths", async (LearningPathQueryService queryService) =>
        {
            var paths = await queryService.GetAllLearningPathsAsync();
            return Results.Ok(paths);
        }).WithName("V2GetLearningPaths");

        group.MapGet("/learning-paths/{slug}", async (string slug, LearningPathQueryService queryService) =>
        {
            var path = await queryService.GetLearningPathBySlugAsync(slug);
            return path == null ? Results.NotFound(new { error = $"Learning path '{slug}' not found." }) : Results.Ok(path);
        }).WithName("V2GetLearningPathBySlug");

        // 2. Knowledge Atlas
        group.MapGet("/knowledge-atlas", async (AtlasQueryService atlasService) =>
        {
            var atlas = await atlasService.GetKnowledgeAtlasAsync();
            return Results.Ok(atlas);
        }).WithName("V2GetKnowledgeAtlas");

        // 3. Reading Map
        group.MapGet("/reading-map", async (ReadingMapService readingService) =>
        {
            var readingMap = await readingService.GetReadingMapAsync();
            return Results.Ok(readingMap);
        }).WithName("V2GetReadingMap");

        // 4. Chapter Reader
        group.MapGet("/chapters/{courseSlug}/{moduleSlug}/{lessonSlug}", async (
            string courseSlug, string moduleSlug, string lessonSlug, StudyTrackerContext db) =>
        {
            var lesson = await db.Lessons
                .Include(l => l.Module)
                    .ThenInclude(m => m!.Course)
                .Include(l => l.Problems)
                .Include(l => l.Resources)
                .Include(l => l.CodeComparisons)
                .Include(l => l.Diagrams)
                .Include(l => l.Notes)
                .Include(l => l.ConceptLinks)
                    .ThenInclude(cl => cl.Concept)
                .Include(l => l.OutgoingRelations)
                .FirstOrDefaultAsync(l => l.Slug == lessonSlug && l.Module!.Slug == moduleSlug && l.Module.Course!.Slug == courseSlug);

            if (lesson == null)
            {
                return Results.NotFound(new { error = $"Chapter '{courseSlug}/{moduleSlug}/{lessonSlug}' not found." });
            }

            return Results.Ok(new
            {
                lesson.Id,
                lesson.Slug,
                lesson.Title,
                lesson.Description,
                lesson.LectureNumber,
                lesson.ClassDate,
                lesson.ContentBody,
                lesson.HorstmannRef,
                lesson.EstimatedMinutes,
                lesson.IsCompleted,
                lesson.Difficulty,
                lesson.ContentStatus,
                course = new { lesson.Module?.Course?.Id, lesson.Module?.Course?.Slug, lesson.Module?.Course?.Title },
                module = new { lesson.Module?.Id, lesson.Module?.Slug, lesson.Module?.Title },
                problems = lesson.Problems,
                resources = lesson.Resources,
                codeComparisons = lesson.CodeComparisons,
                diagrams = lesson.Diagrams,
                notes = lesson.Notes,
                concepts = lesson.ConceptLinks.Select(cl => new { cl.Concept?.Id, cl.Concept?.Slug, cl.Concept?.Title }),
                relatedLessons = lesson.OutgoingRelations.Select(r => new { r.TargetTitle, r.TargetSlug, r.RelationshipType, r.ResolutionStatus })
            });
        }).WithName("V2GetChapterDetail");

        // 5. Progress Explicit Update Endpoints
        group.MapPost("/progress/lesson", async (LessonProgressRequest req, ProgressService progressService) =>
        {
            var result = await progressService.SetLessonCompletionAsync(req.LessonId, req.IsCompleted, req.CorrelationId);
            return result.Success ? Results.Ok(result) : Results.BadRequest(result);
        }).WithName("V2SetLessonProgress");

        group.MapPost("/progress/problem", async (ProblemProgressRequest req, ProgressService progressService) =>
        {
            var result = await progressService.SetProblemCompletionAsync(req.ProblemId, req.IsCompleted, req.CorrelationId);
            return result.Success ? Results.Ok(result) : Results.BadRequest(result);
        }).WithName("V2SetProblemProgress");

        group.MapPost("/progress/task", async (TaskProgressRequest req, ProgressService progressService) =>
        {
            var result = await progressService.SetTaskCompletionAsync(req.TaskId, req.IsCompleted, req.CorrelationId);
            return result.Success ? Results.Ok(result) : Results.BadRequest(result);
        }).WithName("V2SetTaskProgress");

        // 6. Dynamic Practice Questions (MCQs)
        group.MapGet("/practice-questions/{courseSlug}/{moduleSlug}/{lessonSlug}", async (
            string courseSlug,
            string moduleSlug,
            string lessonSlug,
            HttpContext httpContext,
            McqService mcqService) =>
        {
            var sub = httpContext.User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            int? userId = int.TryParse(sub, out var parsedId) ? parsedId : null;

            var questions = await mcqService.GetPracticeQuestionsAsync(courseSlug, moduleSlug, lessonSlug, userId);
            return Results.Ok(questions);
        }).WithName("V2GetPracticeQuestions");

        group.MapPost("/practice-questions/{presentationId:guid}/attempts", async (
            Guid presentationId,
            McqAttemptRequest req,
            McqService mcqService) =>
        {
            if (string.IsNullOrWhiteSpace(req?.SelectedOptionKey))
            {
                return Results.BadRequest(new { error = "selectedOptionKey is required." });
            }

            try
            {
                var result = await mcqService.RecordAttemptAsync(presentationId, req.SelectedOptionKey);
                return Results.Ok(result);
            }
            catch (KeyNotFoundException ex)
            {
                return Results.NotFound(new { error = ex.Message });
            }
        }).WithName("V2RecordPracticeAttempt");
    }
}

public record LessonProgressRequest(int LessonId, bool IsCompleted, Guid? CorrelationId = null);
public record ProblemProgressRequest(int ProblemId, bool IsCompleted, Guid? CorrelationId = null);
public record TaskProgressRequest(int TaskId, bool IsCompleted, Guid? CorrelationId = null);
