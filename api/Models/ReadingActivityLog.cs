using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models;

[Table("reading_activity_logs")]
public class ReadingActivityLog
{
    public int Id { get; set; }
    public string DayLabel { get; set; } = string.Empty; // Mon, Tue, Wed, Thu, Fri, Sat, Sun
    public int ActivityCount { get; set; } = 0;
    public int OrderIndex { get; set; }
    public DateTime LogDate { get; set; } = DateTime.UtcNow;
}
