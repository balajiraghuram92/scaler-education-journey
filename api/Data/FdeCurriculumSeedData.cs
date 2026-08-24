using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

/// <summary>
/// Creates the canonical, editorial FDE course from a verified legacy FDE outline.
/// This is intentionally additive: it never creates task-to-lesson links or chooses a
/// canonical legacy vertical. Those decisions remain in the reconciliation workflow.
/// </summary>
public static class FdeCurriculumSeedData
{
    private const string CourseSlug = "fde-curriculum";

    private sealed record ModuleGuide(string Slug, string Title, string Description, string Badge, string ReferenceUrl, string DeliveryContext);
    private sealed record TopicBrief(string Focus, string Scenario, string Practice);
    private sealed record SupplementalLessonDefinition(string Title, string Focus, string CoreConcepts, string Scenario, string Practice, string Evidence, int EstimatedMinutes = 75);
    private sealed record SupplementalModuleDefinition(string Slug, string Title, string Description, string ReferenceUrl, string DeliveryContext, IReadOnlyList<SupplementalLessonDefinition> Lessons);

    private static SupplementalLessonDefinition Lesson(
        string title,
        string focus,
        string coreConcepts,
        string scenario,
        string practice,
        string evidence,
        int estimatedMinutes = 75) =>
        new(title, focus, coreConcepts, scenario, practice, evidence, estimatedMinutes);

