namespace StudyTracker.Api.Options;

public sealed class AuthOptions
{
    public const string SectionName = "Auth";

    public string JwtSigningKey { get; set; } = string.Empty;

    public string JwtIssuer { get; set; } = "neuralascent";

    public string JwtAudience { get; set; } = "neuralascent-app";

    public int JwtExpiryMinutes { get; set; } = 720; // 12 hours

    public string CookieName { get; set; } = "na_auth";

    public int MinPasswordLength { get; set; } = 10;

    public string TotpEncryptionKey { get; set; } = string.Empty;

    // Backward compatibility aliases
    public string Issuer
    {
        get => JwtIssuer;
        set => JwtIssuer = value;
    }

    public string Audience
    {
        get => JwtAudience;
        set => JwtAudience = value;
    }
}
