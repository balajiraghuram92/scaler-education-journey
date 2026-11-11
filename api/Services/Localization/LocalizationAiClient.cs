using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Localization;

public class LocalizationAiException : Exception
{
    public LocalizationAiException(string message)
        : base(message)
    {
    }

    public LocalizationAiException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}

public sealed record AiGlossaryTermDto(string Source, string Target);

public sealed record OptimizeTranslationResult(
    string OptimizedTranslation,
    bool CacheHit,
    IReadOnlyDictionary<string, bool> Checks,
    int InputTokens,
    int OutputTokens,
    int TokensUsed,
    int LatencyMs,
    bool Fallback);

public sealed record AiQpsScoreResult(
    int? Score,
    IReadOnlyList<string> FlaggedIssues,
    int TokensUsed,
    int LatencyMs,
    bool Fallback);

public sealed record AiCometScoreResult(
    double? Score,
    bool Available,
    int LatencyMs);

public sealed record AiAutoRouteResult(
    bool NeedsReview,
    IReadOnlyList<string> Reasons);

public sealed record AiEvalRunResult(
    int EvalRunId,
    double? AvgCometKiwi,
    double? AvgQpsScore,
    double? GlossaryAdherenceRate,
    double? PlaceholderPreservationRate,
    double? CacheHitRate,
    int? AvgLatencyMs,
    double TotalCostUsd,
    int TokensUsed,
    int FallbackCount,
    string PromptVersion);

/// <summary>
/// Typed HttpClient for the localization-ai Python service (Part F.2 endpoints).
/// House pattern follows LlamaApiClient: options-bound base address and timeout,
/// per-request auth header, logged failures wrapped in a domain exception.
/// Throws NotImplementedException when no base URL is configured so the Phase 3
/// actions keep surfacing HTTP 501; throws LocalizationAiException for any
/// operational failure (transport, timeout, non-success status, bad payload).
/// </summary>
public class LocalizationAiClient
{
    public const string NotConfiguredMessage =
        "The localization-ai service is not configured (LocalizationAi:BaseUrl). " +
        "Configure the AI service base URL to enable MT Optimize, QPS scoring and Auto-Route.";

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly JsonSerializerOptions RequestJsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
    };

    private readonly HttpClient _httpClient;
    private readonly LocalizationAiOptions _options;
    private readonly ILogger<LocalizationAiClient> _logger;

    public LocalizationAiClient(
        HttpClient httpClient,
        IOptions<LocalizationAiOptions> options,
        ILogger<LocalizationAiClient> logger)
    {
        _httpClient = httpClient;
        _options = options.Value;
        _logger = logger;

        if (!string.IsNullOrWhiteSpace(_options.BaseUrl))
        {
            var baseUrl = _options.BaseUrl;
            if (!baseUrl.EndsWith("/"))
            {
                baseUrl += "/";
            }

            _httpClient.BaseAddress = new Uri(baseUrl);
        }

        _httpClient.Timeout = TimeSpan.FromSeconds(_options.TimeoutSeconds > 0 ? _options.TimeoutSeconds : 60);
    }

    public bool IsConfigured => !string.IsNullOrWhiteSpace(_options.BaseUrl);

    public async Task<OptimizeTranslationResult> TranslateAndOptimizeAsync(
        string sourceText,
        string rawMtText,
        string targetLocale,
        string projectSlug,
        IReadOnlyList<AiGlossaryTermDto> glossaryTerms,
        CancellationToken ct = default)
    {
        var body = new
        {
            rawMtText,
            sourceText,
            targetLocale,
            projectSlug,
            glossaryTerms = glossaryTerms ?? Array.Empty<AiGlossaryTermDto>()
        };

        return await PostAsync<OptimizeTranslationResult>("translate-and-optimize", body, ct);
    }

    public async Task<AiQpsScoreResult> ScoreQpsAsync(
        string sourceText,
        string targetText,
        string targetLocale,
        CancellationToken ct = default)
    {
        var body = new { sourceText, targetText, targetLocale };

        return await PostAsync<AiQpsScoreResult>("qps-score", body, ct);
    }

    public async Task<AiCometScoreResult> ScoreCometAsync(
        string sourceText,
        string targetText,
        string targetLocale,
        CancellationToken ct = default)
    {
        var body = new { sourceText, targetText, targetLocale };

        return await PostAsync<AiCometScoreResult>("comet-score", body, ct);
    }

    public async Task<AiAutoRouteResult> AutoRouteAsync(
        int? qpsScore,
        int projectThreshold,
        IReadOnlyDictionary<string, bool>? checks,
        CancellationToken ct = default)
    {
        var body = new { qpsScore, projectThreshold, checks };

        return await PostAsync<AiAutoRouteResult>("auto-route", body, ct);
    }

    public async Task<AiEvalRunResult> RunEvalAsync(
        string projectSlug,
        string pipelineConfig,
        CancellationToken ct = default)
    {
        var body = new { projectSlug, pipelineConfig };

        return await PostAsync<AiEvalRunResult>("run-eval", body, ct);
    }

    private async Task<T> PostAsync<T>(string path, object body, CancellationToken ct)
    {
        if (!IsConfigured)
        {
            throw new NotImplementedException(NotConfiguredMessage);
        }

        var sw = Stopwatch.StartNew();
        using var request = new HttpRequestMessage(HttpMethod.Post, path)
        {
            Content = new StringContent(JsonSerializer.Serialize(body, RequestJsonOptions), Encoding.UTF8, "application/json")
        };

        if (!string.IsNullOrWhiteSpace(_options.SharedSecret))
        {
            request.Headers.Add("x-api-key", _options.SharedSecret);
        }

        try
        {
            using var response = await _httpClient.SendAsync(request, ct);
            sw.Stop();

            var responseJson = await response.Content.ReadAsStringAsync(ct);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError(
                    "localization-ai POST {Path} failed with status {StatusCode}: {Response}",
                    path, response.StatusCode, responseJson);
                throw new LocalizationAiException(
                    $"localization-ai error: {(int)response.StatusCode} {response.ReasonPhrase}");
            }

            try
            {
                var parsed = JsonSerializer.Deserialize<T>(responseJson, JsonOptions);
                if (parsed is null)
                {
                    throw new LocalizationAiException(
                        $"localization-ai POST {path} returned an empty payload.");
                }

                return parsed;
            }
            catch (JsonException ex)
            {
                _logger.LogError(ex, "localization-ai POST {Path} returned an unreadable payload", path);
                throw new LocalizationAiException(
                    $"localization-ai POST {path} returned an unreadable payload.", ex);
            }
        }
        catch (LocalizationAiException)
        {
            throw;
        }
        catch (OperationCanceledException) when (ct.IsCancellationRequested)
        {
            throw;
        }
        catch (Exception ex)
        {
            sw.Stop();
            _logger.LogError(ex, "Exception communicating with localization-ai POST {Path}", path);
            throw new LocalizationAiException($"localization-ai POST {path} failed: {ex.Message}", ex);
        }
    }
}
