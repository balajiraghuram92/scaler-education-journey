Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/HyD5dW1LMe

# Backend LLD: Structural Design Patterns: Decorator and Flyweight

## Overview

This document covers two structural design patterns: **Decorator** and **Flyweight**, which solve distinct problems in system design.

**Decorator** addresses: "How do you add behavior to an object at runtime, layer by layer, without modifying its original class?"

**Flyweight** addresses: "How do you efficiently manage large numbers of nearly identical objects without excessive memory consumption?"

## Decorator Pattern

### Core Concept

The Decorator pattern enables wrapping objects with additional behavior while maintaining the same interface. As the material explains: "Start with a base object. Wrap it with extra behavior, one layer at a time, while the program is running (not decided ahead of time)."

### Coffee Shop Example

The pattern uses a coffee ordering system as its primary example. A customer begins with a base drink (Espresso) and adds condiments (milk, mocha, whip). Each layer modifies cost and description without altering the underlying object.

**Key Implementation Details:**

- All beverages implement a shared `Beverage` interface with `cost()` and `getDescription()` methods
- Base drinks (Espresso, DarkRoast) stand alone without wrapping anything
- Decorators (Mocha, Whip) wrap another Beverage and add their own contribution

```java
interface Beverage {
  double cost();
  String getDescription();
}

class Espresso implements Beverage {
  public double cost() { return 80.0; }
  public String getDescription() { return "Espresso"; }
}

abstract class CondimentDecorator implements Beverage {
  protected Beverage wrappedBeverage;
  CondimentDecorator(Beverage wrappedBeverage) {
    this.wrappedBeverage = wrappedBeverage;
  }
}

class Mocha extends CondimentDecorator {
  public double cost() { return wrappedBeverage.cost() + 20.0; }
  public String getDescription() { 
    return wrappedBeverage.getDescription() + " + Mocha"; 
  }
}
```

### Building an Order

```java
Beverage order = new Espresso();
order = new Mocha(order);
order = new Whip(order);
System.out.println(order.cost()); // 115.0
```

Each new line wraps the previous result, creating nested layers.

### Real-World Applications

**Java I/O:** BufferedReader decorates FileReader, adding buffering and line-reading capabilities without modifying FileReader itself.

**Collections:** `Collections.synchronizedList()` wraps a List to add thread-safety; `Collections.unmodifiableList()` adds immutability.

**Backend Services:** NotificationService can be decorated with logging, retry logic, and rate-limiting concerns as separate layers.

### Backend Notification Example

```java
interface NotificationService {
  void send(String userId, String message);
}

class SmsNotificationService implements NotificationService {
  public void send(String userId, String message) {
    System.out.println("Sending SMS to " + userId);
  }
}

abstract class NotificationDecorator implements NotificationService {
  protected NotificationService wrapped;
  NotificationDecorator(NotificationService wrapped) {
    this.wrapped = wrapped;
  }
}

class LoggingNotificationDecorator extends NotificationDecorator {
  public void send(String userId, String message) {
    System.out.println("[LOG] Sending to " + userId);
    wrapped.send(userId, message);
    System.out.println("[LOG] Send completed");
  }
}

class RetryNotificationDecorator extends NotificationDecorator {
  private final int maxAttempts;
  
  public void send(String userId, String message) {
    int attempts = 0;
    while (attempts < maxAttempts) {
      try {
        wrapped.send(userId, message);
        return;
      } catch (Exception e) {
        attempts++;
        if (attempts == maxAttempts) throw e;
      }
    }
  }
}

class RateLimitedNotificationDecorator extends NotificationDecorator {
  private final Map<String, Integer> countThisMinute;
  private final int maxPerMinute;
  
  public void send(String userId, String message) {
    int count = countThisMinute.getOrDefault(userId, 0);
    if (count >= maxPerMinute) {
      System.out.println("[RATE LIMIT] Blocked");
      return;
    }
    countThisMinute.put(userId, count + 1);
    wrapped.send(userId, message);
  }
}
```

Wiring them together:

```java
NotificationService service = new SmsNotificationService();
service = new RetryNotificationDecorator(service, 3);
service = new RateLimitedNotificationDecorator(service, 5);
service = new LoggingNotificationDecorator(service);
service.send("user_123", "Your order has shipped!");
```

### Key Pitfalls

