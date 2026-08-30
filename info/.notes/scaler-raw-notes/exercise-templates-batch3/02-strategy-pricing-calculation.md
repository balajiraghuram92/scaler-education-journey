# Refactoring Pricing Calculation with the Strategy Pattern

Source folder: `1773391191_c42834cd58c828f3 / Pricing_Strategy-solution`

## Problem Statement

You are tasked with refactoring a pricing calculator for a ride-sharing app. The existing pricing manager class (`PricingManager`) uses a monolithic approach to calculate ride prices based on different strategies: distance-based, time-based, and surge pricing. The goal is to refactor the code to use the Strategy pattern, allowing for more flexible pricing strategies and better maintenance.

## Detailed Requirements

1. **Create the `PricingStrategy` Interface**: Begin by creating the `PricingStrategy` interface. This interface should define a method for calculating the ride price.

2. **Implement Concrete Pricing Strategy Classes**: Create concrete classes that implement the `PricingStrategy` interface. These classes will represent different pricing strategies, including:
   - **Distance-Based Pricing**: Calculate the price based on the distance traveled.
     - Base fare: $5.0
     - Rate per kilometer: $2.0
   - **Time-Based Pricing**: Calculate the price based on the duration of the ride.
     - Base fare: $5.0
     - Rate per minute: $0.5
   - **Surge Pricing**: Implement surge pricing logic to increase the ride price during peak hours.
     - Surge multiplier: 2.0 (e.g., 2x the base price)

3. **Refactor the `PricingManager` Class**: Refactor the existing `PricingManager` class by removing the hardcoded pricing logic and instead delegating the price calculation to the selected pricing strategy. The `PricingManager` class should now use composition to hold an instance of the selected pricing strategy.

4. **Test Your Refactored Code**: Write test cases to ensure that the refactored code produces accurate pricing calculations for each pricing strategy. You should test different scenarios to verify that each strategy behaves as expected.

## Graded Contract (from tests)

- **3 concrete strategy classes** implementing `PricingStrategy`:
  - `DistanceBasedPricingStrategy`
  - `TimeBasedPricingStrategy`
  - `SurgePricingStrategy`
- `PricingStrategy` interface has:
  - `PricingType supportsType()` method
  - `Double calculatePrice(RideDetails rideDetails)` method
- `PricingManager` has:
  - A private field of type `PricingStrategy`
  - Constructor accepting `PricingType` and `PricingStrategy` (2 parameters)
  - `Double calculatePrice(RideDetails rideDetails)` method that delegates to the strategy
- **Test values** (with RideDetails: distance=10.0 km, duration=60 minutes):
  - DISTANCE_BASED: expects 25.0 (BASE_FARE 5.0 + 2.0 * 10.0)
  - TIME_BASED: expects 35.0 (BASE_FARE 5.0 + 0.5 * 60)
  - SURGE: expects 10.0 (BASE_FARE 5.0 * 2.0)

## Learner Template

### Interface

```java
package com.assignment.question;

public interface PricingStrategy {
    PricingType supportsType();

    Double calculatePrice(RideDetails rideDetails);
}
```

### Concrete Strategy Classes (skeleton)

```java
package com.assignment.question;

public class DistanceBasedPricingStrategy implements PricingStrategy {
    private static final double PER_KILOMETER_RATE = 2.0;

    @Override
    public PricingType supportsType() {
        // TODO: return the appropriate PricingType
    }

    @Override
    public Double calculatePrice(RideDetails rideDetails) {
        // TODO: implement distance-based pricing calculation
        // Hint: Use BASE_FARE constant and PER_KILOMETER_RATE
    }
}
```

```java
package com.assignment.question;

public class TimeBasedPricingStrategy implements PricingStrategy {
    private static final double PER_MINUTE_RATE = 0.5;

    @Override
    public PricingType supportsType() {
        // TODO: return the appropriate PricingType
    }

    @Override
    public Double calculatePrice(RideDetails rideDetails) {
        // TODO: implement time-based pricing calculation
        // Hint: Use BASE_FARE constant and PER_MINUTE_RATE
    }
}
```

```java
package com.assignment.question;

public class SurgePricingStrategy implements PricingStrategy {
    private static final double SURGE_MULTIPLIER = 2.0;

    @Override
    public PricingType supportsType() {
        // TODO: return the appropriate PricingType
    }

    @Override
    public Double calculatePrice(RideDetails rideDetails) {
        // TODO: implement surge pricing calculation
        // Hint: Use BASE_FARE constant and SURGE_MULTIPLIER
    }
}
```

### Manager Class (skeleton)

```java
package com.assignment.question;

public class PricingManager {
    static final double BASE_FARE = 5.0;

    private PricingType pricingType;
    private PricingStrategy pricingStrategy;

    public PricingManager(PricingType pricingType, PricingStrategy pricingStrategy) {
        // TODO: initialize both fields
    }

    public Double calculatePrice(RideDetails rideDetails) {
        // TODO: delegate to the strategy
    }
}
```

## Deliberately Left Out (for the learner to design)

- Implementation logic for `calculatePrice` in each concrete strategy (learner must understand pricing formulas)
- Proper initialization in the `PricingManager` constructor
- The `PricingType` enum (already provided in the repo)
- The `RideDetails` model class with getDistance() and getDuration() getters (already provided in the repo)
- Field initialization and constructor implementation details

