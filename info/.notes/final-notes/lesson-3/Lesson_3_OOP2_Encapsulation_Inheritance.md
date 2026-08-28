---
lesson_id: java-spring-lld-oop-foundations-03-oop2-encapsulation-inheritance
lesson_title: "Lesson 3 — OOP-2: Encapsulation Complete, Copy Semantics & Inheritance"
lesson_order: 3

pathway_id: java-spring-lld
pathway_name: "Java Low-Level Design & Spring Architecture"

module_id: oop-foundations
module_name: "OOP Foundations"
module_order: 1

difficulty: Medium-Hard
estimated_minutes: 60
content_status: Published

learning_outcomes:
  - "Apply the four-tier access modifier matrix to enforce minimum required visibility at each class boundary."
  - "Implement the immutability pattern using private final fields, no setters, and a final class declaration."
  - "Chain constructors using this(...) to route all initialization through a single master constructor."
  - "Distinguish shallow copy from deep copy and implement a copy constructor that eliminates reference aliasing."
  - "Build an inheritance hierarchy using extends and super(), delegating shared initialization to a parent constructor."
  - "Override equals() and hashCode() consistently to preserve correctness in hash-based collections."

created_date: "2026-08-28"
last_updated: "2026-08-28"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 10
  has_coding_exercises: true
  exercise_count: 3
  has_further_reading: true
  resource_count: 2
---

<!-- CHAPTER_BODY_START -->

# Lesson 3 — OOP-2: Encapsulation Complete, Copy Semantics & Inheritance

## Concepts Covered

Access modifiers form the outer visibility boundary of encapsulation. The four tiers — `private` (declaring class only), default/package-private (same package, no keyword), `protected` (same package and subclasses across any package), and `public` (unrestricted) — impose a graduated perimeter that controls which callers can reach which state. The design discipline is to grant the minimum required visibility: a field that serves only its own class has no reason to be package-private, and a method intended for subclass specialization has no reason to be public. The `final` keyword adds a second enforcement axis orthogonal to visibility: a `final` field cannot be reassigned after the constructor completes (the compiler treats any subsequent assignment as an error), a `final` method cannot be overridden by a subclass even when it is `public`, and a `final` class cannot be extended at all. Combining these produces the immutability pattern: declare the class `final`, make every field `private final`, provide getters and computed results but no setters, and perform defensive copies on any mutable objects passed in as constructor arguments. An immutable `Fare` class is the canonical example — once a surge multiplier of 1.2x is locked in at trip-acceptance time, no downstream repricing service can silently alter it because `setMultiplier()` simply does not exist on the type. Any renegotiated fare requires constructing a new `Fare` object, leaving the accepted original untouched. Constructor chaining via `this(...)` keeps initialization DRY within this sealed structure: a `Driver` class may expose a full four-argument constructor, a two-argument partial constructor, and a no-arg default, but all three must route through the master constructor that increments `totalRegisteredDrivers++`. Without chaining, each overload carries its own copy of that bookkeeping, and a future change — adding a secondary metric, say — has to be applied across every branch. The rule is absolute: `this(...)` must be the very first statement in a constructor body, and it is mutually exclusive with `super(...)` in the same constructor, because both demand the first slot.

Copy semantics address a failure mode that access modifiers alone cannot close. When an object holds a reference to a mutable inner object, assigning that reference during copy construction creates an alias — not a copy. Two `Trip` instances that both hold `this.route = other.route` share a single `Route` heap object; a call to `tripCopy.getRoute().setSource("Whitefield")` silently rewrites the source on `originalTrip` as well, because both variables reach the same memory address. A deep copy constructor fixes this by allocating a fresh inner object with the same values: `this.route = new Route(other.route)`. The decision rule is crisp: if the nested object is immutable — a `String`, a `Fare`, or any properly sealed class — sharing its reference is safe and memory-efficient because no caller can mutate the shared value; if it is mutable, deep copying is mandatory for isolation. This distinction is not merely theoretical: shallow aliasing is one of the most common root causes of state-corruption bugs in multi-threaded Java services, where two threads operate on what they believe are independent entities that are actually one. Inheritance layers on top of sealed structure through the `extends` keyword. An abstract `Vehicle` parent declares shared fields (`vehicleId`, `licensePlate`, `capacity`) and an abstract `calculateFare(double distanceKm)` method; `Car`, `Auto`, and `Bike` each call `super(vehicleId, licensePlate, capacity)` to delegate shared initialization and override only what differs — their per-km rate and fare formula. Every class in Java implicitly extends `java.lang.Object`, which supplies a default `equals()` that compares references (identity, not value equality) and a default `hashCode()` derived from the object's memory address. The contract between them is strict: if `a.equals(b)` returns `true`, then `a.hashCode()` must equal `b.hashCode()`. Overriding only `equals()` breaks this contract. Two `Trip` objects with the same `tripId` that are logically equal produce different hash codes under the default implementation; `HashSet` computes the bucket from the hash first, never reaching `equals()` to compare them, and stores both as distinct entries — a silent deduplication failure in a collection you expected to hold unique trips.

```java
// Shallow Copy — reference assignment. One Route object lives in heap memory;
// both tripA and tripCopy point to it. Mutating one corrupts the other.
public Trip(Trip other) {
    this.tripId     = other.tripId;
    this.fareAmount = other.fareAmount;
    this.route      = other.route;           // aliased reference, not a copy
}

// Deep Copy — a fresh Route is constructed with the same field values.
// tripA.route and tripCopy.route are independent heap objects.
public Trip(Trip other) {
    this.tripId     = other.tripId;
    this.fareAmount = other.fareAmount;
    this.route      = new Route(other.route); // independent heap object
}
```

## Practical Backend Scenario

A ride dispatch service manages `Trip` entities, each carrying a mutable `Route` that the system can update mid-trip for traffic rerouting or pickup-point corrections. When a driver is reassigned mid-trip, the dispatcher archives the pre-reassignment `Trip` to preserve the audit trail for dispute resolution. Without a deep copy constructor, the archived instance shares the `Route` reference with the live trip — rerouting the live trip's source address for the new pickup also silently rewrites the archived record, making the pre-reassignment state unrecoverable. The `Fare` attached to each `Trip` is an immutable value object: once set at 1.2x surge at acceptance time, no repricing thread can mutate it; any updated fare creates a new `Fare` instance, while the fare stored in the archived trip remains exactly what the driver accepted and what the audit record must show.

## Practice Loop

