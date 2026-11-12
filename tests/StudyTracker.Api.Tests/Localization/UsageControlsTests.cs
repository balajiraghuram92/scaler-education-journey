using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class UsageControlsTests
{
    private sealed class CountingTranslationProvider : ITranslationProvider
    {
        public int CallCount { get; private set; }

        public Task<string> TranslateAsync(string sourceText, string sourceLocale, string targetLocale, CancellationToken ct)
        {
            CallCount++;
            return Task.FromResult($"[{targetLocale}]{sourceText}");
        }
    }

    private sealed class CountingScorer : IQualityScorer
    {
        public bool IsConfigured => true;

        public int CallCount { get; private set; }

        public Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct)
        {
            CallCount++;
            return Task.FromResult(new QualityScoreResult(4, Array.Empty<string>(), 20, 8));
        }
    }

    [Theory]
    [InlineData("Auto-Translate via Azure Translator")]
    [InlineData("Run MT Optimize")]
    [InlineData("Score Quality")]
    [InlineData("Auto-Route")]
    public async Task DisabledProject_ProviderActionsThrow(string action)
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        seed.Project.AiEnabled = false;
        await db.SaveChangesAsync();
        var workflow = LocalizationTestFixture.Workflow(db);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, action, null));
        var ex = await Assert.ThrowsAsync<LocalizationAiDisabledException>(
            () => workflow.RunStepAsync(seed.Project.Slug, step.Id));
        Assert.Equal(seed.Project.Slug, ex.ProjectSlug);
    }

    [Fact]
    public async Task MtCapAlreadyReached_ThrowsWithoutCallingProvider()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationUsageCaps.Add(new LocalizationUsageCap
        {
            ProjectId = seed.Project.Id, Kind = UsageCapKinds.MachineTranslation,
            MonthlyLimit = 100, UpdatedAt = DateTime.UtcNow
        });
        var metering = new UsageMeteringService(db);
        await metering.RecordAsync(
            new UsageCallRecord(
                seed.Project.Id, null, UsageMeters.MachineTranslation, UsageOperations.MtDraft,
                "de-DE", 100, null, false, true),
            DateTime.UtcNow, CancellationToken.None);
        await db.SaveChangesAsync();

        var provider = new CountingTranslationProvider();
        var workflow = new WorkflowService(
            db,
            provider,
            new MtOptimizeService(),
            new FakeQualityScorer(),
            new AutoRoutingService(),
            LocalizationTestFixture.Jobs(db),
            null,
            metering);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Auto-Translate via Azure Translator", null));
        var ex = await Assert.ThrowsAsync<LocalizationUsageCapReachedException>(
            () => workflow.RunStepAsync(seed.Project.Slug, step.Id));

        Assert.Equal(0, provider.CallCount);
        Assert.Equal(UsageCapKinds.MachineTranslation, ex.Kind);
        Assert.Equal(100, ex.Used);
        Assert.Equal(100, ex.Limit);
    }

    [Fact]
    public async Task MtCapReachedPartWay_SkipsBeforeAndAfterKeepingTranslated()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var project = new LocalizationProject
        {
            Slug = "cap-mt", Name = "Cap MT", SourceLocale = "en-US", AiEnabled = true
        };
        db.LocalizationProjects.Add(project);
        await db.SaveChangesAsync();
        db.LocalizationLocales.Add(new LocalizationLocale
        {
            ProjectId = project.Id, LocaleCode = "de-DE", DisplayName = "German"
        });
        foreach (var length in new[] { 25, 11, 12 })
        {
            db.LocalizationStrings.Add(new LocalizationString
            {
                ProjectId = project.Id, SourceText = new string('x', length),
                CreatedAt = DateTime.UtcNow
            });
        }
        db.LocalizationUsageCaps.Add(new LocalizationUsageCap
        {
            ProjectId = project.Id, Kind = UsageCapKinds.MachineTranslation,
            MonthlyLimit = 20, UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();

        var provider = new CountingTranslationProvider();
        var workflow = new WorkflowService(
            db,
            provider,
            new MtOptimizeService(),
            new FakeQualityScorer(),
            new AutoRoutingService(),
            LocalizationTestFixture.Jobs(db),
            null,
            new UsageMeteringService(db));

        var step = await workflow.AddStepAsync(project.Slug, new AddWorkflowStepRequest(null, "Auto-Translate via Azure Translator", null));
        var ran = await workflow.RunStepAsync(project.Slug, step.Id);

        Assert.Equal(
            "1 strings translated via Azure Translator, 2 skipped: monthly machine-translation cap reached (11 of 20)",
            ran.LastRunOutcome);
        Assert.Equal(1, provider.CallCount);

        var translations = await db.LocalizationTranslations.AsNoTracking().ToListAsync();
        var kept = Assert.Single(translations, t => !string.IsNullOrWhiteSpace(t.TargetText));
        Assert.Equal("[de-DE]" + new string('x', 11), kept.TargetText);

        var events = await db.LocalizationUsageEvents.AsNoTracking().ToListAsync();
        Assert.Single(events);
    }

    [Fact]
    public async Task LlmCap_CrossingCallCompletesAndLaterCallsStop()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.AddRange(
            new LocalizationTranslation
            {
                StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "t1",
                Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
            },
            new LocalizationTranslation
            {
                StringId = seed.Strings[1].Id, LocaleCode = "de-DE", TargetText = "t2",
                Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
            });
        db.LocalizationUsageCaps.Add(new LocalizationUsageCap
        {
            ProjectId = seed.Project.Id, Kind = UsageCapKinds.Llm,
            MonthlyLimit = 25, UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();

        var scorer = new CountingScorer();
        var workflow = new WorkflowService(
            db,
            new FakeTranslationProvider(),
            new MtOptimizeService(),
            scorer,
            new AutoRoutingService(),
            LocalizationTestFixture.Jobs(db),
            null,
            new UsageMeteringService(db));

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Score Quality", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("1 strings scored, 1 skipped: monthly llm cap reached (28 of 25)", ran.LastRunOutcome);
        Assert.Equal(1, scorer.CallCount);

        var scored = await db.LocalizationUsageEvents.AsNoTracking().SingleAsync();
        Assert.True(scored.Succeeded);
        Assert.Equal(20, scored.Units);
        Assert.Equal(8, scored.UnitsOut);
    }

    [Fact]
    public async Task HighCap_RunMatchesUncappedBehaviour()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationUsageCaps.Add(new LocalizationUsageCap
        {
            ProjectId = seed.Project.Id, Kind = UsageCapKinds.MachineTranslation,
            MonthlyLimit = 1000000000, UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();

        var workflow = new WorkflowService(
            db,
            new FakeTranslationProvider(),
            new MtOptimizeService(),
            new FakeQualityScorer(),
            new AutoRoutingService(),
            LocalizationTestFixture.Jobs(db),
            null,
            new UsageMeteringService(db));

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Auto-Translate via Azure Translator", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("4 strings translated via Azure Translator", ran.LastRunOutcome);
        Assert.DoesNotContain("skipped", ran.LastRunOutcome!);

        var events = await db.LocalizationUsageEvents.AsNoTracking().ToListAsync();
        Assert.Equal(4, events.Count);
        Assert.All(events, e => Assert.Equal(UsageMeters.MachineTranslation, e.Meter));
        Assert.All(events, e => Assert.Equal(UsageOperations.MtDraft, e.Operation));
        Assert.All(events, e => Assert.Equal(step.Id, e.WorkflowStepId));
        Assert.All(events, e => Assert.Equal(0m, e.CostUsd));

        // R3 removed the ledger writes; usage events are the record now.
        Assert.Empty(db.LocalizationLedgerEntries);
    }
}
