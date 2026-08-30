# Prompt for Local LLM — Insert Pre-Written Additions Into Lessons 4–13

Paste everything below this line into the local LLM as-is. Every block of new content in
this file was already written by hand from the real Scaler source material — you are NOT
being asked to write new prose, invent examples, or paraphrase. Your job is purely
mechanical: insert each block at the exact location specified, and fix one syntax bug.
Do not summarize, skip, reorder, or improve the wording of any block below — copy it
verbatim into the C# verbatim string.

---

## 0. Fix this bug FIRST

File: `api/Data/JavaVerticalSeedData.cs`, case `"09-concurrency-4-semaphores"`.

Find this exact sentence (it currently breaks C# compilation because the quotes inside it
are not doubled):

```
A counting semaphore solves the **Capacity Problem** ("how many threads may enter"). It does NOT solve the **Mutation Problem** ("what happens when multiple threads touch the underlying `ArrayList` simultaneously"). If 3 producers enter and execute `items.add(item)` concurrently on a plain list, internal array pointers corrupt.
```

Replace it with (quotes doubled, everything else identical):

```
A counting semaphore solves the **Capacity Problem** (""how many threads may enter""). It does NOT solve the **Mutation Problem** (""what happens when multiple threads touch the underlying `ArrayList` simultaneously""). If 3 producers enter and execute `items.add(item)` concurrently on a plain list, internal array pointers corrupt.
```

Scan the rest of the file for any other single (non-doubled) `"` inside verbatim-string
content before proceeding — if you find one, fix it the same way and report it.

---

## 1. Lesson 4 — `04-oop-3-polymorphism-interfaces`

Insert the following as a new question **Q4** at the end of the existing
`## Self-Check (From Class Material)` section (after the current Q3, before the closing
`",`):

```
**Q4.** Consider the following classes:
```java
public class P {
  protected int d1 = 10;
  protected int d = 100;

  protected void fun1(){
    System.out.println("P's fun1");
  }
  protected void fun(){
    System.out.println("P's fun");
  }
  static protected void sfun(){
    System.out.println("P's sfun");
  }
}

public class C extends P {
  protected int d2 = 20;
  protected int d = 200;

  protected void fun2(){
    System.out.println("C's fun2");
  }
  protected void fun(){
    System.out.println("C's fun");
  }
  static protected void sfun(){
    System.out.println("C's sfun");
  }
}
```
If client code does `P obj = new C(); obj.display();` where `display()` prints `d1`, `d`,
then calls `fun1()`, `fun()`, `sfun()` — what is the output?
- A. Compile Time Error
- B. 10 100 P's fun1 C's fun P's sfun
- C. 100 100 P's fun1 C's fun P's sfun
- D. 10 10 P's fun1 C's fun P's sfun

**Answer: B** — Fields are never polymorphic in Java; `obj.d1` and `obj.d` resolve by the
*reference type* (`P`), so both read `P`'s fields (10, 100) regardless of the actual object
being a `C`. `fun1()` is not overridden in `C`, so it prints `P's fun1`. `fun()` **is**
overridden, and instance methods dispatch dynamically on the *actual object type* (`C`), so
it prints `C's fun`. `sfun()` is `static`, so it is hidden, not overridden — static calls
resolve at compile time by reference type (`P`), printing `P's sfun`.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 60; answer determined from source material, not marked in original)*
```

---

## 2. Lesson 5 — `05-oop-4-lms-lab`

### 2a. Insert into `## Concepts Covered`, as a new subsection right after the existing
"5. Polymorphic Execution Without `instanceof`" point and before `## Practical Backend
Scenario`:

```

**6. The Access Modifiers Table (Why Every LMS Field Is `private`):**
| Modifier | Same Class | Same Package | Subclass | Everywhere |
|----------|------------|--------------|----------|------------|
| `private` | yes | no | no | no |
| default | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

Every entity field in the LMS (`userId`, `borrowedBooksCount`, `isAvailable`) stays
`private`, with access only through public getters and controlled mutator methods. This is
why `Member.borrowedBooksCount` cannot be touched directly by `Book.lend()` — the two
classes are not in an inheritance relationship, so `protected` would not even help; the
field must go through `Member`'s own public methods.

**7. Why `Book.lend()` Never Calls `incrementBorrowCount()` Directly:**
`LibraryManagementSystem.lendBook()` delegates in two separate steps: first `book.lend(member)`,
then — only if that succeeded — `member.incrementBorrowCount()`. `Book.lend()` itself never
calls `incrementBorrowCount()`. This separation is deliberate: a `Book` should not need to
know how a `Member` tracks its own borrow count internally, and a `Member`'s counting logic
should not need to know how a `Book` decides availability. Each class stays responsible for
exactly one piece of state, and the orchestrator (`LibraryManagementSystem`) is the only
place that knows both steps must happen together.

**8. The IS-A Test for This Domain:**
Every inheritance relationship in the LMS should pass a simple intuition check: does
"Child IS-A Parent" read naturally as a sentence? "Member IS-A User" and "Librarian IS-A
User" both read naturally, confirming `extends` is the right tool. If a relationship does
not read naturally as IS-A, composition (a field reference) is the correct choice instead,
not inheritance.
```

