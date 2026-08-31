# FDE Phase 10 — Module 4: Cloud, DevOps, Kubernetes & Infrastructure (Lessons 7-12 of 12)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-10-cloud-devops-infrastructure-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `cloud-devops-infrastructure` ("4. Cloud, DevOps, Kubernetes & Infrastructure")

This is the second half of the module (lessons 7-12 of 12) and completes it. Phase 9 covered
lessons 1-6 (AWS Core, Compute/Storage, AWS Security, Docker, Kubernetes Architecture, EKS/Helm).

---

# LESSON 7

```yaml
lesson_id: cloud-devops-infrastructure-07-kubernetes-networking-security-and-gpu-workloads
lesson_title: "Kubernetes Networking, Security & GPU Workloads"
lesson_order: 7

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Design a default-deny NetworkPolicy layout that opens only the specific namespace-to-namespace paths a workload actually needs."
  - "Scope RBAC Roles and ServiceAccounts to the minimum verbs and resources a workload's control-plane access actually requires."
  - "Schedule GPU workloads correctly using device-plugin resource requests, node taints/tolerations, and node affinity so GPU capacity isn't silently wasted or misallocated."

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
# Kubernetes Networking, Security & GPU Workloads

## Concepts Covered

By default, every Pod in a Kubernetes cluster can reach every other Pod — there is no implicit network isolation between namespaces the way there's implicit isolation between separate VPCs. A `NetworkPolicy` changes that, but only if the cluster's CNI plugin actually enforces policies (Calico and Cilium do; a bare default CNI without a policy engine silently ignores `NetworkPolicy` objects entirely, which is worth confirming explicitly before relying on one). The correct pattern, mirroring the least-reachability discipline from the AWS Core lesson's security-group design, is default-deny: a policy selecting all Pods in a namespace with empty `ingress` and `egress` rules blocks everything, and then additive `Allow` policies open specific, named paths — a `podSelector` plus `namespaceSelector` combination naming exactly which namespace's Pods may reach this one, on which port. `NetworkPolicy` rules are additive across policies (a Pod matched by multiple policies gets the union of what each allows), not first-match like the security groups from Lesson 1 — which changes how you reason about a review: you can't infer the final effective rule set from reading one policy in isolation, you have to consider every policy that selects the Pod.

RBAC applies the same least-privilege reasoning IAM used for AWS API calls to the Kubernetes API itself. A `Role` and its `RoleBinding` are namespace-scoped; a `ClusterRole` and `ClusterRoleBinding` are cluster-scoped — using a `ClusterRole` binding for something that only ever needs namespace-level access is the RBAC equivalent of the wildcard IAM policy the AWS Core lesson warned against, a broader grant than the task requires. Every Pod runs under a `ServiceAccount` (the `default` one in its namespace if none is specified), and that ServiceAccount's mounted token can call the Kubernetes API with whatever permissions its RBAC bindings grant — a namespace where the `default` ServiceAccount hasn't had its permissions deliberately scoped down is a live risk if any Pod in that namespace is ever compromised, since the attacker inherits whatever that ServiceAccount can do against the API server, not just against the compromised container's own workload. Pod Security Standards (the `restricted`, `baseline`, and `privileged` admission-time levels that replaced the deprecated PodSecurityPolicy) enforce this at Pod creation time rather than relying on convention: `restricted` rejects privileged containers, host namespace access, and root-as-default, which is the same non-root, least-privilege thread the Docker lesson established at image build time, now enforced by the cluster at admission time regardless of what the image itself was built to allow.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: inference
spec:
  podSelector: {}
  policyTypes: ["Ingress", "Egress"]
```

GPU scheduling introduces a resource type ordinary CPU/memory requests don't cover. A device plugin (a DaemonSet, typically the NVIDIA device plugin, running only on nodes with GPU hardware) advertises `nvidia.com/gpu` to the kubelet as an extended resource with an integer quantity — by default the scheduler treats it as indivisible, so a Pod requests `resources.limits: {"nvidia.com/gpu": 1}` for a whole GPU, not a fraction, unless the cluster has additional tooling layered on for time-slicing or MIG partitioning. Because GPU nodes are expensive and scarce relative to ordinary compute, cluster operators taint them (a `NoSchedule` taint on the GPU node pool) specifically so that a workload with no GPU need can't accidentally land there and occupy capacity a GPU workload actually needs; a Pod that wants GPU scheduling needs a matching `toleration` to be schedulable there at all, but the toleration alone only permits scheduling — it doesn't attract it, so GPU-requesting workloads also carry a `nodeSelector` or `nodeAffinity` naming the GPU node pool explicitly, so a Pod isn't left to the scheduler's default placement heuristics for a decision this consequential. The GPU Operator's own DaemonSet needs the identical toleration to run on the tainted nodes in the first place — an operator that isn't tolerated never starts on the GPU node pool, which means the device plugin never registers `nvidia.com/gpu` on those nodes at all, and every GPU workload's request for that resource sits `Pending` for a reason that has nothing to do with the workload's own manifest.

## Practical Backend Scenario

An FDE deploys a fraud-detection ML inference service onto the customer's EKS cluster from the EKS/Helm lesson, sharing the cluster with the order-management API and other teams' workloads, each in its own namespace. The `inference` namespace gets a default-deny `NetworkPolicy` first, then one explicit `Allow` rule permitting ingress only from Pods in the `api-gateway` namespace on port 8080 — no other namespace, including the customer's own analytics team's namespace one row over in the same cluster, can reach it. The inference Deployment's `ServiceAccount`, `inference-sa`, is bound via a `RoleBinding` to a `Role` granting only `get`/`list`/`watch` on `ConfigMaps` in its own namespace — the one thing it actually needs, to read which model version is currently active — and nothing else; it cannot list `Secrets`, cannot touch another namespace, and cannot modify anything. The Deployment requests `nvidia.com/gpu: 1`, carries the toleration matching the GPU node pool's taint, and specifies `nodeAffinity` naming that node pool explicitly. During initial rollout, the FDE forgets the toleration, and the Pod sits `Pending` indefinitely — not crashing, not erroring, just unscheduled — until `kubectl describe pod` surfaces the exact scheduling-failure event naming the untolerated taint as the reason, which is the concrete diagnostic signal that distinguishes "this Pod is broken" from "this Pod is correctly refusing to run somewhere it shouldn't."

## Practice Loop

1. Write the default-deny `NetworkPolicy` for the `inference` namespace, apply it, and confirm — by testing a request that previously worked — that it now breaks.
2. Add the explicit allow-ingress rule scoped to the `api-gateway` namespace via `namespaceSelector` and `podSelector`, and confirm the service works again only from that source.
3. Diagnostic: send a request to the inference service from a Pod in an unrelated third namespace and record exactly what happens (connection refused, timeout, which) versus a request from the `api-gateway` namespace, and note the difference.
4. Write the `Role` and `RoleBinding` scoping `inference-sa` to `get`/`list`/`watch` on `ConfigMaps` only, then `kubectl exec` into a Pod using that ServiceAccount and attempt to list `Secrets` — confirm the API server denies it and record the exact error.
5. Add the GPU resource request, toleration, and node affinity to the Deployment; deliberately remove just the toleration and observe the Pod stuck `Pending`, reading the scheduling-failure event that names the taint, then restore the toleration and confirm it schedules.

## Evidence of Understanding

You can design a default-deny `NetworkPolicy` layout and add exactly the additive allow rules a workload needs, and explain why `NetworkPolicy` enforcement depends on the cluster's CNI plugin rather than being guaranteed by the object's existence alone. You can scope a `ServiceAccount`'s RBAC permissions to the minimum verbs and resources a workload's own control-plane access requires, and explain the risk a permissive default `ServiceAccount` creates if the workload is ever compromised. You can schedule a GPU workload correctly using a device-plugin resource request, a matching toleration, and node affinity, and can read a `Pending` Pod's scheduling-failure event to diagnose a missing toleration rather than assuming the workload itself is broken.

## Suggested Extension

Add a `NetworkPolicy` egress rule restricting the inference Pods to reach only the specific IP range of the model-artifact S3 VPC endpoint, and explain why an unrestricted egress rule would have undermined the entire namespace-isolation design even with every ingress rule locked down correctly.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** When a NetworkPolicy is actually enforced
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson say is required before a `NetworkPolicy` object actually has any effect on traffic?

**OPTIONS:**
- [x] A: The cluster's CNI plugin must implement policy enforcement (like Calico or Cilium) — without one, a `NetworkPolicy` object is silently ignored even though it exists in the cluster
- [ ] B: Every Pod in the cluster must be manually labeled with a "policy-enabled" annotation before any NetworkPolicy applies
- [ ] C: NetworkPolicy objects are enforced automatically by every Kubernetes distribution with no dependency on the CNI
- [ ] D: NetworkPolicy only works for Pods running on GPU-tainted nodes

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a genuinely easy trap — a `NetworkPolicy` can exist, be well-written, and do nothing at all if the CNI doesn't enforce policies, which is why confirming enforcement explicitly matters before relying on one.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [networkpolicy-enforcement, cni-dependency]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Additive policies versus first-match security groups
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say you can't infer a Pod's final effective NetworkPolicy rules by reading just one policy that selects it?

**OPTIONS:**
- [x] A: NetworkPolicy rules are additive across every policy that selects a Pod — the effective rule set is the union of all of them, unlike a first-match evaluation order
- [ ] B: Kubernetes always applies only the most recently created policy and ignores any older ones
- [ ] C: A Pod can only ever be selected by exactly one NetworkPolicy at a time
- [ ] D: NetworkPolicy rules are evaluated in alphabetical order by policy name, with the first match winning

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The additive/union behavior is exactly why a full review has to consider every policy selecting a Pod, not just the one you happen to be reading — a different mental model than a first-match rule list.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [networkpolicy-additive, policy-review]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Role versus ClusterRole scope
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson call using a ClusterRole binding for a workload that only needs namespace-level access the RBAC equivalent of a wildcard IAM policy?

