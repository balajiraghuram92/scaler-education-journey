# Observer Pattern for Stock Trading Platform

Source folder: `1773391231_9f553c4f9e79cc93/Stock_Observer-solution`

## Problem Statement

You are developing a stock trading platform where users need to be notified whenever the price of a particular stock crosses a certain threshold. These notifications should be sent through various channels such as email, SMS, and mobile app notifications. To achieve this, you want to implement the Observer pattern, allowing users to subscribe to stock price updates and receive notifications through multiple channels.

## Detailed Requirements

1. **Review the original class**: Study the `StockTradingManager` class and its dependencies. Understand how it currently handles stock price updates and notifications.

2. **Implement the publisher interface**: You have been provided with a `Publisher` interface. Your task is to implement the methods required by this interface in the `StockTradingManager` class. Remember that the `Publisher` interface is a contract that defines the methods that a class can use to notify observers.

3. **Implement the observer interface**: Design an interface named `Observer` with a method that accepts the stock name and current price as arguments. Observer classes (such as `EmailService`, `SmsService`, `AppService`) will implement this interface to receive notifications.

4. **Modify the publisher**: Refactor the `StockTradingManager` class as required. **Do not modify the constructor** as it used by the tests.

5. **Modify the observers**: Refactor the observer classes to implement the `Observer` interface. Update their existing methods to match the new interface method signature.

6. **Test your implementation**: Run the provided test cases in the `StockTradingManagerTest` class to ensure that your observer pattern implementation is correct. These test cases will check if observers are being notified correctly and if the StockTradingManager behaves as expected.

## Graded Contract (from tests)

- StockTradingManager must **not have any fields** of type `EmailService`, `SmsService`, or `AppService` (loose coupling requirement)
- `Observer` interface must declare exactly **one method with two parameters: `String` (stock name) and `double` (current price)**
- `Publisher` abstract class must implement `ObserverRegistry` interface
- `Publisher` must declare **at least two methods taking a single `Observer` parameter** (for add and remove)
- `Publisher` must declare a `notifyObservers(String stockName, double currentPrice)` method
- `StockTradingManager` must have a **3-parameter constructor** accepting `String stockName`, `double initialPrice`, and `double notificationThreshold`
- `StockTradingManager` must **extend `Publisher`**
- `EmailService`, `SmsService`, and `AppService` must each **implement `Observer`**
- When `StockTradingManager.updateStockPrice(double newPrice)` is called and price exceeds threshold:
  - All registered observers' `notifyObserver(String stockName, double currentPrice)` must be invoked
  - Observers must receive correct stock name and price values
  - `NotificationUtils.sendEmail()`, `NotificationUtils.sendSms()`, and `NotificationUtils.sendPush()` must be called with subject `"Price update for <stockName>"` and message `"New price is <currentPrice>"`

## Graded Contract - ObserverRegistry Interface

The `ObserverRegistry` interface defines the contract that `Publisher` must implement:

```java
public interface ObserverRegistry {
    void addObserver(Observer observer);
    void removeObserver(Observer observer);
    void notifyObservers(String stockName, double currentPrice);
}
```

## Learner Template

```java
// Observer.java
package com.assignment.question;

public interface Observer {
    // TODO: Implement the observer notification method
    // Should accept two parameters: stockName (String) and currentPrice (double)
}
```

```java
// ObserverRegistry.java
package com.assignment.question;

public interface ObserverRegistry {
    void addObserver(Observer observer);

    void removeObserver(Observer observer);

    void notifyObservers(String stockName, double currentPrice);
}
```

```java
// Publisher.java
package com.assignment.question;

import java.util.ArrayList;
import java.util.List;

public abstract class Publisher implements ObserverRegistry {

    private List<Observer> observers = new ArrayList<>();

    // TODO: Implement addObserver method from ObserverRegistry
    
    // TODO: Implement removeObserver method from ObserverRegistry
    
    // TODO: Implement notifyObservers method from ObserverRegistry
    // Should invoke notifyObserver() on each observer with stockName and currentPrice
}
```

```java
// StockTradingManager.java
package com.assignment.question;

public class StockTradingManager extends Publisher {

    private String stockName;
    private double currentPrice;
    private double notificationThreshold;

    public StockTradingManager(String stockName, double initialPrice, double notificationThreshold) {
        this.stockName = stockName;
        this.currentPrice = initialPrice;
        this.notificationThreshold = notificationThreshold;
    }

    // TODO: Implement updateStockPrice method
    // Should update currentPrice and notify observers if price exceeds threshold
}
```

```java
// EmailService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class EmailService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendEmail() with subject "Price update for <stockName>"
    // and message "New price is <currentPrice>"
}
```

```java
// SmsService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class SmsService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendSms() with subject "Price update for <stockName>"
    // and message "New price is <currentPrice>"
}
```

```java
// AppService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class AppService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendPush() with subject "Price update for <stockName>"
    // and message "New price is <currentPrice>"
}
```

## Deliberately Left Out (for the learner to design)

- The exact method signature of `notifyObserver()` in the `Observer` interface (parameters and types)
- The implementation of `addObserver()`, `removeObserver()`, and `notifyObservers()` in `Publisher`
- The implementation of `StockTradingManager.updateStockPrice()` and how it uses the Publisher methods
- The threshold comparison logic in `updateStockPrice()`
- The implementation of each service's `notifyObserver()` method and the exact message format
- The internal `observers` list management in `Publisher`
- How `Publisher` implements the `ObserverRegistry` interface methods
