# FDE Phase 23 — Elective: AWS Multi-Region Cloud Deep Dive (Lessons 1-6 of 17)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-23-elective-aws-multi-region-cloud-deep-dive-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `elective-aws-multi-region-cloud-deep-dive` ("AWS Multi-Region
Cloud Deep Dive") — a `SupplementalModuleDefinition`, **the second of three elective modules** now
in scope. This phase is applied fourth in the electives batch, after Phase 20, 21, and 22 (which
together complete the first elective module, `elective-containerization-orchestration`, 17/17).
The ~104-lesson core curriculum is already 100% complete.

This file covers **lessons 1-6 of 17 only** — VPC/networking fundamentals through Lambda/API
Gateway. Two later phases complete the module: Phase 24 covers lessons 7-12 (End-to-End Cloud
Project Day, AWS ECS and ECR Introduction, ECS Fundamentals, EKS Basics, EKS Advanced, EKS Security
and Operations) and Phase 25 covers lessons 13-17 (Microservices on AWS Project, Microservices
Project: Phase 2, AWS Security: Identity and Network, AWS Security: Data and Detection, AWS
Security Hands-on) and completes the module — do not add placeholder content for those 11 lessons
here.

**Overlap note (checked against Module 4, `cloud-devops-infrastructure`, Phases 9-10):** Module 4's
"Serverless & Event-Driven Cloud (Lambda, API Gateway, Step Functions)" lesson already covers the
architectural framing of serverless — cold starts as a cost/latency trade-off, Standard vs Express
Step Functions workflows, and choosing serverless vs a continuously-running container for a given
workload's shape. This phase's Lesson 6 (AWS Lambda and API Gateway) deliberately does not
re-teach that framing. Instead it goes one level more mechanical: the actual `aws apigateway`
resource/method/integration wiring, the Lambda execution-role and resource-based-permission JSON
that makes an API Gateway route callable at all, `--reserved-concurrent-executions` and
`--timeout` as CLI-level configuration, and a concrete idempotency implementation using a
DynamoDB conditional write — mechanics Module 4's lesson assumes rather than demonstrates. Lesson
6 states this differentiation explicitly in its Concepts Covered section.

All six lessons follow one continuous scenario: an FDE engagement for **Lighthouse Freight Co.**,
a regional freight-forwarding company. The deliverable is **ManifestFlow**, a service that ingests
customs manifests (PDF/XML) uploaded by freight brokers, extracts structured shipment data, and
routes it to Lighthouse's dispatch system. The FDE builds ManifestFlow's AWS foundation from a
private VPC up through serverless intake, with a live customer requirement (public ingress, private
processing, a database that must never see direct internet traffic) driving every design decision.

---

# LESSON 1

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-01-aws-vpc-and-networking-basics
lesson_title: "AWS VPC and Networking Basics"
lesson_order: 1

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Intermediate
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Explain why a subnet's 'public' or 'private' status is a route table property, not an inherent attribute of the subnet, and design route tables accordingly."
  - "Distinguish a security group's stateful, instance-level, allow-only model from a network ACL's stateless, subnet-level, allow-and-deny model, and choose correctly between them for a given control."
  - "Design a three-tier subnet layout (public, private-app, private-data) where the database subnet has no route to the internet at all, and verify that with a live permitted and denied flow."

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
# AWS VPC and Networking Basics

## Concepts Covered

A VPC is a logically isolated slice of AWS network address space, scoped to one AWS Region and
carved into one or more CIDR blocks you choose (`10.20.0.0/16`, for instance, gives you 65,536
addresses to subdivide). A subnet inherits a portion of that CIDR range and is pinned to exactly
one Availability Zone — this is why a highly-available design always needs at least two subnets
per tier, one per AZ, not one subnet that somehow "spans" two AZs. The critical mental model to
get right, because almost every misconfiguration traces back to getting it wrong, is that "public
subnet" and "private subnet" are not properties AWS assigns to a subnet — they are just the names
engineers give to a subnet based on what its **route table** does. A subnet becomes "public" the
moment its route table has a route sending `0.0.0.0/0` traffic to an Internet Gateway (IGW); a
subnet is "private" simply because its route table has no such route. Two subnets with identical
CIDR ranges, security groups, and instances are public or private based purely on which route
table is associated with them — you can make a subnet private by detaching the IGW route, with
zero changes to anything running inside it.

Reachability then layers two independent controls on top of routing. A security group is
stateful, attached to individual resources (an EC2 instance's network interface, an RDS instance,
a Lambda function's ENI), and can only allow traffic — there is no explicit deny rule, only the
implicit deny of "not listed." Statefulness means a security group rule permitting inbound port
443 automatically permits the corresponding outbound response traffic without a matching outbound
rule. A network ACL (NACL) is the opposite in every respect: stateless (you must write both
inbound and outbound rules explicitly, including for return traffic), evaluated at the subnet
boundary rather than per-resource, and capable of explicit `DENY` rules evaluated in numbered
order until the first match. This makes NACLs the right tool for a coarse, subnet-wide block (an
IP range you never want touching this subnet at all, regardless of what security group any
individual instance carries) and security groups the right tool for fine-grained, per-service
"as-strict-as-actually-needed" rules — using a NACL for fine-grained allow rules is unnecessarily
brittle because of the statelessness tax, and relying on a security group alone to block a known-bad
CIDR range subnet-wide means auditing every resource's security group individually rather than one
subnet-level rule. A NAT Gateway, finally, is the asymmetric-access primitive: it lives in a public
subnet and lets private-subnet resources initiate outbound connections (to pull an OS update, call
an external API) while remaining completely unreachable for anything initiating a connection
inbound from the internet — the private subnet's route table sends `0.0.0.0/0` to the NAT Gateway,
not to the IGW directly, which is the mechanical reason a NAT Gateway subnet is never itself called
"private."

```bash
# Create the VPC and a public/private subnet pair in one AZ
aws ec2 create-vpc --cidr-block 10.20.0.0/16 --tag-specifications \
  'ResourceType=vpc,Tags=[{Key=Name,Value=manifestflow-vpc}]'
# -> Vpc: { "VpcId": "vpc-0a1b2c3d4e5f60789", "CidrBlock": "10.20.0.0/16" }

aws ec2 create-subnet --vpc-id vpc-0a1b2c3d4e5f60789 \
  --cidr-block 10.20.0.0/24 --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-1a}]'
aws ec2 create-subnet --vpc-id vpc-0a1b2c3d4e5f60789 \
  --cidr-block 10.20.10.0/24 --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-app-1a}]'
aws ec2 create-subnet --vpc-id vpc-0a1b2c3d4e5f60789 \
  --cidr-block 10.20.20.0/24 --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-db-1a}]'

# Attach an IGW and route ONLY the public subnet's table to it
aws ec2 create-internet-gateway --tag-specifications \
  'ResourceType=internet-gateway,Tags=[{Key=Name,Value=manifestflow-igw}]'
aws ec2 attach-internet-gateway --internet-gateway-id igw-0d4f5a6b --vpc-id vpc-0a1b2c3d4e5f60789
aws ec2 create-route --route-table-id rtb-public-1a \
  --destination-cidr-block 0.0.0.0/0 --gateway-id igw-0d4f5a6b

# private-db-1a's route table has NO 0.0.0.0/0 route of any kind — verify it
aws ec2 describe-route-tables --route-table-ids rtb-private-db-1a \
  --query 'RouteTables[0].Routes[].DestinationCidrBlock'
# -> [ "10.20.0.0/16" ]   <-- local VPC traffic only, no internet route at all
```

## Practical Backend Scenario

ManifestFlow needs three reachability tiers inside one VPC: an Application Load Balancer in a
public subnet that accepts broker uploads over HTTPS from the internet, extraction workers in a
private-app subnet that call out to Amazon Textract and an internal API but must never accept a
direct inbound connection from the internet, and an RDS PostgreSQL instance in a private-data
subnet that must be unreachable from the internet under every circumstance, including a
misconfigured security group on the workers. The security group on the workers allows outbound
443 to Textract's VPC endpoint and inbound 8080 only from the ALB's security group by reference
(not by CIDR) — so redeploying the ALB with a new IP never requires touching the worker's rule. The
database subnet's route table carries no route to the IGW or the NAT Gateway at all, which means
even a security group misconfiguration that opened port 5432 to `0.0.0.0/0` would still fail,
because there is no path for that traffic to arrive from the internet in the first place — the
route table is the backstop, not the security group.

## Practice Loop

1. Draw the packet path for a broker's HTTPS upload from their laptop to the RDS instance,
   labeling every hop (IGW, ALB, worker ENI, RDS ENI) and which route table governs each leg.
2. Create the three-subnet layout in a sandbox VPC using the CLI commands above, associating each
   subnet with a distinct route table rather than reusing the VPC's main route table for all three.
3. Run `aws ec2 describe-route-tables` against the private-data subnet's route table and count how
   many `0.0.0.0/0`-reaching routes exist — the diagnostic answer must be zero before you proceed.
4. Test one permitted flow (worker security group to RDS security group on port 5432, referenced
   by security-group ID, not CIDR) and one denied flow (attempt a direct connection to the RDS
   instance's private IP from an EC2 instance in the public subnet with no matching security group
   rule) and capture the connection timeout as your evidence of denial.
5. Review the security group rules and note every rule that references a CIDR block instead of a
   peer security group ID, and rewrite each one to reference the security group instead, since a
   CIDR-based rule silently stops matching the moment the peer's IP changes.

## Evidence of Understanding

You can explain that "public" and "private" describe a subnet's route table, not an inherent
property of the subnet itself, and can make any subnet private by removing its IGW route without
touching a single instance inside it. You can choose correctly between a stateful, per-resource
security group and a stateless, subnet-wide NACL for a given control, and explain why relying on a
security group alone for a subnet-wide block requires auditing every resource individually. You
can design a database subnet whose route table has no path to the internet at all, and demonstrate
that this backstop holds even against a security group misconfiguration.

## Suggested Extension

Add a fourth subnet tier for a bastion host used only for emergency database access, restrict its
security group to a specific corporate IP range, and explain why routing the RDS security group's
inbound rule to the bastion's security group ID (not the bastion's current public IP) keeps the
rule valid even if the bastion is replaced.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What makes a subnet "public"
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what actually determines whether a subnet is "public" or "private" in AWS?

**OPTIONS:**
- [ ] A: A flag set on the subnet resource itself at creation time
- [x] B: Whether the subnet's associated route table has a `0.0.0.0/0` route pointing to an Internet Gateway
- [ ] C: Whether the subnet's CIDR block falls within a specific reserved range
- [ ] D: Whether any instance inside the subnet has a public IP address assigned

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1
**EXPLANATION:**
The lesson is explicit that "public" and "private" are just names for what a subnet's route table does — the presence or absence of an IGW-bound default route — not an inherent subnet property.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [route-table, public-subnet, private-subnet]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Security group vs NACL statefulness
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A security group allows inbound port 443 with no matching outbound rule, and response traffic still flows correctly. A NACL allowing the same inbound port 443 blocks response traffic unless a matching outbound rule is also added. What explains this difference?

**OPTIONS:**
- [x] A: Security groups are stateful (a permitted inbound request auto-allows its response); NACLs are stateless (inbound and outbound must each be explicitly allowed)
- [ ] B: NACLs are a deprecated feature that no longer evaluates outbound traffic correctly
- [ ] C: Security groups only apply to TCP while NACLs apply to all protocols
- [ ] D: The difference is a bug specific to port 443 and does not generalize to other ports

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is the lesson's core statefulness distinction — security groups track connection state and auto-permit responses, NACLs evaluate every direction independently.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [security-group, nacl, statefulness]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the route table diagnostic
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ aws ec2 describe-route-tables --route-table-ids rtb-private-db-1a \
  --query 'RouteTables[0].Routes[].DestinationCidrBlock'
