# STRICT PROMPT — Add a Spring Boot runtime profile to the exercise sandbox, additively

Read this entire document before touching any file. This adds a **second** exercise runner
profile alongside the existing one. The existing plain-Java profile, its Docker image, and every
exercise already using it (`hotel-*`, `tictactoe-*`, and whatever the two Parking Lot exercises
from the companion prompt add) must remain **byte-for-byte unchanged in behavior**. This is
additive infrastructure, not a migration or a replacement.

## Why

Scaler's course moves to real Spring Boot + JPA partway through (confirmed directly from the real
class material already in this repo — see `info/.notes/scaler-raw-notes/hackmd/50-H1QaIsMOGg.md`
onward, and the two real Splitwise exercises already sitting at
`exercises/practice-pool/java/splitwise-manage-group-members/` and
`splitwise-create-delete-group/`, both genuinely using `@Controller`, `@Autowired`, JPA
`@MappedSuperclass`/`@Id`, and Lombok `@Data`). The current sandbox cannot run this content at
all — not just because its `pom.xml` is leaner, but because **the runner image
(`runner/java/Dockerfile`, `FROM maven:3.9.9-eclipse-temurin-11`) is Java 11, and Spring Boot 3.x
requires Java 17 minimum.** This is a hard version floor, not a dependency-weight problem.

## Required reading before writing anything

- `runner/java/Dockerfile` and `runner/java/run.sh` — the exact existing runner image and
  invocation (`mvn --batch-mode --no-transfer-progress test`). The new image reuses this same
  `run.sh` unchanged — it's already framework-agnostic.
- `api/Options/ExerciseExecutionOptions.cs` — the current single global `RunnerImage` string,
  `MaxExecutionSeconds` (120s default), `MemoryLimitBytes` (~768MB), `MavenCacheVolume`.
- `api/Services/Exercises/LocalDockerExerciseRunner.cs`, specifically `RunAsync` (which container
  config it builds, including the `Mounts`/`HostConfig`) and `GetExecutionTimeout` (which reads
  `definition.Manifest.Runtime.TimeoutSeconds`, capped by `_options.MaxExecutionSeconds`).
- `api/Services/Exercises/ExerciseManifestModels.cs` — confirm the `Runtime.Profile` field
  already exists on the manifest (it does, currently unused by the runner — every existing
  `exercise.json` already sets `"profile": "java-maven"`, but nothing branches on it today).
- `docker-compose.yml` line with `ExerciseExecution__RunnerImage:
  ${EXERCISE_RUNNER_IMAGE:-neuralascent-java-runner:dev}` — confirms the runner image is built
  manually (no `build:` block in compose) and referenced by tag via an env var. The new image
  follows the identical pattern, under a new env var.

## Part 1 — New runner image, not a modification of the existing one

Create `runner/java-spring/Dockerfile`:
```dockerfile
FROM maven:3.9.9-eclipse-temurin-17

WORKDIR /workspace

COPY run.sh /usr/local/bin/neuralascent-java-run
RUN chmod 0755 /usr/local/bin/neuralascent-java-run

ENTRYPOINT ["/usr/local/bin/neuralascent-java-run"]
```
Copy `runner/java/run.sh` to `runner/java-spring/run.sh` unchanged — `mvn test` doesn't care
whether the project is Spring Boot or plain Java, the image's JDK version is what matters.

Do **not** modify `runner/java/Dockerfile` or `runner/java/run.sh` at all.

## Part 2 — Per-profile image resolution (additive, with a safe fallback)

In `api/Options/ExerciseExecutionOptions.cs`, add:
```csharp
public Dictionary<string, string> RunnerImagesByProfile { get; set; } = new();
```
Keep the existing `RunnerImage` property exactly as-is — it becomes the fallback default for any
manifest whose `Runtime.Profile` isn't a key in `RunnerImagesByProfile`.

In `api/Services/Exercises/LocalDockerExerciseRunner.cs`, change `RunAsync` (and
`EnsureRunnerImageAsync`, which currently hard-codes `_options.RunnerImage`) to resolve the image
as: look up `workspace.Definition.Manifest.Runtime.Profile` in `_options.RunnerImagesByProfile`;
if found, use that image; otherwise, fall back to `_options.RunnerImage` (today's exact existing
behavior, unchanged for every current exercise since none of them will match a new dictionary key
unless explicitly given the new profile string).

