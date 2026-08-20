using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public static class DbSeeder
{
    public static void Initialize(StudyTrackerContext db)
    {
        // Ensure database exists and schema is created
        // We use Migrate instead of EnsureCreated to support future migrations
        try
        {
            db.Database.Migrate();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Migration warning: {ex.Message}");
        }

        // Resilient DDL safeguard for Reading Map tables
        db.Database.ExecuteSqlRaw(@"
            CREATE TABLE IF NOT EXISTS reading_map_items (
                ""Id"" SERIAL PRIMARY KEY,
                ""Category"" TEXT NOT NULL,
                ""Title"" TEXT NOT NULL,
                ""SubText"" TEXT,
                ""OrderIndex"" INT NOT NULL DEFAULT 0,
                ""IsCompleted"" BOOLEAN NOT NULL DEFAULT FALSE,
                ""CreatedAt"" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                ""UpdatedAt"" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS reading_activity_logs (
                ""Id"" SERIAL PRIMARY KEY,
                ""DayLabel"" TEXT NOT NULL,
                ""ActivityCount"" INT NOT NULL DEFAULT 0,
                ""OrderIndex"" INT NOT NULL DEFAULT 0,
                ""LogDate"" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS knowledge_threads (
                ""Id"" SERIAL PRIMARY KEY,
                ""Domain"" TEXT NOT NULL,
                ""RawPath"" TEXT NOT NULL,
                ""OrderIndex"" INT NOT NULL DEFAULT 0
            );
        ");

        // 1. Seed Lab Projects
        if (!db.Verticals.Any(v => v.Name == "Lab Projects"))
        {
            var labs = new StudyVertical { Name = "Lab Projects", Description = "Rebuild, Break, Narrate" };
            labs.Tasks.Add(new StudyTask { Title = "Rebuild Lab A — WMS Defect Detection", IsCompleted = false, Module = "Lab Projects" });
            labs.Tasks.Add(new StudyTask { Title = "Rebuild Lab B — Unity Localization Platform", IsCompleted = false, Module = "Lab Projects" });
            db.Verticals.Add(labs);
        }

        // 2. Seed Azure Certifications
        if (!db.Verticals.Any(v => v.Name == "Azure Certifications"))
        {
            var azure = new StudyVertical { Name = "Azure Certifications", Description = "Cloud Architecture and AI" };
            azure.Tasks.Add(new StudyTask { Title = "AI-103 (Apps & Agents) Study & Lab Prep", IsCompleted = false, Module = "Azure Certifications" });
            azure.Tasks.Add(new StudyTask { Title = "AI-200 (Cloud Developer) Practice Exams", IsCompleted = false, Module = "Azure Certifications" });
            db.Verticals.Add(azure);
        }

        // 3. Seed or Update FDE Self-Study
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

        // 4. Seed Java & Spring Architecture Vertical and Courses
        JavaVerticalSeedData.Seed(db);

        // 5. Seed Knowledge Atlas Domains, Concepts, and Synapses
        KnowledgeAtlasSeedData.Seed(db);

        // 6. Seed Reading Map Items, Activity Timeline, and Knowledge Threads (Panel B)
        ReadingMapSeedData.Seed(db);

        // Save all changes
        db.SaveChanges();
        
        Console.WriteLine("Database seeding completed successfully.");
    }
}
