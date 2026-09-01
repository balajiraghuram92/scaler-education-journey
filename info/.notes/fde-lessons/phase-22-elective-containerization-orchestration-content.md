# FDE Phase 22 — Elective: Containerization and Orchestration (Lessons 13-17 of 17, COMPLETES THE MODULE)

Five lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-22-elective-containerization-orchestration-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `elective-containerization-orchestration` ("Containerization and
Orchestration", a `SupplementalModuleDefinition` / elective).

This is the **third and final phase** of a **17-lesson elective module**. Phase 20 (authored
separately) covers lessons 1-6 (Docker Introduction through Docker Networking Deep Dive). Phase 21
(authored separately) covers lessons 7-12 (Docker hardening, hardening demo, Introduction to
Orchestration, Kubernetes Architecture, Kubernetes Pod Deep Dive, ReplicaSets/Deployments/
Sidecars). This file covers the **remaining five lessons — 13-17 of 17 — and completes the
module at 17/17** once applied.

Lessons 13-17: Kubernetes Networking, Kubernetes Scaling (HPA/Cluster Autoscaler/VPA/Karpenter),
Kubernetes Scaling and Network Policies, Kubernetes Security (RBAC and DevSecOps), Kubernetes
Volumes.

**Overlap note (read before assuming duplication):** Module 4 of the CORE curriculum
(`cloud-devops-infrastructure`) already has a lesson, "Kubernetes Networking, Security & GPU
Workloads," covering default-deny `NetworkPolicy` design, RBAC least-privilege scoping, and GPU
scheduling — but at a **production-operations, incident-diagnosis angle**: it assumes Services and
Ingress already exist and focuses on securing an already-running cluster (namespace isolation for
a shared multi-tenant cluster, GPU node taints/tolerations, `Pending`-pod diagnosis). This phase's
Lesson 13 (Kubernetes Networking) and Lesson 16 (Kubernetes Security: RBAC and DevSecOps)
deliberately go one level **more mechanism-focused and hands-on**: the actual YAML anatomy and
`kubectl` mechanics of building a `Service` and `Ingress` from nothing, reading `kubectl describe
endpoints` output, constructing a `Role`/`RoleBinding` pair from scratch and verifying it with
`kubectl auth can-i --as`, and the day-to-day DevSecOps loop of scoping a new `ServiceAccount`
before a workload ships — not the already-secured-cluster incident-response framing Module 4
covers. Each lesson's opening paragraph names this distinction explicitly. Lesson 15 (Kubernetes
Scaling and Network Policies) also touches `NetworkPolicy`, but from the different angle of
"scaling must not silently widen the network blast radius," building on Lesson 13's mechanics
rather than repeating Module 4's default-deny design lesson.

All five lessons continue the same running example established in Phases 20-21: **Northwind
Fulfillment**, a mid-market logistics customer, and its FastAPI service `routeplanner` (backed by
Redis and Postgres), now running on Kubernetes after Phase 21's ReplicaSet/Deployment lesson.

---

# LESSON 13

```yaml
lesson_id: fde-elective-containerization-orchestration-13-kubernetes-networking
lesson_title: "Kubernetes Networking"
lesson_order: 13

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Medium-Hard
estimated_minutes: 60
content_status: Draft

learning_outcomes:
  - "Build a ClusterIP Service, read its Endpoints object, and trace how cluster DNS resolves a Service name to a set of Pod IPs that changes as Pods are replaced."
  - "Distinguish ClusterIP, NodePort, and LoadBalancer Service types by which traffic direction and trust boundary each one actually opens, and route external traffic through an Ingress instead of exposing a Service type directly."
  - "Read Endpoints/EndpointSlice readiness state to explain why a Pod that is Running can still be excluded from a Service's traffic rotation."

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
# Kubernetes Networking

## Concepts Covered

Module 4's Kubernetes networking lesson assumed a `Service` already existed and focused on
locking a running cluster down with `NetworkPolicy`. This lesson goes one level earlier: how a
`Service` object itself gets built, what cluster DNS actually does with it, and why the traffic
that reaches a Pod through one is never sent to a Pod's IP directly. Every Pod in a cluster gets
its own IP address, but that address is worthless as a stable target — Phase 21's ReplicaSet
lesson established that Pods are disposable and get replaced with new IPs constantly, so nothing
should ever hardcode one. A `Service` solves this by giving a stable virtual IP and DNS name to a
*set* of Pods selected by label, and continuously updating which real Pod IPs sit behind that
stable address as Pods come and go. The mechanism has two halves working together: `kube-proxy`
(or the CNI's equivalent) programs iptables or IPVS rules on every node so that traffic to the
Service's virtual IP gets load-balanced across the real Pod IPs currently marked ready, and
`kube-dns`/CoreDNS resolves `routeplanner.default.svc.cluster.local` (or just `routeplanner`
inside the same namespace) to that virtual IP so application code never needs to know the virtual
IP either — it just calls the Service by name. The list of real Pod IPs behind a Service isn't
part of the Service object itself; it lives in a separate `Endpoints` (or `EndpointSlice`) object
that the Endpoints controller keeps in sync, adding a Pod's IP only once its readiness probe
passes and removing it the instant the Pod stops being ready or is deleted — this is the same
readiness signal from Phase 21's Pod lesson, now wired directly into traffic routing rather than
just restart behavior.

```yaml
# routeplanner-service.yaml — internal ClusterIP Service
apiVersion: v1
kind: Service
metadata:
  name: routeplanner
  namespace: default
spec:
  type: ClusterIP
  selector:
    app: routeplanner
  ports:
    - name: http
      port: 8080
      targetPort: 8080
```

Three Service types open three different traffic directions, and picking the wrong one is a
common trust-boundary mistake. `ClusterIP` (the default, shown above) is reachable only from
inside the cluster — the correct choice for `routeplanner` reaching Redis or Postgres, and for
anything that should never be internet-facing. `NodePort` opens a fixed port (30000-32767) on
every node's own IP, which technically makes the Service reachable from outside the cluster the
moment any node's firewall allows it — a shortcut that is almost always the wrong production
choice because it bypasses any central routing, TLS termination, or path-based rule, and ties
external reachability to node IPs that can change. `LoadBalancer` provisions a cloud load balancer
(an AWS NLB/ALB, in Northwind's case) pointing at the Service, which works but provisions one
load balancer *per Service* — expensive and unwieldy once there are several externally-facing
services. An `Ingress` object is the better answer for HTTP(S) traffic specifically: one Ingress
controller (commonly `ingress-nginx` or an AWS Load Balancer Controller) runs as a single entry
point handling TLS termination and path/host-based routing to multiple backend Services, so
`api.northwind.example.com/routes` and `api.northwind.example.com/admin` can route to two
different internal ClusterIP Services behind one externally-facing load balancer instead of two.

```yaml
# routeplanner-ingress.yaml — HTTP routing through one entry point
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: routeplanner-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: api.northwind.example.com
      http:
        paths:
          - path: /routes
            pathType: Prefix
            backend:
              service:
                name: routeplanner
                port:
                  number: 8080
```

## Practical Backend Scenario

Northwind's `routeplanner` Deployment runs three replicas behind a `ClusterIP` Service that the
customer's internal order-processing job calls by DNS name. During a rolling update, one new Pod
starts but its readiness probe never passes because its Postgres connection string points at the
wrong environment variable name for the new revision. `kubectl get pods` shows it as `Running` —
the container process is alive — but requests to `routeplanner` never land on it, and nobody
notices anything is wrong because the other two Pods still serving traffic absorb the load fine.
The FDE runs `kubectl get endpoints routeplanner` and sees only two IPs listed where three Pods
exist, immediately narrowing the investigation from "is the Service broken" to "which specific Pod
is excluded and why" — `kubectl describe pod` on the missing one shows the readiness probe's exact
failure reason. Separately, when Northwind's product team asks to expose `routeplanner`'s read-only
route-history endpoint to a partner logistics company without exposing anything else, the FDE
resists the instinct to flip the Service to `LoadBalancer` (which would expose every port the
Service defines, not just the one route) and instead adds a second `Ingress` path scoped to
exactly `/routes/history`, routed through the existing TLS-terminating entry point.

## Practice Loop

1. Create the `routeplanner` ClusterIP Service and confirm `kubectl get endpoints routeplanner`
   lists exactly as many IPs as there are ready Pods.
2. Exec into any Pod in the cluster and run `nslookup routeplanner` (or
   `routeplanner.default.svc.cluster.local`) to confirm cluster DNS resolves the Service name to
   its virtual IP.
3. Deliberately break one Pod's readiness probe (point it at a nonexistent health endpoint),
   redeploy, and watch `kubectl get endpoints` drop that Pod's IP while `kubectl get pods` still
   shows it `Running`.
4. Write the `Ingress` manifest routing `api.northwind.example.com/routes` to the `routeplanner`
   Service, apply it, and trace the full request path from client to Pod in one sentence per hop.
5. Compare `NodePort` and `LoadBalancer` for the same Service and write one sentence stating which
   trust boundary each one opens that `ClusterIP` does not.

## Evidence of Understanding

You can build a `ClusterIP` Service and explain the two-part mechanism (kube-proxy's traffic
routing, CoreDNS's name resolution) that makes it work without any application code knowing a Pod
IP. You can read an `Endpoints`/`EndpointSlice` object to distinguish a Pod's container-alive state
from its traffic-eligible state, and use that distinction to diagnose a Pod that is `Running` but
silently excluded from rotation. You can choose the correct Service type or Ingress for a given
traffic direction and explain why a shortcut like `NodePort` or an unscoped `LoadBalancer` opens
more surface than the task actually requires.

## Suggested Extension

Add a second backend Service and a second `Ingress` path rule so two different routes on the same
host route to two different Deployments, and confirm with `curl` that each path reaches only its
intended backend.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What actually makes a Service's target list dynamic
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What object does the Endpoints controller update to keep a Service's traffic targets in sync with
which Pods currently exist and are ready?

**OPTIONS:**
- [ ] A: The Service object's own `spec.selector` field, rewritten on every Pod change
- [x] B: A separate `Endpoints` (or `EndpointSlice`) object, whose Pod-IP list is added to only once a Pod's readiness probe passes and removed the instant the Pod stops being ready or is deleted
- [ ] C: The cluster's CoreDNS zone file, updated directly by kubelet
- [ ] D: The ReplicaSet's `status.readyReplicas` field

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is explicit that the target list lives in a separate object from the Service itself,
and that readiness — not just Pod existence — gates membership in it.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [endpoints, endpointslice, readiness-gating]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Reading the ClusterIP Service manifest
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the lesson's `routeplanner-service.yaml`, what determines which Pods this Service sends traffic
to?

**CODE_BLOCK:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: routeplanner
spec:
  type: ClusterIP
  selector:
    app: routeplanner
  ports:
    - port: 8080
      targetPort: 8080
```

