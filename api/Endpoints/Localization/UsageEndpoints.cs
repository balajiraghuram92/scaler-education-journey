using System;
using System.Globalization;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Services.Localization;

namespace StudyTracker.Api.Endpoints.Localization;

public static class UsageEndpoints
{
    public static void MapUsageEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/localization/ops");

        group.MapGet("/usage", GetUsageSummary)
            .WithName("GetLocalizationUsageSummary");

        group.MapGet("/usage/events", GetUsageEvents)
            .WithName("GetLocalizationUsageEvents");

        group.MapGet("/rates", GetRates)
            .WithName("GetLocalizationProviderRates");

        group.MapPost("/rates", AddRate)
            .WithName("AddLocalizationProviderRate");
    }

    private static async Task<IResult> GetUsageSummary(
        string? project,
        string? month,
        UsageMeteringService metering,
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await AdminAuthorization.LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var now = DateTime.UtcNow;
        var year = now.Year;
        var monthNumber = now.Month;
        if (!string.IsNullOrWhiteSpace(month))
        {
            if (!DateTime.TryParseExact(month, "yyyy-MM", CultureInfo.InvariantCulture, DateTimeStyles.None, out var parsed))
            {
                return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid month.", "Query parameter 'month' must be in yyyy-MM format.");
            }

            year = parsed.Year;
            monthNumber = parsed.Month;
        }

        try
        {
            var summary = await metering.GetSummaryAsync(project, year, monthNumber, ct);
            return Results.Ok(summary);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
    }

    private static async Task<IResult> GetUsageEvents(
        string? project,
        int? limit,
        UsageMeteringService metering,
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await AdminAuthorization.LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        try
        {
            var events = await metering.GetRecentEventsAsync(project, limit ?? 100, ct);
            return Results.Ok(events);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
    }

    private static async Task<IResult> GetRates(
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await AdminAuthorization.LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var rates = await db.LocalizationProviderRates
            .AsNoTracking()
            .OrderByDescending(r => r.ValidFrom)
            .Select(r => new ProviderRateDto(r.Id, r.Meter, r.UnitKind, r.UsdPerMillion, r.ValidFrom))
            .ToListAsync(ct);
        return Results.Ok(rates);
    }

    private static async Task<IResult> AddRate(
        AddProviderRateRequest request,
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await AdminAuthorization.LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var meters = new[] { UsageMeters.MachineTranslation, UsageMeters.LlmOptimize, UsageMeters.LlmScore };
        var kinds = new[] { UsageUnitKinds.Char, UsageUnitKinds.InputToken, UsageUnitKinds.OutputToken };
        if (string.IsNullOrWhiteSpace(request.Meter) || !meters.Contains(request.Meter))
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Unknown meter.", $"Meter '{request.Meter}' is not a known usage meter.");
        }

        if (string.IsNullOrWhiteSpace(request.UnitKind) || !kinds.Contains(request.UnitKind))
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Unknown unit kind.", $"Unit kind '{request.UnitKind}' is not a known unit kind.");
        }

        if (request.UsdPerMillion is null || request.UsdPerMillion.Value < 0m)
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid price.", "UsdPerMillion is required and must not be negative.");
        }

        var validFrom = request.ValidFrom ?? DateTime.UtcNow;
        var duplicate = await db.LocalizationProviderRates
            .AsNoTracking()
            .AnyAsync(r => r.Meter == request.Meter && r.UnitKind == request.UnitKind && r.ValidFrom == validFrom, ct);
        if (duplicate)
        {
            return Problem(httpContext, StatusCodes.Status409Conflict, "Rate already exists.", $"A rate for meter '{request.Meter}', unit kind '{request.UnitKind}' and this valid-from already exists.");
        }

        var rate = new LocalizationProviderRate
        {
            Meter = request.Meter,
            UnitKind = request.UnitKind,
            UsdPerMillion = request.UsdPerMillion.Value,
            ValidFrom = validFrom
        };
        db.LocalizationProviderRates.Add(rate);
        await db.SaveChangesAsync(ct);

        return Results.Json(
            new ProviderRateDto(rate.Id, rate.Meter, rate.UnitKind, rate.UsdPerMillion, rate.ValidFrom),
            statusCode: StatusCodes.Status201Created);
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