1. Implement `Fare` as a fully immutable value object: declare the class `final`, mark all fields `private final` (base fare and surge multiplier), provide only getters and a `getFinalFare()` computed result, and write no setters — verify the compiler rejects any attempt to reassign a field after the constructor completes.
2. Implement `Route` (mutable: source and destination settable) and `Trip` (holds a `Route` and a `Fare`). Write a shallow copy constructor for `Trip` using direct reference assignment for the `route` field, then write a unit test that modifies the copy's route source and asserts the original is unchanged — confirm the assertion fails, proving aliasing.
3. Count every call site outside `Trip` that reaches `route.setSource()` or `route.setDestination()` on the inner field. Each is a line of code that can corrupt the original through the aliased copy. Replace the shallow assignment with `this.route = new Route(other.route)` and re-run the test; confirm the assertion now passes.
4. Add an abstract `Vehicle` class with `protected` fields `vehicleId`, `licensePlate`, and `capacity`, and an abstract `calculateFare(double distanceKm)` method. Implement `Car` (15.0 per km) and `Auto` (10.0 per km), each calling `super(vehicleId, licensePlate, capacity)` from their constructor and providing a concrete fare override.
5. Override `equals()` and `hashCode()` on `Trip` using `tripId` as the identity field. Add two `Trip` objects with the same `tripId` to a `HashSet<Trip>` and assert the set size is 1. Then remove only the `hashCode()` override, re-run, and observe the size become 2 — confirming that `equals()` without `hashCode()` leaves the contract broken.

## Evidence of Understanding

You can explain why `private final` fields alone are insufficient for immutability — a non-`final` class can be subclassed, and the subclass can introduce setters that expose the parent's state through the child's type. You can trace heap state after a shallow copy to show that two object references point to the same inner object, then demonstrate in a test that a deep copy constructor eliminates the aliasing. You can build a two-level vehicle hierarchy using `extends` and `super()`, override `calculateFare` in each subclass, and confirm that a polymorphic collection of `Vehicle` references dispatches to the correct implementation at runtime. You can break the `equals`/`hashCode` contract deliberately — overriding only `equals` — and show the resulting `HashSet` duplication that makes the violation concrete.

## Suggested Extension

Add a `TripArchiveService` backed by a `HashMap<String, Trip>` that stores deep copies of trips at dispatch time. Write a test that reroutes the live trip's source address after archiving, then retrieves the archived trip by `tripId` and confirms its route still holds the original source — verifying deep copy isolation and the `equals`/`hashCode` contract in a single, integrated scenario.

<!-- CHAPTER_BODY_END -->

Reference: Effective Java, 3rd ed., Joshua Bloch — Items 10 (equals), 11 (hashCode), 17 (Minimize mutability)

---

<!-- MCQ_SECTION_START -->

## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1

**QUESTION_ID:** Q1
**QUESTION_TITLE:** Access Modifier — Cross-Package Subclass Visibility
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
Which access modifier makes a member accessible to subclasses in a different package, but NOT to unrelated classes in that same package?

**OPTIONS:**
- [ ] A: `private`
- [ ] B: default (no modifier)
- [x] C: `protected`
- [ ] D: `public`

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
`protected` grants access within the declaring package (like default) AND to subclasses in any package. An unrelated class in a different package has no access. `public` removes all restrictions, so it also allows unrelated classes in the same package — it does not meet the constraint. `private` and default are both too restrictive.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 — the four-tier visibility matrix

**KEYWORDS:** access-modifiers, protected, visibility, encapsulation

### QUESTION_BLOCK_END: Q1

---

### QUESTION_BLOCK_START: Q2

**QUESTION_ID:** Q2
**QUESTION_TITLE:** Constructor Chaining — Placement Rule
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
In Java, where must a `this(...)` constructor call be placed within a constructor body?

**OPTIONS:**
- [ ] A: Anywhere before the first field assignment
- [ ] B: After all field assignments are complete
- [x] C: As the very first statement in the constructor body
- [ ] D: Only in a constructor that takes no arguments

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
The Java Language Specification (JLS §8.8.7) requires that both `this(...)` and `super(...)` appear as the first statement of a constructor body. The compiler enforces this at compile time — any code before `this(...)` is a compile error. This ensures the delegated constructor fully initializes the object before any additional logic runs.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 — constructor chaining via this(...)

**KEYWORDS:** constructor-chaining, this(), constructor-overloading, initialization

### QUESTION_BLOCK_END: Q2

---

### QUESTION_BLOCK_START: Q3

**QUESTION_ID:** Q3
**QUESTION_TITLE:** Class-Level Data Members
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
What keyword is used to make class-level data members in Java — members that belong to the class itself and are shared across all instances?

**OPTIONS:**
- [ ] A: `const`
- [ ] B: `final`
- [ ] C: `auto`
- [x] D: `static`

**CORRECT_ANSWER_KEY:** D
**CORRECT_ANSWER_INDEX:** 3

**EXPLANATION:**
`static` designates a member as class-level: one copy exists in the method area regardless of how many instances are created. `const` is a reserved word in Java but has no use — compile-time constants use `static final`. `final` makes a variable unresettable but does not make it class-level (a `final` instance field is per-object). `auto` does not exist in Java.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 — constructor chaining example uses static totalRegisteredDrivers

**KEYWORDS:** static, class-level, instance-vs-class, data-members

### QUESTION_BLOCK_END: Q3

---

### QUESTION_BLOCK_START: Q4

**QUESTION_ID:** Q4
**QUESTION_TITLE:** Immutability — Required Combination
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
A `Fare` class should be fully immutable so no subclass can introduce a setter that breaks the guarantee. Which combination of characteristics is required?

**OPTIONS:**
- [ ] A: All fields `private` and all methods declared `final`
- [x] B: The class declared `final` and all fields declared `private final`
- [ ] C: All fields `private final` and a private constructor
- [ ] D: All fields declared `static final`

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Declaring the class `final` prevents subclassing — no subclass can add a setter or expose a field. Declaring each field `private final` ensures the field is inaccessible from outside and cannot be reassigned after construction. Omitting setters completes the recipe. Option A's `final` methods prevent method overriding but do not prevent a subclass from adding entirely new setter methods. Option C (private constructor) prevents subclassing but also prevents any external instantiation via normal constructors, which is overly restrictive and not the standard immutability recipe. Option D makes class-level constants, not immutable per-instance state.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 — immutability pattern

**KEYWORDS:** immutability, final-class, private-final, encapsulation

### QUESTION_BLOCK_END: Q4

---

### QUESTION_BLOCK_START: Q5

**QUESTION_ID:** Q5
**QUESTION_TITLE:** Shallow Copy — Aliasing Behaviour
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
A `Trip` copy constructor contains `this.route = other.route`. After creating `tripCopy` from `originalTrip`, the caller executes `tripCopy.getRoute().setSource("Delhi")`. What is the state of `originalTrip.getRoute().getSource()`?

