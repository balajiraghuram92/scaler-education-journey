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
    private readonly MarketplaceService _marketplaceService;

    public VendorPortalService(StudyTrackerContext db, MarketplaceService marketplaceService)
    {
        _db = db;
        _marketplaceService = marketplaceService;
    }

    public async Task<IReadOnlyList<VendorDto>> GetVendorRosterAsync(CancellationToken ct = default)
    {
        var vendors = await _db.LocalizationVendors
            .AsNoTracking()
            .OrderBy(v => v.Id)
            .ToListAsync(ct);

        return vendors.Select(v => new VendorDto(
            v.Id,
            v.Name,
            v.Languages,
            v.Rating
        )).ToList();
    }

    public async Task<IReadOnlyList<MarketplaceJobSummaryDto>> GetOpenJobsForVendorAsync(
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

        var vendorLanguages = vendor.Languages
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .ToHashSet(StringComparer.OrdinalIgnoreCase);

        var openJobs = await _db.LocalizationMarketplaceJobs
            .AsNoTracking()
            .Where(j => j.Status == "Open")
            .Include(j => j.AwardedVendor)
            .Include(j => j.Bids)
            .OrderByDescending(j => j.PostedAt)
            .ToListAsync(ct);

        var matchingJobs = openJobs
            .Where(j => vendorLanguages.Contains(j.LocaleCode))
            .Select(job => new MarketplaceJobSummaryDto(
                job.Id,
                job.ProjectId,
                job.LocaleCode,
                job.Status,
                job.StringCount,
                job.WordCount,
                job.SuggestedPriceLow,
                job.SuggestedPriceHigh,
                job.AwardedVendorId,
                job.AwardedVendor?.Name,
                job.PostedAt,
                job.AwardedAt,
                job.SubmittedAt,
                job.ApprovedAt,
                job.Bids.Count
            ))
            .ToList();

        return matchingJobs;
    }

    public async Task<MarketplaceBidDto> SubmitBidAsync(
        int marketplaceJobId,
        int vendorId,
        decimal proposedPrice,
        string note,
        CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .FirstOrDefaultAsync(j => j.Id == marketplaceJobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(marketplaceJobId);
        }

        var vendor = await _db.LocalizationVendors
            .FirstOrDefaultAsync(v => v.Id == vendorId, ct);

        if (vendor == null)
        {
            throw new VendorNotFoundException(vendorId);
        }

        if (job.Status != "Open")
        {
            throw new InvalidJobStateException($"Cannot bid on job {marketplaceJobId} because it is in status '{job.Status}'. Expected 'Open'.");
        }

        var vendorLanguages = vendor.Languages
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .ToHashSet(StringComparer.OrdinalIgnoreCase);

        if (!vendorLanguages.Contains(job.LocaleCode))
        {
            throw new VendorLanguageMismatchException(vendorId, job.LocaleCode);
        }

        var hasPendingBid = await _db.LocalizationMarketplaceBids
            .AnyAsync(b => b.MarketplaceJobId == marketplaceJobId && b.VendorId == vendorId && b.Status == "Pending", ct);

        if (hasPendingBid)
        {
            throw new InvalidJobStateException($"Vendor {vendorId} already has a pending bid on job {marketplaceJobId}.");
        }

        if (proposedPrice <= 0)
        {
            throw new ArgumentException("Proposed price must be greater than zero.", nameof(proposedPrice));
        }

        var bid = new MarketplaceBid
        {
            MarketplaceJobId = marketplaceJobId,
            VendorId = vendorId,
            ProposedPrice = proposedPrice,
            Note = note ?? string.Empty,
            Status = "Pending",
            SubmittedAt = DateTime.UtcNow
        };

        _db.LocalizationMarketplaceBids.Add(bid);
        await _db.SaveChangesAsync(ct);

        return new MarketplaceBidDto(
            bid.Id,
            bid.MarketplaceJobId,
            bid.VendorId,
            vendor.Name,
            vendor.Languages,
            vendor.Rating,
            bid.ProposedPrice,
            bid.Note,
            bid.Status,
            bid.SubmittedAt
        );
    }

    public async Task<IReadOnlyList<MarketplaceJobSummaryDto>> GetAwardedJobsForVendorAsync(
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

        var jobs = await _db.LocalizationMarketplaceJobs
            .AsNoTracking()
            .Where(j => j.AwardedVendorId == vendorId && (j.Status == "Awarded" || j.Status == "InProgress" || j.Status == "NeedsRevision" || j.Status == "SubmittedForReview" || j.Status == "Approved"))
            .Include(j => j.AwardedVendor)
            .Include(j => j.Bids)
            .OrderByDescending(j => j.AwardedAt ?? j.PostedAt)
            .ToListAsync(ct);

        return jobs.Select(job => new MarketplaceJobSummaryDto(
            job.Id,
            job.ProjectId,
            job.LocaleCode,
            job.Status,
            job.StringCount,
            job.WordCount,
            job.SuggestedPriceLow,
            job.SuggestedPriceHigh,
            job.AwardedVendorId,
            job.AwardedVendor?.Name,
            job.PostedAt,
            job.AwardedAt,
            job.SubmittedAt,
            job.ApprovedAt,
            job.Bids.Count
        )).ToList();
    }

    public async Task<IReadOnlyList<LocalizationStringRowDto>> GetJobStringsAsync(
        int marketplaceJobId,
        CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .AsNoTracking()
            .FirstOrDefaultAsync(j => j.Id == marketplaceJobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(marketplaceJobId);
        }

        var strings = await _db.LocalizationStrings
            .AsNoTracking()
            .Where(s => s.ProjectId == job.ProjectId)
            .Include(s => s.Translations.Where(t => t.LocaleCode == job.LocaleCode))
            .OrderBy(s => s.Id)
            .ToListAsync(ct);

        var result = new List<LocalizationStringRowDto>();
        foreach (var str in strings)
        {
            var translation = str.Translations.FirstOrDefault();
            result.Add(new LocalizationStringRowDto(
                str.Id,
                str.Key,
                str.SourceText,
                job.LocaleCode,
                translation?.TargetText,
                translation?.Stage ?? "New",
                translation?.TranslationSource ?? "Marketplace",
                translation?.QpsScore,
                translation?.NeedsReview ?? false,
                translation?.UpdatedAt
            ));
        }

        return result;
    }

    public async Task<LocalizationStringRowDto> UpdateJobStringAsync(
        int marketplaceJobId,
        int stringId,
        string? targetText,
        CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .FirstOrDefaultAsync(j => j.Id == marketplaceJobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(marketplaceJobId);
        }

        if (job.Status != "Awarded" && job.Status != "InProgress" && job.Status != "NeedsRevision")
        {
            throw new InvalidJobStateException($"Cannot edit strings on job {marketplaceJobId} because it is in status '{job.Status}'.");
        }

        var str = await _db.LocalizationStrings
            .FirstOrDefaultAsync(s => s.Id == stringId && s.ProjectId == job.ProjectId, ct);

        if (str == null)
        {
            throw new LocalizationStringNotFoundException(stringId);
        }

        var translation = await _db.LocalizationTranslations
            .FirstOrDefaultAsync(t => t.StringId == stringId && t.LocaleCode == job.LocaleCode, ct);

        var hasTarget = !string.IsNullOrWhiteSpace(targetText);

        if (translation == null)
        {
            translation = new LocalizationTranslation
            {
                StringId = stringId,
                LocaleCode = job.LocaleCode,
                TargetText = targetText,
                Stage = hasTarget ? "Translated" : "New",
                TranslationSource = "Marketplace",
                NeedsReview = false,
                UpdatedAt = DateTime.UtcNow
            };
            _db.LocalizationTranslations.Add(translation);
        }
        else
        {
            translation.TargetText = targetText;
            translation.TranslationSource = "Marketplace";
            translation.Stage = hasTarget ? "Translated" : "New";
            translation.UpdatedAt = DateTime.UtcNow;
        }

        if (job.Status == "Awarded" || job.Status == "NeedsRevision")
        {
            job.Status = "InProgress";
        }

        await _db.SaveChangesAsync(ct);

        return new LocalizationStringRowDto(
            str.Id,
            str.Key,
            str.SourceText,
            job.LocaleCode,
            translation.TargetText,
            translation.Stage,
            translation.TranslationSource,
            translation.QpsScore,
            translation.NeedsReview,
            translation.UpdatedAt
        );
    }

    public async Task<MarketplaceJobDto> SubmitJobForReviewAsync(
        int marketplaceJobId,
        CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .FirstOrDefaultAsync(j => j.Id == marketplaceJobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(marketplaceJobId);
        }

        if (job.Status != "Awarded" && job.Status != "InProgress" && job.Status != "NeedsRevision")
        {
            throw new InvalidJobStateException($"Cannot submit job {marketplaceJobId} for review because it is in status '{job.Status}'.");
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

        job.Status = "SubmittedForReview";
        job.SubmittedAt = DateTime.UtcNow;

        await _db.SaveChangesAsync(ct);
        return await _marketplaceService.GetJobDtoAsync(job.Id, ct);
    }
}
