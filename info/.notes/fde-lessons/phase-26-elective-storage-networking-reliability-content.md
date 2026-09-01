# FDE Phase 26 — Elective "Storage, Networking & Reliability for FDEs" (Lessons 1-7 of 14)

Seven lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-26-elective-storage-networking-reliability-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `elective-storage-networking-reliability` ("Storage, Networking
& Reliability for FDEs")

This is the **first phase of the THIRD and FINAL elective module**, applied after both the
Containerization/K8s elective (17 lessons, Phases 20-22) and the AWS Multi-Region elective (17
lessons, Phases 23-25) are fully complete. This file covers **lessons 1-7 of 14 only**. A later
phase (27) covers lessons 8-14 (Edge Caching/CDNs, Microservices Performance, Multi-Region
Active-Active, Fault Tolerance Engineering, Graceful Degradation, Rate Limiting/Throttling, Data
Consistency Trade-offs: CAP and PACELC) and completes this module — do not add placeholder content
for those 7 lessons here. Once Phase 27 lands, the entire ~152-lesson FDE curriculum (104 core +
17 + 17 + 14 elective) is complete.

**Overlap-avoidance notes (checked against prior phases before writing):**
- Lessons 1-3 (storage architecture, lifecycle, backup/DR) deliberately stay on operational
  infrastructure storage — EBS volume types, S3 storage classes and lifecycle rules, snapshot and
  restore mechanics — rather than re-teaching Postgres internals, NoSQL, or vector-DB material
  already covered in Module 2 (`backend-observability-data`, Phases 5-7) or the RDS/S3/SQS basics
  already covered in Module 4 Phase 9 lesson 2 ("Compute, Storage & Managed Services"). Where this
  file touches S3 or EBS, it goes one level deeper (storage-class transition mechanics, IOPS/
  throughput provisioning trade-offs with real pricing, snapshot/DLM automation) than that prior
  coverage.
- Lesson 4 (application networking design) deliberately does not re-teach VPC/subnet/route-table/
  security-group mechanics — those are covered in depth in Module 4 (Phases 9-10) and, AWS-
  specifically, in `elective-aws-multi-region-cloud-deep-dive` lessons 1-2 (Phase 23). This lesson
  instead works one level up: which application tier belongs in which subnet, where the load
  balancer sits relative to each tier, and how a request's trust boundary changes as it crosses
  tiers — assuming subnet/route-table mechanics as background, not re-explaining them.
- Lesson 7 (sharding) deliberately focuses on shard-key selection mechanics, hot-spot quantification,
  and resharding — not the tenant-isolation architectural framing already covered in
  `system-design-capstone` Phase 17 lesson 4 ("System Design: Multi-Tenant SaaS Platform").

All seven lessons follow one continuous scenario: an FDE engagement for **Kestrel Underwriting**, a
regional insurance MGA. The deliverable is **PolicyVault**, a multi-tenant SaaS platform that
stores policy documents, endorsements, and claims photos for independent underwriting agencies,
tracks policy and claim status transactionally, and must satisfy a seven-year regulatory retention
requirement with an auditable trail. The FDE builds PolicyVault's storage, network, and scaling
foundation from first principles, with a live customer requirement — durable binaries, transactional
status, searchable metadata, and provable recoverability — driving every design decision.

---

# LESSON 1

```yaml
lesson_id: fde-elective-storage-networking-reliability-01-architect-the-storage-for-an-application
lesson_title: "Architect the Storage for an Application"
lesson_order: 1

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-storage-networking-reliability
module_name: "Storage, Networking & Reliability for FDEs (Elective)"
module_order: "Elective 3"

difficulty: Intermediate
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Map a data class to a storage service (object, block, or file) by its actual access pattern and durability need, not by habit or by what is already provisioned."
  - "Choose between EBS gp3 and io2 Block Express by workload IOPS/throughput requirements and real per-GB and per-IOPS pricing, rather than a default volume type."
  - "Build a storage decision matrix that names, for every data class in a system, what happens when its backing store is unavailable."

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
# Architect the Storage for an Application

## Concepts Covered

Object, block, and file storage are not interchangeable options ranked by convenience — each has a
distinct access contract that determines which workloads it can serve correctly. Object storage
(S3) exposes a flat namespace of immutable-per-version objects addressed by key, written and read
whole through an HTTP API (`PutObject`/`GetObject`); there is no in-place partial-byte edit, no
POSIX file handle, and no guaranteed low-latency random access — which is exactly right for a policy
PDF or a claims photo that is written once and read whole, and exactly wrong for a database's
write-ahead log. Block storage (EBS) is a raw, low-latency block device attached to a single EC2
instance (except io2 Block Express volumes, which support Multi-Attach across up to 16 instances in
the same Availability Zone) — the OS lays a filesystem on top of it, and it is the only one of the
three that can serve the small, random, latency-sensitive read/write pattern a relational database's
storage engine actually generates. File storage (EFS) is a shared, POSIX-compliant filesystem
mounted concurrently by many instances over NFS — the right choice when multiple compute nodes need
to see the same mutable file tree at once, which object storage's whole-object model cannot provide
and block storage's single-attach model (io2 Multi-Attach aside) does not either.

The concrete decision is IOPS and throughput per dollar, not "SSD versus HDD." A `gp3` EBS volume
provisions a 3,000 IOPS / 125 MiB/s baseline at $0.08/GB-month regardless of volume size, with
additional IOPS purchasable up to 16,000 at $0.005/IOPS-month and additional throughput up to 1,000
MiB/s at $0.04/MiB/s-month — decoupled from volume size, which is the change from the older `gp2`
family, where IOPS scaled with size and a small volume could not be provisioned for high IOPS at
all. An `io2` Block Express volume goes further, to 256,000 IOPS and 4,000 MiB/s per volume, at
$0.125/GB-month plus $0.065 per provisioned IOPS-month — an order of magnitude more expensive per
IOPS than gp3's purchasable tier, which only makes sense once a workload's actual measured IOPS
requirement, not an assumed one, exceeds what gp3 can provision. S3 storage classes make the
equivalent trade differently: S3 Standard is $0.023/GB-month with no retrieval fee and millisecond
first-byte latency; S3 has no per-request minimum storage duration. Choosing wrong in either
direction — over-provisioning io2 for a workload gp3 would serve, or under-provisioning IOPS for a
database whose real write pattern was never measured — is a cost or an outage waiting to surface
under load, not a stylistic preference.

```hcl
resource "aws_ebs_volume" "policyvault_db_data" {
  availability_zone = "us-east-1a"
  size              = 200
  type              = "gp3"
  iops              = 6000     # above the 3000 baseline, purchased explicitly
  throughput        = 250      # MiB/s, above the 125 baseline
  encrypted         = true

  tags = { Name = "policyvault-primary-db-data" }
}

resource "aws_s3_bucket" "policyvault_documents" {
  bucket = "kestrel-policyvault-documents-prod"
}

resource "aws_s3_bucket_versioning" "policyvault_documents" {
  bucket = aws_s3_bucket.policyvault_documents.id
  versioning_configuration { status = "Enabled" }
}
```

Encryption is a property of the storage layer, not a separate system, and it should be decided at
the same time as the storage class rather than bolted on afterward: EBS volumes and S3 objects both
support encryption at rest transparently, using either an AWS-managed key or a customer-managed KMS
key, with no application-level code change required to read or write encrypted data — the encryption
happens below the API the application already calls. The reason to choose a customer-managed KMS
key over the AWS-managed default is auditability and revocation: a customer-managed key appears in
CloudTrail with every `Encrypt`/`Decrypt` call attributable to a specific principal, and it can be
disabled or have its key policy tightened independently of the data it protects, which an
AWS-managed key does not expose. This decision belongs in the same sitting as the object/block/file
choice, because retrofitting encryption onto an existing unencrypted EBS volume requires creating a
new encrypted volume from a snapshot and cutting over, not a live in-place change — exactly the kind
of retrofit cost that argues for deciding storage properties once, deliberately, at provisioning
time rather than accepting a default and revisiting it under pressure later.

## Practical Backend Scenario

Kestrel Underwriting's PolicyVault stores four distinct data classes for each tenant agency, and the
FDE maps each to a different backing store rather than defaulting everything to one. Policy PDFs,
endorsement documents, and claims photos — written once, read occasionally, never partially
modified — go into S3 with versioning enabled, so an accidental overwrite (a broker re-uploading a
corrected policy under the same object key) is recoverable from a prior version instead of a
destructive in-place edit. Policy and claim status — actively updated multiple times a day per
active claim, queried by primary key and by adjuster, and requiring transactional consistency when
a claim moves from "under review" to "approved" — goes into RDS for PostgreSQL on a `gp3` EBS
volume provisioned at 6,000 IOPS after a load test showed the default 3,000 baseline caused write
latency spikes during month-end batch premium recalculation. Searchable policy metadata (insured
name, policy number, effective dates, tags) that underwriters filter and full-text search across
goes into a Postgres `GIN` index on a `tsvector` column in the same RDS instance, rather than a
separate search service, since query volume never justified the added operational surface. The
seven-year regulatory audit trail — write-once records of every status change and document access —
goes into a second, append-only S3 prefix with Object Lock in compliance mode, so no principal,
including an account administrator, can delete or overwrite an audit record before its retention
period expires.

## Practice Loop

1. Create a storage decision matrix listing PolicyVault's four data classes (documents, status,
   metadata, audit trail) as rows and access pattern, durability need, and consistency need as
   columns.
2. Map each row to a specific AWS storage service (S3 Standard, RDS/EBS gp3, S3 with Object Lock)
   and write one sentence justifying why the alternative services were rejected for that row.
3. Measure the actual IOPS your policy-status database workload generates under a realistic load
   test (month-end batch recalculation plus live adjuster traffic), and compare that measured
   figure against gp3's 3,000-IOPS baseline to decide whether additional provisioned IOPS is
   actually justified.
4. Test one read, one write, one backup, and one restore assumption for each storage class in the
   matrix — for example, confirm an S3 versioned object can actually be recovered to a prior
   version, not just that versioning is "enabled."
5. For each row in the matrix, write one sentence stating what happens to that specific workflow
   (claim approval, document upload, audit lookup) if that store becomes unavailable, and whether
   the failure is visible to the tenant or silently degraded.

## Evidence of Understanding

You can map a data class to object, block, or file storage by its actual access pattern rather than
convention, and explain precisely why a database's storage engine needs block storage's random-I/O
contract while a policy PDF does not. You can choose between gp3 and io2 Block Express using a
measured IOPS requirement and the real per-GB and per-IOPS pricing, rather than an assumed default.
You can produce a storage decision matrix that states, for every data class in a system, what
happens to the dependent workflow when that store is unavailable.

## Suggested Extension

Add a fifth data class to PolicyVault — real-time underwriting-decision audit events streamed from
a rules engine — and decide whether it belongs in the existing RDS instance, a new time-series
store, or S3, justified by its actual write rate and query pattern rather than by convenience.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Object storage's access contract
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why is S3 the wrong backing store for a relational database's write-ahead log, per the lesson's
distinction between object and block storage?

**OPTIONS:**
- [x] A: S3's access contract is whole-object PUT and GET over HTTP with no in-place partial-byte edit and no guaranteed low-latency random access, while a WAL needs small, low-latency, sequential appends a block device provides
- [ ] B: S3 objects are not durable enough for a database's write-ahead log
- [ ] C: S3 does not support versioning, which a write-ahead log requires
- [ ] D: S3 is more expensive per GB than EBS in every region

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's distinction is about access contract, not durability or cost — object storage's
whole-object model cannot serve the low-latency append pattern a WAL generates.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [object-storage, block-storage, wal, access-pattern]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** gp3 versus io2 Block Express
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given the Terraform snippet in the lesson provisioning a `gp3` volume at 6,000 IOPS, under what
condition would switching to `io2` Block Express actually be justified?

**CODE_BLOCK:**
```hcl
resource "aws_ebs_volume" "policyvault_db_data" {
  size       = 200
  type       = "gp3"
  iops       = 6000
  throughput = 250
}
```

**OPTIONS:**
- [ ] A: io2 should always be preferred over gp3 regardless of measured workload, since it is a newer volume type
- [x] B: Only once a measured workload requirement exceeds what gp3 can provision (up to 16,000 IOPS / 1,000 MiB/s) — io2's per-IOPS price is an order of magnitude higher, so it only makes sense past gp3's ceiling
- [ ] C: io2 is required whenever a volume is attached to a database instance, regardless of IOPS
- [ ] D: gp3 cannot be encrypted, so io2 is required for any regulated workload like PolicyVault's

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson states io2's per-IOPS cost is roughly an order of magnitude higher than gp3's, so the
switch is justified only once a measured requirement exceeds gp3's provisionable ceiling, not by
volume type preference alone.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [gp3, io2, iops-pricing, capacity-planning]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why EFS exists distinct from S3 and EBS
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What access pattern does EFS serve that neither S3 nor a standard EBS volume can serve correctly?

**OPTIONS:**
- [ ] A: Storing large binary objects durably for occasional whole-file reads
- [ ] B: Providing the lowest possible per-request latency for a single-instance database
- [x] C: Multiple compute instances mounting the same mutable, POSIX-compliant file tree concurrently over NFS
- [ ] D: Immutable, write-once-read-many archival storage with the lowest per-GB cost

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
EFS's distinguishing capability is concurrent multi-instance mount of a shared mutable filesystem —
object storage's whole-object model and standard EBS's single-attach model cannot provide that.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [efs, file-storage, shared-mount]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why versioning, not a separate backup, protects against the accidental overwrite in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the PolicyVault scenario, a broker re-uploads a corrected policy PDF under the same S3 object
key, overwriting the original. What makes this recoverable?

**OPTIONS:**
- [x] A: S3 versioning was enabled on the bucket, so the overwrite creates a new version rather than destroying the prior one, and the prior version can be restored
- [ ] B: S3 objects cannot actually be overwritten once written, regardless of configuration
- [ ] C: The FDE configured a nightly snapshot of the S3 bucket that captured the prior state
- [ ] D: S3's eleven-nines durability guarantee prevents any object from ever being lost or changed

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Versioning is the specific mechanism the scenario relies on — an overwrite becomes a new version,
not a destructive edit, which is why the prior version is recoverable.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [s3-versioning, recoverability]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Object Lock compliance mode's guarantee
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
PolicyVault's seven-year audit trail uses S3 Object Lock in compliance mode. What does this
specifically guarantee that plain versioning alone does not?

**OPTIONS:**
- [x] A: No principal, including an account administrator, can delete or overwrite the locked object version before its retention period expires
- [ ] B: The audit records are automatically encrypted with a customer-managed KMS key
- [ ] C: The audit records are replicated to a second AWS region automatically
- [ ] D: The audit records become searchable via full-text query without a separate index

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Compliance mode's distinguishing property over plain versioning is that deletion or overwrite is
blocked for every principal, including root/admin, until retention expires — this is what a
regulatory retention requirement actually needs.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [object-lock, compliance-mode, retention]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** The point of Practice Loop step 3
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the Practice Loop ask you to measure actual IOPS under a realistic load test before
deciding whether additional provisioned IOPS is justified, rather than provisioning a higher figure
up front?

**OPTIONS:**
- [x] A: Provisioning IOPS beyond what the workload actually needs is a real, ongoing cost, and the only way to know whether the gp3 baseline is insufficient is to measure the actual workload, not assume it
- [ ] B: AWS caps the maximum IOPS a newly created volume can request without a prior measurement on file
- [ ] C: Load testing is required by AWS before any gp3 volume can be provisioned above baseline
- [ ] D: Measuring IOPS is only relevant for io2 volumes, not gp3

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the diagnostic step of the loop — it makes the cost of over- or under-provisioning
concrete by grounding the IOPS decision in a measured figure rather than an assumption.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [capacity-measurement, iops-provisioning]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What a storage decision matrix must state per row
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's Evidence of Understanding, what must a correct storage decision matrix state for
every data class, beyond which service it maps to?

**OPTIONS:**
- [ ] A: The exact dollar cost per month for that data class's storage
- [x] B: What happens to the dependent workflow when that specific store is unavailable
- [ ] C: The names of every engineer who approved the storage choice
- [ ] D: A comparison against every AWS storage service that was not chosen

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson's evidence bar is explicit: a correct matrix explains why each datum lives where it
does AND what happens when that store is unavailable, not merely a service mapping.

**LESSON_CONNECTION:** Evidence of Understanding
**KEYWORDS:** [decision-matrix, failure-mode]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** gp3 versus the older gp2 family
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What changed with gp3 relative to the older gp2 EBS volume family, per the lesson?

**OPTIONS:**
- [x] A: IOPS and throughput are provisioned independently of volume size, whereas gp2's IOPS scaled with volume size, making a small gp2 volume unable to reach high IOPS at all
- [ ] B: gp3 volumes can no longer be encrypted at rest
- [ ] C: gp3 removed the ability to resize a volume without downtime
- [ ] D: gp3 is only available for Multi-Attach configurations, unlike gp2

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson calls this out specifically: gp3 decouples IOPS/throughput from size, fixing gp2's
limitation where a small volume could not be provisioned for high IOPS.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [gp3, gp2, iops-decoupling]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 2

```yaml
lesson_id: fde-elective-storage-networking-reliability-02-data-lifecycle-management-and-storage-optimization
lesson_title: "Data Lifecycle Management and Storage Optimization"
lesson_order: 2

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-storage-networking-reliability
module_name: "Storage, Networking & Reliability for FDEs (Elective)"
module_order: "Elective 3"

difficulty: Intermediate
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Write an S3 lifecycle policy that transitions and expires objects by observed access pattern, and explain the retrieval-cost trade-off of each storage class it transitions through."
  - "Distinguish a retention hold that must block automatic deletion from ordinary lifecycle-managed data, and implement that distinction rather than exempting data by hand."
  - "Attribute storage cost to a specific data class and tenant, and use that attribution to find and fix an unbounded-growth source."

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
# Data Lifecycle Management and Storage Optimization

## Concepts Covered

Data lifecycle management is the discipline of making the transition from hot to warm to cold to
deleted an explicit, automated, observable policy rather than a fact nobody tracked. S3 lifecycle
rules operate on object age (or a tag-based filter) and move an object between storage classes on a
schedule: S3 Standard ($0.023/GB-month, millisecond access, no retrieval fee) to S3 Standard-IA
($0.0125/GB-month, same millisecond access, but a $0.01/GB retrieval fee and a 30-day minimum
storage duration charge) to S3 Glacier Flexible Retrieval ($0.0036/GB-month, retrieval in minutes
to hours depending on tier, with its own retrieval fee) to S3 Glacier Deep Archive ($0.00099/GB-
month, 12-hour standard retrieval). The trade is always the same shape — lower per-GB storage cost
in exchange for a retrieval fee and higher retrieval latency — which means a lifecycle rule is only
correct if it is built from the object's actual access pattern (how often is a document class
genuinely re-read after 30, 90, or 365 days) rather than a guess; transitioning frequently-accessed
data into Glacier trades a small storage saving for a large, recurring retrieval cost and a support
ticket every time a user needs a document "immediately."

