Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/SJXV0p4EGe

# Post-Reads-Java-Advanced-3.md - Complete Content

| POST-READ | Java Advanced Concepts | Java Advanced Concepts-3 — Streams & Lambdas |
|-----------|-------------------------|-----------------------------------------------| 

This document consolidates the material covered in the session. Each section states the relevant definition, walks through the Java code built live in class, and closes with the pitfalls most commonly associated with that concept. This is the third session of the Java Advanced Concepts series and builds directly on the `Comparable` and `Comparator` implementations written in the previous session's lab.

## Section 1: Functional Interfaces

### Definition

A **functional interface** is an interface that declares exactly one abstract method. This is also referred to as a **SAM interface** — Single Abstract Method. `Runnable` (`run()`), `Callable` (`call()`), `Comparable` (`compareTo()`), and `Comparator` (`compare()`) — all used in earlier sessions — are each functional interfaces. An interface with more than one method is not a functional interface. The `Stack` interface built in an earlier session, which declared both `push` and `pop`, is one such example.

### Hidden Pitfalls

- **Assuming every Java interface is a functional interface.** Only interfaces with exactly one abstract method qualify. An interface with two or more methods cannot be implemented using a lambda expression, as demonstrated in Section 2.

---

## Section 2: Lambda Expressions

### Deep-Dive Theory

Prior to lambda expressions, implementing a functional interface required either a separate named class or an anonymous class. Both approaches require boilerplate — a class declaration, an `@Override` annotation, and a method signature — to express what is often a single line of actual logic. Consider the task of printing "Hello World" from a separate thread. A named-class implementation of `Runnable` requires an entire additional file:

```java
// Task.java
public class Task implements Runnable {
    @Override
    public void run() {
        System.out.println("Hello World");
    }
}
```

```java
// LambdasClient.java
public class LambdasClient {
    public static void main(String[] args) {
        Task task = new Task();
        Thread t = new Thread(task);
        t.start();
    }
}
```

An anonymous class removes the separate file but retains the same ceremony inline:

```java
Runnable task = new Runnable() {
    @Override
    public void run() {
        System.out.println("Hello World");
    }
};
Thread t = new Thread(task);
t.start();
```

Of the code above, only `System.out.println("Hello World")` is actual business logic. `new Runnable()`, `@Override`, and `public void run()` are boilerplate — required by Java's syntax, but expressing no decision of the developer's own.

**Definition to note formally:** A **lambda expression** is a concise way of writing the implementation of a functional interface's single method, without declaring a separate class or an anonymous class. Its general syntax is:

```java
(parameter1, parameter2, ...) -> { // method body }
```

A lambda expression specifies no access modifier, no return type, and no method name. Java determines all of this from the functional interface the lambda is being assigned to. This is why a lambda expression can only be used where a functional interface is expected — it is not new functionality, but syntactic sugar over the anonymous-class pattern above; anything expressible as a lambda was already expressible using a named or anonymous class.

### Practical Mechanics

`Runnable.run()` takes no arguments, so the parameter list is empty:

```java
public class LambdasClient {
    public static void main(String[] args) {
        Runnable task = () -> { System.out.println("Hello World"); };
        Thread t = new Thread(task);
        t.start();
    }
}
```

Where `()` matches `run()`'s empty parameter list, `->` reads as "implement it like this," and `{ ... }` is the method body. Once the body is a single statement, the braces may be dropped:

```java
Runnable task = () -> System.out.println("Hello World");
```

This compact form is the style most commonly seen in production code once the lambda body is a single line. It is also common to hand the lambda directly to a constructor or method without an intermediate variable at all:

```java
Thread t = new Thread(() -> System.out.println("Running in a new thread"));
t.start();
```

**Why Java is not confused about which method a lambda implements:** because a functional interface has exactly one method, there is no ambiguity about which method the lambda body is implementing. This breaks down immediately on an interface with two methods:

```java
interface Test {
    void run();
    void stop();
}
Test t = () -> System.out.println("hi"); // compile error
```

With two candidate methods, Java has no way of resolving which one the lambda is meant to implement, and the code above does not compile. This is precisely why lambda expressions are restricted to functional interfaces.

**Applying a lambda to `Comparator`:** the same pattern applies to any functional interface, not just `Runnable`. Consider sorting a list of integers so that even numbers appear before odd numbers, with both groups sorted in descending order:

```java
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;

public class LambdasClient {
    public static void main(String[] args) {
        List<Integer> l = new ArrayList<>();
        l.add(12);
        l.add(13);
        l.add(46);
        l.add(5);
        Collections.sort(l, (a, b) -> {
            if (a % 2 == b % 2) {
                return b - a;
            } else if (a % 2 == 0) {
                return -1;
            } else {
                return 1;
            }
        });
    }
}
```

