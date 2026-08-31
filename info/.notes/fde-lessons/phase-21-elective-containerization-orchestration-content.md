# FDE Phase 21 — Elective: Containerization and Orchestration (Lessons 7-12 of 17)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-21-elective-containerization-orchestration-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `elective-containerization-orchestration` ("Containerization and
Orchestration", a `SupplementalModuleDefinition` / elective).

This is a **17-lesson elective module, not yet complete**. This file covers its **middle
section only — lessons 7-12 of 17**. A sibling phase (Phase 20, authored separately) covers
lessons 1-6 (Docker Introduction through Docker Networking Deep Dive). A later phase (Phase 22)
covers lessons 13-17 (Kubernetes Networking, Kubernetes Scaling, Kubernetes Scaling and Network
Policies, Kubernetes Security: RBAC and DevSecOps, Kubernetes Volumes) and completes the module —
do not add placeholder content for either range here.

Lessons 7-8 finish the Docker half of the module (hardening and a hardening demo). Lesson 9
("Introduction to Orchestration") is the deliberate bridge from single-host Docker to
Kubernetes. Lessons 10-12 begin the Kubernetes portion of the module at a foundational,
mechanism level — how the control plane, the Pod, and the Deployment/ReplicaSet actually work —
deliberately **not** duplicating Module 4's `cloud-devops-infrastructure` lessons ("Kubernetes
Architecture & Core Concepts" and "Kubernetes Networking, Security & GPU Workloads"), which
already cover the API-server/etcd/controller reconciliation story and production
operations (RBAC, network policy, GPU scheduling, EKS). Where this phase's lessons touch the same
ground (the API server as the single writer to `etcd`, the reconciliation loop), they name it in
one sentence and move directly into terrain Module 4 does not cover: hands-on `kubectl` mechanics,
full YAML manifest anatomy, Pod internals (pause container, shared network namespace, probes, QoS
classes), and the ReplicaSet/Deployment/rolling-update state machine with real revision history.

All six lessons continue one running example: **Northwind Fulfillment**, a mid-market logistics
customer whose FDE engagement is containerizing and then orchestrating **routeplanner**, a Python
FastAPI service that computes delivery routes, backed by a Redis queue and a Postgres database.
Lessons 1-6 (Phase 20) most plausibly built and networked the `routeplanner` image and its Redis/
Postgres sidecort containers under plain Docker and Docker Compose — this phase picks the same
service up, hardens its image, and then moves it onto Kubernetes.

---

# LESSON 7

```yaml
lesson_id: fde-elective-containerization-orchestration-07-hardening-the-docker-environment-devsecops
lesson_title: "Hardening the Docker Environment (DevSecOps)"
lesson_order: 7

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Medium-Hard
estimated_minutes: 60
content_status: Draft

learning_outcomes:
  - "Rebuild a container image to run as a non-root user with a read-only root filesystem and dropped Linux capabilities, and state what each change actually removes from an attacker's reach."
  - "Generate and read a software bill of materials (SBOM) and a vulnerability scan report, and distinguish a finding that blocks a release from one that is an accepted, documented exception."
  - "Explain image provenance and signed promotion well enough to say why a customer's admission policy should trust a digest, not a mutable tag."

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
# Hardening the Docker Environment (DevSecOps)

## Concepts Covered

A container's attack surface is everything present inside it that an attacker who gets code
execution could use, and the naive Dockerfile maximizes that surface by default: it runs as root
because no `USER` line ever changes that, it ships a full Debian or Ubuntu base with a shell, a
package manager, and every build tool still installed, and its filesystem is writable everywhere
because nothing ever says otherwise. None of this is malicious — it is simply what you get when a
Dockerfile is written to make the build succeed and nothing else. Hardening is the deliberate
process of removing everything that isn't required for the container's one job, because every
tool left inside is a tool an attacker inherits for free the moment they get a foothold: a shell
lets them explore, a package manager lets them install more tools, root lets them read any file
in the container and, if the runtime is misconfigured, sometimes reach the host. `docker run
--user 1000:1000` forces a container to run as a named non-root UID even if the image itself
never set one, but this is a weaker, ops-time fix — the correct place to fix it is in the
Dockerfile with a dedicated `USER` line, so the constraint travels with the image and cannot be
silently dropped by whoever runs it next. `--cap-drop=ALL --cap-add=NET_BIND_SERVICE` (only if
the process genuinely needs to bind a privileged port) narrows the kernel capabilities the
container process holds from the roughly 40 Linux grants a root process gets by default down to
exactly the ones named — `CAP_SYS_ADMIN`, `CAP_NET_RAW`, and the rest stay denied even if the
process is somehow compromised. `--read-only` with an explicit `--tmpfs /tmp` for the one
directory that genuinely needs to be writable means a compromised process cannot write a
persistent backdoor into the image's own filesystem, only into memory-backed scratch space that
disappears when the container exits.

The second half of hardening is supply-chain integrity, not just runtime restriction: an SBOM
(software bill of materials) is a structured, machine-readable inventory of every package and
library baked into an image — every OS package, every Python or Node dependency, down to a
specific version — generated by a tool like `syft` and typically emitted as a CycloneDX or SPDX
JSON document. It matters because a CVE announcement names a package and a version range, and
without an SBOM you cannot answer "are we affected?" for a fleet of images without re-scanning
each one from scratch; with one, it's a lookup. A vulnerability scanner (`trivy`, `grype`) reads
that inventory (or scans the image directly) against a CVE database and reports findings by
severity, but a scanner's severity rating is about the vulnerable package in the abstract, not
about whether the vulnerability is actually reachable in this image's specific runtime
configuration — a CRITICAL finding in a library your application never calls, running as
non-root with the vulnerable syscall path denied by a dropped capability, may be a documented,
risk-accepted exception rather than a release blocker, and part of an FDE's job during a customer
security review is writing that exception down with its reasoning, not silently ignoring the scan
or blindly blocking every release on any CRITICAL finding regardless of exploitability.
Provenance and signed promotion close the loop: a mutable tag like `routeplanner:latest` can point
to a different image tomorrow than it does today, so a customer's admission policy that trusts
`latest` is trusting whoever last pushed to that tag, not a specific, reviewed artifact — pinning
and admitting by immutable digest (`routeplanner@sha256:3f9c...`), ideally signed with a tool like
`cosign` so the digest's origin is verifiable, is what actually lets a customer's platform team
say "this exact, reviewed build is what's running," the same guarantee image-layer immutability
gave you inside a single build, now extended across the promotion pipeline.

```dockerfile
# routeplanner/Dockerfile — hardened
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

FROM python:3.12-slim
RUN groupadd -r routeplanner && useradd -r -g routeplanner -u 10001 routeplanner \
    && apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages
COPY --chown=routeplanner:routeplanner . .
USER 10001
EXPOSE 8080
ENTRYPOINT ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Practical Backend Scenario

Northwind Fulfillment's security team runs a pre-handoff review of `routeplanner` and flags three
findings in the same report: the image's Dockerfile has no `USER` line, so the FastAPI process
runs as UID 0 inside the container; the base image is `python:3.12` (the full image, with `apt`,
`gcc`, and a shell present) rather than `python:3.12-slim`; and a `grype` scan against the image's
generated SBOM turns up a CRITICAL CVE in a transitively-pulled `cryptography` package version
that `routeplanner` itself never imports directly. The FDE rebuilds the Dockerfile with a
dedicated non-root user and a slim base, re-scans, and confirms the CVE is still present (a
transitive dependency, not something a base-image swap alone fixes) — but writes a documented
exception noting the vulnerable code path is in an unused optional feature of the `cryptography`
package, the container runs non-root with capabilities dropped, and the fix ships in the next
scheduled dependency bump, which the customer's security lead signs off on as an accepted,
time-boxed risk rather than a release blocker.

## Practice Loop

1. Add a dedicated non-root `USER` to the `routeplanner` Dockerfile and rebuild the image, then run `docker run --rm routeplanner id` to confirm the process UID is no longer 0.
2. Swap the base image from `python:3.12` to `python:3.12-slim`, rebuild, and compare `docker images` output for both tags to measure the size reduction.
3. Generate an SBOM with `syft routeplanner:hardened -o cyclonedx-json > sbom.json` and run `grype sbom:sbom.json`, counting how many findings are CRITICAL, HIGH, and MEDIUM before deciding what to act on.
4. Pick the one CRITICAL finding, determine whether `routeplanner`'s code actually reaches the vulnerable function, and write a one-paragraph accepted-risk exception if it does not.
5. Run the hardened image with `--read-only --cap-drop=ALL --tmpfs /tmp` and confirm the application still starts and serves a request, adjusting the tmpfs mount if the app needs additional scratch space.

## Evidence of Understanding

You can rebuild a Dockerfile to run as a dedicated non-root user with a read-only root filesystem
and a minimal capability set, and state precisely what each restriction removes from an
attacker's reach. You can generate an SBOM and read a vulnerability scan's severity output, and
you can distinguish a finding that must block a release from one that is a legitimate,
documented, risk-accepted exception based on reachability, not scanner severity alone. You can
explain why a customer's admission policy should trust an immutable, ideally signed digest rather
than a mutable tag.

## Suggested Extension

Add a `HEALTHCHECK` instruction to the hardened Dockerfile and wire a CI step that fails the build
if `grype`'s exit code reports any new CRITICAL finding not already present in a checked-in
exceptions file.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why a dedicated Dockerfile `USER` beats a runtime `--user` flag
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson argues that setting `USER` inside the Dockerfile is a stronger fix than running the
container with `docker run --user 1000:1000`. Why?

**OPTIONS:**
- [ ] A: `docker run --user` is not supported by most container runtimes
- [x] B: A Dockerfile `USER` line travels with the image itself, so the non-root constraint holds no matter who runs the container later; a runtime flag can be silently omitted by whoever runs it next
- [ ] C: `--user` only works for images built from Alpine, not Debian-based images
- [ ] D: Setting `USER` in the Dockerfile is required before a `HEALTHCHECK` instruction will work

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific point is about durability of the constraint — baking it into the image
means it can't be dropped at run time the way a flag can be forgotten.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [non-root, dockerfile-user, durability]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What `--cap-drop=ALL --cap-add=NET_BIND_SERVICE` actually does
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the effect of running a container with `--cap-drop=ALL --cap-add=NET_BIND_SERVICE`?

