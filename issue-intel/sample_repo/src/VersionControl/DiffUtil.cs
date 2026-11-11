namespace TesseraEditorTools.VersionControl;

public static class DiffUtil
{
    public static int CountChangedLines(string[] before, string[] after)
    {
        var beforeSet = new HashSet<string>(before);
        return after.Count(line => !beforeSet.Contains(line));
    }
}
