using System.Net;
using System.Net.Http;
using System.Text;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class VendorPortalServiceTests
{
    private static async Task<Vendor> SeedVendorAsync(
        StudyTrackerContext db,
        string alias = "Vendor Team Test",
        string name = "Test Team")
    {
        var vendor = new Vendor { Name = name, Alias = alias, Languages = "de-DE,fr-FR" };
        db.LocalizationVendors.Add(vendor);
        await db.SaveChangesAsync();
        return vendor;
    }

    private static async Task<TranslationJob> SeedJobAsync(
        StudyTrackerContext db,
        int projectId,
        int vendorId,
        string status,
        string localeCode = "de-DE")
    {
        var job = new TranslationJob
        {
            ProjectId = projectId,
            LocaleCode = localeCode,
            Status = status,
            StringCount = 2,
            WordCount = 4,
            VendorId = vendorId,
            CreatedAt = DateTime.UtcNow
        };
        db.LocalizationTranslationJobs.Add(job);
        await db.SaveChangesAsync();
        return job;
    }

    private sealed class CountingOptimizeHandler : HttpMessageHandler
    {
        public int CallCount { get; private set; }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
        {
            CallCount++;
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(
                    "{\"optimizedTranslation\":\"opt\",\"cacheHit\":false,\"checks\":{},\"inputTokens\":10,"
                    + "\"outputTokens\":5,\"embeddingTokens\":0,\"tokensUsed\":15,\"latencyMs\":3,\"costUsd\":0.001,\"fallback\":false}",
                    Encoding.UTF8,
                    "application/json")
            });
        }
    }

    [Fact]
    public async Task GetVendorRoster_ReturnsAliasesWithoutRealNames()
    {
        using var db = LocalizationTestFixture.CreateDb();
        await SeedVendorAsync(db, "Vendor Team Larch", "Maria Fischer");
        await SeedVendorAsync(db, "Vendor Team Osprey", "Kenji Sato");
        var portal = LocalizationTestFixture.VendorPortal(db);

        var roster = await portal.GetVendorRosterAsync();

        Assert.Equal(2, roster.Count);
        Assert.Equal("Vendor Team Larch", roster[0].Alias);
        Assert.Equal("de-DE,fr-FR", roster[0].Languages);
        Assert.Equal("Vendor Team Osprey", roster[1].Alias);
    }

    [Fact]
    public async Task GetJobsForVendor_ReturnsOwnJobsNewestFirst()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        seed.Project.ClientAlias = "Client Team Kestrel";
        await db.SaveChangesAsync();
        var mine = await SeedVendorAsync(db, "Vendor Team Mine");
        var other = await SeedVendorAsync(db, "Vendor Team Other", "Other Team");
        var oldJob = await SeedJobAsync(db, seed.Project.Id, mine.Id, "Approved");
        oldJob.CreatedAt = DateTime.UtcNow.AddDays(-2);
        var newJob = await SeedJobAsync(db, seed.Project.Id, mine.Id, "Assigned");
        await SeedJobAsync(db, seed.Project.Id, other.Id, "Assigned");
        await db.SaveChangesAsync();
        var portal = LocalizationTestFixture.VendorPortal(db);

        var jobs = await portal.GetJobsForVendorAsync(mine.Id);

        Assert.Equal(2, jobs.Count);
        Assert.Equal(newJob.Id, jobs[0].Id);
        Assert.Equal(oldJob.Id, jobs[1].Id);
        Assert.All(jobs, j => Assert.Equal("Client Team Kestrel", j.ClientAlias));
    }

    [Fact]
    public async Task UpdateJobString_OnAssignedJob_SavesTargetAndReturnsVendorRow()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var job = await SeedJobAsync(db, seed.Project.Id, vendor.Id, "Assigned");
        var portal = LocalizationTestFixture.VendorPortal(db);

        var row = await portal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "Hallo Welt");

        Assert.Equal("Hallo Welt", row.TargetText);
        Assert.Equal("Translated", row.Stage);
        Assert.Null(row.Score);
        Assert.False(row.NeedsReview);

        var reloaded = await db.LocalizationTranslationJobs.AsNoTracking()
            .SingleAsync(j => j.Id == job.Id);
        Assert.Equal("InProgress", reloaded.Status);
    }

    [Fact]
    public async Task UpdateJobString_OnApprovedJob_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var job = await SeedJobAsync(db, seed.Project.Id, vendor.Id, "Approved");
        var portal = LocalizationTestFixture.VendorPortal(db);

        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => portal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "x"));
    }

    [Fact]
    public async Task UpdateJobString_OnNeedsRevision_MovesJobToInProgress()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var job = await SeedJobAsync(db, seed.Project.Id, vendor.Id, "NeedsRevision");
        var portal = LocalizationTestFixture.VendorPortal(db);

        await portal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "Hallo Welt");

        var reloaded = await db.LocalizationTranslationJobs.AsNoTracking()
            .SingleAsync(j => j.Id == job.Id);
        Assert.Equal("InProgress", reloaded.Status);
    }

    [Fact]
    public async Task UpdateJobString_OnSubmittedForReview_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var job = await SeedJobAsync(db, seed.Project.Id, vendor.Id, "SubmittedForReview");
        var portal = LocalizationTestFixture.VendorPortal(db);

        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => portal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "x"));
    }

    [Fact]
    public async Task SubmitJobForReview_TransitionsToSubmittedForReview()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        seed.Project.ClientAlias = "Client Team Kestrel";
        await db.SaveChangesAsync();
        var vendor = await SeedVendorAsync(db);
        var job = await SeedJobAsync(db, seed.Project.Id, vendor.Id, "InProgress");
        foreach (var str in seed.Strings)
        {
            db.LocalizationTranslations.Add(new LocalizationTranslation
            {
                StringId = str.Id, LocaleCode = "de-DE", TargetText = "done",
                Stage = "Translated", TranslationSource = "Marketplace", UpdatedAt = DateTime.UtcNow
            });
        }
        await db.SaveChangesAsync();
        var portal = LocalizationTestFixture.VendorPortal(db);

        var row = await portal.SubmitJobForReviewAsync(job.Id);

        Assert.Equal("SubmittedForReview", row.Status);
        Assert.Equal("Client Team Kestrel", row.ClientAlias);
        Assert.NotNull(row.SubmittedAt);
    }

    [Fact]
    public async Task UpdateJobString_SameText_AcceptsMachineDraft()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var job = await SeedJobAsync(db, seed.Project.Id, vendor.Id, "Assigned");
        db.LocalizationTranslations.Add(new LocalizationTranslation
        {
            StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "maschinell",
            RawMtText = "maschinell", Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();
        var portal = LocalizationTestFixture.VendorPortal(db);

        var row = await portal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "maschinell");

        Assert.True(row.InJob);
        Assert.True(row.VendorReviewed);
        Assert.Equal("Marketplace", row.TranslationSource);

        var stored = await db.LocalizationTranslations.AsNoTracking()
            .SingleAsync(t => t.StringId == seed.Strings[0].Id);
        Assert.Equal("Marketplace", stored.TranslationSource);
        Assert.Equal("maschinell", stored.RawMtText);

        var reloaded = await db.LocalizationTranslationJobs.AsNoTracking()
            .SingleAsync(j => j.Id == job.Id);
        Assert.Equal("InProgress", reloaded.Status);
    }

    [Fact]
    public async Task UpdateJobString_OnApprovedString_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var job = await SeedJobAsync(db, seed.Project.Id, vendor.Id, "InProgress");
        db.LocalizationTranslations.Add(new LocalizationTranslation
        {
            StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "genehmigt",
            Stage = "Approved", TranslationSource = "Marketplace", UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();
        var portal = LocalizationTestFixture.VendorPortal(db);

        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => portal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "neu"));
        Assert.Contains("already approved", ex.Message);
    }

    [Fact]
    public async Task SubmitJobForReview_WithUnreviewedMachineOutput_IsRejectedUntilAccepted()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var job = await SeedJobAsync(db, seed.Project.Id, vendor.Id, "InProgress");
        db.LocalizationTranslations.AddRange(
            new LocalizationTranslation
            {
                StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "done",
                Stage = "Translated", TranslationSource = "Marketplace", UpdatedAt = DateTime.UtcNow
            },
            new LocalizationTranslation
            {
                StringId = seed.Strings[1].Id, LocaleCode = "de-DE", TargetText = "maschinell",
                Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
            });
        await db.SaveChangesAsync();
        var portal = LocalizationTestFixture.VendorPortal(db);

        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => portal.SubmitJobForReviewAsync(job.Id));
        Assert.Contains("1 machine-translated strings still need review", ex.Message);

        await portal.UpdateJobStringAsync(job.Id, seed.Strings[1].Id, "maschinell");
        var row = await portal.SubmitJobForReviewAsync(job.Id);
        Assert.Equal("SubmittedForReview", row.Status);
    }

    [Fact]
    public async Task RunMtOptimize_SkipsVendorEditedTranslations()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.AddRange(
            new LocalizationTranslation
            {
                StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "vendor text", RawMtText = "roh1",
                Stage = "Translated", TranslationSource = "Marketplace", UpdatedAt = DateTime.UtcNow
            },
            new LocalizationTranslation
            {
                StringId = seed.Strings[1].Id, LocaleCode = "de-DE", TargetText = "alt2", RawMtText = "roh2",
                Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
            });
        await db.SaveChangesAsync();

        var handler = new CountingOptimizeHandler();
        var options = new LocalizationAiOptions { BaseUrl = "http://ai/", SharedSecret = "test-secret" };
        var client = new LocalizationAiClient(
            new HttpClient(handler),
            Microsoft.Extensions.Options.Options.Create(options),
            NullLogger<LocalizationAiClient>.Instance);
        var workflow = new WorkflowService(
            db,
            new FakeTranslationProvider(),
            new MtOptimizeService(client),
            new FakeQualityScorer(),
            new AutoRoutingService(),
            LocalizationTestFixture.Jobs(db),
            null,
            null);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Run MT Optimize", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("1 strings optimized", ran.LastRunOutcome);
        Assert.Equal(1, handler.CallCount);

        var vendor = await db.LocalizationTranslations.AsNoTracking()
            .SingleAsync(t => t.StringId == seed.Strings[0].Id);
        Assert.Equal("vendor text", vendor.TargetText);
        Assert.Equal("Marketplace", vendor.TranslationSource);
    }
}
