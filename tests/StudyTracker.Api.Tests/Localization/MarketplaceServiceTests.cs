using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class MarketplaceServiceTests
{
    [Fact]
    public async Task PostToMarketplace_UnknownLocale_ThrowsLocaleNotFound()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);

        await Assert.ThrowsAsync<LocalizationLocaleNotFoundException>(
            () => marketplace.PostToMarketplaceAsync(seed.Project.Slug, "xx-XX"));

        Assert.Empty(db.LocalizationMarketplaceJobs);
    }

    [Fact]
    public async Task PostToMarketplace_WhenJobAlreadyOpen_ThrowsAndLeavesRowUntouched()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);

        var first = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        Assert.Equal("Open", first.Status);

        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE"));
        Assert.Contains("Open", ex.Message);

        var jobs = await db.LocalizationMarketplaceJobs.AsNoTracking().ToListAsync();
        var only = Assert.Single(jobs);
        Assert.Equal(first.Id, only.Id);
        Assert.Equal("Open", only.Status);
        Assert.Equal(first.StringCount, only.StringCount);
        Assert.Equal(first.WordCount, only.WordCount);
        Assert.Equal(first.SuggestedPriceLow, only.SuggestedPriceLow);
        Assert.Equal(first.SuggestedPriceHigh, only.SuggestedPriceHigh);
        Assert.Equal(first.PostedAt, only.PostedAt);
    }

    [Fact]
    public async Task PostToMarketplace_WhenNothingLeftToTranslate_Throws()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);

        foreach (var str in seed.Strings)
        {
            db.LocalizationTranslations.Add(new LocalizationTranslation
            {
                StringId = str.Id,
                LocaleCode = "de-DE",
                TargetText = "übersetzt",
                Stage = "Translated",
                TranslationSource = "Manual",
                UpdatedAt = DateTime.UtcNow
            });
        }
        await db.SaveChangesAsync();

        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE"));
        Assert.Contains("nothing left to translate", ex.Message);

        Assert.Empty(db.LocalizationMarketplaceJobs);
    }

    [Fact]
    public async Task PostToMarketplace_AfterApproved_CreatesSecondRowAndLeavesFirstUntouched()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var first = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var bid = await vendorPortal.SubmitBidAsync(first.Id, seed.Vendor.Id, 120m, "note");
        await marketplace.AwardBidAsync(first.Id, bid.Id);
        foreach (var str in seed.Strings)
        {
            await vendorPortal.UpdateJobStringAsync(first.Id, str.Id, $"target-{str.Key}");
        }
        await vendorPortal.SubmitJobForReviewAsync(first.Id);
        await marketplace.ApproveSubmissionAsync(first.Id);

        // New source string arrives after approval, so there is work for a second job.
        var s3 = new LocalizationString { ProjectId = seed.Project.Id, Key = "k.three", SourceText = "Brand new string" };
        db.LocalizationStrings.Add(s3);
        await db.SaveChangesAsync();

        var second = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");

        Assert.NotEqual(first.Id, second.Id);
        Assert.Equal("Open", second.Status);
        Assert.Equal(1, second.StringCount);

        var jobs = await db.LocalizationMarketplaceJobs.AsNoTracking()
            .Where(j => j.LocaleCode == "de-DE")
            .OrderBy(j => j.Id)
            .ToListAsync();
        Assert.Equal(2, jobs.Count);
        Assert.Equal(first.Id, jobs[0].Id);
        Assert.Equal("Approved", jobs[0].Status);
        Assert.Equal(first.StringCount, jobs[0].StringCount);
        Assert.Equal(first.WordCount, jobs[0].WordCount);
        Assert.Equal(first.PostedAt, jobs[0].PostedAt);
    }

    [Fact]
    public async Task AwardBid_OnNonOpenJob_Throws()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var bid = await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 120m, "note");
        var awarded = await marketplace.AwardBidAsync(job.Id, bid.Id);
        Assert.Equal("Awarded", awarded.Status);

        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => marketplace.AwardBidAsync(job.Id, bid.Id));
        Assert.Contains("Awarded", ex.Message);
    }

    [Fact]
    public async Task AwardBid_DeclinesSiblingBids()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var other = new Vendor { Name = "Other Vendor", Languages = "de-DE", Rating = 4.0m };
        db.LocalizationVendors.Add(other);
        await db.SaveChangesAsync();

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var chosen = await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 120m, "first");
        var sibling = await vendorPortal.SubmitBidAsync(job.Id, other.Id, 100m, "second");

        await marketplace.AwardBidAsync(job.Id, chosen.Id);

        var bids = await db.LocalizationMarketplaceBids.AsNoTracking()
            .Where(b => b.MarketplaceJobId == job.Id)
            .ToDictionaryAsync(b => b.Id);
        Assert.Equal("Awarded", bids[chosen.Id].Status);
        Assert.Equal("Declined", bids[sibling.Id].Status);
    }

    [Fact]
    public async Task ApproveSubmission_WhenNotSubmittedForReview_Throws()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => marketplace.ApproveSubmissionAsync(job.Id));

        var bid = await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 120m, "note");
        await marketplace.AwardBidAsync(job.Id, bid.Id);
        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => marketplace.ApproveSubmissionAsync(job.Id));

        Assert.Empty(db.LocalizationLedgerEntries);
    }

    [Fact]
    public async Task SendBackForRevision_WhenNotSubmittedForReview_Throws()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => marketplace.SendBackForRevisionAsync(job.Id));
        Assert.Contains("Open", ex.Message);

        var reloaded = await db.LocalizationMarketplaceJobs.AsNoTracking().SingleAsync(j => j.Id == job.Id);
        Assert.Equal("Open", reloaded.Status);
    }

    [Fact]
    public async Task ApproveSubmission_AdvancesOnlyTranslatedStrings_AndWritesSingleLedgerEntry()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var marketplace = LocalizationTestFixture.Marketplace(db);
        var vendorPortal = LocalizationTestFixture.VendorPortal(db);

        var job = await marketplace.PostToMarketplaceAsync(seed.Project.Slug, "de-DE");
        var bid = await vendorPortal.SubmitBidAsync(job.Id, seed.Vendor.Id, 123.45m, "note");
        await marketplace.AwardBidAsync(job.Id, bid.Id);
        foreach (var str in seed.Strings)
        {
            await vendorPortal.UpdateJobStringAsync(job.Id, str.Id, $"target-{str.Key}");
        }
        await vendorPortal.SubmitJobForReviewAsync(job.Id);

        // One translation loses its target text before approval; it must stay behind.
        var blanked = await db.LocalizationTranslations
            .SingleAsync(t => t.StringId == seed.Strings[0].Id && t.LocaleCode == "de-DE");
        blanked.TargetText = "";
        blanked.Stage = "New";
        await db.SaveChangesAsync();

        var approved = await marketplace.ApproveSubmissionAsync(job.Id);
        Assert.Equal("Approved", approved.Status);

        var translations = await db.LocalizationTranslations.AsNoTracking()
            .Where(t => t.LocaleCode == "de-DE")
            .ToDictionaryAsync(t => t.StringId);
        Assert.Equal("New", translations[seed.Strings[0].Id].Stage);
        Assert.Equal("Approved", translations[seed.Strings[1].Id].Stage);

        var entries = await db.LocalizationLedgerEntries.AsNoTracking()
            .Where(e => e.RelatedMarketplaceJobId == job.Id)
            .ToListAsync();
        var entry = Assert.Single(entries);
        Assert.Equal(123.45m, entry.Amount);
        Assert.Equal("Marketplace", entry.Source);
    }
}
