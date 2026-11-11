namespace TesseraEditorTools.AssetImport;

public static class TextureScaler
{
    public static int MipSize(int size, int level)
    {
        for (var i = 0; i < level; i++)
        {
            size /= 2;
        }
        return Math.Max(1, size);
    }
}
