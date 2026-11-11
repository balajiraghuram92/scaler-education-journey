namespace TesseraEditorTools.Localization;

public static class PluralRules
{
    // CLDR: French treats 0 as singular ("0 fichier").
    public static string FrenchCategory(int count)
    {
        return count is 0 or 1 ? "one" : "other";
    }

    public static string EnglishCategory(int count)
    {
        return count == 1 ? "one" : "other";
    }
}