**OPTIONS:**
- [x] A: It grants a broader scope than the task requires — cluster-wide instead of namespace-scoped — the same unnecessary blast-radius expansion the AWS Core lesson warned against for wildcard IAM actions and resources
- [ ] B: ClusterRoles are technically deprecated and no longer function in current Kubernetes versions
- [ ] C: A Role and a ClusterRole always grant identical permissions regardless of scope
- [ ] D: RBAC has no meaningful concept of scope; all bindings are cluster-wide by default

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The parallel is deliberate — both cases are about granting more surface than the actual task needs, whether that surface is an AWS resource ARN or a Kubernetes API scope.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [role-vs-clusterrole, least-privilege-rbac]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why an unscoped default ServiceAccount is a risk
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson treat a namespace's un-scoped `default` ServiceAccount as a live security risk, even if the Pods running under it appear to be working correctly?

**OPTIONS:**
- [x] A: If any Pod in that namespace is ever compromised, the attacker inherits whatever the ServiceAccount's RBAC bindings allow against the Kubernetes API — a risk that exists independent of whether the workload is currently functioning correctly
- [ ] B: The default ServiceAccount has no effect on security at all, since it can never be used to call the Kubernetes API
- [ ] C: This risk only applies to Pods that explicitly request `nvidia.com/gpu` resources
- [ ] D: Kubernetes automatically scopes every default ServiceAccount to read-only access with no configuration needed

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the same "what could go wrong if compromised" test the AWS Core lesson applied to IAM — a workload functioning correctly says nothing about whether it also carries far more API access than it needs.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [default-serviceaccount-risk, compromise-blast-radius]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What Pod Security Standards enforce, and when
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How do Pod Security Standards' `restricted` level relate to the Docker lesson's non-root, least-privilege thread?

**OPTIONS:**
- [x] A: They enforce the same non-root, least-privilege discipline, but at Pod admission time by the cluster, regardless of what the container image itself was built to allow — rather than relying on the image build alone
- [ ] B: Pod Security Standards replace the need for a non-root user in the Dockerfile entirely, making that earlier lesson's guidance obsolete
- [ ] C: They only apply to Pods that do not request any GPU resources
- [ ] D: `restricted` is the least strict of the three levels, allowing privileged containers by default

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a deliberate cross-lesson echo — the same discipline reappears as a cluster-enforced admission control instead of an image-build convention, closing the gap left if an image itself wasn't built correctly.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [pod-security-standards, docker-lesson-connection]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What a GPU toleration alone accomplishes
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A Pod requesting `nvidia.com/gpu: 1` has a toleration matching the GPU node pool's taint, but no node affinity or node selector naming that pool. What does the lesson say this leaves unresolved?

**OPTIONS:**
- [x] A: The toleration only permits the Pod to be scheduled on the tainted GPU nodes — it doesn't attract the scheduler toward them, so placement is left to the scheduler's default heuristics for a decision that deserves an explicit choice
- [ ] B: The Pod is guaranteed to be rejected outright without a node selector, since a toleration alone is invalid configuration
- [ ] C: The toleration automatically implies node affinity for the matching taint's node pool
- [ ] D: Without a node selector, the Pod cannot request `nvidia.com/gpu` at all

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Tolerating a taint permits scheduling there; it doesn't direct the scheduler there — the lesson is explicit that GPU placement deserves the more deliberate node affinity/selector, not just a toleration.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [gpu-toleration-vs-affinity, scheduling-precision]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Diagnosing the Pending inference Pod
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, the inference Pod is stuck `Pending` after the FDE forgets the GPU toleration. What does `kubectl describe pod` reveal, and why does that matter diagnostically?

**OPTIONS:**
- [x] A: A scheduling-failure event naming the untolerated taint as the specific reason — distinguishing "this Pod is correctly refusing to run somewhere it shouldn't" from a crash or generic error, which would otherwise send the FDE looking in the wrong place
- [ ] B: A CrashLoopBackOff error indicating the container failed to start due to a code exception
- [ ] C: Nothing — Pending Pods with a missing toleration produce no diagnostic event at all
- [ ] D: An OOMKilled event indicating the Pod exceeded its memory limit

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The specific, named scheduling-failure event is the concrete diagnostic signal — without reading it, a missing toleration looks like an unexplained stall rather than an identifiable, fixable cause.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [pending-pod-diagnosis, scheduling-failure-event]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why the inference namespace's RoleBinding is scoped so narrowly
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, `inference-sa`'s Role grants only `get`/`list`/`watch` on ConfigMaps in its own namespace. Why exactly that set, and nothing more?

**OPTIONS:**
- [x] A: It matches the one genuine need — reading which model version is currently active — while denying everything else, including listing Secrets or reaching another namespace, so a compromise of this Pod has a small, bounded, explainable blast radius
- [ ] B: Kubernetes RBAC does not support granting write permissions to ServiceAccounts under any circumstances
- [ ] C: ConfigMap access is required for GPU scheduling to function at all
- [ ] D: This scoping has no security rationale; it was chosen arbitrarily as a minimal example

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is least privilege applied concretely — the grant matches the actual task (reading model version config) and nothing else, so the answer to "what could this Pod do if compromised" stays short and specific.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scoped-rolebinding, blast-radius]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why the default-deny policy is applied before any allow rule
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the practice loop have you apply the default-deny NetworkPolicy first, confirming it breaks existing traffic, before adding the explicit allow rule?

**OPTIONS:**
- [x] A: It makes the isolation verifiable rather than assumed — confirming traffic actually breaks under default-deny proves the policy is enforced, so the later allow rule can be trusted to be the only path back in, not one of several unnoticed gaps
- [ ] B: Kubernetes requires NetworkPolicy objects to be applied in a specific numbered order or the API server rejects them
- [ ] C: There is no reason for this order; applying the allow rule first would produce an identical result
- [ ] D: Breaking traffic temporarily is required to reset the CNI plugin's internal state

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Confirming the deny actually takes effect is the diagnostic step that turns "I wrote a policy" into "I verified isolation" — an unverified default-deny could be silently unenforced, per Q1's CNI dependency.

**LESSON_CONNECTION:** Practice Loop, Step 1
**KEYWORDS:** [verify-before-trust, default-deny-validation]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 8

```yaml
lesson_id: cloud-devops-infrastructure-08-ci-cd-pipelines-and-gitops-github-actions-argocd
lesson_title: "CI/CD Pipelines & GitOps (GitHub Actions, ArgoCD)"
lesson_order: 8

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Explain why GitOps's pull-based reconciliation model removes the need for a CI pipeline to ever hold a production cluster credential."
  - "Design a CI/CD split where GitHub Actions owns build/test/push and a separate manifests repo plus ArgoCD owns deployment."
  - "Explain what ArgoCD self-heal enforces in practice, and why a manual cluster change gets reverted rather than persisting."

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
# CI/CD Pipelines & GitOps (GitHub Actions, ArgoCD)

## Concepts Covered

CI and CD answer genuinely different questions, and keeping them separate is what makes GitOps's design make sense. CI (build, test, produce an artifact) answers "is this change correct, and does it produce a valid deployable artifact" — the same PR-gated, required-check discipline the FDE Foundations module's Git/GitHub lesson and the testing/CI lesson established, where a pull request cannot merge until the test suite passes. CD answers "is that artifact actually running in the target environment," and GitOps's central move is making CD pull-based and declarative instead of push-based and imperative: rather than the CI pipeline holding a credential capable of writing to the production cluster and running `kubectl apply` the moment code merges, a controller running inside the cluster (ArgoCD) continuously reconciles the live cluster state against a desired state declared in Git, and applies whatever diff exists between the two. This is the same "declare the target state, let a controller reconcile toward it" logic a Kubernetes Deployment already uses for its own replica count, applied one layer up to the entire set of cluster manifests.

This decoupling has a concrete security payoff worth stating precisely, not just architecturally: the CI pipeline never needs a credential capable of writing to the production cluster at all. GitHub Actions builds the image, pushes it to a registry, and its last action is a Git commit to a separate manifests repository updating an image tag — a credential scoped to that one repository, nothing more. ArgoCD, running inside the cluster with its own cluster-scoped credential, is the only thing that ever calls the Kubernetes API to apply changes, and every change it makes traces back to a specific, reviewable Git commit rather than a CI run's transient log output. Self-heal — ArgoCD continuously re-applying the declared state whenever it detects the live cluster has drifted from Git, such as an engineer running a manual `kubectl edit` during an incident — is the concrete mechanism that makes "Git is the source of truth" actually true in practice, not just true in aspiration: without self-heal, a manual hotfix silently becomes the de facto state until an unrelated sync happens to overwrite it later, which is a confusing, hard-to-explain source of incidents in its own right. ArgoCD's sync status (`Synced`/`OutOfSync`) and health status (`Healthy`/`Degraded`/`Progressing`) are two genuinely separate signals worth reading correctly: sync status says whether the live cluster matches Git, health status says whether the resources that match Git are actually working — a Deployment can be perfectly `Synced` to a broken manifest and still be `Degraded`, which is exactly the case where the fix is a new commit correcting the manifest, not a re-sync of the one already applied.

```yaml
# order-management-gitops repo: overlays/prod/kustomization.yaml
images:
  - name: order-management
    newTag: a1b2c3d   # updated by the GitHub Actions workflow, not by hand