**OPTIONS:**
- [ ] A: It disables networking entirely except for binding a single named port
- [x] B: It removes all default Linux kernel capabilities (roughly 40 for a root process) except the one explicitly re-added, narrowing what a compromised process inside the container could do even with root privileges
- [ ] C: It makes the container filesystem read-only
- [ ] D: It forces the container to run as a non-root user

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Capabilities are a distinct control from filesystem writability or UID — the lesson is explicit
that this flag narrows the kernel-level grants held by the process, not the filesystem or the
user identity.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [capabilities, cap-drop, kernel-grants]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the hardened Dockerfile
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the lesson's hardened `routeplanner` Dockerfile, what is the purpose of the multi-stage
`builder` stage?

**CODE_BLOCK:**
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

FROM python:3.12-slim
...
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages
```

**OPTIONS:**
- [x] A: It resolves dependencies in an isolated stage so build-time tooling and caches never make it into the final image, keeping the shipped image smaller and its attack surface narrower
- [ ] B: It runs the application's test suite before the final image is built
- [ ] C: It is required so the final image can run as a non-root user
- [ ] D: It generates the image's SBOM automatically as part of the build

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Multi-stage builds separate dependency resolution from the runtime image; only the resolved
`deps` directory is copied forward, not `pip`'s cache or any build tooling.

**LESSON_CONNECTION:** Chapter Body, Dockerfile example
**KEYWORDS:** [multi-stage-build, attack-surface]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What an SBOM actually is
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does an SBOM (software bill of materials) contain?

**OPTIONS:**
- [ ] A: A list of every CVE currently affecting the image, ranked by severity
- [x] B: A structured, machine-readable inventory of every package and library baked into the image, down to specific versions
- [ ] C: A signed cryptographic hash proving who built the image
- [ ] D: A record of every container that has ever run from this image in production

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson defines the SBOM as an inventory (what's inside), distinct from the scan report (what's
vulnerable) that a tool like `grype` produces by checking the inventory against a CVE database.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [sbom, syft, inventory]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the CRITICAL finding was not an automatic release blocker
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did the FDE write a documented exception for the CRITICAL
CVE in `cryptography` instead of blocking the release?

**OPTIONS:**
- [ ] A: CRITICAL findings never need to be addressed if the base image was recently updated
- [ ] B: The customer's security lead does not have authority to approve release exceptions
- [x] C: `routeplanner`'s code never reaches the vulnerable function, and the container already runs non-root with capabilities dropped — the finding's severity rating describes the package in the abstract, not whether it is reachable in this specific runtime configuration
- [ ] D: `grype` reported the finding as a false positive, so no further action was required

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The lesson's central point about scanning is that severity and reachability are separate
questions — a documented, reasoned exception is legitimate when the vulnerable path is genuinely
unreachable, not a shortcut around every CRITICAL finding.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [reachability, accepted-risk, scan-severity]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why a mutable tag is a weaker admission control than a digest
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue a customer's admission policy should trust an image digest rather than a
tag like `routeplanner:latest`?

**OPTIONS:**
- [ ] A: Digests are required by the Docker CLI and tags are being deprecated
- [x] B: A tag is mutable and can point to a different image tomorrow than it does today, so trusting it means trusting whoever last pushed to that tag rather than a specific, reviewed artifact
- [ ] C: Tags cannot be pulled from a private registry
- [ ] D: A digest is shorter and therefore faster to type in a deployment manifest

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Immutability is the property that matters — a digest always resolves to the exact same content,
while a tag is just a movable pointer.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [provenance, digest, mutable-tag]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Read-only root filesystem with a tmpfs exception
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson pair `--read-only` with an explicit `--tmpfs /tmp` mount rather than leaving
the container fully read-only?

**OPTIONS:**
- [ ] A: `--read-only` alone would prevent the container from starting at all
- [x] B: Some processes need scratch space to function; `--tmpfs` grants writability only to a memory-backed, ephemeral directory, so a compromised process still cannot persist a backdoor into the image's own filesystem
- [ ] C: `--tmpfs` is required for the container to bind any network port
- [ ] D: `--read-only` only applies to the image layers, not the container's writable layer, so `--tmpfs` is redundant

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scoped tmpfs exception preserves the functional need for scratch space while denying
persistence — anything written there disappears when the container exits.

**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [read-only-root, tmpfs, ephemeral-scratch]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** The role of a vulnerability scanner versus an SBOM tool
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson distinguish the job of `syft` from the job of `grype` in the hardening
workflow?

**OPTIONS:**
- [ ] A: `syft` scans for vulnerabilities and `grype` generates the SBOM
- [x] B: `syft` generates the structured package inventory (the SBOM); `grype` checks that inventory (or the image directly) against a CVE database and reports findings by severity
- [ ] C: They perform the same function and are used interchangeably
- [ ] D: `syft` only works on Alpine-based images, and `grype` only works on Debian-based images

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson names the two-tool pipeline explicitly: inventory generation, then vulnerability
lookup against that inventory.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [syft, grype, tool-pipeline]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why root inside a container still matters
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson states that root inside a container "lets them read any file in the container and, if
the runtime is misconfigured, sometimes reach the host." What does this imply about container
isolation as a security boundary?

**OPTIONS:**
- [ ] A: Container isolation makes the in-container user identity irrelevant to security
- [x] B: Container isolation is not an absolute guarantee; a misconfigured runtime can allow a root process inside a container to affect the host, so non-root is a defense-in-depth measure, not a redundant one
- [ ] C: Root inside a container is always equivalent to root on the host, regardless of runtime configuration
- [ ] D: Only Kubernetes clusters, not standalone Docker, are exposed to this risk

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's phrasing is deliberately conditional ("if the runtime is misconfigured, sometimes
reach the host") — non-root is one layer of defense among several, not a claim that isolation is
worthless without it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [defense-in-depth, container-isolation, root-risk]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 8

```yaml
lesson_id: fde-elective-containerization-orchestration-08-industry-standard-container-hardening-demo
lesson_title: "Industry-Standard Container Hardening Demo"
lesson_order: 8

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Medium-Hard
estimated_minutes: 60
content_status: Draft

learning_outcomes:
  - "Run a before-and-after image comparison through an automated CI security gate and interpret the pass/fail decision."
  - "Distinguish a genuine false positive from an under-investigated finding when reviewing a scanner result."
  - "Produce a short, auditable release decision document a teammate could reproduce without access to the original FDE."

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
# Industry-Standard Container Hardening Demo

## Concepts Covered

A hardening review that lives only in one engineer's head is not a repeatable process — the
customer's platform team needs a demo they can rerun themselves, with the same tools, against the
next release, and get a comparable answer without needing the original FDE in the room. That
requirement shapes what "industry-standard" means here: not a one-off manual audit, but a small,
automated pipeline stage that runs the same checks on every build and produces the same kind of
evidence every time. A CI security gate is the mechanism: a pipeline step that builds the image,
runs a scanner against it, and fails the build if the result crosses a defined policy threshold —
for example, "block on any CRITICAL finding with a known fix available; warn but allow on HIGH;
ignore LOW and MEDIUM unless explicitly flagged." The threshold itself is a policy decision a
customer's security team owns, not something a scanner decides on its own, and writing it down
explicitly (rather than leaving "block or allow" as an ad hoc judgment call each time) is what
makes the gate auditable — anyone can read the policy and predict the outcome for a given scan
result before the pipeline even runs.

The harder skill in this lesson is reviewing a specific finding rather than trusting the gate's
verdict blindly in either direction. A scanner reports a finding as a "false positive" only when
it is provably wrong — the CVE database entry doesn't actually apply to how this package is
compiled or configured in this image, a case a tool like `grype` sometimes gets wrong for
distro-patched packages that backport a fix without bumping the version string the scanner keys
on. That is different from a finding that is real but not exploitable in this deployment, which is
a risk-acceptance decision, not a false-positive determination — conflating the two is the single
most common mistake an FDE makes under time pressure, because both outcomes end with "the build is
allowed to proceed," and it's tempting to label anything inconvenient a false positive without
actually checking the distro's patch metadata. A release decision document exists precisely to
force that distinction onto paper: it names the specific finding, states which category it falls
into (false positive with evidence, or accepted risk with a reachability argument and an owner),
and links the exact scan output and policy version used, so a teammate reviewing it six months
later can reconstruct the reasoning without re-running the investigation from scratch.

```yaml
# .github/workflows/image-scan.yml — CI security gate
name: container-security-gate
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t routeplanner:${{ github.sha }} .
      - name: Generate SBOM
        run: syft routeplanner:${{ github.sha }} -o cyclonedx-json=sbom.json
      - name: Scan and gate
        run: |
          grype sbom:sbom.json --fail-on critical --output table
```

## Practical Backend Scenario

Northwind's platform team asks for a short demo before signing off on `routeplanner`'s release
process: build the image before and after last week's hardening changes, run both through the CI
gate, and show one real finding reviewed end to end. The FDE runs the pre-hardening image through
the pipeline — it fails, blocked on a CRITICAL finding for a root-owned `setuid` binary left over
from the full `python:3.12` base image. The hardened image passes the CRITICAL gate but produces a
HIGH warning for an OpenSSL version string the scanner flags; checking the base image's changelog
shows Debian backported the actual fix without bumping the version Trivy keys on, so the FDE marks
it a genuine false positive with the changelog link as evidence, re-runs the scan to confirm the
suppression is scoped to that one CVE ID only, and publishes a one-page release decision the
platform team can read without asking a follow-up question.

## Practice Loop

1. Write a CI-style pipeline step (as a shell script or a GitHub Actions job) that builds
   `routeplanner`, generates its SBOM, and gates the build on any CRITICAL finding.
2. Run the pipeline against the pre-hardening and post-hardening image tags and record the two
   pass/fail outcomes side by side.
3. For the one HIGH finding that survives hardening, check the base image's distro changelog or
   advisory page to determine whether the fix was actually backported — count how many minutes
   this verification step takes versus simply suppressing the finding.
4. Classify the finding as either a genuine false positive (with the changelog link as evidence)
   or an accepted risk (with a reachability argument and an owner), never both.
5. Publish a one-page release decision naming the finding, its classification, the evidence, and
   the policy threshold applied, written so a teammate could reproduce the same verdict without
   asking you a question.

## Evidence of Understanding

