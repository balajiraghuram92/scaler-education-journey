using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public class CreditLedgerService
{
    private readonly StudyTrackerContext _db;

    public CreditLedgerService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<decimal> GetProjectBalanceAsync(string projectSlug, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        return await _db.LocalizationLedgerEntries
            .AsNoTracking()
            .Where(e => e.ProjectId == project.Id)
            .SumAsync(e => e.Amount, ct);
    }

    public async Task<LedgerEntry> RecordEntryAsync(
        string projectSlug,
        string source,
        decimal amount,
        int? relatedMarketplaceJobId,
        CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var entry = new LedgerEntry
        {
            ProjectId = project.Id,
            Source = source,
            Amount = amount,
            RelatedMarketplaceJobId = relatedMarketplaceJobId,
            CreatedAt = DateTime.UtcNow
        };

        _db.LocalizationLedgerEntries.Add(entry);
        await _db.SaveChangesAsync(ct);
        return entry;
    }

    public Task<(decimal Low, decimal High)> EstimatePriceBandAsync(int wordCount, CancellationToken ct = default)
    {
        // Formula: Low = wordCount * 0.145m rounded to nearest 5, High = wordCount * 0.19m rounded to nearest 5
        decimal rawLow = wordCount * 0.145m;
        decimal rawHigh = wordCount * 0.19m;

        decimal low = Math.Round(rawLow / 5m, MidpointRounding.AwayFromZero) * 5m;
        decimal high = Math.Round(rawHigh / 5m, MidpointRounding.AwayFromZero) * 5m;

        if (low < 5m && wordCount > 0) low = 5m;
        if (high < low) high = low;

        return Task.FromResult((low, high));
    }
}
