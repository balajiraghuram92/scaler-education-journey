# Future Platform Migration Plan

**Repository:** Neuralascent / StudyTracker  
**Status:** Planning document; no infrastructure or workflow changes are implied by this file  
**Audience:** Personal learning platform owner, maintainer, and future operators  
**Last reviewed:** 2026-08-24

## 1. Purpose and target outcome

This plan describes a staged evolution from the current single-EC2 Docker deployment to a reproducible AWS platform. It deliberately separates the immediate reliability work from the later infrastructure migration so that learning-content changes can continue without risking user progress.

The target operating model is:

```text
Git push
  -> validate and test
  -> build one immutable multi-platform image release
  -> publish image digests and SBOM
  -> back up / verify the database as required
  -> run one-shot schema migration and reference-data seed
  -> deploy the API and frontend
  -> wait for health and smoke checks
  -> retain the previous release for rollback
```

The later platform target is:

```text
Route 53 / HTTPS
  -> CloudFront + S3 (React frontend)
  -> Application Load Balancer
  -> ECS Fargate API service with autoscaling
  -> RDS PostgreSQL in private subnets

GitHub Actions + OIDC -> ECR -> ECS deployment
Terraform/OpenTofu -> VPC, IAM, ALB, ECS, RDS, S3, CloudFront, alarms
```

Kubernetes/EKS is an optional future path, not the default destination for this personal platform.

## 2. Scope and non-goals

### In scope

- Make the current single-EC2 Docker deployment repeatable from GitHub Actions.
- Make API and frontend images usable on both `linux/amd64` and `linux/arm64` hosts.
- Bootstrap a new EC2 host without undocumented manual setup.
- Preserve PostgreSQL data, curriculum content, notes, and completion state during all moves.
- Later introduce Terraform/OpenTofu, RDS, ECS Fargate, an ALB, autoscaling, S3/CloudFront, secrets management, and observability.
- Keep migrations, seeding, reconciliation, backup, restore, and rollback as observable operations with evidence.

### Not in scope for the immediate phase

- Kubernetes or a multi-service microservice split.
- Automatically applying content reconciliation on every deployment.
- Destructive cleanup of legacy rows, old routes, or PostgreSQL data.
- Rewriting the application into a different backend stack.
- Treating a frontend-embedded API key as a long-term authentication design.

## 3. Current repository baseline

The following facts were confirmed from the current workspace. They are constraints for the next implementation phase.

### Runtime and Compose

- [`docker-compose.yml`](../../docker-compose.yml) runs PostgreSQL 16, the API, and the React/Nginx app on a named bridge network with a named PostgreSQL volume.
- The default API and app services pull published images from GHCR using `IMAGE_API`, `IMAGE_APP`, and `IMAGE_TAG`, defaulting to mutable `latest`.
- [`docker-compose.dev.yml`](../../docker-compose.dev.yml) provides local builds for both images. This is the correct local-build path when a published image does not contain the host architecture.
- The API exposes port 8080 inside its container; Compose publishes it on host port 5000. The app publishes port 80 and optionally 443 in the EC2 deployment command.
- The database is stateful; the API and frontend should be treated as replaceable.

### API lifecycle contract

[`api/Program.cs`](../../api/Program.cs) has explicit, fail-fast operational modes:

- `--migrate` applies EF Core schema migrations and exits.
- `--seed-reference-data` (also `--seed`) runs idempotent reference-data seeding and exits.
- `--reconcile-content --scope <scope> --dry-run|--apply|--verify` handles reviewed content mapping.
- Normal API startup checks connectivity and pending migrations; production startup must not silently repair the schema.
- `/health/live` is a process liveness check. `/health/ready` checks database and schema readiness.

This contract should remain intact through every platform move. Migration and seed tasks must use the same image digest as the service being deployed.

### Current GitHub Actions deployment

`.github/workflows/deploy-api.yml` currently:

