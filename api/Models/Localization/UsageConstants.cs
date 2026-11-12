namespace StudyTracker.Api.Models.Localization;

public static class UsageMeters
{
    public const string MachineTranslation = "machine-translation";
    public const string LlmOptimize = "llm-optimize";
    public const string LlmScore = "llm-score";
}

public static class UsageOperations
{
    public const string MtDraft = "mt-draft";
    public const string MtOptimize = "mt-optimize";
    public const string QpsScore = "qps-score";
}

public static class UsageUnitKinds
{
    public const string Char = "char";
    public const string InputToken = "input-token";
    public const string OutputToken = "output-token";
}

public static class UsageCapKinds
{
    public const string MachineTranslation = "machine-translation";
    public const string Llm = "llm";
}
