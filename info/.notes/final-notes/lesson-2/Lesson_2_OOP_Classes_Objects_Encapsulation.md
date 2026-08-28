<!--
================================================================================
LESSON 2 - OOP-1: CLASSES, OBJECTS & ENCAPSULATION
Neuralascent Editorial Platform - Java/Spring Low-Level Design Module
================================================================================

LOCAL_LLM_PARSING_GUIDE:
This file contains FOUR distinct sections:

1. METADATA_BLOCK (YAML)
   Location: Lines after this comment
   Purpose: Database fields (pathway, module, difficulty, content_status, etc.)
   Destination: Lesson metadata table
   Action: Parse YAML, populate lesson attributes

2. CHAPTER_BODY (Core Teaching Content)
   Markers: <!-- CHAPTER_BODY_START --> to <!-- CHAPTER_BODY_END -->
   Purpose: The actual lesson students read
   Destination: Lesson.ContentBody (database)
   Structure: # Title, ## Concepts Covered, ## Practical Backend Scenario,
              ## Practice Loop, ## Evidence of Understanding, ## Suggested Extension
   Action: Extract everything between markers AS-IS, insert into ContentBody

3. SUPPLEMENTARY_CONTENT (MCQs, Exercises, Resources)
   Markers: Each section has explicit markers
   Purpose: Extended learning and assessment
   Destination: Separate database tables (questions, exercises, resources)
   Action: Parse by section type, extract structured data

4. MANIFEST (Inventory & Validation)
   Current inventory:
   - MCQ_COUNT: 8 (Q1–Q8; Q1–Q7 FROM_MATERIAL, Q8 LLM_GENERATED)
   - EXERCISE_COUNT: 1 (EX1: build Rider class)
   - EXTERNAL_ZIP_COUNT: 1 (lesson-2 starter zip, needs rename — see MANIFEST)
   - RESOURCE_COUNT: 2 (further reading)

SOURCE_TYPE LEGEND (applies to all MCQ and EXERCISE blocks):
   FROM_MATERIAL  — derived directly from provided source files (lecture notes, pre-read, post-read)
   LLM_GENERATED  — added by the LLM based on lesson topics; not from a specific source provided

EXTRACTION WORKFLOW FOR LOCAL_LLM:
1. Parse YAML metadata → Store lesson attributes
2. Extract CHAPTER_BODY (between markers) → Validate 6-section structure → Insert to ContentBody
3. Extract MCQs (between MCQ markers) → Create Question records with QUESTION_ID (Q1–Q8)
4. Extract Exercises (between EXERCISE markers) → Create Exercise records with EXERCISE_ID (EX1)
5. Validate external references (zip) exist before linking
6. Update Lesson.ContentStatus = "Published"

CRITICAL: Chapter body must be extracted cleanly without metadata or supplementary sections.
================================================================================
-->

---
# METADATA BLOCK (DATABASE FIELDS)

lesson_id: java-spring-lld-02-oop-classes-objects
lesson_title: "Lesson 2 — OOP-1: Classes, Objects & Encapsulation"
lesson_order: 2

pathway_id: java-spring-lld
pathway_name: "Java Low-Level Design & Spring Architecture"

module_id: oop-foundations
module_name: "OOP Foundations & Entities"
module_order: 1

difficulty: Intermediate
estimated_minutes: 60
content_status: Published

learning_outcomes:
  - "Distinguish a class (blueprint) from an object (heap instance) and explain the JVM memory model"
  - "Predict the result of assigning one reference variable to another"
  - "Use constructors and the this keyword to initialize fields correctly"
  - "Explain when a member should be static vs instance-level"
  - "Apply encapsulation — private fields with validated methods — to enforce business rules at the entity boundary"

created_date: "2026-08-28"
last_updated: "2026-08-28"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: true
  exercise_count: 1
  has_further_reading: true
  resource_count: 2

---

<!-- CHAPTER_BODY_START: This is the core lesson content. Extract everything between START and END markers (inclusive of headers) for Lesson.ContentBody database field. -->

# Lesson 2 — OOP-1: Classes, Objects & Encapsulation

## Concepts Covered

Abstraction is the overarching principle of OOP — the idea that a complex system is best understood as a set of clearly-bounded ideas working together. Encapsulation, inheritance, and polymorphism are the three mechanisms that implement it. A **class** is a template: it defines the fields an object will carry and the methods it exposes. The class definition occupies minimal JVM memory (bytecode only) and creates no object at runtime. Every call to `new Driver(...)` allocates a distinct **object** on the **heap** — the JVM memory region for dynamically allocated instances — and initializes each field independently. A reference variable on the stack (`Driver d1`) holds the heap address, not the object itself. Assigning `Driver d2 = d1` copies that address; both variables now point at the same heap allocation. `d2.name = "Suresh"` modifies the single shared object, and `d1.name` returns `"Suresh"` afterwards. Two independent Driver objects require two separate `new` calls.

