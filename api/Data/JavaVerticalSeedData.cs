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

            // Module 4: Spring & Enterprise Architecture
            var mod4 = new CourseModule
            {
                CourseId = course.Id,
                Slug = "spring-enterprise-architecture",
                Title = "Spring Boot & Enterprise Architecture",
                Description = "Dependency injection, Spring Data JPA, RESTful API design, PostgreSQL integration, and distributed architectures.",
                Badge = "Module 4",
                OrderIndex = 4
            };
            db.Modules.Add(mod4);
            db.SaveChanges();

            // Seed Lessons for Module 1
            SeedModule1Lessons(db, mod1.Id);

            // Seed Lessons for Module 2
            SeedModule2Lessons(db, mod2.Id);

            // Seed Lessons for Module 3
            SeedModule3Lessons(db, mod3.Id);

            // Seed Lessons for Module 4
            SeedModule4Lessons(db, mod4.Id);

            db.SaveChanges();
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
                "design-principles-patterns",
                "Design Principles & Patterns for Extensible Systems",
                "SOLID reasoning, patterns, UML, and extensibility for backend and AI integrations.",
                "Module 10",
                5,
                new[]
                {
                    Chapter("patterns-01-solid", "SOLID Principles for Extensible Systems with AI Integrations", "Dependency direction, change isolation, and honest abstractions.", "SOLID is a set of design questions, not a reason to create interfaces for every class. Ask which behavior varies, who owns the policy, and which dependency should point toward stable business rules.", "A support assistant can use hosted or local model providers. Keep prompt policy, retrieval, provider transport, and audit logging replaceable without spreading provider conditionals through the use case.", "Mark responsibilities in a small service, invert only the dependencies that vary, and write a test that swaps a provider without changing the application service.", "You can identify a real reason for an abstraction and describe the cost of a premature one.", "Review a design after a second provider and a new compliance rule arrive; list the changes that should remain localized.", 75, "Spring Framework Documentation: Dependency Injection"),
                    Chapter("patterns-02-singleton", "Design Patterns: Introduction and Singleton", "Pattern intent, lifecycle ownership, and singleton hazards.", "A pattern is a named trade-off. Singleton can centralize a stateless registry or expensive resource, but hidden global state harms tests, tenant isolation, and lifecycle control. Container-managed singleton scope is not the same as a static global.", "A model client pool is shared within one process and closed during shutdown. Its configuration must be immutable and its metrics must not leak tenant data.", "Compare a static singleton, constructor injection, and container scope; test reset behavior, shutdown, and concurrent access.", "You can explain when singleton scope is appropriate and why global mutable state is dangerous.", "Replace a singleton cache with an explicit boundary and document ownership, capacity, and invalidation.", 60, "Spring Framework Documentation: Bean Scopes"),
                    Chapter("patterns-03-builder", "Design Patterns: Builder", "Safe construction of complex immutable requests.", "Builder is useful when an object has many optional values, cross-field validation, or readable construction. It should not hide required decisions or turn every simple value into ceremony.", "Construct an AI inference request with model, messages, temperature, tool policy, timeout, and tenant budget. Invalid combinations must fail before the network call.", "Define required and optional fields, validate cross-field rules in `build`, and expose an immutable result with a safe `toBuilder` path.", "You can choose a builder from construction complexity and show that invalid requests cannot be created.", "Add a versioned request builder and test compatibility when a provider-specific option is introduced.", 60, "Effective Java: Builder Pattern"),
                    Chapter("patterns-04-prototype-registry", "Design Patterns: Prototype and Registry", "Copying configured templates without shared mutable state.", "Prototype can create related objects from a configured template, while a registry selects a named prototype. Copy semantics must be explicit: immutable values may be shared, mutable maps and lists must not alias accidentally.", "An organization registry stores prompt templates for invoice extraction, support triage, and summarization. A request receives a tenant-scoped copy with overrides.", "Define deep versus shallow copy rules, reject unknown registry names, and test that one request's overrides cannot mutate the template or another tenant's request.", "You can explain the ownership of copied state and prevent a registry from becoming an unbounded global cache.", "Add versioned templates with an audit trail and a safe retirement policy.", 75, "Java Documentation: Object Cloning and Copy Semantics"),
                    Chapter("patterns-05-factory", "Design Patterns: Factory for Service Abstraction", "Selecting providers without leaking construction logic.", "A factory centralizes selection rules when the application needs a product contract but construction depends on configuration, capability, or environment. Keep the factory from becoming a switch statement that owns every business policy.", "Select an embedding, chat, or moderation provider by capability and tenant policy. The use case receives an interface and does not know SDK classes.", "Define the product contract, validate provider capability at startup, implement two adapters, and test unknown or unavailable providers.", "You can distinguish factory selection from strategy behavior and explain where configuration validation belongs.", "Add a provider health state and decide whether selection fails fast, falls back, or returns a degraded result.", 75, "Spring Framework Documentation: FactoryBean"),
                    Chapter("patterns-06-adapter-facade", "Design Patterns: Adapter and Facade", "Boundary translation and simplified subsystem APIs.", "An adapter translates an incompatible external contract into the application port. A facade gives callers a smaller workflow-oriented API over several collaborators. Both should preserve errors and avoid hiding important consistency decisions.", "Wrap two model vendors with one `ChatCompletionPort`, then expose a `SupportAnswerFacade` that coordinates retrieval, generation, safety checks, and audit recording.", "Write the port from the use case, translate provider errors at the adapter boundary, and test the facade with deterministic fakes.", "You can identify which class owns translation and which class owns orchestration.", "Add a provider response fixture and verify that a new SDK version does not change the domain error contract.", 75, "Spring Framework Documentation: Integration"),
                    Chapter("patterns-07-decorator-flyweight", "Design Patterns: Decorator and Flyweight", "Composable behavior and safe sharing of intrinsic state.", "Decorators add cross-cutting behavior around a stable port without modifying the core implementation. Flyweight shares immutable intrinsic data while keeping request-specific extrinsic data outside the shared object.", "Decorate a model client with timeout, retry budget, metrics, and redaction. Share immutable tokenizer metadata across requests while keeping conversation state per request.", "Compose decorators in a deliberate order, test failure and metric behavior, and prove that shared metadata cannot retain tenant-specific data.", "You can explain the difference between wrapping behavior and sharing state, including the memory and observability trade-offs.", "Add a circuit breaker decorator and define how it interacts with retries and fallback.", 75, "OpenTelemetry Documentation: Instrumentation"),
                    Chapter("patterns-08-behavioral", "Design Patterns: Behavioral Design Patterns", "Strategy, state, command, observer, and chain-of-responsibility choices.", "Behavioral patterns organize decisions and transitions. Strategy varies an algorithm, state makes legal transitions visible, command captures an action for retry or audit, observer introduces eventual notification, and a chain can make ordered policy checks explicit.", "An AI request passes through budget, safety, retrieval, and provider policies. The policy chain must stop on a hard rejection and record the reason.", "Model one workflow with a strategy and a state machine, then compare it with a conditional chain; test ordering, rejection, and replay.", "You can choose a behavioral pattern from the change and lifecycle problem rather than its name.", "Add a command log for retryable work and document whether observers are best-effort or part of the transaction.", 90, "Spring Framework Documentation: Events"),
                    Chapter("patterns-09-uml", "UML Diagrams", "Communication diagrams that clarify ownership and runtime behavior.", "UML is valuable when it makes a design review faster: class diagrams show contracts and ownership, sequence diagrams show collaboration and timing, and state diagrams show legal transitions. Avoid diagramming every getter.", "Document a payment plus AI receipt-processing workflow, including synchronous authorization, asynchronous extraction, retry, and manual review states.", "Create a context, sequence, class, and state diagram; annotate external boundaries, failure paths, and transaction ownership.", "A reviewer can follow the request, identify the invariant owner, and spot an unsafe lifecycle transition without reading implementation code.", "Keep the diagrams next to the decision record and update them when a boundary changes.", 60, "PlantUML Documentation"),
                    Chapter("patterns-10-contest", "Contest - 2: Design Principles & Design Patterns", "Timed design selection, modeling, and extensibility review.", "A design contest rewards a small model with clear invariants, not a catalogue of patterns. State the use case, choose one or two patterns only where they reduce a real change cost, and make the trade-offs visible.", "Design a notification platform that supports email, SMS, push, and AI-generated message content with retries, tenant policy, and delivery history.", "Clarify requirements, draw the domain and sequence, implement the core path, inject a failure, and explain how a second channel is added.", "You can defend every interface, pattern, and state transition under interview questioning.", "Write a post-contest review listing the abstraction you would remove if the system remained small.", 120, "Backend Design Interview Practice")
                }),
            new(
                "applied-design-machine-coding",
                "Applied Design & Machine Coding",
                "Interview-style design-to-code practice using small, extensible backend systems.",
                "Module 11",
                6,
                new[]
                {
                    Chapter("machine-01-approach", "How to Approach Design Problems", "Requirement clarification, invariants, APIs, and implementation sequencing.", "A machine-coding solution should move from requirements to a runnable vertical slice. Separate must-have behavior from extensions, identify state transitions, and choose seams for tests before writing classes.", "For a booking or game problem, clarify concurrency, persistence, time, idempotency, and error behavior in the first ten minutes.", "Practice a timed checklist: assumptions, nouns and verbs, invariants, interfaces, happy path, edge cases, tests, and review.", "You can start implementation without guessing silently and can explain what is intentionally out of scope.", "Create a reusable one-page design template for future interviews.", 60, "Software Design Interview Practice"),
                    Chapter("machine-02-design-tictactoe", "Design TicTacToe", "Board state, turn rules, winning lines, and extensible game policy.", "Design starts with invariants: one move per turn, valid coordinates, no move after completion, and a winner determined by the board rules. Keep player identity, board storage, and win detection separately testable.", "Support configurable board size and win length without making the first implementation abstract for every possible game.", "Write the state model, choose an O(1) or incremental win check, define invalid-move errors, and sketch the public game API.", "You can show where the game rejects an illegal move and how a variant can change without rewriting storage.", "Add a draw state and a replay log for deterministic debugging.", 75, "Object-Oriented Design Practice"),
                    Chapter("machine-03-code-tictactoe-1", "Code TicTacToe 1", "Implementing the core model with clear ownership.", "The first coding pass should be small: board, players, turn transition, and a result. Avoid UI or persistence until the domain behavior is deterministic and easy to test.", "A service endpoint calls the game aggregate and returns a move result without reaching into board internals.", "Implement construction validation, move application, turn switching, and unit tests for the happy path and invalid coordinates.", "The core game can be exercised without a framework and cannot expose mutable internal board state.", "Add a fake clock or move number only if it supports a real product requirement.", 90, "Java Collections and Testing Practice"),
                    Chapter("machine-04-code-tictactoe-2", "Code TicTacToe 2", "Winning detection, draw behavior, and safe extension.", "Optimize only after correctness. An incremental win counter can reduce repeated scanning, but it must stay consistent with the board and be tested against a simple reference implementation.", "Handle a concurrent or retried move request so a move is applied once and the game result is stable.", "Add win and draw tests, compare incremental and full-scan detection, and define idempotency for a move command.", "You can explain the complexity of win detection and prove that a completed game cannot accept another move.", "Persist move commands and make replay produce the same final state.", 90, "Java Concurrency and Testing Practice"),
                    Chapter("machine-05-design-parking-lot", "Design Parking Lot", "Spaces, vehicle fit policy, tickets, and allocation rules.", "Separate inventory, allocation policy, ticket lifecycle, and pricing. A parking spot should not know how money is collected, and a pricing policy should not scan every spot.", "Allocate the smallest suitable spot for a vehicle, issue a ticket, and release the spot exactly once when the vehicle exits.", "Define vehicle and spot capabilities, state transitions, allocation indexes, and error outcomes for a full lot or duplicate exit.", "You can add a new vehicle type or pricing policy without changing unrelated domain classes.", "Add reservations and discuss whether they consume capacity immediately or at arrival.", 90, "Object-Oriented Design Practice"),
                    Chapter("machine-06-code-parking-lot", "Code Parking Lot", "Implementing allocation, ticketing, and release behavior.", "The implementation should protect the invariant that one spot has at most one active ticket. Use a repository or in-memory store behind a port so the domain is not coupled to a data structure.", "Two entry requests arrive simultaneously for the final compatible space. The allocation boundary must be explicit even in a single-process interview solution.", "Implement a deterministic allocation policy, ticket service, duplicate-release handling, and tests for capacity and vehicle compatibility.", "You can trace a vehicle from entry to exit and identify where a concurrent deployment needs a database constraint or lock.", "Add a pricing calculator that uses a clock abstraction and supports a grace period.", 120, "Backend Machine Coding Practice"),
                    Chapter("machine-07-design-bookmyshow", "Design BookMyShow", "Shows, seats, holds, bookings, payments, and expiry.", "Seat booking is a state machine with a short-lived hold. Separate catalog reads from transactional seat allocation, and make payment callbacks idempotent so a retry cannot create a second booking.", "A popular show has one remaining seat, several users hold it, and one payment provider times out. The system needs an expiry and recovery path.", "Define aggregates, APIs, hold and booking states, expiration ownership, and the consistency boundary before considering search or recommendations.", "You can explain how a seat moves from available to held to booked and what happens after payment failure.", "Add an outbox event for confirmation and a reconciliation job for stuck payments.", 90, "Distributed Transaction Design"),
                    Chapter("machine-08-code-bookmyshow-1", "Code BookMyShow 1", "Implementing show catalog and seat hold commands.", "Start with one theater and one show. The code should expose a read model for available seats and a command that atomically creates a hold with an expiry time.", "A client retries the hold request because the network response was lost. The same idempotency key must return the original hold.", "Implement repositories, a clock, hold creation, and tests for duplicate requests, expiry, and unavailable seats.", "You can keep catalog reads separate from hold writes and prove that an expired hold becomes available.", "Replace in-memory state with a repository contract without changing the use-case tests.", 120, "Spring Data and Transaction Practice"),
                    Chapter("machine-09-code-bookmyshow-2", "Code BookMyShow 2", "Payment confirmation, booking transitions, and failure recovery.", "A payment callback is an external command and may arrive late, twice, or out of order. The booking state machine should validate the callback and record the provider reference before confirming.", "Payment succeeds after the hold expiry job runs. Define whether the system refunds, reopens the hold, or requires manual review.", "Add callback idempotency, invalid-transition tests, a recovery state, and a deterministic reconciliation command.", "You can defend the order of state changes and explain how a duplicate callback affects the booking.", "Add a payment outbox and compare synchronous confirmation with eventual confirmation UX.", 120, "Payment API Reliability Practice"),
                    Chapter("machine-10-code-bookmyshow-3", "Code BookMyShow 3", "Scaling reads, isolation, and operational visibility.", "Once the core flow is correct, separate a seat-availability read model from the write model. Add indexes and metrics only for observed access patterns, while keeping the booking invariant authoritative.", "Traffic spikes on one show while browsing traffic dominates all other shows. The system needs cache boundaries without caching a stale booking decision as truth.", "Add query pagination, a measured cache, conflict metrics, and a load test that exercises the final-seat race.", "You can identify which data can be stale and which decision must be serialized at the booking boundary.", "Document a rollback and a reconciliation dashboard for expired holds and payment mismatches.", 120, "High-Level Design and Observability Practice"),
                    Chapter("machine-11-design-splitwise", "Design Splitwise", "Expense ownership, split policies, balances, and settlement.", "An expense system needs immutable facts, explicit split rules, and a derived balance view. Do not make a balance the only source of truth; corrections and audit history matter.", "Create a group expense paid by one member and split by exact amounts, percentages, or shares while rejecting totals that do not reconcile.", "Define the expense aggregate, split strategy interface, balance projection, and idempotent settlement command.", "You can add a new split policy without changing the expense lifecycle and can explain how a correction changes balances.", "Add multi-currency boundaries and state where exchange-rate snapshots are stored.", 90, "Object-Oriented Design Practice"),
                    Chapter("machine-12-code-splitwise-1", "Code Splitwise 1", "Implementing expense creation and split validation.", "Keep money values precise and immutable. Validate that participants belong to the group, split totals match the expense, and the payer is represented in the transaction.", "A mobile client retries an expense creation request with the same idempotency key after a timeout.", "Implement exact, equal, and percentage splits, validate rounding, and test duplicate requests and unknown members.", "You can show that every cent is assigned exactly once and that a retry does not create a second expense.", "Add a domain event for a new expense and define when it becomes visible to balance readers.", 120, "Money and Transaction Design Practice"),
                    Chapter("machine-13-code-splitwise-2", "Code Splitwise 2", "Balance projection, settlement, and correction workflows.", "Balances are a projection of expenses and settlements. Rebuildability, idempotent events, and audit records are more valuable than a clever mutable balance map.", "Two settlements race while an expense correction arrives. The system must not lose a settlement or silently rewrite history.", "Build a balance calculator, add settlement commands, replay events, and test correction and duplicate-event scenarios.", "You can reconcile a member's balance from source facts and identify where eventual consistency is acceptable.", "Add a periodic projection rebuild and a report for records that cannot reconcile.", 120, "Event-Driven Backend Practice"),
                    Chapter("machine-14-final", "Machine Coding", "Timed end-to-end implementation and review discipline.", "The final exercise combines design, implementation, tests, and communication. Favor a coherent vertical slice with visible invariants over a broad but unfinished feature set.", "Implement a booking, parking, or expense service in two hours, then handle a retry, concurrent request, external failure, and one operational question.", "Time-box discovery, model the core, implement the happy path, add failure tests, and reserve time for an explicit review.", "A reviewer can run the code, understand the trade-offs, and see evidence for correctness under the chosen constraints.", "Write a retrospective that separates missing requirements from design mistakes and lists the next safe increment.", 120, "Machine Coding Interview Practice")
                }),
            new(
                "ai-first-backend-capstone-primer",
                "AI-First Backend Capstone Project - Primer",
                "The first production-shaped backend slice: Git, Spring APIs, persistence, security, AI services, and AWS delivery.",
                "Module 12",
                7,
                new[]
                {
                    Chapter("primer-01-backend-ai-development", "Intro to Backend Systems & AI-Augmented Development", "Backend boundaries, AI-assisted workflow, and engineering verification.", "AI tools can accelerate exploration and boilerplate, but the engineer remains responsible for requirements, invariants, security, tests, and operational behavior. Start with a small backend boundary and use AI output as a draft to review.", "Build a document-assistant API that accepts a request, validates tenant scope, calls a retrieval or model port, and records an auditable result.", "Write the contract first, ask an AI tool for alternatives, compare the output against invariants, and retain only code you can explain and test.", "You can identify where AI assistance helps and where human verification is mandatory.", "Create a prompt checklist for safe code generation, data handling, and test review.", 60, "NIST AI Risk Management Framework"),
                    Chapter("primer-02-git", "Version Control and Git", "Commits, branches, reviews, and recoverable delivery.", "Git is a coordination and recovery tool. Small commits should express one coherent change, branches should make intent visible, and history should help reviewers understand why a backend decision was made.", "A capstone team needs to introduce an API change while a production fix is being prepared. The history must support review and selective rollback.", "Practice focused commits, rebasing or merging deliberately, resolving a conflict, and recovering a lost change with reflog or a known commit.", "You can explain the state of the working tree and produce a reviewable change without committing generated secrets.", "Add a repository check that rejects credentials and generated build artifacts.", 60, "Git Documentation"),
                    Chapter("primer-03-git-ai-tools", "Learning Git Commands & AI Development Tools", "Safe tool use, diffs, prompts, and repeatable coding loops.", "An AI-assisted loop should be inspectable: read the relevant files, state constraints, make a small change, inspect the diff, and run focused verification. Git diff is the boundary that prevents invisible changes from entering the codebase.", "Use an AI assistant to refactor a Spring service while preserving API behavior and database semantics.", "Ask for a plan, apply one bounded edit, review the diff, compare tests before and after, and record any assumption that remains unverified.", "You can reproduce a change and explain which evidence supports it.", "Create a pull-request template with data-migration, security, and observability checks.", 60, "Git Documentation"),
                    Chapter("primer-04-spring-apis", "Intro to Spring Framework and Building APIs", "Application context, controllers, services, ports, and HTTP contracts.", "A Spring API should keep transport mapping at the edge and business decisions in application or domain services. Constructor injection makes dependencies visible and allows most behavior to be tested without starting the server.", "Implement a `/documents` API with request validation, an application service, a repository port, and an AI extraction port.", "Define request and response DTOs, add a service test with fakes, wire it through Spring, and document error responses.", "You can trace one request from HTTP input to a domain decision without coupling the core to Spring annotations.", "Add an OpenAPI contract and a contract test for validation and error shape.", 90, "Spring Framework Reference Documentation"),
                    Chapter("primer-05-mvc-microservice", "MVC, Requests in Spring and Starting a Microservice", "Request lifecycle, validation, service boundaries, and AI integration seams.", "MVC separates request mapping, application orchestration, and infrastructure. A microservice boundary should own a capability and make its synchronous and asynchronous dependencies explicit.", "Start a document-processing service that validates uploads, stores metadata, and queues extraction rather than holding an HTTP request open for model latency.", "Trace filters, controller, service, repository, and queue boundaries; add timeout and correlation handling; test the service without the web layer.", "You can explain where request validation ends, where business validation begins, and why long AI work should not block a request by default.", "Add an idempotency key for submission and a status endpoint for eventual processing.", 90, "Spring Web MVC Documentation"),
                    Chapter("primer-06-third-party-ai", "Calling 3rd Party APIs & LLM Services", "Timeouts, contracts, redaction, retries, and provider translation.", "External AI APIs are unreliable dependencies with cost, latency, quota, and data-handling constraints. Wrap the SDK behind a port, set explicit deadlines, and translate provider errors into stable application outcomes.", "Call an LLM to classify a support ticket while redacting secrets and retaining a provider request id for troubleshooting.", "Build an adapter with a timeout and bounded retry policy, add a deterministic fake, redact logs, and test rate-limit, malformed-response, and timeout paths.", "You can explain what is safe to retry and how the user learns that the result is pending or degraded.", "Add provider fallback only after defining semantic equivalence and cost limits.", 90, "OpenAI API Safety and Reliability Guidance"),
                    Chapter("primer-07-spring-data", "Intro to Spring Data JPA", "Entity boundaries, repositories, transactions, and query shape.", "Spring Data reduces persistence boilerplate but does not remove data modeling decisions. Keep entities from becoming API DTOs, define transaction ownership, and make repository methods match access patterns.", "Persist document metadata and processing status while the extracted content remains versioned and auditable.", "Model the aggregate, write a repository port, add a transaction boundary, and test duplicate submissions and status transitions.", "You can identify the aggregate root, explain when a transaction ends, and avoid lazy-loading behavior in a response serializer.", "Add an outbox row for a processing job created in the same transaction as the submission.", 90, "Spring Data JPA Documentation"),
                    Chapter("primer-08-jpa-queries", "JPA Queries and Repositories", "Projections, pagination, query plans, and safe repository APIs.", "A repository is a data-access contract, not a synonym for one table. Prefer projections and explicit fetch plans for read endpoints, and inspect generated SQL when query count or shape matters.", "List a tenant's documents with status, latest processing result, and cursor pagination without loading full content or triggering N+1 queries.", "Write a projection, add stable pagination, inspect query count, and test tenant isolation and empty results.", "You can explain the SQL your repository produces and prove that a tenant cannot read another tenant's rows.", "Add a measured index and a query-plan regression note for the hot endpoint.", 90, "Spring Data JPA Documentation"),
                    Chapter("primer-09-unit-testing", "Unit Testing and Good Practices", "Test seams, deterministic time, AI-assisted tests, and failure evidence.", "A useful unit test checks a business outcome at a stable boundary. AI-generated tests can miss negative cases or assert implementation details, so review coverage by invariant, failure mode, and external contract.", "Test document submission, extraction failure, retryable provider errors, and duplicate requests without starting PostgreSQL or calling a real model.", "List invariants, write focused tests, use fakes for ports, add property or parameterized cases, and inspect AI-generated assertions for false confidence.", "You can name what a test proves, what it does not prove, and which integration test is still needed.", "Add a small integration test against a disposable database after the unit suite is trustworthy.", 75, "JUnit 5 User Guide"),
                    Chapter("primer-10-authentication-authorization", "Authentication vs Authorization, OAuth2, JWT", "Identity, claims, scopes, expiry, and resource policy.", "Authentication answers who the caller is; authorization answers what that identity may do to this resource. JWT validation must check issuer, audience, signature, time claims, and key rotation, while authorization remains an application decision.", "A document endpoint must enforce tenant membership and role-based access even when a token is valid.", "Define a token validation boundary, map claims to an identity object, write ownership and role tests, and ensure forbidden responses do not leak data.", "You can distinguish 401 from 403 and explain why decoding a JWT is not authorization.", "Add a key rotation scenario and document revocation or short-lived token behavior.", 90, "Spring Security Reference"),
                    Chapter("primer-11-user-auth-service", "Implementing UserAuthService", "Registration, login, password handling, and account policy.", "An authentication service owns credential lifecycle, not every authorization decision. Passwords must be hashed with an appropriate adaptive function, sessions or tokens must be bounded, and user enumeration should be considered.", "Implement a service that registers a user, authenticates credentials, issues a short-lived access token, and records failed attempts without exposing whether an email exists.", "Separate credential storage from token issuance, inject a clock and hasher, and test lockout, expiry, duplicate registration, and invalid credentials.", "You can trace identity creation and login without logging secrets or coupling the domain to JWT claims.", "Add refresh-token rotation and a recovery flow with an auditable security event.", 90, "OWASP Authentication Cheat Sheet"),
                    Chapter("primer-12-aws-deploy", "Deploying Backend & AI-Enabled Applications to AWS", "Container delivery, configuration, managed data, and operational readiness.", "Deployment is part of the backend contract. Build an image, inject configuration through a secret mechanism, run migrations deliberately, expose health signals, and verify that the AI dependency has a budget and timeout.", "Deploy the capstone API with a managed PostgreSQL database, an object store for documents, and a model provider while keeping credentials outside the image.", "Write a deployment checklist, separate schema migration from reference seeding, add health/readiness checks, and perform a rollback rehearsal.", "You can explain what runs before traffic is accepted and how an operator knows whether the app, database, or AI provider is unhealthy.", "Add a cost alarm and a runbook for model quota exhaustion.", 90, "AWS Well-Architected Framework")
                }),
            new(
                "ai-first-backend-capstone-advanced",
                "AI-First Backend Capstone Project - Advance",
                "Production hardening for resilient APIs, payments, search, distributed services, and containerized delivery.",
                "Module 13",
                8,
                new[]
                {
                    Chapter("advanced-01-resttemplate-resilience", "RestTemplate, Resilience & Handling Failures in AI/API Systems", "Timeouts, retry budgets, circuit breakers, and failure classification.", "Resilience starts with a dependency contract: deadline, retryability, idempotency, fallback, and observability. Retrying an AI or payment call without a request key can multiply side effects.", "An order service calls pricing, payment, and an AI fraud signal provider under one user deadline.", "Classify errors, set per-dependency timeouts, add bounded retries and circuit state, and test a slow or malformed provider.", "You can explain why each failure is retried or surfaced and show that the total work remains bounded.", "Compare synchronous fallback with an asynchronous review queue and define the user-visible state.", 90, "Spring Framework Documentation: HTTP Clients"),
                    Chapter("advanced-02-uuid-inheritance", "UUIDs and Representing Inheritance", "Identifier strategy, aggregate identity, and relational inheritance choices.", "Identifiers should support boundary safety, generation, indexing, and operational debugging. Inheritance in a relational model is a trade-off between shared columns, joins, and polymorphic queries; composition is often clearer for evolving backend capabilities.", "Represent card, wallet, and bank payment attempts with stable ids while keeping provider-specific details out of the common payment record.", "Compare UUID storage choices, model one inheritance strategy and one composition strategy, and test serialization and lookup behavior.", "You can justify identity and inheritance choices from access patterns, not aesthetics.", "Add an external reference separate from the internal id and document privacy or enumeration concerns.", 75, "PostgreSQL Documentation: Data Types"),
                    Chapter("advanced-03-mocking", "Mocking and Writing Unit Tests", "Mock boundaries, interaction risk, and AI-service test doubles.", "Mock a port when the external behavior is expensive, nondeterministic, or unavailable; do not mock every internal method. A fake that models useful behavior is often more valuable than a brittle interaction script.", "Test a payment plus AI decision service with a deterministic provider fake and one contract fixture from the real adapter.", "Replace SDK calls at a port, assert outcomes and important side effects, and add a contract test for provider response translation.", "You can identify an over-mocked test and explain what belongs in unit, integration, and contract suites.", "Add a replayable production failure fixture with sensitive values removed.", 75, "JUnit 5 User Guide"),
                    Chapter("advanced-04-testing-strategies", "Advanced Testing Strategies for Backend Systems", "Contract, integration, property, concurrency, and failure testing.", "Testing strategy follows risk. Unit tests protect decisions, integration tests protect persistence and wiring, contract tests protect boundaries, and load or fault tests reveal behavior under pressure.", "Verify a document pipeline across API, database, queue, and model adapter while keeping provider costs controlled.", "Build a test matrix by invariant and dependency, add a property for idempotency, exercise concurrent requests, and inject a timeout or duplicate event.", "You can show why a test exists and identify the gap left by a passing unit suite.", "Add a small deterministic load test and record the bottleneck instead of optimizing by guesswork.", 90, "OpenTelemetry Documentation: Testing Observability"),
                    Chapter("advanced-05-jwt", "JWT Generation and Validation", "Token claims, signing keys, expiry, rotation, and audience checks.", "JWT is a signed representation of claims, not a session database. Validate the complete contract at the boundary, keep lifetimes short, and do not place mutable authorization truth in a token without a revocation or version strategy.", "Issue an access token for a tenant-scoped user and reject it when issuer, audience, signature, time, or token version is invalid.", "Define claims, generate and validate tokens, rotate a signing key in a test, and test clock skew and expired tokens.", "You can explain which checks are cryptographic and which are business authorization.", "Add a token-version lookup for account disablement and document its latency trade-off.", 75, "OWASP JSON Web Token Cheat Sheet"),
                    Chapter("advanced-06-oauth2", "Authentication - Implementing OAuth 2", "Authorization-code flow, scopes, clients, and resource-server boundaries.", "OAuth2 delegates authorization and identity relationships but does not automatically define your application's permissions. Keep the authorization server, client, and resource server responsibilities distinct.", "A web client obtains delegated access to a user's document service, while the API enforces tenant and resource ownership.", "Draw the flow, validate state and redirect constraints, map scopes to policies, and test missing scope, expired token, and wrong audience.", "You can explain the authorization-code flow and why a resource server must still enforce local authorization.", "Document refresh-token storage and rotation for the chosen client type.", 90, "IETF OAuth 2.0 RFC 6749"),
                    Chapter("advanced-07-ebs-rds", "EBS and RDS", "Durable storage, backups, connection limits, and failure recovery.", "Managed database services remove some operational burden but not capacity planning, backups, network access, migrations, or recovery testing. Storage performance and database connections should be treated as finite resources.", "Run the capstone API against RDS with encrypted storage, private networking, a limited connection pool, and a tested restore procedure.", "Map application data to storage needs, set backup and retention expectations, test a connection spike, and rehearse restore to a new instance.", "You can explain what RDS manages and what the application team still owns.", "Add a migration compatibility check for a rolling deployment.", 75, "AWS RDS Documentation"),
                    Chapter("advanced-08-vpc-security-groups", "VPC, Security Groups, Route 53", "Network boundaries, ingress, egress, and service discovery.", "A secure deployment defines which components can communicate and why. Private subnets, security groups, DNS, and TLS are architecture decisions, not setup details to postpone.", "Expose only the load balancer publicly; allow the API to reach RDS, object storage, queues, and model providers through explicitly documented paths.", "Draw the traffic flows, write least-privilege security rules, test a denied path, and verify DNS and certificate behavior.", "You can trace a request and show which network control prevents an unintended connection.", "Add a failure runbook for DNS propagation and a controlled security-group change.", 90, "AWS VPC Documentation"),
                    Chapter("advanced-09-search", "Implementing Search: Paging, Sorting & Intro to Semantic Search", "Stable pagination, lexical search, embeddings, and relevance boundaries.", "Search has distinct concerns: deterministic retrieval, ranking, freshness, filtering, and semantic similarity. Start with a testable lexical baseline before adding embeddings, and do not treat a vector score as truth.", "Search tenant documents by status and date, then offer semantic retrieval for paraphrased questions while preserving access filters.", "Implement cursor pagination, a lexical query, an embedding adapter, and relevance tests with tenant isolation and empty results.", "You can explain which result is authoritative and how filters are applied before or alongside semantic ranking.", "Add an evaluation set with expected relevant documents and track false positives.", 90, "PostgreSQL Documentation: Full Text Search"),
                    Chapter("advanced-10-payments", "Creating Payment Microservice", "Payment intent lifecycle, idempotency, and provider boundaries.", "Payments need an explicit intent and attempt model. The service owns its state machine, while provider adapters translate external statuses and callbacks without deciding business fulfillment alone.", "Create a payment intent for an order, authorize it once, and make a retry or callback safe.", "Define states, idempotency keys, provider references, timeout outcomes, and reconciliation fields before coding the API.", "You can explain when an order becomes paid and how an uncertain provider result is represented.", "Add a manual-review state with operator actions and audit events.", 90, "Payment Service Reliability Practice"),
                    Chapter("advanced-11-stripe", "Implementing Stripe Payments and Reconciliation", "Provider webhooks, signatures, idempotency, and settlement reconciliation.", "A payment provider's webhook is an untrusted, retryable message. Verify its signature, persist the event id, make processing idempotent, and reconcile provider truth with internal records.", "A charge succeeds but the confirmation response is lost; a webhook arrives twice; a refund is later corrected by the provider.", "Implement signature verification at the adapter boundary, store event ids, map states, and produce a mismatch report.", "You can prove duplicate webhook processing is harmless and identify when finance or support intervention is required.", "Schedule a daily reconciliation against provider exports and define alert thresholds.", 90, "Stripe Webhooks Documentation"),
                    Chapter("advanced-12-redis-kafka", "Optimizing APIs using Redis and Kafka", "Caching, invalidation, event delivery, and backpressure.", "Redis can reduce repeated reads but introduces staleness and eviction behavior. Kafka decouples producers and consumers but introduces offsets, replay, ordering scope, and delivery semantics. Neither replaces a source-of-truth transaction.", "Publish an order event after commit, update a read model, and cache a high-volume product query without serving data across tenants.", "Define cache keys and invalidation, choose an event key, test duplicate and out-of-order events, and expose lag metrics.", "You can explain which guarantee is local, partition-scoped, or eventual and what happens after a consumer restart.", "Add an outbox and dead-letter path with a replay procedure.", 90, "Apache Kafka Documentation"),
                    Chapter("advanced-13-spring-cloud", "Spring Cloud for Distributed Microservices & AI Services", "Configuration, service boundaries, resilience, and distributed operations.", "A microservice is useful when ownership, scaling, or release boundaries justify the operational cost. Shared libraries should not silently couple release cycles; distributed calls need deadlines and trace context.", "Split document intake, extraction, and search only when their scaling or ownership needs differ, keeping the user-visible workflow coherent.", "Define service contracts, timeouts, failure states, configuration ownership, and a trace propagation plan.", "You can explain why a boundary exists and how a request is followed across services.", "Compare a modular monolith with the split architecture and state the evidence needed before extracting a service.", 90, "Spring Cloud Documentation"),
                    Chapter("advanced-14-api-gateway", "Spring Cloud: API Gateway, Load Balancing, Logging & Monitoring", "Routing, edge policy, telemetry, and safe failure behavior.", "An API gateway can centralize routing, authentication checks, rate limits, and correlation, but it should not absorb domain policy. Load balancing needs health semantics and a plan for partial failure.", "Route public document and payment endpoints to separate services while preserving tenant identity, request ids, and meaningful error responses.", "Define routes, apply an edge timeout, propagate trace context, add structured logs and metrics, and test an unhealthy backend.", "You can identify which policy belongs at the edge and which belongs in the service.", "Add a canary route and a rollback signal based on latency and error rate.", 90, "OpenTelemetry Documentation"),
                    Chapter("advanced-15-docker", "Docker for Backend & AI Service Deployment", "Images, layers, configuration, health, and local reproducibility.", "A container image should be reproducible, minimal, and free of secrets. Runtime configuration belongs outside the image, and health checks should distinguish process liveness from dependency readiness.", "Package the capstone API and a worker with separate targets, run them against PostgreSQL, and make a migration or seed step explicit.", "Write a multi-stage image, configure a non-root runtime, add health checks, pin dependencies, and verify the image on the target architecture.", "You can explain what happens during build, startup, migration, seeding, and rollback.", "Add an image scan and a deployment manifest that runs additive reference seeding only after schema readiness.", 75, "Docker Documentation: Get Started")
                }),
            new(
                "production-ai-enabled-system",
                "Build a Production-Ready AI-Enabled System",
                "An applied elective for building, evaluating, and operating AI features inside real backend workflows.",
                "Elective",
                9,
                new[]
                {
                    Chapter("production-01-llm-prompts", "Intro to LLMs for Backend Engineers & Prompt Engineering", "Tokens, context, structured output, prompt contracts, and backend controls.", "A backend engineer should treat a prompt as versioned input to a probabilistic dependency. Define the task, context budget, output schema, refusal behavior, and evaluation cases before optimizing wording.", "Generate a structured support-triage result with category, urgency, rationale, and confidence while keeping customer data scoped and redacted.", "Create a prompt contract, enforce a schema, test adversarial and incomplete inputs, and record model/version metadata.", "You can explain what the model is allowed to decide and what the application must validate.", "Add a prompt version registry and compare changes against a fixed evaluation set.", 75, "NIST AI Risk Management Framework"),
                    Chapter("production-02-bookmyshow-agent-1", "Building BookMyShow Chat Agent - 1", "Intent detection, catalog tools, and read-only conversational flows.", "An agent should call narrow, typed tools rather than inventing catalog facts. Keep the conversation layer separate from the booking state machine and authorize every resource lookup.", "Let a user find movies and showtimes by city and date, returning only data the user is allowed to see.", "Define tool schemas, add deterministic fixtures, validate arguments, and test ambiguous requests and no-result responses.", "You can show that an answer is grounded in a tool response and that a malformed tool call is rejected.", "Add a trace that records tool name and latency without storing unnecessary message content.", 90, "Model Context Protocol Specification"),
                    Chapter("production-03-bookmyshow-agent-2", "Building BookMyShow Chat Agent - 2", "Seat availability, holds, and conversational confirmation.", "The agent may explain options but must not bypass transactional APIs. Confirmation is a domain command with idempotency and state validation, not merely a natural-language response.", "A user asks the agent to reserve seats, then repeats the request after a slow response.", "Connect the agent to a hold API, require explicit confirmation, propagate idempotency, and test a hold expiry and unavailable seat.", "You can separate recommendation from commitment and explain how the booking service remains authoritative.", "Add a human handoff when the request is ambiguous or payment state is uncertain.", 90, "OWASP LLM Application Security"),
                    Chapter("production-04-bookmyshow-agent-3", "Building BookMyShow Chat Agent - 3", "Payment handoff, recovery, guardrails, and evaluation.", "A production agent needs refusal and escalation paths. Payment should move to a trusted flow, sensitive details should not enter prompts, and the agent should recover from tool or provider failures with a clear status.", "A payment succeeds but the model provider times out before the confirmation message is generated.", "Model the workflow states, create failure fixtures, redact sensitive fields, and evaluate both successful and unsafe conversations.", "You can show that a tool failure cannot cause a fabricated booking confirmation.", "Build a regression set from anonymized transcripts and track unsupported claims.", 90, "OWASP LLM Application Security"),
                    Chapter("production-05-splitwise-agent-1", "Building Splitwise AI Receipt Processor - 1", "Document ingestion, extraction, and validation boundaries.", "Receipt processing combines untrusted files, OCR or vision output, and financial facts. Treat extracted fields as suggestions that require schema validation and, where needed, user confirmation.", "Upload a receipt and extract merchant, date, currency, total, and line items without trusting the model to enforce arithmetic.", "Store the original reference, validate MIME and size, call an extraction port, and compare line-item totals with the reported total.", "You can identify which fields are model output and which facts the application verifies.", "Add a quarantine state for malformed or suspicious documents.", 90, "OWASP File Upload Cheat Sheet"),
                    Chapter("production-06-splitwise-agent-2", "Building Splitwise AI Receipt Processor - 2", "Human confirmation, split suggestions, and correction workflows.", "The system should make uncertainty visible. Let a user correct participants, amounts, and currency while preserving the original extraction and the final confirmed expense.", "The receipt model misreads a tax line and suggests an incorrect split; the user edits it before creating an expense.", "Create a review state, show field provenance, validate corrected totals, and make confirmation idempotent.", "You can audit what the model suggested, what the user changed, and what became the financial source of truth.", "Add confidence thresholds that route low-confidence receipts to manual review.", 90, "NIST AI Risk Management Framework"),
                    Chapter("production-07-splitwise-agent-3", "Building Splitwise AI Receipt Processor - 3", "Batch processing, retries, privacy, and cost controls.", "AI pipelines need bounded concurrency, retention rules, retry classification, and cost visibility. A failed extraction should be resumable without duplicating expenses or re-uploading sensitive data unnecessarily.", "Process a burst of receipts with provider rate limits and a user-visible queue while preserving tenant isolation.", "Add a work queue, retry budget, dead-letter state, cost counters, and deletion or retention behavior.", "You can explain backpressure, duplicate prevention, and how an operator recovers a stuck item.", "Add a per-tenant budget and a model fallback policy with quality thresholds.", 90, "OpenTelemetry Documentation"),
                    Chapter("production-08-contest", "Backend Capstone Project: Contest", "End-to-end AI feature delivery, evaluation, and operational review.", "The contest combines a narrow user outcome with a dependable backend. Assess correctness, safety, latency, cost, observability, and recovery instead of rewarding a demo that only succeeds on a happy prompt.", "Deliver either a grounded booking assistant or receipt processor with real persistence, an explicit human fallback, and a reproducible evaluation set.", "Write the product contract, implement the critical path, test adversarial and provider failure cases, measure latency and cost, and present the trade-offs.", "You can demonstrate that the system does not fabricate business facts and can recover when the model or downstream service is unavailable.", "Create a launch checklist and a post-launch review with the first metrics you would watch.", 150, "NIST AI Risk Management Framework")
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

## Self-Check (From Class Material)

**Q1.** Consider the following statements:
i. Calling of overloaded methods is decided at compile time
ii. Calling of overridden methods is decided at runtime.
Which of the following is correct?
- A. Both are correct
- B. Both are incorrect
- C. i is correct, ii is incorrect
- D. i is incorrect, ii is correct

**Answer: A** — Overloaded method resolution is performed statically by the compiler based on parameter signatures, while overridden method invocation is dispatched dynamically by the JVM at runtime based on the actual object instance.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 5; answer determined from source material, not marked in original)*

**Q2.** Which of the following does Java not support?
- A. Method overriding
- B. Method overloading
- C. Operator overloading
- D. Method hiding

**Answer: C** — Java natively supports method overriding, method overloading, and static method hiding, but intentionally does not support programmer-defined operator overloading.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 7; answer determined from source material, not marked in original)*

