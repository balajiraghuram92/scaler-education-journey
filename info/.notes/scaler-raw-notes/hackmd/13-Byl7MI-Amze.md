Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/Byl7MI-Amze

# Pre-Reads-Java-Advanced-1.md - HackMD

---

## title: Pre-Reads
tags: [Final]

---

| PRE-READ | Java Advanced Concepts | Java Advanced Concepts-1 — Generics & Collections |
|----------|-------------------------|-----------------------------------------------------| 

## Context 

Prior to this session, Java classes have been written using concrete types declared explicitly at every point of use. This session introduces a mechanism that changes that: a class or method can be written once, without committing to a specific type, and the type is supplied later, at the point where the class is actually used. Java enforces that choice from that point onward, at compile time. 

Before this mechanism existed, a general-purpose container in Java had exactly one way to hold "any type of data" — declaring it to hold `Object`. This worked, but it removed all type checking. A container built to hold text could just as easily accept a number, and the compiler would raise no objection. The mistake would only surface later, while the program was running, typically as a `ClassCastException`. 

This session covers the construct introduced specifically to close that gap, along with the standard library of ready-made containers built using it. 

## Overview 

| Segment | What is covered | Concepts in play | 
|---------|------------------|-------------------| 
| What is a Collection | The general idea of grouping similar items, before any Java-specific detail | Collection, Collections Framework | 
| The problem, before Generics | Why a general-purpose container built on `Object` compiles cleanly but fails at runtime | `Object`, `ClassCastException` | 
| Generics — the solution | A class or method parameterized by a placeholder type, enforced at compile time | Type parameter, `Stack<T>`, raw type | 
| Storing a pair of values | Parameterizing a class by more than one type at once | `Pair<T, V>`, generic methods | 
| Generics with inheritance | Why a list of a subtype is not automatically usable where a list of the supertype is expected | Wildcard, `? extends`, `? super`, PECS | 
| The Collections Framework | The standard hierarchy of interfaces and implementations Java provides | `List`, `Set`, `Queue`, `Map` and their implementations | 

## Why This Session Matters 

Nearly every non-trivial Java program stores and processes groups of data — a list of orders, a set of unique identifiers, a mapping from a user ID to a session object. Writing a separate, hand-built container class for each type stored would mean duplicating the same logic repeatedly. Generics remove that duplication by letting a single class definition work correctly, and safely, across any type. This also has direct bearing on interview performance. Code that compiles using raw types or unchecked `Object` casts is a common signal of unfamiliarity with idiomatic Java, and reviewers typically expect fluency with generic classes, bounded wildcards, and the standard Collections hierarchy without hesitation. 

## Real-World Use Cases 

- **Generic containers:** A repository class that fetches and stores domain objects — `Repository<User>`, `Repository<Order>` — is written once and reused across every entity type in an application, with the compiler enforcing that a `User` repository is never accidentally handed an `Order`. 

- **Pair and tuple types:** Returning two related values from a method — a coordinate, a key and its associated score, a result and an error — is commonly expressed using a generic `Pair<T, V>` rather than a purpose-built class for every combination of types. 

- **API design with wildcards:** Library and framework methods that accept "a list of something in this family" — for example, a method that processes any `List` of a common supertype — rely on bounded wildcards to remain flexible without giving up compile-time type safety. 

- **Choosing the right collection:** Selecting between `ArrayList`, `LinkedList`, `HashSet`, and `TreeSet` for a given use case is one of the most frequently exercised decisions in everyday backend development, and is assumed knowledge in most machine coding rounds. 

## Key Concept Preview 

The core idea to walk in with: 

> **Generics** allow a class, interface, or method to be written with one or more **type parameters** — placeholders such as `T` or `V` — that are supplied with an actual type at the point of use. Once supplied, Java enforces that type at compile time, rather than allowing a mismatch to surface only when the program runs. 

A distinction worth previewing, since it surprises most people the first time they encounter it: 

> Even where `Cat` is a subtype of `Animal`, `List<Cat>` is **not** treated as a subtype of `List<Animal>`. Passing a `List<Cat>` to a method expecting a `List<Animal>` does not compile, unless the method's parameter is declared using a wildcard. 

## Connection to Prior Material 

This session assumes familiarity with the following foundational Java concepts: 

- **Classes, objects, and inheritance:** In particular, that every class in Java ultimately derives from `Object`, and that a subtype reference can always be used wherever its supertype is expected. 

- **Compile-time versus runtime errors:** The distinction between a mistake the compiler catches immediately and one that only appears while the program is executing, since this distinction is central to why Generics exist at all. 

- **Arrays:** Basic familiarity with array declaration and indexing, since the motivating examples in this session build a simple `Stack` backed by an array. 

## Connection to What Comes Next 

This session is the first of the Java Advanced Concepts series and establishes the vocabulary — type parameter, wildcard, raw type — used throughout the remainder of the series. The next session goes into `HashMap` specifically, examining how hashing, buckets, and collisions work internally, building directly on the `Map` implementations introduced briefly at the end of this session. 

## Prerequisites 

Confirm the following before the session: 

- A working Java development environment (JDK and an IDE such as IntelliJ or VS Code). 
- Comfort reading and writing basic Java classes, including constructors and instance methods. 
- No prior exposure to Generics is assumed; the session introduces the topic from first principles. 

## Reference Links 

- Search "Java Generics tutorial Oracle" for the official language documentation on type parameters and bounded types. 
- Search "Java Collections Framework hierarchy" for background on the interface-and-implementation structure covered toward the end of this session. 
- Search "PECS Producer Extends Consumer Super" for a preview of the wildcard rule covered in this session — useful to read before class. 

## What You Will Walk Away With 

| Learning Outcome | 
|-------------------| 
| Explain why a container built using `Object` compiles without error but permits type-mismatch bugs that only surface at runtime. | 
| Define a type parameter and write a simple generic class such as `Stack<T>`. | 
| Distinguish a raw type from a properly parameterized generic type, and explain why raw types should not be used in new code. | 
| Write a generic class parameterized by more than one type, such as `Pair<T, V>`. | 
| Declare a generic method independently of a generic class. | 
| Explain why `List<Cat>` is not usable where `List<Animal>` is expected, and fix this using a bounded wildcard. | 
| State the PECS rule and apply `? extends` and `? super` correctly. | 
| Identify the core interfaces and implementations of the Collections Framework — `List`, `Set`, `Queue`, and a preview of `Map` — and describe the practical difference between commonly used implementations of each. |