[ "10.20.0.0/16" ]
```

**QUESTION_TEXT:**
Given this output for the private-data subnet's route table, what can you conclude about its reachability from the internet?

**OPTIONS:**
- [x] A: No traffic from the internet can reach resources in this subnet through this route table, since the only route is to the local VPC CIDR
- [ ] B: The subnet is reachable from the internet as long as a security group allows it
- [ ] C: This output is inconclusive without also checking the subnet's NACL
- [ ] D: This route table proves a NAT Gateway is attached to this subnet

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
With only a local VPC route and no `0.0.0.0/0` route of any kind (IGW or NAT), there is no path for internet traffic to arrive at all — this is the route-table backstop the lesson describes.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [route-table, cli-diagnostic, database-isolation]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** NAT Gateway asymmetric access
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A worker in a private subnet needs to call Amazon Textract's public API but must never accept an inbound connection initiated from the internet. What AWS component provides exactly this asymmetric behavior?

**OPTIONS:**
- [ ] A: An Internet Gateway attached directly to the private subnet's route table
- [x] B: A NAT Gateway in a public subnet, with the private subnet's route table sending `0.0.0.0/0` traffic to it
- [ ] C: A network ACL with an explicit deny rule for all inbound traffic
- [ ] D: A security group rule allowing outbound 443 with no other component involved

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1
**EXPLANATION:**
The lesson names the NAT Gateway specifically as the asymmetric-access primitive — outbound-initiated connections succeed, inbound-initiated connections from the internet cannot reach the private subnet through it at all.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [nat-gateway, asymmetric-access, outbound-only]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the worker's security group references the ALB by ID
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The scenario has the worker's security group allow inbound 8080 from the ALB's security group by reference, not by CIDR. Why does this matter operationally?

**OPTIONS:**
- [x] A: A security-group reference stays valid automatically if the ALB is redeployed with a new IP, while a CIDR-based rule would silently stop matching
- [ ] B: Referencing a security group by ID is required by AWS and CIDR-based rules are not permitted between two AWS resources
- [ ] C: It has no operational effect; both approaches behave identically in every case
- [ ] D: It makes the rule stateless instead of stateful
- [ ] E: It reduces the AWS bill for the ALB
- [ ] F: It's only relevant if the ALB spans more than one Availability Zone

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Referencing a peer security group by ID tracks the peer's actual current membership; a hardcoded CIDR rule breaks the moment that peer's address changes, which the Practice Loop's diagnostic step is built to surface.
**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [security-group-reference, cidr-brittleness]
### QUESTION_BLOCK_END: Q5
<!-- NOTE: draft above had 6 options by mistake — corrected block below is authoritative -->
### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the worker's security group references the ALB by ID
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The scenario has the worker's security group allow inbound 8080 from the ALB's security group by reference, not by CIDR. Why does this matter operationally?

**OPTIONS:**
- [x] A: A security-group reference stays valid automatically if the ALB is redeployed with a new IP, while a CIDR-based rule would silently stop matching
- [ ] B: Referencing a security group by ID is required by AWS; CIDR-based rules are not permitted between two AWS resources
- [ ] C: It has no operational effect; both approaches behave identically in every case
- [ ] D: It makes the rule stateless instead of stateful

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Referencing a peer security group by ID tracks the peer's actual current membership; a hardcoded CIDR rule breaks the moment that peer's address changes, which the Practice Loop's diagnostic step is built to surface.
**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [security-group-reference, cidr-brittleness]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Subnets and Availability Zones
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does a highly-available design need at least two subnets per tier (public, private-app, private-data), rather than one subnet per tier?

**OPTIONS:**
- [x] A: A subnet is pinned to exactly one Availability Zone, so surviving the loss of one AZ requires a second subnet in a second AZ for each tier
- [ ] B: AWS enforces a maximum of 256 addresses per subnet, requiring a second subnet for capacity
- [ ] C: Route tables can only be associated with one subnet at a time across the entire VPC
- [ ] D: Security groups require at least two subnets to function correctly

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states plainly that a subnet is pinned to one AZ — a single subnet cannot "span" two AZs, so AZ-level resilience requires a subnet pair, not a single wider subnet.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [availability-zone, subnet-scope, high-availability]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** When a NACL is the right tool
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A known-malicious IP range needs to be blocked from every resource in a subnet, regardless of which security group any individual resource carries. Per the lesson, which control is the right tool for this, and why?

**OPTIONS:**
- [x] A: A NACL explicit deny rule at the subnet boundary, since it applies to every resource in the subnet in one place rather than requiring an audit of each resource's security group individually
- [ ] B: A security group deny rule, since security groups support explicit denies unlike NACLs
- [ ] C: There is no AWS-native way to block a CIDR range subnet-wide; this requires a third-party firewall
- [ ] D: An IGW route removal, since that is the only way to block a specific CIDR range

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this exact case — a coarse, subnet-wide block — as where a NACL's explicit deny at the subnet boundary beats relying on individually auditing every resource's security group.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [nacl, explicit-deny, subnet-wide-block]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** The denied-flow test
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practice Loop's denied-flow test, an EC2 instance in the public subnet attempts a direct connection to the RDS instance's private IP and the connection times out. What does the timeout (rather than an immediate "connection refused") most likely indicate?

**OPTIONS:**
- [x] A: There is no matching security group rule allowing the traffic, so packets are silently dropped rather than actively rejected
- [ ] B: The RDS instance is not running
- [ ] C: The route table has no route to the RDS subnet's CIDR at all, so the packet cannot leave the public subnet
- [ ] D: A NACL is actively sending a TCP RST packet back to the sender

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Both hosts share the same VPC CIDR, so the route exists; a security group without a matching allow rule drops the packet silently, producing a timeout rather than an explicit rejection — this is the expected signature of a security-group-level denial.
**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [connection-timeout, security-group-denial, diagnostic-signature]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 2

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-02-advanced-aws-networking
lesson_title: "Advanced AWS Networking"
lesson_order: 2

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Choose between VPC peering and Transit Gateway for a multi-VPC connectivity requirement based on the number of VPCs involved and the transitive-routing limitation of peering."
  - "Expose a private service to another AWS account using a PrivateLink interface endpoint without opening broad CIDR-based network access."
  - "Configure a Route 53 failover routing policy backed by a health check, and verify the failover behavior by forcing the health check to fail."

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
# Advanced AWS Networking

## Concepts Covered

VPC peering connects exactly two VPCs with a direct, non-transitive route: if VPC A peers with
VPC B, and VPC B peers with VPC C, traffic from A cannot reach C through B — each pair needs its
own explicit peering connection and its own route table entries on both sides. This is fine for two
or three VPCs, but the number of connections in a full mesh grows as `n(n-1)/2`, so ten VPCs
needing full connectivity require 45 separate peering connections, each with its own route table
maintenance. Transit Gateway solves this by acting as a regional routing hub: each VPC attaches
once to the Transit Gateway, and the Transit Gateway's own route table decides which attachments
can reach which — turning an `n(n-1)/2` peering mesh into `n` attachments, and centralizing the
routing policy (which VPC can reach which) in one place instead of scattering it across every
VPC's own route table. Transit Gateway also supports inter-region peering between two Transit
Gateways, which is the primitive that makes a genuinely multi-region network topology manageable
rather than a hand-wired mesh of point-to-point VPC peering connections across regions.

PrivateLink solves a different problem: exposing one specific service to another VPC or another
AWS account without exposing network-level reachability to anything else in either VPC. A
PrivateLink interface endpoint places an elastic network interface, with its own private IP, inside
the consumer's VPC; that ENI forwards traffic to the provider's service over AWS's internal
network, never crossing the public internet and never requiring the consumer's VPC to be peered,
routed, or CIDR-reachable to the provider's VPC at all. This is the correct tool specifically when
the requirement is "let this one service be called," not "let these two networks talk" — VPC
peering or Transit Gateway grants broad network reachability (anything in VPC A can potentially
reach anything in VPC B, gated only by security groups and NACLs), while PrivateLink grants
reachability to exactly one named service and nothing else, which matters enormously when the
consumer is a different company's AWS account and you do not want to trust their network
hygiene. Route 53 routing policies then decide, at the DNS layer, which endpoint a client resolves
to at all: a failover policy pairs a primary and secondary record with a health check, returning
the primary's IP while its health check passes and switching to the secondary the moment it fails;
a latency-based policy resolves to whichever region's endpoint has the lowest measured latency from
the resolving location; a weighted policy splits traffic by percentage for canary rollouts. Because
DNS resolvers cache aggressively, a low TTL on the record is what actually determines how quickly a
failover becomes visible to clients — a failover policy with a 3600-second TTL will still route
some fraction of clients to a dead endpoint for up to an hour after the health check fails.

```bash
# Attach ManifestFlow's VPC to a Transit Gateway shared with Lighthouse's shared-services VPC
aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id tgw-0f1e2d3c4b5a69870 \
  --vpc-id vpc-0a1b2c3d4e5f60789 \
  --subnet-ids subnet-0priv1 subnet-0priv2

# Create a PrivateLink endpoint service fronting ManifestFlow's internal broker API (NLB-backed)
aws ec2 create-vpc-endpoint-service-configuration \
  --network-load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:111122223333:loadbalancer/net/manifestflow-nlb/abc123 \
  --acceptance-required
# -> ServiceId: vpce-svc-0d5e6f7a8b9c0d1e2

# The customs-broker partner's account then creates the consumer-side interface endpoint:
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-partner-0011 --service-name com.amazonaws.vpce.us-east-1.vpce-svc-0d5e6f7a8b9c0d1e2 \
  --vpc-endpoint-type Interface --subnet-ids subnet-partner-1

# Route 53 failover: primary us-east-1 ALB, secondary us-west-2 ALB, gated by a health check
aws route53 create-health-check --caller-reference manifestflow-primary-hc-2026 \
  --health-check-config Type=HTTPS,ResourcePath=/health,FullyQualifiedDomainName=api.manifestflow.io,Port=443
aws route53 change-resource-record-sets --hosted-zone-id Z1D633PJN98FT9 \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.manifestflow.io", "Type": "A", "SetIdentifier": "primary-us-east-1",
        "Failover": "PRIMARY", "TTL": 30, "HealthCheckId": "a1b2c3d4-hc-primary",
        "ResourceRecords": [{"Value": "203.0.113.10"}]
      }
    }]
  }'
