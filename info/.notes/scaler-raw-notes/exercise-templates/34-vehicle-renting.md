# Vehicle Renting System

Source folder: 1773391699_fb8c24dadb0c9d74/Vehicle_Renting_-solution

## Problem Statement

You are tasked with implementing a vehicle rental system that allows customers to rent cars and bicycles. You need to create classes for cars and bicycles, ensuring they implement a common interface for rental operations. The Rentable interface should declare methods for renting and returning items. Both Car and Bicycle classes must implement this interface with public fields for rental status and methods that manage rental state. The system should prevent double-renting and handle return operations correctly.

## Graded Contract (from tests)

- **Rentable interface**: Must declare methods `rent()` and `returnItem()`
- **Car class**: Must implement Rentable; have public boolean field `isRented`; constructor `(String carModel)`; override `rent()` and `returnItem()` methods that manage isRented state
- **Bicycle class**: Must implement Rentable; have public boolean field `isRented`; constructor `(String bicycleModel)`; override `rent()` and `returnItem()` methods that manage isRented state
- Tests verify state management: renting sets isRented to true, returning sets it to false, double-renting or returning a non-rented item is handled

## Learner Template

```java
package org.example;

public interface Rentable {
    void rent();
    void returnItem();
}
```

```java
package org.example;

public class Car implements Rentable {
    // TODO: Declare field for carModel (package-private or private)
    public boolean isRented;

    public Car(String carModel) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void rent() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void returnItem() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

public class Bicycle implements Rentable {
    // TODO: Declare field for bicycleModel (package-private or private)
    public boolean isRented;

    public Bicycle(String bicycleModel) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void rent() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void returnItem() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field carModel/bicycleModel declaration and initialization
- Constructor bodies for field initialization and isRented default state
- Logic to check if already rented before renting
- Logic to check if currently rented before returning
- Output messages (println statements)
- Main method if any