- Assuming Decorator is simply inheritance with extra steps (inheritance is compile-time; Decorator is runtime)
- Modeling add-ons as a fixed List (fails with repeated add-ons or price interactions)
- Giving separate interfaces to base drinks and condiments
- Skipping the abstract base decorator class
- Forgetting decorators must call the wrapped object's method first
- Letting a base class accumulate boolean flags

### AI Corner Lesson

When asked to add a "combo discount," the AI initially added boolean flags directly to Espresso, reverting to the rejected design. The corrected approach creates a new `ComboDiscount` decorator that inspects the wrapped object's description:

```java
class ComboDiscount extends CondimentDecorator {
  public double cost() {
    double baseCost = wrappedBeverage.cost();
    String desc = wrappedBeverage.getDescription();
    boolean qualifies = desc.contains("Mocha") && desc.contains("Whip");
    return qualifies ? baseCost * 0.9 : baseCost;
  }
}
```

---

## Flyweight Pattern

### Core Concept

Flyweight addresses memory efficiency when managing huge numbers of similar objects. The pattern splits object data into two categories:

- **Intrinsic data:** Identical across many instances, stored once and shared
- **Extrinsic data:** Unique per instance, stored separately

### The PUBG Problem

In a game with 100,000 bullets fired, storing complete bullet information for each would consume ~110 MB. However, most data repeats:

- **Intrinsic (shared):** color, radius, weight, maxDamage, maxRange, image
- **Extrinsic (unique):** currentCoordinate, targetCoordinate, direction, speed

```java
class BulletType {
  private final String color;
  private final double radius;
  private final double weight;
  private final int maxDamage;
  private final int maxRange;
  private final byte[] image;
  
  BulletType(String color, double radius, double weight, 
             int maxDamage, int maxRange, byte[] image) {
    this.color = color;
    this.radius = radius;
    this.weight = weight;
    this.maxDamage = maxDamage;
    this.maxRange = maxRange;
    this.image = image;
  }
}

class BulletTypeFactory {
  private static final Map<String, BulletType> cache = new HashMap<>();
  
  static BulletType getBulletType(String gunName) {
    if (!cache.containsKey(gunName)) {
      cache.put(gunName, loadBulletTypeFromConfig(gunName));
    }
    return cache.get(gunName);
  }
  
  private static BulletType loadBulletTypeFromConfig(String gunName) {
    return new BulletType("black", 0.03, 0.008, 40, 400, new byte[1024]);
  }
}

class Bullet {
  private final BulletType type;
  private double[] currentCoordinate;
  private double[] targetCoordinate;
  private double[] direction;
  private double speed;
  
  Bullet(String gunName, double[] currentCoordinate, 
         double[] direction, double speed) {
    this.type = BulletTypeFactory.getBulletType(gunName);
    this.currentCoordinate = currentCoordinate;
    this.direction = direction;
    this.speed = speed;
  }
}
```

With 5 gun types, only 5 BulletType objects exist regardless of bullet count.

### Real-World Applications

**Java Caching:** `Integer.valueOf()` caches values from -128 to 127, reusing the same object for repeated values.

**Food Delivery Backend:** Category objects (Beverages, Desserts) are shared across millions of order line items:

```java
class Category {
  private final String name;
  private final String iconUrl;
  private final double taxRate;
  
  Category(String name, String iconUrl, double taxRate) {
    this.name = name;
    this.iconUrl = iconUrl;
    this.taxRate = taxRate;
  }
}

class CategoryFactory {
  private static final Map<String, Category> cache = new HashMap<>();
  
  static Category get(String name) {
    return cache.computeIfAbsent(name, CategoryFactory::loadFromDb);
  }
  
  private static Category loadFromDb(String name) {
    return new Category(name, "/icons/" + name + ".png", 0.05);
  }
}

class OrderLineItem {
  private final Category category;
  private final String itemName;
  private final double price;
  
  OrderLineItem(String categoryName, String itemName, double price) {
    this.category = CategoryFactory.get(categoryName);
    this.itemName = itemName;
    this.price = price;
  }
}
```

### Key Pitfalls

- Assuming memory savings only matter at extreme scale
- Splitting fields based on importance rather than whether they're identical across instances
- Constructing shared objects directly instead of routing through factory
- Making intrinsic fields mutable instead of final
- Assuming Integer caching applies to all values (only -128 to 127)
- Loading reference data from database on every request

---

## Terminology