**OPTIONS:**
- [ ] A: The `metadata.name` field must exactly match the Deployment's name
- [x] B: The `spec.selector` field (`app: routeplanner`) — any ready Pod carrying that label is included as a traffic target, regardless of which Deployment or ReplicaSet created it
- [ ] C: The `targetPort` value, which must be unique across the cluster
- [ ] D: The namespace alone; all Pods in `default` receive traffic from this Service

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Label selection, not naming or namespace alone, is what ties a Service to its backing Pods — this
is also why two different Deployments' Pods could be accidentally included if they share a label.

**LESSON_CONNECTION:** Chapter Body, Service manifest example
**KEYWORDS:** [service-selector, label-matching]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why NodePort is usually the wrong production choice
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson call `NodePort` "almost always the wrong production choice" for exposing a
service externally?

**OPTIONS:**
- [ ] A: NodePort Services cannot be reached from outside the cluster under any configuration
- [x] B: It bypasses any central routing, TLS termination, or path-based rule, and ties external reachability directly to node IPs, which can change — an Ingress with a single controller is the better entry point for HTTP(S) traffic
- [ ] C: NodePort only works with the `LoadBalancer` Service type as a prerequisite
- [ ] D: NodePort Services do not support DNS resolution inside the cluster

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific objection is about bypassing centralized routing/TLS and coupling to
volatile node IPs, not about NodePort being unreachable.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [nodeport, ingress, entry-point]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why LoadBalancer doesn't scale to many services
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific problem does the lesson say makes `LoadBalancer` Services unwieldy once a cluster has
several externally-facing services, and how does `Ingress` solve it?

**OPTIONS:**
- [ ] A: LoadBalancer Services cannot terminate TLS, while Ingress always can
- [x] B: A `LoadBalancer` Service provisions one cloud load balancer per Service; an `Ingress` lets a single controller handle TLS termination and path/host-based routing to multiple backend Services behind one externally-facing load balancer
- [ ] C: LoadBalancer Services are deprecated in current Kubernetes versions
- [ ] D: Ingress objects replace the need for any Service object at all

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson names the per-Service cost explicitly and contrasts it with Ingress's single-entry-point,
multi-backend routing model.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [loadbalancer-cost, ingress-consolidation]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Diagnosing a Running-but-unreachable Pod
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did `kubectl get endpoints routeplanner` show only two IPs
while `kubectl get pods` showed three Pods as `Running`?

**OPTIONS:**
- [ ] A: The third Pod had not yet been scheduled to a node
- [ ] B: The Service's selector no longer matched the third Pod's labels
- [x] C: The third Pod's readiness probe was failing (due to a misconfigured environment variable), so it was excluded from the Endpoints object even though its container process was alive and the Pod phase was `Running`
- [ ] D: `kubectl get endpoints` only shows a maximum of two IPs regardless of how many Pods exist

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The scenario's specific point is the gap between "container alive" (`Running`) and "traffic
eligible" (ready and therefore listed in Endpoints) — readiness, not process liveness, gates
Endpoints membership.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [readiness-vs-running, endpoints-diagnosis]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** The Ingress path-routing decision
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE add a second `Ingress` path rule rather than changing the `routeplanner` Service's
type to `LoadBalancer` to expose the partner-facing route-history endpoint?

**OPTIONS:**
- [ ] A: `LoadBalancer` Services cannot be created in the `default` namespace
- [x] B: Changing the Service type to `LoadBalancer` would expose every port the Service defines, not just the one intended route; a scoped `Ingress` path exposes only the specific endpoint needed, through the existing TLS-terminating entry point
- [ ] C: `Ingress` objects are required before a Service can have more than one port
- [ ] D: The partner company's network could not reach a `LoadBalancer`-type Service under any circumstances

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's point is about surface minimization — a path-scoped Ingress rule opens exactly what's
needed, while flipping the Service type would have opened the whole Service.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scoped-exposure, ingress-path-routing]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** How cluster DNS resolves a Service name
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does CoreDNS resolve `routeplanner.default.svc.cluster.local` to?

**OPTIONS:**
- [ ] A: The IP address of whichever Pod most recently started
- [x] B: The Service's stable virtual IP, which `kube-proxy` (or the CNI's equivalent) then load-balances across the real Pod IPs currently marked ready in the Endpoints object
- [ ] C: A random Pod IP chosen fresh for every DNS lookup, bypassing the Service entirely
- [ ] D: The node IP of whichever node the Deployment happens to be scheduled on

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
DNS resolves to the Service's stable virtual IP; the actual load-balancing across ready Pod IPs
happens at the kube-proxy layer, a separate step from name resolution.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [coredns, cluster-dns, virtual-ip]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why hardcoding a Pod IP is always wrong
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a Pod's own IP address is "worthless as a stable target"?

**OPTIONS:**
- [ ] A: Pod IPs are randomized on every network request
- [x] B: Pods are disposable and routinely replaced (by rolling updates, rescheduling, or crashes), each time getting a new IP, so anything hardcoding a specific Pod IP breaks the next time that Pod is replaced
- [ ] C: Pod IPs are not routable outside the node they run on
- [ ] D: Only Services have IP addresses; Pods do not receive one individually

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This connects directly to Phase 21's Pod-disposability lesson — the churn in Pod identity is
exactly the problem a Service's stable virtual IP and DNS name exist to solve.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [pod-disposability, stable-target]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** How this lesson differs from Module 4's Kubernetes networking lesson
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson opens by distinguishing itself from Module 4's "Kubernetes Networking, Security & GPU
Workloads" lesson. What is that distinction?

**OPTIONS:**
- [ ] A: Module 4's lesson does not cover Kubernetes at all; it is purely about AWS VPC design
- [x] B: Module 4's lesson assumes a Service already exists and focuses on securing an already-running cluster with `NetworkPolicy`; this lesson covers the earlier, more mechanism-focused question of how a Service and Ingress actually get built and how DNS/endpoint routing works
- [ ] C: This lesson covers only `NodePort` Services, while Module 4 covers only `ClusterIP`
- [ ] D: The two lessons cover identical content and either can be skipped

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's opening paragraph states this explicitly — the difference is mechanism-and-construction
versus already-running-cluster security operations.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (opening)
**KEYWORDS:** [overlap-differentiation, module-4-contrast]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 14

