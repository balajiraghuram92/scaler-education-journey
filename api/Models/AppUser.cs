using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("app_users")]
public class AppUser
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [MaxLength(320)]
    [Column("email")]
    public string Email { get; set; } = string.Empty;

    [Required]
    [Column("password_hash")]
    public string PasswordHash { get; set; } = string.Empty;

    [Required]
    [Column("password_salt")]
    public string PasswordSalt { get; set; } = string.Empty;

    [Column("password_iterations")]
    public int PasswordIterations { get; set; } = 210_000;

    [Required]
    [MaxLength(20)]
    [Column("role")]
    public string Role { get; set; } = "User";

    [Required]
    [MaxLength(30)]
    [Column("status")]
    public string Status { get; set; } = "PendingApproval";

    [MaxLength(120)]
    [Column("display_name")]
    public string? DisplayName { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("decided_at")]
    public DateTime? DecidedAt { get; set; }

    [Column("decided_by_user_id")]
    public int? DecidedByUserId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(DecidedByUserId))]
    public AppUser? DecidedByUser { get; set; }

    [Column("last_login_at")]
    public DateTime? LastLoginAt { get; set; }

    [Column("totp_secret_encrypted")]
    public string? TotpSecretEncrypted { get; set; }

    [Column("totp_enabled")]
    public bool TotpEnabled { get; set; } = false;

    [Column("last_accepted_totp_counter")]
    public long? LastAcceptedTotpCounter { get; set; }
}
