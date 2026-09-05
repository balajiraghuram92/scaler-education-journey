using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

public interface ITranslationProvider
{
    Task<string> TranslateAsync(string sourceText, string sourceLocale, string targetLocale, CancellationToken ct);
}
