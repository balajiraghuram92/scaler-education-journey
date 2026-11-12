using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

// The table keeps its original name (localization_marketplace_jobs) and column
// names to avoid a table rename with its constraint renames.
[Table("localization_marketplace_jobs")]
public class TranslationJob
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
    [MaxLength(20)]
    [Column("status")]
    public string Status { get; set; } = "Assigned";

    [Column("string_count")]
    public int StringCount { get; set; }

    [Column("word_count")]
    public int WordCount { get; set; }

    [Column("awarded_vendor_id")]
    public int? VendorId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(VendorId))]
    public Vendor? Vendor { get; set; }

    [Column("posted_at")]
    public DateTime? CreatedAt { get; set; }

    [Column("submitted_at")]
    public DateTime? SubmittedAt { get; set; }

    [Column("approved_at")]
    public DateTime? ApprovedAt { get; set; }
}
