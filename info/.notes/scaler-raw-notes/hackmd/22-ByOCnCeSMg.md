Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/ByOCnCeSMg

# Post Read - Design Patterns — Introduction and Singleton

---

title: Post-Read — Design Patterns: Introduction and Singleton
tags: [Final]

---

POST-READ | Design Principles & Patterns for Extensible Systems | Design Patterns — Introduction and Singleton

This is the first post-read of the new module on Design Patterns. Last class you learned SOLID principles, which are general guidelines for writing good code. This class introduces something a little different: design patterns, which are ready-made, reusable solutions to problems that keep showing up again and again in software. Today's session focused on one specific pattern called Singleton, built up slowly using one running example: a DBConnection class that starts out badly written and gets fixed, one problem at a time.

This document explains each idea in plain language, with the code from class, so you can revise it at your own pace.

## Section 1: What Is a Design Pattern, and Why Do We Need Named Ones?

### What It Means

A design pattern is a well-known way of solving a problem that shows up again and again in different software systems. It is not one person's clever idea for one project. It is a solution shape that many engineers, working on completely different projects, in different companies, ended up arriving at independently, because the same kind of problem kept appearing.

Think of the word "pattern" the same way you would think of it anywhere else, a repeating design, like the stripes on a shirt or the tiles on a floor. Software has repeating problems too, and design patterns are the repeating solutions to those problems.

### Where the Idea Comes From

In 1994, four authors, Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides, wrote a book collecting 23 of these common solutions. This book is usually just called "Gang of Four" or GoF for short (it is simply a nickname for "the book written by these four authors"). This module will cover about 10 of the most commonly used patterns from that book.

### Why Learn Named Patterns Instead of Just Using SOLID?

SOLID principles (from last class) tell you how to think about good design. Design patterns give you an actual, ready-made shape to use, so you do not have to reinvent it every time.

The biggest practical benefit is communication. If you tell a teammate in a design review, "let's use a Factory here," they instantly understand the shape of the solution you mean, no diagram or long explanation needed. It is like using a shared shortcut word that an entire team already understands.

### Hidden Pitfalls
- Thinking a design pattern is a totally new idea, separate from SOLID. It is not. Patterns are built using good principles like SOLID; they are just a named, reusable shape for applying those principles to a common problem.
- Assuming you need to memorize the exact names of all 23 GoF patterns before you can write good code. You only need to recognize the problem a pattern solves; the name is just a shared label for that solution once you already understand it.

## Section 2: The Three Families of Design Patterns

### What It Means

The 23 GoF patterns are usually grouped into three broad families, based on what kind of problem they solve:

1. Creational Patterns — HOW and WHEN objects get created
2. Structural Patterns — HOW classes/objects combine into bigger structures
3. Behavioural Patterns — HOW objects talk to each other and share work

This module focuses on creational patterns, patterns about how and when we create objects. The creational patterns covered this module are:

- Singleton ← today
- Builder ← next class
- Prototype (+ Registry)
- Factory (Simple / Method / Abstract)

Just from the name "Singleton," you can probably guess what it is about: making sure there is only one instance of something. That is exactly what today's class builds and explains.

### Hidden Pitfalls
- Trying to memorize which pattern belongs to which family before understanding what any of them actually do. The grouping is just a way to organize your thinking later; the important thing is understanding each pattern's actual problem first.

## Section 3: Singleton — What Problem Is It Actually Solving?

### What It Means

Singleton Pattern:
Makes sure a class has EXACTLY ONE object in the whole system,
and gives one shared way to access it.

In simple words: normally, you can create as many objects of a class as you want. Singleton is a rule that says, "no matter how many times anyone asks for an object of this class, always give them back the same one."

If a class X has one object x sitting at some memory address, say 200, then Singleton working correctly means: every single part of the code that touches x is pointing to that exact same address, 200. Not a copy. Not a similar object. The same object, everywhere.

### Why Would We Ever Want Only One Object?

There are two separate reasons this turns out to be useful.

#### Reason 1: A shared resource sits behind the class.

Think of one shared office printer. Everyone in the office prints to it. Buying five printers instead of one does not help anyone, it just wastes money and desk space. The same idea applies in code.

A DB connection is our app's open "line" to the database, it is what lets the app save and read data. Setting up this line takes real work behind the scenes, and once it is set up, it can be reused again and again. If UserService needs this line to save users, and OrderService needs it to save orders, both of them should really be sharing the same line, instead of each building their own.

If each service sets up its own separate connection instead of sharing one, we end up repeating the exact same setup work over and over, and ending up with many open connections all doing the exact same job that one shared connection could have done.

The same logic applies to a Logger. If five different logger objects all print to the same file or terminal, having five separate objects instead of one gains nothing, it just adds the risk of things stepping on each other while writing at the same time.

#### Reason 2: The object is genuinely expensive to create.

Setting up a fresh DB connection usually involves passing the host, username, and password, sending a request over the network (called a TCP request), and then waiting for the connection to actually open on the other end. That is several network round-trips, just to get ready, before even running one query.

