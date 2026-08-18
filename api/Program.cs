using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using System.Text.RegularExpressions;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddDbContext<StudyTrackerContext>(options =>
{
    var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");

    if (string.IsNullOrWhiteSpace(connectionString))
    {
        var dbHost = builder.Configuration["DATABASE_HOST"] ?? "database";
        var dbPort = builder.Configuration["DATABASE_PORT"] ?? "5432";
        var dbName = builder.Configuration["DATABASE_NAME"] ?? "studytracker";
        var dbUser = builder.Configuration["DATABASE_USER"] ?? "studyuser";
        var dbPass = builder.Configuration["DATABASE_PASSWORD"] ?? builder.Configuration["POSTGRES_PASSWORD"];

        if (!string.IsNullOrWhiteSpace(dbPass))
        {
            connectionString = $"Host={dbHost};Port={dbPort};Database={dbName};Username={dbUser};Password={dbPass}";
        }
    }

    if (string.IsNullOrWhiteSpace(connectionString))
    {
        if (builder.Environment.IsProduction())
        {
            throw new InvalidOperationException("Production database connection configuration is missing.");
        }
        connectionString = "Host=localhost;Database=studytracker;Username=studyuser;Password=studyuserpass";
    }

    options.UseNpgsql(connectionString);
});

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.Configure<Microsoft.AspNetCore.Http.Json.JsonOptions>(options =>
{
    options.SerializerOptions.ReferenceHandler = System.Text.Json.Serialization.ReferenceHandler.IgnoreCycles;
});

// Add CORS policy
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowVite", policy =>
    {
        var frontendUrl = builder.Configuration["frontend_url"];
        var allowedOrigins = new List<string> { "http://localhost:5173" };
        
        if (!string.IsNullOrWhiteSpace(frontendUrl))
        {
            allowedOrigins.Add(frontendUrl.TrimEnd('/'));
        }
        
        policy.WithOrigins(allowedOrigins.ToArray())
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Apply CORS
app.UseCors("AllowVite");

// Apply API Key security
app.Use(async (context, next) =>
{
    if (context.Request.Path.StartsWithSegments("/health") || 
        context.Request.Path.StartsWithSegments("/swagger") || 
        context.Request.Method == "OPTIONS")
    {
        await next(context);
        return;
    }

    var expectedApiKey = builder.Configuration["api_key"] ?? builder.Configuration["API_KEY"];
    if (string.IsNullOrWhiteSpace(expectedApiKey))
    {
        if (app.Environment.IsProduction())
        {
            app.Logger.LogError("API key is not configured in production environment.");
            context.Response.StatusCode = 500;
            await context.Response.WriteAsync("Internal Server Error: API key is not configured.");
            return;
        }

        // Allow unauthenticated access only in non-production development testing
        await next(context);
        return;
    }

    if (!context.Request.Headers.TryGetValue("x-api-key", out var extractedApiKey) || extractedApiKey != expectedApiKey)
    {
        context.Response.StatusCode = 401;
        await context.Response.WriteAsync("Unauthorized: Invalid or missing API Key.");
        return;
    }

    await next(context);
});

// Health check endpoint for Docker Compose & CI/CD verification
app.MapGet("/health", async (StudyTrackerContext db) =>
{
    try
    {
        var canConnect = await db.Database.CanConnectAsync();
        if (canConnect)
        {
            return Results.Ok(new { status = "Healthy", database = "Connected", timestamp = DateTime.UtcNow });
        }
        return Results.Json(new { status = "Unhealthy", database = "Disconnected" }, statusCode: 503);
    }
    catch (Exception ex)
    {
        app.Logger.LogError(ex, "Health check database connection failed.");
        return Results.Json(new { status = "Unhealthy", error = "Database connection error" }, statusCode: 503);
    }
}).WithName("HealthCheck");

// Check if running as a separate script to populate data
if (args.Contains("--seed"))
{
    using var scope = app.Services.CreateScope();
    var db = scope.ServiceProvider.GetRequiredService<StudyTrackerContext>();
    DbSeeder.Initialize(db);
    return; // Exit script after seeding
}

// Apply schema migrations & idempotent seed on startup
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<StudyTrackerContext>();
    db.Database.Migrate();
    DbSeeder.Initialize(db);
}

app.MapGet("/", () => "StudyTracker API is running. Use /health for service health.");

