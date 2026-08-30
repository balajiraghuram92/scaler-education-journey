Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/SJF9_Wy8Ml

# Pre-Reads-DesignPatterns-DecoratorFlyweight - HackMD

| PRE-READ | Design Principles & Patterns for Extensible Systems | Backend LLD: Structural Design Patterns: Decorator and Flyweight |
|----------|-------------------------|-----------------------------------------------|

## Context

- The last session covered Adapter and Facade, both about making things fit together nicely: Adapter translated between two incompatible interfaces, Facade hid a messy, multi-step process behind one simple entry point.
- This session stays in Structural Patterns but moves to two problems that have nothing to do with translation or hiding coordination.
- The first problem: what happens when an object needs new behavior added on top of it, repeatedly, without knowing every possible combination ahead of time, and without editing the object's original class. The running example is a coffee shop where a customer keeps adding espresso, milk, mocha, and whip one at a time. This is **Decorator**.
- The second problem: what happens when a system has to manage a huge number of nearly identical objects (think 100,000 bullets in a PUBG match) without duplicating the same heavy data across every single one. This is **Flyweight**.
- For each pattern, the session moves through the same rhythm as always: an everyday, non-code example first, then a naive coding attempt that breaks down, then the fix, then a real production example (Java's own standard library shows up for both patterns).
- The session closes with an AI Corner showing how a "special case" request can quietly push a Decorator design back into the exact boolean-flag mess it was built to avoid.

## Overview

| Segment | What is covered | Concepts in play |
|---------|------------------|-------------------|
| Decorator: The Everyday Idea | A coffee order and a pizza order, building up in layers, before any code | Wrapping a base object one layer at a time, each layer changing only cost/description |
| The Problem: Coffee Shop Ordering | Why a `Beverage` holding a fixed list of add-ons breaks down once add-ons repeat or affect each other's price | Treating drinks and add-ons as the same kind of thing, shared interface |
| Coding the Decorator | A `Beverage` interface, base drinks (`Espresso`, `DarkRoast`) that stand alone, and a `CondimentDecorator` base class that wraps another `Beverage` | Interface implementation, wrapping/delegation, recursive method calls |
| Decorator in Real Tools | `BufferedReader` wrapping `FileReader`, CSS styling layered onto a plain button, `Collections.synchronizedList()` and `unmodifiableList()` | Recognizing Decorator already present in a language's standard library |
| Decorator in a Real Backend Example | A `NotificationService` wrapped by logging, retry, and rate-limiting decorators instead of stuffing all of that logic into one class | Cross-cutting concerns, middleware-style layering |
| Flyweight: The Everyday Idea and the PUBG Problem | A shared library book as the seed idea, then the memory cost of 100,000 full `Bullet` objects in a single match | Intrinsic (shared) data versus extrinsic (unique) data |
| Coding the Flyweight | Splitting `Bullet` into a shared `BulletType` (color, weight, image) and a small per-bullet object (position, direction, speed), cached through a factory | Object caching, a factory enforcing single shared instances |
| Flyweight in a Real Backend Example | Java's `Integer.valueOf()` caching and String pool, then a `Category` reference-data object shared across millions of food-delivery order line items | Reference-data caching, read-only shared objects behind a factory |
| AI Corner: Decorator Quietly Turning Into if/else | An AI "fix" for a combo discount that adds boolean flags and conditionals back into the base `Espresso` class instead of adding a new decorator | Pattern regression, prompt specificity as a design safeguard |

## Why This Session Matters

- "Cross-cutting concerns (logging, retries, rate limiting, caching, authentication, metrics) show up in essentially every backend service ever built." Decorator is the standard approach to add these without polluting the core business logic class, and mirrors middleware patterns in frameworks like Express.js and Spring filter chains.
- Flyweight-style thinking appears constantly, often invisibly: "Java's own `Integer` caching and String pool are built on it, and any system caching reference data (categories, configuration objects, lookup tables) instead of rebuilding it per request is applying the same idea." Recognizing safe-to-share versus unique-to-instance data addresses real performance concerns.
- "The moment a 'just one more special case' request adds a flag to the original class instead of a new wrapping layer, the pattern's core benefit, that the base class never needs to change, has already been lost." This trap emerges easily under deadline pressure when requesting AI assistance.

## Real-World Use Cases

- **Decorator, the everyday idea:** A coffee order built up one add-on at a time (espresso, then milk, then mocha, then whip), or a pizza built up the same way (base, then cheese, then olives, then jalapeños), where each addition changes cost and description without altering what came before it.
- **Coffee shop ordering, coded:** A backend for a coffee chain that must support repeatable add-ons (double mocha) and add-ons affecting the base price (a "large" size), which a fixed list of condiments attached to `Beverage` cannot cleanly support.
- **Decorator in real tools:** `BufferedReader` wrapping a `FileReader` to add `readLine()` and faster chunked reading, without changing what `FileReader` itself does; `Collections.synchronizedList()` and `Collections.unmodifiableList()` wrapping a plain list to add thread-safety or a read-only restriction.
- **Decorator in a real backend example:** A `NotificationService` layered with a logging decorator, a retry decorator, and a rate-limiting decorator, where adding a fourth concern (an audit copy) means writing one new decorator class, never touching the original sender or any existing decorator.
- **Flyweight, the everyday idea:** A library owning one physical copy of a popular book that hundreds of students borrow across the year, instead of purchasing a new copy for every single reader.
- **Flyweight, the PUBG problem:** A battle royale game with 100,000 bullets in play at once, where sharing each gun type's color, weight, and image across every bullet fired from that gun avoids roughly 110 MB of duplicated memory.
- **Flyweight in production:** Java's `Integer.valueOf()` caching small integer values so that `Integer a = 100` and `Integer b = 100` can share the same object, and a food delivery backend sharing one `Category` object (name, icon, tax rate) across millions of order line items instead of rebuilding it per item.

## Connection to the Upcoming Class

- Today's two patterns solved problems about a single object: how to keep adding behavior to it without touching its class (Decorator), and how to avoid duplicating its heaviest data across huge numbers of near-identical copies (Flyweight).
- The next session, per the lecture's own closing bridge, moves into Behavioral Patterns, starting with Strategy and Observer.
- This is a genuine shift in the kind of question being asked. Creational patterns asked how objects get created; Structural patterns (Adapter, Facade, Decorator, Flyweight) asked how objects are organized, connected, wrapped, or shared. Behavioral patterns ask a different question again: how objects actually talk to and coordinate with each other once they exist and are wired together.
- Strategy, in particular, tends to build on the same instinct Decorator relied on, defining a shared interface and swapping in different implementations, but applies it to swapping an algorithm or behavior at runtime rather than layering additional behavior on top of an object.

## Prerequisites from the Previous Class

Recall the following from the Adapter/Facade session before this one:

- **Structural Patterns framing:**
  - Adapter and Facade were both introduced as ways of "fitting things together": Adapter by translating between two incompatible interfaces, Facade by hiding a messy multi-step process behind one simple entry point.
  - This session's two patterns stay in the same Structural bucket but solve different problems again: adding behavior to a single object over time, and managing large numbers of similar objects efficiently.
- **Shared-interface thinking:**
  - `BankAPI` let `PhonePe` talk to any bank the same way, and `ChatModel` let an app talk to any LLM provider the same way.
  - This session applies the identical move twice: `Beverage` lets every base drink and every add-on be treated identically, and `NotificationService` lets the base sender and every decorator around it be treated identically.
- **The Open/Closed Principle:**
  - Adapter's core rule was that adding a new bank should mean writing a new adapter class, never editing `PhonePe`. The AI Corner in that session tested whether an if/else had crept back into the client.
  - This session applies the same rule to Decorator: adding a new add-on or a new cross-cutting concern should mean writing a new decorator class, never adding a new flag or `if` check inside the base class. This session's own AI Corner tests exactly this.
- **Single Responsibility:**
  - Facade's motivating problem was `Amazon.orderPlace()` doing the job of four unrelated subsystems itself.
  - This session's coffee shop problem and notification service problem are the same shape again: a base class threatening to absorb responsibilities (add-on combinations, logging, retries, rate limiting) that should instead live in their own separate, wrapped layers.
- **What carries forward directly:**
  - Adapter and Facade both dealt with fitting already-existing pieces together. Decorator and Flyweight assume that comfort with wrapping and interfaces, and extend it: Decorator wraps the same object repeatedly to add behavior, while Flyweight splits a single conceptual object into a shared part and a unique part.

## Key Concept Preview

> **Each decorator layer changes only the result, never the object underneath it.** Whether it is cost and description in the coffee example, or logging and retry behavior in the notification example, every wrapping layer leaves the object it wraps completely unchanged.

> **Calling a decorated object dives inward, then unwinds back outward.** A call like `cost()` on a fully wrapped object travels down through every layer to the innermost base object first, then the results travel back up, with each layer adding its own contribution on the way out. This recursive shape is worth sitting with before class, since it is easy to describe but easy to trace incorrectly on paper.

> **Intrinsic versus extrinsic is the one question to ask before optimizing memory for repeated objects.** Data that stays identical across many objects (a bullet's color, weight, image) is intrinsic and safe to share. Data that is different for every single instance (a bullet's current position) is extrinsic and must stay separate.

> **A factory or cache is what actually enforces sharing in Flyweight, not just good intentions.** Without something checking "has this shared object already been built" before creating a new one, the intrinsic/extrinsic split alone does nothing to save memory.

> **The clearest warning sign that a Decorator design is regressing is new fields or new `if` checks appearing on the base class.** The moment a "just one more special case" request adds a flag to the original class instead of a new wrapping layer, the pattern's core benefit, that the base class never needs to change, has already been lost.

## What You Will Walk Away With

| Learning Outcome |
|-------------------|
| Explain the Decorator idea (wrapping a base object with additional behavior, one layer at a time, without altering the object underneath) using a non-software example first. |
| Implement a Decorator using a shared interface, a base implementation, and one wrapper class per additional behavior, including tracing how a chained method call resolves inward and back out. |
| Recognize Decorator already in use in a language's standard library or common tooling, such as `BufferedReader` wrapping `FileReader` or list-wrapping utilities in `Collections`. |
| Design a layered solution for cross-cutting concerns (logging, retries, rate limiting) around a core service, without editing the core service itself for each new concern. |
| Explain the Flyweight idea (splitting an object into shared intrinsic data and unique extrinsic data) and identify which fields belong in each category for a given scenario. |
| Implement a Flyweight using a shared, cached object built through a factory, and a small per-instance object holding only unique data. |
| Evaluate whether an AI-generated or teammate-written change to a Decorator design preserves the pattern, or quietly reintroduces flags and conditionals into the base class. |
