Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/rJwOAvvrGx

# Factory Pattern Pre-Read: Content Summary

## Core Teaching Structure

This session addresses runtime selection of classes rather than object reuse. As the document states: "The question is no longer 'how do I reuse an existing object' but 'how do I decide, at runtime, which class to construct.'"

## Key Problem Domain

The material uses a consistent example throughout: "a service that must talk to different backend AI providers (OpenAI, Anthropic, Gemini) through a single interface."

## Pattern Progression

The session moves through three levels:
1. **Factory Method** — selecting correct objects based on runtime input
2. **Abstract Factory** — ensuring related object families stay matched by vendor
3. **Registry-backed Factory** — enabling extension without editing existing code

## Critical Learning Point

A crucial distinction emerges: "Centralized" decision logic differs fundamentally from "eliminated" logic. Factories concentrate the vendor-selection decision into one predictable location rather than removing it entirely.

## Real-World Application

The pattern appears across production systems including "payment gateways, cloud storage SDKs, JDBC drivers, and logging frameworks." The document emphasizes this represents "arguably the single most common creational pattern in real code."

## Extensibility Challenge

The session specifically flags "a factory that looks extensible but still requires editing shipped code for every new case" as a common real-world gap between pattern appearance and actual delivery—a trap AI assistants frequently miss.