When both numbers share the same parity, the comparator falls back to descending order (`b - a`). When parity differs, the even number is placed first by returning `-1`. This is the same `Comparator` logic pattern used in the previous session's lab, now written without a separate class or an `implements Comparator` declaration.

### Hidden Pitfalls

- **Attempting to use a lambda on an interface with more than one abstract method.** This does not compile, since Java cannot determine which method the lambda body is meant to implement.
- **Treating a lambda as introducing new capability.** A lambda expression achieves nothing that a named or anonymous class implementation could not already achieve; its only advantage is conciseness.
- **Assuming a lambda always needs to be stored in a variable.** In practice, most lambdas are written directly at the call site — for example, passed straight into a `Thread` constructor — rather than assigned to an intermediate variable first.

---

## Section 3: Design Judgment — When Not to Use a Lambda

### Deep-Dive Theory

Lambda expressions are best suited to short, single-use logic. If the same logic is required in multiple places across a codebase, a lambda is the wrong tool: a lambda cannot be reused outside the location it is written in, and copying the same lambda body into several files creates a maintenance burden identical to duplicating any other piece of logic. Representative production scenarios where a named class remains the correct choice:

- A `Comparator` used for sorting the same entity across multiple REST endpoints — written once as a named class such as `ItemPriceComparator`, rather than repeated as a lambda in every controller.
- A validation rule, such as validating an email address or phone number, used across multiple services — written as a named, independently testable class rather than embedded as a lambda inside one method.
- Any business rule shared by more than one module of an application, for the same underlying reason.

### Hidden Pitfalls

- **Defaulting to a lambda purely because it is shorter to write.** Conciseness is a benefit only when the logic is genuinely local to one call site; reused logic belongs in a named, testable class regardless of how short it is.

---

## Section 4: The Streams API — Thinking in Pipelines

### Deep-Dive Theory

Introduced in Java 8, the **Streams API** provides a set of ready-made methods for processing collections of data, reducing the need to write loops by hand. A stream can be understood as a pipeline: data enters at one end, passes through a series of processing stages, each performing one specific transformation, and a final result emerges at the other end — comparable to a refinery, where crude oil enters, passes through a sequence of processing tanks, and refined output emerges. A few characteristics worth noting:

- A stream, by default, is single-threaded, not parallel.
- Depending on the type of operation, a stream is evaluated either lazily or eagerly — covered in Section 8.
- Java also provides `.parallelStream()`, which distributes work across multiple cores. This is only appropriate when each element's processing is genuinely independent of the others, and is covered in the extra material at the end of this document, since it was not part of the live session.

### Practical Mechanics — The Problem Without Streams

Consider the task of taking a list of integers, retaining only the even numbers, sorting them, squaring each one, and removing duplicates:

```java
List<Integer> numbers = Arrays.asList(5, 3, 8, 2, 9, 4, 7, 6, 2, 8);
List<Integer> evens = new ArrayList<>();
for (int n : numbers) {
    if (n % 2 == 0) {
        evens.add(n);
    }
}
Collections.sort(evens);
List<Integer> result = new ArrayList<>();
for (int n : evens) {
    int squared = n * n;
    if (!result.contains(squared)) {
        result.add(squared);
    }
}
```

Two aspects of this code are worth noting explicitly: two temporary lists exist purely to hold intermediate state, and `contains()` re-scans the entire `result` list on every call, which is inefficient. The underlying intent — "even numbers, squared, unique, sorted" — is a single sentence, yet the loop-based version requires ten lines and two throwaway lists to express it.

### Practical Mechanics — The Stream Pipeline

```java
List<Integer> result = numbers.stream()
    .filter(n -> n % 2 == 0)
    .sorted()
    .map(n -> n * n)
    .distinct()
    .collect(Collectors.toList());
System.out.println(result);
```

This produces the identical outcome as the loop-based version, with one line per logical step and no temporary lists. The **stream lifecycle** consists of three parts:

- **Create** the stream — `list.stream()`.
- **Apply operations** on it — filtering, mapping, sorting, and so on.
- **Collect the output** — via `collect()`, or another terminal operation such as `forEach()`.

Building the pipeline up incrementally clarifies what each stage contributes:

```java
numbers.stream()
    // connects a stream to the list; nothing happens yet
    .filter(n -> n % 2 == 0)
    // only even numbers now pass through
    .sorted()
    // sorted into natural order
    .map(n -> n * n)
    // each surviving number is squared
    .distinct()
    // duplicates removed
    .collect(Collectors.toList());
    // finally collected into a List
```

### Hidden Pitfalls

