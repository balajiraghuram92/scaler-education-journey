using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("courses")]
public class Course
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [MaxLength(100)]
    [Column("slug")]
    public string Slug { get; set; } = string.Empty;

    [Required]
    [MaxLength(200)]
    [Column("title")]
    public string Title { get; set; } = string.Empty;

    [Column("description")]
    public string Description { get; set; } = string.Empty;

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("vertical_id")]
    public int? VerticalId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(VerticalId))]
    public StudyVertical? Vertical { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<CourseModule> Modules { get; set; } = new List<CourseModule>();
}
