# 85-Day Interview Prep Roadmap: Java → AI Engineering → FDE → Cloud
## For Senior Backend Roles in India (7+ yrs exp)

**Reality:** You have 85 days max before interview season heats up.  
**Goal:** Build a portfolio that shows mastery across Java, AI engineering, system design, and cloud.  
**Strategy:** Use Neuralascent as the vehicle to learn all four areas.

---

## What Senior Roles in India Actually Want (2026)

Based on your market analysis (Hyderabad JDs Jan 2025 - Aug 2026):

```
✅ REQUIRED (every job)
   - Java 17+ with Spring Boot 3+
   - SQL + database optimization
   - REST API design + contract evolution
   - Authentication & authorization patterns
   - Transaction handling & idempotency
   - Testing (unit + integration)

✅ HIGHLY DESIRED (80% of postings)
   - LangChain / LLM integration (AI engineering)
   - RAG architecture + evaluation
   - Database design (schema, indices, query optimization) — FDE
   - Docker + Kubernetes (orchestration)
   - AWS (EC2, RDS, S3, Lambda)
   - System design (scale to 1M requests/day)

🟡 NICE TO HAVE (50% of postings)
   - Redis / caching strategies
   - Message queues (Kafka, RabbitMQ)
   - Observability (Prometheus, ELK)
   - Load balancing, CDN concepts
```

**Your gap:** FDE + Cloud infrastructure (those are the interview blockers).

---

## The 85-Day Plan: Four Phases

### **Phase 1: 30 Days (120 hrs/week) — Java/Spring Foundation**
**Goal:** Ship Sprints 1-9 of NeuralAscent  
**Outcome:** Working platform, secure auth, AI gateway with cost controls  
**Interview value:** "I built a multi-user platform with Spring Security, Spring Data JPA, and cost-managed AI calls"

### **Phase 2: 20 Days (80 hrs/week) — AI Engineering Vertical**
**Goal:** Add RAG + evaluation to Neuralascent, learn LangChain patterns  
**Outcome:** Cross-vertical retrieval, retrieval evaluation, cost-per-query metrics  
**Interview value:** "I implemented RAG with access control, metadata filtering, and evaluation harness"

### **Phase 3: 20 Days (80 hrs/week) — FDE Vertical (System Design)**
**Goal:** Deep-dive PostgreSQL optimization, schema design, query performance  
**Outcome:** Indexed queries, optimized joins, scalable architecture  
**Interview value:** "I designed a schema to handle 1M+ lessons with sub-100ms queries"

### **Phase 4: 15 Days (60 hrs/week) — AWS/Docker/Kubernetes**
**Goal:** Containerize, deploy to AWS, set up CI/CD  
**Outcome:** Multi-container app on ECS/EKS, automated deployments  
**Interview value:** "I containerized a Java app, deployed to AWS ECS, set up Kubernetes for scaling"

---

## Phase 1: Days 1-30 (120 hrs/week) — Java/Spring MVP
**Sprints 1-9: Identity → Support**

### Daily Breakdown (17 hrs/day)

**Week 1: Sprints 1-2 (Identity + Auth)**
```
Mon-Tue: AppUser + Spring Security + login
         (17 hrs each)
Wed:      Registration flow + invitations
         (17 hrs)
Thu-Fri:  Authorization policies + access control
         (17 hrs each)
Sat-Sun:  Buffer + integration tests
         (17 hrs total)
```

**Week 2: Sprint 3 (AI Gateway)**
```
Mon-Tue: Provider interfaces + admission pipeline
         (17 hrs each)
Wed-Thu: Rate limiting + quota management
         (17 hrs each)
Fri:      Muse Spark adapter + circuit breaker
         (17 hrs)
Sat-Sun:  Buffer + tests
         (17 hrs total)
```

