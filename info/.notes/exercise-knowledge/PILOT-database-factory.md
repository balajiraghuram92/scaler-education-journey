---
exerciseId: java-lld-creational-database-factory
lessonSlug: 15-creational-patterns
title: Factory Design Pattern for Database Connections
language: java
difficulty: intermediate
estimatedMinutes: 40
concepts:
  - simple-factory
  - abstract-classes
  - enum-dispatch
  - polymorphic-return-types
  - open-closed-principle
prerequisites:
  - inheritance
  - abstract-methods
  - enums
sourceArchive: 1773391484_86d37a1e94ef71c7/Database_factory-solution
tutorPolicy:
  revealSolutionWhen: learnerPassedTests OR learnerExplicitlyDemandsAnswerTwice
  hintOrder: [L1, L2, L3]
---

# Factory Design Pattern for Database Connections

## 1. Problem (learner-facing)

You are building an application that needs to connect to a database. Depending on the
database type (MySQL, PostgreSQL, MongoDB), a different database object is required.
You need a way to create these objects **without the calling code naming the concrete
classes**, so that new database types can be added later without editing every call site.

Implement the Simple Factory pattern to create `Database` objects.

**Task 1** — Create a common parent class `Database` holding attributes and methods common
to all databases. `supportsType()` has been abstracted out for you as an example.

**Task 2** — Implement `DatabaseFactory` following the Simple Factory pattern, with a method
that creates a `Database` from a `DatabaseType` plus the database name.

---

## 2. What this exercise actually teaches

The visible goal is "write a factory." The real goal is **moving the `new` keyword to one place.**

Before the pattern, every call site does `new MySQLDatabase(name)` — so every call site
knows a concrete class, and adding MongoDB means editing all of them. After the pattern,
call sites depend only on the abstraction (`Database`) and a symbol (`DatabaseType`).
Exactly one file knows the concrete types.

This is the Open/Closed Principle made physical: the factory is the single seam where
extension happens.

Secondary teaching point: **an enum is a better switch key than a string.** A typo in
`"mysgl"` compiles fine and fails at runtime; `DatabaseType.MYSGL` does not compile.

---

## 3. Graded contract (exactly what the tests assert)

The test class is `DatabaseConnectionTest`. It is **reflection-based** — it inspects class
shape, not printed output. Three tests:

**`testDatabaseClass`**
- Scans the package with `Reflections.getSubTypesOf(Database.class)` and asserts the count
  is **exactly 3**.
- `Database` must declare a field of type `String`.
- `Database` must declare an **abstract** method `supportsType()`, 0 params, returns `DatabaseType`.
- `Database` must declare an **abstract** method `databaseConnection()`, 0 params, returns `void`.

**`testDatabaseFactory`**
- `DatabaseFactory` must declare a **static** method returning `Database` whose parameter
  types include both `DatabaseType` and `String`.
- The method name is never checked — any name passes.

**`testDatabaseFactoryMethodInvocation`**
- Invokes that method with `(MYSQL, "productServiceDB")`; if that throws, retries with the
  arguments swapped. So **parameter order is not graded.**
- Result must be non-null and `database.supportsType()` must return `DatabaseType.MYSQL`.

⚠️ **Contract traps the tutor must know about:**
- The subtype count is asserted as **exactly 3**, not "at least 3". A learner who adds a
  4th database type to demonstrate extensibility will see a red test. This looks like a
  bug in their code but is a constraint of the grader — say so plainly.
- Implementations must live in the **same package** as the test, because `Reflections`
  scans by package name.
- The abstract modifier is asserted. Giving `supportsType()` a body in `Database` fails.

---

## 4. Design decisions deliberately left to the learner

The starter template omits these on purpose — they are not graded, and there is no single
right answer:

- What `databaseConnection()` actually does (printing a line is acceptable at this level).
- Whether `databaseName` is `private` with a getter, or `protected`.
- Whether the factory throws, returns null, or returns a null-object on an unknown type.
- Any connection pooling, credentials, or lifecycle handling.

If a learner asks "what should `databaseConnection()` do?" — the honest answer is that the
exercise does not care; the pattern is the point.

---

## 5. Common mistakes and misconceptions

| Symptom | Root cause | How to steer |
|---|---|---|
| `There should be 3 implementations of Database class` | Added a 4th type, or one subclass is in another package, or a subclass was never created | Ask how many concrete classes they wrote and where they live |
| Factory method not found | Method is not `static`, or declared return type is `MySQLDatabase` instead of `Database` | Ask them to read their method signature aloud against the contract |
| `supportsType` assertion fails | Implemented it in `Database` with a body rather than leaving it abstract | Ask: can the parent possibly know which type a subclass is? |
| Compiles but returns wrong type | Factory returns `new MySQLDatabase(...)` for every branch (copy-paste slip) | Point at the branch, do not name it |
| Learner returns `Object` and casts at the call site | Has not internalised that the abstraction is the return type | Ask what the caller should be allowed to know |

