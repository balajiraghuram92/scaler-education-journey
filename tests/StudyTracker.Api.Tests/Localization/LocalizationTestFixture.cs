using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Services.Localization;

namespace StudyTracker.Api.Tests.Localization;

public sealed class FakeTranslationProvider : ITranslationProvider
{
    public Task<string> TranslateAsync(string sourceText, string sourceLocale, string targetLocale, CancellationToken ct)
    {
        return Task.FromResult($"[{targetLocale}]{sourceText}");
    }
}

public sealed class FakeQualityScorer : IQualityScorer
{
    public Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct)
    {
        return Task.FromResult(new QualityScoreResult(90, Array.Empty<string>()));
    }
}

public static class LocalizationTestFixture
{
    public sealed record SeededProject(LocalizationProject Project, LocalizationString[] Strings, Vendor Vendor);

    public static StudyTrackerContext CreateDb()
    {
        return new StudyTrackerContext(new DbContextOptionsBuilder<StudyTrackerContext>()
            .UseInMemoryDatabase($"loc-{Guid.NewGuid()}").Options);
    }

    public static async Task<SeededProject> SeedProjectAsync(
        StudyTrackerContext db,
        string slug = "test-proj",
        string vendorLanguages = "de-DE,fr-FR")
    {
        var project = new LocalizationProject
        {
            Slug = slug,
            Name = "Test Project",
            SourceLocale = "en-US",
            CreatedAt = DateTime.UtcNow
        };
        db.LocalizationProjects.Add(project);
        await db.SaveChangesAsync();

        db.LocalizationLocales.AddRange(
            new LocalizationLocale { ProjectId = project.Id, LocaleCode = "de-DE", DisplayName = "German" },
            new LocalizationLocale { ProjectId = project.Id, LocaleCode = "fr-FR", DisplayName = "French" });

        var s1 = new LocalizationString { ProjectId = project.Id, Key = "k.one", SourceText = "Hello world" };
        var s2 = new LocalizationString { ProjectId = project.Id, Key = "k.two", SourceText = "Goodbye moon" };
        db.LocalizationStrings.AddRange(s1, s2);

        var vendor = new Vendor { Name = "Test Vendor", Languages = vendorLanguages, Rating = 4.5m };
        db.LocalizationVendors.Add(vendor);

        await db.SaveChangesAsync();
        return new SeededProject(project, new[] { s1, s2 }, vendor);
    }

    public static MarketplaceService Marketplace(StudyTrackerContext db)
    {
        return new MarketplaceService(db, new CreditLedgerService(db));
    }

    public static VendorPortalService VendorPortal(StudyTrackerContext db)
    {
        return new VendorPortalService(db, Marketplace(db));
    }

    public static WorkflowService Workflow(StudyTrackerContext db)
    {
        return new WorkflowService(
            db,
            new FakeTranslationProvider(),
            new MtOptimizeService(),
            new FakeQualityScorer(),
            new AutoRoutingService(),
            Marketplace(db));
    }
}