    private static readonly IReadOnlyList<SupplementalModuleDefinition> SupplementalModules = new[]
    {
        new SupplementalModuleDefinition(
            "elective-containerization-orchestration",
            "Containerization and Orchestration",
            "Package FDE applications reproducibly, run them safely, and operate their workloads with Kubernetes primitives.",
            "https://docs.docker.com/get-started/",
            "An FDE often turns a local proof of value into a customer-managed deployment. The handoff is credible only when the image, runtime contract, security posture, and recovery path are explicit.",
            new[]
            {
                Lesson("Docker Introduction", "Understand the container boundary and the problem Docker solves for repeatable delivery.", "Images, containers, the Docker client and daemon, namespaces, cgroups, and the difference between packaging and orchestration.", "A customer prototype works on a laptop but fails during handoff because its operating-system assumptions were never captured.", "Run a small service in a container, record its inputs and outputs, and compare the container contract with the host-machine setup.", "You can explain what is isolated, what is shared with the host, and which operational concerns Docker does not solve by itself."),
                Lesson("Docker Images and Containers", "Use image layers and container lifecycle deliberately instead of treating a running container as a permanent server.", "Image manifests, layers, tags, registries, writable container layers, process lifecycles, and immutable artifact promotion.", "A support team needs to reproduce the exact build that handled a production incident weeks earlier.", "Build two image tags from a small application, inspect their layers, run each with explicit configuration, and record the digest used for the test.", "You can identify the immutable artifact, runtime configuration, persistent state, and rollback point in a deployment."),
                Lesson("Building Your Own Docker Image", "Write a small, reproducible Dockerfile that is fast to build and safe to run.", "Build context, cache ordering, multi-stage builds, dependency pinning, `.dockerignore`, entrypoints, and non-root execution.", "A customer image is large, slow to rebuild, and accidentally includes local credentials and test data.", "Create a multi-stage image, measure its size and build time, remove unnecessary context, and run it as a non-root user with a health check.", "The image can be rebuilt from a clean checkout, contains no secret or development artefact, and starts with a documented command."),
                Lesson("Images and Containers Deep Dive", "Diagnose container behaviour by separating image construction, runtime configuration, process signals, and resource limits.", "PID 1, signal propagation, environment precedence, stdout/stderr logging, CPU and memory limits, exit codes, and health checks.", "A worker ignores termination and is killed during a rollout, leaving duplicate customer jobs behind.", "Instrument a worker, send termination signals, impose a memory limit, and capture the resulting lifecycle and exit behaviour.", "You can distinguish an application bug from an image entrypoint, signal, resource-limit, or health-check problem.", 90),
                Lesson("Docker Volumes", "Choose when data belongs in a container filesystem and when it requires a durable storage boundary.", "Named volumes, bind mounts, storage ownership, backup scope, portability, and the twelve-factor boundary between code and state.", "A document-processing demo loses uploaded files whenever the container is recreated.", "Move state to a named volume, document its backup and restore path, and test recovery after removing and recreating the container.", "You can state what survives replacement, who owns the data, and how a customer would restore it."),
                Lesson("Docker Networking Deep Dive", "Design container-to-container reachability without exposing internal services unnecessarily.", "Bridge networks, service discovery, ports versus exposed ports, DNS names, network isolation, and connection troubleshooting.", "An API can reach its database from one compose service but is accidentally published to the public host.", "Create a private application network, publish only the edge service, test service-name resolution, and capture the reachable surface.", "You can trace a request from host to edge to internal service and explain why each port is or is not exposed."),
                Lesson("Hardening the Docker Environment (DevSecOps)", "Reduce container attack surface before a customer sees the first deployment.", "Minimal bases, non-root users, read-only filesystems, dropped capabilities, secret handling, SBOMs, image scanning, and signed promotion.", "A customer security review finds a root process, an unpinned base image, and credentials embedded in an image layer.", "Harden an image and runtime, scan it, inspect its metadata, and write the exceptions that still need customer approval.", "The hardening report names the remaining risks, their owners, and the evidence supporting each mitigation."),
                Lesson("Industry-Standard Container Hardening Demo", "Demonstrate a repeatable container security review that a customer team can operate after handoff.", "Threat modelling, policy checks, vulnerability severity, provenance, admission criteria, and the difference between a scanner result and exploitable risk.", "A platform team needs a short, auditable demo showing why a release is allowed or blocked.", "Create a before-and-after image, run automated checks in CI, review one false positive, and publish a release decision with evidence.", "A teammate can reproduce the checks and understand the policy threshold without relying on the original FDE."),
                Lesson("Introduction to Orchestration", "Recognize when independently managed containers need scheduling, service discovery, rollout, and recovery control.", "Desired state, reconciliation, scheduling, replica management, service identity, health signals, and the limits of manual container commands.", "A customer has several services and a worker fleet that must survive host replacement and uneven traffic.", "List the manual operations in the current deployment, map each to an orchestration capability, and identify the first workload worth migrating.", "You can justify orchestration from an operational need rather than from technology preference."),
                Lesson("Kubernetes Architecture", "Navigate the Kubernetes control plane and workload objects well enough to debug a customer deployment.", "API server, controllers, scheduler, etcd, nodes, kubelet, container runtime, desired state, and declarative reconciliation.", "A deployment is accepted by the API but never becomes ready because scheduling and node capacity were misunderstood.", "Draw the control-plane request path, deploy a small workload, inspect events, and correlate desired state with observed state.", "You can explain which component owns a failed transition and which signal would confirm the diagnosis.", 90),
                Lesson("Kubernetes Pod Deep Dive", "Use pods as the smallest scheduling and lifecycle unit without confusing them with durable application identity.", "Pod sandboxing, containers, shared network and volumes, init containers, probes, QoS, restart policy, and ephemeral identity.", "A sidecar must share files and localhost with an application, but the team expects the pod to be a permanent machine.", "Run an application with an init container and a sidecar, add readiness and liveness probes, and observe restart behaviour.", "You can choose a pod boundary, explain shared resources, and identify state that must live outside the pod.", 90),
                Lesson("ReplicaSets, Deployments, and Sidecars", "Roll out application versions safely while keeping auxiliary behaviour observable and bounded.", "ReplicaSets, Deployments, rolling strategy, revision history, sidecar responsibilities, termination order, and configuration separation.", "A customer wants request tracing added without changing application code, but the sidecar increases startup and resource cost.", "Deploy two revisions, force a failed rollout, roll back, and measure the sidecar's effect on readiness and resource requests.", "You can prove which revision served traffic and describe the failure and rollback path."),
                Lesson("Kubernetes Networking", "Reason about service discovery and ingress as explicit traffic and trust boundaries.", "Services, cluster DNS, ClusterIP, NodePort, ingress, endpoint readiness, network plugins, and east-west versus north-south traffic.", "An internal worker must call an API, while only the customer portal should be reachable from outside the cluster.", "Expose the API internally, route the portal through ingress, test readiness changes, and document the traffic policy.", "You can trace a request to its service endpoints and identify where authorization or network policy belongs.", 90),
                Lesson("Kubernetes Scaling: HPA, Cluster Autoscaler, VPA, and Karpenter", "Select a scaling mechanism based on workload signals, placement latency, and customer cost constraints.", "Pod replicas, CPU and custom metrics, HPA, node-group autoscaling, VPA recommendations, Karpenter provisioning, and stabilization windows.", "A bursty inference workload scales pods but remains pending because the cluster has no suitable capacity.", "Create a load experiment, observe pod and node signals, compare HPA with node provisioning, and record the cost and latency trade-off.", "You can state which layer is saturated, which scaler responds, and how oscillation or runaway cost is controlled.", 90),
                Lesson("Kubernetes Scaling and Network Policies", "Combine capacity planning with least-privilege traffic so scaling does not silently widen access.", "Resource requests and limits, autoscaling signals, policy selectors, ingress and egress rules, default deny, and policy testing.", "A newly scaled worker needs database access but should not reach the administrative API or the public internet.", "Apply a default-deny policy, allow the required paths, scale the workload, and test both an expected and forbidden connection.", "The deployment remains functional under scale and the policy test proves the intended blast radius."),
                Lesson("Kubernetes Security: RBAC and DevSecOps", "Make Kubernetes permissions narrow, auditable, and compatible with a customer security review.", "Users, groups, service accounts, Roles, ClusterRoles, bindings, impersonation, secret access, image policy, and admission controls.", "A debugging service account has cluster-admin permissions because a quick demo never separated observation from mutation.", "Create read-only and deployer identities, inspect their allowed verbs, remove the excessive binding, and record an emergency access path.", "You can show who can perform a privileged action, why they need it, and how that access is revoked.", 90),
                Lesson("Kubernetes Volumes", "Match workload state to a volume type and recovery contract that survives the expected failure.", "Ephemeral volumes, ConfigMaps, Secrets, PersistentVolumes, PersistentVolumeClaims, StorageClasses, access modes, and snapshots.", "A stateful processing component needs durable scratch space while credentials and configuration must be mounted separately.", "Deploy the component with a PVC, rotate a secret, simulate pod replacement, and document snapshot and restore assumptions.", "You can explain the storage lifecycle, access mode, failure domain, and backup responsibility.", 90)
            }),
        new SupplementalModuleDefinition(
            "elective-aws-multi-region-cloud-deep-dive",
            "AWS Multi-Region Cloud Deep Dive",
            "Design and operate AWS workloads across regions with explicit routing, observability, security, deployment, and recovery trade-offs.",
            "https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html",
            "A multi-region design is a customer promise about failure and recovery, not a diagram with two copies of the same stack. The FDE must make data ownership, routing, detection, promotion, and cost testable.",
            new[]
            {
                Lesson("AWS VPC and Networking Basics", "Build a private AWS network whose reachability and identity boundaries can be explained to a customer team.", "Regions, Availability Zones, VPCs, subnets, route tables, internet and NAT gateways, security groups, and network ACLs.", "A document service needs public ingress, private workers, and a database that must never receive direct internet traffic.", "Draw the packet path, implement public and private subnets in a sandbox, and test one permitted and one denied flow.", "You can identify the route, security group, and identity boundary for every important hop.", 90),
                Lesson("Advanced AWS Networking", "Choose AWS connectivity and routing patterns for hybrid, cross-account, and multi-region customer environments.", "Transit Gateway, VPC peering, PrivateLink, Route 53 routing, inter-region links, DNS failure modes, and egress control.", "A customer wants a private integration between two accounts and a regional failover path without opening broad CIDR access.", "Compare two connectivity designs, model their route tables and ownership, and run a DNS or endpoint failure drill.", "The design documents traffic ownership, blast radius, cost, and the signal that proves failover is working.", 90),
                Lesson("AWS Observability with CloudWatch", "Turn AWS service signals into a customer-facing view of health, latency, and capacity.", "Metrics, dimensions, logs, alarms, dashboards, embedded metrics, tracing boundaries, and service-level indicators.", "A customer reports intermittent slow document processing, but average latency hides a queue backlog and one unhealthy AZ.", "Define a journey-level SLI, publish service and queue metrics, build an alarm, and trace one slow request to a dependency.", "You can show the difference between symptom, cause, threshold, and customer impact."),
                Lesson("CloudWatch and CloudTrail Advanced", "Correlate operational behaviour with control-plane activity and use audit evidence during an incident.", "CloudTrail management and data events, log integrity, event history, metric filters, alarms, retention, and least-privilege investigation.", "A production role changed a security rule and the customer needs a timeline that separates intended deployment from suspicious activity.", "Enable the relevant events, create a filter and alarm, perform a controlled change, and reconstruct the actor, time, resource, and outcome.", "The investigation produces an auditable timeline without relying on a screenshot or an engineer's memory.", 90),
                Lesson("Docker App on EC2 Project", "Deploy a containerized FDE service on EC2 with a deliberate operating and recovery contract.", "AMI and instance lifecycle, IAM roles, security groups, user data, container runtime, health checks, logs, and replacement strategy.", "A customer needs a small private service quickly and has not yet adopted a managed container platform.", "Package and deploy an app, restrict inbound access, send logs to CloudWatch, replace the instance, and verify recovery from the documented steps.", "A new operator can deploy, inspect, restart, and replace the service without hand-crafted console actions.", 120),
                Lesson("AWS Lambda and API Gateway", "Use serverless boundaries when event shape, execution limits, and retry behaviour fit the customer workflow.", "Invocation models, API Gateway routes, Lambda lifecycle, timeouts, concurrency, permissions, retries, idempotency, and cold starts.", "A customer wants a low-volume upload callback that validates a document and starts asynchronous processing.", "Implement the endpoint with an idempotency key, set a timeout and permission boundary, and exercise a duplicate and a downstream failure.", "You can explain whether failure is retried, returned, or queued and how a duplicate request is made safe.", 90),
                Lesson("End-to-End Cloud Project Day", "Connect network, compute, data, identity, observability, and delivery into one evidence-backed cloud slice.", "Architecture boundaries, deployment sequencing, configuration, migrations, health checks, alarms, rollback, and handoff.", "The customer panel wants a working workflow by the end of the day and will judge operability as well as the demo path.", "Time-box discovery, deploy the smallest path, break one dependency, recover it, and finish with a one-page handoff and demo narrative.", "The project has a reproducible runbook, a failure demonstration, a measured outcome, and an explicit list of deferred risks.", 120),
                Lesson("AWS ECS and ECR Introduction", "Use ECS and ECR to create a managed container delivery path with explicit artifact and task ownership.", "Repositories, image scanning, task definitions, clusters, services, capacity providers, execution roles, and deployment revisions.", "A team is ready to leave a single EC2 host but wants a simpler operational model than a self-managed cluster.", "Push an image, define a task, run it as a service, configure health checks, and inspect a failed deployment revision.", "You can identify the image digest, task role, execution role, service health, and rollback mechanism."),
                Lesson("ECS Fundamentals", "Operate ECS services by understanding task lifecycle, placement, networking, and deployment behaviour.", "Fargate versus EC2 capacity, awsvpc networking, desired count, target groups, service discovery, rolling deployments, and task stops.", "A service scales out but tasks remain unhealthy because the target group and container port contract disagree.", "Deploy a service behind a load balancer, force a bad health check, inspect events, fix it, and verify a rolling update.", "You can diagnose a task that is pending, stopping, or unhealthy from service events and target health."),
                Lesson("EKS Basics", "Map Kubernetes concepts onto EKS without hiding AWS identity, networking, or node ownership.", "EKS control plane, node groups, IAM integration, VPC CNI, kubeconfig, add-ons, and cluster responsibility boundaries.", "A customer has Kubernetes expertise but needs an AWS deployment with clear ownership of nodes, IAM, and upgrades.", "Create or inspect a small EKS design, deploy a workload, verify identity and networking, and write the operator boundary.", "You can state what AWS manages, what the customer manages, and where an FDE should look during a failed rollout.", 90),
                Lesson("EKS Advanced", "Plan EKS capacity, upgrades, ingress, and workload placement for a customer environment that will evolve.", "Managed node groups, Fargate, taints and tolerations, cluster upgrades, ingress controllers, add-ons, and workload identity.", "A mixed workload needs isolated compute for background jobs, predictable upgrades, and a public ingress path.", "Model placement constraints, perform a staged upgrade plan, and test one workload with an explicit identity and ingress route.", "The plan includes a rollback or recovery path for control plane, node, add-on, and workload failures.", 120),
                Lesson("EKS Security and Operations", "Operate EKS with least privilege, auditable changes, and signals that reveal cluster and workload failure.", "IRSA or pod identity, Kubernetes RBAC, security groups for pods, secrets, audit logs, control-plane logging, and runbooks.", "A customer security team needs evidence that a pod can access only its assigned bucket and that administrative changes are traceable.", "Create a narrow workload identity, deny an unrelated resource, enable relevant logs, and rehearse a pod and node incident.", "You can produce evidence for identity, permission, audit, detection, and recovery without granting cluster-admin access.", 120),
                Lesson("Microservices on AWS Project", "Deliver a small multi-service workflow with service boundaries that reflect ownership and failure semantics.", "Service contracts, discovery, asynchronous events, data ownership, API gateways or load balancers, deployment units, and observability.", "A customer wants order, payment, and notification capabilities released by different teams without losing traceability.", "Build two or three services, define one synchronous and one asynchronous boundary, add correlation, and simulate a dependency outage.", "The architecture names ownership and failure behaviour, and the demo shows recovery rather than only the happy path.", 120),
                Lesson("Microservices Project: Phase 2", "Harden a multi-service design with data consistency, delivery safety, and operational feedback.", "Outbox or event publication, idempotent consumers, retries, dead letters, contract tests, capacity, and progressive delivery.", "A duplicate payment event and a delayed notification expose that the first project treated at-least-once delivery as exactly once.", "Add idempotency and a recovery queue, run contract and failure tests, and compare a canary with a full rollout.", "You can show how a message is deduplicated, retried, inspected, and replayed without corrupting business state.", 120),
                Lesson("AWS Security: Identity and Network", "Design AWS access around workload identity and network reachability rather than shared credentials.", "IAM policies, roles, trust policies, permission boundaries, VPC endpoints, security groups, private subnets, and egress control.", "A customer integration needs to read one bucket and call one private service, but the first prototype uses an admin key.", "Replace the key with a role, restrict the policy and routes, test allowed and denied actions, and document emergency access.", "The access review identifies principal, action, resource, condition, network path, and audit evidence."),
                Lesson("AWS Security: Data and Detection", "Protect customer data while making suspicious access and configuration drift detectable.", "KMS keys, envelope encryption, S3 and database controls, secret rotation, CloudTrail data events, GuardDuty signals, and retention.", "A regulated customer asks how sensitive documents are encrypted and how an unusual download would be detected.", "Classify data, choose key and retention boundaries, generate a controlled access signal, and walk through the alert response.", "You can explain protection at rest and in transit plus the evidence used to investigate a data event.", 90),
                Lesson("AWS Security Hands-on", "Demonstrate an end-to-end secure deployment and defend the decisions under customer questioning.", "Threat model, IAM, network isolation, encryption, secrets, audit, detection, patching, and security acceptance criteria.", "A customer review finds that a service is encrypted but still over-privileged and has no tested incident path.", "Run a security review against the project, fix the highest-risk findings, simulate an access incident, and present the before-and-after evidence.", "The final review distinguishes implemented controls, tested controls, residual risk, and the owner of each follow-up.", 120)
            }),
        new SupplementalModuleDefinition(
            "elective-storage-networking-reliability",
            "Storage, Networking & Reliability for FDEs",
            "Make storage, network, performance, consistency, and recovery trade-offs explicit for customer-facing systems.",
            "https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html",
            "FDE reliability work is about preserving the customer's critical workflow when data grows, dependencies slow down, or a region fails. Every design choice needs a failure model and a recovery story.",
            new[]
            {
                Lesson("Architect the Storage for an Application", "Choose storage from access patterns, durability, consistency, and recovery needs rather than from habit.", "Operational versus analytical data, object versus block versus file storage, relational and key-value access patterns, metadata, and ownership.", "A document workflow needs durable binaries, transactional status, searchable metadata, and an audit trail with different retention rules.", "Create a storage decision matrix, map each data class to a service, and test one read, write, backup, and restore assumption.", "The design explains why each datum lives where it does and what happens when that store is unavailable.", 90),
                Lesson("Data Lifecycle Management and Storage Optimization", "Control cost and risk by making data lifecycle, retention, archival, and deletion observable.", "Hot, warm, and cold data, TTLs, object lifecycle rules, compaction, partitioning, retention holds, and cost attribution.", "A customer archive grows faster than expected because temporary exports and historical versions never expire.", "Classify data, define retention and legal-hold exceptions, apply a lifecycle policy in a sandbox, and measure the resulting storage profile.", "You can show which data moves, when it is deleted, who can restore it, and how cost is attributed.", 90),
                Lesson("Backup and Disaster Recovery Strategies", "Design recovery around explicit RPO, RTO, dependency order, and verified restore evidence.", "Full and incremental backups, snapshots, point-in-time recovery, cross-region copies, immutability, restore testing, RPO, and RTO.", "A customer can take backups but has never restored the database and cannot state how much work may be lost.", "Write an RPO/RTO table, perform a restore into an isolated environment, measure it, and record the gaps between the plan and the result.", "The recovery runbook has tested commands, owners, dependency order, validation checks, and a timestamped result.", 120),
                Lesson("Designing the Networking of an Application", "Shape network paths around latency, trust, ownership, and failure domains.", "Request paths, DNS, routing, subnets, security groups, service discovery, egress, private connectivity, and network observability.", "A customer application works in one environment but has hidden cross-zone and public-egress assumptions.", "Draw the critical paths, identify every boundary, test a dependency timeout, and document the least-privilege network rule set.", "You can explain how traffic reaches each dependency and what signal distinguishes DNS, route, policy, and application failure.", 90),
                Lesson("Load Balancing and Auto Scaling Groups", "Keep service capacity and traffic distribution aligned as instances change and workloads burst.", "Health checks, target registration, connection draining, listener rules, scaling policies, warm-up, and capacity limits.", "A deployment registers new instances before the application is ready, sending users to unhealthy targets.", "Configure a meaningful health check and scaling policy, run a load test, terminate an instance, and verify draining and replacement.", "You can relate target health, scaling events, user latency, and capacity headroom in one explanation.", 90),
                Lesson("Designing for Scalability of Application and Data", "Scale the critical path by identifying its bottleneck and choosing the least complex effective boundary.", "Vertical and horizontal scaling, stateless services, queues, partitioning, read replicas, back-pressure, and capacity models.", "A customer expects ten times the traffic, but the real bottleneck is a serial database write and an unbounded in-memory queue.", "Estimate workload, model the bottleneck, add one scaling boundary, and measure throughput, latency, and failure behaviour before and after.", "The design names the bottleneck, the scaling signal, the new limit, and the operational cost of the change.", 90),
                Lesson("Database Sharding Strategies and Hot-Spot Mitigation", "Partition data without creating uneven load, cross-shard transaction traps, or an unexplainable migration.", "Shard keys, cardinality, locality, consistent hashing, rebalancing, scatter-gather queries, hot keys, and tenant isolation.", "One large customer becomes a hot partition while smaller tenants remain healthy.", "Compare candidate shard keys, simulate skew, add a mitigation such as bucketing or isolation, and write a migration plan.", "You can quantify skew, state which queries become harder, and explain how to move a hot tenant safely.", 120),
                Lesson("Edge Caching, CDNs, and Latency Reduction", "Use edge delivery and caching while preserving correctness, privacy, and invalidation semantics.", "Cache keys, TTLs, cache-control, invalidation, stale-while-revalidate, CDN origins, geographic latency, and tenant-sensitive content.", "A globally distributed portal is fast for static assets but leaks stale or cross-tenant responses through an overly broad cache key.", "Define cacheability rules, test hit and miss paths from multiple locations, invalidate a changed asset, and verify tenant separation.", "The cache policy states what may be cached, for how long, by which key, and how correctness is recovered.", 90),
                Lesson("Microservices Performance: Latency, Throughput, and Concurrency", "Measure service performance as a queueing and dependency problem rather than chasing one slow function.", "Latency percentiles, throughput, concurrency, Little's Law, connection pools, back-pressure, batching, and tail amplification.", "A workflow's average response is acceptable while p99 latency grows because each request fans out to several services.", "Profile the critical path, measure p50 and p99, vary concurrency, and identify the first saturation point and the recovery lever.", "You can connect a performance symptom to queueing, dependency, resource, or code evidence and propose a bounded fix.", 90),
                Lesson("Designing for High Availability: Multi-Region Active-Active", "Evaluate active-active architecture by data conflict, routing, operational readiness, and recovery evidence.", "Failure domains, health-based routing, replication, conflict resolution, regional independence, quorum choices, and failback.", "A customer wants users served from the nearest healthy region, but writes may arrive in both regions for the same account.", "Define the write ownership and conflict policy, simulate regional loss, measure recovery and reconciliation, and document the operator decision points.", "The design states what remains available, what may be stale or conflicted, and how the system returns to normal.", 120),
                Lesson("Fault Tolerance Engineering: Circuit Breakers, Retries, and Backoff", "Prevent a failing dependency from becoming a cascading customer outage.", "Timeout budgets, retries, exponential backoff, jitter, circuit states, bulkheads, idempotency, and retryable versus permanent errors.", "A slow billing provider causes every request thread to wait and repeated retries multiply the load.", "Add a bounded timeout and retry policy, implement a circuit breaker or bulkhead, inject failure, and observe recovery and user feedback.", "The policy documents which errors retry, the maximum work, the fallback, and the signal that closes the circuit.", 90),
                Lesson("Graceful Degradation", "Preserve the most valuable customer outcome when optional capabilities or dependencies fail.", "Critical versus optional paths, stale-but-useful data, feature flags, fallback responses, partial results, and user communication.", "An AI enrichment service is unavailable while the customer still needs to search, review, and export existing records.", "Define the minimum viable workflow, implement a feature-level fallback, inject the dependency failure, and verify that users understand the degraded state.", "You can state what is unavailable, what remains safe, and how the system signals recovery without hiding errors.", 75),
                Lesson("Rate Limiting, Throttling, and Shedding", "Protect shared capacity and make overload behaviour fair, visible, and aligned with customer priorities.", "Token and leaky buckets, concurrency limits, quotas, priority, queue admission, load shedding, 429 contracts, and tenant fairness.", "One tenant's batch import consumes every worker and makes interactive requests time out for everyone else.", "Define per-tenant limits, apply priority-aware admission, simulate overload, and inspect rejected, delayed, and completed work.", "The policy has a capacity basis, a customer-facing response, an operator signal, and a documented exception process.", 90),
                Lesson("Data Consistency Trade-offs: CAP and PACELC", "Choose consistency and latency trade-offs by business invariant and failure model, not by slogan.", "Partition tolerance, availability, consistency, latency, replica lag, quorum, read-your-writes, PACELC, and per-operation guarantees.", "A multi-region order view can tolerate slightly stale analytics but must never show a payment as settled before the authoritative record says so.", "Classify operations by invariant, choose read and write guarantees, inject partition and lag, and document the user-visible result.", "You can explain which guarantee each operation receives, what a partition changes, and why that is acceptable to the customer.", 90)
            })
    };

