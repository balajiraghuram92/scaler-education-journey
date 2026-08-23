using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("study_task_content_links")]
public class StudyTaskContentLink
{
    [Key]
    [Column("task_id")]
    public int TaskId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(TaskId))]
    public StudyTask? Task { get; set; }

    [Column("lesson_id")]
    public int? LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    [Column("problem_id")]
    public int? ProblemId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ProblemId))]
    public Problem? Problem { get; set; }

    [Required]
    [MaxLength(32)]
    [Column("mapping_type")]
    public string MappingType { get; set; } = "TitleAndModule"; // Exact, TitleAndModule, Manual, DuplicateAlias

    [Required]
    [MaxLength(32)]
    [Column("mapping_status")]
    public string MappingStatus { get; set; } = "Proposed"; // Proposed, Verified, Rejected

    [Column("confidence", TypeName = "numeric(5,4)")]
    public decimal Confidence { get; set; } = 1.0000m;

    [Required]
    [MaxLength(64)]
    [Column("source_checksum")]
    public string SourceChecksum { get; set; } = string.Empty;

    [Column("verified_at")]
    public DateTime? VerifiedAt { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
