# Strategy Pattern for Stock Trading Indicators

Source folder: `1773391186_dae477aff1fe2f5c / Strategy_Stocks-solution`

## Problem Statement

You are tasked with refactoring a stock trading application. The application currently calculates various trading indicators such as moving averages, momentum, and volatility. These indicators are used to make decisions about buying, selling, or holding stocks. However, the current implementation relies on a single class, making it challenging to extend and maintain as new indicators are added. To address this, you need to refactor the application to use the Strategy pattern. This pattern allows you to encapsulate each trading indicator as a separate strategy and easily switch between them without modifying the core trading algorithm.

## Detailed Requirements

1. **Create a Strategy Interface**: Define a common interface, e.g., `TradingIndicatorStrategy`, that declares a method for calculating the trading indicator and another method for checking if the strategy supports a specific indicator type.

2. **Implement Concrete Strategies**: Create concrete strategy classes for each trading indicator (Moving Averages, Momentum, and Volatility). Implement the methods defined in the `TradingIndicatorStrategy` interface for calculating the respective indicators. Ensure that each strategy class also implements the `supportsType` method to specify which indicator type it supports.

3. **Refactor `StockTradingManager`**: Modify the `StockTradingManager` class to accept a `TradingIndicatorStrategy` instead of a `TradingStrategyType`. The `calculateIndicator` method should delegate the calculation to the selected strategy.

4. **Copy Existing Logic**: For each strategy, copy the existing indicator calculation logic from the original `StockTradingManager` class into the corresponding strategy class.

5. **Test Your Implementation**: Write test cases to ensure that each strategy correctly calculates the corresponding indicator, and that the `StockTradingManager` class works seamlessly with different strategies.

### Trading Indicator Calculations

- **Moving Averages**: Calculate the average of a stock's price and its previous price. It can help identify trends by smoothing out price fluctuations.
  - Formula: `(current_price + previous_price) / 2`

- **Momentum**: Momentum is the difference between the current stock price and its previous price. It provides insights into the stock's rate of change.
  - Formula: `current_price - previous_price`

- **Volatility**: Volatility measures the magnitude of price fluctuations in a stock. It calculates the absolute difference between the current price and the previous price.
  - Formula: `|current_price - previous_price|`

## Graded Contract (from tests)

- **3 concrete strategy classes** implementing `TradingIndicatorStrategy`
- `TradingIndicatorStrategy` interface has:
  - `TradingStrategyType supportsType()` method
  - `Double calculateIndicator(Stock stock)` method
- `StockTradingManager` has:
  - A private field of type `TradingIndicatorStrategy`
  - Constructor accepting `TradingIndicatorStrategy` (or alternatively, both `TradingStrategyType` and `TradingIndicatorStrategy`)
  - `Double calculateIndicator(Stock stock)` method that delegates to the strategy
- **Test values** (with Stock: price=100.0, previousPrice=60.0):
  - MOVING_AVERAGES: expects 80.0
  - MOMENTUM: expects 40.0
  - VOLATILITY: expects 40.0

## Learner Template

### Interface

```java
package com.assignment.question;

public interface TradingIndicatorStrategy {
    TradingStrategyType supportsType();

    Double calculateIndicator(Stock stock);
}
```

### Concrete Strategy Classes (skeleton)

```java
package com.assignment.question;

public class MovingAveragesStrategy implements TradingIndicatorStrategy {
    @Override
    public TradingStrategyType supportsType() {
        // TODO: return the appropriate TradingStrategyType
    }

    @Override
    public Double calculateIndicator(Stock stock) {
        // TODO: implement moving averages calculation
    }
}
```

```java
package com.assignment.question;

public class MomentumStrategy implements TradingIndicatorStrategy {
    @Override
    public TradingStrategyType supportsType() {
        // TODO: return the appropriate TradingStrategyType
    }

    @Override
    public Double calculateIndicator(Stock stock) {
        // TODO: implement momentum calculation
    }
}
```

```java
package com.assignment.question;

public class VolatilityStrategy implements TradingIndicatorStrategy {
    @Override
    public TradingStrategyType supportsType() {
        // TODO: return the appropriate TradingStrategyType
    }

    @Override
    public Double calculateIndicator(Stock stock) {
        // TODO: implement volatility calculation
    }
}
```

### Manager Class (skeleton)

```java
package com.assignment.question;

public class StockTradingManager {
    private TradingIndicatorStrategy indicatorStrategy;

    public StockTradingManager(TradingIndicatorStrategy indicatorStrategy) {
        // TODO: initialize the indicatorStrategy field
    }

    public Double calculateIndicator(Stock stock) {
        // TODO: delegate to the strategy
    }
}
```

## Deliberately Left Out (for the learner to design)

- Implementation logic for `calculateIndicator` in each concrete strategy (learner must understand the indicator formulas)
- Proper initialization in the `StockTradingManager` constructor
- The `TradingStrategyType` enum values (already provided in the repo)
- The `Stock` model class (already provided in the repo)

