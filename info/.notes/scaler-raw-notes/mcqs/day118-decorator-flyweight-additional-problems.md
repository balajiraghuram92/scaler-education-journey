Source: Scaler platform, live "Additional Problems" tab — Day 118, Backend LLD: Design Patterns: Decorator and Flyweight (class date Fri, 7 Aug 2026)
Transcribed directly from screenshots provided by the user. These are scenario/code-based reasoning questions, not simple recall — richer than the earlier screenshot batch. None were marked as answered on the platform; all correct answers below were determined by Claude from the question logic and cross-checked against `info/.notes/scaler-raw-notes/pdfs-transcribed/2.3__Decorator_and_Flyweight.md` and `info/.notes/scaler-raw-notes/hackmd/30-SJF9_Wy8Ml.md` / `31-HyD5dW1LMe.md`.

## Q3. Decorator Design

**Question:** What is the main idea behind the Decorator pattern?

**Options:**
- A. Copying an existing object to create a new one
- B. Adding new behavior to an object by wrapping it, without changing its original class
- C. Storing shared data in one place and reusing it across many objects
- D. Notifying multiple objects whenever one object changes

**Answer: B** — Decorator attaches new responsibilities to an object dynamically by wrapping it in another object implementing the same interface, leaving the original class untouched. (A describes Prototype, C describes Flyweight, D describes Observer.)
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q3)*

## Q4. Coffee Orders

**Question:**
```java
Beverage order = new Espresso();        // cost = 80.0
order = new Mocha(order);               // adds 20.0
order = new Whip(order);                // adds 15.0
System.out.println(order.cost());
```
What gets printed?

**Options:**
- A. 80.0
- B. 100.0
- C. 115.0
- D. Compile error

**Answer: C** — Each decorator's `cost()` calls the wrapped object's `cost()` and adds its own charge: 80.0 (Espresso) + 20.0 (Mocha) + 15.0 (Whip) = 115.0. This is the core Decorator mechanic: each layer delegates to the one it wraps before adding its own contribution.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q4)*

## Q5. Beverage Customization

**Question:** A student writes this Decorator code but it doesn't compile:
```java
class Mocha extends CondimentDecorator {
    public double cost() {
        return wrappedBeverage.cost() + 20.0;
    }
}
```
No constructor was written for `Mocha`. What's the most likely problem?

**Options:**
- A. `CondimentDecorator` requires a constructor that passes the wrapped `Beverage`, and `Mocha` never provides one
- B. `cost()` should not call `wrappedBeverage.cost()`
- C. `Mocha` should implement `Beverage` directly, not extend `CondimentDecorator`
- D. There is no problem, this code is correct

**Answer: A** — `CondimentDecorator` needs to receive the wrapped `Beverage` instance somehow (typically via its own constructor storing it into `wrappedBeverage`). Without `Mocha` writing a constructor that calls `super(beverage)` (or equivalent), the compiler cannot default-construct a class whose superclass has no no-arg constructor available, or `wrappedBeverage` is simply never initialized. `cost()` calling `wrappedBeverage.cost()` (B) is correct Decorator behavior, not a bug; C would break the pattern's polymorphism; D is wrong since it's stated the code doesn't compile.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q5)*

## Q6. Double Mocha

**Question:** You're building a coffee shop app. The business now wants a "double mocha" option — mocha added twice for extra flavor and cost. Which design lets you support this most naturally?

**Options:**
- A. Add a `mochaCount` field to `Espresso`
- B. Add an `if (isDouble)` check inside `Mocha.cost()`
- C. Create a new class called `DoubleMocha` that copies all of `Espresso`'s fields
- D. Wrap the order in `Mocha` twice: `new Mocha(new Mocha(order))`

**Answer: D** — This is the entire point of Decorator: decorators can be stacked arbitrarily. Wrapping a beverage in `Mocha` twice naturally doubles the mocha charge and behavior with zero new code. A, B, and C all reintroduce the tight coupling and combinatorial-explosion problem the pattern exists to avoid.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q6)*

## Q7. Intrinsic State

**Question:** In the Flyweight pattern, what does "intrinsic state" mean?

**Options:**
- A. Data that changes every time, unique to one specific object
- B. Data used only for logging and debugging
- C. Data that is shared and identical across many objects
- D. Data that is never stored in memory

**Answer: C** — Intrinsic state is the part of an object's data that is identical across many instances and can therefore be shared from a single cached flyweight object, which is exactly what makes the memory savings possible. (A describes extrinsic state — the context passed in per call, not stored in the shared object.)
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q7)*

## Q8. Bullet Caching

