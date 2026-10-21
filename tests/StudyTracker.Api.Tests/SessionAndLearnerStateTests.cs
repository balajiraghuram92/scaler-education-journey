using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services;
using StudyTracker.Api.Services.Auth;
using Xunit;

namespace StudyTracker.Api.Tests;

public class SessionAndLearnerStateTests
{
    private static readonly AuthOptions Options = new()
    {
        JwtSigningKey = "test-signing-key-that-is-at-least-32-bytes-long!!",
        JwtIssuer = "neuralascent",
        JwtAudience = "neuralascent-app",
        AccessTokenMinutes = 30,
        RememberMeDays = 30,
        SessionHours = 24,
        IdleTimeoutDays = 14,
        RefreshReuseGraceSeconds = 60
    };

    private static StudyTrackerContext NewDb() =>
        new(new DbContextOptionsBuilder<StudyTrackerContext>()
            .UseInMemoryDatabase($"learner-state-{Guid.NewGuid()}")
            .Options);

    private static SessionService NewSessions(StudyTrackerContext db) =>
        new(db, new JwtTokenService(Microsoft.Extensions.Options.Options.Create(Options)), Microsoft.Extensions.Options.Options.Create(Options), new MemoryCache(new MemoryCacheOptions()), NullLogger<SessionService>.Instance);

    private static AppUser AddUser(StudyTrackerContext db, string status = "Approved")
    {
        var user = new AppUser { Email = $"{Guid.NewGuid():N}@example.com", PasswordHash = "h", PasswordSalt = "s", Role = "User", Status = status };
        db.Users.Add(user);
        db.SaveChanges();
        return user;
    }

    private static Dictionary<string, string> SetCookies(HttpContext ctx) =>
        ctx.Response.Headers.SetCookie
            .Select(h => h!.Split(';')[0])
            .Where(pair => pair.Contains('='))
            .ToDictionary(pair => pair[..pair.IndexOf('=')], pair => pair[(pair.IndexOf('=') + 1)..]);

    private static HttpContext RequestWithRefresh(string token)
    {
        var ctx = new DefaultHttpContext();
        ctx.Request.Headers.Cookie = $"na_refresh={token}";
        return ctx;
    }

    [Fact]
    public async Task StartSession_WritesShortLivedAccessTokenWithSessionClaim_AndHashedRefreshToken()
    {
        using var db = NewDb();
        var user = AddUser(db);
        var ctx = new DefaultHttpContext();

        var session = await NewSessions(db).StartSessionAsync(user, rememberMe: true, ctx);

        var cookies = SetCookies(ctx);
        Assert.True(cookies.ContainsKey("na_auth"));
        Assert.True(cookies.ContainsKey("na_refresh"));

        var jwt = new JwtSecurityTokenHandler().ReadJwtToken(cookies["na_auth"]);
        Assert.Equal(session.Id.ToString(), jwt.Claims.First(c => c.Type == HttpContextCurrentUser.SessionIdClaim).Value);
        Assert.True(jwt.ValidTo <= DateTime.UtcNow.AddMinutes(31));

        // Only the hash is stored, never the raw token.
        Assert.Equal(SessionService.Hash(cookies["na_refresh"]), session.RefreshTokenHash);
        Assert.NotEqual(cookies["na_refresh"], session.RefreshTokenHash);
        Assert.True(session.ExpiresAt > DateTime.UtcNow.AddDays(29));
    }

    [Fact]
    public async Task Refresh_RotatesToken_AndOldTokenAfterGraceRevokesSession()
    {
        using var db = NewDb();
        var user = AddUser(db);
        var sessions = NewSessions(db);
        var login = new DefaultHttpContext();
        var session = await sessions.StartSessionAsync(user, rememberMe: false, login);
        var firstToken = SetCookies(login)["na_refresh"];

        var refreshCtx = RequestWithRefresh(firstToken);
        var result = await sessions.RefreshAsync(refreshCtx);
        Assert.Equal(RefreshOutcome.Refreshed, result.Outcome);
        var secondToken = SetCookies(refreshCtx)["na_refresh"];
        Assert.NotEqual(firstToken, secondToken);

        // Re-presenting the rotated-out token inside the grace window is a benign tab race.
        var raceResult = await sessions.RefreshAsync(RequestWithRefresh(firstToken));
        Assert.Equal(RefreshOutcome.Refreshed, raceResult.Outcome);

        // Outside the grace window it is treated as theft and the whole session is revoked.
        var stored = db.UserSessions.Single(s => s.Id == session.Id);
        stored.RotatedAt = DateTime.UtcNow.AddMinutes(-5);
        db.SaveChanges();

        var reuse = await sessions.RefreshAsync(RequestWithRefresh(firstToken));
        Assert.Equal(RefreshOutcome.ReuseDetected, reuse.Outcome);
        Assert.NotNull(db.UserSessions.Single(s => s.Id == session.Id).RevokedAt);

        var afterRevoke = await sessions.RefreshAsync(RequestWithRefresh(secondToken));
        Assert.Equal(RefreshOutcome.Revoked, afterRevoke.Outcome);
    }

