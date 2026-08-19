using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("concept_next_lessons")]
public class ConceptNextLesson
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("concept_id")]
    public int ConceptId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ConceptId))]
    public KnowledgeConcept? Concept { get; set; }

    [Required]
    [MaxLength(300)]
    [Column("lesson_title")]
    public string LessonTitle { get; set; } = string.Empty;

    [MaxLength(200)]
    [Column("module_name")]
    public string ModuleName { get; set; } = string.Empty;

    [MaxLength(150)]
    [Column("lesson_slug")]
    public string LessonSlug { get; set; } = string.Empty;

    [Column("lesson_id")]
    public int? LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;
}
