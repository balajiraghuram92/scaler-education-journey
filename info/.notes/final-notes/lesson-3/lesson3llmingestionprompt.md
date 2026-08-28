# Neuralascent — Lesson 3 Ingestion Prompt (Pre-filled, Copy-Paste Ready)

**Lesson:** Lesson 3 — OOP-2: Encapsulation Complete, Copy Semantics & Inheritance  
**Slug:** `03-oop2-encapsulation-inheritance`  
**Module:** `oop-foundations`  
**Lesson file:** `info/.notes/final-notes/lesson-3/Lesson_3_OOP2_Encapsulation_Inheritance.md`

**When to use:** After the self-review checklist passes. Paste the block below directly into your Local LLM session.

---

═══════════════════════════════════════════════
START OF PROMPT — COPY EVERYTHING BELOW THIS LINE
═══════════════════════════════════════════════

## TASK: Wire Lesson 3 into the Neuralascent app

You are wiring a reviewed, approved lesson file into the four app files listed below.
Read all source files carefully before writing any output. Do not guess at field names or
method signatures — derive everything from what you read.

---

## STEP 1 — READ THESE FILES IN FULL

1. **`info/.notes/final-notes/lesson-3/Lesson_3_OOP2_Encapsulation_Inheritance.md`**  
   Primary source. All lesson content, exercises, MCQs, and JS data come from here.

2. **`api/Data/JavaVerticalSeedData.cs`**  
   Find `GetAuthoredLessonContent(string slug)` — a switch statement. You will add one new `case`.  
   Also find where Exercise records are seeded (look for a method that creates `Exercise` objects
   or inserts them via a list). You will add three new Exercise records following the same pattern.

3. **`app/src/data/lessonInteractions.js`**  
   Find `const lessonInteractions = { ... }`. You will add one new key. Do NOT touch existing keys.

4. **`app/src/data/lessonExerciseAssociations.js`**  
   Find `const lessonExerciseAssociations = { ... }`. You will add one new entry for this lesson.
   Do NOT touch existing entries.

---

## STEP 2 — ADD THE LESSON CONTENT BODY (`api/Data/JavaVerticalSeedData.cs`)

Find `GetAuthoredLessonContent(string slug)` — it is a switch statement with cases like:

```csharp
"01-intro-to-lld" => @"# Lesson 1 — ...",
"02-oop-1-intro-lab" => @"# Lesson 2 — ...",
_ => null
```

Add this case immediately before `_ => null`:

```csharp
"03-oop2-encapsulation-inheritance" => @"[CHAPTER BODY HERE]",
```

**CHAPTER BODY extraction rules:**
- Copy the text between `<!-- CHAPTER_BODY_START -->` and `<!-- CHAPTER_BODY_END -->` markers in the lesson file **verbatim**.
- In a C# verbatim string (`@"..."`), escape every double-quote by doubling it: `"` → `""`.
- Do NOT include the HTML marker comments themselves in the string.
- The string must end with a newline before the closing `"`.
- Backticks are fine inside C# verbatim strings — no escaping needed.

Do NOT change any other part of the seed file.

---

## STEP 3 — SEED THREE EXERCISE RECORDS (`api/Data/JavaVerticalSeedData.cs`)

Find where Exercise records are seeded (look for a list of `Exercise` objects, a method named
something like `SeedExercises`, or a collection passed to `db.Exercises.AddRange`). Follow the
exact same pattern — same field names, same property assignments.

Seed these three exercises linked to lesson slug `03-oop2-encapsulation-inheritance`:

### Exercise 1 — Point and Rectangle (Primary)

| Field | Value |
|---|---|
| Id / ExerciseId | `java-lld-03-point-rectangle` |
| Title | `Deep Copy Constructors — Point and Rectangle` |
| Difficulty | `Intermediate` |
| EstimatedMinutes | `30` |
| LessonSlug (or LessonId FK) | `03-oop2-encapsulation-inheritance` |
| ExternalResource (zip filename) | `exercises-lesson-03-ex1-point-rectangle-deep-copy.zip` |
| Description / Scenario | `Implement class Point with x and y fields, a two-param constructor, and a copy constructor. Implement class Rectangle with topLeft and bottomRight Point fields and three constructors (four ints, two Points, one Rectangle) that each perform deep copies of the Point objects so no two Rectangle instances share a Point heap reference.` |
| Skills | `Deep copy constructors, copy semantics, aliasing prevention` |

