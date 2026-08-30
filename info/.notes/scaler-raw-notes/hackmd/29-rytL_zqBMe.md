Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/rytL_zqBMe

# Backend LLD: Structural Design Patterns: Adapter and Facade

## Overview

This post-read examines two structural design patterns that address how objects organize and connect after creation, distinct from creational patterns that handle object instantiation.

## Adapter Pattern

### Core Concept

An adapter functions as a translation layer between incompatible interfaces. The key principle: "without changing either side." As the document states, "A middle layer that connects two things that don't fit together — WITHOUT changing either side."

### Real-World Example: PhonePe & Banking APIs

The pattern solves the problem where PhonePe needs to support multiple banks (Yes Bank, HDFC, etc.) without rewriting code for each integration. Rather than editing third-party bank code directly, an adapter implements PhonePe's internal `BankAPI` interface while wrapping the external bank's actual methods.

### Three Components

1. **Target Interface** — The client's expected contract
2. **Adaptee** — The existing incompatible class (usually third-party)
3. **Adapter** — Implements the target, wraps the adaptee, translates between them

### Translation Types

The `YesBankAdapter` demonstrates four translation approaches:
- Type conversion (int status codes to boolean)
- Data reshaping (object fields to primitive arguments)
- Pass-through (when shapes already align)
- Method renaming (identical behavior, different name)

### Benefits

- Decoupling from specific bank implementations
- Versioning resilience—bank API changes only affect adapter code
- Open/Closed Principle compliance—new banks require new adapters, not editing existing code

## Facade Pattern

### Core Concept

A facade provides one simple entry point coordinating multiple complex subsystems. Per the document: "One simple entry point that hides the coordination of several complex systems behind it."

### Real-World Example: Amazon Order Placement

Instead of `Amazon.orderPlace()` directly calling invoice, warehouse, inventory, and email services, a dedicated `OrderPlacedFacade` coordinates this complexity, ensuring single responsibility.

### Dependency Injection

Facade constructors receive subsystem dependencies from outside rather than creating them internally with `new`. This approach:
- Prevents locking to concrete implementations
- Enables testability through mock substitution
- Allows future implementation swaps without facade modification

## Distinguishing Adapter from Facade

| Aspect | Adapter | Facade |
|--------|---------|--------|
| Problem | Two incompatible interfaces | Complex, hard-to-use system |
| Solution | Translate between shapes | Hide coordination behind simple entry |
| Typical Count | One adaptee | Multiple subsystems |

The key differentiator: ask why the wrapper exists. Incompatibility = Adapter. Complexity = Facade.

## Real-World AI Applications

### Adapter Use Case
Multiple LLM providers (OpenAI, Anthropic, Gemini) each have different SDKs. A `ChatModel` interface with provider-specific adapters allows swapping models without application rewrites. Libraries like LiteLLM implement exactly this pattern.

### Facade Use Case
An AI agent's single message triggers retrieval, planning, tool execution, and memory recording behind the scenes. The user sees only one clean interface (`run()` or `invoke()`), while orchestration stays hidden.

## Common Pitfalls

1. **Editing third-party code directly** — Upstream updates overwrite changes; use a separate adapter class instead
2. **Target interface design** — Avoid mirroring one implementation's quirks; design for client needs
3. **Type leakage** — Don't expose adaptee types through the target interface
4. **Incomplete translation** — Forgetting return-type conversions causes silent failures
5. **Direct construction** — Building adaptees inside clients reintroduces coupling
6. **Misplaced coordination** — SRP violation leaving multi-subsystem logic in business classes
7. **Hardcoded dependencies** — Using `new` inside facades locks them to implementations
8. **Forced categorization** — Real systems often combine adapters within facades
9. **Vague AI prompts** — "Add support for X" invites if/else branches in client code instead of new adapters
10. **Correctness ≠ extensibility** — Code working today doesn't prove it scales to new cases

## AI Corner: The Deceptive Adapter

When prompted vaguely to "add HDFC Bank support," an AI might generate code that:
```
if (bankName.equals("YesBank")) {
    bankAPI = new YesBankAdapter(...);
} else if (bankName.equals("HDFCBank")) {
    bankAPI = new HDFCBankAdapter(...);
}
```

This appears functional but violates Open/Closed—PhonePe requires editing for each new bank. The pattern's entire value depends on client immutability.

**Fix:** Use explicit prompts naming the guarantee needed: "without editing the PhonePe class at all."

## Key Terminology

- **Structural Pattern** — How objects organize and connect after creation
- **Adaptee** — Incompatible existing class being wrapped
- **Dependency Injection** — Supplying dependencies from outside rather than constructing them internally
- **Orchestration** — Coordinating multiple steps/subsystems to accomplish a larger task

## Interview Questions Summary

Likely areas for discussion include distinguishing pattern categories, identifying the three adapter components, explaining why third-party code shouldn't be edited directly, demonstrating translation types, understanding what the Open/Closed test means for adapters, articulating adapter versus facade differences, recognizing both patterns working together, explaining dependency injection rationale, understanding why generic AI prompts produce flawed results, and recognizing these patterns in real libraries.

## Self-Assessment Topics

- MacBook dongle analogy and "without changing either side"
- Component identification in banking example
- Step-by-step call tracing through adapters
- Writing adapter implementations with different success signals
- Single Responsibility Principle application
- Dependency injection reasoning
- Subsystem dependency roles
- Categorizing hybrid adapter/facade scenarios
- Identifying AI-generated code failures
- Correcting prompts with explicit constraints
- Real-world library examples
- Evaluating conflated adapter-facade designs

## Further Study

Real implementations appear in LiteLLM (LLM adapter layer), LangChain (model abstraction), Retrofit (HTTP to typed interface conversion), and prior posts on Factory Pattern and Prototype/Registry patterns.