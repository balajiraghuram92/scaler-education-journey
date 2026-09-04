namespace StudyTracker.Api.Options;

public sealed class EmailOptions
{
    public const string SectionName = "Email";

    public string SmtpHost { get; set; } = string.Empty;

    public int SmtpPort { get; set; } = 587;

    public string SmtpUsername { get; set; } = string.Empty;

    public string SmtpPassword { get; set; } = string.Empty;

    public bool UseSsl { get; set; } = true;

    public string FromAddress { get; set; } = "noreply@neuralascent.top";

    public string FromDisplayName { get; set; } = "Neuralascent";
}
