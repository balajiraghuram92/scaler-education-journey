using System;
using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

/// <summary>
/// HAND-WRITTEN BOUNDARY: prompt construction for the glossary-aware post-edit
/// pass is written by the project owner, not generated. This method must throw
/// until the owner implements it by hand. Do not fill in prompt text, glossary
/// lookup logic, or LLM call plumbing here.
/// </summary>
public class MtOptimizeService
{
    public Task<string> OptimizeAsync(string rawTranslation, string projectSlug, string targetLocale, CancellationToken ct)
    {
        throw new NotImplementedException(
            "MT Optimize prompt construction is a hand-written component per the project's locked AI boundary. " +
            "Implement this method by hand — do not have an LLM generate this logic.");
    }
}
