namespace TesseraEditorTools.UiState;

public sealed class RecentFiles
{
    private readonly List<string> _files = [];
    private readonly int _capacity;

    public RecentFiles(int capacity = 8)
    {
        _capacity = capacity;
    }

    public void Add(string path)
    {
        _files.Remove(path);
        _files.Insert(0, path);
        while (_files.Count > _capacity)
        {
            _files.RemoveAt(_files.Count - 1);
        }
    }

    public IReadOnlyList<string> Files => _files;
}