**OPTIONS:**
- [ ] A: The original source — the copy owns an independent Route
- [x] B: "Delhi" — both Trip objects reference the same Route heap object
- [ ] C: `null` — the Route field was cleared during copy construction
- [ ] D: A `NullPointerException` is thrown because Route was not deeply copied

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
`this.route = other.route` copies the reference (a 64-bit pointer), not the object. Both `tripCopy.route` and `originalTrip.route` point to the same `Route` instance in heap memory. Calling `setSource("Delhi")` through either reference modifies the single shared object, so reading source through either reference returns "Delhi". This is aliasing — one object, multiple names.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 — shallow vs deep copy code block

**KEYWORDS:** shallow-copy, aliasing, reference, heap, copy-constructor

### QUESTION_BLOCK_END: Q5

---

### QUESTION_BLOCK_START: Q6

**QUESTION_ID:** Q6
**QUESTION_TITLE:** equals() Without hashCode() in a HashSet
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A `Trip` class overrides `equals()` to return `true` when two trips share the same `tripId`. It does NOT override `hashCode()`. Two distinct `Trip` objects — both with `tripId = "T-101"` — are added to a `HashSet<Trip>`. How many entries does the set contain?

**OPTIONS:**
- [ ] A: 0 — the broken contract causes an exception during insertion
- [x] B: 2 — the unoverridden hashCode produces different bucket assignments, and equals() is never called
- [ ] C: 1 — HashSet calls equals() first to detect duplicates before consulting hashCode()
- [ ] D: It depends on JVM garbage-collection timing

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
`HashSet` uses a two-step lookup: first compute `hashCode()` to find the bucket, then scan that bucket's chain with `equals()`. When `hashCode()` is not overridden, Java's default implementation (from `Object`) derives the hash from memory identity — two distinct objects almost always produce different hashes, land in separate buckets, and `equals()` is never called between them. Both trips are stored, giving a set size of 2. Option C has the pipeline backwards; `hashCode()` always comes first. The contract states equal objects must have equal hashes — not the converse — so the JVM cannot enforce it at runtime, making option A wrong.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 — equals/hashCode contract; Practice Loop, Step 5

**KEYWORDS:** equals, hashCode, HashSet, contract, Object, bucket

### QUESTION_BLOCK_END: Q6

---

### QUESTION_BLOCK_START: Q7

**QUESTION_ID:** Q7
**QUESTION_TITLE:** final Field — Assignment Rules
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A `Driver` class declares `private final long driverId`. Which statement correctly describes how this field may be assigned?

**OPTIONS:**
- [ ] A: It must be assigned in the field declaration itself; constructor assignment is not allowed
- [ ] B: It can be assigned repeatedly from within any instance method
- [x] C: It can be assigned exactly once, either in a field initializer or in any constructor of the class
- [ ] D: It is automatically assigned the default value 0L and cannot be explicitly set

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
A `final` instance field must be definitely assigned before the constructor completes (JLS §8.3.1.2). Assignment can happen at the declaration site (`private final long driverId = 1001L`) or inside any constructor body — but whichever path executes must assign it exactly once. The compiler performs definite-assignment analysis and rejects constructors that might exit without assigning a `final` field, or that assign it more than once. Instance methods cannot assign a `final` field after construction — that is a compile error.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 — final keyword at the field level

**KEYWORDS:** final, field, assignment, constructor, definite-assignment

### QUESTION_BLOCK_END: Q7

---

### QUESTION_BLOCK_START: Q8

**QUESTION_ID:** Q8
**QUESTION_TITLE:** this() and super() — Mutual Exclusivity
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why is it impossible for `this(...)` and `super(...)` to both appear explicitly in the same constructor?

**OPTIONS:**
- [ ] A: The JVM only permits one parent-class initializer call per class
- [x] B: Both must occupy the first statement of the constructor body — a structural impossibility in a single constructor
- [ ] C: `super(...)` is implicitly invoked after `this(...)` completes, making an explicit call redundant
- [ ] D: `this(...)` internally delegates to `super(...)`, so an explicit super call would execute it twice

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The Java Language Specification mandates that both `this(...)` and `super(...)` appear as the first statement of a constructor body. A constructor body has exactly one first statement, so only one of them can hold that slot. When `this(...)` is used, the delegated master constructor is responsible for calling `super(...)` (either explicitly or via the implicit no-arg super call the compiler inserts). This ensures the inheritance chain is initialized exactly once in the correct order. Option C is partially true — the delegated constructor will call super — but "redundant" misrepresents the error: the compiler rejects the double placement as a structural violation, not as a logical redundancy.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 — this() and super() mutual exclusivity

**KEYWORDS:** constructor-chaining, this(), super(), first-statement, JLS

### QUESTION_BLOCK_END: Q8

---

### QUESTION_BLOCK_START: Q9

**QUESTION_ID:** Q9
**QUESTION_TITLE:** super() in a Subclass Constructor
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given the following code, what does the `super(vehicleId, licensePlate, 4)` call accomplish?

```java
public class Car extends Vehicle {
    private static final double PER_KM_RATE = 15.0;

    public Car(String vehicleId, String licensePlate) {
        super(vehicleId, licensePlate, 4);
    }

    @Override
    public double calculateFare(double distanceKm) {
        return distanceKm * PER_KM_RATE;
    }
}
```

**OPTIONS:**
- [ ] A: It creates a new `Vehicle` instance and stores it as a hidden parent field inside `Car`
- [x] B: It invokes `Vehicle`'s constructor to initialize the shared fields `vehicleId`, `licensePlate`, and `capacity` on the current object
- [ ] C: It calls a static factory method on `Vehicle` that pre-configures four-seat defaults
- [ ] D: It overrides `Vehicle`'s constructor with `Car`-specific behaviour

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
There is only one object being constructed — the `Car` instance. `super(vehicleId, licensePlate, 4)` delegates the initialization of shared state to `Vehicle`'s constructor, which assigns the inherited fields on that same object. No second `Vehicle` instance is created. This is the standard inheritance delegation pattern: shared fields live in the parent constructor; subclass-specific fields and overrides live in the child. Option A reflects a common misconception that Java uses composition internally for inheritance — it does not.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 — inheritance with extends and super(); Practice Loop, Step 4

**KEYWORDS:** super(), inheritance, constructor-delegation, Vehicle, extends

### QUESTION_BLOCK_END: Q9

---

### QUESTION_BLOCK_START: Q10

**QUESTION_ID:** Q10
**QUESTION_TITLE:** Constructor Chaining — Static Counter Trace
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Given the following `Driver` class, what is `Driver.totalCount` after executing all three statements in the order shown?

```java
public class Driver {
    static int totalCount = 0;
    long id; String name; double rating; boolean isOnline;

    public Driver(long id, String name, double rating, boolean isOnline) {
        this.id = id; this.name = name;
        this.rating = rating; this.isOnline = isOnline;
        Driver.totalCount++;
    }
    public Driver(long id, String name) { this(id, name, 0.0, false); }
    public Driver() { this(0L, "Anonymous", 0.0, false); }
}

// Execution:
new Driver();
new Driver(1L, "Alice");
new Driver(2L, "Bob", 4.8, true);
```

