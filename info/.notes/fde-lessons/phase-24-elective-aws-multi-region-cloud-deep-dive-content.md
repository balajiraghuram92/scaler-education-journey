# FDE Phase 24 — Elective: AWS Multi-Region Cloud Deep Dive (Lessons 7-12 of 17)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-24-elective-aws-multi-region-cloud-deep-dive-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `elective-aws-multi-region-cloud-deep-dive` ("AWS Multi-Region
Cloud Deep Dive") — a `SupplementalModuleDefinition`, the second of three elective modules now in
scope. This phase is applied fifth in the electives batch, after Phase 20, 21, 22 (which complete
the first elective module, `elective-containerization-orchestration`, 17/17) and Phase 23 (lessons
1-6 of this same module). The ~104-lesson core curriculum is already 100% complete.

This file covers **lessons 7-12 of 17 only** — End-to-End Cloud Project Day through EKS Security
and Operations. A later phase, Phase 25, covers lessons 13-17 (Microservices on AWS Project,
Microservices Project: Phase 2, AWS Security: Identity and Network, AWS Security: Data and
Detection, AWS Security Hands-on) and completes the module — do not add placeholder content for
those 5 lessons here.

**Scenario continuity with Phase 23:** all six lessons continue the same FDE engagement for
**Lighthouse Freight Co.**, a regional freight-forwarding company, building **ManifestFlow** — a
service that ingests customs manifests (PDF/XML) uploaded by freight brokers, extracts structured
shipment data, and routes it to Lighthouse's dispatch system. Phase 23 left ManifestFlow with a
three-tier VPC, CloudWatch/CloudTrail observability, a containerized instance running on a single
EC2 host (Lesson 5), and a serverless intake callback on Lambda/API Gateway (Lesson 6). Lesson 7
(End-to-End Cloud Project Day) is a checkpoint that assembles those pieces into one demoable slice
with a runbook and a deliberate failure drill. Lessons 8-9 then move ManifestFlow's containerized
workload off the single EC2 host from Lesson 5 onto ECS, motivated by exactly the operational gap
that lesson's skeleton names ("a team is ready to leave a single EC2 host but wants a simpler
operational model than a self-managed cluster"). Lessons 10-12 introduce EKS as the alternative
managed-Kubernetes path for a customer team that already has Kubernetes expertise, per Lesson 10's
skeleton scenario.