**Q3.** What is true about static methods?
i. They can be overloaded
ii. They can be overridden
Which of the following is correct?
- A. Both are correct
- B. Both are incorrect
- C. i is correct, ii is incorrect
- D. i is incorrect, ii is correct

**Answer: C** — Static methods belong to the class rather than an instance; they can be overloaded with different parameter signatures, but cannot be polymorphically overridden (redefining them in a subclass results in method hiding).
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 7; answer determined from source material, not marked in original)*

**Q4.** Consider the following classes:
```java
public class P {
  protected int d1 = 10;
  protected int d = 100;

  protected void fun1(){
    System.out.println(""P's fun1"");
  }
  protected void fun(){
    System.out.println(""P's fun"");
  }
  static protected void sfun(){
    System.out.println(""P's sfun"");
  }
}

public class C extends P {
  protected int d2 = 20;
  protected int d = 200;

  protected void fun2(){
    System.out.println(""C's fun2"");
  }
  protected void fun(){
    System.out.println(""C's fun"");
  }
  static protected void sfun(){
    System.out.println(""C's sfun"");
  }
}
```
If client code does `P obj = new C(); obj.display();` where `display()` prints `d1`, `d`,
then calls `fun1()`, `fun()`, `sfun()` — what is the output?
- A. Compile Time Error
- B. 10 100 P's fun1 C's fun P's sfun
- C. 100 100 P's fun1 C's fun P's sfun
- D. 10 10 P's fun1 C's fun P's sfun

