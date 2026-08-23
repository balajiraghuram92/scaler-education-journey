using System;
using System.Collections.Generic;
using StudyTracker.Api.Services;
using Xunit;

namespace StudyTracker.Api.Tests;

public class CurriculumImportTests
{
    [Fact]
    public void CurriculumImportRequest_Validation()
    {
        var req = new CurriculumImportRequest
        {
            CourseSlug = "java-spring-lld",
            ModuleSlug = "concurrency",
            Title = "Virtual Threads & Structured Concurrency",
            EstimatedMinutes = 60,
            ContentStatus = "Published"
        };

        Assert.Equal("java-spring-lld", req.CourseSlug);
        Assert.Equal("concurrency", req.ModuleSlug);
        Assert.Equal("Virtual Threads & Structured Concurrency", req.Title);
        Assert.Equal("Published", req.ContentStatus);
    }
}
