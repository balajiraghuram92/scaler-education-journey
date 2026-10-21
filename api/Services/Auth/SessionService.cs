using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Auth;

public enum RefreshOutcome
{
    Refreshed,
    Missing,
    Invalid,
    Expired,
    Revoked,
    ReuseDetected,
    UserInactive
}

public sealed record RefreshResult(RefreshOutcome Outcome, AppUser? User = null, UserSession? Session = null);

public sealed record SessionSummaryDto(
    Guid Id,
    DateTime CreatedAt,
    DateTime LastSeenAt,
    DateTime ExpiresAt,
    bool RememberMe,
    string? UserAgent,
    string? IpAddress,
    bool IsCurrent);

/// <summary>
/// Owns the session lifecycle: issue on login, rotate on refresh (with reuse detection),
/// revoke on logout, and answer "is this session still valid" for every authenticated request.
/// </summary>
public class SessionService
{
    private static readonly TimeSpan ActiveCheckCacheTtl = TimeSpan.FromSeconds(30);

    private readonly StudyTrackerContext _db;
    private readonly IJwtTokenService _jwt;
    private readonly AuthOptions _options;
    private readonly IMemoryCache _cache;
    private readonly ILogger<SessionService> _logger;

    public SessionService(
        StudyTrackerContext db,
        IJwtTokenService jwt,
        IOptions<AuthOptions> options,
        IMemoryCache cache,
        ILogger<SessionService> logger)
    {
        _db = db;
        _jwt = jwt;
        _options = options.Value;
        _cache = cache;
        _logger = logger;
    }

    private string AccessCookieName => string.IsNullOrWhiteSpace(_options.CookieName) ? "na_auth" : _options.CookieName;
    private string RefreshCookieName => string.IsNullOrWhiteSpace(_options.RefreshCookieName) ? "na_refresh" : _options.RefreshCookieName;

    /// <summary>Creates a session for a fully authenticated user and writes both cookies.</summary>
    public async Task<UserSession> StartSessionAsync(AppUser user, bool rememberMe, HttpContext httpContext, CancellationToken ct = default)
    {
        var now = DateTime.UtcNow;
        var rawRefreshToken = NewRefreshToken();
        var session = new UserSession
        {
            Id = Guid.NewGuid(),
            UserId = user.Id,
            RefreshTokenHash = Hash(rawRefreshToken),
            RememberMe = rememberMe,
            CreatedAt = now,
            LastSeenAt = now,
            ExpiresAt = rememberMe
                ? now.AddDays(Math.Max(1, _options.RememberMeDays))
                : now.AddHours(Math.Max(1, _options.SessionHours)),
            UserAgent = Truncate(httpContext.Request.Headers.UserAgent.ToString(), 400),
            IpAddress = Truncate(ResolveClientIp(httpContext), 64)
        };

        _db.UserSessions.Add(session);
        await _db.SaveChangesAsync(ct);

        WriteCookies(httpContext, user, session, rawRefreshToken);
        return session;
    }

