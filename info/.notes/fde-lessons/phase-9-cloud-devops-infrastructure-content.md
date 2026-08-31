# FDE Phase 9 — Module 4: Cloud, DevOps, Kubernetes & Infrastructure (Lessons 1-6 of 12)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-9-cloud-devops-infrastructure-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `cloud-devops-infrastructure` ("4. Cloud, DevOps, Kubernetes & Infrastructure")

This is the first half of the module (lessons 1-6 of 12). A later Phase 10 will cover lessons
7-12 (CI/CD & GitOps, Terraform, Serverless, SRE, and an assessment) and complete the module.

---

# LESSON 1

```yaml
lesson_id: cloud-devops-infrastructure-01-aws-core-iam-vpc-and-networking
lesson_title: "AWS Core: IAM, VPC & Networking"
lesson_order: 1

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Design IAM policies around least privilege — explicit actions, explicit resource ARNs, explicit conditions — instead of an admin key used for convenience."
  - "Distinguish a trust policy (who may assume a role) from a permission policy (what the assumed role may do) from a permission boundary (the maximum either can ever grant)."
  - "Design a VPC's subnet, security-group, and endpoint layout to match a workload's actual reachability needs rather than defaulting to a flat, permissive network."

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
# AWS Core: IAM, VPC & Networking

## Concepts Covered

An IAM policy is a JSON document with four load-bearing parts: `Effect` (Allow or Deny), `Action` (which API calls), `Resource` (which specific things those calls apply to), and an optional `Condition` (further narrowing, such as source IP or a required tag). Least privilege means scoping both `Action` and `Resource` deliberately — `"s3:GetObject"` on `arn:aws:s3:::customer-uploads/orders/*`, not `"s3:*"` on `"*"` — because a wildcard action on a wildcard resource is not a shortcut to the same outcome with fewer keystrokes, it is a fundamentally different, much larger blast radius that happens to satisfy the same demo. This is the same privilege-separation discipline from the AI-safety lesson's tool-scoping argument and the shell-scripting lesson's warning against reaching for `chmod 777` to make a permission error disappear — in every case, the fix that actually works is naming the minimum surface a task needs, not the maximum surface that would make every future task convenient too. A long-lived IAM user access key embedded in an application is the AWS-specific version of the same anti-pattern: it doesn't expire on its own, it's easy to leak into a log line or a config file committed by accident, and it grants whatever that user's policy allows for as long as the key exists, with no automatic connection to whether the workload using it is still running. An IAM role, assumed by a workload (an EC2 instance, an ECS task, a Lambda function) via short-lived, automatically-rotated credentials, is the correct default specifically because the credential's lifetime is tied to the workload's actual lifetime.

Three distinct policy concepts get conflated by engineers new to AWS, and keeping them separate is what makes an access design explainable under review. A **trust policy** (attached to the role itself) answers "who is allowed to assume this role" — for a role an EC2 instance profile uses, the trust policy's principal is the EC2 service (`ec2.amazonaws.com`), not a person; for a role a customer's CI pipeline assumes via federation, the principal is that identity provider. A **permission policy** (attached to the role, or to a user or group) answers "once assumed, what can this identity actually do" — the `Action`/`Resource`/`Condition` scoping described above. A **permission boundary** is a separate, optional policy that caps the maximum permissions an identity can ever have, regardless of what its permission policies say — the effective permission is always the intersection of the permission policy and the boundary, never their union. Boundaries exist specifically to let an FDE safely delegate role-creation to someone else on a customer's team: without one, anyone holding `iam:CreateRole` and `iam:AttachRolePolicy` can create a new role with `AdministratorAccess` and hand it to themselves, a privilege-escalation path that a boundary closes by guaranteeing no role created under it can ever exceed the boundary's own ceiling, no matter what permission policy gets attached later. Service Control Policies (SCPs), applied at the AWS Organizations level, add a third layer above both — an account-wide guardrail (for example, "no principal in this account may ever disable CloudTrail") that no IAM policy inside the account can override, useful specifically because an FDE working inside a customer's account should not be the only thing standing between a mistake and an unrecoverable one.

VPC networking applies the same least-reachability logic to the network layer instead of the API layer. A typical layout splits subnets into public (with a route to an internet gateway, holding only what genuinely needs a public IP — a load balancer, a NAT gateway) and private (no direct internet route, holding the actual application and database). Security groups are stateful and allow-only — attached to specific resources (an EC2 instance, an RDS instance), they permit specified inbound and outbound traffic and automatically allow the corresponding return traffic, and the common, correct pattern is chaining them by reference rather than by IP range: an application's security group allows inbound on its port only from the load balancer's security group, not from a CIDR block, so the rule stays correct even as instances are replaced. Network ACLs, by contrast, are stateless and operate at the subnet boundary, evaluated in numbered order, and can express explicit `Deny` rules that security groups cannot — useful as a coarse, subnet-wide backstop, but security groups do most of the real access-control work in practice because they're resource-scoped and easier to reason about per-workload. VPC endpoints let a private resource call specific AWS APIs (S3, Secrets Manager, and others) without ever routing through the public internet or a NAT gateway — for a workload in a private subnet that needs no other public egress, this closes an entire class of exfiltration path that would otherwise exist purely because a NAT gateway was provisioned for one narrow need and left as a general-purpose exit route.

## Practical Backend Scenario

An FDE is deploying the order-management FastAPI service from Module 2 into a new customer's AWS account. The fastest path to a working demo is an IAM user with `AdministratorAccess` and a long-lived access key pasted into the deployment's environment variables — it works immediately, and that's exactly the problem: it works for every possible action on every possible resource, on a credential that never rotates and that a leaked log line would hand to anyone. The FDE replaces it with an EC2 instance role whose trust policy allows only the EC2 service to assume it, and whose permission policy grants exactly three things: `s3:GetObject` on the specific `customer-uploads/orders/*` prefix the service reads attachments from, `secretsmanager:GetSecretValue` on the one named ARN holding the database connection string, and nothing else — no `s3:*`, no access to any other customer's bucket, no IAM permissions to modify its own role. The instance itself sits in a private subnet, reachable only from the load-balancer's security group on the application's port, with no direct route to the public internet; the one AWS API call it needs outside its VPC endpoints for S3 and Secrets Manager goes through those endpoints instead of a NAT gateway, so the private subnet has no general-purpose path out to the internet at all. When a customer security reviewer later asks "what could this service actually do if compromised," the answer is a short, specific list instead of "everything," which is the entire point of having gone through this exercise instead of shipping the admin key.

## Practice Loop

1. Write the over-broad starting policy (`"Action": "s3:*"`, `"Resource": "*"`) for the order-management service's S3 access, then rewrite it scoped to exactly the actions (`GetObject`, `PutObject`) and the exact bucket prefix the service actually touches.
2. Write out, in plain terms, the trust policy and the permission policy for an EC2 instance role separately, and state in one sentence what each one controls that the other does not.
3. Design a permission boundary for a hypothetical customer teammate who needs to create IAM roles for their own workloads, and demonstrate — by writing out the intersection — that a role created under your boundary with an attached `AdministratorAccess` policy still cannot exceed the boundary's actual ceiling.
4. Design the VPC layout for the order-management service: which subnet the load balancer sits in, which subnet the application sits in, and the exact security-group rule (by reference, not CIDR) that permits traffic between them and nothing else.
5. List every AWS API call the deployed service actually needs to make, and for each one, decide whether it should route through a VPC endpoint or genuinely needs internet egress — count how many of them turn out to need a NAT gateway at all.

## Evidence of Understanding

You can write an IAM policy scoped to specific actions and specific resource ARNs instead of reaching for a wildcard, and explain in concrete terms what blast radius the wildcard version would have added. You can distinguish a trust policy, a permission policy, and a permission boundary by what each one actually controls, and explain why a permission boundary is what makes delegated role-creation safe. You can design a VPC's subnet split, security-group rules, and endpoint usage to match a specific workload's actual reachability needs, and can state, for any given resource in that design, exactly what could reach it and from where.

## Suggested Extension

Add a Service Control Policy at the AWS Organizations level that denies disabling CloudTrail from any principal in the account, including an account administrator — and explain why this guardrail belongs above IAM entirely rather than as just another IAM policy an administrator could edit or remove.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why a wildcard action/resource policy is a different design, not a shortcut
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that `"Action": "s3:*"` on `"Resource": "*"` is not simply a faster way to reach the same outcome as a scoped policy?

**OPTIONS:**
- [x] A: It grants a fundamentally larger blast radius — every S3 action on every bucket — that happens to also satisfy the narrow task, rather than being equivalent in effect to a properly scoped policy
- [ ] B: AWS technically evaluates wildcard policies more slowly, making them a performance concern rather than a security one
- [ ] C: Wildcard policies and scoped policies always produce identical effective permissions in practice
- [ ] D: This concern only applies to S3 specifically and not to other AWS services

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The risk isn't stylistic — a wildcard action/resource combination is a categorically larger grant of access than the task requires, and that gap is exactly the surface a compromised credential or a mistaken caller could exploit.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [least-privilege, wildcard-policy-risk]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why an IAM role beats a long-lived access key for a workload
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why is an IAM role assumed by a workload preferred over a long-lived IAM user access key embedded in that workload's configuration?

**OPTIONS:**
- [x] A: A role's credentials are short-lived and automatically rotated, tied to the workload's actual runtime, whereas a long-lived key never expires on its own and grants the same access whether or not the workload is even still running
- [ ] B: IAM roles are technically incapable of being over-permissioned, unlike IAM user keys
- [ ] C: There is no meaningful security difference; the choice is purely about which is more convenient to configure
- [ ] D: Long-lived access keys are required for any workload that needs to call more than one AWS service
- [ ] E: Roles are only relevant for Lambda functions and do not apply to EC2 or ECS

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The credential-lifetime mismatch is the actual risk — a leaked long-lived key remains valid indefinitely and independent of whether the workload it was meant for still exists, while a role's short-lived credentials expire and rotate automatically.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [iam-role-vs-key, credential-lifetime]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Trust policy versus permission policy
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the difference between a role's trust policy and its permission policy?

**OPTIONS:**
- [x] A: The trust policy controls who or what is allowed to assume the role; the permission policy controls what the role can actually do once assumed
- [ ] B: They are two names for the same policy document with no functional distinction
- [ ] C: The permission policy controls who can assume the role; the trust policy controls what actions are allowed
- [ ] D: Trust policies apply only to IAM users, and permission policies apply only to IAM roles

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the core distinction the lesson insists on keeping separate — "who may assume this" versus "what may the assumed identity do" are different questions answered by different policy documents.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [trust-policy, permission-policy]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What a permission boundary actually guarantees
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A role is created with a permission boundary attached, and later a permission policy granting `AdministratorAccess` is attached to that same role. What is the role's effective, actual permission?

**OPTIONS:**
- [x] A: The intersection of the permission policy and the boundary — the role cannot exceed whatever ceiling the boundary defines, no matter how broad the attached permission policy is
- [ ] B: Full AdministratorAccess, since the most recently attached policy always takes precedence over the boundary
- [ ] C: The union of the permission policy and the boundary, granting the combined total of both
- [ ] D: No permissions at all, since attaching AdministratorAccess to a bounded role always results in an error
- [ ] E: The boundary is disabled automatically whenever a broader permission policy is attached

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is exactly the privilege-escalation path a permission boundary is designed to close — the effective permission is always the intersection, so attaching a broad permission policy on top of a boundary cannot exceed the boundary's own ceiling.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [permission-boundary, privilege-escalation-prevention]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why SCPs sit above IAM policies
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson describe a Service Control Policy denying CloudTrail from ever being disabled as sitting "above" IAM entirely, rather than as just another IAM policy?

**OPTIONS:**
- [x] A: An SCP is an account-wide guardrail that no IAM policy inside the account — including an administrator's — can override, which matters specifically because an FDE working in a customer's account shouldn't be the only thing preventing an unrecoverable mistake
- [ ] B: SCPs and IAM policies use identical syntax and enforcement, making the distinction purely organizational
- [ ] C: SCPs can only be applied to S3 buckets and have no relevance to CloudTrail or account-wide settings
- [ ] D: An IAM administrator can always override an SCP by editing their own permission policy

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The whole value of an SCP is that it isn't just another editable IAM policy — it's an organization-level ceiling that holds even against an account administrator, which is the guardrail property the lesson highlights.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [service-control-policy, account-wide-guardrail]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why security groups reference each other instead of CIDR blocks
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend an application's security group allow inbound traffic by referencing the load balancer's security group, rather than by allowing a specific CIDR range?

**OPTIONS:**
- [x] A: A reference-based rule stays correct automatically as instances behind the load balancer are replaced, whereas a CIDR-based rule would need to be manually updated whenever the underlying IP ranges change
- [ ] B: AWS security groups technically do not support CIDR-based rules at all
- [ ] C: CIDR-based rules are always more permissive than reference-based rules regardless of configuration
- [ ] D: Referencing another security group removes the need for the rule to specify a port

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The reference-based pattern is specifically about staying correct under change — resources get replaced and IPs shift, but a security-group reference keeps tracking the right source without manual upkeep.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [security-group-reference, network-design]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What a VPC endpoint closes off
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why does routing S3 and Secrets Manager calls through VPC endpoints instead of a NAT gateway matter for the private subnet's security posture?

**OPTIONS:**
- [x] A: It means the private subnet has no general-purpose route to the public internet at all, closing off an entire exfiltration path that would otherwise exist purely because a NAT gateway had been provisioned
- [ ] B: VPC endpoints are required by AWS before any private subnet can make any AWS API call whatsoever
- [ ] C: NAT gateways are technically incapable of routing traffic to S3 or Secrets Manager
- [ ] D: This choice has no security implication and is purely a cost optimization

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The security payoff is specific — without a NAT gateway at all, there's no general internet egress path to worry about, not just a cheaper way to reach the same two AWS services.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [vpc-endpoint, egress-elimination]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Connecting IAM least privilege to the AI-safety lesson
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson connect scoping an IAM policy's actions and resources to the earlier AI-safety lesson's privilege-separation argument?

**OPTIONS:**
- [x] A: Both describe the same discipline in different domains — a tool or credential should be scoped to the minimum surface a specific task needs, not the maximum surface that would make every future task convenient, whether that's a triage agent's tool permissions or an IAM policy's actions and resources
- [ ] B: The two lessons describe entirely unrelated concerns with no shared underlying principle
- [ ] C: This connection only holds if the IAM policy in question is attached to an AI agent's own workload
- [ ] D: IAM least privilege replaces the need for the AI-safety lesson's privilege-separation defenses entirely

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a deliberate cross-module echo — minimum-necessary-scope reasoning reappears here applied to cloud credentials instead of an agent's tool-calling permissions, but it's the same judgment call.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [ai-safety-connection, privilege-separation-reuse]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What the security reviewer's question actually tests
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the scenario end on the question "what could this service actually do if compromised" rather than "does this service have the access it needs to function"?

**OPTIONS:**
- [x] A: A design is only actually least-privilege if the answer to "what could go wrong" is a short, specific, bounded list — a service having enough access to function says nothing about whether it also has far more access than that, which is the real risk the whole exercise is meant to close
- [ ] B: These two questions are functionally identical and always produce the same answer for any IAM design
- [ ] C: The compromise question only matters for services that handle payment data specifically
- [ ] D: A service having sufficient access to function is sufficient proof that its permissions are properly scoped
- [ ] E: This question is only relevant during an actual security incident, not during initial design

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
"Does it have enough access" only verifies the lower bound; "what could it do if compromised" is what actually verifies the upper bound has been controlled — and least privilege is fundamentally a claim about the upper bound.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [blast-radius-evaluation, upper-bound-vs-lower-bound]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 2

```yaml
lesson_id: cloud-devops-infrastructure-02-compute-storage-and-managed-services-ec2-s3-rds-sqs
lesson_title: "Compute, Storage & Managed Services (EC2, S3, RDS, SQS)"
lesson_order: 2

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Choose RDS versus self-managed Postgres by the actual operational trade-off (patching, backups, failover) rather than by default or by cost alone."
  - "Explain S3's durability and consistency model precisely enough to reason about what it does and does not protect against."
  - "Design an SQS-backed queue (visibility timeout, dead-letter queue) that tolerates at-least-once delivery instead of assuming exactly-once."

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
# Compute, Storage & Managed Services (EC2, S3, RDS, SQS)

## Concepts Covered

EC2 gives you a virtual machine and, with it, full responsibility for everything above the hypervisor: choosing and patching the AMI, managing the instance's local (ephemeral, lost on stop/terminate unless it's a separate EBS-backed root or attached volume) versus durable storage, and — unless you also stand up an Auto Scaling group with a launch template and health checks — no automatic replacement if the instance or the process on it dies. This is the right tool when a workload genuinely needs OS-level control an AWS-managed service doesn't expose, but it is not a neutral, "closer to the metal, therefore safer" default — every operational concern a managed service would have absorbed (patch cadence, backup scheduling, failover orchestration) becomes something the FDE, or the customer's team after handoff, now owns indefinitely. RDS is the managed alternative for relational data specifically: automated backups with point-in-time recovery, Multi-AZ deployment that maintains a synchronously-replicated standby and fails over automatically on primary failure, and OS/engine patching handled on a schedule the customer chooses rather than a task someone has to remember. The real trade-off, worth stating precisely rather than gesturing at "less control": you give up direct filesystem and OS access to the database host, and some engine-level extensions or tuning knobs available on a self-managed instance aren't exposed. For the overwhelming majority of customer engagements this course prepares an FDE for, that's the correct trade to make — the customer's team is not going to want to have inherited hand-rolled Postgres failover scripts after the FDE moves on to the next engagement, and RDS's managed failover is exactly the kind of operational burden an FDE should be actively avoiding leaving behind. Self-managed Postgres on EC2 earns its place only when a specific, named requirement RDS doesn't support forces it — a particular extension, a specific replication topology, or genuinely extreme cost optimization at a scale where the operational overhead is justified by dedicated staff who will actually own it.

S3 stores objects (not a filesystem — there's no in-place partial-file edit, only whole-object PUT and GET) with eleven-nines durability, achieved by replicating each object across multiple facilities within a region automatically, and strong read-after-write consistency for both new object PUTs and overwrites of existing objects — a `GET` immediately following a successful `PUT` is guaranteed to return the new data, not a stale or missing result, which was not always true of S3's original consistency model and is worth stating precisely because "eventually consistent" is still a common but outdated assumption about S3 that leads to unnecessary defensive retry logic. Durability and consistency are not the same guarantee as availability or correctness under application-level misuse, though: an object can be technically durable and immediately consistent while still being world-readable because a bucket policy or an object ACL was left too permissive, which is an access-control failure, not a storage-durability one — the two failure modes get diagnosed differently and confusing them wastes time during an incident. Storage classes (Standard, Infrequent Access, Glacier and its variants) trade retrieval latency and per-request cost against per-GB storage cost, and presigned URLs let a backend grant a client temporary, scoped access to a specific object without the client ever holding real AWS credentials — the same "scoped, time-limited access instead of a standing credential" pattern IAM roles use, reapplied at the object level.

SQS decouples a producer from a consumer by holding messages in a durable queue between them, and its delivery guarantee is explicitly at-least-once, not exactly-once — a message can be delivered more than once, which is the identical hazard the Stripe webhook lesson covered for inbound events, now showing up as an AWS primitive instead of a third-party integration, and it means a consumer processing SQS messages needs the same idempotency discipline (checking whether a given message's underlying operation has already been applied before reapplying it) rather than assuming delivery count and processing count are the same number. The visibility timeout is the mechanism that makes this concrete: when a consumer receives a message, SQS hides it from other consumers for a configured duration rather than deleting it immediately, and the consumer must explicitly delete the message after successfully finishing its work — if that duration is shorter than the consumer's actual processing time, the message becomes visible again and a second consumer picks it up before the first one finishes, producing exactly the duplicate-processing scenario idempotency is meant to guard against; setting the visibility timeout comfortably longer than the slowest realistic processing time, not the average case, is the concrete fix. A dead-letter queue (DLQ), configured with a maximum-receive-count threshold, catches a message that has failed processing repeatedly and routes it out of the main queue instead of letting it retry forever and block queue throughput — the DLQ becomes the place an operator looks for messages that are structurally broken (a malformed payload, a poison message) rather than transiently failing, which is a diagnostic signal in its own right.

## Practical Backend Scenario

An FDE deploys the Module 2 order-management and payments system into a customer's AWS account. Order and payment data goes into RDS for PostgreSQL, configured Multi-AZ, so a primary-instance failure triggers automatic failover to the synchronously-replicated standby without the FDE writing or maintaining any custom failover script. Customer-uploaded order attachments (receipts, delivery-proof photos) go into S3, with presigned URLs generated server-side so the customer's mobile app can upload directly to the correct object without ever holding an AWS credential itself. The Celery-based notification queue from the payments lesson is replaced with SQS: a payment-confirmation event enqueues a notification-send message, with the visibility timeout set to comfortably exceed the slowest observed email-provider response time (learned the hard way, the same operational lesson the original Celery scenario surfaced) so a slow send doesn't cause a duplicate delivery to reprocess the same notification, and a DLQ with a maximum-receive-count of three catches any message that fails repeatedly — during testing, a malformed order ID in one message causes the notification handler to throw on every attempt, and instead of blocking the queue indefinitely, it lands in the DLQ after the third failure, where the FDE finds it immediately instead of hunting through hours of application logs for a queue that "just seems stuck."

## Practice Loop

1. For the order-management and payments system, write out which AWS storage/compute service each piece of data or workload maps to (order rows, uploaded attachments, the notification task), and justify each choice by its actual access pattern and durability need.
2. Write a one-paragraph comparison of RDS Multi-AZ versus self-managed Postgres on EC2 for this specific system, naming the concrete operational tasks (patching, backup, failover) each option would leave the FDE or the customer's team owning.
3. Implement (or simulate) an SQS consumer for the notification task, deliberately set its visibility timeout shorter than the actual processing time, and observe a message being picked up a second time before the first attempt finishes — then fix the timeout and confirm the duplicate stops.
4. Configure a dead-letter queue with a maximum-receive-count of three, deliberately send a message that always fails processing, and confirm it lands in the DLQ after the third failed attempt rather than retrying indefinitely.
5. Generate a presigned URL for an S3 upload, and write a one-paragraph explanation of why this is preferable to giving the uploading client a standing AWS credential.

## Evidence of Understanding

You can justify a choice between RDS and self-managed Postgres on EC2 using the actual operational trade-off (patching, backup, failover ownership) rather than a default preference, and name a specific requirement that would force the self-managed choice. You can explain S3's durability and read-after-write consistency guarantees precisely, and distinguish a durability/consistency question from an access-control failure. You can design an SQS-backed queue with a visibility timeout sized to actual processing time and a dead-letter queue that catches structurally broken messages, and explain why SQS's at-least-once guarantee requires the same idempotency discipline as the Stripe webhook handler from Module 2.

## Suggested Extension

Add an S3 event notification that triggers when a new attachment is uploaded, publishing to the same SQS queue pattern used for notifications, and design the consumer so that a duplicate event notification (S3 also does not guarantee exactly-once event delivery) does not cause the attachment to be processed twice.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why EC2 is not a neutral "more control" default
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson push back on treating EC2 as a neutral, "closer to the metal, therefore safer" default choice compared to a managed service like RDS?

**OPTIONS:**
- [x] A: Every operational concern a managed service would absorb — patching, backup scheduling, failover orchestration — becomes something the FDE or the customer's team now owns indefinitely, which is a real, ongoing cost, not a free upgrade in control
- [ ] B: EC2 instances are technically incapable of running a production database workload
- [ ] C: There is no operational difference between EC2 and RDS; the choice is purely about raw compute price
- [ ] D: RDS is always strictly more expensive than EC2 for any workload of any size

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The real trade-off is who ends up owning the operational burden after the choice is made — EC2 gives more control at the cost of taking on everything a managed service would otherwise have handled.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [ec2-vs-managed, operational-ownership]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** When self-managed Postgres actually earns its place
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, when does self-managed Postgres on EC2 become the right choice over RDS?

**OPTIONS:**
- [x] A: Only when a specific, named requirement RDS doesn't support forces it — a particular extension, a specific replication topology, or cost optimization at a scale justified by dedicated staff who will actually own the operational burden
- [ ] B: Self-managed Postgres should always be the default for any customer engagement, regardless of requirements
- [ ] C: RDS is technically incapable of running PostgreSQL, only MySQL-compatible engines
- [ ] D: Self-managed Postgres is preferable whenever the customer wants to reduce their AWS bill by any amount
- [ ] E: This choice should be made solely based on which option the FDE personally has more experience with

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson frames RDS as the correct default and self-managed as the exception that needs a specific, justified reason — not a symmetric choice made on convenience or familiarity.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [self-managed-postgres, rds-default]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** S3 durability versus an access-control failure
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
An object stored in S3 turns out to be world-readable due to an overly permissive bucket policy. Is this a failure of S3's durability guarantee?

**OPTIONS:**
- [x] A: No — durability and consistency are separate guarantees from access control; the object was stored durably and consistently exactly as promised, but a misconfigured bucket policy is an access-control failure, a distinct problem diagnosed differently
- [ ] B: Yes, because any unintended data exposure is automatically classified as a durability failure by definition
- [ ] C: This scenario is impossible, since S3's durability guarantee also enforces correct access permissions automatically
- [ ] D: It depends entirely on which storage class the object is stored in

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson explicitly separates these two failure modes because conflating them wastes time during an incident — durability is about whether the data survives, access control is about who can reach it, and they fail independently.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [s3-durability, access-control-distinction]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What a presigned URL avoids
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend a presigned URL for a client uploading directly to S3, rather than giving that client a standing AWS credential?

**OPTIONS:**
- [x] A: A presigned URL grants scoped, time-limited access to one specific object, the same pattern as an IAM role's short-lived credentials, instead of handing the client a standing credential with open-ended access and lifetime
- [ ] B: Presigned URLs are required because S3 technically does not accept direct uploads from any AWS credential
- [ ] C: There is no meaningful access-control difference between a presigned URL and a standing credential
- [ ] D: Presigned URLs are exclusively a cost-optimization feature with no security implication

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the same scoped, time-limited pattern from the IAM lesson reapplied at the object level — narrow, expiring access instead of a standing credential the client would otherwise need to hold and protect.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [presigned-url, scoped-temporary-access]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why SQS requires the same idempotency discipline as Stripe webhooks
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does SQS's delivery guarantee connect to the idempotency discipline covered in the Module 2 Stripe webhook lesson?

**OPTIONS:**
- [x] A: SQS is explicitly at-least-once, not exactly-once — the identical hazard the Stripe webhook lesson covered for inbound events — so an SQS consumer needs the same "check whether this has already been processed" discipline rather than assuming delivery count equals processing count
- [ ] B: SQS and Stripe webhooks share no meaningful similarity; the comparison is coincidental
- [ ] C: SQS guarantees exactly-once delivery, making idempotency unnecessary for SQS consumers specifically
- [ ] D: This connection only applies if the SQS queue is being used to relay Stripe webhook events specifically

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a deliberate cross-lesson echo — the same at-least-once delivery hazard shows up as a first-class AWS primitive here, requiring the identical defensive discipline the webhook lesson established.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [sqs-idempotency, stripe-webhook-connection]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Sizing the visibility timeout correctly
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend sizing an SQS visibility timeout against the slowest realistic processing time, rather than the average case?

**OPTIONS:**
- [x] A: If the timeout is shorter than an actual processing run, the message becomes visible again and a second consumer picks it up before the first finishes, causing duplicate processing — sizing to the average case would still let slower-than-average runs trigger exactly this failure
- [ ] B: The visibility timeout has no effect on whether a message is processed more than once
- [ ] C: SQS automatically adjusts the visibility timeout to match actual processing time with no configuration needed
- [ ] D: Sizing to the average case is always safe because SQS deduplicates messages by content automatically

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
An average-case timeout still leaves every slower-than-average run exposed to the exact duplicate-delivery scenario the lesson describes — sizing to the slowest realistic case is what actually closes the gap.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [visibility-timeout-sizing, duplicate-processing]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What the dead-letter queue revealed in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, what specific problem did the dead-letter queue surface, and why was that better than the alternative?

**OPTIONS:**
- [x] A: A structurally broken message (a malformed order ID that failed on every attempt) landed in the DLQ after three failed receives, giving the FDE an immediate, specific signal — rather than the message retrying indefinitely and blocking queue throughput while the FDE searched through hours of logs
- [ ] B: The DLQ automatically repaired the malformed order ID and reprocessed the message successfully
- [ ] C: The DLQ prevented the malformed message from ever being sent in the first place
- [ ] D: The scenario describes a queue with no actual problem; the DLQ was configured but never used
- [ ] E: The DLQ only logs an error without moving the message anywhere

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The DLQ's value here is diagnostic — it turns an indefinitely-retrying, hard-to-notice problem into an immediately visible one, distinguishing a structurally broken message from a transient failure.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [dead-letter-queue, diagnostic-signal]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Mapping workload data to the right storage service
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the practical scenario, why does order/payment data go into RDS while uploaded attachments go into S3, rather than both going into the same service?

**OPTIONS:**
- [x] A: Order and payment data is relational, transactional, and needs Multi-AZ failover with point-in-time recovery, while attachments are whole-object files best served by S3's object storage model and presigned direct-upload pattern — each service matches the actual access pattern and shape of its data
- [ ] B: RDS and S3 are functionally interchangeable, and the split in the scenario is arbitrary
- [ ] C: S3 cannot store any data related to financial transactions under AWS's terms of service
- [ ] D: RDS technically cannot store more than one type of data per database instance

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This mirrors the access-pattern-matching discipline from the NoSQL lesson in Module 2 — the right storage choice follows from what the data actually is and how it's actually used, not a single default service for everything.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [storage-service-mapping, access-pattern-fit]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 3

```yaml
lesson_id: cloud-devops-infrastructure-03-aws-security-and-secrets-management-kms-secrets-manager-cloudtrail
lesson_title: "AWS Security & Secrets Management (KMS, Secrets Manager, CloudTrail)"
lesson_order: 3

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Explain KMS envelope encryption precisely enough to reason about why a key policy is a separate control surface from an IAM policy."
  - "Choose between Secrets Manager and SSM Parameter Store for a given secret based on its actual rotation and cost requirements, not by default."
  - "Use CloudTrail data events as investigative evidence for an unexpected access pattern, not just as a compliance checkbox."

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
# AWS Security & Secrets Management (KMS, Secrets Manager, CloudTrail)

## Concepts Covered

KMS encrypts data through envelope encryption, and the mechanism is worth naming precisely because "KMS encrypts your data" understates what actually happens: a KMS key almost never encrypts your actual data directly (large payloads and KMS's own request limits make that impractical); instead, KMS generates a unique data key for the object or record being encrypted, that data key encrypts the actual data locally, and then the data key itself — small — gets encrypted by the KMS key and stored alongside the encrypted data. Decryption reverses this: KMS decrypts the wrapped data key (an operation that hits KMS and can be logged, rate-limited, and access-controlled), and only then can the now-plaintext data key decrypt the actual payload locally. This is why a KMS key policy is a genuinely separate control surface from an IAM policy, not a redundant second copy of the same rule: the key policy, attached directly to the KMS key, controls who may use or administer that specific key, and by default a KMS key's policy requires the account's IAM policies to *also* grant access before an identity can use it — meaning both the key policy and the IAM policy have to agree, a dual-control design that exists specifically so that neither a compromised IAM policy alone nor a compromised key policy alone is sufficient to decrypt sensitive data; an FDE reviewing "why can't this role decrypt this secret even though its IAM policy allows `kms:Decrypt`" needs to check the key policy as a genuinely separate place the answer could live, not assume the IAM policy is the whole story.

Secrets Manager and SSM Parameter Store both store sensitive values encrypted (via KMS, tying directly back to the envelope-encryption mechanism above), but they solve different problems and the choice between them is a real trade-off, not a default. Parameter Store's standard tier is free for a large number of parameters, supports hierarchical paths and versioning, and is the right choice for configuration that doesn't need automatic rotation — feature flags, non-sensitive endpoints, and even sensitive-but-static values where manual rotation on a known schedule is acceptable. Secrets Manager costs per secret per month specifically because it does more: native automatic rotation via a rotation Lambda function, cross-region replication, and a staged versioning model (`AWSCURRENT` and `AWSPENDING` labels track which version is live versus mid-rotation) that lets a rotation happen without a window where the secret is simply gone. The native rotation Lambdas AWS provides out of the box are built for AWS-adjacent secrets — RDS, DocumentDB, Redshift credentials — where Secrets Manager can coordinate the rotation with the database engine directly; for a third-party API credential like a Stripe secret key, there's no native rotation target, so rotation either means writing a custom rotation Lambda that calls Stripe's own key-rotation API, or accepting a manual, scheduled rotation process using Secrets Manager's versioning to stage the new value before cutting over — either way, the win over Parameter Store is Secrets Manager's staged-version model doing the coordination work, not fully automatic zero-touch rotation for a credential AWS doesn't own the rotation mechanics for.

CloudTrail records API calls made against an AWS account, split into two categories that matter differently for an investigation: management events (control-plane actions — creating a role, modifying a security group, changing a KMS key policy) are logged by default and answer "what changed about how this account is configured." Data events (data-plane actions — a specific `GetObject` call on a specific S3 object, a specific `GetSecretValue` call on a specific secret) are not logged by default because of their volume and cost, and have to be explicitly enabled per-resource for the ones that matter — a secret holding a customer's payment-provider credential is exactly the kind of resource worth paying that cost for, because "who called `GetSecretValue` on this ARN, and from where" is precisely the evidence needed to investigate a suspected credential compromise, and it doesn't exist unless it was turned on before the incident, not after. This is the security-domain equivalent of the OpenTelemetry distributed-tracing discipline from Module 2 — an audit trail you can query after the fact only exists if the specific events worth tracing were instrumented in advance, not reconstructed from memory once something's already gone wrong. GuardDuty layers anomaly detection on top of this raw event stream (an unusual API call pattern, a credential being used from a geography it's never been used from before), turning "the evidence exists somewhere in CloudTrail if someone goes looking" into "an alert fires automatically when the evidence looks wrong" — the difference between a passive record and an active detection signal.

## Practical Backend Scenario

An FDE reviewing a customer's early prototype of the Module 2 payments integration finds the Stripe webhook signing secret hardcoded directly into the EC2 instance's user-data script — visible in plaintext to anyone with `ec2:DescribeInstanceAttribute` permission on that instance, a far larger set of people than anyone realizes, since user-data isn't treated as sensitive by most teams' own IAM reviews. The fix moves the secret into Secrets Manager, encrypted under a customer-managed KMS key whose key policy explicitly lists only the payments service's IAM role as an authorized user — not the broader account, and not every EC2 instance profile in the account, closing the dual-control gap a default AWS-managed key wouldn't have surfaced as clearly. Because Stripe doesn't have a native Secrets Manager rotation integration, the FDE sets up a quarterly manual rotation process using the `AWSPENDING` version label to stage a newly-generated Stripe secret before cutting the application over to it, rather than a risky in-place overwrite with no fallback if the new value turns out to be wrong. Finally, the FDE enables CloudTrail data events specifically on that one secret's ARN — a low-volume, deliberate choice, not a blanket "log everything" that would bury the signal — so that any `GetSecretValue` call from a principal or source IP that isn't the payments service's own role becomes a visible, queryable anomaly instead of an invisible one, giving the customer's security team actual investigative evidence instead of a compliance checkbox that was never wired up to catch anything real.

## Practice Loop

1. Diagram envelope encryption step by step for a specific secret: which key encrypts what, in what order, on both the encrypt and decrypt paths.
2. Write out a KMS key policy that grants `kms:Decrypt` to exactly one IAM role's ARN, and explain what would happen if that role's own IAM policy did not also separately grant `kms:Decrypt` — confirm both are required.
3. For three example secrets — a Stripe API key, an RDS database password, and a non-sensitive feature-flag value — decide which belongs in Secrets Manager versus Parameter Store, and justify each choice by its actual rotation need.
4. Design the manual rotation process for the Stripe secret using Secrets Manager's `AWSCURRENT`/`AWSPENDING` version labels, and write out the exact sequence of steps that avoids a window where the application has no valid secret to use.
5. Enable (or simulate enabling) CloudTrail data events on one specific secret's ARN, and write the exact CloudTrail query or filter you'd use to answer "who called GetSecretValue on this secret in the last 24 hours, and from where."

## Evidence of Understanding

You can explain envelope encryption precisely — which key encrypts what, and why a KMS key policy is a genuinely separate control surface that must independently agree with an IAM policy before access is granted. You can choose between Secrets Manager and Parameter Store for a specific secret based on its actual rotation need and cost, and explain why a third-party credential like a Stripe key needs a different rotation approach than an RDS-native secret. You can explain the difference between CloudTrail management events and data events, and design a deliberate, narrow data-event logging choice that produces real investigative evidence for a specific sensitive resource rather than an unfocused, unusable firehose.

## Suggested Extension

Design a GuardDuty-style anomaly rule (in prose, naming the specific signal) that would have caught the original hardcoded-secret exposure earlier — before the fix — by detecting an unusual pattern of `DescribeInstanceAttribute` calls against instances whose user-data is known to contain sensitive values, and explain what evidence that rule would need that a default AWS setup doesn't already provide.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What envelope encryption actually encrypts
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In KMS envelope encryption, what does the KMS key itself directly encrypt?

**OPTIONS:**
- [x] A: A small, unique data key generated for the object or record being encrypted — the data key then encrypts the actual data locally, and the KMS key only ever encrypts that small data key, not the full payload
- [ ] B: The KMS key directly encrypts the entire data payload itself, regardless of size
- [ ] C: KMS keys are used exclusively for signing operations and never perform encryption
- [ ] D: The KMS key encrypts nothing; all encryption happens entirely outside of KMS

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the precise mechanism the lesson insists on — KMS wraps a small data key, and that data key (not the KMS key directly) does the actual work of encrypting the real payload.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [envelope-encryption, kms-data-key]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why a KMS key policy is a separate control surface
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
An IAM role's permission policy grants `kms:Decrypt` on a specific key, but the role still cannot decrypt data with that key. What is the most likely explanation, per the lesson's dual-control design?

**OPTIONS:**
- [x] A: The KMS key's own key policy does not also grant that role access — by default, both the IAM policy and the key policy must independently agree before access is allowed, so an IAM grant alone is not sufficient
- [ ] B: KMS keys never actually check IAM policies at all, only key policies matter
- [ ] C: This situation is impossible; an IAM policy grant is always sufficient on its own
- [ ] D: The role's credentials must have expired, since key policies cannot block an otherwise-valid IAM grant
- [ ] E: KMS requires a separate MFA prompt for every decrypt call regardless of policy configuration

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is exactly the dual-control gap the lesson highlights — checking only the IAM policy misses half the story, since the key policy is a genuinely separate, independently-required grant.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [key-policy-dual-control, kms-access-troubleshooting]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Secrets Manager versus Parameter Store
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A team needs to store a non-sensitive feature-flag value that never needs automatic rotation. Which service does the lesson recommend, and why?

**OPTIONS:**
- [x] A: SSM Parameter Store — its standard tier is free for a large number of parameters and is the right fit for configuration that doesn't need Secrets Manager's rotation machinery, which exists specifically to justify its per-secret cost
- [ ] B: Secrets Manager, because it should always be used for every stored value regardless of sensitivity or rotation need
- [ ] C: Neither service supports storing non-sensitive configuration values
- [ ] D: Parameter Store is only usable for values larger than 4KB, making it unsuitable for a short flag value

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson frames this as a real trade-off — Secrets Manager's cost buys rotation and staged versioning that a non-sensitive, non-rotating flag simply doesn't need.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [secrets-manager-vs-parameter-store, cost-tradeoff]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why a Stripe secret needs a different rotation approach than an RDS password
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why can't Secrets Manager's native, out-of-the-box automatic rotation Lambda handle rotating a Stripe API key the same way it handles an RDS database password?

**OPTIONS:**
- [x] A: The native rotation Lambdas are built for AWS-adjacent secrets where Secrets Manager can coordinate directly with the database engine; a third-party service like Stripe has no such native rotation target, so it needs either a custom rotation Lambda calling Stripe's own API or a manual, staged rotation process
- [ ] B: Secrets Manager technically cannot store any value that isn't an AWS-native database credential
- [ ] C: Stripe secrets do not require rotation under any circumstances, unlike RDS passwords
- [ ] D: There is no actual difference; the native RDS rotation Lambda works identically for any third-party API key
- [ ] E: Rotation is only possible for secrets stored in the us-east-1 region

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The gap is specifically about coordination — Secrets Manager's native rotation Lambdas assume an AWS-managed rotation target, which a third-party credential like Stripe's simply doesn't have.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [third-party-secret-rotation, native-rotation-limits]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Management events versus data events
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the difference between a CloudTrail management event and a CloudTrail data event?

**OPTIONS:**
- [x] A: Management events are control-plane actions (changing a security group, modifying a key policy) and are logged by default; data events are data-plane actions on a specific resource (a specific GetObject or GetSecretValue call) and must be explicitly enabled per resource due to their volume
- [ ] B: Management events and data events are two names for the same category of CloudTrail log entry
- [ ] C: Data events are logged by default and management events must be explicitly enabled
- [ ] D: CloudTrail only records management events; data events are not a CloudTrail concept at all

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This distinction is exactly why the scenario's data-event logging had to be a deliberate choice on one specific secret's ARN — data events don't exist by default, unlike management events.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [cloudtrail-management-vs-data-events, audit-logging]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the audit evidence had to exist before the incident
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson connect enabling CloudTrail data events in advance to the OpenTelemetry distributed-tracing discipline from Module 2?

**OPTIONS:**
- [x] A: Both make the same point — an audit trail or trace you can query after the fact only exists if the specific events worth capturing were instrumented in advance; you cannot reconstruct "who called GetSecretValue" or a request's trace after the fact if it was never being recorded
- [ ] B: CloudTrail and OpenTelemetry are unrelated tools serving entirely different purposes with no shared principle
- [ ] C: This connection only holds for secrets specifically, not for any other CloudTrail data event type
- [ ] D: OpenTelemetry traces are automatically retained by CloudTrail without any separate configuration
- [ ] E: This is purely a coincidental naming similarity between the two systems

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a deliberate cross-module echo — proactive instrumentation, whether it's a distributed trace or an audit log, is what makes after-the-fact investigation possible at all.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [proactive-instrumentation, observability-connection]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the original secret exposure was more dangerous than it looked
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson specifically call out that the Stripe secret hardcoded in EC2 user-data was visible to "a far larger set of people than anyone realizes"?

**OPTIONS:**
- [x] A: User-data isn't treated as sensitive by most teams' own IAM reviews, so anyone with the relatively ordinary `ec2:DescribeInstanceAttribute` permission — a far broader group than anyone who'd expect to see a payment secret — could read it, unlike a properly access-controlled secret
- [ ] B: EC2 user-data is technically encrypted by default, so this exposure could not actually have occurred
- [ ] C: This exposure only mattered because the instance was in a public subnet
- [ ] D: The exposure was limited to exactly one person: the engineer who originally wrote the user-data script

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The real danger is the mismatch between how sensitive the secret actually is and how ordinary the permission needed to read it turns out to be — user-data doesn't get the scrutiny a secret deserves.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [user-data-exposure, unexpected-access-surface]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why blanket CloudTrail logging would defeat the purpose
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the scenario describe enabling data events on one specific secret's ARN as "a low-volume, deliberate choice, not a blanket 'log everything'"?

**OPTIONS:**
- [x] A: A blanket, unfocused firehose of every data event across every resource buries the specific signal that actually matters under noise, whereas a narrow, deliberate choice on the one sensitive resource keeps the resulting evidence usable and queryable
- [ ] B: AWS technically limits every account to logging exactly one data event source at a time
- [ ] C: Logging more data events always costs strictly less than logging fewer, so the distinction is irrelevant to cost
- [ ] D: Blanket logging and narrow logging produce identical investigative value; the distinction is stylistic only
- [ ] E: This distinction only matters for accounts operating in multiple AWS regions simultaneously

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The value of the audit trail depends on being able to actually use it — a deliberate, narrow choice produces a signal an investigator can act on, while an indiscriminate firehose produces volume without focus.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [deliberate-logging-scope, signal-vs-noise]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 4

```yaml
lesson_id: cloud-devops-infrastructure-04-docker-production-containers
lesson_title: "Docker: Production Containers"
lesson_order: 4

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Write a multi-stage Dockerfile that separates build-time dependencies from the runtime image, reducing both image size and attack surface."
  - "Run a production container as a non-root user and explain the concrete escalation risk that default root execution leaves open."
  - "Design a container's shutdown behavior (signal handling, health checks) so an orchestrator's stop or restart does not corrupt in-flight work."

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
# Docker: Production Containers

## Concepts Covered

A `Dockerfile` written the naive way — a single stage `FROM python:3.12`, `pip install` everything including build-time-only compilers, `COPY . .` for the whole application — produces a working container, but a working container and a production-ready one are different bars. A single-stage build carries every build tool (a C compiler, headers, package-manager caches) into the final image, even though none of that is needed once the application is actually running; it just sits there, larger than it needs to be, and more importantly, larger as an attack surface — anything present in a running container is a potential tool for whoever manages to execute code inside it. A multi-stage build separates these concerns explicitly: an early `FROM python:3.12 AS builder` stage installs build dependencies and compiles or resolves wheels, and a final stage starts fresh `FROM python:3.12-slim` (or a distroless base with no shell or package manager at all), copying only the compiled artifacts and application code from the builder stage across — the compiler, the package-manager cache, anything that was only ever needed to produce the artifact, never makes it into what actually ships. The size difference is not cosmetic: a build that drops from roughly a gigabyte down to a couple hundred megabytes or less measurably improves cold-start latency (less to pull and unpack) on every platform that has to fetch the image before starting a container, which matters directly for how quickly a customer's autoscaler or a rolling deployment can bring up new instances of a service under load.

Layer ordering interacts with build speed in a way that's easy to get backwards. Docker caches each instruction as a layer and reuses a cached layer if nothing above it in the Dockerfile changed and the instruction itself is identical; putting `COPY . .` (the application's own source code, which changes on nearly every commit) before the dependency-installation step means every single code change invalidates the cache for the dependency install that follows it, forcing a full reinstall on every build. Ordering instead from least-frequently-changing to most-frequently-changing — copy only the dependency manifest (`requirements.txt`, `pyproject.toml`) and run the install first, then copy the actual application code afterward — means a code-only change reuses the cached dependency layer and only rebuilds the fast, final steps, which is the difference between a CI build taking seconds versus minutes once a dependency list has stabilized. Running the final container as a non-root user (a dedicated `USER appuser` directive, or the `:nonroot` tag distroless base images provide) closes a specific, concrete risk rather than satisfying an abstract security checklist: a container escape or a misconfigured volume mount turns "the process runs as root inside the container" into "the process runs as root on the host" far more easily than most engineers expect, and a non-root process inside the container simply has nothing equivalent to escalate into even if the isolation boundary around it is imperfect.

Production readiness also means the container behaves correctly when it's told to stop, not just when it's told to start. A `HEALTHCHECK` instruction (or an orchestrator-level equivalent) gives whatever is managing the container a way to know it's actually serving traffic correctly, not merely that the process hasn't crashed — a process can be technically running while its actual dependency (a database connection, a downstream service) is unreachable, and a health check that verifies real readiness catches that distinction a bare process-alive check would miss. Signal handling matters on the way down: when an orchestrator stops a container, it sends `SIGTERM` first and gives the process a grace period to shut down cleanly before escalating to an unconditional `SIGKILL`; an application that ignores `SIGTERM` (the default behavior for many process managers unless the application explicitly traps it) gets killed uncleanly the moment the grace period expires, mid-request or mid-task, regardless of what it was doing. This directly reconnects to the Celery worker scenario from Module 2's payments lesson: a worker mid-task when it receives an unhandled `SIGKILL` doesn't get a chance to finish or to roll back cleanly, which is exactly the kind of interrupted, half-completed state that can produce a duplicate or lost notification on the next delivery attempt — the same idempotency concern from that lesson, now caused by a container lifecycle event instead of a webhook retry, which is why a production container's application code needs to explicitly catch `SIGTERM`, stop accepting new work, finish or safely abandon in-flight work, and exit on its own before the grace period runs out and the orchestrator stops waiting.

## Practical Backend Scenario

The FastAPI order-management service and its Celery notification worker from Module 2 are first containerized the fast way: a single-stage `Dockerfile` `FROM python:3.12`, installing everything (including build tools needed only to compile one dependency's C extension) with `pip install`, `COPY . .` placed before the install step, and the container's default user left as root because nobody set a `USER` directive. The image comes out close to a gigabyte, every code change forces a full dependency reinstall in CI because the cache never survives a `COPY . .` placed too early, and during a routine rolling deployment, the Celery worker container receives `SIGTERM`, has no signal handler registered, and gets killed uncleanly by the orchestrator's `SIGKILL` a few seconds later while mid-way through sending a notification — producing, once again, the double-send problem the original payments lesson already had to solve for webhook retries, this time caused by a deploy instead of a network hiccup. The fix rebuilds the Dockerfile as a multi-stage build (a `builder` stage compiling the one dependency needing a C extension, a final `python:3.12-slim` stage copying only the built wheels and application code), reorders the dependency-install step ahead of the application-code copy so CI cache hits return, adds `USER appuser` so the container never runs as root, and adds an explicit `SIGTERM` handler in the Celery worker that stops pulling new tasks, finishes (or safely defers) the task already in flight, and exits cleanly — with the orchestrator's grace period tuned to comfortably exceed the worker's longest realistic single-task duration, so the clean shutdown path actually has time to complete before `SIGKILL` would otherwise cut it off.

## Practice Loop

1. Write the naive single-stage Dockerfile for a small Python service (root user, `COPY . .` before `pip install`), build it, and record its final image size.
2. Rewrite it as a multi-stage build with a `builder` stage and a `python:3.12-slim` (or distroless) final stage, add a non-root `USER` directive, and record the new image size and the reduction.
3. Make a small code-only change (no dependency change) and time a rebuild under both the original instruction order and the reordered (dependencies-before-code) version, to measure the cache-hit difference directly.
4. Add a `HEALTHCHECK` instruction that verifies a real readiness signal (e.g., a `/health` endpoint that checks a database connection) rather than just process liveness, and confirm it correctly reports unhealthy when the dependency is unreachable.
5. Add a `SIGTERM` handler to a worker process that simulates a long-running task, send it `SIGTERM` mid-task, and confirm it finishes or safely defers the in-flight task and exits cleanly before an enforced grace-period timeout would otherwise kill it.

## Evidence of Understanding

You can write a multi-stage Dockerfile that keeps build-only dependencies out of the final image, and explain the concrete size and attack-surface consequences of not doing so. You can order Dockerfile instructions to maximize CI cache reuse, and measure the difference a correct ordering makes on a code-only rebuild. You can run a container as a non-root user and explain the specific escalation risk that default root execution leaves open, and you can implement `SIGTERM` handling that lets an in-flight task finish or safely defer before an orchestrator's grace period expires, connecting this directly to the duplicate-processing risk from Module 2's Celery notification scenario.

## Suggested Extension

Add a `.dockerignore` file that excludes the local `.git` directory, test fixtures, and any local `.env` file from the build context, and explain — beyond just build speed — the specific risk of a `.env` file containing real secrets accidentally being baked into an image layer if it isn't excluded.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What a multi-stage build actually removes
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does a multi-stage Docker build remove from the final production image that a single-stage build would otherwise include?

**OPTIONS:**
- [x] A: Build-time-only tools and artifacts — compilers, headers, package-manager caches — that were only ever needed to produce the compiled artifact, not to run the application
- [ ] B: The application's own source code, which must be copied back in through a separate deployment step
- [ ] C: All environment variables, which must be reconfigured manually after the image is built
- [ ] D: The container's networking configuration, which is not preserved across build stages

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The whole point of the separate builder stage is that its tools never need to exist in the image that actually ships — only the compiled output does.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [multi-stage-build, image-size-reduction]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why image size is not just cosmetic
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that reducing image size from roughly a gigabyte to a couple hundred megabytes matters beyond aesthetics?

**OPTIONS:**
- [x] A: A smaller image measurably improves cold-start latency, since less data has to be pulled and unpacked before a container can start — directly affecting how quickly an autoscaler or rolling deployment can bring up new instances under load
- [ ] B: Docker technically refuses to run any image larger than 500MB in a production environment
- [ ] C: Image size has no measurable effect on anything besides local disk usage
- [ ] D: Smaller images automatically run faster once started, regardless of pull or unpack time

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The concrete operational consequence is startup speed under real deployment and scaling events, not an abstract preference for smaller numbers.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [image-size, cold-start-latency]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why COPY . . placed early breaks the cache
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does placing `COPY . .` before the dependency-installation step force a full dependency reinstall on nearly every build?

**OPTIONS:**
- [x] A: Docker's layer cache is invalidated for every instruction after one that changed, and since application source code changes on nearly every commit, placing the code copy first invalidates the cache for the dependency install that follows it, every time
- [ ] B: Docker technically does not cache any layer that involves a COPY instruction, regardless of its position
- [ ] C: Placing COPY . . early has no effect on caching; the reinstall happens regardless of instruction order
- [ ] D: This only affects builds running on CI, never local development builds

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The cache-invalidation mechanism is exactly why ordering matters — a layer's cache is only reused if nothing above it changed, so a frequently-changing layer placed early poisons the cache for everything after it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [dockerfile-layer-caching, build-instruction-order]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** The concrete risk of running a container as root
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific, concrete risk does running a production container as a non-root user close, according to the lesson?

**OPTIONS:**
- [x] A: A container escape or misconfigured volume mount can turn "the process runs as root inside the container" into "the process runs as root on the host" — a non-root process has nothing equivalent to escalate into, even under an imperfect isolation boundary
- [ ] B: Root-user containers are technically incapable of accessing the network, making them unsuitable for any server workload
- [ ] C: There is no actual security difference; the non-root recommendation is purely a stylistic convention
- [ ] D: Running as non-root prevents the container from ever crashing due to a resource limit

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the concrete escalation path the lesson names precisely — it's not an abstract checklist item, it's a specific consequence of what root access inside a container can become if isolation is ever imperfect.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [non-root-container, container-escape-risk]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What a real health check verifies that a liveness check doesn't
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson distinguish a health check that verifies real readiness (e.g., checking a database connection) from one that only confirms the process hasn't crashed?

**OPTIONS:**
- [x] A: A process can be technically running while a real dependency it needs is unreachable, and a bare process-alive check would miss that distinction entirely, reporting the container healthy when it actually cannot serve real traffic correctly
- [ ] B: These two types of health check are functionally identical in every practical scenario
- [ ] C: A process-alive check is always sufficient because a crashed dependency always crashes the whole process too
- [ ] D: Health checks that verify dependencies are technically not supported by any container orchestrator
- [ ] E: This distinction only matters for containers running a database directly, not an application server

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The gap between "process alive" and "actually able to serve traffic" is exactly what a real readiness check closes — a crashed dependency doesn't necessarily crash the process that depends on it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [health-check-readiness, liveness-vs-readiness]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why an unhandled SIGTERM reconnects to the Celery duplicate-send problem
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does an application ignoring SIGTERM during a container stop connect to the duplicate-notification problem from Module 2's payments lesson?

**OPTIONS:**
- [x] A: A worker killed uncleanly (SIGKILL after an unhandled SIGTERM) mid-task doesn't get a chance to finish or roll back cleanly, producing the same kind of interrupted, half-completed state that can cause a duplicate or lost notification on the next delivery attempt — the identical idempotency hazard, now triggered by a container lifecycle event instead of a webhook retry
- [ ] B: SIGTERM and webhook retries are unrelated failure modes with no shared consequence
- [ ] C: This connection only applies if the worker is specifically processing a Stripe webhook at the moment SIGTERM arrives
- [ ] D: A container that ignores SIGTERM is guaranteed to lose the in-flight task entirely, never to duplicate it
- [ ] E: Handling SIGTERM prevents the container from ever needing to restart in the first place

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a deliberate cross-module echo — the same interrupted-mid-task hazard that motivated idempotent webhook handling in Module 2 reappears here, caused by a deploy's SIGTERM/SIGKILL sequence instead of a network retry.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [sigterm-handling, celery-duplicate-connection]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the grace period must exceed the longest task, not the average one
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the scenario tune the orchestrator's grace period to exceed the worker's longest realistic single-task duration, rather than an average task duration?

**OPTIONS:**
- [x] A: A grace period sized to the average case would still let any slower-than-average task get cut off by SIGKILL before its clean-shutdown handler finishes, which is exactly the failure the fix was meant to close
- [ ] B: The grace period has no relationship to task duration; it is a fixed value that cannot be configured
- [ ] C: Average-case sizing is always sufficient because Celery automatically extends the grace period for slow tasks
- [ ] D: This consideration only matters for tasks that involve a network call, not any other kind of work

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The same "size to the worst realistic case, not the average" reasoning that applies to an SQS visibility timeout applies here — an average-case grace period still leaves the slower tail exposed to an unclean kill.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [grace-period-sizing, worst-case-not-average]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What the reordered instructions fixed in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific problem did reordering the Dockerfile's instructions (dependency install before code copy) fix in the scenario?

**OPTIONS:**
- [x] A: It restored the CI build cache for the dependency-install layer, so a code-only change no longer forced a full dependency reinstall on every single build
- [ ] B: It fixed the container's non-root user configuration, which was unrelated to instruction ordering
- [ ] C: It reduced the final image's runtime memory usage during normal operation
- [ ] D: It had no actual effect described in the scenario; the reordering was purely stylistic

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the direct, named fix for the cache-invalidation problem the scenario describes — a build-speed issue, distinct from the separate root-user and multi-stage fixes applied alongside it.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [instruction-reordering-fix, ci-build-speed]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Distinguishing the three separate fixes in the scenario
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The scenario applies four distinct fixes to the original Dockerfile and worker. Which pairing correctly matches a fix to the specific problem it addresses?

**OPTIONS:**
- [x] A: Multi-stage build addresses image bloat from build tools; instruction reordering addresses CI cache invalidation; the non-root USER directive addresses container-escape severity; the SIGTERM handler addresses unclean shutdown during deploys
- [ ] B: All four fixes address the exact same underlying problem and are functionally interchangeable
- [ ] C: The SIGTERM handler is what reduces the final image size, not the multi-stage build
- [ ] D: The non-root USER directive is what restores the CI build cache, not the instruction reordering
- [ ] E: Instruction reordering is what prevents the container from running as root

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Each of the four fixes in the scenario targets a genuinely distinct problem — conflating them (as the distractors do) misses that production-readiness here is several separate, composable concerns, not one fix applied four times.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [distinct-production-fixes, composable-concerns]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 5

```yaml
lesson_id: cloud-devops-infrastructure-05-kubernetes-architecture-and-core-concepts
lesson_title: "Kubernetes Architecture & Core Concepts"
lesson_order: 5

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Explain which control-plane component owns a given failed transition (scheduling, reconciliation, networking) well enough to know where to look first."
  - "Explain why a Pod is not durable identity, and how a Service and a Deployment each solve a different consequence of that fact."
  - "Distinguish a readiness probe's effect (traffic routing) from a liveness probe's effect (restart) and diagnose which one explains a given symptom."

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
# Kubernetes Architecture & Core Concepts

## Concepts Covered

A Kubernetes cluster splits into a control plane and worker nodes, and the API server sits at the center of the control plane as the single component that ever talks directly to `etcd`, the cluster's backing key-value store holding the entire desired-state configuration — every other component (the scheduler, the various controllers, the `kubelet` on each worker node) interacts with cluster state exclusively through the API server, watching for changes and submitting their own updates through it, never touching `etcd` directly. This isn't an implementation detail worth skipping past: it's what makes the whole system's declarative reconciliation model actually work as one coherent loop instead of several components racing each other against a shared database. You declare desired state — a `Deployment` spec saying "run 3 replicas of this image" — as an object submitted to the API server, and a controller (the Deployment controller, working through an intermediate `ReplicaSet`) continuously watches for drift between that desired state and the actual observed state, and acts to close the gap: if a pod dies, the controller doesn't wait for a schedule or a human to notice, it observes the replica count is now short of 3 and creates a replacement, repeatedly, as its whole job. This is fundamentally different from an imperative "run this command once" model — you are never telling Kubernetes to do a specific action, you are telling it what should continuously be true, and every controller in the system is a loop enforcing one narrow slice of that truth.

A Pod is the smallest unit Kubernetes schedules — one or more containers that share a network namespace (they can reach each other over `localhost`) and, optionally, volumes — but a Pod is explicitly not durable identity: when a Pod is rescheduled (its node fails, it's evicted, a rolling update replaces it), it gets a new Pod, typically with a new internal IP, not a resurrection of the old one. This matters because it means nothing in the system should be built assuming a specific Pod's IP or identity will still be valid a minute from now, and two different Kubernetes objects exist specifically to solve two different consequences of that fact. A `Service` provides a stable virtual IP and DNS name in front of a *changing* set of Pod IPs — it selects which Pods currently back it via a label selector, and as Pods come and go, the Service's own address stays constant while its underlying endpoint list is continuously updated; nothing that talks to the Service ever needs to know or care that the specific Pod behind it changed. A `Deployment` (managing a `ReplicaSet`, which manages the Pods) solves the separate problem of *maintaining* the right number and version of Pods over time, including rolling updates — replacing old-version Pods with new-version ones gradually, in a controlled sequence, rather than all at once — and rollback, keeping enough history to revert to a previous `ReplicaSet` if a new rollout turns out to be broken. Confusing these two objects' jobs is a common source of misdiagnosed incidents: a Service problem (wrong selector, no matching Pods) looks like "nothing is reachable," while a Deployment problem (a bad rollout, insufficient replicas) looks like "some or all of what should be reachable isn't running" — they're different failure surfaces even though both eventually present as "the app is down."

Probes are the mechanism that connects a Pod's actual runtime health back into both of these systems, and readiness and liveness probes control two genuinely different things, not two settings for the same concept. A readiness probe controls whether a Pod is included in a Service's endpoint list at all — a Pod that's running but fails its readiness probe (say, because it hasn't finished loading a cache, or a dependency it needs is briefly unreachable) is simply removed from receiving traffic until it passes again, with no restart involved; this is the mechanism that prevents traffic from being routed to a Pod that's alive but not actually able to serve a request correctly. A liveness probe controls something different: whether the `kubelet` decides the container is stuck badly enough to restart it — a container that's technically running but permanently deadlocked, for instance, would never recover on its own and never fail cleanly enough to trigger a normal crash, which is exactly the situation a liveness probe exists to catch and correct by forcing a restart. Configuring a liveness probe with the same check as a readiness probe (or with too aggressive a threshold) is a specific, real misconfiguration: a transient dependency blip that should only pull a Pod out of Service traffic for a moment instead triggers unnecessary restarts, disrupting in-flight work for a problem a readiness probe alone would have handled correctly without disrupting anything.

## Practical Backend Scenario

An FDE deploys the order-management service from Module 2 into a customer's cluster as a `Deployment` requesting 3 replicas. The `Deployment` is accepted by the API server immediately, but `kubectl get pods` shows all three Pods stuck in `Pending` — `kubectl describe pod` reveals a `FailedScheduling` event, because the scheduler cannot find any node with enough allocatable CPU: another team's workload had already saturated the cluster's existing node capacity, and nothing about accepting the `Deployment` object into `etcd` implies a node was actually available to run it on. Once node capacity is freed up and the Pods move to `Running`, a second, separate problem surfaces: the Service in front of the Deployment reports zero available endpoints, even though all three Pods are genuinely running — the readiness probe was configured against the wrong port (a leftover from an earlier version of the container image), so every Pod fails readiness continuously despite being fully healthy, and the Service correctly, if unhelpfully, keeps them all out of its endpoint list. Diagnosing this correctly means recognizing it as two entirely separate problems that happened to occur in sequence — a scheduling/capacity problem (owned by the scheduler, visible through `FailedScheduling` events) and a readiness-configuration problem (owned by the probe definition, visible through `kubectl describe pod`'s readiness status) — rather than treating "the deployment isn't working" as one undifferentiated symptom and guessing at a single cause.

## Practice Loop

1. Deploy a small workload with a `Deployment` requesting more CPU per replica than the available nodes can provide, and use `kubectl describe pod` to find and read the exact `FailedScheduling` event explaining why.
2. Fix the capacity problem, confirm all Pods reach `Running`, then deliberately misconfigure the readiness probe (wrong port or path) and observe the Service reporting zero endpoints despite the Pods being `Running`.
3. Use `kubectl get endpoints` (or `kubectl describe service`) to confirm precisely which Pods are and are not in the Service's endpoint list, and correlate that against each Pod's readiness status directly, not by inference.
4. Fix the readiness probe and confirm the Service's endpoint list updates to include the now-passing Pods, without any Pod having been restarted in the process.
5. Deliberately misconfigure a liveness probe to be overly aggressive (a very short timeout against a slightly slow health endpoint) and observe unnecessary restarts occurring — then correct it and explain, in writing, why a liveness misconfiguration and a readiness misconfiguration produce different-looking symptoms even though both start from "the probe is failing."

## Evidence of Understanding

You can trace which control-plane component owns a specific failed transition — the scheduler for a `FailedScheduling` event, the Deployment/ReplicaSet controller for a rollout or replica-count problem, the `kubelet` for a liveness-triggered restart — and use `kubectl describe` to find the specific evidence that confirms which one is actually responsible rather than guessing. You can explain why a Pod is not durable identity, and articulate the separate job a Service and a Deployment each do in response to that fact. You can distinguish a readiness-probe failure (Pod stays running, removed from traffic) from a liveness-probe failure (Pod gets restarted) by their different observable symptoms, and diagnose a real misconfiguration of either from a Service reporting zero endpoints or a Pod restarting unexpectedly.

## Suggested Extension

Add a `PodDisruptionBudget` requiring at least 2 of the 3 order-management replicas to remain available at all times, then simulate a voluntary disruption (a node drain) and confirm Kubernetes respects the budget by not evicting more Pods than the budget allows at once — and explain why this matters specifically for a service handling in-flight customer requests during a customer-initiated cluster maintenance window.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why only the API server talks to etcd
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson emphasize that the API server is the only component that directly talks to `etcd`?

**OPTIONS:**
- [x] A: It's what makes the declarative reconciliation model work as one coherent loop — every other component interacts with cluster state exclusively through the API server, rather than several components racing each other against a shared database directly
- [ ] B: Every Kubernetes component is technically permitted to write to etcd directly; the API server is simply the fastest path
- [ ] C: This is purely a performance optimization with no bearing on the system's correctness or consistency
- [ ] D: etcd does not actually exist in a Kubernetes cluster; the API server maintains state entirely in memory

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This centralization is structural, not incidental — it's exactly what allows every controller's reconciliation loop to observe and act on a single, coherent source of truth.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [api-server-etcd, control-plane-architecture]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Declarative reconciliation versus imperative commands
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does a Deployment controller's behavior differ from an imperative "run this command once" model when a Pod dies?

**OPTIONS:**
- [x] A: The controller continuously observes that the replica count has dropped below the desired state and creates a replacement — it never waits for a schedule or a human to notice, because its job is enforcing a continuously-true condition, not executing a one-time action
- [ ] B: Nothing happens automatically; a human operator must manually trigger the replacement Pod's creation
- [ ] C: The controller only checks replica counts once per day on a fixed schedule
- [ ] D: A dead Pod is never replaced automatically under any circumstances in Kubernetes

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the core distinction of declarative reconciliation — desired state is continuously enforced by a loop, not achieved once and left alone.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [declarative-reconciliation, deployment-controller]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why a Pod's IP cannot be relied upon
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson state that nothing in the system should be built assuming a specific Pod's IP will still be valid a minute from now?

**OPTIONS:**
- [x] A: A rescheduled Pod (due to node failure, eviction, or a rolling update) is a new Pod, typically with a new IP, not a resurrection of the old one — Pod identity is explicitly not durable
- [ ] B: Pod IPs change on a fixed schedule every 60 seconds regardless of whether the Pod itself is rescheduled
- [ ] C: This concern only applies to Pods running stateful workloads, never to stateless application Pods
- [ ] D: Pod IPs are actually permanent and this is a common misconception the lesson is correcting in the opposite direction

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the exact reason a Service exists — Pod identity and IP are explicitly ephemeral, so anything durable has to be built on a different abstraction.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [pod-ephemeral-identity, non-durable-ip]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What a Service solves versus what a Deployment solves
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the difference between the problem a Service solves and the problem a Deployment solves?

**OPTIONS:**
- [x] A: A Service provides a stable address in front of a changing set of Pod IPs; a Deployment maintains the right number and version of Pods over time, including rolling updates and rollback — two separate consequences of Pod identity being ephemeral
- [ ] B: A Service and a Deployment solve the exact same problem and are interchangeable in any Kubernetes manifest
- [ ] C: A Deployment provides a stable network address; a Service manages replica count and rolling updates
- [ ] D: A Service exists only to manage rollback history, with no role in network addressing

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
These are genuinely separate responsibilities — confusing them is exactly what the lesson calls out as a common source of misdiagnosed incidents.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [service-vs-deployment, separate-responsibilities]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Readiness probe versus liveness probe
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the fundamental difference in effect between a readiness probe failing and a liveness probe failing?

**OPTIONS:**
- [x] A: A failed readiness probe removes the Pod from the Service's endpoint list without restarting it; a failed liveness probe causes the kubelet to restart the container
- [ ] B: Both probes have an identical effect: they always trigger a container restart when they fail
- [ ] C: A failed liveness probe removes the Pod from Service traffic; a failed readiness probe triggers a restart
- [ ] D: Probe failures of either kind have no observable effect on the cluster's behavior

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the precise distinction the lesson insists on — traffic-routing consequence versus restart consequence — and mixing them up is the specific misconfiguration the lesson warns about.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [readiness-vs-liveness, probe-effects]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Diagnosing the scenario's first failure
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why were the three Pods stuck in `Pending` after the Deployment was accepted by the API server?

**OPTIONS:**
- [x] A: The API server accepting the Deployment object only means desired state was recorded in etcd — it does not guarantee a node was actually available; the scheduler could not find a node with enough allocatable CPU, a separate, later step in the pipeline
- [ ] B: The Deployment manifest itself contained a YAML syntax error that the API server should have rejected
- [ ] C: The container image referenced by the Deployment did not exist in any accessible registry
- [ ] D: The cluster's Service object was misconfigured, which is unrelated to Pod scheduling
- [ ] E: This is impossible; a Deployment accepted by the API server always results in Running Pods immediately

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is exactly the gap between "accepted into desired state" and "actually scheduled onto a node" that the lesson's control-plane explanation sets up — API acceptance and successful scheduling are different steps, owned by different components.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [failed-scheduling, desired-state-vs-actual]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Diagnosing the scenario's second, separate failure
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the Service report zero available endpoints even after all three Pods reached `Running` in the scenario?

**OPTIONS:**
- [x] A: The readiness probe was misconfigured against the wrong port, so every Pod continuously failed readiness despite being genuinely healthy — the Service correctly excluded them from its endpoint list based on that readiness status, a separate problem from the earlier scheduling issue
- [ ] B: The Pods were still technically Pending, contradicting the premise that they had reached Running
- [ ] C: A liveness probe failure was restarting the Pods in an infinite loop, preventing any of them from staying up
- [ ] D: The Service object itself had not yet been created, so no endpoint list could exist
- [ ] E: This second failure was actually a continuation of the same scheduling problem from before

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the scenario's deliberate second, unrelated failure — a readiness misconfiguration, distinct from the scheduling problem, and correctly diagnosed only by treating it as a separate cause rather than assuming one root cause explains everything.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [readiness-misconfiguration, zero-endpoints]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why treating "the deployment isn't working" as one symptom is a mistake
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist the scenario's two problems must be diagnosed as separate issues rather than treated as one undifferentiated "the deployment isn't working" symptom?

**OPTIONS:**
- [x] A: The two problems are owned by different control-plane components (the scheduler versus the readiness-probe/Service mechanism) with different diagnostic evidence (a FailedScheduling event versus a Pod's readiness status) — collapsing them into one symptom risks fixing one and assuming the whole problem is solved when it isn't
- [ ] B: There is no actual benefit to separating the diagnosis; both problems always have the same root cause in Kubernetes
- [ ] C: This distinction only matters when working with a cluster running more than 100 nodes
- [ ] D: Treating them separately is only useful for documentation purposes, not for actually resolving the incident faster

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Correct diagnosis depends on recognizing distinct evidence trails owned by distinct components — conflating them risks declaring victory after fixing only one of two real, separate problems.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [separate-root-causes, diagnostic-discipline]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Consequence of an overly aggressive liveness probe
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What real consequence does the lesson describe from configuring a liveness probe with the same aggressive threshold as a readiness check?

**OPTIONS:**
- [x] A: A transient dependency blip that should only pull a Pod out of Service traffic momentarily instead triggers an unnecessary restart, disrupting in-flight work for a problem readiness alone would have handled without disruption
- [ ] B: This configuration has no negative consequence; using identical thresholds for both probes is always the recommended approach
- [ ] C: An aggressive liveness threshold causes the Pod to never restart, even when it is genuinely deadlocked
- [ ] D: This misconfiguration only affects the Service's endpoint list, never causing an actual container restart

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the concrete cost of mixing up the two probes' purposes — a transient issue that readiness alone would have handled gracefully instead escalates into a disruptive restart.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [aggressive-liveness-probe, unnecessary-restart]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 6

```yaml
lesson_id: cloud-devops-infrastructure-06-eks-helm-and-production-kubernetes
lesson_title: "EKS, Helm & Production Kubernetes"
lesson_order: 6

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "State precisely what AWS manages versus what the customer/FDE manages in EKS, including how EKS Auto Mode shifts that boundary."
  - "Use a Helm chart's values.yaml to deploy the same release consistently across environments, and use helm rollback as a real incident-response tool."
  - "Scope a pod's AWS permissions to that pod's own workload identity (IRSA/Pod Identity) instead of the node's shared IAM role."

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
# EKS, Helm & Production Kubernetes

## Concepts Covered

EKS is AWS's managed control plane for Kubernetes, and the specific line between what AWS manages and what the customer (or the FDE deploying into a customer's account) manages is the single most important fact to have memorized before debugging a production EKS issue, because it tells you where to look first. AWS operates the API server's availability and patching and the `etcd` backing store — a failure there shows up on AWS's own health dashboard, not in anything a customer's team could have misconfigured. Everything below that — the worker nodes themselves, in the traditional self-managed or managed-node-group model — has historically been the customer's (or the FDE's) responsibility: the node AMI, the IAM role attached to nodes, the VPC CNI plugin handling pod networking, and any add-on version compatibility across an upgrade. EKS Auto Mode changes where that line sits, not the underlying architecture: it bundles Karpenter-based node provisioning, the VPC CNI, EBS CSI, CoreDNS, and `kube-proxy` into AWS-managed components as well, so a cluster running in Auto Mode has AWS operating meaningfully more of the stack than a traditionally-managed node group would — worth naming specifically because "EKS" no longer implies one fixed responsibility boundary the way it did a few years earlier, and an FDE needs to check which mode a given customer's cluster is actually running in before assuming who owns a given failure.

Helm packages a set of Kubernetes manifests as a versioned, parameterized chart — templates plus a `values.yaml` file supplying the specific values that differ per environment (replica count, resource limits, an environment-specific RDS endpoint) — so the same chart deploys consistently to dev, staging, and production with different values files, instead of maintaining near-duplicate hand-written YAML per environment that drifts the moment someone edits one copy and forgets the others. `helm install` and `helm upgrade` create tracked, numbered releases, and `helm rollback <release> <revision>` reverts to a previous release's exact rendered manifests by revision number — this is a genuinely different recovery mechanism than manually reconstructing what the "last known good" YAML looked like from memory or from scattered git history during an incident, because Helm already has the exact prior state recorded and can reapply it as a single, tested operation. This matters concretely during a bad rollout: if a new image tag causes the order-management or payments service to enter `CrashLoopBackOff` after a `helm upgrade`, `helm rollback` restores the previous working release immediately, buying time to investigate the actual cause without leaving the service down for however long that investigation takes.

IAM Roles for Service Accounts (IRSA), and its newer successor EKS Pod Identity, solve the same least-privilege problem the IAM lesson raised, now applied at the granularity of an individual pod inside a shared cluster rather than an entire EC2 instance. Without IRSA, every pod scheduled onto a given node inherits whatever IAM permissions that node's own instance role has — which means a broad node-level role granting Secrets Manager access for one specific workload's needs is, by default, also available to every other, entirely unrelated pod that happens to land on the same node, a privilege-separation gap that gets worse as a cluster hosts more distinct workloads sharing the same underlying nodes. IRSA/Pod Identity instead lets a specific Kubernetes `ServiceAccount` — used only by the pods of one specific workload — assume a narrowly-scoped IAM role of its own, so the payments service's pods can be granted `secretsmanager:GetSecretValue` on exactly the one Stripe-secret ARN they need, with no other pod on the same node, running a completely different workload, inheriting that same access just because it happens to share a node. This is the direct continuation of the same thread running through this entire module — the IAM lesson's least-privilege reasoning, the AI-safety lesson's tool-scoping argument, the shell-scripting lesson's warning against `chmod 777` — now expressed at the level of "which specific pod, not which node, gets which specific AWS permission."

## Practical Backend Scenario

An FDE deploys the order-management and payments services from Module 2 onto a customer's EKS cluster using a single Helm chart with three separate `values.yaml` files (dev, staging, prod) supplying different replica counts, resource limits, and RDS endpoints per environment — the same chart, parameterized, rather than three near-duplicate manifest sets that would inevitably drift out of sync. Before IRSA is set up, the node group's shared IAM instance role has broad Secrets Manager access (originally granted so the payments pods could reach the Stripe secret), which means every other pod scheduled onto those same nodes — including a completely unrelated internal reporting workload the customer's own team runs on the same cluster — can technically call `GetSecretValue` on that same ARN too, an access gap nobody had actually intended or reviewed. The FDE creates a dedicated `ServiceAccount` used only by the payments deployment, configures IRSA so that service account can assume a role scoped to exactly the Stripe-secret ARN, and removes the broad Secrets Manager grant from the node's own instance role — closing the gap without touching anything about how the reporting workload itself runs. Weeks later, a `helm upgrade` deploying a new payments image tag triggers `CrashLoopBackOff` across all replicas; rather than debugging live in production under pressure, the FDE runs `helm rollback payments 4` to restore the last known-good release immediately, restoring service within minutes, and only then investigates the new image's actual defect against a now-stable, non-production-impacting baseline.

## Practice Loop

1. Write out, precisely, what AWS manages versus what the customer/FDE manages for a traditionally-managed EKS node group, then do the same for a cluster running in Auto Mode, and name exactly what shifted between the two.
2. Package a small service as a Helm chart with a `values.yaml` exposing at least replica count and one environment-specific configuration value, and deploy it with two different values files representing two environments.
3. Deploy a version, then deliberately deploy a broken image tag via `helm upgrade` that causes `CrashLoopBackOff`, and use `helm rollback` to restore the previous working release — time how long the rollback itself takes versus how long a from-scratch manual fix would likely take.
4. Set up IRSA (or Pod Identity) for one workload's dedicated ServiceAccount, scoped to exactly one AWS resource ARN, and confirm a different pod on the same node — using its own default node-level permissions — cannot access that same resource.
5. Write a one-paragraph incident-response note explaining why `helm rollback` was the correct first move in the CrashLoopBackOff scenario, rather than attempting to debug and fix forward in production immediately.

## Evidence of Understanding

You can state precisely what AWS manages versus what the customer/FDE manages in EKS, and explain specifically how EKS Auto Mode shifts that boundary rather than eliminating it. You can use a Helm chart's `values.yaml` to deploy the same release consistently across environments, and use `helm rollback` as an actual incident-response tool that restores a known-good state faster than debugging forward under pressure. You can configure IRSA or Pod Identity to scope a specific pod's AWS access to exactly what its own workload needs, and explain why relying on a node's shared IAM role instead leaves every other pod on that node with access it was never meant to have.

## Suggested Extension

Add a Helm chart test (a `helm test` hook) that verifies the payments service can successfully read its Stripe secret via IRSA immediately after a deploy, and explain why catching a broken IRSA configuration through an automated post-deploy test is preferable to discovering it only when the first real payment webhook fails in production.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why the EKS management boundary matters for debugging
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson call knowing the EKS management boundary "the single most important fact to have memorized before debugging a production EKS issue"?

**OPTIONS:**
- [x] A: It tells you where to look first — a control-plane/API-server failure shows up on AWS's own health dashboard and isn't something the customer's team could have misconfigured, while a node, networking, or add-on issue is the customer/FDE's own responsibility to investigate
- [ ] B: EKS technically has no meaningful management boundary; AWS and the customer share identical responsibility for every component
- [ ] C: This boundary only matters for billing purposes, not for actual incident diagnosis
- [ ] D: The management boundary is irrelevant once a cluster has been running for more than a year

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Knowing who owns a given layer directly determines the first diagnostic step during an incident — checking AWS's health dashboard versus investigating the customer's own node/network configuration.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [eks-shared-responsibility, incident-diagnosis]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What EKS Auto Mode actually changes
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does EKS Auto Mode change about the traditional EKS management boundary?

**OPTIONS:**
- [x] A: It shifts more of the stack — Karpenter-based node provisioning, the VPC CNI, EBS CSI, CoreDNS, kube-proxy — into AWS-managed components, meaning AWS operates meaningfully more of the cluster than under a traditionally-managed node group, not that the architecture itself changes
- [ ] B: Auto Mode eliminates the control plane entirely, replacing it with a fully customer-managed API server
- [ ] C: Auto Mode has no effect on which components AWS manages; it only changes billing
- [ ] D: Auto Mode requires the customer to manage node provisioning manually, unlike traditional EKS

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Auto Mode moves the responsibility line, not the underlying architecture — which is exactly why an FDE needs to check which mode a given cluster runs before assuming who owns a failure.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [eks-auto-mode, management-boundary-shift]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why Helm's values.yaml prevents environment drift
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does deploying the same Helm chart with different `values.yaml` files avoid the drift problem that hand-maintained per-environment YAML files have?

**OPTIONS:**
- [x] A: The chart's templates stay identical across environments, with only the specific values (replica count, endpoints, limits) differing per environment file, so there's no separate near-duplicate manifest per environment that could be edited in one place and forgotten in another
- [ ] B: Helm technically prevents any configuration difference between environments, forcing every environment to be identical
- [ ] C: There is no actual difference between Helm charts and hand-maintained YAML; drift happens equally in both approaches
- [ ] D: values.yaml files are automatically synchronized across environments by Helm without any explicit deployment step

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The single-source-of-template design is what closes the drift gap — one chart, several values files, instead of several independently-editable copies of the whole manifest set.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [helm-values-yaml, environment-drift-prevention]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why helm rollback beats manual reconstruction
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why is `helm rollback` a genuinely different recovery mechanism than manually reconstructing the "last known good" YAML from memory or scattered git history?

**OPTIONS:**
- [x] A: Helm already has the exact prior release's rendered manifests recorded by revision number, and can reapply that exact known state as a single, already-tested operation, rather than requiring someone to reconstruct it accurately under incident pressure
- [ ] B: Manual YAML reconstruction is always faster than helm rollback in a real incident
- [ ] C: helm rollback and manual reconstruction produce identical results with identical risk; the difference is purely about which command is typed
- [ ] D: helm rollback only works if the exact same person who performed the original deploy is present to run it

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The reliability gain is specific — the exact prior state already exists and is tracked, removing the risk of misremembering or misreconstructing it during a high-pressure incident.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [helm-rollback, tracked-release-history]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** The risk of a broad node-level IAM role
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Before IRSA was configured in the scenario, why could the customer's unrelated internal reporting workload technically access the payments service's Stripe secret?

**OPTIONS:**
- [x] A: The node's shared IAM instance role had broad Secrets Manager access originally granted for the payments pods, and every pod scheduled onto that same node — including the unrelated reporting workload — inherited that same node-level access by default, regardless of what that pod actually needed
- [ ] B: The reporting workload had been explicitly and deliberately granted access to the Stripe secret by a separate IAM policy
- [ ] C: Kubernetes ServiceAccounts automatically share credentials across every pod in the entire cluster, not just pods on the same node
- [ ] D: This access was never actually possible; the scenario describes a purely hypothetical, unrealistic risk

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is exactly the node-level privilege-separation gap IRSA is designed to close — access granted at the node level is available to every pod scheduled there, not scoped to the specific workload that actually needs it.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [node-level-iam-gap, unintended-access]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What IRSA changed without disrupting the reporting workload
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How did configuring IRSA for the payments deployment close the access gap without affecting how the unrelated reporting workload runs?

**OPTIONS:**
- [x] A: IRSA moved the Secrets Manager permission from the shared node-level role to a dedicated ServiceAccount used only by the payments pods, and the broad grant was removed from the node's own role — the reporting workload's own operation was never touched, only its previously unintended access to a secret it never needed
- [ ] B: IRSA required migrating the reporting workload onto entirely different nodes to isolate it from the payments pods
- [ ] C: IRSA disabled the reporting workload's networking entirely as a side effect of the payments configuration change
- [ ] D: This fix necessarily required redeploying every workload in the cluster, including the reporting workload

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The fix is precisely scoped — it removes an unintended access path for the reporting workload without touching anything about how that workload actually functions.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [irsa-fix-precision, unintended-access-removal]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why rollback before root-cause investigation was the right sequence
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE run `helm rollback` before investigating the new image's actual defect, rather than debugging the CrashLoopBackOff live in production first?

**OPTIONS:**
- [x] A: Restoring service to a known-good state immediately minimizes customer-facing downtime, and the investigation can then happen against a stable, non-production-impacting baseline instead of under the added pressure and risk of debugging a broken deploy that's actively affecting real traffic
- [ ] B: Rolling back first is always unnecessary, since the root cause should always be identified before any recovery action is taken
- [ ] C: helm rollback and root-cause investigation cannot be performed in either order; the sequence in the scenario was arbitrary
- [ ] D: Rolling back destroys all evidence needed to investigate the original defect, making this sequence a mistake

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Restore-first is the standard incident-response sequence for exactly this reason — minimizing customer impact immediately, then investigating without the added pressure of live production impact.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [restore-first-sequence, incident-response-priority]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Connecting IRSA to the module's recurring least-privilege thread
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does IRSA/Pod Identity connect to the least-privilege reasoning established earlier in this module's IAM lesson?

**OPTIONS:**
- [x] A: It's the same minimum-necessary-scope discipline, now applied at pod granularity inside a shared cluster instead of at the level of an entire IAM role or EC2 instance — the specific workload gets exactly the access it needs, not the access every pod sharing its node happens to inherit
- [ ] B: IRSA and the IAM lesson's least-privilege reasoning are unrelated; IRSA is purely a networking feature
- [ ] C: This connection only holds if the pod in question is running on a self-managed EC2 node rather than inside EKS
- [ ] D: IRSA replaces the need for any IAM least-privilege reasoning at the account level entirely
- [ ] E: The connection is coincidental naming overlap with no shared underlying principle

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the module's recurring thread reaching its final, most granular form — the same least-privilege reasoning from Lesson 1's IAM policies, now scoped down to an individual pod's own workload identity.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [irsa-least-privilege-thread, module-wide-connection]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->