```yaml
lesson_id: fde-elective-containerization-orchestration-14-kubernetes-scaling-hpa-cluster-autoscaler-vpa-and-karpenter
lesson_title: "Kubernetes Scaling: HPA, Cluster Autoscaler, VPA, and Karpenter"
lesson_order: 14

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Medium-Hard
estimated_minutes: 60
content_status: Draft

learning_outcomes:
  - "Write a HorizontalPodAutoscaler that scales on CPU utilization, and explain why a Pod without resource requests set makes the HPA's percentage-based target meaningless."
  - "Distinguish the four scaling layers (HPA, VPA, Cluster Autoscaler, Karpenter) by which resource dimension each one changes and diagnose which layer is saturated when a workload scales pods but stays Pending."
  - "Explain how a stabilization window prevents scaling oscillation, and state the cost/latency trade-off between reactive node provisioning and pre-provisioned headroom."

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
# Kubernetes Scaling: HPA, Cluster Autoscaler, VPA, and Karpenter

## Concepts Covered

Kubernetes scaling is really four separate mechanisms answering four different questions, and the
single most common scaling failure is diagnosing the wrong one — adding more Pods when the cluster
has no room to run them, or right-sizing a Pod when the actual problem is Pod count. The
**HorizontalPodAutoscaler (HPA)** answers "how many replicas of this Deployment should exist right
now," watching a metric (CPU/memory utilization by default, or a custom metric like queue depth via
the metrics API) against a target and adjusting `spec.replicas` on the Deployment it targets. It
only works correctly if every container has `resources.requests` set — CPU utilization is measured
*as a percentage of the request*, so a Pod with no request set has an undefined percentage and the
HPA cannot compute a target at all, a subtle configuration gap that silently makes autoscaling
inert rather than erroring loudly. The **Vertical Pod Autoscaler (VPA)** answers a different
question — "is this Pod's own CPU/memory request sized correctly" — recommending (or, in `Auto`
mode, applying) request/limit changes based on observed usage history; it and the HPA should not
both actively resize the same resource dimension on the same workload, since they'd fight each
other's decisions.

```yaml
# routeplanner-hpa.yaml — scale 3-10 replicas targeting 70% CPU
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: routeplanner-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: routeplanner
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
```

Both HPA and VPA operate entirely at the Pod level — they never change how many *nodes* exist. That
is the **Cluster Autoscaler**'s job: it watches for Pods stuck `Pending` because no node has enough
allocatable CPU/memory to schedule them, and adds nodes to a node group to make room (and,
symmetrically, removes underutilized nodes when it's safe to). This is why a bursty workload can
scale its Pod count via HPA and still sit `Pending` — the HPA did its job correctly, but the
cluster genuinely had no spare node capacity, and Cluster Autoscaler hadn't caught up yet (node
provisioning takes real minutes, not the seconds Pod scheduling takes). **Karpenter** is a newer
alternative to Cluster Autoscaler that skips the node-group abstraction entirely: instead of
scaling a pre-defined group of identically-shaped nodes, it looks at the actual pending Pods'
resource requests, taints/tolerations, and affinity rules and provisions right-sized nodes directly
from a flexible instance-type pool, which is both faster to react and avoids the classic Cluster
Autoscaler waste of over-provisioning a large uniform node just to fit one small Pod.
`stabilizationWindowSeconds` on the HPA's `scaleDown` behavior (shown above) exists because a
workload with a bursty, spiky metric can otherwise oscillate — scaling up, immediately scaling back
down as the burst passes, scaling up again seconds later — churning Pods and nodes for no real
benefit; the window makes the HPA wait for a sustained low reading before actually scaling down,
trading a little latency for stability. All four layers trade cost against latency in the same
direction: pre-provisioned headroom (extra nodes or Pods sitting idle, ready) costs money
continuously but responds instantly; purely reactive provisioning costs nothing when idle but
means a real, measurable delay — Pod scheduling in seconds, new node provisioning in minutes — before
capacity actually exists.

## Practical Backend Scenario

Northwind's `routeplanner` Deployment gets a HPA targeting 70% CPU, `minReplicas: 3,
maxReplicas: 10`. During a regional weather event that spikes delivery-route recalculation
requests, the HPA correctly scales `routeplanner` from 3 to 9 replicas within two minutes — but six
of the new Pods sit `Pending` for four more minutes before becoming schedulable. The FDE checks
`kubectl describe pod` on one `Pending` replica and sees the scheduling-failure event: `0/6 nodes
are available: insufficient cpu`. The HPA layer worked exactly as designed; the bottleneck was one
layer down, at cluster node capacity, and Cluster Autoscaler needed those four minutes to actually
provision and join a new node before the Pending Pods could schedule. Separately, a VPA
recommendation run against `routeplanner`'s historical usage shows its containers are requesting
500m CPU but only ever using roughly 120m — the FDE right-sizes the request down to 200m (leaving
headroom, not matching the exact observed average), which both improves node bin-packing (more
Pods fit per node at a smaller, more accurate request) and makes the HPA's utilization percentage
meaningful again, since it had been computing against an inflated denominator.

## Practice Loop

1. Add `resources.requests` to the `routeplanner` Deployment (a prerequisite the HPA silently
   depends on) and apply the `HorizontalPodAutoscaler` manifest above.
2. Generate synthetic CPU load against `routeplanner` and watch `kubectl get hpa routeplanner-hpa
   --watch` to see `TARGETS` climb and `REPLICAS` increase.
3. Deliberately cap the cluster's available node capacity (or run this against a small cluster) and
   reproduce a `Pending` Pod during a scale-up event; run `kubectl describe pod` and identify
   exactly which resource the scheduling-failure event names as insufficient.
4. Run a VPA in recommendation-only mode against `routeplanner`'s historical usage and compare its
   suggested CPU/memory request against the value currently set.
5. Explain in one paragraph why Karpenter's node provisioning can be faster than Cluster
   Autoscaler's for the same pending-Pod event, naming the specific abstraction Karpenter skips.

## Evidence of Understanding

You can write a `HorizontalPodAutoscaler` that scales on CPU utilization and explain precisely why
it depends on every container having `resources.requests` set. You can distinguish which of the
four scaling layers (HPA, VPA, Cluster Autoscaler, Karpenter) is responsible when a workload's Pod
count scaled correctly but new Pods remain `Pending`, and read the exact `kubectl describe pod`
event that confirms which resource is actually saturated. You can explain what a stabilization
window prevents and state the cost/latency trade-off between pre-provisioned headroom and reactive
provisioning in concrete terms.

## Suggested Extension

Configure the HPA to scale on a custom metric (queue depth from the Redis-backed route-calculation
queue) instead of CPU, and explain in one paragraph why queue depth is a more accurate scaling
signal than CPU utilization for a workload whose bottleneck is I/O-bound queue processing rather
than compute.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why a missing resource request breaks the HPA silently
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a Pod without `resources.requests` set makes the HPA's CPU-utilization
target "undefined" rather than simply causing an error?

**OPTIONS:**
- [ ] A: The HPA controller refuses to start at all if any target Pod lacks a resource request
- [x] B: CPU utilization is measured as a percentage of the configured request; with no request set, there is no denominator to compute a percentage against, so the HPA silently cannot determine whether to scale
- [ ] C: Kubernetes automatically sets a default request of 100m, which is always too low for CPU-bound workloads
- [ ] D: The HPA only supports memory-based targets when no CPU request is set

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific mechanism is the percentage calculation itself — utilization is relative to
the request, so no request means no meaningful percentage, a silent rather than loud failure mode.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [hpa, resource-requests, utilization-percentage]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** HPA versus Cluster Autoscaler — which layer changes what
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the core difference between what the HorizontalPodAutoscaler changes and what the Cluster
Autoscaler changes?

**OPTIONS:**
- [x] B: HPA changes how many Pod replicas a Deployment runs; Cluster Autoscaler changes how many nodes exist in the cluster — HPA never adds node capacity, and Cluster Autoscaler never changes Pod replica counts
- [ ] A: They are two names for the same controller, with HPA being the older, deprecated term
- [ ] C: HPA operates on nodes, and Cluster Autoscaler operates on individual Pods
- [ ] D: Cluster Autoscaler only runs once per day on a schedule, while HPA runs continuously

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is explicit that both HPA and VPA operate at the Pod level and never change node count —
that is specifically the Cluster Autoscaler's (or Karpenter's) job.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [hpa-vs-cluster-autoscaler, scaling-layers]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the HPA manifest's scaleDown behavior
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the lesson's `routeplanner-hpa.yaml`, what does `stabilizationWindowSeconds: 300` under
`behavior.scaleDown` actually do?

**CODE_BLOCK:**
```yaml
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
```

**OPTIONS:**
- [ ] A: It delays every scale-up decision by 300 seconds regardless of metric readings
- [x] B: It makes the HPA wait for a sustained low metric reading over that window before actually reducing replica count, preventing rapid oscillation from a brief dip in load
- [ ] C: It sets the minimum number of replicas to 300
- [ ] D: It is the maximum time a Pod is allowed to remain Pending before being evicted

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Stabilization windows specifically target scale-down oscillation, requiring a sustained reading
rather than reacting to every momentary dip.

**LESSON_CONNECTION:** Chapter Body, HPA manifest example
**KEYWORDS:** [stabilization-window, scale-down-oscillation]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why Pods stayed Pending despite a correct HPA scale-up
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, the HPA scaled `routeplanner` from 3 to 9 replicas correctly,
but six Pods sat `Pending` for four minutes. What does this indicate about where the actual
bottleneck was?

**OPTIONS:**
- [ ] A: The HPA itself was misconfigured and needed a longer stabilization window
- [ ] B: The VPA was actively fighting the HPA's replica changes
- [x] C: The bottleneck was one layer down, at cluster node capacity — the scheduler had nowhere to place the new Pods until Cluster Autoscaler provisioned and joined a new node, which takes real minutes unlike Pod scheduling's seconds
- [ ] D: The `routeplanner` Deployment's image had not finished pulling on any node

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The scenario's `kubectl describe pod` event ("insufficient cpu") confirms the HPA's replica-count
decision was correct; the gap was node-level capacity, a different layer entirely.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [pending-pods, node-capacity, layer-diagnosis]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why HPA and VPA should not both actively resize the same dimension
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson warn against running an HPA and a VPA that both actively manage CPU on the same
Deployment?

**OPTIONS:**
- [ ] A: Kubernetes does not allow both controllers to be installed in the same cluster
- [x] B: HPA scales replica count based on utilization relative to the CPU request; if VPA is simultaneously changing that same CPU request, the two controllers' decisions can fight each other rather than converge
- [ ] C: VPA can only manage memory, never CPU, so the conflict described is not possible
- [ ] D: Running both always causes the Deployment to be deleted automatically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's specific concern is the shared dependency — HPA's utilization math depends on the same
request value VPA is actively changing, creating a feedback conflict.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [hpa-vpa-conflict, shared-resource-dimension]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** How Karpenter differs from Cluster Autoscaler
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson say Karpenter does differently from Cluster Autoscaler when provisioning new
node capacity?

**OPTIONS:**
- [ ] A: Karpenter only works with spot instances, never on-demand capacity
- [x] B: Karpenter skips the pre-defined node-group abstraction and provisions right-sized nodes directly from a flexible instance-type pool based on the actual pending Pods' requirements, rather than scaling a group of identically-shaped nodes
- [ ] C: Karpenter operates entirely at the Pod level and never adds node capacity, unlike Cluster Autoscaler
- [ ] D: Karpenter requires the VPA to be disabled before it can run

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson names this exact distinction — skipping the node-group abstraction for direct,
requirement-driven, right-sized provisioning.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [karpenter, node-groups, right-sizing]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the FDE right-sized the CPU request downward, not to the exact average
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, the FDE reduces `routeplanner`'s CPU request from 500m to 200m,
not to the observed average of roughly 120m. What is the reasoning?

**OPTIONS:**
- [ ] A: Kubernetes requires CPU requests to be set in increments of 100m
- [x] B: Setting the request to exactly the observed average leaves no headroom for normal variance above that average, which would cause CPU throttling or scheduling pressure; 200m preserves some margin while still being far more accurate than the original 500m
- [ ] C: 200m is the minimum CPU request Kubernetes allows for any container
- [ ] D: The VPA tool automatically overrides any value below 200m
- [ ] E: Lower CPU requests always increase the HPA's target utilization automatically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Right-sizing means leaving deliberate headroom above the observed average, not matching it exactly
— matching the exact average would leave no margin for normal fluctuation.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [right-sizing, headroom, vpa-recommendation]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** The cost/latency trade-off across all four scaling layers
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what trade-off do all four scaling layers (HPA, VPA, Cluster Autoscaler,
Karpenter) share?

**OPTIONS:**
- [x] A: Pre-provisioned headroom costs money continuously but responds instantly; purely reactive provisioning costs nothing when idle but introduces a real, measurable delay before capacity actually exists
- [ ] B: All four layers have identical response times regardless of provisioning strategy
- [ ] C: Only HPA has a cost trade-off; the other three are always free to operate
- [ ] D: The trade-off is unique to Karpenter and does not apply to Cluster Autoscaler

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson closes on this exact generalization — headroom versus reactive provisioning is the same
cost/latency trade-off at every layer, just at different timescales (seconds for Pods, minutes for
nodes).

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (closing)
**KEYWORDS:** [cost-latency-tradeoff, headroom, reactive-provisioning]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why Pod scheduling and node provisioning differ in speed
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson notes Pod scheduling happens "in seconds" while new node provisioning takes "minutes."
Why does this timing gap matter for how an FDE should read a scaling incident?

**OPTIONS:**
- [ ] A: It doesn't matter; both operations always complete within the same time window
- [x] B: A correctly-functioning HPA can add replicas within seconds, but if those replicas need a new node, the workload will still show `Pending` Pods for several minutes even though nothing is actually broken — the gap is expected latency, not a failure
- [ ] C: It means Cluster Autoscaler should always be disabled in favor of pre-provisioning all node capacity permanently
- [ ] D: It implies HPA should be configured with a longer stabilization window to match node provisioning time

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Recognizing this timing gap as expected (not a bug) is exactly what let the FDE in the scenario
correctly diagnose the Pending Pods as a capacity-provisioning delay rather than an HPA malfunction.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [provisioning-latency, expected-delay, incident-reading]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 15

```yaml
lesson_id: fde-elective-containerization-orchestration-15-kubernetes-scaling-and-network-policies
lesson_title: "Kubernetes Scaling and Network Policies"
lesson_order: 15

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Medium-Hard
estimated_minutes: 60
content_status: Draft