**OPTIONS:**
- [ ] A: 1 — only the master constructor is counted
- [ ] B: 2 — the no-arg and partial constructors are excluded
- [x] C: 3 — every construction routes through the master constructor, incrementing the counter once per object
- [ ] D: 0 — `totalCount++` inside a chained constructor is not executed

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
Constructor chaining with `this(...)` means `new Driver()` calls `this(0L, "Anonymous", 0.0, false)`, which calls the four-argument master constructor — `totalCount++` runs once. `new Driver(1L, "Alice")` chains to the master — `totalCount++` again. `new Driver(2L, "Bob", 4.8, true)` calls the master directly — `totalCount++` a third time. Result: 3. This is the key benefit of chaining: the counter exists in exactly one place and runs exactly once per object regardless of which overload was called.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 — constructor chaining ensures single-path initialization

**KEYWORDS:** constructor-chaining, this(), static-counter, totalCount, initialization

### QUESTION_BLOCK_END: Q10

<!-- MCQ_SECTION_END -->

---

<!-- EXERCISES_SECTION_START -->

## Coding Exercises

### EXERCISE_BLOCK_START: EX1

**EXERCISE_ID:** EX1
**EXERCISE_TITLE:** Deep Copy Constructors — Point and Rectangle
**DIFFICULTY:** Intermediate
**BLOOM_LEVEL:** Application
**ESTIMATED_TIME_MINUTES:** 30
**SOURCE_TYPE:** FROM_MATERIAL

**SKILLS_TESTED:**
- Implementing a copy constructor on a simple value class (Point)
- Propagating deep copy through a composite class (Rectangle) across three constructor overloads
- Understanding that every Rectangle constructor must produce independent Point heap objects to prevent aliasing

**SCENARIO:**
The `Rectangle` class holds two `Point` objects — `topLeft` and `bottomRight`. Implementing any constructor with a shallow reference assignment (e.g. `this.topLeft = topLeft`) would allow mutation through one `Rectangle` to corrupt another's corner. Every `Rectangle` constructor must create fresh `Point` instances so that no two `Rectangle` objects ever share a `Point` heap object.

**STARTER_CODE_STRUCTURE:**
```
exercises/exercise-03-ex1-point-rectangle/
├── pom.xml
└── src/
    ├── main/java/
    │   ├── Point.java           (stub: fields declared, constructors to implement)
    │   └── Rectangle.java       (stub: fields declared, all 3 constructors to implement)
    └── test/java/
        ├── PointTest.java        (do not modify — provided by Scaler)
        └── RectangleTest.java    (do not modify — provided by Scaler)
```

**STARTER_CODE — Point.java:**
```java
public class Point {
    // write the code of point class here
}
```

**STARTER_CODE — Rectangle.java:**
```java
public class Rectangle {
    // write the code of Rectangle class here
}
```

**CLASS POINT — REQUIREMENTS:**
- Data members: `int x`, `int y`
- Constructor: `Point(int x, int y)` — assigns x and y
- Copy constructor: `Point(Point p)` — creates a distinct Point object with the same x and y values

**CLASS RECTANGLE — REQUIREMENTS:**
- Data members: `Point topLeft`, `Point bottomRight` (not private — tests read them via reflection)
- Constructor 1: `Rectangle(int topLeftX, int topLeftY, int bottomRightX, int bottomRightY)` — constructs two fresh Points internally
- Constructor 2: `Rectangle(Point topLeft, Point bottomRight)` — deep copies both Points via Point's copy constructor; the stored Points must NOT be the same references as the parameters
- Constructor 3 (copy constructor): `Rectangle(Rectangle r)` — deep copies both inner Points from the source Rectangle

**IMPLEMENTATION_CHECKLIST:**
- [ ] `Point(int, int)` correctly sets x and y
- [ ] `Point(Point)` creates a distinct object (assertNotSame passes) with equal x and y values
- [ ] `Rectangle(Point, Point)` stores deep copies — stored topLeft ≠ passed-in topLeft by reference
- [ ] `Rectangle(Rectangle)` stores deep copies — inner Points are not aliases of the source Rectangle's Points
- [ ] `Rectangle(int, int, int, int)` stores the correct x/y values in topLeft and bottomRight

**TEST_EXPECTATIONS:**
- ✓ `testXDataMemberExists` — Point has an int field named x
- ✓ `testYDataMemberExists` — Point has an int field named y
- ✓ `testTwoParamConstructorSignature` — Point has a constructor taking (int, int)
- ✓ `testTwoParamConstructor` — constructing Point(3, 4) sets x=3, y=4
- ✓ `testCopyConstructorSignature` — Point has a copy constructor taking (Point)
- ✓ `testCopyConstructor` — copy is a distinct object (assertNotSame) with equal x and y
- ✓ `testClassExists` — Rectangle class can be loaded
- ✓ `testTopLeftExists` — topLeft field of type Point exists and is not private
- ✓ `testBottomRightExists` — bottomRight field of type Point exists and is not private
- ✓ `testFourParamConstructorExists` — Rectangle(int, int, int, int) is public
- ✓ `testTwoPointParamConstructorExists` — Rectangle(Point, Point) is public
- ✓ `testOneRectangleParamConstructorExists` — Rectangle(Rectangle) is public
- ✓ `testRectangleConstructorWith2Parameters` — passed-in Points are NOT the same reference as stored Points; stored Point values are correct
- ✓ `testRectangleConstructorWith1Parameter` — stored Points are deep copies of source Rectangle's Points
- ✓ `testRectangleConstructorWith4Parameters` — topLeft and bottomRight hold the correct x/y values

**DELIVERABLES:**
- `Point.java`
- `Rectangle.java`

**WHY_THIS_MATTERS:**
The Rectangle/Point problem is the canonical introduction to deep copy semantics in Java. The same structural pattern — a composite class aggregating mutable value objects — appears in every production domain model, from `Reservation` holding a mutable `TimeSlot` to `Order` holding a mutable `ShippingAddress`. Implementing shallow copy first and watching the mutation propagate (before fixing it with a proper copy constructor) builds the visceral mental model that abstract prose about "aliasing" never does.

**LEARNING_CONNECTION:** Concepts Covered Paragraph 2 — copy semantics, shallow vs. deep copy; Practice Loop Steps 2–3; the code block in Concepts Covered

**EXTERNAL_RESOURCE:** exercises-lesson-03-ex1-point-rectangle-deep-copy.zip

### EXERCISE_BLOCK_END: EX1

---

### EXERCISE_BLOCK_START: EX2

**EXERCISE_ID:** EX2
**EXERCISE_TITLE:** Static Class Members — Math Circle Area
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Application
**ESTIMATED_TIME_MINUTES:** 15
**SOURCE_TYPE:** FROM_MATERIAL