```

The split into an application repo and a separate manifests (GitOps) repo is deliberate, not incidental. It keeps ArgoCD watching only deployment-relevant changes — image tags, config, replica counts — instead of attempting a reconciliation on every application-code commit, and it lets the manifests repo carry its own review discipline: a required PR review on a production image-tag bump is a meaningfully different gate than the code review the application repo already required to get that image built in the first place. Progressive delivery tooling (Argo Rollouts, canary and blue-green strategies) builds on the same reconciliation loop, incrementally shifting traffic to a new ReplicaSet based on live health signals instead of ArgoCD's default all-at-once rollout — which matters when a bad release needs to be caught by a small fraction of real traffic before it reaches everyone, echoing the same "confirm it actually works in production, not just in a demo" caution the FDE-role lesson opened this course with. Required checks and required reviewers are configured on the manifests repo the same way they'd be configured on an application repo, but the review question they're actually gating is different — an application-repo reviewer is asking "is this code change correct," while a manifests-repo reviewer is asking "should this exact artifact be running in production right now," and conflating the two into a single gate loses the second question's answer the moment it's needed most, during an unplanned rollback where the code is already known-good and the only open question is whether it should be live.

## Practical Backend Scenario

The order-management service's deployment pipeline: a GitHub Actions workflow triggers on merge to `main`, runs the test suite from the Backend Observability module's CI lesson as a required check, builds and pushes an image to ECR tagged with the commit SHA, and its final step commits to a separate `order-management-gitops` repository updating the image tag in a Kustomize overlay — using a credential scoped only to that manifests repo, never a cluster credential. ArgoCD, watching that repo, detects the diff within its configured reconciliation interval and syncs the change to the EKS cluster. During an incident, an on-call engineer manually edits the Deployment's replica count via `kubectl` to add capacity immediately, and three minutes later ArgoCD's self-heal reverts it back to whatever the manifests repo declares — confusing, until the FDE explains that the correct fix is committing the new replica count to the manifests repo itself, at which point ArgoCD applies it and stops reverting it, because Git now agrees with what the engineer wanted.

## Practice Loop

1. Write the GitHub Actions workflow's stages (test, build, push, update manifest repo) and identify exactly which stage, if this were push-based CD instead of GitOps, would need a production cluster credential — confirm none of your actual GitOps stages need one.
2. Set up the separate manifests repo with a Kustomize overlay for the order-management Deployment, and configure ArgoCD to watch it with auto-sync and self-heal enabled.
3. Diagnostic: manually edit the live Deployment's image tag via `kubectl` to a value different from what's in Git, and time exactly how long ArgoCD's next reconciliation takes to revert it.
4. Make the same change correctly by committing the new image tag to the manifests repo instead, and confirm ArgoCD applies it without reverting anything.
5. Review the manifests repo's commit history for one week of simulated deploys, and confirm every production change traces back to a specific, identifiable commit rather than an untracked manual change.

## Evidence of Understanding

You can explain the distinct questions CI and CD each answer, and why GitOps makes CD pull-based rather than push-based. You can design a CI/CD split where GitHub Actions never holds a production cluster credential, with ArgoCD as the only component that writes to the cluster, and explain the security and audit-trail benefit that split produces. You can explain what ArgoCD self-heal enforces in practice — why a manual cluster change gets reverted rather than persisting — and why that behavior is what actually makes Git the source of truth instead of merely the intended one.

## Suggested Extension

Add an Argo Rollouts canary step that shifts 10% of traffic to a new order-management ReplicaSet and automatically rolls back if the error rate observed via the OTel metrics from Module 2 exceeds a threshold, and explain what live signal that automated rollback depends on that a plain ArgoCD sync wouldn't check on its own.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** The distinct questions CI and CD answer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what distinct question does CD answer that CI does not?

**OPTIONS:**
- [x] A: Whether the built and tested artifact is actually running in the target environment — CI only answers whether the change is correct and produces a valid artifact
- [ ] B: CD and CI answer the identical question; the distinction is purely a naming convention
- [ ] C: CD answers whether the code compiles, which CI does not check
- [ ] D: CD is only relevant for GPU workloads, while CI applies to all other workload types

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Keeping these two questions distinct is what makes the rest of the GitOps design legible — CI validates the artifact, CD is a separate concern about that artifact's actual running state.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [ci-vs-cd, gitops-motivation]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why GitOps's pull model removes a CI credential
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say the GitHub Actions pipeline never needs a credential capable of writing to the production cluster under the GitOps pattern described?

**OPTIONS:**
- [x] A: Its last action is a Git commit to a separate manifests repo, requiring only a credential scoped to that repo — ArgoCD, running inside the cluster with its own credential, is the only component that ever calls the Kubernetes API to apply changes
- [ ] B: GitHub Actions is technically incapable of authenticating to any Kubernetes cluster under any configuration
- [ ] C: A cluster credential is still required in CI, just stored differently, so the security benefit described doesn't actually hold
- [ ] D: ArgoCD requires the CI pipeline to supply a cluster credential on every sync

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The pull-based design is exactly what eliminates the need — the CI pipeline's last write is to a Git repo it already has narrow access to, not to the cluster itself.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [gitops-credential-scoping, pull-based-cd]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What ArgoCD self-heal actually enforces
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why does ArgoCD revert the on-call engineer's manual `kubectl` replica-count change three minutes later?

**OPTIONS:**
- [x] A: Self-heal continuously re-applies the state declared in Git whenever the live cluster drifts from it — a manual change that wasn't made through Git is exactly the drift self-heal is designed to correct
- [ ] B: ArgoCD detected the change was made by an unauthorized user account and blocked it specifically for that reason
- [ ] C: Kubernetes itself, not ArgoCD, automatically reverts any manual kubectl edit after a fixed timeout
- [ ] D: The revert is a bug in ArgoCD's default configuration that most teams disable

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the concrete enforcement mechanism the lesson highlights — self-heal is what makes "Git is the source of truth" actually true rather than aspirational.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [argocd-self-heal, drift-correction]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** The correct way to make the replica-count change stick
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given self-heal's behavior in the scenario, what is the correct way for the engineer to make the increased replica count actually persist?

**OPTIONS:**
- [x] A: Commit the new replica count to the manifests repo, so Git now agrees with the desired state — ArgoCD will then apply it and stop reverting it
- [ ] B: Disable ArgoCD self-heal permanently across the entire cluster so manual kubectl edits are never reverted again
- [ ] C: Repeat the manual kubectl edit more frequently than ArgoCD's reconciliation interval
- [ ] D: Edit the replica count directly in ArgoCD's own internal database rather than in Kubernetes or Git

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The fix works with the reconciliation loop rather than fighting it — once Git reflects the desired state, ArgoCD applies exactly that instead of reverting it.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [gitops-correct-change-path, self-heal-resolution]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the manifests repo is separate from the application repo
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson treat the split between an application repo and a separate GitOps manifests repo as deliberate rather than incidental?

**OPTIONS:**
- [x] A: It keeps ArgoCD watching only deployment-relevant changes instead of triggering on every application-code commit, and lets the manifests repo carry its own review discipline distinct from the application code review
- [ ] B: Kubernetes technically requires manifests and application code to live in physically separate Git hosting providers
- [ ] C: A single combined repo would exceed GitHub's maximum file-count limit for any real application
- [ ] D: The split exists only to satisfy a naming convention with no functional benefit

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The separation is functional, not cosmetic — it scopes what ArgoCD reacts to and lets the manifests repo apply a review gate suited specifically to production deployment changes.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [manifests-repo-separation, review-discipline]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why every production change traces to a commit
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson claim that under the GitOps pattern described, every change ArgoCD makes to the cluster traces back to a specific, reviewable Git commit rather than a CI run's transient log?

**OPTIONS:**
- [x] A: ArgoCD only ever applies what's declared in the manifests repo, and that repo's commit history is the durable record of every desired-state change — unlike CI logs, which can rotate out or be harder to correlate after the fact
- [ ] B: ArgoCD writes its own separate audit log that has nothing to do with Git commit history
- [ ] C: CI run logs are actually more durable and reliable than Git commit history for this purpose
- [ ] D: This traceability claim only holds if the cluster has CloudTrail data events enabled

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Because ArgoCD's only input is the manifests repo, the repo's commit history is inherently the durable, reviewable record of every change it ever applied.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [audit-trail, gitops-traceability]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What progressive delivery adds on top of ArgoCD's default sync
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson describe what progressive delivery tooling (Argo Rollouts) adds compared to ArgoCD's default all-at-once rollout?

**OPTIONS:**
- [x] A: It incrementally shifts traffic to a new ReplicaSet based on live health signals, catching a bad release with a small fraction of real traffic before it reaches everyone
- [ ] B: It replaces ArgoCD's reconciliation loop with a completely different, unrelated deployment mechanism
- [ ] C: It removes the need for a manifests repo entirely
- [ ] D: It only applies to Lambda-based deployments, not Kubernetes Deployments

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Progressive delivery builds on the same reconciliation loop but adds gradual, health-signal-driven traffic shifting instead of switching every replica over at once.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [progressive-delivery, canary-rollout]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Connecting this pipeline's CI stage to earlier lessons
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the scenario's GitHub Actions test-suite stage connect to the FDE Foundations Git/GitHub lesson and the Backend Observability CI lesson?

**OPTIONS:**
- [x] A: It reuses the same PR-gated, required-check discipline — the test suite must pass before an image is even built, the identical "CI gates the merge" pattern established in those earlier lessons, now feeding into a GitOps deployment instead of ending at merge
- [ ] B: There is no meaningful connection; the CI stage in this lesson is an entirely new mechanism unrelated to earlier lessons
- [ ] C: The connection only holds if the test suite specifically includes Hypothesis property-based tests
- [ ] D: The Git/GitHub lesson's discipline applies only to Python projects, not to a containerized service like order-management

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a deliberate cross-module echo — the same required-check gating discipline extends naturally into a pipeline that also handles deployment, not a new, unrelated practice.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [ci-gating-reuse, cross-module-connection]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 9

```yaml
lesson_id: cloud-devops-infrastructure-09-terraform-and-infrastructure-as-code
lesson_title: "Terraform & Infrastructure as Code"
lesson_order: 9

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Explain Terraform's declarative plan/apply model as the infrastructure-layer analog of the hexagonal-architecture port/adapter split."
  - "Configure a remote backend with state locking and explain why concurrent applies against unlocked shared state are unsafe."
  - "Diagnose infrastructure drift from a `terraform plan` diff and choose deliberately between reconciling it into configuration or reverting it."

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
# Terraform & Infrastructure as Code

## Concepts Covered

Terraform's declarative model is the direct infrastructure-layer analog of the hexagonal-architecture lesson's port/adapter reasoning. A `.tf` configuration describes the desired end state — this VPC, these subnets, this RDS instance, with these exact attributes — not the imperative sequence of AWS API calls needed to reach it, and Terraform's own job is diffing that declared state against its record of the last-known real state, then computing the minimal set of API calls to reconcile the two. That's the same "describe the what, let the mechanism supply the how" separation that made a `PaymentAuthorizer` interface valuable instead of inlining provider-specific calls directly into the order service. A hand-rolled provisioning script calling `aws ec2 create-*` commands in sequence is the imperative equivalent of the pre-interface procedural code from the polymorphism lesson: it works for the one path it was written for, but re-running it against an already-provisioned environment, or reasoning about what state a partial failure left behind, requires the script's author to have manually encoded every case Terraform's `plan`/`apply` diff computes automatically.

