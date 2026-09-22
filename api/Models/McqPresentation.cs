using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("mcq_presentations")]
public class McqPresentation
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("question_id")]
    public int QuestionId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(QuestionId))]
    public McqQuestion? Question { get; set; }

    [Column("user_id")]
    public int? UserId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(UserId))]
    public AppUser? User { get; set; }

    [Required]
    [Column("displayed_option_order", TypeName = "jsonb")]
    public string DisplayedOptionOrder { get; set; } = "[]";

    [Column("question_text_shown")]
    public string? QuestionTextShown { get; set; }

    [Column("presented_at")]
    public DateTime PresentedAt { get; set; } = DateTime.UtcNow;

    public McqAttempt? Attempt { get; set; }
}