Lifecycle management is inseparable from retention correctness: an expiration rule that deletes
data unconditionally at 90 days is wrong the moment a legal hold, an active claim, or a regulatory
retention requirement applies to a specific object, which is why a lifecycle policy needs an
explicit exception path — tag-based exclusion, S3 Object Lock, or a separate "held" prefix the
lifecycle rule's filter does not match — rather than a human manually pulling flagged objects out of
the deletion queue before each run. Cost attribution closes the loop: S3 Storage Lens and per-prefix
or per-tag cost allocation let you answer "which tenant's data is actually driving this month's
storage bill" instead of only seeing an aggregate total, which is the only way to catch the common
failure mode where a temporary export or an old document version nobody ever intended to keep
accumulates silently because no lifecycle rule or attribution tag was ever applied to that prefix.

```json
{
  "Rules": [
    {
      "ID": "policyvault-claims-photos-lifecycle",
      "Filter": { "And": {
        "Prefix": "tenants/",
        "Tags": [{ "Key": "retention-hold", "Value": "false" }]
      }},
      "Status": "Enabled",
      "Transitions": [
        { "Days": 30,  "StorageClass": "STANDARD_IA" },
        { "Days": 180, "StorageClass": "GLACIER" }
      ],
      "NoncurrentVersionTransitions": [
        { "NoncurrentDays": 30, "StorageClass": "GLACIER" }
      ],
      "NoncurrentVersionExpiration": { "NoncurrentDays": 730 }
    }
  ]
}
```

S3 Intelligent-Tiering is a distinct alternative to writing explicit day-based transition rules: it
monitors each object's actual access pattern and moves it automatically between a Frequent Access
tier and an Infrequent Access tier (and, if enabled, Archive Instant Access and deeper archive
tiers) after 30, 90, and up to 180 days without access — for a small monitoring fee, roughly
$0.0025 per 1,000 objects per month, with no retrieval fee at all on the two most common tiers. The
trade-off against a hand-written lifecycle rule is the inverse of the storage-class trade-off
itself: Intelligent-Tiering costs more per object in monitoring overhead but removes the risk of a
wrong access-pattern assumption baked into a static day threshold, which makes it the better default
for a prefix whose access pattern is genuinely unpredictable (documents flagged for occasional
re-review by an underwriter, for instance), while a hand-written rule with explicit day thresholds
remains the better choice for a prefix whose access pattern is well understood and stable, like the
weekly-export prefix in this lesson's scenario, where the correct threshold is already known and
paying a monitoring fee to discover it again adds no value. Partitioning strategy is the parallel
concern on the transactional side of the system: a `claims` table growing without bound degrades
every sequential scan and every index rebuild over time, and range-partitioning it by a natural
lifecycle boundary (policy year, or claim-closed date) lets an old partition be detached and archived
as a unit — a single metadata operation — instead of a row-by-row delete that holds locks and
generates enormous write-ahead-log volume for no equivalent benefit.

## Practical Backend Scenario

Six months into the PolicyVault engagement, Kestrel's monthly S3 bill has grown 40% faster than
tenant count, and nobody can say why. The FDE finds the cause with S3 Storage Lens broken down by
prefix: a batch-export job, run weekly for underwriting analytics, writes a full CSV snapshot of
every active policy to `tenants/{tenant_id}/exports/` and never deletes the prior week's file, so
52 near-duplicate exports accumulate per tenant per year with no lifecycle rule ever applied to that
prefix — because the prefix was added after the original lifecycle policy was written and nobody
updated the filter. The fix has two parts: first, a lifecycle rule scoped to the `exports/` prefix
specifically, expiring objects after 14 days, since no export has ever been referenced by an
underwriter after that window; second, the FDE explicitly checks that the audit-trail prefix (which
must never expire before its seven-year hold) is not accidentally caught by the same broad
`tenants/` prefix filter, so it tags every audit object `retention-hold: true` and adds that tag as
an exclusion filter on every lifecycle rule that touches the `tenants/` prefix, rather than relying
on separate prefixes alone to prevent an accidental future rule from matching audit data.

## Practice Loop

1. Classify every S3 prefix PolicyVault writes to (documents, exports, audit trail) as hot, warm,
   cold, or held, based on its actual observed re-access pattern rather than a guess.
2. For each non-held prefix, define transition and expiration rules with specific day thresholds,
   and justify each threshold with the access-pattern evidence from step 1.
3. Apply the lifecycle policy in a sandbox bucket seeded with objects of varying ages, and confirm
   with `aws s3api list-objects-v2` (checking the `StorageClass` field) that objects actually
   transitioned on schedule rather than only that the rule was accepted.
4. Attempt to delete a tagged `retention-hold: true` object directly, and confirm the deletion is
   rejected — this is the diagnostic step that proves the hold actually blocks deletion rather than
   merely being excluded from the lifecycle rule's filter.
5. Run S3 Storage Lens (or per-prefix cost allocation tags) and produce a cost-by-prefix breakdown
   that shows which prefix is driving the largest share of the bill, and confirm it now matches
   what the lifecycle policy intends to control.

## Evidence of Understanding

You can write an S3 lifecycle policy that transitions and expires objects by their actual access
pattern, and explain the specific retrieval-cost and latency trade-off of each storage class
transition. You can show which data moves, when it is deleted, who can restore it, and how cost is
attributed, using a tag-based exclusion mechanism to keep held data safe from a broad lifecycle
filter rather than relying on prefix separation alone. You can find an unbounded-growth source using
per-prefix cost attribution rather than only observing an aggregate bill increase.

## Suggested Extension

Add a second export type (a nightly incremental delta file, distinct from the weekly full export)
and design its own lifecycle rule, reasoning explicitly about why its retention window should differ
from the weekly export's 14-day rule.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** The shape of the storage-class trade-off
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What trade-off does every S3 storage-class transition (Standard to Standard-IA to Glacier to Deep
Archive) share, per the lesson?

