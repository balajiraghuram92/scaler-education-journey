using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

/// <summary>
/// Seeds the Python Engineering course from files under Data/Content/python:
///   course.json              — vertical, course, modules and lesson metadata (source of truth for structure)
///   lessons/{slug}.md        — lesson body (markdown)
///   assignments/{slug}.json  — coding assignments, stored as Problems
///
/// Unlike the Java/FDE seeders, the files are canonical: when a lesson file changes, the
/// stored body is replaced and the lesson returns to Draft for review. Learner progress,
/// notes and MCQ history are keyed by lesson id, so they survive content updates.
/// </summary>
public static class PythonCurriculumSeedData
{
    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNameCaseInsensitive = true };

    public static void Seed(StudyTrackerContext db, string? contentRoot = null)
    {
        var root = contentRoot ?? ResolveContentRoot();
        if (root == null)
        {
            Console.WriteLine("[WARN] Python curriculum content folder (Data/Content/python) was not found. Skipping Python seeding.");
            return;
        }

        var manifest = JsonSerializer.Deserialize<CourseManifest>(File.ReadAllText(Path.Combine(root, "course.json")), JsonOptions)
            ?? throw new InvalidOperationException("Python course.json could not be parsed.");

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
            }
        }

        Console.WriteLine($"[INFO] Python curriculum seeded: {manifest.Modules.Count} modules, {lectureNumber} lessons ({lessonsChanged} new or updated).");
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

    public static string? ResolveContentRoot()
    {
        var candidates = new[]
        {
            Path.Combine(AppContext.BaseDirectory, "Data", "Content", "python"),
            Path.Combine(Directory.GetCurrentDirectory(), "Data", "Content", "python"),
            Path.Combine(Directory.GetCurrentDirectory(), "api", "Data", "Content", "python"),
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "Data", "Content", "python")
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
        public string VerticalName { get; set; } = "Python Engineering";
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
}
