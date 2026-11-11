namespace TesseraEditorTools.VersionControl;

public static class HashUtil
{
    public static string ToHex(byte[] bytes)
    {
        return Convert.ToHexString(bytes).ToLowerInvariant();
    }
}
