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
}
