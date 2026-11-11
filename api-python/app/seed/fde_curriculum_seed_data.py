"""Ported from api/Data/FdeCurriculumSeedData.cs.

Seeder LOGIC is hand-ported here; the supplemental-module/lesson DATA and the authored
bodies are extracted from the C# file by tools/extract_seed_data.py into
app/seed/data/fde_curriculum.json. Run the converter first:

    python api-python/tools/extract_seed_data.py
"""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.course import Course
from ..models.course_domain_link import CourseDomainLink
from ..models.course_module import CourseModule
from ..models.knowledge_domain import KnowledgeDomain
from ..models.lesson import Lesson
from ..models.study_task import StudyTask
from ..models.study_vertical import StudyVertical
from ..services.reconciliation.normalization_helper import generate_slug as _slugify

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fde_curriculum.json")


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _load_data() -> dict:
    if not os.path.isfile(DATA_PATH):
        raise RuntimeError(
            "fde_curriculum.json is missing. Run the converter first: "
            "python api-python/tools/extract_seed_data.py"
        )
    with open(DATA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


async def seed(session: AsyncSession) -> None:
    data = _load_data()
    authored: dict[str, str] = data["authored_content"]
    module_guides: dict[str, dict] = data["module_guides"]

    # Derive the curriculum from the seeded FDE vertical. In production the vertical never
    # has tasks: the "FDE" vertical is a hand-written checklist, and it only has tasks in
    # the old seeded database. Use whichever FDE-like vertical actually has tasks.
    all_verticals = (await session.execute(select(StudyVertical))).scalars().all()
    tasks_by_vertical: dict[int, list[StudyTask]] = {}
    for task in (await session.execute(select(StudyTask))).scalars().all():
        tasks_by_vertical.setdefault(task.vertical_id, []).append(task)
    fde_vertical = next(
        (
            v
            for v in all_verticals
            if "FDE" in v.name.upper() and tasks_by_vertical.get(v.id)
        ),
        None,
    )
    if fde_vertical is None:
        fde_vertical = next(
            (v for v in all_verticals if "FDE" in v.name.upper()), None
        )
    if fde_vertical is None:
        print("[WARN] No FDE-like vertical found ('FDE' in name, case-insensitive); skipping FDE curriculum seed.")
        return

    existing_course = (
        await session.execute(select(Course).where(Course.slug == "fde-curriculum"))
    ).scalar_one_or_none()
    if existing_course is None:
        now = _utcnow()
        course = Course(
            slug="fde-curriculum",
            title=fde_vertical.name,
            description=fde_vertical.description,
            order_index=1,
            path_type="Course",
            is_published=True,
            vertical_id=fde_vertical.id,
            created_at=now,
            updated_at=now,
        )
        session.add(course)
        await session.flush()
    else:
        course = existing_course

    tasks = sorted(tasks_by_vertical.get(fde_vertical.id, []), key=lambda t: t.id)
    legacy_modules = sorted({t.module for t in tasks})

    # 1. Create or refresh modules from the legacy vertical's module structure
    module_by_legacy: dict[str, CourseModule] = {}
    for index, legacy_module in enumerate(legacy_modules):
        guide = module_guides.get(legacy_module)
        if guide is None:
            print(f"[WARN] No module guide for legacy module '{legacy_module}'. Skipping.")
            continue
        module_slug = guide["slug"]
        db_module = (
            await session.execute(
                select(CourseModule).where(
                    CourseModule.course_id == course.id, CourseModule.slug == module_slug
                )
            )
        ).scalar_one_or_none()
        if db_module is None:
            db_module = CourseModule(
                course_id=course.id,
                slug=module_slug,
                title=guide["title"],
                description=guide["description"],
                badge=guide["badge"],
                order_index=index + 1,
                created_at=_utcnow(),
                updated_at=_utcnow(),
            )
            session.add(db_module)
            await session.flush()
        module_by_legacy[legacy_module] = db_module

    # 2. Create lessons from tasks, or refresh authored bodies for matching lessons
    lecture_number = 0
    lessons_created = 0
    lessons_updated = 0
    for legacy_module in legacy_modules:
        if legacy_module not in module_by_legacy:
            continue
        db_module = module_by_legacy[legacy_module]
        module_tasks = sorted(
            [t for t in tasks if t.module == legacy_module], key=lambda t: t.id
        )
        existing_lessons: list[Lesson] = list(
            (
                await session.execute(
                    select(Lesson).where(Lesson.module_id == db_module.id)
                )
            )
            .scalars()
            .all()
        )

        for task in module_tasks:
            lecture_number += 1
            lesson_slug = (
                task.title.lower()
                .strip()
                .replace(" ", "-")
                .replace(":", "")
                .replace(",", "")
                .replace("(", "")
                .replace(")", "")
                .replace("&", "and")
                .replace("/", "-")
            )
            lesson_slug = re.sub(r"-+", "-", lesson_slug).strip("-")
            lesson = next(
                (candidate for candidate in existing_lessons if candidate.slug == lesson_slug),
                None,
            )
            # C# TextInfo.ToTitleCase(task.Title.ToLower()): lowercase first, then
            # uppercase every letter following a non-letter (including after apostrophes).
            lesson_title = re.sub(
                r"(^|[^a-zA-Z])([a-z])",
                lambda m: m.group(1) + m.group(2).upper(),
                task.title.lower(),
            )
            guide = module_guides[legacy_module]
            if lesson is None:
                lesson = Lesson(
                    module_id=db_module.id,
                    slug=lesson_slug,
                    title=lesson_title,
                    description=_build_lesson_description(task.title, guide),
                    lecture_number=lecture_number,
                    class_date="",
                    content_body=_resolve_lesson_content(
                        task.title, guide, authored, lesson_slug
                    ),
                    horstmann_ref=guide["reference_url"],
                    estimated_minutes=_estimate_minutes(task.title),
                    is_completed=task.is_completed,
                    order_index=task.id,
                    difficulty=_resolve_difficulty(task.title, guide["badge"]),
                    content_status="Published",
                    created_at=_utcnow(),
                    updated_at=_utcnow(),
                )
                session.add(lesson)
                existing_lessons.append(lesson)
                lessons_created += 1
            else:
                authored_body = authored.get(lesson_slug)
                if authored_body and _needs_authored_body(lesson.content_body):
                    lesson.content_body = authored_body
                    lesson.content_status = "Draft"
                    lesson.updated_at = _utcnow()
                    lessons_updated += 1

    await _ensure_supplemental_modules(session, course, data, authored)
    await _ensure_domain_links(session, course)
    await session.flush()

    print(
        f"[INFO] FDE curriculum seeded: course '{course.slug}' with {len(module_by_legacy)} modules. "
        f"Created {lessons_created} lessons, refreshed {lessons_updated} authored bodies."
    )


def _needs_authored_body(content: str | None) -> bool:
    if not content or not content.strip():
        return True
    return not (
        "## Practical Backend Scenario" in content
        and "## Practice Loop" in content
        and "## Evidence of Understanding" in content
    )


async def _ensure_supplemental_modules(
    session: AsyncSession, course: Course, data: dict, authored: dict[str, str]
) -> None:
    for module_def in data["supplemental_modules"]:
        db_module = (
            await session.execute(
                select(CourseModule).where(
                    CourseModule.course_id == course.id,
                    CourseModule.slug == module_def["slug"],
                )
            )
        ).scalar_one_or_none()
        if db_module is None:
            max_order = (
                await session.execute(
                    select(CourseModule.order_index)
                    .where(CourseModule.course_id == course.id)
                    .order_by(CourseModule.order_index.desc())
                )
            ).scalars().first()
            # C# DefaultIfEmpty(0).Max(): no rows means order 1.
            next_order = (max_order if max_order is not None else 0) + 1
            db_module = CourseModule(
                course_id=course.id,
                slug=module_def["slug"],
                title=module_def["title"],
                description=module_def["description"],
                badge=f"Module {next_order}",
                order_index=next_order,
                created_at=_utcnow(),
                updated_at=_utcnow(),
            )
            session.add(db_module)
            await session.flush()

        existing_slugs = {
            row[0]
            for row in (
                await session.execute(
                    select(Lesson.slug).where(Lesson.module_id == db_module.id)
                )
            ).all()
        }
        for lesson_def in module_def["lessons"]:
            lesson_slug = _slugify(lesson_def["title"])
            if not lesson_slug or lesson_slug in existing_slugs:
                continue
            now = _utcnow()
            session.add(
                Lesson(
                    module_id=db_module.id,
                    slug=lesson_slug,
                    title=lesson_def["title"],
                    description=_resolve_supplemental_description(
                        lesson_def, module_def
                    ),
                    lecture_number=len(existing_slugs) + 1,
                    content_body=authored.get(
                        lesson_slug,
                        _build_supplemental_lesson_content(lesson_def, module_def),
                    ),
                    horstmann_ref=module_def["reference_url"],
                    estimated_minutes=lesson_def.get("estimated_minutes", 75),
                    is_completed=False,
                    order_index=len(existing_slugs) + 1,
                    difficulty=_resolve_supplemental_difficulty(lesson_def),
                    content_status="Published",
                    created_at=now,
                    updated_at=now,
                )
            )
            existing_slugs.add(lesson_slug)
        await session.flush()


async def _ensure_domain_links(session: AsyncSession, course: Course) -> None:
    desired_slugs = ["foundations", "backend", "enterprise", "agent-systems", "reliability"]
    domains = (
        await session.execute(
            select(KnowledgeDomain).where(KnowledgeDomain.slug.in_(desired_slugs))
        )
    ).scalars().all()
    if not domains:
        print("[WARN] No knowledge domains found; skipping FDE domain links.")
        return
    existing = {
        row[0]
        for row in (
            await session.execute(
                select(CourseDomainLink.domain_id).where(
                    CourseDomainLink.course_id == course.id
                )
            )
        ).all()
    }
    order_index = 0
    for domain in domains:
        if domain.id in existing:
            continue
        session.add(
            CourseDomainLink(
                course_id=course.id,
                domain_id=domain.id,
                is_primary=order_index == 0,
                order_index=order_index,
                created_at=_utcnow(),
            )
        )
        order_index += 1
    await session.flush()


def _resolve_lesson_content(
    title: str, guide: dict, authored: dict[str, str], lesson_slug: str
) -> str:
    body = authored.get(lesson_slug)
    if body:
        return body
    return _build_lesson_content(title, guide)


def _build_lesson_description(title: str, guide: dict) -> str:
    return _resolve_topic_brief(title, guide)[0]


def _build_lesson_content(title: str, guide: dict) -> str:
    focus, scenario, practice = _resolve_topic_brief(title, guide)
    nl = "\r\n"
    return nl.join(
        [
            f"# {title}",
            "",
            focus,
            "",
            "## Core concepts",
            "",
            _resolve_core_concepts(title),
            "",
            "## Why it matters in an FDE engagement",
            "",
            guide["delivery_context"],
            "",
            "## Worked scenario",
            "",
            scenario,
            "",
            "## Practice loop",
            "",
            f"1. {practice}",
            "2. Write down the assumptions, inputs, owners, and failure conditions before optimising the solution.",
            "3. Demonstrate the result to a teammate or stakeholder with one success case and one deliberately uncomfortable edge case.",
            "",
            "## Evidence of understanding",
            "",
            f"- {_resolve_evidence(title)}",
            "- You can explain the trade-off in plain language as well as technical language.",
            "- You have a small artefact: a diagram, test, query, deployment note, decision record, or working slice.",
            "- You can name the next signal you would inspect if the customer outcome degraded.",
            "",
            "## Continue learning",
            "",
            f"- Primary reference: {guide['reference_url']}",
            "- Treat this chapter as a working draft. Improve it with your own implementation notes, measurements, and customer-specific constraints.",
        ]
    )


def _contains(value: str, phrase: str) -> bool:
    return phrase.lower() in value.lower()


_CORE_CONCEPTS: list[tuple[tuple[str, ...], str]] = [
    (("The FDE Role",), "- Customer-embedded ownership: clarify the outcome, constraints, and handoff boundary.\n- The FDE loop: discover, prototype, instrument, validate, and enable the customer team.\n- Delivery judgment: optimise for a useful, operable slice before broad platform completeness."),
    (("Problem Discovery",), "- User pain versus requested feature.\n- Observable success measures and acceptance criteria.\n- Assumptions, constraints, risks, and the smallest test that can reduce uncertainty."),
    (("Python Toolchain",), "- Isolated interpreters and reproducible dependency locking.\n- Formatting, linting, static typing, and the boundary between local convenience and CI truth.\n- A repeatable command surface that another engineer can run without knowing the author's machine."),
    (("GenAI", "LLM Landscape"), "- Model capabilities, context limits, latency, cost, and data-handling boundaries.\n- Predictive text versus retrieval, tools, workflows, and agents.\n- A customer outcome is the selection criterion, not novelty of the model."),
    (("LLM Built-in",), "- Structured generation, tool use, embeddings, vision, and model-provided capabilities.\n- Capability limits and fallback behaviour.\n- Separating a useful built-in primitive from a production-ready workflow."),
    (("Prompting", "Prompt Engineering"), "- Task framing, context, examples, constraints, output schemas, and refusal behaviour.\n- Prompt versions and representative evaluation cases.\n- The prompt is one component of a controlled application boundary."),
    (("RAG",), "- Source ingestion, chunking, metadata, embeddings, retrieval, grounding, citations, and no-answer behaviour.\n- Retrieval quality separated from answer quality.\n- Customer data access enforced before context reaches a model."),
    (("n8n",), "- Triggers, state transitions, credentials, branching, retries, approvals, and idempotency.\n- Workflow automation as an explicit integration surface.\n- Human control for consequential customer actions."),
    (("What Is an AI Agent", "Building Agents", "OpenClaw"), "- An agent combines a model with state, tools, policies, and a termination condition.\n- Observe, decide, act, verify, and recover as distinct steps.\n- Autonomy must be bounded by permissions, budgets, and human escalation."),
    (("Debugging AI",), "- Retrieval, prompt, model, tool, policy, and rendering layers.\n- Trace evidence and a reproducible failure case.\n- Targeted experiments that distinguish a bad input from a bad decision."),
    (("Iterators", "Closures"), "- Lazy evaluation and state carried across iterations.\n- Function scope, captured variables, decorators, and resource lifetime.\n- The operational difference between streaming work and materialising an entire dataset."),
    (("OOP, Concurrency",), "- Composition and ownership of mutable state.\n- Cooperative async execution, cancellation, back-pressure, and blocking work.\n- Explicit lifecycle boundaries for customer requests and background tasks."),
    (("Pydantic",), "- Boundary validation versus internal domain invariants.\n- Structured logs with correlation and customer-safe fields.\n- Profiling as measurement of a real bottleneck, not premature optimisation."),
    (("Git Internals",), "- Objects, refs, commits, branches, and the graph that makes changes recoverable.\n- Small reviewable changes and automated checks.\n- AI-assisted coding with human ownership of context, secrets, and final diffs."),
    (("Testing:",), "- Example-based tests for contracts and property-based tests for invariants.\n- Unit, integration, and end-to-end boundaries.\n- CI as a feedback system that protects delivery speed rather than a ceremonial gate."),
    (("SOLID", "Hexagonal"), "- Business rules separated from transport, persistence, and vendor adapters.\n- Dependency inversion and ports-and-adapters boundaries.\n- Design for replacement, testing, and incremental customer-specific change."),
    (("Linux, Shell",), "- Processes, files, pipes, exit codes, signals, and environment variables.\n- Safe composition of small commands and explicit failure handling.\n- Diagnostics that can be copied into a ticket or runbook."),
    (("HTTP", "FastAPI"), "- Resources, methods, status codes, idempotency, pagination, and error contracts.\n- Dependency injection and validation at the API boundary.\n- Authentication and authorization as separate decisions."),
    (("OAuth2", "JWT", "OIDC", "RBAC"), "- Authentication, token claims, scopes, sessions, and identity-provider trust.\n- Authorization as a server-side policy decision.\n- Tenant, role, and audit context carried through every privileged action."),
    (("Order Management",), "- Explicit order state transitions and invariants.\n- Idempotency keys, optimistic concurrency, and audit history.\n- API behaviour that keeps retries from creating duplicate business effects."),
    (("Payments",), "- Payment intent versus payment confirmation.\n- Webhook verification, idempotency, retries, and reconciliation.\n- Background work that can be observed without blocking the customer request."),
    (("Demo Frontend",), "- A thin vertical slice across API, state, UI, and error handling.\n- Loading, empty, success, and failure states.\n- A demo narrative tied to a measurable user task, not a collection of disconnected screens."),
    (("Real-Time", "Queues", "Caching"), "- Push versus pull delivery, acknowledgement, ordering, and retry semantics.\n- Queue ownership, dead-letter handling, and duplicate events.\n- Cache key, freshness, invalidation, and the user-visible meaning of stale data."),
    (("Observability", "Tracing", "Logging", "Profiling"), "- Signals: logs for detail, metrics for trends, traces for causality.\n- Correlation identifiers and context propagation.\n- Service-level indicators connected to a customer journey."),
    (("Postgres Advanced",), "- JSONB indexing and containment queries.\n- Full-text search versus vector similarity search.\n- Query shape, metadata filters, and retrieval quality for customer evidence."),
    (("Postgres Internals",), "- Query plans, selectivity, indexes, locks, and MVCC snapshots.\n- EXPLAIN ANALYZE as an evidence-driven tuning loop.\n- The difference between a fast local query and a safe production query under contention."),
    (("NoSQL",), "- Access-pattern-first modelling, partitioning, consistency, and document boundaries.\n- Vector index recall, filtering, and freshness.\n- Choosing a data store by workload and recovery contract."),
    (("Dimensional Modeling",), "- Facts, dimensions, grain, keys, and slowly changing business meaning.\n- Transformations, lineage, tests, and incremental models.\n- Separating operational truth from reporting-friendly projections."),
    (("Airflow",), "- DAG tasks, dependencies, retries, backfills, schedules, and data-quality gates.\n- Idempotent transformations and late-arriving data.\n- Ownership and alerting for a pipeline that a customer can trust."),
    (("Kafka",), "- Topics, partitions, consumer groups, offsets, ordering, and retention.\n- At-least-once delivery and idempotent consumers.\n- Schema evolution and replay as operational capabilities."),
    (("TypeScript",), "- Structural typing, unions, narrowing, generics, and runtime validation.\n- Types as communication between frontend and API teams.\n- The limit of compile-time safety when data comes from a customer or network."),
    (("React Essentials",), "- Component boundaries, props, state, effects, and controlled inputs.\n- Async state and optimistic versus confirmed UI.\n- Accessible interaction states for a user who is waiting on an AI workflow."),
    (("Next.js",), "- Server and client boundaries, routing, data loading, and caching.\n- Environment and secret boundaries.\n- Rendering choices based on freshness, interactivity, and customer data sensitivity."),
    (("Vercel AI SDK",), "- Token streaming, partial state, cancellation, and reconnect behavior.\n- Structured messages and tool results that the UI can render safely.\n- The distinction between a stream being open and an answer being trustworthy."),
    (("AI Product UX", "Frontend Essentials"), "- User intent, confidence, source evidence, review, and recovery.\n- Progressive disclosure for complex AI behavior.\n- Accessible, keyboard-friendly, and honest feedback during partial failure."),
    (("AWS Core",), "- IAM principals, policies, roles, and least privilege.\n- VPC subnets, routes, security groups, and private versus public reachability.\n- Cloud operations as identity plus network plus observability."),
    (("Compute, Storage",), "- Compute lifecycle, object durability, relational transactions, and queue delivery.\n- Managed service boundaries and shared responsibility.\n- Mapping workload characteristics to scaling, recovery, and cost behaviour."),
    (("AWS Security",), "- Key ownership, envelope encryption, secret rotation, and audit trails.\n- Credential exposure paths and workload identity.\n- Evidence that a sensitive customer action was allowed or denied for the right reason."),
    (("Docker",), "- Image layers, reproducible builds, non-root execution, and runtime configuration.\n- Health checks, signal handling, resource limits, and graceful shutdown.\n- The difference between a container image and a production deployment."),
    (("Kubernetes Architecture",), "- Control plane reconciliation, desired state, pods, deployments, and services.\n- Readiness versus liveness and rollout history.\n- Scheduling and resource requests as customer-impacting decisions."),
    (("EKS", "Helm"), "- Cluster ownership, namespaces, charts, values, ingress, and workload identity.\n- Rollout, rollback, and version compatibility.\n- A deployment handover that names what the customer team operates."),
    (("Kubernetes Networking",), "- Service discovery, ingress, network policies, and pod-to-pod reachability.\n- Secret and identity boundaries for workloads.\n- GPU scheduling and capacity as a product latency constraint."),
    (("CI/CD", "GitOps"), "- Build, test, artifact promotion, deployment, verification, and rollback.\n- Declarative desired state and environment-specific configuration.\n- Approval and audit boundaries for customer production changes."),
    (("Terraform",), "- Resources, state, modules, plans, drift, and safe change sequencing.\n- Inputs and outputs as an infrastructure contract.\n- Reviewable infrastructure changes with recovery for partial apply."),
    (("Serverless",), "- Event triggers, execution limits, retries, idempotency, and orchestration state.\n- Synchronous API response versus asynchronous completion.\n- Cost and cold-start effects on a customer workflow."),
    (("SRE",), "- Service-level objectives, error budgets, toil, and incident ownership.\n- Reliability as a measurable customer promise.\n- Recovery, runbooks, and escalation paths."),
    (("Customer Discovery", "Scoping", "Stakeholder", "Demo Storytelling"), "- Outcome, user, workflow, constraint, measure, and decision owner.\n- Options, risks, assumptions, dependencies, and non-goals.\n- Communication as a mechanism for reducing technical ambiguity."),
    (("LLM Fundamentals",), "- Tokens, context windows, sampling, embeddings, tool calls, and model limits.\n- Capability, latency, quality, privacy, and cost trade-offs.\n- Evaluation before model selection or prompt tuning."),
    (("Prompt Engineering",), "- Role and task framing, grounded context, examples, output schemas, and refusal rules.\n- Prompt versioning and regression cases.\n- Prompt changes as product changes that require evaluation."),
    (("RAG Architecture",), "- Ingestion, parsing, chunking, metadata, embeddings, retrieval, reranking, and generation.\n- Citation and source-boundary requirements.\n- Retrieval quality separated from answer quality."),
    (("RAG over Customer",), "- Tenant-aware document access, hybrid search, filters, freshness, and citations.\n- Source authority and conflicting documents.\n- Retrieval failures that should produce a transparent no-answer."),
    (("RAG Evaluation",), "- Dataset design, faithfulness, context relevance, answer relevance, and human review.\n- Slice-based evaluation by customer workflow and risk.\n- Iteration driven by a failure taxonomy rather than a single score."),
    (("LLM Safety",), "- Prompt injection, data leakage, unsafe tool use, output validation, and human review.\n- Threat modelling and defence in depth.\n- Safety controls that are observable and testable."),
    (("Cost, Latency",), "- Token budgets, batching, caching, routing, timeouts, and fallbacks.\n- Quality thresholds for model substitution.\n- Cost and latency measured per customer task, not only per API call."),
    (("Tool Calling", "Structured Output"), "- JSON schema, validation, tool permissions, retries, and idempotency.\n- Planning versus execution boundaries.\n- Dry-run and approval modes for consequential actions."),
    (("Agentic Patterns",), "- State machines, planning loops, bounded context, memory, and termination.\n- Tool authority and recovery from partial completion.\n- Deterministic workflow steps around probabilistic model decisions."),
    (("Agent Debugging",), "- Trace spans for model, retrieval, tool, policy, and UI layers.\n- Failure taxonomy, reproducible evaluations, and counterexamples.\n- Debugging the first incorrect decision rather than the final symptom."),
    (("MCP",), "- Discoverable tools, resources, prompts, schemas, and transport boundaries.\n- Capability negotiation and least-authority integration.\n- Auditability when an agent accesses customer systems."),
    (("Multi-Agent",), "- Delegation, shared state, coordination, arbitration, and termination.\n- Human approval for high-impact steps.\n- Preventing duplicated work and conflicting agent actions."),
    (("Enterprise Systems", "API Integration"), "- System ownership, source of truth, contracts, identity, rate limits, and change management.\n- Connector boundaries and anti-corruption layers.\n- Integration topology drawn from actual business workflows."),
    (("Integration Failure", "Entity Resolution"), "- Timeouts, retries, dead letters, duplicates, stale records, and reconciliation.\n- Matching confidence and human review for ambiguous entities.\n- Failure evidence that lets two system owners collaborate."),
    (("CRM-to-AI",), "- CRM read authority, retrieval grounding, ticket-write permissions, and approval.\n- Entity resolution and idempotent follow-up actions.\n- End-to-end trace from customer record to generated recommendation to human decision."),
    (("Product Thinking",), "- User journey, domain model, permission boundary, feedback loop, and handover.\n- Thin-slice architecture that can grow without hiding risk.\n- Product decisions expressed as measurable behaviour."),
    (("Multi-Tenant",), "- Tenant identity propagation, row-level isolation, background-job ownership, and noisy-neighbor controls.\n- Secure defaults at every query and worker boundary.\n- Testing that proves one tenant cannot observe another tenant's work."),
    (("Document Processing",), "- Upload validation, parsing, extraction, confidence, provenance, and human review.\n- Asynchronous workflow state and repeatable reprocessing.\n- Separating extracted data from approved business truth."),
    (("Developer Experience",), "- Contract-first API documentation, examples, error semantics, authentication, and changelogs.\n- A first-success path for the next engineer.\n- Documentation tested as part of delivery."),
    (("Enterprise Security",), "- Data classification, PII minimisation, access review, retention, audit, and incident response.\n- Security controls mapped to customer obligations.\n- Evidence for compliance conversations without claiming certification."),
    (("Secrets, Encryption",), "- Secret lifecycle, key hierarchy, encryption in transit and at rest, and deployment trust zones.\n- Rotation without downtime.\n- Topology decisions that make blast radius explicit."),
    (("Load Testing",), "- Workload model, concurrency, saturation, latency percentiles, throughput, and bottleneck.\n- Capacity assumptions and headroom.\n- Load tests that resemble a customer journey rather than an isolated endpoint."),
    (("Incident Response",), "- Detection, triage, mitigation, communication, recovery, and learning.\n- Customer-facing facts separated from internal hypotheses.\n- RCA focused on contributing conditions and prevention, not blame."),
    (("Enterprise Readiness",), "- Functional acceptance, security, observability, support, runbooks, backups, and rollback.\n- Named owners and evidence for each go-live criterion.\n- Handover as a product deliverable."),
    (("Distributed Systems",), "- Failure, partitions, consistency, availability, latency, and coordination.\n- CAP, PACELC, Raft, and Saga as decision tools rather than slogans.\n- Recovery and compensation paths for an incomplete workflow."),
    (("System Design: RAG",), "- Ingestion scale, index freshness, tenant isolation, retrieval latency, evaluation, and cost.\n- Query path versus ingestion path.\n- Degraded behaviour when sources are stale or unavailable."),
    (("System Design: Agentic",), "- Agent runtime, tool gateway, state, policy, evaluation, tracing, and human escalation.\n- Bounded autonomy and replayable decisions.\n- Capacity and failure isolation across model and enterprise dependencies."),
    (("System Design: Multi-Tenant",), "- Tenant isolation, workload fairness, data lifecycle, authorization, queues, and observability.\n- Control plane versus data plane.\n- Trade-offs between shared infrastructure and dedicated isolation."),
    (("System Design: Enterprise Integration",), "- Connector registry, schema translation, identity, rate limits, retries, reconciliation, and audit.\n- Ownership across system boundaries.\n- A topology that supports adding integrations without multiplying failure modes."),
    (("Interview Readiness",), "- Clarify requirements, state assumptions, design the critical path, identify bottlenecks, and validate.\n- Trade-off vocabulary grounded in user and operational outcomes.\n- Clear communication under time pressure."),
    (("Capstone",), "- Discovery, architecture, vertical delivery, integration, security, observability, evaluation, and handover.\n- Milestones that create evidence before the final demo.\n- Scope control when requirements change."),
    (("Mock Engagement", "Graduation Review"), "- End-to-end FDE behaviour: clarify, build, diagnose, communicate, and transfer ownership.\n- Portfolio evidence and decision records.\n- Honest treatment of limitations, unresolved risks, and next steps."),
]


def _resolve_core_concepts(title: str) -> str:
    for phrases, concepts in _CORE_CONCEPTS:
        if any(_contains(title, phrase) for phrase in phrases):
            return concepts
    return (
        f"- Identify the purpose, inputs, outputs, invariants, and failure modes of {title}.\n"
        "- Connect the technical mechanism to a customer workflow and an observable outcome.\n"
        "- Record the assumptions that must be validated before production use."
    )


def _resolve_evidence(title: str) -> str:
    if any(_contains(title, p) for p in ("Assessment", "Capstone", "Build:", "Mock Engagement", "Graduation Review")):
        return "You can present a working slice, its acceptance evidence, known limitations, operating notes, and the next decision a customer should make."
    if any(_contains(title, p) for p in ("Discovery", "Scoping", "Stakeholder", "Demo")):
        return "You can turn a customer conversation into a one-page brief with a measurable outcome, explicit non-goals, risks, owners, and a credible next step."
    if any(_contains(title, p) for p in ("System Design", "Distributed Systems")):
        return "You can defend the architecture against one scale assumption and one failure scenario, including what you would measure after launch."
    if any(_contains(title, p) for p in ("Security", "Secrets", "Auth", "RBAC")):
        return "You can demonstrate an allowed action, a denied action, the audit evidence for both, and the recovery path if a credential or policy is wrong."
    if any(_contains(title, p) for p in ("Observability", "Tracing", "Logging", "Incident", "SRE")):
        return "You can use the captured signals to locate a deliberately introduced failure and explain the customer impact without guessing."
    return "You can complete the practice task, explain one deliberate edge case, and show the artefact or measurement that proves the capability works."


_TOPIC_BRIEFS: list[tuple[tuple[str, ...], tuple[str, str, str]]] = [
    (("The FDE Role",), (
        "Understand the Forward Deployed Engineer as the bridge between a customer's ambiguous workflow and a dependable technical outcome.",
        "A customer describes a painful process but cannot yet name the right product or architecture. The FDE earns trust by observing the workflow, narrowing the first experiment, and staying accountable through validation and handover.",
        "Write a one-page engagement brief with the user, current workflow, desired outcome, constraints, success measure, first slice, owner, and explicit non-goals.")),
    (("Problem Discovery",), (
        "Turn an observed customer problem into a testable solution hypothesis without prematurely committing to a framework, model, or feature list.",
        "An operations team requests an AI assistant because analysts spend hours searching. Interview two users, map the actual search-and-decision workflow, and separate the expensive step from the merely visible step.",
        "Create a problem statement, assumption log, opportunity-solution tree, and smallest validation experiment; include one plausible solution that you deliberately reject and why.")),
    (("Python Toolchain",), (
        "Make Python delivery reproducible across an FDE laptop, CI, staging, and the customer's environment.",
        "A prototype works locally but a handoff fails because Python versions, dependencies, lint rules, and environment variables differ. The fix is a repeatable toolchain contract, not another manual setup note.",
        "Create a clean environment with a locked dependency set, add ruff and mypy checks, run them in CI, and write the exact setup and verification commands for the next engineer.")),
    (("Assessment", "Capstone", "Mock Engagement", "Graduation Review"), (
        "Use this checkpoint to prove you can make engineering decisions under real delivery constraints, not simply recall vocabulary.",
        "A client sponsor asks for a short demonstration by Friday. The team must scope the smallest credible workflow, document its risks, and show evidence that it can be operated after the demo.",
        "Time-box the work, define an acceptance checklist, capture a decision log, and finish with a short retrospective covering what failed, what changed, and what should be handed over.")),
    (("GenAI", "LLM Landscape", "LLM Built-in", "LLM Fundamentals"), (
        "Choose an AI capability by matching task shape, data sensitivity, evaluation needs, latency, and operating cost to the customer outcome.",
        "A team asks for a general-purpose chatbot, but their actual need is a constrained policy lookup with an audit trail. The FDE must make the capability boundary visible before selecting a model.",
        "Write a one-page capability brief: user action, allowed evidence, unacceptable failure, expected response time, and how quality will be evaluated.")),
    (("RAG",), (
        "Design retrieval as an evidence pipeline: define the knowledge boundary, retrieve relevant sources, and make answer quality measurable before expanding the system.",
        "A support team wants answers grounded only in approved product policy. Compare a keyword-only baseline with hybrid retrieval, preserve citations to source chunks, and record the cases where either approach fails.",
        "Create a 20-question evaluation set from real support scenarios, record retrieval context and answer quality separately, then improve one failure mode at a time.")),
    (("Prompt",), (
        "Treat prompts as versioned interface contracts with clear inputs, structured outputs, evaluation cases, and explicit safety boundaries.",
        "A customer asks for an incident-summary assistant. The assistant must distinguish facts from assumptions, refuse to invent missing evidence, and return a schema the UI can render safely.",
        "Write three representative prompts, define a JSON response shape, create adversarial inputs, and compare output quality after each small change.")),
    (("n8n",), (
        "Use workflow automation to make state transitions, approvals, credentials, and retries visible rather than hiding delivery logic in a single opaque flow.",
        "A customer wants inbound feedback routed to the right team. The workflow must classify the request, tolerate a temporary CRM outage, and require a human approval for high-impact actions.",
        "Draw the trigger, state, tool call, retry, and human-approval boundary; then replay a duplicate event and a downstream timeout.")),
    (("Debugging AI",), (
        "Debug AI-assisted workflows by separating retrieval, prompt, model, tool, and user-interface failures instead of treating every bad answer as a model problem.",
        "A response is wrong even though the source document is correct. Inspect the retrieved chunks, prompt version, tool trace, model output, and rendered answer in that order.",
        "Capture one failed interaction end to end, label the failing layer, and write a targeted experiment that could falsify your first explanation.")),
    (("Agent", "Tool Calling", "MCP"), (
        "Build agentic behavior from explicit state, narrow tool contracts, bounded authority, and traces that let a human reconstruct every decision.",
        "A procurement copilot may search contracts and draft a recommendation, but must request approval before creating a ticket or changing a vendor record.",
        "Model the workflow as observe, decide, act, and verify; add a dry-run mode; then test malformed tool responses, permission failures, and repeated actions.")),
    (("Python", "Iterators", "Closures", "Pydantic", "pytest", "Linux"), (
        "Use Python to make a customer workflow repeatable: make environments explicit, validate boundaries, test behaviour, and leave an operator-friendly trail.",
        "A file-processing script works on one laptop but fails on a customer export. The team needs reproducible dependencies, validated input models, structured logs, and a small regression test suite.",
        "Build the smallest executable example, add one invalid-input test, emit structured context for each run, and document the command a teammate can use to reproduce it.")),
    (("Git Internals", "Hexagonal Architecture", "Software Engineering Best Practices"), (
        "Create a delivery system that makes changes reviewable, reversible, testable, and independent from accidental details such as a specific vendor SDK or local machine setup.",
        "A customer asks for a quick integration. The team must move quickly without letting production credentials, unreviewed code paths, or direct vendor coupling become permanent architecture.",
        "Create a small adapter boundary, write a meaningful commit history, add a test around the business rule, and identify the change that can be rolled back independently.")),
    (("HTTP", "FastAPI", "Order Management", "Payments", "Auth"), (
        "Design APIs around stable resource contracts, safe failure behaviour, and authorization rules that match the customer’s real roles.",
        "An operations lead creates an order while a finance user approves payment. The API must reject invalid state changes, make retries safe, and reveal who performed each privileged action.",
        "Write the request and error shapes first, add an idempotency or concurrency case, and test each role against an action it must not perform.")),
    (("Real-Time", "Queues", "Caching"), (
        "Use asynchronous delivery and caching only after defining message ownership, ordering needs, retry behavior, cache invalidation, and the user experience during lag.",
        "An agent job takes thirty seconds while the UI needs immediate feedback. The system must report progress without pretending that the final answer is ready or losing work after a worker restart.",
        "Design the request acknowledgement, event payload, retry policy, cache key, and invalidation trigger; then test a duplicate event and a stale read.")),
    (("Observability", "Tracing", "Logging", "Profiling"), (
        "Instrument the customer outcome, not merely the process: logs, metrics, and traces should answer what failed, where, for whom, and how often.",
        "A user reports that an approval flow is slow. Trace one request across the API, database, queue, and worker to decide whether the cause is latency, a retry storm, or a stuck dependency.",
        "Define one service-level indicator, add a correlation identifier, capture a trace for the happy path and a failure path, then write the first diagnostic question an operator should ask.")),
    (("Postgres", "NoSQL", "Dimensional", "Airflow", "Kafka", "Data Pipeline"), (
        "Choose storage and data movement based on access patterns, freshness, lineage, and recovery needs—not on the popularity of a database or queue.",
        "A customer needs operational search, historical reporting, and near-real-time notifications from the same order data. The design must make ownership and consistency boundaries visible.",
        "Sketch the producer, storage, consumer, and recovery paths; measure one representative query or job; and define what happens when a record is late, duplicated, or malformed.")),
    (("TypeScript", "React", "Next.js", "Vercel", "Frontend", "UX"), (
        "Make the product surface truthful: model states explicitly, keep asynchronous work visible, and give users a safe way to recover from uncertainty.",
        "A document-review user submits a question to an AI workflow. The UI must show progress, surface retrieved evidence, allow cancellation, and make a partial failure understandable.",
        "Implement loading, empty, success, and failure states for one workflow; test keyboard navigation; and ask a teammate to complete the task using only the visible cues.")),
    (("Compute, Storage",), (
        "Select managed compute, storage, database, and queue services by their operational contract: scaling behaviour, durability, isolation, cost model, and recovery characteristics.",
        "A new document workflow needs burst compute, durable uploads, transactional metadata, and asynchronous notifications. One service choice should not silently assume the properties of another.",
        "Map each workload step to a service, state its durability and retry expectation, then test how the design handles a partial write or delayed notification.")),
    (("AWS", "EC2", "S3", "RDS", "SQS", "Lambda", "VPC", "KMS"), (
        "Use cloud services as a set of explicit trust and failure boundaries: identity, network reachability, data protection, cost, and recovery must be designed together.",
        "A customer wants a private document-processing service. The design needs least-privilege roles, private networking where appropriate, encrypted storage, and audit records for high-value actions.",
        "Draw the request path from user to storage, list the identity at each hop, test one denied action, and record how an operator would investigate an unexpected cost or access event.")),
    (("Docker", "Kubernetes", "Helm", "Terraform", "CI/CD", "GitOps", "Serverless"), (
        "Turn delivery into a repeatable system: build once, make configuration explicit, promote through environments, and make rollback a planned operation.",
        "A release passes locally but fails in staging because a secret, migration, or request limit differs. The team needs a declarative deployment record and a safe rollback path.",
        "Package a minimal service, deploy it with an explicit configuration value, force one controlled failure, and document the exact rollback and verification steps.")),
    (("LLM Safety", "Cost, Latency", "Model Routing"), (
        "Make model behavior safe and economical with explicit data handling, output validation, budget limits, latency targets, and a fallback policy that users can understand.",
        "A customer wants every request sent to the largest available model. The FDE must show when a smaller model, a retrieval-only answer, a queue, or a human escalation is safer and cheaper.",
        "Define a request budget, timeout, safety check, fallback response, and evaluation threshold; then simulate a slow model, an unsafe output, and an exhausted budget.")),
    (("SRE", "Load Testing", "Incident", "Readiness", "Secrets", "Security"), (
        "Operational readiness means knowing the normal state, protecting sensitive data, and rehearsing what happens when the system is stressed or wrong.",
        "A customer-facing workflow has a sudden error-rate spike. The team must protect data, communicate status, mitigate impact, and produce a useful root-cause analysis afterwards.",
        "Define a readiness checklist, run one small failure drill, capture the timeline and owner decisions, and turn the first discovered gap into a concrete backlog item.")),
    (("Customer Discovery", "Scoping", "Stakeholder", "Demo Storytelling"), (
        "Convert a conversation into an engineering decision: identify the user, workflow, success measure, constraints, risks, and the smallest testable next step.",
        "A sponsor asks for an AI assistant because ‘the team wastes time searching’. The FDE must uncover who searches, what evidence is trusted, which cases are high risk, and how improvement will be measured.",
        "Run a 30-minute discovery outline, write a one-page option matrix, and present a recommendation that includes a deliberate non-solution option.")),
    (("Integration", "CRM", "Entity Resolution", "Enterprise Systems"), (
        "Treat an integration as a contract between systems with different owners, data quality, timing, and recovery rules.",
        "A support copilot reads CRM data and creates follow-up tickets. Duplicate identities, stale fields, and a temporary connector outage must not lead to duplicate or unauthorized actions.",
        "Document the source of truth for each field, define an idempotency key, model a retry and dead-letter path, and rehearse a connector outage.")),
    (("Product Thinking", "Document Processing", "Developer Experience"), (
        "Shape the application around an observable user job: make inputs, evidence, permissions, review steps, and handover needs explicit from the first prototype.",
        "A legal operations team receives mixed-format documents and needs a review queue. The product must preserve source evidence, distinguish extraction confidence from approval, and leave a usable audit trail.",
        "Map the end-to-end user journey, create one clear review state, document the API contract, and identify the point at which a human must make the final decision.")),
    (("Distributed Systems", "System Design"), (
        "Use system design to make trade-offs visible: workload, latency, scale, consistency, failure modes, capacity, and operations are all part of one argument.",
        "A multi-tenant AI workflow receives unpredictable traffic and must preserve tenant isolation while giving operators a way to recover failed background jobs.",
        "Start with requirements and constraints, draw the critical path, name the bottleneck, choose one trade-off deliberately, and defend it against a failure scenario.")),
    (("Interview Readiness",), (
        "Communicate an engineering decision with structure: clarify the goal, state constraints, propose a design, explain trade-offs, and show how you would validate it in production.",
        "An interviewer asks for an internal knowledge assistant. A useful answer includes the user workflow, retrieval boundary, data protection, evaluation strategy, rollout, and operational failure plan.",
        "Practice a seven-minute design explanation, ask two clarifying questions first, and end with the metric that would determine whether the proposed system should be expanded.")),
]


def _resolve_topic_brief(title: str, guide: dict) -> tuple[str, str, str]:
    for phrases, brief in _TOPIC_BRIEFS:
        if any(_contains(title, phrase) for phrase in phrases):
            return brief
    return (
        f"Study {title} as a practical engineering capability that can be demonstrated, observed, and safely handed over.",
        f"A delivery team needs to apply {title} in a customer environment where requirements are incomplete and the cost of an unexamined assumption is high.",
        f"Create a small artefact for {title}, test one edge case, and explain the chosen trade-off to a non-specialist stakeholder.",
    )


def _estimate_minutes(title: str) -> int:
    lowered = title.lower()
    if "assessment" in lowered or "challenge" in lowered:
        return 120
    if "deep dive" in lowered or "internals" in lowered:
        return 90
    if "introduction" in lowered or "setup" in lowered:
        return 45
    return 60


def _resolve_difficulty(title: str, badge: str) -> str:
    lowered_title = title.lower()
    lowered_badge = badge.lower()
    if any(
        word in lowered_title or word in lowered_badge
        for word in ("assessment", "capstone", "internals")
    ):
        return "Advanced"
    if "fundamentals" in lowered_title or "introduction" in lowered_title:
        return "Foundational"
    return "Intermediate"


def _resolve_supplemental_description(lesson_def: dict, module_def: dict) -> str:
    return f"{lesson_def['focus']} Part of {module_def['title']}: {module_def['description']}"


def _build_supplemental_lesson_content(lesson_def: dict, module_def: dict) -> str:
    return (
        f"# {lesson_def['title']}\r\n"
        f"\r\n"
        f"**Focus:** {lesson_def['focus']}\r\n"
        f"\r\n"
        f"**Module context:** {module_def['delivery_context']}\r\n"
        f"\r\n"
        f"**Core concepts:** {lesson_def['core_concepts']}\r\n"
        f"\r\n"
        f"**Backend scenario:** {lesson_def['scenario']}\r\n"
        f"\r\n"
        f"**Practice loop:** {lesson_def['practice']}\r\n"
        f"\r\n"
        f"**Evidence of understanding:** {lesson_def['evidence']}"
    )


def _resolve_supplemental_difficulty(lesson_def: dict) -> str:
    title = (lesson_def.get("title") or "").lower()
    focus = (lesson_def.get("focus") or "").lower()
    combined = f"{title} {focus}"
    if any(word in combined for word in ("assessment", "capstone", "internals")):
        return "Advanced"
    if "fundamentals" in combined or "introduction" in combined:
        return "Foundational"
    return "Intermediate"