**Week 3: Sprint 4-5 (Tutor + Admin)**
```
Mon-Tue: Tutor context resolver + progressive hints
         (17 hrs each)
Wed-Thu: SSE streaming + tutor service
         (17 hrs each)
Fri:      Admin dashboard + operational controls
         (17 hrs)
Sat-Sun:  Buffer + integration tests
         (17 hrs total)
```

**Week 4: Sprints 6-9 (State + Support)**
```
Mon-Tue: Learner progress persistence
         (17 hrs each)
Wed-Thu: Conversation memory + ownership
         (17 hrs each)
Fri:      Telemetry + support tickets
         (17 hrs)
Sat-Sun:  Final polish + deployment to staging
         (17 hrs total)
```

### Phase 1 Deliverable

```
✅ Working NeuralAscent platform (Sprints 1-9)
✅ ~9,000 lines of production Java
✅ Secure (Spring Security)
✅ Cost-controlled (rate limits + quotas)
✅ Can demo live
✅ GitHub repo with 30 days of commits

Interview talking point:
"I built a multi-user learning platform with Spring Boot,
Spring Data JPA, Spring Security, and implemented a cost-managed
AI gateway with rate limiting and quota enforcement. The system
handles authentication, authorization, and progressive disclosure
of hints based on user policy."
```

### Interview Q&A You Can Answer After Phase 1

```
Q: "Tell me about your authentication design"
A: "Used Spring Security with HttpOnly cookies, CSRF protection,
   password BCrypt hashing. Invitations for registration, email
   validation. Suspension prevents login at CustomUserDetailsService."

Q: "How do you prevent unauthorized access?"
A: "Every endpoint has @PreAuthorize checks. Lessons loaded after
   authorization, not before. Cross-vertical access denied at policy
   layer before retrieval. No user A can see user B's conversations."

Q: "How do you handle expensive API calls?"
A: "Admission control pipeline: rate limit → quota check → budget
   check → token estimate → reserve atomically. Provider call only
   after all checks pass. Token reconciliation after response."

Q: "What design patterns did you use?"
A: "Adapter (provider-neutral interface), Strategy (tutor routing),
   Factory (repository patterns with Spring Data), Repository
   (data access abstraction), Builder (DTOs with Lombok)."
```

---

## Phase 2: Days 31-50 (80 hrs/week) — AI Engineering Vertical
**Sprints 10-11: RAG + Evaluation**

### What to Build

**RAG Implementation (10 days, 40 hrs):**
- [ ] Add pgvector to PostgreSQL
- [ ] Content ingestion pipeline (chunk lessons with metadata)
- [ ] Embedding model selection (OpenAI or local)
- [ ] Similarity search with metadata filtering
- [ ] Access-controlled retrieval (enforce vertical boundaries)
- [ ] Hybrid search (full-text + vector)
- [ ] Reranking (optional, for quality)
- [ ] Integration with tutor (use RAG chunks in prompt)

**Evaluation Harness (10 days, 40 hrs):**
- [ ] Build evaluation datasets:
  - Query + expected chunks (retrieval correctness)
  - Query + expected tutor response (tutoring quality)
  - Cross-vertical query + denied access (security)
- [ ] Implement evaluation metrics:
  - NDCG (retrieval ranking quality)
  - MRR (mean reciprocal rank)
  - Precision@K, Recall@K
  - Response correctness (semantic similarity to ground truth)
- [ ] A/B testing framework (compare routes/models)
- [ ] Cost per completed exercise metric

### How This Connects to Your AI Engineering Vertical

**Your site has Java LLD + AI Engineering verticals.**

**Use them:**
1. **Java LLD:** Reference for design patterns, OOP concepts used in RAG
2. **AI Engineering:** Reference for RAG architecture, evaluation frameworks

**Build:**
```
NeuralAscent AI Engineering Vertical:
├─ Lesson 1: RAG fundamentals
│  └─ Your RAG implementation IS the lesson content
├─ Lesson 2: Metadata filtering
│  └─ Your cross-vertical access control IS the example
├─ Lesson 3: Evaluation & metrics
│  └─ Your evaluation harness IS the working code
└─ Lesson 4: Cost optimization
   └─ Your per-query cost tracking IS the case study
```

