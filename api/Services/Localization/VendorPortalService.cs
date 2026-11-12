using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public class VendorPortalService
{
    private readonly StudyTrackerContext _db;

    public VendorPortalService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<IReadOnlyList<VendorTeamDto>> GetVendorRosterAsync(CancellationToken ct = default)
    {
        var vendors = await _db.LocalizationVendors
            .AsNoTracking()
            .OrderBy(v => v.Id)
            .ToListAsync(ct);

        return vendors.Select(v => new VendorTeamDto(
            v.Id,
            v.Alias,
            v.Languages
        )).ToList();
    }

    public async Task<IReadOnlyList<VendorJobRowDto>> GetJobsForVendorAsync(
        int vendorId,
        CancellationToken ct = default)
    {
        var vendor = await _db.LocalizationVendors
            .AsNoTracking()
            .FirstOrDefaultAsync(v => v.Id == vendorId, ct);

        if (vendor == null)
        {
            throw new VendorNotFoundException(vendorId);
        }

        var jobs = await _db.LocalizationTranslationJobs
            .AsNoTracking()
            .Where(j => j.VendorId == vendorId)
            .OrderByDescending(j => j.CreatedAt)
            .ThenByDescending(j => j.Id)
            .ToListAsync(ct);

        var rows = new List<VendorJobRowDto>();
        foreach (var job in jobs)
        {
            rows.Add(await VendorJobRowAsync(job.Id, ct));
        }

        return rows;
    }

    public async Task<IReadOnlyList<VendorStringRowDto>> GetJobStringsAsync(
        int jobId,
        CancellationToken ct = default)
    {
        var job = await _db.LocalizationTranslationJobs
            .AsNoTracking()
            .FirstOrDefaultAsync(j => j.Id == jobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(jobId);
        }

        var strings = await _db.LocalizationStrings
            .AsNoTracking()
            .Where(s => s.ProjectId == job.ProjectId)
            .Include(s => s.Translations.Where(t => t.LocaleCode == job.LocaleCode))
            .OrderBy(s => s.Id)
            .ToListAsync(ct);

        var result = new List<VendorStringRowDto>();
        foreach (var str in strings)
        {
            var translation = str.Translations.FirstOrDefault();
            result.Add(VendorStringRow(str, job.LocaleCode, translation));
        }

        return result;
    }

    public async Task<VendorStringRowDto> UpdateJobStringAsync(
        int jobId,
        int stringId,
        string? targetText,
        CancellationToken ct = default)
    {
        var job = await _db.LocalizationTranslationJobs
            .FirstOrDefaultAsync(j => j.Id == jobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(jobId);
        }

        if (job.Status != "Assigned" && job.Status != "InProgress" && job.Status != "NeedsRevision")
        {
            throw new InvalidJobStateException($"Cannot edit strings on job {jobId} because it is in status '{job.Status}'.");
        }

        var str = await _db.LocalizationStrings
            .FirstOrDefaultAsync(s => s.Id == stringId && s.ProjectId == job.ProjectId, ct);

        if (str == null)
        {
            throw new LocalizationStringNotFoundException(stringId);
        }

        var translation = await _db.LocalizationTranslations
            .FirstOrDefaultAsync(t => t.StringId == stringId && t.LocaleCode == job.LocaleCode, ct);

        if (translation != null && translation.Stage == "Approved")
        {
            throw new InvalidJobStateException($"String {stringId} is already approved for {job.LocaleCode}.");
        }

        var hasTarget = !string.IsNullOrWhiteSpace(targetText);

        if (translation == null)
        {
            translation = new LocalizationTranslation
            {
                StringId = stringId,
                LocaleCode = job.LocaleCode,
                TargetText = targetText,
                Stage = hasTarget ? "Translated" : "New",
                TranslationSource = JobScope.VendorSource,
                NeedsReview = false,
                UpdatedAt = DateTime.UtcNow
            };
            _db.LocalizationTranslations.Add(translation);
        }
        else
        {
            translation.TargetText = targetText;
            translation.TranslationSource = JobScope.VendorSource;
            translation.Stage = hasTarget ? "Translated" : "New";
            translation.UpdatedAt = DateTime.UtcNow;
        }

        if (job.Status == "Assigned" || job.Status == "NeedsRevision")
        {
            job.Status = "InProgress";
        }

        await _db.SaveChangesAsync(ct);

        return VendorStringRow(str, job.LocaleCode, translation);
    }

    public async Task<VendorJobRowDto> SubmitJobForReviewAsync(
        int jobId,
        CancellationToken ct = default)
    {
        var job = await _db.LocalizationTranslationJobs
            .FirstOrDefaultAsync(j => j.Id == jobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(jobId);
        }

        if (job.Status != "Assigned" && job.Status != "InProgress" && job.Status != "NeedsRevision")
        {
            throw new InvalidJobStateException($"Cannot submit job {jobId} for review because it is in status '{job.Status}'.");
        }

        var strings = await _db.LocalizationStrings
            .Where(s => s.ProjectId == job.ProjectId)
            .Include(s => s.Translations.Where(t => t.LocaleCode == job.LocaleCode))
            .ToListAsync(ct);

        var untranslatedExists = strings.Any(s =>
            !s.Translations.Any(t => t.LocaleCode == job.LocaleCode && !string.IsNullOrWhiteSpace(t.TargetText)));

        if (untranslatedExists)
        {
            throw new InvalidJobStateException("All strings must have non-empty translations before submitting the job for review.");
        }

        var unreviewedMachineCount = strings.Count(s =>
        {
            var translation = s.Translations.FirstOrDefault(t => t.LocaleCode == job.LocaleCode);
            return translation != null
                && translation.TranslationSource == JobScope.MachineSource
                && JobScope.IsOpen(s, job.LocaleCode);
        });

        if (unreviewedMachineCount > 0)
        {
            throw new InvalidJobStateException($"{unreviewedMachineCount} machine-translated strings still need review before the job can be submitted.");
        }

        job.Status = "SubmittedForReview";
        job.SubmittedAt = DateTime.UtcNow;

        await _db.SaveChangesAsync(ct);
        return await VendorJobRowAsync(job.Id, ct);
    }

    private async Task<VendorJobRowDto> VendorJobRowAsync(int jobId, CancellationToken ct)
    {
        var job = await _db.LocalizationTranslationJobs
            .AsNoTracking()
            .FirstOrDefaultAsync(j => j.Id == jobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(jobId);
        }

        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Id == job.ProjectId, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(job.ProjectId.ToString());
        }

        var strings = await _db.LocalizationStrings
            .AsNoTracking()
            .Where(s => s.ProjectId == job.ProjectId)
            .Include(s => s.Translations.Where(t => t.LocaleCode == job.LocaleCode))
            .ToListAsync(ct);

        return new VendorJobRowDto(
            job.Id,
            project.ClientAlias,
            job.LocaleCode,
            job.Status,
            job.StringCount,
            job.WordCount,
            JobScope.CompletedPercent(strings, job.LocaleCode, job.StringCount, job.Status),
            job.CreatedAt,
            job.SubmittedAt,
            job.ApprovedAt);
    }

    private static VendorStringRowDto VendorStringRow(
        LocalizationString str,
        string localeCode,
        LocalizationTranslation? translation)
    {
        return new VendorStringRowDto(
            str.Id,
            str.Key,
            str.SourceText,
            localeCode,
            translation?.TargetText,
            translation?.Stage ?? "New",
            translation?.TranslationSource ?? "Manual",
            translation?.UpdatedAt,
            translation?.QpsScore,
            translation?.NeedsReview ?? false,
            translation?.RawMtText,
            translation?.RawMtQpsScore,
            JobScope.IsOpen(str, localeCode),
            JobScope.IsVendorReviewed(translation));
    }
}
