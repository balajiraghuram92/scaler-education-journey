using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_ledger_entries")]
public class LedgerEntry
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
    [Column("source")]
    public string Source { get; set; } = string.Empty;

    [Column("amount", TypeName = "numeric(10,2)")]
    public decimal Amount { get; set; }

    [Column("units_consumed")]
    public int? UnitsConsumed { get; set; }

    [MaxLength(20)]
    [Column("unit_type")]
    public string? UnitType { get; set; }

    [Column("real_cost_usd", TypeName = "numeric(12,6)")]
    public decimal? RealCostUsd { get; set; }

    [Column("related_marketplace_job_id")]
    public int? RelatedMarketplaceJobId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(RelatedMarketplaceJobId))]
    public TranslationJob? RelatedMarketplaceJob { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
