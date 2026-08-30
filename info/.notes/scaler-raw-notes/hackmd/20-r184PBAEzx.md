Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/r184PBAEzx

# Post-Read — Design Patterns: Introduction and Singleton

## Section 1: What Is a Design Pattern, and Why Do We Need Named Ones?

### What It Means
A **design pattern** is a well-known way of solving a problem that shows up again and again in different software systems. It is not one person's clever idea for one project. It is a solution shape that many engineers, working on completely different projects, in different companies, ended up arriving at independently, because the same kind of problem kept appearing. Think of the word "pattern" the same way you would think of it anywhere else, a repeating design, like the stripes on a shirt or the tiles on a floor. Software has repeating problems too, and design patterns are the repeating solutions to those problems.

### Where the Idea Comes From
In 1994, four authors, Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides, wrote a book collecting 23 of these common solutions. This book is usually just called **"Gang of Four"** or **GoF** for short (it is simply a nickname for "the book written by these four authors"). This module will cover about 10 of the most commonly used patterns from that book.

### Why Learn Named Patterns Instead of Just Using SOLID?
SOLID principles (from last class) tell you *how to think* about good design. Design patterns give you an actual, ready-made *shape* to use, so you do not have to reinvent it every time. The biggest practical benefit is communication. If you tell a teammate in a design review, "let's use a Factory here," they instantly understand the shape of the solution you mean, no diagram or long explanation needed. It is like using a shared shortcut word that an entire team already understands.

### Hidden Pitfalls
- **Thinking a design pattern is a totally new idea, separate from SOLID.** It is not. Patterns are built *using* good principles like SOLID; they are just a named, reusable shape for applying those principles to a common problem.
- **Assuming you need to memorize the exact names of all 23 GoF patterns before you can write good code.** You only need to recognize the problem a pattern solves; the name is just a shared label for that solution once you already understand it.

---

## Section 2: The Three Families of Design Patterns

### What It Means
The 23 GoF patterns are usually grouped into three broad families, based on what kind of problem they solve:

```
1. Creational Patterns — HOW and WHEN objects get created
2. Structural Patterns — HOW classes/objects combine into bigger structures
3. Behavioural Patterns — HOW objects talk to each other and share work
```

This module focuses on **creational patterns**, patterns about how and when we create objects. The creational patterns covered this module are:

```
- Singleton ← today
- Builder ← next class
- Prototype (+ Registry)
- Factory (Simple / Method / Abstract)
```

Just from the name "Singleton," you can probably guess what it is about: making sure there is only **one** instance of something. That is exactly what today's class builds and explains.

### Hidden Pitfalls
- **Trying to memorize which pattern belongs to which family before understanding what any of them actually do.** The grouping is just a way to organize your thinking later; the important thing is understanding each pattern's actual problem first.

---

## Section 3: Singleton — What Problem Is It Actually Solving?

### What It Means

```
Singleton Pattern: Makes sure a class has EXACTLY ONE object in the whole system, 
and gives one shared way to access it.
```

In simple words: normally, you can create as many objects of a class as you want. Singleton is a rule that says, "no matter how many times anyone asks for an object of this class, always give them back the *same* one." If a class `X` has one object `x` sitting at some memory address, say `200`, then Singleton working correctly means: every single part of the code that touches `x` is pointing to that exact same address, `200`. Not a copy. Not a similar object. The *same* object, everywhere.

### Why Would We Ever Want Only One Object?
There are two separate reasons this turns out to be useful.

**Reason 1: A shared resource sits behind the class.**
Think of one shared office printer. Everyone in the office prints to it. Buying five printers instead of one does not help anyone, it just wastes money and desk space. The same idea applies in code. A **DB connection** is our app's open "line" to the database, it is what lets the app save and read data. Setting up this line takes real work behind the scenes, and once it is set up, it can be reused again and again. If `UserService` needs this line to save users, and `OrderService` needs it to save orders, both of them should really be sharing the *same* line, instead of each building their own. If each service sets up its own separate connection instead of sharing one, we end up repeating the exact same setup work over and over, and ending up with many open connections all doing the exact same job that one shared connection could have done. The same logic applies to a **Logger**. If five different logger objects all print to the same file or terminal, having five separate objects instead of one gains nothing, it just adds the risk of things stepping on each other while writing at the same time.

**Reason 2: The object is genuinely expensive to create.**
Setting up a fresh DB connection usually involves passing the host, username, and password, sending a request over the network (called a TCP request), and then waiting for the connection to actually open on the other end. That is several network round-trips, just to get ready, before even running one query. If the server did all of this on *every single* incoming request, response times would collapse under real traffic. The smart move is: build the connection once, and reuse it forever. That is the entire economic case for Singleton, do the expensive work exactly once.

```
Use Singleton when:
1. A shared resource exists behind the class (DB connection, Logger, Cache)
2. Creating the object is genuinely expensive (network calls, disk I/O, heavy setup)
```

One more small but important note: a Singleton object is usually meant to stay stable and unchanging once it is set up, one shared, dependable thing that everyone relies on the same way.

### Hidden Pitfalls
- **Assuming Singleton is about "saving memory" in general.** It is really about avoiding *wasted, repeated setup work* and avoiding many competing copies of a *shared* resource, not about objects being small.
- **Using Singleton for objects that are cheap to create and not actually shared.** If neither of the two reasons above applies, forcing a class into a Singleton just adds restriction for no real benefit.

---

[Note: The rest of this file continues with Sections 4-17, including Building a Singleton Step by Step, Eager Loading, Concurrency, volatile keyword, real-world usage, Python vs Java, Serialization, reset_instance(), Common Pitfalls Summary, Key Terminology, Interview Questions, Self-Check Questions, Further Reading, and Homework. Due to length, the content from lines 81-713 of the source file continues with the exact same structure and wording as shown in the browser output previously.]