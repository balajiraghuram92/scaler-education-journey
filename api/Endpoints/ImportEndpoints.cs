using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Services;

namespace StudyTracker.Api.Endpoints;

public static class ImportEndpoints
{
    public static void MapImportEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapPost("/api/v2/curriculum/import", async (CurriculumImportRequest req, CurriculumImportService service) =>
        {
            var result = await service.ImportChapterAsync(req);
            return result.Success ? Results.Ok(result) : Results.BadRequest(result);
        }).WithName("V2ImportChapter");
    }
}