**Interview value:**
"I built RAG for a multi-vertical learning platform. Implemented
metadata filtering to enforce access control — learners can't retrieve
concepts from verticals they're not enrolled in. Built evaluation
harness to measure retrieval quality (NDCG, MRR) and tutoring
effectiveness. Tracks cost per completed exercise."

### Interview Q&A After Phase 2

```
Q: "What's a retrieval pipeline you've built?"
A: "Chunk curriculum by heading + example + exercise. Index with
   pgvector embeddings + metadata (vertical, lesson_id, access_level).
   Similarity search returns filtered chunks based on user policy.
   Rerank by relevance if needed."

Q: "How do you prevent unauthorized RAG access?"
A: "Metadata filters applied in WHERE clause before similarity search.
   Denied vertical chunks never retrieved, never sent to LLM. Tested
   with adversarial queries (e.g., 'explain FDE' from Java learner)."

Q: "How do you measure if RAG is working?"
A: "Evaluation dataset: 50 queries with ground truth chunks. Measure
   NDCG@5 (ranked retrieval quality), MRR (first relevant rank),
   Precision/Recall. Compare different retrieval strategies."

Q: "What about cost per query?"
A: "Track input tokens (including cached prompt), output tokens,
   reasoning tokens (model-specific). Calculate cost per query.
   Optimize: expensive models only for complex queries, cheaper for simple."
```

---

## Phase 3: Days 51-70 (80 hrs/week) — FDE Vertical (System Design)
**Database Optimization + Scalability**

### What to Study & Build

**FDE Concepts (from your FDE vertical):**
- [ ] Indexing strategies (B-tree, hash, bitmaps, partial indices)
- [ ] Query optimization (EXPLAIN ANALYZE, execution plans)
- [ ] Schema design for scale (normalization vs. denormalization)
- [ ] Partitioning (time-based, hash-based, range-based)
- [ ] Caching strategies (Redis, query cache)
- [ ] Concurrency (MVCC, locks, isolation levels)
- [ ] Transaction design (idempotency, atomicity)

**Apply to NeuralAscent:**

1. **Indexing for your schema (5 days):**
   ```sql
   -- What queries are slow?
   SELECT lessons WHERE vertical_code = ? AND published = true
   → CREATE INDEX idx_lesson_vertical_published
   
   SELECT user_lesson_progress WHERE user_id = ? AND status = ?
   → CREATE INDEX idx_progress_user_status
   
   SELECT conversations WHERE owner_id = ?
   → CREATE INDEX idx_conversation_owner
   
   SELECT knowledge_chunks WHERE vertical_id IN (...)
   → CREATE INDEX idx_chunk_vertical
   ```

2. **Query optimization (3 days):**
   ```
   EXPLAIN ANALYZE your slow queries
   Find N+1 problems, missing joins, sequential scans
   Rewrite with proper JOINs + indexes
   Measure latency before/after
   ```

3. **Scaling design (5 days):**
   ```
   - Partitioning: Split knowledge_chunks by vertical (1000+ lessons)
   - Archiving: Old conversations move to archive table/schema
   - Materialized views: Pre-compute user progress aggregations
   - Caching: Redis for lesson content (immutable), user policy (TTL 1hr)
   ```

4. **Concurrency + transactions (4 days):**
   ```
   - Quota reservation must be atomic (SELECT + UPDATE in transaction)
   - Conversation ownership checks use row-level locks if needed
   - Progress updates use optimistic locking (version field)
   - Idempotency: conversation message with client request ID unique
   ```

5. **Load testing (3 days):**
   ```
   - Simulate 100 concurrent users
   - Each sends 6 messages/min
   - Measure latency at P50/P95/P99
   - Find bottleneck (DB? API? LLM?)
   - Optimize accordingly
   ```

