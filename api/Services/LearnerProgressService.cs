using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services;

public sealed record LessonPositionRequest(string? SectionId, int? ScrollPercent, int? SecondsDelta);
public sealed record LessonCompletionRequest(bool IsCompleted);
public sealed record ProblemStatusRequest(string Status, bool? SolutionRevealed);

public sealed record LessonProgressDto(
    int LessonId,
    string Status,
    bool IsCompleted,
    DateTime FirstOpenedAt,
    DateTime LastOpenedAt,
    DateTime? CompletedAt,
    string? LastSectionId,
    int ScrollPercent,
    int VisitCount,
    int TimeSpentSeconds);

public sealed record ProblemProgressDto(
    int ProblemId,
    string Status,
    DateTime? SolutionRevealedAt,
    DateTime? SolvedAt,
    DateTime UpdatedAt);

public sealed record ResumeLessonDto(
    int LessonId,
    string Title,
    string FullSlug,
    string CourseSlug,
    string CourseTitle,
    string ModuleSlug,
    string ModuleTitle,
    string Status,
    string? LastSectionId,
    int ScrollPercent,
    DateTime LastOpenedAt);

public sealed record ResumeDto(ResumeLessonDto? LastLesson, ResumeLessonDto? NextLesson);

public sealed record CourseProgressSummaryDto(
    int CourseId,
    string CourseSlug,
    string CourseTitle,
    int TotalLessons,
    int CompletedLessons,
    int InProgressLessons,
    int ProgressPercentage,
    int McqAnswered,
    int McqCorrect,
    int AssignmentsSolved,
    DateTime? LastActivityAt);

public sealed record LearnerSummaryDto(
    int TotalLessonsCompleted,
    int TotalLessonsInProgress,
    int TotalMcqAnswered,
    int TotalMcqCorrect,
    int TotalTimeSpentSeconds,
    int AssignmentsSolved,
    List<CourseProgressSummaryDto> Courses);

public sealed record LessonMcqPerformanceDto(
    int LessonId,
    string LessonTitle,
    string FullSlug,
    int QuestionCount,
    int AnsweredCount,
    int CorrectCount,
    int AccuracyPercentage,
    DateTime? LastAnsweredAt);

public sealed record ActivityEventDto(
    long Id,
    string EventType,
    DateTime OccurredAt,
    int? LessonId,
    string? LessonTitle,
    int? ProblemId,
    string MetadataJson);

/// <summary>
/// Per-learner learning state: lesson reading/completion, assignment status, the
/// activity log, resume pointers and MCQ performance. All reads are keyed by user id,
/// so anonymous readers simply see no progress.
/// </summary>
public class LearnerProgressService
{
    // Re-opening a lesson within this window continues the same visit.
    private static readonly TimeSpan VisitWindow = TimeSpan.FromMinutes(30);
    private const int MaxSecondsPerHeartbeat = 300;

    private readonly StudyTrackerContext _db;
    private readonly ILogger<LearnerProgressService> _logger;