**OPTIONS:**
- [x] A: Lower per-GB storage cost in exchange for a retrieval fee and higher retrieval latency
- [ ] B: Lower durability in exchange for lower storage cost
- [ ] C: Lower storage cost with no other trade-off, since AWS absorbs the retrieval cost
- [ ] D: Higher storage cost in exchange for guaranteed millisecond retrieval at every tier

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson states this as the consistent shape of the trade-off across every storage class
transition — cheaper storage, more expensive and slower retrieval.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [storage-class-transition, retrieval-cost]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why a lifecycle rule needs an explicit exception path
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that an unconditional expiration rule (delete everything at 90 days) is
wrong the moment a legal hold or regulatory retention applies to some objects in that prefix?

**OPTIONS:**
- [x] A: The rule would delete held data along with ordinary data unless an explicit exception path (tag-based exclusion, Object Lock, or a separate prefix the filter does not match) is built in
- [ ] B: AWS technically prevents any lifecycle rule from ever deleting an object under 7 years old
- [ ] C: S3 lifecycle rules cannot operate on tagged objects at all
- [ ] D: A 90-day expiration is always too short for any regulated data regardless of the retention requirement

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's point is mechanism-specific: without an explicit exclusion, a broad expiration rule
has no way to distinguish held objects from ordinary ones and will delete both.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [retention-hold, lifecycle-exception]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the lifecycle policy JSON
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lifecycle policy JSON in the lesson, what happens to a noncurrent (prior) version of an
object 800 days after it became noncurrent?

**CODE_BLOCK:**
```json
"NoncurrentVersionTransitions": [
  { "NoncurrentDays": 30, "StorageClass": "GLACIER" }
],
"NoncurrentVersionExpiration": { "NoncurrentDays": 730 }
```

**OPTIONS:**
- [x] A: It has already been permanently expired (deleted), since 800 days exceeds the 730-day noncurrent expiration threshold
- [ ] B: It transitions to Glacier for the first time at day 800
- [ ] C: It remains in Standard storage since the rule only applies to current versions
- [ ] D: It is restored to Standard-IA automatically after the transition period elapses

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
`NoncurrentVersionExpiration` at 730 days means a noncurrent version is deleted once it has been
noncurrent for 730 days — 800 days exceeds that, so it would already be gone.

**LESSON_CONNECTION:** Concepts Covered, code block
**KEYWORDS:** [noncurrent-version, lifecycle-json, expiration]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Root cause of the 40% bill growth in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What was the actual root cause of PolicyVault's S3 bill growing 40% faster than tenant count?

**OPTIONS:**
- [ ] A: S3 Standard-IA pricing increased for all Kestrel's tenants simultaneously
- [x] B: A weekly batch-export job wrote to a new prefix (`exports/`) that was added after the original lifecycle policy was written, so no rule ever expired the accumulating weekly exports
- [ ] C: Claims photo uploads grew faster than tenant onboarding
- [ ] D: The audit-trail prefix's Object Lock retention period was misconfigured to be permanent

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scenario's root cause is specifically the unmanaged `exports/` prefix accumulating weekly
near-duplicate files with no lifecycle rule ever applied to it.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [cost-growth, unmanaged-prefix]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why the FDE used a tag, not just a separate prefix, to protect audit data
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE add a `retention-hold: true` tag as an exclusion filter, rather than relying on the
audit trail's separate prefix alone to keep it safe from lifecycle rules?

**OPTIONS:**
- [x] A: Prefix separation alone does not prevent a future, broader rule from accidentally matching the audit prefix — the tag makes the exclusion explicit and independent of which prefix a rule happens to target
- [ ] B: S3 lifecycle rules cannot filter by prefix at all, only by tag
- [ ] C: Tags are required by AWS for any object under Object Lock
- [ ] D: The audit trail does not actually use a separate prefix from ordinary tenant documents

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's stated reasoning is defense against a future broad rule — a tag-based exclusion does
not depend on every future rule remembering to exclude the audit prefix by path.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [tag-exclusion, defense-in-depth]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Purpose of Practice Loop step 4
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the Practice Loop have you attempt to delete a `retention-hold: true` object directly,
rather than only confirming it was excluded from the lifecycle rule's filter?

**OPTIONS:**
- [x] A: Being excluded from a lifecycle rule only proves automatic deletion won't happen — it does not prove a direct manual or programmatic delete is actually blocked, which is what a real hold requires
- [ ] B: S3 requires this test before any lifecycle rule can be enabled
- [ ] C: It confirms the object's storage class transitioned correctly
- [ ] D: It measures the retrieval latency of a held object

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the diagnostic step distinguishing "excluded from an automated rule" from "actually
protected against deletion" — only Object Lock's enforcement, tested directly, proves the latter.

**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [object-lock-verification, diagnostic-step]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Standard-IA's retrieval-fee mechanic
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What distinguishes S3 Standard-IA from S3 Standard in terms of access cost, per the lesson's
pricing figures?

**OPTIONS:**
- [x] A: Standard-IA has the same millisecond access latency as Standard, but adds a per-GB retrieval fee and a 30-day minimum storage duration charge
- [ ] B: Standard-IA has retrieval latency measured in hours, unlike Standard's millisecond access
- [ ] C: Standard-IA has no retrieval fee but a higher per-GB storage cost than Standard
- [ ] D: Standard-IA is identical to Standard in every way except a different AWS region requirement

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's figures are specific: Standard-IA keeps Standard's millisecond access but adds a
retrieval fee and a minimum storage duration charge — that is its distinguishing trade.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [standard-ia, retrieval-fee]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What per-prefix cost attribution actually enables
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does per-prefix or per-tag cost attribution (via S3 Storage Lens) let an FDE do that an
aggregate monthly bill total does not?

**OPTIONS:**
- [x] A: Identify which specific tenant's or workload's data is actually driving a cost increase, rather than only observing that the total grew
- [ ] B: Automatically apply a lifecycle rule to the most expensive prefix
- [ ] C: Reduce the per-GB storage cost of the most expensive prefix
- [ ] D: Encrypt objects in the most expensive prefix with a dedicated KMS key

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Cost attribution is a diagnostic capability, not an automatic remediation — it narrows an
aggregate cost signal down to the specific source, which is exactly what found the `exports/`
prefix problem in the scenario.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [cost-attribution, storage-lens]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 3

```yaml
lesson_id: fde-elective-storage-networking-reliability-03-backup-and-disaster-recovery-strategies
lesson_title: "Backup and Disaster Recovery Strategies"
lesson_order: 3

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-storage-networking-reliability
module_name: "Storage, Networking & Reliability for FDEs (Elective)"
module_order: "Elective 3"

difficulty: Medium-Hard
estimated_minutes: 120
content_status: Draft

learning_outcomes:
  - "State a system's RPO and RTO as specific numbers derived from the business cost of lost work and downtime, not as aspirational defaults."
  - "Perform and time a full restore into an isolated environment, and use the measured result to correct a previously untested RTO assumption."
  - "Distinguish a full backup, an incremental backup, and a snapshot by what each actually captures and what restoring from each actually costs in time."

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
# Backup and Disaster Recovery Strategies

## Concepts Covered

RPO (Recovery Point Objective) and RTO (Recovery Time Objective) are the two numbers that turn
"we take backups" into an actual recovery commitment: RPO is how much recent work can be lost —
the maximum acceptable gap between the last recoverable backup and the moment of failure — and RTO
is how long the system may stay down while recovery happens. Neither number is a default; both must
be derived from what the business actually loses per unit of data or per hour of downtime, and a
system with no stated RPO/RTO effectively has an RPO and RTO of "however long it takes," discovered
for the first time during a real incident. RDS automated backups combine a daily full snapshot with
continuous transaction-log shipping, which is what makes point-in-time recovery (PITR) possible —
restoring the database to any specific second within the retention window (up to 35 days), not only
to the moment of the last snapshot — because the log lets AWS replay every committed transaction
between the snapshot and the requested timestamp. A snapshot alone (an EBS volume snapshot, or an
RDS snapshot without PITR) captures a single point in time; restoring from it always means losing
everything written after that snapshot was taken, however recent the failure — the gap between
snapshot frequency and PITR's continuous log is exactly the difference between a coarse RPO and a
near-zero one.

Full and incremental backups differ in what they capture and, more consequentially, in what
restoring from them costs: a full backup contains everything and restores in one step; an
incremental backup contains only what changed since the last backup (full or incremental) and
restoring means applying the full backup and then every incremental in sequence, so restore time
grows with the number of increments since the last full — which is why a backup strategy needs a
periodic full backup even when incrementals are cheaper day to day. Cross-region backup copies
protect against a regional failure a same-region snapshot cannot survive, at the cost of the
replication lag between the source and the copy, which becomes the effective RPO floor for a
region-level disaster regardless of how tight the same-region RPO is. None of this is real until it
is tested: a backup that has never been restored is a hypothesis, not a capability, and the only way
to know the actual RTO is to perform a full restore into an isolated environment and time it — a
number derived from an untested assumption is not evidence, and the gap between the assumed RTO and
the measured one is frequently the first honest finding of a DR exercise.

```bash
# Point-in-time restore of the PolicyVault RDS instance to a specific second
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier policyvault-prod \
  --target-db-instance-identifier policyvault-pitr-restore-test \
  --restore-time 2026-08-30T14:32:00Z \
  --db-instance-class db.r6g.xlarge \
  --no-multi-az \
  --db-subnet-group-name policyvault-restore-sandbox

