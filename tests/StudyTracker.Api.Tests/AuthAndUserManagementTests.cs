using System;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Auth;
using Xunit;

namespace StudyTracker.Api.Tests;

public class AuthAndUserManagementTests
{
    private readonly Pbkdf2PasswordHasher _hasher = new();

    [Fact]
    public void Pbkdf2PasswordHasher_HashPassword_ProducesNonEmptyHashAndSalt()
    {
        var password = "SecureTestPassword123!";
        var hash = _hasher.HashPassword(password, out var salt, out var iterations);

        Assert.False(string.IsNullOrWhiteSpace(hash));
        Assert.False(string.IsNullOrWhiteSpace(salt));
        Assert.True(iterations >= 100_000);
    }

    [Fact]
    public void Pbkdf2PasswordHasher_VerifyPassword_ReturnsTrueForMatchingPassword()
    {
        var password = "MySecretPassword!";
        var hash = _hasher.HashPassword(password, out var salt, out var iterations);

        var isValid = _hasher.VerifyPassword(password, hash, salt, iterations);

        Assert.True(isValid);
    }

    [Fact]
    public void Pbkdf2PasswordHasher_VerifyPassword_ReturnsFalseForWrongPassword()
    {
        var password = "CorrectPassword123";
        var hash = _hasher.HashPassword(password, out var salt, out var iterations);

        var isValid = _hasher.VerifyPassword("WrongPassword456", hash, salt, iterations);

        Assert.False(isValid);
    }

    [Fact]
    public void Pbkdf2PasswordHasher_VerifyPassword_HandlesCorruptedSaltOrHashSafely()
    {
        var isValid = _hasher.VerifyPassword("password", "invalid_base64_hash", "invalid_salt", 100_000);
        Assert.False(isValid);
    }

    [Fact]
    public void AppUser_DefaultValues_ArePendingApprovalAndUserRole()
    {
        var user = new AppUser
        {
            Email = "learner@example.com",
            PasswordHash = "hash123",
            PasswordSalt = "salt123"
        };

        Assert.Equal("User", user.Role);
        Assert.Equal("PendingApproval", user.Status);
        Assert.Null(user.DisplayName);
        Assert.Null(user.DecidedAt);
        Assert.Null(user.DecidedByUserId);
        Assert.Null(user.LastLoginAt);
    }

    [Fact]
    public void AuthDtos_SealedRecords_VerifyProperties()
    {
        var signupReq = new SignupRequest("user@example.com", "Password123", "Test Learner");
        Assert.Equal("user@example.com", signupReq.Email);
        Assert.Equal("Password123", signupReq.Password);
        Assert.Equal("Test Learner", signupReq.DisplayName);

        var loginReq = new LoginRequest("user@example.com", "Password123");
        Assert.Equal("user@example.com", loginReq.Email);
        Assert.Equal("Password123", loginReq.Password);

        var rejectReq = new RejectUserRequest("Account outside scope");
        Assert.Equal("Account outside scope", rejectReq.Reason);

        var challengeGuid = Guid.NewGuid();
        var loginResp = new LoginResponse(challengeGuid, true);
        Assert.Equal(challengeGuid, loginResp.ChallengeId);
        Assert.True(loginResp.RequiresEnrollment);

        var enrollStartReq = new TotpEnrollStartRequest(challengeGuid);
        Assert.Equal(challengeGuid, enrollStartReq.ChallengeId);

        var enrollStartResp = new TotpEnrollStartResponse("otpauth://totp/...", "BASE32SECRET");
        Assert.Equal("otpauth://totp/...", enrollStartResp.OtpAuthUri);
        Assert.Equal("BASE32SECRET", enrollStartResp.ManualEntryCode);

        var enrollConfirmReq = new TotpEnrollConfirmRequest(challengeGuid, "123456");
        Assert.Equal(challengeGuid, enrollConfirmReq.ChallengeId);
        Assert.Equal("123456", enrollConfirmReq.Code);

        var verifyReq = new TotpVerifyRequest(challengeGuid, "654321");
        Assert.Equal(challengeGuid, verifyReq.ChallengeId);
        Assert.Equal("654321", verifyReq.Code);

        var now = DateTime.UtcNow;
        var userDto = new UserDto(42, "user@example.com", "Test Learner", "User", "Approved", now, now);
        Assert.Equal(42, userDto.Id);
        Assert.Equal("Approved", userDto.Status);
        Assert.Equal("User", userDto.Role);
    }

    [Fact]
    public void MfaChallenge_DefaultValues_VerifyInitialization()
    {
        var challenge = new MfaChallenge
        {
            UserId = 10,
            Purpose = "Login"
        };

        Assert.NotEqual(Guid.Empty, challenge.Id);
        Assert.Equal(10, challenge.UserId);
        Assert.Equal("Login", challenge.Purpose);
        Assert.Equal(0, challenge.FailedAttempts);
        Assert.Null(challenge.ConsumedAt);
        Assert.True(challenge.ExpiresAt > challenge.CreatedAt);
    }

    [Fact]
    public void JwtTokenService_GenerateToken_ContainsExpectedClaims()
    {
        var authOptions = Microsoft.Extensions.Options.Options.Create(new AuthOptions
        {
            JwtSigningKey = "Test_Secret_Key_For_Unit_Testing_32_Bytes_Long!",
            JwtIssuer = "TestIssuer",
            JwtAudience = "TestAudience",
            JwtExpiryMinutes = 1440
        });

        var jwtService = new JwtTokenService(authOptions);

        var user = new AppUser
        {
            Id = 99,
            Email = "admin@example.com",
            DisplayName = "Admin Boss",
            Role = "Admin",
            Status = "Approved"
        };

        var tokenString = jwtService.GenerateToken(user);
        Assert.False(string.IsNullOrWhiteSpace(tokenString));

        var handler = new JwtSecurityTokenHandler();
        var token = handler.ReadJwtToken(tokenString);

        Assert.Equal("TestIssuer", token.Issuer);
        Assert.Contains("TestAudience", token.Audiences);

        var nameIdClaim = token.Claims.First(c => c.Type == ClaimTypes.NameIdentifier || c.Type == "nameid").Value;
        var emailClaim = token.Claims.First(c => c.Type == ClaimTypes.Email || c.Type == "email").Value;
        var roleClaim = token.Claims.First(c => c.Type == ClaimTypes.Role || c.Type == "role").Value;

        Assert.Equal("99", nameIdClaim);
        Assert.Equal("admin@example.com", emailClaim);
        Assert.Equal("Admin", roleClaim);
    }
}
