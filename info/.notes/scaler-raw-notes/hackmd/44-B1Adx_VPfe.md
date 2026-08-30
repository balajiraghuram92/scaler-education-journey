Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/B1Adx_VPfe

# Pre-Reads-AppliedDesignMachineCoding-05: Parking Lot System Design

## Overview

This session introduces a Parking Lot system design problem, moving beyond the TicTacToe domain. The teaching method reinforces the established 6-step framework while introducing new concepts relevant to systems involving physical resources and financial transactions.

## Key Design Principles

**Strategy Pattern Recognition**: The instructional material emphasizes that "a requirement phrased as 'this behavior needs to be changeable without rewriting the system' is a Strategy pattern in disguise."

**Snapshot vs. Live References**: The distinction between storing data at a point in time versus maintaining current references is presented as critical for production systems. A ticket captures who operated the gate *when issued*, separate from who operates it *now*.

**Field Duplication Trade-offs**: Decisions about storing redundant fields depend on query frequency—commonly accessed data merits duplication for speed, while audit-only lookups typically don't.

## Core Learning Outcomes

Students will be able to:
- Scope systems involving physical resources and transactions
- Identify strategy-pattern requirements from wording alone
- Derive class diagrams from user journey walkthroughs
- Apply class-to-table schema algorithms to new domains
- Distinguish one-to-many from many-to-many relationships
- Evaluate enum columns versus lookup table trade-offs
- Recognize unresolved concurrency risks in paper designs

## Real-World Connections

The material connects parking lot concepts to production systems: exact-match resource allocation in cloud scheduling, snapshot fields in e-commerce orders, pluggable pricing engines in ride-hailing platforms, and enum-as-lookup-table patterns in support systems.

## Disciplined AI Integration

AI is introduced only *after* design completion, serving to catch genuine gaps rather than generate designs—here revealing a potential concurrency issue without resolving it immediately.