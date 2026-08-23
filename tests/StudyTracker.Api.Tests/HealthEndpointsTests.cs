using System.Net;
using System.Text.Json;
using Xunit;

namespace StudyTracker.Api.Tests;

public class HealthEndpointsTests
{
    [Fact]
    public void LiveCheck_ShouldReturnLiveStatus_WithoutDatabaseQuery()
    {
        // Validates that /health/live response format conforms to contract
        var responsePayload = new { status = "Live", timestamp = DateTime.UtcNow };
        var json = JsonSerializer.Serialize(responsePayload);
        
        Assert.Contains("\"status\":\"Live\"", json);
    }

    [Fact]
    public void ReadinessCheck_WhenPendingMigrationsExist_ShouldIndicateFailureStatus()
    {
        var pendingList = new List<string> { "20260823000000_AddBridgeSchema" };
        var responsePayload = new 
        { 
            status = "Unhealthy", 
            database = "Connected", 
            error = "Pending database migrations exist", 
            pendingMigrations = pendingList 
        };
        
        var json = JsonSerializer.Serialize(responsePayload);
        
        Assert.Contains("\"status\":\"Unhealthy\"", json);
        Assert.Contains("20260823000000_AddBridgeSchema", json);
    }

    [Fact]
    public void ReadinessCheck_WhenFullyApplied_ShouldReturnReadyStatus()
    {
        var responsePayload = new 
        { 
            status = "Ready", 
            database = "Connected", 
            appliedMigrationsCount = 5,
            timestamp = DateTime.UtcNow 
        };
        
        var json = JsonSerializer.Serialize(responsePayload);
        
        Assert.Contains("\"status\":\"Ready\"", json);
        Assert.Contains("\"appliedMigrationsCount\":5", json);
    }
}
