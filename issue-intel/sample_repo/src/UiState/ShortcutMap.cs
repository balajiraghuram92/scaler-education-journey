namespace TesseraEditorTools.UiState;

public sealed class ShortcutMap
{
    private readonly Dictionary<string, string> _map = new(StringComparer.Ordinal);

    public void Bind(string gesture, string command) => _map[gesture] = command;

    public string? Resolve(string gesture)
    {
        return _map.TryGetValue(gesture, out var command) ? command : null;
    }
}
