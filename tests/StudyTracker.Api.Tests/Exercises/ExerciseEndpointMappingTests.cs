using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.DependencyInjection;
using StudyTracker.Api.Endpoints;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class ExerciseEndpointMappingTests
{
    [Fact]
    public void EndpointMapping_RegistersRunAndCheckRoutes()
    {
        var builder = WebApplication.CreateBuilder();
        builder.Services.AddScoped<ExerciseService>();
        builder.Services.AddSingleton<ExerciseMetadataService>();
        var app = builder.Build();

        app.MapExerciseEndpoints();

        var routeNames = ((IEndpointRouteBuilder)app).DataSources
            .SelectMany(dataSource => dataSource.Endpoints)
            .Select(endpoint => endpoint.Metadata
                .FirstOrDefault(metadata => metadata.GetType().Name == "EndpointNameMetadata")
                ?.GetType()
                .GetProperty("EndpointName")
                ?.GetValue(endpoint.Metadata.FirstOrDefault(metadata => metadata.GetType().Name == "EndpointNameMetadata")) as string)
            .Where(name => name is not null)
            .ToList();

        Assert.Contains("RunExercise", routeNames);
        Assert.Contains("CheckExercise", routeNames);
        Assert.Contains("GetExerciseMetadata", routeNames);
    }
}