learning_outcomes:
  - "Write a default-deny NetworkPolicy plus one additive allow rule, and explain why scaling a Deployment's replicas never widens the set of paths a NetworkPolicy permits."
  - "Set resource requests/limits deliberately as a precondition for safe autoscaling, and explain the difference between a request (scheduling guarantee) and a limit (throttling ceiling)."
  - "Design and run a two-part test (an expected-allowed connection and an expected-forbidden connection) that proves a scaled workload's blast radius stayed bounded."

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
# Kubernetes Scaling and Network Policies

## Concepts Covered

Lesson 14 covered the mechanics of scaling in isolation. This lesson covers the question that
matters once scaling is live in a real customer environment: does adding replicas ever change
*what a workload is allowed to reach*, and if not, why does that reassurance still need to be
tested rather than assumed. The short mechanical answer is that a `NetworkPolicy`'s rules are
defined by label selectors, not by replica count — a policy allowing ingress from Pods labeled
`app: routeplanner` covers every Pod carrying that label whether there are 3 of them or 30, because
new replicas created by a scale-up event inherit the Deployment's Pod template labels automatically.
Scaling and network policy are, mechanically, orthogonal concerns. But orthogonal-in-theory is not
the same as verified-in-practice, and this is exactly the kind of gap an FDE should not take on
faith during a customer engagement: a policy written sloppily — for example, a namespace-level
`podSelector: {}` matching *any* Pod in the namespace rather than the specific `app: routeplanner`
label — would silently let every newly-scaled replica of some *other* future workload in the same
namespace inherit access nobody intended, precisely because nobody re-reads the policy's selector
scope every time a new Deployment or a scale-up event happens.

```yaml
# default-deny-then-allow.yaml — namespace-wide default-deny, then one scoped allow
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: default
spec:
  podSelector: {}
  policyTypes: ["Ingress", "Egress"]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: routeplanner-allow-db-and-redis
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: routeplanner
  policyTypes: ["Egress"]
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

The second half of this lesson's concern is that autoscaling *without* a resource ceiling is its
own kind of blast-radius problem, just in the compute dimension instead of the network dimension.
A `resources.limits` value caps how much CPU/memory a single container can consume — CPU is
throttled (the process slows down but keeps running) when it exceeds its limit, while memory is
hard-killed (`OOMKilled`) the instant it exceeds its limit, an asymmetry worth knowing before
debugging a mysterious container restart. Without a `limits.memory` ceiling, a single leaking
replica during a scale-up burst can consume an entire node's memory and get every other Pod
scheduled on that node evicted alongside it — a single workload's bug taking down unrelated
neighbors sharing the node, which is precisely the kind of silently-widened blast radius the
network-policy half of this lesson is also about, just expressed through a different resource.
`resources.requests`, separately, is what the scheduler uses to decide whether a node has room for
a new Pod at all (Lesson 14's HPA/Cluster-Autoscaler mechanics depend on it) — a request that's set
too low lets the scheduler over-pack a node with more Pods than it can actually sustain under real
load, and a request set too high wastes capacity and triggers unnecessary Cluster Autoscaler
scale-outs. Getting both dimensions right — a tight, label-scoped `NetworkPolicy` and an honest
`requests`/`limits` pair — is what lets a customer trust that "we can scale this workload" doesn't
quietly also mean "we widened what it can reach or how much of a shared node it can consume."

## Practical Backend Scenario

Northwind's platform team asks the FDE to prove that scaling `routeplanner` from 3 to 9 replicas
during a traffic spike does not change its network reachability. The FDE applies the default-deny
policy above plus the scoped `routeplanner-allow-db-and-redis` policy, then forces a scale-up to 9
replicas and runs the same connectivity test against every one of the 9 Pods: a `curl` to Postgres
on port 5432 succeeds from all 9 (the expected-allowed path), and a `curl` attempt to the
`admin-console` Deployment's ClusterIP (which no policy explicitly allows) times out from all 9
(the expected-forbidden path) — proving the policy's blast radius held constant across the scale
event because it was written against the `app: routeplanner` label, not against a fixed replica
count. Separately, a load test against `routeplanner` without a `resources.limits.memory` ceiling
set reveals that one replica with a slow memory leak, when it happens to land on the same node as
the customer's separate `admin-console` Deployment, eventually consumes enough of that node's
memory to trigger the kubelet's node-pressure eviction, which kills several `admin-console` Pods
that had nothing to do with the leak — a customer-visible incident the FDE traces back to the
missing memory limit, not to anything `admin-console` itself did wrong.

## Practice Loop

1. Apply the namespace-wide default-deny `NetworkPolicy`, confirm all existing traffic breaks, then
   apply the scoped `routeplanner-allow-db-and-redis` policy and confirm only Postgres and Redis
   traffic from `routeplanner` succeeds.
2. Scale `routeplanner` from 3 to 9 replicas and re-run the same connectivity test against every
   replica, confirming the expected-allowed and expected-forbidden outcomes hold for all 9, not
   just the original 3.
3. Set `resources.requests` and `resources.limits` on the `routeplanner` container and explain, in
   one sentence each, what the scheduler uses the request for and what the kubelet does when the
   limit is exceeded for CPU versus for memory.
4. Remove the memory limit deliberately, run a load test that induces high memory usage, and
   observe (in a sandbox, not production) whether an unrelated Pod on the same node gets evicted.
5. Write a one-paragraph test report stating the exact allowed and forbidden connections tested,
   the replica counts at which each was tested, and the resource limits in place during the test.

## Evidence of Understanding

You can write a default-deny `NetworkPolicy` plus a label-scoped allow rule and explain why the
policy's blast radius does not change as a Deployment scales, because it's defined by label
selectors that every new replica inherits automatically. You can distinguish a CPU limit's
throttling behavior from a memory limit's hard-kill (`OOMKilled`) behavior, and explain how an
unset memory limit lets one workload's bug evict unrelated neighbors sharing a node. You can design
and run a two-part connectivity test — one expected-allowed path, one expected-forbidden path —
that proves a scaled workload's network and resource blast radius held constant, rather than
assuming it from the policy's theoretical correctness alone.

## Suggested Extension

Add an egress `NetworkPolicy` rule restricting `routeplanner` from reaching the public internet at
all except a named external DNS/IP range, and explain in one paragraph why an unrestricted egress
rule would undermine the rest of this lesson's network-isolation testing even with every ingress
rule locked down correctly.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why scaling replicas doesn't widen a NetworkPolicy's reach
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a `NetworkPolicy`'s allowed traffic paths stay the same whether a
Deployment has 3 replicas or 30?

**OPTIONS:**
- [ ] A: NetworkPolicy objects have a hard cap of a fixed number of matched Pods regardless of replica count
- [x] B: A NetworkPolicy's rules are defined by label selectors, and every new replica created by a scale-up event inherits the Deployment's Pod template labels automatically, so the same rule covers all replicas without being rewritten
- [ ] C: Kubernetes automatically creates a new NetworkPolicy object for every new replica
- [ ] D: NetworkPolicy rules only apply to the first replica created; later replicas are unrestricted

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Label-based matching, combined with label inheritance from the Pod template, is exactly why
scaling and NetworkPolicy scope are orthogonal — the lesson's central mechanical point.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [networkpolicy-label-selector, replica-independence]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Reading the default-deny-then-allow policy pair
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the lesson's two-policy YAML, what traffic does the `routeplanner-allow-db-and-redis` policy
permit, given that `default-deny-all` is also applied to the same namespace?

**CODE_BLOCK:**
```yaml
spec:
  podSelector:
    matchLabels:
      app: routeplanner
  policyTypes: ["Egress"]
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