// ==========================================
// 1. VERTICALS & TASKS ENDPOINTS (Base & Dynamic)
// ==========================================

app.MapGet("/api/verticals", async (StudyTrackerContext db) =>
    await db.Verticals.AsNoTracking().Include(v => v.Tasks).ToListAsync())
    .WithName("GetVerticals");

app.MapGet("/api/verticals/{id:int}", async (int id, StudyTrackerContext db) =>
{
    var vertical = await db.Verticals.AsNoTracking()
        .Include(v => v.Tasks)
        .FirstOrDefaultAsync(v => v.Id == id);

    return vertical != null ? Results.Ok(vertical) : Results.NotFound();
})
.WithName("GetVerticalById");

app.MapPost("/api/verticals", async (CreateVerticalRequest req, StudyTrackerContext db) =>
{
    if (string.IsNullOrWhiteSpace(req.Name))
    {
        return Results.BadRequest(new { message = "Name is required." });
    }

    var vertical = new StudyVertical
    {
        Name = req.Name,
        Description = req.Description ?? string.Empty
    };

    db.Verticals.Add(vertical);
    await db.SaveChangesAsync();

    return Results.Created($"/api/verticals/{vertical.Id}", vertical);
})
.WithName("CreateVertical");

app.MapPost("/api/verticals/ingest", async (IngestRequest req, StudyTrackerContext db) =>
{
    if (string.IsNullOrWhiteSpace(req.MarkdownContent))
    {
        return Results.BadRequest(new { message = "Markdown content is required." });
    }

    var parsedTasks = ParseMarkdownToTasks(req.MarkdownContent);

    if (req.VerticalId.HasValue && req.VerticalId.Value > 0)
    {
        var vertical = await db.Verticals
            .Include(v => v.Tasks)
            .FirstOrDefaultAsync(v => v.Id == req.VerticalId.Value);

        if (vertical == null)
        {
            return Results.NotFound(new { message = $"Vertical with ID {req.VerticalId} not found." });
        }

        if (!string.IsNullOrWhiteSpace(req.Name))
        {
            vertical.Name = req.Name;
        }
        if (req.Description != null)
        {
            vertical.Description = req.Description;
        }

        // Clear existing tasks and re-add parsed tasks
        db.Tasks.RemoveRange(vertical.Tasks);

        foreach (var task in parsedTasks)
        {
            vertical.Tasks.Add(task);
        }

        await db.SaveChangesAsync();
        return Results.Ok(vertical);
    }
    else
    {
        var vertical = new StudyVertical
        {
            Name = string.IsNullOrWhiteSpace(req.Name) ? "New Vertical" : req.Name,
            Description = req.Description ?? string.Empty
        };

        foreach (var task in parsedTasks)
        {
            vertical.Tasks.Add(task);
        }

        db.Verticals.Add(vertical);
        await db.SaveChangesAsync();

        return Results.Created($"/api/verticals/{vertical.Id}", vertical);
    }
})
.WithName("IngestVerticalMarkdown");

app.MapPut("/api/tasks/{id:int}/toggle", async (int id, StudyTrackerContext db) =>
{
    var task = await db.Tasks.FindAsync(id);
    if (task == null)
    {
        return Results.NotFound();
    }
    
    task.IsCompleted = !task.IsCompleted;
    await db.SaveChangesAsync();
    
    return Results.Ok(task);
})
.WithName("ToggleTask");

// ==========================================
// 2. COURSES & CURRICULUM ENDPOINTS (Hierarchical)
// ==========================================

