using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models;

[Table("knowledge_concepts")]
public class KnowledgeConcept
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

    [Column("sub_label")]
    public string SubLabel { get; set; } = string.Empty;

    [Column("summary")]
    public string Summary { get; set; } = string.Empty;

    [Column("description")]
    public string Description { get; set; } = string.Empty;

    [MaxLength(50)]
    [Column("difficulty")]
    public string Difficulty { get; set; } = "Intermediate";

    [MaxLength(100)]
    [Column("icon")]
    public string Icon { get; set; } = "sparkles";

    [Column("estimated_hours")]
    public int EstimatedHours { get; set; } = 10;

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<DomainConceptConnection> DomainConnections { get; set; } = new List<DomainConceptConnection>();
    public ICollection<ConceptPrerequisite> Prerequisites { get; set; } = new List<ConceptPrerequisite>();
    public ICollection<ConceptPrerequisite> PrerequisiteFor { get; set; } = new List<ConceptPrerequisite>();
    public ICollection<ConceptRelation> OutgoingRelations { get; set; } = new List<ConceptRelation>();
    public ICollection<ConceptRelation> IncomingRelations { get; set; } = new List<ConceptRelation>();
    public ICollection<ConceptNextLesson> NextLessons { get; set; } = new List<ConceptNextLesson>();
}
