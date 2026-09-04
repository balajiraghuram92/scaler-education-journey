using System;
using System.Security.Claims;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Auth;
using StudyTracker.Api.Services.Email;

namespace StudyTracker.Api.Endpoints;

public static class AuthEndpoints
{
    private static readonly Regex EmailRegex = new(
        @"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    public static void MapAuthEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/auth");

        group.MapPost("/signup", SignupAsync)
            .WithName("AuthSignup")
            .RequireRateLimiting("AuthPolicy");

        group.MapPost("/login", LoginAsync)
            .WithName("AuthLogin")
            .RequireRateLimiting("AuthPolicy");

        group.MapPost("/totp/enroll/start", TotpEnrollStartAsync)
            .WithName("AuthTotpEnrollStart");

        group.MapPost("/totp/enroll/confirm", TotpEnrollConfirmAsync)
            .WithName("AuthTotpEnrollConfirm")
            .RequireRateLimiting("AuthPolicy");

        group.MapPost("/totp/verify", TotpVerifyAsync)
            .WithName("AuthTotpVerify")
            .RequireRateLimiting("AuthPolicy");

        group.MapPost("/logout", Logout)
            .WithName("AuthLogout");

        group.MapGet("/me", GetCurrentUserAsync)
            .WithName("AuthGetCurrentUser");
    }

    private static async Task<IResult> SignupAsync(
        SignupRequest request,
        StudyTrackerContext db,
        IPasswordHasher passwordHasher,
        IEmailNotificationService emailService,
        IOptions<AuthOptions> authOptions,
        HttpContext httpContext,
        CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(request.Email) || !EmailRegex.IsMatch(request.Email.Trim()))
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid email.", "A valid email address is required.");
        }

        var minLength = authOptions.Value.MinPasswordLength > 0 ? authOptions.Value.MinPasswordLength : 10;
        if (string.IsNullOrWhiteSpace(request.Password) || request.Password.Length < minLength)
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid password.", $"Password must be at least {minLength} characters in length.");
        }

        var normalizedEmail = request.Email.Trim().ToLowerInvariant();

        var emailExists = await db.Users.AnyAsync(u => u.Email.ToLower() == normalizedEmail, ct);
        if (emailExists)
        {
            // Enumeration attack protection: return uniform generic success message without leaking account existence
            return Results.Ok(new
            {
                message = "Registration request received. If eligible, your account will be reviewed by an administrator."
            });
        }

        var passwordHash = passwordHasher.HashPassword(request.Password, out var salt, out var iterations);

        var newUser = new AppUser
        {
            Email = normalizedEmail,
            PasswordHash = passwordHash,
            PasswordSalt = salt,
            PasswordIterations = iterations,
            Role = "User",
            Status = "PendingApproval",
            DisplayName = string.IsNullOrWhiteSpace(request.DisplayName) ? null : request.DisplayName.Trim(),
            CreatedAt = DateTime.UtcNow
        };

        db.Users.Add(newUser);
        await db.SaveChangesAsync(ct);

        // Send asynchronous notifications to admin and user
        _ = emailService.SendAdminNewUserAlertAsync(newUser, ct);
        _ = emailService.SendUserPendingConfirmationAsync(newUser, ct);

        return Results.Ok(new
        {
            message = "Registration request received. If eligible, your account will be reviewed by an administrator."
        });
    }

    private static async Task<IResult> LoginAsync(
        LoginRequest request,
        StudyTrackerContext db,
        IPasswordHasher passwordHasher,
        HttpContext httpContext,
        CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(request.Email) || string.IsNullOrWhiteSpace(request.Password))
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid credentials.", "Email and password are required.");
        }

        var normalizedEmail = request.Email.Trim().ToLowerInvariant();

        var user = await db.Users.FirstOrDefaultAsync(u => u.Email.ToLower() == normalizedEmail, ct);
        if (user == null)
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Invalid credentials.", "The email or password entered is incorrect.");
        }

        var passwordValid = passwordHasher.VerifyPassword(request.Password, user.PasswordHash, user.PasswordSalt, user.PasswordIterations);
        if (!passwordValid)
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Invalid credentials.", "The email or password entered is incorrect.");
        }

        if (string.Equals(user.Status, "PendingApproval", StringComparison.OrdinalIgnoreCase))
        {
            return Problem(
                httpContext,
                StatusCodes.Status403Forbidden,
                "Account Pending Approval",
                "Your registration is pending administrator approval. You will receive an email once approved.");
        }

        if (string.Equals(user.Status, "Rejected", StringComparison.OrdinalIgnoreCase))
        {
            return Problem(
                httpContext,
                StatusCodes.Status403Forbidden,
                "Registration Rejected",
                "Your registration was not approved by an administrator.");
        }

        if (string.Equals(user.Status, "Disabled", StringComparison.OrdinalIgnoreCase) ||
            !string.Equals(user.Status, "Approved", StringComparison.OrdinalIgnoreCase))
        {
            return Problem(
                httpContext,
                StatusCodes.Status403Forbidden,
                "Account Inactive",
                "Your account is inactive or disabled. Please contact an administrator.");
        }

        // Two-factor authentication handshake: do NOT set session cookie here.
        // Return a single-purpose challenge ID backed by an mfa_challenge record.
        var purpose = user.TotpEnabled ? "Login" : "Enrollment";
        var challenge = new MfaChallenge
        {
            Id = Guid.NewGuid(),
            UserId = user.Id,
            Purpose = purpose,
            CreatedAt = DateTime.UtcNow,
            ExpiresAt = DateTime.UtcNow.AddMinutes(5),
            FailedAttempts = 0
        };

        db.MfaChallenges.Add(challenge);
        await db.SaveChangesAsync(ct);

        return Results.Ok(new LoginResponse(challenge.Id, !user.TotpEnabled));
    }

    private static async Task<IResult> TotpEnrollStartAsync(
        TotpEnrollStartRequest request,
        StudyTrackerContext db,
        ITotpService totpService,
        TotpSecretProtector secretProtector,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var challenge = await db.MfaChallenges
            .Include(c => c.User)
            .FirstOrDefaultAsync(c => c.Id == request.ChallengeId, ct);

        if (challenge == null || challenge.ConsumedAt != null || challenge.ExpiresAt <= DateTime.UtcNow || challenge.Purpose != "Enrollment")
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid or expired MFA challenge.", "The MFA challenge is invalid, expired, or has already been used. Please log in again.");
        }

        var user = challenge.User;
        if (user == null || !string.Equals(user.Status, "Approved", StringComparison.OrdinalIgnoreCase))
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Unauthorized.", "User account is invalid or unapproved.");
        }

        var rawSecret = totpService.GenerateSecret();
        var base32Secret = totpService.ToBase32(rawSecret);
        var encryptedSecret = secretProtector.Encrypt(rawSecret);

        user.TotpSecretEncrypted = encryptedSecret;
        await db.SaveChangesAsync(ct);

        var otpAuthUri = totpService.BuildOtpAuthUri(base32Secret, user.Email);

        return Results.Ok(new TotpEnrollStartResponse(otpAuthUri, base32Secret));
    }

    private static async Task<IResult> TotpEnrollConfirmAsync(
        TotpEnrollConfirmRequest request,
        StudyTrackerContext db,
        ITotpService totpService,
        TotpSecretProtector secretProtector,
        IJwtTokenService jwtTokenService,
        IOptions<AuthOptions> authOptions,
        HttpContext httpContext,
        CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(request.Code))
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Verification code required.", "A 6-digit TOTP code is required.");
        }

        var challenge = await db.MfaChallenges
            .Include(c => c.User)
            .FirstOrDefaultAsync(c => c.Id == request.ChallengeId, ct);

        if (challenge == null || challenge.ConsumedAt != null || challenge.ExpiresAt <= DateTime.UtcNow || challenge.Purpose != "Enrollment")
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid or expired MFA challenge.", "The MFA challenge is invalid, expired, or has already been used. Please log in again.");
        }

        if (challenge.FailedAttempts >= 5)
        {
            challenge.ConsumedAt = DateTime.UtcNow;
            await db.SaveChangesAsync(ct);
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Too many failed attempts.", "Maximum verification attempts reached. Please restart login.");
        }

        var user = challenge.User;
        if (user == null || !string.Equals(user.Status, "Approved", StringComparison.OrdinalIgnoreCase) || string.IsNullOrWhiteSpace(user.TotpSecretEncrypted))
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Unauthorized.", "User account is invalid or enrollment has not been initialized.");
        }

        byte[] secret;
        try
        {
            secret = secretProtector.Decrypt(user.TotpSecretEncrypted);
        }
        catch (Exception)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Decryption error.", "Failed to decrypt TOTP secret.");
        }

        if (!totpService.TryVerify(secret, request.Code, user.LastAcceptedTotpCounter, out var acceptedCounter))
        {
            challenge.FailedAttempts++;
            if (challenge.FailedAttempts >= 5)
            {
                challenge.ConsumedAt = DateTime.UtcNow;
            }
            await db.SaveChangesAsync(ct);
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid code.", "The 6-digit verification code is invalid or has expired.");
        }

        // Enrollment confirmed: mark TOTP enabled, record counter, update last login, consume challenge
        user.TotpEnabled = true;
        user.LastAcceptedTotpCounter = acceptedCounter;
        user.LastLoginAt = DateTime.UtcNow;
        challenge.ConsumedAt = DateTime.UtcNow;
        await db.SaveChangesAsync(ct);

        SetAuthCookie(httpContext, jwtTokenService, authOptions, user);

        return Results.Ok(new UserDto(
            user.Id,
            user.Email,
            user.DisplayName,
            user.Role,
            user.Status,
            user.CreatedAt,
            user.LastLoginAt));
    }

    private static async Task<IResult> TotpVerifyAsync(
        TotpVerifyRequest request,
        StudyTrackerContext db,
        ITotpService totpService,
        TotpSecretProtector secretProtector,
        IJwtTokenService jwtTokenService,
        IOptions<AuthOptions> authOptions,
        HttpContext httpContext,
        CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(request.Code))
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Verification code required.", "A 6-digit TOTP code is required.");
        }

        var challenge = await db.MfaChallenges
            .Include(c => c.User)
            .FirstOrDefaultAsync(c => c.Id == request.ChallengeId, ct);

        if (challenge == null || challenge.ConsumedAt != null || challenge.ExpiresAt <= DateTime.UtcNow || challenge.Purpose != "Login")
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid or expired MFA challenge.", "The MFA challenge is invalid, expired, or has already been used. Please log in again.");
        }

        if (challenge.FailedAttempts >= 5)
        {
            challenge.ConsumedAt = DateTime.UtcNow;
            await db.SaveChangesAsync(ct);
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Too many failed attempts.", "Maximum verification attempts reached. Please restart login.");
        }

        var user = challenge.User;
        if (user == null || !string.Equals(user.Status, "Approved", StringComparison.OrdinalIgnoreCase) || !user.TotpEnabled || string.IsNullOrWhiteSpace(user.TotpSecretEncrypted))
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Unauthorized.", "User account is invalid or TOTP is not enabled.");
        }

        byte[] secret;
        try
        {
            secret = secretProtector.Decrypt(user.TotpSecretEncrypted);
        }
        catch (Exception)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Decryption error.", "Failed to decrypt TOTP secret.");
        }

        if (!totpService.TryVerify(secret, request.Code, user.LastAcceptedTotpCounter, out var acceptedCounter))
        {
            challenge.FailedAttempts++;
            if (challenge.FailedAttempts >= 5)
            {
                challenge.ConsumedAt = DateTime.UtcNow;
            }
            await db.SaveChangesAsync(ct);
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid code.", "The 6-digit verification code is invalid or has expired.");
        }

        // Verification successful: record counter, update last login, consume challenge
        user.LastAcceptedTotpCounter = acceptedCounter;
        user.LastLoginAt = DateTime.UtcNow;
        challenge.ConsumedAt = DateTime.UtcNow;
        await db.SaveChangesAsync(ct);

        SetAuthCookie(httpContext, jwtTokenService, authOptions, user);

        return Results.Ok(new UserDto(
            user.Id,
            user.Email,
            user.DisplayName,
            user.Role,
            user.Status,
            user.CreatedAt,
            user.LastLoginAt));
    }

    private static void SetAuthCookie(
        HttpContext httpContext,
        IJwtTokenService jwtTokenService,
        IOptions<AuthOptions> authOptions,
        AppUser user)
    {
        var cookieName = !string.IsNullOrWhiteSpace(authOptions.Value.CookieName)
            ? authOptions.Value.CookieName
            : "na_auth";

        var token = jwtTokenService.GenerateToken(user);
        var cookieOptions = new CookieOptions
        {
            HttpOnly = true,
            Secure = httpContext.Request.IsHttps,
            SameSite = SameSiteMode.Lax,
            Expires = jwtTokenService.GetExpiration(),
            Path = "/"
        };

        httpContext.Response.Cookies.Append(cookieName, token, cookieOptions);
    }

    private static IResult Logout(
        IOptions<AuthOptions> authOptions,
        HttpContext httpContext)
    {
        var cookieName = !string.IsNullOrWhiteSpace(authOptions.Value.CookieName)
            ? authOptions.Value.CookieName
            : "na_auth";

        httpContext.Response.Cookies.Delete(cookieName, new CookieOptions
        {
            HttpOnly = true,
            Secure = httpContext.Request.IsHttps,
            SameSite = SameSiteMode.Lax,
            Path = "/"
        });

        return Results.Ok(new { message = "Logged out successfully." });
    }

    private static async Task<IResult> GetCurrentUserAsync(
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var userIdClaim = httpContext.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrWhiteSpace(userIdClaim) || !int.TryParse(userIdClaim, out var userId))
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Unauthenticated.", "You are not authenticated.");
        }

        var user = await db.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Id == userId, ct);
        if (user == null || !string.Equals(user.Status, "Approved", StringComparison.OrdinalIgnoreCase))
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Unauthorized.", "User account is invalid or unapproved.");
        }

        return Results.Ok(new UserDto(
            user.Id,
            user.Email,
            user.DisplayName,
            user.Role,
            user.Status,
            user.CreatedAt,
            user.LastLoginAt));
    }

    private static IResult Problem(HttpContext context, int statusCode, string title, string detail)
    {
        return Results.Json(
            new
            {
                type = "https://tools.ietf.org/html/rfc7231",
                title,
                status = statusCode,
                detail,
                instance = context.Request.Path.Value,
                traceId = context.TraceIdentifier
            },
            contentType: "application/problem+json",
            statusCode: statusCode);
    }
}
