using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_usage_events")]
public class LocalizationUsageEvent
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("project_id")]
    public int ProjectId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ProjectId))]
    public LocalizationProject? Project { get; set; }

    [Column("workflow_step_id")]
    public int? WorkflowStepId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(WorkflowStepId))]
    public WorkflowStep? WorkflowStep { get; set; }

    [Required]
    [MaxLength(30)]
    [Column("meter")]
    public string Meter { get; set; } = string.Empty;

    [Required]
    [MaxLength(30)]
    [Column("operation")]
    public string Operation { get; set; } = string.Empty;

    [MaxLength(20)]
    [Column("locale_code")]
    public string? LocaleCode { get; set; }

    [Column("units")]
    public int Units { get; set; }

    [Column("units_out")]
    public int? UnitsOut { get; set; }

    [Column("cache_hit")]
    public bool CacheHit { get; set; }

    [Column("succeeded")]
    public bool Succeeded { get; set; }

    [Column("cost_usd", TypeName = "numeric(12,6)")]
    public decimal CostUsd { get; set; }

    [Column("occurred_at")]
    public DateTime OccurredAt { get; set; } = DateTime.UtcNow;
}
