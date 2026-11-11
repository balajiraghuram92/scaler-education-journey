using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;
using Microsoft.EntityFrameworkCore;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_translations")]
[Index(nameof(StringId), nameof(LocaleCode), IsUnique = true)]
public class LocalizationTranslation
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("string_id")]
    public int StringId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(StringId))]
    public LocalizationString? String { get; set; }

    [Required]
    [MaxLength(20)]
    [Column("locale_code")]
    public string LocaleCode { get; set; } = string.Empty;

    [Column("target_text")]
    public string? TargetText { get; set; }

    [Required]
    [MaxLength(20)]
    [Column("stage")]
    public string Stage { get; set; } = "New";

    [Required]
    [MaxLength(20)]
    [Column("translation_source")]
    public string TranslationSource { get; set; } = "Manual";

    [Column("qps_score")]
    public int? QpsScore { get; set; }

    [Column("raw_mt_text")]
    public string? RawMtText { get; set; }

    [Column("raw_mt_qps_score")]
    public int? RawMtQpsScore { get; set; }

    [Column("comet_kiwi_score", TypeName = "numeric(5,4)")]
    public decimal? CometKiwiScore { get; set; }

    [Column("needs_review")]
    public bool NeedsReview { get; set; } = false;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
