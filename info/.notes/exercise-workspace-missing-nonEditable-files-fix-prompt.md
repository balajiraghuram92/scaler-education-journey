# STRICT PROMPT — Fix exercise grading always failing to compile: non-editable files never copied into the workspace

Read this entire document before touching any file. This is a second, separate, confirmed live bug in
the exercise-grading pipeline, found immediately after fixing the Docker-socket permission bug (see
`info/.notes/exercise-runner-docker-socket-permission-fix-prompt.md`, already applied). With that fix
in place, the pipeline runs a real container for the first time ever — and every single submission,
including a submission of the exercise's own **real reference solution**, fails with a Maven
**compilation failure**, not a test failure. This is the first time this feature has ever been exercised
end-to-end; it has never worked, for any exercise, until this is fixed.

## Root cause, confirmed by direct reproduction

A real live POST to `http://127.0.0.1:5000/api/exercises/java-lld-hotel-add-rooms/run`, submitting the
exact solution content for that exercise's 3 editable files
(`InMemoryRoomRepository.java`, `InMemoryUserRepository.java`, `RoomServiceImpl.java`, read verbatim
from `exercises/java/java-lld/applied-machine-coding/hotel-add-rooms/solution/...`), returned:

```json
{"status":"compilationFailure","passed":false, ...
 "diagnostics":{"compilerOutput":"... package com.example.addroomshotelmanagement.models does not exist ...
 cannot find symbol: class RoomRepository ... cannot find symbol: class Room ..."}}
```

Reading `api/Services/Exercises/ExerciseWorkspaceBuilder.cs`'s `BuildAsync` method shows exactly why:
it copies **only three things** into the built Maven workspace — `pom.xml`, the test suite file, and the
submitted (editable-only) files from the request. It never copies any of the exercise's **non-editable**
reference files (models, DTOs, exceptions, repository/service interfaces, controllers) at all. Since
`ExerciseSubmissionValidator.cs` correctly *rejects* a client submission that includes non-editable
paths (by design — the client should only ever submit the files it's allowed to edit), those files must
be merged in server-side from the exercise's own directory tree. That merge step is simply missing.

This means every exercise, for every submission (even a perfect one), has always failed to compile,
because the vast majority of a typical exercise's source files (its models, DTOs, exceptions,
interfaces) were never being placed in the Maven workspace at all.

## Required reading before writing anything

- `api/Services/Exercises/ExerciseWorkspaceBuilder.cs` — the full `BuildAsync` method (currently lines
  17–66). Note the existing pattern for `pomSource`/`testSource`→destination copying — the fix should
  follow the exact same style (trusted-path construction, `Directory.CreateDirectory` before
  `File.Copy`).
- `api/Services/Exercises/ExerciseManifestModels.cs` — `ExerciseFileManifest` (has `Path` and `Editable`
  bool) and `ExerciseDefinition.Manifest.Files` (the full `List<ExerciseFileManifest>`, both editable and
  non-editable entries) and `ExerciseDefinition.ExerciseRoot` (the exercise's own directory, containing
  `starter/`, `solution/`, `tests/`, `pom.xml`).
- `api/Services/Exercises/ExerciseMetadataService.cs`, line ~54 — confirms `starter` is the established,
  already-used canonical source directory name for non-editable file content elsewhere in this codebase
  (`starterRoot = ExercisePathRules.ResolveInside(definition.ExerciseRoot, "starter")`) — use the same
  `starter/` source for this fix, for consistency.
- `exercises/java/java-lld/applied-machine-coding/hotel-add-rooms/` — a real exercise directory to
  manually cross-check the fix against (its `starter/src/main/java/.../models/Room.java` etc. must
  exist and match the `Path` values declared as non-editable in its `exercise.json`).

## The fix

In `api/Services/Exercises/ExerciseWorkspaceBuilder.cs`, inside `BuildAsync`, immediately after the
existing test-file copy block (after `File.Copy(testSource, testDestination);`) and before the
`foreach (var file in submission.Values)` loop that writes the submitted editable files, add a loop that
copies every non-editable file declared in the manifest from the exercise's `starter/` directory into
the workspace:

