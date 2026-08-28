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
            Title = "Lesson 2 — OOP-1: Intro to OOP Lab",
            Description = "Hands-on foundation lab covering classes, objects, state encapsulation, and instance methods.",
            LectureNumber = 2,
            ClassDate = "2026-06-21",
            HorstmannRef = "Core Java Vol I Ch. 4 §4.4",
            EstimatedMinutes = 45,
            IsCompleted = true,
            OrderIndex = 2,
            ContentBody = @"# Lesson 2 — OOP-1: Intro to OOP Lab
*Note: Foundation lab covering Java class anatomy, reference types, heap vs stack memory allocation, and constructors.*"
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
            ContentBody = @"# Lesson 3 — OOP-2: Access Modifiers, Encapsulation & Inheritance

## Concepts Covered
- **Access Modifiers**: `private`, package-private, `protected`, and `public` controlling field and method visibility.
- **Encapsulation**: Bundling state and behavior together while preventing unrestricted external mutation.
- **Constructor Chaining**: Using `this(...)` to delegate to a single canonical constructor.
- **Inheritance (`extends`)**: Declaring IS-A relationships and constructor delegation with `super(...)`.
- **`final` Keyword**: Freezing variable references, locking methods against overrides, and sealing classes against subclassing.
- **Copy Semantics**: Deep copy vs shallow copy, and defending object invariants at API boundaries.
- **`equals()` & `hashCode()` Contract**: Symmetry under subclassing, hash bucket consistency, and `getClass()` vs `instanceof`."
        };
        db.Lessons.Add(lesson3);
        db.SaveChanges();

        // Add the 5 Practice Problems for Lesson 3
        SeedLesson3Problems(db, lesson3.Id);

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

    private static void SeedLesson3Problems(StudyTrackerContext db, int lessonId)
    {
        // Problem 1: Immutable Fare
        db.Problems.Add(new Problem
        {
            LessonId = lessonId,
            Slug = "prb1-immutable-fare",
            Title = "1. Immutable Fare",
            Difficulty = "Warm-up",
            PackageName = "com.assignment.prb1",
            TestClassName = "FareTest",
            OrderIndex = 1,
            IsCompleted = true,
            ProblemStatement = @"On a ride-hailing platform the business rule is absolute: *the fare shown on screen when the rider taps Accept is the fare they are charged.* It must not be possible for any other code, anywhere in the system, to change that number afterwards.

A `Fare` object with a `setSurgeMultiplier()` method is a loaded gun. Some far-away service recalculates surge, mutates the shared `Fare`, and the rider who accepted ₹180 is billed ₹375.

Your job is to make that bug impossible to write, using the compiler rather than a code-review convention.",
            RequirementsBody = @"### Structure
- The class must be declared `final`.
- Every instance field must be `private` **and** `final`.
- The class must expose **no** method whose name starts with `set`.

### Data Members
- `baseFare` (`double`, `private final`)
- `surgeMultiplier` (`double`, `private final`)
- `currency` (`String`, `private final`)

### Constructor & Validation
`Fare(double baseFare, double surgeMultiplier, String currency)`
Reject with `IllegalArgumentException`:
- `baseFare < 0`
- `surgeMultiplier < 1.0` (surge can raise a fare, never lower it)
- `currency` is null, empty, or whitespace

### Methods
- `getBaseFare()`: `double`
- `getSurgeMultiplier()`: `double`
- `getCurrency()`: `String`
- `getTotalFare()`: `baseFare * surgeMultiplier`
- `withSurge(double newSurge)`: Returns a **new** `Fare` instance with same baseFare and currency, and the given surge. Receiver remains untouched.
- `toString()`: Exactly `Fare{baseFare=150.00, surgeMultiplier=1.20, currency='INR', total=180.00}`",
            WorkedExample = @"```java
Fare accepted = new Fare(150.0, 1.2, ""INR"");
accepted.getTotalFare();          // 180.0

Fare surged = accepted.withSurge(2.0);
surged.getTotalFare();            // 300.0
accepted.getTotalFare();          // still 180.0  <-- immutable!
```",
            Hints = @"- Use `String.format(""%.2f"", value)` for formatting decimals in `toString()`.
- `withSurge` creates a new instance rather than modifying `this`.
- Marking the class `final` prevents subclass mutability leaks."
        });

        // Problem 2: Driver Onboarding
        db.Problems.Add(new Problem
        {
            LessonId = lessonId,
            Slug = "prb2-driver-onboarding",
            Title = "2. Driver Onboarding",
            Difficulty = "Easy–Mid",
            PackageName = "com.assignment.prb2",
            TestClassName = "DriverTest",
            OrderIndex = 2,
            IsCompleted = true,
            ProblemStatement = @"Drivers get onboarded through three different flows: full onboarding, partner app onboarding, and bulk CSV import.

The naive answer is three constructors, each doing its own initialisation. That works right up until someone adds a fourth field and updates only some constructors, shipping silent bugs.

Your job is to write three constructors so that **all initialisation happens in exactly one place** and the other two delegate to it.",
            RequirementsBody = @"### Structure & Fields
- Every instance field must be `private`.
- `driverId` (`String`) must additionally be `final`.
- `getDriverId()` must be declared `final`.
- `name` (`String`), `rating` (`double`), `phone` (`String`), `isOnline` (`boolean` - starts `false`).
- One `static int` counter tracking total onboarded drivers.

### Constructors
- `Driver(String driverId, String name, double rating, String phone)` — The primary constructor. Validates, assigns fields, sets `isOnline = false`, and increments the static counter.
- `Driver(String driverId, String name)` — Delegates via `this(...)` with rating `0.0`, phone `null`.
- `Driver(String driverId)` — Delegates via `this(...)` with name `""Unknown""`, rating `0.0`, phone `null`.

### Methods
- `goOnline()`, `goOffline()`, `isOnline()`
- `updateRating(double newRating)`: Valid range 0.0 to 5.0 inclusive. Outside throws `IllegalArgumentException` and old rating is preserved.
- `static int getTotalDriversOnboarded()`
- `static void resetOnboardedCount()`
- `equals` / `hashCode` by `driverId` only.
- `toString()`: `Driver{driverId='D001', name='Rahul', rating=4.8, online=false}`",
            WorkedExample = @"```java
Driver.resetOnboardedCount();

Driver full    = new Driver(""D001"", ""Rahul"", 4.8, ""9876543210"");
Driver partial = new Driver(""D002"", ""Priya"");
Driver bulk    = new Driver(""D003"");

Driver.getTotalDriversOnboarded();  // 3
partial.getRating();   // 0.0
bulk.getName();        // ""Unknown""
```",
            Hints = @"- `this(...)` calls another constructor of the same class and must be the very first statement.
- Only the canonical 4-argument constructor increments the static counter."
        });

        // Problem 3: Vehicle Hierarchy
        db.Problems.Add(new Problem
        {
            LessonId = lessonId,
            Slug = "prb3-vehicle-hierarchy",
            Title = "3. Vehicle Hierarchy",
            Difficulty = "Mid",
            PackageName = "com.assignment.prb3",
            TestClassName = "VehicleHierarchyTest",
            OrderIndex = 3,
            IsCompleted = true,
            ProblemStatement = @"The platform dispatches cars, autos, and bikes. All three have an id, a plate, a seating capacity, registration logic, and fare calculation. The only thing that genuinely differs is the per-kilometre rate and number of seats.

Pull the shared parts into a parent class `Vehicle`. Let each child (`Car`, `Auto`, `Bike`) supply only its differences.",
            RequirementsBody = @"### `Vehicle` (Parent)
- Fields (`private`): `vehicleId` (String), `licensePlate` (String), `seatingCapacity` (int).
- `public static final List<String> CONSTRUCTION_LOG = new ArrayList<>();`
- Constructor `Vehicle(String vehicleId, String licensePlate, int seatingCapacity)`: assigns fields, then logs `""Vehicle:"" + vehicleId`.
- `public final String getVehicleId()`
- `protected double getBaseRate()`: returns `0.0`; overridden by children.
- `public double calculateFare(double km)`: returns `km * getBaseRate()`. Throws `IllegalArgumentException` on negative km.
- `public String register()`: `""Vehicle V001 registered successfully.""`
- `equals` / `hashCode` using `vehicleId` and `getClass()`.

### Children (`Car`, `Auto`, `Bike`)
- `Car`: 4 seats, base rate 12.0
- `Auto`: 3 seats, base rate 8.0
- `Bike`: 1 seat, base rate 5.0
- Constructors call `super(...)`, then log `""Car:"" + vehicleId` etc.
- Overrides `protected double getBaseRate()`.
- **Must NOT declare own vehicleId/plate/seats fields or override calculateFare.**

### `DispatchService`
- `static double totalFare(List<Vehicle> fleet, double km)`
- `static int totalSeatingCapacity(List<Vehicle> fleet)`
- `static Vehicle cheapest(List<Vehicle> fleet, double km)`",
            WorkedExample = @"```java
Vehicle.CONSTRUCTION_LOG.clear();
Car car = new Car(""V001"", ""KA01AB1234"");
// CONSTRUCTION_LOG: [""Vehicle:V001"", ""Car:V001""]

car.calculateFare(10.0);  // 120.0 (10 * 12.0)
car.getSeatingCapacity(); // 4
```",
            Hints = @"- `super(...)` must be the first line in child constructors.
- Dynamic method dispatch ensures `Vehicle.calculateFare` calls child's overridden `getBaseRate()`."
        });

        // Problem 4: Trip Copy Semantics
        db.Problems.Add(new Problem
        {
            LessonId = lessonId,
            Slug = "prb4-trip-copy-semantics",
            Title = "4. Trip Copy Semantics",
            Difficulty = "Mid–Hard",
            PackageName = "com.assignment.prb4",
            TestClassName = "TripCopyTest",
            OrderIndex = 4,
            IsCompleted = true,
            ProblemStatement = @"Support needs to snapshot a trip before applying a correction, so the original stays intact for the dispute record.

`copy.route = original.route` does not copy a `Route` — it copies an *address*. Both trips then point at the same `Route`, and editing the snapshot mutates the original.

Your job is to implement copy constructors and defensive copying correctly.",
            RequirementsBody = @"### `Money` (Immutable)
- `final` class with `private final double amount` and `private final String currency`.
- `equals`/`hashCode` by value; `toString()` -> `""INR 300.00""`.

### `Route` (Mutable)
- Fields: `source` (String), `destination` (String), `distanceKm` (double).
- Getters and setters for all three.
- Copy constructor `Route(Route other)`.

### `Trip`
- Fields: `tripId` (String), `fare` (Money - immutable), `route` (Route - mutable), `waypoints` (List<String> - mutable).
- Primary constructor `Trip(...)`: copies `Route` and `waypoints` defensively on the way IN.
- Copy constructor `Trip(Trip other)`:
  - `route`: deep copied (`new Route(other.route)`)
  - `waypoints`: deep copied (`new ArrayList<>(other.waypoints)`)
  - `fare`: **shared reference** (because Money is immutable!).
- `getWaypoints()` returns `Collections.unmodifiableList(...)`.
- `static Trip shallowCopyForDemo(Trip other)`: deliberately wrong demo sharing the same Route.",
            WorkedExample = @"```java
Route route = new Route(""Koramangala"", ""Whitefield"", 18.5);
Trip original = new Trip(""T001"", new Money(300.0, ""INR""), route, Arrays.asList(""Domlur"", ""Marathahalli""));

Trip snapshot = new Trip(original);
snapshot.getRoute().setDestination(""Hebbal"");

original.getRoute().getDestination(); // ""Whitefield"" (safe!)
snapshot.getFare() == original.getFare(); // true (shared reference)
```",
            Hints = @"- Mutable fields need deep copy; immutable fields should share references.
- Protect mutable collections on exit using `Collections.unmodifiableList()`."
        });

        // Problem 5: The equals/hashCode Contract
        db.Problems.Add(new Problem
        {
            LessonId = lessonId,
            Slug = "prb5-equals-hashcode-contract",
            Title = "5. The equals/hashCode Contract",
            Difficulty = "Hard",
            PackageName = "com.assignment.prb5",
            TestClassName = "EqualsHashCodeContractTest",
            OrderIndex = 5,
            IsCompleted = true,
            ProblemStatement = @"Dispatch keeps a running log of every driver's trips in a `HashMap<Driver, List<String>>`. In production, trips start vanishing — a driver's log is written, then read back a moment later as empty.

The cause is a broken `equals`/`hashCode` pair. A `HashMap` uses `hashCode()` to find the bucket and only then uses `equals()` inside it.

This problem asks you to get the entire contract right: reflexivity, symmetry under subclassing, null-safety, and keeping mutable fields out of the hash.",
            RequirementsBody = @"### `Driver`
- `driverId` (`private final String`), `name` (`String`), `rating` (`double`).
- Getters for all; setters for `name` and `rating` (**no `setDriverId`**).
- `equals` and `hashCode` by `driverId` **only**.
- Use strict `getClass() != obj.getClass()` check to enforce symmetry with subclasses.

### `PremiumDriver extends Driver`
- Adds `loungeAccess` (`boolean`) and `hasLoungeAccess()`.
- Does NOT override `equals`/`hashCode` (inherits from Driver).
- Must NEVER equal a plain `Driver`, even with matching `driverId`.

### `DriverTripLog`
- Wraps `HashMap<Driver, List<String>>`.
- `void logTrip(Driver driver, String tripDescription)`: appends trip description.
- `List<String> getTrips(Driver driver)`: returns unmodifiable list; empty list if driver not found.
- `int getDriverCount()`, `int getTotalTripCount()`.",
            WorkedExample = @"```java
DriverTripLog log = new DriverTripLog();
Driver d1 = new Driver(""D001"", ""Rahul"", 4.8);
log.logTrip(d1, ""Koramangala to Whitefield"");

Driver d2 = new Driver(""D001"", ""Rahul"", 4.8);
log.getTrips(d2); // [""Koramangala to Whitefield""]

d1.setName(""Rahul Kumar"");
log.getTrips(d1); // still found! Name is not in hashCode.
```",
            Hints = @"- Use `Objects.equals(a, b)` and `Objects.hash(driverId)`.
- Use `getClass()` instead of `instanceof` to preserve symmetric equality across subclasses."
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

        // Lesson 3 predates this authoring pass but is already a detailed lesson with
        // linked practice problems and a study guide. Do not replace it.
        if (content.Length >= 900 && content.Contains("## Concepts Covered", StringComparison.Ordinal))
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
            "02-oop-1-intro-lab" => @"# Lesson 2 — OOP-1: Intro to OOP Lab

## Concepts Covered
An object combines state with the operations that are allowed to change that state. A class is a definition; an object is a runtime instance with identity, fields, and behavior. In Java, references point to heap objects, while local variables and call frames belong to an executing thread. This distinction explains why assigning one reference to another does not copy the object.

Start a model with meaningful nouns and verbs, then make invalid transitions difficult to express. A constructor should establish the minimum valid state. Methods should represent business actions such as `reserve`, `cancel`, or `confirm`, rather than expose setters for every field. Keep data accessors small and make the object responsible for rules that belong to its own state.

## Practical Backend Scenario
Model a delivery order moving from `CREATED` to `ASSIGNED`, `PICKED_UP`, and `DELIVERED`. The order owns its status transition rules; a caller cannot move a delivered order back to created by mutating a public field. A `DeliveryAddress` value is validated once at construction. The application service coordinates the courier and notification ports but does not directly rewrite the order status.

## Practice Loop
1. List the fields, valid initial state, and allowed transitions.
2. Implement a small immutable value object and a stateful aggregate with private fields.
3. Write tests for a valid transition, an invalid transition, and a repeated command.
4. Inspect the heap-reference behavior by assigning two variables to one object and then using a separate copy.
5. Refactor any public setter into a named business operation or remove it.

## Evidence of Understanding
You can distinguish identity from value, explain why two references can mutate the same object, and show where the order prevents an illegal state transition. Your tests prove that construction rejects invalid addresses and that command methods report invalid status changes explicitly.

## Suggested Extension
Add an event such as `OrderDelivered` without allowing the event publisher to mutate the aggregate. Keep the event payload immutable and verify that a retry does not publish the same delivery twice.
",
            "04-oop-3-polymorphism-interfaces" => @"# Lesson 4 — OOP-3: Polymorphism & Interfaces

## Concepts Covered
Polymorphism lets application code depend on a stable contract while different implementations provide behavior. An interface expresses a capability; an abstract class is useful when related implementations share protected mechanics or invariant checks. Dynamic dispatch selects the overriding implementation at runtime, which makes a collection of interface values useful without a chain of type checks.

Design interfaces around a consumer need. A `PaymentAuthorizer` should expose authorization behavior, not every detail of a gateway SDK. Keep interfaces small enough to fake in a unit test, and use default methods only for behavior that is genuinely safe for every implementation. Substitution means an implementation must honor the timing, error, nullability, and side-effect promises of the contract, not merely compile against it.

## Practical Backend Scenario
An order service supports card, wallet, and bank-transfer payments. It depends on `PaymentAuthorizer`, while `CardAuthorizer`, `WalletAuthorizer`, and `BankTransferAuthorizer` implement the contract. A registry selects the implementation by payment method. The service handles a declined authorization uniformly, while each adapter translates provider-specific responses at its own boundary.

## Practice Loop
1. Define a minimal interface from the use case rather than from a concrete SDK.
2. Implement two real strategies and one deterministic fake for tests.
3. Add an abstract base only if it removes duplicated invariant logic without hiding important behavior.
4. Test dispatch through the interface reference, including a provider timeout and a declined payment.
5. Replace any `instanceof` branch that is really a missing polymorphic operation.

## Evidence of Understanding
You can explain the difference between a type relationship and shared implementation, demonstrate dynamic dispatch through a collection of payment strategies, and show that the application service remains unchanged when a new payment method is added. Your tests assert contract behavior rather than implementation details.

## Suggested Extension
Add a `PaymentAuthorizerFactory` with explicit registration and validation for duplicate method names. Keep the factory separate from the payment adapters so composition remains visible at startup.
",
            "05-oop-4-lms-lab" => @"# Lesson 5 — OOP-4: Library Management System Lab

## Concepts Covered
This lab combines encapsulation, composition, interfaces, value objects, and policy objects in one small domain. Separate catalog data from lending transactions: a `BookCopy` has inventory identity, a `Member` has borrowing policy, and a `Loan` records a time-bounded agreement. A `Library` coordinates the use case but should delegate rules such as eligibility, due-date calculation, and fine calculation to focused collaborators.

Model state transitions explicitly. A copy can be available, on loan, reserved, or under repair; a loan can be open, returned, or overdue. Avoid a collection of booleans that permits contradictory combinations. Use a repository interface for persistence and keep the aggregate independent of SQL, HTTP, and framework annotations.

## Practical Backend Scenario
A branch library receives a request to lend a particular edition. The service checks member eligibility, locks or atomically reserves one available copy, creates a loan, and emits a notification after the transaction succeeds. Two simultaneous requests must not lend the same copy. Returning a book calculates the fine from a clock abstraction so the rule is deterministic in tests.

## Practice Loop
1. Write the aggregate boundaries and a state diagram for copies and loans.
2. Implement the happy path with in-memory repositories and explicit domain errors.
3. Add concurrent checkout, duplicate return, unknown member, and overdue-fine tests.
4. Introduce interfaces for clock, notification, and persistence only at real boundaries.
5. Review the design for public setters, boolean state combinations, and hidden repository calls.

## Evidence of Understanding
You can trace a checkout from API command to domain decision and persistence without mixing responsibilities. Your tests prove that a copy cannot be loaned twice, a return is idempotent, and a fine calculation does not depend on the wall clock during a unit test.

## Suggested Extension
Add a reservation queue with a clear ordering rule and publish `CopyAvailable` only after a successful return. Document what happens if notification delivery is delayed.
",
            "06-concurrency-1-threads" => @"# Lesson 6 — Concurrency 1: Processes, Threads & Context Switching

## Concepts Covered
A process owns an address space and operating-system resources; threads within it share heap state but have independent stacks and execution positions. A context switch saves one execution context and restores another, so more threads do not automatically mean more throughput. Blocking I/O, CPU work, thread creation, scheduler decisions, and memory visibility all affect the useful concurrency of a backend.

`Runnable` describes work without a return value, while `Callable` can return a value or fail. Thread interruption is a cooperative cancellation signal, not a forced kill. Code that catches `InterruptedException` should either propagate it or restore the interrupt flag. Shared mutable state must have an ownership or synchronization story before a thread is introduced.

## Practical Backend Scenario
An order endpoint needs to create a payment audit record and enqueue a notification. A naive implementation starts a raw thread per request, causing unbounded growth during a traffic burst and making failures invisible to the request lifecycle. Replace it with an explicit execution boundary, a bounded queue, and a clear decision about which work must finish before the HTTP response.

## Practice Loop
1. Sketch process, thread, heap, and stack ownership for the service.
2. Run a small task with `Runnable`, then repeat with interruption and a slow dependency.
3. Measure throughput and latency while varying task count and queue capacity.
4. Add cancellation, exception reporting, and graceful shutdown behavior.
5. Identify every shared field and write down its visibility and ownership rule.

## Evidence of Understanding
You can explain why a raw thread per request is unsafe, distinguish CPU-bound from I/O-bound work, and show how an interruption reaches a task. Your service has a bounded lifecycle and does not silently lose a background exception during shutdown.

## Suggested Extension
Add request correlation data to the task without using a mutable global. Verify that cancellation does not leave a half-written audit record.
",
            "07-concurrency-2-executors" => @"# Lesson 7 — Concurrency 2: Executors, Thread Pools & Callable/Future

## Concepts Covered
An executor separates task submission from thread management. A pool has a worker policy, queue policy, rejection policy, and shutdown contract; all four matter in production. Fixed pools protect a dependency with a known concurrency budget, while work-stealing pools suit many small CPU tasks with different trade-offs. A `Future` represents a result that may not be ready, and waiting on it at the wrong layer can erase the benefit of concurrency.

Bound every fan-out. A pool that accepts unlimited work merely moves overload into memory. Timeouts need an owner, and cancellation must be propagated to the task and the downstream client where possible. Always close or shut down executors that the application owns, and expose metrics for active workers, queue depth, rejected work, and task duration.

## Practical Backend Scenario
A profile endpoint fetches account, recommendation, and loyalty data. It uses separate bounded executors because recommendation work is CPU-heavy while the other calls are I/O-bound. The application waits only until the response deadline, cancels unfinished work, and returns a partial response only when the product contract permits it.

## Practice Loop
1. Implement a `Callable` that returns a typed result and a task that fails predictably.
2. Compare a fixed pool with an unbounded queue and a bounded queue under burst load.
3. Add a deadline, cancellation, and a rejection response to the caller.
4. Test shutdown while tasks are queued, running, and blocked on I/O.
5. Record pool metrics and use them to explain whether the bottleneck is CPU, I/O, or queueing.

## Evidence of Understanding
You can choose a pool from workload characteristics, explain why queue capacity is part of the reliability design, and prove that a timeout does not leave work running indefinitely. Your tests distinguish task failure from executor failure and verify graceful shutdown.

## Suggested Extension
Build a small fan-out coordinator that returns the fastest acceptable result while cancelling the rest. Document the consistency trade-off of that choice.
",
            "08-concurrency-3-synchronization" => @"# Lesson 8 — Concurrency 3: Synchronization, Race Conditions & Locks

## Concepts Covered
A race condition occurs when the result depends on an unsafe interleaving of operations. Mutual exclusion protects a critical section, while visibility ensures one thread can observe another thread's completed write. `synchronized` provides an intrinsic monitor; `ReentrantLock` adds features such as timed acquisition and multiple conditions, but also adds responsibility to unlock in a `finally` block.

Lock only the invariant that needs protection. Holding a lock across a network call increases contention and can create deadlocks when another component acquires locks in a different order. Prefer immutable values, atomic operations, or ownership transfer when they make the state simpler. A correct design states which lock guards which fields and in what order locks may be acquired.

## Practical Backend Scenario
Two checkout requests try to reserve the final seat for an event. A check-then-update sequence without synchronization lets both requests succeed. Protect the reservation invariant, keep external payment calls outside the critical section, and use a database constraint or transactional boundary as the final authority when multiple service instances are involved.

## Practice Loop
1. Write a deliberately racy counter and reproduce the failure with many workers.
2. Fix it with `synchronized`, then compare an atomic counter and a lock-based design.
3. Add a two-resource transfer test that exercises lock ordering and interruption.
4. Use timeouts and thread dumps to diagnose a stalled lock rather than guessing.
5. Document visibility, ownership, lock scope, and the cross-instance database guarantee.

## Evidence of Understanding
You can separate a thread-local fix from a distributed correctness guarantee, identify the exact invariant a lock protects, and explain why a network call should not happen while holding that lock. Your tests demonstrate both the race and the corrected behavior.

## Suggested Extension
Add optimistic versioning to the reservation record and compare conflict handling with in-memory locking when two application instances process the same seat.
",
            "09-concurrency-4-semaphores" => @"# Lesson 9 — Concurrency 4: Semaphores & Bounded Buffer

## Concepts Covered
A semaphore controls access to a finite number of permits. It is useful when several operations may proceed concurrently but a downstream resource has a hard capacity. A binary semaphore can resemble a mutex, but a semaphore does not require the releasing thread to be the acquiring thread. A bounded buffer combines producer and consumer coordination with backpressure so memory usage cannot grow without limit.

Permit acquisition belongs at the boundary of the scarce resource. Always release a permit in a `finally` block, define what happens when no permit is available, and include cancellation in the wait. Fairness can reduce starvation but may reduce throughput, so make the choice explicit. A semaphore inside one process does not coordinate separate service replicas.

## Practical Backend Scenario
The service may make only eight concurrent calls to a partner shipping API. Incoming jobs enter a bounded queue, workers acquire a permit before the remote call, and the permit is released after the response or timeout. When the queue is full, the system applies backpressure instead of accepting work it cannot complete within its deadline.

## Practice Loop
1. Implement a producer-consumer buffer with explicit capacity and shutdown markers.
2. Add a semaphore around a fake slow dependency and verify the maximum in-flight count.
3. Test permit timeout, task interruption, downstream failure, and worker shutdown.
4. Compare reject, block, and shed-load policies when the buffer is full.
5. Explain why the local permit count is not a replacement for a distributed rate limiter.

## Evidence of Understanding
You can calculate the capacity represented by each permit, prove that permits are not leaked on exceptions, and show how bounded queues create backpressure. Your metrics expose queue depth, wait time, and in-flight calls.

## Suggested Extension
Add a token-bucket limiter for a multi-instance deployment and explain which guarantees remain local and which are shared.
",
            "10-java-adv-1-generics" => @"# Lesson 10 — Generics & Type Erasure

## Concepts Covered
Generics move type errors to compilation and let APIs express what they accept and return. A generic class or method can be reused without casts, while bounded wildcards describe variance at the point of use. The PECS rule is a useful shorthand: a producer of values is usually `? extends T`, and a consumer is usually `? super T`.

Java implements generics through type erasure for most runtime code. This means a type parameter is not generally available for `instanceof`, generic arrays are restricted, and overloads that erase to the same signature are illegal. Bridge methods may be generated by the compiler to preserve polymorphism after erasure. These constraints should shape API design rather than be discovered through a production cast failure.

## Practical Backend Scenario
An event bus accepts `DomainEvent` values and routes them to handlers. `EventHandler<T>` should preserve the relationship between an event type and its payload at compile time, while a registry needs a deliberate strategy for runtime type tokens because erased generic parameters cannot identify `T` by themselves. A typed pagination wrapper similarly prevents a repository from returning an unvalidated mixture of records.

## Practice Loop
1. Implement a generic `Page<T>` with immutable items, total count, and cursor metadata.
2. Write producer and consumer utilities using `extends` and `super`, then let the compiler guide misuse.
3. Demonstrate one type-erasure limitation and redesign it with a `Class<T>` token.
4. Remove an unsafe cast from the event bus and add a compile-time test case.
5. Review public generic names and bounds for clarity at the call site.

## Evidence of Understanding
You can choose a wildcard from how a collection is used, explain why a generic type is unavailable at runtime, and design a typed repository API without raw collections. Your code contains no unchecked cast that could be replaced by a better boundary.

## Suggested Extension
Add a sealed event hierarchy and a handler registry that rejects duplicate runtime event types during startup.
",
            "11-java-adv-2-collections-lab" => @"# Lesson 11 — Collections Lab & Sorting

## Concepts Covered
Collection choice is a domain and workload decision. `ArrayList` is strong for indexed reads and append-heavy sequences, `HashMap` provides expected constant-time key lookup, `TreeMap` maintains sorted keys with logarithmic operations, and `PriorityQueue` exposes the next highest-priority item rather than the whole collection in sorted order. Hashing, equality, memory layout, and access patterns matter more than memorizing labels.

`Comparable` defines a type's natural order; `Comparator` defines a context-specific order. Comparators must be transitive and consistent enough for the collection being used. A mutable key in a hash-based collection can become unreachable after its hash changes, so identity fields used for keys must be stable.

## Practical Backend Scenario
A dispatch service keeps drivers by id, selects the nearest eligible driver, and maintains a queue of urgent jobs. Use a map for identity lookup, a priority queue for the next job, and a separate scoring structure if the selection rule changes frequently. Do not sort the entire fleet for every request when a bounded or indexed strategy can answer the question directly.

## Practice Loop
1. Implement the dispatch operations with three candidate collection designs.
2. Generate realistic data and measure lookup, insertion, selection, and memory behavior.
3. Add comparator tests for ties, null policy, transitivity, and stable tie-breaking.
4. Mutate a key after insertion in a safe experiment and explain the lookup failure.
5. Document why the chosen structure matches the access pattern and consistency needs.

## Evidence of Understanding
You can justify a collection from operations and constraints, write a comparator that remains transitive under ties, and recognize when a benchmark is needed instead of relying on folklore. Your tests cover empty, duplicate, and large-input cases.

## Suggested Extension
Add a cache with a bounded size and eviction order. Compare insertion-order, access-order, and explicit priority semantics.
",
            "12-java-adv-3-lambdas-streams" => @"# Lesson 12 — Lambdas & Functional Streams

## Concepts Covered
Lambdas provide behavior as a value for a functional interface. A stream is a lazy pipeline over a source, not a collection that stores another result. Intermediate operations describe a transformation; a terminal operation starts traversal. `map` changes one value into another, `flatMap` removes nested structure, `filter` narrows values, and `collect` materializes a result.

Keep stream pipelines readable and side-effect-light. A lambda should not silently mutate shared state, depend on execution order, or perform an expensive remote call inside an innocent-looking transformation. Parallel streams are not a free thread pool and are especially risky around blocking I/O. `Optional` can clarify a return value that may be absent, but it should not replace every nullable field or be used as a method parameter by default.

## Practical Backend Scenario
A reconciliation job reads payment records, removes duplicates by provider reference, filters settled entries, converts them to ledger commands, and groups the result by merchant. The stream performs in-memory transformations; database writes happen in a controlled batch boundary so retries, transaction size, and failure reporting remain visible.

## Practice Loop
1. Build the pipeline in named stages and inspect the type after each transformation.
2. Add duplicate, missing, malformed, and empty input cases.
3. Replace a side-effecting `forEach` with a collector or an explicit loop when the operation is stateful.
4. Compare sequential execution with a measured parallel experiment only for CPU-bound work.
5. Decide where absence becomes a domain result, an exception, or a filtered record.

## Evidence of Understanding
You can explain when a stream executes, why `flatMap` is needed for nested data, and where side effects make a pipeline unsafe. Your reconciliation output is deterministic, testable, and does not hide database writes inside a transformation.

## Suggested Extension
Add a custom collector for a balanced reconciliation summary and verify its behavior with sequential and parallel accumulation tests.
",
            "13-java-adv-4-streams-exceptions" => @"# Lesson 13 — Streams in Depth & Exception Architecture

## Concepts Covered
Collectors such as `groupingBy`, `partitioningBy`, `mapping`, and `toMap` express aggregation, but duplicate-key and null policies must be explicit. `flatMap` is useful for nested orders or line items, while `mapMulti` can avoid temporary collections in hot paths. Exception architecture should distinguish programmer errors, invalid input, transient dependency failures, and domain rejections so callers can choose retry, correction, or escalation.

Checked exceptions document recoverable boundaries but can make functional pipelines noisy. Do not wrap every failure in a generic runtime exception and lose the original category. Translate exceptions at the adapter or application boundary, preserve the cause, and attach stable error codes. `try`-with-resources closes `AutoCloseable` resources in reverse order and retains suppressed failures, which is safer than hand-written cleanup.

## Practical Backend Scenario
A nightly settlement job reads paginated statements, flattens transactions, groups them by merchant, and writes a reconciliation report. A malformed record is quarantined with its source reference, a database timeout causes the batch to retry, and a duplicate provider reference becomes a conflict report rather than silently overwriting a map entry.

## Practice Loop
1. Define an exception taxonomy and the boundary that translates each category.
2. Implement grouping with an explicit duplicate-key merge policy.
3. Add a resource that fails on read and close; inspect the primary and suppressed exceptions.
4. Test partial batch failure, retry safety, malformed records, and empty input.
5. Review logs for stable identifiers and absence of sensitive payment data.

## Evidence of Understanding
You can choose between rejecting, quarantining, retrying, and compensating for a failure. Your collector cannot silently lose duplicate data, your resources close deterministically, and callers receive an error contract that is useful without exposing implementation details.

## Suggested Extension
Add a dead-letter output for quarantined records and make the retry command idempotent by storing a batch execution key.
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
