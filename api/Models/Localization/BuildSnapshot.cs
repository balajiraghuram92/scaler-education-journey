using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_build_snapshots")]
public class BuildSnapshot
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
    [Column("snapshot_identifier")]
    public string SnapshotIdentifier { get; set; } = string.Empty;

    [Required]
    [MaxLength(50)]
    [Column("source_revision")]
    public string SourceRevision { get; set; } = string.Empty;

    [Required]
    [MaxLength(50)]
    [Column("localization_revision")]
    public string LocalizationRevision { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    [Column("config")]
    public string Config { get; set; } = "Production-Default";

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [JsonIgnore]
    public ICollection<BuildSnapshotLocaleCount> LocaleCounts { get; set; } = new List<BuildSnapshotLocaleCount>();
}
