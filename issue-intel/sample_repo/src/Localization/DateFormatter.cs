using System.Globalization;

namespace TesseraEditorTools.Localization;

public static class DateFormatter
{
    public static string ToSortableDate(DateOnly date)
    {
        return date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
    }
}
