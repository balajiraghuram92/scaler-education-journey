using System;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("course_domain_links")]
public class CourseDomainLink
{
    [Column("course_id")]
    public int CourseId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(CourseId))]
    public Course? Course { get; set; }

    [Column("domain_id")]
    public int DomainId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(DomainId))]
    public KnowledgeDomain? Domain { get; set; }

    [Column("is_primary")]
    public bool IsPrimary { get; set; } = false;

    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
