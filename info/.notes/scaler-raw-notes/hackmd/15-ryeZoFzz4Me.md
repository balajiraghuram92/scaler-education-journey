Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/ryeZoFzz4Me

# Pre-Reads-Java-Advanced-2.md Summary

## Document Overview

This HackMD document provides a comprehensive pre-read guide for a Java Advanced Concepts lab focused on "Generics & Collections." The material transitions from theoretical knowledge to practical application through six milestones building an Inventory Management System.

## Core Educational Scope

The session emphasizes the gap between understanding collections concepts and applying them in real systems. As noted: "knowing that `HashMap` offers O(1) lookup is different from deciding to use `HashMap<String, T>`" in actual implementation.

## Six Milestone Structure

| Milestone | Primary Focus |
|-----------|--------------|
| 1 | Item class hierarchy with `Comparable` |
| 2 | Generic `Inventory<T>` with bounded types |
| 3 | `LinkedList`-based recently-viewed cache |
| 4 | `PriorityQueue` for order processing |
| 5 | Custom `Comparator` implementations |
| 6 | `equals()`/`hashCode()` for `HashSet` |

## Key Conceptual Distinctions

**Comparable vs Comparator**: "One defines a single 'natural' order inside the class itself, and the other defines an external, swappable ordering strategy."

**Hash Contract Requirement**: Objects considered equal must return identical `hashCode()` values, or hash-based collections silently malfunction.

## Prerequisites & Outcomes

Students should possess familiarity with basic generics, inheritance, and Java fundamentals. The session culminates in eight learning outcomes ranging from class hierarchy design to `equals()`/`hashCode()` override mastery.
