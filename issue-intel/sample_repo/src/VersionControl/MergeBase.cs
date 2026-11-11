namespace TesseraEditorTools.VersionControl;

public static class MergeBase
{
    public static string? FindCommonAncestor(IEnumerable<string> first, IEnumerable<string> second)
    {
        var seen = new HashSet<string>(second);
        foreach (var commit in first)
        {
            if (seen.Contains(commit))
            {
                return commit;
            }
        }
        return null;
    }
}
