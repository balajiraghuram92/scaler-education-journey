using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services;

public class AtlasQueryService
{
    private readonly StudyTrackerContext _db;

    public AtlasQueryService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<object> GetKnowledgeAtlasAsync()
    {
        var domains = await _db.KnowledgeDomains
            .Include(d => d.ConceptConnections)
                .ThenInclude(cc => cc.Concept)
            .OrderBy(d => d.OrderIndex)
            .ToListAsync();

        var concepts = await _db.KnowledgeConcepts
            .Include(c => c.DomainConnections)
            .Include(c => c.Prerequisites)
                .ThenInclude(p => p.PrerequisiteConcept)
            .Include(c => c.OutgoingRelations)
                .ThenInclude(r => r.TargetConcept)
            .Include(c => c.NextLessons)
            .OrderBy(c => c.OrderIndex)
            .ToListAsync();

        return new
        {
            domains = domains.Select(d => new
            {
                d.Id,
                d.Slug,
                d.Name,
                d.Code,
                d.Description,
                d.Icon,
                d.ColorHex,
                d.OrderIndex,
                conceptCount = d.ConceptConnections.Count
            }),
            concepts = concepts.Select(c => new
            {
                c.Id,
                c.Slug,
                c.Title,
                c.SubLabel,
                c.Summary,
                c.Difficulty,
                c.Icon,
                c.EstimatedHours,
                c.OrderIndex,
                domainIds = c.DomainConnections.Select(dc => dc.DomainId).ToList(),
                prerequisites = c.Prerequisites.Select(p => new
                {
                    name = p.PrerequisiteConcept?.Title ?? "Prerequisite",
                    p.PrerequisiteConceptId,
                    p.Status
                }),
                outgoingRelations = c.OutgoingRelations.Select(r => new
                {
                    r.TargetConceptId,
                    targetTitle = r.TargetConcept?.Title ?? "Related Concept",
                    targetSlug = r.TargetConcept?.Slug ?? string.Empty,
                    r.RelationshipType
                }),
                nextLessons = c.NextLessons
                    .OrderBy(nl => nl.OrderIndex)
                    .Select(nl => new { nl.LessonId, nl.LessonSlug, nl.LessonTitle, nl.ModuleName })
            })
        };
    }
}
