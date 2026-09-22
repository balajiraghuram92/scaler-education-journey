using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("mcq_questions")]
public class McqQuestion
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [Column("lesson_id")]
    public int LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    [MaxLength(120)]
    [Column("legacy_key")]
    public string? LegacyKey { get; set; }

    [Required]
    [Column("question_text")]
    public string QuestionText { get; set; } = string.Empty;

    [Required]
    [MaxLength(50)]
    [Column("source_type")]
    public string SourceType { get; set; } = "FROM_MATERIAL";

    [Required]
    [Column("explanation")]
    public string Explanation { get; set; } = string.Empty;

    [Column("is_active")]
    public bool IsActive { get; set; } = true;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<McqOption> Options { get; set; } = new List<McqOption>();

    [JsonIgnore]
    public ICollection<McqPresentation> Presentations { get; set; } = new List<McqPresentation>();
}
