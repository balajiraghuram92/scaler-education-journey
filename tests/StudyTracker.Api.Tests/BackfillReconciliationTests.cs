using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services.Reconciliation;
using Xunit;

namespace StudyTracker.Api.Tests;

public class BackfillReconciliationTests
{
    private static StudyTrackerContext CreateInMemoryContext(string dbName)
    {
        var options = new DbContextOptionsBuilder<StudyTrackerContext>()
            .UseInMemoryDatabase(databaseName: dbName)
            .ConfigureWarnings(w => w.Ignore(Microsoft.EntityFrameworkCore.Diagnostics.InMemoryEventId.TransactionIgnoredWarning))
            .Options;
        return new StudyTrackerContext(options);
    }

    [Fact]
    public void FdeDeduplication_GroupsDuplicatesAccurately()
    {
        var tasks = new List<(int Id, string Module, string Title, bool Completed)>
        {
            (1, "Module 1", "Python Basics", true),
            (2, "Module 1", "Python Basics", false), // duplicate with completion conflict
            (3, "Module 2", "SQL Deep Dive", true)
        };

        var grouped = tasks.GroupBy(t => $"{NormalizationHelper.NormalizeText(t.Module)}::{NormalizationHelper.NormalizeText(t.Title)}").ToList();

        Assert.Equal(2, grouped.Count);
        var dupGroup = grouped.First(g => g.Count() > 1);
        Assert.Equal(2, dupGroup.Count());
        Assert.True(dupGroup.Any(x => x.Completed) && dupGroup.Any(x => !x.Completed));
    }

    [Fact]
    public void FdeCurriculumSeedData_CreatesCanonicalDraftsWithoutChoosingLegacyOwnership()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.Add(new StudyVertical
        {
            Id = 1,
            Name = "FDE Self-Study",
            Tasks = new List<StudyTask>
            {
                new()
                {
                    Id = 101,
                    Module = "1. FDE Foundations: Python, Workflow & Delivery",
                    Title = "Python Toolchain & Environment Setup (pyenv, uv, ruff, mypy)",
                    IsCompleted = true
                }
            }
        });
        db.SaveChanges();

        FdeCurriculumSeedData.Seed(db);

        var course = db.Courses.Single(c => c.Slug == "fde-curriculum");
        var lesson = db.Lessons.Single(l => l.Title == "Python Toolchain & Environment Setup (pyenv, uv, ruff, mypy)");

