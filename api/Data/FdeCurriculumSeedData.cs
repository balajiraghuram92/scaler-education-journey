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

        EnsureDomainLinks(db, course);
        db.SaveChanges();
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

## Why it matters in an FDE engagement

{guide.DeliveryContext}

## Worked scenario

{brief.Scenario}

## Practice loop

1. {brief.Practice}
2. Write down the assumptions, inputs, owners, and failure conditions before optimising the solution.
3. Demonstrate the result to a teammate or stakeholder with one success case and one deliberately uncomfortable edge case.

## Evidence of understanding

- You can explain the trade-off in plain language as well as technical language.
- You have a small artefact: a diagram, test, query, deployment note, decision record, or working slice.
- You can name the next signal you would inspect if the customer outcome degraded.

## Continue learning

- Primary reference: {guide.ReferenceUrl}
- Treat this chapter as a working draft. Improve it with your own implementation notes, measurements, and customer-specific constraints.";
    }

    private static TopicBrief ResolveTopicBrief(string title, ModuleGuide guide)
    {
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
