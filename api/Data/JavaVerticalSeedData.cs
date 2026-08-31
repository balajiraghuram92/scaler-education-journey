using System;
using System.Collections.Generic;
using System.Linq;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public static class JavaVerticalSeedData
{
    private static readonly IReadOnlyDictionary<string, int> StandaloneExpandedCourseOrders =
        new Dictionary<string, int>(StringComparer.Ordinal)
        {
            ["databases-sql"] = 3,
            ["high-level-design"] = 4,
            ["data-engineering"] = 5
        };

    public static void Seed(StudyTrackerContext db)
    {
        // 1. Seed or Update StudyVertical for Java & Spring Architecture
        var javaVertical = db.Verticals.FirstOrDefault(v => v.Name == "Java & Spring Architecture");
        if (javaVertical == null)
        {
            javaVertical = new StudyVertical
            {
                Name = "Java & Spring Architecture",
                Description = "Low-Level Design, Concurrency, Spring Boot & Distributed Enterprise Systems"
            };
            db.Verticals.Add(javaVertical);
            db.SaveChanges();
        }

        // Populate vertical tasks if empty
        if (!db.Tasks.Any(t => t.VerticalId == javaVertical.Id))
        {
            var tasks = GetVerticalTasks(javaVertical.Id);
            db.Tasks.AddRange(tasks);
            db.SaveChanges();
        }

        // 2. Seed Course Hierarchy for Java LLD & Spring Architecture
        var course = db.Courses.FirstOrDefault(c => c.Slug == "java-spring-lld");
        if (course == null)
        {
            course = new Course
            {
                Slug = "java-spring-lld",
                Title = "Java Low-Level Design & Spring Architecture",
                Description = "Mastering Object-Oriented Design, Concurrency, JVM Internals, and Spring Boot Enterprise Architecture.",
                OrderIndex = 1,
                VerticalId = javaVertical.Id
            };
            db.Courses.Add(course);
            db.SaveChanges();

            // Module 1: OOP Foundations
            var mod1 = new CourseModule
            {
                CourseId = course.Id,
                Slug = "oop-foundations",
                Title = "OOP Foundations & Design Principles",
                Description = "Core encapsulation, constructor chaining, class hierarchies, polymorphism, and abstraction.",
                Badge = "Module 1",
                OrderIndex = 1
            };
            db.Modules.Add(mod1);
            db.SaveChanges();

            // Module 2: Concurrency & Multithreading
            var mod2 = new CourseModule
            {
                CourseId = course.Id,
                Slug = "concurrency-multithreading",
                Title = "Concurrency & Multithreading",
                Description = "Thread lifecycles, race conditions, synchronized blocks, locks, semaphores, and executors.",
                Badge = "Module 2",
                OrderIndex = 2
            };
            db.Modules.Add(mod2);
            db.SaveChanges();

            // Module 3: Advanced Java & Functional Programming
            var mod3 = new CourseModule
            {
                CourseId = course.Id,
                Slug = "advanced-java-collections",
                Title = "Advanced Java, Collections & Streams",
                Description = "Generics, type erasure, collections framework internals, lambda expressions, and functional stream pipelines.",
                Badge = "Module 3",
                OrderIndex = 3
            };
            db.Modules.Add(mod3);
            db.SaveChanges();

            // Module 4: Design Principles & Patterns
            var mod4 = new CourseModule
            {
                CourseId = course.Id,
                Slug = "design-principles-patterns",
                Title = "Design Principles & Patterns for Extensible Systems",
                Description = "SOLID principles, creational, structural, and behavioural design patterns, and UML class diagrams.",
                Badge = "Module 4",
                OrderIndex = 4
            };
            db.Modules.Add(mod4);
            db.SaveChanges();

            // Module 5: Applied Design & Machine Coding
            var mod5 = new CourseModule
            {
                CourseId = course.Id,
                Slug = "applied-machine-coding",
                Title = "Applied Design & Machine Coding",
                Description = "End-to-end object-oriented design and implementation of real-world systems: TicTacToe, Parking Lot, BookMyShow, and Splitwise.",
                Badge = "Module 5",
                OrderIndex = 5
            };
            db.Modules.Add(mod5);
            db.SaveChanges();

            // Module 6: Spring & Enterprise Architecture
            var mod6Spring = new CourseModule
            {
                CourseId = course.Id,
                Slug = "spring-enterprise-architecture",
                Title = "Spring Boot & Enterprise Architecture",
                Description = "Dependency injection, Spring Data JPA, RESTful API design, PostgreSQL integration, and distributed architectures.",
                Badge = "Module 6",
                OrderIndex = 6
            };
            db.Modules.Add(mod6Spring);
            db.SaveChanges();

            // Seed Lessons for Module 1
            SeedModule1Lessons(db, mod1.Id);

            // Seed Lessons for Module 2
            SeedModule2Lessons(db, mod2.Id);

            // Seed Lessons for Module 3
            SeedModule3Lessons(db, mod3.Id);

            // Seed Lessons for Module 4
            SeedModule4Lessons(db, mod4.Id);

            // Seed Lessons for Module 5
            SeedModule5Lessons(db, mod5.Id);

            // Seed Lessons for Module 6
            SeedModule6Lessons(db, mod6Spring.Id);

            db.SaveChanges();
        }

        // Idempotent module restructure — safe to run on existing databases
        // Ensures the correct 6-module ordering regardless of when the database was first seeded.
        var existingCourse = db.Courses.FirstOrDefault(c => c.Slug == "java-spring-lld");
        if (existingCourse != null)
        {
            // Ensure Spring module is at OrderIndex 6 (it may be at 4 in older seeds)
            var springModule = db.Modules.FirstOrDefault(m => m.CourseId == existingCourse.Id && m.Slug == "spring-enterprise-architecture");
            if (springModule != null && springModule.OrderIndex != 6)
            {
                springModule.OrderIndex = 6;
                springModule.Badge = "Module 6";
                db.SaveChanges();
            }

            // Ensure Module 4 (design-principles-patterns) exists, is canonical, and has its lessons
            var designModule = db.Modules.FirstOrDefault(m => m.CourseId == existingCourse.Id && m.Slug == "design-principles-patterns");
            if (designModule == null)
            {
                designModule = new CourseModule
                {
                    CourseId = existingCourse.Id,
                    Slug = "design-principles-patterns",
                    Title = "Design Principles & Patterns for Extensible Systems",
                    Description = "SOLID principles, creational, structural, and behavioural design patterns, and UML class diagrams.",
                    Badge = "Module 4",
                    OrderIndex = 4
                };
                db.Modules.Add(designModule);
                db.SaveChanges();
            }
            else if (designModule.Badge != "Module 4" ||
                     designModule.Title != "Design Principles & Patterns for Extensible Systems" ||
                     designModule.Description != "SOLID principles, creational, structural, and behavioural design patterns, and UML class diagrams." ||
                     designModule.OrderIndex != 4)
            {
                designModule.Badge = "Module 4";
                designModule.Title = "Design Principles & Patterns for Extensible Systems";
                designModule.Description = "SOLID principles, creational, structural, and behavioural design patterns, and UML class diagrams.";
                designModule.OrderIndex = 4;
                db.SaveChanges();
            }

            if (!db.Lessons.Any(l => l.ModuleId == designModule.Id && l.Slug == "14-solid-principles"))
            {
                SeedModule4Lessons(db, designModule.Id);
                db.SaveChanges();
            }

            // Ensure Module 5 (applied-machine-coding) exists, is canonical, and has its lessons
            var machineModule = db.Modules.FirstOrDefault(m => m.CourseId == existingCourse.Id && m.Slug == "applied-machine-coding");
            if (machineModule == null)
            {
                machineModule = new CourseModule
                {
                    CourseId = existingCourse.Id,
                    Slug = "applied-machine-coding",
                    Title = "Applied Design & Machine Coding",
                    Description = "End-to-end object-oriented design and implementation of real-world systems: TicTacToe, Parking Lot, BookMyShow, and Splitwise.",
                    Badge = "Module 5",
                    OrderIndex = 5
                };
                db.Modules.Add(machineModule);
                db.SaveChanges();
            }
            else if (machineModule.Badge != "Module 5" ||
                     machineModule.Title != "Applied Design & Machine Coding" ||
                     machineModule.Description != "End-to-end object-oriented design and implementation of real-world systems: TicTacToe, Parking Lot, BookMyShow, and Splitwise." ||
                     machineModule.OrderIndex != 5)
            {
                machineModule.Badge = "Module 5";
                machineModule.Title = "Applied Design & Machine Coding";
                machineModule.Description = "End-to-end object-oriented design and implementation of real-world systems: TicTacToe, Parking Lot, BookMyShow, and Splitwise.";
                machineModule.OrderIndex = 5;
                db.SaveChanges();
            }

            if (!db.Lessons.Any(l => l.ModuleId == machineModule.Id && l.Slug == "18-how-to-approach-design"))
            {
                SeedModule5Lessons(db, machineModule.Id);
                db.SaveChanges();
            }
        }

        // Existing databases may already have the course and its lessons. Backfill only
        // lessons that still contain the original outline or no body at all.
        BackfillLessonContent(db, course.Id);
        EnsureStandaloneExpandedCourses(db, course);
        EnsureExpandedModules(db, course.Id);
        db.SaveChanges();
    }

    private static List<StudyTask> GetVerticalTasks(int verticalId)
    {
        return new List<StudyTask>
        {
            // Prerequisite / Module 1
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "Lesson 01: Intro to LLD for Scalable & AI-Ready Systems", IsCompleted = true },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "Lesson 02: OOP-1 Intro Lab (Core OOP Foundations)", IsCompleted = true },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "Lesson 03: OOP-2 Access Modifiers, Encapsulation & Inheritance", IsCompleted = true },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "OOP-2 Problem 1: Immutable Fare (Warm-up)", IsCompleted = true },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "OOP-2 Problem 2: Driver Onboarding (Easy-Mid)", IsCompleted = true },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "OOP-2 Problem 3: Vehicle Hierarchy (Mid)", IsCompleted = true },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "OOP-2 Problem 4: Trip Copy Semantics (Mid-Hard)", IsCompleted = true },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "OOP-2 Problem 5: The equals/hashCode Contract (Hard)", IsCompleted = true },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "Lesson 04: OOP-3 Polymorphism, Interfaces & Abstract Classes", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "1. OOP & Design Foundations", Title = "Lesson 05: OOP-4 Library Management System (LMS) Lab", IsCompleted = false },

            // Module 2: Concurrency
            new StudyTask { VerticalId = verticalId, Module = "2. Concurrency & Multithreading", Title = "Lesson 06: Concurrency 1: Processes, Threads & PCB Context Switching", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "2. Concurrency & Multithreading", Title = "Lesson 07: Concurrency 2: Executors, Thread Pools & Callable/Future", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "2. Concurrency & Multithreading", Title = "Lesson 08: Concurrency 3: Synchronization, Race Conditions & Locks", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "2. Concurrency & Multithreading", Title = "Lesson 09: Concurrency 4: Semaphores & Bounded Buffer", IsCompleted = false },

            // Module 3: Advanced Java
            new StudyTask { VerticalId = verticalId, Module = "3. Advanced Java & Collections", Title = "Lesson 10: Java Advanced 1: Generics, Wildcards & Type Erasure", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "3. Advanced Java & Collections", Title = "Lesson 11: Java Advanced 2: Collections Lab & Comparator/Comparable", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "3. Advanced Java & Collections", Title = "Lesson 12: Java Advanced 3: Lambdas, Functional Interfaces & Streams", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "3. Advanced Java & Collections", Title = "Lesson 13: Java Advanced 4: Streams in Depth & Exception Architecture", IsCompleted = false },

            // Module 4: Spring & Architecture
            new StudyTask { VerticalId = verticalId, Module = "4. Spring & Enterprise Architecture", Title = "Spring Boot 3 Core: Inversion of Control & Dependency Injection", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "4. Spring & Enterprise Architecture", Title = "Data Layer: Spring Data JPA, Hibernate & PostgreSQL 16", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "4. Spring & Enterprise Architecture", Title = "API Architecture: RESTful Services, Validation & Security", IsCompleted = false },
            new StudyTask { VerticalId = verticalId, Module = "4. Spring & Enterprise Architecture", Title = "Contest Capstone: Java, OOP & Concurrency Machine Coding", IsCompleted = false }
        };
    }

    private static void SeedModule1Lessons(StudyTrackerContext db, int moduleId)
    {
        // Lesson 1
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "01-intro-to-lld",
            Title = "Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems",
            Description = "High-Level Design vs Low-Level Design, vertical vs horizontal scaling, and procedural to object-oriented paradigm shift.",
            LectureNumber = 1,
            ClassDate = "2026-06-19",
            HorstmannRef = "Core Java Vol I Ch. 4 §4.1–§4.3",
            EstimatedMinutes = 60,
            IsCompleted = true,
            OrderIndex = 1,
            ContentBody = GetAuthoredLessonContent("01-intro-to-lld") ?? string.Empty
        });

        // Lesson 2
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "02-oop-1-intro-lab",
            Title = "Lesson 2 — OOP-1: Classes, Objects & Encapsulation",
            Description = "Distinguish a class from an object, predict JVM memory reference model results, use constructors/this keyword, static vs instance fields, and enforce business rules with encapsulation.",
            LectureNumber = 2,
            ClassDate = "2026-06-21",
            HorstmannRef = "Core Java Vol I Ch. 4 §4.4",
            EstimatedMinutes = 60,
            IsCompleted = true,
            OrderIndex = 2,
            ContentBody = GetAuthoredLessonContent("02-oop-1-intro-lab") ?? string.Empty
        });

        // Lesson 3 - THE COMPREHENSIVE OOP-2 LESSON
        var lesson3 = new Lesson
        {
            ModuleId = moduleId,
            Slug = "03-oop-2-access-modifiers-encapsulation",
            Title = "Lesson 3 — OOP-2: Access Modifiers, Encapsulation & Inheritance",
            Description = "Deep dive into access levels, constructor overloading and chaining, final semantics, defensive copying, and the equals/hashCode contract.",
            LectureNumber = 3,
            ClassDate = "2026-06-24",
            HorstmannRef = "Core Java Vol I Ch. 4 §4.5, Ch. 5 (all), Ch. 6 §6.1/§6.3; Vol II Ch. 5 §5.2",
            EstimatedMinutes = 120,
            IsCompleted = true,
            OrderIndex = 3,
            ContentBody = GetAuthoredLessonContent("03-oop-2-access-modifiers-encapsulation") ?? string.Empty
        };
        db.Lessons.Add(lesson3);
        db.SaveChanges();

        // Add the 15 Study Guide Topics for Lesson 3
        SeedLesson3StudyGuide(db, lesson3.Id);

        // Lesson 4
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "04-oop-3-polymorphism-interfaces",
            Title = "Lesson 4 — OOP-3: Polymorphism & Interfaces",
            Description = "Dynamic method dispatch, abstract classes, interface contracts, multiple inheritance of type, and default methods.",
            LectureNumber = 4,
            ClassDate = "2026-06-26",
            HorstmannRef = "Core Java Vol I Ch. 6 §6.1",
            EstimatedMinutes = 90,
            IsCompleted = false,
            OrderIndex = 4,
            ContentBody = @"# Lesson 4 — OOP-3: Polymorphism & Interfaces
## Key Topics
- Dynamic Dispatch and Virtual Method Tables (VMT)
- Abstract classes vs Interfaces: when to choose which
- Interface segregation and contract-driven architecture
- Default and static interface methods in modern Java"
        });

        // Lesson 5
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "05-oop-4-lms-lab",
            Title = "Lesson 5 — OOP-4: Library Management System Lab",
            Description = "Capstone OOP machine coding lab integrating all four pillars into an extensible domain model.",
            LectureNumber = 5,
            ClassDate = "2026-06-29",
            HorstmannRef = "Core Java Vol I Ch. 4–6 Comprehensive",
            EstimatedMinutes = 120,
            IsCompleted = false,
            OrderIndex = 5,
            ContentBody = @"# Lesson 5 — OOP-4: Library Management System Lab