    [Fact]
    public async Task Refresh_FailsForIdleSessions_AndDisabledUsers()
    {
        using var db = NewDb();
        var sessions = NewSessions(db);

        var idleUser = AddUser(db);
        var idleLogin = new DefaultHttpContext();
        var idle = await sessions.StartSessionAsync(idleUser, rememberMe: true, idleLogin);
        db.UserSessions.Single(s => s.Id == idle.Id).LastSeenAt = DateTime.UtcNow.AddDays(-20);
        db.SaveChanges();
        Assert.Equal(RefreshOutcome.Expired, (await sessions.RefreshAsync(RequestWithRefresh(SetCookies(idleLogin)["na_refresh"]))).Outcome);

        var disabledUser = AddUser(db);
        var disabledLogin = new DefaultHttpContext();
        await sessions.StartSessionAsync(disabledUser, rememberMe: true, disabledLogin);
        disabledUser.Status = "Disabled";
        db.SaveChanges();
        Assert.Equal(RefreshOutcome.UserInactive, (await sessions.RefreshAsync(RequestWithRefresh(SetCookies(disabledLogin)["na_refresh"]))).Outcome);

        Assert.Equal(RefreshOutcome.Missing, (await sessions.RefreshAsync(new DefaultHttpContext())).Outcome);
        Assert.Equal(RefreshOutcome.Invalid, (await sessions.RefreshAsync(RequestWithRefresh("not-a-real-token"))).Outcome);
    }

    [Fact]
    public async Task RevokeAll_EndsEverySession_AndActiveCheckReflectsIt()
    {
        using var db = NewDb();
        var user = AddUser(db);
        var sessions = NewSessions(db);
        var a = await sessions.StartSessionAsync(user, true, new DefaultHttpContext());
        var b = await sessions.StartSessionAsync(user, false, new DefaultHttpContext());

        Assert.Equal(2, (await sessions.ListActiveAsync(user.Id, a.Id)).Count);
        Assert.True((await sessions.ListActiveAsync(user.Id, a.Id)).Single(s => s.Id == a.Id).IsCurrent);

        Assert.Equal(2, await sessions.RevokeAllAsync(user.Id, null, "LogoutAll"));
        Assert.False(await sessions.IsSessionActiveAsync(a.Id, user.Id));
        Assert.False(await sessions.IsSessionActiveAsync(b.Id, user.Id));
        Assert.Empty(await sessions.ListActiveAsync(user.Id, null));

        // A session cannot be revoked through another account.
        var other = AddUser(db);
        var c = await sessions.StartSessionAsync(other, true, new DefaultHttpContext());
        Assert.False(await sessions.RevokeAsync(c.Id, user.Id, "x"));
        Assert.True(await sessions.IsSessionActiveAsync(c.Id, other.Id));
    }

    private static (Course course, Lesson first, Lesson second, Problem problem) AddCourse(StudyTrackerContext db)
    {
        var course = new Course { Slug = "python-engineering", Title = "Python", Description = "d", OrderIndex = 2 };
        db.Courses.Add(course);
        db.SaveChanges();
        var module = new CourseModule { CourseId = course.Id, Slug = "m1", Title = "Module 1", Description = "d", Badge = "Module 1", OrderIndex = 1 };
        db.Modules.Add(module);
        db.SaveChanges();
        var first = new Lesson { ModuleId = module.Id, Slug = "py-01", Title = "One", OrderIndex = 1 };
        var second = new Lesson { ModuleId = module.Id, Slug = "py-02", Title = "Two", OrderIndex = 2 };
        db.Lessons.AddRange(first, second);
        db.SaveChanges();
        var problem = new Problem { LessonId = first.Id, Slug = "p1", Title = "Problem", Language = "python" };
        db.Problems.Add(problem);
        db.SaveChanges();
        return (course, first, second, problem);
    }

