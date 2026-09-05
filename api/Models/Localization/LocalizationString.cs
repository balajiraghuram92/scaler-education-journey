using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_strings")]
public class LocalizationString
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("project_id")]
    public int ProjectId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ProjectId))]
    public LocalizationProject? Project { get; set; }

    [Required]
    [MaxLength(200)]
    [Column("key")]
    public string Key { get; set; } = string.Empty;

    [Required]
    [Column("source_text")]
    public string SourceText { get; set; } = string.Empty;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [JsonIgnore]
    public ICollection<LocalizationTranslation> Translations { get; set; } = new List<LocalizationTranslation>();
}
