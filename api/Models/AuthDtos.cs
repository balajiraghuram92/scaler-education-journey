using System;

namespace StudyTracker.Api.Models;

public sealed record SignupRequest(string Email, string Password, string? DisplayName);
public sealed record LoginRequest(string Email, string Password);
public sealed record LoginResponse(Guid ChallengeId, bool RequiresEnrollment);
public sealed record TotpEnrollStartRequest(Guid ChallengeId);
public sealed record TotpEnrollStartResponse(string OtpAuthUri, string ManualEntryCode);
public sealed record TotpEnrollConfirmRequest(Guid ChallengeId, string Code, bool RememberMe = false);
public sealed record TotpVerifyRequest(Guid ChallengeId, string Code, bool RememberMe = false);
public sealed record RejectUserRequest(string? Reason);
public sealed record UserDto(int Id, string Email, string? DisplayName, string Role, string Status, DateTime CreatedAt, DateTime? LastLoginAt);
