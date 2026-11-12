using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Services.Localization;

namespace StudyTracker.Api.Endpoints.Localization;

public static class VendorPortalEndpoints
{
    public static void MapVendorPortalEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/localization/vendor");

        group.MapGet("/roster", GetVendorRoster)
            .WithName("GetVendorRoster");

        group.MapGet("/{vendorId:int}/jobs", GetJobs)
            .WithName("GetVendorJobs");

        group.MapGet("/jobs/{jobId:int}/strings", GetJobStrings)
            .WithName("GetVendorJobStrings");

        group.MapPut("/jobs/{jobId:int}/strings/{stringId:int}", UpdateJobString)
            .WithName("UpdateVendorJobString");

        group.MapPost("/jobs/{jobId:int}/submit", SubmitJob)
            .WithName("SubmitVendorJobForReview");
    }

    private static async Task<IResult> GetVendorRoster(
        VendorPortalService vendorPortalService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var vendors = await vendorPortalService.GetVendorRosterAsync(ct);
            return Results.Ok(vendors);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving vendor roster.", ex.Message);
        }
    }

    private static async Task<IResult> GetJobs(
        int vendorId,
        VendorPortalService vendorPortalService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var jobs = await vendorPortalService.GetJobsForVendorAsync(vendorId, ct);
            return Results.Ok(jobs);
        }
        catch (VendorNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Vendor not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving jobs.", ex.Message);
        }
    }

    private static async Task<IResult> GetJobStrings(
        int jobId,
        VendorPortalService vendorPortalService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var strings = await vendorPortalService.GetJobStringsAsync(jobId, ct);
            return Results.Ok(strings);
        }
        catch (MarketplaceJobNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Job not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving job strings.", ex.Message);
        }
    }

    private static async Task<IResult> UpdateJobString(
        int jobId,
        int stringId,
        VendorStringRowDto body,
        VendorPortalService vendorPortalService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var row = await vendorPortalService.UpdateJobStringAsync(jobId, stringId, body.TargetText, ct);
            return Results.Ok(row);
        }
        catch (MarketplaceJobNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Job not found.", ex.Message);
        }
        catch (LocalizationStringNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "String not found.", ex.Message);
        }
        catch (InvalidJobStateException ex)
        {
            return Problem(httpContext, StatusCodes.Status409Conflict, "Invalid job state.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error updating job string.", ex.Message);
        }
    }

    private static async Task<IResult> SubmitJob(
        int jobId,
        VendorPortalService vendorPortalService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await vendorPortalService.SubmitJobForReviewAsync(jobId, ct);
            return Results.Ok(job);
        }
        catch (MarketplaceJobNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Job not found.", ex.Message);
        }
        catch (InvalidJobStateException ex)
        {
            return Problem(httpContext, StatusCodes.Status409Conflict, "Invalid job state.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error submitting job for review.", ex.Message);
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
