# Neuralascent Java Maven Runner

This image is the Phase 1 generic Java execution primitive. It knows only how
to run a Maven project mounted at `/workspace`; it contains no exercise source,
tests, golden solutions, API code, Docker socket, or repository credentials.

## Build the runner

From the repository root:

```bash
docker build -t neuralascent-java-runner:dev runner/java
```

The production build targets `linux/arm64` and publishes the runner at
`ghcr.io/balajiraghuram92/neuralascent-java-runner:<git-sha>`. Verify the base
image with Buildx before the first production release:

```bash
docker buildx build --platform linux/arm64 --load \
  -t neuralascent-java-runner:arm64 \
  -f runner/java/Dockerfile runner/java
docker image inspect --format '{{.Os}}/{{.Architecture}}' \
  neuralascent-java-runner:arm64
```

The base image is `maven:3.9.9-eclipse-temurin-11-alpine`, which provides Maven
and a Java 11 JDK matching the supplied exercise POM while using Alpine Linux
for a smaller runner footprint. The exercise is pure Java/JUnit, so it does not
depend on native libraries. If this ARM64 build fails in the validation
environment, replace it with the smallest multi-architecture Temurin Java 11
Maven image without changing the Maven or Java versions.

## Canonical exercise

The Point/ThreedPoint fixture lives at:

```text
exercises/java/java-lld/oop-3/point-threedpoint/
```

The exercise package separates learner-visible starter files, trusted tests,
and the golden solution. The final ZIP supplied an artifact ID of
`Lecture1_Asgn1`, while the starter ZIP used `Lecture3_Asgn1`; the canonical
POM keeps the final ZIP's Maven semantics and uses one shared POM for both
variants.

## Development harness

Make the harness executable once in WSL:

```bash
chmod +x scripts/run-java-exercise.sh scripts/validate-java-exercise.sh
```

Build the runner, then run the golden solution:

```bash
docker build -t neuralascent-java-runner:dev runner/java
KEEP_WORKSPACE=1 scripts/run-java-exercise.sh \
  java-lld-oop3-point-threedpoint solution
```

Run the incomplete starter:

```bash
KEEP_WORKSPACE=1 scripts/run-java-exercise.sh \
  java-lld-oop3-point-threedpoint starter
```

The harness also accepts a third argument containing a custom source root. This
is used only by development validation fixtures; the POM and tests still come
from the canonical exercise package:

```bash
scripts/run-java-exercise.sh \
  java-lld-oop3-point-threedpoint fixture /tmp/source-root
```

Run all Phase 1 acceptance scenarios, including compile failure, behavioral
failure, and timeout handling:

```bash
JAVA_RUNNER_TIMEOUT=120 JAVA_EXERCISE_TIMEOUT=20 \
  scripts/validate-java-exercise.sh
```

`JAVA_RUNNER_TIMEOUT` is the larger first-run allowance for Maven dependency
downloads. `JAVA_EXERCISE_TIMEOUT` is used after the cache is warm for the
starter, failure, and bad-code checks.

The harness creates a unique temporary Maven workspace, copies the canonical
POM and trusted tests, copies only the selected source variant, mounts that
workspace at `/workspace`, and removes the execution container with
`docker run --rm`. It runs Maven as the invoking WSL user and aligns the named
cache volume ownership before execution, so generated `target/` files remain
removable by the developer. `KEEP_WORKSPACE=1` retains the host workspace so
`target/surefire-reports/` can be inspected after the run.

Maven dependencies are stored in the dedicated named volume
`neuralascent-maven-cache` and are never mixed with exercise source.

## Resource and network policy

The harness uses a disposable bridge-network container with development
defaults of 768 MB memory, one CPU, 128 PIDs, and a 120-second outer timeout.
The outer timeout accommodates the first Maven dependency download; set
`JAVA_RUNNER_TIMEOUT=20` for subsequent execution-focused checks. Internet is
intentionally allowed in Phase 1 so Maven can retrieve JUnit.

The harness does not mount the Docker socket, PostgreSQL storage, API source,
environment files, AWS credentials, SSH keys, host networking, or the whole
repository read/write.

## Expected evidence mapping

The seven authoritative tests map to the manifest evidence IDs as follows:

| Test method | Evidence ID |
| --- | --- |
| `testPointHasX` | `point-x` |
| `testPointHasY` | `point-y` |
| `testPointHasDisplay` | `point-display-signature` |
| `testPointDisplay` | `point-display-output` |
| `testThreedPointInheritsPoint` | `threedpoint-inheritance` |
| `testThreedPointDisplayMethodOverride` | `threedpoint-override` |
| `testThreedPointDisplayMethodOutput` | `threedpoint-output` |

Surefire XML is written to the retained workspace at:

```text
target/surefire-reports/TEST-ThreedPointTest.xml
```

It records the test suite name, test count, failures/errors, test method names,
failure messages, and durations for later Phase 2 parsing.

## Phase 1 boundaries

The API creates runner containers dynamically through Docker.DotNet. The
runner receives the copied `/workspace` archive and the named Maven cache
volume only; it never receives the Docker socket, API environment, database
credentials, cloud credentials, or arbitrary host mounts. Production starts
with one concurrent execution through `ExerciseExecution__MaxConcurrentExecutions=1`.
