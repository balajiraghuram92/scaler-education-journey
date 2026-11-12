namespace StudyTracker.Api.Options;

public sealed class AzureTranslatorOptions
{
    public const string SectionName = "AzureTranslator";

    public string Endpoint { get; set; } = "https://api.cognitive.microsofttranslator.com";

    public string Key { get; set; } = string.Empty;

    public string Region { get; set; } = string.Empty;
}
