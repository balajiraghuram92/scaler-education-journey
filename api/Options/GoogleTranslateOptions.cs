namespace StudyTracker.Api.Options;

public sealed class GoogleTranslateOptions
{
    public const string SectionName = "GoogleTranslate";

    public string ApiKey { get; set; } = string.Empty;
}