### 2b. Insert into `## Practice Loop`, as a new step 6 (after the existing step 5, still
before `## Evidence of Understanding`):

```
6. Trace this exact sequence and predict how many `User` objects exist and how many unique
   IDs are generated:
   ```java
   Member asha = new Member("Asha", "asha@email.com");
   User copy = new Member(asha);
   System.out.println(asha.getUserId().equals(copy.getUserId()));
   ```
   (Two independent `Member` objects exist; the copy constructor must call
   `generateUniqueId()` rather than copying `asha`'s ID, so the printed result is `false`.)
```

---

## 3. Lesson 6 — `06-concurrency-1-threads`

Insert the following as a new subsection in `## Concepts Covered`, immediately after the
existing "Diagnostic Questions — Concurrency vs. Parallelism" bullet block and before
"**From Code to Process in Memory:**":

```

**Five Real-World Anchors for the Office Metaphor (from class):**
- **Process = browser tabs:** modern browsers run separate tabs in separate processes; one
  tab crashing does not take down the others, because each has its own isolated memory space.
- **Thread = a video game's internal workers:** one thread renders graphics, a second
  manages audio, a third reads controller input, and a fourth autosaves progress — all four
  share the same game state in memory but run independently.
- **CPU Scheduler = a web server under load:** when incoming requests outnumber the
  server's processing capacity, the scheduler decides execution order so no request starves
  while avoiding excessive switching overhead.
- **Context Switching = losing your place while studying:** pausing one subject to
  context-switch to another and back costs real time re-orienting yourself — time spent on
  logistics, not on the actual work. A CPU pays the same cost saving and restoring register
  state on every thread switch.
- **Runnable = handing off a written task:** a scheduled report defines *what* needs doing
  without specifying *which* employee performs it — exactly like handing a task description
  to whichever thread the scheduler assigns next.
```

---

## 4. Lesson 7 — `07-concurrency-2-executors`

Insert the following two questions as **Q4** and **Q5** at the end of the existing
`## Self-Check (From Class Material)` section:

```
**Q4.** Consider the following two statements:
1. Runnable interface is used to create classes that run on a separate thread and return values to the main thread.
2. Callable interface is used to create classes that run on a separate thread and don't need to return values to the main thread.
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both a and b are false

**Answer: D** — Both statements have it backwards: `Runnable.run()` returns `void` and
cannot return a value to the caller, while `Callable<V>.call()` is specifically designed to
return a typed value `V`. Neither statement correctly describes its interface.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 8; answer determined from source material, not marked in original)*

**Q5.** Consider the following two statements:
1. A class implementing Callable<Integer> will have a call function that returns integer
2. To get a value from a class implementing Callable<Integer>, we can use Future<Integer>
Which of the following is correct?
- A. Both a and b are true
- B. Only a is true
- C. Only b is true
- D. Both are false

**Answer: A** — `Callable<Integer>.call()` is declared to return `Integer`, and submitting
that `Callable` to an `ExecutorService` returns a `Future<Integer>` whose `.get()` retrieves
the computed value once ready.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 10; answer determined from source material, not marked in original)*
```

---

## 5. Lesson 8 — `08-concurrency-3-synchronization`

Insert the following two questions as **Q4** and **Q5** at the end of the existing
`## Self-Check (From Class Material)` section:

```
**Q4.** Which of the following is true regarding the differences between Hashtable and
ConcurrentHashMap in Java?
- A. Hashtable allows multiple threads to access different parts of the map at the same time, while ConcurrentHashMap does not.
- B. ConcurrentHashMap is synchronized, while Hashtable is not.
- C. Hashtable is synchronized, ConcurrentHashMap is not.
- D. ConcurrentHashMap allows multiple threads to access different parts of the map at the same time, while Hashtable does not.

**Answer: D** — `Hashtable` synchronizes on the entire map for every operation, allowing
only one thread in at a time. `ConcurrentHashMap` uses finer-grained internal locking
(segment/bucket-level), letting multiple threads operate on different parts of the map
concurrently.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 5; answer determined from source material, not marked in original)*

**Q5.** Consider the following class:
```java
public class A {
  synchronized static void fun1(){}
  synchronized void fun2(){}
  void fun3(){}
}
```
And client code creating `A obj1 = new A();` and `A obj2 = new A();`. Which pair of calls
CANNOT execute concurrently?
- A. obj1.fun1() and obj1.fun2()
- B. obj1.fun1() and obj2.fun1()
- C. obj2.fun2() and obj2.fun3()
- D. obj1.fun2() and obj2.fun2()

**Answer: B** — `fun1()` is `static synchronized`, so it locks the shared `Class` object
(`A.class`), not any particular instance. Both `obj1.fun1()` and `obj2.fun1()` compete for
that one class-level lock regardless of which instance calls it, so they cannot run
concurrently. `fun2()` is an instance-level lock, so different instances (`obj1`/`obj2`)
calling it are unaffected by each other.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 2; answer determined from source material, not marked in original)*
```

