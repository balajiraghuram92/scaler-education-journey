namespace TesseraEditorTools.UiState;

public sealed class SettingsStore
{
    public static class WellKnown
    {
        public const string Theme = "Theme";
    }

    private readonly Dictionary<string, string> _values = new(StringComparer.Ordinal);

    public void Set(string key, string value)
    {
        _values[key] = value;
    }

    public string? Get(string key)
    {
        return _values.TryGetValue(key, out var value) ? value : null;
    }
}
