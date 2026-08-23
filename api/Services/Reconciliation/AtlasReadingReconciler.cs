using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services.Reconciliation;

public class AtlasReadingReconciler
{
    private readonly StudyTrackerContext _db;
    private readonly ILogger<AtlasReadingReconciler> _logger;

    public AtlasReadingReconciler(StudyTrackerContext db, ILogger<AtlasReadingReconciler> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<ReconciliationReport> ReconcileAtlasAndReadingAsync(ReconciliationExecutionMode mode)
    {
        var report = new ReconciliationReport
        {
            Scope = "atlas-reading",
            Mode = mode,
            ExecutedAt = DateTime.UtcNow
        };

        var readingItems = await _db.ReadingMapItems.ToListAsync();
        var threads = await _db.KnowledgeThreads.Include(t => t.Steps).ToListAsync();
        var concepts = await _db.KnowledgeConcepts.ToListAsync();
        var lessons = await _db.Lessons.ToListAsync();

        report.DiscoveredCount = readingItems.Count + threads.Count;

        if (mode == ReconciliationExecutionMode.Apply)
        {
            using var tx = await _db.Database.BeginTransactionAsync();
            try
            {
                // 1. Tag prototype reading map items as IsSeeded = true
                foreach (var item in readingItems)
                {
                    item.IsSeeded = true;
                    // Attempt linking with Java lessons
                    var normalizedTitle = NormalizationHelper.NormalizeText(item.Title);
                    var matchedLesson = lessons.FirstOrDefault(l =>
                        NormalizationHelper.NormalizeText(l.Title) == normalizedTitle ||
                        NormalizationHelper.NormalizeText(l.Title).Contains(normalizedTitle));

                    if (matchedLesson != null)
                    {
                        item.LessonId = matchedLesson.Id;
                    }
                }

                // 2. Normalize KnowledgeThread.RawPath into KnowledgeThreadStep
                foreach (var thread in threads)
                {
                    if (string.IsNullOrWhiteSpace(thread.RawPath)) continue;

                    // Parse path items separated by "→" or "->"
                    var segments = thread.RawPath.Split(new[] { "→", "->", ">" }, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
                    int stepIdx = 0;
                    foreach (var segment in segments)
                    {
                        var normalizedSegment = NormalizationHelper.NormalizeText(segment);
                        var matchedConcept = concepts.FirstOrDefault(c =>
                            NormalizationHelper.NormalizeText(c.Title) == normalizedSegment ||
                            NormalizationHelper.NormalizeText(c.Slug) == normalizedSegment);

                        var existingStep = await _db.KnowledgeThreadSteps.FindAsync(thread.Id, stepIdx);
                        if (existingStep == null)
                        {
                            _db.KnowledgeThreadSteps.Add(new KnowledgeThreadStep
                            {
                                ThreadId = thread.Id,
                                OrderIndex = stepIdx,
                                Label = segment,
                                ConceptId = matchedConcept?.Id,
                                CreatedAt = DateTime.UtcNow
                            });
                        }
                        stepIdx++;
                    }
                }

                await _db.SaveChangesAsync();
                await tx.CommitAsync();
                report.AuditLog.Add("Reading map seed tagging and Knowledge thread step normalization completed.");
            }
            catch (Exception ex)
            {
                await tx.RollbackAsync();
                report.AuditLog.Add($"ERROR: Atlas/Reading transaction failed: {ex.Message}");
                throw;
            }
        }

        return report;
    }
}
