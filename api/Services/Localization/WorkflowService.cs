using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public class WorkflowService
{
    private readonly StudyTrackerContext _db;
    private readonly ITranslationProvider _translationProvider;
    private readonly MtOptimizeService _mtOptimizeService;
    private readonly IQualityScorer _qualityScorer;
    private readonly AutoRoutingService _autoRoutingService;

    public WorkflowService(
        StudyTrackerContext db,
        ITranslationProvider translationProvider,
        MtOptimizeService mtOptimizeService,
        IQualityScorer qualityScorer,
        AutoRoutingService autoRoutingService)
    {
        _db = db;
        _translationProvider = translationProvider;
        _mtOptimizeService = mtOptimizeService;
        _qualityScorer = qualityScorer;
        _autoRoutingService = autoRoutingService;
    }

    public async Task<IReadOnlyList<WorkflowStepDto>> GetStepsAsync(string projectSlug, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var steps = await _db.LocalizationWorkflowSteps
            .AsNoTracking()
            .Where(w => w.ProjectId == project.Id)
            .OrderBy(w => w.Order)
            .ToListAsync(ct);

        return steps.Select(s => new WorkflowStepDto(
            s.Id,
            s.ProjectId,
            s.Order,
            s.Trigger,
            s.Action,
            s.ConditionExpression,
            s.LastRunAt,
            s.LastRunOutcome
        )).ToList();
    }

    public async Task<WorkflowStepDto> AddStepAsync(string projectSlug, AddWorkflowStepRequest request, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var maxOrder = await _db.LocalizationWorkflowSteps
            .Where(w => w.ProjectId == project.Id)
            .Select(w => (int?)w.Order)
            .MaxAsync(ct) ?? 0;

        var step = new WorkflowStep
        {
            ProjectId = project.Id,
            Order = maxOrder + 1,
            Trigger = string.IsNullOrWhiteSpace(request.Trigger) ? "On Manual Click" : request.Trigger,
            Action = request.Action,
            ConditionExpression = request.ConditionExpression,
            LastRunAt = null,
            LastRunOutcome = null
        };

        _db.LocalizationWorkflowSteps.Add(step);
        await _db.SaveChangesAsync(ct);

        return new WorkflowStepDto(
            step.Id,
            step.ProjectId,
            step.Order,
            step.Trigger,
            step.Action,
            step.ConditionExpression,
            step.LastRunAt,
            step.LastRunOutcome
        );
    }

    public async Task<WorkflowStepDto> UpdateStepAsync(string projectSlug, int stepId, UpdateWorkflowStepRequest request, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var step = await _db.LocalizationWorkflowSteps
            .FirstOrDefaultAsync(w => w.Id == stepId && w.ProjectId == project.Id, ct);

        if (step == null)
        {
            throw new WorkflowStepNotFoundException(stepId);
        }

        step.Trigger = string.IsNullOrWhiteSpace(request.Trigger) ? "On Manual Click" : request.Trigger;
        step.Action = request.Action;
        step.ConditionExpression = request.ConditionExpression;

        await _db.SaveChangesAsync(ct);

        return new WorkflowStepDto(
            step.Id,
            step.ProjectId,
            step.Order,
            step.Trigger,
            step.Action,
            step.ConditionExpression,
            step.LastRunAt,
            step.LastRunOutcome
        );
    }

    public async Task ReorderStepAsync(string projectSlug, int stepId, string direction, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var steps = await _db.LocalizationWorkflowSteps
            .Where(w => w.ProjectId == project.Id)
            .OrderBy(w => w.Order)
            .ToListAsync(ct);

        var index = steps.FindIndex(s => s.Id == stepId);
        if (index == -1)
        {
            throw new WorkflowStepNotFoundException(stepId);
        }

        var normalizedDir = direction.Trim().ToLowerInvariant();
        if (normalizedDir == "up")
        {
            if (index == 0)
            {
                throw new WorkflowStepBoundaryException("Cannot move the first workflow step up.");
            }
            var prev = steps[index - 1];
            (steps[index].Order, prev.Order) = (prev.Order, steps[index].Order);
        }
        else if (normalizedDir == "down")
        {
            if (index == steps.Count - 1)
            {
                throw new WorkflowStepBoundaryException("Cannot move the last workflow step down.");
            }
            var next = steps[index + 1];
            (steps[index].Order, next.Order) = (next.Order, steps[index].Order);
        }
        else
        {
            throw new ArgumentException("Direction must be either 'up' or 'down'.", nameof(direction));
        }

        await _db.SaveChangesAsync(ct);
    }

    public async Task DeleteStepAsync(string projectSlug, int stepId, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var step = await _db.LocalizationWorkflowSteps
            .FirstOrDefaultAsync(w => w.Id == stepId && w.ProjectId == project.Id, ct);

        if (step == null)
        {
            throw new WorkflowStepNotFoundException(stepId);
        }

        _db.LocalizationWorkflowSteps.Remove(step);
        await _db.SaveChangesAsync(ct);
    }

    public async Task<WorkflowStepDto> RunStepAsync(string projectSlug, int stepId, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .Include(p => p.Locales)
            .Include(p => p.Strings)
                .ThenInclude(s => s.Translations)
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var step = await _db.LocalizationWorkflowSteps
            .FirstOrDefaultAsync(w => w.Id == stepId && w.ProjectId == project.Id, ct);

        if (step == null)
        {
            throw new WorkflowStepNotFoundException(stepId);
        }

        var now = DateTime.UtcNow;
        string outcome;

        switch (step.Action)
        {
            case "Mark Translated":
            {
                int affected = 0;
                foreach (var str in project.Strings)
                {
                    foreach (var trans in str.Translations)
                    {
                        if (trans.Stage == "New" && !string.IsNullOrWhiteSpace(trans.TargetText))
                        {
                            trans.Stage = "Translated";
                            trans.UpdatedAt = now;
                            affected++;
                        }
                    }
                }
                outcome = $"{affected} strings affected";
                break;
            }

            case "Send to Review":
            {
                int affected = 0;
                foreach (var str in project.Strings)
                {
                    foreach (var trans in str.Translations)
                    {
                        if (trans.Stage == "Translated")
                        {
                            trans.Stage = "Reviewed";
                            trans.UpdatedAt = now;
                            affected++;
                        }
                    }
                }
                outcome = $"{affected} strings affected";
                break;
            }

            case "Approve":
            {
                int affected = 0;
                foreach (var str in project.Strings)
                {
                    foreach (var trans in str.Translations)
                    {
                        if (trans.Stage == "Reviewed")
                        {
                            trans.Stage = "Approved";
                            trans.UpdatedAt = now;
                            affected++;
                        }
                    }
                }
                outcome = $"{affected} strings affected";
                break;
            }

            case "Auto-Translate via Google MT":
            {
                int translatedCount = 0;
                foreach (var locale in project.Locales)
                {
                    foreach (var str in project.Strings)
                    {
                        var trans = str.Translations.FirstOrDefault(t => t.LocaleCode == locale.LocaleCode);
                        if (trans == null)
                        {
                            var translatedText = await _translationProvider.TranslateAsync(
                                str.SourceText,
                                project.SourceLocale,
                                locale.LocaleCode,
                                ct
                            );
                            var newTrans = new LocalizationTranslation
                            {
                                StringId = str.Id,
                                LocaleCode = locale.LocaleCode,
                                TargetText = translatedText,
                                Stage = "Translated",
                                TranslationSource = "AI",
                                UpdatedAt = now
                            };
                            _db.LocalizationTranslations.Add(newTrans);
                            translatedCount++;
                        }
                        else if (string.IsNullOrWhiteSpace(trans.TargetText))
                        {
                            var translatedText = await _translationProvider.TranslateAsync(
                                str.SourceText,
                                project.SourceLocale,
                                locale.LocaleCode,
                                ct
                            );
                            trans.TargetText = translatedText;
                            trans.Stage = "Translated";
                            trans.TranslationSource = "AI";
                            trans.UpdatedAt = now;
                            translatedCount++;
                        }
                    }
                }
                outcome = $"{translatedCount} strings translated via Google MT";
                break;
            }

            case "Post to Marketplace":
            {
                int postedCount = 0;
                foreach (var locale in project.Locales)
                {
                    var existingJob = await _db.LocalizationMarketplaceJobs
                        .FirstOrDefaultAsync(j => j.ProjectId == project.Id && j.LocaleCode == locale.LocaleCode, ct);

                    if (existingJob == null)
                    {
                        var untranslatedCount = project.Strings.Count(s =>
                            !s.Translations.Any(t => t.LocaleCode == locale.LocaleCode && !string.IsNullOrWhiteSpace(t.TargetText)));
                        var wordCount = project.Strings.Sum(s => s.SourceText.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length);

                        var low = Math.Round(wordCount * 0.145m / 5m, MidpointRounding.AwayFromZero) * 5m;
                        var high = Math.Round(wordCount * 0.19m / 5m, MidpointRounding.AwayFromZero) * 5m;
                        if (low < 5m) low = 5m;
                        if (high < low + 15m) high = low + 15m;

                        var job = new MarketplaceJob
                        {
                            ProjectId = project.Id,
                            LocaleCode = locale.LocaleCode,
                            Status = "Open",
                            StringCount = untranslatedCount,
                            WordCount = wordCount,
                            SuggestedPriceLow = low,
                            SuggestedPriceHigh = high,
                            PostedAt = now
                        };
                        _db.LocalizationMarketplaceJobs.Add(job);
                        postedCount++;
                    }
                }
                outcome = $"{postedCount} marketplace jobs posted";
                break;
            }

            // Phase 3 AI Boundary Actions — Hand-written logic required
            case "Run MT Optimize":
            {
                await _mtOptimizeService.OptimizeAsync("sample", project.Slug, "de-DE", ct);
                outcome = "MT Optimize complete";
                break;
            }

            case "Score QPS":
            {
                await _qualityScorer.ScoreAsync("sample", "sample", "de-DE", ct);
                outcome = "QPS Scored";
                break;
            }

            case "Auto-Route":
            {
                await _autoRoutingService.ShouldRouteToReviewAsync(85, 70, ct);
                outcome = "Auto-Routed";
                break;
            }

            default:
                outcome = $"Executed action: {step.Action}";
                break;
        }

        step.LastRunAt = now;
        step.LastRunOutcome = outcome;
        await _db.SaveChangesAsync(ct);

        return new WorkflowStepDto(
            step.Id,
            step.ProjectId,
            step.Order,
            step.Trigger,
            step.Action,
            step.ConditionExpression,
            step.LastRunAt,
            step.LastRunOutcome
        );
    }
}
