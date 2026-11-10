using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public static class WorkflowActions
{
    public const string MarkTranslated = "Mark Translated";
    public const string SendToReview = "Send to Review";
    public const string Approve = "Approve";
    public const string AutoTranslateViaGoogleMt = "Auto-Translate via Google MT";
    public const string PostToMarketplace = "Post to Marketplace";
    public const string RunMtOptimize = "Run MT Optimize";
    public const string ScoreQps = "Score QPS";
    public const string AutoRoute = "Auto-Route";

    public static readonly IReadOnlySet<string> All = new HashSet<string>
    {
        MarkTranslated,
        SendToReview,
        Approve,
        AutoTranslateViaGoogleMt,
        PostToMarketplace,
        RunMtOptimize,
        ScoreQps,
        AutoRoute
    };
}

public static class WorkflowTriggers
{
    public const string OnManualClick = "On Manual Click";

    public static readonly IReadOnlySet<string> All = new HashSet<string>
    {
        OnManualClick
    };
}

public class WorkflowService
{
    private readonly StudyTrackerContext _db;
    private readonly ITranslationProvider _translationProvider;
    private readonly MtOptimizeService _mtOptimizeService;
    private readonly IQualityScorer _qualityScorer;
    private readonly AutoRoutingService _autoRoutingService;
    private readonly MarketplaceService _marketplaceService;

    public WorkflowService(
        StudyTrackerContext db,
        ITranslationProvider translationProvider,
        MtOptimizeService mtOptimizeService,
        IQualityScorer qualityScorer,
        AutoRoutingService autoRoutingService,
        MarketplaceService marketplaceService)
    {
        _db = db;
        _translationProvider = translationProvider;
        _mtOptimizeService = mtOptimizeService;
        _qualityScorer = qualityScorer;
        _autoRoutingService = autoRoutingService;
        _marketplaceService = marketplaceService;
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

        ValidateActionAndTrigger(request.Action, request.Trigger);

        var maxOrder = await _db.LocalizationWorkflowSteps
            .Where(w => w.ProjectId == project.Id)
            .Select(w => (int?)w.Order)
            .MaxAsync(ct) ?? 0;

        var step = new WorkflowStep
        {
            ProjectId = project.Id,
            Order = maxOrder + 1,
            Trigger = string.IsNullOrWhiteSpace(request.Trigger) ? WorkflowTriggers.OnManualClick : request.Trigger,
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

        ValidateActionAndTrigger(request.Action, request.Trigger);

        step.Trigger = string.IsNullOrWhiteSpace(request.Trigger) ? WorkflowTriggers.OnManualClick : request.Trigger;
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
            case WorkflowActions.MarkTranslated:
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

            case WorkflowActions.SendToReview:
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

            case WorkflowActions.Approve:
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

            case WorkflowActions.AutoTranslateViaGoogleMt:
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

            case WorkflowActions.PostToMarketplace:
            {
                int postedCount = 0;
                int skippedCount = 0;
                foreach (var locale in project.Locales)
                {
                    try
                    {
                        await _marketplaceService.PostToMarketplaceAsync(project.Slug, locale.LocaleCode, ct);
                        postedCount++;
                    }
                    catch (InvalidJobStateException)
                    {
                        skippedCount++;
                    }
                }
                outcome = $"{postedCount} marketplace jobs posted, {skippedCount} skipped";
                break;
            }

            // Phase 3 AI Boundary Actions — Hand-written logic required
            case WorkflowActions.RunMtOptimize:
            {
                await _mtOptimizeService.OptimizeAsync("sample", project.Slug, "de-DE", ct);
                outcome = "MT Optimize complete";
                break;
            }

            case WorkflowActions.ScoreQps:
            {
                await _qualityScorer.ScoreAsync("sample", "sample", "de-DE", ct);
                outcome = "QPS Scored";
                break;
            }

            case WorkflowActions.AutoRoute:
            {
                await _autoRoutingService.ShouldRouteToReviewAsync(85, 70, ct);
                outcome = "Auto-Routed";
                break;
            }

            default:
                throw new InvalidOperationException($"Unknown workflow action '{step.Action}'.");
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

    private static void ValidateActionAndTrigger(string action, string? trigger)
    {
        if (!WorkflowActions.All.Contains(action))
        {
            throw new ArgumentException($"Unknown workflow action '{action}'.", nameof(action));
        }

        var effectiveTrigger = string.IsNullOrWhiteSpace(trigger) ? WorkflowTriggers.OnManualClick : trigger;
        if (!WorkflowTriggers.All.Contains(effectiveTrigger))
        {
            throw new ArgumentException($"Unknown workflow trigger '{effectiveTrigger}'.", nameof(trigger));
        }
    }
}
