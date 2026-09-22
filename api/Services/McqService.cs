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
    public string QuestionText { get; set; } = string.Empty;
    public List<McqOptionPresentationDto> Options { get; set; } = new();
}

public class McqOptionPresentationDto
{
    public string OptionKey { get; set; } = string.Empty;
    public string OptionText { get; set; } = string.Empty;
}

public class McqAttemptResultDto
{
    public bool IsCorrect { get; set; }
    public string CorrectOptionKey { get; set; } = string.Empty;
    public string Explanation { get; set; } = string.Empty;
}

public record McqAttemptRequest(string SelectedOptionKey);

public class McqService
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<McqService> _logger;

    public McqService(StudyTrackerContext db, ILogger<McqService> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<List<McqPresentationDto>> GetPracticeQuestionsAsync(
        string courseSlug,
        string moduleSlug,
        string lessonSlug,
        int? userId)
    {
        var lesson = await _db.Lessons
            .Include(l => l.Module)
                .ThenInclude(m => m!.Course)
            .FirstOrDefaultAsync(l =>
                l.Slug == lessonSlug &&
                l.Module != null && l.Module.Slug == moduleSlug &&
                l.Module.Course != null && l.Module.Course.Slug == courseSlug);

        if (lesson == null)
        {
            _logger.LogWarning(
                "Lesson not found for path {CourseSlug}/{ModuleSlug}/{LessonSlug}",
                courseSlug, moduleSlug, lessonSlug);
            return new List<McqPresentationDto>();
        }

        var questions = await _db.McqQuestions
            .Include(q => q.Options)
            .Where(q => q.LessonId == lesson.Id && q.IsActive)
            .OrderBy(q => q.Id)
            .ToListAsync();

        if (questions.Count == 0)
        {
            return new List<McqPresentationDto>();
        }

        var result = new List<McqPresentationDto>(questions.Count);

        foreach (var question in questions)
        {
            // Shuffles options randomly: Random.Shared.Next()
            var shuffledOptions = question.Options
                .OrderBy(_ => Random.Shared.Next())
                .ToList();

            var shuffledKeys = shuffledOptions
                .Select(o => o.OptionKey)
                .ToList();

            var presentation = new McqPresentation
            {
                Id = Guid.NewGuid(),
                QuestionId = question.Id,
                UserId = userId,
                DisplayedOptionOrder = JsonSerializer.Serialize(shuffledKeys),
                QuestionTextShown = null,
                PresentedAt = DateTime.UtcNow
            };

            _db.McqPresentations.Add(presentation);

            // Options: optionKey and optionText only - NO correctness or explanation!
            result.Add(new McqPresentationDto
            {
                PresentationId = presentation.Id,
                QuestionText = question.QuestionText,
                Options = shuffledOptions.Select(o => new McqOptionPresentationDto
                {
                    OptionKey = o.OptionKey,
                    OptionText = o.OptionText
                }).ToList()
            });
        }

        await _db.SaveChangesAsync();

        return result;
    }

    public async Task<McqAttemptResultDto> RecordAttemptAsync(
        Guid presentationId,
        string selectedOptionKey)
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
                Explanation = question.Explanation
            };
        }

        var trimmedKey = selectedOptionKey?.Trim() ?? string.Empty;
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
                    Explanation = question.Explanation
                };
            }

            throw;
        }

        return new McqAttemptResultDto
        {
            IsCorrect = isCorrect,
            CorrectOptionKey = correctOptionKey,
            Explanation = question.Explanation
        };
    }
}
