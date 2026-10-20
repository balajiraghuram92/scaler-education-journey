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

public class McqPresentationDto
{
    public Guid PresentationId { get; set; }
    public int QuestionId { get; set; }
    public string Category { get; set; } = "Assignment";
    public string SourceType { get; set; } = "FROM_MATERIAL";
    public string QuestionText { get; set; } = string.Empty;
    public List<McqOptionPresentationDto> Options { get; set; } = new();

    // Populated for a signed-in learner who already answered this question.
    public McqPreviousAttemptDto? PreviousAttempt { get; set; }
    public int AttemptCount { get; set; }
}

public class McqOptionPresentationDto
{
    public string OptionKey { get; set; } = string.Empty;
    public string OptionText { get; set; } = string.Empty;
}

public class McqPreviousAttemptDto
{
    public string SelectedOptionKey { get; set; } = string.Empty;
    public bool IsCorrect { get; set; }
    public string CorrectOptionKey { get; set; } = string.Empty;
    public string Explanation { get; set; } = string.Empty;
    public DateTime AnsweredAt { get; set; }
}

public class McqAttemptResultDto
{
    public bool IsCorrect { get; set; }
    public string CorrectOptionKey { get; set; } = string.Empty;
    public string Explanation { get; set; } = string.Empty;
    public string SelectedOptionKey { get; set; } = string.Empty;
    public DateTime AnsweredAt { get; set; }
}

public record McqAttemptRequest(string SelectedOptionKey);

public sealed class McqAccessDeniedException : Exception
{
    public McqAccessDeniedException(string message) : base(message) { }
}

