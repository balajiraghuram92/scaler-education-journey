# C14 — `issue-intel/`: first end-to-end run (history, C# tests, ingest, evals)

The pytest suite is green (71 passed). This is the first time the reviewer ran everything else in the README quickstart, in a clean Linux container with Python 3.12, the .NET 8 SDK, git and a fresh PostgreSQL, all with the fake model adapter.

Worked as written: `alembic upgrade head`, `python -m synthetic.generate --seed 20240917`, `python sample_repo/setup-history.py` (14 commits, `release/2023.3`, `release/2024.3`), `python -m app.ingest.run` (1,050 cases, 250 threads, 839 messages, 20 changes, 1,320 chunks; a second ingest added nothing), and both `run_g4 score` commands.

Failed:

```
dotnet test sample_repo/TesseraEditorTools.sln     does not compile   (Task 1)
dotnet test evals/fix_cases/FixCases.csproj        does not compile   (Task 1)
python -m evals.run_g1 --adapter fake              TypeError          (Task 3)
python -m evals.run_g2 --adapter fake              DetachedInstanceError   (Task 2)
python -m evals.run_g3 --adapter fake              FileNotFoundError  (Tasks 1, 4, 5)
python -m evals.run_g4 report ...                  DetachedInstanceError   (Task 2)
```

The reviewer then applied the six changes below to a throwaway copy with `sed` and ran everything again. With them, every step exits 0: the sample repo's 12 tests pass, G1, G2 and the G4 report are written, and G3 ends with `offered=10/10 flipped=10`, every fix branch verified, and all 10 backports `OPEN hidden=True`. So the tasks below are the complete list as far as the fake adapter can show; they are known to work together.