### Build on Top of Java LLD Vertical

Your FDE vertical teaches database design principles. **Use it:**
1. Extract key concepts (indexing, query optimization, scaling)
2. Apply them to NeuralAscent schema
3. Document: "Here's how I optimized queries for 1M+ lessons"
4. Measurements: "Latency went from 200ms → 45ms after indexing"

### Interview Q&A After Phase 3

```
Q: "How would you scale this to 1M+ lessons?"
A: "Partition knowledge_chunks table by vertical (reduces index size).
   Materialized view for user progress aggregation. Cache lesson
   content in Redis (immutable, TTL 24h). Archive conversations >90d.
   Read replicas for reporting queries. Optimized indexes on access
   patterns (vertical, user_id, status)."

Q: "Tell me about a complex query you optimized"
A: "Query to get user progress + lesson metadata + hint count across
   multiple lessons. Initial: 3 joins, no index = 500ms.
   Optimized: Added index on (user_id, lesson_id, status), used
   aggregate functions, reduced joins = 45ms. Measured with EXPLAIN ANALYZE."

Q: "How do you handle concurrency?"
A: "Quota reservation uses SELECT … FOR UPDATE to lock row,
   preventing concurrent overspend. Conversation inserts use unique
   constraint on (owner_id, client_request_id) for idempotency.
   Progress updates use optimistic locking (version field, check
   version on update)."

Q: "What if you scale to 10x traffic?"
A: "Identified bottleneck: quiz attempt table getting full scan.
   Added index (user_id, lesson_id, created_at). Added read replica
   for analytics queries. Cached frequently-accessed lessons in Redis.
   Partitioned old data. These changes reduced P95 latency from 400ms → 120ms."
```

---

## Phase 4: Days 71-85 (60 hrs/week) — AWS/Docker/Kubernetes
**Containerization + Cloud Deployment**

### What to Build (15 days, 60 hrs)

**Docker (3-4 days, 12-16 hrs):**
- [ ] Write Dockerfile for Java app (multi-stage build)
- [ ] Dockerfile for PostgreSQL (optional, can use AWS RDS)
- [ ] docker-compose.yml locally (app + postgres + redis)
- [ ] Image optimization (small base, layer caching)
- [ ] Build & push to ECR (AWS Elastic Container Registry)

**Kubernetes Basics (4-5 days, 16-20 hrs):**
- [ ] Understand Kubernetes concepts (Pod, Service, Deployment, ConfigMap)
- [ ] Write Deployment YAML for NeuralAscent Java app
- [ ] ConfigMap for DB connection, API keys
- [ ] Service for load balancing across pods
- [ ] StatefulSet for PostgreSQL (or use AWS RDS)
- [ ] Deploy to minikube or EKS (AWS Kubernetes)
- [ ] Scaling example: "kubectl scale deployment neuralascent --replicas=3"

**AWS (4-5 days, 16-20 hrs):**
- [ ] EC2: Launch instance, SSH in, run Docker container manually
- [ ] RDS: Create PostgreSQL instance, connect from EC2
- [ ] ECR: Push Docker image to registry
- [ ] ECS: Define task, service, load balancer (simpler alternative to EKS)
- [ ] S3: Store backup data / artifacts
- [ ] CloudFront: CDN for static assets (React frontend)
- [ ] Cost monitoring (CloudWatch, billing)

**CI/CD Pipeline (2-3 days, 8-12 hrs):**
- [ ] GitHub Actions: Run tests on push
- [ ] Build Docker image on main branch
- [ ] Push to ECR automatically
- [ ] Deploy to ECS/EKS automatically
- [ ] Rollback strategy

### Minimal Setup to Demo

```yaml
# docker-compose.yml (local)
version: '3.8'
services:
  neuralascent:
    build: .
    ports:
      - "8080:8080"
    environment:
      DB_URL: jdbc:postgresql://db:5432/neuralascent
      REDIS_URL: redis://redis:6379
  
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: neuralascent
      POSTGRES_PASSWORD: secret
  
  redis:
    image: redis:7-alpine
```

