# FDE Phase 25 — Elective: AWS Multi-Region Cloud Deep Dive (Lessons 13-17 of 17, COMPLETES THE MODULE)

Five lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-25-elective-aws-multi-region-cloud-deep-dive-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `elective-aws-multi-region-cloud-deep-dive` ("AWS Multi-Region
Cloud Deep Dive") — a `SupplementalModuleDefinition`, the second of three elective modules now in
scope. This phase is applied third and last in this module's own sub-sequence, after Phase 23
(lessons 1-6) and Phase 24 (lessons 7-12). **This phase completes the module at 17/17 lessons** —
the second of the three elective modules to reach 100%, after Containerization/K8s (Phases 20-22).
Only "Storage, Networking & Reliability for FDEs" (Phases 26-27) will remain unauthored after this
lands.

This file covers **lessons 13-17 of 17 only**: Microservices on AWS Project, Microservices
Project: Phase 2, AWS Security: Identity and Network, AWS Security: Data and Detection, and AWS
Security Hands-on. Do not add placeholder content for lessons 1-12 — those were authored in Phases
23 and 24.

**Scenario continuity with Phase 23:** all five lessons continue the established FDE engagement for
**Lighthouse Freight Co.**, the same customer whose primary deliverable, **ManifestFlow**
(customs-manifest ingestion, running in the VPC built in Phase 23 Lesson 1, with the networking,
observability, and EC2/Lambda mechanics from Phase 23 Lessons 2-6), is assumed as prior context.
Lessons 13-14 introduce a second, purpose-built multi-service system on the same AWS account and
VPC family — **DispatchWorks**, a freight-booking and carrier-settlement platform — because the
skeleton's own scenario ("order, payment, and notification capabilities released by different
teams") does not fit ManifestFlow's single-pipeline shape and a believable multi-service project
needs genuinely separable ownership boundaries. DispatchWorks reuses ManifestFlow's account
(`111122223333`), region (`us-east-1`), and private-subnet layout, and is presented as the next
FDE deliverable for the same customer, deployed on ECS Fargate — the managed container platform
Lighthouse adopted in the (not-yet-authored-in-this-repo-snapshot) ECS/EKS lessons that occupy this
module's lessons 9-10. Lessons 15-17 return to securing the AWS foundation itself — both
ManifestFlow and DispatchWorks are used as the concrete subjects of the IAM, network, data, and
detection review.

**Overlap-avoidance note (checked against Module 7, `application-security-reliability`, Phase 16 —
required reading per this phase's task brief):** Phase 16's Module 7 lessons already cover
enterprise compliance and secrets management at an architectural level — SOC2 control mapping
(CC6.1/CC7.2), cross-account KMS grants for BYOK, deployment topology selection (shared vs.
single-tenant vs. customer VPC), and CloudTrail-based incident timelines for a security-group
change. This phase's lessons 15-17 deliberately do not re-teach any of that. Lesson 15 goes one
level more AWS-mechanism-specific than Phase 16 ever does: actual overly-broad-vs-scoped IAM policy
JSON, trust policies, permission boundaries, and VPC endpoint wiring, not the BYOK/cross-account
grant mechanism Phase 16 Lesson 8 already owns. Lesson 16 covers KMS and CloudTrail data events
too, but from the angle of S3/RDS-specific controls and **GuardDuty findings** — a detection
surface Phase 16 never mentions at all — rather than the cross-account grant mechanics Phase 16
Lesson 8 covers. Lesson 17 is a hands-on synthesis specific to this module's own IAM/network/data/
detection mechanics, distinct from Phase 16 Lesson 12's compliance-brief-and-load-test mock
engagement.

---

# LESSON 13

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-13-microservices-on-aws-project
lesson_title: "Microservices on AWS Project"
lesson_order: 13

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 120
content_status: Draft

learning_outcomes:
  - "Choose a synchronous versus asynchronous service boundary based on whether the caller needs an immediate answer, and implement a hard timeout with a fallback for the synchronous case."
  - "Design per-service data ownership (no shared database across services) and wire an SNS-to-SQS event boundary with a filter policy for one-directional, retryable delivery."
  - "Propagate a correlation ID across both a synchronous call and a published event, and use it to trace one business transaction across three independently deployed services."

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
# Microservices on AWS Project

## Concepts Covered

A service boundary is a decision about ownership, not just a network hop: each service in
DispatchWorks — `booking-service`, `settlement-service`, `notification-service` — owns its own
database schema, and no service ever queries another service's tables directly, even when they run
in the same VPC and the same RDS instance would technically permit it. This "write your own table"
discipline is what lets Lighthouse's three teams release independently, because a schema migration
in `settlement-service` can never break `booking-service` at the database level — only through the
API contract the two services actually agree on, which is a much smaller, more reviewable surface
than "whatever columns happen to exist in the shared table today." Discovery between services
running on ECS Fargate uses **Service Connect**, which registers each service under an internal DNS
name in a private namespace (`booking-service.dispatchworks.internal`) — this is different from
routing every internal call through the public-facing Application Load Balancer, which would mean
internal traffic leaves and re-enters the VPC boundary unnecessarily and depends on the ALB's own
availability for calls that never needed to touch it.

The choice between a synchronous and an asynchronous boundary follows directly from whether the
caller actually needs an answer before it can proceed. `booking-service` calls
`settlement-service`'s `/estimate` endpoint synchronously, with a short connect timeout and a
shorter overall request timeout, because a booking confirmation page needs *some* settlement figure
immediately — but the call carries a fallback: if the timeout fires, the booking still completes
with `estimatedSettlement = PENDING`, rather than failing the entire booking because one downstream
call was slow. Settlement completion, by contrast, is asynchronous: `settlement-service` publishes
a `SETTLEMENT_COMPLETED` event to an SNS topic once the real settlement finishes (independent of
whether the earlier estimate call succeeded, timed out, or was skipped), and `notification-service`
consumes it from its own SQS queue subscribed to that topic — a boundary that tolerates
`notification-service` being briefly unavailable, since SQS holds the message until it is
processed, something a synchronous call could never do. A correlation ID, generated once at
`booking-service`'s edge and propagated as an `X-Correlation-Id` header on the synchronous call and
as a message attribute on the published event, is what lets an engineer reconstruct one booking's
full path across three independently deployed services and two different delivery mechanisms from
CloudWatch Logs alone.

```bash
# Each service is its own ECS Fargate service under Service Connect —
# internal DNS discovery, not a shared load balancer hop for internal traffic.
aws ecs create-service --cluster dispatchworks --service-name booking-service \
  --task-definition booking-service:7 --desired-count 2 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-0priv1,subnet-0priv2],securityGroups=[sg-0booking4a5b],assignPublicIp=DISABLED}" \
  --service-connect-configuration '{
    "enabled": true,
    "namespace": "dispatchworks.internal",
    "services": [{"portName": "http", "discoveryName": "booking-service",
                   "clientAliases": [{"port": 8080, "dnsName": "booking-service.dispatchworks.internal"}]}]
  }'

# settlement-service publishes completion events; notification-service subscribes via its
# own SQS queue with a filter policy so it only receives the event type it cares about.
aws sns create-topic --name settlement-completed
aws sqs create-queue --queue-name notification-inbox
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:111122223333:settlement-completed \
  --protocol sqs --notification-endpoint arn:aws:sqs:us-east-1:111122223333:notification-inbox \
  --attributes '{"FilterPolicy": "{\"eventType\": [\"SETTLEMENT_COMPLETED\"]}"}'
```

```java
// booking-service calling settlement-service SYNCHRONOUSLY for an estimate only.
// A hard timeout plus a fallback keep a slow dependency from blocking the booking itself.
HttpClient settlementClient = HttpClient.newBuilder()
    .connectTimeout(Duration.ofMillis(300))
    .build();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://booking-service.dispatchworks.internal:8080/estimate"))
    .header("X-Correlation-Id", correlationId)
    .timeout(Duration.ofMillis(800))
    .GET().build();
try {
    var response = settlementClient.send(request, HttpResponse.BodyHandlers.ofString());
    booking.setEstimatedSettlement(parseEstimate(response.body()));
} catch (HttpTimeoutException e) {
    booking.setEstimatedSettlement(Estimate.PENDING); // booking proceeds; settlement resolves async
}
```

## Practical Backend Scenario

Lighthouse wants freight bookings, carrier settlement, and dispatcher notifications released by
three separate teams without losing the ability to trace one booking end to end. The FDE builds
`booking-service` with a synchronous, timeout-bounded call to `settlement-service` for a settlement
estimate at booking time, and an asynchronous SNS-to-SQS event from `settlement-service` to
`notification-service` once real settlement completes. To prove the design survives a real failure,
the FDE injects a 3-second artificial delay into `settlement-service`'s `/estimate` handler while
running a load test against `booking-service`: with the 800ms timeout and `PENDING` fallback in
place, every booking still completes successfully, just with a deferred settlement figure, and the
correlation ID on one sampled booking is traced from `booking-service`'s request log, through the
timeout event, to the eventual `SETTLEMENT_COMPLETED` message and `notification-service`'s log
entry — proving the asynchronous path recovers independently of the synchronous one's outcome.

## Practice Loop

1. Build `booking-service` and `settlement-service` as separate ECS Fargate services under Service
   Connect, each with its own database schema, and implement the synchronous `/estimate` call with
   an explicit connect timeout and request timeout.
2. Wire the asynchronous boundary: an SNS topic for `SETTLEMENT_COMPLETED`, an SQS queue for
   `notification-service` subscribed with a filter policy on `eventType`, and a consumer that logs
   the message.
3. Inject an artificial delay into `settlement-service`'s `/estimate` handler that exceeds the
   configured timeout, run a fixed batch of bookings against `booking-service`, and count how many
   bookings completed successfully with `estimatedSettlement = PENDING` versus how many would have
   blocked or failed without the timeout and fallback in place.
4. Generate a correlation ID at `booking-service`'s edge, propagate it through the synchronous call
   header and the published event's message attribute, and trace one specific booking's correlation
   ID across all three services' CloudWatch Logs entries.
5. Review each service's data access code and confirm none of the three services executes a query
   against another service's database schema — flag and fix any direct cross-service table access
   you find.

## Evidence of Understanding

You can justify a synchronous versus asynchronous boundary choice by whether the caller needs an
immediate answer, and you can implement a timeout with a fallback that keeps a slow synchronous
dependency from blocking an otherwise-completable operation. You can wire an SNS-to-SQS event
boundary with a filter policy so a consumer receives only the event types it needs, and you can
propagate a correlation ID across both delivery mechanisms to trace one business transaction
end to end. You can demonstrate, under an injected dependency delay, that the system degrades
gracefully rather than failing outright, and can prove that no service directly queries another
service's database.

## Suggested Extension

Add a fourth service, `carrier-rate-service`, that `settlement-service` calls synchronously for the
actual settlement calculation, and give `settlement-service` a circuit breaker (open after 5
consecutive timeouts, half-open retry after 30 seconds) so a persistently failing `carrier-rate-
service` stops accumulating blocked threads in `settlement-service` rather than retrying every
request against a dependency already known to be down.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Choosing sync vs. async for the settlement estimate
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does `booking-service` call `settlement-service`'s `/estimate` endpoint synchronously rather than publishing an event and waiting for a later response?

**OPTIONS:**
- [x] A: The booking confirmation page needs some settlement figure immediately before it can render, so the caller cannot proceed without a timely answer
- [ ] B: SNS and SQS cannot be used for any interaction involving money
- [ ] C: Synchronous calls are always faster than asynchronous ones regardless of the workload
- [ ] D: ECS Fargate does not support asynchronous messaging between services

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's rule is that the boundary choice follows from whether the caller needs an immediate answer — the confirmation page needs a figure now, which is exactly the synchronous case.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [sync-vs-async, service-boundary, caller-need]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What the timeout-and-fallback code actually does
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```java
try {
    var response = settlementClient.send(request, HttpResponse.BodyHandlers.ofString());
    booking.setEstimatedSettlement(parseEstimate(response.body()));
} catch (HttpTimeoutException e) {
    booking.setEstimatedSettlement(Estimate.PENDING);
}
```

**QUESTION_TEXT:**
When `settlement-service`'s `/estimate` call exceeds its 800ms timeout, what happens to the booking, per this code?

**OPTIONS:**
- [x] A: The booking still completes, with its estimated settlement set to a PENDING placeholder rather than the request failing
- [ ] B: The booking request fails and returns an error to the caller
- [ ] C: The code retries the call indefinitely until it succeeds
- [ ] D: The booking is silently discarded without any record being created

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The `catch` block sets a `PENDING` placeholder rather than propagating the timeout as a failure — the booking proceeds, and the real settlement value resolves later through the asynchronous path.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [timeout-fallback, graceful-degradation, http-timeout]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why the SNS subscription carries a filter policy
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:111122223333:settlement-completed \
  --protocol sqs --notification-endpoint arn:aws:sqs:us-east-1:111122223333:notification-inbox \
  --attributes '{"FilterPolicy": "{\"eventType\": [\"SETTLEMENT_COMPLETED\"]}"}'
```

**QUESTION_TEXT:**
What does the `FilterPolicy` attribute on this subscription accomplish?

**OPTIONS:**
- [x] A: It ensures `notification-inbox` only receives messages whose `eventType` attribute is `SETTLEMENT_COMPLETED`, filtering out any other event types the topic might later carry
- [ ] B: It encrypts the message body before delivery to the queue
- [ ] C: It sets the maximum number of messages the queue can hold at once
- [ ] D: It delays delivery of the message by a fixed number of seconds

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
SNS filter policies let a subscriber receive only messages matching specific attribute values, so `notification-inbox` stays scoped to the one event type it actually needs even if the topic later carries others.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [sns-filter-policy, event-filtering, sqs-subscription]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why Service Connect instead of routing through the public ALB
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does `booking-service` reach `settlement-service` through Service Connect's internal DNS name rather than through the public-facing Application Load Balancer?

**OPTIONS:**
- [x] A: Routing internal traffic through the public ALB would mean it unnecessarily leaves and re-enters the VPC boundary and depends on the ALB's own availability for calls that never needed to touch it
- [ ] B: ECS Fargate tasks are technically incapable of calling an Application Load Balancer
- [ ] C: Service Connect is required by AWS for any service with more than one replica
- [ ] D: The public ALB does not support HTTP, only HTTPS

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this exactly — unnecessary VPC round-trips and an availability dependency on a component the call never needed are the reasons internal service-to-service calls use Service Connect's DNS names.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [service-connect, internal-discovery, alb-vs-internal-dns]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why "write your own table" matters for independent releases
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why does the "no service queries another service's database directly" rule matter for Lighthouse's three teams releasing independently, even though all three services could technically share one RDS instance?

**OPTIONS:**
- [x] A: A schema migration in `settlement-service` could otherwise silently break `booking-service` at the database level, bypassing the smaller, more reviewable API contract the two services actually agree on
- [ ] B: RDS technically enforces one schema per database and cannot host multiple services' tables at all
- [ ] C: Shared databases are always slower than per-service databases regardless of query pattern
- [ ] D: AWS billing requires each ECS service to have its own dedicated RDS instance

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's stated reasoning is about the failure surface: an API contract is small and reviewable, while direct table access means any schema change anywhere can silently break an unrelated service.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [data-ownership, schema-isolation, independent-releases]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What the correlation ID actually proves
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The Practice Loop asks the learner to trace one booking's correlation ID across all three services' logs. What does successfully doing this demonstrate that checking each service's logs independently would not?

**OPTIONS:**
- [x] A: That one specific business transaction's full path — across both the synchronous call and the asynchronous event — can be reconstructed as a single connected story, not three unrelated log entries
- [ ] B: That the ECS cluster has enough CPU capacity to run all three services
- [ ] C: That the SNS topic has message encryption enabled
- [ ] D: That the correlation ID is cryptographically signed and tamper-proof

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Tracing the same correlation ID across services is what turns three independently deployed services' logs into one reconstructable transaction narrative, which is the lesson's stated purpose for propagating it.
**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [correlation-id, distributed-tracing, transaction-reconstruction]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why SQS tolerates notification-service being briefly down
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the asynchronous SNS-to-SQS boundary tolerate `notification-service` being briefly unavailable, in a way a synchronous call never could?

**OPTIONS:**
- [x] A: SQS holds the message until `notification-service` is able to process it, rather than requiring the receiver to be available at the exact moment the message is sent
- [ ] B: SNS automatically retries the entire booking transaction if `notification-service` is down
- [ ] C: SQS messages are deleted automatically if the receiver does not respond within one second
- [ ] D: Asynchronous boundaries do not actually decouple availability; the lesson is incorrect on this point

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this directly — SQS's durability lets it hold a message until the consumer is ready, which a synchronous call cannot do since both sides must be available simultaneously.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [sqs-durability, decoupled-availability, async-tolerance]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Interpreting the outage-simulation load test
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The scenario injects a 3-second delay into `settlement-service`'s `/estimate` handler while running a load test against `booking-service`, and every booking still completes successfully. What does this outcome actually demonstrate?

**OPTIONS:**
- [x] A: The 800ms timeout and `PENDING` fallback prevent a slow synchronous dependency from cascading into booking failures, proving the system degrades gracefully rather than failing outright
- [ ] B: That `settlement-service`'s 3-second delay has no effect on the system at all
- [ ] C: That the asynchronous SNS-to-SQS path was bypassed entirely during the test
- [ ] D: That `booking-service` retried the estimate call until it eventually succeeded

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The point of the injected delay is to prove the timeout-and-fallback design, not the absence of impact — bookings still complete, just with a deferred settlement figure, which is graceful degradation, not a bypass of the failure.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [graceful-degradation, dependency-outage, load-test-diagnostic]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 14

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-14-microservices-project-phase-2
lesson_title: "Microservices Project: Phase 2"
lesson_order: 14

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Medium-Hard
estimated_minutes: 120
content_status: Draft

learning_outcomes:
  - "Implement the transactional outbox pattern so a database write and an event publication commit atomically, eliminating the dual-write failure mode."
  - "Design an idempotent consumer using a processed-message ledger and a dead-letter queue, and explain why 'at-least-once' delivery requires the consumer, not the queue, to guarantee exactly-once processing."
  - "Compare a canary deployment against a full rollout for a specific risk profile, and choose the CloudWatch alarm that would automatically halt a bad canary."

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
# Microservices Project: Phase 2

## Concepts Covered

Lesson 13's `settlement-service` had a quiet bug: it wrote the settlement record to its own
database, then published the `SETTLEMENT_COMPLETED` event to SNS as a separate, second step. If the
process crashes between those two operations — after the database commit, before the publish call
succeeds — the settlement is recorded but `notification-service` never learns about it, and a
dispatcher never gets notified. This is the **dual-write problem**: two independent operations
(a database write and a message publish) that need to happen together but have no shared
transaction, so any interruption between them leaves the system in an inconsistent state that no
retry of either operation alone can fix. The **transactional outbox pattern** solves this by making
the event publication part of the same database transaction as the business write: instead of
calling SNS directly, `settlement-service` inserts a row into an `outbox_events` table in the same
transaction that writes the settlement record, and a separate poller (or a Debezium-style
change-data-capture stream) reads unpublished outbox rows and publishes them to SNS, marking each
row published only after the SNS call succeeds. Because the settlement write and the outbox insert
are one atomic transaction, "settlement recorded but event never queued for publish" becomes
structurally impossible — the worst case is "event queued for publish but not yet published,"
which the poller simply retries.

The receiving side needs its own guarantee, because SNS-to-SQS delivery is **at-least-once**, not
exactly-once: a message can be delivered twice (a consumer that processes a message successfully
but crashes before deleting it from the queue will see that same message redelivered). An
**idempotent consumer** handles this by recording each processed message's unique ID in a
`processed_events` table before acting on it, inside the same transaction as the side effect — if
the same message arrives again, the insert into `processed_events` fails on a unique-constraint
violation, and the consumer skips reprocessing rather than sending a duplicate notification. A
message that fails processing repeatedly (a malformed payload, a downstream dependency that is
permanently down) needs a **dead-letter queue (DLQ)**: after a configured `maxReceiveCount`, SQS
moves the message to a separate DLQ instead of redelivering it forever, which turns "one bad
message blocking the entire queue" into "one bad message sitting in a DLQ waiting for a human to
inspect it, while the rest of the queue keeps flowing." For deployment safety, a **canary**
release — sending a small percentage of traffic to the new revision and watching a specific
CloudWatch alarm (elevated 5xx rate, elevated p99 latency) before promoting to 100% — catches a bad
deployment against a small blast radius, whereas a full rollout exposes every request to a
regression the moment it deploys; the trade-off is that a canary takes longer to fully roll out and
requires the alarm threshold to be tuned precisely enough to catch a real regression without
false-triggering on normal variance.

```sql
-- Transactional outbox: the settlement write and the event insert commit atomically
BEGIN;
INSERT INTO settlements (id, booking_id, amount_cents, status)
  VALUES ('stl_8f2a', 'bkg_1c3d', 48900, 'COMPLETED');
INSERT INTO outbox_events (id, event_type, payload, published)
  VALUES ('evt_9b1e', 'SETTLEMENT_COMPLETED',
          '{"settlementId":"stl_8f2a","bookingId":"bkg_1c3d","amountCents":48900}', false);
COMMIT;
-- A separate poller reads WHERE published = false, calls sns:Publish, then sets published = true
```

```java
// Idempotent consumer: the unique-constraint insert is the deduplication mechanism itself
@Transactional
void handle(SettlementCompletedEvent event) {
    boolean firstTimeSeen = processedEventsRepo.tryInsert(event.getMessageId()); // unique constraint on message_id
    if (!firstTimeSeen) {
        log.info("Duplicate delivery of {}, skipping", event.getMessageId());
        return; // already processed — do NOT send a second notification
    }
    dispatcherAlertService.notify(event.getBookingId(), event.getAmountCents());
}
```

```bash
# DLQ after 5 failed delivery attempts — the malformed message stops blocking the live queue
aws sqs set-queue-attributes --queue-url https://sqs.us-east-1.amazonaws.com/111122223333/notification-inbox \
  --attributes '{"RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:111122223333:notification-inbox-dlq\",\"maxReceiveCount\":\"5\"}"}'

# Canary deployment: 10% of traffic to the new task set, halted automatically if 5xx alarm fires
aws cloudwatch put-metric-alarm --alarm-name notification-service-canary-5xx \
  --namespace ManifestFlow/DispatchWorks --metric-name 5xxCount --statistic Sum \
  --period 60 --evaluation-periods 2 --threshold 5 --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:111122223333:deployment-rollback-topic
```

## Practical Backend Scenario

A production incident exposes the dual-write bug directly: `settlement-service` crashes
immediately after committing a settlement record but before its SNS publish call completes,
leaving a real settlement with no corresponding notification ever sent to the dispatcher, discovered
only when Lighthouse manually reconciles settlement totals against dispatcher acknowledgments a week
later. The FDE implements the transactional outbox pattern so the settlement write and the outbox
insert commit together, and a poller handles publishing with its own retry logic. Separately, a
transient SQS redelivery causes `notification-service` to receive the same `SETTLEMENT_COMPLETED`
message twice; without the idempotent-consumer check, this would have sent the dispatcher two
notifications for one settlement. With the `processed_events` unique-constraint guard in place, the
second delivery is detected and skipped, and the FDE confirms this by deliberately re-delivering a
message and verifying only one notification was ever actually sent.

## Practice Loop

1. Add an `outbox_events` table to `settlement-service`'s schema, rewrite the settlement-completion
   code path so the settlement write and the outbox insert happen in one transaction, and build a
   poller that publishes unpublished rows to SNS and marks them published only after the SNS call
   succeeds.
2. Add a `processed_events` table with a unique constraint on message ID to `notification-service`,
   and rewrite its consumer to insert-then-act, skipping any message whose ID insert fails on the
   constraint.
3. Deliberately kill `settlement-service`'s process between the outbox insert and the poller's next
   run, restart it, and count how many settlements are missing their published event afterward —
   the diagnostic answer must be zero, since the poller picks up any unpublished row on restart.
4. Manually re-deliver one already-processed SQS message to `notification-service` and verify
   exactly one notification was sent in total, not two, using the `processed_events` table as
   evidence.
5. Configure the DLQ redrive policy and the canary CloudWatch alarm above, deploy a deliberately
   broken revision of `notification-service` behind the canary, and confirm the alarm fires and
   halts promotion before 100% of traffic reaches the broken revision.

## Evidence of Understanding

You can explain the dual-write problem and implement the transactional outbox pattern so a database
write and its corresponding event publication cannot become inconsistent from a mid-process crash.
You can build an idempotent consumer using a processed-message ledger and demonstrate, by forcing a
duplicate delivery, that it sends the side effect exactly once despite at-least-once delivery
semantics. You can configure a dead-letter queue so a permanently failing message stops blocking
the live queue, and you can compare a canary deployment's smaller blast radius against a full
rollout's faster completion for a given regression risk.

## Suggested Extension

Add a consumer-driven contract test between `booking-service` and `settlement-service` that fails
the build if `settlement-service`'s `/estimate` response shape changes in a way `booking-service`
does not expect, and explain why this test belongs in `settlement-service`'s own CI pipeline rather
than only in `booking-service`'s.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What the dual-write problem actually is
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what specifically causes the dual-write problem in the original `settlement-service` design?

**OPTIONS:**
- [x] A: The database write and the SNS publish call are two independent operations with no shared transaction, so a crash between them leaves the settlement recorded but the event never published
- [ ] B: SNS itself corrupts messages under high load
- [ ] C: PostgreSQL does not support transactions for insert statements
- [ ] D: The dual-write problem only occurs when two different databases are involved

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson defines the dual-write problem precisely as two independent operations lacking a shared transaction — any interruption between them leaves an inconsistent state neither retry can fix alone.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [dual-write-problem, transaction-boundary, event-publication]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Reading the transactional outbox SQL
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```sql
BEGIN;
INSERT INTO settlements (id, booking_id, amount_cents, status)
  VALUES ('stl_8f2a', 'bkg_1c3d', 48900, 'COMPLETED');
INSERT INTO outbox_events (id, event_type, payload, published)
  VALUES ('evt_9b1e', 'SETTLEMENT_COMPLETED', '{"settlementId":"stl_8f2a"...}', false);
COMMIT;
```

**QUESTION_TEXT:**
Why does inserting into `outbox_events` inside the same transaction as the `settlements` insert eliminate the dual-write problem?

**OPTIONS:**
- [x] A: Both inserts either commit together or neither does, so "settlement recorded but no event queued for publish" becomes structurally impossible
- [ ] B: It makes the SNS publish call itself part of the same database transaction
- [ ] C: It removes the need for a poller to ever publish the event
- [ ] D: It guarantees the event reaches `notification-service` within one second

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The outbox pattern's guarantee is atomicity between the business write and the outbox insert, not the publish call itself — the lesson is explicit that the worst remaining case is "queued but not yet published," which a poller retries.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [transactional-outbox, atomicity, outbox-pattern]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What actually deduplicates the idempotent consumer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```java
boolean firstTimeSeen = processedEventsRepo.tryInsert(event.getMessageId());
if (!firstTimeSeen) {
    return; // already processed
}
dispatcherAlertService.notify(event.getBookingId(), event.getAmountCents());
```

**QUESTION_TEXT:**
What mechanism actually prevents a duplicate SQS delivery from sending a second notification here?

**OPTIONS:**
- [x] A: A unique constraint on `message_id` in the `processed_events` table causes the second insert attempt to fail, and the failed insert is what signals "already processed"
- [ ] B: SQS itself guarantees each message is delivered exactly once, making the check redundant
- [ ] C: The `@Transactional` annotation alone prevents duplicate notifications with no other logic needed
- [ ] D: `dispatcherAlertService.notify` internally deduplicates by booking ID

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The insert's unique constraint is the actual deduplication mechanism — a duplicate message's insert fails, `firstTimeSeen` is false, and the notification is skipped, exactly as the lesson describes.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [idempotent-consumer, unique-constraint, deduplication]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why SQS delivery is at-least-once, not exactly-once
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why can a consumer that successfully processes an SQS message still see that same message delivered again?

**OPTIONS:**
- [x] A: If the consumer crashes after processing the message but before deleting it from the queue, SQS will redeliver it, since delivery guarantees are at-least-once rather than exactly-once
- [ ] B: SQS intentionally duplicates every message twice for durability
- [ ] C: SNS always sends two copies of every published event
- [ ] D: This scenario cannot actually happen; the lesson is describing a hypothetical that SQS prevents
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this exactly — the gap between "processed successfully" and "deleted from the queue" is where a crash produces redelivery, which is the mechanical reason delivery is at-least-once.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [at-least-once-delivery, sqs-redelivery, consumer-crash]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What the DLQ's maxReceiveCount accomplishes
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```json
{"RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:111122223333:notification-inbox-dlq\",\"maxReceiveCount\":\"5\"}"}
```

**QUESTION_TEXT:**
What happens to a message that fails processing on `notification-inbox` for the 6th consecutive time, given this redrive policy?

**OPTIONS:**
- [x] A: SQS moves it to `notification-inbox-dlq` instead of redelivering it again, so it stops blocking the live queue
- [ ] B: SQS deletes the message permanently with no further trace
- [ ] C: SQS pauses the entire queue until a human manually intervenes
- [ ] D: SQS automatically retries the message every millisecond until it succeeds
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`maxReceiveCount: 5` means the 6th failed receive triggers the redrive to the DLQ — exactly the "one bad message sitting in a DLQ, rest of the queue keeps flowing" behavior the lesson describes.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [dead-letter-queue, max-receive-count, redrive-policy]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Canary vs. full rollout trade-off
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the trade-off the lesson names between a canary deployment and a full rollout?

**OPTIONS:**
- [x] A: A canary limits a bad deployment's blast radius but takes longer to fully roll out and requires a precisely tuned alarm threshold; a full rollout is faster but exposes every request to a regression immediately
- [ ] B: A canary is always strictly better with no downside, which is why it should always be used
- [ ] C: A full rollout is safer because it tests the new revision against more traffic at once
- [ ] D: Canary deployments are only possible for stateless Lambda functions, not ECS services
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this trade-off directly — smaller blast radius and slower full completion, dependent on a well-tuned alarm, versus a full rollout's speed at the cost of immediate full exposure.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [canary-deployment, blast-radius, rollout-tradeoff]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What the canary alarm's evaluation periods guard against
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
aws cloudwatch put-metric-alarm --alarm-name notification-service-canary-5xx \
  --namespace ManifestFlow/DispatchWorks --metric-name 5xxCount --statistic Sum \
  --period 60 --evaluation-periods 2 --threshold 5 --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:111122223333:deployment-rollback-topic
```

**QUESTION_TEXT:**
What does this alarm require before it transitions to ALARM and triggers the rollback action?

**OPTIONS:**
- [x] A: More than 5 total 5xx responses in each of two consecutive 60-second periods
- [ ] B: A single 5xx response at any point during the canary
- [ ] C: A 5xx rate above 5% averaged over the entire canary duration
- [ ] D: Any 5xx response combined with a p99 latency breach in the same period
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`--period 60 --evaluation-periods 2 --threshold 5 --comparison-operator GreaterThanThreshold` requires more than 5 in each of two consecutive 60-second windows before the alarm fires.
**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [cloudwatch-alarm, evaluation-periods, canary-rollback]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why the outbox poller only needs to retry the publish, not the write
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
After adopting the outbox pattern, `settlement-service` crashes right after the transaction in the SQL example commits. What is the worst-case state the poller has to recover from, per the lesson?

**OPTIONS:**
- [x] A: The event row exists in `outbox_events` with `published = false` — the poller simply retries publishing it; the settlement write itself is never at risk of being lost or duplicated
- [ ] B: Both the settlement row and the outbox row may or may not exist, requiring manual reconciliation
- [ ] C: The settlement row is lost and must be manually re-entered from a paper record
- [ ] D: The poller must roll back the settlement transaction entirely and ask the customer to resubmit
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Because both inserts commit atomically, a crash right after commit leaves a fully consistent, already-committed transaction with only the downstream publish outstanding — the lesson states this is the entire remaining failure surface.
**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [outbox-recovery, crash-consistency, poller-retry]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 15

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-15-aws-security-identity-and-network
lesson_title: "AWS Security: Identity and Network"
lesson_order: 15

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Rewrite an overly broad IAM policy into a scoped, resource-and-condition-constrained policy, and explain what an Action-vs-Resource-vs-Condition review actually checks."
  - "Design a trust policy and a permission boundary together so a role's assumability and its maximum grantable permissions are two independently enforced limits."
  - "Replace a broad CIDR-based network path with a VPC endpoint (Gateway or Interface) for one specific AWS service, and articulate the reduced blast radius."

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
# AWS Security: Identity and Network

## Concepts Covered

An IAM policy grants permission along four dimensions, and a security review that checks only one
of them — usually just `Action` — misses most of the actual risk. `Effect` is `Allow` or `Deny`;
`Action` names the specific API calls (`s3:GetObject`, not just "S3 access"); `Resource` scopes
which specific ARNs the action applies to, and a `Resource: "*"` alongside a broad action is the
single most common overprivilege pattern an FDE finds in an early prototype; `Condition` narrows the
grant further by context — the calling principal's source IP, whether the request used TLS, a
specific tag on the target resource — and is what turns "this role can read this bucket" into "this
role can read this bucket, but only over TLS, and only for objects tagged for its own tenant."
A **trust policy** (the `AssumeRolePolicyDocument` attached to a role) is a completely separate
control from the role's permission policy: the trust policy decides *who* can assume the role at
all (which principal — a specific IAM user, a specific service, a specific external account with a
specific external ID), while the permission policy decides *what* the role can do once assumed —
conflating the two is a common error, because a role with a narrow permission policy but an
overly-broad trust policy (e.g., trusting an entire AWS account rather than one specific role
within it) can still be assumed by far more principals than intended. A **permission boundary** adds
a third, independent ceiling: it is a policy attached to a user or role that caps the *maximum*
permissions that identity's own policies can ever grant, regardless of how permissive those
policies are — useful specifically when an automated process creates roles on a customer's behalf
(a self-service provisioning pipeline) and the customer wants a hard guarantee that no role it
creates can ever exceed a defined ceiling, even if the pipeline's own policy-generation logic has a
bug.

On the network side, a **VPC endpoint** replaces a broad, internet-routed (or NAT-Gateway-routed)
path to an AWS service with a private, in-VPC path scoped to exactly that service. A **Gateway
endpoint** (available for S3 and DynamoDB only) adds a route-table entry that sends traffic for that
service's IP ranges directly within the VPC, with no ENI and no additional hourly cost; an
**Interface endpoint** (available for most other AWS services, including Secrets Manager and KMS)
places an ENI with a private IP inside your subnet, the same PrivateLink mechanism used for
cross-account service exposure. Either way, traffic to that AWS service never traverses the NAT
Gateway or the public internet at all, which matters for two reasons beyond cost: it removes an
entire class of egress-filtering bypass (a compromised instance that would otherwise reach any
public S3 bucket over the NAT Gateway can be restricted, via the endpoint policy, to only your own
account's buckets), and it means a private subnet with no NAT Gateway route at all can still reach
the AWS services it needs — collapsing the network's actual internet-reachable surface to zero for
that workload, not just to "whatever the security group happens to allow."

```json
// BEFORE: the first prototype's actual policy — broad action, broad resource, no condition
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": "s3:*", "Resource": "*" },
    { "Effect": "Allow", "Action": "secretsmanager:*", "Resource": "*" }
  ]
}
```

```json
// AFTER: scoped to exactly what manifestflow-worker-role needs, with a TLS condition
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::manifestflow-manifests/*",
      "Condition": { "Bool": { "aws:SecureTransport": "true" } }
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:us-east-1:111122223333:secret:manifestflow/textract-api-key-*"
    }
  ]
}
```

```json
// Trust policy: only the deploy pipeline's role in THIS account can assume manifestflow-worker-role
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::111122223333:role/deploy-pipeline-role" },
    "Action": "sts:AssumeRole",
    "Condition": { "StringEquals": { "sts:ExternalId": "manifestflow-2026" } }
  }]
}
```

```bash
# Replace the NAT-Gateway-routed path to Secrets Manager with a private Interface endpoint
aws ec2 create-vpc-endpoint --vpc-id vpc-0a1b2c3d4e5f60789 \
  --service-name com.amazonaws.us-east-1.secretsmanager --vpc-endpoint-type Interface \
  --subnet-ids subnet-0priv1 subnet-0priv2 --security-group-ids sg-0endpoint1a2b

# Gateway endpoint for S3 — a route-table entry, no ENI, no hourly cost
aws ec2 create-vpc-endpoint --vpc-id vpc-0a1b2c3d4e5f60789 \
  --service-name com.amazonaws.us-east-1.s3 --vpc-endpoint-type Gateway \
  --route-table-ids rtb-private-app-1a
```

## Practical Backend Scenario

ManifestFlow's extraction worker needs to read one specific S3 bucket and fetch one specific
Secrets Manager secret (the Textract API key). The first prototype, written under deadline pressure,
attaches an IAM role with `s3:*`/`Resource: *` and `secretsmanager:*`/`Resource: *` — the "admin
key" pattern the skeleton describes, expressed here as an over-scoped role rather than a literal
long-lived access key, since the actual prototype already used role-based auth but never scoped the
policy. A customer security review flags it in minutes: the worker could read or write any bucket
in the account, and read any secret, including ones belonging to unrelated services. The FDE
rewrites the policy to the scoped version above, adds a trust policy restricting who can assume the
role at all, and replaces the worker's NAT-Gateway-routed calls to S3 and Secrets Manager with VPC
endpoints — so even a fully compromised worker process has no network path to any AWS service
outside these two specific endpoints, and no IAM permission beyond these two specific resources.

## Practice Loop

1. Pull the current `manifestflow-worker-role` policy and mark every statement whose `Action` or
   `Resource` is a wildcard (`*`), then write down, for each one, exactly which specific action and
   resource the worker code actually calls.
2. Rewrite the policy to the scoped version, adding the `aws:SecureTransport` condition on the S3
   statements, and attach a trust policy that names the specific deploy-pipeline role rather than
   trusting the account as a whole.
3. Run `aws iam simulate-principal-policy` against the new policy for one allowed action
   (`s3:GetObject` on the manifests bucket) and one action that should now be denied
   (`s3:DeleteBucket`), and record both results as your evidence the scoping actually took effect.
4. Create the S3 Gateway endpoint and the Secrets Manager Interface endpoint, remove the worker
   subnet's NAT Gateway route entirely, and confirm the worker can still read the bucket and fetch
   the secret with zero route to the public internet.
5. Document a break-glass emergency-access path (a separate, tightly-scoped role requiring MFA and
   logged via CloudTrail) for the case where the scoped policy turns out to be missing a permission
   an on-call engineer needs during an incident.

## Evidence of Understanding

You can review an IAM policy along all four dimensions — Effect, Action, Resource, and Condition —
and identify a `Resource: "*"` alongside a broad action as the specific overprivilege pattern to
flag first. You can design a trust policy and a permission boundary as two independently enforced
limits, one controlling who can assume a role and the other capping what any of that identity's own
policies can ever grant. You can replace a NAT-Gateway-routed path to an AWS service with a VPC
endpoint and demonstrate, with a route-table check, that the resulting private subnet has zero
route to the public internet while still reaching the services it needs.

## Suggested Extension

Attach a permission boundary to `deploy-pipeline-role` itself, capping the maximum permissions any
role it creates on Lighthouse's behalf can ever have, and write the one IAM policy statement that
would let the pipeline create new scoped worker roles freely while guaranteeing none of them can
ever be granted `iam:*` or `s3:*`/`Resource:*`, even by a future bug in the pipeline's own
policy-generation code.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** The four dimensions of an IAM policy statement
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, checking only which dimension of an IAM policy statement causes a security review to miss most of the actual risk?

**OPTIONS:**
- [x] A: Checking only `Action` while ignoring `Resource` and `Condition`
- [ ] B: Checking only the policy's `Version` field
- [ ] C: Checking only whether the policy is attached to a role versus a user
- [ ] D: Checking only the policy's character-count length

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson opens with exactly this point — a review that checks only `Action` misses the `Resource: "*"` overprivilege pattern and any missing `Condition` narrowing.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [iam-policy-dimensions, action-resource-condition, security-review]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Reading the before-policy's overprivilege
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```json
{ "Effect": "Allow", "Action": "s3:*", "Resource": "*" }
```

**QUESTION_TEXT:**
What can `manifestflow-worker-role` do under this single statement, beyond reading the one manifests bucket it actually needs?

**OPTIONS:**
- [x] A: Read, write, and delete objects in every S3 bucket in the account, not just the manifests bucket
- [ ] B: Nothing beyond reading the manifests bucket; `s3:*` is scoped automatically to buckets the role has previously accessed
- [ ] C: Only read access is granted; `s3:*` never includes write or delete actions
- [ ] D: Access to S3 in other AWS accounts, but not other buckets within this account
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`s3:*` grants every S3 action (read, write, delete, and administrative actions), and `Resource: "*"` scopes it to every bucket in the account — exactly the overprivilege the customer review flags.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [wildcard-action, wildcard-resource, s3-overprivilege]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What the aws:SecureTransport condition adds
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```json
"Condition": { "Bool": { "aws:SecureTransport": "true" } }
```

**QUESTION_TEXT:**
What does adding this condition to the scoped S3 statement accomplish that scoping `Resource` alone does not?

**OPTIONS:**
- [x] A: It denies the action if the request was not made over TLS, adding a context-based restriction beyond which resource is targeted
- [ ] B: It restricts the action to only the account's root user
- [ ] C: It automatically encrypts objects at rest with a customer-managed KMS key
- [ ] D: It has no effect since S3 always requires TLS regardless of policy
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`Condition` narrows a grant by context — here, the transport security of the request — which `Resource` scoping alone does not address, exactly as the lesson's four-dimension framing describes.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [iam-condition, securetransport, context-based-restriction]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Trust policy vs. permission policy
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A role has a narrowly scoped permission policy but its trust policy names an entire AWS account as the trusted principal rather than one specific role within it. What is the actual risk here, per the lesson?

**OPTIONS:**
- [x] A: Far more principals than intended — any identity in that trusted account — can assume the role, regardless of how narrow the role's own permission policy is
- [ ] B: There is no risk, since the permission policy's narrow scope caps what any assumer could do anyway
- [ ] C: The role becomes unassumable entirely because the trust policy is too broad
- [ ] D: AWS automatically rejects trust policies that name an entire account
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's core distinction is that the trust policy controls *who* can assume the role, entirely separate from what the role can do — a broad trust policy widens the set of principals regardless of how tight the permission policy is.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [trust-policy, assume-role, principal-scope]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What a permission boundary caps
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what does attaching a permission boundary to `deploy-pipeline-role` actually guarantee?

**OPTIONS:**
- [x] A: No role that `deploy-pipeline-role` creates can ever be granted permissions beyond the boundary's ceiling, even if the pipeline's own policy-generation logic has a bug
- [ ] B: It prevents `deploy-pipeline-role` itself from being deleted by mistake
- [ ] C: It automatically rotates the credentials of every role the pipeline creates
- [ ] D: It replaces the need for a trust policy on any role the pipeline creates
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names this exact use case — a hard ceiling on maximum grantable permissions, independent of and as a backstop against bugs in whatever generates the actual policies.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [permission-boundary, maximum-permissions, self-service-provisioning]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Gateway endpoint vs. Interface endpoint
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the mechanical difference between the S3 Gateway endpoint and the Secrets Manager Interface endpoint in the lesson's CLI example?

**OPTIONS:**
- [x] A: The Gateway endpoint adds a route-table entry with no ENI or hourly cost; the Interface endpoint places an ENI with a private IP inside the subnet, using the PrivateLink mechanism
- [ ] B: Both are functionally identical; the naming difference is purely cosmetic
- [ ] C: The Interface endpoint is only usable for S3, and the Gateway endpoint only for Secrets Manager
- [ ] D: The Gateway endpoint requires a security group while the Interface endpoint does not
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this mechanical distinction directly — Gateway endpoints (S3, DynamoDB only) are route-table entries; Interface endpoints use an ENI via the same PrivateLink primitive covered in an earlier lesson.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [gateway-endpoint, interface-endpoint, privatelink]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What removing the NAT Gateway route actually proves
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 4 has the FDE remove the worker subnet's NAT Gateway route entirely after adding the VPC endpoints, then confirm the worker still functions. What does this specific test demonstrate?

**OPTIONS:**
- [x] A: That the worker's only remaining network dependencies (S3, Secrets Manager) are reachable through the endpoints alone, so the subnet's internet-reachable surface for outbound traffic is now genuinely zero, not merely "restricted by a security group"
- [ ] B: That the NAT Gateway was never actually necessary for any AWS workload
- [ ] C: That VPC endpoints are faster than NAT Gateway-routed calls
- [ ] D: That removing a NAT Gateway route has no effect on which services a subnet can reach
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's point is the network-level backstop: with the NAT Gateway route gone and only the two endpoints present, there is no path to the general internet at all — a stronger guarantee than a security-group-only restriction.
**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [nat-gateway-removal, vpc-endpoint-verification, zero-internet-surface]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why simulate-principal-policy is run for both an allowed and a denied action
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 3 asks the learner to run `aws iam simulate-principal-policy` for one action that should be allowed (`s3:GetObject`) and one that should now be denied (`s3:DeleteBucket`). Why check both rather than only the allowed action?

**OPTIONS:**
- [x] A: Confirming only the allowed action would not prove the wildcard permissions were actually removed — the denied-action check is the evidence the scoping took effect, not just that the intended access still works
- [ ] B: `simulate-principal-policy` requires exactly two actions to be checked in a single call
- [ ] C: `s3:DeleteBucket` is technically part of the same API call as `s3:GetObject`
- [ ] D: There is no reason; checking only the allowed action would be equally sufficient
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
Verifying the scoped policy still allows what it should is only half the evidence — confirming a previously-allowed, now out-of-scope action is denied is what proves the wildcard was actually removed rather than just additively extended.
**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [policy-simulator, allow-deny-verification, scoping-evidence]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why the break-glass path still needs to exist
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
After scoping `manifestflow-worker-role` tightly, why does the lesson still recommend documenting a separate break-glass emergency-access role?

**OPTIONS:**
- [x] A: A scoped policy can turn out to be missing a permission an on-call engineer genuinely needs during a real incident, and a tightly-scoped, MFA-required, CloudTrail-logged break-glass path handles that case without permanently widening the worker role's own policy
- [ ] B: Break-glass roles are required by AWS for every account regardless of policy scope
- [ ] C: The scoped policy is expected to be wrong on first attempt, so break-glass is the primary access path
- [ ] D: MFA cannot be applied to the worker role itself, only to break-glass roles
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson frames break-glass access as the deliberate escape hatch for a scoped policy's inevitable edge case, kept separately auditable rather than solved by loosening the worker role's everyday permissions.
**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [break-glass-access, emergency-access, least-privilege-tradeoff]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 16

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-16-aws-security-data-and-detection
lesson_title: "AWS Security: Data and Detection"
lesson_order: 16

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Apply an S3 bucket policy that denies non-TLS and non-KMS-encrypted uploads, and explain why this control belongs at the bucket-policy layer rather than relying on client-side discipline alone."
  - "Read a GuardDuty finding's severity, type, and resource fields to distinguish a reconnaissance signal from an active-exfiltration signal."
  - "Enable CloudTrail S3 data events for one sensitive bucket and use them, alongside a GuardDuty finding, to reconstruct which principal accessed which object and when."

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
# AWS Security: Data and Detection

## Concepts Covered

Protecting data at rest with KMS is only as strong as what is allowed to bypass it, which is why
the enforcement belongs in the **bucket policy**, not only in application code's own encryption
call. A bucket policy statement can deny any `PutObject` that does not carry
`x-amz-server-side-encryption: aws:kms` and any request at all that did not arrive over TLS — this
is a resource-level control that holds regardless of which client, script, or misconfigured tool
attempts the upload, whereas relying on "the application always sets the encryption header" is a
promise that breaks the moment someone runs `aws s3 cp` by hand or a new integration forgets the
header. Envelope encryption itself follows the same shape covered for cross-account BYOK elsewhere
in this curriculum, but the mechanism that matters most operationally for a regulated customer is
**key rotation and scope**: a customer-managed KMS key (not the AWS-managed default) lets you
control the rotation schedule, restrict which principals can use the key via the key policy, and —
critically — revoke access to all data encrypted under that key by disabling or scheduling deletion
of the key itself, which is a data-level kill switch no amount of IAM policy tightening on the
application role alone can replicate.

**GuardDuty** is a managed threat-detection service that continuously analyzes VPC Flow Logs, DNS
query logs, and CloudTrail management and S3 data events, and produces findings without you writing
any detection logic yourself — each finding carries a `type` (a structured taxonomy, e.g.
`UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration`), a `severity` score (a low score often
means reconnaissance-shaped activity worth noting but not paging on; a high score means the finding
matches a pattern GuardDuty associates with active compromise), and the specific resource and
principal involved. The judgment an FDE needs is distinguishing what a finding actually asserts:
`Recon:IAMUser/TorIPCaller` means a call was made from a Tor exit node — worth investigating, not
necessarily an active breach — while `Exfiltration:S3/ObjectRead.Unusual` means GuardDuty's model
detected an S3 read pattern (volume, timing, source) that deviates sharply from that principal's
historical baseline, a materially more urgent signal. GuardDuty findings are strongest paired with
**CloudTrail S3 data events**, which are off by default (unlike CloudTrail's always-on management
events) because of their volume and cost, and must be explicitly enabled per bucket — once enabled,
a GuardDuty finding naming a specific object gives you the alert, and the corresponding CloudTrail
data event for that same object and time window gives you the exact principal, source IP, and
whether the call succeeded, which is what turns "GuardDuty flagged something" into an actual,
attributable incident timeline.

```json
// Bucket policy: deny any upload that is not TLS, and any upload not using the customer-managed KMS key
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny", "Principal": "*", "Action": "s3:*",
      "Resource": ["arn:aws:s3:::manifestflow-manifests", "arn:aws:s3:::manifestflow-manifests/*"],
      "Condition": { "Bool": { "aws:SecureTransport": "false" } }
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny", "Principal": "*", "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::manifestflow-manifests/*",
      "Condition": {
        "StringNotEquals": { "s3:x-amz-server-side-encryption": "aws:kms" }
      }
    }
  ]
}
```

```bash
# Enable CloudTrail S3 data events for the sensitive manifests bucket only (off by default — volume/cost)
aws cloudtrail put-event-selectors --trail-name manifestflow-org-trail \
  --event-selectors '[{
    "ReadWriteType": "All", "IncludeManagementEvents": true,
    "DataResources": [{"Type": "AWS::S3::Object", "Values": ["arn:aws:s3:::manifestflow-manifests/"]}]
  }]'
```

```json
// A representative GuardDuty finding — worth reading field by field
{
  "type": "Exfiltration:S3/ObjectRead.Unusual",
  "severity": 8.0,
  "resource": {
    "s3BucketDetails": [{"name": "manifestflow-manifests"}],
    "accessKeyDetails": {"principalId": "AROAEXAMPLE:manifestflow-worker-role", "userType": "AssumedRole"}
  },
  "service": {
    "action": {
      "awsApiCallAction": {
        "api": "GetObject", "callerType": "Remote IP",
        "remoteIpDetails": {"ipAddressV4": "198.51.100.77", "country": {"countryName": "Unknown"}}
      }
    },
    "count": 214
  },
  "title": "Unusual volume of GetObject calls against manifestflow-manifests by manifestflow-worker-role"
}
```

```bash
# Correlate the finding's object-level activity against CloudTrail data events for the exact window
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=manifestflow-manifests \
  --start-time 2026-08-31T09:00:00Z --end-time 2026-08-31T10:00:00Z \
  --query 'Events[].{Time:EventTime,User:Username,Event:EventName,Source:SourceIPAddress}'
```

## Practical Backend Scenario

Lighthouse's security review asks two direct questions: how are customs manifests encrypted, and
how would an unusual download be detected. The FDE answers the first by enabling the bucket policy
above (denying non-TLS traffic and any upload not using the customer-managed KMS key) and confirms
the key's rotation and access are controlled through its own key policy, not just the worker role's
IAM permissions. For the second, GuardDuty is already enabled account-wide, but S3 data events for
`manifestflow-manifests` were not — the FDE enables them specifically for this bucket, then
generates a controlled test signal: from an unused development credential, the FDE calls
`GetObject` 200 times in under a minute against the manifests bucket, well outside
`manifestflow-worker-role`'s normal access pattern. GuardDuty produces an
`Exfiltration:S3/ObjectRead.Unusual` finding within minutes, and the corresponding CloudTrail data
events — now that they are enabled — confirm the exact API calls, the source IP, and the specific
objects read, giving the security team a full, attributable timeline rather than only GuardDuty's
summary.

## Practice Loop

1. Classify the manifests bucket's contents (customs data, PII-adjacent) and write the bucket
   policy above, denying non-TLS traffic and any upload not using the customer-managed KMS key.
2. Attempt an upload with `aws s3 cp` using default (unencrypted) settings and confirm it is
   denied by the bucket policy itself, not merely flagged by a linter or application-level check.
3. Enable CloudTrail S3 data events for this one bucket only (not account-wide, given the
   volume/cost trade-off the lesson names), and generate the controlled `GetObject` burst described
   in the scenario.
4. Retrieve the resulting GuardDuty finding, and identify its `type`, `severity`, and the
   specific principal and IP it names, distinguishing whether this finding's language matches
   reconnaissance or active exfiltration.
5. Run the CloudTrail `lookup-events` query for the same time window and object, and write the
   one-paragraph incident timeline combining the GuardDuty finding's summary with CloudTrail's
   per-call detail — actor, timestamp, action, and source IP.

## Evidence of Understanding

You can write an S3 bucket policy that denies non-TLS and non-KMS-encrypted uploads and explain why
this control belongs at the bucket-policy layer rather than depending on application code always
setting the right header. You can read a GuardDuty finding's `type` and `severity` fields to
distinguish a reconnaissance-shaped signal from one GuardDuty associates with active exfiltration.
You can enable CloudTrail S3 data events for one specific bucket, understand why they are off by
default elsewhere, and combine a GuardDuty finding with the matching CloudTrail data events into an
attributable incident timeline naming actor, time, action, and source IP.

## Suggested Extension

Add an EventBridge rule that triggers a Lambda function automatically when a GuardDuty finding of
severity 7 or higher targets `manifestflow-manifests`, and have that function immediately revoke
the implicated principal's active sessions — write the one sentence explaining why this automated
first response should still require a human to confirm before permanently disabling the principal,
rather than doing that step automatically too.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why enforcement belongs at the bucket-policy layer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why does denying unencrypted uploads at the S3 bucket-policy layer matter more than relying on application code always setting the encryption header?

**OPTIONS:**
- [x] A: A bucket policy holds regardless of which client attempts the upload, while relying on application code is a promise that breaks the moment someone uploads by hand or a new integration forgets the header
- [ ] B: Application-level encryption headers are not actually supported by S3 at all
- [ ] C: Bucket policies are evaluated faster than application code, which is the only reason to prefer them
- [ ] D: There is no meaningful difference; both approaches are equally reliable
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's point is resource-level enforcement versus a client-side promise — the bucket policy holds no matter which tool or script attempts the upload.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [bucket-policy-enforcement, encryption-at-rest, resource-level-control]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Reading the deny-unencrypted-uploads statement
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```json
{
  "Sid": "DenyUnencryptedObjectUploads",
  "Effect": "Deny", "Principal": "*", "Action": "s3:PutObject",
  "Resource": "arn:aws:s3:::manifestflow-manifests/*",
  "Condition": { "StringNotEquals": { "s3:x-amz-server-side-encryption": "aws:kms" } }
}
```

**QUESTION_TEXT:**
What upload does this statement actually block?

**OPTIONS:**
- [x] A: Any `PutObject` into this bucket whose server-side-encryption header is not exactly `aws:kms` — including uploads with no encryption header at all
- [ ] B: Any upload larger than the default S3 object size limit
- [ ] C: Any upload made outside business hours
- [ ] D: Any upload that uses AWS-managed (not customer-managed) KMS encryption specifically
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`StringNotEquals` on the encryption header denies any `PutObject` where that header is missing or set to anything other than `aws:kms` — exactly the "no encryption header at all" case this control is meant to catch.
**LESSON_CONNECTION:** Practice Loop, Step 2
**KEYWORDS:** [bucket-policy-condition, kms-encryption-header, deny-statement]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why a customer-managed key gives a real kill switch
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why does using a customer-managed KMS key (rather than the AWS-managed default) give a data-level kill switch that tightening the application role's IAM policy alone cannot replicate?

**OPTIONS:**
- [x] A: Disabling or scheduling deletion of the key itself revokes access to every object ever encrypted under it, regardless of what IAM permissions any role still holds
- [ ] B: Customer-managed keys are automatically rotated every 24 hours, unlike AWS-managed keys
- [ ] C: AWS-managed keys cannot be used with S3 server-side encryption at all
- [ ] D: A customer-managed key removes the need for a bucket policy entirely
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this exactly — disabling the key revokes access at the data layer itself, independent of any IAM policy tightening on the roles that would otherwise still hold their existing permissions.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [customer-managed-key, kill-switch, key-revocation]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Reconnaissance vs. exfiltration findings
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the difference in what `Recon:IAMUser/TorIPCaller` and `Exfiltration:S3/ObjectRead.Unusual` each assert, per the lesson?

**OPTIONS:**
- [x] A: The Tor-caller finding means a call originated from a Tor exit node — worth investigating but not necessarily active compromise; the exfiltration finding means GuardDuty's model detected an S3 read pattern that deviates sharply from the principal's historical baseline, a materially more urgent signal
- [ ] B: Both findings mean exactly the same thing; the naming is cosmetic
- [ ] C: The Tor-caller finding is always more severe than any S3-related finding
- [ ] D: `Recon` findings are false positives by definition and can be safely ignored
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson draws this exact distinction between the two named finding types — origin-based reconnaissance versus a baseline-deviation exfiltration signal.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [guardduty-finding-types, reconnaissance, exfiltration]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Reading the GuardDuty finding JSON
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```json
{
  "type": "Exfiltration:S3/ObjectRead.Unusual",
  "severity": 8.0,
  "resource": {
    "s3BucketDetails": [{"name": "manifestflow-manifests"}],
    "accessKeyDetails": {"principalId": "AROAEXAMPLE:manifestflow-worker-role", "userType": "AssumedRole"}
  },
  "service": {"action": {"awsApiCallAction": {"api": "GetObject", "count": 214}}}
}
```

**QUESTION_TEXT:**
Which principal does this finding implicate, and what specific behavior triggered it?

**OPTIONS:**
- [x] A: The `manifestflow-worker-role` assumed role, flagged for an unusual volume (214) of `GetObject` calls against the `manifestflow-manifests` bucket
- [ ] B: An anonymous, unauthenticated caller with no identifiable principal
- [ ] C: The AWS account root user, flagged for a billing anomaly
- [ ] D: `deploy-pipeline-role`, flagged for a failed deployment
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`accessKeyDetails.principalId` names `manifestflow-worker-role` as an assumed role, and `service.action.awsApiCallAction` shows 214 `GetObject` calls as the specific triggering behavior.
**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [guardduty-finding-fields, principal-identification, api-call-count]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why S3 data events are off by default
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why are CloudTrail S3 data events off by default, unlike CloudTrail's management events?

**OPTIONS:**
- [x] A: Data events capture object-level operations (every GetObject/PutObject), which produce far higher volume and cost than management events, so they must be explicitly enabled per resource
- [ ] B: AWS considers data events a security risk and disables them by policy
- [ ] C: Data events are a paid add-on that requires a separate AWS support contract
- [ ] D: Data events only work for DynamoDB, not S3, so they are irrelevant here by default
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this directly — the volume and cost of logging every object-level operation is why data events require explicit, per-resource opt-in unlike always-on management events.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [cloudtrail-data-events, volume-cost-tradeoff, opt-in-logging]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What CloudTrail adds beyond the GuardDuty finding
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The GuardDuty finding already names the bucket, the principal, and a call count. What does correlating it with the CloudTrail S3 data events add that the finding alone does not provide?

**OPTIONS:**
- [x] A: The exact per-call detail — specific timestamps, source IP for each call, and whether each individual call succeeded — turning a summary alert into a full, attributable timeline
- [ ] B: CloudTrail data events duplicate exactly what GuardDuty already reports, adding no new information
- [ ] C: CloudTrail can retroactively change the GuardDuty finding's severity score
- [ ] D: CloudTrail is required before GuardDuty can generate any finding at all
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's stated payoff is exactly this — GuardDuty gives the alert and summary, CloudTrail data events give the granular per-call timeline needed for full attribution.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [guardduty-cloudtrail-correlation, incident-timeline, per-call-detail]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Reading the CloudTrail event-selector configuration
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```bash
aws cloudtrail put-event-selectors --trail-name manifestflow-org-trail \
  --event-selectors '[{
    "ReadWriteType": "All", "IncludeManagementEvents": true,
    "DataResources": [{"Type": "AWS::S3::Object", "Values": ["arn:aws:s3:::manifestflow-manifests/"]}]
  }]'
```

**QUESTION_TEXT:**
What is the scope of the S3 data events this command enables?

**OPTIONS:**
- [x] A: Only object-level events for the `manifestflow-manifests` bucket specifically, not every S3 bucket in the account
- [ ] B: Every S3 bucket in the account, since data events cannot be scoped to a single bucket
- [ ] C: Only write events (`PutObject`); read events are excluded by `ReadWriteType: All`
- [ ] D: Only events triggered by `manifestflow-worker-role`, excluding all other principals
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`DataResources` names the specific bucket ARN, scoping the (costly) data events to just this one sensitive bucket rather than every bucket in the account — matching the lesson's stated volume/cost trade-off reasoning.
**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [cloudtrail-event-selectors, per-bucket-scoping, data-resources]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why the automated response should stop short of permanent action
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The Suggested Extension proposes an EventBridge-triggered Lambda that revokes a principal's active sessions automatically on a high-severity GuardDuty finding, but still requires a human to confirm before permanently disabling that principal. Why keep that second step manual?

**OPTIONS:**
- [x] A: Revoking active sessions is a fast, reversible containment step with low cost if the finding turns out to be a false positive, while permanently disabling a principal is a higher-cost, harder-to-reverse action that benefits from human judgment before being taken
- [ ] B: AWS Lambda is technically incapable of calling `iam:DeleteRole` or similar disabling actions
- [ ] C: EventBridge cannot trigger two Lambda actions from a single finding
- [ ] D: There is no real reason; full automation would be strictly better
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The reasoning is a cost/reversibility trade-off — automating the cheap, reversible first response while keeping the higher-cost, harder-to-reverse action gated on human confirmation.
**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [automated-response, human-in-the-loop, containment-vs-remediation]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 17

```yaml
lesson_id: fde-elective-aws-multi-region-cloud-deep-dive-17-aws-security-hands-on
lesson_title: "AWS Security Hands-on"
lesson_order: 17

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-aws-multi-region-cloud-deep-dive
module_name: "AWS Multi-Region Cloud Deep Dive (Elective)"
module_order: "Elective 2"

difficulty: Hard
estimated_minutes: 120
content_status: Draft

learning_outcomes:
  - "Run a structured security review against a deployed system distinguishing implemented, tested, and residual-risk controls, using IAM Access Analyzer output as evidence rather than a self-report."
  - "Simulate a credential-compromise incident end to end — detect via GuardDuty, contain via session revocation, and verify via CloudTrail that the access path is actually closed."
  - "Defend a specific security trade-off (what was fixed first, and why something else was accepted as residual risk) under direct customer questioning."

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
# AWS Security Hands-on

## Concepts Covered

A security review's output is only useful if it distinguishes three genuinely different claims:
**implemented** (the control exists — a policy is attached, an endpoint is created), **tested**
(the control was actually exercised and observed to hold — a denied-flow test timed out as
expected, a scoped IAM policy actually rejected the out-of-scope action under
`simulate-principal-policy`), and **residual risk** (a gap the team knows about, has not closed,
and has consciously accepted for a stated reason, with a named owner and a target date). Conflating
"implemented" with "tested" is the specific failure the DispatchWorks review below finds:
`notification-service`'s role was encrypted correctly and had a reasonable-looking policy attached,
but nobody had ever actually attempted the denied action to confirm the policy held — it turned out
to still carry a stale, unused `s3:*` statement from an earlier iteration that the "policy looks
fine" review missed and only a `simulate-principal-policy` run against every listed action would
have caught. **IAM Access Analyzer** automates part of this: it continuously evaluates every
resource-based policy and role-trust-policy in the account against what it can prove about external
or cross-account access, and reports specific findings (a role trust policy that grants access to an
external principal, a bucket policy that is more permissive than its own analysis expected) — using
its findings as evidence in a review is stronger than a manual read-through, because Access Analyzer
is checking the policy's actual logical implications, not just its apparent intent.

An end-to-end incident simulation exercises detection, containment, and verification as three
distinct, ordered steps, and a review that only tests one of them has not actually proven the
incident path works. **Detection**: a deliberately generated signal (a credential used from an
unexpected source, an unusual `GetObject` volume) must actually produce a GuardDuty finding within
a reasonable window — if it does not, the detection layer is broken regardless of how good the
IAM policy looks. **Containment**: the response — typically revoking the compromised principal's
active sessions via `aws sts` or, for a long-lived key, deactivating it via `aws iam
update-access-key` — must actually stop further access, not just look like it did; the only way to
know is to attempt the same action again immediately afterward and confirm it now fails.
**Verification**: CloudTrail is the evidence that containment held — a `lookup-events` query for
the compromised principal, run for the period after containment, should show either nothing or a
string of `AccessDenied` errors, and a single successful call in that window means containment
did not actually work and the review is not finished. The final artifact a customer-facing review
produces is not a list of fixes — it is a short, specific defense of sequencing: which finding was
fixed first and why, which was accepted as residual risk and why, and what evidence (not
assertion) backs each claim, because a customer's own security team will ask exactly these
questions and "we fixed everything" is never itself a credible answer.

```bash
# Access Analyzer finding — a stale statement the manual review missed
aws accessanalyzer list-findings --analyzer-arn arn:aws:access-analyzer:us-east-1:111122223333:analyzer/dispatchworks-analyzer \
  --filter '{"status": {"eq": ["ACTIVE"]}}' \
  --query 'findings[].{Resource:resource,Action:action,IsPublic:isPublic,Condition:condition}'
# -> [{"Resource": "arn:aws:s3:::dispatchworks-audit-exports", "Action": ["s3:*"],
#      "IsPublic": false, "Condition": {}}]
#    ^ notification-service-role's stale s3:* statement, unscoped by any Condition — a manual read caught none of this

# End-to-end incident simulation: compromise a credential, detect, contain, verify
aws sts get-caller-identity --profile compromised-test-cred
# 1) DETECT — trigger an unusual access pattern, confirm GuardDuty produces a finding within minutes
aws guardduty list-findings --detector-id d0abc123 \
  --finding-criteria '{"Criterion": {"resource.accessKeyDetails.principalId": {"Eq": ["AIDAEXAMPLECOMPROMISED"]}}}'

# 2) CONTAIN — revoke the compromised role's active sessions
aws iam put-role-policy --role-name notification-service-role --policy-name deny-all-emergency \
  --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Deny","Action":"*","Resource":"*"}]}'

# 3) VERIFY — the same call that worked before containment must now fail
aws s3 ls s3://dispatchworks-audit-exports --profile compromised-test-cred
# -> An error occurred (AccessDenied) when calling the ListObjectsV2 operation
```

## Practical Backend Scenario

Lighthouse's security team reviews DispatchWorks before general rollout and finds a familiar gap:
`notification-service-role` is KMS-encrypted correctly and its policy "looks fine" in a manual
read, but the team has never actually attempted a denied action against it. Running Access
Analyzer surfaces the stale `s3:*` statement above — a leftover from an early prototype iteration
that the manual review missed entirely, over-privileging the role to every object in an unrelated
audit-exports bucket. The FDE fixes the policy, then runs the full incident simulation: using a
disposable test credential standing in for the same role, the FDE generates an access pattern
GuardDuty flags within four minutes, contains it by attaching an explicit deny-all emergency
policy, and verifies with a repeated `aws s3 ls` call that the same action that worked pre-
containment now returns `AccessDenied`. The final review presents Lighthouse with three columns —
implemented, tested, residual risk — rather than a single "done" checklist, and names one accepted
residual risk explicitly: `booking-service`'s development environment still uses a broader IAM
policy than production, accepted because the environment has no production data and the fix is
scheduled for the next sprint, not because it was overlooked.

## Practice Loop

1. Run `aws accessanalyzer list-findings` against every role in the DispatchWorks account and
   list every finding naming a wildcard action or an unexpected external principal, cross-checking
   each one against what that role's owning service actually calls.
2. Fix the highest-risk finding (the stale `s3:*` statement) by removing it, then re-run
   `simulate-principal-policy` for the specific action the role previously had and confirm it is
   now denied.
3. Diagnostic: for every control in the review, mark it implemented, tested, or residual risk —
   count how many controls were previously assumed "done" but had never actually been tested, since
   this count is the review's central finding.
4. Run the three-step incident simulation (detect via GuardDuty, contain via the deny-all policy,
   verify via a repeated denied call) against a disposable test credential, and time how long
   detection took from the triggering action to the GuardDuty finding appearing.
5. Write the one-page findings summary with the three-column implemented/tested/residual-risk
   table, naming an explicit owner and target date for every residual-risk row.

## Evidence of Understanding

You can run a security review that distinguishes implemented, tested, and residual-risk controls,
using IAM Access Analyzer findings as evidence rather than a manual policy read-through, and you
can name a specific case where "looks fine" and "actually tested" produced different answers. You
can simulate a credential-compromise incident through detection, containment, and verification as
three distinct steps, and prove containment held by showing the exact same action fails after your
response that succeeded before it. You can present a security review's findings as a defensible
sequencing decision — what was fixed first, what was accepted as residual risk and why, with a
named owner — rather than an unqualified "it's secure" claim.

## Suggested Extension

Schedule the Access Analyzer scan and the three-column implemented/tested/residual-risk review as
a recurring monthly job (an EventBridge-triggered Lambda that runs the scan and posts a summary to
a security review channel), and explain why a security review that only happens once, at launch, is
insufficient for a system that keeps shipping new services and IAM roles after that first review.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Implemented vs. tested vs. residual risk
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what is the difference between a control being "implemented" and a control being "tested"?

**OPTIONS:**
- [x] A: Implemented means the control exists (a policy is attached); tested means the control was actually exercised and observed to hold under a real attempt, such as a denied action actually being denied
- [ ] B: The two terms are interchangeable in the lesson's framing
- [ ] C: "Tested" only applies to network controls, never to IAM policies
- [ ] D: A control can only be "tested" after it has been marked as residual risk
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's opening distinction is exactly this — existence versus verified behavior under an actual attempt, which is the gap that let the stale `s3:*` statement go unnoticed.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [implemented-vs-tested, residual-risk, security-review-taxonomy]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What Access Analyzer actually evaluates
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson consider an IAM Access Analyzer finding stronger evidence than a manual policy read-through?

**OPTIONS:**
- [x] A: Access Analyzer checks a policy's actual logical implications for external or cross-account access, rather than relying on a reviewer's read of the policy's apparent intent
- [ ] B: Access Analyzer replaces the need for IAM policies entirely
- [ ] C: A manual read-through is always faster, so Access Analyzer is only used when time allows
- [ ] D: Access Analyzer only checks network configuration, not IAM policies
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this precisely — Access Analyzer evaluates logical implications of a policy, which is exactly what a manual read missed with the stale `s3:*` statement.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [access-analyzer, policy-analysis, evidence-based-review]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the Access Analyzer finding
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**CODE_BLOCK:**
```json
[{"Resource": "arn:aws:s3:::dispatchworks-audit-exports", "Action": ["s3:*"],
  "IsPublic": false, "Condition": {}}]
```

**QUESTION_TEXT:**
What does this Access Analyzer finding reveal about `notification-service-role`'s policy?

**OPTIONS:**
- [x] A: It holds an unscoped `s3:*` statement against the `dispatchworks-audit-exports` bucket, with no `Condition` narrowing it — an over-privileged, leftover grant a manual read missed
- [ ] B: The bucket is publicly accessible to the entire internet
- [ ] C: The finding indicates the role has no access to S3 at all
- [ ] D: The finding is a false positive that requires no action
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
`IsPublic: false` rules out public exposure, but the unscoped `s3:*` action with an empty `Condition` is exactly the stale, over-privileged leftover statement the scenario describes.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [access-analyzer-finding, stale-permission, unscoped-action]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why containment must be re-tested, not just applied
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why is attaching the deny-all emergency policy not, by itself, sufficient evidence that containment worked?

**OPTIONS:**
- [x] A: The only way to know containment actually stopped access is to attempt the same action again immediately afterward and confirm it now fails — applying a policy is not the same claim as verifying its effect
- [ ] B: IAM deny policies technically take up to 24 hours to propagate, so no verification is possible sooner
- [ ] C: Deny-all policies are known to be unreliable and should never be used for containment
- [ ] D: There is no need to re-test; attaching the policy is sufficient proof on its own
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's containment step explicitly requires re-attempting the action to confirm the deny actually took effect — matching its broader implemented-vs-tested distinction applied to this specific step.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [containment-verification, deny-all-policy, incident-response]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What a successful call after containment would mean
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
During the verification step, the CloudTrail `lookup-events` query for the compromised principal, run after containment, shows one successful `GetObject` call in the post-containment window. What does the lesson say this means?

**OPTIONS:**
- [x] A: Containment did not actually work and the review is not finished — a single successful call in that window disproves the claim that access was closed
- [ ] B: One successful call is expected and acceptable as long as most subsequent calls are denied
- [ ] C: The successful call must be a CloudTrail logging error, not a real access event
- [ ] D: This result has no bearing on whether containment succeeded
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson states this as an unambiguous verification standard — any successful call after containment invalidates the claim that access was closed, not merely a partial success to be tolerated.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [verification-standard, cloudtrail-evidence, containment-failure]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the residual-risk row needs an owner and date
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson require every residual-risk row in the final review to name an explicit owner and target date, rather than just listing the gap?

**OPTIONS:**
- [x] A: Without an owner and date, "accepted residual risk" is indistinguishable from a gap that was simply overlooked and forgotten, undermining the credibility of the review's other claims
- [ ] B: AWS requires this information for compliance purposes on every account
- [ ] C: The owner and date fields are only cosmetic formatting with no substantive purpose
- [ ] D: A residual risk without an owner automatically becomes a tested control
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's scenario explicitly distinguishes an accepted, owned, dated risk (the dev-environment IAM gap) from something merely overlooked — the owner and date are what make that distinction credible.
**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [residual-risk-ownership, review-credibility, accepted-risk]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why "we fixed everything" is not a credible answer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, why is "we fixed everything" insufficient when a customer's security team asks about a review's findings?

**OPTIONS:**
- [x] A: A customer's security team will ask specifically which finding was fixed first and why, and which was accepted as residual risk and why — an unqualified claim provides no sequencing rationale or evidence to answer either question
- [ ] B: It is factually always false; no security review can ever fix every finding
- [ ] C: Customers legally require a minimum number of residual risks to be reported
- [ ] D: The phrase is too short to be considered a proper review deliverable
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson names the specific questions a customer's security team will ask — sequencing and evidence — which an unqualified "fixed everything" claim does not answer.
**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [customer-facing-review, sequencing-defense, evidence-based-claims]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Detection timing as part of the simulation's evidence
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Practice Loop step 4 has the FDE time how long detection took from the triggering action to the GuardDuty finding appearing. Why is this measurement part of the review's evidence, not just an interesting side note?

**OPTIONS:**
- [x] A: It proves the detection layer works within a reasonable, real window — if detection took hours instead of minutes, the review would need to flag that latency as its own residual risk rather than assume detection "works" in the abstract
- [ ] B: AWS bills GuardDuty based on how long a finding takes to appear
- [ ] C: Detection timing has no bearing on the review; only whether a finding eventually appears matters
- [ ] D: The timing measurement is only useful for the containment step, not detection
**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0
**EXPLANATION:**
The lesson's framing treats detection as one of three steps that must each be verified, not assumed — a slow detection window is itself a finding the review should surface, not a detail to skip past.
**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [detection-latency, incident-simulation-evidence, guardduty-timing]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->