If the server did all of this on every single incoming request, response times would collapse under real traffic. The smart move is: build the connection once, and reuse it forever. That is the entire economic case for Singleton, do the expensive work exactly once.

Use Singleton when:
1. A shared resource exists behind the class (DB connection, Logger, Cache)
2. Creating the object is genuinely expensive (network calls, disk I/O, heavy setup)

One more small but important note: a Singleton object is usually meant to stay stable and unchanging once it is set up, one shared, dependable thing that everyone relies on the same way.

### Hidden Pitfalls
- Assuming Singleton is about "saving memory" in general. It is really about avoiding wasted, repeated setup work and avoiding many competing copies of a shared resource, not about objects being small.
- Using Singleton for objects that are cheap to create and not actually shared. If neither of the two reasons above applies, forcing a class into a Singleton just adds restriction for no real benefit.

## Section 4: Building a Singleton, Step by Step

### What It Means

Let's build a Singleton from scratch, the same way it was done in class, starting from a version that is not a Singleton at all, and fixing it one problem at a time.

### Step 1: The Broken Starting Point

```java
public class DBConnection {
    String url;
    String userName;
    String password;
    List<Connection> pool;
}
```

Is this a Singleton? No. Nothing here stops anyone from creating as many objects as they like:

```java
DBConnection db1 = new DBConnection();
DBConnection db2 = new DBConnection();
// nothing stops this
```

The problem: nothing enforces "only one." The constructor is public (usable from anywhere), so anyone, anywhere in the code, can create a brand-new object whenever they want.

### Step 2: Make the Constructor Private

The obvious first fix: stop outside code from calling the constructor directly.

```java
public class DBConnection {
    String url;
    String userName;
    String password;
    List<Connection> pool;

    private DBConnection() { }
}
```

Now, from outside this class, can we create even one object? No, the constructor is private, so nothing outside the class is allowed to call it.

A new problem appears: we went from "too many objects" to "zero objects." Still broken, just broken in a different way. We need the class itself to call its own private constructor, exactly once, and hand that one object out to whoever asks.

### Step 3: Add a Public, Static Method to Control Access

If outside code cannot call the constructor directly, but something still needs to trigger it from outside, what do we need? A method that:

- is public, so outside code can call it, and
- is static, so it can be called without already having an object (you cannot call a normal method on an object you do not have yet)

```java
public class DBConnection {
    String url;
    String userName;
    String password;
    List<Connection> pool;

    private static DBConnection instance = null;

    private DBConnection() { }

    public static DBConnection getInstance() {
        if (instance == null) {
            instance = new DBConnection();
        }
        return instance;
    }
}
```

Let's trace two calls to getInstance() back to back:

- First call: instance is currently null, so a new object gets created and stored in instance.
- Second call: instance already holds an object, so that same object is simply returned, no new object is made.

Steps to build a Singleton:
1. Make the constructor private
2. Keep one static reference to the single instance
3. Add a public static method that creates the instance only if it doesn't exist yet, then returns it

A natural question here: why not just make the instance field public directly, and skip getInstance() entirely? Because then nothing checks or controls creation anymore, anyone could overwrite that reference directly and break the "only one" rule. The getInstance() method is exactly what protects that rule.

### What the Animation Shows

The class animation compares two classes side by side, a plain non-singleton DBConnection (with a public constructor) and a proper Singleton (with getInstance()), both being called repeatedly from main().

On the non-singleton side, every single new DBConnection() call creates a brand-new box on the heap (the heap is just the area of memory where objects live), so the count of boxes keeps climbing with every call.

On the singleton side, the very first getInstance() call creates exactly one box on the heap. Every call after that just draws an arrow pointing back to that same existing box, no new memory used at all. This is the clearest possible way to actually see "one shared object" instead of just being told about it.

### Hidden Pitfalls
- Making the constructor private but forgetting to add any way to actually create the object. This leaves you with zero usable objects, just as broken as having too many, only in the opposite direction.
- Making the instance field public instead of using a controlled getInstance() method. This removes all protection, since any code, anywhere, could now overwrite the shared instance directly.
- Forgetting that getInstance() must be static. A normal (non-static) method needs an object to be called on, but at the very start, before the first call, no object exists yet. Only a static method solves this chicken-and-egg problem.

## Section 5: Eager Loading — Creating It Too Early

### What It Means

The version built above waits until the first call to getInstance() before creating the object. This is called lazy loading, lazy meaning "wait until it's actually needed."

There is a simpler alternative worth understanding first, before dealing with multiple threads: create the object immediately, the moment the class loads (right when the app starts up), instead of waiting for the first getInstance() call. This is called eager loading, eager meaning "do it right away, without waiting."

```java
public class DBConnection {
    String url;
    String userName;
    String password;
    List<Connection> pool;

    private static DBConnection instance = new DBConnection();

    private DBConnection() { }

    public static DBConnection getInstance() {
        return instance;
    }
}
```

