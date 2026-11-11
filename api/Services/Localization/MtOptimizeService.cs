using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

/// <summary>
/// Thin client over the localization-ai /translate-and-optimize endpoint.
/// Contains no prompt, scoring or threshold logic; that stays in the Python service.
/// </summary>
public class MtOptimizeService
{
    private readonly LocalizationAiClient? _client;

    public MtOptimizeService(LocalizationAiClient? client = null)
    {
        _client = client;
    }

    public async Task<string> OptimizeAsync(string rawTranslation, string projectSlug, string targetLocale, CancellationToken ct)
    {
        var result = await OptimizeDetailedAsync(
            rawTranslation,
            rawTranslation,
            projectSlug,
            targetLocale,
            new List<AiGlossaryTermDto>(),
            ct);

        return result.OptimizedTranslation;
    }

    /// <summary>
    /// Full optimize call with source text and applicable glossary terms; returns
    /// the optimized text plus token usage for ledger accounting. Used by WorkflowService.
    /// </summary>
    public async Task<OptimizeTranslationResult> OptimizeDetailedAsync(
        string sourceText,
        string rawTranslation,
        string projectSlug,
        string targetLocale,
        IReadOnlyList<AiGlossaryTermDto> glossaryTerms,
        CancellationToken ct)
    {
        if (_client is null)
        {
            throw new NotImplementedException(LocalizationAiClient.NotConfiguredMessage);
        }

        return await _client.TranslateAndOptimizeAsync(
            sourceText,
            rawTranslation,
            targetLocale,
            projectSlug,
            glossaryTerms,
            ct);
    }
}
