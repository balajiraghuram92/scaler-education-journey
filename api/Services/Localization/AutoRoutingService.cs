using System;
using System.Threading;
using System.Threading.Tasks;

namespace StudyTracker.Api.Services.Localization;

/// <summary>
/// Thin client over the localization-ai /auto-route endpoint.
/// Contains no threshold or routing logic; that stays in the Python service.
/// </summary>
public class AutoRoutingService
{
    private readonly LocalizationAiClient? _client;

    public AutoRoutingService(LocalizationAiClient? client = null)
    {
        _client = client;
    }

    public async Task<bool> ShouldRouteToReviewAsync(int qpsScore, int projectThreshold, CancellationToken ct)
    {
        if (_client is null)
        {
            throw new NotImplementedException(LocalizationAiClient.NotConfiguredMessage);
        }

        var response = await _client.AutoRouteAsync(qpsScore, projectThreshold, null, ct);

        return response.NeedsReview;
    }
}
