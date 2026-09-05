using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_marketplace_jobs")]
public class MarketplaceJob
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
    [MaxLength(20)]
    [Column("status")]
    public string Status { get; set; } = "Draft";

    [Column("string_count")]
    public int StringCount { get; set; }

    [Column("word_count")]
    public int WordCount { get; set; }

    [Column("suggested_price_low", TypeName = "numeric(10,2)")]
    public decimal SuggestedPriceLow { get; set; }

    [Column("suggested_price_high", TypeName = "numeric(10,2)")]
    public decimal SuggestedPriceHigh { get; set; }

    [Column("awarded_vendor_id")]
    public int? AwardedVendorId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(AwardedVendorId))]
    public Vendor? AwardedVendor { get; set; }

    [Column("posted_at")]
    public DateTime? PostedAt { get; set; }

    [Column("awarded_at")]
    public DateTime? AwardedAt { get; set; }

    [Column("submitted_at")]
    public DateTime? SubmittedAt { get; set; }

    [Column("approved_at")]
    public DateTime? ApprovedAt { get; set; }

    [JsonIgnore]
    public ICollection<MarketplaceBid> Bids { get; set; } = new List<MarketplaceBid>();
}
