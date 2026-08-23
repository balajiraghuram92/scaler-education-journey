using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("reading_map_items")]
public class ReadingMapItem
{
    [Column("Id")]
    public int Id { get; set; }

    [Column("Category")]
    public string Category { get; set; } = string.Empty; // ReadThisWeek, Revisited, Deferred, Lists, Prerequisites

    [Column("Title")]
    public string Title { get; set; } = string.Empty;

    [Column("SubText")]
    public string? SubText { get; set; }

    [Column("OrderIndex")]
    public int OrderIndex { get; set; }

    [Column("IsCompleted")]
    public bool IsCompleted { get; set; } = false;

    [Column("CreatedAt")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("UpdatedAt")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    [Column("lesson_id")]
    public int? LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    [Column("task_id")]
    public int? TaskId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(TaskId))]
    public StudyTask? Task { get; set; }

    [MaxLength(32)]
    [Column("status")]
    public string Status { get; set; } = "Planned"; // Planned, Reading, Completed, Revisited, Deferred, Archived

    [Column("scheduled_for")]
    public DateOnly? ScheduledFor { get; set; }

    [Column("priority")]
    public int Priority { get; set; } = 0;

    [Column("is_seeded")]
    public bool IsSeeded { get; set; } = false;

    [Column("archived_at")]
    public DateTime? ArchivedAt { get; set; }
}
