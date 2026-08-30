Source: Scaler platform, live "Additional Problems" and "Assignment" tabs — Day 120, Backend LLD: Design Patterns: Behavioural Design Patterns (class date Mon, 10 Aug 2026)
Transcribed directly from screenshots provided by the user. Scenario/code-based reasoning questions, none marked as answered on the platform. Correct answers below determined by Claude from the question logic, cross-checked against `info/.notes/scaler-raw-notes/hackmd/32-SkR3R4QIzg.md` / `33-HJ4uR4XUMe.md` (Strategy & Observer).

## Q1. Observer Registration and Notification Order
*(Additional Problems Q4)*

**Question:**
```java
interface Observer {
    void onOrderPlaced(String orderId);
}
class Amazon {
    private List<Observer> subscribers = new ArrayList<>();
    void register(Observer o) { subscribers.add(o); }
    void orderPlaced(String orderId) {
        for (Observer o : subscribers) {
            o.onOrderPlaced(orderId);
        }
    }
}
public class Main {
    public static void main(String[] args) {
        Amazon amazon = new Amazon();
        amazon.register(o -> System.out.println("Invoice generated for " + o));
        amazon.register(o -> System.out.println("Inventory updated for " + o));
        amazon.orderPlaced("ORD123");
    }
}
```
What gets printed?

**Options:**
- A. Only "Invoice generated for ORD123"
- B. Only "Inventory updated for ORD123"
- C. Both lines print, in the order they were registered
- D. Nothing prints, this code has a compile error

**Answer: C** — `orderPlaced` iterates `subscribers` in insertion order (an `ArrayList`) and invokes each observer's callback, so both lambdas fire in registration order.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q4)*

## Q2. Strategy Factory Null Pointer Issue
*(Additional Problems Q5)*

**Question:** A developer wrote this `RouterFactory` for choosing between a cheap and an expensive AI model:
```java
class RouterFactory {
    private static final Map<QueryComplexity, RoutingStrategy> STRATEGIES = Map.of(
        QueryComplexity.SIMPLE, new SimpleQueryStrategy()
    );
    static RoutingStrategy getStrategy(QueryComplexity c) {
        return STRATEGIES.get(c);
    }
}
```
When called with `QueryComplexity.COMPLEX`, what happens?

**Options:**
- A. It automatically falls back to `SimpleQueryStrategy`
- B. It throws a `ClassNotFoundException` immediately
- C. It compiles but silently does nothing
- D. It returns `null`, which will likely cause a `NullPointerException` later when a method is called on it

**Answer: D** — `Map.get()` returns `null` for a missing key; there is no fallback logic, so `getStrategy(COMPLEX)` returns `null` and the caller crashes with an NPE the moment it invokes a method on the result.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q5)*

## Q3. Fallback Behavior Pattern Identification
*(Additional Problems Q6)*

**Question:** A payment system tries Razorpay first. If Razorpay fails, it tries Stripe next. If Stripe also fails, it tries PayPal. Which pattern best fits this situation?

**Options:**
- A. Neither Strategy nor Observer — this is closer to Chain of Responsibility
- B. Strategy, since each payment provider is a different way of paying
- C. Observer, since all providers get notified together
- D. Factory, since it creates payment objects

**Answer: A** — Strategy picks exactly *one* implementation up front; Observer notifies *all* subscribers simultaneously. Here, providers are tried sequentially, one at a time, only moving to the next on failure — that ordered, pass-along-until-handled behavior is the defining shape of Chain of Responsibility, not Strategy or Observer.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q6)*

## Q4. Strategy Statelessness and Parameters
*(Additional Problems Q7)*

**Question:** Why does each concrete strategy class (like `CarPathCalculator`) NOT take a `mode` parameter in its methods?

**Options:**
- A. Because Java doesn't allow extra parameters in overridden methods
- B. Because the class itself already represents one specific way of doing the task, so it doesn't need to be told what "mode" it is
- C. Because mode is only needed inside the Factory class
- D. Because strategies are stateless and can't accept any parameters at all

**Answer: B** — The entire point of Strategy is that the *choice* of algorithm is made once, externally, by selecting which concrete class to instantiate — a `CarPathCalculator` already *is* the "car mode" implementation, so passing a mode flag into it would be redundant and would reopen the door to internal branching the pattern exists to eliminate.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q7)*

## Q5. Strategy Selection Loop Output
*(Additional Problems Q8)*

