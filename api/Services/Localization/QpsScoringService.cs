using System;
using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

/// <summary>
/// Thin client over the localization-ai /qps-score endpoint.
/// Contains no scoring rubric; that stays in the Python service.
/// Throws LocalizationAiException when the judge falls back without a score.
/// </summary>
public class QpsScoringService : IQualityScorer
{
    private readonly LocalizationAiClient? _client;

    public QpsScoringService(LocalizationAiClient? client = null)
    {
        _client = client;
    }

    /// <summary>
    /// True when a client is present and the AI service base URL is configured.
    /// Lets callers fail up front instead of discovering it per string.
    /// </summary>
    public bool IsConfigured => _client?.IsConfigured == true;

    public async Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct)
    {
        if (_client is null)
        {
            throw new NotImplementedException(LocalizationAiClient.NotConfiguredMessage);
        }

        var response = await _client.ScoreQpsAsync(sourceText, targetText, targetLocale, ct);

        if (response.Score is null)
        {
            throw new LocalizationAiException("The QPS judge fell back without producing a score.")
            {
                InputTokens = response.InputTokens,
                OutputTokens = response.OutputTokens
            };
        }

        return new QualityScoreResult(response.Score.Value, response.FlaggedIssues, response.InputTokens, response.OutputTokens);
    }
}