The state file is not an implementation detail to skip past — it's the ground truth Terraform diffs against, mapping every resource block in a configuration to a specific real AWS resource ID. Losing or corrupting it means Terraform can no longer tell what it already created, leading either to duplicate resources on the next `apply` or to a `plan` that wants to destroy something still genuinely in use. This is why a remote backend (state stored in S3, not on an engineer's laptop) with state locking is treated as non-negotiable for any team larger than one person: locking exists specifically to prevent two concurrent `terraform apply` runs from racing each other and corrupting the state — the infrastructure equivalent of two database transactions writing the same row with no lock between them. State locking has traditionally used a separate DynamoDB table to track who currently holds the lock; Terraform 1.11 added native S3-based locking as a simpler alternative for teams already on an S3 backend, removing the need for that separate table. The state file itself should be encrypted at rest and access-controlled with the same least-privilege discipline as the AWS Core lesson's IAM policies, because it often contains sensitive values — a database password set via a Terraform variable ends up in plaintext in the state file unless the backend encrypts at rest and the value is explicitly marked sensitive — and treating state as just another config artifact instead of a secret-adjacent asset is a common, avoidable exposure.

```hcl
terraform {
  backend "s3" {
    bucket       = "customer-terraform-state"
    key          = "prod/order-management/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

Modules are Terraform's reuse mechanism — a module packages a set of resources (a VPC with its subnets, route tables, and endpoints, matching the AWS Core lesson's design) behind input variables and output values, the same interface-first thinking as an OOP abstraction: a consuming configuration passes in a CIDR block and gets back subnet IDs without needing to know the module's internal resource count or naming. Separating state per environment — dev, staging, and prod each with their own state file, rather than one shared state distinguishing environments via `count` or `for_each` — reduces blast radius the same way the AWS Core lesson's IAM policies scoped access to a specific resource ARN: a mistaken `apply` against the wrong state file is a small, contained mistake, not one shared state where an error can touch every environment at once. Drift — a resource's real AWS state diverging from what the state file records, usually because someone made a manual console change — surfaces as an unexpected diff in `terraform plan` even though no configuration changed, and the deliberate choice is either to reconcile the configuration to match an intentional manual change or to `apply` and revert it; leaving drift undiagnosed means the next `apply` behaves unpredictably against a state file that no longer reflects reality. Terraform's provider ecosystem extends this same declarative model to more than raw AWS resources — a Kubernetes provider can manage Helm releases, and a Vault or AWS provider can manage secrets — but stacking every layer of a system into one Terraform configuration trades away the layer-appropriate tooling from earlier lessons (Helm's own templating and release history, ArgoCD's reconciliation loop) for a single tool's plan/apply model, which is worth doing deliberately rather than by default; most production setups keep Terraform scoped to the infrastructure layer and let GitOps own the workload layer specifically so each tool is used where its own model fits best.

## Practical Backend Scenario

An FDE provisions the VPC, subnets, security groups, and RDS instance for the order-management system (from the AWS Core and Compute/Storage lessons) using a `vpc` module and an `rds` module, each with their own input variables and output values, composed in a root `environments/prod` configuration with remote state in S3 and locking enabled. Mid-engagement, a customer engineer, troubleshooting an urgent connectivity issue, manually adds an inbound rule to the RDS security group via the AWS console to unblock themselves, without telling anyone. The next `terraform plan` the FDE runs shows an unexpected diff — Terraform wants to remove that rule, since it doesn't exist anywhere in the module's configuration — which is exactly how the drift gets surfaced instead of silently persisting as an unreviewed, undocumented hole in the security group. The FDE reconciles by adding the exact rule to the module's configuration, turning the emergency fix into a reviewed, permanent, declared part of the infrastructure, rather than either blindly reverting a fix someone genuinely needed or leaving an undocumented change sitting in production indefinitely.

## Practice Loop

1. Write a minimal `vpc` module with input variables and output values matching the AWS Core lesson's subnet design, and a root configuration that consumes it.
2. Configure a remote S3 backend with state locking for the root configuration, and confirm two simultaneous `apply` attempts against the same state produce a lock-conflict error instead of racing.
3. Diagnostic: manually add a security-group rule via the AWS console outside of Terraform, then run `terraform plan` and read the exact diff it reports — confirm it identifies precisely the manually-added rule as the unexpected change.
4. Decide, and justify in one sentence, whether to reconcile the manual change into the module's configuration or revert it with `apply`, and carry out that choice.
5. Split the root configuration's state into separate per-environment state files (dev/prod), and confirm an `apply` against the dev state file cannot touch any prod resource.

## Evidence of Understanding

You can explain Terraform's plan/apply model as declaring desired state and letting the tool compute the reconciling diff, and connect that reasoning to the same port/adapter separation from the hexagonal-architecture lesson. You can configure a remote backend with state locking and explain concretely what unsafe outcome locking prevents. You can read a `terraform plan` diff to identify infrastructure drift, and choose deliberately between reconciling a manual change into configuration versus reverting it, rather than leaving the drift unaddressed.

## Suggested Extension

Add a `terraform plan` step to the CI/CD pipeline from the previous lesson that posts the plan output as a PR comment before any `apply` happens, and explain why running `plan` in CI — not just locally on an engineer's machine — matters for the same audit-trail reason ArgoCD's Git-sourced changes did in that lesson.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Terraform's declarative model versus a hand-rolled script
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson call a hand-rolled provisioning script the imperative equivalent of the polymorphism lesson's pre-interface procedural code?

**OPTIONS:**
- [x] A: It works for the one path it was written for, but re-running it against an already-provisioned environment or reasoning about a partial failure requires the author to have manually encoded every case Terraform's plan/apply diff computes automatically
- [ ] B: Hand-rolled scripts are technically incapable of calling any AWS API
- [ ] C: There is no meaningful difference between a Terraform configuration and an equivalent bash script
- [ ] D: This comparison only applies to scripts that provision RDS instances specifically

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The comparison is precise — a hand-rolled script only handles the cases its author anticipated, while Terraform's diff-based reconciliation handles the general case of "what's the difference between desired and actual state" automatically.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [declarative-vs-imperative, hexagonal-analogy]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What Terraform's state file actually is
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist the state file is not an implementation detail to skip past?

**OPTIONS:**
- [x] A: It's the ground truth mapping every resource block in configuration to a specific real resource ID, and losing or corrupting it means Terraform can no longer tell what it already created — leading to duplicate resources or a plan that wants to destroy things still in use
- [ ] B: The state file only matters for cosmetic reasons, like formatting `terraform plan`'s output
- [ ] C: Terraform can always regenerate a lost state file automatically from the AWS account with no data loss
- [ ] D: The state file exists purely for Terraform's internal logging and has no bearing on plan/apply behavior

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The state file is what lets Terraform reason about "what already exists" — without an accurate one, the plan/apply diff has nothing reliable to compare the configuration against.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [state-file-purpose, ground-truth]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What state locking actually prevents
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific problem does state locking prevent, per the lesson's database-transaction analogy?

**OPTIONS:**
- [x] A: Two concurrent `terraform apply` runs racing each other and corrupting the shared state file — the same hazard as two database transactions writing the same row with no lock between them
- [ ] B: A single engineer accidentally running `terraform destroy` instead of `terraform apply`
- [ ] C: Terraform configuration files being edited by two people in the same Git branch
- [ ] D: An AWS resource being deleted manually through the console

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Locking's entire purpose is preventing two concurrent writers from racing against the same state file — the exact hazard the transaction-locking analogy is meant to make concrete.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [state-locking, concurrent-apply-race]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the state file needs the same discipline as an IAM policy
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say the state file should be treated with the same least-privilege discipline as the AWS Core lesson's IAM policies?

**OPTIONS:**
- [x] A: The state file often contains sensitive values in plaintext — a database password set via a Terraform variable ends up in the state file unless the backend encrypts at rest and the value is marked sensitive — making it a secret-adjacent asset, not just a config artifact
- [ ] B: Terraform state files are technically stored as IAM policy documents themselves
- [ ] C: This concern only applies when the state file is stored locally rather than in a remote backend
- [ ] D: State files never contain any sensitive data by design, so this comparison is purely stylistic

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Treating the state file as "just config" misses that it can hold real secrets in plaintext — the same access-control discipline that scopes IAM policies applies here for the same reason.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [state-file-secrets, access-control]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why modules parallel an OOP interface
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson compare a Terraform module's input variables and output values to interface-first OOP thinking?

**OPTIONS:**
- [x] A: A consuming configuration passes inputs (like a CIDR block) and gets back outputs (like subnet IDs) without needing to know the module's internal resource count or naming — the same "depend on the contract, not the implementation" pattern
- [ ] B: Terraform modules are compiled using the same bytecode as Java interfaces
- [ ] C: A module's internal resource structure must always be visible to any configuration that consumes it
- [ ] D: Modules and interfaces share no meaningful conceptual similarity; the comparison is purely coincidental phrasing

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The module's variables/outputs are its contract — a consumer depends on that contract without needing to know how the module implements it internally, mirroring interface-based design.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [terraform-modules, interface-analogy]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Diagnosing drift in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, how does the FDE first discover the customer engineer's manual security-group change?

**OPTIONS:**
- [x] A: The next `terraform plan` shows an unexpected diff — Terraform wants to remove a rule that doesn't exist in the module's configuration, surfacing the drift automatically
- [ ] B: The customer engineer immediately reports the change through a support ticket
- [ ] C: CloudTrail sends an automatic email notification listing every manual console change
- [ ] D: The RDS instance fails to start until the FDE investigates manually

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is exactly how Terraform surfaces drift — an unexpected diff in `plan`, computed by comparing the state file against real, current AWS state.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [drift-detection, terraform-plan-diff]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the FDE reconciles rather than reverting outright
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why does the FDE add the manually-created rule into the module's configuration rather than simply running `apply` to revert it?

**OPTIONS:**
- [x] A: The manual rule fixed a genuine connectivity issue — reconciling it into configuration turns an undocumented emergency fix into a reviewed, permanent, declared part of the infrastructure instead of either silently reverting a needed fix or leaving an unreviewed change in production
- [ ] B: Terraform configuration cannot be edited once a resource has drifted, so reconciliation is the only technically possible option
- [ ] C: Reverting the rule would have caused the RDS instance itself to be destroyed
- [ ] D: The rule was already present in the module's configuration before the manual change, so no action was actually needed

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The deliberate choice matters here — a genuinely needed fix should become a reviewed, declared part of the configuration rather than being silently reverted or left as undocumented drift.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [drift-reconciliation, deliberate-choice]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why per-environment state reduces blast radius
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend separate state files per environment (dev/prod) rather than one shared state distinguishing environments with `count` or `for_each`?

**OPTIONS:**
- [x] A: A mistaken `apply` against the wrong state file is a small, contained mistake, whereas one shared state file lets an error touch every environment at once — the same blast-radius reasoning as scoping an IAM policy to a specific resource ARN
- [ ] B: Terraform technically forbids using `count` or `for_each` for environment-based configuration
- [ ] C: Separate state files are required because Terraform cannot manage more than one AWS region from a single state file
- [ ] D: This separation has no bearing on risk; it is purely an organizational preference with no safety benefit

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the same least-reachability, contained-blast-radius reasoning from the AWS Core lesson, reapplied to how Terraform state itself is partitioned.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [per-environment-state, blast-radius]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 10

```yaml
lesson_id: cloud-devops-infrastructure-10-serverless-and-event-driven-cloud-lambda-api-gateway-step-functions
lesson_title: "Serverless & Event-Driven Cloud (Lambda, API Gateway, Step Functions)"
lesson_order: 10

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Explain why Lambda's on-demand execution model makes cold starts a first-class concern, and when that trade-off genuinely pays off."
  - "Design a Step Functions state machine using Retry and Catch fields instead of hand-rolled application-level retry logic."
  - "Choose deliberately between serverless and a continuously-running container by naming the specific constraint (throughput, hardware, or execution shape) that decides it."

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
# Serverless & Event-Driven Cloud (Lambda, API Gateway, Step Functions)

