Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/SkgIVwB0Nzx

# Pre-Reads-LLD-SOLID-Principles.md - HackMD

---

title: Pre-Reads-LLD-SOLID-Principles.md
tags: [Final]

---

| PRE-READ | Low-Level Design (LLD) | Backend LLD: SOLID Design Principles for Extensible Systems with AI Integrations |
|----------|-------------------------|-----------------------------------------------| 

## Context 

The previous module covered core object-oriented programming: encapsulation, inheritance, polymorphism, and the practical distinction between `extends`, `implements`, and composition, applied hands-on to a layered Uber design (abstract classes for `User` and `Vehicle`, interfaces for `PaymentGateway` and `Dispatchable`). That module established the tools available in Java's type system. This session does not introduce new syntax or new Java keywords. It introduces judgment: when to reach for which of those tools, and why one design choice is preferable to another as a system is expected to grow. The session is built around a single running example, a `Bird` class hierarchy, deliberately constructed in a naive way at the start and then corrected one principle at a time, so that each of the five SOLID principles is motivated by a concrete failure before it is formally named or defined.

## Overview

| Segment | What is covered | Concepts in play |
|---------|------------------|-------------------|
| The Naive Design Problem | Building a single `Bird` class holding all attributes and a branching `fly()` method, and observing how it degrades as bird types increase | Conditional branching, code duplication, readability |
| Single Responsibility Principle (SRP) | Identifying when a method or class is carrying more than one unrelated reason to change | Monster methods, utility-class overload |
| Open/Closed Principle (OCP) | Distinguishing extending a system from modifying its existing, working code when new requirements arrive | Regression risk, extension vs. modification |
| Refactoring `Bird`: Abstract Class | Rebuilding the hierarchy using an abstract class and an abstract `fly()` method, and encountering the case of a bird that cannot fly | Abstract classes, forced method overrides, runtime failure |
| Liskov Substitution Principle (LSP) | Establishing that a subtype must be safely usable anywhere its parent type is expected, without special-case handling | Substitutability, behavioral contracts |
| Interface Segregation Principle (ISP) | Recognizing when a single interface bundles unrelated behaviors and forces unwanted implementations | Interface design, capability-based modeling |
| Dependency Inversion Principle (DIP) | Making concrete classes depend on abstractions rather than on each other directly | Interfaces as contracts, coupling |
| Dependency Injection (not itself a SOLID principle) | Supplying a class's dependencies from outside rather than having the class construct them itself | Constructor injection, inversion of control |

## Why This Session Matters

Most engineers, without being taught to, already sense when a codebase feels difficult to work with: a function that has grown to do too much, a change in one place that unexpectedly breaks something unrelated, a new requirement that seems to demand editing code that already worked. The five SOLID principles are a way of naming these instincts precisely, so that a design problem can be diagnosed and discussed in specific terms rather than a vague sense that "this code is messy." This session is deliberately structured so that each principle is felt before it is named. The `Bird` hierarchy is allowed to break in a specific, predictable way, and only after that failure is examined is the corresponding principle introduced as the formal fix. The intent is that the definitions are easy to recall later because they are anchored to a concrete failure that was worked through directly, not memorized as an abstract rule.

## Real-World Use Cases

- **Single Responsibility Principle:** An employee expected to simultaneously be the accountant, the IT support, the office cleaner, and the receptionist will inevitably drop something the moment two of those responsibilities compete for attention at once. A class or method carrying multiple unrelated responsibilities fails in the same way, for the same reason.

- **Open/Closed Principle:** A well-designed house allows a new room to be added without demolishing the kitchen to do it. A system designed for extension allows a new feature, such as a new bird type or a new discount type, to be added as new code, without editing a method that already had working, tested behavior.

- **Liskov Substitution Principle:** A job description for "Backend Developer" states that the role must be able to write REST APIs. Anyone hired into that role is expected to deliver on that promise without the rest of the team needing to handle them differently. A subtype that cannot safely stand in for its parent type, without extra checks or special handling, breaks that same expectation.

- **Interface Segregation Principle:** A fixed thali forces every customer to take the full combination of courses, whether they want all of it or not. An à la carte menu lets a customer order exactly what they need. An interface that bundles several unrelated capabilities into one contract forces every implementer to take on obligations it may not actually have.

- **Dependency Inversion Principle:** A phone charger does not wire itself directly into the power plant; it plugs into a wall socket, a standard interface both sides agree to. A class that depends directly on another concrete class is wired the way the charger is not meant to be wired.

- **Dependency Injection:** A new employee joining a company is not expected to bring their own laptop, desk, and chair; the company supplies all of it on day one, and the employee simply plugs in and starts working. A class that receives its dependencies from outside, rather than constructing them itself, is set up to work the same way.

## Connection to the Upcoming Class

The `FlyingBehaviour` design arrived at by the end of this session, where flying is extracted into its own interface and supplied to a bird rather than hard-coded inside it, is already a named, well-established design pattern. The way a framework such as Spring performs dependency injection automatically also follows a named pattern of its own. Both are the subject of the next class, and both will be easier to follow because this session builds the underlying reasoning manually, by hand, before either pattern is named.

## Prerequisites from the Previous Class

Confirm the following from Module 1 before this session, since today's material is built directly on top of it without re-explaining it from scratch:

- **Encapsulation, inheritance, polymorphism:** The three foundational OOP concepts, and how a subclass can be substituted for its parent type in code that expects the parent type.

- **`extends` vs. `implements`:** A class can `extend` exactly one other class in Java, but can `implement` as many interfaces as it genuinely needs.

- **Abstract classes:** A class that can declare abstract methods, methods with no body, that every concrete subclass is then forced to override and implement.

- **Composition:** Building a class's behavior by holding a reference to another object and delegating to it, as an alternative to inheriting that behavior.

## Key Concept Preview

Three ideas worth sitting with before the session:

> **A method with many unrelated reasons to change is a Single Responsibility Principle violation, not simply a long method.** Length by itself is not the problem; a long method built from steps of one coherent algorithm can still respect SRP. The violation is specifically when the reasons the method might need to change are unrelated to one another.

> **"Open for extension, closed for modification" means a new requirement should be met with new code, not edits to code that already worked.** Editing a shared method that already has passing tests introduces the risk of a regression, breaking something that used to work, purely to accommodate something unrelated.

> **Liskov Substitution is about a promise being kept, not about inheritance syntax being valid.** Code that compiles without error can still violate LSP if a subtype requires special handling, such as a `try-catch` or a type check, before it can safely be used wherever its parent type is expected.

## What You Will Walk Away With

| Learning Outcome |
|-------------------|
| Recognize a Single Responsibility Principle violation, including the specific traps of excessive branching, monster methods, and garbage-drawer utility classes. |
| Distinguish an extension of a system from a modification of its existing code, and explain why modification of shared, working code carries regression risk. |
| Rebuild a class hierarchy using an abstract class and abstract methods, and identify the failure mode, the "Penguin problem," that arises when a subtype cannot honestly implement a forced method. |
| Explain Liskov Substitution Principle in terms of safe substitutability, and identify when a subtype requires special-case handling that breaks that substitutability. |
| Identify when an interface has been designed too broadly, and split it into smaller, capability-focused interfaces consistent with Interface Segregation Principle. |
| Explain Dependency Inversion Principle, and rewrite a direct dependency between two concrete classes so that both instead depend on a shared abstraction. |
| Distinguish Dependency Injection from Dependency Inversion Principle, and explain why the former is a natural consequence of the latter rather than a sixth SOLID letter. |