**Question:**
```java
interface TradingIndicatorStrategy {
    boolean supportsType(String type);
    double calculate(double current, double previous);
}
class MomentumStrategy implements TradingIndicatorStrategy {
    public boolean supportsType(String type) { return type.equals("MOMENTUM"); }
    public double calculate(double current, double previous) { return current - previous; }
}
class VolatilityStrategy implements TradingIndicatorStrategy {
    public boolean supportsType(String type) { return type.equals("VOLATILITY"); }
    public double calculate(double current, double previous) { return Math.abs(current - previous); }
}
public class Main {
    public static void main(String[] args) {
        List<TradingIndicatorStrategy> strategies = List.of(new MomentumStrategy(), new VolatilityStrategy());
        for (TradingIndicatorStrategy s : strategies) {
            if (s.supportsType("VOLATILITY")) {
                System.out.println(s.calculate(50, 70));
            }
        }
    }
}
```
What is printed?

**Options:**
- A. -20.0
- B. 0.0
- C. 20.0
- D. Nothing is printed

**Answer: C** — Only `VolatilityStrategy.supportsType("VOLATILITY")` returns `true`; its `calculate(50, 70)` returns `Math.abs(50 - 70) = 20.0`. `MomentumStrategy` is skipped entirely since its `supportsType` check fails.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q8)*

## Q6. Missing Notification in Observer Publisher
*(Additional Problems Q9)*

**Question:**
```java
class WeatherMonitoringApplication {
    private List<Observer> observers = new ArrayList<>();
    void addObserver(Observer o) {
        observers.add(o);
    }
    void setTemperature(double temp) {
        this.temperature = temp;
        // missing something here
    }
}
```
The `TemperatureService` observer is registered correctly, but it never receives updates when `setTemperature` is called. What is missing?

**Options:**
- A. The `Observer` interface needs a `getTemperature` method
- B. `observers` should be a `Map` instead of a `List`
- C. `setTemperature` needs to be declared `static`
- D. A call to notify all observers (e.g., looping through `observers` and calling their `update` method) inside `setTemperature`

**Answer: D** — Registering an observer only adds it to the list; the publisher must explicitly iterate its observers and invoke their update callback whenever its state changes. Without that notification loop inside `setTemperature`, registered observers never learn about the change — this is the single most common Observer-pattern bug.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q9)*

## Q7. Bridging Incompatible Interfaces
*(Additional Problems Q10)*

**Question:** Your team's third-party analytics library only understands `trackEvent(XML data)`, but your entire codebase only works with `log(JSON data)`. Which pattern should you use to make them work together, without changing your existing app or the library?

**Options:**
- A. Adapter
- B. Strategy
- C. Observer
- D. Factory

**Answer: A** — This is the textbook Adapter scenario: two incompatible interface shapes (JSON `log()` vs XML `trackEvent()`) need to be bridged without modifying either side.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q10)*

## Q8. Reusing Strategy Objects in Factories
*(Additional Problems Q11)*

**Question:** Why is it usually fine for a Strategy Factory to reuse the same strategy object every time instead of creating a new one on each call?

**Options:**
- A. Because Java does not allow creating multiple objects of the same class
- B. Because most strategy classes have no changing internal state, so sharing one instance (like a Singleton) is safe and avoids unnecessary object creation
- C. Because reusing objects makes the code violate Open-Closed Principle
- D. Because Factory pattern requires objects to be reused

**Answer: B** — Concrete strategies are typically stateless (all the data they operate on is passed in as method parameters, not stored as instance fields), so a single shared instance behaves identically no matter how many callers use it concurrently — caching and returning one instance from the factory avoids pointless allocation.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q11)*

## Q9. Observer Subscribe and Unsubscribe Lifecycle
*(Additional Problems Q12)*

**Question:**
```java
interface Observer {
    void update(String event);
}
class Logger implements Observer {
    public void update(String event) {
        System.out.println("LOG: " + event);
    }
}
class Publisher {
    private List<Observer> observers = new ArrayList<>();
    void subscribe(Observer o) { observers.add(o); }
    void unsubscribe(Observer o) { observers.remove(o); }
    void publish(String event) {
        for (Observer o : observers) o.update(event);
    }
}
public class Main {
    public static void main(String[] args) {
        Publisher publisher = new Publisher();
        Logger logger = new Logger();
        publisher.subscribe(logger);
        publisher.publish("Order Placed");
        publisher.unsubscribe(logger);
        publisher.publish("Order Shipped");
    }
}
```
What is printed?

**Options:**
- A. Both "LOG: Order Placed" and "LOG: Order Shipped" print
- B. Only "LOG: Order Shipped" prints
- C. Only "LOG: Order Placed" prints
- D. Nothing is printed

**Answer: C** — `logger` is subscribed when the first `publish("Order Placed")` fires, so it prints. It is then unsubscribed before the second `publish("Order Shipped")` call, so the (now-empty) observer list means nothing fires for the second event.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q12)*

## Q10. Strategy vs. Observer Intent
*(Additional Problems Q3, separate list)*

**Question:** What is the key difference in intent between Strategy and Observer, even though both rely on one interface with multiple implementing classes?

