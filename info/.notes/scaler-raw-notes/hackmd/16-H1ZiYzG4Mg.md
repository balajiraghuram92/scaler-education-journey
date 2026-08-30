Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/H1ZiYzG4Mg

# Java Advanced Concepts 2 — Post-Read Summary

This document provides a comprehensive guide to generics, collections, and ordering in Java through an Inventory Management System lab project.

## Core Concepts Covered

**Comparable vs. Comparator**: The material explains that "a class can implement Comparable exactly once, giving it one natural ordering" while multiple Comparators provide flexibility for different sort strategies.

**Bounded Type Parameters**: Using `T extends Item` allows generic classes to call methods specific to the bound type, ensuring type safety while maintaining flexibility for subclasses.

**Key Collections**:
- `HashMap<K,V>` for O(1) lookup by key
- `LinkedList` for front/rear insertions via `addFirst()` and `removeLast()`
- `PriorityQueue` backed by binary heap for priority-based extraction
- `HashSet` for uniqueness enforcement

## Critical Contract: equals() and hashCode()

The material emphasizes: "if a.equals(b) is true, then a.hashCode() must equal b.hashCode()." Violating this contract causes hash-based collections to malfunction silently—duplicates slip through or lookups fail without error messages.

## Common Pitfalls

- Casting `double` differences to `int` truncates values, breaking comparisons
- Assuming `PriorityQueue` iteration yields sorted output (only `poll()` does)
- Returning internal collections directly instead of defensive copies
- Using mutable fields in `hashCode()` implementations

## Modern Java Notes

The document includes supplementary sections on lambda-based Comparators and method references, reflecting contemporary Java practices while maintaining pedagogical clarity through explicit class implementations.