Think of a restaurant that pre-cooks every single dish on the menu before opening, instead of cooking to order. Once a customer arrives, there is nothing to wait for, the food is already ready. But this also means a lot of wasted effort, if some dishes never actually get ordered by anyone.

### The Downside

Creating the object this early means the app takes longer to start up, since this setup work happens right when the class loads, whether it turns out to be needed yet or not.

Eager Loading (create at class load time):
+ Simple, no locking needed
- Slower app startup
- Can't use runtime/dynamic configuration

There is a second downside worth knowing: with eager loading, the connection details get locked in at class-load time, before we even know what configuration (like which environment, or which settings) we actually want to use. This makes it harder to pass in settings that are only decided later, once the app is actually running.

### What the Animation Shows

Two timelines run side by side, both starting from "app launches," one labelled Eager, one labelled Lazy.

On the Eager timeline, the DBConnection object is built immediately, right at class-load time, before main() even starts running, before any request has arrived at all.

On the Lazy timeline, the object is not built at launch. The app starts up faster, and the object only gets constructed later, exactly at the moment the first getInstance() call actually happens.

If you drag the clock to a point where getInstance() is never called at all, the Lazy timeline shows the object simply never getting built, while the Eager side already paid that setup cost regardless, whether it was ever needed or not.

Because of these downsides, class returns to building the object lazily (on first use), but this raises a new question: what happens if multiple threads (multiple requests happening at the same time) call getInstance() at once? That is covered next.