        Assert.Null(course.VerticalId);
        Assert.True(lesson.IsCompleted);
        Assert.Equal("Draft", lesson.ContentStatus);
        Assert.Contains("Why it matters in an FDE engagement", lesson.ContentBody);
        Assert.Empty(db.StudyTaskContentLinks);
    }

    [Fact]
    public void FdeCurriculumSeedData_CreatesSupplementalElectivesWithoutProgressFabrication()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.Add(new StudyVertical
        {
            Id = 1,
            Name = "FDE Self-Study",
            Tasks = new List<StudyTask>
            {
                new()
                {
                    Id = 101,
                    Module = "1. FDE Foundations: Python, Workflow & Delivery",
                    Title = "Python Toolchain & Environment Setup (pyenv, uv, ruff, mypy)",
                    IsCompleted = true
                }
            }
        });
        db.SaveChanges();

        FdeCurriculumSeedData.Seed(db);

        var course = db.Courses.Single(c => c.Slug == "fde-curriculum");
        var expectedModuleSlugs = new HashSet<string>(StringComparer.Ordinal)
        {
            "elective-containerization-orchestration",
            "elective-aws-multi-region-cloud-deep-dive",
            "elective-storage-networking-reliability"
        };
        var supplementalModules = db.Modules
            .Where(module => module.CourseId == course.Id && expectedModuleSlugs.Contains(module.Slug))
            .ToList();
        var supplementalModuleIds = supplementalModules.Select(module => module.Id).ToHashSet();
        var supplementalLessons = db.Lessons
            .Where(lesson => supplementalModuleIds.Contains(lesson.ModuleId))
            .ToList();

        Assert.True(expectedModuleSlugs.SetEquals(supplementalModules.Select(module => module.Slug)));
        Assert.Equal(3, supplementalModules.Count);
        Assert.Equal(48, supplementalLessons.Count);
        Assert.All(supplementalLessons, lesson => Assert.False(lesson.IsCompleted));
        Assert.Empty(db.StudyTaskContentLinks);
    }

    [Fact]
    public void JavaVerticalSeedData_AddsExpandedModulesAndIsIdempotent()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());

        JavaVerticalSeedData.Seed(db);

        var course = db.Courses.Single(c => c.Slug == "java-spring-lld");
        var expectedJavaModuleSlugs = new HashSet<string>(StringComparer.Ordinal)
        {
            "design-principles-patterns",
            "applied-machine-coding"
        };
        var expectedStandaloneModuleSlugs = new HashSet<string>(StringComparer.Ordinal)
        {
            "databases-sql",
            "high-level-design",
            "data-engineering"
        };
        var firstModuleCounts = db.Modules
            .Where(module => module.CourseId == course.Id && expectedJavaModuleSlugs.Contains(module.Slug))
            .ToDictionary(module => module.Slug, module => db.Lessons.Count(lesson => lesson.ModuleId == module.Id));
        var firstStandaloneCourseIds = db.Courses
            .Where(candidate => expectedStandaloneModuleSlugs.Contains(candidate.Slug))
            .Select(candidate => candidate.Id)
            .ToHashSet();
        var firstStandaloneModuleCounts = db.Modules
            .Where(module => firstStandaloneCourseIds.Contains(module.CourseId) && expectedStandaloneModuleSlugs.Contains(module.Slug))
            .ToDictionary(module => module.Slug, module => db.Lessons.Count(lesson => lesson.ModuleId == module.Id));
        var firstModuleTotal = db.Modules.Count(module => module.CourseId == course.Id);
        var firstLessonTotal = db.Lessons.Count(lesson => db.Modules
            .Where(module => module.CourseId == course.Id)
            .Select(module => module.Id)
            .Contains(lesson.ModuleId));

        Assert.True(expectedJavaModuleSlugs.SetEquals(firstModuleCounts.Keys));
        Assert.True(expectedStandaloneModuleSlugs.SetEquals(firstStandaloneModuleCounts.Keys));

        JavaVerticalSeedData.Seed(db);

        var secondModuleCounts = db.Modules
            .Where(module => module.CourseId == course.Id && expectedJavaModuleSlugs.Contains(module.Slug))
            .ToDictionary(module => module.Slug, module => db.Lessons.Count(lesson => lesson.ModuleId == module.Id));
        var secondStandaloneCourseIds = db.Courses
            .Where(candidate => expectedStandaloneModuleSlugs.Contains(candidate.Slug))
            .Select(candidate => candidate.Id)
            .ToHashSet();
        var secondStandaloneModuleCounts = db.Modules
            .Where(module => secondStandaloneCourseIds.Contains(module.CourseId) && expectedStandaloneModuleSlugs.Contains(module.Slug))
            .ToDictionary(module => module.Slug, module => db.Lessons.Count(lesson => lesson.ModuleId == module.Id));
        var secondModuleTotal = db.Modules.Count(module => module.CourseId == course.Id);
        var secondLessonTotal = db.Lessons.Count(lesson => db.Modules
            .Where(module => module.CourseId == course.Id)
            .Select(module => module.Id)
            .Contains(lesson.ModuleId));

        Assert.Equal(firstModuleCounts, secondModuleCounts);
        Assert.Equal(firstStandaloneModuleCounts, secondStandaloneModuleCounts);
        Assert.Equal(firstModuleTotal, secondModuleTotal);
        Assert.Equal(firstLessonTotal, secondLessonTotal);
    }

    [Fact]
    public void ThreadPathParsing_SplitsArrowSeparatorsCorrectly()
    {
        var rawPath = "Java → concurrency → virtual threads → structured concurrency";
        var segments = rawPath.Split(new[] { "→", "->", ">" }, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        Assert.Equal(4, segments.Length);
        Assert.Equal("Java", segments[0]);
        Assert.Equal("concurrency", segments[1]);
        Assert.Equal("virtual threads", segments[2]);
        Assert.Equal("structured concurrency", segments[3]);
    }

    [Fact]
    public async Task FdeReconciler_ExactMatch_ResolvesBothVerticals()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        var course = new Course
        {
            Id = 1,
            Slug = "fde-curriculum",
            Title = "FDE Course",
            Modules = new List<CourseModule>
            {
                new()
                {
                    Id = 1,
                    Slug = "mod-1",
                    Title = "Mod 1",
                    Lessons = new List<Lesson>
                    {
                        new() { Id = 10, Title = "Task A", Slug = "task-a", Problems = new List<Problem>() },
                        new() { Id = 11, Title = "Task B", Slug = "task-b", Problems = new List<Problem>() }
                    }
                }
            }
        };
        db.Courses.Add(course);
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "FDE Curriculum", Tasks = new List<StudyTask> { new() { Id = 101, Title = "Task A", Module = "Mod 1" } } },
            new StudyVertical { Id = 2, Name = "FDE Self-Study", Tasks = new List<StudyTask> { new() { Id = 102, Title = "Task B", Module = "Mod 2" } } }
        );
        await db.SaveChangesAsync();

        var reconciler = new FdeReconciler(db, NullLogger<FdeReconciler>.Instance);
        var report = await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.DryRun);

        Assert.Equal(0, report.ConflictCount);
        Assert.Equal(2, report.DiscoveredCount);
        Assert.Equal(2, report.VerifiedCount);
    }

    [Fact]
    public async Task FdeReconciler_UnmappedLegacyTask_IsProposedWithoutLinkOrFabrication()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "FDE Curriculum", Tasks = new List<StudyTask> { new() { Id = 101, Title = "Legacy Custom Task", Module = "Mod 1" } } },
            new StudyVertical { Id = 2, Name = "FDE Self-Study", Tasks = new List<StudyTask>() }
        );
        await db.SaveChangesAsync();

        var reconciler = new FdeReconciler(db, NullLogger<FdeReconciler>.Instance);
        var report = await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.Apply);

        Assert.Equal(1, report.ProposedCount);
        Assert.Equal(0, report.VerifiedCount);
        Assert.Empty(db.StudyTaskContentLinks);
        Assert.Empty(db.Lessons);
    }

    [Fact]
    public async Task FdeReconciler_AmbiguousTarget_RecordsConflictWithoutLink()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        var course = new Course
        {
            Id = 1,
            Slug = "fde-curriculum",
            Title = "FDE Course",
            Modules = new List<CourseModule>
            {
                new()
                {
                    Id = 1,
                    Slug = "mod-1",
                    Title = "Mod 1",
                    Lessons = new List<Lesson>
                    {
                        new() { Id = 10, Title = "Python Basics", Slug = "python-basics-1", Problems = new List<Problem>() },
                        new() { Id = 11, Title = "Python Basics", Slug = "python-basics-2", Problems = new List<Problem>() }
                    }
                }
            }
        };
        db.Courses.Add(course);
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "FDE Curriculum", Tasks = new List<StudyTask> { new() { Id = 101, Title = "Python Basics", Module = "Mod 1" } } },
            new StudyVertical { Id = 2, Name = "FDE Self-Study", Tasks = new List<StudyTask>() }
        );
        await db.SaveChangesAsync();

        var reconciler = new FdeReconciler(db, NullLogger<FdeReconciler>.Instance);
        var report = await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.Apply);

        Assert.Equal(1, report.ConflictCount);
        Assert.Empty(db.StudyTaskContentLinks);
    }

    [Fact]
    public async Task FdeReconciler_RepeatApplyRun_IsIdempotent()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        var course = new Course
        {
            Id = 1,
            Slug = "fde-curriculum",
            Title = "FDE Course",
            Modules = new List<CourseModule>
            {
                new()
                {
                    Id = 1,
                    Slug = "mod-1",
                    Title = "Mod 1",
                    Lessons = new List<Lesson>
                    {
                        new() { Id = 10, Title = "Task A", Slug = "task-a", Problems = new List<Problem>() }
                    }
                }
            }
        };
        db.Courses.Add(course);
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "FDE Curriculum", Tasks = new List<StudyTask> { new() { Id = 101, Title = "Task A", Module = "Mod 1" } } },
            new StudyVertical { Id = 2, Name = "FDE Self-Study", Tasks = new List<StudyTask>() }
        );
        await db.SaveChangesAsync();

        var reconciler = new FdeReconciler(db, NullLogger<FdeReconciler>.Instance);
        await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.Apply);

        var linksCount1 = await db.StudyTaskContentLinks.CountAsync();
        var auditsCount1 = await db.MigrationReconciliations.CountAsync();

        // Second run
        await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.Apply);

        var linksCount2 = await db.StudyTaskContentLinks.CountAsync();
        var auditsCount2 = await db.MigrationReconciliations.CountAsync();

        Assert.Equal(1, linksCount1);
        Assert.Equal(linksCount1, linksCount2);
        Assert.Equal(auditsCount1, auditsCount2);
    }

    [Fact]
    public async Task FdeReconciler_MissingVertical_RecordsMissingSourceConflict()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.Add(new StudyVertical { Id = 1, Name = "FDE Curriculum", Tasks = new List<StudyTask>() });
        await db.SaveChangesAsync();

        var reconciler = new FdeReconciler(db, NullLogger<FdeReconciler>.Instance);
        var report = await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.DryRun);

        Assert.True(report.ConflictCount > 0);
        Assert.Contains(report.AuditLog, log => log.Contains("Missing source conflict") && log.Contains("FDE Self-Study"));
    }

    [Fact]
    public async Task FdeReconciler_DuplicateVertical_RecordsAmbiguityConflict()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "FDE Curriculum" },
            new StudyVertical { Id = 2, Name = "FDE Curriculum" },
            new StudyVertical { Id = 3, Name = "FDE Self-Study" }
        );
        await db.SaveChangesAsync();

        var reconciler = new FdeReconciler(db, NullLogger<FdeReconciler>.Instance);
        var report = await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.DryRun);

        Assert.True(report.ConflictCount > 0);
        Assert.Contains(report.AuditLog, log => log.Contains("Ambiguity conflict") && log.Contains("Id: 1") && log.Contains("Id: 2"));
    }

    [Fact]
    public async Task FdeReconciler_SimilarCurriculumName_IsIgnoredWhenSelfStudyIsTheOnlyExactSource()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "FDE Curriculum Specialization" },
            new StudyVertical { Id = 2, Name = "FDE Self-Study" }
        );
        await db.SaveChangesAsync();

        var reconciler = new FdeReconciler(db, NullLogger<FdeReconciler>.Instance);
        var report = await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.DryRun);

        Assert.Equal(0, report.ConflictCount);
        Assert.Contains(report.AuditLog, log => log.Contains("Optional source vertical 'FDE Curriculum' was not found"));
    }

    [Fact]
    public async Task JavaReconciler_ReviewedLegacyTitle_MapsToCanonicalLessonSlug()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Courses.Add(new Course
        {
            Id = 1,
            Slug = "java-spring-lld",
            Title = "Java",
            Modules = new List<CourseModule>
            {
                new()
                {
                    Id = 1,
                    Slug = "oop-foundations",
                    Title = "OOP",
                    Lessons = new List<Lesson>
                    {
                        new() { Id = 10, Slug = "03-oop-2-access-modifiers-encapsulation", Title = "Canonical editorial title", Problems = new List<Problem>() }
                    }
                }
            }
        });
        db.Verticals.Add(new StudyVertical
        {
            Id = 2,
            Name = "Java & Spring Architecture",
            Tasks = new List<StudyTask>
            {
                new() { Id = 101, Module = "1. OOP & Design Foundations", Title = "Lesson 03: OOP-2 Access Modifiers, Encapsulation & Inheritance" }
            }
        });
        await db.SaveChangesAsync();

        var reconciler = new JavaReconciler(db, NullLogger<JavaReconciler>.Instance);
        var report = await reconciler.ReconcileJavaAsync(ReconciliationExecutionMode.DryRun);

        Assert.Equal(1, report.VerifiedCount);
        Assert.Equal(10, report.Mappings.Single().TargetLessonId);
    }

    [Fact]
    public async Task AzureLabsReconciler_ExactMatch_ResolvesBothVerticals()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        var azureCourse = new Course
        {
            Id = 1,
            Slug = "azure-certification",
            Title = "Azure",
            Modules = new List<CourseModule>
            {
                new()
                {
                    Id = 1,
                    Slug = "az",
                    Title = "Azure",
                    Lessons = new List<Lesson>
                    {
                        new() { Id = 20, Title = "AZ-900", Slug = "az-900", Problems = new List<Problem>() }
                    }
                }
            }
        };
        var labsCourse = new Course
        {
            Id = 2,
            Slug = "lab-projects",
            Title = "Labs",
            Modules = new List<CourseModule>
            {
                new()
                {
                    Id = 2,
                    Slug = "labs",
                    Title = "Labs",
                    Lessons = new List<Lesson>
                    {
                        new() { Id = 30, Title = "WMS Sandbox", Slug = "wms-sandbox", Problems = new List<Problem>() }
                    }
                }
            }
        };
        db.Courses.AddRange(azureCourse, labsCourse);
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "Azure Certifications", Tasks = new List<StudyTask> { new() { Id = 201, Title = "AZ-900", Module = "Azure" } } },
            new StudyVertical { Id = 2, Name = "Lab Projects", Tasks = new List<StudyTask> { new() { Id = 202, Title = "WMS Sandbox", Module = "Labs" } } }
        );
        await db.SaveChangesAsync();

        var reconciler = new AzureLabsReconciler(db, NullLogger<AzureLabsReconciler>.Instance);
        var report = await reconciler.ReconcileAzureAndLabsAsync(ReconciliationExecutionMode.DryRun);

        Assert.Equal(0, report.ConflictCount);
        Assert.Equal(2, report.DiscoveredCount);
        Assert.Equal(2, report.VerifiedCount);
    }

    [Fact]
    public async Task AzureLabsReconciler_UnmappedTask_IsProposedWithoutLinkOrFabrication()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "Azure Certifications", Tasks = new List<StudyTask> { new() { Id = 201, Title = "Custom Cloud Task", Module = "Azure" } } },
            new StudyVertical { Id = 2, Name = "Lab Projects", Tasks = new List<StudyTask>() }
        );
        await db.SaveChangesAsync();

        var reconciler = new AzureLabsReconciler(db, NullLogger<AzureLabsReconciler>.Instance);
        var report = await reconciler.ReconcileAzureAndLabsAsync(ReconciliationExecutionMode.Apply);

        Assert.Equal(1, report.ProposedCount);
        Assert.Equal(0, report.VerifiedCount);
        Assert.Empty(db.StudyTaskContentLinks);
        Assert.Empty(db.Lessons);
    }

    [Fact]
    public async Task AzureLabsReconciler_RepeatApplyRun_IsIdempotent()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        var azureCourse = new Course
        {
            Id = 1,
            Slug = "azure-certification",
            Title = "Azure",
            Modules = new List<CourseModule>
            {
                new()
                {
                    Id = 1,
                    Slug = "az",
                    Title = "Azure",
                    Lessons = new List<Lesson>
                    {
                        new() { Id = 20, Title = "AZ-900", Slug = "az-900", Problems = new List<Problem>() }
                    }
                }
            }
        };
        db.Courses.Add(azureCourse);
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "Azure Certifications", Tasks = new List<StudyTask> { new() { Id = 201, Title = "AZ-900", Module = "Azure" } } },
            new StudyVertical { Id = 2, Name = "Lab Projects", Tasks = new List<StudyTask>() }
        );
        await db.SaveChangesAsync();

        var reconciler = new AzureLabsReconciler(db, NullLogger<AzureLabsReconciler>.Instance);
        await reconciler.ReconcileAzureAndLabsAsync(ReconciliationExecutionMode.Apply);

        var links1 = await db.StudyTaskContentLinks.CountAsync();
        var audits1 = await db.MigrationReconciliations.CountAsync();

        // Second apply run
        await reconciler.ReconcileAzureAndLabsAsync(ReconciliationExecutionMode.Apply);

        var links2 = await db.StudyTaskContentLinks.CountAsync();
        var audits2 = await db.MigrationReconciliations.CountAsync();

        Assert.Equal(1, links1);
        Assert.Equal(links1, links2);
        Assert.Equal(audits1, audits2);
    }

    [Fact]
    public async Task AzureLabsReconciler_MissingVertical_RecordsConflict()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.Add(new StudyVertical { Id = 1, Name = "Lab Projects", Tasks = new List<StudyTask>() });
        await db.SaveChangesAsync();

        var reconciler = new AzureLabsReconciler(db, NullLogger<AzureLabsReconciler>.Instance);
        var report = await reconciler.ReconcileAzureAndLabsAsync(ReconciliationExecutionMode.DryRun);

        Assert.True(report.ConflictCount > 0);
        Assert.Contains(report.AuditLog, log => log.Contains("Missing source conflict") && log.Contains("Azure Certifications"));
    }

    [Fact]
    public async Task AzureLabsReconciler_DuplicateVertical_RecordsAmbiguityConflict()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "Azure Certifications" },
            new StudyVertical { Id = 10, Name = "Lab Projects" },
            new StudyVertical { Id = 11, Name = "Lab Projects" }
        );
        await db.SaveChangesAsync();

        var reconciler = new AzureLabsReconciler(db, NullLogger<AzureLabsReconciler>.Instance);
        var report = await reconciler.ReconcileAzureAndLabsAsync(ReconciliationExecutionMode.DryRun);

        Assert.True(report.ConflictCount > 0);
        Assert.Contains(report.AuditLog, log => log.Contains("Ambiguity conflict") && log.Contains("Id: 10") && log.Contains("Id: 11"));
    }

    [Fact]
    public async Task AzureLabsReconciler_SimilarName_DoesNotMatch()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "Azure Certification Tracks" },
            new StudyVertical { Id = 2, Name = "Lab Projects" }
        );
        await db.SaveChangesAsync();

        var reconciler = new AzureLabsReconciler(db, NullLogger<AzureLabsReconciler>.Instance);
        var report = await reconciler.ReconcileAzureAndLabsAsync(ReconciliationExecutionMode.DryRun);

        Assert.True(report.ConflictCount > 0);
        Assert.Contains(report.AuditLog, log => log.Contains("Missing source conflict") && log.Contains("Azure Certifications"));
    }

    [Fact]
    public async Task JavaReconciler_ExactMatch_ResolvesVertical()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        var course = new Course
        {
            Id = 1,
            Slug = "java-spring-lld",
            Title = "Java & Spring",
            Modules = new List<CourseModule>
            {
                new()
                {
                    Id = 1,
                    Slug = "mod-1",
                    Title = "Module 1",
                    Lessons = new List<Lesson>
                    {
                        new() { Id = 1, Title = "Virtual Threads", Slug = "virtual-threads", Problems = new List<Problem>() }
                    }
                }
            }
        };
        db.Courses.Add(course);
        db.Verticals.Add(new StudyVertical
        {
            Id = 1,
            Name = "Java & Spring Architecture",
            Tasks = new List<StudyTask>
            {
                new() { Id = 301, Title = "Virtual Threads", Module = "Module 1", IsCompleted = true }
            }
        });
        await db.SaveChangesAsync();

        var reconciler = new JavaReconciler(db, NullLogger<JavaReconciler>.Instance);
        var report = await reconciler.ReconcileJavaAsync(ReconciliationExecutionMode.DryRun);

        Assert.Equal(0, report.ConflictCount);
        Assert.Equal(1, report.DiscoveredCount);
        Assert.Equal(1, report.VerifiedCount);
    }

    [Fact]
    public async Task JavaReconciler_MissingVertical_RecordsConflict()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        var reconciler = new JavaReconciler(db, NullLogger<JavaReconciler>.Instance);
        var report = await reconciler.ReconcileJavaAsync(ReconciliationExecutionMode.DryRun);

        Assert.True(report.ConflictCount > 0);
        Assert.Contains(report.AuditLog, log => log.Contains("Missing source conflict") && log.Contains("Java & Spring Architecture"));
    }

    [Fact]
    public async Task JavaReconciler_DuplicateVertical_RecordsAmbiguityConflict()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.AddRange(
            new StudyVertical { Id = 20, Name = "Java & Spring Architecture" },
            new StudyVertical { Id = 21, Name = "Java & Spring Architecture" }
        );
        await db.SaveChangesAsync();

        var reconciler = new JavaReconciler(db, NullLogger<JavaReconciler>.Instance);
        var report = await reconciler.ReconcileJavaAsync(ReconciliationExecutionMode.DryRun);

        Assert.True(report.ConflictCount > 0);
        Assert.Contains(report.AuditLog, log => log.Contains("Ambiguity conflict") && log.Contains("Id: 20") && log.Contains("Id: 21"));
    }

    [Fact]
    public async Task JavaReconciler_SimilarName_DoesNotMatch()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.Add(new StudyVertical { Id = 1, Name = "Java & Spring" });
        await db.SaveChangesAsync();

        var reconciler = new JavaReconciler(db, NullLogger<JavaReconciler>.Instance);
        var report = await reconciler.ReconcileJavaAsync(ReconciliationExecutionMode.DryRun);

        Assert.True(report.ConflictCount > 0);
        Assert.Contains(report.AuditLog, log => log.Contains("Missing source conflict") && log.Contains("Java & Spring Architecture"));
    }

    [Fact]
    public async Task Reconcilers_DryRunMode_DoesNotMutateDatabase()
    {
        using var db = CreateInMemoryContext(Guid.NewGuid().ToString());
        db.Verticals.AddRange(
            new StudyVertical { Id = 1, Name = "FDE Curriculum", Tasks = new List<StudyTask> { new() { Id = 1, Title = "Task 1", Module = "Mod 1" } } },
            new StudyVertical { Id = 2, Name = "FDE Self-Study", Tasks = new List<StudyTask> { new() { Id = 2, Title = "Task 2", Module = "Mod 2" } } }
        );
        await db.SaveChangesAsync();

        var reconciler = new FdeReconciler(db, NullLogger<FdeReconciler>.Instance);
        await reconciler.ReconcileFdeAsync(ReconciliationExecutionMode.DryRun);

        Assert.Empty(db.Courses);
        Assert.Empty(db.StudyTaskContentLinks);
    }
}