    public LearnerProgressService(StudyTrackerContext db, ILogger<LearnerProgressService> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<HashSet<int>> GetCompletedLessonIdsAsync(int? userId, CancellationToken ct = default)
    {
        if (userId is not int id) return new HashSet<int>();
        var ids = await _db.UserLessonProgress.AsNoTracking()
            .Where(p => p.UserId == id && p.Status == "Completed")
            .Select(p => p.LessonId)
            .ToListAsync(ct);
        return ids.ToHashSet();
    }

    public async Task<Dictionary<int, LessonProgressDto>> GetLessonProgressMapAsync(int? userId, IEnumerable<int>? lessonIds = null, CancellationToken ct = default)
    {
        if (userId is not int id) return new Dictionary<int, LessonProgressDto>();
        var query = _db.UserLessonProgress.AsNoTracking().Where(p => p.UserId == id);
        if (lessonIds != null)
        {
            var idList = lessonIds.ToList();
            query = query.Where(p => idList.Contains(p.LessonId));
        }

        var rows = await query.ToListAsync(ct);
        return rows.ToDictionary(r => r.LessonId, ToDto);
    }

    public async Task<HashSet<int>> GetSolvedProblemIdsAsync(int? userId, CancellationToken ct = default)
    {
        if (userId is not int id) return new HashSet<int>();
        var ids = await _db.UserProblemProgress.AsNoTracking()
            .Where(p => p.UserId == id && p.Status == "Solved")
            .Select(p => p.ProblemId)
            .ToListAsync(ct);
        return ids.ToHashSet();
    }

    public async Task<Dictionary<int, ProblemProgressDto>> GetProblemProgressMapAsync(int? userId, IEnumerable<int> problemIds, CancellationToken ct = default)
    {
        if (userId is not int id) return new Dictionary<int, ProblemProgressDto>();
        var idList = problemIds.ToList();
        var rows = await _db.UserProblemProgress.AsNoTracking()
            .Where(p => p.UserId == id && idList.Contains(p.ProblemId))
            .ToListAsync(ct);
        return rows.ToDictionary(r => r.ProblemId, ToDto);
    }

    /// <summary>Records that the learner opened a lesson (starts or continues a visit).</summary>
    public async Task<LessonProgressDto?> RecordVisitAsync(int userId, int lessonId, CancellationToken ct = default)
    {
        if (!await _db.Lessons.AnyAsync(l => l.Id == lessonId, ct)) return null;

        var now = DateTime.UtcNow;
        var (row, created) = await UpsertLessonRowAsync(userId, lessonId, ct);
        var isNewVisit = created || now - row.LastOpenedAt > VisitWindow;

        if (!created && isNewVisit)
        {
            row.VisitCount += 1;
        }

        row.LastOpenedAt = now;
        row.UpdatedAt = now;

        if (isNewVisit)
        {
            AddActivity(userId, "LessonOpened", lessonId: lessonId, metadata: new { row.VisitCount });
        }

        await SaveWithUniqueRetryAsync(ct);
        return ToDto(row);
    }

    /// <summary>Heartbeat from the reader: where the learner is and how long they stayed.</summary>
    public async Task<LessonProgressDto?> UpdatePositionAsync(int userId, int lessonId, LessonPositionRequest request, CancellationToken ct = default)
    {
        if (!await _db.Lessons.AnyAsync(l => l.Id == lessonId, ct)) return null;

        var now = DateTime.UtcNow;
        var (row, _) = await UpsertLessonRowAsync(userId, lessonId, ct);

        if (!string.IsNullOrWhiteSpace(request.SectionId))
        {
            var section = request.SectionId.Trim();
            row.LastSectionId = section.Length > 160 ? section[..160] : section;
        }

        if (request.ScrollPercent.HasValue)
        {
            row.ScrollPercent = Math.Clamp(request.ScrollPercent.Value, 0, 100);
        }

        if (request.SecondsDelta is int delta && delta > 0)
        {
            row.TimeSpentSeconds += Math.Min(delta, MaxSecondsPerHeartbeat);
        }

        row.LastOpenedAt = now;
        row.UpdatedAt = now;
        await SaveWithUniqueRetryAsync(ct);
        return ToDto(row);
    }

    public async Task<LessonProgressDto?> SetLessonCompletionAsync(int userId, int lessonId, bool isCompleted, CancellationToken ct = default)
    {
        if (!await _db.Lessons.AnyAsync(l => l.Id == lessonId, ct)) return null;

        var now = DateTime.UtcNow;
        var (row, _) = await UpsertLessonRowAsync(userId, lessonId, ct);
        var wasCompleted = row.Status == "Completed";

        row.Status = isCompleted ? "Completed" : "InProgress";
        row.CompletedAt = isCompleted ? (row.CompletedAt ?? now) : null;
        row.UpdatedAt = now;

        if (wasCompleted != isCompleted)
        {
            AddActivity(userId, isCompleted ? "LessonCompleted" : "LessonReopened", lessonId: lessonId);
        }

        await SaveWithUniqueRetryAsync(ct);
        return ToDto(row);
    }

    public async Task<ProblemProgressDto?> SetProblemStatusAsync(int userId, int problemId, ProblemStatusRequest request, CancellationToken ct = default)
    {
        var status = request.Status?.Trim() ?? string.Empty;
        if (status is not ("NotStarted" or "Attempted" or "Solved"))
        {
            throw new ArgumentException("Status must be NotStarted, Attempted or Solved.");
        }

        var problem = await _db.Problems.AsNoTracking().FirstOrDefaultAsync(p => p.Id == problemId, ct);
        if (problem == null) return null;

        var now = DateTime.UtcNow;
        var row = await _db.UserProblemProgress.FirstOrDefaultAsync(p => p.UserId == userId && p.ProblemId == problemId, ct);
        var created = row == null;
        if (row == null)
        {
            row = new UserProblemProgress { UserId = userId, ProblemId = problemId, CreatedAt = now };
            _db.UserProblemProgress.Add(row);
        }

        var previous = row.Status;
        row.Status = status;
        row.SolvedAt = status == "Solved" ? (row.SolvedAt ?? now) : null;
        row.UpdatedAt = now;

        if (request.SolutionRevealed == true && row.SolutionRevealedAt == null)
        {
            row.SolutionRevealedAt = now;
            AddActivity(userId, "SolutionRevealed", lessonId: problem.LessonId, problemId: problemId);
        }

        if (previous != status || created)
        {
            var eventType = status switch
            {
                "Solved" => "ProblemCompleted",
                "Attempted" => "ProblemAttempted",
                _ => "ProblemReopened"
            };
            AddActivity(userId, eventType, lessonId: problem.LessonId, problemId: problemId);
        }

        await SaveWithUniqueRetryAsync(ct);
        return ToDto(row);
    }

    public async Task<ResumeDto> GetResumeAsync(int userId, CancellationToken ct = default)
    {
        var last = await _db.UserLessonProgress.AsNoTracking()
            .Where(p => p.UserId == userId)
            .OrderByDescending(p => p.LastOpenedAt)
            .Include(p => p.Lesson!)
                .ThenInclude(l => l.Module!)
                    .ThenInclude(m => m.Course)
            .FirstOrDefaultAsync(ct);

        if (last?.Lesson?.Module?.Course == null)
        {
            return new ResumeDto(null, null);
        }

        var lastDto = ToResumeDto(last.Lesson, last);

        // Next = first lesson after the last-opened one (in course order) that isn't completed.
        var course = last.Lesson.Module.Course;
        var orderedLessons = await _db.Lessons.AsNoTracking()
            .Include(l => l.Module)
            .Where(l => l.Module != null && l.Module.CourseId == course.Id)
            .OrderBy(l => l.Module!.OrderIndex)
            .ThenBy(l => l.OrderIndex)
            .ToListAsync(ct);

        var completed = await GetCompletedLessonIdsAsync(userId, ct);
        var startIndex = orderedLessons.FindIndex(l => l.Id == last.LessonId);
        var candidates = orderedLessons.Skip(startIndex + 1).Concat(orderedLessons.Take(Math.Max(startIndex, 0)));
        var next = last.Status == "Completed"
            ? candidates.FirstOrDefault(l => !completed.Contains(l.Id))
            : null;

        ResumeLessonDto? nextDto = null;
        if (next != null)
        {
            next.Module!.Course = course;
            nextDto = ToResumeDto(next, null);
        }

        return new ResumeDto(lastDto, nextDto);
    }

    public async Task<LearnerSummaryDto> GetSummaryAsync(int userId, CancellationToken ct = default)
    {
        var courses = await _db.Courses.AsNoTracking()
            .Include(c => c.Modules)
                .ThenInclude(m => m.Lessons)
                    .ThenInclude(l => l.Problems)
            .OrderBy(c => c.OrderIndex)
            .ToListAsync(ct);

        var lessonRows = await _db.UserLessonProgress.AsNoTracking().Where(p => p.UserId == userId).ToListAsync(ct);
        var lessonMap = lessonRows.ToDictionary(r => r.LessonId);
        var solvedProblems = await GetSolvedProblemIdsAsync(userId, ct);

        // Latest attempt per question for this user; a question counts once.
        var latestAttempts = await GetLatestAttemptsAsync(userId, ct);

        var courseDtos = new List<CourseProgressSummaryDto>();
        foreach (var course in courses)
        {
            var lessons = course.Modules.SelectMany(m => m.Lessons).ToList();
            if (lessons.Count == 0) continue;

            var lessonIds = lessons.Select(l => l.Id).ToHashSet();
            var rows = lessonRows.Where(r => lessonIds.Contains(r.LessonId)).ToList();
            var attempts = latestAttempts.Where(a => lessonIds.Contains(a.LessonId)).ToList();
            var completed = rows.Count(r => r.Status == "Completed");
            var lastActivity = rows.Select(r => (DateTime?)r.LastOpenedAt)
                .Concat(attempts.Select(a => (DateTime?)a.AnsweredAt))
                .Max();

            courseDtos.Add(new CourseProgressSummaryDto(
                course.Id,
                course.Slug,
                course.Title,
                lessons.Count,
                completed,
                rows.Count(r => r.Status == "InProgress"),
                (int)Math.Round((double)completed / lessons.Count * 100),
                attempts.Count,
                attempts.Count(a => a.IsCorrect),
                lessons.SelectMany(l => l.Problems).Count(p => solvedProblems.Contains(p.Id)),
                lastActivity));
        }

        return new LearnerSummaryDto(
            lessonRows.Count(r => r.Status == "Completed"),
            lessonRows.Count(r => r.Status == "InProgress"),
            latestAttempts.Count,
            latestAttempts.Count(a => a.IsCorrect),
            lessonRows.Sum(r => r.TimeSpentSeconds),
            solvedProblems.Count,
            courseDtos);
    }

    public async Task<List<LessonMcqPerformanceDto>> GetMcqPerformanceAsync(int userId, string? courseSlug, CancellationToken ct = default)
    {
        var latest = await GetLatestAttemptsAsync(userId, ct);
        if (latest.Count == 0) return new List<LessonMcqPerformanceDto>();

        var lessonIds = latest.Select(a => a.LessonId).Distinct().ToList();
        var lessons = await _db.Lessons.AsNoTracking()
            .Include(l => l.Module!)
                .ThenInclude(m => m.Course)
            .Where(l => lessonIds.Contains(l.Id))
            .ToListAsync(ct);

        var questionCounts = await _db.McqQuestions.AsNoTracking()
            .Where(q => lessonIds.Contains(q.LessonId) && q.IsActive)
            .GroupBy(q => q.LessonId)
            .Select(g => new { LessonId = g.Key, Count = g.Count() })
            .ToDictionaryAsync(x => x.LessonId, x => x.Count, ct);

        return lessons
            .Where(l => string.IsNullOrWhiteSpace(courseSlug) || l.Module?.Course?.Slug == courseSlug)
            .Select(l =>
            {
                var attempts = latest.Where(a => a.LessonId == l.Id).ToList();
                var correct = attempts.Count(a => a.IsCorrect);
                return new LessonMcqPerformanceDto(
                    l.Id,
                    l.Title,
                    $"{l.Module?.Course?.Slug}/{l.Module?.Slug}/{l.Slug}",
                    questionCounts.TryGetValue(l.Id, out var count) ? count : attempts.Count,
                    attempts.Count,
                    correct,
                    attempts.Count == 0 ? 0 : (int)Math.Round((double)correct / attempts.Count * 100),
                    attempts.Max(a => (DateTime?)a.AnsweredAt));
            })
            .OrderBy(x => x.AccuracyPercentage)
            .ThenByDescending(x => x.LastAnsweredAt)
            .ToList();
    }

    public async Task<List<ActivityEventDto>> GetActivityAsync(int userId, int limit, DateTime? before, CancellationToken ct = default)
    {
        var take = Math.Clamp(limit, 1, 200);
        var query = _db.LearningActivities.AsNoTracking()
            .Include(a => a.Lesson)
            .Where(a => a.UserId == userId);

        if (before.HasValue)
        {
            query = query.Where(a => a.OccurredAt < before.Value);
        }

        return await query
            .OrderByDescending(a => a.OccurredAt)
            .Take(take)
            .Select(a => new ActivityEventDto(a.Id, a.EventType, a.OccurredAt, a.LessonId, a.Lesson != null ? a.Lesson.Title : null, a.ProblemId, a.MetadataJson))
            .ToListAsync(ct);
    }

    public void AddActivity(int userId, string eventType, int? lessonId = null, int? problemId = null, object? metadata = null)
    {
        _db.LearningActivities.Add(new LearningActivity
        {
            UserId = userId,
            EventType = eventType,
            LessonId = lessonId,
            ProblemId = problemId,
            CorrelationId = Guid.NewGuid(),
            OccurredAt = DateTime.UtcNow,
            MetadataJson = metadata == null ? "{}" : JsonSerializer.Serialize(metadata)
        });
    }

    /// <summary>For each question the user answered, only their most recent attempt.</summary>
    public async Task<List<LatestAttemptRow>> GetLatestAttemptsAsync(int userId, CancellationToken ct = default)
    {
        var attempts = await (from a in _db.McqAttempts.AsNoTracking()
                              join p in _db.McqPresentations.AsNoTracking() on a.PresentationId equals p.Id
                              join q in _db.McqQuestions.AsNoTracking() on p.QuestionId equals q.Id
                              where p.UserId == userId
                              select new LatestAttemptRow(q.Id, q.LessonId, a.IsCorrect, a.AnsweredAt))
            .ToListAsync(ct);

        // A single learner's attempt history is small; grouping in memory keeps the SQL simple.
        return attempts
            .GroupBy(a => a.QuestionId)
            .Select(g => g.OrderByDescending(a => a.AnsweredAt).First())
            .ToList();
    }

    public sealed record LatestAttemptRow(int QuestionId, int LessonId, bool IsCorrect, DateTime AnsweredAt);

    private async Task<(UserLessonProgress Row, bool Created)> UpsertLessonRowAsync(int userId, int lessonId, CancellationToken ct)
    {
        var row = await _db.UserLessonProgress.FirstOrDefaultAsync(p => p.UserId == userId && p.LessonId == lessonId, ct);
        if (row != null) return (row, false);

        var now = DateTime.UtcNow;
        row = new UserLessonProgress
        {
            UserId = userId,
            LessonId = lessonId,
            Status = "InProgress",
            FirstOpenedAt = now,
            LastOpenedAt = now,
            UpdatedAt = now,
            VisitCount = 1
        };
        _db.UserLessonProgress.Add(row);
        return (row, true);
    }

    private async Task SaveWithUniqueRetryAsync(CancellationToken ct)
    {
        try
        {
            await _db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException ex)
        {
            // Two tabs inserted the same (user, lesson) row at once. The other insert won;
            // drop ours and let the caller's next heartbeat update the existing row.
            _logger.LogInformation(ex, "Concurrent progress insert detected; discarding duplicate row.");
            foreach (var entry in _db.ChangeTracker.Entries().Where(e => e.State == EntityState.Added).ToList())
            {
                entry.State = EntityState.Detached;
            }
        }
    }

    private static ResumeLessonDto ToResumeDto(Lesson lesson, UserLessonProgress? row)
    {
        var module = lesson.Module!;
        var course = module.Course!;
        return new ResumeLessonDto(
            lesson.Id,
            lesson.Title,
            $"{course.Slug}/{module.Slug}/{lesson.Slug}",
            course.Slug,
            course.Title,
            module.Slug,
            module.Title,
            row?.Status ?? "NotStarted",
            row?.LastSectionId,
            row?.ScrollPercent ?? 0,
            row?.LastOpenedAt ?? DateTime.MinValue);
    }

    private static LessonProgressDto ToDto(UserLessonProgress row) => new(
        row.LessonId,
        row.Status,
        row.Status == "Completed",
        row.FirstOpenedAt,
        row.LastOpenedAt,
        row.CompletedAt,
        row.LastSectionId,
        row.ScrollPercent,
        row.VisitCount,
        row.TimeSpentSeconds);

    private static ProblemProgressDto ToDto(UserProblemProgress row) => new(
        row.ProblemId,
        row.Status,
        row.SolutionRevealedAt,
        row.SolvedAt,
        row.UpdatedAt);
}
