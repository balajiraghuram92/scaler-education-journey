using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_workflow_steps")]
public class WorkflowStep
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("project_id")]
    public int ProjectId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ProjectId))]
    public LocalizationProject? Project { get; set; }

    [Column("order")]
    public int Order { get; set; }

    [Required]
    [MaxLength(50)]
    [Column("trigger")]
    public string Trigger { get; set; } = "On Manual Click";

    [Required]
    [MaxLength(50)]
    [Column("action")]
    public string Action { get; set; } = string.Empty;

    [MaxLength(200)]
    [Column("condition_expression")]
    public string? ConditionExpression { get; set; }

    [Column("last_run_at")]
    public DateTime? LastRunAt { get; set; }

    [MaxLength(200)]
    [Column("last_run_outcome")]
    public string? LastRunOutcome { get; set; }
}