**Options:**
- A. Strategy is only for payments; Observer is only for notifications
- B. Strategy picks exactly one implementation to use; Observer notifies many implementations at once
- C. Strategy requires a Factory; Observer never uses a Factory
- D. There is no real difference between them

**Answer: B** — Both patterns program to an interface, but the *purpose* differs completely: Strategy selects and delegates to a single chosen algorithm, while Observer broadcasts a state change to every registered listener simultaneously. This is the conceptual key that also explains Q3 and Q6 above.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q3)*

## Q11. Strategy Pattern vs If-Else Blocks
*(Assignment Q5)*

**Question:** What is the main problem with writing one method that uses if-else blocks to handle different "modes" (like car, bike, walk) inside the same class?

**Options:**
- A. It violates Open-Closed and Single Responsibility Principles, since adding a new mode means editing existing working code
- B. The code runs slower than using classes
- C. Java does not allow more than 3 if-else conditions
- D. It cannot be tested using JUnit

**Answer: A** — Every new mode requires reopening and modifying the same method, risking regressions in already-tested branches, and the one class now owns the logic for every mode instead of a single, focused responsibility — exactly the two principles Strategy is designed to restore.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q5)*

## Q12. PricingStrategy Composition Output
*(Assignment Q6)*

**Question:**
```java
interface PricingStrategy {
    double calculatePrice(double input);
}
class DistancePricing implements PricingStrategy {
    public double calculatePrice(double distanceKm) {
        return 5.0 + (2.0 * distanceKm);
    }
}
class PricingManager {
    private PricingStrategy strategy;
    PricingManager(PricingStrategy strategy) { this.strategy = strategy; }
    double getPrice(double input) { return strategy.calculatePrice(input); }
}
public class Main {
    public static void main(String[] args) {
        PricingManager manager = new PricingManager(new DistancePricing());
        System.out.println(manager.getPrice(10));
    }
}
```
What will be printed?

**Options:**
- A. 20.0
- B. 25.0
- C. 15.0
- D. 5.0

**Answer: B** — `manager.getPrice(10)` delegates to `DistancePricing.calculatePrice(10)`, which computes `5.0 + (2.0 * 10) = 25.0`.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q6)*

## Q13. Strategy Pattern Interface Argument Bug
*(Assignment Q7)*

**Question:** A student implemented the `QualityAdjustmentStrategy` interface for a video streaming app, but their manager class won't compile:
```java
interface QualityAdjustmentStrategy {
    VideoQuality supportsType();
    Video adjust(Video video);
}
class LowQualityStrategy implements QualityAdjustmentStrategy {
    public VideoQuality supportsType() { return VideoQuality.LOW; }
    public Video adjust(Video video) {
        video.setBitrate(500);
        return video;
    }
}
class VideoStreamingManager {
    private QualityAdjustmentStrategy strategy;
    VideoStreamingManager(QualityAdjustmentStrategy strategy) { this.strategy = strategy; }
    Video streamVideo(Video video) {
        return strategy.adjust();
    }
}
```
What is the bug?

**Options:**
- A. `LowQualityStrategy` does not implement `supportsType` correctly
- B. `VideoQuality.LOW` does not exist in Java
- C. `strategy.adjust()` is called without passing the required `video` argument
- D. The interface should not have two methods

**Answer: C** — `adjust(Video video)` requires one argument, but `streamVideo` calls `strategy.adjust()` with none — a straightforward missing-argument compile error, unrelated to the interface design itself.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q7)*

## Q14. Observer Pattern for Notifications
*(Assignment Q8)*

**Question:** You are building a notification system where the `TaskManager` class notifies `AlertService`, `EmailService`, and `SlackService` whenever a new task is assigned. A new team wants to add a `WhatsAppService` reaction without touching `TaskManager`'s existing code at all. Which pattern makes this possible?

**Options:**
- A. Strategy, because it lets you pick one way of doing something
- B. Factory, because it creates objects
- C. Adapter, because it translates one interface into another
- D. Observer, because new subscribers can register themselves without changing the publisher

**Answer: D** — `TaskManager` (the publisher) only needs to loop over a list of registered observers; adding `WhatsAppService` is just registering one more observer instance, with zero changes to `TaskManager` itself.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q8)*

## Q15. Role of Factory in Strategy Pattern
*(Assignment Q9)*

**Question:** In the Strategy pattern, what is the actual job of the Factory class (e.g., `PathCalculatorFactory`)?

**Options:**
- A. To decide and return the correct strategy object based on some input
- B. To execute the algorithm itself
- C. To notify all subscribers when an event occurs
- D. To translate one interface into another

**Answer: A** — The Factory's sole job is selection and construction — mapping some input (a mode string, an enum, a config value) to the correct concrete `Strategy` instance. It never executes the algorithm itself; that responsibility stays entirely inside the chosen strategy class.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q9)*
