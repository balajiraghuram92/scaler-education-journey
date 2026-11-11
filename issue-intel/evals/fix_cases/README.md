# Fix cases (hidden from the app and the fix agent)

One entry per planted bug in `bugs.json`: the symptom, module, files touched,
in/out-of-scope flag, branches the bug is present on, and the hidden-test
class name in `HiddenTests.cs`.

- `bugNN.patch` — reference fix, buggy tree -> clean tree, applied from
  `sample_repo/`. `setup-history.py` reverse-applies these to introduce the
  bugs (bug12 in two per-file commits via `git apply -R --include=...`).
- `HiddenTests.cs` — fails on `main` with the bugs, passes with the fix.
  Never referenced by `sample_repo/`; `app/` is forbidden from reading this
  folder (`tests/test_import_boundary.py`).

Run (NOT RUN here):

```powershell
dotnet test evals/fix_cases/FixCases.csproj
```