    private static readonly Dictionary<string, ModuleGuide> ModuleGuides = new(StringComparer.Ordinal)
    {
        ["Prerequisite: Agentic AI Core"] = new(
            "agentic-ai-core",
            "Agentic AI Core",
            "Prepare for the FDE pathway with practical GenAI, retrieval, workflow automation, and agent foundations.",
            "Prerequisite",
            "https://www.nist.gov/itl/ai-risk-management-framework",
            "An FDE needs enough AI fluency to separate a useful prototype from an unsafe or unobservable production promise."),
        ["1. FDE Foundations: Python, Workflow & Delivery"] = new(
            "fde-foundations",
            "FDE Foundations: Python, Workflow & Delivery",
            "Build the engineering habits, Python fluency, delivery discipline, and diagnostic approach needed in customer-facing work.",
            "Module 1",
            "https://docs.python.org/3/",
            "The work starts by turning an unclear customer need into a small, reproducible, well-instrumented engineering slice."),
        ["2. Backend Engineering, Observability & Advanced Data Systems"] = new(
            "backend-observability-data",
            "Backend Engineering, Observability & Data Systems",
            "Design secure APIs, dependable data systems, and observability that makes a customer deployment diagnosable.",
            "Module 2",
            "https://opentelemetry.io/docs/",
            "A customer should be able to trace an important workflow from request to data change to downstream event without guesswork."),
        ["3. Full-Stack FDE: TypeScript, React & AI-First Frontends"] = new(
            "full-stack-ai-frontends",
            "Full-Stack FDE: TypeScript, React & AI-First Frontends",
            "Build credible, accessible product surfaces that make AI-assisted workflows understandable and controllable.",
            "Module 3",
            "https://react.dev/learn",
            "A proof of value becomes persuasive when a user can understand the state, source, latency, and consequence of every action."),
        ["4. Cloud, DevOps, Kubernetes & Infrastructure"] = new(
            "cloud-devops-infrastructure",
            "Cloud, DevOps, Kubernetes & Infrastructure",
            "Operate production workloads with secure cloud foundations, repeatable delivery, and observable infrastructure.",
            "Module 4",
            "https://kubernetes.io/docs/concepts/",
            "An FDE must be able to explain how a service is deployed, secured, observed, recovered, and handed over to its operating team."),
        ["5. Enterprise Communication, Consulting & LLM Engineering"] = new(
            "enterprise-consulting-llm",
            "Enterprise Communication, Consulting & LLM Engineering",
            "Translate enterprise needs into bounded technical work and deploy LLM systems with evaluation, safety, and cost controls.",
            "Module 5",
            "https://www.nist.gov/itl/ai-risk-management-framework",
            "Good consulting makes success measurable before a model, vector store, or UI is selected."),
        ["6. Agentic Systems & Enterprise Integrations"] = new(
            "agentic-systems-integrations",
            "Agentic Systems & Enterprise Integrations",
            "Connect agentic workflows to real enterprise systems with explicit tool contracts, evaluation, and human control.",
            "Module 6",
            "https://modelcontextprotocol.io/introduction",
            "Enterprise automation succeeds when its tool boundaries, data ownership, and failure paths are more explicit than its demo script."),
        ["7. Application Engineering, Security & Reliability"] = new(
            "application-security-reliability",
            "Application Engineering, Security & Reliability",
            "Harden customer-facing applications through secure tenancy, reliable operations, documentation, and incident-ready delivery.",
            "Module 7",
            "https://owasp.org/www-project-top-ten/",
            "A customer outcome is only real when it survives load, bad input, evolving permissions, and an on-call handover."),
        ["8. System Design, Capstone & Hiring Readiness"] = new(
            "system-design-capstone",
            "System Design, Capstone & Hiring Readiness",
            "Practice architecture decisions, end-to-end delivery, and the technical communication expected of a Forward Deployed Engineer.",
            "Module 8",
            "https://aws.amazon.com/builders-library/",
            "The final test is not a whiteboard answer: it is a defensible customer solution with clear trade-offs and evidence."),
    };