**SKILLS_TESTED:**
- Declaring a static class-level data member
- Implementing a static class-level method that reads the static field
- Understanding that static members are accessible on the class itself, not on an instance

**SCENARIO:**
A utility class `Math` provides geometric calculations without requiring instantiation. The class-level constant `PI` and the method `getCircleArea` must both be `static` — callable as `Math.getCircleArea(radius)`, not as `new Math().getCircleArea(radius)`.

**STARTER_CODE_STRUCTURE:**
```
exercises/exercise-03-ex2-math-static/
├── pom.xml
└── src/
    ├── main/java/
    │   └── Math.java      (stub: class declared, members to implement)
    └── test/java/
        └── MathTest.java   (do not modify — provided by Scaler)
```

**STARTER_CODE — Math.java:**
```java
public class Math {
// write code for Math class here
}
```

**CLASS MATH — REQUIREMENTS:**
- A static data member `PI` of type `double`, with value `3.14`
- A static public method `getCircleArea(int radius)` that returns `PI * radius * radius` as a `double`

**IMPLEMENTATION_CHECKLIST:**
- [ ] `PI` is declared `static double` and equals 3.14
- [ ] `getCircleArea` is declared `static` and returns type `double`
- [ ] `Math.getCircleArea(5)` returns `3.14 * 25 = 78.5`
- [ ] `Math.getCircleArea(0)` returns `0.0`

**TEST_EXPECTATIONS:**
- ✓ `testPiExists` — PI is a static double field with value 3.14 (±0.0001 tolerance)
- ✓ `testGetCircleAreaExists` — getCircleArea is static and has return type double
- ✓ `testGetCircleArea` — getCircleArea(5) returns PI * 5 * 5 (correctly reads the static field)
- ✓ `testGetCircleAreaZeroRadius` — getCircleArea(0) returns 0.0

**DELIVERABLES:**
- `Math.java`

**WHY_THIS_MATTERS:**
The `static` keyword is how Java separates class-level shared state from per-instance state. Understanding that static members exist independently of any object — initialized once at class loading, accessible on the class name directly — is essential before encountering static counters in constructor chaining (e.g. `Driver.totalRegisteredDrivers++`), singleton patterns, or utility libraries. This exercise makes that distinction mechanical.

**LEARNING_CONNECTION:** Concepts Covered Paragraph 1 — static class-level members in constructor chaining; MCQ Q3 (static keyword)

**EXTERNAL_RESOURCE:** exercises-lesson-03-ex2-math-static-class.zip

### EXERCISE_BLOCK_END: EX2

---

### EXERCISE_BLOCK_START: EX3

**EXERCISE_ID:** EX3
**EXERCISE_TITLE:** Basic Constructor — Person Class
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**ESTIMATED_TIME_MINUTES:** 10
**SOURCE_TYPE:** FROM_MATERIAL

**SKILLS_TESTED:**
- Declaring instance data members
- Implementing a constructor that initializes all fields
- Providing getter methods to expose private state

**SCENARIO:**
A `Person` class stores an age and a name. The constructor accepts both and assigns them to private fields. Callers retrieve values via `getAge()` and `getName()`. This is the baseline constructor pattern that all subsequent exercises (copy constructors, chaining, immutability) build on.

**STARTER_CODE_STRUCTURE:**
```
exercises/exercise-03-ex3-person-constructor/
├── pom.xml
└── src/
    ├── main/java/com/assignment/
    │   └── Person.java       (stub: class and package declared, members to implement)
    └── test/java/com/assignment/
        └── PersonTest.java    (do not modify — provided by Scaler)
```

**STARTER_CODE — Person.java:**
```java
package com.assignment;

public class Person {
    // TODO: Declare private data members age and name
        int age;
        String name;
    // TODO: Create a constructor that takes age and name as parameters
        public Person(int age, String name)
        {
            this.age = age;
            this.name = name;
        }

        public Person()
        {
            this.age = 0;
            this.name = "";
        }
    // TODO: Implement getter methods for age and name
        public int getAge()
        {
            return this.age;
        }

        public String getName()
        {
            return this.name;
        }
    public static void main(String[] args) {
        // TODO: Test your implementation by creating a Person object
        Person person = new Person(33, "Ram");
    }
}
```

**CLASS PERSON — REQUIREMENTS (package: `com.assignment`):**
- Data member: `age` (int)
- Data member: `name` (String)
- Constructor: `Person(int age, String name)` — assigns both fields
- Method: `getAge()` — returns the int age value
- Method: `getName()` — returns the String name value

**IMPLEMENTATION_CHECKLIST:**
- [ ] Class is in package `com.assignment`
- [ ] Constructor accepts (int age, String name) in that order
- [ ] `new Person(30, "Bob").getAge()` returns 30
- [ ] `new Person(30, "Bob").getName()` returns "Bob"

**TEST_EXPECTATIONS:**
- ✓ `testPersonConstructor` — Person(30, "Bob") → getAge() = 30, getName() = "Bob"
- ✓ `testAnotherPerson` — Person(22, "Charlie") → getAge() = 22, getName() = "Charlie"

**DELIVERABLES:**
- `src/main/java/com/assignment/Person.java`

**WHY_THIS_MATTERS:**
The constructor is the guaranteed initialization path for object state — the earliest and simplest contract between a class and its callers. Before tackling copy constructors and chaining, internalizing that a constructor's job is to assign every field — and that getters are the only public window into private state — makes every subsequent pattern immediately legible.

**LEARNING_CONNECTION:** Concepts Covered Paragraph 1 — constructor fundamentals; MCQ Q2 (this() placement rule)

**EXTERNAL_RESOURCE:** exercises-lesson-03-ex3-person-constructor.zip

### EXERCISE_BLOCK_END: EX3

<!-- EXERCISES_SECTION_END -->

---

<!-- FURTHER_READING_SECTION_START -->

## Further Reading & Resources

### RESOURCE_BLOCK_START: RESOURCE_1

**RESOURCE_ID:** RESOURCE_1
**RESOURCE_TYPE:** BookChapter
**RESOURCE_TITLE:** Effective Java — Items 10, 11, 17: equals, hashCode, and Immutability
**AUTHOR:** Joshua Bloch
**SOURCE:** Effective Java, 3rd Edition (Addison-Wesley, 2018) — Chapter 3 (Items 10–11) and Chapter 4 (Item 17)

**READING_LEVEL:** Advanced
**TIME_ESTIMATE_MINUTES:** 45

**RELEVANCE:**
Item 17 ("Minimize mutability") is the authoritative recipe for the immutability pattern: five rules, their rationale, and the trade-offs. Items 10 and 11 codify the equals/hashCode contract with worked examples of the failure modes, including the symmetry and transitivity traps that arise when equals() is partially overridden in a hierarchy. These items represent accumulated production-correctness wisdom from the Java platform team.