Java initializes unassigned instance fields to zero-equivalents — reference types to `null`, numerics to `0`, booleans to `false` — so a `Driver` created with `new Driver()` and no constructor body has `name = null` and `rating = 0.0`. Constructors replace those defaults with real values; the `this` keyword distinguishes an instance field from a same-named parameter. Without it, `name = name` in a constructor is a no-op: the parameter is assigned to itself, the field stays `null`, and the compiler raises no warning. The `static` keyword marks class-level members shared across every instance — a `totalDrivers` counter that tracks how many Driver objects exist belongs on the class, not on each driver; making it an instance field means every driver holds its own counter starting at zero, which is nonsensical. **Encapsulation** serves two jobs: bundling state and behaviour inside a class, and protecting that state by making fields `private` and routing all changes through methods that enforce business rules. With public fields, any caller anywhere can write `driver.rating = 10.0`, bypassing every validation the team ever agreed on; private fields close that door at compile time:

```java
// Without encapsulation — invalid state compiles silently
public double rating;
driver.rating = 10.0;  // Uber max is 5.0 — no error

// With encapsulation — the rule lives in exactly one place
private double rating;

public void setRating(double newRating) {
    if (newRating < 1.0 || newRating > 5.0) {
        throw new IllegalArgumentException(
            "Rating must be between 1.0 and 5.0, got: " + newRating);
    }
    this.rating = newRating;
}
```

## Practical Backend Scenario

A `FareBoostService` computes dynamic fare multipliers based on driver ratings. In the unencapsulated `Driver` class, `rating` is a public field. A junior engineer writing a test fixture types `driver.rating = 10.0` to simulate a high-rated driver, commits the fixture, and the corrupt value reaches the staging database. Every trip processed by that driver in staging now carries an inflated multiplier, and the regression surfaces only when fare totals look wrong in a dashboard review. In the encapsulated design, `Driver.rating` is `private`; `setRating(double r)` throws `IllegalArgumentException` for any value outside `[1.0, 5.0]`. The test fixture doesn't compile until the engineer supplies a valid rating. The `FareBoostService` reads the value through `driver.getRating()` and has no path to write it directly. When a rating bug does surface in production, the entire blame radius is one method in one class — not a search across every service that ever touched the public field.

## Practice Loop

1. List the `Driver` class fields (`name`, `driverId`, `rating`, `isOnline`, `phoneNumber`) and the operations it must support (`goOnline`, `goOffline`, `acceptRide`, `setRating`, `getRating`, `maskPhoneNumber`) on paper, without any code — you are naming the entity's responsibility boundary before a single line is written.
2. Write the bare class with `public` fields and no methods; from a separate `Main` class, set `driver.rating = 10.0` and `driver.rating = -3.0` — observe that both compile and execute without error.
3. Count every line in your codebase that reads or writes `driver.rating` directly and write down the total. That count is your blast radius: every one of those sites must be audited when an incorrect rating surfaces in production.
4. Add the `private` modifier to `rating`; add `setRating(double r)` with the 1.0–5.0 guard; recompile — observe that every direct field write in step 2 now fails at compile time, forcing all callers through the validated method.
5. Add `private static int totalDrivers = 0;` to the class, increment it inside the constructor with `totalDrivers++`, and add `public static int getTotalDrivers()`. Create three separate Driver objects and call `Driver.getTotalDrivers()` — verify the counter reflects the total across all instances, not a per-object value of 1.

## Evidence of Understanding

You can explain why `Driver d2 = d1` creates no new object and predict that `d2.name = "Suresh"` changes what `d1.name` returns, because both variables hold the same heap address. You can write a `Driver` constructor using `this` to disambiguate field names from parameters and demonstrate that omitting `this` causes fields to silently retain their default values. You can explain the difference between a static field and an instance field by showing that `Driver.totalDrivers` increments with each constructor call while `d1.rating` and `d2.rating` are independent — and you can articulate why making a shared counter an instance field is a design error, not just a style one. You can build a `Driver` class with private fields and a `setRating()` method that rejects invalid values with a descriptive exception, and you can demonstrate that the resulting design eliminates the compile-time path for a `FareBoostService` to corrupt a driver's rating.

## Suggested Extension

Add a `maskPhoneNumber()` method to `Driver` that returns a `String` in the format `+91 XXXXX XX234` — exposing only the last three digits of the subscriber number. Verify that `phoneNumber` is `private`, that no getter returns the raw number, and that the masking logic lives entirely inside `Driver`. The caller that needs the display string receives it in one call without knowing the internal format or length.

---

Reference: Lecture material — "OOP-1: Classes, Objects & Encapsulation" (Scaler, June 2026)

<!-- CHAPTER_BODY_END: End of core lesson content for Lesson.ContentBody field. -->

---

<!-- MCQ_SECTION_START: Multiple-Choice Questions (Assessment). Extract each QUESTION_BLOCK separately. -->

## Multiple-Choice Questions

**SUPPLEMENTARY_CONTENT_TYPE: MCQ**
**SECTION_PURPOSE: Assessment and concept verification**
**DESTINATION: questions table (one record per MCQ)**

---

### QUESTION_BLOCK_START: Q1

**QUESTION_ID:** Q1
**QUESTION_TITLE:** Reference Variable Memory Puzzle
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
What does the following code print?

```java
Driver d1 = new Driver();
d1.name = "Rahul";

Driver d2 = d1;
d2.name = "Suresh";

System.out.println(d1.name);
```

