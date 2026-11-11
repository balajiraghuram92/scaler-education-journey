using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

public sealed record QualityScoreResult(int Score, IReadOnlyList<string> FlaggedIssues);

public interface IQualityScorer
{
    /// <summary>True when this scorer can score (the AI service it needs is configured).</summary>
    bool IsConfigured { get; }

    Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct);
}