```bash
# Deploy to AWS ECS
aws ecs create-service \
  --cluster neuralascent \
  --service-name neuralascent-api \
  --task-definition neuralascent-task \
  --desired-count 3 \
  --load-balancers targetGroupArn=arn:...,containerName=neuralascent,containerPort=8080
```

### Interview Q&A After Phase 4

```
Q: "How would you containerize this application?"
A: "Multi-stage Dockerfile: build stage compiles Java with Maven,
   runtime stage uses slim JRE image, copies JAR. Optimized for layer
   caching (dependencies don't change often). Push to ECR for
   production deployments."

Q: "How would you deploy to Kubernetes?"
A: "Deployment manifest specifies 3 replicas of the app pod.
   ConfigMap for database connection, API keys. Service load balances
   across pods. PersistentVolume for postgres (or use managed RDS).
   kubectl apply -f deployment.yaml handles rollout."

Q: "How would you set up scaling?"
A: "HorizontalPodAutoscaler monitors CPU/memory. If average CPU > 70%,
   scales to max 10 replicas. If < 30%, scales down. Pod disruption
   budgets prevent cascading failures. Handled by Kubernetes automatically."

Q: "What about CI/CD?"
A: "GitHub Actions runs tests on every push. If tests pass, builds
   Docker image, tags with git commit, pushes to ECR. Triggers
   deployment to ECS. Deployment controller rolls out gradually,
   monitors health, rolls back if >5% errors."

Q: "How do you monitor costs?"
A: "CloudWatch tracks pod resource usage. S3 bucket storage costs.
   RDS instance type (storage + compute). Set billing alarms for
   budget ($100/month limit). Use Spot instances for non-critical workloads."
```

---

## Timeline Visualization

```
Days 1-30 (120 hrs/week):  ████████████████████████████
   Sprints 1-9: Working platform

Days 31-50 (80 hrs/week):  ████████████████
   Sprints 10-11: RAG + evaluation

Days 51-70 (80 hrs/week):  ████████████████
   FDE: Database optimization + scaling

Days 71-85 (60 hrs/week):  ████████
   Docker + Kubernetes + AWS

Total: 85 days
Total hours: ~8,200 hours (or ~116 hrs/week average)
```

---

## What Your Portfolio Looks Like by Day 85

### GitHub Repository: `neuralascent-java-migration`

```
✅ Sprints 1-9: Full working platform
   - 9,000 LOC Java/Spring
   - Secure auth + authorization
   - AI gateway with cost controls
   - Tutor with SSE streaming
   - Admin dashboard
   - Support system

✅ Sprint 10-11: RAG + evaluation
   - pgvector integration
   - Retrieval evaluation suite
   - Metadata filtering
   - Cost per query tracking

✅ FDE optimization
   - PostgreSQL schema optimized (indices, partitioning)
   - Query performance measurements (200ms → 45ms)
   - Concurrency & transaction design
   - Load testing results

✅ Docker + Kubernetes
   - Multi-stage Dockerfile
   - Kubernetes manifests (Deployment, Service, ConfigMap)
   - CI/CD pipeline (GitHub Actions → ECR → ECS)
   - AWS deployment (RDS, S3, CloudFront)

📊 ~12,000 total lines of production code
📈 30+ integration tests, load tests, evaluation metrics
📚 Comprehensive README with architecture diagrams
🎯 Interview talking points for every phase
```

### Interview Pitch (60 seconds)

