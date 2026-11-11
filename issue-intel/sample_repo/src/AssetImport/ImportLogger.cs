namespace TesseraEditorTools.AssetImport;

public sealed class ImportLogger
{
    private readonly List<string> _entries = [];

    public void Log(string message) => _entries.Add(message);

    public IReadOnlyList<string> Entries => _entries;
}