- **Assuming a stream pipeline executes as it is written, top to bottom, all at once.** As covered in Section 8, a stream does not process any element until a terminal operation is invoked; the pipeline is only a description of work until that point.
- **Reaching for a manual loop out of habit when a stream pipeline would be clearer and shorter.** This is precisely the pattern the Streams API was introduced to replace.

---

## Section 5: `filter()`, `map()`, and `Predicate`

### Deep-Dive Theory

`filter()` and `map()` serve fundamentally different purposes and should not be confused: `filter()` removes elements based on a condition, while `map()` transforms every element that passes through — it never removes anything. `filter()` accepts a `Predicate<T>` — a functional interface with a single method, `boolean test(T t)`. It is nothing more than a condition, returning `true` for elements that should be kept and `false` for elements that should be discarded.

```java
Predicate<Integer> isEven = n -> n % 2 == 0;
```

Whatever lambda is passed into `filter()` is treated internally by Java as the implementation of `Predicate`'s `test()` method — the same mechanism covered in Section 2, applied to a different functional interface.

### Practical Mechanics

```java
numbers.stream().filter(n -> n % 2 == 0);
// retains only even numbers
numbers.stream().map(n -> n * n);
// squares every element, removes nothing
```

Inspecting the declaration of `filter()` shows that it accepts a `Predicate` and returns a `Stream`, which is precisely what allows further methods to be chained after it.

### Hidden Pitfalls

- **Confusing `filter()` with `map()`.** `filter()` can shrink the number of elements in the stream; `map()` never changes the element count, only the value of each element.
- **Expecting `filter()`'s internal mechanics to run immediately.** As with all intermediate operations, nothing actually executes at the point `filter()` is called — this is explored fully in Section 8.

---

## Section 6: `distinct()` and `sorted()`

### Deep-Dive Theory

`.distinct()` retains only unique elements from the stream. Like `filter()` and `map()`, it is an intermediate operation and does not close the stream. `.sorted()` orders elements according to their natural ordering by default, but can also accept a `Comparator` for a custom order:

```java
numbers.stream().sorted((a, b) -> b - a);
// descending order
```

### Hidden Pitfalls

- **Attempting to chain two terminal operations one after another.** This is not possible: the first terminal operation closes the stream, leaving nothing for a second terminal operation to act on. Section 7 covers stream closure in detail.

---

## Section 7: Intermediate vs. Terminal Operations

### Deep-Dive Theory

Every stream operation belongs to one of two categories. **Intermediate operations** — `filter`, `map`, `sorted`, `distinct` — return a `Stream`, allowing further operations to be chained, and do not execute immediately. **Terminal operations** — `collect`, `forEach`, `findAny`, `findFirst` — produce an actual result and close the stream in the process.

| Type | Examples | Behaviour |
|------|----------|-----------|
| Intermediate | `filter`, `map`, `sorted`, `distinct` | Returns a `Stream`; lazy — nothing runs yet |
| Terminal | `collect`, `forEach`, `findAny`, `findFirst` | Returns a real result; closes the stream |

`collect()` is a terminal operation that gathers whatever remains in the stream into a specified container — a `List`, a `Set`, and so on — comparable to the final collection tank at the end of a refinery pipeline. Another terminal operation, `reduce()`, exists for aggregating a stream into a single combined value, and is covered in full in the next session.

### Practical Mechanics — Stream Closure

A stream cannot be reused once a terminal operation has been called on it:

```java
Stream<Integer> stream = numbers.stream();
stream.forEach(System.out::println);
// runs fine
stream.forEach(System.out::println);
// IllegalStateException
```

The second call fails with `IllegalStateException: stream has already been operated upon or closed`. Every terminal operation closes the stream it is called on; a fresh stream must be created with a new call to `.stream()` in order to process the same data again.

### Hidden Pitfalls

- **Reusing a stream reference after a terminal operation has been invoked on it.** This throws `IllegalStateException` at runtime; the fix is to call `.stream()` again, which is inexpensive to do.
- **Assuming an intermediate operation is executing meaningful work at the moment it appears in code.** Intermediate operations are classified as lazy for precisely this reason, detailed in Section 8.

---

## Section 8: `Optional` and `findAny()`

### Deep-Dive Theory

```java
Optional<Integer> result = numbers.stream()
    .filter(n -> n > 100)
    .findAny();
```

If no element in the stream satisfies the filter condition, `findAny()` must return something meaningful in place of a matching value. Returning `null` directly would defer the discovery of this problem to wherever the result is eventually used — potentially far from where the absence actually originated, making the resulting failure difficult to trace.

**Definition:** `Optional` is a container for a value that may or may not be present. It forces the caller to check for absence at the point the value is received, rather than allowing that check to be skipped and the gap to surface later as an unrelated failure. Internally, `Optional` is a simple class wrapping a single value field, with methods such as `isPresent()` and `get()` reading essentially as ordinary null-checks underneath — there is no special mechanism beyond what a manual null-check would already provide; the value lies in making that check explicit and difficult to skip.

