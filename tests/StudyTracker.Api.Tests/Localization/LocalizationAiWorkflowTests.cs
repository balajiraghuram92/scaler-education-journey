using System.Net;
using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class LocalizationAiWorkflowTests
{
    private sealed class FakeAiHandler : HttpMessageHandler
    {
        private readonly Dictionary<string, Queue<HttpResponseMessage>> _queued = new();
        private readonly Dictionary<string, Func<string, string>> _responders = new();

        public readonly List<HttpRequestMessage> Requests = new();
        public readonly List<string> Bodies = new();

        public void QueueJson(string path, string json)
        {
            Queue(path, new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(json, Encoding.UTF8, "application/json")
            });
        }

        public void QueueStatus(string path, HttpStatusCode status)
        {
            Queue(path, new HttpResponseMessage(status) { Content = new StringContent("boom") });
        }

        public void Queue(string path, HttpResponseMessage response)
        {
            if (!_queued.TryGetValue(path, out var queue))
            {
                queue = new Queue<HttpResponseMessage>();
                _queued[path] = queue;
            }

            queue.Enqueue(response);
        }

        public void Respond(string path, Func<string, string> json)
        {
            _responders[path] = json;
        }

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
        {
            Requests.Add(request);
            var body = request.Content is null ? string.Empty : await request.Content.ReadAsStringAsync(ct);
            Bodies.Add(body);

            var path = request.RequestUri!.AbsolutePath.Trim('/');
            if (_responders.TryGetValue(path, out var responder))
            {
                return new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(responder(body), Encoding.UTF8, "application/json")
                };
            }

            if (_queued.TryGetValue(path, out var queue) && queue.Count > 0)
            {
                return queue.Dequeue();
            }

            return new HttpResponseMessage(HttpStatusCode.NotFound)
            {
                Content = new StringContent($"no scripted response for {path}")
            };
        }
    }

    private static LocalizationAiOptions AiOptions() => new()
    {
        BaseUrl = "http://ai/",
        SharedSecret = "test-secret",
        ChatPricePer1kInputTokensUsd = 1000m,
        ChatPricePer1kOutputTokensUsd = 2000m,
        LegacyMtPricePerCharUsd = 0.00002m
    };

    private static LocalizationAiClient AiClient(FakeAiHandler handler, LocalizationAiOptions options)
    {
        var http = new HttpClient(handler);
        return new LocalizationAiClient(http, Microsoft.Extensions.Options.Options.Create(options), NullLogger<LocalizationAiClient>.Instance);
    }

    private static WorkflowService Workflow(
        StudyTrackerContext db,
        LocalizationAiClient client,
        LocalizationAiOptions options)
    {
        return new WorkflowService(
            db,
            new FakeTranslationProvider(),
            new MtOptimizeService(client),
            new QpsScoringService(client),
            new AutoRoutingService(client),
            LocalizationTestFixture.Marketplace(db),
            Microsoft.Extensions.Options.Options.Create(options));
    }

    private static void RespondEchoOptimize(FakeAiHandler handler)
    {
        handler.Respond("translate-and-optimize", body =>
        {
            using var doc = JsonDocument.Parse(body);
            var raw = doc.RootElement.GetProperty("rawMtText").GetString();
            return "{\"optimizedTranslation\":\"opt:" + raw + "\",\"cacheHit\":false,\"checks\":{},"
                + "\"inputTokens\":10,\"outputTokens\":5,\"embeddingTokens\":0,\"tokensUsed\":15,"
                + "\"latencyMs\":3,\"costUsd\":0.001,\"fallback\":false}";
        });
    }

    [Fact]
    public async Task RunMtOptimize_UpdatesTargetsAndWritesTokenLedger()
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
        db.LocalizationGlossaryTerms.Add(new GlossaryTerm
        {
            ProjectId = seed.Project.Id, LocaleCode = "de-DE", SourceTerm = "Hello", TargetTerm = "Hallo"
        });
        await db.SaveChangesAsync();

        var handler = new FakeAiHandler();
        RespondEchoOptimize(handler);
        var options = AiOptions();
        var workflow = Workflow(db, AiClient(handler, options), options);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Run MT Optimize", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("2 strings optimized", ran.LastRunOutcome);

        var targets = await db.LocalizationTranslations.AsNoTracking()
            .OrderBy(t => t.TargetText).Select(t => t.TargetText).ToListAsync();
        Assert.Equal(new[] { "opt:roh1", "opt:roh2" }, targets);

        var entry = await db.LocalizationLedgerEntries.AsNoTracking().SingleAsync();
        Assert.Equal("AI", entry.Source);
        Assert.Equal("tokens", entry.UnitType);
        Assert.Equal(30, entry.UnitsConsumed);
        Assert.Equal(40m, entry.RealCostUsd);

        Assert.Equal(2, handler.Requests.Count);
        Assert.All(handler.Requests, r => Assert.Equal("test-secret", r.Headers.GetValues("x-api-key").Single()));
        Assert.All(handler.Bodies, b => Assert.Contains("Hallo", b));
    }

    [Fact]
    public async Task RunMtOptimize_PartialFailure_ContinuesAndCounts()
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
        await db.SaveChangesAsync();

        var handler = new FakeAiHandler();
        handler.QueueStatus("translate-and-optimize", HttpStatusCode.InternalServerError);
        handler.QueueJson("translate-and-optimize",
            "{\"optimizedTranslation\":\"opt-ok\",\"cacheHit\":false,\"checks\":{},\"inputTokens\":10,"
            + "\"outputTokens\":5,\"embeddingTokens\":0,\"tokensUsed\":15,\"latencyMs\":3,\"costUsd\":0.001,\"fallback\":false}");
        var options = AiOptions();
        var workflow = Workflow(db, AiClient(handler, options), options);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Run MT Optimize", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("1 strings optimized, 1 failed", ran.LastRunOutcome);

        var targets = await db.LocalizationTranslations.AsNoTracking()
            .OrderBy(t => t.TargetText).Select(t => t.TargetText).ToListAsync();
        Assert.Contains("opt-ok", targets);

        var entry = await db.LocalizationLedgerEntries.AsNoTracking().SingleAsync();
        Assert.Equal(15, entry.UnitsConsumed);
    }

    [Fact]
    public async Task ScoreQps_StoresScoreAndRawScoreOnce()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.AddRange(
            new LocalizationTranslation
            {
                StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "t1", RawMtText = "r1",
                Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
            },
            new LocalizationTranslation
            {
                StringId = seed.Strings[1].Id, LocaleCode = "de-DE", TargetText = "manual", RawMtText = "r2",
                Stage = "Translated", TranslationSource = "Manual", UpdatedAt = DateTime.UtcNow
            });
        await db.SaveChangesAsync();

        var handler = new FakeAiHandler();
        handler.QueueJson("qps-score",
            "{\"score\":85,\"flaggedIssues\":[\"tone\"],\"inputTokens\":20,\"outputTokens\":8,\"tokensUsed\":28,\"latencyMs\":4,\"costUsd\":0.002,\"fallback\":false}");
        handler.QueueJson("qps-score",
            "{\"score\":60,\"flaggedIssues\":[],\"inputTokens\":20,\"outputTokens\":8,\"tokensUsed\":28,\"latencyMs\":4,\"costUsd\":0.002,\"fallback\":false}");
        var options = AiOptions();
        var workflow = Workflow(db, AiClient(handler, options), options);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Score QPS", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("1 strings scored", ran.LastRunOutcome);
        Assert.Equal(2, handler.Requests.Count);

        var ai = await db.LocalizationTranslations.AsNoTracking()
            .SingleAsync(t => t.StringId == seed.Strings[0].Id);
        Assert.Equal(85, ai.QpsScore);
        Assert.Equal(60, ai.RawMtQpsScore);

        var manual = await db.LocalizationTranslations.AsNoTracking()
            .SingleAsync(t => t.StringId == seed.Strings[1].Id);
        Assert.Null(manual.QpsScore);
        Assert.Null(manual.RawMtQpsScore);
    }

    [Fact]
    public async Task ScoreQps_DoesNotRescoreRawWhenAlreadySet()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        db.LocalizationTranslations.Add(new LocalizationTranslation
        {
            StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "t1", RawMtText = "r1", RawMtQpsScore = 55,
            Stage = "Translated", TranslationSource = "AI", UpdatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();

        var handler = new FakeAiHandler();
        handler.QueueJson("qps-score",
            "{\"score\":90,\"flaggedIssues\":[],\"inputTokens\":1,\"outputTokens\":1,\"tokensUsed\":2,\"latencyMs\":1,\"costUsd\":0,\"fallback\":false}");
        var options = AiOptions();
        var workflow = Workflow(db, AiClient(handler, options), options);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Score QPS", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("1 strings scored", ran.LastRunOutcome);
        Assert.Single(handler.Requests);

        var row = await db.LocalizationTranslations.AsNoTracking().SingleAsync();
        Assert.Equal(90, row.QpsScore);
        Assert.Equal(55, row.RawMtQpsScore);
    }

    [Fact]
    public async Task AutoRoute_SetsNeedsReviewFromProjectThreshold()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        seed.Project.QpsThreshold = 75;
        db.LocalizationTranslations.AddRange(
            new LocalizationTranslation
            {
                StringId = seed.Strings[0].Id, LocaleCode = "de-DE", TargetText = "t1",
                Stage = "Translated", TranslationSource = "AI", QpsScore = 80, UpdatedAt = DateTime.UtcNow
            },
            new LocalizationTranslation
            {
                StringId = seed.Strings[1].Id, LocaleCode = "de-DE", TargetText = "t2",
                Stage = "Translated", TranslationSource = "AI", QpsScore = 70, UpdatedAt = DateTime.UtcNow
            },
            new LocalizationTranslation
            {
                StringId = seed.Strings[0].Id, LocaleCode = "fr-FR", TargetText = "t3",
                Stage = "Translated", TranslationSource = "AI", QpsScore = null, UpdatedAt = DateTime.UtcNow
            });
        await db.SaveChangesAsync();

        var handler = new FakeAiHandler();
        handler.Respond("auto-route", body =>
        {
            using var doc = JsonDocument.Parse(body);
            var score = doc.RootElement.GetProperty("qpsScore").GetInt32();
            var threshold = doc.RootElement.GetProperty("projectThreshold").GetInt32();
            var needs = score < threshold;
            return "{\"needsReview\":" + (needs ? "true" : "false")
                + ",\"reasons\":[],\"tokensUsed\":0,\"latencyMs\":0,\"fallback\":false}";
        });
        var options = AiOptions();
        var workflow = Workflow(db, AiClient(handler, options), options);

        var step = await workflow.AddStepAsync(seed.Project.Slug, new AddWorkflowStepRequest(null, "Auto-Route", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("2 strings processed, 1 flagged for review", ran.LastRunOutcome);
        Assert.Equal(2, handler.Requests.Count);
        Assert.All(handler.Bodies, b => Assert.Contains("\"projectThreshold\":75", b));

        var rows = await db.LocalizationTranslations.AsNoTracking()
            .OrderBy(t => t.QpsScore).ToListAsync();
        Assert.Equal(new int?[] { 70, 80 }, rows.Where(t => t.LocaleCode == "de-DE").Select(t => t.QpsScore));
        Assert.True(rows.Single(t => t.QpsScore == 70).NeedsReview);
        Assert.False(rows.Single(t => t.QpsScore == 80).NeedsReview);
        Assert.False(rows.Single(t => t.LocaleCode == "fr-FR").NeedsReview);
    }

    [Fact]
    public async Task AutoTranslate_WritesCharactersLedgerEntry()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var options = AiOptions();
        // No AI calls happen on this path; the client is never touched.
        var workflow = Workflow(db, AiClient(new FakeAiHandler(), options), options);

        var step = await workflow.AddStepAsync(
            seed.Project.Slug, new AddWorkflowStepRequest(null, "Auto-Translate via Google MT", null));
        var ran = await workflow.RunStepAsync(seed.Project.Slug, step.Id);

        Assert.Equal("4 strings translated via Google MT", ran.LastRunOutcome);

        var rows = await db.LocalizationTranslations.AsNoTracking().ToListAsync();
        Assert.Equal(4, rows.Count);
        Assert.All(rows, t => Assert.Equal(t.TargetText, t.RawMtText));

        var entry = await db.LocalizationLedgerEntries.AsNoTracking().SingleAsync();
        Assert.Equal("AI", entry.Source);
        Assert.Equal("characters", entry.UnitType);
        Assert.Equal(74, entry.UnitsConsumed);
        Assert.Equal(0.00148m, entry.RealCostUsd);
    }

    [Fact]
    public async Task Phase3Actions_NotConfigured_ThrowNotImplemented()
    {
        var handler = new FakeAiHandler();
        var unconfigured = new LocalizationAiOptions();
        var client = AiClient(handler, unconfigured);

        var mtEx = await Assert.ThrowsAsync<NotImplementedException>(
            () => new MtOptimizeService(client).OptimizeAsync("r", "s", "de-DE", CancellationToken.None));
        var qpsEx = await Assert.ThrowsAsync<NotImplementedException>(
            () => new QpsScoringService(client).ScoreAsync("s", "t", "de-DE", CancellationToken.None));
        var routeEx = await Assert.ThrowsAsync<NotImplementedException>(
            () => new AutoRoutingService(client).ShouldRouteToReviewAsync(80, 70, CancellationToken.None));

        Assert.Contains("not configured", mtEx.Message);
        Assert.Contains("not configured", qpsEx.Message);
        Assert.Contains("not configured", routeEx.Message);
        Assert.Empty(handler.Requests);

        // A missing client is the same 501 path.
        await Assert.ThrowsAsync<NotImplementedException>(
            () => new MtOptimizeService().OptimizeAsync("r", "s", "de-DE", CancellationToken.None));
    }
}
