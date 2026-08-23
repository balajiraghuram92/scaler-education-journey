using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("lesson_concept_links")]
public class LessonConceptLink
{
    [Column("lesson_id")]
    public int LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    [Column("concept_id")]
    public int ConceptId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ConceptId))]
    public KnowledgeConcept? Concept { get; set; }

    [Required]
    [MaxLength(32)]
    [Column("relationship_type")]
    public string RelationshipType { get; set; } = "Related"; // Primary, Related, PrerequisiteContext

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