### Hidden Pitfalls

- **Calling `.get()` on an `Optional` without first checking `isPresent()`.** This defeats the purpose of `Optional` entirely and throws `NoSuchElementException` if the value is absent — functionally equivalent to the `NullPointerException` `Optional` is meant to help avoid.
- **Treating `Optional` as eliminating the possibility of absence, rather than making it explicit.** `Optional` does not prevent a value from being missing; it forces the missing case to be acknowledged at the point of retrieval.

---

## Section 9: Lazy vs. Eager Evaluation

### Deep-Dive Theory

Intermediate stream operations are **lazily evaluated**: none of them execute the moment they are written. Instead, Java records each operation and defers all actual work until a **terminal operation** is called and a result is genuinely required. Terminal operations are **eagerly evaluated** — they run immediately once invoked. An intermediate operation can be thought of as a set of instructions handed to someone who will only act on them once a final request for the result actually arrives; the instructions are noted down but not executed until that point, and once the request does arrive, only the work actually necessary to satisfy it is performed.

### Practical Mechanics — Short-Circuiting

```java
Optional<Integer> result = numbers.stream()
    .filter(n -> {
        System.out.println("Checking: " + n);
        return n % 2 == 0;
    })
    .findAny();
```

Running this prints `"Checking: "` only up to the point where the first even number is found — not for every element in the list. This early exit is called **short-circuiting**: since `findAny()` only ever needs one matching result, the pipeline stops pulling further elements the moment that one result is available.

**Laziness does not mean less work is always done — it means exactly as much work as the terminal operation requires is done.** Replacing `findAny()` with a terminal operation that genuinely needs every matching element removes the early exit:

```java
List<Integer> result = numbers.stream()
    .filter(n -> {
        System.out.println("Checking: " + n);
        return n % 2 == 0;
    })
    .collect(Collectors.toList());
```

Here, printing occurs for every element, since `collect()` requires the complete set of matches, leaving nothing to short-circuit on.

**`sorted()` breaks short-circuiting.** Adding `.sorted()` before `.findAny()` forces a full pass over the entire input, even though `findAny()` still only needs one result:

```java
Optional<Integer> result = numbers.stream()
    .filter(n -> {
        System.out.println("Checking: " + n);
        return n % 2 == 0;
    })
    .sorted()
    .findAny();
```

This happens because `sorted()` cannot determine the correct order of any element until it has examined the entire stream, and is therefore forced to make a full pass regardless of what the terminal operation actually needs downstream.

### Naming the Terms

- **Terminal operations** are eagerly evaluated — they execute the instant they are called.
- **Intermediate operations** are lazily evaluated — they execute only once a terminal operation demands the result.

### Hidden Pitfalls

- **Assuming all lazy pipelines process less data than an eager equivalent.** Laziness guarantees "no more work than necessary," not "always minimal work" — a terminal operation that genuinely needs all elements will still cause the full stream to be processed.
- **Placing `sorted()` before a short-circuiting terminal operation without recognizing the cost.** `sorted()` requires the entire stream to be materialized before it can produce any output, silently removing any early-exit benefit that would otherwise apply.

---

## Section 10: Introduction to Exceptions

### Deep-Dive Theory

An **exception** is an unwanted and unexpected event that disrupts the normal flow of a program's execution at runtime. Java maintains a dedicated mechanism for exceptions, rather than allowing a program to fail silently, because an exception communicates precisely what went wrong and halts execution at the exact point of failure, rather than allowing execution to continue on data that is already known to be invalid.

### Compile-Time Errors vs. Runtime Exceptions

A compile-time error — such as a missing bracket — is caught by the compiler before the program ever runs. A runtime exception, by contrast, only becomes visible once the program is actually executing, because the compiler has no way of knowing the state of an object while the program runs. Reusing an already-closed stream, covered in Section 7, is an example: this failure could not have been caught at compile time, since it depends entirely on the runtime sequence of calls made on that particular object.

### An Analogy — the Escalation Chain

An unhandled exception behaves much like an unresolved workplace issue: if the immediate point of contact does not act on it, the issue does not disappear but escalates further up the chain, eventually reaching the highest level if nothing intervenes. An unhandled exception similarly keeps moving up the call chain until something catches it, or it reaches the top of the program and terminates it.

### Hidden Pitfalls

- **Treating "exception" as synonymous with "bug."** An exception is a structured signal that something went wrong at a specific point; the code that raises or fails to handle it correctly may or may not itself contain the underlying bug.

---

## Section 11: Exception Hierarchy, and Checked vs. Unchecked Exceptions

### Deep-Dive Theory

