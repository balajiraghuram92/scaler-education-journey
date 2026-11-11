namespace TesseraEditorTools.UiState;

public sealed record PanelLayout(string Name, int Width, int Height);

public static class LayoutSerializer
{
    public static string Serialize(PanelLayout layout)
    {
        return $"{layout.Name}|{layout.Width}|{layout.Height}";
    }

    public static PanelLayout Deserialize(string text)
    {
        var parts = text.Split('|');
        return new PanelLayout(parts[0], int.Parse(parts[1]), int.Parse(parts[2]));
    }
}
