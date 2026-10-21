using System;
using System.Security.Claims;
using Microsoft.AspNetCore.Http;

namespace StudyTracker.Api.Services.Auth;

/// <summary>
/// Reads the signed-in learner from the validated JWT. Anonymous readers get nulls,
/// which every learner-state query treats as "no progress".
/// </summary>
public interface ICurrentUser
{
    int? UserId { get; }
    Guid? SessionId { get; }
    bool IsAuthenticated { get; }
}

public sealed class HttpContextCurrentUser : ICurrentUser
{
    // Not "sid": the JWT handler remaps that registered name to ClaimTypes.Sid on read.
    public const string SessionIdClaim = "na_sid";

    private readonly IHttpContextAccessor _accessor;

    public HttpContextCurrentUser(IHttpContextAccessor accessor)
    {
        _accessor = accessor;
    }

    public int? UserId => ReadUserId(_accessor.HttpContext?.User);

    public Guid? SessionId => ReadSessionId(_accessor.HttpContext?.User);

    public bool IsAuthenticated => UserId.HasValue;

    public static int? ReadUserId(ClaimsPrincipal? principal)
    {
        var value = principal?.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        return int.TryParse(value, out var id) ? id : null;
    }

    public static Guid? ReadSessionId(ClaimsPrincipal? principal)
    {
        var value = principal?.FindFirst(SessionIdClaim)?.Value;
        return Guid.TryParse(value, out var id) ? id : null;
    }
}
