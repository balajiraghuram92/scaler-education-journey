using System;
using System.Collections.Generic;
using System.Linq;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Data;

public static class JavaVerticalSeedData
{
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
            ContentBody = @"# Lesson 1 — Intro to LLD for Scalable Systems
## Concepts Covered
- **High-Level Design (HLD)**: Architecture diagrams, microservices boundaries, database choices, load balancers, caching layers.
- **Low-Level Design (LLD)**: Class diagrams, design patterns, schemas, interfaces, thread safety, and method contracts.
- **Scaling Axes**: Vertical scaling (bigger compute) vs Horizontal scaling (more nodes).
- **Procedural vs Object-Oriented**: Moving from centralized state mutation to localized state and encapsulated behaviors."
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
            "01-intro-to-lld" => @"# Lesson 1 — Intro to LLD for Scalable Systems

## Concepts Covered
Low-Level Design is the practice of turning a business capability into dependable objects, interfaces, state transitions, and failure boundaries. It sits below an HLD service diagram: the HLD may say that an order service owns checkout, while the LLD explains how an `Order`, `PaymentAttempt`, `InventoryReservation`, and `OrderRepository` collaborate without leaking persistence or transport concerns.

Separate responsibilities before writing classes. A controller translates an HTTP request, an application service coordinates a use case, domain objects protect invariants, and adapters talk to databases or external systems. Prefer composition when behavior varies independently; use inheritance only when the subtype really satisfies the parent contract. Scaling concerns also appear in LLD: immutable values reduce coordination, idempotency prevents duplicate work, and bounded interfaces make later horizontal scaling safer.

## Practical Backend Scenario
Design the first slice of a ride-booking quote service. A `QuoteService` receives a pickup, destination, vehicle type, and request id. It asks a distance provider for route facts, applies a pricing policy, and returns an immutable quote with an expiry time. The HTTP layer should not calculate fares or know whether distance came from a cache or a remote provider. If the same request id arrives twice, the application boundary should return the same quote rather than create two independent negotiations.

## Practice Loop
1. Write the use-case sentence and list the invariants that must always hold.
2. Draw the collaborators and mark which ones are domain objects, ports, or adapters.
3. Implement the smallest happy path with constructor validation and no framework annotations.
4. Add duplicate requests, provider timeout, expired quote, and unsupported vehicle tests.
5. Review each public method: can it be called in an invalid order, and who owns that rule?

## Evidence of Understanding
You can explain why the controller does not own pricing, identify the boundary that makes a quote idempotent, and change the distance provider without editing the pricing policy. Your tests demonstrate that invalid state cannot be constructed and that a timeout becomes a deliberate application outcome rather than an accidental stack trace.

## Suggested Extension
Add a `QuoteRepository` port and two adapters: an in-memory implementation for tests and a PostgreSQL implementation for production. Compare the design before and after introducing the persistence boundary.
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
