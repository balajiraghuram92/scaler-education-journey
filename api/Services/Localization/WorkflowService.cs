using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Localization;

public static class WorkflowActions
{
    public const string MarkTranslated = "Mark Translated";
    public const string SendToReview = "Send to Review";
    public const string Approve = "Approve";
    public const string AutoTranslateViaAzureTranslator = "Auto-Translate via Azure Translator";
    public const string CreateTranslationJobs = "Create Translation Jobs";
    public const string RunMtOptimize = "Run MT Optimize";
    public const string ScoreQuality = "Score Quality";
    public const string AutoRoute = "Auto-Route";

    public static readonly IReadOnlySet<string> All = new HashSet<string>
    {
        MarkTranslated,
        SendToReview,
        Approve,
        AutoTranslateViaAzureTranslator,
        CreateTranslationJobs,
        RunMtOptimize,
        ScoreQuality,
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
    private readonly TranslationJobService _translationJobService;
    private readonly UsageMeteringService? _usage;

    public WorkflowService(
        StudyTrackerContext db,
        ITranslationProvider translationProvider,
        MtOptimizeService mtOptimizeService,
        IQualityScorer qualityScorer,
        AutoRoutingService autoRoutingService,
        TranslationJobService translationJobService,
        IOptions<LocalizationAiOptions>? aiOptions = null,
        UsageMeteringService? usage = null)
    {
        _db = db;
        _translationProvider = translationProvider;
        _mtOptimizeService = mtOptimizeService;
        _qualityScorer = qualityScorer;
        _autoRoutingService = autoRoutingService;
        _translationJobService = translationJobService;
        _usage = usage;
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

            case WorkflowActions.AutoTranslateViaAzureTranslator:
            {
                if (!project.AiEnabled)
                {
                    throw new LocalizationAiDisabledException(project.Slug);
                }
                var mtBudget = await StartBudgetAsync(project.Id, UsageCapKinds.MachineTranslation, now, ct);
                int translatedCount = 0;
                int skipped = 0;
                foreach (var locale in project.Locales)
                {
                    foreach (var str in project.Strings)
                    {
                        var trans = str.Translations.FirstOrDefault(t => t.LocaleCode == locale.LocaleCode);
                        if (trans == null)
                        {
                            if (mtBudget is not null && !mtBudget.CanSpend(UsageCapKinds.MachineTranslation, str.SourceText.Length))
                            {
                                skipped++;
                                continue;
                            }
                            var translatedText = await _translationProvider.TranslateAsync(
                                str.SourceText,
                                project.SourceLocale,
                                locale.LocaleCode,
                                ct
                            );
                            await RecordUsageAsync(new UsageCallRecord(
                                project.Id, step.Id, UsageMeters.MachineTranslation, UsageOperations.MtDraft,
                                locale.LocaleCode, str.SourceText.Length, null, false, true), now, ct);
                            mtBudget?.Spent(UsageCapKinds.MachineTranslation, str.SourceText.Length);
                            var newTrans = new LocalizationTranslation
                            {
                                StringId = str.Id,
                                LocaleCode = locale.LocaleCode,
                                TargetText = translatedText,
                                RawMtText = translatedText,
                                Stage = "Translated",
                                TranslationSource = "AI",
                                UpdatedAt = now
                            };
                            _db.LocalizationTranslations.Add(newTrans);
                            translatedCount++;
                        }
                        else if (string.IsNullOrWhiteSpace(trans.TargetText))
                        {
                            if (mtBudget is not null && !mtBudget.CanSpend(UsageCapKinds.MachineTranslation, str.SourceText.Length))
                            {
                                skipped++;
                                continue;
                            }
                            var translatedText = await _translationProvider.TranslateAsync(
                                str.SourceText,
                                project.SourceLocale,
                                locale.LocaleCode,
                                ct
                            );
                            await RecordUsageAsync(new UsageCallRecord(
                                project.Id, step.Id, UsageMeters.MachineTranslation, UsageOperations.MtDraft,
                                locale.LocaleCode, str.SourceText.Length, null, false, true), now, ct);
                            mtBudget?.Spent(UsageCapKinds.MachineTranslation, str.SourceText.Length);
                            trans.TargetText = translatedText;
                            trans.RawMtText = translatedText;
                            trans.Stage = "Translated";
                            trans.TranslationSource = "AI";
                            trans.UpdatedAt = now;
                            translatedCount++;
                        }
                    }
                }
                outcome = WithSkippedClause(
                    $"{translatedCount} strings translated via Azure Translator",
                    mtBudget, UsageCapKinds.MachineTranslation, skipped);
                break;
            }

            case WorkflowActions.CreateTranslationJobs:
            {
                int createdCount = 0;
                int skippedCount = 0;
                foreach (var locale in project.Locales)
                {
                    try
                    {
                        await _translationJobService.CreateJobAsync(project.Slug, locale.LocaleCode, ct);
                        createdCount++;
                    }
                    catch (InvalidJobStateException)
                    {
                        skippedCount++;
                    }
                }
                outcome = $"{createdCount} jobs created, {skippedCount} skipped";
                break;
            }

            // Phase 3 AI actions — thin orchestration over the localization-ai service.
            // A per-string AI failure is counted and the run continues; only
            // NotImplementedException (service not configured) aborts into HTTP 501.
            // Each branch checks its service up front so the 501 surfaces even with no eligible strings.
            case WorkflowActions.RunMtOptimize:
            {
                if (!project.AiEnabled)
                {
                    throw new LocalizationAiDisabledException(project.Slug);
                }
                ThrowIfAiNotConfigured(_mtOptimizeService.IsConfigured);
                var llmBudget = await StartBudgetAsync(project.Id, UsageCapKinds.Llm, now, ct);
                var glossary = await _db.LocalizationGlossaryTerms
                    .AsNoTracking()
                    .Where(g => g.ProjectId == project.Id)
                    .ToListAsync(ct);
                int optimizedCount = 0;
                int failedCount = 0;
                int skipped = 0;
                foreach (var str in project.Strings)
                {
                    foreach (var trans in str.Translations)
                    {
                        var rawMt = trans.RawMtText;
                        if (string.IsNullOrWhiteSpace(rawMt))
                        {
                            continue;
                        }
                        if (llmBudget is not null && !llmBudget.CanSpend(UsageCapKinds.Llm, 0))
                        {
                            skipped++;
                            continue;
                        }

                        var terms = glossary
                            .Where(g => g.LocaleCode == trans.LocaleCode)
                            .Select(g => new AiGlossaryTermDto(g.SourceTerm, g.TargetTerm))
                            .ToList();
                        try
                        {
                            var result = await _mtOptimizeService.OptimizeDetailedAsync(
                                str.SourceText,
                                rawMt,
                                project.Slug,
                                trans.LocaleCode,
                                terms,
                                ct);
                            await RecordUsageAsync(new UsageCallRecord(
                                project.Id, step.Id, UsageMeters.LlmOptimize, UsageOperations.MtOptimize,
                                trans.LocaleCode, result.InputTokens, result.OutputTokens, result.CacheHit, true), now, ct);
                            llmBudget?.Spent(UsageCapKinds.Llm, result.CacheHit ? 0 : result.InputTokens + result.OutputTokens);
                            trans.TargetText = result.OptimizedTranslation;
                            trans.UpdatedAt = now;
                            optimizedCount++;
                        }
                        catch (LocalizationAiException)
                        {
                            failedCount++;
                        }
                    }
                }
                outcome = WithSkippedClause(
                    failedCount == 0
                        ? $"{optimizedCount} strings optimized"
                        : $"{optimizedCount} strings optimized, {failedCount} failed",
                    llmBudget, UsageCapKinds.Llm, skipped);
                break;
            }

            case WorkflowActions.ScoreQuality:
            {
                if (!project.AiEnabled)
                {
                    throw new LocalizationAiDisabledException(project.Slug);
                }
                ThrowIfAiNotConfigured(_qualityScorer.IsConfigured);
                var llmBudget = await StartBudgetAsync(project.Id, UsageCapKinds.Llm, now, ct);
                int scoredCount = 0;
                int failedCount = 0;
                int skipped = 0;
                foreach (var str in project.Strings)
                {
                    foreach (var trans in str.Translations)
                    {
                        if (trans.TranslationSource != "AI")
                        {
                            continue;
                        }
                        if (llmBudget is not null && !llmBudget.CanSpend(UsageCapKinds.Llm, 0))
                        {
                            skipped++;
                            continue;
                        }

                        try
                        {
                            var result = await _qualityScorer.ScoreAsync(
                                str.SourceText,
                                trans.TargetText ?? string.Empty,
                                trans.LocaleCode,
                                ct);
                            if (result.Score < 1 || result.Score > 5)
                            {
                                await RecordUsageAsync(new UsageCallRecord(
                                    project.Id, step.Id, UsageMeters.LlmScore, UsageOperations.QpsScore,
                                    trans.LocaleCode, result.InputTokens, result.OutputTokens, false, false), now, ct);
                                llmBudget?.Spent(UsageCapKinds.Llm, result.InputTokens + result.OutputTokens);
                                failedCount++;
                                continue;
                            }
                            await RecordUsageAsync(new UsageCallRecord(
                                project.Id, step.Id, UsageMeters.LlmScore, UsageOperations.QpsScore,
                                trans.LocaleCode, result.InputTokens, result.OutputTokens, false, true), now, ct);
                            llmBudget?.Spent(UsageCapKinds.Llm, result.InputTokens + result.OutputTokens);
                            trans.QpsScore = result.Score;
                            trans.UpdatedAt = now;
                            scoredCount++;
                        }
                        catch (LocalizationAiException ex)
                        {
                            if (ex.InputTokens + ex.OutputTokens > 0)
                            {
                                await RecordUsageAsync(new UsageCallRecord(
                                    project.Id, step.Id, UsageMeters.LlmScore, UsageOperations.QpsScore,
                                    trans.LocaleCode, ex.InputTokens, ex.OutputTokens, false, false), now, ct);
                                llmBudget?.Spent(UsageCapKinds.Llm, ex.InputTokens + ex.OutputTokens);
                            }
                            failedCount++;
                            continue;
                        }

                        var rawMt = trans.RawMtText;
                        if (!string.IsNullOrWhiteSpace(rawMt) && trans.RawMtQpsScore is null)
                        {
                            if (llmBudget is not null && !llmBudget.CanSpend(UsageCapKinds.Llm, 0))
                            {
                                skipped++;
                            }
                            else try
                            {
                                var rawResult = await _qualityScorer.ScoreAsync(
                                    str.SourceText,
                                    rawMt,
                                    trans.LocaleCode,
                                    ct);
                                if (rawResult.Score < 1 || rawResult.Score > 5)
                                {
                                    await RecordUsageAsync(new UsageCallRecord(
                                        project.Id, step.Id, UsageMeters.LlmScore, UsageOperations.QpsScore,
                                        trans.LocaleCode, rawResult.InputTokens, rawResult.OutputTokens, false, false), now, ct);
                                    llmBudget?.Spent(UsageCapKinds.Llm, rawResult.InputTokens + rawResult.OutputTokens);
                                    failedCount++;
                                }
                                else
                                {
                                    await RecordUsageAsync(new UsageCallRecord(
                                        project.Id, step.Id, UsageMeters.LlmScore, UsageOperations.QpsScore,
                                        trans.LocaleCode, rawResult.InputTokens, rawResult.OutputTokens, false, true), now, ct);
                                    llmBudget?.Spent(UsageCapKinds.Llm, rawResult.InputTokens + rawResult.OutputTokens);
                                    trans.RawMtQpsScore = rawResult.Score;
                                }
                            }
                            catch (LocalizationAiException ex)
                            {
                                if (ex.InputTokens + ex.OutputTokens > 0)
                                {
                                    await RecordUsageAsync(new UsageCallRecord(
                                        project.Id, step.Id, UsageMeters.LlmScore, UsageOperations.QpsScore,
                                        trans.LocaleCode, ex.InputTokens, ex.OutputTokens, false, false), now, ct);
                                    llmBudget?.Spent(UsageCapKinds.Llm, ex.InputTokens + ex.OutputTokens);
                                }
                                failedCount++;
                            }
                        }
                    }
                }
                outcome = WithSkippedClause(
                    failedCount == 0
                        ? $"{scoredCount} strings scored"
                        : $"{scoredCount} strings scored, {failedCount} failed",
                    llmBudget, UsageCapKinds.Llm, skipped);
                break;
            }

            case WorkflowActions.AutoRoute:
            {
                if (!project.AiEnabled)
                {
                    throw new LocalizationAiDisabledException(project.Slug);
                }
                ThrowIfAiNotConfigured(_autoRoutingService.IsConfigured);
                int processedCount = 0;
                int flaggedCount = 0;
                int failedCount = 0;
                foreach (var str in project.Strings)
                {
                    foreach (var trans in str.Translations)
                    {
                        if (trans.TranslationSource != "AI" || trans.QpsScore is null)
                        {
                            continue;
                        }

                        try
                        {
                            var needsReview = await _autoRoutingService.ShouldRouteToReviewAsync(
                                trans.QpsScore.Value,
                                project.QpsThreshold,
                                ct);
                            trans.NeedsReview = needsReview;
                            trans.UpdatedAt = now;
                            processedCount++;
                            if (needsReview)
                            {
                                flaggedCount++;
                            }
                        }
                        catch (LocalizationAiException)
                        {
                            failedCount++;
                        }
                    }
                }
                outcome = failedCount == 0
                    ? $"{processedCount} strings processed, {flaggedCount} flagged for review"
                    : $"{processedCount} strings processed, {flaggedCount} flagged for review, {failedCount} failed";
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

    /// <summary>
    /// Fails a Phase 3 AI action up front when the AI service it needs is not
    /// configured, so the step surfaces HTTP 501 regardless of the data.
    /// Call before any loop and before any database write.
    /// </summary>
    private Task RecordUsageAsync(UsageCallRecord call, DateTime occurredAtUtc, CancellationToken ct)
    {
        return _usage is null
            ? Task.CompletedTask
            : _usage.RecordAsync(call, occurredAtUtc, ct);
    }

    private async Task<UsageBudget?> StartBudgetAsync(int projectId, string capKind, DateTime now, CancellationToken ct)
    {
        if (_usage is null)
        {
            return null;
        }

        var budget = await _usage.BeginRunAsync(projectId, now, ct);
        var limit = budget.Limit(capKind);
        if (limit is not null && budget.Used(capKind) >= limit.Value)
        {
            throw new LocalizationUsageCapReachedException(capKind, budget.Used(capKind), limit.Value);
        }

        return budget;
    }

    private static string WithSkippedClause(string outcome, UsageBudget? budget, string capKind, int skipped)
    {
        if (skipped <= 0 || budget is null)
        {
            return outcome;
        }

        return $"{outcome}, {skipped} skipped: monthly {capKind} cap reached ({budget.Used(capKind)} of {budget.Limit(capKind)})";
    }

    private static void ThrowIfAiNotConfigured(bool configured)
    {
        if (!configured)
        {
            throw new NotImplementedException(LocalizationAiClient.NotConfiguredMessage);
        }
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
