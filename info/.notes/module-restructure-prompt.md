# Neuralascent — Java LLD Module Restructure Prompt

## Context (Read Before Acting)

You are modifying the seed data for the Neuralascent learning platform. This is a C# ASP.NET Core project backed by PostgreSQL. The seed data is in `api/Data/JavaVerticalSeedData.cs`. You must read that file fully before writing any changes.

**Do not invent content. Do not add explanation prose. Do not write lesson body text unless this prompt explicitly provides the exact text to use. Every change you make must be traceable to a specific instruction below.**

---

## Step 1 — Read These Files First (Mandatory)

Read the full content of these files before writing any code:

1. `api/Data/JavaVerticalSeedData.cs` — you will modify this file
2. `api/Models/` — scan for the `CourseModule` and `Lesson` model definitions to confirm field names

Do not proceed past Step 1 until you have read both.

---

## Step 2 — Understand the Current State

After reading `api/Data/JavaVerticalSeedData.cs`, confirm you can see:

- A course with slug `java-spring-lld`
- 4 modules created inside `if (course == null)` block:
  - Module 1: slug `oop-foundations`, `OrderIndex = 1`, Title = "OOP Foundations & Design Principles"
  - Module 2: slug `concurrency-multithreading`, `OrderIndex = 2`, Title = "Concurrency & Multithreading"
  - Module 3: slug `advanced-java-collections`, `OrderIndex = 3`, Title = "Advanced Java, Collections & Streams"
  - Module 4: slug `spring-enterprise-architecture`, `OrderIndex = 4`, Title = "Spring Boot & Enterprise Architecture"
- 4 private static seed methods: `SeedModule1Lessons`, `SeedModule2Lessons`, `SeedModule3Lessons`, `SeedModule4Lessons`
- `SeedModule4Lessons` seeds 4 Spring Boot lessons with slugs: `14-spring-boot-core`, `15-spring-data-jpa`, `16-spring-rest-api`, `17-machine-coding-capstone`

If what you read does not match this description, stop and report the discrepancy. Do not proceed.

---

## Step 3 — The Target State

After your changes, the `java-spring-lld` course must have exactly **6 modules** in this order:

| OrderIndex | Slug | Title | Lessons |
|---|---|---|---|
| 1 | `oop-foundations` | "OOP Foundations & Design Principles" | **UNCHANGED** — do not touch |
| 2 | `concurrency-multithreading` | "Concurrency & Multithreading" | **UNCHANGED** — do not touch |
| 3 | `advanced-java-collections` | "Advanced Java, Collections & Streams" | **UNCHANGED** — do not touch |
| 4 | `design-principles-patterns` | "Design Principles & Patterns for Extensible Systems" | **NEW** — 4 stub lessons (see §4A) |
| 5 | `applied-machine-coding` | "Applied Design & Machine Coding" | **NEW** — 6 stub lessons (see §4B) |
| 6 | `spring-enterprise-architecture` | "Spring Boot & Enterprise Architecture" | **MOVED** — same 4 Spring lessons, OrderIndex updated to 6 |

---

## Step 4 — Changes to Make

### 4A — Add Module 4: Design Principles & Patterns

**Module definition** (add inside the existing `if (course == null)` block, after `mod3`, before `mod4`):

```csharp
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
```

**Seed call** — add immediately after `SeedModule3Lessons(db, mod3.Id);`:
```csharp
SeedModule4Lessons(db, mod4.Id);
```

**Lesson method** — rename the current `SeedModule4Lessons` to `SeedModule6Lessons`, then add this new method named `SeedModule4Lessons`:

```csharp
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
```

---

### 4B — Add Module 5: Applied Design & Machine Coding

**Module definition** (add inside `if (course == null)` block, after `mod4`, before the old `mod4` which is now `mod5Spring`):

```csharp
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
```

**Seed call** — add after `SeedModule4Lessons(db, mod4.Id);`:
```csharp
SeedModule5Lessons(db, mod5.Id);
```

**Lesson method** — add this new method `SeedModule5Lessons`:

```csharp
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
}
```

---

### 4C — Move Spring Module to Position 6

