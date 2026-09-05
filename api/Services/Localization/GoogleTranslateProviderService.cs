using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json.Nodes;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Localization;

public class GoogleTranslateProviderService : ITranslationProvider
{
    private readonly HttpClient _httpClient;
    private readonly GoogleTranslateOptions _options;
    private readonly IWebHostEnvironment _environment;
    private readonly ILogger<GoogleTranslateProviderService> _logger;

    public GoogleTranslateProviderService(
        HttpClient httpClient,
        IOptions<GoogleTranslateOptions> options,
        IWebHostEnvironment environment,
        ILogger<GoogleTranslateProviderService> logger)
    {
        _httpClient = httpClient;
        _options = options.Value;
        _environment = environment;
        _logger = logger;
    }

    public async Task<string> TranslateAsync(
        string sourceText,
        string sourceLocale,
        string targetLocale,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(_options.ApiKey))
        {
            if (_environment.IsProduction())
            {
                throw new InvalidOperationException("Google Translate API key is not configured in production environment.");
            }

            _logger.LogWarning("Google Translate API key not set. Using mock translation in non-production.");
            return $"[MOCK-{targetLocale.ToUpperInvariant()}] {sourceText}";
        }

        try
        {
            var targetLang = targetLocale.Split('-')[0];
            var sourceLang = sourceLocale.Split('-')[0];

            var url = $"https://translation.googleapis.com/language/translate/v2?key={Uri.EscapeDataString(_options.ApiKey)}";
            var requestBody = new
            {
                q = new[] { sourceText },
                target = targetLang,
                source = sourceLang,
                format = "text"
            };

            var response = await _httpClient.PostAsJsonAsync(url, requestBody, ct);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadFromJsonAsync<JsonObject>(cancellationToken: ct);
            var translatedText = json?["data"]?["translations"]?[0]?["translatedText"]?.GetValue<string>();

            return translatedText ?? $"[MOCK-{targetLocale.ToUpperInvariant()}] {sourceText}";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Google Translate API call failed for target locale {Locale}", targetLocale);
            if (!_environment.IsProduction())
            {
                return $"[MOCK-{targetLocale.ToUpperInvariant()}] {sourceText}";
            }
            throw;
        }
    }
}
