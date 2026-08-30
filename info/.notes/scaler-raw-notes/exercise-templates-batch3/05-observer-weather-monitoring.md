# Observer Pattern for Weather Monitoring System

Source folder: `1773391225_03c7a8319fd5c150/Weather_Observer-solution`

## Problem Statement

You are developing a weather monitoring system that collects data from various sensors such as temperature, humidity, and pressure sensors. When any sensor reading goes beyond a predefined threshold, you need to notify different weather stations through various communication channels like emails, SMS, and push notifications. Your task is to implement the Observer pattern to create a flexible notification system for this weather monitoring system.

## Detailed Requirements

1. **Review the original class**: Study the `WeatherMonitoringApplication` class and its dependencies. Understand how it currently handles weather condition updates and notifications.

2. **Implement the publisher class**: You have been provided with a `Publisher` abstract class. Implement the required methods defined by this interface in the `WeatherMonitoringApplication` class. Remember that the `Publisher` interface defines the methods that a class can use to notify observers.

3. **Implement the observer interface**: Create an interface named `Observer` with a method that takes the weather conditions (e.g., temperature, humidity, pressure) as arguments. Observer classes (e.g., `TemperatureService`, `PressureService`, `HumidityService`) will implement this interface to receive notifications.

4. **Refactor the publisher**: Modify the `WeatherMonitoringApplication` class to adhere to the Observer pattern. **Do not change the constructor signature** as it's used by the tests.

5. **Refactor the observers**: Update the observer classes to implement the `Observer` interface. Modify their existing methods to match the new interface method signature.

6. **Test your implementation**: Run the provided test cases in the `WeatherMonitoringTests` class to verify that your observer pattern implementation works correctly. These test cases will check if observers are notified appropriately and if the `WeatherMonitoringApplication` functions as expected.

## Graded Contract (from tests)

- WeatherMonitoringApplication must **not have any fields** of type `TemperatureService`, `HumidityService`, or `PressureService` (loose coupling requirement)
- `Observer` interface must declare exactly **one method with a single `double` parameter** (sensor value)
- `Publisher` class must declare **at least two methods taking a single `Observer` parameter** (for add and remove)
- `WeatherMonitoringApplication` must have a **6-parameter constructor** accepting two `double` values for temperature/humidity/pressure initial values, and three `double` threshold values
- `WeatherMonitoringApplication` must **extend `Publisher`**
- `TemperatureService`, `HumidityService`, and `PressureService` must each **implement `Observer`**
- When `WeatherMonitoringApplication.updateWeatherConditions(double newTemperature, double newHumidity, double newPressure)` is called:
  - If any sensor reading exceeds its threshold, observers must be notified with that value
  - Each notification must call `NotificationUtils.sendNotification(String)` with message format: `"New value is <value>"` (formatted to 1 decimal place)
  - Multiple notifications for the same observer can occur if multiple thresholds are exceeded

## Learner Template

```java
// Observer.java
package com.assignment.question;

public interface Observer {
    // TODO: Implement the observer notification method
    // Should accept one double parameter for the sensor value
}
```

```java
// Publisher.java
package com.assignment.question;

import java.util.ArrayList;
import java.util.List;

public abstract class Publisher {
    private List<Observer> observers = new ArrayList<>();

    // TODO: Implement method to add an observer
    
    // TODO: Implement method to remove an observer
    
    // TODO: Implement method to notify all observers
    // Should invoke notifyObserver() on each observer with the sensor value
}
```

```java
// WeatherMonitoringApplication.java
package com.assignment.question;

public class WeatherMonitoringApplication extends Publisher {

    private double temperature;
    private double humidity;
    private double pressure;
    private double temperatureThreshold;
    private double humidityThreshold;
    private double pressureThreshold;

    // DO NOT MODIFY THIS CONSTRUCTOR
    public WeatherMonitoringApplication(double initialTemperature, double initialHumidity, double initialPressure,
                                        double temperatureThreshold, double humidityThreshold, double pressureThreshold) {
        this.temperature = initialTemperature;
        this.humidity = initialHumidity;
        this.pressure = initialPressure;
        this.temperatureThreshold = temperatureThreshold;
        this.humidityThreshold = humidityThreshold;
        this.pressureThreshold = pressureThreshold;
    }
    // DO NOT MODIFY THIS CONSTRUCTOR

    // TODO: Implement updateWeatherConditions method
    // Should update temperature, humidity, and pressure
    // For each reading that exceeds its threshold, notify observers with that value
}
```

```java
// TemperatureService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class TemperatureService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendNotification() with message "New value is <value>"
}
```

```java
// HumidityService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class HumidityService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendNotification() with message "New value is <value>"
}
```

```java
// PressureService.java
package com.assignment.question.services;

import com.assignment.question.Observer;
import com.assignment.question.utils.NotificationUtils;

public class PressureService implements Observer {
    // TODO: Implement Observer interface method
    // Should call NotificationUtils.sendNotification() with message "New value is <value>"
}
```

## Deliberately Left Out (for the learner to design)

- The exact method signature of `notifyObserver()` in the `Observer` interface
- The implementation of `addObserver()`, `removeObserver()`, and `notifyObservers()` in `Publisher`
- The implementation of `WeatherMonitoringApplication.updateWeatherConditions()` and threshold comparison logic
- The implementation of each service's `notifyObserver()` method and the message format
- The internal `observers` list management in `Publisher`
- The logic to notify observers only when thresholds are exceeded (not on every update)
