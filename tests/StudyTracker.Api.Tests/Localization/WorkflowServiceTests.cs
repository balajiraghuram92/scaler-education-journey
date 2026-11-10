using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class WorkflowServiceTests
{
    [Fact]
    public async Task PostToMarketplaceAction_MatchesDirectCall()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var workflow = LocalizationTestFixture.Workflow(db);

        var direct = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "fr-FR");
        Assert.Equal(2, direct.StringCount);
        Assert.Equal(4, direct.WordCount);

        var step = await workflow.AddStepAsync(
            seed.Project.Slug, new AddWorkflowStepRequest(null, "Post to Marketplace", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("1 marketplace jobs posted, 1 skipped", ran.LastRunOutcome);

        var viaWorkflow = await db.LocalizationMarketplaceJobs.AsNoTracking()
            .SingleAsync(j => j.LocaleCode == "de-DE");
        Assert.Equal("Open", viaWorkflow.Status);
        Assert.Equal(direct.StringCount, viaWorkflow.StringCount);
        Assert.Equal(direct.WordCount, viaWorkflow.WordCount);
        Assert.Equal(direct.SuggestedPriceLow, viaWorkflow.SuggestedPriceLow);
        Assert.Equal(direct.SuggestedPriceHigh, viaWorkflow.SuggestedPriceHigh);
    }

    [Fact]
    public async Task PostToMarketplaceAction_SkipsLocalesWithNothingLeftToTranslate()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var workflow = LocalizationTestFixture.Workflow(db);

        foreach (var locale in new[] { "de-DE", "fr-FR" })
        {
            foreach (var str in seed.Strings)
            {
                db.LocalizationTranslations.Add(new LocalizationTranslation
                {
                    StringId = str.Id,
                    LocaleCode = locale,
                    TargetText = "done",
                    Stage = "Translated",
                    TranslationSource = "Manual",
                    UpdatedAt = DateTime.UtcNow
                });
            }
        }
        await db.SaveChangesAsync();

        var step = await workflow.AddStepAsync(
            seed.Project.Slug, new AddWorkflowStepRequest(null, "Post to Marketplace", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("0 marketplace jobs posted, 2 skipped", ran.LastRunOutcome);
        Assert.Empty(db.LocalizationMarketplaceJobs);
    }

    [Fact]
    public async Task AddStep_UnknownAction_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var workflow = LocalizationTestFixture.Workflow(db);

        await Assert.ThrowsAsync<ArgumentException>(
            () => workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Teleport", null)));

        Assert.Empty(db.LocalizationWorkflowSteps);
    }

    [Fact]
    public async Task UpdateStep_UnknownTrigger_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var workflow = LocalizationTestFixture.Workflow(db);

        var step = await workflow.AddStepAsync(
            seed.Project.Slug, new AddWorkflowStepRequest(null, "Mark Translated", null));

        await Assert.ThrowsAsync<ArgumentException>(
            () => workflow.UpdateStepAsync(
                seed.Project.Slug, step.Id, new UpdateWorkflowStepRequest("On Full Moon", "Mark Translated", null)));
    }

    [Fact]
    public async Task RunStep_UnknownAction_ThrowsInvalidOperationException()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var workflow = LocalizationTestFixture.Workflow(db);

        // Bypass AddStepAsync validation to simulate a row written before validation existed.
        var legacy = new WorkflowStep
        {
            ProjectId = seed.Project.Id,
            Order = 1,
            Trigger = "On Manual Click",
            Action = "Legacy Mystery Action"
        };
        db.LocalizationWorkflowSteps.Add(legacy);
        await db.SaveChangesAsync();

        await Assert.ThrowsAsync<InvalidOperationException>(
            () => workflow.RunStepAsync(seed.Project.Slug, legacy.Id));
    }

    [Fact]
    public async Task RunStep_Phase3Actions_StillSurfaceNotImplemented()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        // Production wiring: the real QpsScoringService stub, not the fake scorer.
        var workflow = new WorkflowService(
            db,
            new FakeTranslationProvider(),
            new MtOptimizeService(),
            new QpsScoringService(),
            new AutoRoutingService(),
            LocalizationTestFixture.Marketplace(db));

        foreach (var action in new[] { "Run MT Optimize", "Score QPS", "Auto-Route" })
        {
            var step = await workflow.AddStepAsync(
                seed.Project.Slug, new AddWorkflowStepRequest(null, action, null));
            await Assert.ThrowsAsync<NotImplementedException>(
                () => workflow.RunStepAsync(seed.Project.Slug, step.Id));
        }
    }
}