```
"I built NeuralAscent, a multi-user AI learning platform in Java/Spring.
It has secure authentication with Spring Security, role-based authorization,
and a cost-managed AI gateway with rate limiting and quota enforcement.

I implemented RAG for cross-lesson retrieval with access control—learners
can't retrieve content from verticals they're not enrolled in. Built an
evaluation harness to measure retrieval quality and tutoring effectiveness.

I optimized the PostgreSQL schema for scale: added strategic indices,
reduced query latency from 200ms to 45ms. Tested with 100 concurrent users.

I containerized it with Docker, deployed to AWS ECS, and set up CI/CD
with GitHub Actions. The system auto-scales and has monitoring/alerts.

Total: ~12K lines of production code across Java, RAG, system design,
and cloud infrastructure."
```

---

## What Interviewers Will Ask

### After Phase 1 (Days 1-30)
```
□ Authentication/authorization design
□ Spring Security patterns
□ API contract evolution
□ Rate limiting + quota strategies
□ Testing approach
□ Transactional semantics
```

### After Phase 2 (Days 31-50)
```
□ RAG architecture + tradeoffs
□ Metadata filtering for access control
□ Evaluation frameworks for LLM output
□ Cost optimization for LLM calls
□ Embedding model choices
```

### After Phase 3 (Days 51-70)
```
□ Database indexing strategy
□ Query optimization + EXPLAIN ANALYZE
□ Scaling to 1M+ records
□ Concurrency control
□ Caching strategies
□ Transaction isolation levels
```

### After Phase 4 (Days 71-85)
```
□ Containerization best practices
□ Kubernetes vs. ECS vs. serverless
□ CI/CD pipeline design
□ AWS services selection
□ Cost monitoring
□ Disaster recovery / high availability
```

---

## How to Use Your Existing Verticals

You already have:
- **Java LLD Vertical:** Reference while building
- **AI Engineering Vertical:** Use as reference + contribute lessons based on your RAG implementation
- **FDE Vertical:** Use as reference for database design principles

**Strategy:**
```
Week 1-4 (Phase 1):
  - Read Java LLD lessons on interfaces, design patterns
  - Implement them in NeuralAscent
  - Note how patterns appear in real code

Week 5-6 (Phase 2):
  - Read AI Engineering vertical on RAG
  - Implement RAG in NeuralAscent
  - Notice connection between lesson content + your code

Week 7-8 (Phase 3):
  - Read FDE vertical on indexing, optimization
  - Optimize your schema
  - Document measurements in your repo

Week 9-12 (Phase 4):
  - Use AWS documentation
  - Deploy your platform
  - Write case study: "Scaling a Java app to AWS"
```

---

## Success Metrics by Day 85

**Code Quality:**
- [ ] 70%+ test coverage
- [ ] 0 security issues (no SQL injection, XSS, CSRF)
- [ ] Latency P95 < 200ms for most queries
- [ ] Handles 100 concurrent users

**Portfolio:**
- [ ] GitHub repo with 85 days of commit history
- [ ] ~12K lines of production code
- [ ] Comprehensive README with diagrams
- [ ] Running on AWS (live URL to demo)
- [ ] Blog post or case study: "Building a scalable learning platform"

**Interview Readiness:**
- [ ] Can discuss auth, authorization, rate limiting in depth
- [ ] Can explain RAG architecture + tradeoffs
- [ ] Can discuss database optimization + scaling
- [ ] Can explain Docker/Kubernetes/AWS choices
- [ ] Can answer adversarial questions ("What if you scale 10x?")

---

## Daily Routine for 85 Days

```
6:00 AM: Wake up
6:30 AM: Review day's plan + last day's progress (30 min)
7:00 AM: Deep work - coding (4 hrs, minimize distractions)
11:00 AM: Breakfast + break (45 min)
11:45 AM: Deep work - coding (4 hrs)
3:45 PM: Lunch + break (45 min)
4:30 PM: Testing + debugging (3 hrs)
7:30 PM: Documentation + learning (2-3 hrs)
10:30 PM: Wrap up, prepare next day (30 min)
11:00 PM: Sleep (7 hrs minimum)

Weekly:
  Fri: Code review (self), test on staging
  Sat: Buffer day (fix bugs from week)
  Sun: Learning (read papers, watch videos, rest)
```

