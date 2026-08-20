using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("lesson_diagrams")]
public class LessonDiagram
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("lesson_id")]
    public int LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    [Required]
    [MaxLength(200)]
    [Column("title")]
    public string Title { get; set; } = string.Empty;

    [MaxLength(300)]
    [Column("caption")]
    public string Caption { get; set; } = string.Empty;

    [MaxLength(50)]
    [Column("diagram_type")]
    public string DiagramType { get; set; } = "svg-inline";

    [Column("svg_content")]
    public string SvgContent { get; set; } = string.Empty;

    [Column("diagram_spec_json")]
    public string? DiagramSpecJson { get; set; }

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
