using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("Verticals")]
public class StudyVertical
{
    [Column("Id")]
    public int Id { get; set; }

    [Column("Name")]
    public string Name { get; set; } = string.Empty;

    [Column("Description")]
    public string Description { get; set; } = string.Empty;

    [Column("canonical_vertical_id")]
    public int? CanonicalVerticalId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(CanonicalVerticalId))]
    public StudyVertical? CanonicalVertical { get; set; }

    [JsonIgnore]
    public ICollection<StudyVertical> Aliases { get; set; } = new List<StudyVertical>();

    [Column("archived_at")]
    public DateTime? ArchivedAt { get; set; }

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<StudyTask> Tasks { get; set; } = new List<StudyTask>();

    [NotMapped]
    public string LayoutMode
    {
        get => Tasks != null && Tasks.Any(t => !string.IsNullOrEmpty(t.Module) && t.Module != "General") ? "Modular" : "Flat";
        set { }
    }
}