Every exception in Java derives from a common hierarchy:

```text
Throwable
|-- Error (fatal, not covered in this session)
|-- Exception
|-- RuntimeException (UNCHECKED)
| |-- NullPointerException
| |-- ArithmeticException
| |-- IllegalStateException
| |-- ArrayIndexOutOfBoundsException
|-- (everything else) (CHECKED)
|-- IOException -> FileNotFoundException
|-- SQLException
```

The distinction between **checked** and **unchecked** exceptions depends on where the fault genuinely lies. `NullPointerException`, `ArithmeticException`, `IllegalStateException`, and `ArrayIndexOutOfBoundsException` are all logic errors — each is preventable by writing correct code, and none should typically be handled explicitly; the correct response is to fix the line of code causing them, not to catch them. `SQLException`, `FileNotFoundException`, and `IOException`, by contrast, represent genuine external risks outside a developer's control — a database going down, a file being deleted externally, a network dropping. Java compels these to be addressed, either through a try-catch block or by declaring them with `throws`.

| Feature | Checked | Unchecked |
|---|---|---|
| Compiler handling | Must handle (`try`-`catch`) or declare (`throws`) | No mandatory handling |
| Cause | External (I/O, network) | Logic errors |
| Examples | `IOException`, `SQLException` | `NullPointerException`, `ArithmeticException` |
| What to do about it | Always handle | Fix the underlying logic instead |
| Inheritance | Extends `Exception` | Extends `RuntimeException` |

### Hidden Pitfalls

- **Explicitly catching an exception that should instead be prevented in code.** If a `NullPointerException` is anticipated at a particular line, the correct response is to fix that line, not to wrap it in a `try`-`catch`.
- **Assuming Java enforces handling uniformly across all exception types.** Only checked exceptions carry this requirement; unchecked exceptions compile without any handling at all, by design.

---

## Section 12: `throw`, Propagation, and try-catch Ordering

### Deep-Dive Theory — Raising an Exception Manually

The `throw` keyword raises an exception explicitly:

```java
public class ExceptionDemo {
    static void find(int x) {
        if (x % 5 == 0) {
            throw new NullPointerException();
        } else if (x % 3 == 0) {
            throw new ArithmeticException();
        }
    }
}
```

Calling `find(5)` from `main()` without a surrounding `try`-`catch` causes the program to crash, since both exceptions above are unchecked. Substituting a checked exception changes this behaviour entirely:

```java
static void find(int x) {
    if (x % 5 == 0) {
        throw new SQLException();
        // compile error here
    }
}
```

This produces a compile-time error — `unreported exception, must be caught or declared to be thrown` — because `SQLException` represents something a developer genuinely cannot prevent, and Java requires that the caller be made explicitly aware this can happen. Extending this requirement to unchecked exceptions would allow poorly written code to hide behind a declaration instead of being fixed at the source.

### Practical Mechanics — Propagation Across Layers

An unhandled checked exception propagates upward through the call chain until a layer decides to handle it:

```java
// Layer 1 — the actual risky call
void find(int x) throws SQLException {
    if (x % 5 == 0)
        throw new SQLException();
}
```

```java
// Layer 2 — doesn't know how to handle it either, passes it up
void doSomething(int x) throws SQLException {
    find(x);
}
```

```java
// Layer 3 — main knows what to do, so it catches it here
public static void main(String[] args) {
    try {
        doSomething(5);
    } catch (SQLException e) {
        System.out.println("Retry the DB call, or log and move on.");
    }
}
```

`find()` cannot itself resolve a database failure, so it declares `throws` and allows the exception to pass upward. `doSomething()` similarly has no way to resolve it and simply passes it further up. `main()` is where the decision of what to actually do — retry, log, or otherwise respond — is finally made. Catching an exception does not require fully resolving the underlying problem; logging it and re-throwing is an equally valid response.

### Practical Mechanics — try-catch Ordering

Multiple `catch` blocks must be ordered from most specific to most general:

```java
try {
    FileReader reader = new FileReader("data.txt");
} catch (Exception e) {
    // general exception first
    System.out.println("General error");
} catch (FileNotFoundException e) {
    // compile error: unreachable code
    System.out.println("File not found");
}
```

Placing the general `catch (Exception e)` before the more specific `catch (FileNotFoundException e)` produces a compile-time error, since the specific block becomes unreachable — every `FileNotFoundException` would already have matched the preceding, broader `Exception` clause. The correct ordering places the most specific exception type first:

```java
try {
    FileReader reader = new FileReader("data.txt");
} catch (FileNotFoundException e) {
    System.out.println("File not found");
} catch (Exception e) {
    System.out.println("General error");
}
```

### Hidden Pitfalls

