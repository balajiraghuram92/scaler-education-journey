using System;
using System.Text;
using StudyTracker.Api.Services.Auth;
using Xunit;

namespace StudyTracker.Api.Tests;

public class TotpServiceTests
{
    private readonly TotpService _totpService = new();

    [Fact]
    public void GenerateSecret_Returns20RandomBytes()
    {
        var secret1 = _totpService.GenerateSecret();
        var secret2 = _totpService.GenerateSecret();

        Assert.Equal(20, secret1.Length);
        Assert.Equal(20, secret2.Length);
        Assert.False(secret1.SequenceEqual(secret2));
    }

    [Theory]
    [InlineData("", "")]
    [InlineData("f", "MY")]
    [InlineData("fo", "MZXQ")]
    [InlineData("foo", "MZXW6")]
    [InlineData("foob", "MZXW6YQ")]
    [InlineData("fooba", "MZXW6YTB")]
    [InlineData("foobar", "MZXW6YTBOI")]
    public void ToBase32_MatchesRfc4648TestVectorsWithoutPadding(string input, string expectedBase32)
    {
        var bytes = Encoding.ASCII.GetBytes(input);
        var base32 = _totpService.ToBase32(bytes);
        Assert.Equal(expectedBase32, base32);
    }

    [Fact]
    public void ToBase32_For20ByteSecret_Produces32CharactersWithoutPadding()
    {
        var secret = _totpService.GenerateSecret();
        var base32 = _totpService.ToBase32(secret);

        Assert.Equal(32, base32.Length);
        Assert.DoesNotContain("=", base32);
        Assert.Matches("^[A-Z2-7]{32}$", base32);
    }

    [Fact]
    public void BuildOtpAuthUri_ContainsExpectedSchemeAndParameters()
    {
        var secret = "JBSWY3DPEHPK3PXP";
        var email = "learner@example.com";

        var uri = _totpService.BuildOtpAuthUri(secret, email);

        Assert.StartsWith("otpauth://totp/Neuralascent:", uri);
        Assert.Contains(Uri.EscapeDataString(email), uri);
        Assert.Contains($"secret={secret}", uri);
        Assert.Contains("issuer=Neuralascent", uri);
        Assert.Contains("algorithm=SHA1", uri);
        Assert.Contains("digits=6", uri);
        Assert.Contains("period=30", uri);
    }

    [Theory]
    [InlineData(1L, "287082")]
    [InlineData(37037036L, "081804")]
    [InlineData(37037037L, "050471")]
    [InlineData(41152263L, "005924")]
    [InlineData(66666666L, "279037")]
    public void ComputeCode_MatchesOfficialRfc6238Sha1TestVectors(long counter, string expectedCode)
    {
        // RFC 6238 Appendix B SHA1 key: "12345678901234567890" (20 ASCII bytes)
        var rfcSecret = Encoding.ASCII.GetBytes("12345678901234567890");
        var code = _totpService.ComputeCode(rfcSecret, counter);
        Assert.Equal(expectedCode, code);
    }

    [Fact]
    public void TryVerify_WithCurrentCode_ReturnsTrue()
    {
        var secret = _totpService.GenerateSecret();
        var currentCounter = _totpService.CurrentCounter();
        var currentCode = _totpService.ComputeCode(secret, currentCounter);

        var verified = _totpService.TryVerify(secret, currentCode, null, out var acceptedCounter);

        Assert.True(verified);
        Assert.Equal(currentCounter, acceptedCounter);
    }

    [Fact]
    public void TryVerify_AllowsTimeWindowPlusMinusOne()
    {
        var secret = _totpService.GenerateSecret();
        var current = _totpService.CurrentCounter();

        var codeMinus1 = _totpService.ComputeCode(secret, current - 1);
        Assert.True(_totpService.TryVerify(secret, codeMinus1, null, out var accepted1));
        Assert.Equal(current - 1, accepted1);

        var codePlus1 = _totpService.ComputeCode(secret, current + 1);
        Assert.True(_totpService.TryVerify(secret, codePlus1, null, out var accepted2));
        Assert.Equal(current + 1, accepted2);
    }

    [Fact]
    public void TryVerify_RejectsCodesOutsideWindow()
    {
        var secret = _totpService.GenerateSecret();
        var current = _totpService.CurrentCounter();

        var codeMinus2 = _totpService.ComputeCode(secret, current - 2);
        Assert.False(_totpService.TryVerify(secret, codeMinus2, null, out _));

        var codePlus2 = _totpService.ComputeCode(secret, current + 2);
        Assert.False(_totpService.TryVerify(secret, codePlus2, null, out _));
    }

    [Fact]
    public void TryVerify_ReplayProtection_RejectsEqualOrOlderAcceptedCounters()
    {
        var secret = _totpService.GenerateSecret();
        var current = _totpService.CurrentCounter();
        var code = _totpService.ComputeCode(secret, current);

        // Counter already accepted at 'current'
        Assert.False(_totpService.TryVerify(secret, code, lastAcceptedCounter: current, out _));

        // Counter already accepted at future step 'current + 1'
        Assert.False(_totpService.TryVerify(secret, code, lastAcceptedCounter: current + 1, out _));

        // When previous counter was older, verification succeeds
        Assert.True(_totpService.TryVerify(secret, code, lastAcceptedCounter: current - 1, out var accepted));
        Assert.Equal(current, accepted);
    }

    [Theory]
    [InlineData("12345")] // too short
    [InlineData("1234567")] // too long
    [InlineData("abcdef")] // non-numeric
    [InlineData("")]
    [InlineData(null)]
    public void TryVerify_InvalidInputFormat_ReturnsFalse(string? code)
    {
        var secret = _totpService.GenerateSecret();
        Assert.False(_totpService.TryVerify(secret, code!, null, out _));
    }
}
