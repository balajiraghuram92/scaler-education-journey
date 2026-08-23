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

public class AzureLabsReconciler
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<AzureLabsReconciler> _logger;

    public AzureLabsReconciler(StudyTrackerContext db, ILogger<AzureLabsReconciler> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<ReconciliationReport> ReconcileAzureAndLabsAsync(ReconciliationExecutionMode mode)
    {
        var report = new ReconciliationReport
        {
            Scope = "azure-labs",
            Mode = mode,
            ExecutedAt = DateTime.UtcNow
        };

        // 1. Strict Vertical Lookups with normalized exact matching (No numeric IDs, Contains, or FirstOrDefault)
        var allVerticals = await _db.Verticals.Include(v => v.Tasks).ToListAsync();

        var azureNormalized = NormalizationHelper.NormalizeText("Azure Certifications");
        var azureCandidates = allVerticals
            .Where(v => NormalizationHelper.NormalizeText(v.Name) == azureNormalized)
            .ToList();

        var labsNormalized = NormalizationHelper.NormalizeText("Lab Projects");
        var labsCandidates = allVerticals
            .Where(v => NormalizationHelper.NormalizeText(v.Name) == labsNormalized)
            .ToList();

        StudyVertical? azureVertical = null;
        if (azureCandidates.Count == 0)
        {
            report.ConflictCount++;
            report.AuditLog.Add("Missing source conflict: Required source vertical 'Azure Certifications' was not found.");
        }
        else if (azureCandidates.Count > 1)
        {
            report.ConflictCount++;
            var candidateDetails = string.Join(", ", azureCandidates.Select(c => $"[Id: {c.Id}, Name: '{c.Name}']"));
            report.AuditLog.Add($"Ambiguity conflict: Expected exactly 1 vertical for 'Azure Certifications', found {azureCandidates.Count} candidates: {candidateDetails}.");
        }
        else
        {
            azureVertical = azureCandidates[0];
        }

        StudyVertical? labsVertical = null;
        if (labsCandidates.Count == 0)
        {
            report.ConflictCount++;
            report.AuditLog.Add("Missing source conflict: Required source vertical 'Lab Projects' was not found.");
        }
        else if (labsCandidates.Count > 1)
        {
            report.ConflictCount++;
            var candidateDetails = string.Join(", ", labsCandidates.Select(c => $"[Id: {c.Id}, Name: '{c.Name}']"));
            report.AuditLog.Add($"Ambiguity conflict: Expected exactly 1 vertical for 'Lab Projects', found {labsCandidates.Count} candidates: {candidateDetails}.");
        }
        else
        {
            labsVertical = labsCandidates[0];
        }

        if (azureVertical == null || labsVertical == null)
        {
            report.AuditLog.Add("Reconciliation stopped: One or more required Azure/Labs source verticals could not be uniquely resolved.");
            return report;
        }

        // 2. Fetch pre-existing canonical Courses, Modules, Lessons, Problems (Do not fabricate new ones)
        var azureCourseCandidates = await _db.Courses
            .Include(c => c.Modules)
                .ThenInclude(m => m.Lessons)
                    .ThenInclude(l => l.Problems)
            .Where(c => c.Slug == "azure-certification")
            .ToListAsync();

        var allAzureLessons = azureCourseCandidates.Count == 1
            ? azureCourseCandidates[0].Modules.SelectMany(m => m.Lessons).ToList()
            : new List<Lesson>();
        var allAzureProblems = allAzureLessons.SelectMany(l => l.Problems).ToList();

        var labsCourseCandidates = await _db.Courses
            .Include(c => c.Modules)
                .ThenInclude(m => m.Lessons)
                    .ThenInclude(l => l.Problems)
            .Where(c => c.Slug == "lab-projects")
            .ToListAsync();

        var allLabsLessons = labsCourseCandidates.Count == 1
            ? labsCourseCandidates[0].Modules.SelectMany(m => m.Lessons).ToList()
            : new List<Lesson>();
        var allLabsProblems = allLabsLessons.SelectMany(l => l.Problems).ToList();

        var totalTasks = azureVertical.Tasks.Count + labsVertical.Tasks.Count;
        report.DiscoveredCount = totalTasks;

        // 3. Classify Azure Tasks against pre-existing canonical Azure lessons/problems
        foreach (var task in azureVertical.Tasks)
        {
            var rawSignature = $"{task.Id}|{task.Module}|{task.Title}|{task.IsCompleted}";
            var checksum = NormalizationHelper.ComputeSha256Checksum(rawSignature);
            var normalizedTitle = NormalizationHelper.NormalizeText(task.Title);

            var candidate = new MappingCandidate
            {
                LegacyTaskId = task.Id,
                LegacyTitle = task.Title,
                LegacyModule = task.Module,
                LegacyIsCompleted = task.IsCompleted,
                SourceChecksum = checksum
            };

            var matchingProblems = allAzureProblems.Where(p => NormalizationHelper.NormalizeText(p.Title) == normalizedTitle).ToList();
            var matchingLessons = allAzureLessons.Where(l => NormalizationHelper.NormalizeText(l.Title) == normalizedTitle).ToList();

            var totalMatches = matchingProblems.Count + matchingLessons.Count;
            if (totalMatches == 0)
            {
                candidate.MappingType = "Manual";
                candidate.MappingStatus = "Proposed";
                candidate.Confidence = 0.6000m;
                candidate.IssueCode = "UNMAPPED_LEGACY_TASK";
                candidate.Note = "No pre-existing canonical Azure lesson found in curriculum. Retained as proposed item without fabricating database entities.";
                report.ProposedCount++;
            }
            else if (totalMatches > 1)
            {
                candidate.MappingType = "Ambiguous";
                candidate.MappingStatus = "Conflict";
                candidate.Confidence = 0.5000m;
                candidate.IssueCode = "AMBIGUOUS_CANONICAL_TARGET";
                candidate.Note = $"Ambiguous target match: found {matchingLessons.Count} lessons and {matchingProblems.Count} problems matching title '{task.Title}'.";
                report.ConflictCount++;
            }
            else if (matchingProblems.Count == 1)
            {
                var problem = matchingProblems[0];
                candidate.TargetProblemId = problem.Id;
                candidate.TargetTitle = problem.Title;
                candidate.MappingType = "Exact";
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
                candidate.MappingType = "TitleAndModule";
                candidate.MappingStatus = "Verified";
                candidate.Confidence = 0.9500m;
                candidate.Note = $"Deterministically mapped to canonical Lesson (Id: {lesson.Id}).";
                report.ExactMappedCount++;
                report.VerifiedCount++;
            }

            report.Mappings.Add(candidate);
        }

        // 4. Classify Lab Tasks against pre-existing canonical Lab lessons/problems
        foreach (var task in labsVertical.Tasks)
        {
            var rawSignature = $"{task.Id}|{task.Module}|{task.Title}|{task.IsCompleted}";
            var checksum = NormalizationHelper.ComputeSha256Checksum(rawSignature);
            var normalizedTitle = NormalizationHelper.NormalizeText(task.Title);

            var candidate = new MappingCandidate
            {
                LegacyTaskId = task.Id,
                LegacyTitle = task.Title,
                LegacyModule = task.Module,
                LegacyIsCompleted = task.IsCompleted,
                SourceChecksum = checksum
            };

            var matchingProblems = allLabsProblems.Where(p => NormalizationHelper.NormalizeText(p.Title) == normalizedTitle).ToList();
            var matchingLessons = allLabsLessons.Where(l => NormalizationHelper.NormalizeText(l.Title) == normalizedTitle).ToList();

            var totalMatches = matchingProblems.Count + matchingLessons.Count;
            if (totalMatches == 0)
            {
                candidate.MappingType = "Manual";
                candidate.MappingStatus = "Proposed";
                candidate.Confidence = 0.6000m;
                candidate.IssueCode = "UNMAPPED_LEGACY_TASK";
                candidate.Note = "No pre-existing canonical Lab lesson found in curriculum. Retained as proposed item without fabricating database entities.";
                report.ProposedCount++;
            }
            else if (totalMatches > 1)
            {
                candidate.MappingType = "Ambiguous";
                candidate.MappingStatus = "Conflict";
                candidate.Confidence = 0.5000m;
                candidate.IssueCode = "AMBIGUOUS_CANONICAL_TARGET";
                candidate.Note = $"Ambiguous target match: found {matchingLessons.Count} lessons and {matchingProblems.Count} problems matching title '{task.Title}'.";
                report.ConflictCount++;
            }
            else if (matchingProblems.Count == 1)
            {
                var problem = matchingProblems[0];
                candidate.TargetProblemId = problem.Id;
                candidate.TargetTitle = problem.Title;
                candidate.MappingType = "Exact";
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
                candidate.MappingType = "TitleAndModule";
                candidate.MappingStatus = "Verified";
                candidate.Confidence = 0.9500m;
                candidate.Note = $"Deterministically mapped to canonical Lesson (Id: {lesson.Id}).";
                report.ExactMappedCount++;
                report.VerifiedCount++;
            }

            report.Mappings.Add(candidate);
        }

        // 5. Apply mode creates StudyTaskContentLink ONLY for Verified mappings and audits in MigrationReconciliation
        if (mode == ReconciliationExecutionMode.Apply)
        {
            using var tx = await _db.Database.BeginTransactionAsync();
            try
            {
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

                    // Audit records in MigrationReconciliation (Idempotent)
                    var rec = await _db.MigrationReconciliations.FirstOrDefaultAsync(r =>
                        r.MigrationKey == "PHASE-3C" && r.SourceType == "StudyTask" && r.SourceId == candidate.LegacyTaskId.ToString());

                    if (rec == null)
                    {
                        _db.MigrationReconciliations.Add(new MigrationReconciliation
                        {
                            MigrationKey = "PHASE-3C",
                            SourceType = "StudyTask",
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
                report.AuditLog.Add("Azure & Labs reconciliation changes committed successfully without fabricating database entities.");
            }
            catch (Exception ex)
            {
                await tx.RollbackAsync();
                report.AuditLog.Add($"ERROR: Azure/Labs transaction failed: {ex.Message}");
                throw;
            }
        }

        return report;
    }
}