**What the tests verify (PointTest.java + RectangleTest.java):**
- Point has int fields x and y
- Point(int, int) sets x and y correctly
- Point(Point) creates a distinct object (assertNotSame) with equal x and y
- Rectangle(Point, Point) stores deep copies — stored references ≠ passed-in references
- Rectangle(Rectangle) stores deep copies of inner Points
- Rectangle(int, int, int, int) stores correct x/y values

---

### Exercise 2 — Math Static Class

| Field | Value |
|---|---|
| Id / ExerciseId | `java-lld-03-math-static` |
| Title | `Static Class Members — Math Circle Area` |
| Difficulty | `Easy` |
| EstimatedMinutes | `15` |
| LessonSlug (or LessonId FK) | `03-oop2-encapsulation-inheritance` |
| ExternalResource (zip filename) | `exercises-lesson-03-ex2-math-static-class.zip` |
| Description / Scenario | `Implement class Math with a static double field PI set to 3.14, and a static public method getCircleArea(int radius) that returns PI * radius * radius as a double.` |
| Skills | `Static class-level members, class-level methods` |

**What the tests verify (MathTest.java):**
- PI is a static double field with value 3.14 (±0.0001)
- getCircleArea is static and returns double
- getCircleArea(5) returns 3.14 * 25 = 78.5
- getCircleArea(0) returns 0.0

---

### Exercise 3 — Person Constructor

| Field | Value |
|---|---|
| Id / ExerciseId | `java-lld-03-person-constructor` |
| Title | `Basic Constructor — Person Class` |
| Difficulty | `Easy` |
| EstimatedMinutes | `10` |
| LessonSlug (or LessonId FK) | `03-oop2-encapsulation-inheritance` |
| ExternalResource (zip filename) | `exercises-lesson-03-ex3-person-constructor.zip` |
| Description / Scenario | `Implement class Person in package com.assignment with int field age and String field name. Add a constructor Person(int age, String name) and getter methods getAge() and getName().` |
| Skills | `Constructor initialization, encapsulation, getters` |

**What the tests verify (PersonTest.java):**
- Person(30, "Bob") → getAge() = 30, getName() = "Bob"
- Person(22, "Charlie") → getAge() = 22, getName() = "Charlie"

---

## STEP 4 — UPDATE `app/src/data/lessonInteractions.js`

Add the following entry to the `lessonInteractions` object. The key is
`'java-spring-lld/oop-foundations/03-oop2-encapsulation-inheritance'`.

Paste this **exactly** (the JS was pre-authored in the lesson file — copy from the
`## lessonInteractions.js Entry` section there):

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

**HARD RULES for the lessonInteractions.js entry:**
- Copy the object above exactly. Do not reformat, do not add fields.
- NEVER add `initialSelectedOption` or `initialSubmitted` to any concept check object.
- Do NOT include `SOURCE_TYPE` as a data field — it belongs only in `.md` files as a marker.
- Do NOT change any existing entry in the file.

---

## STEP 5 — UPDATE `app/src/data/lessonExerciseAssociations.js`

Add this entry to `lessonExerciseAssociations`:

```js
'java-spring-lld/oop-foundations/03-oop2-encapsulation-inheritance': {
  exerciseId: 'java-lld-03-point-rectangle',
},
```

The `exerciseId` value `'java-lld-03-point-rectangle'` must match the Id of the Exercise record
you seeded in Step 3. This is what the `ImplementationExercise` component uses to fetch the exercise from the API.

Do NOT touch any existing entries.

---

## STEP 6 — CONSTRAINTS

Do NOT touch:
- Any other `case` in `GetAuthoredLessonContent` switch
- Any existing key in `lessonInteractions`
- Any existing entry in `lessonExerciseAssociations.js`
- Any CSS file, any other `.cs` file
- `BackfillLessonContent` or `NeedsLessonContent` methods
- The `getLessonInteractions` export at the bottom of `lessonInteractions.js`
- The `getLessonExerciseAssociation` export at the bottom of `lessonExerciseAssociations.js`

Match code style exactly:
- `JavaVerticalSeedData.cs`: C# verbatim strings, double-quote escaping, 4-space indent
- `lessonInteractions.js`: single quotes, 2-space indent, trailing comma on last property
- `lessonExerciseAssociations.js`: single quotes, 2-space indent, trailing comma