## Concepts Covered

Lambda's execution model inverts the always-running assumption every container and Kubernetes lesson so far has built on. There is no long-running process to keep healthy, patch, or scale a Deployment's replica count for — AWS provisions an execution environment on demand for an incoming event, runs the handler, and can freeze, reuse, or destroy that environment between invocations. This is why a cold start — the latency cost of provisioning a fresh execution environment, loading the deployment package, and initializing the runtime before the handler runs for the first time — is a first-class concern rather than an edge case: a function receiving infrequent, bursty traffic pays that cost regularly, while one kept warm by steady, frequent traffic mostly reuses already-initialized environments. This isn't a strictly worse trade. A function that runs for milliseconds a few times an hour has genuinely no idle cost at all — billed per invocation and per millisecond of actual execution, not for a Pod sitting `Ready` and consuming node capacity between requests — which is the exact inverse of the GPU inference Deployment from the Kubernetes Networking lesson, provisioned and paid for continuously specifically because its workload needs steady throughput and a multi-second model load that would make paying the cold-start cost on every invocation prohibitively expensive.

API Gateway sits in front of Lambda (or other backends) as the HTTP-facing layer, handling request/response transformation, authentication (via a Lambda authorizer, IAM auth, or a Cognito authorizer), throttling, and request validation before a request ever reaches application code — the same boundary-enforcement role a load balancer plus an application's own middleware plays for the EC2/EKS-hosted order-management service, just fully managed and configured declaratively instead of code deployed and scaled by hand. Step Functions makes multi-step orchestration a first-class, declarative construct instead of application code manually chaining calls with hand-rolled retry logic: a state machine defines a sequence of states — a Lambda invocation, a wait, a choice branch, a parallel branch — and built-in `Retry` and `Catch` fields on each state express exactly the kind of "retry this specific failure mode up to N times with backoff, then fall through to this specific error-handling state" logic that would otherwise be scattered try/except blocks across a hand-written orchestrator. The state machine's execution history is also a complete, inspectable audit trail of exactly which state ran, with what input and output, at what time — a debugging advantage a custom retry loop buried in application logs doesn't give for free. Step Functions also distinguishes Standard workflows (durable, up to a year of execution, exactly-once state transitions, billed per state transition — the right choice for a multi-step business process like order fulfillment) from Express workflows (higher-throughput, shorter-lived, at-least-once semantics, billed per invocation and duration — the right choice for a high-volume, short-lived event-processing pipeline), and picking between them is the same "match the mechanism to what the workload actually needs" judgment as choosing between Lambda and a container in the first place, not a default either way.

```json
"ChargePayment": {
  "Type": "Task",
  "Resource": "arn:aws:lambda:us-east-1:...:function:ChargePayment",
  "Retry": [{
    "ErrorEquals": ["Stripe.RateLimitError", "Stripe.APIConnectionError"],
    "IntervalSeconds": 2,
    "MaxAttempts": 3,
    "BackoffRate": 2.0
  }],
  "Catch": [{
    "ErrorEquals": ["Stripe.CardError"],
    "Next": "NotifyFailure"
  }],
  "Next": "SendNotification"
}
```

The actual trade-off worth stating precisely, echoing the "match complexity to genuine need" theme from the agent-vs-workflow and event-driven-architecture lessons: serverless wins decisively when traffic is genuinely spiky or infrequent — a Lambda triggered by an S3 upload event, or the SQS-triggered notification handler from the Compute, Storage & Managed Services lesson, both run for milliseconds occasionally and would waste a container's continuous compute cost sitting idle most of the time — when the operational simplicity of "no cluster, no node group, no patching" is worth more than fine-grained control, and when a workload's execution comfortably fits Lambda's per-invocation time limit. It loses when a workload needs steady, high, predictable throughput where a warm container avoids paying repeated cold-start cost, when it needs specialized hardware Lambda doesn't expose (GPU access, for instance — the inference workload from the Kubernetes Networking lesson cannot run as a Lambda function at all), or when a workload's natural shape is a long-running connection, echoing the WebSockets-vs-SSE lesson's own "match the mechanism to what the interaction actually needs" argument, rather than a short, stateless request/response cycle. An FDE choosing between the two isn't picking the more modern option — it's naming which of these genuine constraints applies to the specific workload in front of them.

## Practical Backend Scenario

The order-fulfillment workflow — validate order, charge payment, send notification — gets rebuilt as a Step Functions state machine. A `ValidateOrder` Lambda state runs first, followed by a `ChargePayment` Lambda state whose `Retry` field is configured for the specific transient Stripe error codes from the Module 2 payments lesson, not a blanket retry-everything policy, and whose `Catch` field routes a permanently-declined charge to a distinct `NotifyFailure` state instead of retrying something that will never succeed. A final `SendNotification` Lambda state publishes to the same SQS-backed notification pattern from the Compute, Storage & Managed Services lesson. This entire workflow runs a few thousand times a day, each execution completing in under two seconds — exactly the spiky, short-lived, infrequent-relative-to-continuous-capacity shape that makes Lambda and Step Functions the right choice here, in direct contrast to the GPU inference Deployment from the Kubernetes Networking lesson, which stays provisioned continuously because its workload — steady request volume, multi-second model warm-up, GPU hardware Lambda can't provide — fails every one of the conditions that made serverless the right call for this workflow.

## Practice Loop

1. Define the order-fulfillment state machine's states (Validate, ChargePayment, Notify) and, for each Lambda state, decide whether it sits on the cold-start-sensitive critical path or is tolerant of occasional cold-start latency.
2. Configure the `ChargePayment` state's `Retry` field to match only the specific transient Stripe error codes worth retrying, and its `Catch` field to route a permanent decline to a distinct failure-handling state.
3. Diagnostic: trigger a permanently-declined charge through the state machine and read its execution history — confirm it shows exactly which state ran, in what order, with what input/output, without needing to search application logs for it.
4. Write a one-paragraph comparison naming, specifically, why the GPU inference Deployment from the Kubernetes Networking lesson could not be rebuilt as a Lambda function, citing the exact constraint (hardware, warm-up time, or throughput shape) that rules it out.
5. Estimate the idle-compute cost the order-fulfillment workflow would have paid if built as an always-running container instead, given its actual invocation volume and per-execution duration.

## Evidence of Understanding

You can explain why Lambda's on-demand execution model makes cold starts a first-class concern, and why that trade-off genuinely pays off for spiky or infrequent workloads rather than being a universal downside. You can design a Step Functions state machine using `Retry` and `Catch` fields scoped to specific failure modes rather than a blanket retry-everything policy, and explain the debugging advantage its execution history provides over application-log-based tracing. You can choose deliberately between serverless and a continuously-running container for a specific workload by naming the exact constraint — throughput, hardware, or execution shape — that decides it, rather than defaulting to whichever is more familiar.

## Suggested Extension

Add an API Gateway-fronted Lambda authorizer that validates a customer's API key against a value stored in Secrets Manager (from the AWS Security lesson) before any request reaches the `ValidateOrder` state, and explain why putting that check at the API Gateway layer is preferable to checking it inside the first Lambda state itself.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why cold starts are a first-class concern
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson describe cold starts as a first-class concern rather than an edge case for Lambda?

**OPTIONS:**
- [x] A: Because execution environments are provisioned on demand and can be frozen, reused, or destroyed between invocations, a function receiving infrequent or bursty traffic regularly pays the full provisioning-and-initialization cost rather than reusing an already-warm environment
- [ ] B: Cold starts only occur once per AWS account, on the very first Lambda invocation ever made
- [ ] C: Cold starts are exclusively a concern for functions triggered by API Gateway, never for event-triggered functions
- [ ] D: AWS Lambda does not actually experience cold starts under any circumstances as of current runtime versions

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The on-demand provisioning model is exactly what makes cold starts recur for bursty or infrequent traffic — it's a direct structural consequence of the execution model, not an occasional glitch.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [cold-start, lambda-execution-model]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why Lambda's cost model can be a genuine win
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson call Lambda's per-invocation billing model the "exact inverse" of the GPU inference Deployment's cost profile?

**OPTIONS:**
- [x] A: A function invoked briefly and infrequently has genuinely no idle cost, billed only for actual execution time, whereas the GPU Deployment is provisioned and paid for continuously regardless of whether it's actively serving a request
- [ ] B: Lambda functions are always cheaper than any container-based deployment under every workload pattern
- [ ] C: GPU Deployments are billed per invocation in the same way Lambda functions are
- [ ] D: This comparison only applies to functions triggered directly by API Gateway

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The two cost models are genuinely opposite — pay-per-millisecond-of-actual-work versus pay-for-continuous-provisioned-capacity — which is exactly why matching the model to the workload's actual traffic shape matters.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [serverless-cost-model, idle-cost-comparison]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What API Gateway handles before a request reaches Lambda
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what role does API Gateway play before a request ever reaches the Lambda handler?

