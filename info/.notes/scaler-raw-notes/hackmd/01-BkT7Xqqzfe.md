Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/BkT7Xqqzfe

# Pre-Read - OOP-3 Polymorphism, Interfaces and Abstract Classes

## Overview

This session covers three major topics in object-oriented design:

1. **Runtime Polymorphism** - How Java selects the correct `calculateFare()` method at execution time through method overriding and JVM dispatch
2. **Compile-time Polymorphism** - How the compiler resolves multiple methods with identical names via method overloading
3. **Abstraction as Code** - Using the `abstract` keyword to prevent instantiation of generic base classes
4. **Abstract Classes** - Classes that enforce obligations on subclasses without being instantiatable
5. **Interfaces** - Contracts expressing capability across unrelated class hierarchies
6. **Composition vs Inheritance** - When composition (HAS-A) provides better design than inheritance (IS-A)

## Why This Matters

The document emphasizes that "Polymorphism is what makes the whole system flexible." Without it, adding new vehicle types requires rewriting dispatch logic. The real-world implications include preventing production incidents caused by poor design choices around payment providers, vehicle types, and class hierarchies.

## Three-Question Design Test

The core decision-making framework presented:

| Relationship Type | Question | Tool |
|---|---|---|
| IS A TYPE OF | Does X inherit structure from Y? | `extends` / abstract class |
| CAN DO | Does X possess capability Y? | `implements` / interface |
| HAS A | Does X contain Y as a component? | composition / field |

## Key Learning Outcomes

Students will understand method overriding rules, the `@Override` annotation's purpose, abstract method enforcement, interface contracts, and composition patterns for cleaner separation of concerns.