**OPTIONS:**
- [x] A: Pods labeled `app: routeplanner` may make outbound (egress) connections only to Pods labeled `app: postgres` on port 5432 and Pods labeled `app: redis` on port 6379 — every other egress path stays blocked by the default-deny policy
- [ ] B: All Pods in the namespace may reach Postgres and Redis on any port
- [ ] C: `routeplanner` Pods may accept inbound connections from Postgres and Redis, but cannot initiate any connection themselves
- [ ] D: The policy grants unrestricted egress to `routeplanner` Pods, overriding the default-deny policy entirely

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is an egress-only allow rule scoped to two specific destination labels and ports; the
default-deny policy still blocks everything not explicitly named here, including ingress.

**LESSON_CONNECTION:** Chapter Body, NetworkPolicy example
**KEYWORDS:** [networkpolicy-egress, scoped-allow-rule]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** CPU throttling versus memory OOMKill
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the difference the lesson draws between exceeding a container's CPU limit and exceeding its
memory limit?

**OPTIONS:**
- [ ] A: Both result in the container being immediately killed and restarted
- [x] B: Exceeding a CPU limit throttles the process (it slows down but keeps running); exceeding a memory limit gets the container hard-killed (`OOMKilled`) immediately
- [ ] C: CPU limits are enforced by the scheduler, while memory limits are enforced by the NetworkPolicy controller
- [ ] D: Neither limit is actually enforced unless a `resources.requests` value is also set

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson calls this out explicitly as an asymmetry worth knowing — throttling versus a hard
kill are very different failure signatures to debug.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [cpu-throttling, oomkilled, resource-limits]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the admin-console Pods got evicted
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did unrelated `admin-console` Pods get evicted during
`routeplanner`'s load test?

**OPTIONS:**
- [ ] A: The default-deny NetworkPolicy blocked `admin-console`'s traffic during the test
- [ ] B: `admin-console` shared the same NetworkPolicy label as `routeplanner` by mistake
- [x] C: `routeplanner` had no `resources.limits.memory` ceiling set, so a leaking replica consumed enough of the shared node's memory to trigger the kubelet's node-pressure eviction, which killed other Pods on that same node regardless of which Deployment they belonged to
- [ ] D: The Cluster Autoscaler removed the node `admin-console` was running on to make room for `routeplanner`'s new replicas

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The scenario is explicit that the missing memory limit, not anything network-related or
`admin-console`'s own behavior, was the root cause — a node-sharing blast-radius failure.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [node-pressure-eviction, missing-memory-limit, neighbor-impact]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** The risk of an unscoped podSelector
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson warns that a policy using `podSelector: {}` at the allow-rule level (matching any Pod in
the namespace) rather than a specific label is a real risk. What specifically does this risk?

**OPTIONS:**
- [ ] A: The policy would fail to apply at all, since Kubernetes rejects empty selectors on allow rules
- [x] B: Every newly-scaled replica of some other, unrelated future workload placed in the same namespace would silently inherit the access the sloppy rule granted, since nobody re-reads the policy's scope every time a new Deployment appears
- [ ] C: It would cause the NetworkPolicy to apply only to the `routeplanner` Deployment specifically and no other workload
- [ ] D: It would prevent `routeplanner` itself from communicating with Postgres or Redis
- [ ] E: It has no practical effect since default-deny policies always take precedence over allow rules

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's point is specifically about future, unrelated workloads silently inheriting broad
access — a scope error that isn't obvious at write-time and doesn't surface until something new is
deployed into the same namespace.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [unscoped-selector, silent-scope-creep]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What resources.requests is actually used for
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what does the Kubernetes scheduler use a Pod's `resources.requests` value
for?

**OPTIONS:**
- [ ] A: To enforce a hard ceiling on how much CPU or memory the container may ever consume
- [x] B: To decide whether a node has enough allocatable capacity for a new Pod before scheduling it there — an over-packed node (from requests set too low) risks not sustaining every scheduled Pod under real load
- [ ] C: To determine which NetworkPolicy rules apply to the Pod
- [ ] D: To set the container's process priority relative to other containers on the same node

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Requests are a scheduling input, distinct from limits (an enforcement ceiling) — the lesson ties
this directly back to Lesson 14's HPA/Cluster-Autoscaler dependency on requests being set honestly.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [requests-vs-limits, scheduler-decision]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the FDE tested all 9 replicas, not just the original 3
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE re-run the connectivity test against all 9 replicas after scaling up, rather than
trusting that the policy's correctness on the original 3 replicas would hold?

**OPTIONS:**
- [ ] A: NetworkPolicy rules are evaluated independently per replica and can behave inconsistently, so full re-testing is the only way to be certain
- [x] B: Orthogonal-in-theory (label-based rules should cover all replicas automatically) is not the same as verified-in-practice; the test exists to actually prove the blast radius held constant rather than assume it from the policy's design
- [ ] C: Kubernetes requires a manual policy re-application after every scaling event
- [ ] D: The original 3 replicas use a different Pod template than the 6 added during scale-up

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the lesson's explicit framing — the mechanical guarantee is real, but an FDE verifies it
under real conditions rather than taking it on faith during a customer engagement.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [verify-dont-assume, blast-radius-testing]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What a two-part connectivity test proves
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson's practice loop require testing both an expected-allowed connection AND an
expected-forbidden connection, rather than only confirming the allowed path works?

**OPTIONS:**
- [ ] A: Testing only the allowed path is sufficient; the forbidden-path test is optional
- [x] B: Confirming only that the allowed path works proves the policy isn't blocking too much, but says nothing about whether it's blocking too little — the forbidden-path test is what proves the blast radius is actually bounded, not just that the intended traffic still functions
- [ ] C: Kubernetes NetworkPolicy objects require exactly two test cases before they can be considered valid
- [ ] D: The forbidden-path test is only necessary when scaling beyond 5 replicas

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
A functional test alone can't distinguish "correctly scoped" from "too permissive" — only a
deliberately-forbidden path failing as expected proves the narrower claim.

**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [two-part-test, forbidden-path-verification]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 16