# Time the restore end to end
START=$(date +%s)
aws rds wait db-instance-available --db-instance-identifier policyvault-pitr-restore-test
END=$(date +%s)
echo "Restore completed in $(( (END - START) / 60 )) minutes"
```

## Practical Backend Scenario

Kestrel's compliance team asks the FDE a direct question during a customer security review: "If
your production database is destroyed right now, how much of today's claim updates do you lose, and
how long until PolicyVault is back?" The FDE cannot answer with confidence, because PolicyVault has
automated daily RDS snapshots but has never performed a restore. The FDE first states the actual
business-derived numbers: an RPO of 5 minutes (the maximum acceptable loss, since a lost claim-
status update requires manual reconciliation against the underwriting agency's own records, which
Kestrel's ops team can tolerate for a few minutes of work but not a full day) and an RTO of 30
minutes (the maximum acceptable downtime before Kestrel's SLA with its underwriting-agency
customers is breached). RDS's automated backups with PITR already meet the 5-minute RPO, since the
transaction log is shipped continuously. RTO is untested, so the FDE runs the restore command above
against a snapshot from the previous night, into an isolated sandbox subnet group with no
production traffic, and times it: 22 minutes for a `db.r6g.xlarge` instance with roughly 200 GB of
data — under the 30-minute target, but only 8 minutes of margin, which the FDE flags as a risk given
the database will keep growing and restore time is proportional to data volume, not a fixed constant.

## Practice Loop

1. Write an RPO/RTO table for PolicyVault naming the specific business cost that sets each number
   (manual reconciliation effort for RPO, SLA breach for RTO), not a round-number default.
2. Confirm PITR is actually enabled and that the transaction-log retention window covers the stated
   RPO — check the RDS console or `describe-db-instances` for `BackupRetentionPeriod`, not just that
   automated backups exist.
3. Perform a full point-in-time restore into an isolated sandbox environment (no shared subnet or
   security group with production) and measure the wall-clock time from restore command to the
   instance reaching `available` — this is the diagnostic step that converts an assumed RTO into a
   measured one.
4. Compare the measured restore time against the stated 30-minute RTO, and if the margin is thin,
   identify the largest lever for closing the gap (a smaller instance class restoring faster, a more
   frequent snapshot cadence, or a warm standby that skips the restore step entirely).
5. Write the recovery runbook with the exact commands used, the owner responsible for triggering it,
   the dependency order (database before application, application before DNS cutover), and the
   validation query that confirms the restored data is correct before traffic is routed to it.

## Evidence of Understanding

You can state RPO and RTO as specific numbers derived from the actual business cost of lost work or
downtime, not aspirational defaults. You can distinguish what a full backup, an incremental backup,
and a point-in-time-recovery-enabled continuous log each capture, and what restoring from each
actually costs in time. You can produce a recovery runbook with tested commands, an owner, a
dependency order, a validation check, and a timestamped measured result — not an assumption about
how long recovery would take.

## Suggested Extension

Add a cross-region copy of the nightly RDS snapshot to a second AWS region, and restate the DR
plan's effective RPO for a full regional failure, accounting for the replication lag between the
source snapshot and the cross-region copy rather than assuming the same-region RPO still applies.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** RPO versus RTO
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What is the precise distinction between RPO and RTO, per the lesson?

**OPTIONS:**
- [x] A: RPO is the maximum acceptable amount of recent work that can be lost; RTO is the maximum acceptable time the system may stay down during recovery
- [ ] B: RPO is measured in dollars and RTO is measured in minutes
- [ ] C: RPO applies only to databases while RTO applies only to application servers
- [ ] D: RPO and RTO both measure the same thing — total time to restore full service

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the lesson's core definitional distinction — RPO bounds data loss, RTO bounds downtime.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [rpo, rto, definitions]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why a system with no stated RPO/RTO still has one
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that a system with no explicitly stated RPO and RTO still effectively has
values for both?

**OPTIONS:**
- [x] A: Without a stated commitment, the actual RPO and RTO are "however long it takes" — discovered for the first time during a real incident rather than chosen deliberately in advance
- [ ] B: AWS assigns a default RPO and RTO of 24 hours to every RDS instance automatically
- [ ] C: Every database technically guarantees a zero RPO and zero RTO unless explicitly configured otherwise
- [ ] D: RPO and RTO only apply once a system has been in production for over a year

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's point is that the absence of a stated commitment does not mean the absence of a real
outcome — it just means that outcome is unknown until an incident forces it to be discovered.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [rpo-rto-default, untested-assumption]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What PITR adds beyond a daily snapshot
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specifically does point-in-time recovery add beyond a daily RDS snapshot alone?

**OPTIONS:**
- [x] A: Continuous transaction-log shipping lets the database be restored to any specific second within the retention window, not only to the moment of the last snapshot
- [ ] B: PITR makes the backup encrypted, while a plain snapshot is not
- [ ] C: PITR automatically replicates the backup to a second AWS region
- [ ] D: PITR eliminates the need to ever take a full snapshot again

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is precise about the mechanism: the transaction log lets AWS replay committed
transactions between the snapshot and the requested restore timestamp, giving second-level
granularity a snapshot alone cannot.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [pitr, transaction-log, restore-granularity]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why incremental-only backup restore time grows over time
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson state that a backup strategy needs a periodic full backup even when
incrementals are cheaper day to day?

**OPTIONS:**
- [x] A: Restoring from incrementals means applying the last full backup and then every incremental in sequence, so restore time grows with the number of increments since the last full
- [ ] B: Incremental backups are less durable than full backups and degrade over time
- [ ] C: Cloud providers charge a penalty fee for restoring from more than 5 incremental backups
- [ ] D: Incremental backups cannot capture schema changes, only data changes

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's specific claim is about restore-time growth, not durability or cost of the backups
themselves — the accumulation of increments to replay is what a periodic full backup bounds.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [incremental-backup, restore-time-growth]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What the RDS restore command actually establishes
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the lesson's CLI transcript, what does the `--restore-time` flag specifically control, and why
does the restored instance target a separate sandbox subnet group rather than production's?

**CODE_BLOCK:**
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier policyvault-prod \
  --target-db-instance-identifier policyvault-pitr-restore-test \
  --restore-time 2026-08-30T14:32:00Z \
  --db-subnet-group-name policyvault-restore-sandbox
```

**OPTIONS:**
- [x] A: `--restore-time` sets the exact second the database is reconstructed to via the transaction log; the sandbox subnet group isolates the restore-test instance from production traffic and network paths during the test
- [ ] B: `--restore-time` sets how long the restore command is allowed to run before timing out
- [ ] C: `--restore-time` is ignored unless Multi-AZ is enabled on the target instance
- [ ] D: The sandbox subnet group is required because RDS cannot restore into the same VPC as the source

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The flag drives PITR's specific-second reconstruction; the isolated subnet group is a deliberate
test-safety choice, not an AWS technical requirement — it keeps the restore test from touching
production network paths.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [restore-command, sandbox-isolation]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the 22-minute restore result is still flagged as a risk
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The FDE's measured restore took 22 minutes against a 30-minute RTO target — under budget. Why does
the lesson still flag this as a risk rather than closing the finding?

**OPTIONS:**
- [x] A: Restore time is proportional to data volume, not a fixed constant, and the database will keep growing, so the current 8-minute margin will shrink and eventually violate the RTO unless something changes
- [ ] B: A 22-minute restore is never acceptable regardless of the stated RTO
- [ ] C: The restore was performed in the wrong AWS region
- [ ] D: RDS PITR restores are not reliable enough to trust a single measurement

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's point is about the trend, not the single measurement — a thin, shrinking margin
against a growing dataset is a real risk even when today's number technically passes.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [rto-margin, data-growth-risk]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why cross-region replication lag sets the DR RPO floor
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson state that cross-region backup replication lag becomes the "effective RPO
floor" for a regional disaster, regardless of how tight the same-region RPO is?

**OPTIONS:**
- [x] A: In a full regional failure, only the cross-region copy survives, so recovery can only be as fresh as that copy — any lag between the source and the copy is unrecoverable data loss no same-region backup frequency can fix
- [ ] B: Cross-region replication is always slower than same-region replication, making it functionally useless
- [ ] C: AWS charges extra for cross-region PITR, so most customers disable it
- [ ] D: The same-region RPO and the cross-region RPO are always numerically identical by design

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the lesson's specific reasoning about failure scope — a regional failure removes the
same-region backups from consideration entirely, so only the cross-region copy's freshness matters.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [cross-region-backup, replication-lag, rpo-floor]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why a snapshot alone is a coarser RPO than PITR
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does restoring from a snapshot alone (without PITR) always mean losing everything written after
the snapshot, however recent the failure?

**OPTIONS:**
- [x] A: A snapshot captures a single point in time with no continuous log to replay forward from, so recovery can only reconstruct state as of the snapshot, not up to the moment of failure
- [ ] B: Snapshots are inherently less durable than transaction logs
- [ ] C: AWS deletes all writes made after a snapshot is taken, by design
- [ ] D: Snapshots can only be restored once every 24 hours regardless of how frequently they are taken

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's distinction is mechanism-based: a snapshot has no log to replay forward from, so its
RPO is bounded by snapshot frequency, unlike PITR's continuous log.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [snapshot-only-restore, coarse-rpo]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** What makes a backup "real" per the lesson
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson's closing claim in Concepts Covered, what actually distinguishes a real recovery
capability from a hypothesis?

**OPTIONS:**
- [x] A: The backup has actually been restored and the restore time measured — an untested backup is a hypothesis, not a capability
- [ ] B: The backup is stored in more than one AWS region
- [ ] C: The backup retention period exceeds 30 days
- [ ] D: The backup was taken using RDS automated backups rather than a manual snapshot

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the lesson's explicit closing claim in Concepts Covered — testing via an actual restore is
what converts an assumption into evidence.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [tested-restore, evidence-vs-hypothesis]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 4

```yaml
lesson_id: fde-elective-storage-networking-reliability-04-designing-the-networking-of-an-application
lesson_title: "Designing the Networking of an Application"
lesson_order: 4

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-storage-networking-reliability
module_name: "Storage, Networking & Reliability for FDEs (Elective)"
module_order: "Elective 3"

difficulty: Intermediate
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Assign each application tier (edge, app, data) to a subnet tier by its actual trust boundary and public-reachability need, not by convenience."
  - "Place a load balancer at the correct trust boundary for a given request path, distinguishing an internet-facing ALB from an internal one."
  - "Diagnose whether a failed dependency call is a DNS, route, security-policy, or application-layer failure using the signal each layer actually produces."

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
# Designing the Networking of an Application

## Concepts Covered

Application network design is a set of trust-boundary decisions layered on top of subnet and route-
table mechanics you should already have (VPCs, subnets, route tables, and security groups are
covered elsewhere in this curriculum) — the question this lesson answers is which tier belongs where
and why, not how a route table works. The rule that decides subnet placement is reachability, not
convenience: a tier needs a public subnet (a route to an internet gateway) only if something outside
the VPC must reach it directly, and every tier that does not need direct external reachability
belongs in a private subnet, reachable only through whatever fronts it. For a typical three-tier
application, that means exactly one thing sits in a public subnet by default: the load balancer.
Everything the load balancer fronts — the application tier — sits in a private subnet, reachable only
from the load balancer's security group, not from the internet directly; and the data tier sits in a
still more private subnet, reachable only from the application tier's security group, with no route
to an internet gateway or NAT gateway at all, since a database has no legitimate reason to originate
or receive traffic from the public internet.

Where the load balancer sits changes what "internet-facing" means for the rest of the design: an
internet-facing ALB terminates public traffic in the public subnet and forwards it, over the private
network, to targets in the private app subnet — the app tier never has a public IP and is
unreachable from outside the VPC by construction, not by security-group configuration alone, which
is a stronger guarantee than "the security group happens to deny it today." An internal ALB, by
contrast, has no route to an internet gateway and exists specifically to load-balance east-west
traffic between internal tiers — for example, a public-facing API tier calling an internal claims-
processing tier that should never be reachable from outside the VPC under any security-group
misconfiguration, because the ALB itself has no public path to misconfigure. Diagnosing a broken
request path means reading which layer actually failed: a DNS failure looks like a resolution error
before any connection is attempted; a route failure (a missing route-table entry, or a security
group denying the specific port) looks like a connection timeout, since the packet either has
nowhere to go or is silently dropped; and an application-layer failure (the service itself returning
a 5xx or hanging) looks like a connection that succeeds but a request that fails or stalls after
that — conflating a route-layer timeout with an application-layer hang wastes an incident's most
valuable minutes chasing the wrong layer.

```
# Three-tier PolicyVault subnet layout (single AZ shown; mirrored per AZ for HA)
public-subnet-1a      10.0.0.0/24   route: 0.0.0.0/0 -> igw-xxxx
                                     hosts: internet-facing ALB only

private-app-subnet-1a 10.0.10.0/24  route: 0.0.0.0/0 -> nat-gw-1a (outbound only)
                                     hosts: PolicyVault API service (ECS tasks)
                                     ingress: from ALB security group, port 443 only

private-data-subnet-1a 10.0.20.0/24 route: no 0.0.0.0/0 route at all
                                     hosts: RDS PostgreSQL primary
                                     ingress: from app-tier security group, port 5432 only
