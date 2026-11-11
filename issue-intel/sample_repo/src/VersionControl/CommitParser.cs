namespace TesseraEditorTools.VersionControl;

public sealed record Trailer(string Key, string Value);

public static class CommitParser
{
    public static List<Trailer> ParseTrailers(IEnumerable<string> lines)
    {
        var trailers = new List<Trailer>();
        foreach (var line in lines)
        {
            var idx = line.IndexOf(':');
            if (idx <= 0)
            {
                continue;
            }
            var key = line[..idx].Trim();
            var value = line[(idx + 1)..].Trim();
            trailers.Add(new Trailer(key, value));
        }
        return trailers;
    }
}
