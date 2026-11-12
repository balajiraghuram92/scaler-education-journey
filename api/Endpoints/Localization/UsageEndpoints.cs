using System;
using System.Globalization;
using System.Linq;
using System.Text.Json;
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

        group.MapGet("/projects/{slug}/controls", GetControls)
            .WithName("GetLocalizationProjectControls");

        group.MapPut("/projects/{slug}/controls", UpdateControls)
            .WithName("UpdateLocalizationProjectControls");

        group.MapGet("/teams", GetTeams)
            .WithName("GetLocalizationTeams");

        group.MapGet("/projects/{slug}/agreement", GetAgreement)
            .WithName("GetLocalizationAgreement");

        group.MapPut("/projects/{slug}/agreement", SaveAgreement)
            .WithName("SaveLocalizationAgreement");
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

    private static async Task<IResult> GetControls(
        string slug,
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

        var project = await db.LocalizationProjects
            .FirstOrDefaultAsync(p => p.Slug == slug, ct);
        if (project == null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", $"Localization project '{slug}' was not found.");
        }

        return Results.Ok(await ControlsDtoAsync(db, metering, project, ct));
    }

    private static async Task<IResult> UpdateControls(
        string slug,
        JsonElement body,
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

        var project = await db.LocalizationProjects
            .FirstOrDefaultAsync(p => p.Slug == slug, ct);
        if (project == null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", $"Localization project '{slug}' was not found.");
        }

        // Every field is optional: absent leaves the value unchanged, explicit
        // null on a limit removes the cap. A nullable record property cannot
        // tell those apart, so the body is read as JSON here.
        if (TryGetProperty(body, "aiEnabled", out var aiEnabled) && aiEnabled.ValueKind != JsonValueKind.Null)
        {
            if (aiEnabled.ValueKind != JsonValueKind.True && aiEnabled.ValueKind != JsonValueKind.False)
            {
                return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid controls.", "Property 'aiEnabled' must be a boolean.");
            }

            project.AiEnabled = aiEnabled.GetBoolean();
        }

        var limits = new[]
        {
            ("machineTranslationMonthlyLimit", UsageCapKinds.MachineTranslation),
            ("llmMonthlyLimit", UsageCapKinds.Llm)
        };
        foreach (var (property, kind) in limits)
        {
            if (!TryGetProperty(body, property, out var value))
            {
                continue;
            }

            if (value.ValueKind == JsonValueKind.Null)
            {
                var doomed = await db.LocalizationUsageCaps
                    .FirstOrDefaultAsync(c => c.ProjectId == project.Id && c.Kind == kind, ct);
                if (doomed is not null)
                {
                    db.LocalizationUsageCaps.Remove(doomed);
                }

                continue;
            }

            if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt64(out var monthlyLimit) || monthlyLimit < 0)
            {
                return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid controls.", $"Property '{property}' must be a non-negative integer or null.");
            }

            var existing = await db.LocalizationUsageCaps
                .FirstOrDefaultAsync(c => c.ProjectId == project.Id && c.Kind == kind, ct);
            if (existing is null)
            {
                db.LocalizationUsageCaps.Add(new LocalizationUsageCap
                {
                    ProjectId = project.Id,
                    Kind = kind,
                    MonthlyLimit = monthlyLimit,
                    UpdatedAt = DateTime.UtcNow
                });
            }
            else
            {
                existing.MonthlyLimit = monthlyLimit;
                existing.UpdatedAt = DateTime.UtcNow;
            }
        }

        await db.SaveChangesAsync(ct);
        return Results.Ok(await ControlsDtoAsync(db, metering, project, ct));
    }

    private static async Task<ProjectControlsDto> ControlsDtoAsync(
        StudyTrackerContext db,
        UsageMeteringService metering,
        LocalizationProject project,
        CancellationToken ct)
    {
        var budget = await metering.BeginRunAsync(project.Id, DateTime.UtcNow, ct);
        return new ProjectControlsDto(
            project.Slug,
            project.AiEnabled,
            new[] { UsageCapKinds.MachineTranslation, UsageCapKinds.Llm }
                .Select(kind => new UsageCapDto(kind, budget.Limit(kind), budget.Used(kind)))
                .ToList());
    }

    private static bool TryGetProperty(JsonElement body, string name, out JsonElement value)
    {
        value = default;
        return body.ValueKind == JsonValueKind.Object && body.TryGetProperty(name, out value);
    }

    private static async Task<IResult> GetTeams(
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var admin = await AdminAuthorization.LoadApprovedAdminAsync(httpContext, db, ct);
        if (admin == null)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Forbidden", "Administrative privileges required.");
        }

        var teams = await db.LocalizationVendors
            .AsNoTracking()
            .OrderBy(v => v.Id)
            .Select(v => new OpsVendorTeamDto(v.Id, v.Alias, v.Name, v.Languages))
            .ToListAsync(ct);
        return Results.Ok(teams);
    }

    private static async Task<IResult> GetAgreement(
        string slug,
        TranslationJobService jobService,
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
            var agreement = await jobService.GetAgreementAsync(slug, true, ct);
            if (agreement == null)
            {
                return Problem(httpContext, StatusCodes.Status404NotFound, "Agreement not found.", $"Localization project '{slug}' has no service agreement.");
            }

            return Results.Ok(agreement);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving agreement.", ex.Message);
        }
    }

    private static async Task<IResult> SaveAgreement(
        string slug,
        SaveAgreementRequest request,
        TranslationJobService jobService,
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
            var agreement = await jobService.SaveAgreementAsync(slug, request, ct);
            return Results.Ok(agreement);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (ArgumentException ex)
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid agreement.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error saving agreement.", ex.Message);
        }
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
