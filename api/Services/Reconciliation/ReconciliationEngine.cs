using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using StudyTracker.Api.Data;

namespace StudyTracker.Api.Services.Reconciliation;

public class ReconciliationEngine
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<ReconciliationEngine> _logger;
    private readonly JavaReconciler _javaReconciler;
    private readonly FdeReconciler _fdeReconciler;
    private readonly AzureLabsReconciler _azureLabsReconciler;
    private readonly AtlasReadingReconciler _atlasReadingReconciler;

    public ReconciliationEngine(
        StudyTrackerContext db,
        ILogger<ReconciliationEngine> logger,
        JavaReconciler javaReconciler,
        FdeReconciler fdeReconciler,
        AzureLabsReconciler azureLabsReconciler,
        AtlasReadingReconciler atlasReadingReconciler)
    {
        _db = db;
        _logger = logger;
        _javaReconciler = javaReconciler;
        _fdeReconciler = fdeReconciler;
        _azureLabsReconciler = azureLabsReconciler;
        _atlasReadingReconciler = atlasReadingReconciler;
    }

    public async Task<List<ReconciliationReport>> ExecuteAsync(ReconciliationOptions options)
    {
        var reports = new List<ReconciliationReport>();
        var scope = options.Scope.ToLowerInvariant();

        _logger.LogInformation("Executing ReconciliationEngine for scope '{Scope}' in '{Mode}' mode.", scope, options.Mode);

        if (scope == "java" || scope == "all")
        {
            reports.Add(await _javaReconciler.ReconcileJavaAsync(options.Mode));
        }

        if (scope == "fde" || scope == "all")
        {
            reports.Add(await _fdeReconciler.ReconcileFdeAsync(options.Mode));
        }

        if (scope == "azure" || scope == "labs" || scope == "azure-labs" || scope == "all")
        {
            reports.Add(await _azureLabsReconciler.ReconcileAzureAndLabsAsync(options.Mode));
        }

        if (scope == "atlas" || scope == "reading-map" || scope == "knowledge-threads" || scope == "all")
        {
            reports.Add(await _atlasReadingReconciler.ReconcileAtlasAndReadingAsync(options.Mode));
        }

        return reports;
    }
}