In `docker-compose.yml`, add the new image reference alongside the existing one, following the
identical env-var-with-default pattern:
```yaml
ExerciseExecution__RunnerImagesByProfile__java-maven-spring: ${EXERCISE_RUNNER_IMAGE_SPRING:-neuralascent-java-spring-runner:dev}
```
(Confirm the exact ASP.NET Core configuration binding syntax for a nested dictionary key with a
hyphenated key name works as written — hyphens in the profile string may need the dictionary key
quoted differently in the env var name; verify against how ASP.NET Core binds `Dictionary<string,string>`
from colon/double-underscore env var paths, and adjust the key naming if `java-maven-spring`
causes a binding issue — an underscore-only profile name like `java_maven_spring` is an acceptable
fallback if hyphens prove problematic in the env var path.)

## Part 3 — Timeout and memory headroom for Spring Boot's real cold-start cost

Spring context initialization plus (for JPA-backed exercises) an H2 schema bootstrap adds real,
unavoidable startup latency beyond what a plain JUnit run has — separate from Maven dependency
download time, which the existing shared `MavenCacheVolume` already absorbs after a first run.

- Raise `ExerciseExecutionOptions.MaxExecutionSeconds` from 120 to 240 (global ceiling — this
  only raises the *cap*, it does not change behavior for exercises whose own
  `runtime.timeoutSeconds` is already well under 120).
- For the new Spring-profile exercises specifically (not existing ones), use a
  `runtime.timeoutSeconds` of 60–90 in their own `exercise.json` — enough headroom for Spring
  context boot + H2 init + the actual test assertions, still comfortably under the raised 240s
  ceiling.
- Raise `MemoryLimitBytes` from ~768MB (`805_306_368`) to at least 1.5GB
  (`1_610_612_736`) — a Spring context plus an embedded H2 instance genuinely needs more headroom
  than a bare JUnit run. Apply this as a global option change (this repo doesn't currently support
  per-profile memory limits — do not build that out unless it's trivially easy; a single, slightly
  more generous global limit is the pragmatic fix here, not a new per-profile resource system).

## Constraints

- Every existing exercise (`hotel-*`, `tictactoe-*`, and the Parking Lot ones from the companion
  wiring prompt) must continue to resolve to the exact same runner image and continue passing
  exactly as before — this is the regression bar. If you cannot verify this, say so explicitly.
- Do not touch `runner/java/Dockerfile` or `runner/java/run.sh`.
- Do not wire the two real Splitwise exercises into `exercises/java/java-lld/` in this pass — this
  prompt is infrastructure only. Content wiring for Splitwise is separate, deliberately scoped
  work once this sandbox extension is confirmed working.
- Do not build a fully generic multi-profile resource-limit system (per-profile memory/CPU/pids)
  unless it falls out naturally from the change above — a second image plus a raised global
  timeout/memory ceiling is the right amount of infrastructure for what's needed right now.

## Critical constraint — the same honesty discipline as the last prompt

Actually build the new image (`docker build -t neuralascent-java-spring-runner:dev
runner/java-spring/`) and confirm it builds successfully. If possible, actually run a minimal
smoke test — a trivial Spring Boot `@SpringBootTest`-free JUnit test inside a throwaway project
using the new image — and confirm it passes, and report the *real* command output. If your
environment cannot run Docker builds, state that explicitly and clearly instead of asserting the
image works.

## Output expectations

Report: the new Dockerfile/run.sh content, the exact diff to `ExerciseExecutionOptions.cs` and
`LocalDockerExerciseRunner.cs`, the `docker-compose.yml` addition, and either real build/smoke-test
output or an explicit statement that it could not be verified in your environment.

## Verification checklist (self-check before returning the result)

1. `runner/java/Dockerfile` and `runner/java/run.sh` are byte-for-byte unchanged (`git diff` shows
   zero touches to either file).
2. Every existing `exercise.json` (`hotel-*`, `tictactoe-*`) still resolves to
   `neuralascent-java-runner:dev` (the untouched fallback path), not the new image.
3. The new `runner/java-spring/Dockerfile` builds successfully (real output, not asserted).
4. `RunnerImagesByProfile` defaults to an empty dictionary, so a deployment that never sets the
   new env var behaves identically to today (fallback to `RunnerImage` for every exercise).
5. `MaxExecutionSeconds` and `MemoryLimitBytes` changes are the only global option changes — no
   other option values were altered.