```

## Practical Backend Scenario

Lighthouse's shared-services VPC (holding an internal identity provider and a logging pipeline)
needs to reach ManifestFlow's private subnets without a full mesh of point-to-point peering as more
service VPCs get added later, so the FDE attaches both to a Transit Gateway and writes the TGW
route table to allow ManifestFlow to reach shared-services but not the reverse, since ManifestFlow
never needs to initiate a connection into shared-services. Separately, a customs-broker partner
needs to call ManifestFlow's internal broker-status API from their own AWS account, but Lighthouse's
security team will not approve any VPC peering or CIDR-based access into a partner's network they
do not control — so the FDE exposes only that one API through a PrivateLink endpoint service,
which the partner's own VPC endpoint reaches without any broader network path existing between the
two accounts at all. For disaster recovery, ManifestFlow is deployed to both `us-east-1` (primary)
and `us-west-2` (secondary, kept warm but not serving traffic), with a Route 53 failover record
whose health check polls `/health` on the primary ALB every 30 seconds and switches DNS resolution
to the secondary region after three consecutive failures.

## Practice Loop

1. Model the connectivity requirement as a small graph (which VPCs must reach which) and decide,
   using the peering-mesh-growth argument, whether VPC peering or Transit Gateway fits — justify
   the choice with the actual number of VPCs involved, not a default preference.
2. Write the Transit Gateway route table entries that let ManifestFlow reach shared-services but
   not the reverse, and state which specific route's absence enforces the one-way restriction.
3. Compare the blast radius of a PrivateLink endpoint (one named service reachable) against a VPC
   peering connection (broad network reachability gated only by security groups) for the
   customs-broker integration, and count how many additional resources the partner could reach
   under each option if a security group were ever misconfigured.
4. Create the Route 53 health check and failover record set from the CLI above, then intentionally
   fail the health check (stop the primary ALB's target group) and time how long DNS resolution
   takes to return the secondary region's IP, comparing that to the record's configured TTL.
5. Document the one-way TGW route table entry and the PrivateLink endpoint service's
   `--acceptance-required` flag as the two access decisions a security reviewer should check first,
   since both directly bound blast radius rather than relying on downstream security groups alone.

## Evidence of Understanding

You can choose between VPC peering and Transit Gateway for a given number of VPCs, justified by
peering's non-transitive routing and the `n(n-1)/2` mesh-growth problem it creates at scale. You
can expose one specific service to an external AWS account through a PrivateLink interface
endpoint and explain why its blast radius is smaller than a VPC peering connection granting the
same functional access. You can configure and verify a Route 53 failover policy, including why the
record's TTL — not just the health check interval — determines how quickly a failover becomes
visible to real clients.

## Suggested Extension

Add a second PrivateLink endpoint service for a different partner's read-only reporting API, set
`--acceptance-required` so each partner's endpoint connection request must be manually approved,
and write the one-sentence justification for why manual acceptance matters more here than it does
for the Transit Gateway attachment between Lighthouse's own two VPCs.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why peering doesn't scale past a few VPCs
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend Transit Gateway over VPC peering once more than a handful of VPCs need to interconnect?

**OPTIONS:**
- [x] A: Peering is non-transitive and requires its own connection per pair, so full connectivity among n VPCs needs n(n-1)/2 peering connections, while Transit Gateway needs only n attachments
- [ ] B: VPC peering connections expire automatically after 90 days and must be recreated
- [ ] C: AWS technically limits any VPC to a maximum of two peering connections
- [ ] D: Peering connections cannot carry HTTPS traffic, only HTTP

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson gives the exact mesh-growth math — n(n-1)/2 pairwise peering connections versus n Transit Gateway attachments — as the reason peering stops scaling.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [vpc-peering, transit-gateway, mesh-growth]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Peering's transitive-routing limitation
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
VPC A peers with VPC B, and VPC B peers with VPC C. Can traffic from VPC A reach VPC C through VPC B using only these two peering connections?

**OPTIONS:**
- [ ] A: Yes, peering connections automatically chain transitively
- [x] B: No, peering is non-transitive — A and C would need their own direct peering connection
- [ ] C: Yes, but only if all three VPCs are in the same Availability Zone
- [ ] D: No, because peering connections can only exist between VPCs in different AWS accounts

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1
**EXPLANATION:**
The lesson states this directly as the core limitation of peering — no transitive routing through an intermediate VPC, regardless of how many pairwise connections exist.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [transitive-routing, vpc-peering-limitation]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** PrivateLink vs peering blast radius
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Lighthouse's security team refuses to approve VPC peering with an external partner's account but does approve a PrivateLink endpoint service for one specific API. What is the core reason PrivateLink is the lower-risk option here?

**OPTIONS:**
- [x] A: PrivateLink grants reachability to exactly one named service, while peering grants broad network reachability across both VPCs gated only by security groups and NACLs
- [ ] B: PrivateLink connections are encrypted while peering connections are not
- [ ] C: PrivateLink is only usable within a single AWS account, so external partners cannot use it at all
- [ ] D: Peering connections require the partner to share their entire VPC CIDR block publicly

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's central distinction is scope of access: PrivateLink exposes one service, peering exposes a network path that anything in either VPC could reach if security groups were ever misconfigured.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [privatelink, blast-radius, cross-account-access]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What a PrivateLink interface endpoint actually is
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Mechanically, what does creating a PrivateLink interface endpoint place inside the consumer's VPC?

**OPTIONS:**
- [x] A: An elastic network interface with its own private IP, which forwards traffic to the provider's service over AWS's internal network
- [ ] B: A new route table entry pointing to the public internet
- [ ] C: A full copy of the provider's VPC, replicated into the consumer's account
- [ ] D: A NAT Gateway dedicated to the provider's traffic

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson describes the endpoint as an ENI with its own private IP forwarding over AWS's internal network — never touching the public internet and never requiring VPC-level peering or routing.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [privatelink, interface-endpoint, eni]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What actually gates failover visibility
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A Route 53 failover record's health check fails and switches immediately at the DNS layer. Some clients still resolve to the dead primary endpoint for up to an hour afterward. What most likely explains this?

**OPTIONS:**
- [x] A: The record's TTL is set high (e.g., 3600 seconds), so resolvers that already cached the primary's answer will not re-query Route 53 until that TTL expires
- [ ] B: Route 53 failover records do not actually take effect until the next AWS billing cycle
- [ ] C: The health check itself was misconfigured to check the wrong path
- [ ] D: Failover records only work for weighted routing policies, not for failover policies

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson makes this explicit: DNS caching means the record's TTL, not the health check's own responsiveness, determines how quickly failover becomes visible to clients that already cached an answer.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [dns-ttl, route53-failover, caching]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** One-way TGW routing
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The FDE wants ManifestFlow to reach Lighthouse's shared-services VPC through the Transit Gateway, but not the reverse. How is this one-way restriction actually enforced?

**OPTIONS:**
- [x] A: By omitting the route in the Transit Gateway route table that would let shared-services' attachment reach ManifestFlow's attachment, while including the reverse route
- [ ] B: By setting a "one-way" flag on the Transit Gateway attachment itself
- [ ] C: This cannot be enforced at the Transit Gateway level; it requires a security group change in shared-services instead
- [ ] D: By using a NACL on ManifestFlow's subnet to block all inbound traffic from the Transit Gateway

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Transit Gateway routing is controlled entirely by which routes exist in its own route table per attachment — omitting the reverse route is what enforces the one-way access, exactly as the lesson's Practice Loop step 2 asks the learner to state.
**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [transit-gateway-route-table, one-way-access]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Route 53 routing policy for a canary rollout
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Which Route 53 routing policy is designed specifically for splitting a percentage of traffic to a new endpoint for a canary rollout, per the lesson?

**OPTIONS:**
- [ ] A: Failover routing
- [ ] B: Latency-based routing
- [x] C: Weighted routing
- [ ] D: Geolocation routing

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2
**EXPLANATION:**
The lesson names weighted routing specifically as the policy that splits traffic by percentage, which is exactly the canary-rollout use case.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [route53, weighted-routing, canary]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** `--acceptance-required` on the endpoint service
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
aws ec2 create-vpc-endpoint-service-configuration \
  --network-load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:111122223333:loadbalancer/net/manifestflow-nlb/abc123 \
  --acceptance-required
```

**QUESTION_TEXT:**
What does the `--acceptance-required` flag on this PrivateLink endpoint service configuration accomplish?

**OPTIONS:**
- [x] A: Any consumer's request to create an interface endpoint connecting to this service must be manually approved before traffic can flow
- [ ] B: It requires the consumer to accept a legal terms-of-service agreement before the API returns a response
- [ ] C: It forces the connection to use mutual TLS instead of standard TLS
- [ ] D: It has no functional effect and is purely cosmetic metadata

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`--acceptance-required` gates every consumer's endpoint connection behind manual approval by the service owner — the specific control the Suggested Extension asks the learner to reason about for a second partner integration.
**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [privatelink, acceptance-required, endpoint-service]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 3

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-03-aws-observability-with-cloudwatch
lesson_title: "AWS Observability with CloudWatch"
lesson_order: 3

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Intermediate
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Define a journey-level SLI (not a per-service metric) for a multi-step workflow and identify which individual metric a customer-visible symptom actually maps to."
  - "Distinguish a metric's average from its percentile distribution and explain why an average can hide a backlog or a single unhealthy AZ."
  - "Write a CloudWatch Logs Insights query and a metric-filter-backed alarm that surfaces a specific failure signature rather than a generic error count."

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
# AWS Observability with CloudWatch

## Concepts Covered

A CloudWatch metric is a time-ordered sequence of data points identified by a namespace, a metric
name, and a set of dimensions — key-value pairs that let you slice the same metric name by, for
example, which Availability Zone or which queue produced it. This dimensional slicing matters more
than the metric name itself for diagnosing a real incident: `Duration` on a Lambda function
aggregated across all invocations tells you the overall average, but `Duration` filtered by the
`FunctionName` and further correlated against which AZ the underlying execution environment ran in
can reveal that one AZ's invocations are consistently slower while the aggregate hides it entirely,
because an average is a single number computed across every data point regardless of how unevenly
they are distributed. This is why a percentile (p50, p90, p99) is a fundamentally different, and
usually more useful, statistic than an average for latency: p50 tells you what a typical request
experiences, while p99 tells you what your worst-served one-in-a-hundred requests experience — and
a workflow with a healthy average and a terrible p99 is exactly the "some customers are having a
bad time and the dashboard looks fine" scenario an FDE gets paged for. CloudWatch Logs organizes
application log output into log groups and log streams, and a metric filter turns a pattern match
against incoming log lines into a CloudWatch metric in real time — for instance, counting every
line matching `[ERROR] extraction_failed` as they arrive, without the application code needing to
publish a custom metric explicitly for that condition.

An alarm watches one metric (or a math expression combining several) against a threshold over an
evaluation window, and transitions between `OK`, `ALARM`, and `INSUFFICIENT_DATA` states, each of
which can trigger an SNS notification or an Auto Scaling action. The judgment that separates a
useful alarm from a noisy one is choosing a threshold and evaluation period that reflects an actual
customer-impacting condition rather than a number that merely differs from normal — an alarm on
"CPU above 70%" is a resource-utilization signal, not a customer-impact signal, and firing it
during a legitimate traffic spike that customers are experiencing perfectly fine service through
trains the on-call engineer to ignore the alarm. A dashboard should be built around a **service-level
indicator (SLI)** defined at the level of the customer's actual journey, not at the level of any
one AWS resource's internal metric: "manifest processing completes within 60 seconds of upload,
p90" is an SLI; "SQS `ApproximateNumberOfMessagesVisible`" is a component metric that might explain
a violation of that SLI but is not itself the thing the customer experiences. Embedded Metric
Format (EMF) lets application code emit a metric as a specially structured JSON log line — written
once to stdout, ingested by the CloudWatch agent, and automatically extracted into both a metric
and a searchable log entry — which avoids the extra network call and API rate limit exposure of
calling `PutMetricData` directly from inside a hot request path.

```bash
# Publish a custom metric for queue depth, tagged with the AZ it was measured from
aws cloudwatch put-metric-data --namespace ManifestFlow/Processing \
  --metric-name QueueBacklogDepth --dimensions AvailabilityZone=us-east-1b \
  --value 842 --unit Count

# Create a metric filter that turns a log pattern into a real-time metric
aws logs put-metric-filter --log-group-name /manifestflow/extraction-worker \
  --filter-name ExtractionFailures \
  --filter-pattern '[ts, level=ERROR, msg="extraction_failed*"]' \
  --metric-transformations \
    metricName=ExtractionFailureCount,metricNamespace=ManifestFlow/Processing,metricValue=1,defaultValue=0

# Alarm on the p90 of end-to-end processing latency, not the average
aws cloudwatch put-metric-alarm --alarm-name manifestflow-p90-processing-latency \
  --namespace ManifestFlow/Processing --metric-name ProcessingLatencyMs \
  --statistic p90 --period 300 --evaluation-periods 3 \
  --threshold 60000 --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:111122223333:manifestflow-oncall

# CloudWatch Logs Insights: correlate a slow request to its dependency chain
```
```sql
fields @timestamp, requestId, dependency, latencyMs
| filter @message like /extraction_failed/
| stats count(*) as failures by dependency, bin(5m)
| sort failures desc
```

