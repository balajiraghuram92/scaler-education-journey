using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("lesson_code_comparisons")]
public class LessonCodeComparison
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

    [Column("description")]
    public string Description { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    [Column("before_label")]
    public string BeforeLabel { get; set; } = "Unstructured Concurrency";

    [Required]
    [MaxLength(50)]
    [Column("before_language")]
    public string BeforeLanguage { get; set; } = "java";

    [Column("before_code")]
    public string BeforeCode { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    [Column("after_label")]
    public string AfterLabel { get; set; } = "Structured Concurrency";

    [Required]
    [MaxLength(50)]
    [Column("after_language")]
    public string AfterLanguage { get; set; } = "java";

    [Column("after_code")]
    public string AfterCode { get; set; } = string.Empty;

    [Column("explanation")]
    public string Explanation { get; set; } = string.Empty;

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
