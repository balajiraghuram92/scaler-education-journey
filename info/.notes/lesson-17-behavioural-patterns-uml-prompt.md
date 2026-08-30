# Prompt for Local LLM — Add Lesson 17: Behavioural Patterns & UML Diagrams

Paste everything below this line into the local LLM as-is. All lesson content and MCQs below
were already authored by hand from the real Scaler source material — you are NOT being
asked to write new prose or invent examples. Copy everything verbatim into the correct
place in the C# code. If any step below doesn't match what you find in the actual file,
STOP and report the discrepancy instead of guessing.

---

## 0. Prerequisite check — READ THIS FIRST

This prompt adds content to lesson slug `17-behavioural-patterns-uml`. That slug only
exists if the module restructure and the `16-structural-patterns` lesson have already been
applied. Check `api/Data/JavaVerticalSeedData.cs` right now:

- If you find 6 modules (Badges "Module 1" through "Module 6"), a `SeedModule4Lessons`
  method containing slugs `14-solid-principles`, `15-creational-patterns`,
  `16-structural-patterns`, `17-behavioural-patterns-uml`, and a `GetAuthoredLessonContent`
  case for `"16-structural-patterns"` already returning real content — the prior two rounds
  have already been applied. Proceed to Section 1.
- If any of that is missing, first apply `info/.notes/module-restructure-prompt.md` and then
  `info/.notes/lesson-16-structural-patterns-prompt.md`, in that order, in full, before
  proceeding here.

Do not proceed with Section 1 until `17-behavioural-patterns-uml` exists as a lesson with
placeholder `ContentBody`.

---

## 1. What to do

Find the lesson with slug `"17-behavioural-patterns-uml"` inside
`api/Data/JavaVerticalSeedData.cs`. Add a case for it inside the
`GetAuthoredLessonContent(string slug)` switch, returning the full lesson content given in
Section 2 below — the same mechanism already used for lessons 4–16. Do not touch any other
lesson's content.

## 2. Lesson content — copy this exactly into the new switch case

