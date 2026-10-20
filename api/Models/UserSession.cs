using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

/// <summary>
/// A signed-in browser/device. The short-lived access JWT (auth cookie) carries this
/// session's id in its "sid" claim; the long-lived refresh cookie is an opaque random
/// token whose SHA-256 hash is stored here and rotated on every refresh.
/// </summary>
[Table("user_sessions")]
public class UserSession
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Column("user_id")]
    public int UserId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(UserId))]
    public AppUser? User { get; set; }

    [Required]
    [MaxLength(64)]
    [Column("refresh_token_hash")]
    public string RefreshTokenHash { get; set; } = string.Empty;

    // The token that was current before the latest rotation. Presenting it inside the
    // grace window is a benign race between tabs; after it, it signals token theft.
    [MaxLength(64)]
    [Column("previous_refresh_token_hash")]
    public string? PreviousRefreshTokenHash { get; set; }

    [Column("rotated_at")]
    public DateTime? RotatedAt { get; set; }

    [Column("remember_me")]
    public bool RememberMe { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("last_seen_at")]
    public DateTime LastSeenAt { get; set; } = DateTime.UtcNow;

    // Hard upper bound on the session's lifetime, regardless of activity.
    [Column("expires_at")]
    public DateTime ExpiresAt { get; set; }

    [Column("revoked_at")]
    public DateTime? RevokedAt { get; set; }

    [MaxLength(40)]
    [Column("revoked_reason")]
    public string? RevokedReason { get; set; }

    [MaxLength(400)]
    [Column("user_agent")]
    public string? UserAgent { get; set; }

    [MaxLength(64)]
    [Column("ip_address")]
    public string? IpAddress { get; set; }

    [NotMapped]
    public bool IsActive => RevokedAt == null && ExpiresAt > DateTime.UtcNow;
}