**Answer: B** — Fields are never polymorphic in Java; `obj.d1` and `obj.d` resolve by the
*reference type* (`P`), so both read `P`'s fields (10, 100) regardless of the actual object
being a `C`. `fun1()` is not overridden in `C`, so it prints `P's fun1`. `fun()` **is**
overridden, and instance methods dispatch dynamically on the *actual object type* (`C`), so
it prints `C's fun`. `sfun()` is `static`, so it is hidden, not overridden — static calls
resolve at compile time by reference type (`P`), printing `P's sfun`.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 60; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** Consider the following about interface data-members:
1. They are final
2. They are static
Which of the following is true?
- A. Both are correct
- B. Both are incorrect
- C. i is correct, ii is incorrect
- D. i is incorrect, ii is correct

**Answer: A** — All fields declared in a Java interface are implicitly `public static final` constants.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 1; answer determined from source material, not marked in original)*

**Q2.** Consider the following two statements:
1. Abstract classes should necessarily have abstract methods
2. Classes having abstract methods should be abstract
Which of the following is true?
- A. Both are correct
- B. Both are incorrect
- C. i is correct, ii is incorrect
- D. i is incorrect, ii is correct

**Answer: D** — An abstract class is not required to declare any abstract methods (it may contain only concrete methods to prevent instantiation), but any class that contains at least one abstract method must be declared abstract.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 9; answer determined from source material, not marked in original)*

