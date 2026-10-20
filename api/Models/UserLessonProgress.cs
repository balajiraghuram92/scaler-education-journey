using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

/// <summary>
/// Per-learner reading state for one lesson. One row per (user, lesson).
/// Also the source of truth an AI tutor reads to know what a learner has studied.
/// </summary>
[Table("user_lesson_progress")]
public class UserLessonProgress
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Column("user_id")]
    public int UserId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(UserId))]
    public AppUser? User { get; set; }

    [Column("lesson_id")]
    public int LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    // InProgress | Completed
    [Required]
    [MaxLength(20)]
    [Column("status")]
    public string Status { get; set; } = "InProgress";

    [Column("first_opened_at")]
    public DateTime FirstOpenedAt { get; set; } = DateTime.UtcNow;

    [Column("last_opened_at")]
    public DateTime LastOpenedAt { get; set; } = DateTime.UtcNow;

    [Column("completed_at")]
    public DateTime? CompletedAt { get; set; }

    // The heading anchor the learner was last reading, used to resume in place.
    [MaxLength(160)]
    [Column("last_section_id")]
    public string? LastSectionId { get; set; }

    [Column("scroll_percent")]
    public int ScrollPercent { get; set; }

    [Column("visit_count")]
    public int VisitCount { get; set; } = 1;

    [Column("time_spent_seconds")]
    public int TimeSpentSeconds { get; set; }

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    [NotMapped]
    public bool IsCompleted => Status == "Completed";
}
