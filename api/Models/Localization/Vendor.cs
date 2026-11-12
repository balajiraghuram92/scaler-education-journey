using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_vendors")]
public class Vendor
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [MaxLength(150)]
    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [Required]
    [MaxLength(200)]
    [Column("languages")]
    public string Languages { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    [Column("alias")]
    public string Alias { get; set; } = string.Empty;

    [JsonIgnore]
    public ICollection<TranslationJob> Jobs { get; set; } = new List<TranslationJob>();
}
