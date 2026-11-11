using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_eval_golden_cases")]
public class EvalGoldenCase
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
    [Column("source_text")]
    public string SourceText { get; set; } = string.Empty;

    [Required]
    [Column("gold_translation")]
    public string GoldTranslation { get; set; } = string.Empty;

    [Required]
    [MaxLength(30)]
    [Column("category")]
    public string Category { get; set; } = string.Empty;

    [MaxLength(500)]
    [Column("notes")]
    public string? Notes { get; set; }

    [JsonIgnore]
    public ICollection<EvalCaseResult> CaseResults { get; set; } = new List<EvalCaseResult>();
}
