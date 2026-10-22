using System;
using System.Linq;
using System.Text.Json;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Services;
using StudyTracker.Api.Services.Auth;

namespace StudyTracker.Api.Endpoints;

public static class V2Endpoints
{
    public static void MapV2Endpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v2");

        // 1. Learning Paths (progress is the caller's own; anonymous readers see none)
        group.MapGet("/learning-paths", async (LearningPathQueryService queryService, ICurrentUser currentUser) =>
        {
            var paths = await queryService.GetAllLearningPathsAsync(currentUser.UserId);
            return Results.Ok(paths);
        }).WithName("V2GetLearningPaths");

        group.MapGet("/learning-paths/{slug}", async (string slug, LearningPathQueryService queryService, ICurrentUser currentUser) =>
        {
            var path = await queryService.GetLearningPathBySlugAsync(slug, currentUser.UserId);
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
            string courseSlug, string moduleSlug, string lessonSlug,
            StudyTrackerContext db, ICurrentUser currentUser, LearnerProgressService progress,
            StudyTracker.Api.Services.Exercises.IExerciseRepository exerciseRepository) =>
        {
            var userId = currentUser.UserId;
            var lesson = await db.Lessons
                .AsNoTracking()
                .Include(l => l.Module)
                    .ThenInclude(m => m!.Course)
                .Include(l => l.Problems.OrderBy(p => p.OrderIndex))
                .Include(l => l.Resources)
                .Include(l => l.CodeComparisons)
                .Include(l => l.Diagrams)
                .Include(l => l.Notes.Where(n => n.UserId == null || n.UserId == userId))
                .Include(l => l.ConceptLinks)
                    .ThenInclude(cl => cl.Concept)
                .Include(l => l.OutgoingRelations)
                .FirstOrDefaultAsync(l => l.Slug == lessonSlug && l.Module!.Slug == moduleSlug && l.Module.Course!.Slug == courseSlug);

            if (lesson == null)
            {
                return Results.NotFound(new { error = $"Chapter '{courseSlug}/{moduleSlug}/{lessonSlug}' not found." });
            }

            // Personal notes written before notes became per-user have no owner; only
            // editorial note types are shared, so hide ownerless personal ones.
            var notes = lesson.Notes
                .Where(n => n.UserId != null || !string.Equals(n.NoteType, "PersonalNote", StringComparison.OrdinalIgnoreCase))
                .OrderBy(n => n.OrderIndex)
                .ToList();

            // Course-wide reading order for previous/next and the in-module sibling list.
            var courseLessons = await db.Lessons.AsNoTracking()
                .Include(l => l.Module)
                .Where(l => l.Module != null && l.Module.CourseId == lesson.Module!.CourseId)
                .OrderBy(l => l.Module!.OrderIndex)
                .ThenBy(l => l.OrderIndex)
                .Select(l => new ChapterNavRow(l.Id, l.Slug, l.Title, l.EstimatedMinutes, l.ModuleId, l.Module!.Slug, l.Module.Title))
                .ToListAsync();

            var progressMap = await progress.GetLessonProgressMapAsync(userId, courseLessons.Select(l => l.Id));
            var problemProgress = await progress.GetProblemProgressMapAsync(userId, lesson.Problems.Select(p => p.Id));

            object ToNav(ChapterNavRow l) => new
            {
                id = l.Id,
                slug = l.Slug,
                fullSlug = $"{courseSlug}/{l.ModuleSlug}/{l.Slug}",
                title = l.Title,
                moduleTitle = l.ModuleTitle,
                readingTimeMinutes = l.EstimatedMinutes,
                isCompleted = progressMap.TryGetValue(l.Id, out var p) && p.IsCompleted
            };

            var index = courseLessons.FindIndex(l => l.Id == lesson.Id);
            var previous = index > 0 ? ToNav(courseLessons[index - 1]) : null;
            var next = index >= 0 && index < courseLessons.Count - 1 ? ToNav(courseLessons[index + 1]) : null;
            var siblings = courseLessons.Where(l => l.ModuleId == lesson.ModuleId).Select(ToNav).ToList();

            progressMap.TryGetValue(lesson.Id, out var myProgress);

            return Results.Ok(new
            {
                lesson.Id,
                lesson.Slug,
                fullSlug = $"{courseSlug}/{moduleSlug}/{lesson.Slug}",
                lesson.Title,
                lesson.Description,
                lesson.LectureNumber,
                lesson.ClassDate,
                lesson.ContentBody,
                lesson.HorstmannRef,
                lesson.EstimatedMinutes,
                IsCompleted = myProgress?.IsCompleted ?? false,
                lesson.Difficulty,
                lesson.ContentStatus,
                userProgress = myProgress,
                course = new { lesson.Module?.Course?.Id, lesson.Module?.Course?.Slug, lesson.Module?.Course?.Title },
                module = new { lesson.Module?.Id, lesson.Module?.Slug, lesson.Module?.Title, lesson.Module?.Badge },
                problems = lesson.Problems.Select(p => new
                {
                    p.Id,
                    p.LessonId,
                    p.Slug,
                    p.Title,
                    p.Difficulty,
                    p.PackageName,
                    p.TestClassName,
                    p.ProblemStatement,
                    p.RequirementsBody,
                    p.WorkedExample,
                    p.Hints,
                    p.Language,
                    p.RunCommand,
                    p.ReferenceSolution,
                    p.SourceType,
                    p.OrderIndex,
                    // Live in-browser exercise (hidden tests) when one exists for this assignment.
                    exerciseId = exerciseRepository.GetById(p.Slug) is null ? null : p.Slug,
                    IsCompleted = problemProgress.TryGetValue(p.Id, out var pp) && pp.Status == "Solved",
                    userStatus = problemProgress.TryGetValue(p.Id, out var ps) ? ps : null
                }),
                resources = lesson.Resources,
                codeComparisons = lesson.CodeComparisons,
                diagrams = lesson.Diagrams,
                notes,
                concepts = lesson.ConceptLinks.Select(cl => new { cl.Concept?.Id, cl.Concept?.Slug, cl.Concept?.Title }),
                relatedLessons = lesson.OutgoingRelations.Select(r => new { r.TargetTitle, r.TargetSlug, r.RelationshipType, r.ResolutionStatus }),
                previousChapter = previous,
                nextChapter = next,
                siblingChapters = siblings
            });
        }).WithName("V2GetChapterDetail");