**Overlap-avoidance note (checked against Module 4 `cloud-devops-infrastructure`, Phases 9-10, and
this elective's own first module `elective-containerization-orchestration`, Phases 20-22):**
Module 4's "EKS, Helm & Production Kubernetes" lesson already covers the AWS-manages-vs-customer-
manages control-plane boundary, EKS Auto Mode, IRSA at an introductory level (a single IAM role
per ServiceAccount), Helm chart deployment and rollback, and GPU node scheduling with taints and
tolerations. Module 4's "Kubernetes Networking" and "Kubernetes Security: RBAC and DevSecOps"
lessons, plus this elective's own first module (Docker/generic-Kubernetes electives, Phases 20-22),
already cover generic Kubernetes mechanics — Pods, Deployments, Services, ingress objects, RBAC
Roles/RoleBindings, NetworkPolicy. Lessons 10-12 here deliberately do not re-teach any of that.
Lesson 10 (EKS Basics) states AWS's specific management boundary once, briefly, then moves straight
into what is genuinely EKS-specific and not covered elsewhere: `eksctl`/`aws eks` cluster creation
mechanics, kubeconfig wiring, the VPC CNI's ENI/IP-per-pod model and its exhaustion failure mode,
and EKS add-ons as a distinct AWS-managed lifecycle from a Helm-installed chart. Lesson 11 (EKS
Advanced) goes deeper on managed node groups versus Fargate profiles as two genuinely different
compute-ownership models, staged cluster upgrades (control plane, then add-ons, then node groups,
in that specific order), and the AWS Load Balancer Controller as the AWS-specific ingress
implementation. Lesson 12 (EKS Security and Operations) goes past Module 4's introductory IRSA
example into the actual OIDC-provider/trust-policy mechanics that make IRSA work, `SecurityGroupPolicy`
for pod-level (not node-level) security groups via the VPC CNI, and control-plane audit-log
enablement and investigation — none of which Module 4's lesson demonstrates mechanically.

---

# LESSON 7

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-07-end-to-end-cloud-project-day
lesson_title: "End-to-End Cloud Project Day"
lesson_order: 7

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 120
content_status: Draft

learning_outcomes:
  - "Sequence a multi-service deployment (network, data, compute, identity, observability) so each step is independently verifiable before the next one starts."
  - "Write a health-check and rollback runbook precise enough that an operator who did not build the system can execute it under time pressure."
  - "Run a deliberate dependency-failure drill against a live deployment and produce timestamped recovery evidence rather than a verbal claim that recovery works."

created_date: "2026-09-01"
last_updated: "2026-09-01"
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
# End-to-End Cloud Project Day

## Concepts Covered

Every prior lesson in this module produced one working piece of ManifestFlow in isolation — a VPC
with a verified reachability boundary, CloudWatch alarms on a queue backlog, a CloudTrail-backed
incident timeline, a containerized service on a single EC2 host, and a serverless intake callback.
A project day is where those pieces have to compose into one deployable, demoable, recoverable
slice, and composing them exposes a category of defect that no individual lesson's scenario ever
surfaces: sequencing. An RDS instance that takes four minutes to become available will make an
application's first health check fail if the deployment script does not wait for it; a security
group written against a load balancer that has not been created yet will reference an ID that does
not exist. The discipline that prevents this is treating deployment as an ordered pipeline with an
explicit verification gate after each stage, not a single `terraform apply` or shell script that
either succeeds completely or fails somewhere in the middle with no record of how far it got.
Health checks belong at each gate, not only at the end: verifying the VPC's route tables before
provisioning compute, verifying RDS is `available` and reachable from the app subnet before
deploying the application, and verifying the application's own `/healthz` returns 200 before
wiring it behind a load balancer or before declaring the project day's demo path "done."

The second discipline a project day forces is writing the runbook for someone who is not you. An
FDE who built every layer personally over five prior lessons has all the sequencing and rollback
knowledge in their head; a customer's on-call operator, or a teammate covering for the FDE next
week, has none of it. A runbook that says "redeploy the service" is not a runbook — it needs the
literal command, the expected output, the specific log line or metric that confirms success, and
the specific rollback command if that confirmation does not appear within a stated time window. The
same standard applies to the failure drill: "recovery works" is a claim, and a claim is not
evidence. Breaking one real dependency (stopping the RDS instance, or removing the security group
rule the application needs) and then following the runbook's documented recovery steps, with
timestamps captured at each step, converts the claim into evidence a customer panel — or an
incident retrospective — can actually trust. The deliverable at the end of a project day is not
just a running system; it is a one-page handoff document naming what was built, what was
deliberately deferred (and why), and what the measured recovery time actually was, not what it was
assumed to be.

```bash
# Staged deployment script: each stage gates on a verification check before the next runs
set -euo pipefail

echo "[1/4] Verifying VPC route tables..."
aws ec2 describe-route-tables --route-table-ids "$PRIVATE_DATA_RTB" \
  --query 'RouteTables[0].Routes[?DestinationCidrBlock==`0.0.0.0/0`]' --output text | grep -q '' \
  && { echo "FAIL: private-data subnet has an internet route"; exit 1; } || echo "  OK: no internet route"

echo "[2/4] Waiting for RDS to become available..."
aws rds wait db-instance-available --db-instance-identifier manifestflow-db
aws rds describe-db-instances --db-instance-identifier manifestflow-db \
  --query 'DBInstances[0].Endpoint.Address' --output text

echo "[3/4] Deploying application and polling health check..."
aws ecs update-service --cluster manifestflow --service manifestflow-api --force-new-deployment
for i in $(seq 1 30); do
  status=$(curl -sf -o /dev/null -w '%{http_code}' "https://internal.manifestflow.local/healthz" || echo "000")
  [ "$status" = "200" ] && { echo "  OK: healthz 200 after ${i}0s"; break; }
  sleep 10
done
[ "$status" = "200" ] || { echo "FAIL: healthz never returned 200"; exit 1; }

echo "[4/4] Confirming CloudWatch alarm state is OK before declaring done..."
aws cloudwatch describe-alarms --alarm-names manifestflow-queue-backlog \
  --query 'MetricAlarms[0].StateValue' --output text
```

## Practical Backend Scenario

The customer panel wants a working end-to-end path by close of business: a broker uploads a
manifest through the Lambda/API Gateway callback from Lesson 6, the extraction worker (running on
the EC2 host from Lesson 5) picks it up, and a status query confirms the manifest reached the
dispatch queue — all inside a VPC whose reachability the FDE already verified in Lessons 1-2, with
CloudWatch alarms from Lesson 3 watching the queue depth. The FDE time-boxes discovery to thirty
minutes (confirm which pieces from prior lessons are still live in the sandbox account, which
config values have drifted), then deploys the smallest path that makes the full workflow real
rather than gold-plating any single stage. Mid-afternoon, the FDE deliberately stops the RDS
instance mid-demo-rehearsal to prove the recovery story: the extraction worker's health check
starts failing within thirty seconds, the CloudWatch alarm transitions to `ALARM` within the
evaluation period, and the documented runbook step — restart the RDS instance, wait for
`db-instance-available`, redeploy the worker — brings the workflow back in just under six minutes,
a number the FDE records rather than estimates. The one-page handoff lists three deferred risks
explicitly: no automated failover for the single RDS instance, no synthetic canary running outside
demo hours, and the Lambda callback's DynamoDB idempotency table has no documented backup policy
yet — naming what was not done is as much a part of the deliverable as what was.

## Practice Loop

1. Inventory every resource from Lessons 1-6 still live in the sandbox account and note any
   configuration that has drifted from what those lessons documented (an expired security group
   rule, a stopped instance, a Lambda concurrency limit that was never reset).
2. Write the staged deployment script above (or your own equivalent) with an explicit verification
   gate after each stage, and run it once end-to-end before touching anything else.
3. Break exactly one dependency on purpose — stop the RDS instance, or remove the worker's security
   group rule to the database — and time how long the CloudWatch alarm takes to reach `ALARM`.
4. Execute your own documented recovery runbook against the induced failure, capturing a timestamp
   at each step, and record the actual end-to-end recovery time rather than an estimate.
5. Write the one-page handoff: what was built, the measured recovery time from step 4, and at
   least two deliberately deferred risks with a one-sentence reason each for deferring them.

## Evidence of Understanding

You can sequence a multi-service deployment with an independent verification gate after every
stage, rather than a single script that either fully succeeds or fails somewhere unrecoverable in
the middle. You can write a runbook precise enough — literal commands, expected output, a stated
time window — that someone who did not build the system could execute it under pressure. You have
timestamped evidence, not a verbal claim, that a specific induced failure recovers within a
measured time, and a handoff document that names deferred risk as explicitly as delivered scope.

## Suggested Extension

Add a synthetic canary (a scheduled Lambda that uploads a small test manifest and polls for its
status every five minutes) so the alarm from step 3 above would have fired automatically outside a
rehearsed demo window, and explain why a canary catches a class of failure a passive health check
on the application itself cannot.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why stage the deployment with gates
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist on a verification gate after every deployment stage rather than one script that runs all stages and reports success or failure only at the end?

**OPTIONS:**
- [x] A: A single script that fails midway gives no record of how far it got or which stage actually failed, while gated stages fail fast with a specific, attributable checkpoint
- [ ] B: AWS requires deployment scripts to include explicit sleep statements between API calls
- [ ] C: Gated stages run faster than an ungated script in every case
- [ ] D: Verification gates are only necessary when deploying to more than one AWS region

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's core sequencing argument: composing several working pieces exposes ordering defects that isolated lessons never surface, and a gate after each stage turns an ambiguous mid-script failure into an attributable one.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [deployment-sequencing, verification-gate, staged-rollout]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What makes a runbook actually usable
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why does a runbook step like "redeploy the service" fail as a usable runbook entry?

**OPTIONS:**
- [x] A: It has no literal command, no expected output, and no stated time window or rollback trigger — all things an operator who did not build the system needs
- [ ] B: It is too short; a usable runbook step must be at least one paragraph long
- [ ] C: Runbooks should never mention specific AWS CLI commands, only high-level intent
- [ ] D: It fails only because it does not name a specific engineer to execute it

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson is specific: a usable runbook step needs the literal command, expected output, and a stated time window with a rollback trigger — not vague intent.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [runbook, operational-readiness, handoff]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the staged deployment script's gate 2
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
echo "[2/4] Waiting for RDS to become available..."
aws rds wait db-instance-available --db-instance-identifier manifestflow-db
aws rds describe-db-instances --db-instance-identifier manifestflow-db \
  --query 'DBInstances[0].Endpoint.Address' --output text
```

**QUESTION_TEXT:**
Why does stage 2 call `aws rds wait db-instance-available` before stage 3 deploys the application, instead of proceeding immediately after stage 1 passes?

**OPTIONS:**
- [x] A: RDS instances can take several minutes to become reachable, and deploying the application before then would fail its first health check against a database that is not actually ready yet
- [ ] B: The `wait` subcommand is required syntax for every `aws rds` call regardless of context
- [ ] C: It has no functional purpose; it only improves the script's readability
- [ ] D: It substitutes for creating the RDS instance in the first place

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names exactly this failure mode — an RDS instance that takes minutes to become available will fail the application's first health check if the deployment does not wait for it first.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [rds-wait, deployment-sequencing, health-check]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Claim versus evidence for recovery
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson says "recovery works" is a claim, not evidence. What converts it into evidence, per the scenario?

**OPTIONS:**
- [x] A: Deliberately breaking one real dependency, executing the documented recovery runbook, and capturing timestamps at each step to produce a measured recovery time
- [ ] B: Writing a longer and more detailed description of the recovery process in the handoff document
- [ ] C: Having a second engineer independently agree that recovery should work
- [ ] D: Running the deployment script an additional time without inducing any failure

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is the scenario's explicit recovery drill — a real induced failure plus timestamped execution of the documented runbook is what makes the six-minute recovery time evidence rather than an estimate.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [failure-drill, recovery-evidence, timestamped-runbook]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Deferred risk in the handoff
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The one-page handoff explicitly lists deferred risks such as "no automated failover for the single RDS instance." Why does the lesson treat naming this as important as the delivered scope itself?

**OPTIONS:**
- [x] A: A handoff that only lists what was built lets an unstated gap surface later as a surprise incident instead of a known, prioritized follow-up
- [ ] B: AWS billing requires every deferred risk to be documented for cost-allocation purposes
- [ ] C: Listing deferred risks is a formality with no operational consequence
- [ ] D: It is only necessary when the customer explicitly asks for a risk register

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this directly: naming what was not done is as much a part of the deliverable as what was — an unstated gap becomes a surprise later instead of a tracked decision now.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [deferred-risk, handoff-document, single-instance-risk]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Gate 1's route-table check
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
echo "[1/4] Verifying VPC route tables..."
aws ec2 describe-route-tables --route-table-ids "$PRIVATE_DATA_RTB" \
  --query 'RouteTables[0].Routes[?DestinationCidrBlock==`0.0.0.0/0`]' --output text | grep -q '' \
  && { echo "FAIL: private-data subnet has an internet route"; exit 1; } || echo "  OK: no internet route"
```

**QUESTION_TEXT:**
What does this gate confirm before the script proceeds to provisioning compute, and why does that ordering matter?

**OPTIONS:**
- [x] A: It confirms the private-data route table still has no `0.0.0.0/0` route before anything else is built on top of it, catching a regressed network boundary at the earliest possible stage rather than after compute is already live
- [ ] B: It confirms the RDS instance itself is reachable, which is what stage 2 already checks
- [ ] C: It provisions the route table for the first time as part of the deployment
- [ ] D: It has no ordering purpose; it could run at any point in the script with an identical result

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is the "verify before provisioning compute" gate the lesson describes — catching a network regression at the earliest stage is cheaper than discovering it once an application is already deployed on top of it.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [route-table-verification, staged-gate, network-regression]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Time-boxing discovery
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The FDE time-boxes discovery to thirty minutes before deploying anything. What is the purpose of that time-box in the scenario?

**OPTIONS:**
- [x] A: To confirm which pieces from prior lessons are still live and which config has drifted, without letting discovery consume the time needed to deploy and demonstrate the working path
- [ ] B: AWS enforces a hard thirty-minute limit on how long a sandbox account may run `describe` API calls
- [ ] C: Thirty minutes is the minimum time required for an RDS instance to start
- [ ] D: The time-box exists only to satisfy the customer panel's meeting schedule, with no engineering purpose

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The scenario states the discovery time-box's purpose directly — confirm state and drift without letting discovery crowd out deploying and demonstrating the smallest working path.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [time-boxing, discovery, project-day]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What a synthetic canary catches that a passive health check does not
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The Suggested Extension proposes a synthetic canary that uploads a test manifest every five minutes. Why would this catch a failure class that the application's own passive `/healthz` check would miss?

**OPTIONS:**
- [x] A: A passive health check only confirms the application process is up and can reach its immediate dependencies; a canary exercises the actual end-to-end broker-upload-to-dispatch workflow the customer cares about, catching a break anywhere along that path
- [ ] B: A synthetic canary is functionally identical to `/healthz` and provides no additional coverage
- [ ] C: `/healthz` checks cannot run inside a VPC, so only a canary can verify connectivity
- [ ] D: A canary is only useful for verifying Lambda cold-start latency, unrelated to workflow correctness

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The extension's point is exactly this distinction — a passive check confirms local health, while an active canary exercises the real customer-facing workflow end to end and would fire even outside a rehearsed demo window.
**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [synthetic-canary, passive-health-check, end-to-end-verification]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 8

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-08-aws-ecs-and-ecr-introduction
lesson_title: "AWS ECS and ECR Introduction"
lesson_order: 8

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Push a scanned, immutable-tagged image to ECR and trace it by digest through an ECS task definition and deployed revision."
  - "Distinguish an ECS task's execution role (what the platform does on the task's behalf) from its task role (what the task's own code is permitted to do)."
  - "Diagnose a failed ECS deployment revision from service events and roll back to the last known-good revision."

created_date: "2026-09-01"
last_updated: "2026-09-01"
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
# AWS ECS and ECR Introduction

## Concepts Covered

ManifestFlow's extraction worker has been running on the single EC2 host from Lesson 5, which
means every deployment is a manual sequence of stopping the old container, pulling the new image,
and starting it again — no rolling update, no automatic recovery if the process dies, and no
record of which image tag was actually running at 3 a.m. when something went wrong. ECS (Elastic
Container Service) replaces that manual sequence with a managed orchestration layer while ECR
(Elastic Container Registry) replaces ad hoc image storage with a registry that gives every pushed
image an immutable content digest. The digest — `sha256:...` — is the actual identity of an image;
a tag like `latest` or `v14` is just a mutable pointer that can be repointed to a different digest
at any time, which is why a deployment record that only logs "deployed `v14`" is not trustworthy
evidence of what actually ran — the same tag can mean two different images at two different points
in time. ECR also runs an image scan on push (basic OS-package CVE scanning is free; enhanced
scanning via Inspector covers more), and a customer security review will specifically ask whether a
deployed image was scanned before it reached production, not just whether it eventually was.

An ECS **task definition** is the declarative blueprint — container image (by digest, ideally),
CPU/memory reservation, port mappings, environment variables, log configuration, and two distinct
IAM roles that are easy to confuse: the **execution role** governs what the ECS platform itself is
permitted to do on the task's behalf before your code ever runs — pulling the image from ECR,
writing logs to CloudWatch Logs, retrieving a secret from Secrets Manager to inject as an
environment variable — while the **task role** governs what your application's own code is
permitted to do once it's running, the same way a Lambda's execution role does. A task definition
is versioned every time it changes; deploying a new image produces a new **task definition
revision**, and an ECS **service** maintains a desired count of running tasks from a specific
revision, replacing failed tasks automatically and rolling forward or back across revisions rather
than manually stopping and starting containers. A **cluster** is the logical grouping tasks run in,
and a **capacity provider** determines what actually runs them — Fargate (no EC2 instances to
manage at all) or an EC2 capacity provider (a managed auto-scaling group of instances you still
own the AMI and patching for) — the same Fargate-versus-EC2 trade-off the next lesson covers in
operational depth.

```bash
# Authenticate to ECR and push the extraction-worker image
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 111122223333.dkr.ecr.us-east-1.amazonaws.com

docker build -t manifestflow-worker:build-482 .
docker tag manifestflow-worker:build-482 \
  111122223333.dkr.ecr.us-east-1.amazonaws.com/manifestflow-worker:build-482
docker push 111122223333.dkr.ecr.us-east-1.amazonaws.com/manifestflow-worker:build-482
# -> digest: sha256:c3f8e1a29b7d4c1e8f6a0b2d9c4e7f1a3b5c8d0e2f4a6b8c0d2e4f6a8b0c2d4e

# Register a task definition referencing the image BY DIGEST, not the mutable tag
cat > task-def.json <<'EOF'
{
  "family": "manifestflow-worker",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::111122223333:role/manifestflow-worker-execution-role",
  "taskRoleArn": "arn:aws:iam::111122223333:role/manifestflow-worker-task-role",
  "containerDefinitions": [
    {
      "name": "worker",
      "image": "111122223333.dkr.ecr.us-east-1.amazonaws.com/manifestflow-worker@sha256:c3f8e1a29b7d4c1e8f6a0b2d9c4e7f1a3b5c8d0e2f4a6b8c0d2e4f6a8b0c2d4e",
      "portMappings": [{"containerPort": 8080, "protocol": "tcp"}],
      "secrets": [
        {"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:us-east-1:111122223333:secret:manifestflow-db-password"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/manifestflow-worker",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "worker"
        }
      }
    }
  ]
}
EOF
aws ecs register-task-definition --cli-input-json file://task-def.json
# -> "taskDefinitionArn": ".../manifestflow-worker:14"   <-- revision 14

aws ecs create-service --cluster manifestflow --service-name manifestflow-worker \
  --task-definition manifestflow-worker:14 --desired-count 2 \
  --launch-type FARGATE --network-configuration \
  '{"awsvpcConfiguration":{"subnets":["subnet-0a1b2c3"],"securityGroups":["sg-0worker"],"assignPublicIp":"DISABLED"}}'
```

## Practical Backend Scenario

The customer is ready to leave the single EC2 host — a hurricane-season incident review flagged
that the host's failure would take ManifestFlow's extraction pipeline down entirely with no
automatic recovery, and the team wants a simpler operational model than standing up a self-managed
cluster themselves. The FDE pushes the extraction worker image to a new ECR repository, enabling
scan-on-push, and registers a task definition that references the image by digest rather than a
mutable tag, with two separate roles: an execution role scoped to pull from this one ECR repository
and write to this one CloudWatch log group, and a task role scoped to the worker's actual runtime
needs — reading one S3 bucket of uploaded manifests and writing to one SQS queue, nothing broader.
The first deployed revision (`:14`) works; a follow-up change to add a new environment variable
produces revision `:15`, which the FDE deploys with `update-service --task-definition
manifestflow-worker:15` — and it fails to reach steady state, with `describe-services` showing
tasks starting and immediately stopping. `aws ecs describe-tasks` on a stopped task reveals the
actual stop reason: the new environment variable references a Secrets Manager ARN the execution
role was never granted `secretsmanager:GetSecretValue` on, so the task fails before the
application container even starts. The FDE rolls the service back to revision `:14` immediately,
restoring service, then fixes the execution role's policy and redeploys `:15` cleanly — this time
verifying the stop reason is absent before calling it done.

## Practice Loop

1. Push an image to a new ECR repository with scan-on-push enabled, and capture the resulting
   digest rather than only the tag you pushed it under.
2. Register a task definition referencing the image by digest, with two separate roles — an
   execution role scoped to ECR pull and CloudWatch Logs write, and a task role scoped to only the
   application's actual runtime AWS calls.
3. Create a service from that task definition with a desired count of 2, and confirm both tasks
   reach `RUNNING` with a passing container health check.
4. Deploy a second revision that references a Secrets Manager ARN the execution role has not been
   granted access to, and use `aws ecs describe-tasks` to read the actual stop reason from a
   failed task rather than guessing from the service's steady-state failure alone.
5. Roll the service back to the last known-good task definition revision, confirm steady state
   returns, then fix the execution role's policy and redeploy the fixed revision cleanly.

## Evidence of Understanding

You can identify an image's digest as its actual immutable identity, distinct from a mutable tag,
and reference images by digest in a task definition for that reason. You can name the specific
difference between an execution role (what ECS does on the task's behalf) and a task role (what
the task's own code may do), and diagnose a stopped-task failure to the correct one of the two. You
can read a service's failed-deployment evidence from `describe-tasks`' stop reason rather than
inferring it, and execute a clean rollback to a specific prior task definition revision.

## Suggested Extension

Add a CI step that runs `aws ecs wait services-stable` after every `update-service` call and fails
the pipeline (triggering an automatic rollback to the previous task definition revision) if steady
state is not reached within a bounded timeout, rather than leaving that judgment to a human
watching a dashboard.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Digest versus tag as image identity
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson call a tag like `v14` an untrustworthy record of what image actually ran, while treating the digest as the image's real identity?

**OPTIONS:**
- [x] A: A tag is a mutable pointer that can be repointed to a different digest at any time, so a deployment log recording only the tag cannot prove which actual image content ran
- [ ] B: Tags are deprecated in ECR and no longer supported for new repositories
- [ ] C: Digests are shorter and therefore easier to log than tags
- [ ] D: A digest and a tag always refer to the same image content by definition, making this a non-issue

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson is explicit: a tag is a mutable pointer, and the digest is the image's actual content identity — logging only the tag loses that guarantee.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [image-digest, mutable-tag, ecr]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Execution role versus task role
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the precise difference between an ECS task's execution role and its task role?

**OPTIONS:**
- [x] A: The execution role governs what the ECS platform does on the task's behalf before the application runs (pulling the image, injecting a secret, writing logs); the task role governs what the application's own code may do once it is running
- [ ] B: The execution role and task role are two names for the same IAM concept and can be used interchangeably
- [ ] C: The task role is only used for Fargate tasks, while the execution role is only used for EC2-launch-type tasks
- [ ] D: The execution role only applies to the first task definition revision; later revisions use only the task role

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson draws this exact line — execution role for what the platform does on the task's behalf, task role for what the running application code itself is permitted to do.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [execution-role, task-role, iam]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Diagnosing the revision `:15` failure
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Revision `:15` adds a new environment variable sourced from Secrets Manager, and the task stops immediately after starting, before the application container even runs. Which role's permissions is the actual cause, and why?

**OPTIONS:**
- [x] A: The execution role — it had not been granted `secretsmanager:GetSecretValue` on the new ARN, and injecting the secret is something ECS itself does on the task's behalf before the application starts
- [ ] B: The task role — the application's own code failed while trying to read the secret from within its runtime logic
- [ ] C: Neither role; this specific failure mode is always caused by a security group misconfiguration
- [ ] D: The task role, because Secrets Manager access is always modeled at the task-role level regardless of when the read happens

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Injecting a secret as an environment variable is an execution-role operation performed before the application container starts — exactly the scenario's diagnosis, confirmed via the stopped task's stop reason.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [execution-role, secrets-manager, task-failure-diagnosis]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Reading the task definition's role fields
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```json
{
  "family": "manifestflow-worker",
  "executionRoleArn": "arn:aws:iam::111122223333:role/manifestflow-worker-execution-role",
  "taskRoleArn": "arn:aws:iam::111122223333:role/manifestflow-worker-task-role",
  "containerDefinitions": [
    {
      "name": "worker",
      "secrets": [
        {"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:us-east-1:111122223333:secret:manifestflow-db-password"}
      ]
    }
  ]
}
```

**QUESTION_TEXT:**
Given this task definition excerpt, which role's policy must grant `secretsmanager:GetSecretValue` on the `manifestflow-db-password` secret for the task to start successfully?

**OPTIONS:**
- [x] A: `manifestflow-worker-execution-role`, since the `secrets` field is resolved by ECS before the container starts
- [ ] B: `manifestflow-worker-task-role`, since it is the role most closely associated with the running container
- [ ] C: Both roles must independently grant the same permission, or the task fails
- [ ] D: Neither role needs this permission; `secrets` resolution is handled entirely by the Fargate control plane with no IAM check

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Injecting a `secrets`-block value happens via the execution role, the platform-side identity used before the container's own code runs — reinforcing the same execution-role/task-role distinction as Q2 and Q3.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [task-definition, execution-role, secrets-injection]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** ECR scan-on-push
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson highlight enabling scan-on-push for the new ECR repository specifically, rather than treating it as an optional afterthought?

**OPTIONS:**
- [x] A: A customer security review will specifically ask whether a deployed image was scanned before it reached production, not just whether it was eventually scanned
- [ ] B: ECS refuses to run any image that has not been scanned, so scan-on-push is a hard technical requirement
- [ ] C: Scan-on-push is required only for images referenced by tag, not by digest
- [ ] D: Scanning is purely a cost-optimization feature unrelated to security posture

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson makes this the specific reason to care about scan timing — "before" production, not just "eventually," is what a security review asks about.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [ecr-scan-on-push, security-review]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Cluster, service, and capacity provider
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what is the relationship between an ECS cluster, a service, and a capacity provider?

**OPTIONS:**
- [x] A: A cluster is the logical grouping tasks run in; a service maintains a desired count of tasks from a specific task definition revision; a capacity provider (Fargate or an EC2 auto-scaling group) determines what actually runs those tasks
- [ ] B: A capacity provider is a synonym for a cluster, and a service is what ECR calls a repository
- [ ] C: A service replaces the need for a task definition entirely
- [ ] D: A cluster can only contain one service at a time

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson defines these three terms precisely in that layered relationship — cluster as grouping, service as desired-state management of a revision, capacity provider as the actual compute substrate.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [ecs-cluster, ecs-service, capacity-provider]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Rolling back a bad deployment revision
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
After diagnosing revision `:15`'s failure, what does the FDE do first, before fixing the execution role's policy?

**OPTIONS:**
- [x] A: Roll the service back to the last known-good revision (`:14`) immediately, restoring service, and only then fix the underlying permission and redeploy the corrected revision
- [ ] B: Fix the execution role's policy first, then leave the failing revision `:15` running while the fix propagates
- [ ] C: Delete the ECR repository and start the deployment over from scratch
- [ ] D: Wait for the next scheduled maintenance window before taking any action

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The scenario's sequence is explicit — restore service via rollback first, then diagnose and fix the underlying cause, mirroring the same "stabilize first" discipline as the project-day lesson's runbook.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [ecs-rollback, task-definition-revision, incident-sequencing]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Fargate versus EC2 capacity provider
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what is the essential difference between running ECS tasks on a Fargate capacity provider versus an EC2 capacity provider?

**OPTIONS:**
- [x] A: Fargate has no EC2 instances to manage at all; an EC2 capacity provider is a managed auto-scaling group of instances whose AMI and patching you still own
- [ ] B: Fargate is only usable for tasks with fewer than 256 MB of memory
- [ ] C: An EC2 capacity provider cannot be used with a task definition that references an image by digest
- [ ] D: There is no meaningful difference; the two terms describe the same underlying compute

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this trade-off directly and defers the operational depth of it to the next lesson (ECS Fundamentals) — the essential distinction is who owns the underlying instance lifecycle.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [fargate, ec2-capacity-provider, compute-ownership]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Automating the rollback decision
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The Suggested Extension proposes running `aws ecs wait services-stable` after every `update-service` call in CI. What problem does this solve compared to the manual rollback the FDE performed in the scenario?

**OPTIONS:**
- [x] A: It removes the dependency on a human watching a dashboard to notice a failed deployment, making the bounded-timeout failure and rollback decision automatic and consistent
- [ ] B: It eliminates the need for task definition revisions entirely
- [ ] C: It replaces the need for an execution role on any future task definition
- [ ] D: It guarantees that no future task definition will ever reference an inaccessible secret

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The extension's point is automation of the rollback trigger itself — a bounded wait-and-fail replaces relying on a human to notice and manually decide to roll back.
**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [services-stable, ci-automation, automated-rollback]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 9

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-09-ecs-fundamentals
lesson_title: "ECS Fundamentals"
lesson_order: 9

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Configure a target group health check whose path and port genuinely match what the container serves, and explain the specific failure mode when they disagree."
  - "Read ECS service events to distinguish a task stuck PENDING from one cycling STOPPING, and diagnose each to a distinct root cause."
  - "Configure a rolling deployment's minimum/maximum healthy percent to control blast radius during a bad rollout."

created_date: "2026-09-01"
last_updated: "2026-09-01"
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
# ECS Fundamentals

## Concepts Covered

Running `manifestflow-worker` as an ECS service, rather than a one-off task, means committing to a
specific networking mode and a specific health-check contract, and getting either one slightly
wrong produces a service that looks like it deployed successfully but never actually serves
traffic. `awsvpc` networking mode — required for Fargate, optional but strongly preferred for
EC2-launch-type tasks — gives every task its own elastic network interface (ENI) with its own
private IP address inside the VPC, rather than sharing the host's network namespace the way
classic `bridge` mode does; this is what makes a security group attachable directly to a task
rather than only to the host it happens to land on, closing the same "any pod on this node
inherits the node's networking exposure" gap the containerization elective's networking lesson
raised for Docker bridge networks. An Application Load Balancer's **target group** is the second
half of the contract: the target group's health check path, port, and expected status code must
match what the container actually serves, and these are two independently configured settings that
silently disagree far more often than either configuration is independently wrong — a target group
still checking `/health` on port 80 after the container definition changed to serve `/healthz` on
port 8080 will mark every newly launched task unhealthy, deregister it, and the service will churn
tasks indefinitely while `desired count` never actually reaches `running count`, with no error
message pointing directly at the mismatch.

A service's **rolling deployment** configuration — `minimumHealthyPercent` and
`maximumPercent` — controls exactly how aggressively a deployment replaces old tasks with new ones,
and this is the actual blast-radius control during a bad rollout: `minimumHealthyPercent: 100` with
`maximumPercent: 200` means ECS starts new tasks alongside the old ones and only stops an old task
once its replacement passes health checks, so a bad new revision never drops capacity below what
was already running; the more aggressive default of `minimumHealthyPercent: 50` allows ECS to stop
half the old tasks before any new ones are confirmed healthy, trading deployment speed for a real
capacity dip if the new revision turns out to be broken. Reading `aws ecs describe-services`'
`events` array is the actual diagnostic tool for a stuck deployment — a task that stays `PENDING`
indefinitely is a placement failure (no capacity satisfies the task's CPU/memory reservation, or a
subnet has run out of available IP addresses), while a task that reaches `RUNNING` and then almost
immediately transitions to `STOPPING` is a health-check or application-startup failure, and these
two failure classes point an FDE toward completely different fixes — the events array names which
one occurred, in plain English, rather than requiring you to correlate CloudWatch metrics to guess.

```bash
# Create a target group whose health check matches the container's actual contract
aws elbv2 create-target-group --name manifestflow-worker-tg --protocol HTTP --port 8080 \
  --vpc-id vpc-0a1b2c3d4e5f60789 --target-type ip \
  --health-check-path /healthz --health-check-port 8080 \
  --healthy-threshold-count 2 --unhealthy-threshold-count 3 --health-check-interval-seconds 15

# Update the service with a conservative rolling-deployment configuration
aws ecs update-service --cluster manifestflow --service manifestflow-worker \
  --task-definition manifestflow-worker:16 \
  --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...:targetgroup/manifestflow-worker-tg/abc,containerName=worker,containerPort=8080"

# Diagnose a stuck deployment from service events
aws ecs describe-services --cluster manifestflow --services manifestflow-worker \
  --query 'services[0].events[:5]'
# -> [
#      "service manifestflow-worker registered 0 targets in (target-group arn) due to unhealthy state",
#      "service manifestflow-worker (port 8080) is unhealthy in target-group manifestflow-worker-tg due to (reason Health checks failed)",
#      "service manifestflow-worker has started 2 tasks: task 8f1a... task 3c9b..."
#    ]

# Confirm whether tasks are stuck PENDING (placement) or cycling STOPPING (health/startup)
aws ecs describe-tasks --cluster manifestflow --tasks 8f1a3c9b \
  --query 'tasks[0].{status:lastStatus,stopCode:stopCode,stoppedReason:stoppedReason}'
```

## Practical Backend Scenario

A load test doubles ManifestFlow's traffic, and the service scales `desired count` from 2 to 6 —
but `running count` stalls at 3, with the other 3 tasks stuck `PENDING`. `describe-services`'
events array names the cause directly: "unable to place a task because no container instance met
all of its requirements" — the private-app subnet's available IP address pool is nearly exhausted
because `awsvpc` mode assigns each task its own ENI and IP, and the subnet was originally sized for
a handful of tasks, not the load test's burst. Separately, one of the 3 running tasks starts
cycling — `RUNNING` for eight seconds, then `STOPPING` — and the target group's health check
reveals why: a prior task definition change moved the container's listen port from 8080 to 8090,
but the target group was never updated to match, so the health check on port 8080 fails against a
container that is actually healthy and listening on 8090, and ECS treats a failed health check
identically to a genuinely broken container. The FDE fixes both problems independently — resizing
the private-app subnet's CIDR allocation (a change that requires care, since it affects every other
tenant of that subnet) to relieve the IP exhaustion, and updating the target group's health-check
port to 8090 to match the container's actual listen port — then re-runs the load test and confirms
`running count` reaches `desired count` with zero target-group churn this time.

## Practice Loop

1. Deploy the worker service behind an ALB with a target group whose health-check path and port
   deliberately do NOT match the container's actual listen port, and observe the resulting
   service-event churn without fixing it yet.
2. Read `describe-services`' events array and `describe-tasks`' `stoppedReason` to name the exact
   mismatch before consulting any documentation.
3. Fix the target-group health check to match the container's real port and path, redeploy, and
   confirm the service reaches steady state with zero unhealthy-target events.
4. Scale `desired count` well beyond what the subnet's available IPs can support, and read the
   resulting placement-failure event to distinguish it from the health-check failure in step 1.
5. Reconfigure the service's `minimumHealthyPercent`/`maximumPercent` to `100`/`200`, deploy a
   deliberately broken revision, and confirm the service never drops below its prior running
   capacity even though the new revision fails.

## Evidence of Understanding

You can diagnose a task stuck `PENDING` as a placement failure (capacity or subnet IP exhaustion)
distinct from a task cycling `RUNNING`→`STOPPING` as a health-check or startup failure, using the
service events array and `describe-tasks`' stop reason rather than guessing. You can configure a
target group's health check to genuinely match a container's listening contract, and explain the
specific silent-mismatch failure mode when the two disagree. You can set a conservative rolling
deployment configuration that bounds capacity loss during a bad rollout, and explain the trade-off
against the faster but riskier default.

## Suggested Extension

Add a CloudWatch alarm on the target group's `UnHealthyHostCount` metric with a short evaluation
period, and wire it to the same SNS topic the CloudWatch lesson's queue-backlog alarm already uses,
so a target-group health-check mismatch is caught by an automated alert within minutes rather than
discovered only when a load test happens to expose it.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What awsvpc mode gives each task
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does `awsvpc` networking mode give each ECS task that classic `bridge` mode does not, and why does that matter for security groups?

**OPTIONS:**
- [x] A: Its own ENI with its own private IP, which lets a security group attach directly to the task rather than only to the shared host it happens to land on
- [ ] B: Direct public internet access by default, regardless of the subnet's route table
- [ ] C: A permanent IP address that survives task replacement indefinitely
- [ ] D: Exemption from needing any target group health check

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this as the direct mechanical reason `awsvpc` matters for security — per-task ENI/IP lets a security group scope to that specific task, not to every task sharing a host.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [awsvpc, eni, security-group-scoping]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** PENDING versus STOPPING as distinct failure classes
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A task stuck `PENDING` indefinitely and a task cycling `RUNNING`→`STOPPING` are described as two different failure classes. What does each one indicate, and why does the distinction matter?

**OPTIONS:**
- [x] A: `PENDING` indicates a placement failure (no capacity or subnet IPs satisfy the task's requirements); `STOPPING` after briefly running indicates a health-check or startup failure — each points toward a completely different fix
- [ ] B: Both states indicate the exact same underlying failure and can be diagnosed identically
- [ ] C: `PENDING` always means the task definition itself is malformed JSON
- [ ] D: `STOPPING` always means the execution role lacks ECR pull permission

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson draws this exact distinction — placement failure versus health/startup failure — and states that the events array names which one occurred rather than requiring the FDE to guess.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [pending-task, stopping-task, failure-classification]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the service events output
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ aws ecs describe-services --cluster manifestflow --services manifestflow-worker \
  --query 'services[0].events[:5]'
[
  "service manifestflow-worker registered 0 targets in (target-group arn) due to unhealthy state",
  "service manifestflow-worker (port 8080) is unhealthy in target-group manifestflow-worker-tg due to (reason Health checks failed)",
  "service manifestflow-worker has started 2 tasks: task 8f1a... task 3c9b..."
]
```

**QUESTION_TEXT:**
Given this events output, what is the most likely root cause to investigate first?

**OPTIONS:**
- [x] A: A mismatch between the target group's configured health-check port/path and what the container actually serves, since tasks are starting but registering as unhealthy against the target group specifically
- [ ] B: The execution role is missing ECR pull permission
- [ ] C: The subnet has run out of available IP addresses for new ENIs
- [ ] D: The task definition references an image tag instead of a digest

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Tasks starting successfully but registering unhealthy against the target group specifically points at the health-check contract, exactly the scenario's port-mismatch diagnosis.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [service-events, target-group-health, diagnostic-reading]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Rolling deployment blast radius
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
aws ecs update-service --cluster manifestflow --service manifestflow-worker \
  --task-definition manifestflow-worker:16 \
  --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200"
```

**QUESTION_TEXT:**
With this deployment configuration, if revision `:16` is broken and never passes its health check, what happens to the currently running (old) tasks?

**OPTIONS:**
- [x] A: ECS starts new tasks alongside the old ones and only stops an old task once its replacement is confirmed healthy, so a broken new revision never drops capacity below what was already running
- [ ] B: ECS immediately stops all old tasks before starting any new ones, causing a capacity outage
- [ ] C: This configuration has no effect on deployment behavior; it only changes billing
- [ ] D: ECS stops exactly half the old tasks regardless of the configured percentages

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`minimumHealthyPercent=100` with `maximumPercent=200` is exactly the conservative configuration the lesson describes — new tasks are added alongside old ones, and old tasks are only stopped once a healthy replacement exists.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [minimum-healthy-percent, rolling-deployment, blast-radius]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** IP exhaustion under awsvpc mode
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
During the load test, `desired count` scales to 6 but `running count` stalls at 3, with tasks stuck `PENDING`. What is the root cause per the scenario, and what does fixing it actually require?

**OPTIONS:**
- [x] A: The private-app subnet's available IP pool is nearly exhausted because each task under `awsvpc` mode consumes one ENI/IP; fixing it requires resizing the subnet's CIDR allocation, a change that affects every other tenant of that subnet
- [ ] B: The target group's health check is misconfigured; fixing it only requires updating the health-check port
- [ ] C: The execution role lacks permission to launch new tasks; fixing it requires an IAM policy change
- [ ] D: The cluster has reached its maximum task-definition-revision limit

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The scenario's diagnosis is explicit — `awsvpc` mode's per-task ENI/IP consumption exhausted the subnet's IP pool, and the fix is a CIDR resize affecting other tenants, distinct from the target-group mismatch in the other stuck task.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [ip-exhaustion, awsvpc, subnet-sizing]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Two independent failures in the same scenario
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The scenario has two distinct problems occurring at once: IP exhaustion for some tasks and a port mismatch for another. Why is it important that the FDE diagnose and fix these as two independent issues rather than assuming one root cause explains both symptoms?

**OPTIONS:**
- [x] A: They are genuinely unrelated failure classes (placement capacity versus health-check contract) with different fixes, and conflating them risks either fix being applied to the wrong problem or one issue being missed entirely
- [ ] B: ECS requires all service failures to share a single root cause by design
- [ ] C: There is no actual distinction; both symptoms always resolve from the same CIDR resize
- [ ] D: The health-check port mismatch is caused by the IP exhaustion itself

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson treats these as the two failure classes from Q2 occurring simultaneously in one scenario, requiring independent diagnosis — the FDE fixes the subnet sizing and the target-group port as two separate corrections.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [independent-failures, root-cause-diagnosis]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Health check threshold configuration
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
aws elbv2 create-target-group --name manifestflow-worker-tg --protocol HTTP --port 8080 \
  --vpc-id vpc-0a1b2c3d4e5f60789 --target-type ip \
  --health-check-path /healthz --health-check-port 8080 \
  --healthy-threshold-count 2 --unhealthy-threshold-count 3 --health-check-interval-seconds 15
```

**QUESTION_TEXT:**
What must be true about the `worker` container definition for this target group's health check to succeed?

**OPTIONS:**
- [x] A: The container must actually listen on port 8080 and serve a successful response at `/healthz`
- [ ] B: The container must be launched with the EC2 launch type rather than Fargate
- [ ] C: The container must reference its image by tag rather than by digest
- [ ] D: The container's execution role must grant `elasticloadbalancing:DescribeTargetGroups`

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The target group's health check path and port must genuinely match what the container serves — this is the exact contract the lesson emphasizes, and getting it wrong is the recurring silent-mismatch failure this lesson demonstrates.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [target-group, health-check-path, health-check-port]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why bridge mode weakens security-group scoping
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson compares `awsvpc` mode's per-task ENI to a gap it echoes from the containerization elective's Docker networking lesson. What is that gap under classic `bridge` mode?

**OPTIONS:**
- [x] A: Tasks share the host's network namespace, so a security-group-equivalent exposure at the host level applies to every task on that host rather than being scoped to one task specifically
- [ ] B: `bridge` mode makes every task's traffic automatically encrypted, unlike `awsvpc`
- [ ] C: `bridge` mode is not supported at all by ECS and only exists in plain Docker
- [ ] D: `bridge` mode assigns each task a public IP by default, which `awsvpc` does not

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson draws this parallel explicitly — a shared network namespace under `bridge` mode means host-level exposure applies broadly, the same "any workload on this host inherits the host's exposure" gap the networking lesson raised for Docker.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [bridge-mode, shared-namespace, security-scoping]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Catching the health-check mismatch earlier
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The Suggested Extension proposes a CloudWatch alarm on `UnHealthyHostCount` with a short evaluation period. What does this catch that waiting for the next load test would not?

**OPTIONS:**
- [x] A: A target-group health-check mismatch introduced by a routine deployment, caught automatically within minutes rather than only being discovered when traffic happens to spike enough to expose it
- [ ] B: IP address exhaustion in the private-app subnet, which this metric measures directly
- [ ] C: Whether the execution role has ECR pull permission
- [ ] D: Nothing meaningfully different; a load test and this alarm catch identical failure classes

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The extension's value is proactive detection — an automated alarm catches a routine-deployment mismatch within minutes, rather than the failure only surfacing when a future load test happens to exercise it.
**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [cloudwatch-alarm, unhealthyhostcount, proactive-detection]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 10

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-10-eks-basics
lesson_title: "EKS Basics"
lesson_order: 10

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Create an EKS cluster and wire local kubectl access to it via `aws eks update-kubeconfig`, explaining what the generated kubeconfig entry actually authenticates."
  - "Explain the VPC CNI's one-ENI-per-pod-IP model and its specific exhaustion failure mode, distinct from ECS's equivalent awsvpc-mode exhaustion."
  - "Distinguish an EKS add-on's AWS-managed lifecycle from a Helm-installed chart's customer-managed lifecycle, and choose correctly between them for a given component."

created_date: "2026-09-01"
last_updated: "2026-09-01"
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
# EKS Basics

## Concepts Covered

Lighthouse Freight Co.'s platform team, separate from the FDE's ManifestFlow work, already runs
Kubernetes on-prem for their dispatch system and wants their next AWS workload on EKS rather than
ECS — they know Kubernetes primitives (Pods, Deployments, Services, RBAC) already, so this lesson
does not re-teach those; it covers what is genuinely different about running Kubernetes as an AWS
managed service rather than a self-hosted cluster. AWS operates the control plane's availability,
patching, and the `etcd` backing store; everything below that has historically been the customer's
responsibility — the worker nodes' AMI, the IAM role attached to them, and add-on version
compatibility across an upgrade — a boundary this module's core-curriculum sibling lesson already
covers in more depth. What that lesson doesn't demonstrate is the actual mechanics of standing a
cluster up and connecting to it: `eksctl create cluster` (or the equivalent Terraform module)
provisions the control plane and an initial managed node group in one operation, and `aws eks
update-kubeconfig` is what wires local `kubectl` access to it — this command does not create any
new AWS identity, it writes a kubeconfig entry that shells out to `aws eks get-token` at
connection time, meaning `kubectl`'s authentication is really "whatever IAM credentials are active
in your current AWS CLI session," mapped to a Kubernetes RBAC identity via the cluster's
`aws-auth` ConfigMap (or, in newer clusters, EKS's native access-entry API) — losing or rotating
those IAM credentials silently breaks `kubectl` access with no separate Kubernetes-level credential
to fall back on.

Pod networking is the other genuinely AWS-specific piece: the VPC CNI plugin assigns each pod a
real routable IP address from the VPC's own CIDR range — not an overlay network's separate address
space — by attaching secondary IP addresses to each node's ENIs (or, with prefix delegation
enabled, allocating a `/28` prefix per ENI slot instead of one IP at a time, dramatically raising
the pod-per-node ceiling). This is the direct EKS analog to the ECS/Fargate `awsvpc` IP-exhaustion
failure the previous lesson demonstrated at the task level: without prefix delegation, a node's
maximum pod count is capped by its instance type's ENI and IP-per-ENI limits, and a cluster that
scales pod count faster than it scales node count (or that uses undersized instance types) hits
this ceiling with pods stuck `Pending` and a scheduler event citing insufficient IP addresses,
diagnosed the same way the ECS IP-exhaustion failure was — by reading the actual scheduler/CNI
event rather than assuming it's a compute-capacity problem. Finally, an EKS **add-on** (the VPC
CNI itself, CoreDNS, `kube-proxy`, the EBS CSI driver) is lifecycle-managed by AWS through the EKS
API — `aws eks create-addon`, with AWS handling version compatibility and update orchestration —
which is a fundamentally different operational model from installing the same logical component
as a customer-managed Helm chart: an add-on's version and health are visible via `aws eks
describe-addon`, while a Helm-installed equivalent's lifecycle is entirely the customer's (or FDE's)
own responsibility to track, a distinction worth stating explicitly before assuming "installed via
`kubectl apply`" and "installed as an EKS add-on" are operationally interchangeable.

```bash
# Create the cluster and an initial managed node group in one operation
eksctl create cluster --name manifestflow-eks --region us-east-1 \
  --vpc-private-subnets subnet-0a1b2c3,subnet-0d4e5f6 \
  --nodegroup-name standard-workers --node-type m5.large \
  --nodes 2 --nodes-min 2 --nodes-max 5 --managed

# Wire local kubectl access -- this writes a kubeconfig entry, it creates no new IAM identity
aws eks update-kubeconfig --name manifestflow-eks --region us-east-1
kubectl get nodes
# -> NAME                          STATUS   ROLES    AGE   VERSION
#    ip-10-20-10-45.ec2.internal   Ready    <none>   4m    v1.29.3-eks-...

# Check who kubectl currently authenticates as -- it's your active AWS CLI identity, not a separate credential
aws sts get-caller-identity --query Arn
kubectl auth can-i get pods --as=arn:aws:iam::111122223333:role/manifestflow-eks-admin

# Confirm the VPC CNI add-on's AWS-managed version, and enable prefix delegation
aws eks describe-addon --cluster-name manifestflow-eks --addon-name vpc-cni \
  --query 'addon.{version:addonVersion,status:status}'
kubectl set env daemonset aws-node -n kube-system ENABLE_PREFIX_DELEGATION=true

# A pod stuck Pending due to IP exhaustion -- the scheduler event names the real cause
kubectl describe pod extraction-worker-7d9f8c-xk2p9 -n manifestflow | grep -A2 Events
# -> Warning  FailedScheduling  ...  0/2 nodes are available: 2 Too many pods (node has reached IP address capacity)
```

## Practical Backend Scenario

The platform team wants a second EKS cluster hosting a new extraction-worker deployment that
mirrors the ECS-based one, using the Kubernetes primitives they already know. The FDE creates the
cluster with `eksctl`, confirms `aws eks update-kubeconfig` grants `kubectl` access using the
same IAM role the FDE's AWS CLI session is already authenticated as, and deploys the worker. A
scale-up event pushes pod count on one `m5.large` node past what its ENI/IP allocation supports
under the default VPC CNI configuration, and new pods sit `Pending` — `kubectl describe pod`
surfaces "Too many pods (node has reached IP address capacity)" as the scheduling-failure reason,
the same category of diagnostic evidence ECS's placement-failure events gave for subnet IP
exhaustion, just surfaced through a different API. Rather than immediately reaching for larger
instance types (a cost-increasing fix that side-steps the actual constraint), the FDE enables
prefix delegation on the VPC CNI add-on, which raises the pod-per-node ceiling on the existing node
type without changing the instance size at all, and confirms via `aws eks describe-addon` that the
add-on's managed version supports the feature before enabling it. The platform team asks whether
they should also install the EBS CSI driver as a Helm chart, matching their on-prem convention; the
FDE recommends the EKS add-on instead specifically because its version compatibility with the
cluster's own Kubernetes version is then AWS's responsibility to track, not theirs.

## Practice Loop

1. Create an EKS cluster with `eksctl` and confirm `aws eks update-kubeconfig` wires `kubectl`
   access, then run `kubectl auth can-i` under two different assumed IAM roles to observe how
   authorization changes with the underlying AWS identity.
2. Deploy a workload and deliberately scale its pod count past what the node's default VPC CNI
   IP allocation supports, and read the exact scheduler event naming the cause.
3. Enable prefix delegation on the VPC CNI add-on and redeploy the same scaled workload, confirming
   the pod-per-node ceiling has genuinely increased without changing the node's instance type.
4. Compare `aws eks describe-addon` output for the VPC CNI against `helm list` output for a
   customer-managed chart, and write down which one AWS handles the version-compatibility lifecycle
   for and which one you would need to track yourself.
5. Simulate a lost or rotated IAM credential (assume a different role with no cluster access) and
   confirm `kubectl` access breaks immediately, with no separate Kubernetes-level credential to
   fall back on.

## Evidence of Understanding

You can explain that `aws eks update-kubeconfig` wires access to an existing IAM identity rather
than creating a new one, and that losing that IAM credential breaks `kubectl` access with no
separate fallback. You can diagnose a pod stuck `Pending` due to VPC CNI IP exhaustion from the
scheduler event, and fix it via prefix delegation rather than defaulting to a larger instance type.
You can state precisely which lifecycle (AWS-managed add-on versus customer-managed Helm chart) a
given cluster component follows, and choose the add-on path when you want AWS to own version
compatibility.

## Suggested Extension

Configure EKS access entries (the newer alternative to the `aws-auth` ConfigMap) to grant the
platform team's own IAM role `kubectl` access scoped to only the `manifestflow` namespace, and
compare how that authorization boundary is expressed differently than it would be for a Helm-based,
ConfigMap-driven cluster running outside AWS.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What update-kubeconfig actually does
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does `aws eks update-kubeconfig` actually do, per the lesson?

**OPTIONS:**
- [x] A: It writes a kubeconfig entry that shells out to `aws eks get-token` at connection time, wiring kubectl to whatever IAM credentials are active in the current AWS CLI session — it creates no new identity
- [ ] B: It creates a brand-new, separate Kubernetes-level credential independent of any AWS IAM identity
- [ ] C: It permanently grants cluster-admin to the IAM user who ran the command
- [ ] D: It has no effect on authentication; kubectl always uses an anonymous connection to EKS

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson is precise about this mechanism — the command writes a kubeconfig entry tied to the current AWS CLI session's IAM identity, not a separate credential, which is why losing that IAM access breaks kubectl too.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [update-kubeconfig, iam-authentication, kubectl-access]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** VPC CNI's pod IP model
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the VPC CNI assign pod IP addresses, and what does that imply about a pod's routability inside the VPC?

**OPTIONS:**
- [x] A: It assigns each pod a real, routable IP from the VPC's own CIDR range via secondary IPs (or prefix delegation) on each node's ENIs, rather than a separate overlay address space
- [ ] B: It assigns pods addresses from a private overlay network entirely separate from the VPC's own CIDR
- [ ] C: All pods on a node share one single IP address, distinguished only by port
- [ ] D: Pod IP addresses are assigned randomly from any AWS region's address pool, not the VPC's

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson is explicit that the VPC CNI gives pods real routable VPC-CIDR addresses via node ENIs, not a separate overlay space — the mechanical basis for the IP-exhaustion failure mode it then describes.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [vpc-cni, pod-ip, eni]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the scheduling failure event
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ kubectl describe pod extraction-worker-7d9f8c-xk2p9 -n manifestflow | grep -A2 Events
Warning  FailedScheduling  ...  0/2 nodes are available: 2 Too many pods (node has reached IP address capacity)
```

**QUESTION_TEXT:**
Given this event, what is the correct fix per the lesson, and what fix does the lesson explicitly caution against reaching for first?

**OPTIONS:**
- [x] A: Enable prefix delegation on the VPC CNI add-on to raise the pod-per-node IP ceiling on the existing node type; the lesson cautions against immediately switching to larger, more expensive instance types
- [ ] B: Increase the node's CPU request; the lesson cautions against touching the VPC CNI configuration at all
- [ ] C: Delete and recreate the cluster; the lesson cautions against any partial fix
- [ ] D: Add more nodes to the node group without changing any CNI configuration; the lesson cautions against prefix delegation as unsafe

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The scenario states this directly — the FDE enables prefix delegation rather than reaching for larger, cost-increasing instance types that side-step the actual IP-allocation constraint.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [prefix-delegation, ip-exhaustion-fix, scheduling-failure]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** EKS add-on versus Helm chart lifecycle
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The platform team asks whether to install the EBS CSI driver as a Helm chart, matching their on-prem convention. Why does the FDE recommend the EKS add-on instead?

**OPTIONS:**
- [x] A: An EKS add-on's version compatibility with the cluster's Kubernetes version is AWS's managed responsibility to track; a Helm-installed equivalent's lifecycle is entirely the customer's own responsibility
- [ ] B: Helm charts cannot be installed on EKS clusters at all; only add-ons are supported
- [ ] C: EKS add-ons are always free while Helm-installed components always incur additional cost
- [ ] D: There is no functional difference; the recommendation is purely about matching AWS's marketing preference

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this exact operational distinction — AWS tracks add-on version compatibility, while a Helm-installed equivalent leaves that lifecycle entirely to the customer or FDE.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [eks-addon, helm-chart, lifecycle-ownership]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** ECS IP exhaustion versus EKS IP exhaustion
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson calls EKS's pod IP exhaustion "the direct EKS analog" to the ECS `awsvpc` subnet IP exhaustion from the previous lesson. What is genuinely the same, and what is different?

**OPTIONS:**
- [x] A: Both stem from per-task/per-pod ENI-based IP consumption hitting a ceiling, diagnosed by reading a platform-specific scheduling event rather than assuming a generic compute-capacity problem; the difference is the ceiling itself — subnet-wide IP availability for ECS versus per-node ENI/IP allocation for EKS
- [ ] B: They are completely unrelated failure modes with no shared mechanism
- [ ] C: Both are fixed by the exact same command, `kubectl set env daemonset aws-node`
- [ ] D: ECS's version is caused by CoreDNS misconfiguration, while EKS's is caused by a target-group mismatch

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson draws this comparison precisely — same underlying ENI-based-IP-ceiling mechanism and same diagnostic discipline (read the actual event), different scope of the ceiling itself.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [ip-exhaustion, ecs-eks-comparison, diagnostic-discipline]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Prefix delegation's effect
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does enabling prefix delegation on the VPC CNI change, mechanically?

**OPTIONS:**
- [x] A: Instead of allocating one secondary IP at a time per ENI slot, it allocates a `/28` prefix per slot, dramatically raising the pod-per-node ceiling without changing the node's instance type
- [ ] B: It removes the pod-per-node IP ceiling entirely, with no upper bound
- [ ] C: It moves pod networking to an overlay network, bypassing the VPC CIDR entirely
- [ ] D: It changes which IAM role the VPC CNI add-on runs as

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson describes this mechanism precisely — a `/28` prefix per ENI slot instead of one IP at a time, raising the ceiling on the same node type rather than requiring a larger instance.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [prefix-delegation, vpc-cni, pod-density]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Control plane versus node responsibility
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what does AWS operate directly in EKS, and what has historically remained the customer/FDE's responsibility?

**OPTIONS:**
- [x] A: AWS operates the control plane's availability, patching, and the etcd backing store; the worker nodes' AMI, IAM role, and add-on version compatibility have historically been the customer's responsibility
- [ ] B: AWS operates every layer including the worker nodes' AMI by default in all configurations, with no customer responsibility remaining
- [ ] C: The customer operates the control plane; AWS only manages the worker nodes
- [ ] D: There is no meaningful division of responsibility in EKS; everything is jointly managed

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this boundary briefly, deferring depth to Module 4's dedicated lesson, but the basic split — control plane to AWS, node/AMI/IAM ownership historically to the customer — is stated directly.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [eks-control-plane, management-boundary]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Simulating lost IAM access
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Step 5 of the Practice Loop has you assume a different IAM role with no cluster access and confirm `kubectl` access breaks immediately. What does this exercise directly demonstrate?

**OPTIONS:**
- [x] A: That kubectl has no separate Kubernetes-level credential to fall back on — access is entirely a function of the currently active AWS IAM identity, mapped via aws-auth or access entries
- [ ] B: That EKS clusters maintain a permanent local credential cache independent of IAM, so access should not actually break
- [ ] C: That kubectl access is tied to the specific laptop the kubeconfig file was generated on, not to any IAM identity
- [ ] D: That losing IAM access only affects the AWS Console, never kubectl

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is exactly the point Q1 and the lesson's opening paragraph make — kubectl access is a live function of the current IAM identity, with no independent Kubernetes-level credential as a fallback.
**LESSON_CONNECTION:** Evidence of Understanding
**KEYWORDS:** [iam-dependency, kubeconfig, access-loss]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 11

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-11-eks-advanced
lesson_title: "EKS Advanced"
lesson_order: 11

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Hard
estimated_minutes: 120
content_status: Draft

learning_outcomes:
  - "Choose between a managed node group and a Fargate profile for a given workload based on genuine compute-ownership and scheduling constraints, not habit."
  - "Sequence a staged EKS cluster upgrade — control plane, then add-ons, then node groups — and explain why that specific order matters."
  - "Configure the AWS Load Balancer Controller to provision an ALB from a Kubernetes Ingress object, and trace the IAM identity that makes that provisioning possible."

created_date: "2026-09-01"
last_updated: "2026-09-01"
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
# EKS Advanced

## Concepts Covered

The platform team's EKS cluster now needs to host two genuinely different workload shapes: the
steady-state extraction-worker Deployment, and a bursty batch job that runs Lighthouse's monthly
customs-reconciliation report — a workload isolated on its own compute so a spike in report
processing never competes with the worker's steady-state capacity. A **managed node group** is
AWS-provisioned EC2 capacity behind an auto-scaling group, where you choose the instance type,
AMI, and scaling bounds, and AWS handles the node lifecycle mechanics (draining, replacing) around
whatever scaling policy you configure — the FDE still owns the node's actual sizing and patch
cadence, just not the raw EC2 orchestration. A **Fargate profile** is a different compute-ownership
model entirely: pods matching the profile's namespace/label selector run on AWS-managed, per-pod
isolated compute with no node to patch, size, or even see via `kubectl get nodes` in the
traditional sense — the trade-off is that Fargate pods cannot use `DaemonSet`s, cannot mount an EBS
volume directly, and carry a different (typically higher, though workload-dependent) per-pod cost
model than a well-utilized shared node group. Taints and tolerations are how a managed node group
achieves the same workload isolation Fargate gives for free: tainting the batch-job node group
`NoSchedule` and giving only the batch job's pod spec the matching toleration keeps the
extraction-worker Deployment off that capacity entirely, without needing a separate Fargate profile
for it.

Cluster upgrades in EKS have a specific required order, and getting it backwards produces failures
that look unrelated to the actual cause: the **control plane** must be upgraded first (`aws eks
update-cluster-version`), because a newer node kubelet talking to an older API server is a
supported (temporarily) configuration, while the reverse — an older control plane fielding requests
shaped for a newer node's kubelet — is not; **add-ons** come next, since the VPC CNI, CoreDNS, and
`kube-proxy` versions each have their own compatibility matrix against the now-upgraded control
plane; **managed node groups** come last, replaced via a rolling node replacement that drains and
reschedules pods onto new nodes running the upgraded kubelet — upgrading node groups before the
control plane risks a compatibility gap the platform silently tolerates today but is not guaranteed
to keep tolerating on a future version. Ingress in EKS is provided by the **AWS Load Balancer
Controller** (installed as a Helm chart, notably — not an EKS add-on, since it is a community
project rather than an AWS-first-party component), which watches Kubernetes `Ingress` objects and
translates them into an actual ALB, target groups, and listener rules — the controller itself needs
an IAM role (via IRSA or Pod Identity) with permission to call `elasticloadbalancing:*` and related
EC2 APIs on the cluster's behalf, which is the specific dependency that breaks silently if that
IAM role is ever narrowed without accounting for the controller's own needs.

```bash
# A Fargate profile isolating the batch-reconciliation namespace onto per-pod compute
cat > fargate-profile.yaml <<'EOF'
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: manifestflow-eks
  region: us-east-1
fargateProfiles:
  - name: batch-reconciliation
    selectors:
      - namespace: batch-reconciliation
EOF
eksctl create fargateprofile -f fargate-profile.yaml

# A tainted managed node group isolating the SAME batch workload via tolerations instead
eksctl create nodegroup --cluster manifestflow-eks --name batch-workers \
  --node-type c5.2xlarge --nodes 0 --nodes-min 0 --nodes-max 4 \
  --taints batch-only=true:NoSchedule --managed
```

```yaml
# Only this pod spec tolerates the batch-workers node group's taint
spec:
  tolerations:
    - key: "batch-only"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
  nodeSelector:
    eks.amazonaws.com/nodegroup: batch-workers
```

```bash
# Staged upgrade sequence: control plane, then add-ons, then node groups -- in that order
aws eks update-cluster-version --name manifestflow-eks --kubernetes-version 1.30
aws eks wait cluster-active --name manifestflow-eks

aws eks update-addon --cluster-name manifestflow-eks --addon-name vpc-cni --addon-version v1.18.1-eksbuild.1
aws eks update-addon --cluster-name manifestflow-eks --addon-name coredns --addon-version v1.11.1-eksbuild.9
aws eks update-addon --cluster-name manifestflow-eks --addon-name kube-proxy --addon-version v1.30.0-eksbuild.3

eksctl upgrade nodegroup --cluster manifestflow-eks --name standard-workers --kubernetes-version 1.30
```

```yaml
# Kubernetes Ingress translated into an ALB by the AWS Load Balancer Controller
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: manifestflow-portal
  namespace: manifestflow
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  rules:
    - host: portal.manifestflow.lighthousefreight.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: manifestflow-portal-svc
                port:
                  number: 80
```

## Practical Backend Scenario

The FDE isolates the monthly reconciliation batch job on a Fargate profile scoped to its own
`batch-reconciliation` namespace, since the job runs for a few hours once a month and per-pod
Fargate billing beats paying for idle node-group capacity the rest of the time; the steady-state
extraction worker stays on the managed node group, since it needs `DaemonSet`-based log forwarding
Fargate does not support. A planned cluster upgrade from 1.29 to 1.30 goes through the staged
sequence — control plane first, then the three core add-ons, then a rolling node-group
replacement — and the FDE deliberately does not skip the add-on stage even though the cluster
appears to function immediately after the control-plane upgrade alone, because the VPC CNI's
compatibility matrix for 1.30 is not guaranteed by an untested older version, even one that has not
yet visibly broken. Separately, the platform team wants a customer-facing portal exposed via
Ingress; the FDE installs the AWS Load Balancer Controller via Helm, configures its IRSA role with
the exact `elasticloadbalancing` and EC2 permissions AWS's own IAM policy document specifies (no
more), and applies the Ingress manifest above — the controller reconciles it into a real ALB within
about ninety seconds, confirmed by describing the Ingress object and reading its assigned address.
When a well-intentioned security tightening pass later narrows the IRSA role's policy without
checking against the controller's documented requirements, new Ingress objects silently stop
provisioning ALBs, and the controller's own pod logs — not the Ingress object's events — are where
the FDE finds the actual `AccessDenied` error.

## Practice Loop

1. Create both a Fargate profile and a tainted managed node group targeting two different
   namespaces, deploy a workload to each, and confirm via `kubectl get pods -o wide` that each
   landed on the compute you intended.
2. Attempt to run a `DaemonSet` on the Fargate-profile namespace and observe the specific failure,
   confirming the trade-off the lesson names rather than taking it on faith.
3. Perform the staged upgrade sequence against a test cluster, and note what (if anything) already
   appears to work correctly after only the control-plane stage, before running the add-on stage.
4. Install the AWS Load Balancer Controller via Helm with an IRSA role scoped to its documented
   IAM policy, apply the Ingress manifest above, and confirm an ALB is provisioned by describing
   the Ingress object's assigned address.
5. Deliberately narrow the controller's IRSA role by removing one required permission, apply a new
   Ingress object, and find the resulting `AccessDenied` error in the controller's own pod logs
   rather than the Ingress object's Kubernetes events.

## Evidence of Understanding

You can choose between a managed node group and a Fargate profile for a given workload based on
its actual constraints — `DaemonSet` and EBS needs, cost shape, isolation requirement — not by
default habit. You can sequence a cluster upgrade correctly (control plane, add-ons, node groups)
and explain why upgrading out of order risks a compatibility gap even when nothing visibly breaks
immediately. You can trace an Ingress object through the AWS Load Balancer Controller to the actual
IAM identity that makes ALB provisioning possible, and diagnose a silent provisioning failure to
the controller's own logs rather than the Ingress object's events.

## Suggested Extension

Add a Kubernetes `PodDisruptionBudget` to the extraction-worker Deployment before the next node-group
upgrade rehearsal, and confirm the rolling node replacement respects it — reschedule pods only as
fast as the budget allows rather than draining nodes at a pace that could otherwise drop the
worker's available replica count during the upgrade window.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Fargate profile versus managed node group
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the essential compute-ownership difference between a Fargate profile and a managed node group?

**OPTIONS:**
- [x] A: A Fargate profile runs matching pods on AWS-managed, per-pod isolated compute with no node to patch or size; a managed node group is AWS-provisioned EC2 capacity where you still choose instance type, AMI, and scaling bounds
- [ ] B: Both are functionally identical; the only difference is naming convention
- [ ] C: A managed node group runs pods on per-pod isolated compute, while Fargate requires you to choose an instance type
- [ ] D: A Fargate profile requires manually patching each pod's underlying host OS

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson draws this exact ownership distinction — Fargate's per-pod AWS-managed compute versus a managed node group's customer-sized, customer-patched EC2 capacity.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [fargate-profile, managed-node-group, compute-ownership]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Fargate's specific trade-offs
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson name as a limitation of Fargate pods compared to pods on a managed node group?

**OPTIONS:**
- [x] A: Fargate pods cannot use DaemonSets and cannot mount an EBS volume directly
- [ ] B: Fargate pods cannot make outbound network calls of any kind
- [ ] C: Fargate pods cannot be scheduled with any resource requests or limits
- [ ] D: Fargate pods are always billed at a lower rate than an equivalent node-group pod in every case

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this exact limitation and uses it directly in the scenario — the worker stays on the node group specifically because it needs DaemonSet-based log forwarding that Fargate does not support.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [fargate-limitations, daemonset, ebs-volume]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why the upgrade order matters
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why must the control plane be upgraded before the node groups, per the lesson, rather than the reverse order?

**OPTIONS:**
- [x] A: A newer node kubelet talking to an older API server is a temporarily supported configuration, while an older control plane fielding requests shaped for a newer node's kubelet is not
- [ ] B: AWS bills node-group upgrades at a higher rate if performed before the control plane
- [ ] C: The order has no functional consequence; it is a stylistic convention only
- [ ] D: Add-ons must always be upgraded before the control plane, and node groups have no ordering constraint relative to either

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this asymmetry directly — newer-node/older-control-plane is a supported transitional state, the reverse is not, which is the mechanical reason the control plane goes first.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [upgrade-order, control-plane-first, kubelet-compatibility]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why not skip the add-on stage
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The scenario has the FDE run the add-on upgrade stage even though the cluster "appears to function immediately after the control-plane upgrade alone." Why not skip straight to node groups once things look fine?

**OPTIONS:**
- [x] A: The add-ons' compatibility with the newly upgraded control plane is not guaranteed by an untested older version, even one that has not yet visibly broken — apparent function is not the same as a verified compatibility guarantee
- [ ] B: Skipping the add-on stage is technically impossible; the EKS API blocks any node-group upgrade until add-ons are upgraded first
- [ ] C: The add-on stage is purely cosmetic and has no bearing on cluster stability either way
- [ ] D: Add-ons must be upgraded only after node groups, making the described order actually backwards

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The scenario states this reasoning explicitly — not skipping a stage just because things look fine, since compatibility is a guarantee, not an observation.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [add-on-upgrade, compatibility-matrix, upgrade-discipline]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Reading the tainted node group and toleration
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
eksctl create nodegroup --cluster manifestflow-eks --name batch-workers \
  --node-type c5.2xlarge --nodes 0 --nodes-min 0 --nodes-max 4 \
  --taints batch-only=true:NoSchedule --managed
```
```yaml
spec:
  tolerations:
    - key: "batch-only"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
```

**QUESTION_TEXT:**
What does this taint-and-toleration pair achieve for the batch-reconciliation workload, if it were run on this node group instead of a Fargate profile?

**OPTIONS:**
- [x] A: Only pods carrying the matching toleration can be scheduled onto the tainted node group, keeping the extraction-worker Deployment (which lacks that toleration) off that capacity entirely
- [ ] B: It grants the batch job's pods elevated IAM permissions automatically
- [ ] C: It guarantees the node group scales to zero whenever the batch job is idle, with no other configuration required
- [ ] D: It has no scheduling effect; taints only affect networking, not pod placement

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this exact use — taints/tolerations achieve the same workload isolation Fargate gives by default, without needing a separate Fargate profile.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [taints, tolerations, workload-isolation]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the AWS Load Balancer Controller is a Helm chart, not an add-on
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why is the AWS Load Balancer Controller installed via Helm rather than as an EKS add-on?

**OPTIONS:**
- [x] A: It is a community project rather than an AWS first-party component, which is the same lifecycle distinction the EKS Basics lesson drew between AWS-managed add-ons and customer-managed Helm charts
- [ ] B: EKS add-ons cannot provision any AWS resource outside the cluster, and the controller needs to create ALBs
- [ ] C: Helm charts install faster than EKS add-ons in every case, which is the only reason for the choice
- [ ] D: The AWS Load Balancer Controller does not require any IAM permissions, unlike EKS add-ons

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson calls this out explicitly, connecting back to the previous lesson's add-on-versus-Helm distinction — the controller is a community project, hence Helm-installed rather than an AWS-managed add-on.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [aws-load-balancer-controller, helm-vs-addon]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Diagnosing the silent Ingress provisioning failure
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
After the IRSA role's policy is narrowed without checking the controller's documented requirements, new Ingress objects silently stop provisioning ALBs. Where does the FDE actually find the root-cause error, and why not the Ingress object's own events?

**OPTIONS:**
- [x] A: In the AWS Load Balancer Controller's own pod logs, since the controller — not the Ingress object itself — is what calls the ALB-provisioning API and receives the AccessDenied error from AWS
- [ ] B: In the Ingress object's Kubernetes events, since Kubernetes always surfaces IAM-level API errors directly on the object that triggered them
- [ ] C: In the EKS control plane's own audit log exclusively, with no other location containing this error
- [ ] D: The error cannot be found in logs at all; only a support ticket to AWS reveals it

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The scenario states this directly — the controller's own pod logs, not the Ingress object's events, are where the actual AccessDenied error surfaces, because the controller is the actor making the AWS API call.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [irsa, accessdenied, controller-logs]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Reading the Ingress manifest's annotations
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```yaml
metadata:
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
```

**QUESTION_TEXT:**
What do these annotations tell the AWS Load Balancer Controller to do?

**OPTIONS:**
- [x] A: Handle this Ingress object (via the `alb` ingress class), provision a publicly reachable ALB rather than an internal one, and register pod IPs directly as ALB targets rather than routing through node ports
- [ ] B: Deploy this workload onto a Fargate profile automatically
- [ ] C: Enable IRSA for every pod matched by this Ingress object
- [ ] D: Restrict this Ingress to only the `manifestflow` namespace's internal traffic

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Each annotation maps to exactly one of these controller behaviors — ingress class selection, public scheme, and IP target-type registration — which the controller translates into real ALB configuration.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [ingress-annotations, alb-controller, target-type]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Respecting a PodDisruptionBudget during upgrade
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The Suggested Extension adds a `PodDisruptionBudget` to the extraction-worker Deployment before the next node-group upgrade rehearsal. What problem does this specifically prevent during the rolling node replacement?

**OPTIONS:**
- [x] A: Nodes draining faster than the budget allows could otherwise drop the worker's available replica count below an acceptable threshold during the upgrade window
- [ ] B: It prevents the control plane from being upgraded before the node groups
- [ ] C: It prevents the AWS Load Balancer Controller from provisioning a new ALB during the upgrade
- [ ] D: It has no functional effect during a node-group upgrade; it only applies to Fargate profiles


