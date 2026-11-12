using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Services.Localization;

namespace StudyTracker.Api.Endpoints.Localization;

public static class JobEndpoints
{
    public static void MapJobEndpoints(this IEndpointRouteBuilder app)
    {
        var projectJobsGroup = app.MapGroup("/api/localization/projects/{slug}/jobs");

        projectJobsGroup.MapGet("/", GetJobs)
            .WithName("GetLocalizationJobs");

        projectJobsGroup.MapPost("/{localeCode}", CreateJob)
            .WithName("CreateLocalizationJob");

        var jobsGroup = app.MapGroup("/api/localization/jobs");

        jobsGroup.MapPost("/{jobId:int}/approve", ApproveJob)
            .WithName("ApproveLocalizationTranslationJob");

        jobsGroup.MapPost("/{jobId:int}/send-back", SendBackJob)
            .WithName("SendBackLocalizationTranslationJob");

        app.MapGet("/api/localization/projects/{slug}/agreement", GetAgreement)
            .WithName("GetLocalizationServiceAgreement");
    }

    private static async Task<IResult> GetJobs(
        string slug,
        TranslationJobService jobService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var jobs = await jobService.GetJobsForProjectAsync(slug, ct);
            return Results.Ok(jobs);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving jobs.", ex.Message);
        }
    }

    private static async Task<IResult> CreateJob(
        string slug,
        string localeCode,
        TranslationJobService jobService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await jobService.CreateJobAsync(slug, localeCode, ct);
            return Results.Ok(job);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (LocalizationLocaleNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Locale not found.", ex.Message);
        }
        catch (InvalidJobStateException ex)
        {
            return Problem(httpContext, StatusCodes.Status409Conflict, "Invalid job state.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error creating job.", ex.Message);
        }
    }

    private static async Task<IResult> ApproveJob(
        int jobId,
        TranslationJobService jobService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await jobService.ApproveAsync(jobId, ct);
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
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error approving job.", ex.Message);
        }
    }

    private static async Task<IResult> SendBackJob(
        int jobId,
        TranslationJobService jobService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var job = await jobService.SendBackAsync(jobId, ct);
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
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error sending job back for revision.", ex.Message);
        }
    }

    private static async Task<IResult> GetAgreement(
        string slug,
        TranslationJobService jobService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var agreement = await jobService.GetAgreementAsync(slug, false, ct);
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