Logs in `info/muse-prompts/corrections/round17/`: `first-run/` (the failures, as on the repository's code), `probe/` (results with the changes applied; `reviewer-probe-patch.sh.txt` is the exact `sed` script, for reference only).

Paste everything below this line into Muse Code at the repository root.

---

Work only in `issue-intel/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `issue-intel/PROGRESS.md` under "C14 — end-to-end run corrections" before starting the next.

## Task 1 — the three xUnit test projects do not import `Xunit`

```
sample_repo/tests/TesseraEditorTools.Tests/ToolTests.cs(97,6): error CS0246: The type or namespace name 'Fact' could not be found
evals/fix_cases/HiddenTests.cs(152,6):                          error CS0246: The type or namespace name 'Fact' could not be found
```

`ImplicitUsings` adds the `System.*` namespaces, not `Xunit`. Neither test file has `using Xunit;` and neither project declares it. The same template is generated at run time by `evals/run_g3.py` (`HIDDEN_CSPROJ`, lines 42-58), so the hidden-test project never compiled either; that is why every fix attempt ended as `GAVE_UP` with `hidden_flipped=False` even with the scripted reference patch.

Change, the same line in three places: add a global using to the project file,

```xml
  <ItemGroup>
    <Using Include="Xunit" />
  </ItemGroup>
```

- `sample_repo/tests/TesseraEditorTools.Tests/TesseraEditorTools.Tests.csproj`
- `evals/fix_cases/FixCases.csproj`
- `evals/run_g3.py`, inside `HIDDEN_CSPROJ` (put `<Using Include="Xunit" />` in the existing `ItemGroup` next to the `Compile` item)

Do not add `using Xunit;` to the `.cs` files as well; one mechanism only.

Expected afterwards (reviewer's probe): the sample repo's tests are 12 passed; `FixCases` compiles and is 16 failed, 5 passed on `main`, which is right, because those are the hidden tests for bugs that are still planted. Say so in the README next to the `dotnet test evals/fix_cases/FixCases.csproj` line, with the numbers, so the failure is not read as a broken build.

## Task 2 — objects loaded inside `service_session()` are unusable after the block (`app/governance/rls.py`)

```
evals/run_g2.py:154  ->  app/pipeline/render.py:56   by_name = {s.stage: s.output_json for s in stages}
evals/run_g4.py:239                                  latest[(row.model, row.task_type)] = row
E  sqlalchemy.orm.exc.DetachedInstanceError: Instance <RunStage ...> is not bound to a Session; attribute refresh operation cannot proceed
```

This is a regression from the reviewer's own C9 instruction. C9 put `await session.rollback()` first in the `finally` block of `service_session` so a failed flush no longer hides the real error. But a rollback expires every object the session loaded, whatever `expire_on_commit` says. Code that reads rows inside the block and uses them after it (`render_for_viewer` in `app/pipeline/render.py:42-56`, `cmd_report` in `evals/run_g4.py:229-239`, `_seed_candidate` in `evals/run_g3.py`) then touches an expired object on a closed session.

Change in `service_session` only: detach the loaded objects before rolling back, so they keep the values they were loaded with. First statement of the `finally` block becomes `session.expunge_all()`, then `await session.rollback()`, then the `RESET` statements as now. Update the docstring to say why both lines are there.

Then search `app/` and `evals/` for the same pattern with `rls_session` (objects loaded inside `async with rls_session(...)` and read after it). `rls_session` commits through `session.begin()` with `expire_on_commit=False`, so it should be safe; confirm by reading, and list in `PROGRESS.md` every call site you checked for both context managers.

Add a database test (`ISSUEINTEL_TEST_DATABASE_URL`): load a row inside `service_session()`, leave the block, and read a column attribute of that row; it must not raise. Keep the existing C9 behaviour test (the original error is not replaced by `PendingRollbackError`).

## Task 3 — `await` inside a generator passed to `sum()` (`evals/run_g1.py:158`)

```
bad = sum(1 for aid in visible if not await _entitled(acls[aid], ent))
E  TypeError: 'async_generator' object is not iterable
```

A generator expression that contains `await` is an async generator, and `sum()` cannot consume one. `_entitled` (line 129) does no I/O.

Change: make `_entitled` a plain `def` and drop the `await` at line 158. Check for any other caller of `_entitled` and for the same construct (`sum(`, `any(`, `all(`, `min(`, `max(`, `sorted(` over a generator containing `await`) anywhere in `app/` and `evals/`; list what you find.

## Task 4 — the sandbox path is relative to two different directories (`app/agents/sandbox.py`)

```
FileNotFoundError: [Errno 2] No such file or directory: 'sandboxes/fix-TES-0001-1'
  app/agents/gate.py:59  dotnet_test  ->  app/agents/sandbox.py:21  run_cmd(cwd=worktree)
```

`settings.sandbox_root` defaults to the relative path `sandboxes`. `create_sandbox` (lines 43-51) passes `str(path)` to `git worktree add` with `cwd=repo`, so git creates the worktree at `sample_repo/sandboxes/fix-…`. The returned `Sandbox.path` is still the relative `sandboxes/fix-…`, and every later `run_cmd(cwd=sandbox.path)` resolves it against the process's working directory, where nothing exists.

Change in `create_sandbox`: resolve the root to an absolute path before anything else (`root = root.resolve()`), so git and every later command agree. Nothing else in the function changes.

`app/agents/fix_loop.py:97-99` and `app/agents/backport.py:35-37` both carry a workaround that prefixes `issue-intel/` when that directory exists in the working directory. With an absolute root the two call sites still behave as before; leave them, but say in `PROGRESS.md` what directory the sandboxes end up in when the process is started from `issue-intel/` and when it is started from the repository root, and add `sandboxes/` to `issue-intel/.gitignore` if it is not already ignored.

Add a unit test with a temporary git repository (git is available to the reviewer; mark the test to skip when `git` is not on `PATH`): `create_sandbox` with a relative root returns an absolute `path` that exists, and `remove_sandbox` removes it.

## Task 5 — the benchmark's verification step creates a nested directory without its parent (`evals/run_g3.py`)

```
evals/run_g3.py:164  branch_ok = await hidden_passing(sandbox.path, bug["test_class"], hidden_dir / "verify")
evals/run_g3.py:72   proj_dir.mkdir(exist_ok=True)
E  FileNotFoundError: [Errno 2] No such file or directory: '/tmp/g3bench-…/bug01/verify/hidden'
```

`hidden_passing` builds `tmp / "hidden"` and calls `mkdir(exist_ok=True)`. For the first call `tmp` exists; for the verification call (`hidden_dir / "verify"`) and the backport call (`tmp / f"bp-{row.id}"`, line 207) it does not.

Change at line 72: `proj_dir.mkdir(parents=True, exist_ok=True)`.

## Task 6 — full-text search requires every word of the query to match (`app/search/hybrid.py`)

Retrieval numbers from G1 on the generated corpus (fake adapter; the vector column is not meaningful with fake embeddings, the full-text column is):

```
                         as written     any-word query (probe)
fulltext recall@5          0.003            0.051
fulltext recall@10         0.003            0.115
fulltext MRR               0.022            0.055
regression change hit@5    0.00             0.30
```

`_fulltext` (lines 25-37) uses `plainto_tsquery('english', :q)`, which joins every term with AND. The callers pass a whole ticket title and body as the query (`evals/run_g1.py:74-76`, and the similar-case search in the app), so a chunk only matches when it contains every word of the ticket. A duplicate report, written in different words, never does.

Change in `_fulltext` only: build the query so that any term may match, and keep ordering by `ts_rank` so chunks that share more terms rank higher. The reviewer's probe used

```sql
replace(plainto_tsquery('english', :q)::text, '&', '|')::tsquery
```

in both places `plainto_tsquery('english', :q)` appears. Use that or an equivalent; if you choose another form, say why. Check the behaviour for a query with no indexable words (all stop words or empty): it must return no rows, not raise.

The numbers are still low. Part of that is the metric (the won't-fix queries have up to 49 relevant cases, so recall@10 cannot be high) and part may be real. Do not tune further in this prompt. In `PROGRESS.md`, write down what you think limits full-text recall on this corpus after the change (chunking, `ts_rank` normalisation, the query text used), as notes for the reviewer.

Update or add a database test: two chunks, one sharing most but not all words with the query and one sharing none; the first is returned and the second is not.

## Finish

End with a short report: each task done or not done, files changed, the lists Tasks 2 and 3 ask for, the two directories Task 4 asks about, your notes for Task 6, and anything that could not be done as written. Never say a test or check passes; you have not run it.
