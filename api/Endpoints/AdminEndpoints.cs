using System;
using System.Linq;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services;
using StudyTracker.Api.Services.Email;

namespace StudyTracker.Api.Endpoints;

public static class AdminEndpoints
{
    public static void MapAdminEndpoints(this IEndpointRouteBuilder app)
    {
        var usersGroup = app.MapGroup("/api/admin/users")
            .RequireAuthorization("AdminOnly");

        usersGroup.MapGet("/", GetAllUsersAsync)
            .WithName("AdminGetUsers");

        usersGroup.MapPost("/{id:int}/approve", ApproveUserAsync)
            .WithName("AdminApproveUser");

        usersGroup.MapPost("/{id:int}/reject", RejectUserAsync)
            .WithName("AdminRejectUser");

        usersGroup.MapPost("/{id:int}/reset-totp", ResetTotpAsync)
            .WithName("AdminResetTotp");

        var usageGroup = app.MapGroup("/api/admin/usage")
            .RequireAuthorization("AdminOnly");

        usageGroup.MapGet("/today", GetUsageTodayAsync)
            .WithName("AdminGetUsageToday");

        usageGroup.MapGet("/by-user", GetUsageByUserAsync)
            .WithName("AdminGetUsageByUser");
    }

    private static async Task<AppUser?> LoadApprovedAdminAsync(
        HttpContext httpContext,
        StudyTrackerContext db,
        CancellationToken ct)
    {
        var sub = httpContext.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrWhiteSpace(sub) || !int.TryParse(sub, out var adminId))
        {
            return null;
        }

        var admin = await db.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Id == adminId, ct);
        if (admin == null || admin.Role != "Admin" || admin.Status != "Approved")
        {
            return null;
        }

        return admin;
    }

    private static async Task<IResult> GetAllUsersAsync(
        string? status,
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var query = db.Users.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(status) && !string.Equals(status, "all", StringComparison.OrdinalIgnoreCase))
        {
            query = query.Where(u => u.Status == status);
        }

        var users = await query
            .OrderByDescending(u => u.CreatedAt)
            .Select(u => new UserDto(
                u.Id,
                u.Email,
                u.DisplayName,
                u.Role,
                u.Status,
                u.CreatedAt,
                u.LastLoginAt))
            .ToListAsync(ct);

        return Results.Ok(users);
    }

    private static async Task<IResult> ApproveUserAsync(
        int id,
        StudyTrackerContext db,
        IEmailNotificationService emailService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var user = await db.Users.FirstOrDefaultAsync(u => u.Id == id, ct);
        if (user == null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "User not found.", $"No user found with ID {id}.");
        }

        user.Status = "Approved";
        user.DecidedAt = DateTime.UtcNow;
        user.DecidedByUserId = admin.Id;

        await db.SaveChangesAsync(ct);

        _ = emailService.SendUserApprovedNoticeAsync(user, ct);

        return Results.Ok(new UserDto(
            user.Id,
            user.Email,
            user.DisplayName,
            user.Role,
            user.Status,
            user.CreatedAt,
            user.LastLoginAt));
    }

    private static async Task<IResult> RejectUserAsync(
        int id,
        RejectUserRequest? request,
        StudyTrackerContext db,
        IEmailNotificationService emailService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var user = await db.Users.FirstOrDefaultAsync(u => u.Id == id, ct);
        if (user == null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "User not found.", $"No user found with ID {id}.");
        }

        user.Status = "Rejected";
        user.DecidedAt = DateTime.UtcNow;
        user.DecidedByUserId = admin.Id;

        await db.SaveChangesAsync(ct);

        _ = emailService.SendUserRejectedNoticeAsync(user, request?.Reason, ct);

        return Results.Ok(new UserDto(
            user.Id,
            user.Email,
            user.DisplayName,
            user.Role,
            user.Status,
            user.CreatedAt,
            user.LastLoginAt));
    }

    // Emergency self-recovery if the sole admin loses their TOTP device:
    // Run directly in PostgreSQL:
    // UPDATE app_users SET totp_enabled = false, totp_secret_encrypted = null, last_accepted_totp_counter = null WHERE email = 'admin@neuralascent.local';
    private static async Task<IResult> ResetTotpAsync(
        int id,
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var user = await db.Users.FirstOrDefaultAsync(u => u.Id == id, ct);
        if (user == null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "User not found.", $"No user found with ID {id}.");
        }

        user.TotpEnabled = false;
        user.TotpSecretEncrypted = null;
        user.LastAcceptedTotpCounter = null;

        var activeChallenges = await db.MfaChallenges
            .Where(c => c.UserId == id && c.ConsumedAt == null)
            .ToListAsync(ct);
        foreach (var challenge in activeChallenges)
        {
            challenge.ConsumedAt = DateTime.UtcNow;
        }

        await db.SaveChangesAsync(ct);

        return Results.Ok(new
        {
            message = $"TOTP second-factor reset successfully for user {user.Email}. The user will be required to re-enroll on their next login.",
            userId = user.Id,
            email = user.Email,
            totpEnabled = false
        });
    }

    private static async Task<IResult> GetUsageTodayAsync(
        BudgetGuardService budgetGuard,
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var usage = await budgetGuard.GetTodayUsageAsync(ct);
        return Results.Ok(usage);
    }

    private static async Task<IResult> GetUsageByUserAsync(
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        // Project to an anonymous type first: EF Core cannot translate an ORDER BY
        // on a property of a record built through its constructor.
        var rows = await db.ChatMessages
            .AsNoTracking()
            .Where(m => m.Role == "assistant" && m.Conversation != null)
            .GroupBy(m => new { m.Conversation!.UserId, m.Conversation.User!.Email, m.Conversation.User.DisplayName })
            .Select(g => new
            {
                g.Key.UserId,
                g.Key.Email,
                g.Key.DisplayName,
                TotalRequests = g.Count(),
                TotalCostUsd = decimal.Round(g.Sum(m => m.EstimatedCostUsd ?? 0m), 6),
                TotalPromptTokens = g.Sum(m => m.PromptTokens ?? 0),
                TotalCompletionTokens = g.Sum(m => m.CompletionTokens ?? 0),
                LastRequestAt = g.Max(m => (DateTime?)m.CreatedAt)
            })
            .OrderByDescending(u => u.TotalCostUsd)
            .ToListAsync(ct);

        var userUsage = rows
            .Select(u => new UserUsageDto(
                u.UserId,
                u.Email,
                u.DisplayName,
                u.TotalRequests,
                u.TotalCostUsd,
                u.TotalPromptTokens,
                u.TotalCompletionTokens,
                u.LastRequestAt))
            .ToList();

        return Results.Ok(userUsage);
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
