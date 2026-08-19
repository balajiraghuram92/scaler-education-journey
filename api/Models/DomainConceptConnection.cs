using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("domain_concept_connections")]
public class DomainConceptConnection
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("domain_id")]
    public int DomainId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(DomainId))]
    public KnowledgeDomain? Domain { get; set; }

    [Column("concept_id")]
    public int ConceptId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ConceptId))]
    public KnowledgeConcept? Concept { get; set; }

    [Column("is_primary")]
    public bool IsPrimary { get; set; } = false;

    [Column("relevance_weight")]
    public int RelevanceWeight { get; set; } = 5;

    [MaxLength(250)]
    [Column("role_description")]
    public string RoleDescription { get; set; } = string.Empty;

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;
}
