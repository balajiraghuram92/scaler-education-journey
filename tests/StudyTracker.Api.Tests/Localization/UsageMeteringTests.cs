using System.Net;
using System.Net.Http;
using System.Text;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class UsageMeteringTests
{
    private sealed class FakeAiHandler : HttpMessageHandler
    {
        private readonly Dictionary<string, Queue<string>> _queued = new();

        public void QueueJson(string path, string json)
        {
            if (!_queued.TryGetValue(path, out var queue))
            {
                queue = new Queue<string>();
                _queued[path] = queue;
            }

            queue.Enqueue(json);
        }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
        {
            var path = request.RequestUri!.AbsolutePath.Trim('/');
            if (_queued.TryGetValue(path, out var queue) && queue.Count > 0)
            {
                return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(queue.Dequeue(), Encoding.UTF8, "application/json")
                });
            }

            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.NotFound)
            {
                Content = new StringContent($"no scripted response for {path}")
            });
        }
    }

    private sealed class TokenScorer : IQualityScorer
    {
        public bool IsConfigured => true;

        public Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct)
        {
            return Task.FromResult(new QualityScoreResult(4, Array.Empty<string>(), 20, 8));
        }
    }

    private sealed class ThrowingScorer : IQualityScorer
    {
        private readonly int _inputTokens;
        private readonly int _outputTokens;

        public ThrowingScorer(int inputTokens, int outputTokens)
        {
            _inputTokens = inputTokens;
            _outputTokens = outputTokens;
        }

        public bool IsConfigured => true;

        public Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct)
        {
            throw new LocalizationAiException("The QPS judge fell back without producing a score.")
            {
                InputTokens = _inputTokens,
                OutputTokens = _outputTokens
            };
        }
    }

    private static LocalizationAiClient AiClient(FakeAiHandler handler)
    {
        var http = new HttpClient(handler);
        return new LocalizationAiClient(
            http,
            Microsoft.Extensions.Options.Options.Create(new LocalizationAiOptions { BaseUrl = "http://ai/" }),
            NullLogger<LocalizationAiClient>.Instance);
    }

    private static WorkflowService WorkflowWithMetering(
        StudyTrackerContext db,
        ITranslationProvider? provider = null,
        MtOptimizeService? optimize = null,
        IQualityScorer? scorer = null)
    {
        return new WorkflowService(
            db,
            provider ?? new FakeTranslationProvider(),
            optimize ?? new MtOptimizeService(),
            scorer ?? new FakeQualityScorer(),
            new AutoRoutingService(),
            LocalizationTestFixture.Jobs(db),
            null,
            new UsageMeteringService(db));
    }

    [Fact]
    public async Task AutoTranslate_RecordsOneEventPerTranslatedStringLocale()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.Add(new LocalizationTranslation
        {
            StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "schon da",
            Stage = "Translated", TranslationSource = "Manual", UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();
        var workflow = WorkflowWithMetering(db);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Auto-Translate via Azure Translator", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("3 strings translated via Azure Translator", ran.LastRunOutcome);

        var events = await db.LocalizationUsageEvents.AsNoTracking().ToListAsync();
        Assert.Equal(3, events.Count);
        Assert.All(events, e => Assert.Equal(UsageMeters.MachineTranslation, e.Meter));
        Assert.All(events, e => Assert.Equal(UsageOperations.MtDraft, e.Operation));
        Assert.All(events, e => Assert.Equal(seed.Project.Id, e.ProjectId));
        Assert.All(events, e => Assert.Equal(step.Id, e.WorkflowStepId));
        Assert.All(events, e => Assert.True(e.Succeeded));
        Assert.All(events, e => Assert.False(e.CacheHit));
        Assert.All(events, e => Assert.Null(e.UnitsOut));
        Assert.All(events, e => Assert.Equal(0m, e.CostUsd));

        var german = Assert.Single(events, e => e.LocaleCode == "de-DE");
        Assert.Equal("Goodbye moon".Length, german.Units);
        Assert.Equal(
            new[] { "Hello world".Length, "Goodbye moon".Length },
            events.Where(e => e.LocaleCode == "fr-FR").Select(e => e.Units).OrderBy(u => u));
    }

    [Fact]
    public async Task MtOptimize_RecordsTokensAndZeroCostCacheHit()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.AddRange(
            new LocalizationTranslation
            {
                StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "alt1", RawMtText = "roh1",
                Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
            },
            new LocalizationTranslation
            {
                StringId = seed.Strings[1].Id, LocaleCode = "de-DE", TargetText = "alt2", RawMtText = "roh2",
                Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
            });
        db.LocalizationProviderRates.AddRange(
            new LocalizationProviderRate
            {
                Meter = UsageMeters.LlmOptimize, UnitKind = UsageUnitKinds.InputToken,
                UsdPerMillion = 2000m, ValidFrom = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc)
            },
            new LocalizationProviderRate
            {
                Meter = UsageMeters.LlmOptimize, UnitKind = UsageUnitKinds.OutputToken,
                UsdPerMillion = 4000m, ValidFrom = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc)
            });
        await db.SaveChangesAsync();

        var handler = new FakeAiHandler();
        handler.QueueJson("translate-and-optimize",
            "{\"optimizedTranslation\":\"opt-a\",\"cacheHit\":false,\"checks\":{},\"inputTokens\":10,"
            + "\"outputTokens\":5,\"tokensUsed\":15,\"latencyMs\":3,\"fallback\":false}");
        handler.QueueJson("translate-and-optimize",
            "{\"optimizedTranslation\":\"opt-b\",\"cacheHit\":true,\"checks\":{},\"inputTokens\":7,"
            + "\"outputTokens\":3,\"tokensUsed\":10,\"latencyMs\":1,\"fallback\":false}");
        var workflow = WorkflowWithMetering(db, optimize: new MtOptimizeService(AiClient(handler)));

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Run MT Optimize", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("2 strings optimized", ran.LastRunOutcome);

        var events = await db.LocalizationUsageEvents.AsNoTracking().ToListAsync();
        Assert.Equal(2, events.Count);
        Assert.All(events, e => Assert.Equal(UsageMeters.LlmOptimize, e.Meter));
        Assert.All(events, e => Assert.Equal(UsageOperations.MtOptimize, e.Operation));

        var cached = Assert.Single(events, e => e.CacheHit);
        Assert.Equal(0m, cached.CostUsd);
        var fresh = Assert.Single(events, e => !e.CacheHit);
        Assert.Equal(10, fresh.Units);
        Assert.Equal(5, fresh.UnitsOut);
        Assert.Equal(0.04m, fresh.CostUsd);
    }

    [Fact]
    public async Task QpsScore_RecordsBothCallsWithTokens()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.Add(new LocalizationTranslation
        {
            StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "t1", RawMtText = "r1",
            Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();
        var workflow = WorkflowWithMetering(db, scorer: new TokenScorer());

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Score Quality", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("1 strings scored", ran.LastRunOutcome);

        var events = await db.LocalizationUsageEvents.AsNoTracking().ToListAsync();
        Assert.Equal(2, events.Count);
        Assert.All(events, e => Assert.Equal(UsageMeters.LlmScore, e.Meter));
        Assert.All(events, e => Assert.Equal(UsageOperations.QpsScore, e.Operation));
        Assert.All(events, e => Assert.True(e.Succeeded));
        Assert.All(events, e => Assert.Equal(20, e.Units));
        Assert.All(events, e => Assert.Equal(8, e.UnitsOut));
    }

    [Fact]
    public async Task QpsScore_FailedCallWithTokens_RecordsUnsuccessfulEvent()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.Add(new LocalizationTranslation
        {
            StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "t1",
            Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();
        var workflow = WorkflowWithMetering(db, scorer: new ThrowingScorer(5, 2));

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Score Quality", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("0 strings scored, 1 failed", ran.LastRunOutcome);

        var failed = await db.LocalizationUsageEvents.AsNoTracking().SingleAsync();
        Assert.Equal(UsageMeters.LlmScore, failed.Meter);
        Assert.False(failed.Succeeded);
        Assert.Equal(5, failed.Units);
        Assert.Equal(2, failed.UnitsOut);
    }

    [Fact]
    public async Task QpsScore_FailedCallWithoutTokens_RecordsNothing()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.Add(new LocalizationTranslation
        {
            StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "t1",
            Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();
        var workflow = WorkflowWithMetering(db, scorer: new ThrowingScorer(0, 0));

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Score Quality", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("0 strings scored, 1 failed", ran.LastRunOutcome);
        Assert.Empty(db.LocalizationUsageEvents);
    }

    [Fact]
    public async Task UsageCost_UsesRateInForceAtEventTime()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationProviderRates.AddRange(
            new LocalizationProviderRate
            {
                Meter = UsageMeters.LlmScore, UnitKind = UsageUnitKinds.InputToken,
                UsdPerMillion = 1000m, ValidFrom = new DateTime(2026, 1, 10, 0, 0, 0, DateTimeKind.Utc)
            },
            new LocalizationProviderRate
            {
                Meter = UsageMeters.LlmScore, UnitKind = UsageUnitKinds.InputToken,
                UsdPerMillion = 2000m, ValidFrom = new DateTime(2026, 6, 10, 0, 0, 0, DateTimeKind.Utc)
            },
            new LocalizationProviderRate
            {
                Meter = UsageMeters.LlmScore, UnitKind = UsageUnitKinds.OutputToken,
                UsdPerMillion = 4000m, ValidFrom = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc)
            });
        await db.SaveChangesAsync();
        var metering = new UsageMeteringService(db);

        var call = new UsageCallRecord(
            seed.Project.Id, null, UsageMeters.LlmScore, UsageOperations.QpsScore,
            "de-DE", 100, 10, false, true);
        await metering.RecordAsync(call, new DateTime(2026, 3, 5, 12, 0, 0, DateTimeKind.Utc), CancellationToken.None);
        await metering.RecordAsync(call, new DateTime(2026, 7, 5, 12, 0, 0, DateTimeKind.Utc), CancellationToken.None);
        await db.SaveChangesAsync();

        var costs = await db.LocalizationUsageEvents.AsNoTracking()
            .OrderBy(e => e.OccurredAt).Select(e => e.CostUsd).ToListAsync();
        Assert.Equal(new[] { 0.14m, 0.24m }, costs);
    }

    [Fact]
    public async Task UsageCost_WithoutRate_IsZeroAndListedMissing()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var metering = new UsageMeteringService(db);

        await metering.RecordAsync(
            new UsageCallRecord(
                seed.Project.Id, null, UsageMeters.MachineTranslation, UsageOperations.MtDraft,
                "de-DE", 100, null, false, true),
            new DateTime(2026, 3, 5, 12, 0, 0, DateTimeKind.Utc),
            CancellationToken.None);
        await db.SaveChangesAsync();

        var stored = await db.LocalizationUsageEvents.AsNoTracking().SingleAsync();
        Assert.Equal(0m, stored.CostUsd);

        var summary = await metering.GetSummaryAsync(seed.Project.Slug, 2026, 3, CancellationToken.None);
        Assert.Single(summary.RatesMissing);
        Assert.Equal(UsageMeters.MachineTranslation, summary.RatesMissing[0].Meter);
        Assert.Equal(UsageUnitKinds.Char, summary.RatesMissing[0].UnitKind);
    }

    [Fact]
    public async Task UsageSummary_TotalsForOneMonthAndProjectAreExact()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var first = await LocalizationTestFixture.SeedProjectAsync(db, "slug-a");
        var second = await LocalizationTestFixture.SeedProjectAsync(db, "slug-b");
        var metering = new UsageMeteringService(db);

        UsageCallRecord Mt(int projectId, string locale, int units) => new(
            projectId, null, UsageMeters.MachineTranslation, UsageOperations.MtDraft,
            locale, units, null, false, true);
        await metering.RecordAsync(Mt(first.Project.Id, "de-DE", 100), new DateTime(2026, 3, 5, 12, 0, 0, DateTimeKind.Utc), CancellationToken.None);
        await metering.RecordAsync(
            new UsageCallRecord(
                first.Project.Id, null, UsageMeters.LlmScore, UsageOperations.QpsScore,
                "de-DE", 10, 2, false, true),
            new DateTime(2026, 3, 6, 12, 0, 0, DateTimeKind.Utc), CancellationToken.None);
        await metering.RecordAsync(Mt(first.Project.Id, "fr-FR", 50), new DateTime(2026, 4, 2, 12, 0, 0, DateTimeKind.Utc), CancellationToken.None);
        await metering.RecordAsync(Mt(second.Project.Id, "de-DE", 1000), new DateTime(2026, 3, 7, 12, 0, 0, DateTimeKind.Utc), CancellationToken.None);
        await db.SaveChangesAsync();

        var summary = await metering.GetSummaryAsync("slug-a", 2026, 3, CancellationToken.None);
        Assert.Equal("2026-03", summary.Month);
        Assert.Equal("slug-a", summary.ProjectSlug);

        var mt = Assert.Single(summary.Meters, m => m.Meter == UsageMeters.MachineTranslation);
        Assert.Equal(1, mt.Calls);
        Assert.Equal(0, mt.FailedCalls);
        Assert.Equal(0, mt.CacheHits);
        Assert.Equal(100, mt.Units);
        Assert.Null(mt.UnitsOut);
        Assert.Equal(0m, mt.CostUsd);

        var score = Assert.Single(summary.Meters, m => m.Meter == UsageMeters.LlmScore);
        Assert.Equal(1, score.Calls);
        Assert.Equal(10, score.Units);
        Assert.Equal(2, score.UnitsOut);

        Assert.Equal(2, summary.ByOperation.Count);
        var de = Assert.Single(summary.ByLocale, l => l.LocaleCode == "de-DE" && l.Meter == UsageMeters.MachineTranslation);
        Assert.Equal(100, de.Units);
        Assert.Equal(
            new[] { "2026-03-05", "2026-03-06" },
            summary.ByDay.OrderBy(d => d.Date).Select(d => d.Date));
        Assert.Equal(3, summary.RatesMissing.Count);

        var all = await metering.GetSummaryAsync(null, 2026, 3, CancellationToken.None);
        Assert.Null(all.ProjectSlug);
        Assert.Equal(1100, all.Meters.Single(m => m.Meter == UsageMeters.MachineTranslation).Units);
        Assert.Equal(10, all.Meters.Single(m => m.Meter == UsageMeters.LlmScore).Units);
    }

    [Fact]
    public async Task WorkflowWithoutMetering_RunsEveryAction()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var workflow = LocalizationTestFixture.Workflow(db);

        async Task<string> Run(string action)
        {
            var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, action, null));
            return (await workflow.RunStepAsync(seed.Project.Slug, step.Id)).LastRunOutcome!;
        }

        Assert.Equal("0 jobs created, 2 skipped", await Run("Create Translation Jobs"));
        Assert.Equal("4 strings translated via Azure Translator", await Run("Auto-Translate via Azure Translator"));
        Assert.Equal("0 strings affected", await Run("Mark Translated"));
        Assert.Equal("4 strings affected", await Run("Send to Review"));
        Assert.Equal("4 strings affected", await Run("Approve"));

        var optimizeStep = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Run MT Optimize", null));
        await Assert.ThrowsAsync<NotImplementedException>(
            () => workflow.RunStepAsync(seed.Project.Slug, optimizeStep.Id));

        Assert.Equal("0 strings scored", await Run("Score Quality"));

        var routeStep = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Auto-Route", null));
        await Assert.ThrowsAsync<NotImplementedException>(
            () => workflow.RunStepAsync(seed.Project.Slug, routeStep.Id));

        Assert.Empty(db.LocalizationUsageEvents);
    }
}
