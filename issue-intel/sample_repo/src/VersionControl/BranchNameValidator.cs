namespace TesseraEditorTools.VersionControl;

public static class BranchNameValidator
{
    public static bool IsValid(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            return false;
        }
        if (name.Contains(".."))
        {
            return false;
        }
        return name.All(c => char.IsLetterOrDigit(c) || c is '/' or '-' or '_' or '.');
    }
}
