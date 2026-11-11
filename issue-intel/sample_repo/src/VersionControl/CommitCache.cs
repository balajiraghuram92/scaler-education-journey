namespace TesseraEditorTools.VersionControl;

public sealed class CommitCache
{
    private readonly Dictionary<string, string> _entries = new(StringComparer.Ordinal);

    public void Store(string id, string payload)
    {
        _entries[Normalize(id)] = payload;
    }

    public bool TryGet(string id, out string? payload)
    {
        return _entries.TryGetValue(Normalize(id), out payload);
    }

    private static string Normalize(string id) => id.ToLowerInvariant();
}