**Q3.** Which keyword is used to make a non-inheritable class in Java?
- A. static
- B. abstract
- C. final
- D. finally

**Answer: C** — Applying the `final` keyword to a class declaration prevents any other class from extending it.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 9; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** Consider the following two statements:
i. Runnable interface is implemented by class which will be invoked via a separate Thread
ii. The name of the function to start a new Thread is run
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both a and b are false

**Answer: B** — Statement i is true; statement ii is false because the method to start a new concurrent thread is `start()`. Calling `run()` directly merely executes the method synchronously on the calling thread.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 11; answer determined from source material, not marked in original)*

**Q2.** Consider the following two statements:
1. Threads of same process can access each other's stack data
2. Threads of same process can access each other's global data
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both a and b are false

**Answer: C** — Each thread has its own private call stack and local variable storage, while global, static, and heap data is shared across all threads within the same process.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 7; answer determined from source material, not marked in original)*

**Q3.** Consider the following two statements:
1. Parallel programming requires multiple program counters
2. Concurrent programming requires time-bound CPU scheduling
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both a and b are false

**Answer: A** — Parallel execution requires multiple physical CPU cores executing instructions simultaneously (each with its own hardware Program Counter), whereas concurrency on a single core relies on time-sliced CPU scheduling and context switching.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 1; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** Consider the following two statements:
i. ExecutorService.submit returns a Future object
ii. The method name to receive a value from Future object is get.
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both a and b are false