```
"17-behavioural-patterns-uml" => @"# Lesson 17 — Behavioural Patterns & UML Diagrams

## Concepts Covered

Behavioural patterns govern how objects communicate and distribute responsibility for an algorithm or a reaction to change — distinct from structural patterns (which govern how objects are wired together) and creational patterns (which govern how objects are made).

**Strategy — Selecting an Algorithm, Not Branching Inside One:**
Strategy extracts an algorithm into its own interface so the algorithm in use can be swapped without touching the class that uses it. The failure mode it replaces: one method full of `if (mode.equals(""car""))` / `else if (mode.equals(""bike""))` branches, where adding a new mode means editing and re-testing existing, already-working code — a direct violation of the Open-Closed Principle and Single Responsibility. Strategy's fix: each mode becomes its own class implementing a shared interface (e.g. `CarPathCalculator`, `BikePathCalculator`), and the class that needs the behavior (e.g. `PricingManager`, `VideoStreamingManager`) holds a reference to the interface, not to any concrete implementation, receiving it through its constructor. A concrete strategy class deliberately does **not** take a ""mode"" parameter in its methods — the class itself already represents one specific way of doing the task, so telling it what mode it is would be redundant and would reopen the door to the same branching the pattern exists to remove. Most concrete strategies are stateless (all their inputs arrive as method parameters, nothing is stored as instance state), which is exactly why a Strategy Factory can safely cache and return one shared instance per type instead of constructing a new object on every call. A `StrategyFactory`'s only job is selection: mapping some input (a mode string, an enum) to the correct concrete strategy object — it never executes the algorithm itself, and a common bug is a factory built on a lookup map that only covers some of the possible inputs, silently returning `null` for any input it wasn't given an entry for, which surfaces later as a `NullPointerException` far from the real mistake.

**Strategy vs. Chain of Responsibility — Choosing One vs. Trying in Sequence:**
It's a common misclassification to call a fallback/retry sequence a ""Strategy"" because multiple implementations share one interface. The test is behavioral: Strategy selects exactly one implementation up front and uses only that one. A payment flow that tries Razorpay, then falls back to Stripe on failure, then falls back to PayPal, is not Strategy — no single provider was chosen ahead of time, and control passes along a sequence until one succeeds. That ordered, try-until-handled shape is Chain of Responsibility, a related but distinct pattern.

**Observer — Broadcasting a Change to Many Listeners:**
Observer lets a subject (the publisher) notify an open-ended set of listeners (observers) whenever its state changes, without the publisher needing to know anything about who those listeners are or how many there will be. The publisher holds a list of a shared `Observer` interface, exposes `subscribe`/`unsubscribe` (or `register`/`addObserver`) to manage that list, and — critically — must actually iterate the list and invoke each observer inside every method that changes state. The single most common Observer bug is exactly that last step going missing: a `setTemperature(double temp)` method that updates the field but never loops through `observers` and calls their update method leaves every registered listener silently uninformed, even though registration itself worked perfectly. Unsubscribing removes an observer from the list going forward only — a `Publisher` that subscribes a `Logger`, publishes an event (which the logger receives), unsubscribes the logger, then publishes a second event, delivers only the first event to that logger, not the second. This is why adding an entirely new kind of subscriber (e.g. a `WhatsAppService` next to existing `AlertService`, `EmailService`, `SlackService` observers) requires zero changes to the publisher — it's simply one more object registering itself against the same interface.

**Strategy vs. Observer — the Real Distinguishing Question:**
Both patterns program against one interface implemented by multiple classes, which is why they're often confused. The distinguishing question is intent: does the caller pick exactly *one* implementation to delegate to (Strategy), or does the caller notify *every* registered implementation at once (Observer)? A `RoutingStrategy` selects one AI model to route a query to; a list of `Observer`s all receive the same order-placed event simultaneously. Neither pattern is ""better"" — they solve different problems that happen to share the same programming-to-an-interface mechanic.

**UML — A Shared Notation for Communicating Design:**
UML (Unified Modelling Language) is a standardized visual notation so any engineer reads the same diagram shapes the same way, independent of implementation language. It splits into **Structural UML** (Class, Object, Component diagrams — describing the frozen structure of a codebase) and **Behavioral UML** (Use Case, Sequence, Activity diagrams — describing behavior over time). A Class diagram box has three sections: name, then attributes (`- privateField: Type`, `+ publicField: Type`), then methods (`+ methodName(): ReturnType`), using `-`/`+`/`#` for private/public/protected. Static members are underlined regardless of access modifier. An abstract class's name and abstract methods are shown in italics; an interface carries a `<<interface>>` stereotype label; an enum carries `<<enumeration>>`. In Use Case diagrams, a solid **includes** arrow means the parent use case *always* triggers the child (e.g. ""Enroll in Course"" includes ""Make Payment""); a dashed **extends** arrow means the child is one *optional* variant of the parent (e.g. ""Pay by UPI"" and ""Pay by Card"" both extend ""Make Payment""). For HAS-A relationships, a hollow diamond denotes **aggregation** (both objects can exist independently — e.g. a reusable `Module` shared across multiple `Course`s), while a filled diamond denotes **composition** (the child cannot exist without the parent — e.g. a one-off `Module` that belongs to exactly one `Course`). There is deliberately no universal rule for which one applies to a given relationship — the same `Module`-to-`Course` relationship can be legitimately aggregation or composition depending on the actual product requirement, and this judgment call cannot be automated away by an ORM.

## Practical Backend Scenario

