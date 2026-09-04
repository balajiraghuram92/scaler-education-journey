namespace StudyTracker.Api.Options;

public sealed class SmtpOptions
{
    public const string SectionName = "Smtp";

    public string Host { get; set; } = string.Empty;

    public int Port { get; set; } = 587;

    public string Username { get; set; } = string.Empty;
    public string User { get => Username; set => Username = value; }

    public string Password { get; set; } = string.Empty;
    public string Pass { get => Password; set => Password = value; }

    public bool EnableSsl { get; set; } = true;

    public string FromEmail { get; set; } = "noreply@neuralascent.com";

    public string FromName { get; set; } = "Neuralascent";

    public string AdminNotificationEmail { get; set; } = string.Empty;

    public string FrontendUrl { get; set; } = "http://localhost:5173";

    public bool IsConfigured => !string.IsNullOrWhiteSpace(Host);
}
