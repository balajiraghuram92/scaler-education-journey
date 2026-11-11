namespace StudyTracker.Api.Options;

public sealed class LocalizationAiOptions
{
    public const string SectionName = "LocalizationAi";

    /// <summary>Base URL of the localization-ai Python service (e.g. http://localization-ai:8000). Empty means not configured.</summary>
    public string BaseUrl { get; set; } = string.Empty;

    /// <summary>Shared secret sent as the x-api-key header. Must match the service's API_SHARED_SECRET.</summary>
    public string SharedSecret { get; set; } = string.Empty;

    public int TimeoutSeconds { get; set; } = 60;

    /// <summary>Legacy MT cost per source character in USD (e.g. Google's published rate).</summary>
    public decimal LegacyMtPricePerCharUsd { get; set; } = 0m;

    /// <summary>Chat model cost per 1,000 input tokens in USD.</summary>
    public decimal ChatPricePer1kInputTokensUsd { get; set; } = 0m;

    /// <summary>Chat model cost per 1,000 output tokens in USD.</summary>
    public decimal ChatPricePer1kOutputTokensUsd { get; set; } = 0m;
}
