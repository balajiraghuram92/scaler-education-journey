using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

/// <summary>
/// Seeds a file-driven course from a folder under Data/Content/{folder}:
///   course.json              — vertical, course, modules and lesson metadata (source of truth for structure)
///   lessons/{slug}.md        — lesson body (markdown)
///   assignments/{slug}.json  — coding assignments, stored as Problems
///   diagrams/{slug}.json     — inline SVG diagrams, referenced from the body as {{diagram:N}} (N = order index)
///   mcqs/{slug}.json         — multiple-choice questions, keyed by a globally unique legacyKey
///
/// The files are canonical: when a lesson file changes, the stored body is replaced and the lesson
/// returns to Draft for review. Diagrams and MCQs are updated in place from their files. Learner
/// progress, notes and MCQ history are keyed by lesson id, question id and option key, so they
/// survive content updates.
/// </summary>
public static class ContentCurriculumSeedData
{
    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNameCaseInsensitive = true };

    public static void SeedFolder(StudyTrackerContext db, string folder)
    {
        var root = ResolveContentRoot(folder);
        if (root == null)
        {
            Console.WriteLine($"[WARN] Curriculum content folder (Data/Content/{folder}) was not found. Skipping.");
            return;
        }

        Seed(db, root);
    }

    public static void Seed(StudyTrackerContext db, string root)
    {
        var manifest = JsonSerializer.Deserialize<CourseManifest>(File.ReadAllText(Path.Combine(root, "course.json")), JsonOptions)
            ?? throw new InvalidOperationException($"{Path.Combine(root, "course.json")} could not be parsed.");

        var vertical = db.Verticals.FirstOrDefault(v => v.Name == manifest.VerticalName);
        if (vertical == null)
        {
            vertical = new StudyVertical { Name = manifest.VerticalName, Description = manifest.VerticalDescription };
            db.Verticals.Add(vertical);
            db.SaveChanges();
        }

        var course = db.Courses.FirstOrDefault(c => c.Slug == manifest.Slug);
        if (course == null)
        {
            course = new Course { Slug = manifest.Slug };
            db.Courses.Add(course);
        }

        course.Title = manifest.Title;
        course.Description = manifest.Description;
        course.OrderIndex = manifest.OrderIndex;
        course.PathType = "Course";
        course.IsPublished = true;
        course.VerticalId = vertical.Id;
        db.SaveChanges();

        var lectureNumber = 0;
        var lessonsChanged = 0;
        for (var moduleIndex = 0; moduleIndex < manifest.Modules.Count; moduleIndex++)
        {
            var moduleDef = manifest.Modules[moduleIndex];
            var module = db.Modules.FirstOrDefault(m => m.CourseId == course.Id && m.Slug == moduleDef.Slug);
            if (module == null)
            {
                module = new CourseModule { CourseId = course.Id, Slug = moduleDef.Slug };
                db.Modules.Add(module);
            }

            module.Title = moduleDef.Title;
            module.Description = moduleDef.Description;
            module.Badge = moduleDef.Badge;
            module.OrderIndex = moduleIndex + 1;
            db.SaveChanges();

            for (var lessonIndex = 0; lessonIndex < moduleDef.Lessons.Count; lessonIndex++)
            {
                var lessonDef = moduleDef.Lessons[lessonIndex];
                lectureNumber++;

                var bodyPath = Path.Combine(root, "lessons", $"{lessonDef.Slug}.md");
                var body = File.Exists(bodyPath)
                    ? NormalizeNewlines(File.ReadAllText(bodyPath))
                    : $"# {lessonDef.Title}\n\n{lessonDef.Description}\n\nThis chapter is being written.";

                var lesson = db.Lessons.FirstOrDefault(l => l.ModuleId == module.Id && l.Slug == lessonDef.Slug);
                if (lesson == null)
                {
                    lesson = new Lesson
                    {
                        ModuleId = module.Id,
                        Slug = lessonDef.Slug,
                        ClassDate = string.Empty,
                        ContentStatus = File.Exists(bodyPath) ? "Draft" : "Outline",
                        ContentBody = body,
                        CreatedAt = DateTime.UtcNow
                    };
                    db.Lessons.Add(lesson);
                    lessonsChanged++;
                }
                else if (!string.Equals(NormalizeNewlines(lesson.ContentBody), body, StringComparison.Ordinal))
                {
                    lesson.ContentBody = body;
                    lesson.ContentStatus = File.Exists(bodyPath) ? "Draft" : "Outline";
                    lesson.UpdatedAt = DateTime.UtcNow;
                    lessonsChanged++;
                }

                lesson.Title = lessonDef.Title;
                lesson.Description = lessonDef.Description;
                lesson.LectureNumber = lectureNumber;
                lesson.OrderIndex = lessonIndex + 1;
                lesson.EstimatedMinutes = lessonDef.Minutes > 0 ? lessonDef.Minutes : 60;
                lesson.Difficulty = string.IsNullOrWhiteSpace(lessonDef.Difficulty) ? "Intermediate" : lessonDef.Difficulty;
                lesson.HorstmannRef = lessonDef.Reference ?? string.Empty;
                db.SaveChanges();

                SeedAssignments(db, root, lesson);
                SeedDiagrams(db, root, lesson);
                SeedMcqs(db, root, lesson);
            }
        }

        Console.WriteLine($"[INFO] {manifest.Title} seeded: {manifest.Modules.Count} modules, {lectureNumber} lessons ({lessonsChanged} new or updated).");
    }

    private static void SeedAssignments(StudyTrackerContext db, string root, Lesson lesson)
    {
        var path = Path.Combine(root, "assignments", $"{lesson.Slug}.json");
        if (!File.Exists(path)) return;

        var file = JsonSerializer.Deserialize<AssignmentFile>(File.ReadAllText(path), JsonOptions);
        if (file?.Assignments == null) return;

        for (var i = 0; i < file.Assignments.Count; i++)
        {
            var def = file.Assignments[i];
            if (string.IsNullOrWhiteSpace(def.Slug)) continue;

            var problem = db.Problems.FirstOrDefault(p => p.LessonId == lesson.Id && p.Slug == def.Slug);
            if (problem == null)
            {
                problem = new Problem { LessonId = lesson.Id, Slug = def.Slug, CreatedAt = DateTime.UtcNow };
                db.Problems.Add(problem);
            }

            problem.Title = Truncate(def.Title, 200);
            problem.Difficulty = Truncate(string.IsNullOrWhiteSpace(def.Difficulty) ? "Core" : def.Difficulty, 50);
            problem.PackageName = string.Empty;
            problem.TestClassName = string.Empty;
            problem.ProblemStatement = def.ProblemStatement ?? string.Empty;
            problem.RequirementsBody = def.Requirements ?? string.Empty;
            problem.WorkedExample = def.WorkedExample ?? string.Empty;
            problem.Hints = def.Hints ?? string.Empty;
            problem.ReferenceSolution = def.ReferenceSolution ?? string.Empty;
            problem.RunCommand = Truncate(string.IsNullOrWhiteSpace(def.RunCommand) ? "pytest -q" : def.RunCommand, 200);
            problem.Language = "python";
            problem.SourceType = Truncate(string.IsNullOrWhiteSpace(def.Source) ? "LLM_GENERATED" : def.Source, 30);
            problem.OrderIndex = i + 1;
            problem.UpdatedAt = DateTime.UtcNow;
        }

        db.SaveChanges();
    }

    private static void SeedDiagrams(StudyTrackerContext db, string root, Lesson lesson)
    {
        var path = Path.Combine(root, "diagrams", $"{lesson.Slug}.json");
        if (!File.Exists(path)) return;

        var file = JsonSerializer.Deserialize<DiagramFile>(File.ReadAllText(path), JsonOptions);
        if (file?.Diagrams == null) return;

        // Diagrams are matched by position: the body references them as {{diagram:N}}.
        var existing = db.LessonDiagrams.Where(d => d.LessonId == lesson.Id).ToList();
        for (var i = 0; i < file.Diagrams.Count; i++)
        {
            var def = file.Diagrams[i];
            var orderIndex = i + 1;
            var diagram = existing.FirstOrDefault(d => d.OrderIndex == orderIndex);
            if (diagram == null)
            {
                diagram = new LessonDiagram { LessonId = lesson.Id, OrderIndex = orderIndex, CreatedAt = DateTime.UtcNow };
                db.LessonDiagrams.Add(diagram);
            }

            diagram.Title = Truncate(string.IsNullOrWhiteSpace(def.Title) ? $"Diagram {orderIndex}" : def.Title, 200);
            diagram.Caption = Truncate(def.Caption, 300);
            diagram.DiagramType = "svg-inline";
            diagram.SvgContent = def.Svg ?? string.Empty;
        }

        db.LessonDiagrams.RemoveRange(existing.Where(d => d.OrderIndex > file.Diagrams.Count));
        db.SaveChanges();
    }

    private static void SeedMcqs(StudyTrackerContext db, string root, Lesson lesson)
    {
        var path = Path.Combine(root, "mcqs", $"{lesson.Slug}.json");
        if (!File.Exists(path)) return;

        var file = JsonSerializer.Deserialize<McqFile>(File.ReadAllText(path), JsonOptions);
        if (file?.Questions == null) return;

        var keys = file.Questions.Select(q => q.LegacyKey).Where(k => !string.IsNullOrWhiteSpace(k)).ToList();
        var existing = db.McqQuestions.Include(q => q.Options)
            .Where(q => q.LessonId == lesson.Id || (q.LegacyKey != null && keys.Contains(q.LegacyKey)))
            .ToList();

        foreach (var def in file.Questions)
        {
            if (string.IsNullOrWhiteSpace(def.LegacyKey)) continue;

            var question = existing.FirstOrDefault(q => q.LegacyKey == def.LegacyKey);
            if (question == null)
            {
                question = new McqQuestion { LegacyKey = def.LegacyKey, CreatedAt = DateTime.UtcNow };
                db.McqQuestions.Add(question);
            }

            question.LessonId = lesson.Id;
            question.QuestionText = def.QuestionText;
            question.Explanation = def.Explanation ?? string.Empty;
            question.SourceType = Truncate(string.IsNullOrWhiteSpace(def.SourceType) ? "FROM_MATERIAL" : def.SourceType, 50);
            question.Category = Truncate(string.IsNullOrWhiteSpace(def.Category) ? "Checkpoint" : def.Category, 30);
            question.IsActive = true;
            question.UpdatedAt = DateTime.UtcNow;

            // Attempts store the option key, so options are updated in place by key.
            foreach (var optionDef in def.Options)
            {
                var option = question.Options.FirstOrDefault(o => o.OptionKey == optionDef.OptionKey);
                if (option == null)
                {
                    option = new McqOption { OptionKey = optionDef.OptionKey };
                    question.Options.Add(option);
                }

                option.OptionText = optionDef.OptionText;
                option.IsCorrect = optionDef.IsCorrect;
            }

            foreach (var stale in question.Options.Where(o => def.Options.All(d => d.OptionKey != o.OptionKey)).ToList())
            {
                question.Options.Remove(stale);
                db.McqOptions.Remove(stale);
            }
        }

        // Questions removed from the file stop being served but keep their attempt history.
        foreach (var removed in existing.Where(q => q.LessonId == lesson.Id && !keys.Contains(q.LegacyKey ?? string.Empty)))
        {
            removed.IsActive = false;
        }

        db.SaveChanges();
    }

    public static string? ResolveContentRoot(string folder)
    {
        var candidates = new[]
        {
            Path.Combine(AppContext.BaseDirectory, "Data", "Content", folder),
            Path.Combine(Directory.GetCurrentDirectory(), "Data", "Content", folder),
            Path.Combine(Directory.GetCurrentDirectory(), "api", "Data", "Content", folder),
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "Data", "Content", folder)
        };

        return candidates.FirstOrDefault(c => File.Exists(Path.Combine(c, "course.json")));
    }

    private static string NormalizeNewlines(string? text) => (text ?? string.Empty).Replace("\r\n", "\n").TrimEnd() + "\n";

    private static string Truncate(string? value, int max)
    {
        var text = value ?? string.Empty;
        return text.Length <= max ? text : text[..max];
    }

    private sealed class CourseManifest
    {
        public string Slug { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string VerticalName { get; set; } = string.Empty;
        public string VerticalDescription { get; set; } = string.Empty;
        public int OrderIndex { get; set; } = 2;
        public List<ModuleManifest> Modules { get; set; } = new();
    }

    private sealed class ModuleManifest
    {
        public string Slug { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Badge { get; set; } = string.Empty;
        public List<LessonManifest> Lessons { get; set; } = new();
    }

    private sealed class LessonManifest
    {
        public string Slug { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public int Minutes { get; set; }
        public string? Difficulty { get; set; }
        public string? Reference { get; set; }
    }

    private sealed class AssignmentFile
    {
        public List<AssignmentDefinition> Assignments { get; set; } = new();
    }

    private sealed class AssignmentDefinition
    {
        public string Slug { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string? Difficulty { get; set; }
        public string? Source { get; set; }
        public string? ProblemStatement { get; set; }
        public string? Requirements { get; set; }
        public string? WorkedExample { get; set; }
        public string? Hints { get; set; }
        public string? ReferenceSolution { get; set; }
        public string? RunCommand { get; set; }
    }

    private sealed class DiagramFile
    {
        public List<DiagramDefinition> Diagrams { get; set; } = new();
    }

    private sealed class DiagramDefinition
    {
        public string Title { get; set; } = string.Empty;
        public string? Caption { get; set; }
        public string? Svg { get; set; }
    }

    private sealed class McqFile
    {
        public List<McqDefinition> Questions { get; set; } = new();
    }

    private sealed class McqDefinition
    {
        public string LegacyKey { get; set; } = string.Empty;
        public string QuestionText { get; set; } = string.Empty;
        public string? Explanation { get; set; }
        public string? SourceType { get; set; }
        public string? Category { get; set; }
        public List<McqOptionDefinition> Options { get; set; } = new();
    }

    private sealed class McqOptionDefinition
    {
        public string OptionKey { get; set; } = string.Empty;
        public string OptionText { get; set; } = string.Empty;
        public bool IsCorrect { get; set; }
    }
}
