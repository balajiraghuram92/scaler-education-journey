using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_build_snapshot_locale_counts")]
public class BuildSnapshotLocaleCount
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("build_snapshot_id")]
    public int BuildSnapshotId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(BuildSnapshotId))]
    public BuildSnapshot? BuildSnapshot { get; set; }

    [Required]
    [MaxLength(20)]
    [Column("locale_code")]
    public string LocaleCode { get; set; } = string.Empty;

    [Column("approved_count")]
    public int ApprovedCount { get; set; }
}
