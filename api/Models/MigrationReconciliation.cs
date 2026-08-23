using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models;

[Table("migration_reconciliation")]
public class MigrationReconciliation
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Required]
    [MaxLength(100)]
    [Column("migration_key")]
    public string MigrationKey { get; set; } = string.Empty;

    [Required]
    [MaxLength(50)]
    [Column("source_type")]
    public string SourceType { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    [Column("source_id")]
    public string SourceId { get; set; } = string.Empty;

    [MaxLength(50)]
    [Column("target_type")]
    public string? TargetType { get; set; }

    [MaxLength(100)]
    [Column("target_id")]
    public string? TargetId { get; set; }

    [Required]
    [MaxLength(64)]
    [Column("source_checksum")]
    public string SourceChecksum { get; set; } = string.Empty;

    [Required]
    [MaxLength(32)]
    [Column("status")]
    public string Status { get; set; } = "Discovered"; // Discovered, Mapped, Applied, Verified, Conflict, Skipped

    [MaxLength(100)]
    [Column("issue_code")]
    public string? IssueCode { get; set; }

    [Column("details", TypeName = "jsonb")]
    public string DetailsJson { get; set; } = "{}";

    [Column("applied_at")]
    public DateTime? AppliedAt { get; set; }

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
