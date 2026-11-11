using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_eval_case_results")]
public class EvalCaseResult
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("eval_run_id")]
    public int EvalRunId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(EvalRunId))]
    public EvalRun? EvalRun { get; set; }

    [Column("eval_golden_case_id")]
    public int EvalGoldenCaseId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(EvalGoldenCaseId))]
    public EvalGoldenCase? EvalGoldenCase { get; set; }

    [Required]
    [Column("produced_translation")]
    public string ProducedTranslation { get; set; } = string.Empty;

    [Column("comet_kiwi_score", TypeName = "numeric(5,4)")]
    public decimal? CometKiwiScore { get; set; }

    [Column("qps_score")]
    public int? QpsScore { get; set; }

    [Column("glossary_adherence_ok")]
    public bool? GlossaryAdherenceOk { get; set; }

    [Column("placeholder_preserved_ok")]
    public bool? PlaceholderPreservedOk { get; set; }

    [Column("latency_ms")]
    public int? LatencyMs { get; set; }

    [Column("cache_hit")]
    public bool? CacheHit { get; set; }

    [Column("cost_usd", TypeName = "numeric(12,6)")]
    public decimal? CostUsd { get; set; }
}