    public static void Seed(StudyTrackerContext db)
    {
        var sourceVerticals = db.Verticals
            .Where(v => v.Name == "FDE Curriculum" || v.Name == "FDE Self-Study")
            .ToList();
        var curriculumCandidates = sourceVerticals.Where(v => v.Name == "FDE Curriculum").ToList();
        var selfStudyCandidates = sourceVerticals.Where(v => v.Name == "FDE Self-Study").ToList();

        if (curriculumCandidates.Count > 1 || selfStudyCandidates.Count > 1)
        {
            throw new InvalidOperationException("FDE course seeding stopped because one or more legacy FDE source names are ambiguous. Resolve the duplicate verticals first.");
        }

        var curriculumTasks = curriculumCandidates.Count == 1
            ? db.Tasks.Where(t => t.VerticalId == curriculumCandidates[0].Id).OrderBy(t => t.Id).ToList()
            : new List<StudyTask>();
        var selfStudyTasks = selfStudyCandidates.Count == 1
            ? db.Tasks.Where(t => t.VerticalId == selfStudyCandidates[0].Id).OrderBy(t => t.Id).ToList()
            : new List<StudyTask>();

        if (curriculumTasks.Count > 0 && selfStudyTasks.Count > 0 && !HaveEquivalentOutline(curriculumTasks, selfStudyTasks))
        {
            throw new InvalidOperationException("FDE course seeding stopped because FDE Curriculum and FDE Self-Study contain different task outlines. Run reconciliation and resolve the source mapping before creating canonical chapters.");
        }

        var sourceTasks = selfStudyTasks.Count > 0 ? selfStudyTasks : curriculumTasks;

        if (sourceTasks.Count == 0)
        {
            return;
        }

        var courseCandidates = db.Courses
            .Where(c => c.Slug == CourseSlug)
            .ToList();

        if (courseCandidates.Count > 1)
        {
            throw new InvalidOperationException($"Expected at most one canonical FDE course '{CourseSlug}'; found {courseCandidates.Count}.");
        }

        var course = courseCandidates.SingleOrDefault();
        if (course == null)
        {
            course = new Course
            {
                Slug = CourseSlug,
                Title = "Forward Deployed Engineer (FDE)",
                Description = "A customer-embedded engineering pathway spanning applied AI, delivery, product systems, cloud infrastructure, and enterprise integration.",
                OrderIndex = 2,
                PathType = "Specialisation",
                IsPublished = true,
                // Keep this null until the FDE Curriculum / FDE Self-Study ownership decision is verified.
                VerticalId = null
            };
            db.Courses.Add(course);
            db.SaveChanges();
        }

        var modules = db.Modules
            .Where(m => m.CourseId == course.Id)
            .ToList();

        var groups = sourceTasks
            .GroupBy(task => task.Module)
            .Select((group, index) => new { Group = group, Order = index + 1 })
            .ToList();

        foreach (var group in groups)
        {
            var guide = ResolveModuleGuide(group.Group.Key, group.Order);
            var module = modules.SingleOrDefault(m => m.Slug == guide.Slug);
            if (module == null)
            {
                module = new CourseModule
                {
                    CourseId = course.Id,
                    Slug = guide.Slug,
                    Title = guide.Title,
                    Description = guide.Description,
                    Badge = guide.Badge,
                    OrderIndex = group.Order
                };
                db.Modules.Add(module);
                modules.Add(module);
            }
            else
            {
                module.Title = guide.Title;
                module.Description = guide.Description;
                module.Badge = guide.Badge;
                module.OrderIndex = group.Order;
                module.UpdatedAt = DateTime.UtcNow;
            }
        }

        db.SaveChanges();

        var lessonModules = db.Modules
            .Where(m => m.CourseId == course.Id)
            .ToDictionary(m => m.Slug);
        var existingLessons = db.Lessons
            .Where(l => lessonModules.Values.Select(m => m.Id).Contains(l.ModuleId))
            .ToList();

        foreach (var group in groups)
        {
            var guide = ResolveModuleGuide(group.Group.Key, group.Order);
            var module = lessonModules[guide.Slug];
            var lessonIndex = 0;

            foreach (var task in group.Group)
            {
                lessonIndex++;
                var lessonSlug = $"{lessonIndex:00}-{Slugify(task.Title)}";
                var lesson = existingLessons.SingleOrDefault(l => l.ModuleId == module.Id && l.Slug == lessonSlug);
                var content = BuildLessonContent(task.Title, guide);

                if (lesson == null)
                {
                    lesson = new Lesson
                    {
                        ModuleId = module.Id,
                        Slug = lessonSlug,
                        Title = task.Title,
                        Description = BuildLessonDescription(task.Title, guide),
                        LectureNumber = lessonIndex,
                        EstimatedMinutes = EstimateMinutes(task.Title),
                        IsCompleted = task.IsCompleted,
                        OrderIndex = lessonIndex,
                        Difficulty = ResolveDifficulty(task.Title, guide.Badge),
                        ContentStatus = "Draft",
                        ContentBody = content,
                        HorstmannRef = guide.ReferenceUrl
                    };
                    db.Lessons.Add(lesson);
                    existingLessons.Add(lesson);
                }
                else
                {
                    // Populate only empty scaffold fields. Manual editorial work always wins over a seed refresh.
                    if (string.IsNullOrWhiteSpace(lesson.Description)) lesson.Description = BuildLessonDescription(task.Title, guide);
                    if (string.IsNullOrWhiteSpace(lesson.ContentBody)) lesson.ContentBody = content;
                    if (string.IsNullOrWhiteSpace(lesson.HorstmannRef)) lesson.HorstmannRef = guide.ReferenceUrl;
                    lesson.UpdatedAt = DateTime.UtcNow;
                }
            }
        }

        EnsureSupplementalModules(db, course);
        EnsureDomainLinks(db, course);
        db.SaveChanges();
    }

    private static void EnsureSupplementalModules(StudyTrackerContext db, Course course)
    {
        var existingModules = db.Modules
            .Where(module => module.CourseId == course.Id)
            .ToList();
        var supplementalSlugs = SupplementalModules
            .Select(module => module.Slug)
            .ToHashSet(StringComparer.Ordinal);
        var lastExistingOrder = existingModules
            .Where(module => !supplementalSlugs.Contains(module.Slug))
            .Select(module => module.OrderIndex)
            .DefaultIfEmpty(0)
            .Max();

        for (var moduleIndex = 0; moduleIndex < SupplementalModules.Count; moduleIndex++)
        {
            var definition = SupplementalModules[moduleIndex];
            var module = existingModules.SingleOrDefault(candidate => candidate.Slug == definition.Slug);
            if (module == null)
            {
                module = new CourseModule
                {
                    CourseId = course.Id,
                    Slug = definition.Slug,
                    Title = definition.Title,
                    Description = definition.Description,
                    Badge = "Elective",
                    OrderIndex = lastExistingOrder + moduleIndex + 1
                };
                db.Modules.Add(module);
                existingModules.Add(module);
            }
        }

        db.SaveChanges();

        var modulesBySlug = db.Modules
            .Where(module => module.CourseId == course.Id && supplementalSlugs.Contains(module.Slug))
            .ToDictionary(module => module.Slug, StringComparer.Ordinal);
        var moduleIds = modulesBySlug.Values.Select(module => module.Id).ToList();
        var existingLessons = db.Lessons
            .Where(lesson => moduleIds.Contains(lesson.ModuleId))
            .ToList();

        foreach (var definition in SupplementalModules)
        {
            var module = modulesBySlug[definition.Slug];
            for (var lessonIndex = 0; lessonIndex < definition.Lessons.Count; lessonIndex++)
            {
                var lessonDefinition = definition.Lessons[lessonIndex];
                var lessonSlug = $"{lessonIndex + 1:00}-{Slugify(lessonDefinition.Title)}";
                var lesson = existingLessons.SingleOrDefault(candidate =>
                    candidate.ModuleId == module.Id && candidate.Slug == lessonSlug);
                var content = BuildSupplementalLessonContent(lessonDefinition, definition);

                if (lesson == null)
                {
                    lesson = new Lesson
                    {
                        ModuleId = module.Id,
                        Slug = lessonSlug,
                        Title = lessonDefinition.Title,
                        Description = lessonDefinition.Focus,
                        LectureNumber = lessonIndex + 1,
                        EstimatedMinutes = lessonDefinition.EstimatedMinutes,
                        IsCompleted = false,
                        OrderIndex = lessonIndex + 1,
                        Difficulty = ResolveSupplementalDifficulty(lessonDefinition.Title),
                        ContentStatus = "Draft",
                        ContentBody = content,
                        HorstmannRef = ResolveSupplementalReference(lessonDefinition.Title, definition)
                    };
                    db.Lessons.Add(lesson);
                    existingLessons.Add(lesson);
                }
                else
                {
                    // Supplemental content is additive. Existing editorial text and progress always win.
                    if (string.IsNullOrWhiteSpace(lesson.Description)) lesson.Description = lessonDefinition.Focus;
                    if (string.IsNullOrWhiteSpace(lesson.ContentBody)) lesson.ContentBody = content;
                    if (string.IsNullOrWhiteSpace(lesson.HorstmannRef))
                    {
                        lesson.HorstmannRef = ResolveSupplementalReference(lessonDefinition.Title, definition);
                    }
                    lesson.UpdatedAt = DateTime.UtcNow;
                }
            }
        }

        db.SaveChanges();
    }

    private static string BuildSupplementalLessonContent(
        SupplementalLessonDefinition lesson,
        SupplementalModuleDefinition module)
    {
        var referenceUrl = ResolveSupplementalReference(lesson.Title, module);
        return $@"# {lesson.Title}

{lesson.Focus}

## Core concepts

{lesson.CoreConcepts}

## Why it matters in an FDE engagement

{module.DeliveryContext}

## Worked FDE scenario

{lesson.Scenario}

## Practice loop

1. {lesson.Practice}
2. Capture the assumptions, owner, success signal, and failure boundary before changing the design.
3. Demonstrate one successful path and one deliberately uncomfortable failure path to a teammate or customer stakeholder.

## Evidence of understanding

- {lesson.Evidence}
- You can explain the trade-off in plain language as well as technical language.
- You have a small artefact: a diagram, test, policy, query, deployment note, runbook, or measured experiment.
- You can name the next signal you would inspect if the customer outcome degraded.

## Continue learning

- Primary reference: {referenceUrl}
- Treat this chapter as a working draft and add customer-specific constraints, measurements, and implementation notes during review.";
    }

