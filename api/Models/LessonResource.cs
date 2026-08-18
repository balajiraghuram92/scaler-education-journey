using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("lesson_resources")]
public class LessonResource
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
    [MaxLength(50)]
    [Column("resource_type")]
    public string ResourceType { get; set; } = "StudyGuideTopic"; // StudyGuideTopic, HackMdPre, HackMdPost, PdfNotes, HorstmannRef

    [Required]
    [MaxLength(250)]
    [Column("title")]
    public string Title { get; set; } = string.Empty;

    [Column("content_body")]
    public string ContentBody { get; set; } = string.Empty;

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
