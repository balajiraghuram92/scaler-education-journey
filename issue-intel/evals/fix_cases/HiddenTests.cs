using System.Globalization;
using TesseraEditorTools.AssetImport;
using TesseraEditorTools.Localization;
using TesseraEditorTools.UiState;
using TesseraEditorTools.VersionControl;

// Hidden tests: each fails on main with the planted bugs and passes with its
// reference patch applied. Not referenced by sample_repo; app/ may not read
// this folder. Bug09 needs ICU data for tr-TR casing (present on Windows).

public sealed class Bug01TrailerTests
{
    [Fact]
    public void TrailerValueKeepsInnerColons()
    {
        var trailers = CommitParser.ParseTrailers(["Reviewed-By: ada: senior", "NoColon"]);
        Assert.Single(trailers);
        Assert.Equal("Reviewed-By", trailers[0].Key);
        Assert.Equal("ada: senior", trailers[0].Value);
    }
}

public sealed class Bug02BranchNameTests
{
    [Fact]
    public void InnerDotSequenceRejected()
    {
        Assert.False(BranchNameValidator.IsValid("feature/a..b"));
    }

    [Fact]
    public void NormalNameAccepted()
    {
        Assert.True(BranchNameValidator.IsValid("feature/login"));
    }
}

public sealed class Bug03PluralTests
{
    [Fact]
    public void FrenchZeroIsSingular()
    {
        Assert.Equal("one", PluralRules.FrenchCategory(0));
    }

    [Fact]
    public void EnglishOneIsSingular()
    {
        Assert.Equal("one", PluralRules.EnglishCategory(1));
    }
}

public sealed class Bug04FallbackTests
{
    [Fact]
    public void FallsBackToParentCulture()
    {
        var table = new Dictionary<string, string> { ["fr"] = "Fichier" };
        Assert.Equal("Fichier", ResourceFallback.Lookup(table, "fr-CA", "File"));
    }

    [Fact]
    public void FallsBackToInvariantWithoutParent()
    {
        var table = new Dictionary<string, string> { ["fr"] = "Fichier" };
        Assert.Equal("File", ResourceFallback.Lookup(table, "de", "File"));
    }
}

public sealed class Bug05RecentFilesTests
{
    [Fact]
    public void ReaddedFileMovesToFrontWithoutDuplicate()
    {
        var recent = new RecentFiles();
        recent.Add("a");
        recent.Add("b");
        recent.Add("a");
        Assert.Equal<string>(new[] { "a", "b" }, recent.Files);
    }
}

public sealed class Bug06LayoutTests
{
    [Fact]
    public void RoundtripPreservesWidthAndHeight()
    {
        var layout = new PanelLayout("Explorer", 800, 600);
        var roundtrip = LayoutSerializer.Deserialize(LayoutSerializer.Serialize(layout));
        Assert.Equal(layout, roundtrip);
    }
}

public sealed class Bug07MipmapTests
{
    [Fact]
    public void OddSizeRoundsDown()
    {
        Assert.Equal(2, TextureScaler.MipSize(5, 1));
    }

    [Fact]
    public void MinimumSizeIsOne()
    {
        Assert.Equal(1, TextureScaler.MipSize(1, 3));
    }
}

public sealed class Bug08NormaliserTests
{
    [Fact]
    public void PeakStaysBelowFullScale()
    {
        var peak = AudioNormalizer.PeakNormalize([0.5f, -0.25f]).Max(Math.Abs);
        Assert.True(peak < 1.0f);
    }

    [Fact]
    public void SilencePassesThrough()
    {
        var result = AudioNormalizer.PeakNormalize([0f, 0f]);
        Assert.Equal(2, result.Length);
    }
}

public sealed class Bug09TurkishLookupTests : IDisposable
{
    private readonly CultureInfo _previous = CultureInfo.CurrentCulture;

    public Bug09TurkishLookupTests()
    {
        CultureInfo.CurrentCulture = new CultureInfo("tr-TR");
    }

    public void Dispose()
    {
        CultureInfo.CurrentCulture = _previous;
    }

    [Fact]
    public void NormalizeLowercasesInvariantly()
    {
        Assert.Equal("title", CultureCode.Normalize("TITLE"));
    }

    [Fact]
    public void BuildKeyUppercasesInvariantly()
    {
        Assert.Equal("TITLE", ResourceLoader.BuildKey("title"));
    }

    [Fact]
    public void LookupFindsResourceUnderTurkishCulture()
    {
        var resources = new Dictionary<string, string> { ["TITLE"] = "v" };
        Assert.Equal("v", ResourceLoader.Find(resources, "title"));
    }
}

public sealed class Bug10RootAncestorTests
{
    [Fact]
    public void MergeBaseFindsRootAncestor()
    {
        Assert.Equal("root", MergeBase.FindCommonAncestor(["root", "a"], ["root", "b"]));
    }

    [Fact]
    public void WalkIncludesRoot()
    {
        var root = new HistoryNode { Id = "root" };
        var head = new HistoryNode { Id = "a", Parent = root };
        Assert.Equal<string>(new[] { "a", "root" }, HistoryWalker.Walk(head));
    }
}

public sealed class Bug11ThemeTests
{
    [Fact]
    public void SavedThemeRestores()
    {
        var store = new SettingsStore();
        var themes = new ThemeManager(store);
        themes.SaveTheme("dark");
        Assert.Equal("dark", themes.LoadTheme());
    }

    [Fact]
    public void StoreLookupIsExact()
    {
        var store = new SettingsStore();
        store.Set("Mixed", "v");
        Assert.Equal("v", store.Get("Mixed"));
        Assert.Null(store.Get("mixed"));
    }
}

public sealed class Bug12CacheInteractionTests
{
    [Fact]
    public void RoundtripThroughWriterAndCache()
    {
        var id = HashUtil.ToHex([0xAB, 0x12]);
        var cache = new CommitCache();
        cache.Store(id, "payload");
        Assert.True(cache.TryGet(id, out var payload));
        Assert.Equal("payload", payload);
    }
}
