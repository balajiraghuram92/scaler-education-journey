namespace TesseraEditorTools.Localization;

public static class LocaleComparer
{
    public static bool EqualsIgnoreCase(string left, string right)
    {
        return string.Equals(left, right, StringComparison.OrdinalIgnoreCase);
    }
}