    private static string ResolveSupplementalReference(
        string title,
        SupplementalModuleDefinition module)
    {
        if (module.Slug == "elective-containerization-orchestration")
        {
            if (Contains(title, "Kubernetes") || Contains(title, "Orchestration") || Contains(title, "ReplicaSet") || Contains(title, "Scaling") || Contains(title, "Pod") || Contains(title, "RBAC"))
            {
                return "https://kubernetes.io/docs/concepts/";
            }

            if (Contains(title, "Volume")) return "https://docs.docker.com/engine/storage/";
            if (Contains(title, "Networking")) return "https://docs.docker.com/engine/network/";
            return "https://docs.docker.com/get-started/";
        }

        if (module.Slug == "elective-aws-multi-region-cloud-deep-dive")
        {
            if (Contains(title, "VPC") || Contains(title, "Networking")) return "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html";
            if (Contains(title, "CloudWatch") || Contains(title, "Observability")) return "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html";
            if (Contains(title, "CloudTrail") || Contains(title, "Security")) return "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html";
            if (Contains(title, "Lambda") || Contains(title, "API Gateway")) return "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html";
            if (Contains(title, "EKS")) return "https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html";
            if (Contains(title, "ECS") || Contains(title, "ECR")) return "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html";
            return "https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html";
        }

        if (Contains(title, "Storage") || Contains(title, "Backup") || Contains(title, "Disaster Recovery"))
        {
            return "https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html";
        }

        if (Contains(title, "Networking") || Contains(title, "Load Balancing") || Contains(title, "CDN") || Contains(title, "Caching"))
        {
            return "https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html";
        }

        return module.ReferenceUrl;
    }

    private static string ResolveSupplementalDifficulty(string title)
    {
        if (Contains(title, "Project") || Contains(title, "Advanced") || Contains(title, "High Availability") || Contains(title, "Sharding") || Contains(title, "Disaster") || Contains(title, "Hands-on"))
        {
            return "Advanced";
        }

        return "Intermediate";
    }

    private static ModuleGuide ResolveModuleGuide(string legacyModule, int order)
    {
        if (ModuleGuides.TryGetValue(legacyModule, out var guide)) return guide;

        var title = Regex.Replace(legacyModule, @"^\d+\.\s*", string.Empty).Trim();
        return new ModuleGuide(
            $"module-{order:00}-{Slugify(title)}",
            title,
            "A focused FDE learning module prepared from the legacy curriculum outline.",
            $"Module {order}",
            "https://www.nist.gov/itl/ai-risk-management-framework",
            "Use this module to turn a delivery question into a measurable engineering outcome.");
    }

    private static void EnsureDomainLinks(StudyTrackerContext db, Course course)
    {
        var desiredSlugs = new[] { "agentic-ai", "foundations", "backend", "full-stack", "cloud", "enterprise", "agent-systems", "reliability" };
        var domains = db.KnowledgeDomains.Where(d => desiredSlugs.Contains(d.Slug)).ToList();

        foreach (var domain in domains)
        {
            if (db.CourseDomainLinks.Any(link => link.CourseId == course.Id && link.DomainId == domain.Id)) continue;

            db.CourseDomainLinks.Add(new CourseDomainLink
            {
                CourseId = course.Id,
                DomainId = domain.Id,
                IsPrimary = domain.Slug == "foundations",
                OrderIndex = Array.IndexOf(desiredSlugs, domain.Slug),
                CreatedAt = DateTime.UtcNow
            });
        }
    }

    private static string BuildLessonDescription(string title, ModuleGuide guide)
    {
        var brief = ResolveTopicBrief(title, guide);
        return brief.Focus;
    }

    private static string BuildLessonContent(string title, ModuleGuide guide)
    {
        var brief = ResolveTopicBrief(title, guide);
        return $@"# {title}

{brief.Focus}

## Core concepts

{ResolveCoreConcepts(title)}

## Why it matters in an FDE engagement

{guide.DeliveryContext}

## Worked scenario

{brief.Scenario}

## Practice loop

1. {brief.Practice}
2. Write down the assumptions, inputs, owners, and failure conditions before optimising the solution.
3. Demonstrate the result to a teammate or stakeholder with one success case and one deliberately uncomfortable edge case.

## Evidence of understanding

- {ResolveEvidence(title)}
- You can explain the trade-off in plain language as well as technical language.
- You have a small artefact: a diagram, test, query, deployment note, decision record, or working slice.
- You can name the next signal you would inspect if the customer outcome degraded.

## Continue learning

- Primary reference: {guide.ReferenceUrl}
- Treat this chapter as a working draft. Improve it with your own implementation notes, measurements, and customer-specific constraints.";
    }

