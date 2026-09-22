# STRICT PROMPT — Fix live exercise-grading 503 caused by Docker socket permission denial

Read this entire document before touching any file. This fixes a **confirmed, live, production-breaking
bug**: the real exercise-grading feature (`POST /api/exercises/{exerciseId}/run`) currently returns
`503 Exercise runner unavailable` for every single submission, on every exercise, with zero exception
detail logged anywhere. This was diagnosed by hand, live, against the running `api` container — not
guessed. Do not treat this as theoretical; it is currently broken end-to-end.

## Root cause, confirmed by direct reproduction

`docker-compose.yml` bind-mounts the host's Docker socket into the `api` container:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```
and `api/Options/ExerciseExecutionOptions.cs` has `DockerEndpoint` defaulting to
`unix:///var/run/docker.sock` — the container connects to that same bind-mounted path internally.

On this deployment, the actual running container engine is **rootless Podman** (confirmed via
`docker context show` → `default`, `DOCKER_HOST=unix:///run/user/1000/podman/podman.sock` in the host
user's shell environment, and `docker info` reporting `Podman Engine`). The host user (`rbalaji`, uid
1000) is a member of the host's `docker` group and can read/write `/var/run/docker.sock` directly. But
rootless Podman does **not** propagate the host user's supplementary groups (like `docker`) into
containers by default. Reproduced directly:

```
docker exec studytracker-api id
→ uid=0(root) gid=0(root) groups=0(root)

docker exec studytracker-api ls -la /var/run/docker.sock
→ srw-rw---- 1 nobody nogroup 0 ... /var/run/docker.sock   (ownership doesn't map cleanly into the container's user namespace)

docker exec studytracker-api curl -v --unix-socket /var/run/docker.sock http://localhost/version
→ * Immediate connect fail for /var/run/docker.sock: Permission denied
```

So `LocalDockerExerciseRunner`'s `DockerClient` can never reach the daemon at all. Every call into
`EnsureRunnerImageAsync`/`CreateContainerAsync` throws (caught and rethrown as
`ExerciseRunnerUnavailableException` in `api/Services/Exercises/LocalDockerExerciseRunner.cs`, lines
~118–187), which the endpoint (`api/Endpoints/ExerciseEndpoints.cs`) correctly maps to a `503` — the
HTTP-layer code is not the bug. The infrastructure wiring is.

## Required reading before writing anything

- `docker-compose.yml` — the `api` service's `volumes:` block (the docker.sock bind mount) and its
  existing `environment:` block (to match the exact env-var-with-default interpolation style already
  used throughout this file, e.g. `${EXERCISE_RUNNER_IMAGE:-neuralascent-java-runner:dev}`).
- `.env.example` — the existing documented env vars, to match style/placement for the new one being
  added.
- `api/Options/ExerciseExecutionOptions.cs` — confirm `DockerEndpoint` stays
  `unix:///var/run/docker.sock` (the path *inside* the container does not change — only which host path
  gets bind-mounted to it changes).
- `api/Services/Exercises/ExerciseService.cs`, the `ExecuteAsync` method (lines ~33–86) — confirm the
  `try/finally` block currently has **no `catch` clause at all**, meaning any exception from
  `_runner.RunAsync(...)` propagates silently with zero logging before the endpoint converts it to a
  `503`. This is why the root cause was invisible in `docker logs studytracker-api` and had to be found
  by manually exec'ing into the container.
- `api/Endpoints/ExerciseEndpoints.cs` — confirm the existing `catch (ExerciseRunnerUnavailableException)`
  block (already correct, do not change its behavior, only ensure the exception is logged before it gets
  there).

## Part 1 — Make the Docker socket bind-mount portable across host container engines

In `docker-compose.yml`, change the `api` service's docker socket volume line from the hardcoded:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```
to:
```yaml
volumes:
  - ${EXERCISE_DOCKER_SOCKET_PATH:-/var/run/docker.sock}:/var/run/docker.sock
```
This lets a rootless-Podman host point at its own real socket (e.g.
`/run/user/1000/podman/podman.sock`) via `.env`, while defaulting to the standard rootful-Docker path
(`/var/run/docker.sock`) for any host — including EC2 later — that doesn't need to override it.

Also add, immediately after that volumes line in the same `api` service, a `group_add` entry so the
container process carries whatever GID actually owns the mounted socket on rootless hosts (this is the
standard, documented fix for rootless-Podman DooD group-membership propagation — it is a no-op on hosts
where the default GID 0 already has access, e.g. rootful Docker):
```yaml
    group_add:
      - "${EXERCISE_DOCKER_SOCKET_GID:-0}"
```

In `.env.example`, add both new variables near the existing `ExerciseExecution`-related documentation
(if none exists yet, add them near `EXERCISE_RUNNER_IMAGE`/similar entries), with comments explaining
they're only needed for rootless-Podman-style hosts:
```
# Only needed on rootless-Podman hosts (e.g. local WSL2 dev). Leave unset/default on real Docker hosts (e.g. EC2).
EXERCISE_DOCKER_SOCKET_PATH=/var/run/docker.sock
EXERCISE_DOCKER_SOCKET_GID=0
```

**Do not hardcode this machine's specific GID (106) anywhere in `docker-compose.yml` or
`.env.example`.** The real numeric value belongs only in the user's own untracked `.env` file, determined
on their own machine (instructions for that are in the Verification section below — this is something
the user or you must run for real, not something to guess).

## Part 2 — Log the actual exception instead of swallowing it silently

In `api/Services/Exercises/ExerciseService.cs`, add a `catch` block to the existing `try/finally` in
`ExecuteAsync` (currently `try { ... } finally { ... }` with no `catch` at all) that logs the exception
with full detail before rethrowing, so any future runner failure is diagnosable from
`docker logs studytracker-api` alone, without needing to manually exec into the container:

