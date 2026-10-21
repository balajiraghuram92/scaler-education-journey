using System;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services.Auth;

public interface IJwtTokenService
{
    /// <summary>
    /// Issues an access token. With a session id the token is short-lived and carries the
    /// session claim; without one it uses the legacy long expiry (CLI/tests only).
    /// </summary>
    string GenerateToken(AppUser user, Guid? sessionId = null);

    DateTime GetExpiration();

    DateTime GetAccessTokenExpiration();
}
