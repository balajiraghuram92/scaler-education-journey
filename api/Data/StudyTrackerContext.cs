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

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<StudyVertical>()
            .HasIndex(v => v.Name)
            .IsUnique();

        modelBuilder.Entity<StudyTask>()
            .HasOne(t => t.Vertical)
            .WithMany(v => v.Tasks)
            .HasForeignKey(t => t.VerticalId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
