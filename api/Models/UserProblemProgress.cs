using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

/// <summary>
/// Per-learner state for one coding assignment (Problem). One row per (user, problem).
/// </summary>
[Table("user_problem_progress")]
public class UserProblemProgress
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Column("user_id")]
    public int UserId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(UserId))]
    public AppUser? User { get; set; }

    [Column("problem_id")]
    public int ProblemId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ProblemId))]
    public Problem? Problem { get; set; }

    // NotStarted | Attempted | Solved
    [Required]
    [MaxLength(20)]
    [Column("status")]
    public string Status { get; set; } = "Attempted";

    [Column("solution_revealed_at")]
    public DateTime? SolutionRevealedAt { get; set; }

    [Column("solved_at")]
    public DateTime? SolvedAt { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
