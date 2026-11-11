namespace TesseraEditorTools.Localization;

public static class ResourceLoader
{
    public static string BuildKey(string name)
    {
        return name.ToUpperInvariant();
    }

    public static string? Find(IReadOnlyDictionary<string, string> resources, string name)
    {
        return resources.TryGetValue(BuildKey(name), out var value) ? value : null;
    }
}
