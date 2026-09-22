using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public static class McqMigrationSeedData
{
    public static void Seed(StudyTrackerContext db)
    {
        var candidatePaths = new[]
        {
            Path.Combine(AppContext.BaseDirectory, "scripts", "mcq-migration-data.json"),
            Path.Combine(AppContext.BaseDirectory, "Data", "mcq-migration-data.json"),
            Path.Combine(AppContext.BaseDirectory, "mcq-migration-data.json"),
            Path.Combine(Directory.GetCurrentDirectory(), "scripts", "mcq-migration-data.json"),
            Path.Combine(Directory.GetCurrentDirectory(), "api", "Data", "mcq-migration-data.json"),
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "scripts", "mcq-migration-data.json"),
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "scripts", "mcq-migration-data.json"),
            Path.Combine(Directory.GetCurrentDirectory(), "..", "scripts", "mcq-migration-data.json")
        };

        string? resolvedPath = candidatePaths.FirstOrDefault(File.Exists);
        if (resolvedPath == null)
        {
            Console.WriteLine("[WARN] mcq-migration-data.json was not found in any candidate path. Skipping MCQ seeding.");
            return;
        }

        Console.WriteLine($"[INFO] Loading MCQ migration data from {resolvedPath}");
        string jsonContent;
        try
        {
            jsonContent = File.ReadAllText(resolvedPath);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] Failed to read MCQ migration file at '{resolvedPath}': {ex.Message}");
            return;
        }

        var jsonOptions = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
        List<LessonMigrationGroup>? lessonGroups;
        try
        {
            lessonGroups = JsonSerializer.Deserialize<List<LessonMigrationGroup>>(jsonContent, jsonOptions);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] Failed to parse MCQ migration JSON: {ex.Message}");
            return;
        }

        if (lessonGroups == null || lessonGroups.Count == 0)
        {
            Console.WriteLine("[WARN] No MCQ migration data found in file.");
            return;
        }

        var allLessons = db.Lessons
            .Include(l => l.Module)
                .ThenInclude(m => m!.Course)
            .ToList();

        var lessonLookup = new Dictionary<string, Lesson>(StringComparer.OrdinalIgnoreCase);
        foreach (var l in allLessons)
        {
            if (l.Module?.Course != null)
            {
                var key = $"{l.Module.Course.Slug}/{l.Module.Slug}/{l.Slug}";
                lessonLookup[key] = l;
            }
        }

        var existingKeys = db.McqQuestions
            .Select(q => q.LegacyKey)
            .Where(k => !string.IsNullOrEmpty(k))
            .ToHashSet(StringComparer.OrdinalIgnoreCase);

        int addedCount = 0;
        int skippedCount = 0;
        int totalQuestions = 0;

        foreach (var group in lessonGroups)
        {
            var lookupKey = $"{group.CourseSlug}/{group.ModuleSlug}/{group.LessonSlug}";
            if (!lessonLookup.TryGetValue(lookupKey, out var lesson))
            {
                lesson = db.Lessons
                    .Include(l => l.Module)
                        .ThenInclude(m => m!.Course)
                    .FirstOrDefault(l => l.Slug == group.LessonSlug &&
                                         l.Module != null && l.Module.Slug == group.ModuleSlug &&
                                         l.Module.Course != null && l.Module.Course.Slug == group.CourseSlug);

                if (lesson != null)
                {
                    lessonLookup[lookupKey] = lesson;
                }
            }

            if (lesson == null)
            {
                Console.WriteLine($"[WARN] Lesson not found for key '{lookupKey}'. Skipping {group.Questions.Count} question(s).");
                continue;
            }

            foreach (var q in group.Questions)
            {
                totalQuestions++;
                if (!string.IsNullOrWhiteSpace(q.LegacyKey) && existingKeys.Contains(q.LegacyKey))
                {
                    skippedCount++;
                    continue;
                }

                var questionEntity = new McqQuestion
                {
                    LessonId = lesson.Id,
                    LegacyKey = string.IsNullOrWhiteSpace(q.LegacyKey) ? null : q.LegacyKey.Trim(),
                    QuestionText = q.QuestionText ?? string.Empty,
                    SourceType = string.IsNullOrWhiteSpace(q.SourceType) ? "FROM_MATERIAL" : q.SourceType.Trim(),
                    Explanation = q.Explanation ?? string.Empty,
                    IsActive = true,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                };

                if (q.Options != null)
                {
                    foreach (var opt in q.Options)
                    {
                        questionEntity.Options.Add(new McqOption
                        {
                            OptionKey = opt.OptionKey?.Trim() ?? string.Empty,
                            OptionText = opt.OptionText ?? string.Empty,
                            IsCorrect = opt.IsCorrect
                        });
                    }
                }

                db.McqQuestions.Add(questionEntity);
                if (!string.IsNullOrWhiteSpace(questionEntity.LegacyKey))
                {
                    existingKeys.Add(questionEntity.LegacyKey);
                }
                addedCount++;

                // Batch save every 250 records to keep change tracking performant
                if (addedCount % 250 == 0)
                {
                    db.SaveChanges();
                }
            }
        }

        if (addedCount % 250 != 0)
        {
            db.SaveChanges();
        }

        Console.WriteLine($"[INFO] MCQ dynamic seeding completed. Added {addedCount} questions, skipped {skippedCount} existing questions (total evaluated: {totalQuestions}).");
    }

    private sealed class LessonMigrationGroup
    {
        public string CourseSlug { get; set; } = string.Empty;
        public string ModuleSlug { get; set; } = string.Empty;
        public string LessonSlug { get; set; } = string.Empty;
        public List<QuestionMigrationItem> Questions { get; set; } = new();
    }

    private sealed class QuestionMigrationItem
    {
        public string LegacyKey { get; set; } = string.Empty;
        public string QuestionText { get; set; } = string.Empty;
        public string SourceType { get; set; } = "FROM_MATERIAL";
        public string Explanation { get; set; } = string.Empty;
        public List<OptionMigrationItem> Options { get; set; } = new();
    }

    private sealed class OptionMigrationItem
    {
        public string OptionKey { get; set; } = string.Empty;
        public string OptionText { get; set; } = string.Empty;
        public bool IsCorrect { get; set; }
    }
}