**OPTIONS:**
- [x] A: Request/response transformation, authentication, throttling, and request validation — the same boundary-enforcement role a load balancer plus application middleware plays for a container-hosted service, but fully managed
- [ ] B: API Gateway executes the actual business logic itself, with Lambda only used for logging
- [ ] C: API Gateway is required only for Lambda functions triggered by SQS, not by direct HTTP requests
- [ ] D: API Gateway has no authentication capability and must always be paired with a separate authentication service

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
API Gateway's boundary role directly parallels what a load balancer and middleware already do for container-hosted services — just managed and configured declaratively.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [api-gateway-role, boundary-enforcement]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What Step Functions Retry/Catch replace
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson say a Step Functions state's `Retry` and `Catch` fields replace, compared to a hand-written orchestrator?

**OPTIONS:**
- [x] A: Scattered try/except blocks implementing retry-with-backoff and error-routing logic manually across application code — expressed instead as a declarative, per-state configuration
- [ ] B: The need for any Lambda function to handle errors internally at all
- [ ] C: API Gateway's own throttling configuration
- [ ] D: The entire need for a database to store workflow state

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the concrete win Step Functions offers — declarative, per-state retry/error-routing configuration instead of the same logic hand-written and scattered across application code.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [step-functions-retry-catch, declarative-orchestration]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the ChargePayment retry is scoped to specific errors
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the scenario's `ChargePayment` state retry only specific transient Stripe error codes rather than retrying on any failure?

**OPTIONS:**
- [x] A: A permanently-declined charge (a card error) will never succeed no matter how many times it's retried — retrying only transient errors and routing permanent declines to a distinct failure state avoids wasted retries on an outcome that can't change
- [ ] B: Step Functions technically only supports retrying a single named error type per state
- [ ] C: Stripe's API rejects any request that includes retry logic of any kind
- [ ] D: Retrying on any failure would exceed Step Functions' maximum state machine size limit

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The distinction matters because a permanent failure retried repeatedly wastes time and obscures the real outcome — routing it to `Catch` instead reflects that no retry will change a card decline.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scoped-retry, permanent-vs-transient-failure]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the inference Deployment can't become a Lambda function
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Which specific constraint does the lesson name as ruling out rebuilding the GPU inference Deployment as a Lambda function?

**OPTIONS:**
- [x] A: GPU hardware access — Lambda does not expose GPU hardware at all, independent of the workload's throughput or warm-up characteristics
- [ ] B: Lambda functions cannot make outbound network calls to any AWS service
- [ ] C: Lambda has no way to process any request that originates from a Kubernetes cluster
- [ ] D: Lambda functions are limited to a maximum of one invocation per second

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The hardware constraint is absolute — Lambda doesn't expose GPU access at all, which alone rules it out regardless of the other throughput and warm-up considerations also mentioned.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [serverless-vs-gpu-constraint, hardware-limitation]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What the execution-history audit trail provides
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the practice loop, why can the FDE confirm exactly which state ran, with what input/output, without searching application logs?

**OPTIONS:**
- [x] A: Step Functions maintains a complete, inspectable execution history for each run — a debugging advantage a hand-written orchestrator's scattered application logs don't provide for free
- [ ] B: Application logs are technically disabled for any Lambda function invoked through Step Functions
- [ ] C: This is only possible if CloudTrail data events were separately enabled for the state machine
- [ ] D: Step Functions requires a third-party logging tool to produce any execution record at all

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The execution history is a built-in feature of Step Functions itself, giving a structured record of every state transition without needing separate log correlation.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [execution-history, step-functions-observability]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Matching complexity to genuine need
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does the lesson's serverless-versus-container framing connect to the "match complexity to genuine need" theme from the agent-vs-workflow and WebSockets-vs-SSE lessons?

**OPTIONS:**
- [x] A: In every case, the right choice is decided by naming the specific constraint the workload actually has — throughput shape, hardware need, or connection lifetime — not by defaulting to whichever option is more modern or more familiar
- [ ] B: These lessons share no meaningful connection; the comparison is coincidental
- [ ] C: This theme only applies to choices between two different AI agent architectures, not infrastructure choices
- [ ] D: The "match complexity to genuine need" theme argues that the newer technology should always be preferred by default

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a deliberate cross-module echo — the same discipline of naming the actual constraint before choosing a mechanism reappears here applied to compute, not agent design or real-time transport.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [match-complexity-to-need, cross-lesson-theme]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why the notification handler fits the serverless case
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson cite the SQS-triggered notification handler from the earlier Compute, Storage & Managed Services lesson as a good serverless fit?

**OPTIONS:**
- [x] A: It runs for milliseconds only occasionally, and running it as an always-on container would waste continuous compute cost sitting idle most of the time — exactly the spiky, infrequent traffic pattern serverless is suited for
- [ ] B: SQS-triggered functions are required by AWS to run as Lambda functions and cannot be implemented any other way
- [ ] C: The notification handler needs GPU access, making it unsuitable for a container deployment
- [ ] D: This workload requires a long-running, stateful connection, which only Lambda can provide

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The notification handler's traffic shape — brief, infrequent invocations — is exactly the pattern where Lambda's per-invocation billing avoids paying for idle capacity a container would otherwise sit on.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [serverless-fit, sqs-notification-handler]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 11

