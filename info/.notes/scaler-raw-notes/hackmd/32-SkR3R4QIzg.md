Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/SkR3R4QIzg

# Design Patterns: Strategy and Observer

## Overview

This pre-read covers two behavioral design patterns:

**Strategy** addresses scenarios where "one task, several genuinely different ways to do it, exactly one chosen at a time" applies. The document illustrates this with Google Maps path-finding across travel modes (driving, biking, walking).

**Observer** handles situations requiring "publisher/subscriber relationship" mechanics. The Amazon order-placement example demonstrates how "invoicing, warehouse updates, inventory updates, and email all need to react to the same event."

## Key Distinctions

The material emphasizes precise vocabulary: "Factory creates, Strategy behaves, Adapter translates." This distinction matters because "all four involve an interface with multiple implementations but solve entirely different problems."

The one-sentence test differentiates these patterns: Strategy "pick[s] exactly one way and uses only that one," while Observer "notifies every registered subscriber, every time, with no notion of picking a single winner."

## Design Principle Application

Both patterns reinforce the Open/Closed Principle. Rather than embedding mode-specific logic via if-else branches, extracting dedicated classes allows new implementations without modifying existing code.

## Practical Implementation Notes

Strategy implementations typically combine three smaller patterns: interface-based Strategy, Singleton-style instance reuse, and Factory-based lookup. Real examples include AI model routing by cost/complexity and RAG pipeline retrieval method selection.

Observer applications appear in streaming callbacks, webhooks, and telemetry systems where independent system components react to events without tight coupling.

## AI Workflow Innovation

The session models "using an assistant to diagnose and propose fixes for code a human already wrote, rather than asking it to generate a solution from scratch."
