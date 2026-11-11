namespace TesseraEditorTools.Localization;

public static class ResourceFallback
{
    public static string Lookup(IReadOnlyDictionary<string, string> table, string culture, string invariant)
    {
        if (table.TryGetValue(culture, out var exact))
        {
            return exact;
        }
        var dash = culture.IndexOf('-');
        if (dash > 0 && table.TryGetValue(culture[..dash], out var parent))
        {
            return parent;
        }
        return invariant;
    }
}
