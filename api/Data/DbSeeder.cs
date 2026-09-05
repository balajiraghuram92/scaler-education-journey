using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public static class DbSeeder
{
    public static void Initialize(StudyTrackerContext db)
    {
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

        // 6. Seed canonical FDE course/modules/lessons from the legacy FDE outline.
        // Task-to-lesson links remain a separate reconciliation step.
        FdeCurriculumSeedData.Seed(db);

        // 7. Seed Reading Map Items, Activity Timeline, and Knowledge Threads (Panel B)
        ReadingMapSeedData.Seed(db);

        // 8. Seed Concept Chapters, Code Comparisons, Diagrams & Notes (Panel D)
        ChapterSeedData.Seed(db);

        // 9. Seed Localization Lab (Phase 1, 2, 2.5, 3 Demo Data)
        LocalizationSeedData.Seed(db);

        // Save all changes
        db.SaveChanges();
        
        Console.WriteLine("Database seeding completed successfully.");
    }
}