```yaml
lesson_id: cloud-devops-infrastructure-11-sre-and-reliability-engineering-for-fdes
lesson_title: "SRE & Reliability Engineering for FDEs"
lesson_order: 11

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Define a concrete SLI/SLO and compute the resulting error budget in real units from actual traffic volume."
  - "Use an error budget policy as a release gate, and explain why a spent budget freezes releases rather than merely triggering a dashboard alert."
  - "Diagnose an incident using distributed traces and query-plan evidence, and write a blameless postmortem that targets the process gap, not an individual."

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
# SRE & Reliability Engineering for FDEs

## Concepts Covered

An SLI (service level indicator) is a specific, measured signal of user-experienced behavior — request latency at some percentile, the proportion of requests returning a non-5xx status, a queue's processing lag — pulled from the same OpenTelemetry traces and metrics the Module 2 observability lesson instrumented, not a separate measurement system built on top. An SLO (service level objective) commits to a target on that SLI over a defined window — 99.9% of order-management API requests complete successfully within 300ms over a rolling 28 days — and an error budget is simply one minus the SLO, expressed as a concrete, spendable quantity: a 99.9% SLO against a million requests in that window is a budget of 1,000 failed or slow requests, not zero. Naming this as a budget rather than a target is the substantive move — a target that's never allowed to be missed forces every release to be treated as equally risky, while a budget that's tracked and spent deliberately turns "how much risk can we take on this release" into a concrete number instead of a vague feeling, the same falsifiable-bar discipline the FDE Foundations module's problem-discovery lesson established for defining "done" before starting.

The error budget's actual operational use is as a release gate, not a dashboard metric. An error budget policy states explicitly what happens when the budget is exhausted for its window — freeze non-critical releases, redirect the team's attention from features to reliability work — and what happens when it isn't: ship normally, and treat the unspent budget as room to take on genuine risk, like the canary rollout from the CI/CD lesson. This makes the SLO a shared, legible contract between engineering and whoever cares about velocity, rather than reliability work competing against feature work as an unstated, perpetually-deprioritized concern. An FDE walking into a customer engagement without an agreed SLO is walking into exactly that unstated conflict, where "is this incident bad enough to stop and fix, or an acceptable cost of shipping fast" gets re-litigated informally every time instead of being answered by a budget both sides already agreed to in advance.

```
error_budget = (1 - SLO_target) * total_requests_in_window
burn_rate    = actual_error_rate / (1 - SLO_target)
# burn_rate > 1 means the budget is being consumed faster
# than the window can sustain — this is what triggers an alert
```

Incident diagnosis under this framework follows the same evidence-first discipline as the debugging-AI and Postgres-internals lessons, applied at the systems level. A burn-rate alert — the error budget being consumed faster than the window would sustain, not merely "an error happened" — is the trigger, and the investigation starts from the same distributed traces Module 2 instrumented: which service, which downstream call, and specifically whether the pattern matches a known failure mode, such as a slow query plan regression the Postgres-internals lesson would have you check via `EXPLAIN ANALYZE` before assuming the database itself is generically "slow." A blameless postmortem — documenting what happened, what the contributing factors were, and what changes would have caught or prevented it, explicitly not who made the mistake — exists because the goal is a system that fails this way less often, not a person who's more careful next time; punishing the engineer who deployed the change that triggered the incident teaches everyone else to hide near-misses instead of surfacing them, which is a worse long-term reliability outcome than the original incident. Toil — manual, repetitive operational work that doesn't durably improve the system, like restarting a stuck Pod by hand every few days instead of fixing why it gets stuck — is worth naming specifically because an SRE practice that spends all its error-budget-earned slack on toil instead of on the automation or architectural fix that would eliminate it never actually converts a healthy error budget into less operational burden over time. Incident severity levels matter for the same reason a burn-rate threshold does — they set, in advance, roughly how fast a given class of incident needs a response (a full outage paging someone immediately versus a minor, budget-tolerable degradation that can wait for business hours), so the decision of "how urgently does this need attention" is answered by a pre-agreed severity definition rather than argued fresh, under pressure, during the incident itself.

## Practical Backend Scenario

The order-management API has an agreed SLO: 99.9% of requests succeed within 300ms over a rolling 28-day window, measured from the OTel traces instrumented in Module 2. A burn-rate alert fires — the error budget that should last 28 days is on pace to be exhausted in under six hours. The FDE pulls the traces for the affected window and finds the pattern immediately: a specific query against the `orders` table, previously fast, now taking four seconds under load, the same query-plan-regression diagnostic the Postgres-internals lesson walked through with `EXPLAIN ANALYZE`, revealed by a recent migration that dropped an index the query relied on, without anyone noticing because the migration's own test suite didn't run against production-scale data volume. Following the error budget policy, feature releases freeze until the fix — restoring the index — ships and the burn rate returns to normal. The postmortem documents the missing index, the gap in the migration review process that let it through, and a follow-up action item requiring an `EXPLAIN ANALYZE` check against a production-scale dataset for any migration touching a heavily-queried table — with no line in the postmortem naming who wrote the migration, because the fix that actually prevents a recurrence is the process gap, not a warning to one engineer.

## Practice Loop

1. Define a concrete SLI (specific query, specific percentile, specific status-code definition of "successful") for the order-management API using the OTel traces already instrumented in Module 2, and write the SLO target and measurement window explicitly.
2. Calculate the error budget in concrete units — number of allowed failed or slow requests — given the SLO and the API's actual observed request volume over a recent window.
3. Diagnostic: given a specific elevated failure rate, compute how many hours until the 28-day budget would be exhausted at that rate, and confirm it crosses the alerting threshold.
4. Use `EXPLAIN ANALYZE` against the regressed query, per the Postgres-internals lesson, to identify the missing index as the root cause rather than assuming a vaguer "the database is slow" explanation.
5. Write the blameless postmortem's contributing-factors and follow-up-action sections, and confirm neither section names an individual engineer as the cause.

## Evidence of Understanding

You can define a concrete SLI and SLO from real traces, and compute the resulting error budget in actual units rather than as an abstract percentage. You can explain why an error budget policy functions as a release gate rather than a dashboard metric, and why a spent budget freezing releases resolves the otherwise unstated conflict between reliability and velocity. You can diagnose an incident using distributed traces and query-plan evidence rather than guessing, and write a blameless postmortem whose follow-up action targets the process gap that let the failure through, not the individual engineer who happened to trigger it.

## Suggested Extension

Define a second SLO for the SQS-based notification pipeline from the Compute, Storage & Managed Services lesson — for example, 99% of notifications delivered within five minutes of the triggering event — and explain why this SLO needs a different SLI (queue lag, not request latency) than the order-management API's SLO.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** SLI versus SLO
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the difference between an SLI and an SLO, per the lesson?

**OPTIONS:**
- [x] A: An SLI is a specific, measured signal of user-experienced behavior; an SLO commits to a target on that measured signal over a defined window
- [ ] B: An SLI and an SLO are two interchangeable names for the same concept
- [ ] C: An SLO is the measured signal, and an SLI is the target committed to over a window
- [ ] D: SLIs apply only to latency, while SLOs apply only to error rate

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The distinction is foundational to the rest of the lesson — the SLI is what you measure, the SLO is the target you commit to hitting on that measurement.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [sli-vs-slo, definitions]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why "budget" is the substantive framing
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say framing reliability as a "budget" rather than a "target" is the substantive move?

**OPTIONS:**
- [x] A: A target that's never allowed to be missed forces every release to be treated as equally risky, while a budget that's tracked and spent deliberately turns "how much risk can we take" into a concrete, decidable number
- [ ] B: A budget and a target produce identical engineering decisions; the wording difference is purely stylistic
- [ ] C: Budgets apply only to financial cost, not to reliability, making this framing a misnomer
- [ ] D: A budget framing means the SLO can be silently ignored whenever convenient

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The budget framing is what makes risk-taking a deliberate, quantified decision instead of an all-or-nothing target that treats every release as equally dangerous.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [error-budget-framing, falsifiable-bar]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What an error budget policy actually gates
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the lesson say an error budget policy does when the budget is exhausted for its window?

**OPTIONS:**
- [x] A: It explicitly freezes non-critical releases and redirects the team's attention from features to reliability work, rather than merely logging the exhaustion on a dashboard
- [ ] B: It automatically increases the SLO target to make the budget easier to meet going forward
- [ ] C: It has no operational effect; the policy exists purely for reporting purposes
- [ ] D: It permanently disables the affected service until a full infrastructure rebuild

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The policy's teeth are the release freeze — this is what makes the error budget an actual release gate instead of a passive metric nobody acts on.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [error-budget-policy, release-gate]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What an agreed SLO resolves for an FDE
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say an FDE without an agreed SLO on a customer engagement is walking into an unstated conflict?

**OPTIONS:**
- [x] A: Without an agreed budget, "is this incident bad enough to stop and fix, or an acceptable cost of shipping fast" gets informally re-litigated every time, instead of being answered by a number both sides already agreed to
- [ ] B: Customers always refuse to engage with an FDE who has not first defined an SLO
- [ ] C: SLOs are a legal requirement for any AWS-hosted production workload
- [ ] D: Without an SLO, the OTel tracing instrumentation from Module 2 cannot function at all

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
An agreed SLO converts a recurring, informal argument about reliability-versus-velocity into a decision already made in advance by both sides.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [slo-as-contract, fde-engagement]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What a burn-rate alert actually signals
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does a burn-rate alert indicate that a plain "an error occurred" alert does not?

**OPTIONS:**
- [x] A: That the error budget is being consumed faster than the measurement window can sustain — a rate-based signal, not just the fact that a single error happened
- [ ] B: That the error budget has already reached exactly zero
- [ ] C: That the SLO target itself needs to be permanently lowered
- [ ] D: That a specific individual engineer is responsible for the ongoing errors

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Burn rate is a pace signal — it says whether the budget is being spent too fast for the window, which is a meaningfully different and more actionable signal than any single error.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [burn-rate, alert-signal]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the FDE checks EXPLAIN ANALYZE before assuming "the database is slow"
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why does the FDE use `EXPLAIN ANALYZE` on the regressed query rather than assuming the database is generically overloaded?

**OPTIONS:**
- [x] A: It follows the same evidence-first diagnostic discipline as the Postgres-internals lesson — checking the actual query plan reveals the specific missing index causing the regression, rather than guessing at a vague, unfalsifiable cause
- [ ] B: EXPLAIN ANALYZE is required by AWS before any RDS query can be executed in production
- [ ] C: This step is unnecessary in the scenario; the FDE could have found the same answer faster by restarting the RDS instance
- [ ] D: EXPLAIN ANALYZE only works for queries that already have an existing index

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a direct reuse of the Postgres-internals lesson's diagnostic discipline — evidence from the actual query plan, not an assumption about the database being generally slow.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [explain-analyze, evidence-first-diagnosis]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the postmortem doesn't name the engineer
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist the postmortem's follow-up action targets the migration review process gap, not the engineer who wrote the migration?

**OPTIONS:**
- [x] A: Punishing the individual who triggered the incident teaches everyone else to hide near-misses instead of surfacing them, which produces a worse long-term reliability outcome than the original incident — the fix that actually prevents recurrence is closing the process gap
- [ ] B: The engineer who wrote the migration was not actually responsible for the missing index in any way
- [ ] C: Blameless postmortems are a purely legal requirement with no bearing on future incident rates
- [ ] D: Naming an individual in a postmortem is technically prohibited by every major cloud provider's terms of service

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The blameless framing is a deliberate choice about what actually reduces future incidents — a culture that surfaces near-misses openly catches more problems than one that punishes whoever happened to trigger the last one.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [blameless-postmortem, process-gap-focus]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why toil undermines a healthy error budget
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson single out toil (like manually restarting a stuck Pod repeatedly) as a specific risk to an SRE practice, even when the error budget is currently healthy?

**OPTIONS:**
- [x] A: If the slack a healthy error budget provides gets spent on repetitive manual work instead of the automation or architectural fix that would eliminate the underlying problem, the operational burden never actually decreases over time
- [ ] B: Toil is defined as any work performed by an on-call engineer, regardless of whether it's repetitive or one-time
- [ ] C: A healthy error budget automatically eliminates the need to address toil at all
- [ ] D: Toil only becomes a concern once the error budget has already been fully exhausted

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The point is about converting slack into durable improvement — spending it on repeated manual fixes instead of the actual fix means the burden never actually goes down.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [toil, durable-reliability-improvement]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why the notification pipeline needs a different SLI
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the suggested extension say the SQS-based notification pipeline's SLO needs a different SLI (queue lag) than the order-management API's SLO (request latency)?

**OPTIONS:**
- [x] A: The notification pipeline's user-experienced behavior is how long a message waits before being delivered, not how fast a single synchronous request completes — the SLI has to measure what the workload actually does, not be copied from an unrelated workload's SLI
- [ ] B: Queue-based systems are technically incapable of having any SLO defined for them
- [ ] C: Request latency and queue lag are actually the same measurement expressed in different units
- [ ] D: The notification pipeline cannot be measured using the OTel instrumentation from Module 2

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
An SLI has to reflect what the specific workload's users actually experience — copying an unrelated workload's SLI onto a queue-based pipeline would measure the wrong thing entirely.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [sli-selection, queue-lag-vs-latency]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 12

```yaml
lesson_id: cloud-devops-infrastructure-12-assessment-deploy-break-fix-on-cloud
lesson_title: "Assessment: Deploy, Break, Fix on Cloud"
lesson_order: 12

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: cloud-devops-infrastructure
module_name: "Cloud, DevOps, Kubernetes & Infrastructure"
module_order: 4

difficulty: Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Integrate IAM/VPC design, managed services, secrets management, containerization, Kubernetes, GitOps, Terraform, serverless judgment, and SRE discipline into one deployed, observable system."
  - "Diagnose an injected production failure using only observable evidence (traces, kubectl events, CloudTrail, ArgoCD sync status), not a hint about what's broken."
  - "Self-assess a cloud deployment against an explicit rubric, and write a blameless postmortem for the diagnosed failure."

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
# Assessment: Deploy, Break, Fix on Cloud

## Concepts Covered

This assessment is a self-check, not a new mechanism — its purpose is confirming that Module 4's twelve lessons (IAM/VPC design, managed AWS services, secrets management, Docker, Kubernetes, EKS/Helm, NetworkPolicy/RBAC/GPU scheduling, GitOps, Terraform, serverless judgment, and SRE discipline) compose into one deployed, observable, diagnosable system, the way they'd actually need to on a real engagement rather than in twelve separate isolated exercises. A rubric-driven self-assessment, evaluated against explicit, checkable criteria rather than a vague "does this feel done," mirrors the discipline the FDE Foundations module's problem-discovery lesson established: a falsifiable bar defined before you call something finished, not a retroactively-adjusted sense of completion.

**The challenge brief:** deploy the order-management system built across this module into a sandbox AWS account, then diagnose and fix one injected failure without being told what's broken. Specifically: (1) infrastructure — VPC, subnets, security groups, RDS, and the EKS cluster — is provisioned via Terraform modules with remote state and locking, not console clicks; (2) IAM roles for every workload follow least privilege, scoped to the exact actions and resources each one needs; (3) the Stripe webhook secret and the RDS credential are stored in Secrets Manager, encrypted under a customer-managed KMS key, never hardcoded; (4) the order-management service is containerized, deployed to EKS behind a NetworkPolicy default-deny layout with explicit allow rules, and its ServiceAccount's RBAC is scoped to only what it needs; (5) deployment happens through the GitHub Actions + ArgoCD GitOps pipeline — no manual `kubectl apply` to production; (6) an SLO is defined for the order-management API's availability and latency, measured from the OTel traces already instrumented in Module 2; (7) once deployed, a specific failure is injected into the environment (by whoever is administering the assessment, or by a peer) without telling you what it is — your job is to find it using only observable evidence.

