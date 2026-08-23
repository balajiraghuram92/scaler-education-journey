using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services;

public class ProgressResult
{
    public bool Success { get; set; }
    public string EntityType { get; set; } = string.Empty;
    public int EntityId { get; set; }
    public bool IsCompleted { get; set; }
    public List<int> SynchronizedTaskIds { get; set; } = new();
    public int? SynchronizedLessonId { get; set; }
    public int? SynchronizedProblemId { get; set; }
    public Guid CorrelationId { get; set; }
    public string? Error { get; set; }
}

public class ProgressService
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<ProgressService> _logger;

    public ProgressService(StudyTrackerContext db, ILogger<ProgressService> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<ProgressResult> SetLessonCompletionAsync(int lessonId, bool isCompleted, Guid? correlationId = null)
    {
        var corrId = correlationId ?? Guid.NewGuid();
        using var tx = await _db.Database.BeginTransactionAsync();
        try
        {
            var lesson = await _db.Lessons
                .Include(l => l.LegacyTaskLinks)
                .FirstOrDefaultAsync(l => l.Id == lessonId);

            if (lesson == null)
            {
                return new ProgressResult { Success = false, Error = $"Lesson {lessonId} not found.", CorrelationId = corrId };
            }

            lesson.IsCompleted = isCompleted;
            lesson.UpdatedAt = DateTime.UtcNow;

            var affectedTaskIds = new List<int>();
            // ONLY synchronize legacy tasks if mapping is explicitly Verified
            var verifiedLinks = lesson.LegacyTaskLinks.Where(link => link.MappingStatus == "Verified").ToList();
            foreach (var link in verifiedLinks)
            {
                var task = await _db.Tasks.FindAsync(link.TaskId);
                if (task != null)
                {
                    task.IsCompleted = isCompleted;
                    task.UpdatedAt = DateTime.UtcNow;
                    affectedTaskIds.Add(task.Id);
                }
            }

            // Record LearningActivity with correlation idempotency
            var eventType = isCompleted ? "LessonCompleted" : "LessonReopened";
            var existingActivity = await _db.LearningActivities.FirstOrDefaultAsync(a =>
                a.CorrelationId == corrId && a.EventType == eventType);

            if (existingActivity == null)
            {
                _db.LearningActivities.Add(new LearningActivity
                {
                    EventType = eventType,
                    LessonId = lesson.Id,
                    CorrelationId = corrId,
                    OccurredAt = DateTime.UtcNow,
                    MetadataJson = JsonSerializer.Serialize(new { SynchronizedTasks = affectedTaskIds })
                });
            }

            await _db.SaveChangesAsync();
            await tx.CommitAsync();

            return new ProgressResult
            {
                Success = true,
                EntityType = "Lesson",
                EntityId = lesson.Id,
                IsCompleted = isCompleted,
                SynchronizedTaskIds = affectedTaskIds,
                CorrelationId = corrId
            };
        }
        catch (Exception ex)
        {
            await tx.RollbackAsync();
            _logger.LogError(ex, "Failed to set Lesson {LessonId} completion atomically (Correlation: {CorrelationId}).", lessonId, corrId);
            return new ProgressResult
            {
                Success = false,
                EntityType = "Lesson",
                EntityId = lessonId,
                CorrelationId = corrId,
                Error = "An error occurred while updating lesson progress. Please refer to traceId for support."
            };
        }
    }

    public async Task<ProgressResult> SetProblemCompletionAsync(int problemId, bool isCompleted, Guid? correlationId = null)
    {
        var corrId = correlationId ?? Guid.NewGuid();
        using var tx = await _db.Database.BeginTransactionAsync();
        try
        {
            var problem = await _db.Problems
                .Include(p => p.LegacyTaskLinks)
                .FirstOrDefaultAsync(p => p.Id == problemId);

            if (problem == null)
            {
                return new ProgressResult { Success = false, Error = $"Problem {problemId} not found.", CorrelationId = corrId };
            }

            problem.IsCompleted = isCompleted;
            problem.UpdatedAt = DateTime.UtcNow;

            var affectedTaskIds = new List<int>();
            // ONLY synchronize legacy tasks if mapping is explicitly Verified
            var verifiedLinks = problem.LegacyTaskLinks.Where(link => link.MappingStatus == "Verified").ToList();
            foreach (var link in verifiedLinks)
            {
                var task = await _db.Tasks.FindAsync(link.TaskId);
                if (task != null)
                {
                    task.IsCompleted = isCompleted;
                    task.UpdatedAt = DateTime.UtcNow;
                    affectedTaskIds.Add(task.Id);
                }
            }

            var eventType = isCompleted ? "ProblemCompleted" : "ProblemReopened";
            var existingActivity = await _db.LearningActivities.FirstOrDefaultAsync(a =>
                a.CorrelationId == corrId && a.EventType == eventType);

            if (existingActivity == null)
            {
                _db.LearningActivities.Add(new LearningActivity
                {
                    EventType = eventType,
                    ProblemId = problem.Id,
                    CorrelationId = corrId,
                    OccurredAt = DateTime.UtcNow,
                    MetadataJson = JsonSerializer.Serialize(new { SynchronizedTasks = affectedTaskIds })
                });
            }

            await _db.SaveChangesAsync();
            await tx.CommitAsync();

            return new ProgressResult
            {
                Success = true,
                EntityType = "Problem",
                EntityId = problem.Id,
                IsCompleted = isCompleted,
                SynchronizedTaskIds = affectedTaskIds,
                CorrelationId = corrId
            };
        }
        catch (Exception ex)
        {
            await tx.RollbackAsync();
            _logger.LogError(ex, "Failed to set Problem {ProblemId} completion atomically (Correlation: {CorrelationId}).", problemId, corrId);
            return new ProgressResult
            {
                Success = false,
                EntityType = "Problem",
                EntityId = problemId,
                CorrelationId = corrId,
                Error = "An error occurred while updating problem progress. Please refer to traceId for support."
            };
        }
    }

    public async Task<ProgressResult> SetTaskCompletionAsync(int taskId, bool isCompleted, Guid? correlationId = null)
    {
        var corrId = correlationId ?? Guid.NewGuid();
        using var tx = await _db.Database.BeginTransactionAsync();
        try
        {
            var task = await _db.Tasks
                .Include(t => t.ContentLink)
                .FirstOrDefaultAsync(t => t.Id == taskId);

            if (task == null)
            {
                return new ProgressResult { Success = false, Error = $"Task {taskId} not found.", CorrelationId = corrId };
            }

            task.IsCompleted = isCompleted;
            task.UpdatedAt = DateTime.UtcNow;

            int? mappedLessonId = null;
            int? mappedProblemId = null;

            // ONLY synchronize canonical entities if mapping is explicitly Verified
            if (task.ContentLink != null && task.ContentLink.MappingStatus == "Verified")
            {
                if (task.ContentLink.LessonId.HasValue)
                {
                    var lesson = await _db.Lessons.FindAsync(task.ContentLink.LessonId.Value);
                    if (lesson != null)
                    {
                        lesson.IsCompleted = isCompleted;
                        lesson.UpdatedAt = DateTime.UtcNow;
                        mappedLessonId = lesson.Id;
                    }
                }

                if (task.ContentLink.ProblemId.HasValue)
                {
                    var problem = await _db.Problems.FindAsync(task.ContentLink.ProblemId.Value);
                    if (problem != null)
                    {
                        problem.IsCompleted = isCompleted;
                        problem.UpdatedAt = DateTime.UtcNow;
                        mappedProblemId = problem.Id;
                    }
                }
            }

            var eventType = isCompleted ? "TaskCompleted" : "TaskReopened";
            var existingActivity = await _db.LearningActivities.FirstOrDefaultAsync(a =>
                a.CorrelationId == corrId && a.EventType == eventType);

            if (existingActivity == null)
            {
                _db.LearningActivities.Add(new LearningActivity
                {
                    EventType = eventType,
                    TaskId = task.Id,
                    LessonId = mappedLessonId,
                    ProblemId = mappedProblemId,
                    CorrelationId = corrId,
                    OccurredAt = DateTime.UtcNow
                });
            }

            await _db.SaveChangesAsync();
            await tx.CommitAsync();

            return new ProgressResult
            {
                Success = true,
                EntityType = "StudyTask",
                EntityId = task.Id,
                IsCompleted = isCompleted,
                SynchronizedLessonId = mappedLessonId,
                SynchronizedProblemId = mappedProblemId,
                CorrelationId = corrId
            };
        }
        catch (Exception ex)
        {
            await tx.RollbackAsync();
            _logger.LogError(ex, "Failed to set Task {TaskId} completion atomically (Correlation: {CorrelationId}).", taskId, corrId);
            return new ProgressResult
            {
                Success = false,
                EntityType = "StudyTask",
                EntityId = taskId,
                CorrelationId = corrId,
                Error = "An error occurred while updating task progress. Please refer to traceId for support."
            };
        }
    }
}
