using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public class StudyTrackerContext : DbContext
{
    public StudyTrackerContext(DbContextOptions<StudyTrackerContext> options)
        : base(options)
    {
    }

    public DbSet<StudyVertical> Verticals { get; set; } = null!;
    public DbSet<StudyTask> Tasks { get; set; } = null!;
    public DbSet<Course> Courses { get; set; } = null!;
    public DbSet<CourseModule> Modules { get; set; } = null!;
    public DbSet<Lesson> Lessons { get; set; } = null!;
    public DbSet<Problem> Problems { get; set; } = null!;
    public DbSet<LessonResource> LessonResources { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Verticals & Tasks
        modelBuilder.Entity<StudyVertical>()
            .HasIndex(v => v.Name)
            .IsUnique();

        modelBuilder.Entity<StudyTask>()
            .HasOne(t => t.Vertical)
            .WithMany(v => v.Tasks)
            .HasForeignKey(t => t.VerticalId)
            .OnDelete(DeleteBehavior.Cascade);

        // Courses
        modelBuilder.Entity<Course>()
            .HasIndex(c => c.Slug)
            .IsUnique();

        // Course Modules
        modelBuilder.Entity<CourseModule>()
            .HasIndex(m => new { m.CourseId, m.Slug })
            .IsUnique();

        modelBuilder.Entity<CourseModule>()
            .HasOne(m => m.Course)
            .WithMany(c => c.Modules)
            .HasForeignKey(m => m.CourseId)
            .OnDelete(DeleteBehavior.Cascade);

        // Lessons
        modelBuilder.Entity<Lesson>()
            .HasIndex(l => new { l.ModuleId, l.Slug })
            .IsUnique();

        modelBuilder.Entity<Lesson>()
            .HasOne(l => l.Module)
            .WithMany(m => m.Lessons)
            .HasForeignKey(l => l.ModuleId)
            .OnDelete(DeleteBehavior.Cascade);

        // Problems
        modelBuilder.Entity<Problem>()
            .HasIndex(p => new { p.LessonId, p.Slug })
            .IsUnique();

        modelBuilder.Entity<Problem>()
            .HasOne(p => p.Lesson)
            .WithMany(l => l.Problems)
            .HasForeignKey(p => p.LessonId)
            .OnDelete(DeleteBehavior.Cascade);

        // Lesson Resources
        modelBuilder.Entity<LessonResource>()
            .HasIndex(r => r.LessonId);

        modelBuilder.Entity<LessonResource>()
            .HasOne(r => r.Lesson)
            .WithMany(l => l.Resources)
            .HasForeignKey(r => r.LessonId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
