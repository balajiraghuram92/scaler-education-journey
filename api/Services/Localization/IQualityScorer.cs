using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

public sealed record QualityScoreResult(int Score, IReadOnlyList<string> FlaggedIssues);

public interface IQualityScorer
{
    Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct);
}
