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

public class JavaReconciler
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<JavaReconciler> _logger;

    public JavaReconciler(StudyTrackerContext db, ILogger<JavaReconciler> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<ReconciliationReport> ReconcileJavaAsync(ReconciliationExecutionMode mode)
    {
        var report = new ReconciliationReport
        {
            Scope = "java",
            Mode = mode,
            ExecutedAt = DateTime.UtcNow
        };

        report.AuditLog.Add($"Starting Java reconciliation in {mode} mode.");

        // 1. Fetch Java Vertical by canonical normalized exact name (No numeric IDs, Contains, or FirstOrDefault)
        var allVerticals = await _db.Verticals.Include(v => v.Tasks).ToListAsync();
        var javaNormalized = NormalizationHelper.NormalizeText("Java & Spring Architecture");
        var javaCandidates = allVerticals
            .Where(v => NormalizationHelper.NormalizeText(v.Name) == javaNormalized)
            .ToList();

        StudyVertical? javaVertical = null;
        if (javaCandidates.Count == 0)
        {
            report.ConflictCount++;
            report.AuditLog.Add("Missing source conflict: Required source vertical 'Java & Spring Architecture' was not found.");
            return report;
        }
        else if (javaCandidates.Count > 1)
        {
            report.ConflictCount++;
            var candidateDetails = string.Join(", ", javaCandidates.Select(c => $"[Id: {c.Id}, Name: '{c.Name}']"));
            report.AuditLog.Add($"Ambiguity conflict: Expected exactly 1 vertical for 'Java & Spring Architecture', found {javaCandidates.Count} candidates: {candidateDetails}.");
            return report;
        }
        else
        {
            javaVertical = javaCandidates[0];
        }

        report.AuditLog.Add($"Found Java vertical '{javaVertical.Name}' (Id: {javaVertical.Id}) with {javaVertical.Tasks.Count} legacy tasks.");
        report.DiscoveredCount = javaVertical.Tasks.Count;

        // 2. Fetch Java Course, Modules, Lessons, Problems
        var courseCandidates = await _db.Courses
            .Include(c => c.Modules)
                .ThenInclude(m => m.Lessons)
                    .ThenInclude(l => l.Problems)
            .Where(c => c.Slug == "java-spring-lld")
            .ToListAsync();

        if (courseCandidates.Count != 1)
        {
            report.ConflictCount++;
            var msg = courseCandidates.Count == 0
                ? "Missing course conflict: Canonical Java Course 'java-spring-lld' not found in database."
                : $"Ambiguity conflict: Expected 1 Java Course 'java-spring-lld', found {courseCandidates.Count}.";
            report.AuditLog.Add(msg);
            return report;
        }

        var javaCourse = courseCandidates[0];
        var allLessons = javaCourse.Modules.SelectMany(m => m.Lessons).ToList();
        var allProblems = allLessons.SelectMany(l => l.Problems).ToList();

        // 3. Classify and map legacy tasks
        foreach (var task in javaVertical.Tasks.OrderBy(t => t.Id))
        {
            var rawSignature = $"{task.Id}|{task.Module}|{task.Title}|{task.IsCompleted}";
            var checksum = NormalizationHelper.ComputeSha256Checksum(rawSignature);
            var normalizedTitle = NormalizationHelper.NormalizeText(task.Title);
            var normalizedModule = NormalizationHelper.NormalizeText(task.Module);

            var candidate = new MappingCandidate
            {
                LegacyTaskId = task.Id,
                LegacyTitle = task.Title,
                LegacyModule = task.Module,
                LegacyIsCompleted = task.IsCompleted,
                SourceChecksum = checksum
            };

            // Exact match to Problem
            var matchingProblems = allProblems.Where(p => NormalizationHelper.NormalizeText(p.Title) == normalizedTitle).ToList();

            if (matchingProblems.Count == 1)
            {
                var matchedProblem = matchingProblems[0];
                candidate.TargetProblemId = matchedProblem.Id;
                candidate.TargetTitle = matchedProblem.Title;
                candidate.MappingType = "Exact";
                candidate.MappingStatus = "Verified";
                candidate.Confidence = 1.0000m;
                candidate.Note = $"Mapped to Problem {matchedProblem.Id}";
                report.ExactMappedCount++;
                report.VerifiedCount++;
            }
            else if (matchingProblems.Count > 1)
            {
                candidate.MappingType = "Exact";
                candidate.MappingStatus = "Conflict";
                candidate.Confidence = 0.5000m;
                candidate.IssueCode = "AMBIGUOUS_PROBLEM_MATCH";
                candidate.Note = $"Ambiguous problem match ({matchingProblems.Count} matches)";
                report.ConflictCount++;
            }
            else
            {
                // Exact match to Lesson
                var matchingLessons = allLessons.Where(l => NormalizationHelper.NormalizeText(l.Title) == normalizedTitle).ToList();

                if (matchingLessons.Count == 1)
                {
                    var matchedLesson = matchingLessons[0];
                    candidate.TargetLessonId = matchedLesson.Id;
                    candidate.TargetTitle = matchedLesson.Title;
                    candidate.MappingType = "TitleAndModule";
                    candidate.MappingStatus = "Verified";
                    candidate.Confidence = 0.9500m;
                    candidate.Note = $"Mapped to Lesson {matchedLesson.Id}";
                    report.ExactMappedCount++;
                    report.VerifiedCount++;
                }
                else if (matchingLessons.Count > 1)
                {
                    candidate.MappingType = "TitleAndModule";
                    candidate.MappingStatus = "Conflict";
                    candidate.Confidence = 0.5000m;
                    candidate.IssueCode = "AMBIGUOUS_LESSON_MATCH";
                    candidate.Note = $"Ambiguous lesson match ({matchingLessons.Count} matches)";
                    report.ConflictCount++;
                }
                else
                {
                    // Spring / Capstone Outline candidates
                    candidate.MappingType = "Manual";
                    candidate.MappingStatus = "Proposed";
                    candidate.Confidence = 0.7000m;
                    candidate.Note = "Spring/Capstone item - candidate for Outline lesson creation";
                    report.ProposedCount++;
                }
            }

            report.Mappings.Add(candidate);
        }

        // 4. Apply Changes if Mode == Apply
        if (mode == ReconciliationExecutionMode.Apply)
        {
            using var tx = await _db.Database.BeginTransactionAsync();
            try
            {
                foreach (var candidate in report.Mappings.Where(m => m.MappingStatus == "Verified"))
                {
                    var existingLink = await _db.StudyTaskContentLinks.FindAsync(candidate.LegacyTaskId);
                    if (existingLink == null)
                    {
                        var newLink = new StudyTaskContentLink
                        {
                            TaskId = candidate.LegacyTaskId,
                            LessonId = candidate.TargetLessonId,
                            ProblemId = candidate.TargetProblemId,
                            MappingType = candidate.MappingType,
                            MappingStatus = candidate.MappingStatus,
                            Confidence = candidate.Confidence,
                            SourceChecksum = candidate.SourceChecksum,
                            VerifiedAt = DateTime.UtcNow
                        };
                        _db.StudyTaskContentLinks.Add(newLink);
                    }
                    else
                    {
                        existingLink.LessonId = candidate.TargetLessonId;
                        existingLink.ProblemId = candidate.TargetProblemId;
                        existingLink.MappingType = candidate.MappingType;
                        existingLink.MappingStatus = candidate.MappingStatus;
                        existingLink.Confidence = candidate.Confidence;
                        existingLink.SourceChecksum = candidate.SourceChecksum;
                        existingLink.VerifiedAt = DateTime.UtcNow;
                        existingLink.UpdatedAt = DateTime.UtcNow;
                    }

                    // Record MigrationReconciliation entry
                    var reconciliationRecord = await _db.MigrationReconciliations.FirstOrDefaultAsync(r =>
                        r.MigrationKey == "PHASE-3A" && r.SourceType == "StudyTask" && r.SourceId == candidate.LegacyTaskId.ToString());

                    if (reconciliationRecord == null)
                    {
                        _db.MigrationReconciliations.Add(new MigrationReconciliation
                        {
                            MigrationKey = "PHASE-3A",
                            SourceType = "StudyTask",
                            SourceId = candidate.LegacyTaskId.ToString(),
                            TargetType = candidate.TargetLessonId.HasValue ? "Lesson" : "Problem",
                            TargetId = (candidate.TargetLessonId ?? candidate.TargetProblemId)?.ToString(),
                            SourceChecksum = candidate.SourceChecksum,
                            Status = "Applied",
                            DetailsJson = JsonSerializer.Serialize(candidate),
                            AppliedAt = DateTime.UtcNow,
                            UpdatedAt = DateTime.UtcNow
                        });
                    }
                    else
                    {
                        reconciliationRecord.Status = "Applied";
                        reconciliationRecord.TargetType = candidate.TargetLessonId.HasValue ? "Lesson" : "Problem";
                        reconciliationRecord.TargetId = (candidate.TargetLessonId ?? candidate.TargetProblemId)?.ToString();
                        reconciliationRecord.DetailsJson = JsonSerializer.Serialize(candidate);
                        reconciliationRecord.UpdatedAt = DateTime.UtcNow;
                    }
                }

                // Add CourseDomainLinks for Java: Foundations, Backend, Reliability
                var domains = await _db.KnowledgeDomains
                    .Where(d => d.Slug == "foundations" || d.Slug == "backend" || d.Slug == "reliability" ||
                                d.Code == "FOUND" || d.Code == "BE" || d.Code == "SRE")
                    .ToListAsync();

                int orderIdx = 0;
                foreach (var domain in domains)
                {
                    var existingDomainLink = await _db.CourseDomainLinks.FindAsync(javaCourse.Id, domain.Id);
                    if (existingDomainLink == null)
                    {
                        _db.CourseDomainLinks.Add(new CourseDomainLink
                        {
                            CourseId = javaCourse.Id,
                            DomainId = domain.Id,
                            IsPrimary = domain.Slug == "backend" || domain.Code == "BE",
                            OrderIndex = orderIdx++,
                            CreatedAt = DateTime.UtcNow
                        });
                    }
                }

                await _db.SaveChangesAsync();
                await tx.CommitAsync();
                report.AuditLog.Add("Reconciliation changes committed successfully to database.");
            }
            catch (Exception ex)
            {
                await tx.RollbackAsync();
                report.AuditLog.Add($"ERROR: Reconciliation transaction rolled back due to error: {ex.Message}");
                throw;
            }
        }

        return report;
    }
}
