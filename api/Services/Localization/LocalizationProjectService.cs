using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;

namespace StudyTracker.Api.Services.Localization;

public class LocalizationProjectService
{
    private readonly StudyTrackerContext _db;

    public LocalizationProjectService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<LocalizationProjectDto> GetProjectAsync(string slug, CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .Include(p => p.Locales)
            .FirstOrDefaultAsync(p => p.Slug == slug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(slug);
        }

        var locales = project.Locales
            .OrderBy(l => l.Id)
            .Select(l => new LocalizationLocaleDto(l.Id, l.LocaleCode, l.DisplayName))
            .ToList();

        return new LocalizationProjectDto(
            project.Id,
            project.Slug,
            project.Name,
            project.SourceLocale,
            project.CreatedAt,
            locales
        );
    }

    public async Task<IReadOnlyList<LocalizationProjectDto>> GetProjectsAsync(CancellationToken ct = default)
    {
        var projects = await _db.LocalizationProjects
            .AsNoTracking()
            .Include(p => p.Locales)
            .OrderBy(p => p.Id)
            .ToListAsync(ct);

        return projects.Select(project => new LocalizationProjectDto(
            project.Id,
            project.Slug,
            project.Name,
            project.SourceLocale,
            project.CreatedAt,
            project.Locales
                .OrderBy(l => l.Id)
                .Select(l => new LocalizationLocaleDto(l.Id, l.LocaleCode, l.DisplayName))
                .ToList()
        )).ToList();
    }
}
