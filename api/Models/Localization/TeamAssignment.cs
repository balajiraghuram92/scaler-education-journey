using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models.Localization;

[Table("localization_team_assignments")]
public class TeamAssignment
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("agreement_id")]
    public int AgreementId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(AgreementId))]
    public ServiceAgreement? Agreement { get; set; }

    [Column("vendor_id")]
    public int VendorId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(VendorId))]
    public Vendor? Vendor { get; set; }

    [Required]
    [MaxLength(20)]
    [Column("locale_code")]
    public string LocaleCode { get; set; } = string.Empty;

    [Column("member_count")]
    public int MemberCount { get; set; }
}
