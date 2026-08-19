using System;
using System.Collections.Generic;
using System.Linq;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public static class KnowledgeAtlasSeedData
{
    public static void Seed(StudyTrackerContext db)
    {
        if (db.KnowledgeDomains.Any())
        {
            return; // Seed only once
        }

        // 1. Define 8 Domains
        var domains = new List<KnowledgeDomain>
        {
            new KnowledgeDomain { Slug = "agentic-ai", Name = "Agentic AI Core", Code = "DOM-AI", Description = "Foundations of GenAI, LLM landscape, prompt engineering, agent loops, and RAG architectures.", Icon = "bot", ColorHex = "#EF4444", OrderIndex = 1 },
            new KnowledgeDomain { Slug = "foundations", Name = "FDE Foundations", Code = "DOM-FND", Description = "Python toolchain, engineering workflows, advanced OOP, functional paradigms, testing, and Linux essentials.", Icon = "code", ColorHex = "#F59E0B", OrderIndex = 2 },
            new KnowledgeDomain { Slug = "backend", Name = "Backend Engineering & Data Systems", Code = "DOM-BE", Description = "HTTP, RESTful APIs, FastAPI, PostgreSQL internals, MVCC, full-text search, and event streaming with Kafka.", Icon = "database", ColorHex = "#3B82F6", OrderIndex = 3 },
            new KnowledgeDomain { Slug = "full-stack", Name = "Full-Stack FDE", Code = "DOM-FS", Description = "TypeScript, modern React, Next.js, Vercel AI SDK, streaming user interfaces, and product polish.", Icon = "layout", ColorHex = "#10B981", OrderIndex = 4 },
            new KnowledgeDomain { Slug = "cloud", Name = "Cloud, DevOps & Infrastructure", Code = "DOM-CLD", Description = "AWS core services, Docker production containers, Kubernetes orchestration, Helm, Terraform IaC, and GitOps.", Icon = "cloud", ColorHex = "#6366F1", OrderIndex = 5 },
            new KnowledgeDomain { Slug = "enterprise", Name = "Enterprise LLM Engineering", Code = "DOM-ENT", Description = "Enterprise discovery, production RAG pipelines, hybrid search, RAGAS evaluation, model routing, and safety guardrails.", Icon = "briefcase", ColorHex = "#8B5CF6", OrderIndex = 6 },
            new KnowledgeDomain { Slug = "agent-systems", Name = "Agent Systems & Integrations", Code = "DOM-AGT", Description = "Tool calling, Model Context Protocol (MCP), multi-agent swarms, human-in-the-loop workflows, and CRM connectors.", Icon = "cpu", ColorHex = "#EC4899", OrderIndex = 7 },
            new KnowledgeDomain { Slug = "reliability", Name = "Application Engineering & Reliability", Code = "DOM-REL", Description = "Multi-tenant design, PostgreSQL RLS, SOC2/GDPR compliance, k6 load testing, incident response, and SRE best practices.", Icon = "shield-check", ColorHex = "#14B8A6", OrderIndex = 8 }
        };

        db.KnowledgeDomains.AddRange(domains);
        db.SaveChanges();

        // 2. Define 8 Concepts
        var concepts = new List<KnowledgeConcept>
        {
            new KnowledgeConcept
            {
                Slug = "rag",
                Title = "RAG",
                SubLabel = "RAG Foundation",
                Summary = "Semantic document indexing, vector embeddings, chunking strategies, hybrid retrieval, and LLM grounding.",
                Description = "RAG bridges static LLM weights and dynamic enterprise data using vector search (pgvector/Pinecone), BM25 hybrid ranking, and automated RAGAS evaluation.",
                Difficulty = "Advanced",
                Icon = "sparkles",
                EstimatedHours = 20,
                OrderIndex = 1
            },
            new KnowledgeConcept
            {
                Slug = "apis",
                Title = "APIs",
                SubLabel = "APIs Databases Concurrency",
                Summary = "REST, gRPC, WebSockets, Server-Sent Events (SSE), and idempotency design for high-throughput AI backends.",
                Description = "Comprehensive API architectural patterns covering HTTP/3, FastAPI dependency injection, streaming token payloads, and rate-limited connector design.",
                Difficulty = "Intermediate",
                Icon = "plug",
                EstimatedHours = 15,
                OrderIndex = 2
            },
            new KnowledgeConcept
            {
                Slug = "databases",
                Title = "Databases",
                SubLabel = "Databases, Concurrency",
                Summary = "PostgreSQL query optimization, MVCC internals, JSONB indexing, pgvector HNSW indexing, and dimensional modeling.",
                Description = "Deep dive into database storage engines, B-Tree vs GIN vs IVFFlat/HNSW vector indices, EXPLAIN ANALYZE interpretation, and connection pooling.",
                Difficulty = "Advanced",
                Icon = "database",
                EstimatedHours = 25,
                OrderIndex = 3
            },
            new KnowledgeConcept
            {
                Slug = "concurrency",
                Title = "Concurrency",
                SubLabel = "Java Concurrency",
                Summary = "Event loops, async/await coroutines, thread pooling, distributed locks, and Celery background workers.",
                Description = "Mastering asynchronous execution in Python and Java, race condition mitigation, thread-safe memory models, and queue-backed worker pipelines.",
                Difficulty = "Intermediate",
                Icon = "zap",
                EstimatedHours = 18,
                OrderIndex = 4
            },
            new KnowledgeConcept
            {
                Slug = "networking",
                Title = "Networking",
                SubLabel = "",
                Summary = "VPC CIDR subnets, NAT gateways, DNS, TLS termination, and Kubernetes CNI / Ingress controllers.",
                Description = "Essential networking topologies for scalable cloud services, service discovery, load balancing algorithms, and secure container overlays.",
                Difficulty = "Intermediate",
                Icon = "network",
                EstimatedHours = 16,
                OrderIndex = 5
            },
            new KnowledgeConcept
            {
                Slug = "caching",
                Title = "Caching",
                SubLabel = "Caching Processing",
                Summary = "Redis data structures, cache-aside/write-through policies, semantic prompt caching, and Redis Streams.",
                Description = "Strategies to reduce LLM latency and database query pressure using TTL policies, distributed locks, and embedding-similarity cache hits.",
                Difficulty = "Intermediate",
                Icon = "server",
                EstimatedHours = 12,
                OrderIndex = 6
            },
            new KnowledgeConcept
            {
                Slug = "observability",
                Title = "Observability",
                SubLabel = "Observability",
                Summary = "OpenTelemetry instrumentation, trace context propagation (W3C), Prometheus metrics, and Grafana telemetry.",
                Description = "Complete visibility into distributed microservices and LLM pipelines, tracing token latency, agent tool execution, and error budgets.",
                Difficulty = "Advanced",
                Icon = "activity",
                EstimatedHours = 14,
                OrderIndex = 7
            },
            new KnowledgeConcept
            {
                Slug = "security",
                Title = "Security",
                SubLabel = "Security",
                Summary = "OAuth2/OIDC, JWT signing, AWS KMS encryption, prompt injection guardrails, and Postgres Row Level Security (RLS).",
                Description = "Hardening enterprise AI applications against data exfiltration, role-based authorization, secrets rotation, and compliance enforcement (SOC2/GDPR).",
                Difficulty = "Advanced",
                Icon = "lock",
                EstimatedHours = 16,
                OrderIndex = 8
            }
        };

        db.KnowledgeConcepts.AddRange(concepts);
        db.SaveChanges();

        // 3. Connect Domains and Concepts
        var domMap = db.KnowledgeDomains.ToDictionary(d => d.Slug, d => d.Id);
        var conMap = db.KnowledgeConcepts.ToDictionary(c => c.Slug, c => c.Id);

        var connections = new List<DomainConceptConnection>
        {
            new() { DomainId = domMap["agentic-ai"], ConceptId = conMap["rag"], IsPrimary = true, RelevanceWeight = 10, RoleDescription = "Core vector retrieval and semantic memory layer", OrderIndex = 1 },
            new() { DomainId = domMap["agentic-ai"], ConceptId = conMap["apis"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "LLM endpoints & completions interface", OrderIndex = 2 },
            new() { DomainId = domMap["foundations"], ConceptId = conMap["apis"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "HTTP/REST protocol fundamentals", OrderIndex = 1 },
            new() { DomainId = domMap["foundations"], ConceptId = conMap["databases"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "Relational data structures & normalization", OrderIndex = 2 },
            new() { DomainId = domMap["foundations"], ConceptId = conMap["concurrency"], IsPrimary = true, RelevanceWeight = 10, RoleDescription = "Asyncio, threading & memory model", OrderIndex = 3 },
            new() { DomainId = domMap["foundations"], ConceptId = conMap["networking"], IsPrimary = false, RelevanceWeight = 7, RoleDescription = "Socket & protocol architecture", OrderIndex = 4 },
            new() { DomainId = domMap["backend"], ConceptId = conMap["apis"], IsPrimary = true, RelevanceWeight = 10, RoleDescription = "FastAPI / Spring backend contracts", OrderIndex = 1 },
            new() { DomainId = domMap["backend"], ConceptId = conMap["databases"], IsPrimary = true, RelevanceWeight = 10, RoleDescription = "PostgreSQL internals & indexing", OrderIndex = 2 },
            new() { DomainId = domMap["backend"], ConceptId = conMap["concurrency"], IsPrimary = false, RelevanceWeight = 9, RoleDescription = "Background job workers & message queues", OrderIndex = 3 },
            new() { DomainId = domMap["backend"], ConceptId = conMap["caching"], IsPrimary = true, RelevanceWeight = 10, RoleDescription = "Redis caching & pub/sub", OrderIndex = 4 },
            new() { DomainId = domMap["backend"], ConceptId = conMap["security"], IsPrimary = false, RelevanceWeight = 9, RoleDescription = "Auth, JWT & access control", OrderIndex = 5 },
            new() { DomainId = domMap["full-stack"], ConceptId = conMap["apis"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "Streaming SSE & client integrations", OrderIndex = 1 },
            new() { DomainId = domMap["full-stack"], ConceptId = conMap["caching"], IsPrimary = false, RelevanceWeight = 7, RoleDescription = "Client-side SWR / React Query caching", OrderIndex = 2 },
            new() { DomainId = domMap["cloud"], ConceptId = conMap["networking"], IsPrimary = true, RelevanceWeight = 10, RoleDescription = "AWS VPC, NAT, Route53 & DNS", OrderIndex = 1 },
            new() { DomainId = domMap["cloud"], ConceptId = conMap["observability"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "CloudWatch & Prometheus telemetry", OrderIndex = 2 },
            new() { DomainId = domMap["cloud"], ConceptId = conMap["security"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "IAM roles & KMS secrets", OrderIndex = 3 },
            new() { DomainId = domMap["enterprise"], ConceptId = conMap["rag"], IsPrimary = false, RelevanceWeight = 9, RoleDescription = "Enterprise document search & RAGAS eval", OrderIndex = 1 },
            new() { DomainId = domMap["enterprise"], ConceptId = conMap["databases"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "Vector databases (Pinecone/pgvector)", OrderIndex = 2 },
            new() { DomainId = domMap["enterprise"], ConceptId = conMap["caching"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "Semantic prompt & embedding caching", OrderIndex = 3 },
            new() { DomainId = domMap["enterprise"], ConceptId = conMap["security"], IsPrimary = false, RelevanceWeight = 9, RoleDescription = "Prompt injection defense & guardrails", OrderIndex = 4 },
            new() { DomainId = domMap["agent-systems"], ConceptId = conMap["rag"], IsPrimary = false, RelevanceWeight = 9, RoleDescription = "Dynamic grounding for agent tools", OrderIndex = 1 },
            new() { DomainId = domMap["agent-systems"], ConceptId = conMap["apis"], IsPrimary = false, RelevanceWeight = 9, RoleDescription = "Model Context Protocol (MCP) integrations", OrderIndex = 2 },
            new() { DomainId = domMap["reliability"], ConceptId = conMap["concurrency"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "Deadlock prevention & thread safety", OrderIndex = 1 },
            new() { DomainId = domMap["reliability"], ConceptId = conMap["databases"], IsPrimary = false, RelevanceWeight = 9, RoleDescription = "Multi-tenant isolation & Postgres RLS", OrderIndex = 2 },
            new() { DomainId = domMap["reliability"], ConceptId = conMap["networking"], IsPrimary = false, RelevanceWeight = 8, RoleDescription = "Ingress controllers & Pod networking", OrderIndex = 3 },
            new() { DomainId = domMap["reliability"], ConceptId = conMap["observability"], IsPrimary = true, RelevanceWeight = 10, RoleDescription = "OpenTelemetry tracing & SRE SLOs", OrderIndex = 4 },
            new() { DomainId = domMap["reliability"], ConceptId = conMap["security"], IsPrimary = true, RelevanceWeight = 10, RoleDescription = "SOC2 / GDPR compliance & audit trails", OrderIndex = 5 }
        };

        db.DomainConceptConnections.AddRange(connections);
        db.SaveChanges();

        // 4. Seed Concept Prerequisites
        var prereqs = new List<ConceptPrerequisite>
        {
            new() { ConceptId = conMap["concurrency"], PrerequisiteConceptId = conMap["concurrency"], Status = "included" },
            new() { ConceptId = conMap["rag"], PrerequisiteConceptId = conMap["databases"], Status = "included" },
            new() { ConceptId = conMap["rag"], PrerequisiteConceptId = conMap["apis"], Status = "included" },
            new() { ConceptId = conMap["apis"], PrerequisiteConceptId = conMap["networking"], Status = "included" },
            new() { ConceptId = conMap["caching"], PrerequisiteConceptId = conMap["databases"], Status = "included" },
            new() { ConceptId = conMap["observability"], PrerequisiteConceptId = conMap["apis"], Status = "included" },
            new() { ConceptId = conMap["security"], PrerequisiteConceptId = conMap["networking"], Status = "included" }
        };

        db.ConceptPrerequisites.AddRange(prereqs);
        db.SaveChanges();

        // 5. Seed Concept Next Lessons
        var nextLessons = new List<ConceptNextLesson>
        {
            new() { ConceptId = conMap["concurrency"], LessonTitle = "Java Concurrency", ModuleName = "Java & Spring Architecture", LessonSlug = "java-concurrency", OrderIndex = 1 },
            new() { ConceptId = conMap["concurrency"], LessonTitle = "Structured Concurrency", ModuleName = "Java & Spring Architecture", LessonSlug = "structured-concurrency", OrderIndex = 2 },
            new() { ConceptId = conMap["concurrency"], LessonTitle = "Next Security", ModuleName = "Application Engineering & Reliability", LessonSlug = "next-security", OrderIndex = 3 },
            new() { ConceptId = conMap["rag"], LessonTitle = "RAG Architecture: Ingestion & Retrieval", ModuleName = "Enterprise LLM Engineering", LessonSlug = "rag-ingestion-retrieval", OrderIndex = 1 },
            new() { ConceptId = conMap["apis"], LessonTitle = "FastAPI & RESTful Design", ModuleName = "Backend Engineering", LessonSlug = "fastapi-rest-design", OrderIndex = 1 },
            new() { ConceptId = conMap["databases"], LessonTitle = "Postgres Internals: Indexing & MVCC", ModuleName = "Backend Engineering", LessonSlug = "postgres-internals-mvcc", OrderIndex = 1 },
            new() { ConceptId = conMap["networking"], LessonTitle = "AWS VPC, Subnets & Routing", ModuleName = "Cloud & Infrastructure", LessonSlug = "aws-vpc-routing", OrderIndex = 1 },
            new() { ConceptId = conMap["caching"], LessonTitle = "Redis Streams & Caching Policies", ModuleName = "Backend Engineering", LessonSlug = "redis-caching-policies", OrderIndex = 1 },
            new() { ConceptId = conMap["observability"], LessonTitle = "OpenTelemetry Distributed Tracing", ModuleName = "Reliability", LessonSlug = "opentelemetry-tracing", OrderIndex = 1 },
            new() { ConceptId = conMap["security"], LessonTitle = "Auth: OAuth2, JWT & RBAC", ModuleName = "Reliability", LessonSlug = "auth-oauth2-jwt", OrderIndex = 1 }
        };

        db.ConceptNextLessons.AddRange(nextLessons);
        db.SaveChanges();

        Console.WriteLine("Knowledge Atlas seeding completed successfully.");
    }
}
