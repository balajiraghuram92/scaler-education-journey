using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Services.Localization;

namespace StudyTracker.Api.Endpoints.Localization;

public static class ProviderHealthEndpoints
{
    public static void MapProviderHealthEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/localization/provider-health");

        group.MapGet("/", GetHealth)
            .WithName("GetLocalizationProviderHealth");

        group.MapPost("/{provider}/simulate-outage", SimulateOutage)
            .WithName("SimulateLocalizationProviderOutage");

        group.MapPost("/{provider}/resolve", ResolveOutage)
            .WithName("ResolveLocalizationProviderOutage");
    }

    private static async Task<IResult> GetHealth(
        ProviderHealthService healthService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var health = await healthService.GetHealthAsync(ct);
            return Results.Ok(health);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving provider health.", ex.Message);
        }
    }

    private static async Task<IResult> SimulateOutage(
        string provider,
        ProviderHealthService healthService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var updated = await healthService.SimulateOutageAsync(provider, ct);
            return Results.Ok(updated);
        }
        catch (ProviderNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Provider not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error simulating outage.", ex.Message);
        }
    }

    private static async Task<IResult> ResolveOutage(
        string provider,
        ProviderHealthService healthService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var updated = await healthService.ResolveOutageAsync(provider, ct);
            return Results.Ok(updated);
        }
        catch (ProviderNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Provider not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error resolving outage.", ex.Message);
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