## Practical Backend Scenario

Lighthouse reports that document processing "feels slow sometimes," but ManifestFlow's dashboard
shows average processing latency holding steady at 8 seconds — well under the 60-second SLI target.
The FDE defines the SLI properly first: "a manifest upload completes extraction and routing within
60 seconds, p90" — a journey-level statement, not a per-resource metric — and immediately finds
that the p90 (not the average) is 74 seconds and climbing. Correlating `QueueBacklogDepth` by
`AvailabilityZone` dimension shows the backlog is concentrated in `us-east-1b`: two of the six
extraction workers, both in that AZ, have been silently failing their health checks and not
processing any messages for the last forty minutes, while workers in `us-east-1a` pick up slack and
keep the average looking fine. The average masked exactly the kind of localized failure a p90 and a
per-AZ dimension breakdown reveal immediately.

## Practice Loop

1. Define the SLI at the customer-journey level ("manifest processing completes within 60 seconds
   of upload, p90") rather than naming any single AWS resource's metric.
2. Publish `QueueBacklogDepth` and `ProcessingLatencyMs` as custom metrics, each dimensioned by
   Availability Zone, from the extraction worker code.
3. Query the p90 (not the average) of `ProcessingLatencyMs` over the last hour, broken down by AZ
   dimension, and identify exactly which AZ's workers are behind — this measurement step is what
   makes the symptom-vs-cause gap visible rather than assumed.
4. Build the alarm from the CLI above on the p90 threshold, and separately build a metric filter
   and alarm on the `ExtractionFailures` log pattern, so a failing worker and a growing backlog
   surface as two distinct signals rather than one blended one.
5. Trace one specific slow request's `requestId` through the Logs Insights query above to its
   exact failing dependency, and write one sentence distinguishing the symptom (slow processing),
   the cause (two unhealthy `us-east-1b` workers), the threshold (60s p90), and the customer impact
   (a subset of uploads delayed, not all of them).

## Evidence of Understanding

You can define an SLI at the level of a customer's actual journey rather than at the level of a
single AWS resource's internal metric, and can name a specific case where an average latency figure
hides a real, customer-visible problem that a percentile reveals. You can build a metric filter
that turns a specific log pattern into a real-time CloudWatch metric, and an alarm whose threshold
reflects a customer-impacting condition rather than a number merely different from baseline. You can
trace one slow request through CloudWatch Logs Insights to its specific failing dependency and
state, precisely, the difference between the symptom, the cause, the threshold, and the customer
impact.

## Suggested Extension

Add a composite alarm that only fires when both the `ExtractionFailures` metric filter alarm and
the p90 latency alarm are simultaneously in `ALARM` state, and explain why this composite reduces
false-positive pages compared to either alarm firing independently for a transient, self-recovering
blip.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why an SLI must be journey-level
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why is "manifest processing completes within 60 seconds of upload, p90" a better SLI than "SQS ApproximateNumberOfMessagesVisible"?

**OPTIONS:**
- [x] A: The first is defined at the level of the customer's actual journey; the second is a component metric that might explain a violation of the first but is not itself what the customer experiences
- [ ] B: SQS metrics are less accurate than custom application metrics
- [ ] C: ApproximateNumberOfMessagesVisible cannot be graphed on a CloudWatch dashboard
- [ ] D: The two metrics measure identical things, so there is no meaningful difference

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson draws this exact distinction — an SLI belongs at the customer-journey level; a queue depth metric is a component signal that may explain, but is not equivalent to, that journey's actual outcome.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [sli, journey-level-metric, component-metric]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why the average hid the problem
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, average processing latency looked healthy at 8 seconds while p90 was 74 seconds and climbing. What explains this gap?

**OPTIONS:**
- [x] A: A localized failure (two workers in one AZ not processing messages) affected only a subset of requests; healthy workers in the other AZ picked up the slack, keeping the average low while the affected subset's latency, visible only in the tail percentile, kept climbing
- [ ] B: CloudWatch computes averages and percentiles from entirely different, unrelated data sources
- [ ] C: The average metric was simply misconfigured with the wrong unit
- [ ] D: Percentiles are always higher than averages by mathematical definition, regardless of the underlying data

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is the lesson's central diagnostic point: a localized, minority-affecting failure is exactly what an average can mask while a tail percentile like p90 reveals, because the average blends unaffected requests in with the affected ones.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [average-vs-percentile, localized-failure, tail-latency]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What a metric filter does
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
aws logs put-metric-filter --log-group-name /manifestflow/extraction-worker \
  --filter-name ExtractionFailures \
  --filter-pattern '[ts, level=ERROR, msg="extraction_failed*"]' \
  --metric-transformations \
    metricName=ExtractionFailureCount,metricNamespace=ManifestFlow/Processing,metricValue=1,defaultValue=0
```

**QUESTION_TEXT:**
What does this metric filter accomplish, without requiring any change to the extraction worker's application code?

**OPTIONS:**
- [x] A: It turns every log line matching the `extraction_failed` pattern, as they arrive in CloudWatch Logs, into a real-time CloudWatch metric that can be alarmed on
- [ ] B: It deletes matching log lines from the log group to save storage costs
- [ ] C: It automatically restarts the extraction worker process whenever a matching line appears
- [ ] D: It requires the application to call `PutMetricData` explicitly whenever this log line is written

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
A metric filter matches an incoming log pattern and produces a metric automatically — the lesson specifically contrasts this with needing the application to publish a custom metric explicitly.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [metric-filter, cloudwatch-logs, real-time-metric]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Choosing a meaningful alarm threshold
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why does an alarm on "CPU above 70%" risk training an on-call engineer to ignore alarms?

**OPTIONS:**
- [x] A: CPU utilization is a resource-utilization signal, not a customer-impact signal — it can fire during a legitimate traffic spike that customers are experiencing perfectly fine service through
- [ ] B: CPU metrics are unreliable and frequently report incorrect values
- [ ] C: 70% is technically below the threshold AWS recommends, so the alarm would never fire in practice
- [ ] D: Alarms on resource metrics are not supported by CloudWatch at all
- [ ] E: The alarm evaluation period is always too short for CPU metrics specifically
- [ ] F: CPU alarms can only be configured on EC2, never on other services

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's judgment call is precisely this: a threshold that merely differs from normal, without reflecting actual customer impact, produces noisy alarms an on-call learns to ignore.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [alarm-threshold, alert-fatigue, customer-impact-signal]
### QUESTION_BLOCK_END: Q4
<!-- NOTE: draft above had 6 options by mistake — corrected block below is authoritative -->
### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Choosing a meaningful alarm threshold
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why does an alarm on "CPU above 70%" risk training an on-call engineer to ignore alarms?

**OPTIONS:**
- [x] A: CPU utilization is a resource-utilization signal, not a customer-impact signal — it can fire during a legitimate traffic spike that customers are experiencing perfectly fine service through
- [ ] B: CPU metrics are unreliable and frequently report incorrect values
- [ ] C: 70% is technically below the threshold AWS recommends, so the alarm would never fire in practice
- [ ] D: Alarms on resource metrics are not supported by CloudWatch at all

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's judgment call is precisely this: a threshold that merely differs from normal, without reflecting actual customer impact, produces noisy alarms an on-call learns to ignore.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [alarm-threshold, alert-fatigue, customer-impact-signal]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What EMF avoids
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does Embedded Metric Format (EMF) let application code avoid, compared to calling `PutMetricData` directly from inside a hot request path?

**OPTIONS:**
- [x] A: The extra network call and API rate-limit exposure of an explicit `PutMetricData` call, since EMF is written as a structured JSON log line and ingested by the CloudWatch agent
- [ ] B: The need to define a metric namespace at all
- [ ] C: The requirement for the application to run inside a container
- [ ] D: The need for any IAM permissions related to CloudWatch

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this trade-off directly: EMF avoids the network round trip and rate-limit exposure of calling `PutMetricData` synchronously in a hot path, by writing a structured log line instead.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [embedded-metric-format, putmetricdata, hot-path]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Reading the alarm CLI's statistic
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
aws cloudwatch put-metric-alarm --alarm-name manifestflow-p90-processing-latency \
  --namespace ManifestFlow/Processing --metric-name ProcessingLatencyMs \
  --statistic p90 --period 300 --evaluation-periods 3 \
  --threshold 60000 --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:111122223333:manifestflow-oncall
```

**QUESTION_TEXT:**
Given this alarm definition, what condition must hold for the alarm to transition into `ALARM` state?

**OPTIONS:**
- [x] A: The p90 of ProcessingLatencyMs must exceed 60000ms for three consecutive 5-minute evaluation periods
- [ ] B: Any single request's latency must exceed 60000ms, once, at any point
- [ ] C: The average latency across the entire account must exceed 60000ms
- [ ] D: The alarm fires immediately the first time p90 crosses 60000ms, with no evaluation window

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`--period 300 --evaluation-periods 3` requires the p90 threshold breach to persist across three consecutive 5-minute periods before the alarm state transitions, not a single instantaneous breach.
**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [cloudwatch-alarm, evaluation-periods, p90-statistic]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Dimensions and slicing a metric
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The FDE publishes `QueueBacklogDepth` with an `AvailabilityZone` dimension. What does this dimension specifically enable that publishing the metric without it would not?

**OPTIONS:**
- [x] A: Slicing and querying the same metric name separately per AZ, which is what reveals that the backlog is concentrated in `us-east-1b` rather than spread evenly
- [ ] B: Reducing the number of API calls needed to publish the metric
- [ ] C: Automatically triggering an Auto Scaling action without a separate alarm
- [ ] D: Making the metric visible in the AWS Billing console

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Dimensions are what let the same metric name be sliced by an attribute like AZ — without it, the metric would only show an aggregate figure and the localized `us-east-1b` concentration would be invisible.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [metric-dimensions, az-slicing, localized-diagnosis]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Reading the Logs Insights query
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```sql
fields @timestamp, requestId, dependency, latencyMs
| filter @message like /extraction_failed/
| stats count(*) as failures by dependency, bin(5m)
| sort failures desc
```

**QUESTION_TEXT:**
What does this CloudWatch Logs Insights query surface that a simple count of ERROR-level log lines would not?

**OPTIONS:**
- [x] A: Which specific downstream dependency each extraction failure is attributed to, grouped into 5-minute buckets, so a spike can be traced to a specific dependency rather than treated as one undifferentiated error count
- [ ] B: The exact dollar cost of each failed extraction request
- [ ] C: Whether the failure occurred in a public or private subnet
- [ ] D: The CPU utilization of the instance at the time of failure

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The query groups failures `by dependency, bin(5m)` — attributing failures to a specific dependency over time, which is exactly the trace-to-failing-dependency step the Practice Loop asks for, rather than a flat error count.
**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [logs-insights, dependency-tracing, query-syntax]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Symptom vs cause vs impact
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario's final diagnosis, which pairing correctly separates the symptom from the cause?

**OPTIONS:**
- [x] A: Symptom: manifest processing feels slow (p90 latency breach); Cause: two workers in us-east-1b silently failing health checks and not processing messages
- [ ] B: Symptom: two workers failing health checks; Cause: the SQS queue existing at all
- [ ] C: Symptom: the 60-second SLI threshold; Cause: the average latency metric
- [ ] D: There is no meaningful distinction between symptom and cause in this scenario

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The customer-visible p90 latency breach is the symptom; the two silently-unhealthy workers are the root cause the investigation traces back to — exactly the distinction the Evidence of Understanding requires the learner to state precisely.
**LESSON_CONNECTION:** Evidence of Understanding
**KEYWORDS:** [symptom-vs-cause, root-cause-diagnosis]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 4

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-04-cloudwatch-and-cloudtrail-advanced
lesson_title: "CloudWatch and CloudTrail Advanced"
lesson_order: 4

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Distinguish CloudTrail management events from data events and enable the correct category for a given investigation, since data events are not logged by default."
  - "Build a metric filter and alarm on CloudTrail's delivered logs that surfaces a specific security-relevant API call rather than a generic activity count."
  - "Reconstruct an auditable timeline of actor, time, resource, and outcome for a production change using CloudTrail Event History and log file integrity validation, without relying on an engineer's memory."

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
# CloudWatch and CloudTrail Advanced

## Concepts Covered

CloudTrail records two distinct categories of activity, and confusing them is the most common
reason an investigation turns up nothing. Management events capture control-plane operations —
creating a security group, modifying an IAM policy, launching an EC2 instance — and are recorded to
your trail by default, with no additional configuration. Data events capture data-plane operations
on individual resources — an S3 `GetObject` call, a Lambda `Invoke` call, a DynamoDB `GetItem` —
and are **not** recorded by default, because the volume is enormous (every single object read,
across every bucket) and enabling them incurs both storage cost and, for S3 specifically, a
per-event charge; you opt in per resource or per resource type. An investigation into "who
modified this security group" only ever needs management events and works out of the box; an
investigation into "who downloaded this specific customer document from S3" needs data events
enabled on that bucket *before* the download happened, which is why deciding what to enable is a
proactive design decision, not something you can retroactively enable after an incident to see the
past.

CloudTrail Event History gives you a 90-day, no-configuration-required rolling window of management
events, searchable in the console or via `lookup-events`, which covers most single-incident
investigations without needing to stand up a dedicated trail. For anything beyond 90 days, or for
data events, or for delivering events into CloudWatch Logs where a metric filter can alarm on them
in near-real-time, you need an explicit trail delivering to an S3 bucket (with optional CloudWatch
Logs delivery for the metric-filter use case). CloudTrail log files are delivered with SHA-256
digest files that let you cryptographically verify a given period's log files were not altered
after delivery — log file integrity validation — which is the specific mechanism that lets you
present CloudTrail evidence in an incident report as tamper-evident rather than merely
"what the log said," a materially stronger claim when a customer's security team is scrutinizing
the timeline. A metric filter on the CloudTrail-delivered CloudWatch Logs group, matching a specific
`eventName` like `AuthorizeSecurityGroupIngress`, turns "a security group rule changed" from
something you'd only discover by manually searching Event History after the fact into a real-time
alarm — the same metric-filter mechanism from the previous lesson, applied to CloudTrail's own log
stream instead of application logs. Reconstructing a defensible timeline means pulling, for one
specific change, the actor (IAM principal ARN, and whether it was an assumed role vs a long-lived
user), the exact timestamp, the source IP, the specific resource ARN modified, the before/after
values where the event captures them, and whether the calling principal's own permission boundary
should have allowed the action at all — a least-privilege investigative role that can read
CloudTrail and query Athena, but cannot itself modify any production resource, keeps the
investigation itself from becoming a second incident.

```bash
# Enable data events for one specific S3 bucket holding customer manifests
aws cloudtrail put-event-selectors --trail-name manifestflow-org-trail \
  --event-selectors '[{
    "ReadWriteType": "All", "IncludeManagementEvents": true,
    "DataResources": [{"Type": "AWS::S3::Object", "Values": ["arn:aws:s3:::manifestflow-manifests/"]}]
  }]'

# Metric filter + alarm on a specific security-relevant CloudTrail API call
aws logs put-metric-filter --log-group-name /aws/cloudtrail/manifestflow-org-trail \
  --filter-name SecurityGroupIngressChanges \
  --filter-pattern '{ ($.eventName = AuthorizeSecurityGroupIngress) || ($.eventName = RevokeSecurityGroupIngress) }' \
  --metric-transformations \
    metricName=SGIngressChangeCount,metricNamespace=ManifestFlow/Security,metricValue=1,defaultValue=0

aws cloudwatch put-metric-alarm --alarm-name manifestflow-sg-ingress-change \
  --namespace ManifestFlow/Security --metric-name SGIngressChangeCount \
  --statistic Sum --period 60 --evaluation-periods 1 \
  --threshold 0 --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:111122223333:manifestflow-security-oncall

# Reconstruct the timeline for one specific security group
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=sg-0worker9a8b7c6d5 \
  --start-time 2026-08-30T00:00:00Z --end-time 2026-08-31T00:00:00Z \
  --query 'Events[].{Time:EventTime,User:Username,Event:EventName,Source:SourceIPAddress}'
# -> [{"Time": "2026-08-30T14:22:10Z", "User": "deploy-pipeline-role",
#      "Event": "AuthorizeSecurityGroupIngress", "Source": "10.20.10.44"},
#     {"Time": "2026-08-30T14:47:03Z", "User": "j.rivera",
#      "Event": "AuthorizeSecurityGroupIngress", "Source": "203.0.113.201"}]
```

## Practical Backend Scenario

A worker security group's inbound rules changed twice in one afternoon: once as part of a scheduled
deploy pipeline run, and once — outside the deploy window — by a human IAM user, opening port 22
to `0.0.0.0/0`. Lighthouse's security team asks the FDE for a timeline that separates the intended
deployment change from the suspicious one, and asks specifically whether the second change was made
by a role that should have had permission to touch that security group at all. Because the
`AuthorizeSecurityGroupIngress` metric filter and alarm were already enabled before this happened,
the security on-call was paged within a minute of the second change rather than discovering it days
later during a routine audit. `lookup-events` against the specific security group's resource ID
returns both events with distinct actors, timestamps, and source IPs; the deploy pipeline's change
came from the CI role's known IP range inside the VPC, while the second change's source IP traces
to a residential ISP range, immediately distinguishing "intended automation" from "a human using
credentials outside of any expected deployment window."

## Practice Loop

1. Enable the relevant CloudTrail event category for the investigation you actually need — confirm
   whether management events alone suffice (they do, for a security group change) or whether you
   would also need data events enabled in advance for a different kind of investigation.
2. Create the metric filter and alarm on `AuthorizeSecurityGroupIngress` /
   `RevokeSecurityGroupIngress` from the CLI above, before making any change, so the alarm is live
   ahead of the controlled test in the next step.
3. Perform a controlled change to a test security group (add and then remove an inbound rule) and
   measure, in seconds, how long the alarm takes to transition to `ALARM` state after the change —
   this diagnostic proves the alarm actually fires rather than assuming it would.
4. Run `lookup-events` scoped to the test security group's resource ID and extract the actor, exact
   timestamp, source IP, and specific action for every matching event.
5. Write the timeline as a table (actor, timestamp, source IP, action, resource) and mark which
   entries fall inside a known, expected change window versus outside it, producing the exact
   artifact the security team asked for.

## Evidence of Understanding

You can distinguish CloudTrail management events (recorded by default) from data events (opt-in,
must be enabled before the activity you want to investigate occurs) and choose correctly which
category a given investigation needs. You can build a metric filter and alarm on a specific,
security-relevant CloudTrail API call, rather than a generic activity-count alarm, and demonstrate
that it fires within a measured, short window of a controlled test change. You can reconstruct an
actor/time/resource/outcome timeline from CloudTrail Event History for one specific resource and
distinguish an expected automated change from a suspicious out-of-window one using source IP and
principal identity, producing an artifact that does not depend on a screenshot or an engineer's
memory.

## Suggested Extension

Create a dedicated, least-privilege IAM role for security investigations — read-only access to
CloudTrail, CloudWatch Logs, and Athena, with no permission to modify any production resource — and
explain why granting broader access "just in case" to whoever runs the next investigation would
undermine the very tamper-evidence property log file integrity validation is meant to provide.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Management events vs data events
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what is the key operational difference between CloudTrail management events and data events?

**OPTIONS:**
- [x] A: Management events (control-plane operations) are recorded by default; data events (per-resource operations like S3 GetObject) are not recorded unless explicitly enabled in advance
- [ ] B: Data events are recorded by default; management events must be explicitly enabled
- [ ] C: Both are recorded by default with identical retention and no configuration needed
- [ ] D: Management events only cover IAM actions, while data events cover everything else

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this precisely: management events are on by default; data events require an explicit opt-in per resource due to their volume and cost.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [management-events, data-events, cloudtrail-defaults]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why data events must be enabled in advance
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A customer asks who downloaded a specific S3 object last month, but data events were never enabled on that bucket. What does the lesson say about recovering this information now?

**OPTIONS:**
- [x] A: It cannot be recovered — data events are not retroactive; they must have been enabled before the download occurred to have been captured at all
- [ ] B: Enabling data events now will backfill the missing history from S3's own internal logs automatically
- [ ] C: Management events already captured this, since S3 GetObject is classified as a management event
- [ ] D: AWS Support can always recover any historical API call regardless of trail configuration

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson is explicit that deciding what to enable is a proactive design decision — you cannot retroactively enable data events to see activity that happened before they were turned on.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [data-events, retroactive-limitation, proactive-configuration]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Event History's built-in window
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does CloudTrail Event History provide without requiring you to configure a dedicated trail first?

**OPTIONS:**
- [x] A: A 90-day rolling window of management events, searchable via the console or `lookup-events`
- [ ] B: An unlimited-retention archive of every event type, including data events
- [ ] C: Real-time alarming capability equivalent to a metric filter
- [ ] D: Automatic cross-region replication of all events

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states Event History gives a 90-day, no-configuration rolling window of management events — sufficient for most single-incident investigations without a dedicated trail.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [event-history, 90-day-window, lookup-events]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What log file integrity validation actually proves
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does CloudTrail's SHA-256 digest file mechanism (log file integrity validation) let you demonstrate that raw log files alone do not?

**OPTIONS:**
- [x] A: That a given period's delivered log files were not altered after delivery, making the evidence tamper-evident rather than merely "what the log said"
- [ ] B: That the underlying API call itself was authorized correctly
- [ ] C: That the events occurred in the correct AWS Region
- [ ] D: That no data events were missed during the investigation window

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this as the specific evidentiary upgrade — tamper-evidence via cryptographic validation, not just an unverified claim about log contents.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [log-file-integrity, tamper-evidence, sha-256-digest]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Reading the CloudTrail metric filter pattern
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
aws logs put-metric-filter --log-group-name /aws/cloudtrail/manifestflow-org-trail \
  --filter-name SecurityGroupIngressChanges \
  --filter-pattern '{ ($.eventName = AuthorizeSecurityGroupIngress) || ($.eventName = RevokeSecurityGroupIngress) }' \
  --metric-transformations \
    metricName=SGIngressChangeCount,metricNamespace=ManifestFlow/Security,metricValue=1,defaultValue=0
```

**QUESTION_TEXT:**
What specific condition does this metric filter turn into a real-time metric?

**OPTIONS:**
- [x] A: Any CloudTrail event whose `eventName` is either `AuthorizeSecurityGroupIngress` or `RevokeSecurityGroupIngress`, regardless of which security group or actor was involved
- [ ] B: Every API call recorded by CloudTrail, with no filtering at all
- [ ] C: Only failed API calls that returned an access-denied error
- [ ] D: Only changes made by IAM users, excluding changes made by assumed roles

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The filter pattern matches on `eventName` for the two specific ingress-rule-changing API calls — any matching event, from any actor or security group, increments the metric.
**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [metric-filter-pattern, eventname-match, security-alarm]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Distinguishing the two changes
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
`lookup-events` returns two `AuthorizeSecurityGroupIngress` events on the same security group in one afternoon: one from `deploy-pipeline-role` sourced from a known internal VPC IP, and one from a human IAM user sourced from a residential ISP IP outside any deployment window. What lets the investigator distinguish "intended" from "suspicious" here?

**OPTIONS:**
- [x] A: Correlating each event's actor identity and source IP against known deployment-automation identities and expected change windows
- [ ] B: CloudTrail automatically labels one event "intended" and the other "suspicious" in its output
- [ ] C: The event names themselves differ between the two calls
- [ ] D: Only the timestamp matters; source IP and actor identity are not relevant to this determination

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's scenario resolves this exactly by correlating actor and source IP against known automation identities and expected windows — CloudTrail records the facts, the investigator draws the conclusion.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [actor-correlation, source-ip, investigative-judgment]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the alarm mattered before the incident
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The scenario notes the alarm was already enabled before the suspicious change happened. Why does this timing matter?

**OPTIONS:**
- [x] A: It let the security on-call be paged within a minute of the change, instead of discovering it days later during a routine audit
- [ ] B: CloudTrail cannot record an event unless a matching alarm already exists for it
- [ ] C: It reduced the AWS bill for the CloudTrail trail
- [ ] D: It has no bearing on detection speed, only on billing

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Proactive alarming is what converts CloudTrail from a forensic record you search after the fact into a near-real-time detection signal — the lesson contrasts near-immediate paging against discovery during a later audit.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [proactive-alarming, detection-latency, security-oncall]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** The least-privilege investigative role
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's Suggested Extension, why should the investigative IAM role have read-only access to CloudTrail, CloudWatch Logs, and Athena, with no permission to modify production resources?

**OPTIONS:**
- [x] A: Granting broader access "just in case" undermines the tamper-evidence goal of the investigation itself — an investigator who could modify production resources could also, even unintentionally, alter the very evidence being examined
- [ ] B: AWS technically forbids granting write permissions to any role used for CloudTrail queries
- [ ] C: Read-only roles are billed at a lower rate than roles with write access
- [ ] D: Athena queries are only supported from roles with no other IAM permissions at all

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's stated reasoning is about investigative integrity — the value of tamper-evident logs is undermined if the very role investigating them could also alter production state.
**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [least-privilege, investigative-role, evidence-integrity]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What lookup-events returns
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=sg-0worker9a8b7c6d5 \
  --start-time 2026-08-30T00:00:00Z --end-time 2026-08-31T00:00:00Z \
  --query 'Events[].{Time:EventTime,User:Username,Event:EventName,Source:SourceIPAddress}'
[{"Time": "2026-08-30T14:22:10Z", "User": "deploy-pipeline-role", "Event": "AuthorizeSecurityGroupIngress", "Source": "10.20.10.44"},
 {"Time": "2026-08-30T14:47:03Z", "User": "j.rivera", "Event": "AuthorizeSecurityGroupIngress", "Source": "203.0.113.201"}]
```

**QUESTION_TEXT:**
Given this output, what four fields does the timeline reconstruction extract for each event, per the lesson's approach?

**OPTIONS:**
- [x] A: Actor (Username), exact timestamp (Time), the API action (Event), and the source IP (Source), for the resource in question
- [ ] B: Only the timestamp and the resource ARN, with actor identity considered irrelevant
- [ ] C: Only the API action name, since the other fields are not captured by CloudTrail
- [ ] D: The AWS Support case number associated with each event
- [ ] E: The billing amount charged for each API call
- [ ] F: The exact line number in the application's own source code that triggered the call

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The `--query` projects exactly these four fields — actor, time, event name, and source IP — matching the lesson's stated timeline reconstruction fields (actor, time, resource, outcome).
**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [lookup-events, timeline-fields, cli-query]
### QUESTION_BLOCK_END: Q9
<!-- NOTE: draft above had 6 options by mistake — corrected block below is authoritative -->
### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What lookup-events returns
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```
$ aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=sg-0worker9a8b7c6d5 \
  --start-time 2026-08-30T00:00:00Z --end-time 2026-08-31T00:00:00Z \
  --query 'Events[].{Time:EventTime,User:Username,Event:EventName,Source:SourceIPAddress}'
[{"Time": "2026-08-30T14:22:10Z", "User": "deploy-pipeline-role", "Event": "AuthorizeSecurityGroupIngress", "Source": "10.20.10.44"},
 {"Time": "2026-08-30T14:47:03Z", "User": "j.rivera", "Event": "AuthorizeSecurityGroupIngress", "Source": "203.0.113.201"}]
```

**QUESTION_TEXT:**
Given this output, what four fields does the timeline reconstruction extract for each event, per the lesson's approach?

**OPTIONS:**
- [x] A: Actor (Username), exact timestamp (Time), the API action (Event), and the source IP (Source), for the resource in question
- [ ] B: Only the timestamp and the resource ARN, with actor identity considered irrelevant
- [ ] C: Only the API action name, since the other fields are not captured by CloudTrail
- [ ] D: The AWS Support case number associated with each event

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The `--query` projects exactly these four fields — actor, time, event name, and source IP — matching the lesson's stated timeline reconstruction fields (actor, time, resource, outcome).
**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [lookup-events, timeline-fields, cli-query]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 5

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-05-docker-app-on-ec2-project
lesson_title: "Docker App on EC2 Project"
lesson_order: 5

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 120
content_status: Draft

learning_outcomes:
  - "Bootstrap a Docker runtime and application container onto EC2 using user data, with an IAM instance role instead of embedded credentials."
  - "Route container logs to CloudWatch Logs via the CloudWatch agent, so log inspection does not require SSH access to the instance."
  - "Apply an immutable-infrastructure replacement strategy — replace the instance rather than patch it in place — and verify the replacement recovers correctly from the documented steps alone."

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
# Docker App on EC2 Project

## Concepts Covered

Deploying a container to a single EC2 instance is the right call when a customer needs something
running quickly and has not yet adopted ECS, EKS, or any managed container platform — but doing it
in a way an operator other than the original FDE can actually maintain requires several deliberate
choices, not just `docker run` typed once over SSH. The instance's identity should come from an
**IAM instance role** attached via an instance profile, never from an access key pair baked into
the container's environment variables or embedded in the AMI — the instance role's temporary
credentials are automatically rotated by the EC2 metadata service and scoped to exactly what the
instance needs (pulling one specific ECR repository, writing to one specific CloudWatch Logs group),
which means a compromised instance leaks a narrowly-scoped, auto-expiring credential rather than a
long-lived key with whatever permissions someone happened to grant it. **User data** is the
mechanism that turns instance launch into a repeatable bootstrap: a shell script (or cloud-init
directive) that runs once, automatically, the first time the instance boots, installing the Docker
engine, authenticating to ECR using the instance role's credentials, and starting the container —
this is what separates "a new operator can launch a working instance from the documented launch
template" from "only the FDE who set it up by hand remembers all the steps."

Getting logs and health signals off the instance without SSH is the second deliberate choice. The
CloudWatch agent, itself running on the instance (or, for container logs specifically, configured
via the `awslogs` Docker logging driver), forwards both the container's stdout/stderr and
instance-level metrics (memory, disk) to CloudWatch, which means an operator diagnosing a problem
opens CloudWatch Logs, not an SSH session — a meaningful distinction for a customer's operations
team that may not have SSH key access to production at all, or whose access is deliberately
break-glass-only. A health check — even something as simple as a container-internal `curl
localhost:8080/health` on an interval, reported via a `HEALTHCHECK` instruction in the Dockerfile
or an external check against an Application Load Balancer target group — is what turns "the
container process is still running" into "the application inside it is actually serving traffic
correctly," since a hung process can stay alive (and pass a naive process-exists check) while never
successfully responding to a real request again. Finally, the replacement strategy matters as much
as the bootstrap: treating the instance as **immutable** — never SSHing in to patch a running
instance, but instead updating the launch template (a new AMI, a new user data script, a new
container image tag) and replacing the instance wholesale — means every instance that exists at any
moment was provisioned by the same documented, versioned process, rather than accumulating
undocumented manual changes over its lifetime that nobody can reconstruct later.

```bash
# IAM trust policy + instance role scoped to exactly what this instance needs
cat > digest-notifier-trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"},
                  "Action": "sts:AssumeRole"}]
}
EOF
aws iam create-role --role-name digest-notifier-instance-role \
  --assume-role-policy-document file://digest-notifier-trust-policy.json

cat > digest-notifier-permissions.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*"},
    {"Effect": "Allow", "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
     "Resource": "arn:aws:ecr:us-east-1:111122223333:repository/digest-notifier"},
    {"Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
     "Resource": "arn:aws:logs:us-east-1:111122223333:log-group:/manifestflow/digest-notifier:*"}
  ]
}
EOF
aws iam put-role-policy --role-name digest-notifier-instance-role \
  --policy-name digest-notifier-scoped-access --policy-document file://digest-notifier-permissions.json
aws iam create-instance-profile --instance-profile-name digest-notifier-profile
aws iam add-role-to-instance-profile --instance-profile-name digest-notifier-profile \
  --role-name digest-notifier-instance-role

# User data: bootstrap Docker, authenticate to ECR, run the container with the awslogs driver
cat > user-data.sh <<'EOF'
#!/bin/bash
yum install -y docker
systemctl enable --now docker
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 111122223333.dkr.ecr.us-east-1.amazonaws.com
docker run -d --name digest-notifier --restart unless-stopped \
  --log-driver awslogs \
  --log-opt awslogs-group=/manifestflow/digest-notifier \
  --log-opt awslogs-region=us-east-1 \
  --log-opt awslogs-stream=$(curl -s http://169.254.169.254/latest/meta-data/instance-id) \
  -p 8080:8080 \
  111122223333.dkr.ecr.us-east-1.amazonaws.com/digest-notifier:1.3.0
EOF

# Launch the instance with the role and user data attached
aws ec2 run-instances --image-id ami-0abcdef1234567890 --instance-type t3.small \
  --iam-instance-profile Name=digest-notifier-profile \
  --security-group-ids sg-0notifier7f8e9d0c \
  --subnet-id subnet-0priv1 --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=digest-notifier}]'
```

## Practical Backend Scenario

Lighthouse needs a small internal service, `digest-notifier`, that emails dispatchers a daily
summary of processed manifests — low traffic, no need for ECS or EKS yet, but it must survive a
restart and be replaceable by whoever is on call, not just the FDE who built it. The FDE launches
it on a single `t3.small` EC2 instance using the instance role, user-data bootstrap, and
`awslogs` logging driver above. Two weeks later, the underlying AMI needs a security patch: instead
of SSHing into the running instance to apply it (which would leave an undocumented, unreproducible
change baked into that one instance), the FDE updates the launch template to reference a patched
AMI, launches a replacement instance from the updated template, confirms its health check passes,
and terminates the original — recovering the exact same running state through the documented
process alone, with zero manual intervention on the instance itself.

## Practice Loop

1. Package `digest-notifier` as a container image and push it to ECR, then create the IAM
   instance role and instance profile scoped to exactly the ECR repository and CloudWatch Logs
   group this one service needs — nothing broader.
2. Write the user-data bootstrap script, launch the instance, and confirm the container is running
   by curling its health endpoint from another instance in the same VPC (not from the public
   internet, since this service has no public ingress requirement).
3. Restrict inbound access to only the security group of whatever internal service calls
   `digest-notifier`, and run the denied-flow test: attempt to reach port 8080 from an unrelated
   security group and confirm the connection is refused.
4. Confirm container logs are visible in the `/manifestflow/digest-notifier` CloudWatch Logs group
   without opening an SSH session to the instance at any point in this step.
5. Update the launch template to reference a new AMI, launch a replacement instance, verify its
   health check passes, terminate the original instance, and time the whole replacement from
   launch to termination as your recovery evidence.

## Evidence of Understanding

You can bootstrap a Docker runtime and a specific application container onto EC2 using user data
and an IAM instance role, with no embedded credentials and no manual post-launch configuration.
You can route container logs to CloudWatch Logs via the `awslogs` driver so an operator can
diagnose the service without SSH access to the instance. You can replace an instance wholesale
using an updated launch template rather than patching it in place, and demonstrate — with a
measured replacement time — that a new operator following only the documented steps recovers the
service correctly.

## Suggested Extension

Wrap the single instance in an Auto Scaling group with `MinSize=1, MaxSize=1` and a target-tracking
policy on the health check, and explain what the ASG's automatic instance replacement adds beyond
the manual launch-template-swap process this lesson walked through by hand.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why an instance role beats an embedded access key
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why should the EC2 instance's ECR and CloudWatch Logs access come from an IAM instance role rather than an access key pair embedded in the container's environment?

**OPTIONS:**
- [x] A: The instance role's credentials are temporary, automatically rotated by the EC2 metadata service, and scoped narrowly — a compromised instance leaks a narrowly-scoped, auto-expiring credential rather than a long-lived key
- [ ] B: Access key pairs are technically incompatible with the Docker CLI
- [ ] C: Instance roles are free while access keys incur an hourly charge
- [ ] D: There is no meaningful security difference; the choice is purely about convenience

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this exactly — auto-rotating, narrowly-scoped temporary credentials versus a long-lived embedded key with whatever permissions were granted.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [iam-instance-role, credential-scoping, instance-profile]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What user data actually enables
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does bootstrapping the instance via user data accomplish that manually configuring the instance over SSH after launch does not?

**OPTIONS:**
- [x] A: It makes the setup a repeatable, documented process any operator can reproduce from the launch template, rather than steps only the original engineer remembers
- [ ] B: It removes the need for the instance to have an IAM role at all
- [ ] C: User data runs continuously in the background, unlike a one-time SSH session
- [ ] D: It automatically encrypts the instance's root EBS volume

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's stated distinction is reproducibility — user data is what separates "a new operator can launch a working instance from the template" from tribal knowledge held by one engineer.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [user-data, bootstrap, reproducibility]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the scoped IAM policy
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```json
{
  "Effect": "Allow", "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
  "Resource": "arn:aws:ecr:us-east-1:111122223333:repository/digest-notifier"
}
```

**QUESTION_TEXT:**
What does scoping this policy statement's `Resource` to one specific ECR repository, rather than `*`, accomplish?

**OPTIONS:**
- [x] A: It limits the instance role to pulling only the `digest-notifier` repository, so a compromised instance cannot pull images from unrelated repositories in the same account
- [ ] B: It has no functional effect since ECR ignores resource-level restrictions
- [ ] C: It prevents the repository from being deleted by any principal
- [ ] D: It is required syntax with no security implication

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Resource-scoping the policy is exactly the "narrowly scoped to what the instance needs" principle the lesson names — this is the difference between a compromised instance leaking narrow versus broad access.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [iam-policy-scoping, ecr-repository, least-privilege]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why logs go to CloudWatch instead of requiring SSH
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what is the operational advantage of routing container logs to CloudWatch Logs via the `awslogs` driver instead of requiring an operator to SSH in and run `docker logs`?

**OPTIONS:**
- [x] A: An operator can diagnose the service from CloudWatch Logs even if they have no SSH key access to production, which matters for teams whose access is deliberately break-glass-only
- [ ] B: The `awslogs` driver makes the container start faster
- [ ] C: SSH access to EC2 instances is technically deprecated by AWS
- [ ] D: CloudWatch Logs is the only place Docker container logs can be written to at all

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this specifically — diagnosing via CloudWatch Logs rather than SSH matters for an operations team that may not have (or want to routinely use) SSH access to production.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [awslogs-driver, no-ssh-diagnosis, operational-access]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Health check vs process-exists check
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist on an application-level health check (curling `/health`) rather than simply checking that the container process is still running?

**OPTIONS:**
- [x] A: A hung process can remain alive and pass a naive process-exists check while never successfully responding to a real request again, so only an application-level check confirms the service is actually serving traffic correctly
- [ ] B: Process-exists checks are not supported by the Docker CLI at all
- [ ] C: An application-level health check uses less CPU than a process check
- [ ] D: There is no meaningful difference between the two kinds of checks

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson makes this exact distinction — "the process is running" is not the same claim as "the application inside it is serving traffic correctly," and only an app-level check verifies the latter.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [health-check, hung-process, liveness-vs-readiness]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Immutable replacement vs in-place patching
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
When `digest-notifier`'s AMI needs a security patch, why does the lesson replace the instance from an updated launch template instead of SSHing in to patch the running instance directly?

**OPTIONS:**
- [x] A: SSHing in to patch a running instance leaves an undocumented, unreproducible change baked into that one instance, while replacing it from an updated launch template keeps every running instance traceable to the same documented process
- [ ] B: EC2 instances cannot technically be patched in place under any circumstances
- [ ] C: Replacing an instance is always faster than applying a security patch
- [ ] D: Launch templates automatically detect and apply security patches without any user action

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is the lesson's immutable-infrastructure argument stated precisely — traceability to a documented, versioned process versus an undocumented manual change nobody can reconstruct later.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [immutable-infrastructure, launch-template, patch-strategy]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Reading the user-data script's ECR login
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 111122223333.dkr.ecr.us-east-1.amazonaws.com
```

**QUESTION_TEXT:**
This command runs successfully during instance boot with no credentials configured anywhere in the user-data script itself. What makes this possible?

**OPTIONS:**
- [x] A: The AWS CLI automatically uses the instance's attached IAM instance role credentials, obtained from the EC2 metadata service, to authorize the `ecr:GetAuthorizationToken` call
- [ ] B: `aws ecr get-login-password` does not actually require any AWS credentials to run
- [ ] C: Docker Hub provides this authentication transparently regardless of the registry specified
- [ ] D: The command silently fails and the container falls back to a public image
- [ ] E: ECR grants anonymous read access to all repositories by default
- [ ] F: The instance's security group grants this permission

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is exactly why the instance role was attached — the AWS CLI transparently uses the role's temporary credentials from the instance metadata service, no explicit credential configuration needed.
**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [instance-metadata-service, ecr-authentication, instance-role-credentials]
### QUESTION_BLOCK_END: Q7
<!-- NOTE: draft above had 6 options by mistake — corrected block below is authoritative -->
### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Reading the user-data script's ECR login
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 111122223333.dkr.ecr.us-east-1.amazonaws.com
```

**QUESTION_TEXT:**
This command runs successfully during instance boot with no credentials configured anywhere in the user-data script itself. What makes this possible?

**OPTIONS:**
- [x] A: The AWS CLI automatically uses the instance's attached IAM instance role credentials, obtained from the EC2 metadata service, to authorize the `ecr:GetAuthorizationToken` call
- [ ] B: `aws ecr get-login-password` does not actually require any AWS credentials to run
- [ ] C: Docker Hub provides this authentication transparently regardless of the registry specified
- [ ] D: The command silently fails and the container falls back to a public image

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is exactly why the instance role was attached — the AWS CLI transparently uses the role's temporary credentials from the instance metadata service, no explicit credential configuration needed.
**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [instance-metadata-service, ecr-authentication, instance-role-credentials]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What the Suggested Extension's ASG adds
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Wrapping the single instance in an Auto Scaling group with `MinSize=1, MaxSize=1` and health-check-based replacement adds what capability beyond the manual launch-template-swap process this lesson walked through?

**OPTIONS:**
- [x] A: Automatic replacement of an unhealthy instance without requiring an operator to notice the failure and manually trigger the swap
- [ ] B: It removes the need for an IAM instance role, since the ASG provides credentials directly
- [ ] C: It eliminates the need for a launch template entirely
- [ ] D: It changes the underlying container image without any user action

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The manual process this lesson taught still requires a human to notice a problem and trigger the swap; an ASG with health-check-based replacement automates that detection-and-replacement loop.
**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [auto-scaling-group, automatic-replacement, health-check-based-recovery]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 6

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-06-aws-lambda-and-api-gateway
lesson_title: "AWS Lambda and API Gateway"
lesson_order: 6

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Wire an API Gateway REST API resource, method, and Lambda proxy integration together with the exact resource-based permission that makes the route callable at all."
  - "Configure a Lambda function's timeout and reserved concurrency from the CLI, and explain what each protects against."
  - "Implement request idempotency using a DynamoDB conditional write, and exercise a duplicate request and a downstream failure to prove the safety property holds."

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
# AWS Lambda and API Gateway

## Concepts Covered

Module 4's serverless lesson already covers the architectural framing of Lambda and API Gateway —
why cold starts are a first-class trade-off, when a Step Functions state machine beats hand-rolled
orchestration, and when serverless wins or loses against a continuously-running container for a
given workload's shape. This lesson deliberately does not repeat that framing; it goes one level
more mechanical, into the actual console/CLI wiring an FDE performs to make an API Gateway route
callable at all, and into the concrete implementation of idempotency this module's earlier lessons
kept assuming rather than showing.

An API Gateway REST API is built from resources (URL path segments), methods (an HTTP verb attached
to a resource), and integrations (what the method actually invokes — here, a Lambda function via
`AWS_PROXY` integration, which forwards the entire HTTP request as-is into the Lambda's event
payload rather than requiring a hand-written request-mapping template). Creating the resource and
method is not, by itself, sufic­ient to make the route work: API Gateway is a separate AWS service
from Lambda, and by default has no permission to invoke your function. You must explicitly grant it
that permission with a **resource-based policy** on the Lambda function itself — `lambda
add-permission` with `--principal apigateway.amazonaws.com` and a `--source-arn` scoped to the
specific API and route — which is easy to forget because the console's "Add Trigger" flow performs
this step invisibly for you, leaving CLI/IaC-driven deployments as the place this omission actually
bites, producing a mysterious 500 "Internal server error" from API Gateway with no useful detail in
the response, discoverable only in the API Gateway execution logs.

Lambda's execution role is the second identity boundary, separate from the resource-based policy:
where the resource-based policy governs *who may invoke the function*, the execution role governs
*what the function's code is permitted to do once invoked* — write to a specific SQS queue, read
one DynamoDB table, nothing more. `--timeout` bounds how long a single invocation may run before
Lambda forcibly terminates it (protecting against a hung downstream dependency consuming billed
execution time indefinitely), while `--reserved-concurrent-executions` caps how many invocations of
this specific function may run simultaneously across the entire account, protecting a downstream
dependency (a database, a rate-limited third-party API) from being overwhelmed by a traffic spike
that Lambda's default near-unlimited concurrency would otherwise pass straight through unthrottled.
API Gateway's own request validation (a JSON Schema model attached to the method) rejects a
malformed request *before* it ever invokes the Lambda function at all, which is strictly cheaper
and faster than writing the same validation as the first lines of the handler and paying for an
invocation that was always going to fail. Idempotency, finally, is not a Lambda or API Gateway
feature — it is something the handler code must implement explicitly, typically via a
conditional write against a store (here, DynamoDB) keyed by a client-supplied idempotency key: the
write only succeeds the first time a given key is seen, and every subsequent request with the same
key can detect the duplicate and return the original result instead of reprocessing.

```bash
# Wire the resource, method, and AWS_PROXY integration
aws apigateway create-resource --rest-api-id abc123xyz \
  --parent-id root-resource-id --path-part callback
aws apigateway put-method --rest-api-id abc123xyz --resource-id res-callback \
  --http-method POST --authorization-type NONE --request-validator-id val-body-required
aws apigateway put-integration --rest-api-id abc123xyz --resource-id res-callback \
  --http-method POST --type AWS_PROXY --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:111122223333:function:manifest-callback/invocations

# The permission API Gateway needs to actually invoke the function — easy to forget
aws lambda add-permission --function-name manifest-callback \
  --statement-id apigateway-invoke-callback --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:111122223333:abc123xyz/*/POST/callback"

# Timeout and concurrency, set independently of the function's code
aws lambda update-function-configuration --function-name manifest-callback \
  --timeout 10 --reserved-concurrent-executions 20

# Execution role: what the function's own code is permitted to do once invoked
cat > manifest-callback-permissions.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": "dynamodb:PutItem",
     "Resource": "arn:aws:dynamodb:us-east-1:111122223333:table/manifest-idempotency-keys",
     "Condition": {"StringEquals": {"dynamodb:LeadingKeys": []}}},
    {"Effect": "Allow", "Action": "sqs:SendMessage",
     "Resource": "arn:aws:sqs:us-east-1:111122223333:manifest-processing-queue"}
  ]
}
EOF
```

```python
# Handler: idempotent callback via a DynamoDB conditional PutItem
import boto3, json, hashlib
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table("manifest-idempotency-keys")
sqs = boto3.client("sqs")

def handler(event, context):
    body = json.loads(event["body"])
    idempotency_key = event["headers"].get("Idempotency-Key")
    if not idempotency_key:
        return {"statusCode": 400, "body": json.dumps({"error": "Idempotency-Key header required"})}

    try:
        # Conditional write: succeeds only if this key has never been seen
        table.put_item(
            Item={"idempotency_key": idempotency_key, "status": "processing"},
            ConditionExpression="attribute_not_exists(idempotency_key)"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"statusCode": 200, "body": json.dumps({"status": "duplicate_ignored"})}
        raise

    sqs.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/111122223333/manifest-processing-queue",
        MessageBody=json.dumps(body),
        MessageAttributes={"idempotency_key": {"DataType": "String", "StringValue": idempotency_key}}
    )
    return {"statusCode": 202, "body": json.dumps({"status": "accepted"})}
```

## Practical Backend Scenario

A customs broker's system calls `POST /manifests/callback` whenever a manifest is finalized on
their side, to notify ManifestFlow to begin processing — a low-volume, bursty event, well suited to
Lambda rather than a continuously-running container. The broker's integration retries on any
non-2xx response or timeout, which means ManifestFlow's callback will occasionally receive the same
manifest notification twice. The Lambda handler above treats the broker-supplied `Idempotency-Key`
header as the deduplication key: the first request's conditional `PutItem` succeeds and the manifest
is queued for processing; a retried duplicate's conditional `PutItem` fails with
`ConditionalCheckFailedException`, and the handler returns `200 duplicate_ignored` instead of
queuing the manifest a second time. Separately, the FDE deliberately sets
`--reserved-concurrent-executions 20`, well above the broker's realistic peak burst but well below
what would overwhelm the downstream SQS-consuming worker fleet if the broker's system ever
misbehaved and fired thousands of callbacks in a tight loop.

## Practice Loop

1. Create the API Gateway resource, method, and `AWS_PROXY` integration, then attempt to call the
   route before granting the `lambda add-permission` statement — capture the exact error API
   Gateway returns, since this is the specific failure mode CLI/IaC deployments hit that the
   console's "Add Trigger" flow hides.
2. Add the resource-based permission scoped to this specific API and route, re-call the endpoint,
   and confirm the invocation now succeeds.
3. Set `--timeout 10` and `--reserved-concurrent-executions 20`, then deliberately invoke the
   function with a payload that causes the downstream SQS call to hang, and measure how long the
   invocation actually runs before Lambda terminates it — this diagnostic proves the timeout is
   enforced rather than assumed.
4. Send the same request twice with an identical `Idempotency-Key` header and confirm, from the
   response bodies, that the manifest was queued exactly once (`accepted` then `duplicate_ignored`),
   not twice.
5. Simulate the downstream SQS call failing (temporarily revoke the execution role's `sqs:SendMessage`
   permission) and confirm the conditional `PutItem` already succeeded, then decide and document
   whether a failed downstream call after a successful idempotency-key write should be treated as
   retryable or as requiring manual reconciliation.

## Evidence of Understanding

You can wire an API Gateway resource, method, and Lambda proxy integration together, and can name
the specific resource-based permission (`lambda add-permission` with a scoped `--source-arn`) that
makes the route actually callable, distinct from the execution role that governs what the function's
own code may do. You can configure `--timeout` and `--reserved-concurrent-executions`
independently and explain what each protects against — a hung dependency consuming billed time
versus an unthrottled traffic spike overwhelming a downstream system. You can implement and prove,
with an actual duplicate request, that a DynamoDB conditional write makes a callback endpoint safe
against retries, and can state whether a failure after the idempotency key is written should be
retried or requires manual reconciliation.

## Suggested Extension

Add a JSON Schema request validator to the `POST /callback` method so a malformed payload (missing
the required `manifest_id` field) is rejected by API Gateway itself with a 400, before the Lambda
function is ever invoked, and measure whether this reduces the function's invocation count during a
deliberate burst of malformed test requests compared to validating inside the handler.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** How this lesson differs from Module 4's Lambda lesson
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's own framing, what does this lesson deliberately focus on that Module 4's serverless lesson does not?

**OPTIONS:**
- [x] A: The actual console/CLI mechanics of wiring API Gateway to Lambda — resource-based permissions, execution role scoping, timeout/concurrency configuration — and a concrete idempotency implementation
- [ ] B: Whether serverless or a container is the right architectural choice for a given workload
- [ ] C: Step Functions state machine design with Retry and Catch fields
- [ ] D: The cold-start cost trade-off between infrequent and steady traffic

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this explicitly in its opening paragraph — Module 4 already covers the architectural framing (B, C, D); this lesson goes one level more mechanical.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [module-differentiation, hands-on-mechanics, lambda-api-gateway]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why the route fails without add-permission
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A `POST /callback` route is created with a correctly configured `AWS_PROXY` integration, but calling it returns a 500 "Internal server error" with no useful detail. What is the most likely cause, per the lesson?

**OPTIONS:**
- [x] A: API Gateway has not been granted permission to invoke the Lambda function — the `lambda add-permission` resource-based policy statement is missing
- [ ] B: The Lambda function's timeout is set too low
- [ ] C: The API Gateway resource path contains an invalid character
- [ ] D: `AWS_PROXY` integrations are incompatible with `POST` methods

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this exact failure mode — a missing resource-based permission produces a vague 500 from API Gateway, discoverable only in execution logs, and is easy to omit in CLI/IaC-driven deployments.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [lambda-add-permission, resource-based-policy, missing-invoke-permission]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Resource-based policy vs execution role
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the difference between the Lambda function's resource-based policy (set via `add-permission`) and its execution role?

**OPTIONS:**
- [x] A: The resource-based policy governs who may invoke the function; the execution role governs what the function's own code may do once invoked
- [ ] B: They are two names for the exact same IAM construct
- [ ] C: The execution role governs who may invoke the function; the resource-based policy governs what the code may do
- [ ] D: The resource-based policy is optional and has no effect if omitted

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson draws this line explicitly — invocation permission (resource-based policy) versus runtime code permission (execution role) are two separate identity boundaries.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [resource-based-policy, execution-role, identity-boundaries]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What --reserved-concurrent-executions protects
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the FDE set `--reserved-concurrent-executions 20` on the `manifest-callback` function, per the lesson?

**OPTIONS:**
- [x] A: To cap how many invocations can run simultaneously, protecting the downstream SQS-consuming worker fleet from being overwhelmed if the broker's system misbehaves and fires an unusually large burst of callbacks
- [ ] B: To guarantee the function always has at least 20 warm execution environments available, eliminating cold starts entirely
- [ ] C: To limit the function's memory allocation to 20MB
- [ ] D: To set the function's maximum execution duration to 20 seconds

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this precisely — concurrency limits cap simultaneous invocations to protect a downstream dependency, distinct from timeout (which bounds a single invocation's duration).
**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [reserved-concurrency, downstream-protection, throttling]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Reading the idempotent handler
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```python
try:
    table.put_item(
        Item={"idempotency_key": idempotency_key, "status": "processing"},
        ConditionExpression="attribute_not_exists(idempotency_key)"
    )
except ClientError as e:
    if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
        return {"statusCode": 200, "body": json.dumps({"status": "duplicate_ignored"})}
    raise
```

**QUESTION_TEXT:**
What happens the second time this handler is invoked with the same `idempotency_key`?

**OPTIONS:**
- [x] A: The conditional `PutItem` fails with `ConditionalCheckFailedException` because the item already exists, and the handler returns `duplicate_ignored` without re-queuing the manifest
- [ ] B: The item is overwritten silently and the manifest is queued a second time
- [ ] C: DynamoDB raises an unrecoverable error that crashes the Lambda function
- [ ] D: The `ConditionExpression` is ignored on the second call, since conditions only apply to the first write ever made to the table

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`attribute_not_exists(idempotency_key)` makes the write succeed only the first time; a second attempt with the same key fails the condition, which the handler catches and turns into a safe no-op response.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [conditional-write, dynamodb-idempotency, duplicate-detection]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** The gap between idempotency-key write and downstream success
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practice Loop's step 5, the conditional `PutItem` succeeds but the subsequent `sqs:SendMessage` call fails because the execution role's permission was revoked. What does this expose about the handler's current idempotency design?

**OPTIONS:**
- [x] A: The idempotency key is marked "seen" before the downstream action (queuing) is confirmed to have succeeded, so a failure after the write leaves the manifest never queued but also permanently treated as a duplicate on any future retry with that same key
- [ ] B: This scenario is impossible, since DynamoDB and SQS calls always succeed or fail together
- [ ] C: The handler automatically retries the SQS call an unlimited number of times before returning
- [ ] D: This has no effect on the manifest's eventual processing outcome

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
This is exactly the gap the Practice Loop's diagnostic step is designed to surface — the write-then-act ordering means a downstream failure after the idempotency key is claimed needs an explicit decision (retryable status vs. manual reconciliation), which the lesson asks the learner to make and document rather than leaving implicit.
**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [idempotency-gap, partial-failure, reconciliation]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why request validation at API Gateway beats validation in the handler
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why is rejecting a malformed request via an API Gateway request validator strictly cheaper than validating the same condition as the first lines of the Lambda handler?

**OPTIONS:**
- [x] A: A request rejected by API Gateway never invokes the Lambda function at all, avoiding paying for an invocation that was always going to fail
- [ ] B: API Gateway request validators are more accurate than any validation logic that could be written in Python
- [ ] C: Lambda functions cannot access the request body at all, making handler-side validation impossible
- [ ] D: There is no cost difference; the two approaches are functionally and financially identical

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this directly — rejecting before invocation avoids billing for an invocation whose outcome (a validation failure) was already certain.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [request-validation, api-gateway-model, invocation-cost]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** AWS_PROXY integration behavior
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does an `AWS_PROXY` integration type do with an incoming HTTP request, compared to a non-proxy integration requiring a request-mapping template?

**OPTIONS:**
- [x] A: It forwards the entire HTTP request (headers, body, path parameters) as-is into the Lambda's event payload, with no hand-written mapping template required
- [ ] B: It strips the request body entirely and forwards only the HTTP headers
- [ ] C: It requires a request-mapping template just like a non-proxy integration, but applies it after invocation instead of before
- [ ] D: It converts the request into an XML payload before invoking Lambda

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson describes `AWS_PROXY` specifically as forwarding the entire request as-is, which is why the handler code above reads `event["body"]` and `event["headers"]` directly.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [aws-proxy-integration, event-payload, no-mapping-template]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Timeout vs concurrency, distinguished
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
`--timeout` and `--reserved-concurrent-executions` protect against two different failure modes. Which pairing is correct?

**OPTIONS:**
- [x] A: `--timeout` bounds how long one invocation may run (protecting against a hung dependency consuming billed time); `--reserved-concurrent-executions` caps how many invocations run simultaneously (protecting a downstream system from a traffic spike)
- [ ] B: Both settings control exactly the same thing — the maximum billed execution time per invocation
- [ ] C: `--timeout` controls simultaneous invocations; `--reserved-concurrent-executions` controls single-invocation duration
- [ ] D: `--reserved-concurrent-executions` only takes effect after `--timeout` is exceeded

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson separates these explicitly — a per-invocation duration bound versus an account-wide simultaneous-invocation cap — each protecting against a distinct failure mode.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [lambda-timeout, reserved-concurrency, failure-mode-distinction]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->
