using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class VendorPortalServiceTests
{
    [Fact]
    public async Task SubmitBid_OnNonOpenJob_Throws()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var other = new Vendor { Name = "Other Vendor", Languages = "de-DE", Rating = 4.0m };
        db.LocalizationVendors.Add(other);
        await db.SaveChangesAsync();

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var bid = await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 120m, "note");
        await marketplace.AwardBidAsync(job.Id, bid.Id);

        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => vendorPortal.SubmitBidAsync(job.Id, other.Id, 100m, "late"));
        Assert.Contains("Awarded", ex.Message);
    }

    [Fact]
    public async Task SubmitBid_VendorWithoutLanguage_ThrowsMismatch()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var japaneseOnly = new Vendor { Name = "JP Vendor", Languages = "ja-JP", Rating = 5.0m };
        db.LocalizationVendors.Add(japaneseOnly);
        await db.SaveChangesAsync();

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");

        await Assert.ThrowsAsync<VendorLanguageMismatchException>(
            () => vendorPortal.SubmitBidAsync(job.Id, japaneseOnly.Id, 100m, "note"));

        Assert.Empty(db.LocalizationMarketplaceBids);
    }

    [Fact]
    public async Task SubmitBid_DuplicatePendingBid_Throws()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 120m, "first");

        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 110m, "second"));

        Assert.Single(db.LocalizationMarketplaceBids);
    }

    [Fact]
    public async Task SubmitBid_NonPositivePrice_ThrowsArgumentException()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");

        await Assert.ThrowsAsync<ArgumentException>(
            () => vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 0m, "free"));

        Assert.Empty(db.LocalizationMarketplaceBids);
    }

    [Fact]
    public async Task UpdateJobString_OnApprovedJob_ThrowsAndLeavesTextUnchanged()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var bid = await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 120m, "note");
        await marketplace.AwardBidAsync(job.Id, bid.Id);
        foreach (var str in seed.Strings)
        {
            await vendorPortal.UpdateJobStringAsync(job.Id, str.Id, $"target-{str.Key}");
        }
        await vendorPortal.SubmitJobForReviewAsync(job.Id);
        await marketplace.ApproveSubmissionAsync(job.Id);

        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => vendorPortal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "sneaky edit"));

        var translation = await db.LocalizationTranslations.AsNoTracking()
            .SingleAsync(t => t.StringId == seed.Strings[0].Id && t.LocaleCode == "de-DE");
        Assert.Equal($"target-{seed.Strings[0].Key}", translation.TargetText);
    }

    [Fact]
    public async Task UpdateJobString_OnNeedsRevision_MovesJobToInProgress()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var bid = await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 120m, "note");
        await marketplace.AwardBidAsync(job.Id, bid.Id);
        foreach (var str in seed.Strings)
        {
            await vendorPortal.UpdateJobStringAsync(job.Id, str.Id, $"target-{str.Key}");
        }
        await vendorPortal.SubmitJobForReviewAsync(job.Id);
        var sentBack = await marketplace.SendBackForRevisionAsync(job.Id);
        Assert.Equal("NeedsRevision", sentBack.Status);

        var updated = await vendorPortal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "revised text");

        Assert.Equal("revised text", updated.TargetText);
        var reloaded = await db.LocalizationMarketplaceJobs.AsNoTracking().SingleAsync(j => j.Id == job.Id);
        Assert.Equal("InProgress", reloaded.Status);
    }

    [Fact]
    public async Task UpdateJobString_OnAwardedJob_MovesJobToInProgress()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var bid = await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 120m, "note");
        await marketplace.AwardBidAsync(job.Id, bid.Id);

        await vendorPortal.UpdateJobStringAsync(job.Id, seed.Strings[0].Id, "first edit");

        var reloaded = await db.LocalizationMarketplaceJobs.AsNoTracking().SingleAsync(j => j.Id == job.Id);
        Assert.Equal("InProgress", reloaded.Status);
    }

    [Fact]
    public async Task SubmitJobForReview_OnOpenJob_Throws()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");

        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => vendorPortal.SubmitJobForReviewAsync(job.Id));
        Assert.Contains("Open", ex.Message);
    }
}