- runs on `main` pushes only when the commit message contains `[deploy]`, or by manual dispatch;
- authenticates to AWS using GitHub OIDC;
- builds and publishes API and app images to GHCR;
- builds `linux/arm64` only;
- tags both the commit SHA and `latest`, but the remote commands pull and run `latest`;
- sends an SSM command to an existing EC2 instance;
- does not wait for the SSM command's final status;
- does not run `--migrate` or `--seed-reference-data`;
- stops/removes the running containers before the replacement containers are proven healthy;
- prunes all unused images, weakening binary rollback;
- assumes Docker, the database container, the Docker network, environment file, certificate directories, and IAM/SSM setup already exist on the host.

The first implementation phase should improve this workflow. The workflow file is currently governed by repository policy and should be changed only as an explicitly reviewed implementation task.

### Backup and restore

[`scripts/backup-db.sh`](../../scripts/backup-db.sh) creates a PostgreSQL custom-format dump with `pg_dump` and uploads it to an S3 prefix. [`scripts/restore-db.sh`](../../scripts/restore-db.sh) downloads a selected or latest dump and restores it with `pg_restore`.

Current operational hazards to resolve in the implementation phase:

- The scripts must record the source database identity, image/deployment SHA, dump checksum, size, timestamp, and S3 object version.
- Restore must be rehearsed into an isolated database before a production migration is approved.
- The restore script's container detection redirect should be checked (`/dev/null` spelling) before relying on its fallback behavior.
- The deployment runbook refers to `studytracker-postgres` while Compose names the database `studytracker-db`; the actual production target must be explicitly confirmed and standardized.
- A named Docker volume is not a backup strategy by itself. S3/RDS snapshots and restore evidence are the recovery boundary.

## 4. Principles that govern every stage

1. **Build once, promote by digest.** A release is an immutable API image digest plus frontend image digest, not an unqualified `latest` tag.
2. **Keep state outside replaceable compute.** User data belongs in PostgreSQL/RDS, not in API containers or ephemeral host filesystems.
3. **Schema changes are additive first.** Never require a binary rollback to run a down migration. Expand, deploy compatible code, backfill, switch reads/writes, then consider cleanup in a separately approved release.
4. **Operational jobs are explicit.** Migration, seeding, reconciliation, backup, and restore are one-shot jobs with logs, exit codes, and evidence.
5. **Make retries safe.** Seeds use stable slugs/keys and preserve progress and authored content. Deployment retries must not duplicate rows or double-apply content.
6. **Prefer a small number of services.** This application currently needs a frontend, an API, and a database; a platform migration must not create artificial microservices.
7. **Measure before optimizing.** Autoscaling and higher availability are introduced after request volume, latency, memory, database connections, and cost are visible.
8. **Keep the learning platform operable by one person.** Every recovery action needs a documented command, expected output, owner, and rollback decision.

## 5. Stage 0 — Immediate single-EC2 automation

**Goal:** A new commit can deploy to the existing EC2 host without manual database initialization, architecture surprises, or losing the previous release.

### 5.1 Release pipeline

The workflow should be reorganized into these jobs or clearly separated steps:

1. Checkout the exact commit.
2. Run the repository's allowed validation checks.
3. Build API and app images with Buildx for `linux/amd64` and `linux/arm64`.
4. Push both images tagged with the commit SHA and publish the manifest-list digest.
5. Generate an SBOM and, when practical, scan the image before deployment.
6. Use a protected GitHub `production` environment for the deployment approval and secrets.
7. Send the SSM deployment command with the exact image digests.
8. Poll `get-command-invocation` until the SSM command is `Success` or `Failed`; fail the workflow on any failure or timeout.
9. Publish a deployment summary containing commit SHA, image digests, migration ID, seed result, health result, and rollback image.

Use the commit SHA as the human-readable release label and the digest as the runtime identity. Keep `latest` only as a convenience alias; never use it for a production pull.

### 5.2 EC2 deployment sequence

The remote deployment should be idempotent and fail closed:

```text
check Docker, disk, network, environment file, and database reachability
  -> identify current release and retain it
  -> take/verify backup when the release changes schema or content
  -> pull the exact API/app digests
  -> run API image --migrate
  -> run API image --seed-reference-data
  -> optionally run reconciliation dry-run and publish report
  -> apply reconciliation only after an explicit reviewed gate
  -> start replacement containers
  -> wait for /health/ready and frontend health
  -> smoke-test the public route
  -> remove only superseded containers after the bake check
```

