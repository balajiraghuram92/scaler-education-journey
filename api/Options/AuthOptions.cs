namespace StudyTracker.Api.Options;

public sealed class AuthOptions
{
    public const string SectionName = "Auth";

    public string JwtSigningKey { get; set; } = string.Empty;

    public string JwtIssuer { get; set; } = "neuralascent";

    public string JwtAudience { get; set; } = "neuralascent-app";

    public int JwtExpiryMinutes { get; set; } = 720; // 12 hours

    public string CookieName { get; set; } = "na_auth";

    // Session management: a short-lived access JWT (CookieName) renewed by a rotating
    // opaque refresh token (RefreshCookieName) tracked in user_sessions.
    public int AccessTokenMinutes { get; set; } = 30;

    public string RefreshCookieName { get; set; } = "na_refresh";

    // Absolute lifetime of a "remember this device" session.
    public int RememberMeDays { get; set; } = 30;

    // Absolute lifetime of a session without "remember me" (refresh cookie is browser-session scoped).
    public int SessionHours { get; set; } = 24;

    // A session unused for this long expires even if its absolute lifetime remains.
    public int IdleTimeoutDays { get; set; } = 14;

    // Window in which re-presenting the just-rotated refresh token is treated as a
    // benign multi-tab race instead of token theft.
    public int RefreshReuseGraceSeconds { get; set; } = 60;

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
