Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/BkzbYfqrfg

# Structural Design Patterns: Adapter and Facade

## Overview

This document covers two structural design patterns that address how objects organize and connect after creation:

**Adapter Pattern**
The adapter pattern creates a middle layer translating between two incompatible interfaces without modifying either side. The running example involves PhonePe integrating multiple bank APIs (Yes Bank, HDFC) through a consistent interface. Key components include:
- Target interface
- Adaptee (existing incompatible class)
- Adapter (translation layer)

Real-world applications include multi-provider AI SDKs like LiteLLM, which lets applications swap between GPT, Claude, or Gemini with minimal code changes.

**Facade Pattern**
The facade pattern hides coordination complexity behind a single entry point. Amazon's order placement demonstrates this—a single method call coordinates invoicing, warehouse updates, inventory changes, and email notifications internally.

## Critical Distinction

"Adapter solves compatibility between mismatched interfaces; Facade solves complexity by coordinating multiple subsystems." Understanding this distinction separates pattern comprehension from mere structural imitation.

## Common Pitfall

A frequent mistake occurs when adding provider support introduces conditional logic back into client code, violating the Open/Closed Principle the pattern intended to preserve.

## Learning Goals

Students should recognize these patterns in existing systems, implement them correctly, distinguish between them, and evaluate whether proposed solutions genuinely maintain design principles.