public class McqService
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<McqService> _logger;

    public McqService(StudyTrackerContext db, ILogger<McqService> logger)
    {
        _db = db;
        _logger = logger;
    }

    private static readonly Dictionary<string, string> LessonSlugAliases = new(StringComparer.OrdinalIgnoreCase)
    {
        ["02-oop-classes-objects"] = "02-oop-1-intro-lab",
        ["03-oop2-encapsulation-inheritance"] = "03-oop-2-access-modifiers-encapsulation"
    };

    private static string NormalizeLessonSlug(string slug)
    {
        return LessonSlugAliases.TryGetValue(slug, out var canonical) ? canonical : slug;
    }

    private static readonly Dictionary<string, int> CategoryOrder = new(StringComparer.OrdinalIgnoreCase)
    {
        ["Checkpoint"] = 0,
        ["Assignment"] = 1,
        ["Additional"] = 2
    };

    public async Task<List<McqPresentationDto>> GetPracticeQuestionsAsync(
        string courseSlug,
        string moduleSlug,
        string lessonSlug,
        int? userId)
    {
        var resolvedLessonSlug = NormalizeLessonSlug(lessonSlug);
        var lesson = await _db.Lessons
            .Include(l => l.Module)
                .ThenInclude(m => m!.Course)
            .FirstOrDefaultAsync(l =>
                l.Slug == resolvedLessonSlug &&
                l.Module != null && l.Module.Slug == moduleSlug &&
                l.Module.Course != null && l.Module.Course.Slug == courseSlug);

        if (lesson == null)
        {
            _logger.LogWarning(
                "Lesson not found for path {CourseSlug}/{ModuleSlug}/{LessonSlug}",
                courseSlug, moduleSlug, lessonSlug);
            return new List<McqPresentationDto>();
        }

        var questions = (await _db.McqQuestions
            .Include(q => q.Options)
            .Where(q => q.LessonId == lesson.Id && q.IsActive)
            .OrderBy(q => q.Id)
            .ToListAsync())
            .OrderBy(q => CategoryOrder.TryGetValue(q.Category, out var order) ? order : 9)
            .ThenBy(q => q.Id)
            .ToList();

        if (questions.Count == 0)
        {
            return new List<McqPresentationDto>();
        }

        // A signed-in learner resumes their own presentations: answered ones come back
        // with the recorded result, unanswered ones keep their option order.
        var latestByQuestion = new Dictionary<int, McqPresentation>();
        var attemptCounts = new Dictionary<int, int>();
        if (userId.HasValue)
        {
            var questionIds = questions.Select(q => q.Id).ToList();
            var presentations = await _db.McqPresentations
                .Include(p => p.Attempt)
                .Where(p => p.UserId == userId && questionIds.Contains(p.QuestionId))
                .ToListAsync();

            foreach (var group in presentations.GroupBy(p => p.QuestionId))
            {
                latestByQuestion[group.Key] = group.OrderByDescending(p => p.PresentedAt).First();
                attemptCounts[group.Key] = group.Count(p => p.Attempt != null);
            }
        }

        var result = new List<McqPresentationDto>(questions.Count);
        var created = false;

        foreach (var question in questions)
        {
            latestByQuestion.TryGetValue(question.Id, out var existing);

            McqPresentation presentation;
            List<McqOption> orderedOptions;
            if (existing != null)
            {
                presentation = existing;
                orderedOptions = OrderOptions(question.Options, existing.DisplayedOptionOrder);
            }
            else
            {
                orderedOptions = question.Options.OrderBy(_ => Random.Shared.Next()).ToList();
                presentation = NewPresentation(question.Id, userId, orderedOptions);
                _db.McqPresentations.Add(presentation);
                created = true;
            }

            var dto = ToPresentationDto(question, presentation, orderedOptions);
            dto.AttemptCount = attemptCounts.TryGetValue(question.Id, out var count) ? count : 0;

            if (presentation.Attempt != null)
            {
                dto.PreviousAttempt = new McqPreviousAttemptDto
                {
                    SelectedOptionKey = presentation.Attempt.SelectedOptionKey,
                    IsCorrect = presentation.Attempt.IsCorrect,
                    CorrectOptionKey = question.Options.FirstOrDefault(o => o.IsCorrect)?.OptionKey ?? string.Empty,
                    Explanation = question.Explanation,
                    AnsweredAt = presentation.Attempt.AnsweredAt
                };
            }

            result.Add(dto);
        }

        if (created)
        {
            await _db.SaveChangesAsync();
        }

        return result;
    }

    /// <summary>Starts a fresh, unanswered presentation of the same question ("try again").</summary>
    public async Task<McqPresentationDto> RetryAsync(Guid presentationId, int? userId)
    {
        var previous = await _db.McqPresentations
            .Include(p => p.Question)
                .ThenInclude(q => q!.Options)
            .FirstOrDefaultAsync(p => p.Id == presentationId)
            ?? throw new KeyNotFoundException($"Presentation '{presentationId}' not found.");

        EnsureOwnership(previous, userId);

        var question = previous.Question
            ?? throw new InvalidOperationException($"Question for presentation '{presentationId}' was not found.");

        var orderedOptions = question.Options.OrderBy(_ => Random.Shared.Next()).ToList();
        var presentation = NewPresentation(question.Id, userId ?? previous.UserId, orderedOptions);
        _db.McqPresentations.Add(presentation);
        await _db.SaveChangesAsync();

        var attemptCount = userId.HasValue
            ? await _db.McqAttempts.CountAsync(a => a.Presentation!.QuestionId == question.Id && a.Presentation.UserId == userId)
            : 0;

        var dto = ToPresentationDto(question, presentation, orderedOptions);
        dto.AttemptCount = attemptCount;
        return dto;
    }

    public async Task<McqAttemptResultDto> RecordAttemptAsync(
        Guid presentationId,
        string selectedOptionKey,
        int? userId = null)
    {
        var presentation = await _db.McqPresentations
            .Include(p => p.Question)
                .ThenInclude(q => q!.Options)
            .Include(p => p.Attempt)
            .FirstOrDefaultAsync(p => p.Id == presentationId);

        if (presentation == null)
        {
            throw new KeyNotFoundException($"Presentation '{presentationId}' not found.");
        }

        EnsureOwnership(presentation, userId);

        var question = presentation.Question
            ?? throw new InvalidOperationException($"Question for presentation '{presentationId}' was not found.");

        var correctOption = question.Options.FirstOrDefault(o => o.IsCorrect);
        var correctOptionKey = correctOption?.OptionKey ?? string.Empty;

        // Idempotency: if attempt already exists, return existing result
        if (presentation.Attempt != null)
        {
            return new McqAttemptResultDto
            {
                IsCorrect = presentation.Attempt.IsCorrect,
                CorrectOptionKey = correctOptionKey,
                Explanation = question.Explanation,
                SelectedOptionKey = presentation.Attempt.SelectedOptionKey,
                AnsweredAt = presentation.Attempt.AnsweredAt
            };
        }

        var trimmedKey = selectedOptionKey?.Trim() ?? string.Empty;
        if (!question.Options.Any(o => string.Equals(o.OptionKey, trimmedKey, StringComparison.OrdinalIgnoreCase)))
        {
            throw new ArgumentException($"'{trimmedKey}' is not an option of this question.");
        }

        var isCorrect = !string.IsNullOrEmpty(correctOptionKey) &&
                        string.Equals(correctOptionKey, trimmedKey, StringComparison.OrdinalIgnoreCase);

        var attempt = new McqAttempt
        {
            Id = Guid.NewGuid(),
            PresentationId = presentation.Id,
            SelectedOptionKey = trimmedKey,
            IsCorrect = isCorrect,
            AnsweredAt = DateTime.UtcNow
        };

        _db.McqAttempts.Add(attempt);

        if (presentation.UserId.HasValue)
        {
            _db.LearningActivities.Add(new LearningActivity
            {
                UserId = presentation.UserId,
                EventType = "McqAnswered",
                LessonId = question.LessonId,
                CorrelationId = attempt.Id,
                OccurredAt = attempt.AnsweredAt,
                MetadataJson = JsonSerializer.Serialize(new
                {
                    questionId = question.Id,
                    question.LegacyKey,
                    question.Category,
                    selectedOptionKey = trimmedKey,
                    isCorrect
                })
            });
        }

        try
        {
            await _db.SaveChangesAsync();
        }
        catch (DbUpdateException ex)
        {
            _logger.LogWarning(ex, "Conflict saving attempt for presentation {PresentationId}. Checking for existing attempt.", presentationId);
            var existingAttempt = await _db.McqAttempts
                .AsNoTracking()
                .FirstOrDefaultAsync(a => a.PresentationId == presentationId);

            if (existingAttempt != null)
            {
                return new McqAttemptResultDto
                {
                    IsCorrect = existingAttempt.IsCorrect,
                    CorrectOptionKey = correctOptionKey,
                    Explanation = question.Explanation,
                    SelectedOptionKey = existingAttempt.SelectedOptionKey,
                    AnsweredAt = existingAttempt.AnsweredAt
                };
            }

            throw;
        }

        return new McqAttemptResultDto
        {
            IsCorrect = isCorrect,
            CorrectOptionKey = correctOptionKey,
            Explanation = question.Explanation,
            SelectedOptionKey = trimmedKey,
            AnsweredAt = attempt.AnsweredAt
        };
    }

    // A presentation issued to a signed-in learner can only be answered by that learner.
    private static void EnsureOwnership(McqPresentation presentation, int? userId)
    {
        if (presentation.UserId.HasValue && presentation.UserId != userId)
        {
            throw new McqAccessDeniedException("This question was presented to a different account.");
        }
    }

    private static McqPresentation NewPresentation(int questionId, int? userId, List<McqOption> orderedOptions) => new()
    {
        Id = Guid.NewGuid(),
        QuestionId = questionId,
        UserId = userId,
        DisplayedOptionOrder = JsonSerializer.Serialize(orderedOptions.Select(o => o.OptionKey).ToList()),
        QuestionTextShown = null,
        PresentedAt = DateTime.UtcNow
    };

    private static List<McqOption> OrderOptions(IEnumerable<McqOption> options, string displayedOrderJson)
    {
        var list = options.ToList();
        try
        {
            var order = JsonSerializer.Deserialize<List<string>>(displayedOrderJson) ?? new List<string>();
            var rank = order.Select((key, index) => (key, index)).ToDictionary(x => x.key, x => x.index, StringComparer.OrdinalIgnoreCase);
            return list.OrderBy(o => rank.TryGetValue(o.OptionKey, out var r) ? r : int.MaxValue).ThenBy(o => o.OptionKey).ToList();
        }
        catch (JsonException)
        {
            return list.OrderBy(o => o.OptionKey).ToList();
        }
    }

    // Options: optionKey and optionText only - NO correctness or explanation!
    private static McqPresentationDto ToPresentationDto(McqQuestion question, McqPresentation presentation, List<McqOption> orderedOptions) => new()
    {
        PresentationId = presentation.Id,
        QuestionId = question.Id,
        Category = question.Category,
        SourceType = question.SourceType,
        QuestionText = question.QuestionText,
        Options = orderedOptions.Select(o => new McqOptionPresentationDto
        {
            OptionKey = o.OptionKey,
            OptionText = o.OptionText
        }).ToList()
    };
}
