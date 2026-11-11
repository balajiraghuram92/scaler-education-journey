namespace TesseraEditorTools.AssetImport;

public static class AudioNormalizer
{
    public static float[] PeakNormalize(float[] samples)
    {
        var peak = 0f;
        foreach (var s in samples)
        {
            peak = Math.Max(peak, Math.Abs(s));
        }
        if (peak <= 0f)
        {
            return (float[])samples.Clone();
        }
        var gain = 0.99f / peak;
        return samples.Select(s => s * gain).ToArray();
    }
}