## Lab Objectives
- Design Book, Member, Librarian, Loan, and Fine entities.
- Implement inventory catalog searching and policy-based lending limits.
- Ensure immutable transaction logs and defensive borrowing records."
        });
    }

    private static void SeedLesson3StudyGuide(StudyTrackerContext db, int lessonId)
    {
        var topics = new List<(string Title, string Content, int Order)>
        {
            ("1. Access Modifiers", @"Four levels, from most closed to most open:
| Modifier | Same class | Same package | Subclass (other package) | Anywhere |
|---|:---:|:---:|:---:|:---:|
| `private` | ✅ | ❌ | ❌ | ❌ |
| *(none)* — package-private | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

**Default to `private`**: Every public field is an irrevocable API promise. `private` fields + deliberate public methods keep internals safe.", 1),

            ("2. Constructor Overloading", @"Several constructors distinguished by parameter types. Avoid duplicate field initialization in multiple constructor bodies — it causes silent field initialization bugs during refactoring.", 2),

            ("3. Constructor Chaining with this(...)", @"Use `this(...)` to delegate from overloaded constructors to a single canonical constructor.
- `this(...)` must be the **very first statement** in the constructor.
- `this(...)` goes sideways (same class); `super(...)` goes upward (parent class).", 3),

            ("4. final on a Variable", @"Assigned once, never reassigned.
**`final` freezes the reference, not the object's contents.** `final List<String> list` prevents reassigning `list`, but `list.add(...)` is still permitted.", 4),

            ("5. final on a Method", @"Prevents subclasses from overriding the method. Critical for identity accessors (e.g. `getDriverId()`) to preserve the integrity of `equals()` and `hashCode()`.", 5),

            ("6. final on a Class", @"Seals the class so no other class can extend it. `java.lang.String` is `final` to ensure immutability cannot be undermined by a mutable subclass.", 6),

            ("7. The Immutability Pattern", @"Three required ingredients:
1. Every field is `final`
2. No setter methods
3. The class itself is `final`
To update an immutable object, return a new instance (e.g., `withSurge(...)`, `String.toUpperCase()`).", 7),

            ("8. Inheritance with extends", @"Declares an **IS-A** relationship. Parent methods run child overrides dynamically at runtime (**dynamic dispatch**).", 8),

            ("9. super(...) and Construction Order", @"Parent constructor always executes before the child constructor body. If omitted, Java inserts an implicit `super()` call.", 9),

            ("10. protected in its Natural Habitat", @"Allows members to be accessible to subclasses and the same package, but closed to external callers. Prefer protected *methods* over protected *fields*.", 10),

            ("11. Shallow Copy Pitfall", @"Copying object references copies memory addresses rather than the underlying state. Mutating a shallow-copied object mutates the original object.", 11),

            ("12. Deep Copy & Copy Constructors", @"Rule: **Mutable field -> Deep copy (new object); Immutable field -> Share the reference.**
Apply defensive copying both on input into constructors and on output via getters.", 12),

            ("13. The Object Class & @Override", @"All classes inherit from `java.lang.Object`. Always annotate method overrides with `@Override` so the compiler catches mismatched parameter types.", 13),

            ("14. == vs equals()", @"`==` compares memory addresses for objects. `equals()` defines semantic equality.
The 5 rules of `equals()`: Reflexive, Symmetric, Transitive, Consistent, Null-safe.
Use `getClass() != obj.getClass()` to ensure strict symmetry across subclasses.", 14),

            ("15. The hashCode Contract & HashMap", @"If `a.equals(b)` is true, then `a.hashCode() == b.hashCode()` MUST be true.
`hashCode()` selects the HashMap bucket; `equals()` disambiguates keys inside the bucket. Never include mutable fields in `hashCode()`.", 15)
        };

        foreach (var topic in topics)
        {
            db.LessonResources.Add(new LessonResource
            {
                LessonId = lessonId,
                ResourceType = "StudyGuideTopic",
                Title = topic.Title,
                ContentBody = topic.Content,
                OrderIndex = topic.Order
            });
        }
    }

    private static void SeedModule2Lessons(StudyTrackerContext db, int moduleId)
    {
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "06-concurrency-1-threads",
            Title = "Lesson 6 — Concurrency 1: Processes, Threads & Context Switching",
            Description = "Process Control Block (PCB), user vs kernel threads, thread states, and the Runnable SOP.",
            LectureNumber = 6,
            ClassDate = "2026-07-01",
            HorstmannRef = "Core Java Vol I Ch. 12 §12.1",
            EstimatedMinutes = 60,
            OrderIndex = 1,
            ContentBody = "# Lesson 6 — Concurrency 1: Processes & Threads\nUnderstanding process memory layouts, thread stacks, context switching overhead, and thread creation via `Thread` and `Runnable`."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "07-concurrency-2-executors",
            Title = "Lesson 7 — Concurrency 2: Executors, Thread Pools & Callable/Future",
            Description = "ThreadPoolExecutor architectures, fixed/cached pools, work stealing, and asynchronous computation with Callable and Future.",
            LectureNumber = 7,
            ClassDate = "2026-07-03",
            HorstmannRef = "Core Java Vol I Ch. 12 §12.4",
            EstimatedMinutes = 75,
            OrderIndex = 2,
            ContentBody = "# Lesson 7 — Concurrency 2: Executors\nManaging thread lifecycle with ExecutorService, submitting tasks, parallel merge sort, and handling Future results."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "08-concurrency-3-synchronization",
            Title = "Lesson 8 — Concurrency 3: Synchronization, Race Conditions & Locks",
            Description = "Critical sections, race conditions, synchronized keyword, intrinsic locks, ReentrantLock, and Producer-Consumer pattern.",
            LectureNumber = 8,
            ClassDate = "2026-07-06",
            HorstmannRef = "Core Java Vol I Ch. 12 §12.2–§12.3",
            EstimatedMinutes = 90,
            OrderIndex = 3,
            ContentBody = "# Lesson 8 — Concurrency 3: Synchronization\nMutual exclusion, memory visibility, deadlocks, and coordinating threads with wait/notify and explicit condition locks."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "09-concurrency-4-semaphores",
            Title = "Lesson 9 — Concurrency 4: Semaphores & Bounded Buffer",
            Description = "Counting vs binary semaphores, permit management, rate limiting, and building bounded blocking queues.",
            LectureNumber = 9,
            ClassDate = "2026-07-08",
            HorstmannRef = "Core Java Vol I Ch. 12 §12.5",
            EstimatedMinutes = 75,
            OrderIndex = 4,
            ContentBody = "# Lesson 9 — Concurrency 4: Semaphores\nPermit acquisition, non-owner release, mutex vs semaphore comparisons, and bounded buffer implementations."
        });
    }

    private static void SeedModule3Lessons(StudyTrackerContext db, int moduleId)
    {
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "10-java-adv-1-generics",
            Title = "Lesson 10 — Java Adv 1: Generics & Type Erasure",
            Description = "Generic classes, methods, wildcards (? extends T, ? super T), and JVM byte-code type erasure.",
            LectureNumber = 10,
            ClassDate = "2026-07-10",
            HorstmannRef = "Core Java Vol I Ch. 8",
            EstimatedMinutes = 60,
            OrderIndex = 1,
            ContentBody = "# Lesson 10 — Generics\nType safety at compile time, PECS (Producer Extends, Consumer Super) rule, bridge methods, and type erasure mechanics."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "11-java-adv-2-collections-lab",
            Title = "Lesson 11 — Java Adv 2: Collections Lab & Sorting",
            Description = "Deep dive into ArrayList, LinkedList, HashMap, TreeMap, PriorityQueue, Comparable and Comparator.",
            LectureNumber = 11,
            ClassDate = "2026-07-13",
            HorstmannRef = "Core Java Vol I Ch. 9",
            EstimatedMinutes = 90,
            OrderIndex = 2,
            ContentBody = "# Lesson 11 — Collections Lab\nBenchmarking data structures, custom ordering with Comparators, collision resolution, and red-black tree operations."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "12-java-adv-3-lambdas-streams",
            Title = "Lesson 12 — Java Adv 3: Lambdas & Functional Streams",
            Description = "Functional interfaces (@FunctionalInterface), lambda syntax, method references, Stream intermediate and terminal operations, Optional.",
            LectureNumber = 12,
            ClassDate = "2026-07-15",
            HorstmannRef = "Core Java Vol I Ch. 6 §6.2; Vol II Ch. 1",
            EstimatedMinutes = 90,
            OrderIndex = 3,
            ContentBody = "# Lesson 12 — Lambdas & Streams\nDeclarative data processing, lazy stream evaluation, filter/map/reduce/collect pipelines, and avoiding null pointer exceptions with Optional."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "13-java-adv-4-streams-exceptions",
            Title = "Lesson 13 — Java Adv 4: Streams in Depth & Exceptions",
            Description = "Collectors (groupingBy, partitioningBy), flatMap, checked vs unchecked exception hierarchy, and try-with-resources.",
            LectureNumber = 13,
            ClassDate = "2026-07-17",
            HorstmannRef = "Core Java Vol I Ch. 7; Vol II Ch. 1",
            EstimatedMinutes = 75,
            OrderIndex = 4,
            ContentBody = "# Lesson 13 — Streams & Exceptions\nAdvanced aggregation with Collectors, exception propagation, custom business exception hierarchies, and AutoCloseable resource cleanup."
        });
    }

    private static void SeedModule4Lessons(StudyTrackerContext db, int moduleId)
    {
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "14-solid-principles",
            Title = "Lesson 14 — SOLID Principles for Extensible Systems",
            Description = "Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion — applied to Java backend design with AI service integration examples.",
            LectureNumber = 14,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 90,
            IsCompleted = false,
            OrderIndex = 1,
            ContentBody = "# Lesson 14 — SOLID Principles\n## Key Topics\n- Single Responsibility Principle\n- Open-Closed Principle\n- Liskov Substitution Principle\n- Interface Segregation Principle\n- Dependency Inversion Principle"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "15-creational-patterns",
            Title = "Lesson 15 — Creational Design Patterns",
            Description = "Singleton, Builder, Prototype, Registry, and Factory — controlling object creation and dependency setup in production Java systems.",
            LectureNumber = 15,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 90,
            IsCompleted = false,
            OrderIndex = 2,
            ContentBody = "# Lesson 15 — Creational Patterns\n## Key Topics\n- Singleton (thread-safe variants)\n- Builder pattern\n- Prototype and Registry\n- Factory pattern for service abstraction"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "16-structural-patterns",
            Title = "Lesson 16 — Structural Design Patterns",
            Description = "Adapter, Facade, Decorator, and Flyweight — composing objects and classes into larger structures without breaking client contracts.",
            LectureNumber = 16,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 90,
            IsCompleted = false,
            OrderIndex = 3,
            ContentBody = "# Lesson 16 — Structural Patterns\n## Key Topics\n- Adapter pattern\n- Facade pattern\n- Decorator pattern\n- Flyweight pattern"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "17-behavioural-patterns-uml",
            Title = "Lesson 17 — Behavioural Patterns & UML Diagrams",
            Description = "Observer, Strategy, Command, Chain of Responsibility — managing algorithms and object communication — plus reading and writing UML class diagrams.",
            LectureNumber = 17,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 90,
            IsCompleted = false,
            OrderIndex = 4,
            ContentBody = "# Lesson 17 — Behavioural Patterns & UML\n## Key Topics\n- Observer pattern\n- Strategy pattern\n- Command pattern\n- Chain of Responsibility\n- UML class diagram notation"
        });
    }

    private static void SeedModule5Lessons(StudyTrackerContext db, int moduleId)
    {
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "18-how-to-approach-design",
            Title = "Lesson 18 — How to Approach Design Problems",
            Description = "A repeatable framework for machine coding interviews and real-world system design: requirements gathering, entity identification, relationship mapping, and iterative refinement.",
            LectureNumber = 18,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 60,
            IsCompleted = false,
            OrderIndex = 1,
            ContentBody = "# Lesson 18 — How to Approach Design Problems\n## Key Topics\n- Clarifying requirements before coding\n- Identifying entities and their relationships\n- Choosing between inheritance and composition\n- Iterative design: sketch first, code second"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "19-machine-coding-tictactoe",
            Title = "Lesson 19 — Machine Coding: TicTacToe",
            Description = "Design and implement a clean, extensible TicTacToe engine: board abstraction, player management, win-condition strategy, and handling NxN generalization.",
            LectureNumber = 19,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 150,
            IsCompleted = false,
            OrderIndex = 2,
            ContentBody = "# Lesson 19 — Machine Coding: TicTacToe\n## Key Topics\n- Board and cell abstraction\n- Player and symbol management\n- Win-condition checking strategy\n- NxN board generalization\n- Game loop and turn management"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "20-machine-coding-parking-lot",
            Title = "Lesson 20 — Machine Coding: Parking Lot",
            Description = "Design and implement a multi-floor parking lot system: spot types, vehicle hierarchy, entry/exit ticketing, fee calculation strategy, and concurrent slot management.",
            LectureNumber = 20,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 150,
            IsCompleted = false,
            OrderIndex = 3,
            ContentBody = "# Lesson 20 — Machine Coding: Parking Lot\n## Key Topics\n- Parking spot and floor abstraction\n- Vehicle type hierarchy\n- Ticket and fee calculation strategy\n- Entry/exit gate management\n- Availability tracking"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "21-machine-coding-bookmyshow",
            Title = "Lesson 21 — Machine Coding: BookMyShow",
            Description = "Design and implement a seat booking system: event and venue modelling, seat locking under concurrency, booking confirmation flow, and payment state management.",
            LectureNumber = 21,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 180,
            IsCompleted = false,
            OrderIndex = 4,
            ContentBody = "# Lesson 21 — Machine Coding: BookMyShow\n## Key Topics\n- Event, show, and venue entities\n- Seat locking and concurrency\n- Booking confirmation and cancellation\n- Payment state machine"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "22-machine-coding-splitwise",
            Title = "Lesson 22 — Machine Coding: Splitwise",
            Description = "Design and implement an expense-splitting system: expense categories, split strategies (equal, exact, percentage), debt simplification, and balance sheet computation.",
            LectureNumber = 22,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 150,
            IsCompleted = false,
            OrderIndex = 5,
            ContentBody = "# Lesson 22 — Machine Coding: Splitwise\n## Key Topics\n- User and group management\n- Expense and split strategy\n- Equal, exact, and percentage splits\n- Balance computation and debt simplification"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "23-machine-coding-contest",
            Title = "Lesson 23 — Machine Coding Contest",
            Description = "Timed machine coding assessment applying all design patterns and OOP principles to a new, unseen problem under interview conditions.",
            LectureNumber = 23,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 120,
            IsCompleted = false,
            OrderIndex = 6,
            ContentBody = "# Lesson 23 — Machine Coding Contest\n## Key Topics\n- Timed system design under pressure\n- Applying SOLID and design patterns to new problems\n- Code review and self-assessment"
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "24-machine-coding-hotel-management",
            Title = "Lesson 24 — Machine Coding: Hotel Management System",
            Description = "Design and implement a layered hotel booking system across four incremental stages: adding rooms, browsing availability, booking rooms, and generating invoices — Controller/DTO/Repository/Service architecture.",
            LectureNumber = 24,
            ClassDate = "TBD",
            HorstmannRef = "TBD",
            EstimatedMinutes = 180,
            IsCompleted = false,
            OrderIndex = 7,
            ContentBody = GetAuthoredLessonContent("24-machine-coding-hotel-management") ?? string.Empty
        });
    }

    private static void SeedModule6Lessons(StudyTrackerContext db, int moduleId)
    {
        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "14-spring-boot-core",
            Title = "Lesson 14 — Spring Boot Core: IoC & Dependency Injection",
            Description = "ApplicationContext, Bean lifecycles, @Component, @Service, @Repository, @Autowired, and configuration management.",
            LectureNumber = 14,
            ClassDate = "2026-07-20",
            HorstmannRef = "Spring Framework Core Documentation",
            EstimatedMinutes = 75,
            OrderIndex = 1,
            ContentBody = "# Lesson 14 — Spring Boot Core\nInversion of Control container, component scanning, constructor injection best practices, and profile-based configuration."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "15-spring-data-jpa",
            Title = "Lesson 15 — Spring Data JPA & PostgreSQL Integration",
            Description = "Entity mappings, repositories, JPQL queries, transaction management (@Transactional), and PostgreSQL connection pooling.",
            LectureNumber = 15,
            ClassDate = "2026-07-22",
            HorstmannRef = "Spring Data JPA Documentation",
            EstimatedMinutes = 90,
            OrderIndex = 2,
            ContentBody = "# Lesson 15 — Spring Data JPA\nHibernate ORM mapping, N+1 query prevention with JOIN FETCH, indexing strategies, and database migrations."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "16-spring-rest-api",
            Title = "Lesson 16 — RESTful APIs, Validation & Security",
            Description = "Controller endpoints (@RestController, @RequestMapping), request DTO validation, global exception handlers (@ControllerAdvice), and API Key / JWT authentication.",
            LectureNumber = 16,
            ClassDate = "2026-07-25",
            HorstmannRef = "Spring Web MVC Documentation",
            EstimatedMinutes = 90,
            OrderIndex = 3,
            ContentBody = "# Lesson 16 — RESTful APIs\nHTTP verbs, clean URL hierarchy, DTO transformations, Bean Validation (@Valid, @NotNull), and custom security filters."
        });

        db.Lessons.Add(new Lesson
        {
            ModuleId = moduleId,
            Slug = "17-machine-coding-capstone",
            Title = "Lesson 17 — Distributed Systems & Machine Coding Capstone",
            Description = "Timed 2-hour machine coding assessment simulating real-world concurrent ride-hailing / booking platform architecture.",
            LectureNumber = 17,
            ClassDate = "2026-07-28",
            HorstmannRef = "Scaler Machine Coding & LLD Assessment",
            EstimatedMinutes = 120,
            OrderIndex = 4,
            ContentBody = "# Lesson 17 — Machine Coding Capstone\nEnd-to-end implementation of multi-threaded service with clean architecture, high throughput, and robust edge case handling."
        });
    }

    private static void EnsureStandaloneExpandedCourses(StudyTrackerContext db, Course javaCourse)
    {
        var definitions = GetExpandedModules()
            .Where(definition => StandaloneExpandedCourseOrders.ContainsKey(definition.Slug))
            .ToDictionary(definition => definition.Slug, StringComparer.Ordinal);

        foreach (var standaloneCourse in StandaloneExpandedCourseOrders)
        {
            EnsureStandaloneExpandedCourse(
                db,
                javaCourse,
                definitions[standaloneCourse.Key],
                standaloneCourse.Value);
        }
    }

    private static void EnsureStandaloneExpandedCourse(
        StudyTrackerContext db,
        Course javaCourse,
        ExpandedModuleSeed definition,
        int orderIndex)
    {
        var standaloneCourse = db.Courses.FirstOrDefault(c => c.Slug == definition.Slug);

        if (standaloneCourse == null)
        {
            standaloneCourse = new Course
            {
                Slug = definition.Slug,
                Title = definition.Title,
                Description = definition.Description,
                OrderIndex = orderIndex,
                PathType = "Course",
                IsPublished = true,
                VerticalId = null
            };
            db.Courses.Add(standaloneCourse);
            db.SaveChanges();
        }
        else
        {
            standaloneCourse.Title = definition.Title;
            standaloneCourse.Description = definition.Description;
            standaloneCourse.PathType = "Course";
            standaloneCourse.IsPublished = true;
            standaloneCourse.OrderIndex = orderIndex;
        }

        var javaDatabaseModule = db.Modules
            .SingleOrDefault(module => module.CourseId == javaCourse.Id && module.Slug == definition.Slug);
        var standaloneDatabaseModule = db.Modules
            .SingleOrDefault(module => module.CourseId == standaloneCourse.Id && module.Slug == definition.Slug);

        if (javaDatabaseModule != null && standaloneDatabaseModule != null && javaDatabaseModule.Id != standaloneDatabaseModule.Id)
        {
            throw new InvalidOperationException(
                $"Expanded curriculum '{definition.Slug}' exists under both Java LLD and its standalone course. Resolve the duplicate modules before seeding.");
        }

        if (standaloneDatabaseModule == null && javaDatabaseModule != null)
        {
            // Re-home the existing module instead of recreating it. This keeps
            // lesson ids, authored bodies, linked resources, and completion state.
            javaDatabaseModule.CourseId = standaloneCourse.Id;
            javaDatabaseModule.UpdatedAt = DateTime.UtcNow;
            standaloneDatabaseModule = javaDatabaseModule;
        }

        db.SaveChanges();
        EnsureExpandedModules(db, standaloneCourse.Id, new[] { definition });
    }

    private static void EnsureExpandedModules(StudyTrackerContext db, int courseId)
    {
        var javaDefinitions = GetExpandedModules()
            .Where(definition => !StandaloneExpandedCourseOrders.ContainsKey(definition.Slug))
            .ToList();

        EnsureExpandedModules(db, courseId, javaDefinitions);
    }

    private static void EnsureExpandedModules(
        StudyTrackerContext db,
        int courseId,
        IReadOnlyList<ExpandedModuleSeed> definitions)
    {
        var nextLectureNumber = (from lesson in db.Lessons
                                 join module in db.Modules on lesson.ModuleId equals module.Id
                                 where module.CourseId == courseId
                                 select (int?)lesson.LectureNumber).Max() ?? 0;

        foreach (var definition in definitions)
        {
            var module = db.Modules.FirstOrDefault(m => m.CourseId == courseId && m.Slug == definition.Slug);
            if (module == null)
            {
                module = new CourseModule
                {
                    CourseId = courseId,
                    Slug = definition.Slug,
                    Title = definition.Title,
                    Description = definition.Description,
                    Badge = definition.Badge,
                    OrderIndex = definition.OrderIndex
                };
                db.Modules.Add(module);
                db.SaveChanges();
            }

            for (var lessonIndex = 0; lessonIndex < definition.Lessons.Count; lessonIndex++)
            {
                var lessonDefinition = definition.Lessons[lessonIndex];
                var lesson = db.Lessons.FirstOrDefault(l => l.ModuleId == module.Id && l.Slug == lessonDefinition.Slug);
                if (lesson == null)
                {
                    lesson = new Lesson
                    {
                        ModuleId = module.Id,
                        Slug = lessonDefinition.Slug,
                        Title = lessonDefinition.Title,
                        Description = lessonDefinition.Description,
                        LectureNumber = ++nextLectureNumber,
                        ClassDate = string.Empty,
                        ContentBody = lessonDefinition.ContentBody,
                        HorstmannRef = lessonDefinition.Reference,
                        EstimatedMinutes = lessonDefinition.EstimatedMinutes,
                        IsCompleted = false,
                        OrderIndex = lessonIndex + 1,
                        Difficulty = lessonDefinition.Difficulty,
                        ContentStatus = "Draft"
                    };
                    db.Lessons.Add(lesson);
                    continue;
                }

                // A refresh may encounter an earlier outline-only import. Complete that
                // row, but never replace a substantive body or alter progress metadata.
                if (string.IsNullOrWhiteSpace(lesson.ContentBody) || lesson.ContentStatus == "Outline")
                {
                    lesson.ContentBody = lessonDefinition.ContentBody;
                    lesson.UpdatedAt = DateTime.UtcNow;
                    if (string.IsNullOrWhiteSpace(lesson.ContentStatus) || lesson.ContentStatus == "Outline")
                    {
                        lesson.ContentStatus = "Draft";
                    }
                }
            }
        }
    }

    private static IReadOnlyList<ExpandedModuleSeed> GetExpandedModules()
    {
        return new List<ExpandedModuleSeed>
        {
            new(
                "databases-sql",
                "Databases & SQL",
                "Relational modeling, query design, transactions, and production data access for backend systems.",
                "Module 8",
                0,
                new[]
                {
                    Chapter("db-sql-01-introduction-keys", "Introduction to DBMS & Keys", "Tables, relationships, constraints, and key design.", "A DBMS is responsible for durable storage, concurrency control, recovery, and query execution; an application should still make ownership and invariants explicit. Compare natural, surrogate, primary, candidate, and foreign keys, and understand why a constraint is stronger than a validation performed only in application code.", "Model a booking system with customers, events, seats, and reservations. The database must prevent two reservations for the same event-seat pair even when two API instances race.", "Draw the entity relationships, declare keys and constraints, insert valid and invalid rows, and explain which invariant belongs in the database.", "You can choose keys from identity and lifecycle needs, explain referential integrity, and show a database constraint rejecting an invalid booking.", "Add a soft-delete policy and explain how it affects uniqueness, foreign keys, and historical reporting.", 60, "PostgreSQL Documentation: Constraints"),
                    Chapter("db-sql-02-crud-operations-1", "CRUD Operations - 1", "Insert, update, delete, and select operations with safe parameters.", "CRUD is not merely syntax: predicates, null semantics, affected-row counts, and parameter binding determine correctness. A command should state whether zero matching rows is an error, a no-op, or an idempotent retry.", "Implement a customer profile update endpoint using parameterized SQL. A retry should not accidentally update every customer because a filter was omitted.", "Write parameterized inserts and updates, test null and duplicate cases, inspect affected-row counts, and make a delete policy explicit.", "You can distinguish a safe command from an unsafe string-built query and define the outcome of repeated updates and deletes.", "Add an audit table and record the actor and reason without placing credentials or raw SQL in logs.", 60, "PostgreSQL Documentation: SQL Commands"),
                    Chapter("db-sql-03-crud-operations-2", "CRUD Operations - 2", "Pagination, ordering, null handling, and reliable write responses.", "Production CRUD needs deterministic ordering, bounded result sets, and a clear response after a write. Offset pagination is simple but can drift under inserts; keyset pagination trades arbitrary page jumps for stable traversal.", "Build an order-history query that remains stable while new orders arrive. Return a cursor based on created time and id so a client can resume without duplicates.", "Implement offset and keyset versions, add a compound sort, test ties and null values, and compare the query plan for a large result set.", "You can explain why `ORDER BY` is required for deterministic pagination and choose a cursor that is unique and opaque to the client.", "Add an export job with a repeatable snapshot boundary and document how late-arriving records are handled.", 75, "PostgreSQL Documentation: LIMIT and OFFSET"),
                    Chapter("db-sql-04-joins", "Joins", "Inner, outer, semi, and anti-joins for relational data.", "Joins express how rows from different relations combine. The join predicate, null behavior, and cardinality determine whether the result is complete, duplicated, or silently filtered.", "Return a booking list with customer name, event title, payment state, and optional refund information. A left join must retain bookings that have no refund.", "Write inner, left, and anti-join queries, inspect duplicate rows, and verify the expected row count with deliberately missing relationships.", "You can choose a join from the business question, identify accidental fan-out, and explain why a filter in `WHERE` can change an outer join into an inner one.", "Refactor a large join into a read model when the endpoint has a stable high-volume access pattern.", 75, "PostgreSQL Documentation: Table Expressions"),
                    Chapter("db-sql-05-aggregate-queries", "Aggregate Queries", "GROUP BY, HAVING, nulls, and metric correctness.", "Aggregations turn events into business measures, but the grouping grain must be explicit. Count rows only when row multiplicity is understood, and distinguish `count(*)`, `count(column)`, and distinct counts.", "Produce daily payment totals by merchant while excluding test transactions and separating authorized from settled amounts.", "State the metric grain, write grouped queries, add `HAVING` thresholds, test empty groups and nulls, and reconcile the result with a hand-calculated sample.", "You can identify double counting caused by joins and explain why a metric needs a documented grain and filter policy.", "Materialize a daily summary and compare its refresh strategy with computing the aggregate at request time.", 75, "PostgreSQL Documentation: Aggregate Functions"),
                    Chapter("db-sql-06-joins-aggregates-workshop", "Joins and Aggregate Queries Working Session", "Combining joins and aggregates without changing the metric grain.", "This working session focuses on query reasoning: establish the base relation, join one relationship at a time, and aggregate only after deciding whether the join multiplies facts. Pre-aggregation or distinct keys may be required.", "Calculate average delivery time per city from orders, deliveries, and driver assignments without counting an order once per status event.", "Write the query in stages, inspect intermediate row counts, add a counterexample, and compare a correlated query with a pre-aggregated subquery.", "You can defend every row in the final result and find a double-counting bug by checking intermediate cardinality.", "Create a small query test fixture that fails when a future schema change changes the metric grain.", 90, "PostgreSQL Documentation: Queries"),
                    Chapter("db-sql-07-subqueries-views", "Subqueries & Views", "Correlated subqueries, common table expressions, and views.", "A subquery can express existence, ranking, or a derived relation. Common table expressions improve readability, while views expose a stable read contract; neither automatically makes a query fast or materialized.", "Expose the latest successful payment per order and hide provider-specific columns behind a view used by support tooling.", "Implement `EXISTS`, a scalar subquery, and a CTE; compare their plans; create a view with an explicit ownership and change policy.", "You can choose a subquery based on the question, explain correlation cost, and treat a view as an API with compatibility expectations.", "Add a materialized view for a measured reporting workload and document refresh staleness.", 75, "PostgreSQL Documentation: WITH Queries"),
                    Chapter("db-sql-08-indexing", "Indexing", "B-tree access, composite indexes, selectivity, and query plans.", "An index is a write and storage trade-off that supports a particular access pattern. Column order, equality and range predicates, sort order, partial predicates, and data distribution all influence whether the planner can use it.", "Speed up a support query for a tenant's recent failed payments without making every insert pay for an unnecessary index.", "Capture a baseline with `EXPLAIN`, add the smallest useful index, measure again, and test a query that does not match the index prefix.", "You can tie an index to a concrete query shape and explain why an index may be ignored or make writes slower.", "Review unused indexes from production statistics and propose a safe removal process with rollback evidence.", 90, "PostgreSQL Documentation: Indexes and EXPLAIN"),
                    Chapter("db-sql-09-transactions", "Transactions", "Atomicity, isolation, locks, retries, and transaction boundaries.", "A transaction defines which changes succeed together and what concurrent work may observe. Isolation is a business trade-off: stronger guarantees can increase waiting, while weaker isolation requires conflict handling.", "Reserve the last inventory unit and create an order atomically. A timeout must not leave a reservation that the user cannot see or release.", "Run two concurrent transactions, observe a conflict, choose an isolation level, and make the retry or user-visible failure behavior explicit.", "You can identify the transaction boundary, explain a lock wait, and distinguish a database retry from blindly repeating a side effect.", "Add an outbox row in the same transaction and design a publisher that can safely retry delivery.", 90, "PostgreSQL Documentation: Transaction Isolation"),
                    Chapter("db-sql-10-window-functions", "Window Functions", "Ranking, running totals, partitions, and frame semantics.", "Window functions calculate across related rows without collapsing the result set. Partition, order, and frame clauses are separate decisions; a default frame can surprise a cumulative metric when values tie.", "Show each merchant's payment with its running settled total, previous payment, and rank within the merchant's day.", "Implement `row_number`, `lag`, and a running sum, test ties and partitions, and verify the frame against a manually calculated example.", "You can select a window function instead of a self-join and explain how partitioning and framing affect the result.", "Use a window query to identify late-arriving events and feed a reconciliation report.", 90, "PostgreSQL Documentation: Window Functions"),
                    Chapter("db-sql-11-schema-design-1", "Schema Design - 1", "Normalization, aggregates, ownership, and lifecycle modeling.", "Schema design starts with business facts and update rules. Normalize data that changes independently, keep derived values deliberate, and model state transitions so invalid combinations are difficult to store.", "Design a ride-booking schema that separates a ride request, assignment, payment attempt, and driver location while preserving historical facts.", "Write the functional dependencies, normalize the first draft, identify aggregate boundaries, and choose which values are snapshots versus references.", "You can explain why a table exists, what one row means, and which changes must be atomic.", "Review the model for tenant isolation, retention, auditability, and migration cost before adding indexes.", 90, "PostgreSQL Documentation: Data Definition"),
                    Chapter("db-sql-12-schema-design-2", "Schema Design - 2", "Denormalization, partitioning, constraints, and migration-ready design.", "Denormalization is justified by measured reads, not by fear of joins. Store derived data with a refresh or correction path, use constraints for invariants, and plan schema changes for old and new application versions.", "Design an order-event table that can serve customer history and operational analytics while growing by millions of rows per day.", "Compare normalized and read-optimized models, choose a partition key, write a backfill plan, and test dual-read or dual-write compatibility.", "You can defend a denormalization decision with a workload, consistency model, and repair strategy.", "Simulate a rolling deployment where the old API and new API both read the schema safely.", 90, "PostgreSQL Documentation: Table Partitioning"),
                    Chapter("db-sql-13-contest", "Databases & SQL Contest: SQL and Schema Design", "Timed query reasoning, schema choices, and production trade-offs.", "The contest evaluates whether you can turn an ambiguous backend requirement into a clear grain, schema, query, constraint, and performance plan. Correctness comes before clever SQL.", "Build the data layer for a marketplace with merchants, orders, refunds, inventory, and daily settlement while handling duplicate events and late corrections.", "Clarify assumptions, sketch the schema, implement the highest-value queries, add constraints, inspect plans, and record unresolved trade-offs.", "You can explain every table and query, prove the important invariants, and identify what must be measured before launch.", "Write a short review of the design as if handing it to an on-call engineer, including rollback and reconciliation steps.", 120, "PostgreSQL Documentation: SQL Command Reference")
                }),
            new(
                "high-level-design",
                "High-Level Design",
                "Distributed-system fundamentals, scalable infrastructure, data platforms, and AI-aware system design.",
                "Module 15",
                10,
                new[]
                {
                    Chapter("hld-01-foundations", "System Design Foundations & Modern Infrastructure", "Requirements, capacity, boundaries, and architecture trade-offs.", "HLD starts with user journeys, scale assumptions, consistency needs, and failure budgets. Components should follow ownership and workload rather than fashionable technology names.", "Design a multi-tenant document platform from request volume, object sizes, latency targets, and retention requirements.", "Write functional and non-functional requirements, estimate rough capacity, draw the first architecture, and list the riskiest assumptions.", "You can communicate an architecture from requirements and identify what must be measured before choosing a technology.", "Add a cost and operational review to the design record.", 90, "AWS Well-Architected Framework"),
                    Chapter("hld-02-load-balancing", "Load Balancing, Consistent Hashing & Traffic Routing at Scale", "Routing, health, stickiness, hashing, and failover.", "Load balancing distributes work while preserving the state and locality guarantees a system needs. Consistent hashing reduces movement during membership changes but does not solve hot keys or unhealthy nodes by itself.", "Route requests for tenants and documents across service replicas while keeping a cache key near its data when helpful.", "Compare round robin, least-loaded, and hash-based routing; model node removal; and define health and retry behavior.", "You can explain why a routing choice affects cache locality, failover, and hot-spot risk.", "Add a hot-key mitigation strategy and a controlled zone failure test.", 90, "AWS Elastic Load Balancing Documentation"),
                    Chapter("hld-03-caching", "Caching Systems: CDN, Backend Caches, Cache Invalidation", "Cache layers, TTL, invalidation, and stale-data policy.", "Caching is a consistency decision. Define what may be stale, who invalidates it, how misses behave, and how memory pressure or a cache outage affects the source of truth.", "Serve public document metadata through a CDN and tenant-scoped search results through a backend cache without leaking private data.", "Choose keys and TTLs, model cache-aside behavior, test invalidation and stampede control, and define cache outage behavior.", "You can state the freshness contract and identify a cache key that would be unsafe.", "Add request coalescing and measure hit rate, staleness, and origin load.", 90, "AWS Caching Best Practices"),
                    Chapter("hld-04-caching-case", "Case Study: Caching at Scale", "Cache design for judge, leaderboard, and AI workload patterns.", "High-read systems have different cache shapes: a leaderboard may need sorted updates, a code judge needs result isolation, and an AI workload may need semantic or response caching with careful privacy boundaries.", "Design caches for contest rankings and repeated model prompts, including invalidation when a submission or prompt version changes.", "Map keys, write paths, TTLs, and consistency needs for each workload; identify what cannot be shared across tenants.", "You can explain why one cache policy cannot be copied across all read-heavy features.", "Add a stampede test and a cost comparison between recomputation and cached responses.", 90, "Redis Documentation"),
                    Chapter("hld-05-facebook-feed", "Case Study: Caching Facebook News Feed", "Fan-out choices, feed ranking, and freshness.", "A feed design balances write amplification, read latency, ranking freshness, and celebrity or hot-user effects. Fan-out-on-write and fan-out-on-read are workload choices, not universal rules.", "Design a personalized activity feed where a small set of publishers has millions of followers and AI ranking is an optional layer.", "Estimate fan-out work, choose a hybrid strategy, define cache invalidation, and handle a ranking service timeout.", "You can explain what is precomputed, what is assembled on read, and how a hot publisher is contained.", "Add a backfill or replay plan when the ranking model version changes.", 90, "Distributed Feed System Design Practice"),
                    Chapter("hld-06-cap-pacelc", "CAP/PACELC Theorem + Master-Slave Replication", "Consistency, availability, latency, and replication lag.", "Distributed systems make trade-offs under partition and normal operation. CAP describes a partition scenario; PACELC adds the latency-versus-consistency decision when the network is healthy. Replication lag must be visible to product behavior.", "A customer reads order status from a replica immediately after writing through the primary.", "State the read-after-write requirement, choose routing or session guarantees, and define what stale data the UI can show.", "You can avoid treating CAP as a database product label and describe the user-visible compromise.", "Add a lag-aware read policy and an alert threshold.", 90, "AWS Database Reliability Guidance"),
                    Chapter("hld-07-sql-nosql-sharding", "SQL vs NoSQL + Sharding", "Data models, partition keys, and operational trade-offs.", "Choose a data model from access patterns, invariants, query flexibility, and operational needs. Sharding can improve scale but makes transactions, queries, rebalancing, and cross-shard uniqueness harder.", "Store tenant documents and processing events where tenant isolation, time-based queries, and per-document state are important.", "Compare a relational and a key-value model, choose a partition key, and list cross-partition operations that need a redesign.", "You can defend the choice without claiming that one database family is universally superior.", "Design a resharding and hot-tenant mitigation plan.", 90, "AWS Database Selection Guidance"),
                    Chapter("hld-08-shard-creation", "Database Orchestration & Shard Creation", "Shard lifecycle, placement, migrations, and routing metadata.", "Shards are an operational system: placement, capacity, ownership, schema version, and routing must be managed. A new shard should become usable through a controlled workflow, not a manual mystery step.", "Provision a tenant shard, copy or initialize schema, update routing, and roll back if health checks fail.", "Define shard metadata, create a state machine, handle partial provisioning, and test a routing update during traffic.", "You can explain how a request finds a shard and how operators recover from a half-created shard.", "Add a rebalancing plan with dual-read or migration checkpoints.", 90, "PostgreSQL Documentation: Partitioning"),
                    Chapter("hld-09-typeahead-approach", "Case Study: Google Typeahead - How to Approach System Design Problems", "Latency goals, query shaping, indexing, and ranking requirements.", "A typeahead design begins with keystroke rate, prefix distribution, result freshness, response budget, and language requirements. The architecture follows those constraints.", "Design autocomplete for products and documents with prefix matching, typo tolerance, tenant filters, and a strict response deadline.", "Estimate query volume, define the index, decide update latency, and write the fallback for an unavailable search tier.", "You can turn a vague autocomplete prompt into measurable requirements and a staged design.", "Add an evaluation set for relevance and latency by prefix frequency.", 75, "Elasticsearch Documentation"),
                    Chapter("hld-10-typeahead-optimization", "Case Study: Google Typeahead - Design and Optimizations", "Caching prefixes, compression, ranking, and incremental updates.", "Optimization should target a measured bottleneck. Popular prefixes may be cached, indexes may be compressed, and ranking can be tiered, but every shortcut has freshness or memory cost.", "Reduce p95 latency for common prefixes while keeping new products searchable within a defined freshness window.", "Measure a baseline, add one optimization at a time, test hot prefixes and cold misses, and document the capacity impact.", "You can connect each optimization to a metric and explain its failure behavior.", "Add admission control so a flood of unique prefixes does not evict useful entries.", 75, "Elasticsearch Documentation"),
                    Chapter("hld-11-lsm-multimaster", "NoSQL Internals - LSM Tree and Multi-Master", "Write paths, compaction, conflict resolution, and read amplification.", "LSM-based systems trade write behavior for compaction and read amplification. Multi-master replication improves write locality and availability but requires explicit conflict resolution and convergence semantics.", "Store high-volume event writes and tolerate regional connectivity gaps while preserving idempotent event identity.", "Trace memtable, log, SSTable, and compaction behavior conceptually; define a conflict key and resolution rule.", "You can explain the operational cost behind the write throughput headline.", "Add tombstone-retention and compaction-pressure signals to an operations plan.", 90, "Apache Cassandra Documentation"),
                    Chapter("hld-12-messaging", "Case Study: Messaging Apps", "Conversation ordering, delivery, presence, and fan-out.", "Messaging systems need a clear ordering scope, delivery semantics, durable history, and presence that is allowed to be approximate. User experience should reflect pending, delivered, and failed states.", "Design direct and group messaging with offline devices, retries, attachments, and AI-assisted summaries that cannot reorder the source conversation.", "Define message ids and ordering, choose storage and queue boundaries, and model reconnect and duplicate delivery.", "You can explain what ordering is guaranteed and how a client reconciles after reconnect.", "Add retention and abuse controls without coupling moderation to message delivery correctness.", 90, "Apache Kafka Documentation"),
                    Chapter("hld-13-kafka", "Messaging Queues - Apache Kafka & Zookeeper", "Partitions, keys, consumer groups, offsets, and rebalancing.", "Kafka provides an ordered log per partition and replayable offsets. Partition keys determine ordering and parallelism, while consumers must handle duplicates and reprocessing.", "Publish order and document-processing events so independent consumers build search, notifications, and audit views.", "Choose keys, model consumer groups, handle offset commits and poison messages, and define replay safety.", "You can explain partition-scoped ordering and why a consumer cannot assume exactly-once business effects without idempotency.", "Add an outbox and a lag-based alert.", 90, "Apache Kafka Documentation"),
                    Chapter("hld-14-elasticsearch", "Case Study: Elasticsearch - Full Text Search", "Inverted indexes, analyzers, relevance, and operational search limits.", "Search indexes are derived views. Choose analyzers and fields from language and query needs, keep source-of-truth data elsewhere, and define refresh and reindex behavior.", "Index tenant documents for keyword and semantic-assisted search while applying authorization filters before returning results.", "Design mappings, analyzers, query clauses, refresh expectations, and a reindex plan for a changed schema.", "You can explain why a search result is not the authoritative document and how deleted or restricted data is removed.", "Add relevance and authorization regression tests.", 90, "Elasticsearch Documentation"),
                    Chapter("hld-15-s3-hdfs", "Case Study: S3 and HDFS - Large File Storage", "Object storage, distributed file systems, multipart transfer, and metadata.", "Large-file systems separate metadata from bytes and optimize for throughput, durability, and parallel access. Object stores have different consistency and namespace behavior from a filesystem.", "Store uploaded documents and derived artifacts with tenant isolation, checksums, lifecycle retention, and resumable uploads.", "Define object keys, metadata, multipart boundaries, access controls, and recovery after a partial upload.", "You can choose object storage or a distributed filesystem from access and processing needs.", "Add a garbage-collection job for abandoned multipart uploads.", 90, "AWS S3 Documentation"),
                    Chapter("hld-16-uber", "Case Study: Uber - Nearest Neighbor Search", "Geo-partitioning, indexing, freshness, and dispatch constraints.", "Nearest-neighbor systems trade exactness, update cost, and latency. Dispatch also needs availability, fairness, and concurrency controls beyond finding the closest coordinate.", "Find eligible drivers near a pickup while respecting vehicle type, current assignment, tenant or region, and stale location data.", "Choose a spatial index, define freshness, filter eligibility, and handle a driver becoming unavailable between search and assignment.", "You can distinguish candidate search from the authoritative assignment transaction.", "Add a hot-zone strategy and a metric for rejected stale candidates.", 90, "PostGIS Documentation"),
                    Chapter("hld-17-rate-limit", "Case Study: Rate Limiter + Unique ID Generator", "Quotas, algorithms, coordination, and globally safe identity.", "Rate limiting is a product and reliability policy. Token bucket, leaky bucket, fixed window, and sliding window have different burst and storage behavior. Unique ids need collision, ordering, and region considerations.", "Protect a model API by tenant and endpoint while generating request ids that remain unique across replicas and regions.", "Choose a limit algorithm, define fail-open or fail-closed behavior, and compare UUID, database, and time-sortable id strategies.", "You can explain the consistency needed for a quota and the operational effect of a limiter outage.", "Add a dry-run mode and quota headers for clients.", 90, "AWS API Gateway Throttling Documentation"),
                    Chapter("hld-18-ott", "Case Study: OTT Platform", "Catalog, playback, CDN, entitlements, and adaptive delivery.", "An OTT design separates control-plane metadata from high-bandwidth media delivery. CDN placement, encoding, entitlement checks, and playback telemetry have different freshness and scaling needs.", "Serve a video catalog with regional rights, adaptive streams, subscriptions, and AI-generated recommendations without putting media bytes through the application tier.", "Draw control and data paths, define caching and entitlement checks, and identify what happens when the recommendation service is down.", "You can explain where scale comes from and which consistency compromises the viewer can tolerate.", "Add a playback QoE metric and a multi-CDN failover policy.", 90, "AWS Media Services Documentation"),
                    Chapter("hld-19-microservices-1", "Microservices - 1", "Service boundaries, data ownership, contracts, and workflow choice.", "Microservices require independent ownership and deployment value. Each service should own its data and expose a contract; cross-service workflows need explicit orchestration or choreography and failure states.", "Split a marketplace into order, payment, inventory, and notification capabilities only when their release or scaling needs justify the cost.", "Map bounded contexts, write APIs and events, identify distributed transactions, and compare a modular monolith with service decomposition.", "You can defend a boundary and name the operational costs it introduces.", "Design an incremental extraction with compatibility and rollback checkpoints.", 90, "AWS Prescriptive Guidance: Microservices"),
                    Chapter("hld-20-microservices-2", "Microservices - 2", "Observability, resilience, deployment, and data consistency across services.", "A distributed system needs trace context, stable error contracts, idempotent consumers, deadlines, and deployment compatibility. Eventual consistency must be visible to users and operators.", "Operate a document workflow across intake, extraction, indexing, and notification services during a provider outage and a rolling deployment.", "Add trace spans, retries with budgets, a dead-letter path, contract compatibility, and a reconciliation process.", "You can trace a failed request, explain its partial state, and identify a safe recovery action.", "Write a service-level objective and an incident runbook for the most likely dependency failure.", 90, "OpenTelemetry Documentation"),
                    Chapter("hld-21-ecommerce", "Case Study: Ecommerce Platform (Microservices)", "Catalog, cart, checkout, inventory, payments, orders, and asynchronous workflows.", "An ecommerce platform is a useful microservices exercise because its domains have different consistency and scaling needs. Catalog browsing can tolerate cached or eventually consistent reads, while inventory reservation, payment authorization, and order state require explicit invariants, idempotency, and auditable transitions. Events connect the workflow, but each service must remain authoritative for its own state.", "Design a multi-tenant ecommerce platform where a customer browses a catalog, adds an item to a cart, checks out, and receives an order confirmation while inventory is contested and a payment provider may retry or time out.", "Define bounded contexts and ownership, estimate traffic for browse versus checkout, model the order saga, add idempotency keys and an outbox, choose synchronous versus asynchronous calls, and test duplicate requests, reservation expiry, payment uncertainty, and compensating actions.", "You can explain which operations require strong coordination, how an order moves through states, how duplicate events are made harmless, and how operators recover an order stuck between payment and fulfillment.", "Add regional traffic routing, inventory oversell protection, contract-versioned events, fraud review, and an SLO dashboard covering checkout success, reservation latency, payment reconciliation, and fulfillment lag.", 120, "AWS Prescriptive Guidance: Microservices")
                }),
            new(
                "data-engineering",
                "Data Engineering",
                "Batch, streaming, distributed storage, orchestration, and data-product foundations for backend engineers.",
                "Module 17",
                11,
                new[]
                {
                    Chapter("data-01-introduction", "Introduction to Data Engineering", "Data products, batch versus streaming, quality, and ownership.", "Data engineering turns operational events into reliable, discoverable, and usable datasets. A pipeline needs an owner, schema, freshness target, quality checks, lineage, and recovery plan.", "Turn order and payment events into a daily settlement dataset and a near-real-time operational view.", "Map sources, transformations, sinks, SLAs, and failure modes; define a small data contract before choosing tools.", "You can explain the difference between an operational database and an analytical data product.", "Add a data-quality scorecard and a backfill policy.", 60, "Apache Spark Documentation"),
                    Chapter("data-02-efficient-queries-1", "Writing Efficient Queries: Part 1", "Filtering, projection, joins, and query plans for analytical workloads.", "Efficient queries reduce scanned data and unnecessary materialization. Select only needed columns, filter early when safe, understand join cardinality, and use the planner to validate assumptions.", "Produce a merchant settlement report from partitioned order and payment data without scanning unrelated tenants or dates.", "Write a baseline query, inspect its plan, reduce scan volume, and test correctness against a small fixture.", "You can tie a query change to bytes scanned, latency, and result correctness.", "Add a regression threshold for a scheduled report.", 75, "PostgreSQL Documentation: EXPLAIN"),
                    Chapter("data-03-efficient-queries-2", "Writing Efficient Queries: Part 2", "Partition pruning, skew, aggregation, and incremental computation.", "Large queries fail through skew, shuffles, wide rows, and repeated full scans. Incremental processing and partition-aware writes reduce cost, but late data and corrections must be handled.", "Recompute a merchant's daily metrics after late payment events without rebuilding the entire warehouse.", "Measure skew, choose a partition and clustering strategy, compare full and incremental aggregates, and define correction behavior.", "You can explain the expensive stage and when incremental results may be temporarily incomplete.", "Add a watermark and a late-arrival reconciliation window.", 75, "Apache Spark Documentation"),
                    Chapter("data-04-hadoop", "Intro to Hadoop", "Distributed storage and compute concepts in the Hadoop ecosystem.", "Hadoop popularized separating distributed storage from parallel batch computation. The lasting concepts are data locality, replication, task failure, and processing data in parallel across nodes.", "Process historical click or order events that are too large for a single machine while tolerating worker failure.", "Trace a file through distributed storage and a batch job, identify replication and locality decisions, and compare with object storage plus managed compute.", "You can explain the problem Hadoop solves and why newer systems may be chosen today.", "Document a migration from legacy Hadoop jobs to a managed lakehouse workflow.", 60, "Apache Hadoop Documentation"),
                    Chapter("data-05-hdfs-mapreduce", "HDFS and MapReduce", "Blocks, replication, map, shuffle, reduce, and failure recovery.", "MapReduce makes data movement explicit: map produces keyed records, shuffle groups them, and reduce combines them. The shuffle is often the cost center, and reducers need a strategy for skew.", "Count and aggregate events by merchant while one key is much hotter than the rest.", "Design the key, map and reduce functions, estimate shuffle volume, and handle malformed records without losing the whole job.", "You can identify where data moves and why a bad key creates a straggler.", "Add a combiner or pre-aggregation and measure the reduction in shuffle data.", 75, "Apache Hadoop MapReduce Documentation"),
                    Chapter("data-06-hive", "Introduction to Hive", "SQL-on-files, schemas, partitions, and table ownership.", "Hive provides a relational interface over distributed data, but file format, partition layout, schema evolution, and small-file behavior still determine performance and reliability.", "Expose an event lake as partitioned tables for analysts while keeping raw immutable data available for replay.", "Define an external table, partition strategy, schema owner, and a query that avoids scanning unrelated partitions.", "You can explain the difference between table metadata and underlying files.", "Add a compaction or small-file mitigation runbook.", 75, "Apache Hive Documentation"),
                    Chapter("data-07-hive-advanced", "Advanced Features of Hive", "Partitioning, bucketing, joins, schema evolution, and warehouse operations.", "Advanced warehouse design is about predictable access and controlled change. Bucketing can help specific joins, while schema evolution must preserve old readers and historical meaning.", "Optimize a recurring customer-activity report and add a nullable field without breaking downstream consumers.", "Compare partition and bucket choices, test a schema change, and document table statistics and retention.", "You can explain which optimization is workload-specific and how a consumer discovers a schema change.", "Add a data catalog entry with lineage and quality ownership.", 90, "Apache Hive Documentation"),
                    Chapter("data-08-spark-basics", "Basics of Spark", "Driver, executors, transformations, actions, and resilient computation.", "Spark builds a logical plan and executes distributed transformations when an action is requested. Partition count, serialization, memory, and shuffle behavior matter more than the API surface alone.", "Clean a large event dataset and compute daily aggregates while one executor is lost during the job.", "Trace a lazy transformation graph, choose an action, observe partitions, and explain how recomputation works.", "You can distinguish a transformation from an action and identify when a shuffle occurs.", "Add a checkpoint or persisted dataset only when reuse justifies the storage cost.", 75, "Apache Spark Documentation: RDD Programming Guide"),
                    Chapter("data-09-spark-programming", "Spark Programming", "DataFrames, schemas, joins, aggregations, and job structure.", "A Spark job should have a clear input contract, typed or validated transformations, bounded output, and metrics. Avoid collecting large data to the driver and make skew visible.", "Build a batch job that creates a tenant-safe settlement dataset from events and writes partitioned output.", "Define the schema, implement transformations, test a small fixture, inspect the plan, and run a failure or skew scenario.", "You can explain the job's stages and why the driver remains bounded.", "Add a data-quality quarantine output for malformed records.", 90, "Apache Spark Documentation: SQL Programming Guide"),
                    Chapter("data-10-pyspark-structured-api", "Structured API - PySpark", "Declarative schemas, expressions, and typed data transformations.", "Structured APIs allow the engine to optimize a logical plan, but correctness still depends on explicit schemas, null behavior, and deterministic transformations.", "Transform semi-structured AI extraction results into a typed dataset with rejected records separated from valid facts.", "Define schemas, handle nulls explicitly, compare inferred and declared schemas, and test nested field transformations.", "You can explain how schema choices affect both correctness and optimization.", "Add a schema registry or versioned manifest for downstream consumers.", 75, "Apache Spark Documentation: DataFrame API"),
                    Chapter("data-11-pyspark-operations", "PySpark Operations", "Joins, windows, UDF trade-offs, caching, and output layout.", "PySpark code can hide distributed costs. Prefer native expressions over Python UDFs when possible, control join strategy, and cache only data reused within a measured job.", "Calculate latest payment status per order and detect duplicate provider events at scale.", "Use window functions, compare a native expression with a UDF, inspect a join plan, and tune output partitioning.", "You can identify a Python boundary or shuffle that drives cost and prove the result remains correct.", "Add a benchmark fixture that runs in CI with a small but representative skew.", 90, "Apache Spark Documentation: Performance Tuning"),
                    Chapter("data-12-streaming-intro", "Introduction to Streaming", "Events, time, delivery, watermarks, and state.", "Streaming systems process unbounded data. Event time, processing time, late data, replay, and state retention determine whether a result is trustworthy.", "Update order metrics as events arrive out of order and allow a bounded delay before closing a daily window.", "Define event and processing timestamps, choose a watermark, model duplicates, and state what happens after a restart.", "You can explain the difference between at-least-once input and exactly-once business effects.", "Add a replay command that rebuilds a window from immutable events.", 75, "Apache Spark Structured Streaming Documentation"),
                    Chapter("data-13-spark-streaming", "Apache Spark Streaming", "Structured Streaming queries, checkpoints, sinks, and triggers.", "Structured Streaming turns a declarative query into a long-running job. Checkpoints, output mode, trigger interval, and sink idempotency form the recovery contract.", "Aggregate payment events into a live merchant dashboard and write results to a durable sink.", "Configure a checkpoint, choose output mode, test a restart, and verify duplicate input handling.", "You can explain what the checkpoint stores and when a sink can safely accept retries.", "Add a backpressure metric and a controlled pause/resume procedure.", 90, "Apache Spark Structured Streaming Documentation"),
                    Chapter("data-14-advanced-streaming", "Advanced Spark Streaming", "Stateful operations, joins, late data, and operational tuning.", "Stateful streams need bounded state, cleanup, and a plan for late or corrupt events. Stream-stream joins and aggregations should be constrained by time or keys.", "Correlate order and payment events arriving on different streams while keeping state within an explicit retention window.", "Define watermarks and join windows, inject late events, observe state growth, and test recovery from a checkpoint.", "You can explain when an event is too late and how the system reports incomplete or corrected results.", "Add a reconciliation stream for events outside the normal watermark.", 90, "Apache Spark Structured Streaming Documentation"),
                    Chapter("data-15-streaming-services", "Additional Streaming Services: Bringing It All Together", "Brokers, schemas, processors, sinks, and end-to-end contracts.", "A streaming architecture is a chain of contracts. Event schema, partition key, retention, consumer ownership, replay, and dead-letter behavior should be designed together.", "Publish application events through Kafka, process them with Spark, write a warehouse table, and update an operational read model.", "Draw the end-to-end path, choose schema and key policies, test a consumer restart, and define replay without duplicating side effects.", "You can trace an event from producer to sink and identify each point where data can be delayed or lost.", "Add lineage metadata and a per-stage freshness dashboard.", 90, "Apache Kafka Documentation"),
                    Chapter("data-16-modern-architectures", "Modern Data Architectures", "Lake, warehouse, lakehouse, serving layers, and data contracts.", "Modern architectures separate raw immutable data, curated analytical tables, and low-latency serving views. The right shape depends on governance, freshness, cost, and consumer needs.", "Design a platform for operational analytics, ML features, and customer-facing search without allowing each consumer to build an inconsistent copy.", "Map data products, ownership, storage layers, quality gates, and serving paths; call out the source of truth for each fact.", "You can describe how data moves and why a layer exists.", "Add a contract-change process and a lineage view for a critical metric.", 90, "AWS Data Analytics Lens"),
                    Chapter("data-17-aws-services", "AWS Services for Data Engineering", "Object storage, catalog, compute, streaming, query, and security choices.", "Managed services reduce undifferentiated operations but create integration and cost decisions. Choose services from latency, scale, format, governance, and recovery requirements.", "Build an AWS data path using S3 for raw data, a catalog, distributed processing, and a query layer with tenant-aware access.", "Map each requirement to one service, define IAM boundaries, encryption and retention, and identify a local development substitute.", "You can explain what each managed service contributes and what remains your responsibility.", "Add cost allocation tags and a lifecycle policy for raw and curated data.", 90, "AWS Analytics Services Documentation"),
                    Chapter("data-18-data-modelling", "Data Modelling", "Facts, dimensions, events, grain, slowly changing attributes, and analytical keys.", "Analytical models make a row's grain explicit. Facts record measurable events, dimensions provide context, and slowly changing attributes require a choice about historical meaning.", "Model order revenue by merchant, product, day, and region while preserving the merchant region at the time of purchase.", "Declare the grain, design fact and dimension tables, choose surrogate or natural keys, and test a late dimension change.", "You can identify double-counting risk and explain which historical value a report should show.", "Add a semantic metric definition for revenue and settlement.", 90, "Kimball Dimensional Modeling Reference"),
                    Chapter("data-19-orchestration", "Orchestrating Data Pipelines", "DAGs, dependencies, retries, idempotency, and backfills.", "Orchestration is about making work observable and repeatable. A task should have inputs, outputs, retry policy, timeout, ownership, and a recovery or backfill path.", "Schedule a daily settlement pipeline that depends on raw ingestion, quality checks, transformation, and publication.", "Draw the DAG, make tasks idempotent, define retry and alert policy, and run a historical backfill without overwriting corrected facts.", "You can explain the state of a failed run and the safe next action.", "Add a run ledger and a freshness SLO.", 75, "Apache Airflow Documentation"),
                    Chapter("data-20-orchestration-continued", "Orchestration Continued", "Sensors, dynamic tasks, deployment, and operational recovery.", "Complex pipelines need bounded dynamic work, dependency checks, concurrency limits, and a deployment strategy that does not silently rerun expensive tasks.", "Process one partition per tenant or date while limiting concurrency and skipping partitions that are already complete.", "Add dependency sensors, run-level idempotency, a concurrency cap, and a resume path after a worker failure.", "You can show how an operator retries one safe task instead of restarting the entire DAG.", "Add a dry-run backfill planner and a cost estimate.", 75, "Apache Airflow Documentation"),
                    Chapter("data-21-distributed-coordination", "Distributed Coordination", "Leases, leader election, locks, and coordination failure.", "Coordination primitives have expiry, ownership, and split-brain behavior. A lock is not a substitute for an idempotent operation or a durable source of truth.", "Only one pipeline coordinator may publish a daily partition while workers process independent shards.", "Define lease ownership and renewal, simulate a coordinator pause, and make publication idempotent after a takeover.", "You can explain what happens when the owner disappears and why fencing or version checks may be required.", "Add a reconciliation task that detects overlapping or missing partition ownership.", 75, "Kubernetes Documentation: Leases"),
                    Chapter("data-22-load-balancing", "Load Balancing", "Data-worker placement, skew, throughput, and fairness.", "Data workloads need balanced partitions and bounded workers. A fast worker does not help if one partition contains most records or a downstream sink has lower capacity.", "Distribute tenant partitions across workers while one enterprise tenant is much larger than the rest.", "Measure partition sizes, split hot partitions, set concurrency, and verify downstream backpressure.", "You can identify whether the bottleneck is compute, shuffle, storage, or the sink.", "Add adaptive partitioning with a reproducible threshold.", 75, "Apache Spark Documentation: Partitioning"),
                    Chapter("data-23-data-pillars", "Data Pillars", "Quality, governance, privacy, lineage, availability, and discoverability.", "A trustworthy data product is accurate enough for its purpose, fresh enough for its SLA, secure, discoverable, and recoverable. Quality checks should be tied to actions, not only dashboards.", "Publish a customer-facing settlement metric with ownership, lineage, freshness, privacy classification, and a correction path.", "Define quality dimensions, checks, alerts, access policy, retention, and a data incident process.", "You can explain who owns a bad number and how a consumer learns whether it is safe to use.", "Create a lightweight data contract template for future FDE and backend projects.", 75, "AWS Data Governance Guidance"),
                    Chapter("data-24-capstone", "Data Engineering Capstone", "End-to-end batch and streaming platform design with evidence.", "The capstone should produce a reliable data product, not a collection of disconnected jobs. Connect ingestion, storage, transformation, serving, quality, lineage, orchestration, and recovery.", "Build an order and payment platform that supports daily settlement, live operations, and a replayable correction path.", "Write contracts and SLAs, implement a representative pipeline, inject late and duplicate events, measure cost and freshness, and present the recovery runbook.", "You can trace a business metric to source events and demonstrate how an operator repairs a failed or late pipeline.", "Add a design review that compares the first architecture with the simplest version you would ship next.", 150, "AWS Data Analytics Lens")
                })
        };
    }

    private static ExpandedLessonSeed Chapter(
        string slug,
        string title,
        string description,
        string concepts,
        string scenario,
        string practice,
        string evidence,
        string extension,
        int estimatedMinutes,
        string reference,
        string difficulty = "Intermediate")
    {
        return new ExpandedLessonSeed(
            slug,
            title,
            description,
            estimatedMinutes,
            reference,
            difficulty,
            $"# {title}\n\n## Concepts Covered\n{concepts}\n\n## Practical Backend Scenario\n{scenario}\n\n## Practice Loop\n{practice}\n\n## Evidence of Understanding\n{evidence}\n\n## Suggested Extension\n{extension}");
    }

    private sealed record ExpandedModuleSeed(
        string Slug,
        string Title,
        string Description,
        string Badge,
        int OrderIndex,
        IReadOnlyList<ExpandedLessonSeed> Lessons);

    private sealed record ExpandedLessonSeed(
        string Slug,
        string Title,
        string Description,
        int EstimatedMinutes,
        string Reference,
        string Difficulty,
        string ContentBody);

    private static void BackfillLessonContent(StudyTrackerContext db, int courseId)
    {
        var lessons = (from lesson in db.Lessons
                       join module in db.Modules on lesson.ModuleId equals module.Id
                       where module.CourseId == courseId
                       select lesson).ToList();

        foreach (var lesson in lessons)
        {
            var authoredContent = GetAuthoredLessonContent(lesson.Slug);
            if (authoredContent == null || !NeedsLessonContent(lesson.ContentBody))
            {
                continue;
            }

            lesson.ContentBody = authoredContent;
            lesson.ContentStatus = "Draft";
            lesson.UpdatedAt = DateTime.UtcNow;
        }
    }

    private static bool NeedsLessonContent(string? content)
    {
        if (string.IsNullOrWhiteSpace(content))
        {
            return true;
        }

        // Preserve an authored body even if it was written outside this seed file.
        if (content.Contains("## Practical Backend Scenario", StringComparison.Ordinal) &&
            content.Contains("## Practice Loop", StringComparison.Ordinal) &&
            content.Contains("## Evidence of Understanding", StringComparison.Ordinal))
        {
            return false;
        }

        return true;
    }

    private static string? GetAuthoredLessonContent(string slug)
    {
        return slug switch
        {
            "01-intro-to-lld" => @"# Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems

## Concepts Covered
System design operates at two altitudes: infrastructure and code. High-Level Design (HLD) answers what components exist and how they connect — load balancers, application servers, databases, caches, message queues. It is a bird's-eye view of the system, deliberately silent on internals. Low-Level Design (LLD) answers how each component is actually written in code. The critical realization is that every infrastructure layer is itself just software. A load balancer is code that reads requests, applies a routing algorithm (round-robin, least-connections, ip-hash), and forwards them. A database is code that handles query parsing, storage engines, indexing, and transaction management. Once HLD has decided what to build, LLD governs how we write that code: maintainably (a teammate can read, modify, and extend it without breaking adjacent behaviour), extensibly (new requirements don't trigger rewrites of existing logic), and reusably (a payment abstraction written once plugs into checkout, refunds, and subscriptions without duplication). The gap between adding a new payment provider taking a day versus three weeks with regressions is an LLD question.

In Procedural style, functions are the active concept and data structs are passive — the puppeteer and the puppets. A `Trip` struct with fields `driverId`, `passengerId`, and `status` can be mutated by `updateTripStatus(trip, ""CANCELLED"")`, by direct assignment `trip.status = ""COMPLETED""`, or by any function across the entire codebase holding a reference. As the system grows across hundreds of files and dozens of engineers, tracing which function corrupted a status field becomes an investigation, not a lookup. OOP resolves this by making entities the primary cognitive unit — a `Trip` object owns its state and exposes controlled methods that enforce business rules at the point where the data lives. Real OOP keeps behaviour close to the data it governs: state transitions belong in the entity, not in an anemic service class that reaches into getters and setters. Service classes coordinate across entities; entities govern their own state.

## Practical Backend Scenario
A passenger requests a ride and a driver accepts. While the driver is en route, the passenger attempts to cancel. In the procedural codebase, three different service functions — `CancellationService`, `NotificationService`, and `FareService` — each reach directly into the `Trip` struct to read and compare `status`. When a race condition under concurrent load corrupts the field, the bug trace spans three files and pulls in four engineers to determine which write landed last. In the OOP design, `Trip.cancelTrip()` is the single method that reads, validates, and writes `status`. All three service functions call it. A `TripException` is thrown if the cancel violates a business rule (trip is already `IN_PROGRESS`); the caller handles that exception at its own boundary. When the same concurrency bug surfaces, the trace ends in one method in one class. The application runs stateless across 15 backend servers; any server can receive the cancel request. The `Trip` entity persisted in the shared database is the single source of truth, and its method contracts prevent concurrent writes from producing incoherent state.

## Practice Loop
1. Write down what data a `Trip` holds (passenger ID, driver ID, source, destination, current status, fare) and what actions it must support (`acceptTrip`, `cancelTrip`, `markArrived`, `complete`).
2. Sketch a procedural version with public struct fields and standalone functions modifying fields directly.
3. Count your blast radius: inspect every line across service functions, HTTP handlers, and helpers reading or writing `trip.status` directly.
4. Refactor into OOP: move state and behaviour into a `Trip` class, make fields private, and enforce state transition invariants internally.
5. Verify encapsulation: ensure internal representation changes (like switching status from String to enum) require zero caller modifications.

## Evidence of Understanding
You can explain why scaling a team on procedural code becomes exponentially harder as the codebase grows — any function can modify any entity's state, so there is no single authoritative location for business rules — and you can design a `Trip` entity that consolidates state ownership and enforces invariants through method contracts. You can demonstrate the difference by refactoring the same scenario from procedural to OOP, showing that the OOP version requires checking exactly one class for trip-state bugs. You can identify an Anemic Domain Model in a Spring codebase — a class with only getters/setters and a Service class holding all logic — and articulate why it recreates the procedural problem in Java syntax.

## Suggested Extension
Add a `Discount` entity and a method `applyDiscount(Discount d)` to `Trip` that applies a discount code only if the trip is still in `REQUESTED` state and the discount has not already been applied. Ensure discount validation logic stays in `Discount`, fare recalculation stays in `Trip`, and neither class leaks internal representation across the boundary.
",
            "02-oop-1-intro-lab" or "02-oop-classes-objects" => @"# Lesson 2 — OOP-1: Classes, Objects & Encapsulation

## Concepts Covered

Abstraction is the overarching principle of OOP — the idea that a complex system is best understood as a set of clearly-bounded ideas working together. Encapsulation, inheritance, and polymorphism are the three mechanisms that implement it. A **class** is a template: it defines the fields an object will carry and the methods it exposes. The class definition occupies minimal JVM memory (bytecode only) and creates no object at runtime. Every call to `new Driver(...)` allocates a distinct **object** on the **heap** — the JVM memory region for dynamically allocated instances — and initializes each field independently. A reference variable on the stack (`Driver d1`) holds the heap address, not the object itself. Assigning `Driver d2 = d1` copies that address; both variables now point at the same heap allocation. `d2.name = ""Suresh""` modifies the single shared object, and `d1.name` returns ""Suresh"" afterwards. Two independent Driver objects require two separate `new` calls.

Java initializes unassigned instance fields to zero-equivalents — reference types to `null`, numerics to `0`, booleans to `false` — so a `Driver` created with `new Driver()` and no constructor body has `name = null` and `rating = 0.0`. Constructors replace those defaults with real values; the `this` keyword distinguishes an instance field from a same-named parameter. Without it, `name = name` in a constructor is a no-op: the parameter is assigned to itself, the field stays `null`, and the compiler raises no warning. The `static` keyword marks class-level members shared across every instance — a `totalDrivers` counter that tracks how many Driver objects exist belongs on the class, not on each driver; making it an instance field means every driver holds its own counter starting at zero, which is nonsensical. **Encapsulation** serves two jobs: bundling state and behaviour inside a class, and protecting that state by making fields `private` and routing all changes through methods that enforce business rules. With public fields, any caller anywhere can write `driver.rating = 10.0`, bypassing every validation the team ever agreed on; private fields close that door at compile time:

```java
// Without encapsulation — invalid state compiles silently
public double rating;
driver.rating = 10.0;  // Uber max is 5.0 — no error

// With encapsulation — the rule lives in exactly one place
private double rating;

public void setRating(double newRating) {
    if (newRating < 1.0 || newRating > 5.0) {
        throw new IllegalArgumentException(
            ""Rating must be between 1.0 and 5.0, got: "" + newRating);
    }
    this.rating = newRating;
}
```

## Practical Backend Scenario

A `FareBoostService` computes dynamic fare multipliers based on driver ratings. In the unencapsulated `Driver` class, `rating` is a public field. A junior engineer writing a test fixture types `driver.rating = 10.0` to simulate a high-rated driver, commits the fixture, and the corrupt value reaches the staging database. Every trip processed by that driver in staging now carries an inflated multiplier, and the regression surfaces only when fare totals look wrong in a dashboard review. In the encapsulated design, `Driver.rating` is `private`; `setRating(double r)` throws `IllegalArgumentException` for any value outside `[1.0, 5.0]`. The test fixture doesn't compile until the engineer supplies a valid rating. The `FareBoostService` reads the value through `driver.getRating()` and has no path to write it directly. When a rating bug does surface in production, the entire blame radius is one method in one class — not a search across every service that ever touched the public field.

## Practice Loop

1. List the `Driver` class fields (`name`, `driverId`, `rating`, `isOnline`, `phoneNumber`) and the operations it must support (`goOnline`, `goOffline`, `acceptRide`, `setRating`, `getRating`, `maskPhoneNumber`) on paper, without any code — you are naming the entity's responsibility boundary before a single line is written.
2. Write the bare class with `public` fields and no methods; from a separate `Main` class, set `driver.rating = 10.0` and `driver.rating = -3.0` — observe that both compile and execute without error.
3. Count every line in your codebase that reads or writes `driver.rating` directly and write down the total. That count is your blast radius: every one of those sites must be audited when an incorrect rating surfaces in production.
4. Add the `private` modifier to `rating`; add `setRating(double r)` with the 1.0–5.0 guard; recompile — observe that every direct field write in step 2 now fails at compile time, forcing all callers through the validated method.
5. Add `private static int totalDrivers = 0;` to the class, increment it inside the constructor with `totalDrivers++`, and add `public static int getTotalDrivers()`. Create three separate Driver objects and call `Driver.getTotalDrivers()` — verify the counter reflects the total across all instances, not a per-object value of 1.

## Evidence of Understanding

You can explain why `Driver d2 = d1` creates no new object and predict that `d2.name = ""Suresh""` changes what `d1.name` returns, because both variables hold the same heap address. You can write a `Driver` constructor using `this` to disambiguate field names from parameters and demonstrate that omitting `this` causes fields to silently retain their default values. You can explain the difference between a static field and an instance field by showing that `Driver.totalDrivers` increments with each constructor call while `d1.rating` and `d2.rating` are independent — and you can articulate why making a shared counter an instance field is a design error, not just a style one. You can build a `Driver` class with private fields and a `setRating()` method that rejects invalid values with a descriptive exception, and you can demonstrate that the resulting design eliminates the compile-time path for a `FareBoostService` to corrupt a driver's rating.

## Suggested Extension

Add a `maskPhoneNumber()` method to `Driver` that returns a `String` in the format `+91 XXXXX XX234` — exposing only the last three digits of the subscriber number. Verify that `phoneNumber` is `private`, that no getter returns the raw number, and that the masking logic lives entirely inside `Driver`. The caller that needs the display string receives it in one call without knowing the internal format or length.

---

Reference: Lecture material — ""OOP-1: Classes, Objects & Encapsulation"" (Scaler, June 2026)
",
            "03-oop-2-access-modifiers-encapsulation" or "03-oop2-encapsulation-inheritance" => @"# Lesson 3 — OOP-2: Encapsulation Complete, Copy Semantics & Inheritance

## Concepts Covered

Access modifiers form the outer visibility boundary of encapsulation. The four tiers — `private` (declaring class only), default/package-private (same package, no keyword), `protected` (same package and subclasses across any package), and `public` (unrestricted) — impose a graduated perimeter that controls which callers can reach which state. The design discipline is to grant the minimum required visibility: a field that serves only its own class has no reason to be package-private, and a method intended for subclass specialization has no reason to be public. The `final` keyword adds a second enforcement axis orthogonal to visibility: a `final` field cannot be reassigned after the constructor completes (the compiler treats any subsequent assignment as an error), a `final` method cannot be overridden by a subclass even when it is `public`, and a `final` class cannot be extended at all. Combining these produces the immutability pattern: declare the class `final`, make every field `private final`, provide getters and computed results but no setters, and perform defensive copies on any mutable objects passed in as constructor arguments. An immutable `Fare` class is the canonical example — once a surge multiplier of 1.2x is locked in at trip-acceptance time, no downstream repricing service can silently alter it because `setMultiplier()` simply does not exist on the type. Any renegotiated fare requires constructing a new `Fare` object, leaving the accepted original untouched. Constructor chaining via `this(...)` keeps initialization DRY within this sealed structure: a `Driver` class may expose a full four-argument constructor, a two-argument partial constructor, and a no-arg default, but all three must route through the master constructor that increments `totalRegisteredDrivers++`. Without chaining, each overload carries its own copy of that bookkeeping, and a future change — adding a secondary metric, say — has to be applied across every branch. The rule is absolute: `this(...)` must be the very first statement in a constructor body, and it is mutually exclusive with `super(...)` in the same constructor, because both demand the first slot.

Copy semantics address a failure mode that access modifiers alone cannot close. When an object holds a reference to a mutable inner object, assigning that reference during copy construction creates an alias — not a copy. Two `Trip` instances that both hold `this.route = other.route` share a single `Route` heap object; a call to `tripCopy.getRoute().setSource(""Whitefield"")` silently rewrites the source on `originalTrip` as well, because both variables reach the same memory address. A deep copy constructor fixes this by allocating a fresh inner object with the same values: `this.route = new Route(other.route)`. The decision rule is crisp: if the nested object is immutable — a `String`, a `Fare`, or any properly sealed class — sharing its reference is safe and memory-efficient because no caller can mutate the shared value; if it is mutable, deep copying is mandatory for isolation. This distinction is not merely theoretical: shallow aliasing is one of the most common root causes of state-corruption bugs in multi-threaded Java services, where two threads operate on what they believe are independent entities that are actually one. Inheritance layers on top of sealed structure through the `extends` keyword. An abstract `Vehicle` parent declares shared fields (`vehicleId`, `licensePlate`, `capacity`) and an abstract `calculateFare(double distanceKm)` method; `Car`, `Auto`, and `Bike` each call `super(vehicleId, licensePlate, capacity)` to delegate shared initialization and override only what differs — their per-km rate and fare formula. Every class in Java implicitly extends `java.lang.Object`, which supplies a default `equals()` that compares references (identity, not value equality) and a default `hashCode()` derived from the object's memory address. The contract between them is strict: if `a.equals(b)` returns `true`, then `a.hashCode()` must equal `b.hashCode()`. Overriding only `equals()` breaks this contract. Two `Trip` objects with the same `tripId` that are logically equal produce different hash codes under the default implementation; `HashSet` computes the bucket from the hash first, never reaching `equals()` to compare them, and stores both as distinct entries — a silent deduplication failure in a collection you expected to hold unique trips.

```java
// Shallow Copy — reference assignment. One Route object lives in heap memory;
// both tripA and tripCopy point to it. Mutating one corrupts the other.
public Trip(Trip other) {
    this.tripId     = other.tripId;
    this.fareAmount = other.fareAmount;
    this.route      = other.route;           // aliased reference, not a copy
}

// Deep Copy — a fresh Route is constructed with the same field values.
// tripA.route and tripCopy.route are independent heap objects.
public Trip(Trip other) {
    this.tripId     = other.tripId;
    this.fareAmount = other.fareAmount;
    this.route      = new Route(other.route); // independent heap object
}
```

## Practical Backend Scenario

A ride dispatch service manages `Trip` entities, each carrying a mutable `Route` that the system can update mid-trip for traffic rerouting or pickup-point corrections. When a driver is reassigned mid-trip, the dispatcher archives the pre-reassignment `Trip` to preserve the audit trail for dispute resolution. Without a deep copy constructor, the archived instance shares the `Route` reference with the live trip — rerouting the live trip's source address for the new pickup also silently rewrites the archived record, making the pre-reassignment state unrecoverable. The `Fare` attached to each `Trip` is an immutable value object: once set at 1.2x surge at acceptance time, no repricing thread can mutate it; any updated fare creates a new `Fare` instance, while the fare stored in the archived trip remains exactly what the driver accepted and what the audit record must show.

## Practice Loop

1. Implement `Fare` as a fully immutable value object: declare the class `final`, mark all fields `private final` (base fare and surge multiplier), provide only getters and a `getFinalFare()` computed result, and write no setters — verify the compiler rejects any attempt to reassign a field after the constructor completes.
2. Implement `Route` (mutable: source and destination settable) and `Trip` (holds a `Route` and a `Fare`). Write a shallow copy constructor for `Trip` using direct reference assignment for the `route` field, then write a unit test that modifies the copy's route source and asserts the original is unchanged — confirm the assertion fails, proving aliasing.
3. Count every call site outside `Trip` that reaches `route.setSource()` or `route.setDestination()` on the inner field. Each is a line of code that can corrupt the original through the aliased copy. Replace the shallow assignment with `this.route = new Route(other.route)` and re-run the test; confirm the assertion now passes.
4. Add an abstract `Vehicle` class with `protected` fields `vehicleId`, `licensePlate`, and `capacity`, and an abstract `calculateFare(double distanceKm)` method. Implement `Car` (15.0 per km) and `Auto` (10.0 per km), each calling `super(vehicleId, licensePlate, capacity)` from their constructor and providing a concrete fare override.
5. Override `equals()` and `hashCode()` on `Trip` using `tripId` as the identity field. Add two `Trip` objects with the same `tripId` to a `HashSet<Trip>` and assert the set size is 1. Then remove only the `hashCode()` override, re-run, and observe the size become 2 — confirming that `equals()` without `hashCode()` leaves the contract broken.

## Evidence of Understanding

You can explain why `private final` fields alone are insufficient for immutability — a non-`final` class can be subclassed, and the subclass can introduce setters that expose the parent's state through the child's type. You can trace heap state after a shallow copy to show that two object references point to the same inner object, then demonstrate in a test that a deep copy constructor eliminates the aliasing. You can build a two-level vehicle hierarchy using `extends` and `super()`, override `calculateFare` in each subclass, and confirm that a polymorphic collection of `Vehicle` references dispatches to the correct implementation at runtime. You can break the `equals`/`hashCode` contract deliberately — overriding only `equals` — and show the resulting `HashSet` duplication that makes the violation concrete.

## Suggested Extension

Add a `TripArchiveService` backed by a `HashMap<String, Trip>` that stores deep copies of trips at dispatch time. Write a test that reroutes the live trip's source address after archiving, then retrieves the archived trip by `tripId` and confirms its route still holds the original source — verifying deep copy isolation and the `equals`/`hashCode` contract in a single, integrated scenario.

---

Reference: Effective Java, 3rd ed., Joshua Bloch — Items 10 (equals), 11 (hashCode), 17 (Minimize mutability)
",
            "04-oop-3-polymorphism-interfaces" => @"# Lesson 4 — OOP-3: Polymorphism, Abstract Classes & Interfaces

## Concepts Covered

Polymorphism originates from the Greek roots *poly* (multiple) and *morph* (form): the core object-oriented principle where a single entity, interface, or method call can take on multiple concrete forms at runtime and compile time. Without polymorphism, software systems become rigid and brittle — adding a new vehicle type or payment gateway would require modifying and rewriting dispatch logic across every calling service.

Object-oriented polymorphism divides into two primary mechanisms:
1. **Runtime Polymorphism (Dynamic Dispatch):** Implemented via **method overriding**, where a subclass provides its own specific implementation of a method declared in its parent class. Dynamic dispatch is governed by a fundamental dual-perspective rule:
   - **Reference type** $\rightarrow$ determines which methods you **CAN** call (enforced strictly by the compiler at compile time).
   - **Actual object type** $\rightarrow$ determines which implementation **RUNS** (dispatched dynamically by the JVM at runtime).
   When `Vehicle v = new Cab(); v.calculateFare();` executes, the compiler verifies that `Vehicle` declares `calculateFare()`, but the JVM dispatches execution to `Cab.calculateFare()`.
2. **Compile-Time Polymorphism (Static Resolution):** Implemented via **method overloading**, where multiple methods in the same class share the exact same method name but differ in their parameter signatures (parameter count, parameter types, or parameter order). The compiler resolves the exact method to invoke before execution. Return type alone, access modifiers, or variable parameter names cannot differentiate overloads because the compiler cannot resolve call sites based on discarded return values. Static methods can be overloaded, but cannot be overridden (they are hidden). Operator overloading is not supported in Java.

**Abstraction as Code:**
The `abstract` keyword represents an idea, concept, or blueprint rather than a concrete instance. A generic base class like `Vehicle` represents a thought; concrete entities like `Cab`, `Auto`, and `Bike` represent physical vehicles. Declaring `public abstract class Vehicle` prevents direct instantiation (`new Vehicle()` is a compile-time error) while enforcing implementation obligations on subclasses through abstract methods such as `public abstract double getBaseFare();`.

**The Diamond Problem & Interfaces:**
Multiple class inheritance creates structural ambiguity when two parent classes (`A` and `B`) extend a common base class and override the same method — a child class `C` inheriting from both cannot determine which parent implementation to execute. Java solves this by prohibiting multiple class inheritance, using `interface` instead. An interface is a pure capability contract across unrelated class hierarchies (`class C implements A, B`). Interface fields are implicitly `public static final`, and methods define capability contracts (expanded to include `default` methods in Java 8+).

**Composition vs. Inheritance — The Three-Question Design Test:**
Inheritance couples classes tightly. The decision framework for choosing the correct design tool is:

| Relationship Type | Question | Tool |
|---|---|---|
| IS A TYPE OF | Does X inherit structural identity and shared mechanics from Y? | `extends` / abstract class |
| CAN DO | Does X possess capability Y across unrelated class families? | `implements` / interface |
| HAS A | Does X contain Y as an internal collaborator or component? | composition / private field |

## Practical Backend Scenario

A ride-hailing dispatch fleet service manages multimodal transport options across a metropolitan network. The system defines an abstract base class `Vehicle` that encapsulates shared state (`vehicleId`, `driverName`) and exposes a template method `calculateFare(int distanceKm) { return distanceKm * getBaseFare(); }` with an abstract `getBaseFare()`. Subclasses specialize only their per-kilometer pricing: `Cab` returns 15.0, `Auto` returns 10.0, and `Bike` returns 5.0.

The dispatch service layer `CabBookingService` overloads `bookRide()` to support multiple client workflows: `bookRide(String pickup, String drop)`, `bookRide(String pickup, String drop, int rideTimeMinutes)`, and `bookRide(String pickup, String drop, int rideTimeMinutes, Coupon coupon)`. When dispatching a trip, the fleet orchestrator iterates over a polymorphic `List<Vehicle> fleet`. Calling `v.calculateFare(distanceKm)` dynamically executes each vehicle's specialized rate without any `instanceof` inspection. Payment processing is decoupled using a `PaymentGateway` interface (`CAN DO`), allowing `RazorpayAdapter` or `StripeAdapter` to be composed into the booking workflow (`HAS A`).

## Practice Loop

1. Write an abstract `Vehicle` class with private fields (`vehicleId`, `driverName`), a concrete `calculateFare(int km)` method, and an abstract `getBaseFare()` method.
2. Create concrete subclasses `Cab`, `Auto`, and `Bike` extending `Vehicle`, implementing `getBaseFare()` and adding `@Override` annotations.
3. Implement `CabBookingService` with overloaded `bookRide()` methods demonstrating parameter count and type variations.
4. Construct a `List<Vehicle>` containing a `Cab`, `Auto`, and `Bike`; iterate through the collection and invoke `calculateFare(10)`, observing dynamic method dispatch at runtime.
5. Create a `PaymentGateway` interface (`CAN DO`) with `processPayment(double amount)` and compose it as a private field (`HAS A`) inside `CabBookingService`, verifying that payment changes require zero modifications to the vehicle hierarchy.

## Evidence of Understanding

You can articulate the dual-perspective rule of polymorphism — reference type governs compile-time method accessibility while actual heap type governs runtime execution. You can explain why return types cannot differentiate overloaded methods, demonstrate how abstract classes enforce subclass obligations, and explain how interfaces prevent the Diamond Problem. You can apply the Three-Question Design Test to justify choosing composition over inheritance.

## Suggested Extension

Add a `Rentable` capability interface with `rent(int hours)` and attach it to both `LuxuryCab` and an unrelated `OfficeSpace` class. Demonstrate that client code can process a `List<Rentable>` polymorphically across completely disjoint class hierarchies.
",
            "05-oop-4-lms-lab" => @"# Lesson 5 — OOP-4: Library Management System Lab

## Concepts Covered

This lab synthesizes all four core pillars of Object-Oriented Programming — **Encapsulation**, **Abstraction**, **Inheritance**, and **Polymorphism** — by constructing a comprehensive Library Management System (LMS) from scratch.

**1. Abstraction & System Blueprinting:**
Abstraction models complex systems as interacting, bounded entities while hiding implementation mechanics. In the LMS architecture, abstraction operates across two distinct constructs:
- **Abstract Classes:** `User` and `Book` serve as abstract base blueprints that cannot be instantiated directly. They define shared state and contract obligations for concrete specializations.
- **Interfaces:** `Lendable` serves as a pure capability contract (`lend`, `returnItem`, `isAvailable`) that attaches lending behavior across disparate entity hierarchies without imposing an unnatural inheritance tree.

**2. Inheritance & Constructor Chaining:**
Inheritance shares structural identity across the domain (`Member IS-A User`, `Librarian IS-A User`). When a subclass object is instantiated (`new Member(""Asha"", ""asha@email.com"")`), Java enforces strict constructor ordering:
1. `Member` constructor is invoked.
2. `super(...)` passes execution immediately to `User`.
3. `User` initializes shared identity fields, generates a unique ID, and increments `totalUsers`.
4. Control returns to `Member` for subclass-specific field initialization.

**3. Class-Level Rules with `static` and `final`:**
- `static` fields (`idCounter`, `totalUsers`) belong to the class itself, maintaining a single shared copy in memory across all instances. `getTotalUsers()` is a `static` method callable on `User` directly.
- `final` instance fields (`final String userId`) are assigned exactly once during constructor execution and cannot be reassigned afterwards.
- `static final` constants (`static final int MAX_BORROW_LIMIT = 5`) define immutable, class-wide policy constants.

**4. The Three Constructor Types & Copy Semantics:**
- **Default Constructor:** Initializes objects with safe, deterministic initial values.
- **Parameterized Constructor:** Provides complete field initialization at creation time.
- **Copy Constructor:** Creates an independent object cloned from an existing instance. In the LMS, a copied user invokes `generateUniqueId()` and increments `totalUsers` rather than copying `other.userId` directly, preserving the strict invariant that all users possess distinct IDs. Similarly, a copied book resets `isAvailable = true`.

**5. Polymorphic Execution Without `instanceof`:**
In `Book.lend(User user)`, the method executes:
```java
if (isAvailable && user.canBorrowBooks()) {
    isAvailable = false;
    return true;
}
```
`user.canBorrowBooks()` executes polymorphically: for a `Member`, it checks `borrowedBooksCount < MAX_BORROW_LIMIT`; for a `Librarian`, it returns `true` unconditionally. No `instanceof` type checks are required.

**6. The Access Modifiers Table (Why Every LMS Field Is `private`):**
| Modifier | Same Class | Same Package | Subclass | Everywhere |
|----------|------------|--------------|----------|------------|
| `private` | yes | no | no | no |
| default | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

Every entity field in the LMS (`userId`, `borrowedBooksCount`, `isAvailable`) stays
`private`, with access only through public getters and controlled mutator methods. This is
why `Member.borrowedBooksCount` cannot be touched directly by `Book.lend()` — the two
classes are not in an inheritance relationship, so `protected` would not even help; the
field must go through `Member`'s own public methods.

**7. Why `Book.lend()` Never Calls `incrementBorrowCount()` Directly:**
`LibraryManagementSystem.lendBook()` delegates in two separate steps: first `book.lend(member)`,
then — only if that succeeded — `member.incrementBorrowCount()`. `Book.lend()` itself never
calls `incrementBorrowCount()`. This separation is deliberate: a `Book` should not need to
know how a `Member` tracks its own borrow count internally, and a `Member`'s counting logic
should not need to know how a `Book` decides availability. Each class stays responsible for
exactly one piece of state, and the orchestrator (`LibraryManagementSystem`) is the only
place that knows both steps must happen together.

**8. The IS-A Test for This Domain:**
Every inheritance relationship in the LMS should pass a simple intuition check: does
""Child IS-A Parent"" read naturally as a sentence? ""Member IS-A User"" and ""Librarian IS-A
User"" both read naturally, confirming `extends` is the right tool. If a relationship does
not read naturally as IS-A, composition (a field reference) is the correct choice instead,
not inheritance.

## Practical Backend Scenario

The Library Management System is structured across three core progressive milestones:

**Milestone 1 — User Hierarchy & Identity Management:**
Implement abstract base class `User` with private fields (`userId`, `name`, `contactInfo`), a `static int idCounter`, and a `static int totalUsers`. Implement constructor chaining across default, parameterized, and copy constructors. Implement `Member` with private `borrowedBooksCount`, `static final int MAX_BORROW_LIMIT = 5`, and concrete `canBorrowBooks()`. Implement `Librarian` with unrestricted borrowing privileges.

**Milestone 2 — Lending Architecture & Capability Attachment:**
Define the `Lendable` interface declaring `boolean lend(User user)`, `void returnItem(User user)`, and `boolean isAvailable()`. Implement abstract base `Book` implementing `Lendable`, encapsulating private fields (`bookId`, `title`, `author`, `isAvailable`). Create concrete subclasses `TextBook` (with subject/edition fields) and `NovelBook` (with genre fields) overriding `displayBookDetails()`. Non-lendable reference items (`Journal`, `Encyclopedia`) extend `Book` but do not implement `Lendable` (or throw unsupported operation exceptions), maintaining clean separation between what an item IS versus what it CAN DO.

**Milestone 3 — Full Management System Coordination:**
Build the central orchestrator `LibraryManagementSystem` managing `List<Book>` and `List<User>`. Implement methods for `registerUser(User u)`, `addBook(Book b)`, `lendBook(String bookId, String userId)`, and `returnBook(String bookId, String userId)`. Implement overloaded book search methods: `searchBooks(String titleQuery)` and `searchBooks(String titleQuery, String itemType)`. Implement `displayRegisteredUsers()` iterating polymorphically over `List<User>` and invoking `u.displayDashboard()`.

## Practice Loop

1. Build Milestone 1: Create `User`, `Member`, and `Librarian`. Verify that creating three users and one copied member increments `User.getTotalUsers()` to 4 and assigns 4 distinct unique IDs.
2. Build Milestone 2: Define `Lendable`, `Book`, `TextBook`, and `NovelBook`. Verify `TextBook` and `NovelBook` inherit lending logic and implement specific details.
3. Build Milestone 3: Implement `LibraryManagementSystem` coordinating user registration, catalog storage, and borrowing transactions.
4. Test borrowing invariants: Register a `Member`, borrow 5 books successfully, and assert that the 6th borrow attempt fails. Register a `Librarian` and assert that borrowing beyond 5 succeeds.
5. Test encapsulation boundaries: Ensure `Member.borrowedBooksCount` cannot be mutated directly by `Book.lend()`, but only through controlled helper methods `incrementBorrowCount()` and `decrementBorrowCount()`.
6. Trace this exact sequence and predict how many `User` objects exist and how many unique
   IDs are generated:
   ```java
   Member asha = new Member(""Asha"", ""asha@email.com"");
   User copy = new Member(asha);
   System.out.println(asha.getUserId().equals(copy.getUserId()));
   ```
   (Two independent `Member` objects exist; the copy constructor must call
   `generateUniqueId()` rather than copying `asha`'s ID, so the printed result is `false`.)

## Evidence of Understanding

You can explain why `User` and `Book` are abstract classes, why copy constructors must generate fresh unique IDs and increment static instance counters, how `Book.lend()` relies on runtime polymorphism rather than `instanceof` checks, and how interfaces attach capabilities across class hierarchies without forcing unrelated entities into an artificial inheritance tree.

## Suggested Extension

Add a `FinePolicy` strategy interface (`calculateFine(int overdueDays)`) with `StandardFinePolicy` (\$1/day) and `PremiumMemberFinePolicy` (first 3 days free), injecting the appropriate policy into `Member` at registration time.
",
            "06-concurrency-1-threads" => @"# Lesson 6 — Concurrency 1: Processes, Threads & Context Switching

## Concepts Covered

Concurrent software execution requires understanding how operating systems allocate processing resources and memory at runtime.

**The Office / Company Metaphor:**
A running system is analogous to an office environment:
- **Company = Process:** A self-contained running program allocated its own physical floor space, address space in RAM, and OS resources.
- **Employees = Threads:** Lightweight execution units operating inside the process. Each employee has their own private notepad (Call Stack) and task bookmark (Program Counter), but all employees share the office desks, filing cabinets, and whiteboard (Heap Memory).
- **Managers = CPU Scheduler:** The decision-maker determining which employee works at a physical desk during each time slice.
- **Desks = CPU Cores:** The physical processing hardware where instructions actively advance.

**Diagnostic Questions — Concurrency vs. Parallelism:**
- *How many tasks are partially done simultaneously?*
- *How many tasks actively advance right now?*
- **Concurrency (Managing Many Things at Once):** A single-core CPU executing multiple tasks via rapid time-slicing. Multiple tasks are in various stages of completion, but only one task actively advances at any given instant.
- **Parallelism (Doing Many Things at Once):** Multi-core hardware running multiple tasks simultaneously. Multiple tasks are partially done AND multiple tasks actively advance at the exact same physical moment across separate cores.

**Five Real-World Anchors for the Office Metaphor (from class):**
- **Process = browser tabs:** modern browsers run separate tabs in separate processes; one
  tab crashing does not take down the others, because each has its own isolated memory space.
- **Thread = a video game's internal workers:** one thread renders graphics, a second
  manages audio, a third reads controller input, and a fourth autosaves progress — all four
  share the same game state in memory but run independently.
- **CPU Scheduler = a web server under load:** when incoming requests outnumber the
  server's processing capacity, the scheduler decides execution order so no request starves
  while avoiding excessive switching overhead.
- **Context Switching = losing your place while studying:** pausing one subject to
  context-switch to another and back costs real time re-orienting yourself — time spent on
  logistics, not on the actual work. A CPU pays the same cost saving and restoring register
  state on every thread switch.
- **Runnable = handing off a written task:** a scheduled report defines *what* needs doing
  without specifying *which* employee performs it — exactly like handing a task description
  to whichever thread the scheduler assigns next.

**From Code to Process in Memory:**
- Source code $\rightarrow$ Compiled into an Executable on Disk (Program) $\rightarrow$ Loaded into RAM upon execution (Process).
- The OS tracks each process using a **Process Control Block (PCB)**, which stores `ProcessID`, `ProcessName`, `State` (Ready, Running, Blocked), `ExecutionTime`, `MemoryLimit`, `ResourcesAllocated`, and `LastLineExecuted` / register snapshots.
- Processes execute in isolated memory spaces; inter-process communication (IPC) requires heavy operating-system mechanisms.

**Threads — Lightweight Execution Units:**
- A **Thread** is the smallest unit of execution scheduled by the CPU.
- Every thread within a process owns an independent **Call Stack** (local variables, method frames) and **Program Counter (PC)**.
- All threads in the same process share the common **Heap**, static memory, and file descriptors. Communication between threads is instant via shared memory, but requires synchronization to prevent corruption.

**Context Switching & Scheduling Overhead:**
- When the CPU switches execution from Thread 1 to Thread 2, it saves Thread 1's register state, program counter, and stack pointer, and loads Thread 2's context.
- Context switching consumes CPU cycles and causes CPU cache line invalidation (cache thrashing). Excessive thread creation degrades throughput because the CPU spends more time switching contexts than executing application logic.

**Standard Operating Procedure (SOP) for Multithreading in Java:**
1. *Think in terms of tasks to be completed in parallel, not raw threads.*
2. Create a dedicated task class implementing the `Runnable` functional interface.
3. Place execution logic inside the `public void run()` method.
4. Pass required parameters to the task object via its constructor.
5. Pass the task object to a new `Thread` instance: `Thread t = new Thread(task);`.
6. Invoke `t.start()`. *Critical rule:* Calling `t.run()` executes the method synchronously on the current thread without spawning a new execution thread. Calling `t.start()` registers the thread with the JVM/OS scheduler to begin concurrent execution.
7. Recognize that thread execution order is **non-deterministic** — the CPU scheduler controls thread execution timing.

## Practical Backend Scenario

A collaborative document processing engine (such as Google Docs or MS Word) runs as a single application process in RAM. Within this process, multiple concurrent threads operate over the shared in-memory document model:
- **Thread 1 (UI & Event Handling):** Captures real-time keyboard inputs, mouse clicks, and renders updates to the display buffer.
- **Thread 2 (Background Autosave):** Periodically serializes document state and flushes changes to persistent cloud storage every 30 seconds.
- **Thread 3 (Spell & Grammar Checking):** Tokenizes text in the background, cross-referencing dictionaries and grammar models without interrupting the user.
- **Thread 4 (Real-time Collaboration Sync):** Listens on WebSockets for incoming remote edits from other collaborators.

All threads share heap memory, allowing instant visibility of text buffer edits, while maintaining independent call stacks so that an I/O pause during cloud autosave never freezes the interactive UI thread.

## Practice Loop

1. Write a `NumberPrinterTask` implementing `Runnable` that takes an integer `number` via constructor and prints `number` along with `Thread.currentThread().getName()`.
2. In `main()`, spawn 10 threads running `NumberPrinterTask` for numbers 1 through 10 using `new Thread(task).start()`; run the program 5 times and observe the non-deterministic output sequence.
3. Replace `t.start()` with `t.run()` in the loop; observe that execution becomes strictly sequential (1..10) on the `main` thread, demonstrating that `run()` bypasses thread creation.
4. Implement a background `AutosaveTask` with a `while(true)` loop containing `Thread.sleep(2000)` and a print statement; run it concurrently alongside a main loop reading user input from `Scanner`.
5. Use an OS process monitor (`Task Manager`, `Activity Monitor`, or `jconsole`) to inspect live thread counts and CPU utilization while varying the number of active worker threads.

## Evidence of Understanding

You can map the office metaphor to processes, threads, CPU schedulers, and cores. You can distinguish concurrency from parallelism using the two diagnostic questions. You can detail which memory segments are private to a thread (Stack, PC) versus shared across threads (Heap), explain context switching overhead, and demonstrate the mandatory SOP for creating and starting Java threads with `Runnable` and `start()`.

## Suggested Extension

Build a concurrent word frequency counter where a large text document is divided into 4 distinct text chunks, each processed by a separate `ChunkWordCounter` thread implementing `Runnable`, aggregating partial word counts into a shared reporting data structure.
",
            "07-concurrency-2-executors" => @"# Lesson 7 — Concurrency 2: Executors, Thread Pools & Callable/Future

## Concepts Covered

Creating raw threads on demand introduces severe scalability bottlenecks in production systems.

**The Too-Many-Threads Problem:**
- Creating a new `Thread` object for every task requires allocating ~1MB of stack memory and making operating system system calls.
- If a server receives 10,000 requests and spawns 10,000 threads, the operating system exhausts RAM and enters severe CPU context-switching thrashing, where CPU cores spend all their time saving and restoring thread states rather than executing application code.
- Threads that finish short tasks immediately die, wasting the resource investment of creating them.

**The TATA Motor Production Line Analogy:**
To manufacture 1,000 cars in a day, TATA Motors does not build 1,000 distinct production assembly lines and demolish each after assembling a single vehicle. Instead, the plant maintains a fixed, reusable set of production lines (e.g. 5 lines). As 1,000 car assembly orders arrive, they enter a waiting queue. Line 1 picks up order 1, completes it, and immediately pulls the next waiting order from the queue.
A **Thread Pool** operates on this exact principle: a bounded roster of pre-allocated worker threads continuously pulls tasks from an internal thread-safe blocking queue, eliminating per-task creation costs and capping resource consumption.

**The Executor Framework Architecture:**
- `Executor`: Root interface declaring `void execute(Runnable command)` to decouple task submission from execution mechanics.
- `ExecutorService`: Sub-interface managing pool lifecycle, batching, and returning `Future` handles for asynchronous computation.
- `Executors`: Factory utility class providing pre-configured thread pool implementations:
  - `Executors.newFixedThreadPool(int nThreads)`: Creates a pool with an exact, unchanging number of worker threads and an unbounded internal queue (`LinkedBlockingQueue`). Excess tasks wait in the queue until a worker becomes free.
  - `Executors.newCachedThreadPool()`: Creates an elastic pool that creates new threads on demand for bursts of work and terminates idle threads (after 60 seconds). *Risk:* Under sustained heavy load, it can spawn unbounded threads and crash system memory.

**Returning Results with `Callable<V>` and `Future<V>`:**
- `Runnable.run()` returns `void` and cannot throw checked exceptions, preventing tasks from returning computed values to the caller.
- `Callable<V>` functional interface declares `V call() throws Exception`, allowing tasks to return typed values and propagate checked exceptions.
- `Future<V>` acts as an asynchronous claim ticket (claim slip / dry-cleaning ticket) representing the eventual result of the computation.
- `Future.get()` blocks the calling thread until the worker completes the task, returning the computed value or throwing an `ExecutionException` wrapping any task error.

**The Submit-First / Collect-Last Pattern:**
A critical bug in concurrent code is calling `.get()` immediately after submitting each individual task:
```java
// WRONG — Silently serializes execution
int a = pool.submit(taskA).get();
int b = pool.submit(taskB).get();

// RIGHT — Genuine parallel execution
Future<Integer> fa = pool.submit(taskA);
Future<Integer> fb = pool.submit(taskB);
int total = fa.get() + fb.get();
```
*Rule:* Submit all tasks first so the pool can execute them concurrently, and collect results via `.get()` only after all tasks are in flight.

**Executor Lifecycle Management:**
Worker threads in a thread pool stay alive waiting for new tasks. Without explicit shutdown, the JVM process will never terminate even after `main()` finishes.
- `pool.shutdown()`: Orderly shutdown — stops accepting new tasks, completes all currently queued/running tasks, then terminates. Non-blocking.
- `pool.shutdownNow()`: Attempts immediate stop — cancels queued tasks and interrupts running workers.
- `pool.awaitTermination(timeout, unit)`: Blocks the caller until all tasks complete or the timeout elapses.

**Multithreaded Merge Sort (Parallel Decomposition):**
Merge Sort recursively decomposes an unsorted list into independent left and right halves that never touch each other's data:
1. Split list into `left` and `right`.
2. Create `MergeSortTask` implementing `Callable<List<Integer>>`.
3. Submit both subtasks to a **single shared `ExecutorService`**:
   ```java
   Future<List<Integer>> leftFuture = pool.submit(new MergeSortTask(left, pool));
   Future<List<Integer>> rightFuture = pool.submit(new MergeSortTask(right, pool));
   List<Integer> sortedLeft = leftFuture.get();
   List<Integer> sortedRight = rightFuture.get();
   return merge(sortedLeft, sortedRight);
   ```
4. *Critical Pitfall — The Shared Executor Requirement:* Never create `Executors.newFixedThreadPool()` inside the recursive `call()` method. Each recursive call would spawn its own pool, creating thousands of thread pools and causing pool exhaustion. Pass a single shared `ExecutorService` through the task constructor.
5. *Pool Starvation:* In a small fixed thread pool, recursive parent tasks waiting on `leftFuture.get()` occupy all worker slots while child tasks wait in the queue, causing a deadlock where CPU usage drops to zero. In production, work-stealing pools (`ForkJoinPool`) or sequential cut-offs for small sub-lists resolve starvation.

## Practical Backend Scenario

A financial portfolio dashboard aggregator compiles real-time asset summaries across stock holdings, mutual fund valuations, fixed-deposit returns, and crypto wallet balances. Each external provider API call takes between 80ms and 250ms. Running them sequentially takes $80 + 150 + 120 + 250 = 600\text{ms}$.

The service constructs an `ExecutorService pool = Executors.newFixedThreadPool(4)` and models each provider query as a `Callable<AssetSummary>`. Using the submit-first / collect-last pattern, the service submits all four queries in parallel and awaits results with a strict timeout `future.get(300, TimeUnit.MILLISECONDS)`. The total response latency drops to $\sim 250\text{ms}$ (the duration of the slowest single provider), and any failed or timed-out subtask is isolated without crashing the entire user dashboard.

## Practice Loop

1. Write a `NumberPrinter` task and submit 20 tasks to `Executors.newFixedThreadPool(5)`; verify via printed thread names that exactly 5 threads process all 20 tasks.
2. Implement `NumberGenerator` implementing `Callable<Integer>` that sums integers $1..N$; submit it to a pool and retrieve the result using `Future.get()`.
3. Implement the serializing anti-pattern (`pool.submit(t1).get()` before submitting `t2`) and measure execution time against the correct submit-first / collect-last pattern.
4. Implement `MergeSortTask` implementing `Callable<List<Integer>>` passing a shared `ExecutorService`, sorting a list of 1,000 random integers.
5. Omit `pool.shutdown()` to verify the JVM remains running indefinitely, then add `pool.shutdown()` and `awaitTermination()` to verify clean termination.

## Evidence of Understanding

You can explain the TATA production line analogy for thread pools, distinguish `Executors` from `ExecutorService`, contrast `Runnable` with `Callable`, articulate why calling `.get()` immediately after `.submit()` serializes work, explain why a single shared executor must be passed down recursive decompositions, and explain the cause of pool starvation in fixed thread pools.

## Suggested Extension

Implement a parallel array sum task `ArraySumTask` implementing `Callable<Long>` that splits an array of 1,000,000 elements across $N$ threads using a shared `ExecutorService`, with a sequential threshold cutoff of 5,000 elements to eliminate thread overhead on small partitions.
",
            "08-concurrency-3-synchronization" => @"# Lesson 8 — Concurrency 3: Synchronization, Race Conditions & Locks

## Concepts Covered

Foundational Law of Concurrency: **""Separate memory is safe. Shared memory is danger.""**
In Concurrency-2, multithreaded Merge Sort executed without conflicts because child tasks operated on completely disjoint list allocations. The moment multiple concurrent threads read and write to the *same* shared mutable memory, safety collapses.

**The Adder-Subtractor Problem (Worked Race Condition):**
- A shared `Count` object holds a single field `private int value = 0`.
- An `Adder` task runs on Thread 1, executing a loop 100,000 times: `count.value++`.
- A `Subtractor` task runs on Thread 2, executing a loop 100,000 times: `count.value--`.
- Mathematically, adding 1 and subtracting 1 the exact same number of times must yield `0`.
- Yet running this program in Java yields unpredictable, corrupted results like `-14`, `37`, or `423`.

**Why Single-Line Statements Fail — The Three-Step Breakdown:**
At the CPU/bytecode level, `count++` is not an atomic operation. It decomposes into three discrete steps:
1. **Read:** Fetch the current value of `count.value` from RAM into a CPU register ($x = \text{value}$).
2. **Modify:** Increment the value in the register ($x = x + 1$).
3. **Write:** Write the register value back to memory in RAM ($\text{value} = x$).

**Pre-emption and Interleaving:**
The OS CPU scheduler can pre-empt (interrupt) a thread between any of these steps. If Thread 1 reads `0` and is pre-empted, Thread 2 runs through read (`0`), decrement (`-1`), and write (`-1`). When Thread 1 resumes, its register holds stale value `0`; it increments to `1` and writes `1` to RAM. Thread 2's completed decrement is completely obliterated.

**Core Concurrency Vocabulary:**
- **Critical Section:** Any region of code that accesses (reads or writes) shared mutable data where concurrent execution can cause corruption.
- **Race Condition:** A defect where the correctness of a program depends on the non-deterministic timing and execution interleaving of concurrent threads.
- **Pre-emption:** The scheduler pausing an active thread mid-task without warning to allocate CPU time to another thread.

**Solution 1: Explicit Mutex (`ReentrantLock`):**
- Mutex = *Mutually Exclusive* lock.
- Only one thread can hold the lock at any time. A thread must acquire the lock before entering the critical section and release it immediately upon exiting.
- *Strict Java Discipline:* Always release the lock inside a `finally` block so that runtime exceptions never cause a permanent lock leak:
  ```java
  Lock lock = new ReentrantLock();
  lock.lock();
  try {
      // Critical Section
      count.value++;
  } finally {
      lock.unlock();
  }
  ```

**Solution 2: The `synchronized` Block:**
Java's intrinsic monitor lock built into every object header.
Syntax: `synchronized (sharedObject) { count.value++; }`.
The JVM automatically acquires the lock upon entering the block and releases it upon exiting (even if an uncaught exception is thrown).

**Solution 3: The `synchronized` Method:**
Declaring `public synchronized void increment()` locks the calling instance (`this`). Declaring `public static synchronized void helper()` locks the class's `Class` object (`Count.class`).

**The Object-Level Lock Ownership Rule:**
**""The lock is on the OBJECT. Not on the method. Not on the thread.""**
- Every Java object has exactly one intrinsic monitor lock.
- If class `A` has two synchronized methods `fun1()` and `fun2()`, two threads calling `obj1.fun1()` and `obj1.fun2()` on the *same* instance `obj1` cannot execute concurrently — both compete for `obj1`'s single lock.
- Two threads calling `obj1.fun1()` and `obj2.fun1()` on *different* instances run concurrently because each object has its own independent lock.
- An unsynchronized method `fun3()` on `obj1` executes concurrently with `fun1()` because `fun3()` does not request the lock.

**Producer-Consumer Introduction & The Check-Then-Act Bug:**
Multiple producer threads add items to a shared `Store`; multiple consumer threads remove items.
Naive code (`if (store.size() > 0) store.removeItem();`) crashes with `IndexOutOfBoundsException` because multiple threads check `size() > 0` simultaneously before any thread removes an item.
Wrapping methods in `synchronized(store)` fixes correctness, but introduces a major throughput limitation: `synchronized` is binary (all-or-nothing), admitting only 1 thread even when a store with capacity 5 has 4 empty shelves.

## Practical Backend Scenario

An e-commerce seat-booking service processes simultaneous ticket reservations for a high-demand concert (like BookMyShow). Two customer requests arrive at the exact same millisecond to reserve the final remaining VIP seat.
Without synchronization, both threads check `if (seat.isAvailable())` and evaluate `true`. Both threads charge the respective customers' credit cards, and both write `seat.setBooked(true)`. The seat is double-booked, resulting in customer escalations and transaction disputes.

By enclosing the reservation logic inside a synchronized critical section (or using `ReentrantLock`), the check-and-book sequence executes atomically:
```java
public synchronized boolean reserveSeat(String customerId) {
    if (this.isAvailable) {
        this.isAvailable = false;
        this.bookedBy = customerId;
        return true;
    }
    return false;
}
```
The first thread acquires the lock, confirms availability, marks the seat booked, and releases the lock. The second thread acquires the lock, sees `isAvailable == false`, and is safely rejected.

## Practice Loop

1. Implement the `Count` class and reproduce the Adder-Subtractor race condition with 100,000 iterations across two threads, verifying non-zero output.
2. Fix the Adder-Subtractor race using `ReentrantLock`, placing `lock.lock()` before the `try` block and `lock.unlock()` inside `finally`.
3. Refactor `Count` using `synchronized` methods on `increment()` and `decrement()`; execute 20 test runs and confirm the result is consistently `0`.
4. Create class `A` with `synchronized void fun1()`, `synchronized void fun2()`, and `void fun3()`; launch threads against the same and different instances to empirically verify the object-level locking rule.
5. Replace locking with Java's lock-free `AtomicInteger` using Compare-And-Swap (CAS) hardware instructions and compare benchmark performance under contention.

## Evidence of Understanding

You can explain the three discrete CPU steps of `count++` (read-modify-write), define Critical Section, Race Condition, and Pre-emption, demonstrate proper `ReentrantLock` usage with `finally`, articulate the object-level lock ownership rule, and explain why `synchronized` limits concurrency in multi-capacity systems.

## Suggested Extension

Implement a thread-safe banking `Account` class with `transfer(Account from, Account to, double amount)`. Enforce a strict lock-ordering protocol based on account IDs (`from.getId().compareTo(to.getId())`) to prevent circular wait deadlocks when two accounts transfer funds to each other simultaneously.
",
            "09-concurrency-4-semaphores" => @"# Lesson 9 — Concurrency 4: Semaphores & Bounded Buffer

## Concepts Covered

In Concurrency-3, `synchronized` solved race conditions by admitting exactly one thread at a time. However, this created an all-or-nothing bottleneck: in a Producer-Consumer store with capacity 5, only 1 producer was permitted to work even when all 5 slots were empty. `synchronized` cannot express admitting up to $N$ concurrent threads.

**The Semaphore Primitive:**
A **Semaphore** is a synchronization construct that maintains an internal count of available **permits** and coordinates access to shared resources through two atomic operations:
- `acquire()`: Decrements the permit count by 1. If the count is 0, the calling thread blocks until a permit is released.
- `release()`: Increments the permit count by 1 and unblocks a waiting thread if one exists. `release()` never blocks.
- **Binary Semaphore (`new Semaphore(1)`):** Initialized with 1 permit; behaves like a mutex for capacity control.
- **Counting Semaphore (`new Semaphore(N)`):** Initialized with $N$ permits; admits up to $N$ threads concurrently into a resource.

**Producer-Consumer with Two Signaling Semaphores:**
Instead of a single lock, the system tracks two independent quantities using two semaphores:
1. `producerSemaphore`: Initialized to total capacity (e.g. $S = 6$), tracking **empty slots**.
2. `consumerSemaphore`: Initialized to 0, tracking **available items**.

**Cross-Thread Signaling Flow:**
- **Producer:**
  ```java
  producerSemaphore.acquire(); // wait for an empty slot
  store.addItem(item);         // insert item
  consumerSemaphore.release(); // signal: an item is now available
  ```
- **Consumer:**
  ```java
  consumerSemaphore.acquire(); // wait for an item
  store.removeItem();          // take item
  producerSemaphore.release(); // signal: an empty slot is now free
  ```
Each side acquires its own semaphore and releases the other's, passing signals between threads without direct coupling.

**Store State Analysis (Queue Capacity Cases from Class Notes):**
For a store with maximum capacity $S = 6$:
- **Case 1 (Full Store — 6 items, 0 empty slots):** `producerSemaphore = 0`, `consumerSemaphore = 6`. Up to 6 consumers may proceed; 0 producers allowed (producers block on `acquire()`).
- **Case 2 (Partially Filled Store — 3 items, 3 empty slots):** `producerSemaphore = 3`, `consumerSemaphore = 3`. Up to 3 producers and 3 consumers may proceed in parallel.
- **Case 3 (Empty Store — 0 items, 6 empty slots):** `producerSemaphore = 6`, `consumerSemaphore = 0`. Up to 6 producers may proceed; 0 consumers allowed (consumers block on `acquire()`).

**The Bounded Buffer Pattern — Semaphore for Capacity, Mutex for Mutation:**
A counting semaphore solves the **Capacity Problem** (""how many threads may enter""). It does NOT solve the **Mutation Problem** (""what happens when multiple threads touch the underlying `ArrayList` simultaneously""). If 3 producers enter and execute `items.add(item)` concurrently on a plain list, internal array pointers corrupt.
The **Bounded Buffer Pattern** combines both: counting semaphores govern capacity and cross-thread signaling, while a mutex (`ReentrantLock`) guards the brief moment of mutating the shared list.

**Semaphore vs. Mutex — The Ownership Difference:**
- **Mutex has an owner:** Only the thread that called `lock()` may call `unlock()`.
- **Semaphore has NO owner:** Any thread can call `release()`, including a thread that never called `acquire()`.
- *No ownership is the strength:* Enables cross-thread signaling where a Consumer releases a Producer permit.
- *No ownership is the danger:* An accidental or duplicate `release()` call creates a **phantom permit**, silently inflating the permit count beyond actual physical capacity without error.

**Specialized Coordination Patterns:**
- **Baton Pattern (Strict Ordering / Turn-Taking):** Enforces ordered interleaving (e.g. *Print Zero Even Odd*). `zeroSem` starts at 1, `oddSem` and `evenSem` start at 0. The zero thread prints `0` and releases `oddSem` or `evenSem`; the number thread prints and releases `zeroSem` back.
- **Grouping Pattern (`acquire(n)` / `release(n)`):** Enforces multi-permit batch assembly (e.g. *Building H2O*). Hydrogen calls `h.acquire()` (starts at 2) and signals `o.release()`; Oxygen calls `o.acquire(2)` (starts at 0) to await two hydrogens before proceeding, then calls `h.release(2)` for the next molecule.

## Practical Backend Scenario

An outbound notification dispatch gateway connects to a third-party SMS carrier API with a strict contractual rate limit of at most 8 concurrent HTTP connections. A batch of 1,000 urgent one-time passwords (OTPs) arrives for dispatch.

The service initializes `Semaphore connectionLimiter = new Semaphore(8)`. When a worker thread processes an OTP dispatch job:
```java
connectionLimiter.acquire();
try {
    smsClient.sendSms(otpRequest); // Up to 8 concurrent network calls
} finally {
    connectionLimiter.release();
}
```
Up to 8 worker threads execute HTTP requests concurrently in parallel, achieving maximum allowable throughput while strictly guaranteeing that the downstream carrier's concurrency threshold is never exceeded.

## Practice Loop

1. Implement the two-semaphore Producer-Consumer `Store` with capacity 5 (`producerSemaphore(5)`, `consumerSemaphore(0)`); spawn 8 producers and 20 consumers, verifying active parallel execution.
2. Add a `ReentrantLock` inside `Store.addItem()` and `Store.removeItem()` to complete the Bounded Buffer pattern, verifying mutation safety on an underlying `ArrayList`.
3. Deliberately add an unmatched `producerSemaphore.release()` inside the producer loop; observe phantom permit inflation violating the capacity limit, demonstrating the lack of semaphore ownership.
4. Implement the Baton pattern for LeetCode 1116 (*Print Zero Even Odd*) using three semaphores (`zero=1`, `odd=0`, `even=0`).
5. Complete the Homework Problem: Implement a multithreaded array sum calculator dividing 1,000,000 numbers across $N$ threads using `Callable` and `Future`, verifying result accuracy against single-threaded reduction.

## Evidence of Understanding

You can define counting vs binary semaphores, explain why two semaphores are required for Producer-Consumer coordination, articulate why bounded buffers require both a semaphore (capacity) and a mutex (mutation), explain the ownership difference between mutex and semaphore, and demonstrate `acquire(n)` / `release(n)` for event grouping.

## Suggested Extension

Implement a `DatabaseConnectionPool` managing 10 physical database connections using a `Semaphore(10)` and a thread-safe `ConcurrentLinkedQueue<Connection>`, with connection validation and timeout handling on `acquire()`.
",
            "10-java-adv-1-generics" => @"# Lesson 10 — Java Advanced 1: Generics & Type Erasure

## Concepts Covered

Prior to Java 5, building reusable data structures required storing and passing data as `Object`.

**The Pre-Generics Problem — `Object`-Based Containers:**
Consider the need to store coordinate pairs (`class Coordinate { double x, y; }`) versus name pairs (`class Name { String x, y; }`). To eliminate duplicate classes, developers wrote universal containers backed by `Object`:
```java
class Pair {
    Object first, second;
    void setFirst(Object f) { first = f; }
    void setSecond(Object s) { second = s; }
}
```
While flexible, this design completely eliminated compile-time type safety:
```java
Pair p = new Pair();
p.setFirst(""yosh"");
p.setSecond(19);

double calculateSum(Pair p) {
    return (Double) p.first + (Double) p.second; // Crashes at runtime!
}
```
The compiler raised zero warnings during compilation. The mismatch surfaced only at runtime as a fatal `ClassCastException`.

**Generics — Parameterized Types:**
Generics allow classes, interfaces, and methods to be parameterized with placeholder type variables (`T`, `V`, `K`):
```java
class Pair<T, V> {
    private T first;
    private V second;
    public Pair(T first, V second) { this.first = first; this.second = second; }
    public T getFirst() { return first; }
    public V getSecond() { return second; }
}
```
Client code binds the concrete types at creation time: `Pair<String, Integer> p = new Pair<>(""Rohit"", 100);`. Attempting `p.setFirst(100)` fails at compile time, eliminating runtime type-cast errors.
**Raw Types (`Pair p = new Pair();`):** Supported for backward compatibility with pre-Java 5 code. Raw types bypass generic type checking and treat fields as `Object`; they should never be used in modern Java.

**Generic Methods:**
Methods can declare their own independent type parameters, even within non-generic classes. This is mandatory for `static` utility methods because static members have no access to class-level type parameters:
```java
public static <T> T getFirstElement(List<T> list) {
    return (list == null || list.isEmpty()) ? null : list.get(0);
}
```

**Generics with Inheritance — Why Subtyping Does Not Transfer:**
If `Dog` extends `Animal`, is `List<Dog>` a subtype of `List<Animal>`? **No.**
If Java allowed `List<Animal> animals = new ArrayList<Dog>();`, a caller could execute `animals.add(new Cat());`. Because `animals` references a list of dogs on the heap, adding a `Cat` would corrupt heap type safety. Therefore, generic collections are **invariant**: `List<Dog>` and `List<Animal>` are treated as completely unrelated types.

**Bounded Wildcards & The PECS Framework:**
To allow generic methods to operate flexibly across class hierarchies, Java provides **wildcards** (`?`):
1. **Upper-Bounded Wildcard (`? extends T`):** Accepts `T` and any subclass of `T` (`List<? extends Animal>`). Used when **reading** data from a collection. Writing elements into the collection is prohibited (except `null`) because the compiler cannot determine the exact underlying subtype.
2. **Lower-Bounded Wildcard (`? super T`):** Accepts `T` and any superclass of `T` (`List<? super Dog>`). Used when **writing / inserting** elements into a collection. Reading from the collection only returns `Object`.
3. **PECS Rule:** **Producer `extends`, Consumer `super`.**
   - If your method reads data from a collection (the collection *produces* values for you), declare it with `? extends`.
   - If your method writes data into a collection (the collection *consumes* values from you), declare it with `? super`.

**Type Erasure & Runtime Implications:**
Java implements generics via **Type Erasure** to maintain binary backward compatibility with legacy JVM bytecode:
- The compiler verifies all type safety rules at compile time and inserts necessary casts into the bytecode.
- The compiler then *erases* type parameters, replacing unbounded parameters `T` with `Object` and bounded parameters `T extends Number` with `Number`.
- *Runtime Consequences:* `new T()` is illegal, creating generic arrays `new T[10]` is prohibited, `instanceof List<String>` is disallowed (only `instanceof List<?>` is valid), and type parameters cannot be queried reflectively without passing explicit `Class<T>` type tokens.

**Collections Framework Hierarchy Overview:**
- Root `Collection<E>` interface branches into `List<E>` (`ArrayList`, `LinkedList`, `Vector`), `Queue<E>` / `Deque<E>` (`PriorityQueue`, `ArrayDeque`), and `Set<E>` (`HashSet`, `LinkedHashSet`, `TreeSet`).
- `Map<K, V>` operates as an independent key-value hierarchy (`HashMap`, `TreeMap`, `LinkedHashMap`).

## Practical Backend Scenario

A multi-tenant SaaS analytics engine manages diverse domain entities (`Customer`, `Order`, `Invoice`) extending a common `BaseEntity`. Instead of writing separate database access objects for every entity, the backend defines a generic repository interface `Repository<T extends BaseEntity, ID>` and a generic response wrapper `Page<T>`.

A batch processing service uses bounded wildcards to process entity streams:
```java
public void logEntityTimestamps(List<? extends BaseEntity> entities) {
    for (BaseEntity entity : entities) {
        System.out.println(entity.getId() + "": "" + entity.getCreatedAt());
    }
}
```
`logEntityTimestamps` accepts `List<Customer>`, `List<Order>`, or `List<Invoice>` safely (`Producer extends`). When seeding default accounts, `public void seedAccounts(List<? super Customer> sink)` safely inserts `Customer` instances (`Consumer super`).

## Practice Loop

1. Write a non-generic `Pair` class with `Object` fields; store a `String` and an `Integer`, attempt a cast to `Double`, and observe the runtime `ClassCastException`.
2. Refactor into generic `Pair<T, V>` with private fields and typed getters/setters; verify that type mismatches fail immediately at compile time.
3. Write a generic method `public static <T> void swap(T[] array, int i, int j)` and test it on both `String[]` and `Integer[]`.
4. Create an `Animal`, `Dog`, `Cat` hierarchy; demonstrate that `List<Dog>` cannot be passed to `List<Animal>`, and fix the method signature using `List<? extends Animal>`.
5. Implement the PECS utility method `public static <T> void copy(List<? super T> dest, List<? extends T> src)` and verify data copying between subtype sources and supertype destinations.

## Evidence of Understanding

You can explain why `Object`-based containers fail type safety, define type parameters versus raw types, articulate why `List<Dog>` is not a subtype of `List<Animal>`, apply the PECS rule (`? extends` for reading, `? super` for writing), and explain how type erasure influences runtime JVM execution.

## Suggested Extension

Build a generic `InMemoryCache<K, V>` with TTL expiration, implementing `putAll(Map<? extends K, ? extends V> entries)` and `getAll(Collection<? extends K> keys)` following strict PECS conventions.
",
            "11-java-adv-2-collections-lab" => @"# Lesson 11 — Java Advanced 2: Collections Framework & Sorting Lab

## Concepts Covered

Selecting the appropriate collection is a core architectural decision dictated by operational access patterns, Big-O algorithmic complexity, and memory overhead.

**Collections Framework Architecture & Trade-Offs:**
- `ArrayList`: Dynamic resizable array. Fast $O(1)$ indexed reads and cache locality; amortized $O(1)$ append; expensive $O(N)$ arbitrary insertions/deletions due to element shifting.
- `LinkedList`: Doubly linked list. $O(1)$ insertions and removals at head and tail (`addFirst()`, `removeLast()`); $O(N)$ sequential search with higher pointer memory overhead per node.
- `Vector`: Legacy synchronized dynamic array. Thread-safe but imposes per-operation lock overhead; superseded by `ArrayList` and `java.util.concurrent` collections in modern design.
- `HashSet`: Backed by a hash table (`HashMap`). Expected $O(1)$ search, insertion, and deletion; unordered.
- `LinkedHashSet`: `HashSet` backed by a doubly linked list; maintains insertion order.
- `TreeSet`: Backed by a balanced Red-Black Tree (`NavigableMap`). Guaranteed $O(\log N)$ search, insertion, and removal; maintains sorted natural or comparator order.
- `PriorityQueue`: Backed by a balanced binary heap. $O(1)$ retrieval of minimum/maximum element via `peek()`, $O(\log N)$ extraction via `poll()`; iteration is unordered.

**Natural Ordering with `Comparable<T>`:**
- `Comparable<T>` defines an entity's single, intrinsic **natural ordering** implemented inside the class via `int compareTo(T other)`.
- Returns a negative integer if `this < other`, zero if `this.equals(other)`, and a positive integer if `this > other`.
- Classes implementing `Comparable` (`String`, `Integer`, `Item`) can be sorted automatically by `Collections.sort(list)` and inserted into `TreeSet` / `TreeMap` without custom configuration.

**Contextual Ordering with `Comparator<T>`:**
- `Comparator<T>` defines an external, swappable sorting strategy implemented outside the target entity via `int compare(T a, T b)`.
- A class can have multiple comparators (e.g. `PriceAscendingComparator`, `QuantityDescendingComparator`, `Comparator.comparing(Item::getName)`).
- Allows adding new sorting criteria without modifying existing entity classes.

**The Strict `equals()` and `hashCode()` Contract:**
**""If `a.equals(b)` is true, then `a.hashCode()` must equal `b.hashCode()`.""**
- `HashSet` and `HashMap` compute the storage bucket using `hashCode() % numBuckets` first.
- If `equals()` is overridden without overriding `hashCode()`, two logically identical objects produce different memory-derived hash codes and land in different buckets. `HashSet` fails to find the existing entry and inserts a duplicate, silently violating uniqueness.
- *Mutable Key Hazard:* If an object's fields used in `hashCode()` mutate after insertion into a map or set, its hash code changes, making the object permanently lost and unretrievable.

## Practical Backend Scenario

The lab builds a comprehensive **Inventory Management System (IMS)** structured across six progressive milestones:

**Milestone 1 — Item Entity & Natural Ordering:**
Create base `Item` class with fields `sku`, `name`, `price`, and `quantity`. Implement `Comparable<Item>` establishing natural ordering sorted by `sku` (or ascending `price`).

**Milestone 2 — Generic Inventory Container:**
Build `Inventory<T extends Item>` backed by `HashMap<String, T>` providing $O(1)$ item lookup, stock additions, and inventory updates by SKU.

**Milestone 3 — Recently-Viewed Item Cache:**
Implement an LRU-style recently-viewed history buffer using `LinkedList<T>` with $O(1)$ front insertion via `addFirst()` on item access and bounded capacity eviction via `removeLast()`.

**Milestone 4 — Priority Order Processing Queue:**
Build an order fulfillment pipeline using `PriorityQueue<Order>` backed by a binary heap, ensuring high-urgency and VIP orders are extracted for fulfillment ahead of standard orders regardless of insertion sequence.

**Milestone 5 — Multi-Criteria Comparator Sorting:**
Implement external `Comparator<Item>` sorting strategies: sorting by stock quantity descending, alphabetical by name, and chained sorting `Comparator.comparing(Item::getPrice).thenComparing(Item::getQuantity)`.

**Milestone 6 — Set Deduplication & Hash Contract Verification:**
Enforce unique product catalog tagging using `HashSet<Item>`. Implement consistent `equals()` and `hashCode()` methods based on `sku`, demonstrating that omitting `hashCode()` causes duplicate entries in hash sets.

## Practice Loop

1. Build Milestone 1: Create `Item` implementing `Comparable<Item>`, populate a `List<Item>`, and sort using `Collections.sort(list)`.
2. Build Milestone 2: Implement generic `Inventory<T extends Item>` with `HashMap<String, T>` storage and bounded type parameter constraints.
3. Build Milestone 3: Implement the recently-viewed cache using `LinkedList`, verifying $O(1)$ `addFirst()` and `removeLast()` operations.
4. Build Milestone 4: Enqueue orders into `PriorityQueue<Order>` and verify that `poll()` extracts orders strictly in priority sequence.
5. Build Milestone 5 & 6: Create custom `Comparator` lambdas, override `equals()` and `hashCode()` on `Item`, and verify duplicate rejection in `HashSet<Item>`.

## Evidence of Understanding

You can justify collection choices based on access patterns ($O(1)$ vs $O(\log N)$ vs $O(N)$), contrast `Comparable` (single internal natural order) with `Comparator` (multiple external strategies), trace how `HashSet` uses hash buckets and equality checks, and explain why violating the `equals`/`hashCode` contract breaks set deduplication.

## Suggested Extension

Implement an in-memory `LruCache<K, V>` by extending `LinkedHashMap<K, V>` with access-order enabled (`new LinkedHashMap<>(capacity, 0.75f, true)`) and overriding `removeEldestEntry()`, verifying $O(1)$ lookup and automated eviction of least-recently-used entries.
",
            "12-java-adv-3-lambdas-streams" => @"# Lesson 12 — Java Advanced 3: Lambdas & Functional Streams

## Concepts Covered

Modern Java balances object-oriented structure with functional programming paradigms introduced in Java 8.

**Functional Interfaces (SAM Interfaces):**
A **Functional Interface** is an interface that declares **exactly one abstract method** (Single Abstract Method). It may contain any number of `default` or `static` methods. Annotated with `@FunctionalInterface`.
Core functional interfaces in `java.util.function`:
- `Predicate<T>`: `boolean test(T t)` — conditional checks and filtering.
- `Consumer<T>`: `void accept(T t)` — accepting inputs and performing side effects (e.g. logging).
- `Function<T, R>`: `R apply(T t)` — transforming an input of type `T` into an output of type `R`.
- `Supplier<T>`: `T get()` — factory supplier returning values without arguments.
- `BinaryOperator<T>`: `T apply(T a, T b)` — combining two operands of the same type.
- `IntFunction<R>`: `R apply(int value)` — primitive-specialized mapping avoiding boxing overhead.

**Evolution of Interface Implementation:**
Consider running a task on a separate thread:
1. **Named Class:** Standalone class `public class MyTask implements Runnable` with boilerplate class definitions.
2. **Anonymous Class:** Inline `new Runnable() { @Override public void run() { System.out.println(""Hello""); } }` — eliminates separate files but carries heavy syntax ceremony.
3. **Lambda Expression:** Direct functional syntax: `Runnable r = () -> System.out.println(""Hello"");`.
Because a functional interface has exactly one abstract method, the compiler infers parameter types, return types, and method identity from target context.

**Syntax Variations for Lambdas:**
- Multiple parameters: `(a, b) -> a + b`
- Single parameter (parentheses optional): `x -> x * x`
- Multi-statement body (requires braces and explicit `return`): `(a, b) -> { int sum = a + b; return sum; }`
- Code Examples from Class Notes:
  ```java
  Consumer<String> c = x -> System.out.println(""hello "" + x);
  Predicate<Integer> isEven = x -> x % 2 == 0;
  ```

**Streams API — Thinking in Pipelines:**
A **Stream** is a sequence of computational elements supporting sequential and parallel aggregate operations. A stream is NOT a data structure — it does not store data; it conveys elements from a source through a pipeline of transformations.

**The Three Pipeline Stages:**
1. **Source:** Collection, array, or I/O generator (`list.stream()`, `Arrays.stream(arr)`).
2. **Intermediate Operations (Lazy):** Transform a stream into another stream. Intermediate operations execute **lazily** — no computation occurs until a terminal operation is invoked. Examples: `filter(Predicate)`, `map(Function)`, `sorted(Comparator)`, `distinct()`, `limit(long)`, `skip(long)`.
3. **Terminal Operations (Eager):** Trigger pipeline traversal, process elements, and produce a result or side effect. Examples: `collect(Collector)`, `forEach(Consumer)`, `count()`, `reduce()`, `allMatch(Predicate)`, `anyMatch(Predicate)`, `findFirst()`.

**Lazy vs. Eager Evaluation & Imperative Loop Elimination:**
Traditional imperative loops require throwaway intermediate lists (`List<Integer> evens = new ArrayList<>()`), multiple passes over data, and inefficient repeated scanning (`contains()`).
Stream pipelines evaluate lazily: elements flow through chained operations vertically element-by-element, short-circuiting early when possible (`findFirst()`, `allMatch()`).

**Design Judgment — When NOT to Use Lambdas:**
Lambdas are intended for concise, locally scoped logic (such as in-line sorting or filtering). Reusable business rules shared across multiple controllers, complex multi-line validation algorithms, or logic requiring isolated unit tests should remain in named, dedicated classes or methods.

## Practical Backend Scenario

A financial transaction auditing engine processes high-volume customer payment events. The service receives a stream of raw transaction records, filters out non-settled payments, isolates transactions exceeding \$100, transforms each transaction into an audit summary DTO with masked account numbers, sorts them in descending order of transaction amount, and collects unique transaction references into a reporting list.

Instead of writing 15 lines of nested loops with temporary collections, the backend expresses the workflow as a clean, declarative stream pipeline:
```java
List<String> highValueAudits = transactions.stream()
    .filter(t -> t.getStatus() == TransactionStatus.SETTLED)
    .filter(t -> t.getAmount() > 100.0)
    .sorted(Comparator.comparing(Transaction::getAmount).reversed())
    .map(Transaction::toMaskedAuditLog)
    .distinct()
    .collect(Collectors.toList());
```

## Practice Loop

1. Declare a custom `@FunctionalInterface StringTransformer` with `String transform(String input)`; implement it using a named class, an anonymous class, and a lambda expression.
2. Instantiate standard functional interfaces (`IntFunction`, `BinaryOperator`, `Function`) and execute them using lambda syntax.
3. Refactor a multi-step imperative loop (filtering even numbers, squaring them, sorting descending, deduplicating) into a declarative stream pipeline.
4. Demonstrate lazy evaluation: construct a stream pipeline with `filter()` and `map()` printing debug logs; verify that nothing executes until `count()` or `collect()` is invoked.
5. Implement custom comparator sorting with lambdas and method references (`Comparator.comparing(String::length).reversed()`).

## Evidence of Understanding

You can define functional interfaces (SAM), explain why lambda expressions are syntactic sugar over functional interfaces, distinguish intermediate (lazy) from terminal (eager) stream operations, contrast declarative stream pipelines with imperative loops, and explain when named classes should be chosen over lambdas.

## Suggested Extension

Build a customer analytics pipeline that processes a list of order records, calculates total revenue per customer tier using `mapToDouble()` and `sum()`, and filters the top 5 spenders into an immutable list.
",
            "13-java-adv-4-streams-exceptions" => @"# Lesson 13 — Java Advanced 4: Streams in Depth & Exception Architecture

## Concepts Covered

Building enterprise backend applications requires mastering advanced stream collectors for data aggregation and designing a resilient exception architecture for production fault tolerance.

**Advanced Stream Collectors & Aggregations:**
The `Collectors` utility class provides powerful aggregation operations for terminal stream processing:
- `Collectors.groupingBy()`: Groups elements by a classifier function into a `Map<K, List<V>>` (e.g. `fruits.stream().collect(Collectors.groupingBy(String::length))` maps character lengths to fruit name lists).
- **Downstream Collectors:** Combining `groupingBy` with secondary collectors such as `Collectors.counting()`, `Collectors.mapping()`, `Collectors.toSet()`, or `Collectors.averagingDouble()` to perform multi-level aggregations in a single pass.
- `Collectors.partitioningBy()`: Specialized grouping using a `Predicate<T>`, partitioning elements into exactly two groups stored in `Map<Boolean, List<T>>`.
- `Collectors.toMap()`: Collects stream elements into key-value maps. *Critical Rule:* An explicit merge function `(existing, replacement) -> existing` must be supplied when keys may collide, preventing runtime `IllegalStateException`.
- `Collectors.joining(delimiter)`: Concatenates stream elements into a single formatted string.

**Java Exception Architecture & Type Hierarchy:**
`Throwable` is the root superclass of all errors and exceptions in Java:
- **`Error`:** Critical system-level failures outside application control (`OutOfMemoryError`, `StackOverflowError`). Application code should never catch `Error`.
- **`Exception`:** Application-level conditions that programs can reasonably intercept and handle.
  - **`RuntimeException` (Unchecked Exceptions):** Subclasses of `RuntimeException` representing programming defects, logic errors, and broken invariants (`NullPointerException`, `IllegalArgumentException`, `IndexOutOfBoundsException`). Unchecked by the compiler; do not require explicit `throws` declarations.
  - **Checked Exceptions:** Subclasses of `Exception` (excluding `RuntimeException`) representing anticipated, recoverable operational failures (`IOException`, `SQLException`). Enforced at compile time; must be caught or declared in method signatures.

**Enterprise Exception Handling Best Practices:**
- **`try`-with-resources:** Automatically closes all `AutoCloseable` resources (database connections, file streams, sockets) in reverse order of declaration upon block exit, safely preserving suppressed exceptions.
- **Layered Exception Translation:** Catch low-level technical exceptions (e.g. `SQLException`, `IOException`) at infrastructure boundaries and translate them into typed domain/application exceptions (`EntityNotFoundException`, `DuplicateKeyException`, `PaymentGatewayException`) carrying structured error codes and HTTP status metadata.
- **Checked Exceptions in Stream Lambdas:** Stream lambdas cannot throw unhandled checked exceptions. Wrap checked exceptions into unchecked domain exceptions or bridge them using dedicated functional error wrappers.

## Practical Backend Scenario

A nightly reconciliation and settlement engine processes paginated merchant transaction batches. The service reads transaction statements, filters settled entries, partitions transactions into domestic versus international settlements (`partitioningBy`), groups transactions by merchant ID (`groupingBy`), and sums total revenue per merchant into a summary map using `Collectors.toMap(Transaction::getMerchantId, Transaction::getAmount, Double::sum)`.

During batch file parsing, the service uses `try`-with-resources to read statement streams. If a corrupted line or database timeout occurs, the system catches the low-level exception, wraps it in a typed `SettlementProcessingException` with batch correlation IDs, logs the failure without exposing sensitive cardholder data, quarantines the malformed record into a dead-letter queue, and allows remaining merchant reconciliations to complete.

## Practice Loop

1. Construct a stream pipeline grouping a list of product names by character length using `Collectors.groupingBy(String::length)`.
2. Partition a list of integers into prime versus non-prime numbers using `Collectors.partitioningBy()`.
3. Implement `Collectors.toMap()` on a list containing duplicate keys, providing an explicit merge function `(v1, v2) -> v1 + v2` to accumulate colliding values.
4. Build a custom exception hierarchy with a base `ApplicationException` and specialized subclasses `ResourceNotFoundException` and `ValidationException`.
5. Implement a file reader method using `try`-with-resources, demonstrating automated resource cleanup and layered exception translation.

## Evidence of Understanding

You can implement multi-level grouping and partitioning with downstream collectors, explain why `toMap()` requires duplicate-key merge functions, articulate the distinction between Checked and Unchecked exceptions in the Java hierarchy, and design layered exception translation that maps internal errors to clean API error contracts.

## Suggested Extension

Implement a resilient stream wrapper utility `CheckedFunction<T, R, E extends Exception>` that cleanly catches checked exceptions within stream mapping pipelines, rethrowing them as typed runtime domain exceptions with structured error context.
",
            "14-solid-principles" => @"# Lesson 14 — SOLID Principles for Extensible Systems

## Concepts Covered

SOLID names five instincts about code quality precisely enough to diagnose and discuss a design problem in specific terms, rather than a vague sense that ""this code is messy."" Each principle in this lesson is anchored to the same running example: a naive `Bird` class holding every bird's data and a branching `fly()` method, corrected one principle at a time.

**Single Responsibility Principle (SRP):** a code unit should have exactly one reason to change. The violation is not about length — a long method built from steps of one coherent algorithm can still respect SRP — it is specifically when the reasons a method might change are unrelated to each other. A `Bird.fly()` method with an `if/else` chain per bird type is really doing two jobs: representing a bird, and knowing how every kind of bird flies. Real-world anchor: an employee expected to simultaneously be the accountant, the IT support, and the receptionist will drop something the moment two of those unrelated responsibilities compete for attention at once.

**Open/Closed Principle (OCP):** a system should be open for extension but closed for modification — a new requirement should be met with new code, not edits to code that already worked and already has passing tests. Refactoring `Bird` into an `abstract class Bird` with an abstract `fly()` method, overridden by `Pigeon`, `Sparrow`, and `Peacock`, means adding a new bird type is a new subclass, not a new `else if` branch in a shared method. Real-world anchor: a well-designed house allows a new room to be added without demolishing the kitchen to do it.

**The Penguin Problem — the bridge from OCP to LSP:** the abstract-`fly()` refactor immediately hits a wall: a `Penguin` cannot honestly fly. Giving it an empty `fly()` body or having it `throw new UnsupportedOperationException()` both compile fine, but both are lies about the contract every other `Bird` subtype honors — client code that does `for (Bird b : birds) b.fly();` now either does nothing for a penguin (silently wrong) or crashes (a runtime surprise nothing in the type system warned about).

**Liskov Substitution Principle (LSP):** a subtype must be usable anywhere its parent type is expected, without the caller needing special-case handling, and this is about a promise being kept, not about inheritance syntax being valid — code that compiles cleanly can still violate LSP. A subclass may only make preconditions less strict (require less than the parent demanded) and postconditions more strict (guarantee at least as much as the parent promised); weakening a guarantee or demanding more up front breaks substitutability even if every method technically overrides correctly. The `Penguin.fly()` problem is exactly an LSP violation dressed up as an OCP fix: client code that loops over `List<Bird>` and calls `.fly()` on each one now needs a `Penguin`-specific `if (b.type == ""Penguin"") continue;` check to avoid a crash — the moment a caller needs a type check or a `try/catch` to safely use a subtype where its parent type was expected, LSP is broken. Real-world anchor: a ""Backend Developer"" job description promises the ability to write REST APIs — anyone hired into that role is expected to deliver on it without the team handling them differently.

**Interface Segregation Principle (ISP):** no client should be forced to depend on methods it does not use. An interface that bundles several unrelated capabilities into one contract forces every implementer to take on obligations it may not actually have — exactly the same shape of problem the Penguin hit, but at the interface level instead of the inheritance level. Real-world anchor: a fixed thali forces every customer to take the full combination of courses, whether they want all of it or not; an à la carte menu lets a customer order exactly what they need.

**Dependency Inversion Principle (DIP):** high-level modules should not depend on low-level modules — both should depend on abstractions. A class that depends directly on another concrete class is wired in a way that makes both classes harder to change independently and harder to test in isolation. Real-world anchor: a phone charger does not wire itself directly into the power plant; it plugs into a wall socket, a standard interface both sides agree to.

**Dependency Injection (not itself a SOLID letter):** a natural consequence of DIP, not a sixth principle — supplying a class's dependencies from outside rather than having the class construct them itself. Real-world anchor: a new employee joining a company is not expected to bring their own laptop and desk; the company supplies it, and the employee simply plugs in and starts working.

**Where this leads next:** by the end of the `Bird` refactor, flying has been extracted into its own `FlyingBehaviour` interface, supplied to a bird rather than hard-coded inside it — this is already a named, well-established design pattern (Strategy), the subject of the very next class, and easier to follow because this lesson builds the underlying reasoning by hand first, before the pattern is named.

## Practical Backend Scenario

A notification system started with a single class containing `if/else` branches for email, SMS, and push notifications — every new channel required editing that same tested method (an OCP violation identical in shape to the `Bird.fly()` branching problem). A separate `UserService` class was found to be simultaneously validating credentials, querying the database directly, and formatting API responses — three unrelated reasons to change bundled into one class (an SRP violation). A `PaymentProcessor` interface required every implementer to expose `refund()`, `chargeSubscription()`, and `generateInvoice()`, even though a one-time-payment provider had no concept of a subscription — forcing that implementer to throw `UnsupportedOperationException` from methods it could never honestly support (an ISP violation with the exact same ""Penguin smell"" as the `Bird` example). Fixing all three: the notification class became a `NotificationChannel` interface with one implementation per channel (OCP), `UserService` was split so authentication, persistence, and formatting each live in their own focused class (SRP), and the fat `PaymentProcessor` interface was split into `Refundable`, `SubscriptionCapable`, and `InvoiceGenerating`, each implemented only by the providers that can genuinely support it (ISP).

## Practice Loop

1. Take the `Bird` class with a branching `fly()` method; refactor it into an abstract class with one subclass per bird type, and identify the exact `Penguin`-shaped case where a subtype cannot honestly implement the forced method.
2. Rewrite the caller loop over `List<Bird>` so that it needs zero special-case type checks for any subtype — if it still needs one, the LSP violation has not actually been fixed yet.
3. Find a fat interface in any codebase (or write one deliberately) where at least one implementer throws `UnsupportedOperationException` from a required method; split it into smaller, capability-specific interfaces.
4. Take two concrete classes wired directly to each other (`new ConcreteLogger()` called directly inside a service); introduce a shared interface and inject the dependency through the constructor instead.
5. Write down, for a class you already have, exactly one sentence naming its single reason to change; if you cannot do it in one sentence, it likely violates SRP.

## Evidence of Understanding

You can recognize an SRP violation as unrelated reasons to change, not merely length. You can distinguish extending a system from modifying its existing, working code, and explain the regression risk of the latter. You can identify the ""Penguin problem"" pattern — a forced method a subtype cannot honestly implement — as the shared root of an OCP-refactor gone wrong and an LSP violation. You can restate LSP as a promise being kept (in terms of precondition/postcondition strictness) rather than a compiler-checked guarantee. You can split a fat interface using ISP and rewrite a direct concrete-to-concrete dependency using DIP, and explain why Dependency Injection is a consequence of DIP rather than a sixth principle.

## Suggested Extension

Take the `FlyingBehaviour` interface this lesson arrives at (flying extracted out of `Bird` and supplied from outside) and predict, before the next lesson, what pattern this already is and why supplying it through a constructor rather than hard-coding it inside `Bird` is itself an application of DIP.
",
            "15-creational-patterns" => @"# Lesson 15 — Creational Design Patterns

## Concepts Covered

A design pattern is a well-known, reusable solution to a problem that keeps showing up across different, unrelated software systems — not one person's clever idea, but a shape many engineers independently arrive at. In 1994, four authors (Gamma, Helm, Johnson, Vlissides — the ""Gang of Four"" or GoF) catalogued 23 of these. Design patterns are not separate from SOLID; they are named, reusable shapes for applying principles like SOLID to a recurring problem. This module covers the **creational** family — patterns about how and when objects get created.

**Singleton — Exactly One Shared Object:** use Singleton when a shared resource sits behind the class (a DB connection, a logger, a cache — one shared office printer beats five competing ones), or when creating the object is genuinely expensive (a DB connection setup involves real network round-trips before the first query even runs). Building one correctly, step by step: (1) make the constructor `private` so outside code cannot call `new` directly; (2) keep one `private static` field holding the single instance; (3) expose a `public static getInstance()` that creates the instance only if it doesn't exist yet, then returns it — never make the instance field itself `public`, since that removes all protection over the ""only one"" rule. **Eager loading** (`private static Instance = new Instance();`, built at class-load time) needs no locking but slows startup and locks in configuration too early; **lazy loading** (built on first `getInstance()` call) avoids that cost but introduces a real concurrency danger: two threads can both see `instance == null` at nearly the same moment and both create their own object, a race condition. The fix, **double-checked locking**, checks for null once without a lock (fast, used almost every call), and only takes the lock — then checks null *again* inside it — during the one risky moment; the inner check exists because a second thread could have been waiting for the lock while the first thread finished creating the instance, and skipping it lets two objects slip through anyway. Even correct double-checked locking has one more gap that AI-generated code frequently misses: the `instance` field must be declared `private static volatile`, because `instance = new DBConnection()` is really three steps (allocate memory, run the constructor, assign the reference) that the compiler and CPU are otherwise free to reorder — without `volatile`, a second thread could see a non-null reference pointing to a half-constructed object. Serialization is a separate hole double-checked locking does not close at all: Java deserialization rebuilds an object directly from saved bytes, skipping the private constructor and `getInstance()` entirely, which is why many engineers reach for an **enum Singleton** instead — the JVM guarantees exactly one instance, thread-safety, and serialization-safety for free. Since a Singleton always hands back the same object, tests can silently leak state between each other; a `resetInstance()` helper (not part of the original GoF pattern, added purely for testing) clears the stored instance so each test starts fresh — but must never be called from production code, since resetting a live instance while other parts of the app still hold the old one creates two competing ""shared"" objects, exactly what Singleton exists to prevent.

**Builder — Safely Constructing Objects with Many Optional Fields:** a large constructor with many same-typed parameters is easy to call with arguments silently swapped (the compiler cannot catch it), and a `Map<String, Object>` of settings makes a wrong key ""silently do nothing"" with type errors only surfacing at runtime. Builder fixes this with a nested helper class that collects values with compiler-checked chainable setters (each setter returns `this`), then performs validation and constructs the real object through a single `build()` method. Four things make a production-quality Builder: a static `getBuilder()` on the main class showing how to begin; `build()` performing real validation before constructing; every setter returning the Builder itself for fluent chaining (`.setAge(21).setName(""Naman"").build()`); and a `private` constructor on the main class so nothing can bypass the Builder's validation. Mutable fields like `List`s must be defensively copied inside `build()`, not just referenced, or the caller can mutate the ""finished"" object from outside after construction completes.

**Prototype and Registry — Copying Instead of Constructing:** manually copying an object's fields from outside the class couples the caller to every internal field name, cannot reach private fields with no setters, and forces a growing `instanceof` chain to handle subclasses (an OCP violation). Prototype fixes this with a `Prototype<T>` interface requiring `T clone()`; every subclass must override `clone()` itself and call `super(instance)`, because a child that forgets to override `clone()` silently runs its parent's clone logic and drops any fields the child added. A **Registry** is a separate `Map`-based store (`ConcurrentHashMap` for thread safety) for retrieving named prototype templates — `registry.get(""ubuntu-base"")` — where a missing key returns `null` silently, which then causes a `NullPointerException` later, on a completely different line, the moment `.clone()` runs on that `null`. The most common implementation bug is a **shallow copy trap**: copying a mutable field like a `List` by reference (`this.list = instance.list;`) leaves the original and the copy sharing the exact same underlying list, so mutating one mutates both; the fix constructs a genuinely new container from the source's contents (`new ArrayList<>(instance.list)`).

**Factory — Deciding Which Class to Instantiate:** the problem Factory solves is a decision (""which class to build"") becoming known only at runtime, from configuration or user choice. A naive `if/else` chain hardcoded inside a client (`if (provider.equals(""openai""))...`) is an OCP violation — a new provider means editing tested code — and duplicates the same decision logic anywhere else it's needed. A **Simple/Static Factory** centralizes that decision into one method (`AIServiceClientProvider.getClient(provider)`), so the client depends only on an interface. This is deliberately not the strict GoF Factory Method (which uses an abstract method overridden by subclasses, with polymorphism doing the dispatch) — the practical static-factory shape is far more common in real codebases. An **Abstract Factory** goes one level up: when a single provider must supply a *family* of related objects that must stay compatible with each other (a chat client, an embeddings client, and a moderation client that must all come from the same vendor), an `AIProviderFactory` interface groups the related creation methods together so a caller can never accidentally mix an OpenAI chat client with a Gemini moderation client. Even a well-intentioned static factory can still secretly violate OCP: if adding a new provider still means reopening `getClient()`'s `if/else` chain, it has only centralized the branching, not eliminated the extensibility problem — a **registry-backed factory** (`Map<String, Supplier<T>>`, populated via a `register(name, Constructor::new)` call from each provider's own bootstrap code) genuinely lets a different team add a new provider without ever touching the factory class itself. Java's built-in `ServiceLoader` takes this even further, discovering implementations automatically from `META-INF/services` metadata files with no shared registration code at all — this is exactly how JDBC drivers and SLF4J logging backends register themselves.

## Practical Backend Scenario

A payments platform needs exactly one shared `ConnectionPoolManager` coordinating all database connections (Singleton, built with double-checked locking and `volatile`, with a `resetInstance()` used only in its test suite). Creating a `PaymentRequest` object safely, with required fields (amount, currency) and several optional ones (idempotency key, metadata, retry policy), uses a `Builder` with a private constructor so no `PaymentRequest` can exist without passing through validation. When a new merchant account is provisioned, its default settings are cloned from a `MerchantConfigTemplate` `Prototype`, looked up by tier name (""gold"", ""silver"") from a `ConfigRegistry`, with every clone defensively copying its mutable `allowedCurrencies` list rather than sharing a reference. Finally, routing a chat completion request to OpenAI, Anthropic, or Gemini goes through a registry-backed `AIServiceClientFactory`, so integrating a fourth provider next quarter is a one-line `register()` call from that provider's own module, not an edit to the factory class.

## Practice Loop

1. Build a `DBConnection` Singleton from scratch, in order: private constructor, static field, `getInstance()`; deliberately remove `volatile` first and explain in one sentence why the code still compiles but is unsafe, then add it back.
2. Add a `resetInstance()` to your Singleton and use it in a `@BeforeEach` to prove two sequential tests don't leak state between each other.
3. Build a `Builder` for a class with at least 5 fields (2 required, 3 optional, one of them a `List`); verify the `List` is defensively copied by mutating the caller's original list after `build()` and confirming the built object is unaffected.
4. Implement `Prototype<T>` on a two-level class hierarchy (a subclass adding its own field); deliberately forget to override `clone()` on the subclass first, observe the dropped field, then fix it with `super(instance)`.
5. Refactor an `if/else` factory into a registry-backed one (`Map<String, Supplier<T>>`), and prove a new type can be registered from a separate class without touching the factory itself.

## Evidence of Understanding

You can name the two legitimate reasons to reach for Singleton and explain why double-checked locking needs two null checks and a `volatile` field. You can build a Builder with proper validation, chaining, and defensive copying, and explain why a public constructor defeats the pattern's entire purpose. You can implement Prototype correctly across a subclass hierarchy and identify the shallow-copy trap on sight. You can distinguish a Simple Factory from an Abstract Factory by whether a single object or a compatible family of objects is being created, and explain why a registry-backed factory is more genuinely extensible than a static if/else factory.

## Suggested Extension

Build a small plugin-style system where a `Registry` of `Prototype` templates is populated at startup via a registry-backed `Factory`, so that adding a new template type requires registering it from that type's own module — combining all four patterns from this lesson into one cohesive design.
",
            "16-structural-patterns" => @"# Lesson 16 — Structural Patterns: Adapter, Facade, Decorator & Flyweight

## Concepts Covered

Structural patterns govern how objects are organized and connected *after* they already exist — a different concern from creational patterns (which govern *how* objects come into being).

**Adapter — Translating Without Touching Either Side:**
An adapter is a middle layer connecting two things that don't fit together, without changing either side. The classic production scenario: PhonePe needs to integrate Yes Bank, HDFC, and other banks, each with its own incompatible API shape, without rewriting PhonePe's core code for every new bank and without editing the banks' own SDK code (which would be overwritten on the next upstream update anyway). An adapter has three components: a **Target Interface** (the client's expected contract, e.g. PhonePe's internal `BankAPI`), an **Adaptee** (the existing incompatible class — the actual bank SDK), and the **Adapter** itself, which implements the target interface while internally wrapping and translating calls to the adaptee. Translation can take several forms: type conversion (an int status code becomes a boolean), data reshaping (an object's fields become primitive arguments), pass-through (when shapes already align), and method renaming (identical behavior under a different name). The everyday physical analogy is a MacBook USB-C-to-HDMI dongle: it changes neither the laptop's port nor the monitor's cable, it just translates between the two shapes.

**Facade — One Simple Entry Point Over Complexity:**
A facade provides one simple entry point that hides the coordination of several complex subsystems behind it. The production scenario: instead of `Amazon.orderPlace()` directly calling invoice, warehouse, inventory, and email services itself (violating single responsibility), a dedicated `OrderPlacedFacade` coordinates all of that complexity behind one method call. A correctly designed facade receives its subsystem dependencies through its constructor (dependency injection) rather than constructing them internally with `new` — this keeps the facade swappable and testable with mocks, and prevents it from being locked to one concrete implementation.

**Distinguishing Adapter from Facade:** the test is *why* the wrapper exists. If the problem is two incompatible interfaces that need translating, it's an Adapter (typically one adaptee). If the problem is a complex, hard-to-use system that needs a simpler front door, it's a Facade (typically multiple subsystems). Real systems often combine both — an adapter can live inside a facade.

**Decorator — Adding Behavior by Wrapping, Not Editing:**
Decorator attaches new responsibilities to an object dynamically by wrapping it in another object that implements the same interface, leaving the original class completely untouched. The canonical worked example is a coffee shop: `Espresso implements Beverage` costs 80.0. Wrapping it as `new Mocha(order)` adds 20.0 by delegating to the wrapped beverage's `cost()` and adding its own charge on top; wrapping again as `new Whip(order)` adds another 15.0 the same way — three layers deep, `order.cost()` returns 115.0. Because decorators are just objects implementing the same interface as what they wrap, they compose: wrapping in `Mocha` *twice* (`new Mocha(new Mocha(order))`) naturally produces a ""double mocha"" with zero new code, which is the entire point of the pattern. The failure mode to recognize: if someone adds boolean flags like `hasMocha`/`hasWhip` and `if` branches directly inside `Espresso` to fake this behavior, they have reintroduced the exact tight coupling Decorator exists to eliminate — every new add-on then requires editing the base class again, and each new combination needs its own branch. A concrete bug to know: a `CondimentDecorator` subclass must have a constructor that receives and stores the wrapped `Beverage` (often via `super(beverage)`); forgetting this constructor is a common reason this pattern fails to compile.

**Flyweight — Sharing State to Cut Memory:**
Flyweight splits an object's data into **intrinsic state** (identical across many instances, safe to share from one cached object) and **extrinsic state** (unique per instance, passed in from the caller at the moment of use, never stored in the shared object). The canonical example: a game needs millions of bullets on screen, but they only come in a handful of *types* (e.g. ""AKM"") — the bullet's damage, model, and sound are intrinsic (identical for every AKM bullet fired) and belong in one cached `BulletType` object per type name, while each bullet's current position is extrinsic and passed in separately per bullet instance. A `BulletTypeFactory` backed by a `HashMap` returns the *same* cached object for the same type name (`getBulletType(""AKM"") == getBulletType(""AKM"")` is `true`), which is what makes the memory saving real. The most common mistake when applying this pattern is inverting the split — for example, in a text-editor `Character` class rendering millions of characters, the *font/size/color* are usually shared across large runs of text (intrinsic, cacheable) while each character's *row/column position* is unique per occurrence (extrinsic, passed in); a design that puts position into the shared/cached class and formatting into the per-instance class has the split exactly backwards. The same reasoning scales to any domain with a small fixed set of categories shared across a huge number of records — a food delivery app with only 30 order categories but millions of daily line items should cache one `Category` object per name and have every line item reference it, not duplicate the category data into every line item.

## Practical Backend Scenario

A payments platform (like PhonePe) needs to onboard a new bank partner every few months, each with its own SDK shape — this is solved with an `Adapter` per bank implementing a shared internal `BankAPI` interface, so onboarding a bank never requires editing the core payment-routing code. That same platform's order-completion flow touches five subsystems (payment confirmation, invoice generation, warehouse dispatch, inventory decrement, and email notification) — a `Facade` coordinates all five behind one `completeOrder()` call, with every subsystem dependency injected through the constructor so the flow can be tested with mocks. The platform's promotions team wants to stack optional order-level perks (free delivery, gift wrap, priority handling) without rewriting the base `Order` class for every combination — `Decorator` lets each perk be its own wrapper class, composable in any combination the promotions team invents later. Finally, the platform's catalog has only ~200 distinct product categories but tens of millions of line items across all orders — a `Flyweight`-backed `CategoryFactory` caches one `Category` object per category name so line items reference shared instances instead of duplicating category data millions of times over.

## Practice Loop

1. Implement a `BankAPI` target interface and two adapters (e.g. `YesBankAdapter`, `HDFCBankAdapter`) wrapping two differently-shaped fake bank SDKs, demonstrating at least one type-conversion translation and one method-renaming translation.
2. Implement an `OrderPlacedFacade` with four injected subsystem dependencies (constructor injection, no internal `new`), and write a test that substitutes a mock for one subsystem to prove testability.
3. Implement the coffee shop `Beverage`/`CondimentDecorator` hierarchy from scratch: `Espresso`, `Mocha`, `Whip`, verify triple-wrapping produces the correct additive cost, and verify double-wrapping the same decorator works without new code.
4. Implement a `BulletTypeFactory` backed by a `HashMap<String, BulletType>`; verify with `==` that two lookups of the same type name return the identical cached object, and that a new type name creates and caches a new object.
5. Take the `CharacterIntrinsic`/`CharacterExtrinsic` split example from this lesson's self-check, deliberately implement it backwards first (position cached, formatting passed in), observe why it fails to deliver any memory saving, then correct the split.

## Evidence of Understanding

You can state the three components of an Adapter and explain why editing third-party SDK code directly is unsafe. You can explain why a Facade's dependencies must be injected rather than constructed internally. You can trace a three-layer Decorator chain's `cost()` calculation by hand and explain why stacking the same decorator twice works without new code. You can classify any given field in a domain object as intrinsic or extrinsic state and justify a Flyweight factory design from an object count versus distinct-type count argument.

## Suggested Extension

Combine two of these patterns in one worked example: build a `PaymentGatewayFacade` that internally selects between `RazorpayAdapter` and `StripeAdapter` (Adapter used inside a Facade), and separately extend the coffee shop model with a `Decorator`-based loyalty-discount chain that a `Flyweight`-backed `DiscountRuleFactory` supplies shared, cached discount-rule objects to.
",
            "17-behavioural-patterns-uml" => @"# Lesson 17 — Behavioural Patterns & UML Diagrams

## Concepts Covered

Behavioural patterns govern how objects communicate and distribute responsibility for an algorithm or a reaction to change — distinct from structural patterns (which govern how objects are wired together) and creational patterns (which govern how objects are made).

**Strategy — Selecting an Algorithm, Not Branching Inside One:**
Strategy extracts an algorithm into its own interface so the algorithm in use can be swapped without touching the class that uses it. The failure mode it replaces: one method full of `if (mode.equals(""car""))` / `else if (mode.equals(""bike""))` branches, where adding a new mode means editing and re-testing existing, already-working code — a direct violation of the Open-Closed Principle and Single Responsibility. Strategy's fix: each mode becomes its own class implementing a shared interface (e.g. `CarPathCalculator`, `BikePathCalculator`), and the class that needs the behavior (e.g. `PricingManager`, `VideoStreamingManager`) holds a reference to the interface, not to any concrete implementation, receiving it through its constructor. A concrete strategy class deliberately does **not** take a ""mode"" parameter in its methods — the class itself already represents one specific way of doing the task, so telling it what mode it is would be redundant and would reopen the door to the same branching the pattern exists to remove. Most concrete strategies are stateless (all their inputs arrive as method parameters, nothing is stored as instance state), which is exactly why a Strategy Factory can safely cache and return one shared instance per type instead of constructing a new object on every call. A `StrategyFactory`'s only job is selection: mapping some input (a mode string, an enum) to the correct concrete strategy object — it never executes the algorithm itself, and a common bug is a factory built on a lookup map that only covers some of the possible inputs, silently returning `null` for any input it wasn't given an entry for, which surfaces later as a `NullPointerException` far from the real mistake.

**Strategy vs. Chain of Responsibility — Choosing One vs. Trying in Sequence:**
It's a common misclassification to call a fallback/retry sequence a ""Strategy"" because multiple implementations share one interface. The test is behavioral: Strategy selects exactly one implementation up front and uses only that one. A payment flow that tries Razorpay, then falls back to Stripe on failure, then falls back to PayPal, is not Strategy — no single provider was chosen ahead of time, and control passes along a sequence until one succeeds. That ordered, try-until-handled shape is Chain of Responsibility, a related but distinct pattern.

**Observer — Broadcasting a Change to Many Listeners:**
Observer lets a subject (the publisher) notify an open-ended set of listeners (observers) whenever its state changes, without the publisher needing to know anything about who those listeners are or how many there will be. The publisher holds a list of a shared `Observer` interface, exposes `subscribe`/`unsubscribe` (or `register`/`addObserver`) to manage that list, and — critically — must actually iterate the list and invoke each observer inside every method that changes state. The single most common Observer bug is exactly that last step going missing: a `setTemperature(double temp)` method that updates the field but never loops through `observers` and calls their update method leaves every registered listener silently uninformed, even though registration itself worked perfectly. Unsubscribing removes an observer from the list going forward only — a `Publisher` that subscribes a `Logger`, publishes an event (which the logger receives), unsubscribes the logger, then publishes a second event, delivers only the first event to that logger, not the second. This is why adding an entirely new kind of subscriber (e.g. a `WhatsAppService` next to existing `AlertService`, `EmailService`, `SlackService` observers) requires zero changes to the publisher — it's simply one more object registering itself against the same interface.

**Strategy vs. Observer — the Real Distinguishing Question:**
Both patterns program against one interface implemented by multiple classes, which is why they're often confused. The distinguishing question is intent: does the caller pick exactly *one* implementation to delegate to (Strategy), or does the caller notify *every* registered implementation at once (Observer)? A `RoutingStrategy` selects one AI model to route a query to; a list of `Observer`s all receive the same order-placed event simultaneously. Neither pattern is ""better"" — they solve different problems that happen to share the same programming-to-an-interface mechanic.

**UML — A Shared Notation for Communicating Design:**
UML (Unified Modelling Language) is a standardized visual notation so any engineer reads the same diagram shapes the same way, independent of implementation language. It splits into **Structural UML** (Class, Object, Component diagrams — describing the frozen structure of a codebase) and **Behavioral UML** (Use Case, Sequence, Activity diagrams — describing behavior over time). A Class diagram box has three sections: name, then attributes (`- privateField: Type`, `+ publicField: Type`), then methods (`+ methodName(): ReturnType`), using `-`/`+`/`#` for private/public/protected. Static members are underlined regardless of access modifier. An abstract class's name and abstract methods are shown in italics; an interface carries a `<<interface>>` stereotype label; an enum carries `<<enumeration>>`. In Use Case diagrams, a solid **includes** arrow means the parent use case *always* triggers the child (e.g. ""Enroll in Course"" includes ""Make Payment""); a dashed **extends** arrow means the child is one *optional* variant of the parent (e.g. ""Pay by UPI"" and ""Pay by Card"" both extend ""Make Payment""). For HAS-A relationships, a hollow diamond denotes **aggregation** (both objects can exist independently — e.g. a reusable `Module` shared across multiple `Course`s), while a filled diamond denotes **composition** (the child cannot exist without the parent — e.g. a one-off `Module` that belongs to exactly one `Course`). There is deliberately no universal rule for which one applies to a given relationship — the same `Module`-to-`Course` relationship can be legitimately aggregation or composition depending on the actual product requirement, and this judgment call cannot be automated away by an ORM. A composite primary key is the alternative to a surrogate `id` column on a junction table: instead of adding a new auto-incrementing column, the combination of both foreign keys together (e.g. `student_id` + `course_id`) serves as the primary key, since that pair is already guaranteed unique. In Hibernate, a plain `@ManyToMany` is sufficient only when the relationship itself carries no extra data; the moment the relationship needs its own fields (e.g. an `enrolledAt` timestamp on an enrollment), it must be modeled as its own full `@Entity` with two `@ManyToOne` sides instead, because a plain many-to-many junction table has nowhere to store that extra column. The most reliable way to tell aggregation from composition is a lifecycle-dependency test, not intuition: if the contained object continues to exist and make sense after the container is deleted (a post surviving its author's account deletion, a song surviving its playlist's deletion), it's aggregation; if the contained object stops making sense the moment the container is gone (a notebook's pages, a car's engine and wheels, a GPS trip's route coordinates), it's composition — and a common implementation bug is a class that claims aggregation but actually constructs its dependency internally in its own constructor (e.g. `this.driver = new Driver();` inside `Car`'s constructor) rather than receiving an already-existing object from outside, which silently turns it into composition-like ownership regardless of what the diagram says.

## Practical Backend Scenario

A logistics platform's delivery-fee calculation started as one method with an `if/else` chain per vehicle type; every new vehicle type meant editing and re-testing that same method. Refactored with Strategy, each vehicle type is its own `DeliveryFeeStrategy` implementation, selected once by a `DeliveryFeeStrategyFactory` and injected into the `OrderPricingService` constructor — adding a new vehicle type is now a new class, with zero changes to existing, already-shipped fee logic. Separately, the platform's order-status system needs to trigger unrelated side effects on every state change: sending an SMS, updating a warehouse dashboard, and logging an audit trail. An `Order` publisher holds a list of `OrderObserver`s and loops through them inside `updateStatus()`; when the growth team later wants to add a loyalty-points side effect, they register a new `LoyaltyPointsObserver` without touching `Order` at all. A design review of the payment flow (Razorpay, then Stripe, then PayPal on failure) correctly identifies this as Chain of Responsibility, not Strategy, since the flow tries providers in sequence rather than committing to one upfront. Finally, before implementing any of this, the team sketches a UML class diagram for the `Order`/`OrderObserver` relationship and a schema diagram showing that `Order` and `Customer` need a foreign key on the ""many"" side, while `Order` and `Promotion` need a junction table since a promotion can apply to many orders and an order can carry many promotions.

## Practice Loop

1. Take a method with an `if/else` chain over 3+ modes and refactor it into a `Strategy` interface with one concrete class per mode, injected via constructor.
2. Build a `StrategyFactory` backed by a lookup map; deliberately call it with an input the map doesn't cover and observe the `NullPointerException`, then fix it with an explicit `IllegalArgumentException` for unknown inputs instead of a silent `null`.
3. Implement a publisher/`Observer` pair; write a test proving that unsubscribing an observer mid-flow means it receives events published before, but not after, the unsubscribe call.
4. Deliberately write a publisher that updates its own field but forgets to loop through observers — confirm no observer fires — then fix it by adding the notification loop.
5. Draw a UML class diagram (by hand or in a tool) for one of the systems built in this lesson, correctly using `-`/`+`/`#` prefixes, underlined statics, italicized abstract members, and a hollow or filled diamond for any HAS-A relationship, justifying your aggregation-versus-composition choice in one sentence.

## Evidence of Understanding

You can explain why a concrete strategy class should never take a mode parameter, and why most strategies are safely shareable as cached singletons. You can distinguish Strategy (picks one implementation) from Chain of Responsibility (tries several in sequence) from Observer (notifies all at once) using the same one-interface-many-classes shape. You can identify the single most common Observer bug (missing notification loop) on sight. You can read and produce a basic UML class diagram with correct visibility, static, and abstract notation, and justify an aggregation-versus-composition choice as a product judgment rather than a memorized rule.

## Suggested Extension

Combine Strategy and Observer in one system: build a trading alert engine where a `StrategyFactory` selects the correct `TradingIndicatorStrategy` (momentum, volatility) per instrument, and every computed alert is broadcast to a list of `AlertObserver`s (email, SMS, dashboard) — then draw the UML class diagram for the resulting design, including the aggregation/composition judgment call for the relationship between an `Instrument` and its list of `TradingIndicatorStrategy` results.
",
            "18-how-to-approach-design" => @"# Lesson 18 — How to Approach Design Problems

A repeatable framework for machine coding interviews and real-world system design: requirements gathering, entity identification, relationship mapping, and iterative refinement.

## Concepts Covered

Machine coding interviews fail most often not from lack of Java knowledge but from lack of sequencing discipline — jumping straight into classes before the requirements are pinned down. Scaler's 6-step framework exists to prevent that: Step 0 is alignment with the interviewer (or with yourself, in a solo problem) — confirm what you already know and explicitly name what you don't, rather than assuming. Two questions settle the shape of the whole exercise before any design starts: does this system need to persist data, or is an in-memory, single-run structure acceptable; and how will a user actually interact with it — a REST API, a CLI, or a hardcoded `main()` method exercising the classes directly. Getting these two answers wrong early costs far more time than getting them right.

Step 1 is requirement gathering, typically producing 5–10 explicit, numbered requirements (R1, R2, R3...) rather than a vague paragraph. Step 2 clarifies and resolves tradeoffs within those requirements — this is where multiple candidate approaches to a tricky requirement (like an undo feature, or a pluggable pricing strategy) get compared on time and space complexity before committing to one. Step 3 turns the clarified requirements into a class diagram: nouns from the requirements become candidate classes, verbs become candidate methods, and the diagram should be walkable as a user journey — a reader should be able to trace what happens, in order, class by class, when a user performs the core action.

A phrase like ""this behavior needs to be swappable without rewriting the system"" is a Strategy pattern appearing in plain English — trained eyes catch it during requirement clarification, before any diagramming starts, rather than noticing only once the code has already ossified around a single hardcoded approach. Requirements that describe multiple interchangeable algorithms (fee calculation, spot assignment, bot difficulty, winning-condition checks) are the strongest signal.

## Practical Backend Scenario

A team is asked to design a vehicle management system: a `Vehicle` class family covering fuel, electric, and hybrid types, each supporting `refuel()`, `recharge()`, and `start()`/`stop()` operations where applicable. Before any class is written, Step 0 settles that this is an in-memory entity system exercised via a hardcoded `main()` — no database, no REST layer. Step 1 produces requirements: vehicles have name, brand, cost, and type; hybrid vehicles must support both refueling and recharging; transmission type (automatic or manual) needs a shared base representation. Step 2 clarifies the inheritance shape — an `IVehicle` interface at the top, with `IFuelable` and `IRechargeable` capability interfaces mixed in per vehicle type, so a `HybridVehicle` can implement both without a fragile single-inheritance chain forcing awkward compromises.

## Practice Loop

Apply the 6-step framework to a single new problem end to end: state Step 0's two answers explicitly (persistence? interaction mode?) before writing a single requirement. Write 6–8 numbered requirements for a vehicle rental system. Identify which requirement phrases signal a Strategy pattern before drawing anything. Produce a class diagram from those requirements, and verify it by walking through one full user journey (a user rents a vehicle, drives it, returns it) using only the diagram — if a step in the journey can't be traced to a class and method, the diagram is incomplete.

## Evidence of Understanding

You can name Step 0's two settling questions from memory and explain why answering them first changes everything downstream. You can read a requirement and identify, before diagramming, whether it signals a Strategy pattern. You can produce a class diagram directly from a numbered requirements list and defend each class's existence by pointing to the requirement that justified it.

## Suggested Extension

Take a requirements list you've already turned into a class diagram for a past problem and audit it: for every class, can you name the exact requirement number that justified its existence? Any class that can't be justified this way is a sign the framework was skipped, not followed.
",
            "19-machine-coding-tictactoe" => @"# Lesson 19 — Machine Coding: TicTacToe

Design and implement a clean, extensible TicTacToe engine: board abstraction, player management, win-condition strategy, and handling NxN generalization.

## Concepts Covered

TicTacToe is Scaler's first full application of the 6-step framework to a complete, working system, and its value is in the seven requirements it generates: an N×N board (not fixed at 3×3), up to N−1 players, unique symbols chosen per player, support for bot players, bots with a difficulty curve (easy, medium, hard), configurable win-condition rules chosen before the game starts, and an undo feature. Each of these pushes the design toward extensibility rather than a special-cased 3×3, two-player script.

The undo feature is the requirement most worth slowing down on, because three genuinely different implementations exist with different tradeoffs. The first stores a stack of past moves and works for TicTacToe specifically, but breaks down for games with more complex state mutation per move (chess captures, for example) because undoing a move isn't always the exact inverse of applying it. The second replays all N−1 prior moves onto a freshly empty board — correct for any game, but O(N²) time and O(N·N·m) space for m stored move-lists, since every undo re-simulates from scratch. The third stores a full board snapshot after every move, making undo an O(N) lookup — trading memory for speed, which is the right trade for a bounded board size where snapshots stay small.

Win-condition checking has its own optimization arc, moving through four solutions. The naive approach checks every player against the entire board (every row, column, and diagonal) after every move: O(N³). Since only the player who just moved could possibly have created a new winning line, checking only the current player already drops this to O(N²). Since a move at position (i, j) can only ever affect row i, column j, and — only when i == j or i + j == N−1 — one or both diagonals, checking only the touched lines drops this further to O(N). The final optimization replaces re-scanning entirely with running counters: a map per row, per column, and two fixed maps for the diagonals, incremented on every placed symbol and compared against N. This reaches O(1) time per move at the cost of O(N) additional space — for a bounded board size, accepting that space cost for constant-time checking is the correct trade, and it only works if the counters live as persistent fields on the class, not as local variables recreated on every call.

Three design patterns organize the resulting system. `Game` is constructed exclusively through a `GameBuilder`, whose validation (bot count capped at one per game, player count matching board dimension minus one, symbol uniqueness across all players) runs before any `Game` instance can exist — a private constructor makes bypassing this impossible. Player creation goes through a `PlayerFactory` returning the correct concrete type. Both winning-condition checks and bot move-selection are Strategy implementations: a `WinningStrategy` interface lets a new rule be added as one new class without touching `Game`'s core logic, and `BotPlayingStrategy` implementations (an easy strategy picking the first empty cell, a hard strategy using minimax with alpha-beta pruning) let a `Bot` delegate its move-selection entirely, keeping `Bot` itself thin.

## Practical Backend Scenario

A generalized N×N TicTacToe engine needs to support a variable board size chosen at game start, an arbitrary number of human and bot players up to N−1, and a pluggable win-condition so a ""diagonal-only"" or ""four-corners"" variant can be added later without modifying `Game`. The engine also needs O(1) win detection per move so that even a large board doesn't degrade turn latency, and an undo feature cheap enough to support repeatedly without rebuilding board state from scratch.

## Practice Loop

Implement the core model — `Board`, `Cell`, `Symbol`, `Move`, an abstract `Player` — with `Game` buildable only through `GameBuilder`, enforcing the three validations (bot cap, player count, symbol uniqueness). Implement `RowWinningStrategy`, `ColWinningStrategy`, and `DiagonalWinningStrategy` using persistent running-count maps rather than rescans, and verify each fires in O(1) per move. Implement `EasyBotPlayingStrategy` (first empty cell) and, as a stretch, a `HardBotPlayingStrategy` using minimax. Implement one undo approach and justify, in a comment, why you chose it over the other two given this specific bounded board size.

## Evidence of Understanding

You can explain all four stages of the win-checking optimization and why each one is strictly better than the last for this problem's bounds. You can compare the three undo approaches by time and space complexity and justify your choice for a bounded N. You can point to the exact three validations `GameBuilder` must enforce and explain why a private `Game` constructor is what makes them unbypassable. You can explain why `WinningStrategy` is a list rather than a single implementation.

## Suggested Extension

Add a new winning condition (for example, four-in-a-row on any N×N board, not just the standard N-in-a-row) as a single new `WinningStrategy` implementation, and confirm `Game`'s core logic required zero changes to support it.
",
            "20-machine-coding-parking-lot" => @"# Lesson 20 — Machine Coding: Parking Lot

Design and implement a multi-floor parking lot system: spot types, vehicle hierarchy, entry/exit ticketing, fee calculation strategy, and concurrent slot management.

## Concepts Covered

Parking Lot moves the 6-step framework from a pure game (TicTacToe) to a system involving physical resources and financial transactions, and the eight requirements it generates read differently as a result: multiple floors per lot, vehicle-type-specific spots with exact-match allocation only (a truck can never occupy a car spot), a token created and a spot assigned simultaneously at entry, payment and spot-release happening together at exit, dynamically swappable fee-calculation algorithms, support for both cash and third-party online payment, multiple physically distinct entry and exit gates, and configurable spot assignment (auto-nearest-pick or user selection). Requirements 5 and 8 are the same Strategy-pattern signal from Lesson 18 appearing twice in one problem — two separate interfaces are needed, one for fee calculation and one for spot allotment.

Walking through a driver's actual journey — arrive, receive a ticket, park, later present the ticket, pay, leave — yields nine classes: `ParkingLot`, `ParkingFloor`, `Gate`, `ParkingSpot`, `Vehicle`, `Operator`, `Ticket`, `Bill`, and `Payment`. Several of the modeling decisions here generalize well beyond parking lots. `Gate` is one class with a `GateType` enum (ENTRY or EXIT) rather than two separate `EntryGate`/`ExitGate` classes, because the two are identical except for that one field — creating a subclass distinction for a single enum value is needless duplication. `Ticket` captures its own `operator` field as a snapshot at the moment of issue, distinct from `Gate.operator`, which reflects whoever is *currently* staffing that gate — conflating the two would mean a ticket's audit trail silently changes when a shift changes, which is wrong: a ticket must record who was actually on duty when it was issued. `Bill` holds a `List<Payment>` rather than a single `Payment`, because real payment splitting (part cash, part card) needs to be representable, and each payment in the list can be independently refunded or audited. `ParkingSpot` stores its `floorId` directly rather than deriving it by walking up through the floor object on every lookup — a deliberate duplication justified by how frequently that lookup happens (printing every ticket), not applied blindly everywhere.

Schema design here follows the same class-to-table algorithm from earlier lessons — every class becomes a table, every simple attribute becomes a column, and every attribute that is itself another class needs its cardinality checked before deciding where the foreign key goes. `ParkingLot`-to-`ParkingFloor` is one-to-many, so `parking_lot_id` lives on the `parking_floor` table, not the reverse — a single `floor_id` column on `parking_lot` could only ever reference one floor, which can't represent a lot having many floors. `Bill`-to-`Payment` is similarly one-to-many, so `bill_id` sits on the `payment` table. `Gate`-to-`Operator`, by contrast, is genuinely many-to-many across the shift history (many operators work many gates over time), which would need its own mapping table if that full history matters — a plain foreign key column would only capture the *current* operator, matching what `Gate.operator` is meant to store, but not the shift history.

The design deliberately leaves one real gap unresolved after the class diagram is complete: nothing in the paper design prevents two entry gates from assigning the same empty spot to two different vehicles arriving at nearly the same moment. `AllotmentStrategy.assignSpot()` decides which spot to hand out, but no lock exists between the moment it reads ""this spot is free"" and the moment it commits that assignment — a genuine concurrency problem that only manifests when gates run concurrently, and one that a single-threaded paper design cannot surface or fix by itself.

## Practical Backend Scenario

A third-party facility-management company needs an in-memory, command-line parking system for airports and malls: multiple floors, vehicle-type-exact spot matching, tickets issued at entry with an assigned spot, bills generated at exit supporting split cash/card payment, and a fee-calculation algorithm that must be swappable per client contract without a code change to the core system.

## Practice Loop

Design the nine core classes and both Strategy interfaces (`FeeCalculationStrategy`, `AllotmentStrategy`), building `ParkingLot` through a `ParkingLotBuilder` that validates floors, gates, and both strategies are set before the lot becomes usable. Implement entry (token creation plus spot assignment as one atomic step from the caller's perspective) and exit (bill generation, payment collection, spot release) as end-to-end flows through in-memory collections. Derive the schema from your class diagram using the class-to-table algorithm, and justify every foreign key placement by naming the cardinality that dictated it. Finally, without writing concurrent code, write down in one paragraph exactly where the two-entry-gates race condition would occur in your specific implementation.

## Evidence of Understanding

You can justify why `Gate` is one class with an enum rather than two subclasses, and why `Ticket` needs its own `operator` snapshot separate from `Gate.operator`. You can explain why `Bill` holds a list of payments rather than one. You can derive correct foreign key placement for a one-to-many relationship from the cardinality alone, and explain why placing the key on the ""one"" side is representationally impossible. You can identify, without writing any threading code, exactly where a concurrent access race would occur in a spot-allotment flow.

## Suggested Extension

Add a `ReservationStrategy` allowing spots to be pre-booked ahead of physical arrival, and work through how it interacts with `AllotmentStrategy` — does a reservation reduce the pool `AllotmentStrategy` chooses from, or bypass it entirely for that vehicle?
",
            "24-machine-coding-hotel-management" => @"# Lesson 24 — Machine Coding: Hotel Management System

## Concepts Covered

This machine-coding exercise builds a Hotel Management System incrementally, across four stages, each adding one capability on top of a shared layered architecture: a **Controller** layer (accepting request DTOs and returning response DTOs), a **Service** layer (interface + implementation holding business logic), a **Repository** layer (interface + an in-memory implementation, so the domain logic stays independent of any real database), and plain **domain models** (`Room`, `User`, `Booking`, `Invoice`, `CustomerSession`) with their own enums (`RoomType`, `UserType`, `CustomerSessionStatus`) and typed exceptions (`UserNotFoundException`, `UnAuthorizedAccess`, `InvalidRoomException`). The four stages build on each other: **Add Rooms** (ADMIN-only capability to register new rooms into the system), **Get Rooms** (customers browse available rooms), **Book Rooms** (customers reserve a room, tracked through a `CustomerSession`), and **Generate Invoice** (producing a bill for a completed booking). Each stage's Controller and Service only add the one new capability the stage is named for, while reusing the Repository and domain models already established by earlier stages — this is the same incremental-milestone structure used in the OOP-4 Library Management System lab, but applied to a full request/response layered architecture instead of a single class hierarchy.

## Practical Backend Scenario

A hotel chain's booking backend separates ADMIN operations (adding rooms with a type and nightly rate) from CUSTOMER operations (browsing available rooms, filtering by type, and booking one for a date range). Every request enters through a Controller that translates an HTTP-shaped request DTO into a call on the Service layer; the Service layer enforces business rules (a `UserType` check before allowing a room to be added, a room-availability check before allowing a booking) and delegates persistence to a Repository interface, currently backed by an in-memory implementation so the whole system can be built and tested before a real database is wired in. A completed booking transitions a `CustomerSession` through its status lifecycle and becomes eligible for `Invoice` generation, which reads the booking's room rate and duration to compute the final bill.

## Practice Loop

1. Implement the **Add Rooms** stage: `RoomController`, `AddRoomRequestDto`/`AddRoomResponseDto`, `RoomService`/`RoomServiceImpl`, `RoomRepository`/`InMemoryRoomRepository`, enforcing that only an ADMIN `UserType` may add a room (throwing `UnAuthorizedAccess` otherwise).
2. Implement the **Get Rooms** stage on top of the same `Room`/`RoomRepository`: a `GetRoomsRequestDto`/`GetRoomsResponseDto` pair letting a customer browse available rooms.
3. Implement the **Book Rooms** stage: introduce `Booking`, `CustomerSession`, and `CustomerSessionStatus`; a `BookingController` accepting a `MakeBookingRequestDto` that validates the room exists (`InvalidRoomException` otherwise) and the user exists (`UserNotFoundException` otherwise) before creating a `Booking`.
4. Implement the **Generate Invoice** stage: an `Invoice` domain object and a `GenerateInvoiceRequestDto`/`GenerateInvoiceResponseDto` pair that looks up a completed `CustomerSession` (throwing `CustomerSessionNotFoundException` if it can't be found) and computes a bill from its associated `Booking` and `Room` rate.
5. Once all four stages are implemented against the same in-memory repositories, write one end-to-end test that adds a room as an ADMIN, browses it as a customer, books it, and generates its invoice — proving all four stages compose correctly through the shared Repository and domain layer.

## Evidence of Understanding

You can explain why splitting a machine-coding problem into Controller/DTO/Service/Repository layers, even for an in-memory-only implementation, keeps business logic independent of any specific persistence technology. You can justify why role-based checks (ADMIN vs. CUSTOMER) belong in the Service layer rather than the Controller. You can trace a booking's full lifecycle from `Room` creation through `CustomerSession` to `Invoice` generation, and name which typed exception fires for which specific failure case (missing room, missing user, missing session).

## Suggested Extension

Add a `CancelBooking` capability that transitions a `CustomerSession` back to an available state and updates `RoomRepository` accordingly, then extend `Invoice` generation to apply a cancellation-fee rule based on how close to the booking date the cancellation occurred.
",
            "14-spring-boot-core" => @"# Lesson 14 — Spring Boot Core: IoC & Dependency Injection

## Concepts Covered
Inversion of Control means application code declares dependencies while a container creates and wires the object graph. Constructor injection makes required dependencies visible, supports immutable fields, and lets a unit test construct a service without starting the framework. Component scanning is convenient, but explicit configuration is valuable when multiple implementations, security-sensitive clients, or environment-specific policies exist.

A bean has a lifecycle: creation, dependency resolution, initialization, use, and destruction. Scope affects state safety; a singleton should not hold request-specific mutable data. Configuration properties should be validated at startup, secrets should come from a managed secret source, and profiles should select infrastructure wiring rather than change business rules.

## Practical Backend Scenario
A payment application has `PaymentService`, `PaymentGateway`, `PaymentRepository`, and `Clock` dependencies. Production wiring selects an HTTP gateway and PostgreSQL repository, while tests provide fakes. The service remains a plain Java class with constructor validation. A feature flag controls gateway routing through a policy object, not through scattered profile checks inside domain logic.

## Practice Loop
1. Write the service as a framework-free class and test it with hand-built fakes.
2. Add Spring configuration at the edge with constructor injection.
3. Validate required endpoint and timeout properties before the application accepts traffic.
4. Test bean replacement, multiple implementations, and shutdown behavior.
5. Search for field injection, hidden service locators, mutable singleton state, and configuration reads inside domain methods.

## Evidence of Understanding
You can draw the object graph, explain which dependencies are required at construction, and run the core payment behavior without a container. A misconfigured endpoint fails at startup with a useful message instead of failing on the first customer request.

## Suggested Extension
Add a decorator that records gateway latency and failure counts while keeping the payment service unaware of metrics implementation details.
",
            "15-spring-data-jpa" => @"# Lesson 15 — Spring Data JPA & PostgreSQL Integration

## Concepts Covered
JPA maps object state to relational rows, but the mapping is not the transaction boundary by itself. Decide aggregate ownership, identifier strategy, fetch behavior, and lifecycle before adding annotations. A persistence context tracks managed entities; lazy loading can trigger queries later, and an accidentally broad entity graph can load far more data than the endpoint needs.

Transactions should be short, explicit, and aligned with a business operation. Use repository methods that match the read shape, project only required fields, and inspect generated SQL for hot paths. Prevent N+1 queries with a deliberate fetch plan, indexes, pagination, and query analysis. Optimistic locking is useful when conflicts are expected and should be surfaced as a retriable domain outcome.

## Practical Backend Scenario
An order history endpoint returns a page of orders with item summaries and payment status. The read model should not load every customer relation or serialize managed entities directly. The application uses a projection or fetch plan, a stable sort key, and a transaction that ends after the response data is assembled. The checkout write uses an idempotency key and a version check so retries do not create duplicate orders.

## Practice Loop
1. Model the order aggregate and identify which relations are owned, read-only, or external.
2. Write the expected SQL shape before writing the repository method.
3. Test query count for a page of orders and expose an N+1 regression deliberately.
4. Add an index based on a measured filter and compare the query plan.
5. Simulate a concurrent update and define the user-visible conflict behavior.

## Evidence of Understanding
You can explain the difference between an entity graph and an API response, identify where a transaction begins and ends, and diagnose an N+1 query from logs or a query-count test. Your repository does not rely on lazy loading during JSON serialization.

## Suggested Extension
Add an outbox record in the same transaction as an order state change, then describe how a separate publisher makes the event eventually delivered without duplicating the order write.
",
            "16-spring-rest-api" => @"# Lesson 16 — RESTful APIs, Validation & Security

## Concepts Covered
An HTTP API is a public contract of resources, methods, status codes, representations, validation errors, and retry semantics. Request DTOs protect the domain model from transport concerns; response DTOs prevent persistence fields from becoming accidental API commitments. Validation should fail close to the boundary, while business rules remain in the application or domain layer.

Idempotency matters for payment, booking, and other retryable commands. Authentication establishes who is calling; authorization decides what that caller may do. API keys, sessions, and JWTs have different rotation, revocation, and audience considerations. Never treat a decoded token as permission by itself. Central error handling should return a stable problem shape, a correlation id, and no stack trace or secret.

## Practical Backend Scenario
Build a booking endpoint that accepts a customer id, event slot, and idempotency key. The controller validates shape and limits, the application service checks ownership and availability, and the repository enforces the final uniqueness rule. A second request with the same key returns the stored result, while a request from another customer receives an authorization error without revealing booking existence unnecessarily.

## Practice Loop
1. Define request, response, validation, and problem-detail contracts.
2. Add tests for malformed JSON, missing fields, duplicate commands, forbidden access, and expired credentials.
3. Separate authentication middleware from resource authorization policy.
4. Add correlation logging and ensure sensitive fields are redacted.
5. Verify timeout, retry, and pagination behavior with a client that repeats requests.

## Evidence of Understanding
You can explain which layer owns each validation, distinguish 401 from 403, and prove that a retried command does not duplicate a booking. The endpoint exposes stable errors and does not serialize internal entities or credentials.

## Suggested Extension
Add an idempotency table with request fingerprint and response metadata. Define how conflicting payloads using the same key are rejected.
",
            "17-machine-coding-capstone" => @"# Lesson 17 — Distributed Systems & Machine Coding Capstone

## Concepts Covered
The capstone combines object modeling, concurrency, persistence, API boundaries, and operational thinking under a time constraint. Start with invariants and the smallest vertical slice. Separate command handling from read concerns, make retry behavior explicit, and choose one consistency boundary before optimizing. A good submission is not the most abstract design; it is a coherent design whose failure behavior can be explained.

Use an application service to coordinate a booking or ride-matching workflow, domain objects to protect state transitions, repositories for persistence, and ports for external providers. Concurrency needs a bounded execution policy and a uniqueness or version guarantee. Observability is part of correctness: record correlation ids, state transitions, latency, and failure categories without logging personal or payment data.

## Practical Backend Scenario
Implement a seat-booking service with inventory, payment authorization, and confirmation. Two customers may request the final seat at once, a payment provider may retry a callback, and notification delivery may fail after the booking commits. The design must prevent double allocation, make callbacks idempotent, and expose a recovery path for a committed booking whose notification is pending.

## Practice Loop
1. Spend the first pass writing requirements, invariants, entities, commands, and failure states.
2. Build the happy path end to end with a narrow interface and one persistence strategy.
3. Add duplicate requests, concurrent allocation, timeout, provider retry, and partial failure tests.
4. Review transaction scope, thread ownership, API errors, indexes, and logs.
5. Explain the next safe improvement and what evidence would justify it.

## Evidence of Understanding
You can defend the aggregate boundary, the concurrency guarantee, the idempotency key, and the recovery process. A reviewer can run your tests and see that the system remains correct when external calls fail or requests arrive concurrently. You can also name the assumptions that would need confirmation before production rollout.

## Suggested Extension
Add an outbox-backed notification publisher and a reconciliation command. Document duplicate delivery handling and the metrics that would alert an operator before customers report a problem.
",
            _ => null
        };
    }
}