    private static string ResolveCoreConcepts(string title)
    {
        if (Contains(title, "The FDE Role")) return
            "- Customer-embedded ownership: clarify the outcome, constraints, and handoff boundary.\n- The FDE loop: discover, prototype, instrument, validate, and enable the customer team.\n- Delivery judgment: optimise for a useful, operable slice before broad platform completeness.";
        if (Contains(title, "Problem Discovery")) return
            "- User pain versus requested feature.\n- Observable success measures and acceptance criteria.\n- Assumptions, constraints, risks, and the smallest test that can reduce uncertainty.";
        if (Contains(title, "Python Toolchain")) return
            "- Isolated interpreters and reproducible dependency locking.\n- Formatting, linting, static typing, and the boundary between local convenience and CI truth.\n- A repeatable command surface that another engineer can run without knowing the author's machine.";
        if (Contains(title, "GenAI") || Contains(title, "LLM Landscape")) return
            "- Model capabilities, context limits, latency, cost, and data-handling boundaries.\n- Predictive text versus retrieval, tools, workflows, and agents.\n- A customer outcome is the selection criterion, not novelty of the model.";
        if (Contains(title, "LLM Built-in")) return
            "- Structured generation, tool use, embeddings, vision, and model-provided capabilities.\n- Capability limits and fallback behaviour.\n- Separating a useful built-in primitive from a production-ready workflow.";
        if (Contains(title, "Prompting") || Contains(title, "Prompt Engineering")) return
            "- Task framing, context, examples, constraints, output schemas, and refusal behaviour.\n- Prompt versions and representative evaluation cases.\n- The prompt is one component of a controlled application boundary.";
        if (Contains(title, "RAG")) return
            "- Source ingestion, chunking, metadata, embeddings, retrieval, grounding, citations, and no-answer behaviour.\n- Retrieval quality separated from answer quality.\n- Customer data access enforced before context reaches a model.";
        if (Contains(title, "n8n")) return
            "- Triggers, state transitions, credentials, branching, retries, approvals, and idempotency.\n- Workflow automation as an explicit integration surface.\n- Human control for consequential customer actions.";
        if (Contains(title, "What Is an AI Agent") || Contains(title, "Building Agents") || Contains(title, "OpenClaw")) return
            "- An agent combines a model with state, tools, policies, and a termination condition.\n- Observe, decide, act, verify, and recover as distinct steps.\n- Autonomy must be bounded by permissions, budgets, and human escalation.";
        if (Contains(title, "Debugging AI")) return
            "- Retrieval, prompt, model, tool, policy, and rendering layers.\n- Trace evidence and a reproducible failure case.\n- Targeted experiments that distinguish a bad input from a bad decision.";
        if (Contains(title, "Iterators") || Contains(title, "Closures")) return
            "- Lazy evaluation and state carried across iterations.\n- Function scope, captured variables, decorators, and resource lifetime.\n- The operational difference between streaming work and materialising an entire dataset.";
        if (Contains(title, "OOP, Concurrency")) return
            "- Composition and ownership of mutable state.\n- Cooperative async execution, cancellation, back-pressure, and blocking work.\n- Explicit lifecycle boundaries for customer requests and background tasks.";
        if (Contains(title, "Pydantic")) return
            "- Boundary validation versus internal domain invariants.\n- Structured logs with correlation and customer-safe fields.\n- Profiling as measurement of a real bottleneck, not premature optimisation.";
        if (Contains(title, "Git Internals")) return
            "- Objects, refs, commits, branches, and the graph that makes changes recoverable.\n- Small reviewable changes and automated checks.\n- AI-assisted coding with human ownership of context, secrets, and final diffs.";
        if (Contains(title, "Testing:")) return
            "- Example-based tests for contracts and property-based tests for invariants.\n- Unit, integration, and end-to-end boundaries.\n- CI as a feedback system that protects delivery speed rather than a ceremonial gate.";
        if (Contains(title, "SOLID") || Contains(title, "Hexagonal")) return
            "- Business rules separated from transport, persistence, and vendor adapters.\n- Dependency inversion and ports-and-adapters boundaries.\n- Design for replacement, testing, and incremental customer-specific change.";
        if (Contains(title, "Linux, Shell")) return
            "- Processes, files, pipes, exit codes, signals, and environment variables.\n- Safe composition of small commands and explicit failure handling.\n- Diagnostics that can be copied into a ticket or runbook.";
        if (Contains(title, "HTTP") || Contains(title, "FastAPI")) return
            "- Resources, methods, status codes, idempotency, pagination, and error contracts.\n- Dependency injection and validation at the API boundary.\n- Authentication and authorization as separate decisions.";
        if (Contains(title, "OAuth2") || Contains(title, "JWT") || Contains(title, "OIDC") || Contains(title, "RBAC")) return
            "- Authentication, token claims, scopes, sessions, and identity-provider trust.\n- Authorization as a server-side policy decision.\n- Tenant, role, and audit context carried through every privileged action.";
        if (Contains(title, "Order Management")) return
            "- Explicit order state transitions and invariants.\n- Idempotency keys, optimistic concurrency, and audit history.\n- API behaviour that keeps retries from creating duplicate business effects.";
        if (Contains(title, "Payments")) return
            "- Payment intent versus payment confirmation.\n- Webhook verification, idempotency, retries, and reconciliation.\n- Background work that can be observed without blocking the customer request.";
        if (Contains(title, "Demo Frontend")) return
            "- A thin vertical slice across API, state, UI, and error handling.\n- Loading, empty, success, and failure states.\n- A demo narrative tied to a measurable user task, not a collection of disconnected screens.";
        if (Contains(title, "Real-Time") || Contains(title, "Queues") || Contains(title, "Caching")) return
            "- Push versus pull delivery, acknowledgement, ordering, and retry semantics.\n- Queue ownership, dead-letter handling, and duplicate events.\n- Cache key, freshness, invalidation, and the user-visible meaning of stale data.";
        if (Contains(title, "Observability") || Contains(title, "Tracing") || Contains(title, "Logging") || Contains(title, "Profiling")) return
            "- Signals: logs for detail, metrics for trends, traces for causality.\n- Correlation identifiers and context propagation.\n- Service-level indicators connected to a customer journey.";
        if (Contains(title, "Postgres Advanced")) return
            "- JSONB indexing and containment queries.\n- Full-text search versus vector similarity search.\n- Query shape, metadata filters, and retrieval quality for customer evidence.";
        if (Contains(title, "Postgres Internals")) return
            "- Query plans, selectivity, indexes, locks, and MVCC snapshots.\n- EXPLAIN ANALYZE as an evidence-driven tuning loop.\n- The difference between a fast local query and a safe production query under contention.";
        if (Contains(title, "NoSQL")) return
            "- Access-pattern-first modelling, partitioning, consistency, and document boundaries.\n- Vector index recall, filtering, and freshness.\n- Choosing a data store by workload and recovery contract.";
        if (Contains(title, "Dimensional Modeling")) return
            "- Facts, dimensions, grain, keys, and slowly changing business meaning.\n- Transformations, lineage, tests, and incremental models.\n- Separating operational truth from reporting-friendly projections.";
        if (Contains(title, "Airflow")) return
            "- DAG tasks, dependencies, retries, backfills, schedules, and data-quality gates.\n- Idempotent transformations and late-arriving data.\n- Ownership and alerting for a pipeline that a customer can trust.";
        if (Contains(title, "Kafka")) return
            "- Topics, partitions, consumer groups, offsets, ordering, and retention.\n- At-least-once delivery and idempotent consumers.\n- Schema evolution and replay as operational capabilities.";
        if (Contains(title, "TypeScript")) return
            "- Structural typing, unions, narrowing, generics, and runtime validation.\n- Types as communication between frontend and API teams.\n- The limit of compile-time safety when data comes from a customer or network.";
        if (Contains(title, "React Essentials")) return
            "- Component boundaries, props, state, effects, and controlled inputs.\n- Async state and optimistic versus confirmed UI.\n- Accessible interaction states for a user who is waiting on an AI workflow.";
        if (Contains(title, "Next.js")) return
            "- Server and client boundaries, routing, data loading, and caching.\n- Environment and secret boundaries.\n- Rendering choices based on freshness, interactivity, and customer data sensitivity.";
        if (Contains(title, "Vercel AI SDK")) return
            "- Token streaming, partial state, cancellation, and reconnect behavior.\n- Structured messages and tool results that the UI can render safely.\n- The distinction between a stream being open and an answer being trustworthy.";
        if (Contains(title, "AI Product UX") || Contains(title, "Frontend Essentials")) return
            "- User intent, confidence, source evidence, review, and recovery.\n- Progressive disclosure for complex AI behavior.\n- Accessible, keyboard-friendly, and honest feedback during partial failure.";
        if (Contains(title, "AWS Core")) return
            "- IAM principals, policies, roles, and least privilege.\n- VPC subnets, routes, security groups, and private versus public reachability.\n- Cloud operations as identity plus network plus observability.";
        if (Contains(title, "Compute, Storage")) return
            "- Compute lifecycle, object durability, relational transactions, and queue delivery.\n- Managed service boundaries and shared responsibility.\n- Mapping workload characteristics to scaling, recovery, and cost behaviour.";
        if (Contains(title, "AWS Security")) return
            "- Key ownership, envelope encryption, secret rotation, and audit trails.\n- Credential exposure paths and workload identity.\n- Evidence that a sensitive customer action was allowed or denied for the right reason.";
        if (Contains(title, "Docker")) return
            "- Image layers, reproducible builds, non-root execution, and runtime configuration.\n- Health checks, signal handling, resource limits, and graceful shutdown.\n- The difference between a container image and a production deployment.";
        if (Contains(title, "Kubernetes Architecture")) return
            "- Control plane reconciliation, desired state, pods, deployments, and services.\n- Readiness versus liveness and rollout history.\n- Scheduling and resource requests as customer-impacting decisions.";
        if (Contains(title, "EKS") || Contains(title, "Helm")) return
            "- Cluster ownership, namespaces, charts, values, ingress, and workload identity.\n- Rollout, rollback, and version compatibility.\n- A deployment handover that names what the customer team operates.";
        if (Contains(title, "Kubernetes Networking")) return
            "- Service discovery, ingress, network policies, and pod-to-pod reachability.\n- Secret and identity boundaries for workloads.\n- GPU scheduling and capacity as a product latency constraint.";
        if (Contains(title, "CI/CD") || Contains(title, "GitOps")) return
            "- Build, test, artifact promotion, deployment, verification, and rollback.\n- Declarative desired state and environment-specific configuration.\n- Approval and audit boundaries for customer production changes.";
        if (Contains(title, "Terraform")) return
            "- Resources, state, modules, plans, drift, and safe change sequencing.\n- Inputs and outputs as an infrastructure contract.\n- Reviewable infrastructure changes with recovery for partial apply.";
        if (Contains(title, "Serverless")) return
            "- Event triggers, execution limits, retries, idempotency, and orchestration state.\n- Synchronous API response versus asynchronous completion.\n- Cost and cold-start effects on a customer workflow.";
        if (Contains(title, "SRE")) return
            "- Service-level objectives, error budgets, toil, and incident ownership.\n- Reliability as a measurable customer promise.\n- Recovery, runbooks, and escalation paths.";
        if (Contains(title, "Customer Discovery") || Contains(title, "Scoping") || Contains(title, "Stakeholder") || Contains(title, "Demo Storytelling")) return
            "- Outcome, user, workflow, constraint, measure, and decision owner.\n- Options, risks, assumptions, dependencies, and non-goals.\n- Communication as a mechanism for reducing technical ambiguity.";
        if (Contains(title, "LLM Fundamentals")) return
            "- Tokens, context windows, sampling, embeddings, tool calls, and model limits.\n- Capability, latency, quality, privacy, and cost trade-offs.\n- Evaluation before model selection or prompt tuning.";
        if (Contains(title, "Prompt Engineering")) return
            "- Role and task framing, grounded context, examples, output schemas, and refusal rules.\n- Prompt versioning and regression cases.\n- Prompt changes as product changes that require evaluation.";
        if (Contains(title, "RAG Architecture")) return
            "- Ingestion, parsing, chunking, metadata, embeddings, retrieval, reranking, and generation.\n- Citation and source-boundary requirements.\n- Retrieval quality separated from answer quality.";
        if (Contains(title, "RAG over Customer")) return
            "- Tenant-aware document access, hybrid search, filters, freshness, and citations.\n- Source authority and conflicting documents.\n- Retrieval failures that should produce a transparent no-answer.";
        if (Contains(title, "RAG Evaluation")) return
            "- Dataset design, faithfulness, context relevance, answer relevance, and human review.\n- Slice-based evaluation by customer workflow and risk.\n- Iteration driven by a failure taxonomy rather than a single score.";
        if (Contains(title, "LLM Safety")) return
            "- Prompt injection, data leakage, unsafe tool use, output validation, and human review.\n- Threat modelling and defence in depth.\n- Safety controls that are observable and testable.";
        if (Contains(title, "Cost, Latency")) return
            "- Token budgets, batching, caching, routing, timeouts, and fallbacks.\n- Quality thresholds for model substitution.\n- Cost and latency measured per customer task, not only per API call.";
        if (Contains(title, "Tool Calling") || Contains(title, "Structured Output")) return
            "- JSON schema, validation, tool permissions, retries, and idempotency.\n- Planning versus execution boundaries.\n- Dry-run and approval modes for consequential actions.";
        if (Contains(title, "Agentic Patterns")) return
            "- State machines, planning loops, bounded context, memory, and termination.\n- Tool authority and recovery from partial completion.\n- Deterministic workflow steps around probabilistic model decisions.";
        if (Contains(title, "Agent Debugging")) return
            "- Trace spans for model, retrieval, tool, policy, and UI layers.\n- Failure taxonomy, reproducible evaluations, and counterexamples.\n- Debugging the first incorrect decision rather than the final symptom.";
        if (Contains(title, "MCP")) return
            "- Discoverable tools, resources, prompts, schemas, and transport boundaries.\n- Capability negotiation and least-authority integration.\n- Auditability when an agent accesses customer systems.";
        if (Contains(title, "Multi-Agent")) return
            "- Delegation, shared state, coordination, arbitration, and termination.\n- Human approval for high-impact steps.\n- Preventing duplicated work and conflicting agent actions.";
        if (Contains(title, "Enterprise Systems") || Contains(title, "API Integration")) return
            "- System ownership, source of truth, contracts, identity, rate limits, and change management.\n- Connector boundaries and anti-corruption layers.\n- Integration topology drawn from actual business workflows.";
        if (Contains(title, "Integration Failure") || Contains(title, "Entity Resolution")) return
            "- Timeouts, retries, dead letters, duplicates, stale records, and reconciliation.\n- Matching confidence and human review for ambiguous entities.\n- Failure evidence that lets two system owners collaborate.";
        if (Contains(title, "CRM-to-AI")) return
            "- CRM read authority, retrieval grounding, ticket-write permissions, and approval.\n- Entity resolution and idempotent follow-up actions.\n- End-to-end trace from customer record to generated recommendation to human decision.";
        if (Contains(title, "Product Thinking")) return
            "- User journey, domain model, permission boundary, feedback loop, and handover.\n- Thin-slice architecture that can grow without hiding risk.\n- Product decisions expressed as measurable behaviour.";
        if (Contains(title, "Multi-Tenant")) return
            "- Tenant identity propagation, row-level isolation, background-job ownership, and noisy-neighbor controls.\n- Secure defaults at every query and worker boundary.\n- Testing that proves one tenant cannot observe another tenant's work.";
        if (Contains(title, "Document Processing")) return
            "- Upload validation, parsing, extraction, confidence, provenance, and human review.\n- Asynchronous workflow state and repeatable reprocessing.\n- Separating extracted data from approved business truth.";
        if (Contains(title, "Developer Experience")) return
            "- Contract-first API documentation, examples, error semantics, authentication, and changelogs.\n- A first-success path for the next engineer.\n- Documentation tested as part of delivery.";
        if (Contains(title, "Enterprise Security")) return
            "- Data classification, PII minimisation, access review, retention, audit, and incident response.\n- Security controls mapped to customer obligations.\n- Evidence for compliance conversations without claiming certification.";
        if (Contains(title, "Secrets, Encryption")) return
            "- Secret lifecycle, key hierarchy, encryption in transit and at rest, and deployment trust zones.\n- Rotation without downtime.\n- Topology decisions that make blast radius explicit.";
        if (Contains(title, "Load Testing")) return
            "- Workload model, concurrency, saturation, latency percentiles, throughput, and bottleneck.\n- Capacity assumptions and headroom.\n- Load tests that resemble a customer journey rather than an isolated endpoint.";
        if (Contains(title, "Incident Response")) return
            "- Detection, triage, mitigation, communication, recovery, and learning.\n- Customer-facing facts separated from internal hypotheses.\n- RCA focused on contributing conditions and prevention, not blame.";
        if (Contains(title, "Enterprise Readiness")) return
            "- Functional acceptance, security, observability, support, runbooks, backups, and rollback.\n- Named owners and evidence for each go-live criterion.\n- Handover as a product deliverable.";
        if (Contains(title, "Distributed Systems")) return
            "- Failure, partitions, consistency, availability, latency, and coordination.\n- CAP, PACELC, Raft, and Saga as decision tools rather than slogans.\n- Recovery and compensation paths for an incomplete workflow.";
        if (Contains(title, "System Design: RAG")) return
            "- Ingestion scale, index freshness, tenant isolation, retrieval latency, evaluation, and cost.\n- Query path versus ingestion path.\n- Degraded behaviour when sources are stale or unavailable.";
        if (Contains(title, "System Design: Agentic")) return
            "- Agent runtime, tool gateway, state, policy, evaluation, tracing, and human escalation.\n- Bounded autonomy and replayable decisions.\n- Capacity and failure isolation across model and enterprise dependencies.";
        if (Contains(title, "System Design: Multi-Tenant")) return
            "- Tenant isolation, workload fairness, data lifecycle, authorization, queues, and observability.\n- Control plane versus data plane.\n- Trade-offs between shared infrastructure and dedicated isolation.";
        if (Contains(title, "System Design: Enterprise Integration")) return
            "- Connector registry, schema translation, identity, rate limits, retries, reconciliation, and audit.\n- Ownership across system boundaries.\n- A topology that supports adding integrations without multiplying failure modes.";
        if (Contains(title, "Interview Readiness")) return
            "- Clarify requirements, state assumptions, design the critical path, identify bottlenecks, and validate.\n- Trade-off vocabulary grounded in user and operational outcomes.\n- Clear communication under time pressure.";
        if (Contains(title, "Capstone")) return
            "- Discovery, architecture, vertical delivery, integration, security, observability, evaluation, and handover.\n- Milestones that create evidence before the final demo.\n- Scope control when requirements change.";
        if (Contains(title, "Mock Engagement") || Contains(title, "Graduation Review")) return
            "- End-to-end FDE behaviour: clarify, build, diagnose, communicate, and transfer ownership.\n- Portfolio evidence and decision records.\n- Honest treatment of limitations, unresolved risks, and next steps.";

        return $"- Identify the purpose, inputs, outputs, invariants, and failure modes of {title}.\n- Connect the technical mechanism to a customer workflow and an observable outcome.\n- Record the assumptions that must be validated before production use.";
    }

