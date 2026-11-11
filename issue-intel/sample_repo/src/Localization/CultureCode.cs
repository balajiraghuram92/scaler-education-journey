namespace TesseraEditorTools.Localization;

public static class CultureCode
{
    public static string Normalize(string code)
    {
        return code.ToLowerInvariant();
    }
}