### Hidden Pitfalls
- Assuming eager loading is always worse than lazy loading. For small, genuinely cheap objects, eager loading is perfectly fine and simpler, since there is no locking to worry about at all. The trade-off matters most for something expensive, like a real DB connection.
- Forgetting that eager loading locks in configuration at class-load time. If your app needs to decide connection details at runtime (for example, based on which environment it's running in), eager loading cannot support that.

## Section 6: Concurrency Breaks the Simple Singleton

### What It Means

A real server is not single-threaded, meaning it does not handle just one request at a time. Many requests can arrive and be processed at the same time, on separate threads (a thread is just one independent path of execution running inside your program).

Here is the danger: say Thread A and Thread B both call getInstance() at nearly the exact same moment, and instance is currently null. What could go wrong?

```
Thread A: checks instance == null → true
Thread B: checks instance == null → true   (A isn't done yet!)
Thread A: creates instance #1
Thread B: creates instance #2

Result: TWO objects. Singleton broken.
```

Both threads can see instance == null at the same time, before either one has finished creating the object. Both then go ahead and create their own separate instance. This is called a race condition, a bug where the exact outcome depends on the unpredictable timing of multiple threads running at once.

This kind of bug will not usually show up in normal, everyday local testing, since it needs two threads to hit that exact moment at almost exactly the same time. It tends to show up quietly in production, under real traffic and load, and can be very painful to reproduce and debug later.

### What the Animation Shows

An interleaved clock steps through Thread A's and Thread B's actions tick by tick, matching the board above, but here you can step through it yourself instead of just reading a table.

You will see both threads hit the instance == null check and both light up as "true" at nearly the same tick, before either one has created anything yet. As you step forward, both threads go ahead and create their own DBConnection object, and the animation shows two separate boxes appearing on the heap, one from each thread, clearly labelled instance #1 and instance #2. A "Singleton broken!" flag appears once both boxes exist.

### The First Fix: synchronized

The simplest fix is a lock, a way of saying "only one thread is allowed inside this section of code at a time." In Java, this is done with the synchronized keyword:

```java
public static synchronized DBConnection getInstance() {
    if (instance == null) {
        instance = new DBConnection();
    }
    return instance;
}
```

This is correct now, but think about the cost. Once instance already exists, say after ten million calls, does every single one of those calls still have to grab the lock, just to return the same object it already has? Yes. synchronized locks the method every single time it is called, even once there is nothing left to protect. This means we are paying the cost of locking forever, just to guard against a race that can genuinely only happen once, the very first time the object gets created.

### The Better Fix: Double-Checked Locking

Can we restructure this so the lock is only taken during that one risky moment, and skipped once the object already safely exists? Yes, using a pattern called double-checked locking:

Double-Checked Locking:
1. Check WITHOUT a lock first — fast, used almost every time
2. If it looks null → THEN take the lock
3. Check AGAIN inside the lock (another thread might have just finished)
4. Only now create the instance

```java
public static DBConnection getInstance() {
    if (instance == null) {
        synchronized (DBConnection.class) {
            if (instance == null) {
                instance = new DBConnection();
            }
        }
    }
    return instance;
}
```

Why do we need a second null check inside the lock, isn't the first check enough? Here is why: another thread could pass the first (outer) check, then get stuck waiting for the lock. By the time it finally gets the lock, the first thread may have already finished creating the instance. The second (inner) check catches exactly this situation, it is what actually guarantees "exactly one" object gets created, no matter how the threads happen to interleave.

Without this inner check, two threads could both pass the outer check, both queue up for the lock one after another, and still end up creating two separate instances, just one slightly after the other instead of at exactly the same moment. The inner check is the single most commonly forgotten line in this entire pattern, including, as you'll see next, by AI tools.

Here is a tick-by-tick trace of two threads racing for the lock:

```
tick:              1        2        3        4        5
Thread A:      outer-null  lock    inner-null CREATE  unlock
Thread B:      outer-null  wait     wait      wait    lock→inner-NOT-null→reuse
```

- Tick 1: both threads check instance == null and both see true.
- Tick 2: Thread A grabs the lock first. Thread B has to wait.
- Tick 3: Thread A checks again inside the lock, still null, so it is safe to create.
- Tick 4: Thread A creates the object.
- Tick 5: Thread A releases the lock. Thread B finally gets the lock, checks again, and this time it is not null, so Thread B skips creating a new object and simply reuses Thread A's object.

### What the Animation Shows

This turns the tick-by-tick board above into a step-through animation. At tick 1, both threads hit the outer null check simultaneously, both lighting up as "true," the same danger moment as before. At tick 2, Thread A visually "grabs" a lock icon while Thread B is shown frozen, waiting beside the lock. At ticks 3 and 4, Thread A performs the inner check (still null) and then creates the object, the heap shows exactly one box appearing. At tick 5, Thread A releases the lock, Thread B finally acquires it, runs its own inner check, sees "not null" this time, and its arrow points to the same existing box instead of creating a new one.

### Hidden Pitfalls
- Assuming a race condition will show up during normal local testing. It usually will not, since it depends on very precise, unlucky timing between threads, which is much more likely under real production traffic than on a developer's own machine.
- Using plain synchronized on the whole method and assuming there is no cost. There is: every single call, forever, has to acquire the lock, even long after the object has already been safely created.
- Writing double-checked locking with only one null check instead of two. Without the inner check, two threads can both pass the outer check, queue for the lock, and still end up creating two separate objects, defeating the entire point of the pattern.

## Section 7: The volatile Keyword — the Bug Even AI Misses

### What It Means

AI coding tools are genuinely useful for getting the basic shape of a Singleton right, since this exact pattern appears constantly in their training data. But there is one small keyword they often quietly skip, and skipping it means the code is not actually safe. That keyword is volatile.

If you ask an AI assistant to "write a thread-safe Singleton class in Java for a database connection," you will usually get a correct-looking double-checked-locking version. The important thing is not just "does it look right," it is checking one specific line: does the instance field say

```java
private static DBConnection instance;
```

or

```java
private static volatile DBConnection instance;
```

If you then ask a more casual, second version of the same prompt, something like "write a simple singleton, keep it minimal," this is often the exact moment volatile quietly disappears from the answer, since it looks like optional extra code to a casual reading, when it is not.

### Why This One Word Actually Matters

Without volatile, is double-checked locking on the JVM fully safe? No, and this genuinely surprises most engineers the first time they hear it.

Here is why: the line instance = new DBConnection() looks like one single step, but to the computer, it is really three separate steps:

1. Allocate memory for the new object
2. Run the constructor (set up the object's actual fields and values)
3. Assign the reference (point the instance variable at that memory)

Without volatile, the compiler and the CPU are allowed to reorder these steps for performance reasons, since they might not realize, just by looking at the code, that the order matters here. Specifically, step 3 (assigning the reference) could happen before step 2 (actually finishing the constructor) has completed.

This means a second thread could see a non-null instance reference, pointing to a real memory location, but the constructor has not actually finished running there yet. In other words, the second thread could get back a half-built object, one that looks like it exists, but whose fields are not actually set up properly yet.

### What the Animation Shows

instance = new DBConnection() is broken into its real three steps, shown as numbered blocks: allocate memory, run the constructor, assign the reference.

Without volatile, the animation shows steps 2 and 3 visually swapping places, the reference gets assigned before the constructor has actually finished running. A second thread is shown checking instance == null right in this danger window, it sees a non-null reference (since step 3 already happened) and happily returns it, even though step 2 has not completed, the object is shown as "half-built," with fields still empty or default.

Switch on volatile in the animation, and steps 2 and 3 get locked into order, the swap is no longer allowed, and the second thread can only ever see a reference after the object is fully and properly constructed.

```java
private static volatile DBConnection instance;
```

volatile does two things:
1. Stops that instruction reordering
2. Makes sure every thread sees the latest value, not an old cached copy

### The Habit Worth Building

The habit to build:
1. Ask AI for a first draft — it's fast and usually gets the shape right
2. Then question it yourself:
   - "What's the subtle bug here?"
   - "What would break this under concurrency?"
   - "What would a senior reviewer flag?"
AI is good at the textbook shape of a pattern.
You are responsible for the one keyword that makes it actually correct.

### Hidden Pitfalls
- Assuming that if the AI-generated code compiles and "looks right," it is safe. Missing volatile will not cause a compile error, or even a visible bug most of the time, it only fails under very specific, unlucky concurrent timing, exactly the kind of bug that is hardest to catch by just reading code.
- Trusting a "keep it minimal" style prompt to preserve every important detail. Casual rewordings of a prompt are exactly where AI tools tend to drop details like volatile, since they can look like unnecessary extra code at a glance.
- Thinking synchronized alone is enough to make double-checked locking safe. The lock protects against two threads creating the object at the same time, but it does nothing about instruction reordering; volatile is a separate, additional fix for a separate problem.

## Section 8: Where Singleton Already Exists in Real Code

### What It Means

If you have ever written a Spring Boot app and marked a class @Service or @Component, you have already used Singleton, just built for you by the framework instead of by hand. Spring's default setting (called "bean scope") for these annotated classes is Singleton: by default, only one instance of that class is ever created and shared throughout the app.

Where Singleton runs in production, right now, everywhere:
- Spring Beans → default scope for every @Service/@Component
- Connection pool managers (HikariCP, etc.) → one pool per data source
- Logging frameworks (Log4j, SLF4J) → one logger per class/app
- App-wide config/cache objects → one shared config in memory
- Redis/cache client instances → one client, reused everywhere

It makes sense that the connection pool manager itself, not just one individual connection, is also usually built as a Singleton. This is the exact same argument from Section 3, just applied one level up: you want one single, shared pool coordinating all the connections, instead of several separate, competing pools each opening their own connections.

### Hidden Pitfalls
- Assuming Singleton only shows up in hand-written code you build yourself. Most beginners use Singleton every day without realizing it, through frameworks like Spring, which apply this pattern automatically behind the scenes.

## Section 9: Python vs Java — Same Idea, Different Effort

### What It Means

Java requires you to build all this machinery by hand: a private constructor, a static field, a static method, and locking. Does Python need all of that for the same guarantee? No, not usually.

Python vs Java — Singleton:

Java: No built-in "only one" mechanism → build it by hand (private constructor + static instance + locking)

Python: A module, once imported, is ALREADY a singleton — Python caches it after the first import; every later import returns the same module object. So the simplest Python singleton is often just module-level variables and functions — no class needed. If a class is really needed, Python singletons are usually built by overriding __new__(), or with a decorator, or (for thread-safety) a metaclass with a lock — same idea as double-checked locking, just Python syntax.

The important thing to notice: the reason for wanting a Singleton, a shared resource, or an expensive-to-create object, is exactly the same in both languages. Only the method of achieving it changes, since Python's module system already gives a kind of free Singleton behaviour that Java simply does not have built in.

### Hidden Pitfalls
- Assuming Python "doesn't need" Singleton at all. It still needs the same underlying guarantee (one shared object); Python just happens to get part of that guarantee for free through its module system, when a class isn't strictly required.

## Section 10: Serialization, Enum Singleton, and Pros and Cons

### What It Means

Double-checked locking (Section 6) handles the concurrency problem, multiple threads racing to create the object. But it does not handle a different problem: serialization.

Serialization is the process of converting an object into a stream of bytes, usually so it can be saved to a file, or sent across a network, and then rebuilt later from those saved bytes (this rebuilding step is called deserialization). If a Singleton object gets serialized and then deserialized, what happens to our "exactly one object" guarantee?

In Java, deserialization, by default, skips your private constructor and skips your getInstance() check completely, it rebuilds the object directly from the saved bytes. This means deserializing a "Singleton" can quietly create a brand-new, second object, breaking the entire guarantee we worked so hard to build.

This is genuinely why many experienced Java engineers reach for a different, simpler tool instead of building it by hand: a Java enum used as the Singleton.

An enum Singleton gets, for free, guaranteed by the JVM itself:
- Exactly one instance
- Thread-safety
- Safe against serialization

An enum in Java is normally used for a fixed set of constant values (like days of the week), but it turns out the JVM's own guarantees about enums, that each enum value exists exactly once, happen to solve all three Singleton problems (multiple objects, thread-safety, and serialization) at the same time, without you having to write any of the manual machinery from Section 4 or Section 6 yourself.

Assignment for next class: read up on enum-based Singleton, and come with questions.

### Pros and Cons of Singleton

Pros of Singleton:
- Efficient — one shared, reused object
- Avoids the real cost of repeated expensive creation

Cons of Singleton:
- Hard to unit test — can't easily swap in a mock, since everyone reaches for the same global instance
- Hidden global state — can make code harder to follow and can quietly couple unrelated parts of the system together

The testing downside is worth sitting with for a moment. If "the database connection" is a hardcoded global Singleton, testing something like UserService in isolation, without needing a real database, becomes genuinely awkward, since the service always reaches for the same real, shared instance. This is exactly why Dependency Injection and interfaces (ideas from the SOLID class) still matter, even when you are using a pattern like Singleton. The next section looks at one practical trick engineers use to make Singleton classes easier to test.

### Hidden Pitfalls
- Assuming double-checked locking alone makes a Singleton fully "safe." It only solves the concurrency problem. Serialization can still quietly break the "exactly one object" guarantee unless it is specifically handled, for example by using an enum.
- Reaching for Singleton everywhere without considering testability. A global, shared instance can make it hard to isolate a class during testing, since you cannot easily substitute a fake or mock version in its place.

## Section 11: reset_instance() — Making a Singleton Testable

### What It Means

Section 10 mentioned a real downside of Singleton: it is hard to unit test, since every part of the code always reaches for the same one shared object. This becomes a real problem during testing. Tests usually want to start from a clean, fresh state every single time, but a Singleton, by design, refuses to give you a fresh object, it always hands back the same old one, even across different tests.

reset_instance() is simply a small helper method, written by the developer, whose entire job is to forget the currently stored instance, so that the very next call to getInstance() is forced to build a brand-new one from scratch. It is not part of the official Singleton pattern from the GoF book; it is a practical addition engineers add specifically to make Singleton classes easier to test.

Think of it like a whiteboard eraser. The Singleton keeps writing its one answer on a whiteboard (the stored instance) and just keeps pointing back at that same board whenever asked. reset_instance() is the eraser, wipe the board clean, so the next question forces someone to write a fresh answer again.

This idea is the same in both Java and Python, only the exact syntax differs, since in both languages a Singleton is really just "an object stored somewhere and reused," and resetting it just means clearing out that stored reference.

### Practical Mechanics — Java

Recall the double-checked-locking version of DBConnection from Section 6:

```java
public class DBConnection {
    private static volatile DBConnection instance;

    private DBConnection() { }

    public static DBConnection getInstance() {
        if (instance == null) {
            synchronized (DBConnection.class) {
                if (instance == null) {
                    instance = new DBConnection();
                }
            }
        }
        return instance;
    }

    // Added purely for testing purposes
    public static synchronized void resetInstance() {
        instance = null;
    }
}
```

resetInstance() does exactly one thing: it sets the static instance field back to null. Nothing more. The next time anyone calls getInstance() after this, instance will once again be null, so a brand-new DBConnection object gets created, exactly like the very first call the app ever made.

A typical use in a test would look like this:

```java
@BeforeEach   // runs before every single test method
void setUp() {
    DBConnection.resetInstance();
}

@Test
void testConnectionIsCreatedFresh() {
    DBConnection conn = DBConnection.getInstance();
    // conn is guaranteed to be a brand-new object here,
    // not left over from a previous test
}
```

Without resetInstance(), every test in the same test run would keep sharing the exact same DBConnection object created by whichever test ran first, so any changes one test made to that shared object could quietly leak into the next test, making tests unreliable and dependent on run order.

### Practical Mechanics — Python

In Python, a Singleton is often built with a class attribute holding the one instance, and __new__ controlling creation:

```python
class DBConnection:
    _instance = None   # class attribute, shared across all uses of this class

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        cls._instance = None
```

reset_instance() here does the same job as the Java version: it clears cls._instance back to None. The next call to DBConnection() will then see _instance is None, and go through __new__ again to build a genuinely fresh object.

A typical test usage looks like this:

```python
import unittest

class TestDBConnection(unittest.TestCase):
    def setUp(self):
        DBConnection.reset_instance()   # runs before every test

    def test_connection_is_created_fresh(self):
        conn = DBConnection()
        # conn is guaranteed to be a brand-new object here,
        # not left over from a previous test
```

Recall from Section 9 that Python often builds a Singleton without a class at all, just module-level variables and functions, since an imported module is already cached and shared. In that style, "resetting" usually just means writing a plain function that clears out the module-level variable holding the shared object:

```python
# db_connection.py
_instance = None

def get_instance():
    global _instance
    if _instance is None:
        _instance = _create_connection()
    return _instance

def reset_instance():
    global _instance
    _instance = None
```

The idea is identical either way, whether it is a class attribute or a module-level variable, reset_instance() simply clears whatever variable is holding onto the one shared object.

### Why This Matters for Both Languages, in Plain Terms

In both Java and Python, a Singleton works by storing its one object somewhere permanent, a static field in Java, a class attribute or module-level variable in Python, and always checking that same storage spot before deciding whether to create something new. reset_instance(), in either language, is just a small, deliberate way to clear out that storage spot on demand, so that tests do not accidentally share state with each other.

### Hidden Pitfalls
- Adding reset_instance() and then calling it anywhere in production code, not just tests. This defeats the entire purpose of Singleton. If production code resets the instance while other parts of the app are still using the old one, you can end up with two different "shared" objects active at the same time, exactly the bug Singleton was built to prevent.
- Forgetting to call reset_instance() between tests. Without it, tests can pass or fail depending on which order they happen to run in, since they are all secretly sharing one leftover object from whichever test ran first. This is a classic source of tests that pass individually but fail when run together.
- Not making reset_instance() thread-safe in Java, when the rest of the Singleton is thread-safe. If multiple threads could call resetInstance() and getInstance() at the same time, the same kind of race condition from Section 6 can reappear. Marking resetInstance() as synchronized, as shown above, keeps it consistent with the rest of the class.
- Treating reset_instance() as part of the "official" Singleton pattern. It is not one of the GoF pattern's original ideas; it is a practical, test-only addition that experienced engineers include specifically to work around Singleton's testing downside mentioned in Section 10.

## Section 12: Common Pitfalls Summary

1. Thinking design patterns are separate from SOLID principles
     -> patterns are just a named, reusable shape for applying
        principles like SOLID to a common, recurring problem.

2. Using Singleton for objects that are cheap to create and not
   actually shared
     -> if there's no shared resource and no real creation cost,
        forcing "only one object" adds restriction with no benefit.

3. Making the constructor private without adding any way to
   actually create the object
     -> leaves you with zero usable objects, a different kind of
        broken than having too many.

4. Making the instance field public instead of using a controlled
   getInstance() method
     -> removes all protection; any code anywhere could overwrite
        the shared instance directly.

5. Assuming eager loading is always worse than lazy loading
     -> fine for small, cheap objects; the trade-off only really
        matters for something genuinely expensive to create.

6. Assuming a race condition will show up in normal local testing
     -> it depends on precise, unlucky thread timing, far more
        likely under real production traffic than on your own machine.

7. Writing double-checked locking with only one null check
     -> without the inner check, two threads can both pass the
        outer check, queue for the lock, and still create two
        separate objects.

8. Trusting AI-generated Singleton code without checking for
   volatile
     -> missing volatile doesn't cause a compile error or an
        obvious bug; it only fails under specific, unlucky
        concurrent timing.

9. Assuming double-checked locking alone makes a Singleton fully
   safe
     -> it only protects against concurrency; serialization can
        still quietly create a second object unless separately
        handled (for example, with enum).

10. Forgetting to reset a Singleton's stored instance between tests
     -> tests silently share leftover state from whichever test ran
        first, causing results that depend on test run order.

### Hidden Pitfalls
- Treating Singleton as a "set it and forget it" pattern. As shown across this document, each individual fix, private constructor, getInstance(), locking, volatile, enum, reset_instance(), solves one specific problem; skipping any one of them leaves a different gap open.

## Section 13: Key Terminology

| Term | Meaning in Simple Words |
|------|-------------------------|
| **Design pattern** | A well-known, reusable solution to a problem that keeps repeating across different software systems |
| **GoF (Gang of Four)** | Nickname for the four authors who wrote the original 1994 book collecting 23 common design patterns |
| **Creational pattern** | A design pattern about how and when objects get created |
| **Singleton** | A pattern that ensures a class has exactly one object, shared everywhere it is used |
| **Private constructor** | A constructor that can only be called from inside its own class, blocking outside code from creating new objects directly |
| **Static method** | A method that can be called without first having an object of that class |
| **Eager loading** | Creating an object immediately, as soon as the class loads, before it is actually needed |
| **Lazy loading** | Creating an object only when it is first actually requested |
| **Race condition** | A bug where the outcome depends on the unpredictable timing of multiple threads running at the same time |
| **synchronized** | A Java keyword that locks a method or block so only one thread can run it at a time |
| **Double-checked locking** | A pattern that checks for null once without a lock (fast), and again inside a lock (safe), to avoid unnecessary locking after the object already exists |
| **volatile** | A Java keyword that stops instruction reordering and makes sure every thread sees the latest value of a variable, not a stale cached copy |
| **Serialization** | Converting an object into a stream of bytes, usually to save it to a file or send it across a network |
| **Deserialization** | Rebuilding an object from previously saved bytes |
| **Enum Singleton** | Using a Java enum to implement Singleton, since the JVM guarantees exactly one instance, thread-safety, and serialization-safety automatically |
| **reset_instance() / resetInstance()** | A developer-added helper method that clears a Singleton's stored instance, forcing the next request for it to create a fresh one, mainly used to keep tests independent of one another |

---

## Section 14: Frequently Asked Interview Questions

**1. What is a design pattern, in your own words?**

A well-known, reusable solution to a problem that keeps showing up again and again across different software systems, not one person's one-time idea, but a shape many engineers independently arrive at.

**2. Why does the Singleton pattern exist, what actual problems does it solve?**

Two main reasons: first, when a shared resource sits behind the class (like a database connection or a logger), having many separate objects doing the same job is wasteful. Second, when creating the object is genuinely expensive (network calls, heavy setup), it makes sense to build it once and reuse it, rather than repeating that expensive work every time.

**3. What are the basic building blocks needed to write a Singleton in Java?**

A private constructor (so outside code cannot create new objects directly), a static field holding the single shared instance, and a public static method (usually called getInstance()) that creates the instance only if it does not already exist, and then returns it.

**4. What is the difference between eager loading and lazy loading in a Singleton?**

Eager loading creates the object immediately, when the class loads, whether it turns out to be needed or not. Lazy loading waits and creates the object only the first time it is actually requested. Eager loading is simpler and needs no locking, but slows down app startup and cannot use runtime configuration; lazy loading avoids that cost but needs careful handling for multiple threads.

**5. What is a race condition, and how can it break a simple Singleton?**

A race condition is a bug where the result depends on the unpredictable timing of multiple threads. In a simple Singleton, two threads could both check instance == null, both see true at nearly the same time (since neither has finished yet), and both go on to create their own separate object, resulting in two instances instead of one.

**6. Why is plain synchronized on getInstance() correct but not ideal?**

It correctly prevents two threads from creating the object at the same time, but it forces every single call, forever, to acquire the lock, even long after the object has already been safely created and there is nothing left to protect. This adds unnecessary cost on every call.

**7. Why does double-checked locking need two null checks instead of one?**

The first (outer) check avoids taking the lock most of the time, for speed. But another thread could pass that outer check, then wait for the lock, and by the time it gets the lock, the object might already exist. The second (inner) check, taken after acquiring the lock, catches exactly this case and prevents a second object from being created.

**8. Why does missing volatile make double-checked locking unsafe, even though the code compiles fine and looks correct?**

Creating an object is really three separate steps: allocating memory, running the constructor, and assigning the reference. Without volatile, the compiler and CPU can reorder these steps, so the reference could be assigned before the constructor has actually finished running. A second thread could then see a non-null reference pointing to a half-built object.

**9. Why can serialization break a Singleton even if double-checked locking is used correctly?**

Because deserialization in Java rebuilds an object directly from saved bytes, skipping the private constructor and the getInstance() check entirely. This can create a second, separate object, even though the original Singleton logic was written correctly.

**10. Why is enum-based Singleton often preferred by experienced engineers?**

Because the JVM itself guarantees, for free, that an enum has exactly one instance, that it is thread-safe, and that it is safe against serialization, all three problems that otherwise require separate, manual fixes (private constructor, double-checked locking, volatile, and special serialization handling).

**11. Why would a developer add a reset_instance() method to a Singleton, when it is not part of the original GoF pattern?**

To make the class testable. Since a Singleton always returns the same shared object, tests that run one after another can end up secretly sharing state left behind by earlier tests. reset_instance() clears the stored instance, so each test can start from a genuinely fresh object.

**12. What is the risk of calling reset_instance() from production code instead of only from tests?**

It defeats the purpose of Singleton. If the instance is reset while other parts of the running application still hold a reference to the old object, two different "shared" objects can end up active in the system at the same time, exactly the problem Singleton exists to prevent.

---

## Section 15: Self-Check Questions

1. In your own words, explain the two reasons given in class for why we would ever want to limit a class to exactly one object.
2. Write the three steps required to build a basic (non-thread-safe) Singleton in Java, in the correct order.
3. Explain why making the instance field public instead of using a getInstance() method breaks the Singleton guarantee.
4. What is the main downside of eager loading, and in what situation would eager loading still be a perfectly reasonable choice?
5. Walk through, step by step, how two threads calling getInstance() at nearly the same time can end up creating two separate objects in the simple (non-synchronized) version.
6. Why is double-checked locking generally preferred over simply marking the entire getInstance() method as synchronized?
7. Explain, in plain words, what instruction reordering means, and why it can cause a thread to see a "half-built" object.
8. What does the volatile keyword actually do, in your own words, and why is it easy to forget when writing or reviewing Singleton code?
9. Why can a correctly written, thread-safe Singleton still end up with two instances if it gets serialized and deserialized?
10. Name at least three places in real-world software (mentioned in class) where the Singleton pattern is already being used, even if the developer never wrote getInstance() by hand.
11. Write a short resetInstance() method for a Java Singleton, and explain, in one or two sentences, exactly what problem it solves.
12. Explain why calling reset_instance() inside a running application's normal request-handling code (not a test) would be dangerous.

---

## Section 16: Further Reading

- "Design Patterns: Elements of Reusable Object-Oriented Software" by Gamma, Helm, Johnson, and Vlissides (the original "Gang of Four" book): the source of the 23 classic design patterns, including Singleton.
- Official Java documentation on the volatile keyword: for a deeper technical explanation of instruction reordering and memory visibility between threads.
- Official Java documentation on synchronized and thread safety: background reading on how locking works in Java more generally, useful before the next class covers more concurrency-related patterns.
- Spring Framework documentation on Bean Scopes: to see, in a real framework, exactly how and why "singleton" is the default scope for @Service, @Component, and @Repository classes.
- Any short article on Java enum Singleton (search "Java enum singleton"): to prepare for the homework assignment and next class's discussion.
- Python documentation on unittest.TestCase.setUp() and JUnit's @BeforeEach: to see how reset_instance()-style methods are typically wired into a real test suite in both languages.

---

## Section 17: Homework

1. Implement DBConnection as a Singleton with double-checked locking
   AND volatile. Write a short comment explaining why volatile is
   needed.

2. Ask an AI assistant to generate a Singleton Logger class. Find
   and fix at least one issue in the output (thread-safety,
   serialization, or anything else) — write down what you found.

3. Read about enum-based Singleton. Rewrite your DBConnection as an
   enum. Compare — which felt easier to get right?

4. Push all code to GitHub — branch: singleton-lecture-complete