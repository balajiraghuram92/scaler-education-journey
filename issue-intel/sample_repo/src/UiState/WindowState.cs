namespace TesseraEditorTools.UiState;

public sealed record WindowState(int X, int Y, int Width, int Height)
{
    public bool IsMinimized => Width == 0 || Height == 0;
}