**OPTIONS:**
- [ ] A: Rahul
- [x] B: Suresh
- [ ] C: null
- [ ] D: A NullPointerException is thrown

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
`Driver d2 = d1` copies the reference (the heap address), not the object. Both `d1` and `d2` point to the same single Driver object on the heap. Assigning `d2.name = "Suresh"` modifies that shared object. Reading `d1.name` afterwards returns "Suresh". There is still only one object in memory. Two independent objects require two separate `new` calls.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (reference model)

**KEYWORDS:** reference variable, heap, stack, object identity, memory model

### QUESTION_BLOCK_END: Q1

---

### QUESTION_BLOCK_START: Q2

**QUESTION_ID:** Q2
**QUESTION_TITLE:** Constructor Silent Bug — Missing `this`
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
After calling `new Driver("Rahul", 4.8)` with the constructor below, what is the value of the driver object's `name` field?

```java
public Driver(String name, double rating) {
    name = name;
    rating = rating;
}
```

**OPTIONS:**
- [ ] A: "Rahul" — the parameter is assigned correctly
- [ ] B: A compile error is produced because `name` appears twice
- [x] C: null — the parameter is assigned to itself, leaving the field at its default value
- [ ] D: "Rahul" — Java automatically infers `this.name` when field and parameter share a name

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
`name = name` assigns the local parameter variable to itself — a legal no-op that the compiler accepts without warning. The instance field `name` (which belongs to `this`) is never touched and stays at its default value of `null`. The fix is `this.name = name`, which explicitly addresses the instance field. This is one of the most common beginner mistakes in Java and the reason `this` exists.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (this keyword)

**KEYWORDS:** constructor, this keyword, default values, instance field, parameter shadowing

### QUESTION_BLOCK_END: Q2

---

### QUESTION_BLOCK_START: Q3

**QUESTION_ID:** Q3
**QUESTION_TITLE:** Static vs Instance Field — Driver Count
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
A `Driver` class needs a counter that tracks how many `Driver` objects have ever been created across the entire application. A developer writes this:

```java
public class Driver {
    int totalDrivers = 0;  // incremented in constructor
    // ...
}
```

What is wrong with this design?

**OPTIONS:**
- [ ] A: Nothing — `totalDrivers` will correctly track the total across all Driver objects
- [x] B: Every Driver object gets its own copy of `totalDrivers`, each starting at 0; the field tracks nothing meaningful at the application level
- [ ] C: The field will cause a compile error because counters must be declared `final`
- [ ] D: The field is private and cannot be incremented from the constructor

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
An instance field belongs to each individual object. If five Driver objects are created, there are five separate `totalDrivers` fields, each holding the value 1 (or whatever the constructor set). No single number reflects the total. The fix is `static int totalDrivers = 0` — a static field belongs to the class itself and is shared by every instance, so incrementing it in any constructor accumulates the true total.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (static keyword)

**KEYWORDS:** static, instance field, class-level, shared state, counter

### QUESTION_BLOCK_END: Q3

---

### QUESTION_BLOCK_START: Q4

**QUESTION_ID:** Q4
**QUESTION_TITLE:** Class vs Object — Memory Model
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
Which of the following statements correctly describes the relationship between a class and an object in Java?

**OPTIONS:**
- [ ] A: A class holds all its objects in memory — deleting the class deletes the objects
- [x] B: A class is a blueprint that occupies minimal memory; each object is a separate heap allocation created by `new`
- [ ] C: A class and an object are the same thing; "object" is just informal terminology for a class at runtime
- [ ] D: An object is stored on the stack and the class is stored on the heap

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The class definition (bytecode) is loaded by the JVM and takes up a fixed, small amount of memory. It does not contain objects; it is the specification from which objects are built. Each `new` call allocates a separate block of heap memory for one object, with its own copy of every instance field. The class and its objects are independent: the class is the template, the objects are the instances that live independently on the heap.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (class vs object)

**KEYWORDS:** class, object, heap, JVM, new keyword, blueprint

### QUESTION_BLOCK_END: Q4

---

### QUESTION_BLOCK_START: Q5

**QUESTION_ID:** Q5
**QUESTION_TITLE:** Encapsulation — Preventing Invalid State
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
A `Driver` class has a public `double rating` field. Uber's rating scale is 1.0 to 5.0. Which statement is most accurate?

**OPTIONS:**
- [ ] A: This is acceptable — developers on the team will know not to set invalid ratings
- [ ] B: The field should be `protected` instead of `public` to prevent subclasses from writing invalid values
- [x] C: Any code anywhere in the codebase can write `driver.rating = 10.0` or `driver.rating = -3.0` with no error; making the field `private` and adding a `setRating()` method that validates the range is the only design that enforces the rule at compile and runtime
- [ ] D: The field can stay public; a `validateRating()` method called by callers is sufficient protection

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
Convention-based protection ("developers will know") fails at scale. Any code with a reference to the Driver object can write any value to a public field — a test fixture, a migration script, a refactor that misses a callsite. Making the field `private` removes that path: the compiler rejects direct writes. A `setRating()` method is then the single enforcement point. Option D is procedural thinking in OOP syntax: it relies on callers to remember to call the validator, which is exactly the pattern encapsulation is designed to eliminate.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 + code block; Practical Backend Scenario

