using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_marketplace_bids")]
public class MarketplaceBid
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("marketplace_job_id")]
    public int MarketplaceJobId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(MarketplaceJobId))]
    public MarketplaceJob? MarketplaceJob { get; set; }

    [Column("vendor_id")]
    public int VendorId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(VendorId))]
    public Vendor? Vendor { get; set; }

    [Column("proposed_price", TypeName = "numeric(10,2)")]
    public decimal ProposedPrice { get; set; }

    [Required]
    [MaxLength(500)]
    [Column("note")]
    public string Note { get; set; } = string.Empty;

    [Required]
    [MaxLength(20)]
    [Column("status")]
    public string Status { get; set; } = "Pending";

    [Column("submitted_at")]
    public DateTime SubmittedAt { get; set; } = DateTime.UtcNow;
}
