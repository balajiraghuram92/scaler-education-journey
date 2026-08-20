using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("lessons")]
public class Lesson
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("module_id")]
    public int ModuleId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ModuleId))]
    public CourseModule? Module { get; set; }

    [Required]
    [MaxLength(150)]
    [Column("slug")]
    public string Slug { get; set; } = string.Empty;

    [Required]
    [MaxLength(250)]
    [Column("title")]
    public string Title { get; set; } = string.Empty;

    [Column("description")]
    public string Description { get; set; } = string.Empty;

    [Column("lecture_number")]
    public int LectureNumber { get; set; }

    [MaxLength(50)]
    [Column("class_date")]
    public string ClassDate { get; set; } = string.Empty;

    [Column("content_body")]
    public string ContentBody { get; set; } = string.Empty;

    [Column("horstmann_ref")]
    public string HorstmannRef { get; set; } = string.Empty;

    [Column("estimated_minutes")]
    public int EstimatedMinutes { get; set; } = 45;

    [Column("is_completed")]
    public bool IsCompleted { get; set; } = false;

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    [MaxLength(50)]
    [Column("difficulty")]
    public string Difficulty { get; set; } = "Intermediate";

    public ICollection<Problem> Problems { get; set; } = new List<Problem>();
    public ICollection<LessonResource> Resources { get; set; } = new List<LessonResource>();
    public ICollection<LessonCodeComparison> CodeComparisons { get; set; } = new List<LessonCodeComparison>();
    public ICollection<LessonDiagram> Diagrams { get; set; } = new List<LessonDiagram>();
    public ICollection<LessonNote> Notes { get; set; } = new List<LessonNote>();
}
