using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using System.Text.RegularExpressions;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddDbContext<StudyTrackerContext>(options =>
{
    var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") 
        ?? "Data Source=studytracker.db";
    options.UseSqlServer(connectionString);
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
        policy.WithOrigins("http://localhost:5173")
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

// Apply migrations and seed data
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<StudyTrackerContext>();

    db.Database.EnsureCreated();

    // Seed Lab Projects
    if (!db.Verticals.Any(v => v.Name == "Lab Projects"))
    {
        var labs = new StudyVertical { Name = "Lab Projects", Description = "Rebuild, Break, Narrate" };
        labs.Tasks.Add(new StudyTask { Title = "Rebuild Lab A — WMS Defect Detection", IsCompleted = false, Module = "Lab Projects" });
        labs.Tasks.Add(new StudyTask { Title = "Rebuild Lab B — Unity Localization Platform", IsCompleted = false, Module = "Lab Projects" });
        db.Verticals.Add(labs);
    }

    // Seed Azure Certifications
    if (!db.Verticals.Any(v => v.Name == "Azure Certifications"))
    {
        var azure = new StudyVertical { Name = "Azure Certifications", Description = "Cloud Architecture and AI" };
        azure.Tasks.Add(new StudyTask { Title = "AI-103 (Apps & Agents) Study & Lab Prep", IsCompleted = false, Module = "Azure Certifications" });
        azure.Tasks.Add(new StudyTask { Title = "AI-200 (Cloud Developer) Practice Exams", IsCompleted = false, Module = "Azure Certifications" });
        db.Verticals.Add(azure);
    }

    // Seed or Update FDE Self-Study
    var fde = db.Verticals.Include(v => v.Tasks).FirstOrDefault(v => v.Name == "FDE Self-Study");
    if (fde == null)
    {
        fde = new StudyVertical { Name = "FDE Self-Study", Description = "Agentic AI Track" };
        db.Verticals.Add(fde);
    }

    if (fde.Tasks.Count == 0)
    {
        var fdeTasks = FdeSeedData.GetTasks();
        foreach (var task in fdeTasks)
        {
            fde.Tasks.Add(task);
        }
    }

    db.SaveChanges();
}

app.MapGet("/", () => "StudyTracker API is running. Use /swagger for API docs.");

// API Endpoints
app.MapGet("/api/verticals", async (StudyTrackerContext db) =>
    await db.Verticals.Include(v => v.Tasks).ToListAsync())
    .WithName("GetVerticals");

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

app.MapPut("/api/tasks/{id}/toggle", async (int id, StudyTrackerContext db) =>
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

app.Run();

// Helper Function & DTOs
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

