Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/HkVAc5EHGx

# Backend LLD: Design Patterns: Builder

## Overview

This document teaches the Builder design pattern through a progression from problems with traditional object construction to a production-ready implementation.

## Core Problem

The Builder pattern addresses the challenge of safely constructing objects with many fields, some optional, all requiring validation before the object can exist.

## Why Traditional Approaches Fail

**Large Constructor Issues:**
"Just by looking at this line, with no other context, it is genuinely hard to tell what `"XYZ"` or `"ABC"` mean" when creating objects with many parameters. Same-type parameters can be swapped silently without compiler detection.

**Telescoping Constructors:**
A class with n fields can require up to 2^n constructor combinations. This approach spreads readability and mistake-proneness across multiple constructors rather than solving the core problem.

**Map<String, Object> Approach:**
"A wrong key just silently does nothing" and type errors only surface at runtime, far from where mistakes occur.

## The Solution: Builder Pattern

The pattern uses a helper class to safely collect values with compiler checking, then validates and constructs the real object through a `build()` method.

### Four Production Improvements

1. **Static getBuilder()** method on the main class reveals how to begin
2. **Builder.build()** method performs validation and creates the object
3. **Chainable setters** return `this` to enable fluent syntax
4. **Private constructor** on the main class prevents bypassing validation

## Implementation Details

**Fluent Chaining:**
Every setter must return the Builder itself, enabling `.setAge(21).setName("Naman").build()` style construction.

**Nested Class:**
Builder lives inside the main class to access its private constructor.

**Defensive Copying:**
Mutable fields like Lists must be copied, not referenced, to prevent external modification after `build()` completes.

## Common Pitfalls

- Setters returning `void` instead of Builder breaks chaining
- Public constructors allow bypassing validation
- Shared List references enable post-construction modification
- Lombok's `@Builder` doesn't auto-validate or defensive-copy collections without `@Singular`

## Real-World Usage

The pattern appears in Firebase's RequestConfiguration, Java's StringBuilder, OkHttp's Request.Builder, and AI API client libraries.

## Lombok Automation

`@Builder` generates the structural boilerplate but requires manual validation logic and `@Singular` for collection safety.