**Answer: A** — `ExecutorService.submit()` returns a `Future` instance representing the pending asynchronous computation, and `.get()` blocks the calling thread until the computed value is available.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 9; answer determined from source material, not marked in original)*

**Q2.** Consider the following two statements:
1. The responsibility of the Executor is to decide how to run different tasks on different threads
2. The responsibility of class implementing Callable is to define a task to be done on a separate thread
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both a and b are false

**Answer: A** — `Executor` manages thread lifecycle, pooling, and task scheduling, while a `Callable` implementation encapsulates the specific computation and return value of the task itself.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 1; answer determined from source material, not marked in original)*

**Q3.** Consider the following two statements:
1. Executor manages the assignment of tasks to threads within the thread pool.
2. Waiting Queue holds the tasks that couldn't be assigned to threads in the thread pool.
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both a and b are false

**Answer: A** — An Executor assigns queued tasks to available worker threads in the pool, while the internal waiting queue holds tasks when all pool threads are currently busy.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 2; answer determined from source material, not marked in original)*

**Q4.** Consider the following two statements:
1. Runnable interface is used to create classes that run on a separate thread and return values to the main thread.
2. Callable interface is used to create classes that run on a separate thread and don't need to return values to the main thread.
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both a and b are false

**Answer: D** — Both statements have it backwards: `Runnable.run()` returns `void` and
cannot return a value to the caller, while `Callable<V>.call()` is specifically designed to
return a typed value `V`. Neither statement correctly describes its interface.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 8; answer determined from source material, not marked in original)*

