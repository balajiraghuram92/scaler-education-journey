using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_eval_runs")]
public class EvalRun
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
    [MaxLength(50)]
    [Column("pipeline_config")]
    public string PipelineConfig { get; set; } = string.Empty;

    [Column("run_at")]
    public DateTime RunAt { get; set; } = DateTime.UtcNow;

    [Column("avg_comet_kiwi", TypeName = "numeric(5,4)")]
    public decimal? AvgCometKiwi { get; set; }

    [Column("avg_qps_score", TypeName = "numeric(5,2)")]
    public decimal? AvgQpsScore { get; set; }

    [Column("glossary_adherence_rate", TypeName = "numeric(5,4)")]
    public decimal? GlossaryAdherenceRate { get; set; }

    [Column("placeholder_preservation_rate", TypeName = "numeric(5,4)")]
    public decimal? PlaceholderPreservationRate { get; set; }

    [Column("cache_hit_rate", TypeName = "numeric(5,4)")]
    public decimal? CacheHitRate { get; set; }

    [Column("avg_latency_ms")]
    public int? AvgLatencyMs { get; set; }

    [Column("total_cost_usd", TypeName = "numeric(12,6)")]
    public decimal? TotalCostUsd { get; set; }

    [JsonIgnore]
    public ICollection<EvalCaseResult> CaseResults { get; set; } = new List<EvalCaseResult>();
}
