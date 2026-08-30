Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/Bk0Qmcqzfl

# Post-Reads - OOP-3 Polymorphism, Interfaces and Abstract Classes

## Document Summary

This comprehensive guide covers the fourth lecture in a Backend Low-Level Design course, consolidating Object-Oriented Programming's three pillars. The material spans five major topics:

**Runtime Polymorphism** explores method overriding, where the JVM dispatches to the correct implementation based on actual object type at execution time, not reference type. The document emphasizes that "reference type → which methods you CAN call (decided at compile time)" while "actual type → which implementation RUNS (decided at runtime)."

**Compile-Time Polymorphism** examines method overloading, where the compiler resolves which overloaded method to invoke before execution based on argument types and count. The guide clarifies that return type and variable names cannot differentiate overloads because they don't exist when the compiler must make its decision.

**Abstract Classes** represent ideas that should never be instantiated directly—concepts like Vehicle or Shape. They enforce obligations through abstract methods while allowing shared concrete implementation.

**Interfaces** establish pure contracts for capabilities (CAN-DO relationships) rather than type relationships (IS-A). The PaymentGateway example demonstrates how interfaces enable loose coupling across unrelated class hierarchies where multiple inheritance of implementation would create ambiguity.

**Composition vs. Inheritance** argues that HAS-A relationships often outperform IS-A relationships, reducing coupling and providing selective use of functionality rather than inheriting everything a parent class contains or gains.

The document uses consistent examples throughout: a rideshare dispatch system with vehicles, drivers, and payment processing, making abstract concepts concrete and immediately applicable.