Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/rJSH0zTGfe

# Library Management System Lab: OOP-4 Overview

## Core Purpose
This lab synthesizes Object-Oriented Programming concepts from three prior classes by applying them to a new domain—a Library Management System. As stated in the material: "every concept from the last three classes gets picked up and used together on a system you have never seen before."

## Three Milestones

**Milestone A** focuses on user hierarchy using inheritance, abstract classes, and constructor patterns.

**Milestone B** introduces lending capabilities through interfaces and polymorphism, distinguishing between classes that *are* something versus those that *can do* something.

**Milestone C** integrates all components into a complete management system using collections and method overloading.

## Key Design Distinction

The material emphasizes a critical decision criterion: "Inheritance models what something IS. An interface models what something CAN DO." For example, `Member` and `Librarian` share an inheritance relationship (both *are* users), while `TextBook` and `Magazine` implement a `Lendable` interface (both *can be* lent).

## Concepts Applied

The lab requires students to work with abstract classes preventing direct instantiation, `static` fields for system-wide counters, `final` fields for immutable IDs, polymorphic method dispatch, and all three constructor types (default, parameterized, and copy).

## Stated Learning Outcomes

Students completing this lab should identify appropriate OOP structures from requirements, choose correctly between abstract classes and interfaces, implement hierarchies with proper constructor chaining, use polymorphism without type-checking, and apply access modifiers and field qualifiers appropriately.