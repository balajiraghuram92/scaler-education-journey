using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

/// <summary>
/// The learner's latest code for a live exercise, so the editor restores it on any device.
/// One row per (user, exercise). Files are stored as JSON: [{ "path": ..., "content": ... }].
/// </summary>
[Table("user_exercise_drafts")]
public class UserExerciseDraft
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Column("user_id")]
    public int UserId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(UserId))]
    public AppUser? User { get; set; }

    [Required]
    [MaxLength(120)]
    [Column("exercise_id")]
    public string ExerciseId { get; set; } = string.Empty;

    [Column("files", TypeName = "jsonb")]
    public string FilesJson { get; set; } = "[]";

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// One run of a live exercise against the hidden tests: what was submitted and how it scored.
/// Kept as history so progress (and an AI tutor) can see how a solution evolved.
/// </summary>
[Table("user_exercise_attempts")]
public class UserExerciseAttempt
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Column("user_id")]
    public int UserId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(UserId))]
    public AppUser? User { get; set; }

    [Required]
    [MaxLength(120)]
    [Column("exercise_id")]
    public string ExerciseId { get; set; } = string.Empty;

    // success | testFailure | compilationFailure | timeout
    [Required]
    [MaxLength(30)]
    [Column("status")]
    public string Status { get; set; } = string.Empty;

    [Column("tests_total")]
    public int TestsTotal { get; set; }

    [Column("tests_passed")]
    public int TestsPassed { get; set; }

    [Column("duration_ms")]
    public long DurationMilliseconds { get; set; }

    [Column("files", TypeName = "jsonb")]
    public string FilesJson { get; set; } = "[]";

    // Failing check labels / first lines of diagnostics, for quick review.
    [Column("summary", TypeName = "jsonb")]
    public string SummaryJson { get; set; } = "{}";

    [Column("submitted_at")]
    public DateTime SubmittedAt { get; set; } = DateTime.UtcNow;
}
