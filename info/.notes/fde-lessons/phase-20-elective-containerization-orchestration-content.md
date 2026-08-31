# FDE Phase 20 — Elective: Containerization and Orchestration (Lessons 1-6 of 17)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-20-elective-containerization-orchestration-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `elective-containerization-orchestration` ("Containerization and
Orchestration") — a `SupplementalModuleDefinition`, **the first of three elective modules** now in
scope (Containerization/K8s, 17 lessons; AWS Multi-Region Cloud Deep Dive, 17 lessons; Storage,
Networking & Reliability for FDEs, 14 lessons). The ~104-lesson core curriculum is already 100%
complete; this is new, optional ground on top of it.

This file covers **lessons 1-6 of 17 only** — Docker fundamentals through networking. A later phase
(21) covers lessons 7-12 (Hardening the Docker Environment, Industry-Standard Container Hardening
Demo, Introduction to Orchestration, Kubernetes Architecture, Kubernetes Pod Deep Dive,
ReplicaSets/Deployments/Sidecars) and Phase 22 covers lessons 13-17 (Kubernetes Networking, Scaling,
RBAC/DevSecOps, Volumes, and whatever the 17th lesson is per the module's inline skeleton) — do not
add placeholder content for those 11 lessons here.

**Overlap note (checked against Module 4, `cloud-devops-infrastructure`, Phases 9-10):** Module 4
lesson 4, "Docker: Production Containers," already teaches multi-stage builds, cache-friendly layer
ordering, non-root execution, and `SIGTERM` handling for a FastAPI/Celery scenario, and Module 4
lesson 7 references Pod Security Standards against "the Docker lesson's" non-root thread. This
elective assumes the learner may reach it with or without that lesson already done, so it does not
skip Dockerfile fundamentals — but it deliberately uses a **different scenario** (Vantage Utilities'
`ticket-api` pilot, not the FastAPI/Celery order-management service) and pushes one level earlier and
one level more mechanical than Module 4 did: Lesson 3 here teaches the Dockerfile instruction set
itself (`ENTRYPOINT` vs `CMD`, exec vs shell form, `ARG` vs `ENV`, `HEALTHCHECK`) which Module 4
assumed as prior knowledge, and Lesson 4 generalizes past one `SIGTERM` fix into the PID 1 problem,
signal propagation mechanics, environment-precedence rules, and OOM-kill exit codes. Where the
mechanism genuinely repeats (cache ordering, multi-stage builds), this phase treats it briefly and
points forward to Module 4 for the production-hardening framing, rather than re-teaching it from
scratch.

All six lessons follow one continuous scenario: an FDE engagement for **Vantage Utilities**, a
regional field-services company. The pilot deliverable is **`ticket-api`**, a small Flask +
PostgreSQL service that lets Vantage's dispatchers create and close field-service tickets, with a
technician-facing upload for photo attachments. The FDE containerizes `ticket-api` from a
laptop-only prototype into something Vantage's ops team can actually run, restart, and hand off.

---

# LESSON 1

```yaml
lesson_id: fde-elective-containerization-orchestration-01-docker-introduction
lesson_title: "Docker Introduction"
lesson_order: 1

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration (Elective)"
module_order: "Elective 1"

difficulty: Intermediate
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Explain what a container actually isolates (process tree, filesystem, network namespace, resource limits) versus what it still shares with the host kernel, and why that distinction matters for a customer handoff."
  - "Distinguish an image (a built, immutable artifact) from a container (a running instance of that artifact) using the Docker CLI, not just definitionally."
  - "State which operational concerns — scheduling, service discovery, rolling restarts across machines — Docker alone does not solve, setting up the reason orchestration exists later in this module."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Docker Introduction

## Concepts Covered

A container is not a lightweight virtual machine, even though it is often introduced that way. A VM virtualizes hardware and boots its own kernel; a container is an ordinary Linux process that the kernel has restricted using three independent mechanisms — namespaces, control groups (cgroups), and a union filesystem — so that it perceives its own process tree, network stack, hostname, and filesystem while actually running on the same shared kernel as the host and every other container next to it. Namespaces control what a process can *see*: the PID namespace gives a containerized process its own view of process IDs starting at 1, the network namespace gives it its own network interfaces and routing table, the mount namespace gives it its own filesystem view. Cgroups control what a process can *use*: CPU shares, memory ceilings, block I/O bandwidth, all enforced by the kernel, not by the containerized process cooperating. Because the kernel is shared, a container is fundamentally cheaper to start than a VM (no second kernel to boot) but also fundamentally less isolated than a VM — a kernel vulnerability or a misconfigured capability can cross the container boundary in a way a hypervisor boundary is designed to resist.

The Docker daemon (`dockerd`) is a long-running background process that does the actual work of applying namespaces and cgroups, building images, and managing container lifecycle; the `docker` command you type is a thin client that talks to the daemon over a local socket (or, unusually, over a remote API). This client/daemon split matters operationally: `docker` commands do not have to run as the same user or even on the same host as `dockerd`, and a hung or slow daemon manifests as every `docker` command hanging, not as a per-command failure. Docker solves *packaging* — it captures an application, its runtime, its dependencies, and its filesystem assumptions into one portable, versioned artifact that runs identically wherever a compatible Docker daemon exists. It does not, by itself, solve *orchestration* — deciding which of several machines should run a given container, restarting a container that dies, discovering one service's address from another, or rolling out a new version across many hosts without downtime. Those are the problems Kubernetes exists to solve, later in this module; conflating "I containerized my app" with "my app is production-ready across a fleet of machines" is the single most common category error this module exists to correct.

```bash
# The client/daemon split, made visible
$ docker version
Client: Docker Engine - Community
 Version:           27.3.1
 API version:       1.47

Server: Docker Engine - Community
 Engine:
  Version:          27.3.1
  Containerd:       1.7.22

# The host's own kernel and process view, for contrast
$ uname -r
6.8.0-generic
$ ps -p 1 -o comm=
systemd

# A container's process view — namespaced, not the host's
$ docker run --rm alpine ps aux
PID   USER     TIME  COMMAND
    1 root      0:00 ps aux        # PID 1 inside the container, not on the host

# A cgroup memory ceiling, enforced by the kernel, not the app
$ docker run --rm --memory=64m alpine sh -c 'cat /sys/fs/cgroup/memory.max'
67108864                            # 64MB, in bytes — the kernel's own accounting
```

## Practical Backend Scenario

Vantage Utilities' pilot service, `ticket-api`, works perfectly on the FDE's laptop: Python 3.12, a locally running PostgreSQL 16, and a `pip install -r requirements.txt` that happened to succeed because the laptop already had `libpq-dev` installed from an unrelated project two years ago. When the FDE hands a zipped source tree to Vantage's ops engineer, `pip install` fails on `psycopg2` because the ops engineer's machine has Python 3.9 and no PostgreSQL client headers at all — an assumption about the host environment that was never written down anywhere, because it never needed to be while the app only ever ran on one laptop. The fix is not a longer README of manual setup steps; it is packaging `ticket-api` and its exact runtime dependencies into a Docker image that Vantage's ops engineer can run with one command, on any machine with Docker installed, regardless of what Python version or system libraries that machine happens to already have.

## Practice Loop

1. Run `python3 --version` and `pip show psycopg2` on your own machine, and list every assumption `ticket-api`'s current setup silently depends on (Python version, system libraries, environment variables) that is not captured in any file in the repository.
2. Pull and run a small existing image — `docker run --rm python:3.12-slim python3 -c "import sys; print(sys.version)"` — and confirm the reported Python version is the image's, not your host's, proving the container carries its own runtime.
3. Run `docker run --rm alpine sh -c 'echo $$; cat /proc/1/comm'` and compare the reported PID to what `ps` shows for the same process on your host — this diagnostic makes "the container has its own PID namespace" concrete instead of asserted.
4. Run the same container twice with `--memory=64m` and without any memory flag, and use `docker inspect --format='{{.HostConfig.Memory}}'` on each to confirm the cgroup limit is actually recorded per-container.
5. Write a one-paragraph handoff note listing exactly what a container guarantees for Vantage's ops engineer (a fixed runtime and dependency set) versus what it does not guarantee (which machine it runs on, what happens if that machine reboots, how a second instance would discover the first) — this becomes the reason this module continues past Docker into orchestration.

## Evidence of Understanding

You can explain what a container isolates (process view, network view, filesystem view, resource ceilings) using the specific kernel mechanisms responsible (namespaces, cgroups) rather than a VM analogy. You can distinguish the `docker` client from the `dockerd` daemon and explain why a hung daemon affects every command rather than one. You can state, with a concrete example, which operational problems (multi-host scheduling, restart-on-failure, service discovery, coordinated rollout) Docker does not solve by itself, and why that gap is what orchestration exists to close.

## Suggested Extension

Run `docker run --rm --pid=host alpine ps aux` and compare its output to a normal `docker run --rm alpine ps aux` — explain, using the PID namespace mechanism from this lesson, exactly what changed and why `--pid=host` is a meaningful isolation trade-off, not just a flag.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What a container actually is
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Which statement most accurately describes what a Docker container is, relative to the host it runs on?

**OPTIONS:**
- [ ] A: A lightweight virtual machine that boots its own kernel but shares the host's hardware drivers
- [x] B: An ordinary Linux process restricted by namespaces (what it can see) and cgroups (what it can use), sharing the host kernel with every other container
- [ ] C: A statically compiled binary that requires no kernel features from the host at all
- [ ] D: A separate physical partition of the host's disk that Docker mounts as a chroot jail

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is explicit that a container is not a lightweight VM — it is a kernel-restricted process, isolated by namespaces and bounded by cgroups, on a kernel shared with the host and every neighboring container.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [namespaces, cgroups, container-vs-vm]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Namespaces vs cgroups
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A container is started with a 64MB memory ceiling and its own process tree, but still ends up on the same physical CPU cores and can still be seen (with the right host tooling) from outside the container. Which pairing of mechanism to responsibility is correct?

**OPTIONS:**
- [x] A: Namespaces control what the process can see (its own PID tree, network view); cgroups control what it can use (the memory ceiling)
- [ ] B: Cgroups control what the process can see; namespaces control what it can use
- [ ] C: Both namespaces and cgroups are purely about memory limiting, with different syntax
- [ ] D: Namespaces and cgroups are two names for the same underlying kernel feature

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson draws this line explicitly: namespaces are about visibility (PID tree, network interfaces, mounts), cgroups are about resource consumption ceilings enforced by the kernel.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [namespaces, cgroups, isolation-mechanism]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Client/daemon split
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Every `docker` command you type on a workstation suddenly hangs, including `docker ps`. Per the lesson's description of the client/daemon architecture, what does this most likely indicate?

**OPTIONS:**
- [ ] A: The specific container you were about to inspect has crashed
- [x] B: `dockerd`, the daemon the `docker` CLI client talks to, is hung or unresponsive — since every client command routes through it, all commands hang together, not just one
- [ ] C: Your shell's `PATH` no longer includes the `docker` binary
- [ ] D: A namespace collision between two unrelated containers

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson calls this out specifically: the `docker` CLI is a thin client to `dockerd`, so a hung daemon manifests as every command hanging, not a per-command failure — a diagnostic signature worth recognizing.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [docker-daemon, client-daemon-architecture]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What Docker does not solve
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, which of the following is explicitly a problem Docker does NOT solve by itself?

**OPTIONS:**
- [ ] A: Packaging an application's runtime and dependencies into one portable artifact
- [x] B: Deciding which of several machines should run a given container, and restarting it automatically on a different host if that machine fails
- [ ] C: Producing an image that runs identically on any host with a compatible Docker daemon
- [ ] D: Giving a container its own filesystem view distinct from the host's

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson lists multi-host scheduling, restart-on-failure, service discovery, and coordinated rollout as orchestration's job, not Docker's — this is the exact gap the rest of the module addresses with Kubernetes.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [orchestration-gap, docker-scope]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why `ticket-api` broke on handoff
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did `pip install -r requirements.txt` fail on Vantage's ops engineer's machine when it had always worked on the FDE's laptop?

**OPTIONS:**
- [ ] A: `requirements.txt` was missing from the zipped source tree
- [x] B: The FDE's laptop had system libraries (PostgreSQL client headers) and a Python version installed from unrelated prior work that were never captured as explicit dependencies anywhere in the repository
- [ ] C: PostgreSQL cannot be installed on any machine other than the original development laptop
- [ ] D: The ops engineer used a different version of `pip` than the FDE

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scenario's point is exactly this: implicit, undocumented host assumptions (installed two years ago, for an unrelated project) silently made the laptop's environment "work" in a way that was never actually written down or reproducible elsewhere.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [implicit-environment-assumptions, reproducibility]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Reading the PID namespace diagnostic
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ docker run --rm alpine sh -c 'echo $$; cat /proc/1/comm'
1
sh
```

**QUESTION_TEXT:**
Given the command and output above, run inside a container, what does the reported PID of `1` demonstrate about the container's PID namespace?

**OPTIONS:**
- [x] A: The container has its own PID namespace, in which its first process is numbered 1, regardless of what PID that same process holds from the host's point of view
- [ ] B: The `alpine` image is broken because a normal process should never be PID 1
- [ ] C: Docker always runs exactly one process per container, so PID 1 is guaranteed by definition rather than by the namespace mechanism
- [ ] D: The host machine itself was rebooted immediately before this command ran

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is Practice Loop step 3's diagnostic: the container's own PID namespace numbers its first process 1 independent of the host's actual process table, making the isolation concrete rather than asserted.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [pid-namespace, diagnostic]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** cgroup memory ceiling verification
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 4 has you run the same container with and without `--memory=64m`, then inspect `HostConfig.Memory` for each. What is this step actually verifying?

**OPTIONS:**
- [ ] A: That the container's application code runs faster with a memory limit set
- [x] B: That the cgroup-based memory ceiling is recorded and enforced per-container, not as a global, shared setting across every container on the host
- [ ] C: That `alpine` requires at least 64MB of memory to start at all
- [ ] D: That `docker inspect` only works on containers that were started with an explicit memory flag

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The step exists to make the per-container cgroup ceiling concrete: one run shows a recorded limit, the other shows none, proving the setting is per-container rather than host-wide.

**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [cgroups, memory-limit-diagnostic]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** `--pid=host` trade-off
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, running `docker run --rm --pid=host alpine ps aux` shows the container the host's own full process list, unlike a normal container run. What does this demonstrate about namespace isolation?

**OPTIONS:**
- [ ] A: `--pid=host` is required for any container that needs to run more than one process
- [x] B: `--pid=host` disables the container's own PID namespace, letting it see (and, with the right privileges, potentially signal) every process on the host — namespace isolation is a configurable boundary, not an unconditional guarantee
- [ ] C: `--pid=host` only affects network namespace behavior, not the process tree
- [ ] D: Alpine-based images ignore `--pid` flags entirely due to their minimal init system

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This extension is designed to show that namespace isolation is a deliberate, removable boundary — `--pid=host` opts a container out of PID namespace isolation, exposing the host's real process tree, which is exactly the kind of flag a security review should flag if present without justification.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [pid-host, isolation-boundary, configurable-isolation]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

Reference: Docker documentation — "Docker overview" (https://docs.docker.com/get-started/docker-overview/)

---

# LESSON 2

```yaml
lesson_id: fde-elective-containerization-orchestration-02-docker-images-and-containers
lesson_title: "Docker Images and Containers"
lesson_order: 2

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration (Elective)"
module_order: "Elective 1"

difficulty: Intermediate
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Distinguish an image's layered, immutable filesystem from a running container's ephemeral writable layer, using `docker history` and `docker diff` as evidence, not assertion."
  - "Pin and reproduce an exact build using a content-addressable digest rather than a mutable tag, and explain why a tag alone is not a reliable reproducibility guarantee."
  - "Trace a container's lifecycle (create, start, stop, remove) and identify at which point its writable layer and any un-persisted state is lost."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Docker Images and Containers

## Concepts Covered

An image is a read-only, layered filesystem plus metadata (the command to run, exposed ports, default environment) captured in a manifest. Each instruction in a Dockerfile that modifies the filesystem produces one layer, identified by a content hash of that layer's contents; `docker build` reuses a previously built layer whenever an earlier instruction and everything above it in the Dockerfile are byte-identical to a prior build, which is the mechanism layer-caching relies on. A tag (`ticket-api:1.4.2`, or the mutable `ticket-api:latest`) is a human-friendly, movable pointer at a specific image ID — nothing stops two different builds from both being tagged `latest`, or from `1.4.2` being silently rebuilt and re-pushed with different contents than what a teammate pulled an hour earlier. A digest (`sha256:e3b0c4...`) is the actual content hash of the image manifest itself — it is what you pin when "the exact same build, byte for byte" is the requirement, not "whatever a mutable tag currently points to."

A container is a running (or stopped) instance of an image, with one additional writable layer stacked on top of the image's read-only layers using a union filesystem (typically `overlayfs`). Every file the container process creates, modifies, or deletes at runtime happens in that writable layer; the underlying image layers are never touched, which is exactly what lets many containers share one image's layers on disk without one container's writes affecting another's, or the image itself. This has a direct operational consequence: anything written only to the writable layer — a log file, a cached computation, an uploaded file saved to a path nobody mounted a volume onto — disappears the moment `docker rm` removes that container, because the writable layer is removed with it. This is not a bug to work around with careful cleanup ordering; it is the entire point of the design, and the correct response (durable state belongs in a volume, covered in Lesson 5, not in the container's writable layer) follows directly from understanding this mechanism rather than memorizing it as a rule. Promoting a *build* from staging to production should mean promoting the exact same image — by digest — rather than rebuilding from the same Dockerfile a second time and hoping the result is identical; a rebuild can silently differ if a base image was updated, an unpinned dependency resolved to a new version, or the build machine's clock or `apt` mirror state differed between runs.

```bash
# Build and tag the image
$ docker build -t ticket-api:1.4.2 .
[+] Building 34.2s (11/11) FINISHED
 => [internal] load build definition from Dockerfile
 => [3/6] COPY requirements.txt .
 => [4/6] RUN pip install --no-cache-dir -r requirements.txt
 => [6/6] COPY . .
 => exporting to image
 => => writing image sha256:7a9f3c1e8b42...
 => => naming to docker.io/library/ticket-api:1.4.2

# The tag and its digest
$ docker images ticket-api
REPOSITORY   TAG      IMAGE ID       CREATED         SIZE
ticket-api   1.4.2    7a9f3c1e8b42   4 seconds ago   214MB

$ docker inspect --format='{{index .RepoDigests 0}}' ticket-api:1.4.2
ticket-api@sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

# Pin the exact build for a reproducible rollback
$ docker pull registry.vantage.internal/ticket-api@sha256:e3b0c442...
```

## Practical Backend Scenario

Two weeks after go-live, Vantage's ops engineer opens an incident: `ticket-api` returned 500s for eleven minutes starting at 02:14 UTC. The support team needs to reproduce the exact build that was running at that timestamp — not "whatever `ticket-api:latest` currently points to," since `latest` has been rebuilt three times since then and none of those rebuilds are guaranteed byte-identical to what was actually deployed. Because the CI pipeline tags every build with both a semantic version (`1.4.2`) and pushes its digest to the deployment log, the FDE looks up the digest recorded at 02:14 UTC and runs `docker pull registry.vantage.internal/ticket-api@sha256:e3b0c442...` — pulling the exact image that was live during the incident, with no ambiguity about what "1.4.2" meant at that particular moment, since the tag alone could have pointed at different content before and after a later rebuild.

## Practice Loop

1. Build `ticket-api` twice from the same Dockerfile with two different tags (`1.4.2` and `1.4.3-test`), and run `docker images` to see both listed with different image IDs despite one intentional code change between builds.
2. Run `docker history ticket-api:1.4.2` and identify which layer corresponds to the `pip install` instruction and which corresponds to the final `COPY . .`.
3. Start a container from the image, write a file inside it that no volume is mounted onto, then run `docker diff <container>` before removing it — count exactly how many filesystem changes are visible in the writable layer versus the image's own layers, which stay untouched.
4. Remove the container with `docker rm -f`, then attempt to find the file you wrote in step 3 anywhere on the host or in the image — confirm it is genuinely gone, not just hidden.
5. Record both the tag and the digest for your final build, and write one sentence explaining which one you would give to a teammate who needs to reproduce this exact build in six months, and why.

## Evidence of Understanding

You can distinguish an image's read-only, content-addressed layers from a running container's single writable layer, and demonstrate with `docker diff` exactly what a container adds on top of its image. You can explain why a mutable tag is not a reliable reproducibility guarantee and pin an exact build using its digest instead. You can trace a container's lifecycle from `docker run` through `docker rm` and identify precisely the point at which any state written only to the writable layer is lost.

## Suggested Extension
Run `docker history --no-trunc ticket-api:1.4.2` and identify one layer you could remove or combine with an earlier instruction to reduce the image's total layer count, without changing what the final image contains.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Image layers vs the writable container layer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the structural relationship between a Docker image and a running container built from it?

**OPTIONS:**
- [ ] A: A container is a full copy of the image's filesystem, independent of the image after it starts
- [x] B: A container adds one writable layer on top of the image's read-only layers via a union filesystem; the image's layers themselves are never modified
- [ ] C: An image is generated dynamically each time a container starts, from the container's current filesystem state
- [ ] D: Images and containers are two names for the same object at different points in Docker's release history

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is explicit: a container stacks exactly one writable layer on the image's read-only layers, and every runtime write lands there, never touching the underlying image.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [writable-layer, union-filesystem, image-vs-container]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why a tag alone is not reproducible
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that a tag like `ticket-api:1.4.2` is not, by itself, a reliable way to reproduce an exact build?

**OPTIONS:**
- [ ] A: Tags are limited to 8 characters, so version information is frequently truncated
- [x] B: A tag is a mutable, movable pointer — nothing prevents the same tag from being silently rebuilt and re-pushed with different underlying content later
- [ ] C: Docker deletes tags automatically after 90 days for storage reasons
- [ ] D: Tags cannot be pulled from a private registry, only digests can

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's point is specifically about mutability: a tag can be repointed at new content at any time, which is exactly why the incident scenario needed the recorded digest, not the tag.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [tag-mutability, digest-pinning]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading `docker inspect` for a digest
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ docker inspect --format='{{index .RepoDigests 0}}' ticket-api:1.4.2
ticket-api@sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

**QUESTION_TEXT:**
Given this command and output, what does the returned value let you do that the tag `ticket-api:1.4.2` alone does not guarantee?

**OPTIONS:**
- [x] A: Pull or reference this exact image content later, unaffected by any future rebuild that reuses the same tag
- [ ] B: Automatically rebuild the image from its original Dockerfile, since the digest encodes the build instructions
- [ ] C: Determine which Dockerfile instruction produced the largest layer
- [ ] D: Guarantee the image will run identically on a different CPU architecture

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The digest is a content hash of this exact manifest — referencing it by digest is immune to the tag being repointed at different content later, which is the whole reason the incident-response scenario relies on it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [digest, content-addressable]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the incident required the digest, not the tag
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why couldn't the support team just pull `ticket-api:latest` to reproduce the build that was live during the 02:14 UTC incident?

**OPTIONS:**
- [ ] A: `latest` tags cannot be pulled from a private registry under any circumstances
- [x] B: `latest` had been rebuilt three times since the incident, and nothing guarantees any of those later rebuilds are byte-identical to what was actually running at 02:14 UTC
- [ ] C: The incident occurred before `ticket-api` had ever been tagged `latest`
- [ ] D: PostgreSQL connection strings are embedded in the `latest` tag and change on every pull

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the scenario's central point: a tag drifts over time as new builds are pushed under it, so only the recorded digest from the actual deployment log guarantees the exact build content.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [incident-reproduction, digest-vs-tag]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What `docker diff` reveals
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 3 has you write a file inside a running container (with no volume mounted) and then run `docker diff` on it before removing the container. What does `docker diff`'s output represent?

**OPTIONS:**
- [ ] A: The difference between two separate image tags built from the same Dockerfile
- [x] B: The filesystem changes present in the container's writable layer relative to its base image — additions, modifications, and deletions the container made at runtime
- [ ] C: A byte-level diff between the container's memory usage before and after the write
- [ ] D: The set of Dockerfile instructions that were cache-invalidated during the most recent build

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
`docker diff` reports exactly the writable-layer changes a container has made since it started — which is why the file from step 3 shows up there and nowhere in the image's own layers.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [docker-diff, writable-layer-diagnostic]

### QUESTION_BLOCK_END: Q5
### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Where the file goes after `docker rm`
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 4 has you remove the container from step 3 and confirm the file you wrote is genuinely gone. Why does removing the container also remove that file?

**OPTIONS:**
- [ ] A: `docker rm` triggers a scheduled garbage-collection job that runs a few minutes later
- [x] B: The file existed only in the container's writable layer, which is deleted along with the container itself; it was never part of the image's own persistent layers
- [ ] C: `docker rm` deletes the entire image, not just the container instance
- [ ] D: Files written without an explicit `chmod` are automatically excluded from the writable layer

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the direct operational consequence of the writable-layer mechanism: anything not placed in a volume disappears when the container that wrote it is removed, because that is exactly what the writable layer is.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [writable-layer-lifecycle, state-loss]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Layer cache reuse across two builds
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 1 builds `ticket-api` twice under different tags, with one intentional code change between builds. Per the mechanism this lesson describes, which layers would the second build most likely reuse from the first build's cache?

**OPTIONS:**
- [x] A: Every layer up to and including the one built from the last Dockerfile instruction that is identical to the first build, in order, before the changed instruction
- [ ] B: No layers at all, since any code change anywhere invalidates the entire build from scratch
- [ ] C: Only the final `COPY . .` layer, since that always changes least often
- [ ] D: All layers, since Docker caches builds by tag name rather than by layer content

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson states the caching rule precisely: a layer is reused only if it and every instruction above it in the Dockerfile are byte-identical to a prior build — reuse holds up to the first point of divergence, then stops.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [layer-cache, build-reuse]

### QUESTION_BLOCK_END: Q7
### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Interpreting `docker history` layer sizes
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 2 has you run `docker history ticket-api:1.4.2` to identify the `pip install` layer versus the final `COPY . .` layer. What is the practical reason for learning to read this output?

**OPTIONS:**
- [ ] A: `docker history` is required before every `docker run`, or the container refuses to start
- [x] B: Being able to attribute image size and layer boundaries to specific Dockerfile instructions is what lets you reason about cache reuse and image bloat concretely, instead of guessing which instruction is expensive
- [ ] C: It reveals the exact CPU time each build step consumed on the build machine
- [ ] D: It shows which layers were pulled from a remote registry versus built locally, which is unrelated to the Dockerfile's instructions

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Mapping layers to instructions is the diagnostic skill this step builds — it turns "the image feels big" into "this specific instruction produced this specific layer size," which is what later Dockerfile-authoring work depends on.

**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [docker-history, layer-attribution]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

Reference: Docker documentation — "About storage drivers" and "Image layers" (https://docs.docker.com/storage/storagedriver/)

---

# LESSON 3

```yaml
lesson_id: fde-elective-containerization-orchestration-03-building-your-own-docker-image
lesson_title: "Building Your Own Docker Image"
lesson_order: 3

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration (Elective)"
module_order: "Elective 1"

difficulty: Intermediate
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Write a Dockerfile using the correct instruction for each concern (FROM, WORKDIR, COPY, RUN, ENV/ARG, EXPOSE, ENTRYPOINT/CMD, HEALTHCHECK) rather than one undifferentiated block of shell commands."
  - "Explain the difference between exec form and shell form for ENTRYPOINT/CMD, and why exec form is required for correct signal handling."
  - "Order Dockerfile instructions and scope the build context (.dockerignore) so that a code-only change rebuilds in seconds, not minutes, and no local secret is ever baked into a layer."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Building Your Own Docker Image

## Concepts Covered

A Dockerfile is a sequence of instructions, and each one has a distinct, non-interchangeable job, even though several of them could technically be faked with `RUN`. `FROM` picks the base image and, with it, the base's own vulnerability surface and package manager — a build starting `FROM python:3.12` inherits Debian's full package set (a compiler, `apt`, shell utilities) even if the application never uses any of them, while `FROM python:3.12-slim` trims that down deliberately. `WORKDIR` sets the working directory for every instruction after it (creating the directory if it does not exist), which is more reliable than `RUN cd some/path && ...`, since a `cd` inside one `RUN` does not persist to the next `RUN` — each `RUN` instruction is its own shell invocation. `COPY` moves files from the build context (the directory you pass to `docker build`, by default the current directory) into the image; `ARG` defines a build-time-only variable available during the build but not inside the running container, while `ENV` defines a variable baked into the image and available at runtime too — using `ARG` for a value like a build-time version tag and `ENV` for a runtime configuration default is a distinction worth getting right, not an interchangeable pair.

`ENTRYPOINT` and `CMD` both define what runs when the container starts, but they compose: `ENTRYPOINT` is the fixed command, `CMD` supplies default arguments to it that `docker run` can override, and the two are commonly written together (`ENTRYPOINT ["python", "-m", "ticket_api"]` with no `CMD`, or `ENTRYPOINT ["python"]` with `CMD ["-m", "ticket_api"]` so a caller can swap the module). Both instructions accept two syntactic forms with materially different runtime behavior: exec form (`CMD ["python", "app.py"]`, a JSON array) runs the process directly as PID 1, while shell form (`CMD python app.py`) wraps it in `/bin/sh -c "python app.py"`, making `/bin/sh` PID 1 and the actual application process a *child* of the shell. This is not a stylistic preference — a signal Docker sends to PID 1 (a `SIGTERM` on `docker stop`) reaches `/bin/sh` in shell form, and `/bin/sh` does not forward that signal to its child by default, meaning the application never sees the termination signal it might need to shut down cleanly, a mechanism this module's next lesson goes into in more depth. `HEALTHCHECK` lets an image declare its own liveness probe as part of the image itself (`HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1`), so any tooling that runs the image — Docker Compose, a bare `docker run`, or later, Kubernetes — inherits a working health signal without having to reinvent one per deployment target.

```dockerfile
# Dockerfile for ticket-api
FROM python:3.12-slim AS builder
WORKDIR /app

# Dependency manifest copied first: this layer only invalidates
# when requirements.txt itself changes, not on every code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 1000 appuser
COPY --from=builder /deps /usr/local/lib/python3.12/site-packages

# Application code copied last: changes here reuse every layer above.
COPY . .

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD curl -f http://localhost:8080/health || exit 1

# Exec form: the app process becomes PID 1 directly, so it
# receives SIGTERM from `docker stop` without a shell in between.
ENTRYPOINT ["python", "-m", "ticket_api"]
```

```text
# .dockerignore — keeps the build context small and secrets out of any layer
.git
__pycache__/
*.pyc
.env
tests/
.pytest_cache/
```

## Practical Backend Scenario

The first `ticket-api` Dockerfile the FDE writes is a single, undifferentiated block: `FROM python:3.12`, `COPY . .` immediately, then `RUN pip install -r requirements.txt`, with `CMD python -m ticket_api` in shell form and no `.dockerignore` at all. It builds and runs, but three things are wrong the moment Vantage's ops engineer tries to operate it: every source-code edit invalidates the dependency-install layer because `COPY . .` runs before `pip install`, so every rebuild reinstalls every dependency from scratch; the build context silently includes a local `.env` file with the FDE's own PostgreSQL password, which ends up baked into an image layer that a `docker history` on the shipped image would reveal; and when the ops engineer runs `docker stop ticket-api`, the container takes the full 10-second grace period and gets `SIGKILL`ed every time, because the shell-form `CMD` puts `/bin/sh` at PID 1, and `/bin/sh` never forwards the `SIGTERM` to the actual Python process underneath it. Rewriting the Dockerfile with the dependency-manifest-first ordering, a `.dockerignore` excluding `.env`, and exec-form `ENTRYPOINT` fixes all three at once, for the reasons named above — none of the three requires extra code, only reordering and syntax that were already available.

## Practice Loop

1. Write the naive single-block Dockerfile described above (no `.dockerignore`, `COPY . .` before `pip install`, shell-form `CMD`), build it, and time the build.
2. Make one code-only change (a comment) and rebuild, recording how many layers the cache reused — confirm the dependency-install step reran even though `requirements.txt` did not change.
3. Run `docker history --no-trunc` on the naive image and search its layers for the string `.env` or a known local password value — count how many layers contain it, confirming the exact leak the scenario describes.
4. Rewrite the Dockerfile with the manifest-first ordering, a `.dockerignore` excluding `.env`, `USER appuser`, and exec-form `ENTRYPOINT`; rebuild and repeat step 2's code-only-change timing, recording the improvement.
5. Run `docker stop` against a container started from each image (naive and fixed) and time how long each takes to actually exit, confirming the exec-form image stops immediately while the shell-form image waits out the full grace period before being killed.

## Evidence of Understanding

You can write a Dockerfile that uses `FROM`, `WORKDIR`, `COPY`, `RUN`, `ARG`/`ENV`, `EXPOSE`, `ENTRYPOINT`/`CMD`, and `HEALTHCHECK` each for their distinct purpose, rather than collapsing everything into `RUN`. You can explain, and demonstrate with `docker stop` timing, why exec-form `ENTRYPOINT` is required for a container's main process to actually receive `SIGTERM`. You can order instructions and write a `.dockerignore` so that a code-only change rebuilds in seconds and no local secret is ever copied into the build context in the first place.

## Suggested Extension
Add a build-time `ARG VERSION` that gets baked into an `ENV APP_VERSION` inside the image (via `ARG VERSION` followed by `ENV APP_VERSION=$VERSION`), and confirm `docker run ticket-api:latest env | grep APP_VERSION` reports it while `docker build --build-arg VERSION=1.5.0` is the only place that value is ever set.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** WORKDIR vs a bare `cd`
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend `WORKDIR /app` over `RUN cd /app && ...` for setting a Dockerfile's working directory?

**OPTIONS:**
- [x] A: Each `RUN` instruction is its own shell invocation, so a `cd` inside one `RUN` does not persist to the next `RUN`; `WORKDIR` sets the directory for every subsequent instruction reliably
- [ ] B: `cd` is not a valid command inside any Docker build context, regardless of instruction
- [ ] C: `WORKDIR` is faster to execute than `cd` at the shell level
- [ ] D: `RUN cd` instructions are not cached, unlike `WORKDIR`

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson states this precisely: each `RUN` is a fresh shell, so a `cd` there has no effect on later instructions, while `WORKDIR` persists across the rest of the Dockerfile.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [workdir, run-instruction-scope]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** ARG vs ENV
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A Dockerfile needs a value known only at build time (a build number passed via `--build-arg`) and a separate value that the running container's application should be able to read via its environment. Which instruction is correct for each?

**OPTIONS:**
- [ ] A: Use `ENV` for both — `ARG` cannot hold string values
- [x] B: Use `ARG` for the build-time-only value, and `ENV` for the value that must also be available inside the running container
- [ ] C: Use `ARG` for both — `ENV` is deprecated in favor of `ARG`
- [ ] D: The distinction is purely stylistic; both instructions behave identically at build time and runtime

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
`ARG` values exist only during the build and are not present in the running container unless explicitly copied into an `ENV`; `ENV` values are baked into the image and available at runtime.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [arg-vs-env, build-time-vs-runtime]

### QUESTION_BLOCK_END: Q2
### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Exec form vs shell form
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```dockerfile
CMD python app.py
```

**QUESTION_TEXT:**
Given this `CMD` instruction, written in shell form, what process actually becomes PID 1 inside the container, and what is the consequence?

**OPTIONS:**
- [ ] A: `python app.py` becomes PID 1 directly, identical in behavior to exec form
- [x] B: `/bin/sh` becomes PID 1, with the Python process as its child; `/bin/sh` does not forward a `SIGTERM` to that child by default, so the application never sees the termination signal
- [ ] C: The container fails to start, since shell form is not valid Dockerfile syntax
- [ ] D: Docker automatically converts shell form to exec form at build time, so there is no runtime difference

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's central mechanism: shell form wraps the command in `/bin/sh -c`, putting the shell at PID 1 and leaving signal forwarding to the shell, which does not happen automatically — exactly what breaks graceful shutdown in the scenario.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [exec-form, shell-form, signal-forwarding]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** ENTRYPOINT and CMD composing
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A Dockerfile has `ENTRYPOINT ["python"]` and `CMD ["-m", "ticket_api"]`. What does `docker run ticket-api -m ticket_worker` actually execute inside the container?

**OPTIONS:**
- [ ] A: `python -m ticket_api -m ticket_worker`, since CMD arguments are always appended, never replaced
- [x] B: `python -m ticket_worker`, since the arguments passed to `docker run` after the image name override CMD's default arguments while ENTRYPOINT stays fixed
- [ ] C: The command fails, since ENTRYPOINT cannot be combined with a separate CMD
- [ ] D: `python` alone, ignoring both CMD and the docker run arguments

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson describes exactly this composition: ENTRYPOINT is the fixed command, CMD supplies default arguments that a `docker run` command line overrides, not appends to.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [entrypoint-cmd-composition]

### QUESTION_BLOCK_END: Q4
### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the naive Dockerfile leaked a secret
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the naive `ticket-api` Dockerfile bake the FDE's local `.env` file, containing a real database password, into an image layer?

**OPTIONS:**
- [ ] A: `COPY . .` always ignores hidden files (those starting with `.`) unless told otherwise
- [x] B: With no `.dockerignore` file, `COPY . .` copies everything in the build context, including `.env`, into the image; the file becomes part of a layer the moment it is copied, regardless of whether the application ever reads it
- [ ] C: Docker automatically injects any local `.env` file into every image as a convenience feature
- [ ] D: `pip install` reads and re-exports environment files by default

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Without a `.dockerignore`, `COPY . .` has no way to know `.env` should be excluded — it copies the entire build context by default, and once a file is in a layer, `docker history` can expose it even if it's later deleted in a subsequent instruction.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [dockerignore, secret-leak, build-context]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Confirming the secret leak diagnostically
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 3 has you search `docker history --no-trunc`'s output for a known local password value. What does finding it there prove that simply knowing "`.env` wasn't excluded" does not?

**OPTIONS:**
- [ ] A: That the password is currently valid and could be used to log in to production
- [x] B: A concrete, verifiable confirmation that the secret actually made it into a built image layer — not just a theoretical risk from a missing `.dockerignore`, but proof it happened in this specific build
- [ ] C: That `pip install` failed during this particular build
- [ ] D: The exact line number of the `.env` file where the password is stored

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This step exists to make the risk visceral and countable rather than asserted — actually finding the value in a layer is the diagnostic proof the lesson's Practice Loop convention calls for.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [diagnostic-verification, secret-in-layer]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What HEALTHCHECK provides
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does declaring `HEALTHCHECK` directly in the Dockerfile provide that running the same `curl` command manually from outside the container would not?

**OPTIONS:**
- [ ] A: It makes the application itself run faster by pre-warming its caches
- [x] B: The liveness check becomes part of the image itself, so any tooling running the image — Compose, a bare `docker run`, or later Kubernetes — inherits a working health signal without reinventing one per deployment target
- [ ] C: It replaces the need for the application to expose a `/health` endpoint at all
- [ ] D: It is required syntax; a Dockerfile without `HEALTHCHECK` fails to build

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson frames `HEALTHCHECK` as portable, image-level metadata — the health signal travels with the image rather than being reinvented by whatever tool happens to run it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [healthcheck, image-portability]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Verifying the graceful-shutdown fix
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 5 times `docker stop` against containers from both the naive and fixed Dockerfiles. What result would confirm the exec-form fix actually worked?

**OPTIONS:**
- [x] A: The fixed image's container exits almost immediately, while the naive image's container waits out the full grace period before being force-killed
- [ ] B: Both containers exit at exactly the same speed, since `docker stop`'s grace period is a fixed, image-independent setting
- [ ] C: The fixed image's container takes longer to stop, since exec form adds extra signal-handling overhead
- [ ] D: Neither container ever stops cleanly, since `SIGTERM` is not supported inside containers at all

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the observable proof of the mechanism: exec form lets the app receive SIGTERM directly and exit promptly, while shell form's un-forwarded signal means the app never reacts until SIGKILL arrives at the end of the grace period.

**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [graceful-shutdown-verification, sigterm]

### QUESTION_BLOCK_END: Q8
### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Passing a version through ARG into ENV
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, a Dockerfile declares `ARG VERSION` followed by `ENV APP_VERSION=$VERSION`, and the image is built with `docker build --build-arg VERSION=1.5.0`. Why is this pattern necessary if the running container needs to read `APP_VERSION` from its environment?

**OPTIONS:**
- [ ] A: `ARG` values are automatically available as environment variables inside the running container, so the `ENV` line is redundant
- [x] B: `ARG` values exist only during the build and are not present in the running container by themselves; explicitly assigning the `ARG` value to an `ENV` variable is what makes it available at runtime
- [ ] C: `docker build --build-arg` sets environment variables directly on the host, bypassing the Dockerfile entirely
- [ ] D: `ENV` variables cannot reference `ARG` values under any circumstances

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is exactly the ARG-vs-ENV distinction applied concretely: the build-time-only ARG must be explicitly bridged into an ENV for the value to survive into the running container.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [arg-to-env-bridge, build-arg]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: Docker documentation — "Dockerfile reference" (https://docs.docker.com/reference/dockerfile/)

---

# LESSON 4

```yaml
lesson_id: fde-elective-containerization-orchestration-04-images-and-containers-deep-dive
lesson_title: "Images and Containers Deep Dive"
lesson_order: 4

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration (Elective)"
module_order: "Elective 1"

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Explain the PID 1 problem — why a process running as PID 1 inside a container does not get default signal handling and reaping behavior from the kernel — and when an init wrapper like tini is warranted."
  - "Read a container's actual exit code (0, 1, 137, 143) to distinguish an application crash from a SIGKILL, an unhandled SIGTERM, or an OOM kill, without guessing."
  - "Trace environment-variable precedence across Dockerfile ENV, docker run -e, and Compose environment/env_file, and predict which value wins when the same variable is set in more than one place."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Images and Containers Deep Dive

## Concepts Covered

Being PID 1 inside a container is not the same as being an ordinary process, and Lesson 3's exec-form fix does not fully solve this by itself. On a normal Linux system, PID 1 is `init` (or `systemd`), a process specifically designed to reap zombie child processes and to run default signal handlers for signals it hasn't explicitly registered a handler for. A container's PID 1, by contrast, is whatever your `ENTRYPOINT` names — your application code, not an init system — and the kernel does not retroactively grant it `init`'s special behaviors just because it happens to hold PID 1. Two concrete consequences follow: if your application never registers a `SIGTERM` handler, the *default* kernel action for `SIGTERM` (terminate the process) still applies, so a naive Python app without an explicit `signal.signal(SIGTERM, handler)` call does actually stop on `docker stop` — but only abruptly, with no chance to flush a buffer or finish an in-flight request, which is different from *ignoring* the signal. Second, and less obvious: if your application spawns child processes of its own (a shell script that forks a subprocess, for instance) and does not explicitly wait for and reap them, those children can become zombies that nothing ever cleans up, because there's no real `init` at PID 1 to do that reaping automatically. This second problem is why a minimal init wrapper like `tini` (`ENTRYPOINT ["tini", "--", "python", "-m", "ticket_api"]`) is the standard fix for any image whose main process forks children — `tini` becomes PID 1 instead, correctly reaps zombies, and forwards signals to your actual application as its own child.

Exit codes are a compact, standardized signal worth reading precisely rather than treating a nonzero code as an undifferentiated "it failed." `0` means clean exit; a small positive number (`1`, `2`) usually means the application itself raised an unhandled exception or called `sys.exit(1)`; `137` is `128 + 9`, meaning the process was killed by signal 9 (`SIGKILL`) — which for a container almost always means either the Docker daemon forcibly killed it after the stop grace period expired, or the kernel's OOM killer terminated it for exceeding its cgroup memory ceiling; `143` is `128 + 15`, meaning it received `SIGTERM` and actually exited in response to it (not necessarily gracefully, just that the signal reached and stopped the process) rather than being force-killed. `docker inspect --format='{{.State.OOMKilled}}'` disambiguates the two most common causes of `137` directly, rather than leaving you to guess between "ran over its memory limit" and "took too long to shut down after SIGTERM." Environment-variable precedence follows a fixed, memorizable order from least to most specific: a Dockerfile's `ENV` sets an image-baked default; `docker run -e VAR=value` (or Compose's `environment:` key) overrides it at container-start time; and an `env_file` entry, depending on the exact tool, typically sits between those two — the practical rule that matters operationally is that anything specified at `docker run` or Compose service level always beats whatever the image itself baked in as a default, which is precisely the mechanism that lets the same image run with different database URLs in staging and production without being rebuilt.

```bash
# PID 1 has no special init behavior unless you provide it
$ docker run --rm ticket-api ps aux
PID   USER     COMMAND
    1 appuser  python -m ticket_api      # the app itself, not an init process

# Reading an exit code precisely
$ docker run --rm --memory=64m ticket-api-worker
$ echo $?
137
$ docker inspect ticket-api-worker --format='{{.State.OOMKilled}}'
true    # confirms this 137 was the kernel OOM killer, not docker stop's SIGKILL

$ docker stop ticket-api           # sends SIGTERM, waits 10s, then SIGKILL
$ docker inspect ticket-api --format='{{.State.ExitCode}}'
143     # the app received SIGTERM and exited in response to it

# tini as PID 1, correctly forwarding signals and reaping children
ENTRYPOINT ["tini", "--", "python", "-m", "ticket_api"]
```

## Practical Backend Scenario

Vantage's rollout process restarts `ticket-api`'s background worker container during every deploy. The worker, which processes photo-attachment uploads by shelling out to `subprocess.run` for image resizing, starts leaving zombie processes behind after several days of uptime — `ps aux` inside the container slowly accumulates `[resize] <defunct>` entries, because the worker's own Python process is PID 1 and never explicitly reaps the children it spawns, and there is no real init process present to do it automatically. Separately, during one deploy the worker is killed mid-task and the deployment log shows exit code `137`; the on-call FDE initially assumes this is an unhandled crash, but `docker inspect --format='{{.State.OOMKilled}}'` on the stopped container returns `true` — the worker actually exceeded its 256MB memory ceiling while resizing an unusually large uploaded photo, not crashed on bad input as first assumed. Both problems trace back to the same root cause treated two different ways: the zombie-process issue is fixed by adding `tini` as the actual PID 1 (`ENTRYPOINT ["tini", "--", "python", "-m", "worker"]`), and the OOM issue is fixed not by "handling the crash better" in application code but by either raising the memory ceiling to match the worker's real peak usage or downsizing images in a streaming fashion that never holds a full-resolution copy in memory at once.

## Practice Loop

1. Run `ticket-api`'s worker container without `tini`, have it spawn a child `subprocess` that exits, and run `ps aux` inside the container repeatedly to watch a `<defunct>` zombie entry accumulate and never clear.
2. Add `tini` as the entrypoint wrapper, repeat step 1, and confirm the zombie no longer appears — `tini` is reaping it.
3. Run the worker with `--memory=64m` against a workload you know will exceed that ceiling, then run `docker inspect --format='{{.State.ExitCode}} {{.State.OOMKilled}}'` and record both values, confirming `137` plus `OOMKilled: true` together, not just the exit code alone.
4. Run `docker stop` against a healthy worker and inspect its exit code, confirming `143` — then compare this to step 3's `137` to build a habit of distinguishing the two by more than "the container died."
5. Set the same environment variable (`DATABASE_URL`) in the Dockerfile's `ENV`, then override it with `docker run -e DATABASE_URL=...`, and confirm inside the running container which value actually won, verifying the precedence rule rather than assuming it.

## Evidence of Understanding

You can explain why a container's PID 1 does not automatically get an `init` process's zombie-reaping and default-signal behavior, and when adding `tini` as the real PID 1 is warranted (any image whose main process forks children it does not explicitly reap). You can read exit codes 137 and 143 precisely, and use `docker inspect`'s `OOMKilled` field to disambiguate a memory-limit kill from a `docker stop`-driven `SIGKILL`, rather than treating any container death as an undifferentiated crash. You can predict which value wins when the same environment variable is set in a Dockerfile's `ENV` and overridden at `docker run` or Compose level, and demonstrate it rather than assume it.

## Suggested Extension
Reduce the worker's memory ceiling until it reliably OOM-kills on a normal-sized (not unusually large) upload, then rewrite the image-resize step to stream the file instead of loading it fully into memory, and confirm the same ceiling no longer triggers `OOMKilled: true` for the same workload.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What PID 1 does NOT automatically get
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why doesn't a container's application process, running as PID 1, automatically behave like a normal system's `init`/`systemd` process?

**OPTIONS:**
- [x] A: The kernel does not retroactively grant special init behaviors (zombie reaping, default signal handling for unregistered signals) to whatever process happens to hold PID 1 — those behaviors belong to actual init software, not to the PID number itself
- [ ] B: Docker explicitly disables all signal handling for any process running as PID 1
- [ ] C: PID 1 is reserved and containers are never actually allowed to run application code as PID 1
- [ ] D: Only processes started with `sudo` inside a container can act as a true init process

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is precise here: PID 1's special behaviors come from being real init software, not from the PID number — a container's ENTRYPOINT process is ordinary application code that happens to hold that number.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [pid-1-problem, init-behavior]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** When tini is actually warranted
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, which situation specifically calls for adding `tini` as a container's real PID 1?

**OPTIONS:**
- [ ] A: Any container at all, regardless of what its main process does, as an unconditional best practice
- [x] B: A main process that spawns its own child processes (e.g. shelling out to a subprocess) without explicitly reaping them, since without a real init at PID 1 those children can become unreaped zombies
- [ ] C: Only containers that expose an HTTP port
- [ ] D: Only containers running as a non-root user

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson ties `tini`'s value specifically to the zombie-reaping problem, which only arises when the main process forks children it doesn't reap itself — not a blanket recommendation for every image.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [tini, zombie-reaping, when-to-use]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading exit code 137
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ echo $?
137
$ docker inspect worker --format='{{.State.OOMKilled}}'
true
```

**QUESTION_TEXT:**
Given this output, what does exit code 137 combined with `OOMKilled: true` tell you, precisely?

**OPTIONS:**
- [ ] A: The application raised an unhandled Python exception
- [x] B: The process was killed by signal 9 (SIGKILL, since 137 = 128 + 9), and specifically because the kernel's OOM killer terminated it for exceeding its cgroup memory ceiling, not because of a `docker stop` timeout
- [ ] C: The container exited cleanly with a warning
- [ ] D: The process received SIGTERM and shut down gracefully in response

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
137 alone only tells you SIGKILL happened; `OOMKilled: true` is what disambiguates an OOM kill from a `docker stop` grace-period SIGKILL, exactly as the lesson describes.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [exit-code-137, oom-killed]

### QUESTION_BLOCK_END: Q3
### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** 137 vs 143
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the specific difference in meaning between exit code 137 and exit code 143?

**OPTIONS:**
- [ ] A: 137 means the application crashed; 143 means it exited cleanly with no signal involved
- [x] B: 137 (128+9) means the process was force-killed with SIGKILL; 143 (128+15) means the process received SIGTERM and exited in response to it, without necessarily being forcibly killed afterward
- [ ] C: They are two different encodings of the same underlying signal, chosen arbitrarily by the container runtime
- [ ] D: 137 applies only to worker containers; 143 applies only to web-facing containers

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is exact signal arithmetic: 128 + signal number. SIGKILL is signal 9 (137), SIGTERM is signal 15 (143) — one is a hard kill, the other is the terminate-request the process actually responded to.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [exit-code-arithmetic, sigkill-vs-sigterm]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the FDE misdiagnosed the worker's death
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why did the on-call FDE initially assume the worker had crashed on bad input, when the actual cause was different?

**OPTIONS:**
- [ ] A: The deployment log showed exit code 1, which is conventionally associated with input validation failures
- [x] B: Exit code 137 alone does not distinguish an OOM kill from other causes of SIGKILL; only checking `OOMKilled` via `docker inspect` revealed the worker had exceeded its 256MB memory ceiling while resizing an unusually large image
- [ ] C: The worker's logs were deleted before the FDE could review them
- [ ] D: PostgreSQL rejected the worker's connection due to a credential mismatch

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the scenario's point precisely: a bare 137 invites a guess, and only the explicit `OOMKilled` check turns the guess into a confirmed diagnosis of a memory-ceiling breach, not an application bug.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [misdiagnosis, oomkilled-field]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Environment variable precedence
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A Dockerfile sets `ENV DATABASE_URL=postgres://localhost/dev`, and the container is started with `docker run -e DATABASE_URL=postgres://prod-db/app ticket-api`. Which value does the running application actually see?

**OPTIONS:**
- [ ] A: `postgres://localhost/dev`, since the image-baked default always wins
- [x] B: `postgres://prod-db/app`, since a value passed at `docker run` (or Compose service level) overrides the image's baked-in default
- [ ] C: Both values are concatenated into a single string
- [ ] D: Neither value is used; the application must read a separate config file

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson states the practical precedence rule directly: `docker run`/Compose-level values beat whatever the image baked in as a default, which is exactly what lets one image run correctly in both staging and production.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [env-precedence, docker-run-override]

### QUESTION_BLOCK_END: Q6
### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Verifying tini's fix diagnostically
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop steps 1 and 2 have you watch for a `<defunct>` zombie entry in `ps aux` without `tini`, then confirm it disappears with `tini` added. What does the disappearance specifically prove?

**OPTIONS:**
- [ ] A: That `tini` made the worker's image-resize subprocess run faster
- [x] B: That `tini`, now running as the real PID 1, is correctly reaping the child processes the worker spawns — the exact mechanism the zombie accumulation problem was missing without it
- [ ] C: That the worker no longer spawns any subprocesses at all
- [ ] D: That the worker's memory ceiling was the actual cause of the zombie processes

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This diagnostic step directly confirms the mechanism claimed in Concepts Covered: with `tini` as PID 1, reaping happens correctly, which is observable as the zombie no longer persisting.

**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [tini-verification, zombie-diagnostic]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Distinguishing 137 from 143 in the practice loop
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 4 has you run `docker stop` on a healthy worker and compare its exit code to step 3's memory-limited run. What result would you expect if both fixes from this lesson are correctly understood?

**OPTIONS:**
- [x] A: Step 3 (memory-limited) shows 137 with `OOMKilled: true`; step 4 (`docker stop`) shows 143, since the process received and responded to SIGTERM rather than being force-killed by the OOM killer
- [ ] B: Both steps should show identical exit codes, since any container termination is functionally the same event
- [ ] C: Step 4 should also show `OOMKilled: true`, since `docker stop` always exceeds the memory ceiling
- [ ] D: Step 3 should show 143 and step 4 should show 137, the reverse of the correct mapping

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the exact contrast the Practice Loop is built to demonstrate: two different causes of container death produce two distinguishable, correctly-attributable exit codes.

**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [exit-code-comparison, practice-loop-diagnostic]

### QUESTION_BLOCK_END: Q8
### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Fixing the OOM kill correctly
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, why does streaming the image-resize step instead of loading the full file into memory fix the recurring OOM kill, rather than simply raising the memory ceiling indefinitely?

**OPTIONS:**
- [ ] A: Raising the memory ceiling is architecturally impossible in Docker past a fixed maximum
- [x] B: Raising the ceiling only postpones the same failure for a larger future upload; reducing the worker's actual peak memory usage (by never holding a full-resolution copy in memory) fixes the root cause rather than moving the threshold
- [ ] C: Streaming makes the resize operation itself run in a separate container automatically
- [ ] D: `docker inspect` refuses to report `OOMKilled` for containers with a memory ceiling above 512MB

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This extension is designed to push past the reflexive "raise the limit" fix toward the actually durable one — reducing real peak memory usage, since any fixed ceiling can eventually be exceeded by a large enough input.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [oom-root-cause-fix, streaming-vs-ceiling]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: Docker documentation — "Run multiple processes in a container" / tini project README (https://github.com/krallin/tini)

---

# LESSON 5

```yaml
lesson_id: fde-elective-containerization-orchestration-05-docker-volumes
lesson_title: "Docker Volumes"
lesson_order: 5

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration (Elective)"
module_order: "Elective 1"

difficulty: Intermediate
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Choose between a named volume, a bind mount, and no persistence at all, based on who owns the data and where it needs to be portable."
  - "Back up and restore a named volume's contents using a throwaway container, without stopping the volume's owning service any longer than necessary."
  - "Apply the twelve-factor boundary between code and state to a container's filesystem, explaining exactly what a container recreation is and is not allowed to lose."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Docker Volumes

## Concepts Covered

A named volume (`docker volume create ticket-uploads`) is storage Docker manages entirely on the host's behalf, at a location the daemon controls (typically under `/var/lib/docker/volumes/`), addressed only by name — you do not need to know or care about the host path to use one. A bind mount (`docker run -v $(pwd)/config:/etc/ticket-api`) instead maps a specific, already-existing host path directly into the container, which is the right tool when a human on the host needs to edit the file directly (local development config, a certificate the host's own tooling also manages) but the wrong tool for a service's actual data directory, since a bind mount ties the container to one specific host's filesystem layout in a way that breaks the moment the container is scheduled onto a different machine. Named volumes are the portable choice precisely because *Docker* owns the mapping from name to location, not the Dockerfile or the person running `docker run` — the same `docker run -v ticket-uploads:/data/uploads` command works on any host, because "where `ticket-uploads` actually lives" is a detail the volume driver resolves, not something baked into the command itself.

This is the twelve-factor "processes are stateless, backing services are attached resources" boundary applied literally to a container's own filesystem: everything a container writes without an explicit volume mount lands in its writable layer, discussed in Lesson 2, and is destroyed with the container; everything that must survive a container being stopped, removed, and recreated — a Postgres data directory, uploaded attachment files, a Redis append-only file — has to live in a named volume or an external, managed data store, not in the container's own filesystem at all. Ownership matters as much as location: a named volume attached to `ticket-api`'s container is, from the ops team's perspective, owned and lifecycled by whatever creates and mounts it, and its backup responsibility does not disappear just because Docker is managing where the bytes physically sit — someone still has to define and test the backup and restore path, since `docker volume rm` deletes it as completely and irreversibly as any other filesystem deletion. Backing up a named volume does not require stopping the container that uses it for read access, but it does require care about consistency: backing up a live Postgres data directory by simply `tar`-ing its volume while the database is actively writing to it can capture a filesystem-level, not transaction-level, consistent snapshot, which is why the backup pattern below uses a throwaway container that mounts the *same* volume rather than reaching into the running service's own container.

```bash
# Create and inspect a named volume
$ docker volume create ticket-uploads
ticket-uploads

$ docker volume inspect ticket-uploads
[
    {
        "Name": "ticket-uploads",
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/ticket-uploads/_data",
        "Scope": "local"
    }
]

# Attach it to the running service
$ docker run -d --name ticket-api \
    -v ticket-uploads:/data/uploads \
    -p 8080:8080 ticket-api:1.4.2

# Bind mount for config a human needs to edit directly
$ docker run -d --name ticket-api \
    -v ticket-uploads:/data/uploads \
    --mount type=bind,source="$(pwd)/config",target=/etc/ticket-api,readonly \
    -p 8080:8080 ticket-api:1.4.2

# Back up the volume with a throwaway container — does not touch ticket-api
$ docker run --rm \
    -v ticket-uploads:/data:ro \
    -v "$(pwd)":/backup \
    alpine tar czf /backup/uploads-backup-$(date +%F).tar.gz -C /data .

# Restore into a fresh (or the same) volume
$ docker run --rm \
    -v ticket-uploads:/data \
    -v "$(pwd)":/backup \
    alpine tar xzf /backup/uploads-backup-2026-08-15.tar.gz -C /data
```

## Practical Backend Scenario

Vantage's dispatchers use `ticket-api`'s technician-facing upload feature to attach photos to a field-service ticket, saved to `/data/uploads` inside the container. During a routine deploy, the ops team runs `docker rm -f ticket-api && docker run ... ticket-api:1.5.0` to pick up the new version — and every photo any technician had ever uploaded is gone, because `/data/uploads` was never mounted to a volume; it was writing directly into the old container's writable layer the entire time, which was destroyed the instant `docker rm -f` ran. The fix is not "be more careful about when you run `docker rm`" — it is moving `/data/uploads` onto a named volume (`ticket-uploads`) so the data's lifecycle is decoupled from any one container's lifecycle entirely; recreating the container for a deploy then genuinely means only the application code changes, while `-v ticket-uploads:/data/uploads` on the new container's `docker run` command reattaches the exact same underlying storage, uploads intact, with zero copying or migration required.

## Practice Loop

1. Reproduce the failure: run `ticket-api` without a volume mount, upload a test attachment, `docker rm -f` the container, start a fresh one from the same image, and confirm the attachment is genuinely gone.
2. Create the named volume `ticket-uploads` and rerun the same sequence with `-v ticket-uploads:/data/uploads` on both the old and the recreated container, confirming the attachment survives this time.
3. Count exactly how many bytes exist under the volume's `Mountpoint` on the host (`sudo du -sh $(docker volume inspect ticket-uploads --format='{{.Mountpoint}}')`) before and after an upload, to confirm the data is really landing on the host-managed volume location, not somewhere else.
4. Back up the volume using the throwaway-container pattern above without stopping `ticket-api`, then delete a test file from inside the volume and restore from the backup to confirm the restore path actually works, not just the backup step.
5. Add a bind-mounted, read-only config file for a setting the ops team needs to hand-edit on the host, and explain in one sentence why this setting is a bind mount while the uploads are a named volume.

## Evidence of Understanding

You can choose between a named volume, a bind mount, and no persistence at all for a given piece of container state, justified by who needs to read or edit it directly and whether it needs to be portable across hosts. You can back up and restore a named volume's contents using a throwaway container that mounts the same volume, without stopping the volume's owning service any longer than the backup itself takes. You can state, for any given container recreation, exactly what survives (anything in a mounted volume) and what does not (anything in the writable layer alone), and explain why decoupling data lifecycle from container lifecycle is the actual fix, not operational carefulness.

## Suggested Extension
Configure `ticket-api`'s Postgres dependency to use a named volume for its data directory as well, then run a full `docker compose down && docker compose up` cycle and confirm the database's data survives, distinguishing `docker compose down` (containers removed, named volumes kept by default) from `docker compose down -v` (which also removes volumes) by testing both.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Named volume vs bind mount
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the key structural difference between a named volume and a bind mount?

**OPTIONS:**
- [ ] A: A named volume is always faster to read from than a bind mount
- [x] B: A named volume's actual storage location is managed and resolved by Docker itself, addressed only by name; a bind mount maps a specific, already-known host path directly into the container
- [ ] C: Bind mounts persist data across container recreation, while named volumes do not
- [ ] D: Named volumes can only be used with PostgreSQL containers

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson draws this distinction precisely: Docker owns the name-to-location mapping for a named volume, while a bind mount ties the container to a specific, pre-known host path.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [named-volume, bind-mount]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why bind mounts break portability
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue a bind mount is the wrong tool for a service's actual application data, even though it works fine on the machine where it was first configured?

**OPTIONS:**
- [ ] A: Bind mounts are deprecated and will be removed from a future Docker release
- [x] B: A bind mount ties the container to one specific host's filesystem layout, which breaks the moment the container is scheduled onto a different machine that doesn't have that exact path
- [ ] C: Bind mounts cannot be made read-only under any circumstances
- [ ] D: Bind mounts silently corrupt data larger than 1GB

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific objection is portability: a hardcoded host path assumption is exactly what breaks when the container later runs somewhere else, which a named volume's Docker-managed indirection avoids.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [bind-mount-portability, host-path-coupling]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why the attachments were lost
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did every technician-uploaded photo disappear when Vantage's ops team ran `docker rm -f ticket-api` during a routine deploy?

**OPTIONS:**
- [ ] A: The deploy script explicitly issued a `DELETE FROM uploads` command against the database
- [x] B: `/data/uploads` was never mounted to a volume, so every uploaded file was written only into the old container's writable layer, which was destroyed the instant that container was removed
- [ ] C: `docker rm -f` always deletes the underlying image along with the container
- [ ] D: The new image version, `ticket-api:1.5.0`, used a different upload path than `1.4.2`

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This directly connects Lesson 2's writable-layer mechanism to this lesson's fix: without a volume mount, uploads live only in the writable layer, which is removed with the container.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [writable-layer-data-loss, missing-volume-mount]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the fix decouples data from container lifecycle
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson argues the correct fix is not "be more careful about when you run `docker rm`" but decoupling the data's lifecycle from any one container's lifecycle. Why is this framing more robust?

**OPTIONS:**
- [x] B: "Be more careful" depends on every future operator remembering a rule with no structural enforcement; mounting the data onto a named volume makes the correct behavior (data survives container recreation) true by construction, regardless of who runs the recreate command
- [ ] A: `docker rm -f` is a deprecated command that should never be used for any reason
- [ ] C: Named volumes prevent `docker rm -f` from being run at all while data exists inside them
- [ ] D: Careful operators never make mistakes, so the framing is purely stylistic

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the lesson's underlying design principle: a structural fix (decoupled lifecycle via a volume) is robust to operator error in a way a procedural rule ("be careful") never is.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [structural-fix, lifecycle-decoupling]

### QUESTION_BLOCK_END: Q4
### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the backup uses a throwaway container
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
$ docker run --rm \
    -v ticket-uploads:/data:ro \
    -v "$(pwd)":/backup \
    alpine tar czf /backup/uploads-backup-$(date +%F).tar.gz -C /data .
```

**QUESTION_TEXT:**
Why does this backup command run a separate, throwaway `alpine` container that mounts the same volume, rather than executing the `tar` command inside `ticket-api`'s own running container?

**OPTIONS:**
- [ ] A: `alpine` is required because `tar` cannot run inside a Python-based image
- [x] B: Any container that mounts the same named volume can read its contents; using a disposable one avoids installing backup tooling into the production image and avoids interfering with the service container's own process
- [ ] C: `docker run --rm` is the only flag combination that can mount a volume as read-only
- [ ] D: `ticket-api`'s container does not have permission to read its own mounted volume

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Since a volume is addressable by name from any container, a throwaway utility container is the cleanest way to read it for backup purposes without bloating or touching the actual service container.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [backup-pattern, throwaway-container]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Verifying the fix in the practice loop
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 2 has you repeat the failure-reproduction sequence with `-v ticket-uploads:/data/uploads` added, this time on both the old and the recreated container. What specifically confirms the fix worked?

**OPTIONS:**
- [ ] A: The recreated container starts faster than the original
- [x] B: The test attachment uploaded to the old container is still present after the old container is removed and a fresh one, mounting the same volume, is started
- [ ] C: The image size shrinks after adding the volume mount
- [ ] D: `docker ps` shows the container's status as "healthy" instead of "running"

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the direct before/after proof: the same volume attached to a new container after the old one is removed retains the earlier data, which is exactly what step 1's reproduction showed failing without the mount.

**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [fix-verification, volume-persistence]

### QUESTION_BLOCK_END: Q6
### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** `docker compose down` vs `down -v`
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, what is the actual difference in behavior between `docker compose down` and `docker compose down -v`?

**OPTIONS:**
- [ ] A: `down -v` only affects bind mounts, not named volumes
- [x] B: `docker compose down` removes containers and networks but keeps named volumes by default; `docker compose down -v` also removes those named volumes, permanently deleting their contents
- [ ] C: `down -v` runs in verbose mode and produces more log output, but behaves identically otherwise
- [ ] D: `docker compose down` deletes named volumes; `down -v` preserves them

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the exact distinction the extension is designed to make concrete by testing both — `-v` is the flag that actually escalates from "recreate containers" to "also destroy the persisted data."

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [compose-down, volume-deletion-flag]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Choosing bind mount vs volume for config
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 5 adds a read-only bind-mounted config file the ops team needs to hand-edit on the host, while uploads stay on a named volume. What justifies this split, per the lesson's framework?

**OPTIONS:**
- [x] A: A human needs to directly read and edit the config file on the host filesystem, which is exactly what a bind mount is for; the uploads need portable, Docker-managed storage that isn't tied to one host's path layout, which is exactly what a named volume is for
- [ ] B: Config files must always use bind mounts and data files must always use named volumes, as an unconditional Docker rule
- [ ] C: Read-only files can only be attached via bind mounts, never via named volumes
- [ ] D: The split is arbitrary; either mechanism would work identically for both use cases

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's decision criterion is not the file's type but who needs direct access and whether portability matters — a human editing on the host favors a bind mount, application data needing portability favors a named volume.

**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [mount-choice-justification, config-vs-data]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

Reference: Docker documentation — "Manage data in Docker" / "Volumes" (https://docs.docker.com/engine/storage/volumes/)

---

# LESSON 6

```yaml
lesson_id: fde-elective-containerization-orchestration-06-docker-networking-deep-dive
lesson_title: "Docker Networking Deep Dive"
lesson_order: 6

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration (Elective)"
module_order: "Elective 1"

difficulty: Intermediate
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Distinguish EXPOSE (documentation only) from a published port (-p host:container, the actual host-reachable surface), and audit a running deployment's real exposure with docker ps and docker port."
  - "Use a user-defined bridge network and Docker's embedded DNS to let containers reach each other by service name, without publishing internal-only services to the host."
  - "Trace a request from host to edge container to an internal service, and diagnose an unreachable service using docker exec plus a network utility rather than guessing at the failure layer."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Docker Networking Deep Dive

## Concepts Covered

By default, `docker run` attaches a new container to the default `bridge` network, a single flat network where every container can reach every other container by IP, but not by any predictable name — the default bridge does not run Docker's embedded DNS server, which is why relying on it for multi-container communication tends to produce brittle setups pinned to IP addresses that change on every restart. A user-defined bridge network (`docker network create ticket-net`) fixes this: any container started with `--network ticket-net` can reach any other container on that same network by its container name (or Compose service name) as a DNS hostname, resolved by Docker's embedded DNS server running inside the network's own scope — `ticket-api` can `curl http://ticket-db:5432` and get a real connection, not because `ticket-db` is a magic reserved word, but because that is literally the container's `--name` on the same user-defined network. A second, entirely separate user-defined network gives you actual network-level isolation: a container attached only to `ticket-net` genuinely cannot reach a container that exists only on a different network, `admin-net`, which is the mechanism (not a firewall rule bolted on afterward) behind restricting which services can talk to which.

`EXPOSE` in a Dockerfile is documentation, not enforcement — it tells a human (and tools like `docker inspect`) which port the containerized application listens on, but it does not, by itself, make that port reachable from the host or from any other network. Actual host reachability is controlled entirely by the `-p` (or `--publish`) flag on `docker run`, or the `ports:` key in a Compose file: `-p 8080:80` maps host port 8080 to the container's port 80, and without an explicit `-p`, no container port — `EXPOSE`d or not — is reachable from the host at all, only from other containers on the same Docker network. This is exactly the distinction that separates an internal service (a database, an internal admin API) that should never leave the container network from an edge service (the public-facing API) that legitimately needs a host-published port; accidentally adding a `-p` to a service that should have stayed internal-only is the single most common way a service intended to be private ends up reachable from outside the host. Diagnosing "my API can't reach my database" is a layered question, not a single check: confirm both containers are actually on the same user-defined network (`docker network inspect ticket-net`), confirm the target container's application is actually listening inside its own namespace (`docker exec ticket-db netstat -tlnp`), then confirm reachability from the caller's side (`docker exec ticket-api nc -zv ticket-db 5432`) — working through these in order isolates whether the problem is network attachment, the target application not binding correctly, or something in between, rather than guessing at all three simultaneously.

```bash
# A private network for ticket-api and its database
$ docker network create ticket-net

$ docker run -d --name ticket-db --network ticket-net \
    -e POSTGRES_PASSWORD=devpassword postgres:16

# ticket-api joins the same network and reaches ticket-db by name —
# note: NOT published to the host, so it's unreachable from outside
$ docker run -d --name ticket-api --network ticket-net \
    -e DATABASE_URL=postgres://ticket-db:5432/tickets \
    ticket-api:1.4.2

# Only the edge service is published to the host
$ docker run -d --name ticket-api --network ticket-net \
    -e DATABASE_URL=postgres://ticket-db:5432/tickets \
    -p 8080:8080 ticket-api:1.4.2

# Confirm what's actually reachable from outside the host
$ docker port ticket-api
8080/tcp -> 0.0.0.0:8080
$ docker port ticket-db
# (no output — nothing published; only reachable inside ticket-net)

# Diagnose "API can't reach DB" layer by layer
$ docker network inspect ticket-net --format='{{range .Containers}}{{.Name}} {{end}}'
ticket-api ticket-db
$ docker exec ticket-db netstat -tlnp | grep 5432
tcp6  0  0  :::5432  :::*  LISTEN  1/postgres
$ docker exec ticket-api nc -zv ticket-db 5432
ticket-db (172.19.0.3:5432) open
```

## Practical Backend Scenario

Vantage's `docker-compose.yml` for staging defines `ticket-api` and `ticket-db` as two services on the same Compose-managed network, and `ticket-api` reaches `ticket-db` by its service name without incident. During a rushed fix for a local testing issue, an engineer adds `ports: ["5432:5432"]` to the `ticket-db` service so they can connect a local GUI database client directly — and forgets to remove it before the change ships to the shared staging environment, which happens to sit on a network reachable from outside Vantage's office. The database, which was never intended to be reachable from anywhere but `ticket-api` itself, is now listening on the public internet with only its default password protecting it, discovered only when a routine external port scan flags it. The fix is not "remember to remove debug ports before merging" as a hope; it is treating `ports:` (a published, host-reachable port) as categorically different from container-to-container reachability on the shared network — `ticket-db` never needed a published port at all for `ticket-api` to reach it, since Docker's embedded DNS and the shared network already provided that, and a policy of "only the edge service gets a `ports:` entry, ever" would have made this specific mistake structurally impossible rather than just discouraged.

## Practice Loop

1. Create a user-defined network and start `ticket-db` and `ticket-api` on it without publishing either port, then confirm `ticket-api` can reach `ticket-db` by name using `docker exec ticket-api nc -zv ticket-db 5432`.
2. Attempt to connect to `ticket-db` from your host machine directly (outside any container) on port 5432, and confirm the connection is refused — nothing is published, so nothing is reachable from outside.
3. Publish `ticket-api`'s port with `-p 8080:8080` only, and count exactly which of the two containers `docker port` reports as reachable from the host — this diagnostic makes the EXPOSE-vs-publish distinction concrete rather than asserted.
4. Reproduce the scenario's mistake deliberately: add `-p 5432:5432` to `ticket-db` as well, confirm it is now reachable from the host, then remove it and confirm the exposure is gone again.
5. Diagnose a deliberately broken setup (start `ticket-api` on a *different* network than `ticket-db`) using the three-step layered method — network attachment, target listening, caller reachability — and identify which layer fails first.

## Evidence of Understanding

You can explain why `EXPOSE` alone never makes a port reachable from the host, and that only `-p`/`--publish` (or Compose's `ports:`) does, with `docker port` as the audit tool for what is actually published on a running deployment. You can attach containers to a user-defined bridge network and use Docker's embedded DNS to let them reach each other by name, without publishing any port that only needs to be reachable internally. You can diagnose an unreachable service by checking network attachment, target-side listening, and caller-side reachability in that order, rather than guessing at which of the three failed.

## Suggested Extension
Add a second, separate network (`admin-net`) for a hypothetical internal admin container, attach `ticket-db` to both `ticket-net` and `admin-net`, but keep `ticket-api` on `ticket-net` only — confirm `ticket-api` still cannot reach anything on `admin-net`, demonstrating that network membership, not just port publication, is an independent isolation boundary.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Default bridge vs user-defined bridge
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the practical difference between the default `bridge` network and a user-defined bridge network for container-to-container communication?

**OPTIONS:**
- [x] A: A user-defined bridge network runs Docker's embedded DNS, letting containers reach each other by container name; the default bridge does not, leaving containers pinned to IP addresses that can change on restart
- [ ] B: The default bridge network is faster because it skips DNS resolution entirely, by design
- [ ] C: User-defined bridge networks are only available in Docker Swarm mode, not plain `docker run`
- [ ] D: There is no functional difference; the naming is purely cosmetic

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is explicit: the embedded DNS server that resolves container names is scoped to user-defined networks, not the default bridge, which is exactly why the default bridge produces brittle, IP-pinned setups.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [default-bridge, user-defined-network, embedded-dns]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** EXPOSE vs publish
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A Dockerfile contains `EXPOSE 8080`, but the container is started with plain `docker run ticket-api` (no `-p` flag). Is port 8080 reachable from the host machine?

**OPTIONS:**
- [ ] A: Yes, `EXPOSE` alone is sufficient to publish a port to the host
- [x] B: No — `EXPOSE` is documentation only; only `-p`/`--publish` (or Compose's `ports:`) actually makes a container port reachable from the host
- [ ] C: Yes, but only if the container is also on the default bridge network
- [ ] D: It depends on whether the image's base is Alpine or Debian

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's central distinction: `EXPOSE` documents intent for humans and tooling, while actual host reachability requires an explicit publish flag — no publish flag means no host reachability, regardless of `EXPOSE`.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [expose-vs-publish]

### QUESTION_BLOCK_END: Q2
### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading `docker port` output
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ docker port ticket-api
8080/tcp -> 0.0.0.0:8080
$ docker port ticket-db
(no output)
```

**QUESTION_TEXT:**
Given this output, what does the absence of any line for `ticket-db` tell you?

**OPTIONS:**
- [x] A: `ticket-db` has no published ports at all — it is reachable only from other containers on its shared Docker network, not from the host or outside world
- [ ] B: `ticket-db` is not currently running
- [ ] C: `ticket-db`'s image failed to declare an `EXPOSE` instruction, which is required for `docker port` to report anything
- [ ] D: `docker port` only works for containers started via Compose, not plain `docker run`

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
`docker port` reports actual published mappings; no output means no `-p` flag was used for that container, meaning no host-level reachability, consistent with the scenario's intended design.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [docker-port, publish-audit]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** How the database got exposed to the internet
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, what specific change made `ticket-db` reachable from outside Vantage's office network, when it had never needed to be?

**OPTIONS:**
- [ ] A: `ticket-api` was moved onto a different Docker network than `ticket-db`
- [x] B: An engineer added `ports: ["5432:5432"]` to the `ticket-db` Compose service for local debugging, which published the database port to the host, and the change was never removed before shipping to shared staging
- [ ] C: The default `bridge` network was used instead of a user-defined one
- [ ] D: `EXPOSE 5432` was added to the database's Dockerfile

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scenario's root cause is precisely the publish flag, not the network topology or `EXPOSE` — `ticket-api` never needed a published `ticket-db` port to reach it over the shared Docker network.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [accidental-port-publish, scenario-root-cause]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why a structural policy beats "remember to remove it"
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson argues that "only the edge service ever gets a `ports:` entry" would have made the scenario's mistake structurally impossible. Why is this stronger than "remember to remove debug ports before merging"?

**OPTIONS:**
- [ ] A: Docker technically enforces a maximum of one published port per Compose file, so the policy is redundant
- [x] B: A policy that never grants internal-only services a `ports:` entry in the first place removes the failure mode entirely, rather than depending on every future engineer remembering to reverse a temporary change before it ships
- [ ] C: `ports:` entries automatically expire after 24 hours in Compose, making the concern moot
- [ ] D: "Remember to remove it" and the structural policy are functionally identical in practice

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This mirrors the same structural-fix-over-procedural-discipline argument from Lesson 5: a rule that makes a mistake impossible by construction is more reliable than one that depends on remembering to undo a temporary change.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [structural-policy, edge-only-publish]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** The three-layer diagnostic order
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's diagnostic method, in what order should you check network attachment, target-side listening, and caller-side reachability when `ticket-api` can't reach `ticket-db`?

**OPTIONS:**
- [x] A: First confirm both containers are on the same network, then confirm the target is actually listening inside its own namespace, then confirm reachability from the caller's side — isolating which layer fails before assuming the cause
- [ ] B: The order does not matter; any single check is sufficient to diagnose the failure
- [ ] C: Always start by restarting both containers before running any diagnostic command
- [ ] D: Check caller-side reachability first, since it is the only check that ever actually reveals the cause

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson lays out this exact sequence and explains why: working through the layers in order isolates whether the fault is network attachment, application binding, or reachability, rather than guessing at all three simultaneously.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [layered-diagnosis, network-troubleshooting]

### QUESTION_BLOCK_END: Q6
### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Practice Loop step 2's confirmation
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 2 has you attempt a direct host-to-database connection on port 5432 with neither port published, and expect it to be refused. What does a successful refusal specifically confirm?

**OPTIONS:**
- [ ] A: That `ticket-db`'s application crashed and is not running at all
- [x] B: That with no `-p` flag published for `ticket-db`, the host genuinely has no path to reach it — proving the "no publish, no host reachability" rule rather than just asserting it
- [ ] C: That the user-defined network was created with the wrong subnet
- [ ] D: That PostgreSQL requires authentication before accepting any connection, unrelated to Docker networking

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This diagnostic step exists to make the EXPOSE/publish rule concrete: attempting and failing to connect from the host is direct evidence of the boundary the lesson describes, not just a repeated assertion of it.

**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [publish-boundary-verification]

### QUESTION_BLOCK_END: Q7
### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Network membership as an independent boundary
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Suggested Extension, `ticket-db` is attached to both `ticket-net` and `admin-net`, while `ticket-api` stays on `ticket-net` only. Why does `ticket-api` still fail to reach anything on `admin-net`?

**OPTIONS:**
- [x] A: Network membership is its own isolation boundary, independent of any one container's other memberships — being on `ticket-net` gives `ticket-api` reachability only within `ticket-net`, not transitively through `ticket-db`'s separate membership in `admin-net`
- [ ] B: `ticket-db` being on two networks automatically merges them into one for every other container
- [ ] C: `admin-net` requires a published port to be reachable from any container, unlike `ticket-net`
- [ ] D: This configuration is not actually possible; a container can only join one network at a time

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This extension demonstrates that network membership is per-container and non-transitive — a container bridging two networks does not grant reachability between all members of both networks, only between its own two memberships.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [network-isolation, non-transitive-membership]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Publishing only the edge service
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
For a deployment with one public-facing API and one internal-only database, which port-publishing setup matches the lesson's recommended pattern?

**OPTIONS:**
- [ ] A: Publish both the API's and the database's ports, since more visibility makes debugging easier
- [x] B: Publish only the API's port with `-p`; leave the database unpublished, reachable only via the shared user-defined network and Docker's embedded DNS
- [ ] C: Publish neither port, and instead rely solely on `EXPOSE` in both Dockerfiles
- [ ] D: Publish only the database's port, since the API can always reach it directly without any network configuration

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's stated pattern: only the edge service needs a host-published port; internal services reach each other over the shared network without ever needing one.

**LESSON_CONNECTION:** Evidence of Understanding
**KEYWORDS:** [edge-only-publish-pattern, internal-service-reachability]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

Reference: Docker documentation — "Networking overview" and "Networking with standalone containers" (https://docs.docker.com/engine/network/)

---

## End of Phase 20

Six lessons authored (Lessons 1-6 of 17 in `elective-containerization-orchestration`). MCQ counts:
L1=8, L2=8, L3=9, L4=9, L5=8, L6=9 — **total 51 MCQs**. All lessons include at least one real,
runnable-looking Dockerfile/CLI code example (Lessons 1, 2, 4, 5, 6 each include one substantial
fenced code block in the chapter body; Lesson 3 includes two — a full Dockerfile plus a
`.dockerignore`). Module remains incomplete after this phase: lessons 7-17 (11 lessons) are out of
scope here, covered by Phases 21 and 22.