Do not stop the known-good API before the replacement has been pulled and the database preconditions have passed. With one host and ports 80/443, true blue/green needs either a temporary alternate port plus a proxy switch or a short controlled restart; the plan should not claim zero downtime until that switch is implemented.

### 5.3 New EC2 bootstrap

A new host must be created from a versioned bootstrap contract, not from memory. The bootstrap should:

- install a pinned/supported Docker Engine and Compose plugin;
- install and register the SSM agent or use a supported base image that already has it;
- create `/etc/studytracker`, the restricted environment-file permissions, certificate directories, and backup directories;
- attach an instance role with only ECR/GHCR pull, SSM, CloudWatch/log, and backup permissions required by the host;
- create or verify the Docker network and database attachment;
- pull the selected release by digest;
- run migration and seed as one-shot containers;
- start the services and verify liveness/readiness;
- write a machine-readable bootstrap result containing host architecture, release digest, migration ID, and health result.

The bootstrap must be safe to rerun. It must never run `docker compose down -v`, delete the PostgreSQL volume, or overwrite an existing environment file without an explicit operator action.

### 5.4 Single-EC2 exit criteria

- A new EC2 instance can be provisioned and become healthy from the bootstrap procedure alone.
- The same commit can run on an ARM64 EC2 host, AMD64 EC2 host, AMD64 WSL2/Docker Desktop, and an ARM64 developer machine.
- Migration and seed each run exactly once per deployment attempt and return observable exit codes.
- A failed migration leaves the old service running and the deployment fails.
- A failed health check leaves the previous image available for binary rollback.
- A backup and isolated restore rehearsal has preserved row counts, completion state, notes, and curriculum content.

## 6. Image portability contract: amd64 and arm64

The published release must be a multi-platform OCI image index containing at least:

```text
linux/amd64
linux/arm64
```

Docker resolves the correct platform from the host when the image is pulled. Buildx can inspect the resulting manifest and confirm each platform before the release is promoted; see the [Docker `imagetools inspect` reference](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/).

Implementation requirements:

- Use `platforms: linux/amd64,linux/arm64` in the release build.
- Keep the runtime Dockerfiles architecture-neutral; do not hard-code an ARM64 base image.
- Keep the frontend builder on `$BUILDPLATFORM` where it is only compiling static assets, while the Nginx runtime is selected for the target platform.
- Validate all native dependencies and shell utilities used by the API/app images on both architectures.
- Do not set `linux/amd64/v4`; use the standard `linux/amd64` platform identifier unless a specific variant is required and published.
- On local Docker/WSL2, omit `platform:` so Docker selects the host architecture. Use an explicit platform only for a deliberate cross-build.
- For local multi-platform builds, push to a registry or build each platform separately; the default Docker image store cannot load a multi-platform manifest as one local image in every configuration.
- Add a release check equivalent to `docker buildx imagetools inspect IMAGE:SHA` and fail if either required platform is absent.
- Record the image index digest, not just child manifest digests, in the deployment evidence.

This prevents the current failure where an AMD64 Docker host cannot pull an ARM64-only published image.

## 7. Stage 1 — Infrastructure as code and reproducible environments

**Goal:** A disposable environment can be recreated without clicking through undocumented AWS console settings.

Use Terraform or OpenTofu in a future `infra/` area with remote, encrypted, versioned state and state locking. Keep environment values separate from reusable modules:

```text
infra/
  modules/network
  modules/ec2-single-host
  modules/registry
  modules/observability
  environments/dev
  environments/prod
```

The first IaC scope should describe the existing EC2 shape: VPC/subnets, security groups, instance profile, SSM, DNS/certificate references, backup bucket, and host bootstrap. It should not attempt an infrastructure migration and application migration in the same change.

### New-environment bootstrap contract

For every environment, the provisioning output must identify:

- AWS account and region;
- environment name;
- host architecture and AMI;
- network and security-group IDs;
- database endpoint and secret reference;
- image registry and deployment role;
- public hostname and certificate;
- backup bucket/prefix and retention;
- release version and health URL.