---

## Critical Checkpoints

### After Day 30 (Phase 1 done)
- [ ] Platform runs locally (docker-compose)
- [ ] GitHub has 30 days of commits
- [ ] Can demo to someone without explaining code
- [ ] All critical path tests passing
- **If behind:** Extend Phase 1 by 5 days, compress Phase 2

### After Day 50 (Phase 2 done)
- [ ] RAG retrieval works end-to-end
- [ ] Evaluation metrics computed
- [ ] Can explain retrieval + evaluation in interview
- [ ] Cost per query measured
- **If behind:** Extend Phase 2 by 5 days, focus on core RAG

### After Day 70 (Phase 3 done)
- [ ] Schema optimized
- [ ] Query performance improved measurably
- [ ] Load test completed
- [ ] Can explain scaling strategy
- **If behind:** Compress Phase 4 (Docker/K8s can be minimal)

### After Day 85 (Phase 4 done)
- [ ] App runs on AWS
- [ ] CI/CD automated
- [ ] Can demo live deployment
- [ ] Ready for interviews
- **If behind:** Use Day 86-90 for final polish

---

## If Interview Comes Early (Before Day 85)

**Day 45 ready:**
- Can discuss Sprints 1-9 thoroughly
- Can explain AI gateway + cost controls
- Can talk about Spring Security patterns
- **Missing:** RAG, database optimization, cloud

**Day 60 ready:**
- All of Day 45 +
- Can discuss RAG + evaluation
- Can explain retrieval + access control
- **Missing:** Database scaling, cloud

**Day 75 ready:**
- All of Day 60 +
- Can discuss database optimization
- Can explain scaling strategy
- **Missing:** Cloud deployment (minor)

**Day 85 ready:**
- Everything + cloud deployment
- Most interview-proof scenario

---

## In Your Interview

**Opening:**
```
"I just completed a 12-sprint migration of a learning platform from
.NET to Java. Let me walk you through what I built."
```

**Part 1: Java/Spring (first 15 min)**
```
- Architecture overview
- Authentication/authorization with Spring Security
- AI gateway design + admission control
- Rate limiting, quotas, cost management
- Testing approach
```

**Part 2: AI Engineering (next 10 min)**
```
- RAG implementation details
- Access control in retrieval
- Evaluation metrics
- Cost optimization
```

**Part 3: System Design (next 10 min)**
```
- Database schema optimization
- Query performance tuning
- Scaling to 1M+ records
- Concurrency control
```

**Part 4: Cloud (final 10 min)**
```
- Docker/Kubernetes deployment
- AWS services selection
- CI/CD pipeline
- Monitoring + cost management
```

**Close:**
```
"GitHub repo: [link]. Running live on AWS at [URL].
Happy to discuss any aspect in depth."
```

---

## One More Reality Check

**Can you do 85 days at stated intensity?**

```
Days 1-30:  120 hrs/week (full intensity)  ← Doable, but hard by week 3
Days 31-50: 80 hrs/week (recover)          ← Much better
Days 51-70: 80 hrs/week (steady)           ← Sustainable
Days 71-85: 60 hrs/week (light)            ← Easy finish

Total average: ~100 hrs/week over 85 days ✅ Sustainable
```

**vs. original 30-day plan:**
```
Days 1-30: 120 hrs/week                    ← Burnout risk
```

**85-day plan is actually MORE realistic** because it includes recovery weeks.

---

## Next Action: Pick Your Interview Date

1. **If interview is 30 days away:** Execute Phase 1 only, hope they ask mostly about Spring/Java
2. **If interview is 45 days away:** Phases 1-2 (Java + AI engineering)
3. **If interview is 60 days away:** Phases 1-3 (Java + AI + system design)
4. **If interview is 85+ days away:** All 4 phases, most interview-proof

What's your interview timeline?
