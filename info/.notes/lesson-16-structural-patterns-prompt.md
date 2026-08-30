# Prompt for Local LLM — Add Lesson 16: Structural Patterns (Adapter, Facade, Decorator, Flyweight)

Paste everything below this line into the local LLM as-is. All lesson content, MCQs, and
structure below were already authored by hand from the real Scaler source material — you
are NOT being asked to write new prose or invent examples. Copy everything verbatim into
the correct place in the C# code. If any step below doesn't match what you find in the
actual file, STOP and report the discrepancy instead of guessing.

---

## 0. Prerequisite check — READ THIS FIRST

The lesson slug this prompt adds (`16-structural-patterns`) only makes sense inside a
6-module course structure with a "Design Principles" module. Check
`api/Data/JavaVerticalSeedData.cs` right now:

- If you find a method called `SeedModule5Lessons` (or similar) and 6 `CourseModule`
  entries (Badges "Module 1" through "Module 6"), the restructure has already been applied
  — skip to Section 1 below.
- If you only find 4 modules and lessons `14-spring-boot-core` through
  `17-machine-coding-capstone`, the restructure has **not** been applied yet. In that case,
  first apply `info/.notes/module-restructure-prompt.md` in full (it is a separate,
  complete, self-contained prompt in this repo — read and execute it exactly as written),
  and only then come back and apply this prompt on top of the result.

Do not proceed with Section 1 until the 6-module structure with slug
`"16-structural-patterns"` (OrderIndex 3 inside "Module 4: Design Principles") exists as an
empty/outline lesson.

---

## 1. What to do

Find the lesson with slug `"16-structural-patterns"` inside `api/Data/JavaVerticalSeedData.cs`
(created by the module restructure). Its `ContentBody` is currently a placeholder
(`## Key Topics` bullet list or similar). Follow the exact same mechanism already used for
lessons 4–13: add a case for `"16-structural-patterns"` inside the
`GetAuthoredLessonContent(string slug)` switch, returning the full lesson content given in
Section 2 below, and make sure `BackfillLessonContent`/`NeedsLessonContent` will pick it up
(it already will, since that logic is generic — you do not need to change those methods).

Do not touch any other lesson's content.

## 2. Lesson content — copy this exactly into the new switch case

