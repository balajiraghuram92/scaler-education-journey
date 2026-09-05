using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public class MarketplaceService
{
    private readonly StudyTrackerContext _db;
    private readonly CreditLedgerService _creditLedgerService;

    public MarketplaceService(StudyTrackerContext db, CreditLedgerService creditLedgerService)
    {
        _db = db;
        _creditLedgerService = creditLedgerService;
    }

    public async Task<IReadOnlyList<MarketplaceJobSummaryDto>> GetLocaleOverviewAsync(
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

        var jobs = await _db.LocalizationMarketplaceJobs
            .AsNoTracking()
            .Where(j => j.ProjectId == project.Id)
            .Include(j => j.AwardedVendor)
            .Include(j => j.Bids)
            .ToListAsync(ct);

        var overview = new List<MarketplaceJobSummaryDto>();

        foreach (var locale in project.Locales.OrderBy(l => l.Id))
        {
            var job = jobs.Where(j => j.LocaleCode == locale.LocaleCode)
                .OrderByDescending(j => j.Id)
                .FirstOrDefault();

            var untranslatedCount = project.Strings.Count(s =>
                !s.Translations.Any(t => t.LocaleCode == locale.LocaleCode && !string.IsNullOrWhiteSpace(t.TargetText)));

            var wordCount = project.Strings
                .Where(s => !s.Translations.Any(t => t.LocaleCode == locale.LocaleCode && !string.IsNullOrWhiteSpace(t.TargetText)))
                .Sum(s => s.SourceText.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length);

            if (job == null)
            {
                var (estLow, estHigh) = await _creditLedgerService.EstimatePriceBandAsync(wordCount, ct);
                overview.Add(new MarketplaceJobSummaryDto(
                    null,
                    project.Id,
                    locale.LocaleCode,
                    "Not Posted",
                    untranslatedCount,
                    wordCount,
                    estLow,
                    estHigh,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    0
                ));
            }
            else
            {
                overview.Add(new MarketplaceJobSummaryDto(
                    job.Id,
                    project.Id,
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
                ));
            }
        }

        return overview;
    }

    public async Task<MarketplaceJobDto> PostToMarketplaceAsync(
        string projectSlug,
        string localeCode,
        CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .Include(p => p.Strings)
                .ThenInclude(s => s.Translations)
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var untranslatedStrings = project.Strings
            .Where(s => !s.Translations.Any(t => t.LocaleCode == localeCode && !string.IsNullOrWhiteSpace(t.TargetText)))
            .ToList();

        var stringCount = untranslatedStrings.Count > 0 ? untranslatedStrings.Count : project.Strings.Count;
        var wordCount = untranslatedStrings.Count > 0
            ? untranslatedStrings.Sum(s => s.SourceText.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length)
            : project.Strings.Sum(s => s.SourceText.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length);

        if (wordCount == 0) wordCount = 1240; // Default fallback word count for demo consistency

        var (low, high) = await _creditLedgerService.EstimatePriceBandAsync(wordCount, ct);

        var existingJob = await _db.LocalizationMarketplaceJobs
            .FirstOrDefaultAsync(j => j.ProjectId == project.Id && j.LocaleCode == localeCode, ct);

        var now = DateTime.UtcNow;

        if (existingJob == null)
        {
            existingJob = new MarketplaceJob
            {
                ProjectId = project.Id,
                LocaleCode = localeCode,
                Status = "Open",
                StringCount = stringCount,
                WordCount = wordCount,
                SuggestedPriceLow = low,
                SuggestedPriceHigh = high,
                PostedAt = now
            };
            _db.LocalizationMarketplaceJobs.Add(existingJob);
        }
        else
        {
            existingJob.Status = "Open";
            existingJob.StringCount = stringCount;
            existingJob.WordCount = wordCount;
            existingJob.SuggestedPriceLow = low;
            existingJob.SuggestedPriceHigh = high;
            existingJob.PostedAt = now;
        }

        await _db.SaveChangesAsync(ct);

        return await GetJobDtoAsync(existingJob.Id, ct);
    }

    public async Task<IReadOnlyList<MarketplaceBidDto>> GetBidsAsync(int marketplaceJobId, CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .AsNoTracking()
            .FirstOrDefaultAsync(j => j.Id == marketplaceJobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(marketplaceJobId);
        }

        var bids = await _db.LocalizationMarketplaceBids
            .AsNoTracking()
            .Where(b => b.MarketplaceJobId == marketplaceJobId)
            .Include(b => b.Vendor)
            .OrderByDescending(b => b.SubmittedAt)
            .ToListAsync(ct);

        return bids.Select(b => new MarketplaceBidDto(
            b.Id,
            b.MarketplaceJobId,
            b.VendorId,
            b.Vendor?.Name ?? "Unknown Vendor",
            b.Vendor?.Languages ?? "",
            b.Vendor?.Rating ?? 5.0m,
            b.ProposedPrice,
            b.Note,
            b.Status,
            b.SubmittedAt
        )).ToList();
    }

    public async Task<MarketplaceJobDto> AwardBidAsync(int marketplaceJobId, int bidId, CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .Include(j => j.Bids)
            .FirstOrDefaultAsync(j => j.Id == marketplaceJobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(marketplaceJobId);
        }

        var selectedBid = job.Bids.FirstOrDefault(b => b.Id == bidId);
        if (selectedBid == null)
        {
            throw new MarketplaceBidNotFoundException(bidId);
        }

        var now = DateTime.UtcNow;

        selectedBid.Status = "Awarded";
        foreach (var sibling in job.Bids.Where(b => b.Id != bidId))
        {
            sibling.Status = "Declined";
        }

        job.Status = "Awarded";
        job.AwardedVendorId = selectedBid.VendorId;
        job.AwardedAt = now;

        await _db.SaveChangesAsync(ct);
        return await GetJobDtoAsync(job.Id, ct);
    }

    public async Task<MarketplaceJobDto> ApproveSubmissionAsync(int marketplaceJobId, CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .Include(j => j.Project)
            .Include(j => j.Bids)
            .FirstOrDefaultAsync(j => j.Id == marketplaceJobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(marketplaceJobId);
        }

        var now = DateTime.UtcNow;
        job.Status = "Approved";
        job.ApprovedAt = now;

        // Record credit ledger spend
        var awardedBid = job.Bids.FirstOrDefault(b => b.Status == "Awarded");
        var price = awardedBid?.ProposedPrice ?? job.SuggestedPriceLow;

        var ledgerEntry = new LedgerEntry
        {
            ProjectId = job.ProjectId,
            Source = "Marketplace",
            Amount = price,
            RelatedMarketplaceJobId = job.Id,
            CreatedAt = now
        };
        _db.LocalizationLedgerEntries.Add(ledgerEntry);

        // Advance all translations in project + locale to "Approved"
        var translations = await _db.LocalizationTranslations
            .Include(t => t.String)
            .Where(t => t.String != null && t.String.ProjectId == job.ProjectId && t.LocaleCode == job.LocaleCode)
            .ToListAsync(ct);

        foreach (var trans in translations)
        {
            trans.Stage = "Approved";
            trans.UpdatedAt = now;
        }

        await _db.SaveChangesAsync(ct);
        return await GetJobDtoAsync(job.Id, ct);
    }

    public async Task<MarketplaceJobDto> SendBackForRevisionAsync(int marketplaceJobId, CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .FirstOrDefaultAsync(j => j.Id == marketplaceJobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(marketplaceJobId);
        }

        job.Status = "NeedsRevision";
        await _db.SaveChangesAsync(ct);
        return await GetJobDtoAsync(job.Id, ct);
    }

    public async Task<MarketplaceJobDto> GetJobDtoAsync(int jobId, CancellationToken ct = default)
    {
        var job = await _db.LocalizationMarketplaceJobs
            .AsNoTracking()
            .Include(j => j.AwardedVendor)
            .Include(j => j.Bids)
                .ThenInclude(b => b.Vendor)
            .FirstOrDefaultAsync(j => j.Id == jobId, ct);

        if (job == null)
        {
            throw new MarketplaceJobNotFoundException(jobId);
        }

        var bids = job.Bids.Select(b => new MarketplaceBidDto(
            b.Id,
            b.MarketplaceJobId,
            b.VendorId,
            b.Vendor?.Name ?? "Unknown Vendor",
            b.Vendor?.Languages ?? "",
            b.Vendor?.Rating ?? 5.0m,
            b.ProposedPrice,
            b.Note,
            b.Status,
            b.SubmittedAt
        )).ToList();

        return new MarketplaceJobDto(
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
            bids
        );
    }
}
