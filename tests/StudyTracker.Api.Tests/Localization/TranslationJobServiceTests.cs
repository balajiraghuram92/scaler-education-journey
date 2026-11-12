using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;
using StudyTracker.Api.Services.Localization;
using Xunit;

namespace StudyTracker.Api.Tests.Localization;

public class TranslationJobServiceTests
{
    private static async Task<Vendor> SeedVendorAsync(
        StudyTrackerContext db,
        string alias = "Vendor Team Test",
        string languages = "de-DE,fr-FR")
    {
        var vendor = new Vendor { Name = "Test Team", Alias = alias, Languages = languages };
        db.LocalizationVendors.Add(vendor);
        await db.SaveChangesAsync();
        return vendor;
    }

    private static async Task SeedAgreementAsync(
        StudyTrackerContext db,
        int projectId,
        int vendorId,
        params string[] localeCodes)
    {
        var agreement = new ServiceAgreement
        {
            ProjectId = projectId,
            Tier = ServiceTiers.Silver,
            ValidFrom = DateTime.UtcNow.AddDays(-1),
            CreatedAt = DateTime.UtcNow
        };
        db.LocalizationServiceAgreements.Add(agreement);
        await db.SaveChangesAsync();

        foreach (var localeCode in localeCodes)
        {
            db.LocalizationTeamAssignments.Add(new TeamAssignment
            {
                AgreementId = agreement.Id,
                VendorId = vendorId,
                LocaleCode = localeCode,
                MemberCount = ServiceTiers.MembersFor(ServiceTiers.Silver)
            });
        }

        await db.SaveChangesAsync();
    }

    [Fact]
    public async Task CreateJobAsync_PicksTeamFromAgreement()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        await SeedAgreementAsync(db, seed.Project.Id, vendor.Id, "de-DE", "fr-FR");
        var jobs = LocalizationTestFixture.Jobs(db);

        var row = await jobs.CreateJobAsync(seed.Project.Slug, "de-DE");

        Assert.Equal("Assigned", row.Status);
        Assert.Equal("Vendor Team Test", row.VendorTeamAlias);
        Assert.Equal(3, row.MemberCount);
        Assert.Equal(2, row.StringCount);
        Assert.NotNull(row.CreatedAt);

