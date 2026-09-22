using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("mcq_options")]
public class McqOption
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [Column("question_id")]
    public int QuestionId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(QuestionId))]
    public McqQuestion? Question { get; set; }

    [Required]
    [MaxLength(10)]
    [Column("option_key")]
    public string OptionKey { get; set; } = string.Empty;

    [Required]
    [Column("option_text")]
    public string OptionText { get; set; } = string.Empty;

    [Column("is_correct")]
    public bool IsCorrect { get; set; }
}