**Q5.** Consider the following two statements:
1. A class implementing Callable<Integer> will have a call function that returns integer
2. To get a value from a class implementing Callable<Integer>, we can use Future<Integer>
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both are false

**Answer: A** — `Callable<Integer>.call()` is declared to return `Integer`, and submitting
that `Callable` to an `ExecutorService` returns a `Future<Integer>` whose `.get()` retrieves
the computed value once ready.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 10; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** What is the name of the algorithm used by Atomic Data types for thread-safety?
- A. Mark and Sweep
- B. Binary Search
- C. Compare and Swap
- D. None of the above

**Answer: C** — Atomic classes (such as `AtomicInteger`) achieve lock-free thread safety using the hardware-level Compare-And-Swap (CAS) instruction.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 1; answer determined from source material, not marked in original)*

**Q2.** Which of the following statements about mutex locks in Java is true?
- A. Mutex locks are used to achieve parallel execution of threads.
- B. Mutex locks are synonymous with atomic data types in Java.
- C. Mutex locks are used to protect critical sections of code from concurrent access.
- D. Mutex locks are only applicable to single-threaded programs

**Answer: C** — A mutex lock enforces mutual exclusion, ensuring that only one thread can execute within a protected critical section at any given time.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 3; answer determined from source material, not marked in original)*

