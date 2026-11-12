using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class WorkflowServiceTests
{
    private static async Task SeedAgreementAsync(StudyTrackerContext db, int projectId)
    {
        var vendor = new Vendor { Name = "Team", Alias = "Vendor Team Test", Languages = "de-DE,fr-FR" };
        db.LocalizationVendors.Add(vendor);
        await db.SaveChangesAsync();

        var agreement = new ServiceAgreement
        {
            ProjectId = projectId,
            Tier = ServiceTiers.Gold,
            ValidFrom = DateTime.UtcNow.AddDays(-1),
            CreatedAt = DateTime.UtcNow
        };
        db.LocalizationServiceAgreements.Add(agreement);
        await db.SaveChangesAsync();

        db.LocalizationTeamAssignments.AddRange(
            new TeamAssignment { AgreementId = agreement.Id, VendorId = vendor.Id, LocaleCode = "de-DE", MemberCount = 6 },
            new TeamAssignment { AgreementId = agreement.Id, VendorId = vendor.Id, LocaleCode = "fr-FR", MemberCount = 6 });
        await db.SaveChangesAsync();
    }

    [Fact]
    public async Task CreateTranslationJobsAction_MatchesDirectCall()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        await SeedAgreementAsync(db, seed.Project.Id);
        var jobs = LocalizationTestFixture.Jobs(db);
        var workflow = LocalizationTestFixture.Workflow(db);

        var direct = await jobs.CreateJobAsync(seed.Project.Slug, "fr-FR");
        Assert.Equal(2, direct.StringCount);
        Assert.Equal(4, direct.WordCount);

        var step = await workflow.AddStepAsync(
            seed.Project.Slug, new AddWorkflowStepRequest(null, "Create Translation Jobs", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("1 jobs created, 1 skipped", ran.LastRunOutcome);

        var viaWorkflow = await db.LocalizationTranslationJobs.AsNoTracking()
            .SingleAsync(j => j.LocaleCode == "de-DE");
        Assert.Equal("Assigned", viaWorkflow.Status);
        Assert.Equal(direct.StringCount, viaWorkflow.StringCount);
        Assert.Equal(direct.WordCount, viaWorkflow.WordCount);
    }

    [Fact]
    public async Task CreateTranslationJobsAction_SkipsLocalesWithNothingLeftToTranslate()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        await SeedAgreementAsync(db, seed.Project.Id);
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
            seed.Project.Slug, new AddWorkflowStepRequest(null, "Create Translation Jobs", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("0 jobs created, 2 skipped", ran.LastRunOutcome);
        Assert.Empty(db.LocalizationTranslationJobs);
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
            LocalizationTestFixture.Jobs(db),
            null,
            null);

        foreach (var action in new[] { "Run MT Optimize", "Score Quality", "Auto-Route" })
        {
            var step = await workflow.AddStepAsync(
                seed.Project.Slug, new AddWorkflowStepRequest(null, action, null));
            await Assert.ThrowsAsync<NotImplementedException>(
                () => workflow.RunStepAsync(seed.Project.Slug, step.Id));
        }
    }
}
