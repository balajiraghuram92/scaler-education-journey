using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("problems")]
public class Problem
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
    [MaxLength(100)]
    [Column("slug")]
    public string Slug { get; set; } = string.Empty;

    [Required]
    [MaxLength(200)]
    [Column("title")]
    public string Title { get; set; } = string.Empty;

    [MaxLength(50)]
    [Column("difficulty")]
    public string Difficulty { get; set; } = "Warm-up";

    [MaxLength(100)]
    [Column("package_name")]
    public string PackageName { get; set; } = string.Empty;

    [MaxLength(100)]
    [Column("test_class_name")]
    public string TestClassName { get; set; } = string.Empty;

    [Column("problem_statement")]
    public string ProblemStatement { get; set; } = string.Empty;

    [Column("requirements_body")]
    public string RequirementsBody { get; set; } = string.Empty;

    [Column("worked_example")]
    public string WorkedExample { get; set; } = string.Empty;

    [Column("hints")]
    public string Hints { get; set; } = string.Empty;

    [Column("is_completed")]
    public bool IsCompleted { get; set; } = false;

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