You can wire an automated CI stage that builds an image, generates its SBOM, scans it, and fails
the build against an explicit, written policy threshold. You can distinguish a genuine false
positive (provably wrong scanner output, backed by distro changelog evidence) from an accepted
risk (a real but unreachable finding), and you never label a finding a false positive without that
evidence. You can write a short release decision document that a teammate can audit and reproduce
without access to you or the original investigation.

## Suggested Extension

Add a second gate tier that fails the build on any finding without either a documented false-positive
suppression or a linked accepted-risk entry, so an unreviewed HIGH or CRITICAL finding can never
silently pass through the pipeline by omission.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What makes a security gate auditable
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what specifically makes a CI security gate auditable rather than an
ad hoc judgment call?

**OPTIONS:**
- [ ] A: It runs automatically on every pull request without human review
- [x] B: The block/allow policy threshold is written down explicitly, so anyone can read it and predict the outcome for a given scan result before the pipeline runs
- [ ] C: It uses `grype` specifically rather than any other scanning tool
- [ ] D: It generates an SBOM in CycloneDX format rather than SPDX

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Auditability comes from the explicit, written policy threshold — a predictable rule anyone can
apply, not from automation or tool choice alone.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [ci-gate, policy-threshold, auditability]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** False positive versus accepted risk
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson calls conflating a "false positive" with an "accepted risk" the most common mistake an
FDE makes under time pressure. What is the actual distinction between the two?

**OPTIONS:**
- [x] A: A false positive means the scanner's finding is provably wrong for this specific image (with evidence, like a distro changelog); an accepted risk means the finding is real but judged unreachable or acceptable, which requires a reachability argument and a named owner
- [ ] B: A false positive is always a HIGH-severity finding, while an accepted risk is always CRITICAL
- [ ] C: An accepted risk requires no documentation, while a false positive must be reported to the vendor
- [ ] D: There is no meaningful distinction; both terms describe the same outcome

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is explicit that both outcomes result in "the build is allowed to proceed," which is
exactly why it's tempting to conflate them — but they require different evidence and different
documentation.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [false-positive, accepted-risk, evidence-requirement]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the CI gate workflow
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the lesson's CI workflow, what happens if `grype sbom:sbom.json --fail-on critical` finds a
HIGH-severity vulnerability but no CRITICAL ones?

**CODE_BLOCK:**
```yaml
      - name: Scan and gate
        run: |
          grype sbom:sbom.json --fail-on critical --output table
```

**OPTIONS:**
- [ ] A: The pipeline step fails, because any non-LOW finding blocks the build
- [x] B: The pipeline step succeeds and the build proceeds, because `--fail-on critical` only fails the step on findings at or above CRITICAL severity
- [ ] C: The build is paused and a human must manually approve it before continuing
- [ ] D: `grype` automatically escalates the HIGH finding to CRITICAL if it is left unaddressed for more than 24 hours

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
`--fail-on critical` sets the exit-code threshold explicitly at CRITICAL; anything below that
severity does not fail the step, matching the lesson's example policy (block CRITICAL, warn on
HIGH).

**LESSON_CONNECTION:** Chapter Body, CI workflow example
**KEYWORDS:** [grype, fail-on, ci-workflow]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the pre-hardening image failed the gate
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did the pre-hardening `routeplanner` image fail the CI
security gate?

**OPTIONS:**
- [ ] A: The image had no SBOM generated at all
- [x] B: It carried a CRITICAL finding for a root-owned `setuid` binary left over from the full `python:3.12` base image
- [ ] C: The Dockerfile failed to build due to a missing dependency
- [ ] D: The image exceeded a maximum size limit enforced by the pipeline

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scenario names the specific finding — a CRITICAL result tied to the un-hardened base image —
as the cause of the block, not a build failure or a missing SBOM.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [pre-hardening-scan, ci-block, setuid-binary]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** How the OpenSSL finding was actually resolved
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why was the OpenSSL HIGH finding on the hardened image classified as a false positive rather than
an accepted risk?

**OPTIONS:**
- [ ] A: HIGH-severity findings are always classified as false positives by convention
- [ ] B: The FDE decided it was low-risk without checking any further evidence
- [x] C: The Debian base image's changelog showed the actual fix had been backported without bumping the version string the scanner keys on, meaning the scanner's finding was provably wrong for this specific image
- [ ] D: The finding disappeared automatically after the SBOM was regenerated

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The scenario's specific evidence — a backported fix the scanner's version check doesn't detect —
is exactly the kind of provable-wrongness the lesson requires before calling something a false
positive.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [backported-fix, false-positive-evidence, changelog]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What a release decision document must contain
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson say a release decision document must name for it to be genuinely reproducible
by a teammate?

**OPTIONS:**
- [ ] A: Only the final pass/fail outcome
- [x] B: The specific finding, its classification (false positive or accepted risk) with supporting evidence, and the exact scan output and policy version used
- [ ] C: A summary of every CVE ever found in the project's history
- [ ] D: The name of the engineer who approved the release, with no further detail

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is explicit about the components needed for reconstruction: the finding, its
classification with evidence, and the exact artifacts (scan output, policy version) used to reach
the verdict.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [release-decision, auditability, reproducibility]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the demo builds both a pre- and post-hardening image
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the demo run both the pre-hardening and post-hardening images through the same CI gate
rather than only showing the final, passing image?

**OPTIONS:**
- [x] A: It gives the platform team concrete before-and-after evidence that the gate actually functions as a control — catching a real problem in one case and passing a genuinely improved image in the other
- [ ] B: Running two builds is required by the `grype` tool itself
- [ ] C: The pre-hardening image is needed to generate the SBOM for the post-hardening image
- [ ] D: It doubles the number of CVEs the scanner is able to detect

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
A gate that always passes proves nothing; the scenario's point is demonstrating the gate actually
discriminates between a vulnerable and a hardened build.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [before-after-demo, gate-verification]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Who owns the policy threshold
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, who decides the block/allow policy threshold used by the CI security
gate?

**OPTIONS:**
- [ ] A: The scanning tool itself, based on its default configuration
- [ ] B: Whichever engineer runs the pipeline that day
- [x] C: The customer's security team, as an explicit, written policy decision — not something a scanner decides on its own
- [ ] D: It is fixed permanently at build time and cannot be changed later

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The lesson is explicit that the threshold is a customer-owned policy decision, distinct from
whatever a scanner reports by default.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [policy-ownership, security-team, threshold]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Suppressing findings scoped correctly
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
After classifying the OpenSSL finding as a false positive, the FDE re-runs the scan to confirm the
suppression is "scoped to that one CVE ID only." Why does this step matter?

**OPTIONS:**
- [ ] A: It is required to regenerate the SBOM after every scan
- [x] B: A suppression rule written too broadly could silently hide a genuinely new, unrelated finding introduced in a later build, defeating the purpose of the gate
- [ ] C: It confirms the CI pipeline has network access to the vulnerability database
- [ ] D: It is only necessary when the finding severity is CRITICAL, not HIGH

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
A suppression scoped only to the specific CVE ID preserves the gate's ability to catch any new,
different finding — a loosely-scoped suppression rule is a common way security gates quietly stop
working.

**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [suppression-scoping, gate-integrity]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 9

```yaml
lesson_id: fde-elective-containerization-orchestration-09-introduction-to-orchestration
lesson_title: "Introduction to Orchestration"
lesson_order: 9

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Medium-Hard
estimated_minutes: 55
content_status: Draft

learning_outcomes:
  - "List the manual operations a Docker Compose deployment requires from a human and map each to the orchestration capability that replaces it."
  - "Explain desired-state reconciliation as a continuous control loop, distinct from a one-time imperative command."
  - "Justify a decision to adopt orchestration from an operational need (host replacement, uneven traffic, service discovery) rather than technology preference."

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
# Introduction to Orchestration

## Concepts Covered

A `docker run` command or a `docker-compose.yml` file describes containers imperatively: you tell
the Docker daemon to start these specific containers, with these specific settings, right now. That
model works cleanly for a single host running a small, static set of services, but it has no
opinion about what should happen next — if a container's process crashes, if the host it's running
on disappears, or if traffic to one service triples while another sits idle, nothing in plain
Docker notices or reacts. An operator has to notice the container is down, run `docker run` again,
figure out which host has capacity, update whatever DNS entry or load-balancer config pointed at
the old instance, and repeat that manually every time it happens again. Orchestration is the
answer to exactly this gap: instead of issuing one-time imperative commands, you declare desired
state — "run 3 replicas of `routeplanner`, each needing 256Mi of memory, exposed as one stable
service address" — to a system that continuously reconciles that declaration against what is
actually running, and keeps doing so indefinitely, not just at the moment you submitted it.
Reconciliation is a control loop: observe actual state, compare it against desired state, take the
smallest action that closes the gap, and repeat, forever, without a human re-triggering it. This is
the single conceptual shift that makes everything downstream in Kubernetes make sense — a
`Deployment` object is not a one-time instruction, it is a standing promise the system keeps
enforcing.

That reconciliation loop only becomes valuable once several problems appear together, and it's
worth being precise about which ones, because reaching for an orchestrator before any of them
exist is adding real operational complexity (a control plane, new failure modes, a steeper learning
curve for the team taking over the system after handoff) against no evidenced need — the same
seam-versus-generality judgment call an FDE makes about any architecture decision. The problems
that justify it: scheduling (deciding which of several hosts has capacity for a new container,
instead of a human picking one by hand), service discovery (giving a set of interchangeable
replicas one stable address that survives any individual replica being replaced, instead of
hardcoding a container's current IP somewhere), rolling deployment (replacing running instances
with a new version gradually, watching health as you go, instead of stopping everything and hoping
the new version starts cleanly), and self-healing (replacing a crashed or unresponsive container
automatically, instead of waiting for a human to notice an alert). A customer running one
`routeplanner` container and one Redis container on a single EC2 instance, with no autoscaling
requirement and acceptable downtime during a deploy, genuinely does not need an orchestrator yet —
Docker Compose is the right, boring tool for that shape of problem. The same customer, once they
have a worker fleet that must survive a host being replaced, traffic that swings 5x between
business hours and overnight, and multiple services that need to find each other without hardcoded
IPs, has crossed into orchestration territory, and the decision should be traceable to those
specific operational facts, not to Kubernetes being the more sophisticated-sounding technology.

```bash
# What "manual orchestration" looks like without a scheduler —
# an operator re-running this by hand every time a host disappears
$ ssh worker-03 'docker run -d --name routeplanner-3 \
    -e REDIS_HOST=redis.internal \
    -e DB_HOST=postgres.internal \
    routeplanner@sha256:3f9c...'