```
"16-structural-patterns" => @"# Lesson 16 — Structural Patterns: Adapter, Facade, Decorator & Flyweight

## Concepts Covered

Structural patterns govern how objects are organized and connected *after* they already exist — a different concern from creational patterns (which govern *how* objects come into being).

**Adapter — Translating Without Touching Either Side:**
An adapter is a middle layer connecting two things that don't fit together, without changing either side. The classic production scenario: PhonePe needs to integrate Yes Bank, HDFC, and other banks, each with its own incompatible API shape, without rewriting PhonePe's core code for every new bank and without editing the banks' own SDK code (which would be overwritten on the next upstream update anyway). An adapter has three components: a **Target Interface** (the client's expected contract, e.g. PhonePe's internal `BankAPI`), an **Adaptee** (the existing incompatible class — the actual bank SDK), and the **Adapter** itself, which implements the target interface while internally wrapping and translating calls to the adaptee. Translation can take several forms: type conversion (an int status code becomes a boolean), data reshaping (an object's fields become primitive arguments), pass-through (when shapes already align), and method renaming (identical behavior under a different name). The everyday physical analogy is a MacBook USB-C-to-HDMI dongle: it changes neither the laptop's port nor the monitor's cable, it just translates between the two shapes.

**Facade — One Simple Entry Point Over Complexity:**
A facade provides one simple entry point that hides the coordination of several complex subsystems behind it. The production scenario: instead of `Amazon.orderPlace()` directly calling invoice, warehouse, inventory, and email services itself (violating single responsibility), a dedicated `OrderPlacedFacade` coordinates all of that complexity behind one method call. A correctly designed facade receives its subsystem dependencies through its constructor (dependency injection) rather than constructing them internally with `new` — this keeps the facade swappable and testable with mocks, and prevents it from being locked to one concrete implementation.

**Distinguishing Adapter from Facade:** the test is *why* the wrapper exists. If the problem is two incompatible interfaces that need translating, it's an Adapter (typically one adaptee). If the problem is a complex, hard-to-use system that needs a simpler front door, it's a Facade (typically multiple subsystems). Real systems often combine both — an adapter can live inside a facade.

**Decorator — Adding Behavior by Wrapping, Not Editing:**
Decorator attaches new responsibilities to an object dynamically by wrapping it in another object that implements the same interface, leaving the original class completely untouched. The canonical worked example is a coffee shop: `Espresso implements Beverage` costs 80.0. Wrapping it as `new Mocha(order)` adds 20.0 by delegating to the wrapped beverage's `cost()` and adding its own charge on top; wrapping again as `new Whip(order)` adds another 15.0 the same way — three layers deep, `order.cost()` returns 115.0. Because decorators are just objects implementing the same interface as what they wrap, they compose: wrapping in `Mocha` *twice* (`new Mocha(new Mocha(order))`) naturally produces a "double mocha" with zero new code, which is the entire point of the pattern. The failure mode to recognize: if someone adds boolean flags like `hasMocha`/`hasWhip` and `if` branches directly inside `Espresso` to fake this behavior, they have reintroduced the exact tight coupling Decorator exists to eliminate — every new add-on then requires editing the base class again, and each new combination needs its own branch. A concrete bug to know: a `CondimentDecorator` subclass must have a constructor that receives and stores the wrapped `Beverage` (often via `super(beverage)`); forgetting this constructor is a common reason this pattern fails to compile.

**Flyweight — Sharing State to Cut Memory:**
Flyweight splits an object's data into **intrinsic state** (identical across many instances, safe to share from one cached object) and **extrinsic state** (unique per instance, passed in from the caller at the moment of use, never stored in the shared object). The canonical example: a game needs millions of bullets on screen, but they only come in a handful of *types* (e.g. "AKM") — the bullet's damage, model, and sound are intrinsic (identical for every AKM bullet fired) and belong in one cached `BulletType` object per type name, while each bullet's current position is extrinsic and passed in separately per bullet instance. A `BulletTypeFactory` backed by a `HashMap` returns the *same* cached object for the same type name (`getBulletType(""AKM"") == getBulletType(""AKM"")` is `true`), which is what makes the memory saving real. The most common mistake when applying this pattern is inverting the split — for example, in a text-editor `Character` class rendering millions of characters, the *font/size/color* are usually shared across large runs of text (intrinsic, cacheable) while each character's *row/column position* is unique per occurrence (extrinsic, passed in); a design that puts position into the shared/cached class and formatting into the per-instance class has the split exactly backwards. The same reasoning scales to any domain with a small fixed set of categories shared across a huge number of records — a food delivery app with only 30 order categories but millions of daily line items should cache one `Category` object per name and have every line item reference it, not duplicate the category data into every line item.

## Practical Backend Scenario

A payments platform (like PhonePe) needs to onboard a new bank partner every few months, each with its own SDK shape — this is solved with an `Adapter` per bank implementing a shared internal `BankAPI` interface, so onboarding a bank never requires editing the core payment-routing code. That same platform's order-completion flow touches five subsystems (payment confirmation, invoice generation, warehouse dispatch, inventory decrement, and email notification) — a `Facade` coordinates all five behind one `completeOrder()` call, with every subsystem dependency injected through the constructor so the flow can be tested with mocks. The platform's promotions team wants to stack optional order-level perks (free delivery, gift wrap, priority handling) without rewriting the base `Order` class for every combination — `Decorator` lets each perk be its own wrapper class, composable in any combination the promotions team invents later. Finally, the platform's catalog has only ~200 distinct product categories but tens of millions of line items across all orders — a `Flyweight`-backed `CategoryFactory` caches one `Category` object per category name so line items reference shared instances instead of duplicating category data millions of times over.

## Practice Loop

1. Implement a `BankAPI` target interface and two adapters (e.g. `YesBankAdapter`, `HDFCBankAdapter`) wrapping two differently-shaped fake bank SDKs, demonstrating at least one type-conversion translation and one method-renaming translation.
2. Implement an `OrderPlacedFacade` with four injected subsystem dependencies (constructor injection, no internal `new`), and write a test that substitutes a mock for one subsystem to prove testability.
3. Implement the coffee shop `Beverage`/`CondimentDecorator` hierarchy from scratch: `Espresso`, `Mocha`, `Whip`, verify triple-wrapping produces the correct additive cost, and verify double-wrapping the same decorator works without new code.
4. Implement a `BulletTypeFactory` backed by a `HashMap<String, BulletType>`; verify with `==` that two lookups of the same type name return the identical cached object, and that a new type name creates and caches a new object.
5. Take the `CharacterIntrinsic`/`CharacterExtrinsic` split example from this lesson's self-check, deliberately implement it backwards first (position cached, formatting passed in), observe why it fails to deliver any memory saving, then correct the split.

## Evidence of Understanding

You can state the three components of an Adapter and explain why editing third-party SDK code directly is unsafe. You can explain why a Facade's dependencies must be injected rather than constructed internally. You can trace a three-layer Decorator chain's `cost()` calculation by hand and explain why stacking the same decorator twice works without new code. You can classify any given field in a domain object as intrinsic or extrinsic state and justify a Flyweight factory design from an object count versus distinct-type count argument.

## Suggested Extension

Combine two of these patterns in one worked example: build a `PaymentGatewayFacade` that internally selects between `RazorpayAdapter` and `StripeAdapter` (Adapter used inside a Facade), and separately extend the coffee shop model with a `Decorator`-based loyalty-discount chain that a `Flyweight`-backed `DiscountRuleFactory` supplies shared, cached discount-rule objects to.

## Self-Check (From Class Material)

**Q1.** What is the main idea behind the Decorator pattern?
- A. Copying an existing object to create a new one
- B. Adding new behavior to an object by wrapping it, without changing its original class
- C. Storing shared data in one place and reusing it across many objects
- D. Notifying multiple objects whenever one object changes

**Answer: B** — Decorator attaches new responsibilities to an object dynamically by wrapping it in another object implementing the same interface, leaving the original class untouched. (A describes Prototype, C describes Flyweight, D describes Observer.)
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q3)*

**Q2.** Consider this code:
```java
Beverage order = new Espresso();        // cost = 80.0
order = new Mocha(order);               // adds 20.0
order = new Whip(order);                // adds 15.0
System.out.println(order.cost());
```
What gets printed?
- A. 80.0
- B. 100.0
- C. 115.0
- D. Compile error

**Answer: C** — Each decorator's `cost()` calls the wrapped object's `cost()` and adds its own charge: 80.0 + 20.0 + 15.0 = 115.0.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q4)*

**Q3.** A student writes this Decorator code but it doesn't compile:
```java
class Mocha extends CondimentDecorator {
    public double cost() {
        return wrappedBeverage.cost() + 20.0;
    }
}
```
No constructor was written for `Mocha`. What's the most likely problem?
- A. `CondimentDecorator` requires a constructor that passes the wrapped `Beverage`, and `Mocha` never provides one
- B. `cost()` should not call `wrappedBeverage.cost()`
- C. `Mocha` should implement `Beverage` directly, not extend `CondimentDecorator`
- D. There is no problem, this code is correct

**Answer: A** — `CondimentDecorator` needs to receive the wrapped `Beverage` instance via a constructor. Without `Mocha` writing one (typically calling `super(beverage)`), `wrappedBeverage` is never properly initialized.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q5)*

**Q4.** You're building a coffee shop app. The business now wants a ""double mocha"" option — mocha added twice for extra flavor and cost. Which design lets you support this most naturally?
- A. Add a `mochaCount` field to `Espresso`
- B. Add an `if (isDouble)` check inside `Mocha.cost()`
- C. Create a new class called `DoubleMocha` that copies all of `Espresso`'s fields
- D. Wrap the order in `Mocha` twice: `new Mocha(new Mocha(order))`

**Answer: D** — Decorators can be stacked arbitrarily. Wrapping a beverage in `Mocha` twice naturally doubles the mocha charge and behavior with zero new code.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q6)*

**Q5.** In the Flyweight pattern, what does ""intrinsic state"" mean?
- A. Data that changes every time, unique to one specific object
- B. Data used only for logging and debugging
- C. Data that is shared and identical across many objects
- D. Data that is never stored in memory

**Answer: C** — Intrinsic state is identical across many instances and can be shared from a single cached flyweight object, which is what makes the memory savings possible.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q7)*

**Q6.** 
```java
BulletType t1 = BulletTypeFactory.getBulletType(""AKM"");
BulletType t2 = BulletTypeFactory.getBulletType(""AKM"");
System.out.println(t1 == t2);
```
Assuming `BulletTypeFactory` caches `BulletType` objects in a `HashMap`, what does this print?
- A. true
- B. false
- C. Compile error
- D. It depends on the bullet's position

**Answer: A** — The factory returns the same cached instance both times for the same key, so `t1` and `t2` reference the identical object and `==` is `true`. Position is extrinsic and irrelevant here.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q8)*

**Q7.** A student splits a `Character` class (used to render millions of characters in a text editor) like this:
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
- A. Nothing — this split is correct
- B. `row` and `column` should be intrinsic; `font`, `size`, `color` should be extrinsic
- C. `row` and `column` should be extrinsic; `font`, `size`, `color` should be intrinsic
- D. All fields should be in the same class

**Answer: C** — Font/size/color are typically shared across large runs of text (intrinsic, cacheable); each character's position is unique per occurrence (extrinsic, passed in at render time). The student inverted the split.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q9)*

**Q8.** A team is building a food delivery app. Every order line item needs a `Category` (like ""Beverages"" or ""Desserts"") with a name, icon, and tax rate. There are only 30 categories, but millions of order line items per day. What's the best approach?
- A. Create a new `Category` object for every line item, since each order is different
- B. Store one shared `Category` object per category name in a factory/cache, and have every line item just reference it
- C. Store all category data directly inside the `OrderLineItem` class as separate fields
- D. Avoid using categories altogether to save memory

**Answer: B** — Classic Flyweight factory: cache one `Category` object per name and have every line item hold a reference to the shared instance.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q10)*

**Q9.** What is the key difference between Decorator and Flyweight?
- A. Flyweight adds new behavior; Decorator saves memory
- B. They are the same pattern with different names
- C. Decorator is only used in games; Flyweight is only used in coffee shop examples
- D. Decorator adds new behavior by wrapping objects; Flyweight saves memory by sharing common data across many objects

**Answer: D** — Decorator's purpose is behavioral extension via wrapping; Flyweight's purpose is memory optimization via sharing intrinsic state.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q11)*

**Q10.** An AI assistant was asked to add a ""combo discount"" to the coffee shop example. It gave back this code:
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
- A. The discount math is calculated incorrectly
- B. It puts add-on flags and combo logic back inside the base class, which is exactly the design the pattern was meant to avoid
- C. Nothing is wrong, this is a valid Decorator
- D. `Espresso` should not implement `Beverage`

**Answer: B** — This reintroduces the exact tight coupling Decorator solves: every new add-on now requires editing `Espresso` itself.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 118, Q12)*

**Q11.** What is the key differentiator between Adapter and Facade?
- A. Adapter always uses more memory than Facade
- B. Adapter solves incompatible interfaces (typically one adaptee); Facade solves complex, hard-to-use systems (typically multiple subsystems)
- C. Facade is only for legacy code; Adapter is only for new code
- D. They are interchangeable and the choice is purely stylistic

**Answer: B** — The test is *why* the wrapper exists: translating between two shapes that don't fit (Adapter) versus hiding coordination across several complex subsystems behind one simple entry point (Facade).
*(SOURCE_TYPE: FROM_MATERIAL — hackmd/29-rytL_zqBMe.md, ""Distinguishing Adapter from Facade"")*

**Q12.** Why should a Facade receive its subsystem dependencies through its constructor instead of creating them internally with `new`?
- A. It has no real benefit, it's just a style preference
- B. It locks the facade to one concrete implementation, which is the goal
- C. It keeps the facade testable with mocks and swappable to different implementations without modifying the facade itself
- D. Constructors in Java cannot call `new` at all

**Answer: C** — Constructing dependencies internally hardcodes the facade to specific implementations, making it untestable without real subsystems and unable to swap implementations later. Injecting them keeps the facade decoupled.
*(SOURCE_TYPE: FROM_MATERIAL — hackmd/29-rytL_zqBMe.md, ""Dependency Injection"")*
",
```

