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

public class AzureTranslatorProviderService : ITranslationProvider
{
    private readonly HttpClient _httpClient;
    private readonly AzureTranslatorOptions _options;
    private readonly IWebHostEnvironment _environment;
    private readonly ILogger<AzureTranslatorProviderService> _logger;

    public AzureTranslatorProviderService(
        HttpClient httpClient,
        IOptions<AzureTranslatorOptions> options,
        IWebHostEnvironment environment,
        ILogger<AzureTranslatorProviderService> logger)
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
        if (string.IsNullOrWhiteSpace(_options.Key))
        {
            if (_environment.IsProduction())
            {
                throw new InvalidOperationException("Azure Translator API key is not configured in production environment.");
            }

            _logger.LogWarning("Azure Translator API key not set. Using mock translation in non-production.");
            return $"[MOCK-{targetLocale.ToUpperInvariant()}] {sourceText}";
        }

        try
        {
            var endpoint = _options.Endpoint.TrimEnd('/');
            var url = $"{endpoint}/translate?api-version=3.0&from={Uri.EscapeDataString(sourceLocale)}&to={Uri.EscapeDataString(targetLocale)}";

            using var request = new HttpRequestMessage(HttpMethod.Post, url);
            request.Headers.Add("Ocp-Apim-Subscription-Key", _options.Key);
            if (!string.IsNullOrWhiteSpace(_options.Region))
            {
                request.Headers.Add("Ocp-Apim-Subscription-Region", _options.Region);
            }
            request.Content = JsonContent.Create(new[] { new { Text = sourceText } });

            var response = await _httpClient.SendAsync(request, ct);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadFromJsonAsync<JsonArray>(cancellationToken: ct);
            var translatedText = json?[0]?["translations"]?[0]?["text"]?.GetValue<string>();

            return translatedText ?? $"[MOCK-{targetLocale.ToUpperInvariant()}] {sourceText}";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Azure Translator API call failed for target locale {Locale}", targetLocale);
            if (!_environment.IsProduction())
            {
                return $"[MOCK-{targetLocale.ToUpperInvariant()}] {sourceText}";
            }
            throw;
        }
    }
}
