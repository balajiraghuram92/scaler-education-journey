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

    /// <summary>
    /// True when a client is present and the AI service base URL is configured.
    /// Lets callers fail up front instead of discovering it per string.
    /// </summary>
    public bool IsConfigured => _client?.IsConfigured == true;

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