    /// <summary>
    /// Exchanges the refresh cookie for a new access token, rotating the refresh token.
    /// A rotated-out token presented again after the grace window revokes the session.
    /// </summary>
    public async Task<RefreshResult> RefreshAsync(HttpContext httpContext, CancellationToken ct = default)
    {
        if (!httpContext.Request.Cookies.TryGetValue(RefreshCookieName, out var rawToken) || string.IsNullOrWhiteSpace(rawToken))
        {
            return new RefreshResult(RefreshOutcome.Missing);
        }

        var tokenHash = Hash(rawToken);
        var now = DateTime.UtcNow;

        var session = await _db.UserSessions
            .Include(s => s.User)
            .FirstOrDefaultAsync(s => s.RefreshTokenHash == tokenHash, ct);

        if (session == null)
        {
            var rotatedOut = await _db.UserSessions
                .Include(s => s.User)
                .FirstOrDefaultAsync(s => s.PreviousRefreshTokenHash == tokenHash, ct);

            if (rotatedOut == null)
            {
                ClearCookies(httpContext);
                return new RefreshResult(RefreshOutcome.Invalid);
            }

            var withinGrace = rotatedOut.RotatedAt.HasValue &&
                              now - rotatedOut.RotatedAt.Value <= TimeSpan.FromSeconds(Math.Max(0, _options.RefreshReuseGraceSeconds));

            if (withinGrace && rotatedOut.IsActive && IsUserActive(rotatedOut.User))
            {
                // Another tab already rotated the token; its response set the new refresh
                // cookie. Re-issue only the access token so this request can proceed.
                WriteAccessCookie(httpContext, rotatedOut.User!, rotatedOut);
                return new RefreshResult(RefreshOutcome.Refreshed, rotatedOut.User, rotatedOut);
            }

            if (rotatedOut.RevokedAt == null)
            {
                rotatedOut.RevokedAt = now;
                rotatedOut.RevokedReason = "RefreshReuse";
                await _db.SaveChangesAsync(ct);
                Evict(rotatedOut.Id);
                _logger.LogWarning("Refresh token reuse detected for session {SessionId} (user {UserId}); session revoked.", rotatedOut.Id, rotatedOut.UserId);
            }

            ClearCookies(httpContext);
            return new RefreshResult(RefreshOutcome.ReuseDetected);
        }

        if (session.RevokedAt != null)
        {
            ClearCookies(httpContext);
            return new RefreshResult(RefreshOutcome.Revoked);
        }

        var idleLimit = TimeSpan.FromDays(Math.Max(1, _options.IdleTimeoutDays));
        if (session.ExpiresAt <= now || now - session.LastSeenAt > idleLimit)
        {
            session.RevokedAt = now;
            session.RevokedReason = "Expired";
            await _db.SaveChangesAsync(ct);
            Evict(session.Id);
            ClearCookies(httpContext);
            return new RefreshResult(RefreshOutcome.Expired);
        }

        if (!IsUserActive(session.User))
        {
            session.RevokedAt = now;
            session.RevokedReason = "UserInactive";
            await _db.SaveChangesAsync(ct);
            Evict(session.Id);
            ClearCookies(httpContext);
            return new RefreshResult(RefreshOutcome.UserInactive);
        }

        var newRawToken = NewRefreshToken();
        session.PreviousRefreshTokenHash = session.RefreshTokenHash;
        session.RefreshTokenHash = Hash(newRawToken);
        session.RotatedAt = now;
        session.LastSeenAt = now;
        session.UserAgent = Truncate(httpContext.Request.Headers.UserAgent.ToString(), 400) ?? session.UserAgent;
        session.IpAddress = Truncate(ResolveClientIp(httpContext), 64) ?? session.IpAddress;
        await _db.SaveChangesAsync(ct);

        WriteCookies(httpContext, session.User!, session, newRawToken);
        return new RefreshResult(RefreshOutcome.Refreshed, session.User, session);
    }

    /// <summary>Called for every request bearing a session-scoped JWT. Cached briefly.</summary>
    public async Task<bool> IsSessionActiveAsync(Guid sessionId, int userId, CancellationToken ct = default)
    {
        var cacheKey = CacheKey(sessionId);
        if (_cache.TryGetValue(cacheKey, out bool cached))
        {
            return cached;
        }

        var now = DateTime.UtcNow;
        var active = await _db.UserSessions.AsNoTracking()
            .AnyAsync(s => s.Id == sessionId && s.UserId == userId && s.RevokedAt == null && s.ExpiresAt > now, ct);

        _cache.Set(cacheKey, active, ActiveCheckCacheTtl);
        return active;
    }

    public async Task<bool> RevokeAsync(Guid sessionId, int userId, string reason, CancellationToken ct = default)
    {
        var session = await _db.UserSessions.FirstOrDefaultAsync(s => s.Id == sessionId && s.UserId == userId, ct);
        if (session == null)
        {
            return false;
        }

        if (session.RevokedAt == null)
        {
            session.RevokedAt = DateTime.UtcNow;
            session.RevokedReason = reason;
            await _db.SaveChangesAsync(ct);
        }

        Evict(sessionId);
        return true;
    }

    /// <summary>Revokes every active session of a user, optionally keeping one.</summary>
    public async Task<int> RevokeAllAsync(int userId, Guid? exceptSessionId, string reason, CancellationToken ct = default)
    {
        var now = DateTime.UtcNow;
        var sessions = await _db.UserSessions
            .Where(s => s.UserId == userId && s.RevokedAt == null && (exceptSessionId == null || s.Id != exceptSessionId))
            .ToListAsync(ct);

        foreach (var session in sessions)
        {
            session.RevokedAt = now;
            session.RevokedReason = reason;
            Evict(session.Id);
        }

        await _db.SaveChangesAsync(ct);
        return sessions.Count;
    }

    public async Task<List<SessionSummaryDto>> ListActiveAsync(int userId, Guid? currentSessionId, CancellationToken ct = default)
    {
        var now = DateTime.UtcNow;
        var sessions = await _db.UserSessions.AsNoTracking()
            .Where(s => s.UserId == userId && s.RevokedAt == null && s.ExpiresAt > now)
            .OrderByDescending(s => s.LastSeenAt)
            .ToListAsync(ct);

        return sessions
            .Select(s => new SessionSummaryDto(
                s.Id,
                s.CreatedAt,
                s.LastSeenAt,
                s.ExpiresAt,
                s.RememberMe,
                s.UserAgent,
                MaskIp(s.IpAddress),
                s.Id == currentSessionId))
            .ToList();
    }

