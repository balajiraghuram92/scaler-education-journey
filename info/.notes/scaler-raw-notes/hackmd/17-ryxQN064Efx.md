Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/ryxQN064Efx

# Java Advanced Concepts: Streams & Lambdas - Pre-Read Summary

This pre-read document introduces three interconnected Java concepts essential for intermediate and senior developers.

## Core Topics Covered

**Functional Interfaces**: Interfaces with exactly one abstract method, including `Runnable`, `Callable`, `Comparable`, and `Comparator`. The document notes that "A functional interface is an interface with exactly one abstract method."

**Lambda Expressions**: Described as "syntactic sugar" rather than new functionality, lambdas provide concise alternatives to anonymous class implementations. They work exclusively with functional interfaces.

**Streams API**: Offers declarative pipeline processing for collections, replacing imperative loops. Key operations include `filter`, `map`, `sorted`, `distinct`, and `collect`.

## Key Distinction: Lazy vs. Eager Evaluation

The material emphasizes that "Intermediate stream operations are lazy; terminal operations are eager." This means operations like `filter` and `map` don't execute until a terminal operation (like `collect`) demands results.

## Practical Importance

The document stresses these skills represent baseline expectations: "Interviewers and code reviewers routinely treat fluency with lambdas and streams as a baseline expectation for intermediate and senior Java roles."

## Exception Handling Introduction

The session covers checked versus unchecked exceptions, exception propagation, and foundational vocabulary needed for subsequent custom exception implementation.