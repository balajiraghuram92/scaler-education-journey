namespace TesseraEditorTools.Localization;

public sealed class StringCatalog
{
    private readonly Dictionary<string, string> _entries = new(StringComparer.Ordinal);

    public void Add(string key, string template) => _entries[key] = template;

    public string Format(string key, params object[] args)
    {
        return string.Format(_entries[key], args);
    }
}