The environment is not considered ready until Terraform/OpenTofu apply, host bootstrap, migration, seed, health checks, and restore validation all have evidence. Secrets are injected by Secrets Manager/SSM Parameter Store or a narrowly protected environment file; they are never committed to state, logs, or the repository.

## 8. Stage 2 — Move PostgreSQL from the EC2 host to RDS

**Goal:** Replacing compute cannot destroy learning progress.

Provision an RDS PostgreSQL instance in private subnets with:

- encryption at rest and TLS in transit;
- automated backups and a defined retention period;
- point-in-time recovery;
- a security group permitting PostgreSQL only from the application security group;
- deletion protection in production;
- a parameter group and engine version recorded in IaC;
- CloudWatch database metrics and connection alarms;
- a maintenance window appropriate for a personal platform.

RDS automated backups and point-in-time recovery provide a recovery path independent of the application host; see the [AWS RDS backup and restore guide](https://docs.aws.amazon.com/AmazonRDS/latest/gettingstartedguide/managing-backup-restore.html).

### Data migration sequence

1. Freeze or explicitly quiesce writes for the cutover window.
2. Take a final verified custom-format `pg_dump` from the EC2 PostgreSQL container.
3. Restore into a new RDS database or a temporary validation database.
4. Run schema migration only if the restored target is behind the selected application release.
5. Compare table counts, completion counts, note counts, curriculum counts, and representative checksums.
6. Run API read-only smoke checks against the RDS endpoint.
7. Change the database secret/connection reference to RDS.
8. Run one-shot migration and idempotent seed against RDS.
9. Start the API against RDS and verify readiness and user progress.
10. Keep the EC2 database intact and read-only for the agreed rollback window.

Preserve at minimum:

```text
legacy verticals and tasks
canonical courses, modules, and lessons
notes, resources, diagrams, and authored content
completion flags and timestamps
reconciliation/link rows
user/profile identifiers and any learning activity
```

Do not restore over the source database during rehearsal. A data rollback is a separate incident procedure, not the normal response to a bad frontend or API binary.

## 9. Stage 3 — ECS Fargate, ALB, and autoscaling

**Goal:** Replace one replaceable API container with a managed, horizontally scalable API service while keeping the database stateful and external.

Use ECR for AWS-native image storage when this stage begins, or retain GHCR temporarily if the IAM/network tradeoff is documented. The release contract remains the same: commit SHA plus immutable digest.

### ECS design

- One ECS cluster and one API service initially.
- Fargate tasks in private subnets; no public IP for the API task.
- An ALB in public subnets terminates HTTPS and routes to the API target group.
- The target group uses `/health/ready` for readiness and `/health/live` for liveness where appropriate.
- The service starts with desired count 1 for cost control, then moves to 2 before a high-availability claim is made.
- The API must remain stateless; no uploaded content or durable local files are required for correctness.
- CloudWatch logs use a retention period and structured fields including deployment SHA and correlation ID.
- Autoscaling begins with CPU/memory and later adds request count or latency only after baselines exist.
- RDS connection limits are part of capacity planning; scaling API tasks without a connection-pool strategy can overload PostgreSQL.

ECS supports ALB routing for Fargate services; see [AWS ECS load balancing](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-load-balancing.html). Enable ECS deployment circuit-breaker rollback so an unhealthy task set does not replace the last completed deployment; see the [ECS deployment circuit breaker guidance](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html).

### ECS release ordering

```text
publish API/app digest
  -> run migration task with API digest
  -> run seed task with API digest
  -> run reviewed reconciliation task if approved
  -> update ECS task definition/service
  -> wait for steady state and ALB health
  -> run smoke checks
```

The migration task must complete before the service deployment. It must be safe to retry after a transient failure. Content reconciliation should remain a manual or separately approved release job because it changes mappings and can have domain-specific exceptions.

## 10. Stage 4 — S3/CloudFront frontend

**Goal:** Remove frontend availability and TLS concerns from the EC2 host.

Build the Vite app once, upload the versioned static assets to S3, and serve them through CloudFront:

- private S3 bucket with CloudFront Origin Access Control;
- immutable hashed assets with long cache lifetimes;
- short-cache `index.html` so releases become visible quickly;
- CloudFront HTTPS certificate and custom domain;
- SPA fallback for client-side routes;
- deployment invalidation only for the entry document or other non-hashed objects;
- release manifest containing commit SHA and asset version;
- rollback by switching the CloudFront origin/prefix or restoring the previous asset manifest.

The API remains behind the ALB. The frontend should not bake a durable privileged secret into JavaScript. The current `VITE_API_KEY` build argument is a compatibility mechanism, not a secure user-authentication boundary; replace it with owner authentication, a same-origin backend boundary, or a deliberately limited public-client credential before exposing sensitive mutations broadly.

## 11. Observability and operations

### Minimum signals

- API request count, 4xx/5xx rate, p50/p95 latency, and response size.
- `/health/live` and `/health/ready` status.
- ECS task restarts, deployment steady-state time, ALB target health, and autoscaling actions.
- RDS CPU, memory pressure, storage, connections, I/O latency, and replica/backup health when applicable.
- Migration/seed/reconciliation duration, exit code, release digest, migration ID, and run ID.
- Backup age, backup size, upload result, restore-test result, and retention status.
- Frontend CloudFront 4xx/5xx, origin errors, cache hit ratio, and deployment version.

### Logging rules

Carry `correlationId`, `deploymentSha`, `migrationId`, `reconciliationRunId`, route, duration, and result through logs. Never log API keys, passwords, tokens, Markdown bodies, personal notes, or raw database dumps. Use CloudWatch log groups with explicit retention and alarms rather than unlimited default retention.

### Security baseline

- GitHub Actions uses OIDC with a trust policy restricted to this repository, branch/tag, and protected environment; do not add long-lived AWS access keys. See [GitHub's AWS OIDC guidance](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).
- Use separate deploy, runtime, and read-only backup roles.
- Restrict the EC2/ECS task role to the exact registry, logs, secrets, and database operations it needs.
- Keep RDS private and permit access only from the application security group.
- Store secrets in Secrets Manager or SSM Parameter Store with rotation ownership documented.
- Enable encryption for EBS, RDS, S3, logs, registry artifacts, and Terraform/OpenTofu state.
- Require protected production approvals and branch/tag conditions for deployment.
- Add dependency/image scanning and secret scanning to CI.
- Treat the API key exposed through a Vite bundle as non-secret until the authentication design changes.

## 12. Backup, restore, and data-preservation policy

### EC2 phase

- Run the repository backup script or an equivalent host-controlled job on a schedule.
- Upload custom-format dumps to an encrypted, versioned S3 bucket with lifecycle retention.
- Keep at least one backup outside the EC2 volume and one restore-tested copy.
- Test restore into an isolated PostgreSQL database at least once per migration milestone.
- Record RPO, RTO, dump checksum, source identity, target identity, and validation counts.

### RDS phase

- Use native automated backups/PITR for operational recovery.
- Use manual snapshots before migrations and major content reconciliation.
- Keep periodic logical exports for portability and an isolated restore rehearsal.
- Test restoration to a new RDS instance, then point a disposable API at it and verify real routes/progress.

### Data invariants

Every migration must prove:

```text
legacy row counts are preserved
completed counts are preserved
notes/resources/authored bodies are preserved
stable slugs remain unique and resolvable
verified mappings still point to the same canonical content
no PostgreSQL volume or table is deleted as part of deployment
```

## 13. Rollback model

### Binary/application rollback

1. Stop promotion of the new release.
2. Use the previous known-good API/app image digests.
3. Restore the previous ECS task definition or EC2 container release.
4. Confirm `/health/ready`, key API routes, chapter reads, and completion updates.
5. Keep the additive schema in place unless it is proven to corrupt data.

### Database rollback

Do not automatically run EF down migrations. Use a restored snapshot or logical dump only when there is confirmed data corruption, an incompatible schema change, or an approved incident procedure. Database restore requires a maintenance decision because it can discard valid writes made after the recovery point.

### Content reconciliation rollback

Do not delete canonical lessons or legacy rows to undo a mapping mistake. Use the reconciliation run ID, mark/review incorrect links, restore from the approved backup if necessary, and rerun a corrected deterministic reconciliation. Preserve substantive authored content and completion state.

## 14. Cost controls for a personal learning platform

- Keep the current single EC2 host until repeatability or availability is a real problem.
- Use one small/burstable RDS instance initially and set storage alarms before scaling.
- Use ECS Fargate desired count 1 initially; use 2 only when availability requirements justify it.
- Avoid NAT gateways for a low-volume personal environment unless private outbound architecture requires them; evaluate VPC endpoints and documented egress tradeoffs.
- Use S3/CloudFront for static assets rather than an always-on frontend container once that stage is reached.
- Apply CloudWatch log retention and S3 lifecycle policies.
- Add AWS Budgets alarms and cost anomaly detection before enabling autoscaling.
- Tag every resource with `project`, `environment`, `owner`, `cost-center`, and `managed-by`.
- Keep dev and prod resources separate and destroy disposable dev environments through IaC rather than manual cleanup.

## 15. Milestones and entry/exit criteria

| Milestone | Outcome | Entry criteria | Exit criteria |
|---|---|---|---|
| M0: Current-state inventory | Known host, image, DB, secret, backup, and route contracts | Existing repository and EC2 access | Target identities and discrepancies recorded; no assumptions about DB container names |
| M1: Reliable single-EC2 release | GitHub Actions deploys a digest, migrates, seeds, waits, and can roll back | Current workflow reviewed; backup target approved | New host bootstrap succeeds; both architectures pull; SSM result is awaited; previous release retained |
| M2: Portable images | One release works on AMD64 and ARM64 | Dockerfiles/buildx available | Manifest contains both platforms; local WSL2 and an ARM64 host smoke-test the same SHA |
| M3: Reproducible EC2 environment | Terraform/OpenTofu and bootstrap can recreate the current shape | M1 stable; state backend and AWS account boundary approved | Disposable environment passes API, frontend, migration, seed, backup, and restore checks |
| M4: RDS cutover | PostgreSQL state survives compute replacement | Restore rehearsal and RPO/RTO approved | RDS restore validates counts and progress; application uses RDS; EC2 source retained during rollback window |
| M5: ECS + ALB | API service is replaceable and health-gated | RDS stable; image registry and IAM design approved | ECS deployment circuit breaker works; ALB health and logs are visible; one-shot jobs run before service rollout |
| M6: S3/CloudFront frontend | Frontend is independently deployable and cacheable | API hostname and CORS/auth design approved | Static release and rollback work; no privileged secret is treated as hidden in the bundle |
| M7: Operational maturity | Backups, alerts, security, and costs are measured | M4/M5 live evidence exists | Restore rehearsal, rollback rehearsal, budget alarms, retention, and runbooks are current |

## 16. Optional EKS/Kubernetes path — only when justified

Choose EKS only if at least one of these becomes true:

- several independently scaling services need a common platform;
- Kubernetes is itself a deliberate learning objective with time for cluster operations;
- the workload needs Kubernetes-native operators, portability, or scheduling controls that ECS does not provide;
- a team already operates EKS and can support upgrades, ingress, IAM, observability, and incident response.

If justified, preserve the same boundaries:

- API `Deployment` and internal `Service`;
- AWS Load Balancer Controller for ALB ingress;
- RDS outside the cluster;
- Helm pre-deployment `Job` for `--migrate` and `--seed-reference-data`;
- External Secrets integration for Secrets Manager;
- readiness/liveness probes using the existing endpoints;
- HPA tied to measured CPU, memory, or request latency;
- immutable image digests and Helm release history;
- PodDisruptionBudget and a tested rollback procedure.

EKS must not be selected simply to solve the current single-EC2 bootstrap problem. Terraform/OpenTofu plus a reliable ECS or EC2 deployment solves that problem with less operational surface area.

## 17. Migration checklist

### Before implementation

- [ ] Confirm the production EC2 instance architecture with `uname -m`.
- [ ] Confirm the actual PostgreSQL container name, network, volume, database endpoint, and backup destination.
- [ ] Confirm the AWS account, region, DNS, certificate, SSM role, GitHub OIDC role, and protected production environment.
- [ ] Record current release image digests and database migration state.
- [ ] Take an approved backup and perform an isolated restore rehearsal.
- [ ] Record baseline counts for users/profiles, legacy tasks, completions, notes, courses, modules, lessons, relationships, and authored content.

### Single-EC2 automation

- [ ] Build and publish API/app images for `linux/amd64` and `linux/arm64`.
- [ ] Verify the image index contains both platforms.
- [ ] Deploy commit SHA/digest, never only `latest`.
- [ ] Run `--migrate` as a one-shot task and fail on non-zero exit.
- [ ] Run `--seed-reference-data` as a one-shot task and capture the result.
- [ ] Run reconciliation dry-run and retain the report.
- [ ] Require explicit approval before reconciliation `--apply`.
- [ ] Wait for SSM completion and verify `/health/live`, `/health/ready`, frontend, and representative chapter/progress routes.
- [ ] Retain the previous release and document the rollback command.

### New environment

- [ ] Provision the host/network/roles through Terraform/OpenTofu or a versioned bootstrap.
- [ ] Inject secrets from the approved secret store.
- [ ] Verify disk, Docker, SSM, network, certificate, and backup prerequisites.
- [ ] Run migration, seed, health checks, and smoke tests automatically.
- [ ] Confirm a rerun is idempotent and does not duplicate content or alter completion state.

### RDS cutover

- [ ] Provision encrypted private RDS with backups, deletion protection, alarms, and an owner.
- [ ] Restore and validate a production-like dump in isolation.
- [ ] Execute the cutover with a documented write-freeze or consistency strategy.
- [ ] Verify counts, checksums, notes, authored bodies, slugs, mappings, and completion state.
- [ ] Switch the application secret to RDS and verify readiness.
- [ ] Retain the EC2 source and rollback artifacts for the agreed period.

### ECS/ALB and frontend

- [ ] Publish the image to the selected registry by digest.
- [ ] Create the one-shot migration/seed task definition.
- [ ] Configure ECS service, ALB target group, HTTPS listener, health checks, logs, and circuit-breaker rollback.
- [ ] Configure conservative autoscaling and RDS connection limits.
- [ ] Publish the frontend to private S3 through CloudFront.
- [ ] Verify SPA routes, API CORS/authentication, cache invalidation, and frontend rollback.

### Operational acceptance

- [ ] Backup age and failure alarms are active.
- [ ] Restore rehearsal is recorded and repeatable.
- [ ] Deployment failure blocks promotion and leaves a known-good release available.
- [ ] Logs and metrics contain release/migration/correlation identifiers without secrets.
- [ ] AWS budget and cost anomaly alarms are active.
- [ ] Runbooks name the exact environment and do not instruct destructive `down -v` troubleshooting.
- [ ] Human owner has approved production cutover and rollback evidence.

## 18. Decision summary

The appropriate sequence for this repository is:

1. Harden the existing GitHub Actions-to-single-EC2 deployment and make the images multi-platform.
2. Add a reproducible EC2 bootstrap and retain PostgreSQL recovery outside the application containers.
3. Introduce Terraform/OpenTofu for environment definition.
4. Move PostgreSQL to RDS before scaling the API.
5. Move the API to ECS Fargate behind an ALB with conservative autoscaling and rollback.
6. Move the static frontend to S3/CloudFront.
7. Consider EKS only after the operational or learning requirements justify its additional cost and complexity.

This gives the platform a reliable path from one personal EC2 instance to a replaceable, observable, and recoverable service without coupling curriculum data to the lifetime of a container or requiring a fresh manual setup for every architecture.

## References

- [AWS ECS load balancing](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-load-balancing.html)
- [AWS ECS deployment circuit breaker](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html)
- [AWS RDS backup and restore](https://docs.aws.amazon.com/AmazonRDS/latest/gettingstartedguide/managing-backup-restore.html)
- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [Docker Buildx multi-platform image inspection](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/)