**KEYWORDS:** encapsulation, private, access modifiers, validation, business rules

### QUESTION_BLOCK_END: Q5

---

### QUESTION_BLOCK_START: Q6

**QUESTION_ID:** Q6
**QUESTION_TITLE:** Access Modifiers — Scope
**DIFFICULTY:** Easy
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
Which access modifier in Java restricts a field so that only the class that declares it can read or write the field?

**OPTIONS:**
- [x] A: `private`
- [ ] B: `protected`
- [ ] C: `public`
- [ ] D: package-private (no modifier)

**CORRECT_ANSWER_KEY:** A
**CORRECT_ANSWER_INDEX:** 0

**EXPLANATION:**
`private` limits access to the declaring class only. `protected` allows access from the declaring class, same-package classes, and subclasses. Package-private (no modifier) allows access from any class in the same package. `public` allows access from anywhere. For encapsulating internal state that no external code should touch directly, `private` is the correct choice.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (access modifiers)

**KEYWORDS:** access modifiers, private, protected, public, encapsulation

### QUESTION_BLOCK_END: Q6

---

### QUESTION_BLOCK_START: Q7

**QUESTION_ID:** Q7
**QUESTION_TITLE:** Abstraction — Principle vs Pillar
**DIFFICULTY:** Medium-Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL

**QUESTION_TEXT:**
A developer says: "Abstraction is one of the four pillars of OOP — alongside Encapsulation, Inheritance, and Polymorphism." A senior engineer disagrees with the framing. Which response best captures the more precise relationship?

**OPTIONS:**
- [ ] A: The developer is correct — all four are independent, equally-ranked pillars
- [ ] B: Abstraction is not part of OOP at all; it belongs to functional programming
- [x] C: Abstraction is the overarching principle that OOP exists to implement; Encapsulation, Inheritance, and Polymorphism are the three mechanisms through which code achieves it — treating them as four equal pillars obscures that relationship
- [ ] D: Abstraction and Encapsulation are synonyms; the real pillars are only Inheritance and Polymorphism

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
Abstraction is a destination — represent a system as clearly-bounded ideas. The three pillars are routes to that destination: Encapsulation hides internal complexity behind a clean interface; Inheritance generalises shared structure across related types; Polymorphism lets the same method call mean different things for different types. Listing all four at the same level is not wrong, but it misses the hierarchy. In interviews, distinguishing the principle from the mechanisms signals design understanding rather than vocabulary recall.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1 (abstraction as overarching principle)

**KEYWORDS:** abstraction, encapsulation, inheritance, polymorphism, OOP principles

### QUESTION_BLOCK_END: Q7

---

### QUESTION_BLOCK_START: Q8

**QUESTION_ID:** Q8
**QUESTION_TITLE:** Null Reference and Default Field Values
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A `Driver` object is created with `Driver d = new Driver()` using only the no-argument constructor (which has an empty body). The code then calls `System.out.println(d.name.length())`. What happens, and why?

**OPTIONS:**
- [ ] A: It prints 0 — Java initializes String fields to an empty string `""`
- [ ] B: It prints the length of the class name "Driver"
- [x] C: A NullPointerException is thrown — reference-type fields default to null, and calling `.length()` on null dereferences a null reference
- [ ] D: It prints -1 — Java uses -1 to indicate an uninitialized String

**CORRECT_ANSWER_KEY:** C
**CORRECT_ANSWER_INDEX:** 2

**EXPLANATION:**
Java initializes unassigned instance fields to type-specific zero-equivalents: reference types (including `String`) default to `null`, not to `""`. Calling any method on a null reference throws `NullPointerException` at runtime. This is why constructors exist: to replace null defaults with real values before the object is used. The fix is either a constructor that sets `this.name` explicitly, or a null guard before the call. NullPointerException is the most common Java runtime error and almost always traces back to a field or return value that was assumed to be non-null but was not initialized.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2 (default field values); Practice Loop, Step 1

**KEYWORDS:** NullPointerException, default values, null, String, instance field, constructor

### QUESTION_BLOCK_END: Q8

---

<!-- MCQ_SECTION_END -->

---

<!-- EXERCISES_SECTION_START: Coding Exercises (Practical Application). Extract each EXERCISE_BLOCK separately. -->

## Coding Exercises

**SUPPLEMENTARY_CONTENT_TYPE: CODING_EXERCISE**
**SECTION_PURPOSE: Hands-on practice building a real OOP entity from scratch**
**DESTINATION: exercises table (one record per exercise)**
**NOTE:** Exercise starter code provided as zip (see EXTERNAL_REFERENCES below)

---

### EXERCISE_BLOCK_START: EX1

**EXERCISE_ID:** EX1
**EXERCISE_TITLE:** Build the Rider Entity — Classes, Encapsulation & Static Counter
**DIFFICULTY:** Intermediate
**BLOOM_LEVEL:** Application
**ESTIMATED_TIME_MINUTES:** 45
**SOURCE_TYPE:** FROM_MATERIAL

