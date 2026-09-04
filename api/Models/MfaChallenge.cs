using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("mfa_challenges")]
public class MfaChallenge
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
    [MaxLength(20)]
    [Column("purpose")]
    public string Purpose { get; set; } = "Login";

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("expires_at")]
    public DateTime ExpiresAt { get; set; } = DateTime.UtcNow.AddMinutes(5);

    [Column("consumed_at")]
    public DateTime? ConsumedAt { get; set; }

    [Column("failed_attempts")]
    public int FailedAttempts { get; set; } = 0;
}