        var stored = await db.LocalizationTranslationJobs.AsNoTracking().SingleAsync();
        Assert.Equal(vendor.Id, stored.VendorId);
    }

    [Fact]
    public async Task CreateJobAsync_LocaleWithoutTeam_ThrowsNoTeam()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        await SeedAgreementAsync(db, seed.Project.Id, vendor.Id, "de-DE");
        var jobs = LocalizationTestFixture.Jobs(db);

        var ex = await Assert.ThrowsAsync<InvalidJobStateException>(
            () => jobs.CreateJobAsync(seed.Project.Slug, "fr-FR"));
        Assert.Contains("NO_TEAM_FOR_LOCALE", ex.Message);
    }

    [Fact]
    public async Task CreateJobAsync_ExistingNonTerminalJob_ThrowsConflict()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        await SeedAgreementAsync(db, seed.Project.Id, vendor.Id, "de-DE");
        var jobs = LocalizationTestFixture.Jobs(db);

        await jobs.CreateJobAsync(seed.Project.Slug, "de-DE");

        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => jobs.CreateJobAsync(seed.Project.Slug, "de-DE"));
        Assert.Equal(1, await db.LocalizationTranslationJobs.CountAsync());
    }

    [Fact]
    public async Task JobLifecycle_AssignedToApproved()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        await SeedAgreementAsync(db, seed.Project.Id, vendor.Id, "de-DE");
        var jobs = LocalizationTestFixture.Jobs(db);
        var portal = LocalizationTestFixture.VendorPortal(db);

        var created = await jobs.CreateJobAsync(seed.Project.Slug, "de-DE");
        Assert.Equal("Assigned", created.Status);
        Assert.NotNull(created.Id);

        await portal.UpdateJobStringAsync(created.Id!.Value, seed.Strings[0].Id, "Hallo Welt");
        await portal.UpdateJobStringAsync(created.Id!.Value, seed.Strings[1].Id, "Gute Nacht");
        var edited = await db.LocalizationTranslationJobs.AsNoTracking()
            .SingleAsync(j => j.Id == created.Id);
        Assert.Equal("InProgress", edited.Status);

        var submitted = await portal.SubmitJobForReviewAsync(created.Id!.Value);
        Assert.Equal("SubmittedForReview", submitted.Status);

        var approved = await jobs.ApproveAsync(created.Id!.Value);
        Assert.Equal("Approved", approved.Status);
        Assert.NotNull(approved.ApprovedAt);

        var stages = await db.LocalizationTranslations.AsNoTracking()
            .Where(t => t.LocaleCode == "de-DE")
            .Select(t => t.Stage)
            .ToListAsync();
        Assert.Equal(2, stages.Count);
        Assert.All(stages, s => Assert.Equal("Approved", s));
    }

    [Fact]
    public async Task ApprovedJob_RejectsFurtherEditsAndSubmits()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        await SeedAgreementAsync(db, seed.Project.Id, vendor.Id, "de-DE");
        var jobs = LocalizationTestFixture.Jobs(db);
        var portal = LocalizationTestFixture.VendorPortal(db);

        var created = await jobs.CreateJobAsync(seed.Project.Slug, "de-DE");
        await portal.UpdateJobStringAsync(created.Id!.Value, seed.Strings[0].Id, "Hallo Welt");
        await portal.UpdateJobStringAsync(created.Id!.Value, seed.Strings[1].Id, "Gute Nacht");
        await portal.SubmitJobForReviewAsync(created.Id!.Value);
        await jobs.ApproveAsync(created.Id!.Value);

        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => portal.UpdateJobStringAsync(created.Id!.Value, seed.Strings[0].Id, "x"));
        await Assert.ThrowsAsync<InvalidJobStateException>(
            () => portal.SubmitJobForReviewAsync(created.Id!.Value));
    }

    [Fact]
    public async Task SendBack_ReturnsJobToVendorLoop()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        await SeedAgreementAsync(db, seed.Project.Id, vendor.Id, "de-DE");
        var jobs = LocalizationTestFixture.Jobs(db);
        var portal = LocalizationTestFixture.VendorPortal(db);

        var created = await jobs.CreateJobAsync(seed.Project.Slug, "de-DE");
        await portal.UpdateJobStringAsync(created.Id!.Value, seed.Strings[0].Id, "Hallo Welt");
        await portal.UpdateJobStringAsync(created.Id!.Value, seed.Strings[1].Id, "Gute Nacht");
        await portal.SubmitJobForReviewAsync(created.Id!.Value);

        var sentBack = await jobs.SendBackAsync(created.Id!.Value);
        Assert.Equal("NeedsRevision", sentBack.Status);

        await portal.UpdateJobStringAsync(created.Id!.Value, seed.Strings[0].Id, "Hallo Welt!");
        var edited = await db.LocalizationTranslationJobs.AsNoTracking()
            .SingleAsync(j => j.Id == created.Id);
        Assert.Equal("InProgress", edited.Status);
    }

    [Fact]
    public async Task CompletedPercent_CountsFinishedStagesOverJobTotal()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var project = new LocalizationProject
        {
            Slug = "pct", Name = "Pct", SourceLocale = "en-US", ClientAlias = "Client Team Test"
        };
        db.LocalizationProjects.Add(project);
        await db.SaveChangesAsync();
        db.LocalizationLocales.Add(new LocalizationLocale
        {
            ProjectId = project.Id, LocaleCode = "de-DE", DisplayName = "German"
        });
        var stages = new[] { "Translated", "InReview", "Approved", "New" };
        for (var i = 0; i < stages.Length; i++)
        {
            var str = new LocalizationString
            {
                ProjectId = project.Id, Key = $"k{i}", SourceText = $"text {i}"
            };
            db.LocalizationStrings.Add(str);
            await db.SaveChangesAsync();
            db.LocalizationTranslations.Add(new LocalizationTranslation
            {
                StringId = str.Id, LocaleCode = "de-DE", TargetText = stages[i] == "New" ? null : "t",
                Stage = stages[i], TranslationSource = "Manual", UpdatedAt = DateTime.UtcNow
            });
        }
        db.LocalizationTranslationJobs.Add(new TranslationJob
        {
            ProjectId = project.Id, LocaleCode = "de-DE", Status = "InProgress",
            StringCount = 4, WordCount = 8, CreatedAt = DateTime.UtcNow
        });
        await db.SaveChangesAsync();
        var jobs = LocalizationTestFixture.Jobs(db);

        var rows = await jobs.GetJobsForProjectAsync("pct");

        var row = Assert.Single(rows);
        Assert.Equal(75, row.CompletedPercent);
    }

    [Fact]
    public async Task CompletedPercent_ZeroStrings_IsZero()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var project = new LocalizationProject
        {
            Slug = "empty", Name = "Empty", SourceLocale = "en-US", ClientAlias = "Client Team Test"
        };
        db.LocalizationProjects.Add(project);
        await db.SaveChangesAsync();
        db.LocalizationLocales.Add(new LocalizationLocale
        {
            ProjectId = project.Id, LocaleCode = "de-DE", DisplayName = "German"
        });
        await db.SaveChangesAsync();
        var jobs = LocalizationTestFixture.Jobs(db);

        var rows = await jobs.GetJobsForProjectAsync("empty");

        var row = Assert.Single(rows);
        Assert.Equal("NotCreated", row.Status);
        Assert.Equal(0, row.StringCount);
        Assert.Equal(0, row.CompletedPercent);
    }

    [Fact]
    public async Task SaveAgreement_UnknownTier_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var jobs = LocalizationTestFixture.Jobs(db);

        await Assert.ThrowsAsync<ArgumentException>(
            () => jobs.SaveAgreementAsync(seed.Project.Slug,
                new SaveAgreementRequest("Bronze", null, null, new List<AgreementTeamRequest>())));
    }

    [Fact]
    public async Task SaveAgreement_ForeignLocale_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var jobs = LocalizationTestFixture.Jobs(db);

        await Assert.ThrowsAsync<ArgumentException>(
            () => jobs.SaveAgreementAsync(seed.Project.Slug,
                new SaveAgreementRequest(ServiceTiers.Gold, null, null,
                    new List<AgreementTeamRequest>
                    {
                        new("xx-XX", vendor.Id)
                    })));
    }

    [Fact]
    public async Task SaveAgreement_UnknownTeam_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var jobs = LocalizationTestFixture.Jobs(db);

        await Assert.ThrowsAsync<ArgumentException>(
            () => jobs.SaveAgreementAsync(seed.Project.Slug,
                new SaveAgreementRequest(ServiceTiers.Gold, null, null,
                    new List<AgreementTeamRequest>
                    {
                        new("de-DE", 999)
                    })));
    }

    [Fact]
    public async Task SaveAgreement_DuplicateLocale_IsRejected()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var jobs = LocalizationTestFixture.Jobs(db);

        await Assert.ThrowsAsync<ArgumentException>(
            () => jobs.SaveAgreementAsync(seed.Project.Slug,
                new SaveAgreementRequest(ServiceTiers.Gold, null, null,
                    new List<AgreementTeamRequest>
                    {
                        new("de-DE", vendor.Id),
                        new("de-DE", vendor.Id)
                    })));
    }

    [Fact]
    public async Task SaveAgreement_TierUpdate_ChangesMemberCounts()
    {
        using var db = LocalizationTestFixture.CreateDb();
        var seed = await LocalizationTestFixture.SeedProjectAsync(db);
        var vendor = await SeedVendorAsync(db);
        var jobs = LocalizationTestFixture.Jobs(db);

        await jobs.SaveAgreementAsync(seed.Project.Slug,
            new SaveAgreementRequest(ServiceTiers.Silver, null, null,
                new List<AgreementTeamRequest>
                {
                    new("de-DE", vendor.Id)
                }));

        var saved = await jobs.SaveAgreementAsync(seed.Project.Slug,
            new SaveAgreementRequest(ServiceTiers.Platinum, null, null,
                new List<AgreementTeamRequest>
                {
                    new("de-DE", vendor.Id)
                }));

        Assert.Equal(ServiceTiers.Platinum, saved.Tier);
        Assert.Equal(10, saved.MembersPerTeam);
        var team = Assert.Single(saved.Teams);
        Assert.Equal(10, team.MemberCount);

        var stored = await db.LocalizationTeamAssignments.AsNoTracking().ToListAsync();
        Assert.Single(stored);
        Assert.Equal(10, stored[0].MemberCount);
    }

    [Fact]
    public void AudienceSeparation_SerializesOnlyAllowedFields()
    {
        var options = new JsonSerializerOptions(JsonSerializerDefaults.Web);

        var jobJson = JsonSerializer.Serialize(new TranslationJobRowDto(
            1, 2, "de-DE", "Assigned", 10, 50, 0, "Vendor Team Larch", 3,
            DateTime.UtcNow, null, null), options);
        Assert.Contains("vendorTeamAlias", jobJson);
        Assert.DoesNotContain("realName", jobJson);
        Assert.DoesNotContain("RealName", jobJson);
        Assert.DoesNotContain("score", jobJson);

        var vendorJson = JsonSerializer.Serialize(new VendorStringRowDto(
            1, "k", "source", "de-DE", "target", "Translated", "Manual", DateTime.UtcNow,
            4, false, "raw", 3), options);
        Assert.Contains("\"score\"", vendorJson);
        Assert.DoesNotContain("project", vendorJson);
        Assert.DoesNotContain("Project", vendorJson);

        var agreementJson = JsonSerializer.Serialize(new ServiceAgreementDto(
            ServiceTiers.Gold, 6, DateTime.UtcNow, null,
            new List<AgreementTeamDto>
            {
                new("de-DE", "Vendor Team Larch", 6)
            }), options);
        Assert.Contains("vendorTeamAlias", agreementJson);
        Assert.DoesNotContain("realName", agreementJson);
        Assert.DoesNotContain("vendorTeamId", agreementJson);
        Assert.DoesNotContain("clientAlias", agreementJson);
    }
}