    /// <summary>Revokes the current session (if any) and clears both cookies.</summary>
    public async Task SignOutAsync(HttpContext httpContext, int? userId, Guid? sessionId, CancellationToken ct = default)
    {
        if (userId.HasValue && sessionId.HasValue)
        {
            await RevokeAsync(sessionId.Value, userId.Value, "Logout", ct);
        }
        else if (httpContext.Request.Cookies.TryGetValue(RefreshCookieName, out var rawToken) && !string.IsNullOrWhiteSpace(rawToken))
        {
            // Access token already expired: find the session through the refresh token.
            var tokenHash = Hash(rawToken);
            var session = await _db.UserSessions.FirstOrDefaultAsync(s => s.RefreshTokenHash == tokenHash && s.RevokedAt == null, ct);
            if (session != null)
            {
                session.RevokedAt = DateTime.UtcNow;
                session.RevokedReason = "Logout";
                await _db.SaveChangesAsync(ct);
                Evict(session.Id);
            }
        }

        ClearCookies(httpContext);
    }

    public void ClearCookies(HttpContext httpContext)
    {
        var secure = httpContext.Request.IsHttps;
        httpContext.Response.Cookies.Delete(AccessCookieName, new CookieOptions { HttpOnly = true, Secure = secure, SameSite = SameSiteMode.Lax, Path = "/" });
        httpContext.Response.Cookies.Delete(RefreshCookieName, new CookieOptions { HttpOnly = true, Secure = secure, SameSite = SameSiteMode.Strict, Path = "/api/auth" });
    }

    private void WriteCookies(HttpContext httpContext, AppUser user, UserSession session, string rawRefreshToken)
    {
        WriteAccessCookie(httpContext, user, session);

        var refreshOptions = new CookieOptions
        {
            HttpOnly = true,
            Secure = httpContext.Request.IsHttps,
            // Only the SPA's own fetches to /api/auth ever need this cookie.
            SameSite = SameSiteMode.Strict,
            Path = "/api/auth",
            // Without "remember me" the cookie dies with the browser session.
            Expires = session.RememberMe ? session.ExpiresAt : null
        };

        httpContext.Response.Cookies.Append(RefreshCookieName, rawRefreshToken, refreshOptions);
    }

    private void WriteAccessCookie(HttpContext httpContext, AppUser user, UserSession session)
    {
        var token = _jwt.GenerateToken(user, session.Id);
        httpContext.Response.Cookies.Append(AccessCookieName, token, new CookieOptions
        {
            HttpOnly = true,
            Secure = httpContext.Request.IsHttps,
            SameSite = SameSiteMode.Lax,
            Path = "/",
            Expires = _jwt.GetAccessTokenExpiration()
        });
    }

    private static bool IsUserActive(AppUser? user) =>
        user != null && string.Equals(user.Status, "Approved", StringComparison.OrdinalIgnoreCase);

    private void Evict(Guid sessionId) => _cache.Remove(CacheKey(sessionId));

    private static string CacheKey(Guid sessionId) => $"session-active:{sessionId}";

    private static string NewRefreshToken() =>
        Convert.ToBase64String(RandomNumberGenerator.GetBytes(32)).TrimEnd('=').Replace('+', '-').Replace('/', '_');

    public static string Hash(string rawToken) =>
        Convert.ToHexString(SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(rawToken))).ToLowerInvariant();

    private static string? ResolveClientIp(HttpContext httpContext)
    {
        var forwarded = httpContext.Request.Headers["X-Forwarded-For"].ToString();
        if (!string.IsNullOrWhiteSpace(forwarded))
        {
            return forwarded.Split(',')[0].Trim();
        }

        return httpContext.Connection.RemoteIpAddress?.ToString();
    }

    private static string? MaskIp(string? ip)
    {
        if (string.IsNullOrWhiteSpace(ip)) return null;
        var parts = ip.Split('.');
        if (parts.Length == 4) return $"{parts[0]}.{parts[1]}.x.x";
        var v6 = ip.Split(':');
        return v6.Length > 2 ? $"{v6[0]}:{v6[1]}:…" : ip;
    }

    private static string? Truncate(string? value, int max)
    {
        if (string.IsNullOrWhiteSpace(value)) return null;
        return value.Length <= max ? value : value[..max];
    }
}
