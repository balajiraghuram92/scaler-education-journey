using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public class SnapshotService
{
    private readonly StudyTrackerContext _db;

    public SnapshotService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<IReadOnlyList<BuildSnapshotDto>> GetSnapshotsAsync(string projectSlug, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var snapshots = await _db.LocalizationBuildSnapshots
            .AsNoTracking()
            .Where(b => b.ProjectId == project.Id)
            .Include(b => b.LocaleCounts)
            .OrderByDescending(b => b.CreatedAt)
            .ToListAsync(ct);

        return snapshots.Select(s => new BuildSnapshotDto(
            s.Id,
            s.SnapshotIdentifier,
            s.SourceRevision,
            s.LocalizationRevision,
            s.Config,
            s.CreatedAt,
            s.LocaleCounts
                .OrderBy(c => c.LocaleCode)
                .Select(c => new BuildSnapshotLocaleCountDto(c.LocaleCode, c.ApprovedCount))
                .ToList()
        )).ToList();
    }

    public async Task<BuildSnapshotDto> CutSnapshotAsync(string projectSlug, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .Include(p => p.Locales)
            .Include(p => p.Strings)
                .ThenInclude(s => s.Translations)
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var now = DateTime.UtcNow;
        var datePrefix = $"snap-{now:yyyy-MM-dd}-";

        var todaysSnapshots = await _db.LocalizationBuildSnapshots
            .Where(s => s.ProjectId == project.Id && s.SnapshotIdentifier.StartsWith(datePrefix))
            .OrderBy(s => s.SnapshotIdentifier)
            .ToListAsync(ct);

        char nextSuffix = (char)('a' + todaysSnapshots.Count);
        var snapshotId = $"{datePrefix}{nextSuffix}";

        var totalSnapshotsCount = await _db.LocalizationBuildSnapshots.CountAsync(s => s.ProjectId == project.Id, ct);
        var sourceRevision = $"r{18235 + totalSnapshotsCount}";
        var localizationRevision = $"l{09982 + totalSnapshotsCount:D5}";

        var snapshot = new BuildSnapshot
        {
            ProjectId = project.Id,
            SnapshotIdentifier = snapshotId,
            SourceRevision = sourceRevision,
            LocalizationRevision = localizationRevision,
            Config = "Production-Default",
            CreatedAt = now
        };

        var localeCounts = new List<BuildSnapshotLocaleCount>();
        foreach (var locale in project.Locales)
        {
            var approvedCount = project.Strings
                .Count(s => s.Translations.Any(t => t.LocaleCode == locale.LocaleCode && t.Stage == "Approved"));

            localeCounts.Add(new BuildSnapshotLocaleCount
            {
                BuildSnapshot = snapshot,
                LocaleCode = locale.LocaleCode,
                ApprovedCount = approvedCount
            });
        }

        snapshot.LocaleCounts = localeCounts;
        _db.LocalizationBuildSnapshots.Add(snapshot);
        await _db.SaveChangesAsync(ct);

        return new BuildSnapshotDto(
            snapshot.Id,
            snapshot.SnapshotIdentifier,
            snapshot.SourceRevision,
            snapshot.LocalizationRevision,
            snapshot.Config,
            snapshot.CreatedAt,
            localeCounts.Select(c => new BuildSnapshotLocaleCountDto(c.LocaleCode, c.ApprovedCount)).ToList()
        );
    }
}