**KEY_CONCEPTS:**
- The five rules for immutable classes (Item 17)
- Reflexivity, symmetry, transitivity, consistency, and non-null requirements for equals() (Item 10)
- Why objects used as HashMap keys must have stable hashCode() values (Item 11)
- When to use composition over inheritance to avoid equals() contract violations (Item 10)

**RELATIONSHIP_TO_LESSON:** Extends Concepts Covered Paragraphs 1–2; the immutability recipe directly maps to the Fare class implementation; the equals/hashCode section directly informs Practice Loop Step 5.

### RESOURCE_BLOCK_END: RESOURCE_1

---

### RESOURCE_BLOCK_START: RESOURCE_2

**RESOURCE_ID:** RESOURCE_2
**RESOURCE_TYPE:** Documentation
**RESOURCE_TITLE:** Java Language Specification — Constructor Bodies (§8.8.7)
**AUTHOR:** Oracle / JDK Authors
**SOURCE:** https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.8.7

**READING_LEVEL:** Reference
**TIME_ESTIMATE_MINUTES:** 15

**RELEVANCE:**
The JLS section on constructor bodies formally specifies the first-statement rule for explicit constructor invocations (this(...) and super(...)), the definite-assignment requirement for final fields, and the initialization order for the class hierarchy. Reading the spec directly — even just the summary paragraphs — builds the precise mental model that prevents the "why did this compile?" surprises around final fields and constructor delegation.

**KEY_CONCEPTS:**
- Explicit constructor invocation rules (first-statement constraint)
- Definite assignment analysis for final instance fields
- Initialization order: static initializers → instance initializers → constructor body

**RELATIONSHIP_TO_LESSON:** Directly underpins the constructor chaining and immutability content in Concepts Covered Paragraph 1.

### RESOURCE_BLOCK_END: RESOURCE_2

<!-- FURTHER_READING_SECTION_END -->

---

## External References & Downloadable Resources

> **ZIP FILE RENAME NOTE:** Original Scaler ZIP filenames are opaque. Rename before placing in the exercises directory:
> - `1773391164_3c2b63f8261a4a43.zip` → `exercises-lesson-03-ex1-point-rectangle-deep-copy.zip`
> - `1773391167_9f935ce4ea5ba481.zip` → `exercises-lesson-03-ex2-math-static-class.zip`
> - `1773393119_09d9e2722a71ce5e.zip` → `exercises-lesson-03-ex3-person-constructor.zip`

| Reference ID | Type             | Filename                                               | Purpose                                               | Status   |
|---|---|---|---|---|
| ZIP_EX1      | Exercise Starter | exercises-lesson-03-ex1-point-rectangle-deep-copy.zip  | Point + Rectangle deep copy constructor exercise      | Required |
| ZIP_EX2      | Exercise Starter | exercises-lesson-03-ex2-math-static-class.zip          | Math class static field and method exercise           | Required |
| ZIP_EX3      | Exercise Starter | exercises-lesson-03-ex3-person-constructor.zip         | Person class basic constructor exercise               | Required |

**VALIDATION_CHECKLIST:**
- [ ] ZIP_EX1 contains Point.java and Rectangle.java (stubs) + PointTest.java + RectangleTest.java (do not modify tests)
- [ ] ZIP_EX2 contains Math.java (stub) + MathTest.java (do not modify tests)
- [ ] ZIP_EX3 contains com/assignment/Person.java (stub) + com/assignment/PersonTest.java (do not modify tests)
- [ ] All pom.xml files reference Java 11+ and JUnit 5 (jupiter)
- [ ] All URLs in RESOURCE_2 (JLS §8.8.7) are accessible

---

## lessonInteractions.js Entry

Paste this object into `app/src/data/lessonInteractions.js` under the key
`'java-spring-lld/oop-foundations/03-oop2-encapsulation-inheritance'`.

