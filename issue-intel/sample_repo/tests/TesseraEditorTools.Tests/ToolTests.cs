using TesseraEditorTools.AssetImport;
using TesseraEditorTools.Localization;
using TesseraEditorTools.UiState;
using TesseraEditorTools.VersionControl;

// Ship tests: they cover behaviour the planted bugs never touch, so they pass
// both on the clean base and on main with all 12 bugs introduced.
public sealed class ToolTests
{
    [Fact]
    public void DiffCountsAddedLines()
    {
        var before = new[] { "a", "b" };
        var after = new[] { "a", "b", "c" };
        Assert.Equal(1, DiffUtil.CountChangedLines(before, after));
    }

    [Fact]
    public void CatalogFormatsTemplate()
    {
        var catalog = new StringCatalog();
        catalog.Add("greet", "Hello, {0}!");
        Assert.Equal("Hello, Ada!", catalog.Format("greet", "Ada"));
    }

    [Fact]
    public void ComparerIgnoresCase()
    {
        Assert.True(LocaleComparer.EqualsIgnoreCase("File", "fILE"));
        Assert.False(LocaleComparer.EqualsIgnoreCase("File", "Edit"));
    }

    [Fact]
    public void SortableDateIsIso()
    {
        Assert.Equal("2024-03-09", DateFormatter.ToSortableDate(new DateOnly(2024, 3, 9)));
    }

    [Fact]
    public void PanelTogglesVisibility()
    {
        var panel = new PanelModel { Name = "Explorer" };
        panel.Toggle();
        Assert.False(panel.IsVisible);
    }

    [Fact]
    public void ShortcutResolvesBinding()
    {
        var map = new ShortcutMap();
        map.Bind("Ctrl+S", "Save");
        Assert.Equal("Save", map.Resolve("Ctrl+S"));
        Assert.Null(map.Resolve("Ctrl+Q"));
    }

    [Fact]
    public void MinimizedWindowHasZeroArea()
    {
        Assert.True(new WindowState(0, 0, 0, 600).IsMinimized);
        Assert.False(new WindowState(0, 0, 800, 600).IsMinimized);
    }

    [Fact]
    public void ModelImporterCountsMeshNodes()
    {
        var nodes = new[] { "mesh:body", "light:key", "mesh:wheel" };
        Assert.Equal(2, ModelImporter.CountMeshes(nodes));
    }

    [Fact]
    public void AtlasCountsSprites()
    {
        var atlas = new SpriteAtlas();
        atlas.Add("hero");
        atlas.Add("enemy");
        Assert.Equal(2, atlas.Count);
    }

    [Fact]
    public void FormatDetectorClassifiesExtensions()
    {
        Assert.Equal("texture", FormatDetector.Detect("wall.PNG"));
        Assert.Equal("audio", FormatDetector.Detect("hit.wav"));
        Assert.Equal("model", FormatDetector.Detect("car.fbx"));
        Assert.Equal("unknown", FormatDetector.Detect("note.txt"));
    }

    [Fact]
    public void ImportLoggerKeepsEntries()
    {
        var log = new ImportLogger();
        log.Log("start");
        Assert.Single(log.Entries);
        Assert.Equal("start", log.Entries[0]);
    }

    [Fact]
    public void ValidBranchNamePasses()
    {
        Assert.True(BranchNameValidator.IsValid("feature/login"));
        Assert.False(BranchNameValidator.IsValid(""));
    }
}
