namespace StudyTracker.Api.Options;

public sealed class JwtOptions
{
    public const string SectionName = "Jwt";

    public string SecretKey { get; set; } = "Neuralascent_Secure_Development_Secret_Key_2026_AtLeast32Bytes!";

    public string Issuer { get; set; } = "Neuralascent";

    public string Audience { get; set; } = "NeuralascentLearners";

    public int ExpirationDays { get; set; } = 7;

    public string CookieName { get; set; } = "auth_token";
}
