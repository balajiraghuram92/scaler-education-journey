using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("knowledge_thread_steps")]
public class KnowledgeThreadStep
{
    [Column("thread_id")]
    public int ThreadId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ThreadId))]
    public KnowledgeThread? Thread { get; set; }

    [Column("order_index")]
    public int OrderIndex { get; set; }

    [Column("concept_id")]
    public int? ConceptId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ConceptId))]
    public KnowledgeConcept? Concept { get; set; }

    [Column("lesson_id")]
    public int? LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    [Required]
    [MaxLength(250)]
    [Column("label")]
    public string Label { get; set; } = string.Empty;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
