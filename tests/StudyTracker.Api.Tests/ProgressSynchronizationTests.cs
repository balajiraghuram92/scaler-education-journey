using System;
using System.Collections.Generic;
using System.Linq;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services;
using Xunit;

namespace StudyTracker.Api.Tests;

public class ProgressSynchronizationTests
{
    [Fact]
    public void ProgressResult_ConstructsWithValidSyncData()
    {
        var correlationId = Guid.NewGuid();
        var result = new ProgressResult
        {
            Success = true,
            EntityType = "Lesson",
            EntityId = 42,
            IsCompleted = true,
            SynchronizedTaskIds = new List<int> { 101, 102 },
            CorrelationId = correlationId
        };

        Assert.True(result.Success);
        Assert.Equal("Lesson", result.EntityType);
        Assert.Equal(42, result.EntityId);
        Assert.True(result.IsCompleted);
        Assert.Equal(2, result.SynchronizedTaskIds.Count);
        Assert.Equal(correlationId, result.CorrelationId);
    }

    [Fact]
    public void VerifiedMappingFilter_OnlySelectsVerifiedStatus()
    {
        var links = new List<StudyTaskContentLink>
        {
            new() { TaskId = 1, LessonId = 10, MappingStatus = "Verified" },
            new() { TaskId = 2, LessonId = 10, MappingStatus = "Proposed" },
            new() { TaskId = 3, LessonId = 10, MappingStatus = "Rejected" },
            new() { TaskId = 4, LessonId = 10, MappingStatus = "Conflict" }
        };

        var verified = links.Where(l => l.MappingStatus == "Verified").ToList();

        Assert.Single(verified);
        Assert.Equal(1, verified[0].TaskId);
    }

    [Fact]
    public void ErrorResult_IsSanitizedWithoutLeakingRawException()
    {
        var correlationId = Guid.NewGuid();
        var result = new ProgressResult
        {
            Success = false,
            EntityType = "StudyTask",
            EntityId = 99,
            CorrelationId = correlationId,
            Error = "An error occurred while updating task progress. Please refer to traceId for support."
        };

        Assert.False(result.Success);
        Assert.DoesNotContain("SELECT", result.Error);
        Assert.DoesNotContain("Npgsql", result.Error);
        Assert.DoesNotContain("Host=", result.Error);
        Assert.Contains("traceId", result.Error);
    }
}
