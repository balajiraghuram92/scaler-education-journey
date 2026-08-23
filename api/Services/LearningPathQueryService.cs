using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services;

public class LearningPathDto
{
    public int Id { get; set; }
    public string Slug { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string PathType { get; set; } = "Course";
    public bool IsPublished { get; set; } = true;
    public int OrderIndex { get; set; }
    public int TotalLessons { get; set; }
    public int CompletedLessons { get; set; }
    public int ProgressPercentage => TotalLessons == 0 ? 0 : (int)Math.Round((double)CompletedLessons / TotalLessons * 100);
    public List<string> Domains { get; set; } = new();
    public List<ModuleDto> Modules { get; set; } = new();
}

public class ModuleDto
{
    public int Id { get; set; }
    public string Slug { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Badge { get; set; } = string.Empty;
    public int OrderIndex { get; set; }
    public List<LearningPathLessonSummaryDto> Lessons { get; set; } = new();
}

public class LearningPathLessonSummaryDto
{
    public int Id { get; set; }
    public string Slug { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Difficulty { get; set; } = "Intermediate";
    public string ContentStatus { get; set; } = "Published";
    public int EstimatedMinutes { get; set; }
    public bool IsCompleted { get; set; }
    public int OrderIndex { get; set; }
    public int ProblemCount { get; set; }
    public List<string> ConceptSlugs { get; set; } = new();
}

public class LearningPathQueryService
{
    private readonly StudyTrackerContext _db;

    public LearningPathQueryService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<List<LearningPathDto>> GetAllLearningPathsAsync()
    {
        var courses = await _db.Courses
            .Include(c => c.DomainLinks)
                .ThenInclude(dl => dl.Domain)
            .Include(c => c.Modules)
                .ThenInclude(m => m.Lessons)
                    .ThenInclude(l => l.Problems)
            .OrderBy(c => c.OrderIndex)
            .ToListAsync();

        return courses.Select(MapToPathDto).ToList();
    }

    public async Task<LearningPathDto?> GetLearningPathBySlugAsync(string slug)
    {
        var course = await _db.Courses
            .Include(c => c.DomainLinks)
                .ThenInclude(dl => dl.Domain)
            .Include(c => c.Modules)
                .ThenInclude(m => m.Lessons)
                    .ThenInclude(l => l.Problems)
            .Include(c => c.Modules)
                .ThenInclude(m => m.Lessons)
                    .ThenInclude(l => l.ConceptLinks)
                        .ThenInclude(cl => cl.Concept)
            .FirstOrDefaultAsync(c => c.Slug == slug);

        return course == null ? null : MapToPathDto(course);
    }

    private static LearningPathDto MapToPathDto(Course c)
    {
        var allLessons = c.Modules.SelectMany(m => m.Lessons).ToList();
        return new LearningPathDto
        {
            Id = c.Id,
            Slug = c.Slug,
            Title = c.Title,
            Description = c.Description,
            PathType = c.PathType,
            IsPublished = c.IsPublished,
            OrderIndex = c.OrderIndex,
            TotalLessons = allLessons.Count,
            CompletedLessons = allLessons.Count(l => l.IsCompleted),
            Domains = c.DomainLinks.Select(dl => dl.Domain?.Name ?? string.Empty).Where(n => !string.IsNullOrEmpty(n)).ToList(),
            Modules = c.Modules.OrderBy(m => m.OrderIndex).Select(m => new ModuleDto
            {
                Id = m.Id,
                Slug = m.Slug,
                Title = m.Title,
                Description = m.Description,
                Badge = m.Badge,
                OrderIndex = m.OrderIndex,
                Lessons = m.Lessons.OrderBy(l => l.OrderIndex).Select(l => new LearningPathLessonSummaryDto
                {
                    Id = l.Id,
                    Slug = l.Slug,
                    Title = l.Title,
                    Difficulty = l.Difficulty,
                    ContentStatus = l.ContentStatus,
                    EstimatedMinutes = l.EstimatedMinutes,
                    IsCompleted = l.IsCompleted,
                    OrderIndex = l.OrderIndex,
                    ProblemCount = l.Problems.Count,
                    ConceptSlugs = l.ConceptLinks.Select(cl => cl.Concept?.Slug ?? string.Empty).Where(s => !string.IsNullOrEmpty(s)).ToList()
                }).ToList()
            }).ToList()
        };
    }
}
