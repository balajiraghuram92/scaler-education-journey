using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_translation_cache_entries")]
public class TranslationCacheEntry
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
    [MaxLength(20)]
    [Column("locale_code")]
    public string LocaleCode { get; set; } = string.Empty;

    [Required]
    [Column("source_text")]
    public string SourceText { get; set; } = string.Empty;

    // The source_embedding pgvector column (vector(384) with an HNSW cosine
    // index) is declared in the migration with raw SQL. It is intentionally
    // unmapped here: the Python localization-ai service is the only reader
    // and writer of that column.
    [NotMapped]
    public float[]? SourceEmbedding { get; set; }

    [Required]
    [Column("cached_translation")]
    public string CachedTranslation { get; set; } = string.Empty;

    [Column("hit_count")]
    public int HitCount { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("last_hit_at")]
    public DateTime? LastHitAt { get; set; }
}