app.MapGet("/api/courses", async (StudyTrackerContext db) =>
{
    var courses = await db.Courses.AsNoTracking()
        .Include(c => c.Modules)
            .ThenInclude(m => m.Lessons)
                .ThenInclude(l => l.Problems)
        .OrderBy(c => c.OrderIndex)
        .ToListAsync();

    var dtos = courses.Select(c =>
    {
        var allLessons = c.Modules.SelectMany(m => m.Lessons).ToList();
        var allProblems = allLessons.SelectMany(l => l.Problems).ToList();
        var totalLessons = allLessons.Count;
        var completedLessons = allLessons.Count(l => l.IsCompleted);
        var totalProblems = allProblems.Count;
        var completedProblems = allProblems.Count(p => p.IsCompleted);
        var progressPercent = totalLessons > 0 ? (int)Math.Round((double)completedLessons / totalLessons * 100) : 0;

        var moduleDtos = c.Modules.OrderBy(m => m.OrderIndex).Select(m =>
        {
            var mLessons = m.Lessons.OrderBy(l => l.OrderIndex).ToList();
            var mTotal = mLessons.Count;
            var mCompleted = mLessons.Count(l => l.IsCompleted);
            var mProgress = mTotal > 0 ? (int)Math.Round((double)mCompleted / mTotal * 100) : 0;

            return new ModuleSummaryDto(
                m.Id,
                m.CourseId,
                m.Slug,
                m.Title,
                m.Description,
                m.Badge,
                m.OrderIndex,
                mTotal,
                mCompleted,
                mProgress,
                mLessons.Select(l => new LessonSummaryDto(
                    l.Id,
                    l.ModuleId,
                    l.Slug,
                    l.Title,
                    l.Description,
                    l.LectureNumber,
                    l.ClassDate,
                    l.HorstmannRef,
                    l.EstimatedMinutes,
                    l.IsCompleted,
                    l.OrderIndex,
                    l.Problems.Count
                )).ToList()
            );
        }).ToList();

        return new CourseSummaryDto(
            c.Id,
            c.Slug,
            c.Title,
            c.Description,
            c.OrderIndex,
            c.VerticalId,
            totalLessons,
            completedLessons,
            totalProblems,
            completedProblems,
            progressPercent,
            moduleDtos
        );
    }).ToList();

    return Results.Ok(dtos);
})
.WithName("GetCourses");

app.MapGet("/api/courses/{slugOrId}", async (string slugOrId, StudyTrackerContext db) =>
{
    var query = db.Courses.AsNoTracking()
        .Include(c => c.Modules)
            .ThenInclude(m => m.Lessons)
                .ThenInclude(l => l.Problems);

    Course? course = null;
    if (int.TryParse(slugOrId, out int id))
    {
        course = await query.FirstOrDefaultAsync(c => c.Id == id);
    }
    else
    {
        course = await query.FirstOrDefaultAsync(c => c.Slug == slugOrId);
    }

    if (course == null) return Results.NotFound(new { message = "Course not found." });

    var allLessons = course.Modules.SelectMany(m => m.Lessons).ToList();
    var allProblems = allLessons.SelectMany(l => l.Problems).ToList();
    var totalLessons = allLessons.Count;
    var completedLessons = allLessons.Count(l => l.IsCompleted);
    var totalProblems = allProblems.Count;
    var completedProblems = allProblems.Count(p => p.IsCompleted);
    var progressPercent = totalLessons > 0 ? (int)Math.Round((double)completedLessons / totalLessons * 100) : 0;

    var moduleDtos = course.Modules.OrderBy(m => m.OrderIndex).Select(m =>
    {
        var mLessons = m.Lessons.OrderBy(l => l.OrderIndex).ToList();
        var mTotal = mLessons.Count;
        var mCompleted = mLessons.Count(l => l.IsCompleted);
        var mProgress = mTotal > 0 ? (int)Math.Round((double)mCompleted / mTotal * 100) : 0;

        return new ModuleSummaryDto(
            m.Id,
            m.CourseId,
            m.Slug,
            m.Title,
            m.Description,
            m.Badge,
            m.OrderIndex,
            mTotal,
            mCompleted,
            mProgress,
            mLessons.Select(l => new LessonSummaryDto(
                l.Id,
                l.ModuleId,
                l.Slug,
                l.Title,
                l.Description,
                l.LectureNumber,
                l.ClassDate,
                l.HorstmannRef,
                l.EstimatedMinutes,
                l.IsCompleted,
                l.OrderIndex,
                l.Problems.Count
            )).ToList()
        );
    }).ToList();

    var result = new CourseSummaryDto(
        course.Id,
        course.Slug,
        course.Title,
        course.Description,
        course.OrderIndex,
        course.VerticalId,
        totalLessons,
        completedLessons,
        totalProblems,
        completedProblems,
        progressPercent,
        moduleDtos
    );

    return Results.Ok(result);
})
.WithName("GetCourseBySlugOrId");

// ==========================================
// 3. LESSONS ENDPOINTS
// ==========================================

