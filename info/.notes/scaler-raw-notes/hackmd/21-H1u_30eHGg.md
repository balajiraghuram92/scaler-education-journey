Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/H1u_30eHGg

# Design Patterns & Singleton: Pre-Read Summary

## Core Distinction
The material establishes that "SOLID tells you what good design should look like, while a design pattern is a named, pre-packaged solution to a problem that keeps recurring."

## Three Pattern Categories
The Gang of Four catalogue organizes patterns into: Creational, Structural, and Behavioural classifications.

## Singleton's Dual Purpose
According to the session, Singleton serves exactly two legitimate functions: either managing a genuinely shared resource (database connections, loggers, caches) or handling "legitimately expensive to create" objects where setup costs justify single instantiation and reuse.

## Implementation Progression
The material describes building Singleton incrementally:
- Private constructor prevents unrestricted instantiation
- Static instance reference maintains the single object
- Static getInstance() method provides controlled access

## Concurrency Challenge
"A race condition in getInstance(), where two threads both see a null instance and each construct their own object, will not show up in normal local testing."

## The Volatile Requirement
Double-checked locking requires the `volatile` keyword because instruction reordering at the compiler or CPU level can expose partially-constructed objects to concurrent threads—a detail frequently omitted from AI-generated code.

## Serialization Risk
Default Java deserialization bypasses private constructors, potentially creating multiple instances. Enum-based Singletons provide JVM-guaranteed safety instead.

## Real-World Locations
Spring's @Service, @Component, and @Repository annotations implement Singleton scope by default, alongside connection pools and logging frameworks.