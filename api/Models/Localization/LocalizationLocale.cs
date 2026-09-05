using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_locales")]
public class LocalizationLocale
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
    [MaxLength(100)]
    [Column("display_name")]
    public string DisplayName { get; set; } = string.Empty;
}
