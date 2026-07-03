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

    bool needsRecreate = false;
    try
    {
        needsRecreate = !db.Tasks.Any(t => t.Module != "");
    }
    catch
    {
        needsRecreate = true;
    }

    if (needsRecreate)
    {
        db.Database.EnsureDeleted();
        db.Database.EnsureCreated();
    }
    else
    {
        db.Database.EnsureCreated();
    }

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

    // Seed FDE Self-Study from markdown file
    if (!db.Verticals.Any(v => v.Name == "FDE Self-Study"))
    {
        var fde = new StudyVertical { Name = "FDE Self-Study", Description = "Agentic AI Track" };
        var fdeTasks = ParseFdeTasks();
        foreach (var task in fdeTasks)
        {
            fde.Tasks.Add(task);
        }
        db.Verticals.Add(fde);
    }

    db.SaveChanges();
}

// Markdown parser for FDE curriculum tasks
List<StudyTask> ParseFdeTasks()
{
    var tasks = new List<StudyTask>();
    var dir = AppContext.BaseDirectory;
    string fullPath = "";
    while (!string.IsNullOrEmpty(dir))
    {
        var tempPath = Path.Combine(dir, "info", "04-fde-curriculum-tracker.md");
        if (File.Exists(tempPath))
        {
            fullPath = tempPath;
            break;
        }
        var parent = Directory.GetParent(dir);
        dir = parent?.FullName;
    }

    if (string.IsNullOrEmpty(fullPath) || !File.Exists(fullPath))
    {
        return tasks;
    }

    var lines = File.ReadAllLines(fullPath);
    var headerPattern = new Regex(@"^##\s+(.+)$");
    var taskPattern = new Regex(@"^- \[([ xX])\]\s+(.+)$");

    string currentModule = "General";

    foreach (var line in lines)
    {
        var trimmed = line.Trim();
        var headerMatch = headerPattern.Match(trimmed);
        if (headerMatch.Success)
        {
            currentModule = headerMatch.Groups[1].Value.Trim();
            continue;
        }

        var taskMatch = taskPattern.Match(trimmed);
        if (taskMatch.Success)
        {
            var statusChar = taskMatch.Groups[1].Value;
            var isCompleted = statusChar.ToLower() == "x";
            var title = taskMatch.Groups[2].Value.Trim();

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

app.MapGet("/", () => "StudyTracker API is running. Use /swagger for API docs.");

// API Endpoints
app.MapGet("/api/verticals", async (StudyTrackerContext db) =>
    await db.Verticals.Include(v => v.Tasks).ToListAsync())
    .WithName("GetVerticals");

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