---

## STEP 7 — OUTPUT

Produce clearly labeled outputs:

### OUTPUT A: New case for `api/Data/JavaVerticalSeedData.cs`
Show only the new `case` block. Mark exactly where it goes (before `_ => null`).
Do NOT print the entire seed file.

### OUTPUT B: New Exercise seed blocks for `api/Data/JavaVerticalSeedData.cs`
Show only the three new Exercise record additions. Mark exactly where they go.
Do NOT print the entire seed file.

### OUTPUT C: Full updated `app/src/data/lessonInteractions.js`
Print the entire file. All existing entries unchanged, plus the new entry.

### OUTPUT D: Addition to `app/src/data/lessonExerciseAssociations.js`
Show only the new entry to add. Confirm `exerciseId` matches the Exercise record id from OUTPUT B.

### OUTPUT E: Architecture diagram decision
State: included or omitted, and one-sentence reason.

═══════════════════════════════════════════════
END OF PROMPT
═══════════════════════════════════════════════

---

## POST-INGESTION CHECKLIST

Run after applying all outputs:

- [ ] Pasted new `case` block into `GetAuthoredLessonContent` switch before `_ => null`
- [ ] Added three Exercise records to the seed data
- [ ] Replaced `lessonInteractions.js` with OUTPUT C (verified no existing entries changed)
- [ ] Added the lessonExerciseAssociations.js entry from OUTPUT D
- [ ] Ran: `docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api`
- [ ] Lesson page renders (not "being prepared" placeholder)
- [ ] Concept Check 01 is NOT pre-answered on load
- [ ] Concept Check 02 is NOT pre-answered on load
- [ ] Practice questions appear at bottom of page
- [ ] `ImplementationExercise` component appears (Point/Rectangle exercise — EX1)
- [ ] Exercise component fetches correctly (no 404 on the exercise API call)
- [ ] If content shows old content, force-reset and restart:
  ```
  docker exec -it studytracker-db psql -U studyuser -d studytracker \
    -c "UPDATE lessons SET content_body = '', content_status = 'Outline' WHERE slug = '03-oop2-encapsulation-inheritance';"
  docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
  ```

## ZIP FILE PREP (do before running the prompt)

The original Scaler ZIPs are solutions, not starters. Strip the solution files before deploying:

| Original ZIP | Rename to | Strip (remove solution files, keep tests + pom.xml) |
|---|---|---|
| `1773391164_3c2b63f8261a4a43.zip` | `exercises-lesson-03-ex1-point-rectangle-deep-copy.zip` | Remove Point.java and Rectangle.java from src/main/; add stub versions |
| `1773391167_9f935ce4ea5ba481.zip` | `exercises-lesson-03-ex2-math-static-class.zip` | Remove Math.java from src/main/; add stub version |
| `1773393119_09d9e2722a71ce5e.zip` | `exercises-lesson-03-ex3-person-constructor.zip` | Remove Person.java from src/main/com/assignment/; add stub version |

**Stub templates:**

`Point.java` starter:
```java
public class Point {
    int x;
    int y;

    // TODO: Implement constructor Point(int x, int y)

    // TODO: Implement copy constructor Point(Point p)
}
```

`Rectangle.java` starter:
```java
public class Rectangle {
    Point topLeft;
    Point bottomRight;

    // TODO: Implement constructor Rectangle(int topLeftX, int topLeftY, int bottomRightX, int bottomRightY)
    // Both Points must be created as NEW instances (deep copy)

    // TODO: Implement constructor Rectangle(Point topLeft, Point bottomRight)
    // Deep copy both Points using Point's copy constructor

    // TODO: Implement copy constructor Rectangle(Rectangle r)
    // Deep copy both inner Points from the source Rectangle
}
```

`Math.java` starter:
```java
public class Math {
    // TODO: Add a class-level (static) data member PI of type double, set to 3.14

    // TODO: Add a class-level (static) public method getCircleArea(int radius)
    //       that returns PI * radius * radius as a double
}
```

`Person.java` starter (in package com.assignment):
```java
package com.assignment;

public class Person {
    // TODO: Add data member age (int)
    // TODO: Add data member name (String)

    // TODO: Implement constructor Person(int age, String name)

    // TODO: Implement getAge() — returns the age
    // TODO: Implement getName() — returns the name
}
```