A logistics platform's delivery-fee calculation started as one method with an `if/else` chain per vehicle type; every new vehicle type meant editing and re-testing that same method. Refactored with Strategy, each vehicle type is its own `DeliveryFeeStrategy` implementation, selected once by a `DeliveryFeeStrategyFactory` and injected into the `OrderPricingService` constructor — adding a new vehicle type is now a new class, with zero changes to existing, already-shipped fee logic. Separately, the platform's order-status system needs to trigger unrelated side effects on every state change: sending an SMS, updating a warehouse dashboard, and logging an audit trail. An `Order` publisher holds a list of `OrderObserver`s and loops through them inside `updateStatus()`; when the growth team later wants to add a loyalty-points side effect, they register a new `LoyaltyPointsObserver` without touching `Order` at all. A design review of the payment flow (Razorpay, then Stripe, then PayPal on failure) correctly identifies this as Chain of Responsibility, not Strategy, since the flow tries providers in sequence rather than committing to one upfront. Finally, before implementing any of this, the team sketches a UML class diagram for the `Order`/`OrderObserver` relationship and a schema diagram showing that `Order` and `Customer` need a foreign key on the ""many"" side, while `Order` and `Promotion` need a junction table since a promotion can apply to many orders and an order can carry many promotions.

## Practice Loop

1. Take a method with an `if/else` chain over 3+ modes and refactor it into a `Strategy` interface with one concrete class per mode, injected via constructor.
2. Build a `StrategyFactory` backed by a lookup map; deliberately call it with an input the map doesn't cover and observe the `NullPointerException`, then fix it with an explicit `IllegalArgumentException` for unknown inputs instead of a silent `null`.
3. Implement a publisher/`Observer` pair; write a test proving that unsubscribing an observer mid-flow means it receives events published before, but not after, the unsubscribe call.
4. Deliberately write a publisher that updates its own field but forgets to loop through observers — confirm no observer fires — then fix it by adding the notification loop.
5. Draw a UML class diagram (by hand or in a tool) for one of the systems built in this lesson, correctly using `-`/`+`/`#` prefixes, underlined statics, italicized abstract members, and a hollow or filled diamond for any HAS-A relationship, justifying your aggregation-versus-composition choice in one sentence.

## Evidence of Understanding

You can explain why a concrete strategy class should never take a mode parameter, and why most strategies are safely shareable as cached singletons. You can distinguish Strategy (picks one implementation) from Chain of Responsibility (tries several in sequence) from Observer (notifies all at once) using the same one-interface-many-classes shape. You can identify the single most common Observer bug (missing notification loop) on sight. You can read and produce a basic UML class diagram with correct visibility, static, and abstract notation, and justify an aggregation-versus-composition choice as a product judgment rather than a memorized rule.

## Suggested Extension

Combine Strategy and Observer in one system: build a trading alert engine where a `StrategyFactory` selects the correct `TradingIndicatorStrategy` (momentum, volatility) per instrument, and every computed alert is broadcast to a list of `AlertObserver`s (email, SMS, dashboard) — then draw the UML class diagram for the resulting design, including the aggregation/composition judgment call for the relationship between an `Instrument` and its list of `TradingIndicatorStrategy` results.

## Self-Check (From Class Material)

**Q1.** 
```java
Amazon amazon = new Amazon();
amazon.register(o -> System.out.println(""Invoice generated for "" + o));
amazon.register(o -> System.out.println(""Inventory updated for "" + o));
amazon.orderPlaced(""ORD123"");
```
Assuming `register` adds to an `ArrayList` and `orderPlaced` loops through and calls each observer, what gets printed?
- A. Only ""Invoice generated for ORD123""
- B. Only ""Inventory updated for ORD123""
- C. Both lines print, in the order they were registered
- D. Nothing prints, this code has a compile error

**Answer: C** — `orderPlaced` iterates subscribers in insertion order and invokes each, so both lambdas fire in registration order.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q4)*

**Q2.** A `RouterFactory` is built like this:
```java
private static final Map<QueryComplexity, RoutingStrategy> STRATEGIES = Map.of(
    QueryComplexity.SIMPLE, new SimpleQueryStrategy()
);
static RoutingStrategy getStrategy(QueryComplexity c) {
    return STRATEGIES.get(c);
}
```
When called with `QueryComplexity.COMPLEX`, what happens?
- A. It automatically falls back to `SimpleQueryStrategy`
- B. It throws a `ClassNotFoundException` immediately
- C. It compiles but silently does nothing
- D. It returns `null`, which will likely cause a `NullPointerException` later when a method is called on it