        // 5. Progress Explicit Update Endpoints (per signed-in learner)
        group.MapPost("/progress/lesson", async (LessonProgressRequest req, ICurrentUser currentUser, LearnerProgressService progress) =>
        {
            var result = await progress.SetLessonCompletionAsync(currentUser.UserId!.Value, req.LessonId, req.IsCompleted);
            return result == null ? Results.NotFound(new { error = $"Lesson {req.LessonId} not found." }) : Results.Ok(result);
        }).WithName("V2SetLessonProgress").RequireAuthorization();

        group.MapPost("/progress/problem", async (ProblemProgressRequest req, ICurrentUser currentUser, LearnerProgressService progress) =>
        {
            var result = await progress.SetProblemStatusAsync(
                currentUser.UserId!.Value,
                req.ProblemId,
                new ProblemStatusRequest(req.IsCompleted ? "Solved" : "Attempted", null));
            return result == null ? Results.NotFound(new { error = $"Problem {req.ProblemId} not found." }) : Results.Ok(result);
        }).WithName("V2SetProblemProgress").RequireAuthorization();

        group.MapPost("/progress/task", async (TaskProgressRequest req, ProgressService progressService) =>
        {
            var result = await progressService.SetTaskCompletionAsync(req.TaskId, req.IsCompleted, req.CorrelationId);
            return result.Success ? Results.Ok(result) : Results.BadRequest(result);
        }).WithName("V2SetTaskProgress").RequireAuthorization();

        // 6. Dynamic Practice Questions (MCQs)
        group.MapGet("/practice-questions/{courseSlug}/{moduleSlug}/{lessonSlug}", async (
            string courseSlug,
            string moduleSlug,
            string lessonSlug,
            ICurrentUser currentUser,
            McqService mcqService) =>
        {
            var questions = await mcqService.GetPracticeQuestionsAsync(courseSlug, moduleSlug, lessonSlug, currentUser.UserId);
            return Results.Ok(questions);
        }).WithName("V2GetPracticeQuestions");

        group.MapPost("/practice-questions/{presentationId:guid}/attempts", async (
            Guid presentationId,
            McqAttemptRequest req,
            ICurrentUser currentUser,
            McqService mcqService) =>
        {
            if (string.IsNullOrWhiteSpace(req?.SelectedOptionKey))
            {
                return Results.BadRequest(new { error = "selectedOptionKey is required." });
            }

            try
            {
                var result = await mcqService.RecordAttemptAsync(presentationId, req.SelectedOptionKey, currentUser.UserId);
                return Results.Ok(result);
            }
            catch (KeyNotFoundException ex)
            {
                return Results.NotFound(new { error = ex.Message });
            }
            catch (McqAccessDeniedException ex)
            {
                return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status403Forbidden);
            }
            catch (ArgumentException ex)
            {
                return Results.BadRequest(new { error = ex.Message });
            }
        }).WithName("V2RecordPracticeAttempt");

        group.MapPost("/practice-questions/{presentationId:guid}/retry", async (
            Guid presentationId,
            ICurrentUser currentUser,
            McqService mcqService) =>
        {
            try
            {
                return Results.Ok(await mcqService.RetryAsync(presentationId, currentUser.UserId));
            }
            catch (KeyNotFoundException ex)
            {
                return Results.NotFound(new { error = ex.Message });
            }
            catch (McqAccessDeniedException ex)
            {
                return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status403Forbidden);
            }
        }).WithName("V2RetryPracticeQuestion");
    }
}

internal sealed record ChapterNavRow(int Id, string Slug, string Title, int EstimatedMinutes, int ModuleId, string ModuleSlug, string ModuleTitle);

public record LessonProgressRequest(int LessonId, bool IsCompleted, Guid? CorrelationId = null);
public record ProblemProgressRequest(int ProblemId, bool IsCompleted, Guid? CorrelationId = null);
public record TaskProgressRequest(int TaskId, bool IsCompleted, Guid? CorrelationId = null);
