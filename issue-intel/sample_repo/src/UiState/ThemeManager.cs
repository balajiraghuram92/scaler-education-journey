namespace TesseraEditorTools.UiState;

public sealed class ThemeManager
{
    private readonly SettingsStore _store;

    public ThemeManager(SettingsStore store)
    {
        _store = store;
    }

    public void SaveTheme(string theme)
    {
        _store.Set(SettingsStore.WellKnown.Theme, theme);
    }

    public string? LoadTheme()
    {
        return _store.Get(SettingsStore.WellKnown.Theme);
    }
}