app.MapGet("/api/lessons/{id:int}", async (int id, StudyTrackerContext db) =>
{
    var lesson = await db.Lessons.AsNoTracking()
        .Include(l => l.Module)
            .ThenInclude(m => m!.Course)
        .Include(l => l.Problems.OrderBy(p => p.OrderIndex))
        .Include(l => l.Resources.OrderBy(r => r.OrderIndex))
        .FirstOrDefaultAsync(l => l.Id == id);

    if (lesson == null) return Results.NotFound(new { message = "Lesson not found." });

    var dto = new LessonDetailDto(
        lesson.Id,
        lesson.ModuleId,
        lesson.Module?.Title ?? string.Empty,
        lesson.Module?.CourseId ?? 0,
        lesson.Module?.Course?.Title ?? string.Empty,
        lesson.Slug,
        lesson.Title,
        lesson.Description,
        lesson.LectureNumber,
        lesson.ClassDate,
        lesson.ContentBody,
        lesson.HorstmannRef,
        lesson.EstimatedMinutes,
        lesson.IsCompleted,
        lesson.OrderIndex,
        lesson.Problems.Select(p => new ProblemSummaryDto(
            p.Id,
            p.LessonId,
            p.Slug,
            p.Title,
            p.Difficulty,
            p.PackageName,
            p.TestClassName,
            p.ProblemStatement,
            p.RequirementsBody,
            p.WorkedExample,
            p.Hints,
            p.IsCompleted,
            p.OrderIndex
        )).ToList(),
        lesson.Resources.Select(r => new LessonResourceDto(
            r.Id,
            r.LessonId,
            r.ResourceType,
            r.Title,
            r.ContentBody,
            r.OrderIndex
        )).ToList()
    );

    return Results.Ok(dto);
})
.WithName("GetLessonById");

app.MapPost("/api/lessons", async (CreateLessonRequest req, StudyTrackerContext db) =>
{
    if (string.IsNullOrWhiteSpace(req.Title) || string.IsNullOrWhiteSpace(req.Slug))
    {
        return Results.BadRequest(new { message = "Title and Slug are required." });
    }

    var moduleExists = await db.Modules.AnyAsync(m => m.Id == req.ModuleId);
    if (!moduleExists)
    {
        return Results.BadRequest(new { message = "Invalid ModuleId." });
    }

    var lesson = new Lesson
    {
        ModuleId = req.ModuleId,
        Slug = req.Slug.Trim().ToLowerInvariant(),
        Title = req.Title.Trim(),
        Description = req.Description ?? string.Empty,
        LectureNumber = req.LectureNumber,
        ClassDate = req.ClassDate ?? DateTime.UtcNow.ToString("yyyy-MM-dd"),
        ContentBody = req.ContentBody ?? string.Empty,
        HorstmannRef = req.HorstmannRef ?? string.Empty,
        EstimatedMinutes = req.EstimatedMinutes ?? 45,
        OrderIndex = req.OrderIndex ?? 0
    };

    db.Lessons.Add(lesson);
    await db.SaveChangesAsync();

    return Results.Created($"/api/lessons/{lesson.Id}", lesson);
})
.WithName("CreateLesson");

app.MapPut("/api/lessons/{id:int}", async (int id, UpdateLessonRequest req, StudyTrackerContext db) =>
{
    var lesson = await db.Lessons.FindAsync(id);
    if (lesson == null) return Results.NotFound();

    if (!string.IsNullOrWhiteSpace(req.Title)) lesson.Title = req.Title;
    if (req.Description != null) lesson.Description = req.Description;
    if (req.ContentBody != null) lesson.ContentBody = req.ContentBody;
    if (req.HorstmannRef != null) lesson.HorstmannRef = req.HorstmannRef;
    if (req.EstimatedMinutes.HasValue) lesson.EstimatedMinutes = req.EstimatedMinutes.Value;
    if (req.IsCompleted.HasValue) lesson.IsCompleted = req.IsCompleted.Value;
    lesson.UpdatedAt = DateTime.UtcNow;

    await db.SaveChangesAsync();
    return Results.Ok(lesson);
})
.WithName("UpdateLesson");

app.MapPatch("/api/lessons/{id:int}/progress", async (int id, StudyTrackerContext db) =>
{
    var lesson = await db.Lessons.FindAsync(id);
    if (lesson == null) return Results.NotFound();

    lesson.IsCompleted = !lesson.IsCompleted;
    lesson.UpdatedAt = DateTime.UtcNow;
    await db.SaveChangesAsync();

    return Results.Ok(new ToggleProgressResponse(lesson.Id, lesson.IsCompleted, $"Lesson status toggled to {(lesson.IsCompleted ? "Completed" : "Pending")}"));
})
.WithName("ToggleLessonProgress");