- **Declaring `throws` on an unchecked exception out of habit.** This compiles without issue but is unnecessary and misleading, since Java does not require unchecked exceptions to be declared or handled.
- **Ordering `catch` blocks from general to specific.** This produces a compile-time "unreachable code" error; `catch` blocks must always be ordered from most specific to most general.
- **Treating "catching" an exception as equivalent to "resolving" it.** A `catch` block that only logs an error and allows the program to continue on invalid data is often a more serious problem than the original exception, since it silently masks the failure instead of surfacing it.

---

## Section 13: Common Pitfalls Summary

```text
1. Using a lambda on an interface with more than one abstract method
   -> does not compile; lambdas are only valid for functional interfaces 
      with exactly one abstract method.
2. Reusing a stream after a terminal operation has been called on it
   -> throws IllegalStateException at runtime; call .stream() again 
      to obtain a fresh stream.
3. Assuming sorted() preserves the short-circuiting behaviour of a 
   terminal operation like findAny()
   -> sorted() must consume the entire stream before producing any output, 
      forcing a full pass regardless of what the terminal operation actually needs.
4. Calling Optional.get() without checking isPresent() first
   -> throws NoSuchElementException if the value is absent, defeating 
      the purpose of using Optional in the first place.
5. Explicitly catching an unchecked exception instead of fixing the 
   logic that causes it
   -> masks a preventable bug instead of resolving it at the source.
6. Ordering catch blocks from general to specific
   -> produces a compile-time "unreachable code" error; the most specific 
      exception type must always be caught first.
```

### Hidden Pitfalls

- **Treating a compiling program as a correct one.** As in earlier sessions, several of the issues above — reused streams, unchecked `Optional` access, masked unchecked exceptions — compile without error and only surface as runtime failures or design defects.
- **Conflating "lazy" with "does nothing."** A lazy operation still executes fully when required; laziness only concerns *when* the work happens, not *whether* it happens.

---

## Section 14: Key Terminology

| Term | Definition |
|------|-----------|
| **Functional interface** | An interface declaring exactly one abstract method; also called a SAM interface |
| **Lambda expression** | A concise, syntax-sugar implementation of a functional interface's single method |
| **Stream** | A sequence of elements supporting pipeline-style processing through chained operations |
| **Intermediate operation** | A stream operation that returns a `Stream` and is evaluated lazily (e.g. `filter`, `map`, `sorted`, `distinct`) |
| **Terminal operation** | A stream operation that produces a final result, evaluated eagerly, and closes the stream (e.g. `collect`, `forEach`, `findAny`) |
| **`Predicate<T>`** | A functional interface with a single `boolean test(T t)` method, used as the condition passed to `filter()` |
| **`Optional`** | A container representing a value that may or may not be present, forcing an explicit check at the point of retrieval |
| **Short-circuiting** | The early termination of a stream pipeline once a terminal operation has obtained all the result it needs |
| **`Throwable`** | The root class of Java's exception hierarchy, with `Error` and `Exception` as its two direct subclasses |
| **Checked exception** | An exception the compiler requires to be either caught or declared with `throws`; represents an external, unpreventable risk |
| **Unchecked exception** | An exception with no mandatory handling requirement; represents a preventable logic error, extends `RuntimeException` |
| **Propagation** | The process by which an unhandled exception moves upward through the call chain until it is caught or reaches the top of the program |

---

## Section 15: Extra Read — Concepts Used in Assignments but Not Covered Live

The following topics were not part of the live session but appear in the accompanying assignment questions. Each is introduced here at a level sufficient to complete those assignments; a fuller treatment may follow in a later session.

### `count()`

A terminal operation that returns the number of elements remaining in the stream, as a `long`:

```java
long evenCount = numbers.stream()
    .filter(n -> n % 2 == 0)
    .count();
```

Like `collect()` and `findAny()`, `count()` closes the stream once called.

### Method References (`::`)

A **method reference** is a further shorthand, applicable when a lambda's entire body consists of calling one existing method. Four forms exist:

```java
// Static method reference
numbers.forEach(System.out::println);
// equivalent to:
numbers.forEach(n -> System.out.println(n));

// Instance method reference on a particular object
Item item = new Item(...);
Supplier<Double> priceSupplier = item::getPrice;

// Instance method reference on an arbitrary object of a particular type
items.stream().map(Item::getName);
// equivalent to:
items.stream().map(i -> i.getName());

// Constructor reference
Supplier<ArrayList<Integer>> listSupplier = ArrayList::new;
```

A method reference is preferred over an equivalent lambda purely for readability when the lambda body does nothing beyond invoking an existing method; it introduces no new behaviour.

### `Collectors.groupingBy()`

A specialized collector, used inside `collect()`, that groups stream elements by a classifier function into a `Map` where each key maps to a `List` of matching elements:

