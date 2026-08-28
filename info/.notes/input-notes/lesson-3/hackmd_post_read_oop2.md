# Post-Read: Complete Encapsulation, Inheritance & Object Architecture

**Topic:** Backend LLD: OOP-2: Access Modifiers, Immutability, Copy Constructors, Inheritance & Object Class  
**Source:** [HackMD Post-Read (ryg_vFyOzGe)](https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/ryg_vFyOzGe)

---

## 1. Complete Encapsulation & Access Matrix

Access modifiers regulate visibility across classes, packages, and inheritance hierarchies:

| Modifier | Class | Package | Subclass (Diff Pkg) | World |
| :--- | :---: | :---: | :---: | :---: |
| `private` | Yes | No | No | No |
| `default` (package-private) | Yes | Yes | No | No |
| `protected` | Yes | Yes | Yes | No |
| `public` | Yes | Yes | Yes | Yes |

---

## 2. Constructor Chaining (`this(...)` and `super(...)`)

Constructor chaining allows constructor reuse within the same class (`this`) or parent class (`super`).

### Critical Rules:
1. `this(...)` or `super(...)` must be the **very first statement** in a constructor body.
2. `this(...)` and `super(...)` cannot both be called explicitly in the same constructor.

### Implementation:
```java
public class Driver {
    private static int totalRegisteredDrivers = 0;
    
    private final long driverId;
    private String name;
    private double rating;
    private boolean isOnline;

    // Master Constructor
    public Driver(long driverId, String name, double rating, boolean isOnline) {
        this.driverId = driverId;
        this.name = name;
        this.rating = rating;
        this.isOnline = isOnline;
        totalRegisteredDrivers++;
    }

    // Chained Partial Constructor
    public Driver(long driverId, String name) {
        this(driverId, name, 0.0, false);
    }

    // Chained Default Constructor
    public Driver() {
        this(0L, "Anonymous", 0.0, false);
    }
}
```

---

## 3. Immutability Pattern

An immutable class guarantees that its internal state cannot change after instantiation.

### Recipe for Immutability:
1. Declare the class as `final` so it cannot be subclassed or overridden.
2. Make all fields `private` and `final`.
3. Do not provide any setter methods.
4. If mutable objects are passed in or returned, perform defensive copying.

```java
public final class Fare {
    private final double baseFare;
    private final double surgeMultiplier;

    public Fare(double baseFare, double surgeMultiplier) {
        this.baseFare = baseFare;
        this.surgeMultiplier = surgeMultiplier;
    }

    public double getFinalFare() {
        return baseFare * surgeMultiplier;
    }

    public double getBaseFare() {
        return baseFare;
    }

    public double getSurgeMultiplier() {
        return surgeMultiplier;
    }
}
```

---

## 4. Deep Copy via Copy Constructors

```java
public class Route {
    private String source;
    private String destination;
    private double distanceKm;

    public Route(String source, String destination, double distanceKm) {
        this.source = source;
        this.destination = destination;
        this.distanceKm = distanceKm;
    }

    // Copy Constructor for Route
    public Route(Route other) {
        this.source = other.source;
        this.destination = other.destination;
        this.distanceKm = other.distanceKm;
    }

    public void setSource(String source) { this.source = source; }
    public String getSource() { return source; }
}

public class Trip {
    private String tripId;
    private double fareAmount;
    private Route route;

    public Trip(String tripId, double fareAmount, Route route) {
        this.tripId = tripId;
        this.fareAmount = fareAmount;
        this.route = route;
    }

    // Deep Copy Constructor
    public Trip(Trip other) {
        this.tripId = other.tripId;
        this.fareAmount = other.fareAmount;
        // Instantiate a separate Route instance to avoid shared references
        this.route = new Route(other.route);
    }

    public Route getRoute() { return route; }
}
```

---

## 5. Inheritance Hierarchy (`extends` and `super`)

```java
public abstract class Vehicle {
    protected String vehicleId;
    protected String licensePlate;
    protected int capacity;

    public Vehicle(String vehicleId, String licensePlate, int capacity) {
        this.vehicleId = vehicleId;
        this.licensePlate = licensePlate;
        this.capacity = capacity;
    }

    public abstract double calculateFare(double distanceKm);
}

public class Car extends Vehicle {
    private static final double PER_KM_RATE = 15.0;

    public Car(String vehicleId, String licensePlate) {
        super(vehicleId, licensePlate, 4);
    }

    @Override
    public double calculateFare(double distanceKm) {
        return distanceKm * PER_KM_RATE;
    }
}
```

---

## 6. The `equals()` and `hashCode()` Contract

When overriding `equals()`, you must always override `hashCode()`:
- If `o1.equals(o2)` is `true`, then `o1.hashCode() == o2.hashCode()` must also be `true`.
- Failure to adhere to this contract breaks hash-based collections like `HashMap` and `HashSet`.
