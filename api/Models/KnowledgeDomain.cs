using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models;

[Table("knowledge_domains")]
public class KnowledgeDomain
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
    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [Required]
    [MaxLength(50)]
    [Column("code")]
    public string Code { get; set; } = string.Empty;

    [Column("description")]
    public string Description { get; set; } = string.Empty;

    [MaxLength(100)]
    [Column("icon")]
    public string Icon { get; set; } = "layers";

    [MaxLength(50)]
    [Column("color_hex")]
    public string ColorHex { get; set; } = "#3B82F6";

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<DomainConceptConnection> ConceptConnections { get; set; } = new List<DomainConceptConnection>();
}