```java
Map<String, List<Item>> itemsByCategory = items.stream()
    .collect(Collectors.groupingBy(Item::getCategory));
```

Every `Item` sharing the same category value is grouped together under that category as the key, with `Item::getCategory` supplying the classifier used to determine grouping.

### `flatMap()`

Where `map()` transforms each element on a one-to-one basis, `flatMap()` is used when each element itself produces a stream or collection of further elements that should be flattened into a single combined stream:

```java
List<List<Integer>> nestedLists = Arrays.asList(
    Arrays.asList(1, 2, 3),
    Arrays.asList(4, 5),
    Arrays.asList(6)
);
List<Integer> flatList = nestedLists.stream()
    .flatMap(list -> list.stream())
    .collect(Collectors.toList());
// flatList: [1, 2, 3, 4, 5, 6]
```

Without `flatMap()`, `map(list -> list.stream())` alone would produce a `Stream<Stream<Integer>>` — a stream of streams — rather than a single flat `Stream<Integer>`. `flatMap()` performs the transformation and the flattening in one step.

### `parallelStream()`

`parallelStream()` creates a stream that distributes its processing across multiple threads, in contrast to the single-threaded behaviour of `.stream()` described in Section 4:

```java
long total = numbers.parallelStream()
    .filter(n -> n % 2 == 0)
    .count();
```

A parallel stream is appropriate only when the processing of each element is genuinely independent of every other element, since Java provides no ordering guarantee across a parallel stream's threads, and any shared mutable state accessed from within the pipeline introduces the risk of a race condition. A full treatment of thread safety and parallel processing belongs to the concurrency unit later in this series; `parallelStream()` should be used with caution until that material has been covered.

### Threading — `Thread`, `sleep()`, and `interrupt()`

Section 1 of this document uses `Thread` to run a `Runnable` on a separate thread, but does not cover controlling that thread's execution once started. Two commonly used methods are relevant for assignment purposes:

```java
Thread t = new Thread(() -> {
    try {
        System.out.println("Working...");
        Thread.sleep(2000);
        // pauses this thread for 2000 milliseconds
        System.out.println("Done.");
    } catch (InterruptedException e) {
        System.out.println("Thread was interrupted before completing.");
    }
});
t.start();
```

`Thread.sleep(milliseconds)` pauses the currently executing thread for the specified duration without consuming CPU cycles while waiting. It declares a checked exception, `InterruptedException`, which must be handled — this occurs because another thread may call `interrupt()` on the sleeping thread, which is Java's mechanism for signalling that a running thread should stop what it is doing:

```java
Thread t = new Thread(() -> {
    while (!Thread.currentThread().isInterrupted()) {
        // keep working until interrupted
    }
    System.out.println("Stopped due to interruption.");
});
t.start();
t.interrupt();
// requests that t stop
```

`interrupt()` does not forcibly terminate a thread; it sets an internal flag that a well-written thread is expected to check periodically, or that surfaces as an `InterruptedException` if the thread happens to be sleeping or waiting at the time. A thread's own code is responsible for deciding how to respond once it observes this signal. A full treatment of thread lifecycle and safe interruption is deferred to the concurrency unit.

---

## Section 16: Frequently Asked Interview Questions

**1. What is a functional interface, and why does a lambda expression require one?**

A functional interface is an interface with exactly one abstract method. A lambda expression has no name, return type, or access modifier of its own — Java infers all of this from the single method of the functional interface the lambda is assigned to. With more than one candidate method, this inference becomes ambiguous, which is why lambdas are restricted to functional interfaces.

**2. Is a lambda expression more performant than an anonymous class?**

Not meaningfully, and this is not the reason lambdas are used. A lambda is syntactic sugar over the same underlying mechanism; its benefit is conciseness and readability, not runtime performance. Any performance difference between the two is an implementation detail rather than a language guarantee.

**3. What is the difference between an intermediate and a terminal stream operation, in terms of actual execution?**

An intermediate operation — such as `filter` or `map` — returns a `Stream` and is not executed at the point it is written; it is only recorded as part of the pipeline. A terminal operation — such as `collect` or `findAny` — triggers actual execution of the entire pipeline up to that point and produces a concrete result, closing the stream in the process.

**4. Why does calling a terminal operation twice on the same stream throw an exception?**

A stream is a one-time pipeline over a data source, not a reusable object. Once a terminal operation has consumed it, the stream is considered closed, and any further operation on that same stream instance throws `IllegalStateException`. A new stream must be created with a fresh call to `.stream()` to process the same underlying data again.

**5. Why does adding `sorted()` before `findAny()` change the pipeline's behaviour, even though both examples eventually return only one result?**