```csharp
foreach (var fileManifest in definition.Manifest.Files.Where(f => !f.Editable))
{
    var nonEditableSource = ExercisePathRules.ResolveInside(definition.ExerciseRoot, $"starter/{fileManifest.Path}");
    var nonEditableDestination = ExercisePathRules.ResolveInside(workspacePath, fileManifest.Path);
    Directory.CreateDirectory(Path.GetDirectoryName(nonEditableDestination)!);
    File.Copy(nonEditableSource, nonEditableDestination);
}
```

Place this so the order is: pom.xml copy → test file copy → **non-editable files copy (new)** →
submitted editable files copy. The editable-files loop must stay last so a submitted file always wins if
its path were ever to collide with something already placed (it shouldn't, since
`ExerciseSubmissionValidator` already guarantees submitted paths are exactly the editable set and
non-editable paths are a disjoint set from the manifest, but keeping submission last preserves that
invariant defensively).

## Constraints

- Do not change `ExerciseSubmissionValidator.cs` — it is already correct (client submits editable files
  only; this bug is purely about the server-side merge step that was missing).
- Do not change what source directory is used for editable files (those still come from the submitted
  request content, never from `starter/` or `solution/`).
- Do not use `solution/` as the source for non-editable files — use `starter/`, matching the existing
  precedent in `ExerciseMetadataService.cs`. (Non-editable file content is identical between `starter/`
  and `solution/` by the existing exercise-authoring contract, but `starter/` is the established
  convention for anything served as part of what a learner works against.)
- Do not change the exception-handling (`catch { DeleteWorkspace(...); throw; }`) wrapping this method —
  a `File.Copy` failure for a missing non-editable file should still surface as today (an
  `ExerciseInfrastructureException`-style failure via whatever currently happens when `File.Copy` throws
  `FileNotFoundException` here — do not add new special-case handling for that, the existing catch-all
  is sufficient and correct).

## Critical constraint — verify with a real live submission, not a unit test claim

This bug was found and must be fixed via the same method: a real live HTTP submission against the
actually-running `api` container, not a code-review claim.

1. Rebuild and recreate the `api` container so the fix is live:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml build api
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate api
   ```
2. Submit the exact same **solution** payload as before for `java-lld-hotel-add-rooms` (its 3 editable
   files' real solution content) to `POST http://127.0.0.1:5000/api/exercises/java-lld-hotel-add-rooms/run`
   with the `x-api-key` header. Paste the full real JSON response. It must now show
   `"status":"success"`, `"passed":true`, and `"summary":{"total":3,"passed":3,"failed":0,"errors":0,"skipped":0}`
   — matching the exercise's 3 evidence entries.
3. Submit the same exercise's **starter** content for the same 3 files (unimplemented TODO stubs) to the
   same endpoint. Paste the full real JSON response. It must now show either `"status":"testFailure"`
   with some tests failing (if the starter stubs compile but don't satisfy the logic) — it must **not**
   be a `"compilationFailure"` anymore, since the starter files themselves are known to compile (this was
   independently verified earlier via direct `mvn test` runs of the starter to confirm it compiles).
4. Do the same two checks (solution → success, starter → not a compilation failure) for at least one
   more exercise that has multiple non-editable files, e.g. `java-lld-generate-parking-ticket`, to
   confirm the fix isn't accidentally specific to `hotel-add-rooms`'s particular file layout.
5. If you cannot run these commands live, say so explicitly instead of asserting the fix works.

## Output expectations

Report: the exact diff to `ExerciseWorkspaceBuilder.cs`, and the four real JSON responses from step 2–4
above, pasted verbatim (not summarized, not truncated to just the top-level `status` field — include the
full `summary` and `evidence` arrays so the pass/fail counts are visible).

## Verification checklist (self-check before returning the result)

1. The new non-editable-file-copy loop is placed between the test-file copy and the submitted-files
   loop, exactly as specified.
2. It reads `definition.Manifest.Files.Where(f => !f.Editable)`, not some other filter.
3. It sources from `starter/{path}`, not `solution/{path}`.
4. A real live submission of `java-lld-hotel-add-rooms`'s real solution now returns
   `"passed":true, "summary":{"total":3,"passed":3,...}` — pasted verbatim.
5. A real live submission of `java-lld-hotel-add-rooms`'s starter content no longer returns
   `"status":"compilationFailure"`.
6. The same solution/starter check passes for a second exercise with a different file layout.
7. `ExerciseSubmissionValidator.cs` is untouched (`git diff` shows no changes to that file).