**The rubric**, in order of weight: **Infrastructure correctness** — is the VPC/security-group layout genuinely least-reachability, is IAM scoped per-workload rather than shared broadly, does `terraform plan` against the finished state show zero unexpected drift. **Deployment & GitOps discipline** — did every change reach the cluster through the GitHub Actions + ArgoCD pipeline, with a Git commit for every production change, or did a manual `kubectl apply` bypass it at any point. **Security posture** — are secrets in Secrets Manager and never hardcoded, is the NetworkPolicy default-deny with narrow explicit allows, is RBAC scoped to least privilege. **Incident diagnosis** — was the injected failure root-caused using actual observable evidence (traces, `kubectl describe` events, CloudTrail, ArgoCD sync status) rather than guessed at or fixed by trial and error, and is the fix documented as a blameless postmortem naming the process gap, not just a note that "it's fixed now."

## Practical Backend Scenario

This assessment doesn't need a separate scenario — it *is* the scenario, deliberately built to be completable in a few sessions but real enough that skipping any single rubric item (provisioning infra by hand instead of through Terraform, hardcoding a secret instead of using Secrets Manager, deploying via a manual `kubectl apply` instead of the GitOps pipeline) produces a noticeably worse, less defensible result rather than a merely less polished one. That gap between "technically works" and "actually meets the rubric" is deliberate: it's the same gap between a demo that happens to run once and a system that's genuinely provisioned declaratively, secured by design, deployed auditable, and diagnosable under failure — the standard this module has built toward lesson by lesson.

## Practice Loop

1. Provision the full infrastructure (VPC, RDS, EKS) using the Terraform modules from the Terraform lesson, with remote state and locking configured before the first `apply`.
2. Deploy the order-management service through the GitHub Actions + ArgoCD pipeline from the CI/CD lesson — confirm the manifests repo's commit history accounts for every change that reached the cluster.
3. Once the environment is stable, have the injected failure introduced without being told what it is, and diagnose it using only observable evidence — traces, `kubectl describe` events, CloudTrail, or ArgoCD sync status — writing down each piece of evidence you check and what it ruled in or out, before you touch anything.
4. Fix the diagnosed failure at the correct layer — a Terraform change for infrastructure drift, a Kubernetes manifest change for a NetworkPolicy or RBAC gap, a Secrets Manager change for an exposed credential — committed through the GitOps pipeline, not a one-off manual patch.
5. Self-score the finished deployment against all four rubric categories, and write the blameless postmortem for the injected failure, naming the process gap that would prevent a recurrence rather than the specific action that caused it.

## Evidence of Understanding

You can provision, secure, and deploy a real multi-component cloud system using the module's full toolset — Terraform, IAM, Secrets Manager, Kubernetes networking and RBAC, and a GitOps pipeline — composed into one coherent deployment, not twelve disconnected exercises. You can diagnose an unannounced production failure using only observable evidence, distinguishing a genuinely evidence-based root cause from a guess that happened to fix the symptom. You can evaluate your own deployment against an explicit rubric and identify specifically which category is weakest, and you can write a blameless postmortem whose follow-up action targets a process gap rather than a specific person or a one-off patch.

## Suggested Extension

Define the SLO's error budget policy explicitly (what freezes and what doesn't when the budget is exhausted), and have a peer inject a second, different failure a week later — compare how much faster the diagnosis goes using the observability and GitOps audit trail already in place versus the first time, and write down specifically what made the difference.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Purpose of this assessment
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the actual purpose of this assessment, according to the lesson?

**OPTIONS:**
- [x] A: Confirming that Module 4's individual tools (infrastructure-as-code, secrets management, Kubernetes networking/RBAC, GitOps, SRE discipline) compose into one deployed, diagnosable system — not testing any single new mechanism
- [ ] B: Teaching an entirely new cloud provider not covered elsewhere in the module
- [ ] C: Testing typing speed under a strict time limit
- [ ] D: Determining whether the learner should use Kubernetes or a different orchestrator going forward

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This assessment is explicitly a composition check, not new content — its value is proving the module's separate lessons actually integrate, a distinct skill from executing each one in isolation.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [assessment-purpose, integration]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why infrastructure must be provisioned via Terraform, not console clicks
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the challenge brief, why does the rubric's "infrastructure correctness" category specifically check that `terraform plan` shows zero unexpected drift?

**OPTIONS:**
- [x] A: It's a concrete, checkable way to confirm the infrastructure was actually provisioned declaratively through Terraform rather than by hand — any manual console change would surface as drift in the plan output
- [ ] B: Terraform plan output has no relationship to whether infrastructure was provisioned by console clicks or by Terraform itself
- [ ] C: This check only matters for the RDS instance, not for the VPC or EKS cluster
- [ ] D: Zero drift is impossible to achieve in practice, so this criterion is intentionally unattainable

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
A clean `terraform plan` is a direct, verifiable signal that the declared configuration and the real infrastructure agree — exactly the kind of falsifiable check the rubric is built around.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (rubric)
**KEYWORDS:** [terraform-drift-check, verifiable-rubric]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What "GitOps discipline" checks for
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the rubric's "deployment & GitOps discipline" category evaluate?

**OPTIONS:**
- [x] A: Whether every change that reached the cluster traces back to a Git commit in the manifests repo, or whether a manual `kubectl apply` bypassed the pipeline at any point
- [ ] B: How many total files exist in the application repository
- [ ] C: Whether the Docker image was built using a specific base image tag
- [ ] D: Whether the cluster is running on EKS specifically rather than another Kubernetes distribution

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This directly reuses the CI/CD lesson's core claim — a bypassed pipeline (a manual `kubectl apply`) breaks the audit-trail guarantee GitOps is meant to provide, which is exactly what this rubric category checks for.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (rubric)
**KEYWORDS:** [gitops-discipline, audit-trail-check]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why diagnosis must precede fixing
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does Practice Loop step 3 have you write down each piece of evidence checked and what it ruled in or out, before touching anything?

**OPTIONS:**
- [x] A: It forces a genuinely evidence-based root cause instead of a guess that happens to fix the symptom — the rubric explicitly distinguishes the two, and an undocumented fix can't demonstrate which one actually happened
- [ ] B: This step exists purely to slow down the assessment and has no diagnostic value
- [ ] C: Kubernetes technically requires a written diagnosis log before any manifest can be edited
- [ ] D: Writing evidence down before fixing anything is only necessary when the failure involves NetworkPolicy specifically

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This directly enforces the "incident diagnosis" rubric category — the value is in demonstrating the reasoning that led to the fix, not just the fact that the symptom eventually disappeared.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [evidence-based-diagnosis, rubric-verification]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Fixing at the correct layer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does Practice Loop step 4 specify fixing infrastructure drift via Terraform and a NetworkPolicy or RBAC gap via a Kubernetes manifest change, rather than any fix that happens to work?

**OPTIONS:**
- [x] A: A fix applied at the wrong layer (a manual console edit for infrastructure, a one-off `kubectl` patch for a manifest gap) reintroduces exactly the kind of undeclared drift or bypassed-pipeline problem the rubric's other categories are checking for
- [ ] B: Terraform and Kubernetes manifests are interchangeable, so the specific layer named makes no real difference
- [ ] C: This requirement only applies to failures injected into the RDS instance specifically
- [ ] D: A one-off manual patch is always faster and therefore always preferable to a declared fix

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Fixing at the correct declared layer keeps the fix consistent with the infrastructure-correctness and GitOps-discipline rubric categories — a fix that bypasses them just reintroduces the problem those categories exist to catch.

**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [fix-at-correct-layer, declared-infrastructure]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the postmortem targets a process gap
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the final rubric category require the postmortem's follow-up action to name a process gap rather than the specific action that caused the injected failure?

**OPTIONS:**
- [x] A: This reuses the SRE lesson's blameless-postmortem discipline — naming the process gap targets what would actually prevent a recurrence, while naming the specific triggering action produces a fix that only prevents that one exact failure from happening the same way again
- [ ] B: The specific triggering action is always impossible to identify in an injected-failure exercise
- [ ] C: Process gaps and triggering actions are the same thing described in different words
- [ ] D: This requirement only applies if the injected failure involved a Terraform-managed resource

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is a direct reuse of the SRE lesson's postmortem framing — a process-gap fix generalizes to prevent a class of failure, while naming only the specific action produces a much narrower, less durable fix.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (rubric)
**KEYWORDS:** [blameless-postmortem-reuse, process-gap-focus]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why skipping a rubric item is functionally worse, not just less polished
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that skipping a rubric item — for example, hardcoding a secret instead of using Secrets Manager — produces a "noticeably worse, less defensible" result rather than merely a less polished one?

**OPTIONS:**
- [x] A: Each rubric item corresponds to a real capability the deployment loses without it — skipping Secrets Manager means losing rotation, access-controlled retrieval, and CloudTrail-visible access auditing, a functional loss, not a cosmetic one
- [ ] B: The rubric items are arbitrary stylistic preferences with no functional consequence
- [ ] C: Hardcoding a secret and using Secrets Manager produce functionally identical security outcomes
- [ ] D: This concern only applies to secrets that are rotated automatically

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The rubric items were chosen because each maps to a real, demonstrated capability from earlier lessons in the module — skipping one is a functional loss of that capability, not a stylistic shortfall.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [rubric-item-consequence, functional-vs-cosmetic]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Value of a second, later injected failure
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the suggested extension recommend having a peer inject a second, different failure a week later and comparing diagnosis speed against the first time?

**OPTIONS:**
- [x] A: It tests whether the observability and GitOps audit trail already in place genuinely made diagnosis faster and more evidence-based the second time, rather than the first success being a one-off — a concrete, comparable measurement instead of a subjective impression
- [ ] B: A second injected failure is required because the first one cannot actually be fixed
- [ ] C: This comparison has no diagnostic value; it exists only to extend the assessment's total time
- [ ] D: The second failure is guaranteed to be identical to the first, making the comparison trivial

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Comparing diagnosis speed across two genuinely separate incidents is a concrete way to check whether the observability and audit-trail investments actually paid off, not just whether the first fix happened to go smoothly.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [repeat-incident-comparison, observability-payoff]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

