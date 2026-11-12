using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public class LocalizationStringService
{
    private readonly StudyTrackerContext _db;

    public LocalizationStringService(StudyTrackerContext db)
    {
        _db = db;
    }

    public async Task<IReadOnlyList<LocalizationStringRowDto>> GetStringsAsync(
        string projectSlug,
        string localeCode,
        CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var strings = await _db.LocalizationStrings
            .AsNoTracking()
            .Where(s => s.ProjectId == project.Id)
            .Include(s => s.Translations.Where(t => t.LocaleCode == localeCode))
            .OrderBy(s => s.Id)
            .ToListAsync(ct);

        var result = new List<LocalizationStringRowDto>();
        foreach (var str in strings)
        {
            var translation = str.Translations.FirstOrDefault();
            result.Add(new LocalizationStringRowDto(
                str.Id,
                str.Key,
                str.SourceText,
                localeCode,
                translation?.TargetText,
                translation?.Stage ?? "New",
                translation?.TranslationSource ?? "Manual",
                translation?.UpdatedAt
            ));
        }

        return result;
    }

    public async Task<LocalizationStringRowDto> UpdateTranslationAsync(
        string projectSlug,
        int stringId,
        string localeCode,
        UpdateTranslationRequest request,
        CancellationToken ct = default)
    {
        var project = await _db.LocalizationProjects
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Slug == projectSlug, ct);

        if (project == null)
        {
            throw new LocalizationProjectNotFoundException(projectSlug);
        }

        var str = await _db.LocalizationStrings
            .FirstOrDefaultAsync(s => s.Id == stringId && s.ProjectId == project.Id, ct);

        if (str == null)
        {
            throw new LocalizationStringNotFoundException(stringId);
        }

        var translation = await _db.LocalizationTranslations
            .FirstOrDefaultAsync(t => t.StringId == stringId && t.LocaleCode == localeCode, ct);

        var hasTarget = !string.IsNullOrWhiteSpace(request.TargetText);

        if (translation == null)
        {
            translation = new LocalizationTranslation
            {
                StringId = stringId,
                LocaleCode = localeCode,
                TargetText = request.TargetText,
                Stage = hasTarget ? "Translated" : "New",
                TranslationSource = "Manual",
                NeedsReview = false,
                UpdatedAt = DateTime.UtcNow
            };
            _db.LocalizationTranslations.Add(translation);
        }
        else
        {
            translation.TargetText = request.TargetText;
            translation.TranslationSource = "Manual";
            translation.Stage = hasTarget ? "Translated" : "New";
            translation.UpdatedAt = DateTime.UtcNow;
        }

        await _db.SaveChangesAsync(ct);

        return new LocalizationStringRowDto(
            str.Id,
            str.Key,
            str.SourceText,
            localeCode,
            translation.TargetText,
            translation.Stage,
            translation.TranslationSource,
            translation.UpdatedAt
        );
    }
}
