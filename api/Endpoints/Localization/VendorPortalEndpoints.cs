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

        group.MapGet("/roster", GetRoster)
            .WithName("GetVendorRoster");

        group.MapGet("/{vendorId:int}/open-jobs", GetOpenJobs)
            .WithName("GetVendorOpenJobs");

        group.MapPost("/{vendorId:int}/jobs/{jobId:int}/bids", SubmitBid)
            .WithName("SubmitVendorBid");

        group.MapGet("/{vendorId:int}/awarded-jobs", GetAwardedJobs)
            .WithName("GetVendorAwardedJobs");

        group.MapGet("/jobs/{jobId:int}/strings", GetJobStrings)
            .WithName("GetVendorJobStrings");

        group.MapPut("/jobs/{jobId:int}/strings/{stringId:int}", UpdateJobString)
            .WithName("UpdateVendorJobString");

        group.MapPost("/jobs/{jobId:int}/submit", SubmitJob)
            .WithName("SubmitVendorJobForReview");
    }

    private static async Task<IResult> GetRoster(
        VendorPortalService vendorService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var roster = await vendorService.GetVendorRosterAsync(ct);
            return Results.Ok(roster);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving vendor roster.", ex.Message);
        }
    }

    private static async Task<IResult> GetOpenJobs(
        int vendorId,
        VendorPortalService vendorService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var openJobs = await vendorService.GetOpenJobsForVendorAsync(vendorId, ct);
            return Results.Ok(openJobs);
        }
        catch (VendorNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Vendor not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving open jobs.", ex.Message);
        }
    }

    private static async Task<IResult> SubmitBid(
        int vendorId,
        int jobId,
        SubmitBidRequest request,
        VendorPortalService vendorService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var bid = await vendorService.SubmitBidAsync(jobId, vendorId, request.ProposedPrice, request.Note, ct);
            return Results.Ok(bid);
        }
        catch (VendorNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Vendor not found.", ex.Message);
        }
        catch (MarketplaceJobNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Job not found.", ex.Message);
        }
        catch (VendorLanguageMismatchException ex)
        {
            return Problem(httpContext, StatusCodes.Status403Forbidden, "Language mismatch.", ex.Message);
        }
        catch (InvalidJobStateException ex)
        {
            return Problem(httpContext, StatusCodes.Status409Conflict, "Invalid job state.", ex.Message);
        }
        catch (ArgumentException ex)
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Invalid bid.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error submitting bid.", ex.Message);
        }
    }

    private static async Task<IResult> GetAwardedJobs(
        int vendorId,
        VendorPortalService vendorService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var awardedJobs = await vendorService.GetAwardedJobsForVendorAsync(vendorId, ct);
            return Results.Ok(awardedJobs);
        }
        catch (VendorNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Vendor not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving awarded jobs.", ex.Message);
        }
    }

    private static async Task<IResult> GetJobStrings(
        int jobId,
        VendorPortalService vendorService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var strings = await vendorService.GetJobStringsAsync(jobId, ct);
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
        UpdateTranslationRequest request,
        VendorPortalService vendorService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var updated = await vendorService.UpdateJobStringAsync(jobId, stringId, request.TargetText, ct);
            return Results.Ok(updated);
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
        VendorPortalService vendorService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await vendorService.SubmitJobForReviewAsync(jobId, ct);
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
