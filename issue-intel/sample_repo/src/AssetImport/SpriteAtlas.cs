namespace TesseraEditorTools.AssetImport;

public sealed class SpriteAtlas
{
    private readonly List<string> _sprites = [];

    public void Add(string sprite) => _sprites.Add(sprite);

    public int Count => _sprites.Count;
}
