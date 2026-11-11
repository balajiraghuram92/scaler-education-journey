"""Ported from api/Data/KnowledgeAtlasSeedData.cs."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.concept_next_lesson import ConceptNextLesson
from ..models.concept_prerequisite import ConceptPrerequisite
from ..models.domain_concept_connection import DomainConceptConnection
from ..models.knowledge_concept import KnowledgeConcept
from ..models.knowledge_domain import KnowledgeDomain


async def seed(session: AsyncSession) -> None:
    exists = (await session.execute(select(KnowledgeDomain.id).limit(1))).first()
    if exists is not None:
        return  # Seed only once

    now = datetime.now(UTC)

    # 1. Define 8 Domains
    domains = [
        _domain("agentic-ai", "Agentic AI Core", "DOM-AI", "Foundations of GenAI, LLM landscape, prompt engineering, agent loops, and RAG architectures.", "bot", "#EF4444", 1, now),
        _domain("foundations", "FDE Foundations", "DOM-FND", "Python toolchain, engineering workflows, advanced OOP, functional paradigms, testing, and Linux essentials.", "code", "#F59E0B", 2, now),
        _domain("backend", "Backend Engineering & Data Systems", "DOM-BE", "HTTP, RESTful APIs, FastAPI, PostgreSQL internals, MVCC, full-text search, and event streaming with Kafka.", "database", "#3B82F6", 3, now),
        _domain("full-stack", "Full-Stack FDE", "DOM-FS", "TypeScript, modern React, Next.js, Vercel AI SDK, streaming user interfaces, and product polish.", "layout", "#10B981", 4, now),
        _domain("cloud", "Cloud, DevOps & Infrastructure", "DOM-CLD", "AWS core services, Docker production containers, Kubernetes orchestration, Helm, Terraform IaC, and GitOps.", "cloud", "#6366F1", 5, now),
        _domain("enterprise", "Enterprise LLM Engineering", "DOM-ENT", "Enterprise discovery, production RAG pipelines, hybrid search, RAGAS evaluation, model routing, and safety guardrails.", "briefcase", "#8B5CF6", 6, now),
        _domain("agent-systems", "Agent Systems & Integrations", "DOM-AGT", "Tool calling, Model Context Protocol (MCP), multi-agent swarms, human-in-the-loop workflows, and CRM connectors.", "cpu", "#EC4899", 7, now),
        _domain("reliability", "Application Engineering & Reliability", "DOM-REL", "Multi-tenant design, PostgreSQL RLS, SOC2/GDPR compliance, k6 load testing, incident response, and SRE best practices.", "shield-check", "#14B8A6", 8, now),
    ]
    session.add_all(domains)
    await session.flush()

    # 2. Define 8 Concepts
    concepts = [
        _concept("rag", "RAG", "RAG Foundation", "Semantic document indexing, vector embeddings, chunking strategies, hybrid retrieval, and LLM grounding.", "RAG bridges static LLM weights and dynamic enterprise data using vector search (pgvector/Pinecone), BM25 hybrid ranking, and automated RAGAS evaluation.", "Advanced", "sparkles", 20, 1, now),
        _concept("apis", "APIs", "APIs Databases Concurrency", "REST, gRPC, WebSockets, Server-Sent Events (SSE), and idempotency design for high-throughput AI backends.", "Comprehensive API architectural patterns covering HTTP/3, FastAPI dependency injection, streaming token payloads, and rate-limited connector design.", "Intermediate", "plug", 15, 2, now),
        _concept("databases", "Databases", "Databases, Concurrency", "PostgreSQL query optimization, MVCC internals, JSONB indexing, pgvector HNSW indexing, and dimensional modeling.", "Deep dive into database storage engines, B-Tree vs GIN vs IVFFlat/HNSW vector indices, EXPLAIN ANALYZE interpretation, and connection pooling.", "Advanced", "database", 25, 3, now),
        _concept("concurrency", "Concurrency", "Java Concurrency", "Event loops, async/await coroutines, thread pooling, distributed locks, and Celery background workers.", "Mastering asynchronous execution in Python and Java, race condition mitigation, thread-safe memory models, and queue-backed worker pipelines.", "Intermediate", "zap", 18, 4, now),
        _concept("networking", "Networking", "", "VPC CIDR subnets, NAT gateways, DNS, TLS termination, and Kubernetes CNI / Ingress controllers.", "Essential networking topologies for scalable cloud services, service discovery, load balancing algorithms, and secure container overlays.", "Intermediate", "network", 16, 5, now),
        _concept("caching", "Caching", "Caching Processing", "Redis data structures, cache-aside/write-through policies, semantic prompt caching, and Redis Streams.", "Strategies to reduce LLM latency and database query pressure using TTL policies, distributed locks, and embedding-similarity cache hits.", "Intermediate", "server", 12, 6, now),
        _concept("observability", "Observability", "Observability", "OpenTelemetry instrumentation, trace context propagation (W3C), Prometheus metrics, and Grafana telemetry.", "Complete visibility into distributed microservices and LLM pipelines, tracing token latency, agent tool execution, and error budgets.", "Advanced", "activity", 14, 7, now),
        _concept("security", "Security", "Security", "OAuth2/OIDC, JWT signing, AWS KMS encryption, prompt injection guardrails, and Postgres Row Level Security (RLS).", "Hardening enterprise AI applications against data exfiltration, role-based authorization, secrets rotation, and compliance enforcement (SOC2/GDPR).", "Advanced", "lock", 16, 8, now),
    ]
    session.add_all(concepts)
    await session.flush()

    # 3. Connect Domains and Concepts
    dom_map = {d.slug: d.id for d in domains}
    con_map = {c.slug: c.id for c in concepts}
    connections = [
        ("agentic-ai", "rag", True, 10, "Core vector retrieval and semantic memory layer", 1),
        ("agentic-ai", "apis", False, 8, "LLM endpoints & completions interface", 2),
        ("foundations", "apis", False, 8, "HTTP/REST protocol fundamentals", 1),
        ("foundations", "databases", False, 8, "Relational data structures & normalization", 2),
        ("foundations", "concurrency", True, 10, "Asyncio, threading & memory model", 3),
        ("foundations", "networking", False, 7, "Socket & protocol architecture", 4),
        ("backend", "apis", True, 10, "FastAPI / Spring backend contracts", 1),
        ("backend", "databases", True, 10, "PostgreSQL internals & indexing", 2),
        ("backend", "concurrency", False, 9, "Background job workers & message queues", 3),
        ("backend", "caching", True, 10, "Redis caching & pub/sub", 4),
        ("backend", "security", False, 9, "Auth, JWT & access control", 5),
        ("full-stack", "apis", False, 8, "Streaming SSE & client integrations", 1),
        ("full-stack", "caching", False, 7, "Client-side SWR / React Query caching", 2),
        ("cloud", "networking", True, 10, "AWS VPC, NAT, Route53 & DNS", 1),
        ("cloud", "observability", False, 8, "CloudWatch & Prometheus telemetry", 2),
        ("cloud", "security", False, 8, "IAM roles & KMS secrets", 3),
        ("enterprise", "rag", False, 9, "Enterprise document search & RAGAS eval", 1),
        ("enterprise", "databases", False, 8, "Vector databases (Pinecone/pgvector)", 2),
        ("enterprise", "caching", False, 8, "Semantic prompt & embedding caching", 3),
        ("enterprise", "security", False, 9, "Prompt injection defense & guardrails", 4),
        ("agent-systems", "rag", False, 9, "Dynamic grounding for agent tools", 1),
        ("agent-systems", "apis", False, 9, "Model Context Protocol (MCP) integrations", 2),
        ("reliability", "concurrency", False, 8, "Deadlock prevention & thread safety", 1),
        ("reliability", "databases", False, 9, "Multi-tenant isolation & Postgres RLS", 2),
        ("reliability", "networking", False, 8, "Ingress controllers & Pod networking", 3),
        ("reliability", "observability", True, 10, "OpenTelemetry tracing & SRE SLOs", 4),
        ("reliability", "security", True, 10, "SOC2 / GDPR compliance & audit trails", 5),
    ]
    session.add_all(
        DomainConceptConnection(
            domain_id=dom_map[d],
            concept_id=con_map[c],
            is_primary=primary,
            relevance_weight=weight,
            role_description=role,
            order_index=order,
        )
        for d, c, primary, weight, role, order in connections
    )
    await session.flush()

    # 4. Seed Concept Prerequisites
    for concept_slug, prereq_slug in [
        ("concurrency", "concurrency"),
        ("rag", "databases"),
        ("rag", "apis"),
        ("apis", "networking"),
        ("caching", "databases"),
        ("observability", "apis"),
        ("security", "networking"),
    ]:
        session.add(
            ConceptPrerequisite(
                concept_id=con_map[concept_slug],
                prerequisite_concept_id=con_map[prereq_slug],
                status="included",
            )
        )
    await session.flush()

    # 5. Seed Concept Next Lessons
    for concept_slug, title, module_name, lesson_slug, order in [
        ("concurrency", "Java Concurrency", "Java & Spring Architecture", "06-concurrency-1-threads", 1),
        ("concurrency", "Structured Concurrency", "Java & Spring Architecture", "structured-concurrency", 2),
        ("concurrency", "Next Security", "Application Engineering & Reliability", "next-security", 3),
        ("rag", "RAG Architecture: Ingestion & Retrieval", "Enterprise LLM Engineering", "07-rag-architecture-ingestion-and-retrieval", 1),
        ("apis", "FastAPI & RESTful Design", "Backend Engineering", "02-fastapi-intro-to-deep-dive", 1),
        ("databases", "Postgres Internals: Indexing & MVCC", "Backend Engineering", "10-postgres-internals-explain-analyze-indexing-and-mvcc", 1),
        ("networking", "AWS VPC, Subnets & Routing", "Cloud & Infrastructure", "01-aws-core-iam-vpc-and-networking", 1),
        ("caching", "Redis Streams & Caching Policies", "Backend Engineering", "07-real-time-queues-and-caching-websockets-sse-redis", 1),
        ("observability", "OpenTelemetry Distributed Tracing", "Reliability", "08-observability-and-distributed-tracing-opentelemetry-grafana", 1),
        ("security", "Auth: OAuth2, JWT & RBAC", "Reliability", "03-auth-oauth2-jwt-oidc-and-rbac", 1),
    ]:
        session.add(
            ConceptNextLesson(
                concept_id=con_map[concept_slug],
                lesson_title=title,
                module_name=module_name,
                lesson_slug=lesson_slug,
                order_index=order,
            )
        )
    await session.flush()

    print("Knowledge Atlas seeding completed successfully.")


def _domain(
    slug: str,
    name: str,
    code: str,
    description: str,
    icon: str,
    color_hex: str,
    order_index: int,
    now: datetime,
) -> KnowledgeDomain:
    return KnowledgeDomain(
        slug=slug,
        name=name,
        code=code,
        description=description,
        icon=icon,
        color_hex=color_hex,
        order_index=order_index,
        created_at=now,
        updated_at=now,
    )


def _concept(
    slug: str,
    title: str,
    sub_label: str,
    summary: str,
    description: str,
    difficulty: str,
    icon: str,
    estimated_hours: int,
    order_index: int,
    now: datetime,
) -> KnowledgeConcept:
    return KnowledgeConcept(
        slug=slug,
        title=title,
        sub_label=sub_label,
        summary=summary,
        description=description,
        difficulty=difficulty,
        icon=icon,
        estimated_hours=estimated_hours,
        order_index=order_index,
        created_at=now,
        updated_at=now,
    )