    [Fact]
    public async Task LessonProgress_IsPerUser_AndResumePointsToLastAndNext()
    {
        using var db = NewDb();
        var (_, first, second, _) = AddCourse(db);
        var alice = AddUser(db);
        var bob = AddUser(db);
        var progress = new LearnerProgressService(db, NullLogger<LearnerProgressService>.Instance);

        await progress.RecordVisitAsync(alice.Id, first.Id);
        await progress.UpdatePositionAsync(alice.Id, first.Id, new LessonPositionRequest("concepts-covered", 140, 9999));
        var completed = await progress.SetLessonCompletionAsync(alice.Id, first.Id, true);

        Assert.True(completed!.IsCompleted);
        Assert.Equal("concepts-covered", completed.LastSectionId);
        Assert.Equal(100, completed.ScrollPercent);       // clamped
        Assert.Equal(300, completed.TimeSpentSeconds);     // heartbeat capped

        Assert.Contains(first.Id, await progress.GetCompletedLessonIdsAsync(alice.Id));
        Assert.Empty(await progress.GetCompletedLessonIdsAsync(bob.Id));
        Assert.Empty(await progress.GetCompletedLessonIdsAsync(null));

        var resume = await progress.GetResumeAsync(alice.Id);
        Assert.Equal(first.Id, resume.LastLesson!.LessonId);
        Assert.Equal("python-engineering/m1/py-01", resume.LastLesson.FullSlug);
        Assert.Equal(second.Id, resume.NextLesson!.LessonId);

        var events = await progress.GetActivityAsync(alice.Id, 10, null);
        Assert.Contains(events, e => e.EventType == "LessonOpened");
        Assert.Contains(events, e => e.EventType == "LessonCompleted");
        Assert.Empty(await progress.GetActivityAsync(bob.Id, 10, null));
    }

    [Fact]
    public async Task ProblemStatus_TracksSolvedAndRevealedSolution()
    {
        using var db = NewDb();
        var (_, _, _, problem) = AddCourse(db);
        var user = AddUser(db);
        var progress = new LearnerProgressService(db, NullLogger<LearnerProgressService>.Instance);

        var revealed = await progress.SetProblemStatusAsync(user.Id, problem.Id, new ProblemStatusRequest("Attempted", true));
        Assert.NotNull(revealed!.SolutionRevealedAt);
        var solved = await progress.SetProblemStatusAsync(user.Id, problem.Id, new ProblemStatusRequest("Solved", null));
        Assert.NotNull(solved!.SolvedAt);
        Assert.Contains(problem.Id, await progress.GetSolvedProblemIdsAsync(user.Id));

        await Assert.ThrowsAsync<ArgumentException>(() => progress.SetProblemStatusAsync(user.Id, problem.Id, new ProblemStatusRequest("Bogus", null)));
        Assert.Null(await progress.SetProblemStatusAsync(user.Id, 99999, new ProblemStatusRequest("Solved", null)));
    }

    [Fact]
    public async Task Mcq_RestoresPreviousAttempt_EnforcesOwnership_AndSupportsRetry()
    {
        using var db = NewDb();
        var (_, first, _, _) = AddCourse(db);
        var alice = AddUser(db);
        var bob = AddUser(db);

        var question = new McqQuestion
        {
            LessonId = first.Id,
            LegacyKey = "python-engineering/py-01/checkpoint/g01",
            QuestionText = "Q?",
            Explanation = "**Answer: (b)**",
            Category = "Checkpoint",
            Options = new List<McqOption>
            {
                new() { OptionKey = "a", OptionText = "A" },
                new() { OptionKey = "b", OptionText = "B", IsCorrect = true }
            }
        };
        db.McqQuestions.Add(question);
        db.SaveChanges();

        var mcq = new McqService(db, NullLogger<McqService>.Instance);
        var presented = (await mcq.GetPracticeQuestionsAsync("python-engineering", "m1", "py-01", alice.Id)).Single();
        Assert.Equal("Checkpoint", presented.Category);
        Assert.Null(presented.PreviousAttempt);

        // Reloading before answering reuses the same presentation (no row explosion).
        var reloaded = (await mcq.GetPracticeQuestionsAsync("python-engineering", "m1", "py-01", alice.Id)).Single();
        Assert.Equal(presented.PresentationId, reloaded.PresentationId);

        await Assert.ThrowsAsync<McqAccessDeniedException>(() => mcq.RecordAttemptAsync(presented.PresentationId, "b", bob.Id));
        await Assert.ThrowsAsync<ArgumentException>(() => mcq.RecordAttemptAsync(presented.PresentationId, "z", alice.Id));

        var result = await mcq.RecordAttemptAsync(presented.PresentationId, "a", alice.Id);
        Assert.False(result.IsCorrect);
        Assert.Equal("b", result.CorrectOptionKey);

        var restored = (await mcq.GetPracticeQuestionsAsync("python-engineering", "m1", "py-01", alice.Id)).Single();
        Assert.Equal("a", restored.PreviousAttempt!.SelectedOptionKey);
        Assert.Equal("b", restored.PreviousAttempt.CorrectOptionKey);
        Assert.Equal(1, restored.AttemptCount);

        var retry = await mcq.RetryAsync(restored.PresentationId, alice.Id);
        Assert.NotEqual(restored.PresentationId, retry.PresentationId);
        Assert.Null(retry.PreviousAttempt);
        await mcq.RecordAttemptAsync(retry.PresentationId, "b", alice.Id);

        var progress = new LearnerProgressService(db, NullLogger<LearnerProgressService>.Instance);
        var latest = await progress.GetLatestAttemptsAsync(alice.Id);
        Assert.Single(latest);
        Assert.True(latest[0].IsCorrect); // latest attempt wins

        var summary = await progress.GetSummaryAsync(alice.Id);
        Assert.Equal(1, summary.TotalMcqAnswered);
        Assert.Equal(1, summary.TotalMcqCorrect);
        Assert.Contains(await progress.GetActivityAsync(alice.Id, 10, null), e => e.EventType == "McqAnswered");
    }

