using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("mcq_attempts")]
public class McqAttempt
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("presentation_id")]
    public Guid PresentationId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(PresentationId))]
    public McqPresentation? Presentation { get; set; }

    [Required]
    [MaxLength(10)]
    [Column("selected_option_key")]
    public string SelectedOptionKey { get; set; } = string.Empty;

    [Column("is_correct")]
    public bool IsCorrect { get; set; }

    [Column("answered_at")]
    public DateTime AnsweredAt { get; set; } = DateTime.UtcNow;
}
