using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
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
}
