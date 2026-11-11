# Tessera Editor Tools (sample repo)

Small C# solution the fix agent (G3) works on. Four modules: `VersionControl`,
`Localization`, `UiState`, `AssetImport`. The on-disk tree is the clean base;
`setup-history.py` turns it into a git repo with the 12 planted bugs.

Build history (NOT RUN here; run from this directory):

```powershell
python setup-history.py
dotnet test TesseraEditorTools.sln
```