**Q3.** Which of the following statements is true about the synchronized keyword?
- A. It can only be applied to instance methods
- B. It can be applied to both instance methods and static methods
- C. It can only be applied to static methods
- D. It cannot be used in a multithreaded application

**Answer: B** — The `synchronized` keyword can be applied to instance methods (locking the instance `this`), static methods (locking the `Class` object), and standalone synchronized blocks.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 6; answer determined from source material, not marked in original)*

**Q4.** Which of the following is true regarding the differences between Hashtable and
ConcurrentHashMap in Java?
- A. Hashtable allows multiple threads to access different parts of the map at the same time, while ConcurrentHashMap does not.
- B. ConcurrentHashMap is synchronized, while Hashtable is not.
- C. Hashtable is synchronized, ConcurrentHashMap is not.
- D. ConcurrentHashMap allows multiple threads to access different parts of the map at the same time, while Hashtable does not.

**Answer: D** — `Hashtable` synchronizes on the entire map for every operation, allowing
only one thread in at a time. `ConcurrentHashMap` uses finer-grained internal locking
(segment/bucket-level), letting multiple threads operate on different parts of the map
concurrently.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 5; answer determined from source material, not marked in original)*

**Q5.** Consider the following class:
```java
public class A {
  synchronized static void fun1(){}
  synchronized void fun2(){}
  void fun3(){}
}
```
And client code creating `A obj1 = new A();` and `A obj2 = new A();`. Which pair of calls
CANNOT execute concurrently?
- A. obj1.fun1() and obj1.fun2()
- B. obj1.fun1() and obj2.fun1()
- C. obj2.fun2() and obj2.fun3()
- D. obj1.fun2() and obj2.fun2()

**Answer: B** — `fun1()` is `static synchronized`, so it locks the shared `Class` object
(`A.class`), not any particular instance. Both `obj1.fun1()` and `obj2.fun1()` compete for
that one class-level lock regardless of which instance calls it, so they cannot run
concurrently. `fun2()` is an instance-level lock, so different instances (`obj1`/`obj2`)
calling it are unaffected by each other.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 2; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** Which of the following statements is true regarding mutex locks and semaphores?
- A. Mutex Locks are used for synchronization while Semaphores is a syntax for creating threads
- B. Mutex Locks allow only 1 thread in critical section while Semaphores can allow multiple threads in the critical section at same time
- C. Lock and unlock are methods of semaphores
- D. Acquire and release are methods of mutex locks

**Answer: B** — A mutex restricts critical section access to at most one thread, whereas a counting semaphore maintains a permit count allowing multiple threads to enter simultaneously up to its capacity limit.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 4; answer determined from source material, not marked in original)*

**Q2.** Which of the following methods in a Semaphore is a blocking method?
- A. acquire
- B. release
- C. Both acquire and release
- D. Neither acquire nor release

**Answer: A** — `acquire()` blocks the calling thread if no permits are available (permit count is 0), whereas `release()` increments the permit count and never blocks.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 3; answer determined from source material, not marked in original)*

**Q3.** Consider the following two statements:
1. Release method of Semaphores increases the number of threads allowed in the critical section by 1.
2. If the value of Semaphore is 0, Release method of Semaphores blocks the thread
Which of the following is true?
- A. Only 1 is true
- B. Only 2 is true
- C. Both 1 and 2 are true
- D. Both 1 and 2 are false

**Answer: A** — Statement 1 is true because `release()` increments the permit count; statement 2 is false because `release()` is a non-blocking operation that unblocks waiting threads rather than blocking itself.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 8; answer determined from source material, not marked in original)*

**Q4.** Consider the following two statements:
a. If the value of a Semaphore is greater than 0, `acquire()` reduces the permit count by 1 but allows the thread to enter the critical section.
b. If the value of a Semaphore is 0, `acquire()` blocks the thread.
Which of the following is true?
- A. Only a is true
- B. Only b is true
- C. Both a and b are true
- D. Both a and b are false

**Answer: C** — Both statements correctly describe `acquire()`'s behavior: when permits
remain, it decrements the count and lets the thread proceed immediately; when the permit
count has reached zero, it blocks the calling thread until another thread calls
`release()`.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 1; answer determined from source material, not marked in original)*

**Q5.** Which of the following is true about the critical section of a correctly working
producer-consumer problem using two semaphores (a producer semaphore tracking empty slots,
a consumer semaphore tracking filled slots)?
- A. Critical section of producer should begin with acquire on producer semaphore and end with release on consumer semaphore
- B. Critical section of producer should begin with acquire on producer semaphore and end with release on producer semaphore
- C. Critical section of consumer should begin with acquire on producer semaphore and end with release on consumer semaphore
- D. Critical section of consumer should begin with acquire on consumer semaphore and end with release on consumer semaphore

**Answer: A** — A producer must first `acquire()` an empty slot (the producer semaphore),
then after producing, `release()` the consumer semaphore to signal that a new item is
available. Signaling the *other* semaphore, not your own, is what lets the two sides
coordinate.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 7; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** What does T denote in the following code:
```java
public class Box<T> {
  // class implementation
}
```
- A. Type parameter
- B. Generic instance
- C. Class name
- D. Class type

**Answer: A** — `T` is a formal type parameter that serves as a placeholder for the concrete type specified when the `Box` class is instantiated.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 64; answer determined from source material, not marked in original)*

**Q2.** What is the purpose of using bounded wildcards in Java generics?
- A. To allow any type to be passed as an argument
- B. To restrict the type of objects that can be used
- C. To enforce type safety in generic classes
- D. To simplify the syntax of generic declarations

**Answer: B** — Bounded wildcards (like `? extends Number` or `? super Integer`) restrict the acceptable type arguments to a specific inheritance hierarchy for controlled reading or writing.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 62; answer determined from source material, not marked in original)*

**Q3.** When is it appropriate to use wildcards with an upper bound in Java generics?
- A. To allow any type as a method parameter
- B. When the method should work with specific subclasses
- C. When the method should work with any object type
- D. To specify a lower limit on the allowed types

**Answer: B** — Upper-bounded wildcards (`? extends SuperType`) are used when a method needs to operate on a collection of elements belonging to any subclass of a given supertype (read-only producer operations).
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 10; answer determined from source material, not marked in original)*