$ curl -sf http://worker-03:8080/health || echo "still not healthy, retry"
# ...and then update the load balancer's target group by hand
```

## Practical Backend Scenario

Northwind Fulfillment's `routeplanner` deployment currently runs as three `docker run` containers
on two EC2 hosts, started by a deploy script an engineer runs by hand, with a manually-maintained
load-balancer target group pointing at their fixed IPs. During a regional AWS maintenance window,
one host is terminated and replaced; nothing restarts `routeplanner`'s container on the new host
automatically, the load balancer keeps sending a third of traffic to a dead target for eleven
minutes until an on-call engineer notices the alert, SSHes into the new host, and re-runs the
deploy script by hand. The FDE lists every manual step that incident required — noticing the host
was gone, picking a new host with capacity, starting the container with the right environment
variables, updating the load-balancer target — and maps each one to a Kubernetes capability
(self-healing, the scheduler, a `Deployment`, a `Service`) that would have closed the same gap
without a human in the loop, and uses that mapping, not a general preference for Kubernetes, to
justify moving `routeplanner` onto it.

## Practice Loop

1. List every manual operation the current `routeplanner` deploy script and on-call runbook
   require a human to perform (starting a container, choosing a host, updating the load balancer,
   restarting after a crash).
2. For each manual operation from step 1, name the orchestration capability that would replace it
   (scheduling, self-healing, service discovery, rolling deployment) and which specific
   Kubernetes object provides it.
3. Time or count how many minutes the eleven-minute incident actually cost in degraded traffic,
   and compare it against how quickly a reconciliation loop checking every few seconds would have
   noticed and replaced the missing container.
4. Identify which of the current three services (`routeplanner`, Redis, Postgres) genuinely needs
   orchestration's scheduling and self-healing first, and which could reasonably stay as a
   simpler, managed component (a managed Redis or RDS instance) instead of being containerized
   and orchestrated at all.
5. Write a one-paragraph justification for adopting Kubernetes that cites only the specific
   operational facts from this incident and the traffic-variance requirement — not a general
   claim that Kubernetes is more modern or more scalable in the abstract.

## Evidence of Understanding

You can list the manual operations a plain-Docker deployment requires from a human and map each
one to the specific orchestration capability that replaces it. You can explain desired-state
reconciliation as a continuous control loop — observe, compare, act, repeat — distinct from a
one-time imperative command, and state why that shift is what makes self-healing and rolling
deployment possible. You can justify a decision to adopt orchestration by citing a specific,
evidenced operational need rather than a general technology preference.

## Suggested Extension

Write the equivalent one-paragraph justification for the opposite decision — a customer scenario
where adopting Kubernetes would be premature complexity — naming the specific operational facts
(single host, no traffic variance, acceptable manual restart) that would make Docker Compose the
correct call instead.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Imperative commands versus declared desired state
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the core difference the lesson draws between running `docker run` commands and declaring
desired state to an orchestrator?

**OPTIONS:**
- [x] A: `docker run` is a one-time instruction with no ongoing opinion about what should happen next; declared desired state is continuously enforced by a control loop that keeps acting until the declaration is true, indefinitely
- [ ] B: `docker run` cannot start more than one container at a time, while orchestrators can
- [ ] C: Declared desired state requires writing YAML, while `docker run` requires writing a shell script — the underlying behavior is otherwise identical
- [ ] D: Orchestrators only support declarative configuration for stateless services, never for containers with persistent state

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's central conceptual claim is about ongoing enforcement versus a one-time action, not
about syntax or container count.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [imperative-vs-declarative, desired-state, control-loop]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** The reconciliation loop's steps
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What are the four steps of the reconciliation loop as described in the lesson?

**OPTIONS:**
- [ ] A: Build, test, deploy, monitor
- [x] B: Observe actual state, compare against desired state, take the smallest action that closes the gap, repeat
- [ ] C: Schedule, provision, scale, terminate
- [ ] D: Request, authenticate, authorize, respond

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson names this exact loop as the mechanism behind reconciliation — a repeated,
never-ending cycle, not a build/deploy pipeline.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [reconciliation-loop, control-loop-steps]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** When orchestration is premature
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson argues that reaching for an orchestrator before certain problems exist is "adding real
operational complexity... against no evidenced need." What kind of customer scenario does the
lesson say genuinely does not need an orchestrator yet?

**OPTIONS:**
- [x] A: One container and one Redis instance on a single host, with no autoscaling requirement and acceptable downtime during a deploy
- [ ] B: Any customer running more than one container, regardless of scale or traffic pattern
- [ ] C: A customer whose containers are written in a compiled language rather than an interpreted one
- [ ] D: A customer who has already purchased AWS support

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson names the specific shape — single host, no autoscaling need, acceptable manual-restart
downtime — as the case where Docker Compose remains the correct, boring tool.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [premature-orchestration, seam-vs-generality]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What actually failed during the host-replacement incident
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did traffic keep routing to a dead target for eleven
minutes after the EC2 host was replaced?

**OPTIONS:**
- [ ] A: Kubernetes was already in use but misconfigured
- [x] B: Nothing in the plain-Docker setup automatically noticed the container was gone or updated the manually-maintained load-balancer target group; a human had to notice the alert and act
- [ ] C: The Redis container had crashed, not the `routeplanner` container
- [ ] D: The deploy script had a syntax error that prevented it from running at all

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scenario's point is specifically about the absence of automated detection and reconciliation —
the setup had no mechanism to notice or self-heal on its own.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [manual-recovery, no-self-healing, incident]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Justifying orchestration from operational need
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson insists a decision to adopt orchestration should be "traceable to specific operational
facts, not to Kubernetes being the more sophisticated-sounding technology." What is this argument
an application of, drawn from elsewhere in the FDE curriculum?

**OPTIONS:**
- [ ] A: The RAG evaluation discipline of measuring retrieval precision before tuning generation
- [x] B: The seam-versus-generality judgment call — adopting real complexity only against an evidenced need, not a speculative or preference-driven one
- [ ] C: The discovery call's four-pass structure for uncovering stakeholder pain points
- [ ] D: The incident postmortem's blameless-language convention

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson explicitly names this as the same judgment call used for any architecture decision:
complexity should be adopted against an evidenced need, not preference.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [operational-need, seam-vs-generality, justification]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Service discovery as an orchestration capability
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson define the service discovery problem that orchestration solves?

**OPTIONS:**
- [ ] A: Discovering which container image version is currently deployed
- [x] B: Giving a set of interchangeable replicas one stable address that survives any individual replica being replaced, instead of hardcoding a container's current IP somewhere
- [ ] C: Finding which host in a cluster has the most available memory
- [ ] D: Automatically generating API documentation for a running service

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's definition centers on address stability across replica churn, not documentation or
resource discovery.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [service-discovery, stable-address]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What a `Deployment` object represents
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson states that "a `Deployment` object is not a one-time instruction, it is a standing
promise the system keeps enforcing." What does this mean in practice?

**OPTIONS:**
- [ ] A: A `Deployment` can only be created once per cluster and cannot be updated afterward
- [x] B: After a `Deployment` is submitted, the system continuously works to keep the actual running state matching it, reacting to drift (a crashed pod, a lost node) without needing the command to be re-issued
- [ ] C: A `Deployment` guarantees zero downtime for every rollout regardless of configuration
- [ ] D: `Deployment` objects are stored only in memory and are lost on any control-plane restart

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the reconciliation concept applied specifically to the `Deployment` object — the promise
is enforced continuously, not fulfilled once.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [deployment-object, standing-promise]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Which service should move to orchestration first
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the Practice Loop's step 4, why might Redis or Postgres reasonably stay as simpler, managed
components rather than being containerized and orchestrated alongside `routeplanner`?

**OPTIONS:**
- [ ] A: Kubernetes cannot run stateful workloads under any circumstances
- [x] B: If a managed equivalent (a managed Redis or RDS instance) already provides the durability, backup, and failover guarantees the orchestrator would otherwise need to be configured to provide, containerizing and orchestrating them adds operational complexity without a matching evidenced benefit
- [ ] C: Redis and Postgres are not available as container images
- [ ] D: Only stateless services are permitted to run inside a `Deployment`

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This continues the lesson's operational-need framing: orchestrate what needs orchestration's
specific guarantees, and let a managed service absorb operational concerns it already handles well.

**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [managed-services, selective-orchestration]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 10

```yaml
lesson_id: fde-elective-containerization-orchestration-10-kubernetes-architecture
lesson_title: "Kubernetes Architecture"
lesson_order: 10

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Trace a `kubectl apply` request through the API server, scheduler, and kubelet to a running container, naming which component owns each step."
  - "Read `kubectl get events` and `kubectl describe` output to diagnose why a workload was accepted but never became ready."
  - "Distinguish node-level responsibility (kubelet, container runtime) from control-plane responsibility (API server, scheduler, controllers) when debugging a stuck deployment."

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
# Kubernetes Architecture

## Concepts Covered

Every Kubernetes cluster splits into a control plane (the API server, `etcd`, the scheduler, and a
set of controllers) and worker nodes (each running a `kubelet` and a container runtime), and the
one fact worth memorizing before debugging anything is that the API server is the single component
that ever writes to `etcd`; every other piece of the system — the scheduler, every controller, the
`kubelet` on every node — talks to cluster state exclusively through the API server's REST
interface, never touching `etcd` directly. This lesson does not re-derive that reconciliation model
in depth; it focuses on the mechanics of what actually happens, command by command, when you submit
one manifest. Run `kubectl apply -f deployment.yaml` and the `kubectl` client serializes your YAML
to JSON and sends an HTTP request to the API server, which authenticates you, authorizes the
request, validates the object against its schema, and — if it passes — writes the object to `etcd`
and returns success. At that exact point, nothing has been scheduled and no container is running;
the API server has only durably recorded what you asked for. The Deployment controller, running as
a separate control-loop process watching the API server for `Deployment` objects, notices the new
object, and creates a `ReplicaSet` object (also just written to the API server, also not yet
running anything). The ReplicaSet controller then notices the ReplicaSet is short of its desired
replica count and creates the requested number of `Pod` objects — still just API objects, still
unscheduled, each with no `nodeName` set.

