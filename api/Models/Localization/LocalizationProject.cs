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

    [Column("qps_threshold")]
    public int QpsThreshold { get; set; } = 4;

    [Required]
    [MaxLength(100)]
    [Column("client_alias")]
    public string ClientAlias { get; set; } = string.Empty;

    [Column("ai_enabled")]
    public bool AiEnabled { get; set; } = true;

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
    public ICollection<TranslationJob> TranslationJobs { get; set; } = new List<TranslationJob>();

    [JsonIgnore]
    public ICollection<GlossaryTerm> GlossaryTerms { get; set; } = new List<GlossaryTerm>();

    [JsonIgnore]
    public ICollection<TranslationCacheEntry> TranslationCacheEntries { get; set; } = new List<TranslationCacheEntry>();

    [JsonIgnore]
    public ICollection<EvalGoldenCase> EvalGoldenCases { get; set; } = new List<EvalGoldenCase>();

    [JsonIgnore]
    public ICollection<EvalRun> EvalRuns { get; set; } = new List<EvalRun>();
}
