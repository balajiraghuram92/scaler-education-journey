namespace TesseraEditorTools.AssetImport;

public static class ModelImporter
{
    public static int CountMeshes(IEnumerable<string> nodes)
    {
        return nodes.Count(n => n.StartsWith("mesh:", StringComparison.Ordinal));
    }
}
