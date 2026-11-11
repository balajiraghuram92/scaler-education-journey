namespace TesseraEditorTools.UiState;

public sealed class PanelModel
{
    public string Name { get; set; } = string.Empty;
    public bool IsVisible { get; set; } = true;

    public void Toggle() => IsVisible = !IsVisible;
}
