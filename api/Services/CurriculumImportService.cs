using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services.Reconciliation;

namespace StudyTracker.Api.Services;

public class CurriculumImportRequest
{
    public string CourseSlug { get; set; } = string.Empty;
    public string ModuleSlug { get; set; } = string.Empty;
    public string LessonSlug { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string ContentBody { get; set; } = string.Empty;
    public string Difficulty { get; set; } = "Intermediate";
    public string ContentStatus { get; set; } = "Published"; // Outline, Draft, Published, Archived
    public int EstimatedMinutes { get; set; } = 45;
    public List<string> ConceptSlugs { get; set; } = new();
    public List<LessonRelationImportDto> Relations { get; set; } = new();
    public Guid CorrelationId { get; set; } = Guid.NewGuid();
}

public class LessonRelationImportDto
{
    public string TargetTitle { get; set; } = string.Empty;
    public string? TargetSlug { get; set; }
    public string RelationshipType { get; set; } = "Related"; // Prerequisite, Related, Next
}

public class CurriculumImportResult
{
    public bool Success { get; set; }
    public int? LessonId { get; set; }
    public string? CanonicalUrl { get; set; }
    public List<string> UnresolvedRelations { get; set; } = new();
    public string? Error { get; set; }
}

public class CurriculumImportService
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<CurriculumImportService> _logger;

    public CurriculumImportService(StudyTrackerContext db, ILogger<CurriculumImportService> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<CurriculumImportResult> ImportChapterAsync(CurriculumImportRequest request)
    {
        // 1. Validate Input Limits
        if (string.IsNullOrWhiteSpace(request.CourseSlug) || string.IsNullOrWhiteSpace(request.ModuleSlug))
        {
            return new CurriculumImportResult { Success = false, Error = "Explicit CourseSlug and ModuleSlug are required. Silent fallbacks are prohibited." };
        }

        if (string.IsNullOrWhiteSpace(request.Title) || request.Title.Length > 250)
        {
            return new CurriculumImportResult { Success = false, Error = "Lesson Title is required and must not exceed 250 characters." };
        }

        if (request.ContentBody != null && request.ContentBody.Length > 500_000)
        {
            return new CurriculumImportResult { Success = false, Error = "ContentBody exceeds maximum size limit (500 KB)." };
        }

        // 2. Validate Explicit Destination Existence
        var course = await _db.Courses.Include(c => c.Modules).FirstOrDefaultAsync(c => c.Slug == request.CourseSlug);
        if (course == null)
        {
            return new CurriculumImportResult { Success = false, Error = $"Target course '{request.CourseSlug}' does not exist. Create the course first." };
        }

        var module = course.Modules.FirstOrDefault(m => m.Slug == request.ModuleSlug);
        if (module == null)
        {
            return new CurriculumImportResult { Success = false, Error = $"Target module '{request.ModuleSlug}' does not exist in course '{request.CourseSlug}'." };
        }

        var lessonSlug = string.IsNullOrWhiteSpace(request.LessonSlug)
            ? NormalizationHelper.GenerateSlug(request.Title)
            : request.LessonSlug;

        using var tx = await _db.Database.BeginTransactionAsync();
        try
        {
            var lesson = await _db.Lessons
                .Include(l => l.ConceptLinks)
                .Include(l => l.OutgoingRelations)
                .FirstOrDefaultAsync(l => l.ModuleId == module.Id && l.Slug == lessonSlug);

            if (lesson == null)
            {
                lesson = new Lesson
                {
                    ModuleId = module.Id,
                    Slug = lessonSlug,
                    Title = request.Title,
                    Description = request.Description ?? string.Empty,
                    ContentBody = request.ContentBody ?? string.Empty,
                    Difficulty = request.Difficulty ?? "Intermediate",
                    ContentStatus = request.ContentStatus ?? "Published",
                    EstimatedMinutes = request.EstimatedMinutes > 0 ? request.EstimatedMinutes : 45,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                };
                _db.Lessons.Add(lesson);
                await _db.SaveChangesAsync();
            }
            else
            {
                lesson.Title = request.Title;
                lesson.Description = request.Description ?? lesson.Description;
                lesson.ContentBody = request.ContentBody ?? lesson.ContentBody;
                lesson.Difficulty = request.Difficulty ?? lesson.Difficulty;
                lesson.ContentStatus = request.ContentStatus ?? lesson.ContentStatus;
                lesson.EstimatedMinutes = request.EstimatedMinutes > 0 ? request.EstimatedMinutes : lesson.EstimatedMinutes;
                lesson.UpdatedAt = DateTime.UtcNow;
            }

            // Link Concepts
            foreach (var conceptSlug in request.ConceptSlugs)
            {
                var concept = await _db.KnowledgeConcepts.FirstOrDefaultAsync(c => c.Slug == conceptSlug);
                if (concept != null)
                {
                    var existingLink = await _db.LessonConceptLinks.FindAsync(lesson.Id, concept.Id, "Related");
                    if (existingLink == null)
                    {
                        _db.LessonConceptLinks.Add(new LessonConceptLink
                        {
                            LessonId = lesson.Id,
                            ConceptId = concept.Id,
                            RelationshipType = "Related",
                            CreatedAt = DateTime.UtcNow
                        });
                    }
                }
            }

            // Persist Lesson Relations
            var unresolved = new List<string>();
            foreach (var rel in request.Relations)
            {
                var targetLesson = !string.IsNullOrWhiteSpace(rel.TargetSlug)
                    ? await _db.Lessons.FirstOrDefaultAsync(l => l.Slug == rel.TargetSlug)
                    : null;

                var resolutionStatus = targetLesson != null ? "Resolved" : "Unresolved";
                if (targetLesson == null) unresolved.Add(rel.TargetTitle);

                _db.LessonRelations.Add(new LessonRelation
                {
                    SourceLessonId = lesson.Id,
                    TargetLessonId = targetLesson?.Id,
                    TargetTitle = rel.TargetTitle,
                    TargetSlug = rel.TargetSlug,
                    RelationshipType = rel.RelationshipType,
                    ResolutionStatus = resolutionStatus,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                });
            }

            // Record ChapterImported LearningActivity with correlation idempotency
            var existingActivity = await _db.LearningActivities.FirstOrDefaultAsync(a =>
                a.CorrelationId == request.CorrelationId && a.EventType == "ChapterImported");

            if (existingActivity == null)
            {
                _db.LearningActivities.Add(new LearningActivity
                {
                    EventType = "ChapterImported",
                    LessonId = lesson.Id,
                    CorrelationId = request.CorrelationId,
                    OccurredAt = DateTime.UtcNow,
                    MetadataJson = JsonSerializer.Serialize(new { Course = request.CourseSlug, Module = request.ModuleSlug, Lesson = lessonSlug })
                });
            }

            await _db.SaveChangesAsync();
            await tx.CommitAsync();

            return new CurriculumImportResult
            {
                Success = true,
                LessonId = lesson.Id,
                CanonicalUrl = $"/learning-paths/{request.CourseSlug}/{request.ModuleSlug}/{lessonSlug}",
                UnresolvedRelations = unresolved
            };
        }
        catch (Exception ex)
        {
            await tx.RollbackAsync();
            _logger.LogError(ex, "Failed to import chapter into {CourseSlug}/{ModuleSlug} (CorrelationId: {CorrelationId})",
                request.CourseSlug, request.ModuleSlug, request.CorrelationId);
            return new CurriculumImportResult
            {
                Success = false,
                Error = "An internal error occurred while saving the chapter. Please reference the correlation ID for support."
            };
        }
    }
}