    private static string ResolveEvidence(string title)
    {
        if (Contains(title, "Assessment") || Contains(title, "Capstone") || Contains(title, "Build:") || Contains(title, "Mock Engagement") || Contains(title, "Graduation Review"))
            return "You can present a working slice, its acceptance evidence, known limitations, operating notes, and the next decision a customer should make.";
        if (Contains(title, "Discovery") || Contains(title, "Scoping") || Contains(title, "Stakeholder") || Contains(title, "Demo"))
            return "You can turn a customer conversation into a one-page brief with a measurable outcome, explicit non-goals, risks, owners, and a credible next step.";
        if (Contains(title, "System Design") || Contains(title, "Distributed Systems"))
            return "You can defend the architecture against one scale assumption and one failure scenario, including what you would measure after launch.";
        if (Contains(title, "Security") || Contains(title, "Secrets") || Contains(title, "Auth") || Contains(title, "RBAC"))
            return "You can demonstrate an allowed action, a denied action, the audit evidence for both, and the recovery path if a credential or policy is wrong.";
        if (Contains(title, "Observability") || Contains(title, "Tracing") || Contains(title, "Logging") || Contains(title, "Incident") || Contains(title, "SRE"))
            return "You can use the captured signals to locate a deliberately introduced failure and explain the customer impact without guessing.";
        return "You can complete the practice task, explain one deliberate edge case, and show the artefact or measurement that proves the capability works.";
    }

