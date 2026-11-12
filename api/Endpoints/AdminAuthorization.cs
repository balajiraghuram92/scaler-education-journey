using System;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Endpoints;

public static class AdminAuthorization
{
    public static async Task<AppUser?> LoadApprovedAdminAsync(
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
}
