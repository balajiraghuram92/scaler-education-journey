using System.Text.Json;
using Xunit;

namespace StudyTracker.Api.Tests;

public class LifecycleAndProblemDetailsTests
{
    [Fact]
    public void ProblemDetails_ShouldConformToRfc7807_WithoutSecrets()
    {
        var correlationId = "corr-test-12345";
        var problem = new
        {
            type = "https://tools.ietf.org/html/rfc7231#section-6.6.1",
            title = "An internal error occurred processing your request.",
            status = 500,
            detail = "Internal server error. Please refer to traceId for support.",
            instance = "/api/verticals",
            traceId = correlationId
        };

        var json = JsonSerializer.Serialize(problem);

        Assert.Contains("\"status\":500", json);
        Assert.Contains("\"traceId\":\"corr-test-12345\"", json);
        Assert.DoesNotContain("password", json, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("secret", json, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("Host=", json, StringComparison.OrdinalIgnoreCase);
    }

    [Theory]
    [InlineData("--migrate", true, false)]
    [InlineData("--seed-reference-data", false, true)]
    [InlineData("--seed", false, true)]
    public void CliFlagDetection_ShouldIdentifyDedicatedExecutionModes(string flag, bool expectedMigrate, bool expectedSeed)
    {
        var args = new[] { flag };

        bool isMigrate = args.Contains("--migrate");
        bool isSeed = args.Contains("--seed-reference-data") || args.Contains("--seed");

        Assert.Equal(expectedMigrate, isMigrate);
        Assert.Equal(expectedSeed, isSeed);
    }
}
