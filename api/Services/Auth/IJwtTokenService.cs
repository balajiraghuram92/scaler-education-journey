using System;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services.Auth;

public interface IJwtTokenService
{
    string GenerateToken(AppUser user);
    DateTime GetExpiration();
}