```js
'java-spring-lld/oop-foundations/03-oop2-encapsulation-inheritance': {
  conceptChecks: [
    {
      id: 'lesson-3-concept-check-01',
      eyebrow: 'CONCEPT CHECK 01 — COPY SEMANTICS',
      question:
        'A Trip copy constructor assigns this.route = other.route. After creating tripCopy from originalTrip, the caller invokes tripCopy.getRoute().setSource("Whitefield"). What does originalTrip.getRoute().getSource() return?',
      options: [
        { id: 'a', label: 'A', text: 'The original source — the copy owns an independent Route object' },
        { id: 'b', label: 'B', text: 'null — the Route field was cleared during copy construction' },
        { id: 'c', label: 'C', text: '"Whitefield" — both Trip objects alias the same Route heap object' },
        { id: 'd', label: 'D', text: 'A NullPointerException is thrown at the setSource call' },
      ],
      correctOptionId: 'c',
      explanation:
        'this.route = other.route copies the 64-bit reference, not the object. Both Trip variables point to the same Route in heap memory. Calling setSource() through the copy mutates that single shared object, so reading getSource() through either Trip returns "Whitefield". This is aliasing — one Route, two names.',
      incorrectExplanation:
        'There is only one Route object in heap memory after this constructor runs. Because the copy constructor used reference assignment rather than new Route(other.route), both Trip instances reach the same heap address. Any mutation through either reference affects the same object.',
      hint: 'How many Route objects exist in heap memory after the copy constructor completes?',
    },
    {
      id: 'lesson-3-concept-check-02',
      eyebrow: 'CONCEPT CHECK 02 — EQUALS AND HASHCODE CONTRACT',
      question:
        'A Trip class overrides equals() to return true when two trips share the same tripId, but does NOT override hashCode(). Two distinct Trip objects, both with tripId "T-101", are added to a HashSet<Trip>. How many entries does the set contain?',
      options: [
        { id: 'a', label: 'A', text: '1 — HashSet calls equals() to detect duplicates before consulting hashCode()' },
        { id: 'b', label: 'B', text: '2 — the default hashCode uses memory identity, producing different bucket assignments; equals() is never reached' },
        { id: 'c', label: 'C', text: '0 — the broken contract throws an exception during insertion' },
        { id: 'd', label: 'd', text: 'It depends on JVM garbage-collection timing' },
      ],
      correctOptionId: 'b',
      explanation:
        'HashSet first calls hashCode() to find the bucket, then scans that bucket with equals(). The default hashCode() (from Object) is derived from memory identity — two distinct Trip objects almost always land in separate buckets. equals() is never called between them, and both trips are stored. The set size is 2, not 1.',
      incorrectExplanation:
        'HashSet does not start with equals() — it starts with hashCode(). Because hashCode() is not overridden, the two Trip objects produce different hashes and land in different buckets. equals() is only called within the same bucket, so it never compares these two trips. Both are stored.',
      hint: 'Which method does HashSet call first when deciding where to store an object?',
    },
  ],

  // No architecture diagram — a before/after code block in Concepts Covered
  // provides a clearer mental model than a linear node flow for this lesson's central claim.

  practiceQuestions: [
    // Q1 — FROM_MATERIAL
    {
      id: 'lesson-3-mcq-01',
      question:
        'Which access modifier makes a member accessible to subclasses in a different package, but NOT to unrelated classes in that same different package?',
      options: [
        { id: 'a', label: 'A', text: '`private`' },
        { id: 'b', label: 'B', text: 'default (no modifier)' },
        { id: 'c', label: 'C', text: '`protected`' },
        { id: 'd', label: 'D', text: '`public`' },
      ],
      correctOptionId: 'c',
      explanation:
        '`protected` grants access within the declaring package AND to subclasses in any package. An unrelated class in a different package has no access. `public` removes all restrictions and is therefore too permissive. `private` and default are both too restrictive.',
    },
    // Q2 — FROM_MATERIAL
    {
      id: 'lesson-3-mcq-02',
      question: 'In Java, where must a `this(...)` constructor call be placed within a constructor body?',
      options: [
        { id: 'a', label: 'A', text: 'Anywhere before the first field assignment' },
        { id: 'b', label: 'B', text: 'After all field assignments are complete' },
        { id: 'c', label: 'C', text: 'As the very first statement in the constructor body' },
        { id: 'd', label: 'D', text: 'Only in a constructor that takes no arguments' },
      ],
      correctOptionId: 'c',
      explanation:
        'The Java Language Specification (JLS §8.8.7) requires that both this(...) and super(...) appear as the first statement of a constructor body. The compiler enforces this at compile time — any code before this(...) is a compile error.',
    },
    // Q3 — FROM_MATERIAL
    {
      id: 'lesson-3-mcq-03',
      question:
        'What keyword designates a member as class-level in Java — shared across all instances rather than belonging to any individual object?',
      options: [
        { id: 'a', label: 'A', text: '`const`' },
        { id: 'b', label: 'B', text: '`final`' },
        { id: 'c', label: 'C', text: '`auto`' },
        { id: 'd', label: 'D', text: '`static`' },
      ],
      correctOptionId: 'd',
      explanation:
        '`static` designates a member as class-level: one copy lives in the method area regardless of how many instances exist. `const` is reserved but unused in Java. `final` makes a variable unresettable but does not make it class-level. `auto` does not exist in Java.',
    },
    // Q4 — FROM_MATERIAL
    {
      id: 'lesson-3-mcq-04',
      question:
        'A Fare class must be fully immutable — no subclass should be able to add a setter that breaks the guarantee. Which combination is required?',
      options: [
        { id: 'a', label: 'A', text: 'All fields `private` and all methods declared `final`' },
        { id: 'b', label: 'B', text: 'The class declared `final` and all fields declared `private final`' },
        { id: 'c', label: 'C', text: 'All fields `private final` and a private constructor' },
        { id: 'd', label: 'D', text: 'All fields declared `static final`' },
      ],
      correctOptionId: 'b',
      explanation:
        'Declaring the class `final` prevents subclassing — no subclass can add setters. Declaring each field `private final` prevents reassignment after construction and blocks external access. Together they form the complete immutability guarantee. `final` methods (option A) still allow a subclass to introduce entirely new setter methods. A private constructor (option C) prevents subclassing but also blocks normal external instantiation.',
    },
    // Q5 — FROM_MATERIAL
    {
      id: 'lesson-3-mcq-05',
      question:
        'A Trip copy constructor contains `this.route = other.route`. After creating tripCopy from originalTrip, the caller calls `tripCopy.getRoute().setSource("Delhi")`. What is `originalTrip.getRoute().getSource()`?',
      options: [
        { id: 'a', label: 'A', text: 'The original source — the copy owns an independent Route' },
        { id: 'b', label: 'B', text: '"Delhi" — both Trip objects reference the same Route heap object' },
        { id: 'c', label: 'C', text: 'null — the Route field was cleared during copy' },
        { id: 'd', label: 'D', text: 'A NullPointerException is thrown' },
      ],
      correctOptionId: 'b',
      explanation:
        'this.route = other.route copies the reference pointer, not the object. Both Trip variables point to the same Route in heap memory. Calling setSource("Delhi") through either reference mutates the single shared object, so reading getSource() through originalTrip also returns "Delhi".',
    },
    // Q6 — LLM_GENERATED
    {
      id: 'lesson-3-mcq-06',
      question:
        'A Trip class overrides equals() to compare by tripId but does NOT override hashCode(). Two Trip objects with tripId "T-101" are added to a HashSet<Trip>. How many entries does the set contain?',
      options: [
        { id: 'a', label: 'A', text: '0 — the broken contract causes an exception during insertion' },
        { id: 'b', label: 'B', text: '2 — the unoverridden hashCode produces different bucket assignments and equals() is never called' },
        { id: 'c', label: 'C', text: '1 — HashSet calls equals() first to detect duplicates before consulting hashCode()' },
        { id: 'd', label: 'D', text: 'It depends on JVM garbage-collection timing' },
      ],
      correctOptionId: 'b',
      explanation:
        'HashSet uses hashCode() to find the bucket before it calls equals(). The default hashCode() derives from memory identity — two distinct objects produce different hashes and land in separate buckets; equals() is never compared between them. Both trips are stored, giving a set size of 2.',
    },
    // Q7 — LLM_GENERATED
    {
      id: 'lesson-3-mcq-07',
      question: 'A Driver class declares `private final long driverId`. Which statement correctly describes how this field may be assigned?',
      options: [
        { id: 'a', label: 'A', text: 'It must be assigned in the field declaration itself; constructor assignment is not allowed' },
        { id: 'b', label: 'B', text: 'It can be assigned repeatedly from within any instance method' },
        { id: 'c', label: 'C', text: 'It can be assigned exactly once, either in a field initializer or in any constructor of the class' },
        { id: 'd', label: 'D', text: 'It is automatically assigned the default value 0L and cannot be explicitly set' },
      ],
      correctOptionId: 'c',
      explanation:
        'A final instance field must be definitely assigned before the constructor exits (JLS §8.3.1.2). Assignment can happen at the declaration site or inside any constructor body — but exactly once across the path that executes. The compiler performs definite-assignment analysis. Instance methods cannot assign a final field after construction.',
    },
    // Q8 — LLM_GENERATED
    {
      id: 'lesson-3-mcq-08',
      question: 'Why is it impossible for `this(...)` and `super(...)` to both appear explicitly in the same constructor?',
      options: [
        { id: 'a', label: 'A', text: 'The JVM only permits one parent-class initializer call per class hierarchy' },
        { id: 'b', label: 'B', text: 'Both must occupy the first statement of the constructor body — a structural impossibility in a single constructor' },
        { id: 'c', label: 'C', text: '`super(...)` is implicitly invoked after `this(...)` completes, making an explicit call redundant' },
        { id: 'd', label: 'D', text: '`this(...)` internally delegates to `super(...)`, so an explicit super call would execute it twice' },
      ],
      correctOptionId: 'b',
      explanation:
        'The JLS mandates that both this(...) and super(...) appear as the first statement of a constructor body. A constructor body has exactly one first statement, so only one can hold that slot. When this(...) is used, the delegated master constructor handles the super() call.',
    },
    // Q9 — LLM_GENERATED
    {
      id: 'lesson-3-mcq-09',
      question: 'In the code below, what does `super(vehicleId, licensePlate, 4)` accomplish?',
      codeBlock: `public class Car extends Vehicle {
    private static final double PER_KM_RATE = 15.0;

    public Car(String vehicleId, String licensePlate) {
        super(vehicleId, licensePlate, 4);
    }

    @Override
    public double calculateFare(double distanceKm) {
        return distanceKm * PER_KM_RATE;
    }
}`,
      options: [
        { id: 'a', label: 'A', text: 'It creates a new Vehicle instance and stores it as a hidden parent field inside Car' },
        { id: 'b', label: 'B', text: 'It invokes Vehicle\'s constructor to initialize the shared fields vehicleId, licensePlate, and capacity on the current Car object' },
        { id: 'c', label: 'C', text: 'It calls a static factory method on Vehicle that pre-configures four-seat defaults' },
        { id: 'd', label: 'D', text: 'It overrides Vehicle\'s constructor with Car-specific behaviour' },
      ],
      correctOptionId: 'b',
      explanation:
        'There is only one object being constructed — the Car instance. super(vehicleId, licensePlate, 4) delegates initialization of inherited fields to Vehicle\'s constructor on that same object. No second Vehicle instance is created. This is standard inheritance delegation: shared fields live in the parent constructor, subclass-specific state and overrides live in the child.',
    },
    // Q10 — LLM_GENERATED
    {
      id: 'lesson-3-mcq-10',
      question:
        'After executing the three statements below in order, what is Driver.totalCount?',
      codeBlock: `public class Driver {
    static int totalCount = 0;
    long id; String name; double rating; boolean isOnline;

    public Driver(long id, String name, double rating, boolean isOnline) {
        this.id = id; this.name = name;
        this.rating = rating; this.isOnline = isOnline;
        Driver.totalCount++;
    }
    public Driver(long id, String name) { this(id, name, 0.0, false); }
    public Driver() { this(0L, "Anonymous", 0.0, false); }
}