```

Service discovery is the mechanism that lets the app tier find the data tier's actual network
location without hard-coding an IP address that changes on every failover or scaling event. Inside
a VPC, this is usually solved with a private DNS name (an RDS instance's endpoint, or a Route 53
private hosted zone entry for an internal service) rather than an IP literal, so a database failover
that promotes a new primary, or a scaling event that changes which instances are in service, is
transparent to the app tier's configuration — it re-resolves the same name and reaches whichever
instance now holds that role. Egress design deserves the same explicitness as ingress: an app tier
that calls an external fraud-check API needs an explicit, named egress path (a NAT gateway route, or
a VPC endpoint if the destination is another AWS service like S3, which avoids sending that traffic
over the public internet and through the NAT gateway entirely) rather than an implicit "it can reach
the internet because it has a route," since an unbounded egress rule is exactly the kind of overly
broad permission a least-privilege network design is meant to eliminate — the app tier should be able
to reach the specific fraud-check endpoint and nothing else outbound that was never a stated
dependency. Network observability closes the diagnostic loop these boundaries create: VPC Flow Logs
record every accepted and rejected connection at the elastic-network-interface level, which is the
concrete evidence that turns "the request timed out" into "the request was rejected by this specific
security group, at this specific timestamp, from this specific source" — without flow logs, a
route-layer failure and a silently-dropped packet look identical from the application's point of
view, and the on-call engineer is left guessing which of several possible boundaries actually
blocked the request.

## Practical Backend Scenario

Kestrel's security team flags an assumption in PolicyVault's early prototype during a review: the
application tier was deployed with a public IP "temporarily, to make debugging easier," and nobody
removed it before the pilot went live. The FDE redraws the network with the three-tier layout above:
the internet-facing ALB moves to the public subnet as the only public-facing component; the API
service moves to a private subnet with its public IP removed, reachable only from the ALB's security
group on port 443; and the RDS instance, already private, gets its security group tightened to allow
inbound only from the app tier's security group, closing a broader rule that had allowed the entire
VPC CIDR. To verify the redesign rather than assume it, the FDE runs a permitted-flow test (a
request through the ALB reaches the API and returns a response) and a denied-flow test (a direct
connection attempt to the app tier's private IP from outside the VPC, which times out rather than
being refused — confirming there is genuinely no route, not merely a security-group denial a
misconfiguration could later loosen). A third test, cutting the API tier's outbound NAT gateway
route deliberately, produces a clean, diagnosable timeout on the API's calls to an external
fraud-check service — distinct from what a DNS misconfiguration or an application exception would
have produced, which is exactly the layer-specific signal the design is meant to preserve.

## Practice Loop

1. Draw PolicyVault's critical request path (a claim-status update: client to ALB to API to
   database, and the API's outbound call to an external fraud-check service) and label the subnet
   and trust boundary each hop crosses.
2. For every component on that path, state explicitly whether it needs a public subnet, and justify
   each answer by actual external reachability need, not convenience.
3. Test a dependency timeout deliberately (cut the app tier's NAT gateway route, or remove a
   security-group rule) and record the exact symptom it produces, so you have a known signature to
   compare against during a real incident.
4. Attempt the denied-flow test — a direct connection to the private app tier from outside the VPC —
   and confirm it times out due to an actual missing route, not merely a security-group rule that
   could be loosened later without anyone noticing the boundary weakened.
5. Document the least-privilege network rule set for every tier boundary (ALB-to-app, app-to-data,
   app-to-external-dependency) as an explicit table of source, destination, and port — no rule wider
   than the specific traffic it must allow.

## Evidence of Understanding

You can assign each application tier to a subnet by its actual external-reachability need, placing
only the load balancer in a public subnet by default. You can explain the difference between an
internet-facing ALB and an internal ALB and choose correctly between them for a given request path.
You can diagnose whether a broken dependency call is a DNS, route, security-policy, or application-
layer failure from the specific symptom each layer produces, rather than guessing from a generic
"it's not working."

## Suggested Extension

Add a second internal ALB in front of a new internal fraud-scoring service that only the API tier
should reach, and justify why this service gets an internal ALB rather than being called directly
from the API tier via its private IP.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** The rule that decides subnet placement
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what determines whether a tier belongs in a public or private subnet?

**OPTIONS:**
- [x] A: Whether something outside the VPC must reach that tier directly — only a tier with a genuine external-reachability need belongs in a public subnet
- [ ] B: Whether the tier stores persistent data or is stateless
- [ ] C: Whether the tier is written in a compiled or interpreted language
- [ ] D: Whichever subnet has the most available IP addresses at deploy time

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson states this explicitly as the deciding rule — reachability need, not convenience or
any property of the workload itself.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [subnet-placement, reachability]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why the app tier having no public IP is a stronger guarantee
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that an app tier with no public IP at all is a stronger guarantee than
"the security group happens to deny external access today"?

**OPTIONS:**
- [x] A: Unreachability by construction (no route to an internet gateway) cannot be undone by a single security-group misconfiguration, while a security-group-only guarantee can be accidentally loosened
- [ ] B: Security groups are stateless and therefore inherently less secure than route tables
- [ ] C: AWS does not allow security groups to be attached to instances without a public IP
- [ ] D: A private IP is technically unroutable on the public internet under any circumstance, making the distinction meaningless in practice

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's distinction is about failure mode: a route-level guarantee survives a security-group
mistake, while a security-group-only guarantee does not survive a security-group mistake.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [defense-in-depth, route-vs-security-group]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** When an internal ALB is the right choice
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, when is an internal (not internet-facing) ALB the right choice?

**OPTIONS:**
- [x] A: To load-balance east-west traffic between internal tiers that should never be reachable from outside the VPC under any misconfiguration, since the ALB itself has no public route to misconfigure
- [ ] B: Whenever TLS termination is required, regardless of whether the traffic is internal or external
- [ ] C: Only when the application has fewer than three backend targets
- [ ] D: Internal ALBs should be used interchangeably with internet-facing ALBs; the distinction has no functional consequence

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's specific reasoning: an internal ALB has no route to an internet gateway, so it cannot
be misconfigured into public exposure the way a security-group-only boundary could.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [internal-alb, east-west-traffic]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Distinguishing a route failure from an application failure by symptom
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what symptom distinguishes a route-layer failure (missing route or a denying
security group) from an application-layer failure during an incident?

**OPTIONS:**
- [x] A: A route failure looks like a connection timeout (the packet has nowhere to go or is silently dropped); an application failure looks like a connection that succeeds but a request that then fails or hangs
- [ ] B: A route failure always produces an HTTP 500; an application failure always produces an HTTP 502
- [ ] C: There is no reliable symptom difference between the two; both must be diagnosed by reading application logs
- [ ] D: A route failure resolves itself within 60 seconds while an application failure does not

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the lesson's precise diagnostic distinction — whether the connection itself succeeds is
the signal that separates a network-layer problem from an application-layer one.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [incident-diagnosis, layer-specific-symptom]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Reading the subnet layout
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the subnet layout in the lesson, why does the data subnet have no `0.0.0.0/0` route at all,
unlike the app subnet, which has one pointed at a NAT gateway?

**CODE_BLOCK:**
```
private-app-subnet-1a  10.0.10.0/24  route: 0.0.0.0/0 -> nat-gw-1a (outbound only)
private-data-subnet-1a 10.0.20.0/24  route: no 0.0.0.0/0 route at all
```

**OPTIONS:**
- [x] A: The app tier needs outbound internet access (to call the external fraud-check service), while the database has no legitimate reason to originate or receive any internet traffic at all
- [ ] B: NAT gateways are limited to one per VPC, so only one private subnet can have outbound access
- [ ] C: RDS instances are technically incapable of using a NAT gateway route
- [ ] D: The data subnet's missing route is a misconfiguration that should be fixed to match the app subnet

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is explicit that the database has no legitimate reason for any internet-bound traffic,
while the app tier's genuine outbound dependency (the fraud-check call) justifies its NAT route.

**LESSON_CONNECTION:** Concepts Covered, code block
**KEYWORDS:** [nat-gateway, data-tier-isolation]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Purpose of the denied-flow test in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE specifically check that the direct connection attempt to the app tier's private IP
timed out, rather than being actively refused, and treat that as the correct result?

**OPTIONS:**
- [x] A: A timeout confirms there is genuinely no route to the app tier from outside the VPC, which cannot be undone by a later security-group change — a "refused" result could instead mean only a security group is denying it, which is a weaker, more easily loosened guarantee
- [ ] B: A timeout is always the correct result for any network test, regardless of what is being tested
- [ ] C: An actively refused connection indicates a firewall is misconfigured, while a timeout indicates it is working correctly
- [ ] D: The distinction between a timeout and a refusal has no security significance; both prove the same thing

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This connects directly to the lesson's route-versus-security-group distinction — a timeout proves
the stronger, construction-level guarantee, not merely a currently-configured denial.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [denied-flow-test, timeout-vs-refusal]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What the security-group tightening in the scenario actually fixed
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specifically was wrong with the RDS instance's original security-group rule in the scenario,
before the FDE tightened it?

**OPTIONS:**
- [x] A: It allowed inbound traffic from the entire VPC CIDR block, rather than only from the app tier's specific security group
- [ ] B: It allowed inbound traffic from the public internet directly
- [ ] C: It blocked all inbound traffic, including from the legitimate app tier
- [ ] D: It used an outdated TLS version for connections to the database

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The scenario states the original rule allowed the entire VPC CIDR, which is broader than
least-privilege — the fix scopes it to only the app tier's own security group.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [least-privilege, security-group-scoping]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What Practice Loop step 5 requires beyond "add security groups"
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does Practice Loop step 5 specifically require when documenting the least-privilege network
rule set for each tier boundary?

**OPTIONS:**
- [x] A: An explicit table of source, destination, and port for every boundary, with no rule wider than the specific traffic it must allow
- [ ] B: A single rule allowing all traffic within the VPC, since every component is already trusted internally
- [ ] C: A written justification only for the ALB-to-app boundary; the app-to-data boundary is assumed safe by default
- [ ] D: A firewall diagram with no reference to specific ports or protocols

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The step's bar is explicit and per-boundary: source, destination, port, and no rule broader than
necessary — matching the lesson's least-privilege framing throughout.

**LESSON_CONNECTION:** Practice Loop, Step 5
**KEYWORDS:** [least-privilege-documentation, rule-set]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 5

```yaml
lesson_id: fde-elective-storage-networking-reliability-05-load-balancing-and-auto-scaling-groups
lesson_title: "Load Balancing and Auto Scaling Groups"
lesson_order: 5

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-storage-networking-reliability
module_name: "Storage, Networking & Reliability for FDEs (Elective)"
module_order: "Elective 3"

difficulty: Intermediate
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Configure a target-group health check whose success criteria actually reflects application readiness, not just process liveness."
  - "Write an Auto Scaling policy with the correct scaling signal, cooldown, and warm-up so it reacts to real load without thrashing."
  - "Verify connection draining and instance replacement behavior under a live termination, not just from the configuration alone."

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
# Load Balancing and Auto Scaling Groups

## Concepts Covered

A target group's health check decides which instances receive traffic, so its correctness is a
direct availability property, not a configuration detail: a health check that only confirms the
process is running (a TCP check on the listen port) will mark an instance healthy the moment the
process binds the port, even if the application has not finished loading its configuration,
warming its connection pool, or completing dependency checks — and the load balancer will start
routing real user requests to an instance that cannot actually serve them correctly yet. An HTTP
health check against a dedicated readiness endpoint (`GET /health/ready`, returning 200 only once
the app has confirmed its database connection pool is live and any required startup cache is
populated) is a stronger signal, because it tests the specific condition that determines whether the
instance can actually do useful work, not merely whether its process exists. The health-check
interval, timeout, healthy threshold, and unhealthy threshold together set how fast the target group
reacts: a 10-second interval with a 2-check healthy threshold takes at least 20 seconds to register
an instance as healthy after it starts passing, and a 3-check unhealthy threshold at the same
interval takes at least 30 seconds to pull a failing instance out of rotation — both numbers are a
direct trade between reacting fast and reacting to noise, not a default to leave untouched.

Connection draining (deregistration delay) determines what happens to in-flight requests when an
instance is being removed from the target group, whether because of a scale-in event or a
deployment: without it, an instance is deregistered immediately and any request mid-flight to it is
abruptly dropped; with a deregistration delay configured (for example, 30 seconds), the load balancer
stops sending new requests to that target immediately but lets existing connections finish naturally
within the delay window before the instance is actually terminated. Auto Scaling policies react to a
signal — target tracking on CPU utilization or request count per target, step scaling on a specific
CloudWatch alarm threshold, or a scheduled action for a known traffic pattern — and the cooldown
period after a scaling action prevents the group from reacting to the same signal again before the
new capacity has had time to actually absorb load and show up in the metric, which is what prevents
a scale-out event from immediately triggering another scale-out on the same, not-yet-resolved
metric spike. A launch template's warm-up time tells the Auto Scaling group how long a newly
launched instance needs before its metrics should count toward the group's scaling decisions —
without it, a fleet of instances still warming up can appear to still be under load, triggering an
unnecessary second scale-out.

```json
{
  "TargetGroupArn": "arn:aws:elasticloadbalancing:...:targetgroup/policyvault-api/abc123",
  "HealthCheckPath": "/health/ready",
  "HealthCheckIntervalSeconds": 10,
  "HealthCheckTimeoutSeconds": 5,
  "HealthyThresholdCount": 2,
  "UnhealthyThresholdCount": 3,
  "Matcher": { "HttpCode": "200" },
  "DeregistrationDelay": { "TimeoutSeconds": 30 }
}
```

```json
{
  "PolicyName": "policyvault-api-target-tracking-cpu",
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingConfiguration": {
    "PredefinedMetricSpecification": { "PredefinedMetricType": "ASGAverageCPUUtilization" },
    "TargetValue": 60.0,
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 300
  },
  "DefaultInstanceWarmup": 90
}
```

Listener rules decide which target group a request reaches before health checks or scaling ever
come into play, and getting the rule priority and condition wrong routes correctly-formed traffic to
the wrong backend silently rather than producing an obvious error: a path-based rule
(`/api/claims/*` to the claims target group, `/api/documents/*` to the documents target group) and a
host-based rule (routing by `Host` header for a multi-tenant custom-domain setup) are evaluated in
priority order, and a broader rule placed at a lower priority number than a more specific one will
match first and swallow traffic the specific rule was meant to catch — the fix is always to order
rules from most specific to least specific, with a catch-all default action last. Capacity limits are
the boundary condition an Auto Scaling policy operates inside, not an afterthought: a target-tracking
policy's `MaxSize` caps how far the group can scale regardless of how far above target the metric
climbs, and choosing that ceiling requires the same capacity-modeling discipline as any other scaling
decision — a `MaxSize` set from a guess rather than a measured peak-plus-margin calculation either
caps the group below real peak demand, causing a sustained overload the policy cannot escape, or
wastes budget provisioning headroom for a peak that never materializes. Sticky sessions, when a load
balancer is configured to route a given client's requests to the same target for the session's
duration (via a cookie), are worth naming as a targeted exception to statelessness rather than a
default: they exist for a specific, narrow reason — an application that has not yet externalized
some piece of session state — and every sticky session configured is a signal that a piece of the
otherwise-stateless design still depends on one particular instance, worth tracking down and removing
rather than leaving as a permanent crutch.

