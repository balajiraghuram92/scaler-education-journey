using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services;

public class ReadingMapService
{
    private readonly StudyTrackerContext _db;

    public ReadingMapService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<object> GetReadingMapAsync()
    {
        var items = await _db.ReadingMapItems
            .Include(r => r.Lesson)
            .OrderBy(r => r.OrderIndex)
            .ToListAsync();

        var threads = await _db.KnowledgeThreads
            .Include(t => t.Steps)
                .ThenInclude(s => s.Concept)
            .OrderBy(t => t.OrderIndex)
            .ToListAsync();

        var recentActivities = await _db.LearningActivities
            .Include(a => a.Lesson)
            .OrderByDescending(a => a.OccurredAt)
            .Take(30)
            .ToListAsync();

        var totalItems = items.Count;
        var completedItems = items.Count(i => i.IsCompleted || i.Status == "Completed");

        return new
        {
            statistics = new
            {
                totalItems,
                completedItems,
                progressPercentage = totalItems == 0 ? 0 : (int)((double)completedItems / totalItems * 100)
            },
            items = items.Select(i => new
            {
                i.Id,
                i.Category,
                i.Title,
                i.SubText,
                i.OrderIndex,
                i.IsCompleted,
                i.Status,
                i.ScheduledFor,
                i.Priority,
                i.IsSeeded,
                lessonSlug = i.Lesson?.Slug
            }),
            threads = threads.Select(t => new
            {
                t.Id,
                t.Domain,
                t.RawPath,
                steps = t.Steps.OrderBy(s => s.OrderIndex).Select(s => new
                {
                    s.OrderIndex,
                    s.Label,
                    conceptSlug = s.Concept?.Slug
                })
            }),
            recentActivities = recentActivities.Select(a => new
            {
                a.Id,
                a.EventType,
                a.OccurredAt,
                a.LessonId,
                lessonTitle = a.Lesson?.Title
            })
        };
    }
}
