Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/BkjtqG8BGg

# Design Patterns — Prototype and Registry

## Overview

This document covers two related design patterns used when object duplication is more efficient than construction from scratch.

## Core Problems with Manual Copying

The document identifies three critical issues when copying object fields outside a class:

1. **Tight Coupling**: Clients must know every internal field name, creating brittle dependencies.

2. **Encapsulation Violations**: "Private fields with no setter → impossible to copy manually from outside the class."

3. **Open/Closed Principle Violations**: Handling subclasses requires growing `instanceof` chains that repeatedly modify working code.

## The Prototype Pattern

**Definition**: "Instead of building an object from scratch, create it by COPYING an existing template object, then changing only what's different."

### Key Implementation Details

The pattern uses a generic interface requiring classes to implement their own copying:

```java
public interface Prototype<T> {
    T clone();
}
```

Copy-constructors should live inside the class with full field access. Subclasses must override `clone()` and call `super(instance)` to avoid silently dropping parent fields.

### Critical Rule

"EVERY subclass MUST override clone() itself. If a child class forgets to override it, calling .clone() on that child silently runs the PARENT's clone logic instead — dropping any fields the child added."

## The Registry Pattern

A separate `Map`-based storage for retrieving templates by name:

```java
public class VMImageRegistry {
    private Map<String, VMInstance> map = new HashMap<>();
    void register(String key, VMInstance instance) {
        map.put(key, instance);
    }
    VMInstance get(String key) {
        return map.get(key);
    }
}
```

**Thread Safety**: Use `ConcurrentHashMap` for multi-threaded access rather than plain `HashMap`.

**Missing Keys**: "get() returns null for a missing key, silently → NullPointerException later, on a completely different line, when .clone() runs on null."

## Shallow Copy Trap

When mutable fields like Lists are copied by reference rather than contents, both original and copy share the same underlying object. The corrected approach:

```java
this.installedPackages = new ArrayList<>(instance.installedPackages);
```

This creates a new container with copied contents, not just a shared reference.

## Python Comparison

Python's `copy` module provides built-in solutions:
- `copy.copy()` performs shallow copying
- `copy.deepcopy()` creates fully independent objects including nested structures

## Common Pitfalls Summary

Ten critical mistakes include forgetting subclass overrides, omitting `super()` calls, using non-generic interfaces, trusting shallow copies, and allowing registry lookups to return `null` silently without clear errors.

## Distinguishing Prototype from Registry

"Prototype → object knows how to copy itself. Registry → a place to store templates, retrievable by name." These address separate concerns following Single Responsibility principles.