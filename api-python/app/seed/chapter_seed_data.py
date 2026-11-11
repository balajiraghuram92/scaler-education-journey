"""Ported from api/Data/ChapterSeedData.cs."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.course import Course
from ..models.course_module import CourseModule
from ..models.lesson import Lesson
from ..models.lesson_code_comparison import LessonCodeComparison
from ..models.lesson_diagram import LessonDiagram
from ..models.lesson_note import LessonNote

_STRUCTURED_CONCURRENCY_BODY = '''## Introduction & Architectural Motivation

Structured concurrency treats concurrent work as a hierarchy with explicit ownership. In traditional concurrent programming ("unstructured concurrency"), tasks split into background threads or promises whose lifecycles outlive the originating function. This leads to leaked resources, silent error swallowing, and untracked thread explosions.

Under **Structured Concurrency**, if a task splits into concurrent subtasks, they all return to the same place. The syntactic structure of the code dictates the concurrent lifecycle: child threads are bound to a parent lexical scope that cannot complete until all children terminate or cancel cleanly.

### The Core Invariants of Structured Scopes

1. **Explicit Scope Hierarchy:** Concurrent forks are enclosed within a `try-with-resources` block (or `TaskGroup`), establishing a clear parent-child tree.
2. **Short-Circuit Error Cascading:** If any subtask throws an exception (such as a database timeout or authentication failure), the scope automatically cancels all sibling subtasks instantly without wasting CPU cycles.
3. **No Thread Leaks:** The parent thread blocks at `scope.join()` until all child subtasks have finished or responded to cancellation.

---

## Worked Backend Scenario: Payment & Risk Orchestration

Consider a high-throughput backend checkout flow requiring three concurrent calls:
- **Price Calculation Service** (HTTP, ~15ms)
- **Fraud Risk Evaluation** (gRPC, ~40ms)
- **Inventory Hold Reservation** (PostgreSQL Transaction, ~25ms)

In an unstructured architecture, if Fraud Risk fails with `FraudRiskExceededException`, the inventory reservation and pricing calculations continue executing in the background, holding database connections and mutating stock counts for an aborted order.

With `StructuredTaskScope.ShutdownOnFailure()`, the moment Fraud Risk fails, a cancellation signal propagates to the Inventory and Pricing child tasks immediately. The entire scope unwinds deterministically and rethrows the underlying domain exception.'''

_STRUCTURED_BEFORE_CODE = '''// ❌ Unstructured Concurrency (CompletableFuture)
public Response handleCheckout(UUID orderId, UUID customerId) {
    // Spawns detached threads on ForkJoinPool with no lexical parent
    CompletableFuture<Pricing> pricingFuture = CompletableFuture.supplyAsync(
        () -> pricingClient.calculate(orderId)
    );
    CompletableFuture<FraudScore> fraudFuture = CompletableFuture.supplyAsync(
        () -> fraudService.evaluate(customerId)
    );
    CompletableFuture<InventoryHold> inventoryFuture = CompletableFuture.supplyAsync(
        () -> inventoryClient.reserve(orderId)
    );

    // If fraudFuture fails, pricing and inventory continue running in background!
    return CompletableFuture.allOf(pricingFuture, fraudFuture, inventoryFuture)
        .thenApply(v -> new Response(pricingFuture.join(), fraudFuture.join(), inventoryFuture.join()))
        .join();
}'''

_STRUCTURED_AFTER_CODE = '''// ✅ Structured Concurrency (Java 21 StructuredTaskScope)
public Response handleCheckout(UUID orderId, UUID customerId) throws Exception {
    // Bounded lexical scope with automatic short-circuit cancellation
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Supplier<Pricing> pricing = scope.fork(() -> pricingClient.calculate(orderId));
        Supplier<FraudScore> fraud = scope.fork(() -> fraudService.evaluate(customerId));
        Supplier<InventoryHold> inventory = scope.fork(() -> inventoryClient.reserve(orderId));

        scope.join(); // Blocks until all finish OR one fails
        scope.throwIfFailed(OrderProcessingException::new); // Cascades instant cancel to siblings

        // Both children guaranteed complete and successful
        return new Response(pricing.get(), fraud.get(), inventory.get());
    } // AutoCloseable: ensures all virtual threads drained
}'''

_STRUCTURED_SVG = '''<svg viewBox="0 0 640 240" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: transparent; font-family: 'Plus Jakarta Sans', sans-serif;">
  <!-- Parent Scope Box -->
  <rect x="220" y="20" width="200" height="45" rx="8" fill="#FFFFFF" stroke="#2C5E55" stroke-width="2"/>
  <text x="320" y="48" text-anchor="middle" font-size="13" font-weight="bold" fill="#2C5E55">Task Ownership Scope</text>

  <!-- Connectors -->
  <path d="M 260 65 L 120 120" stroke="#2C5E55" stroke-width="1.5" stroke-dasharray="4 4" fill="none"/>
  <path d="M 320 65 L 320 120" stroke="#2C5E55" stroke-width="1.5" fill="none"/>
  <path d="M 380 65 L 520 120" stroke="#2C5E55" stroke-width="1.5" stroke-dasharray="4 4" fill="none"/>

  <!-- Subtask Nodes -->
  <rect x="40" y="120" width="160" height="40" rx="6" fill="#FFFFFF" stroke="#2C5E55" stroke-width="1.5"/>
  <text x="120" y="145" text-anchor="middle" font-size="12" fill="#1C2421">Pricing (Subtask A)</text>

  <rect x="240" y="120" width="160" height="40" rx="6" fill="#FFFFFF" stroke="#2C5E55" stroke-width="1.5"/>
  <text x="320" y="145" text-anchor="middle" font-size="12" fill="#1C2421">Fraud Risk (Subtask B)</text>

  <rect x="440" y="120" width="160" height="40" rx="6" fill="#FFFFFF" stroke="#2C5E55" stroke-width="1.5"/>
  <text x="520" y="145" text-anchor="middle" font-size="12" fill="#1C2421">Inventory (Subtask C)</text>

  <!-- Lower Hierarchy Barrier -->
  <path d="M 120 160 L 260 200" stroke="#A39E93" stroke-width="1.2" stroke-dasharray="3 3" fill="none"/>
  <path d="M 320 160 L 320 200" stroke="#A39E93" stroke-width="1.2" stroke-dasharray="3 3" fill="none"/>
  <path d="M 520 160 L 380 200" stroke="#A39E93" stroke-width="1.2" stroke-dasharray="3 3" fill="none"/>

  <rect x="230" y="200" width="180" height="32" rx="6" fill="#F5F2EA" stroke="#A39E93" stroke-width="1"/>
  <text x="320" y="221" text-anchor="middle" font-size="11" font-style="italic" fill="#4A5568">scope.join() Barrier</text>
</svg>'''

_OOP2_BEFORE_CODE = '''// ❌ Mutable JavaBean: Thread-Unsafe
public class Fare {
    private double baseFare;
    private double surgeMultiplier;
    private String currency;

    public void setSurgeMultiplier(double surgeMultiplier) {
        this.surgeMultiplier = surgeMultiplier; // Mutates in-place!
    }
    public double getTotalFare() { return baseFare * surgeMultiplier; }
}'''

_OOP2_AFTER_CODE = '''// ✅ Immutable Value Object: Thread-Safe by Construction
public final class Fare {
    private final double baseFare;
    private final double surgeMultiplier;
    private final String currency;

    public Fare(double baseFare, double surgeMultiplier, String currency) {
        if (baseFare < 0) throw new IllegalArgumentException("baseFare < 0");
        if (surgeMultiplier < 1.0) throw new IllegalArgumentException("surge < 1.0");
        this.baseFare = baseFare;
        this.surgeMultiplier = surgeMultiplier;
        this.currency = Objects.requireNonNull(currency).trim();
    }

    public Fare withSurge(double newSurge) {
        return new Fare(this.baseFare, newSurge, this.currency); // Pure state evolution
    }
    public double getTotalFare() { return baseFare * surgeMultiplier; }
}'''

_OOP2_SVG = '''<svg viewBox="0 0 600 180" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: transparent; font-family: 'Plus Jakarta Sans', sans-serif;">
  <!-- Original Instance -->
  <rect x="30" y="30" width="220" height="120" rx="8" fill="#FFFFFF" stroke="#2C5E55" stroke-width="2"/>
  <text x="45" y="58" font-size="13" font-weight="bold" fill="#2C5E55">Fare @0x10A (Original)</text>
  <text x="45" y="85" font-size="11" fill="#4A5568">baseFare: 150.00</text>
  <text x="45" y="105" font-size="11" fill="#4A5568">surgeMultiplier: 1.20</text>
  <text x="45" y="128" font-size="12" font-weight="bold" fill="#2C5E55">Total: ₹180.00</text>

  <!-- Evolution Arrow -->
  <path d="M 265 90 L 335 90" stroke="#C85A32" stroke-width="2" marker-end="url(#arrow)" fill="none"/>
  <text x="300" y="80" text-anchor="middle" font-size="11" font-style="italic" fill="#C85A32">withSurge(2.0)</text>

  <!-- New Instance -->
  <rect x="350" y="30" width="220" height="120" rx="8" fill="#FFFFFF" stroke="#C85A32" stroke-width="2"/>
  <text x="365" y="58" font-size="13" font-weight="bold" fill="#C85A32">Fare @0x2BF (New)</text>
  <text x="365" y="85" font-size="11" fill="#4A5568">baseFare: 150.00 (Copied)</text>
  <text x="365" y="105" font-size="11" fill="#4A5568">surgeMultiplier: 2.00 (Updated)</text>
  <text x="365" y="128" font-size="12" font-weight="bold" fill="#C85A32">Total: ₹300.00</text>
</svg>'''


# C# verbatim strings span CRLF line endings, so the database stores \r\n.
_STRUCTURED_CONCURRENCY_BODY = _STRUCTURED_CONCURRENCY_BODY.replace("\n", "\r\n")
_STRUCTURED_BEFORE_CODE = _STRUCTURED_BEFORE_CODE.replace("\n", "\r\n")
_STRUCTURED_AFTER_CODE = _STRUCTURED_AFTER_CODE.replace("\n", "\r\n")
_STRUCTURED_SVG = _STRUCTURED_SVG.replace("\n", "\r\n")
_OOP2_BEFORE_CODE = _OOP2_BEFORE_CODE.replace("\n", "\r\n")
_OOP2_AFTER_CODE = _OOP2_AFTER_CODE.replace("\n", "\r\n")
_OOP2_SVG = _OOP2_SVG.replace("\n", "\r\n")


async def seed(session: AsyncSession) -> None:
    now = datetime.now(UTC)
    # 1. Ensure Concurrency module has 'structured-concurrency'
    concurrency_module = (
        await session.execute(
            select(CourseModule)
            .options(selectinload(CourseModule.lessons))
            .where(CourseModule.slug == "concurrency-multithreading")
        )
    ).scalar_one_or_none()
    if concurrency_module is None:
        java_course = (
            await session.execute(select(Course).where(Course.slug == "java-spring-lld"))
        ).scalar_one_or_none()
        if java_course is not None:
            concurrency_module = CourseModule(
                course_id=java_course.id,
                title="Module 2: Concurrency & Multithreading",
                slug="concurrency-multithreading",
                description="OS Threads, Thread Pools, Synchronization, Locks, and Virtual Threads.",
                badge="Module 2",
                order_index=2,
                created_at=now,
                updated_at=now,
            )
            session.add(concurrency_module)
            await session.flush()

    if concurrency_module is not None:
        struct_lesson = (
            await session.execute(
                select(Lesson)
                .options(
                    selectinload(Lesson.code_comparisons),
                    selectinload(Lesson.diagrams),
                    selectinload(Lesson.notes),
                )
                .where(Lesson.slug == "structured-concurrency")
            )
        ).scalar_one_or_none()
        if struct_lesson is None:
            struct_lesson = Lesson(
                module_id=concurrency_module.id,
                slug="structured-concurrency",
                title="Structured Concurrency",
                description="Structured concurrency treats concurrent work as a hierarchy with explicit ownership.",
                lecture_number=9,
                class_date="Aug 2026",
                difficulty="Advanced",
                estimated_minutes=25,
                horstmann_ref="Core Java Vol I §12.4, JEP 453 (Java 21/22)",
                content_body=_STRUCTURED_CONCURRENCY_BODY,
                is_completed=False,
                order_index=9,
                created_at=now,
                updated_at=now,
            )
            session.add(struct_lesson)
            await session.flush()

        # Seed Code Comparisons for Structured Concurrency
        has_comparison = (
            await session.execute(
                select(LessonCodeComparison.id)
                .where(LessonCodeComparison.lesson_id == struct_lesson.id)
                .limit(1)
            )
        ).first()
        if has_comparison is None:
            session.add(
                LessonCodeComparison(
                    lesson_id=struct_lesson.id,
                    title="Unstructured Concurrency vs Structured Concurrency",
                    description="Comparison between unstructured CompletableFuture fan-out and Java 21 StructuredTaskScope",
                    before_label="Unstructured Concurrency",
                    before_language="java",
                    before_code=_STRUCTURED_BEFORE_CODE,
                    after_label="Structured Concurrency",
                    after_language="java",
                    after_code=_STRUCTURED_AFTER_CODE,
                    explanation="StructuredTaskScope guarantees that child tasks are terminated before the try-with-resources block exits. Sibling cancellation happens automatically upon first failure.",
                    order_index=1,
                    created_at=now,
                )
            )

        # Seed SVG Diagram
        has_diagram = (
            await session.execute(
                select(LessonDiagram.id)
                .where(LessonDiagram.lesson_id == struct_lesson.id)
                .limit(1)
            )
        ).first()
        if has_diagram is None:
            session.add(
                LessonDiagram(
                    lesson_id=struct_lesson.id,
                    title="Task Ownership Hierarchy",
                    caption="Fine-line ownership hierarchy under Structured Concurrency",
                    diagram_type="svg-inline",
                    svg_content=_STRUCTURED_SVG,
                    order_index=1,
                    created_at=now,
                )
            )

        # Seed Notes
        has_note = (
            await session.execute(
                select(LessonNote.id)
                .where(LessonNote.lesson_id == struct_lesson.id)
                .limit(1)
            )
        ).first()
        if has_note is None:
            session.add(
                LessonNote(
                    lesson_id=struct_lesson.id,
                    note_type="PersonalNote",
                    title="Production Invariant",
                    content_body="Remember to always join or cancel subtasks before exiting. Never catch InterruptedException without restoring the interrupt flag on carrier threads.",
                    order_index=1,
                    created_at=now,
                    updated_at=now,
                )
            )

    # 2. Enrich Lesson 03: OOP-2 Access Modifiers & Encapsulation
    lessons = (await session.execute(select(Lesson))).scalars().all()
    oop2_lesson = next(
        (
            lesson
            for lesson in lessons
            if lesson.slug == "03-oop-2-access-modifiers-encapsulation"
            or "OOP-2" in (lesson.title or "")
        ),
        None,
    )
    if oop2_lesson is not None:
        has_comparison = (
            await session.execute(
                select(LessonCodeComparison.id)
                .where(LessonCodeComparison.lesson_id == oop2_lesson.id)
                .limit(1)
            )
        ).first()
        if has_comparison is None:
            session.add(
                LessonCodeComparison(
                    lesson_id=oop2_lesson.id,
                    title="Mutable JavaBean vs Immutable Domain Model",
                    description="Eliminating concurrent state mutation bugs at compile time through immutability and final fields.",
                    before_label="Mutable JavaBean (Unsafe)",
                    before_language="java",
                    before_code=_OOP2_BEFORE_CODE,
                    after_label="Immutable Value Object (Safe)",
                    after_language="java",
                    after_code=_OOP2_AFTER_CODE,
                    explanation="The withSurge method returns a new Fare instance, preserving the original quotation for the in-flight transaction.",
                    order_index=1,
                    created_at=now,
                )
            )

        has_diagram = (
            await session.execute(
                select(LessonDiagram.id)
                .where(LessonDiagram.lesson_id == oop2_lesson.id)
                .limit(1)
            )
        ).first()
        if has_diagram is None:
            session.add(
                LessonDiagram(
                    lesson_id=oop2_lesson.id,
                    title="Heap Reference Transformation",
                    caption="Immutable state evolution via fresh heap instance allocation",
                    diagram_type="svg-inline",
                    svg_content=_OOP2_SVG,
                    order_index=1,
                    created_at=now,
                )
            )

        has_note = (
            await session.execute(
                select(LessonNote.id)
                .where(LessonNote.lesson_id == oop2_lesson.id)
                .limit(1)
            )
        ).first()
        if has_note is None:
            session.add(
                LessonNote(
                    lesson_id=oop2_lesson.id,
                    note_type="HorstmannRef",
                    title="Core Java References",
                    content_body="Horstmann Core Java Vol I Ch. 4 §4.5, Ch. 5 (all), Ch. 6 §6.1/§6.3; Vol II Ch. 5 §5.2. Always declare fields private final to prevent unintended external mutability.",
                    order_index=1,
                    created_at=now,
                    updated_at=now,
                )
            )

    await session.flush()
