using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services;

namespace StudyTracker.Api.Services.Exercises;

public sealed record ExerciseDraftFileDto(string Path, string Content);

public sealed record ExerciseDraftRequest(List<ExerciseDraftFileDto> Files);

public sealed record ExerciseAttemptSummaryDto(
    long Id,
    string Status,
    int TestsTotal,
    int TestsPassed,
    long DurationMilliseconds,
    DateTime SubmittedAt);

public sealed record ExerciseWorkspaceStateDto(
    string ExerciseId,
    IReadOnlyList<ExerciseDraftFileDto> DraftFiles,
    DateTime? DraftUpdatedAt,
    ExerciseAttemptSummaryDto? LastAttempt,
    ExerciseAttemptSummaryDto? BestAttempt,
    int AttemptCount,
    bool Solved);

/// <summary>
/// Persists a signed-in learner's live-exercise work: the latest draft (restored in the editor),
/// every run's result, and auto-marks the matching coding assignment solved on an all-green run.
/// </summary>
public sealed class ExerciseProgressService
{
    private const int MaxAttemptsKept = 50;
    private static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web);

    private readonly StudyTrackerContext _db;
    private readonly LearnerProgressService _progress;
    private readonly ILogger<ExerciseProgressService> _logger;

    public ExerciseProgressService(StudyTrackerContext db, LearnerProgressService progress, ILogger<ExerciseProgressService> logger)
    {
        _db = db;
        _progress = progress;
        _logger = logger;
    }

    public async Task SaveDraftAsync(int userId, string exerciseId, IEnumerable<ExerciseDraftFileDto> files, CancellationToken ct = default)
    {
        var draft = await _db.UserExerciseDrafts.FirstOrDefaultAsync(d => d.UserId == userId && d.ExerciseId == exerciseId, ct);
        if (draft == null)
        {
            draft = new UserExerciseDraft { UserId = userId, ExerciseId = exerciseId };
            _db.UserExerciseDrafts.Add(draft);
        }

        draft.FilesJson = JsonSerializer.Serialize(files.Select(f => new ExerciseDraftFileDto(f.Path, f.Content ?? string.Empty)), Json);
        draft.UpdatedAt = DateTime.UtcNow;
        await SaveIgnoringRaceAsync(ct);
    }

    public async Task RecordRunAsync(int userId, string exerciseId, ExerciseSubmissionRequest request, ExerciseExecutionResponse result, CancellationToken ct = default)
    {
        var files = request.Files.Select(f => new ExerciseDraftFileDto(f.Path, f.Content)).ToList();
        await SaveDraftAsync(userId, exerciseId, files, ct);

        var failing = result.Evidence.Where(e => e.Status != "passed").Select(e => e.Label).Take(10).ToList();
        _db.UserExerciseAttempts.Add(new UserExerciseAttempt
        {
            UserId = userId,
            ExerciseId = exerciseId,
            Status = result.Status,
            TestsTotal = result.Summary.Total,
            TestsPassed = result.Summary.Passed,
            DurationMilliseconds = result.DurationMilliseconds,
            FilesJson = JsonSerializer.Serialize(files, Json),
            SummaryJson = JsonSerializer.Serialize(new { failing, result.Summary.Failed, result.Summary.Errors }, Json),
            SubmittedAt = DateTime.UtcNow
        });

        var problem = await _db.Problems.AsNoTracking().FirstOrDefaultAsync(p => p.Slug == exerciseId, ct);
        _progress.AddActivity(userId, "ExerciseRun", problem?.LessonId, problem?.Id, new
        {
            exerciseId,
            result.Status,
            result.Summary.Total,
            result.Summary.Passed
        });
        await _db.SaveChangesAsync(ct);

        if (problem != null)
        {
            var solved = await _progress.GetSolvedProblemIdsAsync(userId, ct);
            if (result.Passed)
            {
                await _progress.SetProblemStatusAsync(userId, problem.Id, new ProblemStatusRequest("Solved", null), ct);
            }
            else if (!solved.Contains(problem.Id))
            {
                await _progress.SetProblemStatusAsync(userId, problem.Id, new ProblemStatusRequest("Attempted", null), ct);
            }
        }

        await TrimHistoryAsync(userId, exerciseId, ct);
    }

    public async Task<ExerciseWorkspaceStateDto> GetStateAsync(int userId, string exerciseId, CancellationToken ct = default)
    {
        var draft = await _db.UserExerciseDrafts.AsNoTracking()
            .FirstOrDefaultAsync(d => d.UserId == userId && d.ExerciseId == exerciseId, ct);
        var attempts = await _db.UserExerciseAttempts.AsNoTracking()
            .Where(a => a.UserId == userId && a.ExerciseId == exerciseId)
            .OrderByDescending(a => a.SubmittedAt)
            .Select(a => new ExerciseAttemptSummaryDto(a.Id, a.Status, a.TestsTotal, a.TestsPassed, a.DurationMilliseconds, a.SubmittedAt))
            .ToListAsync(ct);

        var best = attempts
            .OrderByDescending(a => a.Status == "success")
            .ThenByDescending(a => a.TestsTotal == 0 ? 0 : (double)a.TestsPassed / a.TestsTotal)
            .ThenBy(a => a.SubmittedAt)
            .FirstOrDefault();

        var draftFiles = draft == null
            ? new List<ExerciseDraftFileDto>()
            : JsonSerializer.Deserialize<List<ExerciseDraftFileDto>>(draft.FilesJson, Json) ?? new List<ExerciseDraftFileDto>();

        return new ExerciseWorkspaceStateDto(
            exerciseId,
            draftFiles,
            draft?.UpdatedAt,
            attempts.FirstOrDefault(),
            best,
            attempts.Count,
            attempts.Any(a => a.Status == "success"));
    }

    private async Task TrimHistoryAsync(int userId, string exerciseId, CancellationToken ct)
    {
        var stale = await _db.UserExerciseAttempts
            .Where(a => a.UserId == userId && a.ExerciseId == exerciseId)
            .OrderByDescending(a => a.SubmittedAt)
            .Skip(MaxAttemptsKept)
            .ToListAsync(ct);

        if (stale.Count == 0) return;
        _db.UserExerciseAttempts.RemoveRange(stale);
        await _db.SaveChangesAsync(ct);
    }

    private async Task SaveIgnoringRaceAsync(CancellationToken ct)
    {
        try
        {
            await _db.SaveChangesAsync(ct);
        }
        catch (DbUpdateException ex)
        {
            // Two tabs created the same (user, exercise) draft at once; the other write won.
            _logger.LogInformation(ex, "Concurrent exercise draft insert; keeping the existing row.");
            foreach (var entry in _db.ChangeTracker.Entries().Where(e => e.State == EntityState.Added).ToList())
            {
                entry.State = EntityState.Detached;
            }
        }
    }
}
