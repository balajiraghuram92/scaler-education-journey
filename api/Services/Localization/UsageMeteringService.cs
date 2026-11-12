using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public sealed record UsageCallRecord(
    int ProjectId, int? WorkflowStepId, string Meter, string Operation, string? LocaleCode,
    int Units, int? UnitsOut, bool CacheHit, bool Succeeded);

/// <summary>
/// Records one immutable usage event per paid provider call and serves the
/// operations-only usage summaries. Costs use the rate in force when the
/// call happened; a call with no rate costs 0 and shows up in ratesMissing.
/// </summary>
public class UsageMeteringService
{
    private readonly StudyTrackerContext _db;
    private List<LocalizationProviderRate>? _rates;

    public UsageMeteringService(StudyTrackerContext db)
    {
        _db = db;
    }

    /// <summary>
    /// Computes the cost and adds the event. Does not save; the caller saves.
    /// </summary>
    public async Task RecordAsync(UsageCallRecord call, DateTime occurredAtUtc, CancellationToken ct)
    {
        var rates = await LoadRatesAsync(ct);
        _db.LocalizationUsageEvents.Add(new LocalizationUsageEvent
        {
            ProjectId = call.ProjectId,
            WorkflowStepId = call.WorkflowStepId,
            Meter = call.Meter,
            Operation = call.Operation,
            LocaleCode = call.LocaleCode,
            Units = call.Units,
            UnitsOut = call.UnitsOut,
            CacheHit = call.CacheHit,
            Succeeded = call.Succeeded,
            CostUsd = decimal.Round(CostFor(rates, call, occurredAtUtc), 6),
            OccurredAt = occurredAtUtc
        });
    }

    public async Task<UsageSummaryDto> GetSummaryAsync(string? projectSlug, int year, int month, CancellationToken ct)
    {
        var projectId = await ResolveProjectIdAsync(projectSlug, ct);
        var start = new DateTime(year, month, 1, 0, 0, 0, DateTimeKind.Utc);
        var end = start.AddMonths(1);

        var events = _db.LocalizationUsageEvents
            .AsNoTracking()
            .Where(e => e.OccurredAt >= start && e.OccurredAt < end);
        if (projectId is not null)
        {
            events = events.Where(e => e.ProjectId == projectId.Value);
        }

        // Project to anonymous types before ordering so the queries translate to SQL.
        var byMeter = await events
            .GroupBy(e => e.Meter)
            .Select(g => new
            {
                Meter = g.Key,
                Calls = g.Count(),
                FailedCalls = g.Count(e => !e.Succeeded),
                CacheHits = g.Count(e => e.CacheHit),
                Units = g.Sum(e => e.Units),
                UnitsOut = g.Sum(e => e.UnitsOut),
                CostUsd = g.Sum(e => e.CostUsd)
            })
            .OrderBy(r => r.Meter)
            .ToListAsync(ct);

        var byOperation = await events
            .GroupBy(e => new { e.Meter, e.Operation })
            .Select(g => new
            {
                g.Key.Meter,
                g.Key.Operation,
                Calls = g.Count(),
                FailedCalls = g.Count(e => !e.Succeeded),
                CacheHits = g.Count(e => e.CacheHit),
                Units = g.Sum(e => e.Units),
                UnitsOut = g.Sum(e => e.UnitsOut),
                CostUsd = g.Sum(e => e.CostUsd)
            })
            .OrderBy(r => r.Meter)
            .ThenBy(r => r.Operation)
            .ToListAsync(ct);

        var byLocale = await events
            .GroupBy(e => new { e.Meter, e.LocaleCode })
            .Select(g => new
            {
                g.Key.Meter,
                g.Key.LocaleCode,
                Calls = g.Count(),
                Units = g.Sum(e => e.Units),
                UnitsOut = g.Sum(e => e.UnitsOut),
                CostUsd = g.Sum(e => e.CostUsd)
            })
            .OrderBy(r => r.Meter)
            .ThenBy(r => r.LocaleCode)
            .ToListAsync(ct);

        var byDay = await events
            .GroupBy(e => new { Date = e.OccurredAt.Date, e.Meter })
            .Select(g => new
            {
                g.Key.Date,
                g.Key.Meter,
                Units = g.Sum(e => e.Units),
                UnitsOut = g.Sum(e => e.UnitsOut),
                CostUsd = g.Sum(e => e.CostUsd)
            })
            .OrderBy(r => r.Date)
            .ThenBy(r => r.Meter)
            .ToListAsync(ct);

        var meterUsage = await events
            .GroupBy(e => e.Meter)
            .Select(g => new
            {
                Meter = g.Key,
                MinTime = g.Min(e => e.OccurredAt),
                HasOutput = g.Any(e => e.UnitsOut != null)
            })
            .ToListAsync(ct);

        var rates = await LoadRatesAsync(ct);
        var missing = new List<UsageMissingRateDto>();
        foreach (var meter in meterUsage.OrderBy(m => m.Meter))
        {
            foreach (var kind in KindsFor(meter.Meter, meter.HasOutput))
            {
                var inForce = rates.Any(r =>
                    r.Meter == meter.Meter && r.UnitKind == kind && r.ValidFrom <= meter.MinTime);
                if (!inForce)
                {
                    missing.Add(new UsageMissingRateDto(meter.Meter, kind));
                }
            }
        }

        IReadOnlyList<UsageCapDto>? caps = null;
        if (projectId is not null)
        {
            var capRows = await _db.LocalizationUsageCaps
                .AsNoTracking()
                .Where(c => c.ProjectId == projectId.Value)
                .ToListAsync(ct);
            var used = await UsedTotalsAsync(projectId.Value, start, end, ct);
            caps = new[] { UsageCapKinds.MachineTranslation, UsageCapKinds.Llm }
                .Select(kind => new UsageCapDto(
                    kind,
                    capRows.FirstOrDefault(c => c.Kind == kind)?.MonthlyLimit,
                    used.TryGetValue(kind, out var total) ? total : 0L))
                .ToList();
        }

        return new UsageSummaryDto(
            $"{year:D4}-{month:D2}",
            projectSlug,
            byMeter.Select(r => new UsageMeterTotalDto(
                r.Meter, r.Calls, r.FailedCalls, r.CacheHits, r.Units, OutputUnits(r.Meter, r.UnitsOut), r.CostUsd)).ToList(),
            byOperation.Select(r => new UsageOperationTotalDto(
                r.Meter, r.Operation, r.Calls, r.FailedCalls, r.CacheHits, r.Units, OutputUnits(r.Meter, r.UnitsOut), r.CostUsd)).ToList(),
            byLocale.Select(r => new UsageLocaleTotalDto(
                r.Meter, r.LocaleCode, r.Calls, r.Units, OutputUnits(r.Meter, r.UnitsOut), r.CostUsd)).ToList(),
            byDay.Select(r => new UsageDayTotalDto(
                r.Date.ToString("yyyy-MM-dd"), r.Meter, r.Units, OutputUnits(r.Meter, r.UnitsOut), r.CostUsd)).ToList(),
            missing,
            caps);
    }