**Question:**
```java
BulletType t1 = BulletTypeFactory.getBulletType("AKM");
BulletType t2 = BulletTypeFactory.getBulletType("AKM");
System.out.println(t1 == t2);
```
Assuming `BulletTypeFactory` caches `BulletType` objects in a `HashMap`, what does this print?

**Options:**
- A. true
- B. false
- C. Compile error
- D. It depends on the bullet's position

**Answer: A** — This is the Flyweight factory pattern: the factory looks up `"AKM"` in its cache and returns the *same* cached instance both times, so `t1` and `t2` reference the identical object and `==` (reference equality) is `true`. Position is extrinsic state passed separately at render/use time, not stored on the shared `BulletType`, so it has no bearing on this comparison.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q8)*

## Q9. State Separation

**Question:** A student is asked to split a `Character` class (used to render millions of characters in a text editor) into intrinsic and extrinsic parts. They write this:
```java
class CharacterIntrinsic {
    int row;
    int column;
}

class CharacterExtrinsic {
    String font;
    int size;
    String color;
}
```
What did they get backwards?

**Options:**
- A. Nothing — this split is correct
- B. `row` and `column` should be intrinsic; `font`, `size`, `color` should be extrinsic
- C. `row` and `column` should be extrinsic; `font`, `size`, `color` should be intrinsic
- D. All fields should be in the same class

**Answer: C** — They have it exactly backwards. In a document with millions of characters, the font, size, and color are typically *shared* across large runs of text (the same formatting reused over and over) — that's the definition of intrinsic state, cacheable in a shared flyweight. Each character's row/column position is unique to that one occurrence in the document — that's extrinsic state, passed in from the client at render time, never stored in the shared object. The student put the shared data in the "Extrinsic" class and the per-instance data in the "Intrinsic" class — the exact inversion of the pattern.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q9)*

## Q10. Category Sharing

**Question:** A team is building a food delivery app. Every order line item needs a `Category` (like "Beverages" or "Desserts") with a name, icon, and tax rate. There are only 30 categories, but millions of order line items per day. What's the best approach?

**Options:**
- A. Create a new `Category` object for every line item, since each order is different
- B. Store one shared `Category` object per category name in a factory/cache, and have every line item just reference it
- C. Store all category data directly inside the `OrderLineItem` class as separate fields
- D. Avoid using categories altogether to save memory

**Answer: B** — Classic Flyweight factory: with only 30 distinct categories shared across millions of line items, cache one `Category` object per name and have every line item hold a reference to the shared instance rather than duplicating the (name, icon, tax rate) data millions of times. A wastes massive memory on identical duplicate objects; C denormalizes and duplicates the same data inline; D throws away needed information.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q10)*

## Q11. Pattern Comparison

**Question:** What is the key difference between Decorator and Flyweight?

**Options:**
- A. Flyweight adds new behavior; Decorator saves memory
- B. They are the same pattern with different names
- C. Decorator is only used in games; Flyweight is only used in coffee shop examples
- D. Decorator adds new behavior by wrapping objects; Flyweight saves memory by sharing common data across many objects

**Answer: D** — Decorator's purpose is behavioral extension via composition/wrapping; Flyweight's purpose is memory optimization via sharing intrinsic state across instances. A has the two patterns' purposes swapped; C is a nonsensical restriction (both patterns generalize far beyond any one example domain); B ignores that they solve entirely different problems.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q11)*

## Q12. Wrong Design

**Question:** An AI assistant was asked to add a "combo discount" to the coffee shop example. It gave back this code:
```java
class Espresso implements Beverage {
    boolean hasMocha = false;
    boolean hasWhip = false;

    public double cost() {
        double cost = 80.0;
        if (hasMocha) cost += 20.0;
        if (hasWhip) cost += 15.0;
        if (hasMocha && hasWhip) cost *= 0.9;
        return cost;
    }
}
```
What's wrong with this from a Decorator design point of view?

**Options:**
- A. The discount math is calculated incorrectly
- B. It puts add-on flags and combo logic back inside the base class, which is exactly the design the pattern was meant to avoid
- C. Nothing is wrong, this is a valid Decorator
- D. `Espresso` should not implement `Beverage`

**Answer: B** — This reintroduces the exact problem Decorator solves: every new add-on or combo rule now requires modifying `Espresso` itself (a boolean flag plus an `if` branch per add-on), which is the tightly-coupled, unscalable design the pattern replaces with independently composable wrapper classes. The discount math (A) is a separate, secondary concern; `Espresso implements Beverage` (D) is correct and expected in this pattern.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q12)*
