using System;
using System.Collections.Generic;
using System.Linq;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Services.Localization;

public static class JobScope
{
    public const string VendorSource = "Marketplace";
    public const string MachineSource = "AI";

    public static bool IsOpen(LocalizationString s, string localeCode)
    {
        var translation = s.Translations.FirstOrDefault(t => t.LocaleCode == localeCode);
        return translation == null
            || string.IsNullOrWhiteSpace(translation.TargetText)
            || translation.Stage != "Approved";
    }

    public static bool IsVendorReviewed(LocalizationTranslation? t)
    {
        return t != null && t.TranslationSource == VendorSource && !string.IsNullOrWhiteSpace(t.TargetText);
    }

    public static int CompletedPercent(
        IEnumerable<LocalizationString> strings,
        string localeCode,
        int stringCount,
        string jobStatus)
    {
        if (jobStatus == "Approved")
        {
            return 100;
        }

        if (stringCount == 0)
        {
            return 0;
        }

        var done = strings.Count(s =>
        {
            var translation = s.Translations.FirstOrDefault(t => t.LocaleCode == localeCode);
            return translation != null
                && translation.Stage != "Approved"
                && IsVendorReviewed(translation);
        });

        return Math.Min((done * 100) / stringCount, 100);
    }
}
