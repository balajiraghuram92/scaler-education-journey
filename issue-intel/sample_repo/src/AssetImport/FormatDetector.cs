namespace TesseraEditorTools.AssetImport;

public static class FormatDetector
{
    public static string Detect(string path)
    {
        return Path.GetExtension(path).ToLowerInvariant() switch
        {
            ".png" => "texture",
            ".wav" => "audio",
            ".fbx" => "model",
            _ => "unknown",
        };
    }
}
