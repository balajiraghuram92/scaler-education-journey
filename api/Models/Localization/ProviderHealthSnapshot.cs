using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_provider_health")]
public class ProviderHealthSnapshot
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [MaxLength(30)]
    [Column("provider")]
    public string Provider { get; set; } = string.Empty;

    [Column("p50_latency_ms")]
    public int P50LatencyMs { get; set; }

    [Column("p99_latency_ms")]
    public int P99LatencyMs { get; set; }

    [Column("error_rate_percent", TypeName = "numeric(5,2)")]
    public decimal ErrorRatePercent { get; set; }

    [Required]
    [MaxLength(20)]
    [Column("circuit_state")]
    public string CircuitState { get; set; } = "Closed";

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
