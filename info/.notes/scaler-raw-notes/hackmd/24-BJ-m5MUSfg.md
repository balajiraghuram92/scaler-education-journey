Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/BJ-m5MUSfg

# Prototype and Registry Design Patterns: Session Overview

## Core Problem and Solution

The document addresses a fundamental design challenge: when should developers clone existing objects rather than build them from scratch? According to the material, "manual, outside-the-class copying breaks in three separate ways" — through tight coupling to internal fields, inability to access private fields without setters, and `instanceof` chains that violate the Open/Closed Principle.

The proposed solution moves copying responsibility inside the object itself through the Prototype pattern, enabling "a class that implements a `clone()` method" with full access to its own private fields.

## Critical Implementation Rule

A key learning outcome emphasizes that "every subclass must override `clone()` itself, with no exceptions." The document warns of a dangerous failure mode: "if a subclass forgets to override it, calling `.clone()` silently runs the parent's copying logic instead, which copies only the parent's fields and drops any field the subclass added, with no compiler warning and no runtime crash."

## Practical Applications

Real-world examples include cloud VM image duplication, pre-configured API clients, email templates, game NPC spawning, document platform templates, and Kubernetes Pod specifications. These demonstrate how "fill-once, copy-repeatedly" patterns eliminate repeated setup work at scale.

## Dual Responsibilities

The material distinguishes between two separate concerns: Prototype answers whether "this object copy itself correctly," while Registry answers where to "store a named template so it can be found and reused."