## Practical Backend Scenario

During a PolicyVault deployment, new instances register in the target group and immediately start
receiving traffic before the application has finished loading its RDS connection pool, producing a
burst of connection-refused errors visible in the ALB's 5xx metric for the first 15 seconds after
every deploy. The FDE traces this to a TCP-only health check that marks the instance healthy the
instant its process binds port 8080, regardless of readiness, and replaces it with an HTTP check
against `/health/ready`, an endpoint the FDE adds that returns 200 only after the connection pool
reports itself live. The FDE also sets a 30-second deregistration delay so that a deploy's outgoing
instances finish their in-flight requests instead of dropping them mid-response, and configures a
target-tracking Auto Scaling policy at 60% average CPU with a 300-second scale-in cooldown — chosen
deliberately longer than the 60-second scale-out cooldown, since scaling in too eagerly during a
brief lull and then immediately scaling back out during the next request burst is more expensive
(cold-start latency on new instances) than carrying a small amount of excess capacity for a few extra
minutes. To confirm the whole chain actually works rather than trusting the configuration alone, the
FDE runs a load test that pushes CPU past 60%, watches a new instance launch and register, and
separately terminates a running instance manually to confirm its in-flight requests finish during
the 30-second drain window before it disappears from the target group.

## Practice Loop

1. Replace a TCP-only health check with an HTTP check against a dedicated readiness endpoint, and
   define exactly what condition (database pool live, startup cache populated) must be true for
   that endpoint to return 200.
2. Configure the health-check interval, healthy threshold, and unhealthy threshold, and calculate
   the minimum time each direction (healthy-to-serving, unhealthy-to-removed) takes given those
   settings.
3. Run a load test against the service and record, second by second, when the Auto Scaling group's
   CPU metric crosses the 60% target, when a new instance registers, and when it starts receiving
   traffic — this diagnostic timeline exposes any gap between "scaling triggered" and "capacity
   actually available."
4. Terminate a running, in-service instance manually while it has an in-flight request, and confirm
   the request completes successfully within the deregistration delay window rather than being
   dropped.
5. Compare the scale-out and scale-in cooldowns, and justify why they are set to different values
   given the relative cost of premature scale-in versus a small amount of excess capacity.

## Evidence of Understanding

You can configure a target-group health check whose success condition reflects actual application
readiness, not process liveness, and calculate the minimum registration and removal time from its
interval and threshold settings. You can configure a deregistration delay and verify, by terminating
a live instance, that in-flight requests actually complete rather than being dropped. You can relate
a scaling policy's target metric, cooldown, and warm-up settings to a measured load test, and justify
asymmetric scale-out and scale-in cooldowns by the relative cost of each direction being wrong.

## Suggested Extension

Add a step-scaling policy triggered by a CloudWatch alarm on ALB `TargetResponseTime` p99 (rather
than average CPU alone), and justify why a latency-based signal might catch a capacity problem the
CPU-based target-tracking policy would miss.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why a TCP-only health check is insufficient
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that a TCP-only health check is a weaker readiness signal than an HTTP
check against a dedicated endpoint?

**OPTIONS:**
- [x] A: A TCP check only confirms the process has bound the port, which can be true before the application has finished loading configuration or warming its connection pool, so it can mark an instance healthy before it can actually serve requests correctly
- [ ] B: TCP health checks are deprecated by AWS and no longer supported on target groups
- [ ] C: TCP checks are slower to execute than HTTP checks, adding latency to every health-check cycle
- [ ] D: TCP checks cannot be configured with a custom interval or threshold

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's argument is about what the check actually verifies — process existence versus
application readiness — not about deprecation or performance.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [health-check, readiness-vs-liveness]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Calculating minimum time to healthy
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given the target-group configuration in the lesson, what is the minimum time after an instance
starts passing health checks before the target group marks it healthy?

**CODE_BLOCK:**
```json
{
  "HealthCheckIntervalSeconds": 10,
  "HealthyThresholdCount": 2
}
```

**OPTIONS:**
- [x] A: 20 seconds (2 consecutive passing checks at a 10-second interval)
- [ ] B: 10 seconds (a single passing check is sufficient)
- [ ] C: 30 seconds (the interval times the unhealthy threshold, not the healthy threshold)
- [ ] D: 2 seconds (the healthy threshold count alone, ignoring the interval)

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
Two consecutive passing checks are required, each 10 seconds apart, so the minimum elapsed time is
2 x 10 = 20 seconds.

**LESSON_CONNECTION:** Concepts Covered, code block
**KEYWORDS:** [health-check-math, healthy-threshold]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What connection draining actually changes
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does configuring a deregistration delay (connection draining) actually change about how an
instance is removed from a target group?

**OPTIONS:**
- [x] A: New requests stop being sent to the target immediately, but existing in-flight connections are allowed to finish naturally within the delay window before termination
- [ ] B: The instance keeps receiving new requests throughout the entire delay window, then all connections are dropped simultaneously
- [ ] C: Deregistration delay only affects health checks, not actual request routing
- [ ] D: It extends the health-check interval for that specific instance during shutdown

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's precise mechanism: new traffic stops immediately, but existing connections get a
window to complete rather than being abruptly cut — that is the specific value of draining.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [connection-draining, deregistration-delay]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why the scale-in cooldown is set longer than scale-out
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why does the FDE deliberately set the scale-in cooldown (300 seconds) longer than
the scale-out cooldown (60 seconds)?

**CODE_BLOCK:**
```json
"TargetTrackingConfiguration": {
  "TargetValue": 60.0,
  "ScaleOutCooldown": 60,
  "ScaleInCooldown": 300
}
```

**OPTIONS:**
- [x] A: Scaling in too eagerly during a brief lull and then having to scale back out during the next burst costs more (cold-start latency on new instances) than carrying a small amount of excess capacity for a few extra minutes
- [ ] B: AWS enforces a minimum ratio of 5:1 between scale-in and scale-out cooldowns
- [ ] C: A longer scale-in cooldown reduces the AWS bill regardless of traffic pattern
- [ ] D: Scale-in cooldowns have no functional effect; only scale-out cooldowns matter operationally

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the lesson's explicit cost reasoning — the asymmetric cooldown reflects the asymmetric
cost of being wrong in each direction, not an AWS constraint.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [scale-in-cooldown, asymmetric-cost]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What DefaultInstanceWarmup prevents
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What problem does setting a launch template's warm-up time (`DefaultInstanceWarmup`) specifically
prevent?

**OPTIONS:**
- [x] A: A newly launched instance still warming up can appear to be under load, which would otherwise count toward the group's scaling metric and trigger an unnecessary second scale-out
- [ ] B: It prevents a newly launched instance from ever receiving traffic at all
- [ ] C: It prevents the health check from running until the warm-up period elapses
- [ ] D: It reduces the instance's CPU allocation during the warm-up period

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's specific claim: without excluding a still-warming instance's metrics from the scaling
decision, the group can misread its own not-yet-useful capacity as continued load.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [instance-warmup, scaling-metric-pollution]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What Practice Loop step 3 actually diagnoses
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does Practice Loop step 3 ask you to record, second by second, when the CPU metric crosses the
threshold, when a new instance registers, and when it starts receiving traffic, rather than just
confirming the group eventually scaled out?

**OPTIONS:**
- [x] A: This timeline exposes any gap between "scaling triggered" and "capacity actually available to serve traffic" — a gap that matters during a real burst even if the group eventually reaches the right size
- [ ] B: AWS requires a documented timeline before a scaling policy can be marked production-ready
- [ ] C: It measures the exact dollar cost of the scaling event
- [ ] D: It confirms the CloudWatch alarm fired at exactly the configured threshold value, which is otherwise unverifiable

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the diagnostic value of the step — the lag between trigger and usable capacity is
invisible if you only check the end state, but it directly affects users during the gap.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [scaling-timeline, capacity-lag]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Root cause of the 5xx burst in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What was the actual root cause of the 5xx burst observed in the first 15 seconds after every
PolicyVault deploy?

**OPTIONS:**
- [x] A: A TCP-only health check marked new instances healthy the instant their process bound the port, before the application had finished loading its RDS connection pool
- [ ] B: The Auto Scaling group was launching too many instances at once during each deploy
- [ ] C: The RDS instance itself was running out of available connections
- [ ] D: The deregistration delay was set too short, dropping in-flight requests during deploy

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The scenario traces the 5xx burst specifically to the TCP health check's premature "healthy"
signal, not to scaling behavior or the deregistration delay.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [deploy-5xx, root-cause]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Unhealthy threshold's effect on removal speed
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given a 10-second health-check interval and an unhealthy threshold count of 3, what is the minimum
time before a genuinely failing instance is pulled out of rotation?

**OPTIONS:**
- [x] A: 30 seconds (3 consecutive failing checks at a 10-second interval)
- [ ] B: 10 seconds (a single failed check is sufficient to remove the instance)
- [ ] C: 3 seconds (the threshold count alone, independent of the interval)
- [ ] D: It is removed immediately once the ALB detects any single dropped connection

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The same interval-times-threshold math from the healthy case applies symmetrically to the
unhealthy threshold: 3 x 10 = 30 seconds minimum before removal.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [unhealthy-threshold, removal-time-math]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 6