**SKILLS_TESTED:**
- Class definition with fields and methods
- Constructors and the `this` keyword
- `private` fields with validated getters/setters
- `static` counter for class-level state
- Basic encapsulation and invariant enforcement

**SCENARIO:**
In the Uber system we designed `Driver` live in class. Your task is to design `Rider` the same way — from scratch, on your own. A Rider has a name, phone number, email, and a home address they can optionally save. Riders can be active or inactive (a soft delete). Their email must be non-null and non-empty. Their rating (given by drivers) must stay between 1.0 and 5.0 just as driver ratings do. The system needs to know how many Rider objects have been created across the entire application lifetime.

**STARTER_CODE_STRUCTURE:**
```
exercises/exercise-02-rider-entity/
├── pom.xml                          (Maven config, Java 11+, JUnit 5)
├── README.md                        (problem statement)
├── src/main/java/
│   ├── Rider.java                  (EMPTY: you build from scratch)
│   └── RiderException.java         (PROVIDED: domain exception, do not modify)
└── src/test/java/
    └── RiderTest.java              (HIDDEN: tests all invariants)
```

**IMPLEMENTATION_REQUIREMENTS:**
1. Fields: `private String name`, `private String email`, `private String phoneNumber`, `private String savedHomeAddress` (nullable), `private double rating`, `private boolean isActive`, `private static int totalRiders`
2. Parameterized constructor `Rider(String name, String email, String phoneNumber)` — initializes all fields, increments `totalRiders`, sets `isActive = true`, sets `rating = 5.0` (new riders start with perfect rating)
3. Validated `setRating(double r)` — throws `RiderException` for values outside [1.0, 5.0]
4. `saveHomeAddress(String address)` — throws `RiderException` if rider is not active
5. `deactivate()` — sets `isActive = false`; throws `RiderException` if already inactive
6. `public String getMaskedEmail()` — returns the email with everything before `@` replaced by `****`, e.g. `****@gmail.com`
7. `public static int getTotalRiders()` — returns the class-level counter

**IMPLEMENTATION_CHECKLIST:**
- [ ] Constructor validates email is non-null and non-empty; throws `RiderException` if not
- [ ] `setRating()` rejects values outside [1.0, 5.0]
- [ ] `saveHomeAddress()` rejects calls on inactive riders
- [ ] `deactivate()` is idempotent check — throws if already inactive
- [ ] `getMaskedEmail()` hides local part without exposing raw email
- [ ] `totalRiders` is `static` and increments correctly across multiple object creations
- [ ] No public setters for `isActive`, `rating`, or `email`

**TEST_EXPECTATIONS:**
- ✓ Valid constructor call sets name, email, phoneNumber, isActive=true, rating=5.0
- ✓ Constructor throws `RiderException` for null or empty email
- ✓ `setRating(4.2)` succeeds; `setRating(6.0)` throws `RiderException`
- ✓ `saveHomeAddress("...")` throws `RiderException` after `deactivate()` has been called
- ✓ `deactivate()` on an already-inactive rider throws `RiderException`
- ✓ `getMaskedEmail()` returns `****@gmail.com` for input `rahul@gmail.com`
- ✓ `Driver.getTotalRiders()` returns 3 after three separate constructor calls
- ✓ Reflection test: `email`, `rating`, `isActive` fields are private
- ✓ Reflection test: no public setters for `isActive`, `rating`, or `email`

**DELIVERABLES:**
- `Rider.java` with all fields, constructor, and methods
- All tests passing without modification to `RiderTest.java`

**WHY_THIS_MATTERS:**
The Rider entity exercise mirrors exactly what a junior backend engineer writes in week one of a new product team: a domain object that owns its own validation rules. Getting the `static` counter right, the `this` keyword right, the access modifier choices right, and the exception paths right in a fresh class — without a template to follow — is the real competency being tested. Every decision made here (which fields are private? what does the setter validate?) reappears in every entity across the system.

**LEARNING_CONNECTION:** Concepts Covered (both paragraphs), Practice Loop (all 5 steps), Evidence of Understanding, Suggested Extension (masked phone/email)

**EXTERNAL_RESOURCE:** exercises-lesson-02-ex01-rider-entity.zip

### EXERCISE_BLOCK_END: EX1

---

<!-- EXERCISES_SECTION_END -->

---

<!-- FURTHER_READING_SECTION_START: Optional supplementary resources for deeper learning. -->

## Further Reading & Resources

**SUPPLEMENTARY_CONTENT_TYPE: LEARNING_RESOURCE**
**SECTION_PURPOSE: Extend understanding beyond core lesson**
**DESTINATION: resources table (optional)**

---

### RESOURCE_BLOCK_START: RESOURCE_1

**RESOURCE_ID:** RESOURCE_1
**RESOURCE_TYPE:** BookChapter
**RESOURCE_TITLE:** Effective Java — Minimise Accessibility of Classes and Members
**AUTHOR:** Joshua Bloch
**SOURCE:** *Effective Java*, 3rd Edition, Item 15

**READING_LEVEL:** Intermediate
**TIME_ESTIMATE_MINUTES:** 25