    [Fact]
    public void PythonSeeder_BuildsCourseFromContentFiles_AndIsIdempotent()
    {
        var root = System.IO.Path.Combine(System.IO.Path.GetTempPath(), $"py-content-{Guid.NewGuid():N}");
        System.IO.Directory.CreateDirectory(System.IO.Path.Combine(root, "lessons"));
        System.IO.Directory.CreateDirectory(System.IO.Path.Combine(root, "assignments"));
        System.IO.File.WriteAllText(System.IO.Path.Combine(root, "course.json"), """
        { "slug": "python-engineering", "title": "Python", "description": "d", "verticalName": "Python Engineering", "orderIndex": 2,
          "modules": [ { "slug": "m1", "title": "Module 1", "description": "d", "badge": "Module 1",
            "lessons": [ { "slug": "py-01", "title": "One", "description": "d", "minutes": 70, "difficulty": "Advanced", "reference": "https://docs.python.org" },
                         { "slug": "py-02", "title": "Two", "description": "d", "minutes": 60 } ] } ] }
        """);
        System.IO.File.WriteAllText(System.IO.Path.Combine(root, "lessons", "py-01.md"), "# One\r\n\r\n## Concepts Covered\r\nBody\r\n");
        System.IO.File.WriteAllText(System.IO.Path.Combine(root, "assignments", "py-01.json"), """
        { "lessonSlug": "py-01", "assignments": [ { "slug": "py-01-a", "title": "A", "difficulty": "Core", "source": "FROM_MATERIAL", "problemStatement": "x", "referenceSolution": "y" } ] }
        """);

        try
        {
            using var db = NewDb();
            PythonCurriculumSeedData.Seed(db, root);
            PythonCurriculumSeedData.Seed(db, root);

            var lessons = db.Lessons.OrderBy(l => l.OrderIndex).ToList();
            Assert.Equal(2, lessons.Count);
            Assert.Equal("Draft", lessons[0].ContentStatus);
            Assert.Equal("Outline", lessons[1].ContentStatus);
            Assert.Equal("Advanced", lessons[0].Difficulty);
            Assert.Single(db.Courses);
            var problem = db.Problems.Single();
            Assert.Equal("python", problem.Language);
            Assert.Equal("pytest -q", problem.RunCommand);
            Assert.Equal("y", problem.ReferenceSolution);

            // A published lesson stays published until its file actually changes.
            lessons[0].ContentStatus = "Published";
            db.SaveChanges();
            PythonCurriculumSeedData.Seed(db, root);
            Assert.Equal("Published", db.Lessons.Single(l => l.Slug == "py-01").ContentStatus);

            System.IO.File.WriteAllText(System.IO.Path.Combine(root, "lessons", "py-01.md"), "# One\n\n## Concepts Covered\nRevised\n");
            PythonCurriculumSeedData.Seed(db, root);
            var revised = db.Lessons.Single(l => l.Slug == "py-01");
            Assert.Contains("Revised", revised.ContentBody);
            Assert.Equal("Draft", revised.ContentStatus);
        }
        finally
        {
            System.IO.Directory.Delete(root, recursive: true);
        }
    }
}