```yaml
lesson_id: fde-elective-storage-networking-reliability-06-designing-for-scalability-of-application-and-data
lesson_title: "Designing for Scalability of Application and Data"
lesson_order: 6

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-storage-networking-reliability
module_name: "Storage, Networking & Reliability for FDEs (Elective)"
module_order: "Elective 3"

difficulty: Intermediate
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Model a system's actual bottleneck from a workload estimate rather than scaling the entire system uniformly on assumption."
  - "Choose the least complex effective scaling boundary (a read replica, a queue, statelessness) for a specifically identified bottleneck."
  - "Measure throughput, latency, and failure behavior before and after a scaling change to confirm the bottleneck actually moved."

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
# Designing for Scalability of Application and Data

## Concepts Covered

Scaling a system correctly starts with identifying its actual bottleneck, not applying more
capacity uniformly across every layer — a system under load almost always has one component that
saturates first, and scaling every other component while leaving that one unchanged spends effort
and money without moving the ceiling at all. The distinction between vertical scaling (a bigger
instance: more CPU, memory, or IOPS on the same node) and horizontal scaling (more instances sharing
the load) matters because they solve different bottleneck shapes: vertical scaling has a hard
ceiling (the largest instance type AWS offers) and does nothing for a bottleneck that is structural
rather than resource-bound — a single database accepting serialized writes does not get faster
because the instance below it got bigger, if the actual constraint is that writes are serialized by
a table lock, not by CPU. Horizontal scaling requires statelessness to work at all: an application
tier can only be scaled horizontally if any instance can serve any request, which means session
state, in-memory caches that must stay consistent, and file uploads written to local disk all have
to move to a shared, external store (Redis, S3, the database) before adding a second instance is
safe — an application that silently depends on in-memory state will scale horizontally by
introducing a new class of bug (a request landing on the "wrong" instance sees stale or missing
state), not by getting faster.

A queue is a specific, common bottleneck fix: it absorbs a burst by decoupling the rate work arrives
from the rate work is processed, but an unbounded in-memory queue does not create capacity, it only
defers the moment the bottleneck becomes visible — if the consumer's processing rate is genuinely
below the arrival rate, an unbounded queue grows without limit until the process runs out of memory,
which converts a visible slowdown into an invisible one until it becomes a crash. A bounded queue
with explicit back-pressure (rejecting or delaying new work once the queue reaches a limit) makes the
real constraint visible immediately instead of hiding it behind growing memory usage. A read replica
addresses a specific, narrow bottleneck shape — read-heavy load exceeding what a single database
instance can serve — by routing read queries to one or more replicas while writes still go to the
primary; it does nothing for a write-bottlenecked workload, since every replica still receives the
same write stream via replication, which means adding a read replica to a write-bound problem is a
scaling boundary applied to the wrong layer. Building a capacity model — an estimate of expected
request rate, the resource cost per request, and the resulting required capacity, worked out on
paper or with a load test before the scaling change — is what turns "we might need to scale" into a
specific, falsifiable prediction that a before/after measurement can actually confirm or refute.

```
# Back-of-envelope capacity model for PolicyVault's claim-status write path
Expected peak claim updates: 40 requests/sec (10x current 4 req/sec, per customer's stated growth)
Measured cost per write: 25ms DB time (serialized on the claims table's row lock, not CPU)
Max sustainable throughput with current serialization: 1000ms / 25ms = 40 req/sec ceiling

-> The database is not CPU-bound; it is lock-bound. A bigger RDS instance class raises the CPU
   ceiling, not the lock-serialization ceiling. The actual fix is reducing per-write lock hold time
   or partitioning writes so unrelated claims don't contend for the same lock.
```

## Practical Backend Scenario

Kestrel tells the FDE PolicyVault must support ten times current traffic (400 req/sec) ahead of a
new regional rollout. The FDE's first instinct — resize the RDS instance to a larger class — turns
out to be the wrong lever once measured: a load test shows claim-status writes serialize on a
row-level lock in the `claims` table (every update to a claim's status acquires the same lock
briefly, regardless of which claim it is, because a poorly indexed trigger scans the whole table),
capping throughput at roughly 40 writes/sec no matter how large the instance gets, since the
bottleneck is lock contention, not CPU or IOPS. The FDE also finds an unbounded in-memory queue
buffering outbound notification events, which had been silently growing during traffic spikes and
nearly caused an out-of-memory crash during the last load test — invisible until it became a hard
failure. The actual fix has two parts: the FDE removes the table-wide scan from the trigger so locks
are held only as long as the single row's update actually takes, raising sustainable throughput well
past the 400 req/sec target; and replaces the unbounded queue with a bounded SQS queue with a
visibility timeout and a DLQ, so a genuine processing slowdown produces a visible, boundedqueue-depth
metric instead of unbounded memory growth. A read replica, briefly considered, is correctly rejected
once the FDE confirms the actual read load was never close to saturating the primary — the
bottleneck was never a read-capacity problem at all.

## Practice Loop

1. Estimate PolicyVault's expected peak workload (400 req/sec) and the resource cost per request for
   its most write-heavy operation (claim-status update), using measured, not assumed, per-request
   cost.
2. Model where the system actually saturates first given that estimate — compute the theoretical
   throughput ceiling from the measured cost per operation, the way the capacity model above does.
3. Run a load test against the current system and measure the actual observed ceiling, comparing it
   against the modeled prediction — this diagnostic step confirms or corrects the model against
   reality rather than trusting the paper estimate alone.
4. Add exactly one scaling boundary targeted at the confirmed bottleneck (removing the lock-
   contention source, or bounding the notification queue) — not a uniform resize of every component.
5. Re-run the load test after the change and compare throughput, latency, and failure behavior
   before and after, confirming the bottleneck actually moved rather than assuming the fix worked.

## Evidence of Understanding

You can identify a system's actual bottleneck from a measured workload estimate rather than scaling
every layer uniformly on assumption, and distinguish a resource-bound bottleneck (CPU, IOPS) from a
structural one (lock contention) that a bigger instance cannot fix. You can choose the least complex
effective scaling boundary for a specifically identified bottleneck — a read replica only for a
confirmed read-heavy constraint, a bounded queue with back-pressure rather than an unbounded one for
a burst-absorption problem — and reject a scaling option that does not match the actual bottleneck
shape. You can measure throughput, latency, and failure behavior before and after a scaling change to
confirm it actually moved the ceiling.

## Suggested Extension

Model what happens to PolicyVault's throughput ceiling if a second regional customer base doubles
write volume again after this fix, and identify what would become the next bottleneck once lock
contention is no longer the constraint.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why uniform scaling wastes effort
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue against scaling every layer of a system uniformly under load?

**OPTIONS:**
- [x] A: A system under load almost always has one component that saturates first, and scaling components that are not the bottleneck spends effort without moving the actual ceiling
- [ ] B: Uniform scaling is technically impossible in AWS; only one resource can be resized at a time
- [ ] C: Uniform scaling always costs more than targeted scaling, in every case, by definition
- [ ] D: Scaling multiple components at once always introduces a race condition

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's argument is specifically about wasted effort relative to the actual bottleneck, not a
technical or cost impossibility.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [bottleneck-identification, uniform-scaling-waste]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why a bigger instance does not fix a lock-bound bottleneck
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the capacity model in the lesson, why does resizing the RDS instance to a larger class fail to
raise PolicyVault's throughput ceiling?

**CODE_BLOCK:**
```
Measured cost per write: 25ms DB time (serialized on the claims table's row lock, not CPU)
Max sustainable throughput with current serialization: 1000ms / 25ms = 40 req/sec ceiling
```

**OPTIONS:**
- [x] A: The bottleneck is lock-serialization time, a structural constraint independent of CPU or IOPS, so a bigger instance raises the CPU ceiling while leaving the actual constraining resource (lock hold time) unchanged
- [ ] B: RDS instance resizing requires downtime, making it operationally infeasible regardless of whether it would help
- [ ] C: A bigger instance class always has fewer available IOPS than a smaller one
- [ ] D: The claims table itself has a hard-coded row limit that a larger instance cannot bypass

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the lesson's central worked example: the throughput ceiling is set by lock-serialization
time, not by CPU or IOPS, so resource-based scaling does not touch the actual constraint.

**LESSON_CONNECTION:** Concepts Covered, code block
**KEYWORDS:** [lock-contention, resource-vs-structural-bottleneck]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What horizontal scaling requires
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What must be true of an application tier before it can be scaled horizontally, per the lesson?

**OPTIONS:**
- [x] A: It must be stateless — session state, consistent in-memory caches, and locally-written file uploads must move to a shared external store, since any instance must be able to serve any request
- [ ] B: It must be rewritten to use a different programming language optimized for concurrency
- [ ] C: It must already be running on the largest available instance type
- [ ] D: It must have zero external dependencies of any kind

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's specific requirement is statelessness — any request must be servable by any instance,
which requires moving local/in-memory state to a shared store first.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [horizontal-scaling, statelessness]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why an unbounded queue is a deferred failure, not a fix
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson describe an unbounded in-memory queue as deferring, rather than solving, a
capacity problem?

**OPTIONS:**
- [x] A: If the consumer's processing rate is genuinely below the arrival rate, an unbounded queue grows without limit until memory is exhausted, converting a visible slowdown into an invisible one until it crashes
- [ ] B: Unbounded queues are always slower to enqueue into than bounded ones
- [ ] C: AWS SQS does not support unbounded queues, so the scenario is theoretical only
- [ ] D: An unbounded queue always processes messages out of order, corrupting data

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's specific claim is about visibility, not raw performance — an unbounded queue hides
the real rate mismatch behind growing memory usage until it becomes a crash.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [unbounded-queue, deferred-failure]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why a read replica was correctly rejected
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why was adding a read replica correctly rejected as a fix in the PolicyVault scenario?

**OPTIONS:**
- [x] A: The actual bottleneck was write-lock contention, not read capacity, and a read replica only offloads read queries — it does nothing for a write-bound problem, since every replica still receives the same write stream
- [ ] B: RDS read replicas cannot be added to an instance that already has automated backups enabled
- [ ] C: Read replicas are always more expensive than resizing the primary instance
- [ ] D: PolicyVault's read query volume was too high for a single replica to handle

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is explicit that a read replica addresses a narrow bottleneck shape (read-heavy load) —
applying it to a write-bound problem targets the wrong layer entirely.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [read-replica, wrong-layer-scaling]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** What a capacity model turns an assumption into
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what does building a capacity model (expected rate, cost per request, resulting
required capacity) actually accomplish before a scaling change is made?

**OPTIONS:**
- [x] A: It turns "we might need to scale" into a specific, falsifiable prediction that a before/after load test can confirm or refute
- [ ] B: It guarantees the scaling change will work without needing a load test afterward
- [ ] C: It automatically selects the correct AWS instance type for the workload
- [ ] D: It replaces the need for a health check on the scaled component

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson frames the capacity model as a falsifiable prediction, not a guarantee — its value is
in being checkable against a measured result, which is exactly what the Practice Loop does.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [capacity-model, falsifiable-prediction]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** What actually caused the near-OOM crash in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specifically nearly caused an out-of-memory crash during PolicyVault's last load test?

**OPTIONS:**
- [x] A: An unbounded in-memory queue buffering outbound notification events grew without limit as processing fell behind arrival rate during the traffic spike
- [ ] B: The RDS instance ran out of connections under the increased write load
- [ ] C: A memory leak in the claims table's trigger logic
- [ ] D: Too many read replicas were provisioned simultaneously

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The scenario attributes the near-crash specifically to the unbounded notification queue, not the
database or replicas.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [oom-near-miss, unbounded-queue-scenario]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Purpose of Practice Loop step 3
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the Practice Loop ask you to run a load test and compare the observed ceiling against the
modeled prediction, rather than trusting the paper capacity model alone?

**OPTIONS:**
- [x] A: This diagnostic step confirms or corrects the model against reality — a paper estimate can be wrong about the actual bottleneck, and only a measured result validates or refutes it
- [ ] B: Load tests are required by AWS before any RDS configuration change can be applied
- [ ] C: The paper model is only used for cost estimation, not for predicting throughput
- [ ] D: It measures the exact latency of the health-check endpoint under load

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This is the step's stated diagnostic purpose — checking the model against a measured result,
consistent with the lesson's framing of the capacity model as a falsifiable prediction.

**LESSON_CONNECTION:** Practice Loop, Step 3
**KEYWORDS:** [load-test-validation, model-vs-reality]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->

---

# LESSON 7

```yaml
lesson_id: fde-elective-storage-networking-reliability-07-database-sharding-strategies-and-hot-spot-mitigation
lesson_title: "Database Sharding Strategies and Hot-Spot Mitigation"
lesson_order: 7

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: elective-storage-networking-reliability
module_name: "Storage, Networking & Reliability for FDEs (Elective)"
module_order: "Elective 3"

difficulty: Medium-Hard
estimated_minutes: 120
content_status: Draft

learning_outcomes:
  - "Compare candidate shard keys by their actual traffic-distribution consequence, quantified with real numbers, not by intuition about cardinality alone."
  - "Detect and quantify a hot shard using a concrete skew measurement, and identify which query patterns become harder under a given shard key."
  - "Design a safe resharding or tenant-isolation migration for a hot shard without a full-system outage."

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
# Database Sharding Strategies and Hot-Spot Mitigation

## Concepts Covered

A shard key determines which shard a row lands on, and the entire quality of a sharding scheme
follows from one property of that key: cardinality and distribution under the system's real traffic,
not under a uniform assumption. Hashing the shard key (`hash(shard_key) mod N`) spreads rows evenly
across N shards only if the key's actual value distribution in production traffic is close to
uniform; a key with a small number of highly unequal values — like `tenant_id` in a multi-tenant
system where one enterprise customer generates far more traffic than dozens of small tenants
combined — produces a hot shard no matter how good the hash function is, because hashing cannot fix
skew that already exists in the input distribution, it can only spread already-uniform input evenly.
Consistent hashing improves on plain `mod N` hashing for a different problem — minimizing the
fraction of keys that move when the shard count changes — but it does nothing for input skew either;
a hot tenant's hashed key still lands on one shard and stays there, consistent hashing just makes
adding shard N+1 later cheaper. Locality is the other axis a shard key decision affects: a key that
keeps a tenant's related rows on the same shard (like `tenant_id`) makes single-tenant queries a
single-shard operation, but a key chosen purely for even distribution (a random UUID) can force even
a single tenant's own query to scatter across every shard, turning what should be a simple query into
a scatter-gather across N shards, each contributing a partial result that must be merged — a real
latency and complexity cost that a distribution-optimal key can silently introduce.

Quantifying skew, not asserting it, is what turns a shard-key decision into an engineering choice
rather than a guess: for a candidate key, compute each shard's share of total request volume, and
express the imbalance as a ratio between the busiest and the median shard — a 1.2x ratio is normal
variance, a 5x or 10x ratio is a hot shard that will saturate long before the others, regardless of
overall cluster capacity, since a database cluster's real ceiling is its busiest shard's ceiling, not
an average across all shards. Once a hot shard is confirmed, the two practical mitigations are
different tools for different causes: bucketing (splitting one oversized tenant's key into several
sub-keys — `tenant_id:0` through `tenant_id:9`, spreading that single tenant's rows across ten
shards instead of one) fixes a hot key whose own volume genuinely exceeds one shard's capacity;
tenant isolation (moving one specific hot tenant to a dedicated shard, off the shared pool entirely)
fixes a hot tenant whose volume is disruptive to its neighbors on a shared shard even if it would fit
comfortably alone. A resharding migration — moving rows from an old shard mapping to a new one — must
happen without a full-system outage, which means a dual-write or backfill-then-cutover approach:
write new rows under both the old and new mapping during a transition window, backfill historical
rows into their new location, verify row counts match, then cut reads over and stop the dual write —
never a single atomic "flip" across a dataset large enough that flipping it is not actually
instantaneous.

```
# Shard-key comparison for PolicyVault's claims table, 6 shards, 12,000 req/sec total

Candidate A: shard_key = hash(tenant_id) mod 6
  Kestrel's largest tenant (a national underwriting group) alone generates 5,400 req/sec (45% of
  total). It hashes onto shard 2.
  Shard 0: 800   Shard 1: 950   Shard 2: 6,300 (5,400 + 900 other)   Shard 3: 1,100
  Shard 4: 1,650  Shard 5: 1,200
  Busiest (shard 2, 6,300) / median (~1,100) = 5.7x -> hot shard, will saturate long before others.

Candidate B: shard_key = hash(claim_id) mod 6  (claim_id is a random UUID, no tenant correlation)
  Shard 0: 2,050  Shard 1: 1,980  Shard 2: 2,010  Shard 3: 1,940  Shard 4: 2,020  Shard 5: 2,000
  Busiest / median = 1.03x -> evenly distributed.
  BUT: a single-tenant "list all claims for tenant X" query now scatter-gathers across all 6 shards
  instead of hitting one, since a tenant's claims are no longer co-located.

Mitigation applied to Candidate A: bucket the largest tenant only.
  shard_key = hash(tenant_id) mod 6, UNLESS tenant_id in {large_tenant_ids} ->
    hash(tenant_id || ':' || (claim_id mod 10)) mod 6
  Largest tenant's 5,400 req/sec now spreads across up to 10 sub-buckets, landing across multiple
  shards instead of concentrating on shard 2; every other tenant's locality is unaffected.
```

## Practical Backend Scenario

As Kestrel signs a national underwriting group as PolicyVault's largest customer, the claims table
starts showing uneven load: five of six shards run comfortably under capacity while one, hosting
that single large tenant, saturates during business hours and pushes p99 latency for every tenant
on that shard past the SLA — including several small tenants who did nothing to cause it, sharing
infrastructure with a tenant forty times their size. The FDE runs the shard-key comparison above:
plain `hash(tenant_id) mod 6` produces a 5.7x busiest-to-median skew because the hash function cannot
fix the fact that one tenant's raw traffic share is 45% of the total, while `hash(claim_id) mod 6`
would distribute evenly (1.03x) but breaks tenant-scoped query locality, forcing every "list this
tenant's claims" query — the platform's single most common query — into a six-way scatter-gather.
Neither candidate alone is acceptable, so the FDE applies bucketing specifically to the identified
hot tenant, leaving every other tenant's simple `hash(tenant_id) mod 6` locality untouched, and
writes a resharding migration plan: dual-write the large tenant's new claims under both the old
single-shard mapping and the new bucketed mapping for two weeks, backfill its historical claims into
the bucketed shards in the background, verify row counts and a sample of query results match between
old and new locations, then cut reads over to the bucketed mapping and stop the dual write — timed
for a low-traffic maintenance window, never a single atomic cutover across the tenant's full
multi-year claims history.

## Practice Loop

1. Compute each shard's request-volume share for at least two candidate shard keys, using
   PolicyVault's actual traffic mix (including the known large-tenant share), the way the worked
   comparison above does.
2. Express each candidate's imbalance as a busiest-to-median shard ratio, and state the threshold
   (5x or greater, per this lesson) above which a shard is considered hot.
3. For the candidate that distributes evenly, identify specifically which query pattern (tenant-
   scoped listing) becomes a scatter-gather across all shards instead of a single-shard operation —
   this diagnostic step makes the locality cost concrete rather than abstract.
4. Apply bucketing to the identified hot tenant only, and recompute the shard distribution to confirm
   the skew ratio actually drops while every other tenant's locality is unaffected.
5. Write the resharding migration plan (dual-write window, backfill, row-count verification,
   cutover, dual-write stop) and name the specific verification check that must pass before the
   cutover is considered safe.

## Evidence of Understanding

You can quantify shard-key skew as a busiest-to-median ratio from real traffic numbers, rather than
asserting a key is "well distributed" from intuition about cardinality alone. You can state which
query pattern becomes harder — specifically, scatter-gather across all shards — when a shard key
optimized for even distribution breaks tenant locality. You can explain how to move a hot tenant
safely with a dual-write-then-cutover resharding plan, verified by row-count and sample-result
checks, without a full-system outage.

## Suggested Extension

Model what happens to the skew ratio if Kestrel signs a second national-scale tenant roughly the
same size as the first, and decide whether bucketing both hot tenants on the shared six-shard pool
is still sufficient or whether one or both now warrant dedicated tenant isolation instead.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why hashing cannot fix input skew
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson argue that hashing a shard key (`hash(shard_key) mod N`) cannot fix a hot shard
caused by one tenant generating far more traffic than others?

**OPTIONS:**
- [x] A: Hashing spreads already-uniform input evenly, but it cannot fix skew that already exists in the input distribution itself — a hot tenant's hashed key still lands on one shard and stays there
- [ ] B: Hash functions used for sharding are not deterministic, so the same key can land on different shards each time
- [ ] C: `mod N` sharding only works for numeric keys, not string keys like `tenant_id`
- [ ] D: A well-chosen hash function always produces perfectly even distribution regardless of input skew

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's precise claim: hashing addresses distribution of already-uniform input, not skew
already present in the underlying data, which is exactly what a hot tenant represents.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [hash-sharding, input-skew]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What consistent hashing actually solves
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What problem does consistent hashing solve relative to plain `mod N` hashing, per the lesson —
and what problem does it NOT solve?

**OPTIONS:**
- [x] A: It minimizes the fraction of keys that move when the shard count changes; it does nothing for input skew, since a hot tenant's key still lands on one shard either way
- [ ] B: It eliminates hot shards entirely by rebalancing load automatically across all shards
- [ ] C: It solves input skew but makes adding a new shard more expensive than plain mod N hashing
- [ ] D: It guarantees perfectly even distribution regardless of the underlying key cardinality

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson is explicit that consistent hashing addresses re-sharding cost (fewer keys move), not
skew — it is a different problem from the one bucketing or tenant isolation address.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [consistent-hashing, resharding-cost]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Reading the shard-key comparison — Candidate A's skew ratio
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the worked shard-key comparison in the lesson, what is Candidate A's (`hash(tenant_id) mod 6`)
busiest-to-median skew ratio, and does it cross the lesson's hot-shard threshold?

**CODE_BLOCK:**
```
Shard 0: 800   Shard 1: 950   Shard 2: 6,300   Shard 3: 1,100
Shard 4: 1,650  Shard 5: 1,200
Busiest (shard 2, 6,300) / median (~1,100) = 5.7x
```

**OPTIONS:**
- [x] A: 5.7x, which crosses the lesson's stated 5x-or-greater hot-shard threshold
- [ ] B: 1.03x, which is normal variance and not a hot shard
- [ ] C: 45%, representing the largest tenant's overall traffic share rather than a shard ratio
- [ ] D: 6x, exactly matching the number of shards in the cluster

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The worked example computes 6,300 / ~1,100 = 5.7x, which the lesson explicitly states crosses the
5x-or-greater hot-shard threshold.

**LESSON_CONNECTION:** Concepts Covered, code block
**KEYWORDS:** [skew-ratio, hot-shard-threshold]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What Candidate B trades away
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Candidate B (`hash(claim_id) mod 6`, a random UUID) achieves a 1.03x skew ratio — nearly perfect
distribution. What does the lesson say this trades away?

**OPTIONS:**
- [x] A: Tenant-scoped query locality — a single tenant's claims are no longer co-located on one shard, so a "list this tenant's claims" query becomes a scatter-gather across all six shards
- [ ] B: Write durability, since random UUIDs cannot be indexed as efficiently as sequential IDs
- [ ] C: The ability to add new shards later without a resharding migration
- [ ] D: Read-after-write consistency for any query touching more than one shard

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's specific trade-off: distribution-optimal keys can destroy locality, turning the
platform's most common query pattern (tenant-scoped listing) into an expensive scatter-gather.

**LESSON_CONNECTION:** Concepts Covered, code block
**KEYWORDS:** [locality-tradeoff, scatter-gather]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Bucketing versus tenant isolation
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the lesson, what distinguishes when bucketing is the correct mitigation from when tenant
isolation (moving a tenant to a dedicated shard) is the correct mitigation?

**OPTIONS:**
- [x] A: Bucketing fixes a hot key whose own volume genuinely exceeds one shard's capacity; tenant isolation fixes a hot tenant whose volume is disruptive to shared-shard neighbors even if it would fit comfortably alone
- [ ] B: Bucketing is always preferred; tenant isolation is a legacy technique no longer used in modern sharded systems
- [ ] C: Tenant isolation is required whenever a tenant's ID hashes to a prime-numbered shard
- [ ] D: The two techniques are interchangeable and produce identical outcomes in every case

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson draws this distinction precisely: the two mitigations target different root causes —
raw volume exceeding shard capacity versus disruption to shared neighbors.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [bucketing, tenant-isolation]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why resharding uses dual-write-then-cutover, not an atomic flip
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist a resharding migration use a dual-write/backfill-then-cutover approach
rather than a single atomic "flip" of the shard mapping?

**OPTIONS:**
- [x] A: A dataset large enough to need resharding cannot actually be moved instantaneously, so a single atomic flip is not achievable without a full-system outage while the move happens
- [ ] B: AWS databases technically do not support atomic writes across shards under any circumstance
- [ ] C: Dual-write is required by regulatory compliance for any multi-tenant claims data
- [ ] D: An atomic flip would violate the shard key's hash function determinism

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The lesson's reasoning is about feasibility at scale — a large historical dataset cannot be moved
instantly, so a transition window with dual-write and backfill avoids an outage during the move.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [resharding, dual-write, backfill]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why small tenants were affected in the scenario
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did several small tenants see SLA-breaching p99 latency in the scenario, even though none of
them individually generated unusual traffic?

**OPTIONS:**
- [x] A: They shared a physical shard with the hot large tenant, so that shard's saturation degraded every tenant co-located on it, regardless of each individual tenant's own traffic share
- [ ] B: The small tenants' data was accidentally migrated to the wrong AWS region
- [ ] C: PolicyVault's health check was misconfigured for all tenants simultaneously
- [ ] D: A software bug in the claims API affected only tenants below a certain traffic threshold

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The scenario's mechanism is shared-shard blast radius — a hot tenant's saturation directly
degrades every other tenant co-located on the same physical shard.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [shared-shard-blast-radius, noisy-neighbor]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What must be verified before the migration cutover
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Per the scenario's resharding migration plan, what must be verified before cutting reads over to
the new bucketed mapping and stopping the dual write?

**OPTIONS:**
- [x] A: Row counts and a sample of query results match between the old and new shard locations
- [ ] B: The large tenant has stopped generating new claims entirely
- [ ] C: All six original shards have been fully decommissioned
- [ ] D: The bucketed shard count has been reduced back to a single shard

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
The scenario explicitly names this verification step — row-count and sample-result matching —
as the gate before cutover, consistent with the lesson's Evidence of Understanding.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [migration-verification, cutover-gate]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why bucketing was applied only to the large tenant
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE apply bucketing only to the identified hot tenant, leaving every other tenant's
plain `hash(tenant_id) mod 6` mapping untouched?

**OPTIONS:**
- [x] A: Only the hot tenant's volume actually exceeded one shard's capacity — applying bucketing universally would add scatter-gather cost to every other tenant's queries for no distribution benefit, since their own traffic was never skewed
- [ ] B: Bucketing can only be applied to one tenant per shard cluster at a time, by design
- [ ] C: The other tenants' data was not compatible with the bucketing key format
- [ ] D: Applying bucketing universally would have violated PolicyVault's regulatory retention requirement

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
This connects the mitigation choice back to the lesson's core principle — a targeted fix for the
specific cause of skew, not a blanket change that would cost other tenants' locality unnecessarily.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [targeted-mitigation, bucketing-scope]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->
