Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/HJ4uR4XUMe

# Backend LLD: Behavioural Design Patterns: Strategy and Observer

This comprehensive post-read covers two fundamental behavioral design patterns used in system design. Here's the distilled content:

## Core Concepts

**Strategy Pattern**: "Pick ONE way of doing something, out of several options" — exactly one implementation executes per call, chosen by the caller.

**Observer Pattern**: "Notify MANY interested parties automatically when something happens" — multiple subscribers react to a single event simultaneously.

## Key Distinction

The patterns solve different problems. Strategy addresses selecting a single algorithm from alternatives (like choosing car vs. bike routing). Observer addresses notifying multiple independent listeners about an event without the publisher knowing their identities.

## Strategy Implementation

The pattern combines three concepts:
- **Strategy**: Each approach becomes its own class implementing a shared interface
- **Singleton**: Stateless strategies are cached and reused
- **Factory**: A lookup method returns the appropriate strategy without conditional logic

Example: Google Maps path-finding delegates to `CarPathCalculator`, `BikePathCalculator`, or `WalkPathCalculator` based on user selection through a factory pattern.

## Observer Implementation

Components include:
- **Publisher**: Maintains subscriber list and announces events
- **Subscribers**: Self-register to receive notifications
- **Interface**: All subscribers implement a common contract (e.g., `onOrderPlaced()`)

Example: When Amazon processes an order, independent systems (invoicing, warehouse, fraud detection) subscribe and react without the core logic knowing their details.

## Common Pitfalls

- Treating Strategy as "many implementations running together" (that's Observer's role)
- Passing mode/type parameters into strategy class methods (signals incomplete refactoring)
- Rebuilding stateless strategy objects unnecessarily (causes object churn)
- Having publishers hardcode subscriber lists (reintroduces coupling)
- Letting one subscriber's exception prevent others from executing (requires per-subscriber exception handling)

## Related Patterns

**Factory vs. Strategy vs. Adapter**: Factory *creates* objects; Strategy *behaves* (executes algorithms); Adapter *translates* incompatible interfaces.

**Facade vs. Observer**: Facade centralizes existing logic but still requires editing source code for new reactions. Observer enables external teams to register new behaviors without touching existing code.

## Real-World Applications

- **Model routing**: Directing AI queries to appropriate model tiers based on complexity
- **Token streaming**: Observers handle UI updates, logging, and moderation independently
- **Payment systems**: Multiple payment methods as strategies; webhook callbacks as observers

## Interview Focus

The distinction between "pick one" (Strategy) and "notify all" (Observer) is crucial. Chain of Responsibility, mentioned briefly, handles sequential fallback attempts—fitting neither pattern.

The document emphasizes that while code may "work," design regressions occur silently when coupling reappears. Using AI as a code reviewer (diagnosing problems) rather than just a code generator (producing solutions) catches these issues earlier.