new Driver();
new Driver(1L, "Alice");
new Driver(2L, "Bob", 4.8, true);`,
      options: [
        { id: 'a', label: 'A', text: '1 — only the master constructor is counted' },
        { id: 'b', label: 'B', text: '2 — the no-arg and partial constructors are excluded' },
        { id: 'c', label: 'C', text: '3 — every construction routes through the master constructor, incrementing the counter once per object' },
        { id: 'd', label: 'D', text: '0 — totalCount++ inside a chained constructor is not executed' },
      ],
      correctOptionId: 'c',
      explanation:
        'new Driver() chains to this(0L, "Anonymous", 0.0, false), which calls the four-argument master → totalCount becomes 1. new Driver(1L, "Alice") chains to the master → totalCount = 2. new Driver(2L, "Bob", 4.8, true) calls the master directly → totalCount = 3. Constructor chaining ensures the counter lives in one place and runs once per object regardless of which overload is used.',
    },
  ],
},
```

---

## lessonExerciseAssociations.js Entry

Add this entry to `app/src/data/lessonExerciseAssociations.js`:

```js
'java-spring-lld/oop-foundations/03-oop2-encapsulation-inheritance': {
  exerciseId: 'java-lld-03-point-rectangle',
},
```

**Note:** EX1 (Point and Rectangle) is the primary exercise rendered by the `ImplementationExercise` component — it is the most lesson-relevant (deep copy is the lesson's central mechanism). EX2 (Math) and EX3 (Person) are seeded as Exercise records in the database and linked to this lesson, but they do not appear in the component unless you change the `exerciseId` value above. Both the database record AND this association file entry are required for any exercise to appear on the lesson page.

---

## Self-Review Checklist

1. **FABRICATION:** All API names (`HashMap`, `HashSet`, `Object.equals`, `Object.hashCode`), JLS references (§8.8.7, §8.3.1.2), and Java mechanics are well-established and verified. No invented class or method names.
2. **GENERIC FILLER:** Zero sentences that would still be true if the lesson topic were swapped. Every sentence names a specific mechanism or consequence of this lesson's content.
3. **STRUCTURE:** Six headers present in order — Concepts Covered, Practical Backend Scenario, Practice Loop, Evidence of Understanding, Suggested Extension, Reference. No extra sections.
4. **SCENARIO CONSISTENCY:** The same ride dispatch scenario (Trip/Route/Fare archiving at reassignment) runs through Practical Backend Scenario, Practice Loop (Steps 1–3 directly reference it), and Suggested Extension (TripArchiveService).
5. **DEPTH:** Concepts Covered runs two dense paragraphs — Paragraph 1 covers access modifiers + final + immutability + constructor chaining; Paragraph 2 covers copy semantics + inheritance + Object contract. Not bullets.
6. **CODE BLOCK:** One before/after code block in Concepts Covered showing shallow vs. deep copy — the central distinction of the lesson. Real, compiling-quality Java.
7. **PRACTICE LOOP:** All 5 steps are concrete actions tied to the Fare/Route/Trip scenario. Step 2 runs a failing test to prove aliasing; Step 3 is the diagnostic (count aliasing call sites and fix them); Step 5 breaks the contract deliberately to confirm the dependency.
8. **REFERENCE:** Single line — Effective Java 3rd ed., Items 10, 11, 17.
9. **SOURCE_TYPE:** All 10 MCQ blocks and all three Exercise blocks carry SOURCE_TYPE. Q1–Q5 = FROM_MATERIAL; Q6–Q10 = LLM_GENERATED. EX1, EX2, EX3 = FROM_MATERIAL (sourced directly from Scaler assignment ZIPs).
10. **WORD COUNT:** Advanced mechanism lesson. Concepts Covered ≈ 480 words prose + code block. Full chapter body ≈ 1000 words. Meets Medium-Hard tier.
11. **ARCHITECTURE DIAGRAM:** Not included — the shallow vs. deep copy before/after code block in Concepts Covered provides a clearer mental model than a node diagram for this lesson's central claim. The service flow (dispatch → archive → retrieve) is linear and already covered in the scenario prose.

**VERDICT:** PASS — ready for human review and Local LLM ingestion.
