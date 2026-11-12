using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public class TranslationJobService
{
    private readonly StudyTrackerContext _db;

    public TranslationJobService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<IReadOnlyList<TranslationJobRowDto>> GetJobsForProjectAsync(
        string projectSlug,
        CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .Include(p => p.Locales)
            .Include(p => p.Strings)
                .ThenInclude(s => s.Translations)
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var jobs = await _db.LocalizationTranslationJobs
            .AsNoTracking()
            .Where(j => j.ProjectId == project.Id)
            .Include(j => j.Vendor)
            .ToListAsync(ct);

        var teams = await AssignedTeamsAsync(project.Id, ct);

        var rows = new List<TranslationJobRowDto>();
        foreach (var locale in project.Locales.OrderBy(l => l.Id))
        {
            var job = jobs.Where(j => j.LocaleCode == locale.LocaleCode)
                .OrderByDescending(j => j.Id)
                .FirstOrDefault();

            teams.TryGetValue(locale.LocaleCode, out var team);

            if (job == null)
            {
                var open = project.Strings
                    .Where(s => JobScope.IsOpen(s, locale.LocaleCode))
                    .ToList();
                rows.Add(new TranslationJobRowDto(
                    null,
                    project.Id,
                    locale.LocaleCode,
                    "NotCreated",
                    open.Count,
                    CountWords(open),
                    0,
                    team?.Alias,
                    team?.MemberCount,
                    null,
                    null,
                    null));
            }
            else
            {
                rows.Add(new TranslationJobRowDto(
                    job.Id,
                    project.Id,
                    job.LocaleCode,
                    job.Status,
                    job.StringCount,
                    job.WordCount,
                    JobScope.CompletedPercent(project.Strings, job.LocaleCode, job.StringCount, job.Status),
                    job.Vendor?.Alias,
                    team?.MemberCount,
                    job.CreatedAt,
                    job.SubmittedAt,
                    job.ApprovedAt));
            }
        }

        return rows;
    }

    public async Task<TranslationJobRowDto> CreateJobAsync(
        string projectSlug,
        string localeCode,
        CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .Include(p => p.Locales)
            .Include(p => p.Strings)
                .ThenInclude(s => s.Translations)
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        if (!project.Locales.Any(l => l.LocaleCode == localeCode))
        {
            throw new LocalizationLocaleNotFoundException(localeCode);
        }

        var teams = await AssignedTeamsAsync(project.Id, ct);
        if (!teams.TryGetValue(localeCode, out var team))
        {
            throw new InvalidJobStateException($"NO_TEAM_FOR_LOCALE: the agreement assigns no team to locale '{localeCode}'.");
        }

        var mostRecentJob = await _db.LocalizationTranslationJobs
            .Where(j => j.ProjectId == project.Id && j.LocaleCode == localeCode)
            .OrderByDescending(j => j.Id)
            .FirstOrDefaultAsync(ct);

        if (mostRecentJob != null && mostRecentJob.Status != "Approved" && mostRecentJob.Status != "Closed")
        {
            throw new InvalidJobStateException($"Cannot create a new job for locale '{localeCode}' while job {mostRecentJob.Id} is in status '{mostRecentJob.Status}'.");
        }

        var openStrings = project.Strings
            .Where(s => JobScope.IsOpen(s, localeCode))
            .ToList();

        if (openStrings.Count == 0)
        {
            throw new InvalidJobStateException($"There is nothing left to translate for locale '{localeCode}'.");
        }

        var job = new TranslationJob
        {
            ProjectId = project.Id,
            LocaleCode = localeCode,
            Status = "Assigned",
            StringCount = openStrings.Count,
            WordCount = CountWords(openStrings),
            VendorId = team.VendorId,
            CreatedAt = DateTime.UtcNow
        };
        _db.LocalizationTranslationJobs.Add(job);

        await _db.SaveChangesAsync(ct);

        return await JobRowAsync(job.Id, ct);
    }

    public async Task<TranslationJobRowDto> ApproveAsync(int jobId, CancellationToken ct = default)
    {
        var job = await _db.LocalizationTranslationJobs
            .Include(j => j.Project)
            .FirstOrDefaultAsync(j => j.Id == jobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(jobId);
        }

        if (job.Status != "SubmittedForReview")
        {
            throw new InvalidJobStateException($"Cannot approve job {jobId} because it is in status '{job.Status}'. Expected 'SubmittedForReview'.");
        }

        var now = DateTime.UtcNow;
        job.Status = "Approved";
        job.ApprovedAt = now;

        var translations = await _db.LocalizationTranslations
            .Include(t => t.String)
            .Where(t => t.String != null && t.String.ProjectId == job.ProjectId && t.LocaleCode == job.LocaleCode)
            .ToListAsync(ct);

        foreach (var trans in translations.Where(t => !string.IsNullOrWhiteSpace(t.TargetText)))
        {
            trans.Stage = "Approved";
            trans.UpdatedAt = now;
        }

        await _db.SaveChangesAsync(ct);
        return await JobRowAsync(job.Id, ct);
    }

    public async Task<TranslationJobRowDto> SendBackAsync(int jobId, CancellationToken ct = default)
    {
        var job = await _db.LocalizationTranslationJobs
            .FirstOrDefaultAsync(j => j.Id == jobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(jobId);
        }

        if (job.Status != "SubmittedForReview")
        {
            throw new InvalidJobStateException($"Cannot send back job {jobId} because it is in status '{job.Status}'. Expected 'SubmittedForReview'.");
        }

        job.Status = "NeedsRevision";
        await _db.SaveChangesAsync(ct);
        return await JobRowAsync(job.Id, ct);
    }

    public async Task<object?> GetAgreementAsync(string projectSlug, bool forOperations, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var agreement = await _db.LocalizationServiceAgreements
            .AsNoTracking()
            .FirstOrDefaultAsync(a => a.ProjectId == project.Id, ct);

        if (agreement == null)
        {
            return null;
        }

        var teams = await _db.LocalizationTeamAssignments
            .AsNoTracking()
            .Where(t => t.AgreementId == agreement.Id)
            .Include(t => t.Vendor)
            .OrderBy(t => t.LocaleCode)
            .ToListAsync(ct);

        if (forOperations)
        {
            return new OpsServiceAgreementDto(
                agreement.Tier,
                ServiceTiers.MembersFor(agreement.Tier),
                agreement.ValidFrom,
                agreement.ValidTo,
                project.ClientAlias,
                teams.Select(t => new OpsAgreementTeamDto(
                    t.LocaleCode, t.Vendor!.Alias, t.MemberCount, t.VendorId, t.Vendor!.Name)).ToList());
        }

        return new ServiceAgreementDto(
            agreement.Tier,
            ServiceTiers.MembersFor(agreement.Tier),
            agreement.ValidFrom,
            agreement.ValidTo,
            teams.Select(t => new AgreementTeamDto(t.LocaleCode, t.Vendor!.Alias, t.MemberCount)).ToList());
    }

    public async Task<OpsServiceAgreementDto> SaveAgreementAsync(
        string projectSlug,
        SaveAgreementRequest request,
        CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var tiers = new[] { ServiceTiers.Silver, ServiceTiers.Gold, ServiceTiers.Platinum };
        if (string.IsNullOrWhiteSpace(request.Tier) || !tiers.Contains(request.Tier))
        {
            throw new ArgumentException($"Unknown service tier '{request.Tier}'.", nameof(request));
        }

        var teams = request.Teams ?? Array.Empty<AgreementTeamRequest>();
        var localeCodes = await _db.LocalizationLocales
            .AsNoTracking()
            .Where(l => l.ProjectId == project.Id)
            .Select(l => l.LocaleCode)
            .ToListAsync(ct);
        var vendors = await _db.LocalizationVendors
            .AsNoTracking()
            .ToDictionaryAsync(v => v.Id, ct);

        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var team in teams)
        {
            if (string.IsNullOrWhiteSpace(team.LocaleCode) || !localeCodes.Contains(team.LocaleCode))
            {
                throw new ArgumentException($"Locale '{team.LocaleCode}' is not a locale of project '{projectSlug}'.", nameof(request));
            }

            if (!seen.Add(team.LocaleCode))
            {
                throw new ArgumentException($"Locale '{team.LocaleCode}' is listed twice.", nameof(request));
            }

            if (team.VendorTeamId is null || !vendors.ContainsKey(team.VendorTeamId.Value))
            {
                throw new ArgumentException($"Unknown vendor team '{team.VendorTeamId}'.", nameof(request));
            }
        }

        var agreement = await _db.LocalizationServiceAgreements
            .FirstOrDefaultAsync(a => a.ProjectId == project.Id, ct);

        if (agreement is null)
        {
            agreement = new ServiceAgreement
            {
                ProjectId = project.Id,
                Tier = request.Tier,
                ValidFrom = request.ValidFrom ?? DateTime.UtcNow,
                ValidTo = request.ValidTo,
                CreatedAt = DateTime.UtcNow
            };
            _db.LocalizationServiceAgreements.Add(agreement);
        }
        else
        {
            agreement.Tier = request.Tier;
            if (request.ValidFrom is not null)
            {
                agreement.ValidFrom = request.ValidFrom.Value;
            }

            agreement.ValidTo = request.ValidTo;

            var stale = await _db.LocalizationTeamAssignments
                .Where(t => t.AgreementId == agreement.Id)
                .ToListAsync(ct);
            _db.LocalizationTeamAssignments.RemoveRange(stale);
        }

        var memberCount = ServiceTiers.MembersFor(request.Tier);
        foreach (var team in teams)
        {
            _db.LocalizationTeamAssignments.Add(new TeamAssignment
            {
                Agreement = agreement,
                VendorId = team.VendorTeamId!.Value,
                LocaleCode = team.LocaleCode!,
                MemberCount = memberCount
            });
        }

        await _db.SaveChangesAsync(ct);

        return new OpsServiceAgreementDto(
            agreement.Tier,
            memberCount,
            agreement.ValidFrom,
            agreement.ValidTo,
            project.ClientAlias,
            teams.Select(t => new OpsAgreementTeamDto(
                t.LocaleCode!,
                vendors[t.VendorTeamId!.Value].Alias,
                memberCount,
                t.VendorTeamId!.Value,
                vendors[t.VendorTeamId!.Value].Name)).ToList());
    }

    private async Task<TranslationJobRowDto> JobRowAsync(int jobId, CancellationToken ct)
    {
        var job = await _db.LocalizationTranslationJobs
            .AsNoTracking()
            .Include(j => j.Vendor)
            .FirstOrDefaultAsync(j => j.Id == jobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(jobId);
        }

        var strings = await _db.LocalizationStrings
            .AsNoTracking()
            .Where(s => s.ProjectId == job.ProjectId)
            .Include(s => s.Translations.Where(t => t.LocaleCode == job.LocaleCode))
            .ToListAsync(ct);

        var teams = await AssignedTeamsAsync(job.ProjectId, ct);
        teams.TryGetValue(job.LocaleCode, out var team);

        return new TranslationJobRowDto(
            job.Id,
            job.ProjectId,
            job.LocaleCode,
            job.Status,
            job.StringCount,
            job.WordCount,
            JobScope.CompletedPercent(strings, job.LocaleCode, job.StringCount, job.Status),
            job.Vendor?.Alias,
            team?.MemberCount,
            job.CreatedAt,
            job.SubmittedAt,
            job.ApprovedAt);
    }

    private sealed record AssignedTeam(int VendorId, string Alias, int MemberCount);

    private async Task<Dictionary<string, AssignedTeam>> AssignedTeamsAsync(int projectId, CancellationToken ct)
    {
        var agreement = await _db.LocalizationServiceAgreements
            .AsNoTracking()
            .FirstOrDefaultAsync(a => a.ProjectId == projectId, ct);

        if (agreement == null)
        {
            return new Dictionary<string, AssignedTeam>();
        }

        return (await _db.LocalizationTeamAssignments
            .AsNoTracking()
            .Where(t => t.AgreementId == agreement.Id)
            .Include(t => t.Vendor)
            .ToListAsync(ct))
            .ToDictionary(
                t => t.LocaleCode,
                t => new AssignedTeam(t.VendorId, t.Vendor!.Alias, t.MemberCount));
    }

    private static int CountWords(IEnumerable<LocalizationString> strings)
    {
        return strings.Sum(s => s.SourceText.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length);
    }
}
