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

    // Knowledge Atlas DbSets
    public DbSet<KnowledgeDomain> KnowledgeDomains { get; set; } = null!;
    public DbSet<KnowledgeConcept> KnowledgeConcepts { get; set; } = null!;
    public DbSet<DomainConceptConnection> DomainConceptConnections { get; set; } = null!;
    public DbSet<ConceptPrerequisite> ConceptPrerequisites { get; set; } = null!;
    public DbSet<ConceptRelation> ConceptRelations { get; set; } = null!;
    public DbSet<ConceptNextLesson> ConceptNextLessons { get; set; } = null!;

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

        // Knowledge Domains
        modelBuilder.Entity<KnowledgeDomain>()
            .HasIndex(d => d.Slug)
            .IsUnique();

        modelBuilder.Entity<KnowledgeDomain>()
            .HasIndex(d => d.Code)
            .IsUnique();

        // Knowledge Concepts
        modelBuilder.Entity<KnowledgeConcept>()
            .HasIndex(c => c.Slug)
            .IsUnique();

        // Domain-Concept Connections
        modelBuilder.Entity<DomainConceptConnection>()
            .HasIndex(dc => new { dc.DomainId, dc.ConceptId })
            .IsUnique();

        modelBuilder.Entity<DomainConceptConnection>()
            .HasOne(dc => dc.Domain)
            .WithMany(d => d.ConceptConnections)
            .HasForeignKey(dc => dc.DomainId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<DomainConceptConnection>()
            .HasOne(dc => dc.Concept)
            .WithMany(c => c.DomainConnections)
            .HasForeignKey(dc => dc.ConceptId)
            .OnDelete(DeleteBehavior.Cascade);

        // Concept Prerequisites
        modelBuilder.Entity<ConceptPrerequisite>()
            .HasIndex(cp => new { cp.ConceptId, cp.PrerequisiteConceptId })
            .IsUnique();

        modelBuilder.Entity<ConceptPrerequisite>()
            .HasOne(cp => cp.Concept)
            .WithMany(c => c.Prerequisites)
            .HasForeignKey(cp => cp.ConceptId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<ConceptPrerequisite>()
            .HasOne(cp => cp.PrerequisiteConcept)
            .WithMany(c => c.PrerequisiteFor)
            .HasForeignKey(cp => cp.PrerequisiteConceptId)
            .OnDelete(DeleteBehavior.Restrict);

        // Concept Relations
        modelBuilder.Entity<ConceptRelation>()
            .HasIndex(cr => new { cr.SourceConceptId, cr.TargetConceptId })
            .IsUnique();

        modelBuilder.Entity<ConceptRelation>()
            .HasOne(cr => cr.SourceConcept)
            .WithMany(c => c.OutgoingRelations)
            .HasForeignKey(cr => cr.SourceConceptId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<ConceptRelation>()
            .HasOne(cr => cr.TargetConcept)
            .WithMany(c => c.IncomingRelations)
            .HasForeignKey(cr => cr.TargetConceptId)
            .OnDelete(DeleteBehavior.Restrict);

        // Concept Next Lessons
        modelBuilder.Entity<ConceptNextLesson>()
            .HasIndex(cnl => cnl.ConceptId);

        modelBuilder.Entity<ConceptNextLesson>()
            .HasOne(cnl => cnl.Concept)
            .WithMany(c => c.NextLessons)
            .HasForeignKey(cnl => cnl.ConceptId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<ConceptNextLesson>()
            .HasOne(cnl => cnl.Lesson)
            .WithMany()
            .HasForeignKey(cnl => cnl.LessonId)
            .OnDelete(DeleteBehavior.SetNull);
    }
}