**RELEVANCE:**
Bloch's canonical argument for why `private` should be the default access level and why every widening of access is a conscious design decision. Directly grounds the "encapsulation protects internal state" claim in this lesson with production reasoning.

**KEY_CONCEPTS:**
- Information hiding as a design principle
- Choosing the minimum necessary access level
- Why public mutable fields undermine encapsulation
- Instance fields of public classes should rarely be public

**RELATIONSHIP_TO_LESSON:**
Supports Concepts Covered (Paragraph 2 — encapsulation and access modifiers), Practice Loop Step 4, and the Practical Backend Scenario (FareBoostService rating corruption).

### RESOURCE_BLOCK_END: RESOURCE_1

---

### RESOURCE_BLOCK_START: RESOURCE_2

**RESOURCE_ID:** RESOURCE_2
**RESOURCE_TYPE:** BookChapter
**RESOURCE_TITLE:** Java: The Complete Reference — Classes and Objects
**AUTHOR:** Herbert Schildt
**SOURCE:** *Java: The Complete Reference*, 13th Edition, Chapter 6

**READING_LEVEL:** Intermediate
**TIME_ESTIMATE_MINUTES:** 40

**RELEVANCE:**
Comprehensive reference for all mechanics covered in this lesson: class declarations, instance and static members, constructors, `this`, access modifiers, and the Java memory model. The section on the stack-vs-heap distinction (§6) clarifies the reference variable mechanics behind Q1 and the memory puzzle from the pre-read.

**KEY_CONCEPTS:**
- Class member declarations and the `static` modifier
- Constructors and their initialization order
- `this` reference: when and why
- Java memory model: stack frames vs heap allocations
- Access control in detail

**RELATIONSHIP_TO_LESSON:**
Covers all technical claims in Concepts Covered. Particularly useful for Q1 (reference puzzle), Q2 (constructor `this`), Q3 (static vs instance), and the exercise.

### RESOURCE_BLOCK_END: RESOURCE_2

---

<!-- FURTHER_READING_SECTION_END -->

---

<!-- EXTERNAL_REFERENCES_START: Zips and files referenced in this lesson. -->

## External References & Downloadable Resources

**MANIFEST OF EXTERNAL FILES:**

| Reference ID | Type | Filename | Purpose | Size_Est | Status |
|---|---|---|---|---|---|
| ZIP_EX1 | Exercise Starter | exercises-lesson-02-ex01-rider-entity.zip | Maven project: Build Rider entity from scratch | ~1.5 MB | Required |

**RENAME_NOTE:** The zip provided in the source folder (`1773391155_0f285e8c0551f6da.zip`) should be renamed to `exercises-lesson-02-ex01-rider-entity.zip` before seeding. Confirm it contains: `pom.xml` (Java 11+, JUnit 5), `README.md`, `src/main/java/Rider.java` (empty), `src/main/java/RiderException.java` (provided), and `src/test/java/RiderTest.java` (hidden tests).

**VALIDATION:**
Before seeding this lesson into production, verify:
- [ ] `exercises-lesson-02-ex01-rider-entity.zip` exists and is correctly named
- [ ] `pom.xml` references Java 11+ and JUnit 5
- [ ] `Rider.java` is empty (starter scaffold only — no implementation)
- [ ] `RiderException.java` is provided (learner should not write it)
- [ ] `RiderTest.java` is present in test directory
- [ ] All test assertions in `RiderTest.java` match the TEST_EXPECTATIONS above

<!-- EXTERNAL_REFERENCES_END -->

---

<!-- LESSONINTERACTIONS_JS_DATA_START
This block is NOT part of the lesson body. It is reference data for a human
to manually add to app/src/data/lessonInteractions.js under the key:
'java-spring-lld/oop-foundations/02-oop-classes-objects'

Claude MUST NOT edit app/src/data/lessonInteractions.js directly.
-->

## lessonInteractions.js Reference Data