The scheduler is a distinct control loop that watches specifically for Pods with no assigned node,
evaluates a fit — does any node have enough allocatable CPU and memory (`resources.requests` on the
Pod's containers), does the Pod's node affinity or taint tolerations allow it there, are the
volumes it needs available in that node's zone — and, for the best-fitting node, writes the node
assignment back to the API server as a Pod update, again never touching the node itself directly.
Only now does the target node's `kubelet` — an agent running on every worker node, watching the API
server for Pods assigned to its own node specifically — see the new assignment, and it is the
kubelet, not the scheduler or the API server, that actually talks to the container runtime (via the
Container Runtime Interface, `containerd` in most modern clusters) to pull the image and start the
container. The kubelet then reports the Pod's status — running, ready, failed — back to the API
server, which is how `kubectl get pods` shows you live state: it is not asking every node directly,
it is reading what each node's kubelet last reported into `etcd` via the API server. A Pod stuck
`Pending` almost always means the scheduler could not find a fit (check `kubectl describe pod` for
a `FailedScheduling` event naming the specific constraint); a Pod `Running` but never `Ready` almost
always means the kubelet started the container but a readiness probe is failing, which is a node
and application-level problem, not a control-plane one — knowing which of these two failure
domains you're in before you start debugging saves you from looking at the wrong logs.

```bash
$ kubectl apply -f routeplanner-deployment.yaml
deployment.apps/routeplanner created

$ kubectl get pods -l app=routeplanner
NAME                            READY   STATUS    RESTARTS   AGE
routeplanner-7d9f8b6c4d-2xk9p   0/1     Pending   0          8s

$ kubectl describe pod routeplanner-7d9f8b6c4d-2xk9p
...
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  8s    default-scheduler   0/3 nodes are available:
                                                         3 Insufficient memory.

$ kubectl get nodes -o custom-columns=NAME:.metadata.name,ALLOC-MEM:.status.allocatable.memory
NAME       ALLOC-MEM
node-a     1948Mi
node-b     1948Mi
node-c     1948Mi
```

## Practical Backend Scenario

An FDE deploys `routeplanner` to Northwind's new cluster, and `kubectl get pods` shows the Pod
sitting in `Pending` for several minutes, never transitioning to `Running`. The FDE runs `kubectl
describe pod` and reads a `FailedScheduling` event stating `0/3 nodes are available: 3 Insufficient
memory` — the manifest's `resources.requests.memory` was set to `2Gi` per replica, copied from a
larger customer's production values without adjusting for this cluster's three small `t3.medium`
nodes, each with only about 1948Mi of allocatable memory after system reservations. The Deployment
was accepted by the API server without complaint — the manifest is syntactically and semantically
valid Kubernetes YAML — and a `ReplicaSet` and `Pod` object were created successfully; the failure
is entirely in the scheduler's fit evaluation, a distinct step the API server's acceptance says
nothing about. The FDE lowers the memory request to `512Mi`, matching what the FastAPI process
actually uses under Northwind's traffic, reapplies, and watches the same Pod transition from
`Pending` to `ContainerCreating` to `Running` within seconds, confirming the diagnosis by watching
which specific state transition finally unblocked.

## Practice Loop

1. Draw the full request path for `kubectl apply -f deployment.yaml`, labeling each arrow with the
   specific component that owns that step (API server validation, `etcd` write, Deployment
   controller, ReplicaSet controller, scheduler, kubelet, container runtime).
2. Deploy `routeplanner` with a memory request deliberately set higher than any node's allocatable
   capacity, and confirm the Pod enters `Pending`.
3. Run `kubectl describe pod` and count how many nodes the `FailedScheduling` event says were
   unavailable and for what specific reason — this is the diagnostic step that turns "it's stuck"
   into a specific, actionable cause.
4. Correct the memory request to a realistic value, reapply, and use `kubectl get pods -w` to
   watch the exact sequence of status transitions from `Pending` through to `Running`.
5. Explain, in one sentence per component, which of the API server, scheduler, or kubelet would
   be responsible if the same Pod instead got stuck in `Running` but never reached `Ready`.

## Evidence of Understanding

You can trace a `kubectl apply` request through the API server, `etcd`, the Deployment and
ReplicaSet controllers, the scheduler, and the kubelet to a running container, naming which
component owns each specific step. You can read `kubectl describe pod` events to diagnose a
scheduling failure and distinguish it from a node-level readiness failure. You can explain why the
API server accepting a manifest says nothing about whether the workload will actually be
schedulable or ready, because acceptance, scheduling, and readiness are three genuinely separate
checkpoints owned by three different components.

## Suggested Extension

Add a node with more allocatable memory to the same cluster (or simulate it by lowering another
Pod's request to free capacity) and use `kubectl get events --sort-by=.lastTimestamp` to watch the
scheduler retry and succeed against the new capacity without you resubmitting the manifest.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What happens the instant `kubectl apply` returns success
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The moment `kubectl apply -f deployment.yaml` returns "deployment.apps/routeplanner created," what
has actually happened, per the lesson?

**OPTIONS:**
- [x] A: The API server has validated and durably written the Deployment object to `etcd`; nothing has been scheduled and no container is running yet
- [ ] B: The Pod has already been scheduled to a node and its container image is being pulled
- [ ] C: The kubelet on every node has received and is now processing the new object
- [ ] D: The scheduler has already evaluated node fit and assigned the Pod

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is explicit that API-server acceptance is only a durable write — scheduling and
container startup are later, separate steps owned by different components.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [api-server, etcd-write, request-path]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Who creates the ReplicaSet and who creates the Pods
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's request path, which component creates the `ReplicaSet` object, and which creates
the individual `Pod` objects?

**OPTIONS:**
- [x] A: The Deployment controller creates the ReplicaSet; the ReplicaSet controller creates the Pods
- [ ] B: The scheduler creates both the ReplicaSet and the Pods
- [ ] C: The API server creates both directly, without any controller involvement
- [ ] D: The kubelet on each node creates its own Pod objects once it receives a Deployment update

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson traces this as two distinct controllers acting in sequence, each watching for its own
object kind and creating the next layer down.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [deployment-controller, replicaset-controller, request-path]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What the scheduler actually does
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what does the scheduler do once it finds the best-fitting node for a Pod?

**OPTIONS:**
- [ ] A: It connects directly to that node's container runtime to start the container
- [x] B: It writes the node assignment back to the API server as a Pod update, without ever touching the node itself directly
- [ ] C: It notifies the kubelet on every node in the cluster simultaneously
- [ ] D: It creates a new ReplicaSet scoped to that specific node

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scheduler's action is an API-server write, consistent with the lesson's rule that only the
API server ever writes to `etcd` and every component interacts through it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [scheduler, node-assignment, api-server-write]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Reading a FailedScheduling event
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given this `kubectl describe pod` output, what is the specific cause of the Pod remaining
`Pending`?

**CODE_BLOCK:**
```
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  8s    default-scheduler   0/3 nodes are available:
                                                         3 Insufficient memory.
```

**OPTIONS:**
- [x] A: The scheduler evaluated all 3 nodes and found none had enough allocatable memory to satisfy the Pod's resource request
- [ ] B: The container image failed to pull from the registry
- [ ] C: A readiness probe is failing on all 3 nodes
- [ ] D: The API server rejected the Deployment manifest as invalid

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The event is emitted by `default-scheduler` specifically and names "Insufficient memory" across
all 3 nodes — a scheduling-fit failure, not an image-pull or readiness-probe issue, both of which
would show a different Reason.

**LESSON_CONNECTION:** Chapter Body, kubectl example
**KEYWORDS:** [failedscheduling, describe-pod, insufficient-memory]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the Deployment was accepted despite the scheduling failure
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did the API server accept the `routeplanner` Deployment
manifest without complaint, even though the Pod later failed to schedule?

**OPTIONS:**
- [ ] A: The API server does not validate manifests before accepting them
- [x] B: The manifest was syntactically and semantically valid Kubernetes YAML — acceptance only checks that the object is well-formed and authorized, which says nothing about whether the scheduler will later find a node with enough capacity
- [ ] C: Acceptance always guarantees the Pod will schedule successfully; this scenario is an edge case that should not normally occur
- [ ] D: The API server delegated validation entirely to the scheduler in this case

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's key distinction is that acceptance, scheduling, and readiness are three separate
checkpoints — a valid manifest can still fail to schedule for resource reasons unrelated to its
validity.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [acceptance-vs-scheduling, separate-checkpoints]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Pending versus Running-but-not-Ready
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson distinguishes a Pod stuck `Pending` from a Pod `Running` but never `Ready`. What is the
practical difference in where you should look to debug each?

**OPTIONS:**
- [x] A: `Pending` almost always points to the scheduler failing to find a fit (a control-plane concern); `Running` but not `Ready` almost always points to a failing readiness probe on the node itself (a node/application-level concern)
- [ ] B: Both failure modes are always caused by the same underlying issue — insufficient node memory
- [ ] C: `Pending` is caused by the kubelet, while `Running` but not `Ready` is caused by the scheduler
- [ ] D: There is no meaningful distinction; both should be debugged by restarting the Deployment

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the lesson's explicit closing distinction: knowing which failure domain you're in — control
plane versus node — determines where to look first.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [pending-vs-ready, failure-domain, debugging]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** How `kubectl get pods` learns live status
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
When you run `kubectl get pods` and see a live status like `Running`, where does that information
actually come from?

**OPTIONS:**
- [ ] A: `kubectl` connects directly to each node and asks the container runtime for status
- [x] B: Each node's kubelet reports the Pod's status back to the API server, which persists it to `etcd`; `kubectl get pods` reads that reported state through the API server, not by asking nodes directly
- [ ] C: The scheduler polls every node continuously and forwards status to `kubectl`
- [ ] D: Status is computed client-side by `kubectl` based on how long ago the Pod was created

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This reinforces the lesson's core architectural fact — the API server is the sole intermediary,
and `kubectl` always reads through it, never talking to nodes directly.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [kubelet-reporting, kubectl-get, api-server-read]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What the kubelet does that the scheduler does not
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the specific division of labor between the scheduler and the kubelet once a Pod has an
assigned node?

**OPTIONS:**
- [ ] A: The scheduler starts the container; the kubelet only monitors it afterward
- [x] B: The scheduler's job ends at assigning the node; the kubelet, watching for Pods assigned to its own node, is the component that actually talks to the container runtime to pull the image and start the container
- [ ] C: Both the scheduler and the kubelet independently start the container, and whichever succeeds first wins
- [ ] D: The kubelet assigns the node, and the scheduler starts the container

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is explicit that these are two distinct responsibilities — assignment (scheduler) and
execution (kubelet via the container runtime) — owned by different components.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [kubelet, scheduler, division-of-labor]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Diagnosing the fix's confirmation
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
After lowering the memory request to `512Mi` and reapplying, the FDE watches the Pod transition
from `Pending` to `ContainerCreating` to `Running`. Why does observing this specific sequence of
transitions confirm the diagnosis, rather than just checking the final `Running` state?

**OPTIONS:**
- [x] A: Watching the transition through `ContainerCreating` confirms the scheduler successfully found a node this time — if the fix hadn't addressed the actual scheduling constraint, the Pod would have stayed `Pending` and never reached `ContainerCreating` at all
- [ ] B: The final `Running` state alone is always sufficient confirmation; watching intermediate states is unnecessary
- [ ] C: `ContainerCreating` indicates the API server rejected and reprocessed the manifest
- [ ] D: The sequence of transitions has no diagnostic value beyond showing the Pod eventually started

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Seeing the specific state the previous attempt never reached (`ContainerCreating`, which only
follows successful scheduling) is what verifies the scheduling constraint, specifically, was the
problem that got fixed.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [state-transitions, diagnosis-confirmation]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 11

```yaml
lesson_id: fde-elective-containerization-orchestration-11-kubernetes-pod-deep-dive
lesson_title: "Kubernetes Pod Deep Dive"
lesson_order: 11

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Write a Pod spec with an init container and a sidecar that share a network namespace and a volume, and explain exactly what 'shared' means at the kernel level."
  - "Configure liveness and readiness probes correctly and predict the restart or traffic-removal behavior each produces on failure."
  - "Explain why a Pod is not durable application identity, and identify which state must live outside it."

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
# Kubernetes Pod Deep Dive

## Concepts Covered

A Pod is the smallest unit Kubernetes schedules and manages — never a single container — and the
mechanism behind that is worth naming precisely: every Pod is created with a hidden "pause"
container first, whose only job is to hold open a Linux network namespace and (depending on
configuration) an IPC namespace that every other container in the Pod then joins. This is why
containers in the same Pod can reach each other over `localhost` — they are, at the kernel level,
sharing one network namespace, not communicating over a virtual network the way containers on
different hosts would. It also means a Pod's IP address belongs to the Pod as a whole, not to any
individual container in it, and every container in the Pod must therefore claim distinct ports if
they both listen — there is no port isolation between containers in the same Pod the way there is
between separate Pods. Volumes declared at the Pod level follow the same sharing rule: a Pod-level
`emptyDir` volume mounted into two containers is genuinely the same underlying directory, visible
to both, which is precisely what makes a sidecar pattern possible — one container can write a file
that the other reads, with no network hop involved. An init container runs to completion before
any regular container in the Pod starts, sequentially if there are several, and is the correct
place for a setup step that must finish first (waiting for a dependency to become reachable,
running a database migration, fetching a config file) rather than baking that logic into the main
application's own startup path.

Two probes govern a Pod's health independently and produce different consequences on failure, and
confusing them is one of the most common Kubernetes misconfigurations: a liveness probe answers "is
this container still working, or should it be killed and restarted," and a failing liveness probe
causes the kubelet to kill and restart the container in place — useful for a deadlocked process that
is still technically running but will never recover on its own. A readiness probe answers "should
this Pod currently receive traffic," and a failing readiness probe does not restart anything; it
only removes the Pod from the set of endpoints a Service routes traffic to, which is the correct
response to a container that is temporarily busy (loading a large model, warming a cache) rather
than actually broken. Configuring a liveness probe with the same shallow check as readiness, or
with too short an `initialDelaySeconds`, is a common cause of a crash loop entirely of the probe's
own making: the container is killed for being "unhealthy" before it ever finished starting, gets
restarted, is killed again at the same point, and repeats — `kubectl describe pod` shows this
pattern as an escalating `RESTARTS` count with `Liveness probe failed` events, distinct from an
application crash, which is what makes this diagnosable rather than mysterious. A Pod's QoS class
— `Guaranteed` (requests equal limits on every container), `Burstable` (requests set but below
limits, or only some containers have both), or `BestEffort` (no requests or limits at all) — is
derived automatically from these values and determines eviction priority under node memory
pressure: `BestEffort` Pods are evicted first, `Guaranteed` last. Finally, a Pod is ephemeral by
design: it has no durable identity of its own, and if a Pod dies, its replacement — created by the
ReplicaSet controller — gets a new name, a new IP, and a fresh `emptyDir`. Anything that must
survive that replacement (a database, an uploaded file, a session token) must live in a
PersistentVolume or an external store, never inside the Pod's own writable layer or `emptyDir`.

```yaml
# routeplanner-pod-spec.yaml — excerpt showing init container + sidecar
apiVersion: v1
kind: Pod
metadata:
  name: routeplanner
spec:
  initContainers:
    - name: wait-for-redis
      image: busybox:1.36
      command: ['sh', '-c', 'until nc -z redis-svc 6379; do sleep 2; done']
  containers:
    - name: routeplanner
      image: routeplanner@sha256:3f9c...
      ports: [{ containerPort: 8080 }]
      resources:
        requests: { cpu: "250m", memory: "512Mi" }
        limits: { cpu: "500m", memory: "512Mi" }
      livenessProbe:
        httpGet: { path: /healthz, port: 8080 }
        initialDelaySeconds: 15
        periodSeconds: 20
      readinessProbe:
        httpGet: { path: /ready, port: 8080 }
        initialDelaySeconds: 5
        periodSeconds: 5
      volumeMounts:
        - name: request-log
          mountPath: /var/log/routeplanner
    - name: log-shipper
      image: fluent-bit:3.1
      volumeMounts:
        - name: request-log
          mountPath: /var/log/routeplanner
          readOnly: true
  volumes:
    - name: request-log
      emptyDir: {}
```

## Practical Backend Scenario

Northwind adds a `fluent-bit` log-shipping sidecar to the `routeplanner` Pod so request logs reach
their centralized logging platform without the application code knowing anything about it: both
containers mount the same `emptyDir` volume, `routeplanner` writes to it, `fluent-bit` tails and
ships it, and both processes reach each other's exposed diagnostics port over `localhost` because
they share the Pod's one network namespace. During rollout, an engineer new to the team assumes the
Pod is effectively a small, semi-permanent VM and starts writing an in-progress route-optimization
job's intermediate state to a file on the sidecar's own local disk rather than to Redis. The Pod is
evicted during a routine node drain for a cluster upgrade; its replacement Pod, created fresh by
the ReplicaSet controller, has a new name, a new IP, and an empty `emptyDir` — the in-progress job's
state is gone, and the customer notices a route optimization silently restart from scratch. The FDE
traces the loss to the false assumption of Pod durability, moves the job state to Redis (which
already exists in the architecture and survives Pod replacement), and adds a one-line comment in
the manifest explaining why `emptyDir` is unsuitable for anything the customer needs to survive a
Pod restart.

## Practice Loop

1. Write the Pod spec's `initContainers` entry that waits for Redis to become reachable before the
   main `routeplanner` container starts, and explain why this logic belongs in an init container
   rather than a retry loop inside the application's own startup code.
2. Add the `fluent-bit` sidecar and a shared `emptyDir` volume, and verify with `kubectl exec` into
   each container that both can see the same file written by the other.
3. Deliberately misconfigure the liveness probe's `initialDelaySeconds` to be shorter than the
   application's actual startup time, deploy, and count how many restarts `kubectl get pods` shows
   in the first two minutes — this makes the self-inflicted crash loop visible rather than
   theoretical.
4. Fix the `initialDelaySeconds`, redeploy, and confirm restarts stop while `kubectl describe pod`
   still shows the correct number of successful readiness checks.
5. Identify every piece of state in the current Pod spec (log files, job progress, cached data) and
   classify each as safe to lose on Pod replacement or requiring an external store, then move
   anything misclassified.

## Evidence of Understanding

You can write a Pod spec with an init container and a sidecar sharing a network namespace and a
volume, and explain precisely what "shared" means at the kernel level — one network namespace, the
same underlying directory for a shared volume. You can configure liveness and readiness probes
correctly and predict which one causes a restart versus a traffic-removal on failure, and you can
diagnose a probe-induced crash loop from its `RESTARTS` pattern in `kubectl describe pod`. You can
explain why a Pod has no durable identity of its own and correctly identify which state in a given
manifest must live outside it.

## Suggested Extension

Add a second sidecar that also needs the shared log volume read-only, and update the Pod's resource
requests so the whole Pod's QoS class remains `Burstable` rather than silently dropping to
`BestEffort` because the new container has no requests set.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What the pause container actually provides
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the hidden "pause" container do, and why does its existence explain why containers in
the same Pod can reach each other over `localhost`?

**OPTIONS:**
- [x] A: It holds open the Pod's shared Linux network namespace (and IPC namespace) that every other container in the Pod joins, so containers in the same Pod are genuinely sharing one network namespace at the kernel level, not communicating over a virtual network
- [ ] B: It is a load balancer that routes traffic between containers in the Pod
- [ ] C: It runs the application's health checks on behalf of the other containers
- [ ] D: It is a legacy component with no function in modern Kubernetes versions

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson names the pause container's specific mechanism — holding the shared namespace open —
as the reason `localhost` communication works between containers in one Pod.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [pause-container, network-namespace, localhost]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Liveness versus readiness probe failure behavior
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the difference in consequence between a failing liveness probe and a failing readiness
probe?

**OPTIONS:**
- [x] A: A failing liveness probe causes the kubelet to kill and restart the container; a failing readiness probe only removes the Pod from a Service's routable endpoints, without restarting anything
- [ ] B: Both cause the same restart behavior; the only difference is which HTTP path is checked
- [ ] C: A failing readiness probe kills the container, while a failing liveness probe only removes it from Service endpoints
- [ ] D: A failing liveness probe deletes the entire Pod permanently, with no automatic replacement

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson states this distinction directly — restart for liveness, traffic removal (not restart)
for readiness — and calls confusing the two a common misconfiguration.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [liveness-probe, readiness-probe, failure-behavior]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the Pod spec's probe configuration
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given this snippet from the `routeplanner` Pod spec, what happens if the application takes 25
seconds to become ready to serve `/healthz` after the container starts?

**CODE_BLOCK:**
```yaml
livenessProbe:
  httpGet: { path: /healthz, port: 8080 }
  initialDelaySeconds: 15
  periodSeconds: 20
```

**OPTIONS:**
- [x] A: The kubelet's first liveness check fires at 15 seconds, before the app is ready, likely fails, and — if this pattern repeats each subsequent 20-second period faster than the app actually finishes starting — the container gets killed and restarted in a self-inflicted crash loop
- [ ] B: Nothing happens; `initialDelaySeconds` guarantees the probe will not fail regardless of application startup time
- [ ] C: The Pod is immediately marked `Pending` and never scheduled
- [ ] D: `periodSeconds: 20` means the probe only ever runs once, 20 seconds after the container starts

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is exactly the probe-induced crash loop the lesson describes — an `initialDelaySeconds`
shorter than actual startup time causes premature liveness failures and restarts.

**LESSON_CONNECTION:** Chapter Body, Pod spec example
**KEYWORDS:** [initialDelaySeconds, crash-loop, probe-misconfiguration]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the job state was lost on Pod eviction
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did the in-progress route-optimization job's state
disappear when the Pod was evicted during a node drain?

**OPTIONS:**
- [ ] A: `fluent-bit` deleted the file before shipping it
- [x] B: The state was written to the sidecar container's local disk (effectively the Pod's `emptyDir`), and a Pod has no durable identity — its replacement is a brand-new Pod with a new name, new IP, and a fresh, empty `emptyDir`, not the same Pod resuming
- [ ] C: The node drain corrupted the cluster's etcd store
- [ ] D: Redis was down at the time of the node drain, so the state could not be persisted anywhere

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's central warning about Pod ephemerality — anything written to an `emptyDir`
or the container's own writable layer does not survive Pod replacement.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [pod-ephemerality, emptyDir-loss, state-placement]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Init containers versus retry logic in the app itself
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend an init container for "waiting for Redis to become reachable" rather
than a retry loop written into `routeplanner`'s own application startup code?

**OPTIONS:**
- [x] A: An init container runs to completion before the main container starts at all, keeping setup-ordering logic (a concern about Pod lifecycle) separate from the application's own responsibility, and the main container's status reporting isn't muddied by startup-retry state
- [ ] B: Application code is technically incapable of implementing retry loops
- [ ] C: Init containers run concurrently with the main container, so they finish faster
- [ ] D: Kubernetes forbids any form of retry logic inside application code

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson frames this as a separation-of-concerns argument: the init container's guaranteed
completion-before-start behavior is the mechanism, not a technical restriction on application code.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [init-container, separation-of-concerns]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** QoS class and eviction priority
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What determines whether a Pod is evicted first under node memory pressure, according to the
lesson's QoS class explanation?

**OPTIONS:**
- [ ] A: The Pod's age — older Pods are always evicted first
- [x] B: Its QoS class, derived from its resource requests and limits: `BestEffort` Pods (no requests or limits at all) are evicted before `Burstable`, and `Guaranteed` Pods (requests equal to limits) are evicted last
- [ ] C: Whether the Pod has a sidecar container attached
- [ ] D: The number of restarts the Pod has already had

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson names the three QoS classes and their derivation directly, and states the eviction
order explicitly: `BestEffort` first, `Guaranteed` last.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [qos-class, eviction-priority, guaranteed-burstable-besteffort]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Port claims within one Pod
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
If `routeplanner` listens on port 8080 and its `fluent-bit` sidecar also needs to expose a
diagnostics endpoint, what constraint does the lesson say applies?

**OPTIONS:**
- [ ] A: Kubernetes automatically remaps conflicting ports between containers in the same Pod
- [x] B: The two containers share the Pod's single IP and network namespace, so `fluent-bit` must listen on a distinct port from 8080 — there is no port isolation between containers in the same Pod the way there is between separate Pods
- [ ] C: Only one container per Pod may expose any port at all
- [ ] D: Sidecar containers are prohibited from listening on any network port

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This follows directly from the shared-network-namespace mechanism — one IP, one port space, so
distinct ports are required, with no automatic remapping.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [shared-ip, port-collision, sidecar-ports]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Diagnosing a probe-induced crash loop
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson say you can tell a crash loop is caused by liveness-probe misconfiguration
rather than an actual application crash?

**OPTIONS:**
- [x] A: `kubectl describe pod` shows an escalating `RESTARTS` count paired with `Liveness probe failed` events, a distinct, diagnosable pattern from an application-originated crash
- [ ] B: There is no way to distinguish the two; both require the same fix
- [ ] C: A probe-induced crash loop never appears in `kubectl describe pod` output at all
- [ ] D: Application crashes always show a `FailedScheduling` event, while probe failures never do

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson names the specific diagnostic signal — `Liveness probe failed` events alongside rising
`RESTARTS` — as what makes this pattern identifiable rather than mysterious.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [crash-loop-diagnosis, restarts-count, describe-pod]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What a shared emptyDir volume actually is
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
When `routeplanner` and `fluent-bit` both mount the Pod's `request-log` `emptyDir` volume, what is
actually true about what each container sees?

**OPTIONS:**
- [ ] A: Each container gets its own independent copy of the volume, synced periodically
- [x] B: Both containers are mounting the same underlying directory — a write by one is immediately visible to the other, with no network hop involved, because it is genuinely one shared directory, not two separate ones
- [ ] C: Only the container that declares the volume first can write to it; the other can only read metadata
- [ ] D: `emptyDir` volumes cannot be mounted into more than one container in the same Pod

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson states this precisely: a Pod-level volume mounted into two containers is the same
underlying directory, which is the mechanism that makes the sidecar log-shipping pattern work.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [emptyDir, shared-volume, sidecar-pattern]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 12

```yaml
lesson_id: fde-elective-containerization-orchestration-12-replicasets-deployments-and-sidecars
lesson_title: "ReplicaSets, Deployments, and Sidecars"
lesson_order: 12

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Explain why a Deployment owns a ReplicaSet rather than Pods directly, and what a revision history buys you that a bare ReplicaSet does not."
  - "Force a rolling update to fail partway through, read the resulting state, and roll back using revision history rather than reapplying an old manifest by hand."
  - "Measure a sidecar's effect on Pod startup and resource requests, and decide whether that cost is acceptable for the behavior it adds."

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
# ReplicaSets, Deployments, and Sidecars

## Concepts Covered

A `ReplicaSet` is a control loop with exactly one job: keep a specified number of Pods matching a
label selector running, creating replacements the instant the observed count drops below the
desired count, and deleting the excess if it rises above. It has no concept of a previous version —
if you edit a ReplicaSet's Pod template, existing Pods are untouched; only newly created ones (to
replace a deleted one, for instance) pick up the change, which makes a bare ReplicaSet a poor tool
for rolling out a new application version deliberately. A `Deployment` sits one layer above a
ReplicaSet specifically to solve that gap: a Deployment owns one or more ReplicaSets (never Pods
directly) and manages a rollout by creating a brand-new ReplicaSet for the new Pod template, scaling
it up gradually while scaling the old ReplicaSet down in step, governed by `maxSurge` (how many
extra Pods beyond the desired count are allowed during the transition) and `maxUnavailable` (how
many of the desired count are allowed to be missing) — this is what "rolling" means concretely, not
a single atomic swap but a controlled, gradual handoff between two ReplicaSets that briefly coexist.
Every old ReplicaSet a Deployment created is kept around, scaled to zero, as revision history
(`kubectl rollout history deployment/routeplanner`), which is what makes `kubectl rollout undo`
possible: rolling back means scaling a previous ReplicaSet back up and the current one down — the
exact same mechanism as a forward rollout, run in reverse, not a special-cased operation.

A rollout's health is judged by the new ReplicaSet's Pods actually passing their readiness probes,
not merely by the new containers starting — if the new Pods hit `CrashLoopBackOff` or never pass
readiness, the Deployment controller keeps `maxUnavailable` old Pods alive rather than tearing them
down, so a failed rollout does not, by itself, take the service down; it stalls in a mixed state
with some traffic still served by the last-known-good version, which is precisely the property that
makes `kubectl rollout undo` a safe, reversible operation rather than a scramble. Adding a sidecar
to a Deployment's Pod template changes this calculation directly: a sidecar container adds its own
image pull time and its own resource requests to every single Pod the ReplicaSet creates, so a
lightweight `fluent-bit` sidecar that adds 15 seconds to image pull and 100Mi of memory per replica
means a Deployment running 20 replicas now needs 2Gi of memory it didn't before, purely for
sidecars, and a rollout of that Deployment now needs proportionally more capacity headroom during
the surge window (`maxSurge` Pods, each carrying the sidecar too) before it can complete. None of
this makes a sidecar the wrong choice — request tracing or centralized logging genuinely benefits
from the shared-namespace pattern the previous lesson covered — but the cost is not free, and an
FDE sizing a cluster or setting a rollout's `maxSurge`/`maxUnavailable` needs to account for the
sidecar's footprint multiplied across every replica and every surge Pod, not just the primary
container's.

```yaml
# routeplanner-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: routeplanner
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels: { app: routeplanner }
  template:
    metadata:
      labels: { app: routeplanner }
    spec:
      containers:
        - name: routeplanner
          image: routeplanner@sha256:8a21...   # v2 — new revision
          readinessProbe:
            httpGet: { path: /ready, port: 8080 }
            periodSeconds: 5
```

```bash
$ kubectl rollout status deployment/routeplanner
Waiting for deployment "routeplanner" rollout to finish:
2 out of 4 new replicas have been updated...
error: deployment "routeplanner" exceeded its progress deadline

$ kubectl rollout history deployment/routeplanner
REVISION  CHANGE-CAUSE
1         kubectl apply --record (image sha256:3f9c...)
2         kubectl apply --record (image sha256:8a21...)

$ kubectl rollout undo deployment/routeplanner --to-revision=1
deployment.apps/routeplanner rolled back
```

## Practical Backend Scenario

Northwind ships `routeplanner` v2 with a database-driven feature that reads a new column the
migration hasn't actually run yet in this environment; the Deployment's rolling update starts,
`maxSurge: 1, maxUnavailable: 0` (zero tolerance for capacity loss during rollout), and the first
new-revision Pod hits `CrashLoopBackOff` on the missing column, never passing its readiness probe.
Because `maxUnavailable: 0`, the Deployment controller refuses to scale down any old, healthy v1
Pods until the new ones prove ready — the rollout stalls with 3 old Pods still serving all customer
traffic and one broken new Pod cycling restarts, and `routeplanner` never actually goes down for
Northwind's users despite the failed deploy. The FDE runs `kubectl rollout status` to confirm the
stall, `kubectl rollout history` to see revision 1 (the working image) still recorded, and `kubectl
rollout undo --to-revision=1` to scale the old ReplicaSet back to 4 and the broken one to 0 — the
exact same mechanism as the original rollout, run in reverse — restoring full capacity in under a
minute without anyone hand-editing a manifest or guessing which image tag was previously live.

## Practice Loop

1. Deploy `routeplanner` v1 as a 4-replica Deployment with `maxSurge: 1, maxUnavailable: 0`, and
   confirm with `kubectl get rs` that exactly one ReplicaSet exists, scaled to 4.
2. Push a v2 image with a deliberately broken readiness probe (pointing at a path that 404s) and
   apply the updated Deployment, then watch `kubectl get pods` to see the mixed state of old and
   new Pods.
3. Count how many old v1 Pods remain serving traffic during the stalled rollout, and confirm via
   `kubectl get endpoints routeplanner` that none of the broken v2 Pods are in the Service's
   endpoint list — this measures the actual customer-facing impact, which should be zero.
4. Run `kubectl rollout undo deployment/routeplanner --to-revision=1` and time how long it takes
   for `kubectl get rs` to show the original ReplicaSet back at 4 replicas and the broken one at 0.
5. Add a `fluent-bit` sidecar to the Pod template, redeploy, and compare the new rollout's
   pull-time and peak memory usage (base replicas plus `maxSurge` Pods, each now carrying the
   sidecar) against the pre-sidecar numbers from step 1.

## Evidence of Understanding

You can explain why a Deployment owns a ReplicaSet rather than Pods directly, and what
`maxSurge`/`maxUnavailable` concretely control during a rolling update. You can force a rollout to
fail, read `kubectl rollout status` and `kubectl rollout history` to understand the stalled state,
and roll back with `kubectl rollout undo` rather than reapplying an old manifest by hand. You can
measure a sidecar's added pull-time and memory cost per replica and per surge Pod, and state
whether that cost is acceptable against the behavior the sidecar adds.

## Suggested Extension

Change `maxUnavailable` from `0` to `1` on the same Deployment, force the same broken rollout, and
compare how much capacity is actually lost during the stall versus the zero-tolerance configuration
— then state which setting Northwind should use for a customer-facing service versus an internal
batch worker.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why a bare ReplicaSet is a poor rollout tool
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a bare `ReplicaSet`, without a `Deployment` managing it, is a poor tool for
rolling out a new application version deliberately?

**OPTIONS:**
- [x] A: Editing a ReplicaSet's Pod template does not touch existing Pods — only newly created ones pick up the change, so there is no controlled, gradual mechanism for replacing the running version
- [ ] B: ReplicaSets cannot run more than one replica at a time
- [ ] C: A ReplicaSet automatically deletes all its Pods the moment its template is edited
- [ ] D: ReplicaSets do not support readiness probes

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is explicit: a ReplicaSet's job is only maintaining a count against a template, with no
concept of a previous version or a controlled transition — that's exactly the gap a Deployment
fills.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [replicaset-limitation, no-rollout-mechanism]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What "rolling" concretely means
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what does a "rolling" update concretely consist of at the ReplicaSet level?

**OPTIONS:**
- [ ] A: All old Pods are deleted simultaneously, then all new Pods are created at once
- [x] B: A Deployment creates a brand-new ReplicaSet for the new template and scales it up gradually while scaling the old ReplicaSet down in step, governed by `maxSurge` and `maxUnavailable`, so the two ReplicaSets briefly coexist
- [ ] C: A single ReplicaSet has its Pods updated one at a time in place, without any new ReplicaSet being created
- [ ] D: The Deployment pauses all traffic until every new Pod is confirmed healthy

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson defines rolling update as a controlled, gradual handoff between two coexisting
ReplicaSets, not an atomic swap or in-place Pod mutation.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [rolling-update, maxSurge, maxUnavailable]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the stalled rollout status
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given this `kubectl rollout status` output, what does it tell you about the current state of the
Deployment?

**CODE_BLOCK:**
```
$ kubectl rollout status deployment/routeplanner
Waiting for deployment "routeplanner" rollout to finish:
2 out of 4 new replicas have been updated...
error: deployment "routeplanner" exceeded its progress deadline
```

**OPTIONS:**
- [x] A: The rollout is stalled — only 2 of 4 replicas have successfully transitioned to the new revision, and the Deployment has exceeded its configured progress deadline without completing
- [ ] B: The rollout has completed successfully with 2 replicas remaining on the old version by design
- [ ] C: The Deployment has been deleted and needs to be recreated
- [ ] D: All 4 replicas are running the new revision, but 2 have failed their liveness probes

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The output states explicitly that only 2 of 4 have updated and the progress deadline was exceeded
— a stalled, incomplete rollout, not a successful or intentional partial state.

**LESSON_CONNECTION:** Chapter Body, kubectl example
**KEYWORDS:** [rollout-status, progress-deadline, stalled-rollout]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why customer traffic stayed up during the stalled rollout
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did `routeplanner` never actually go down for customers
despite the v2 rollout failing?

**OPTIONS:**
- [ ] A: Kubernetes automatically rolled back to v1 the instant the first Pod crashed
- [x] B: With `maxUnavailable: 0`, the Deployment controller refused to scale down any old, healthy v1 Pods until new Pods proved ready, so all 3 remaining v1 Pods kept serving all customer traffic while the rollout stalled
- [ ] C: `routeplanner` has no customer-facing traffic during a rollout by design
- [ ] D: The broken v2 Pod was, coincidentally, never selected by the load balancer

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The `maxUnavailable: 0` configuration is exactly what prevents capacity loss during a failed
rollout — old Pods are only removed once new ones are confirmed ready.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [maxUnavailable, zero-downtime-stall, rollout-safety]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What rollback actually does
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does `kubectl rollout undo` actually do mechanically, per the lesson?

**OPTIONS:**
- [ ] A: It deletes the Deployment and recreates it from a backup snapshot
- [x] B: It scales a previous, retained ReplicaSet back up and the current one down — the exact same mechanism as a forward rollout, run in reverse
- [ ] C: It reverts every Pod's container image individually, in place, without touching any ReplicaSet
- [ ] D: It requires the original manifest file to be reapplied manually before it can proceed

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is explicit that rollback is not a special-cased operation — it's the same
scale-up/scale-down mechanism as a forward rollout, applied to the previous ReplicaSet.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [rollout-undo, revision-history, rollback-mechanism]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** How a rollout's health is actually judged
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what determines whether the Deployment controller considers a new Pod
during a rollout "successfully updated"?

**OPTIONS:**
- [ ] A: The new container process starting, regardless of application-level health
- [x] B: The new Pod actually passing its readiness probe, not merely its container starting
- [ ] C: The Pod being scheduled to a node, regardless of its running state
- [ ] D: A fixed timer elapsing after the container image is pulled

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson states rollout health is judged by readiness-probe success, not merely by containers
starting — this is why a `CrashLoopBackOff` Pod correctly stalls the rollout instead of being
counted as done.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [readiness-probe, rollout-health]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** How a sidecar's cost multiplies across a Deployment
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson states a sidecar adding 100Mi of memory per replica means a 20-replica Deployment needs
2Gi more memory purely for sidecars. Why does the lesson also say a rollout of that same Deployment
needs proportionally more capacity headroom during the surge window?

**OPTIONS:**
- [x] A: Each `maxSurge` Pod created during the rollout also carries the sidecar, so the extra memory requirement applies to every surge Pod as well as every steady-state replica, not just the base 20
- [ ] B: `maxSurge` Pods never include sidecar containers, so no additional headroom is actually needed
- [ ] C: Sidecars are only instantiated after a rollout completes, so they don't affect surge capacity
- [ ] D: The sidecar's memory requirement only applies once, regardless of replica or surge count

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's point is that the sidecar's footprint multiplies across every Pod the ReplicaSet
creates, including temporary surge Pods during a rollout, not just the steady-state replica count.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [sidecar-cost, maxSurge-headroom, capacity-planning]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Reading revision history
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given this `kubectl rollout history` output, what does revision 1 represent, and why is it still
available to roll back to even though revision 2 is the currently deployed version?

**CODE_BLOCK:**
```
$ kubectl rollout history deployment/routeplanner
REVISION  CHANGE-CAUSE
1         kubectl apply --record (image sha256:3f9c...)
2         kubectl apply --record (image sha256:8a21...)
```

**OPTIONS:**
- [x] A: Revision 1 is the previous, working ReplicaSet and Pod template; the Deployment keeps every old ReplicaSet it created around, scaled to zero, specifically as revision history, which is what makes rolling back to it possible
- [ ] B: Revision 1 is a snapshot of the entire cluster state, unrelated to `routeplanner` specifically
- [ ] C: Revision numbers are cosmetic labels with no connection to any retained ReplicaSet
- [ ] D: Revision 1 no longer exists once revision 2 is deployed; the history is purely a log with nothing to roll back to

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson states directly that old ReplicaSets are kept, scaled to zero, as revision history —
this retained state is what rollback actually operates on, not just a log entry.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [rollout-history, revision-retention]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why the FDE trusted rollback over reapplying an old manifest
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did the FDE use `kubectl rollout undo --to-revision=1`
rather than manually reapplying the previous manifest file to fix the stalled rollout?

**OPTIONS:**
- [ ] A: Manually reapplying a manifest is technically impossible once a rollout has started
- [x] B: `rollout undo` operates on the exact retained ReplicaSet from revision 1, removing any risk of guessing the wrong image tag or reconstructing a manifest from memory, and uses the same well-understood scale-up/scale-down mechanism as any other rollout
- [ ] C: Reapplying an old manifest would delete the Deployment object entirely
- [ ] D: `kubectl apply` cannot be used more than twice on the same Deployment

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scenario's point is precision and speed — the retained ReplicaSet removes any need to guess
or reconstruct the previous state by hand, and the mechanism is identical to a normal rollout.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [rollback-safety, revision-precision]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->
