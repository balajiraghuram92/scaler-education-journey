using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services;

public class BudgetGuardService
{
    private readonly StudyTrackerContext _db;
    private readonly BudgetOptions _options;
    private readonly ILogger<BudgetGuardService> _logger;

    public BudgetGuardService(
        StudyTrackerContext db,
        IOptions<BudgetOptions> options,
        ILogger<BudgetGuardService> logger)
    {
        _db = db;
        _options = options.Value;
        _logger = logger;
    }

    public async Task<UsageSummaryDto> GetTodayUsageAsync(CancellationToken ct = default)
    {
        var startOfDayUtc = DateTime.UtcNow.Date;

        var assistantMessages = _db.ChatMessages
            .AsNoTracking()
            .Where(m => m.Role == "assistant" && m.CreatedAt >= startOfDayUtc);

        var totalCostToday = await assistantMessages
            .SumAsync(m => m.EstimatedCostUsd ?? 0m, ct);

        var requestCountToday = await assistantMessages
            .CountAsync(ct);

        var dailyCap = _options.DailyCapUsd > 0 ? _options.DailyCapUsd : 2.00m;
        var maxRequests = _options.MaxDailyRequests > 0 ? _options.MaxDailyRequests : 500;

        var exceeded = totalCostToday >= dailyCap || requestCountToday >= maxRequests;

        return new UsageSummaryDto(
            TotalCostTodayUsd: decimal.Round(totalCostToday, 6),
            DailyCapUsd: dailyCap,
            RequestCountToday: requestCountToday,
            MaxDailyRequests: maxRequests,
            BudgetExceeded: exceeded
        );
    }

    public async Task<(bool Allowed, UsageSummaryDto Usage)> TryReserveRequestAsync(CancellationToken ct = default)
    {
        var usage = await GetTodayUsageAsync(ct);

        if (usage.BudgetExceeded)
        {
            _logger.LogWarning(
                "Daily AI Chat budget reached! Cost today: ${Cost:F4}/${Cap:F2}, Requests: {Count}/{MaxRequests}",
                usage.TotalCostTodayUsd,
                usage.DailyCapUsd,
                usage.RequestCountToday,
                usage.MaxDailyRequests);

            return (false, usage);
        }

        return (true, usage);
    }
}
