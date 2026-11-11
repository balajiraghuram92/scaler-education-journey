namespace TesseraEditorTools.VersionControl;

public sealed class HistoryNode
{
    public required string Id { get; init; }
    public HistoryNode? Parent { get; init; }
}

public static class HistoryWalker
{
    public static IEnumerable<string> Walk(HistoryNode start)
    {
        HistoryNode? current = start;
        while (current is not null)
        {
            yield return current.Id;
            current = current.Parent;
        }
    }
}
