using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_projects")]
public class LocalizationProject
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [MaxLength(150)]
    [Column("slug")]
    public string Slug { get; set; } = string.Empty;

    [Required]
    [MaxLength(250)]
    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [Required]
    [MaxLength(20)]
    [Column("source_locale")]
    public string SourceLocale { get; set; } = "en-US";

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [JsonIgnore]
    public ICollection<LocalizationLocale> Locales { get; set; } = new List<LocalizationLocale>();

    [JsonIgnore]
    public ICollection<LocalizationString> Strings { get; set; } = new List<LocalizationString>();

    [JsonIgnore]
    public ICollection<WorkflowStep> WorkflowSteps { get; set; } = new List<WorkflowStep>();

    [JsonIgnore]
    public ICollection<BuildSnapshot> BuildSnapshots { get; set; } = new List<BuildSnapshot>();

    [JsonIgnore]
    public ICollection<MarketplaceJob> MarketplaceJobs { get; set; } = new List<MarketplaceJob>();

    [JsonIgnore]
    public ICollection<LedgerEntry> LedgerEntries { get; set; } = new List<LedgerEntry>();
}
