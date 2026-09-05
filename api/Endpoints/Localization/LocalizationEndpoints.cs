using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Services.Localization;

namespace StudyTracker.Api.Endpoints.Localization;

public static class LocalizationEndpoints
{
    public static void MapLocalizationEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/localization/projects");

        group.MapGet("/", GetProjects)
            .WithName("GetLocalizationProjects");

        group.MapGet("/{slug}", GetProject)
            .WithName("GetLocalizationProject");

        group.MapGet("/{slug}/strings", GetStrings)
            .WithName("GetLocalizationStrings");

        group.MapPut("/{slug}/strings/{stringId:int}/translations/{localeCode}", UpdateTranslation)
            .WithName("UpdateLocalizationTranslation");

        group.MapGet("/{slug}/workflow", GetWorkflow)
            .WithName("GetLocalizationWorkflow");

        group.MapPost("/{slug}/workflow/steps", AddWorkflowStep)
            .WithName("AddLocalizationWorkflowStepPost");

        group.MapPut("/{slug}/workflow/steps/{stepId:int}", UpdateWorkflowStep)
            .WithName("UpdateLocalizationWorkflowStep");

        group.MapPost("/{slug}/workflow/steps/{stepId:int}/reorder", ReorderWorkflowStep)
            .WithName("ReorderLocalizationWorkflowStep");

        group.MapPost("/{slug}/workflow/steps/{stepId:int}/run", RunWorkflowStep)
            .WithName("RunLocalizationWorkflowStep");

        group.MapDelete("/{slug}/workflow/steps/{stepId:int}", DeleteWorkflowStep)
            .WithName("DeleteLocalizationWorkflowStep");

        group.MapGet("/{slug}/snapshots", GetSnapshots)
            .WithName("GetLocalizationSnapshots");

        group.MapPost("/{slug}/snapshots", CutSnapshot)
            .WithName("CutLocalizationSnapshot");
    }

    private static async Task<IResult> GetProjects(
        LocalizationProjectService projectService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var projects = await projectService.GetProjectsAsync(ct);
            return Results.Ok(projects);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving projects.", ex.Message);
        }
    }

    private static async Task<IResult> GetProject(
        string slug,
        LocalizationProjectService projectService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var project = await projectService.GetProjectAsync(slug, ct);
            return Results.Ok(project);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving project.", ex.Message);
        }
    }

    private static async Task<IResult> GetStrings(
        string slug,
        string? locale,
        LocalizationStringService stringService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var localeCode = string.IsNullOrWhiteSpace(locale) ? "de-DE" : locale;
            var strings = await stringService.GetStringsAsync(slug, localeCode, ct);
            return Results.Ok(strings);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving strings.", ex.Message);
        }
    }

    private static async Task<IResult> UpdateTranslation(
        string slug,
        int stringId,
        string localeCode,
        UpdateTranslationRequest request,
        LocalizationStringService stringService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var updated = await stringService.UpdateTranslationAsync(slug, stringId, localeCode, request, ct);
            return Results.Ok(updated);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (LocalizationStringNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "String not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error updating translation.", ex.Message);
        }
    }

    private static async Task<IResult> GetWorkflow(
        string slug,
        WorkflowService workflowService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var steps = await workflowService.GetStepsAsync(slug, ct);
            return Results.Ok(steps);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving workflow steps.", ex.Message);
        }
    }

    private static async Task<IResult> AddWorkflowStep(
        string slug,
        AddWorkflowStepRequest request,
        WorkflowService workflowService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var step = await workflowService.AddStepAsync(slug, request, ct);
            return Results.Ok(step);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error adding workflow step.", ex.Message);
        }
    }

    private static async Task<IResult> UpdateWorkflowStep(
        string slug,
        int stepId,
        UpdateWorkflowStepRequest request,
        WorkflowService workflowService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var updated = await workflowService.UpdateStepAsync(slug, stepId, request, ct);
            return Results.Ok(updated);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (WorkflowStepNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Workflow step not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error updating workflow step.", ex.Message);
        }
    }

    private static async Task<IResult> ReorderWorkflowStep(
        string slug,
        int stepId,
        ReorderWorkflowStepRequest request,
        WorkflowService workflowService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            await workflowService.ReorderStepAsync(slug, stepId, request.Direction, ct);
            return Results.Ok(new { success = true });
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (WorkflowStepNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Workflow step not found.", ex.Message);
        }
        catch (WorkflowStepBoundaryException ex)
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Boundary error.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error reordering workflow step.", ex.Message);
        }
    }

    private static async Task<IResult> RunWorkflowStep(
        string slug,
        int stepId,
        WorkflowService workflowService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var updatedStep = await workflowService.RunStepAsync(slug, stepId, ct);
            return Results.Ok(updatedStep);
        }
        catch (NotImplementedException ex)
        {
            return Problem(httpContext, StatusCodes.Status501NotImplemented, "Not yet implemented.", ex.Message);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (WorkflowStepNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Workflow step not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error running workflow step.", ex.Message);
        }
    }

    private static async Task<IResult> DeleteWorkflowStep(
        string slug,
        int stepId,
        WorkflowService workflowService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            await workflowService.DeleteStepAsync(slug, stepId, ct);
            return Results.NoContent();
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (WorkflowStepNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Workflow step not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error deleting workflow step.", ex.Message);
        }
    }

    private static async Task<IResult> GetSnapshots(
        string slug,
        SnapshotService snapshotService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var snapshots = await snapshotService.GetSnapshotsAsync(slug, ct);
            return Results.Ok(snapshots);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error retrieving snapshots.", ex.Message);
        }
    }

    private static async Task<IResult> CutSnapshot(
        string slug,
        SnapshotService snapshotService,
        HttpContext httpContext,
        CancellationToken ct)
    {
        try
        {
            var snapshot = await snapshotService.CutSnapshotAsync(slug, ct);
            return Results.Ok(snapshot);
        }
        catch (LocalizationProjectNotFoundException ex)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Project not found.", ex.Message);
        }
        catch (Exception ex)
        {
            return Problem(httpContext, StatusCodes.Status500InternalServerError, "Error cutting build snapshot.", ex.Message);
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