```js
// Key: 'java-spring-lld/oop-foundations/02-oop-classes-objects'
// Paste this object as the value in lessonInteractions.js

{
  conceptChecks: [
    {
      id: 'lesson-2-concept-check-01',
      eyebrow: 'CONCEPT CHECK 01 — REFERENCE MODEL',
      question: 'After `Driver d2 = d1;` followed by `d2.name = "Suresh";`, what does `System.out.println(d1.name)` print?',
      options: [
        { id: 'a', label: 'A', text: 'Rahul — d1 was assigned first and is unchanged' },
        { id: 'b', label: 'B', text: 'Suresh — both variables point to the same heap object' },
        { id: 'c', label: 'C', text: 'null — d2 points to a new empty object' },
        { id: 'd', label: 'D', text: 'A NullPointerException is thrown' }
      ],
      correctOptionId: 'b',
      explanation: 'Assigning d2 = d1 copies the reference (the heap address), not the object. Both variables point at the same Driver on the heap, so writing to d2 is writing to d1.',
      incorrectExplanation: 'Java reference variables hold addresses, not objects. d2 = d1 means both point to the same heap allocation — there is still only one Driver in memory.',
      hint: 'Ask yourself: after d2 = d1, how many Driver objects exist on the heap?'
    },
    {
      id: 'lesson-2-concept-check-02',
      eyebrow: 'CONCEPT CHECK 02 — STATIC KEYWORD',
      question: 'A `Driver` class has `int totalDrivers = 0;` (no `static`) and the constructor does `totalDrivers++`. After creating three Driver objects, what does `d1.totalDrivers` equal?',
      options: [
        { id: 'a', label: 'A', text: '3 — it tracks the total across all instances' },
        { id: 'b', label: 'B', text: '1 — each object has its own copy, incremented once at construction' },
        { id: 'c', label: 'C', text: '0 — instance fields are not modified by constructors' },
        { id: 'd', label: 'D', text: 'A compile error — non-static fields cannot be incremented in constructors' }
      ],
      correctOptionId: 'b',
      explanation: 'Without `static`, every Driver object gets its own copy of `totalDrivers`. Each copy is incremented once by that object\'s constructor, ending at 1. Only `static int totalDrivers` is shared across all instances and would reach 3.',
      incorrectExplanation: 'Instance fields belong to each object independently. `d1.totalDrivers`, `d2.totalDrivers`, and `d3.totalDrivers` are three separate integers, each holding 1. To get a shared counter, the field must be `static`.',
      hint: 'How many copies of a non-static field exist when you create three objects?'
    }
  ],

  architecture: {
    id: 'lesson-2-encapsulation-boundary',
    eyebrow: 'PRACTICAL BACKEND SCENARIO — FARE BOOST SERVICE',
    boundaryLabel: 'ENCAPSULATION BOUNDARY',
    boundaryText: 'Driver.setRating() is the single validated gate — no external code can write to rating directly.',
    nodes: [
      { id: 'caller1',   label: 'FareBoostService',    kind: 'input'    },
      { id: 'caller2',   label: 'TestFixture',          kind: 'input'    },
      { id: 'boundary',  label: 'Driver.setRating()',   kind: 'boundary', highlighted: true },
      { id: 'field',     label: 'private double rating', kind: 'output'  }
    ]
  },

  practiceQuestions: [
    {
      // SOURCE_TYPE: FROM_MATERIAL
      id: 'lesson-2-mcq-01',
      question: 'What does the following code print?\n\nDriver d1 = new Driver();\nd1.name = "Rahul";\nDriver d2 = d1;\nd2.name = "Suresh";\nSystem.out.println(d1.name);',
      options: [
        { id: 'a', label: 'A', text: 'Rahul' },
        { id: 'b', label: 'B', text: 'Suresh' },
        { id: 'c', label: 'C', text: 'null' },
        { id: 'd', label: 'D', text: 'A NullPointerException is thrown' }
      ],
      correctOptionId: 'b',
      explanation: 'd2 = d1 copies the reference (heap address), not the object. Both variables point at the same Driver. Writing d2.name modifies that shared object, so d1.name returns "Suresh".'
    },
    {
      // SOURCE_TYPE: FROM_MATERIAL
      id: 'lesson-2-mcq-02',
      question: 'After calling `new Driver("Rahul", 4.8)` with the constructor `name = name; rating = rating;` (no `this`), what is the value of the driver\'s name field?',
      options: [
        { id: 'a', label: 'A', text: '"Rahul" — assigned correctly' },
        { id: 'b', label: 'B', text: 'A compile error — name appears twice' },
        { id: 'c', label: 'C', text: 'null — the parameter assigned to itself, field untouched' },
        { id: 'd', label: 'D', text: '"Rahul" — Java auto-infers this.name when names match' }
      ],
      correctOptionId: 'c',
      explanation: 'name = name reassigns the local parameter to itself — a legal no-op. The instance field this.name is never touched and stays null. The fix is this.name = name.'
    },
    {
      // SOURCE_TYPE: FROM_MATERIAL
      id: 'lesson-2-mcq-03',
      question: 'A Driver class has `int totalDrivers = 0;` (no static) and increments it in the constructor. After three Driver objects are created, what does d1.totalDrivers equal?',
      options: [
        { id: 'a', label: 'A', text: '3 — shared total across all instances' },
        { id: 'b', label: 'B', text: '1 — each object has its own copy, incremented once' },
        { id: 'c', label: 'C', text: '0 — instance fields are not modified by constructors' },
        { id: 'd', label: 'D', text: 'Compile error — cannot increment non-static in constructor' }
      ],
      correctOptionId: 'b',
      explanation: 'Without static, every Driver gets its own totalDrivers, each equal to 1. Only static int totalDrivers is shared and would accumulate to 3.'
    },
    {
      // SOURCE_TYPE: FROM_MATERIAL
      id: 'lesson-2-mcq-04',
      question: 'Which statement correctly describes the relationship between a class and an object in Java?',
      options: [
        { id: 'a', label: 'A', text: 'A class holds all its objects — deleting the class deletes the objects' },
        { id: 'b', label: 'B', text: 'A class is a blueprint with minimal memory; each object is a separate heap allocation created by new' },
        { id: 'c', label: 'C', text: 'A class and an object are the same thing; "object" is just informal for a class at runtime' },
        { id: 'd', label: 'D', text: 'An object is stored on the stack and the class is stored on the heap' }
      ],
      correctOptionId: 'b',
      explanation: 'The class definition (bytecode) is the template. Each new call allocates a separate heap block for one object with its own copy of every instance field. Class and objects are independent.'
    },
    {
      // SOURCE_TYPE: FROM_MATERIAL
      id: 'lesson-2-mcq-05',
      question: 'A Driver class has `public double rating`. Which statement is most accurate?',
      options: [
        { id: 'a', label: 'A', text: 'Acceptable — developers will know not to set invalid values' },
        { id: 'b', label: 'B', text: 'Should be protected to prevent subclass corruption' },
        { id: 'c', label: 'C', text: 'Any code anywhere can write driver.rating = 10.0; making it private with a validated setRating() is the only design that enforces the rule' },
        { id: 'd', label: 'D', text: 'Fine to keep public; a validateRating() method called by callers is sufficient' }
      ],
      correctOptionId: 'c',
      explanation: 'Convention-based protection fails at scale. Any code with a Driver reference can write any value to a public field. Private + setRating() means the compiler rejects direct writes and the method is the single enforcement point.'
    },
    {
      // SOURCE_TYPE: FROM_MATERIAL
      id: 'lesson-2-mcq-06',
      question: 'Which access modifier restricts a field so that only the class that declares it can read or write it?',
      options: [
        { id: 'a', label: 'A', text: 'private' },
        { id: 'b', label: 'B', text: 'protected' },
        { id: 'c', label: 'C', text: 'public' },
        { id: 'd', label: 'D', text: 'package-private (no modifier)' }
      ],
      correctOptionId: 'a',
      explanation: 'private limits access to the declaring class only. protected allows same-package + subclasses. Package-private allows the same package. public allows everywhere.'
    },
    {
      // SOURCE_TYPE: FROM_MATERIAL
      id: 'lesson-2-mcq-07',
      question: 'A developer lists "four pillars of OOP: Abstraction, Encapsulation, Inheritance, Polymorphism." A senior engineer says the framing is imprecise. Which response is most accurate?',
      options: [
        { id: 'a', label: 'A', text: 'The developer is correct — all four are independent equal pillars' },
        { id: 'b', label: 'B', text: 'Abstraction is not part of OOP; it belongs to functional programming' },
        { id: 'c', label: 'C', text: 'Abstraction is the overarching principle OOP exists to implement; Encapsulation, Inheritance, and Polymorphism are the three mechanisms that achieve it' },
        { id: 'd', label: 'D', text: 'Abstraction and Encapsulation are synonyms; the real pillars are only Inheritance and Polymorphism' }
      ],
      correctOptionId: 'c',
      explanation: 'Abstraction is the destination (represent a system as bounded ideas). The three pillars are mechanisms to get there. Treating all four as equal obscures the hierarchy.'
    },
    {
      // SOURCE_TYPE: LLM_GENERATED
      id: 'lesson-2-mcq-08',
      question: 'A Driver is created with `Driver d = new Driver()` (empty constructor). The code then calls `System.out.println(d.name.length())`. What happens?',
      options: [
        { id: 'a', label: 'A', text: 'Prints 0 — Java initializes Strings to empty string ""' },
        { id: 'b', label: 'B', text: 'Prints the length of the class name "Driver"' },
        { id: 'c', label: 'C', text: 'NullPointerException — reference-type fields default to null, not ""' },
        { id: 'd', label: 'D', text: 'Prints -1 — Java uses -1 for uninitialized Strings' }
      ],
      correctOptionId: 'c',
      explanation: 'Reference-type fields default to null, not to "". Calling .length() on null throws NullPointerException at runtime. Constructors exist precisely to replace null defaults with real values before use.'
    }
  ]
}
```