**Q4.** Suppose you are writing a generic method to return the first element of a list.
What is the correct method declaration?
- A. `public static <T> T getFirstElement(List<T> list)`
- B. `public static T getFirstElement(List<T> list)`
- C. `public static void getFirstElement(List<T> list)`
- D. `public static <T> void getFirstElement(List<T> list)`

**Answer: A** — A generic static method must declare its own type parameter `<T>`
immediately before the return type, since static members have no access to a class-level
type parameter. The return type must also be `T`, not `void`, since the method returns the
first element.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 49; answer determined from source material, not marked in original)*

**Q5.** What does the `extends` keyword signify in the context of Java generics (e.g.
`<T extends Number>`)?
- A. It specifies a lower bound for a type parameter.
- B. It restricts the use of wildcard types.
- C. It indicates inheritance for a generic class.
- D. It denotes an upper bound for a type parameter.

**Answer: D** — In a generic type-parameter declaration, `extends` denotes an upper bound:
`T` must be that type or a subtype of it. This is distinct from wildcard usage but relies on
the same ""extends = upper bound"" idea.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 59; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** Consider the following two statements about Vector, ArrayList and LinkedList:
1. Both vector and arraylist are dynamic arrays but the vector is thread-safe while arraylist is not
2. Both arraylist and linkedlist can grow dynamically but memory in an arraylist is contiguous while not so in linkedlist
Which of the following is correct?
- A. Both 1 and 2 are true
- B. Only 1 is true
- C. Only 2 is true
- D. Both 1 and 2 are false

**Answer: A** — Statement 1 is true because `Vector` synchronizes its methods for thread safety while `ArrayList` is unsynchronized; statement 2 is true because `ArrayList` uses contiguous array memory while `LinkedList` allocates disconnected heap nodes linked by pointers.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 4; answer determined from source material, not marked in original)*

**Q2.** Which of the following require the elements passed to implement Comparable interface?
- A. HashSet
- B. ArrayDeque
- C. TreeSet
- D. Stack

**Answer: C** — `TreeSet` requires elements to implement `Comparable` (or have an explicit `Comparator` provided) to maintain its internal Red-Black tree sorted order.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 4; answer determined from source material, not marked in original)*

**Q3.** What should go inside <> if you want to write a generic compare method?
```java
public static <____> int compareTo(T a, T b) {
    return a.compareTo(b);
}
```
- A. T
- B. ?
- C. T extends Comparable
- D. T extends Comparator

**Answer: C** — Declaring `<T extends Comparable<T>>` bounds the type parameter `T` to types that implement `Comparable`, enabling the method body to invoke `.compareTo()`.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 3; answer determined from source material, not marked in original)*

**Q4.** Which of the following is thread-safe?
- A. ArrayList
- B. HashMap
- C. Hashtable
- D. LinkedList

**Answer: C** — `Hashtable` synchronizes every method internally, making it thread-safe
(though coarse-grained and slower under contention). `ArrayList`, `HashMap`, and
`LinkedList` are all unsynchronized by default.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 46; answer determined from source material, not marked in original)*

**Q5.** Which of the following classes doesn't implement the `List` interface (directly or
indirectly)?
- A. Vector
- B. Stack
- C. ArrayList
- D. PriorityQueue

**Answer: D** — `Vector`, `Stack` (which extends `Vector`), and `ArrayList` all implement
`List`. `PriorityQueue` implements the `Queue` interface instead — it is backed by a binary
heap and does not offer indexed `List` access.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 5; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** Output of above code:
```java
public class LambdaExample {
  public static void main(String[] args) {
    IntFunction<Integer> square = x -> x * x;
    System.out.println(square.apply(5));
    
    BinaryOperator<Integer> addition = (x, y) -> x + y;
    System.out.println(addition.apply(10, 20));
    
    Function<Integer, Integer> increment = x -> x + 1;
    System.out.println(increment.apply(7));
  }
}
```
- A. 25 30 8
- B. 25 30 7
- C. 5 30 7
- D. Compile Error

**Answer: A** — `square.apply(5)` computes $5 \times 5 = 25$, `addition.apply(10, 20)` computes $10 + 20 = 30$, and `increment.apply(7)` computes $7 + 1 = 8$.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 10; answer determined from source material, not marked in original)*

**Q2.** Which of the following is a terminal function in streams api?
- A. map
- B. filter
- C. foreach
- D. none of the above

**Answer: C** — `forEach` is a terminal operation that triggers pipeline execution; `map` and `filter` are lazy intermediate operations.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 6; answer determined from source material, not marked in original)*

**Q3.** In the above code, Function, BinaryOperator, IntFunction are types of:
```java
IntFunction<Integer> square = x -> x * x;
BinaryOperator<Integer> addition = (x, y) -> x + y;
Function<Integer, Integer> increment = x -> x + 1;
```
- A. Lambda Expressions
- B. Functional Interfaces
- C. Functions
- D. Classes

**Answer: B** — `IntFunction`, `BinaryOperator`, and `Function` are standard functional interfaces provided in the `java.util.function` package.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 52; answer determined from source material, not marked in original)*

**Q4.** What does the following code snippet do?
```java
Set<String> uniqueFruits = fruits.stream()
  .collect(Collectors.toSet());
System.out.println(""Result: "" + uniqueFruits);
```
- A. Removes duplicate fruits from the list.
- B. Creates a set of all fruit names.
- C. Concatenates all fruits into a single string.
- D. Compile Error.

**Answer: B** — `Collectors.toSet()` collects the stream elements into a `Set<String>`.
Deduplication is a natural consequence of the `Set` contract, but the collector's direct
action is building that set, not ""removing duplicates"" as a separate step.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 8; answer determined from source material, not marked in original)*

**Q5.** Which of the following comparators will sort a list of strings in descending order
according to length?
- A. `Comparator<String> c = (s1, s2) -> Integer.compare(s2.length(), s1.length());`
- B. `Comparator<String> c = (s1, s2) -> s2.length() - s1.length();`
- C. `Comparator<String> c = Comparator.comparingInt(String::length).reversed();`
- D. All of the above

**Answer: D** — All three are valid, equivalent ways of expressing a descending-by-length
comparator: two hand-written lambda forms (integer subtraction and `Integer.compare` for
overflow safety) and one built from the fluent `Comparator.comparingInt(...).reversed()`
API.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 8; answer determined from source material, not marked in original)*
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

## Self-Check (From Class Material)

**Q1.** What does the following code snippet do?
```java
Map<Integer, List<String>> groupedByLength = fruits.stream()
    .collect(Collectors.groupingBy(String::length));
```
- A. Creates a map where keys are fruit lengths and values are fruit names.
- B. Creates a map where keys are fruit names and values are fruit length.
- C. Counts the total number of fruits.
- D. Compile Error.

**Answer: A** — `Collectors.groupingBy(String::length)` classifies elements by their string length, returning a `Map<Integer, List<String>>` where each key is a word length and the value is the list of matching fruits.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 8; answer determined from source material, not marked in original)*

**Q2.** Which of the following stream methods return a boolean?
- A. findFirst
- B. filter
- C. allMatch
- D. collect

**Answer: C** — `allMatch` is a short-circuiting terminal operation that returns a `boolean` indicating whether all elements match the given predicate.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/34-44.md, MCQ 10; answer determined from source material, not marked in original)*

**Q3.** What does the following code snippet do?
```java
String result = fruits.stream()
  .collect(Collectors.joining("", ""));
```
- A. Concatenates all fruits into a single string.
- B. Creates a list of fruits.
- C. Calculates the total length of all fruits.
- D. Compilation Error.

**Answer: A** — `Collectors.joining("", "")` is a terminal collector that concatenates the stream of fruit strings into a single delimited `String`.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 55; answer determined from source material, not marked in original)*

**Q4.** Which of the following is NOT a way of creating a stream?
- A. `Stream.of()`
- B. `list.stream()`
- C. `Stream.iterate()`
- D. `stream.collect()`

**Answer: D** — `Stream.of()`, `list.stream()`, and `Stream.iterate()` all *create* a
stream. `collect()` is a terminal operation that *consumes* an existing stream and produces
a result — it does not create a new stream.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 6; answer determined from source material, not marked in original)*
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