---

## 6. Lesson 9 — `09-concurrency-4-semaphores`

Insert the following two questions as **Q4** and **Q5** at the end of the existing
`## Self-Check (From Class Material)` section:

```
**Q4.** Which of the following methods in a Semaphore is a blocking method?
- A. acquire
- B. release
- C. Both acquire and release
- D. Neither acquire nor release

**Answer: A** — `acquire()` blocks the calling thread if no permits are currently
available, waiting until one is released. `release()` never blocks — it simply increments
the permit count and returns immediately.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 3; answer determined from source material, not marked in original)*

**Q5.** Which of the following is true about the critical section of a correctly working
producer-consumer problem using two semaphores (a producer semaphore tracking empty slots,
a consumer semaphore tracking filled slots)?
- A. Critical section of producer should begin with acquire on producer semaphore and end with release on consumer semaphore
- B. Critical section of producer should begin with acquire on producer semaphore and end with release on producer semaphore
- C. Critical section of consumer should begin with acquire on producer semaphore and end with release on consumer semaphore
- D. Critical section of consumer should begin with acquire on consumer semaphore and end with release on consumer semaphore

**Answer: A** — A producer must first `acquire()` an empty slot (the producer semaphore),
then after producing, `release()` the consumer semaphore to signal that a new item is
available. Signaling the *other* semaphore, not your own, is what lets the two sides
coordinate.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 7; answer determined from source material, not marked in original)*
```

---

## 7. Lesson 10 — `10-java-adv-1-generics`

Insert the following two questions as **Q4** and **Q5** at the end of the existing
`## Self-Check (From Class Material)` section:

```
**Q4.** When is it appropriate to use wildcards with an upper bound in Java generics?
- A. To allow any type as a method parameter
- B. When the method should work with specific subclasses (i.e. read values as that common supertype)
- C. When the method should work with any object type
- D. To specify a lower limit on the allowed types

**Answer: B** — An upper-bounded wildcard (`? extends T`) is used when a method needs to
*read* elements that are guaranteed to be `T` or some subtype of `T`, matching the PECS
"Producer extends" rule.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/12-22.md, MCQ 10; answer determined from source material, not marked in original)*

**Q5.** What does the `extends` keyword signify in the context of Java generics (e.g.
`<T extends Number>`)?
- A. It specifies a lower bound for a type parameter.
- B. It restricts the use of wildcard types.
- C. It indicates inheritance for a generic class.
- D. It denotes an upper bound for a type parameter.

**Answer: D** — In a generic type-parameter declaration, `extends` denotes an upper bound:
`T` must be that type or a subtype of it. This is distinct from wildcard usage but relies on
the same "extends = upper bound" idea.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/56-66.md, MCQ 59; answer determined from source material, not marked in original)*
```

---

## 8. Lesson 11 — `11-java-adv-2-collections-lab`

Insert the following two questions as **Q4** and **Q5** at the end of the existing
`## Self-Check (From Class Material)` section:

```
**Q4.** Which of the following is thread-safe?
- A. ArrayList
- B. HashMap
- C. Hashtable
- D. LinkedList

**Answer: C** — `Hashtable` synchronizes every method internally, making it thread-safe
(though coarse-grained and slower under contention). `ArrayList`, `HashMap`, and
`LinkedList` are all unsynchronized by default.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 46; answer determined from source material, not marked in original)*

**Q5.** Which of the following classes doesn't implement the `List` interface (directly or
indirectly)?
- A. Vector
- B. Stack
- C. ArrayList
- D. PriorityQueue

**Answer: D** — `Vector`, `Stack` (which extends `Vector`), and `ArrayList` all implement
`List`. `PriorityQueue` implements the `Queue` interface instead — it is backed by a binary
heap and does not offer indexed `List` access.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 5; answer determined from source material, not marked in original)*
```

---

## 9. Lesson 12 — `12-java-adv-3-lambdas-streams`

Insert the following two questions as **Q4** and **Q5** at the end of the existing
`## Self-Check (From Class Material)` section:

```
**Q4.** What does the following code snippet do?
```java
Set<String> uniqueFruits = fruits.stream()
  .collect(Collectors.toSet());
