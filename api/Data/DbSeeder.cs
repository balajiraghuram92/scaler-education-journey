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

        // Resilient DDL safeguard for Lessons columns and Chapter tables
        db.Database.ExecuteSqlRaw(@"
            ALTER TABLE lessons ADD COLUMN IF NOT EXISTS difficulty VARCHAR(50) DEFAULT 'Intermediate';
            ALTER TABLE lessons ADD COLUMN IF NOT EXISTS content_body TEXT DEFAULT '';
            ALTER TABLE lessons ADD COLUMN IF NOT EXISTS horstmann_ref VARCHAR(255) DEFAULT '';
            ALTER TABLE lessons ADD COLUMN IF NOT EXISTS class_date VARCHAR(50) DEFAULT '';
            ALTER TABLE lessons ADD COLUMN IF NOT EXISTS estimated_minutes INT DEFAULT 45;

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

            -- Clean drop of newly added empty chapter tables if casing was mismatched
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'lesson_code_comparisons' AND column_name = 'LessonId'
                ) THEN
                    DROP TABLE IF EXISTS lesson_notes CASCADE;
                    DROP TABLE IF EXISTS lesson_diagrams CASCADE;
                    DROP TABLE IF EXISTS lesson_code_comparisons CASCADE;
                END IF;
            END $$;

            CREATE TABLE IF NOT EXISTS lesson_code_comparisons (
                id SERIAL PRIMARY KEY,
                lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                before_label VARCHAR(100) NOT NULL,
                before_language VARCHAR(50) NOT NULL,
                before_code TEXT NOT NULL,
                after_label VARCHAR(100) NOT NULL,
                after_language VARCHAR(50) NOT NULL,
                after_code TEXT NOT NULL,
                explanation TEXT,
                order_index INT NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS lesson_diagrams (
                id SERIAL PRIMARY KEY,
                lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                caption VARCHAR(300),
                diagram_type VARCHAR(50) NOT NULL DEFAULT 'svg-inline',
                svg_content TEXT NOT NULL,
                diagram_spec_json TEXT,
                order_index INT NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS lesson_notes (
                id SERIAL PRIMARY KEY,
                lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                note_type VARCHAR(50) NOT NULL DEFAULT 'FieldNote',
                anchor_section VARCHAR(150),
                title VARCHAR(250) NOT NULL,
                content_body TEXT NOT NULL,
                order_index INT NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
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

        // 7. Seed Concept Chapters, Code Comparisons, Diagrams & Notes (Panel D)
        ChapterSeedData.Seed(db);

        // Save all changes
        db.SaveChanges();
        
        Console.WriteLine("Database seeding completed successfully.");
    }
}
