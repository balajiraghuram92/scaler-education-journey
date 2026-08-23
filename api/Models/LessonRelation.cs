using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("lesson_relations")]
public class LessonRelation
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Column("source_lesson_id")]
    public int SourceLessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(SourceLessonId))]
    public Lesson? SourceLesson { get; set; }

    [Column("target_lesson_id")]
    public int? TargetLessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(TargetLessonId))]
    public Lesson? TargetLesson { get; set; }

    [Required]
    [MaxLength(300)]
    [Column("target_title")]
    public string TargetTitle { get; set; } = string.Empty;

    [MaxLength(150)]
    [Column("target_slug")]
    public string? TargetSlug { get; set; }

    [Required]
    [MaxLength(32)]
    [Column("relationship_type")]
    public string RelationshipType { get; set; } = "Related"; // Prerequisite, Related, Next

    [Required]
    [MaxLength(32)]
    [Column("resolution_status")]
    public string ResolutionStatus { get; set; } = "Unresolved"; // Unresolved, Resolved, External

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
