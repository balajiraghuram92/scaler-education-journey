# Lecture Notes: Introduction to OOP & Fundamentals
**Date:** June 22, 2026  
**Topic:** Object-Oriented Programming (OOP-1) — Classes, Objects & Encapsulation

---

## Agenda
- **Intro to OOP**
- **2 Fundamentals / Principles of OOP:**
  1. Abstraction
  2. Polymorphism
  3. Encapsulation
  4. Inheritance
- *Start time:* 9:08 PM

---

## 1. Entity in OOP
An **Entity** is something real that has its own **data + Actions**.
- *Example:* Uber system
  - Driver
  - Customer (Rider)
  - Ride (Trip)
  - Vehicle
  - Payment

---

## 2. Abstraction
- **Principle of OOP.**
- **Definition:** To give a brief, high-level idea about something without overwhelming details.
- Four core principles/pillars of OOP:
  - Abstraction (Overarching principle)
  - Encapsulation
  - Inheritance
  - Polymorphism

---

## 3. Class & Object
- **Class:** A blueprint of an Entity.
  - Entity (Idea) $\rightarrow$ Class (Blueprint).
  - Takes up little to no memory (just bytecode/definition).
- **Object:** A real instance created from the class blueprint.
  - Takes up actual memory on the heap.
- *Example:* Uber `Driver` class $\rightarrow$ Instances (Objects) `D1`, `D2`, `D3`.

### Class Members
A class consists of:
1. **Attributes (Fields):** Data holding state.
2. **Functions (Methods / Behaviour):** Actions the object can perform.

### Java Syntax Example
```java
public class Driver {
    long driverId;
    String name;
    double rating;
    boolean isOnline;

    void goOffline() {
        // logic to go offline
    }

    void goOnline() {
        // logic to go online
    }

    void acceptRide() {
        // logic to accept ride
    }
}
```

Memory reference example:
```java
Driver d1 = new Driver();
d1.name = "Rahul";
Driver d2 = d1; // d2 points to the same object on the heap
```

---

## 4. Constructor
- A special method that constructs the object with given values.
- If no values are given, it uses default values.
- **Default Constructor:** Always no-argument.
- **Parameterized Constructor:**
```java
public Driver(String name, float rating, long driverId) {
    this.name = name;
    this.driverId = driverId;
    this.rating = rating;
}

Driver d1 = new Driver("Yash", 5.0f, 1232);
```

---

## 5. Static Keyword
- Used to define members shared across all objects (class-level), rather than belonging to a single instance.
- *Example:* `int totalDrivers;` (shared counter across all Driver objects).
- *Static Method Example:*
```java
public static boolean isAboveAgeLimit(int age) {
    return age > 18;
}
```

---

## 6. Encapsulation
- **Capsule using class.**
- **Jobs of Encapsulation:**
  1. To hold different types of things (data + behaviour) together.
  2. To protect internal state and prevent direct outside access.
- **Access Modifiers:**
  - `private`: Only self-class can access it.
  - `public`: Everyone can access it.
  - `protected`: Package-private + subclasses.
  - `default` (package-private): Accessible within the same package.
