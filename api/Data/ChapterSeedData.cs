using System;
using System.Linq;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public static class ChapterSeedData
{
    public static void Seed(StudyTrackerContext db)
    {
        // 1. Ensure Concurrency module has 'structured-concurrency'
        var concurrencyModule = db.Modules.Include(m => m.Lessons).FirstOrDefault(m => m.Slug == "concurrency-multithreading");
        if (concurrencyModule == null)
        {
            var javaCourse = db.Courses.FirstOrDefault(c => c.Slug == "java-spring-lld");
            if (javaCourse != null)
            {
                concurrencyModule = new CourseModule
                {
                    CourseId = javaCourse.Id,
                    Title = "Module 2: Concurrency & Multithreading",
                    Slug = "concurrency-multithreading",
                    Description = "OS Threads, Thread Pools, Synchronization, Locks, and Virtual Threads.",
                    Badge = "Module 2",
                    OrderIndex = 2
                };
                db.Modules.Add(concurrencyModule);
                db.SaveChanges();
            }
        }

        if (concurrencyModule != null)
        {
            var structConcLesson = db.Lessons
                .Include(l => l.CodeComparisons)
                .Include(l => l.Diagrams)
                .Include(l => l.Notes)
                .FirstOrDefault(l => l.Slug == "structured-concurrency");

            if (structConcLesson == null)
            {
                structConcLesson = new Lesson
                {
                    ModuleId = concurrencyModule.Id,
                    Slug = "structured-concurrency",
                    Title = "Structured Concurrency",
                    Description = "Structured concurrency treats concurrent work as a hierarchy with explicit ownership.",
                    LectureNumber = 9,
                    ClassDate = "Aug 2026",
                    Difficulty = "Advanced",
                    EstimatedMinutes = 25,
                    HorstmannRef = "Core Java Vol I §12.4, JEP 453 (Java 21/22)",
                    ContentBody = @"## Introduction & Architectural Motivation

Structured concurrency treats concurrent work as a hierarchy with explicit ownership. In traditional concurrent programming (""unstructured concurrency""), tasks split into background threads or promises whose lifecycles outlive the originating function. This leads to leaked resources, silent error swallowing, and untracked thread explosions.

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

With `StructuredTaskScope.ShutdownOnFailure()`, the moment Fraud Risk fails, a cancellation signal propagates to the Inventory and Pricing child tasks immediately. The entire scope unwinds deterministically and rethrows the underlying domain exception.",
                    OrderIndex = 9
                };

                db.Lessons.Add(structConcLesson);
                db.SaveChanges();
            }

            // Seed Code Comparisons for Structured Concurrency
            if (!db.LessonCodeComparisons.Any(c => c.LessonId == structConcLesson.Id))
            {
                db.LessonCodeComparisons.Add(new LessonCodeComparison
                {
                    LessonId = structConcLesson.Id,
                    Title = "Unstructured Concurrency vs Structured Concurrency",
                    Description = "Comparison between unstructured CompletableFuture fan-out and Java 21 StructuredTaskScope",
                    BeforeLabel = "Unstructured Concurrency",
                    BeforeLanguage = "java",
                    BeforeCode = @"// ❌ Unstructured Concurrency (CompletableFuture)
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
}",
                    AfterLabel = "Structured Concurrency",
                    AfterLanguage = "java",
                    AfterCode = @"// ✅ Structured Concurrency (Java 21 StructuredTaskScope)
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
}",
                    Explanation = "StructuredTaskScope guarantees that child tasks are terminated before the try-with-resources block exits. Sibling cancellation happens automatically upon first failure.",
                    OrderIndex = 1
                });
            }

            // Seed SVG Diagram
            if (!db.LessonDiagrams.Any(d => d.LessonId == structConcLesson.Id))
            {
                db.LessonDiagrams.Add(new LessonDiagram
                {
                    LessonId = structConcLesson.Id,
                    Title = "Task Ownership Hierarchy",
                    Caption = "Fine-line ownership hierarchy under Structured Concurrency",
                    DiagramType = "svg-inline",
                    SvgContent = @"<svg viewBox=""0 0 640 240"" width=""100%"" height=""100%"" xmlns=""http://www.w3.org/2000/svg"" style=""background: transparent; font-family: 'Plus Jakarta Sans', sans-serif;"">
  <!-- Parent Scope Box -->
  <rect x=""220"" y=""20"" width=""200"" height=""45"" rx=""8"" fill=""#FFFFFF"" stroke=""#2C5E55"" stroke-width=""2""/>
  <text x=""320"" y=""48"" text-anchor=""middle"" font-size=""13"" font-weight=""bold"" fill=""#2C5E55"">Task Ownership Scope</text>

  <!-- Connectors -->
  <path d=""M 260 65 L 120 120"" stroke=""#2C5E55"" stroke-width=""1.5"" stroke-dasharray=""4 4"" fill=""none""/>
  <path d=""M 320 65 L 320 120"" stroke=""#2C5E55"" stroke-width=""1.5"" fill=""none""/>
  <path d=""M 380 65 L 520 120"" stroke=""#2C5E55"" stroke-width=""1.5"" stroke-dasharray=""4 4"" fill=""none""/>

  <!-- Subtask Nodes -->
  <rect x=""40"" y=""120"" width=""160"" height=""40"" rx=""6"" fill=""#FFFFFF"" stroke=""#2C5E55"" stroke-width=""1.5""/>
  <text x=""120"" y=""145"" text-anchor=""middle"" font-size=""12"" fill=""#1C2421"">Pricing (Subtask A)</text>

  <rect x=""240"" y=""120"" width=""160"" height=""40"" rx=""6"" fill=""#FFFFFF"" stroke=""#2C5E55"" stroke-width=""1.5""/>
  <text x=""320"" y=""145"" text-anchor=""middle"" font-size=""12"" fill=""#1C2421"">Fraud Risk (Subtask B)</text>

  <rect x=""440"" y=""120"" width=""160"" height=""40"" rx=""6"" fill=""#FFFFFF"" stroke=""#2C5E55"" stroke-width=""1.5""/>
  <text x=""520"" y=""145"" text-anchor=""middle"" font-size=""12"" fill=""#1C2421"">Inventory (Subtask C)</text>

  <!-- Lower Hierarchy Barrier -->
  <path d=""M 120 160 L 260 200"" stroke=""#A39E93"" stroke-width=""1.2"" stroke-dasharray=""3 3"" fill=""none""/>
  <path d=""M 320 160 L 320 200"" stroke=""#A39E93"" stroke-width=""1.2"" stroke-dasharray=""3 3"" fill=""none""/>
  <path d=""M 520 160 L 380 200"" stroke=""#A39E93"" stroke-width=""1.2"" stroke-dasharray=""3 3"" fill=""none""/>

  <rect x=""230"" y=""200"" width=""180"" height=""32"" rx=""6"" fill=""#F5F2EA"" stroke=""#A39E93"" stroke-width=""1""/>
  <text x=""320"" y=""221"" text-anchor=""middle"" font-size=""11"" font-style=""italic"" fill=""#4A5568"">scope.join() Barrier</text>
</svg>",
                    OrderIndex = 1
                });
            }

            // Seed Notes
            if (!db.LessonNotes.Any(n => n.LessonId == structConcLesson.Id))
            {
                db.LessonNotes.Add(new LessonNote
                {
                    LessonId = structConcLesson.Id,
                    NoteType = "PersonalNote",
                    Title = "Production Invariant",
                    ContentBody = "Remember to always join or cancel subtasks before exiting. Never catch InterruptedException without restoring the interrupt flag on carrier threads.",
                    OrderIndex = 1
                });
            }
        }

        // 2. Enrich Lesson 03: OOP-2 Access Modifiers & Encapsulation
        var oop2Lesson = db.Lessons
            .Include(l => l.CodeComparisons)
            .Include(l => l.Diagrams)
            .Include(l => l.Notes)
            .FirstOrDefault(l => l.Slug == "03-oop-2-access-modifiers-encapsulation" || l.Title.Contains("OOP-2"));

        if (oop2Lesson != null)
        {
            if (!db.LessonCodeComparisons.Any(c => c.LessonId == oop2Lesson.Id))
            {
                db.LessonCodeComparisons.Add(new LessonCodeComparison
                {
                    LessonId = oop2Lesson.Id,
                    Title = "Mutable JavaBean vs Immutable Domain Model",
                    Description = "Eliminating concurrent state mutation bugs at compile time through immutability and final fields.",
                    BeforeLabel = "Mutable JavaBean (Unsafe)",
                    BeforeLanguage = "java",
                    BeforeCode = @"// ❌ Mutable JavaBean: Thread-Unsafe
public class Fare {
    private double baseFare;
    private double surgeMultiplier;
    private String currency;

    public void setSurgeMultiplier(double surgeMultiplier) {
        this.surgeMultiplier = surgeMultiplier; // Mutates in-place!
    }
    public double getTotalFare() { return baseFare * surgeMultiplier; }
}",
                    AfterLabel = "Immutable Value Object (Safe)",
                    AfterLanguage = "java",
                    AfterCode = @"// ✅ Immutable Value Object: Thread-Safe by Construction
public final class Fare {
    private final double baseFare;
    private final double surgeMultiplier;
    private final String currency;

    public Fare(double baseFare, double surgeMultiplier, String currency) {
        if (baseFare < 0) throw new IllegalArgumentException(""baseFare < 0"");
        if (surgeMultiplier < 1.0) throw new IllegalArgumentException(""surge < 1.0"");
        this.baseFare = baseFare;
        this.surgeMultiplier = surgeMultiplier;
        this.currency = Objects.requireNonNull(currency).trim();
    }

    public Fare withSurge(double newSurge) {
        return new Fare(this.baseFare, newSurge, this.currency); // Pure state evolution
    }
    public double getTotalFare() { return baseFare * surgeMultiplier; }
}",
                    Explanation = "The withSurge method returns a new Fare instance, preserving the original quotation for the in-flight transaction.",
                    OrderIndex = 1
                });
            }

            if (!db.LessonDiagrams.Any(d => d.LessonId == oop2Lesson.Id))
            {
                db.LessonDiagrams.Add(new LessonDiagram
                {
                    LessonId = oop2Lesson.Id,
                    Title = "Heap Reference Transformation",
                    Caption = "Immutable state evolution via fresh heap instance allocation",
                    DiagramType = "svg-inline",
                    SvgContent = @"<svg viewBox=""0 0 600 180"" width=""100%"" height=""100%"" xmlns=""http://www.w3.org/2000/svg"" style=""background: transparent; font-family: 'Plus Jakarta Sans', sans-serif;"">
  <!-- Original Instance -->
  <rect x=""30"" y=""30"" width=""220"" height=""120"" rx=""8"" fill=""#FFFFFF"" stroke=""#2C5E55"" stroke-width=""2""/>
  <text x=""45"" y=""58"" font-size=""13"" font-weight=""bold"" fill=""#2C5E55"">Fare @0x10A (Original)</text>
  <text x=""45"" y=""85"" font-size=""11"" fill=""#4A5568"">baseFare: 150.00</text>
  <text x=""45"" y=""105"" font-size=""11"" fill=""#4A5568"">surgeMultiplier: 1.20</text>
  <text x=""45"" y=""128"" font-size=""12"" font-weight=""bold"" fill=""#2C5E55"">Total: ₹180.00</text>

  <!-- Evolution Arrow -->
  <path d=""M 265 90 L 335 90"" stroke=""#C85A32"" stroke-width=""2"" marker-end=""url(#arrow)"" fill=""none""/>
  <text x=""300"" y=""80"" text-anchor=""middle"" font-size=""11"" font-style=""italic"" fill=""#C85A32"">withSurge(2.0)</text>

  <!-- New Instance -->
  <rect x=""350"" y=""30"" width=""220"" height=""120"" rx=""8"" fill=""#FFFFFF"" stroke=""#C85A32"" stroke-width=""2""/>
  <text x=""365"" y=""58"" font-size=""13"" font-weight=""bold"" fill=""#C85A32"">Fare @0x2BF (New)</text>
  <text x=""365"" y=""85"" font-size=""11"" fill=""#4A5568"">baseFare: 150.00 (Copied)</text>
  <text x=""365"" y=""105"" font-size=""11"" fill=""#4A5568"">surgeMultiplier: 2.00 (Updated)</text>
  <text x=""365"" y=""128"" font-size=""12"" font-weight=""bold"" fill=""#C85A32"">Total: ₹300.00</text>
</svg>",
                    OrderIndex = 1
                });
            }

            if (!db.LessonNotes.Any(n => n.LessonId == oop2Lesson.Id))
            {
                db.LessonNotes.Add(new LessonNote
                {
                    LessonId = oop2Lesson.Id,
                    NoteType = "HorstmannRef",
                    Title = "Core Java References",
                    ContentBody = "Horstmann Core Java Vol I Ch. 4 §4.5, Ch. 5 (all), Ch. 6 §6.1/§6.3; Vol II Ch. 5 §5.2. Always declare fields private final to prevent unintended external mutability.",
                    OrderIndex = 1
                });
            }
        }

        db.SaveChanges();
    }
}
