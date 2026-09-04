namespace StudyTracker.Api.Options;

public sealed class LlamaApiOptions
{
    public const string SectionName = "LlamaApi";

    public string ApiKey { get; set; } = string.Empty;

    public string BaseUrl { get; set; } = "https://api.llama.com/v1/";

    // Current model ID placeholder — MUST be confirmed against current Meta Llama API documentation before production deployment
    public string Model { get; set; } = "Llama-4-Maverick-17B-128E-Instruct-FP8";

    public int TimeoutSeconds { get; set; } = 30;

    public int MaxHistoryMessages { get; set; } = 10;

    public int MaxContextCharacters { get; set; } = 6000;

    // MUST be set from https://llama.developer.meta.com/docs/ pricing page before production use — a 0 here means the cost tracker will under-report spend.
    public decimal PricePerMillionInputTokensUsd { get; set; } = 0m;

    // MUST be set from https://llama.developer.meta.com/docs/ pricing page before production use — a 0 here means the cost tracker will under-report spend.
    public decimal PricePerMillionOutputTokensUsd { get; set; } = 0m;
}