| Term | Definition |
|------|-----------|
| **Decorator pattern** | Runtime behavior addition via wrapping without modifying original class |
| **Wrapping** | Passing one object into another's constructor to forward calls with added behavior |
| **Concrete component** | Innermost object in decorator chain; doesn't wrap anything |
| **Cross-cutting concern** | Functionality (logging, retries, caching, rate limiting) applying across system |
| **Flyweight pattern** | Efficiently handling large object counts by sharing identical data |
| **Intrinsic data** | Identical across instances; stored once and shared |
| **Extrinsic data** | Unique per instance; stored separately |
| **Flyweight factory** | Creates and caches shared objects once |

---

## Interview Questions

**Q: What problem does Decorator solve that inheritance cannot?**
Inheritance fixes behavior at compile-time; Decorator enables runtime composition of behaviors without creating subclasses for every combination.

**Q: Why reject a Beverage class holding List<Condiment>?**
Fixed lists fail when add-ons repeat or affect each other's pricing. Treating all layers as the same Beverage type handles these cases naturally.

**Q: Why must decorators implement the wrapped object's interface?**
This allows decorators to be used interchangeably and stacked freely.

**Q: Trace cost() on Whip(Mocha(Espresso()))**
Whip calls Mocha's cost(), which calls Espresso's cost() (80.0), returning 100.0. Whip adds 15.0 for 115.0 total.

**Q: What are BufferedReader and Collections.synchronizedList()?**
Both are real Decorators: BufferedReader adds buffering to FileReader; synchronizedList() adds thread-safety.

**Q: What does Flyweight split each object into?**
Intrinsic data (shared, heavy) and extrinsic data (unique, light).

**Q: Why is color intrinsic but currentCoordinate extrinsic in bullets?**
Color depends only on gun type (shareable); currentCoordinate is unique per bullet instance.

**Q: What role does a factory play in Flyweight?**
Guarantees one shared instance per category, checking cache before constructing.

**Q: Why does Integer a = 100; Integer b = 100; yield a == b as true?**
Java's `Integer.valueOf()` caches values -128 to 127, so both reference the same cached object.

**Q: What are cross-cutting concerns and why suit Decorator?**
Concerns like logging and retries apply broadly across systems. Decorator lets each concern exist as an independent layer without touching core logic.

**Q: What was wrong with the AI's combo discount implementation?**
It added boolean flags to Espresso, reintroducing the rejected flags-based design. The correct approach creates a ComboDiscount decorator.

**Q: What general lesson emerges from AI prompting?**
Vague prompts produce fastest fixes that often break patterns; specific prompts naming what to preserve yield extensible designs.

---

## Self-Check Questions

1. Explain why treating beverages and add-ons as the same type solves repeated add-ons and size scaling
2. Write a Soy decorator following Mocha's shape
3. Trace getDescription() for Whip(Mocha(Espresso())) showing recursive calls
4. Explain why BufferedReader is Decorator, not a FileReader subclass
5. What changes if RateLimitedNotificationDecorator wires outside RetryNotificationDecorator?
6. For ride-sharing: identify intrinsic vs extrinsic fields (car model vs pickup location)
7. Explain why BulletTypeFactory uses cache instead of direct construction
8. Compare CategoryFactory.computeIfAbsent() to BulletTypeFactory's manual pattern
9. Explain why Integer a = 200; Integer b = 200; prints false, linking to Flyweight
10. Show how ComboDiscount determines discounts without new Espresso fields
11. Evaluate proposal to add discountPercentage to Beverage interface
12. Compare Decorator and Adapter: what each achieves by wrapping

---

## Further Reading

- "Design Patterns" by Gang of Four: original pattern sources
- Java documentation on BufferedReader and FileReader
- Java documentation on Collections synchronizedList/unmodifiableList
- Java documentation on Integer.valueOf() and caching behavior
- Resilience4j documentation: production-grade retry/circuit-breaker wrappers
- Post-Read 5 (Adapter and Facade): Open/Closed and Single Responsibility Principles

---

## Homework

1. Add Soy decorator to coffee shop; build order with all four layers
2. Create CachingNotificationDecorator skipping duplicate messages within one minute
3. Extend BulletTypeFactory to log only on first gun creation
4. Find one real Decorator and one Flyweight in a used codebase
5. Push code to GitHub branch: decorator-flyweight-lecture-complete
