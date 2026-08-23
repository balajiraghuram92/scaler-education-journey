using System;
using System.Collections.Generic;

namespace StudyTracker.Api.Services.Reconciliation;

public enum ReconciliationExecutionMode
{
    DryRun,
    Apply,
    Verify
}

public class ReconciliationOptions
{
    public string Scope { get; set; } = "all"; // java, fde, azure, labs, atlas, reading-map, knowledge-threads, all
    public ReconciliationExecutionMode Mode { get; set; } = ReconciliationExecutionMode.DryRun;
}

public class MappingCandidate
{
    public int LegacyTaskId { get; set; }
    public string LegacyTitle { get; set; } = string.Empty;
    public string LegacyModule { get; set; } = string.Empty;
    public bool LegacyIsCompleted { get; set; }
    public int? TargetLessonId { get; set; }
    public int? TargetProblemId { get; set; }
    public string TargetTitle { get; set; } = string.Empty;
    public string MappingType { get; set; } = "TitleAndModule"; // Exact, TitleAndModule, Manual, DuplicateAlias
    public string MappingStatus { get; set; } = "Proposed"; // Proposed, Verified, Rejected, Conflict
    public decimal Confidence { get; set; } = 1.0000m;
    public string SourceChecksum { get; set; } = string.Empty;
    public string? IssueCode { get; set; }
    public string? Note { get; set; }
}

public class ReconciliationReport
{
    public string Scope { get; set; } = string.Empty;
    public ReconciliationExecutionMode Mode { get; set; }
    public DateTime ExecutedAt { get; set; } = DateTime.UtcNow;
    public int DiscoveredCount { get; set; }
    public int ExactMappedCount { get; set; }
    public int ProposedCount { get; set; }
    public int VerifiedCount { get; set; }
    public int ConflictCount { get; set; }
    public int SkippedCount { get; set; }
    public List<MappingCandidate> Mappings { get; set; } = new();
    public List<string> AuditLog { get; set; } = new();
}