    // SUM over a column that is always null comes back as 0 from SQL (EF adds COALESCE);
    // the character meter has no output units, so report null rather than 0 (CONTRACT 4.1).
    private static int? OutputUnits(string meter, int? summed) =>
        meter == UsageMeters.MachineTranslation ? null : summed;

    /// <summary>
    /// Loads the project's caps and this UTC month's used totals for a run.
    /// At most two queries; the returned budget tracks in-run spending in memory.
    /// </summary>
    public async Task<UsageBudget> BeginRunAsync(int projectId, DateTime nowUtc, CancellationToken ct)
    {
        var monthStart = new DateTime(nowUtc.Year, nowUtc.Month, 1, 0, 0, 0, DateTimeKind.Utc);
        var monthEnd = monthStart.AddMonths(1);

        var caps = await _db.LocalizationUsageCaps
            .AsNoTracking()
            .Where(c => c.ProjectId == projectId)
            .ToListAsync(ct);

        var used = await UsedTotalsAsync(projectId, monthStart, monthEnd, ct);
        return new UsageBudget(caps.ToDictionary(c => c.Kind, c => c.MonthlyLimit), used);
    }

    private async Task<Dictionary<string, long>> UsedTotalsAsync(int projectId, DateTime start, DateTime end, CancellationToken ct)
    {
        var usage = await _db.LocalizationUsageEvents
            .AsNoTracking()
            .Where(e => e.ProjectId == projectId && !e.CacheHit && e.OccurredAt >= start && e.OccurredAt < end)
            .GroupBy(e => e.Meter)
            .Select(g => new
            {
                Meter = g.Key,
                Units = g.Sum(e => e.Units),
                UnitsOut = g.Sum(e => e.UnitsOut)
            })
            .ToListAsync(ct);

        long MeterUnits(string meter)
        {
            var row = usage.FirstOrDefault(u => u.Meter == meter);
            return row is null ? 0L : row.Units;
        }

        long MeterUnitsOut(string meter)
        {
            var row = usage.FirstOrDefault(u => u.Meter == meter);
            return row is null ? 0L : row.UnitsOut ?? 0L;
        }

        return new Dictionary<string, long>
        {
            [UsageCapKinds.MachineTranslation] = MeterUnits(UsageMeters.MachineTranslation),
            [UsageCapKinds.Llm] =
                MeterUnits(UsageMeters.LlmOptimize) + MeterUnitsOut(UsageMeters.LlmOptimize) +
                MeterUnits(UsageMeters.LlmScore) + MeterUnitsOut(UsageMeters.LlmScore)
        };
    }