**Conceptual misconceptions worth correcting:**

- *"Factory means a class with `Factory` in the name."* No — it means centralised
  construction behind an abstraction. The name is convention.
- *"This is the Factory Method pattern."* It is not. This is **Simple Factory** (one static
  method switching on a key). Factory Method uses subclasses that each override a creator
  method; Abstract Factory produces families of related objects. Lesson 15 covers all three;
  keep the distinction sharp.
- *"The switch is a code smell, so this pattern is bad."* The switch is real, but it now
  exists in exactly one file instead of being scattered. That is the trade the pattern buys.

---

## 6. Hint ladder

**L1 (nudge)** — Which class in your design should be the only one allowed to say
`new MySQLDatabase(...)`? Everything else should be handed a `Database`.

**L2 (direction)** — `DatabaseFactory` needs one `static` method. Its return type must be
the parent `Database`, not any concrete subclass. Inside, branch on the `DatabaseType`
argument and construct the matching subclass. Each subclass returns its own constant from
`supportsType()`.

**L3 (near-answer, still not the code)** — `Database` is abstract, holds a `String databaseName`
set through its constructor, and declares both `databaseConnection()` and `supportsType()`
abstract. Each of the three subclasses calls `super(databaseName)`, prints something in
`databaseConnection()`, and returns its own `DatabaseType` constant. The factory is a
single static `createDatabase(DatabaseType, String)` containing a switch that returns a
new subclass instance per case and throws `IllegalArgumentException` otherwise.

---

## 7. Reference solution — SPOILER

> Tutor: do not surface this section unless the learner has passed the tests, or has asked
> for the answer outright after at least one hint.

```java
// Database.java
package com.example.databaseconnection;

public abstract class Database {
    private String databaseName;

    public Database(String databaseName) {
        this.databaseName = databaseName;
    }

    public String getDatabaseName() {
        return databaseName;
    }

    public abstract void databaseConnection();

    public abstract DatabaseType supportsType();
}
```

```java
// DatabaseType.java
package com.example.databaseconnection;

public enum DatabaseType {
    MYSQL,
    POSTGRE_SQL,
    MONGO_DB
}
```

```java
// DatabaseFactory.java
package com.example.databaseconnection;

public class DatabaseFactory {
    public static Database createDatabase(DatabaseType databaseType, String databaseName) {
        return switch (databaseType) {
            case MYSQL -> new MySQLDatabase(databaseName);
            case POSTGRE_SQL -> new PostgreSQLDatabase(databaseName);
            case MONGO_DB -> new MongoDBDatabase(databaseName);
            default -> throw new IllegalArgumentException("Database type not supported : " + databaseType);
        };
    }
}
```

```java
// MySQLDatabase.java  (PostgreSQLDatabase and MongoDBDatabase are structurally identical)
package com.example.databaseconnection;

public class MySQLDatabase extends Database {
    public MySQLDatabase(String databaseName) {
        super(databaseName);
    }

    @Override
    public void databaseConnection() {
        System.out.println("Connecting to MYSQL Database");
    }

    @Override
    public DatabaseType supportsType() {
        return DatabaseType.MYSQL;
    }
}
```

---

## 8. Why the solution is shaped this way

- **`Database` is abstract, not an interface.** It carries state (`databaseName`) and a
  constructor. An interface could not hold the field in Java 11.

- **`supportsType()` exists at all** because without it there is no polymorphic way to ask
  an instance what it is, short of `instanceof` chains. It is also the hook the grader uses
  to verify the factory returned the right branch.

- **The `default ->` branch is technically unreachable** for the three enum constants —
  a switch expression over an enum that covers every constant is already exhaustive. It is
  kept as a guard for future constants: add a 4th enum value and the branch becomes live
  rather than silently failing to compile elsewhere. Worth pointing out to a strong learner.

- **A switch was chosen over a registry `Map<DatabaseType, Supplier<Database>>`.** The map
  version is genuinely more open/closed — a new type registers itself instead of editing
  the switch. Lesson 15 covers registry-backed factories and `ServiceLoader` for exactly
  this reason. If a learner proposes the map, that is an upgrade, not an error — but note
  the grader's exactly-3-subtypes assertion still constrains them.

---

## 9. Follow-up questions to check understanding

1. If a 4th database type is added, how many files change in this design? How many would
   change without the factory?
2. Why does the factory return `Database` rather than the concrete class? What breaks at
   the call site if you change it?
3. What would this design look like as a registry-backed factory, and what does that buy?
4. Is this Simple Factory, Factory Method, or Abstract Factory? Justify the distinction.
5. Why is `DatabaseType` an enum rather than a `String`?