```yaml
lesson_id: fde-elective-containerization-orchestration-16-kubernetes-security-rbac-and-devsecops
lesson_title: "Kubernetes Security: RBAC and DevSecOps"
lesson_order: 16

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Medium-Hard
estimated_minutes: 60
content_status: Draft

learning_outcomes:
  - "Build a ServiceAccount, Role, and RoleBinding from scratch scoped to specific verbs and resources, and verify the grant with `kubectl auth can-i --as`."
  - "Explain why the namespace's default ServiceAccount is a live risk if left unscoped, and distinguish a Role from a ClusterRole by which one is the least-privilege default choice."
  - "State an emergency-access path for a locked-down cluster that does not require permanently granting cluster-admin to a working identity."

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
# Kubernetes Security: RBAC and DevSecOps

## Concepts Covered

Module 4's Kubernetes security lesson assumed RBAC was already in place and focused on auditing an
already-secured, shared multi-tenant cluster. This lesson covers the earlier, hands-on question:
how do you actually build a `Role` and `RoleBinding` from nothing, and how do you verify — not
assume — that a new identity has exactly the permissions it needs and nothing more. Every request
to the Kubernetes API is made *as* some identity — a human user (typically authenticated via a
cloud provider's IAM integration or a client certificate) or a `ServiceAccount` (the identity every
Pod runs under, `default` if none is specified explicitly). RBAC decides what that identity may do
by combining a `Role` or `ClusterRole` (a named set of allowed verbs — `get`, `list`, `watch`,
`create`, `update`, `delete` — against specific resource types, optionally scoped to specific
resource names) with a `RoleBinding` or `ClusterRoleBinding` (which actually grants that role to a
specific user, group, or `ServiceAccount`). A `Role`/`RoleBinding` pair is namespace-scoped — it
grants access only within the one namespace it's created in — while a `ClusterRole`/
`ClusterRoleBinding` pair is cluster-scoped, valid across every namespace; defaulting to a `Role`
whenever access genuinely only needs to reach one namespace is the deliberate least-privilege
choice, the same discipline this pathway's DevSecOps lessons have applied to Dockerfiles and CI
gates now applied to the Kubernetes API surface itself.

```yaml
# routeplanner-deployer-rbac.yaml — narrow, task-scoped Role
apiVersion: v1
kind: ServiceAccount
metadata:
  name: routeplanner-deployer
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: routeplanner-deployer-role
  namespace: default
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    resourceNames: ["routeplanner"]
    verbs: ["get", "list", "watch", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: routeplanner-deployer-binding
  namespace: default
subjects:
  - kind: ServiceAccount
    name: routeplanner-deployer
    namespace: default
roleRef:
  kind: Role
  name: routeplanner-deployer-role
  apiGroup: rbac.authorization.k8s.io
```

Writing the YAML is only half the job — an FDE never assumes a grant is correctly scoped without
checking it, and the tool for that is `kubectl auth can-i`, which asks the API server directly
whether a given identity can perform a given verb on a given resource, rather than reasoning about
it from the YAML alone (a genuinely error-prone habit once bindings and role aggregation get
involved). `kubectl auth can-i delete secrets --as=system:serviceaccount:default:routeplanner-deployer`
returns a plain `yes` or `no`, and running the full negative-space check — every verb the identity
should *not* have — is what actually proves a least-privilege boundary rather than just checking
that the intended access works. The unscoped-`default`-ServiceAccount risk this lesson opens with
is not abstract: any namespace where nobody has deliberately restricted the `default`
ServiceAccount's bindings means every Pod in that namespace that doesn't specify its own
ServiceAccount inherits whatever `default` can do — if any Pod in that namespace is ever
compromised, the blast radius is exactly whatever `default` is bound to, which is why the DevSecOps
discipline here is to give every workload its own named, narrowly-scoped ServiceAccount rather than
letting anything run under `default` by omission. For the rare case where an operator genuinely
needs emergency, time-boxed elevated access — debugging a production incident that a scoped Role
can't diagnose — the right pattern is a separate, short-lived `ClusterRoleBinding` granted for the
duration of the incident and explicitly revoked afterward (or an automated break-glass tool that
expires the grant), never a standing `cluster-admin` binding kept "just in case."

## Practical Backend Scenario

During Northwind's pre-handoff review, the FDE discovers `routeplanner`'s CI deployment Pod is
running under the `default` ServiceAccount, which was bound to `cluster-admin` months earlier by a
previous engineer during a rushed demo and never revisited. The FDE builds the
`routeplanner-deployer` ServiceAccount/Role/RoleBinding shown above — scoped to exactly `get`,
`list`, `watch`, `update`, and `patch` on the single named `routeplanner` Deployment, plus read-only
Pod access for diagnosing a failed rollout — and verifies the new grant with a full sweep of
`kubectl auth can-i` checks: `can-i update deployments/routeplanner --as=...` returns `yes`, and
`can-i delete secrets --as=...`, `can-i create clusterrolebindings --as=...`, and `can-i get
deployments -A --as=...` (checking access outside the `default` namespace) all correctly return
`no`. The FDE then removes the old `cluster-admin` binding from `default` entirely and re-points the
CI pipeline at the new, narrow ServiceAccount — and separately documents a break-glass procedure
(a time-boxed `ClusterRoleBinding` an on-call engineer can request and that auto-expires after four
hours) for the legitimate but rare case of an incident that needs broader diagnostic access than any
standing Role provides.

## Practice Loop

1. Run `kubectl auth can-i --list --as=system:serviceaccount:default:default` against the current
   cluster to see exactly what the unscoped `default` ServiceAccount can currently do.
2. Build the `routeplanner-deployer` ServiceAccount, Role, and RoleBinding from the YAML above and
   apply it to a sandbox namespace.
3. Run a full sweep of `kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<ns>:routeplanner-deployer`
   checks — both the verbs it should have (confirm `yes`) and at least three it should not (confirm
   `no`, including one cluster-scoped check like listing Deployments across all namespaces).
4. Re-point a Deployment's `spec.template.spec.serviceAccountName` at the new, narrow
   ServiceAccount instead of `default`, redeploy, and confirm the workload still functions.
5. Write a one-paragraph break-glass procedure describing how an on-call engineer would request
   temporary elevated access during an incident, and how that access is guaranteed to expire rather
   than becoming a new standing grant.

## Evidence of Understanding

You can build a `ServiceAccount`, `Role`, and `RoleBinding` from scratch scoped to exactly the
verbs and resources a task needs, and you never assume a grant is correctly scoped without
verifying it with `kubectl auth can-i --as`, including checking verbs the identity should *not*
have. You can explain why leaving the namespace's `default` ServiceAccount unscoped is a live risk
tied directly to what happens if any Pod in that namespace is compromised, and why a `Role` is the
least-privilege default choice over a `ClusterRole` whenever access genuinely only needs one
namespace. You can describe a time-boxed emergency-access pattern that avoids the standing-
cluster-admin anti-pattern.

## Suggested Extension

Write the equivalent `Role` for a genuinely read-only monitoring identity (only `get`/`list`/`watch`
on Pods, Deployments, and Services, no write verbs anywhere) and verify with `kubectl auth can-i`
that it cannot perform a single mutating action anywhere in the namespace.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Role versus RoleBinding — what each one actually does
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the distinct job of a `Role` versus a `RoleBinding` in Kubernetes RBAC?

**OPTIONS:**
- [x] A: A `Role` names a set of allowed verbs against specific resource types; a `RoleBinding` is what actually grants that named Role to a specific user, group, or ServiceAccount — a Role alone grants nothing until bound
- [ ] B: A `Role` and a `RoleBinding` are interchangeable terms for the same object
- [ ] C: A `RoleBinding` defines the allowed verbs, and a `Role` specifies which identity receives them
- [ ] D: A `Role` is cluster-scoped and a `RoleBinding` is namespace-scoped

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is explicit about this two-part combination — permissions are defined in one object and
granted to an identity in a separate, distinct object.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [role-vs-rolebinding, rbac-mechanism]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Reading the routeplanner-deployer Role's scope
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the lesson's `routeplanner-deployer-role` manifest, what specifically is this identity NOT
permitted to do?

**CODE_BLOCK:**
```yaml
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    resourceNames: ["routeplanner"]
    verbs: ["get", "list", "watch", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

**OPTIONS:**
- [x] A: It cannot delete the `routeplanner` Deployment, cannot touch any other Deployment by name, and has no write access to Pods at all (only read verbs)
- [ ] B: It cannot read or watch Pods under any circumstances
- [ ] C: It can update any Deployment in the namespace, not just `routeplanner`
- [ ] D: It has full cluster-admin access because no `resourceNames` restriction applies to the second rule

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
`delete` is absent from the Deployment verbs, `resourceNames` restricts the first rule to exactly
`routeplanner`, and the Pod rule grants only read verbs — no write access anywhere in this Role.

**LESSON_CONNECTION:** Chapter Body, Role manifest example
**KEYWORDS:** [role-scope-reading, resourceNames, verb-restriction]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why kubectl auth can-i matters more than reading the YAML
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist on verifying a grant with `kubectl auth can-i --as` rather than trusting
the Role/RoleBinding YAML's correctness by inspection alone?

**OPTIONS:**
- [ ] A: `kubectl auth can-i` is required before any RBAC object can be applied to the cluster
- [x] B: Reasoning about the final effective permission set from YAML alone becomes genuinely error-prone once multiple bindings or role aggregation are involved; asking the API server directly gives a definitive yes/no answer instead of an inference
- [ ] C: RBAC YAML manifests do not take effect until confirmed by `kubectl auth can-i`
- [ ] D: `kubectl auth can-i` is the only way to create a new RoleBinding

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's point is about verification discipline — asking the API server the actual question
rather than trusting a manual read of potentially-interacting YAML objects.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [kubectl-auth-can-i, verification-discipline]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** The specific risk of the unscoped default ServiceAccount
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why was `routeplanner`'s CI Pod running under `default` bound to
`cluster-admin` a serious finding, independent of whether the Pod itself was ever compromised?

**OPTIONS:**
- [ ] A: `cluster-admin` bindings automatically expire after 30 days, so the binding was already invalid
- [x] B: Every Pod in the namespace that doesn't specify its own ServiceAccount inherits whatever `default` can do — the binding meant any Pod in that namespace, not just the CI Pod, could be silently granted cluster-admin-level API access if it were ever compromised
- [ ] C: `cluster-admin` bindings can only be created by a cluster administrator, so its existence indicated an unauthorized privilege escalation had already occurred
- [ ] D: The binding had no actual security implication since the Pod was only used for CI, not customer-facing traffic

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The finding is significant because of what it exposes namespace-wide (every Pod inheriting
`default`), not just because of the one CI Pod's own behavior.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [default-serviceaccount-risk, namespace-wide-exposure]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Role versus ClusterRole as a least-privilege default
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend defaulting to a `Role` over a `ClusterRole` whenever access only
needs to reach one namespace?

**OPTIONS:**
- [ ] A: `ClusterRole` objects are deprecated and scheduled for removal in future Kubernetes versions
- [x] B: A `Role`/`RoleBinding` pair grants access scoped to exactly the one namespace it's created in, while a `ClusterRole`/`ClusterRoleBinding` pair is valid cluster-wide — using the cluster-scoped option when only namespace-scoped access is needed grants more than the task requires
- [ ] C: `Role` objects support a wider range of verbs than `ClusterRole` objects
- [ ] D: `ClusterRole` objects cannot be bound to ServiceAccounts, only to human users

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson frames this as the same least-privilege discipline applied elsewhere in this pathway —
matching the scope of the grant to the scope of the actual need.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [role-vs-clusterrole, least-privilege-default]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What a real least-privilege verification sweep checks
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson's Practice Loop require checking at least three `can-i` calls that should
return `no`, not just confirming the intended access returns `yes`?

**OPTIONS:**
- [ ] A: `kubectl auth can-i` returns an error if fewer than three checks are performed in sequence
- [x] B: Confirming only the intended access proves the grant works, but says nothing about whether it's also granting more than intended — checking that specific unwanted verbs correctly return `no` is what actually proves the boundary is narrow, not just functional
- [ ] C: Checking three `no` cases is a hard requirement enforced by the Kubernetes API server itself
- [ ] D: A single `no` check is sufficient; three is only a stylistic convention with no functional purpose

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Mirrors Lesson 15's two-part connectivity test logic — proving a boundary requires testing the
negative space, not just confirming the positive case works.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [negative-space-testing, rbac-verification]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the break-glass pattern avoids a standing cluster-admin binding
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson recommend for the legitimate case where an operator genuinely needs broader,
emergency diagnostic access than any scoped Role provides?

**OPTIONS:**
- [ ] A: Permanently bind that operator's identity to `cluster-admin` so the access is always available when needed
- [x] B: A separate, short-lived `ClusterRoleBinding` granted for the duration of the incident and explicitly revoked afterward (or an automated break-glass tool that expires the grant), never a standing binding kept "just in case"
- [ ] C: Disable RBAC entirely for the duration of any incident investigation
- [ ] D: Grant the operator a second, permanent ServiceAccount with unrestricted access as a backup

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson explicitly names time-boxing and automatic expiry as what distinguishes a legitimate
break-glass pattern from the standing-cluster-admin anti-pattern it opened with.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (closing)
**KEYWORDS:** [break-glass, time-boxed-access, anti-pattern]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** How this lesson differs from Module 4's Kubernetes security coverage
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson opens by distinguishing itself from Module 4's Kubernetes security lesson. What is that
distinction?

**OPTIONS:**
- [ ] A: Module 4 does not cover RBAC at all, only network policy
- [x] B: Module 4 assumes RBAC is already in place and audits an already-secured, shared multi-tenant cluster; this lesson covers the earlier, hands-on question of how to build a Role/RoleBinding pair from nothing and verify it rather than assume it
- [ ] C: This lesson only applies to ClusterRole objects, while Module 4 only covers Role objects
- [ ] D: The two lessons are functionally identical and either can be skipped without loss

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's opening paragraph states this explicitly — construction-and-verification versus
already-secured-cluster auditing.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (opening)
**KEYWORDS:** [overlap-differentiation, module-4-contrast]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What identity a Pod uses when none is specified
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
If a Pod's spec does not set `serviceAccountName`, which identity does it run under when calling
the Kubernetes API?

**OPTIONS:**
- [ ] A: No identity; API calls from that Pod are rejected entirely
- [x] B: The `default` ServiceAccount of the namespace it runs in, along with whatever permissions that ServiceAccount is bound to
- [ ] C: A randomly-generated, single-use ServiceAccount created just for that Pod
- [ ] D: The identity of the human who last applied the Deployment manifest

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is the exact fact that makes the unscoped-`default` risk real — omission, not explicit
misconfiguration, is enough to inherit whatever `default` is bound to.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [default-serviceaccount, implicit-identity]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 17

```yaml
lesson_id: fde-elective-containerization-orchestration-17-kubernetes-volumes
lesson_title: "Kubernetes Volumes"
lesson_order: 17

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-containerization-orchestration
module_name: "Containerization and Orchestration"
module_order: 0

difficulty: Medium-Hard
estimated_minutes: 60
content_status: Draft

learning_outcomes:
  - "Distinguish an ephemeral volume, a ConfigMap/Secret mount, and a PersistentVolumeClaim by which one survives Pod replacement and which one does not."
  - "Write a PersistentVolumeClaim against a StorageClass, choose an access mode deliberately, and explain what happens to the underlying volume when the claiming Pod is deleted and recreated."
  - "State the snapshot/restore and backup-ownership contract for a stateful component, distinct from the durability guarantee a PVC alone provides."

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
# Kubernetes Volumes

## Concepts Covered

Phase 20's Docker Volumes lesson established the boundary between a container's disposable
filesystem and durable state at the single-host level; this lesson carries the same question onto
Kubernetes, where the added twist is that a Pod isn't just disposable — the *node* it's scheduled
on is disposable too, so "durable" has to mean "survives being rescheduled onto a completely
different machine," not just "survives a container restart." Kubernetes gives you several distinct
volume mechanisms, and picking the wrong one for a given kind of state is the single most common
storage mistake. An `emptyDir` volume is ephemeral scratch space shared between containers in the
same Pod — it survives a container crash and restart *within* the same Pod, but is deleted the
moment the Pod itself is removed, making it the right tool for a cache or a shared working
directory between an app container and a sidecar, and the wrong tool for anything that must outlive
the Pod. A `ConfigMap` volume mounts non-secret configuration data (an environment file, a feature
flag) as files inside the Pod, updated live if the ConfigMap changes (subject to the kubelet's sync
delay) without requiring a Pod restart; a `Secret` volume works identically but for sensitive data
(API keys, database passwords) and is stored by the API server with tighter access controls and
(depending on cluster configuration) at-rest encryption — neither is meant for data the application
itself writes, only for data that's handed *to* it.

```yaml
# routeplanner-storage.yaml — PVC for durable scratch space, plus config/secret mounts
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: routeplanner-cache-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: gp3
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: routeplanner
spec:
  template:
    spec:
      containers:
        - name: routeplanner
          image: routeplanner@sha256:3f9c...
          volumeMounts:
            - name: cache
              mountPath: /var/cache/routeplanner
            - name: config
              mountPath: /etc/routeplanner
            - name: db-credentials
              mountPath: /etc/secrets
              readOnly: true
      volumes:
        - name: cache
          persistentVolumeClaim:
            claimName: routeplanner-cache-pvc
        - name: config
          configMap:
            name: routeplanner-config
        - name: db-credentials
          secret:
            secretName: routeplanner-db-secret
```

For state that must genuinely outlive a Pod being deleted and recreated on a different node
entirely, a `PersistentVolumeClaim (PVC)` is the mechanism: it's a namespaced *request* for storage
(a size, an access mode, optionally a specific `StorageClass`), which the cluster fulfills by
binding it to an actual `PersistentVolume (PV)` — either pre-provisioned by a platform team, or
dynamically provisioned on demand by the named `StorageClass` (`gp3` above, mapping to an AWS EBS
volume type in an EKS cluster). The access mode is a deliberate choice with real consequences:
`ReadWriteOnce (RWO)` means the volume can be mounted read-write by only one node at a time — the
overwhelmingly common case, and the right default for `routeplanner`'s local cache — while
`ReadWriteMany (RWX)` allows multiple nodes to mount the same volume simultaneously (needed for a
shared file store across replicas, but not every storage backend supports it, EBS notably does
not), and `ReadOnlyMany (ROX)` allows many simultaneous read-only mounts. What actually happens
when the claiming Pod is deleted and rescheduled is the detail worth internalizing precisely: the
PVC and its bound PV are *not* deleted with the Pod — a new Pod referencing the same PVC name
reattaches to the same underlying volume with all its data intact, which is exactly the durability
guarantee a PVC provides that `emptyDir` does not. That guarantee is distinct from, and does not by
itself provide, backup and disaster-recovery coverage: a PVC surviving Pod rescheduling protects
against Pod/node churn, not against the underlying volume itself being corrupted, deleted, or lost
to an availability-zone failure — a `VolumeSnapshot` (a point-in-time copy of a PVC's data, taken
via the storage backend's native snapshot capability through the CSI driver) is the separate
mechanism that provides that coverage, and it needs its own explicit retention and restore-testing
policy, the same way any backup strategy does.

## Practical Backend Scenario

Northwind's `routeplanner` gets a local `PersistentVolumeClaim` for its route-calculation result
cache (state that's expensive to recompute but not the source of truth — Postgres owns that), a
`ConfigMap` mount for its non-secret tuning parameters, and a `Secret` mount for its database
credentials. During a node maintenance drain, `routeplanner`'s Pod is deleted and rescheduled onto
a different node entirely; the FDE confirms the new Pod's cache directory still contains the
pre-drain cache contents (proving the PVC — not `emptyDir` — was the right choice) while a
`test-worker` Pod that was mistakenly using `emptyDir` for the same kind of cache loses its cache
completely on the same drain, forcing a costly full recomputation the FDE has to explain to the
platform team as a design mistake, not a platform bug. Separately, when Northwind's security team
asks how the database credential Secret would be recovered if the underlying EBS volume backing it
were somehow deleted, the FDE has to admit that a PVC's durability guarantee alone doesn't cover
that case — a `VolumeSnapshot` schedule needs to exist independently, with a documented restore
test, or "durable" is a claim that's never actually been verified end to end.

## Practice Loop

1. Create the `routeplanner-cache-pvc` PersistentVolumeClaim against a `gp3` (or your cluster's
   available) `StorageClass` and mount it into the `routeplanner` Deployment at
   `/var/cache/routeplanner`.
2. Write some test data into the mounted cache path, delete the Pod (not the PVC), and confirm the
   replacement Pod's cache directory still contains that data after Kubernetes reschedules it.
3. Add a `ConfigMap` mount for a non-secret setting and a `Secret` mount for a credential, and
   confirm both appear as files at their mount paths inside the running container.
4. Compare an `emptyDir`-backed cache against the PVC-backed one across a Pod deletion and
   recreation, and write one sentence stating exactly which one loses its data and why.
5. Take a `VolumeSnapshot` of the PVC (or describe the exact `kubectl` steps if your cluster's CSI
   driver doesn't support it in your sandbox), and write a one-paragraph restore-test plan stating
   how you'd prove the snapshot is actually restorable, not just that it exists.

## Evidence of Understanding

You can distinguish an `emptyDir`, a `ConfigMap`/`Secret` mount, and a `PersistentVolumeClaim` by
which one survives Pod deletion-and-rescheduling and which one does not, and choose the correct one
for a given kind of state. You can write a PVC against a named `StorageClass`, choose an access mode
deliberately (`ReadWriteOnce` versus `ReadWriteMany`) based on whether the volume needs simultaneous
multi-node access, and explain precisely what happens to the underlying data when the claiming Pod
is deleted and a new Pod references the same PVC. You can state why a PVC's durability guarantee
does not by itself cover disaster recovery, and why a `VolumeSnapshot` policy needs its own
explicit retention and restore-testing discipline rather than being assumed to exist.

## Suggested Extension

Write the equivalent manifest for a stateful component that genuinely needs `ReadWriteMany` access
(a shared file store read by multiple `routeplanner` replicas simultaneously), and explain in one
paragraph why this access mode is not universally supported and what you'd need to confirm about
the cluster's storage backend before relying on it.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why "durable" means more in Kubernetes than in plain Docker
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson says the added twist in Kubernetes, compared to Phase 20's Docker Volumes lesson, is
that "the node itself is disposable too." What does this mean for what "durable" has to guarantee?

**OPTIONS:**
- [ ] A: Nothing changes; a Docker volume and a Kubernetes PersistentVolume provide identical guarantees
- [x] B: Durable state must survive not just a container restart, but a Pod being rescheduled onto a completely different physical node — a guarantee a single-host Docker volume, tied to one machine's disk, cannot provide on its own
- [ ] C: Kubernetes volumes are always slower than Docker volumes because of the added node-independence requirement
- [ ] D: "Durable" in Kubernetes only applies to ConfigMaps and Secrets, never to application data

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's opening frames this exact escalation — surviving node loss, not just container
restart, is the new bar Kubernetes storage mechanisms need to clear.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (opening)
**KEYWORDS:** [node-disposability, durability-bar]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What emptyDir actually survives and what it doesn't
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what does an `emptyDir` volume survive, and what does it not survive?

**OPTIONS:**
- [x] A: It survives a container crash and restart within the same Pod, but is deleted the moment the Pod itself is removed
- [ ] B: It survives the Pod being deleted and rescheduled onto a different node, but not a container crash
- [ ] C: It survives everything except a full cluster restart
- [ ] D: It is deleted immediately on any container restart, including one within the same Pod

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the exact boundary the lesson draws — Pod-scoped survival, not Pod-independent durability,
which is what makes it the wrong tool for anything that must outlive the Pod.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [emptydir, pod-scoped-lifetime]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the routeplanner storage manifest
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the lesson's manifest, what happens to `/etc/secrets` inside the `routeplanner` container if the
`routeplanner-db-secret` Secret's value is later rotated?

**CODE_BLOCK:**
```yaml
          volumeMounts:
            - name: db-credentials
              mountPath: /etc/secrets
              readOnly: true
      volumes:
        - name: db-credentials
          secret:
            secretName: routeplanner-db-secret
```

**OPTIONS:**
- [ ] A: The mount path becomes permanently unavailable until the Pod is manually deleted and recreated
- [x] B: The mounted file is updated to reflect the new Secret value (subject to the kubelet's sync delay), the same live-update behavior the lesson describes for ConfigMap mounts, without requiring a Pod restart
- [ ] C: `readOnly: true` prevents the Secret from ever being updated at the API level
- [ ] D: Kubernetes automatically restarts the container whenever a mounted Secret changes
- [ ] E: The old Secret value remains mounted permanently regardless of any change

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson states this explicitly for ConfigMap mounts and notes Secret mounts work identically —
live sync subject to the kubelet's delay, not a Pod restart trigger.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [secret-mount, live-update, kubelet-sync]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** ReadWriteOnce versus ReadWriteMany
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the practical difference between a PVC's `ReadWriteOnce` and `ReadWriteMany` access modes,
and why does the lesson warn that the choice has real consequences?

**OPTIONS:**
- [x] B: `ReadWriteOnce` allows read-write mounting by only one node at a time; `ReadWriteMany` allows multiple nodes to mount the same volume simultaneously — but not every storage backend supports RWX (EBS notably doesn't), so requiring it can constrain which StorageClass a PVC can actually bind to
- [ ] A: `ReadWriteOnce` is read-only, and `ReadWriteMany` is the only mode that permits writes at all
- [ ] C: The two modes are functionally identical; the name only affects logging output
- [ ] D: `ReadWriteMany` is always faster than `ReadWriteOnce` regardless of the storage backend

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson calls out the EBS-doesn't-support-RWX detail specifically as the kind of consequence
that makes this a deliberate choice, not a default to leave unexamined.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [access-modes, rwo-vs-rwx, storage-backend-constraint]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What actually happens to a PVC when its Pod is deleted
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the Practical Backend Scenario, why did `routeplanner`'s cache survive the node drain while
`test-worker`'s cache did not, given that both Pods were deleted and rescheduled?

**OPTIONS:**
- [ ] A: `test-worker` was scheduled onto a node with less available storage capacity
- [x] B: `routeplanner` used a PersistentVolumeClaim, which is not deleted along with its Pod — a new Pod referencing the same PVC reattaches to the same underlying volume with data intact; `test-worker` used `emptyDir`, which is deleted the moment its Pod is removed
- [ ] C: `routeplanner`'s Deployment had a higher priority class than `test-worker`'s
- [ ] D: The node drain only affected `test-worker`'s node, not `routeplanner`'s

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is exactly the PVC-versus-emptyDir distinction the lesson builds toward — the scenario is a
direct, concrete demonstration of the mechanism difference described in Concepts Covered.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [pvc-survival, emptydir-loss, node-drain]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why a PVC alone is not a disaster-recovery guarantee
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE have to tell Northwind's security team that a PVC's durability guarantee alone
doesn't answer how the database credential Secret would be recovered if the underlying volume were
deleted?

**OPTIONS:**
- [ ] A: Secrets cannot be stored on a PersistentVolumeClaim under any circumstances
- [x] B: A PVC surviving Pod/node rescheduling protects against Pod and node churn specifically, not against the underlying volume itself being corrupted, deleted, or lost — that separate failure mode requires its own `VolumeSnapshot` policy with a tested restore path
- [ ] C: The security team's question was based on a misunderstanding; PVCs already provide full disaster recovery automatically
- [ ] D: `VolumeSnapshot` objects are only available for ConfigMaps, not for PVCs backing Secrets

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson is explicit that PVC durability and disaster-recovery coverage are two separate
guarantees — the first doesn't imply the second, and the second needs its own explicit policy.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (closing) / Practical Backend Scenario
**KEYWORDS:** [pvc-vs-disaster-recovery, volumesnapshot, separate-guarantees]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** How a PVC gets bound to actual storage
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the relationship between a `PersistentVolumeClaim` and a `PersistentVolume`, per the
lesson?

**OPTIONS:**
- [ ] A: They are the same object under two different names, used interchangeably
- [x] B: A PVC is a namespaced request for storage (size, access mode, optionally a StorageClass); the cluster fulfills it by binding the PVC to an actual PersistentVolume, either pre-provisioned or dynamically created on demand by the named StorageClass
- [ ] C: A PersistentVolume is created manually for every Pod, and the PVC only exists to delete it afterward
- [ ] D: PVCs are cluster-scoped, while PersistentVolumes are namespace-scoped

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson describes exactly this request/fulfillment relationship, including the dynamic-
provisioning path via a named StorageClass like `gp3`.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [pvc-pv-binding, dynamic-provisioning, storageclass]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why ConfigMaps and Secrets are the wrong tool for application-written data
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson states neither a `ConfigMap` nor a `Secret` mount is "meant for data the application
itself writes." What is the implication of using one for that purpose anyway?

**OPTIONS:**
- [x] A: ConfigMaps and Secrets are meant for data handed to the application, not data the application generates — using either for application-written output misuses a mechanism designed around the API server managing the object's content, not the running container writing to it at runtime
- [ ] B: Kubernetes physically prevents any container process from writing to a ConfigMap or Secret mount path, making the misuse impossible
- [ ] C: There is no meaningful downside; ConfigMaps and Secrets function identically to a PersistentVolumeClaim for any purpose
- [ ] D: Only Secrets are restricted this way; ConfigMaps may be freely written to by the application

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's framing is about the mechanism's intended direction — data flowing in from the API
server to the Pod, not data the Pod generates and needs to persist, which is what a PVC is for.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (closing)
**KEYWORDS:** [configmap-secret-purpose, data-direction]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->