    public async Task<IReadOnlyList<UsageEventDto>> GetRecentEventsAsync(string? projectSlug, int limit = 100, CancellationToken ct = default)
    {
        limit = Math.Clamp(limit, 1, 500);
        var projectId = await ResolveProjectIdAsync(projectSlug, ct);

        var query = _db.LocalizationUsageEvents.AsNoTracking();
        if (projectId is not null)
        {
            query = query.Where(e => e.ProjectId == projectId.Value);
        }

        var rows = await query
            .OrderByDescending(e => e.OccurredAt)
            .ThenByDescending(e => e.Id)
            .Select(e => new
            {
                e.Id,
                ProjectSlug = e.Project!.Slug,
                e.WorkflowStepId,
                e.Meter,
                e.Operation,
                e.LocaleCode,
                e.Units,
                e.UnitsOut,
                e.CacheHit,
                e.Succeeded,
                e.CostUsd,
                e.OccurredAt
            })
            .Take(limit)
            .ToListAsync(ct);

        return rows.Select(r => new UsageEventDto(
            r.Id, r.ProjectSlug, r.WorkflowStepId, r.Meter, r.Operation, r.LocaleCode,
            r.Units, r.UnitsOut, r.CacheHit, r.Succeeded, r.CostUsd, r.OccurredAt)).ToList();
    }

    private async Task<int?> ResolveProjectIdAsync(string? projectSlug, CancellationToken ct)
    {
        if (projectSlug is null)
        {
            return null;
        }

        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);
        if (project is null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        return project.Id;
    }

    private async Task<IReadOnlyList<LocalizationProviderRate>> LoadRatesAsync(CancellationToken ct)
    {
        if (_rates is null)
        {
            _rates = await _db.LocalizationProviderRates
                .AsNoTracking()
                .ToListAsync(ct);
        }

        return _rates;
    }

    private static decimal CostFor(IReadOnlyList<LocalizationProviderRate> rates, UsageCallRecord call, DateTime occurredAtUtc)
    {
        if (call.CacheHit)
        {
            return 0m;
        }

        if (call.Meter == UsageMeters.MachineTranslation)
        {
            return CostPart(rates, call.Meter, UsageUnitKinds.Char, call.Units, occurredAtUtc);
        }

        return CostPart(rates, call.Meter, UsageUnitKinds.InputToken, call.Units, occurredAtUtc)
            + CostPart(rates, call.Meter, UsageUnitKinds.OutputToken, call.UnitsOut ?? 0, occurredAtUtc);
    }

    private static decimal CostPart(IReadOnlyList<LocalizationProviderRate> rates, string meter, string unitKind, int units, DateTime occurredAtUtc)
    {
        var rate = rates
            .Where(r => r.Meter == meter && r.UnitKind == unitKind && r.ValidFrom <= occurredAtUtc)
            .OrderByDescending(r => r.ValidFrom)
            .FirstOrDefault();
        if (rate is null)
        {
            return 0m;
        }

        return (decimal)units * rate.UsdPerMillion / 1000000m;
    }

    private static IEnumerable<string> KindsFor(string meter, bool hasOutput)
    {
        if (meter == UsageMeters.MachineTranslation)
        {
            yield return UsageUnitKinds.Char;
            yield break;
        }

        yield return UsageUnitKinds.InputToken;
        if (hasOutput)
        {
            yield return UsageUnitKinds.OutputToken;
        }
    }
}

/// <summary>
/// In-memory cap budget for one workflow run. A kind without a cap row is uncapped.
/// </summary>
public sealed class UsageBudget
{
    private readonly Dictionary<string, long> _limits;
    private readonly Dictionary<string, long> _used;

    public UsageBudget(IReadOnlyDictionary<string, long> limits, IReadOnlyDictionary<string, long> used)
    {
        _limits = new Dictionary<string, long>(limits);
        _used = new Dictionary<string, long>(used);
    }

    public bool CanSpend(string capKind, int knownUnits)
    {
        if (!_limits.TryGetValue(capKind, out var limit))
        {
            return true;
        }

        var used = Used(capKind);
        if (capKind == UsageCapKinds.MachineTranslation)
        {
            return used + knownUnits <= limit;
        }

        return used < limit;
    }

    public void Spent(string capKind, int units)
    {
        _used[capKind] = Used(capKind) + units;
    }

    public long Used(string capKind)
    {
        return _used.TryGetValue(capKind, out var used) ? used : 0L;
    }

    public long? Limit(string capKind)
    {
        return _limits.TryGetValue(capKind, out var limit) ? limit : null;
    }
}
