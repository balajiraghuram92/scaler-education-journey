using System;
using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

/// <summary>
/// HAND-WRITTEN BOUNDARY: the QPS/Auto-LQA scoring rubric is hand-written.
/// Implement this method by hand — do not have an LLM generate this logic.
/// </summary>
public class QpsScoringService : IQualityScorer
{
    public Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct)
    {
        throw new NotImplementedException(
            "The QPS/Auto-LQA scoring rubric is hand-written per the project's locked AI boundary. " +
            "Implement this method by hand — do not have an LLM generate this logic.");
    }
}
