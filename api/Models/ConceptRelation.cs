using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("concept_relations")]
public class ConceptRelation
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("source_concept_id")]
    public int SourceConceptId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(SourceConceptId))]
    public KnowledgeConcept? SourceConcept { get; set; }

    [Column("target_concept_id")]
    public int TargetConceptId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(TargetConceptId))]
    public KnowledgeConcept? TargetConcept { get; set; }

    [MaxLength(50)]
    [Column("relationship_type")]
    public string RelationshipType { get; set; } = "Related";
}