**Answer: D** — `Map.get()` returns `null` for a missing key; there is no fallback, so the caller crashes with an NPE the moment it calls a method on the result.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q5)*

**Q3.** A payment system tries Razorpay first, then Stripe, then PayPal, only moving to the next provider if the previous one fails. Which pattern best fits this situation?
- A. Neither Strategy nor Observer — this is closer to Chain of Responsibility
- B. Strategy, since each payment provider is a different way of paying
- C. Observer, since all providers get notified together
- D. Factory, since it creates payment objects

**Answer: A** — Strategy picks one implementation up front; Observer notifies all subscribers at once. Sequential try-until-success is Chain of Responsibility.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q6)*

**Q4.** Why does a concrete strategy class like `CarPathCalculator` NOT take a `mode` parameter in its methods?
- A. Because Java doesn't allow extra parameters in overridden methods
- B. Because the class itself already represents one specific way of doing the task, so it doesn't need to be told what ""mode"" it is
- C. Because mode is only needed inside the Factory class
- D. Because strategies are stateless and can't accept any parameters at all

**Answer: B** — The class instance itself already IS the ""car mode"" implementation; passing a mode flag in would reintroduce the branching Strategy exists to remove.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q7)*

**Q5.** 
```java
List<TradingIndicatorStrategy> strategies = List.of(new MomentumStrategy(), new VolatilityStrategy());
for (TradingIndicatorStrategy s : strategies) {
    if (s.supportsType(""VOLATILITY"")) {
        System.out.println(s.calculate(50, 70));
    }
}
```
`VolatilityStrategy.calculate` returns `Math.abs(current - previous)`. What is printed?
- A. -20.0
- B. 0.0
- C. 20.0
- D. Nothing is printed

**Answer: C** — Only `VolatilityStrategy` matches; `Math.abs(50 - 70) = 20.0`.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q8)*

**Q6.** A `WeatherMonitoringApplication`'s `setTemperature(double temp)` updates its field but never notifies its registered observers. `TemperatureService` is registered correctly but never receives updates. What is missing?
- A. The `Observer` interface needs a `getTemperature` method
- B. `observers` should be a `Map` instead of a `List`
- C. `setTemperature` needs to be declared `static`
- D. A call to notify all observers (e.g., looping through observers and calling their update method) inside `setTemperature`

**Answer: D** — Registration only adds to the list; the publisher must explicitly loop and invoke observers whenever state changes. Missing that loop is the most common Observer bug.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q9)*

**Q7.** Your team's third-party analytics library only understands `trackEvent(XML data)`, but your codebase only works with `log(JSON data)`. Which pattern bridges them without changing either side?
- A. Adapter
- B. Strategy
- C. Observer
- D. Factory

**Answer: A** — Two incompatible interface shapes needing translation without modifying either side is the textbook Adapter scenario.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q10)*

**Q8.** Why is it usually fine for a Strategy Factory to reuse the same strategy object every time instead of creating a new one on each call?
- A. Because Java does not allow creating multiple objects of the same class
- B. Because most strategy classes have no changing internal state, so sharing one instance (like a Singleton) is safe and avoids unnecessary object creation
- C. Because reusing objects makes the code violate Open-Closed Principle
- D. Because Factory pattern requires objects to be reused

**Answer: B** — Concrete strategies are typically stateless, so one shared instance behaves identically for every caller.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q11)*

**Q9.** 
```java
Publisher publisher = new Publisher();
Logger logger = new Logger();
publisher.subscribe(logger);
publisher.publish(""Order Placed"");
publisher.unsubscribe(logger);
publisher.publish(""Order Shipped"");
```
What is printed (assuming `Logger.update` prints ""LOG: "" + event)?
- A. Both ""LOG: Order Placed"" and ""LOG: Order Shipped"" print
- B. Only ""LOG: Order Shipped"" prints
- C. Only ""LOG: Order Placed"" prints
- D. Nothing is printed