// ==========================================
// 4. PROBLEMS ENDPOINTS
// ==========================================

app.MapGet("/api/problems/{id:int}", async (int id, StudyTrackerContext db) =>
{
    var p = await db.Problems.AsNoTracking().FirstOrDefaultAsync(x => x.Id == id);
    if (p == null) return Results.NotFound();

    var dto = new ProblemSummaryDto(
        p.Id,
        p.LessonId,
        p.Slug,
        p.Title,
        p.Difficulty,
        p.PackageName,
        p.TestClassName,
        p.ProblemStatement,
        p.RequirementsBody,
        p.WorkedExample,
        p.Hints,
        p.IsCompleted,
        p.OrderIndex
    );
    return Results.Ok(dto);
})
.WithName("GetProblemById");

app.MapPost("/api/problems", async (CreateProblemRequest req, StudyTrackerContext db) =>
{
    if (string.IsNullOrWhiteSpace(req.Title) || string.IsNullOrWhiteSpace(req.Slug))
    {
        return Results.BadRequest(new { message = "Title and Slug are required." });
    }

    var lessonExists = await db.Lessons.AnyAsync(l => l.Id == req.LessonId);
    if (!lessonExists)
    {
        return Results.BadRequest(new { message = "Invalid LessonId." });
    }

    var problem = new Problem
    {
        LessonId = req.LessonId,
        Slug = req.Slug.Trim().ToLowerInvariant(),
        Title = req.Title.Trim(),
        Difficulty = req.Difficulty ?? "Warm-up",
        PackageName = req.PackageName ?? string.Empty,
        TestClassName = req.TestClassName ?? string.Empty,
        ProblemStatement = req.ProblemStatement ?? string.Empty,
        RequirementsBody = req.RequirementsBody ?? string.Empty,
        WorkedExample = req.WorkedExample ?? string.Empty,
        Hints = req.Hints ?? string.Empty,
        OrderIndex = req.OrderIndex ?? 0
    };

    db.Problems.Add(problem);
    await db.SaveChangesAsync();

    return Results.Created($"/api/problems/{problem.Id}", problem);
})
.WithName("CreateProblem");

app.MapPatch("/api/problems/{id:int}/progress", async (int id, StudyTrackerContext db) =>
{
    var problem = await db.Problems.FindAsync(id);
    if (problem == null) return Results.NotFound();

    problem.IsCompleted = !problem.IsCompleted;
    problem.UpdatedAt = DateTime.UtcNow;
    await db.SaveChangesAsync();

    return Results.Ok(new ToggleProgressResponse(problem.Id, problem.IsCompleted, $"Problem status toggled to {(problem.IsCompleted ? "Completed" : "Pending")}"));
})
.WithName("ToggleProblemProgress");

app.Run();

// Helper Function
List<StudyTask> ParseMarkdownToTasks(string markdown)
{
    var tasks = new List<StudyTask>();
    if (string.IsNullOrWhiteSpace(markdown)) return tasks;

    var lines = markdown.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None);
    string currentModule = "General";

    var headerRegex = new Regex(@"^##\s+(.+)$");
    var taskRegex = new Regex(@"^- \[([ xX])\]\s+(.+)$");

    foreach (var rawLine in lines)
    {
        var line = rawLine.Trim();
        var headerMatch = headerRegex.Match(line);
        if (headerMatch.Success)
        {
            currentModule = headerMatch.Groups[1].Value.Trim();
            continue;
        }

        var taskMatch = taskRegex.Match(line);
        if (taskMatch.Success)
        {
            bool isCompleted = taskMatch.Groups[1].Value.Equals("x", StringComparison.OrdinalIgnoreCase);
            string title = taskMatch.Groups[2].Value.Trim();
            tasks.Add(new StudyTask
            {
                Title = title,
                IsCompleted = isCompleted,
                Module = currentModule
            });
        }
    }

    return tasks;
}

public record CreateVerticalRequest(string Name, string? Description);
public record IngestRequest(int? VerticalId, string? Name, string? Description, string MarkdownContent);
