using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services.Reconciliation;

public class FdeReconciler
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<FdeReconciler> _logger;

    public FdeReconciler(StudyTrackerContext db, ILogger<FdeReconciler> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<ReconciliationReport> ReconcileFdeAsync(ReconciliationExecutionMode mode)
    {
        var report = new ReconciliationReport
        {
            Scope = "fde",
            Mode = mode,
            ExecutedAt = DateTime.UtcNow
        };

        report.AuditLog.Add("Starting FDE track reconciliation (FDE Curriculum vs FDE Self-Study)...");

        // 1. Strict Vertical Matching with normalized exact matching (No numeric IDs, Contains, or FirstOrDefault)
        var allVerticals = await _db.Verticals.Include(v => v.Tasks).ToListAsync();

        var curriculumNormalized = NormalizationHelper.NormalizeText("FDE Curriculum");
        var curriculumCandidates = allVerticals
            .Where(v => NormalizationHelper.NormalizeText(v.Name) == curriculumNormalized)
            .ToList();

        var selfStudyNormalized = NormalizationHelper.NormalizeText("FDE Self-Study");
        var selfStudyCandidates = allVerticals
            .Where(v => NormalizationHelper.NormalizeText(v.Name) == selfStudyNormalized)
            .ToList();

        StudyVertical? fdeCurriculum = null;
        if (curriculumCandidates.Count == 0)
        {
            report.ConflictCount++;
            report.AuditLog.Add("Missing source conflict: Required source vertical 'FDE Curriculum' was not found.");
        }
        else if (curriculumCandidates.Count > 1)
        {
            report.ConflictCount++;
            var candidateDetails = string.Join(", ", curriculumCandidates.Select(c => $"[Id: {c.Id}, Name: '{c.Name}']"));
            report.AuditLog.Add($"Ambiguity conflict: Expected exactly 1 vertical for 'FDE Curriculum', found {curriculumCandidates.Count} candidates: {candidateDetails}.");
        }
        else
        {
            fdeCurriculum = curriculumCandidates[0];
        }

        StudyVertical? fdeSelfStudy = null;
        if (selfStudyCandidates.Count == 0)
        {
            report.ConflictCount++;
            report.AuditLog.Add("Missing source conflict: Required source vertical 'FDE Self-Study' was not found.");
        }
        else if (selfStudyCandidates.Count > 1)
        {
            report.ConflictCount++;
            var candidateDetails = string.Join(", ", selfStudyCandidates.Select(c => $"[Id: {c.Id}, Name: '{c.Name}']"));
            report.AuditLog.Add($"Ambiguity conflict: Expected exactly 1 vertical for 'FDE Self-Study', found {selfStudyCandidates.Count} candidates: {candidateDetails}.");
        }
        else
        {
            fdeSelfStudy = selfStudyCandidates[0];
        }

        if (fdeCurriculum == null || fdeSelfStudy == null)
        {
            report.AuditLog.Add("Reconciliation stopped: One or more required FDE source verticals could not be uniquely resolved.");
            return report;
        }

        var allFdeTasks = new List<StudyTask>();
        allFdeTasks.AddRange(fdeCurriculum.Tasks);
        allFdeTasks.AddRange(fdeSelfStudy.Tasks);

        report.DiscoveredCount = allFdeTasks.Count;
        report.AuditLog.Add($"Discovered {allFdeTasks.Count} total FDE legacy tasks across 'FDE Curriculum' (Id: {fdeCurriculum.Id}) and 'FDE Self-Study' (Id: {fdeSelfStudy.Id}).");

        // 2. Fetch pre-existing canonical Course, Modules, Lessons, Problems for FDE (Do not fabricate new ones)
        var fdeCourseCandidates = await _db.Courses
            .Include(c => c.Modules)
                .ThenInclude(m => m.Lessons)
                    .ThenInclude(l => l.Problems)
            .Where(c => c.Slug == "fde-curriculum")
            .ToListAsync();

        var allCanonicalLessons = fdeCourseCandidates.Count == 1
            ? fdeCourseCandidates[0].Modules.SelectMany(m => m.Lessons).ToList()
            : new List<Lesson>();
        var allCanonicalProblems = allCanonicalLessons.SelectMany(l => l.Problems).ToList();

        // 3. Classify each legacy task against canonical targets and identify duplicate/completion conflicts
        var groupedByNormalized = allFdeTasks.GroupBy(t => $"{NormalizationHelper.NormalizeText(t.Module)}::{NormalizationHelper.NormalizeText(t.Title)}");

        foreach (var group in groupedByNormalized)
        {
            var taskList = group.ToList();
            var hasDuplicateAcrossVerticals = taskList.Count > 1;
            var hasCompletionConflict = taskList.Any(t => t.IsCompleted) && taskList.Any(t => !t.IsCompleted);

            foreach (var t in taskList)
            {
                var normalizedTitle = NormalizationHelper.NormalizeText(t.Title);
                var rawSignature = $"{t.Id}|{t.Module}|{t.Title}|{t.IsCompleted}";
                var checksum = NormalizationHelper.ComputeSha256Checksum(rawSignature);

                var candidate = new MappingCandidate
                {
                    LegacyTaskId = t.Id,
                    LegacyTitle = t.Title,
                    LegacyModule = t.Module,
                    LegacyIsCompleted = t.IsCompleted,
                    SourceChecksum = checksum
                };

                if (hasCompletionConflict)
                {
                    candidate.MappingType = "DuplicateAlias";
                    candidate.MappingStatus = "Conflict";
                    candidate.Confidence = 0.5000m;
                    candidate.IssueCode = "FDE_COMPLETION_MISMATCH";
                    candidate.Note = $"Completion state conflict across FDE duplicate tasks ({taskList.Count} occurrences)";
                    report.ConflictCount++;
                }
                else
                {
                    // Check against pre-existing canonical problems and lessons
                    var matchingProblems = allCanonicalProblems.Where(p => NormalizationHelper.NormalizeText(p.Title) == normalizedTitle).ToList();
                    var matchingLessons = allCanonicalLessons.Where(l => NormalizationHelper.NormalizeText(l.Title) == normalizedTitle).ToList();

                    var totalMatches = matchingProblems.Count + matchingLessons.Count;

                    if (totalMatches == 0)
                    {
                        candidate.MappingType = "Manual";
                        candidate.MappingStatus = "Proposed";
                        candidate.Confidence = 0.6000m;
                        candidate.IssueCode = "UNMAPPED_LEGACY_TASK";
                        candidate.Note = "No pre-existing canonical lesson or problem found in curriculum. Retained as proposed outline item without fabricating database entities.";
                        report.ProposedCount++;
                    }
                    else if (totalMatches > 1)
                    {
                        candidate.MappingType = "Ambiguous";
                        candidate.MappingStatus = "Conflict";
                        candidate.Confidence = 0.5000m;
                        candidate.IssueCode = "AMBIGUOUS_CANONICAL_TARGET";
                        candidate.Note = $"Ambiguous target match: found {matchingLessons.Count} lessons and {matchingProblems.Count} problems matching title '{t.Title}'.";
                        report.ConflictCount++;
                    }
                    else if (matchingProblems.Count == 1)
                    {
                        var problem = matchingProblems[0];
                        candidate.TargetProblemId = problem.Id;
                        candidate.TargetTitle = problem.Title;
                        candidate.MappingType = hasDuplicateAcrossVerticals ? "DuplicateAlias" : "Exact";
                        candidate.MappingStatus = "Verified";
                        candidate.Confidence = 1.0000m;
                        candidate.Note = $"Deterministically mapped to canonical Problem (Id: {problem.Id}).";
                        report.ExactMappedCount++;
                        report.VerifiedCount++;
                    }
                    else // matchingLessons.Count == 1
                    {
                        var lesson = matchingLessons[0];
                        candidate.TargetLessonId = lesson.Id;
                        candidate.TargetTitle = lesson.Title;
                        candidate.MappingType = hasDuplicateAcrossVerticals ? "DuplicateAlias" : "TitleAndModule";
                        candidate.MappingStatus = "Verified";
                        candidate.Confidence = 0.9500m;
                        candidate.Note = $"Deterministically mapped to canonical Lesson (Id: {lesson.Id}).";
                        report.ExactMappedCount++;
                        report.VerifiedCount++;
                    }
                }

                report.Mappings.Add(candidate);
            }
        }

        // 4. Apply mode creates StudyTaskContentLink ONLY for Verified mappings and audits in MigrationReconciliation
        if (mode == ReconciliationExecutionMode.Apply)
        {
            using var tx = await _db.Database.BeginTransactionAsync();
            try
            {
                // Soft link aliases on StudyVertical if uniquely resolved
                if (fdeSelfStudy.CanonicalVerticalId == null)
                {
                    fdeSelfStudy.CanonicalVerticalId = fdeCurriculum.Id;
                    fdeSelfStudy.UpdatedAt = DateTime.UtcNow;
                }

                foreach (var candidate in report.Mappings)
                {
                    // Create or update StudyTaskContentLink ONLY for Verified mappings
                    if (candidate.MappingStatus == "Verified")
                    {
                        var link = await _db.StudyTaskContentLinks.FindAsync(candidate.LegacyTaskId);
                        if (link == null)
                        {
                            link = new StudyTaskContentLink
                            {
                                TaskId = candidate.LegacyTaskId,
                                LessonId = candidate.TargetLessonId,
                                ProblemId = candidate.TargetProblemId,
                                MappingType = candidate.MappingType,
                                MappingStatus = "Verified",
                                Confidence = candidate.Confidence,
                                SourceChecksum = candidate.SourceChecksum,
                                VerifiedAt = DateTime.UtcNow,
                                CreatedAt = DateTime.UtcNow,
                                UpdatedAt = DateTime.UtcNow
                            };
                            _db.StudyTaskContentLinks.Add(link);
                        }
                        else
                        {
                            link.LessonId = candidate.TargetLessonId;
                            link.ProblemId = candidate.TargetProblemId;
                            link.MappingType = candidate.MappingType;
                            link.MappingStatus = "Verified";
                            link.Confidence = candidate.Confidence;
                            link.SourceChecksum = candidate.SourceChecksum;
                            link.VerifiedAt = link.VerifiedAt ?? DateTime.UtcNow;
                            link.UpdatedAt = DateTime.UtcNow;
                        }
                    }

                    // Audit records in MigrationReconciliation (Idempotent: updates existing, adds new)
                    var rec = await _db.MigrationReconciliations.FirstOrDefaultAsync(r =>
                        r.MigrationKey == "PHASE-3B" && r.SourceType == "FdeTask" && r.SourceId == candidate.LegacyTaskId.ToString());

                    if (rec == null)
                    {
                        _db.MigrationReconciliations.Add(new MigrationReconciliation
                        {
                            MigrationKey = "PHASE-3B",
                            SourceType = "FdeTask",
                            SourceId = candidate.LegacyTaskId.ToString(),
                            TargetType = candidate.TargetLessonId.HasValue ? "Lesson" : (candidate.TargetProblemId.HasValue ? "Problem" : null),
                            TargetId = (candidate.TargetLessonId ?? candidate.TargetProblemId)?.ToString(),
                            SourceChecksum = candidate.SourceChecksum,
                            Status = candidate.MappingStatus == "Verified" ? "Applied" : candidate.MappingStatus,
                            IssueCode = candidate.IssueCode,
                            DetailsJson = JsonSerializer.Serialize(candidate),
                            AppliedAt = DateTime.UtcNow,
                            UpdatedAt = DateTime.UtcNow
                        });
                    }
                    else
                    {
                        rec.TargetType = candidate.TargetLessonId.HasValue ? "Lesson" : (candidate.TargetProblemId.HasValue ? "Problem" : null);
                        rec.TargetId = (candidate.TargetLessonId ?? candidate.TargetProblemId)?.ToString();
                        rec.Status = candidate.MappingStatus == "Verified" ? "Applied" : candidate.MappingStatus;
                        rec.IssueCode = candidate.IssueCode;
                        rec.DetailsJson = JsonSerializer.Serialize(candidate);
                        rec.UpdatedAt = DateTime.UtcNow;
                    }
                }

                await _db.SaveChangesAsync();
                await tx.CommitAsync();
                report.AuditLog.Add("FDE reconciliation changes committed successfully without fabricating database entities.");
            }
            catch (Exception ex)
            {
                await tx.RollbackAsync();
                report.AuditLog.Add($"ERROR: FDE transaction failed: {ex.Message}");
                throw;
            }
        }

        return report;
    }
}