    private static TopicBrief ResolveTopicBrief(string title, ModuleGuide guide)
    {
        if (Contains(title, "The FDE Role")) return new TopicBrief(
            "Understand the Forward Deployed Engineer as the bridge between a customer's ambiguous workflow and a dependable technical outcome.",
            "A customer describes a painful process but cannot yet name the right product or architecture. The FDE earns trust by observing the workflow, narrowing the first experiment, and staying accountable through validation and handover.",
            "Write a one-page engagement brief with the user, current workflow, desired outcome, constraints, success measure, first slice, owner, and explicit non-goals.");
        if (Contains(title, "Problem Discovery")) return new TopicBrief(
            "Turn an observed customer problem into a testable solution hypothesis without prematurely committing to a framework, model, or feature list.",
            "An operations team requests an AI assistant because analysts spend hours searching. Interview two users, map the actual search-and-decision workflow, and separate the expensive step from the merely visible step.",
            "Create a problem statement, assumption log, opportunity-solution tree, and smallest validation experiment; include one plausible solution that you deliberately reject and why.");
        if (Contains(title, "Python Toolchain")) return new TopicBrief(
            "Make Python delivery reproducible across an FDE laptop, CI, staging, and the customer's environment.",
            "A prototype works locally but a handoff fails because Python versions, dependencies, lint rules, and environment variables differ. The fix is a repeatable toolchain contract, not another manual setup note.",
            "Create a clean environment with a locked dependency set, add ruff and mypy checks, run them in CI, and write the exact setup and verification commands for the next engineer.");
        if (Contains(title, "Assessment") || Contains(title, "Capstone") || Contains(title, "Mock Engagement") || Contains(title, "Graduation Review"))
        {
            return new TopicBrief(
                "Use this checkpoint to prove you can make engineering decisions under real delivery constraints, not simply recall vocabulary.",
                "A client sponsor asks for a short demonstration by Friday. The team must scope the smallest credible workflow, document its risks, and show evidence that it can be operated after the demo.",
                "Time-box the work, define an acceptance checklist, capture a decision log, and finish with a short retrospective covering what failed, what changed, and what should be handed over.");
        }

        if (Contains(title, "GenAI") || Contains(title, "LLM Landscape") || Contains(title, "LLM Built-in") || Contains(title, "LLM Fundamentals")) return new TopicBrief(
            "Choose an AI capability by matching task shape, data sensitivity, evaluation needs, latency, and operating cost to the customer outcome.",
            "A team asks for a general-purpose chatbot, but their actual need is a constrained policy lookup with an audit trail. The FDE must make the capability boundary visible before selecting a model.",
            "Write a one-page capability brief: user action, allowed evidence, unacceptable failure, expected response time, and how quality will be evaluated.");
        if (Contains(title, "RAG")) return new TopicBrief(
            "Design retrieval as an evidence pipeline: define the knowledge boundary, retrieve relevant sources, and make answer quality measurable before expanding the system.",
            "A support team wants answers grounded only in approved product policy. Compare a keyword-only baseline with hybrid retrieval, preserve citations to source chunks, and record the cases where either approach fails.",
            "Create a 20-question evaluation set from real support scenarios, record retrieval context and answer quality separately, then improve one failure mode at a time.");
        if (Contains(title, "Prompt")) return new TopicBrief(
            "Treat prompts as versioned interface contracts with clear inputs, structured outputs, evaluation cases, and explicit safety boundaries.",
            "A customer asks for an incident-summary assistant. The assistant must distinguish facts from assumptions, refuse to invent missing evidence, and return a schema the UI can render safely.",
            "Write three representative prompts, define a JSON response shape, create adversarial inputs, and compare output quality after each small change.");
        if (Contains(title, "n8n")) return new TopicBrief(
            "Use workflow automation to make state transitions, approvals, credentials, and retries visible rather than hiding delivery logic in a single opaque flow.",
            "A customer wants inbound feedback routed to the right team. The workflow must classify the request, tolerate a temporary CRM outage, and require a human approval for high-impact actions.",
            "Draw the trigger, state, tool call, retry, and human-approval boundary; then replay a duplicate event and a downstream timeout.");
        if (Contains(title, "Debugging AI")) return new TopicBrief(
            "Debug AI-assisted workflows by separating retrieval, prompt, model, tool, and user-interface failures instead of treating every bad answer as a model problem.",
            "A response is wrong even though the source document is correct. Inspect the retrieved chunks, prompt version, tool trace, model output, and rendered answer in that order.",
            "Capture one failed interaction end to end, label the failing layer, and write a targeted experiment that could falsify your first explanation.");
        if (Contains(title, "Agent") || Contains(title, "Tool Calling") || Contains(title, "MCP")) return new TopicBrief(
            "Build agentic behavior from explicit state, narrow tool contracts, bounded authority, and traces that let a human reconstruct every decision.",
            "A procurement copilot may search contracts and draft a recommendation, but must request approval before creating a ticket or changing a vendor record.",
            "Model the workflow as observe, decide, act, and verify; add a dry-run mode; then test malformed tool responses, permission failures, and repeated actions.");
        if (Contains(title, "Python") || Contains(title, "Iterators") || Contains(title, "Closures") || Contains(title, "Pydantic") || Contains(title, "pytest") || Contains(title, "Linux")) return new TopicBrief(
            "Use Python to make a customer workflow repeatable: make environments explicit, validate boundaries, test behaviour, and leave an operator-friendly trail.",
            "A file-processing script works on one laptop but fails on a customer export. The team needs reproducible dependencies, validated input models, structured logs, and a small regression test suite.",
            "Build the smallest executable example, add one invalid-input test, emit structured context for each run, and document the command a teammate can use to reproduce it.");
        if (Contains(title, "Git Internals") || Contains(title, "Hexagonal Architecture") || Contains(title, "Software Engineering Best Practices")) return new TopicBrief(
            "Create a delivery system that makes changes reviewable, reversible, testable, and independent from accidental details such as a specific vendor SDK or local machine setup.",
            "A customer asks for a quick integration. The team must move quickly without letting production credentials, unreviewed code paths, or direct vendor coupling become permanent architecture.",
            "Create a small adapter boundary, write a meaningful commit history, add a test around the business rule, and identify the change that can be rolled back independently.");
        if (Contains(title, "HTTP") || Contains(title, "FastAPI") || Contains(title, "Order Management") || Contains(title, "Payments") || Contains(title, "Auth")) return new TopicBrief(
            "Design APIs around stable resource contracts, safe failure behaviour, and authorization rules that match the customer’s real roles.",
            "An operations lead creates an order while a finance user approves payment. The API must reject invalid state changes, make retries safe, and reveal who performed each privileged action.",
            "Write the request and error shapes first, add an idempotency or concurrency case, and test each role against an action it must not perform.");
        if (Contains(title, "Real-Time") || Contains(title, "Queues") || Contains(title, "Caching")) return new TopicBrief(
            "Use asynchronous delivery and caching only after defining message ownership, ordering needs, retry behavior, cache invalidation, and the user experience during lag.",
            "An agent job takes thirty seconds while the UI needs immediate feedback. The system must report progress without pretending that the final answer is ready or losing work after a worker restart.",
            "Design the request acknowledgement, event payload, retry policy, cache key, and invalidation trigger; then test a duplicate event and a stale read.");
        if (Contains(title, "Observability") || Contains(title, "Tracing") || Contains(title, "Logging") || Contains(title, "Profiling")) return new TopicBrief(
            "Instrument the customer outcome, not merely the process: logs, metrics, and traces should answer what failed, where, for whom, and how often.",
            "A user reports that an approval flow is slow. Trace one request across the API, database, queue, and worker to decide whether the cause is latency, a retry storm, or a stuck dependency.",
            "Define one service-level indicator, add a correlation identifier, capture a trace for the happy path and a failure path, then write the first diagnostic question an operator should ask.");
        if (Contains(title, "Postgres") || Contains(title, "NoSQL") || Contains(title, "Dimensional") || Contains(title, "Airflow") || Contains(title, "Kafka") || Contains(title, "Data Pipeline")) return new TopicBrief(
            "Choose storage and data movement based on access patterns, freshness, lineage, and recovery needs—not on the popularity of a database or queue.",
            "A customer needs operational search, historical reporting, and near-real-time notifications from the same order data. The design must make ownership and consistency boundaries visible.",
            "Sketch the producer, storage, consumer, and recovery paths; measure one representative query or job; and define what happens when a record is late, duplicated, or malformed.");
        if (Contains(title, "TypeScript") || Contains(title, "React") || Contains(title, "Next.js") || Contains(title, "Vercel") || Contains(title, "Frontend") || Contains(title, "UX")) return new TopicBrief(
            "Make the product surface truthful: model states explicitly, keep asynchronous work visible, and give users a safe way to recover from uncertainty.",
            "A document-review user submits a question to an AI workflow. The UI must show progress, surface retrieved evidence, allow cancellation, and make a partial failure understandable.",
            "Implement loading, empty, success, and failure states for one workflow; test keyboard navigation; and ask a teammate to complete the task using only the visible cues.");
        if (Contains(title, "Compute, Storage")) return new TopicBrief(
            "Select managed compute, storage, database, and queue services by their operational contract: scaling behaviour, durability, isolation, cost model, and recovery characteristics.",
            "A new document workflow needs burst compute, durable uploads, transactional metadata, and asynchronous notifications. One service choice should not silently assume the properties of another.",
            "Map each workload step to a service, state its durability and retry expectation, then test how the design handles a partial write or delayed notification.");
        if (Contains(title, "AWS") || Contains(title, "EC2") || Contains(title, "S3") || Contains(title, "RDS") || Contains(title, "SQS") || Contains(title, "Lambda") || Contains(title, "VPC") || Contains(title, "KMS")) return new TopicBrief(
            "Use cloud services as a set of explicit trust and failure boundaries: identity, network reachability, data protection, cost, and recovery must be designed together.",
            "A customer wants a private document-processing service. The design needs least-privilege roles, private networking where appropriate, encrypted storage, and audit records for high-value actions.",
            "Draw the request path from user to storage, list the identity at each hop, test one denied action, and record how an operator would investigate an unexpected cost or access event.");
        if (Contains(title, "Docker") || Contains(title, "Kubernetes") || Contains(title, "Helm") || Contains(title, "Terraform") || Contains(title, "CI/CD") || Contains(title, "GitOps") || Contains(title, "Serverless")) return new TopicBrief(
            "Turn delivery into a repeatable system: build once, make configuration explicit, promote through environments, and make rollback a planned operation.",
            "A release passes locally but fails in staging because a secret, migration, or resource limit differs. The team needs a declarative deployment record and a safe rollback path.",
            "Package a minimal service, deploy it with an explicit configuration value, force one controlled failure, and document the exact rollback and verification steps.");
        if (Contains(title, "LLM Safety") || Contains(title, "Cost, Latency") || Contains(title, "Model Routing")) return new TopicBrief(
            "Make model behavior safe and economical with explicit data handling, output validation, budget limits, latency targets, and a fallback policy that users can understand.",
            "A customer wants every request sent to the largest available model. The FDE must show when a smaller model, a retrieval-only answer, a queue, or a human escalation is safer and cheaper.",
            "Define a request budget, timeout, safety check, fallback response, and evaluation threshold; then simulate a slow model, an unsafe output, and an exhausted budget.");
        if (Contains(title, "SRE") || Contains(title, "Load Testing") || Contains(title, "Incident") || Contains(title, "Readiness") || Contains(title, "Secrets") || Contains(title, "Security")) return new TopicBrief(
            "Operational readiness means knowing the normal state, protecting sensitive data, and rehearsing what happens when the system is stressed or wrong.",
            "A customer-facing workflow has a sudden error-rate spike. The team must protect data, communicate status, mitigate impact, and produce a useful root-cause analysis afterwards.",
            "Define a readiness checklist, run one small failure drill, capture the timeline and owner decisions, and turn the first discovered gap into a concrete backlog item.");
        if (Contains(title, "Customer Discovery") || Contains(title, "Scoping") || Contains(title, "Stakeholder") || Contains(title, "Demo Storytelling")) return new TopicBrief(
            "Convert a conversation into an engineering decision: identify the user, workflow, success measure, constraints, risks, and the smallest testable next step.",
            "A sponsor asks for an AI assistant because ‘the team wastes time searching’. The FDE must uncover who searches, what evidence is trusted, which cases are high risk, and how improvement will be measured.",
            "Run a 30-minute discovery outline, write a one-page option matrix, and present a recommendation that includes a deliberate non-solution option.");
        if (Contains(title, "Integration") || Contains(title, "CRM") || Contains(title, "Entity Resolution") || Contains(title, "Enterprise Systems")) return new TopicBrief(
            "Treat an integration as a contract between systems with different owners, data quality, timing, and recovery rules.",
            "A support copilot reads CRM data and creates follow-up tickets. Duplicate identities, stale fields, and a temporary connector outage must not lead to duplicate or unauthorized actions.",
            "Document the source of truth for each field, define an idempotency key, model a retry and dead-letter path, and rehearse a connector outage.");
        if (Contains(title, "Product Thinking") || Contains(title, "Document Processing") || Contains(title, "Developer Experience")) return new TopicBrief(
            "Shape the application around an observable user job: make inputs, evidence, permissions, review steps, and handover needs explicit from the first prototype.",
            "A legal operations team receives mixed-format documents and needs a review queue. The product must preserve source evidence, distinguish extraction confidence from approval, and leave a usable audit trail.",
            "Map the end-to-end user journey, create one clear review state, document the API contract, and identify the point at which a human must make the final decision.");
        if (Contains(title, "Distributed Systems") || Contains(title, "System Design")) return new TopicBrief(
            "Use system design to make trade-offs visible: workload, latency, scale, consistency, failure modes, capacity, and operations are all part of one argument.",
            "A multi-tenant AI workflow receives unpredictable traffic and must preserve tenant isolation while giving operators a way to recover failed background jobs.",
            "Start with requirements and constraints, draw the critical path, name the bottleneck, choose one trade-off deliberately, and defend it against a failure scenario.");
        if (Contains(title, "Interview Readiness")) return new TopicBrief(
            "Communicate an engineering decision with structure: clarify the goal, state constraints, propose a design, explain trade-offs, and show how you would validate it in production.",
            "An interviewer asks for an internal knowledge assistant. A useful answer includes the user workflow, retrieval boundary, data protection, evaluation strategy, rollout, and operational failure plan.",
            "Practice a seven-minute design explanation, ask two clarifying questions first, and end with the metric that would determine whether the proposed system should be expanded.");

        return new TopicBrief(
            $"Study {title} as a practical engineering capability that can be demonstrated, observed, and safely handed over.",
            $"A delivery team needs to apply {title} in a customer environment where requirements are incomplete and the cost of an unexamined assumption is high.",
            $"Create a small artefact for {title}, test one edge case, and explain the chosen trade-off to a non-specialist stakeholder.");
    }

    private static int EstimateMinutes(string title)
    {
        if (Contains(title, "Assessment") || Contains(title, "Capstone") || Contains(title, "Build:") || Contains(title, "Mock Engagement")) return 120;
        if (Contains(title, "System Design") || Contains(title, "Kubernetes") || Contains(title, "Postgres") || Contains(title, "RAG")) return 90;
        return 60;
    }

    private static string ResolveDifficulty(string title, string badge)
    {
        if (badge == "Prerequisite") return "Foundation";
        if (Contains(title, "Assessment") || Contains(title, "Capstone") || Contains(title, "System Design") || Contains(title, "Production")) return "Advanced";
        return "Intermediate";
    }

    private static bool Contains(string value, string phrase) => value.Contains(phrase, StringComparison.OrdinalIgnoreCase);

    private static bool HaveEquivalentOutline(IEnumerable<StudyTask> first, IEnumerable<StudyTask> second)
    {
        var firstOutline = first.Select(task => NormalizeOutlineItem(task.Module, task.Title)).OrderBy(item => item).ToList();
        var secondOutline = second.Select(task => NormalizeOutlineItem(task.Module, task.Title)).OrderBy(item => item).ToList();
        return firstOutline.SequenceEqual(secondOutline);
    }

    private static string NormalizeOutlineItem(string module, string title)
    {
        var value = $"{module}::{title}".ToLowerInvariant();
        return Regex.Replace(value, @"[^a-z0-9]+", string.Empty);
    }

    private static string Slugify(string value)
    {
        var slug = value.ToLowerInvariant()
            .Replace("&", " and ")
            .Replace("+", " plus ");
        slug = Regex.Replace(slug, @"[^a-z0-9]+", "-");
        return slug.Trim('-');
    }
}
