using System;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("Tasks")]
public class StudyTask
{
    [Column("Id")]
    public int Id { get; set; }

    [Column("VerticalId")]
    public int VerticalId { get; set; }

    [Column("Title")]
    public string Title { get; set; } = string.Empty;

    [Column("IsCompleted")]
    public bool IsCompleted { get; set; }

    [Column("Module")]
    public string Module { get; set; } = string.Empty;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    [JsonIgnore]
    public StudyVertical? Vertical { get; set; }

    [JsonIgnore]
    public StudyTaskContentLink? ContentLink { get; set; }
}
