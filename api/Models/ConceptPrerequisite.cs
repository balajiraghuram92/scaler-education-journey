using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("concept_prerequisites")]
public class ConceptPrerequisite
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("concept_id")]
    public int ConceptId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ConceptId))]
    public KnowledgeConcept? Concept { get; set; }

    [Column("prerequisite_concept_id")]
    public int PrerequisiteConceptId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(PrerequisiteConceptId))]
    public KnowledgeConcept? PrerequisiteConcept { get; set; }

    [MaxLength(50)]
    [Column("status")]
    public string Status { get; set; } = "included";
}
