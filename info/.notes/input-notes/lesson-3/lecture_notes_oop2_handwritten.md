# Lecture Notes: OOP in Java (Access Modifiers, Chaining, Copy Constructors & Final)

**Lecture Date:** June 24, 2026  
**Topic:** Access Modifiers, Constructor Chaining, Copy Constructors, Final Keyword, Inheritance  
**Source:** Class Board Notes (`Note_Jun_24__2026_8_48_30_PM.pdf`)

---

## Agenda
1. Access Modifiers
2. Constructor Chaining
3. Copy Constructors (Shallow vs. Deep Copy)
4. Inheritance & The `final` Keyword

---

## 1. Access Modifiers Summary
Defines visibility boundaries across classes, packages, and inheritance chains:

- **`private`**: Accessible only within the same class.
- **`default` (no modifier)**: Accessible within the same package.
- **`protected`**: Accessible within the same package and by child classes (subclasses) across packages.
- **`public`**: Accessible everywhere.

---

## 2. Constructor Overloading & Chaining

### The Problem:
Writing multiple constructors with duplicated initialization logic leads to maintenance overhead and redundant code when updating counters or defaults.

### The Solution: `this(...)`
Chaining constructors using `this(...)` ensures all object creation routes through a single master constructor.

> **Crucial Rule:** `this(...)` must always be the **first line** inside a constructor.

```java
public class Driver {
    static int totalCount;
    long id;
    String name;
    double rating;
    boolean isOnline;

    // Master Constructor
    public Driver(long id, String name, double rating, boolean isOnline) {
        this.id = id;
        this.name = name;
        this.rating = rating;
        this.isOnline = isOnline;
        Driver.totalCount++;
    }

    // Overloaded Constructor 1 (Chained)
    public Driver(long id, String name) {
        this(id, name, 0.0, false);
    }

    // Overloaded Constructor 2 (Default / Chained)
    public Driver() {
        this(0L, null, 0.0, false);
    }
}
```

---

## 3. The `final` Keyword

The `final` keyword can be applied at three distinct levels:

1. **`final` Variable**: Constant value; cannot be reassigned once initialized.
   ```java
   final long driverId = 101L;
   // this.driverId++; // ERROR: cannot reassign final variable
   ```
2. **`final` Method**: Prevents method overriding by subclasses.
   ```java
   public final int getDriverId() {
       return this.id;
   }
   ```
3. **`final` Class**: Prevents inheritance; no class can extend a `final` class.
   ```java
   public final class Student {
       // Cannot be extended by any subclass
   }
   ```

---

## 4. Copy Constructors: Shallow Copy vs. Deep Copy

### The Shallow Copy Hazard
When copying an object that references other objects, copying just the reference field causes both objects to point to the exact same heap memory address:

```java
Trip originalTrip = new Trip();
originalTrip.tripId = "101x";
originalTrip.fare = 410.0;

Route originalRoute = new Route();
originalRoute.source = "Indiranagar";
originalRoute.destination = "HAL";
originalRoute.distance = 2.0;
originalTrip.route = originalRoute;

// Shallow Copy:
Trip tripCopy = new Trip();
tripCopy.tripId = originalTrip.tripId;
tripCopy.fare = originalTrip.fare;
tripCopy.route = originalTrip.route; // SHARED REFERENCE

// Modifying copy mutates original:
tripCopy.route.source = "Delhi";
// originalTrip.route.source is now ALSO "Delhi"!
```

### Deep Copy Solution
Use a copy constructor that explicitly instantiates a fresh inner object:

```java
public class Trip {
    String tripId;
    double fare;
    Route route;

    // Standard Constructor
    public Trip(String tripId, double fare, Route route) {
        this.tripId = tripId;
        this.fare = fare;
        this.route = route;
    }

    // Deep Copy Constructor
    public Trip(Trip originalTrip) {
        this.tripId = originalTrip.tripId;
        this.fare = originalTrip.fare;
        // Explicitly create a new Route object in heap memory
        this.route = new Route(
            originalTrip.route.source,
            originalTrip.route.destination,
            originalTrip.route.distance
        );
    }
}
```
