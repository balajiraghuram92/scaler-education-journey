using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Services.Localization;

namespace StudyTracker.Api.Endpoints.Localization;

public static class MarketplaceEndpoints
{
    public static void MapMarketplaceEndpoints(this IEndpointRouteBuilder app)
    {
        var projectMarketplaceGroup = app.MapGroup("/api/localization/projects/{slug}/marketplace");

        projectMarketplaceGroup.MapGet("/", GetOverview)
            .WithName("GetLocalizationMarketplaceOverview");

        projectMarketplaceGroup.MapPost("/{localeCode}/post", PostToMarketplace)
            .WithName("PostLocalizationMarketplaceJob");

        var jobsGroup = app.MapGroup("/api/localization/marketplace/jobs");

        jobsGroup.MapGet("/{jobId:int}/bids", GetBids)
            .WithName("GetLocalizationMarketplaceJobBids");

        jobsGroup.MapPost("/{jobId:int}/bids/{bidId:int}/award", AwardBid)
            .WithName("AwardLocalizationMarketplaceBid");

        jobsGroup.MapPost("/{jobId:int}/approve", ApproveSubmission)
            .WithName("ApproveLocalizationMarketplaceSubmission");

        jobsGroup.MapPost("/{jobId:int}/send-back", SendBackForRevision)
            .WithName("SendBackLocalizationMarketplaceSubmission");
    }

    private static async Task<IResult> GetOverview(
        string slug,
        MarketplaceService marketplaceService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var overview = await marketplaceService.GetLocaleOverviewAsync(slug, ct);
            return Results.Ok(overview);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving marketplace overview.", ex.Message);
        }
    }

    private static async Task<IResult> PostToMarketplace(
        string slug,
        string localeCode,
        MarketplaceService marketplaceService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await marketplaceService.PostToMarketplaceAsync(slug, localeCode, ct);
            return Results.Ok(job);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error posting to marketplace.", ex.Message);
        }
    }

    private static async Task<IResult> GetBids(
        int jobId,
        MarketplaceService marketplaceService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var bids = await marketplaceService.GetBidsAsync(jobId, ct);
            return Results.Ok(bids);
        }
        catch (MarketplaceJobNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Job not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving bids.", ex.Message);
        }
    }

    private static async Task<IResult> AwardBid(
        int jobId,
        int bidId,
        MarketplaceService marketplaceService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await marketplaceService.AwardBidAsync(jobId, bidId, ct);
            return Results.Ok(job);
        }
        catch (MarketplaceJobNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Job not found.", ex.Message);
        }
        catch (MarketplaceBidNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Bid not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error awarding bid.", ex.Message);
        }
    }

    private static async Task<IResult> ApproveSubmission(
        int jobId,
        MarketplaceService marketplaceService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await marketplaceService.ApproveSubmissionAsync(jobId, ct);
            return Results.Ok(job);
        }
        catch (MarketplaceJobNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Job not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error approving submission.", ex.Message);
        }
    }

    private static async Task<IResult> SendBackForRevision(
        int jobId,
        MarketplaceService marketplaceService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await marketplaceService.SendBackForRevisionAsync(jobId, ct);
            return Results.Ok(job);
        }
        catch (MarketplaceJobNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Job not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error sending back for revision.", ex.Message);
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
