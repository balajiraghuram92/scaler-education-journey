using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public class ProviderHealthService
{
    private readonly StudyTrackerContext _db;

    public ProviderHealthService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<IReadOnlyList<ProviderHealthSnapshotDto>> GetHealthAsync(CancellationToken ct = default)
    {
        var list = await _db.LocalizationProviderHealth
            .AsNoTracking()
            .OrderBy(p => p.Id)
            .ToListAsync(ct);

        return list.Select(p => new ProviderHealthSnapshotDto(
            p.Id,
            p.Provider,
            p.P50LatencyMs,
            p.P99LatencyMs,
            p.ErrorRatePercent,
            p.CircuitState,
            p.UpdatedAt
        )).ToList();
    }

    public async Task<ProviderHealthSnapshotDto> SimulateOutageAsync(string provider, CancellationToken ct = default)
    {
        var record = await _db.LocalizationProviderHealth
            .FirstOrDefaultAsync(p => p.Provider.ToLower() == provider.ToLower(), ct);

        if (record == null)
        {
            throw new ProviderNotFoundException(provider);
        }

        record.CircuitState = "Open";
        record.ErrorRatePercent = 87.5m;
        record.UpdatedAt = DateTime.UtcNow;

        await _db.SaveChangesAsync(ct);

        return new ProviderHealthSnapshotDto(
            record.Id,
            record.Provider,
            record.P50LatencyMs,
            record.P99LatencyMs,
            record.ErrorRatePercent,
            record.CircuitState,
            record.UpdatedAt
        );
    }

    public async Task<ProviderHealthSnapshotDto> ResolveOutageAsync(string provider, CancellationToken ct = default)
    {
        var record = await _db.LocalizationProviderHealth
            .FirstOrDefaultAsync(p => p.Provider.ToLower() == provider.ToLower(), ct);

        if (record == null)
        {
            throw new ProviderNotFoundException(provider);
        }

        record.CircuitState = "Closed";
        record.ErrorRatePercent = record.Provider.Equals("AzureTranslator", StringComparison.OrdinalIgnoreCase) ? 0.4m : 1.1m;
        record.UpdatedAt = DateTime.UtcNow;

        await _db.SaveChangesAsync(ct);

        return new ProviderHealthSnapshotDto(
            record.Id,
            record.Provider,
            record.P50LatencyMs,
            record.P99LatencyMs,
            record.ErrorRatePercent,
            record.CircuitState,
            record.UpdatedAt
        );
    }
}