**Answer: C** — `logger` is subscribed for the first publish, then unsubscribed before the second — so only the first event reaches it.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q12)*

**Q10.** What is the key difference in intent between Strategy and Observer, even though both rely on one interface with multiple implementing classes?
- A. Strategy is only for payments; Observer is only for notifications
- B. Strategy picks exactly one implementation to use; Observer notifies many implementations at once
- C. Strategy requires a Factory; Observer never uses a Factory
- D. There is no real difference between them

**Answer: B** — Strategy delegates to a single chosen algorithm; Observer broadcasts to every registered listener simultaneously.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Q3)*

**Q11.** What is the main problem with writing one method that uses if-else blocks to handle different ""modes"" (like car, bike, walk) inside the same class?
- A. It violates Open-Closed and Single Responsibility Principles, since adding a new mode means editing existing working code
- B. The code runs slower than using classes
- C. Java does not allow more than 3 if-else conditions
- D. It cannot be tested using JUnit

**Answer: A** — Every new mode requires reopening and modifying the same method, and one class now owns logic for every mode.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q5)*

**Q12.** In the Strategy pattern, what is the actual job of the Factory class (e.g., `PathCalculatorFactory`)?
- A. To decide and return the correct strategy object based on some input
- B. To execute the algorithm itself
- C. To notify all subscribers when an event occurs
- D. To translate one interface into another

**Answer: A** — The Factory's only job is selection and construction; the chosen strategy itself executes the algorithm.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 120, Assignment Q9)*
",
```

## 3. What must NOT change

- Do not touch any lesson other than `17-behavioural-patterns-uml`.
- Do not modify `NeedsLessonContent`, `BackfillLessonContent`, or any other method.
- Keep C# verbatim-string escaping consistent: every literal `"` inside the content above is
  already written as `""` — copy it exactly.
- Do not add a 7th section or reorder the six sections.
- Note: only 12 of the 15 authored MCQs are included in the Self-Check above (Q13, Q14 —
  the PricingStrategy composition-output and interface-argument-bug code-trace questions —
  and the WhatsApp-Observer registration question were left out to keep the section to a
  reasonable length). All 15 are preserved in
  `info/.notes/scaler-raw-notes/mcqs/day120-behavioural-patterns-additional-problems.md` for
  future use (e.g. in exercise write-ups or a later revision pass) — do not treat their
  absence here as data loss.

## 4. Attach the exercise packages (informational — you don't need to create these files)

6 new Java exercise packages covering Strategy and Observer have been analyzed and written
to `info/.notes/scaler-raw-notes/exercise-templates-batch3/` (contract-only templates plus
full problem-statement writeups). That step is handled separately, not part of this prompt.

## 5. Output format

Output the complete, updated `GetAuthoredLessonContent` method body, ready to paste over the
existing method in `api/Data/JavaVerticalSeedData.cs`.

After the code block, report:
- Whether the Section 0 prerequisites were already in place.
- Confirmation the new `"17-behavioural-patterns-uml"` case was added with all 6 sections
  and 12 self-check questions.
- Any discrepancy you hit between what this prompt assumes and what you actually found.

## 6. Self-check before you output

1. The lesson has exactly these six `##` headings in order: Concepts Covered, Practical
   Backend Scenario, Practice Loop, Evidence of Understanding, Suggested Extension,
   Self-Check (From Class Material).
2. All 12 self-check questions are present, none dropped, none duplicated.
3. Every `"` inside the content is doubled (`""`), not single or backslash-escaped.
4. No other lesson's content was touched.

## 7. Operational note

If this is the first time `17-behavioural-patterns-uml` is being populated fresh from the
module restructure (`ContentStatus = "Outline"`), no database reset is needed. If re-running
this prompt after it was already seeded once:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug = '17-behavioural-patterns-uml';
```

Then rebuild/restart the API.
