using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("learning_activity")]
public class LearningActivity
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Required]
    [MaxLength(40)]
    [Column("event_type")]
    public string EventType { get; set; } = string.Empty;

    [Column("occurred_at")]
    public DateTime OccurredAt { get; set; } = DateTime.UtcNow;

    [Column("lesson_id")]
    public int? LessonId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(LessonId))]
    public Lesson? Lesson { get; set; }

    [Column("problem_id")]
    public int? ProblemId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ProblemId))]
    public Problem? Problem { get; set; }

    [Column("task_id")]
    public int? TaskId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(TaskId))]
    public StudyTask? Task { get; set; }

    [Column("reading_map_item_id")]
    public int? ReadingMapItemId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ReadingMapItemId))]
    public ReadingMapItem? ReadingMapItem { get; set; }

    [Column("correlation_id")]
    public Guid CorrelationId { get; set; } = Guid.NewGuid();

    [Column("metadata", TypeName = "jsonb")]
    public string MetadataJson { get; set; } = "{}";
}