<!-- LESSONINTERACTIONS_JS_DATA_END -->

---

## How to Use This Lesson

**For Learners:**
1. Read **Concepts Covered** — the reference model and encapsulation are the two non-obvious mechanics that trip people up in later lessons if missed here.
2. Run the memory puzzle (`d2 = d1`) yourself in IntelliJ before class confirms the answer.
3. Work through **Practice Loop** with IntelliJ open — steps 2–4 are most valuable done in order with a real compiler.
4. Complete **EX1** (Rider entity) without looking at the Driver class from lecture. If you must look, close it before writing.
5. Answer **Q1–Q8** after the exercise — they test exactly what the exercise exposes.

**For Local LLM (Insertion Workflow):**
1. Extract YAML metadata → Populate lesson attributes
2. Extract CHAPTER_BODY (between markers) → Validate 6-section structure → Insert to `Lesson.ContentBody`
3. Extract MCQs (Q1–Q8) → Create Question records; SOURCE_TYPE Q1–Q7 = FROM_MATERIAL (auto-approve), Q8 = LLM_GENERATED (human review)
4. Extract Exercise EX1 → Create Exercise record; FROM_MATERIAL (source: pre-read homework instruction); link renamed zip
5. Extract Resources → Create LessonResource records (optional)
6. Validate zip exists and is renamed correctly (see RENAME_NOTE)
7. Update `Lesson.ContentStatus` = "Published"

---

**Previous Lesson:** Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems
**Next Lesson:** Lesson 3 — OOP-2: Inheritance & Polymorphism
