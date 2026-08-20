using System;
using System.Linq;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public static class ReadingMapSeedData
{
    public static void Seed(StudyTrackerContext db)
    {
        // 1. Seed Reading Map Items
        if (!db.ReadingMapItems.Any())
        {
            var items = new[]
            {
                // Read this week
                new ReadingMapItem { Category = "ReadThisWeek", Title = "Virtual threads", OrderIndex = 1, IsCompleted = true },
                new ReadingMapItem { Category = "ReadThisWeek", Title = "Structured concurrency", OrderIndex = 2, IsCompleted = true },
                new ReadingMapItem { Category = "ReadThisWeek", Title = "Structured concurrency (8)", OrderIndex = 3, IsCompleted = true },
                new ReadingMapItem { Category = "ReadThisWeek", Title = "Structured concurrency", OrderIndex = 4, IsCompleted = true },

                // Revisited
                new ReadingMapItem { Category = "Revisited", Title = "Spring async and resilience", OrderIndex = 1, IsCompleted = false },

                // Deferred
                new ReadingMapItem { Category = "Deferred", Title = "Next sometime", OrderIndex = 1, IsCompleted = false },
                new ReadingMapItem { Category = "Deferred", Title = "Deferred tomorrow", OrderIndex = 2, IsCompleted = false },

                // Lists
                new ReadingMapItem { Category = "Lists", Title = "APIs in (2)", OrderIndex = 1, IsCompleted = false },
                new ReadingMapItem { Category = "Lists", Title = "Deferred (1)", OrderIndex = 2, IsCompleted = false },

                // Prerequisites
                new ReadingMapItem { Category = "Prerequisites", Title = "Java Concurrency", OrderIndex = 1, IsCompleted = false }
            };

            db.ReadingMapItems.AddRange(items);
        }

        // 2. Seed Reading Activity Logs (7-day timeline sparkline matching Study-tracker.png)
        if (!db.ReadingActivityLogs.Any())
        {
            var activityLogs = new[]
            {
                new ReadingActivityLog { DayLabel = "Mon", ActivityCount = 1, OrderIndex = 1, LogDate = DateTime.UtcNow.AddDays(-7) },
                new ReadingActivityLog { DayLabel = "Tue", ActivityCount = 1, OrderIndex = 2, LogDate = DateTime.UtcNow.AddDays(-6) },
                new ReadingActivityLog { DayLabel = "Wed", ActivityCount = 3, OrderIndex = 3, LogDate = DateTime.UtcNow.AddDays(-5) },
                new ReadingActivityLog { DayLabel = "Thu", ActivityCount = 6, OrderIndex = 4, LogDate = DateTime.UtcNow.AddDays(-4) },
                new ReadingActivityLog { DayLabel = "Fri", ActivityCount = 2, OrderIndex = 5, LogDate = DateTime.UtcNow.AddDays(-3) },
                new ReadingActivityLog { DayLabel = "Sat", ActivityCount = 4, OrderIndex = 6, LogDate = DateTime.UtcNow.AddDays(-2) },
                new ReadingActivityLog { DayLabel = "Sun", ActivityCount = 0, OrderIndex = 7, LogDate = DateTime.UtcNow.AddDays(-1) },
                new ReadingActivityLog { DayLabel = "Sun", ActivityCount = 5, OrderIndex = 8, LogDate = DateTime.UtcNow }
            };

            db.ReadingActivityLogs.AddRange(activityLogs);
        }

        // 3. Seed Knowledge Threads (Linear semantic progression pipelines)
        if (!db.KnowledgeThreads.Any())
        {
            var threads = new[]
            {
                new KnowledgeThread
                {
                    Domain = "Java",
                    RawPath = "Java → concurrency → virtual threads → structured concurrency",
                    OrderIndex = 1
                },
                new KnowledgeThread
                {
                    Domain = "Backend",
                    RawPath = "Backend → APIs → async processing → resilience",
                    OrderIndex = 2
                },
                new KnowledgeThread
                {
                    Domain = "Cloud",
                    RawPath = "Cloud → containers → orchestration → networking",
                    OrderIndex = 3
                }
            };

            db.KnowledgeThreads.AddRange(threads);
        }
    }
}