`sorted()` cannot determine the correct position of any single element until it has examined every element in the stream, so it always forces a complete pass over the input. This eliminates the short-circuiting that `findAny()` would otherwise enable on its own, since the full sort must complete before `findAny()` can even begin selecting a result.

**6. Why does Java distinguish between checked and unchecked exceptions instead of treating all exceptions the same way?**

The distinction reflects where the fault genuinely lies. Unchecked exceptions represent logic errors that are preventable through correct code, so Java does not require them to be declared or handled — doing so would only encourage hiding bugs behind a `try`-`catch` instead of fixing them. Checked exceptions represent risks genuinely outside the developer's control, such as external I/O failures, so Java enforces that the calling code at least acknowledge the possibility.

**7. Why does placing a general `catch (Exception e)` before a more specific `catch` block cause a compile-time error?**

Since every more specific exception type is already an `Exception`, a preceding `catch (Exception e)` would match it first, making any subsequent, more specific `catch` block permanently unreachable. Java detects this at compile time and reports it as an error, rather than allowing dead code to exist silently.

**8. What is the practical difference between `Optional` and simply returning `null`?**

Both represent the possibility of an absent value, but `Optional` makes that possibility explicit in the method's return type and requires the caller to actively check for absence before extracting the value. A `null` return relies entirely on the caller remembering to check, and a missed check typically surfaces as a `NullPointerException` at a point in the code far removed from where the value actually originated.

**9. What is the difference between `map()` and `flatMap()`?**

`map()` transforms each element into exactly one new element, preserving a one-to-one relationship between input and output. `flatMap()` is used when each element itself produces a stream or collection of elements, and flattens all of these into a single combined stream, rather than producing a stream of streams.

**10. When is `parallelStream()` an appropriate choice over `.stream()`?**

Only when the processing applied to each element is fully independent of every other element and involves no shared mutable state, since Java provides no ordering guarantee across a parallel stream's threads, and any shared state accessed concurrently risks a race condition. In the majority of everyday backend processing, the overhead and risk of parallelism are not justified, and `.stream()` remains the default choice.

---

## Section 17: Self-Check Questions

1. Explain why `Comparable`, `Comparator`, `Runnable`, and `Callable` all qualify as functional interfaces, and why the `Stack` interface built in an earlier session does not.
2. Rewrite the following anonymous class as a lambda expression: `new Runnable() { public void run() { System.out.println("Task running"); } }`.
3. Why does the following fail to compile: `interface Test { void run(); void stop(); } Test t = () -> System.out.println("hi");`?
4. Explain, using a concrete example, the difference in behaviour between `filter()` and `map()`.
5. Write a stream pipeline that takes a `List<String>`, retains only strings longer than three characters, converts each to uppercase, and collects the result into a `List`.
6. Why does calling `.forEach()` twice on the same `Stream` object throw an exception the second time, and what is the correct fix?
7. In your own words, explain why intermediate stream operations are described as lazy, and terminal operations as eager.
8. Given a pipeline `numbers.stream().filter(...).sorted().findAny()`, will this process the entire input list or exit early? Justify your answer.
9. Why is `NullPointerException` an unchecked exception, while `SQLException` is checked? What does this difference imply about how each should be handled?
10. Write a three-layer method chain where the innermost method throws a checked exception, the middle method neither catches nor handles it, and the outermost method catches and logs it.

---

## Section 18: Further Reading

- **Official Java documentation — Lambda Expressions (The Java Tutorials):** the canonical reference for lambda syntax and functional interfaces.
- **Official Java documentation — the `java.util.stream` package:** the complete reference for `Stream`, `Collectors`, and related classes.
- **Official Java documentation — `java.util.Optional`:** the full API surface of `Optional`, including methods beyond `isPresent()` and `get()`.
- **Effective Java, Items 42–48 (Joshua Bloch):** a widely referenced treatment of lambdas, method references, and Streams API best practices.
- General reading on **Java's exception hierarchy**, extending the introduction in Sections 10–12, ahead of writing custom exception classes in the next session.

---

## Section 19: Homework

```text
1. Rewrite the Comparator built in the previous session's lab 
   (ItemPriceComparator, or equivalent) as a lambda expression, and 
   confirm the sort output is identical to the original.
2. Given a List<String> of words, write a stream pipeline that returns 
   only the words with more than five letters, converted to uppercase, 
   with duplicates removed, sorted alphabetically.
3. Write a short program demonstrating short-circuiting: use .filter() 
   with a print statement inside it, followed by .findAny(), and confirm 
   the printing stops once the first match is found. Then add .sorted() 
   before .findAny() and observe the change in behaviour.
4. Write a three-layer method chain (as in Section 12) where a checked 
   exception is thrown in the innermost method, passed through an 
   intermediate method using throws, and finally caught in main().
5. Push all code to GitHub.
```