System.out.println("Result: " + uniqueFruits);
```
- A. Removes duplicate fruits from the list.
- B. Creates a set of all fruit names.
- C. Concatenates all fruits into a single string.
- D. Compile Error.

**Answer: B** — `Collectors.toSet()` collects the stream elements into a `Set<String>`.
Deduplication is a natural consequence of the `Set` contract, but the collector's direct
action is building that set, not "removing duplicates" as a separate step.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 8; answer determined from source material, not marked in original)*

**Q5.** Which of the following comparators will sort a list of strings in descending order
according to length?
- A. `Comparator<String> c = (s1, s2) -> Integer.compare(s2.length(), s1.length());`
- B. `Comparator<String> c = (s1, s2) -> s2.length() - s1.length();`
- C. `Comparator<String> c = Comparator.comparingInt(String::length).reversed();`
- D. All of the above

**Answer: D** — All three are valid, equivalent ways of expressing a descending-by-length
comparator: two hand-written lambda forms (integer subtraction and `Integer.compare` for
overflow safety) and one built from the fluent `Comparator.comparingInt(...).reversed()`
API.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/23-33.md, MCQ 8; answer determined from source material, not marked in original)*
```

---

## 10. Lesson 13 — `13-java-adv-4-streams-exceptions`

Insert the following two questions as **Q4** and **Q5** at the end of the existing
`## Self-Check (From Class Material)` section:

```
**Q4.** What is the output of the following code?
```java
IntFunction<Integer> square = x -> x * x;
System.out.println(square.apply(5));

BinaryOperator<Integer> addition = (x, y) -> x + y;
System.out.println(addition.apply(10, 20));

Function<Integer, Integer> increment = x -> x + 1;
System.out.println(increment.apply(7));
```
- A. 25 30 8
- B. 25 30 7
- C. 5 30 7
- D. Compile Error

**Answer: A** — `square.apply(5)` computes $5 \times 5 = 25$; `addition.apply(10, 20)`
computes $10 + 20 = 30$; `increment.apply(7)` computes $7 + 1 = 8$.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/01-11.md, MCQ 10; answer determined from source material, not marked in original)*

**Q5.** Which of the following is NOT a way of creating a stream?
- A. `Stream.of()`
- B. `list.stream()`
- C. `Stream.iterate()`
- D. `stream.collect()`

**Answer: D** — `Stream.of()`, `list.stream()`, and `Stream.iterate()` all *create* a
stream. `collect()` is a terminal operation that *consumes* an existing stream and produces
a result — it does not create a new stream.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/67-77.md, MCQ 6; answer determined from source material, not marked in original)*
```

---

## 11. What must NOT change

- Do not touch any other part of any of the 10 lessons beyond the exact insertions above.
- Do not touch lessons `01`–`03` or `14`+.
- Do not renumber existing Q1/Q2/Q3 questions — your new questions are strictly appended as
  Q4 (and Q5 where given).
- Every inserted block already uses correct C# verbatim-string quote escaping (`""` for a
  literal `"`) — copy it exactly as given, character for character.
- Do not add a `SOURCE_TYPE` citation that isn't given above, and do not invent a different
  answer than the one given — these answers were worked out from the actual question logic,
  not guessed.

## 12. Output format

Output the complete, updated `GetAuthoredLessonContent` method body, same as before, ready
to paste over the existing method in `api/Data/JavaVerticalSeedData.cs`.

After the code block, report:
- Confirmation the Lesson 9 quote-escaping bug was fixed.
- One line per lesson confirming which insertions landed and the new approximate word count.
- Any insertion you could not place exactly as specified, and why.

## 13. Self-check before you output

1. The Lesson 9 escaping bug is fixed — search for any remaining single (non-doubled) `"`
   inside the 10 lessons' content before finishing.
2. Lesson 4 has 4 self-check questions now (was 3). Lessons 6 and 5 keep their original
   count plus the prose insertions described. Lessons 7–13 each have 5 self-check questions
   now (was 3, plus 2 new).
3. No existing content was deleted, reworded, or reordered — only new material was added at
   the specified points.
4. Every new MCQ's `SOURCE_TYPE` citation matches exactly what was given above — you did
   not renumber or reassign these.

## 14. Operational note for the human running this (same as before)

The lessons already have `ContentBody` containing the guard headings, so before restarting
the API, reset these 10 lessons in the database again:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '04-oop-3-polymorphism-interfaces',
  '05-oop-4-lms-lab',
  '06-concurrency-1-threads',
  '07-concurrency-2-executors',
  '08-concurrency-3-synchronization',
  '09-concurrency-4-semaphores',
  '10-java-adv-1-generics',
  '11-java-adv-2-collections-lab',
  '12-java-adv-3-lambdas-streams',
  '13-java-adv-4-streams-exceptions'
);
```

Then rebuild/restart the API so `BackfillLessonContent` re-applies the updated content.
