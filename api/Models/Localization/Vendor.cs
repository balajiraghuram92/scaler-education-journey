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

    [Column("rating", TypeName = "numeric(3,1)")]
    public decimal Rating { get; set; }

    [JsonIgnore]
    public ICollection<MarketplaceJob> AwardedJobs { get; set; } = new List<MarketplaceJob>();

    [JsonIgnore]
    public ICollection<MarketplaceBid> Bids { get; set; } = new List<MarketplaceBid>();
}
