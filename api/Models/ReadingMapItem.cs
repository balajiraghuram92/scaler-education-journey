using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models;

[Table("reading_map_items")]
public class ReadingMapItem
{
    public int Id { get; set; }
    public string Category { get; set; } = string.Empty; // ReadThisWeek, Revisited, Deferred, Lists, Prerequisites
    public string Title { get; set; } = string.Empty;
    public string? SubText { get; set; }
    public int OrderIndex { get; set; }
    public bool IsCompleted { get; set; } = false;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