```csharp
catch (Exception ex)
{
    _logger.LogError(
        ex,
        "Exercise execution {RunId} for {ExerciseId} failed.",
        runId,
        exerciseId);
    throw;
}
```

Place it between the existing `try { ... }` block and the existing `finally { ... }` block. Do **not**
change what exception types propagate to the endpoint, do **not** swallow the exception (it must still
`throw;` so `ExerciseEndpoints.cs`'s existing `catch` clauses keep working exactly as before) — this is
purely adding a log line, not changing control flow or the HTTP response shape at all.

## Constraints

- Do not change `ExerciseExecutionOptions.DockerEndpoint`'s default value (`unix:///var/run/docker.sock`)
  — that's the path *inside* the container, which stays constant; only the host-side bind-mount source
  changes.
- Do not touch `LocalDockerExerciseRunner.cs`'s exception-handling logic (lines ~118–187) — those
  `ExerciseRunnerUnavailableException` throws are already correct and must keep working identically.
- Do not touch `ExerciseEndpoints.cs` — its existing catch blocks are correct as-is.
- Do not change any other `docker-compose.yml` service's volumes or environment.
- Do not remove or rename the existing `ExerciseExecution__DockerEndpoint` environment line in
  `docker-compose.yml`.

## Critical constraint — actually verify this live, do not just assert it

This bug was found by a real, live `POST /api/exercises/java-lld-hotel-add-rooms/run` submission
returning `503`. The fix is not verified until the **exact same kind of live submission** succeeds.

1. Determine the real GID that owns the actual running container engine's socket on this specific
   machine (do not guess — run it for real):
   ```bash
   # if using rootless Podman (check: docker context show; docker info | grep -i podman):
   stat -c '%g' /run/user/$(id -u)/podman/podman.sock
   ```
   Set `EXERCISE_DOCKER_SOCKET_PATH` and `EXERCISE_DOCKER_SOCKET_GID` in the real (untracked) `.env`
   file to match — for a rootless-Podman host, `EXERCISE_DOCKER_SOCKET_PATH` should point at that same
   `podman.sock` path, and `EXERCISE_DOCKER_SOCKET_GID` should be `0` in that case (a rootless-Podman
   socket is typically owned by the invoking user directly, not a `docker` group, so the fix there is
   really the socket **path** override; the `group_add` override matters more for a rootful
   `/var/run/docker.sock` owned by a `docker` group on hosts where that's the case) — reason about which
   of the two env vars actually needs overriding based on what `ls -la` on the real socket shows on this
   specific machine, rather than blindly setting both.
2. Recreate the `api` container: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   --force-recreate api`.
3. From inside the container, confirm the socket is now reachable:
   ```bash
   docker exec studytracker-api curl -s --unix-socket /var/run/docker.sock http://localhost/version
   ```
   This must return real JSON (a version payload), not a connection error.
4. Submit a real exercise run against the live endpoint using the **solution** files for
   `java-lld-hotel-add-rooms` (its editable files are `InMemoryRoomRepository.java`,
   `InMemoryUserRepository.java`, `RoomServiceImpl.java` — read their real content from
   `exercises/java/java-lld/applied-machine-coding/hotel-add-rooms/solution/...` and build the POST body
   as `{"files":[{"path":"...","content":"..."},...]}` matching `ExerciseSubmissionRequest`'s shape in
   `api/Models/ExerciseDtos.cs`) against `POST http://127.0.0.1:5000/api/exercises/java-lld-hotel-add-rooms/run`
   with the `x-api-key` header set to this deployment's real `API_KEY` value. Paste the **real** JSON
   response — it must show `"status":"success"`, `"passed":true`, and a `summary` with `Total: 3,
   Passed: 3, Failed: 0, Errors: 0` (matching the 3 evidence entries in that exercise's
   `exercise.json`).
5. If you cannot actually run these commands in your environment, say so explicitly and clearly instead
   of asserting the fix works.

## Output expectations

Report: the exact diff to `docker-compose.yml`, the exact diff to `.env.example`, the exact diff to
`ExerciseService.cs`, the real numeric GID/socket path you determined for this machine and what you set
in the real `.env` (do not paste `.env` itself if it contains secrets — just state the two exercise-related
values), and the real JSON response from the live exercise submission in step 4 above.

## Verification checklist (self-check before returning the result)

1. `docker-compose.yml`'s `api` service volumes line uses `${EXERCISE_DOCKER_SOCKET_PATH:-/var/run/docker.sock}`,
   not a hardcoded path.
2. `docker-compose.yml`'s `api` service has a new `group_add` entry using
   `${EXERCISE_DOCKER_SOCKET_GID:-0}`.
3. `.env.example` documents both new variables with a comment explaining they're rootless-Podman-only.
4. `ExerciseService.ExecuteAsync` now logs the exception via `_logger.LogError` before it propagates,
   and still `throw;`s the original exception unchanged.
5. `docker exec studytracker-api curl -s --unix-socket /var/run/docker.sock http://localhost/version`
   returns real JSON, not a connection error.
6. A real live POST to `/api/exercises/java-lld-hotel-add-rooms/run` with the exercise's real solution
   files returns `"passed":true` with `3/3` tests passing — pasted verbatim, not summarized.
7. Re-run the exact same POST a second time with the **starter** files for the same exercise's editable
   set (from `exercises/java/java-lld/applied-machine-coding/hotel-add-rooms/starter/...`) and confirm
   it returns `"passed":false` — proving the fix didn't accidentally make grading always report success
   regardless of submitted content.
