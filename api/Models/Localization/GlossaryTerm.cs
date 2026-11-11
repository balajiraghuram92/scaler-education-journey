using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_glossary_terms")]
public class GlossaryTerm
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("project_id")]
    public int ProjectId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ProjectId))]
    public LocalizationProject? Project { get; set; }

    [Required]
    [MaxLength(20)]
    [Column("locale_code")]
    public string LocaleCode { get; set; } = string.Empty;

    [Required]
    [MaxLength(200)]
    [Column("source_term")]
    public string SourceTerm { get; set; } = string.Empty;

    [Required]
    [MaxLength(200)]
    [Column("target_term")]
    public string TargetTerm { get; set; } = string.Empty;

    [MaxLength(500)]
    [Column("notes")]
    public string? Notes { get; set; }
}