**In the `if (course == null)` block:**

- Change the existing Spring module variable (previously `mod4`) to be named `mod6Spring`
- Update its `OrderIndex` to `6`
- Update its `Badge` to `"Module 6"`
- The call becomes `SeedModule6Lessons(db, mod6Spring.Id);`

The Spring module definition should now read:

```csharp
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
```

**Rename** the existing `SeedModule4Lessons` method that seeds Spring Boot content to `SeedModule6Lessons`. Change only the method name — do not change any lesson content, slugs, descriptions, or ContentBody text inside it. The lesson slugs inside will remain `14-spring-boot-core`, `15-spring-data-jpa`, `16-spring-rest-api`, `17-machine-coding-capstone` — do not renumber them.

---

### 4D — Add Idempotent UPDATE Block for Existing Databases

The `if (course == null)` guard means the module creation runs only on a fresh database. For an already-seeded database, add an **idempotent update block** that runs unconditionally — outside and after the `if (course == null)` block.

Add this block immediately after the closing `}` of `if (course == null)`:

```csharp
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

    // Ensure Module 4 (design-principles-patterns) exists
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
        SeedModule4Lessons(db, designModule.Id);
    }

    // Ensure Module 5 (applied-machine-coding) exists
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
        SeedModule5Lessons(db, machineModule.Id);
    }
}
```

---

## Step 5 — Output Instructions

Output the **complete, final `JavaVerticalSeedData.cs` file** with all changes applied.

- Do not summarise. Do not write partial diffs. Output the full file from `using System;` to the final closing `}`.
- Preserve every existing comment, using statement, namespace declaration, and method that this prompt does not explicitly ask you to change.
- Match the code style exactly: 4-space indentation, double quotes for strings, verbatim string literals (`@"..."`) only where already used in the file for `ContentBody` values, `string.Empty` for truly empty strings.
- The method order in the file after your changes must be:
  1. `Seed`
  2. `GetVerticalTasks`
  3. `SeedModule1Lessons`
  4. `SeedModule2Lessons`
  5. `SeedModule3Lessons`
  6. `SeedModule4Lessons` *(new — Design Principles)*
  7. `SeedModule5Lessons` *(new — Applied Machine Coding)*
  8. `SeedModule6Lessons` *(renamed from old SeedModule4Lessons — Spring)*
  9. All remaining methods unchanged (`EnsureStandaloneExpandedCourses`, `EnsureStandaloneExpandedCourse`, `GetExpandedModules`, `SeedLesson3StudyGuide`, `BackfillLessonContent`, etc.)

---

## Step 6 — Self-Check Before Outputting

Before outputting, verify:

- [ ] Module 1, 2, 3 definitions and their seed calls are unchanged
- [ ] Module 4 is `design-principles-patterns` at `OrderIndex = 4`, Badge = "Module 4"
- [ ] Module 5 is `applied-machine-coding` at `OrderIndex = 5`, Badge = "Module 5"
- [ ] Module 6 is `spring-enterprise-architecture` at `OrderIndex = 6`, Badge = "Module 6"
- [ ] `SeedModule4Lessons` seeds exactly 4 lessons with slugs: `14-solid-principles`, `15-creational-patterns`, `16-structural-patterns`, `17-behavioural-patterns-uml`
- [ ] `SeedModule5Lessons` seeds exactly 6 lessons with slugs: `18-how-to-approach-design`, `19-machine-coding-tictactoe`, `20-machine-coding-parking-lot`, `21-machine-coding-bookmyshow`, `22-machine-coding-splitwise`, `23-machine-coding-contest`
- [ ] `SeedModule6Lessons` (Spring) is the renamed version of the old `SeedModule4Lessons` — lesson content inside is byte-for-byte identical, only the method name changed
- [ ] The idempotent UPDATE block is present and runs outside the `if (course == null)` guard
- [ ] No lesson content was invented beyond what this prompt specifies (all ContentBody text in the new methods is exactly as written in §4A and §4B above)
- [ ] The file compiles: no unclosed braces, no duplicate method names, no missing semicolons

If any check fails, fix it before outputting.