## 3. What must NOT change

- Do not touch any lesson other than `16-structural-patterns`.
- Do not modify `NeedsLessonContent`, `BackfillLessonContent`, or any other method.
- Keep C# verbatim-string escaping consistent: every literal `"` inside the content above is
  already written as `""` — copy it exactly, do not "fix" it to single quotes.
- Do not add a 7th section or reorder the six sections.

## 4. Attach the exercise packages (informational — you don't need to create these files)

15 new Java exercise packages covering these same four patterns have already been analyzed
and written to `info/.notes/scaler-raw-notes/exercise-templates-batch2/` (contract-only
templates plus full problem-statement writeups, ready to become `exercises/java/java-lld/`
packages the same way `exercises/java/java-lld/oop-3/point-threedpoint/` already works — that
step is being handled separately, not part of this prompt). You do not need to wire them
here; just be aware they exist so the lesson's `Practice Loop` above stays consistent with
real exercises the learner will actually see, which it already is (Adapter, Facade,
Decorator, Flyweight are all represented).

## 5. Output format

Output the complete, updated `GetAuthoredLessonContent` method body, ready to paste over the
existing method in `api/Data/JavaVerticalSeedData.cs`.

After the code block, report:
- Whether the module restructure (Section 0) was already applied or you had to apply it first.
- Confirmation the new `"16-structural-patterns"` case was added with all 6 sections and 12
  self-check questions.
- Any discrepancy you hit between what this prompt assumes and what you actually found in
  the file.

## 6. Self-check before you output

1. The lesson has exactly these six `##` headings in order: Concepts Covered, Practical
   Backend Scenario, Practice Loop, Evidence of Understanding, Suggested Extension,
   Self-Check (From Class Material).
2. All 12 self-check questions are present, none dropped, none duplicated.
3. Every `"` inside the content is doubled (`""`), not single or backslash-escaped.
4. No other lesson's content was touched.

## 7. Operational note

After pasting the LLM's output in and saving, if this is the first time `16-structural-patterns`
is being populated (fresh from the module restructure, `ContentStatus = "Outline"`), no
database reset is needed — the normal seeder will pick it up on the next restart. If you are
re-running this prompt to fix something after it was already seeded once, reset it first:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug = '16-structural-patterns';
```

Then rebuild/restart the API.
