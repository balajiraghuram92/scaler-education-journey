using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_provider_rates")]
public class LocalizationProviderRate
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [MaxLength(30)]
    [Column("meter")]
    public string Meter { get; set; } = string.Empty;

    [Required]
    [MaxLength(20)]
    [Column("unit_kind")]
    public string UnitKind { get; set; } = string.Empty;

    [Column("usd_per_million", TypeName = "numeric(12,6)")]
    public decimal UsdPerMillion { get; set; }

    [Column("valid_from")]
    public DateTime ValidFrom { get; set; } = DateTime.UtcNow;
}
