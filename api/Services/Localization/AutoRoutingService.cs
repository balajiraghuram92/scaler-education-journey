using System;
using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

public class AutoRoutingService
{
    /// <summary>
    /// HAND-WRITTEN BOUNDARY: comparing the QPS score against the project's
    /// threshold to decide Approved vs Needs Review is hand-written routing
    /// logic. Do not implement the comparison/decision here.
    /// </summary>
    public Task<bool> ShouldRouteToReviewAsync(int qpsScore, int projectThreshold, CancellationToken ct)
    {
        throw new NotImplementedException("Auto-Routing decision logic is hand-written per the project's locked AI boundary.");
    }
}
